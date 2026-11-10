# Licencias de cutkit (editor de vídeo)

Auditoría de todo lo que contiene `modulos/cutkit/` y de lo que cutkit genera, descarga o usa en el ordenador de cada
usuario. Las rutas son relativas a `modulos/cutkit/`. Revisada el 2026-11-09; vuelve a revisarla si añades fuentes,
bundles, sonidos, modelos o servicios. `tests/modulos/test_modulos_licencias.py` falla si aparece un archivo binario o
de terceros que no esté en esta lista.

Regla: **solo se redistribuye lo propio o lo que tiene una licencia que lo permite, con su aviso al lado**. Los
modelos, las herramientas y los servicios de terceros no viajan con el producto: se instalan, se descargan o se
contratan en el ordenador de cada usuario y con su cuenta.

## 1. Lo que se redistribuye con el módulo

| Archivo o grupo | Qué es | Licencia | Decisión |
|---|---|---|---|
| `cutkit/**/*.py` | Código de cutkit (montaje, audio, QA, CLI `ck`) | MIT (la de Meta Ads OS, `LICENSE` en la raíz) | Se mantiene |
| `cutkit/motion/runtime.js`, `runtime.css`, `cutkit/motion/components/*.js`, `*.css` | Gráficos animados del modo avanzado (HTML que renderiza HyperFrames) | MIT (propio) | Se mantiene |
| `cutkit/motion/three/ck3d.js`, `cutkit/motion/three/scenes/*.js` | Escenas 3D propias sobre three.js | MIT (propio) | Se mantiene |
| `cutkit/recursos/**/*.yaml`, `cutkit/recursos/marca_defecto.json` | Perfiles, tokens de movimiento, reglas de QA, reglas de SFX y marca neutra | MIT (propio; las reglas citan guías públicas como fuente, sin copiar su texto) | Se mantiene |
| `cutkit/recursos/fuentes/Montserrat-ExtraBold.ttf`, `Montserrat-SemiBold.ttf`, `Montserrat[wght].ttf`, `Montserrat-Italic[wght].ttf` | Tipografía por defecto de hook, subtítulos, CTA y gráficos | SIL Open Font License 1.1 (© 2024 The Montserrat.Git Project Authors) | Se mantiene con `OFL-Montserrat.txt` al lado; no se vende suelta |
| `cutkit/recursos/fuentes/Inter[opsz,wght].ttf` | Tipografía de interfaz de los gráficos | SIL OFL 1.1 (© 2020 The Inter Project Authors) | Se mantiene con `OFL-Inter.txt` |
| `cutkit/recursos/fuentes/JetBrainsMono[wght].ttf` | Tipografía monoespaciada (código en los gráficos) | SIL OFL 1.1 (© 2020 The JetBrains Mono Project Authors) | Se mantiene con `OFL-JetBrainsMono.txt` |
| `cutkit/recursos/fuentes/OFL-*.txt` | Textos de la OFL de cada familia | La propia OFL (obligatorio acompañar a las fuentes) | Se mantienen junto a las `.ttf` |
| `cutkit/motion/three/vendor/three.ck.min.js` | Bundle de three.js r181.2 y sus addons (sin CDN en el render) | MIT (© 2010-2025 three.js authors), texto en `LICENSE.three.txt` | Se mantiene con su licencia al lado |
| `cutkit/motion/three/vendor/fontkit.ck.min.js` | Bundle de fontkit 2.0.4 (contornos de glifos para el texto 3D) y sus dependencias | fontkit: MIT (© 2014 Devon Govett), texto en `LICENSE.fontkit.txt`. Dependencias incluidas en el bundle: restructure, brotli, base64-js, clone, dfa, fast-deep-equal, tiny-inflate, unicode-properties, unicode-trie y pako (MIT) y @swc/helpers (Apache 2.0); textos en `LICENSE.dependencias.txt` | Se mantiene con los tres archivos de licencia al lado |
| `cutkit/motion/three/vendor/LICENSE.three.txt`, `LICENSE.fontkit.txt`, `LICENSE.dependencias.txt` | Avisos de licencia de los bundles | Los de cada paquete | Obligatorios: viajan con los bundles |
| `cutkit/motion/three/vendor/entry_three.js`, `entry_fontkit.js`, `build.sh`, `avisos_licencias.cjs` | Entradas y script para reconstruir los bundles y sus avisos | MIT (propio) | Se mantiene |
| `README.md`, `CLAUDE.md`, `LICENCIAS.md` | Documentación | MIT (propio) | Se mantiene |
| `pyproject.toml`, `uv.lock`, `.gitignore` | Configuración del proyecto uv | MIT (propio) | Se mantiene (`uv.lock` fija versiones para instalar igual en Mac, Linux y Windows) |

