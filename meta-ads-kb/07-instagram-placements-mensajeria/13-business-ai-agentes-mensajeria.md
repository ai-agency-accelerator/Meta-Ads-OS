# Business AI y agentes de IA en WhatsApp, Messenger e Instagram (2024–2026)

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: qué existe realmente en IA conversacional de Meta para empresas (Business AI → Meta Business Agent, Business Agent Platform, Lead Capture AI agent en formularios), para quién, cuánto cuesta, restricciones, alternativas de terceros y cómo encaja con anuncios de mensaje.

## TL;DR

- **Nombre actual: "Meta Business Agent"** (antes "Business AI"). Lanzado globalmente el **3-jun-2026** (Conversations, Londres) para WhatsApp (app Business y Business Platform), Messenger e Instagram; responde preguntas del negocio, recomienda productos del catálogo, **agenda citas, cualifica leads y cierra ventas**, con traspaso a humano cuando el negocio decide. >1 M de empresas ya lo usaban. [OFFICIAL META] ([WhatsApp Business blog](https://whatsappbusiness.com/blog/introducing-meta-business-agent-ai/))
- **Coste**: "gratis para empezar", con suscripciones de pago para pymes (incluido en niveles de *WhatsApp Business Premium*) y **tokens** para empresas grandes/API. BSPs reportan **2 $ por millón de tokens desde el 1-ago-2026** (~4–5 céntimos por respuesta típica), que se suma al coste de mensajes y **no queda cubierto por la ventana gratuita de CTWA**. [OFFICIAL META] (modelo) + [STRONG INFERENCE] (tarifa)
- **Restricciones**: no disponible para **finanzas, gobierno, salud, alcohol, juego, medicamentos sin receta y servicios matrimoniales**; requiere número elegible (vertical, país, buena reputación, verificación); **una integración activa de agente autorizado de terceros en el número bloquea Meta Business Agent**. [OFFICIAL META] ([docs](https://developers.facebook.com/documentation/meta-business-agent/overview))
- **Meta Business Agent Platform** (enterprise): construir/desplegar agentes conectados a sistemas como Shopify, Zendesk o Shopee, con guardrails y medición. [OFFICIAL META]
- **Lead Capture AI agent (jul-2026)**: opción en instant forms para que una IA guíe al usuario conversacionalmente y responda dudas con datos del formulario y la web; Meta decide quién ve chat o formulario; **el anunciante no puede ver la conversación**. [EMPIRICAL] ([Jon Loomer, 9-jul-2026](https://www.jonloomer.com/lead-capture-ai-agent-instant-forms/))
- **Agentes de terceros siguen permitidos** para atención/ventas del propio negocio; lo que Meta vetó (oct-2025, efectivo 15-ene-2026) fueron los **asistentes de IA de propósito general** como producto (tipo ChatGPT en WhatsApp), veto contestado por la Comisión Europea (medidas cautelares 9-jun-2026). [STRONG INFERENCE]
- **Para quién tiene sentido hoy** [STRONG INFERENCE]: pymes con catálogo y FAQs estables (ecommerce, retail, restauración, servicios locales no sanitarios) que reciben muchos chats de CTWA y no pueden responder en minutos. **No** para salud, finanzas o high-ticket donde el error cuesta caro sin control del dataset.

## 1. Cronología

| Fecha | Hito | Evidencia |
|---|---|---|
| 6-jun-2024 | Conversations (São Paulo): Business AI en test en la app WhatsApp Business (soporte y venta en chats; ayuda para crear anuncios CTWA) | [OFFICIAL META] ([blog](https://whatsappbusiness.com/blog/new-ways-for-businesses-to-do-more-with-messaging/)) |
| 1-jul-2025 | Conversations (Miami): Business AI se expande primero en México; base para voz con IA; llamadas para grandes empresas | [OFFICIAL META] (vía prensa) |
| 2-oct-2025 | Business AI en WhatsApp y Messenger en México y Filipinas (20-oct en Filipinas); Business AI para webs de terceros; Meta AI business assistant para anunciantes | [STRONG INFERENCE] ([CNBC](https://www.cnbc.com/amp/2025/10/02/meta-wants-to-bring-its-business-ai-chat-tools-to-third-party-websites.html)) |
| oct-2025 → 15-ene-2026 | Términos de WhatsApp Business API vetan asistentes de IA de propósito general | [STRONG INFERENCE] ([TechCrunch](https://techcrunch.com/2025/12/04/eu-investigating-meta-over-policy-change-that-bans-rival-ai-chatbots-from-whatsapp/)) |
| 3-jun-2026 | **Meta Business Agent** global (WhatsApp, Messenger, Instagram); Agent Platform; búsqueda de empresas por nombre en WhatsApp ("starting soon"); briefing matinal en test | [OFFICIAL META] |
| 9-jul-2026 | Lead Capture AI agent en instant forms (visto en cuentas) | [EMPIRICAL] |
| 1-ago-2026 | Facturación por tokens de Business Agent (2 $/M tokens) | [STRONG INFERENCE] |
| 8-sep-2026 | Pago con tarjeta para Business Agent | [STRONG INFERENCE] (YCloud) |
| 30-sep-2026 | Fecha límite para añadir método de pago (o se interrumpe la entrega de service messages) | [STRONG INFERENCE] |

## 2. Qué hace Meta Business Agent (y qué no sabemos)

**Capacidades declaradas** [OFFICIAL META]:
- Responde preguntas específicas del negocio en el idioma del cliente y con el tono de la marca.
- Recomienda productos del catálogo.
- Agenda citas y cualifica leads entrantes.
- Cierra ventas y hace seguimiento.
- El negocio decide cuándo interviene un humano.
- Para desarrolladores: añadir conocimiento (info, FAQs, webs, archivos), instrucciones de respuesta, conectar APIs/webhooks propios para que el agente ejecute acciones, test antes y después de lanzar, pasar el control entre agente y app en eventos concretos. ([docs](https://developers.facebook.com/documentation/meta-business-agent/overview))

**Canales (nota del 2026-11-09):** la documentación de desarrolladores de Meta Business Agent solo cita WhatsApp; el
blog de Meta cita WhatsApp y Messenger, con Instagram «en camino». Para un cliente que vive en Instagram Direct, no
cuentes con él todavía. [OFFICIAL META] (las dos fuentes, que no coinciden)

**En test / roadmap**: briefing matinal de chats nocturnos e insights (selección de cuentas en WhatsApp Business app, Instagram Pro, Messenger y Business Suite); investigación de mercado, insights de producto, calendario, inteligencia competitiva. [OFFICIAL META]

**Escala y casos**: >1 M empresas usándolo; >1.000 M de hilos activos diarios con empresas en WhatsApp, Messenger e Instagram; Trendyol: >15.000 interacciones comerciales gestionadas por IA la primera semana en Arabia Saudí. [OFFICIAL META]

**Lo que no sabemos** [HYPOTHESIS]:
- Tasas de error/alucinación y control del dataset (Loomer plantea la misma duda para el Lead Capture agent).
- Si Meta usa las conversaciones del agente como señal de optimización de anuncios (plausible, no documentado).
- Disponibilidad exacta por país y vertical en la app Business frente a la Platform.

## 3. Costes y comparación con agentes de terceros

| Opción | Coste de IA | Coste de mensajes WhatsApp (desde 1-oct-2026) | Control | Riesgo |
|---|---|---|---|---|
| Meta Business Agent (app Business, pyme) | Suscripción WhatsApp Business Premium (niveles en despliegue) | App Business: sin cargos por mensaje (salvo marketing messages de pago) | Bajo-medio | Calidad no auditable a fondo |
| Meta Business Agent (Platform/API) | ~2 $/M tokens (~0,04–0,05 $/respuesta) | Service messages a tarifa utility (1.000 gratis/número/mes); FEP no cubre tokens | Medio (instrucciones, APIs) | Verticales excluidos |
| Agente de terceros (BSP + LLM) | Coste del LLM/BSP | Service messages (FEP sí gratis para mensajes) | Alto | Desarrollo y mantenimiento |
| Bot de reglas (ManyChat/Flows) | Cuota de herramienta | Igual | Alto | Menos flexible |
| Humano | Salario | Igual | Máximo | Lentitud fuera de horario |

Evidencia de la tabla: los 1.000 service messages gratis por número y mes y que la FEP no cubre los mensajes del
Business Agent son [OFFICIAL META] desde el 2026-11-09 (página de precios de WhatsApp releída; S10-118 en
`fuentes/ledger-10-cambios-api-ia.md`); antes solo los citaban BSPs. El coste por token y por respuesta es
[STRONG INFERENCE] (BSPs).

Ejemplo de BSP (SleekFlow, vendor competidor): 1.000 respuestas IA en Brasil ≈ 40–50 $ con Business Agent vs 27–97 $ con configuraciones de terceros según complejidad. [STRONG INFERENCE, sesgo comercial]

**Regla de bolsillo** [HYPOTHESIS]: si el coste por conversación cualificada que atiende la IA es <5 % del margen esperado por lead cualificado, el coste de IA es irrelevante; el factor decisivo es la **tasa de cualificación y de cita** que consigue frente a humanos.

## 4. Lead Capture AI agent (instant forms)

- **Dónde**: "Enable lead capture AI agent" al crear anuncios con instant forms (o en el tipo de formulario). [EMPIRICAL]
- **Cómo**: flujo conversacional para rellenar el formulario; responde dudas básicas usando el formulario y la web; si no sabe, lo dice y sigue; termina al enviar o salir. Meta elige chat o formulario por usuario. [EMPIRICAL]
- **Limitaciones**: no ves la conversación ni controlas el dataset; no es un destino (no queda hilo en Messenger). [EMPIRICAL]
- **Cuándo probarlo**: servicios profesionales y ofertas complejas donde las dudas provocan abandono del formulario; menos útil en lead magnets gratuitos. Test A/B con/sin agente midiendo **tasa de cualificación en CRM**, no solo CPL. [EMPIRICAL] (Loomer) + [STRONG INFERENCE]
- Relación con área 05 (lead gen): coordinar.

## 5. Cómo encaja con los anuncios de mensaje

- **CTWA/CTM/IG Direct + Business Agent**: elimina el cuello de botella de la primera respuesta (clave para la FEP de 24 h y para la conversión). [STRONG INFERENCE]
- **Medición**: el agente no envía por sí solo eventos CAPI a tu dataset según la documentación leída; si cualifica o vende, necesitas que tu sistema (vía webhooks/APIs conectadas) dispare LeadSubmitted/QualifiedLead/Purchase. [HYPOTHESIS] (no documentado)
- **Conflicto de "dueño" del número**: si ya tienes un agente/bot autorizado de un BSP en el número, Meta Business Agent queda bloqueado; decide una arquitectura. [OFFICIAL META]
- **Búsqueda de empresas por nombre en WhatsApp** ("Business Discovery"): nueva entrada orgánica de conversaciones (no FEP). [OFFICIAL META]

## 6. Decisión: ¿Meta Business Agent, tercero o humano?

```
¿Vertical excluido (salud, finanzas, alcohol, juego, OTC, gobierno, matrimonio)? → Tercero/humano.
¿Volumen de chats > capacidad de respuesta en <5 min? 
   ├─ No → humano + respuestas rápidas/Flows.
   └─ Sí → ¿Necesitas control fino del guion, CRM y eventos CAPI?
            ├─ Sí → agente de terceros vía BSP (o Business Agent Platform con APIs propias).
            └─ No → Meta Business Agent (empezar gratis), auditar 50–100 conversaciones/semana.
¿Ticket alto o asesoramiento regulado? → IA solo para triaje y agenda; venta humana.
```

[STRONG INFERENCE]

## Implicaciones operativas

- Para cuentas de servicios locales con CTWA: probar Business Agent o bot como **primera respuesta** y medir tasa de cualificación/cita frente a la respuesta humana previa (antes/después o A/B por número/campaña).
- Presupuestar tokens si se usa Business Agent en la Platform; no asumir que la FEP lo hace gratis.
- Revisar contratos con BSP: compatibilidad con Business Agent o exclusividad de su agente.
- Seguir el caso UE sobre "AI providers" si se planea usar asistentes generales dentro de WhatsApp.

## Errores frecuentes

- Activar un agente IA sin auditar respuestas en un vertical con riesgo de claims (precios, garantías, salud).
- Suponer que la IA "envía las conversiones a Meta".
- Mezclar dos bots en el mismo número (handover roto).
- Medir el éxito del agente por % de chats respondidos en vez de % de leads cualificados y citas.

## Preguntas abiertas

- Precios oficiales y niveles de WhatsApp Business Premium con Business Agent.
- Disponibilidad del Business Agent en la UE por vertical; verificación de métricas de calidad.
- ¿Usa Meta las señales del agente para optimizar CTWA (p. ej. "leads")?
- Disponibilidad general del Lead Capture AI agent y si dará acceso a transcripciones.

## Fuentes clave

- [Conversations 2026: Introducing Meta Business Agent](https://whatsappbusiness.com/blog/introducing-meta-business-agent-ai/) — 2026-06-03 — meta-oficial
- [Meta Business Agent overview (developers)](https://developers.facebook.com/documentation/meta-business-agent/overview) — 2026 — meta-developers
- [Meta's AI agent for WhatsApp Business is now available globally](https://techcrunch.com/2026/06/03/metas-ai-agent-for-whatsapp-business-is-now-available-globally/) — 2026-06-03 — prensa
- [Lead Capture AI Agent for Instant Forms](https://www.jonloomer.com/lead-capture-ai-agent-instant-forms/) — 2026-07-09 — practitioner
- [Meta Business Agent pricing changes 2026 (SleekFlow)](https://sleekflow.io/en-sg/blog/meta-business-agent-pricing-changes-2026) — 2026-09 — vendor
- [YCloud: pricing update 1-oct-2026](https://www.ycloud.com/blog/whatsapp-api-message-pricing-update-effective-october-1-2026) — 2026-09-04 — vendor
- [Meta wants to bring its Business AI chat tools to third-party websites](https://www.cnbc.com/amp/2025/10/02/meta-wants-to-bring-its-business-ai-chat-tools-to-third-party-websites.html) — 2025-10-02 — prensa
- [New Ways for Businesses to Do More with Messaging (2024)](https://whatsappbusiness.com/blog/new-ways-for-businesses-to-do-more-with-messaging/) — 2024-06-06 — meta-oficial
- [Cannes Lions 2026 (Meta LatAm)](https://about.fb.com/ltam/news/2026/06/cannes-lions-2026-nuevas-herramientas-creativas-y-para-creadores-que-facilitan-el-salto-hacia-la-ia/) — 2026-06-23 — meta-oficial
- [EU investigating Meta over WhatsApp AI policy](https://techcrunch.com/2025/12/04/eu-investigating-meta-over-policy-change-that-bans-rival-ai-chatbots-from-whatsapp/) — 2025-12-04 — prensa
