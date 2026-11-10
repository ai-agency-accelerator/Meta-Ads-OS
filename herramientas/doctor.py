#!/usr/bin/env python3
"""Comprobaciones de la instalación para `/doctor`: entorno, configuración, instancia y módulos de vídeo.

Incluye, sin red, la coherencia de los nombres de herramientas del MCP de Meta (`mcp_nombres`): los `tools:` de los
agentes usan el servidor `meta-ads` y las skills, los agentes, los workflows, CLAUDE.md y las guías no citan nombres que
no declare ningún agente ni ningún permiso de `.claude/settings.json` (suele ser una generación antigua, como
`ads_catalog_get_catalogs` frente a `ads_catalog_list_catalogs`). Lo que expone de verdad tu servidor no se puede ver
sin conectarse: eso lo comprueba `/conectar meta`.

Uso:
  python3 -I herramientas/doctor.py [--json]

Cada comprobación devuelve {id, ok, detalle, arreglo}; `arreglo` es la orden o el paso concreto para tu sistema
(Mac, Linux o Windows con Git Bash) y va vacío si no hay nada que arreglar. Lo opcional que no tienes instalado
(FFmpeg sin vídeo, el motor, cutkit) sale como ok con la indicación de cómo instalarlo si lo necesitas.
Nunca lee ni imprime el contenido de `.env`: solo mira si existe, sus permisos y si git lo ignora.
Sale con 0 si todo está bien y con 2 si hay algo de configuración que arreglar.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import platform
import re
import shutil
import stat
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _comun  # noqa: E402

PY_MIN = (3, 10)
# Herramienta del MCP de Meta citada en un texto: ads_<familia>_… (no cuenta lo que acaba en * o en _, que es un patrón)
_NOMBRE_META = re.compile(r"(?<![\w-])(ads_(?:get|catalog|insights|create|update|pixel|experiment|library|account|"
                          r"activate|delete|boost)_[a-z0-9_]*[a-z0-9])(?![\w*])")
_TOOL_MCP = re.compile(r"mcp__([A-Za-z0-9_-]+)__([A-Za-z0-9_]+)")


def sistema() -> str:
    """mac | linux | windows (Git Bash, MSYS y Cygwin cuentan como windows)."""
    if os.name == "nt" or sys.platform.startswith(("win", "msys", "cygwin")):
        return "windows"
    return "mac" if sys.platform == "darwin" else "linux"


ARREGLOS = {
    "python": {"mac": "brew install python@3.12  (o: uv python install 3.12)",
               "linux": "sudo apt install python3  (o: uv python install 3.12)",
               "windows": "winget install --id Python.Python.3.12  (y reabre Git Bash)"},
    "uv": {"mac": "curl -LsSf https://astral.sh/uv/install.sh | sh",
           "linux": "curl -LsSf https://astral.sh/uv/install.sh | sh",
           "windows": 'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'},
    "git": {"mac": "xcode-select --install  (o: brew install git)",
            "linux": "sudo apt install git",
            "windows": "winget install --id Git.Git  (incluye Git Bash)"},
    "ffmpeg": {"mac": "brew install ffmpeg",
               "linux": "sudo apt install ffmpeg",
               "windows": "winget install --id Gyan.FFmpeg  (y reabre Git Bash)"},
    "claude": {"mac": "curl -fsSL https://claude.ai/install.sh | bash",
               "linux": "curl -fsSL https://claude.ai/install.sh | bash",
               "windows": 'powershell -c "irm https://claude.ai/install.ps1 | iex"'},
}


def _c(id_: str, ok: bool, detalle: str, arreglo: str = "") -> dict:
    return {"id": id_, "ok": bool(ok), "detalle": detalle, "arreglo": arreglo}


def _version(cmd: list[str]) -> str | None:
    """Primera línea de `<cmd> --version` o None si no se puede ejecutar."""
    exe = shutil.which(cmd[0])
    if not exe:
        return None
    try:
        r = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    salida = (r.stdout or r.stderr or "").strip().splitlines()
    return salida[0][:120] if salida else ""


# ---------------------------------------------------------------- entorno
def c_python(so: str) -> dict:
    v = sys.version_info
    ok = (v.major, v.minor) >= PY_MIN
    return _c("python", ok, f"Python {v.major}.{v.minor}.{v.micro} ({sys.executable})",
              "" if ok else f"Necesitas Python ≥ {PY_MIN[0]}.{PY_MIN[1]}: {ARREGLOS['python'][so]}")


def c_herramienta(id_: str, so: str, opcional_si: bool = False, motivo_opcional: str = "") -> dict:
    v = _version([id_, "-version" if id_ == "ffmpeg" else "--version"])
    if v is not None:
        return _c(id_, True, v or "instalado")
    if opcional_si:
        return _c(id_, True, f"No instalado ({motivo_opcional})", f"Si lo necesitas: {ARREGLOS[id_][so]}")
    return _c(id_, False, "No se encuentra en el PATH", ARREGLOS[id_][so])


# ---------------------------------------------------------------- configuración del producto
def c_mcp() -> dict:
    f = _comun.RAIZ / ".mcp.json"
    if not f.exists():
        return _c("mcp_json", False, "Falta .mcp.json en la raíz",
                  "Recupéralo del repositorio: git checkout -- .mcp.json")
    try:
        datos = json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return _c("mcp_json", False, f".mcp.json no es JSON válido ({e.msg if hasattr(e, 'msg') else e})",
                  "Recupéralo del repositorio: git checkout -- .mcp.json")
    meta = (datos.get("mcpServers") or {}).get("meta-ads") or {}
    if meta.get("url") != "https://mcp.facebook.com/ads":
        return _c("mcp_json", False, "El servidor «meta-ads» no está o no apunta a https://mcp.facebook.com/ads",
                  "Recupéralo del repositorio: git checkout -- .mcp.json")
    return _c("mcp_json", True, "Servidor meta-ads configurado (conéctalo con /conectar meta)")


def c_settings() -> dict:
    f = _comun.RAIZ / ".claude" / "settings.json"
    if not f.exists():
        return _c("settings", False, "Falta .claude/settings.json: los permisos y los hooks no están activos",
                  "Recupéralo del repositorio: git checkout -- .claude/settings.json")
    try:
        json.loads(f.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _c("settings", False, ".claude/settings.json no es JSON válido: Claude Code lo ignorará",
                  "Recupéralo del repositorio: git checkout -- .claude/settings.json")
    return _c("settings", True, "Permisos y hooks configurados")


def _tools_agente(md: pathlib.Path) -> list[str]:
    m = re.match(r"---\r?\n(.*?)\r?\n---", md.read_text(encoding="utf-8", errors="replace"), re.S)
    linea = re.search(r"^tools:\s*(.+)$", m.group(1), re.M) if m else None
    return [t.strip() for t in linea.group(1).split(",") if t.strip()] if linea else []


def c_mcp_nombres() -> dict:
    """Nombres del MCP de Meta coherentes entre agentes, permisos y textos (sin red)."""
    raiz = _comun.RAIZ
    agentes = sorted((raiz / ".claude" / "agents").glob("*.md"))
    if not agentes:
        return _c("mcp_nombres", True, "Sin agentes en .claude/agents/: nada que comparar")
    declarados: set[str] = set()
    servidor_raro: list[str] = []
    for md in agentes:
        for t in _tools_agente(md):
            m = _TOOL_MCP.fullmatch(t)
            if not m:
                continue
            if m.group(1) == "meta-ads":
                declarados.add(m.group(2))
            elif "meta" in m.group(1).lower():
                servidor_raro.append(f"{md.name}: {t}")
    try:
        permisos = json.loads((raiz / ".claude" / "settings.json").read_text(encoding="utf-8")).get("permissions") or {}
    except (OSError, ValueError, AttributeError):
        permisos = {}
    for regla in [r for k in ("allow", "ask", "deny") for r in permisos.get(k) or [] if isinstance(r, str)]:
        m = _TOOL_MCP.fullmatch(regla)
        if m and m.group(1) == "meta-ads":
            declarados.add(m.group(2))
    textos = [*(raiz / ".claude" / "skills").rglob("*.md"), *agentes, *(raiz / ".claude" / "workflows").glob("*.js"),
              raiz / "CLAUDE.md", *(raiz / "docs" / "guias").glob("*.md")]
    sueltos: dict[str, set[str]] = {}
    for f in textos:
        if not f.is_file():
            continue
        for nombre in _NOMBRE_META.findall(f.read_text(encoding="utf-8", errors="replace")):
            if declarados and nombre not in declarados:
                sueltos.setdefault(nombre, set()).add(str(f.relative_to(raiz)))
    problemas = [f"servidor mal escrito en {x} (es mcp__meta-ads__…)" for x in servidor_raro]
    problemas += [f"{n} (en {', '.join(sorted(fs)[:3])}) no lo declara ningún agente ni permiso"
                  for n, fs in sorted(sueltos.items())]
    if problemas:
        return _c("mcp_nombres", False, "Nombres del MCP de Meta incoherentes: " + "; ".join(problemas[:6])
                  + (f" y {len(problemas) - 6} más" if len(problemas) > 6 else ""),
                  "Usa los nombres que declaran los agentes (inventario oficial, el de .claude/agents/operador-meta.md) "
                  "o actualiza el producto con /actualizar")
    return _c("mcp_nombres", True, f"{len(declarados)} herramientas del MCP de Meta, con los mismos nombres en agentes, "
              "permisos y textos (lo que expone tu servidor lo comprueba /conectar meta)")


# ---------------------------------------------------------------- instancia
def c_contexto() -> list[dict]:
    d = _comun.RAIZ / "contexto"
    if not d.is_dir():
        return [_c("contexto", False, "No existe la carpeta contexto/", "Ejecuta bash scripts/instalar.sh y luego /empezar")]
    out = []
    faltan = [n for n in ("operador.md", "preferencias.md") if not (d / n).exists()]
    out.append(_c("contexto", not faltan, "contexto/ completo" if not faltan else f"Faltan en contexto/: {', '.join(faltan)}",
                  "" if not faltan else "Ejecuta /empezar para crearlos"))
    inst = d / "instalacion.json"
    if inst.exists():
        try:
            json.loads(inst.read_text(encoding="utf-8"))
            out.append(_c("instalacion", True, "contexto/instalacion.json válido"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            out.append(_c("instalacion", False, "contexto/instalacion.json no es JSON válido",
                          "Ejecuta /empezar: rehace el estado de la instalación"))
    else:
        out.append(_c("instalacion", False, "Falta contexto/instalacion.json (la instalación no ha terminado)",
                      "Ejecuta /empezar"))
    pref = d / "preferencias.md"
    if pref.exists():
        try:
            p = _comun.parsear_cabecera(pref.read_text(encoding="utf-8"))
            canal = str((p.get("brief") or {}).get("canal", "")) if isinstance(p.get("brief"), dict) else ""
            bien = canal in ("", "telegram", "email", "slack", "ninguno")
            out.append(_c("preferencias", bien, f"Preferencias legibles · canal del brief: {canal or 'sin definir'}",
                          "" if bien else "brief.canal debe ser telegram, email, slack o ninguno"))
        except _comun.FichaInvalida as e:
            out.append(_c("preferencias", False, f"Cabecera de contexto/preferencias.md no válida: {e}",
                          "Corrígela con el formato de plantillas/contexto/preferencias.md"))
    return out


def c_fichas() -> list[dict]:
    d = _comun.CLIENTES
    if not d.is_dir():
        return [_c("clientes", False, "No existe la carpeta clientes/", "Ejecuta bash scripts/instalar.sh")]
    slugs = sorted(x.name for x in d.iterdir() if x.is_dir() and not x.name.startswith((".", "_")))
    if not slugs:
        return [_c("clientes", True, "Aún no hay clientes", "Crea el primero con /cliente-nuevo")]
    out = []
    for s in slugs:
        id_ = f"ficha:{s}"
        try:
            f = _comun.leer_ficha(s)
        except _comun.FichaInvalida as e:
            out.append(_c(id_, False, str(e), f"Corrige clientes/{s}/ficha.md (formato: plantillas/cliente/ficha.md)"))
            continue
        problemas = []
        if f.get("slug") != s:
            problemas.append(f"el slug de la cabecera ({f.get('slug')}) no coincide con la carpeta")
        cuenta = str((f.get("meta") or {}).get("cuenta", "")) if isinstance(f.get("meta"), dict) else ""
        if cuenta and not re.fullmatch(r"act_\d+", cuenta):
            problemas.append(f"meta.cuenta debe ser act_<número> (ahora: {cuenta})")
        topes = f.get("topes") if isinstance(f.get("topes"), dict) else {}
        if str(f.get("estado", "")).lower() == "activo":
            if not cuenta:
                problemas.append("cliente activo sin meta.cuenta")
            if not (isinstance(topes.get("cambio_dia"), (int, float)) and topes.get("cambio_dia", 0) > 0):
                problemas.append("cliente activo con topes.cambio_dia a 0: el sistema no dejará crear ni subir "
                                 "presupuestos")
        if problemas:
            out.append(_c(id_, False, "; ".join(problemas), f"Edita la cabecera de clientes/{s}/ficha.md"))
        else:
            out.append(_c(id_, True, f"{f.get('nombre', s)} · {f.get('estado', '')} · {f.get('tipo', '')}"))
    return out


def c_env(so: str) -> list[dict]:
    f = _comun.RAIZ / ".env"
    if not f.exists():
        return [_c("env", True, "No hay .env (solo hace falta para herramientas con token o el motor)",
                   "Si lo necesitas: crea .env en la raíz y protégelo con chmod 600 .env")]
    out = []
    if so == "windows":
        out.append(_c("env_permisos", True, "En Windows los permisos de .env dependen de tu cuenta de usuario"))
    else:
        modo = stat.S_IMODE(f.stat().st_mode)
        ok = not modo & 0o077
        out.append(_c("env_permisos", ok, f"Permisos de .env: {oct(modo)[2:]}" + ("" if ok else " (otros usuarios pueden leerlo)"),
                      "" if ok else "chmod 600 .env"))
    if shutil.which("git") and (_comun.RAIZ / ".git").exists():
        try:
            r = subprocess.run(["git", "-C", str(_comun.RAIZ), "check-ignore", "-q", ".env"],
                               capture_output=True, timeout=15)
            ignorado = r.returncode == 0
            out.append(_c("env_git", ignorado, ".env está ignorado por git" if ignorado else
                          "¡.env NO está ignorado por git: podrías subir tus claves!",
                          "" if ignorado else "Añade la línea .env a .gitignore y, si ya lo subiste, rota las claves"))
        except (OSError, subprocess.SubprocessError):
            pass
    return out


def c_logs() -> dict:
    d = _comun.LOGS
    if not d.is_dir():
        return _c("logs", False, "No existe la carpeta logs/: los hooks no pueden registrar", "mkdir logs")
    return _c("logs", os.access(d, os.W_OK), "logs/ con permiso de escritura" if os.access(d, os.W_OK)
              else "logs/ no tiene permiso de escritura", "" if os.access(d, os.W_OK) else "chmod u+w logs")


# ---------------------------------------------------------------- módulos de vídeo
def _venv_ok(d: pathlib.Path) -> bool:
    return (d / ".venv" / "bin" / "python").exists() or (d / ".venv" / "Scripts" / "python.exe").exists()


def c_modulos() -> list[dict]:
    out = []
    motor = _comun.RAIZ / "modulos" / "motor-ia"
    if not motor.is_dir():
        out.append(_c("motor_ia", False, "Falta modulos/motor-ia en el producto", "Actualiza con /actualizar"))
    elif _venv_ok(motor):
        clave = "sí" if _comun.credencial("GEMINI_API_KEY") else "no"
        out.append(_c("motor_ia", True, f"Motor de vídeo con IA instalado · clave de Gemini presente: {clave}",
                      "" if clave == "sí" else "Añade GEMINI_API_KEY a .env para producir (sin ella solo MOTOR_MOCK=1)"))
    else:
        out.append(_c("motor_ia", True, "Motor de vídeo con IA no instalado (opcional)", "Si lo quieres: /motor instalar"))
    cutkit = _comun.RAIZ / "modulos" / "cutkit"
    if not cutkit.is_dir():
        out.append(_c("cutkit", False, "Falta modulos/cutkit en el producto", "Actualiza con /actualizar"))
    elif _venv_ok(cutkit):
        out.append(_c("cutkit", True, "cutkit instalado (montaje de vídeo propio)"))
    else:
        out.append(_c("cutkit", True, "cutkit no instalado (opcional)", "Se instala la primera vez que usas /producir-video"))
    return out


def comprobar() -> list[dict]:
    so = sistema()
    modulos = c_modulos()
    usa_video = any(_venv_ok(_comun.RAIZ / "modulos" / m) for m in ("motor-ia", "cutkit"))
    checks = [c_python(so), c_herramienta("uv", so), c_herramienta("git", so),
              c_herramienta("ffmpeg", so, opcional_si=not usa_video, motivo_opcional="solo hace falta para vídeo"),
              c_herramienta("claude", so), c_mcp(), c_settings(), c_mcp_nombres(), *c_contexto(), *c_fichas(), *c_env(so), c_logs(),
              *modulos]
    return checks


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"Error: {message}", file=sys.stderr)
        sys.exit(1)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    ap = _Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    checks = comprobar()
    if a.json:
        print(json.dumps(checks, ensure_ascii=False, indent=2))
    else:
        so = sistema()
        print(f"Doctor de Meta Ads OS · {so} ({platform.platform(terse=True)})\n")
        for c in checks:
            print(f"[{'OK' if c['ok'] else 'FALLA'}] {c['id']}: {c['detalle']}")
            if c["arreglo"]:
                print(f"       {'Arreglo' if not c['ok'] else 'Opcional'}: {c['arreglo']}")
        fallos = sum(not c["ok"] for c in checks)
        if not fallos:
            print("\nTodo en orden.")
        else:
            print(f"\n{fallos} {'cosa' if fallos == 1 else 'cosas'} que arreglar (de arriba abajo).")
    return 0 if all(c["ok"] for c in checks) else 2


if __name__ == "__main__":
    sys.exit(main())