No hay música, vídeos, fotos, logos de marcas reales, caras ni voces de personas reales dentro del módulo. Los efectos
de sonido no vienen grabados: se sintetizan en cada ordenador (sección 2).

Nota sobre los bundles: los dos `.min.js` actuales se compilaron sin comentarios legales dentro; los avisos completos
están en los tres `LICENSE.*.txt` de su carpeta. `build.sh` ya los recompila con `--legal-comments=eof` y regenera
`LICENSE.dependencias.txt` con el texto literal de cada dependencia. `LICENSE.dependencias.txt` se generó con las
versiones de una caché local de npm; si recompilas, se regenera con las que instale `build.sh`.

## 2. Lo que se genera o se descarga en el ordenador del usuario (no se redistribuye)

Todo va a `datos/` (o a `CUTKIT_DATOS`), que Git ignora.

| Archivo o grupo | Qué es | Licencia | Decisión |
|---|---|---|---|
| `datos/sfx/<tipo>/<id>.wav` (31 efectos), `datos/sfx/LICENCIA.txt`, `datos/sfx/catalogo.yaml` | Biblioteca de SFX sintetizada con NumPy por `ck instalar` (sin muestras de terceros) | CC0 1.0 | Se genera; se puede usar en anuncios sin atribución |
| `datos/modelos/ggml-large-v3-turbo-q5_0.bin` (≈550 MB) | Modelo de whisper.cpp para subtítulos locales y gratis | MIT (Whisper de OpenAI; conversión GGML de whisper.cpp) | Opcional: `ck instalar --whisper` lo descarga de `huggingface.co/ggerganov/whisper.cpp` |
| `datos/biblioteca/` | Cachés: música elegida o generada, B-roll de stock, copias procesadas de SFX | La de cada origen (sección 5) | Se genera al usarlo |
| `datos/mates/` | Recortes del sujeto con Apple Vision (solo Mac) | Propios del usuario (derivan de su vídeo) | Se genera al usarlo |
| Clasificador Haar `haarcascade_frontalface_default.xml` | Detección de caras para encuadrar el 9:16 | Intel License Agreement (tipo BSD); viene dentro del paquete de OpenCV | No se copia: se usa desde la instalación de OpenCV |
| Modelo MMS_FA de torchaudio | Alineación forzada palabra a palabra | **CC-BY-NC 4.0 (uso no comercial)** | **Apagado por defecto.** Solo se usa con `CK_ALINEAR=mms` (`cutkit/tools/align_mms.py`, con torch y torchaudio en un entorno aparte). No lo actives para anuncios de clientes |
| Chromium de Playwright | Navegador del modo avanzado (eventos visuales y capturas) | BSD y licencias de Chromium | Opcional: `uv run --project modulos/cutkit playwright install chromium` |

## 3. Herramientas del sistema (las instala cada usuario)

| Herramienta | Qué hace | Licencia | Decisión |
|---|---|---|---|
| FFmpeg y FFprobe (con libass y libx264) | Todo el montaje, subtítulos y codificación | LGPL 2.1+; las compilaciones con libx264 son GPL | Lo instala el usuario (`brew install ffmpeg`, `sudo apt install ffmpeg`, `winget install Gyan.FFmpeg`). cutkit solo lo invoca como programa externo |
| whisper.cpp (`whisper-cli`) | Transcripción local | MIT | Opcional (`brew install whisper-cpp` o compilarlo) |
| Node.js y npx | Modo avanzado | MIT | Opcional |
| HyperFrames 0.8.114 (`npx hyperframes@0.8.114`) | Render de los gráficos HTML a vídeo en el modo avanzado | Apache 2.0 | Lo descarga npx al usarlo; no viaja con el producto |
| GSAP 3.15 (`cdn.jsdelivr.net/npm/gsap@3.15`) | Animación de los gráficos HTML del modo avanzado | Licencia estándar de GSAP: gratuita también para uso comercial desde 2025, pero no es una licencia de código abierto y excluye herramientas que compitan con el constructor visual de Webflow | Se carga desde la CDN en el navegador del render; no se redistribuye. [HYPOTHESIS] cutkit no compite con Webflow; revisa `gsap.com/standard-license` antes de revender el modo avanzado como herramienta independiente |
| Tesseract OCR | OCR de la QA avanzada fuera de Mac | Apache 2.0 | Opcional |
| uv | Entornos de Python | MIT o Apache 2.0 | Lo instala el usuario |

