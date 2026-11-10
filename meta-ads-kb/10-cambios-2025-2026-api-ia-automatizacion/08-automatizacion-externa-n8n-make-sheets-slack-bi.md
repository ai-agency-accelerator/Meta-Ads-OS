# Automatización externa: Marketing API + n8n/Make/código + Sheets/Slack/BI + CRM→CAPI (arquitecturas y riesgos)

> Última verificación: 2026-10-15 · Autor: A10 (agente) · Ámbito: cómo montar reporting automático, alertas, QA de
> anuncios, sincronización CRM→Conversions API y agentes (MCP) fuera de Ads Manager, con los cambios de API 2025-2026.
> Nada de esto se ha ejecutado contra cuentas reales.

## TL;DR

- **Arquitectura recomendada por tamaño**: (1) pequeño → conector SaaS (Porter, Dataslayer, Windsor, Supermetrics…) a
  Sheets/Looker Studio + alertas nativas; (2) mediano → n8n/Make programado + Sheets/BigQuery + Slack; (3) grande/agencia →
  ELT a warehouse (BigQuery/Snowflake) + dbt + BI + servicio propio de alertas y QA. **[EMPIRICAL]**
- **Regla de oro del reporting de Meta**: re-descargar siempre una **ventana móvil** (p. ej., últimos 7–28 días) porque las
  conversiones se atribuyen con retraso (7d click) y Meta recalcula; hacer **upsert idempotente** por fecha+ID. **[STRONG INFERENCE]**
- **Marcar discontinuidades** en los dashboards: 10-jun-2025 (atribución unificada en API), 12-ene-2026 (sin 7d/28d view),
  3-mar-2026 (link clicks/engage-through), 22-jun-2026 (DMA→Comscore), 6-ago-2026 (breakdowns opt-in). **[OFFICIAL META]**
- **CRM→CAPI es la automatización de mayor ROI** para lead gen: guardar el **Meta Lead ID**, subir eventos de etapa al
  menos **a diario**, con volumen suficiente (el mínimo de **200 leads/mes** se retiró oficialmente el 30-oct-2025, aunque la guía de developers aún lo lista), etapa objetivo dentro de **28 días** y tasa de conversión de etapa **1–40%**
  (requisitos oficiales de Conversion Leads). **[OFFICIAL META]** (S10-087)
- **Agentes (MCP) para analizar sí; para escribir, con borradores, reglas MCP restrictivas y aprobación humana.** Las
  escrituras son irreversibles y la API tiene límites (4 cambios de presupuesto/hora por ad set). **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Riesgos principales**: fallos silenciosos (200 OK con datos vacíos o campos ignorados), deprecaciones (27-oct-2026),
  tokens y PII en herramientas no-code, conectores que no siguen los cambios de esquema, y decisiones automáticas sobre
  datos ruidosos. **[EMPIRICAL]**

---

## 1. Reporting automático

### 1.1 Opciones

| Nivel | Stack | Pros | Contras |
|---|---|---|---|
| A. SaaS conector | Porter Metrics (gratis), Dataslayer, Windsor.ai, Supermetrics, Two Minute Reports → Sheets/Looker Studio | Rápido (<1 h); mantenimiento del esquema lo hace el proveedor | Coste por cuenta; dependencia; cambios de Meta llegan con retraso (campos vacíos) |
| B. No-code orquestado | n8n (nodos HTTP/Facebook Graph API), Make (apps de Facebook/Meta) → Google Sheets/BigQuery → Slack/email | Flexible, barato; mezcla CRM y Meta | Tú mantienes versiones, paginación, rate limits; plantillas comunitarias con duplicados (S10-075) |
| C. Ingeniería de datos | Airbyte/Fivetran o script propio (Python SDK v26) → BigQuery/Snowflake → dbt → Looker Studio/Metabase/Power BI | Histórico propio, joins con CRM/ventas, control total | Requiere desarrollador; mantener v26/v27 |
| D. Agente/MCP | Claude/ChatGPT + MCP oficial (`mcp.facebook.com/ads`), Manus (read-only) | Preguntas ad hoc en lenguaje natural | No es fuente de verdad auditada; resultados no reproducibles si no se guardan |

