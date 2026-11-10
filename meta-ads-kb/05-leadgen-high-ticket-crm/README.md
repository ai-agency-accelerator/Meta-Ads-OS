# Área 05 — Lead generation, high-ticket, funnels de venta y CRM

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: captación de leads en Meta para servicios, formaciones, high-ticket, B2B, SaaS y negocio local; calidad de lead, qualified leads (antes conversion leads), Conversions API for CRM, integraciones, economía del funnel hasta cash, speed to lead, show rate y feedback loop de ventas. Ledger: `../fuentes/ledger-05-leadgen-high-ticket-crm.md` (96 fuentes, S05-001 a S05-096).

## Índice

| Archivo | Para qué sirve |
|---|---|
| [01-canales-captacion-comparativa.md](01-canales-captacion-comparativa.md) | Elegir canal: instant form, web, Messenger, IG DM, WhatsApp, llamadas, booking; cómo optimiza Meta en cada uno |
| [02-instant-forms-a-fondo.md](02-instant-forms-a-fondo.md) | Tipos de formulario, preguntas (qué sí / qué no), filtros (SMS, work email), spam, booking embebido |
| [03-calidad-de-lead-y-conversion-leads.md](03-calidad-de-lead-y-conversion-leads.md) | Qualified leads, requisitos CAPI CRM, qué etapa optimizar según volumen, mensajería, Sequenced Events |
| [04-integraciones-crm.md](04-integraciones-crm.md) | HubSpot, GHL, Salesforce, Zapier, Make, Pipedrive, Zoho, Kommo…: qué soportan y arquitectura |
| [05-economia-funnel-lead-gen-calculadoras.md](05-economia-funnel-lead-gen-calculadoras.md) | Fórmulas y ejemplos: ¿cuánto puedo pagar por lead / llamada / venta? |
| [`herramientas/economia.py`](../../herramientas/economia.py) | Calculadora ejecutable (Python, sin dependencias) usada en los ejemplos: modos `leadgen` y `prevision` |
| [06-high-ticket-funnels.md](06-high-ticket-funnels.md) | VSL + aplicación + calendario, setter/closer, DM setting, tripwire, challenge; benchmarks con fuente |
| [07-webinars-eventos-lanzamientos.md](07-webinars-eventos-lanzamientos.md) | Fases, presupuesto por fase, medir registro → asistencia → venta |
| [08-speed-to-lead-calendarios-show-rate.md](08-speed-to-lead-calendarios-show-rate.md) | Evidencia (MIT 2007, HBR 2011…), diseño de booking y recordatorios, valor del show rate |
| [09-sales-feedback-loop.md](09-sales-feedback-loop.md) | Campos de CRM, parámetros dinámicos, informes por anuncio hasta cash, rituales |
| [10-b2b-saas-local.md](10-b2b-saas-local.md) | B2B vs LinkedIn, SaaS (trial/demo), negocio local (geo, llamadas, WhatsApp), agencias |

Playbooks en `../14-playbooks/`: [lead gen](../14-playbooks/playbook-lead-gen.md) · [high-ticket](../14-playbooks/playbook-high-ticket.md) · [cursos e infoproductos](../14-playbooks/playbook-cursos-infoproductos.md) · [webinars/eventos/lanzamientos](../14-playbooks/playbook-webinars-eventos-lanzamientos.md) · [negocio local](../14-playbooks/playbook-negocio-local.md) · [B2B](../14-playbooks/playbook-b2b.md) · [SaaS](../14-playbooks/playbook-saas.md) · [agencias y consultores](../14-playbooks/playbook-agencias-consultores.md).

## TL;DR del área

