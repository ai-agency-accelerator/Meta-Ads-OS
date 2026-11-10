"""cutkit.motion.registry_graphics_extra — catálogo de los gráficos EDITORIALES (cifras, datos, secuencias, señalar,
destacar, citar, rotular y abrir bloques). Lo fusiona `registry.py` igual que `registry_graphics.GRAPHICS`.

Mismo esquema: kind, track, file, media, props (JSON Schema), dur_min/dur_rec (s),
sfx ([{"at": "enter"|"exit"|"<cue>", "offset": s, "kind": …}]), when/when_not.

Reglas comunes (las aplica el JS con los kits `CK.gx` + `CK.gxx`, ver components/<nombre>.js):
- Contenido en ctx.slot ∩ zona segura; texto clave ≥ 48 px; un foco por momento; salida limpia 1 f antes de t1.
- Entradas power3.out ~7 f (héroe expo.out), salidas power2.in ~4–5 f; `back` solo para asentar marcas/logos.
- Seek-safe: sin callbacks; los conteos son tiras de dígitos (stat.big_number) o innerText+snap (progress.bar).
- NUNCA inventan datos: todo texto y toda cifra llegan por props, con `source` (fuente registrada) cuando es un dato.
- Color con significado (`tone`): accent (marca/oro), money (verde), time (azul), red (pérdida/error), brand (color del tema).
- `backdrop`: none|black|navy|paper; en cara completa se pinta a sangre del lienzo; «auto» = navy si hace falta campo limpio.
"""
from __future__ import annotations

from typing import Any

STR = {"type": "string", "minLength": 1}
NUM = {"type": "number"}
INT = {"type": "integer"}
BOOL = {"type": "boolean"}
TONE = {"type": "string", "description": "accent | money | time | red | white | brand | #RRGGBB (color con significado)"}
ANCHOR = {"oneOf": [{"enum": ["auto", "top", "center", "bottom"]}, {"type": "number", "minimum": 0, "maximum": 1}],
          "description": "colocación vertical en el área (número = centro en fracción del lienzo)"}
BACKDROP = {"enum": ["none", "black", "navy", "paper"], "default": "none", "description": "fondo a sangre (si el layout no lo da)"}
BACKDROP_AUTO = {"enum": ["auto", "none", "black", "navy", "paper"], "default": "auto",
                 "description": "auto = navy en cara completa (campo limpio para leer datos), none en split/tarjeta"}
SOURCE = {"type": "string", "minLength": 1, "description": "fuente registrada del dato (no se muestra; stat.big_number la pinta solo con show_source: true): frase de quien habla, URL, fichero"}
POINT = {"type": "object", "properties": {"x": {"type": "number", "minimum": 0, "maximum": 1},
                                          "y": {"type": "number", "minimum": 0, "maximum": 1}},
         "required": ["x", "y"], "additionalProperties": False}
COMMON = {"hide_captions": BOOL,
          "sfx_skip": {"type": "array", "items": {"type": "string"}, "description": "«evento:n» sin SFX (n desde 0)"},
          "sfx_rel": {"type": "object", "additionalProperties": {"type": "number"}, "description": "nivel propio por evento (LU)"}}


def _obj(props: dict, required: list[str] | None = None) -> dict:
    p = dict(COMMON)
    p.update(props)
    return {"type": "object", "properties": p, "required": required or [], "additionalProperties": False}


def _g(file: str, props: dict, dur_min: float, dur_rec: float, sfx: list, when: str, when_not: str, media: str | None = None) -> dict:
    return {"kind": "graphic", "track": "graphic", "file": file, "media": media, "props": props,
            "dur_min": dur_min, "dur_rec": dur_rec, "sfx": sfx, "when": when, "when_not": when_not}


