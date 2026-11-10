"""`MOTOR_MOCK=1 motor status` en el entorno del motor: funciona, muestra el presupuesto y nunca imprime claves."""
from __future__ import annotations

from motor_ia_apoyo import entorno_limpio

SECRETO = "clave-de-prueba-0123456789-no-debe-salir"


def _status(uv_motor, tmp_path, prefs: str | None = None, env_file: str = ""):
    raiz = tmp_path / "os"
    (raiz / "contexto").mkdir(parents=True)
    (raiz / ".env").write_text(f"GEMINI_API_KEY={SECRETO}\n{env_file}", encoding="utf-8")
    if prefs:
        (raiz / "contexto" / "preferencias.md").write_text(prefs, encoding="utf-8")
    env = entorno_limpio(MOTOR_MOCK="1", META_ADS_OS_RAIZ=str(raiz), MOTOR_DATA_DIR=str(tmp_path / "data"),
                         COLUMNS="200")
    return uv_motor(["motor", "status"], env)


def test_status_simulado_5_dolares_sin_imprimir_claves(uv_motor, tmp_path):
    p = _status(uv_motor, tmp_path)
    assert p.returncode == 0, p.stderr
    out = p.stdout + p.stderr
    assert "presupuesto global 5.00 $" in out and "(por defecto)" in out
    assert "GEMINI_API_KEY=✔" in out and "MockVideo" in out and "sí, coste 0" in out
    assert SECRETO not in out


def test_status_lee_preferencias_y_env(uv_motor, tmp_path):
    p = _status(uv_motor, tmp_path, prefs="---\nmotor:\n  presupuesto_usd: 12\n---\n")
    assert p.returncode == 0 and "presupuesto global 12.00 $" in p.stdout, p.stdout + p.stderr
    p = _status(uv_motor, tmp_path / "b", prefs="---\nmotor:\n  presupuesto_usd: 12\n---\n", env_file="MOTOR_PRESUPUESTO_USD=9\n")
    assert p.returncode == 0 and "presupuesto global 9.00 $" in p.stdout, p.stdout + p.stderr
