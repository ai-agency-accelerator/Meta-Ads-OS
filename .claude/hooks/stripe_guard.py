#!/usr/bin/env python3
"""Guardia de Stripe: MCP `stripe` (PreToolUse y PostToolUse) y CLI `stripe` o curl a api.stripe.com vía Bash.

Stripe es de SOLO LECTURA en Meta Ads OS: se usa para unir pruebas, pagos y suscripciones con anuncios.
- Lecturas (stripe_api_read, stripe_api_search, stripe_api_details, get_*, list_*, retrieve_*, search_*, fetch_*…)
  → pasan. El id de la operación sale solo de las claves conocidas del PRIMER NIVEL (`stripe_api_operation_id`,
  `operation_id`, `operationId`, `operation`), como en `ghl_guard`:
  - una operación que escribe (PostRefunds, DeleteCoupons…), en el primer nivel o anidada en los parámetros → deny;
  - varios ids distintos en el primer nivel → ask (no se sabe cuál ejecutará Stripe);
  - `stripe_api_read` sin id de operación → ask.
- Cualquier otra herramienta (stripe_api_write, crear, actualizar, reembolsar, cancelar, mover dinero…) → deny,
  también las desconocidas.
- Bash: `stripe <recurso> create|update|delete…`, `stripe post|delete|trigger` y curl con escritura a api.stripe.com
  → deny.
Registra todas las llamadas al MCP en `logs/stripe-mcp.jsonl`. Cubre `stripe` y `stripe-<slug>`.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "stripe_guard"

LECTURAS_CONOCIDAS = {"stripe_api_read", "stripe_api_search", "stripe_api_details", "get_stripe_account_info",
                      "get_balance_summary", "search_stripe_documentation", "stripe_analytics",
                      "stripe_implementation_planner", "search_stripe_resources", "fetch_stripe_resources",
                      "retrieve_balance", "search_documentation"}
_PREFIJOS_LECTURA = ("get_", "list_", "retrieve_", "search_", "fetch_", "read_", "describe_")
_VERBOS_ESCRITURA = re.compile(r"(?i)(create|update|delete|cancel|refund|finalize|void|pay|capture|confirm|send|"
                               r"transfer|convert|setup|close|apply|attach|detach|mark|reverse|post|write|formation|"
                               r"feedback|approve|resume|pause)")
_OPERACION_ESCRITURA = re.compile(r"^\s*((Post|Delete|Put|Patch)[A-Z]|(post|delete|put|patch|POST|DELETE|PUT|PATCH)"
                                  r"[\s_/-])")
_CLAVES_OPERACION = ("stripe_api_operation_id", "operation_id", "operationid", "operation")
_CON_OPERACION = {"stripe_api_read"}  # herramientas genéricas que necesitan el id de la operación
MOTIVO = ("Stripe es de solo lectura en Meta Ads OS: crear, cambiar, reembolsar, cancelar o mover dinero está "
          "bloqueado. Si hace falta, hazlo tú en el Dashboard de Stripe.")


def es_lectura(corto: str) -> bool:
    if corto in LECTURAS_CONOCIDAS:
        return True
    return corto.startswith(_PREFIJOS_LECTURA) and not _VERBOS_ESCRITURA.search(corto.split("_", 1)[1])


def operaciones(entrada: dict) -> tuple:
    """(ids distintos del primer nivel, ids anidados) de la operación de Stripe."""
    primer = []
    for k, v in (entrada.items() if isinstance(entrada, dict) else []):
        if str(k).lower() in _CLAVES_OPERACION and isinstance(v, str) and v.strip() and v.strip() not in primer:
            primer.append(v.strip())
    anidadas = [v for k, v, padre in L.recorrer(entrada)
                if padre is not entrada and k.lower() in _CLAVES_OPERACION and isinstance(v, str) and v.strip()]
    return primer, anidadas


def operacion(entrada: dict) -> str:
    """El id de la operación si hay uno solo en el primer nivel (para registros)."""
    primer, _ = operaciones(entrada)
    return primer[0] if len(primer) == 1 else ""


def pre_mcp(e: dict):
    tool = e.get("tool_name", "")
    corto = tool.split("__")[-1]
    entrada = e.get("tool_input") or {}
    primer, anidadas = operaciones(entrada)
    L.registrar("stripe-mcp.jsonl", {"ts": L.ts(), "evento": "PreToolUse", "tool": tool, "agente": L.agente(e),
                                     "session": e.get("session_id", ""), "operacion": " / ".join(primer),
                                     "input": entrada})
    if not es_lectura(corto):
        return L.pre("deny", f"{MOTIVO} (herramienta: {corto})")
    escriben = [o for o in primer + anidadas if _OPERACION_ESCRITURA.match(o)]
    if escriben:
        return L.pre("deny", f"{MOTIVO} (la operación {escriben[0]} escribe aunque vaya por {corto})")
    if len(primer) > 1:
        return L.pre("ask", f"La llamada a Stripe ({corto}) trae varios ids de operación distintos "
                            f"({' / '.join(primer)[:160]}): no sé cuál ejecutará Stripe. Repítela con uno solo.")
    if corto in _CON_OPERACION and not primer:
        return L.pre("ask", f"La llamada a Stripe ({corto}) no trae el id de la operación en el primer nivel "
                            "(`stripe_api_operation_id`): no sé qué hará. Repítela con él.")
    # allow también para servidores `stripe-<slug>`, que no tienen reglas propias en settings.json
    return L.pre("allow", f"Lectura en Stripe ({corto}).")


def post_mcp(e: dict):
    tool = e.get("tool_name", "")
    corto = tool.split("__")[-1]
    if es_lectura(corto):
        return None
    # No debería ocurrir (las escrituras se bloquean), pero si una pasa queda registrada para el change log.
    entrada = e.get("tool_input") or {}
    L.registrar("stripe-mcp.jsonl", {"ts": L.ts(), "evento": "PostToolUse", "tool": tool, "agente": L.agente(e),
                                     "session": e.get("session_id", ""), "operacion": operacion(entrada)})
    L.registrar_cambio(e, "stripe", corto, "", "", operacion(entrada))
    return None


_CLI_ESCRITURA = re.compile(r"^(create|update|delete|cancel|refund|finalize|void|pay|capture|confirm|send|close|"
                            r"apply|attach|detach|mark_uncollectible|reverse|resume|pause|approve)")


def pre_bash(e: dict):
    cmd = str((e.get("tool_input") or {}).get("command") or "")
    if not re.search(r"stripe", cmd):
        return None
    for seg in L.segmentos(cmd):
        args = seg["args"]
        if not args:
            continue
        programa = L.base(args[0]).lower()
        if programa in ("stripe", "stripe.exe"):
            pos = [a for a in args[1:] if not a.startswith("-")]
            if pos and pos[0] in ("post", "delete", "trigger", "fixtures"):
                return L.pre("deny", f"{MOTIVO} (stripe {pos[0]})")
            if any(_CLI_ESCRITURA.match(p) for p in pos[1:3]):
                return L.pre("deny", f"{MOTIVO} (stripe {' '.join(pos[:2])})")
        if programa in ("curl", "curl.exe", "wget", "http", "https", "xh") and any("api.stripe.com" in a for a in args):
            metodo = next((args[i + 1].upper() for i, a in enumerate(args[:-1]) if a in ("-X", "--request")), "")
            con_datos = any(a.startswith(("-d", "--data", "-F", "--form", "--json", "--post-data")) for a in args)
            forzado_get = any(a in ("-G", "--get") for a in args)
            escribe = (metodo not in ("", "GET")) or (con_datos and not forzado_get and metodo != "GET")
            if escribe:
                return L.pre("deny", f"{MOTIVO} (curl a api.stripe.com con escritura)")
    return None


def logica(e: dict):
    evento = e.get("hook_event_name")
    tool = e.get("tool_name", "")
    if re.match(r"mcp__stripe[\w-]*__", tool):
        if evento == "PreToolUse":
            return pre_mcp(e)
        if evento == "PostToolUse":
            return post_mcp(e)
    elif tool == "Bash" and evento == "PreToolUse":
        return pre_bash(e)
    return None


def al_fallar(e: dict):
    """Si la comprobación falla en una llamada al MCP de Stripe, no se queda sin decisión (settings.json permite las
    lecturas): ask en la sesión principal, deny en subagentes."""
    if e.get("hook_event_name") != "PreToolUse" or not re.match(r"mcp__stripe[\w-]*__", str(e.get("tool_name") or "")):
        return None
    texto = ("No he podido comprobar la llamada a Stripe (fallo interno de stripe_guard; el detalle queda en "
             "logs/hooks.jsonl)")
    if L.es_subagente(e):
        return L.pre("deny", texto + ": un subagente no la ejecuta sin esa comprobación.")
    return L.pre("ask", texto + ". Stripe es de solo lectura aquí: confirma solo si es una lectura.")


def main() -> int:
    return L.ejecutar(HOOK, logica, al_fallar)


if __name__ == "__main__":
    sys.exit(main())
