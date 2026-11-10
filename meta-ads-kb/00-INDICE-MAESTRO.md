# Meta Ads — Índice maestro de la base de conocimiento

> Última actualización: 2026-11-09 (playbook de consultoras de IA y automatización) · ~470.000 palabras (recuento del 2026-11-10, sin contar `fuentes/` ni ledgers) · ~1.340 fuentes registradas · 16 secciones.
> Esta base alimenta Meta Ads OS (`../CLAUDE.md`, guía de uso en `../README.md` y `../docs/`, skills y agentes en `../.claude/`).
> Empieza por **[00-SINTESIS-EJECUTIVA](00-SINTESIS-EJECUTIVA.md)** (lo importante en una lectura) y
> **[00-ESTADO-ACTUAL-2026](00-ESTADO-ACTUAL-2026.md)** (qué está vigente hoy). Para trabajar una cuenta, ve a
> **[13-sistema-operativo](13-sistema-operativo/README.md)**.

## Documentos raíz

| Documento | Para qué |
|---|---|
| [00-SINTESIS-EJECUTIVA](00-SINTESIS-EJECUTIVA.md) | Resumen de todo: cómo funciona Meta, cambios, arquitectura, presupuesto, pujas, creatividad, tracking, atribución, lead gen, ecommerce, IG, WhatsApp, escalado, políticas, mitos, frameworks y preguntas abiertas |
| [00-ESTADO-ACTUAL-2026](00-ESTADO-ACTUAL-2026.md) | **Documento vivo**: qué funciona, qué cambió, qué desaparece, nomenclatura vigente, reglas oficiales, calendario |
| [00-CONVENCIONES](00-CONVENCIONES.md) | Etiquetas de evidencia, plantilla y formato del ledger |
| [fuentes/00-SOURCE-LEDGER-MAESTRO](fuentes/00-SOURCE-LEDGER-MAESTRO.md) | Ledgers por área, fuentes fundamentales y métodos de acceso |

## Preguntas frecuentes → dónde está la respuesta

