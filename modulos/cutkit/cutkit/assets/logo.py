"""Logos para vídeo: el del cliente y los de terceros que aportas tú. cutkit no descarga ningún logo.

Dos fuentes, las dos dentro de la marca del cliente (`clientes/<cliente>/marca/`):

1. **Logo del cliente**, declarado en `marca.json` (rutas relativas a `marca/`):
       "logo": {"principal": "logo.svg", "claro": "logo-claro.png"}
   Se pide con `query` = `cliente` (o `marca`, o el slug o el nombre del cliente, p. ej. «Acme Automations»).
2. **Logos de terceros** (herramientas que integra el cliente, partners, medios en los que ha salido…), que
   aportas tú en `marca/logos/<nombre>.svg` o `.png` (variantes opcionales: `<nombre>-claro.png`,
   `<nombre>-mono.svg`…). Se piden por su nombre: «Nimbo» → `marca/logos/nimbo.svg`.
   Son marcas registradas de sus titulares: úsalos solo con permiso o de forma nominativa (para referirte a ese
   producto), sin alterarlos ni sugerir patrocinio. Sácalos del kit de prensa oficial de cada marca.

`params`: `variant` o `variante` (`principal` | `claro` | otra variante por nombre; `white`/`light` = `claro`),
`fmt` (`svg` | `png`; por defecto el archivo tal cual), `size` (lado mayor en px al rasterizar, 1024) y `cliente`
(si no se deduce del proyecto).

SVG → PNG (con `fmt: png` y solo un SVG): se usa el PNG hermano (`logo.svg` → `logo.png`) si existe; si no, el
Chromium de Playwright (extra `avanzado`); si tampoco hay, error que pide el PNG.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

from cutkit import marca as marca_mod
from cutkit.paths import marca_dir

from . import library

LOGO_EXT = (".svg", ".png")
NOTA_TERCEROS = ("Marca registrada de su titular: úsala solo con permiso o de forma nominativa (para referirte a ese "
                 "producto o servicio), sin alterarla ni sugerir patrocinio o respaldo.")
_CLIENTE = {"cliente", "marca", "logo", "logo-cliente", "propio", "mi-logo"}
_CLARO = {"claro", "white", "light", "blanco", "negativo", "inverse", "inverso"}
_PRINCIPAL = {"", "principal", "color", "symbol", "primary", "default", "normal"}


class LogoFailure(RuntimeError):
    """No hay logo utilizable; el mensaje dice dónde ponerlo (el director debe usar otra cosa mientras)."""


def slug(s: str) -> str:
    """«Nimbo CRM» → `nimbo-crm` (minúsculas, sin tildes, guiones)."""
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def logos_dir(cliente: str) -> Path:
    """Carpeta de los logos de terceros del cliente: `clientes/<cliente>/marca/logos/`."""
    d = marca_dir(cliente)
    assert d is not None
    return d / "logos"


def variante_de(params: dict[str, Any]) -> str:
    v = slug(params.get("variante") or params.get("variant") or params.get("colorway") or "")
    if v in _PRINCIPAL:
        return "principal"
    return "claro" if v in _CLARO else v


def es_cliente(query: str, cliente: str, nombre_marca: str = "") -> bool:
    """¿`query` pide el logo propio del cliente (y no uno de terceros)?"""
    q = slug(query)
    return q in _CLIENTE or q == slug(cliente) or (bool(nombre_marca) and q == slug(nombre_marca))


def _archivos_terceros(cliente: str) -> list[Path]:
    d = logos_dir(cliente)
    if not d.is_dir():
        return []
    return sorted(p for p in d.iterdir() if p.is_file() and p.suffix.lower() in LOGO_EXT)


def nombres_terceros(cliente: str) -> list[str]:
    """Nombres (slug del archivo) de los logos de terceros aportados, sin repetir."""
    return sorted({slug(p.stem) for p in _archivos_terceros(cliente)})


def _hermano(p: Path, ext: str) -> Path | None:
    for cand in (p.with_suffix(ext), p.with_suffix(ext.upper())):
        if cand.exists():
            return cand
    return None


def originales(entidad: str, cliente: str) -> list[Path]:
    """Todos los archivos originales de una entidad (para comparar en la QA): el logo del cliente (todas sus variantes
    declaradas y sus PNG hermanos) o los de un tercero (`<nombre>.*` y `<nombre>-<variante>.*`)."""
    m = marca_mod.cargar(cliente)
    out: list[Path] = []
    if es_cliente(entidad, cliente, m.nombre):
        for rel in (m.datos.get("logo") or {}).values():
            if not isinstance(rel, str) or not rel or m.carpeta is None:
                continue
            p = Path(rel) if Path(rel).is_absolute() else m.carpeta / rel
            if p.exists():
                out.append(p)
                if p.suffix.lower() == ".svg" and (png := _hermano(p, ".png")):
                    out.append(png)
    else:
        n = slug(entidad)
        out = [p for p in _archivos_terceros(cliente) if slug(p.stem) == n or slug(p.stem).startswith(n + "-")]
    return list(dict.fromkeys(out))


def a_png(path: Path, out: Path, size: int = 1024) -> tuple[Path, bool]:
    """(PNG utilizable, ¿se ha rasterizado en `out`?). Raster → tal cual; SVG → PNG hermano o Playwright."""
    path = Path(path)
    if path.suffix.lower() != ".svg":
        return path, False
    if png := _hermano(path, ".png"):
        return png, False
    from .web import PlaywrightNoDisponible, svg_a_png

    try:
        return svg_a_png(path, out, size), True
    except PlaywrightNoDisponible as exc:
        raise LogoFailure(f"{path.name} es SVG y hace falta un PNG: pon un PNG con fondo transparente al lado "
                          f"({path.with_suffix('.png').name}) o instala el rasterizador. {exc}") from exc
    except ValueError as exc:
        raise LogoFailure(f"No puedo rasterizar {path.name}: {exc}") from exc


def _logo_cliente(cliente: str, m: marca_mod.Marca, variante: str, fmt: str | None) -> tuple[Path, list[str]]:
    decl = {k: v for k, v in (m.datos.get("logo") or {}).items() if isinstance(v, str) and v}
    notes: list[str] = []
    rel = decl.get(variante)
    if rel is None and decl.get("principal"):
        rel = decl["principal"]
        if variante != "principal":
            notes.append(f"marca.json no declara la variante «{variante}» del logo: uso el principal")
    base = f"clientes/{cliente}/marca"
    raw = None
    if rel and m.carpeta is not None:
        p = Path(rel) if Path(rel).is_absolute() else m.carpeta / rel
        raw = p if p.exists() else None
    if raw is None:
        motivo = (f"marca.json declara «{rel}» pero no existe en {base}/" if rel else
                  f"no hay logo declarado en {base}/marca.json")
        avisos = f" ({'; '.join(m.avisos)})" if m.avisos else ""
        raise LogoFailure(f"Logo del cliente «{cliente}» no disponible: {motivo}{avisos}. Copia el archivo (SVG, o PNG "
                          f"con fondo transparente) en {base}/ y decláralo en marca.json: "
                          '"logo": {"principal": "logo.svg", "claro": "logo-claro.png"}.')
    if fmt != "svg" and raw.suffix.lower() != ".svg":
        return raw, notes
    if fmt == "png":
        raster = m.logo(variante)               # raster listo para vídeo (o el PNG hermano del SVG)
        if raster is not None:
            return raster, notes
    return raw, notes


def _logo_tercero(query: str, cliente: str, variante: str) -> tuple[Path, list[str]]:
    n = slug(query)
    if not n:
        raise LogoFailure("Petición de logo sin nombre: usa `cliente` o el nombre del logo aportado en marca/logos/")
    files = _archivos_terceros(cliente)
    notes: list[str] = []
    elegidos = [p for p in files if slug(p.stem) == f"{n}-{variante}"] if variante != "principal" else []
    if not elegidos:
        elegidos = [p for p in files if slug(p.stem) == n]
        if elegidos and variante != "principal":
            notes.append(f"no hay variante «{variante}» de {n} (marca/logos/{n}-{variante}.svg|png): uso la principal")
    if not elegidos:
        hay = nombres_terceros(cliente)
        disponibles = f" Logos aportados: {', '.join(hay)}." if hay else ""
        raise LogoFailure(f"No tengo el logo «{query}»: cutkit no descarga logos. Descárgalo del kit de prensa oficial "
                          f"y guárdalo como clientes/{cliente}/marca/logos/{n}.svg (o .png con fondo transparente). "
                          f"{NOTA_TERCEROS}{disponibles}")
    # SVG primero (escala sin perder nitidez en el render HTML); el PNG se usa si se pide o si no hay SVG
    elegidos.sort(key=lambda p: (p.suffix.lower() != ".svg", p.name))
    return elegidos[0], notes


def resolve_logo(query: str, params: dict[str, Any], *, cliente: str | None = None) -> dict[str, Any]:
    """Devuelve {path, move, entity, source, source_url, license, license_detail, original, notes}.

    `move=True` indica que `path` es un PNG temporal rasterizado aquí (el resolver lo mueve a la biblioteca);
    si no, `path` es el archivo del usuario y se copia sin tocarlo.
    """
    cliente = params.get("cliente") or cliente
    if not cliente:
        raise LogoFailure("No sé de qué cliente es este vídeo, y los logos salen de su carpeta de marca: crea el "
                          "proyecto con `--cliente <cliente>` o pasa params.cliente en la petición.")
    fmt = (str(params.get("fmt") or "").lower() or None)
    if fmt not in (None, "svg", "png"):
        raise LogoFailure(f"fmt no válido: {fmt!r} (svg | png)")
    variante = variante_de(params)
    try:
        m = marca_mod.cargar(cliente)
    except marca_mod.MarcaInvalida as exc:
        raise LogoFailure(f"marca.json de «{cliente}» no válido: {exc}") from exc
    propio = es_cliente(query, cliente, m.nombre)
    if propio:
        path, notes = _logo_cliente(cliente, m, variante, fmt)
    else:
        path, notes = _logo_tercero(query, cliente, variante)
    original = path
    move = False
    if fmt == "png" and path.suffix.lower() == ".svg":
        path, move = a_png(path, library.new_tmp("png"), int(params.get("size", 1024)))
        if move:
            notes.append(f"rasterizado a PNG ({int(params.get('size', 1024))} px) desde {original.name}")
    elif fmt == "svg" and path.suffix.lower() != ".svg":
        svg = _hermano(path, ".svg")
        if svg is None:
            raise LogoFailure(f"No hay versión SVG de {path.name}: pide fmt png o aporta el SVG al lado")
        path = original = svg
    if propio:
        entity = slug(cliente)
        lic, detail, source = "logo-cliente", "Logo del cliente (marca.json); úsalo según su guía de marca.", \
            "marca del cliente"
    else:
        entity = slug(query)
        lic, detail, source = "marca-registrada-terceros", NOTA_TERCEROS, "logos aportados por el usuario"
        notes.append(NOTA_TERCEROS)
    return {"path": Path(path), "move": move, "entity": entity, "source": source, "source_url": None,
            "license": lic, "license_detail": detail, "original": library.rel_or_abs(original), "variant": variante,
            "notes": notes}


__all__ = ["LogoFailure", "resolve_logo", "originales", "nombres_terceros", "logos_dir", "es_cliente", "a_png",
           "slug", "NOTA_TERCEROS"]
