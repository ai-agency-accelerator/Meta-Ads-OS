"""registro_obligatorio: no se cierra la sesión con escrituras en Meta, GHL o Stripe sin anotar en el change log."""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone

from ayudas_hooks import SESION, escribir_log, leer_log, post_archivo, stop


def _cambio(sesion=SESION, minutos=1, cliente="acme", sistema="meta"):
    return {"ts": (datetime.now() - timedelta(minutes=minutos)).isoformat(timespec="seconds"), "session": sesion,
            "sistema": sistema, "via": "mcp", "accion": "ads_update_entity", "entidad_id": "120000000000000001",
            "cliente": cliente, "detalle": "daily_budget=5000"}


def _envejecer_change_log(instancia):
    f = instancia / "clientes" / "acme" / "change-log.md"
    viejo = time.time() - 86400
    os.utime(f, (viejo, viejo))


def test_sin_escrituras_deja_terminar(instancia, correr):
    escribir_log(instancia, "cambios.jsonl", [_cambio(sesion="otra-sesion")])
    assert correr("registro_obligatorio", stop(instancia)) is None


def test_lecturas_o_capi_no_cuentan(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [_cambio(sistema="capi")])
    assert correr("registro_obligatorio", stop(instancia)) is None


def test_escritura_sin_anotar_bloquea_el_cierre(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [_cambio()])
    salida = correr("registro_obligatorio", stop(instancia))
    assert salida["decision"] == "block"
    assert "acme" in salida["reason"] and "120000000000000001" in salida["reason"]


def test_anotar_por_edit_desbloquea(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [_cambio()])
    ruta = str(instancia / "clientes" / "acme" / "change-log.md")
    correr("registro_obligatorio", post_archivo(instancia, "Edit", {"file_path": ruta, "old_string": "|",
                                                                     "new_string": "| 2026-11-09 10:00 |"}))
    fila = leer_log(instancia, "changelog.jsonl")[-1]
    assert fila["cliente"] == "acme" and fila["session"] == SESION and set(fila) == {"ts", "session", "cliente"}
    assert correr("registro_obligatorio", stop(instancia)) is None


def test_anotar_desde_la_shell_tambien_cuenta(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [_cambio(minutos=5)])
    os.utime(instancia / "clientes" / "acme" / "change-log.md", None)  # modificado ahora
    assert correr("registro_obligatorio", stop(instancia)) is None


def test_segundo_intento_avisa_sin_bucle(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [_cambio()])
    salida = correr("registro_obligatorio", stop(instancia, activo=True))
    assert "decision" not in salida and "sin anotar" in salida["systemMessage"]


def test_escrituras_de_la_cli_sin_sesion(instancia, correr):
    _envejecer_change_log(instancia)
    escribir_log(instancia, "cambios.jsonl", [dict(_cambio(sesion=""), via="cli")])
    assert correr("registro_obligatorio", stop(instancia)) is None  # sin transcript no se atribuye
    transcript = instancia / ".transcripts" / f"{SESION}.jsonl"
    transcript.parent.mkdir(parents=True, exist_ok=True)
    inicio = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat().replace("+00:00", "Z")
    transcript.write_text(json.dumps({"type": "user", "timestamp": inicio}) + "\n", encoding="utf-8")
    assert correr("registro_obligatorio", stop(instancia))["decision"] == "block"


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import registro_obligatorio

    def rota(e):
        raise ZeroDivisionError("fallo simulado")

    monkeypatch.setattr(registro_obligatorio, "pendientes", rota)
    codigo, salida = en_proceso("registro_obligatorio", stop(instancia))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "registro_obligatorio"
