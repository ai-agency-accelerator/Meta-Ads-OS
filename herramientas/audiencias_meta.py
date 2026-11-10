#!/usr/bin/env python3
"""Audiencias de lista de clientes por etapa del CRM (solo biblioteca estándar).

Para qué: en un ciclo de venta largo, las etapas del pipeline (no se presentó, propuesta enviada, perdido por
timing, cliente) son audiencias con las que hacer anuncios pequeños y medibles, o listas con las que excluir. Esta
herramienta prepara esas listas hasheadas desde una exportación de GHL en `privado/`, deja aparte un grupo de
control para saber si los anuncios suman, las crea y las sincroniza en Meta y mide el resultado contra el control.
Guía: `docs/guias/anuncios-por-etapa.md`. Marco:
`meta-ads-kb/02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md`.

Leer y preparar (no toca Meta):
  python3 -I herramientas/audiencias_meta.py listar --cliente acme [--buscar ETAPA]
  python3 -I herramientas/audiencias_meta.py etapas --cliente acme \\
      --archivo clientes/acme/privado/ghl-oportunidades_2026-01-01_2026-11-08.csv \\
      --contactos clientes/acme/privado/ghl-contactos_2026-01-01_2026-11-08.csv --prefijo 34 --pais es \\
      [--control 0.2] [--control-en no-show,propuesta,perdido-timing] [--agrupar reenganche=no-show,propuesta] \\
      [--mapa "Reunión hecha=asistio,Nurture=ignorar"] [--por-anuncio] [--sin-archivos] [--sobrescribir]
  python3 -I herramientas/audiencias_meta.py medir --cliente acme \\
      --manifiesto clientes/acme/privado/audiencias/2026-11-09/manifiesto.json --archivo <exportación nueva>

Escribir en Meta (solo `operador-meta`, con un plan aprobado; exigen `--confirmo`, `--simular` no sale a la red):
  python3 -I herramientas/audiencias_meta.py crear "ETAPA_PROPUESTA_GHL" --cliente acme [--descripcion TXT] \\
      [--retencion 1..180] [--etiqueta QUALIFIED_LEADS] --confirmo
  python3 -I herramientas/audiencias_meta.py sincronizar <id> --cliente acme \\
      --archivo clientes/acme/privado/audiencias/2026-11-09/propuesta.csv --reemplazar --confirmo

Cómo funciona `etapas`:
- Cada oportunidad se lleva a una etapa del contrato §16 (lead, diagnostico, cualificado, llamada, asistio,
  propuesta, ganado, perdido) más `no-show` (agendó y no vino). Manda el estado (won → ganado; lost o abandoned →
  perdido); si no, el nombre de la etapa. Los nombres que no reconoce se listan y no entran: tradúcelos con --mapa.
  Las etapas que no son del §16 (un pipeline de taller, por ejemplo) se declaran como segmentos propios:
  --pipeline taller --mapa "Registrado=propio:registrado-sin-asistir,Asistió=propio:asistio-sin-llamada".
- Un contacto con varias oportunidades queda en la más avanzada; perdido solo si no tiene otra abierta o ganada.
  `perdido-timing` son los perdidos cuyo motivo (o, si la exportación no lo trae, una etiqueta como «mal-momento»)
  casa con --motivo-timing («ahora no», «más adelante», «timing»...) y cuya pérdida tiene entre 60 y 180 días
  (--dias-perdida; la fecha es el cambio de estado si la exportación lo trae y, si no, el último cambio de etapa).
  Los de fuera de la ventana o sin fecha siguen en `perdido` (para excluir) y se cuentan en el manifiesto.
- Se quitan los contactos con DND, baja u opt-out (columna o etiqueta); con --bajas van a `bajas.csv`, solo para una
  audiencia de exclusión. La columna DND sale de `ghl.py contactos` (`dnd`); si falta, se avisa. Los datos se normalizan y hashean con las funciones de `capi.py` (SHA-256 en minúsculas) y
  solo se escriben hashes, con las columnas de la plantilla de listas de clientes de Meta. `contact id` no se sube por
  defecto, y `nombre` tampoco si no hay columna de apellido (suele ser el nombre completo).
- Grupo de control: en los segmentos de --control-en, una fracción fija de contactos (--control) no se sube. La
  asignación sale de un hash de --semilla y el contacto: es la misma en cada refresco y en cada segmento, así que
  quien cae en control se queda en control. Para esos segmentos también se escribe `<segmento>-completa.csv`, con
  todos, que solo sirve para EXCLUIR (si excluyeras solo el tratamiento, el control vería tus otros anuncios).
- Escribe en clientes/<slug>/privado/audiencias/<fecha>/: un CSV por segmento, `asignacion.csv` (clave hasheada,
  segmento y grupo, para medir) y `manifiesto.json` (recuentos, columnas, mapa de etapas; sin datos personales).
  Con --por-anuncio, además clientes/<slug>/datos/etapas-por-anuncio_<fecha>.csv (agregados, sin datos personales).

Reglas de `crear` y `sincronizar`:
- Comprueban que la cuenta de la ficha ha aceptado las condiciones de listas de clientes; si no, dan el enlace.
- `crear` no duplica: si ya hay una audiencia con ese nombre, da su ID y no crea otra.
- `sincronizar` solo sube archivos de clientes/<slug>/privado/ del mismo cliente y con todas las celdas ya
  hasheadas: si encuentra texto en claro, no envía nada. Sube en lotes de 10.000 dentro de una sesión.
- `--reemplazar` usa `usersreplace`: cambia la lista entera sin reiniciar el aprendizaje de los conjuntos que la usan.
  Sin él, `users` añade a lo que hay (y añadir o quitar sí reinicia el aprendizaje). Borrar está bloqueado aquí.
- Cada escritura queda en logs/cambios.jsonl y la orden imprime la fila para el change log del cliente.

Credenciales (`.env`): `META_TOKEN` (o `META_TOKEN_<SLUG>`), el de `meta_ads.py`, con ads_management.
`META_APP_SECRET` opcional. La cuenta sale de `meta.cuenta` de la ficha.

Códigos de salida: 0 bien · 1 error del usuario (archivo, columnas, texto en claro, falta --confirmo, Meta rechaza) ·
2 configuración (ficha, token, cuenta de ejemplo, condiciones sin aceptar).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import re
import secrets
import statistics
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun as comun  # noqa: E402
import capi  # noqa: E402
import meta_ads  # noqa: E402

LOTE = 10_000  # máximo de registros por llamada a /users y /usersreplace [OFFICIAL META]
MINIMO_AVISO = 100  # [HYPOTHESIS] Meta no publica un mínimo para listas; por debajo apenas hay a quién mostrar
DIAS_ESTANCADA = 14  # [HYPOTHESIS] días en la misma etapa a partir de los cuales una oportunidad se avisa
URL_CONDICIONES = "https://business.facebook.com/ads/manage/customaudiences/tos/?act={cuenta}"

ETAPAS = ("lead", "diagnostico", "cualificado", "llamada", "asistio", "propuesta", "ganado", "perdido")  # §16
RANGO = {"lead": 0, "diagnostico": 1, "cualificado": 2, "llamada": 3, "no-show": 4, "asistio": 5, "propuesta": 6,
         "ganado": 7}
SEGMENTOS = ETAPAS + ("no-show", "perdido-timing")
CONTROL_EN = "no-show,propuesta,perdido-timing"
# Nombre visible de la etapa (sin tildes, en minúsculas) → etapa. El orden importa: «no cualificado» es perdido.
PATRONES = (
    ("perdido", comun.PATRON_ETAPA_PERDIDA),
    ("ganado", r"ganad|\bwon\b|firmad|purchase|contratad|closed won|venta cerrada"),
    ("no-show", r"no ?show|no asisti|no se present|no vino|ausente"),
    ("propuesta", r"propuest|proposal|presupuest|oferta enviada|quote"),
    ("asistio", r"asisti|\bshow|realizad|celebrad|attended"),
    ("llamada", r"llamada|cita|agend|book|schedul|reserv|appointment|\bcall\b|reunion|demo"),
    ("cualificado", r"cualificad|qualified|\bmql\b|\bsql\b"),
    ("diagnostico", r"diagnost|calculadora|auditoria|assessment|quiz|\btest\b"),
    ("lead", r"lead|nuevo|\bnew\b|entrante|contacto|contactad|inbound"),
)
MOTIVO_TIMING = (r"timing|momento|mas adelante|mas tarde|ahora no|not now|later|proximo (ano|trimestre|mes|curso)"
                 r"|siguiente (ano|trimestre)|next (year|quarter)"
                 r"|presupuesto (del )?(ano|trimestre) (que viene|siguiente)")
ETIQUETA_BAJA = r"\bbaja\b|no ?contactar|opt ?out|unsubscrib|\bdnd\b|no molestar"
EXITO = {"lead": "llamada", "diagnostico": "llamada", "cualificado": "llamada", "llamada": "asistio",
         "no-show": "asistio", "asistio": "propuesta", "propuesta": "ganado", "perdido": "reabierto",
         "perdido-timing": "reabierto"}
ETIQUETAS_META = ("QUALIFIED_LEADS", "DISQUALIFIED_LEADS", "HIGH_VALUE_CUSTOMERS")  # verificadas el 2026-11-09

COL_ETAPA = ("etapa", "stage", "pipeline stage", "stage name", "fase", "etapa del pipeline")
COL_ESTADO = ("estado", "status", "opportunity status", "estado oportunidad")
COL_MOTIVO = ("motivo", "motivo perdida", "motivo de perdida", "motivo perdido", "lost reason", "lost reason name",
              "razon perdida")
COL_FECHA = ("cambio etapa", "last stage change", "last stage change at", "laststagechangeat", "stage changed",
             "fecha cambio etapa", "updated on", "actualizada")
# Fecha de la pérdida: marcar «perdido» no mueve la etapa, así que manda el cambio de estado si la exportación lo trae
# (`ghl.py oportunidades` lo exporta como cambio_estado, de lastStatusChangeAt).
COL_FECHA_ESTADO = ("cambio estado", "last status change", "last status change at", "laststatuschangeat",
                    "fecha cambio estado", "status changed")
# perdido-timing: de 60 a 180 días desde la pérdida (skill anuncios-por-etapa, tabla de segmentos; playbook de
# consultoras, reactivación de perdidos) [HYPOTHESIS]. Antes es pronto para volver; después la lista está fría.
DIAS_PERDIDA = "60-180"
COL_CONTACTO = ("contact id", "contactid", "id contacto")
COL_PIPELINE = ("pipeline", "embudo", "pipeline name")
COL_ETIQUETAS = ("etiquetas", "tags", "tag")
COL_DND = ("dnd", "no molestar", "do not disturb", "baja", "opt out", "unsubscribed")
COL_ANUNCIO = ("ad id", "anuncio", "utm content", "ad name")
SI = {"1", "true", "si", "yes", "x", "verdadero", "y"}

# Cabecera del CSV hasheado (plantilla de listas de clientes) → clave del esquema multiclave de la API.
ESQUEMA = {"email": "EMAIL", "phone": "PHONE", "fn": "FN", "ln": "LN", "ct": "CT", "st": "ST", "zip": "ZIP",
           "country": "COUNTRY", "gen": "GEN", "doby": "DOBY", "dobm": "DOBM", "dobd": "DOBD", "extern_id": "EXTERN_ID"}
CAMPOS = ("id,name,subtype,description,approximate_count_lower_bound,approximate_count_upper_bound,delivery_status,"
          "operation_status,time_updated,retention_days,customer_file_source")
OPERACION = {200: "normal", 410: "sin archivo", 411: "coincidencia baja", 412: "muchas entradas no válidas",
             414: "reemplazo en curso", 415: "reemplazo fallido", 441: "poblándose", 450: "desactualizada",
             471: "marcada por Meta"}
ENTREGA = {200: "lista", 300: "demasiado pequeña"}


class Invalido(ValueError):
    """Error del usuario: archivo, columnas u opciones."""


def _salir(mensaje: str, codigo: int) -> None:
    print(mensaje, file=sys.stderr)
    sys.exit(codigo)


def _json(datos) -> None:
    print(json.dumps(datos, ensure_ascii=False, indent=2))


def _normal(texto) -> str:
    return capi._cabecera_normal(texto or "")


def _clave_hash(clave: str) -> str:
    return hashlib.sha256(clave.encode("utf-8")).hexdigest()


def en_control(semilla: str, clave: str, fraccion: float) -> bool:
    """Asignación estable: el mismo contacto con la misma semilla cae siempre en el mismo grupo."""
    return int(_clave_hash(f"{semilla}|{clave}")[:15], 16) / 16 ** 15 < fraccion


def _hoy(texto: str | None, ctx: meta_ads.Contexto) -> date:
    if not texto:
        return datetime.now(ctx.zona).date()
    try:
        return date.fromisoformat(texto)
    except ValueError:
        raise Invalido(f"--fecha «{texto}»: escríbela como AAAA-MM-DD") from None


def _privado(slug: str) -> pathlib.Path:
    return (comun.ruta_cliente(slug) / "privado").resolve()


def _dentro(ruta: pathlib.Path, base: pathlib.Path) -> bool:
    try:
        ruta.resolve().relative_to(base)
        return True
    except ValueError:
        return False


def _archivo_privado(texto: str, slug: str, que: str) -> pathlib.Path:
    ruta = capi._ruta(texto)
    if not ruta.is_file():
        raise Invalido(f"no existe {texto}")
    if not _dentro(ruta, _privado(slug)):
        raise Invalido(f"{que} tiene que estar en clientes/{slug}/privado/ (trae datos personales o sus hashes)")
    return ruta


# ---------------------------------------------------------------- leer la exportación del CRM

@dataclass
class Contacto:
    clave: str
    final: str = ""          # etapa actual (perdido si todas sus oportunidades están perdidas)
    alcanzada: str = ""      # etapa más avanzada a la que llegó, aunque luego se perdiera
    timing: bool = False
    baja: bool = False
    datos: dict = field(default_factory=dict)  # tipo → valor en claro (solo en memoria)
    etiquetas: set = field(default_factory=set)
    anuncio: str = ""
    dias: int | None = None  # días desde el último cambio de etapa (oportunidad abierta más avanzada)
    dias_perdida: int | None = None  # días desde la pérdida más reciente (si está perdido)


def _columna(cabeceras: list[str], forzada: str | None, alias: tuple[str, ...]) -> int | None:
    normal = [_normal(h) for h in cabeceras]
    if forzada:
        if _normal(forzada) not in normal:
            raise Invalido(f"no hay ninguna columna «{forzada}» (columnas: {', '.join(cabeceras)})")
        return normal.index(_normal(forzada))
    return next((normal.index(a) for a in alias if a in normal), None)


def _celda(fila: list[str], i: int | None) -> str:
    return fila[i].strip() if i is not None and i < len(fila) else ""


def _fecha(texto: str) -> date | None:
    t = texto.strip()
    try:
        return date.fromisoformat(t[:10])
    except ValueError:
        pass
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", t)
    if m:
        try:
            return date(int(m[3]), int(m[2]), int(m[1]))
        except ValueError:
            return None
    return None


def _estado(texto: str) -> str | None:
    t = _normal(texto)
    if t in ("won", "ganada", "ganado"):
        return "ganado"
    if t in ("lost", "perdida", "perdido", "abandoned", "abandonada", "abandonado"):
        return "perdido"
    return None


def _mapa(texto: str | None) -> dict[str, str]:
    """«Nombre=etapa» (etapa del §16, no-show, perdido o ignorar) o «Nombre=propio:<segmento>» para etapas que no son
    del §16 (p. ej. las de un pipeline de taller: propio:registrado-sin-asistir)."""
    mapa = {}
    for trozo in (x.strip() for x in (texto or "").split(",") if x.strip()):
        nombre, _, etapa = trozo.rpartition("=")
        etapa = etapa.strip().lower()
        if etapa.startswith("propio:"):
            etapa = etapa.removeprefix("propio:").strip()
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", etapa) or etapa in SEGMENTOS or etapa in ("ignorar",
                                                                                                "reabierto"):
                raise Invalido(f"--mapa «{trozo}»: el segmento propio va en minúsculas con guiones y no puede llamarse "
                               "como una etapa del §16")
        elif etapa not in RANGO and etapa not in ("perdido", "ignorar"):
            raise Invalido(f"--mapa «{trozo}»: escribe «Nombre de la etapa=<etapa>» con una etapa de "
                           f"{', '.join(list(RANGO) + ['perdido', 'ignorar'])} o «=propio:<segmento>»")
        if not nombre.strip():
            raise Invalido(f"--mapa «{trozo}»: falta el nombre de la etapa")
        mapa[_normal(nombre)] = etapa
    return mapa


def _rangos(mapa: dict[str, str]) -> tuple[dict[str, float], list[str]]:
    """Rango de cada etapa. Las propias quedan entre cualificado y llamada, en el orden en que se escriben: quien
    luego agenda una llamada pasa a llamada."""
    propios = list(dict.fromkeys(v for v in mapa.values() if v not in RANGO and v not in ("perdido", "ignorar")))
    return {**RANGO, **{s: RANGO["cualificado"] + (i + 1) / 100 for i, s in enumerate(propios)}}, propios


def clasificar(nombre: str, mapa: dict[str, str] | None = None) -> str | None:
    """Nombre visible de la etapa → etapa del §16, `no-show`, `ignorar` o None si no se reconoce."""
    n = _normal(nombre)
    if mapa and n in mapa:
        return mapa[n]
    if re.search(r"taller|webinar|masterclass", n):
        return None  # «Asistió al taller» no es la llamada: se declara con --mapa (=propio:…)
    return next((etapa for etapa, patron in PATRONES if re.search(patron, n)), None)


def _tabla(ruta: pathlib.Path) -> tuple[list[str], list[list[str]]]:
    try:
        return capi._leer_tabla(ruta)
    except capi.Invalido as e:
        raise Invalido(f"{ruta.name}: {e}") from None


def _unir(cab: list[str], filas: list[list[str]], ruta_contactos: pathlib.Path | None) -> tuple[list, list, int]:
    """Añade a cada oportunidad las columnas de su contacto (por contact id). Devuelve también los sin oportunidad."""
    if not ruta_contactos:
        return cab, filas, 0
    cab_c, filas_c = _tabla(ruta_contactos)
    i_o, i_c = _columna(cab, None, COL_CONTACTO), _columna(cab_c, None, COL_CONTACTO)
    if i_o is None or i_c is None:
        raise Invalido("para unir oportunidades y contactos, los dos archivos necesitan la columna contact id")
    ya = {_normal(h) for h in cab}
    extra = [j for j, h in enumerate(cab_c) if _normal(h) not in ya]
    por_id = {_celda(f, i_c): f for f in filas_c if _celda(f, i_c)}
    usados = set()
    unidas = []
    for f in filas:
        c = por_id.get(_celda(f, i_o))
        if c is not None:
            usados.add(_celda(f, i_o))
        unidas.append(list(f) + [_celda(c, j) if c else "" for j in extra])
    return cab + [cab_c[j] for j in extra], unidas, len(set(por_id) - usados)


def leer_contactos(a: argparse.Namespace, slug: str, hoy: date, exige_ids: bool = True,
                   mapa_base: dict[str, str] | None = None) -> tuple[dict[str, Contacto], dict]:
    """Lee la exportación (y los contactos), clasifica y agrupa por contacto. Nada personal sale de aquí salvo en
    `Contacto.datos`, que solo se usa para hashear. `exige_ids=False` (medir) no pide email ni teléfono."""
    ruta = _archivo_privado(a.archivo, slug, "--archivo")
    ruta_c = _archivo_privado(a.contactos, slug, "--contactos") if getattr(a, "contactos", None) else None
    cab, filas = _tabla(ruta)
    cab, filas, sin_oportunidad = _unir(cab, filas, ruta_c)
    i_etapa = _columna(cab, a.columna_etapa, COL_ETAPA)
    if i_etapa is None:
        raise Invalido("no encuentro la columna de la etapa: indícala con --columna-etapa "
                       f"(columnas: {', '.join(cab)})")
    i_estado = _columna(cab, a.columna_estado, COL_ESTADO)
    i_motivo = _columna(cab, a.columna_motivo, COL_MOTIVO)
    i_fecha = _columna(cab, a.columna_fecha, COL_FECHA)
    i_fecha_estado = _columna(cab, None, COL_FECHA_ESTADO)
    i_contacto = _columna(cab, None, COL_CONTACTO)
    i_pipeline = _columna(cab, None, COL_PIPELINE)
    i_etiquetas = _columna(cab, None, COL_ETIQUETAS)
    i_dnd = _columna(cab, None, COL_DND)
    i_anuncio = _columna(cab, None, COL_ANUNCIO)
    try:
        elegidas = capi._columnas_pedidas(cab, a.columnas)
    except capi.Invalido as e:
        if exige_ids:
            raise Invalido(str(e)) from None
        elegidas = []
    avisos = []
    if exige_ids and i_dnd is None:
        avisos.append("la exportación no trae la columna DND («No molestar»): solo se quitan las bajas por etiqueta. "
                      "Exporta los contactos con `ghl.py contactos` (trae `dnd`) y pásalos con --contactos")
    if not a.columnas:
        elegidas = [x for x in elegidas if x[2] != "external_id"]
        if any(t == "fn" for _, _, t in elegidas) and not any(t == "ln" for _, _, t in elegidas):
            elegidas = [x for x in elegidas if x[2] != "fn"]
            if exige_ids:
                avisos.append("«nombre» no se sube: sin columna de apellido suele ser el nombre completo y no casa")
    tipos = list(dict.fromkeys(t for _, _, t in elegidas))
    if exige_ids and not {"em", "ph", "external_id"} & set(tipos):
        raise Invalido("no hay columna de email ni de teléfono: añade --contactos con la exportación de contactos "
                       "o indícalas con --columnas (p. ej. --columnas correo=em,movil=ph)")
    columnas = [{"columna": h, "tipo": t} for _, h, t in elegidas]
    if a.pais and "country" not in tipos:
        tipos.append("country")
        columnas.append({"columna": f"--pais {a.pais}", "tipo": "country"})
    mapa = {**(mapa_base or {}), **_mapa(a.mapa)}
    rango, propios = _rangos(mapa)
    try:
        patron_timing = re.compile(a.motivo_timing or MOTIVO_TIMING)
        patron_baja = re.compile(a.excluir_etiqueta or ETIQUETA_BAJA)
    except re.error as e:
        raise Invalido(f"expresión regular no válida en --motivo-timing o --excluir-etiqueta: {e}") from None
    filtro = _normal(a.pipeline) if getattr(a, "pipeline", None) else ""

    contactos: dict[str, Contacto] = {}
    mapa_usado: Counter = Counter()
    sin_mapear: Counter = Counter()
    sin_clave = filtradas = 0
    for f in filas:
        if not any(c.strip() for c in f):
            continue
        if filtro and filtro not in _normal(_celda(f, i_pipeline)):
            filtradas += 1
            continue
        nombre = _celda(f, i_etapa)
        etapa = clasificar(nombre, mapa)
        estado = _estado(_celda(f, i_estado))
        if etapa == "ignorar":
            mapa_usado[(nombre, "ignorar")] += 1
            continue
        if etapa is None:
            sin_mapear[nombre or "(vacía)"] += 1
            if estado is None:
                continue
        else:
            mapa_usado[(nombre, etapa)] += 1
        final = estado or etapa
        alcanzada = "ganado" if final == "ganado" else (etapa if etapa in rango else "")
        valores: dict[str, str] = {}
        for i, _, t in elegidas:
            valores[t] = valores.get(t) or _celda(f, i)
        if a.pais and not valores.get("country"):
            valores["country"] = a.pais
        if _celda(f, i_contacto):
            clave = "id:" + _celda(f, i_contacto)
        elif valores.get("em"):
            clave = "em:" + valores["em"].strip().lower()
        elif valores.get("ph"):
            clave = "ph:" + re.sub(r"\D", "", valores["ph"])
        else:
            sin_clave += 1
            continue
        c = contactos.setdefault(clave, Contacto(clave))
        for t, v in valores.items():
            if v and not c.datos.get(t):
                c.datos[t] = v
        etiquetas = {_normal(x) for x in re.split(r"[,;|]", _celda(f, i_etiquetas)) if x.strip()}
        c.etiquetas |= etiquetas
        if _normal(_celda(f, i_dnd)) in SI or any(patron_baja.search(x) for x in etiquetas):
            c.baja = True
        if _celda(f, i_anuncio) and not c.anuncio:
            c.anuncio = _celda(f, i_anuncio)
        if rango.get(final, -1) > rango.get(c.final, -1) or not c.final:
            c.final = final
            fecha = _fecha(_celda(f, i_fecha))
            c.dias = (hoy - fecha).days if fecha and final not in ("ganado", "perdido") else None
        if final == "perdido":
            perdida = _fecha(_celda(f, i_fecha_estado)) or _fecha(_celda(f, i_fecha))
            if perdida and (c.dias_perdida is None or (hoy - perdida).days < c.dias_perdida):
                c.dias_perdida = (hoy - perdida).days  # la pérdida más reciente
        if rango.get(alcanzada, -1) > rango.get(c.alcanzada, -1):
            c.alcanzada = alcanzada
        if final == "perdido" and patron_timing.search(_normal(_celda(f, i_motivo))):
            c.timing = True
    ventana = _ventana_perdida(getattr(a, "dias_perdida", None))
    fuera = Counter()
    for c in contactos.values():
        # Sin motivo en la exportación, vale una etiqueta del contacto («mal-momento», «timing»...).
        c.timing = c.final == "perdido" and (c.timing or any(patron_timing.search(x) for x in c.etiquetas))
        if c.timing and ventana and not c.baja:
            if c.dias_perdida is None:
                fuera["sin_fecha"] += 1
            elif c.dias_perdida < ventana[0]:
                fuera["antes_de_tiempo"] += 1
            elif c.dias_perdida > ventana[1]:
                fuera["pasados"] += 1
            else:
                continue
            c.timing = False  # sigue en `perdido` (exclusión); no recibe anuncios de reactivación
    perdido_timing = None
    if ventana:
        perdido_timing = {"dias": list(ventana), "antes_de_tiempo": fuera["antes_de_tiempo"],
                          "pasados": fuera["pasados"], "sin_fecha": fuera["sin_fecha"]}
        if fuera["sin_fecha"]:
            avisos.append(f"{fuera['sin_fecha']} perdidos por timing sin fecha de pérdida no entran en perdido-timing "
                          f"(criterio: {ventana[0]}–{ventana[1]} días desde la pérdida): exporta con `ghl.py "
                          "oportunidades`, que trae la fecha, o indica la columna con --columna-fecha")
        con_timing = sum(fuera.values()) + sum(c.timing for c in contactos.values())
        if con_timing and i_fecha_estado is None and i_fecha is not None:
            avisos.append("la fecha de la pérdida sale del último cambio de etapa: si en el CRM se marca «perdido» sin "
                          "mover la etapa, la pérdida es más reciente. `ghl.py oportunidades` exporta también "
                          "cambio_estado")
    if i_motivo is None and i_etiquetas is None and any(c.final == "perdido" for c in contactos.values()):
        avisos.append("la exportación no trae el motivo de pérdida ni etiquetas: no se puede separar perdido-timing "
                      "(indica la columna con --columna-motivo, exporta ese campo o etiqueta «mal-momento»)")
    if sin_mapear:
        avisos.append("etapas sin reconocer (no entran): " + ", ".join(f"«{k}» ({v})" for k, v in sin_mapear.items())
                      + ". Tradúcelas con --mapa \"Nombre=etapa\" o \"Nombre=ignorar\"")
    info = {"archivo": capi._rel(ruta), "contactos_archivo": capi._rel(ruta_c) if ruta_c else None,
            "columnas": columnas, "tipos": tipos, "propios": propios, "mapa": [{"etapa_crm": k[0], "etapa": k[1], "oportunidades": v}
                                     for k, v in sorted(mapa_usado.items(), key=lambda x: -x[1])],
            "sin_mapear": dict(sin_mapear), "sin_clave": sin_clave, "filtradas_pipeline": filtradas,
            "contactos_sin_oportunidad": sin_oportunidad, "con_motivo": i_motivo is not None,
            "con_fecha": i_fecha is not None, "con_anuncio": i_anuncio is not None,
            "con_etiquetas": i_etiquetas is not None, "columna_dnd": i_dnd is not None,
            "perdido_timing": perdido_timing, "avisos": avisos}
    return contactos, info


def _ventana_perdida(texto: str | None) -> tuple[int, int] | None:
    """«60-180» → (60, 180). None (en `medir`) = sin filtro por antigüedad de la pérdida."""
    if texto is None:
        return None
    m = re.fullmatch(r"\s*(\d+)\s*-\s*(\d+)\s*", str(texto))
    if not m or int(m[1]) > int(m[2]):
        raise Invalido(f"--dias-perdida «{texto}»: escribe MÍNIMO-MÁXIMO en días desde la pérdida (p. ej. 60-180)")
    return int(m[1]), int(m[2])


def segmentos_de(c: Contacto, grupos: dict[str, list[str]]) -> list[str]:
    segs = [c.final] + (["perdido-timing"] if c.timing else [])
    return segs + [g for g, partes in grupos.items() if set(partes) & set(segs)]


def _grupos(lista: list[str] | None, propios: list[str] = ()) -> dict[str, list[str]]:
    validos = list(SEGMENTOS) + list(propios)
    grupos = {}
    for texto in lista or []:
        nombre, _, partes = texto.partition("=")
        nombre = nombre.strip().lower()
        segs = [x.strip().lower() for x in partes.split(",") if x.strip()]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", nombre) or nombre in validos or not segs:
            raise Invalido(f"--agrupar «{texto}»: escribe nombre=segmento1,segmento2 con un nombre nuevo en minúsculas")
        malos = [s for s in segs if s not in validos]
        if malos:
            raise Invalido(f"--agrupar: no conozco {', '.join(malos)} (segmentos: {', '.join(validos)})")
        grupos[nombre] = segs
    return grupos


# ---------------------------------------------------------------- etapas

def _hashes(c: Contacto, tipos: list[str], prefijo: str | None, invalidos: Counter) -> list[str] | None:
    fila: list[str] = []
    validos = set()
    for t in tipos:
        valor = c.datos.get(t, "")
        ancho = len(capi.SALIDA_LISTA[t])
        if not valor:
            fila += [""] * ancho
            continue
        try:
            fila += list(capi.hashear_para_lista(t, valor, prefijo))
            validos.add(t)
        except capi.Invalido:
            invalidos[t] += 1
            fila += [""] * ancho
    if not ({"em", "ph", "external_id"} & validos or {"fn", "ln"} <= validos):
        return None
    return fila


def _manifiesto_anterior(base: pathlib.Path, fecha: str) -> dict | None:
    previos = sorted(p for p in base.glob("*/manifiesto.json") if p.parent.name < fecha)
    if not previos:
        return None
    try:
        return json.loads(previos[-1].read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def cmd_etapas(a: argparse.Namespace) -> None:
    ctx = meta_ads.contexto(a.cliente)
    hoy = _hoy(a.fecha, ctx)
    fecha = hoy.isoformat()
    if not 0 <= a.control < 0.5:
        raise Invalido("--control es la fracción que NO se sube: entre 0 y 0.5 (0.1–0.2 es lo habitual)")
    propios = _rangos(_mapa(a.mapa))[1]
    grupos = _grupos(a.agrupar, propios)
    control_en = {x.strip().lower() for x in (a.control_en or "").split(",") if x.strip()}
    malos = control_en - set(SEGMENTOS) - set(grupos) - set(propios)
    if malos:
        raise Invalido(f"--control-en: no conozco {', '.join(sorted(malos))}")
    semilla = a.semilla or f"{ctx.slug}:etapas"
    contactos, info = leer_contactos(a, ctx.slug, hoy)
    tipos = info["tipos"]
    fuente = str((ctx.ficha.get("crm") or {}).get("tipo") or "crm").upper()

    def controlado(seg: str) -> bool:
        return a.control > 0 and (seg in control_en or any(p in control_en for p in grupos.get(seg, [])))

    invalidos: Counter = Counter()
    bajas = sin_ids = 0
    filas_bajas: list[list[str]] = []
    filas_seg: dict[str, list[list[str]]] = {}
    completas: dict[str, list[list[str]]] = {}
    asignacion: list[list[str]] = []
    recuento: dict[str, Counter] = {}
    for c in contactos.values():
        if c.baja:
            bajas += 1
            hashes = _hashes(c, tipos, a.prefijo, invalidos) if a.bajas else None
            if hashes:
                filas_bajas.append(hashes)
            continue
        hashes = _hashes(c, tipos, a.prefijo, invalidos)
        if hashes is None:
            sin_ids += 1
            continue
        control = en_control(semilla, c.clave, a.control)
        for seg in segmentos_de(c, grupos):
            r = recuento.setdefault(seg, Counter())
            r["total"] += 1
            grupo = "control" if controlado(seg) and control else "tratamiento"
            r[grupo] += 1
            if grupo == "tratamiento":
                filas_seg.setdefault(seg, []).append(hashes)
            if controlado(seg):
                completas.setdefault(seg, []).append(hashes)
            asignacion.append([_clave_hash(c.clave), seg, grupo if controlado(seg) else "sin-control", c.final,
                               c.alcanzada])

    avisos = list(info["avisos"])
    telefonos = "ph" in tipos
    if telefonos and not a.prefijo and invalidos.get("ph"):
        avisos.append(f"{invalidos['ph']} teléfonos sin prefijo de país se han quedado fuera: repite con --prefijo 34")
    for t, n in invalidos.items():
        if not (t == "ph" and not a.prefijo):
            avisos.append(f"{n} valores de {t} no se han podido normalizar")
    if not a.control:
        avisos.append("sin grupo de control (--control 0): podrás ver qué pasa, pero no afirmar que los anuncios suman")
    segmentos = {}
    for seg in [s for s in list(SEGMENTOS) + propios + list(grupos) if s in recuento]:
        r = recuento[seg]
        tratamiento = r["tratamiento"]
        unicas = {tuple(x) for x in filas_seg.get(seg, [])}
        segmentos[seg] = {"total": r["total"], "tratamiento": tratamiento, "control": r["control"],
                          "filas_archivo": len(unicas), "control_activo": controlado(seg),
                          "archivo": f"{seg}.csv" if tratamiento else None,
                          "archivo_exclusion": f"{seg}-completa.csv" if controlado(seg) else None,
                          "audiencia_sugerida": f"ETAPA_{seg.upper()}_{fuente}",
                          "exclusion_sugerida": f"EXCL_{seg.upper()}_{fuente}" if controlado(seg) else None}
        if seg in control_en | set(grupos) | set(propios) and 0 < tratamiento < MINIMO_AVISO:
            avisos.append(f"{seg}: {tratamiento} en tratamiento; con la coincidencia típica en B2B quizá no llegue a "
                          f"entregar [HYPOTHESIS]. Valora --agrupar o esperar a tener más")
    estancadas = {}
    for etapa in ("lead", "diagnostico", "cualificado", "llamada", "no-show", "asistio", "propuesta"):
        dias = [c.dias for c in contactos.values() if c.final == etapa and c.dias is not None and not c.baja]
        if dias:
            estancadas[etapa] = {"con_fecha": len(dias), "mediana_dias": statistics.median(dias),
                                 f"mas_de_{a.dias_estancada}_dias": sum(d > a.dias_estancada for d in dias)}
    base = _privado(ctx.slug) / "audiencias"
    carpeta = base / fecha
    anterior = _manifiesto_anterior(base, fecha)
    if anterior and (anterior.get("semilla") != semilla or anterior.get("control") != a.control):
        avisos.append(f"el refresco anterior ({anterior.get('fecha')}) usó otra semilla o fracción de control: el "
                      "grupo de control ha cambiado y las mediciones no se pueden juntar")
    manifiesto = {"fecha": fecha, "cliente": ctx.slug, "origen": info["archivo"],
                  "contactos": info["contactos_archivo"],
                  "columnas": info["columnas"], "prefijo": a.prefijo, "pais": a.pais, "control": a.control,
                  "control_en": sorted(control_en), "semilla": semilla, "grupos": grupos,
                  "mapa": info["mapa"], "sin_mapear": info["sin_mapear"],
                  "contactos_total": len(contactos), "excluidos": {"baja_o_dnd": bajas, "sin_identificadores": sin_ids,
                                                                  "sin_clave": info["sin_clave"],
                                                                  "filtrados_por_pipeline": info["filtradas_pipeline"],
                                                                  "contactos_sin_oportunidad":
                                                                      info["contactos_sin_oportunidad"]},
                  "no_validos": dict(invalidos), "segmentos": segmentos, "estancadas": estancadas,
                  "columna_dnd": info["columna_dnd"], "perdido_timing": info["perdido_timing"],
                  "bajas": {"personas": len({tuple(x) for x in filas_bajas}),
                            "archivo": "bajas.csv" if filas_bajas else None, "uso": "solo exclusión"},
                  "avisos": avisos}
    por_anuncio = _por_anuncio(contactos, propios) if a.por_anuncio and info["con_anuncio"] else None
    if a.por_anuncio and not info["con_anuncio"]:
        avisos.append("--por-anuncio: no hay columna de anuncio (ad_id o utm_content); añade --contactos")
    escritos = []
    if not a.sin_archivos:
        if (carpeta / "manifiesto.json").exists() and not a.sobrescribir:
            raise Invalido(f"ya hay audiencias preparadas el {fecha} en {capi._rel(carpeta)}: añade --sobrescribir "
                           "para rehacerlas o usa otra --fecha")
        carpeta.mkdir(parents=True, exist_ok=True)
        cabecera = [col for t in tipos for col in capi.SALIDA_LISTA[t]]
        listas = list(filas_seg.items()) + [(f"{s}-completa", f) for s, f in completas.items()]
        for seg, filas in listas + ([("bajas", filas_bajas)] if filas_bajas else []):
            _escribe_csv(carpeta / f"{seg}.csv", cabecera, sorted({tuple(x) for x in filas}))
            escritos.append(capi._rel(carpeta / f"{seg}.csv"))
        _escribe_csv(carpeta / "asignacion.csv", ["clave", "segmento", "grupo", "etapa", "alcanzada"], asignacion)
        (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n",
                                                 encoding="utf-8")
        escritos += [capi._rel(carpeta / "asignacion.csv"), capi._rel(carpeta / "manifiesto.json")]
        if por_anuncio:
            ruta_pa = comun.ruta_cliente(ctx.slug) / "datos" / f"etapas-por-anuncio_{fecha}.csv"
            _escribe_csv(ruta_pa, list(por_anuncio[0]), [list(x.values()) for x in por_anuncio])
            escritos.append(capi._rel(ruta_pa))
    if a.json:
        return _json({**manifiesto, "por_anuncio": por_anuncio, "escritos": escritos})
    _imprime_etapas(manifiesto, escritos, ctx.slug, carpeta, por_anuncio, a.dias_estancada)


def _escribe_csv(ruta: pathlib.Path, cabecera: list[str], filas) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cabecera)
        w.writerows(filas)


def _por_anuncio(contactos: dict[str, Contacto], propios: list[str] = ()) -> list[dict]:
    """Agregados por anuncio: etapa actual y hasta dónde llegaron (sin datos personales)."""
    por: dict[str, Counter] = {}
    for c in contactos.values():
        r = por.setdefault(c.anuncio or "(sin anuncio)", Counter())
        r["contactos"] += 1
        r[f"ahora_{c.final}"] += 1
        rango = RANGO.get(c.alcanzada, -1)
        for nombre, minimo in (("llamada", 3), ("asistio", 5), ("propuesta", 6), ("ganado", 7)):
            r[f"llegaron_a_{nombre}"] += rango >= minimo
    columnas = (["anuncio", "contactos"] + [f"ahora_{e}" for e in list(RANGO) + list(propios) + ["perdido"]]
                + [f"llegaron_a_{x}" for x in ("llamada", "asistio", "propuesta", "ganado")])
    filas = [{"anuncio": k, **{col: r[col] for col in columnas[1:]}} for k, r in por.items()]
    return sorted(filas, key=lambda x: (-x["llegaron_a_propuesta"], -x["contactos"]))


def _imprime_etapas(m: dict, escritos: list[str], slug: str, carpeta: pathlib.Path, por_anuncio, dias: int) -> None:
    print(f"{m['contactos_total']} contactos desde {m['origen']} · fuera: {m['excluidos']['baja_o_dnd']} con baja o "
          f"DND{'' if m.get('columna_dnd') else ' (sin columna DND: solo bajas por etiqueta)'}, "
          f"{m['excluidos']['sin_identificadores']} sin email ni teléfono válidos")
    pt = m.get("perdido_timing")
    if pt and (pt["antes_de_tiempo"] or pt["pasados"]):
        print(f"perdido-timing ({pt['dias'][0]}–{pt['dias'][1]} días desde la pérdida): {pt['antes_de_tiempo']} aún "
              f"pronto, {pt['pasados']} pasados; siguen en perdido para excluir")
    print(f"Columnas que se suben (hasheadas): {', '.join(c['tipo'] for c in m['columnas'])}")
    print("\nEtapas del CRM → etapa:")
    for x in m["mapa"]:
        print(f"  {x['etapa_crm'][:34]:<36}→ {x['etapa']:<12} {x['oportunidades']} oportunidades")
    print(f"\n{'Segmento':<22}{'total':>7}{'tratam.':>9}{'control':>9}  audiencia sugerida")
    for seg, s in m["segmentos"].items():
        print(f"  {seg:<20}{s['total']:>7}{s['tratamiento']:>9}{s['control'] if s['control_activo'] else '-':>9}  "
              f"{s['audiencia_sugerida']}" + (f" (+ {s['exclusion_sugerida']} para excluir)"
                                              if s["exclusion_sugerida"] else ""))
    if m["estancadas"]:
        print(f"\nAntigüedad de las oportunidades abiertas (días en la etapa actual; avisa a partir de {dias}):")
        for etapa, e in m["estancadas"].items():
            print(f"  {etapa:<14}mediana {e['mediana_dias']:>5} días · {e[f'mas_de_{dias}_dias']} de "
                  f"{e['con_fecha']} con más de {dias}")
    if por_anuncio:
        print("\nPor anuncio (llegaron a propuesta / contactos):")
        for x in por_anuncio[:10]:
            print(f"  {x['anuncio'][:40]:<42}{x['llegaron_a_propuesta']:>4} / {x['contactos']}")
    for aviso in m["avisos"]:
        print(f"Aviso: {aviso}")
    if escritos:
        print("\nEscrito (los CSV con hashes no salen de privado/):\n  " + "\n  ".join(escritos))
        seg = next((s for s, x in m["segmentos"].items() if x["archivo"] and x["control_activo"]), None)
        if seg:
            ejemplo = m["segmentos"][seg]
            print("\nSiguiente, vía operador-meta y con el plan aprobado:\n"
                  f"  python3 -I herramientas/audiencias_meta.py crear \"{ejemplo['audiencia_sugerida']}\" "
                  f"--cliente {slug} --confirmo\n"
                  f"  python3 -I herramientas/audiencias_meta.py sincronizar <id> --cliente {slug} "
                  f"--archivo {capi._rel(carpeta / ejemplo['archivo'])} --reemplazar --confirmo")
    else:
        print("\nNo se ha escrito nada (--sin-archivos).")


# ---------------------------------------------------------------- Meta: listar, crear y sincronizar

def _codigo(x) -> int | None:
    return x.get("code") if isinstance(x, dict) else (x if isinstance(x, int) else None)


def condiciones_aceptadas(meta: meta_ads.Meta, ctx: meta_ads.Contexto) -> bool:
    r = meta.uno(ctx.cuenta, fields="tos_accepted")
    return str((r.get("tos_accepted") or {}).get("custom_audience_tos")) == "1"


def _exige_condiciones(meta: meta_ads.Meta, ctx: meta_ads.Contexto) -> None:
    if not condiciones_aceptadas(meta, ctx):
        _salir("La cuenta no ha aceptado las condiciones de las listas de clientes de Meta. Acéptalas (lo hace el "
               f"titular, una vez) en {URL_CONDICIONES.format(cuenta=ctx.cuenta.removeprefix('act_'))} y repite.", 2)


def _audiencias(meta: meta_ads.Meta, ctx: meta_ads.Contexto) -> list[dict]:
    return list(meta.lista(f"{ctx.cuenta}/customaudiences", fields=CAMPOS, limit=200))


def _fila_listar(x: dict, ctx: meta_ads.Contexto) -> dict:
    bajo, alto = x.get("approximate_count_lower_bound"), x.get("approximate_count_upper_bound")
    op, en = _codigo(x.get("operation_status")), _codigo(x.get("delivery_status"))
    actualizada = ""
    if x.get("time_updated"):
        try:
            actualizada = datetime.fromtimestamp(int(x["time_updated"]), ctx.zona).strftime("%Y-%m-%d")
        except (TypeError, ValueError, OSError):
            actualizada = str(x["time_updated"])[:10]
    return {"id": x.get("id"), "nombre": x.get("name"), "subtipo": x.get("subtype"),
            "tamano": f"{bajo}–{alto}" if isinstance(bajo, int) and bajo >= 0 else "sin estimar",
            "entrega": ENTREGA.get(en, "no utilizable" if en and en >= 400 else str(en or "")),
            "operacion": OPERACION.get(op, str(op or "")), "actualizada": actualizada,
            "retencion_dias": x.get("retention_days")}


def cmd_listar(a: argparse.Namespace) -> None:
    ctx = meta_ads.contexto(a.cliente)
    meta = meta_ads.conectar(ctx)
    aceptadas = condiciones_aceptadas(meta, ctx)
    filas = [_fila_listar(x, ctx) for x in _audiencias(meta, ctx)
             if not a.buscar or a.buscar.lower() in str(x.get("name", "")).lower()]
    if a.json:
        return _json({"condiciones_aceptadas": aceptadas, "audiencias": filas})
    if not aceptadas:
        print("Aviso: la cuenta no ha aceptado las condiciones de listas de clientes: "
              + URL_CONDICIONES.format(cuenta=ctx.cuenta.removeprefix("act_")))
    print(f"{len(filas)} audiencias en {ctx.cuenta} (máximo 500 por cuenta):")
    for f in filas:
        print(f"  {f['id']}  {str(f['nombre'])[:38]:<40}{str(f['subtipo']):<10}{f['tamano']:<16}{f['entrega']:<20}"
              f"{f['operacion']:<20}{f['actualizada']}")
    raras = [f for f in filas if f["entrega"] == "demasiado pequeña" or f["operacion"] in
             ("marcada por Meta", "reemplazo fallido", "coincidencia baja")]
    if raras:
        motivo = {f["id"]: f["entrega"] if f["entrega"] == "demasiado pequeña" else f["operacion"] for f in raras}
        print("Ojo: " + "; ".join(f"{f['nombre']}: {motivo[f['id']]}" for f in raras))


def _change_log(objeto: str, cambio: str, dias: int = 7) -> str:
    return meta_ads.fila_change_log("audiencia", objeto, cambio, dias).replace("(meta_ads.py)", "(audiencias_meta.py)")


def cmd_crear(a: argparse.Namespace) -> None:
    ctx = meta_ads.contexto(a.cliente)
    nombre = (a.nombre or "").strip()
    if not nombre or len(nombre) > 200:
        raise Invalido("el nombre de la audiencia no puede estar vacío ni pasar de 200 caracteres")
    if a.retencion is not None and not 1 <= a.retencion <= 180:
        raise Invalido("--retencion va de 1 a 180 días (sin ella, la persona se queda hasta que la quites)")
    aviso = "" if re.fullmatch(r"(ETAPA|EXCL)_[A-Z0-9-]+_[A-Z0-9-]+", nombre) else (
        "el nombre no sigue ETAPA_<SEGMENTO>_<FUENTE> (o EXCL_… para exclusión); se crea igual")
    params = {"name": nombre, "subtype": "CUSTOM", "description": a.descripcion or f"Lista de clientes · {nombre}",
              "customer_file_source": "USER_PROVIDED_ONLY", "retention_days": a.retencion,
              "audience_labels": [a.etiqueta] if a.etiqueta else None}
    if a.simular:
        if a.json:
            return _json({"simulado": True, "cuenta": ctx.cuenta, "params": params, "aviso": aviso})
        print(f"Se crearía en {ctx.cuenta} una audiencia de lista de clientes vacía:\n  "
              + "\n  ".join(f"{k}: {v}" for k, v in params.items() if v is not None))
        if aviso:
            print(f"Aviso: {aviso}")
        print("No se ha tocado Meta (--simular).")
        return
    if not a.confirmo:
        _salir("Crear una audiencia escribe en Meta: añade --confirmo cuando el plan esté aprobado "
               "(o prueba antes con --simular).", 1)
    meta = meta_ads.conectar(ctx)
    _exige_condiciones(meta, ctx)
    existente = next((x for x in _audiencias(meta, ctx) if str(x.get("name", "")).strip().lower() == nombre.lower()),
                     None)
    if existente:
        if a.json:
            return _json({"creada": False, "id": existente.get("id"), "motivo": "ya existe"})
        print(f"Ya existe «{nombre}» ({existente.get('id')}): no se crea otra. Sincronízala con ese ID.")
        return
    r = meta.escribe(f"{ctx.cuenta}/customaudiences", **params)
    nuevo = str(r.get("id", ""))
    comun.registrar_cambio("meta", "cli", "crear_audiencia", nuevo, ctx.slug,
                           f"nombre={nombre}; lista de clientes; retencion={a.retencion or 'sin limite'}"
                           + (f"; etiqueta={a.etiqueta}" if a.etiqueta else ""))
    fila = _change_log(f"{nombre} ({nuevo})", "— → audiencia de lista de clientes creada, vacía")
    if a.json:
        return _json({"creada": True, "id": nuevo, "fila_change_log": fila, "aviso": aviso})
    print(f"Creada «{nombre}» → {nuevo} (vacía; súbele la lista con `sincronizar {nuevo} --archivo …`).")
    if aviso:
        print(f"Aviso: {aviso}")
    print(f"Anota en clientes/{ctx.slug}/change-log.md:\n{fila}")


def leer_hasheado(ruta: pathlib.Path) -> tuple[list[str], list[list[str]], dict]:
    """CSV con cabeceras de la plantilla y celdas SHA-256 → (esquema, filas únicas). Nunca devuelve texto en claro."""
    cab, filas = _tabla(ruta)
    normal = [_normal(h).replace(" ", "_") for h in cab]
    desconocidas = [h for h, n in zip(cab, normal) if n not in ESQUEMA]
    if desconocidas:
        raise Invalido(f"columnas que no son de la plantilla de listas de clientes: {', '.join(desconocidas)} "
                       f"(válidas: {', '.join(ESQUEMA)}). Prepara el archivo con `etapas` o "
                       "`capi.py hashear --archivo`")
    en_claro = Counter()
    for f in filas:
        for h, v in zip(cab, f):
            if v.strip() and not capi.es_hash(v.strip()):
                en_claro[h] += 1
    if en_claro:
        raise Invalido("hay celdas sin hashear, no se envía nada: "
                       + ", ".join(f"{h} ({n})" for h, n in en_claro.items())
                       + ". Hashéalo antes con `etapas` o `capi.py hashear --archivo`")
    usadas = [i for i in range(len(cab)) if any(i < len(f) and f[i].strip() for f in filas)]
    vistas, unicas, vacias = set(), [], 0
    for f in filas:
        fila = tuple(f[i].strip().lower() if i < len(f) else "" for i in usadas)
        if not any(fila):
            vacias += 1
            continue
        if fila not in vistas:
            vistas.add(fila)
            unicas.append(list(fila))
    if not unicas:
        raise Invalido("el archivo no tiene ninguna fila con datos")
    return [ESQUEMA[normal[i]] for i in usadas], unicas, {"filas": len(filas), "vacias": vacias,
                                                         "repetidas": len(filas) - vacias - len(unicas)}


def cmd_sincronizar(a: argparse.Namespace) -> None:
    ctx = meta_ads.contexto(a.cliente)
    if not re.fullmatch(r"\d{5,}", a.id or ""):
        raise Invalido("el ID de la audiencia es numérico (sácalo de `listar` o de `crear`)")
    ruta = _archivo_privado(a.archivo, ctx.slug, "--archivo")
    if ruta.name == "bajas.csv" and not a.exclusion:
        raise Invalido("bajas.csv es de personas que no quieren comunicaciones: solo sirve para una audiencia de "
                       "exclusión (añade --exclusion; mejor, una audiencia «solo de exclusión» en Ads Manager)")
    if ruta.name.endswith("-completa.csv") and not a.exclusion:
        raise Invalido(f"{ruta.name} incluye al grupo de control: solo sirve para EXCLUIR. Si esta audiencia es de "
                       "exclusión, añade --exclusion; si es para anuncios, sube el CSV del segmento sin «-completa»")
    esquema, filas, rec = leer_hasheado(ruta)
    lotes = math.ceil(len(filas) / LOTE)
    modo = "reemplazar" if a.reemplazar else "añadir"
    resumen = {"audiencia": a.id, "archivo": capi._rel(ruta), "esquema": esquema, "personas": len(filas),
               "lotes": lotes, "modo": modo, **rec}
    if a.simular:
        if a.json:
            return _json({"simulado": True, **resumen})
        print(f"Se enviarían {len(filas)} personas ({', '.join(esquema)}) a {a.id} en {lotes} lote(s), modo {modo}. "
              f"{rec['repetidas']} repetidas y {rec['vacias']} vacías fuera.\nNo se ha tocado Meta (--simular).")
        return
    if not a.confirmo:
        _salir("Sincronizar sube datos de clientes a Meta: añade --confirmo cuando el plan esté aprobado "
               "(o prueba antes con --simular).", 1)
    meta = meta_ads.conectar(ctx)
    info = meta.uno(a.id, fields="account_id,name,subtype,operation_status,approximate_count_lower_bound")
    if str(info.get("account_id", "")).removeprefix("act_") != ctx.cuenta.removeprefix("act_"):
        raise Invalido(f"la audiencia {a.id} no es de la cuenta de la ficha ({ctx.cuenta})")
    if info.get("subtype") != "CUSTOM":
        raise Invalido(f"la audiencia {a.id} es de tipo {info.get('subtype')}: solo se sincronizan listas de clientes")
    op = _codigo(info.get("operation_status"))
    if op == 414:
        raise Invalido("Meta aún está procesando un reemplazo de esta audiencia: espera a que termine (`listar`)")
    if op == 471:
        raise Invalido("Meta ha marcado esta audiencia (operation_status 471): revisa el aviso en Ads Manager antes")
    _exige_condiciones(meta, ctx)
    poblada = isinstance(info.get("approximate_count_lower_bound"), int) and info["approximate_count_lower_bound"] > 0
    if poblada and not a.reemplazar:
        print("Aviso: añadir con `users` a una audiencia en uso reinicia el aprendizaje de sus conjuntos; para "
              "refrescar, usa --reemplazar.", file=sys.stderr)
    ruta_api = f"{a.id}/{'usersreplace' if a.reemplazar else 'users'}"
    sesion = secrets.randbits(63) or 1
    recibidas = no_validas = 0
    for n in range(lotes):
        lote = filas[n * LOTE:(n + 1) * LOTE]
        try:
            r = meta.escribe(ruta_api, payload={"schema": esquema, "data": lote},
                             session={"session_id": sesion, "batch_seq": n + 1, "last_batch_flag": n == lotes - 1,
                                      "estimated_num_total": len(filas)})
        except meta_ads.ErrorMeta as e:
            if n:
                comun.registrar_cambio("meta", "cli", f"{'reemplazar' if a.reemplazar else 'anadir'}_audiencia_parcial",
                                       a.id, ctx.slug, f"lotes enviados={n} de {lotes}; recibidas={recibidas}")
            caducada = "1870158" in str(e)
            _salir(f"Meta cortó en el lote {n + 1} de {lotes}: {e}\n"
                   + ("La sesión caducó (dura 90 minutos). " if caducada else "")
                   + (f"Se enviaron {n} lote(s). " + (
                       "Repite la orden entera con --reemplazar: deja la lista como el archivo." if a.reemplazar else
                       "Repite la misma orden, sin --reemplazar: Meta deduplica a quien ya se subió. Con "
                       "--reemplazar la audiencia se quedaría solo con este archivo y perdería a los de antes.")
                      if n else "No se ha cambiado nada."), e.salida)
        recibidas += int(r.get("num_received") or 0)
        no_validas += int(r.get("num_invalid_entries") or 0)
    accion = "reemplazar_audiencia" if a.reemplazar else "anadir_audiencia"
    comun.registrar_cambio("meta", "cli", accion, a.id, ctx.slug,
                           f"archivo={ruta.name}; personas={len(filas)}; lotes={lotes}; recibidas={recibidas}; "
                           f"no_validas={no_validas}; esquema={'+'.join(esquema)}")
    fila = _change_log(f"{info.get('name', a.id)} ({a.id})",
                       f"lista {'reemplazada' if a.reemplazar else 'ampliada'} con {ruta.name} ({len(filas)} personas)")
    if a.json:
        return _json({**resumen, "recibidas": recibidas, "no_validas": no_validas, "fila_change_log": fila})
    print(f"{modo.capitalize()}: Meta recibió {recibidas} de {len(filas)} ({no_validas} no válidas) en {lotes} "
          "lote(s). "
          "La coincidencia tarda en calcularse: mira el tamaño con `listar` en 24–48 h.")
    if no_validas > 0.05 * max(recibidas, 1):
        print("Aviso: muchas entradas no válidas: revisa la normalización (prefijo del teléfono, emails).")
    print(f"Anota en clientes/{ctx.slug}/change-log.md:\n{fila}")


# ---------------------------------------------------------------- medir contra el grupo de control

def _lcomb(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def fisher(a: int, b: int, c: int, d: int) -> float:
    """Test exacto de Fisher bilateral para [[a, b], [c, d]] (éxitos y fracasos de tratamiento y control)."""
    n1, n2, m = a + b, c + d, a + c
    n = n1 + n2
    if n == 0:
        return 1.0

    def p(x: int) -> float:
        return math.exp(_lcomb(n1, x) + _lcomb(n2, m - x) - _lcomb(n, m))

    observado = p(a)
    return min(1.0, sum(p(x) for x in range(max(0, m - n2), min(m, n1) + 1) if p(x) <= observado * (1 + 1e-7)))


def control_necesario(pt: float, pc: float, razon: float) -> int | None:
    """Tamaño del control (y razon·control de tratamiento) para ver esa diferencia con alfa 0,05 y potencia 0,8."""
    if pt == pc or razon <= 0:
        return None
    za, zb = 1.959963984540054, 0.8416212335729143
    pm = (razon * pt + pc) / (razon + 1)
    n = (za * math.sqrt(pm * (1 - pm) * (1 + 1 / razon)) + zb * math.sqrt(pt * (1 - pt) / razon + pc * (1 - pc))) ** 2
    return math.ceil(n / (pt - pc) ** 2)


def exito(c: Contacto, objetivo: str) -> bool:
    if objetivo == "reabierto":
        return c.final != "perdido"
    if objetivo == "ganado":
        return c.final == "ganado"
    return RANGO.get(c.alcanzada, -1) >= RANGO[objetivo]


def veredicto(et: int, nt: int, ec: int, nc: int) -> dict:
    pt, pc = (et / nt if nt else 0.0), (ec / nc if nc else 0.0)
    p = fisher(et, nt - et, ec, nc - ec)
    r = {"tratamiento": {"n": nt, "exitos": et, "tasa": round(pt, 4)}, "control": {"n": nc, "exitos": ec,
                                                                                 "tasa": round(pc, 4)},
         "diferencia_pp": round(100 * (pt - pc), 1), "p_fisher": round(p, 4),
         "control_necesario": control_necesario(pt, pc, nt / nc if nc else 0)}
    if nc < 30 or et + ec < 10:  # [HYPOTHESIS] por debajo, cualquier diferencia es ruido
        r["veredicto"] = "faltan datos"
    elif p < 0.05:
        r["veredicto"] = "suma" if pt > pc else "resta"
    else:
        r["veredicto"] = "no distinguible"
    return r


def cmd_medir(a: argparse.Namespace) -> None:
    ctx = meta_ads.contexto(a.cliente)
    hoy = _hoy(a.fecha, ctx)
    if a.objetivo and a.objetivo not in list(RANGO) + ["reabierto"]:
        raise Invalido(f"--exito: una etapa de {', '.join(RANGO)} o reabierto")
    manifiestos = []
    for texto in a.manifiesto or []:
        ruta = _archivo_privado(texto, ctx.slug, "--manifiesto")
        try:
            manifiestos.append((ruta, json.loads(ruta.read_text(encoding="utf-8"))))
        except ValueError:
            raise Invalido(f"{ruta.name} no es un manifiesto válido") from None
    # Se clasifica igual que en la subida: el mapa de etapas del manifiesto, y --mapa encima.
    mapa_base = {_normal(x["etapa_crm"]): x["etapa"] for _, m in manifiestos for x in m.get("mapa", [])}
    contactos, info = leer_contactos(a, ctx.slug, hoy, exige_ids=False, mapa_base=mapa_base)
    por_hash = {_clave_hash(c.clave): c for c in contactos.values()}
    avisos = [x for x in info["avisos"] if not x.startswith("la exportación no trae el motivo")]
    resultados = []
    if a.etiqueta_grupo:
        if not a.etiqueta_control or not a.objetivo:
            raise Invalido("en modo etiquetas indica --etiqueta-control y --exito (la etapa que cuenta como éxito)")
        if not info["con_etiquetas"]:
            raise Invalido("modo etiquetas: la exportación no trae etiquetas (las oportunidades de `ghl.py` no las "
                           "llevan). Añade --contactos con la exportación de contactos (`ghl.py contactos`)")
        g, k = _normal(a.etiqueta_grupo), _normal(a.etiqueta_control)
        dentro = [c for c in contactos.values() if g in c.etiquetas]
        if not dentro:
            raise Invalido(f"ningún contacto lleva la etiqueta «{a.etiqueta_grupo}»: revisa el nombre exacto en el CRM "
                           "o que la exportación de contactos sea la del periodo de la prueba")
        ctrl = [c for c in dentro if k in c.etiquetas]
        trat = [c for c in dentro if k not in c.etiquetas]
        v = veredicto(sum(exito(c, a.objetivo) for c in trat), len(trat), sum(exito(c, a.objetivo) for c in ctrl),
                      len(ctrl))
        resultados.append({"segmento": f"etiqueta {a.etiqueta_grupo}", "exito": a.objetivo, "desde": None, **v})
    else:
        if not manifiestos:
            raise Invalido("di qué medir: --manifiesto <privado/audiencias/<fecha>/manifiesto.json> (repetible) "
                           "o el modo etiquetas (--etiqueta-grupo y --etiqueta-control)")
        asignados: dict[tuple[str, str], str] = {}
        desde, semillas = None, set()
        for ruta, m in sorted(manifiestos, key=lambda x: x[1].get("fecha", "")):
            semillas.add((m.get("semilla"), m.get("control")))
            desde = min(desde or m["fecha"], m["fecha"])
            _, filas = _tabla(ruta.parent / "asignacion.csv")
            for clave, seg, grupo, *_ in filas:
                if grupo in ("tratamiento", "control"):
                    asignados.setdefault((clave, seg), grupo)  # se queda la primera asignación
        if len(semillas) > 1:
            avisos.append("los manifiestos usan semillas o controles distintos: los grupos no son comparables")
        dias = (hoy - date.fromisoformat(desde)).days
        if dias < 14:
            avisos.append(f"solo han pasado {dias} días desde la primera subida: en un ciclo de semanas es pronto "
                          "[HYPOTHESIS]; repite al cumplirse el ciclo de venta")
        segs = sorted({s for _, s in asignados} if not a.segmento else {a.segmento})
        for seg in segs:
            objetivo = a.objetivo or EXITO.get(seg)
            if not objetivo:
                avisos.append(f"{seg}: no hay un éxito por defecto (p. ej. referidos o ampliaciones de clientes): "
                              "pásalo con --exito o mídelo fuera del CRM")
                continue
            grupos = {"tratamiento": [0, 0], "control": [0, 0]}
            perdidos = 0
            for (clave, s), grupo in asignados.items():
                if s != seg:
                    continue
                c = por_hash.get(clave)
                if c is None:
                    perdidos += 1
                    continue
                grupos[grupo][0] += exito(c, objetivo)
                grupos[grupo][1] += 1
            v = veredicto(*grupos["tratamiento"], *grupos["control"])
            resultados.append({"segmento": seg, "exito": objetivo, "desde": desde, "no_encontrados": perdidos, **v})
            if perdidos:
                avisos.append(f"{seg}: {perdidos} contactos de la subida no aparecen en la exportación nueva "
                              "(¿borrados o de otro pipeline?): quedan fuera de los dos grupos")
    if a.json:
        return _json({"resultados": resultados, "avisos": avisos})
    for r in resultados:
        t, c = r["tratamiento"], r["control"]
        print(f"{r['segmento']} → éxito = {r['exito']}" + (f" (desde {r['desde']})" if r.get("desde") else ""))
        print(f"  tratamiento {t['exitos']}/{t['n']} = {100 * t['tasa']:.1f} % · control {c['exitos']}/{c['n']} = "
              f"{100 * c['tasa']:.1f} % · diferencia {r['diferencia_pp']:+.1f} pp · p = {r['p_fisher']:.3f} (Fisher)")
        extra = (f" · para ver esta diferencia harían falta ≈{r['control_necesario']} en control"
                 if r["veredicto"] in ("no distinguible", "faltan datos") and r["control_necesario"] else "")
        print(f"  Veredicto: {r['veredicto'].upper()}{extra}")
    print("Se compara por intención de tratar: el tratamiento incluye a quien Meta no encontró o no vio el anuncio, "
          "así que el efecto real en quien sí lo vio es mayor que esta diferencia.")
    for aviso in avisos:
        print(f"Aviso: {aviso}")


# ---------------------------------------------------------------- CLI

def _opciones_lectura(p: argparse.ArgumentParser) -> None:
    p.add_argument("--archivo", required=True, help="exportación de oportunidades de GHL en clientes/<slug>/privado/")
    p.add_argument("--contactos", help="exportación de contactos para unir por contact id (emails, teléfonos, anuncio)")
    p.add_argument("--mapa", help="\"Nombre de etapa=etapa,...\" para las que no se reconocen (o =ignorar)")
    p.add_argument("--columna-etapa", dest="columna_etapa")
    p.add_argument("--columna-estado", dest="columna_estado")
    p.add_argument("--columna-motivo", dest="columna_motivo")
    p.add_argument("--columna-fecha", dest="columna_fecha", help="fecha del último cambio de etapa")
    p.add_argument("--pipeline", help="solo las oportunidades de pipelines que contienen este texto")
    p.add_argument("--columnas", help="columnas de datos y su tipo, como en capi.py (p. ej. correo=em,movil=ph)")
    p.add_argument("--prefijo", help="prefijo de país para teléfonos sin él (34 en España)")
    p.add_argument("--pais", help="código ISO del país si la exportación no lo trae (es)")
    p.add_argument("--motivo-timing", dest="motivo_timing",
                   help="regex (sin tildes, en minúsculas) del motivo de pérdida que cuenta como timing")
    p.add_argument("--excluir-etiqueta", dest="excluir_etiqueta",
                   help="regex (sin tildes, en minúsculas) de etiquetas de baja")
    p.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy en la zona de la ficha)")


def main(argv: list[str] | None = None) -> None:
    comunes = argparse.ArgumentParser(add_help=False)
    comunes.add_argument("--cliente", help="slug del cliente (clientes/<slug>/ficha.md)")
    comunes.add_argument("--json", action="store_true", help="salida en JSON")
    p = argparse.ArgumentParser(description="Audiencias de lista de clientes por etapa del CRM, con grupo de control.")
    sub = p.add_subparsers(dest="comando", required=True)
    li = sub.add_parser("listar", parents=[comunes], help="audiencias de la cuenta, tamaño y estado")
    li.add_argument("--buscar", help="solo las que contienen este texto en el nombre")
    et = sub.add_parser("etapas", parents=[comunes], help="CSV hasheados por etapa desde una exportación en privado/")
    _opciones_lectura(et)
    et.add_argument("--control", type=float, default=0.2, help="fracción que no se sube (por defecto 0.2)")
    et.add_argument("--control-en", dest="control_en", default=CONTROL_EN,
                    help=f"segmentos con grupo de control (por defecto {CONTROL_EN})")
    et.add_argument("--semilla", help="texto fijo de la asignación (por defecto <slug>:etapas); no lo cambies")
    et.add_argument("--agrupar", action="append", help="nombre=seg1,seg2 para unir segmentos pequeños (repetible)")
    et.add_argument("--dias-estancada", dest="dias_estancada", type=int, default=DIAS_ESTANCADA)
    et.add_argument("--dias-perdida", dest="dias_perdida", default=DIAS_PERDIDA,
                    help=f"perdido-timing solo con la pérdida entre estos días (por defecto {DIAS_PERDIDA})")
    et.add_argument("--por-anuncio", dest="por_anuncio", action="store_true", help="agregados por anuncio en datos/")
    et.add_argument("--sin-archivos", dest="sin_archivos", action="store_true", help="solo recuentos por pantalla")
    et.add_argument("--sobrescribir", action="store_true", help="rehace las de esta fecha")
    et.add_argument("--bajas", action="store_true",
                    help="escribe también bajas.csv (DND y opt-out) para una audiencia solo de exclusión")
    cr = sub.add_parser("crear", parents=[comunes], help="crea una audiencia de lista de clientes vacía (--confirmo)")
    cr.add_argument("nombre")
    cr.add_argument("--descripcion")
    cr.add_argument("--retencion", type=int, help="días que se queda cada persona (1–180; por defecto, sin límite)")
    cr.add_argument("--etiqueta", choices=ETIQUETAS_META, help="etiqueta de audiencia para value rules")
    cr.add_argument("--simular", action="store_true", help="enseña lo que haría, sin red")
    cr.add_argument("--confirmo", action="store_true", help="el usuario ha aprobado el plan")
    si = sub.add_parser("sincronizar", parents=[comunes], help="sube un CSV hasheado a una audiencia (--confirmo)")
    si.add_argument("id")
    si.add_argument("--archivo", required=True, help="CSV hasheado de clientes/<slug>/privado/")
    si.add_argument("--reemplazar", action="store_true", help="sustituye la lista entera (refresco recomendado)")
    si.add_argument("--exclusion", action="store_true", help="permite subir <segmento>-completa.csv o bajas.csv")
    si.add_argument("--simular", action="store_true", help="comprueba el archivo y cuenta lotes, sin red")
    si.add_argument("--confirmo", action="store_true", help="el usuario ha aprobado el plan")
    me = sub.add_parser("medir", parents=[comunes], help="tratamiento contra control con una exportación nueva")
    _opciones_lectura(me)
    me.add_argument("--manifiesto", action="append", help="manifiesto.json de una subida (repetible)")
    me.add_argument("--segmento", help="solo este segmento")
    me.add_argument("--exito", dest="objetivo", help="etapa que cuenta como éxito (por defecto, la siguiente)")
    me.add_argument("--etiqueta-grupo", dest="etiqueta_grupo", help="modo GHL: etiqueta de quien entró en el flujo")
    me.add_argument("--etiqueta-control", dest="etiqueta_control", help="modo GHL: etiqueta del grupo de control")
    a = p.parse_args(argv)
    ordenes = {"listar": cmd_listar, "etapas": cmd_etapas, "crear": cmd_crear, "sincronizar": cmd_sincronizar,
               "medir": cmd_medir}
    try:
        ordenes[a.comando](a)
    except Invalido as e:
        _salir(f"No se puede: {e}", 1)
    except comun.FichaInvalida as e:
        _salir(str(e), 2)
    except meta_ads.ErrorMeta as e:
        _salir(str(e), e.salida)


if __name__ == "__main__":
    main()