Looker Studio **no** tiene conector nativo de Meta: se usan conectores de partners. **[EMPIRICAL]** (S10-088)

### 1.2 Diseño mínimo de un pipeline fiable (B o C)

1. **Extracción**: `GET /act_{id}/insights` a nivel `ad` con `time_increment=1`, campos explícitos, `action_attribution_windows`
   explícitas (p. ej., `7d_click`, `1d_view`; **no** `7d_view`/`28d_view`, que vuelven vacías desde 12-ene-2026) y jobs
   **async** para rangos largos. **[OFFICIAL META]** (S10-001, S10-011)
2. **Ventana móvil**: cada día re-extraer los últimos 28 días (o 7 como mínimo) y sobrescribir. **[STRONG INFERENCE]**
3. **Clave idempotente**: `date + ad_id (+ breakdown)`; nunca "append" sin dedup (problema típico de plantillas n8n).
4. **Metadatos**: guardar `attribution_setting`, versión de API, fecha de extracción. Permite explicar saltos.
5. **Breakdowns**: activar el opt-in de "Additional Breakdowns" por cuenta si se necesita device/hourly/frequency; sin él,
   la API devuelve 200 con datos vacíos (desde 6-ago-2026). **[OFFICIAL META]** (S10-002)
6. **Retención**: unique/hourly solo 13 meses, frequency 6 meses → **guardar histórico propio**. **[OFFICIAL META]** (S10-001)
7. **Geografía**: usar `comscore_market` (no `dma`) desde 22-jun-2026. **[OFFICIAL META]** (S10-002)
8. **Monitorización técnica**: header `X-Ad-Api-Version-Warning` (auto-upgrade), `X-Business-Use-Case`, errores 17/613/80000-80014; alertar si un campo pasa a nulo en todo el día. **[OFFICIAL META]** (S10-010, S10-011)
9. **Capa de negocio**: unir con CRM/ventas (lead cualificado, venta cerrada, margen) para CPA/ROAS "reales".

### 1.3 Contenido mínimo del informe semanal (cliente/dirección)

- Gasto, resultados y coste por resultado **según Meta** (con su atribución declarada) y **según negocio** (CRM/ventas).
- Mix por campaña/objetivo y por concepto creativo (no solo por anuncio).
- Frecuencia y CPM (con opt-in), cambios de la semana (log), incidencias de Meta (status page).
- Nota de discontinuidades cuando aplique (p. ej., "desde marzo-2026 click = link click").

## 2. Alertas

| Alerta | Fuente | Mecanismo recomendado |
|---|---|---|
| Entrega cero / rechazos / cuenta restringida | Ad account webhooks (`effective_status`, jul-2026) o polling | Webhook → n8n → Slack (canal por cliente) |
| Gasto anómalo (pacing) | Insights intradía | Job cada 2–3 h; comparar con curva esperada (flexibilidad 75%) |
| CPA/ROAS fuera de rango | Insights `LAST_3D/7D` excluyendo hoy | Job diario; umbral con volumen mínimo (ver 07) |
| Fatiga creativa | `link_ctr`, `frequency` | Job diario; z-score vs 14 días |
| Caída de señales | Events Manager (diagnósticos, EMQ), volumen de eventos CAPI vs pedidos de backend | Comparar eventos enviados vs pedidos/leads reales |
| Leads que no llegan al CRM | Webhook `leadgen` + conteo en CRM | Conteo diario Meta vs CRM; recordar nueva CA mTLS (31-mar-2026) |
| Cambios hechos por terceros/agentes | Activity log (también vía MCP) | Resumen diario |

**Patrón híbrido** con reglas nativas: regla de Meta trigger-based con `PING_ENDPOINT` → webhook de tu app → n8n decide
(notificar, pedir aprobación en Slack, ejecutar). Ventaja: evaluación en tiempo real en Meta y lógica/aprobación fuera.
**[OFFICIAL META]** (acción PING_ENDPOINT, S10-012) + **[STRONG INFERENCE]** (patrón)

## 3. QA de anuncios (pre-flight y post-launch)

