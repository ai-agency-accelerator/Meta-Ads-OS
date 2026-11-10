#!/usr/bin/env python3
"""Aplica las migraciones de datos de `scripts/migraciones/` (solo biblioteca estándar, Python ≥ 3.10).

Lo llama `scripts/actualizar.sh` después de traer una versión nueva. Es la única vía por la que una actualización
puede cambiar tu instancia (`contexto/`, `clientes/`, `aprendizajes/`, `informes/`). Formato de una migración:
`scripts/migraciones/README.md`.

Cada migración decide sola si hace falta (`necesaria`), así que se puede ejecutar las veces que quieras. Antes de
aplicar una, copia los archivos que declara en `ARCHIVOS` a `logs/copias-migracion/<fecha>_<migración>/`. Nunca borra.

Uso (desde la raíz del proyecto):
  python3 -I scripts/migrar.py pendientes [--json]
  python3 -I scripts/migrar.py aplicar
Códigos de salida: 0 bien · 1 una migración falló (las siguientes no se aplican) · 2 una migración no se puede cargar.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import re
import shutil
import sys
from datetime import datetime

RAIZ = pathlib.Path(os.environ.get("META_ADS_OS_RAIZ") or pathlib.Path(__file__).resolve().parent.parent)
NOMBRE_VALIDO = re.compile(r"^(\d{4})_[a-z0-9][a-z0-9-]*\.py$")


class MigracionInvalida(Exception):
    pass


def descubrir(carpeta: pathlib.Path) -> list[pathlib.Path]:
    if not carpeta.is_dir():
        return []
    return sorted(p for p in carpeta.iterdir() if p.is_file() and NOMBRE_VALIDO.match(p.name))


def cargar(ruta: pathlib.Path):
    spec = importlib.util.spec_from_file_location(f"migracion_{ruta.stem.replace('-', '_')}", ruta)
    if spec is None or spec.loader is None:
        raise MigracionInvalida(f"{ruta.name}: no se puede importar")
    modulo = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(modulo)
    except Exception as e:  # el error es de la migración, no del usuario
        raise MigracionInvalida(f"{ruta.name}: error al importar ({type(e).__name__}: {e})") from None
    for nombre in ("VERSION", "DESCRIPCION", "necesaria", "aplicar"):
        if not hasattr(modulo, nombre):
            raise MigracionInvalida(f"{ruta.name}: falta {nombre} (ver scripts/migraciones/README.md)")
    return modulo


def copiar_antes(raiz: pathlib.Path, modulo, id_migracion: str) -> pathlib.Path | None:
    patrones = list(getattr(modulo, "ARCHIVOS", []) or [])
    archivos: list[pathlib.Path] = []
    for patron in patrones:
        archivos.extend(p for p in raiz.glob(patron) if p.is_file())
    if not archivos:
        return None
    destino = raiz / "logs" / "copias-migracion" / f"{datetime.now():%Y%m%d-%H%M%S}_{id_migracion}"
    for f in archivos:
        rel = f.relative_to(raiz)
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, destino / rel)
    return destino


def pendientes(raiz: pathlib.Path, carpeta: pathlib.Path) -> list[tuple[pathlib.Path, object]]:
    lista = []
    for ruta in descubrir(carpeta):
        modulo = cargar(ruta)
        if modulo.necesaria(raiz):
            lista.append((ruta, modulo))
    return lista


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raiz", type=pathlib.Path, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--carpeta", type=pathlib.Path, default=None, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="orden", required=True)
    p = sub.add_parser("pendientes", help="lista las migraciones que hacen falta, sin aplicarlas")
    p.add_argument("--json", action="store_true")
    sub.add_parser("aplicar", help="aplica las migraciones pendientes en orden")
    a = ap.parse_args(argv)

    raiz = (a.raiz or RAIZ).resolve()
    carpeta = (a.carpeta or raiz / "scripts" / "migraciones").resolve()
    try:
        lista = pendientes(raiz, carpeta)
    except MigracionInvalida as e:
        print(f"[ERROR]  Migración no válida: {e}")
        return 2

    if a.orden == "pendientes":
        if a.json:
            print(json.dumps([{"id": r.stem, "version": m.VERSION, "descripcion": m.DESCRIPCION} for r, m in lista],
                             ensure_ascii=False, indent=2))
        elif not lista:
            print("[OK]     Sin migraciones pendientes")
        else:
            for r, m in lista:
                print(f"[INFO]   Pendiente {r.stem} (v{m.VERSION}): {m.DESCRIPCION}")
        return 0

    if not lista:
        print("[OK]     Sin migraciones pendientes: tus datos ya tienen el formato de esta versión")
        return 0
    for ruta, modulo in lista:
        copia = None
        try:
            copia = copiar_antes(raiz, modulo, ruta.stem)
            mensajes = modulo.aplicar(raiz) or []
        except Exception as e:
            donde = f" Hay copia de lo que tocaba en {copia.relative_to(raiz).as_posix()}/." if copia else ""
            print(f"[ERROR]  Migración {ruta.stem} fallida: {type(e).__name__}: {e}")
            print(f"         No he aplicado las siguientes.{donde} Ejecuta /doctor o pide ayuda con este mensaje.")
            return 1
        print(f"[OK]     Migración {ruta.stem} (v{modulo.VERSION}): {modulo.DESCRIPCION}")
        if copia:
            print(f"         Copia previa en {copia.relative_to(raiz).as_posix()}/")
        for linea in mensajes:
            print(f"         {linea}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
