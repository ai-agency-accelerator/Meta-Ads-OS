"""scripts/validar.py sobre un producto mínimo construido en un directorio temporal."""
from __future__ import annotations

import json
import shutil
import subprocess

import pytest

import validar
from apoyo_scripts import GIT

U = "/" + "Users/"            # partido para que el propio test no cuente como fuga


def _skill(nombre: str, extra: str = "") -> str:
    dmi = "disable-model-invocation: true\n" if nombre in validar.SIN_INVOCACION else ""
    return (f"---\nname: {nombre}\ndescription: \"Skill {nombre}: hace lo suyo y solo lo suyo ({nombre}).\"\n"
            f"argument-hint: \"<cliente>\"\n{dmi}{extra}---\n\nPasos en `meta-ads-kb/00-INDICE-MAESTRO.md`.\n")


def _agente(nombre: str, tools: str = "Read, Grep") -> str:
    return f"---\nname: {nombre}\ndescription: Agente {nombre}\ntools: {tools}\nmodel: inherit\n---\n\nCuerpo.\n"


@pytest.fixture
def producto(tmp_path):
    r = tmp_path / "producto"
    c = r / ".claude"
    for n in (n for g in validar.SKILLS.values() for n in g):
        (c / "skills" / n).mkdir(parents=True)
        (c / "skills" / n / "SKILL.md").write_text(_skill(n), encoding="utf-8")
    (c / "agents").mkdir()
    for n in validar.AGENTES:
        (c / "agents" / f"{n}.md").write_text(_agente(n), encoding="utf-8")
    (c / "hooks").mkdir()
    for n in validar.HOOKS:
        (c / "hooks" / f"{n}.py").write_text("import json\nimport sys\n\nprint(json.dumps({}))\n", encoding="utf-8")
    (c / "hooks" / "_lib.py").write_text("import os\n", encoding="utf-8")
    hooks = [{"matcher": "Bash", "hooks": [{"type": "command",
                                            "command": f'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/{n}.py"'}]}
             for n in validar.HOOKS]
    (c / "settings.json").write_text(json.dumps({"permissions": {"deny": ["Read(./.env)"]},
                                                 "hooks": {"PreToolUse": hooks}}), encoding="utf-8")
    (c / "workflows").mkdir()
    for n in validar.WORKFLOWS:
        (c / "workflows" / f"{n}.js").write_text(
            f"export const meta = {{\n  name: '{n}',\n  description: 'x',\n  phases: [{{ title: 'a', n: 1 }}],\n}}\n"
            "const A = args || {}\nreturn { ok: true, A }\n", encoding="utf-8")
    (c / "output-styles").mkdir()
    for n in validar.ESTILOS:
        (c / "output-styles" / f"{n}.md").write_text(f"---\nname: {n}\ndescription: Estilo {n}\n---\n",
                                                     encoding="utf-8")
    (r / "herramientas").mkdir()
    for n in validar.HERRAMIENTAS:
        (r / "herramientas" / f"{n}.py").write_text("print('ok')\n", encoding="utf-8")
    kb = r / "meta-ads-kb" / "13-sistema-operativo"
    kb.mkdir(parents=True)
    (kb / "01-principios.md").write_text("# Principios\n\n## Regla uno\n", encoding="utf-8")
    (r / "meta-ads-kb" / "00-INDICE-MAESTRO.md").write_text(
        "# Índice\n[Principios](13-sistema-operativo/01-principios.md#regla-uno)\n", encoding="utf-8")
    (r / "plantillas" / "contexto").mkdir(parents=True)
    (r / "plantillas" / "contexto" / "operador.md").write_text("# Operador\n", encoding="utf-8")
    n = validar.CIFRAS
    (r / "CLAUDE.md").write_text(
        f"# Meta Ads OS\n\n@contexto/operador.md\n\n{n['skills']} comandos, {n['agentes']} agentes, {n['hooks']} "
        f"guardas, {n['workflows']} modos profundos y {n['herramientas']} scripts.\n\n- `/empezar` · `/mcp` · "
        "`operador-meta` · `13-sistema-operativo/01-principios.md` · `clientes/<slug>/ficha.md` · "
        "`herramientas/estado.py`\n", encoding="utf-8")
    (r / "docs").mkdir()
    (r / "docs" / "primeros-pasos.md").write_text("# Primeros pasos\n\nVer [principios](../meta-ads-kb/13-sistema-"
                                                  "operativo/01-principios.md).\n", encoding="utf-8")
    (r / "README.md").write_text(f"# Meta Ads OS\n\n{n['skills']} skills y {n['agentes']} agentes. "
                                 "[Docs](docs/primeros-pasos.md)\n", encoding="utf-8")
    return r


