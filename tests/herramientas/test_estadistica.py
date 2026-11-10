import json
import math

import pytest

import estadistica as e


def test_ic_poisson_valores_de_referencia():
    lo, hi = e.ic_poisson(0)
    assert lo == 0 and hi == pytest.approx(3.689, abs=1e-3)
    lo, hi = e.ic_poisson(30)
    assert lo == pytest.approx(20.24, abs=0.01) and hi == pytest.approx(42.83, abs=0.01)
    lo, hi = e.ic_poisson(1000)  # Wilson-Hilferty frente al Garwood exacto (938,973 – 1063,952)
    assert lo == pytest.approx(938.973, abs=0.01) and hi == pytest.approx(1063.952, abs=0.01)


def test_cdf_y_cuantil():
    assert e.cdf(0, 2) == pytest.approx(math.exp(-2))
    assert e.cdf(-1, 2) == 0 and e.cdf(3, 0) == 1
    assert e.cdf(5000, 5000) == pytest.approx(0.5038, abs=1e-3)  # sin desbordar
    assert e.cuantil(20, 0.025) == 12 and e.cuantil(20, 0.975) == 29
    assert e.cuantil(0, 0.5) == 0


def test_ic_cpa():
    d, t = e.ic_cpa(3000, 30)
    assert d["cpa"] == 100 and d["ruidoso"] is False
    assert d["ic95_cpa"][0] == pytest.approx(3000 / 42.83, abs=0.05)
    assert d["ic95_cpa"][1] == pytest.approx(3000 / 20.24, abs=0.1)
    d, t = e.ic_cpa(500, 0)
    assert d["cpa"] is None and d["ic95_cpa"][1] is None and "≥" in t[0] and d["ruidoso"] is True


def test_kill():
    d, _ = e.kill(40, 120)
    assert d["veces_cpa"] == 3 and d["p_cero"] == pytest.approx(0.0498, abs=1e-4)
    assert d["p_max_una"] == pytest.approx(4 * math.exp(-3))


def test_comparar():
    d, _ = e.comparar(500, 12, 500, 20)
    assert d["real"] is False and d["veredicto"] == "no distinguible del ruido"
    d, _ = e.comparar(500, 10, 500, 40)
    assert d["real"] is True and d["p_valor"] < 0.001 and d["ratio_tasas"] == pytest.approx(0.25)
    d, _ = e.comparar(50000, 4000, 50000, 4200)  # miles de conversiones: antes desbordaba
    assert 0 < d["p_valor"] < 1
    d, t = e.comparar(500, 0, 500, 0)
    assert d["veredicto"] == "sin datos"
    d, t = e.comparar(500, 0, 500, 8)
    assert d["cpa_a"] is None and "∞" in t[0] and d["real"] is True


def test_potencia_y_detectable():
    d, _ = e.potencia(0.2, 0.8)
    assert d["conversiones_por_brazo"] == math.ceil(2 * (1.959964 + 0.841621) ** 2 / math.log(1.2) ** 2)
    assert list(d["tabla"]) == ["10%", "20%", "30%", "50%", "100%", "200%"]
    d, _ = e.detectable(d["conversiones_por_brazo"], 0.8)
    assert d["diferencia_minima"] == pytest.approx(0.2, abs=0.005)


def test_banda_con_observado():
    d, t = e.banda(20)
    assert (d["bajo"], d["alto"]) == (12, 29) and "observado" not in d
    d, t = e.banda(20, 9)
    assert d["estado"] == "por debajo" and d["p_cola"] == pytest.approx(e.cdf(9, 20)) and "revisa" in t[1]
    d, _ = e.banda(20, 35)
    assert d["estado"] == "por encima" and d["p_cola"] == pytest.approx(1 - e.cdf(34, 20))
    d, t = e.banda(20, 18)
    assert d["estado"] == "dentro" and d["p_cola"] is None and "ruido normal" in t[1]
    d, _ = e.banda(3, 0)
    assert d["estado"] == "dentro"  # con media 3, un día a 0 es normal


def test_lag():
    d, t = e.lag(80, 100, 50)
    assert d["ratio_maduracion"] == 1.25 and d["cpa_estimado"] == 40
    assert "cpa_estimado" not in e.lag(80, 100, None)[0]


def test_identicos_monotono_y_exacto():
    p = [e.identicos(n, 0.3)[0]["probabilidad"] for n in (5, 10, 30, 100, 1000)]
    assert all(a > b for a, b in zip(p, p[1:]))
    assert p[0] > 0.5 and p[-1] < 0.001
    assert e.identicos(10, 0.3)[0]["probabilidad"] == e.identicos(10, 0.3)[0]["probabilidad"]  # determinista


def test_main_json_para_todos(capsys):
    casos = [["ic-cpa", "--gasto", "3000", "--conversiones", "30"], ["kill", "--cpa-objetivo", "40", "--gasto", "100"],
             ["comparar", "--gasto-a", "500", "--conv-a", "12", "--gasto-b", "500", "--conv-b", "20"],
             ["potencia", "--diferencia", "0.2"], ["detectable", "--conversiones", "50"],
             ["banda", "--media", "20", "--observado", "9"], ["lag", "--conv-1d", "80", "--conv-7d", "100"],
             ["identicos", "--conversiones", "10"]]
    for c in casos:
        assert e.main([*c, "--json"]) == 0
        assert isinstance(json.loads(capsys.readouterr().out), dict)
        assert e.main(c) == 0
        assert capsys.readouterr().out.strip()


@pytest.mark.parametrize("argv", [
    ["ic-cpa", "--gasto", "0", "--conversiones", "3"], ["ic-cpa", "--gasto", "100", "--conversiones", "-1"],
    ["kill", "--cpa-objetivo", "0", "--gasto", "100"], ["potencia", "--diferencia", "0.2", "--potencia", "80"],
    ["detectable", "--conversiones", "0"], ["banda", "--media", "-2"], ["banda", "--media", "2", "--observado", "-1"],
    ["lag", "--conv-1d", "0", "--conv-7d", "10"], ["identicos", "--conversiones", "50000"],
])
def test_validacion_sale_con_1(argv, capsys):
    assert e.main(argv) == 1
    assert capsys.readouterr().err.startswith("Error:")


def test_argumentos_mal_escritos_salen_con_1():
    with pytest.raises(SystemExit) as x:
        e.main(["ic-cpa", "--gasto", "mil", "--conversiones", "3"])
    assert x.value.code == 1
