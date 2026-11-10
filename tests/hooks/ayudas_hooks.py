"""Entradas JSON con la forma real de Claude Code para probar los hooks (campos comunes + los de cada evento)."""
from __future__ import annotations

import json
import pathlib

RAIZ_PRODUCTO = pathlib.Path(__file__).resolve().parents[2]
HOOKS = RAIZ_PRODUCTO / ".claude" / "hooks"
SESION = "5f1c2a9e-0d4b-4c7e-9a51-3b2f0c6d7e81"
CUENTA = "act_000000000000000"


def _comun(evento: str, raiz, **extra) -> dict:
    datos = {
        "session_id": SESION,
        "transcript_path": str(pathlib.Path(raiz) / ".transcripts" / f"{SESION}.jsonl"),
        "cwd": str(raiz),
        "permission_mode": "default",
        "hook_event_name": evento,
    }
    datos.update(extra)
    return datos


def pre_mcp(raiz, tool: str, tool_input: dict, **extra) -> dict:
    servidor = tool.split("__")[1]
    return _comun("PreToolUse", raiz, tool_name=tool, tool_input=tool_input,
                  tool_use_id="toolu_01AbCdEfGhIjKlMnOpQrStUv", mcp_server=servidor, **extra)


def post_mcp(raiz, tool: str, tool_input: dict, tool_response, **extra) -> dict:
    servidor = tool.split("__")[1]
    return _comun("PostToolUse", raiz, tool_name=tool, tool_input=tool_input, tool_response=tool_response,
                  tool_use_id="toolu_01AbCdEfGhIjKlMnOpQrStUv", mcp_server=servidor, **extra)


def respuesta_mcp(objeto: dict) -> list:
    """Forma habitual de la respuesta de una herramienta MCP: bloques de contenido de texto."""
    return [{"type": "text", "text": json.dumps(objeto)}]


def pre_bash(raiz, command: str, **extra) -> dict:
    return _comun("PreToolUse", raiz, tool_name="Bash",
                  tool_input={"command": command, "description": "Ejecutar orden de prueba"},
                  tool_use_id="toolu_01BashBashBashBashBashBa", **extra)


def pre_archivo(raiz, tool: str, tool_input: dict) -> dict:
    return _comun("PreToolUse", raiz, tool_name=tool, tool_input=tool_input,
                  tool_use_id="toolu_01FileFileFileFileFileFi")


def post_archivo(raiz, tool: str, tool_input: dict) -> dict:
    return _comun("PostToolUse", raiz, tool_name=tool, tool_input=tool_input,
                  tool_response={"filePath": tool_input.get("file_path"), "success": True},
                  tool_use_id="toolu_01FileFileFileFileFileFi")


def stop(raiz, activo: bool = False) -> dict:
    return _comun("Stop", raiz, stop_hook_active=activo, last_assistant_message="Hecho.")


def inicio(raiz, source: str = "startup") -> dict:
    return _comun("SessionStart", raiz, source=source, model="claude-opus-5-5")


def decision(salida) -> str | None:
    if not salida:
        return None
    return (salida.get("hookSpecificOutput") or {}).get("permissionDecision")


def motivo(salida) -> str:
    return ((salida or {}).get("hookSpecificOutput") or {}).get("permissionDecisionReason", "")


def leer_log(raiz, nombre: str) -> list:
    f = pathlib.Path(raiz) / "logs" / nombre
    if not f.exists():
        return []
    return [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]


def escribir_log(raiz, nombre: str, filas: list) -> None:
    f = pathlib.Path(raiz) / "logs" / nombre
    f.parent.mkdir(parents=True, exist_ok=True)
    with f.open("a", encoding="utf-8") as h:
        for fila in filas:
            h.write(json.dumps(fila, ensure_ascii=False) + "\n")


def ficha(slug: str, cuenta: str, cambio: int, total: int, moneda: str = "EUR", crm: str = "ninguno") -> str:
    return f"""---
slug: {slug}
nombre: Cliente de prueba {slug}
estado: activo
tipo: servicios-high-ticket
relacion: cliente
moneda: {moneda}
zona_horaria: Europe/Madrid
meta:
  cuenta: {cuenta}
  pagina: ""
  instagram: ""
  dataset: ""
  catalogo: ""
  evento_principal: Lead
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: {cambio}
  total_dia: {total}
crm:
  tipo: {crm}
  servidor_mcp: ghl
stripe: false
mejoras_automaticas: off
explorar_explotar: 0.3
---

# Cliente de prueba (ficticio)
"""
