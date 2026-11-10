# Arquitectura

## Flujo

```
Brief ─▶ creative.make_angles ─▶ creative.write_script ─▶ creative.make_storyboard ─▶ router.plan_routes
                                                                                         │ (coste estimado por plano)
   ┌─────────────────────────────────────────────────────────────────────────────────────┘
   ▼
orchestrator.produce
   ├─ scenes.make_keyframe (talking)  ── imagen con refs del actor, best-of-N por SFace
   ├─ scenes.generate_aroll           ── tramo 1 (Omni hablado) → extensiones encadenadas; ASR+identidad por tramo
   └─ scenes.generate_cutaway ×N (en paralelo)
         ├─ compose.app_phone  → capturas/grabaciones reales en un móvil (product.app_screen_clip)
         ├─ compose.packshot   → foto/vídeo real del producto
         └─ i2v                → fotograma clave → Omni (actor sin hablar) / Veo Lite (B-roll sin personas)
   ▼
edit.build_timeline ─▶ render.render ─▶ qa (deterministic + vlm) ─▶ judge.decide
   ▲                                                                  │
   └──────────── orchestrator.regenerate (solo escenas rechazadas) ◀──┘   (máx. 2 rondas, 2 regens/escena)
   ▼
orchestrator.export (MP4, miniatura, manifest.json) ─▶ variants.make_variant / commands.apply
```

## Principios de diseño

1. **Contratos tipados** (`models.py`): cada etapa lee y escribe objetos pydantic persistidos en SQLite.
   Un proyecto se puede reanudar en cualquier punto; los planos `ready` no se vuelven a generar.
2. **Proveedores intercambiables** (`providers/base.py` define los protocolos; `registry.py` elige según claves).
   Añadir un modelo = un adaptador con `generate(...) -> Asset` que mida su coste con `meter(...)`.
3. **Todo lo generado es un asset inmutable** (dirección por contenido, sha256). Los clips no se sobrescriben: una
   regeneración crea otro asset y sube la `revision` del plano; la timeline tiene `version`.
4. **Caché en dos niveles**: llamadas a proveedores (clave = modelo + prompt + refs + semilla) y segmentos de render
   (clave = asset + recorte + zoom + tamaño). Una variante solo paga lo que cambia.
5. **El coste se mide, no se estima**: cada llamada registra unidades reales devueltas por el proveedor (tokens de
   vídeo/audio/imagen, segundos), latencia y estado. El guardián de presupuesto corta antes de llamar.
6. **Verificar en vez de confiar**: identidad (SFace) y diálogo (ASR) se comprueban en cada tramo antes de aceptarlo;
   el QA final combina señales deterministas con el juez multimodal, y solo lo determinista o lo confirmado por dos
   señales gasta dinero en regenerar.

## Edición no destructiva

| Orden | Qué se regenera | Qué se reutiliza |
|---|---|---|
| «regenera la escena 3» | ese plano; si es A-roll en modo nativo, desde ese tramo hasta el final (la toma es una cadena de extensiones); en modo `lipsync`, solo ese tramo | todo lo demás (caché) |
| «vuelve a la versión 2» / «usa la toma anterior de la escena 3» | nada | timelines y tomas guardadas (historial inmutable) |
| «cambia el texto del hook» | nada (solo re-render) | todos los clips |
| «cambia el hook» (hablado) | A-roll completo (el hook es el primer tramo de la toma) | todos los cortes |
| «que diga al final …» | último tramo del A-roll (extensión del penúltimo) | resto |
| «hazlo en alemán» | guion transcreado + A-roll | B-roll, app, producto, tarjeta |
| «versión 4:5», «sin música», «subtítulos limpios» | nada | todo |

Los cambios de texto/idioma/formato crean **variantes** (proyectos hijos con `parent_id`); el máster nunca se toca. Las
variantes son acumulativas (una variante de una 4:5 sigue en 4:5) y las órdenes de pago muestran el coste y piden confirmación.

## Montaje (reglas aplicadas automáticamente)

- El A-roll se monta por **tramos con voz**: las pausas >0,25 s se eliminan en audio y vídeo a la vez (microfundidos de
  10 ms) y el tono de sala de la propia toma suena de fondo de principio a fin (sin caídas a silencio).
- Nunca se corta dentro del hook; los planos de corte no muestran una cara frontal callada bajo la voz; ningún plano
  dura menos de 0,5 s; todo cuadrado a fotograma (sin desfase audio/vídeo); 24 fps si la fuente es Omni.
- Todos los segmentos se normalizan a BT.709 rango limitado antes de concatenar (si no, FFmpeg reconstruye el grafo y
  pierde capas como la etiqueta de IA).

## Paso a SaaS

- `store.DB` → Postgres (mismas tablas `docs/assets/costs/jobs/cache`), `AssetStore` → R2/S3 (mismo contrato
  `ingest/abspath`), cola en proceso → cola durable (Arq/Celery) con los mismos `Job`.
- Multi-tenant: `brand_id` ya cuelga de todo; añadir `org_id` a `BrandKit`/`Actor` y filtrar en `DB.list`.
- Webhooks de proveedores (fal, BytePlus) en lugar de sondeo cuando el volumen lo justifique.
- Los actores son paquetes propios (retrato, hoja, centroide de identidad, voces, banco): portables entre modelos.
