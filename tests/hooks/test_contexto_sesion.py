"""contexto_sesion: resumen de ≤6 líneas al empezar, con estado.py o sin él."""
from __future__ import annotations

import json
from datetime import date, timedelta

from ayudas_hooks import SESION, inicio, leer_log


def _lineas(salida) -> list:
    return salida["hookSpecificOutput"]["additionalContext"].splitlines()


def test_instancia_nueva(instancia, correr):
    salida = correr("contexto_sesion", inicio(instancia))
    lineas = _lineas(salida)
    assert 1 <= len(lineas) <= 6
    assert salida["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert salida["systemMessage"] == salida["hookSpecificOutput"]["additionalContext"]
    texto = "\n".join(lineas)
    assert "instalación: sin hacer" in texto and "acme F0" in texto and "Siguiente: /empezar" in texto
    assert "Meta (MCP)" not in texto  # la instancia de prueba no tiene .mcp.json


def test_instancia_en_marcha(instancia, correr):
    hoy = date.today()
    (instancia / "contexto" / "instalacion.json").write_text(json.dumps({"completada": True}), encoding="utf-8")
    (instancia / ".mcp.json").write_text(json.dumps({"mcpServers": {"meta-ads": {"type": "http"}}}), encoding="utf-8")
    vencida = f"{hoy - timedelta(days=1):%Y-%m-%d}"
    with (instancia / "clientes" / "acme" / "change-log.md").open("a", encoding="utf-8") as h:
        h.write(f"| 2026-11-01 10:00 | operador-meta | Conjunto | 120000000000000001 | 30 → 50 €/día | Escalar "
                f"| CPL < 40 € | {vencida} |  |\n")
        h.write(f"| 2026-11-01 11:00 | operador-meta | Anuncio | 120000000000000002 | pausa | Fatiga | — | {vencida} "
                "| Mejoró |\n")
    diario = instancia / "clientes" / "acme" / "informes" / "diario"
    diario.mkdir(parents=True, exist_ok=True)
    (diario / f"{hoy:%Y-%m-%d}.md").write_text("# Brief", encoding="utf-8")
    texto = "\n".join(_lineas(correr("contexto_sesion", inicio(instancia))))
    assert "instalación: completa" in texto and "Meta (MCP)" in texto
    assert "Evaluaciones vencidas: 1" in texto and "120000000000000001" in texto
    assert "Brief de hoy: hecho" in texto and "Siguiente: /hoy" in texto


def _brief(instancia, slug: str, fecha: str, semaforo: str, acciones: int) -> None:
    diario = instancia / "clientes" / slug / "informes" / "diario"
    diario.mkdir(parents=True, exist_ok=True)
    (diario / f"{fecha}.md").write_text(f"---\nfecha: {fecha}\ncliente: {slug}\nsemaforo: {semaforo}\n"
                                        f"acciones: {acciones}\ngenerado: programado\nfuente_meta: mcp\n"
                                        "ventana_atribucion: 7d_click_1d_view\n---\n\n# Brief\n", encoding="utf-8")


def test_brief_de_hoy_con_semaforo(instancia, correr):
    from ayudas_hooks import ficha

    otra = instancia / "clientes" / "nimbo"
    otra.mkdir()
    (otra / "ficha.md").write_text(ficha("nimbo", "act_000000000000001", 50, 150), encoding="utf-8")
    hoy = "2026-11-10"
    _brief(instancia, "acme", hoy, "rojo", 2)
    _brief(instancia, "nimbo", hoy, "verde", 0)
    texto = "\n".join(_lineas(correr("contexto_sesion", inicio(instancia), env={"META_ADS_OS_HOY": hoy})))
    assert "Meta Ads OS · 2026-11-10" in texto
    assert "Brief de hoy: hecho · rojo: acme (2 acciones)" in texto and "nimbo (" not in texto
    _brief(instancia, "nimbo", hoy, "sin-datos", 1)
    texto = "\n".join(_lineas(correr("contexto_sesion", inicio(instancia), env={"META_ADS_OS_HOY": hoy})))
    assert "rojo: acme (2 acciones) · sin datos: nimbo (1 acción)" in texto
    assert len(texto.splitlines()) <= 6


def test_brief_sin_cabecera_no_rompe(instancia, correr):
    diario = instancia / "clientes" / "acme" / "informes" / "diario"
    diario.mkdir(parents=True, exist_ok=True)
    (diario / "2026-11-10.md").write_text("# Brief sin cabecera\n", encoding="utf-8")
    texto = "\n".join(_lineas(correr("contexto_sesion", inicio(instancia), env={"META_ADS_OS_HOY": "2026-11-10"})))
    assert "Brief de hoy: hecho" in texto and "rojo" not in texto


def test_usa_estado_py_si_existe(instancia, correr):
    herramientas = instancia / "herramientas"
    herramientas.mkdir()
    resumen = {"fecha": "2026-11-09", "clientes": [{"slug": "acme", "fase": "F3", "pendientes": ["F3.piezas"],
                                                   "evaluaciones_vencidas": [], "informe_semanal_pendiente": True,
                                                   "brief_hoy": False, "cola_produccion": 2}]}
    (herramientas / "estado.py").write_text(f"import json\nprint(json.dumps({resumen!r}))\n", encoding="utf-8")
    texto = "\n".join(_lineas(correr("contexto_sesion", inicio(instancia))))
    assert "acme F3" in texto and "informe semanal pendiente: acme" in texto


def test_estado_py_roto_degrada(instancia, correr):
    (instancia / "herramientas").mkdir()
    (instancia / "herramientas" / "estado.py").write_text("raise SystemExit(2)\n", encoding="utf-8")
    assert "acme F0" in "\n".join(_lineas(correr("contexto_sesion", inicio(instancia))))


def test_compactar_no_molesta_al_usuario(instancia, correr):
    salida = correr("contexto_sesion", inicio(instancia, source="compact"))
    assert "systemMessage" not in salida and _lineas(salida)


def test_exporta_el_id_de_sesion(instancia, correr):
    destino = instancia / "entorno.sh"
    correr("contexto_sesion", inicio(instancia), env={"CLAUDE_ENV_FILE": str(destino)})
    assert destino.read_text(encoding="utf-8") == f"export CLAUDE_SESSION_ID={SESION}\n"


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import contexto_sesion

    def rota(hoy):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(contexto_sesion, "resumen", rota)
    codigo, salida = en_proceso("contexto_sesion", inicio(instancia))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "contexto_sesion"
