"""Stock de Pexels y Pixabay, solo con tu clave. Sin clave → fallo claro para que el director use otra cosa.

Claves (se cargan del `.env` de la raíz del producto con `cargar_entorno()`; nunca se imprimen):
- `PEXELS_API_KEY`: vídeo o foto con la licencia de Pexels (uso comercial gratuito, sin atribución obligatoria;
  no se puede revender sin modificar ni insinuar que las personas o marcas que aparecen respaldan el anuncio).
- `PIXABAY_API_KEY`: vídeo o foto con la licencia de contenido de Pixabay (condiciones parecidas). Sus términos
  piden descargar (no enlazar en caliente) y cachear: la biblioteca persistente ya lo cumple.

`params`: `media` (video | image, por defecto video), `orientation` (landscape | portrait | square),
`min_width` (px), `provider` (pexels | pixabay). `query` = búsqueda (mejor en inglés).

Cada descarga devuelve su licencia, autor, página de origen e id del proveedor: el resolver lo guarda en la
biblioteca y en el `Asset` de `assets.json`, así queda constancia de la licencia de cada archivo.
Los mensajes de error no incluyen nunca la clave (Pixabay la lleva en la URL).
"""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from cutkit.paths import cargar_entorno

PROVIDERS = {"pexels": "PEXELS_API_KEY", "pixabay": "PIXABAY_API_KEY"}
LICENSES = {
    "pexels": {"license": "Pexels License", "license_url": "https://www.pexels.com/license/",
               "detail": "Uso comercial gratuito y sin atribución obligatoria; prohibido revenderlo sin modificar y "
                         "dar a entender que las personas o marcas que aparecen respaldan el producto."},
    "pixabay": {"license": "Pixabay Content License", "license_url": "https://pixabay.com/service/license-summary/",
                "detail": "Uso comercial gratuito y sin atribución obligatoria; prohibido revenderlo sin modificar, "
                          "usarlo de forma engañosa o insinuar respaldo de las personas o marcas que aparecen."},
}


class StockFailure(RuntimeError):
    pass


def _err(exc: Exception) -> str:
    """Error de red legible y sin secretos (nada de URLs con `key=`)."""
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code} en {exc.request.url.host}"
    if isinstance(exc, httpx.HTTPError):
        host = ""
        try:
            host = f" ({exc.request.url.host})"
        except RuntimeError:          # el error no lleva petición asociada
            pass
        return f"{type(exc).__name__}{host}"
    return str(exc)


def _pexels(query: str, params: dict[str, Any], key: str) -> dict[str, Any]:
    media = params.get("media", "video")
    orient = params.get("orientation", "landscape")
    min_w = int(params.get("min_width", 1920 if orient == "landscape" else 1080))
    headers = {"Authorization": key}
    if media == "video":
        r = httpx.get("https://api.pexels.com/videos/search", headers=headers, timeout=30,
                      params={"query": query, "orientation": orient, "per_page": 15, "size": "large"})
        r.raise_for_status()
        for v in r.json().get("videos", []):
            files = sorted((f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4"
                            and (f.get("width") or 0) >= min_w), key=lambda f: f.get("width") or 0)
            if files:
                user = v.get("user") or {}
                return {"url": files[0]["link"], "ext": "mp4", "page": v.get("url"), "author": user.get("name"),
                        "author_url": user.get("url"), "id": v.get("id")}
    else:
        r = httpx.get("https://api.pexels.com/v1/search", headers=headers, timeout=30,
                      params={"query": query, "orientation": orient, "per_page": 15})
        r.raise_for_status()
        for ph in r.json().get("photos", []):
            if (ph.get("width") or 0) >= min_w:
                return {"url": ph["src"]["original"], "ext": "jpg", "page": ph.get("url"),
                        "author": ph.get("photographer"), "author_url": ph.get("photographer_url"), "id": ph.get("id")}
    raise StockFailure(f"Pexels: sin resultados ≥{min_w}px para '{query}'")


