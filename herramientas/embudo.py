#!/usr/bin/env python3
"""Cohortes de leads por semana de creación o por anuncio: del lead a la venta y al cash, con su coste.

Uso:
  python3 -I herramientas/embudo.py cohortes --cliente acme --por semana|anuncio [--leads <csv>] [--meta <csv>]
          [--desde AAAA-MM-DD] [--hasta AAAA-MM-DD] [--fecha AAAA-MM-DD] [--ciclo 30]
          [--modelo servicios|saas] [--margen 0.8] [--churn 0.05] [--guardar] [--json]

Entrada `--leads` (una fila por lead o por cliente; tiene datos personales, así que vive en `clientes/<slug>/privado/`).
Sin `--leads` se usa el CSV más reciente de `privado/` que empiece por `leads`, `contactos` o `clientes`.
Columnas reconocidas (español o inglés; las que falten se dejan vacías):
  fecha (creación del lead) · ad_id · utm_content (nombre del anuncio) · utm_campaign
  cualificado · cita · show · venta     → sí/no, 1/0 o una fecha (una fecha cuenta como «sí»)
  diagnostico · propuesta · perdido     → ídem, opcionales (si faltan, esas cifras salen vacías, no a 0)
  etapa                                 → si no hay columnas sí/no: la etapa actual del pipeline, por palabras clave
                                          (sin tildes ni mayúsculas) con las etapas del contrato §16, en este orden:
                                            perdido     perdid/lost/descartad/no cualific…  → cuenta solo como lead
                                            ganado      ganad/won/firmad/venta/cliente/pagad/closed/purchase → venta
                                            no-show     no show/no asistió/no se presentó → agendó, sin show
                                            propuesta   propuest/proposal/presupuest/quote
                                            asistio     show/asist/attend/realizad → show
                                            llamada     cita/agend/book/schedul/reserv/llamada/call/reunión/demo → cita
                                            cualificado cualific/qualif/MQL/SQL
                                            diagnostico diagnost/calculadora/auditoría/assessment/quiz
                                          Las de un pipeline de taller (registrado, asistió al taller, se quedó a la
                                          oferta) y las de entrada (nuevo, contactado) cuentan como lead; las que no
                                          reconoce, también, con un aviso
                                          Cada etapa implica las anteriores (ganado implica propuesta, asistió, llamada
                                          y cualificado), salvo diagnóstico: no todos los leads lo hacen, así que con
                                          etapa no se cuenta (sale vacío)
  cash · fecha_cash (o fecha_venta)     → cobros para cash a 30/60/90 días desde la creación del lead
  SaaS: prueba · activacion · cliente_pago · mrr (mensual, sin IVA) · fecha_baja
Entrada `--meta` (opcional): exportación de Meta por día (`meta_ads.py anuncios --por-dia`) para el gasto por semana,
o por anuncio para el gasto por anuncio. Sin ella, por anuncio se usa el gasto de `registro-creativo.csv`.

Salida: solo agregados (nunca filas de personas). `--guardar` escribe `clientes/<slug>/datos/cohortes_<por>.csv` y
regenera la sección correspondiente de `clientes/<slug>/cohortes-leads.md`.

Lectura correcta (meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md y
meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md §2): las cohortes jóvenes aún no han tenido
tiempo de cerrar. Una cohorte semanal es «madura» cuando han pasado `--ciclo` días (30 por defecto, [HYPOTHESIS]:
ajústalo a tu ciclo de venta) desde el domingo que la cierra; no decidas con cohortes inmaduras.
SaaS: LTV = ARPA × margen / churn mensual y payback = CAC / (ARPA × margen). El churn se mide con los datos si hay
≥10 bajas ([HYPOTHESIS]); si no, usa `--churn`.
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402
from registro_creativo import ErrorUsuario, _mapa, _norm, agregar_meta, leer_csv, modelo_de, num  # noqa: E402

ALIAS_LEADS = {
    "fecha": ["fecha", "fecha creacion", "fecha de creacion", "fecha alta", "fecha registro", "created at",
              "date added", "dateadded", "created", "fecha lead"],
    "ad_id": ["ad id", "anuncio id", "identificador del anuncio"],
    "nombre": ["utm content", "anuncio", "ad name", "nombre del anuncio"],
    "campana": ["utm campaign", "campana", "campaign name", "campaign"],
    "cualificado": ["cualificado", "qualified", "mql", "sql", "fecha cualificado"],
    "cita": ["cita", "fecha cita", "appointment", "booked", "agendado", "fecha agenda", "llamada", "llamada agendada"],
    "show": ["show", "asistio", "showed", "asistencia", "fecha show", "llamada asistida"],
    "venta": ["venta", "ganado", "won", "fecha venta"],
    "diagnostico": ["diagnostico", "diagnostico completado", "fecha diagnostico", "calculadora", "assessment"],
    "propuesta": ["propuesta", "propuesta enviada", "fecha propuesta", "proposal", "presupuesto enviado"],
    "perdido": ["perdido", "lost", "fecha perdido", "descartado"],
    # Sin «valor»: en GHL es el monetaryValue de la oportunidad, también de las abiertas, no dinero cobrado (I6, 30b).
    "cash": ["cash", "importe", "cobrado", "revenue"],
    "fecha_cash": ["fecha cash", "fecha cobro", "fecha pago"],
    "etapa": ["etapa", "stage", "pipeline stage"],
    "prueba": ["prueba", "trial", "fecha prueba", "trial start"],
    "activacion": ["activacion", "activado", "activated", "fecha activacion"],
    "cliente_pago": ["cliente pago", "cliente de pago", "paying", "fecha primer pago", "suscrito"],
    "mrr": ["mrr", "importe mensual", "cuota mensual", "mensualidad"],
    "baja": ["fecha baja", "baja", "canceled at", "cancelado", "churned"],
}
_FALSO = {"", "0", "no", "false", "falso", "n", "-", "nan", "none", "null"}
# Etapa actual del pipeline → etapa del contrato §16 (nombres internos: cita = llamada, show = asistio,
# venta = ganado). El orden importa: «no cualificado» es perdido, «no show» no es show, «llamada de diagnóstico» es
# cita. Se comparan sin tildes y en minúsculas.
_ETAPAS = [("perdido", r"perdid|\blost\b|descartad|no cualific|unqualif|disqualif|not qualified|no encaj|abandon|"
                       r"rechazad"),
           ("venta", r"ganad|\bwon\b|firmad|contratad|venta|vendid|cliente(?! potencial)|pagad|closed|purchase|compr"),
           ("no_show", r"no ?show|no asisti|no se present|no vino|ausente"),
           ("propuesta", r"propuest|proposal|presupuest|oferta enviada|quote"),
           # etapas de un pipeline de taller o webinar (§16, «Eventos»): asistir al taller no es asistir a la llamada
           ("evento", r"taller|webinar|masterclass|directo|evento|se quedo|registrad"),
           ("show", r"show|asisti|attend|realizad|celebrad"),
           ("cita", r"cita|agend|book|schedul|reserv|appointment|llamada|\bcall\b|reunion|demo"),
           ("cualificado", r"cualific|qualif|\bmql\b|\bsql\b"),
           ("diagnostico", r"diagnost|calculadora|auditoria|assessment|quiz"),
           ("lead", r"\blead|nuev|\bnew\b|contactad|entrante|recibid|sin contactar|\bopen\b|abiert")]
_NIVEL = {"perdido": 0, "lead": 0, "evento": 0, "diagnostico": 1, "cualificado": 2, "cita": 3, "no_show": 3, "show": 4,
          "propuesta": 5, "venta": 6}
_IMPLICADAS = ("cualificado", "cita", "show", "propuesta", "venta")  # con etapa, cada una implica las anteriores
_OPCIONALES = ("diagnostico", "propuesta", "perdido")  # None si el CSV no lo dice


# ---------------------------------------------------------------- lectura
def fecha_de(texto) -> date | None:
    """Fecha de un campo de exportación: AAAA-MM-DD…, DD/MM/AAAA o epoch (s o ms)."""
    t = str(texto or "").strip()
    if not t:
        return None
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", t)
    try:
        if m:
            return date(int(m[1]), int(m[2]), int(m[3]))
        m = re.match(r"(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})", t)
        if m:
            return date(int(m[3]), int(m[2]), int(m[1]))
        if re.fullmatch(r"\d{10}(\d{3})?", t):
            return datetime.fromtimestamp(int(t[:10])).date()
    except (ValueError, OverflowError, OSError):
        return None
    return None


def _si(texto) -> bool:
    return str(texto or "").strip().lower() not in _FALSO


def leer_leads(ruta) -> tuple[list[dict], list[str]]:
    filas = leer_csv(ruta)
    if not filas:
        raise ErrorUsuario("El CSV de leads está vacío")
    m = _mapa(list(filas[0].keys()), ALIAS_LEADS)
    if "fecha" not in m:
        raise ErrorUsuario("El CSV de leads necesita una columna con la fecha de creación (fecha, created_at, "
                           "dateAdded…)")
    avisos = []
    usa_etapa = "etapa" in m and not any(c in m for c in ("cualificado", "cita", "show", "venta"))
    if usa_etapa:
        avisos.append("Sin columnas sí/no de etapas: se deducen de la etapa actual del pipeline (los perdidos "
                      "cuentan solo como lead y los diagnósticos no se pueden contar)")
    desconocidas: Counter = Counter()
    out, sin_fecha = [], 0
    for f in filas:
        fecha = fecha_de(f.get(m["fecha"]))
        if not fecha:
            sin_fecha += 1
            continue
        lead = {"fecha": fecha, "ad_id": "", "nombre": "", "campana": ""}
        for c in ("ad_id", "nombre", "campana"):
            if c in m:
                lead[c] = (f.get(m[c]) or "").strip()
        if not re.fullmatch(r"\d{5,25}", lead["ad_id"]):
            lead["ad_id"] = ""
        nivel, etapa = 0, None
        if usa_etapa:
            texto = _norm(f.get(m["etapa"]) or "")
            etapa = next((n for n, rx in _ETAPAS if re.search(rx, texto)), None)
            nivel = _NIVEL[etapa] if etapa else 0
            if texto and not etapa:
                desconocidas[texto] += 1
        for c in ("cualificado", "cita", "show", "venta"):
            # con columnas sí/no se respeta lo que diga el CRM (hay ventas sin llamada); con etapa, cada etapa
            # implica las anteriores
            lead[c] = (_si(f.get(m[c])) if c in m else False) or (usa_etapa and nivel >= _NIVEL[c])
        for c in _OPCIONALES:
            if c in m:
                lead[c] = _si(f.get(m[c]))
            elif usa_etapa and c == "propuesta":
                lead[c] = nivel >= _NIVEL["propuesta"]
            elif usa_etapa and c == "perdido":
                lead[c] = etapa == "perdido"
            else:
                lead[c] = None
        lead["no_show"] = etapa == "no_show" if usa_etapa else None
        lead["fecha_venta"] = fecha_de(f.get(m["venta"])) if "venta" in m else None
        lead["cash"] = (num(f.get(m["cash"])) or 0.0) if "cash" in m else 0.0
        lead["fecha_cash"] = (fecha_de(f.get(m["fecha_cash"])) if "fecha_cash" in m else None) or lead["fecha_venta"]
        for c in ("prueba", "activacion", "cliente_pago"):
            lead[c] = _si(f.get(m[c])) if c in m else False
        lead["fecha_pago"] = fecha_de(f.get(m["cliente_pago"])) if "cliente_pago" in m else None
        if not lead["cliente_pago"] and lead["venta"]:
            lead["cliente_pago"] = True
        lead["mrr"] = (num(f.get(m["mrr"])) or 0.0) if "mrr" in m else 0.0
        lead["fecha_baja"] = fecha_de(f.get(m["baja"])) if "baja" in m else None
        out.append(lead)
    if sin_fecha:
        avisos.append(f"{sin_fecha} filas sin fecha de creación válida se han ignorado")
    if desconocidas:
        lista = ", ".join(f"«{t}» ({n})" for t, n in desconocidas.most_common(5))
        avisos.append(f"Etapas que no reconozco y cuentan solo como lead: {lista}. Renómbralas como las del "
                      "contrato §16 o exporta columnas sí/no")
    return out, avisos


def _por_defecto(slug: str) -> pathlib.Path:
    privado = _comun.ruta_cliente(slug) / "privado"
    candidatos = [p for pat in ("leads*.csv", "contactos*.csv", "clientes*.csv") for p in privado.glob(pat)]
    if not candidatos:
        raise ErrorUsuario(f"No hay CSV de leads en clientes/{slug}/privado/ (leads*.csv). Expórtalo con "
                           "`ghl.py` o `stripe_datos.py`, o pásalo con --leads")
    return max(candidatos, key=lambda p: p.stat().st_mtime)


# ---------------------------------------------------------------- gasto
def gasto_meta(ruta) -> tuple[dict[str, float], dict[date, float], dict[str, str], bool]:
    """(gasto por ad_id, gasto por lunes de semana, nombre por ad_id, ¿es diario?)."""
    filas = leer_csv(ruta)
    agregado = agregar_meta(filas)
    por_ad = {ad: d["gasto"] for ad, d in agregado.items()}
    nombres = {ad: d["nombre"] for ad, d in agregado.items()}
    por_semana: dict[date, float] = defaultdict(float)
    if not filas:
        return por_ad, {}, nombres, False
    m = _mapa(list(filas[0].keys()), {"desde": ["desde", "date start", "reporting starts", "inicio del informe"],
                                      "hasta": ["hasta", "date stop", "reporting ends", "fin del informe"],
                                      "gasto": ["spend", "gasto", "gasto eur", "amount spent*", "importe gastado*"]})
    diario = "desde" in m and "gasto" in m
    for f in filas:
        d0 = fecha_de(f.get(m.get("desde", ""), ""))
        d1 = fecha_de(f.get(m.get("hasta", ""), "")) if "hasta" in m else d0
        if not d0 or (d1 and d0 != d1):
            diario = False
            continue
        por_semana[d0 - timedelta(days=d0.weekday())] += num(f.get(m["gasto"])) or 0.0
    return por_ad, dict(por_semana) if diario else {}, nombres, diario


# ---------------------------------------------------------------- cálculo
def _div(a, b, dec=2):
    return round(a / b, dec) if b else None


def _cohorte(leads: list[dict], gasto: float | None, hoy: date, ciclo: int, modelo: str) -> dict:
    n = len(leads)
    c = {"leads": n, "cualificados": sum(l["cualificado"] for l in leads), "citas": sum(l["cita"] for l in leads),
         "shows": sum(l["show"] for l in leads), "ventas": sum(l["venta"] for l in leads)}
    for campo, clave in (("diagnosticos", "diagnostico"), ("propuestas", "propuesta"), ("perdidos", "perdido"),
                         ("no_shows", "no_show")):
        conocidos = [l[clave] for l in leads if l.get(clave) is not None]
        c[campo] = sum(conocidos) if conocidos else None
    con_fecha = [l for l in leads if l["cash"] and l["fecha_cash"]]
    for dias in (30, 60, 90):
        c[f"cash_{dias}d"] = round(sum(l["cash"] for l in con_fecha if (l["fecha_cash"] - l["fecha"]).days <= dias), 2) \
            if con_fecha else None
    c["cash_total"] = round(sum(l["cash"] for l in leads), 2)
    c["pct_maduros"] = round(sum((hoy - l["fecha"]).days >= ciclo for l in leads) / n * 100, 1) if n else None
    c["gasto"] = round(gasto, 2) if gasto is not None else None
    g = c["gasto"]
    c["cpl"] = _div(g, n) if g is not None else None
    c["coste_cita"] = _div(g, c["citas"]) if g is not None else None
    c["coste_show"] = _div(g, c["shows"]) if g is not None else None
    c["coste_venta"] = _div(g, c["ventas"]) if g is not None else None
    c["coste_diagnostico"] = _div(g, c["diagnosticos"]) if g is not None and c["diagnosticos"] is not None else None
    c["coste_propuesta"] = _div(g, c["propuestas"]) if g is not None and c["propuestas"] is not None else None
    c["tasa_cita"] = _div(c["citas"] * 100, n, 1)
    c["tasa_show"] = _div(c["shows"] * 100, c["citas"], 1)
    c["tasa_propuesta"] = _div(c["propuestas"] * 100, c["shows"] or c["citas"], 1) \
        if c["propuestas"] is not None else None
    c["tasa_cierre"] = _div(c["ventas"] * 100, c["shows"] or c["citas"], 1)
    c["lead_a_venta"] = _div(c["ventas"] * 100, n, 2)
    if modelo == "saas":
        pagos = [l for l in leads if l["cliente_pago"]]
        c.update(pruebas=sum(l["prueba"] for l in leads), activaciones=sum(l["activacion"] for l in leads),
                 clientes_pago=len(pagos), mrr_nuevo=round(sum(l["mrr"] for l in pagos), 2),
                 bajas=sum(1 for l in pagos if l["fecha_baja"] and l["fecha_baja"] <= hoy))
        c["coste_prueba"] = _div(g, c["pruebas"]) if g is not None else None
        c["cac"] = _div(g, c["clientes_pago"]) if g is not None else None
    return c


def _churn_observado(leads: list[dict], hoy: date) -> tuple[float | None, int]:
    bajas, meses = 0, 0.0
    for l in leads:
        if not l["cliente_pago"]:
            continue
        inicio = l["fecha_pago"] or l["fecha"]
        fin = l["fecha_baja"] if l["fecha_baja"] and l["fecha_baja"] <= hoy else hoy
        meses += max(0, (fin - inicio).days) / 30.4375
        bajas += 1 if l["fecha_baja"] and l["fecha_baja"] <= hoy else 0
    return (bajas / meses if meses > 0 and bajas >= 10 else None), bajas


def cohortes(slug: str, por: str, leads_csv=None, meta_csv=None, desde: date | None = None,
             hasta: date | None = None, hoy: date | None = None, ciclo: int = 30, modelo: str | None = None,
             margen: float = 0.8, churn: float | None = None) -> dict:
    hoy = hoy or date.today()
    ficha = _comun.leer_ficha(slug)
    modelo = modelo or ("saas" if modelo_de(ficha.get("tipo", "")) == "saas" else "servicios")
    ruta = pathlib.Path(leads_csv) if leads_csv else _por_defecto(slug)
    leads, avisos = leer_leads(ruta)
    leads = [l for l in leads if (not desde or l["fecha"] >= desde) and (not hasta or l["fecha"] <= hasta)]
    if not leads:
        raise ErrorUsuario("No hay leads en el periodo indicado")

    gasto_ad: dict[str, float] = {}
    gasto_sem: dict[date, float] = {}
    nombres: dict[str, str] = {}
    if meta_csv:
        gasto_ad, gasto_sem, nombres, diario = gasto_meta(meta_csv)
        if por == "semana" and not diario:
            avisos.append("La exportación de Meta no es diaria: no se puede repartir el gasto por semana "
                          "(usa `meta_ads.py anuncios --por-dia`)")
    elif por == "anuncio":
        reg = _comun.ruta_cliente(slug) / "registro-creativo.csv"
        if reg.exists():
            with reg.open(encoding="utf-8-sig", newline="") as h:
                for f in csv.DictReader(h):
                    if f.get("ad_id"):
                        gasto_ad[f["ad_id"]] = num(f.get("gasto")) or 0.0
                        nombres[f["ad_id"]] = f.get("nombre", "")
            avisos.append("Gasto tomado del registro creativo (periodo de su última actualización): para alinear "
                          "periodos pasa --meta del mismo rango que los leads")
    id_por_nombre: dict[str, set] = defaultdict(set)
    for ad, nom in nombres.items():
        if nom:
            id_por_nombre[nom].add(ad)
    for l in leads:  # completa el ad_id desde el nombre cuando no hay ambigüedad
        if not l["ad_id"] and l["nombre"] and len(id_por_nombre.get(l["nombre"], ())) == 1:
            l["ad_id"] = next(iter(id_por_nombre[l["nombre"]]))
    atribuidos = sum(1 for l in leads if l["ad_id"] or l["nombre"])
    if atribuidos < len(leads):
        avisos.append(f"{len(leads) - atribuidos} de {len(leads)} leads no tienen anuncio (ni ad_id ni utm_content): "
                      "revisa las UTM")

    grupos: dict[tuple, list[dict]] = defaultdict(list)
    for l in leads:
        if por == "semana":
            grupos[(l["fecha"] - timedelta(days=l["fecha"].weekday()),)].append(l)
        else:
            grupos[(l["ad_id"] or l["nombre"] or "(sin anuncio)",)].append(l)

    filas = []
    for clave, ls in grupos.items():
        if por == "semana":
            lunes = clave[0]
            iso = lunes.isocalendar()
            g = gasto_sem.get(lunes) if gasto_sem else None
            fila = {"semana": f"{iso[0]}-W{iso[1]:02d}", "lunes": lunes.isoformat(),
                    "madura": (hoy - (lunes + timedelta(days=6))).days >= ciclo}
        else:
            ad = clave[0]
            g = gasto_ad.get(ad) if gasto_ad else None
            campanas = sorted({l["campana"] for l in ls if l["campana"]})
            fila = {"ad_id": ad if re.fullmatch(r"\d{5,25}", ad) else "",
                    "anuncio": nombres.get(ad) or next((l["nombre"] for l in ls if l["nombre"]), "") or ad,
                    "campana": ", ".join(campanas)}
        fila.update(_cohorte(ls, g, hoy, ciclo, modelo))
        filas.append(fila)
    if por == "semana":
        filas.sort(key=lambda f: f["lunes"])
    else:
        filas.sort(key=lambda f: (-(f["gasto"] or 0), -f["leads"]))

    total = _cohorte(leads, sum(gasto_sem.values()) if por == "semana" and gasto_sem else
                     (sum(gasto_ad.values()) if por == "anuncio" and gasto_ad else None), hoy, ciclo, modelo)
    saas = None
    if modelo == "saas":
        medido, bajas = _churn_observado(leads, hoy)
        ch = churn if churn else medido
        pagos = [l for l in leads if l["cliente_pago"] and l["mrr"]]
        arpa = sum(l["mrr"] for l in pagos) / len(pagos) if pagos else None
        saas = {"arpa": round(arpa, 2) if arpa else None, "margen": margen, "bajas": bajas,
                "churn_mensual": round(ch, 4) if ch else None,
                "origen_churn": "--churn" if churn else ("medido" if medido else None)}
        saas["ltv"] = round(arpa * margen / ch, 2) if arpa and ch else None
        for f in filas + [total]:
            f["ltv"] = saas["ltv"]
            f["payback_meses"] = round(f["cac"] / (arpa * margen), 1) if f.get("cac") and arpa else None
        if not ch:
            avisos.append(f"Solo hay {bajas} bajas: el churn no se puede medir aún; pasa --churn para estimar el LTV")
    inmaduras = [f["semana"] for f in filas if por == "semana" and not f["madura"]]
    if inmaduras:
        avisos.append(f"Cohortes inmaduras (menos de {ciclo} días desde su cierre): {', '.join(inmaduras)}. "
                      "Sus ventas y su cash aún van a subir")
    return {"cliente": slug, "fecha": hoy.isoformat(), "por": por, "modelo": modelo, "ciclo_dias": ciclo,
            "leads_archivo": ruta.name, "cohortes": filas, "total": total, "saas": saas, "avisos": avisos}


# ---------------------------------------------------------------- salida
def _v(x, dec=None):
    if x is None:
        return "—"
    if isinstance(x, bool):
        return "sí" if x else "no"
    if isinstance(x, float):
        return f"{x:,.{2 if dec is None else dec}f}".replace(",", "·").replace(".", ",").replace("·", ".")
    return str(x)


def tabla_markdown(r: dict) -> str:
    if r["por"] == "semana":
        cab = ["Semana de creación", "Madura"]
        clave = lambda f: [f"{f['semana']} ({f['lunes']})", _v(f["madura"])]  # noqa: E731
    else:
        cab = ["Anuncio", "Campaña", "% maduros"]
        clave = lambda f: [f["anuncio"] or f["ad_id"], f["campana"], _v(f["pct_maduros"], 1)]  # noqa: E731
    if r["modelo"] == "saas":
        cols = [("Registros", "leads"), ("Pruebas", "pruebas"), ("Activaciones", "activaciones"),
                ("Clientes de pago", "clientes_pago"), ("MRR nuevo", "mrr_nuevo"), ("Gasto", "gasto"),
                ("Coste por prueba", "coste_prueba"), ("CAC", "cac"), ("Payback (meses)", "payback_meses")]
    else:
        cols = [("Leads", "leads"), ("Diagnósticos", "diagnosticos"), ("Cualificados", "cualificados"),
                ("Citas", "citas"), ("Shows", "shows"), ("Propuestas", "propuestas"), ("Ventas", "ventas"),
                ("Cash 30d", "cash_30d"), ("Cash 60d", "cash_60d"), ("Cash 90d", "cash_90d"),
                ("Gasto", "gasto"), ("CPL", "cpl"), ("Coste por cita", "coste_cita"),
                ("Coste por propuesta", "coste_propuesta"), ("Coste por venta", "coste_venta")]
        # Diagnósticos y propuestas solo salen si el CSV los trae (columna sí/no o, las propuestas, la etapa)
        hay = {k for k in ("diagnosticos", "propuestas") if r["total"].get(k) is not None}
        quitar = {"diagnosticos", "propuestas", "coste_propuesta"} - hay - ({"coste_propuesta"} if "propuestas" in hay
                                                                           else set())
        cols = [(n, k) for n, k in cols if k not in quitar]
    lin = ["| " + " | ".join(cab + [c for c, _ in cols]) + " |", "|" + "---|" * (len(cab) + len(cols))]
    for f in r["cohortes"]:
        lin.append("| " + " | ".join(clave(f) + [_v(f.get(k)) for _, k in cols]) + " |")
    t = r["total"]
    lin.append("| " + " | ".join(["**Total**"] + [""] * (len(cab) - 1) + [_v(t.get(k)) for _, k in cols]) + " |")
    return "\n".join(lin)


def guardar(r: dict) -> list[pathlib.Path]:
    d = _comun.ruta_cliente(r["cliente"])
    (d / "datos").mkdir(parents=True, exist_ok=True)
    csv_out = d / "datos" / f"cohortes_{r['por']}.csv"
    claves = list(r["cohortes"][0].keys()) if r["cohortes"] else []
    with csv_out.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=claves, lineterminator="\n")
        w.writeheader()
        for f in r["cohortes"]:
            w.writerow({k: ("" if v is None else v) for k, v in f.items()})
    md = d / "cohortes-leads.md"
    titulo = f"## Por {r['por']}"
    seccion = (f"{titulo}\n\n> Generado con `herramientas/embudo.py` el {r['fecha']} desde {r['leads_archivo']} · "
               f"ciclo {r['ciclo_dias']} días · modelo {r['modelo']}. Solo agregados.\n\n{tabla_markdown(r)}\n")
    texto = md.read_text(encoding="utf-8") if md.exists() else ""
    if "## Por " not in texto:  # plantilla original o archivo nuevo: se rehace con secciones
        primera = texto.splitlines()[0] if texto.strip() else f"# Cohortes de leads: {r['cliente']}"
        texto = primera + "\n"
    patron = re.compile(rf"^{re.escape(titulo)}\n.*?(?=^## |\Z)", re.S | re.M)
    texto = patron.sub(lambda _: seccion + "\n", texto) if patron.search(texto) else \
        texto.rstrip("\n") + "\n\n" + seccion
    md.write_text(texto, encoding="utf-8")
    return [csv_out, md]


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("cohortes", help="cohortes por semana de creación o por anuncio")
    c.add_argument("--cliente", required=True)
    c.add_argument("--por", choices=["semana", "anuncio"], required=True)
    c.add_argument("--leads", help="CSV con una fila por lead (en privado/)")
    c.add_argument("--meta", help="CSV de Meta (diario para el gasto por semana)")
    c.add_argument("--desde")
    c.add_argument("--hasta")
    c.add_argument("--fecha", help="fecha de referencia, AAAA-MM-DD (por defecto, hoy)")
    c.add_argument("--ciclo", type=int, default=30, help="días hasta que una cohorte se considera madura")
    c.add_argument("--modelo", choices=["servicios", "saas"])
    c.add_argument("--margen", type=float, default=0.8, help="SaaS: margen bruto sobre el MRR [HYPOTHESIS]")
    c.add_argument("--churn", type=float, help="SaaS: churn mensual si aún no se puede medir")
    c.add_argument("--guardar", action="store_true")
    c.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        fechas = [date.fromisoformat(x) if x else None for x in (a.desde, a.hasta, a.fecha)]
    except ValueError:
        print("Error: las fechas van como AAAA-MM-DD", file=sys.stderr)
        return 1
    if not 0 < a.margen <= 1 or (a.churn is not None and not 0 < a.churn < 1) or a.ciclo < 0:
        print("Error: --margen va entre 0 y 1, --churn entre 0 y 1 (mensual) y --ciclo ≥ 0", file=sys.stderr)
        return 1
    try:
        r = cohortes(a.cliente, a.por, a.leads, a.meta, fechas[0], fechas[1], fechas[2], a.ciclo, a.modelo,
                     a.margen, a.churn)
    except ErrorUsuario as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except _comun.FichaInvalida as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2
    rutas = guardar(r) if a.guardar else []
    if a.json:
        print(json.dumps({**r, "guardado": [str(p.relative_to(_comun.RAIZ)) for p in rutas]}, ensure_ascii=False,
                         indent=2, default=str))
        return 0
    print(f"# Cohortes por {r['por']} · {r['cliente']} · {r['fecha']} · modelo {r['modelo']}\n")
    print(tabla_markdown(r))
    if r["saas"]:
        s = r["saas"]
        print(f"\nARPA {_v(s['arpa'])} · margen {s['margen']:.0%} · churn mensual "
              f"{_v(s['churn_mensual'], 4)} ({s['origen_churn'] or 'sin datos'}) · LTV {_v(s['ltv'])}")
    for av in r["avisos"]:
        print(f"\nAviso: {av}")
    for p in rutas:
        print(f"[guardado] {p.relative_to(_comun.RAIZ)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