| Pregunta | Ir a |
|---|---|
| ¿Cómo decide Meta a quién mostrar un anuncio? | [01/03](01-subasta-delivery-ml/03-pipeline-retrieval-ranking-entrega.md), [01/02](01-subasta-delivery-ml/02-subasta-total-value.md) |
| ¿Qué son Andromeda, GEM, Lattice, Generative Recommender y qué cambian para mí? | [01/04](01-subasta-delivery-ml/04-sistemas-ml-andromeda-gem-lattice.md), [01/09](01-subasta-delivery-ml/09-implicaciones-para-el-anunciante.md) |
| ¿Qué objetivo y qué evento elijo? | [02/01](02-estructura-campanas/01-objetivos-campana-2026.md), [02/02](02-estructura-campanas/02-eventos-de-optimizacion.md) |
| ¿Cuánto necesito para salir de learning? ¿Qué lo reinicia? | [02/03](02-estructura-campanas/03-learning-phase.md) |
| Tengo X €/día, ¿qué estructura? | [02/06](02-estructura-campanas/06-presupuesto-por-niveles.md), [13/09](13-sistema-operativo/09-presupuesto-pequeno-y-grande.md) |
| ¿Broad, intereses, lookalikes? ¿Cuándo segmentar? | [02/07](02-estructura-campanas/07-audiencias-2026.md) |
| ¿Qué automatiza Advantage+ y qué controlo? | [02/08](02-estructura-campanas/08-advantage-plus-ecosistema.md) |
| ¿Retargeting separado? ¿Duplicar? | [02/09](02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md) |
| ¿Hook, ángulo, concepto…? ¿Qué es un creativo nuevo? | [03/02](03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md) |
| ¿Cómo testeo creatividades? | [13/05](13-sistema-operativo/05-framework-testing-creativo.md), [03/05](03-creatividad/05-testing-creativo.md) |
| ¿Es fatiga o ruido? | [03/06](03-creatividad/06-fatiga-creativa.md), [13/07 §9](13-sistema-operativo/07-framework-diagnostico.md) |
| ¿Qué formato funciona en B2B y SaaS? ¿Avatar, clon o voz con IA? ¿Tengo que etiquetar la IA? | [03/16](03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md) |
| ¿Cómo instalo Pixel + CAPI y lo valido? | [04/02](04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md), [04/16](04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md) |
| ¿Por qué Meta, GA4 y Shopify no coinciden? | [04/11](04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md) |
| ¿Qué ventas causó Meta de verdad? | [04/13](04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md), [04/14](04-tracking-atribucion-medicion/14-mmm-robyn-meridian.md) |
| ¿Cuánto puedo pagar por lead / llamada / venta? | [05/05](05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md) + `herramientas/economia.py`, [09/08](09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md) |
| ¿Mi landing convierte el tráfico de Meta? ¿Problema de anuncio o de conversión? | [03/15](03-creatividad/15-landing-pages-y-cro-trafico-meta.md), [03/09](03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md) |
| ¿Instant form o landing? ¿Qué preguntas? | [05/01](05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md), [05/02](05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md) |
| ¿Cómo devuelvo la calidad del lead a Meta? | [05/03](05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md), [05/04](05-leadgen-high-ticket-crm/04-integraciones-crm.md), [05/09](05-leadgen-high-ticket-crm/09-sales-feedback-loop.md) |
| Soy una consultora o agencia de IA y automatización: ¿cómo capto pymes con Meta (oferta de entrada, embudo, evento, creatividad, propuesta)? | [Playbook de consultoras de IA y automatización](14-playbooks/playbook-consultoras-ia-automatizacion.md) |
| ¿Cómo gestiono Meta para los clientes de mi agencia (onboarding, contrato, reporting, precio)? | [Agencias y consultores, parte B](14-playbooks/playbook-agencias-consultores.md), [consultoras de IA §14](14-playbooks/playbook-consultoras-ia-automatizacion.md) |
| ¿ROAS break-even, MER, nCAC, LTV? | [06/05](06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md) |
| ¿Placements, specs, safe zones? | [07/01](07-instagram-placements-mensajeria/01-mapa-placements-2026.md), [07/03](07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md) |
| ¿WhatsApp: cómo medir revenue? | [07/12](07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md) |
| ¿Me van a rechazar este copy? ¿Cómo lo escribo compliant? | [08/08](08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md), [08/11](08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md) |
| Me han restringido la cuenta | [08/01](08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md), [08/09](08-cuenta-politicas-seguridad/09-rechazos-apelaciones-que-no-hacer.md) |
| ¿Qué puja uso? | [09/01](09-bidding-escalado-economia-analitica/01-estrategias-de-puja.md) |
| ¿Cómo escalo? ¿Cuánto subo el presupuesto? | [13/06](13-sistema-operativo/06-framework-escalado.md), [09/03](09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md), [09/04](09-bidding-escalado-economia-analitica/04-cambios-de-presupuesto-y-duplicacion.md) |
| ¿Cuándo no tocar una campaña? ¿Es significativo? | [09/11](09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md), [09/12](09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md) |
| ¿Qué ha cambiado este año? | [00-ESTADO-ACTUAL-2026](00-ESTADO-ACTUAL-2026.md), [10/02](10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md) |
| ¿Qué puedo automatizar con la API/MCP/IA? | [10/06](10-cambios-2025-2026-api-ia-automatizacion/06-marketing-api-versiones-y-automatizacion.md), [10/08](10-cambios-2025-2026-api-ia-automatizacion/08-automatizacion-externa-n8n-make-sheets-slack-bi.md), [10/09](10-cambios-2025-2026-api-ia-automatizacion/09-ia-para-nuestro-workflow.md) |
| ¿Qué cambia en España y LatAm (costes, impuestos, WhatsApp, pagos, regulación)? | [11/10](11-benchmarks-casos-expertos/10-espana-latam.md) |
| ¿Qué se queja la comunidad ahora mismo? | [11/08](11-benchmarks-casos-expertos/08-voice-of-advertiser-2025-2026.md) (barrido de Reddit), [11/09](11-benchmarks-casos-expertos/09-bugs-y-comportamientos-raros.md) |
| ¿Este CPM/CTR/CPL es normal? | [11/01](11-benchmarks-casos-expertos/01-benchmarks-2025-2026.md), [11/02](11-benchmarks-casos-expertos/02-como-usar-benchmarks.md) |
| ¿Esto que dicen en un curso es verdad? | [12/01](12-mitos-contradicciones/01-mitos-meta-ads-2026.md) |
| Algo va mal, ¿por dónde empiezo? | [13/07](13-sistema-operativo/07-framework-diagnostico.md) |

