# Runbook del motor

Todas las órdenes se lanzan desde la raíz de Meta Ads OS: `uv run --project modulos/motor-ia motor <orden>`. En los
ejemplos se abrevia como `motor <orden>`. Delante de cualquier orden, `MOTOR_MOCK=1` la simula a coste 0.

## 1. Configuración

| Qué | Dónde | Por defecto |
|---|---|---|
| Claves (`GEMINI_API_KEY`, `FAL_KEY`, `OPENAI_API_KEY`…) | Variables de entorno → `.env` de la raíz → `modulos/motor-ia/.env` (compatibilidad) → ficheros de `MOTOR_SECRETS_FILES` | Ninguna: sin claves, solo simulado |
| Presupuesto global del guardián | `MOTOR_PRESUPUESTO_USD` (entorno o `.env` de la raíz) → `motor.presupuesto_usd` en la cabecera de `contexto/preferencias.md` | 5 $ |
| Presupuesto por proyecto | `MOTOR_PRESUPUESTO_PROYECTO_USD` | Igual que el global |
| Datos (`motor.sqlite3`, `assets/`, `work/`, `exports/`, `models/`) | `MOTOR_DATA_DIR` (absoluta o relativa a `modulos/motor-ia/`) | `modulos/motor-ia/data/` |
| Codificador H.264 | `MOTOR_H264_ENCODER` | `libx264` si existe; si no, el de hardware disponible |
| Panel y API (`motor serve`) | Variables de entorno `MOTOR_API_TOKEN` (cookie `motor_token` o `Authorization: Bearer`) y `MOTOR_ALLOWED_HOSTS` (separados por comas) | Escucha en `127.0.0.1`; hosts `127.0.0.1` y `localhost`; sin token |

Formato del presupuesto en `contexto/preferencias.md` (la clave plana antigua `motor_presupuesto_usd: 5` también vale):

```yaml
---
motor:
  presupuesto_usd: 5
---
```

- Los alias antiguos `MOTOR_BUDGET_GLOBAL_USD` y `MOTOR_BUDGET_PER_PROJECT_USD` siguen funcionando.
- El guardián bloquea la llamada **antes** de enviarla si la estimación supera lo que queda. `motor status` enseña el
  presupuesto efectivo y de dónde sale.
- `MOTOR_SECRETS_FILES` admite varias rutas separadas por `:` (Mac/Linux) o `;` (Windows); de ellas solo se importan
  las claves de `MOTOR_SECRETS_ALLOW` (p. ej. `GEMINI_API_KEY`). Los valores nunca se imprimen ni se copian a disco.
- Recomendado: un proyecto de Google AI Studio con facturación **propia** para el motor. Si el saldo prepago se
  comparte con otras apps, otra puede agotarlo a mitad de un anuncio.

## 2. Flujo típico

```bash
motor brand add --name "Nimbo" --primary "#2F5BEA" --accent "#12B76A" --cta "Pruébalo 14 días gratis" \
  --claim "responde a cada lead nuevo en menos de 5 minutos" --dont "no prometer un número de clientes"
motor product add --brand <brand_id> --name "Nimbo" --kind app --capture-url https://app.nimbo.example/panel \
  --benefit "respuesta automática a leads" --benefit "aviso cuando hay cita"
motor actor create --handle @presentadora_01 --appearance "mujer de 32 años, pelo oscuro por los hombros" \
  --wardrobe "jersey azul marino" --voice-hint "warm, clear, Castilian Spanish" \
  --location "despacho en casa luminoso con escritorio de madera"            # de pago (≈0,3 $)
motor project new --brand <id> --product <id> --actor @presentadora_01 --objective "pruebas gratuitas" --duration 25
motor run <project_id>                                                      # de pago
motor variant <project_id> hook_text "¿Cuánto tardas en contestar a un lead?"   # ≈0 $
motor variant <project_id> aspect 4:5                                       # ≈0 $
motor variant <project_id> spoken_cta "Pruébalo hoy, son catorce días gratis."  # de pago
motor variant <project_id> language en-US                                   # de pago
motor regen <project_id> 3 --action strengthen_identity                     # de pago; escena 3 = tercera del vídeo
motor edit <project_id> "regenera únicamente la escena 3" --yes             # de pago: enseña el coste y pide --yes
motor edit <project_id> "versión 4:5 y sin música"                          # 0 $: edición acumulativa
motor edit <project_id> "vuelve a la versión 2"                             # 0 $: historial inmutable
motor edit <project_id> "usa la toma anterior de la escena 3"               # 0 $: las tomas se conservan
motor costs <project_id>
motor gc --dry-run                                                          # qué temporales liberaría
```

