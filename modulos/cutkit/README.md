# cutkit, el editor de vídeo de Meta Ads OS

Convierte una grabación tuya (fundador, equipo, creador o demo de pantalla) en anuncios **9:16 y 4:5** listos para
subir a Meta: quita los silencios, pone el **hook en los 2 primeros segundos**, subtítulos palabra a palabra, la CTA y
el logo de la marca del cliente, todo dentro de las **zonas seguras** de Reels, Stories y Feed, y pasa una QA técnica
antes de entregarte nada. Es local, determinista y gratis: solo FFmpeg, NumPy y Pillow. Las IA de pago son opcionales
y nunca se activan solas.

Es un proyecto uv independiente dentro de Meta Ads OS. Todo se ejecuta desde la raíz del producto con
`uv run --project modulos/cutkit ck <orden>`. Para vídeos generados con IA, usa el motor (`modulos/motor-ia`); para
cortes rápidos sin marca, `python3 -I herramientas/editar_video.py`. La guía completa está en
`docs/guias/video-propio.md`.

## Instalación

Requisitos:

- **uv**.
- **FFmpeg con libass y libx264**:
  - Mac: `brew install ffmpeg`.
  - Linux: `sudo apt install ffmpeg`.
  - Windows: `winget install Gyan.FFmpeg`.

Opcional: **whisper.cpp**, para sacar subtítulos gratis en tu ordenador (`brew install whisper-cpp` o compilarlo).

```bash
uv run --project modulos/cutkit ck instalar              # crea el entorno (la primera vez, con red), comprueba
                                                         # FFmpeg, libass, libx264, Node y whisper.cpp, y genera
                                                         # los 31 efectos de sonido libres (CC0)
uv run --project modulos/cutkit ck instalar --whisper    # además descarga el modelo de whisper.cpp (≈550 MB, MIT)
```

`ck instalar` te dice qué falta y cómo arreglarlo en tu sistema. Si después falta una herramienta, sale con código 2.

## Montar un anuncio

```bash
uv run --project modulos/cutkit ck anuncio grabacion.mp4 --slug demo-crm --cliente acme \
  --hook "¿Tu CRM pierde leads cada semana?" --cta "Reserva tu llamada"
```

Deja en `clientes/acme/creativos/<AAAA-MM-DD>_demo-crm/`:

```
demo-crm_9x16.mp4      1080×1920, H.264 yuv420p, AAC 48 kHz, −14 LUFS
demo-crm_4x5.mp4       1080×1350
demo-crm.srt           subtítulos (para subirlos aparte en Ads Manager si quieres)
qa_anuncio.json        resultado de la QA, con las cajas de cada texto
LEEME.md               bloque «QA técnica (cutkit)», que se actualiza en cada montaje sin borrar tus notas
brutos/                copia de la grabación original
edicion/anuncio/       archivos intermedios (ASS de cada formato, audio procesado)
```

Qué hace, en orden:

1. **Ingesta.** Comprueba que hay vídeo y audio que suena, y guarda el bruto en `brutos/`.
2. **Silencios.** Quita el silencio inicial y las pausas de 0,35 s o más (deja 80 ms de aire). Para no tocarlos:
   `--sin-quitar-silencios`.
3. **Subtítulos.** Por orden:
   - `--subtitulos archivo.srt` o `.json` de palabras;
   - un `.srt` o `.json` con el mismo nombre que el bruto;
   - whisper.cpp local;
   - `--subtitulos openai`: whisper-1, de pago, ≈0,006 $/min con tu `OPENAI_API_KEY`;
   - `--subtitulos no`: sin subtítulos.

   Se muestran en páginas de 1 a 3 palabras, con la palabra que se está diciendo resaltada, en el tercio central.
4. **Audio.** Procesa la voz (paso alto, nivelador, compresor, de-esser) y masteriza a −14 LUFS con techo de −1,5 dBTP.
   La música solo se añade si la pides: `--musica pista.mp3`, o una pista de `clientes/<cliente>/marca/musica/` con
   su licencia al lado.