## Mapa completo

### 01 · Subasta, delivery, ML e historia — [README](01-subasta-delivery-ml/README.md)
[01 modelo de negocio](01-subasta-delivery-ml/01-modelo-negocio-meta.md) · [02 subasta y total value](01-subasta-delivery-ml/02-subasta-total-value.md) ·
[03 pipeline retrieval→ranking→entrega](01-subasta-delivery-ml/03-pipeline-retrieval-ranking-entrega.md) · [04 sistemas de ML](01-subasta-delivery-ml/04-sistemas-ml-andromeda-gem-lattice.md) ·
[05 exploración/explotación y señales](01-subasta-delivery-ml/05-exploracion-explotacion-senales-feedback.md) · [06 pacing, presupuesto y frecuencia](01-subasta-delivery-ml/06-pacing-presupuesto-frecuencia.md) ·
[07 calidad y diagnósticos de relevancia](01-subasta-delivery-ml/07-calidad-anuncio-y-diagnosticos-relevancia.md) · [08 historia 2015–2026](01-subasta-delivery-ml/08-historia-evolucion-2015-2026.md) ·
[09 implicaciones para el anunciante](01-subasta-delivery-ml/09-implicaciones-para-el-anunciante.md)

### 02 · Estructura de campañas — [README](02-estructura-campanas/README.md)
[01 objetivos](02-estructura-campanas/01-objetivos-campana-2026.md) · [02 eventos de optimización](02-estructura-campanas/02-eventos-de-optimizacion.md) ·
[03 learning phase](02-estructura-campanas/03-learning-phase.md) · [04 Business Portfolio y activos](02-estructura-campanas/04-business-portfolio-activos-estructura-cuenta.md) ·
[05 arquitectura](02-estructura-campanas/05-arquitectura-de-campanas.md) · [06 presupuesto por niveles](02-estructura-campanas/06-presupuesto-por-niveles.md) ·
[07 audiencias](02-estructura-campanas/07-audiencias-2026.md) · [08 Advantage+](02-estructura-campanas/08-advantage-plus-ecosistema.md) ·
[09 retargeting, exclusiones, duplicación](02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md) · [10 cuenta nueva vs heredada](02-estructura-campanas/10-cuenta-nueva-vs-heredada.md)

