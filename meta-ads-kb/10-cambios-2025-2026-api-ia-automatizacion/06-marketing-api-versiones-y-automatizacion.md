# Marketing API 2025-2026: versiones, deprecaciones, límites, qué se puede automatizar y MCP oficial

> Última verificación: 2026-11-09 (B21: v27.0 y tabla de versiones; la anterior, 2026-10-15) · Autor: A10 (agente),
> ampliado por B21 · Ámbito: calendario de versiones, cambios que rompen
> integraciones, Insights, rate limits y niveles de acceso, capacidades automatizables y herramientas oficiales/terceras
> (MCP, CLI, SDK). Solo investigación: no se ha llamado a la API con credenciales.

## TL;DR

- **Versiones vigentes a 9-nov-2026**: Marketing API **v25.0** (18-feb-2026, hasta el 23-feb-2027), **v26.0**
  (29-jul-2026, fin TBD) y **v27.0** (4-nov-2026, la última). **v24 expira el 10-nov-2026** (corrección 2026-11-09:
  antes decía "expiró el 6-oct"); v23 el 9-jun-2026; v22 el 19-feb-2026. Ojo: **Graph API** vive ~2 años (v24 hasta
  18-feb-2028) pero **Marketing API** ~1 año. **[OFFICIAL META]** (S10-005, S10-006, S10-007, S10-100)
- **v27.0 (4-nov-2026)** trae dos defaults que afectan a cualquier integración que cree conjuntos de Ventas o
  lookalikes: **expansión de dispositivos activada** si se segmenta por `user_device`/`user_os` (opt-out con
  `targeting_automation.individual_setting.device=0`) y **rechazo de `lookalike_spec` con `country`/`location_spec`**;
  ambos llegan a todas las versiones ~90 días después (≈feb-2027). Además, product showcase por defecto, `items_batch`,
  Ads Burst/Super Burst y OTP de teléfono en formularios. **[OFFICIAL META]** (S10-099, S10-101)
- **27-oct-2026 es la fecha crítica**: la mayoría de retiradas de v26 (Messenger Stories, poll ads, campos de delivery
  estimate, Commerce Order Management API, `web_only` en Web+App, features de protocolo legacy) se aplican a **todas** las
  versiones, incluidas llamadas sin versión. Fijar v25 no protege. **[OFFICIAL META]** (S10-004)
- **ASC/AAC están muertos**: no se pueden crear/editar en ninguna versión desde el 19-may-2026; v26 pausa los restantes. El
  "estado Advantage+" depende de tres palancas (presupuesto de campaña, Advantage+ audience, sin restricciones de
  placement) y se lee en `advantage_state_info`. **[OFFICIAL META]** (S10-003, S10-034)
- **Insights cambió de forma silenciosa varias veces**: atribución unificada forzada (10-jun-2025), sin 7d/28d view
  (12-ene-2026), retención de 13/6 meses para unique/hourly/frequency, breakdowns device/hourly/frequency solo con opt-in
  (6-ago-2026, devuelven vacío sin error), Nielsen DMA → Comscore (22-jun-2026). **[OFFICIAL META]** (S10-001, S10-002)
- **Acceso y límites**: "Marketing API Access Tier" (Limited/Full) desde 4-may-2026; Full Access con 500 llamadas en 15
  días y <15% errores. Presupuesto de un ad set: máx. **4 cambios/hora**; spend cap: **10 cambios/día**. **[OFFICIAL META]** (S10-006, S10-011)
- **Meta ya ofrece herramientas oficiales para agentes**: MCP server (`mcp.facebook.com/ads`, beta abierta 29-abr-2026,
  abierto a cualquier app 16-jul), **Ads CLI**, Developer Tools MCP (read-only), reglas MCP por portfolio y, desde
  6-oct, cambios de agentes como **borradores** con aprobación. **[OFFICIAL META]** (S10-013, S10-014, S10-035)
- **Auto-upgrade**: llamadas a versiones expiradas en endpoints no afectados se ejecutan como la versión siguiente con
  header `X-Ad-Api-Version-Warning`; las afectadas fallan. Algunas retiradas son **silenciosas** (Messenger Stories se
  elimina y devuelve 200). Validar siempre lo guardado. **[OFFICIAL META]** (S10-010, S10-004)

---

## 1. Calendario de versiones

