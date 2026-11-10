# Área 06 — E-commerce/DTC, apps y suscripciones

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: catálogo, Advantage+ catalog ads, Advantage+ sales para e-commerce, clientes nuevos vs existentes, economía (márgenes, MER, LTV), arquitectura por presupuesto, Shops/checkout/promociones, estacionalidad, apps (Advantage+ app, SDK, AEM/SKAN/AdAttributionKit, MMP), suscripciones y web-to-app, casos.

## Índice

| Archivo | Qué resuelve |
|---|---|
| [01-catalogo-feeds-product-sets.md](01-catalogo-feeds-product-sets.md) | Campos y límites del catálogo, match rate, variantes, product sets, overlays, vídeo de catálogo y Dynamic Media |
| [02-advantage-plus-catalog-ads.md](02-advantage-plus-catalog-ads.md) | Catalog ads (ex-DPA): prospección vs retargeting, fin de "Audience Types", incrementalidad, formatos |
| [03-advantage-plus-sales-ecommerce.md](03-advantage-plus-sales-ecommerce.md) | Qué es Advantage+ sales en 2026, cronología API, controles, evidencia (Meta vs Haus), problemas, cuándo manual |
| [04-clientes-nuevos-vs-existentes.md](04-clientes-nuevos-vs-existentes.md) | Definiciones, Customer lifecycle strategy, exclusiones, nCAC (4 variantes), ejemplo de ROAS bueno con adquisición cara |
| [05-economia-ecommerce-margenes-mer-ltv.md](05-economia-ecommerce-margenes-mer-ltv.md) | CM1/CM2/CM3, ROAS/CPA break-even (derivación), MER, cohortes, payback, ejemplos numéricos |
| [06-arquitectura-ecommerce-por-presupuesto.md](06-arquitectura-ecommerce-por-presupuesto.md) | Estructura a €100/€500/€5.000/€50.000 al día; hero product vs catálogo grande; ticket/margen |
| [07-shops-checkout-collection-promociones.md](07-shops-checkout-collection-promociones.md) | Retirada del checkout nativo (2025), Shops ads, colecciones, nuevos checkouts IA (2026, en test), ofertas |
| [08-estacionalidad-bfcm-operativa.md](08-estacionalidad-bfcm-operativa.md) | BFCM 2025 con datos, fases, calendario 2026 (BF 27-nov), ejemplo de descuento vs CPA |
| [09-apps-campanas-y-medicion.md](09-apps-campanas-y-medicion.md) | Advantage+ app 2026, SDK/CAPI/MMP, AEM vs SKAN vs AdAttributionKit, elección de evento, economía de apps |
| [10-suscripciones-y-web2app.md](10-suscripciones-y-web2app.md) | LTV y churn, trial vs pago, benchmarks 2026, web-to-app, Epic v. Apple (estado oct-2026), suscripción e-commerce |
| [11-casos-ecommerce.md](11-casos-ecommerce.md) | 13 casos con números (Haus, Meta, vendors) y plantilla para casos propios |
| Playbooks | [`../14-playbooks/playbook-ecommerce-dtc.md`](../14-playbooks/playbook-ecommerce-dtc.md), [`playbook-productos-consumo.md`](../14-playbooks/playbook-productos-consumo.md), [`playbook-suscripciones.md`](../14-playbooks/playbook-suscripciones.md), [`playbook-apps.md`](../14-playbooks/playbook-apps.md) |
| Ledger | [`../fuentes/ledger-06-ecommerce-apps.md`](../fuentes/ledger-06-ecommerce-apps.md) (98 fuentes) |

## TL;DR del área (las 12 ideas que más importan)

