# Funnels de mensajería para lead gen y ventas: anuncio → DM/WhatsApp → cualificación → cita → venta

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: diseño, operación y medición de funnels conversacionales (Instagram Direct, WhatsApp, Messenger) para negocio local, servicios y high-ticket, y variantes para ecommerce. Integra lo de los archivos 05, 10, 11, 12 y 13 en un sistema operativo con métricas.

## TL;DR

- **El funnel conversacional gana cuando la venta necesita conversación** (precio variable, dudas, confianza, cita) y pierde cuando el producto se compra solo con una landing. [STRONG INFERENCE]
- **La métrica que importa no es el coste por conversación sino el coste por lead cualificado, por cita asistida y por venta.** Optimizar a conversaciones atrae "gente que chatea"; optimizar a leads/compras o enviar eventos de cualificación por CAPI mejora la calidad (Meta: −24 % CPL con lead optimization; caso IG DM: −35 % coste por lead cualificado). [OFFICIAL META] + [EMPIRICAL]
- **Velocidad de respuesta = conversión.** Evidencia clásica (HBR 2011, leads web): contactar en <1 h multiplicaba ~7x la probabilidad de cualificar frente a hacerlo una hora más tarde. En WhatsApp, además, responder en ≤24 h es condición para la ventana gratuita. Primera respuesta automática en segundos; humano en minutos para los cualificados. [EMPIRICAL] (antiguo, no específico de mensajería) + [OFFICIAL META] (FEP)
- **Arquitectura mínima**: anuncio de mensaje con promesa clara → primer mensaje automático con 1 pregunta y botones → 2–4 preguntas de cualificación (o WhatsApp Flow) → bifurcación (agenda / humano / nurturing) → CRM con origen del anuncio → eventos CAPI por etapa → informe por anuncio. [STRONG INFERENCE]
- **Elección de canal**: WhatsApp en mercados WhatsApp-first (España, LatAm) y servicios locales; Instagram Direct cuando la audiencia y la prueba social viven en IG (creadores, estética, formación, moda); Messenger para públicos 35+ de Facebook en mercados donde aún se usa; multi-destino si no sabes. [STRONG INFERENCE]
- **No hay benchmarks públicos fiables de conversación→venta.** Construye los tuyos con al menos 4 semanas de datos y 100+ conversaciones por variante antes de concluir. [STRONG INFERENCE]
- **2026 cambia la economía**: service messages de WhatsApp de pago (desde 1-oct-2026, 1.000 gratis/número/mes), FEP de CTWA hasta 7 días, Business Agent por tokens, Reply to Keywords en IG, Lead Capture AI agent en formularios, booking embebido en lead ads (jun-2026). [OFFICIAL META]/[STRONG INFERENCE]

## 1. Cuándo usar un funnel de mensajería (y cuándo no)

| Señal | Mensajería | Formulario (instant form) | Web/landing |
|---|---|---|---|
| Precio depende del caso (presupuesto, diagnóstico) | ✅ | ⚠️ | ⚠️ |
| Necesidad de confianza/relación (salud estética, formación, inmobiliaria, reformas) | ✅ | ⚠️ | ⚠️ |
| Producto estándar con precio claro y checkout fácil | ❌ | ❌ | ✅ |
| Volumen alto, coste mínimo por lead, cualificación posterior por teléfono | ⚠️ | ✅ | ⚠️ |
| Equipo capaz de responder en minutos (o IA/bot) | Requisito | Recomendable | — |
| Audiencia joven en IG | IG Direct | IG instant forms | — |
| España/LatAm, negocio local | WhatsApp | — | — |

[STRONG INFERENCE]. Alternativas 2026 que compiten con el chat: instant forms con **Lead Capture AI agent** (jul-2026) y **booking embebido en la pantalla de gracias** (24-jun-2026, Calendly/HighLevel; en Instagram muestra botón "Book time"). [EMPIRICAL]/[STRONG INFERENCE] (ver área 05).

## 2. Arquitectura del funnel (plantilla)

```
[Anuncio CTM/CTWA/IG Direct o comment-to-DM]
   promesa concreta + CTA de mensaje + mensaje prellenado con código de campaña
        │
[Mensaje 1 automático, <10 s]  confirma + entrega valor + 1 pregunta con botones
        │ (si no responde en X h → 1 recordatorio dentro de la ventana)
[Cualificación 2–4 preguntas o WhatsApp Flow]  necesidad · plazo · presupuesto/rango · ubicación
        │
   ┌────┴─────────────┬──────────────────────┐
[Cualificado]     [Dudoso]              [No cualificado]
 agenda (link/Flow)  humano en <15 min     recurso + despedida (sin spam)
 o llamada            (setter)
        │
[Cita confirmada] → recordatorios (utility; ojo coste desde oct-2026) → [Asiste] → [Venta]
        │
CRM: contacto + source_id/ctwa_clid/ig_sid/PSID + etapa + importe
CAPI BM: LeadSubmitted → QualifiedLead → (Schedule no soportado; usar QualifiedLead/evento propio en web) → Purchase{value}
```

