# Autoevaluación — condición de finalización

> 2026-10-16 · Autor: agente principal · Respuesta honesta a cada pregunta de la condición de finalización del encargo,
> con el documento que lo respalda y lo que sigue débil.

| Pregunta | Respuesta | Dónde | Límite honesto |
|---|---|---|---|
| ¿Podría auditar profesionalmente una cuenta? | **Sí** | [13/02](../13-sistema-operativo/02-framework-auditoria.md), [13/08](../13-sistema-operativo/08-cuenta-nueva-y-heredada.md) | Sin acceso a una cuenta real no se ha probado el framework sobre datos vivos; algunos defaults (atribución, enhancements) solo se ven en la interfaz |
| ¿Podría diseñar campañas desde cero? | **Sí** | [13/03](../13-sistema-operativo/03-framework-lanzamiento.md), [14](../14-playbooks/) | — |
| ¿Podría elegir el evento correcto? | **Sí**, con el criterio "más cercano al dinero con volumen" | [02/02](../02-estructura-campanas/02-eventos-de-optimizacion.md) | El umbral exacto en que un evento profundo con poco volumen supera a un proxy con mucho no está publicado (requiere test propio) |
| ¿Podría diseñar tracking? | **Sí** (Shopify, WordPress, GTM/sGTM, custom, CRM, apps) | [04/02](../04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md)–[04/08](../04-tracking-atribucion-medicion/08-eventos-offline-y-crm.md), [04/16](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md) | Qué envía exactamente el nivel "Maximum" de Shopify y la CAPI de un clic no está documentado por Meta |
| ¿Entiendo Pixel + CAPI? | **Sí** (dedup, matching, EMQ, consentimiento, categorías sensibles) | [04/01](../04-tracking-atribucion-medicion/01-arquitectura-senales-pixel-capi-datasets.md), [04/03](../04-tracking-atribucion-medicion/03-emq-advanced-matching-pii-hashing.md), [04/09](../04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md) | Si Meta fusiona el `user_data` de eventos deduplicados no está documentado |
| ¿Entiendo por qué Meta atribuye una venta? | **Sí** (interacción elegible en ventana, último toque dentro de Meta, link click vs engage-through vs view, fecha de conversión) | [04/10](../04-tracking-atribucion-medicion/10-atribucion-ventanas-y-modelos.md), [04/12](../04-tracking-atribucion-medicion/12-attribution-lag.md) | Metodología de incremental attribution sin publicar |
| ¿Puedo explicar diferencias con GA4/CRM? | **Sí** | [04/11](../04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md) | — |
| ¿Puedo calcular unit economics? | **Sí**, con calculadora | [09/08](../09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md), [05/05](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md), [06/05](../06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md), `herramientas/economia.py` | Tasas de funnel por defecto son supuestos: siempre sustituir por datos del negocio |
| ¿Puedo evaluar creatividades? | **Sí** (taxonomía, métricas, qué predicen) | [03/02](../03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md), [03/07](../03-creatividad/07-analitica-creativa-metricas.md) | Peso de imagen/audio/texto en la representación de Meta, desconocido |
| ¿Puedo diseñar un sistema de testing? | **Sí** | [13/05](../13-sistema-operativo/05-framework-testing-creativo.md) | Testing "dentro vs fuera" de la campaña principal sigue [CONTESTED]: se decide por volumen |
| ¿Puedo detectar por qué sube un CPA? | **Sí** (descomposición CPM/CTR/CVR + árbol) | [13/07](../13-sistema-operativo/07-framework-diagnostico.md), [09/09](../09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md) | Anomalías de plataforma sin explicar (jul/sep-2026) |
| ¿Puedo separar un problema de ads de uno de funnel? | **Sí** | [03/09](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md), [03/15](../03-creatividad/15-landing-pages-y-cro-trafico-meta.md) | — |
| ¿Puedo trabajar con e-commerce? | **Sí** | [06](../06-ecommerce-apps/README.md), [14/playbook-ecommerce-dtc](../14-playbooks/playbook-ecommerce-dtc.md) | Faltan casos españoles con margen y nCAC completos |
| ¿Puedo trabajar con high-ticket? | **Sí** | [05/06](../05-leadgen-high-ticket-crm/06-high-ticket-funnels.md), [14/playbook-high-ticket](../14-playbooks/playbook-high-ticket.md) | Benchmarks de show/cierre sin metodología pública |
| ¿Puedo trabajar con lead gen? | **Sí** | [05](../05-leadgen-high-ticket-crm/README.md) | — |
| ¿Puedo trabajar con WhatsApp? | **Sí** (CTWA, Platform, precios, revenue, Business Agent) | [07/11](../07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md)–[07/14](../07-instagram-placements-mensajeria/14-funnels-de-mensajeria.md) | Ventana gratuita 72 h vs 7 días sin confirmar por Meta; benchmarks conversación→venta inexistentes |
| ¿Puedo trabajar con apps? | **Sí, nivel sólido pero menos profundo** | [06/09](../06-ecommerce-apps/09-apps-campanas-y-medicion.md), [04/15](../04-tracking-atribucion-medicion/15-apps-sdk-skan-mmp.md), [14/playbook-apps](../14-playbooks/playbook-apps.md) | Soporte de AdAttributionKit por Meta no confirmado |
| ¿Conozco las políticas? | **Sí** | [08](../08-cuenta-politicas-seguridad/README.md) | Umbrales internos de Meta (rechazos → restricción) no públicos; detalle de verificación financiera en España |
| ¿Conozco los cambios actuales de 2026? | **Sí, a 16-oct-2026** | [00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md), [10/02](../10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md) | Caduca: Q3-2026 earnings (finales de oct), condiciones del 30-oct, retiradas de v26 (27-oct) |
| ¿Sé qué consejos antiguos ignorar? | **Sí** | [12/01](../12-mitos-contradicciones/01-mitos-meta-ads-2026.md), [12/03](../12-mitos-contradicciones/03-folklore-obsoleto-por-era.md), [00-ESTADO §7](../00-ESTADO-ACTUAL-2026.md) | — |
| ¿Sé cuáles de mis conclusiones son hechos y cuáles inferencias? | **Sí**: etiquetas en cada archivo y revisión adversarial | [00-CONVENCIONES](../00-CONVENCIONES.md), [12/05](../12-mitos-contradicciones/05-revision-adversarial-kb.md) | Parte del Help Center solo se leyó vía fuentes secundarias en las áreas que no usaron el truco del user-agent (marcado en cada caso) |

## Lo que la investigación NO pudo hacer

- Probar nada en una cuenta real (por diseño: fase de solo investigación).
- Ver la interfaz de Ads Manager directamente: defaults como la atribución con engage-through o las mejoras de IA activadas
  se conocen por terceros y deben verificarse en la primera cuenta que se audite.
- Obtener datos controlados públicos sobre subidas de presupuesto, curvas de rendimientos decrecientes por vertical o
  efecto de las mejoras de IA de Meta: no existen públicamente.