GRAPHICS_EXTRA: dict[str, dict[str, Any]] = {
    "stat.big_number": _g(
        "stat.big_number.js",
        _obj({
            "value": NUM, "decimals": {"type": "integer", "minimum": 0, "maximum": 2},
            "prefix": {"type": "string", "maxLength": 3, "description": "«+», «$», «−»"},
            "suffix": {"type": "string", "maxLength": 12, "description": "«%», «€», «mill», «MESES» (unidad, sale a la vez)"},
            "kicker": STR, "label": STR, "tail": {"type": "string", "description": "coletilla en Montserrat 900 («construyendo»), hasta 2 líneas"},
            "style": {"enum": ["serif", "sans"], "default": "sans", "description": "sin efecto (nunca serif): la cifra va siempre en Montserrat 900; «serif» se acepta para los planes antiguos"},
            "tone": TONE, "group": {"enum": ["dot", "rae", "none"], "default": "dot"},
            "roll": {"type": "boolean", "default": True, "description": "false = sin cuentakilómetros (cifras que no deben «contar», p. ej. años)"},
            "anchor": ANCHOR, "align": {"enum": ["center", "left"], "default": "center"},
            "size": {"type": "integer", "minimum": 160, "maximum": 360}, "backdrop": BACKDROP, "source": SOURCE,
            "show_source": {"type": "boolean", "default": False, "description": "pinta la fuente bajo la cifra (por defecto, no)"},
        }, ["value", "source"]),
        1.4, 2.5, [],   # sin ticks: quien habla dice la cifra a la vez (catálogo SFX → cifra_cuenta.prohibido)
        "cifra concreta que quien habla dice (tracción, dinero, tiempo, esfuerzo): «+5 millones», «7 meses», «2.000 €»; Montserrat 900, color por tipo",
        "cifras vagas («millones», «muchísimo»), dos cifras a la vez (→ chart.bar), una cifra que quien habla no dice o sin fuente",
    ),
    "chart.bar": _g(
        "chart.bar.js",
        _obj({
            "items": {"type": "array", "minItems": 2, "maxItems": 5, "items": {
                "type": "object", "properties": {"label": STR, "value": {"type": "number", "minimum": 0}, "highlight": BOOL},
                "required": ["label", "value"], "additionalProperties": False}},
            "unit": {"type": "string", "maxLength": 8}, "decimals": {"type": "integer", "minimum": 0, "maximum": 2},
            "title": STR, "tone": TONE, "max": {"type": "number", "exclusiveMinimum": 0}, "group": {"enum": ["dot", "rae", "none"]},
            "anchor": ANCHOR, "backdrop": BACKDROP_AUTO, "source": SOURCE,
            "keep_start": BOOL,
            "band": {"enum": ["safe", "center"], "description": "safe = zona segura clásica (696 px centrados bajo y=1000); center = banda centrada"},
            "exit": {"enum": ["fade", "cut"], "description": "cut = acaba en el corte de plano, sin salida animada"},
            "title_lines": {"enum": [1, 2], "description": "2 = el título puede partirse en dos líneas equilibradas"},
            "measure": {"type": "array", "maxItems": 3, "items": {"type": "object", "properties": {
                "row": {"type": "integer", "minimum": 0, "maximum": 4}, "cue": STR, "label": STR},
                "required": ["row"], "additionalProperties": False},
                "description": "la barra destacada como medida: en su cue, la barra `row` se llena de tramos en oro del largo de la "
                               "destacada (2 = la mitad, 5 = una quinta parte); `label` = nota en oro junto al rótulo de la destacada; evento measure"},
        }, ["items", "source"]),
        2.5, 4.0, [],
        "comparar 2–5 cosas con cifras reales («a mano 6 h, con cutkit 30 min»): barras desde 0, una destacada (un foco)",
        "series temporales (chart.line), > 5 categorías, diferencias del 2 %, cifras de esquema o inventadas",
    ),
    "chart.line": _g(
        "chart.line.js",
        _obj({
            "points": {"type": "array", "minItems": 4, "maxItems": 24, "items": {
                "type": "object", "properties": {"x": {"type": ["string", "number"]}, "y": NUM}, "required": ["y"], "additionalProperties": False}},
            "unit": {"type": "string", "maxLength": 8}, "decimals": {"type": "integer", "minimum": 0, "maximum": 2},
            "title": STR, "tone": TONE, "y_from_zero": {"type": "boolean", "default": True},
            "hide_value": {"type": "boolean", "description": "esquema sin cifras: sin valor final (la curva usa todo el alto)"},
            "events": {"type": "array", "maxItems": 2, "items": {
                "type": "object", "properties": {"index": {"type": "integer", "minimum": 0}, "text": STR},
                "required": ["index", "text"], "additionalProperties": False}},
            "labels": {"enum": ["ends", "none"], "default": "ends"}, "group": {"enum": ["dot", "rae", "none"]},
            "anchor": ANCHOR, "backdrop": BACKDROP_AUTO, "source": SOURCE,
        }, ["points", "source"]),
        3.0, 4.5, [],
        "tendencia o punto de inflexión de UNA serie real (crecimiento, caída): la línea se dibuja y el último valor sube grande",
        "< 4 puntos (stat.big_number / chart.bar), más de una serie, datos sin fuente, suavizar curvas",
    ),
    "timeline.steps": _g(
        "timeline.steps.js",
        _obj({
            "steps": {"type": "array", "minItems": 2, "maxItems": 5, "items": {
                "type": "object", "properties": {"label": STR, "sub": STR, "marker": {"type": "string", "maxLength": 6}},
                "required": ["label"], "additionalProperties": False}},
            "title": STR, "marker": {"enum": ["number", "dot", "text"], "default": "number"},
            "title_px": {"type": "integer", "minimum": 52, "maximum": 140, "description": "cuerpo máximo del título (72 por defecto)"},
            "title_wide": {"type": "boolean", "description": "en la «T» de pantalla completa el título (arriba, sobre y=1000) usa los 950 px"},
            "label_px": {"type": "integer", "minimum": 44, "maximum": 96, "description": "cuerpo máximo de los rótulos"},
            "label_lines": {"enum": [1, 2], "description": "1 = cada rótulo en una línea (mismo cuerpo para todos)"},
            "recenter": {"type": "boolean", "description": "lo ya dicho (título + pasos) queda centrado en el ancla; el bloque sube al sumarse cada paso"},
            "rail_gap": {"type": "integer", "minimum": 0, "maximum": 300, "description": "px libres entre el borde inferior del bloque y el raíl de subtítulos (80 por defecto; si no cabe, el bloque se compacta)"},
            "tone": TONE, "anchor": ANCHOR, "backdrop": BACKDROP_AUTO, "source": STR,
        }, ["steps"]),
        2.5, 5.0, [],
        "secuencia que se acumula en un plano: «primero… luego… por último», historia con fechas; cada paso en su palabra (cues s1…s5)",
        "pasos demostrables con captura real (split + media), solo 2 fechas (antes/después), > 5 pasos",
    ),
    "progress.bar": _g(
        "progress.bar.js",
        _obj({
            "value": {"type": "number", "minimum": 0, "maximum": 100}, "label": STR,
            "decimals": {"type": "integer", "minimum": 0, "maximum": 1}, "tone": TONE,
            "threshold": {"type": "object", "properties": {"value": {"type": "number", "minimum": 0, "maximum": 100}, "label": STR},
                          "required": ["value"], "additionalProperties": False},
            "anchor": ANCHOR, "backdrop": BACKDROP, "source": SOURCE,
        }, ["value", "label", "source"]),
        1.8, 3.0, [],
        "un porcentaje o proporción concreta (adopción, cuota, ahorro, avance real): número y barra con la misma curva",
        "como barra de carga decorativa, sin cifra concreta, para comparar varias cosas (chart.bar)",
    ),
    "callout.arrow": _g(
        "callout.arrow.js",
        _obj({
            "target": POINT, "text": STR,
            "side": {"enum": ["auto", "left", "right", "above", "below"], "default": "auto"},
            "ring": {"oneOf": [BOOL, {"type": "object", "properties": {"w": {"type": "number", "minimum": 0, "maximum": 1},
                                                                         "h": {"type": "number", "minimum": 0, "maximum": 1}},
                                       "required": ["w", "h"], "additionalProperties": False}]},
            "color": TONE, "bend": {"type": "number", "minimum": -1, "maximum": 1},
            "distance": {"type": "integer", "minimum": 140, "maximum": 520}, "source": STR,
        }, ["target", "text"]),
        1.2, 2.2, [{"at": "point", "offset": 0.0, "kind": "whoosh"}],
        "«este botón», «fíjate en esta cifra»: UN foco sobre una captura o plano real (target medido por OCR/selector)",
        "objetivos estimados a ojo, más de una flecha a la vez, señalar la cara de la persona en cámara",
    ),
    "keyword.highlight": _g(
        "keyword.highlight.js",
        _obj({
            "text": {"type": "string", "minLength": 1, "maxLength": 40},
            "mark": {"enum": ["marker", "underline", "circle", "strike"], "default": "marker"},
            "mark_words": {"type": "string", "description": "marker: solo estas palabras del texto (p. ej. «Natural»); el resto sin banda"},
            "replace": {"type": "string", "minLength": 1, "maxLength": 40, "description": "solo con strike: lo que sustituye al tachado"},
            "replace_lines": {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "string", "minLength": 1, "maxLength": 24},
                              "description": "strike: la sustitución en 1–2 líneas grandes (la 2.ª en la cue «replace2»); lo tachado se atenúa"},
            "rep_width": {"type": "integer", "minimum": 300, "maximum": 950, "description": "ancho máximo de esas líneas (696 si bajan de y=1000)"},
            "serif": {"type": "boolean", "description": "sin efecto (nunca serif); se acepta para los planes antiguos"}, "tone": TONE, "size": {"type": "integer", "minimum": 72, "maximum": 220},
            "anchor": ANCHOR, "backdrop": BACKDROP, "source": STR,
        }, ["text"]),
        1.2, 2.0, [],
        "LA palabra que pesa en la frase («sin código», «gratis», «en local») o antes→ahora con strike («3 días» → «20 minutos»)",
        "si el subtítulo ya muestra esas palabras (hide_captions), > 1 por frase, frases largas",
    ),
    "quote.card": _g(
        "quote.card.js",
        _obj({
            "quote": {"type": "string", "minLength": 1, "maxLength": 240}, "author": STR, "role": STR, "source": STR,
            "highlight": STR, "theme": {"enum": ["paper", "ink"], "default": "paper"},
            "size": {"type": "integer", "minimum": 50, "maximum": 80}, "anchor": ANCHOR,
            "logo": {"type": "string", "description": "id del asset (logo verificado) en ctx.media"},
        }, ["quote", "author", "source"]),
        3.0, 4.5, [],
        "Quien habla cita textualmente a alguien o lee un titular/post real que prueba el argumento (cita literal + autor + dónde)",
        "citas parafraseadas o sin fuente, > 34 palabras (mejor media.screenshot_card con la captura real)",
        media="optional",
    ),
    "lower_third.name": _g(
        "lower_third.name.js",
        _obj({
            "name": STR, "role": STR, "logo": {"type": "string", "description": "id del asset (logo verificado) en ctx.media"},
            "position": {"enum": ["auto", "top", "bottom"], "default": "auto"},
            "align": {"enum": ["left", "right"], "default": "left"}, "plate": {"type": "boolean", "default": True},
            "tone": TONE, "source": STR,
        }, ["name"]),
        1.8, 3.0, [],
        "primera aparición o mención de una persona real (entrevistado, autor de la cita, creador de la herramienta)",
        "para quien presenta el vídeo, repetirlo en el mismo vídeo, nombres o cargos sin verificar",
        media="optional",
    ),
    "section.title": _g(
        "section.title.js",
        _obj({
            "title": {"type": "string", "minLength": 1, "maxLength": 40}, "number": {"type": "string", "maxLength": 8},
            "kicker": STR, "backdrop": {"enum": ["none", "black", "navy", "paper"], "default": "navy"},
            "tone": TONE, "number_style": {"enum": ["serif", "sans"], "default": "sans", "description": "los dos en Montserrat 900 (nunca serif)"}, "anchor": ANCHOR,
        }, ["title"]),
        1.0, 1.6, [{"at": "enter", "offset": 0.0, "kind": "whoosh"}],
        "ordinal o paso de una lista («Primero», «El segundo truco») como plantilla RECURRENTE del vídeo; cambio de bloque en vídeos largos",
        "en cada frase, Shorts de un solo bloque, si el plano siguiente ya es la captura del paso",
    ),
}
