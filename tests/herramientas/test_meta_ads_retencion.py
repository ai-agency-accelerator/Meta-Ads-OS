"""meta_ads.py anuncios (B12): columnas de retención de vídeo, fórmulas y reintento sin los campos nuevos. Sin red."""
from __future__ import annotations

import csv
import importlib
import socket
import urllib.request

import pytest

from http_simulado import HttpSimulado


@pytest.fixture(autouse=True)
def _sin_red(monkeypatch):
    def bloqueado(*_a, **_k):
        raise RuntimeError("Test sin red")

    monkeypatch.setattr(socket.socket, "connect", bloqueado)
    monkeypatch.setattr(socket, "create_connection", bloqueado)
    monkeypatch.setattr(socket, "getaddrinfo", bloqueado)


@pytest.fixture
def meta(instancia, monkeypatch):
    import meta_ads as modulo
    modulo = importlib.reload(modulo)
    monkeypatch.setattr(modulo.time, "sleep", lambda *_: None)
    monkeypatch.delenv("META_TOKEN_ACME", raising=False)
    monkeypatch.setenv("META_TOKEN", "token-global")
    f = instancia / "clientes" / "acme" / "ficha.md"
    f.write_text(f.read_text(encoding="utf-8").replace("act_000000000000000", "act_12345"), encoding="utf-8")
    return modulo


def _accion(valor) -> list[dict]:
    return [{"action_type": "video_view", "value": valor}]


FILA_VIDEO = {
    "ad_id": "120000000000701", "ad_name": "20261102_tiempo-perdido_caso-gestoria_founder_h1", "adset_id": "501",
    "adset_name": "BROAD_LEAD", "campaign_id": "500", "campaign_name": "ES_LEADS_ADQ", "spend": "100.00",
    "impressions": "10000", "reach": "8000", "frequency": "1.25", "inline_link_clicks": "150",
    "date_start": "2026-11-02", "date_stop": "2026-11-08",
    "actions": [{"action_type": "lead", "value": "10"}, {"action_type": "video_view", "value": "2500"}],
    "video_thruplay_watched_actions": _accion("500"),
    "video_p25_watched_actions": _accion("1000"), "video_p50_watched_actions": _accion("600"),
    "video_p75_watched_actions": _accion("300"), "video_p95_watched_actions": _accion("150"),
    "video_p100_watched_actions": _accion("100"), "video_play_actions": _accion("3000"),
    "video_continuous_2_sec_watched_actions": _accion("2600"), "video_avg_time_watched_actions": _accion("7.456"),
    "video_play_curve_actions": [{"action_type": "video_view", "value": [100, 81.6, 60.2, 44, 30]}],
}
FILA_ESTATICO = {k: v for k, v in FILA_VIDEO.items() if not k.startswith("video_")} | {
    "ad_id": "120000000000702", "ad_name": "20261102_tiempo-perdido_dato-horas_estatico_h1",
    "actions": [{"action_type": "lead", "value": "4"}]}


def _http(monkeypatch, insights) -> HttpSimulado:
    http = HttpSimulado()
    http.cuando("GET", r"/act_12345$", {"currency": "EUR"})
    http.cuando("GET", r"/act_12345/insights$", insights)
    http.cuando("GET", r"/act_12345/adsets$", {"data": [{"campaign_id": "500",
                                                         "promoted_object": {"custom_event_type": "LEAD"}}]})
    monkeypatch.setattr(urllib.request, "urlopen", http)
    return http


def _filas(instancia) -> dict[str, dict]:
    ruta = instancia / "clientes" / "acme" / "datos" / "meta-anuncios_2026-11-02_2026-11-08.csv"
    return {f["ad_id"]: f for f in csv.DictReader(ruta.open(encoding="utf-8"))}


def _anuncios(meta) -> None:
    meta.main(["anuncios", "--cliente", "acme", "--desde", "2026-11-02", "--hasta", "2026-11-08"])


def test_pide_los_campos_de_retencion_verificados(meta, instancia, monkeypatch):
    http = _http(monkeypatch, {"data": [FILA_VIDEO]})
    _anuncios(meta)
    campos = http.de("GET", r"/insights$")[0]["query"]["fields"].split(",")
    for campo in ("video_p25_watched_actions", "video_p50_watched_actions", "video_p75_watched_actions",
                  "video_p95_watched_actions", "video_p100_watched_actions", "video_thruplay_watched_actions",
                  "video_play_actions", "video_continuous_2_sec_watched_actions", "video_avg_time_watched_actions",
                  "video_play_curve_actions"):
        assert campo in campos
    assert http.de("POST", ".") == []


