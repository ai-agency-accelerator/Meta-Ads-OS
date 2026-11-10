# Motor de vídeo con IA

Módulo opcional de Meta Ads OS que convierte un brief o un plan creativo en un anuncio vertical (9:16, y 4:5 como
variante) con **presentadora sintética persistente**, **producto real** (capturas, grabaciones o fotos tuyas),
**edición no destructiva**, **QA automático con regeneración selectiva** y **variantes casi gratis**. Cada llamada a un
proveedor se mide y un guardián de presupuesto la frena antes de enviarla si no cabe.

```
brief → ángulos → guion → storyboard → router → fotogramas clave (identidad verificada)
      → A-roll continuo (presentadora hablando, toma única extendida) → planos de corte (app real / packshot / IA)
      → montaje (timeline tipada) → render FFmpeg → QA (determinista + Gemini) → regenerar SOLO lo rechazado
      → exportar (MP4 + miniatura + manifiesto con costes y procedencia) → variantes
```

Guía de uso dentro del sistema (cuándo usarlo, flujo completo, políticas): `docs/guias/video-ia.md` en la raíz.

## Instalación

Lo normal es pedírselo a Claude con `/motor instalar`. A mano, desde la raíz de Meta Ads OS:

| Paso | Orden | Notas |
|---|---|---|
| 1. Requisitos | `uv --version` · `ffmpeg -version` | FFmpeg: Mac `brew install ffmpeg` · Windows `winget install Gyan.FFmpeg` · Linux `sudo apt install ffmpeg`. Python ≥3.11 lo pone uv si no lo tienes |
| 2. Entorno | `uv sync --project modulos/motor-ia --extra local` | Crea `modulos/motor-ia/.venv` en tu ordenador (no se copia entre carpetas ni se versiona). `--extra local` añade el QA local completo (transcripción, boca, objeto en la mano, captura de apps) |
| 3. Modelos locales | `uv run --project modulos/motor-ia motor setup` | Gratis: ≈50 MB (caras y OCR) + ≈150 MB de CLIP (`--sin-clip` para omitirlo; ver `LICENCIAS.md`) |
| 4. Claves | `GEMINI_API_KEY` en el `.env` de la raíz | La pegas tú con tu editor, nunca en el chat. Las demás variables, en `plantillas/env.ejemplo` |
| 5. Comprobación | `uv run --project modulos/motor-ia motor status` | Proveedores activos, claves (✔/·), gasto y presupuesto |
| 6. Prueba sin gasto | `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q` | Recorre todo el pipeline con medios simulados (varios minutos, 0 $) |

Opcionales: Tesseract (OCR de pantallas y de la etiqueta de IA: `brew install tesseract`, `sudo apt install
tesseract-ocr` o `winget install UB-Mannheim.TesseractOCR`) y el Chromium de Playwright si no tienes Chrome ni Edge
(`uv run --project modulos/motor-ia playwright install chromium`).

## Dinero

- **Presupuesto del guardián: 5 $ por defecto.** Lo cambias en la cabecera de `contexto/preferencias.md`
  (`motor:` → `presupuesto_usd: 20`) o con `MOTOR_PRESUPUESTO_USD=20` en el `.env` de la raíz, que tiene prioridad.
  Por proyecto, el mismo salvo que fijes `MOTOR_PRESUPUESTO_PROYECTO_USD`.
- **Órdenes de pago** (el hook `motor_guard` pide confirmación): `run`, `regen`, `demo`, `actor create`,
  `edit --yes`, `variant` con voz o idioma (`spoken_cta`, `rewrite_line`, `language`) y los scripts de `scripts/`
  que generan imagen o vídeo.
- **Gratis**: `setup`, `status`, `costs`, `brand`, `product`, `actor list`, `project new`, `plan-import`, `serve`,
  `variant` de texto o formato (`hook_text`, `cta`, `captions`, `aspect`, `music`), y todo con `MOTOR_MOCK=1`.
- Coste medido en octubre de 2026 (cambia con los precios de Google): anuncio de 20–30 s ≈4–6,5 $ · vídeo ≈0,10 $/s ·
  imagen ≈0,07 $ · variante de texto o formato ≈0,0004 $ · CTA hablada ≈0,6–0,8 $ · idioma ≈3–4 $.
  Detalle: `docs/ESTADO.md`.

