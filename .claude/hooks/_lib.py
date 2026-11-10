"""Librería compartida de los hooks de Meta Ads OS (no es un hook: no cuenta en los 10 del contrato).

- Solo biblioteca estándar. Sintaxis compatible con Python 3.8+ (el `python3` de las herramientas de línea de
  comandos de macOS es 3.9): nada de `match`, ni `X | Y` fuera de anotaciones.
- Ningún hook depende de `herramientas/`: aquí está el código mínimo para leer fichas, registros, nomenclatura y
  comandos de shell sobre el mismo formato de `docs/desarrollo/contratos.md` (§3, §5, §7 y §8).
- Si la lógica de un hook falla, el error queda en `logs/hooks.jsonl` y el hook NO decide (actúan los permisos de
  `.claude/settings.json`, que son la red de seguridad), salvo que el hook dé su propia respuesta de fallo
  (`ejecutar(..., al_fallar=…)`): `meta_guard` falla cerrado en las escrituras en Meta.
- Nunca se imprimen ni se guardan secretos. En los registros, emails y teléfonos se sustituyen por `***`.
- La salida por stdout va en ASCII (`ensure_ascii`) para no romper con la codificación de consola de Windows.
"""
from __future__ import annotations

import fnmatch
import glob
import json
import math
import os
import pathlib
import re
import shlex
import sys
import traceback
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta

VERSION_MINIMA = (3, 8)

# ─────────────────────────────────────────────────────────────── rutas, tiempo y entrada/salida


def raiz() -> pathlib.Path:
    """Raíz de la instancia: CLAUDE_PROJECT_DIR (lo pone Claude Code), META_ADS_OS_RAIZ o la carpeta del producto."""
    for var in ("CLAUDE_PROJECT_DIR", "META_ADS_OS_RAIZ"):
        valor = os.environ.get(var)
        if valor:
            return pathlib.Path(valor)
    return pathlib.Path(__file__).resolve().parent.parent.parent


def ahora() -> datetime:
    """Fecha y hora locales para decidir (paciencia, resumen de la sesión).

    `META_ADS_OS_HOY=AAAA-MM-DD` fija solo la fecha, para que las evals (`scripts/evals.py`) sean reproducibles; la hora
    sigue siendo la real. Un valor mal escrito se ignora. Las marcas de tiempo de los registros (`ts()`) son siempre las
    reales: se comparan con las de las herramientas y con las fechas de los archivos.
    """
    real = datetime.now()
    fijada = os.environ.get("META_ADS_OS_HOY", "").strip()
    if fijada:
        try:
            d = date.fromisoformat(fijada)
        except ValueError:
            return real
        return real.replace(year=d.year, month=d.month, day=d.day)
    return real


def ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


def leer_entrada() -> dict:
    flujo = getattr(sys.stdin, "buffer", None)
    crudo = flujo.read() if flujo is not None else (sys.stdin.read() or "").encode("utf-8")
    if not crudo or not crudo.strip():
        return {}
    datos = json.loads(crudo.decode("utf-8", "replace"))
    return datos if isinstance(datos, dict) else {}


def emitir(salida: dict) -> None:
    sys.stdout.write(json.dumps(salida, ensure_ascii=True))
    sys.stdout.flush()


def pre(decision: str, motivo: str, contexto: str = "") -> dict:
    """Respuesta de PreToolUse: decision ∈ allow | ask | deny."""
    cuerpo = {"hookEventName": "PreToolUse", "permissionDecision": decision, "permissionDecisionReason": motivo}
    if contexto:
        cuerpo["additionalContext"] = contexto
    return {"hookSpecificOutput": cuerpo}


def combinar(decisiones: list) -> dict | None:
    """Une varias (decision, motivo) del mismo hook: deny > ask > allow; los motivos se concatenan."""
    orden = {"deny": 3, "ask": 2, "allow": 1}
    validas = [(d, m) for d, m in decisiones if d in orden]
    if not validas:
        return None
    peor = max(validas, key=lambda x: orden[x[0]])[0]
    motivos = []
    for d, m in validas:
        if d == peor and m and m not in motivos:
            motivos.append(m)
    return pre(peor, " ".join(motivos))


def agente(entrada: dict) -> str:
    return entrada.get("agent_type") or "principal"


def es_subagente(entrada: dict) -> bool:
    return bool(entrada.get("agent_id"))


# ─────────────────────────────────────────────────────────────── limpieza de secretos y datos personales

_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
_DOMINIOS_EJEMPLO = re.compile(
    r"(?i)(^|\.)(example\.(com|org|net)|ejemplo\.(com|es|org)|[\w-]*\.(test|invalid|example|local|localhost)"
    r"|localhost|acme[\w-]*\.[a-z.]+|nimbo[\w-]*\.[a-z.]+|clinicasonrisa[\w-]*\.[a-z.]+|clinica-sonrisa[\w-]*\.[a-z.]+"
    r"|dominio\.[a-z.]+|tudominio\.[a-z.]+|midominio\.[a-z.]+|empresa\.[a-z.]+|correo\.[a-z.]+|email\.com"
    r"|users\.noreply\.github\.com|anthropic\.com)$")
_EXTENSIONES = re.compile(r"(?i)\.(png|jpe?g|gif|svg|webp|avif|mp4|mov|webm|pdf|css|js|ts|py|md)$")
_TEL_CANDIDATO = re.compile(r"(?<![\w+/.:-])(\+?\(?\d[\d \t().-]{6,20}\d)(?![\w/:-]|\.\d)")
_TOKENS = [re.compile(p) for p in (
    r"\bEAA[A-Za-z0-9]{20,}",                      # Meta
    r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{10,}",  # Stripe
    r"\bwhsec_[A-Za-z0-9]{10,}",                   # Stripe webhooks
    r"\bpit-[0-9a-fA-F-]{20,}",                    # GHL, integración privada
    r"\bAIza[0-9A-Za-z_-]{30,}",                   # Google / Gemini
    r"\bsk-ant-[A-Za-z0-9_-]{10,}",                # Anthropic
    r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}",          # OpenAI
    r"\bxox[abprs]-[A-Za-z0-9-]{10,}",             # Slack
    r"\b\d{8,10}:[A-Za-z0-9_-]{30,}",              # Telegram (bot)
    r"https://hooks\.slack\.com/services/[A-Za-z0-9/_-]+",
    r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{10,}",
)]
_PARAM_SECRETO = re.compile(r"(?i)\b(access_token|api_key|apikey|token|secret|password|clave)=([^\s&\"']+)")
_CLAVE_SECRETA = re.compile(r"(?i)(token|secret|password|passwd|^clave$|api_?key|authorization|credential|cookie)")


def es_email_real(dominio: str) -> bool:
    return not (_DOMINIOS_EJEMPLO.search(dominio) or _EXTENSIONES.search(dominio))


def _es_telefono(candidato: str) -> bool:
    digitos = re.sub(r"\D", "", candidato)
    if re.fullmatch(r"\d{4}[-/.]\d{1,2}[-/.]\d{1,2}", candidato.strip()):
        return False
    if candidato.startswith("+"):
        return 8 <= len(digitos) <= 15
    return len(digitos) == 9 and digitos[0] in "6789"


