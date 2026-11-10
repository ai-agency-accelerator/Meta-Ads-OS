# Área 04 — Tracking, atribución y medición (índice y resumen)

> Última verificación: 2026-10-16 · Autor: A04 (agente, tracking specialist / measurement lead) · Ámbito: señales (Pixel, CAPI, datasets, apps, offline, CRM), privacidad, atribución, incrementalidad, MMM y diagnóstico. Ledger: `../fuentes/ledger-04-tracking-atribucion-medicion.md` (115 fuentes).

## Nota sobre etiquetas usadas en esta área

Además de las etiquetas de `00-CONVENCIONES.md`, se usan variantes explícitas para no mezclar fuentes:
- **[OFFICIAL Shopify] / [OFFICIAL Google] / [OFFICIAL WebKit]**: documentación oficial del proveedor correspondiente sobre su propio producto (no es Meta).
- **[OFFICIAL META open source]**: documentación/código de repositorios de Meta (Robyn, GeoLift, plantillas GTM, plugin de WooCommerce).
- **[OFFICIAL META vía practitioner] / [OFFICIAL META citado por …]**: anuncio de Meta conocido a través de una fuente secundaria fiable (no se pudo descargar el texto original).
- **[EMPIRICAL — académico/prensa/vendor]**: evidencia empírica con su tipo de fuente.
- "Inspección de código": conclusiones obtenidas leyendo el código fuente público (p. ej. `template.tpl`), etiquetadas como [OFFICIAL META] cuando el repositorio es de Meta y [STRONG INFERENCE] cuando se infiere comportamiento.

## Índice

| # | Archivo | Para qué sirve |
|---|---|---|
| 01 | [01-arquitectura-senales-pixel-capi-datasets.md](01-arquitectura-senales-pixel-capi-datasets.md) | Modelo mental de señales, datasets, identificadores (`fbc`, `fbp`, `external_id`…), Gateway products, CAPI en un clic, métricas de calidad |
| 02 | [02-implementacion-pixel-capi-paso-a-paso.md](02-implementacion-pixel-capi-paso-a-paso.md) | Implementación con código: `fbq` con `eventID`, payload CAPI, hash, consentimiento, validación |
| 03 | [03-emq-advanced-matching-pii-hashing.md](03-emq-advanced-matching-pii-hashing.md) | EMQ, normalización por campo, vectores de prueba SHA-256, advanced matching |
| 04 | [04-shopify.md](04-shopify.md) | App Facebook & Instagram, niveles de data sharing, web pixels, Customer Privacy API, checkout extensibility |
| 05 | [05-wordpress-woocommerce.md](05-wordpress-woocommerce.md) | Meta for WooCommerce y plugins de terceros (estado oct-2026) |
| 06 | [06-gtm-web-y-server-side.md](06-gtm-web-y-server-side.md) | GTM web + sGTM, tag oficial vs Stape (auditados por código), consentimiento |
| 07 | [07-custom-builds-api-directa.md](07-custom-builds-api-directa.md) | Arquitectura propia, colas, reintentos, Stripe, versionado de API |
| 08 | [08-eventos-offline-y-crm.md](08-eventos-offline-y-crm.md) | Offline (`physical_store`), fin de OCAPI, Conversion Leads (CRM) |
| 09 | [09-privacidad-att-gdpr-consentimiento-aem.md](09-privacidad-att-gdpr-consentimiento-aem.md) | ATT, AEM, UE (consentimiento, LPA/DMA), LDU, categorías sensibles, Safari |
| 10 | [10-atribucion-ventanas-y-modelos.md](10-atribucion-ventanas-y-modelos.md) | Click/engage/view-through, ventanas, incremental attribution, Custom Attribution |
| 11 | [11-meta-vs-ga4-shopify-crm-stripe.md](11-meta-vs-ga4-shopify-crm-stripe.md) | Por qué no coinciden las cifras y qué fuente responde a qué |
| 12 | [12-attribution-lag.md](12-attribution-lag.md) | Retrasos de conversión/señal y su efecto en optimización y reporting |
| 13 | [13-incrementalidad-lift-geo-tests.md](13-incrementalidad-lift-geo-tests.md) | Lift, geo tests, evidencia publicada (Haus, académicos) |
| 14 | [14-mmm-robyn-meridian.md](14-mmm-robyn-meridian.md) | MMM: cuándo, herramientas (estado verificado), triangulación |
| 15 | [15-apps-sdk-skan-mmp.md](15-apps-sdk-skan-mmp.md) | SDK, CAPI para apps, SKAN/AAK, AEM, MMPs |
| 16 | [16-checklist-qa-y-diagnostico-tracking.md](16-checklist-qa-y-diagnostico-tracking.md) | Checklists y árboles de diagnóstico |