Para un SaaS, el producto es siempre la interfaz real: `--capture-url` (Playwright la captura), `--screenshot` o
`--recording`. Para producto físico: `--packshot` y `--footage` con fotos y vídeos reales.

## 3. Del estudio creativo al motor (`plan-import`)

Los pasos creativos los hace el workflow `estudio-creativo` de Meta Ads OS (`.claude/workflows/estudio-creativo.js`) o
`productor-ugc` a partir de un guion aprobado; el motor solo produce. Ejemplo completo:
`examples/plan_ejemplo_nimbo.json`.

```bash
motor plan-import plan.json <brand_id> <product_id> --actor @presentadora_01 --duration 22 --locale es-ES
```

Formato: `{"plans": [{"angle": {…}, "plan": {…}}]}` o un plan suelto.

| Campo del plan | Contenido |
|---|---|
| `title` | Nombre del anuncio |
| `segments[]` | `role` (`hook`, `problem`, `agitate`, `solution`, `demo`, `proof`, `offer`, `cta`), `text` hablado, `on_screen_text`, `emotion`, `gesture` |
| `cta_card` | Texto de la tarjeta final (si falta, la primera CTA de la marca) |
| `continuity` | `location_en`, `lighting_en`, `wardrobe_en`, `hair_en`, `props_en[]`, `time_of_day` (en inglés, físico y concreto) |
| `shots[]` | `shot_type` (`talking_head`, `app_screen`, `product_hero`, `product_hand`, `broll`, `actor_motion`), `segment_indexes[]`, `description_en`, `camera`, `duration` (cortes de 1,5–3 s), `uses_product` |
| `audience[]`, `production_notes`, `hook_product_overlay` | Opcionales |
| `angle` (al lado de `plan`) | `family` (`pain`, `desire`, `mechanism`, `social_proof`, `objection`, `offer`, `novelty`, `comparison`), `insight`, `promise`, `demo_idea`, `hooks[]`, `score`, `why_it_works` |

Reglas que `plan-import` comprueba o corrige solo: el primer tramo es el hook, solo y de ≤9 palabras; ningún tramo
hablado pasa de 17 palabras (se parte); ≤3 planos de corte, nunca encima del hook ni de la CTA (se mueven al tramo
intermedio más cercano); `app_screen` en un producto que no es app pasa a `product_hero`; los planos de actor en
movimiento van sin cara; ninguna frase del guion se pierde; sin testimonios en primera persona (avisa). Devuelve el
**coste estimado** de cada proyecto antes de producir.

## 4. Estilo Flow y POV (scripts)

Para anuncios de producto en uso con varios planos dentro de una misma generación (el «estilo Flow») y para B-roll
POV sin personas. El subcomando va siempre justo después del nombre del script.