| Versión | Lanzamiento | Marketing API disponible hasta | Graph API disponible hasta |
|---|---|---|---|
| v21.0 | 2-oct-2024 | (expirada) | 21-ene-2027 |
| v22.0 | 21-ene-2025 | **19-feb-2026** | 20-may-2027 |
| v23.0 | 29-may-2025 | **9-jun-2026** | 8-oct-2027 |
| v24.0 | 8-oct-2025 | **10-nov-2026** (la KB decía 6-oct; corrección 2026-11-09) | 18-feb-2028 |
| v25.0 | 18-feb-2026 | **23-feb-2027** | 29-jul-2028 |
| v26.0 | 29-jul-2026 | TBD | TBD |
| v27.0 | **4-nov-2026** | TBD | TBD |

Fuentes: S10-005 (Graph), S10-006/S10-007 (Marketing), **S10-100** (tabla oficial de versiones de la Marketing API en
formato `.md`, consultada el 2026-11-09; las URL antiguas `/docs/...` devolvían una caché sin v27). La v27 llegó ~3
meses después de la v26, antes de lo que estimaba la cadencia de 4 meses.

**Política** (S10-010): nueva versión cada ~4 meses; la anterior convive ≥90 días; al expirar, auto-upgrade si el endpoint
no cambió (desde mayo-2024), opt-out en *Marketing API App Product > Settings*.

## 2. Cambios por versión que importan a un anunciante/integrador

### v22.0 (21-ene-2025) — S10-007
- Fin del opt-in/out del bundle `STANDARD_ENHANCEMENTS` (cada mejora de Advantage+ creative por separado).
- Exclusiones de targeting detallado limitadas a las de control de audiencia de cuenta; `excluded_custom_audiences`.
- `instagram_actor_id` → `instagram_user_id`; endpoints Instagram de Marketing API deprecados (usar Instagram Platform).
- Certificación de custom audiences en categorías especiales (luego cancelada en v23).

### v23.0 (29-may-2025) — S10-008
- `advantage_state` (read-only) en `advantage_state_info`.
- **Advantage+ Audience por defecto** en ad sets nuevos; edad y género como **sugerencias** (`targeting_automation.individual_setting`).

### v24.0 (8-oct-2025) — S10-009
- **Bloqueo ASC/AAC** (crear, duplicar, editar) → Advantage+ campaigns; métodos `migrate_to_advantage_plus` (copy-and-migrate
  o migrate-only, este conserva ID).
- **Daily budget flexibility 25% → 75%** (media semanal ≤ 7× diario).
- `is_adset_budget_sharing_enabled` obligatorio en ABO (hasta 20% compartido).
- `placement_soft_opt_out` (hasta 5% en placements excluidos; Sales/Leads).
- Fin de Facebook video feeds; consolidación de intereses (ad sets antiguos paran el 15-ene-2026).
- Objetos marcados (salud/finanzas) bloqueados; validación de `lookalike_spec` (todas las versiones 6-ene-2026).
- Website destination optimization; fin de lead ads de Messenger por API; `allow_upsert` y límite 30 MB en catálogo.

### v25.0 (18-feb-2026) — S10-003
- ASC/AAC: bloqueo extendido a todas las versiones antes del 19-may-2026; ECBC editable hasta v26 (duplicar → IDs nuevos).
- Ads Insights async: campos de error (`error_code` pasa de uint a int).
- `metadata=1` ignorado.
- Graph: métricas de alcance/impresiones de Página y vídeo deprecadas (jun-2026) → `page_total_media_view_unique`,
  `post_total_media_view_unique`, `page_media_view`, `post_media_view`.
- Webhooks mTLS con nueva CA de Meta (31-mar-2026).

### v26.0 (29-jul-2026) — S10-004
- **HEC-F (vivienda, empleo, finanzas)**: `targeting_automation.advantage_audience` explícito (1 o 0) obligatorio en
  v26+ (error `ADS_TARGETING__REQUIRE_EXPLICIT_ADVANTAGE_AUDIENCE_FLAG`); obligatorio para todos cuando expire v25.