## Uso rápido

```bash
alias motor='uv run --project modulos/motor-ia motor'      # opcional, para abreviar
motor brand add --name "Nimbo" --primary "#2F5BEA" --accent "#12B76A" --cta "Pruébalo 14 días gratis"
motor product add --brand <brand_id> --name "Nimbo" --kind app --capture-url https://app.nimbo.example/panel
motor plan-import modulos/motor-ia/examples/plan_ejemplo_nimbo.json <brand_id> <product_id> --actor @presentadora_01
motor run <project_id>                                       # de pago: confirma el coste estimado
motor variant <project_id> aspect 4:5                        # ≈0 $
motor costs <project_id>
motor serve                                                  # panel interno en http://127.0.0.1:8765
```

Flujo completo, formato de los planes, estilo Flow, QA y problemas conocidos: `docs/RUNBOOK.md`.

## Estructura

| Módulo | Qué hace |
|---|---|
| `motor/models.py` | Contratos de datos: marca, producto, actor (paquete persistente), brief, guion, planos, timeline, QA, costes |
| `motor/config.py` | Raíz del producto, claves del `.env` de la raíz, presupuesto y carpeta de datos |
| `motor/store.py` | SQLite (documentos, costes, trabajos, caché) + almacén de assets por contenido |
| `motor/costs.py` | Tabla de precios, libro de costes por llamada, guardián de presupuesto, caché de pasos |
| `motor/media.py` | FFmpeg multiplataforma: localización de binarios, codificador H.264, escapado de rutas en filtros |
| `motor/providers/` | Adaptadores intercambiables: `gemini` (texto, imagen, Omni, Veo, TTS, Lyria, juez), `fal`, `openai_compat`, `local_asr`, `mock`; `registry` elige según las claves |
| `motor/pipeline/creative.py` | Ángulos, guion (formato presentadora, reglas duras), storyboard y continuidad |
| `motor/pipeline/prompts.py` | Compilador de presets UGC → prompts por modelo |
| `motor/pipeline/router.py` | Router de modelos por tipo de plano con coste estimado y respaldos |
| `motor/pipeline/actors.py` | Actor persistente: retrato maestro, hoja multivista validada, voz, identidad |
| `motor/pipeline/identity.py` | Identidad facial con YuNet + SFace (licencias comerciales) |
| `motor/pipeline/scenes.py` | Fotogramas clave best-of-N, A-roll encadenado, cortes con respaldos |
| `motor/pipeline/product.py` | App real en un móvil, packshot real animado, captura con Playwright, OCR de etiqueta |
| `motor/pipeline/edit.py` | Montaje UGC: cortes sobre la voz, hook, subtítulos, CTA, etiqueta de IA, música |
| `motor/editing/` | Render FFmpeg con caché por segmento, subtítulos ASS, gráficos, mezcla de audio |
| `motor/qa/` | QA determinista (identidad con impostores, objeto en la mano con CLIP, boca, etiqueta de IA por OCR, afirmaciones, ritmo), juez Gemini en 3 pasadas y decisión por escena |
| `motor/orchestrator.py` | Ejecución de extremo a extremo, reanudable, con bucle de QA y regeneración selectiva |
| `motor/variants.py` | Variantes acumulativas: hook, CTA, subtítulos, formato, música (≈0 $) · CTA hablada, frase, idioma (solo el A-roll) |
| `motor/commands.py` | Órdenes en lenguaje natural con coste estimado y confirmación; historial de versiones y tomas |
| `motor/plans.py` | Planes del estudio creativo de agentes → proyectos (`motor plan-import`) |
| `motor/api/server.py` + `motor/ui/` | API interna y panel web |
| `motor/cli.py` | CLI `motor …` |
| `scripts/` | Estilo Flow (`flow_style.py`), B-roll POV (`pov_broll.py`), producción automática al recargar saldo (`auto_produce.py`) |
| `examples/` | App ficticia Nimbo, receta Flow, planos POV y plan de ejemplo |

Decisiones y su porqué: `docs/STACK.md` · Arquitectura: `docs/ARCHITECTURE.md` · Estado y costes medidos:
`docs/ESTADO.md` · Licencias: `LICENCIAS.md`.