```bash
S=modulos/motor-ia/scripts
uv run --project modulos/motor-ia python $S/flow_style.py validar  --receta mi_receta.json   # gratis
uv run --project modulos/motor-ia python $S/flow_style.py plan     --receta mi_receta.json   # gratis: prompts y coste
uv run --project modulos/motor-ia python $S/flow_style.py setup    --receta mi_receta.json   # gratis: crea el proyecto
uv run --project modulos/motor-ia python $S/flow_style.py keyframe --receta mi_receta.json --n 2      # de pago
uv run --project modulos/motor-ia python $S/flow_style.py gen_a    --receta mi_receta.json <fotograma> # de pago
uv run --project modulos/motor-ia python $S/flow_style.py gen_b    --receta mi_receta.json <toma_a>    # de pago
uv run --project modulos/motor-ia python $S/flow_style.py check    --receta mi_receta.json <toma>      # gratis, local
uv run --project modulos/motor-ia python $S/flow_style.py stills   --receta mi_receta.json             # de pago
uv run --project modulos/motor-ia python $S/flow_style.py animate  --receta mi_receta.json <plano> <still>  # de pago
uv run --project modulos/motor-ia python $S/pov_broll.py list --planos mis_planos.json              # gratis
```

- Parte de `examples/flow_receta_nimbo.json` y `examples/pov_planos_ejemplo.json`: cambia `marca_id`, `producto_id`
  (míralos con `motor brand list` y `motor product list`) y `actor`.
- Las referencias de producto son assets del motor (`producto:captura:0`, `producto:packshot:0`,
  `producto:grabacion:0`) o rutas a fotos reales.
- `validar` explica cada problema: hook de más de 9 palabras, segmentos de más de 17, testimonio en primera persona,
  referencias que no existen, planos que no dicen ningún segmento, duraciones fuera de 3–10 s.
- `--simular` (o `MOTOR_MOCK=1`) recorre todo a coste 0 para probar la receta.

## 5. Cómo leer el QA

Veredicto de cada versión: **APROBADO** · **RECHAZADO** (se regenera solo lo rechazado) · **REVISAR ANTES DE PUBLICAR**
(hallazgos que no se arreglan solos: afirmaciones sin respaldo, visión sin confirmar) · **SIN REVISIÓN VISUAL** (el juez
multimodal no pudo correr: saldo, caída o modo simulado). Estado del proyecto: `done`, `needs_review`, `done_unreviewed`,
`done_with_warnings`, `paused_billing`, `paused_budget`, `interrupted`.

Cada versión del anuncio genera un `QAReport`:
- `checks.identity`: similitud SFace por escena (mediana, p10, mínimo; suelo 0,363).
- `checks.asr`: error de palabras entre lo que se oye en el render y el guion.
- `checks.freeze_black`, `checks.loudness` (objetivo −14 LUFS), `checks.duration`.
- `checks.vlm_realism` / `checks.vlm_looks_ai`: puntuaciones globales del juez multimodal.
- Escenas rechazadas, p. ej. `S04 rejected → identity_drift + hands → strengthen_identity: …`: el orquestador
  regenera **solo** esas escenas (máx. 2 rondas y 2 regeneraciones por escena).

Regla de disparo: un fallo determinista grave, o un hallazgo del juez multimodal `major`/`critical` con confianza
≥0,7 apoyado por otra señal. Lo que solo ve el juez queda como aviso (no gasta dinero).

El veredicto del motor no sustituye a mirar el vídeo: revisa fotogramas del hook (0,5 s, 1 s, 2 s), de cada cambio de
plano y de la CTA. Busca producto o interfaz deformados, manos raras, deriva de identidad, texto quemado, frases
repetidas, escenario sin sentido y etiqueta de IA ausente.

## 6. Pruebas

| Prueba | Qué cubre | Coste |
|---|---|---|
| `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q` | Configuración, recetas, `plan-import` y pipeline completo simulado con FFmpeg real (varios minutos) | 0 $ |
| `uv run --project modulos/motor-ia python modulos/motor-ia/tests/bench_replay.py --help` | Montaje, QA y variantes sobre clips reales que ya tengas | ≈0 $ (sin API) |
| `motor demo` | Prueba de referencia real con la app ficticia Nimbo: actor, anuncio de ~24 s y 3 variantes (reanuda si quedó en pausa) | ≈4–6 $ |

## 7. Costes

`motor costs [<proyecto>]` o la pestaña del proyecto en el panel: total, por etapa, por modelo y por escena. Las
llamadas en caché cuestan 0 (se registran como `cached`). Los errores se registran con su coste si el proveedor lo
cobra. El trabajo local (render, ASR, identidad) se valora con una tarifa de CPU de VPS.

