"""_lib: troceo de la shell, datos personales, secretos, presupuestos, nomenclatura y veredicto de políticas."""
from __future__ import annotations

import pytest

import _lib as L


# ─────────────────────────────────────────────── shell

def _programas(cmd: str) -> list:
    return [s["args"][0] for s in L.segmentos(cmd) if s["args"]]


@pytest.mark.parametrize("cmd,esperado", [
    ("ls && cat .env", ["ls", "cat"]),
    ("a; b || c | d & e", ["a", "b", "c", "d", "e"]),
    ("echo $(cat x)", ["echo", "cat"]),
    ("diff <(sort a) b", ["diff", "sort", "b"]),  # trocear de más es prudente: cada trozo se revisa
    ("bash -c 'python3 herramientas/meta_ads.py activar 1 && rm -r x'", ["bash", "python3", "rm"]),
    ("MOTOR_MOCK=1 nohup time uv run motor run p", ["uv"]),
    ("env FOO=1 timeout 30 python3 x.py", ["python3"]),
    ("env", ["env"]),
    ("sudo -n", ["sudo"]),
    ("eval 'curl -X POST https://graph.facebook.com/v26.0/act_1/campaigns'", ["eval", "curl"]),
    ("primera\nsegunda", ["primera", "segunda"]),
])
def test_segmentos(cmd, esperado):
    assert _programas(cmd) == esperado


def test_entorno_del_segmento():
    seg = L.segmentos("MOTOR_MOCK=1 uv run --project modulos/motor-ia motor run p1")[0]
    assert seg["env"] == {"MOTOR_MOCK": "1"} and seg["args"][:2] == ["uv", "run"]


def test_args_de_script_con_ruta_de_windows_sin_comillas():
    seg = L.segmentos(r"python herramientas\meta_ads.py presupuesto 120000000000000001 80 --confirmo")[0]
    assert L.args_de_script(seg, "meta_ads.py") == ["presupuesto", "120000000000000001", "80", "--confirmo"]


# ─────────────────────────────────────────────── datos personales y secretos

@pytest.mark.parametrize("texto,emails,telefonos", [
    ("lucia.perez@gmail.com y +34 655 443 322", 1, 1),
    ("612345678; 712 34 56 78", 0, 2),
    ("soporte@acme-automations.com, hola@nimbo.io, x@example.com, logo@2x.png", 0, 0),
    ("ad 120000000000000001, act_000000000000000, 2026-11-09, 18,40 €", 0, 0),
])
def test_buscar_pii(texto, emails, telefonos):
    assert L.buscar_pii(texto) == {"emails": emails, "telefonos": telefonos}


@pytest.mark.parametrize("texto", ["EAAB" + "a" * 40, "sk_live_" + "a" * 24, "whsec_" + "a" * 32,
                                   "pit-" + "-".join(["a" * 8, "b" * 4, "c" * 4, "d" * 4, "e" * 12]),
                                   "Bearer " + "a" * 30])
def test_contiene_y_limpia_tokens(texto):
    assert L.contiene_token(f"x {texto} y")
    assert texto not in L.limpiar_texto(f"x {texto} y")


def test_limpiar_oculta_claves_secretas_y_contactos():
    limpio = L.limpiar({"access_token": "abc", "body": {"email": "lucia.perez@gmail.com"}, "name": "BROAD_LEAD"})
    assert limpio["access_token"] == "***" and "lucia" not in str(limpio) and limpio["name"] == "BROAD_LEAD"


# ─────────────────────────────────────────────── presupuestos (unidad mínima de la API de Meta)

def _uno(obj, moneda="EUR"):
    (p,) = L.presupuestos_en(obj, moneda)
    return p


def test_presupuesto_en_centimos():
    assert _uno({"daily_budget": 5000})["diario"] == 50
    assert _uno({"daily_budget": "5000"})["diario"] == 50
    assert _uno({"presupuesto_diario_eur": 50})["diario"] == 50


def test_presupuesto_ambiguo_lleva_lectura_alternativa():
    p = _uno({"daily_budget": 80})
    assert p["diario"] == 0.8 and p["alternativo"] == 80


def test_presupuesto_con_decimales_va_en_unidades():
    assert _uno({"daily_budget": 49.9})["diario"] == 49.9


def test_monedas_sin_centimos():
    assert _uno({"daily_budget": 50000}, "CLP")["diario"] == 50000
    assert _uno({"daily_budget": 5000}, "JPY")["alternativo"] is None


