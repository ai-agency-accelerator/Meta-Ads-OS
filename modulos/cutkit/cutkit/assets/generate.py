"""B-roll generado con IA: en el producto NO se hace en cutkit.

Las imágenes y los clips generados con IA (`kind: gen_image` / `gen_video`) los produce el motor de vídeo
(`modulos/motor-ia`), que estima el coste, pide confirmación y respeta su presupuesto. Así en cutkit no queda ningún
gasto sin control: aquí no se llama a ningún proveedor ni se lee ninguna clave.

Flujo para un vídeo híbrido:
1. genera la escena con el motor (`uv run --project modulos/motor-ia motor --help`; es una orden de pago y pide
   confirmación);
2. deja el MP4 o la imagen en `<proyecto>/brutos/broll-ia/`;
3. pídelo en el plan como archivo: `{"id": "broll_oficina", "kind": "file", "query": "brutos/broll-ia/oficina.mp4",
   "params": {"license": "generado con IA (motor)"}}` y marca el anuncio con la etiqueta de IA.

Las funciones públicas conservan su firma para que el resolver y el código existente no se rompan: todas lanzan
`BrollIANoDisponible` (subclase de `GenFailure`), que el resolver anota como recurso no disponible.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


class GenFailure(RuntimeError):
    """La generación no se hizo; el director debe usar otra cosa."""


class BrollIANoDisponible(GenFailure):
    """cutkit no genera con IA: el B-roll generado sale del motor o lo aportas tú."""


def mensaje(kind: str = "gen_video", concept: str = "") -> str:
    que = "la imagen" if kind == "gen_image" else "el clip"
    sobre = f" «{concept.strip()[:80]}»" if concept and concept.strip() else ""
    return (f"cutkit no genera B-roll con IA ({kind}{sobre}). Genera {que} con el motor "
            "(`uv run --project modulos/motor-ia motor …`: estima el coste, pide confirmación y respeta su "
            "presupuesto), déjalo en <proyecto>/brutos/broll-ia/ y pídelo con kind \"file\"; o aporta tú el "
            "archivo, o usa otra fuente (captura, scroll, stock o gráfico).")


def generate(kind: str, concept: str, params: dict[str, Any] | None = None, **_: Any) -> dict[str, Any]:
    """Punto único de generación: siempre lanza `BrollIANoDisponible` con el camino correcto."""
    raise BrollIANoDisponible(mensaje(kind, concept))


def gen_image(concept: str, params: dict[str, Any], *, slug: str) -> dict[str, Any]:
    """Firma histórica de la imagen generada: no disponible en cutkit (ver `generate`)."""
    return generate("gen_image", concept, params)


def gen_video(concept: str, params: dict[str, Any], out: Path, *, slug: str,
              charge: Callable[[float], None] | None = None) -> dict[str, Any]:
    """Firma histórica del clip generado: no disponible en cutkit (ver `generate`). Nunca llama a `charge`."""
    return generate("gen_video", concept, params)


def estimate_image(params: dict[str, Any]) -> float:
    """cutkit no gasta en imagen generada: 0 $. El coste real lo estima el motor antes de generar."""
    return 0.0


def estimate_video(params: dict[str, Any]) -> float:
    """cutkit no gasta en vídeo generado: 0 $. El coste real lo estima el motor antes de generar."""
    return 0.0


__all__ = ["GenFailure", "BrollIANoDisponible", "generate", "gen_image", "gen_video", "estimate_image",
           "estimate_video", "mensaje"]
