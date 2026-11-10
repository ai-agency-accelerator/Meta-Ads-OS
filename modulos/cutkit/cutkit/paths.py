"""Rutas de cutkit dentro de Meta Ads OS (o de forma autónoma).

Raíz del producto: `META_ADS_OS_RAIZ` o tres carpetas por encima de este archivo
(`<raíz>/modulos/cutkit/cutkit/paths.py`).

| Qué | Dónde |
|---|---|
| Recursos del producto (perfiles, tokens de movimiento, reglas de QA, catálogo de SFX, fuentes libres, marca neutra) | `cutkit/recursos/` |
| Marca de cada cliente (`marca.json` + archivos) | `<raíz>/clientes/<cliente>/marca/` |
| Proyecto de montaje | `<raíz>/clientes/<cliente>/creativos/<AAAA-MM-DD>_<slug>/` (brutos en `brutos/`, trabajo en `edicion/`) |
| Cachés regenerables (biblioteca de medios, música, mates, SFX sintéticos) | `modulos/cutkit/datos/` (`CUTKIT_DATOS`) |

`CUTKIT_RUNS=<dir>` fuerza otra carpeta de trabajo: `<dir>/<slug>/edit` (útil en pruebas y fuera del producto).
"""
from __future__ import annotations

import datetime as _dt
import os
import re
from pathlib import Path

PAQUETE = Path(__file__).resolve().parent
MODULO = PAQUETE.parent
RAIZ = Path(os.environ.get("META_ADS_OS_RAIZ") or PAQUETE.parents[2]).resolve()
CLIENTES = RAIZ / "clientes"

RECURSOS = PAQUETE / "recursos"
PERFILES = RECURSOS / "perfiles"
FUENTES = RECURSOS / "fuentes"
DATOS = Path(os.environ.get("CUTKIT_DATOS") or MODULO / "datos")
LIBRARY = DATOS / "biblioteca"
HF_VERSION = "0.8.114"

# nombres antiguos que aún usa parte del código
EDICION = RECURSOS
FONTS = FUENTES
REPO = MODULO

_SLUG = re.compile(r"[a-z0-9][a-z0-9-]*")


class ProyectoNoEncontrado(LookupError):
    """No hay carpeta de trabajo para ese slug."""


def _valida(slug: str, que: str = "slug") -> str:
    if not _SLUG.fullmatch(slug or ""):
        raise ValueError(f"{que} no válido: {slug!r} (minúsculas, números y guiones)")
    return slug


def cargar_entorno() -> None:
    """Carga `<raíz>/.env` sin sobrescribir lo que ya está en el entorno. Nunca imprime valores."""
    f = RAIZ / ".env"
    if not f.exists():
        return
    for linea in f.read_text(encoding="utf-8", errors="ignore").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        k, v = linea.split("=", 1)
        k = k.strip().removeprefix("export ").strip()
        os.environ.setdefault(k, v.strip().strip('"').strip("'"))


def marca_dir(cliente: str | None) -> Path | None:
    return CLIENTES / _valida(cliente, "cliente") / "marca" if cliente else None


def proyecto_dir(slug: str, cliente: str | None = None, fecha: str | None = None, crear: bool = False) -> Path:
    """Carpeta de entrega del proyecto: `clientes/<cliente>/creativos/<AAAA-MM-DD>_<slug>/`.

    Sin `cliente`, busca un proyecto existente con ese slug en todos los clientes (el más reciente).
    """
    _valida(slug)
    if cliente:
        base = CLIENTES / _valida(cliente, "cliente") / "creativos"
        existentes = sorted(base.glob(f"*_{slug}")) if base.exists() else []
        if existentes and not fecha:
            return existentes[-1]
        if not crear:
            if existentes:
                return existentes[-1]
            raise ProyectoNoEncontrado(f"no existe ningún proyecto «{slug}» en clientes/{cliente}/creativos/")
        if not (CLIENTES / cliente).exists():
            raise ProyectoNoEncontrado(f"no existe clientes/{cliente}/ (créalo con /cliente-nuevo)")
        d = base / f"{fecha or _dt.date.today().isoformat()}_{slug}"
        d.mkdir(parents=True, exist_ok=True)
        return d
    hits = sorted(CLIENTES.glob(f"*/creativos/*_{slug}")) if CLIENTES.exists() else []
    hits = [h for h in hits if h.is_dir()]
    if not hits:
        raise ProyectoNoEncontrado(f"no encuentro el proyecto «{slug}»: créalo con `ck new {slug} --cliente <cliente>` "
                                   "o `ck anuncio … --cliente <cliente>`")
    return max(hits, key=lambda p: p.name[:10])


def cliente_de(slug: str) -> str | None:
    """Slug del cliente dueño del proyecto (None si se trabaja con CUTKIT_RUNS)."""
    if os.environ.get("CUTKIT_RUNS"):
        return None
    try:
        return proyecto_dir(slug).parent.parent.name
    except ProyectoNoEncontrado:
        return None


def run_dir(slug: str, cliente: str | None = None, crear: bool = False) -> Path:
    """Carpeta de trabajo de cutkit (media/, versions/, export/) de un proyecto."""
    env = os.environ.get("CUTKIT_RUNS")
    if env:
        d = Path(env) / _valida(slug) / "edit"
    else:
        d = proyecto_dir(slug, cliente, crear=crear) / "edicion"
    (d / "media").mkdir(parents=True, exist_ok=True)
    (d / "versions").mkdir(parents=True, exist_ok=True)
    return d


def runs_root() -> Path:
    """Carpeta que agrupa los proyectos (para buscar historiales, p. ej. pistas de música usadas)."""
    env = os.environ.get("CUTKIT_RUNS")
    return Path(env) if env else CLIENTES


def all_timelines():
    """Timelines de todas las versiones conocidas (para no repetir música entre vídeos seguidos)."""
    env = os.environ.get("CUTKIT_RUNS")
    if env:
        return Path(env).glob("*/edit/versions/*/timeline.json")
    return CLIENTES.glob("*/creativos/*/edicion/versions/*/timeline.json")


def version_dir(slug: str, vid: str) -> Path:
    d = run_dir(slug) / "versions" / vid
    d.mkdir(parents=True, exist_ok=True)
    return d