### 03 · Creatividad — [README](03-creatividad/README.md)
[01 creative = targeting](03-creatividad/01-creative-es-targeting.md) · [02 taxonomía](03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md) ·
[03 estrategia desde primeros principios](03-creatividad/03-estrategia-creativa-primeros-principios.md) · [04 formatos y estilos](03-creatividad/04-formatos-y-estilos.md) ·
[05 testing](03-creatividad/05-testing-creativo.md) · [06 fatiga](03-creatividad/06-fatiga-creativa.md) · [07 analítica creativa](03-creatividad/07-analitica-creativa-metricas.md) ·
[08 copy](03-creatividad/08-copy-de-anuncios.md) · [09 oferta y diagnóstico ad/oferta/landing/ventas](03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md) ·
[10 competencia y Ad Library](03-creatividad/10-investigacion-competencia-ad-library.md) · [11 sistema de investigación 50–100 anuncios](03-creatividad/11-sistema-investigacion-creativa-50-100-anuncios.md) ·
[12 comentarios y prueba social](03-creatividad/12-comentarios-y-prueba-social.md) · [13 producción y feedback loop](03-creatividad/13-produccion-y-feedback-loop-creativo.md) ·
[14 IA creativa de Meta](03-creatividad/14-herramientas-ia-creativa-meta.md) · [15 landing pages y CRO para tráfico de Meta](03-creatividad/15-landing-pages-y-cro-trafico-meta.md) ·
[16 IA generativa en anuncios: qué funciona y etiquetado](03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md)

### 04 · Tracking, atribución y medición — [README](04-tracking-atribucion-medicion/README.md)
[01 arquitectura de señales](04-tracking-atribucion-medicion/01-arquitectura-senales-pixel-capi-datasets.md) · [02 implementación paso a paso](04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md) ·
[03 EMQ, matching, hashing](04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md) · [04 Shopify](04-tracking-atribucion-medicion/04-shopify.md) ·
[05 WordPress/WooCommerce](04-tracking-atribucion-medicion/05-wordpress-woocommerce.md) · [06 GTM y sGTM](04-tracking-atribucion-medicion/06-gtm-web-y-server-side.md) ·
[07 builds custom](04-tracking-atribucion-medicion/07-custom-builds-api-directa.md) · [08 offline y CRM](04-tracking-atribucion-medicion/08-eventos-offline-y-crm.md) ·
[09 privacidad, ATT, GDPR, AEM](04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md) · [10 atribución](04-tracking-atribucion-medicion/10-atribucion-ventanas-y-modelos.md) ·
[11 Meta vs GA4/Shopify/CRM/Stripe](04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md) · [12 attribution lag](04-tracking-atribucion-medicion/12-attribution-lag.md) ·
[13 incrementalidad](04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md) · [14 MMM](04-tracking-atribucion-medicion/14-mmm-robyn-meridian.md) ·
[15 apps](04-tracking-atribucion-medicion/15-apps-sdk-skan-mmp.md) · [16 QA y diagnóstico](04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md)

### 05 · Lead gen, high-ticket y CRM — [README](05-leadgen-high-ticket-crm/README.md)
[01 canales](05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md) · [02 instant forms](05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md) ·
[03 calidad y qualified leads](05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md) · [04 integraciones CRM](05-leadgen-high-ticket-crm/04-integraciones-crm.md) ·
[05 economía y calculadoras](05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md) · [06 funnels high-ticket](05-leadgen-high-ticket-crm/06-high-ticket-funnels.md) ·
[07 webinars, eventos, lanzamientos](05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md) · [08 speed to lead y show rate](05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md) ·
[09 sales feedback loop](05-leadgen-high-ticket-crm/09-sales-feedback-loop.md) · [10 B2B, SaaS y local](05-leadgen-high-ticket-crm/10-b2b-saas-local.md) ·
calculadora: [`herramientas/economia.py`](../herramientas/economia.py) (fuera de la KB)

### 06 · Ecommerce, apps y suscripciones — [README](06-ecommerce-apps/README.md)
[01 catálogo](06-ecommerce-apps/01-catalogo-feeds-product-sets.md) · [02 Advantage+ catalog ads](06-ecommerce-apps/02-advantage-plus-catalog-ads.md) ·
[03 Advantage+ sales](06-ecommerce-apps/03-advantage-plus-sales-ecommerce.md) · [04 nuevos vs existentes](06-ecommerce-apps/04-clientes-nuevos-vs-existentes.md) ·
[05 economía (MER, nCAC, LTV)](06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md) · [06 arquitectura por presupuesto](06-ecommerce-apps/06-arquitectura-ecommerce-por-presupuesto.md) ·
[07 Shops, checkout, collection](06-ecommerce-apps/07-shops-checkout-collection-promociones.md) · [08 estacionalidad y BFCM](06-ecommerce-apps/08-estacionalidad-bfcm-operativa.md) ·
[09 apps](06-ecommerce-apps/09-apps-campanas-y-medicion.md) · [10 suscripciones y web-to-app](06-ecommerce-apps/10-suscripciones-y-web2app.md) · [11 casos](06-ecommerce-apps/11-casos-ecommerce.md)