**Pre-flight (antes de publicar)**, automatizable leyendo borradores por API/MCP:
- Naming convention y UTMs presentes y coherentes; URL de destino devuelve 200 y carga rápido.
- Pixel/CAPI disparan el evento de optimización en la landing (test events).
- Categoría especial declarada si aplica (vivienda, empleo, finanzas; en v26 `advantage_audience` explícito).
- Estado de **mejoras de Advantage+ creative** (texto en imagen, música, traducción, destino optimizado, landing IA) según
  la política de la cuenta (ver 04).
- Copy vs guía de marca y lista de palabras prohibidas (un LLM puede pre-revisar; aprobación humana final; ver 09).
- Presupuesto coherente con el CPA objetivo y el volumen necesario (p. ej., presupuesto semanal ≥ ~50 × CPA si se busca
  salir de aprendizaje; ver área 01/09).
- Ubicación/idioma correctos; sin placements excluidos que rompan el estado Advantage+ sin motivo.

**Post-launch (24–72 h)**: rechazos, entrega, CPM anómalo, destino real servido (si "optimize website destination" está ON),
variantes generadas por Meta (capturas para registro).

## 4. Sincronización CRM → Conversions API

### 4.1 Lead ads (Instant Forms) → Conversion Leads (oficial)

- Requisitos (S10-087): usar Instant Forms; etapa a optimizar dentro de **28 días** desde el lead; tasa de conversión de la
  etapa **1–40%**; ~200 leads/mes como orientación (ya no requisito); subida **al menos diaria**; enviar el **Meta Lead ID** (15–17 dígitos) o, si no hay,
  click ID/teléfono/email hasheados. Verificación ~1–2 días; aprendizaje 2–4 semanas; ~3–4 semanas hasta valor.
- Flujo: webhook `leadgen` → CRM (guardar lead_id, form_id, ad_id, campaign_id) → cambios de etapa en CRM → evento CAPI
  (nombre de etapa, timestamp de la etapa, lead_id) → objetivo "Conversion leads". **[OFFICIAL META]**
- Herramientas: integraciones nativas de CRM (HubSpot, Salesforce…), Zapier/Make (apps de Lead Ads y Conversions API),
  n8n (Facebook Lead Ads trigger + HTTP), código propio. **[EMPIRICAL]**

### 4.2 Leads web / ventas offline → CAPI

- Guardar en el CRM `fbc` (de `fbclid`), `fbp`, email/teléfono (normalizados y hasheados SHA-256), `event_id` para
  deduplicar con el Pixel, IP/UA cuando sea legal. El **CAPI Parameter Builder** (Business SDK v26) ayuda a generarlos.
  **[OFFICIAL META]** (S10-004)
- Eventos de etapa (lead cualificado, oportunidad, venta) con `value` = valor esperado o real → permite value
  optimization y value rules por label (`QUALIFIED_LEADS`, `HIGH_VALUE_CUSTOMERS`). **[OFFICIAL META]** (S10-002)
- Ventas en tienda / teléfono: CAPI con `action_source` físico/telefónico (la Offline Conversions API se retiró en mayo-2025).
- Alternativas sin código: CAPI "Meta-enabled" de un clic (solo web, abr-2026), Conversions API Gateway, Signals Gateway
  (envía también a destinos no-Meta). **[OFFICIAL META]**/prensa (S10-063, S10-028)

### 4.3 Cumplimiento

- Restricciones de salud/finanzas: no enviar parámetros/URLs que revelen condiciones (desde 2-sep-2025 Meta marca y
  bloquea audiencias/conversiones sensibles). **[OFFICIAL META]** (S10-066, S10-009)
- UE: base legal/consentimiento para enviar datos de CRM; minimizar campos; usuarios en LPA reciben anuncios con menos
  señales. Contrastar con área 04/08.

## 5. Agentes externos con MCP (arquitectura segura)

1. **Agente analista (read-only)**: lee insights y activity log, genera informes y diagnósticos. Token de system user
   **Employee** (el MCP no acepta Admin, sep-2026) con solo `ads_read`. **[OFFICIAL META]** vía S10-042