def _validar(raiz, *args):
    return validar.validar(raiz, list(validar.SECCIONES) if not args else list(args), None)


def _fallos(inf):
    return [x.mensaje for x in inf.r if x.nivel == "falla"]


def test_producto_minimo_pasa(producto, capsys):
    assert validar.main(["--raiz", str(producto)]) == 0, capsys.readouterr().out


def test_faltan_y_sobran_con_renombradas(producto):
    shutil.rmtree(producto / ".claude" / "skills" / "hoy")
    (producto / ".claude" / "skills" / "pulso").mkdir()
    (producto / ".claude" / "skills" / "pulso" / "SKILL.md").write_text(_skill("pulso"), encoding="utf-8")
    fallos = " | ".join(_fallos(_validar(producto, "cifras")))
    total = validar.CIFRAS["skills"]
    assert f"skills: {total - 1}/{total} · faltan: hoy" in fallos
    assert "sobra «pulso» (renombrada a «brief-diario»)" in fallos


def test_catalogo_de_docs_completo(producto):
    cat = producto / "docs" / "catalogo"
    cat.mkdir()
    todos = {"skills": [n for g in validar.SKILLS.values() for n in g], "agentes": validar.AGENTES + validar.ESTILOS,
             "hooks": validar.HOOKS, "workflows": validar.WORKFLOWS, "herramientas": validar.HERRAMIENTAS}
    for tipo, nombres in todos.items():
        (cat / f"{tipo}.md").write_text("\n".join(f"- `{n}`" for n in nombres) + "\n", encoding="utf-8")
    assert not _fallos(_validar(producto, "cifras"))
    # «operador-meta» no cuenta como el estilo «operador»
    (cat / "agentes.md").write_text("\n".join(f"- `{n}`" for n in validar.AGENTES) + "\n- `profesor`\n",
                                    encoding="utf-8")
    assert any("no documenta estilos: operador" in m for m in _fallos(_validar(producto, "cifras")))


def test_cabeceras(producto):
    (producto / ".claude" / "skills" / "menu" / "SKILL.md").write_text(
        "---\nname: menu\ndescription: \"Menú\"\nargument-hint: \"\"\n---\n", encoding="utf-8")
    (producto / ".claude" / "agents" / "analista-meta.md").write_text(
        _agente("analista-meta", "Read, mcp__meta-ads__ads_get_dataset_stats, mcp__meta-ads__ads_create_campaign"),
        encoding="utf-8")
    (producto / ".claude" / "agents" / "mentor-meta.md").write_text(
        _agente("mentor-meta").replace("model: inherit", "model: opus"), encoding="utf-8")
    (producto / ".claude" / "hooks" / "secretos.py").write_text("import requests\n", encoding="utf-8")
    (producto / ".claude" / "workflows" / "lote-creativo.js").write_text(
        "export const meta = { name: 'lote-creativo', description: `x ${1}` }\nreturn 1\n", encoding="utf-8")
    fallos = " | ".join(_fallos(_validar(producto, "cabeceras")))
    assert "skill menu: escribe, gasta o actualiza" in fallos
    assert "ads_create_campaign" in fallos and "ads_get_dataset_stats" not in fallos
    assert "agente mentor-meta: model «opus»" in fallos
    assert "hook secretos: importa «requests»" in fallos
    assert "workflow lote-creativo" in fallos


def test_workflow_sin_fases_o_con_lo_que_el_runtime_no_tiene(producto):
    wf = producto / ".claude" / "workflows"
    (wf / "investigacion-mercado.js").write_text(
        "export const meta = { name: 'investigacion-mercado', description: 'x' }\nreturn 1\n", encoding="utf-8")
    (wf / "auditoria-profunda.js").write_text(
        "export const meta = { name: 'auditoria-profunda', description: 'x', phases: [] }\n"
        "// Date.now() en un comentario no cuenta\nconst p = 'process.env en un texto tampoco'\n"
        "const fs = require('fs')\nconst t = Date.now()\nreturn { p, t }\n", encoding="utf-8")
    inf = _validar(producto, "cabeceras")
    fallos = " | ".join(_fallos(inf))
    assert "workflow investigacion-mercado: a meta le falta phases" in fallos
    assert "workflow auditoria-profunda: usa require()" in fallos and "process" not in fallos
    avisos = [(x.mensaje, x.linea) for x in inf.r if x.nivel == "aviso"]
    assert ("workflow auditoria-profunda: usa Date.now(); al reanudar daría otro valor", 5) in avisos


def test_workflow_con_error_de_sintaxis(producto):
    if not shutil.which("node"):
        pytest.skip("sin node")
    (producto / ".claude" / "workflows" / "estudio-creativo.js").write_text(
        "export const meta = { name: 'estudio-creativo' }\nconst x = {\nreturn x\n", encoding="utf-8")
    assert any("workflow estudio-creativo" in m for m in _fallos(_validar(producto, "cabeceras")))


