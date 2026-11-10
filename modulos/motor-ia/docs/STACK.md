# Stack del motor (decisiones de octubre de 2026)

Elecciones de modelos y herramientas tras varias rondas de investigación y pruebas reales con la API de Gemini. Los
modelos, sus nombres y sus precios cambian cada pocas semanas: los precios vigentes para el motor están en
`motor/config/prices.yaml` (fechados) y lo que realmente has gastado, en `motor costs`.

## Principio rector

**Generar solo lo que no se puede componer, reutilizar o verificar.** El píxel caro solo donde aporta realismo humano
(actor hablando, actor actuando); todo lo que es «verdad de marca» (texto, CTA, app, producto, logo) sale de assets
reales y composición determinista.

## Capas y proveedores

| Capa | Elección (con `GEMINI_API_KEY`) | Por qué | Respaldo / cuando haya más claves |
|---|---|---|---|
| Cerebro creativo | `gemini-3.1-pro-preview` (ángulos, guion) + `gemini-3.8-flash` (storyboard, JSON) | Calidad creativa en los pasos que venden; barato en el resto | Claude u OpenAI vía `providers/openai_compat` |
| Identidad del actor | Paquete propio: retrato maestro + hoja multivista con `gemini-3.1-flash-image`, validada con **YuNet + SFace** (MIT / Apache 2.0) | Activos propios, no IDs de proveedor; métrica con licencia comercial (InsightFace no la tiene) | `gemini-3-pro-image` como refuerzo automático cuando la identidad baja |
| Fotogramas clave | `gemini-3.1-flash-image` con hasta 3 refs de identidad + producto + localización; best-of-N por similitud SFace | Previa barata (≈0,07 $) que fija identidad y composición antes de pagar vídeo | Seedream 5 (BytePlus/fal), gpt-image |
| Actor hablando | **A-roll continuo con Gemini Omni 1.1 Flash**: primer tramo desde el fotograma clave + **extensiones encadenadas** (mismo vídeo, misma voz, misma sala) | En las pruebas en castellano: sin errores de palabras, identidad estable y costura de la extensión sin clic ni salto de sala. Muestra pequeña: no es una garantía, por eso cada tramo se verifica | Modo `lipsync` (escrito, sin probar con el proveedor): voz TTS fija del actor + Kling Avatar v2 vía `FAL_KEY` → misma voz entre anuncios |
| Actor sin hablar / B-roll | Omni 1.1 (720p, ≈0,10 $/s) desde fotograma clave; B-roll sin personas con Veo 3.1 Lite (≈0,05 $/s) → Omni | Omni rinde mejor que Veo en imagen → vídeo; las versiones preview de Veo tenían retirada anunciada (2026-10-22): si no responden, el router cae a Omni | H3 Max / Kling 3.0 vía fal |
| Voz persistente (voz en off) | `gemini-3.8-flash-tts` con voz de catálogo castellana o voz diseñada propia | Voces nativas de castellano; céntimos por minuto; ID persistente | ElevenLabs / Cartesia (sin adaptador) |
| Producto / app | **Píxeles reales**: capturas o grabaciones reales (Playwright) en un móvil genérico; packshot real animado | Cero interfaz inventada, cero etiquetas deformadas, coste ≈0 | Imagen de producto compuesta + imagen → vídeo solo si no hay fotos |
| Edición | Timeline tipada no destructiva → FFmpeg (segmentos en caché, concatenación sin recodificar, pasada única de acabado; H.264 con libx264 o el codificador disponible) | Variantes a céntimos; «regenera la escena 3» sin rehacer nada más | HyperFrames para tarjetas animadas (opcional) |
| Subtítulos | ASS palabra a palabra (Montserrat ExtraBold, OFL) dentro de la zona segura 9:16 de Meta (14 % arriba, 35 % abajo, 6 % a los lados) | Legibles sin sonido; tiempos del ASR, texto exacto del guion | — |
| Audio | Mezcla FFmpeg: voz/diálogo + tono de sala + música Lyria con ducking + loudnorm −14 LUFS | Quita el «audio demasiado limpio» | Música propia con licencia comercial |
| ASR / alineado | faster-whisper `small` local (MIT) + alineado al guion | Subtítulos exactos y control de palabras corruptas a coste 0 | `gemini-3.5-transcribe` |
| QA | Determinista (local, 0 $): SFace por escena en el tramo usado con margen frente a impostores («gemelas»), error por caracteres audio ↔ guion por tramo (segunda escucha guiada), **objetos en la mano con CLIP ViT-B/16 ONNX** (segundo móvil), boca en planos mudos (MediaPipe), etiqueta de IA visible por OCR, microcortes, afirmaciones/cifras/temas vetados, congelados, loudness. Multimodal: **Gemini 3.8 Flash** en 3 pasadas sobre un proxy numerado por escena | Veredicto de 3 estados: sin juez multimodal el anuncio queda **SIN REVISIÓN VISUAL**, nunca «aprobado». Descartado tras probarlo: EfficientDet/COCO para el móvil (no lo ve de canto) | Pasada de verificación con `gemini-3.1-pro-preview` |
| Regeneración | Por escena; en el A-roll, desde el tramo fallido (los anteriores se conservan) | Coste proporcional al fallo | — |
| Costes | Libro de costes por llamada con unidades reales del proveedor + guardián de presupuesto (proyecto y global) | Coste real medido por etapa, escena y modelo | — |
| Infra | Python ≥3.11 (3.12 recomendado), SQLite (WAL), almacén de assets por contenido, cola de trabajos en proceso, FastAPI + panel estático | Funciona en un portátil o un VPS pequeño | Postgres + almacenamiento de objetos + cola durable cuando haya volumen |

