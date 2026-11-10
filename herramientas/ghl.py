#!/usr/bin/env python3
"""GoHighLevel (HighLevel) en SOLO LECTURA por la API v2: contactos, oportunidades, citas, pagos y resultados por
anuncio. Es la vía desatendida (brief diario, informes) junto al MCP oficial de HighLevel; nunca escribe, nunca
manda mensajes y nunca borra: solo hace GET, más la búsqueda de contactos (`POST /contacts/search`, que solo lee).

  python3 -I herramientas/ghl.py contactos --cliente acme [--desde AAAA-MM-DD --hasta AAAA-MM-DD]
  python3 -I herramientas/ghl.py oportunidades --cliente acme [--desde --hasta]
  python3 -I herramientas/ghl.py citas --cliente acme [--desde --hasta] [--calendario ID]
  python3 -I herramientas/ghl.py pagos --cliente acme [--desde --hasta]
  python3 -I herramientas/ghl.py por-anuncio --cliente acme --desde 2026-10-01 --hasta 2026-10-31
        [--cualificado "Cualificado"] [--campo-anuncio <id de campo personalizado>]

Fechas: por defecto los últimos 7 días completos (hasta ayer), en la zona horaria de la ficha. Todas las órdenes
aceptan `--json` (agregados por pantalla) y `--sin-archivos` (no guarda nada: es lo que usa el brief diario).

Archivos (contrato §9):
- Con datos personales (una fila por contacto, cita o pago) → clientes/<slug>/privado/ghl-<orden>_<desde>_<hasta>.csv
- Agregados por anuncio → clientes/<slug>/datos/ghl-por-anuncio_<desde>_<hasta>.csv con ad_id, utm_content, campana,
  leads, cualificados, citas, shows, clientes_pago, cash, valor_ganado, moneda (lo lee `registro_creativo.py`;
  utm_content es el nombre del anuncio).
- `por-anuncio` deja además una fila por lead (IDs, fechas y sí/no, sin nombres ni contacto) en
  clientes/<slug>/privado/leads-ghl_<desde>_<hasta>.csv con las columnas que lee `embudo.py cohortes`.
- Por pantalla y en JSON, solo agregados: ni nombres, ni emails, ni teléfonos.

`por-anuncio` trabaja por cohorte: los contactos creados en el periodo que vienen de Meta y todo lo que les pasó
después (oportunidades, citas y pagos hasta hoy). El anuncio sale de:
1. el campo personalizado `--campo-anuncio` (con un ID numérico de anuncio o su nombre), si lo pasas;
2. el parámetro `ad_id` de la URL de llegada guardada en la atribución del contacto (lo pone la plantilla de UTMs de
   `meta_ads.py`);
3. `utm_content` (el nombre del anuncio).
HighLevel no guarda el ID del anuncio en el contacto (su esquema de atribución no tiene ese campo, comprobado el
2026-11-09). En formularios instantáneos, mapea el anuncio a un campo personalizado y usa `--campo-anuncio`.
«Cualificado» = oportunidad ganada o en una etapa igual o posterior a la primera cuyo nombre contiene `--cualificado`
(por defecto «cualific» o «qualif»). Las etapas de perdido o descarte («Perdido», «No cualificado», «Unqualified»…,
patrón `_comun.PATRON_ETAPA_PERDIDA`) no cuentan nunca, aunque vayan detrás en el pipeline; una oportunidad perdida en
una etapa normal («Propuesta enviada») sí, porque llegó hasta ahí. «Cita» = cualquier cita no cancelada; «show» =
estado showed o completed.

`contactos` exporta también `dnd` (sí/no) y `dnd_canales` («todos» si es el DND global, o los canales con «No molestar»
activo): `audiencias_meta.py` deja fuera esos contactos y, con `--bajas`, los pasa a la lista de exclusión.

`oportunidades` añade el motivo de pérdida (`motivo_perdida`, el nombre que tiene en HighLevel; scope
opportunities.readonly) a cada fila y lo cuenta en `por_motivo_perdida`. `citas` da dos show rates: el de siempre
(shows / citas ya celebradas, sin canceladas) y el estricto (`show_rate_estricto`: con las canceladas y reprogramadas
ya pasadas en el denominador), que es el que mide cuánto se pierde entre agendar y presentarse.

Credenciales (`.env`, nunca se imprimen): `GHL_TOKEN` (Private Integration Token de la sub-cuenta, solo con scopes
de lectura) y `GHL_LOCATION` (ID de la sub-cuenta), o `GHL_TOKEN_<SLUG>` y `GHL_LOCATION_<SLUG>` por cliente.
Cómo sacarlos: docs/guias/ghl-meta.md §1.

Códigos de salida: 0 bien · 1 error del usuario · 2 configuración (ficha, credenciales, scopes).
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import re
import statistics
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone, tzinfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402

BASE = "https://services.leadconnectorhq.com"
VERSION_API = "2021-07-28"          # contactos, oportunidades y pagos
VERSION_CALENDARIOS = "2021-04-15"  # calendarios y citas
POST_DE_LECTURA = {"/contacts/search"}  # la única petición que no es GET, y solo busca
PAGINA_CONTACTOS = 500
PAGINA = 100
DIAS_CITAS_FUTURAS = 60
META = re.compile(r"(^|[^a-z])(fb|fb_ad|facebook|instagram|ig|meta)([^a-z]|$)", re.I)
ESTADOS_CITA_NULA = {"cancelled", "invalid"}
ESTADOS_CANCELADA = {"cancelled", "rescheduled"}  # cuentan en el show rate estricto (invalid = prueba o duplicada)
ESTADOS_SHOW = {"showed", "completed"}
ESTADOS_COBRO = {"succeeded", "success", "paid", "completed", "partially_refunded", "refunded"}
COLUMNAS_ANUNCIO = ["ad_id", "utm_content", "campana", "leads", "cualificados", "citas", "shows", "clientes_pago", "cash",
                    "valor_ganado", "moneda"]


class ErrorGHL(Exception):
    def __init__(self, mensaje: str, salida: int = 1):
        super().__init__(mensaje)
        self.salida = salida


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


# ---------------------------------------------------------------- conexión (solo lectura)

class GHL:
    def __init__(self, token: str, location: str):
        self.token = token
        self.location = location

    def _cabeceras(self, version: str) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Version": version, "Accept": "application/json"}

    @staticmethod
    def _error(e: Exception) -> ErrorGHL:
        texto = str(e)
        if "HTTP 401" in texto:
            return ErrorGHL("HighLevel rechaza el token (401): revisa GHL_TOKEN o rótalo en Settings → Private "
                            "Integrations.", 2)
        if "HTTP 403" in texto:
            return ErrorGHL(f"HighLevel deniega el acceso (403): al token le falta un scope de lectura o la "
                            f"location no es la suya. Detalle: {texto[:200]}", 2)
        return ErrorGHL(f"HighLevel: {texto[:300]}")

    def get(self, ruta: str, params: dict, version: str = VERSION_API) -> dict:
        try:
            return comun.get_json(BASE + ruta, params, self._cabeceras(version))
        except RuntimeError as e:
            raise self._error(e) from None

    def buscar(self, ruta: str, cuerpo: dict) -> dict:
        """POST de búsqueda (solo lectura). Cualquier otra ruta se niega: esta herramienta nunca escribe."""
        if ruta not in POST_DE_LECTURA:
            raise ErrorGHL(f"ghl.py es de solo lectura: {ruta} no es una búsqueda permitida.", 1)
        peticion = urllib.request.Request(
            BASE + ruta, data=json.dumps(cuerpo).encode(), method="POST",
            headers={**self._cabeceras(VERSION_API), "Content-Type": "application/json", "User-Agent": "meta-ads-os/1.0"})
        ultimo = ""
        for intento in range(4):
            try:
                with urllib.request.urlopen(peticion, timeout=60) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                cuerpo_err = e.read().decode("utf-8", "ignore")
                if e.code in (400, 401, 403, 404, 422):
                    try:
                        msg = json.loads(cuerpo_err).get("message", cuerpo_err[:300])
                    except ValueError:
                        msg = cuerpo_err[:300]
                    raise self._error(RuntimeError(f"HTTP {e.code}: {msg}")) from None
                ultimo = f"HTTP {e.code}"  # 429 (ráfaga de 100 cada 10 s) o 5xx
            except urllib.error.URLError as e:
                ultimo = str(e.reason)
            time.sleep(10 if intento == 0 else 5 * (intento + 1))
        raise ErrorGHL(f"HighLevel no responde tras varios intentos ({ultimo}).")


def conectar(slug: str) -> GHL:
    token = comun.credencial("GHL_TOKEN", slug)
    location = comun.credencial("GHL_LOCATION", slug)
    sufijo = slug.upper().replace("-", "_")
    falta = [v for v, x in ((f"GHL_TOKEN (o GHL_TOKEN_{sufijo})", token),
                            (f"GHL_LOCATION (o GHL_LOCATION_{sufijo})", location)) if not x]
    if falta:
        _salir(f"Falta {' y '.join(falta)} en .env. Cómo sacarlos: docs/guias/ghl-meta.md §1.", 2)
    return GHL(token, location)


# ---------------------------------------------------------------- fechas y salida

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


def _instante(texto) -> datetime | None:
    if not texto:
        return None
    if isinstance(texto, (int, float)):
        return datetime.fromtimestamp(texto / 1000 if texto > 1e11 else texto, timezone.utc)
    try:
        dt = datetime.fromisoformat(str(texto).replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _dia_local(texto, zona: tzinfo) -> date | None:
    dt = _instante(texto)
    return dt.astimezone(zona).date() if dt else None


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


# ---------------------------------------------------------------- lecturas

def contactos(api: GHL, desde: date, hasta: date, zona: tzinfo) -> list[dict]:
    """Contactos creados en el periodo (día local de la ficha)."""
    gte = datetime.combine(desde, datetime.min.time(), zona).astimezone(timezone.utc)
    lte = datetime.combine(hasta + timedelta(days=1), datetime.min.time(), zona).astimezone(timezone.utc)
    cuerpo = {"locationId": api.location, "pageLimit": PAGINA_CONTACTOS,
              "filters": [{"field": "dateAdded", "operator": "range",
                           "value": {"gte": gte.isoformat().replace("+00:00", "Z"),
                                     "lte": lte.isoformat().replace("+00:00", "Z")}}],
              "sort": [{"field": "dateAdded", "direction": "asc"}]}
    salida: list[dict] = []
    pagina = 1
    while True:
        datos = api.buscar("/contacts/search", {**cuerpo, "page": pagina} if pagina == 1 or not salida
                           or not salida[-1].get("searchAfter") else {**cuerpo, "searchAfter": salida[-1]["searchAfter"]})
        lote = datos.get("contacts") or []
        salida += lote
        if len(lote) < PAGINA_CONTACTOS:
            break
        pagina += 1
    # Por si el filtro no se aplicara: se recorta en local al periodo pedido.
    return [c for c in salida if (d := _dia_local(c.get("dateAdded"), zona)) is None or desde <= d <= hasta]


def pipelines(api: GHL) -> dict[str, dict]:
    """pipeline_id → {nombre, etapas: {etapa_id: (posición, nombre)}}."""
    salida = {}
    for p in api.get("/opportunities/pipelines", {"locationId": api.location}).get("pipelines") or []:
        etapas = p.get("stages") or []
        if all("position" in e for e in etapas):
            etapas = sorted(etapas, key=lambda e: e["position"])
        salida[p["id"]] = {"nombre": p.get("name", ""),
                           "etapas": {e["id"]: (i, e.get("name", "")) for i, e in enumerate(etapas)}}
    return salida


def oportunidades(api: GHL, desde: date, hasta: date) -> list[dict]:
    params = {"location_id": api.location, "status": "all", "limit": PAGINA,
              "date": desde.strftime("%m-%d-%Y"), "endDate": hasta.strftime("%m-%d-%Y")}
    salida: list[dict] = []
    while True:
        datos = api.get("/opportunities/search", params)
        lote = datos.get("opportunities") or []
        salida += lote
        meta = datos.get("meta") or {}
        if len(lote) < PAGINA or not meta.get("startAfterId"):
            return salida
        params = {**params, "startAfter": meta.get("startAfter"), "startAfterId": meta["startAfterId"]}


def motivos_perdida(api: GHL) -> dict[str, str]:
    """lostReasonId → nombre del motivo (`GET /opportunities/lost-reason`). Si no se puede leer, {}: salen los IDs."""
    try:
        datos = api.get("/opportunities/lost-reason", {"locationId": api.location})
    except ErrorGHL:
        return {}
    return {str(x["id"]): str(x.get("name") or x["id"]) for x in datos.get("lostReasons") or []
            if isinstance(x, dict) and x.get("id")}


def calendarios(api: GHL) -> list[dict]:
    return api.get("/calendars/", {"locationId": api.location}, VERSION_CALENDARIOS).get("calendars") or []


def citas(api: GHL, inicio: datetime, fin: datetime, calendario: str | None = None) -> list[dict]:
    """Citas cuyo inicio cae entre inicio y fin, de un calendario o de todos (la API exige uno)."""
    ids = [calendario] if calendario else [c["id"] for c in calendarios(api)]
    salida = []
    for cid in ids:
        datos = api.get("/calendars/events", {"locationId": api.location, "calendarId": cid,
                                              "startTime": int(inicio.timestamp() * 1000),
                                              "endTime": int(fin.timestamp() * 1000)}, VERSION_CALENDARIOS)
        salida += [{**e, "calendarId": e.get("calendarId") or cid} for e in datos.get("events") or []]
    return salida


def pagos(api: GHL, desde: date, hasta: date) -> list[dict]:
    salida: list[dict] = []
    offset = 0
    while True:
        datos = api.get("/payments/transactions", {"altId": api.location, "altType": "location",
                                                   "startAt": desde.isoformat(), "endAt": hasta.isoformat(),
                                                   "limit": PAGINA, "offset": offset})
        lote = datos.get("data") or datos.get("transactions") or []
        salida += lote
        total = datos.get("totalCount") or datos.get("total")
        offset += len(lote)
        if len(lote) < PAGINA or (total is not None and offset >= int(total)):
            return salida


def cobrado(t: dict) -> float:
    """Importe neto cobrado de una transacción (en unidades de la moneda, no en céntimos)."""
    if str(t.get("status", "")).lower() not in ESTADOS_COBRO:
        return 0.0
    return max(float(t.get("amount") or 0) - float(t.get("amountRefunded") or 0), 0.0)


# ---------------------------------------------------------------- atribución

def _params_url(url: str | None) -> dict:
    if not url:
        return {}
    return {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlsplit(url).query).items()}


def atribucion(contacto: dict, campo_anuncio: str | None = None) -> dict:
    """Origen de Meta del contacto: es_meta, ad_id, anuncio (utm_content), campana, utm_source."""
    candidatas = [x for x in (contacto.get("attributions") or []) if isinstance(x, dict)]
    candidatas += [x for x in (contacto.get("attributionSource"), contacto.get("lastAttributionSource"))
                   if isinstance(x, dict)]
    candidatas.sort(key=lambda x: not x.get("isFirst"))  # primer toque delante, si viene marcado

    def de_meta(x: dict) -> bool:
        q = _params_url(x.get("url"))
        return bool(META.search(str(x.get("utmSource") or "")) or META.search(str(x.get("medium") or ""))
                    or x.get("fbclid") or x.get("fbc") or "fbclid" in q or "ad_id" in q)

    elegida = next((x for x in candidatas if de_meta(x)), candidatas[0] if candidatas else {})
    q = _params_url(elegida.get("url"))
    ad_id = q.get("ad_id", "")
    anuncio = elegida.get("utmContent") or q.get("utm_content") or ""
    if campo_anuncio:
        for cf in contacto.get("customFields") or contacto.get("customField") or []:
            if cf.get("id") == campo_anuncio and str(cf.get("value") or "").strip():
                valor = str(cf["value"]).strip()
                if re.fullmatch(r"\d{5,25}", valor):
                    ad_id = valor
                else:
                    anuncio = valor
    es_meta = de_meta(elegida) if elegida else False
    es_meta = es_meta or bool(campo_anuncio and (ad_id or anuncio)) or bool(META.search(str(contacto.get("source") or "")))
    return {"es_meta": es_meta, "ad_id": ad_id if re.fullmatch(r"\d{5,25}", ad_id) else "",
            "anuncio": urllib.parse.unquote_plus(anuncio), "utm_source": elegida.get("utmSource") or "",
            "campana": elegida.get("campaign") or q.get("utm_campaign") or "",
            "campaign_id": elegida.get("campaignId") or q.get("campaign_id") or ""}


# ---------------------------------------------------------------- órdenes

def _ficha(slug: str) -> dict:
    try:
        return comun.leer_ficha(slug)
    except comun.FichaInvalida as e:
        _salir(str(e), 2)


def _privado(slug: str, nombre: str, desde: date, hasta: date) -> pathlib.Path:
    return comun.ruta_cliente(slug) / "privado" / f"ghl-{nombre}_{desde}_{hasta}.csv"


def dnd_de(c: dict) -> list[str]:
    """Canales con «No molestar» activo: `dnd: true` es el global; `dndSettings.<Canal>.status` va por canal
    (active/permanent). Va al CSV privado para que `audiencias_meta.py` deje fuera a quien no quiere comunicaciones."""
    canales = [canal for canal, x in (c.get("dndSettings") or {}).items()
               if isinstance(x, dict) and str(x.get("status", "")).lower() in ("active", "permanent")]
    if c.get("dnd") is True or str(c.get("dnd", "")).lower() == "true":
        canales = ["todos"] + canales
    return canales


def cmd_contactos(a, api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    cs = contactos(api, desde, hasta, zona)
    filas = []
    for c in cs:
        at = atribucion(c, a.campo_anuncio)
        dnd = dnd_de(c)
        filas.append({"contact_id": c.get("id", ""), "fecha_alta": str(c.get("dateAdded", ""))[:19],
                      "nombre": " ".join(x for x in (c.get("firstName"), c.get("lastName")) if x),
                      "email": c.get("email") or "", "telefono": c.get("phone") or "",
                      "origen": c.get("source") or "", "de_meta": "sí" if at["es_meta"] else "no",
                      "utm_source": at["utm_source"], "campana": at["campana"], "anuncio": at["anuncio"],
                      "ad_id": at["ad_id"], "etiquetas": ";".join(c.get("tags") or []),
                      "dnd": "sí" if dnd else "no", "dnd_canales": ";".join(dnd)})
    de_meta = [f for f in filas if f["de_meta"] == "sí"]
    resumen = {"desde": desde, "hasta": hasta, "contactos": len(filas), "de_meta": len(de_meta),
               "de_meta_con_ad_id": sum(1 for f in de_meta if f["ad_id"]),
               "de_meta_con_anuncio": sum(1 for f in de_meta if f["ad_id"] or f["anuncio"]),
               "con_dnd": sum(1 for f in filas if f["dnd"] == "sí"),
               "por_dia": dict(sorted(Counter(str(_dia_local(c.get("dateAdded"), zona)) for c in cs).items())),
               "por_anuncio": dict(Counter(f["anuncio"] or f["ad_id"] or "(sin anuncio)" for f in de_meta).most_common(15))}
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "contactos", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    print(f"Contactos creados {desde} → {hasta}: {len(filas)} · de Meta: {len(de_meta)} · con anuncio identificado: "
          f"{resumen['de_meta_con_anuncio']} (con ad_id: {resumen['de_meta_con_ad_id']})")
    for anuncio, n in resumen["por_anuncio"].items():
        print(f"  {n:>5}  {anuncio[:80]}")
    if de_meta and resumen["de_meta_con_anuncio"] / len(de_meta) < 0.6:
        print("Menos del 60 % de los leads de Meta llegan con el anuncio: revisa las UTMs (docs/guias/ghl-meta.md §3).")
    if resumen.get("csv_privado"):
        print(f"Detalle con datos personales: {resumen['csv_privado']} (no lo compartas ni lo subas a git)")


def cmd_oportunidades(a, api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    pls = pipelines(api)
    ops = oportunidades(api, desde, hasta)
    motivos = motivos_perdida(api) if any(o.get("lostReasonId") for o in ops) else {}
    por_etapa: Counter = Counter()
    por_estado: Counter = Counter()
    por_motivo: Counter = Counter()
    valor_ganado = 0.0
    filas = []
    for o in ops:
        pl = pls.get(o.get("pipelineId"), {"nombre": o.get("pipelineId", ""), "etapas": {}})
        etapa = pl["etapas"].get(o.get("pipelineStageId"), (None, o.get("pipelineStageId", "")))[1]
        por_etapa[(pl["nombre"], etapa)] += 1
        por_estado[o.get("status", "")] += 1
        if o.get("status") == "won":
            valor_ganado += float(o.get("monetaryValue") or 0)
        motivo = motivos.get(str(o.get("lostReasonId")), str(o.get("lostReasonId"))) if o.get("lostReasonId") else ""
        if o.get("status") in ("lost", "abandoned") or motivo:
            por_motivo[motivo or "(sin motivo)"] += 1
        filas.append({"opportunity_id": o.get("id", ""), "contact_id": o.get("contactId", ""),
                      "pipeline": pl["nombre"], "etapa": etapa, "estado": o.get("status", ""),
                      "valor": o.get("monetaryValue") or 0, "creada": str(o.get("createdAt", ""))[:19],
                      "cambio_etapa": str(o.get("lastStageChangeAt", ""))[:19],
                      # marcar perdido no mueve la etapa: la fecha de la pérdida es la del cambio de estado
                      "cambio_estado": str(o.get("lastStatusChangeAt", ""))[:19], "motivo_perdida": motivo})
    resumen = {"desde": desde, "hasta": hasta, "oportunidades": len(ops), "por_estado": dict(por_estado),
               "valor_ganado": round(valor_ganado, 2), "moneda": ficha.get("moneda"),
               "por_etapa": [{"pipeline": p, "etapa": e, "n": n} for (p, e), n in sorted(por_etapa.items())],
               "por_motivo_perdida": dict(por_motivo.most_common())}
    sin_nombre = any(o.get("lostReasonId") for o in ops) and not motivos
    if sin_nombre:
        resumen["aviso"] = ("No he podido leer los nombres de los motivos de pérdida (¿falta el scope "
                            "opportunities.readonly?): salen sus IDs")
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "oportunidades", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    print(f"Oportunidades creadas {desde} → {hasta}: {len(ops)} · "
          + " · ".join(f"{k or '—'} {v}" for k, v in por_estado.items())
          + f" · valor ganado {_n(valor_ganado, 2)} {ficha.get('moneda', '')}")
    for x in resumen["por_etapa"]:
        print(f"  {x['n']:>5}  {x['pipeline'][:30]} › {x['etapa']}")
    if por_motivo:
        print("Perdidas por motivo: " + " · ".join(f"{k} {v}" for k, v in por_motivo.most_common()))
    if resumen.get("aviso"):
        print(f"Aviso: {resumen['aviso']}.")
    if resumen.get("csv_privado"):
        print(f"Detalle: {resumen['csv_privado']}")


def cmd_citas(a, api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    inicio = datetime.combine(desde, datetime.min.time(), zona)
    fin = datetime.combine(hasta + timedelta(days=1), datetime.min.time(), zona)
    cal = {c["id"]: c.get("name", c["id"]) for c in calendarios(api)} if not a.calendario else {}
    evs = citas(api, inicio, fin, a.calendario)
    por_estado = Counter(str(e.get("appointmentStatus", "")).lower() for e in evs)
    validas = [e for e in evs if str(e.get("appointmentStatus", "")).lower() not in ESTADOS_CITA_NULA]
    ahora = datetime.now(timezone.utc)
    pasadas = [e for e in validas if (_instante(e.get("startTime")) or fin) < ahora]
    shows = sum(1 for e in pasadas if str(e.get("appointmentStatus", "")).lower() in ESTADOS_SHOW)
    canceladas = [e for e in evs if str(e.get("appointmentStatus", "")).lower() in ESTADOS_CANCELADA]
    canceladas_pasadas = [e for e in canceladas if (_instante(e.get("startTime")) or fin) < ahora]
    estricto = len(pasadas) + len(canceladas_pasadas)
    filas = [{"event_id": e.get("id", ""), "calendario": cal.get(e.get("calendarId"), e.get("calendarId", "")),
              "contact_id": e.get("contactId", ""), "estado": e.get("appointmentStatus", ""),
              "inicio": str(e.get("startTime", ""))[:19], "reservada": str(e.get("dateAdded", ""))[:19]} for e in evs]
    resumen = {"desde": desde, "hasta": hasta, "citas": len(validas), "por_estado": dict(por_estado),
               "ya_celebradas": len(pasadas), "shows": shows,
               "show_rate": round(shows / len(pasadas) * 100, 1) if pasadas else None,
               "canceladas": len(canceladas), "canceladas_ya_pasadas": len(canceladas_pasadas),
               "show_rate_estricto": round(shows / estricto * 100, 1) if estricto else None,
               "por_calendario": dict(Counter(f["calendario"] for f in filas))}
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "citas", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    print(f"Citas con inicio {desde} → {hasta}: {len(validas)} válidas · "
          + " · ".join(f"{k or '—'} {v}" for k, v in por_estado.items()))
    if pasadas:
        print(f"Ya celebradas: {len(pasadas)} · shows {shows} · show rate {resumen['show_rate']} % "
              "(solo es fiable si el equipo marca showed/noshow)")
    if estricto:
        print(f"Show rate estricto: {resumen['show_rate_estricto']} % ({shows} de {estricto}: las celebradas más "
              f"{len(canceladas_pasadas)} canceladas o reprogramadas cuya hora ya pasó)")
    if resumen.get("csv_privado"):
        print(f"Detalle: {resumen['csv_privado']}")


def cmd_pagos(a, api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    ts = pagos(api, desde, hasta)
    por_moneda: dict[str, float] = defaultdict(float)
    for t in ts:
        por_moneda[str(t.get("currency") or ficha.get("moneda") or "").upper()] += cobrado(t)
    filas = [{"transaction_id": t.get("_id") or t.get("id", ""), "contact_id": t.get("contactId", ""),
              "importe": t.get("amount", ""), "reembolsado": t.get("amountRefunded", ""),
              "moneda": t.get("currency", ""), "estado": t.get("status", ""),
              "fecha": str(t.get("createdAt", ""))[:19], "origen": t.get("entitySourceType", "")} for t in ts]
    resumen = {"desde": desde, "hasta": hasta, "transacciones": len(ts),
               "por_estado": dict(Counter(str(t.get("status", "")) for t in ts)),
               "cobrado_neto": {k: round(v, 2) for k, v in por_moneda.items()},
               "clientes_con_cobro": len({t.get("contactId") for t in ts if cobrado(t) > 0})}
    if not a.sin_archivos and filas:
        resumen["csv_privado"] = guardar_csv(_privado(a.cliente, "pagos", desde, hasta), filas, list(filas[0]))
    if a.json:
        return _json(resumen)
    print(f"Pagos {desde} → {hasta}: {len(ts)} transacciones · cobrado neto "
          + (", ".join(f"{_n(v, 2)} {k}" for k, v in por_moneda.items()) or "0")
          + f" · {resumen['clientes_con_cobro']} contactos con cobro")
    if resumen.get("csv_privado"):
        print(f"Detalle: {resumen['csv_privado']}")


def _sin_tildes(texto) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", str(texto or "")) if not unicodedata.combining(c)).lower()


def etapa_perdida(nombre) -> bool:
    """«Perdido», «No cualificado», «Unqualified», «Descartado»…: nunca cuentan como cualificadas aunque vayan detrás
    de «Cualificado» en el pipeline (la guía ghl-meta.md pone «Perdido» al final). Patrón común en `_comun`."""
    return bool(re.search(comun.PATRON_ETAPA_PERDIDA, _sin_tildes(nombre)))


def _etapas_cualificadas(pls: dict, patrones: list[str]) -> dict[str, int]:
    """pipeline_id → posición de la primera etapa que cuenta como cualificada (las de perdido no cuentan)."""
    reg = re.compile("|".join(re.escape(p) for p in patrones) if patrones else r"cualific|qualif", re.I)
    salida = {}
    for pid, pl in pls.items():
        posiciones = [pos for pos, nombre in pl["etapas"].values() if reg.search(nombre) and not etapa_perdida(nombre)]
        if posiciones:
            salida[pid] = min(posiciones)
    return salida


def _llego_a_cualificado(o: dict, pls: dict, umbral: dict[str, int]) -> bool:
    """La etapa de la oportunidad está en o después de la primera cualificada y no es una etapa de perdido. Una
    oportunidad `lost` en «Propuesta enviada» sí llegó a cualificarse; una en «Perdido» o «No cualificado», no."""
    pid = o.get("pipelineId")
    if pid not in umbral:
        return False
    pos, nombre = pls[pid]["etapas"].get(o.get("pipelineStageId"), (-1, ""))
    return pos >= umbral[pid] and not etapa_perdida(nombre)


def por_anuncio(api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date, campo_anuncio: str | None,
                patrones: list[str]) -> tuple[list[dict], list[dict], dict]:
    """(filas por anuncio, detalle por contacto, resumen). Cohorte: contactos de Meta creados en el periodo."""
    moneda = str(ficha.get("moneda") or "").upper()
    hoy = date.today()
    cs = contactos(api, desde, hasta, zona)
    pls = pipelines(api)
    umbral = _etapas_cualificadas(pls, patrones)
    ops = oportunidades(api, desde, hoy)
    ahora = datetime.now(timezone.utc)
    evs = citas(api, datetime.combine(desde, datetime.min.time(), zona), ahora + timedelta(days=DIAS_CITAS_FUTURAS))
    ts = pagos(api, desde, hoy)

    ops_de: dict[str, list] = defaultdict(list)
    for o in ops:
        ops_de[o.get("contactId")].append(o)
    citas_de: dict[str, list] = defaultdict(list)
    for e in evs:
        citas_de[e.get("contactId")].append(e)
    cash_de: dict[str, float] = defaultdict(float)
    primer_cobro: dict[str, datetime] = {}
    otras_monedas: Counter = Counter()
    for t in ts:
        if str(t.get("currency") or moneda).upper() == moneda:
            cash_de[t.get("contactId")] += cobrado(t)
            cuando = _instante(t.get("createdAt"))
            if cobrado(t) > 0 and cuando and (t.get("contactId") not in primer_cobro
                                               or cuando < primer_cobro[t.get("contactId")]):
                primer_cobro[t.get("contactId")] = cuando
        elif cobrado(t):
            otras_monedas[str(t.get("currency")).upper()] += 1

    grupos: dict[tuple, dict] = {}
    detalle: list[dict] = []
    horas_hasta_cita: list[float] = []
    no_meta = 0
    for c in cs:
        at = atribucion(c, campo_anuncio)
        if not at["es_meta"]:
            no_meta += 1
            continue
        cid = c.get("id")
        sus_ops = ops_de.get(cid, [])
        ganada = any(o.get("status") == "won" for o in sus_ops)
        cualificado = ganada or any(_llego_a_cualificado(o, pls, umbral) for o in sus_ops)
        validas = [e for e in citas_de.get(cid, []) if str(e.get("appointmentStatus", "")).lower() not in ESTADOS_CITA_NULA]
        show = any(str(e.get("appointmentStatus", "")).lower() in ESTADOS_SHOW for e in validas)
        cash = cash_de.get(cid, 0.0)
        valor = sum(float(o.get("monetaryValue") or 0) for o in sus_ops if o.get("status") == "won")
        alta = _instante(c.get("dateAdded"))
        reservas = [r for e in validas if (r := _instante(e.get("dateAdded")))]
        if alta and reservas:
            horas_hasta_cita.append((min(reservas) - alta).total_seconds() / 3600)
        clave = (at["ad_id"], at["anuncio"]) if at["ad_id"] or at["anuncio"] else ("", "")
        g = grupos.setdefault(clave, {"ad_id": at["ad_id"], "utm_content": at["anuncio"],
                                      "campana": at["campana"] if clave != ("", "") else "(sin anuncio identificado)",
                                      "leads": 0, "cualificados": 0, "citas": 0, "shows": 0, "clientes_pago": 0,
                                      "cash": 0.0, "valor_ganado": 0.0, "moneda": moneda})
        g["leads"] += 1
        g["cualificados"] += cualificado
        g["citas"] += bool(validas)
        g["shows"] += show
        g["clientes_pago"] += bool(ganada or cash > 0)
        g["cash"] = round(g["cash"] + cash, 2)
        g["valor_ganado"] = round(g["valor_ganado"] + valor, 2)
        cobro = primer_cobro.get(cid)
        detalle.append({"contact_id": cid, "fecha": str(c.get("dateAdded", ""))[:19], "ad_id": at["ad_id"],
                        "utm_content": at["anuncio"], "utm_campaign": at["campana"], "cualificado": int(cualificado),
                        "cita": int(bool(validas)), "show": int(show), "venta": int(ganada or cash > 0),
                        "cash": round(cash, 2), "fecha_cash": cobro.astimezone(zona).date().isoformat() if cobro else ""})
    filas = sorted(grupos.values(), key=lambda g: (g["ad_id"] == "" and g["utm_content"] == "", -g["leads"]))
    total_meta = sum(g["leads"] for g in filas)
    identificados = sum(g["leads"] for g in filas if g["ad_id"] or g["utm_content"])
    resumen = {"desde": desde, "hasta": hasta, "cohorte": "contactos creados en el periodo; etapas hasta hoy",
               "contactos": len(cs), "de_meta": total_meta, "no_meta": no_meta,
               "cobertura_anuncio_pct": round(identificados / total_meta * 100, 1) if total_meta else None,
               "pipelines_sin_etapa_cualificada": [pl["nombre"] for pid, pl in pls.items() if pid not in umbral],
               "horas_hasta_cita_mediana": round(statistics.median(horas_hasta_cita), 1) if horas_hasta_cita else None,
               "pagos_en_otras_monedas": dict(otras_monedas),
               "totales": {k: round(sum(g[k] for g in filas), 2) for k in
                           ("leads", "cualificados", "citas", "shows", "clientes_pago", "cash", "valor_ganado")}}
    return filas, detalle, resumen


def cmd_por_anuncio(a, api: GHL, ficha: dict, zona: tzinfo, desde: date, hasta: date) -> None:
    filas, detalle, resumen = por_anuncio(api, ficha, zona, desde, hasta, a.campo_anuncio, a.cualificado or [])
    if not a.sin_archivos:
        resumen["csv"] = guardar_csv(comun.ruta_cliente(a.cliente) / "datos" / f"ghl-por-anuncio_{desde}_{hasta}.csv",
                                     filas, COLUMNAS_ANUNCIO)
        if detalle:
            resumen["csv_privado"] = guardar_csv(
                comun.ruta_cliente(a.cliente) / "privado" / f"leads-ghl_{desde}_{hasta}.csv", detalle, list(detalle[0]))
    if a.json:
        return _json({**resumen, "por_anuncio": filas})
    m = resumen["totales"]
    print(f"Cohorte {desde} → {hasta} · {resumen['de_meta']} contactos de Meta ({resumen['no_meta']} de otros "
          f"orígenes) · anuncio identificado en el {resumen['cobertura_anuncio_pct'] or 0} %")
    print(f"{'Anuncio':<52}{'Leads':>6}{'Cualif.':>8}{'Citas':>6}{'Shows':>6}{'Pago':>5}{'Cash':>11}")
    for g in filas:
        nombre = g["utm_content"] or g["ad_id"] or g["campana"]
        print(f"{nombre[:51]:<52}{g['leads']:>6}{g['cualificados']:>8}{g['citas']:>6}{g['shows']:>6}"
              f"{g['clientes_pago']:>5}{_n(g['cash'], 2):>11}")
    print(f"{'TOTAL':<52}{m['leads']:>6}{m['cualificados']:>8}{m['citas']:>6}{m['shows']:>6}"
          f"{m['clientes_pago']:>5}{_n(m['cash'], 2):>11}")
    if resumen["pipelines_sin_etapa_cualificada"]:
        print(f"Aviso: sin etapa «cualificado» en {', '.join(resumen['pipelines_sin_etapa_cualificada'])}: ahí solo "
              "cuenta la oportunidad ganada (usa --cualificado \"<nombre de etapa>\").")
    if resumen["horas_hasta_cita_mediana"] is not None:
        print(f"Del alta a la reserva de la cita: mediana de {_n(resumen['horas_hasta_cita_mediana'], 1)} h.")
    if resumen["cobertura_anuncio_pct"] is not None and resumen["cobertura_anuncio_pct"] < 60:
        print("Menos del 60 % con anuncio identificado: revisa las UTMs o usa --campo-anuncio (docs/guias/ghl-meta.md §3).")
    print("Ventas y citas son de la cohorte hasta hoy: los leads recientes aún no han tenido tiempo de convertir.")
    if resumen.get("csv"):
        print(f"CSV: {resumen['csv']}" + (f" · un lead por fila (para `embudo.py cohortes`): {resumen['csv_privado']}"
                                          if resumen.get("csv_privado") else ""))


def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", required=True, help="slug del cliente (credenciales y zona horaria)")
    comunes.add_argument("--desde", help="AAAA-MM-DD (por defecto, hace 7 días)")
    comunes.add_argument("--hasta", help="AAAA-MM-DD (por defecto, ayer)")
    comunes.add_argument("--json", action="store_true", help="agregados en JSON (sin datos personales)")
    comunes.add_argument("--sin-archivos", action="store_true", help="no guarda CSV (para el brief diario)")
    comunes.add_argument("--campo-anuncio", help="ID del campo personalizado con el ID o el nombre del anuncio")
    p = argparse.ArgumentParser(description="HighLevel en solo lectura: contactos, oportunidades, citas, pagos y "
                                            "resultados por anuncio.")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("contactos", parents=[comunes], help="contactos creados en el periodo y su origen")
    sub.add_parser("oportunidades", parents=[comunes], help="oportunidades por pipeline, etapa y estado")
    ci = sub.add_parser("citas", parents=[comunes], help="citas por estado y show rate")
    ci.add_argument("--calendario", help="ID de un calendario (por defecto, todos)")
    sub.add_parser("pagos", parents=[comunes], help="transacciones y cobrado neto")
    pa = sub.add_parser("por-anuncio", parents=[comunes], help="leads, cualificados, citas, shows y cash por anuncio")
    pa.add_argument("--cualificado", action="append", help="texto del nombre de la etapa que cuenta como cualificada")
    a = p.parse_args(argv)
    if not hasattr(a, "calendario"):
        a.calendario = None
    ficha = _ficha(a.cliente)
    zona = _zona(str(ficha.get("zona_horaria") or "UTC"))
    desde, hasta = periodo(a)
    api = conectar(a.cliente)
    ordenes = {"contactos": cmd_contactos, "oportunidades": cmd_oportunidades, "citas": cmd_citas,
               "pagos": cmd_pagos, "por-anuncio": cmd_por_anuncio}
    try:
        ordenes[a.comando](a, api, ficha, zona, desde, hasta)
    except ErrorGHL as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