## TL;DR del área

1. **Pixel + CAPI redundantes con `event_id` + `event_name` idénticos (48 h) siguen siendo la arquitectura base**; CAPI debe salir del sistema que confirma el pago, no solo replicar el navegador. [OFFICIAL META]
2. **Solo los eventos emparejados atribuyen y optimizan**: la palanca técnica de mayor retorno es `fbc` persistido en servidor + email/teléfono normalizados + IP/UA reales + `external_id`. [OFFICIAL META]
3. **Calidad = EMQ (≥ 6 mínimo Meta), coverage CAPI (objetivo 75 %), freshness real time, dedup alta**; todo consultable por la Dataset Quality API (ampliada may-2025). [OFFICIAL META]
4. **Click-through = solo link clicks desde finales de marzo de 2026**; likes/shares/saves y vídeo ≥ 5 s pasan a *engage-through* (1 día). Series que cruzan marzo de 2026 no son comparables. [OFFICIAL META]
5. **`7d_view` y `28d_view` desaparecieron de la API el 12-ene-2026**; la API replica Ads Manager desde el 10-jun-2025 (report time `mixed`: compras web por fecha de conversión). [OFFICIAL META]
6. **Incremental attribution ya no es una curiosidad**: Haus midió 0,80× iROAS vs standard (jul-24/jun-25) y 1,26× (jul-25/jun-26). Testéala con experimento propio. [EMPIRICAL]
7. **Custom Attribution (AppendAttribution, beta 2026)** permite que Meta optimice con tu modelo de atribución externo — cambio estructural a vigilar. [OFFICIAL META]
8. **AEM web ya no requiere 8 eventos ni verificación de dominio desde mayo de 2023**; quien lo date en 2025 o lo siga configurando trabaja con información desactualizada. [OFFICIAL META vía practitioner] / [OUTDATED]
9. **Sectores sensibles:** core setup, bloqueo de eventos y custom conversions/audiences "flagged" (desde 2-sep-2025) se aplican igual a Pixel y CAPI. [OFFICIAL META] + [EMPIRICAL]
10. **UE 2026:** consentimiento + opción de "compartir menos datos" (LPA, DMA, enero de 2026) reducen la atribución; Meta no ofrece modelado tipo Consent Mode. Experimentos y MMM ganan peso. [OFFICIAL META] + [HYPOTHESIS] (magnitud)
11. **Meta vs GA4 vs Shopify vs Stripe no deben coincidir**; audita tracking comparando Events Manager (recibidos) con backend, no Ads Manager (atribuidos). [STRONG INFERENCE]
12. **Meta es, en la evidencia más amplia disponible, un canal incremental** (Haus: +19 % lift medio, 7d click infra-reporta un 15 % en DTC), pero la atribución sobre-reclama en tácticas concretas; decide con experimentos. [EMPIRICAL]
13. **MMM: Robyn en mantenimiento bajo (CRAN 3.12.1, jul-2025); Meridian muy activo (2.0 en sep-2026 con calibración por experimentos GeoX); PyMC-Marketing 1.x.** [OFFICIAL] (repositorios)
14. **Abril de 2026: CAPI "en un clic" (Meta-enabled) y "AI enrichment" del Pixel**: baja la barrera para pymes, pero no sustituye a un CAPI de backend y requiere revisar duplicados y datos enviados. [EMPIRICAL]

## Línea temporal de cambios 2025–2026 (verificados)

