""".claude/settings.json: permisos, registro de los 10 hooks y lanzador multiplataforma (Mac, Linux y Git Bash)."""
from __future__ import annotations

import ast
import fnmatch
import json
import os
import shutil
import subprocess
import sys

import pytest

from ayudas_hooks import HOOKS, RAIZ_PRODUCTO, decision, pre_bash, pre_mcp

SETTINGS = json.loads((RAIZ_PRODUCTO / ".claude" / "settings.json").read_text(encoding="utf-8"))
PERMISOS = SETTINGS["permissions"]
DIEZ = ("meta_guard", "motor_guard", "ghl_guard", "stripe_guard", "eventos_guard", "control_publicacion",
        "datos_personales", "secretos", "registro_obligatorio", "contexto_sesion")
BASH = shutil.which("bash") or ("/bin/bash" if os.path.exists("/bin/bash") else None)


def _comandos():
    for evento, grupos in SETTINGS["hooks"].items():
        for grupo in grupos:
            for h in grupo["hooks"]:
                yield evento, grupo.get("matcher", ""), h


def _decision_reglas(herramienta: str):
    """Decisión de las reglas MCP (sin hooks): deny > ask > allow; None si ninguna regla aplica."""
    for nivel in ("deny", "ask", "allow"):
        if any(not r.endswith(")") and fnmatch.fnmatchcase(herramienta, r) for r in PERMISOS.get(nivel, [])):
            return nivel
    return None


def _comando_de(hook: str) -> str:
    return next(h["command"] for _, _, h in _comandos() if f"/{hook}.py" in h["command"])


# ─────────────────────────────────────────────── registro de hooks

def test_los_diez_hooks_estan_registrados_y_existen():
    registrados = {h["command"].split("/.claude/hooks/")[1].split(".py")[0] for _, _, h in _comandos()}
    assert registrados == set(DIEZ)
    for nombre in DIEZ:
        assert (HOOKS / f"{nombre}.py").is_file()


def test_eventos_y_matchers():
    def hooks_de(evento, matcher):
        return {h["command"].split("/.claude/hooks/")[1].split(".py")[0]
                for ev, m, h in _comandos() if ev == evento and m == matcher}

    assert "contexto_sesion" in hooks_de("SessionStart", "")
    assert {"meta_guard", "control_publicacion"} <= hooks_de("PreToolUse", "mcp__meta-ads__.*")
    assert hooks_de("PreToolUse", "mcp__ghl.*") == {"ghl_guard"}  # cubre ghl y ghl-<slug>
    assert hooks_de("PreToolUse", "mcp__stripe.*") == {"stripe_guard"}
    assert set(DIEZ) - {"contexto_sesion", "datos_personales", "registro_obligatorio"} <= hooks_de("PreToolUse", "Bash")
    assert "datos_personales" in hooks_de("PreToolUse", "Write|Edit|MultiEdit|NotebookEdit")
    assert "registro_obligatorio" in hooks_de("Stop", "")
    assert "registro_obligatorio" in hooks_de("PostToolUse", "Write|Edit|MultiEdit")


@pytest.mark.parametrize("evento,matcher,h", list(_comandos()))
def test_cada_comando_usa_el_lanzador(evento, matcher, h):
    nombre = h["command"].split("/.claude/hooks/")[1].split(".py")[0]
    ruta = f'"$CLAUDE_PROJECT_DIR/.claude/hooks/{nombre}.py"'
    assert h["type"] == "command"
    assert h["command"] == f"python3 -I {ruta} || python -I {ruta} || py -3 -I {ruta}"
    assert 1 <= h.get("timeout", 600) <= 30  # el brief desatendido no debe quedarse colgado


# ─────────────────────────────────────────────── permisos

def test_reglas_clave():
    allow, ask, deny = PERMISOS["allow"], PERMISOS["ask"], PERMISOS["deny"]
    assert "Bash(python3 -I herramientas/notificar.py*)" in allow
    assert {"Read(./.env)", "Read(./.env.*)", "Read(**/.env)", "Read(**/.env.*)"} <= set(deny)
    assert "Bash(*meta_ads.py* presupuesto*)" in ask and "Bash(*capi.py* enviar*)" in ask
    assert "mcp__meta-ads__ads_catalog_list_*" in allow
    # GHL: execute_operation puede leer, escribir, mandar mensajes y borrar; el hook nunca le da allow (hallazgo 1).
    assert "mcp__ghl__execute_operation" in ask and not any("execute_operation" in r for r in allow)
    # Promocionar una publicación no nace en pausa ni pasa por los topes (hallazgo 5).
    assert "mcp__meta-ads__ads_boost_ig_post" in deny and "mcp__meta-ads__ads_boost_ig_post" not in ask


