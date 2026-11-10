"""cutkit.motion.registry — catálogo de componentes de motion para el director y el compilador.

`COMPONENTS: dict[str, dict]` → por componente:
  kind       layout | camera | media | caption | transition | overlay | graphic
  track      pista del Timeline donde va (layout/camera/broll/caption/transition/overlay/graphic)
  props      JSON Schema (draft 2020-12) de las props; validar con `validate_props(name, props)`
  dur_min / dur_rec   segundos
  sfx        eventos de sonido relativos: [{"at": "enter"|"exit"|"cut"|"<cue>", "offset": s, "kind": "whoosh|pop|…"}]
  when / when_not     criterio editorial en una línea (para el director)
  media      None | "required" | "optional" (si el item lleva items[].media)
  file       fichero JS que lo registra (components/<file>)

Los gráficos (title.*, stat.*, list.* …) los declara el otro agente en `cutkit/motion/registry_graphics.py`
(`GRAPHICS: dict[str, dict]` con el mismo esquema) y aquí se fusionan.
"""
from __future__ import annotations

import copy
from typing import Any

# ───────────────────────────────────────────────────────── piezas de esquema
NUM = {"type": "number"}
INT = {"type": "integer"}
BOOL = {"type": "boolean"}
STR = {"type": "string"}
FRAMES = {"type": "integer", "minimum": 0, "maximum": 30, "description": "fotogramas a 30 fps"}
EASE_NAME = {"enum": ["enter", "exit", "move", "pop"], "description": "uno de los 4 eases del sistema (CK.ease)"}
ENTER_LAYOUT = {"enum": ["cut", "slide"], "default": "cut",
                "description": "cut = corte seco (con transition.* encima si cambia de bloque); slide = deslizado ~5–8 f"}
POINT = {"type": "object", "properties": {"x": {"type": "number", "minimum": 0, "maximum": 1},
                                          "y": {"type": "number", "minimum": 0, "maximum": 1}},
         "required": ["x", "y"], "additionalProperties": False}
REGION = {"type": "object", "properties": {k: {"type": "number", "minimum": 0, "maximum": 1} for k in "xywh"},
          "required": ["x", "y", "w", "h"], "additionalProperties": False}
COLOR = {"type": "string", "description": "accent | accent2 | green | red | white | muted | #RRGGBB"}
MEDIA_START = {"type": "number", "minimum": 0, "description": "s de la fuente en que arranca el vídeo"}
MEDIA_EXIT = {"enum": ["cut", "fade"], "default": "cut",
              "description": "cut = corte seco; fade = se funde con el fondo del panel en sus últimos 5 f (nunca se cruza con otra pieza)"}
WORD = {
    "type": "object",
    "properties": {
        "text": STR, "t0": NUM, "t1": NUM,
        "emphasis": {"enum": [None, "accent", "brand", "hero", "scale"],
                     "description": "accent = oro · brand = color del tema (tokens.subject_color) · hero = Montserrat 800 ~1,5× en su línea (nunca serif) · scale = 1,35×"},
        "color": COLOR, "id": STR,
    },
    "required": ["text", "t0", "t1"],
}


def _obj(props: dict, required: list[str] | None = None, extra: bool = False) -> dict:
    return {"type": "object", "properties": props, "required": required or [], "additionalProperties": extra}


SFX_WHOOSH = [{"at": "cut", "offset": 0.0, "kind": "whoosh"}]