1. **Juzga por coste por venta y cash, no por CPL.** CPL y calidad pueden moverse en direcciones opuestas; la fórmula maestra es `CPL máximo = contribución por venta × P(venta | lead)`. **[STRONG INFERENCE]**
2. **El objetivo se llama ahora "Maximize number of qualified leads"** (antes conversion leads) y **desde abril de 2026 no se puede crear en campañas nuevas sin integración CAPI** (existentes afectadas desde agosto de 2026). **[OFFICIAL META]**
3. **Integración CAPI for CRM:** lead ID guardado, envío ≥ diario, etapa objetivo en ≤28 días y con 1-40% de conversión, ≥2-3 etapas, cobertura ≥60%, learning 2-4 semanas. El "mínimo de 200 leads/mes" **ya no es requisito**: Meta anunció su eliminación el 30-oct-2025; la guía de developers lo sigue listando como criterio de "buen encaje" (documentación desfasada). Con poco volumen el aprendizaje sigue siendo pobre. **[OFFICIAL META]**
4. **Optimiza a la etapa más profunda con volumen** (≈50/semana): en high-ticket suele ser "cualificado" o "agendado", casi nunca la venta. **[STRONG INFERENCE]**
5. **Qualified leads ya admite formularios web**, y en ago-oct 2026 se despliega **Sequenced Events** (`Lead → Schedule`, crédito solo si ocurren en orden) sin documentación oficial. **[OFFICIAL META]** / **[EMPIRICAL]**
6. **Instant form por defecto para servicios: Higher intent + SMS verification + 3-5 preguntas de opción múltiple + intro honesta + reserva/WhatsApp al final.** Prohibido preguntar ingresos/patrimonio/salud. **[OFFICIAL META]** + **[STRONG INFERENCE]**
7. **Reserva embebida en instant forms (Calendly, LeadConnector/HighLevel; HubSpot anunciado), lanzada el 24-06-2026, solo embebida en la app móvil de Facebook,** despliegue global previsto en oct-nov 2026: la mayor palanca nueva contra la caída de interés y el no-show. **Los datos de reserva no se reportan en Ads Manager**: devuélvelos tú vía CAPI CRM si quieres que Meta aprenda de ellos. **[OFFICIAL META]** (S05-095)
8. **Speed to lead:** 5 vs 30 min → ×100 contacto y ×21 cualificación (MIT/InsideSales 2007, no mide cierre); HBR 2011: solo 37% responde en <1 h. No hay estudio independiente 2025-2026 que lo actualice. **[EMPIRICAL]**
9. **El show rate y el cierre pesan linealmente en lo que puedes pagar:** pasar de 50% a 80% de show sube el CPL pagable un 60%. Arreglar ventas suele valer más que bajar el CPL. **[STRONG INFERENCE]**
10. **Las exclusiones de placement por ad set desaparecen en Leads/Sales** (avisos desde 19-20-ago-2026; guía de alternativas 12-oct-2026): solo quedan exclusiones a nivel de cuenta y value rules. Evalúa placements por coste por cita antes de bloquear. **[OFFICIAL META]** + **[EMPIRICAL]**
11. **Mensajería en la UE tiene huecos:** métricas/campañas de mensajería y detección automática de eventos de WhatsApp no disponibles en Europa; la optimización por eventos downstream vía CAPI de mensajería solo existe para compras en Messenger/WhatsApp. **[OFFICIAL META]**
12. **Benchmarks de high-ticket (show 60-85%, cierre 15-40%, 150-350 $ por llamada agendada) vienen de agencias sin metodología pública.** Mide los tuyos el primer mes. **[EMPIRICAL]** débil

## Cronología de cambios 2025-2026 relevantes para el área

| Fecha | Cambio | Fuente | Etiqueta |
|---|---|---|---|
| 14-01-2025 | "Financial products and services" sustituye a Credit como categoría especial (EE. UU.) | S05-080 | [OFFICIAL META] vía secundaria |
| Mar 2025 | Caso oficial Braip: CTWA optimizado a leads (+45% leads cualificados) | S05-053 | [OFFICIAL META] |
| Abr 2025 | Vistas en cuentas: desactivar autofill, SMS verification, flexible form delivery, chat por Messenger/WhatsApp tras formulario, fuentes de datos CRM/Calls/Messages | S05-031 | [EMPIRICAL] |
| May 2025 | Retirada de la Offline Conversions API (Graph v16); todo por CAPI | S05-052 | [OFFICIAL META] vía secundarias |
| 2025 (inicio) | Configuración Advantage+ por defecto en Leads/Sales/App | S05-066, S05-067 | [OFFICIAL META] |
| Oct 2025 | Make: Lead ID ya no obligatorio si se envía email | S05-030 | [EMPIRICAL] |
| 30-10-2025 | Advantage+ leads global (−14% CPL, −10% coste por lead cualificado, autorreportado); campañas híbridas web+IF; optimizar a un único evento CRM; "eliminado el mínimo mensual de leads"; Zapier 100.000 eventos gratis; Salesforce Sales Cloud directo; SMS, work email; agente de nurturing en test | S05-005 | [OFFICIAL META] |
| Dic 2025 | Guía de integración CAPI CRM (fecha del buscador) sigue listando ≥200 leads/mes | S05-001 | [OFFICIAL META] |
| 27-02-2026 | App de Make para CAPI CRM gratis hasta feb-2028 | S05-030 | [EMPIRICAL] |
| Mar 2026 | Meta redefine clic en atribución web (solo link clicks; engage-through) — ver área 04 | S04-003 | [OFFICIAL META] |
| Abr 2026 | Qualified leads deja de estar disponible en campañas nuevas sin integración CAPI | S05-007 | [OFFICIAL META] |
| 15-04-2026 | Guía Salesforce Webhooks (partner, sin código) | S05-003 | [OFFICIAL META] |
| 01-06-2026 | Kommo: CAPI solo en plan Pro | S05-068 | [EMPIRICAL] |
| 24-06-2026 | Reserva de citas embebida en lead ads (Calendly, HighLevel) | S05-059, S05-062 | [OFFICIAL META] vía prensa |
| Ago 2026 | Qualified leads afecta a campañas existentes sin CAPI; test de Sequenced Events y Preferred lead answers en instant forms | S05-007, S05-033 | [OFFICIAL META] / [EMPIRICAL] |
| 19/20-08-2026 | Avisos de retirada de exclusiones de placement por ad set (Sales/Leads, test) | S05-049, S05-064 | [EMPIRICAL] |
| 25-08-2026 | Test "Reply to keywords" en anuncios de Instagram (comentario → DM) | S05-049 | [EMPIRICAL] |
| 28-09-2026 | Ventana gratuita de mensajes tras click-to-message hasta 7 días | S05-022, S05-049 | [OFFICIAL META] |
| 01-10-2026 | Service messages de WhatsApp facturables por mensaje (doc oficial: sin tiers ni franquicia; los "1.000 gratis/mes por número" solo los citan BSPs) | S05-049 | [OFFICIAL META] (cobro) / [CONTESTED] (franquicia) |
| Oct 2026 | Qualified leads + Sequenced Events en conversion location Website, en despliegue; guía de Meta sobre alternativas a exclusiones de placement (12-10) | S05-034, S05-065 | [EMPIRICAL] / [OFFICIAL META] |