@pytest.mark.parametrize("herramienta,esperado", [
    ("mcp__meta-ads__ads_get_ad_entities", "allow"),
    ("mcp__meta-ads__ads_insights_performance_trend", "allow"),
    ("mcp__meta-ads__ads_catalog_list_product_sets", "allow"),
    ("mcp__meta-ads__ads_update_entity", "ask"),
    ("mcp__meta-ads__ads_activate_entity", "ask"),
    ("mcp__meta-ads__ads_create_campaign", "ask"),
    ("mcp__meta-ads__ads_delete_entity", "deny"),
    ("mcp__meta-ads__ads_pixel_event_delete", "deny"),
    ("mcp__stripe__stripe_api_read", "allow"),
    ("mcp__stripe__list_customers", "allow"),
    ("mcp__stripe__stripe_api_write", "deny"),
    ("mcp__stripe__create_refund", "deny"),
    ("mcp__stripe__send_money", "deny"),
    ("mcp__ghl__search_operations", "allow"),
    ("mcp__ghl__execute_operation", "ask"),
    ("mcp__meta-ads__ads_boost_ig_post", "deny"),
])
def test_decision_de_las_reglas(herramienta, esperado):
    assert _decision_reglas(herramienta) == esperado


def _decision_bash(orden: str):
    """Aproximación de las reglas Bash(...) (sin hooks): `*` vale cualquier texto; deny > ask > allow."""
    for nivel in ("deny", "ask", "allow"):
        for r in PERMISOS.get(nivel, []):
            if r.startswith("Bash(") and fnmatch.fnmatchcase(orden, r[5:-1]):
                return nivel
    return None


@pytest.mark.parametrize("orden,esperado", [
    # Fotogramas con FFmpeg en segundo plano (B7): sin preguntas; sobrescribir o leer de la red, sí.
    ("ffmpeg -ss 1 -i clientes/acme/creativos/a.mp4 -frames:v 1 clientes/acme/creativos/qa/f_1.png", "allow"),
    ("ffmpeg -i a.mp4 -vf fps=2,scale=270:-1,tile=6x4 -frames:v 1 clientes/acme-yoga/qa/hoja_1.png", "allow"),
    ("ffmpeg -y -i a.mp4 b.png", "ask"),
    ("ffmpeg -i a.mp4 -y b.png", "ask"),
    ("ffmpeg -i https://example.com/a.mp4 b.png", "ask"),
    ("ffmpeg -i a.mp4 -y", "ask"),
    # La regla allow de herramientas/ es un prefijo: `..` encaja; lo frena meta_guard (hallazgo 14).
    ("python3 -I herramientas/../scripts/otro.py", "allow"),
    # Instalación y validación (B9)
    ("python3 -I scripts/instalacion.py ver", "allow"),
    ("python3 scripts/validar.py", "allow"),
    ("python3 -I scripts/validar.py --json", "allow"),
    ("bash scripts/instalar.sh --comprobar", "allow"),
    ("bash scripts/actualizar.sh --comprobar", "allow"),
    ("bash scripts/instalar.sh", None),
    ("bash scripts/actualizar.sh", None),
    # Herramientas: lo que escribe en Meta o envía a la Conversions API pregunta; el resto, libre.
    ("python3 -I herramientas/reglas_meta.py crear clientes/acme/planes/reglas.json --confirmo", "ask"),
    ("python3 -I herramientas/reglas_meta.py pausar 120000000000000200 --confirmo", "ask"),
    ("python3 -I herramientas/reglas_meta.py reactivar 120000000000000200 --confirmo", "ask"),
    ("python3 -I herramientas/reglas_meta.py historial --cliente acme", "allow"),
    ("python3 -I herramientas/formularios_meta.py crear clientes/acme/planes/f.json --confirmo", "ask"),
    ("python3 -I herramientas/formularios_meta.py leads 120000000000000300", "ask"),
    ("python3 -I herramientas/formularios_meta.py ver 120000000000000300", "allow"),
    ("python3 -I herramientas/audiencias_meta.py crear ACME_CRM --confirmo", "ask"),
    ("python3 -I herramientas/audiencias_meta.py sincronizar 1200000000004 --archivo x.csv --confirmo", "ask"),
    ("python3 -I herramientas/audiencias_meta.py etapas --archivo clientes/acme/privado/ghl.csv", "allow"),
    ("python3 -I herramientas/meta_ads.py activar --plan clientes/acme/planes/p.json --confirmo", "ask"),
    ("python3 -I herramientas/capi.py enviar --cliente acme --test-code TEST1 e.json", "ask"),
    ("python3 -I herramientas/capi.py origen --cliente acme", "allow"),
    ("python3 -I herramientas/paginas.py --help", "allow"),
    ("python3 -I herramientas/elementos_creativos.py --help", "allow"),
    ("rm clientes/acme/borrador.md", "ask"),
    ("rm -rf clientes", "deny"),
])
def test_decision_de_las_reglas_bash(orden, esperado):
    assert _decision_bash(orden) == esperado


