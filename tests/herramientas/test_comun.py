import json

import pytest


def test_leer_ficha(instancia):
    import _comun
    f = _comun.leer_ficha("acme")
    assert f["topes"] == {"cambio_dia": 100, "total_dia": 300}
    assert f["meta"]["evento_principal"] == "Lead"
    assert f["stripe"] is False and f["explorar_explotar"] == 0.3


def test_ficha_inexistente_o_slug_malo(instancia):
    import _comun
    with pytest.raises(_comun.FichaInvalida):
        _comun.leer_ficha("no-existe")
    with pytest.raises(_comun.FichaInvalida):
        _comun.leer_ficha("../etc")


def test_credencial_por_cliente(instancia, monkeypatch):
    import _comun
    monkeypatch.setenv("GHL_TOKEN", "global")
    monkeypatch.setenv("GHL_TOKEN_CLINICA_SONRISA", "propio")
    assert _comun.credencial("GHL_TOKEN", "clinica-sonrisa") == "propio"
    assert _comun.credencial("GHL_TOKEN", "acme") == "global"


def test_registrar_cambio_anonimiza(instancia):
    import _comun
    _comun.registrar_cambio("meta", "cli", "crear", "123", "acme", "lead ana@ejemplo.com +34 600 000 000")
    fila = json.loads((instancia / "logs" / "cambios.jsonl").read_text(encoding="utf-8").strip())
    assert fila["detalle"] == "lead *** ***"
    assert set(fila) == {"ts", "session", "sistema", "via", "accion", "entidad_id", "cliente", "detalle"}


def test_cabecera_con_comentario_tras_valor_entre_comillas(instancia):
    import _comun

    datos = _comun.parsear_cabecera('---\nmoneda: "EUR" # de la cuenta\nnota: \'a # b\' # aparte\ntope: 30 # €\n---\n')
    assert datos["moneda"] == "EUR" and datos["nota"] == "a # b" and datos["tope"] == 30


# ---------------------------------------------------------------- I6: revisión de corrección

@pytest.mark.parametrize("texto, esperado", [
    # miles con espacio, NBSP o espacio fino (RAE), con punto (España) y con coma (MX, EE. UU.)
    ("1 200 €", 1200), ("1 200 €", 1200), ("12 500", 12500), ("1 200 000", 1200000),
    ("1.200", 1200), ("4.800", 4800), ("1.234.567", 1234567), ("12.500,5", 12500.5), ("1.200,50 €", 1200.5),
    ("1,200", 1200), ("12,345", 12345), ("1,200.50", 1200.5), ("$1,500", 1500), ("1,234,567", 1234567),
    # decimales: un 0 delante nunca es separador de miles; con 1, 2 o más de 3 cifras tras el separador, decimal
    ("0.175", 0.175), ("0,175", 0.175), ("120,5", 120.5), ("1,5", 1.5), ("80.5 (sin IVA)", 80.5), ("1234.5", 1234.5),
    ("1234,5", 1234.5), (".5", 0.5),
    # notación científica, signos, celdas con texto
    ("9e3", 9000), ("1.20212E+17", 1.20212e17), ("-1.200", -1200), ("≈ 95", 95), ("€ 99", 99), ("30 / 120", 30),
    ("", None), ("—", None), (None, None), ("abc", None), (7, 7.0), (2.5, 2.5),
])
def test_numero_humano_una_sola_regla(texto, esperado):
    import _comun
    assert _comun.numero(texto) == esperado


def test_numero_humano_mismas_reglas_en_todas_las_herramientas():
    """registro_creativo.num, num_humano y reglas_meta.numero son la misma función: «1 200 €» = 1200 en todas."""
    import _comun
    import registro_creativo
    import reglas_meta

    for celda in ("1 200 €", "1,200", "4.800", "0.175", "1.200,50 €", "$1,500"):
        v = _comun.numero(celda)
        assert registro_creativo.num(celda) == v and registro_creativo.num_humano(celda) == v
        assert reglas_meta.numero(celda) == v


