"""datos_personales: emails, teléfonos y listas de personas fuera de privado/ (RGPD)."""
from __future__ import annotations

from ayudas_hooks import decision, leer_log, motivo, pre_archivo


def _write(instancia, rel: str, contenido: str):
    return pre_archivo(instancia, "Write", {"file_path": str(instancia / rel), "content": contenido})


def test_agregados_y_ejemplos_pasan(instancia, correr):
    informe = "# Semana 45\n\n| Anuncio | Leads | CPL |\n|---|---|---|\n| 120000000000000001 | 12 | 18,40 |\n"
    assert correr("datos_personales", _write(instancia, "clientes/acme/informes/2026-W45.md", informe)) is None
    docs = "Escribe a soporte@acme-automations.com o a nombre@example.com. Cuenta act_000000000000000, 2026-11-09."
    assert correr("datos_personales", _write(instancia, "docs/guia.md", docs)) is None
    csv = "ad_id,nombre,fecha,leads\n120000000000000001,20261110_x_y_demo_h1,2026-11-10,4\n"
    assert correr("datos_personales", _write(instancia, "clientes/acme/registro-creativo.csv", csv)) is None


def test_privado_contexto_y_fuera_del_proyecto_no_se_revisan(instancia, correr, tmp_path):
    leads = "email,telefono\nlucia.perez@gmail.com,+34 655 443 322\nmarc.soler@hotmail.com,612 345 678\n"
    assert correr("datos_personales", _write(instancia, "clientes/acme/privado/leads-2026-11.csv", leads)) is None
    assert correr("datos_personales", _write(instancia, "contexto/operador.md", "Email: yo@miagencia.es")) is None
    fuera = pre_archivo(instancia, "Write", {"file_path": str(tmp_path / "otro" / "x.md"), "content": leads})
    assert correr("datos_personales", fuera) is None


def test_emails_y_telefonos_fuera_de_privado_preguntan(instancia, correr):
    salida = correr("datos_personales", _write(instancia, "clientes/acme/informes/leads.md",
                                               "- Lucía: lucia.perez@gmail.com, 655 44 33 22\n"))
    assert decision(salida) == "ask"
    assert "clientes/acme/privado/" in motivo(salida) and "lucia.perez" not in motivo(salida)


def test_edicion_y_multiedicion(instancia, correr):
    edit = pre_archivo(instancia, "Edit", {"file_path": str(instancia / "clientes/acme/ficha.md"),
                                           "old_string": "x", "new_string": "Contacto: +34 600 112 233"})
    assert decision(correr("datos_personales", edit)) == "ask"
    multi = pre_archivo(instancia, "MultiEdit", {"file_path": str(instancia / "clientes/acme/estado.md"),
                                                 "edits": [{"old_string": "a", "new_string": "b"},
                                                           {"old_string": "c", "new_string": "ana@empresa-real.es"}]})
    assert decision(correr("datos_personales", multi)) == "ask"


def test_tabla_con_columnas_personales(instancia, correr):
    tabla = "nombre_completo;dni;utm_content\nLucía Pérez;12345678Z;h1\nMarc Soler;87654321X;h2\n"
    salida = correr("datos_personales", _write(instancia, "clientes/acme/datos/cruce.csv", tabla))
    assert decision(salida) == "ask" and "columnas de datos personales" in motivo(salida)


def test_fallo_interno_deja_pasar(instancia, en_proceso, monkeypatch):
    import _lib

    def rota(texto):
        raise MemoryError("fallo simulado")

    monkeypatch.setattr(_lib, "buscar_pii", rota)
    codigo, salida = en_proceso("datos_personales", _write(instancia, "docs/x.md", "ana@example.com"))
    assert codigo == 0 and salida is None
    assert leer_log(instancia, "hooks.jsonl")[-1]["hook"] == "datos_personales"


# ─────────────────────────────── topes de gasto de la ficha (hallazgo 13 de la revisión de seguridad)

def _ficha(instancia):
    return instancia / "clientes" / "acme" / "ficha.md"


def test_editar_los_topes_pregunta(instancia, correr):
    actual = _ficha(instancia).read_text(encoding="utf-8")
    assert "cambio_dia: 100" in actual
    entrada = pre_archivo(instancia, "Edit", {"file_path": str(_ficha(instancia)), "old_string": "cambio_dia: 100",
                                              "new_string": "cambio_dia: 5000"})
    salida = correr("datos_personales", entrada)
    assert decision(salida) == "ask" and "«acme»" in motivo(salida) and "cambio_dia 100 → 5000" in motivo(salida)