## 4. Dependencias de Python (las instala uv desde PyPI)

| Paquetes | Uso | Licencia | Decisión |
|---|---|---|---|
| typer, rich, pydantic, PyYAML, pyloudnorm | CLI, consola, modelos, YAML, sonoridad | MIT | Dependencias |
| numpy, scipy, httpx | Cálculo, filtros, HTTP | BSD-3-Clause (numpy con partes 0BSD, MIT, Zlib y CC0) | Dependencias |
| soundfile | Lectura y escritura de audio | BSD-3-Clause; sus ruedas incluyen libsndfile (LGPL 2.1+, enlazada dinámicamente) | Dependencia |
| Pillow | Medida de texto e imágenes | MIT-CMU (HPND) | Dependencia |
| opencv-python-headless (< 5) | Caras y encuadre | Apache 2.0; sus ruedas incluyen FFmpeg (LGPL) y otras bibliotecas con sus avisos | Dependencia |
| playwright, jsonschema | Extra `avanzado` | Apache 2.0, MIT | Opcional |
| openai, google-genai | Extra `ia` (servicios de pago) | Apache 2.0 | Opcional |
| ocrmac, pyobjc-framework-Vision, pyobjc-framework-Quartz | Extra `mac` (Apple Vision) | MIT | Opcional, solo Mac |

## 5. Contenido de terceros y servicios de pago (con tus claves, nunca por defecto)

- **Música.** Por defecto no hay música. Si la quieres, pon tus pistas en `clientes/<cliente>/marca/musica/` con su
  licencia al lado (`<pista>.licencia.txt` o `LICENCIA.txt`): tiene que cubrir **publicidad de pago en Meta**. Nunca
  música de catálogo comercial sin licencia publicitaria. La música generada con Lyria (Google, de pago) solo se activa
  con `CK_MUSICA_IA=1` y queda bajo las condiciones de tu cuenta de Google.
- **B-roll de stock.** Con `PEXELS_API_KEY` o `PIXABAY_API_KEY` (gratuitas) cutkit puede buscar clips. Licencia de
  Pexels (`pexels.com/license`) y de contenido de Pixabay (`pixabay.com/service/license-summary`): uso comercial sin
  atribución obligatoria, pero no puedes dar a entender que una persona que sale en el clip recomienda tu producto ni
  usar marcas o logotipos que aparezcan en él.
- **Capturas de webs** (modo avanzado): las de la web o la app del cliente son material propio. Para las de un
  tercero necesitas permiso del titular: el derecho de cita (art. 32 de la Ley de Propiedad Intelectual) cubre fines
  docentes o de investigación, no la publicidad [STRONG INFERENCE]. cutkit lo deja escrito en la licencia de cada
  captura.
- **Logos de terceros** (por ejemplo, «se integra con…»): cutkit nunca los descarga. Los pones tú en
  `clientes/<cliente>/marca/logos/` y solo si las normas de marca de ese tercero lo permiten. No los uses para sugerir
  que esa empresa te respalda.
- **Transcripción con OpenAI** (`--subtitulos openai` o `CK_ASR=openai`): whisper-1, ≈0,006 $/min con tu
  `OPENAI_API_KEY`. El audio sale de tu ordenador hacia OpenAI.
- **Juez multimodal** (`--judge` en el modo avanzado): Gemini con tu `GEMINI_API_KEY`, de pago. Apagado por defecto.
- **Tus brutos.** Lo que grabas tú (fundador, equipo, creadores) es tuyo o de tu cliente. Si sale una persona que no
  eres tú, necesitas su permiso por escrito para usar su imagen y su voz en publicidad.
- **Etiqueta de IA.** Si una pieza lleva imagen o voz generada con IA, monta con `--etiqueta-ia` y decláralo al
  publicar en Meta.
