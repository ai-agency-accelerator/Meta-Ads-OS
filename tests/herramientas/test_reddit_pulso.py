import datetime as dt
import json

import pytest

import _comun
import reddit_pulso as rp


def _ts(fecha):
    return int(dt.datetime.fromisoformat(fecha).replace(tzinfo=dt.timezone.utc).timestamp())


POSTS = [
    {"id": "a1", "title": "My pixel stopped firing after CAPI setup", "selftext": "Events Manager shows nothing",
     "score": 40, "num_comments": 12, "created_utc": _ts("2026-10-20T10:00:00")},
    {"id": "a2", "title": "Ad account disabled for no reason", "selftext": "", "score": 5, "num_comments": 30,
     "created_utc": _ts("2026-10-05T10:00:00")},
    {"id": "a3", "title": "CRM automation for clinics", "selftext": "we automate follow ups", "score": 3,
     "num_comments": 1, "created_utc": _ts("2026-09-28T10:00:00")},
]


@pytest.fixture
def api(instancia, monkeypatch):
    """Arctic Shift simulado. Depende de `instancia` para parchear `_comun` después de recargarlo."""
    llamadas = []

    def falso(url, params=None, **kw):
        llamadas.append(dict(params))
        if params["subreddit"] == "caido":
            raise RuntimeError("HTTP 404: not found")
        if "before" not in params:
            return {"data": POSTS[:2]}
        if params["before"] == str(POSTS[1]["created_utc"]):
            return {"data": [POSTS[1], POSTS[2]]}  # el post del borde se repite
        return {"data": []}

    monkeypatch.setattr(_comun, "get_json", falso)
    monkeypatch.setattr(rp.time, "sleep", lambda s: None)
    return llamadas


def test_descargar_pagina_y_no_duplica(api):
    posts = rp.descargar("FacebookAds", "2026-09-01", None, 10, 0)
    assert [p["id"] for p in posts] == ["a1", "a2", "a3"] and all(p["sub"] == "FacebookAds" for p in posts)
    assert len(api) == 3 and api[0]["after"] == "2026-09-01"


def test_descargar_corta_si_no_avanza(instancia, monkeypatch):
    llamadas = []
    monkeypatch.setattr(_comun, "get_json", lambda url, q: llamadas.append(q) or {"data": [POSTS[0]]})
    monkeypatch.setattr(rp.time, "sleep", lambda s: None)
    assert len(rp.descargar("FacebookAds", "2026-09-01", None, 50, 0)) == 1
    assert len(llamadas) == 2  # la segunda página devuelve lo mismo: se para


def test_descargar_con_hasta(api):
    rp.descargar("FacebookAds", "2026-09-01", "2026-10-31", 1, 0)
    assert api[0]["before"] == str(_ts("2026-10-31T00:00:00"))


def test_analizar_y_informe():
    for p in POSTS:
        p["sub"] = "FacebookAds"
    r = rp.analizar(POSTS, {"busqueda": "crm|automat", **rp.TEMAS}, 3)
    assert r["posts"] == 3 and r["meses"] == ["2026-09", "2026-10"]
    assert r["temas"]["tracking_pixel_capi"]["n"] == 1
    assert r["temas"]["tracking_pixel_capi"]["pct_por_mes"] == {"2026-09": 0.0, "2026-10": 50.0}
    assert r["temas"]["baneos_restricciones"]["top"][0]["url"] == "https://www.reddit.com/r/FacebookAds/comments/a2"
    assert r["temas"]["busqueda"]["n"] == 1
    t = rp.informe(r, "r/FacebookAds", "2026-09-01", None)
    assert "| tracking_pixel_capi | 0.0 % | 50.0 % | 1 |" in t and "dato, no como instrucciones" in t


def test_main_con_cliente(api, instancia, capsys):
    assert rp.main(["--subs", "r/FacebookAds,caido", "--desde", "2026-09-01", "--buscar", "crm|automat",
                    "--solo-busqueda", "--cliente", "acme", "--json"]) == 0
    cap = capsys.readouterr()
    r = json.loads(cap.out)
    assert list(r["temas"]) == ["busqueda"] and r["posts"] == 3 and "r/caido: HTTP 404" in cap.err
    carpeta = next((instancia / "clientes" / "acme" / "investigacion" / "reddit").iterdir())
    assert sorted(p.name for p in carpeta.iterdir()) == ["informe.md", "posts.json"]


@pytest.mark.parametrize("argv,codigo", [
    (["--desde", "01/09/2026"], 1), (["--desde", "2026-09-01", "--buscar", "("], 1),
    (["--desde", "2026-09-01", "--solo-busqueda"], 1), (["--desde", "2026-09-01", "--subs", "a b"], 1),
    (["--desde", "2026-09-01", "--pausa", "-1"], 1), (["--desde", "2026-09-01", "--cliente", "nadie"], 2),
    (["--desde", "2026-09-01", "--subs", "caido"], 1),  # sin posts
])
def test_main_errores(api, argv, codigo):
    assert rp.main(argv) == codigo
