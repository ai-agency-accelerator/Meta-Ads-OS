import datetime as dt
import json

import pytest

import _comun
import ad_library

HOY = dt.date(2026, 11, 9)


def _ad(i, pagina="Competidor A", page_id="111111111111111", inicio="2026-09-01", fin=None, texto="Automatiza tu "
        "atención al cliente con IA"):
    d = {"id": f"9000000000000{i:02d}", "page_id": page_id, "page_name": pagina, "ad_delivery_start_time": inicio,
         "publisher_platforms": ["facebook", "instagram"], "ad_creative_bodies": [texto],
         "ad_snapshot_url": f"https://www.facebook.com/ads/library/?id=9000000000000{i:02d}"}
    if fin:
        d["ad_delivery_stop_time"] = fin
    return d


@pytest.fixture
def sin_token(monkeypatch):
    for k in ("META_ADLIBRARY_TOKEN", "META_ACCESS_TOKEN", "META_ADLIBRARY_TOKEN_ACME", "META_ACCESS_TOKEN_ACME"):
        monkeypatch.delenv(k, raising=False)


@pytest.fixture
def api(instancia, monkeypatch):
    """Ad Library simulada: devuelve las páginas en orden y guarda las llamadas (sin red).

    Depende de `instancia` para parchear `_comun` después de que la fixture lo recargue."""
    llamadas = []

    def falso(url, params=None, **kw):
        llamadas.append((url, dict(params or {})))
        return respuestas.pop(0)

    respuestas: list[dict] = []
    monkeypatch.setattr(_comun, "get_json", falso)
    monkeypatch.setenv("META_ADLIBRARY_TOKEN", "token-falso")
    return llamadas, respuestas


def test_normalizar_campos_de_api_y_de_mcp():
    api = ad_library.normalizar(_ad(1), HOY)
    assert api["ad_id"] == "900000000000001" and api["dias_activo"] == 69 and api["plataformas"] == "facebook,instagram"
    mcp = ad_library.normalizar({"adArchiveID": 42, "pageName": "Nimbo", "startDate": 1759276800,
                                 "body": {"text": "Hola\n  mundo"}, "publisherPlatform": "FACEBOOK"}, HOY)
    assert (mcp["ad_id"], mcp["page_name"], mcp["inicio"], mcp["texto"], mcp["plataformas"]) == \
        ("42", "Nimbo", "2025-10-01", "Hola mundo", "facebook")
    assert ad_library.normalizar({}, HOY)["dias_activo"] == 0