def test_allow_mcp_con_servidor_literal():
    """En allow, el comodín solo vale tras `mcp__<servidor>__`: un comodín en el servidor se ignoraría."""
    for regla in PERMISOS["allow"]:
        if regla.startswith("mcp__"):
            servidor, _, herramienta = regla[5:].partition("__")
            assert servidor and "*" not in servidor and herramienta, regla


def test_sin_rutas_ni_datos_personales():
    textos = [(RAIZ_PRODUCTO / ".claude" / "settings.json").read_text(encoding="utf-8")]
    textos += [f.read_text(encoding="utf-8") for f in sorted(HOOKS.glob("*.py"))]
    textos += [f.read_text(encoding="utf-8") for f in sorted((RAIZ_PRODUCTO / "tests" / "hooks").glob("*.py"))]
    personal = "/" + "Users" + "/"
    assert not any(personal in t for t in textos)


# ─────────────────────────────────────────────── compatibilidad

def test_sintaxis_compatible_con_python_38():
    for f in sorted(HOOKS.glob("*.py")):
        ast.parse(f.read_text(encoding="utf-8"), filename=str(f), feature_version=(3, 8))
        texto = f.read_text(encoding="utf-8")
        for api in (".removeprefix(", ".removesuffix(", "zoneinfo", "tomllib", "datetime.UTC"):
            assert api not in texto, f"{f.name} usa {api} (no existe en Python 3.8)"


def test_python_antiguo_cede_el_turno_sin_leer_stdin(instancia, en_proceso, monkeypatch):
    monkeypatch.setattr(sys, "version_info", (3, 7, 9))
    codigo, salida = en_proceso("secretos", pre_bash(instancia, "cat .env"))
    assert codigo == 3 and salida is None
    assert sys.stdin.buffer.tell() == 0  # el siguiente intérprete del lanzador recibe la entrada entera