5. **Maquetación por formato.** Hook (máximo 3 líneas equilibradas, hasta 2,5 s), subtítulos, CTA y logo en los
   últimos 2,5 s, y la etiqueta de IA con `--etiqueta-ia`. Para el B-roll a pantalla completa:
   `--broll 3.2-5.0:pantalla.mp4`, repetible, en segundos del montaje final. El encuadre del 9:16 sigue la cara
   (`--foco auto`); también acepta `centro` o un valor de 0 a 1.
6. **QA.** Revisa:
   - resolución exacta y ratio (tolerancia de Meta del 1 %);
   - códecs y fps;
   - hook dentro de los 2 primeros segundos y sin exceso de líneas;
   - cobertura y ritmo de los subtítulos;
   - que **ninguna caja de texto pise la interfaz de Meta**;
   - sonoridad y picos;
   - que no arranque en negro ni en silencio.

   El veredicto es `pass`, `warn` o `fail`. Con `fail`, el código de salida es 1.

Otras opciones:

- `--formatos 9x16`
- `--logo siempre|cta|no`
- `--mayusculas`
- `--nombre <nombre del anuncio según la nomenclatura>`
- `--fecha AAAA-MM-DD`
- `--salida <carpeta>`
- `--json`

Todas están en `ck anuncio --help`.

### Zonas seguras

Están en `cutkit/recursos/perfiles/anuncio.yaml`. Las comprueba la QA con las cajas reales del texto, medidas con la
misma tipografía y la misma escala que usa libass para pintarlo.

| Formato | Margen arriba | Margen abajo | Laterales | Notas |
|---|---|---|---|---|
| 9:16 (1080×1920) | 269 px (14 %) | 672 px (35 %) | 65 px (6 %) | Desde y = 1152, los botones de Reels ocupan 227 px a la derecha [OFFICIAL META] |
| 4:5 (1080×1350) | 5 % | 5 % | 5 % | [HYPOTHESIS] margen prudente para Feed |

Fuente: `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md`.

## La marca del cliente

cutkit lee `clientes/<cliente>/marca/marca.json`. Las rutas son relativas a esa carpeta y todos los campos son
opcionales: lo que falte sale de una marca neutra. Es el mismo esquema que usan `herramientas/render.py` y
`herramientas/editar_video.py`.

```json
{"nombre": "Acme Automations",
 "colores": {"primario": "#1F6FEB", "secundario": "#0B1F3A", "acento": "#FFB020", "fondo": "#FFFFFF",
             "texto": "#0B1F3A", "texto_sobre_primario": "#FFFFFF"},
 "tipografias": {"titulos": {"familia": "Montserrat", "archivo": "fuentes/Montserrat-ExtraBold.ttf", "peso": 800},
                 "texto": {"familia": "Montserrat", "archivo": "fuentes/Montserrat-Medium.ttf", "peso": 500}},
 "logo": {"principal": "logo.png", "claro": "logo-claro.png"},
 "subtitulos": {"color": "#FFFFFF", "resaltado": "#FFB020", "contorno": "#000000", "mayusculas": false},
 "cta_por_defecto": "Reserva tu llamada",
 "etiqueta_ia": "Contenido generado con IA"}
```

- El hook va en `primario`, con el texto en `texto_sobre_primario`. Si el contraste es menor de 4,5:1, cutkit te avisa.
- La CTA va en `acento`.
- La tipografía tiene que ser **TTF u OTF estática**:
  - una fuente variable se pinta con su instancia por defecto (normalmente la más fina);
  - una WOFF o WOFF2 no sirve para vídeo.

  En los dos casos cutkit avisa. Sin tipografía, usa Montserrat (OFL).
- Para vídeo, el logo debe ser **PNG con fondo transparente**. Un SVG solo, sin PNG, se queda fuera y cutkit te avisa.
- Para ver la marca resuelta y sus avisos: `uv run --project modulos/cutkit ck marca acme`.

## Modo avanzado: montaje por decisiones

Sirve para piezas con gráficos animados, B-roll resuelto automáticamente, efectos de sonido sincronizados y QA visual.
Es más lento y necesita más instalación:

