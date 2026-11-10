"""cutkit.motion.registry_three — escenas 3D/WebGL OPCIONALES (motor en cutkit/motion/three/, ver su README.md).

Capa «más a más»: NO sustituye a ningún componente 2D ni la elige el director por defecto. Se activa en un plan
cambiando el `component` de una decisión por el de la escena (mismas props y cues que su equivalente 2D), p. ej.
`"component": "logo.reveal"` → `"component": "scene.logo_reveal3d"`. Si WebGL o el montaje fallan en el render, la
escena delega en su `fallback` 2D (mismo item, mismas props).

Esquema igual que registry_graphics (kind, track, file, media, props, dur_min/dur_rec, sfx, when/when_not) más:
  engine   "three"
  fonts3d  familias de cutkit/recursos/fuentes que html.py embebe en ck3d/assets.js para texto 3D (contornos con fontkit)
  fallback componente 2D equivalente
  cost     coste orientativo de render (Apple M4, Metal, 1080×1920, 8 subfotogramas de motion blur)
"""
from __future__ import annotations

import copy
from typing import Any

STR = {"type": "string", "minLength": 1}
ASSET_ID = {"type": "string", "minLength": 1, "description": "id de un asset del manifiesto (SVG verificado)"}


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or [], "additionalProperties": False}


RENDER = {
    "type": "object",
    "description": "ajustes del motor (opcional): motionBlur {samples 1–16, shutter 0–1}, bloom {strength, radius, "
                   "threshold}, grade {exposure, vignette, grain, ca}, dof {enabled}, msaa (0|4), shadows (bool)",
}

GRAPHICS_3D: dict[str, dict[str, Any]] = {
    "scene.logo_reveal3d": {
        "kind": "graphic", "track": "graphic", "engine": "three", "file": "../three/scenes/scene.logo_reveal3d.js",
        "media": "required", "fallback": "logo.reveal", "fonts3d": ["Montserrat"],
        "props": _obj({
            "asset": ASSET_ID,
            "name": {"type": "string", "minLength": 1, "maxLength": 14, "description": "nombre exacto (Montserrat 900, extruido)"},
            "by": {"type": "string", "maxLength": 28, "description": "autoría bajo el nombre (Montserrat 600)"},
            "color": {"type": "string", "description": "#RRGGBB del logo (por defecto, el fill del SVG)"},
            "material": {"enum": ["enamel", "metal", "glass"], "default": "enamel",
                         "description": "enamel (RECOMENDADO) = esmalte con clearcoat y cantos satinados, fiel al color de marca · "
                                        "metal / glass = EXPERIMENTALES: sobre la tinta oscura salen apagados (malva) y "
                                        "glass cuesta más (pase de transmisión)"},
            "sweep": {"type": "boolean", "default": True, "description": "barrido de luz especular sobre logo y nombre"},
            "dust": {"type": "boolean", "default": True, "description": "polvo en suspensión con bokeh"},
            "minimal": {"type": "boolean", "description": "compatibilidad con logo.reveal (se ignora en 3D)"},
            "size": {"type": "integer", "minimum": 120, "maximum": 700, "description": "alto del logo en px (pose final)"},
            "canvas": {"type": "string", "description": "compatibilidad con logo.reveal (fondo: siempre tinta de estudio)"},
            "exit": {"enum": ["cut", "fade"], "description": "cut = corte seco en t1 (lo pone normalize_spec si acaba con su layout)"},
            "render": RENDER,
            "hide_captions": {"type": "boolean"},
        }, ["asset"]),
        "dur_min": 1.0, "dur_rec": 1.5,
        "cues_doc": "name (entra el nombre; si no, t0 + 0,25 s)",
        "sfx": [{"at": "enter", "offset": 0.0, "kind": "impact"}],
        "cost": "≈ 60–110 ms/fotograma en HF con 1 worker (frente a ~50 ms sin 3D); 1,5 s ≈ 5–8 s de render extra",
        "when": "OPCIONAL, solo a petición expresa (acabado de estudio opcional): revelación de nombre/logo "
                "de herramienta a pantalla completa (broll_full) con acabado de estudio — logo SVG extruido con bisel, "
                "barrido especular, dolly-in con arco, foco que se ajusta, polvo con bokeh, nombre en Montserrat 900 con máscara",
        "when_not": "por defecto (usa logo.reveal 2D); logos que no sean SVG verificados; varios logos seguidos (minimal); "
                    "sobre la cara de la persona en cámara (es opaco a pantalla completa); más de una escena 3D por vídeo sin probar el coste",
    },
    "scene.pipeline3d": {
        "kind": "graphic", "track": "graphic", "engine": "three", "file": "../three/scenes/scene.pipeline3d.js",
        "media": "optional", "fallback": "flow.pipeline", "fonts3d": ["Montserrat"],
        "props": None,   # = las de flow.pipeline + reflow/render (se rellena abajo)
        "dur_min": 3.0, "dur_rec": 7.0,
        "cues_doc": "messy, label_top, label_top2, transform, label_bottom, output (las de flow.pipeline)",
        # mismos SFX que flow.pipeline (eventos flip/option del 3D)
        "sfx": [{"at": "transform", "offset": 0.0, "kind": "whoosh", "rel_lu": -14.0, "max_s": 0.4},
                {"at": "output", "offset": 0.0, "kind": "pop", "file": "firma_1", "pitch": 3.0, "rel_lu": -16.0,
                 "signature": "viz.decision"}],
        "cost": "≈ 60–90 ms/fotograma (8 subfotogramas, sombras VSM); 6 s ≈ 25–35 s de render con varios workers",
        "when": "versión 3D VERTICAL (a petición) de flow.pipeline: 3 fichas de papel apiladas que caen "
                "con desorden real (±8–12°, tres profundidades, cámara que orbita con paralaje), se enderezan una a una y su "
                "copia cruza por delante de la pila y por detrás del logo extruido para salir como barra de tinta en el mismo "
                "orden (DOF en la ficha que cruza, motion blur real); etiquetas espejo; reposo con push lento",
        "when_not": "por defecto (flow.pipeline 2D); más de 3 fichas/salidas; textos de ficha muy largos (<34 px)",
    },
}


