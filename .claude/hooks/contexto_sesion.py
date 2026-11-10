#!/usr/bin/env python3
"""Contexto de sesión (SessionStart): un resumen de ≤6 líneas al empezar.

- Instalación (`contexto/instalacion.json`), conexiones (Meta, GHL, Stripe, token avanzado), clientes y su fase,
  evaluaciones vencidas del change log, brief de hoy (`clientes/<slug>/informes/diario/<fecha>.md`, con los clientes
  en rojo, ámbar o sin datos según su cabecera `semaforo`/`acciones`) y siguiente paso.
- Usa `herramientas/estado.py resumen --json` si existe; si no está o falla, lo calcula con su propio código mínimo.
- Lo ve Claude (`additionalContext`) y, al arrancar o reanudar, también el usuario (`systemMessage`).
- Deja `CLAUDE_SESSION_ID` en `CLAUDE_ENV_FILE` (si Claude Code lo ofrece) para que `meta_ads.py` y `capi.py`
  registren sus escrituras con el id de la sesión y `registro_obligatorio` las atribuya bien.
Sin red, sin preguntas y con tiempo acotado: funciona igual con `claude -p` en modo dontAsk.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import date

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _lib as L  # noqa: E402

HOOK = "contexto_sesion"
MAX_LINEAS = 6


def via_estado_py(hoy: date):
    script = L.raiz() / "herramientas" / "estado.py"
    if not script.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, "-I", str(script), "resumen", "--json", "--fecha", f"{hoy:%Y-%m-%d}"],
                           capture_output=True, timeout=8, cwd=str(L.raiz()), stdin=subprocess.DEVNULL)
        datos = json.loads(r.stdout.decode("utf-8", "replace"))
        return datos if isinstance(datos, dict) and isinstance(datos.get("clientes"), list) else None
    except Exception:
        return None


def _fase(carpeta: pathlib.Path) -> str:
    try:
        texto = (carpeta / "estado.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "F0"
    m = re.search(r"^- \[ \] (F\d)\.", texto, re.M)
    if m:
        return m.group(1)
    return "F6" if "- [x]" in texto else "F0"


def evaluaciones_vencidas(carpeta: pathlib.Path, hoy: date) -> list:
    try:
        lineas = (carpeta / "change-log.md").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    cabecera = None
    vencidas = []
    for linea in lineas:
        if not linea.strip().startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if cabecera is None:
            if any("evaluaci" in c.lower() for c in celdas):
                cabecera = [c.lower() for c in celdas]
            continue
        if set("".join(celdas)) <= set("-: "):
            continue
        fila = dict(zip(cabecera, celdas))
        fecha = next((v for k, v in fila.items() if "fecha de evaluaci" in k), "")
        resultado = next((v for k, v in fila.items() if k.startswith("resultado")), "")
        objeto = next((v for k, v in fila.items() if k.startswith("objeto")), "")
        cambio = next((v for k, v in fila.items() if k.startswith("cambio")), "")
        try:
            d = date.fromisoformat(fecha[:10])
        except ValueError:
            continue
        if d <= hoy and not resultado:
            vencidas.append({"fecha": f"{d:%Y-%m-%d}", "objeto": objeto, "cambio": cambio})
    return vencidas


def calcular(hoy: date) -> dict:
    clientes = []
    for slug, ficha in L.fichas().items():
        if str(ficha.get("estado") or "activo") == "pausa":
            continue
        carpeta = L.raiz() / "clientes" / slug
        clientes.append({"slug": slug, "fase": _fase(carpeta),
                         "evaluaciones_vencidas": evaluaciones_vencidas(carpeta, hoy),
                         "brief_hoy": (carpeta / "informes" / "diario" / f"{hoy:%Y-%m-%d}.md").is_file(),
                         "informe_semanal_pendiente": False})
    return {"fecha": f"{hoy:%Y-%m-%d}", "clientes": clientes}


def instalacion() -> str:
    f = L.raiz() / "contexto" / "instalacion.json"
    if not f.is_file():
        return "sin hacer (empieza con /empezar)"
    try:
        datos = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return "archivo ilegible (revísalo con /doctor)"
    if not isinstance(datos, dict):
        return "en curso (/empezar la retoma)"
    if any(datos.get(k) is True for k in ("completada", "completa", "terminada")):
        return "completa"
    if isinstance(datos.get("pendientes"), list):
        return "completa" if not datos["pendientes"] else f"faltan {len(datos['pendientes'])} pasos (/empezar la retoma)"
    fases = datos.get("fases") or datos.get("pasos")
    hechos = (True, "hecho", "hecha", "completa", "completado", "completada", "ok")
    if isinstance(fases, dict):
        faltan = [k for k, v in fases.items() if v not in hechos and not (isinstance(v, dict) and v.get("hecho"))]
        return "completa" if not faltan else f"faltan {len(faltan)} pasos (/empezar la retoma)"
    return "en curso (/empezar la retoma)"


def conexiones() -> str:
    nombres = set()
    try:
        mcp = json.loads((L.raiz() / ".mcp.json").read_text(encoding="utf-8"))
        nombres.update((mcp.get("mcpServers") or {}).keys())
    except (OSError, ValueError, AttributeError):
        pass
    try:  # servidores añadidos con `claude mcp add --scope local` (solo los nombres)
        global_cfg = json.loads((pathlib.Path.home() / ".claude.json").read_text(encoding="utf-8"))
        objetivo = str(L.raiz()).replace("\\", "/").rstrip("/").lower()
        for ruta, proyecto in (global_cfg.get("projects") or {}).items():
            if str(ruta).replace("\\", "/").rstrip("/").lower() == objetivo and isinstance(proyecto, dict):
                nombres.update((proyecto.get("mcpServers") or {}).keys())
    except (OSError, ValueError, AttributeError):
        pass
    partes = []
    partes.append("Meta (MCP)" if "meta-ads" in nombres else "Meta sin conectar (/conectar meta)")
    if any(n.startswith("ghl") for n in nombres):
        partes.append("GHL")
    if any(n.startswith("stripe") for n in nombres):
        partes.append("Stripe")
    partes.append("token avanzado sí" if L.credencial("META_TOKEN") else "sin token avanzado")
    return " · ".join(partes)


SEMAFOROS = (("rojo", "rojo"), ("ambar", "ámbar"), ("sin-datos", "sin datos"))


def semaforos(clientes: list, hoy: date) -> str:
    """Lo que dicen los briefs de hoy: cabecera YAML `semaforo` (verde|ambar|rojo|sin-datos) y `acciones` (§15)."""
    grupos: dict = {clave: [] for clave, _ in SEMAFOROS}
    for c in clientes:
        slug = str(c.get("slug") or "")
        if not c.get("brief_hoy") or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
            continue
        f = L.raiz() / "clientes" / slug / "informes" / "diario" / f"{hoy:%Y-%m-%d}.md"
        try:
            cabecera = "\n".join(f.read_text(encoding="utf-8", errors="replace").splitlines()[:40])
        except OSError:
            continue
        datos = L.parsear_cabecera(cabecera) or {}
        color = str(datos.get("semaforo") or "").strip().lower().replace("á", "a").replace(" ", "-")
        if color in grupos:
            n = L.numero(datos.get("acciones"))
            grupos[color].append(slug + (f" ({int(n)} {'acción' if int(n) == 1 else 'acciones'})" if n else ""))
    return " · ".join(f"{texto}: {', '.join(grupos[clave][:3])}" + (" …" if len(grupos[clave]) > 3 else "")
                      for clave, texto in SEMAFOROS if grupos[clave])


def resumen(hoy: date) -> list:
    datos = via_estado_py(hoy) or calcular(hoy)
    clientes = [c for c in datos.get("clientes") or [] if isinstance(c, dict)]
    lineas = [f"Meta Ads OS · {hoy:%Y-%m-%d} · instalación: {instalacion()}", f"Conexiones: {conexiones()}"]
    if not clientes:
        lineas.append("Clientes: ninguno todavía (/cliente-nuevo).")
    else:
        fases = ", ".join(f"{c.get('slug')} {c.get('fase', '¿?')}" for c in clientes[:6])
        lineas.append(f"Clientes ({len(clientes)}): {fases}{' …' if len(clientes) > 6 else ''}")
        vencidas = [(c.get("slug"), v) for c in clientes for v in (c.get("evaluaciones_vencidas") or [])]
        if vencidas:
            ejemplos = "; ".join(f"{s}: {str(v.get('objeto'))[:40]} ({v.get('fecha')})" for s, v in vencidas[:2])
            lineas.append(f"Evaluaciones vencidas: {len(vencidas)} — {ejemplos}")
        con = [c.get("slug") for c in clientes if c.get("brief_hoy")]
        sin = [c.get("slug") for c in clientes if not c.get("brief_hoy")]
        global_hoy = (L.raiz() / "informes" / "diario" / f"{hoy:%Y-%m-%d}.md").is_file()
        brief = "hecho" if global_hoy or not sin else ("sin hacer" if not con else f"falta en {', '.join(sin[:4])}")
        semanal = [c.get("slug") for c in clientes if c.get("informe_semanal_pendiente")]
        extra = f" · informe semanal pendiente: {', '.join(semanal[:4])}" if semanal else ""
        colores = semaforos(clientes, hoy)
        lineas.append(f"Brief de hoy: {brief}" + (f" · {colores}" if colores else "") + extra)
    instal = instalacion()
    lineas.append("Siguiente: /empezar" if not instal.startswith("completa") else "Siguiente: /hoy")
    return lineas[:MAX_LINEAS]


def exportar_sesion(e: dict) -> None:
    destino = os.environ.get("CLAUDE_ENV_FILE")
    sesion = str(e.get("session_id") or "")
    if not destino or not re.fullmatch(r"[A-Za-z0-9_-]{6,100}", sesion):
        return
    try:
        with open(destino, "a", encoding="utf-8") as h:
            h.write(f"export CLAUDE_SESSION_ID={sesion}\n")
    except OSError:
        pass


def logica(e: dict):
    if e.get("hook_event_name") != "SessionStart":
        return None
    exportar_sesion(e)
    lineas = resumen(L.ahora().date())
    texto = "\n".join(lineas)
    salida = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": texto}}
    if e.get("source", "startup") in ("startup", "resume", "clear"):
        salida["systemMessage"] = texto
    return salida


def main() -> int:
    return L.ejecutar(HOOK, logica)


if __name__ == "__main__":
    sys.exit(main())
