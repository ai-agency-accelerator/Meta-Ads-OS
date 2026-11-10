# Licencias del motor de vídeo con IA

Auditoría de todo lo que contiene `modulos/motor-ia/` y de lo que el motor descarga o usa al instalarse. Las rutas son
relativas a `modulos/motor-ia/`. Revisada el 2026-11-09; vuelve a revisarla si añades fuentes, modelos o assets.

Regla: **solo se redistribuye lo propio o lo que tiene una licencia que lo permite**; los modelos y las herramientas
de terceros no viajan con el producto: se descargan o se instalan en el ordenador de cada usuario.

## 1. Lo que se redistribuye con el módulo

| Archivo o grupo | Qué es | Licencia | Se redistribuye | Decisión |
|---|---|---|---|---|
| `motor/**/*.py`, `scripts/*.py`, `tests/*.py` | Código del motor, scripts y pruebas | MIT (la de Meta Ads OS, `LICENSE` en la raíz) | Sí | Se mantiene |
| `motor/assets/Montserrat-Medium.ttf` | Tipografía de rótulos y subtítulos | SIL Open Font License 1.1 (© 2024 The Montserrat.Git Project Authors) | Sí | Se mantiene con su licencia al lado; no se vende suelta |
| `motor/assets/Montserrat-SemiBold.ttf` | Tipografía de rótulos y subtítulos | SIL OFL 1.1 | Sí | Igual que la anterior |
| `motor/assets/Montserrat-Bold.ttf` | Tipografía de rótulos y subtítulos | SIL OFL 1.1 | Sí | Igual que la anterior |
| `motor/assets/Montserrat-ExtraBold.ttf` | Tipografía de los subtítulos palabra a palabra | SIL OFL 1.1 | Sí | Igual que la anterior |
| `motor/assets/OFL-Montserrat.txt` | Texto de la licencia OFL de Montserrat | La propia OFL (obligatorio acompañar a las fuentes) | Sí | Se mantiene junto a las `.ttf` |
| `motor/ui/index.html` | Panel web interno (`motor serve`) | MIT (propio) | Sí | Se mantiene |
| `motor/config/prices.yaml` | Tabla de precios de los proveedores (datos públicos, fechados) | MIT (propio; los precios son hechos, no obra protegida) | Sí | Se mantiene; actualízala cuando cambien |
| `examples/nimbo_app/index.html` | App ficticia «Nimbo» para la prueba de referencia (capturas reales con Playwright) | MIT (propio) | Sí | Se mantiene |
| `examples/flow_receta_nimbo.json` | Receta de ejemplo del estilo Flow | MIT (propio) | Sí | Se mantiene |
| `examples/pov_planos_ejemplo.json` | Planos POV de ejemplo | MIT (propio) | Sí | Se mantiene |
| `examples/plan_ejemplo_nimbo.json` | Plan de ejemplo para `motor plan-import` | MIT (propio) | Sí | Se mantiene |
| `README.md`, `CLAUDE.md`, `LICENCIAS.md`, `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`, `docs/STACK.md`, `docs/ESTADO.md` | Documentación | MIT (propio) | Sí | Se mantiene |
| `pyproject.toml`, `uv.lock`, `.python-version`, `.gitignore` | Configuración del proyecto uv | MIT (propio) | Sí | Se mantiene (`uv.lock` fija versiones para instalar igual en Mac, Linux y Windows) |

No hay música, vídeos, imágenes de stock, caras ni voces de personas reales dentro del módulo. Las pruebas generan sus
medios en simulado (colores planos, tonos sinusoidales).

## 2. Lo que se descarga en la instalación (no se redistribuye)

`motor setup` descarga estos modelos a `data/models/` (fuera de Git) desde su origen oficial:

