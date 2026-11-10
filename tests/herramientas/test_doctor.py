import json
import os

import pytest

import doctor


@pytest.fixture
def entorno(instancia, monkeypatch):
    """Instancia con todo lo necesario y las herramientas externas simuladas."""
    monkeypatch.setattr(doctor, "_version", lambda cmd: f"{cmd[0]} 1.0")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    (instancia / ".mcp.json").write_text(json.dumps(
        {"mcpServers": {"meta-ads": {"type": "http", "url": "https://mcp.facebook.com/ads"}}}), encoding="utf-8")
    (instancia / ".claude").mkdir()
    (instancia / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    ctx = instancia / "contexto"
    (ctx / "operador.md").write_text("# Operador\n", encoding="utf-8")
    (ctx / "preferencias.md").write_text("---\nbrief:\n  canal: telegram\n---\n\n# Preferencias\n", encoding="utf-8")
    (ctx / "instalacion.json").write_text("{}", encoding="utf-8")
    for m in ("motor-ia", "cutkit"):
        (instancia / "modulos" / m).mkdir(parents=True)
    return instancia


def _por_id(checks):
    return {c["id"]: c for c in checks}


def test_todo_en_orden(entorno, capsys):
    checks = doctor.comprobar()
    assert all(set(c) == {"id", "ok", "detalle", "arreglo"} for c in checks)
    malos = [c for c in checks if not c["ok"]]
    assert malos == []
    c = _por_id(checks)
    assert c["ficha:acme"]["detalle"].startswith("Acme Automations")
    assert c["motor_ia"]["arreglo"] == "Si lo quieres: /motor instalar"
    assert doctor.main([]) == 0
    assert "Todo en orden." in capsys.readouterr().out


def test_falta_herramienta_y_ffmpeg_opcional(entorno, monkeypatch):
    monkeypatch.setattr(doctor, "_version", lambda cmd: None)
    c = _por_id(doctor.comprobar())
    assert c["uv"]["ok"] is False and "astral.sh/uv" in c["uv"]["arreglo"]
    assert c["claude"]["ok"] is False and "claude.ai/install" in c["claude"]["arreglo"]
    assert c["ffmpeg"]["ok"] is True and c["ffmpeg"]["arreglo"].startswith("Si lo necesitas:")
    # con un módulo de vídeo instalado, FFmpeg pasa a ser obligatorio
    venv = entorno / "modulos" / "cutkit" / ".venv" / "bin"
    venv.mkdir(parents=True)
    (venv / "python").write_text("", encoding="utf-8")
    c = _por_id(doctor.comprobar())
    assert c["ffmpeg"]["ok"] is False and c["cutkit"]["detalle"].startswith("cutkit instalado")


@pytest.mark.parametrize("so,trozo", [("mac", "brew"), ("linux", "apt"), ("windows", "winget")])
def test_arreglos_por_sistema(so, trozo):
    assert trozo in doctor.ARREGLOS["ffmpeg"][so]
    assert set(doctor.ARREGLOS) == {"python", "uv", "git", "ffmpeg", "claude"}
    assert all(set(v) == {"mac", "linux", "windows"} for v in doctor.ARREGLOS.values())


def test_sistema(monkeypatch):
    monkeypatch.setattr(doctor.os, "name", "posix")
    monkeypatch.setattr(doctor.sys, "platform", "darwin")
    assert doctor.sistema() == "mac"
    monkeypatch.setattr(doctor.sys, "platform", "linux")
    assert doctor.sistema() == "linux"
    monkeypatch.setattr(doctor.sys, "platform", "msys")
    assert doctor.sistema() == "windows"


def test_mcp_y_settings(entorno):
    (entorno / ".mcp.json").write_text('{"mcpServers": {"meta-ads": {"url": "https://otro.example"}}}',
                                       encoding="utf-8")
    assert doctor.c_mcp()["ok"] is False
    (entorno / ".mcp.json").write_text("{roto", encoding="utf-8")
    assert doctor.c_mcp()["ok"] is False
    (entorno / ".mcp.json").unlink()
    assert "Falta .mcp.json" in doctor.c_mcp()["detalle"]
    (entorno / ".claude" / "settings.json").write_text("{roto", encoding="utf-8")
    assert doctor.c_settings()["ok"] is False


def test_contexto(entorno):
    ctx = entorno / "contexto"
    (ctx / "preferencias.md").write_text("---\nbrief:\n  canal: whatsapp\n---\n", encoding="utf-8")
    c = _por_id(doctor.c_contexto())
    assert c["preferencias"]["ok"] is False and "telegram" in c["preferencias"]["arreglo"]
    (ctx / "instalacion.json").unlink()
    (ctx / "operador.md").unlink()
    c = _por_id(doctor.c_contexto())
    assert c["instalacion"]["ok"] is False and c["contexto"]["detalle"] == "Faltan en contexto/: operador.md"


def test_fichas(entorno):
    ficha = entorno / "clientes" / "acme" / "ficha.md"
    texto = ficha.read_text(encoding="utf-8")
    ficha.write_text(texto.replace("cuenta: act_000000000000000", "cuenta: 000000000000000")
                     .replace("cambio_dia: 100", "cambio_dia: 0"), encoding="utf-8")
    c = _por_id(doctor.c_fichas())["ficha:acme"]
    assert c["ok"] is False and "act_<número>" in c["detalle"] and "cambio_dia" in c["detalle"]
    ficha.write_text(texto.replace("slug: acme", "slug: otro"), encoding="utf-8")
    assert "no coincide" in _por_id(doctor.c_fichas())["ficha:acme"]["detalle"]
    ficha.write_text("sin cabecera\n", encoding="utf-8")
    assert _por_id(doctor.c_fichas())["ficha:acme"]["ok"] is False
    # un cliente en pausa sin cuenta no es un fallo
    ficha.write_text(texto.replace("estado: activo", "estado: pausa").replace("act_000000000000000", '""'),
                     encoding="utf-8")
    assert _por_id(doctor.c_fichas())["ficha:acme"]["ok"] is True


@pytest.mark.skipif(os.name == "nt", reason="permisos POSIX")
def test_env_sin_leer_su_contenido(entorno, capsys):
    assert doctor.c_env("mac")[0]["ok"] is True  # no hay .env
    env = entorno / ".env"
    env.write_text("# sin claves\n", encoding="utf-8")
    env.chmod(0o644)
    c = doctor.c_env("mac")[0]
    assert c["id"] == "env_permisos" and c["ok"] is False and c["arreglo"] == "chmod 600 .env"
    env.chmod(0o600)
    assert doctor.c_env("mac")[0]["ok"] is True
    assert doctor.c_env("windows")[0]["ok"] is True


def test_modulos_y_clave(entorno, monkeypatch):
    venv = entorno / "modulos" / "motor-ia" / ".venv" / "bin"
    venv.mkdir(parents=True)
    (venv / "python").write_text("", encoding="utf-8")
    c = _por_id(doctor.c_modulos())["motor_ia"]
    assert c["ok"] is True and "presente: no" in c["detalle"] and "GEMINI_API_KEY" in c["arreglo"]
    monkeypatch.setenv("GEMINI_API_KEY", "falsa")
    c = _por_id(doctor.c_modulos())["motor_ia"]
    assert "presente: sí" in c["detalle"] and "falsa" not in json.dumps(c)
    (entorno / "modulos" / "cutkit").rmdir()
    assert _por_id(doctor.c_modulos())["cutkit"]["ok"] is False


def test_main_falla_con_2_y_json(entorno, capsys):
    (entorno / "logs").rmdir()
    assert doctor.main(["--json"]) == 2
    datos = json.loads(capsys.readouterr().out)
    assert {"id": "logs", "ok": False, "detalle": "No existe la carpeta logs/: los hooks no pueden registrar",
            "arreglo": "mkdir logs"} in datos
    assert doctor.main([]) == 2
    out = capsys.readouterr().out
    assert "[FALLA] logs" in out and "1 cosa que arreglar" in out
    with pytest.raises(SystemExit) as e:
        doctor.main(["--desconocido"])
    assert e.value.code == 1


def test_instancia_vacia(instancia, monkeypatch):
    monkeypatch.setattr(doctor, "_version", lambda cmd: "x 1.0")
    c = _por_id(doctor.comprobar())
    assert c["mcp_json"]["ok"] is False and c["instalacion"]["ok"] is False
    assert c["motor_ia"]["ok"] is False and c["motor_ia"]["arreglo"] == "Actualiza con /actualizar"


def _agente(raiz, nombre, tools):
    d = raiz / ".claude" / "agents"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{nombre}.md").write_text(f"---\nname: {nombre}\ndescription: x\ntools: {tools}\n---\n\nCuerpo.\n",
                                    encoding="utf-8")


