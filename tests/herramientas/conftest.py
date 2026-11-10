"""Red de seguridad de B1: los tests de las herramientas de B1 no pueden abrir conexiones de red.

Si uno de esos tests olvida simular `_comun.get_json` / `get_texto` (o lo simula antes de que la fixture `instancia`
recargue `_comun`), falla en vez de salir a internet. Solo se aplica a los módulos de B1: los tests de otros bloques
(p. ej. los que usan `http_simulado.py` con un servidor local) no se tocan.
"""
import socket

import pytest

MODULOS_B1 = {
    "test_ad_library", "test_doctor", "test_economia", "test_embudo", "test_estadistica", "test_estado",
    "test_ig_competidores", "test_landing_check", "test_motor_proyectos", "test_nomenclatura", "test_reddit_pulso",
    "test_registro_creativo", "test_transcribir",
}


@pytest.fixture(autouse=True)
def _sin_red_b1(request, monkeypatch):
    if request.module.__name__.rsplit(".", 1)[-1] not in MODULOS_B1:
        yield
        return

    def bloqueado(*a, **k):
        raise RuntimeError("Test sin red: simula _comun.get_json / _comun.get_texto")

    monkeypatch.setattr(socket.socket, "connect", bloqueado)
    monkeypatch.setattr(socket, "create_connection", bloqueado)
    monkeypatch.setattr(socket, "getaddrinfo", bloqueado)
    yield
