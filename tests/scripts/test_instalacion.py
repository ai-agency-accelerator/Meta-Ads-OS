"""scripts/instalacion.py: estado de la instalación con el esquema de plantillas/contexto/instalacion.json."""
from __future__ import annotations

import json
import shutil

import instalacion
from apoyo_scripts import RAIZ_PRODUCTO


def _raiz(tmp_path):
    raiz = tmp_path / "os"
    (raiz / "plantillas" / "contexto").mkdir(parents=True)
    shutil.copy2(RAIZ_PRODUCTO / "plantillas" / "contexto" / "instalacion.json",
                 raiz / "plantillas" / "contexto" / "instalacion.json")
    (raiz / "pyproject.toml").write_text('[project]\nname = "x"\nversion = "1.2.3"\n', encoding="utf-8")
    return raiz


def _estado(raiz):
    return json.loads((raiz / "contexto" / "instalacion.json").read_text(encoding="utf-8"))


def test_plantilla_coherente_con_el_script():
    datos = json.loads((RAIZ_PRODUCTO / "plantillas" / "contexto" / "instalacion.json").read_text(encoding="utf-8"))
    assert tuple(datos["fases"]) == instalacion.FASES
    for fase in datos["fases"].values():
        assert fase["estado"] in instalacion.ESTADOS
        assert isinstance(fase["requerida"], bool)


def test_ver_sin_archivo(tmp_path, capsys):
    raiz = _raiz(tmp_path)
    assert instalacion.main(["--raiz", str(raiz), "ver", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["existe"] is False and r["completa"] is False


def test_preparar_marca_tecnica_y_version(tmp_path):
    raiz = _raiz(tmp_path)
    assert instalacion.main(["--raiz", str(raiz), "preparar", "--sistema", '{"so": "linux", "uv": "0.9"}']) == 0
    e = _estado(raiz)
    assert e["fases"]["tecnica"]["estado"] == "hecho"
    assert e["sistema"]["so"] == "linux" and e["producto"]["version"] == "1.2.3"
    assert e["iniciado"] and e["actualizado"]


def test_completa_cuando_las_requeridas_estan_hechas_u_omitidas(tmp_path, capsys):
    raiz = _raiz(tmp_path)
    instalacion.main(["--raiz", str(raiz), "preparar"])
    for fase in ("perfil", "cliente", "entregable"):
        instalacion.main(["--raiz", str(raiz), "marcar", fase, "hecho"])
    instalacion.main(["--raiz", str(raiz), "marcar", "meta", "omitido", "--detalle", "sin cuenta publicitaria"])
    capsys.readouterr()
    instalacion.main(["--raiz", str(raiz), "ver", "--json"])
    r = json.loads(capsys.readouterr().out)
    assert r["completa"] is True
    assert "brief" in r["opcionales_pendientes"]


def test_marcar_con_datos_propios_de_la_fase(tmp_path):
    raiz = _raiz(tmp_path)
    assert instalacion.main(["--raiz", str(raiz), "marcar", "cliente", "hecho", "--dato", "slug=acme"]) == 0
    assert _estado(raiz)["fases"]["cliente"]["slug"] == "acme"
    assert instalacion.main(["--raiz", str(raiz), "marcar", "cliente", "hecho", "--dato", "estado=x"]) == 1
    assert instalacion.main(["--raiz", str(raiz), "marcar", "cliente", "regular"]) == 1


def test_conserva_lo_existente_y_anade_claves_nuevas(tmp_path):
    raiz = _raiz(tmp_path)
    (raiz / "contexto").mkdir()
    (raiz / "contexto" / "instalacion.json").write_text(json.dumps(
        {"esquema": 1, "fases": {"perfil": {"estado": "hecho", "requerida": True, "fecha": "2026-11-01",
                                             "detalle": "propio"}}, "pausa": None}), encoding="utf-8")
    instalacion.main(["--raiz", str(raiz), "preparar"])
    e = _estado(raiz)
    assert e["fases"]["perfil"]["detalle"] == "propio"
    assert set(instalacion.FASES) <= set(e["fases"])


def test_marcar_hecha_la_fase_en_pausa_la_quita(tmp_path):
    raiz = _raiz(tmp_path)
    instalacion.main(["--raiz", str(raiz), "preparar"])
    e = _estado(raiz)
    e["pausa"] = {"fecha": "2026-11-09", "fase": "meta", "motivo": "sin tiempo"}
    (raiz / "contexto" / "instalacion.json").write_text(json.dumps(e), encoding="utf-8")
    instalacion.main(["--raiz", str(raiz), "marcar", "meta", "hecho"])
    assert _estado(raiz)["pausa"] is None


def test_pausar_y_reanudar(tmp_path, capsys):
    raiz = _raiz(tmp_path)
    instalacion.main(["--raiz", str(raiz), "preparar"])
    instalacion.main(["--raiz", str(raiz), "marcar", "perfil", "hecho"])
    capsys.readouterr()
    assert instalacion.main(["--raiz", str(raiz), "pausar", "--motivo", "sin tiempo", "--json"]) == 0
    pausa = json.loads(capsys.readouterr().out)["pausa"]
    assert pausa["fase"] == "meta" and pausa["motivo"] == "sin tiempo" and pausa["fecha"]
    assert _estado(raiz)["fases"]["meta"]["estado"] == "pendiente"   # pausar no cambia el estado de la fase
    instalacion.main(["--raiz", str(raiz), "ver"])
    assert "En pausa desde" in capsys.readouterr().out

    assert instalacion.main(["--raiz", str(raiz), "reanudar", "--json"]) == 0
    r = json.loads(capsys.readouterr().out)
    assert r["fase"] == "meta" and r["pausa_anterior"]["motivo"] == "sin tiempo"
    assert _estado(raiz)["pausa"] is None


def test_pausar_fase_concreta_y_reanudar_si_ya_esta_hecha(tmp_path, capsys):
    raiz = _raiz(tmp_path)
    instalacion.main(["--raiz", str(raiz), "pausar", "brief"])
    instalacion.main(["--raiz", str(raiz), "marcar", "brief", "en_curso"])
    assert _estado(raiz)["pausa"]["fase"] == "brief"
    e = _estado(raiz)
    e["fases"]["brief"]["estado"] = "hecho"          # terminada por otra vía: reanudar sigue por la siguiente
    (raiz / "contexto" / "instalacion.json").write_text(json.dumps(e), encoding="utf-8")
    capsys.readouterr()
    instalacion.main(["--raiz", str(raiz), "reanudar", "--json"])
    assert json.loads(capsys.readouterr().out)["fase"] == "tecnica"


def test_pausar_sin_nada_pendiente_pide_la_fase(tmp_path):
    raiz = _raiz(tmp_path)
    for fase in instalacion.FASES:
        instalacion.main(["--raiz", str(raiz), "marcar", fase, "hecho"])
    assert instalacion.main(["--raiz", str(raiz), "pausar"]) == 1
    assert instalacion.main(["--raiz", str(raiz), "pausar", "motor"]) == 0


def test_json_danado_sin_crear_da_error_de_configuracion(tmp_path, capsys):
    raiz = _raiz(tmp_path)
    (raiz / "contexto").mkdir()
    (raiz / "contexto" / "instalacion.json").write_text("[]", encoding="utf-8")
    assert instalacion.main(["--raiz", str(raiz), "ver"]) == 2