- **Instagram Explore feed eliminado** (pedirlo explícitamente da error).
- **Messenger Stories eliminado** (se quita en silencio; todas las versiones 27-oct).
- **Poll ads deprecados** (todas las versiones 27-oct).
- **Web+App con `applink_treatment=web_only`** ya no se puede adjuntar (todas las versiones 27-oct).
- **Delivery estimate**: se eliminan `daily_outcomes_curve`, `budget_guardrail`, `estimate_dau` sin reemplazo (27-oct).
- **Shop ads**: por defecto `WEBSITE_AND_SHOP` si hay tienda (opt-out `WEBSITE_AND_SHOP_OPT_OUT`).
- **WhatsApp Status ads**: `wamo_whatsapp_identity_spec`; optimización offsite para Sales/Leads/Engagement; LPV; carrusel 10.
- **Commerce Order Management API** bloqueada (47 endpoints; fin de checkout en Shops; sin reemplazo; todas las versiones 27-oct).
- Protocolo legacy: `pretty`, `debug` ignorados; `date_format` y `GET /?ids=` dan error; sin ETag/304.
- Business SDK v26 integra el **Conversions API Parameter Builder** (genera/mejora `fbc`, `fbp`, IP, URLs; normaliza y hashea PII).

### v27.0 (4-nov-2026) — S10-099, S10-101
- **Expansión de dispositivos por defecto**: en conjuntos de Ventas nuevos que segmentan por `user_device` o `user_os`,
  `targeting_automation.individual_setting.device` viene activado (Meta puede entregar fuera de esos dispositivos o SO si
  predice mejor resultado). Opt-out: enviar `0`. Llega a todas las versiones ~90 días después. Para B2B que segmenta
  por SO (p. ej. solo escritorio o solo iOS por el producto), hay que enviarlo explícitamente.
- **`lookalike_spec` con `country` o `location_spec` se rechaza** (todas las versiones a los ~90 días). Ya desde el
  1-sep-2026 el país se ignoraba (S10-042): ahora da error.
- **Product showcase por defecto** (`product_extensions` en `creative_features_spec`): Meta puede añadir productos del
  catálogo a anuncios nuevos. Opt-out:
  `degrees_of_freedom_spec.creative_features_spec.product_extensions.enroll_status=OPT_OUT`; vista previa de lo que
  añadiría: `GET /{ad-account-id}/product_extensions/catalog_suggestions_preview`. Contexto en prensa (S10-129).
- **Catálogos**: `POST /{catalog-id}/batch` → `items_batch`.
- **Reach & frequency**: `meta_moment_maker_spec` → `product_type` `ADS_BURST`/`ADS_SUPER_BURST` en
  `reachfrequencypredictions` (Ads Super Burst del Brand Building Summit, S10-116).
- **Formularios de leads**: `phone_otp_verification_type` (`NOT_ENABLED`, `OTP_REQUIRED`, `OTP_OPTIONAL`). El legacy
  `is_phone_sms_verify_enabled` sigue; `OTP_OPTIONAL` exige un `ad_account_id` elegible; en formularios antiguos el campo
  puede venir `null`. El código llega por WhatsApp o SMS, a elección de Meta (S10-142).
- **Graph API**: funciones legacy (`ids`, `date_format`, `method`, `.as()`, `callback`, `asyncbatch`) cerradas a apps
  nuevas en todas las versiones y eliminadas en v28; `is_ai_generated` en posts de Página; `total_video_consumption_rate`
  sin datos desde principios de nov-2026, sin reemplazo. Graph v21 se elimina el 21-ene-2027 y v22 el 20-may-2027.

## 3. Cambios fuera de ciclo (OCC) relevantes

