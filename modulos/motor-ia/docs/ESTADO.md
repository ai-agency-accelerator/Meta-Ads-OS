# Estado y validación del motor

Qué está probado con proveedores reales, qué solo en simulado y qué falta. Las cifras son medidas del libro de costes
del motor en octubre de 2026 con precios de esa fecha: tómalas como orden de magnitud y comprueba los tuyos con
`motor costs`.

## 1. Qué hay y cómo está probado

| Pieza | Dónde | Estado |
|---|---|---|
| Brief, ángulos, guion, storyboard | `motor/pipeline/creative.py` | Probado en real (Gemini 3.1 Pro y 3.8 Flash) |
| Planes del estudio creativo de agentes | `motor/plans.py`, `motor plan-import` | Probado en real: dos anuncios cortos producidos y entregados desde planes de agentes |
| Actor persistente e identidad | `motor/pipeline/actors.py`, `motor/pipeline/identity.py` | Probado en real: retrato + 4 vistas por ≈0,33 $, coherencia SFace ≈0,75, calibrado contra «gemelas» |
| Producto y app reales | `motor/pipeline/product.py`, `motor/editing/graphics.py` | Probado: captura de la app con Playwright, pantalla elegida por OCR, packshot real |
| Escenas y router de modelos | `motor/pipeline/scenes.py`, `motor/pipeline/router.py` | A-roll Omni probado en real (toma con extensiones, castellano, sin errores de palabras en la muestra) |
| Voz y lip-sync | `motor/providers/gemini.py`, `motor/providers/fal.py` | Voz nativa de Omni y TTS probados; lip-sync con fal escrito **sin probar** contra el proveedor |
| Montaje, subtítulos, audio | `motor/pipeline/edit.py`, `motor/editing/` | Probado con píxeles reales |
| QA y regeneración selectiva | `motor/qa/`, `motor/orchestrator.py` | Determinista probado en real; bucle rechazo → regeneración probado en simulado; juez multimodal Gemini sin una ejecución real documentada con éxito (si no corre, el veredicto es «SIN REVISIÓN VISUAL», nunca «aprobado») |
| Variantes y órdenes en lenguaje natural | `motor/variants.py`, `motor/commands.py` | Probado (variantes de texto o formato a ≈0,0004 $) |
| Estilo Flow y POV | `scripts/flow_style.py`, `scripts/pov_broll.py` | Recetas genéricas validadas y recorrido completo probado en simulado (`tests/test_flow_style.py`) |
| Almacenamiento, trabajos, costes, API, panel | `motor/store.py`, `motor/costs.py`, `motor/api/server.py`, `motor/ui/` | Probado |

## 2. Coste medido (octubre de 2026)

| Pieza | Coste | Nota |
|---|---|---|
| Anuncio corto (objetivo 20–30 s) desde un plan de agentes, con QA y arreglos | 5,6–6,3 $ | Dos anuncios reales; la mayor parte es vídeo |
| Vídeo Omni 1.1 Flash 720p | ≈0,10 $/s | La extensión de una toma cobra también el vídeo previo como entrada |
| Imagen (fotograma clave, plano de producto) | ≈0,07 $ | `gemini-3.1-flash-image` 1K |
| Actor persistente nuevo | ≈0,3 $ | Retrato maestro + hoja de vistas |
| Variante de texto, formato, subtítulos o música | ≈0,0004 $ | Solo re-render local |
| CTA hablada nueva | ≈0,6–0,8 $ | Regenera el último tramo del A-roll |
| Idioma nuevo | ≈3–4 $ | Guion transcreado + A-roll completo |

## 3. Pruebas del módulo (sin red ni gasto)

| Prueba | Qué cubre | Duración |
|---|---|---|
| `tests/test_config.py` | Raíz del producto, claves del `.env` de la raíz, presupuesto (entorno, preferencias, 5 $ por defecto) | <1 s |
| `tests/test_flow_style.py` | Validación de recetas Flow/POV y recorrido completo en simulado | ≈5 s |
| `tests/test_plans.py` | `plan-import`: reglas del plan, cortes fuera del hook, ninguna frase perdida | ≈2 s |
| `tests/test_e2e_mock.py` | Pipeline completo con FFmpeg real y proveedores simulados, defecto inyectado → rechazo → regeneración, órdenes en lenguaje natural, seguridad de la API | 3–12 min según el ordenador |
| `tests/bench_replay.py` | Montaje, QA y variantes sobre clips reales que ya tengas (no llama a la API) | Según los clips |

Todas: `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q` desde la raíz.

## 4. Limitaciones conocidas

- **Voz entre anuncios**: con solo Gemini, la voz nativa de Omni no tiene identificador persistente. Dentro de un
  anuncio es constante (una toma extendida); entre anuncios puede variar. Soluciones: formato voz en off (voz TTS
  persistente) o `FAL_KEY` + lip-sync (sin probar).
- **Identidad**: SFace separa personas reales, pero puntúa alto a «gemelas» generadas con la misma descripción. El
  motor compara contra impostores conocidos (margen); falta una curva ROC con ≥20 gemelas.
- **Español**: Google solo evalúa formalmente el inglés en Omni. El motor verifica cada tramo con ASR y lo regenera si
  cambia palabras.
- **Cuotas**: Omni tiene un tope diario de peticiones en el nivel 1 de Gemini (ventana móvil de 24 h, no se reinicia a
  medianoche). El motor reintenta solo errores seguros (429/503) para no duplicar trabajos facturados.
- **Windows**: el código evita rutas fijas, codificadores exclusivos de Mac y comandos de un solo sistema, y las
  rutas de los filtros de FFmpeg se escapan para `C:\…`; las pruebas automáticas se ejecutan en Mac.

## 5. Pendiente (por prioridad)

1. Voz idéntica entre anuncios en modo nativo: conversión de voz local + verificación de hablante.
2. Probar contra el proveedor los adaptadores de fal (Kling Avatar, Kling LipSync, Seedream, upscaler).
3. Banco de hooks (tomas independientes) y borradores a 480p para iterar más barato.
4. Curva ROC de identidad y calibración de umbrales con veredictos humanos en el panel.
5. Producto físico en mano con packshot real pegado por esquinas; flujos de app grabados con toques.
6. Adaptadores de HeyGen, BytePlus y ElevenLabs (las claves están reservadas en la configuración, sin adaptador).
