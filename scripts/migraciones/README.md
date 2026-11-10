# Migraciones de datos

Una actualización cambia el **producto** (lo versionado). Tus datos —la **instancia**: `contexto/`, `clientes/`,
`aprendizajes/`, `informes/`, `logs/` y `.env`— no se tocan nunca, salvo que una versión cambie el formato de algo que
ya tienes (una clave nueva en la ficha, un archivo que se renombra). Para eso existen las migraciones: pequeños
scripts que `scripts/actualizar.sh` aplica después de traer la versión nueva, mediante `scripts/migrar.py`.

Hoy no hay ninguna: la v0.1.0 es la primera versión.

## Reglas

1. **Una migración por cambio de formato**, en un archivo `NNNN_descripcion-corta.py` (cuatro cifras correlativas y
   minúsculas con guiones): `0001_ficha-clave-crm.py`. Los archivos con otro nombre se ignoran.
2. **Idempotente.** `necesaria()` mira los datos y decide; no hay registro de «ya aplicadas». Ejecutarla dos veces no
   cambia nada la segunda vez.
3. **Nunca borra ni mueve.** Si un archivo cambia de nombre, se copia al nuevo y el antiguo se queda (y se avisa en el
   mensaje). Si una clave sobra, se deja.
4. **Declara lo que toca** en `ARCHIVOS` (patrones relativos a la raíz). El ejecutor copia esos archivos a
   `logs/copias-migracion/<fecha>_<migración>/` antes de llamar a `aplicar()`.
5. **Solo biblioteca estándar**, Python 3.10, sin red y sin leer `.env`. Nada personal en los mensajes: rutas
   relativas y slugs, nunca contenidos.
6. **No toques lo que el usuario ha cambiado a propósito.** Añade lo que falta con el valor por defecto; no
   sobrescribas valores existentes.
7. **Con test** en `tests/scripts/test_migraciones.py` (caso «hace falta», caso «ya aplicada» y caso «dato raro»), y
   con una línea en `CHANGELOG.md` dentro de la versión que la introduce.

## Formato

```python
"""Añade `crm.servidor_mcp: ghl` a las fichas que no lo tienen (cambio de formato de la v0.2.0)."""
from __future__ import annotations

import pathlib

VERSION = "0.2.0"                                   # versión del producto que la introduce
DESCRIPCION = "Fichas: añade crm.servidor_mcp"      # una línea, la ve el usuario
ARCHIVOS = ["clientes/*/ficha.md"]                  # se copian antes de aplicar


def _fichas(raiz: pathlib.Path):
    return sorted(raiz.glob("clientes/*/ficha.md"))


def _le_falta(texto: str) -> bool:
    cabecera = texto.split("\n---", 1)[0]
    return "\ncrm:" in cabecera and "servidor_mcp:" not in cabecera


def necesaria(raiz: pathlib.Path) -> bool:
    return any(_le_falta(f.read_text(encoding="utf-8")) for f in _fichas(raiz))


def aplicar(raiz: pathlib.Path) -> list[str]:
    cambiadas = []
    for f in _fichas(raiz):
        texto = f.read_text(encoding="utf-8")
        if _le_falta(texto):
            f.write_text(texto.replace("\ncrm:\n", "\ncrm:\n  servidor_mcp: ghl\n", 1), encoding="utf-8")
            cambiadas.append(f"{f.relative_to(raiz).as_posix()}: añadido crm.servidor_mcp")
    return cambiadas                                # mensajes que se muestran al usuario
```

## Cómo se ejecuta

```bash
python3 -I scripts/migrar.py pendientes     # qué haría, sin tocar nada
python3 -I scripts/migrar.py aplicar        # lo que hace actualizar.sh
```

- Se aplican en orden de número. Si una falla, las siguientes no se aplican y `actualizar.sh` termina con código 1:
  el producto queda actualizado y basta con volver a ejecutarlo cuando se arregle.
- Una migración que no se puede importar (error de sintaxis, falta `VERSION`, `DESCRIPCION`, `necesaria` o
  `aplicar`) detiene el proceso antes de tocar nada (código 2).

## Probarla antes de publicar

En el test, crea una instancia falsa en un directorio temporal (la fixture `instancia` de `tests/conftest.py` sirve) y
llama a `necesaria()` y `aplicar()` directamente, o ejecuta el ejecutor contra ella:

```bash
python3 -I scripts/migrar.py --raiz /ruta/a/la/instancia/de/prueba pendientes
```