def test_nombres_mcp_coherentes(entorno):
    _agente(entorno, "operador-meta", "Read, mcp__meta-ads__ads_get_ad_accounts, mcp__meta-ads__ads_catalog_list_catalogs")
    (entorno / ".claude" / "settings.json").write_text(json.dumps(
        {"permissions": {"deny": ["mcp__meta-ads__ads_delete_custom_audience", "mcp__meta-ads__ads_get_*"]}}),
        encoding="utf-8")
    skill = entorno / ".claude" / "skills" / "cliente-nuevo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("Usa `ads_get_ad_accounts`, `ads_catalog_list_catalogs`, `ads_catalog_list_*` y "
                                    "nunca `ads_delete_custom_audience`.\n", encoding="utf-8")
    c = _por_id(doctor.comprobar())["mcp_nombres"]
    assert c["ok"] is True and c["detalle"].startswith("3 herramientas")
    (skill / "SKILL.md").write_text("Y después `ads_catalog_get_catalogs`.\n", encoding="utf-8")
    c = _por_id(doctor.comprobar())["mcp_nombres"]
    assert c["ok"] is False and "ads_catalog_get_catalogs (en .claude/skills/cliente-nuevo/SKILL.md)" in c["detalle"]
    _agente(entorno, "analista", "mcp__meta_ads__ads_get_ad_entities")
    c = _por_id(doctor.comprobar())["mcp_nombres"]
    assert "servidor mal escrito en analista.md" in c["detalle"]


def test_nombres_mcp_sin_agentes(entorno):
    assert _por_id(doctor.comprobar())["mcp_nombres"]["ok"] is True