2. **Agente operador (write con borrador)**: crea borradores de campañas/anuncios; un humano publica en Ads Manager
   (borradores co-editables desde oct-2026). **[OFFICIAL META]** (S10-014)
3. **Reglas MCP en Business Settings**: bloquear por defecto cambios de presupuesto y estado salvo cuentas autorizadas;
   observado que el panel llega con 7/7 escrituras permitidas → revisarlo en cada portfolio. **[EMPIRICAL]** (S10-084)
4. **Log y reversibilidad**: registrar cada acción del agente (prompt, herramienta, parámetros, respuesta) en tu sistema;
   preparar procedimiento manual de reversión.
5. **Límites**: no más de 1 cambio de presupuesto/hora por ad set desde agentes (margen frente al límite oficial de 4).

## 6. Riesgos y mitigaciones

| Riesgo | Ejemplo | Mitigación |
|---|---|---|
| Fallo silencioso | Breakdown sin opt-in devuelve vacío; Messenger Stories se elimina con 200 | Validar respuestas y objetos guardados; alertas de "campo nulo" |
| Deprecaciones | 27-oct-2026: retiradas de v26 en todas las versiones | Calendario de versiones; tests de integración; ver 06 |
| Discontinuidad de métricas | Cambio a link clicks (mar-2026) | Anotar en dashboards; comparar YoY con cuidado |
| Tokens y secretos | Token de larga duración en un nodo n8n compartido | System users con mínimo privilegio; vault; rotación |
| PII | Emails sin hashear en Sheets | Hashear en origen; minimizar; acceso restringido |
| Rate limits | Bucle que actualiza presupuesto cada 15 min | Respetar 4/h por ad set y BUC; backoff |
| Decisiones sobre ruido | Pausas automáticas por CPA diario | Umbrales estadísticos (07) y aprobación humana |
| Dependencia de vendor | Conector que tarda semanas en adaptarse | Histórico propio en warehouse |
| Agentes con escritura | Agente cambia presupuesto en la cuenta equivocada | Reglas MCP, borradores, cuentas permitidas, logs |
| Coste oculto | Location fees, WhatsApp service messages | Conciliar facturas vs "Amount spent" |

## Implicaciones operativas

- Montar primero: (1) histórico diario propio con ventana móvil, (2) alertas de entrega/gasto/leads, (3) CRM→CAPI.
- Solo después: agentes, QA automático con LLM, reglas de escalado externas.
- Revisar antes del 27-oct-2026 todas las integraciones (n8n/Make/código) que crean o editan anuncios.

## Errores frecuentes

- Descargar solo "ayer" cada día (pierde conversiones atribuidas tarde).
- Mezclar datos de antes y después del 3-mar-2026 sin nota.
- Enviar a CAPI eventos de CRM sin `lead_id`/`fbc` (match pobre) o con retraso semanal.
- Dar a un agente un token de Admin con `ads_management` en todas las cuentas.

## Preguntas abiertas

- ¿Habrá API oficial para las "tareas programadas" del asistente o para exportar sus recomendaciones?
- ¿Qué cuota consume el MCP oficial (comparte BUC con la app del desarrollador)? No documentado en lo consultado.

## Fuentes clave

- [Conversion Leads integration](https://developers.facebook.com/docs/marketing-api/conversions-api/conversion-leads-integration) — meta-developers (S10-087)
- [Rate Limiting](https://developers.facebook.com/docs/marketing-api/overview/rate-limiting) — meta-developers (S10-011)
- [2025](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2025) y [2026 OCC](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) — meta-developers (S10-001, S10-002)
- [Ads MCP server overview](https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-mcp-server/ads-mcp-server-overview.md) — meta-developers (S10-013)
- [n8n: Sync Meta Ads insights to Google Sheets](https://n8n.io/workflows/14721-sync-meta-ads-insights-to-google-sheets-with-backfill-and-weekly-etl/) — comunidad (S10-075)
- [Porter Metrics Looker Studio connector](https://portermetrics.com/en/templates/sheets/facebook-ads) — vendor (S10-088)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Requisitos de Conversion Leads: el "≥200 leads/mes" se presentaba como requisito; Meta lo eliminó el 30-oct-2025 (Meta for Business, "More quality leads this Q5…").