### 07 · Instagram, placements y mensajería — [README](07-instagram-placements-mensajeria/README.md)
[01 mapa de placements](07-instagram-placements-mensajeria/01-mapa-placements-2026.md) · [02 Advantage+ placements y exclusiones](07-instagram-placements-mensajeria/02-advantage-placements-y-exclusiones.md) ·
[03 specs y safe zones](07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md) · [04 Instagram a fondo](07-instagram-placements-mensajeria/04-instagram-a-fondo.md) ·
[05 Instagram DM y automatización](07-instagram-placements-mensajeria/05-instagram-dm-y-automatizacion.md) · [06 partnership ads y creadores](07-instagram-placements-mensajeria/06-partnership-ads-creadores-ugc-whitelisting.md) ·
[07 orgánico + pagado](07-instagram-placements-mensajeria/07-organico-mas-pagado-post-ids-boost.md) · [08 comentarios](07-instagram-placements-mensajeria/08-comentarios-y-moderacion.md) ·
[09 Threads](07-instagram-placements-mensajeria/09-threads-ads.md) · [10 Messenger](07-instagram-placements-mensajeria/10-messenger-ads.md) ·
[11 WhatsApp ads](07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md) · [12 WhatsApp Platform y revenue](07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md) ·
[13 Business AI](07-instagram-placements-mensajeria/13-business-ai-agentes-mensajeria.md) · [14 funnels de mensajería](07-instagram-placements-mensajeria/14-funnels-de-mensajeria.md)

### 08 · Cuenta, políticas y seguridad — [README](08-cuenta-politicas-seguridad/README.md)
[01 Account Quality](08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md) · [02 verificaciones](08-cuenta-politicas-seguridad/02-verificaciones.md) ·
[03 seguridad del Portfolio](08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md) · [04 pagos y límites](08-cuenta-politicas-seguridad/04-pagos-facturacion-limites.md) ·
[05 soporte](08-cuenta-politicas-seguridad/05-soporte-meta-canales-elegibilidad.md) · [06 Advertising Standards](08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md) ·
[07 categorías especiales y sensibles](08-cuenta-politicas-seguridad/07-categorias-especiales-y-sensibles.md) · [08 infoproductos y claims](08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md) ·
[09 rechazos y apelaciones](08-cuenta-politicas-seguridad/09-rechazos-apelaciones-que-no-hacer.md) · [10 landing pages](08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md) ·
[11 copy compliant](08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md) · [12 cuentas nuevas y anti-scam](08-cuenta-politicas-seguridad/12-cuentas-nuevas-y-enforcement-antiscam.md)

### 09 · Bidding, escalado, economía y analítica — [README](09-bidding-escalado-economia-analitica/README.md)
[01 pujas](09-bidding-escalado-economia-analitica/01-estrategias-de-puja.md) · [02 value optimization y value rules](09-bidding-escalado-economia-analitica/02-value-optimization-y-value-rules.md) ·
[03 escalado](09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md) · [04 cambios de presupuesto y duplicación](09-bidding-escalado-economia-analitica/04-cambios-de-presupuesto-y-duplicacion.md) ·
[05 CPM](09-bidding-escalado-economia-analitica/05-cpm-que-lo-determina.md) · [06 estacionalidad](09-bidding-escalado-economia-analitica/06-estacionalidad.md) · [07 frecuencia](09-bidding-escalado-economia-analitica/07-frecuencia.md) ·
[08 economía unitaria](09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md) · [09 métricas y diagnóstico top-down](09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md) ·
[10 dashboards](09-bidding-escalado-economia-analitica/10-dashboards-reporting.md) · [11 cuándo no tocar](09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md) ·
[12 estadística](09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md) · [13 experimentación](09-bidding-escalado-economia-analitica/13-experimentacion-ab-tests.md)

