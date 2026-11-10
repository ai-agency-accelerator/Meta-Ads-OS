# Business AI, Meta Business Agent y agentes conversacionales (WhatsApp, Messenger, Instagram)

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A10 (agente) · Ámbito: evolución 2025-2026 de la IA de Meta para conversar
> con clientes, su relación con los anuncios click-to-message, precios, límites y cómo usarla. Contrastar con área 07
> (mensajería/placements) y área 05 (lead gen/CRM).

## TL;DR

- **De test a producto global en 12 meses**: Business AI en test (México/Filipinas, 2025) → 1 M conversaciones/semana
  (Q4-2025) → 10 M conversaciones/semana (Q1-2026) → **Meta Business Agent global** en WhatsApp y Messenger (3-jun-2026),
  >1 M de negocios usándolo cada semana, Instagram en despliegue (Q2-2026). **[OFFICIAL META]** (S10-018, S10-019, S10-020, S10-058)
- **Ya no es gratis**: desde **1-ago-2026** cada mensaje del Business Agent cuesta **$2 por 1 M de tokens** (~4–5 céntimos
  por mensaje con 20–25k tokens); desde **1-oct-2026** WhatsApp cobra también los **service messages** (respuestas
  no-plantilla, humanas o de IA de terceros) a tarifa utility/auth. Solo hay un cargo por mensaje. Los mensajes dentro de
  la ventana gratuita de 72 h de anuncios CTWA siguen sin coste de entrega. **[OFFICIAL META]** (S10-024, S10-023) **Corrección 2026-11-09**: la FEP de CTWA puede durar hasta 7 días, hay 1.000 service messages gratis por número y mes y los mensajes del Business Agent se cobran también dentro de la FEP (S10-118).
- **Business Agent Platform** (julio-2026): capa enterprise con controles, guardrails y medición; integraciones previstas
  con Shopify y Zendesk. **[OFFICIAL META]** (S10-020)
- **Verticales excluidas** del Business Agent (doc dev): finanzas, gobierno, salud, alcohol, juego, medicamentos OTC,
  servicios matrimoniales. **[OFFICIAL META]** (S10-025)
- **Comercio en la conversación**: checkout de Shopify dentro del Business Agent en Messenger (test, oct-2026); checkout
  en Meta AI con Adyen/PayPal/Shopify/Stripe ("este otoño"); Muse (agente personal) compra con comisión. **[OFFICIAL META]** (S10-014, S10-061)
- **Caso oficial**: Movida (Brasil) +44% reservas diarias por WhatsApp y 85% de conversaciones resueltas sin humano en un
  mes (Q2-2026). Es un caso elegido por Meta. **[OFFICIAL META]** (S10-020)
- **Chatbots de IA de terceros**: WhatsApp prohibió los chatbots generalistas en la Business API (efectivo 15-ene-2026);
  la atención al cliente con IA propia sigue permitida; en la UE, excepción de 12 meses con tarifa (mar-2026). **[OFFICIAL META]**/prensa (S10-057)
- **Mensajería como palanca publicitaria**: click-to-message +40% (Q2-2025) y +50% (Q4-2025) en EE. UU.; CTWA +60%
  (Q3-2025); paid messaging $2B run-rate (Q4-2025); "other revenue" de FoA superó $1B en Q2-2026 por WhatsApp. **[OFFICIAL META]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Muse para pequeñas empresas** (29-sep, act. 8-oct; EE. UU. y Canadá): se conecta a cuentas publicitarias, analiza el rendimiento y redacta campañas; nada se publica, envía ni gasta sin aprobación. Es la versión nativa de lo que hace un agente externo con el MCP; no está disponible en España. **[OFFICIAL META]**
> - **Q3 (21-oct)**: Personal Agent Protocol con Sierra, Walmart, Stripe y Shopify; Meta One con más de 15 M de suscripciones; el asistente de Ads Manager despliega "acciones más agénticas" con aprobación. **[OFFICIAL META]**
> - **WhatsApp**: la FEP de CTWA puede durar hasta 7 días; 1.000 service messages gratis por número y mes; los mensajes del Business Agent se cobran también dentro de la FEP (2 $ por millón de tokens). **[OFFICIAL META]**
> - **Facturación del Business Agent en Instagram y Messenger**: la doc oficial solo habla de WhatsApp. **[HYPOTHESIS]**
> - **Checkout en Meta AI**: sigue "este otoño" (test); sin disponibilidad general a 9-nov.
> - Fuentes: S10-117, S10-118, S10-122, S10-123, S10-131 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Línea temporal