[OFFICIAL META] (campos y eventos CAPI) + [STRONG INFERENCE] (diseño). Nota: el endpoint de mensajería no admite `Schedule`; si la cita se reserva en web, usa CAPI web para el evento de cita. [STRONG INFERENCE]

## 3. Variantes por tipo de negocio

### 3.1 Negocio local (clínica estética no médica, peluquería, taller, gimnasio, restaurante)
- **Canal**: WhatsApp (CTWA) + Status ads si disponibles (segmentación por ciudad).
- **Oferta**: precio de entrada o diagnóstico gratis; disponibilidad ("huecos esta semana").
- **Cualificación**: zona, servicio, cuándo.
- **Cierre**: reserva en el chat (Flow o link) + recordatorio 24 h antes.
- **Clave**: velocidad y agenda visible. Business Agent puede cubrir FAQs (fuera de verticales sanitarios).

### 3.2 Servicios profesionales (abogados, asesorías, reformas, inmobiliaria)
- **Canal**: WhatsApp o Messenger lead ads (con preguntas descalificadoras) o IG Direct según audiencia.
- **Cualificación**: tipo de caso, urgencia, presupuesto, ubicación; descalificar fuera de zona/servicio.
- **Cierre**: llamada o visita con humano; propuesta.
- **Clave**: QualifiedLead por CAPI para enseñar al algoritmo qué es un buen lead.

### 3.3 High-ticket (formación, mentoring, servicios >1.000 €)
- **Canal**: Instagram (Reels + comment-to-DM + click-to-Direct) o WhatsApp.
- **Flujo**: contenido de valor → keyword → recurso → 3–4 preguntas (situación, objetivo, inversión disponible, urgencia) → **setter** humano → llamada de venta.
- **Clave**: separar curiosos de compradores antes de la llamada; medir **coste por llamada cualificada asistida** y **cash collected**; enviar Purchase con valor real (y, si hay pagos fraccionados, decidir si envías el primer cobro o el contrato total — consistencia > perfección).
- **Riesgo**: claims de ingresos/resultados (políticas de Meta; área 08).

### 3.4 Ecommerce con consulta (moda a medida, muebles, joyería, electrónica)
- **Canal**: CTWA con catálogo o IG Direct; Business Agent para recomendaciones de catálogo.
- **Optimización**: compras (CTWA/CTM con CAPI) si la venta cierra en chat; si cierra en web, conversión web con el clic del anuncio.
- **Clave**: carritos/links de pago en el chat; Purchase con valor.

## 4. Métricas y fórmulas

| Etapa | Métrica | Fórmula | Dónde |
|---|---|---|---|
| Anuncio | CPM, CTR, coste por conversación iniciada | gasto / conversaciones | Ads Manager |
| Apertura | **Tasa de respuesta al mensaje 1** | usuarios que responden / conversaciones | BSP/CRM |
| Cualificación | **% cualificados** | cualificados / conversaciones | CRM |
| | Coste por lead cualificado (CPQL) | gasto / cualificados | CRM + Ads |
| Agenda | % cita | citas / cualificados | CRM |
| | Show rate | asistidas / citas | CRM |
| Venta | % cierre | ventas / asistidas | CRM |
| | CAC | gasto (+ coste de mensajes, IA y equipo) / ventas | Finanzas |
| | ROAS de caja | ingresos cobrados / gasto | Finanzas |
| Operación | Tiempo a primera respuesta (mediana, p90) | — | BSP |
| | Coste de mensajería por venta | (service + utility + marketing + tokens) / ventas | Facturas Meta/BSP |

**Ejemplo ilustrativo (cifras inventadas para enseñar la mecánica, no benchmark)**: 3.000 € → 600 conversaciones (5 €/conv.) → 60 % responden (360) → 35 % cualificados (126; CPQL 23,8 €) → 50 % cita (63) → 75 % asisten (47) → 30 % cierran (14) → CAC de medios 214 €. Si el ticket es 1.500 € con 60 % de margen, rentable; si optimizar a leads sube el coste por conversación a 6 € pero el % cualificados a 50 %, el CPQL baja a 20 €. [HYPOTHESIS] (ejemplo)

**Lectura correcta**: un coste por conversación más alto puede ser mejor si sube la cualificación (caso real IG DM de Spur: coste por chat +9 %, cualificados 22 %→37 %, CPQL −35 %). [EMPIRICAL, n=1]

## 5. Diagnóstico rápido