## Restricciones conocidas

- **Identidad**: SFace separa personas reales pero puntúa alto (≈0,72) a «gemelas» generadas con la misma
  descripción. El motor compara contra impostores conocidos (margen); falta una curva ROC con ≥20 gemelas.
- **Voz entre anuncios**: con solo Gemini, la voz del diálogo nativo de Omni no tiene ID persistente. Dentro de un
  anuncio es constante (toma única extendida); entre anuncios puede variar. Soluciones: formato voz en off (voz TTS
  persistente) o `FAL_KEY` para lip-sync con la voz TTS del actor.
- **Español**: Google solo evalúa formalmente el inglés en Omni; el motor verifica cada tramo con ASR y lo regenera si
  cambia palabras.
- **Cuotas**: el nivel 1 de Gemini limita el gasto por periodo y las peticiones diarias de vídeo. El motor respeta el
  presupuesto y reintenta solo errores seguros (429/503) para no duplicar trabajos facturados.
- **API de interacciones**: con claves de API, `GET /v1beta/interactions/{id}` fallaba («Multiple authentication
  credentials», comprobado en octubre de 2026). El motor usa streaming SSE.
- **Cumplimiento**: etiqueta visible «Creado con IA» por defecto, SynthID de Google se conserva, manifiesto de
  procedencia en cada exportación y formato presentador por defecto (sin testimonios falsos en primera persona).

## Qué se activa al añadir claves

| Clave | Estado real |
|---|---|
| `FAL_KEY` | Adaptadores escritos (Kling Avatar v2, Kling LipSync, Kling 3.0 imagen → vídeo, Seedream 5 edit, upscaler) y modo `lipsync` conectado al pipeline. **Sin probar contra el proveedor**: el primer uso es la prueba |
| `HEYGEN_API_KEY`, `BYTEPLUS_API_KEY`, `ELEVENLABS_API_KEY` | **Solo reservadas** en la configuración: falta escribir sus adaptadores (con el patrón de `motor/providers/fal.py`) |
| `OPENAI_API_KEY` | Adaptador de LLM alternativo escrito; no se usa mientras haya Gemini |