1. **"Advantage+ shopping" ya no existe**: es "Advantage+ sales" (feb-2025) y técnicamente una campaña de Ventas con presupuesto, audiencia y placements Advantage+; la API dejó de crear ASC en v24 (oct-2025), bloqueó crear/actualizar ASC/AAC en todas las versiones con v25 (feb→may-2026) y Meta anunció la pausa de las ASC/AAC restantes con v26 (publicada 29-jul-2026; verificar en cuenta). [OFFICIAL META]
2. **El cap de clientes existentes murió; lo sustituyen Customer lifecycle strategy (GA anunciada 6-oct-2026), exclusiones y la estructura oficial de 2 ad sets con min/max de gasto.** [OFFICIAL META]
3. **Advantage+ no es "mejor" por defecto**: Meta dice +22 % ROAS; Haus (640 tests) vio que gana en iROAS solo en el 42 % de marcas, con −12 % de media y que 50/50 es la peor mezcla. En 2025-2026 la atribución incremental de Meta mejoró (Haus: 1,26× vs estándar). [CONTESTED]
4. **El retargeting / BOF es donde más miente el ROAS** (Javvy: TOF >13× más incremental; BOF con CPIA +250 % vs lo reportado). [EMPIRICAL]
5. **El catálogo es inventario creativo**: match ≥ 90 %, `internal_label` para product sets, vídeo de catálogo en top SKUs (Dynamic Media por defecto desde sep/oct-2025), imagen→vídeo en beta (oct-2026). [OFFICIAL META]
6. **Revenue no es profit**: ROAS break-even = (1 + f) / CM2 % sobre la misma base que reporta Meta (IVA incluido en España). En el ejemplo de cosmética, break-even 2,70; con IF 0,7, hay que ver 3,86 en Ads Manager. [STRONG INFERENCE]
7. **Gestiona adquisición con nCAC y clientes nuevos de tienda, no con el segmento "Nuevo" de Meta** (depende de tu lista). [STRONG INFERENCE]
8. **Estructura según señal**: ~50 eventos/ad set/semana; a €100/día, una campaña y un ad set. El cuello de botella al escalar es creativo (5–8 % de ganadores). [OFFICIAL META] + [EMPIRICAL]
9. **BFCM: CPM +35–57 %, CPA −20 a −42 %; la segunda semana de diciembre es la peor (CPA +39 %)** y el descuento puede hacer que un CPA más bajo sea menos rentable. [EMPIRICAL] + cálculo
10. **El checkout nativo de Shops (solo EE. UU.) se retiró en 2025**; Meta prueba en 2026 checkouts nuevos (Stripe/PayPal, Messenger + Shopify, Meta AI) sin calendario. [OFFICIAL META vía prensa]
11. **Apps: evento temprano y predictivo, AEM para optimizar y SKAN/backend para auditar**; que Meta use AdAttributionKit no está verificado. [OFFICIAL META] / [HYPOTHESIS]
12. **Suscripciones: el churn fija el CPA permitido**; benchmarks 2026 (RevenueCat) y contexto legal de web-to-app en EE. UU. (Supremo revisa desde 30-jun-2026; Apple no cobra en compras enlazadas mientras tanto). [EMPIRICAL] + [OFFICIAL]

## Cambios 2025-2026 detectados (cronológico)