| Archivo o grupo | Qué es | Licencia | Se redistribuye | Decisión |
|---|---|---|---|---|
| `data/models/face/face_detection_yunet_2026may.onnx`, `face_detection_yunet_2023mar.onnx` | YuNet, detector de caras (OpenCV Zoo) | MIT | No | Descarga en `motor setup` |
| `data/models/face/face_recognition_sface_2021dec.onnx` | SFace, identidad facial del actor (OpenCV Zoo) | Apache 2.0 | No | Descarga en `motor setup`. Se eligió frente a InsightFace porque este último no permite uso comercial |
| `data/models/face/face_landmarker.task` | MediaPipe Face Landmarker (boca abierta en planos mudos) | Apache 2.0 según las fichas de modelo de MediaPipe (BlazeFace, Face Mesh V2, Blendshape V2); la página de la solución no lo repite | No | Descarga en `motor setup`. Comprueba la ficha del modelo si un cliente lo pide por escrito |
| `data/models/tessdata/spa.traineddata`, `eng.traineddata` | Idiomas de Tesseract (tessdata_fast) | Apache 2.0 | No | Descarga en `motor setup` |
| `data/models/clip/vision_model_quantized.onnx`, `text_model_quantized.onnx`, `tokenizer.json` | CLIP ViT-B/16 en ONNX (Xenova): detecta un segundo móvil u objeto inventado en la mano | El repositorio de Xenova no declara licencia; es una conversión de `openai/clip-vit-base-patch16` (código y pesos de OpenAI CLIP con licencia MIT). La ficha de OpenAI considera «fuera de alcance» los usos desplegados | No | **Opcional**: `motor setup --sin-clip` no lo descarga y el detector queda como «sin datos» (nunca como aprobado). Riesgo bajo pero no nulo: decide tú si lo usas en producción comercial |
| Modelo `small` de faster-whisper (caché de Hugging Face, ≈480 MB) | Transcripción local para subtítulos y control de palabras | MIT (Whisper de OpenAI; conversión CTranslate2 de Systran) | No | Lo descarga faster-whisper la primera vez que transcribe (extra `local`) |
| Chromium de Playwright (solo si no tienes Chrome ni Edge) | Navegador para capturar la app real | BSD y licencias de Chromium | No | `uv run --project modulos/motor-ia playwright install chromium` |

## 3. Herramientas del sistema (las instala cada usuario)

| Archivo o grupo | Qué es | Licencia | Se redistribuye | Decisión |
|---|---|---|---|---|
| FFmpeg y FFprobe | Render, cortes, audio | LGPL 2.1+; las compilaciones con libx264 son GPL | No | Lo instala el usuario (`brew`, `apt`, `winget install Gyan.FFmpeg`). El motor solo lo invoca como programa externo |
| Tesseract OCR | Lee la etiqueta de IA y las pantallas | Apache 2.0 | No | Opcional; lo instala el usuario |
| uv | Gestor de entornos de Python | MIT o Apache 2.0 | No | Lo instala el usuario |

## 4. Dependencias de Python (las instala uv desde PyPI)

| Archivo o grupo | Qué es | Licencia | Se redistribuye | Decisión |
|---|---|---|---|---|
| pydantic, fastapi, typer, rich, PyYAML, pytest | Modelos de datos, API, CLI, consola, YAML, pruebas | MIT | No | Dependencias |
| httpx, uvicorn, Jinja2 | HTTP, servidor, plantillas | BSD-3-Clause | No | Dependencias |
| numpy | Cálculo numérico | BSD-3-Clause (con partes 0BSD, MIT, Zlib y CC0) | No | Dependencia |
| Pillow (PIL) | Imágenes | MIT-CMU (HPND) | No | Dependencia |
| opencv-python-headless, python-multipart, google-genai, fal-client | Visión, subidas, SDK de Gemini, SDK de fal | Apache 2.0 | No | Dependencias |
| faster-whisper, onnxruntime | Extra `local`: transcripción y ONNX | MIT | No | Extra opcional |
| mediapipe, playwright, tokenizers | Extra `local`: puntos faciales, navegador, tokenizador de CLIP | Apache 2.0 | No | Extra opcional |

## 5. Lo que generan los proveedores

Los vídeos, imágenes y voces que crea el motor salen de los modelos del proveedor (Gemini y, si añades su clave, fal)
con **tu** cuenta y bajo **sus** condiciones de uso: tú respondes de lo que publicas.

- Los vídeos e imágenes de Google llevan **SynthID** (marca de agua invisible). No se elimina ni se intenta eliminar.
- Cada anuncio lleva la etiqueta visible «Creado con IA» por defecto (`ai_label_policy: visible` en la marca). Esa
  etiqueta en la pieza es la que cuenta: en la UE, el art. 50 del Reglamento de IA (obligaciones de transparencia) se
  aplica desde el 2026-08-02, y el «AI info» de Meta no basta ni suele saltar con vídeo reencodado.
- Las personas del motor son sintéticas. No uses la cara ni la voz de una persona real sin su permiso por escrito.
- La música se genera (Lyria) o la aportas tú con licencia comercial. Nunca música de catálogo con derechos: Meta no
  la admite en anuncios de Reels.
