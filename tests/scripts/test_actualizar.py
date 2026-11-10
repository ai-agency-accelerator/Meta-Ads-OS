"""scripts/actualizar.sh contra un remoto local: avanza, migra y se niega a pisar cambios."""
from __future__ import annotations

import re
import shutil
import subprocess

import pytest

from apoyo_scripts import RAIZ_PRODUCTO, necesita_bash, necesita_git

pytestmark = [necesita_bash, necesita_git]
GIT_ID = ["-c", "user.name=Prueba", "-c", "user.email=prueba@example.com", "-c", "commit.gpgsign=false"]


def _git(cwd, *args):
    subprocess.run(["git", *GIT_ID, *args], cwd=cwd, check=True, capture_output=True, text=True)


def _actualizar(raiz, bin_dir, *args):
    entorno = {"PATH": str(bin_dir), "HOME": str(raiz.parent), "LANG": "C.UTF-8",
               "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"}
    return subprocess.run(["bash", "scripts/actualizar.sh", *args], cwd=raiz, env=entorno, capture_output=True,
                          text=True, timeout=120)


@pytest.fixture
def repos(tmp_path, copia_producto):
    """(origen, alumno): el alumno es un clon del remoto; el origen publica versiones nuevas en el remoto."""
    origen = copia_producto
    _git(origen, "init", "-q", "-b", "main")
    _git(origen, "add", "-A")
    _git(origen, "commit", "-qm", "v0.1.0")
    remoto = tmp_path / "remoto.git"
    _git(tmp_path, "clone", "-q", "--bare", str(origen), str(remoto))
    alumno = tmp_path / "alumno"
    _git(tmp_path, "clone", "-q", str(remoto), str(alumno))
    (alumno / "clientes" / "acme").mkdir(parents=True)
    (alumno / "clientes" / "acme" / "ficha.md").write_text("---\nslug: acme\ncrm:\n  tipo: ghl\n---\n",
                                                           encoding="utf-8")

    def publicar(version: str, migracion: str | None = None) -> None:
        py = origen / "pyproject.toml"
        py.write_text(re.sub(r'(?m)^version = ".*"', f'version = "{version}"', py.read_text(encoding="utf-8")),
                      encoding="utf-8")
        cambios = origen / "CHANGELOG.md"
        anterior = cambios.read_text(encoding="utf-8") if cambios.exists() else "# Cambios\n"
        cambios.write_text(anterior.replace("\n## ", f"\n## [{version}] — 2026-12-01\n- Novedad de prueba.\n\n## ", 1),
                           encoding="utf-8")
        if migracion:
            (origen / "scripts" / "migraciones" / "0001_prueba.py").write_text(migracion, encoding="utf-8")
        _git(origen, "add", "-A")
        _git(origen, "commit", "-qm", f"v{version}")
        _git(remoto, "fetch", "-q", str(origen), "main:main")

    return origen, alumno, publicar


def _ejemplo_readme() -> str:
    texto = (RAIZ_PRODUCTO / "scripts" / "migraciones" / "README.md").read_text(encoding="utf-8")
    return re.search(r"```python\n(.*?)```", texto, re.S).group(1)


def test_al_dia(repos, bin_falso):
    _, alumno, _ = repos
    r = _actualizar(alumno, bin_falso[0])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Ya tienes la última versión" in r.stdout


def test_trae_version_nueva_y_migra(repos, bin_falso):
    _, alumno, publicar = repos
    publicar("0.2.0", _ejemplo_readme())
    r = _actualizar(alumno, bin_falso[0], "--comprobar")
    assert r.returncode == 0 and "hay versión nueva" in r.stdout
    assert "servidor_mcp" not in (alumno / "clientes" / "acme" / "ficha.md").read_text(encoding="utf-8")

    r = _actualizar(alumno, bin_falso[0])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "Producto actualizado a v0.2.0" in r.stdout
    assert "Migración 0001_prueba" in r.stdout
    assert "servidor_mcp: ghl" in (alumno / "clientes" / "acme" / "ficha.md").read_text(encoding="utf-8")
    assert list((alumno / "logs" / "copias-migracion").rglob("ficha.md"))


def test_no_pisa_cambios_en_el_producto(repos, bin_falso):
    _, alumno, publicar = repos
    publicar("0.2.0")
    instalar = alumno / "scripts" / "instalar.sh"
    instalar.write_text(instalar.read_text(encoding="utf-8") + "\n# cambio local\n", encoding="utf-8")
    r = _actualizar(alumno, bin_falso[0])
    assert r.returncode == 1
    assert "Has modificado archivos del producto" in r.stdout
    assert "git stash" in r.stdout
    assert "# cambio local" in instalar.read_text(encoding="utf-8")


def test_no_avanza_con_commits_propios(repos, bin_falso):
    _, alumno, publicar = repos
    publicar("0.2.0")
    (alumno / "notas.md").write_text("mío\n", encoding="utf-8")
    _git(alumno, "add", "notas.md")
    _git(alumno, "commit", "-qm", "propio")
    r = _actualizar(alumno, bin_falso[0])
    assert r.returncode == 1
    assert "commit(s) propios" in r.stdout


def test_sin_git_explica_el_zip(copia_producto, bin_falso):
    r = _actualizar(copia_producto, bin_falso[0])
    assert r.returncode == 1
    assert "ZIP" in r.stdout


def test_no_toca_la_instancia(repos, bin_falso):
    _, alumno, publicar = repos
    (alumno / "contexto").mkdir()
    (alumno / "contexto" / "operador.md").write_text("propio\n", encoding="utf-8")
    publicar("0.2.0")
    assert _actualizar(alumno, bin_falso[0]).returncode == 0
    assert (alumno / "contexto" / "operador.md").read_text(encoding="utf-8") == "propio\n"
    assert shutil.which("git")