def test_quitar_los_topes_con_texto_vacio_pregunta(instancia, correr):
    entrada = pre_archivo(instancia, "Edit", {"file_path": str(_ficha(instancia)),
                                              "old_string": "  total_dia: 300\n", "new_string": ""})
    salida = correr("datos_personales", entrada)
    assert decision(salida) == "ask" and "total_dia 300 → sin definir" in motivo(salida)


def test_reescribir_la_ficha_con_otros_topes_pregunta(instancia, correr):
    nuevo = _ficha(instancia).read_text(encoding="utf-8").replace("total_dia: 300", "total_dia: 3000")
    salida = correr("datos_personales", pre_archivo(instancia, "Write", {"file_path": str(_ficha(instancia)),
                                                                         "content": nuevo}))
    assert decision(salida) == "ask" and "total_dia 300 → 3000" in motivo(salida)


def test_multiedit_que_sube_y_baja_a_la_vez(instancia, correr):
    edits = [{"old_string": "cambio_dia: 100", "new_string": "cambio_dia: 80"},
             {"old_string": "cambio_dia: 80", "new_string": "cambio_dia: 900"}]
    salida = correr("datos_personales", pre_archivo(instancia, "MultiEdit", {"file_path": str(_ficha(instancia)),
                                                                             "edits": edits}))
    assert decision(salida) == "ask" and "cambio_dia 100 → 900" in motivo(salida)


def test_ficha_con_cabecera_rota_pregunta(instancia, correr):
    entrada = pre_archivo(instancia, "Edit", {"file_path": str(_ficha(instancia)), "old_string": "topes:\n",
                                              "new_string": "topes de gasto\n"})
    salida = correr("datos_personales", entrada)
    assert decision(salida) == "ask" and "cabecera inválida" in motivo(salida)


def test_editar_la_ficha_sin_tocar_los_topes_no_decide(instancia, correr):
    for entrada in ({"old_string": "estado: activo", "new_string": "estado: pausado"},
                    {"old_string": "cambio_dia: 100", "new_string": "cambio_dia: 100.0"},
                    {"old_string": "no está en la ficha", "new_string": "cambio_dia: 9000"}):
        salida = correr("datos_personales", pre_archivo(instancia, "Edit", {"file_path": str(_ficha(instancia)),
                                                                            **entrada}))
        assert salida is None, entrada


def test_ficha_nueva_con_topes_a_cero_no_decide(instancia, correr):
    from ayudas_hooks import ficha
    ruta = instancia / "clientes" / "nimbo" / "ficha.md"
    contenido = ficha("nimbo", "act_000000000000001", 0, 0)
    assert correr("datos_personales", pre_archivo(instancia, "Write", {"file_path": str(ruta),
                                                                       "content": contenido})) is None
    salida = correr("datos_personales", pre_archivo(instancia, "Write", {"file_path": str(ruta),
                                                                         "content": ficha("nimbo", "act_1", 50, 150)}))
    assert decision(salida) == "ask" and "cambio_dia sin definir → 50" in motivo(salida)


def test_topes_y_datos_personales_a_la_vez(instancia, correr):
    actual = _ficha(instancia).read_text(encoding="utf-8")
    nuevo = actual.replace("cambio_dia: 100", "cambio_dia: 200") + "\nContacto: lucia.perez@gmail.com\n"
    salida = correr("datos_personales", pre_archivo(instancia, "Write", {"file_path": str(_ficha(instancia)),
                                                                         "content": nuevo}))
    assert decision(salida) == "ask" and "cambio_dia 100 → 200" in motivo(salida) and "RGPD" in motivo(salida)


def test_fallo_al_comprobar_los_topes_pregunta(instancia, en_proceso, monkeypatch):
    import datos_personales

    def rota(*a):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(datos_personales, "decision_topes", rota)
    entrada = pre_archivo(instancia, "Edit", {"file_path": str(_ficha(instancia)), "old_string": "cambio_dia: 100",
                                              "new_string": "cambio_dia: 5000"})
    codigo, salida = en_proceso("datos_personales", entrada)
    assert codigo == 0 and decision(salida) == "ask" and "topes" in motivo(salida)
    otro = pre_archivo(instancia, "Write", {"file_path": str(instancia / "docs" / "x.md"), "content": "hola"})
    assert en_proceso("datos_personales", otro) == (0, None)
