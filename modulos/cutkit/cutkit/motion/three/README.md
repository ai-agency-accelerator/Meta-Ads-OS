# cutkit/motion/three — capa 3D/WebGL opcional

Escenas Three.js renderizadas **en vivo dentro de HyperFrames**, en el mismo fotograma que el resto de la
composición, con postproducción de estudio: motion blur por acumulación, DOF, bloom, grano, viñeta y aberración.

> **Es una capa «más a más».** Se incluye por si acaso y para probar. No sustituye a ningún componente
> 2D y el director no la elige por defecto. Se activa en un plan **cambiando el `component` de una decisión**: las
> props y las cues son las mismas que las de su equivalente 2D. Si WebGL o el montaje fallan, la escena delega en
> su `fallback` 2D.

```jsonc
// plan.json → decisión d012: solo cambia el componente
"params": { "component": "scene.logo_reveal3d", "assets": ["logo_nimbo"], "cues": {"name": "main_w0036"},
            "props": {"asset": "logo_nimbo", "name": "Nimbo", "by": "Acme Automations", "sweep": true} }
```

## Viabilidad medida (HF 0.8.114 · Apple M4)

| Qué | Dato |
|---|---|
| Backend WebGL en el render de HF | `ANGLE (Apple, ANGLE Metal Renderer: Apple M4)`, GPU real. El CLI hace un probe «auto» y elige hardware; con `--no-browser-gpu` o `--docker` usa SwiftShader |
| Cómo recorre HF la timeline | `__hf.seek(t)` → `timeline.totalTime(t, suppressEvents)`. **Después** el adaptador `three` del runtime despacha `window` `hf-seek` `{time, waitUntil}` (y fija `window.__hfThreeTime`). Captura con `Page.captureScreenshot` |
| Sincronía DOM ↔ WebGL | 90/90 fotogramas: la barra GSAP (DOM) y la barra WebGL coinciden al píxel |
| Determinismo | 2 renders HF a PNG: 90/90 y 63/63 fotogramas **idénticos bit a bit**. `-w 1` y `-w auto` (2 workers): 63/63 PNG idénticos. Los MP4 de `-w 1` y `-w auto` difieren a 45–57 dB, también en 2D: es la codificación de HF (en streaming con 1 worker frente a troceada), no el contenido |
| Coste de GPU por fotograma (1080×1920, MSAA ×4, PBR + sombras + bloom) | ~10 ms con N=1 · ~30 ms con N=8 · ~55 ms con N=16 subfotogramas |
| Coste en HF (ventana real de 63 f, 43 de ellos en 3D) | 1 worker: captura 6,3 s frente a 4,4 s en 2D (≈ +44 ms por fotograma 3D) · `-w auto`: 8–13 s frente a 6 s |
| `preserveDrawingBuffer` | `true` (coste despreciable). Además, cualquier `<canvas>` desactiva la deduplicación de fotogramas estáticos de HF |

**Decisión: render en vivo en HF**, sin pre-renderizar a clip con alfa. Es determinista, sale en el mismo fotograma
que el DOM y cuesta segundos por escena.

## Arquitectura

```
plan (component: scene.*) → compile → render_spec → html.py:_three_block()
   └─ si algún item usa three/scenes/<componente>.js:
        hf/ck3d/three.ck.min.js     three r181.2 + addons (vendor, IIFE: window.THREE, window.THREE_ADDONS)
        hf/ck3d/fontkit.ck.min.js   fontkit 2.0.4 (contornos de glifos, variaciones wght, kerning GPOS)
        hf/ck3d/assets.js           window.__CK3D_ASSETS = {fonts:{"Montserrat|normal": base64}, svg:{"media/x.svg": "<svg…>"}}
        hf/ck3d/ck3d.js             el motor (CK3D)
        hf/ck3d/scene.*.js          solo las escenas usadas
      (sin escenas 3D el HTML no cambia: no se copia nada)
```

