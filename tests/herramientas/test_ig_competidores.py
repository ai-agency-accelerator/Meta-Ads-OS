import json

import pytest

import _comun
import ig_competidores as ig

CUENTA = {
    "username": "nimbo.ia", "name": "Nimbo", "biography": "Automatizamos\nprocesos con IA", "website": "",
    "followers_count": 2000, "media_count": 120,
    "media": {"data": [
        {"id": "1", "caption": "Caso real #automatizacion #IA", "media_type": "VIDEO", "media_product_type": "REELS",
         "like_count": 90, "comments_count": 10, "timestamp": "2026-11-08T10:00:00+0000", "permalink": "https://x/1"},
        {"id": "2", "caption": "Carrusel #ia", "media_type": "CAROUSEL_ALBUM", "media_product_type": "FEED",
         "like_count": 30, "comments_count": 0, "timestamp": "2026-11-01T10:00:00+0000", "permalink": "https://x/2"},
        {"id": "3", "caption": None, "media_type": "IMAGE", "media_product_type": "FEED", "like_count": None,
         "comments_count": 2, "timestamp": "2026-10-25T10:00:00+0000", "permalink": "https://x/3"},
    ]},
}


@pytest.fixture
def api(instancia, monkeypatch):
    llamadas = []

    def falso(url, params=None, **kw):
        llamadas.append((url, params))
        if "noexiste" in params["fields"]:
            raise RuntimeError("HTTP 400: Invalid user id")
        return {"business_discovery": CUENTA}

    monkeypatch.setattr(_comun, "get_json", falso)
    monkeypatch.setenv("IG_USER_ID", "17800000000000000")
    monkeypatch.setenv("IG_ACCESS_TOKEN", "token-falso")
    return llamadas


def test_analizar():
    r = ig.analizar(CUENTA, "nimbo.ia")
    assert r["posts_analizados"] == 3 and r["dias"] == 14 and r["posts_semana"] == 1.5
    assert r["formatos"] == {"REELS/VIDEO": 1, "FEED/CAROUSEL_ALBUM": 1, "FEED/IMAGE": 1}
    assert r["interaccion_media"] == 44 and r["interaccion_mediana"] == 30
    assert r["interaccion_sobre_seguidores"] == round(132 / 3 / 2000, 4)
    assert r["hashtags"][0] == "ia" and r["top"][0]["enlace"] == "https://x/1"
    assert r["bio"] == "Automatizamos procesos con IA"
    vacia = ig.analizar({"username": "x"}, "x")
    assert vacia["interaccion_media"] is None and vacia["posts_semana"] == 0
    assert "Sin posts" in ig.informe([vacia], {}, ig.dt.date(2026, 11, 9))


def test_fecha_ig():
    assert ig._fecha_ig("2026-11-08T10:00:00+0000").isoformat() == "2026-11-08T10:00:00+00:00"
    assert ig._fecha_ig("2026-11-08T10:00:00Z").year == 2026
    assert ig._fecha_ig("ayer") is None and ig._fecha_ig(None) is None


def test_main_con_cliente_guarda(api, instancia, capsys):
    assert ig.main(["@nimbo.ia", "noexiste", "mal usuario!", "--cliente", "acme", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert [c["usuario"] for c in r["cuentas"]] == ["nimbo.ia"] and "posts" not in r["cuentas"][0]
    assert set(r["errores"]) == {"noexiste", "mal usuario!"} and len(api) == 2
    assert "business_discovery.username(nimbo.ia)" in api[0][1]["fields"]
    carpeta = next((instancia / "clientes" / "acme" / "investigacion" / "instagram").iterdir())
    assert sorted(p.name for p in carpeta.iterdir()) == ["informe.md", "posts.csv"]
    assert "token-falso" not in (carpeta / "informe.md").read_text(encoding="utf-8")


def test_main_texto_y_errores(api, capsys):
    assert ig.main(["nimbo.ia"]) == 0
    assert "## @nimbo.ia — Nimbo" in capsys.readouterr().out
    assert ig.main(["noexiste"]) == 1  # todas fallan
    assert ig.main(["nimbo.ia", "--posts", "500"]) == 1
    assert ig.main(["nimbo.ia", "--cliente", "nadie"]) == 2


def test_sin_credenciales(instancia, monkeypatch, capsys):
    for k in ("IG_USER_ID", "IG_ACCESS_TOKEN", "META_ACCESS_TOKEN"):
        monkeypatch.delenv(k, raising=False)
    assert ig.main(["nimbo.ia"]) == 2
    assert "IG_USER_ID" in capsys.readouterr().err
