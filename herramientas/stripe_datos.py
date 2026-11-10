#!/usr/bin/env python3
"""Stripe en SOLO LECTURA para SaaS: clientes, suscripciones (pruebas, estados, MRR), pagos y resultados por anuncio.
Solo hace GET con una clave restringida de lectura: no puede crear, cambiar, reembolsar ni cancelar nada.

  python3 -I herramientas/stripe_datos.py clientes --cliente nimbo [--desde AAAA-MM-DD --hasta AAAA-MM-DD]
  python3 -I herramientas/stripe_datos.py suscripciones --cliente nimbo [--desde --hasta]
  python3 -I herramientas/stripe_datos.py pagos --cliente nimbo [--desde --hasta]
  python3 -I herramientas/stripe_datos.py por-anuncio --cliente nimbo --desde 2026-10-01 --hasta 2026-10-31

Fechas: por defecto los últimos 7 días completos (hasta ayer), en la zona horaria de la ficha. Todas las órdenes
aceptan `--json` (agregados por pantalla) y `--sin-archivos` (no guarda nada: es lo que usa el brief diario).

Archivos (contrato §9):
- Una fila por cliente o pago (datos personales) → clientes/<slug>/privado/stripe-<orden>_<desde>_<hasta>.csv
- Agregados por anuncio → clientes/<slug>/datos/stripe-por-anuncio_<desde>_<hasta>.csv con ad_id, utm_content, campana,
  registros, pruebas, clientes_pago, cash, reembolsos, mrr, moneda (lo lee `registro_creativo.py`; utm_content es el
  nombre del anuncio).
- `por-anuncio` deja además una fila por cliente de Meta (IDs, fechas y sí/no, sin nombre ni email) en
  clientes/<slug>/privado/clientes-stripe_<desde>_<hasta>.csv con las columnas que lee `embudo.py cohortes --modelo saas`.

`por-anuncio` trabaja por cohorte: los clientes de Stripe creados en el periodo que traen origen de Meta en sus
metadatos, y lo que pasó después hasta hoy. Para que funcione, el registro de tu producto tiene que guardar en los
metadatos del cliente de Stripe `ad_id`, `utm_source`, `utm_campaign`, `utm_content`, `fbc` y `fbp` (lo monta
/implementar-capi; ver docs/guias/stripe.md §3). Si no están en el cliente, se buscan en la suscripción.
«Prueba» = suscripción con periodo de prueba. «Cliente de pago» = al menos un cargo cobrado con importe > 0.
«Cash» = cobrado neto de reembolsos, en la moneda de la ficha. «MRR» = suscripciones activas o en mora de la cohorte,
normalizadas a mes (sin descuentos ni impuestos; los precios por uso o por tramos no entran).

Credenciales (`.env`, nunca se imprimen): `STRIPE_KEY` o `STRIPE_KEY_<SLUG>`: clave RESTRINGIDA (rk_live_… o
rk_test_…) con permiso de lectura en Customers, Subscriptions, Charges y Prices. Una clave secreta (sk_…) se rechaza.
Versión de la API: `STRIPE_API_VERSION` (por defecto la de VERSION_API).

Códigos de salida: 0 bien · 1 error del usuario · 2 configuración (ficha, clave, permisos).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import pathlib
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone, tzinfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402

BASE = "https://api.stripe.com/v1"
VERSION_API = "2026-10-28.endive"  # la más reciente el 2026-11-09 (docs.stripe.com/api/versioning)
PAGINA = 100
# Monedas sin decimales en Stripe (JPY comprobada; el resto, de la lista de Stripe sin verificar el 2026-11-09).
# ISK y UGX se envían con dos decimales «00», así que van con 100.
SIN_DECIMALES = {"BIF", "CLP", "DJF", "GNF", "JPY", "KMF", "KRW", "MGA", "PYG", "RWF", "VND", "VUV", "XAF", "XOF",
                 "XPF"}
META = re.compile(r"(^|[^a-z])(fb|fb_ad|facebook|instagram|ig|meta)([^a-z]|$)", re.I)
MESES_POR_INTERVALO = {"day": 12 / 365.25, "week": 12 / 52.1775, "month": 1.0, "year": 12.0}
COLUMNAS_ANUNCIO = ["ad_id", "utm_content", "campana", "registros", "pruebas", "clientes_pago", "cash", "reembolsos",
                    "mrr", "moneda"]


class ErrorStripe(Exception):
    def __init__(self, mensaje: str, salida: int = 1):
        super().__init__(mensaje)
        self.salida = salida


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


# ---------------------------------------------------------------- conexión (solo GET)

class Stripe:
    def __init__(self, clave: str):
        self.clave = clave
        self.version = os.environ.get("STRIPE_API_VERSION") or VERSION_API
        self.prueba = clave.startswith("rk_test_")

    def lista(self, recurso: str, **params):
        """Recorre todas las páginas de un listado GET (más reciente primero)."""
        params = {"limit": PAGINA, **params}
        while True:
            try:
                datos = comun.get_json(f"{BASE}/{recurso}", params,
                                       {"Authorization": f"Bearer {self.clave}", "Stripe-Version": self.version})
            except RuntimeError as e:
                texto = str(e)
                if "HTTP 401" in texto:
                    raise ErrorStripe("Stripe rechaza la clave (401): revisa STRIPE_KEY (caducada o revocada).", 2) from None
                if "HTTP 403" in texto:
                    raise ErrorStripe(f"A la clave restringida le falta permiso de lectura para «{recurso}» (403). "
                                      "Añádelo en Stripe → Developers → API keys.", 2) from None
                raise ErrorStripe(f"Stripe: {texto[:300]}") from None
            lote = datos.get("data") or []
            yield from lote
            if not datos.get("has_more") or not lote:
                return
            params = {**params, "starting_after": lote[-1]["id"]}


def conectar(slug: str) -> Stripe:
    clave = comun.credencial("STRIPE_KEY", slug)
    if not clave:
        _salir(f"Falta STRIPE_KEY (o STRIPE_KEY_{slug.upper().replace('-', '_')}) en .env: una clave restringida de "
               "lectura (docs/guias/stripe.md §1).", 2)
    if not clave.startswith(("rk_live_", "rk_test_")):
        _salir("STRIPE_KEY no es una clave restringida (rk_…). Por seguridad no se usa una clave secreta: crea una "
               "restringida solo con lectura (docs/guias/stripe.md §1).", 2)
    return Stripe(clave)


# ---------------------------------------------------------------- fechas, importes y salida

def _zona(nombre: str) -> tzinfo:
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(nombre)
    except Exception:
        return datetime.now().astimezone().tzinfo or timezone.utc


def periodo(a: argparse.Namespace) -> tuple[date, date]:
    try:
        hasta = date.fromisoformat(a.hasta) if a.hasta else date.today() - timedelta(days=1)
        desde = date.fromisoformat(a.desde) if a.desde else hasta - timedelta(days=6)
    except ValueError:
        _salir("Fechas como AAAA-MM-DD.", 1)
    if desde > hasta:
        _salir("--desde es posterior a --hasta.", 1)
    return desde, hasta


def rango_unix(desde: date, hasta: date, zona: tzinfo) -> dict:
    return {"created[gte]": int(datetime.combine(desde, datetime.min.time(), zona).timestamp()),
            "created[lt]": int(datetime.combine(hasta + timedelta(days=1), datetime.min.time(), zona).timestamp())}


def importe(minimo, moneda: str) -> float:
    """Unidad mínima de Stripe → unidades de la moneda."""
    return float(minimo or 0) / (1 if str(moneda).upper() in SIN_DECIMALES else 100)


def neto(cargo: dict) -> float:
    """Cobrado neto de reembolsos de un cargo, en unidades de su moneda."""
    if cargo.get("status") != "succeeded" or not cargo.get("paid"):
        return 0.0
    capturado = cargo["amount_captured"] if cargo.get("amount_captured") is not None else cargo.get("amount")
    return importe(max(int(capturado or 0) - int(cargo.get("amount_refunded") or 0), 0), cargo.get("currency", ""))


def mrr(sub: dict) -> float:
    """Ingreso mensual recurrente de una suscripción (precio × cantidad normalizado a mes), en unidades."""
    total = 0.0
    for item in (sub.get("items") or {}).get("data") or []:
        precio = item.get("price") or {}
        rec = precio.get("recurring") or {}
        meses = MESES_POR_INTERVALO.get(rec.get("interval"))
        # Precios por uso (metered) o por tramos (sin unit_amount): no se pueden normalizar sin la factura → fuera.
        if not meses or precio.get("unit_amount") is None or rec.get("usage_type") == "metered":
            continue
        meses *= max(int(rec.get("interval_count") or 1), 1)
        total += importe(precio["unit_amount"], precio.get("currency", "")) * int(item.get("quantity") or 1) / meses
    return total


def _fecha(ts) -> str:
    return datetime.fromtimestamp(int(ts), timezone.utc).strftime("%Y-%m-%d %H:%M") if ts else ""


def _dia(ts, zona: tzinfo) -> str:
    """Día local (zona de la ficha) de un instante de Stripe, o "" si no hay."""
    return datetime.fromtimestamp(int(ts), zona).date().isoformat() if ts else ""


def guardar_csv(ruta: pathlib.Path, filas: list[dict], columnas: list[str]) -> str:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    try:
        return str(ruta.relative_to(comun.RAIZ))
    except ValueError:
        return str(ruta)


def _n(x: float, dec: int = 0) -> str:
    return f"{x:,.{dec}f}".replace(",", "·").replace(".", ",").replace("·", ".")


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2, default=str))


# ---------------------------------------------------------------- atribución

def atribucion(*metadatos: dict) -> dict:
    """Origen del cliente según los metadatos (el primero que tenga algo de Meta manda)."""
    for md in metadatos:
        md = md or {}
        fuente = str(md.get("utm_source") or "")
        ad_id = str(md.get("ad_id") or "").strip()
        if META.search(fuente) or md.get("fbc") or md.get("fbclid") or re.fullmatch(r"\d{5,25}", ad_id):
            return {"es_meta": True, "ad_id": ad_id if re.fullmatch(r"\d{5,25}", ad_id) else "",
                    "anuncio": str(md.get("utm_content") or ""), "campana": str(md.get("utm_campaign") or ""),
                    "utm_source": fuente}
    return {"es_meta": False, "ad_id": "", "anuncio": "", "campana": "", "utm_source": ""}


# ---------------------------------------------------------------- órdenes

def _ficha(slug: str) -> dict:
    try:
        return comun.leer_ficha(slug)
    except comun.FichaInvalida as e:
        _salir(str(e), 2)


def _privado(slug: str, nombre: str, desde: date, hasta: date) -> pathlib.Path:
    return comun.ruta_cliente(slug) / "privado" / f"stripe-{nombre}_{desde}_{hasta}.csv"


def _aviso_prueba(api: Stripe, como_json: bool) -> None:
    if api.prueba and not como_json:
        print("(clave de modo de prueba: datos del entorno de pruebas de Stripe)")


def cmd_clientes(a, api: Stripe, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    filas = []
    for c in api.lista("customers", **rango_unix(desde, hasta, zona)):
        at = atribucion(c.get("metadata"))
        filas.append({"customer_id": c["id"], "alta": _fecha(c.get("created")), "email": c.get("email") or "",
                      "nombre": c.get("name") or "", "de_meta": "sí" if at["es_meta"] else "no",
                      "utm_source": at["utm_source"], "campana": at["campana"], "anuncio": at["anuncio"],
                      "ad_id": at["ad_id"], "fbc": "sí" if (c.get("metadata") or {}).get("fbc") else "no"})
    de_meta = [f for f in filas if f["de_meta"] == "sí"]
    resumen = {"desde": desde, "hasta": hasta, "clientes": len(filas), "de_meta": len(de_meta),
               "de_meta_con_ad_id": sum(1 for f in de_meta if f["ad_id"]),
               "con_metadatos_de_origen": sum(1 for f in filas if f["utm_source"] or f["ad_id"]),
               "por_anuncio": dict(Counter(f["anuncio"] or f["ad_id"] or "(sin anuncio)" for f in de_meta).most_common(15))}
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "clientes", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    _aviso_prueba(api, a.json)
    print(f"Clientes de Stripe creados {desde} → {hasta}: {len(filas)} · de Meta: {len(de_meta)} "
          f"(con ad_id: {resumen['de_meta_con_ad_id']}) · con metadatos de origen: {resumen['con_metadatos_de_origen']}")
    for anuncio, n in resumen["por_anuncio"].items():
        print(f"  {n:>5}  {anuncio[:80]}")
    if filas and not resumen["con_metadatos_de_origen"]:
        print("Ningún cliente trae utm_* ni ad_id en metadatos: sin eso no se puede unir con los anuncios "
              "(docs/guias/stripe.md §3).")
    if resumen.get("csv_privado"):
        print(f"Detalle con datos personales: {resumen['csv_privado']} (no lo compartas ni lo subas a git)")


def cmd_suscripciones(a, api: Stripe, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    moneda = str(ficha.get("moneda") or "").upper()
    subs = list(api.lista("subscriptions", status="all", **rango_unix(desde, hasta, zona)))
    por_estado = Counter(s.get("status", "") for s in subs)
    pruebas = [s for s in subs if s.get("trial_start")]
    ahora = datetime.now(timezone.utc).timestamp()
    terminadas = [s for s in pruebas if s.get("trial_end") and s["trial_end"] < ahora]
    convertidas = [s for s in terminadas if s.get("status") in ("active", "past_due")]
    activas = list(api.lista("subscriptions", status="active"))
    mrr_total = sum(mrr(s) for s in activas if str(s.get("currency", moneda)).upper() == moneda)
    resumen = {"desde": desde, "hasta": hasta, "suscripciones_nuevas": len(subs), "por_estado": dict(por_estado),
               "pruebas_iniciadas": len(pruebas), "pruebas_terminadas": len(terminadas),
               "pruebas_convertidas": len(convertidas),
               "conversion_prueba_pct": round(len(convertidas) / len(terminadas) * 100, 1) if terminadas else None,
               "mrr_cuenta": round(mrr_total, 2), "suscripciones_activas": len(activas), "moneda": moneda}
    if a.json:
        return _json(resumen)
    _aviso_prueba(api, a.json)
    print(f"Suscripciones creadas {desde} → {hasta}: {len(subs)} · "
          + " · ".join(f"{k} {v}" for k, v in por_estado.items()))
    print(f"Pruebas: {len(pruebas)} iniciadas · {len(terminadas)} terminadas · {len(convertidas)} convertidas"
          + (f" ({resumen['conversion_prueba_pct']} %)" if terminadas else ""))
    print(f"MRR de la cuenta hoy: {_n(mrr_total, 2)} {moneda} en {len(activas)} suscripciones activas "
          "(sin descuentos ni impuestos)")


def cmd_pagos(a, api: Stripe, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    cargos = list(api.lista("charges", **rango_unix(desde, hasta, zona)))
    por_moneda: dict[str, float] = defaultdict(float)
    reembolsado: dict[str, float] = defaultdict(float)
    for c in cargos:
        m = str(c.get("currency", "")).upper()
        por_moneda[m] += neto(c)
        reembolsado[m] += importe(c.get("amount_refunded"), m)
    filas = [{"charge_id": c["id"], "customer_id": c.get("customer") or "", "fecha": _fecha(c.get("created")),
              "importe": importe(c.get("amount"), c.get("currency", "")),
              "reembolsado": importe(c.get("amount_refunded"), c.get("currency", "")),
              "moneda": str(c.get("currency", "")).upper(), "estado": c.get("status", "")} for c in cargos]
    resumen = {"desde": desde, "hasta": hasta, "cargos": len(cargos),
               "por_estado": dict(Counter(c.get("status", "") for c in cargos)),
               "cobrado_neto": {k: round(v, 2) for k, v in por_moneda.items()},
               "reembolsado": {k: round(v, 2) for k, v in reembolsado.items() if v},
               "clientes_con_cobro": len({c.get("customer") for c in cargos if neto(c) > 0})}
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "pagos", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    _aviso_prueba(api, a.json)
    print(f"Cargos {desde} → {hasta}: {len(cargos)} · cobrado neto "
          + (", ".join(f"{_n(v, 2)} {k}" for k, v in por_moneda.items()) or "0")
          + f" · {resumen['clientes_con_cobro']} clientes con cobro"
          + (" · reembolsado " + ", ".join(f"{_n(v, 2)} {k}" for k, v in resumen["reembolsado"].items())
             if resumen["reembolsado"] else ""))
    if resumen.get("csv_privado"):
        print(f"Detalle: {resumen['csv_privado']}")


def por_anuncio(api: Stripe, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> tuple[list, list, dict]:
    moneda = str(ficha.get("moneda") or "").upper()
    rango = rango_unix(desde, hasta, zona)
    clientes = list(api.lista("customers", **rango))
    ids = {c["id"] for c in clientes}
    desde_cohorte = {"created[gte]": rango["created[gte]"]}  # lo que pasó después, hasta hoy
    subs_de: dict[str, list] = defaultdict(list)
    for s in api.lista("subscriptions", status="all", **desde_cohorte):
        if s.get("customer") in ids:
            subs_de[s["customer"]].append(s)
    cash_de: dict[str, float] = defaultdict(float)
    reemb_de: dict[str, float] = defaultdict(float)
    primer_cobro: dict[str, int] = {}
    otras: Counter = Counter()
    for c in api.lista("charges", **desde_cohorte):
        if c.get("customer") not in ids:
            continue
        if str(c.get("currency", "")).upper() != moneda:
            otras[str(c.get("currency", "")).upper()] += 1
            continue
        cash_de[c["customer"]] += neto(c)
        reemb_de[c["customer"]] += importe(c.get("amount_refunded"), moneda)
        if neto(c) > 0 and c.get("created"):
            primer_cobro[c["customer"]] = min(primer_cobro.get(c["customer"], c["created"]), c["created"])

    grupos: dict[tuple, dict] = {}
    detalle: list[dict] = []
    no_meta = 0
    for c in clientes:
        subs = subs_de.get(c["id"], [])
        at = atribucion(c.get("metadata"), *(s.get("metadata") for s in subs))
        if not at["es_meta"]:
            no_meta += 1
            continue
        prueba = any(s.get("trial_start") for s in subs)
        cash = cash_de.get(c["id"], 0.0)
        ingreso = sum(mrr(s) for s in subs if s.get("status") in ("active", "past_due")
                      and str(s.get("currency", moneda)).upper() == moneda)
        clave = (at["ad_id"], at["anuncio"])
        g = grupos.setdefault(clave, {"ad_id": at["ad_id"], "utm_content": at["anuncio"],
                                      "campana": at["campana"] if any(clave) else "(sin anuncio identificado)",
                                      "registros": 0, "pruebas": 0, "clientes_pago": 0, "cash": 0.0,
                                      "reembolsos": 0.0, "mrr": 0.0, "moneda": moneda})
        g["registros"] += 1
        g["pruebas"] += prueba
        g["clientes_pago"] += cash > 0
        g["cash"] = round(g["cash"] + cash, 2)
        g["reembolsos"] = round(g["reembolsos"] + reemb_de.get(c["id"], 0.0), 2)
        g["mrr"] = round(g["mrr"] + ingreso, 2)
        pago = _dia(primer_cobro.get(c["id"]), zona)
        vivas = [s for s in subs if s.get("status") in ("active", "past_due", "trialing", "unpaid", "incomplete")]
        fin = max((s.get("ended_at") or s.get("canceled_at") or 0 for s in subs), default=0)
        detalle.append({"customer_id": c["id"], "fecha": _dia(c.get("created"), zona), "ad_id": at["ad_id"],
                        "utm_content": at["anuncio"], "utm_campaign": at["campana"], "trial": int(prueba),
                        "fecha_primer_pago": pago, "cash": round(cash, 2), "fecha_cash": pago, "mrr": round(ingreso, 2),
                        "fecha_baja": _dia(fin, zona) if subs and not vivas else ""})
    filas = sorted(grupos.values(), key=lambda g: (not (g["ad_id"] or g["utm_content"]), -g["registros"]))
    de_meta = sum(g["registros"] for g in filas)
    identificados = sum(g["registros"] for g in filas if g["ad_id"] or g["utm_content"])
    resumen = {"desde": desde, "hasta": hasta, "cohorte": "clientes creados en el periodo; cobros hasta hoy",
               "clientes": len(clientes), "de_meta": de_meta, "no_meta": no_meta,
               "cobertura_anuncio_pct": round(identificados / de_meta * 100, 1) if de_meta else None,
               "cargos_en_otras_monedas": dict(otras), "moneda": moneda,
               "totales": {k: round(sum(g[k] for g in filas), 2)
                           for k in ("registros", "pruebas", "clientes_pago", "cash", "reembolsos", "mrr")}}
    return filas, detalle, resumen


def cmd_por_anuncio(a, api: Stripe, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    filas, detalle, resumen = por_anuncio(api, ficha, zona, desde, hasta)
    if not a.sin_archivos:
        resumen["csv"] = guardar_csv(comun.ruta_cliente(a.cliente) / "datos" / f"stripe-por-anuncio_{desde}_{hasta}.csv",
                                     filas, COLUMNAS_ANUNCIO)
        if detalle:
            resumen["csv_privado"] = guardar_csv(
                comun.ruta_cliente(a.cliente) / "privado" / f"clientes-stripe_{desde}_{hasta}.csv", detalle, list(detalle[0]))
    if a.json:
        return _json({**resumen, "por_anuncio": filas})
    _aviso_prueba(api, a.json)
    t = resumen["totales"]
    print(f"Cohorte {desde} → {hasta} · {resumen['de_meta']} clientes de Meta ({resumen['no_meta']} sin origen de "
          f"Meta en metadatos) · anuncio identificado en el {resumen['cobertura_anuncio_pct'] or 0} %")
    print(f"{'Anuncio':<52}{'Registros':>10}{'Pruebas':>8}{'Pago':>6}{'Cash':>11}{'MRR':>10}")
    for g in filas:
        print(f"{(g['anuncio'] or g['ad_id'] or g['campana'])[:51]:<52}{g['registros']:>10}{g['pruebas']:>8}"
              f"{g['clientes_pago']:>6}{_n(g['cash'], 2):>11}{_n(g['mrr'], 2):>10}")
    print(f"{'TOTAL':<52}{t['registros']:>10}{t['pruebas']:>8}{t['clientes_pago']:>6}{_n(t['cash'], 2):>11}"
          f"{_n(t['mrr'], 2):>10}")
    if resumen["cargos_en_otras_monedas"]:
        print(f"Aviso: cargos en otras monedas fuera del cash: {resumen['cargos_en_otras_monedas']}")
    print("Los pagos son de la cohorte hasta hoy: las pruebas recientes aún no han tenido tiempo de convertir.")
    if resumen.get("csv"):
        print(f"CSV: {resumen['csv']}" + (f" · un cliente por fila (para `embudo.py cohortes --modelo saas`): "
                                          f"{resumen['csv_privado']}" if resumen.get("csv_privado") else ""))


def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", required=True, help="slug del cliente (clave, moneda y zona horaria)")
    comunes.add_argument("--desde", help="AAAA-MM-DD (por defecto, hace 7 días)")
    comunes.add_argument("--hasta", help="AAAA-MM-DD (por defecto, ayer)")
    comunes.add_argument("--json", action="store_true", help="agregados en JSON (sin datos personales)")
    comunes.add_argument("--sin-archivos", action="store_true", help="no guarda CSV (para el brief diario)")
    p = argparse.ArgumentParser(description="Stripe en solo lectura: clientes, suscripciones, pagos y resultados "
                                            "por anuncio.")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("clientes", parents=[comunes], help="clientes creados en el periodo y su origen")
    sub.add_parser("suscripciones", parents=[comunes], help="suscripciones nuevas, pruebas, conversión y MRR")
    sub.add_parser("pagos", parents=[comunes], help="cargos, cobrado neto y reembolsos")
    sub.add_parser("por-anuncio", parents=[comunes], help="registros, pruebas, clientes de pago y cash por anuncio")
    a = p.parse_args(argv)
    ficha = _ficha(a.cliente)
    zona = _zona(str(ficha.get("zona_horaria") or "UTC"))
    desde, hasta = periodo(a)
    api = conectar(a.cliente)
    ordenes = {"clientes": cmd_clientes, "suscripciones": cmd_suscripciones, "pagos": cmd_pagos,
               "por-anuncio": cmd_por_anuncio}
    try:
        ordenes[a.comando](a, api, ficha, zona, desde, hasta)
    except ErrorStripe as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