### 10 · Cambios 2025–2026, API, IA y automatización — [README](10-cambios-2025-2026-api-ia-automatizacion/README.md)
[01 changelog 2025](10-cambios-2025-2026-api-ia-automatizacion/01-changelog-2025.md) · [02 changelog 2026](10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md) ·
[03 tendencias y control](10-cambios-2025-2026-api-ia-automatizacion/03-tendencias-que-desaparece-que-controla-meta.md) · [04 IA nativa](10-cambios-2025-2026-api-ia-automatizacion/04-ia-nativa-meta-advantage-creative-genai.md) ·
[05 Business AI y agentes](10-cambios-2025-2026-api-ia-automatizacion/05-business-ai-y-agentes.md) · [06 Marketing API y MCP](10-cambios-2025-2026-api-ia-automatizacion/06-marketing-api-versiones-y-automatizacion.md) ·
[07 reglas automáticas](10-cambios-2025-2026-api-ia-automatizacion/07-reglas-automaticas.md) · [08 automatización externa](10-cambios-2025-2026-api-ia-automatizacion/08-automatizacion-externa-n8n-make-sheets-slack-bi.md) ·
[09 IA para nuestro workflow](10-cambios-2025-2026-api-ia-automatizacion/09-ia-para-nuestro-workflow.md) · [10 cómo vigilar cambios](10-cambios-2025-2026-api-ia-automatizacion/10-como-vigilar-cambios.md) ·
[11 MCP oficial de Meta: herramientas, conexión y seguridad](10-cambios-2025-2026-api-ia-automatizacion/11-mcp-meta-inventario-y-conexion.md)

### 11 · Benchmarks, casos, expertos y comunidad — [README](11-benchmarks-casos-expertos/README.md)
[01 benchmarks](11-benchmarks-casos-expertos/01-benchmarks-2025-2026.md) · [02 cómo usarlos](11-benchmarks-casos-expertos/02-como-usar-benchmarks.md) ·
[03 geografías](11-benchmarks-casos-expertos/03-geografias-costes-comportamiento.md) · [04 escalado internacional](11-benchmarks-casos-expertos/04-escalado-internacional.md) ·
[05 casos reales](11-benchmarks-casos-expertos/05-biblioteca-casos-reales.md) · [06 fracasos](11-benchmarks-casos-expertos/06-biblioteca-fracasos.md) ·
[07 expertos y discrepancias](11-benchmarks-casos-expertos/07-expertos-mapa-y-discrepancias.md) · [08 Voice of Advertiser](11-benchmarks-casos-expertos/08-voice-of-advertiser-2025-2026.md) ·
[09 bugs y comportamientos raros](11-benchmarks-casos-expertos/09-bugs-y-comportamientos-raros.md) ·
[10 España y LatAm](11-benchmarks-casos-expertos/10-espana-latam.md)

### 12 · Mitos y contradicciones — [README](12-mitos-contradicciones/README.md)
[01 mitos 2026 (66)](12-mitos-contradicciones/01-mitos-meta-ads-2026.md) · [02 contradicciones entre expertos](12-mitos-contradicciones/02-contradicciones-entre-expertos.md) ·
[03 folklore obsoleto por era](12-mitos-contradicciones/03-folklore-obsoleto-por-era.md) · [04 afirmaciones sin evidencia](12-mitos-contradicciones/04-afirmaciones-sin-evidencia.md) ·
[05 revisión adversarial de toda la base (16-oct-2026)](12-mitos-contradicciones/05-revision-adversarial-kb.md)