## 8. Publicación y cumplimiento

- Etiqueta «Creado con IA» visible por defecto (política de marca `visible`). Cambiarla a `end_card` o
  `metadata_only` es una decisión legal del anunciante (en la UE, art. 50 del Reglamento de IA desde el 2026-08-02).
  Al publicar en Meta se declara además el uso de IA.
- Los vídeos de Google llevan SynthID (marca invisible): no se elimina.
- Firma C2PA opcional antes de publicar (requiere `c2patool` y un certificado):
  `c2patool exports/<id>/<id>.mp4 -m manifest_c2pa.json -o firmado.mp4` (el `manifest.json` del motor trae los datos
  de procedencia).
- Formato presentador por defecto: una persona sintética no cuenta experiencias personales de uso.

## 9. Problemas conocidos

| Síntoma | Causa | Qué hace el motor / qué haces tú |
|---|---|---|
| `402 … prepayment credits are depleted` | Saldo prepago de Gemini agotado | Sin reintentos; el proyecto queda `paused_billing` con todo lo generado. Recarga en Google AI Studio y `motor run <id>` continúa donde se quedó |
| `429` en vídeo | Cuota diaria de peticiones de Omni (ventana móvil de 24 h, no se reinicia a medianoche) | Espera; `motor run <id>` reanuda sin volver a pagar lo hecho |
| Proyecto en `paused_budget` | Se alcanzó el presupuesto del guardián | Decide si subes el presupuesto (§1) o paras; `motor run <id>` reanuda |
| `Multiple authentication credentials` al consultar una interacción | `GET /interactions/{id}` falla con claves de API | El motor usa streaming SSE |
| Veo no responde | Modelos preview retirados de la Gemini API | El router cae a Omni |
| FFmpeg colgado al 0 % de CPU | Entradas superpuestas que terminan antes que el vídeo base, o stdin heredado | Imágenes como fotograma repetido dentro del grafo (`loop` + `trim`), vídeos alargados con `tpad`, `-nostdin` |
| Faltan capas (p. ej. la etiqueta de IA) a mitad del vídeo | Segmentos con rango de color distinto hacen que FFmpeg reconstruya el grafo | Todo se normaliza a BT.709 rango limitado antes de concatenar |
| `allow_adult … not supported` | Texto → vídeo con personas desde la UE | Siempre imagen → vídeo con fotograma clave |
| Subtítulos quemados, tramos saltados o frases repetidas en una extensión de Omni | Comportamiento del modelo | Detectores `burned_text`, continuidad de la cadena y `repeated_spans`; corte en el mínimo de energía |
| El peinado cambia en la extensión | Omni mantiene voz e identidad pero no siempre el pelo | Fija el peinado en el prompt (`hair_en` / `pelo_en`) |
| Producto o etiqueta deformados (rejillas, letras) | Producto generado por IA | Planos de producto desde fotos reales o stills animados |
| Voz distinta entre anuncios | Omni no tiene ID de voz | Formato voz en off (TTS persistente) o `FAL_KEY` + lip-sync |
| Anuncio en `done_unreviewed` | El juez multimodal no corrió | Recarga saldo y repite el QA (`motor run <id>` reutiliza lo generado) |
| Una regeneración falla a mitad | Proveedor caído, moderación o saldo | Se restaura la toma anterior (nunca se pierde un clip aprobado) |
| El ASR rechaza un hook corto bien dicho | Whisper falla más en frases cortas | Segunda escucha guiada por el texto esperado antes de rechazar |
| Tesseract no lee un fichero | Algunos sistemas limitan el acceso a carpetas temporales | El motor trabaja bajo `data/work/` |
| `falta ffmpeg` / `libx264` no disponible | FFmpeg sin instalar o compilado sin libx264 | `motor status` da el comando de instalación; sin libx264 se usa el codificador de hardware disponible o `MOTOR_H264_ENCODER` |