COMPONENTS: dict[str, dict[str, Any]] = {
    # ─────────────────────────── layouts
    "layout.full_face": {
        "kind": "layout", "track": "layout", "file": "layout.js", "media": None,
        "props": _obj({"enter": ENTER_LAYOUT, "reframe": {"type": "boolean", "default": True,
                        "description": "sube y escala (≤ ×1,22) el A-roll para que la barbilla quede sobre el raíl"},
                       "max_scale": {"type": "number", "minimum": 1, "maximum": 1.4}, "rail_y": INT, "chin_pad": NUM}),
        "dur_min": 0.7, "dur_rec": 2.5, "sfx": [],
        "when": "opinión, tesis, pivote («Pero…»), pregunta, confianza, novedad, estructura: la cara manda (es el layout por defecto)",
        "when_not": "si hay algo concreto que enseñar mientras se nombra (herramienta, paso, resultado)",
    },
    "layout.split_top": {
        "kind": "layout", "track": "layout", "file": "layout.js", "media": None,
        "props": _obj({
            "enter": ENTER_LAYOUT, "enter_frames": {"type": "integer", "minimum": 4, "maximum": 12, "default": 8},
            "junction_y": {"type": "integer", "minimum": 720, "maximum": 1100, "default": 1008,
                           "description": "< 860 solo con una toma de cara completa sin versión 50/50 (outro): cara a escala 1 y a todo el ancho"},
            "face_fit": {"enum": ["fill", "card"], "default": "fill"}, "face_scale": {"type": "number", "minimum": 0.6, "maximum": 1.2},
            "face_air": {"type": "integer", "minimum": 20, "maximum": 120, "default": 40, "description": "px de aire sobre el pelo en fill/card"},
            "feather": {"type": "integer", "minimum": 40, "maximum": 200, "default": 110},
            "face_shift": {"type": "integer", "minimum": 200, "maximum": 700, "description": "px que baja la cara (auto con las caras)"},
            "eyes_y": {"type": "integer", "minimum": 1150, "maximum": 1300, "default": 1250},
            "seam_opacity": {"type": "number", "minimum": 0, "maximum": 0.7, "default": 0.45},
            "panel_bg": {"enum": ["ink", "navy", "paper", "white", "accent"], "description": "o #RRGGBB; paper = crema con grano sutil"}, "grain": {"type": "number", "minimum": 0, "maximum": 0.2},
        }),
        "dur_min": 1.0, "dur_rec": 4.0, "sfx": [],
        "when": "explicar o demostrar algo mientras la persona en cámara habla (paso, captura, demo, ejemplo): recurso arriba (1080×1008), cara abajo; el subtítulo va en la junta",
        "when_not": "frases de opinión o confianza (cara completa); resultados que merecen toda la pantalla (broll_full / card_float)",
    },
    "layout.broll_full": {
        "kind": "layout", "track": "layout", "file": "layout.js", "media": None,
        "props": _obj({"enter": ENTER_LAYOUT, "aroll": {"enum": ["hide", "behind"], "default": "hide"}, "bg": COLOR,
                       "panel_bg": {"enum": ["ink", "navy", "paper", "white", "accent"], "description": "o #RRGGBB; paper = crema con grano sutil"}, "grain": {"type": "number", "minimum": 0, "maximum": 0.2},
                       "rail_y_full": {"type": "number", "minimum": 0.5, "maximum": 0.78, "default": 0.62, "description": "raíl bajo el gráfico en planos sin cara: base del texto ≤1248 (zona segura de 672 px abajo); deja 260–1110 a los gráficos"}}),
        "dur_min": 0.6, "dur_rec": 2.0, "sfx": [],
        "when": "la prueba ES la imagen (resultado generado, demo en marcha, clip) y merece la pantalla entera",
        "when_not": "en la palabra clave de una revelación o tesis (la cara se queda: ly.face_on_reveal)",
    },
    "layout.card_float": {
        "kind": "layout", "track": "layout", "file": "layout.js", "media": None,
        "props": _obj({
            "enter": ENTER_LAYOUT, "bg": {"enum": ["ink", "navy", "paper"], "default": "ink"},
            "grain": {"type": "number", "minimum": 0, "maximum": 0.2, "default": 0.09},
            "card_width": {"type": "integer", "minimum": 600, "maximum": 960, "default": 880},
            "center_y": {"type": "number", "minimum": 0.3, "maximum": 0.5, "default": 0.42},
            "max_height": {"type": "integer", "minimum": 300, "maximum": 900},
            "rail_y_full": {"type": "number", "minimum": 0.5, "maximum": 0.78, "default": 0.62, "description": "raíl bajo el gráfico en planos sin cara: base del texto ≤1248 (zona segura de 672 px abajo); deja 260–1110 a los gráficos"},
        }),
        "dur_min": 1.2, "dur_rec": 3.0, "sfx": [],
        "when": "resultado generado, recompensa o una pieza que se mira con calma: tarjeta redondeada sobre negro con grano",
        "when_not": "capturas de pasos de un tutorial (split); frases de opinión (cara)",
    },
    "layout.pip": {
        "kind": "layout", "track": "layout", "file": "layout.js", "media": None,
        "props": _obj({
            "enter": ENTER_LAYOUT, "enter_frames": FRAMES,
            "shape": {"enum": ["card", "circle"], "default": "card"},
            "position": {"enum": ["bottom_left", "bottom_right", "top_left", "top_right"], "default": "bottom_left"},
            "width": {"type": "integer", "minimum": 300, "maximum": 520, "default": 420},
            "x": INT, "y": INT, "radius": INT, "aspect": NUM, "face_fill": NUM,
        }),
        "dur_min": 1.0, "dur_rec": 3.0, "sfx": [],
        "when": "el recurso necesita la pantalla pero la reacción de la persona en cámara importa (comentar una demo, acusación sobre el recurso)",
        "when_not": "por defecto: es raro (1–2 por vídeo); nunca abajo a la derecha bajo los botones de Shorts",
    },
    # ─────────────────────────── cámara
    "camera.punch_in": {
        "kind": "camera", "track": "camera", "file": "camera.js", "media": None,
        "props": _obj({
            "scale": {"type": "number", "minimum": 1.12, "maximum": 2.0, "default": 1.3, "description": "recomendado 1,25–1,5; nunca 1,03–1,10"},
            "cut": {"type": "boolean", "default": True}, "frames": FRAMES,
            "from": {"type": "number", "minimum": 1, "maximum": 2},
            "focus": {"oneOf": [{"enum": ["face", "eyes", "chin", "center"]}, POINT], "default": "face",
                      "description": "face = barbilla en cara completa (no baja hacia el raíl), ojos en el split"},
            "ease": EASE_NAME, "blur": {"type": "number", "minimum": 0, "maximum": 4},
            "out": {"enum": ["cut", "ease", "hold"], "default": "cut"},
        }),
        "dur_min": 0.5, "dur_rec": 1.5, "sfx": [],
        "when": "énfasis prosódico, remate, cifra, o alternar escala al quitar una pausa en un plano de cara",
        "when_not": "zoom periódico sin causa (≥ 6 s entre dos sin disparador), sobre texto que se lee, dos seguidos en el mismo sentido",
    },
    "camera.slow_push": {
        "kind": "camera", "track": "camera", "file": "camera.js", "media": None,
        "props": _obj({
            "mode": {"enum": ["breath", "expressive"], "default": "breath"},
            "amount": {"type": "number", "minimum": 0.01, "maximum": 0.16},
            "from": NUM, "to": NUM, "direction": {"enum": ["in", "out"], "default": "in"},
            "ease": EASE_NAME, "focus": {"oneOf": [{"enum": ["face", "eyes", "chin", "center"]}, POINT]},
            "out": {"enum": ["cut", "hold"], "default": "cut"}, "force": BOOL, "hold_end": NUM,
        }),
        "dur_min": 0.9, "dur_rec": 3.5, "sfx": [],
        "when": "frase a cara de 3–6 s que necesita vida (respiración 1,00→1,06) o una tesis que sube (expresivo 1,00→1,16 en 0,9–2,3 s)",
        "when_not": "cara del split (va fija), > 40 % del vídeo con cámara moviéndose, frases sagradas",
    },
    "camera.reframe": {
        "kind": "camera", "track": "camera", "file": "camera.js", "media": None,
        "props": _obj({
            "target": POINT, "scale": {"type": "number", "minimum": 1, "maximum": 2.0, "default": 1.15},
            "frames": FRAMES, "ease": EASE_NAME, "out": {"enum": ["cut", "ease", "hold"], "default": "cut"},
        }),
        "dur_min": 0.8, "dur_rec": 2.5, "sfx": [],
        "when": "dejar sitio a un gráfico al lado de la cara o encuadre de segundo ángulo",
        "when_not": "si un layout ya resuelve el sitio (split, pip)",
    },
    # ─────────────────────────── media
    "media.full": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "fit": {"enum": ["cover", "contain"], "default": "cover"}, "position": STR, "bg": COLOR,
            "enter": {"enum": ["cut", "fade", "zoom"], "default": "cut"},
            "kb": {"type": "number", "minimum": 0, "maximum": 0.1, "default": 0.04}, "kb_dir": {"enum": ["in", "out"]},
        }),
        "dur_min": 0.6, "dur_rec": 2.0, "sfx": [],
        "when": "B-roll a pantalla completa (con layout.broll_full) — muestra literal de lo que se dice",
        "when_not": "capturas con texto pequeño (mejor tarjeta o ui_focus)",
    },
    "media.slot": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "fit": {"enum": ["cover", "contain"], "default": "cover"}, "position": STR, "radius": INT,
            "enter": {"enum": ["auto", "cut"], "default": "auto"}, "settle": BOOL,
            "kb": {"type": "number", "minimum": 0, "maximum": 0.08}, "kb_dir": {"enum": ["in", "out"]},
            "media_start": MEDIA_START, "exit": MEDIA_EXIT,
            "frame": {"type": "boolean", "default": True,
                      "description": "en broll_full con fit contain, una captura/vídeo real lleva el marco de las capturas a pantalla completa (el de scene.capture3d: esquina 10 px, filo claro de 2 px, sombra), a 950 px de ancho centrada en 288–1240; false lo quita"},
        }),
        "dur_min": 0.8, "dur_rec": 2.4, "sfx": [],
        "when": "el recurso del layout activo: mitad superior del split (cover + junta), tarjeta en card_float, pantalla en broll_full/pip",
        "when_not": "si el recurso necesita marco propio (screenshot_card, device) o enfocar una zona (ui_focus)",
    },
    "media.screenshot_card": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "width": {"type": "integer", "minimum": 400, "maximum": 1000}, "radius": INT, "position": STR,
            "enter_frames": FRAMES, "parallax": BOOL, "sheen": BOOL,
        }),
        "dur_min": 1.2, "dur_rec": 2.8, "sfx": [{"at": "enter", "offset": 0.0, "kind": "whoosh"}],
        "when": "captura web real (prueba de credibilidad, titular, página oficial) que se lee de un vistazo",
        "when_not": "capturas inventadas o con texto ilegible a 1080 px; más de 3 tarjetas seguidas",
    },
    "media.scroll": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "stops": {"type": "array", "items": {"type": "number", "minimum": 0, "maximum": 1}, "minItems": 2},
            "move_s": {"type": "number", "minimum": 0.4, "maximum": 3}, "hold_start": NUM, "hold_end": NUM,
            "width": INT, "height": INT, "radius": INT, "ease": EASE_NAME,
            "speed": {"enum": ["slow", "normal", "fast"], "default": "normal"},
            "frame": {"enum": ["card", "phone", "none"], "default": "card"},
        }),
        "dur_min": 2.0, "dur_rec": 3.5, "sfx": [],
        "when": "idea larga con un único referente (página, documento, lista) o «muchísimo/meses» de contenido",
        "when_not": "si hay que leer algo concreto (para y enfoca con ui_focus)",
    },
    "media.ui_focus": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "region": REGION, "zoom": {"type": "number", "minimum": 1.0, "maximum": 3.5,
                                       "description": "manda sobre el encaje de la región; sin él, 2,4 limitado a que la región quepa"},
            "delay": NUM, "zoom_frames": FRAMES, "dim": {"type": "number", "minimum": 0, "maximum": 0.85},
            "color": {"type": ["string", "null"], "description": "color del anillo (accent…); null = sin anillo"},
            "width": INT, "radius": INT, "enter": {"enum": ["auto", "cut"], "default": "auto"},
            "media_start": MEDIA_START, "exit": MEDIA_EXIT,
            "zoom_lead": {"type": "number", "minimum": 0, "maximum": 1.0, "default": 0.35,
                          "description": "s que el zoom arranca ANTES de la cue `focus`: el anillo queda dibujado ≤ 6 f después de la palabra"},
            "ring": {"type": "boolean", "default": True, "description": "false = zoom limpio: sin anillo ni oscurecido"},
            "ring_frames": {"type": "integer", "minimum": 4, "maximum": 14, "default": 6},
            "start_framed": {"type": "boolean", "default": False,
                             "description": "el plano abre ya encuadrado en la región (sin zoom de entrada); anillo/oscurecido en la cue"},
            "freeze_at_focus": {"type": "boolean", "default": False,
                                "description": "el vídeo se congela en el fotograma de la cue `focus` (compile.py crea la copia congelada)"},
            "bleed": {"type": "boolean", "default": False,
                      "description": "solo en broll_full, la captura A SANGRE: ocupa el lienzo entero "
                                     "(1080 de ancho, centrada en vertical, alto = 1080/aspecto hasta 1920), sin marco ni esquinas, y el "
                                     "subtítulo va encima, como en las VSL. Pide un recorte vertical (aspecto 0,56–0,8) de una interfaz "
                                     "OSCURA (el subtítulo blanco tiene que leerse encima); el zoom lleva la región al centro del lienzo"},
            "badge": {"type": "string", "description": "id de un logo que va en `assets` DESPUÉS de la captura; baldosa blanca en la esquina de arriba a la izquierda de la tarjeta (no en `bleed`)"},
            "sfx_skip": {"type": "array", "items": {"type": "string"}, "description": "«evento:n» sin SFX (n desde 0), p. ej. «media.ring:0»"},
            "sfx_rel": {"type": "object", "additionalProperties": {"type": "number"}, "description": "nivel propio (LU) por evento"},
            "card_h": {"type": "number", "minimum": 120, "maximum": 1000,
                       "description": "alto de la tarjeta (px, sin `bleed`) aunque la imagen a su ancho sea más baja; la cámara entra lo justo para cubrirla (zoom ≥ card_h / alto). Sin la prop, el alto de la imagen"},
            "card_cy": {"type": "number", "minimum": 288, "maximum": 1240,
                        "description": "y del lienzo del centro de la tarjeta (sin `bleed`), dentro de 288–1240. Sin la prop, centrada en esa banda"},
            "badge_pos": {"type": "string", "enum": ["corner", "above"],
                          "description": "`above` = la baldosa del `badge` ENTERA encima de la tarjeta (no tapa el texto de una tira baja); por defecto, en la esquina"},
            "pile": {"type": "array", "minItems": 1, "maxItems": 4, "items": {"type": "object", "properties": {
                "asset": {"type": "string", "description": "id de la captura (en `assets`)"},
                "badge": {"type": "string", "description": "id del logo de la app (en `assets`)"},
                "in": {"type": "string", "description": "cue en que entra (la primera, en el t0 del item)"},
                "ring": {"type": "string", "description": "cue en que se dibuja su aro (por fuera del borde)"}},
                "required": ["asset"], "additionalProperties": False},
                "description": "PILA de capturas reales que se acumulan en vez de sustituirse. Cada una entra en su cue `in` a ancho completo con su logo encima y empuja las anteriores hacia arriba (reducidas a `pile_prev`, con el logo al lado); el aro oro, por fuera del borde (no pisa el texto), en su cue `ring`. Todo en 288–`pile_bottom`. `region` y `zoom` no se usan. Sin la prop, nada cambia"},
            "pile_prev": {"type": "number", "minimum": 0.4, "maximum": 0.8, "description": "pila: escala de las capturas anteriores (0,6)"},
            "pile_logo": {"type": "number", "minimum": 96, "maximum": 240, "description": "pila: lado de la baldosa del logo de la captura actual (180; baja sola hasta 96 si no cabe)"},
            "pile_bottom": {"type": "number", "minimum": 700, "maximum": 1240, "description": "pila: borde de abajo (1000: a ancho completo, nada baja a la columna de botones)"},
            "overlap_in": {"type": "integer", "minimum": 1, "maximum": 6, "description": "compile.py: entra N f antes de que acabe la salida de la pieza anterior del mismo panel. Sin la prop, nada cambia"},
            "preroll": {"type": "integer", "minimum": 1, "maximum": 6, "description": "runtime: el reloj de la animación arranca N f antes del t0 (visible desde su t0). Sin la prop, nada cambia"},
            "path": {"type": "array", "minItems": 1, "maxItems": 10, "items": {"type": "object", "properties": {
                "cue": {"type": "string", "description": "cue (en `cues`) en que llega la parada"},
                "frame": REGION, "ring": {"anyOf": [REGION, {"type": "null"}]},
                "zoom": {"type": "number", "minimum": 1.0, "maximum": 3.5}, "frames": FRAMES},
                "required": ["cue"], "additionalProperties": False},
                "description": "después del foco, la cámara recorre la MISMA captura o vídeo parada a parada, cada una en su cue (arranca `zoom_lead` antes): encuadre `frame` (por defecto, su `ring`) con su `zoom`; el anillo y el oscurecido pasan a `ring` (null = esa parada sin anillo). Sin la prop, nada cambia"},
        }, ["region"]),
        "dur_min": 1.8, "dur_rec": 3.0, "sfx": [{"at": "focus", "offset": 0.0, "kind": "click"}],
        "when": "un dato o botón concreto dentro de una interfaz real (cue `focus` = palabra que lo nombra)",
        "when_not": "regiones inventadas: la región debe salir de la captura real (OCR o selector)",
    },
    "media.device": {
        "kind": "media", "track": "broll", "file": "media.js", "media": "required",
        "props": _obj({
            "device": {"enum": ["browser", "phone"], "default": "browser"}, "url": STR,
            "width": INT, "height": INT, "position": STR, "kb": NUM,
        }),
        "dur_min": 1.5, "dur_rec": 3.0, "sfx": [{"at": "enter", "offset": 0.0, "kind": "whoosh"}],
        "when": "grabación o captura de una web/app real que gana contexto con su marco (navegador o móvil)",
        "when_not": "si la URL no es real (no se inventa); si el marco resta tamaño a algo que hay que leer",
    },
    # ─────────────────────────── subtítulos
    "caption.rail": {
        "kind": "caption", "track": "caption", "file": "caption.js", "media": None,
        "props": _obj({
            "words": {"type": "array", "items": WORD, "minItems": 1, "maxItems": 4},
            "pages": {"type": "array", "items": _obj({"t0": NUM, "t1": NUM, "words": {"type": "array", "items": WORD}}, ["words"], True)},
            "y": {"type": "number", "minimum": 0.4, "maximum": 0.65},
            "rail": {"enum": ["auto", "fixed"], "default": "auto"},
            "size": {"type": "integer", "minimum": 48, "maximum": 72, "default": 58},
            "case": {"enum": ["as_is", "lower", "upper"], "default": "as_is"},
            "reveal": {"enum": ["word", "page"], "default": "word"},
            "plate": {"enum": ["none", "pill"], "default": "none"}, "lead_frames": FRAMES,
            "build": {"enum": ["center", "in_place"], "default": "center",
                      "description": "center = la línea se recentra en x=540 a medida que aparecen palabras"},
        }),
        "dur_min": 0.2, "dur_rec": 0.9, "sfx": [],
        "when": "siempre (página de 1–3 palabras); como mucho 1 destacada por frase",
        "when_not": "mientras un lockup o gráfico ya dice esas palabras (caption.hide)",
    },
    "caption.lockup": {
        "kind": "caption", "track": "caption", "file": "caption.js", "media": None,
        "props": _obj({
            "words": {"type": "array", "items": WORD, "minItems": 1},
            "lines": {"type": "array", "items": _obj({"text": STR, "t0": NUM, "t1": NUM, "weight": {"enum": ["bold", "light", "black"]}, "color": COLOR}, ["text"])},
            "hero": _obj({"text": STR, "t0": NUM, "t1": NUM, "color": COLOR}, ["text"]),
            "hero_position": {"enum": ["below", "above"], "default": "below"},
            "hero_color": COLOR, "hero_size": INT, "big_size": INT,
            "y": NUM, "anchor": {"oneOf": [{"enum": ["auto", "face", "top", "rail", "seam", "center"]}, {"type": "number"}],
                                "description": "auto: seam en split, face (bajo la boca, en el raíl) en cara completa, rail en el resto"},
            "align": {"enum": ["center", "left", "right"], "default": "center"},
            "size": {"type": "integer", "minimum": 48, "maximum": 90, "default": 62},
            "max_chars": INT, "stagger_align": BOOL, "light_second": BOOL,
            "exit": {"enum": ["cut", "soft"], "default": "cut"},
        }),
        "dur_min": 1.0, "dur_rec": 2.2, "sfx": [],
        "when": "la frase-gancho o la frase clave (4–5 por vídeo, casi siempre en el hook): conectores en Montserrat 800 + 1 palabra héroe en Montserrat 900 ~1,75× (nunca serif)",
        "when_not": "frases sin una palabra que pese; dos lockups seguidos",
    },
    # ─────────────────────────── transiciones (item t0–t1 ≤ 0,4 s; cue `cut` = corte editorial)
    "transition.light_leak": {
        "kind": "transition", "track": "transition", "file": "transition.js", "media": None,
        "props": _obj({
            "frames": {"type": "integer", "minimum": 6, "maximum": 8, "default": 7},
            "palette": {"enum": ["dorado", "iris", "rojo", "rosa", "plata"], "default": "dorado"},
            "direction": {"enum": ["left", "right"], "default": "right"},
            "intensity": {"type": "number", "minimum": 0.4, "maximum": 1.0}, "burn": BOOL,
            "peak": {"type": "number", "minimum": 0.05, "maximum": 0.88, "description": "opacidad máxima a mano (0,35 = luz discreta)"},
        }),
        "dur_min": 0.2, "dur_rec": 0.27, "sfx": [{"at": "cut", "offset": -0.03, "kind": "whoosh"}],
        "when": "cambio de bloque narrativo o de layout (vuelta a cara para opinión, nombre de la herramienta)",
        "when_not": "dentro del mismo bloque o a mitad de frase; < 2,5 s después de otra transición con luz",
    },
    "transition.flash": {
        "kind": "transition", "track": "transition", "file": "transition.js", "media": None,
        "props": _obj({"color": STR, "peak": {"type": "number", "minimum": 0.3, "maximum": 1}, "bloom": BOOL}),
        "dur_min": 0.17, "dur_rec": 0.23, "sfx": [{"at": "cut", "offset": 0.0, "kind": "transicion_luz"}],
        "when": "golpe: vuelta tras silencio o confidencia, antes→después, cifra que impacta",
        "when_not": "sin sonido ni causa; > 3 destellos por segundo (WCAG)",
    },
    "transition.whip": {
        "kind": "transition", "track": "transition", "file": "transition.js", "media": None,
        "props": _obj({
            "frames": {"type": "integer", "minimum": 3, "maximum": 5, "default": 4},
            "direction": {"enum": ["left", "right", "up", "down"], "default": "left"},
            "blur": {"type": "number", "minimum": 12, "maximum": 48}, "travel": INT,
        }),
        "dur_min": 0.1, "dur_rec": 0.13, "sfx": SFX_WHOOSH,
        "when": "giro con energía («pero…», salir de cámara), siempre en la dirección del relato (adelante = izquierda)",
        "when_not": "dirección contraria a la anterior sin motivo; dentro del mismo layout",
    },
    "transition.zoom_blur": {
        "kind": "transition", "track": "transition", "file": "transition.js", "media": None,
        "props": _obj({
            "frames": {"type": "integer", "minimum": 4, "maximum": 8, "default": 6},
            "scale": {"type": "number", "minimum": 1.1, "maximum": 1.35}, "blur": {"type": "number", "minimum": 6, "maximum": 16},
            "focus": {"oneOf": [{"enum": ["face", "center"]}, POINT]},
        }),
        "dur_min": 0.15, "dur_rec": 0.2, "sfx": SFX_WHOOSH,
        "when": "juicio u opinión que entra a cara (con punto focal claro)",
        "when_not": "sin punto focal; más de 2 por minuto",
    },
    "transition.glitch": {
        "kind": "transition", "track": "transition", "file": "transition.js", "media": None,
        "props": _obj({"frames": {"type": "integer", "minimum": 3, "maximum": 6, "default": 5},
                       "rgb_offset": {"type": "number", "minimum": 6, "maximum": 14}}),
        "dur_min": 0.1, "dur_rec": 0.17, "sfx": [{"at": "cut", "offset": 0.0, "kind": "glitch"}],
        "when": "paso de ítem en un vídeo de tono técnico (raro: ≤ 2 por vídeo)",
        "when_not": "como maquillaje o en cada cambio",
    },
    # ─────────────────────────── overlays
    "overlay.grain": {
        "kind": "overlay", "track": "overlay", "file": "overlay.js", "media": None,
        "props": _obj({
            "opacity": {"type": "number", "minimum": 0.02, "maximum": 0.16, "default": 0.05},
            "fps": {"type": "integer", "minimum": 6, "maximum": 24, "default": 12},
            "blend": {"enum": ["normal", "overlay", "soft-light", "screen", "multiply"], "default": "normal"},
            "area": {"oneOf": [{"enum": ["slot", "full"]}, _obj({k: NUM for k in "xywh"}, ["x", "y", "w", "h"])]},
            "seed": {"type": ["string", "integer"]}, "freq": NUM,
        }),
        "dur_min": 0.5, "dur_rec": 3.0, "sfx": [],
        "when": "fondos y tarjetas (textura de las referencias) — card_float ya lo trae",
        "when_not": "sobre la cara (por defecto se recorta al slot del layout)",
    },
    "overlay.vignette": {
        "kind": "overlay", "track": "overlay", "file": "overlay.js", "media": None,
        "props": _obj({"strength": {"type": "number", "minimum": 0.1, "maximum": 0.6, "default": 0.25},
                       "shape": STR, "fade_frames": FRAMES}),
        "dur_min": 0.5, "dur_rec": 3.0, "sfx": [],
        "when": "B-roll a pantalla completa que necesita foco central",
        "when_not": "sobre la junta del split",
    },
}