| Fecha efectiva | Cambio | Fuente |
|---|---|---|
| 14-ene-2025 | `CREDIT` → `FINANCIAL_PRODUCTS_SERVICES` | S10-001 |
| 31-mar-2025 | Placement `notification` | S10-001 |
| 10-jun-2025 | Insights ignora `use_unified_attribution_setting`/`action_report_time` (= Ads Manager) | S10-001 |
| 18-ago-2025 | `is_adset_budget_sharing` | S10-001 |
| 19-ago-2025 | `COMSCORE_MARKET` geotargeting | S10-001 |
| 6-oct-2025 | Fin anuncios políticos/sociales en la UE | S10-001 |
| 11-nov-2025 | Fin `messenger_home` | S10-001 |
| 29-oct-2025 | Métrica `instagram_profile_visits` | S10-001 |
| 12-ene-2026 | Fin 7d_view/28d_view; límites 13/6 meses; MMM breakdowns solo async | S10-001 |
| feb–abr-2026 | Threads: app ads, moderación de respuestas, cuentas de Página, promoción de posts FB/IG | S10-002 |
| 30-mar-2026 | Partnership ads: permisos por creador y ad codes por API | S10-002 |
| 30-abr-2026 | `audience_labels` | S10-002 |
| 1-jun-2026 | IG Audio Swap | S10-002 |
| 11-jun-2026 | Creator Marketplace API ampliada | S10-002 |
| 22-jun-2026 | `breakdowns=dma` → `comscore_market` | S10-002 |
| 28-jun-2026 | `image_animation`, `video_filtering`, `video_uncrop` en `creative_features_spec` | S10-002 |
| 6-ago-2026 | `impression_device`, hourly, `frequency_value` requieren opt-in (async: cuota `min(10, nº ad groups)`/24 h) | S10-002 |
| 13-ago-2026 | Mensajes de marketing de WhatsApp en la Marketing API | S10-102 |
| 6-oct-2026 | `ig_search`: vídeo en los resultados de búsqueda de Instagram (gradual) | S10-102 |
| 19-oct-2026 | `targeting_automation.creative_audience_pairing` (0/1) y `creative_audience_pairing_persona` (en el anuncio o en el medio de `media_sourcing_spec`): audiencia por creativo | S10-102, S10-103 |
| 22-oct-2026 | `is_pca_unified` en campañas (solo OUTCOME_SALES, inmutable; Meta no define "PCA") | S10-102 |
| 5-nov-2026 | Breakdown `pa_creator_ig_handle` (partnership ads por creador; no se combina con otros breakdowns) | S10-102 |

## 4. Migración ASC/AAC → Advantage+ (resumen técnico)

- Estado Advantage+ = tres palancas ENABLED (`advantage_budget_state`, `advantage_audience_state`,
  `advantage_placement_state`): presupuesto a nivel campaña con estrategia soportada; `advantage_audience=1` solo con
  geolocalización (o targeting relajado); sin restricciones de placement. `advantage_state` devuelve
  `ADVANTAGE_PLUS_SALES/APP/LEADS` o `DISABLED`. **[OFFICIAL META]** (S10-034)
- Si el anunciante cambia algo (p. ej., excluye placements), la campaña sigue funcionando pero **pierde el estado
  Advantage+**; no es un error. **[OFFICIAL META]**
- Sustituto del ECBC: dos ad sets (clientes existentes con `targeting_relaxation_types` 0 / resto excluyendo esa audiencia)
  o, desde oct-2026, **Customer Lifecycle Strategy** y labels. **[OFFICIAL META]** (S10-034, S10-014)

## 5. Acceso, permisos y límites

### Niveles de acceso (S10-006, S10-011)
- **Limited Access** (antes Standard/desarrollo): cuotas mínimas; no apto para producción multi-cliente.
- **Full Access** (antes Advanced): requiere ≥500 llamadas en 15 días y <15% de errores en las últimas 500 (desde
  4-may-2026; antes 1.500) + App Review y verificación de negocio para gestionar activos de terceros.

### Límites clave (S10-011)
| Límite | Valor |
|---|---|
| Score por cuenta (lectura 1 / escritura 3) | Limited 60 (bloqueo 300 s) · Full 9.000 (bloqueo 60 s), decae en 300 s |
| Mutaciones (campañas/ad sets/ads) | 100 QPS por app y cuenta |
| BUC `ads_management` | 100.000 (Full) / 300 (Limited) + 40 × anuncios activos, por hora |
| BUC `ads_insights` | 190.000 / 600 + 400 × anuncios activos − 0,001 × errores |
| BUC `custom_audience` | 190.000 / 5.000 + 40 × audiencias activas, tope 700.000 |
| Cambios de presupuesto de un ad set | **4 por hora** (error 613/1487632, bloqueo 1 h) |
| Cambios de spend cap de la cuenta | **10 por día** |
| Creación de anuncios | Ligada al límite de gasto diario de la cuenta |

Headers a monitorizar: `X-Business-Use-Case`, `X-Ad-Account-Usage`, `X-FB-Ads-Insights-Throttle`. Buenas prácticas:
espaciar, batch/async, backoff exponencial, filtrar en Insights, no hacer polling (usar webhooks de cuenta desde jul-2026).

### Permisos
- `ads_read` (lectura/insights), `ads_management` (escritura), `business_management` (activos del portfolio),
  `leads_retrieval` (leads), **`ads_mcp_management`** (MCP con app propia; Advanced Access + App Review para agencias).
  **[OFFICIAL META]**/prensa (S10-035)