def buscar_pii(texto: str) -> dict:
    """Cuenta emails y teléfonos (sin devolverlos). Ignora dominios de ejemplo y nombres de archivo tipo logo@2x.png."""
    emails = sum(1 for m in _EMAIL.finditer(texto) if es_email_real(m.group(1)))
    telefonos = sum(1 for m in _TEL_CANDIDATO.finditer(texto) if _es_telefono(m.group(1)))
    return {"emails": emails, "telefonos": telefonos}


def contiene_token(texto: str) -> bool:
    return any(p.search(texto) for p in _TOKENS)


def limpiar_texto(texto: str) -> str:
    for patron in _TOKENS:
        texto = patron.sub("***", texto)
    texto = _PARAM_SECRETO.sub(lambda m: m.group(1) + "=***", texto)
    texto = _EMAIL.sub(lambda m: "***" if es_email_real(m.group(1)) else m.group(0), texto)
    texto = _TEL_CANDIDATO.sub(lambda m: "***" if _es_telefono(m.group(1)) else m.group(0), texto)
    return texto


def limpiar(obj, profundidad: int = 0):
    """Copia sin secretos ni datos personales, apta para registrar."""
    if profundidad > 12:
        return "…"
    if isinstance(obj, dict):
        limpio = {}
        for k, v in obj.items():
            if _CLAVE_SECRETA.search(str(k)) and not isinstance(v, (dict, list)):
                limpio[k] = "***" if v not in (None, "", False) else v
            else:
                limpio[k] = limpiar(v, profundidad + 1)
        return limpio
    if isinstance(obj, list):
        return [limpiar(v, profundidad + 1) for v in obj[:200]]
    if isinstance(obj, str):
        return limpiar_texto(obj[:20000])
    return obj


# ─────────────────────────────────────────────────────────────── registros (logs/*.jsonl)