# ───────────────────────────────────────────────────────── fusión con los gráficos del otro agente
try:  # pragma: no cover - depende de otro módulo
    from cutkit.motion.registry_graphics import GRAPHICS as _GRAPHICS  # type: ignore
except Exception:  # noqa: BLE001
    _GRAPHICS = {}
try:  # pragma: no cover - gráficos editoriales (stat/chart/timeline/progress/callout/keyword/quote/lower_third/section)
    from cutkit.motion.registry_graphics_extra import GRAPHICS_EXTRA as _GRAPHICS_EXTRA  # type: ignore
    _GRAPHICS = {**(_GRAPHICS or {}), **{k: v for k, v in _GRAPHICS_EXTRA.items() if k not in (_GRAPHICS or {})}}
except Exception:  # noqa: BLE001
    pass
try:  # pragma: no cover - componentes con sujeto recortado por fotograma (mate de Vision: title.behind_subject)
    from cutkit.motion.registry_subject import GRAPHICS_SUBJECT as _GRAPHICS_SUBJECT  # type: ignore
    _GRAPHICS = {**(_GRAPHICS or {}), **{k: v for k, v in _GRAPHICS_SUBJECT.items() if k not in (_GRAPHICS or {})}}
except Exception:  # noqa: BLE001
    pass