| Fecha | Cambio | Fuente |
|---|---|---|
| 2025-01-14 | `FINANCIAL_PRODUCTS_SERVICES` sustituye a `CREDIT` (categoría especial) | S04-048 |
| 2025-01-15 | Signals Gateway GA (v2.0.0): pipelines, píxel propio, BigQuery | S04-062 |
| 2025-01-29 | Google Meridian disponible para todos | S04-027 |
| 2025 (primavera) | Incremental attribution desplegada (anunciada otoño 2024) | S04-019 |
| 2025-05 | Fin de la Offline Conversions API (con v16.0) | S04-061, S04-097 |
| 2025-05-28 | Dataset Quality API: ACR, coverage, dedup, freshness, diagnósticos EMQ | S04-016 |
| 2025-06-02 / 09-09 / 11-17 | LDU añade Minnesota / Maryland / Rhode Island | S04-067 |
| 2025-06-10 | API ignora `use_unified_attribution_setting` y `action_report_time` (replica Ads Manager, `mixed`) | S04-048 |
| 2025-06-17 | Meta reactiva AMM (datos a nivel dispositivo para MMPs) | S04-046 |
| 2025-07-02 | Robyn 3.12.1 en CRAN (última versión) | S04-025 |
| 2025-08-28 | Shopify: additional scripts de Thank you/Order status en solo lectura | S04-034 |
| 2025-09-02 | Custom audiences/conversions "flagged" (salud, finanzas) bloqueadas en nuevas campañas | S04-095 |
| 2025-10-13/16 | Anuncio de retirada de 7d/28d view y límites de histórico en la API | S04-001 |
| 2026-01 | UE: elección de "compartir menos datos" (DMA) | S04-042 |
| 2026-01-12 | `7d_view`/`28d_view` dejan de devolver datos; límites de histórico de breakdowns | S04-001 |
| 2026-02-18 | Marketing API v25.0 | S04-094 |
| 2026-02-19 | Meridian Scenario Planner | S04-028 |
| 2026-03-03 (despliegue finales de marzo) | Click-through = solo link clicks; engage-through; vídeo 10 s → 5 s | S04-003 |
| 2026 (beta) | Custom Attribution / AppendAttribution | S04-052 |
| 2026-04-15 | Meta-enabled CAPI (un clic) + AI enrichment del Pixel | S04-112, S04-113 |
| 2026-06-22 | `breakdowns=dma` → `comscore_market` | S04-049 |
| 2026-07-16 | Haus: IA supera a standard (1,26×) | S04-022 |
| 2026-08-06 | `frequency_value`, `impression_device`, hourly por zona de audiencia requieren opt-in en algunas cuentas | S04-049 |
| 2026-08-26 | Fecha límite non-Plus Shopify para Thank you/Order status | S04-034 |
| 2026-09-02 | Meridian 2.0 (JAX, calibración con experimentos) | S04-026 |
| 2026-10-06 | Expira Marketing API v24.0 | S04-094 |

## Contradicciones y puntos a contrastar con otras áreas

- **Fecha del fin de la configuración de 8 eventos AEM:** 2023 (Meta vía Jon Loomer/Adviso) vs "junio 2025" (varios blogs de vendors). Esta área concluye 2023 para web. → áreas 10 (cambios), 12 (mitos).
- **Default de atribución post-marzo-2026:** "7d click + 1d engage-through + 1d view" (Dataslayer, Bloom) vs "7d click + 1d view" (Jetfuel). → área 09 (bidding/analítica), 12.
- **Ventana de engage-through y umbral de vídeo:** 1 día y 5 s según Meta/fuentes 2026; algunos blogs siguen con 10 s/97 %. → área 03 (creatividad: métricas de vídeo).
- **Conversion Leads:** "solo Instant Forms" (página principal Meta) vs "Instant Forms o Website Forms" (FAQ Meta); plazos 2–4 semanas vs 1–2 meses. → área 05.
- **Advantage+ vs manual:** Haus (2025) encontró mayor iROAS en manual para 58 % de marcas y sobre-reporte de A+ ~12 pp. → áreas 02 y 12 deben contrastar con su evidencia.
- **Fecha de reporte:** la idea "Meta atribuye la compra al día de la impresión" está desactualizada para conversiones web (conversion time desde 2021; API `mixed`). → área 09/13 (analítica, sistema operativo).
- **Learning phase ~50 eventos/semana:** sin cambio oficial verificado 2025–2026; un blog cita "10 eventos" desde 2024 (no verificado). → área 01/09.
- **Offline `event_time` 7 vs 62 días:** documentación de Meta ambigua.

## Huecos y preguntas abiertas

- Texto oficial del Business Help Center para: core setup, default de atribución 2026, incremental attribution (las páginas no se pudieron descargar; se usaron fuentes secundarias concordantes y documentación de developers).
- Metodología de Incremental attribution (¿PIE? ¿entrenada con Conversion Lift?).
- Requisitos actuales de Conversion Lift self-serve y Brand Lift (mínimos de gasto).
- Soporte oficial de AdAttributionKit por Meta.
- Adopción y efecto en atribución de la opción UE de "compartir menos datos".
- Si Meta fusiona `user_data` de eventos navegador/servidor deduplicados.
- Qué eventos envía exactamente el nivel "Maximum" de Shopify por CAPI.
- Documentación técnica de la Meta-enabled CAPI (hosting, consentimiento, filtrado).

## Fuentes clave del área

Ver ledger completo: [../fuentes/ledger-04-tracking-atribucion-medicion.md](../fuentes/ledger-04-tracking-atribucion-medicion.md). Las más importantes: S04-001, S04-003, S04-005, S04-016, S04-021, S04-022, S04-025/026, S04-048/049/050, S04-052, S04-067, S04-077/078, S04-112/113.