| Síntoma | Causa probable | Acción |
|---|---|---|
| Muchas conversaciones, pocas respuestas al mensaje 1 | Anuncio genera clics curiosos; mensaje 1 pobre | Promesa más concreta; botones; revisar placement (AN/overlays) |
| Responden pero no cualifican | Segmentación/creatividad atrae público equivocado; oferta "gratis" | Optimizar a leads/CAPI QualifiedLead; filtrar en el copy ("desde X €") |
| Cualifican pero no agendan | Fricción de agenda; respuesta lenta del humano | Agenda dentro del chat; SLA <15 min |
| Agendan pero no asisten | Falta de compromiso/recordatorios | Recordatorios 24 h y 2 h; señal/depósito |
| Asisten y no compran | Venta/oferta/precio | Formación comercial; no es problema de anuncios |
| CPQL sube tras escalar | Saturación de audiencia/creatividad | Nuevos conceptos; creadores/partnership ads |
| Volumen cae en fines de semana/noche | Sin cobertura | IA/bot de primera respuesta |

[STRONG INFERENCE]

## 6. Medición y atribución del funnel

1. **Identificar el origen** en el primer mensaje: `referral.source_id` y `ctwa_clid` (WhatsApp; no existe `ctwa_clid` para Status ads), PSID (Messenger), IGSID (Instagram). Si usas la app sin API, mensaje prellenado con código de campaña. [OFFICIAL META]
2. **CRM con etapas** y fecha/importe.
3. **CAPI for Business Messaging** por etapa (LeadSubmitted, QualifiedLead, Purchase). Meta no deduplica. [OFFICIAL META]
4. **Optimización**: WhatsApp/Messenger → compras con CAPI; Instagram → leads/conversaciones (sin optimización a compra). Messenger lead ads → QUALITY_LEAD con fuente CRM. [OFFICIAL META]
5. **Informe semanal por anuncio**: CPQL, coste por cita, coste por venta; no por conversación.
6. **Incrementalidad**: lift test o geo test cuando el gasto lo justifique (área 04).

## 7. Operación: personas, SLAs y guiones

- **Roles**: bot/IA (primer contacto 24/7), setter (cualifica y agenda), closer (vende), responsable de CRM/datos.
- **SLAs** [HYPOTHESIS]: primera respuesta automática <10 s; humano para cualificados <15 min en horario; seguimiento dentro de la ventana de 24 h (o FEP).
- **Guiones**: preguntas cerradas con botones; nunca más de 2 mensajes seguidos sin pregunta; recapitular antes de agendar.
- **Cumplimiento**: consentimiento para mensajes de marketing posteriores (WhatsApp opt-in); no enviar promociones fuera de ventana en Instagram/Messenger; datos sensibles fuera del chat (salud).
- **Costes 2026**: en WhatsApp con API, cada mensaje de servicio fuera de FEP y por encima de 1.000/mes cuesta; diseñar flujos cortos y aprovechar la FEP para cualificar y agendar. [STRONG INFERENCE]

## Implicaciones operativas

- Antes de lanzar un funnel de mensajería: SLA, guion, CRM con origen, CAPI por etapa y responsable de bandeja. Sin estos cinco, no escalar presupuesto.
- Revisar semanalmente 20–30 conversaciones reales (calidad de leads, objeciones, errores del bot/IA).
- Decidir con datos entre chat, formulario con IA y formulario con booking embebido para cada oferta.

## Errores frecuentes

- Celebrar coste por conversación bajo.
- Bot que hace 10 preguntas antes de dar valor.
- Setter que responde al día siguiente (y en WhatsApp se pierde la FEP).
- No registrar el anuncio de origen → imposible saber qué creatividad vende.
- Enviar Purchase por cada pago parcial sin regla consistente (ROAS inflado).

## Preguntas abiertas

- Benchmarks públicos de conversación→venta por vertical (no existen; construir propios).
- Impacto real de la FEP de 7 días en tasas de cierre (esperable en ciclos de 3–7 días).
- Rendimiento comparado: chat humano vs Business Agent vs Lead Capture AI agent en servicios.

## Fuentes clave

- [Lead generation strategies for SMBs on WhatsApp](https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/) — 2025 — meta-oficial
- [Down-funnel optimizations on WhatsApp](https://whatsappbusiness.com/resources/resource-library/down-funnel-optimizations-whatsapp/) — 2025 — meta-oficial
- [Conversions API for Business Messaging](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging) — vigente — meta-developers
- [Click to Messenger ads (QUALITY_LEAD, lead templates)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-messenger) — vigente — meta-developers
- [Webhook referral object (WhatsApp)](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/text) — vigente — meta-developers
- [Click to WhatsApp Ads Benchmarks (incluye caso IG DM)](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks) — 2026-10 — vendor
- [How to improve Meta lead quality](https://respond.io/blog/how-to-improve-meta-lead-quality) — 2025–2026 — vendor
- [The Short Life of Online Sales Leads (HBR)](https://hbr.org/2011/03/the-short-life-of-online-sales-leads) — 2011-03 — academico/prensa
- [Lead Capture AI Agent for Instant Forms](https://www.jonloomer.com/lead-capture-ai-agent-instant-forms/) — 2026-07-09 — practitioner
- [Meta in-app appointment booking for lead ads](https://www.socialsamosa.com/news-2/meta-in-app-appointment-booking-facebook-lead-ads-12103721) — 2026-06 — prensa