- **Montaje síncrono.** Las fuentes y los SVG van embebidos en `assets.js`, sin `fetch`. Así funciona igual por
  http (HF) y por `file://` (`cutkit.motion.preview`), y el lienzo nunca espera a una carga.
- **Un componente CK por escena.** `CK3D.scene(name, def)` llama a `CK.register(name, {mount})`. `mount` crea el
  `<canvas>` (a pantalla completa o en `ctx.slot`) dentro del root del item, que es el `div.clip` cuya visibilidad
  controla HF, junto con su `WebGLRenderer` y los render targets. `animate(tl, t0, t1, cues)` llama a `def.setup(…)`,
  precompila los shaders y renderiza t=0 para detectar fallos pronto.
- **Bucle sin callbacks.** Un único listener de `hf-seek` llama a `CK3D.renderAll(t)` y renderiza cada instancia
  activa (`t ∈ [t0 − ½f, t1 + ½f)`). La vista previa sin HF (`window.__ckSeek` de boxes.js) se envuelve al montar
  para hacer lo mismo. No hay `runtime.js` modificado ni ningún rAF.
- **Timeline privada.** Cada escena anima sus objetos JS (cámara, materiales, luces, post) en `k.tl`, una
  `gsap.timeline({paused:true})` que **no** está en `__timelines`. El motor la busca a cualquier subinstante sin
  tocar el DOM, y eso es lo que permite el motion blur real.
- **Fotograma** (`renderInstance`):
  1. Para N subinstantes del obturador (por defecto 8, a 180°): `k.tl.totalTime(s)` → `def.update(s, cues, k)` →
     render HDR (HalfFloat, MSAA ×4) → suma con peso 1/N. El subinstante central se pinta el último, para que su
     profundidad y su estado alimenten el post.
  2. DOF de reunión de 56 muestras en espiral áurea, con CoC desde la profundidad (opcional).
  3. `UnrealBloomPass` sobre HDR (umbral en luz lineal).
  4. Grado: aberración radial, exposición, tonemap **Khronos PBR Neutral** (respeta el color de marca), saturación
     y contraste, viñeta, sRGB, y grano triangular con semilla = nº de fotograma (también hace de dither contra el
     banding).
- **Fallback.** Si falla el contexto WebGL, `setup` o un render, se quita el canvas, se marca
  `data-ck3d-fallback` en el root y se monta y anima el componente 2D de `def.fallback` con las mismas props. El
  error queda en `CK3D.errors`.

## API

```js
CK3D.scene('scene.mi_escena', {
  fallback: 'logo.reveal',                 // componente 2D equivalente (recomendado)
  options: {                               // se fusiona con DEFAULTS y con props.render
    fov: 24, msaa: 4, shadows: true, fit: 'full' /* | 'slot' */, background: '#0B0A0E',
    motionBlur: { samples: 8, shutter: 0.5 },          // samples: 1 = sin motion blur
    dof: { enabled: true, focus: 12, aperture: 0, maxBlur: 16 },
    bloom: { strength: 0.4, radius: 0.5, threshold: 1.5 },
    grade: { exposure: 1, vignette: 0.32, grain: 0.03, ca: 0.0011, contrast: 1.03, saturation: 1.02, lift: 0.012 },
  },
  setup(scene, camera, renderer, ctx, props, k) {
    // construir la escena y animar k.tl (segundos LOCALES del item; nunca dos tweens sobre la misma propiedad)
    k.framing(12, [0, 0, 0], 24);            // pose final de la cámara → k.px(x, y) y k.ppu() mapean px ↔ mundo
    const p = k.px(540, 555);                // px del lienzo (1080×1920) → mundo en el plano z=0
    k.tl.fromTo(k.post, { exposure: 0.3 }, { exposure: 1, duration: 0.24, ease: 'power2.out', immediateRender: false }, 0);
  },
  update(tLocal, cues, k) { /* estado procedimental en tLocal, subinstantes incluidos: cámara en arco, partículas, foco… */ },
  animateMain(tl, t0, t1, cues, k) { /* opcional: tweens DOM en la timeline principal */ },
});
```