- MCP acepta tokens de **system user con rol Employee**, no Admin (4-sep-2026). **[OFFICIAL META]** vía agregador (S10-042)

## 6. Qué se puede automatizar (y con qué)

| Dominio | Qué | Endpoints/herramientas | Nota |
|---|---|---|---|
| Reporting | Métricas por nivel, breakdowns, atribución | `/{id}/insights` (sync/async), MCP, CLI | Async para rangos grandes; opt-in para device/hourly/frequency |
| Creación de campañas | Campañas, ad sets, ads (Advantage+ o manuales) | `/act_/campaigns`, `/adsets`, `/ads`, MCP (borrador) | Validar `advantage_state`; HEC-F con flag explícito |
| Creatividades | Subida de imágenes/vídeos, creatives, mejoras Advantage+ | `/adimages`, `/advideos`, `/adcreatives`, `creative_features_spec` | Opt-in/out por mejora |
| Audiencias | Customer lists (hash), website/app, lookalikes, labels | `/customaudiences`, `audience_labels` | Objetos marcados por salud/finanzas fallan |
| Señales | CAPI (web, app, offline/físico, CRM), datasets | `/{dataset_id}/events`, Parameter Builder, Signals Gateway | OCAPI retirada |
| Leads | Recuperación y webhooks de leads | `leadgen` webhook, `/{form}/leads` | mTLS nueva CA (mar-2026) |
| Reglas | Automated rules por API | `adrules_library` (schedule/trigger) | Ver 07 |
| Recomendaciones | Opportunity Score, aplicar recomendaciones | recommendations API | `lift_estimate` (may-2026) |
| Estado de entrega | Webhooks de cuenta publicitaria | ad account webhooks (jul-2026) | Sustituye polling |
| Catálogos | Productos, feeds, batch | `/{catalog}/items_batch` | 30 MB por payload |
| Threads | Ads, moderación de respuestas | Marketing API (Threads) | `ads_management` para ocultar/responder |
| WhatsApp | Status ads, marketing messages | Marketing API, Marketing Messages API | Max price (2026) |
| Creadores | Creator Marketplace, partnership ads | Creator Marketplace API, branded content permissions | Partnership ads en MCP "pronto" |
| Biblioteca de anuncios | Investigación de competencia | Ad Library API | Política/sociales global; todos los anuncios en la UE (DSA) |

## 7. Herramientas oficiales y de terceros para agentes (2026)

| Herramienta | Tipo | Estado | Notas |
|---|---|---|---|
| **Meta Ads MCP server** (`https://mcp.facebook.com/ads`) | Oficial | Beta abierta (29-abr-2026); cualquier app (16-jul) | OAuth (Facebook Login for Business); reporting, CRUD de campañas/ad sets/ads, audiencias, catálogos, signal diagnostics, búsqueda en Help Center, A/B tests y lift; nº de herramientas variable (fuentes dicen 29 o ~90) |
| **Reglas del MCP** (Business Settings > Integrations > Ads MCP Server) | Oficial | Desde 16-jul / panel 11-ago | Allowed/Blocked por acción y cuenta; observado 7/7 escrituras permitidas por defecto → **bloquear lo que no se use** |
| **Borradores y aprobación** | Oficial | 6-oct-2026 | Lo que hace un agente llega como draft en Ads Manager |
| **Ads CLI** | Oficial | Beta (29-abr-2026) | CRUD desde terminal, para scripts |
| **Developer Tools MCP** | Oficial | ~30-jun-2026 | Read-only (docs, diagnósticos); escritura solo suscripciones de webhooks |
| **Manus connector** | Oficial (Meta) | Beta (mar-2026), read-only | Informes en lenguaje natural |
| **Business SDK v26** + CAPI Parameter Builder | Oficial | jul-2026 | Calidad de señal |
| MCP comunitarios (GitHub: decenas de servidores con 40–135 herramientas) | Terceros | Variable | Revisar permisos, versión de API y si hacen preview antes de escribir |
| SaaS con MCP (AdManage.ai, Triple Whale, Snowflake, Databricks…) | Partners | Integrados (oct-2026) | Ver 08 |