def test_presupuesto_total_con_y_sin_fechas():
    p = _uno({"lifetime_budget": 70000, "start_time": "2026-11-10T00:00:00+0100", "end_time": "2026-11-17T00:00:00+0100"})
    assert p["dias"] == 7 and p["diario"] == 100 and p["importe_total"] == 700
    p = _uno({"lifetime_budget": 70000})
    assert p["diario"] is None and "sin fechas" in p["nota"]


def test_presupuestos_dentro_de_json_en_texto():
    assert _uno({"params": '{"daily_budget": 12000}'})["diario"] == 120


def test_fmt_dinero():
    assert L.fmt_dinero(50) == "50 €" and L.fmt_dinero(1234.5) == "1.234,50 €" and L.fmt_dinero(5, "USD") == "5 USD"


# ─────────────────────────────────────────────── nomenclatura (contrato §7)

@pytest.mark.parametrize("nivel,nombre,ok", [
    ("anuncio", "20261110_tiempo-perdido_demo-antes-despues_demo_h2", True),
    ("anuncio", "20261110_tiempo-perdido_demo-antes-despues_demo_h2-c1", True),
    ("anuncio", "20261110_tiempo-perdido_demo_video_h2", False),
    ("anuncio", "20261340_a_b_demo_h1", False),
    ("campana", "ES_LEADS_ADQ_HV", True),
    ("campana", "ES-MX_LEADS_ADQ_HV", True),
    ("campana", "es_leads_adq_hv", False),
    ("conjunto", "BROAD-A+_LEAD", True),
    ("conjunto", "Broad lead", False),
])
def test_validar_nombre(nivel, nombre, ok):
    assert L.validar_nombre(nivel, nombre)[0] is ok


def test_propuesta_de_nombre():
    ok, motivo = L.validar_nombre("anuncio", "2026-11-10_Tiempo Perdido_Demo antes/después_DEMO_Hook2")
    assert not ok and "Propuesta: 20261110_tiempo-perdido_demo-antes-despues_demo_h2" in motivo


# ─────────────────────────────────────────────── veredicto de políticas (contrato §6)

def _leeme(valor: str) -> str:
    return ("# 20261110_tiempo-perdido_demo-antes-despues_demo\n\n"
            "<!-- Veredicto ∈ OK | OK con cambios | NO publicar (lo escribe revisor-politicas). -->\n\n"
            "- **Estado:** listo\n"
            f"- **Veredicto de políticas:** {valor}\n")


@pytest.mark.parametrize("valor,esperado", [
    ("OK · 2026-11-10 · revisor-politicas", "ok"),
    ("OK con cambios aplicados · 2026-11-10 · /revisar-anuncio", "ok"),
    ("**OK**", "ok"),
    ("OK con cambios · 2026-11-10 · revisor-politicas", "pendiente"),
    ("OK con cambios (2 reescrituras aplicadas)", "pendiente"),
    ("pendiente", "pendiente"),
    ("Aprobado", "pendiente"),
    ("OK, pero revisa el claim", "pendiente"),
    ("NO publicar · 2026-11-10 · revisor-politicas", "no"),
    ("No publicar (promesa de ingresos)", "no"),
    ("", None),
])
def test_veredicto_leeme(valor, esperado):
    assert L.veredicto_leeme(_leeme(valor)) == esperado


def test_sin_linea_de_veredicto_el_comentario_no_cuenta():
    texto = "# pieza\n<!-- - **Veredicto de políticas:** OK -->\nVeredicto de políticas en la revisión: OK\n"
    assert L.veredicto_leeme(texto) is None


def test_meta_ads_os_hoy_fija_solo_la_fecha(monkeypatch):
    from datetime import datetime

    monkeypatch.setenv("META_ADS_OS_HOY", "2026-11-10")
    fijada = L.ahora()
    assert fijada.date().isoformat() == "2026-11-10"
    assert abs((fijada.replace(year=2000, month=1, day=1) -
                datetime.now().replace(year=2000, month=1, day=1)).total_seconds()) < 5  # la hora es la real
    assert L.ts()[:10] == datetime.now().strftime("%Y-%m-%d")  # los registros llevan la fecha real