try:  # pragma: no cover - escenas 3D/WebGL OPCIONALES (cutkit/motion/three; se activan cambiando el component)
    from cutkit.motion.registry_three import GRAPHICS_3D as _GRAPHICS_3D  # type: ignore
    _GRAPHICS = {**(_GRAPHICS or {}), **{k: v for k, v in _GRAPHICS_3D.items() if k not in (_GRAPHICS or {})}}
except Exception:  # noqa: BLE001
    pass
for _name, _spec in (_GRAPHICS or {}).items():
    if _name not in COMPONENTS:
        _s = dict(_spec)
        _s.setdefault("kind", "graphic")
        _s.setdefault("track", "graphic")
        _s.setdefault("sfx", [])
        _s.setdefault("media", None)
        COMPONENTS[_name] = _s


def get(name: str) -> dict[str, Any]:
    if name not in COMPONENTS:
        raise KeyError(f"componente desconocido: {name}")
    return COMPONENTS[name]


def validate_props(name: str, props: dict) -> list[str]:
    """Lista de errores (vacía = válido). Usa jsonschema si está instalado."""
    spec = COMPONENTS.get(name)
    if spec is None:
        return [f"componente desconocido: {name}"]
    schema = spec.get("props") or {"type": "object"}
    try:
        import jsonschema  # type: ignore
    except Exception:  # noqa: BLE001
        return []
    v = jsonschema.Draft202012Validator(schema)
    return [f"{name}: {'/'.join(map(str, e.path)) or '(raíz)'}: {e.message}" for e in v.iter_errors(props or {})]


def sfx_events(name: str, t0: float, t1: float, cues: dict | None = None) -> list[dict]:
    """Eventos de SFX del componente en segundos de programa (para el planificador de audio)."""
    out = []
    cues = cues or {}
    for ev in COMPONENTS.get(name, {}).get("sfx", []):
        at = ev.get("at", "enter")
        base = t0 if at == "enter" else t1 if at == "exit" else cues.get(at, cues.get("cut", t0))
        out.append({"t": round(base + float(ev.get("offset", 0.0)), 4), "kind": ev.get("kind", "whoosh")})
    return out


def catalog_for_director() -> list[dict]:
    """Resumen compacto (nombre, kind, when, when_not, dur_rec) para el prompt del director."""
    return [{"name": n, "kind": s.get("kind"), "dur_rec": s.get("dur_rec"), "when": s.get("when"), "when_not": s.get("when_not")}
            for n, s in sorted(COMPONENTS.items())]


def schema_copy(name: str) -> dict:
    return copy.deepcopy(get(name).get("props") or {})