| Fecha | Hito | Fuente |
|---|---|---|
| Q2-2025 | Zuckerberg: "cada negocio tendrá una business AI"; integración de business AIs en anuncios de FB/IG y en webs | S10-016 |
| 1-jul-2025 | Conversations (Miami): Business AI en test en México; WhatsApp gestionable en Ads Manager; llamadas | S10-059 |
| 1-jul-2025 | WhatsApp: cobro por mensaje; utility dentro de ventana gratis | S10-023 |
| Q3-2025 | Business AI disponible para todos los elegibles en México (WA) y Filipinas (Messenger); en EE. UU., Business AI en la web del comerciante | S10-017 |
| oct-2025 | WhatsApp prohíbe chatbots IA generalistas en Business API (efectivo 15-ene-2026) | S10-057 |
| Q4-2025 | >1 M conversaciones semanales con Business AIs | S10-018 |
| Q1-2026 | Business AIs en WhatsApp para pymes de LatAm e Indonesia; Messenger en APAC; 10 M conversaciones/semana; "gratis para la mayoría" | S10-019 |
| 16-feb-2026 | WhatsApp: política de precios para AI Providers | S10-026 |
| 5-mar-2026 | UE: chatbots de terceros permitidos 12 meses con tarifa | S10-057 |
| 3-jun-2026 | Conversations (Londres): **Meta Business Agent** global (WA, Messenger, IG) | S10-058 |
| jul-2026 | **Meta Business Agent Platform** (enterprise) | S10-020 |
| ~9-jul-2026 | Lead Capture AI agent para Instant Forms (documentado) | S10-044 |
| 1-ago-2026 | Business Agent facturado por tokens | S10-024 |
| 1-oct-2026 | Service messages de WhatsApp facturados | S10-024 |
| 6-oct-2026 | Checkout Shopify en Business Agent (Messenger, test); Personal Agent Protocol (Meta + Sierra) | S10-014 |

## 2. Qué es Meta Business Agent (según la documentación oficial)

- Agente de IA que atiende conversaciones 24/7 con la voz de la marca. Se alimenta de: información del negocio, FAQs,
  web y ficheros; **instrucciones de respuesta** (tono, prioridades); **conexión a APIs propias y webhooks** para ejecutar
  acciones (reservar, confirmar pagos); **handoff** a tu app/humano en eventos concretos; pruebas con mensajes de ejemplo.
  **[OFFICIAL META]** (S10-025)
- Requiere número elegible de WhatsApp Business Platform en país autorizado; un número que ya usa otro agente IA no es
  elegible; endpoint de elegibilidad = fuente de verdad. **[OFFICIAL META]** (S10-025)
- En los anuncios: Meta presentó el Business Agent también para **click-to-message ads** (jun-2026), y desde 2025 integra
  business AIs en anuncios de FB/IG. **[OFFICIAL META]** (S10-016, S10-044)

## 3. Economía (lo que cambia el cálculo de CPL/CPA en mensajería)

| Concepto | Precio/regla | Desde | Fuente |
|---|---|---|---|
| Plantillas de marketing | Por mensaje entregado, por país; sin tramos de volumen; **max-price** configurable en Marketing Messages API (2026) | 1-jul-2025 | S10-023 |
| Plantillas utility/auth | Por mensaje; tramos de volumen; utility dentro de ventana de servicio gratis | 1-jul-2025 | S10-023 |
| Service messages (no plantilla) | **Cobrados** a tarifa utility/auth, sin tramos | 1-oct-2026 | S10-024 |
| Mensajes del Business Agent | $2 / 1 M tokens (~4–5 cts por mensaje); un solo cargo por mensaje | 1-ago-2026 | S10-024 |
| Ventana Free Entry Point (CTWA, botón de Página) | 72 h, todos los mensajes gratis si se responde en 24 h | vigente | S10-023 · **2026-11-09**: ya oficial (página de precios releída: FEP de CTWA de hasta 7 días y 1.000 service messages gratis por número y mes; S10-118) |
| IA de terceros | Coste de IA lo cobra el proveedor; Meta cobra la entrega | vigente | S10-024 |

**Implicación**: el coste de una conversación ya no es solo el CPC/CPM del anuncio. Para CTWA, la ventana de 72 h
amortigua el coste; fuera de ella, cada intercambio cuesta. Un agente que da 15 respuestas largas por conversación puede
costar ~0,6–0,75 $ en tokens. **[STRONG INFERENCE]** (cálculo con la tarifa oficial; el número de tokens por mensaje varía).

Las cifras de terceros de "1.000 service messages gratis al mes" o "FEP de 7 días" **no aparecen** en la documentación **[OUTDATED] desde el 2026-11-09**: ambas cifras están ya en la página oficial de precios (S10-118); la subpágina de no plantilla sigue sin los 1.000 (S10-119).
oficial consultada a 15-oct-2026 → **[CONTESTED]**/no confirmado.