def test_retencion_con_formulas_explicitas(meta, instancia, monkeypatch):
    _http(monkeypatch, {"data": [FILA_VIDEO, FILA_ESTATICO]})
    _anuncios(meta)
    f = _filas(instancia)["120000000000701"]
    assert (f["hook_rate"], f["hold_rate"]) == ("25.0", "20.0")          # 2.500/10.000 · 500/2.500
    assert (f["video_p25"], f["video_p95"], f["video_p100"]) == ("1000", "150", "100")
    # retencion_pXX = reproducciones hasta el XX % / vistas de 3 s
    assert [f[f"retencion_p{q}"] for q in (25, 50, 75, 95, 100)] == ["40.0", "24.0", "12.0", "6.0", "4.0"]
    assert (f["reproducciones"], f["vistas_2s_continuas"], f["tiempo_medio_s"]) == ("3000", "2600", "7.46")
    assert f["curva_retencion"] == "100|82|60|44|30"
    assert ";" not in f["curva_retencion"] and "," not in f["curva_retencion"]  # no rompe el Sniffer de B1


def test_estatico_deja_la_retencion_vacia(meta, instancia, monkeypatch):
    _http(monkeypatch, {"data": [FILA_VIDEO, FILA_ESTATICO]})
    _anuncios(meta)
    f = _filas(instancia)["120000000000702"]
    assert all(f[c] == "" for c in ("hook_rate", "hold_rate", "retencion_p25", "retencion_p100", "tiempo_medio_s",
                                    "curva_retencion"))


def test_registro_creativo_sigue_leyendo_el_csv(meta, instancia, monkeypatch):
    _http(monkeypatch, {"data": [FILA_VIDEO]})
    _anuncios(meta)
    import registro_creativo
    ruta = instancia / "clientes" / "acme" / "datos" / "meta-anuncios_2026-11-02_2026-11-08.csv"
    ad = registro_creativo.agregar_meta(registro_creativo.leer_csv(ruta))["120000000000701"]
    assert (ad["gasto"], ad["impresiones"], ad["clics"], ad["vistas_3s"], ad["thruplay"]) == (100.0, 10000, 150, 2500, 500)


def test_error_100_repite_sin_los_campos_nuevos(meta, instancia, monkeypatch, capsys):
    rechazo = (400, {"error": {"code": 100, "message": "(#100) Invalid field video_play_curve_actions"}})
    base = {k: v for k, v in FILA_VIDEO.items() if k not in
            ("video_p95_watched_actions", "video_play_actions", "video_continuous_2_sec_watched_actions",
             "video_avg_time_watched_actions", "video_play_curve_actions")}
    http = _http(monkeypatch, [rechazo, {"data": [base]}])
    _anuncios(meta)
    pedidas = http.de("GET", r"/insights$")
    assert len(pedidas) == 2
    assert pedidas[1]["query"]["fields"] == ",".join(meta.CAMPOS_BASE)
    assert "video_play_curve_actions" not in pedidas[1]["query"]["fields"]
    assert "Repito sin ellos" in capsys.readouterr().err
    f = _filas(instancia)["120000000000701"]
    assert (f["hook_rate"], f["retencion_p25"], f["retencion_p95"], f["curva_retencion"]) == ("25.0", "40.0", "", "")


def test_otro_error_no_se_traga(meta, instancia, monkeypatch):
    http = _http(monkeypatch, [(400, {"error": {"code": 200, "message": "Permissions error"}})])
    with pytest.raises(SystemExit) as salida:
        _anuncios(meta)
    assert salida.value.code == 2
    assert len(http.de("GET", r"/insights$")) == 1


def test_columnas_nuevas_al_final_del_bloque_de_video(meta):
    i = meta.COLUMNAS.index
    assert i("hook_rate") < i("retencion_p25") < i("curva_retencion") < i("evento_resultado")
    assert meta.CAMPOS == meta.CAMPOS_BASE + meta.CAMPOS_RETENCION
    assert len(set(meta.COLUMNAS)) == len(meta.COLUMNAS)