## Contradicciones y puntos para contrastar con otras áreas

- **Mínimo de 200 leads/mes** (guía de desarrolladores, GHL dice 250) vs "eliminado el requisito" (anuncio oficial oct-2025). → Área 10 (cambios) y 01 (learning).
- **"Meta source + Leads with WhatsApp conversations"** como vía de qualified leads sin CRM vs la regla de abril 2026 (qualified leads solo con CAPI) — ambas en la misma página oficial. → Área 07 (mensajería) y 10.
- **Instant form vs landing:** test de Loomer (misma calidad, mitad de coste por lead de calidad) vs agencias (cierre 2-8× peor en formularios). [CONTESTED]. → Área 11 (benchmarks/casos) y 12 (mitos).
- **Higher intent "−20-40% de volumen, +contacto"**: cifras sin fuente que circulan como hechos. → Área 12 (mitos).
- **Audience Network como fuente de leads basura:** afirmado por agencias/vendors antifraude, no reconocido por Meta; ahora sin exclusión por ad set. → Área 07 (placements) y 08.
- **"Allow limited spending to excluded placements" (hasta 5%)**: un vendor dice "5% por cada placement excluido desde oct-2025". → Área 07/02.
- **Preguntas de presupuesto/capacidad de inversión** en formularios vs prohibición de "información financiera". → Área 08 (políticas).
- **Atribución:** el cambio de clic de marzo de 2026 altera la comparación de resultados web de lead gen antes/después. → Área 04.
- **HubSpot nativo**: KB dice que sirve para conversion leads; comunidad dice que no envía lead ID y Meta lo marca incompleto. → Área 04.
- **Fechas de despliegue de la reserva embebida:** octubre (SMT) vs noviembre (agregador de nota de prensa). → Área 10.

## Preguntas abiertas del área

1. ¿Existe todavía un umbral efectivo de volumen para qualified leads tras oct-2025? ¿Y para Sequenced Events (~30 eventos/7 días reportados)?
2. ~~¿La reserva embebida envía algún evento a Meta?~~ Resuelto a 2026-10-16: no se reporta en Ads Manager (S05-095). Abierto: si Meta lo añadirá y si el booking embebido mejora show/cierre medibles.
3. Efecto cuantificado de Higher intent, autofill desactivado y Preferred lead answers (Meta no publica cifras).
4. Disponibilidad real en España/UE de "Maximize leads through messaging", "Meta source + WhatsApp conversations" y métricas de mensajería.
5. Benchmarks con metodología de show/cierre high-ticket, impagos de planes de pago y reembolsos en infoproductos en España.
6. Estudio independiente reciente sobre speed to lead en leads de redes sociales y en mercados WhatsApp-first.
7. Impacto de la retirada de exclusiones de placement en la calidad media de leads.
8. Opción "Calls" como fuente de datos de qualified leads y optimización de llamadas largas en 2026.

## Notas de método

- Help Center de Meta leído en inglés (locale en_US) el 2026-10-15/16; las páginas cambian sin fecha visible → re-verificar antes de decisiones críticas.
- Reddit bloqueó el acceso (403) y no se pudo leer de primera mano; las referencias a "comunidad" vienen de fuentes secundarias y están marcadas con confianza baja.
- Los benchmarks de agencias/vendors se incluyen como contraste, nunca como objetivo, y llevan su etiqueta de confianza en el ledger.

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Mínimo de 200 leads/mes: se resuelve a favor del anuncio oficial más reciente (Meta for Business, 30-oct-2025: "removing the minimum monthly lead volume requirement"). La guía de developers es anterior en contenido y no se ha actualizado.
- Service messages de WhatsApp: la franquicia de 1.000 no aparece en la doc oficial ("Volume tiers: None"); FEP oficial de 72 h a 16-oct-2026.
