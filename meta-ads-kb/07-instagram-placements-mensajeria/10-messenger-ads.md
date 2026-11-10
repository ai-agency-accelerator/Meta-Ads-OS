# Messenger en 2026: click-to-Messenger, lead ads en Messenger, marketing messages y automatización

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: qué queda de Messenger como canal publicitario en 2026, cómo funcionan los anuncios click-to-Messenger y los Messenger lead ads con chat automatizado, marketing messages de pago (sustituto de recurring notifications), optimizaciones disponibles, medición y cuándo elegir Messenger frente a WhatsApp/Instagram.

## TL;DR

- **Messenger ya no es una superficie de inventario relevante; es un destino conversacional.** Sponsored messages (desactivado jun-2024), Messenger inbox (retirado 11-nov-2025) y Messenger Stories (27-ago-2026) han desaparecido como placements. [OFFICIAL META] (sponsored messages) + [STRONG INFERENCE] (fechas de inbox y Stories)
- **Click-to-Messenger (CTM) sigue plenamente vigente**: objetivos Traffic, Engagement, Sales y Leads; goals de conversaciones, leads (`LEAD_GENERATION`, `QUALITY_LEAD` con fuente de CRM), compras vía CAPI y **optimización a valor anunciada en jul-2025**. [OFFICIAL META]
- **Messenger lead ads (chat automatizado)**: formulario conversacional con preguntas, validación de respuestas, ramificación y preguntas **descalificadoras**; se crea en Ads Manager (la creación vía API se depreca desde v24). [OFFICIAL META] ([docs CTM](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-messenger))
- **Recurring notifications terminaron el 10-feb-2026**; las sustituye la **Marketing Messages API for Messenger** (de pago por mensaje, solo vía tech providers con App Review, en una lista de países; no se puede enviar a suscriptores de UE, UK, Japón, Corea del Sur ni Australia). Cooldown de envío 1 cada 48 h por suscriptor. [OFFICIAL META] ([docs](https://developers.facebook.com/documentation/business-messaging/messenger-platform/marketing-messages-on-messenger), [SMT](https://www.socialmediatoday.com/news/metas-recurring-marketing-messages-api-will-end-this-week/811668/))
- **Click-to-subscribe**: anuncio CTM que invita a suscribirse a marketing messages (máx. 1 al día a quien acepta). Útil para crear lista de remarketing en Messenger fuera de la UE. [OFFICIAL META]
- **Señal estratégica**: Meta cerró las apps de escritorio de Messenger (oct-2025) y messenger.com (abr-2026, redirige a facebook.com/messages). Messenger se integra en Facebook; su peso relativo frente a WhatsApp/IG Direct baja. [OFFICIAL META] vía [TechCrunch](https://www.techcrunch.com/2026/02/19/meta-is-shutting-down-messengers-standalone-website/)
- **Elegir destino por penetración local de la app**: Messenger sigue siendo fuerte en Filipinas, partes de LatAm y EE. UU. para públicos de Facebook; WhatsApp domina en la mayoría de mercados (España incluida). El **multi-destino** reduce el coste mediano por mensaje ~9,5 % vs solo WhatsApp (test Meta H2-2024, 734K empresas, citado por terceros). [STRONG INFERENCE]

## 1. Qué ha cambiado (2024–2026)

| Fecha | Cambio | Evidencia |
|---|---|---|
| 1-jun-2024 | Desactivación de campañas de sponsored messages; fuera de API desde v20 | [OFFICIAL META] (vía [Loomer](https://www.jonloomer.com/qvt/meta-to-deprecate-sponsored-messages/)) |
| jun-2024 | CAPI for Business Messaging disponible (incl. Messenger) | [OFFICIAL META] |
| 1-jul-2025 | Conversations 2025: optimización a compras y leads en click-to-message; **value optimization para CTM**; destino automático según app preferida; llamadas en Messenger (test: ver si la llamada viene de un anuncio, resúmenes IA) | [OFFICIAL META] vía [SMT](https://www.socialmediatoday.com/news/meta-announces-business-messaging-updates-conversations-2025-whatsapp/752250/) |
| oct-2025 | Cierre de apps de escritorio de Messenger | [OFFICIAL META] |
| 20-oct-2025 | Business AI en Messenger (Filipinas; también México) | [STRONG INFERENCE] ([CNBC](https://www.cnbc.com/amp/2025/10/02/meta-wants-to-bring-its-business-ai-chat-tools-to-third-party-websites.html), Marketech APAC) |
| 11-nov-2025 | Placement Messenger inbox retirado | [STRONG INFERENCE] |
| 10-feb-2026 | Fin de recurring notifications → Marketing Messages API for Messenger | [OFFICIAL META] |
| abr-2026 | messenger.com cierra | [OFFICIAL META] |
| 3-jun-2026 | Meta Business Agent disponible también en Messenger | [OFFICIAL META] |
| 27-ago-2026 | Placement Messenger Stories retirado (API todas las versiones 27-oct-2026) | [STRONG INFERENCE] |

## 2. Click-to-Messenger: configuración

| Elemento | Opciones | Notas |
|---|---|---|
| Objetivo | Traffic, Engagement, Sales, Leads | API: OUTCOME_TRAFFIC/ENGAGEMENT/SALES/LEADS |
| Goal | Conversations; Leads (LEAD_GENERATION) o **QUALITY_LEAD** (con `pixel_id` de fuente CRM); compras/valor con CAPI | Value optimization para CTM (jul-2025) |
| Mensaje inicial | Greeting (≤300 caracteres, `{{user_first_name}}`), ice breakers (título ≤80, respuesta ≤300), hasta 5 plantillas, call prompt | Plantillas no editables tras crearse |
| Automatización | App partner (ManyChat, Chatfuel, BSP) vía handover; Business Agent; respuestas automáticas de Business Suite | — |
| Placements | Los compatibles (no right column) | Meta filtra automáticamente |
| Requisitos | Usuario con Messenger instalado; anuncios con `object_story_id` no soportados en CTM | [OFFICIAL META] |

Fuente: [Click to Messenger (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-messenger) [OFFICIAL META].

## 3. Messenger lead ads (chat automatizado)

**Cómo funciona** [OFFICIAL META]:
- Plantilla con pasos: INTRO (bienvenida) → preguntas (respuesta libre, prefill de ciudad/email/teléfono, o quick replies) → CONFIRMATION → mensaje de descalificación.
- Validación de respuestas (ciudad, país, email, DNI/ID nacional, teléfono, código postal) y opción de saltar preguntas.
- Ramificación con `next_step_ids` según la respuesta (no puede volver a un paso anterior).
- **Preguntas descalificadoras** para priorizar leads.
- Requiere aceptar los términos de Messenger Ads for Leads y URL de privacidad.
- Se crea un `fblead_form` asociado: los leads se descargan/integran como los de instant forms.
- **API**: creación de estas plantillas en deprecación desde v24 → usar Ads Manager.

**Variantes relacionadas**:
- **Instant form → Messenger**: guías de terceros describen la opción de convertir un instant form en un flujo de chat de Messenger y que Meta entrega el formato preferido por cada usuario. [STRONG INFERENCE]
- **Leads con conversion location "Instant forms and Messenger"** como opción del objetivo Leads. [EMPIRICAL] (Loomer, lista de performance goals)

**Evidencia**: caso de Meta (broker Equiti): CTM vs formularios web → −27 % CPL y +36 % leads en A/B test. [OFFICIAL META, caso autoreportado] ([Trade Informer](https://www.tradeinformer.com/broker-news/equiti-sees-36-increase-in-leads-27-cost-reduction-using-meta-messenger-ads))

**Cuándo usar Messenger lead ads vs instant forms** [STRONG INFERENCE]:
- Messenger lead ads: cuando necesitas cualificar con 3–6 preguntas y descalificar, y tu público usa Messenger.
- Instant forms: volumen y simplicidad; menos contexto.
- El chat deja un hilo abierto: puedes seguir conversando (dentro de la ventana de 24 h) — ventaja frente al formulario.

## 4. Marketing messages en Messenger (re-engagement)

| Aspecto | Detalle | Evidencia |
|---|---|---|
| Qué es | Mensajes promocionales personalizados a suscriptores que hicieron opt-in | [OFFICIAL META] |
| Acceso | Solo tech providers con app aprobada (ads_management, pages_messaging, paid_marketing_messages/marketing_messages_messenger); solo web apps | [OFFICIAL META] |
| Países de empresas | AU, BR, CL, CO, HK, IN, ID, IL, MY, MX, NZ, PE, PH, SA, SG, TW, TH, AE, US, VN | [OFFICIAL META] |
| Suscriptores excluidos | UE, Japón, Corea del Sur, Australia, Reino Unido | [OFFICIAL META] |
| Precio | Integración gratis; Meta cobra por mensaje a la empresa (tarifas no publicadas en la página) | [OFFICIAL META] |
| Opt-in | Solo se puede pedir dentro de la ventana estándar; el opt-in no abre ventana; otros métodos: m.me, QR, plugin; también click-to-subscribe ads | [OFFICIAL META] |
| Frecuencia | Cooldown 1 envío/48 h por suscriptor (desde feb-2026); click-to-subscribe habla de "hasta 1 al día" | [OFFICIAL META] (fuentes de distinta fecha; usar el más restrictivo) |
| Caducidad del opt-in | ~6 meses según terceros | [HYPOTHESIS] |

**Implicación para España/UE**: no puedes enviar marketing messages de Messenger a suscriptores de la UE. Para re-engagement en España, la vía es WhatsApp (plantillas de marketing) o email/SMS. [OFFICIAL META]

## 5. Medición en Messenger

- **CAPI for Business Messaging (Messenger)**: `messaging_channel=messenger`, `page_id` + `page_scoped_user_id` (PSID), permiso `page_events`, un dataset por página. Eventos: LeadSubmitted, QualifiedLead, Purchase (con currency y value), etc. **Optimización a compras disponible** para CTM. Meta no deduplica: hazlo tú. [OFFICIAL META] ([docs](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging))
- **QUALITY_LEAD** en Messenger lead ads con `pixel_id` de CRM: optimiza a leads que tu CRM marca como cualificados (equivalente a "conversion leads"). [OFFICIAL META]
- Atribución estándar de clic (1 o 7 días). [STRONG INFERENCE]

## 6. Messenger vs WhatsApp vs Instagram Direct

| Criterio | Messenger | WhatsApp | Instagram Direct |
|---|---|---|---|
| Penetración en España | Baja-media | Muy alta | Alta (<35 años) |
| Optimización a compras | Sí (CAPI) | Sí (CAPI) | No (conversaciones/leads/web) |
| Lead ads conversacionales nativos | Sí (chat automatizado) | Leads optimization + Flows | Leads → Instagram |
| Re-engagement pagado | Marketing messages (no UE) | Plantillas de marketing (pago por mensaje; no a +1 EE. UU.) | No hay equivalente (ventana 24 h; human agent) |
| Coste de mensajería | Gratis en ventana; marketing messages de pago | Service messages de pago desde 1-oct-2026 (1.000 gratis/número/mes); gratis en FEP | Gratis |
| Identidad del usuario | PSID (Facebook) | Número de teléfono | IGSID |
| Mejor para | Públicos 35+ de Facebook, PH/LatAm/EE. UU. | Mercados WhatsApp-first, local, servicios, ventas | Marcas con audiencia IG, creadores |

[STRONG INFERENCE] (penetración) + [OFFICIAL META] (capacidades). Con **multi-destino**, Meta decide por usuario; útil si no sabes qué app prefiere tu público, a costa de operar 2–3 bandejas.

## Implicaciones operativas

- Quitar Messenger de las conversaciones de "placements"; tratarlo solo como destino.
- En mercados UE, Messenger no ofrece re-engagement pagado a suscriptores: construir lista en WhatsApp (opt-in) o email.
- Para lead gen con cualificación en Facebook (públicos 35+), probar Messenger lead ads con 1–2 preguntas descalificadoras frente a instant forms "higher intent".
- Si se usan apps partner, revisar el enrutamiento (handover) antes de lanzar.

## Errores frecuentes

- Seguir planificando sponsored messages o Messenger Stories.
- Lanzar CTM sin respuesta automática ni humana inmediata.
- Optimizar a "conversations" cuando hay CAPI disponible para leads/compras.
- Pedir opt-in a marketing messages fuera de la ventana de 24 h.
- Intentar crear Messenger lead ads por API en versiones ≥v24.

## Preguntas abiertas

- Tarifas por mensaje de Marketing Messages on Messenger (no publicadas en la doc consultada).
- Fecha y estado definitivos de la retirada de Messenger Stories en API (27-oct-2026).
- ¿Llegará a la UE algún mecanismo de marketing messages en Messenger?
- Ampliación de ventana para conversaciones desde anuncios en Messenger (no verificada).

## Fuentes clave

- [Click to Messenger ads (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-messenger) — vigente — meta-developers
- [Messaging ads overview (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads) — vigente — meta-developers
- [Marketing Messages on Messenger](https://developers.facebook.com/documentation/business-messaging/messenger-platform/marketing-messages-on-messenger) — vigente — meta-developers
- [Meta's Recurring Marketing Messages API will end this week](https://www.socialmediatoday.com/news/metas-recurring-marketing-messages-api-will-end-this-week/811668/) — 2026-02-08 — prensa
- [Conversions API for Business Messaging](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging) — vigente — meta-developers
- [Meta announces business messaging updates (Conversations 2025)](https://www.socialmediatoday.com/news/meta-announces-business-messaging-updates-conversations-2025-whatsapp/752250/) — 2025-07-02 — prensa
- [Meta to deprecate sponsored messages](https://www.jonloomer.com/qvt/meta-to-deprecate-sponsored-messages/) — 2024 — practitioner
- [Meta is shutting down Messenger's standalone website](https://www.techcrunch.com/2026/02/19/meta-is-shutting-down-messengers-standalone-website/) — 2026-02-19 — prensa
- [Equiti: Messenger ads case](https://www.tradeinformer.com/broker-news/equiti-sees-36-increase-in-leads-27-cost-reduction-using-meta-messenger-ads) — 2025 — prensa (caso Meta)