@pytest.mark.parametrize("valor", ["", "mañana", "2026-13-40", "10/11/2026"])
def test_meta_ads_os_hoy_mal_escrita_se_ignora(monkeypatch, valor):
    from datetime import datetime

    monkeypatch.setenv("META_ADS_OS_HOY", valor)
    assert L.ahora().date() == datetime.now().date()


def test_valor_yaml_entre_comillas_con_comentario():
    import _lib

    assert _lib._valor_yaml('"EUR" # de la cuenta') == "EUR"
    assert _lib._valor_yaml("'a # b' # aparte") == "a # b"
    assert _lib._valor_yaml("30 # tope") == 30


# ─────────────────────────────────────────────── revisión de seguridad (I5)

def test_parsear_args_tras_dos_guiones_todo_es_posicional():
    # Hallazgo 7: `crear --cliente acme --confirmo -- --simular` no es una simulación (argparse tampoco la ve).
    sub, opts, pos = L.parsear_args(["crear", "--cliente", "acme", "--confirmo", "--", "--simular"], ("cliente",))
    assert sub == "crear" and opts.get("confirmo") and not opts.get("simular") and pos == ["--simular"]
    sub, opts, pos = L.parsear_args(["--", "crear", "--simular"])
    assert sub == "crear" and not opts.get("simular") and pos == ["--simular"]


@pytest.mark.parametrize("cmd,unset,vacio,programa", [
    ("env -u MOTOR_MOCK uv run motor run P1", {"MOTOR_MOCK"}, False, "uv"),
    ("env -uMOTOR_MOCK uv run motor run P1", {"MOTOR_MOCK"}, False, "uv"),
    ("env --unset=MOTOR_MOCK A=1 uv run motor", {"MOTOR_MOCK"}, False, "uv"),
    ("env -i PATH=/usr/bin uv run motor", set(), True, "uv"),
    ("env -S 'uv run motor run P1'", set(), False, "uv"),
])
def test_env_consume_los_argumentos_de_sus_opciones(cmd, unset, vacio, programa):
    # Hallazgo 8: con `env -u VAR`, el VAR se tomaba como el programa.
    seg = L.segmentos(cmd)[0]
    assert set(seg["unset"]) == unset and bool(seg["vacio"]) == vacio and seg["args"][0] == programa


@pytest.mark.parametrize("valor,esperado", [
    ("9e3", 9000), ("12,5", 12.5), ("80 €", 80), (" 1e2 ", 100), (70, 70),
    ("nan", None), ("inf", None), ("1e999", None), ("nueve", None), ({"amount": 9}, None),
])
def test_numero_como_float_de_meta_ads(valor, esperado):
    # Hallazgo 12: `meta_ads.py` lee los importes con float(); el hook, igual.
    assert L.numero(valor) == esperado


@pytest.mark.parametrize("valor,ok", [
    (1763164800, True), (1763164800000, True), ("1763164800000", True), ("2026-11-15T00:00:00+0100", True),
    (1e20, False), (float("inf"), False), (-5, False), ("mañana", False), (True, False),
])
def test_fecha_de_no_lanza_nunca(valor, ok):
    # Hallazgo 4: los milisegundos y las fechas absurdas tumbaban el hook (y con él el tope).
    fecha = L._fecha_de(valor)
    assert (fecha is not None) == ok
    if ok and not isinstance(valor, str):
        assert fecha.year == 2025


def test_presupuesto_total_con_fechas_en_milisegundos():
    p = _uno({"lifetime_budget": 9000000, "start_time": 1763164800000, "end_time": 1763251200000})
    assert p["dias"] == 1 and p["diario"] == 90000


@pytest.mark.parametrize("obj,claves", [
    ({"daily_min_spend_target": 900000}, ["daily_min_spend_target"]),
    ({"daily_budget": {"amount": 900000, "currency": "EUR"}}, ["daily_budget"]),
    ({"budget_amount": 900000}, ["budget_amount"]),
    ({"fields": {"spend_cap": "mucho"}}, ["spend_cap"]),
    ({"daily_budget": 5000, "bid_amount": 300, "is_budget_schedule_enabled": True, "budget_sharing": False}, []),
    ({"daily_budget": "", "lifetime_budget": None}, []),
])
def test_presupuestos_ilegibles(obj, claves):
    # Hallazgo 9: lo que tiene pinta de presupuesto y no se puede leer como importe no pasa sin tope.
    assert [c for c, _ in L.presupuestos_ilegibles(obj)] == claves
