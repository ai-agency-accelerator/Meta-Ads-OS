#!/usr/bin/env python3
"""Guardia de GoHighLevel: MCP `ghl` (PreToolUse y PostToolUse) y llamadas directas a su API vía Bash (PreToolUse).

El MCP oficial de HighLevel tiene pocas herramientas genéricas (`search_operations`, `describe_operation`,
`execute_operation`, `list_locations`…) y `execute_operation` puede leer, escribir, mandar mensajes y borrar. Los
nombres de sus argumentos no están publicados, así que la operación se reconoce por los campos de PRIMER NIVEL con su
id, método o ruta (`operation_id`, `operationId`, `operation`, `name`, `method`, `path`…). Lo que va dentro del
cuerpo (`body.name`, `params.type`…) son datos del contacto, nunca el id de la operación.

Clasificación de `execute_operation`:
- un id de operación anidado (`params.operation_id`…) que manda mensajes, borra o paga → deny;
- varios ids de operación, métodos o rutas distintos en el primer nivel → deny si alguno manda mensajes, borra o
  paga; si no, ask (no se sabe cuál ejecutará GHL);
- lectura (get, list, search…, o método GET) → sin decisión: pregunta la regla `ask` de settings.json. El hook nunca
  da `allow` a `execute_operation`, así que una escritura mal clasificada no puede pasar sin pregunta;
- borrados (delete, remove… o método DELETE) → deny;
- mensajes a contactos (SMS, WhatsApp, email, llamadas, añadir a campañas o workflows que envían) → deny;
- facturas y pagos que escriben (invoices, orders, refunds, subscriptions…) → deny;
- otras escrituras (crear o actualizar contactos, oportunidades, citas, notas…) → ask;
- desconocida o sin id de operación → ask.

Registra todas las llamadas en `logs/ghl-mcp.jsonl` y las escrituras ejecutadas en `logs/cambios.jsonl`.
Solo `operador-meta` escribe: otro subagente que intente escribir → deny.
Cubre el servidor `ghl` y los de agencia por sub-cuenta `ghl-<slug>` (el cliente sale del nombre del servidor).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "ghl_guard"

_CLAVES_OPERACION = ("operation_id", "operationid", "operation", "operation_name", "operationname", "op", "name",
                     "tool", "action", "endpoint_id")
_CLAVES_OPERACION_ANIDADA = ("operation_id", "operationid", "operation_name", "operationname")
_CLAVES_METODO = ("method", "http_method", "httpmethod", "verb")
_CLAVES_RUTA = ("path", "url", "endpoint", "route")

LECTURA = {"get", "list", "search", "find", "fetch", "retrieve", "read", "count", "check", "lookup", "describe",
           "validate", "verify", "preview", "free", "slots", "availability"}
BORRADO = {"delete", "remove", "destroy", "purge", "erase", "unassign", "bulk-delete"}
MENSAJE = {"send", "sms", "whatsapp", "mms", "call", "calls", "voicemail", "broadcast", "reply", "outbound",
           "inbound", "message", "messages", "email-send", "dial", "ringless"}
DISPARA_ENVIOS = {"campaign", "campaigns", "workflow", "workflows", "sequence", "sequences", "drip"}
PAGOS = {"invoice", "invoices", "estimate", "estimates", "payment", "payments", "order", "orders", "transaction",
         "transactions", "subscription", "subscriptions", "refund", "refunds", "charge", "charges", "coupon",
         "coupons", "text2pay", "record-payment", "void", "fulfillment", "fulfillments"}
ESCRITURA = {"create", "update", "upsert", "add", "edit", "set", "post", "put", "patch", "assign", "move", "mark",
             "book", "schedule", "merge", "import", "bulk", "enable", "disable", "change", "publish", "cancel",
             "upload", "tag", "tags", "complete", "trigger", "start", "stop", "pause", "resume"}


def _texto(valor) -> str:
    return valor if isinstance(valor, str) else ""


def _distintos(valores: list) -> list:
    vistos = []
    for v in valores:
        if v not in vistos:
            vistos.append(v)
    return vistos


def candidatos(entrada: dict) -> dict:
    """Ids de operación, métodos y rutas del PRIMER NIVEL (distintos) y los ids de operación anidados."""
    ops, metodos, rutas = [], [], []
    for k, v in (entrada.items() if isinstance(entrada, dict) else []):
        kl = str(k).lower()
        if not _texto(v) or not v.strip():
            continue
        if kl in _CLAVES_OPERACION and len(v) < 200:
            ops.append(v.strip())
        elif kl in _CLAVES_METODO:
            metodos.append(v.strip().upper())
        elif kl in _CLAVES_RUTA and len(v) < 500:
            rutas.append(v.strip())
    anidadas = [v for k, v, padre in L.recorrer(entrada)
                if padre is not entrada and k.lower() in _CLAVES_OPERACION_ANIDADA and _texto(v) and len(v) < 200]
    return {"ops": _distintos(ops), "metodos": _distintos(metodos), "rutas": _distintos(rutas), "anidadas": anidadas}


def analizar(entrada: dict) -> tuple:
    """(tipo, descripción) de una llamada a execute_operation. tipo ∈ lectura | borrado | mensaje | pago | escritura |
    desconocida | varios (ids, métodos o rutas en conflicto)."""
    c = candidatos(entrada)
    for v in c["anidadas"]:  # un id de operación metido en el cuerpo: si es peligroso, no se arriesga
        tipo = clasificar(v, "", "")
        if tipo in MOTIVOS:
            return tipo, v
    ops, metodos, rutas = c["ops"] or [""], c["metodos"] or [""], c["rutas"] or [""]
    combinaciones = [(o, m, r) for o in ops for m in metodos for r in rutas]
    tipos = [(clasificar(o, m, r), o or f"{m} {r}".strip()) for o, m, r in combinaciones]
    peligrosos = [t for t in tipos if t[0] in MOTIVOS]
    if peligrosos:
        orden = ("borrado", "mensaje", "pago")
        return min(peligrosos, key=lambda t: orden.index(t[0]))
    if len(combinaciones) > 1:
        partes = c["ops"] + c["metodos"] + c["rutas"]
        return "varios", " / ".join(partes)[:200]
    tipo, descripcion = tipos[0]
    return tipo, descripcion or "sin id de operación"


def firma(entrada: dict) -> tuple:
    """(id_operacion, metodo, ruta) del primer nivel, solo si cada uno es único (para registros)."""
    c = candidatos(entrada)
    uno = lambda lista: lista[0] if len(lista) == 1 else ""  # noqa: E731
    return uno(c["ops"]), uno(c["metodos"]), uno(c["rutas"])


def _palabras(texto: str) -> list:
    texto = re.sub(r"([a-z])([A-Z])", r"\1 \2", texto)  # camelCase → palabras
    return [p for p in re.split(r"[^a-z0-9]+", texto.lower()) if p]


def clasificar(op: str, metodo: str, ruta: str) -> str:
    """lectura | borrado | mensaje | pago | escritura | desconocida."""
    if not (op or metodo or ruta):
        return "desconocida"
    # el verbo de la operación: lo que va detrás del dominio (contacts_get-contact → get)
    accion = op.split("_", 1)[1] if "_" in op else op
    verbos = _palabras(accion)[:2]
    palabras = set(_palabras(op) + _palabras(ruta))
    if metodo == "DELETE" or palabras & BORRADO:
        return "borrado"
    if verbos and verbos[0] in LECTURA:
        return "lectura"
    if metodo == "GET" and not (set(verbos) & (ESCRITURA | MENSAJE)):
        return "lectura"
    if palabras & MENSAJE or (palabras & DISPARA_ENVIOS and palabras & {"add", "enroll", "trigger", "start",
                                                                          "contact", "contacts", "post"}):
        return "mensaje"
    if palabras & PAGOS:
        return "pago"
    if (set(verbos) & ESCRITURA) or metodo in ("POST", "PUT", "PATCH"):
        return "escritura"
    return "desconocida"


def _cliente(e: dict) -> str | None:
    """Cliente por el servidor: `ghl-<slug>`, `crm.servidor_mcp` de la ficha o la única ficha con CRM ghl."""
    servidor = e.get("mcp_server") or (e.get("tool_name", "").split("__")[1] if "__" in e.get("tool_name", "") else "")
    if servidor.startswith("ghl-") and servidor[4:] in L.fichas():
        return servidor[4:]
    con_ghl = []
    for slug, f in L.fichas().items():
        crm = f.get("crm") if isinstance(f.get("crm"), dict) else {}
        if crm.get("servidor_mcp") and crm.get("servidor_mcp") == servidor and servidor != "ghl":
            return slug
        if str(crm.get("tipo") or "") == "ghl":
            con_ghl.append(slug)
    return con_ghl[0] if len(con_ghl) == 1 else None


MOTIVOS = {
    "borrado": "Los borrados en GoHighLevel están bloqueados en Meta Ads OS. Si de verdad hace falta, hazlo tú en GHL.",
    "mensaje": ("Mandar mensajes a contactos (SMS, WhatsApp, email, llamadas) o meterlos en campañas o workflows que "
                "envían está bloqueado en Meta Ads OS: lo hace una persona desde GHL, no Claude."),
    "pago": ("Crear, enviar o cambiar facturas, pedidos, pagos o suscripciones en GHL está bloqueado en Meta Ads OS: "
             "toca dinero de clientes reales. Hazlo tú en GHL."),
}


def pre_mcp(e: dict):
    tool = e.get("tool_name", "")
    corto = tool.split("__")[-1]
    entrada = e.get("tool_input") or {}
    op, metodo, ruta = firma(entrada) if corto == "execute_operation" else ("", "", "")
    L.registrar("ghl-mcp.jsonl", {"ts": L.ts(), "evento": "PreToolUse", "tool": tool, "agente": L.agente(e),
                                  "session": e.get("session_id", ""), "operacion": op, "metodo": metodo,
                                  "input": entrada})
    if corto != "execute_operation":
        palabras = set(_palabras(corto))
        if palabras & BORRADO:
            return L.pre("deny", MOTIVOS["borrado"])
        if palabras & (LECTURA | {"operations", "locations"}) and not palabras & (ESCRITURA | MENSAJE):
            # descubrimiento o lectura: allow también para servidores `ghl-<slug>`, que no tienen reglas en settings
            return L.pre("allow", f"Lectura en GHL ({corto}).")
        return L.pre("ask", f"Herramienta de GHL desconocida ({corto}): confirma qué hace antes de dejarla pasar.")
    tipo, descripcion = analizar(entrada)
    if tipo == "lectura":
        return None  # pregunta la regla `ask` de settings.json: el hook nunca da allow a execute_operation
    if tipo in MOTIVOS:
        return L.pre("deny", f"{MOTIVOS[tipo]} (operación: {descripcion})")
    if L.es_subagente(e) and L.agente(e) != "operador-meta":
        return L.pre("deny", f"Solo `operador-meta` escribe en GHL; `{L.agente(e)}` es de lectura.")
    cliente = _cliente(e)
    quien = f" de «{cliente}»" if cliente else ""
    if tipo == "varios":
        return L.pre("ask", f"La llamada a GHL{quien} trae varios ids de operación, métodos o rutas distintos "
                            f"({descripcion}): no sé cuál ejecutará GHL. Repítela con uno solo en el primer nivel "
                            "(`operation_id`) antes de confirmar.")
    if tipo == "escritura":
        aviso = ""
        if re.search(r"(?i)appointment|calendar|booking|cita", descripcion):
            aviso = " Ojo: crear o mover citas puede disparar confirmaciones automáticas al contacto."
        return L.pre("ask", f"Escritura en GHL{quien} ({descripcion}). Confirma que es lo aprobado y anótalo en el "
                            f"change log.{aviso}")
    return L.pre("ask", f"Operación de GHL que no sé clasificar ({descripcion}). Comprueba con describe_operation "
                        "qué hace antes de confirmar: si escribe, manda mensajes o borra, recházala.")


def post_mcp(e: dict):
    tool = e.get("tool_name", "")
    if tool.split("__")[-1] != "execute_operation":
        return None
    entrada = e.get("tool_input") or {}
    op, metodo, ruta = firma(entrada)
    tipo, descripcion = analizar(entrada)
    if tipo == "lectura":
        return None
    op = op or descripcion
    resp = e.get("tool_response")
    texto = json.dumps(resp, ensure_ascii=False, default=str) if resp is not None else ""
    fallo = bool(re.search(r'"(isError|is_error)"\s*:\s*true', texto)) or (isinstance(resp, dict) and
                                                                            "error" in resp)
    L.registrar("ghl-mcp.jsonl", {"ts": L.ts(), "evento": "PostToolUse", "tool": tool, "agente": L.agente(e),
                                  "session": e.get("session_id", ""), "operacion": op, "metodo": metodo,
                                  "resultado": "error" if fallo else "ok"})
    if not fallo:
        ids = re.findall(r'"(?:id|contactId|opportunityId|appointmentId)"\s*:\s*"([A-Za-z0-9]{6,})"', texto)
        L.registrar_cambio(e, "ghl", op or f"{metodo} {ruta}".strip(), ids[0] if ids else "", _cliente(e) or "",
                           f"{metodo} {ruta}".strip())
    return None


def pre_bash(e: dict):
    """curl a la API de GHL: lecturas pasan; el resto se clasifica igual que execute_operation."""
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if not re.search(r"leadconnectorhq\.com|gohighlevel\.com", cmd):
        return None
    decisiones = []
    for seg in L.segmentos(cmd):
        args = seg["args"]
        if not args or L.base(args[0]).lower() not in ("curl", "curl.exe", "wget", "http", "https", "xh"):
            continue
        urls = [a for a in args if re.search(r"leadconnectorhq\.com|gohighlevel\.com", a)]
        if not urls:
            continue
        explicito = next((args[i + 1].upper() for i, a in enumerate(args[:-1]) if a in ("-X", "--request")), "")
        con_datos = any(a.startswith(("-d", "--data", "-F", "--form", "--json")) for a in args)
        forzado_get = any(a in ("-G", "--get") for a in args)
        metodo = explicito or ("POST" if con_datos and not forzado_get else "GET")
        ruta = re.sub(r"^https?://[^/]+", "", urls[0])
        tipo = clasificar("", metodo, ruta)
        if tipo == "lectura":
            continue
        if tipo in MOTIVOS:
            decisiones.append(("deny", f"{MOTIVOS[tipo]} ({metodo} {ruta})"))
        else:
            decisiones.append(("ask", f"Escritura directa en la API de GHL ({metodo} {ruta}) fuera del MCP. "
                                      "Confirma que es lo aprobado y anótalo en el change log."))
    return L.combinar(decisiones)


def logica(e: dict):
    evento = e.get("hook_event_name")
    tool = e.get("tool_name", "")
    if re.match(r"mcp__ghl[\w-]*__", tool):
        if evento == "PreToolUse":
            return pre_mcp(e)
        if evento == "PostToolUse":
            return post_mcp(e)
    elif tool == "Bash" and evento == "PreToolUse":
        return pre_bash(e)
    return None


def al_fallar(e: dict):
    """Si la clasificación falla en `execute_operation`, no se queda sin decisión (los servidores `ghl-<slug>` no
    tienen reglas en settings.json): ask en la sesión principal, deny en subagentes."""
    if e.get("hook_event_name") != "PreToolUse":
        return None
    tool = str(e.get("tool_name") or "")
    if not re.match(r"mcp__ghl[\w-]*__execute_operation$", tool):
        return None
    texto = ("No he podido clasificar la operación de GHL (fallo interno de ghl_guard; el detalle queda en "
             "logs/hooks.jsonl)")
    if L.es_subagente(e):
        return L.pre("deny", texto + ": un subagente no la ejecuta sin esa comprobación.")
    return L.pre("ask", texto + ". Comprueba tú en la llamada que es una lectura: si manda mensajes, borra o toca "
                                "pagos, recházala.")


def main() -> int:
    return L.ejecutar(HOOK, logica, al_fallar)


if __name__ == "__main__":
    sys.exit(main())
