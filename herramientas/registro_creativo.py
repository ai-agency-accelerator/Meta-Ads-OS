#!/usr/bin/env python3
"""Registro creativo: cruza Meta con los resultados de negocio por anuncio y propone un veredicto.

Escribe `clientes/<slug>/registro-creativo.csv` (contrato §6, una fila por ad_id). La clasificación (ángulo, concepto,
formato, hook) sale del nombre del anuncio con `nomenclatura.py`.

Uso:
  python3 -I herramientas/registro_creativo.py actualizar --cliente acme --meta <csv> [--ghl <csv>] [--stripe <csv>]
          [--objetivo citas=120 ...] [--madurez citas=14 ...] [--fecha AAAA-MM-DD] [--simular] [--json]
  python3 -I herramientas/registro_creativo.py sin-nomenclatura --cliente acme [--meta <csv>] [--json]

Entradas (CSV con coma, punto y coma o tabulador; con o sin BOM; cabeceras en español o inglés):
- `--meta`: `meta_ads.py anuncios`, una exportación de Ads Manager (con «Identificador del anuncio») o un CSV con
  ad_id, ad_name, spend, impressions… Si hay varias filas por anuncio (por día o país) se suman. Exporta el periodo
  completo que quieras evaluar: las métricas de Meta se sustituyen, no se acumulan. Una celda de resultados vacía
  con gasto cuenta como 0 (Ads Manager no escribe el 0). Un ID en notación científica (CSV guardado con Excel) es
  un error: el ID ya no se puede recuperar.
- `--ghl` / `--stripe`: agregados por anuncio (`ghl.py por-anuncio`, `stripe_datos.py por-anuncio`, en
  `clientes/<slug>/datos/`). Se unen por `ad_id` y, si no lo hay, por nombre del anuncio (`utm_content`). Columnas
  reconocidas: leads (o registros), cualificados, citas, shows, pruebas, activaciones, clientes_pago (o ventas), cash.
  Si las dos traen la misma columna, manda Stripe. Usa el mismo periodo en las tres exportaciones.

Columnas calculadas (porcentajes en 0–100 con punto decimal):
  hook_rate = vistas de 3 s / impresiones · hold_rate = ThruPlays / vistas de 3 s · ctr = clics en el enlace /
  impresiones · cpm · coste_resultado_meta · coste_cita · coste_venta (gasto / clientes_pago).
  (Fórmulas fijadas según meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md; hook y hold rate no son
  métricas oficiales de Meta y el hold rate está inflado en vídeos de ≤15 s.)

Veredicto (meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md §5 y principio 4 de
13-sistema-operativo/01-principios-de-razonamiento.md: decidir con la capa más baja de verdad):
- Capas, de más profunda a menos: servicios → clientes_pago, shows, citas, cualificados, leads, resultado_meta;
  SaaS → clientes_pago, activaciones, pruebas, leads, resultado_meta; e-commerce → clientes_pago, resultado_meta.
- Referencia de coste por capa: `--objetivo`, si no la columna «Target» de la tabla «Economía» de la ficha y, si
  tampoco, la media de la cuenta (solo con ≥10 eventos en esa capa).
- `resultado_meta` es el evento que optimiza cada conjunto (columna `evento_resultado` de `meta_ads.py anuncios` o
  «Indicador de resultado» de Ads Manager; si no, `meta.evento_principal` de la ficha): se compara con el objetivo de
  esa capa (Schedule → coste por cita, StartTrial → coste por prueba, Purchase → CAC). Si los anuncios optimizan
  eventos distintos, cada uno se compara con el suyo y no se usa la media de la cuenta.
- perdedor: en cualquier capa con referencia, si el anuncio rindiera al objetivo, ver tan pocos eventos con su gasto
  tendría una probabilidad < 5 % (Poisson). Con 0 eventos equivale a gastar 3× el coste objetivo (regla 2–3×).
  Madurez por capa: en capas por debajo del lead no se juzga a un anuncio antes de que sus leads hayan tenido
  tiempo de llegar a esa etapa (`MADUREZ`; servicios: cualificado 7, cita 14, show 21 y cliente de pago 56 días;
  cámbialo con `--madurez capa=días`). La edad cuenta desde el inicio del anuncio (fecha del nombre o primer día con
  gasto en una exportación por día) o desde el inicio del periodo, si es posterior: la cohorte es la del periodo.
  Sin fecha fiable (sin nomenclatura y exportación sin `--por-dia`) las capas profundas no se juzgan.
- ganador: en la capa de decisión (la más profunda en la que algún anuncio tiene ≥10 eventos), ≥10 eventos y coste
  ≤ referencia. «Provisional» con <30 eventos; «candidato a confirmado» con ≥30 y ≥7 días (falta ver que aguanta
  al subir gasto).
- en-test: con gasto pero sin datos para decidir. sin-datos: sin gasto en el periodo exportado.
- Las métricas antes del clic solo añaden una nota («candidato a apagar o iterar el hook») cuando hook rate y CTR
  están por debajo del 50 % de la mediana de la cuenta con ≥2.000 impresiones.
- Para fijar un veredicto a mano, escribe en `motivo` un texto que empiece por «manual:»: no se recalcula.
- Al guardar, `datos/registro-creativo_ultima-exportacion.json` dice qué anuncios y qué periodo traía la exportación:
  `elementos_creativos.py` solo analiza esos (el registro conserva las cifras viejas de los demás).

Identidad (`pagina` o `colaboracion`, contrato §6): separa las dos versiones de una misma pieza, que comparten nombre y
`utm_content`. Si la columna está vacía, sale de la tabla `| ad_id | Identidad | …` de la sección «Prueba social y
derechos» de los LEEME de `clientes/<slug>/creativos/`. Un valor escrito a mano no se cambia.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import pathlib
import re
import statistics
import sys
import unicodedata
import urllib.parse
from collections import defaultdict
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402
import nomenclatura  # noqa: E402

COLUMNAS = ("ad_id,nombre,fecha,campana,conjunto,angulo,concepto,formato,hook,via,identidad,ruta_creativo,gasto,"
            "impresiones,"
            "hook_rate,hold_rate,ctr,cpm,resultado_meta,coste_resultado_meta,leads,cualificados,citas,shows,pruebas,"
            "activaciones,clientes_pago,cash,coste_cita,coste_venta,n_suficiente,veredicto,fecha_veredicto,"
            "motivo").split(",")

N_DECIDIR = 10          # eventos para un ganador provisional (KB 13/05 §5: 10–20)
N_CONFIRMAR = 30        # ganador confirmado (KB 13/05 §5: 30–50 y ≥7 días)
N_MEDIA = 10            # eventos mínimos para usar la media de la cuenta como referencia [HYPOTHESIS]
ALFA_DESCARTE = 0.05    # 0 eventos → 3× la referencia (KB 13/05: 2–3×, 5 % de falsos negativos)
IMPRESIONES_ATENCION = 2000

CAPAS = {
    "servicios": ["clientes_pago", "shows", "citas", "cualificados", "leads", "resultado_meta"],
    "saas": ["clientes_pago", "activaciones", "pruebas", "leads", "resultado_meta"],
    "ecommerce": ["clientes_pago", "resultado_meta"],
}
CAPAS_SUPERFICIALES = {"leads", "resultado_meta"}
# Días que tarda en madurar cada capa profunda, desde el inicio del anuncio (o del periodo exportado, si es posterior).
# Servicios: meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md §10.2 (cohorte semanal legible a partir
# de: cualificado 1 semana, llamada 1–2, asistió 2, propuesta 3–4 y ganado 6–10 semanas desde el lead).
# SaaS y e-commerce: meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md §8 (≥7 días y ventana de
# atribución madurada) y playbook-saas.md (trial → pago por cohorte). Valores de partida [HYPOTHESIS]: mídelos con
# `embudo.py cohortes` y cámbialos con --madurez.
MADUREZ = {"servicios": {"cualificados": 7, "citas": 14, "shows": 21, "clientes_pago": 56},
           "saas": {"pruebas": 7, "activaciones": 14, "clientes_pago": 28},
           "ecommerce": {"clientes_pago": 7}}
# Evento de optimización (nombres de la ficha y del §16, o action_type de Insights) → capa del registro.
CAPA_DE_EVENTO = {"lead": "leads", "contact": "leads", "submitapplication": "leads", "completeregistration": "leads",
                  "diagnosticocompletado": "leads", "leadcualificado": "cualificados", "qualifiedlead": "cualificados",
                  "schedule": "citas", "llamadaasistida": "shows", "starttrial": "pruebas",
                  "subscribe": "clientes_pago", "purchase": "clientes_pago"}
_ACCION_A_CAPA = (("schedule", "citas"), ("starttrial", "pruebas"), ("subscribe", "clientes_pago"),
                  ("purchase", "clientes_pago"), ("completeregistration", "leads"), ("submitapplication", "leads"),
                  ("contact", "leads"), ("lead", "leads"))
NOMBRE_CAPA = {"clientes_pago": "clientes de pago", "shows": "shows", "citas": "citas",
               "cualificados": "cualificados", "leads": "leads", "resultado_meta": "resultados de Meta",
               "activaciones": "activaciones", "pruebas": "pruebas"}
CAMPOS_NEGOCIO = ("leads", "cualificados", "citas", "shows", "pruebas", "activaciones", "clientes_pago", "cash")

# Alias de cabecera (normalizados: minúsculas, sin acentos, todo lo que no es letra o número → espacio).
# Un alias que acaba en «*» se compara como prefijo.
ALIAS_META = {
    "ad_id": ["ad id", "anuncio id", "identificador del anuncio", "id del anuncio", "id anuncio"],
    "nombre": ["ad name", "nombre del anuncio", "anuncio", "nombre"],
    "campana": ["campaign name", "nombre de la campana", "campana"],
    "conjunto": ["ad set name", "adset name", "nombre del conjunto de anuncios", "conjunto"],
    "gasto": ["spend", "gasto", "gasto eur", "amount spent*", "importe gastado*"],
    "impresiones": ["impressions", "impresiones"],
    "clics": ["inline link clicks", "clics enlace", "link clicks", "clics en el enlace"],
    "vistas_3s": ["vistas 3s", "video 3s", "video view", "3 second video plays", "3 second video views",
                  "reproducciones de video de 3 segundos*"],
    "thruplay": ["thruplay", "thruplays", "video thruplay watched actions", "reproducciones de thruplay*"],
    "resultado": ["resultado meta", "resultados", "results", "leads"],
    "inicio": ["desde", "date start", "reporting starts", "inicio del informe"],
    "fin": ["hasta", "date stop", "reporting ends", "fin del informe"],
    "evento": ["evento resultado", "indicador de resultado", "result indicator", "tipo de resultado", "result type"],
}
ALIAS_NEGOCIO = {
    "ad_id": ["ad id", "anuncio id", "identificador del anuncio"],
    "nombre": ["utm content", "anuncio", "ad name", "nombre del anuncio", "nombre"],
    "leads": ["leads", "registros", "contactos", "signups", "altas"],
    "cualificados": ["cualificados", "leads cualificados", "qualified", "mql", "sql"],
    "citas": ["citas", "agendas", "appointments", "booked", "reservas"],
    "shows": ["shows", "asistencias", "asistidas", "showed"],
    "pruebas": ["pruebas", "trials", "trial"],
    "activaciones": ["activaciones", "activados", "activated", "activations"],
    "clientes_pago": ["clientes pago", "clientes de pago", "ventas", "won", "ganadas", "clientes",
                      "paying customers", "customers", "sales"],
    "cash": ["cash", "importe", "cobrado", "ingresos", "revenue", "valor"],
}


class ErrorUsuario(Exception):
    pass


# ---------------------------------------------------------------- lectura de CSV
def _norm(texto: str) -> str:
    t = "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def leer_csv(ruta: str | pathlib.Path) -> list[dict]:
    p = pathlib.Path(ruta)
    if not p.is_file():
        raise ErrorUsuario(f"No existe el archivo {ruta}")
    texto = p.read_text(encoding="utf-8-sig", errors="replace")
    if not texto.strip():
        return []
    try:
        dialecto = csv.Sniffer().sniff(texto[:8192], delimiters=",;\t")
    except csv.Error:
        dialecto = csv.excel
    return list(csv.DictReader(io.StringIO(texto), dialect=dialecto))


def _mapa(cabeceras: list[str], alias: dict[str, list[str]]) -> dict[str, str]:
    """campo → cabecera real, respetando el orden de preferencia de los alias."""
    normal = {_norm(h): h for h in cabeceras if h is not None}
    out = {}
    for campo, opciones in alias.items():
        for op in opciones:
            if op.endswith("*"):
                real = next((h for n, h in normal.items() if n.startswith(op[:-1])), None)
            else:
                real = normal.get(op)
            if real is not None and real not in out.values():
                out[campo] = real
                break
    return out


def num(texto, entero: bool = False) -> float | None:
    """Número de una exportación o de la ficha, con la regla única de `_comun.numero` («1.234,56», «1,200», «4.800»,
    «1 200 €», «0.175»…). `entero` se conserva por compatibilidad: la regla ya no depende de él."""
    return _comun.numero(texto)


def num_humano(texto: str) -> float | None:
    """Número escrito a mano en la ficha («1.200 €» = 1200, «0.175» = 0.175): la misma regla que `num`."""
    return _comun.numero(texto)


# ---------------------------------------------------------------- Meta
def agregar_meta(filas: list[dict]) -> dict[str, dict]:
    if not filas:
        return {}
    m = _mapa(list(filas[0].keys()), ALIAS_META)
    if "ad_id" not in m:
        raise ErrorUsuario("La exportación de Meta no tiene columna de ID del anuncio (ad_id / «Identificador del "
                           "anuncio»). Añádela en Ads Manager o usa `meta_ads.py anuncios`.")
    out: dict[str, dict] = {}
    redondeados = 0
    for f in filas:
        ad = (f.get(m["ad_id"]) or "").strip()
        gasto_fila = num(f.get(m["gasto"])) if "gasto" in m else None
        if not re.fullmatch(r"\d{5,25}", ad):  # filas de totales o vacías
            if id_redondeado(ad) and (gasto_fila or 0) > 0:
                redondeados += 1
            continue
        d = out.setdefault(ad, {"ad_id": ad, "nombre": "", "campana": "", "conjunto": "", "inicio": "", "fin": "",
                                "primer_gasto": "", "eventos": set(),
                                **{k: 0.0 for k in ("gasto", "impresiones", "clics", "vistas_3s", "thruplay",
                                                    "resultado")}, "_tiene": set()})
        for campo in ("nombre", "campana", "conjunto"):
            if campo in m and (f.get(m[campo]) or "").strip():
                d[campo] = f[m[campo]].strip()
        inicio = fin = ""
        if "inicio" in m:
            mi = re.search(r"\d{4}-\d{2}-\d{2}", f.get(m["inicio"]) or "")
            inicio = mi.group(0) if mi else ""
            if inicio and (not d["inicio"] or inicio < d["inicio"]):
                d["inicio"] = inicio
        if "fin" in m:
            mf = re.search(r"\d{4}-\d{2}-\d{2}", f.get(m["fin"]) or "")
            fin = mf.group(0) if mf else ""
            if fin and fin > d["fin"]:
                d["fin"] = fin
        # Fila de un solo día con gasto (exportación por día): el anuncio ya gastaba ese día.
        if inicio and inicio == fin and (gasto_fila or 0) > 0 and (not d["primer_gasto"] or inicio < d["primer_gasto"]):
            d["primer_gasto"] = inicio
        if "evento" in m and (f.get(m["evento"]) or "").strip():
            d["eventos"].add(f[m["evento"]].strip())
        for campo in ("gasto", "impresiones", "clics", "vistas_3s", "thruplay", "resultado"):
            if campo in m:
                v = num(f.get(m[campo]), entero=campo != "gasto")
                if v is None and campo == "resultado" and (gasto_fila or 0) > 0:
                    v = 0.0  # Ads Manager deja la celda vacía (o «—») cuando no hay resultados: es un 0
                if v is not None:
                    d[campo] += v
                    d["_tiene"].add(campo)
    if redondeados:
        raise ErrorUsuario(aviso_id_redondeado(redondeados))
    return out


def id_redondeado(ad: str) -> bool:
    """«1.20212E+17» o «120212345678901234.0»: un ID que la hoja de cálculo ha convertido en número."""
    return bool(re.fullmatch(r"\d+(?:[.,]\d+)?[eE][+]?\d+|\d{5,25}[.,]0+", (ad or "").strip()))


def aviso_id_redondeado(filas: int) -> str:
    return (f"{filas} filas con datos traen el ID del anuncio en notación científica o con decimales (p. ej. "
            "«1.20212E+17»): la hoja de cálculo lo ha redondeado y ya no se puede recuperar. Exporta de nuevo sin "
            "abrirlo en Excel o Sheets, o con la columna como texto.")


# ---------------------------------------------------------------- negocio
def agregar_negocio(filas: list[dict], fuente: str) -> tuple[dict[str, dict], dict[str, dict], set[str]]:
    """(por ad_id, por nombre, columnas presentes)."""
    if not filas:
        return {}, {}, set()
    m = _mapa(list(filas[0].keys()), ALIAS_NEGOCIO)
    if "ad_id" not in m and "nombre" not in m:
        raise ErrorUsuario(f"El CSV de {fuente} necesita una columna ad_id o utm_content (nombre del anuncio)")
    presentes = {c for c in CAMPOS_NEGOCIO if c in m}
    if not presentes:
        raise ErrorUsuario(f"El CSV de {fuente} no tiene ninguna columna de resultados reconocible "
                           f"({', '.join(CAMPOS_NEGOCIO)})")
    por_id: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    por_nombre: dict[str, dict] = defaultdict(lambda: defaultdict(float))
    for f in filas:
        ad = (f.get(m["ad_id"]) or "").strip() if "ad_id" in m else ""
        nombre = (f.get(m["nombre"]) or "").strip() if "nombre" in m else ""
        if "%" in nombre or "+" in nombre:
            nombre = urllib.parse.unquote_plus(nombre)
        destino = por_id[ad] if re.fullmatch(r"\d{5,25}", ad) else (por_nombre[nombre] if nombre else None)
        if destino is None:
            continue
        for c in presentes:
            v = num(f.get(m[c]), entero=c != "cash")
            if v is not None:
                destino[c] += v
    return dict(por_id), dict(por_nombre), presentes


# ---------------------------------------------------------------- objetivos
_FILAS_FICHA = [
    (r"coste por venta|cac", ["clientes_pago"]),
    (r"coste por lead cualificado", ["cualificados"]),
    (r"coste por cita", ["citas", "shows"]),
    (r"coste por prueba", ["pruebas", "activaciones"]),
    (r"^cpl\b", ["leads"]),
]


def objetivos_ficha(texto: str) -> dict[str, float]:
    """Lee la columna «Target» de la tabla «Economía» del cuerpo de la ficha."""
    out: dict[str, float] = {}
    i_target = None
    for linea in texto.splitlines():
        if not linea.strip().startswith("|"):
            if i_target is not None and linea.strip():
                i_target = None
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        normal = [_norm(c) for c in celdas]
        if "target" in normal or "objetivo" in normal:
            i_target = normal.index("target") if "target" in normal else normal.index("objetivo")
            continue
        if i_target is None or i_target >= len(celdas) or all(re.fullmatch(r":?-+:?", c) for c in celdas if c):
            continue
        metrica = normal[0]
        valores = [v for v in (num_humano(x) for x in celdas[i_target].split("/")) if v and v > 0]
        for patron, capas in _FILAS_FICHA:
            if re.search(patron, metrica):
                for capa, v in zip(capas, valores):
                    out.setdefault(capa, v)
                break
    return out


def _objetivos_cli(pares: list[str]) -> dict[str, float]:
    out = {}
    validas = set().union(*CAPAS.values())
    for p in pares or []:
        if "=" not in p:
            raise ErrorUsuario(f"--objetivo va como capa=valor (p. ej. citas=120): {p!r}")
        capa, valor = p.split("=", 1)
        capa = capa.strip()
        if capa not in validas:
            raise ErrorUsuario(f"Capa '{capa}' no válida: usa {', '.join(sorted(validas))}")
        v = num(valor)
        if not v or v <= 0:
            raise ErrorUsuario(f"El objetivo de {capa} debe ser un número > 0")
        out[capa] = v
    return out


def modelo_de(tipo: str) -> str:
    return {"saas": "saas", "app": "saas", "ecommerce": "ecommerce"}.get(str(tipo).lower(), "servicios")


def capa_de_evento(evento: str) -> str | None:
    """«Schedule», «LEAD», «lead_cualificado», «offsite_conversion.fb_pixel_schedule», «actions:schedule_total»… →
    capa del registro. None si no se reconoce (p. ej. una conversión personalizada)."""
    t = re.sub(r"[^a-z]", "", str(evento or "").lower())
    if not t:
        return None
    if t in CAPA_DE_EVENTO:
        return CAPA_DE_EVENTO[t]
    if "cualificad" in t or "qualified" in t:
        return "cualificados"
    return next((capa for patron, capa in _ACCION_A_CAPA if patron in t), None)


def madurez_de(modelo: str, dias_madurez: int | None = None, pares: list[str] | None = None) -> dict[str, int]:
    """Días de madurez de cada capa profunda: `MADUREZ`, todas a `dias_madurez` si se da, y `capa=días` encima."""
    out = {c: (dias_madurez if dias_madurez is not None else MADUREZ[modelo].get(c, 14))
           for c in CAPAS[modelo] if c not in CAPAS_SUPERFICIALES}
    for p in pares or []:
        capa, _, valor = p.partition("=")
        capa = capa.strip()
        if capa not in out:
            raise ErrorUsuario(f"--madurez va como capa=días con una capa de {', '.join(out)}: {p!r}")
        if not re.fullmatch(r"\d{1,3}", valor.strip()):
            raise ErrorUsuario(f"--madurez {capa}: los días son un entero ≥ 0: {p!r}")
        out[capa] = int(valor)
    return out


# ---------------------------------------------------------------- utilidades
def _f(v) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return num(v)


def _fmt(v, dec: int = 2) -> str:
    """Número con punto decimal y sin ceros sobrantes (contrato §6): 120.50 → «120.5»."""
    if v is None or v == "":
        return ""
    v = float(v)
    if math.isnan(v) or math.isinf(v):
        return ""
    s = f"{v:.{dec}f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def _cnt(v) -> str:
    return "" if v is None or v == "" else str(int(round(float(v))))


def poisson_cdf(k: int, lam: float) -> float:
    if lam <= 0:
        return 1.0
    total, termino = 0.0, math.exp(-lam)
    for i in range(int(k) + 1):
        if i:
            termino *= lam / i
        total += termino
    return min(1.0, total)


def _euros(v: float) -> str:
    return f"{v:,.2f}".replace(",", "·").replace(".", ",").replace("·", ".")


# ---------------------------------------------------------------- veredicto
def referencias(filas: list[dict], capas: list[str], objetivos: dict[str, float]) -> dict[str, dict]:
    out = {}
    for capa in capas:
        if capa in objetivos:
            out[capa] = {"valor": objetivos[capa], "origen": "objetivo"}
            continue
        con = [f for f in filas if _f(f.get(capa)) is not None and (_f(f.get("gasto")) or 0) > 0]
        eventos = sum(_f(f[capa]) for f in con)
        if eventos >= N_MEDIA:
            out[capa] = {"valor": sum(_f(f["gasto"]) for f in con) / eventos, "origen": "media de la cuenta"}
    return out


def capa_decision(filas: list[dict], capas: list[str]) -> str | None:
    for capa in capas:
        if any((_f(f.get(capa)) or 0) >= N_DECIDIR for f in filas):
            return capa
    return None


_SIN_EDAD = object()


def _nombre_ref(capa: str, ref: dict) -> str:
    """«citas» o, para los resultados de Meta, «resultados de Meta (citas)» si se sabe qué evento son."""
    return NOMBRE_CAPA[capa] + (f" ({NOMBRE_CAPA[ref['capa']]})" if capa == "resultado_meta" and ref.get("capa")
                                else "")


def veredicto(fila: dict, capas: list[str], refs: dict, decision: str | None, hoy: date, dias_madurez,
              medianas: dict, edad=_SIN_EDAD) -> tuple[str, str, str]:
    """(veredicto, n_suficiente, motivo). `dias_madurez`: un entero para todas las capas profundas o {capa: días}.
    `edad`: días desde el inicio de la cohorte (None = sin fecha fiable); si no se da, sale de `fecha`."""
    gasto = _f(fila.get("gasto")) or 0.0
    if gasto <= 0:
        return "sin-datos", "no", "Sin gasto en el periodo exportado"
    if edad is _SIN_EDAD:
        try:
            edad = (hoy - date.fromisoformat(fila.get("fecha") or "")).days
        except ValueError:
            edad = None
    notas = []
    sin_fecha = False
    for capa in capas:
        k = _f(fila.get(capa))
        ref = refs.get(capa)
        if k is None or not ref:
            continue
        if capa not in CAPAS_SUPERFICIALES:
            dias = dias_madurez.get(capa, 14) if isinstance(dias_madurez, dict) else dias_madurez
            if edad is None:
                sin_fecha = True
                continue
            if edad < dias:
                notas.append(f"{NOMBRE_CAPA[capa]} sin madurar ({edad} días; madura a los {dias})")
                continue
        lam = gasto / ref["valor"]
        p = poisson_cdf(int(k), lam)
        if p < ALFA_DESCARTE:
            motivo = (f"{int(k)} {NOMBRE_CAPA[capa]} con {_euros(gasto)} de gasto ({lam:.1f}× el coste "
                      f"{'objetivo' if ref['origen'] == 'objetivo' else 'medio de la cuenta'} de "
                      f"{_euros(ref['valor'])} por {_nombre_ref(capa, ref)}): si rindiera a ese coste, la probabilidad "
                      f"de ver tan pocos sería del {p:.1%}")
            return "perdedor", "si", motivo
        if capa not in CAPAS_SUPERFICIALES and k >= N_DECIDIR:
            # Una capa de negocio madura, con n suficiente y sin descartar, manda sobre las de arriba: un CPL alto
            # con citas a su coste no es un perdedor (KB 13/01 principio 4: decide la capa más profunda que ha
            # madurado con muestra suficiente).
            break
    if sin_fecha:
        notas.append("capas de negocio sin juzgar: no hay fecha fiable del anuncio (ponle la nomenclatura o exporta "
                     "con `meta_ads.py anuncios --por-dia`)")
    nota_atencion = _nota_atencion(fila, medianas)
    if nota_atencion:
        notas.append(nota_atencion)
    sufijo = (". " + "; ".join(notas)) if notas else ""
    if decision is None:
        return "en-test", "no", f"Ningún anuncio tiene aún {N_DECIDIR} eventos en una capa de negocio{sufijo}"
    k = _f(fila.get(decision)) or 0.0
    ref = refs.get(decision)
    coste = gasto / k if k else None
    nombre = NOMBRE_CAPA[decision]
    if decision == "resultado_meta" and ref:
        nombre = _nombre_ref(decision, ref)
    if k >= N_DECIDIR and ref and coste <= ref["valor"]:
        etapa = ("candidato a confirmado: comprueba que aguanta al subir gasto"
                 if k >= N_CONFIRMAR and edad is not None and edad >= 7 else "provisional")
        motivo = (f"Ganador {etapa}: {int(k)} {nombre} a {_euros(coste)} (≤ "
                  f"{'objetivo' if ref['origen'] == 'objetivo' else 'media de la cuenta'} {_euros(ref['valor'])})")
        if ref["origen"] != "objetivo":
            motivo += "; fija el objetivo en la ficha para decidir contra el negocio"
        return "ganador", "si", motivo + sufijo
    if k >= N_DECIDIR:
        return "en-test", "si", (f"{int(k)} {nombre} a {_euros(coste)}, por encima de la referencia "
                                 f"{_euros(ref['valor']) if ref else '—'}: no gana; vigilar{sufijo}")
    return "en-test", "no", f"{int(k)} de {N_DECIDIR} {nombre} necesarios para decidir{sufijo}"


def _nota_atencion(fila: dict, medianas: dict) -> str | None:
    imp = _f(fila.get("impresiones")) or 0
    hr, ctr = _f(fila.get("hook_rate")), _f(fila.get("ctr"))
    mh, mc = medianas.get("hook_rate"), medianas.get("ctr")
    if imp >= IMPRESIONES_ATENCION and hr is not None and ctr is not None and mh and mc \
            and hr < 0.5 * mh and ctr < 0.5 * mc:
        return "candidato a apagar o iterar el hook: hook rate y CTR por debajo del 50 % de la mediana de la cuenta"
    return None


# ---------------------------------------------------------------- actualizar
_FILA_IDENTIDAD = re.compile(r"^\|\s*(\d{6,25})\s*\|\s*(pagina|página|colaboracion|colaboración)\b", re.I | re.M)


def identidades_leeme(dir_c: pathlib.Path) -> dict[str, str]:
    """ad_id → pagina|colaboracion según las tablas de identidades de los LEEME del cliente."""
    out: dict[str, str] = {}
    for leeme in sorted((dir_c / "creativos").glob("*/LEEME.md")):
        try:
            texto = leeme.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for ad, ident in _FILA_IDENTIDAD.findall(texto):
            out[ad] = "colaboracion" if ident.lower().startswith("colab") else "pagina"
    return out


def _leer_registro(ruta: pathlib.Path) -> tuple[list[dict], list[str]]:
    if not ruta.exists():
        return [], []
    with ruta.open(encoding="utf-8-sig", newline="") as h:
        r = csv.DictReader(h)
        filas = list(r)
        extra = [c for c in (r.fieldnames or []) if c and c not in COLUMNAS]
    return filas, extra


def _escribir_registro(ruta: pathlib.Path, filas: list[dict], extra: list[str]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=COLUMNAS + extra, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for f in filas:
            w.writerow({c: f.get(c, "") if f.get(c) is not None else "" for c in COLUMNAS + extra})
    tmp.replace(ruta)


def _capas_resultado_meta(datos_meta: dict[str, dict], ficha: dict, modelo: str) -> dict[str, str]:
    """ad_id → capa del evento que cuentan sus «resultados de Meta»: el de la fila (evento_resultado o «Indicador
    de resultado»), si no el `meta.evento_principal` de la ficha y, si tampoco se reconoce, lead (compra en
    e-commerce)."""
    base = "clientes_pago" if modelo == "ecommerce" else "leads"
    de_ficha = capa_de_evento(str((ficha.get("meta") or {}).get("evento_principal") or "")) or base
    out = {}
    for ad, d in datos_meta.items():
        capas_fila = {capa_de_evento(e) for e in d.get("eventos") or ()}
        capas_fila.discard(None)
        out[ad] = next(iter(capas_fila)) if len(capas_fila) == 1 else de_ficha
    return out


ULTIMA_EXPORTACION = "registro-creativo_ultima-exportacion.json"


def _guardar_ultima_exportacion(ruta: pathlib.Path, meta: str, datos_meta: dict[str, dict], hoy: date) -> None:
    """Qué anuncios y qué periodo trae la exportación con la que se ha actualizado el registro (hallazgo 19, I6):
    `elementos_creativos.py` analiza solo esos, para no mezclar cifras de periodos distintos."""
    desde = min((d["inicio"] for d in datos_meta.values() if d["inicio"]), default="")
    hasta = max((d["fin"] for d in datos_meta.values() if d["fin"]), default="")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    tmp = ruta.with_suffix(".json.tmp")
    tmp.write_text(json.dumps({"fecha": hoy.isoformat(), "desde": desde, "hasta": hasta,
                               "meta": pathlib.Path(meta).name, "ad_ids": sorted(datos_meta)},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(ruta)


def actualizar(slug: str, meta: str, ghl: str | None = None, stripe: str | None = None,
               objetivos_cli: list[str] | None = None, hoy: date | None = None, dias_madurez: int | None = None,
               simular: bool = False, madurez_cli: list[str] | None = None) -> dict:
    hoy = hoy or date.today()
    ficha = _comun.leer_ficha(slug)
    dir_c = _comun.ruta_cliente(slug)
    modelo = modelo_de(ficha.get("tipo", ""))
    capas = CAPAS[modelo]
    madurez = madurez_de(modelo, dias_madurez, madurez_cli)
    avisos: list[str] = []

    objetivos = objetivos_ficha((dir_c / "ficha.md").read_text(encoding="utf-8"))
    objetivos.update(_objetivos_cli(objetivos_cli or []))
    filas_meta = leer_csv(meta)
    datos_meta = agregar_meta(filas_meta)
    if not datos_meta:
        raise ErrorUsuario("La exportación de Meta no tiene ninguna fila con ID de anuncio")
    # Hallazgo 2 (I6): los resultados de Meta se juzgan contra el objetivo del evento que se optimiza, no contra el
    # CPL. Con un objetivo explícito de resultado_meta (ficha o --objetivo) se usa ese para todos.
    capa_rm: dict[str, str] = {}
    if "resultado_meta" not in objetivos:
        capa_rm = _capas_resultado_meta(datos_meta, ficha, modelo)
        unicas = set(capa_rm.values())
        if len(unicas) == 1 and next(iter(unicas)) in objetivos:
            objetivos["resultado_meta"] = objetivos[next(iter(unicas))]
        elif len(unicas) > 1:
            avisos.append("Los anuncios optimizan eventos distintos ("
                          + ", ".join(sorted(NOMBRE_CAPA[c] for c in unicas)) + "): cada uno se compara con el "
                          "objetivo de su evento y no se usa la media de la cuenta para los resultados de Meta")

    ruta = dir_c / "registro-creativo.csv"
    previas, extra = _leer_registro(ruta)
    if extra:
        avisos.append(f"registro-creativo.csv tiene columnas fuera del contrato ({', '.join(extra)}): se conservan "
                      "al final")
    filas: dict[str, dict] = {}
    for f in previas:
        ad = (f.get("ad_id") or "").strip()
        if ad:
            filas[ad] = {c: f.get(c, "") or "" for c in COLUMNAS + extra}

    for ad, d in datos_meta.items():
        f = filas.setdefault(ad, {c: "" for c in COLUMNAS + extra})
        f["ad_id"] = ad
        for c in ("nombre", "campana", "conjunto"):
            if d[c]:
                f[c] = d[c]
        p = nomenclatura.parsear_anuncio(f["nombre"])
        if p:
            f.update(fecha=p["fecha"].isoformat(), angulo=p["angulo"], concepto=p["concepto"], formato=p["formato"],
                     hook=p["hook"])
        elif d["primer_gasto"] and (not f["fecha"] or d["primer_gasto"] < f["fecha"]):
            # Hallazgo 17 (I6): sin nomenclatura, la fecha es el primer día con gasto de una exportación por día;
            # el inicio del periodo exportado no es la fecha del anuncio.
            f["fecha"] = d["primer_gasto"]
        # Inicio de la cohorte que se juzga: el del anuncio o el del periodo, si es posterior. Sin nomenclatura ni
        # exportación por día no hay fecha fiable y las capas de negocio no se juzgan.
        inicio_anuncio = p["fecha"].isoformat() if p else d["primer_gasto"]
        d["inicio_cohorte"] = max(inicio_anuncio, d["inicio"]) if inicio_anuncio else ""
        g, imp, tiene = d["gasto"], d["impresiones"], d["_tiene"]
        f["gasto"] = _fmt(g)
        f["impresiones"] = _cnt(imp)
        f["cpm"] = _fmt(g / imp * 1000) if imp else ""
        if "clics" in tiene:
            f["ctr"] = _fmt(d["clics"] / imp * 100) if imp else ""
        f["hook_rate"] = _fmt(d["vistas_3s"] / imp * 100) if imp and d["vistas_3s"] > 0 else ""
        f["hold_rate"] = _fmt(d["thruplay"] / d["vistas_3s"] * 100) if d["vistas_3s"] > 0 and "thruplay" in tiene else ""
        if "resultado" in tiene:
            f["resultado_meta"] = _cnt(d["resultado"])
            f["coste_resultado_meta"] = _fmt(g / d["resultado"]) if d["resultado"] else ""

    identidades = identidades_leeme(dir_c)
    for ad, f in filas.items():
        if not (f.get("identidad") or "").strip() and ad in identidades:
            f["identidad"] = identidades[ad]

    # resultados de negocio
    if not (ghl or stripe) and any(filas[ad].get(c) for ad in datos_meta for c in CAMPOS_NEGOCIO):
        avisos.append("Los resultados de negocio son los de la actualización anterior y el gasto es el de ahora: "
                      "pasa --ghl o --stripe del mismo periodo para no mezclar")
    nombre_a_ids: dict[str, set] = defaultdict(set)
    for ad, f in filas.items():
        if f.get("nombre"):
            nombre_a_ids[f["nombre"].strip()].add(ad)
    for fuente, ruta_csv in (("GHL", ghl), ("Stripe", stripe)):
        if not ruta_csv:
            continue
        por_id, por_nombre, presentes = agregar_negocio(leer_csv(ruta_csv), fuente)
        valores: dict[str, dict] = defaultdict(lambda: defaultdict(float))
        for ad, v in por_id.items():
            if ad not in filas:
                avisos.append(f"{fuente}: el anuncio {ad} no está en Meta ni en el registro; se ignora")
                continue
            for c, x in v.items():
                valores[ad][c] += x
        ambiguos: set[str] = set()  # anuncios cuyo resultado no se puede saber: se dejan como estaban, nunca a 0
        for nombre, v in por_nombre.items():
            ids = nombre_a_ids.get(nombre, set())
            if len(ids) != 1:
                ambiguos |= ids
                avisos.append(f"{fuente}: el nombre «{_comun.anonimizar(nombre)[:80]}» "
                              + ("no coincide con ningún anuncio" if not ids else
                                 f"lo comparten {len(ids)} anuncios; añade ad_id={{{{ad.id}}}} a las UTM")
                              + "; se ignora")
                continue
            for c, x in v.items():
                valores[next(iter(ids))][c] += x
        for ad in (set(datos_meta) | set(valores)) - (ambiguos - set(por_id)):
            # sin fila en la exportación de negocio = 0 en el periodo
            for c in presentes:
                filas[ad][c] = _fmt(valores.get(ad, {}).get(c, 0.0)) if c == "cash" else \
                    _cnt(valores.get(ad, {}).get(c, 0.0))

    for f in filas.values():
        g = _f(f.get("gasto"))
        citas, ventas = _f(f.get("citas")), _f(f.get("clientes_pago"))
        f["coste_cita"] = _fmt(g / citas) if g is not None and citas else ""
        f["coste_venta"] = _fmt(g / ventas) if g is not None and ventas else ""

    # veredictos (solo para los anuncios de esta exportación)
    actuales = [filas[ad] for ad in datos_meta]
    refs = referencias(actuales, capas, objetivos)
    refs_fila: dict[str, dict] = {}
    if capa_rm:
        if len(set(capa_rm.values())) == 1:
            if "resultado_meta" in refs:
                refs["resultado_meta"]["capa"] = next(iter(capa_rm.values()))
        else:
            refs.pop("resultado_meta", None)
            for ad, c in capa_rm.items():
                refs_fila[ad] = dict(refs)
                if c in objetivos:
                    refs_fila[ad]["resultado_meta"] = {"valor": objetivos[c], "origen": "objetivo", "capa": c}
    decision = capa_decision(actuales, capas)
    medianas = {}
    for c in ("hook_rate", "ctr"):
        vals = [_f(f[c]) for f in actuales if _f(f.get(c)) is not None and (_f(f.get("impresiones")) or 0)
                >= IMPRESIONES_ATENCION]
        medianas[c] = statistics.median(vals) if vals else None
    cuenta = defaultdict(int)
    for f in actuales:
        if (f.get("motivo") or "").strip().lower().startswith("manual:"):
            cuenta[f.get("veredicto") or "manual"] += 1
            continue
        inicio = datos_meta[f["ad_id"]]["inicio_cohorte"]
        edad = (hoy - date.fromisoformat(inicio)).days if inicio else None
        v, n, motivo = veredicto(f, capas, refs_fila.get(f["ad_id"], refs), decision, hoy, madurez, medianas,
                                 edad=edad)
        if v != f.get("veredicto"):
            f["fecha_veredicto"] = hoy.isoformat()
        f.update(veredicto=v, n_suficiente=n, motivo=motivo)
        cuenta[v] += 1

    orden = sorted(filas.values(), key=lambda f: (f.get("fecha") or "", f["ad_id"]), reverse=True)
    ruta_ultima = dir_c / "datos" / ULTIMA_EXPORTACION
    if not simular:
        _escribir_registro(ruta, orden, extra)
        _guardar_ultima_exportacion(ruta_ultima, meta, datos_meta, hoy)
    sin_nombre = [f["ad_id"] for f in actuales if not nomenclatura.parsear_anuncio(f.get("nombre", ""))]
    if sin_nombre:
        avisos.append(f"{len(sin_nombre)} anuncios sin nomenclatura: no se clasifican por ángulo ni concepto "
                      "(lista: sin-nomenclatura)")
    if not objetivos:
        avisos.append("La ficha no tiene objetivos de coste en la tabla «Economía»: se compara con la media de la "
                      "cuenta. Calcúlalos con economia.py y anótalos en la ficha")
    return {
        "cliente": slug, "fecha": hoy.isoformat(), "modelo": modelo, "archivo": str(ruta.relative_to(_comun.RAIZ)),
        "guardado": not simular, "anuncios_actualizados": len(actuales), "filas_totales": len(filas),
        "capa_decision": decision,
        "referencias": {c: {"valor": round(r["valor"], 2), "origen": r["origen"],
                            **({"capa": r["capa"]} if r.get("capa") else {})} for c, r in refs.items()},
        "madurez": madurez, "veredictos": dict(cuenta), "avisos": avisos,
        "ultima_exportacion": str(ruta_ultima.relative_to(_comun.RAIZ)),
    }


def sin_nomenclatura(slug: str, meta: str | None = None) -> list[dict]:
    if meta:
        filas = [{"ad_id": d["ad_id"], "nombre": d["nombre"], "gasto": d["gasto"]}
                 for d in agregar_meta(leer_csv(meta)).values()]
    else:
        ruta = _comun.ruta_cliente(slug) / "registro-creativo.csv"
        if not ruta.exists():
            raise ErrorUsuario(f"No existe {ruta.relative_to(_comun.RAIZ)}: pasa --meta o ejecuta antes actualizar")
        filas = [{"ad_id": f.get("ad_id", ""), "nombre": f.get("nombre", ""), "gasto": _f(f.get("gasto")) or 0}
                 for f in _leer_registro(ruta)[0]]
    out = []
    for f in filas:
        ok, msg = nomenclatura.validar("anuncio", f["nombre"] or "")
        if not ok:
            out.append({"ad_id": f["ad_id"], "nombre": f["nombre"], "gasto": round(f["gasto"] or 0, 2),
                        "motivo": msg})
    return sorted(out, key=lambda x: -x["gasto"])


# ---------------------------------------------------------------- CLI
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
    u = sub.add_parser("actualizar", help="cruza Meta con GHL/Stripe y recalcula veredictos")
    u.add_argument("--cliente", required=True)
    u.add_argument("--meta", required=True, help="CSV de anuncios de Meta")
    u.add_argument("--ghl", help="CSV por anuncio de GHL")
    u.add_argument("--stripe", help="CSV por anuncio de Stripe")
    u.add_argument("--objetivo", action="append", default=[], metavar="CAPA=VALOR",
                   help="coste objetivo por capa (citas=120); sustituye al de la ficha")
    u.add_argument("--fecha", help="fecha del veredicto, AAAA-MM-DD (por defecto, hoy)")
    u.add_argument("--madurez", action="append", default=[], metavar="CAPA=DÍAS",
                   help="días que tarda en madurar una capa (clientes_pago=42); por defecto, MADUREZ por modelo")
    u.add_argument("--dias-madurez", type=int, default=None,
                   help="los mismos días para todas las capas de negocio (antiguo; mejor --madurez)")
    u.add_argument("--simular", action="store_true", help="calcula sin escribir el registro")
    u.add_argument("--json", action="store_true")
    s = sub.add_parser("sin-nomenclatura", help="anuncios cuyo nombre no cumple la nomenclatura")
    s.add_argument("--cliente", required=True)
    s.add_argument("--meta", help="CSV de Meta (si no, se usa el registro)")
    s.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    try:
        if a.cmd == "actualizar":
            hoy = date.fromisoformat(a.fecha) if a.fecha else date.today()
            r = actualizar(a.cliente, a.meta, a.ghl, a.stripe, a.objetivo, hoy, a.dias_madurez, a.simular,
                           a.madurez)
            if a.json:
                print(json.dumps(r, ensure_ascii=False, indent=2))
            else:
                print(f"Registro creativo de {r['cliente']} ({r['modelo']}) · {r['fecha']}")
                print(f"- {r['anuncios_actualizados']} anuncios actualizados · {r['filas_totales']} en el registro"
                      + ("" if r["guardado"] else " · SIMULADO: no se ha escrito nada"))
                print(f"- Capa de decisión: {NOMBRE_CAPA.get(r['capa_decision'], 'ninguna con n suficiente')}")
                for c, ref in r["referencias"].items():
                    print(f"- Referencia {NOMBRE_CAPA[c]}: {_euros(ref['valor'])} ({ref['origen']})")
                print("- Veredictos: " + (", ".join(f"{k} {v}" for k, v in sorted(r["veredictos"].items())) or "—"))
                for av in r["avisos"]:
                    print(f"  Aviso: {av}")
                print(f"Archivo: {r['archivo']}")
            return 0
        filas = sin_nomenclatura(a.cliente, a.meta)
        if a.json:
            print(json.dumps(filas, ensure_ascii=False, indent=2))
        elif not filas:
            print("Todos los anuncios cumplen la nomenclatura.")
        else:
            print(f"{len(filas)} anuncios sin nomenclatura (de más a menos gasto):")
            for f in filas:
                print(f"- {f['ad_id']} · {f['nombre'] or '(sin nombre)'} · gasto {_euros(f['gasto'])}\n    {f['motivo']}")
        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ErrorUsuario as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except _comun.FichaInvalida as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