## 4. Cuándo usar el Business Agent (y cuándo no)

| Situación | Recomendación | Etiqueta |
|---|---|---|
| Alto volumen de preguntas repetitivas pre-venta (horarios, stock, precios, envío) | Usar; medir resolución y conversión | [EMPIRICAL] (patrón) |
| Reservas/citas con sistema propio accesible por API | Usar con acciones vía API y handoff | [OFFICIAL META] capacidad |
| Lead gen high-ticket donde la cualificación humana es diferencial | Usar solo para pre-cualificar y agendar; handoff temprano | [STRONG INFERENCE] |
| Sectores excluidos (salud, finanzas, alcohol, juego…) | No disponible; usar flujos/humanos o IA propia permitida | [OFFICIAL META] |
| Marca con tono muy específico o claims regulados | Instrucciones estrictas + revisión de muestras; no dejar al agente prometer precios/condiciones | [STRONG INFERENCE] |
| Mercado UE | Revisar privacidad y la política de IA de terceros | [STRONG INFERENCE] |

## 5. Métricas mínimas para gobernar un agente conversacional

- Tasa de resolución sin humano (Meta reporta 85% en el caso Movida) **y** tasa de handoff correcto.
- Conversión por conversación (cita/compra/lead cualificado) vs conversaciones atendidas por humanos (control).
- Coste por conversación (anuncio + mensajes + tokens) y por resultado de negocio.
- Muestreo semanal de transcripciones (alucinaciones, promesas indebidas, tono).
- Señal de vuelta a Meta: enviar los resultados de negocio (lead cualificado, venta) por CAPI para que los anuncios
  click-to-message optimicen a calidad. **[STRONG INFERENCE]**

## 6. Comercio agéntico: lo que viene

- **Checkout en conversación** (Shopify en Messenger, test) y **checkout en Meta AI** (otoño 2026). **[OFFICIAL META]** (S10-014)
- **Muse** (agente personal, EE. UU., 8-sep-2026): compra en webs con tarjeta de un solo uso; Meta cobrará una pequeña
  comisión; Amazon lo bloquea. **[OFFICIAL META]**/prensa (S10-061)
- **Personal Agent Protocol** (Meta + Sierra, 6-oct-2026): estándar para que agentes personales se autentiquen con negocios
  (OAuth, permisos). Spec en borrador. **[OFFICIAL META]**/prensa.
- Implicación posible: catálogos limpios, datos estructurados y políticas claras (envíos, devoluciones) pasan a ser
  "creatividad" para agentes. **[HYPOTHESIS]**

## Implicaciones operativas

- Recalcular el coste real de campañas CTWA/CTM con la tarifa de octubre-2026 y el Business Agent por tokens.
- Diseñar el agente con **handoff** explícito y conectar resultados a CRM → CAPI.
- No automatizar promesas comerciales (precios, descuentos, plazos) sin validación desde sistema (API) — el agente debe
  consultar, no inventar.
- Revisar elegibilidad por vertical antes de prometer el producto a un cliente.

## Errores frecuentes

- Medir el agente por "conversaciones atendidas" en lugar de resultado de negocio.
- Olvidar que las respuestas fuera de la ventana gratuita ahora se pagan.
- Asumir que un chatbot genérico de terceros puede operar en WhatsApp como asistente general (prohibido desde 15-ene-2026 salvo excepción UE).

## Preguntas abiertas

- ¿Qué precio y condiciones tendrá Business Agent Platform? ¿Medición de incrementalidad del agente?
- ¿El Business Agent en Instagram tendrá el mismo modelo de precios?
- ¿Meta pasará a cobrar "por resultado" (cita/venta) como sugirió en Q2-2026?

## Fuentes clave

- [Non-template messages pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages) — 2026 — meta-developers (S10-024)
- [Meta Business Agent overview](https://developers.facebook.com/documentation/meta-business-agent/overview) — 2026 — meta-developers (S10-025)
- [WhatsApp pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — meta-developers (S10-023)
- Earnings Q3-2025 → Q2-2026 (S10-017 a S10-020) — meta-investors
- [Business Agent platform (Conversations 2026)](https://www.businesstoday.in/technology/artificial-intelligence/story/meta-unveils-ai-business-agent-platform-for-whatsapp-instagram-and-messenger-534739-2026-06-03) — 2026-06-03 — prensa (S10-058)
- [Rival AI chatbots on WhatsApp in Europe](https://techcrunch.com/2026/03/05/meta-will-allow-rival-ai-chatbots-on-whatsapp-in-europe-but-for-a-fee/) — 2026-03-05 — prensa (S10-057)