@pytest.mark.parametrize("texto, esperado", [
    ("2026-12-01T23:59:59+0100", "2026-12-01T22:59:59+00:00"),     # formato de Graph
    ("2026-12-01T23:59:59+0000", "2026-12-01T23:59:59+00:00"),
    ("2026-11-01T10:00:00.000Z", "2026-11-01T10:00:00+00:00"),     # GHL
    ("2026-11-01T10:00:00.12345+00:00", "2026-11-01T10:00:00.123450+00:00"),
    ("2026-11-16 08:00", "2026-11-16T08:00:00"),
])
def test_fecha_iso_formato_graph(texto, esperado):
    from datetime import timezone

    import _comun
    dt = _comun.fecha_iso(texto)
    assert (dt.astimezone(timezone.utc) if dt.tzinfo else dt).isoformat() == esperado
    assert _comun.fecha_iso("") is None and _comun.fecha_iso("mañana") is None


def _pythons_antiguos():
    import shutil
    import subprocess
    vistos, salida = set(), []
    for nombre in ("python3.8", "python3.9", "python3.10", "python3.11", "python3.12", "/usr/bin/python3"):
        ruta = shutil.which(nombre)
        if not ruta or ruta in vistos:
            continue
        vistos.add(ruta)
        v = subprocess.run([ruta, "-I", "-c", "import sys; print(sys.version_info[1])"], capture_output=True,
                           text=True, timeout=30)
        if v.returncode == 0 and v.stdout.strip().isdigit() and 8 <= int(v.stdout) <= 12:
            salida.append(ruta)
    return salida


def test_fecha_iso_en_python_3_8_a_3_12():
    """Hallazgo 22: antes de 3.11, `fromisoformat` no acepta «+0100»; la función común sí, en cualquier versión."""
    import pathlib
    import subprocess
    import sys

    herramientas = pathlib.Path(__file__).resolve().parents[2] / "herramientas"
    codigo = ("import sys; sys.path.insert(0, sys.argv[1]); import _comun; "
              "print(_comun.fecha_iso('2026-12-01T23:59:59+0100').isoformat())")
    probados = [sys.executable] + _pythons_antiguos()
    for py in probados:
        r = subprocess.run([py, "-I", "-c", codigo, str(herramientas)], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, (py, r.stderr)
        assert r.stdout.strip() == "2026-12-01T23:59:59+01:00"


def test_consola_segura_no_revienta_con_cp1252():
    """Hallazgo 28: Git Bash en Windows con la salida redirigida es cp1252; ✓ y → no existen ahí."""
    import io
    import sys

    import _comun
    falsa = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    viejo = sys.stdout
    try:
        sys.stdout = falsa
        _comun.consola_segura()
        print("✓ hecho → siguiente ≥ 3")
        sys.stdout.flush()
    finally:
        sys.stdout = viejo
    assert falsa.buffer.getvalue().decode("cp1252") == "? hecho ? siguiente ? 3\n"


HERRAMIENTAS_CON_COMUN = ["ad_library", "audiencias_meta", "capi", "doctor", "economia", "editar_video",
                          "elementos_creativos", "embudo", "estado", "formularios_meta", "ghl", "ig_competidores",
                          "landing_check", "meta_ads", "motor_proyectos", "notificar", "paginas", "reddit_pulso",
                          "registro_creativo", "reglas_meta", "render", "stripe_datos", "transcribir"]


@pytest.mark.parametrize("herramienta", HERRAMIENTAS_CON_COMUN)
def test_ayuda_en_consola_cp1252(herramienta, tmp_path):
    """Hallazgo 28: con la salida en cp1252 estricto (Windows, salida redirigida), `--help` no revienta."""
    import pathlib
    import subprocess
    import sys

    ruta = pathlib.Path(__file__).resolve().parents[2] / "herramientas" / f"{herramienta}.py"
    envoltorio = ("import io, runpy, sys\n"
                  "sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='cp1252', errors='strict')\n"
                  "sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='cp1252', errors='strict')\n"
                  "sys.argv = [sys.argv[1], '--help']\n"
                  "runpy.run_path(sys.argv[0], run_name='__main__')\n")
    r = subprocess.run([sys.executable, "-I", "-c", envoltorio, str(ruta)], capture_output=True, timeout=120,
                       env={"META_ADS_OS_RAIZ": str(tmp_path), "PATH": "/usr/bin:/bin"})
    assert b"UnicodeEncodeError" not in r.stderr, r.stderr.decode("cp1252", "replace")[-600:]
    assert r.returncode == 0
