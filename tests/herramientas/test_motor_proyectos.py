import json
import sqlite3

import pytest

import motor_proyectos as mp


def _db(ruta):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(ruta)
    c.executescript("""
        CREATE TABLE docs (kind TEXT, id TEXT, json TEXT, updated_at REAL, PRIMARY KEY (kind, id));
        CREATE TABLE costs (id TEXT PRIMARY KEY, project_id TEXT, usd REAL);
    """)
    docs = [
        ("brand", "b1", {"name": "Acme Automations"}),
        ("brand", "b2", {"name": "Nimbo"}),
        ("project", "p1", {"name": "Demo antes/después", "status": "done", "brief": {"brand_id": "b1"},
                           "variant_spec": {"estimated_cost_usd": 4.5}}),
        ("project", "p2", {"name": "Hook nuevo", "status": "paused_billing", "brief": {"brand_id": "b1"},
                           "parent_id": "p1"}),
        ("project", "p3", {"name": "Testimonio", "status": "done", "brief": {"brand_id": "b2"}}),
    ]
    for i, (kind, id_, d) in enumerate(docs):
        c.execute("insert into docs values (?, ?, ?, ?)", (kind, id_, json.dumps(d), 1_790_000_000 + i * 60))
    c.execute("insert into docs values ('project', 'roto', '{no json', 1)")
    c.executemany("insert into costs values (?, ?, ?)", [("c1", "p1", 1.234), ("c2", "p1", 2.0), ("c3", "p3", 0.5)])
    c.commit()
    c.close()


@pytest.fixture
def motor(instancia, monkeypatch):
    monkeypatch.delenv("MOTOR_DATA_DIR", raising=False)
    db = instancia / "modulos" / "motor-ia" / "data" / "motor.sqlite3"
    _db(db)
    return db


def test_ruta_db(instancia, monkeypatch, tmp_path):
    monkeypatch.delenv("MOTOR_DATA_DIR", raising=False)
    assert mp.ruta_db() == instancia / "modulos" / "motor-ia" / "data" / "motor.sqlite3"
    monkeypatch.setenv("MOTOR_DATA_DIR", "otra")
    assert mp.ruta_db() == instancia / "modulos" / "motor-ia" / "otra" / "motor.sqlite3"
    monkeypatch.setenv("MOTOR_DATA_DIR", str(tmp_path / "abs"))
    assert mp.ruta_db() == tmp_path / "abs" / "motor.sqlite3"


def test_proyectos(motor):
    filas = mp.proyectos(motor)
    assert [f["proyecto"] for f in filas] == ["p3", "p2", "p1"]  # el más reciente primero; el roto se salta
    p1 = filas[-1]
    assert p1["marca"] == "Acme Automations" and p1["coste_real_usd"] == 3.23 and p1["estimado_usd"] == 4.5
    assert filas[1]["variante_de"] == "p1" and filas[1]["coste_real_usd"] is None
    assert [f["proyecto"] for f in mp.proyectos(motor, marca="Acme Automations")] == ["p2", "p1"]
    assert [f["proyecto"] for f in mp.proyectos(motor, marca="b2")] == ["p3"]
    assert [f["proyecto"] for f in mp.proyectos(motor, estado="paused_billing")] == ["p2"]


def test_solo_lectura(motor):
    antes = motor.read_bytes()
    mp.proyectos(motor)
    assert motor.read_bytes() == antes
    with pytest.raises(sqlite3.OperationalError):
        c = sqlite3.connect(f"file:{motor.as_posix()}?mode=ro", uri=True)
        c.execute("insert into costs values ('x', 'p1', 1)")


def test_main(motor, capsys):
    assert mp.main(["--json", "--max", "2"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 2
    assert mp.main([]) == 0
    out = capsys.readouterr().out
    assert "| p1 | Demo antes/después | done | Acme Automations |  | 3.23 | 4.50 |" in out
    assert "3 proyectos · coste real total 3.73 $" in out and "modulos/motor-ia motor costs" in out


def test_sin_motor_sale_con_2(instancia, monkeypatch, capsys):
    monkeypatch.delenv("MOTOR_DATA_DIR", raising=False)
    assert mp.main([]) == 2
    assert "/motor instalar" in capsys.readouterr().err


def test_base_rota_sale_con_2(instancia, monkeypatch, capsys):
    monkeypatch.delenv("MOTOR_DATA_DIR", raising=False)
    db = instancia / "modulos" / "motor-ia" / "data" / "motor.sqlite3"
    db.parent.mkdir(parents=True)
    db.write_bytes(b"esto no es sqlite" * 100)
    assert mp.main([]) == 2
    assert "No se pudo leer" in capsys.readouterr().err