**`k`**: `THREE`, `A` (addons), `tl` (timeline privada), `dur`, `fps`, `W`, `H`, `cues` (en segundos locales),
`props`, `ctx` (el de CK: slot, safe, tokens, media…), `post` (estado animable: `exposure, vignette, grain, ca,
contrast, saturation, lift, bloomStrength, bloomRadius, bloomThreshold, dof, focus, aperture, maxBlur`), `rng(seed)`
(mulberry32), `frameAt(t)`, `framing()`, `px()`, `ppu()` y `kit`.

**`k.kit`** (también en `CK3D.util`):

| Función | Qué hace |
|---|---|
| `svgShapes(svgText, {height, simplify, curveSegments})` | SVG verificado → `THREE.Shape[]`, centrado y con Y hacia arriba. `simplify` = tolerancia RDP en unidades del viewBox: endereza los logos trazados desde bitmap |
| `textShapes(text, {family, style, weight, size, tracking})` | Contornos de texto con las fuentes locales (fontkit: `wght` variable y kerning). Devuelve `{glyphs:[{char, shapes, x, adv}], width, capHeight, ascent, descent}`. La familia tiene que estar en `fonts3d` del registro |
| `extrude(shapes, {depth, bevelThickness, bevelSize, bevelSegments, curveSegments, crease})` | `ExtrudeGeometry` con bisel, normales con pliegue en los laterales y normales **planas** en las tapas (grupo 0 = tapas, 1 = laterales) |
| `makeSweep({dir, width, intensity, color})` | Barrido especular por shader: banda diagonal en espacio de mundo que se suma a la luz saliente. `.apply(material)` (Standard/Physical) y se anima `uniforms.uSweepPos.value` |
| `studioEnv({panels, ambient, blur})` | Entorno PMREM de estudio con softboxes emisivos, para reflejos de producto |
| `bokehParticles({count, seed, box, size, color, intensity, drift})` | Polvo con bokeh: el CoC de cada partícula sale de su distancia al foco. `.update(t, camera, focus, aperture, H)` |
| `imagePlane(img, {width, radius, shadow, emissive})` | Plano para capturas reales: esquinas redondeadas y sombra suave. `img` = `<img>` ya decodificado (p. ej. `ctx.media[i]`) |
| `radialTexture(stops)` · `canvasTexture(w, h, draw)` | Texturas procedimentales deterministas |

## Reglas de determinismo (además de las del runtime)

- Todo el estado visual es **función pura de t**: tweens de `k.tl` (absolutos, con `immediateRender:false`) y
  `update(t)`. Nada de `clock.getDelta()`, `performance.now()` para el estado, `Math.random()` (usa `k.rng(seed)`),
  `requestAnimationFrame` ni `setAnimationLoop`.
- Nada que dependa del fotograma anterior: sin TAA, sin afterimage, sin feedback. El motion blur se reconstruye
  desde t.
- Nada de cargas en el seek: todo llega por `assets.js` o por `ctx.media` (ya decodificados).
- Tamaño y `pixelRatio` fijos (1). El canvas mide lo que mide su slot.

## Crear una escena nueva

1. `cutkit/motion/three/scenes/<componente>.js` con `CK3D.scene('<componente>', {...})`. El nombre del fichero es
   el nombre del componente: `html.py` lo detecta solo.
2. Entrada en `cutkit/motion/registry_three.py` (`GRAPHICS_3D`): mismo esquema que `registry_graphics`, más
   `engine: "three"`, `fallback`, `fonts3d`, `cost` y un `when` que diga que es **opcional**.