- **Node 20+**, porque el render usa HyperFrames por npx.
- **El extra `avanzado`**: `uv sync --project modulos/cutkit --extra avanzado` y después
  `uv run --project modulos/cutkit playwright install chromium`.

```bash
uv run --project modulos/cutkit ck new demo-crm --cliente acme --raw grabacion.mp4   # ingesta, transcripción y análisis
uv run --project modulos/cutkit ck context demo-crm      # paquete de contexto para el agente que escribe el plan
#   el agente escribe edicion/versions/v001/plan.json: decisiones ancladas a ids de palabra, nunca a segundos
uv run --project modulos/cutkit ck validate demo-crm v001  # esquema, anclas, assets y afirmaciones con fuente
uv run --project modulos/cutkit ck run demo-crm v001       # assets → voz → compilar → render → QA → export
uv run --project modulos/cutkit ck edit demo-crm v001 --op '{"op":"remove","select":{"at":32}}' --reason "sobra el B-roll"
#   cada edición crea una versión hija (v002…); ck versions demo-crm las lista y ck export demo-crm v002 entrega
```

Limitaciones conocidas:

- Los gráficos animados toman de la marca los colores (primario y acento), pero la tipografía es siempre la del
  producto (Montserrat, Inter o JetBrains Mono).
- El recorte del sujeto (texto detrás de la persona) solo funciona en Mac, con el extra `mac`.
- El juez multimodal (`--judge`) es de pago (Gemini) y viene apagado.
- `--budget` limita el gasto en assets de pago (por defecto, 0 $).

## Variables de entorno

Van en el `.env` de la raíz del producto (cutkit lo carga sin imprimir nada) o en el entorno.

| Variable | Para qué | Por defecto |
|---|---|---|
| `OPENAI_API_KEY` | Subtítulos con whisper-1 (`--subtitulos openai`), de pago | No se usa |
| `GEMINI_API_KEY` | Música con Lyria (`CK_MUSICA_IA=1`) y juez (`--judge`), de pago | No se usa |
| `PEXELS_API_KEY`, `PIXABAY_API_KEY` | B-roll de stock en el modo avanzado (gratis con clave) | No se usa |
| `CK_ASR` | `local` (whisper.cpp) u `openai` | `local` |
| `CK_WHISPER_MODELO` | Ruta a otro modelo de whisper.cpp | `datos/modelos/ggml-large-v3-turbo-q5_0.bin` o la caché del usuario |
| `CK_MUSICA_IA` | `1` permite generar música con Lyria si no hay pista | Apagado |
| `CK_ALINEAR` | `mms` activa la alineación MMS_FA (licencia no comercial: no la uses en anuncios) | Apagado |
| `CK_SFX_DIR` | Tu biblioteca de efectos, que se suma a la sintética (comprueba su licencia) | — |
| `CK_OCR` | OCR de la QA avanzada: `vision`, `tesseract` o `no` | Automático |
| `CK_CODIFICADOR` | Codificador H.264 de los intermedios: `auto` (VideoToolbox en Mac si existe) o `libx264`. El máster siempre sale con libx264 | `auto` |
| `CK_HF_WORKERS` | Procesos de render de HyperFrames | 2 |
| `CUTKIT_DATOS` | Carpeta de cachés y modelos | `modulos/cutkit/datos/` |
| `CUTKIT_RUNS` | Carpeta de trabajo fuera de `clientes/` (pruebas) | — |
| `META_ADS_OS_RAIZ` | Raíz del producto | Tres carpetas por encima del paquete |

## Pruebas

Desde la raíz del producto, sin red ni gasto:

```bash
uv run pytest tests/modulos/cutkit -q
```

Las pruebas que necesitan FFmpeg o el entorno de cutkit se saltan y dicen por qué si no los encuentran. La prueba de
punta a punta monta un anuncio con un vídeo sintético de FFmpeg y tarda unos 50 s.

## Licencias

Todo lo que contiene y usa el módulo está auditado en `LICENCIAS.md`. Lo esencial:

- Las tipografías son OFL.
- Los efectos de sonido son sintéticos (CC0).
- No se incluye música ni vídeo de terceros.
- Los servicios de pago solo se usan si los activas tú, con tus claves.