def test_enlaces_rotos(producto):
    (producto / "docs" / "faq.md").write_text("[roto](no-existe.md) · `meta-ads-kb/99-nada/x.md`\n",
                                              encoding="utf-8")
    fallos = " | ".join(_fallos(_validar(producto, "enlaces")))
    assert "enlace roto: no-existe.md" in fallos
    assert "meta-ads-kb/99-nada/x.md" in fallos


def test_claude_md(producto):
    claude = producto / "CLAUDE.md"
    claude.write_text(claude.read_text(encoding="utf-8") + "\n`/noexiste` · `herramientas/nada.py` · 39 agentes\n",
                      encoding="utf-8")
    fallos = " | ".join(_fallos(_validar(producto, "claude-md")))
    assert "cita /noexiste" in fallos
    assert "herramientas/nada.py" in fallos
    assert "39 agentes" in fallos


def test_fugas(producto):
    cuenta = "act_" + "1234598765432"
    (producto / "docs" / "fuga.md").write_text(
        f"Ruta {U}maria/proyecto\nCuenta {cuenta} y la de ejemplo act_000000000000000\n"
        "Escribe a ana.garcia" + "@empresa-real.es, a hola@example.com o a soporte@acme-automations.com\n"
        "Token " + "EAA" + "Gm0PX4ZCpsBAKZB7hjhDk9sZBpZC0ZAm3qWe\n"
        'Pixel: "pixel_id": "' + "73920" + '1847201938" · relleno: "adset_id": "120000000000000010"\n',
        encoding="utf-8")
    fallos = " | ".join(_fallos(_validar(producto, "fugas")))
    assert "ruta personal" in fallos
    assert "cuenta publicitaria: " + cuenta in fallos and "act_000000000000000" not in fallos
    assert "email: a***@empresa-real.es" in fallos and "example.com" not in fallos and "acme" not in fallos
    assert "token de Meta: EAAG…" in fallos
    assert "ID de Meta" in fallos and "120000000000000010" not in fallos


def test_datos_con_forma_real_en_tests_son_aviso(producto):
    (producto / "tests").mkdir()
    (producto / "tests" / "test_x.py").write_text(
        'EMAIL = "lucia.perez' + '@gmail.com"\nTEL = "+34 655 ' + '443 322"\n'
        'META = "' + "EAA" + 'Gm0PX4ZCpsBAKZB7hjhDk9sZBpZC0ZAm3qWe"\n', encoding="utf-8")
    inf = _validar(producto, "fugas")
    fallos = " | ".join(_fallos(inf))
    assert "email" not in fallos and "teléfono" not in fallos
    assert "token de Meta" in fallos                     # los tokens nunca se rebajan a aviso
    assert any(x.nivel == "aviso" and "2 email(s) o teléfono(s)" in x.mensaje for x in inf.r)


def test_lista_negra_local(producto, tmp_path):
    lista = tmp_path / "fugas.txt"
    lista.write_text("# nombres propios\nZorblax\n!README.md\n", encoding="utf-8")
    (producto / "docs" / "caso.md").write_text("Caso de Zorblax\n", encoding="utf-8")
    (producto / "README.md").write_text((producto / "README.md").read_text(encoding="utf-8") + "Zorblax\n",
                                        encoding="utf-8")
    inf = validar.validar(producto, ["fugas"], lista)
    fallos = [(x.mensaje, x.archivo) for x in inf.r if x.nivel == "falla"]
    assert ("término de la lista negra «Zorblax»", "docs/caso.md") in fallos
    assert all(a != "README.md" for _, a in fallos)


@pytest.mark.skipif(not GIT, reason="necesita git")
def test_instancia_versionada_es_fuga(producto):
    (producto / ".gitignore").write_text("/clientes/*\n!/clientes/README.md\n", encoding="utf-8")
    (producto / "clientes" / "acme").mkdir(parents=True)
    (producto / "clientes" / "acme" / "ficha.md").write_text("---\nslug: acme\n---\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=producto, check=True)
    subprocess.run(["git", "add", "-f", "clientes/acme/ficha.md"], cwd=producto, check=True)
    assert any("clientes/acme/ficha.md es de la instancia" in m for m in _fallos(_validar(producto, "fugas")))


def test_el_repositorio_real_se_puede_validar(capsys):
    codigo = validar.main(["--json"])
    salida = json.loads(capsys.readouterr().out)
    assert codigo in (0, 1)
    assert codigo == (0 if salida["ok"] else 1)
    assert {r["seccion"] for r in salida["resultados"]} <= set(validar.SECCIONES)
