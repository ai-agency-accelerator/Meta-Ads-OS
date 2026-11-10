"""cutkit.motion.registry_graphics — catálogo de los componentes de GRÁFICOS (los fusiona `registry.py`).

Mismo esquema que `registry.COMPONENTS`: kind, track, file, media, props (JSON Schema), dur_min/dur_rec (s),
sfx ([{"at": "enter"|"exit"|"<cue>", "offset": s, "kind": "whoosh|pop|click|ding|type|riser|impact"}]), when/when_not.

Reglas comunes a todos (las aplica el JS, ver el kit `CK.gx` v4 en cada componente):
- `canvas` fija el tema de contraste; el lienzo lo pinta el layout. `exit: "cut"` = sin tween de salida.
- Contenido centrado en x=540; por encima de y≈1016 usa 950 px de ancho (zona segura dependiente de la altura).
- El contenido va en ctx.slot ∩ zona segura; texto clave ≥ 44 px; salida limpia antes de t1; todo seek-safe.
- Nunca inventan datos: todo el texto y toda cifra vienen en props (la confianza o las probabilidades solo si son reales).
- Los logos se buscan en ctx.media por `data-asset` (el <img> estático no se mueve; se pinta como fondo).
- `backdrop` (none|black|navy|paper) pinta un fondo a sangre del slot con grano a 12 fps; por defecto lo pone el layout.
- `hide_captions` lo lee el runtime/compilador (no el componente).
"""
from __future__ import annotations

from typing import Any

STR = {"type": "string"}
NUM = {"type": "number"}
BOOL = {"type": "boolean"}
BACKDROP = {"enum": ["none", "black", "navy", "paper", "white", "ink", "accent"], "default": "none",
            "description": "PINTA un fondo a sangre del slot (solo si el layout no da panel_bg)"}
CANVAS = {"anyOf": [{"enum": ["none", "paper", "white", "ink", "accent", "black", "navy"]},
                    {"type": "string", "pattern": "^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"}], "default": "none",
          "description": "TEMA de contraste según el lienzo del layout (panel_bg); un hex elige tinta o blanco por contraste"}
COMMON = {"backdrop": BACKDROP, "canvas": CANVAS, "paint_canvas": BOOL, "hide_captions": BOOL, "sfx": BOOL,
          "exit": {"enum": ["fade", "cut"], "description": "cut = sin tween de salida (la pone html.py al acabar en el corte del layout)"},
          "enter": {"enum": ["fade", "cut"]},
          "keep_start": {"type": "boolean", "description": "el compilador no adelanta t0 a la cue (continúa un gráfico anterior)"},
          "ghost": {"type": "boolean", "description": "estado 0 en fantasma (cajas vacías) antes de cada cue; false = sin fantasmas"},
          "band": {"enum": ["high", "full", "center", "safe"], "description": "high = contenido por encima de y≈1016 (950 px centrados) en pantalla completa; center = banda simétrica alrededor del centro del lienzo (460–1460); safe = zona segura clásica"},
          # SFX por item (cutkit/audio/sfxplan): silenciar una aparición concreta de un evento o fijar su nivel
          "sfx_skip": {"type": "array", "items": {"type": "string"}, "description": "«evento:n» sin SFX (n desde 0), p. ej. «option:1»; «evento:*» todas; «class:<at>» quita el sonido del registro del componente en ese momento (p. ej. «class:enter» en logo.reveal)"},
          "sfx_rel": {"type": "object", "additionalProperties": {"type": "number"}, "description": "nivel propio (LU respecto a la voz) por evento, p. ej. {\"hero\": -15}"},
          "stack": {"type": "boolean", "description": "se suma a lo que ya hay en el panel (no lo recorta al entrar)"},
          # evita destellos de 2–3 f de panel vacío entre piezas
          "overlap_in": {"type": "integer", "minimum": 1, "maximum": 6, "description": "compile.py: la pieza arranca N f ANTES de que acabe la salida de la anterior del MISMO panel (pensado para cuando la anterior sale con `exit: \"fade\"`): el panel no queda en blanco liso entre las dos. Sin la prop, nada cambia"},
          "preroll": {"type": "integer", "minimum": 1, "maximum": 6, "description": "runtime: el reloj de la animación arranca N f antes del t0 del item (sigue visible desde su t0): en un corte de cara a panel, la entrada ya va por su fotograma N y el panel no sale vacío. Los sonidos, en el primer fotograma visible"}}


# `zoom` opcional en logo.row, viz.shapes, viz.gauges,
# viz.many_to_one y viz.crm: a pantalla completa, el gráfico entero ×k alrededor de `from` y ese punto a `to` (px del
# lienzo), aplicado al final de animate (las medidas de texto no cambian). Quien lo usa comprueba la «T» de la zona segura
ZOOM = {"type": "object", "properties": {
    "k": {"type": "number", "minimum": 0.5, "maximum": 2.5},
    "from": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
    "to": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}},
    "required": ["k", "from", "to"], "additionalProperties": False,
    "description": "a pantalla completa: el gráfico ENTERO ×k alrededor de `from` [x, y] y ese punto a `to` [x, y] (px del lienzo); tiempos y medidas iguales. Comprueba tú la zona segura de texto (perfil organico.yaml y la QA: x 65–1015 si la caja acaba por encima de y=1000; x 65–888 si baja de y=1000, por los botones de Shorts; centrado en x=540 eso deja 696 px, 192–888) y el subtítulo (si lo último es un rótulo, y ≤ 1280)"}

def _obj(props: dict, required: list[str] | None = None) -> dict:
    p = dict(COMMON)
    p.update(props)
    return {"type": "object", "properties": p, "required": required or [], "additionalProperties": False}


ASSET_ID = {"type": "string", "description": "id del asset sin «m_» (p. ej. logo_nimbo); se busca por data-asset en ctx.media"}
# compare.vs: escena por lado y glifo neutro del kit (gx.GLYPHS) en oro
VS_SCENE = {"enum": ["flatten", "layers"], "description": "flatten = tres láminas (texto, imagen, efecto) que se aplastan en un archivo y se cierran con candado "
            "en la cue `lock`; layers = las mismas láminas separadas dentro de una ventana con los logos (`assets` en su barra)"}
VS_GLYPH = {"type": "string", "description": "glifo neutro del kit (doc, screen, check, clock, chat, mail…) en oro; sin escena va en la fila de logos, con «layers» en la barra de la ventana"}
VS_HERO = {**ASSET_ID, "description": "solo con scene «layers»: logo verificado que entra GRANDE (baldosa blanca ≥ 200 px) en el centro de la ventana "
           "con su lado (cue left/right) y en la cue `dock` encaja en SU ranura de la barra (la suya si el id está en `assets`; si no, una nueva a la izquierda), "
           "mientras las capas aparecen y se separan. Evento `dock` en el fotograma del encaje (= la palabra de la cue)"}

