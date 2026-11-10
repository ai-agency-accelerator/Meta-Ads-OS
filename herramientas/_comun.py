"""Utilidades comunes de las herramientas de Meta Ads OS (solo biblioteca estándar).

- Carga variables del `.env` de la raíz del proyecto sin imprimirlas nunca.
- Credenciales por cliente: `<VAR>_<SLUG>` con la variable global como alternativa.
- Lee la cabecera YAML de `clientes/<slug>/ficha.md` (contrato §3 de docs/desarrollo/contratos.md).
- Registra escrituras ejecutadas en `logs/cambios.jsonl` (contrato §8).
- Peticiones HTTP con reintentos.
- `numero()`: la única regla para leer cifras escritas por personas o exportadas por hojas y CRM.
- `fecha_iso()`: fechas ISO de Graph y GHL («+0100», «Z») en cualquier Python ≥ 3.8.
- `consola_segura()`: imprimir ✓ o → no revienta en una consola cp1252 (Windows con la salida redirigida). Se
  llama al importar este módulo, así que vale para todas las herramientas que lo importan.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

RAIZ = pathlib.Path(os.environ.get("META_ADS_OS_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
CLIENTES = RAIZ / "clientes"
LOGS = RAIZ / "logs"


def consola_segura() -> None:
    """Con la salida redirigida en Windows (Git Bash: cp1252) y `python3 -I` (que ignora PYTHONUTF8 y
    PYTHONIOENCODING), un ✓, un → o un ≥ revientan con UnicodeEncodeError. Así salen como «?» y la orden termina."""
    for nombre in ("stdout", "stderr"):
        flujo = getattr(sys, nombre, None)
        if hasattr(flujo, "reconfigure"):
            try:
                flujo.reconfigure(errors="replace")
            except (ValueError, OSError):  # flujo cerrado o que no admite el cambio
                pass


consola_segura()


# ---------------------------------------------------------------- números y fechas
_MILES_ESPACIO = re.compile(r"(?<=\d)[    ](?=\d{3}(?!\d))")
_TOKEN_NUMERO = re.compile(r"[-+]?(?:\d[\d.,]*|[.,]\d+)(?:[eE][-+]?\d+)?")


def numero(texto) -> float | None:
    """Primer número de un texto escrito por una persona o exportado de una hoja o un CRM. None si no hay.

    Una sola regla para todas las herramientas (antes había cuatro parsers distintos):
    - Espacio, NBSP o espacio fino entre cifras y un grupo de 3 = miles: «1 200 €» = 1200, «12 500» = 12500.
    - Con punto y coma, el último es el decimal: «1.234,56» = 1234,56 y «1,234.56» = 1234,56.
    - Con un solo tipo de separador, grupos de exactamente 3 cifras tras un primer grupo de 1–3 que no empieza por 0
      son miles: «4.800» = 4800, «1,200» = 1200 (México, EE. UU.), «1.234.567». Si no, es el decimal: «0.175»,
      «0,175», «120,5», «80.5» (un 0 delante nunca es separador de miles).
    - Notación científica: «9e3» = 9000. Signo: «-1.200» = -1200. Un número (int/float) se devuelve tal cual.
    Ambigüedad conocida: «1,200» se lee 1200, nunca 1,2 (una cifra de 1,2 se escribe «1,2»).
    """
    if texto is None or isinstance(texto, bool):
        return None
    if isinstance(texto, (int, float)):
        return float(texto) if math.isfinite(texto) else None
    m = _TOKEN_NUMERO.search(_MILES_ESPACIO.sub("", str(texto)))
    if not m:
        return None
    tok = m.group(0)
    exp = ""
    me = re.search(r"[eE][-+]?\d+$", tok)
    if me:
        tok, exp = tok[:me.start()], me.group(0)
    signo = "-" if tok.startswith("-") else ""
    tok = tok.lstrip("+-").rstrip(".,")
    if not tok or not re.search(r"\d", tok):
        return None
    try:
        if "," in tok and "." in tok:
            dec = "," if tok.rfind(",") > tok.rfind(".") else "."
            entero, _, fraccion = tok.rpartition(dec)
            miles = "." if dec == "," else ","
            if not re.fullmatch(rf"\d{{1,3}}(?:\{miles}\d{{3}})*|\d+", entero) or not fraccion.isdigit():
                return None
            return float(f"{signo}{entero.replace(miles, '')}.{fraccion}{exp}")
        for sep in (",", "."):
            if sep in tok:
                if re.fullmatch(rf"[1-9]\d{{0,2}}(?:\{sep}\d{{3}})+", tok):
                    return float(signo + tok.replace(sep, "") + exp)
                if tok.count(sep) > 1:
                    return None
                return float(signo + tok.replace(sep, ".") + exp)
        return float(signo + tok + exp)
    except ValueError:
        return None


def numero_arg(texto: str) -> float:
    """Tipo de argparse con la regla de `numero`: «--cierre 0,25», «--precio 5.000» o «--cpa 1 200»."""
    import argparse  # noqa: PLC0415 — solo lo necesitan las herramientas con CLI

    v = numero(texto)
    if v is None or not re.search(r"\d", str(texto)) or re.search(r"[^\d\s.,+\-eE€$%   ]", str(texto)):
        raise argparse.ArgumentTypeError(f"«{texto}» no es un número")
    return float(v)


def fecha_iso(texto) -> datetime | None:
    """Fecha y hora ISO 8601 en cualquier Python ≥ 3.8. None si no se entiende.

    Graph da «2026-12-01T23:59:59+0100» y GHL «2026-11-01T10:00:00.000Z»; `datetime.fromisoformat` no acepta ni
    «+0100» ni «Z» antes de 3.11, ni fracciones de segundo que no tengan 3 o 6 cifras.
    """
    if not texto:
        return None
    t = str(texto).strip()
    t = re.sub(r"[zZ]$", "+00:00", t)
    t = re.sub(r"(?<=\d)([+-]\d{2})(\d{2})$", r"\1:\2", t)
    t = re.sub(r"\.(\d+)(?=[+-]\d{2}:\d{2}$|$)", lambda m: "." + (m.group(1) + "000000")[:6], t)
    try:
        return datetime.fromisoformat(t)
    except ValueError:
        return None


# Etapas del CRM que significan «perdido» o «no cualificado» (sobre el nombre en minúsculas y sin tildes). Una sola
# fuente: `ghl.py por-anuncio` no las cuenta como cualificadas y `audiencias_meta.py` las clasifica como perdidas.
PATRON_ETAPA_PERDIDA = (r"perdid|\blost\b|descartad|no cualif|unqualif|disqualif|not qualified|no encaj|abandon"
                        r"|rechazad")


class FichaInvalida(Exception):
    """La ficha del cliente no existe o su cabecera no cumple el contrato."""


def ruta_cliente(slug: str) -> pathlib.Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug or ""):
        raise FichaInvalida(f"Slug no válido: {slug!r} (usa minúsculas, números y guiones)")
    return CLIENTES / slug


def _valor_yaml(texto: str):
    t = texto.strip()
    if t[:1] in ("'", '"'):  # entre comillas, con o sin comentario detrás: «"a # b" # nota» → a # b
        cierre = t.find(t[0], 1)
        if cierre != -1 and (t[cierre + 1:].strip() == "" or t[cierre + 1:].strip().startswith("#")):
            return t[1:cierre]
    elif " #" in t:
        t = t.split(" #", 1)[0].strip()
    if t == "" or t in ("~", "null"):
        return ""
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        return t[1:-1]
    if t.lower() in ("true", "false"):
        return t.lower() == "true"
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+\.\d+", t):
        return float(t)
    return t


def parsear_cabecera(texto: str) -> dict:
    """Parsea la cabecera YAML (subconjunto: claves, escalares y un nivel de anidación con 2 espacios)."""
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        raise FichaInvalida("La ficha no empieza por una cabecera '---'")
    datos: dict = {}
    padre: str | None = None
    for n, linea in enumerate(lineas[1:], start=2):
        if linea.strip() == "---":
            return datos
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"( *)([A-Za-z_][\w-]*):(.*)", linea)
        if not m:
            raise FichaInvalida(f"Línea {n} de la cabecera no válida: {linea.strip()!r}")
        sangria, clave, resto = len(m.group(1)), m.group(2), m.group(3)
        if sangria == 0:
            if resto.split("#", 1)[0].strip() == "":
                datos[clave] = {}
                padre = clave
            else:
                datos[clave] = _valor_yaml(resto)
                padre = None
        else:
            if padre is None:
                raise FichaInvalida(f"Línea {n}: '{clave}' está sangrada sin una clave padre")
            datos[padre][clave] = _valor_yaml(resto)
    raise FichaInvalida("La cabecera de la ficha no se cierra con '---'")


def leer_ficha(slug: str) -> dict:
    """Devuelve la cabecera de `clientes/<slug>/ficha.md` como dict. Lanza FichaInvalida si falta o está mal."""
    f = ruta_cliente(slug) / "ficha.md"
    if not f.exists():
        raise FichaInvalida(f"No existe {f.relative_to(RAIZ)}. Crea el cliente con /cliente-nuevo")
    datos = parsear_cabecera(f.read_text(encoding="utf-8"))
    for campo in ("slug", "tipo", "moneda", "meta", "topes"):
        if campo not in datos:
            raise FichaInvalida(f"Falta el campo '{campo}' en la cabecera de la ficha de {slug}")
    return datos


def cargar_entorno() -> None:
    """Carga RAIZ/.env en os.environ (sin sobrescribir variables ya definidas). Nunca imprime valores."""
    f = RAIZ / ".env"
    if not f.exists():
        return
    for linea in f.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


cargar_env = cargar_entorno  # nombre antiguo


def credencial(nombre: str, slug: str | None = None) -> str | None:
    """`<NOMBRE>_<SLUG>` (slug en mayúsculas con guion bajo) y, si no existe, `<NOMBRE>`."""
    cargar_entorno()
    if slug:
        v = os.environ.get(f"{nombre}_{slug.upper().replace('-', '_')}")
        if v:
            return v
    return os.environ.get(nombre) or None


def secreto(nombre: str) -> str | None:
    return credencial(nombre)


_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_TELEFONO = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def anonimizar(texto: str) -> str:
    return _TELEFONO.sub("***", _EMAIL.sub("***", texto))


def registrar_cambio(sistema: str, via: str, accion: str, entidad_id: str = "", cliente: str = "",
                     detalle: str = "", session: str = "") -> None:
    """Añade una escritura ejecutada a logs/cambios.jsonl (sin tokens ni datos personales)."""
    LOGS.mkdir(parents=True, exist_ok=True)
    fila = {"ts": datetime.now().isoformat(timespec="seconds"), "session": session or os.environ.get("CLAUDE_SESSION_ID", ""),
            "sistema": sistema, "via": via, "accion": accion, "entidad_id": str(entidad_id),
            "cliente": cliente, "detalle": anonimizar(str(detalle))[:2000]}
    with (LOGS / "cambios.jsonl").open("a", encoding="utf-8") as h:
        h.write(json.dumps(fila, ensure_ascii=False) + "\n")


UA_NAVEGADOR = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"
)
GRAPH = f"https://graph.facebook.com/{os.environ.get('META_API_VERSION', 'v27.0')}"


def get_json(url: str, params: dict | None = None, headers: dict | None = None,
             intentos: int = 4, timeout: int = 60) -> dict:
    if params:
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    h = {"User-Agent": "meta-ads-os/1.0"}
    h.update(headers or {})
    ultimo = None
    for i in range(intentos):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode("utf-8", "ignore")
            if e.code in (400, 401, 403, 404):
                # Errores de la API: no tiene sentido reintentar. Nunca devolvemos la URL (puede llevar token).
                try:
                    msg = json.loads(cuerpo).get("error", {}).get("message", cuerpo[:300])
                except Exception:
                    msg = cuerpo[:300]
                raise RuntimeError(f"HTTP {e.code}: {msg}") from None
            ultimo = f"HTTP {e.code}"
        except Exception as e:  # red, timeout
            ultimo = type(e).__name__
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"Fallo de red tras {intentos} intentos ({ultimo})")


def get_texto(url: str, timeout: int = 40) -> tuple[str, str, int]:
    """Devuelve (html, url_final, status)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA_NAVEGADOR,
                                               "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore"), r.geturl(), r.status
