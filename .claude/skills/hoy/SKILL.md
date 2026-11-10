---
name: hoy
description: "Qué toca hoy en todos tus clientes, sin coste y sin llamar a Meta: semáforo del brief diario, evaluaciones vencidas del change log, siguiente punto de la fase, informe semanal pendiente y cola de producción, y acaba con 1–3 acciones ordenadas. Úsala al empezar el día o cuando no sepas por dónde seguir."
argument-hint: "[cliente]"
---

# /hoy

Agenda del día a partir de los archivos locales. **Solo lectura y sin coste**: no llama al MCP de Meta, ni a GHL, ni a
Stripe (eso lo hace `/brief-diario`). No escribe nada. Marco: `meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md`
(diario = salud, no rendimiento) y la regla de paciencia de `13-sistema-operativo/01-principios-de-razonamiento.md` §8.

## Pasos

1. **Instalación.** Si `contexto/instalacion.json` no existe o tiene fases requeridas sin `hecho`/`omitido`, pon una
   línea arriba: «Tu instalación está a medias (falta X): `/empezar` la retoma». Sigue igualmente.
2. **Estado.** Ejecuta `python3 -I herramientas/estado.py resumen --json` (o `--cliente <slug>` si te lo pasan).
   - Sale con 2 → configuración rota: recomienda `/doctor` y para.
   - Sin clientes → «Aún no hay clientes: `/cliente-nuevo <nombre>` o `/empezar`». Fin.
3. **Por cliente**, lee la cabecera de `clientes/<slug>/ficha.md` (`nombre`, `estado`). Los `activo` van completos;
   los `prospecto`, en una línea al final. Los de `pausa` no salen: `estado.py` los salta (con `--todos` entran).
   - **Brief de hoy** (`brief_hoy`): si es `true`, lee `clientes/<slug>/informes/diario/<AAAA-MM-DD>.md` y saca su
     semáforo y, si no está en verde, su primera acción. Si es `false`:
     - y en `contexto/preferencias.md` el brief está programado (`brief.programado_con` no vacío) → «el brief
       programado no se ha generado hoy: revisa la tarea con `/brief-diario programar`»;
     - si no está programado → «sin brief: `/brief-diario <slug>` (solo lectura)».
     - Si existe el resumen global `informes/diario/<AAAA-MM-DD>.md`, úsalo como contexto.
   - **Evaluaciones vencidas** (`evaluaciones_vencidas`): fecha, objeto y cambio de cada una, la más antigua primero.
     Evaluar = comparar la métrica de éxito del change log desde la fecha del cambio, con la ventana de atribución
     madurada, y rellenar `Resultado`. Lo hace `/informe-semanal <slug>` si toca esta semana; si no, `analista-meta`
     en solo lectura.
   - **Informe semanal** (`informe_semanal_pendiente`) → `/informe-semanal <slug>`.
   - **Cola de producción** (`cola_produccion`): piezas en `creativos/` sin terminar o sin publicar →
     `/producir-video`, `/producir-estatico` o `/publicar-anuncios`.
   - **Derechos que caducan**: con Grep, busca `^- \*\*Derechos hasta:\*\* \d{4}-\d{2}-\d{2}` en
     `clientes/<slug>/creativos/*/LEEME.md` (las líneas dentro del comentario de la plantilla llevan «AAAA-MM-DD» y no
     casan). Si la pieza tiene `- **Estado:** publicado` y la fecha cae en los próximos 30 días o ya pasó → «renueva
     el permiso con `/casos-y-creadores <slug>` o pausa el anuncio con `/ejecutar-cambio <slug>`».
   - **Siguiente punto de la fase**: el primer id de `pendientes`, traducido con la tabla de abajo.
4. **Salida.**
   - Tabla: `Cliente | Fase | Brief | Vencidas | Semanal | Cola | Siguiente punto`.
   - Debajo, **«Hoy, por este orden:»** con 1–3 acciones en total (no por cliente), cada una con su comando.
   - Fecha absoluta (AAAA-MM-DD) en el título.

## Prioridad de las acciones

1. **Algo roto** (brief en rojo: tracking caído, gasto fuera de límites, rechazos o cuenta restringida, web caída) →
   `/diagnostico <slug> "<síntoma>"` o `/rescate-cuenta <slug>`. Son las excepciones a la regla de paciencia.
2. **Evaluaciones vencidas**, de la más antigua a la más reciente, y **derechos de un caso o un socio ya vencidos** en
   una pieza publicada (publicar sin derechos es un riesgo legal y de políticas).
3. **Informe semanal pendiente**, en la ventana de edición fija de la semana (`04-operativa…` §5).
4. **Siguiente punto de fase**: primero clientes activos con gasto, después los que están en F0–F1.
5. **Cola de producción.**

Nunca propongas tocar campañas por el CPA de ayer ni pausar por 1–3 días de datos (`04-operativa…` §1, «Qué NO hacer a
diario»). Si no hay nada urgente, dilo: «Nada roto. Hoy toca: …».

## Del punto pendiente a la skill

| Id | Skill |
|---|---|
| `F0.ficha`, `F0.topes` | `/cliente-nuevo <slug>` (completa la ficha) · topes y reglas del lado de Meta: `/configurar-meta` |
| `F0.economia` | `/economia` |
| `F0.oferta` | `/oferta <slug>` |
| `F0.funnel` | `/disenar-funnel <slug>` (y `/iman-de-leads <slug>` si la oferta de entrada es un diagnóstico o una calculadora) |
| `F1.portfolio`, `F1.cuenta`, `F1.activos`, `F1.dominio`, `F1.reglas-mcp` | `/configurar-meta <slug>` |
| `F1.dataset`, `F1.dedup`, `F1.crm` | `/implementar-capi <slug>` |
| `F1.landing` | `/landing <url> <slug>` si la página ya existe; `/construir-landing <slug>` si no; `/formulario-instantaneo <slug>` si el lead se capta en Meta; `/webinar <slug>` si es un evento |
| `F2.competencia` | `/competencia` |
| `F2.voz` | `/voz-cliente` |
| `F2.angulos`, `F3.briefs` | `/brief-creativo <slug>` (o `/siguiente-anuncio <slug>` si ya hay anuncios con datos) |
| `F3.piezas` | `/producir-video` o `/producir-estatico` (casos reales: `/casos-y-creadores`; orgánicos que ya funcionaron: `/organico-a-anuncios`) |
| `F4.plan`, `F4.creada`, `F4.activa` | `/lanzar-campana <slug>` |
| `F5.cadencia` | `/brief-diario programar` y `/informe-semanal <slug>` |
| `F5.registro` | `/siguiente-anuncio <slug>` (actualiza el registro creativo) |
| `F5.evaluaciones` | evaluar como en el paso 3 |
| `F5.reglas` | `/reglas-automaticas <slug>` (y `revisar` al acabar el modo sombra) |
| `F6.condiciones` | `/escalar <slug>` |

Un id que no esté en la tabla: muéstralo con su texto de `estado.md` y sugiere `/menu`.
