# modulos/motor-ia — Motor de vídeo con IA

Módulo opcional que convierte un brief o un plan en un anuncio vertical: presentadora sintética persistente, producto
real, edición no destructiva, QA con regeneración selectiva, variantes casi gratis y coste medido por llamada.
Documentación: `README.md` (instalación y estructura), `docs/RUNBOOK.md` (operación, formato de planes, QA,
problemas), `docs/STACK.md` (modelos y porqué), `docs/ARCHITECTURE.md`, `docs/ESTADO.md` (qué está probado y costes
medidos), `LICENCIAS.md`. Guía para el usuario: `docs/guias/video-ia.md` (raíz). Desde el sistema: agente
`productor-ugc`, `/producir-video ia`, `/variantes` y `/motor` (estado, instalar, costes, test, reanudar, limpiar).

## Uso
- Siempre desde la raíz: `uv run --project modulos/motor-ia motor <orden>`. Si no existe `modulos/motor-ia/.venv`,
  el motor no está instalado: propón `/motor instalar`. El entorno se crea en cada ordenador; no lo copies ni lo muevas.
- Antes de producir: `motor status` (proveedores, claves ✔/·, gasto frente al presupuesto, modo simulado).
- Simulado sin coste: `MOTOR_MOCK=1` delante de cualquier orden. Prueba completa:
  `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q`.
- Datos en `modulos/motor-ia/data/` (`MOTOR_DATA_DIR`): base de datos, assets, trabajo, exportaciones y modelos. No
  borres nada a mano; los temporales se liberan con `motor gc` (enseña antes la lista con `--dry-run` y espera un sí).

## Dinero (leer antes de producir)
- Claves en el `.env` de la raíz (`GEMINI_API_KEY` y las opcionales). **Nunca leas, imprimas ni copies `.env`**:
  `motor status` enseña solo ✔/·.
- Presupuesto global del guardián: **5 $** por defecto. Lo fija el usuario con `MOTOR_PRESUPUESTO_USD` en `.env`
  (prioridad) o en la cabecera de `contexto/preferencias.md` (`motor:` → `presupuesto_usd: <n>`). No lo cambies sin
  que el usuario te dé la cifra.
- Órdenes de pago (las frena `motor_guard`): `run`, `regen`, `demo`, `actor create`, `edit --yes`, `variant` con voz
  o idioma (`spoken_cta`, `rewrite_line`, `language`), `scripts/auto_produce.py` y los subcomandos de pago de
  `scripts/flow_style.py` (`keyframe`, `gen_a`, `gen_b`, `stills`, `animate`) y `scripts/pov_broll.py` (`keyframe`,
  `gen`). Gratis: `setup`, `status`, `costs`, `brand`, `product`, `actor list`, `project new`, `plan-import` (da el
  coste estimado), variantes de texto o formato, `flow_style.py validar|plan|setup|check`, `pov_broll.py list`.
- Antes de cada orden de pago, da el coste estimado y espera el sí. Referencias (octubre de 2026, cambian): anuncio
  de 20–30 s ≈4–6,5 $, vídeo ≈0,10 $/s, imagen ≈0,07 $, actor nuevo ≈0,3 $, variante de texto ≈0,0004 $.
- `402` = saldo del proveedor agotado → proyecto `paused_billing`; `429` = cuota diaria de vídeo (ventana móvil de
  24 h). En los dos casos `motor run <id>` reanuda después sin volver a pagar lo hecho.

## Flujo
1. Guion aprobado (de `estratega-creativo`, `/brief-creativo` o el workflow `estudio-creativo`) con veredicto de
   `revisor-politicas` sobre el texto.
2. Marca y producto (`motor brand add`, `motor product add`, gratis) con material real: en SaaS, la interfaz real
   (`--capture-url`, `--screenshot`, `--recording`), nunca una inventada.
3. `motor plan-import <plan.json> <brand_id> <product_id> --actor @<handle> --duration <s> --locale es-ES` → coste
   estimado → sí → `motor run <id>`.
4. QA: veredicto del motor + fotogramas revisados a mano (hook, cada cambio de plano, CTA). Arreglos selectivos con
   `motor regen` o `motor edit … --yes`; nunca regeneres el anuncio entero si basta una escena.
5. Variantes baratas (`hook_text`, `cta`, `captions`, `aspect 4:5`, `music`).
6. Entrega en `clientes/<slug>/creativos/<carpeta-del-anuncio>/` con `LEEME.md` (plantilla
   `.claude/skills/producir-video/plantilla-leeme.md`: archivos, QA, coste real con `motor costs`, afirmaciones con
   su fuente, etiqueta de IA). Los vídeos no se quedan solo en `data/exports/`. Después, `/revisar-anuncio` y
   `/publicar-anuncios` (el MCP de Meta no sube vídeos: se suben en Ads Manager).

## Reglas creativas y legales
- La presentadora es sintética: prohibido el testimonio en primera persona («lo he probado», «llevo meses usándolo»).
- Hook solo y ≤9 palabras; ningún tramo hablado >17 palabras; ≤3 planos de corte de 1,5–3 s, nunca sobre el hook ni
  la CTA ni con una cara frontal callada bajo la voz; último tramo = CTA.
- Ninguna cifra ni afirmación fuera de `approved_claims` de la marca; nada de salud, ingresos ni resultados
  garantizados sin respaldo.
- Producto en uso en su contexto real y a escala real; estilo Flow multiplano con `scripts/flow_style.py` y una
  receta (`examples/flow_receta_nimbo.json`); voz nativa del idioma del mercado; sin texto dentro de la generación (los
  rótulos se componen después).
- Etiqueta «Creado con IA» visible por defecto + declaración de IA al publicar en Meta; SynthID no se elimina.
- Sin caras ni voces de personas reales sin permiso por escrito. Música generada o con licencia comercial, nunca de
  catálogo.

## Trampas conocidas (detalle en `docs/RUNBOOK.md` §9)
- `GET /interactions/{id}` falla con claves de API → el motor usa streaming SSE.
- Las extensiones de Omni pueden quemar subtítulos, saltar tramos, repetir frases o cambiar el peinado → detectores
  `burned_text`, continuidad de cadena y `repeated_spans`; fija el peinado en el prompt.
- FFmpeg: entradas superpuestas más cortas que el vídeo base pueden colgarlo; segmentos con rangos de color distintos
  pierden capas → todo se normaliza a BT.709 antes de concatenar.
- Producto generado por IA se deforma → planos de producto desde fotos reales o stills animados.

## Al cambiar código
- Ejecuta las pruebas simuladas antes y después; mantén los contratos de `motor/models.py`.
- Multiplataforma: rutas con `pathlib`, rutas de filtros con `media.filter_path`, listas de concat con
  `media.write_concat_list`, codificador con `media.h264()`, binarios con `media.FFMPEG`/`FFPROBE`, ficheros de texto
  con `encoding="utf-8"`.
- Nada personal en el módulo (rutas de usuario, marcas o IDs reales): los ejemplos usan Nimbo, una app ficticia.
- Si añades una fuente, un modelo o un asset, regístralo en `LICENCIAS.md`.