def test_buscar_con_paginacion(instancia, api, capsys):
    llamadas, respuestas = api
    respuestas += [{"data": [_ad(1), _ad(2)], "paging": {"next": "https://graph.example/next?access_token=x"}},
                   {"data": [_ad(3, texto="Automatiza tu atención al cliente con IA")]}]
    assert ad_library.main(["buscar", "--buscar", "automatización con IA", "--paises", "es,fr", "--cliente", "acme",
                            "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["anuncios"] == 3 and len(llamadas) == 2
    url, params = llamadas[0]
    assert url.endswith("/ads_archive") and params["ad_reached_countries"] == '["ES", "FR"]'
    assert params["search_type"] == "KEYWORD_UNORDERED" and params["access_token"] == "token-falso"
    assert "×3" in r["resumen"] and "| Competidor A | 3 |" in r["resumen"]
    carpeta = instancia / "clientes" / "acme" / "investigacion" / "ad-library"
    csvs = list(carpeta.glob("*/anuncios.csv"))
    assert len(csvs) == 1 and "angulo,concepto,hook" in csvs[0].read_text(encoding="utf-8")
    assert "token-falso" not in json.dumps(r)


def test_buscar_forma_antigua_y_maximo(instancia, api, capsys):
    llamadas, respuestas = api
    respuestas += [{"data": [_ad(i) for i in range(5)], "paging": {"next": "https://graph.example/next"}}]
    assert ad_library.main(["--page-ids", "111111111111111", "--max", "3", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["anuncios"] == 3 and len(llamadas) == 1 and r["guardado"] == []
    assert llamadas[0][1]["search_page_ids"] == '["111111111111111"]'


def test_buscar_errores(instancia, sin_token, monkeypatch, capsys):
    assert ad_library.main(["buscar", "--buscar", "x"]) == 2
    assert "META_ADLIBRARY_TOKEN" in capsys.readouterr().err
    assert ad_library.main(["buscar"]) == 1
    monkeypatch.setenv("META_ADLIBRARY_TOKEN", "token-falso")
    assert ad_library.main(["buscar", "--buscar", "x", "--cliente", "nadie"]) == 1

    def roto(*a, **k):
        raise RuntimeError("HTTP 400: Application does not have permission")
    monkeypatch.setattr(_comun, "get_json", roto)
    assert ad_library.main(["buscar", "--buscar", "x"]) == 1
    assert "identidad no confirmada" in capsys.readouterr().err


def test_vigilar_crea_plantilla(instancia, sin_token, capsys):
    assert ad_library.main(["vigilar", "--cliente", "acme"]) == 1
    lista = instancia / "clientes" / "acme" / "investigacion" / "vigilancia" / "competidores.txt"
    assert lista.exists() and "competidores.txt" in capsys.readouterr().err
    assert ad_library.leer_competidores(lista) == ([], [])  # la plantilla solo trae comentarios


def test_leer_competidores(tmp_path):
    f = tmp_path / "c.txt"
    f.write_text("# comentario\n111111111111111  # Competidor A\nbuscar: automatización con IA\nBuscar:chatbots\n"
                 "no-es-un-id\n\n", encoding="utf-8")
    assert ad_library.leer_competidores(f) == (["111111111111111"], ["automatización con IA", "chatbots"])


def test_vigilar_con_entrada_y_diferencias(instancia, sin_token, tmp_path, capsys):
    s1 = tmp_path / "s1.json"
    s1.write_text(json.dumps({"data": [_ad(1), _ad(2), _ad(3, pagina="Nimbo", page_id="222222222222222"),
                                       _ad(9, fin="2026-10-01")]}), encoding="utf-8")
    assert ad_library.main(["vigilar", "--cliente", "acme", "--entrada", str(s1), "--fecha", "2026-11-02",
                            "--json"]) == 0
    r1 = json.loads(capsys.readouterr().out)
    assert r1["activos"] == 3 and r1["foto_anterior"] is None and "primera foto" in r1["informe"]
    s2 = tmp_path / "s2.json"
    s2.write_text(json.dumps([_ad(2), _ad(3, pagina="Nimbo", page_id="222222222222222"), _ad(4), _ad(4)]),
                  encoding="utf-8")
    assert ad_library.main(["vigilar", "--cliente", "acme", "--entrada", str(s2), "--fecha", "2026-11-09",
                            "--json"]) == 0
    r2 = json.loads(capsys.readouterr().out)
    assert (r2["foto_anterior"], r2["activos"], r2["nuevos"], r2["retirados"]) == ("2026-11-02", 3, 1, 1)
    assert r2["por_pagina"]["Competidor A"] == {"antes": 2, "ahora": 2, "nuevos": 1, "retirados": 1}
    carpeta = instancia / "clientes" / "acme" / "investigacion" / "vigilancia"
    assert sorted(p.name for p in carpeta.iterdir()) == ["2026-11-02.json", "2026-11-02.md", "2026-11-09.json",
                                                         "2026-11-09.md"]
    md = (carpeta / "2026-11-09.md").read_text(encoding="utf-8")
    assert "## Nuevos desde 2026-11-02 (1)" in md and "dato, no instrucciones" in md
    assert r2["guardado"] == ["clientes/acme/investigacion/vigilancia/2026-11-09.json",
                              "clientes/acme/investigacion/vigilancia/2026-11-09.md"]


def test_vigilar_con_api_agrupa_paginas(instancia, api, capsys):
    llamadas, respuestas = api
    lista = instancia / "clientes" / "acme" / "investigacion" / "vigilancia" / "competidores.txt"
    lista.parent.mkdir(parents=True)
    ids = [f"1111111111111{i:02d}" for i in range(12)]
    lista.write_text("\n".join(ids) + "\nbuscar: chatbots para clínicas\n", encoding="utf-8")
    respuestas += [{"data": [_ad(1)]}, {"data": [_ad(2)]}, {"data": [_ad(1), _ad(5)]}]
    assert ad_library.main(["vigilar", "--cliente", "acme", "--fecha", "2026-11-09", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert len(llamadas) == 3 and r["activos"] == 3  # 10 + 2 páginas y una búsqueda; el repetido cuenta una vez
    assert len(json.loads(llamadas[0][1]["search_page_ids"])) == 10
    assert llamadas[2][1]["search_terms"] == "chatbots para clínicas"


@pytest.mark.parametrize("contenido,trozo", [("{roto", "no es JSON"), ('{"data": 5}', "lista de anuncios")])
def test_vigilar_entrada_mala(instancia, sin_token, tmp_path, capsys, contenido, trozo):
    f = tmp_path / "x.json"
    f.write_text(contenido, encoding="utf-8")
    assert ad_library.main(["vigilar", "--cliente", "acme", "--entrada", str(f)]) == 1
    assert trozo in capsys.readouterr().err


def test_vigilar_errores(instancia, sin_token, tmp_path):
    assert ad_library.main(["vigilar", "--cliente", "acme", "--entrada", str(tmp_path / "no.json")]) == 1
    assert ad_library.main(["vigilar", "--cliente", "nadie", "--page-ids", "111111111111111"]) == 1
    assert ad_library.main(["vigilar", "--cliente", "acme", "--page-ids", "111111111111111"]) == 2  # sin token
    assert ad_library.main(["vigilar", "--cliente", "acme", "--fecha", "9/11/2026", "--page-ids", "1"]) == 1
    assert ad_library.main(["vigilar", "--cliente", "Mal Slug", "--page-ids", "1"]) == 2