GRAPHICS: dict[str, dict[str, Any]] = {
    "viz.token_stream": {
        "file": "viz.token_stream.js", "media": None,
        "props": _obj({
            "phase": {"enum": ["intro", "loop", "full"], "default": "loop",
                      "description": "intro: se teclea la instrucción y sale la respuesta; loop: contexto → candidatos → elige → añade → se acelera; full: las dos en un item"},
            "prewritten": {"type": "boolean", "description": "el prompt ya está escrito en t0 (callbacks)"},
            "burst": {"type": "boolean", "description": "todos los tokens en ≤1,2 s (callbacks)"},
            "from_tokens": {"type": "integer", "minimum": 0, "description": "los N primeros tokens ya están (continúa el diagrama de un item anterior)"},
            "intro_tokens": {"type": "integer", "minimum": 0, "description": "full: tokens que salen en «tokens» antes de las vueltas lentas"},
            "prompt": STR,
            "tokens": {"type": "array", "maxItems": 40, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "text": STR, "candidates": {"type": "array"}}, "required": ["text"]}]},
                "description": "con espacio inicial = token separado (« Marta»); sin espacio se pega («irnos»)"},
            "candidates": {"type": "array", "items": {"anyOf": [{"type": "array", "items": STR, "maxItems": 4}, {"type": "null"}]},
                           "description": "alineadas con tokens (null = sin vuelta lenta); el token elegido debe estar en su lista"},
            "probs": {"type": "array", "items": {"type": "array", "items": NUM},
                      "description": "SOLO probabilidades reales (logprobs); sin ellas las barras son un esquema sin cifra"},
            "show_pct": BOOL,
            "compact": {"type": "boolean", "description": "versión menor y arriba (callback rápido del diagrama)"},
            "style": {"enum": ["chips", "text"], "default": "chips", "description": "chips: un token por ficha con hueco discontinuo"},
            "prompt_label": {"type": "string", "description": "rótulo sobre la instrucción (p. ej. «instrucción»)"},
            "layout_tokens": {"type": "array", "items": STR, "description": "chips: frase FINAL para maquetar los huecos (p. ej. el intro con los tokens de su continuación: las fichas no se mueven entre items)"},
            "candidates_label": {"type": "string", "description": "rótulo pequeño del panel (p. ej. «esquema»)"},
        }, ["tokens"]),
        "dur_min": 2.5, "dur_rec": 7.0,
        "sfx": [{"at": "append", "offset": 0.0, "kind": "click"}, {"at": "loop", "offset": 0.0, "kind": "type"}],
        "cues_doc": "intro: prompt, generate, tokens, loop/full: context, compute, next, append, repeat, loop, final (+ prompt/tokens en full)",
        "when": "explicar cómo genera un LLM (contexto → siguiente token → se añade → se repite); un diagrama que se construye en un plano, con layout card_float o split_top",
        "when_not": "si quien habla no explica el mecanismo; nunca con probabilidades inventadas en cifra (sin `probs` reales, son barras de esquema)",
    },
    "viz.decision": {
        "file": "viz.decision.js", "media": "optional",
        "props": _obj({
            "input": {"type": "object", "properties": {"label": STR, "text": STR, "body": STR}, "required": ["text"], "additionalProperties": False,
                      "description": "inbox: label = remitente, text = asunto, body = primera línea; route: label = cabecera del chat, text = mensaje"},
            "style": {"enum": ["template", "inbox", "route", "meter"], "default": "template",
                      "description": "inbox: fila de bandeja + sello «<question>: <opción>» en choose; route: burbuja de chat → flechas a los destinos, "
                                     "el elegido se enciende; meter: tarea + selector de posiciones (opt0..N) que se clava en la elegida; template: tarjeta + opciones (antiguo)"},
            "stamp": {"type": "string", "description": "inbox: texto del sello (por defecto «<question sin ¿?>: <opción elegida>»)"},
            "question": STR,
            "options": {"type": "array", "minItems": 1, "maxItems": 4, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "label": STR, "asset": ASSET_ID, "glyph": STR, "tone": {"enum": ["gold", "ink", "white", "silver", "color"]}}, "required": ["label"]}]},
                "description": "opciones reales; `asset` (icono del kit) o `glyph` delante de la etiqueta, en el oro del kit y ≥ 48 px"},
            "chosen": {"type": "integer", "minimum": 0, "description": "índice de la opción elegida"},
            "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1, "description": "real o null (sin cifra)"},
            "abstract": {"type": "boolean", "description": "ejemplo genérico: el texto de entrada va en Montserrat 500 (más ligero que el 700 normal; nunca serif ni cursiva)"},
            "model": {"type": "object", "properties": {"label": STR, "asset": ASSET_ID}, "additionalProperties": False},
            "result_note": {"type": "string", "description": "línea bajo el resultado (p. ej. «destino: ventas, urgencia alta»)"},
            "layout": {"enum": ["auto", "grid", "row", "column"], "default": "auto",
                       "description": "opciones: auto (≤4 en fila, >4 rejilla de 2 columnas); column: una por fila, automático si una etiqueta pasa de ~16 caracteres. "
                                      "En la elección, la no elegida queda con borde de tinta (no se desvanece) y el check mide ≥ 40 px"},
            "register": {"type": "array", "items": {"type": "object", "properties": {"label": STR, "value": STR}, "required": ["label", "value"]},
                         "description": "registro de arriba: ejemplos YA decididos (píldoras «Email ✓ Sí»…)"},
            "register_slots": {"type": "array", "items": STR, "description": "huecos del registro en orden (p. ej. [\"Email\",\"Lead\",\"Tarea\"]); los pendientes, discontinuos"},
            "fold_to_register": {"type": "boolean", "description": "al final, la plantilla se pliega en su píldora del registro (match cut)"},
            "sequence": {"type": "array", "maxItems": 6, "items": {"type": "object"},
                         "description": "[{input, question, options, chosen, confidence, result_note?}] — la MISMA tarjeta cambia en cada sN_input"},
        }, []),
        "dur_min": 2.2, "dur_rec": 4.5,
        "sfx": [{"at": "input", "offset": 0.0, "kind": "whoosh"}, {"at": "choose", "offset": 0.1, "kind": "ding"}],
        "cues_doc": "input, question, options|optN, choose, fold (plegado al registro; por defecto choose+0,45 s); secuencia: s0_input, s0_question, s0_options|s0_optN, s0_choose, s1_input…",
        "when": "una entrada concreta (email, lead, tarea) → pregunta → opciones definidas → se elige una; varios ejemplos seguidos = `sequence` (contenedor que nunca corta)",
        "when_not": "si no hay opciones cerradas; confianza solo si es un dato real de la prueba",
    },
    "list.build": {
        "file": "list.build.js", "media": "optional",
        "props": _obj({
            "items": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "label": STR, "value": STR, "icon": {"type": "string", "description": "asset id (data-asset); un nombre genérico sin asset → índice en Montserrat 800"}},
                "required": ["label"], "additionalProperties": False}]}},
            "style": {"enum": ["cards", "chips"], "default": "cards", "description": "cards: tarjetas con índice, chips: etiqueta + valor real"},
            "title": STR, "ghost": BOOL,
        }, ["items"]),
        "dur_min": 1.5, "dur_rec": 4.5,
        "sfx": [],
        "when": "enumeración de 3–6 elementos abstractos o formatos que se acumulan en un plano (cada uno en su palabra: cues i0…)",
        "when_not": "elementos demostrables con su propia captura (mejor un recurso por elemento); listas ya escritas en una captura",
    },
    "compare.vs": {
        "file": "compare.vs.js", "media": "optional",
        "props": _obj({
            "left": {"type": "object", "properties": {"label": STR, "assets": {"type": "array", "items": ASSET_ID, "maxItems": 4}, "highlight": BOOL,
                                                      "glyph": VS_GLYPH, "scene": VS_SCENE, "hero": VS_HERO},
                     "required": ["label"], "additionalProperties": False},
            "right": {"type": "object", "properties": {"label": STR, "assets": {"type": "array", "items": ASSET_ID, "maxItems": 4}, "highlight": BOOL,
                                                       "glyph": VS_GLYPH, "scene": VS_SCENE, "hero": VS_HERO},
                      "required": ["label"], "additionalProperties": False},
            "winner": {"enum": ["left", "right", None], "description": "el otro lado se apaga (no se tacha)"},
            "vs_label": STR, "ghost": {"type": "boolean", "default": False, "description": "true = estado 0 en fantasma (cajas vacías) antes de cada cue; por defecto, nada hasta su cue"},
            "separator": {"enum": ["vs", "+"], "default": "vs", "description": "«+» y sin highlight = ninguno gana («no sustituye»)"},
            "dim_right": {"type": "boolean", "description": "la derecha EN ESPERA (bucle abierto): contorno discontinuo y atenuada; "
                          "automático si left.highlight y no right.highlight (sin winner)"},
            "parity": {"type": "boolean", "description": "los dos rótulos con el MISMO número de líneas y cuerpo (gx.lineParity) también sin escenas"},
            "vs_px": {"type": "integer", "minimum": 40, "maximum": 260, "description": "cuerpo en px del separador (`vs_label`, p. ej. «≠» a 230); el eje se ensancha para que quepa. Sin la prop, 68 px·s de siempre"},
            "vs_tone": {"enum": ["ink", "muted"], "description": "color del separador: tinta (ink) o el gris de siempre (muted, por defecto)"},
            "solo_center": {"type": "boolean", "description": "con la cue `vs`: mientras solo están la izquierda y el separador, el par va centrado; en `right` se desliza a su sitio (0,35 s, power3.out) mientras entra la derecha"},
            "tile_px": {"type": "integer", "minimum": 80, "maximum": 320, "description": "lado en px de la baldosa del icono en cada tarjeta (tope: el ancho de la columna); por defecto 120–176 según cuántos haya"},
        }, ["left", "right"]),
        "dur_min": 1.8, "dur_rec": 3.5,
        "sfx": [{"at": "right", "offset": 0.0, "kind": "whoosh"}],
        "cues_doc": "left, right (cada lado en su palabra); vs (opcional y sin fantasmas: el separador sube EN esa palabra y la izquierda entra ya en su sitio, sin centrarse); pulse0/pulse1/pulse2 opcionales: late el logo k de la izquierda (6 f, 1→1,08→1 y brillo) cuando quien habla lo vuelve a nombrar; "
                    "con escenas: lock (el archivo aplastado se cierra con candado; en su palabra, p. ej. «archivo final») y flatten opcional (por defecto, 0,5 s antes de lock); "
                    "eventos: enter, option, flatten (las láminas se aplastan), lock (se cierra el candado), layers (las láminas de la ventana se abren), pulse, exit. "
                    "el candado cae ABIERTO y se cierra de golpe EN el fotograma de `lock` (evento ahí); con `hero` en el lado «layers»: "
                    "dock (el logo grande encaja en su ranura de la barra EN esa palabra; vuela los 9 f anteriores; evento `dock`, sin `layers`), "
                    "right_label opcional (el rótulo derecho sube en su palabra; la tarjeta y el héroe, en `right`)",
        "when": "contraste A frente a B dicho por quien habla («generar respuestas» vs «tomar decisiones»); cada lado en su palabra (cues left/right). "
                "con `scene` por lado, contraste de FORMA DE TRABAJAR con imágenes y no solo texto: «generar el archivo final» "
                "(`scene: \"flatten\"`: tres láminas que se aplastan y se cierran con candado) frente a «trabajar dentro de la herramienta» "
                "(`scene: \"layers\"`: las mismas láminas, separadas y editables, en una ventana con los logos)",
        "when_not": "si no hay contraste explícito; nunca para atribuir funciones que quien habla no dice",
    },
    "viz.puzzle": {
        "file": "viz.puzzle.js", "media": "optional",
        "props": _obj({
            "left": {"type": "object", "properties": {"label": STR, "assets": {"type": "array", "items": ASSET_ID, "maxItems": 4}}, "required": ["label"], "additionalProperties": False},
            "right": {"type": "object", "properties": {"label": STR, "assets": {"type": "array", "items": ASSET_ID, "maxItems": 4}}, "required": ["label"], "additionalProperties": False},
            "orient": {"enum": ["auto", "horizontal", "vertical"], "default": "auto",
                       "description": "auto: lado a lado si las etiquetas caben en una línea a ≥44 px; si no, piezas apiladas a todo el ancho"},
        }, ["left", "right"]),
        "dur_min": 2.0, "dur_rec": 4.5,
        "sfx": [{"at": "right", "offset": 0.0, "kind": "whoosh"}, {"at": "lock", "offset": 0.03, "kind": "click"}],
        "cues_doc": "left (la izquierda, sola; en el corte si cae a ≤0,6 s), right (se aparta y entra la derecha), lock (encaja con un clic; luego brillo y una sola pieza)",
        "when": "dos cosas que se COMPLEMENTAN (no compiten): «no viene a sustituir… sino a ocupar una parte diferente del trabajo»",
        "when_not": "contrastes A frente a B (eso es compare.vs)",
    },
    "viz.layers_control": {
        "file": "viz.layers_control.js", "media": None,
        "props": _obj({
            "labels": {"type": "object", "properties": {"agent": STR, "human": STR}, "additionalProperties": False,
                       "description": "rótulos de una línea junto a cada insignia, los DOS encima de la tarjeta (agente arriba, nosotros debajo; "
                                      "a 48 px y el texto más bajo ≥ 120 px sobre el subtítulo, y ≤ 840 en el 50/50); NO pasan por Title Case automático: escríbelos ya en Title Case"},
            "layers": {"anyOf": [{"type": "integer", "minimum": 3, "maximum": 5},
                                 {"type": "array", "items": {"type": "string", "minLength": 1, "maxLength": 24}, "minItems": 2, "maxItems": 5}],
                       "default": 4,
                       "description": "número de capas (sin nombre: ojo, miniatura y barra en esqueleto) o sus NOMBRES REALES de arriba abajo "
                                      "(p. ej. [\"NOVA\", \"Tagline\", \"Lens Flare\", \"Glow Orb\"], los de la capa NOVA del largo): tarjeta de 900 px, filas de 96 px, "
                                      "ojo de 52 px, miniatura deducida del nombre (luz/destello → efecto, foto/fondo → imagen, orbe/forma → relleno, resto → texto)"},
            "toggle_row": {"type": "integer", "minimum": 0, "maximum": 4, "default": 1, "description": "capa (desde arriba, 0 = la primera) cuyo ojo apaga el cursor"},
        }),
        "dur_min": 3.0, "dur_rec": 5.5,
        "sfx": [{"at": "build", "offset": 0.0, "kind": "click"}, {"at": "toggle", "offset": 0.0, "kind": "click"}, {"at": "seal", "offset": 0.0, "kind": "ding"}],
        "cues_doc": "agent (insignia del agente + rótulo), build (las capas salen de la insignia y se apilan de abajo arriba, una cada 5–8 f), human (nuestra insignia + rótulo), "
                    "cursor (el cursor de ~70 px sale de nuestra insignia y va al ojo de `toggle_row`), toggle (clic con onda oro: ojo tachado, capa atenuada), "
                    "seal (el sello de 104 px con check de 73 px IMPACTA en la cue —cae 3 f antes—, la pila late, el borde oro se dibuja ENTERO alrededor de la "
                    "tarjeta desde el sello y se queda; el sello late con una onda cada 1 s). Todas opcionales. Eventos: enter, build ×n (uno por capa en el "
                    "fotograma en que aparece, `index` 0…n−1 en orden de aparición: build:0…build:3 en sfx_skip), cursor, toggle (fotograma del clic), "
                    "seal (fotograma del impacto), exit",
        "when": "la IA hace el trabajo pesado pero NOSOTROS mantenemos el control (capas editables, decidir qué se ve): «la IA genera las capas y tú decides»",
        "when_not": "un archivo final aplanado frente a capas editables (eso es compare.vs con scene flatten/layers); dos piezas que se complementan (viz.puzzle)",
    },
    "viz.offer_grid": {
        "file": "viz.offer_grid.js", "media": "required",
        "props": _obj({
            "items": {"type": "array", "minItems": 2, "maxItems": 9, "items": {"type": "object", "properties": {"icon": ASSET_ID, "label": STR,
                      "media": {**ASSET_ID, "description": "miniatura REAL (imagen cuadrada) en vez del icono: en reposo en gris, a color en el foco"}},
                      "required": ["icon", "label"], "additionalProperties": False},
                      "description": "las ofertas, en orden: icono 3D del kit (carpeta de iconos 3D de la marca, como asset) + nombre en Title Case (hasta 9: rejilla 3×3); `media` opcional = miniatura real"},
            "mode": {"enum": ["all", "focus", "pick", "combine"], "default": "all",
                     "description": "all: gancho (cascada + kicker) · focus: ordinal N (la N se enciende, «N/6» + nombre) · pick: cierre (cinco se apagan, una en oro crece) · "
                                    "combine: la rejilla se abre, cada baldosa de `also` se enciende en su cue (c0…) y lanza un conector de circuito (tinta + oro) "
                                    "con un pulso hasta la de `focus`, que late con cada pulso y GIRA con el último; `note` debajo en su cue"},
            "carry": {"type": "boolean", "description": "arranca en el estado FINAL de la rejilla anterior del plan (sin reentrar desde opacidad 0): baldosas, "
                                                         "medias luces y foco; en «number» el aro viaja de la baldosa anterior a la nueva y la cámara empuja suave (≤ 4 %) hacia la activa"},
            "carry_from": {"anyOf": [{"type": "integer", "minimum": 1, "maximum": 9},
                                     {"type": "object", "properties": {"mode": {"enum": ["focus", "combine", "all"]}, "focus": {"type": "integer", "minimum": 1, "maximum": 9},
                                                                       "done": {"type": "array", "items": {"type": "integer"}}, "also": {"type": "array", "items": {"type": "integer"}}},
                                      "additionalProperties": False}],
                           "description": "estado de partida explícito (el foco anterior, o {focus, done, also}); manda sobre `carry`"},
            "tiles": {"enum": ["in"], "description": "las baldosas ya están puestas en el fotograma 0 (sin texto); en all, la cascada es un pulso que recorre la rejilla"},
            "name_gap": {"type": "integer", "minimum": 8, "maximum": 140, "description": "con band_pos top: px de aire banda → rejilla; entre ordinal y nombre, la mitad"},
            "note": {"type": "string", "description": "combine: remate bajo la rejilla (Title Case), sube por su máscara en la cue «note»"},
            "note_px": {"type": "integer", "minimum": 48, "maximum": 120, "description": "combine: cuerpo máximo del remate (64)"},
            "push": {"type": "boolean", "description": "empuje de cámara a la activa (por defecto, solo con carry/carry_from); false lo quita"},
            "spin": {"type": "boolean", "description": "combine: false = el foco no gira al recibir el último pulso"},
            "focus": {"type": "integer", "minimum": 1, "maximum": 9, "description": "baldosa en foco (focus/pick)"},
            "cols": {"enum": [2, 3, 4], "description": "columnas de la rejilla (por defecto 3; 2 = 2×2 para 4 baldosas)"},
            "band_pos": {"enum": ["bottom", "top"], "default": "bottom",
                         "description": "top: banda de texto arriba (950 px, por encima de y=1000) y la rejilla debajo (≤ 696 px en la «T»), hasta el raíl de subtítulos"},
            "ordinal_style": {"enum": ["sans", "serif"], "description": "sin valor: «N/6» pequeño en oro (de siempre) · serif: se acepta pero se pinta como «sans» (nunca serif) · sans: ordinal grande en Montserrat 900 con la «ª» pequeña y elevada («1.ª», 140 px por defecto)"},
            "ordinal_px": {"type": "integer", "minimum": 34, "maximum": 260, "description": "cuerpo máximo del ordinal"},
            "ordinal_bar": {"type": "boolean", "description": "sans: raya bajo la «o»/«a» volada («1.º» no se lee «1.°»)"},
            "pick_solo": {"type": "boolean", "description": "pick: las demás baldosas se apagan del todo (no al 10 %) antes de que la elegida crezca, y la elegida va por encima"},
            "name_tone": {"enum": ["gold"], "description": "el nombre en el oro oscuro del kit (#C99A12): el uso bajo el repo en «cuál instalar»"},
            "name_weight": {"type": "integer", "minimum": 400, "maximum": 900, "description": "peso del nombre (por defecto, el de la hoja)"},
            "tee_rows": {"type": "boolean", "description": "band_pos top a pantalla completa, rejilla de 2 filas con la última incompleta (3 + 2): la primera fila usa los 950 px de la banda alta y solo la última cabe en 696 (baldosas ~300 en vez de ~220); si la primera no acaba por encima de y=1000, como siempre"},
            "name": {"type": "string", "description": "focus: texto de la banda en vez del rótulo de la baldosa (p. ej. en el gancho)"},
            "name_px": {"type": "integer", "minimum": 48, "maximum": 140, "description": "cuerpo máximo del nombre (band_pos top)"},
            "show_ordinal": {"type": "boolean", "description": "focus: false = sin ordinal"},
            "tile_px": {"type": "integer", "minimum": 100, "maximum": 340, "description": "tope del lado de baldosa (band_pos top); máximo 340 (el JS ya lo limita al ancho de la «T», 2 × 339 en 696 px)"},
            "done": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 9},
                     "description": "focus: baldosas ya contadas, a media luz (se ve por dónde va la lista)"},
            "keep_also": {"type": "boolean", "default": False, "description": "en focus con carry, las de `also` ya encendidas siguen encendidas (sin apagarse en el corte)"},
            "also": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 9},
                     "description": "focus: baldosas que se encienden a la vez en la cue «also» («combinar varias de las anteriores»)"},
            "pick_glyph": {"enum": ["icon", "target"], "default": "icon",
                           "description": "pick: target = la elegida enseña una diana en vez de su icono (quien habla no dice cuál)"},
            "pick_from": {"enum": ["tile", "center"], "description": "pick con `pick_glyph: target`: `center` = las cinco baldosas se apagan a la vez y la diana nace en el CENTRO de la rejilla (no viaja desde una baldosa: no se lee «elige esa»). Sin la prop, como siempre"},
            "carry_hop": {"enum": ["travel", "fade"], "description": "focus con `carry`: `fade` = el aro se apaga en la baldosa anterior y se enciende en la nueva, sin viajar por encima de otras. Sin la prop, viaja"},
            "sub": {"type": "string", "description": "all/pick: segunda línea bajo el kicker (cue «sub»)"},
            "kicker": {"type": "string", "description": "all/pick: titular bajo la rejilla (≥64 px, 1–2 líneas)"},
            "ordinal": {"type": "string", "description": "focus: texto oro sobre el nombre (por defecto «N/6»; p. ej. «1.ª»)"},
            "show_name": {"type": "boolean", "description": "focus: false = sin el nombre (solo el ordinal)"},
            "icon_focus": {"enum": ["gold", "color"], "default": "gold", "description": "icono en foco: duotono oro (defecto) o su color real"},
        }, ["items"]),
        "dur_min": 1.0, "dur_rec": 2.0,
        "sfx": [],
        "cues_doc": "focus/combine: n0…nk (cada palabra del nombre sube en su cue; sin ellas, el nombre entero en «name») · all: tiles (empieza la cascada) o i0…i8 (cada baldosa en su palabra, en oro mientras se nombra; «all» apaga el último), title (sube el kicker) · focus: number («La primera»: se enciende la N; con carry, el aro viaja), name (sube el nombre), also (se encienden `also`) · pick: pick, title (kicker en su palabra), sub · combine: number|hub (el foco), name, c0…c7 (cada pieza de `also`), note; eventos: enter, tile, focus (extra step = N), carry (el foco viaja), name, also→focus, spread (la rejilla se abre), connect (cada conector), merge (el foco recibe el último pulso y gira), note, pick, exit",
        "when": "Short de «N ofertas/ideas»: misma rejilla en gancho, en cada ordinal y en el cierre (empalma sin saltos: geometría fija)",
        "when_not": "listas sin iconos propios; más de 9 elementos",
    },
    "viz.mode_ladder": {
        "file": "viz.mode_ladder.js", "media": None,
        "props": _obj({
            "items": {"type": "array", "minItems": 2, "maxItems": 6, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "label": STR, "level": {"type": "integer", "minimum": 1, "maximum": 8}}, "required": ["label"], "additionalProperties": False}]},
                "description": "los modos/niveles en orden (Low → Ultracode); `level` = segmentos llenos del medidor (ordinal, sin cifras)"},
            "cols": {"type": "integer", "minimum": 1, "maximum": 3, "default": 2},
            "mode": {"enum": ["grid", "duel"], "default": "grid"},
            "enter": {"enum": ["cascade", "cut", "fade"]},
            "build": {"type": "boolean", "description": "cada nombre entra en su palabra (cues n0…n5)"},
            "names": {"type": "boolean", "description": "false = solo medidores hasta la cue «names»"},
            "labels": {"type": "boolean", "description": "false = sin rótulos de fila"},
            "steps": {"type": "array", "maxItems": 10, "items": {"type": "object", "properties": {
                "cue": STR, "lit": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 5}},
                "labels": {"type": "object", "additionalProperties": STR}, "grow": BOOL, "glow": {"type": "integer", "minimum": 0, "maximum": 5},
                "dim": BOOL, "neutral": {"type": "boolean", "description": "encendidas en blanco (sin foco): «todas a la vez»"},
                "stagger": {"type": "number", "minimum": 0}}, "additionalProperties": False},
                "description": "cada paso fija qué píldoras se encienden en oro (el resto se atenúa) y el rótulo de cada fila (Title Case corto)"},
            "initial": {"type": "object", "properties": {"lit": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 5}},
                        "labels": {"type": "object", "additionalProperties": STR}, "neutral": BOOL}, "additionalProperties": False,
                        "description": "estado heredado de la instancia anterior (se aplica en el corte sin animar ni sonar)"},
            "eyebrow": STR, "kicker": {"type": "string", "description": "titular bajo la rejilla (cue «title»)"},
            "duel": {"type": "array", "maxItems": 2, "items": {"type": "object", "properties": {
                "label": STR, "level": {"type": "integer", "minimum": 1, "maximum": 8}, "hot": BOOL, "cue": STR,
                "stats": {"type": "array", "maxItems": 2, "items": {"type": "object", "properties": {"k": STR, "v": STR, "hot": BOOL, "cue": STR},
                          "required": ["k", "v"], "additionalProperties": False}}}, "required": ["label"], "additionalProperties": False},
                "description": "mode duel: dos tarjetas (nombre + medidor) con dos cifras REALES cada una; la `hot` en oro"},
        }, ["items"]),
        "dur_min": 1.2, "dur_rec": 3.0,
        "sfx": [],
        "cues_doc": "grid: tiles (cascada), n0…n5 (build), names, s0…sN (pasos), title (kicker) · duel: c0, c0s0, c0s1, c1, c1s0, c1s1; eventos: enter, tile, land, highlight, option, name, exit",
        "when": "Short de «modos/niveles» de un mismo producto (esfuerzo, planes): la misma escalera como hilo conductor en gancho, explicación, duelo de cifras y recomendación",
        "when_not": "comparar productos distintos (logo.row / compare.vs); cifras que quien habla no dice",
    },
    "label.mode_tag": {
        "file": "label.mode_tag.js", "media": None, "overlay": True,
        "props": _obj({
            "label": STR, "meter": {"type": "boolean", "description": "false = rótulo simple, sin medidor de nivel"},
            "level": {"type": "integer", "minimum": 0, "maximum": 8, "description": "segmentos llenos (ordinal, sin cifras)"},
            "of": {"type": "integer", "minimum": 1, "maximum": 8, "default": 6}, "hot": {"type": "boolean", "description": "aro y medidor oro (el foco)"},
            "enter": {"enum": ["pop", "swap"], "default": "pop", "description": "swap = encadenado a otro tag en un montaje (sube de nivel)"},
            "from_level": {"type": "integer", "minimum": 0, "maximum": 8, "description": "swap: segmentos que ya estaban llenos"},
            "y": {"type": "integer", "minimum": 288, "maximum": 1000},
            "w": {"type": "integer", "minimum": 360, "maximum": 900, "description": "ancho fijo (montajes: misma geometría en cada corte)"},
        }, ["label", "level"]),
        "dur_min": 0.4, "dur_rec": 2.0,
        "sfx": [],
        "cues_doc": "eventos: enter (aparece o cambia de modo), exit",
        "when": "clip REAL de un modo/nivel concreto (Short de «modos»): dice qué modo hizo lo que se ve, arriba y centrado",
        "when_not": "rotular mejoras o cifras que quien habla no dice; clips sin un modo concreto",
    },
    "viz.gauges": {
        "file": "viz.gauges.js", "media": "optional",
        "props": _obj({
            "title": STR, "sub": STR,
            "icon": {"type": "string", "description": "id del asset (icono del kit propio) a la izquierda del título"},
            "gauges": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "object", "properties": {
                "label": STR, "level": {"type": "number", "minimum": 0, "maximum": 1, "description": "llenado visual (sin cifra en pantalla)"},
                "cue": STR,
                "ease": {"enum": ["move", "enter"], "description": "curva del llenado de ESTE medidor (manda sobre `fill_ease`)"},
                "brand": {**ASSET_ID, "description": "logo verificado DENTRO del medidor desde que se dibuja su pista; va también en `assets`"},
                "brand_text": {**STR, "description": "nombre en texto dentro del medidor, para marcas sin logo verificado"}},
                "required": ["label", "level"], "additionalProperties": False},
                "description": "medidores semicirculares con su rótulo (Title Case), cada uno se llena en su palabra"},
            "zoom": ZOOM,
            "label_hide": {"type": "boolean", "description": "sin rótulo debajo (cuando la marca va dentro con `brand`/`brand_text`)"},
            "titles": {"type": "array", "items": {"type": "object", "properties": {"text": STR, "cue": STR}, "required": ["text", "cue"], "additionalProperties": False},
                       "description": "relevos del título, cada uno en su cue"},
            "jump_marker": {"type": "boolean", "description": "barra oro bajo el medidor en curso que salta al siguiente cuando este llega a su nivel"},
            "column_gap": {"type": "integer", "minimum": 16, "maximum": 120, "description": "con `column`: hueco entre un medidor (con su rótulo) y el de debajo, en px antes de la escala (28 por defecto): el rótulo queda más cerca de SU medidor que del siguiente"},
            "column": {"type": "boolean", "description": "2–3 medidores uno DEBAJO de otro, centrados y del mismo radio (`radius`): a pantalla completa crecen en alto (en fila los limita el ancho de la «T»); `span_w` no se usa. No se llama `stack` porque chocaba con el de la compilación"},
            "fill_ease": {"enum": ["move", "enter"], "description": "curva del llenado (arco y aguja): move (por defecto, power2.inOut: los ~3 primeros f casi quieta) o enter (token de entrada, power3.out: gira visible desde el primer fotograma del tween, para un SFX en el evento `fill`)"},
            "anchor": {"type": "number", "minimum": 0.2, "maximum": 0.8},
            "still": {"type": "boolean", "description": "la aguja llega a su nivel y se queda quieta (sin el temblor de ±1,5°)"},
            "ramp": {"enum": ["warm", "gold"], "description": "rampa del relleno: warm (por defecto, oro → naranja-rojo) o gold (todo en el oro del kit)"},
            "draw_each": {"type": "boolean", "description": "cada pista se dibuja ~0,5 s antes de SU llenado (sin medidores vacíos esperando); con cue `gauges`, la primera pista se dibuja en esa palabra si cae antes"},
            "hero": {**ASSET_ID, "description": "el objeto del kit GRANDE y centrado ENCIMA del título (ya en el corte: nunca papel vacío en el relevo; se balancea despacio), "
                     "en vez de `icon` pegado al título; va también en `assets`"},
            "hero_size": {"type": "integer", "minimum": 160, "maximum": 320, "description": "px del héroe (220); suma su alto al bloque: con 2 medidores a pantalla completa, `anchor` ≈ 0,335 y ≤ 200 para que los rótulos queden sobre y=1000"},
            "label_fit": {"type": "boolean", "description": "rótulos medidos de verdad: el mayor cuerpo ≤ 58 px que quepa en su columna, todos iguales, nunca bajo `label_min`, con la caja ajustada al texto (sin esto bajan a 36 px y la caja ocupa toda la columna)"},
            "label_min": {"type": "integer", "minimum": 40, "maximum": 72, "description": "con `label_fit`, cuerpo mínimo de los rótulos (48)"},
            "span_w": {"type": "integer", "minimum": 300, "maximum": 950, "description": "ancho en px de la fila de medidores, centrada (p. ej. 696: el ancho seguro bajo y=1000); el radio se ajusta para que no se toquen. Sin la prop, todo el ancho del área"},
            "radius": {"type": "integer", "minimum": 80, "maximum": 320, "description": "radio del medidor en px (168 con 1–2, 128 con 3); 290 = un medidor de ~610 px"},
            "title_max": {"type": "integer", "minimum": 52, "maximum": 92, "description": "tope del título en px (por defecto 92·s): que no mande sobre el medidor"},
            "quick": {"type": "boolean", "description": "sin `draw_each`: las pistas se dibujan CON el título y cada medidor se llena en SU cue con 4–6 f de margen (no ~1,2 s después del título)"},
            "limit": {"type": "boolean", "description": "false = sin tope de límite al final de la pista (ni evento `limit`) y el nivel puede llegar a 1: arco entero, sin muñón gris con la marca. Sin la prop, el tope de siempre (nivel ≤ 0,98)"},
        }, ["title", "gauges"]),
        "dur_min": 2.0, "dur_rec": 6.0,
        "sfx": [],
        "cues_doc": "title, sub, gauges (se dibujan las pistas), limits (topes), g0…g2 (cada medidor se llena); eventos: enter, title, sub, draw, limit, fill, exit",
        "when": "consumo frente a un límite o cuota («cuánto gastamos», «lo cerca que estamos del límite de 5 horas o del semanal»): "
                "medidores de instrumento que se llenan en su palabra, sin cifras que quien habla no diga",
        "when_not": "un porcentaje concreto que quien habla dice (progress.bar / stat.big_number); comparar opciones (compare.vs)",
    },
    "viz.capture_cam": {
        "file": "viz.capture_cam.js", "media": "required",
        "props": _obj({
            "sheets": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"type": "object", "properties": {
                "asset": STR, "img_w": {"type": "integer"}, "img_h": {"type": "integer"}, "left": {"type": "integer"}, "top": {"type": "integer"},
                "width": {"type": "integer"}, "cue": STR}, "required": ["asset", "img_w", "img_h", "top"], "additionalProperties": False},
                "description": "capturas reales colocadas en px del lienzo (quien dirige comprueba la «T»); cada una entra en su cue"},
            "marks": {"type": "array", "items": {"type": "object"},
                      "description": "[{cue, sheet?, box:[x,y,w,h], kind: underline|box}]: marca oro sobre una línea o un botón de la hoja, en fracciones de esa hoja"},
            "frame": BOOL, "drift": {"type": "number", "minimum": 0, "maximum": 0.04},
            "drift_at": {"type": "array", "items": NUM, "minItems": 2, "maxItems": 2},
            "texts": {"type": "array", "maxItems": 2, "items": {"type": "object", "properties": {
                "text": STR, "px": {"type": "integer", "minimum": 48, "maximum": 96}, "y": {"type": "integer", "minimum": 360}, "cue": STR, "out": STR},
                "required": ["text", "y"], "additionalProperties": False},
                "description": "rótulo con máscara, centrado, que entra en `cue` y sale en `out` sin cortar la captura"},
            "row": {"type": "object", "properties": {"idle": STR, "gold": STR, "n": {"type": "integer", "minimum": 1, "maximum": 8}, "cy": {"type": "integer"},
                                                     "size": {"type": "integer"}, "gap": {"type": "integer"}, "cue": STR, "lit": {"type": "array", "items": STR}},
                    "required": ["idle", "n", "cy"], "additionalProperties": False,
                    "description": "fila centrada de iconos bajo las hojas: entra en `cue` y cada uno se enciende en su cue de `lit`"},
        }, ["sheets"]),
        "dur_min": 1.0, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "las que nombren `sheets`, `marks` y `row`; eventos: enter, sheet, mark, box, row, lit, exit",
        "when": "capturas REALES (una respuesta, un diálogo) como hojas que entran en su palabra y se marcan en oro línea a línea",
        "when_not": "un vídeo o una web a 950 px (media.slot, media.capture_plane); algo que no sea una captura real",
    },
    "viz.sessions": {
        "file": "viz.sessions.js", "media": "optional",
        "props": _obj({
            "n": {"type": "integer", "minimum": 1, "maximum": 40, "description": "cuántas sesiones hay en el plano (un dato real con `source`, o las que diga)"},
            "bubble": STR, "bubble_idle": STR,
            "marker": {"type": "string", "description": "asset de la lupa que recorre las sesiones; sin él, un aro oro"},
            "steps": {"type": "array", "minItems": 1, "items": {"type": "object"},
                      "description": "guion de operaciones, cada una en su cue: pop, arrange, tone, marker_in, hop, marker_out, text, text_out, logo, logo_move, logo_out, collapse, wires, pulse, ring, swing, wires_out, logo_tone (detalle en viz.sessions.js). Coordenadas en px del lienzo: quien dirige comprueba la «T»"},
        }, ["n", "bubble", "steps"]),
        "dur_min": 1.5, "dur_rec": 5.0,
        "sfx": [],
        "cues_doc": "las que nombre cada step; eventos: enter, pop, arrange, marker, hop, text, mark, fly, logo, swing, wire, pulse, dim, light, exit",
        "when": "sesiones o conversaciones de un agente como enjambre de bocadillos: cuántas hay, que algo las recorre, se reparten, se funden en una o brotan de una; un solo plano vivo que cambia de composición en sus palabras",
        "when_not": "una lista de cosas distintas con nombre (logo.row, viz.session_tree); una interfaz real (captura)",
    },
    "viz.session_tree": {
        "file": "viz.session_tree.js", "media": "optional",
        "props": _obj({
            "mode": {"enum": ["build", "grow"], "default": "build", "description": "build = la carpeta y cada fila en su palabra; grow = nace una conversación, vuela a su rama y se fija arriba"},
            "head": {"type": "object", "properties": {"asset": STR, "label": STR}, "required": ["asset", "label"], "additionalProperties": False},
            "rows": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"type": "object", "properties": {"label": STR, "asset": STR, "cue": STR}, "required": ["label", "asset"], "additionalProperties": False}},
            "flag": {"type": "object", "properties": {"row": {"type": "integer", "minimum": 0, "maximum": 5}, "text": STR, "px": {"type": "integer", "minimum": 48, "maximum": 90}}, "required": ["text"], "additionalProperties": False,
                     "description": "build: la fila elegida con su coletilla en oro; las demás se apagan en la cue `dim`"},
            "born": {"type": "object", "properties": {"label": STR, "asset": STR, "idle_asset": STR, "agent": STR, "pin": STR}, "required": ["label", "asset"], "additionalProperties": False},
            "verbs": {"type": "array", "maxItems": 3, "items": {"type": "object", "properties": {"text": STR, "cue": STR}, "required": ["text", "cue"], "additionalProperties": False}},
            "top": {"type": "integer"}, "top_after": {"type": "integer"}, "row_h": {"type": "integer"}, "icon": {"type": "integer"}, "px": {"type": "integer"},
            "head_size": {"type": "integer"}, "head_px": {"type": "integer"}, "head_big": {"type": "integer"}, "head_big_y": {"type": "integer"}, "head_big_px": {"type": "integer"},
            "trunk_x": {"type": "integer"}, "arm": {"type": "integer"}, "born_big": {"type": "integer"}, "born_big_y": {"type": "integer"}, "born_big_px": {"type": "integer"},
            "card_y": {"type": "integer"}, "card_icon": {"type": "integer"}, "card_px": {"type": "integer"}, "agent_size": {"type": "integer"}, "pin_size": {"type": "integer"},
            "verbs_y": {"type": "integer"}, "verbs_px": {"type": "integer"},
            "recall": {**BOOL, "description": "grow: el árbol entra montado en el corte y la conversación nace suelta bajo él, sin título grande; cues born, proj, agent, wire, solid, place, ok, right, pin, glow"}, "agent_x": {"type": "integer"},
        }, ["head", "rows"]),
        "dur_min": 3.0, "dur_rec": 7.0,
        "sfx": [],
        "cues_doc": "build: head, settle, r0…r5, dim, flag · grow: tree, agent, solid, place, ok, pin, glow y las de `verbs`; grow + recall: además born, proj, wire y right (sin tree); eventos: enter, head, row, dim, flag, born, tree, agent, light, fly, branch, pin, glow, verb, exit",
        "when": "un proyecto y sus conversaciones como esquema de árbol dibujado (carpeta, ramas, filas con icono), o la conversación nueva que el agente crea, coloca y fija en ese árbol",
        "when_not": "enseñar la interfaz real de una herramienta de software (eso es una captura); filas sin nombre (no hay nada que colgar)",
    },
    "viz.search_tasks": {
        "file": "viz.search_tasks.js", "media": "optional",
        "props": _obj({
            "search": {"type": "object", "properties": {"hero": STR, "mark": STR, "icon": STR, "fast_icon": STR},
                       "required": ["hero"], "additionalProperties": False,
                       "description": "escena 1: barra de búsqueda que encuentra al instante; `hero` = la frase (Title Case), `mark` = trozo con rotulador"},
            "tasks": {"type": "object", "properties": {"hero": STR, "mark": STR, "icon": STR, "rows": {"type": "integer", "minimum": 2, "maximum": 4}},
                      "required": ["hero"], "additionalProperties": False,
                      "description": "escena 2: lista de tareas que se ejecuta y se marca sola"},
            "anchor": {"type": "number", "minimum": 0.2, "maximum": 0.8},
        }, ["search", "tasks"]),
        "dur_min": 2.5, "dur_rec": 4.5,
        "sfx": [],
        "cues_doc": "a_in (aparece la barra), a_fast (resultados al instante + héroe), a_mark, a_found (el resultado se marca), "
                    "b_in (pasa a las tareas), b_run (se ejecutan y se marcan), b_hero, b_mark; eventos: enter, burst, found, swap, tick, hero, mark",
        "when": "remate «encontrar la información más rápido / ejecutar tareas de forma más sencilla»: una búsqueda que acierta al "
                "instante y una lista de tareas que se marca sola, cada parte en su palabra",
        "when_not": "si no dice las dos cosas; interfaces reales (eso es una captura)",
    },
    "title.header": {
        "file": "title.header.js", "media": "optional", "overlay": True,
        "props": _obj({
            "text": STR, "asset": ASSET_ID,
            "y": {"type": "integer", "minimum": 120, "maximum": 1000, "default": 210, "description": "centro vertical (px)"},
            "size": {"type": "integer", "minimum": 40, "maximum": 120, "default": 68, "description": "cuerpo del nombre"},
            "logo_size": {"type": "integer", "minimum": 40, "maximum": 140, "description": "lado del logo (por defecto size×1,12)"},
            "from": {"type": "object", "additionalProperties": False, "properties": {
                "logo": {"type": "array", "items": NUM, "minItems": 3, "maxItems": 3},
                "text": {"type": "array", "items": NUM, "minItems": 3, "maxItems": 3}},
                "description": "geometría del héroe anterior en px del lienzo ({logo:[cx,cy,lado], text:[cx,cy,cuerpo]}): la cabecera nace ahí y se encoge a su sitio"},
            "hold": {"type": "number", "minimum": 0, "maximum": 1, "description": "s quieta en la posición del héroe antes de encogerse"},
            "tone": {"type": "string", "pattern": "^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$"},
        }, ["text"]),
        "dur_min": 1.0, "dur_rec": 8.0,
        "sfx": [],
        "cues_doc": "eventos: enter, move (el encogido desde el héroe)",
        "when": "cabecera fija pequeña (logo + nombre) durante un tramo de varias tarjetas (p. ej. «✳ Mods» en todo el gancho): "
                "con `from`, el héroe de logo.reveal se encoge a la cabecera sin desaparecer",
        "when_not": "un solo plano (basta el héroe); encima de la cara; títulos de sección (section.title)",
    },
    "viz.duel_board": {
        "file": "viz.duel_board.js", "media": None,
        "props": _obj({
            "sides": {"type": "array", "minItems": 1, "maxItems": 3, "items": {"type": "object", "properties": {
                "label": STR, "asset": {"type": "string", "description": "id del logo verificado sin «m_» (logo_nimbo…)"},
                "mono": {"type": "string", "maxLength": 4, "description": "sin logo: monograma de la ficha (p. ej. «REA»)"},
                "strike": {"type": "boolean", "description": "monograma tachado (el lado «sin»)"},
                "big": {"type": "boolean", "description": "monograma grande (~58 % de la baldosa), p. ej. el «?» del gancho"}},
                "required": ["label"], "additionalProperties": False},
                "description": "A (izquierda) y B (derecha), siempre en el mismo orden. UNO con `solo` (columna centrada) o TRES "
                               "en `table` sin «duel» ni carrera (fichas apiladas; celdas c0…c2)"},
            "solo": {"type": "boolean", "description": "table con un solo lado: una columna centrada (la ficha y sus cifras en el eje)"},
            "q": {"type": "boolean", "default": True, "description": "false = celdas sin «?» (vacías hasta su cifra)"},
            "text_in": {"type": "boolean", "description": "`title` y rótulos de fila entran con gx.textIn (8 f, suben 32 px), también en el corte"},
            "ghost": {"type": "boolean", "default": True, "description": "false = sin esqueleto fantasma de filas: cada fila (filete, rótulo, pistas) nace en su cue r<i>"},
            "cols_in": {"type": "boolean", "description": "filas en el corte: la pista y el divisor de cada columna entran con su ficha (cue h<i>), no antes"},
            "max_w": {"type": "number", "minimum": 300, "maximum": 950, "description": "ancho máximo del marcador en px, centrado (696 = zona de texto de Shorts, x 192–888)"},
            "mode": {"enum": ["table", "lanes", "pick"], "default": "table"},
            "title": {"type": "string", "description": "rótulo en oro sobre las fichas (cue «title»)"},
            "vs": {"type": "boolean", "description": "«vs» entre las fichas (solo en la primera aparición)"},
            "intro": {"anyOf": [{"type": "boolean"}, {"enum": ["duel"]}], "description": "true = las fichas entran cada una en su palabra (h0, h1); «duel» = gancho: fichas grandes + VS desde el fotograma 0 que se encogen a la cabecera en «title»"},
            "hero": {"type": "boolean", "description": "table: cada cifra entra GRANDE sobre el marcador velado y vuela a su celda"},
            "dim": {"type": "boolean", "default": True, "description": "lanes/pick: al empezar el lado B, el A se atenúa"},
            "rows": {"type": "array", "maxItems": 3, "items": {"type": "object", "properties": {
                "k": STR, "cue": STR, "bars": BOOL,
                "cells": {"type": "array", "maxItems": 3, "items": {"type": "object", "properties": {
                    "v": {"type": "string", "description": "la cifra tal como la dice quien habla («1 h 12 min», «19 $»); sin v = «?» (o vacía con q: false)"},
                    "n": {"type": "number", "minimum": 0, "description": "valor numérico REAL para la barra (misma unidad en la fila)"},
                    "cue": STR, "hot": BOOL,
                    "hero": {"type": "boolean", "description": "false = esta cifra entra en su celda aunque el marcador tenga `hero`"},
                    "run": {"type": "string", "description": "carrera: cue desde la que la barra corre (contador de minutos) hasta su cifra"}},
                    "additionalProperties": False}}},
                "required": ["k"], "additionalProperties": False}, "description": "table: criterio + dos celdas (A, B)"},
            "steps": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {
                "cue": STR, "hot": {"type": "array", "items": {"type": "string", "pattern": "^r[0-2]c[0-2]$"}}, "dim": BOOL},
                "additionalProperties": False}, "description": "table: el foco (oro) pasa a esas celdas"},
            "lanes": {"type": "array", "maxItems": 2, "items": {"type": "object", "properties": {
                "steps": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {"label": STR, "cue": STR,
                          "draw": {"type": "string", "description": "cue desde la que el raíl corre hasta este nodo"}},
                          "required": ["label"], "additionalProperties": False}},
                "end": {"type": "object", "properties": {"label": STR, "cue": STR, "kind": {"enum": ["stop", "done"]}},
                        "required": ["label"], "additionalProperties": False}}, "additionalProperties": False}},
            "cols": {"type": "array", "maxItems": 2, "items": {"type": "object", "properties": {
                "items": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {"label": STR, "cue": STR},
                          "required": ["label"], "additionalProperties": False}},
                "cue": {"type": "string", "description": "palabra en la que la ficha (la respuesta) se enciende; sin cue no sale"},
                "built": {"type": "boolean", "description": "columna heredada de la instancia anterior: ya construida en el corte"},
                "ring": {"type": "boolean", "description": "built: aro de oro de la ficha (false = ya sin foco)"}},
                "additionalProperties": False}},
        }, ["sides"]),
        "dur_min": 1.2, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "h0, h1, h2 (fichas) · title · eyebrow («duel»: el title sube en esa palabra durante el duelo) · table: r0…, celdas por su cue, s0… · lanes: cue de cada paso · pick: cue de cada criterio, p0/p1 (respuesta); eventos: enter, land, row, value, highlight, node, stop, pick, exit",
        "when": "Short «A contra B» (dos modelos, dos herramientas): el mismo marcador como hilo conductor: gancho (criterios con «?»), cifras reales con barras, cómo trabaja cada uno (carriles) y la recomendación (pick)",
        "when_not": "más de tres lados (tres solo en tabla); cifras que quien habla no dice o sin fuente; ganadores absolutos que quien habla no declara",
    },
    "viz.road": {
        "file": "viz.road.js", "media": None,
        "props": _obj({
            "steps": {"type": "array", "minItems": 2, "maxItems": 8, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "label": STR, "n": {"type": "integer"}}, "required": ["label"], "additionalProperties": False}]},
                "description": "los pasos en orden, con el rótulo de cada paso (Title Case corto)"},
            "title": STR, "top": {"type": "integer", "minimum": 1, "maximum": 8, "description": "nodos en el tramo de arriba"},
            "colors": {"type": "object", "properties": {"a": STR, "b": STR, "c": STR}, "additionalProperties": False},
            "focus": {"type": "array", "maxItems": 8, "items": {"type": "object", "properties": {
                "cue": STR, "lit": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 7}}, "dim": BOOL,
                "stagger": {"type": "number", "minimum": 0, "maximum": 0.5, "description": "s entre nodos al encenderse (recorrido 1→N)"}},
                "additionalProperties": False}},
            "built": {"type": "boolean", "description": "la carretera ya construida en el corte (vuelta al final)"},
            "nodes_first": {"type": "boolean", "description": "los pasos sueltos (sin carretera) en el corte; la carretera los une en `draw`"},
            "loose": {"type": "object", "properties": {
                "stagger": {"type": "number", "minimum": 0, "maximum": 0.5, "default": 0.12, "description": "s entre pasos al entrar"}},
                "additionalProperties": False,
                "description": "con nodes_first: los pasos entran uno a uno desperdigados y flotando; cada uno encaja en su sitio cuando el trazo llega a él"},
            "flow": {"type": "object", "properties": {
                "every": {"type": "number", "minimum": 0.1, "maximum": 1.5, "default": 0.42, "description": "s entre los dos primeros circulitos"},
                "accel": {"type": "number", "minimum": 0.6, "maximum": 1.0, "default": 0.84, "description": "cada hueco = el anterior × accel (cada vez más seguidos)"},
                "min": {"type": "number", "minimum": 0.08, "maximum": 1.0, "default": 0.16},
                "dur": {"type": "number", "minimum": 0.6, "maximum": 4.0, "default": 1.4, "description": "s de recorrido del paso 1 al último"}},
                "additionalProperties": False,
                "description": "circulitos (clientes, proyectos) que recorren la carretera ya hecha del primer paso al último, cada vez más seguidos: escalar"},
            "ghost": {"type": "boolean", "default": True, "description": "trazo fantasma desde el corte"},
            "label_px": {"type": "integer", "minimum": 44, "maximum": 72,
                         "description": "cuerpo de los rótulos (todos iguales, ≤ 2 líneas); su fila crece con él, el bloque se escala para caber y "
                                        "cada rótulo queda centrado bajo su nodo dentro del cuadro (sin pisar la curva ni salirse con `top: 2`)"},
        }, ["steps"]),
        "dur_min": 1.2, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "title, nodes (pasos sueltos), draw, drawn (fin), n0…n7 (el trazo llega a cada nodo en su palabra; sustituye a draw/drawn), flow (circulitos), f0… (focos); eventos: enter, node, highlight, exit",
        "when": "VETADO: el estilo de iconos 2D animados para «investigar / buscar / sintetizar» queda descartado. No usar; `ck validate` lo marca",
        "when_not": "siempre: para pasos en orden, el material real (prompt, pantalla, resultado) o la cara de la persona en cámara",
    },
    "viz.step": {
        "file": "viz.step.js", "media": "optional",
        "props": _obj({
            "step": {"type": "integer", "minimum": 1, "maximum": 8, "description": "el paso actual (1…total)"},
            "total": {"type": "integer", "minimum": 2, "maximum": 8, "default": 7},
            "top": {"type": "integer", "minimum": 1, "maximum": 8, "description": "pasos del primer tramo (color a); el tramo que sigue es la curva (b)"},
            "title": STR, "kicker": {"type": "string", "description": "por defecto «Paso N»"},
            "road": {"type": "boolean", "default": True, "description": "false = sin carretera (tarjeta de resultado)"},
            "checks": {"type": "boolean", "description": "cada punto con su casilla que se marca en su palabra (lo que funcionó)"},
            "points": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {
                "text": STR, "cue": STR, "mark": {"type": "string", "description": "trozo literal de `text` que se subraya"},
                "mark_cue": STR,
                "icon": {"type": "string", "description": "id del asset (icono del kit propio) que sustituye al punto o numeral"},
                "motion": {"enum": ["swing", "spin", "bob"], "description": "movimiento del icono tras entrar (vaivén, giro, flote)"}},
                "required": ["text"], "additionalProperties": False},
                "description": "frases CORTAS (≤ 6 palabras) de lo que dice quien habla en ese paso, en Title Case, cada una en su palabra"},
            "colors": {"type": "object", "properties": {"a": STR, "b": STR, "c": STR}, "additionalProperties": False},
            "foot": {"type": "object", "properties": {"text": STR, "mark": STR}, "required": ["text"], "additionalProperties": False,
                     "description": "línea final SIN casilla ni punto (una condición de lo anterior), en la cue «foot» (rotulador en «foot_mark»)"},
            "icon": {"type": "string", "description": "id del asset (objeto del kit) a la izquierda del título"},
            "static_title": {"type": "boolean", "description": "kicker, título e icono ya puestos en el corte (continúan el plano anterior)"},
            "numbered": {"type": "boolean", "description": "numerales en círculo oro en vez de puntos de color"},
            "point_px": {"type": "integer", "minimum": 34, "maximum": 80, "description": "cuerpo máximo de los puntos (52 por defecto)"},
            "icon_px": {"type": "integer", "minimum": 60, "maximum": 160, "description": "lado de los iconos de los puntos (104)"},
            "anchor": {"type": "number", "minimum": 0.2, "maximum": 0.8, "description": "centro vertical del bloque completo (fracción del lienzo)"},
            "recenter": {"type": "boolean", "description": "lo ya dicho queda centrado en el ancla y el bloque sube al sumarse cada fila (como timeline.steps)"},
        }, ["step", "title"]),
        "dur_min": 1.5, "dur_rec": 5.0,
        "sfx": [],
        "cues_doc": "kicker, title (cada uno en su palabra), p0…p3 (puntos), m0…m3 (rotulador), foot, foot_mark; eventos: enter, node, point, mark, exit",
        "when": "cada paso de un Short de «N pasos»: dónde estamos en el recorrido, el nombre del paso y lo que dice quien habla en frases cortas (en vez de una captura de un board o documento)",
        "when_not": "capturas reales que son la prueba (interfaces, resultados); frases largas (eso es el subtítulo)",
    },
    "viz.layer": {
        "file": "viz.layer.js", "media": None,
        "props": _obj({
            "top": {"type": "object", "properties": {"label": STR, "assets": {"type": "array", "maxItems": 3, "items": STR}},
                    "required": ["label"], "additionalProperties": False, "description": "arriba: quien usa la capa (p. ej. «Tu Agente» + logos verificados)"},
            "middle": {"type": "object", "properties": {"label": STR, "sub": STR}, "required": ["label"], "additionalProperties": False,
                       "description": "la capa (la herramienta), en oro"},
            "bottom": {"type": "object", "properties": {"label": STR, "tiles": {"type": "array", "maxItems": 3, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "asset": ASSET_ID, "glyph": STR, "tone": {"enum": ["gold", "ink", "white", "silver", "color"]}}, "additionalProperties": False}]}}},
                       "required": ["label"], "additionalProperties": False,
                       "description": "abajo: lo que la capa conecta (baldosas abstractas, nunca logos inventados); `tiles` = baldosas de estado con icono "
                                      "del kit o glifo en el oro del kit ([] = sin baldosas)"},
            "warn": {"type": "string", "description": "aviso rojo sobre la banda de abajo (palabras de quien habla)"},
        }, ["top", "middle", "bottom"]),
        "dur_min": 2.0, "dur_rec": 5.0,
        "sfx": [],
        "cues_doc": "layer, agent, tools, hard, flow; eventos: enter, land, node, warn, exit",
        "when": "una herramienta que es una CAPA INTERMEDIA entre dos cosas («conecta tu agente con…», «actúa como puente»): tres bandas y el flujo que baja",
        "when_not": "procesos de transformación de datos (flow.pipeline); comparar dos cosas (compare.vs)",
    },
    "viz.scope": {
        "file": "viz.scope.js", "media": None,
        "props": _obj({
            "label_small": STR, "label_big": STR,
            "mark": {"type": "string", "description": "trozo literal de label_big que se subraya"},
            "scope_label": {"type": "string", "default": "Alcance"},
            "colors": {"type": "object", "properties": {"warn": STR}, "additionalProperties": False},
        }, ["label_small", "label_big"]),
        "dur_min": 2.0, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "small, grow, diff; eventos: enter, grow, warn, mark, exit",
        "when": "«si no lo acotas, algo pequeño acaba siendo algo enorme/diferente» (alcance, scope creep): la solución dentro de su recuadro crece, brota fuera y el borde se pone rojo",
        "when_not": "crecimiento con cifras reales (chart.line); comparar dos cosas (compare.vs)",
    },
    "viz.many_to_one": {
        "file": "viz.many_to_one.js", "media": None,
        "props": _obj({
            "n": {"type": "integer", "minimum": 4, "maximum": 30, "default": 20, "description": "cuántos (la cifra que dice quien habla)"},
            "cols": {"type": "integer", "minimum": 2, "maximum": 8, "default": 5},
            "pick": {"type": "integer", "minimum": 0, "maximum": 29},
            "asset": {"type": "string", "description": "icono real del objeto elegido (kit propio; nunca un logo inventado)"},
            "label_many": STR, "label_one": STR,
            "one_glyph": {"enum": ["target"], "description": "sin asset: la elegida muestra una diana (un problema concreto)"},
            "glyphs": {"enum": ["bars", "varied"], "default": "bars",
                       "description": "varied: cada baldosa con una forma distinta («N servicios DISTINTOS»), abstracta"},
            "sub_one": {"type": "string", "description": "segunda línea bajo label_one, en la cue «sub»"},
            "zoom": ZOOM,
            "first_from": {"type": "number", "minimum": 0.4, "maximum": 1, "description": "si la cascada arranca en el corte (cue `all` ≤ inicio), la primera baldosa ya se ve en ese fotograma a esta opacidad (0,6): ningún fotograma en blanco"},
        }, ["label_many", "label_one"]),
        "dur_min": 1.5, "dur_rec": 5.0,
        "sfx": [],
        "cues_doc": "all, label, dim, pick, sub; eventos: enter, dim, pick, sub, exit",
        "when": "«no necesitas N cosas, solo una bien hecha»: muchas baldosas que se apagan y una que crece y se vuelve el objeto real",
        "when_not": "cifras que quien habla no dice; comparar dos cosas concretas (compare.vs)",
    },
    "viz.projects": {
        "file": "viz.projects.js", "media": None,
        "props": _obj({
            "mode": {"enum": ["chaos", "base", "repeat", "adapt", "grow"], "default": "chaos",
                     "description": "chaos: columnas con celdas TODAS distintas y «≠» rojo · base: la misma tabla ordenada (la "
                                    "solución se copia con «=» y cada copia cambia una pieza a oro) · repeat: el mismo "
                                    "proyecto cliente tras cliente, cada vez mejor (esquema sin cifras) · adapt: estructura "
                                    "principal + lo que se adapta encima · grow: la columna 1 se construye, se copia a la derecha SIN «=» "
                                    "y cada copia enciende más piezas en oro (1, 2, 3…): acumulativo"},
            "seed": {"type": "object", "properties": {"asset": ASSET_ID, "glyph": STR, "tone": {"enum": ["gold", "ink", "white", "silver", "color"]}},
                     "additionalProperties": False,
                     "description": "grow: la columna HEREDA la baldosa elegida del bloque anterior (asset o glifo; por defecto la diana): está grande en el "
                                    "centro en el corte y se vuelve la cabecera de la columna en «one»; las copias la llevan con su número en una chapa"},
            "from": {"enum": ["chaos"], "description": "base: la tabla del caos está en el corte y se ORDENA (antes/después)"},
            "ghost": {"type": "boolean", "description": "huecos punteados de cada pieza desde el corte (por defecto, no)"},
            "base_ghost": {"type": "string", "description": "adapt: rótulo del hueco de la base hasta la cue «base» (lo ya dicho)"},
            "cards": {"type": "array", "minItems": 2, "maxItems": 4, "items": {"type": "object", "properties": {"label": STR},
                      "required": ["label"], "additionalProperties": False},
                      "description": "columnas (clientes, proyectos, implementaciones) con las palabras de quien habla"},
            "rows": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {
                "label": STR, "kind": {"enum": ["tools", "process", "delivery", "time", "errors", "auto", "result", "meter", "icon"]}},
                "required": ["label"], "additionalProperties": False},
                "description": "filas con su rótulo; formas abstractas (baldosas, nodos, entregables; en repeat: tiempo, "
                               "errores, automatización, resultado), nunca logos. `meter` = un medidor por copia que se "
                               "llena más en cada una (1/n, 2/n…); `icon` = el icono real de la elegida (`seed`) en cada copia"},
            "big": {"type": "boolean", "description": "chaos: una forma grande por columna (gancho), sin filas"},
            "note": STR, "note2": {"type": "string", "description": "base: rótulo que sustituye a `note` en la cue note2/vary"},
            "kicker": STR, "base_label": STR, "stamp": STR,
            "items": {"type": "array", "maxItems": 6, "items": {"type": "object", "properties": {"label": STR},
                      "required": ["label"], "additionalProperties": False},
                      "description": "adapt: lo que se adapta, en Title Case, cada uno en su palabra (cues i0…i5)"},
        }, []),
        "dur_min": 1.5, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "chaos: c0…c3 (columnas), r0…r2 (filas), signs (big: «≠»), note, shake · base: one, copies, vary, note, "
                    "note2 · grow: one, note, copies, vary, note2 · repeat: c0…c2, r0…r3, best · adapt: kick, i0…i5, toggle, dim, base, same; eventos: enter, card, "
                    "row, note, copy, vary, grow (cada copia enciende sus piezas), best, item, toggle, base, stamp, exit",
        "when": "«cada cliente necesita algo distinto» frente a «una solución que adaptas con pequeñas variaciones»: la MISMA "
                "tabla en caos, ordenada y como estructura que no cambia",
        "when_not": "comparar dos productos o herramientas (compare.vs); cifras; formas que pretendan ser logos de marcas",
    },
    "viz.shapes": {
        "file": "viz.shapes.js", "media": None,
        "props": _obj({
            "tracks": {"type": "array", "minItems": 2, "maxItems": 4, "items": {"type": "object", "properties": {
                "label": STR, "glyph": STR, "asset": ASSET_ID,
                "mono": {"type": "string", "maxLength": 3, "description": "texto corto en el icono en vez de glifo («Aa» = textos)"}},
                "required": ["label"], "additionalProperties": False},
                "description": "tracks: pistas de la línea de tiempo (cabecera = icono del kit en oro o `mono` + rótulo), cada una en su cue k<i>"},
            "sync_at": {"type": "number", "minimum": 0.15, "maximum": 0.85, "description": "tracks: columna de sincronía (fracción de la zona de clips, 0,15–0,55; 0,3)"},
            "track_in": {"enum": ["cut", "cue"], "description": "tracks: `cue` = la cabecera y el carril de cada pista entran en SU cue k<i>, con su clip (no se ve un esqueleto de carriles con rótulos antes de que quien habla los diga). Sin la prop, todo en el corte"},
            "sync_equal": {"type": "boolean", "description": "tracks: en `sync` los clips quedan del MISMO largo (la media). Sin la prop, cada uno el suyo"},
            "ring_gap": {"type": "boolean", "description": "loop: el trazo del aro se corta alrededor de cada rótulo (máscara del color del lienzo): el ciclo no atraviesa el texto. Sin la prop, como siempre"},
            "stations_in": {"enum": ["cut", "cue"], "description": "loop: `cue` = cada estación (forma y rótulo) entra en SU cue r<k> (r0, r1…); el aro, en el corte. Sin la prop, todas en el corte"},
            "track_heads": {"enum": ["left", "above"], "description": "tracks: `above` = icono y rótulo de cada pista ENCIMA de su carril y los carriles a todo el ancho útil (65–888) a pantalla completa, más grande; por defecto, la columna de cabeceras a la izquierda"},
            "mode": {"enum": ["morph", "hub", "loop", "dial", "tracks"], "default": "morph",
                     "description": "morph: una forma grande que cambia por completo con cada cliente · hub: red radial (tú, "
                                    "oportunidades, servicios, posibilidades, el primer cliente) · loop: ciclo que se recorre "
                                    "cada vez más rápido con estaciones que se encienden · dial: reloj de 24 h de instrumento "
                                    "(esfera, bisel, 24 marcas), la aguja barre la vuelta en `sweep` dejando el arco de oro, estaciones con "
                                    "icono del kit en las diagonales en su cue mientras la aguja las señala, `center` en c0; luego la aguja "
                                    "avanza una hora por segundo"},
            "ticks": {"type": "integer", "minimum": 8, "maximum": 60, "description": "dial: marcas de la esfera (24)"},
            "range": {"enum": [24, 60], "default": 24, "description": "dial: 24 (horas) o 60 (cronómetro de «1 minuto»: 60 marcas, la aguja avanza un segundo por segundo)"},
            "sweep_to": {"type": "number", "exclusiveMinimum": 0, "maximum": 1,
                         "description": "dial: fracción de vuelta del barrido (p. ej. 0.0833 = 5 de 60) = CRONÓMETRO de «unos pocos minutos»: "
                                        "la aguja sale de las 12 y barre en 22 f hasta ahí con el arco detrás, luego avanza continua (1 marca/s) hasta la "
                                        "última estación (o la cue `stop`), frena en 6 f y sigue a saltos. Sin `sweep_to`, la vuelta entera de siempre"},
            "plate": {"enum": ["bottom", "center"], "description": "dial: placa del rótulo central a las 6 sobre el bisel (bottom; por defecto con sweep_to: la aguja nunca pasa por debajo) o encima del eje (center)"},
            "stations_at": {"enum": ["sides", "diagonals"], "description": "dial: estaciones a los dos lados (9 y 3, separadas del bisel; por defecto con sweep_to) o en las diagonales"},
            "stations_ghost": {"type": "boolean", "description": "dial: las estaciones esperan en fantasma (0,36) desde el corte y se encienden en su cue (por defecto con sweep_to)"},
            "advance": {"enum": ["continuous", "ticks"], "description": "dial: tras el barrido, avance continuo (por defecto con sweep_to) o a saltos de una marca"},
            "zoom": ZOOM,
            "sweep_from": {"type": "number", "exclusiveMinimum": 0, "maximum": 1, "description": "dial con sweep_to: la esfera NACE ya en esa fracción (aguja y arco puestos en el corte: la vuelta de un dial que ya se vio); igual a sweep_to = sin barrido ni eventos dial/dial_end"},
            "cards": {"type": "array", "minItems": 2, "maxItems": 4, "items": {"type": "object", "properties": {"label": STR},
                      "required": ["label"], "additionalProperties": False}},
            "note": STR, "kicker": STR, "center": STR, "client": STR,
            "pick": {"type": "integer", "minimum": 0, "maximum": 11},
            "scale_max": {"type": "number", "minimum": 1.0, "maximum": 1.4, "description": "loop: tope de escala del aro (1,1 por defecto; a pantalla completa 1,3 ≈ aro de 800 px)"},
            "stations": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {
                "label": STR, "kind": {"enum": ["time", "errors", "auto", "result"]}, "asset": ASSET_ID, "glyph": STR,
                "tone": {"enum": ["gold", "ink", "white", "silver", "color"]},
                "slot": {"type": "integer", "minimum": 0, "maximum": 3, "description": "dial: hueco del reparto que ocupa (con «sides»: 0 izquierda, 1 derecha) en vez del de su orden"}}, "additionalProperties": False},
                "description": "loop/dial: estaciones; `asset` (icono del kit) o `glyph` en el ORO DEL KIT en vez del glifo de línea genérico (encendida = aro de tinta); `slot` (dial) para fijar el lado"},
        }, []),
        "dur_min": 1.5, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "morph: c0…c3, signs, note · hub: kick, opps, services, spread, client · loop: kick, c0…c3, r0…r3, best · "
                    "tracks: k0…k3 (cada pista), sync (el cabezal llega y las claves se alinean en oro) · "
                    "dial: c0 (rótulo central, en placa por encima del eje o a las 6 con `plate: bottom`), plate_pulse (la placa late en esa palabra; evento pulse), sweep (o best: la vuelta o el barrido hasta `sweep_to`), "
                    "r0…r3 (estaciones), stop (opcional, con sweep_to: dónde frena el avance continuo; por defecto la última estación); "
                    "eventos: enter, morph, note, opps, node, spread, client, lap, station (+2 f del encendido), best, dial (barrido), dial_end (el arco llega; "
                    "con sweep_to a +18 f del barrido), exit",
        "when": "ideas que piden FORMA y no tabla: algo que cambia del todo (morph), muchas posibilidades alrededor de ti (hub), "
                "repetir lo mismo cada vez mejor (loop)",
        "when_not": "listas de texto (eso es el subtítulo); cifras; formas que pretendan ser logos",
    },
    "viz.crm": {
        "file": "viz.crm.js", "media": None,
        "props": _obj({
            "rows": {"type": "integer", "minimum": 3, "maximum": 6, "default": 5, "description": "filas de la lista (esqueleto: sin nombres ni datos)"},
            "lit": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 5},
                    "description": "filas que se encienden en oro, en orden, cada una en su cue r0, r1… (por defecto, todas)"},
            "title": {"type": "string", "description": "titular opcional (palabras de quien habla, Title Case); sube por su máscara en «title»"},
            "anchor": {"type": "number", "minimum": 0.2, "maximum": 0.8},
            "ink": {"type": "boolean", "description": "filas en tinta al 50 % (no el esqueleto gris al 18 %): la lista se lee y el apagado de `dim` se nota"},
            "stamp": {"type": "string", "description": "sello de tinta (Title Case, palabras de quien habla) que cae sobre la tarjeta en la cue `stamp`, girado −6°; el texto sube por su máscara; evento stamp (sin sonido en el mapa)"},
            "stamp_sub": {"type": "string", "description": "segunda línea en una píldora de tinta bajo el sello, en la cue `stamp_sub` (p. ej. «Hace 2 Meses»); evento stamp_sub"},
            "stamp_sub_min": {"type": "integer", "minimum": 44, "maximum": 72, "description": "cuerpo mínimo de `stamp_sub` (48 por defecto)"},
            "count": {"type": ["string", "integer"], "description": "la cifra que dice quien habla (p. ej. «200»): cabecera DENTRO de la tarjeta, la cifra grande (150·s) y debajo `title`, cada uno por su máscara (cues count y title); la tarjeta entra sin fundir y el sello se centra sobre las filas. las filas ya están en el corte al 15 % y se entintan en la cue `rows`; el texto del sello sube con su caja. Nunca rueda"},
            "zoom": ZOOM,
            "card_w": {"type": "integer", "minimum": 560, "maximum": 820, "description": "ancho de la tarjeta en px, centrada (por defecto 820·s, solo en la banda alta 288–1000); con la prop, el bloque usa la banda ENTERA de pantalla completa (288–1240) y la tarjeta puede bajar de y=1000 si cabe en 696 px (680 → x 200–880): más alta con `rows` 6 en vez de ancha"},
            "title_to": {"type": "string", "description": "con `count`: en la cue `title_to` el título cambia (el viejo sale por arriba y se apaga en 5 f; el nuevo sube 5 f después, sin pisarse), p. ej. «Leads Antiguos» → «Leads Pagados»"},
            "rows_with_card": {"type": "boolean", "description": "las filas (no son texto) están YA con la tarjeta en el corte y la tarjeta no funde desde 0 (solo se asienta de 0,97 a 1): ningún fotograma en blanco ni tarjeta vacía en el relevo"},
        }, []),
        "dur_min": 1.5, "dur_rec": 4.0,
        "sfx": [],
        "cues_doc": "title, count y title_to (con `count`), rows (entran las filas; por defecto en el corte), dim (se apagan: «olvidados»), r0…r5 (cada fila de `lit` se enciende en oro), stamp y stamp_sub (con sus props); eventos: enter, row, dim, light, stamp, stamp_sub, exit",
        "when": "una base de contactos o un CRM («contactos que llevan meses olvidados en un CRM… los vuelves a contactar»): filas en esqueleto con el glifo de usuario que se apagan y se encienden en oro en su palabra",
        "when_not": "datos o nombres concretos (eso sería inventar); listas de texto (subtítulo)",
    },
    "card.lesson": {
        "file": "card.lesson.js", "media": "optional",
        "props": _obj({
            "kicker": {"type": "string", "description": "rótulo pequeño sobre el marco (p. ej. «Clase Gratuita»)"},
            "title": {"type": "string", "description": "título de la clase en Title Case, tal cual se dice o se anuncia"},
            "badge": {"type": "string", "description": "sello oro (p. ej. «Gratis»)"},
            "badge_inset": {"type": "boolean", "description": "el sello DENTRO de la esquina del marco (18 px·s, −6°); "
                            "por defecto sobresale por arriba y puede salir de la zona segura"},
            "y": {"type": "integer", "minimum": -400, "maximum": 400,
                  "description": "desplazamiento vertical del bloque en px (+ abajo); se limita para no salir de la banda"},
            "image": {**ASSET_ID, "description": "asset de imagen que llena el marco: 16:9 en el de vídeo (un fotograma real del largo o su "
                      "miniatura elegida; el play va ENCIMA), A4 vertical en `frame: page` (la portada real de la guía); va también en `assets` de la decisión"},
            "point_arrow": {"type": "boolean", "description": "flecha oro bajo el marco de vídeo que baja y rebota desde `cues.arrow` («aquí abajo»); opcional, por plan"},
            "play_button": {"type": "boolean", "description": "con `image` en el marco de vídeo, el botón de play va encima por defecto; false lo quita (el marco acusa la pulsación)"},
            "frame": {"enum": ["video", "page"], "default": "video",
                      "description": "video = marco 16:9 con play y barra; page = documento vertical A4 (−3°, sombra suave) para una GUÍA: con `image` la "
                                     "página es la imagen; sin ella, un documento genérico con líneas (nunca un rectángulo negro); sin play ni barra; `badge_inset` en su esquina"},
        }, []),
        "dur_min": 1.2, "dur_rec": 2.6,
        "sfx": [{"at": "badge", "offset": 0.0, "kind": "stamp"}, {"at": "play", "offset": 0.1, "kind": "click"}],
        "cues_doc": "title (sube el título; `title` es opcional: sin él la imagen ocupa el bloque), badge (el sello IMPACTA en la cue —aparece grande y cae 6 f "
                    "antes—; sin la cue, ~0,45 s después del título; ponla en la palabra «gratis»), play (pulsa el play —o el marco con `image` y "
                    "`play_button: false`— y la barra empieza a avanzar; la página no tiene play). El título queda ≥ 72 px sobre la caja del subtítulo (sin título, el marco ≥ 60 px). "
                    "Eventos: enter, badge (fotograma del impacto; antes «stamp»), play, exit",
        "when": "anunciar una clase/vídeo gratuito real (outro): marco 16:9 con play, título y sello «Gratis»; una guía gratuita real: `frame: page` con su portada",
        "when_not": "inventar duración, visitas, plataformas o caras; enseñar contenido de la clase",
    },
    "logo.row": {
        "file": "logo.row.js", "media": "required",
        "props": _obj({
            "items": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"type": "object", "properties": {
                "label": STR, "asset": ASSET_ID,
                "hot": {"type": "boolean", "description": "el foco del plano: aro de oro en la baldosa y rótulo en oro"},
                "fill": {"type": "number", "minimum": 0.62, "maximum": 0.9, "description": "fracción de la baldosa que ocupa el icono (0,62 por defecto); p. ej. 0,84 para un objeto apaisado que si no queda pequeño"},
                "grow": {"type": "object", "properties": {"from": STR, "to": STR, "scale": {"type": "number", "minimum": 1.02, "maximum": 1.25}},
                         "required": ["from", "to"], "additionalProperties": False,
                         "description": "entre las cues `from` y `to` la baldosa crece a saltos (contador sin cifra) hasta `scale` (1,14); evento grow"},
                "glyph": {"enum": ["mail", "chat", "wave", "keys", "terminal", "braces", "screen", "play", "doc", "gear", "search", "globe", "user",
                                   "clock", "calendar", "bolt", "chart", "check", "star", "phone", "clip", "text", "coin"],
                          "description": "sin asset: glifo neutro de trazo de tinta (por defecto, por el nombre: email→mail, sms→chat, voz→wave, cli/terminal→terminal, json/api→braces, after effects/animación→keys; si no, screen). keys = dos fotogramas clave sobre su pista con la curva de ease; terminal = «>_» con cursor que parpadea; braces = «{ }». `text` = monograma, NUNCA para una marca de terceros"}},
                "required": ["label"], "additionalProperties": False},
                "description": "cada herramienta en su palabra; sin `asset` → baldosa de texto del mismo tamaño (glifo neutro, nunca un icono de marca inventado)"},
            "zoom": ZOOM,
            "label_gap": {"type": "integer", "minimum": 6, "maximum": 26, "description": "hueco baldosa → rótulo en px (26 por defecto); el alto reservado al rótulo baja lo mismo: el rótulo queda pegado a SU baldosa (con `row_gap` 56, lejos de la siguiente)"},
            "size": {"type": "integer", "minimum": 120, "maximum": 420, "description": "px de baldosa (por defecto: pantalla completa 2 → 360, 3 → 320, 4–5 → 300 en 2 filas; split 280)"},
            "compact": BOOL, "labels": BOOL, "ghost": {"type": "boolean", "default": False, "description": "true = todas las ranuras en fantasma desde el corte (SOLO el contorno, sin «?»; entran en 6 f) y cada una se enciende en su palabra; la fila no se recoloca"},
            "rows": {"type": "array", "items": {"type": "integer", "minimum": 1, "maximum": 4}, "maxItems": 3,
                     "description": "reparto por filas (suma = nº de items), p. ej. [2, 3]: agrupa por sentido (plataformas arriba, canales abajo)"},
            "cy": {"type": "integer", "minimum": 400, "maximum": 1500,
                   "description": "centro vertical del bloque en px del lienzo (p. ej. 960, centrado en pantalla); las filas quedan fijas desde el corte (sin salto al nacer la segunda) y, en la «T», caben en 696 px"},
            "dim_items": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 4},
                          "description": "en la cue `dim` esas baldosas y sus rótulos bajan al 38 % (siguen leyéndose; evento off)"},
            "label_px": {"type": "integer", "minimum": 38, "maximum": 72, "description": "tope del cuerpo de los rótulos (todos iguales; baja para dejar ≥ 0,25 × baldosa entre vecinos)"},
            "connect": {"anyOf": [BOOL, {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 4}, "minItems": 2},
                                  {"type": "array", "items": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 4}, "minItems": 2, "maxItems": 2}, "minItems": 1}],
                        "description": "circuito de tinta + oro de baldosa en baldosa (true = todas en orden; [2, 3, 4] = solo esas, en cadena; [[2, 3], [3, 4]] = pares): cada tramo se dibuja "
                                       "cuando entra su baldosa y un pulso oro recorre el circuito mientras dura el plano. Las baldosas conectadas son más pequeñas "
                                       "(hueco ≥ 0,4 × baldosa) para que el trazo se lea; si cruza filas, esas filas quedan fijas desde el corte"},
            "cross_pair": {"type": "integer", "minimum": 0, "maximum": 3, "description": "con la cue `cross`: qué tramo del circuito se rompe (índice del par de `connect`; 0)"},
            "cross_tone": {"enum": ["red", "ink"], "description": "disco del «×» de la cue `cross`: rojo del kit (por defecto) o tinta"},
            "cross_item": {"type": "integer", "minimum": 0, "maximum": 4, "description": "SIN `connect`: en la cue `cross` el disco con «×» cae sobre esa baldosa (abajo a la derecha) y la baldosa y su rótulo bajan al 38 %; evento off"},
            "crosses": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"type": "object", "properties": {"item": {"type": "integer", "minimum": 0, "maximum": 4}, "cue": STR},
                        "required": ["item", "cue"], "additionalProperties": False},
                        "description": "SIN `connect`: como `cross_item` + `cross`, pero en varias baldosas, cada una en su cue (la lista acaba junta); evento off"},
            "row_gap": {"type": "integer", "minimum": 8, "maximum": 56, "description": "a pantalla completa, hueco entre filas en px (56 por defecto): más bajo = baldosas más grandes en una columna 1+1+1"},
            "first_from": {"type": "number", "minimum": 0.4, "maximum": 1, "description": "la primera baldosa, si entra en el corte, ya se ve en ese fotograma a esa opacidad (escala 0,92 → 1): ningún fotograma en blanco en el relevo"},
            "label_band": {"enum": ["row"], "description": "a pantalla completa, cada rótulo se mide contra el ancho seguro de SU altura (950 px si acaba por encima de y=1000, 696 si no) en vez de 696 para todos: en una columna 1+1+1, el rótulo largo del medio cabe en una línea al cuerpo del grupo"},
            "label_min": {"type": "integer", "minimum": 30, "maximum": 72, "description": "cuerpo mínimo de los rótulos antes de partirlos en dos líneas (38 por defecto): con 52, «Cualquier Proceso» pasa a «Cualquier / Proceso» a ≥ 52 px en vez de una línea a 38"},
            "label_two_px": {"type": "integer", "minimum": 64, "maximum": 120, "description": "a pantalla completa, TODOS los rótulos en dos líneas equilibradas al mayor cuerpo ≤ esta cifra que quepa en el ancho seguro (696 px en la «T»), nunca bajo `label_min`: frases largas en una columna 1+1+1 a ~90 px en vez de una línea a ~63. Sin la prop, nada cambia"},
            "connect_route": {"enum": ["straight"], "description": "con `connect`: baldosas en columna (mismo centro) unidas por un trazo RECTO vertical (de debajo del rótulo de arriba a la baldosa de abajo) en vez del codo por la derecha"},
            "split_row_gap": {"type": "integer", "minimum": 8, "maximum": 80, "description": "hueco entre filas fuera de pantalla completa (50/50; 0 por defecto): los rótulos de arriba no tocan las baldosas de abajo"},
            "stack_gap": {"type": "integer", "minimum": 60, "maximum": 200, "description": "hueco entre filas a pantalla completa que manda sobre row_gap (columna con circuito recto: con 140 el trazo mide ≥ 90 px)"},
            "reserve": {"type": "boolean", "description": "cada baldosa nace en su sitio FINAL: las filas no se recentran al llegar la siguiente"},
            "cell_gap": {"type": "integer", "minimum": 16, "maximum": 200, "description": "rejilla de verdad: cada celda mide lo que su baldosa y entre columnas hay este hueco (px); con filas [2, 2], las mismas columnas arriba y abajo. Sin la prop, cada celda mide lo que su rótulo"},
            "solo_size": {"type": "integer", "minimum": 160, "maximum": 640, "description": "a pantalla completa y con 2+ filas: mientras la PRIMERA baldosa está sola, mide eso (px) y baja a su tamaño con el mismo movimiento con el que su fila sube al nacer la segunda (8 f, move); su rótulo, siempre a su cuerpo, baja con el borde de la baldosa. Sin `reserve` ni `cy`. Sin la prop, igual"},
            "merge": {"type": "object", "properties": {"asset": ASSET_ID, "glyph": STR, "label": STR,
                                                       "tone": {"enum": ["gold", "ink", "white", "silver", "color"]}},
                      "additionalProperties": False,
                      "description": "en la cue «merge» las baldosas vuelan al centro y se juntan en UN icono final (asset con su color o glifo en el oro del kit) con `label` debajo"},
        }, ["items"]),
        "dur_min": 1.2, "dur_rec": 2.6,
        "sfx": [],
        "cues_doc": "<label en minúsculas sin espacios ni tildes> (nimbo, acmeflow, agenda…) o i0, i1…; pulse_all (todas las baldosas presentes laten a la vez, sin destacar ninguna; evento pulse); merge (se juntan en el icono final); "
                    "off (las baldosas encendidas se apagan y vuelve su contorno fantasma; rótulos al 35 %; p. ej. en «sino» tras «no tanto… sustituir»); "
                    "cross (con `connect`: el tramo `cross_pair` se rompe en esa palabra —el pulso para, el trazo baja al 22 % y cae un disco con «×»—; evento off); "
                    "hot (las baldosas `hot` se encienden EN esa palabra —aro y rótulo en oro— en vez de desde que entran; evento hot, sin sonido en el mapa); "
                    "eventos: logo por baldosa, connect (cada tramo del circuito), merge, off, exit. A pantalla completa los rótulos van a ≥ 48 px en una línea si "
                    "caben con 1 em de hueco real entre vecinos dentro de la banda segura",
        "when": "se nombran varias herramientas o modelos seguidos: cada logo en su palabra (cue = label en minúsculas: nimbo, acmeflow…); con 4–5 en pantalla completa, rejilla 2+2 / 3+2",
        "when_not": "lo genérico («otros modelos») no lleva logo; un solo nombre propio → logo.reveal",
    },
    "logo.reveal": {
        "file": "logo.reveal.js", "media": "required",
        "props": _obj({
            "asset": ASSET_ID, "name": STR, "by": STR,
            "by_mark": {"type": "string", "description": "trozo literal de `by` con el rotulador oro (en la cue «by»)"},
            "sweep": {"type": "boolean", "default": False, "description": "barrido de luz recortado a la forma del logo"},
            "size": {"type": "integer", "minimum": 120, "maximum": 520},
            "minimal": {"type": "boolean", "description": "logo grande y rápido por nombre (0,5–0,8 s), sin barrido ni autoría; con cue «name», el nombre entra en su palabra"},
            "name_size": {"type": "integer", "minimum": 80, "maximum": 320, "description": "cuerpo máximo del nombre (héroe bajo el logo)"},
            "name_lines": {"enum": [1, 2], "description": "2 = el nombre en DOS líneas equilibradas (corte por la palabra que deja la línea más ancha más corta) al mayor cuerpo ≤ `name_size` que quepa en el ancho (696 px en la «T»): «Mejores / Oportunidades» a ~90 px en vez de una línea a ~60. Sin la prop, una línea como siempre"},
        }, ["asset"]),
        "dur_min": 0.45, "dur_rec": 1.2,
        "sfx": [{"at": "enter", "offset": 0.0, "kind": "impact"}],
        "cues_doc": "logo (opcional; si no, en el corte), name (el nombre en su palabra), by (la coletilla en su palabra; con `by_mark`, el subrayado oro "
                    "6 f después). con `by_mark` la coletilla es SEGUNDO NIVEL (500, 44 px, blanco al 75 %, «Una Forma Diferente / de "
                    "Trabajar»); con `band: center` el bloque se centra en y ≈ 880 y acaba ≥ 120 px sobre el subtítulo (reserva el raíl). "
                    "Eventos: logo, enter, name, mark (fotograma en que la barra oro ya se ve), exit",
        "when": "revelación del nombre de la herramienta o marca (la palabra exacta), con layout broll_full o card_float",
        "when_not": "si la cara debe quedarse en la palabra clave (entonces el logo va detrás o al lado del sujeto)",
    },
    "flow.pipeline": {
        "file": "flow.pipeline.js", "media": "optional",
        "props": _obj({
            "steps": {"type": "array", "maxItems": 5, "items": {"type": "object", "properties": {
                "label": STR, "kind": {"enum": ["messy", "model", "structured", "target"]}, "asset": ASSET_ID,
                # ya lo leía el componente (icono central); se declara para que el plan valide
                "tone": {"enum": ["gold", "ink", "white", "silver", "color"], "default": "gold",
                         "description": "tinte del icono central en `inputs: tiles` (gold = oro del kit; color = el logo con sus colores verificados)"}},
                "required": ["label"], "additionalProperties": False}},
            "cards": {"type": "array", "maxItems": 3, "items": {"anyOf": [STR, {"type": "object", "properties": {"eyebrow": STR, "text": STR,
                      "glyph": {"enum": ["play", "wave", "screen", "mail", "chat", "phone", "clock", "calendar", "check", "bolt", "chart", "user", "doc", "gear", "search", "globe", "star", "keys", "terminal", "braces"]},
                      "asset": ASSET_ID, "tone": {"enum": ["ink", "gold", "white", "silver", "color"]}}, "required": ["text"]}]},
                      "description": "entradas de papel (texto real; eyebrow opcional: «Email», «Lead», «Tarea»); con inputs «tiles»: baldosa con `glyph` (o `asset`) y `text` como rótulo"},
            "inputs": {"enum": ["cards", "tiles"], "default": "cards",
                       "description": "tiles: entradas como BALDOSAS rectas con glifo (play, wave, screen por defecto) a ≥ 48 px, cada una en su cue c0…c2; en "
                                      "`transform` vuelan dentro del icono central y desaparecen (sin huellas), el plano sube y sale la publicación como tarjeta de post "
                                      "en esqueleto (avatar, dos líneas e imagen); rótulos ≥ 48 px. El icono central (`steps[kind=model].asset`) va en el oro del kit"},
            "outputs": {"type": "array", "maxItems": 3, "items": {"anyOf": [STR, {"type": "object", "properties": {"key": STR, "value": STR}, "required": ["value"]}]},
                        "description": "salidas tipadas reales «clave: valor» → fichas de tinta con mono blanco"},
            "labels": {"type": "object", "properties": {"top": STR, "bottom": STR}, "additionalProperties": False,
                       "description": "etiquetas espejo (palabras de quien habla): «información desordenada» / «salida útil»; se omiten si no caben"},
            "target": STR,
            "layout": {"enum": ["vertical", "columns"], "default": "vertical",
                       "description": "vertical: fichas apiladas → logo → barras de tinta, eje x=540; columns: 3 columnas (antiguo)"},
            "clip": {"anyOf": [BOOL, {"type": "object", "properties": {"keep": {"type": "array", "items": {"type": "array", "items": {"type": "integer", "minimum": 0, "maximum": 7}}}},
                                       "additionalProperties": False}],
                     "description": "inputs tiles: paso de transformación entre el icono central y la publicación: tira de clip de 8 fotogramas; los "
                                    "segmentos `keep` (por defecto [[1,2],[4],[6]]) se encienden en oro en «clip» y se recortan (lo demás cae y se juntan) en «trim»"},
            "platform": {"enum": ["linkedin", "instagram"], "description": "inputs tiles: la tarjeta de post con el marco de la red (cabecera, texto, imagen y "
                                                                           "fila de acciones con glifos neutros)"},
            "platform_asset": {**ASSET_ID, "description": "logo verificado de la red en la cabecera del post (tk assets logo)"},
            # modo agente → app con las vías como ranuras
            "agent": {"type": "object", "properties": {
                          "glyph": {"enum": ["robot", "user", "chat", "bolt", "gear", "terminal", "screen", "keys"], "default": "robot",
                                    "description": "robot = el MISMO robot de viz.layers_control (insignia de tinta, trazo oro)"},
                          "label": {**STR, "description": "rótulo bajo la insignia (≥ 48 px), entra por máscara en la cue `agent`; por defecto labels.top"},
                          "count": {"type": "integer", "minimum": 1, "maximum": 3, "default": 1, "description": "insignias superpuestas (varios agentes)"}},
                      "additionalProperties": False,
                      "description": "MODO AGENTE (manda sobre inputs/layout): arriba el agente (insignia + rótulo), abajo la app "
                                     "(steps[kind=model].asset, 320 px, desde el corte) y entre ambos las `cards` (≤ 3, 260 px) en ranuras "
                                     "fantasma simétricas reservadas desde el corte; la del centro va sobre el conector, las laterales con su "
                                     "carril. En pantalla completa todo entre y=420 y y=1248. Cues: agent, link, pulse, lanes, c0…c2, transform"},
        }, []),
        "dur_min": 2.5, "dur_rec": 6.0,
        # transform: soplido corto (≤ 0,4 s, −14 LU) al cruzar por detrás del logo; output: la «elección» cierra la
        # escalera de viz.decision (firma_1, +3 st). cutkit.audio.sfxplan los alinea a los eventos flip/option
        "sfx": [{"at": "transform", "offset": 0.0, "kind": "whoosh", "rel_lu": -14.0, "max_s": 0.4},
                {"at": "output", "offset": 0.0, "kind": "pop", "file": "firma_1", "pitch": 3.0, "rel_lu": -16.0,
                 "signature": "viz.decision"}],
        "cues_doc": "messy (caen las fichas), label_top (+ label_top2: 2.ª palabra), transform (pasan por detrás del logo: papel → tinta), label_bottom, output · inputs tiles: c0…c2 (cada baldosa), label_top, transform (se funden en el icono), clip (segmentos en oro), trim (recorte), output (sale el post), label_bottom; eventos: enter, card_drop, flip, merge (la última entra en el icono), clip, trim, lock (el post se asienta), exit · agent: agent (insignia + rótulo), link (se dibuja el conector agente → app; evento al tocar la app), pulse (un pulso oro llega a la app), lanes (carriles fantasma de las vías laterales), c0…c2 (cada vía encaja en su ranura y su carril se enciende), transform (un pulso por carril a la vez, la app se enciende); eventos: enter, agent, link, pulse, card_drop, merge, exit, todos en el fotograma del impacto y nunca después de t1",
        "when": "información desordenada → modelo → salida estructurada → destino: tres bandas a todo el ancho con Flip en «transform»",
        "when_not": "pasos de un tutorial con captura real (mejor split con la captura de cada paso)",
    },
    "title.lockup_hero": {
        "file": "title.lockup_hero.js", "media": None,
        "props": _obj({
            "lines": {"type": "array", "minItems": 1, "maxItems": 5, "items": {"anyOf": [STR, {"type": "object", "properties": {
                "text": STR, "role": {"enum": ["lead", "word", "hero"]}, "cue": STR},
                "required": ["text"], "additionalProperties": False}]}},
            "align": {"enum": ["left", "center"], "default": "left"},
            "hero_color": {"enum": ["accent", "white", "accent2"], "default": "accent"},
            "position": {"enum": ["top", "center", "bottom"], "default": "center"},
            "over_face": {"type": "boolean", "description": "sobre la cara: franja superior (36 %) con velo oscuro funcional detrás"},
            "tee": {"type": "boolean", "description": "a pantalla completa: banda en «T» (con band center, 460–1460) y toda línea a ≤ 696 px, así que el bloque puede centrarse en el lienzo y bajar de y=1000; sin la prop, la banda alta de siempre"},
            "scale_max": {"type": "number", "minimum": 1.0, "maximum": 1.4, "description": "multiplica los cuerpos de referencia (héroe 184, palabra 150, entrada 84) antes del ajuste al ancho; sin la prop, 1"},
        }, ["lines"]),
        "dur_min": 1.2, "dur_rec": 2.8,
        "sfx": [],
        "when": "momento tipográfico de sección, gancho o resumen: conectores en sans y UNA palabra emocional en Montserrat 900 gigante (nunca serif)",
        "when_not": "como subtítulo (eso es el raíl); más de una palabra héroe; frases de más de 6 palabras",
    },
    "demo.snippet": {
        "file": "demo.snippet.js", "media": None,
        "props": _obj({
            "kind": {"enum": ["chat", "email", "code", "json"], "default": "chat"},
            "typed": {"type": "boolean", "description": "chat: las burbujas del usuario se escriben LETRA A LETRA (hasta la cue w<i>; una línea puede llevar typed/until propios) · email: el cuerpo se escribe letra a letra (una por fotograma como mucho)"},
            "frame": {"enum": ["web"], "description": "chat: la conversación dentro de una ventana de navegador (puntos + barra de dirección)"},
            "grow": {"type": "boolean", "description": "chat typed: la burbuja crece línea a línea con el texto y la ventana crece hacia abajo; `lines[i].mark` = trozo literal con el rotulador oro al acabar de escribirse (cue m<i>)"},
            "url": {"type": "string", "description": "chat con frame web: dirección REAL que se ve en la barra (sin ella, barra en esqueleto)"},
            "fields": {"type": "array", "maxItems": 4, "items": {"type": "object", "properties": {"k": STR, "v": STR}, "additionalProperties": False},
                       "description": "chat: formulario que se rellena: `k` = rótulo, `v` = valor que se escribe (sin `v`, barra en esqueleto); cada campo en f<k>, check en `done`"},
            "title": STR,
            "lines": {"type": "array", "maxItems": 14, "items": {"anyOf": [STR, {"type": "object"}]},
                      "description": "chat: [{role:user|ai, text, typed?, check?: true (check de oro en c<i>), dots?: true (burbuja «escribiendo…» hasta `until`/u<i>)}], email: [{k, v}…, {text}], code: [\"línea\", …] (≤14 literales; "
                                     "las largas se parten dentro de la tarjeta, sangría a media anchura)"},
            "json": {"type": "object", "description": "registro real (plano) que se enseña resaltado"},
            "focus_key": {"type": "string", "description": "json: clave en foco (equivale a highlights:[{key, cue:\"focus\"}])"},
            "highlights": {"type": "array", "items": {"anyOf": [
                               {"type": "object", "properties": {"key": STR, "cue": STR}, "required": ["key"]},
                               {"type": "object", "properties": {"lines": {"type": "array", "items": {"type": "integer", "minimum": 0}, "minItems": 1, "maxItems": 2},
                                                                 "cue": STR}, "required": ["lines"]}]},
                           "description": "json: [{key, cue}] la lupa salta a cada clave (≥64 px; el resto al 55 %). "
                                          "code: [{lines:[a,b], cue}] índices 0-based inclusivos: marcador oro sobre el rango, punch suave, resto al 55 %"},
            "prewritten": {"type": "boolean", "description": "code: ya escrito (automático si dura <1,5 s); false = se escribe línea a línea desde t0 y acaba ≥0,4 s antes del primer highlight"},
            "fill": {"type": "number", "minimum": 0.5, "maximum": 0.95, "description": "fracción del alto de la banda que llena la ventana (0,88 por defecto); menos = más aire sobre la junta"},
            "plain": {"type": "boolean", "description": "code: texto de README o salida, sin colorear palabras clave"},
            "code_scale": {"type": "number", "minimum": 0.9, "maximum": 1.35, "description": "code (≤8 líneas): escala de la ventana (0,9 por defecto ≈ 700 px; 1,25 ≈ 970 px)"},
            "entry": {"enum": ["rise"], "description": "code con highlights: la ventana entra subiendo 32 px y fundiendo en 8 f (pasa mo.text_entry) en vez de «en el corte»"},
            "code_wide": {"type": "boolean", "description": "code a pantalla completa: ventana de 950 px en la banda alta (acaba por encima de y=1000) en vez de 696 px en la «T»"},
            "code_center": {"type": "boolean", "description": "con code_wide: la ventana se centra en la banda entera (288–1240) en vez de en la alta"},
            "push": {"type": "number", "minimum": 0, "maximum": 0.06, "description": "code con highlights: tras el punch, la ventana sigue acercándose despacio (escala 1 → 1+push) hasta el final"},
            "fill_max": {"type": "number", "minimum": 1.6, "maximum": 2.2, "description": "chat/texto (no code): tope de la escala con la que el contenido llena la banda (1,6 por defecto); con pocas burbujas en la «T», más grande"},
            "bubble_font": {"enum": ["ui", "sans"], "description": "`sans` = las burbujas de chat en Montserrat (--ck-sans) 600 en vez de Inter (Montserrat siempre). Sin la prop, como siempre"},
            "line_from": {"type": "integer", "minimum": 1, "maximum": 999, "description": "code: número de la primera línea en el canal de números (un extracto de un bloque más largo). Sin la prop, desde 1"},
        }, ["kind"]),
        "dur_min": 0.8, "dur_rec": 1.8,
        "sfx": [],
        "cues_doc": "l0, l1… (cada burbuja o campo), w<i> (fin del tecleo de la burbuja i), c<i> (su check), u<i> (fin de «escribiendo…»), f0…f3 (campos del formulario), done (check del formulario), type (código), las de highlights[].cue (json y code); eventos: enter, type, check, field, …",
        "when": "enseñar la cosa real en vez de nombrarla: una conversación, un correo, unas líneas de código o el registro JSON que devuelve un modelo (con foco en el campo que dice quien habla)",
        "when_not": "capturas reales de una web o app (eso es media); texto inventado que quien habla no dice o que no sale de las pruebas",
    },
    "media.capture_plane": {
        "kind": "media", "track": "broll", "file": "media.capture_plane.js", "media": "required",
        "props": _obj({
            "fit": {"enum": ["contain", "cover"], "default": "contain"}, "position": STR, "radius": {"type": "integer"},
            "settle": BOOL, "kb": {"type": "number", "minimum": 0, "maximum": 0.08, "description": "dolly lento (escala final 1+kb)"},
            "kb_dir": {"enum": ["in", "out"]}, "asset": ASSET_ID,
            "media_start": {"type": "number", "minimum": 0, "description": "vídeo (mp4): segundo del clip en el que arranca (lo reproduce HyperFrames)"},
            "width": {"type": "integer", "minimum": 200, "maximum": 1080, "description": "ancho de la hoja en px (≤ el del área): varias hojas a la misma escala"},
            "y": {"type": "number", "minimum": 0, "maximum": 1, "description": "centro vertical de la hoja en fracción del área (apilar hojas)"},
            "aspect": {"type": "number", "minimum": 0.2, "maximum": 20, "description": "ancho/alto real del vídeo (al montar aún no hay metadatos: sin esto, 16:9 con bandas blancas)"},
            "tilt": {"type": "number", "minimum": 0, "maximum": 3, "default": 2, "description": "inclinación hacia atrás en grados (≤3)"},
            "sheen": {"type": "boolean", "default": True, "description": "un brillo que cruza la hoja una vez"},
            "focus": {"type": "object", "properties": {"text_box": {"type": "array", "items": NUM, "minItems": 4, "maxItems": 4,
                      "description": "[x, y, w, h] relativos (0–1) dentro de la captura"},
                      "marker": {"enum": ["gold", "underline"], "description": "underline = barra oro de 6 px bajo la base (mezcla "
                                 "normal): por defecto en vídeo y en capturas oscuras; gold = rotulador multiply (solo capturas claras)"}},
                      "required": ["text_box"], "description": "foco oro sobre una palabra real de la captura (nunca relleno encima del texto en vídeo)"},
        }, []),
        "dur_min": 0.8, "dur_rec": 2.4,
        # sin SFX de registro en focus/sheen (0,5 SFX/s era demasiado denso); la entrada suena por
        # animaciones.yaml solo si entra con movimiento (props.enter ≠ "cut")
        "sfx": [],
        "cues_doc": "focus (se dibuja el marcador), sheen (cruza el brillo)",
        "when": "toda captura real de una web (acme.example…) como hoja 2.5D a ancho útil (950 px): inclinada ≤3°, sombra de una luz, brillo y dolly lento",
        "when_not": "vídeos o grabaciones de pantalla (media.slot); capturas que no son la prueba de lo que se dice",
    },
    "title.lockup_grid": {
        "file": "title.lockup_grid.js", "media": "optional",   # miniaturas por línea (lines[].media)
        "props": _obj({
            "lines": {"type": "array", "minItems": 1, "maxItems": 6, "items": {"type": "object", "properties": {
                "text": STR, "role": {"enum": ["lead", "word", "hero"]}, "cue": STR,
                "entry": {"enum": ["fade", "whip", "drop", "assemble"], "description": "whip = entra rápido con estela; drop = cae y asienta; assemble = letra a letra sobre la rejilla"},
                "settle_on": {"type": "string", "description": "cue (p. ej. «l2») en la que la línea, que entró GRANDE y centrada en el panel, se ASIENTA a su cuerpo y su sitio de la rejilla (9 f que ACABAN en la cue, sin salto). Las líneas normales que entran antes de esa cue van en la pila DEBAJO de la grande, en orden de lectura, y se asientan con ella; con settle_on en varias líneas, todas se asientan en la primera de sus cues"},
                "big_px": {"type": "integer", "minimum": 60, "maximum": 220, "description": "con settle_on: cuerpo de la línea en grande (por defecto, el de las palabras; nunca más ancho que el panel)"},
                # miniatura real por línea
                "media": {**ASSET_ID, "description": "miniatura REAL (imagen PNG/JPG o vídeo; el id también en `assets` de la decisión) a la derecha de su "
                          "fila, en la columna que acaba con el filete (188 px, 16:9, recorte «cover»); entra con máscara de 8 f en la cue de la línea "
                          "(si la línea va en la pila de `settle_on`, al asentarse). El texto sigue centrado en el eje con márgenes simétricos"},
                "media_start": {"type": "number", "minimum": 0, "description": "vídeo: segundo del clip que se ve cuando ENTRA la miniatura (lo aplica el compilador al <video>; HyperFrames lo reproduce)"},
                "media_loop": {"type": "boolean", "description": "vídeo: en bucle si el clip acaba antes que el item (atributo `loop` del <video>, lo emite el compilador)"},
                "media_pos": {"type": "string", "description": "encuadre del recorte (CSS object/background-position, p. ej. «50% 30%»)"}},
                "required": ["text"], "additionalProperties": False}},
            "rules": {"type": "boolean", "default": True, "description": "filetes finos entre líneas (la rejilla visible)"},
            "fill": {"type": "number", "minimum": 0.5, "maximum": 0.96, "default": 0.96,
                     "description": "alto máximo del bloque respecto al área fuera de la «T» (5 líneas en el 50/50: ~0,84)"},
            "lead_px": {"type": "integer", "minimum": 40, "maximum": 120, "description": "cuerpo máximo de las líneas «lead» (56 por defecto; suelo 44)"},
            "parity": {"type": "boolean", "description": "todas las líneas «word» al MISMO cuerpo (el menor que cabe); por defecto cada una a su ancho"},
            "media_px": {"type": "integer", "minimum": 180, "maximum": 200, "default": 188, "description": "ancho de la columna de miniaturas (lines[].media)"},
        }, ["lines"]),
        "dur_min": 1.5, "dur_rec": 3.2,
        # golpe sutil SOLO en la línea héroe (role = hero): `at: hero` = la cue de esa línea (evento `word`)
        # golpe con energía en 1–5 kHz (asoma en el móvil) sobre un cuerpo grave (sala/sub), solo en la línea héroe
        # (−13 LU y sin la capa de suspense: era el golpe más fuerte del vídeo y bajo una invitación suave)
        "sfx": [{"at": "hero", "offset": 0.0, "kind": "pop", "file": "pop_1", "pitch": 0.0, "rel_lu": -13.0,
                 "max_s": 0.5, "prio": 6}],
        "cues_doc": "las de cada línea en `cue` (l0, l1, l2, l3…); la miniatura de una línea (lines[].media) entra en la misma cue; eventos: enter, word, settle, exit",
        "when": "tríada o resumen tipográfico a pantalla completa (lienzo oro): cada palabra entra como lo que significa",
        "when_not": "como subtítulo; más de una vez por vídeo",
    },
    "cta.comment": {
        "file": "cta.comment.js", "media": None,
        "props": _obj({
            "verb": {"type": "string", "default": "Comenta"},
            "keyword": STR, "sub": STR, "placeholder": STR,
        }, ["keyword"]),
        "dur_min": 1.8, "dur_rec": 2.6,
        "sfx": [{"at": "keyword", "offset": 0.0, "kind": "pop"}],
        "when": "CTA del outro de un Short («Comenta PALABRA y te mando…»): rótulo arriba y caja de comentario que se escribe y se envía",
        "when_not": "a mitad de vídeo; si quien habla no dice la palabra clave",
    },
}

for _spec in GRAPHICS.values():
    _spec.setdefault("kind", "graphic")
    _spec.setdefault("track", "graphic")

# Los secundarios (stat, chart, callout…) los declara otro agente en registry_graphics_extra.py. A todos se les añaden
# las props comunes del kit (canvas, exit, keep_start…) que ya entienden sus componentes a través de CK.gx.
try:  # pragma: no cover
    from cutkit.motion import registry_graphics_extra as _rx  # type: ignore
    _EXTRA = getattr(_rx, "GRAPHICS_EXTRA", None) or getattr(_rx, "GRAPHICS", {})
    for _n, _s in (_EXTRA or {}).items():
        if _n in GRAPHICS:
            continue
        _s = dict(_s)
        _p = _s.get("props")
        if isinstance(_p, dict) and isinstance(_p.get("properties"), dict):
            _p = dict(_p); _p["properties"] = dict(_p["properties"])
            for _k, _v in COMMON.items():
                _p["properties"].setdefault(_k, _v)
            if _n == "stat.big_number":
                _p["properties"].setdefault("source", {"type": "string", "description": "fuente del dato (línea ≥32 px)"})
            _s["props"] = _p
        GRAPHICS[_n] = _s
except Exception:  # noqa: BLE001
    pass