3. Pruébala sobre un tramo real sin tocar el plan:
   ```bash
   uv run python -m cutkit.motion.three.lab <proyecto> <version> --item it_d012 --component scene.logo_reveal3d \
       --from 9.3 --to 11.4 --out clientes/<cliente>/creativos/<fecha>_<slug>/edicion/lab3d --render --frames 0.4,0.9,1.25
   # vista previa aislada (file:// + SwiftShader: lenta pero vale)
   uv run python -m cutkit.motion.preview scene.logo_reveal3d --props '{"asset":"logo_nimbo","name":"Nimbo"}' \
       --media clientes/<cliente>/creativos/<fecha>_<slug>/edicion/media/logo_nimbo.svg --layout layout.broll_full --dur 1.5 --cues '{"name":0.3}' \
       --at 0.2,0.6,1.3 --out /tmp/prev
   ```
4. Mira los fotogramas de verdad. Comprueba el determinismo con dos renders `--format png-sequence` y compara los
   píxeles.

## Escena incluida: `scene.logo_reveal3d`

Sustituye a `logo.reveal` (props `asset, name, by, sweep, size, color, material, dust, exit, render`; cue `name`):
logo SVG extruido con bisel (esmalte con clearcoat), autosombra suave, dolly-in con arco y alabeo leve, rack focus
en los primeros ~0,4 s, barrido especular sobre logo y nombre, polvo con bokeh, halo de color de marca, nombre en
Montserrat 900 extruido que sube a través de una máscara (plano de recorte) y autoría en Montserrat 600.
Composición final: logo en y≈555 (470 px), línea base del nombre en y=1000, autoría en y≈1070. La banda de
subtítulos (y≈1180) queda libre. `material: metal | glass` son experimentales: sobre la tinta salen apagados.

## Escena incluida: `scene.pipeline3d` (vertical, styleframe 07)

Alternativa 3D de `flow.pipeline`, con las MISMAS props y cues (`cards`, `outputs`, `labels`, `steps`, `layout`;
`messy/label_top/label_top2/transform/label_bottom/output`). Fallback a `flow.pipeline`.

**Composición.** Columna en x=540 y banda 288–1240, de arriba abajo:
- «información desordenada»;
- 3 fichas de papel apiladas de 820–900 px (el ancho mínimo que deja más fichas en una línea; texto a 34 px);
- 36 px;
- baldosa con el logo extruido, y «Nimbo» debajo (centro en y=768);
- 36 px;
- 3 barras de tinta de 680×88 con mono a 36 px;
- «salida útil».

**Desorden.** Las fichas caen con gravedad y un rebote de ≤ 8 px, y quedan revueltas en 3D: ±8–12° en los tres ejes
y tres profundidades. Una proyección de sus 8 esquinas garantiza que no invaden la etiqueta ni el logo. Mientras
dura el desorden, la cámara **orbita alrededor del eje vertical x=0** (−6° → +5°) con un dolly: la columna central no
se mueve en pantalla, y las fichas y sus sombras, que están a otras profundidades, se desplazan. Eso es paralaje real.

**Cruce** (`transform`). Cada ficha se endereza, una a una. Una copia se adelanta (z +1,2), baja por delante de la
pila y se hunde por detrás de la baldosa encogiendo. Por debajo sale la barra i, que llega a su hueco pasando por
detrás de las barras ya posadas. Así la ficha i (que se queda arriba, enderezada) y la barra i se leen en el mismo
orden. El DOF enfoca la copia que cruza, la baldosa da un pulso en cada paso y un barrido especular cruza la
baldosa y las barras.

**Reposo.** Composición del styleframe con sombras de contacto entre fichas y push lento (1,02).

Lecciones de luz (r181, luces físicas): el difuso es `albedo·I·cosθ/π`, así que el papel blanco necesita I≈4 a
~50°. Una luz casi en el eje de la cámara vela de gris todas las caras planas por su reflejo especular: la luz de
modelado tiene que ir arriba y a un lado. Para fondos de color de marca exacto, `grade.tonemap: 'none'` y
`MeshBasicMaterial`.

Otras opciones del motor: `shadowType: 'vsm'`, `grade.tonemap: 'none'` y `kit.roundedPlane(w, h, r)` (cara con
texto o imagen con UV 0..1, sin la deformación de las UV de `RoundedBoxGeometry`).