def registrar(nombre: str, fila: dict) -> None:
    """Añade una línea JSON a logs/<nombre>. Si no se puede escribir, sigue (el registro nunca bloquea)."""
    try:
        carpeta = raiz() / "logs"
        carpeta.mkdir(parents=True, exist_ok=True)
        with (carpeta / nombre).open("a", encoding="utf-8") as h:
            h.write(json.dumps(limpiar(fila), ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass


def registrar_cambio(entrada: dict, sistema: str, accion: str, entidad_id: str = "", cliente: str = "",
                     detalle: str = "") -> None:
    """Escritura ejecutada → logs/cambios.jsonl (contrato §8)."""
    registrar("cambios.jsonl", {"ts": ts(), "session": entrada.get("session_id", ""), "sistema": sistema,
                                "via": "mcp", "accion": accion, "entidad_id": str(entidad_id or ""),
                                "cliente": cliente or "", "detalle": limpiar_texto(str(detalle))[:2000]})


def leer_jsonl(nombre: str, max_bytes: int = 2_000_000) -> list:
    f = raiz() / "logs" / nombre
    try:
        with f.open("rb") as h:
            h.seek(0, os.SEEK_END)
            tam = h.tell()
            h.seek(max(0, tam - max_bytes))
            crudo = h.read().decode("utf-8", "replace")
    except OSError:
        return []
    filas = []
    for linea in crudo.splitlines():
        try:
            fila = json.loads(linea)
        except ValueError:
            continue
        if isinstance(fila, dict):
            filas.append(fila)
    return filas


def leer_ts(valor) -> datetime | None:
    """ISO 8601 → datetime local sin zona (los ts de logs/ ya son locales)."""
    if not valor or not isinstance(valor, str):
        return None
    texto = valor.strip().replace("Z", "+00:00")
    texto = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", texto)  # +0100 → +01:00 (Graph API; Python < 3.11)
    texto = re.sub(r"\.(\d{1,6})\d*", lambda m: "." + m.group(1).ljust(6, "0"), texto)
    try:
        d = datetime.fromisoformat(texto)
    except ValueError:
        return None
    if d.tzinfo is not None:
        d = d.astimezone().replace(tzinfo=None)
    return d


def ejecutar(hook: str, logica, al_fallar=None) -> int:
    """Envoltorio común: lee stdin, llama a logica(entrada) y emite su respuesta. Registra los fallos.

    Si la lógica falla, por defecto no decide (mandan los permisos de settings.json). Con `al_fallar(entrada)`, el hook
    da su respuesta de fallo (p. ej. `ask`/`deny` en una escritura que no ha podido comprobar): falla cerrado.
    """
    if sys.version_info < VERSION_MINIMA:
        return 3  # el lanzador de settings.json prueba el siguiente intérprete (stdin sigue intacto)
    entrada: dict = {}
    emitido = False
    try:
        entrada = leer_entrada()
        salida = logica(entrada)
        if salida:
            emitir(salida)
            emitido = True
            _registrar_decision(hook, entrada, salida)
    except Exception as e:  # la lógica ha fallado
        registrar("hooks.jsonl", {"ts": ts(), "hook": hook, "evento": entrada.get("hook_event_name", ""),
                                  "tool": entrada.get("tool_name", ""), "session": entrada.get("session_id", ""),
                                  "decision": "error", "error": f"{type(e).__name__}: {e}"[:500],
                                  "traza": traceback.format_exc(limit=4)[-1500:]})
        if al_fallar is not None and not emitido:
            try:
                salida = al_fallar(entrada if isinstance(entrada, dict) else {})
            except Exception:
                salida = None
            if salida:
                emitir(salida)
                _registrar_decision(hook, entrada, salida)
    return 0


def _registrar_decision(hook: str, entrada: dict, salida: dict) -> None:
    cuerpo = salida.get("hookSpecificOutput") or {}
    decision = cuerpo.get("permissionDecision") or salida.get("decision")
    if not decision:
        return
    motivo = cuerpo.get("permissionDecisionReason") or salida.get("reason") or ""
    registrar("hooks.jsonl", {"ts": ts(), "hook": hook, "evento": entrada.get("hook_event_name", ""),
                              "tool": entrada.get("tool_name", ""), "session": entrada.get("session_id", ""),
                              "agente": agente(entrada), "decision": decision, "motivo": motivo[:600]})


# ─────────────────────────────────────────────────────────────── fichas de cliente (contrato §3)


def _valor_yaml(texto: str):
    t = texto.strip()
    if t[:1] in ("'", '"'):  # entre comillas, con o sin comentario detrás: «"a # b" # nota» → a # b
        cierre = t.find(t[0], 1)
        if cierre != -1 and (t[cierre + 1:].strip() == "" or t[cierre + 1:].strip().startswith("#")):
            return t[1:cierre]
    elif " #" in t:
        t = t.split(" #", 1)[0].strip()
    if t in ("", "~", "null"):
        return ""
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
        return t[1:-1]
    if t.lower() in ("true", "false"):
        return t.lower() == "true"
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d+[.,]\d+", t):
        return float(t.replace(",", "."))
    return t


def parsear_cabecera(texto: str) -> dict | None:
    """Subconjunto YAML del contrato §3 (claves, escalares y un nivel de anidación). None si no es válida."""
    lineas = texto.splitlines()
    if not lineas or lineas[0].strip() != "---":
        return None
    datos: dict = {}
    padre = None
    for linea in lineas[1:]:
        if linea.strip() == "---":
            return datos
        if not linea.strip() or linea.lstrip().startswith("#"):
            continue
        m = re.fullmatch(r"( *)([A-Za-z_][\w-]*):(.*)", linea.rstrip())
        if not m:
            return None
        sangria, clave, resto = len(m.group(1)), m.group(2), m.group(3)
        if sangria == 0:
            if resto.split("#", 1)[0].strip() == "":
                datos[clave] = {}
                padre = clave
            else:
                datos[clave] = _valor_yaml(resto)
                padre = None
        elif padre is not None:
            datos[padre][clave] = _valor_yaml(resto)
        else:
            return None
    return None


_FICHAS: dict | None = None


def fichas() -> dict:
    """{slug: cabecera} de todas las fichas legibles en clientes/*/ficha.md (las inválidas se ignoran)."""
    global _FICHAS
    if _FICHAS is None:
        _FICHAS = {}
        carpeta = raiz() / "clientes"
        if carpeta.is_dir():
            for f in sorted(carpeta.glob("*/ficha.md")):
                try:
                    cab = parsear_cabecera(f.read_text(encoding="utf-8", errors="replace"))
                except OSError:
                    cab = None
                if isinstance(cab, dict):
                    _FICHAS[f.parent.name] = cab
    return _FICHAS


def olvidar_fichas() -> None:
    global _FICHAS
    _FICHAS = None


def numero(valor) -> float | None:
    """Importe o cifra con el mismo `float()` que las herramientas (`"9e3"` → 9000), y además `12,5` y `50 €`.

    None si no es un número finito (`nan`, `inf`, textos, objetos): quien llama decide qué hacer con lo ilegible.
    """
    if isinstance(valor, bool) or valor is None:
        return None
    try:
        if isinstance(valor, (int, float)):
            n = float(valor)
        else:
            texto = str(valor).strip().replace("€", "").replace("$", "").strip()
            if re.fullmatch(r"-?\d+,\d+", texto):
                texto = texto.replace(",", ".")
            n = float(texto)
    except (ValueError, OverflowError):
        return None
    return n if math.isfinite(n) else None


def tope(slug: str, clave: str) -> float | None:
    """topes.<clave> de la ficha (> 0) o None si falta o es 0."""
    f = fichas().get(slug) or {}
    topes = f.get("topes") if isinstance(f.get("topes"), dict) else {}
    n = numero(topes.get(clave))
    return n if n and n > 0 else None


def moneda(slug: str | None) -> str:
    f = fichas().get(slug or "") or {}
    return str(f.get("moneda") or "EUR").upper()


def digitos_cuenta(valor) -> str | None:
    m = re.fullmatch(r"(?:act_)?(\d{5,})", str(valor or "").strip())
    return m.group(1) if m else None


def cuenta_de(slug: str) -> str | None:
    f = fichas().get(slug) or {}
    meta = f.get("meta") if isinstance(f.get("meta"), dict) else {}
    return digitos_cuenta(meta.get("cuenta"))


def cliente_por_cuenta(cuenta: str) -> str | None:
    encontrados = [s for s in fichas() if cuenta_de(s) == cuenta]
    return encontrados[0] if len(encontrados) == 1 else None


_CLAVES_CUENTA = {"ad_account_id", "account_id", "adaccount_id", "ad_account", "account", "act_id", "cuenta"}


def recorrer(obj, profundidad: int = 0):
    """Recorre dicts y listas (también JSON incrustado en cadenas) devolviendo (clave, valor, dict_padre)."""
    if profundidad > 10:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k), v, obj
            if isinstance(v, str) and v.strip().startswith(("{", "[")):
                try:
                    v = json.loads(v)
                except ValueError:
                    continue
            if isinstance(v, (dict, list)):
                yield from recorrer(v, profundidad + 1)
    elif isinstance(obj, list):
        for v in obj[:500]:
            yield from recorrer(v, profundidad + 1)


def cuentas_en(obj) -> set:
    cuentas = set()
    for k, v, _ in recorrer(obj):
        if isinstance(v, (str, int)):
            if k.lower() in _CLAVES_CUENTA and digitos_cuenta(v):
                cuentas.add(digitos_cuenta(v))
            elif isinstance(v, str):
                cuentas.update(re.findall(r"\bact_(\d{5,})", v))
    return cuentas


def cliente_por_entidad(entidad: str) -> str | None:
    """Busca el ID en logs/cambios.jsonl y, si no, en change-logs y planes de cada cliente."""
    if not entidad:
        return None
    for fila in reversed(leer_jsonl("cambios.jsonl")):
        if str(fila.get("entidad_id")) == entidad and fila.get("cliente"):
            return str(fila["cliente"])
    candidatos = set()
    carpeta = raiz() / "clientes"
    if carpeta.is_dir():
        for slug in fichas():
            rutas = [carpeta / slug / "change-log.md"] + sorted((carpeta / slug / "planes").glob("*.json"))[:200]
            for r in rutas:
                try:
                    if r.is_file() and r.stat().st_size < 3_000_000 and entidad in r.read_text(encoding="utf-8",
                                                                                               errors="replace"):
                        candidatos.add(slug)
                        break
                except OSError:
                    continue
    return candidatos.pop() if len(candidatos) == 1 else None


def deducir_cliente(cuentas=(), entidades=(), explicito: str | None = None):
    """(slug, cómo) con cómo ∈ explicito | cuenta | entidad | unico; (None, motivo) si no se puede."""
    todas = fichas()
    if explicito:
        return (explicito, "explicito") if explicito in todas else (None, f"no existe la ficha de «{explicito}»")
    for c in cuentas:
        slug = cliente_por_cuenta(c)
        if slug:
            return slug, "cuenta"
    if cuentas:
        return None, "la cuenta act_" + sorted(cuentas)[0] + " no está en ninguna ficha"
    for e in entidades:
        slug = cliente_por_entidad(str(e))
        if slug:
            return slug, "entidad"
    activos = [s for s, f in todas.items() if str(f.get("estado") or "activo") != "prospecto"]
    if len(todas) == 1:
        return next(iter(todas)), "unico"
    if len(activos) == 1:
        return activos[0], "unico"
    if not todas:
        return None, "no hay ninguna ficha de cliente"
    return None, "no puedo deducir el cliente (la llamada no trae la cuenta act_ y hay varias fichas)"


# ─────────────────────────────────────────────────────────────── credenciales y HTTP (solo para el tope total)


def _valores_dotenv() -> dict:
    f = raiz() / ".env"
    try:
        lineas = f.read_text(encoding="utf-8", errors="replace").splitlines() if f.is_file() else []
    except OSError:
        lineas = []
    valores = {}
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith("export "):
            linea = linea[7:].strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        valores[k.strip()] = v.strip().strip('"').strip("'")
    return valores


def credencial(nombre: str, slug: str | None = None, entorno: bool = True) -> str | None:
    """<NOMBRE>_<SLUG> o <NOMBRE> del entorno o del .env de la raíz. Nunca se imprime ni se registra.

    `entorno=False`: solo el `.env` (lo que una herramienta vuelve a cargar aunque la orden quite la variable).
    """
    claves = []
    if slug:
        claves.append(f"{nombre}_{slug.upper().replace('-', '_')}")
    claves.append(nombre)
    if entorno:
        for k in claves:
            if os.environ.get(k):
                return os.environ[k]
    valores = _valores_dotenv()
    for k in claves:
        if valores.get(k):
            return valores[k]
    return None


def http_get_json(url: str, token: str, timeout: float = 6.0) -> dict:
    """GET con el token en la cabecera (nunca en la URL). Los errores no incluyen ni URL ni token."""
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token,
                                               "User-Agent": "meta-ads-os-hooks/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except Exception as e:
        codigo = getattr(e, "code", None)
        raise RuntimeError(f"HTTP {codigo}" if codigo else type(e).__name__) from None


# ─────────────────────────────────────────────────────────────── comandos de shell


_CONTROL = re.compile(r"^(?:[;&|()]+|[<>]\(+)$")  # operadores y sustitución de procesos <( … ) / >( … )
_ENVOLTORIOS = {"time", "nohup", "nice", "command", "builtin", "exec", "sudo", "stdbuf", "xargs", "caffeinate"}
_SHELLS = {"bash", "sh", "zsh", "dash", "bash.exe", "sh.exe"}


def base(token: str) -> str:
    return token.replace("\\", "/").rstrip("/").split("/")[-1]


def tokens(cmd: str) -> list:
    try:
        lex = shlex.shlex(cmd.replace("\r", " ").replace("\n", " ; "), posix=True, punctuation_chars=";&|()<>")
        lex.whitespace_split = True
        lex.commenters = ""
        return list(lex)
    except ValueError:  # comillas sin cerrar: troceo simple
        return re.findall(r"[;&|()]+|[^\s;&|()]+", cmd)


def segmentos(cmd: str, profundidad: int = 0) -> list:
    """Divide un comando en subcomandos (&&, ||, ;, |, &, saltos de línea, $( ) y `bash -c '…'`).

    Cada segmento es un dict {"env": {VAR: valor}, "args": [tokens], "unset": {VAR…}, "vacio": bool} sin asignaciones
    iniciales ni envoltorios. `unset` son las variables que quita `env -u VAR`; `vacio`, que `env -i` vacía el entorno.
    """
    resultado = []
    actual: list = []
    for tok in tokens(cmd) + [";"]:
        if _CONTROL.match(tok):
            if actual:
                resultado.extend(_normalizar(actual, profundidad))
            actual = []
        else:
            actual.append(tok)
    return resultado


_ENV_CON_VALOR = {"-u", "--unset", "-C", "--chdir", "-P", "-a", "--argv0"}


def _opciones_env(toks: list, i: int, env: dict, quitadas: set) -> tuple:
    """Consume las opciones y asignaciones de `env` desde toks[i]. Devuelve (i, toks, vacio).

    `-u VAR`/`--unset VAR` consumen su argumento y quitan VAR; `-i`/`-` vacían el entorno; `-S "orden"` se trocea de
    nuevo (es una orden entera dentro de un argumento).
    """
    vacio = False
    while i < len(toks):
        t = toks[i]
        if t in ("-i", "-", "--ignore-environment"):
            vacio = True
            env.clear()
            i += 1
        elif t in _ENV_CON_VALOR or re.fullmatch(r"-u\S+|--unset=\S+", t):
            if t in _ENV_CON_VALOR:
                variable = toks[i + 1] if i + 1 < len(toks) else ""
                i += 2
            else:
                variable = t[2:] if t.startswith("-u") else t.split("=", 1)[1]
                i += 1
                t = "-u"
            if t in ("-u", "--unset") and variable:
                env.pop(variable, None)
                quitadas.add(variable)
        elif t in ("-S", "--split-string") or t.startswith(("-S", "--split-string=")):
            texto = toks[i + 1] if t in ("-S", "--split-string") and i + 1 < len(toks) else (
                t[2:] if t.startswith("-S") else t.split("=", 1)[1])
            fin = i + 2 if t in ("-S", "--split-string") else i + 1
            toks = toks[:i] + tokens(texto) + toks[fin:]
        elif t.startswith("-"):
            i += 1
        elif re.fullmatch(r"[A-Za-z_]\w*=.*", t):
            k, v = t.split("=", 1)
            env[k] = v
            quitadas.discard(k)
            i += 1
        else:
            break
    return i, toks, vacio


def _normalizar(toks: list, profundidad: int) -> list:
    env = {}
    quitadas: set = set()
    vacio = False
    i = 0
    envoltorio = None  # posición del último envoltorio: si no le sigue ninguna orden, el programa es él (`env` a secas)
    while i < len(toks):
        t = toks[i]
        if base(t) in _ENVOLTORIOS or base(t) in ("env", "timeout"):
            envoltorio = i
        if re.fullmatch(r"[A-Za-z_]\w*=.*", t):
            k, v = t.split("=", 1)
            env[k] = v
            quitadas.discard(k)
            i += 1
        elif base(t) in _ENVOLTORIOS:
            i += 1
            while i < len(toks) and toks[i].startswith("-"):
                i += 1
        elif base(t) == "env":
            i, toks, vaciado = _opciones_env(toks, i + 1, env, quitadas)
            vacio = vacio or vaciado
        elif base(t) == "timeout":
            i += 1
            while i < len(toks) and (toks[i].startswith("-") or re.fullmatch(r"[\d.]+[smhd]?", toks[i])):
                i += 1
        else:
            break
    args = toks[i:] or (toks[envoltorio:] if envoltorio is not None else [])
    segs = [{"env": env, "args": args, "unset": quitadas, "vacio": vacio}]
    if profundidad < 3 and args:
        if base(args[0]) in _SHELLS and "-c" in args[1:]:
            j = args.index("-c", 1)
            if j + 1 < len(args):
                segs.extend(segmentos(args[j + 1], profundidad + 1))
        elif args[0] == "eval" and len(args) > 1:
            segs.extend(segmentos(" ".join(args[1:]), profundidad + 1))
    return segs


def args_de_script(seg: dict, nombre: str):
    """Si el segmento ejecuta <nombre> (p. ej. meta_ads.py), devuelve los argumentos que le siguen.

    Acepta también rutas de Windows sin comillas (`herramientas\\meta_ads.py` llega como `herramientasmeta_ads.py`).
    """
    for i, t in enumerate(seg["args"]):
        if base(t) == nombre or (t.endswith(nombre) and not t.startswith("-") and "=" not in t):
            return seg["args"][i + 1:]
    return None


def antes_de_guion(args: list) -> list:
    """Los argumentos anteriores a `--` (lo que va detrás son posicionales para argparse, aunque empiecen por `-`)."""
    return args[:args.index("--")] if "--" in args else list(args)


def parsear_args(args: list, con_valor=()) -> tuple:
    """(subcomando, opciones, posicionales). Las opciones de `con_valor` consumen el siguiente token.

    Como argparse, todo lo que va después de `--` es posicional: `crear -- --simular` NO es una simulación.
    """
    sub = None
    opciones: dict = {}
    posicionales = []
    solo_posicionales = False
    i = 0
    while i < len(args):
        a = args[i]
        if a in (">", ">>", "<", "2>", "2>>", "&>", ">&"):
            i += 2
            continue
        if a == "--" and not solo_posicionales:
            solo_posicionales = True
        elif solo_posicionales:
            if sub is None:
                sub = a
            else:
                posicionales.append(a)
        elif a.startswith("--") and len(a) > 2:
            if "=" in a:
                k, v = a[2:].split("=", 1)
                opciones[k] = v
            elif a[2:] in con_valor and i + 1 < len(args):
                opciones[a[2:]] = args[i + 1]
                i += 1
            else:
                opciones[a[2:]] = True
        elif sub is None and not a.startswith("-"):
            sub = a
        else:
            posicionales.append(a)
        i += 1
    return sub, opciones, posicionales


def resolver_ruta(ruta: str, entrada: dict, cwd_extra: str | None = None) -> pathlib.Path:
    p = pathlib.Path(ruta.replace("\\", "/"))
    if p.is_absolute():
        return p
    bases = [cwd_extra, entrada.get("cwd"), str(raiz())]
    for b in bases:
        if b:
            candidato = pathlib.Path(b) / p
            if candidato.exists():
                return candidato
    return raiz() / p


# ─────────────────────────────────────────────────────────────── intérpretes que el troceo no puede leer
#
# El troceo reconoce los scripts por su nombre literal (`meta_ads.py`, `capi.py`, `motor`…). Con comodines
# (`meta_ad?.py`), variables (`$S.py`), `-c`, `-m`, `runpy`, `exec` o `..`, Python ejecuta algo que el hook no ve.
# Primero se resuelven los comodines con `glob` respecto al cwd (un único archivo → se trata como ese script); lo que
# sigue siendo opaco y afecta a herramientas/, modulos/ o .claude/hooks/ lo deciden los hooks con `decision_opaca`:
# `ask` en la sesión principal y `deny` en subagentes. Solo mira la ejecución de intérpretes: `ls clientes/*/` o
# `grep -n x herramientas/*.py` no son ejecuciones.

CARPETAS_SENSIBLES = ("herramientas", "modulos", ".claude/hooks")
_INTERPRETE = re.compile(r"(?i)^(python[\d.]*w?|py|pypy[\d.]*)(\.exe)?$")
_COMODIN = re.compile(r"[*?\[{]")
_PUNTOS = re.compile(r"(^|[/\\])\.\.([/\\]|$)")
_CODIGO_DINAMICO = re.compile(r"\b(runpy|exec|execfile|eval|compile|subprocess|os\.system|os\.exec\w*|os\.spawn\w*|"
                              r"popen\w*|importlib|__import__)\b")
_EXEC_FIND = ("-exec", "-execdir", "-ok", "-okdir")
_GESTORES_RUN = {"poetry", "pipenv", "pdm", "hatch", "rye"}
_UV_CON_VALOR = {"--project", "--directory", "--with", "-w", "--with-editable", "--with-requirements", "--extra",
                 "--group", "--only-group", "--no-group", "--package", "--python", "-p", "--env-file", "--index",
                 "--default-index", "--index-url", "-i", "--extra-index-url", "--find-links", "-f", "--config-file",
                 "--cache-dir", "--color", "--refresh-package", "--upgrade-package", "-P", "--reinstall-package",
                 "--exclude-newer", "--resolution", "--prerelease", "--index-strategy", "--keyring-provider",
                 "--link-mode", "-C", "--config-setting", "--python-preference", "--from", "--allow-insecure-host"}
# Herramientas que escriben en Meta o envían eventos (para `-m <módulo>` con PYTHONPATH=herramientas).
_MODULOS_HERRAMIENTAS = {"meta_ads", "reglas_meta", "formularios_meta", "audiencias_meta", "capi", "_comun"}


def tiene_comodin(token: str) -> bool:
    return bool(_COMODIN.search(token or ""))


def lanza_python(cmd: str) -> bool:
    """Filtro rápido: la orden puede ejecutar Python (o un script de las carpetas vigiladas)."""
    return bool(re.search(r"(?i)python|\bpy\b|\buvx?\b|poetry|pipenv|\bpdm\b|hatch|\brye\b|herramientas|modulos|"
                          r"\.claude", cmd))


def sustituir_variables(token: str) -> str:
    """Sustituye las variables que se conocen con certeza (`$CLAUDE_PROJECT_DIR`): el resto quedan como están."""
    proyecto = str(raiz())
    return re.sub(r"\$\{CLAUDE_PROJECT_DIR\}|\$CLAUDE_PROJECT_DIR(?!\w)", lambda m: proyecto, token)


def expandir(patron: str, entrada: dict | None = None, cwd: str | None = None) -> list:
    """Lo que la shell pondría en lugar de `patron` (comodines de `glob`, sin archivos ocultos salvo `.x*`)."""
    if not tiene_comodin(patron) or len(patron) > 400:
        return []
    p = os.path.expanduser(patron.replace("\\", "/"))
    try:
        if os.path.isabs(p):
            return sorted(glob.glob(p))[:50]
        base_dir = cwd or (entrada or {}).get("cwd") or str(raiz())
        if not os.path.isdir(base_dir):
            return []
        return [os.path.relpath(x, base_dir) for x in sorted(glob.glob(os.path.join(base_dir, p)))[:50]]
    except (OSError, ValueError, re.error):
        return []


def resolver_segmento(seg: dict, entrada: dict | None = None, cwd: str | None = None) -> dict:
    """Copia del segmento con `$CLAUDE_PROJECT_DIR` sustituido y los comodines que dan un único archivo resueltos."""
    nuevos = []
    for t in seg["args"][:200]:
        t2 = sustituir_variables(t)
        if tiene_comodin(t2):
            encontrados = expandir(t2, entrada, cwd)
            if len(encontrados) == 1:
                t2 = encontrados[0]
        nuevos.append(t2)
    return dict(seg, args=nuevos + seg["args"][200:])


def con_cwd(segs: list, entrada: dict | None = None):
    """(segmento resuelto, cwd) de cada segmento que no es `cd`; sigue los `cd` para resolver rutas y comodines."""
    cwd = None
    for seg in segs:
        args = seg["args"]
        if args[:1] == ["cd"] and len(args) > 1:
            cwd = str(resolver_ruta(sustituir_variables(args[1]), entrada or {}, cwd))
            continue
        yield resolver_segmento(seg, entrada, cwd), cwd


def _objetivo_python(args: list, j: int) -> dict:
    while j < len(args):
        a = args[j]
        if a == "--":
            j += 1
            break
        if a == "-" or a.startswith("<"):
            return {"tipo": "stdin", "valor": args[j + 1] if a.startswith("<") and j + 1 < len(args) else "", "i": j}
        if a.startswith("--"):
            j += 2 if a == "--check-hash-based-pycs" else 1
            continue
        if a.startswith("-") and len(a) > 1:
            salto = 1
            for k, ch in enumerate(a[1:], 1):
                if ch in "cm":
                    valor = a[k + 1:] or (args[j + 1] if j + 1 < len(args) else "")
                    return {"tipo": "codigo" if ch == "c" else "modulo", "valor": valor, "i": j}
                if ch in "WX":
                    salto = 1 if a[k + 1:] else 2
                    break
            j += salto
            continue
        break
    if j >= len(args):
        return {"tipo": "stdin", "valor": "", "i": j}
    return {"tipo": "script", "valor": args[j], "i": j}


def _objetivo_uv(args: list, j: int) -> dict | None:
    while j < len(args):
        a = args[j]
        if a == "--":
            j += 1
            break
        if a in ("-m", "--module") or a.startswith("--module="):
            valor = a.split("=", 1)[1] if "=" in a else (args[j + 1] if j + 1 < len(args) else "")
            return {"tipo": "modulo", "valor": valor, "i": j}
        if a in _UV_CON_VALOR:
            j += 2
            continue
        if a.startswith("-"):
            j += 1
            continue
        break
    if j >= len(args):
        return None
    if _INTERPRETE.match(base(args[j])):
        return _objetivo_python(args, j + 1)
    return {"tipo": "script", "valor": args[j], "i": j}  # un .py o una orden del proyecto (motor, ck, pytest…)


def _objetivo_en(args: list, i: int) -> dict | None:
    t = args[i]
    b = base(t).lower()
    siguiente = args[i + 1:i + 3]
    if _INTERPRETE.match(b):
        return _objetivo_python(args, i + 1)
    if b in ("uv", "uv.exe") and siguiente[:1] == ["run"]:
        return _objetivo_uv(args, i + 2)
    if b in ("uv", "uv.exe") and siguiente == ["tool", "run"]:
        return _objetivo_uv(args, i + 3)
    if b in ("uvx", "uvx.exe"):
        return _objetivo_uv(args, i + 1)
    if b in _GESTORES_RUN and siguiente[:1] == ["run"]:
        return _objetivo_uv(args, i + 2)
    if "/" in t.replace("\\", "/") or t.lower().endswith(".py"):  # ./herramientas/x.py con shebang
        return {"tipo": "script", "valor": t, "i": i}
    return None


def objetivo_interprete(args: list) -> dict | None:
    """Qué ejecuta un segmento que lanza Python: {"tipo": script|codigo|modulo|stdin, "valor": …, "i": índice}.

    Solo si el intérprete es el programa (o lo lanza `uv run`, `uvx`, `poetry run`… o `find -exec`): en
    `grep -n python herramientas/*.py`, `python` es un argumento de grep.
    """
    if not args:
        return None
    posiciones = [0]
    if base(args[0]).lower() == "find":
        posiciones = [j + 1 for j, a in enumerate(args[:-1]) if a in _EXEC_FIND]
    for i in posiciones:
        objetivo = _objetivo_en(args, i)
        if objetivo:
            return objetivo
    return None


def _patron_carpetas(carpetas) -> re.Pattern:
    # sin límite por la derecha: en Windows, `herramientas\x.py` sin comillas llega como `herramientasx.py`
    partes = [re.escape(c).replace("/", r"[/\\]*") for c in carpetas]
    return re.compile(r"(?i)(?<![\w-])(?:" + "|".join(partes) + r")")


def _cwd_dentro(cwd, carpetas) -> bool:
    if not cwd:
        return False
    try:
        rel = pathlib.Path(cwd).resolve().relative_to(raiz().resolve()).as_posix()
    except (ValueError, OSError):
        return False
    return any(rel == c or rel.startswith(c + "/") for c in carpetas)


def _corto(texto: str, n: int = 70) -> str:
    texto = re.sub(r"\s+", " ", str(texto)).strip()
    return texto if len(texto) <= n else texto[:n - 1] + "…"


def ejecucion_opaca(seg: dict, entrada: dict | None = None, cwd: str | None = None, carpetas=CARPETAS_SENSIBLES,
                    desconocida: bool = True, cmd: str = "") -> str | None:
    """Motivo si el segmento ejecuta Python sobre `carpetas` de una forma que el hook no puede leer; si no, None.

    `seg` ya debe venir resuelto (`con_cwd`/`resolver_segmento`). `desconocida`: cuenta también lo que no dice sobre
    qué carpeta actúa (`python3 $X`, `-c` con `runpy`/`exec`/`subprocess`); solo debe activarlo un hook por carpeta.
    """
    objetivo = objetivo_interprete(seg["args"])
    if not objetivo:
        return None
    patron = _patron_carpetas(carpetas)
    texto = " ".join(seg["args"] + [str(v) for v in seg["env"].values()])
    dentro = _cwd_dentro(cwd or (entrada or {}).get("cwd"), carpetas)
    menciona = dentro or bool(patron.search(texto))
    tipo, valor = objetivo["tipo"], str(objetivo["valor"] or "")
    if tipo == "codigo":
        if menciona or (desconocida and _CODIGO_DINAMICO.search(valor)):
            return f"ejecuta código en línea con `-c` («{_corto(valor)}»)"
        return None
    if tipo == "stdin":
        todo = cmd or texto
        if dentro or patron.search(todo) or (desconocida and _CODIGO_DINAMICO.search(todo)):
            return "le pasa a Python el código por la entrada estándar (tubería, `<` o heredoc)"
        return None
    if tipo == "modulo":
        raiz_mod = valor.split(".")[0].strip().lower()
        nombres = {c.split("/")[0].lstrip(".").lower() for c in carpetas} | {"runpy"}
        herramienta = "herramientas" in carpetas and bool(raiz_mod) and (
            raiz_mod in _MODULOS_HERRAMIENTAS or (raiz() / "herramientas" / f"{raiz_mod}.py").is_file())
        if raiz_mod in nombres or herramienta or dentro or patron.search(str(seg["env"].get("PYTHONPATH", ""))):
            return f"ejecuta un módulo con `-m {_corto(valor, 40)}`"
        return None
    if "$" in valor or "`" in valor:
        if menciona or (desconocida and valor.lstrip("\"'").startswith(("$", "`"))):
            return f"usa variables o sustituciones en la ruta del script (`{_corto(valor, 60)}`)"
        return None
    if _PUNTOS.search(valor) and menciona:
        return f"usa `..` en la ruta del script (`{_corto(valor, 60)}`)"
    if tiene_comodin(valor):
        encontrados = expandir(valor, entrada, cwd)
        if menciona or any(patron.search(x) for x in encontrados):
            cuantos = ("no casa con ningún archivo" if not encontrados
                       else f"casa con {len(encontrados)} archivos, no con uno solo")
            return f"usa comodines en la ruta del script (`{_corto(valor, 60)}`, que {cuantos})"
    return None


def decision_opaca(entrada: dict, motivo: str, consecuencia: str, ejemplo: str) -> tuple:
    """(decision, motivo) para una ejecución opaca: `deny` en subagentes y `ask` en la sesión principal."""
    if es_subagente(entrada):
        return ("deny", f"Esta orden {motivo}: el hook no puede ver qué script ejecuta ni con qué opciones. Un "
                        "subagente no lanza así nada de herramientas/, modulos/ ni .claude/hooks/: escribe la ruta "
                        f"literal del script (p. ej. `{ejemplo}`).")
    return ("ask", f"No puedo saber qué ejecuta esta orden: {motivo}. {consecuencia} Escribe la ruta literal del "
                   f"script (p. ej. `{ejemplo}`) para que los hooks lo revisen; confirma solo si sabes exactamente qué "
                   "hace.")


# ─────────────────────────────────────────────────────────────── dinero en Meta

# Monedas sin decimales para Meta (offset 1): el importe va en unidades, no en céntimos. [OFFICIAL META]
# developers.facebook.com/docs/marketing-api/currencies
MONEDAS_OFFSET_1 = {"CLP", "COP", "CRC", "HUF", "ISK", "IDR", "JPY", "KRW", "PYG", "TWD", "VND"}

_CLAVES_DIARIO_MINIMO = {"daily_budget", "dailybudget", "budget", "daily_spend_limit"}
_CLAVES_DIARIO_UNIDADES = {"daily_budget_eur", "presupuesto_diario_eur", "presupuesto_diario", "daily_budget_amount"}
_CLAVES_TOTAL_MINIMO = {"lifetime_budget", "lifetimebudget"}
_CLAVES_TOTAL_UNIDADES = {"lifetime_budget_eur", "presupuesto_total_eur", "presupuesto_total"}
_CLAVES_INICIO = ("start_time", "inicio", "start_date")
_CLAVES_FIN = ("end_time", "fin", "end_date", "stop_time")


def _fecha_de(valor) -> datetime | None:
    """Fecha de `start_time`/`end_time`: ISO 8601 o marca Unix en segundos o en milisegundos. None si no se puede leer
    (nunca lanza: una fecha rara no puede tumbar el hook y llevarse el tope por delante)."""
    try:
        if isinstance(valor, str) and re.fullmatch(r"\s*\d{9,}(?:\.\d+)?\s*", valor):
            valor = float(valor)
        if isinstance(valor, (int, float)) and not isinstance(valor, bool) and valor > 10 ** 9:
            segundos = float(valor)
            if segundos > 10 ** 11:  # milisegundos (10**11 s sería el año 5138)
                segundos /= 1000
            return datetime.fromtimestamp(segundos)
        if isinstance(valor, str):
            return leer_ts(valor.replace(" ", "T", 1) if re.match(r"\d{4}-\d{2}-\d{2} \d", valor) else valor)
    except (ValueError, OverflowError, OSError):
        return None
    return None


def presupuestos_en(obj, moneda_iso: str = "EUR") -> list:
    """Presupuestos de una llamada. Cada uno: {clave, diario, alternativo, total, dias, nota}.

    - `diario`: € (o la moneda de la ficha) por día. En la API de Meta, `daily_budget`/`lifetime_budget` van en la
      unidad mínima (céntimos salvo monedas de offset 1).
    - `alternativo`: lectura en unidades si el valor es ambiguo (un entero < 100 céntimos no es un presupuesto
      realista; quizá venía ya en euros). El hook nunca subestima: compara también esta lectura.
    - Presupuesto total sin fechas → diario None y nota.
    """
    salida = []
    offset = 1 if moneda_iso in MONEDAS_OFFSET_1 else 100
    for k, v, padre in recorrer(obj):
        kl = k.lower()
        es_minimo = kl in _CLAVES_DIARIO_MINIMO or kl in _CLAVES_TOTAL_MINIMO
        es_unidades = kl in _CLAVES_DIARIO_UNIDADES or kl in _CLAVES_TOTAL_UNIDADES
        if not (es_minimo or es_unidades):
            continue
        n = numero(v)
        if n is None or n <= 0:
            continue
        total = kl in _CLAVES_TOTAL_MINIMO or kl in _CLAVES_TOTAL_UNIDADES
        alternativo = None
        if es_minimo:
            if offset == 100 and not float(n).is_integer():
                valor = n  # con decimales no pueden ser céntimos: va en unidades
            else:
                valor = n / offset
                if offset == 100 and n < 100:
                    alternativo = n
        else:
            valor = n
        item = {"clave": k, "diario": valor, "alternativo": alternativo, "total": total, "dias": None, "nota": ""}
        if total:
            inicio = next((_fecha_de(padre.get(c)) for c in _CLAVES_INICIO if padre.get(c)), None)
            fin = next((_fecha_de(padre.get(c)) for c in _CLAVES_FIN if padre.get(c)), None)
            if inicio and fin and fin > inicio:
                dias = max(1, -(-int((fin - inicio).total_seconds()) // 86400))
                item.update(diario=valor / dias, dias=dias, importe_total=valor,
                            alternativo=(alternativo / dias if alternativo else None))
            else:
                item.update(diario=None, importe_total=valor,
                            nota=f"presupuesto total de {fmt_dinero(valor, moneda_iso)} sin fechas de inicio y fin: "
                                 "no puedo calcular cuánto gasta al día")
        salida.append(item)
    return salida


_CLAVE_PRESUPUESTO = re.compile(r"(?i)budget|spend_cap|spend_target")
_CLAVE_BANDERA = re.compile(r"(?i)^is_|_(flag|enabled|sharing|type|mode|strategy|optimization)$")
_CLAVES_LIMITE = {"spend_cap", "daily_spend_cap", "lifetime_spend_cap"}  # límites, no presupuestos: basta leerlos
CLAVES_PRESUPUESTO = _CLAVES_DIARIO_MINIMO | _CLAVES_DIARIO_UNIDADES | _CLAVES_TOTAL_MINIMO | _CLAVES_TOTAL_UNIDADES


def presupuestos_ilegibles(obj) -> list:
    """Claves de presupuesto de una llamada que el hook no sabe leer como importe: [(clave, por qué)].

    - Una clave conocida (`daily_budget`, `lifetime_budget`…) o un límite (`spend_cap`…) cuyo valor no es un número
      (un objeto `{amount, currency}`, una lista, un texto): no se puede comparar con el tope.
    - Cualquier otra clave con `budget`, `spend_cap` o `spend_target` (`budget_amount`, `daily_min_spend_target`,
      `budget_schedule_specs`…): el hook no sabe en qué unidad va ni si es diario o total.
    No cuentan las banderas (`is_adset_budget_sharing_enabled`, `budget_rebalance_flag`…) ni los valores vacíos o
    booleanos. `bid_amount` es una puja, no un presupuesto: no entra.
    """
    salida = []
    for k, v, _ in recorrer(obj):
        kl = k.lower()
        conocida = kl in CLAVES_PRESUPUESTO or kl in _CLAVES_LIMITE
        if not (conocida or _CLAVE_PRESUPUESTO.search(kl)):
            continue
        if v is None or isinstance(v, bool) or (isinstance(v, str) and not v.strip()):
            continue
        if _CLAVE_BANDERA.search(kl):
            continue
        if conocida:
            if isinstance(v, (dict, list)):
                salida.append((k, "es un objeto, no un número"))
            elif numero(v) is None:
                salida.append((k, f"«{str(v)[:40]}» no es un número"))
        else:
            salida.append((k, "no es un campo de presupuesto que sepa leer"))
    return salida


def fmt_dinero(valor: float, moneda_iso: str = "EUR") -> str:
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if texto.endswith(",00"):
        texto = texto[:-3]
    return f"{texto} {'€' if moneda_iso == 'EUR' else moneda_iso}"


# ─────────────────────────────────────────────────────────────── nomenclatura (contrato §7)

FORMATOS = ("ugc", "founder", "demo", "testimonio", "podcast", "estatico", "carrusel", "meme", "otro")
_KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
RE_ANUNCIO = re.compile(r"^(\d{8})_(" + _KEBAB + r")_(" + _KEBAB + r")_(" + "|".join(FORMATOS) + r")_(h\d+(?:-c\d+)?)$")
RE_CAMPANA = re.compile(r"^[A-Z]{2,5}(?:-[A-Z]{2,5})*_[A-Z0-9+-]+_[A-Z0-9+-]+_[A-Z0-9+-]+$")
RE_CONJUNTO = re.compile(r"^[A-Z0-9+-]+_[A-Z0-9+-]+$")
_SINONIMOS_FORMATO = {"static": "estatico", "imagen": "estatico", "image": "estatico", "img": "estatico",
                      "carousel": "carrusel", "testimonial": "testimonio", "fundador": "founder"}


def kebab(texto: str) -> str:
    sin_acentos = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sin_acentos.lower()).strip("-")


def parsear_anuncio(nombre: str) -> dict | None:
    m = RE_ANUNCIO.match(nombre or "")
    if not m:
        return None
    try:
        fecha = datetime.strptime(m.group(1), "%Y%m%d").date()
    except ValueError:
        return None
    return {"fecha": fecha, "angulo": m.group(2), "concepto": m.group(3), "formato": m.group(4), "hook": m.group(5)}


def _fecha_flexible(texto: str) -> date | None:
    for formato in ("%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto.strip(), formato).date()
        except ValueError:
            continue
    return None


def sugerir_anuncio(nombre: str) -> str:
    partes = [p for p in re.split(r"[_|]+", (nombre or "").strip()) if p.strip()]
    if len(partes) == 5:
        fecha = _fecha_flexible(partes[0])
        formato = kebab(partes[3])
        formato = _SINONIMOS_FORMATO.get(formato, formato)
        m = re.fullmatch(r"(?i)h(?:ook)?[-_ ]?(\d+)(?:[-_ ]?c(?:uerpo)?[-_ ]?(\d+))?", partes[4].strip())
        if fecha and formato in FORMATOS and m and kebab(partes[1]) and kebab(partes[2]):
            hook = "h" + m.group(1) + ("-c" + m.group(2) if m.group(2) else "")
            return f"{fecha:%Y%m%d}_{kebab(partes[1])}_{kebab(partes[2])}_{formato}_{hook}"
    return f"{ahora():%Y%m%d}_<angulo>_<concepto>_<formato>_h1"


def validar_nombre(nivel: str, nombre: str) -> tuple:
    """(ok, motivo). Mismo formato que herramientas/nomenclatura.py (contrato §7)."""
    nombre = (nombre or "").strip()
    if nivel == "anuncio":
        if parsear_anuncio(nombre):
            return True, ""
        return False, (f"El nombre de anuncio «{nombre}» no cumple la nomenclatura "
                       "<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook> (minúsculas kebab; formato ∈ "
                       f"{'|'.join(FORMATOS)}; hook h<n> o h<n>-c<n>). Propuesta: {sugerir_anuncio(nombre)}")
    if nivel == "campana":
        if RE_CAMPANA.match(nombre):
            return True, ""
        return False, (f"El nombre de campaña «{nombre}» no cumple <MERCADO>_<OBJETIVO>_<PROPOSITO>_<PUJA> en "
                       "mayúsculas (p. ej. ES_LEADS_ADQ_HV).")
    if nivel == "conjunto":
        if RE_CONJUNTO.match(nombre):
            return True, ""
        return False, (f"El nombre de conjunto «{nombre}» no cumple <AUDIENCIA>_<EVENTO> en mayúsculas "
                       "(p. ej. BROAD-A+_LEAD).")
    return True, ""


# ─────────────────────────────────────────────────────────────── veredicto de políticas en LEEME.md

# Contrato §6: `- **Veredicto de políticas:** <valor> · AAAA-MM-DD · <quién>`. Solo cuenta esa línea (al principio de
# línea y fuera de comentarios HTML, para no leer la explicación de la plantilla).
_LINEA_VEREDICTO = re.compile(r"(?im)^[ \t>]*(?:[-*+][ \t]+)?[*_]*[ \t]*veredicto[ \t]+de[ \t]+pol[ií]ticas?"
                              r"[ \t]*[*_]*[ \t]*:[ \t]*[*_]*(?P<valor>[^\n]*)$")
_FIN_VALOR = re.compile(r"\s*·|\s+[|—–-]\s+")
VEREDICTOS_OK = ("ok", "ok con cambios aplicados")


def valor_veredicto(texto: str) -> str | None:
    """Valor de la línea de veredicto (minúsculas, sin markdown, sin fecha ni autor); None si no hay línea."""
    m = _LINEA_VEREDICTO.search(re.sub(r"<!--.*?-->", "", texto, flags=re.S))
    if not m:
        return None
    valor = _FIN_VALOR.split(m.group("valor"), maxsplit=1)[0]
    valor = re.sub(r"[*_`]", "", valor)
    return re.sub(r"\s+", " ", valor).strip(" .;,").lower()


def veredicto_leeme(texto: str) -> str | None:
    """'ok' | 'pendiente' | 'no' según la tabla del contrato §6; None si el LEEME no tiene la línea o está vacía.

    `OK` y `OK con cambios aplicados` → ok; `NO publicar` → no (también con un motivo detrás, p. ej.
    «NO publicar (promesa de ingresos)»: bloquear es más prudente que preguntar); cualquier otro texto, incluidos
    `OK con cambios` y `pendiente` → pendiente.
    """
    valor = valor_veredicto(texto)
    if not valor:
        return None
    if valor.startswith("no publicar"):
        return "no"
    if valor in VEREDICTOS_OK:
        return "ok"
    return "pendiente"
