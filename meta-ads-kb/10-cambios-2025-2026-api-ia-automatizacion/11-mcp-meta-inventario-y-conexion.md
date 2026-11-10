# MCP oficial de Meta Ads: inventario de herramientas, conexión y seguridad

> Última verificación: 2026-10-17 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: agente principal · Fuentes: documentación de developers (índice
> `developers.facebook.com/documentation/ads-commerce/llms.txt`), Help Center 1456422242197840 y prueba del endpoint.

## TL;DR
- Servidor remoto alojado por Meta: `https://mcp.facebook.com/ads`. Claude Code es cliente soportado oficialmente; no
  hace falta app propia: OAuth con Facebook Login for Business y **registro dinámico de cliente**
  (`registration_endpoint: https://mcp.facebook.com/.well-known/register/ads`, PKCE S256). **[OFFICIAL META]**
- Permisos (scopes) que pide: `ads_management`, `ads_read`, `catalog_management`, `business_management`,
  `pages_show_list`, `pages_manage_ads`, `instagram_basic`, `instagram_branded_content_ads_brand`, `ads_mcp_management`.
- Las herramientas de escritura **crean entidades en pausa**; `ads_activate_entity` es la que empieza a gastar. **[OFFICIAL META]**
- Control en el servidor: Business Settings → Integrations → **Ads MCP server** → por cuenta/catálogo, permitir o
  bloquear acciones (crear campañas, editar presupuesto, editar catálogos…) y bloquear presupuestos por encima de un
  importe. Los partners pueden fijar reglas para sus empleados. **[OFFICIAL META]**
- Meta afirma que usar el MCP no pone la cuenta en riesgo de baneo por sí mismo. **[OFFICIAL META]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - La página oficial de herramientas del MCP devolvió contenido vacío el 2026-11-09: no hay cambios de herramientas verificables desde el 17-oct.
> - **Muse para pequeñas empresas** (EE. UU. y Canadá) es la alternativa nativa de Meta a conectar un agente externo; también redacta y espera aprobación. **[OFFICIAL META]**
> - La API v27 (4-nov) no cambia el MCP, pero lo que se crea por el MCP hereda los defaults nuevos (expansión de dispositivos, product showcase): revisa el borrador antes de aprobarlo. **[STRONG INFERENCE]**
> - Fuentes: S10-099, S10-123, S10-133 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## Inventario (17-oct-2026)
| Categoría | Lectura | Escritura |
|---|---|---|
| Reporting | `ads_get_ad_entities`, `ads_get_opportunity_score`, `ads_insights_advertiser_context`, `ads_insights_anomaly_signal`, `ads_insights_auction_ranking_benchmarks`, `ads_insights_industry_benchmark`, `ads_insights_performance_trend` | — |
| Cuentas y Páginas | `ads_get_ad_accounts`, `ads_get_ad_account_pages`, `ads_get_pages_for_business`, `ads_get_user_pages`, `ads_get_field_context` | — |
| Campañas / ad sets / anuncios | (`ads_get_ad_entities`) | `ads_create_campaign`, `ads_create_ad_set`, `ads_create_ad` (en pausa), `ads_update_entity`, `ads_activate_entity` |
| Creatividades | `ads_get_creatives`, `ads_get_creative_ads`, `ads_get_ad_images`, `ads_get_ad_videos`, `ads_get_ad_preview` | `ads_create_creative` (imagen única con enlace) |
| Ad Library | `ads_library_search` | — |
| Instagram | `ads_get_ig_accounts`, `ads_get_ig_media` | `ads_boost_ig_post` |
| Audiencias | `ads_get_ad_account_custom_audiences`, `ads_get_custom_audience`, `ads_get_custom_audience_adsets` | `ads_create_custom_audience`, `ads_update_custom_audience`, `ads_update_custom_audience_users`, `ads_delete_custom_audience` |
| Datasets / píxel | `ads_get_datasets`, `ads_get_dataset_details`, `ads_get_dataset_stats`, `ads_get_dataset_quality`, `ads_pixel_event_read`, `ads_pixel_parameter_read`, `ads_get_customconversions` | `ads_pixel_event_create/update/delete`, `ads_pixel_parameter_create/update/delete` |
| Catálogos | `ads_catalog_get_*` (catálogos, detalles, diagnósticos, salud de dynamic ads, fuentes, productos, product sets, feeds, reglas), `ads_catalog_search_product`, `ads_catalog_event_source_get*` | `ads_catalog_create*`, `ads_catalog_update*`, `ads_catalog_product_create`, `ads_catalog_*delete*`, `ads_catalog_event_source_connect/disconnect` |
| Ayuda | `ads_get_errors`, `ads_get_help_article` | — |
| Experimentos | `ads_experiment_list_tests`, `ads_experiment_check_eligibility`, `ads_experiment_abtest_get_test`, `ads_experiment_lift_get_test` | `ads_experiment_abtest_create_test`, `ads_experiment_abtest_update_test`, `ads_experiment_lift_create_test` |
| Historial | `ads_account_get_activity_logs` | — |

En Claude Code los nombres quedan como `mcp__meta-ads__<herramienta>`. La configuración de permisos de este proyecto
(`.claude/settings.json`): lectura permitida, escritura con confirmación, borrados bloqueados.

## Limitaciones a tener en cuenta
- `ads_create_creative` solo cubre creatividades de imagen única con enlace; vídeo, carrusel, catálogo o partnership
  ads pueden requerir Ads Manager, Ads CLI o la Marketing API (verificar novedades).
- `ads_library_search`: sujeto a los mismos límites de datos de la Ad Library (alcance y segmentación solo en la UE).
- Herramientas y nombres pueden cambiar: revisar con `/mcp` y `/conectar meta` tras cada actualización de Meta.

## Alternativas
- **Ads CLI** oficial (`meta ads <recurso> <acción>`): token de system user; útil para scripts y automatizaciones fuera de Claude.
- **Marketing API** directa (Graph API v26.0 a oct-2026).
