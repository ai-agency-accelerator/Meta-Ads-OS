#!/usr/bin/env python3
"""Registro obligatorio en el change log (PostToolUse sobre Write/Edit/MultiEdit y Stop).

- PostToolUse: cada vez que se escribe `clientes/<slug>/change-log.md`, lo apunta en `logs/changelog.jsonl`
  (`ts, session, cliente`, contrato §8).
- Stop: si en esta sesión hubo escrituras ejecutadas en Meta, GHL o Stripe (`logs/cambios.jsonl`, por MCP o por
  `meta_ads.py`) que no se han anotado después en el change log de su cliente, no deja terminar y dice cuáles faltan.
  Cuenta como anotado: una entrada de `logs/changelog.jsonl` de esta sesión o un change-log.md modificado después
  de la escritura (también si se editó desde la shell). Si la escritura no tiene cliente, vale el de cualquiera.
- Si Claude ya continúa por este mismo hook (`stop_hook_active`), no vuelve a bloquear (evita bucles): avisa al
  usuario con un mensaje visible.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "registro_obligatorio"
SISTEMAS = ("meta", "ghl", "stripe")
_RUTA_CHANGELOG = re.compile(r"(?:^|[/\\])clientes[/\\]([a-z0-9][a-z0-9-]*)[/\\]change-log\.md$")
MARGEN = timedelta(seconds=2)


def post(e: dict):
    if e.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return None
    ruta = str((e.get("tool_input") or {}).get("file_path") or "")
    m = _RUTA_CHANGELOG.search(ruta)
    if m:
        L.registrar("changelog.jsonl", {"ts": L.ts(), "session": e.get("session_id", ""), "cliente": m.group(1)})
    return None


def inicio_sesion(transcript: str):
    """Primera marca de tiempo del transcript (para atribuir escrituras de la CLI sin id de sesión)."""
    if not transcript:
        return None
    try:
        with open(transcript, encoding="utf-8", errors="replace") as h:
            for _, linea in zip(range(200), h):
                try:
                    fila = json.loads(linea)
                except ValueError:
                    continue
                if isinstance(fila, dict) and fila.get("timestamp"):
                    return L.leer_ts(fila["timestamp"])
    except OSError:
        return None
    return None


def _mtime(ruta: pathlib.Path):
    try:
        return datetime.fromtimestamp(ruta.stat().st_mtime)
    except OSError:
        return None


def escrituras_de_sesion(e: dict) -> list:
    sesion = e.get("session_id", "")
    inicio = inicio_sesion(e.get("transcript_path") or "")
    salida = []
    for fila in L.leer_jsonl("cambios.jsonl"):
        if fila.get("sistema") not in SISTEMAS:
            continue
        t = L.leer_ts(fila.get("ts"))
        if not t:
            continue
        propia = fila.get("session") or ""
        if (sesion and propia == sesion) or (not propia and inicio is not None and t >= inicio):
            salida.append((t, fila))
    return salida


def pendientes(e: dict) -> list:
    escrituras = escrituras_de_sesion(e)
    if not escrituras:
        return []
    sesion = e.get("session_id", "")
    anotaciones = [(L.leer_ts(f.get("ts")), str(f.get("cliente") or "")) for f in L.leer_jsonl("changelog.jsonl")
                   if f.get("session") == sesion]
    carpeta = L.raiz() / "clientes"
    modificados = {}
    if carpeta.is_dir():
        for f in carpeta.glob("*/change-log.md"):
            modificados[f.parent.name] = _mtime(f)
    faltan = []
    for t, fila in escrituras:
        cliente = str(fila.get("cliente") or "")
        hecho = any(ta and ta >= t - MARGEN and (not cliente or ca == cliente) for ta, ca in anotaciones)
        if not hecho:
            fechas = [modificados.get(cliente)] if cliente else list(modificados.values())
            hecho = any(m and m >= t - MARGEN for m in fechas)
        if not hecho:
            faltan.append((t, fila))
    return faltan


def stop(e: dict):
    faltan = pendientes(e)
    if not faltan:
        return None
    lineas = []
    for t, f in faltan[:8]:
        quien = f.get("cliente") or "cliente sin deducir"
        entidad = f" {f.get('entidad_id')}" if f.get("entidad_id") else ""
        lineas.append(f"- {quien}: {f.get('sistema')} · {f.get('accion')}{entidad} ({t:%Y-%m-%d %H:%M})")
    if len(faltan) > 8:
        lineas.append(f"- … y {len(faltan) - 8} más")
    lista = "\n".join(lineas)
    if e.get("stop_hook_active"):
        return {"systemMessage": f"Meta Ads OS: quedan {len(faltan)} escritura(s) sin anotar en el change log:\n{lista}\n"
                                 "Anótalas en clientes/<cliente>/change-log.md antes de seguir."}
    return {"decision": "block",
            "reason": ("Antes de terminar, anota en el change log las escrituras de esta sesión que aún no están:\n"
                       f"{lista}\nUna fila por cambio en clientes/<cliente>/change-log.md con las columnas del contrato "
                       "(Fecha/hora, Quién, Nivel, Objeto (ID), Cambio de → a, Motivo / hipótesis, Métrica de éxito, "
                       "Fecha de evaluación y Resultado vacío). Si una escritura no tuvo efecto, anótalo igual.")}


def logica(e: dict):
    evento = e.get("hook_event_name")
    if evento == "PostToolUse":
        return post(e)
    if evento == "Stop":
        return stop(e)
    return None


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