def _python_del_sistema():
    for candidato in ("/usr/bin/python3", shutil.which("python3.8"), shutil.which("python3.9")):
        if not candidato or not os.path.exists(candidato):
            continue
        try:
            version = subprocess.run([candidato, "-I", "-c", "import sys; print(sys.version_info[:2])"],
                                     capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if version in ("(3, 8)", "(3, 9)"):
            return candidato
    return None


@pytest.mark.skipif(_python_del_sistema() is None, reason="no hay un Python 3.8 o 3.9 en el sistema")
@pytest.mark.parametrize("hook,entrada,esperado", [
    ("secretos", lambda r: pre_bash(r, "cat .env"), "deny"),
    ("meta_guard", lambda r: pre_mcp(r, "mcp__meta-ads__ads_delete_entity", {"id": "120000000000000001"}), "deny"),
    ("meta_guard", lambda r: pre_mcp(r, "mcp__meta-ads__ads_update_entity",
                                     {"id": "120000000000000001", "daily_budget": 9000000}), "deny"),
    ("ghl_guard", lambda r: pre_mcp(r, "mcp__ghl__execute_operation",
                                    {"operation_id": "conversations_send-a-new-message"}), "deny"),
    ("stripe_guard", lambda r: pre_mcp(r, "mcp__stripe__stripe_api_write", {}), "deny"),
    ("motor_guard", lambda r: pre_bash(r, "uv run --project modulos/motor-ia motor run p1"), "ask"),
    ("eventos_guard", lambda r: pre_bash(r, "python3 -I herramientas/capi.py enviar --cliente acme --real"), "ask"),
])
def test_los_hooks_corren_en_el_python_del_sistema(instancia, hook, entrada, esperado):
    """El python3 de las herramientas de Xcode en macOS es 3.9: los hooks tienen que funcionar ahí."""
    proceso = subprocess.run([_python_del_sistema(), "-I", str(HOOKS / f"{hook}.py")],
                             input=json.dumps(entrada(instancia)).encode("utf-8"), capture_output=True, timeout=30,
                             env={"PATH": os.environ.get("PATH", ""), "CLAUDE_PROJECT_DIR": str(instancia),
                                  "META_ADS_OS_RAIZ": str(instancia), "HOME": str(instancia / ".home")})
    assert proceso.returncode == 0, proceso.stderr.decode("utf-8", "replace")
    assert decision(json.loads(proceso.stdout)) == esperado
    errores = [l for l in (instancia / "logs" / "hooks.jsonl").read_text(encoding="utf-8").splitlines()
               if '"decision": "error"' in l]
    assert not errores


# ─────────────────────────────────────────────── lanzador real con bash

def _shim(carpeta, nombre: str, cuerpo: str):
    f = carpeta / nombre
    f.write_text("#!/bin/sh\n" + cuerpo + "\n", encoding="utf-8")
    f.chmod(0o755)


def _lanzar(instancia, tmp_path, interpretes: dict, hook="secretos", orden="cat .env"):
    destino = instancia / ".claude" / "hooks"
    if not destino.exists():
        shutil.copytree(HOOKS, destino, ignore=shutil.ignore_patterns("__pycache__"))
    shims = tmp_path / ("shims-" + "-".join(sorted(interpretes)) or "vacio")
    shims.mkdir(exist_ok=True)
    real = sys.executable
    cuerpos = {
        "real": f'exec "{real}" "$@"',
        "tienda": 'echo "Python was not found; run without arguments to install from the Microsoft Store" >&2\n'
                  'exit 9009',
        "py": f'[ "$1" = "-3" ] && shift\nexec "{real}" "$@"',
    }
    for nombre, tipo in interpretes.items():
        _shim(shims, nombre, cuerpos[tipo])
    entrada = json.dumps(pre_bash(instancia, orden)).encode("utf-8")
    return subprocess.run([BASH, "-c", _comando_de(hook)], input=entrada, capture_output=True, timeout=60,
                          env={"PATH": str(shims), "CLAUDE_PROJECT_DIR": str(instancia),
                               "META_ADS_OS_RAIZ": str(instancia), "HOME": str(instancia / ".home")})


@pytest.mark.skipif(BASH is None, reason="sin bash")
@pytest.mark.parametrize("interpretes", [
    {"python3": "real"},                                       # Mac y Linux
    {"python3": "tienda", "python": "real"},                   # Windows: python3 es el aviso de la Microsoft Store
    {"py": "py"},                                              # Windows: solo el lanzador py
    {"python3": "tienda", "py": "py"},
])
def test_lanzador_encuentra_un_python(instancia, tmp_path, interpretes):
    proceso = _lanzar(instancia, tmp_path, interpretes)
    assert proceso.returncode == 0, proceso.stderr.decode("utf-8", "replace")
    salida = json.loads(proceso.stdout)
    assert decision(salida) == "deny"
    proceso.stdout.decode("ascii")  # salida en ASCII: no se rompe en consolas de Windows


@pytest.mark.skipif(BASH is None, reason="sin bash")
def test_lanzador_sin_python_es_error_no_bloqueante(instancia, tmp_path):
    proceso = _lanzar(instancia, tmp_path, {})
    assert proceso.returncode not in (0, 2)  # 2 bloquearía la herramienta; otro código es un aviso y se sigue
    assert not proceso.stdout.strip()