### 13 · Sistema operativo — [README](13-sistema-operativo/README.md)
[01 principios](13-sistema-operativo/01-principios-de-razonamiento.md) · [02 auditoría](13-sistema-operativo/02-framework-auditoria.md) · [03 lanzamiento](13-sistema-operativo/03-framework-lanzamiento.md) ·
[04 operativa diaria/semanal/mensual](13-sistema-operativo/04-operativa-diaria-semanal-mensual.md) · [05 testing creativo](13-sistema-operativo/05-framework-testing-creativo.md) ·
[06 escalado](13-sistema-operativo/06-framework-escalado.md) · [07 diagnóstico](13-sistema-operativo/07-framework-diagnostico.md) ·
[08 cuenta nueva y heredada](13-sistema-operativo/08-cuenta-nueva-y-heredada.md) · [09 presupuesto pequeño y grande](13-sistema-operativo/09-presupuesto-pequeno-y-grande.md) · [10 plantillas](13-sistema-operativo/10-plantillas.md)

### 14 · Playbooks por modelo de negocio
[Lead gen](14-playbooks/playbook-lead-gen.md) · [High-ticket](14-playbooks/playbook-high-ticket.md) · [Cursos e infoproductos](14-playbooks/playbook-cursos-infoproductos.md) ·
[Webinars, eventos, lanzamientos](14-playbooks/playbook-webinars-eventos-lanzamientos.md) · [Negocio local](14-playbooks/playbook-negocio-local.md) ·
[B2B](14-playbooks/playbook-b2b.md) · [SaaS](14-playbooks/playbook-saas.md) · [Agencias y consultores](14-playbooks/playbook-agencias-consultores.md) ·
**[Consultoras y agencias de IA y automatización](14-playbooks/playbook-consultoras-ia-automatizacion.md)** (el más completo: oferta de entrada que precualifica, economía con el coste de vender, Conversion Leads verificado, ejemplo Acme Automations) ·
[Ecommerce DTC](14-playbooks/playbook-ecommerce-dtc.md) · [Productos de consumo](14-playbooks/playbook-productos-consumo.md) ·
[Suscripciones](14-playbooks/playbook-suscripciones.md) · [Apps](14-playbooks/playbook-apps.md)

### 15 · Escenarios de validación — [README](15-escenarios-validacion/README.md)
[Casos A–E](15-escenarios-validacion/01-casos-A-E.md) (curso 2.000 € con 100 €/día, ecommerce 500 €/día, clínica dental 50 €/día, SaaS B2B, webinar) ·
[Casos F–J](15-escenarios-validacion/02-casos-F-J.md) (escalar 5.000 €/día, leads basura, CTR alto CPA malo, ROAS bueno con pérdidas, tracking roto) ·
[Autoevaluación](15-escenarios-validacion/03-autoevaluacion.md)

### 16 · Aprendizajes propios — [README](16-aprendizajes-propios/README.md)
Aprendizajes de cuentas reales ya verificados e incorporados al producto. Los tuyos viven en `aprendizajes/`, fuera de la KB, para que no se pierdan al actualizar.

### Fuentes
[Ledger maestro](fuentes/00-SOURCE-LEDGER-MAESTRO.md) y 12 ledgers por área en [fuentes/](fuentes/).

## Mantenimiento

- Mensual: revisar [10/10-como-vigilar-cambios](10-cambios-2025-2026-api-ia-automatizacion/10-como-vigilar-cambios.md),
  actualizar [00-ESTADO-ACTUAL-2026](00-ESTADO-ACTUAL-2026.md) y el changelog.
- Trimestral: tras los resultados de Meta, actualizar área 01 (modelos y precios) y 11 (benchmarks).
- Cada nueva fuente → ledger del área. Cada contradicción nueva → 12/02 o 12/04.