**Riesgos de dar escritura a un agente** (detalle en 08/09): sin deshacer, cambios de presupuesto limitados a 4/hora por
ad set (un agente en bucle puede bloquear el ad set una hora), prompts ambiguos, cuentas equivocadas, credenciales
filtradas. Mitigación: reglas MCP restrictivas, system user Employee, borradores obligatorios, logging. **[STRONG INFERENCE]**

## Implicaciones operativas (checklist de integración, oct-2026; ampliada el 2026-11-09)

0. **Nov-2026**: la v26 sigue siendo válida (fin TBD). Pasar a **v27** tras revisar S10-099 y, en cualquier versión,
   preparar ya los defaults que llegarán a todas en ~feb-2027: `targeting_automation.individual_setting.device=0`
   cuando el plan segmente por dispositivo o SO en Ventas y no quiera expansión; nada de `country`/`location_spec` en
   `lookalike_spec`; opt-out explícito de `product_extensions`; leer `phone_otp_verification_type` tolerando `null`;
   quitar `total_video_consumption_rate` de los informes; no usar funciones legacy de la Graph API.
1. Fijar la integración a **v26** y probar antes del **27-oct-2026**.
2. Buscar en el código: `v22`/`v23`/`v24`, `smart_promotion_type`, `AUTOMATED_SHOPPING_ADS`, `existing_customer_budget_percentage`,
   `7d_view`, `28d_view`, `breakdowns=dma`, `explore`, `messenger_positions: story`, `poll_spec`, `daily_outcomes_curve`.
3. Enviar siempre `targeting_automation.advantage_audience` en ad sets de categorías especiales.
4. Tras cada escritura, **leer y comparar** el objeto guardado (retiradas silenciosas).
5. Activar opt-in de breakdowns en cada cuenta si se reporta frecuencia, hora o dispositivo.
6. Respetar 4 cambios de presupuesto/hora por ad set en cualquier automatización.
7. Monitorizar `X-Ad-Api-Version-Warning` para detectar auto-upgrades.
8. Webhooks: confiar la nueva CA de Meta (mTLS) y migrar polling de estado a webhooks de cuenta.

## Errores frecuentes

- Confundir la vida de Graph API (2 años) con la de Marketing API (~1 año).
- Pensar que un 200 OK significa que el cambio se aplicó como se pidió.
- Reportar con columnas que ahora vuelven vacías (7d_view, breakdowns sin opt-in) sin alertas.
- Usar MCP comunitarios con escritura sin preview ni límites.

## Preguntas abiertas

- ~~Fecha exacta de expiración de Marketing API v25 y llegada de v27.~~ Resuelta el 2026-11-09: v25 hasta el
  23-feb-2027; v27 el 4-nov-2026 (S10-100).
- Fecha de fin de la v26 y fecha exacta en que los defaults de la v27 llegan a todas las versiones.
- Qué significa "PCA" en `is_pca_unified`.
- Lista oficial y estable de herramientas del MCP de Meta (las fuentes discrepan: 29 vs ~90). La página de herramientas
  devolvió contenido vacío el 2026-11-09 (S10-133).
- ¿Llegarán partnership ads y WhatsApp al MCP? (Anunciado sin fecha.)

## Fuentes clave

- [Graph API Versions](https://developers.facebook.com/docs/graph-api/changelog/versions/) — meta-developers (S10-005)
- [Marketing API Changelog](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog) — meta-developers (S10-006)
- [v24.0](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog/version24.0), [v25 blog](https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25), [v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) — meta-developers (S10-009, S10-003, S10-004)
- [v27.0](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version27.0.md), [versiones](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/versions.md), [blog v27](https://developers.facebook.com/blog/post/2026/11/04/introducing-graph-api-v27-and-marketing-api-v27/), [OCC 2026](https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2026.md) — meta-developers (S10-099 a S10-102)
- [Rate Limiting](https://developers.facebook.com/docs/marketing-api/overview/rate-limiting) — meta-developers (S10-011)
- [Versioning](https://developers.facebook.com/documentation/ads-commerce/marketing-api/overview/versioning) — meta-developers (S10-010)
- [Meta Ads AI Connectors](https://www.facebook.com/business/news/meta-ads-ai-connectors) — meta-oficial (S10-013)
- [Meta opens ads MCP to any app](https://ppc.land/meta-opens-ads-mcp-to-any-app-cutting-integration-code-to-zero/) — 2026-07-18 — prensa (S10-035)