## Escena incluida: `scene.capture3d` (capturas y vídeos reales como pantallas)

Sustituye a `media.capture_plane` (imagen) o a `media.slot` (vídeo) cambiando solo el `component`: mismas props
(`fit`, `kb`, `kb_dir`, `sheen`, `focus {text_box, marker}`, `media_start`…) y cues (`focus`, `sheen`). Su fallback
es el componente 2D que toque según el media.

- **Encaje.** En split, el lienzo llega hasta la junta (y 0–840) y la pantalla va en el panel (0–768). En
  `broll_full`, en la banda 288–1240. El contenido mide ≥ 900 px de ancho (932 + bisel de 14 px).
- **Lienzo TRANSPARENTE** (`options.alpha`). Se ve el panel real del layout, con su grano, y la sombra blanda (VSM
  sobre `ShadowMaterial`) cae sobre él.
- **La pantalla.** La imagen o el vídeo es EMISIVO: colores exactos y texto legible, con un cristal que refleja el
  estudio. Lleva bisel grafito en paneles claros (figura/fondo de dispositivo) o aluminio en paneles oscuros.
- **Entrada.** La cámara es un rig que rota alrededor del centro de la pantalla, así que ese centro no se mueve en
  pantalla. Arranca con 8–14° en Y (alterna lado por item) y 5° en X, con un dolly de ×1,22, y en 0,55 s queda casi
  frontal (≤ 1,5°). Lleva DOF solo durante la entrada y motion blur real. Después, deriva mínima y `kb` como dolly lento.
- **Marcador.** `focus.text_box` pinta un marcador oro (multiply) en la cue `focus` y empuja la cámara hacia la
  palabra: el pivote pasa a la palabra, que se queda quieta mientras todo se acerca. Hay un barrido especular.
- **VÍDEO.** `html.py:_vframes_pass` extrae los fotogramas con ffmpeg (JPEG, desde `media_start`; caché por hash en
  `clientes/<cliente>/creativos/<fecha>_<slug>/edicion/media/vframes/`) para los componentes con `video_frames: True`. La escena carga por índice el
  fotograma de cada seek con `prepare()`: si no está listo, lo pinta cuando lo esté y HF espera esa promesa antes de
  capturar (`hf-seek` → `waitUntil`, que HF espera después de inyectar sus vídeos y antes del screenshot). No se
  precarga todo: solo una caché de 8 fotogramas.

### Ampliaciones del motor que usa
- `options.alpha`: lienzo transparente; acumulación, DOF y grado trabajan en premultiplicado.
- `options.rect(ctx, props)`: rectángulo propio del lienzo.
- `def.prepare(tLocal, k) → Promise|null`: recursos por instante con `waitUntil`. La vista previa espera la
  promesa que devuelve `__ckSeek`.
- `def.fallback`: puede ser una función `(props, ctx) → nombre`.

## Límites conocidos

- El texto pintado en el canvas **no lo ve `__ckBoxes`** (QA de cajas de texto). Ortografía y zonas seguras de
  ese texto hay que revisarlas a ojo en los fotogramas.
- Hay un contexto WebGL por instancia (máximo 6 por composición). Cada worker de HF compila sus shaders: ~0,3–1 s
  por worker.
- La vista previa de cutkit lanza Chromium sin flags de GPU (SwiftShader): funciona, pero tarda ~5–8 s por
  instante. El render de HF usa Metal.
- Con `--docker` o `--no-browser-gpu`, HF usa SwiftShader: sigue siendo determinista, pero mucho más lento.

## Vendor

`vendor/three.ck.min.js` (three **0.181.2**, MIT) y `vendor/fontkit.ck.min.js` (fontkit **2.0.4**, MIT) se
compilan con `bash cutkit/motion/three/vendor/build.sh` a partir de `entry_three.js` y `entry_fontkit.js`. Sin
CDN en render. No se ha añadido ninguna dependencia a `pyproject.toml`.