| Fecha | Cambio |
|---|---|
| 29-ene-2025 | Fin de "Audience Types" en Advantage+ catalog ads con objetivo Ventas |
| 6/10-feb-2025 | Consolidación ASC + BAU → "Advantage+ sales" (beta; rollout Q2-2025); retirada del Existing Customer Budget Cap |
| Jun-2025 | Value rules; inicio de la retirada del checkout nativo en Shops (EE. UU.); (corrección A12: el fin de la configuración de 8 eventos AEM y de la verificación de dominio para eventos web es de mayo de 2023 según Meta; en 2025 solo terminó de desaparecer la pestaña AEM en cuentas rezagadas) |
| Ago/sep-2025 | Mayoría de Shops migradas a checkout web; 26-ago Meta deja de ser marketplace tax facilitator |
| 1-sep / 20-oct-2025 | Dynamic Media opt-in por defecto en catalog ads (API) |
| 8-oct-2025 | Marketing API v24: no se crean ASC/AAC |
| 11-dic-2025 | Noveno Circuito en Epic v. Apple (desacato confirmado; comisión razonable permitida) |
| 12-ene-2026 | Retirada de ventanas 7d view y 28d view en Ads Insights API |
| 18-feb-2026 (v25) → 19-may-2026 | Creación/actualización ASC/AAC bloqueada en todas las versiones; `existing_customer_budget_percentage` deprecado |
| Mar-2026 | Engage-through separado de click-through; Flexible/Collection movidos a opciones de formato; test de checkout de un toque (Shoptalk) |
| 30-jun-2026 | Supremo de EE. UU. acepta revisar el estándar de desacato en Epic v. Apple |
| 1-jul-2026 | Location fees de Meta: 2 % UK, 3 % FR/IT/ES, 5 % AT/TR |
| 29-jul-2026 (v26) | Changelog oficial: checkout de Shops discontinuado y Commerce Order Management API deprecada (todas las versiones 27-oct-2026); Shops ads `WEBSITE_AND_SHOP` por defecto (opt-out); Explore Feed y Messenger Stories fuera como placements explícitos. El post de v25 anunciaba pausa de ASC/AAC restantes con v26 (prevista sep-2026; no confirmada en changelog) |
| ~19-ago-2026 | Retirada de controles de placement a nivel ad set (Sales, Leads, App promotion (Engagement no; corrección 2026-11-09)) |
| 6/7-oct-2026 | Customer lifecycle strategy GA ("Adquirir clientes nuevos" con exclusión automática de compradores, 730 d por defecto según Jon Loomer 13-oct); static→video GA; catalog image→video beta; checkouts en Messenger/Meta AI en test |

## Contradicciones y afirmaciones que otras áreas deberían contrastar

- **Fecha exacta y alcance de la retirada del requisito de 8 eventos de AEM web** (fuentes dicen 2023 o jun-2025) → área 04 (tracking).
- **Ventanas de atribución 2026** (7d view/28d view retiradas en API; ¿también en Ads Manager?; engage-through) → área 04.
- **Placements**: alcance de la retirada a nivel ad set (¿4 objetivos?, ¿fecha?) → área 02/07.
- **Learning phase** (~50 eventos/semana) y su vigencia tras Andromeda/Generative Recommender → área 01/09.
- **"Creative Diversity Score"** (ago-2026, solo CTC) → área 03/10.
- **Advantage+ vs manual**: Haus 2025 vs Meta; posible cambio con la mejora de 2025-2026 → área 09/12.
- **Benchmarks de ROAS/CPA** (Triple Whale 1,86–1,88 vs Varos 2,19) → área 11.
- **Location fees** (fechas mayo vs julio-2026) → área 08/09.

## Preguntas abiertas del área

- Definición exacta (ventana, fuentes) de "cliente existente" en Customer lifecycle strategy y efecto en coste.
- Soporte de AdAttributionKit por Meta (reporting/optimización).
- Disponibilidad de value rules en catalog ads; estado del targeting manual en catalog ads de Ventas en 2026.
- Calendario/países de los checkouts dentro de Meta (Stripe/PayPal, Messenger, Meta AI).
- Incrementalidad del retargeting dinámico 2025-2026 con fuente primaria (el "40–70 %" no está trazado).
- Datos estacionales y de devoluciones específicos de España/UE.
- Comisión final de Apple para compras enlazadas en EE. UU. (remand) y reglas DMA en la UE para web-to-app.

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- AEM web: la tabla fechaba en jun-2025 la retirada del requisito de 8 eventos. El Help Center "About Meta's Aggregated Event Measurement" (126789292407737, leído 2026-10-16) describe el cambio (sin priorizar 8 eventos, sin verificación de dominio para configurar eventos, pestaña AEM eliminada) y la documentación de Meta citada por Jon Loomer lo sitúa en mayo de 2023 (posts de LinkedIn del 17/18-may-2023). Coherente con el área 04.