def _pixabay(query: str, params: dict[str, Any], key: str) -> dict[str, Any]:
    media = params.get("media", "video")
    orient = params.get("orientation", "landscape")
    min_w = int(params.get("min_width", 1920 if orient == "landscape" else 1080))
    if media == "video":
        r = httpx.get("https://pixabay.com/api/videos/", timeout=30,
                      params={"key": key, "q": query, "per_page": 20, "safesearch": "true"})
        r.raise_for_status()
        for hit in r.json().get("hits", []):
            for size in ("large", "medium"):
                f = (hit.get("videos") or {}).get(size) or {}
                if f.get("url") and (f.get("width") or 0) >= min_w:
                    return {"url": f["url"], "ext": "mp4", "page": hit.get("pageURL"), "author": hit.get("user"),
                            "author_url": None, "id": hit.get("id")}
    else:
        r = httpx.get("https://pixabay.com/api/", timeout=30,
                      params={"key": key, "q": query, "per_page": 20, "image_type": "photo", "safesearch": "true",
                              "orientation": "vertical" if orient == "portrait" else "horizontal",
                              "min_width": min_w})
        r.raise_for_status()
        for hit in r.json().get("hits", []):
            url = hit.get("largeImageURL")
            if url:
                return {"url": url, "ext": "jpg", "page": hit.get("pageURL"), "author": hit.get("user"),
                        "author_url": None, "id": hit.get("id")}
    raise StockFailure(f"Pixabay: sin resultados ≥{min_w}px para '{query}'")


def _key(env: str) -> str:
    return os.environ.get(env, "").strip()


def available() -> list[str]:
    """Proveedores con clave en el entorno o en el `.env` de la raíz."""
    cargar_entorno()
    return [n for n, env in PROVIDERS.items() if _key(env)]


def fetch(query: str, params: dict[str, Any], out_base: Path) -> dict[str, Any]:
    """Busca y descarga el mejor resultado en `out_base.<ext>`.

    Devuelve {path, source_url, download_url, license, license_url, license_detail, author, author_url,
    provider, provider_id, fetched}.
    """
    cargar_entorno()
    providers = [params["provider"]] if params.get("provider") else list(PROVIDERS)
    errors = []
    for prov in providers:
        env = PROVIDERS.get(prov)
        if env is None:
            errors.append(f"{prov}: proveedor desconocido (pexels | pixabay)")
            continue
        key = _key(env)
        if not key:
            errors.append(f"{prov}: sin clave ({env} en el .env de la raíz)")
            continue
        out = None
        try:
            hit = (_pexels if prov == "pexels" else _pixabay)(query, params, key)
            out = Path(out_base).with_suffix("." + hit["ext"])
            with httpx.stream("GET", hit["url"], timeout=120, follow_redirects=True) as r:
                r.raise_for_status()
                with open(out, "wb") as f:
                    for chunk in r.iter_bytes(1 << 20):
                        f.write(chunk)
            lic = LICENSES[prov]
            return {"path": out, "source_url": hit.get("page") or hit["url"], "download_url": hit["url"],
                    "license": f"{lic['license']} ({lic['license_url']})", "license_url": lic["license_url"],
                    "license_detail": lic["detail"], "author": hit.get("author"), "author_url": hit.get("author_url"),
                    "provider": prov, "provider_id": hit.get("id"), "fetched": date.today().isoformat()}
        except (StockFailure, httpx.HTTPError, ValueError, KeyError) as exc:   # ValueError: JSON roto
            if out is not None:
                out.unlink(missing_ok=True)
            errors.append(f"{prov}: {_err(exc)}")
    raise StockFailure("Stock no disponible — " + "; ".join(errors) +
                       ". Usa otra fuente (captura, logo, archivo propio o gráfico programático).")


__all__ = ["StockFailure", "available", "fetch", "LICENSES", "PROVIDERS"]