def _pipeline_props() -> dict:
    """Mismas props que flow.pipeline (las define el agente de gráficos) + reflow y render del motor 3D."""
    try:
        from cutkit.motion.registry_graphics import GRAPHICS
        base = copy.deepcopy(GRAPHICS["flow.pipeline"]["props"])
    except Exception:  # noqa: BLE001
        base = {"type": "object", "properties": {}, "additionalProperties": True}
    pr = base.setdefault("properties", {})
    pr.setdefault("canvas", {"type": "string"})
    pr.setdefault("ghost", {"type": "boolean"})
    pr.setdefault("labels", {"type": "object", "properties": {"top": {"type": "string"}, "bottom": {"type": "string"}}})
    pr.setdefault("layout", {"enum": ["vertical", "row"], "description": "el 3D es siempre VERTICAL"})
    pr["reflow"] = {"type": "boolean", "description": "(versión anterior en fila; se ignora)"}
    pr["mono"] = {"type": "boolean", "description": "salidas en JetBrains Mono (por defecto Montserrat; mono automático si parecen código)"}
    pr["render"] = RENDER
    return base


GRAPHICS_3D["scene.pipeline3d"]["props"] = _pipeline_props()


def _capture_props() -> dict:
    """Unión de las props de media.capture_plane y media.slot (las define el agente de gráficos) + las del 3D."""
    props: dict = {"type": "object", "properties": {}, "additionalProperties": False}
    try:
        from cutkit.motion.registry_graphics import GRAPHICS
        from cutkit.motion.registry import COMPONENTS
        for src in (COMPONENTS.get("media.slot"), GRAPHICS.get("media.capture_plane")):
            if src and isinstance(src.get("props"), dict):
                props["properties"].update(copy.deepcopy(src["props"].get("properties", {})))
    except Exception:  # noqa: BLE001
        props["additionalProperties"] = True
    props["properties"]["yaw"] = {"type": "number", "minimum": 8, "maximum": 14, "description": "giro de entrada en Y (°)"}
    props["properties"]["render"] = RENDER
    props["properties"].setdefault("hide_captions", {"type": "boolean"})
    return props


GRAPHICS_3D["scene.capture3d"] = {
    "kind": "media", "track": "broll", "engine": "three", "file": "../three/scenes/scene.capture3d.js",
    "media": "required", "fallback": "media.capture_plane (imagen) / media.slot (vídeo)", "fonts3d": [],
    "video_frames": True,
    "props": None,
    "dur_min": 0.8, "dur_rec": 2.4,
    "cues_doc": "focus (marcador oro + empuje de cámara hacia la palabra), sheen (barrido)",
    # barrido: aire filtrado > 2 kHz (−18 LU, ≤ 0,3 s); marcador: tic suave. Eventos `sheen` / `highlight` (o sus cues)
    "sfx": [],   # sin SFX en focus/sheen (densidad ≤ 0,25/s); la entrada, por animaciones.yaml
    "cost": "≈ 40–60 ms/fotograma (6 subfotogramas, VSM); vídeo: un JPEG por fotograma cargado en el seek",
    "when": "captura o VÍDEO real (acme.example…) presentado como pantalla en el espacio: entra con perspectiva (giro "
            "8–14° Y, 4–6° X) y en ≤ 0,55 s queda casi frontal (≤ 1,5°) para leerse; canto fino, sombra blanda sobre el "
            "panel, un barrido y marcador oro + empuje a la palabra (focus). Split (panel 0–768) o broll_full (288–1240)",
    "when_not": "capturas que deben leerse desde el primer fotograma (la entrada dura 0,55 s); planos < 0,8 s; "
                "grabaciones verticales a pantalla completa (mejor media.slot)",
}


GRAPHICS_3D["scene.capture3d"]["props"] = _capture_props()
