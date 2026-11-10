"""cutkit.motion.registry_subject — componentes que necesitan al SUJETO RECORTADO por fotograma (mate de Apple Vision,
cutkit/tools/matte.py). Lo fusiona `registry.py` igual que los demás registros.

Claves extra del esquema:
  matte      True → html.py calcula (o reutiliza de la caché clientes/<cliente>/creativos/<fecha>_<slug>/edicion/media/mattes/<hash>/) el recorte RGBA del
             sujeto para el tramo del item y lo inyecta en props._matte + <img> de precarga
  matte_res  ancho de FUENTE al que se guardan los recortes (1260 ≈ 0,875 de 1440: nítido hasta ×1,15 de escala)
  cost       coste orientativo (Apple M4)
"""
from __future__ import annotations

from typing import Any

STR = {"type": "string", "minLength": 1}
COLOR = {"type": "string", "pattern": "^#[0-9A-Fa-f]{6}$"}

GRAPHICS_SUBJECT: dict[str, dict[str, Any]] = {
    "title.behind_subject": {
        "kind": "graphic", "track": "graphic", "file": "title.behind_subject.js", "media": None,
        "matte": True, "matte_res": 1260,
        "props": {"type": "object", "additionalProperties": False, "required": ["text"], "properties": {
            "text": {"type": "string", "minLength": 1, "maxLength": 12,
                     "description": "palabra exacta (nombre de la herramienta): Montserrat 900, ~930 px de ancho, blanca"},
            "by": {"type": "string", "maxLength": 28, "description": "autoría encima del título (Montserrat 700, 44 px)"},
            "panel_bg": {**COLOR, "default": "#F386A1", "description": "lienzo (color de marca del tema)"},
            "color": {**COLOR, "default": "#FFFFFF"},
            "subject": {"enum": ["auto", "aroll", "lowered", "none"], "default": "auto",
                        "description": "auto = encuadre del A-roll si el título cabe encima de la cabeza; si no, «lowered» "
                                       "(sujeto a ancho de lienzo y bajado hasta que el pelo tape la base del título, como "
                                       "en un titular de revista). none = sin sujeto (lienzo + título)"},
            "subject_scale": {"type": "number", "minimum": 0.7, "maximum": 1.4, "default": 1.0,
                              "description": "ancho del sujeto en «lowered» (1 = fuente a ancho de lienzo)"},
            "subject_dy": {"type": "integer", "minimum": -400, "maximum": 400, "description": "ajuste vertical extra (px)"},
            "title_y": {"type": "integer", "minimum": 200, "maximum": 900, "default": 340,
                        "description": "y de la parte superior de las letras"},
            "width": {"type": "integer", "minimum": 500, "maximum": 960, "default": 930, "description": "ancho de tinta del título"},
            "overlap": {"type": "number", "minimum": 0, "maximum": 0.5, "default": 0.18,
                        "description": "fracción de la altura de mayúscula que tapa el pelo (solo «lowered»)"},
            "halo": {"type": "boolean", "default": True}, "parallax": {"type": "boolean", "default": True},
            "shadow": {"type": "boolean", "default": True},
            "exit": {"enum": ["cut"], "default": "cut"},
            "hide_captions": {"type": "boolean"},
        }},
        "dur_min": 1.0, "dur_rec": 1.5,
        "cues_doc": "name (sube el título: cue − 0,155 s, 2 f de anticipación + 9 f expo.out)",
        "sfx": [{"at": "name", "offset": -0.05, "kind": "impact"}],
        "cost": "mate: ~1 s/fotograma la primera vez (Vision 65 ms + refinado), luego caché; render ≈ el de un gráfico 2D",
        "when": "revelación del NOMBRE (una palabra) con la persona en cámara presente: título enorme sobre el color de marca, detrás de la persona "
                "recortado (título detrás del sujeto). Layout full_face (la persona sigue en pantalla); salida en corte seco a la cara",
        "when_not": "frases largas (>12 caracteres); planos sin la persona en cámara o con varias personas; si el mate falla (cae a lienzo + "
                    "título sin sujeto); dos veces seguidas en el mismo vídeo",
    },
}
