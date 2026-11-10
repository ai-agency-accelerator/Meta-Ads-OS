# WhatsApp ads: click-to-WhatsApp, Status ads, canales promocionados y optimización

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: anuncios que llevan a WhatsApp (CTWA) desde Facebook/Instagram/Threads, anuncios dentro de WhatsApp (Status en la pestaña Updates, canales promocionados), objetivos y performance goals, ventana gratuita (FEP), creatividad y mensaje de bienvenida, cualificación y evidencia de rendimiento. Plataforma, precios y medición de revenue en `12-…`.

## TL;DR

- **CTWA se configura con conversion location "Messaging apps / Message destinations" → WhatsApp** en Engagement, Leads, Sales o Traffic. Performance goals: **conversaciones**, **leads** y **compras** (estas dos últimas son las "down-funnel optimizations"). [OFFICIAL META] ([WhatsApp Business](https://whatsappbusiness.com/resources/resource-library/down-funnel-optimizations-whatsapp/))
- **Optimizar a leads o compras supera a optimizar a conversaciones en los tests de Meta:** −24 % coste por lead (116K campañas, nov-2024) y −10 % coste por compra (estudio de incrementalidad H2-2024). Casos de Meta: −12 % a −79 % coste por resultado. [OFFICIAL META] (sesgo de selección en casos de éxito)
- **La optimización a leads de CTWA NO está disponible en la UE, Reino Unido, Japón ni Corea del Sur** (según Meta). En España optimizarás a conversaciones o a compras/eventos vía CAPI. [OFFICIAL META] ([Meta](https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/)) **Matiz 2026-11-09:** el Help Center (575610661605746 y 447934475640650) no lo dice con esas palabras: da un aviso genérico de que ciertas métricas, campañas y funciones de mensajería no están disponibles para anuncios entregados a o desde Europa, dice que la optimización a leads por mensajería se introduce de forma gradual (donde existe, pide ≥ 10 leads o compras en 30 días) y no menciona el Reino Unido. [OFFICIAL META] (aviso genérico) Compruébalo en Ads Manager con la cuenta antes de planificar.
- **Ventana gratuita (FEP)**: si respondes en ≤24 h a un usuario que llega desde un CTWA (o el botón de WhatsApp de la Página) en la app móvil, todos los mensajes son gratis durante la ventana: **72 h** históricamente; **"hasta 7 días" para CTWA desde el 28-sep-2026** según el changelog citado por varios BSP (la página de precios que pude leer aún decía 72 h). Las respuestas de Meta Business Agent se cobran por tokens incluso dentro. [OFFICIAL META] (72 h y, desde el 2026-11-09, los 7 días; antes [CONTESTED]: solo BSPs, la doc oficial de precios seguía diciendo 72 h el 16-oct-2026) **Corrección 2026-11-09**: la página oficial de precios de WhatsApp, releída, ya dice que la FEP de CTWA "may remain open for up to 7 days" y que hay **1.000 service messages gratis por número y mes**; los mensajes del Business Agent se cobran también dentro de la FEP. Pasa a [OFFICIAL META] (la fecha del 28-sep la dan BSPs; la subpágina de mensajes sin plantilla no cita los 1.000). Fuente: S10-118 en `fuentes/ledger-10-cambios-api-ia.md`.
- **Status ads (pestaña Updates)**: anunciados el 16-jun-2025; rollout global feb–mar 2026; vertical 9:16; CTA a chat de WhatsApp o web; segmentación limitada (país/ciudad, idioma, canales seguidos, interacción con anuncios; datos de Accounts Center solo si el usuario vinculó WhatsApp). Usuarios pueden ocultar anuncios por empresa. [OFFICIAL META] + [STRONG INFERENCE] (rollout)
- **Canales promocionados**: pago por aparecer en el directorio de canales → seguidores. Seguir un canal **no** otorga permiso para mensajes de marketing 1:1. [STRONG INFERENCE]
- **Multi-destino** (WhatsApp + Messenger + IG Direct): −9,5 % coste mediano por mensaje frente a solo WhatsApp en un test de Meta (734K empresas, H2-2024; citado por terceros). Útil si tu operación puede atender varias bandejas. [STRONG INFERENCE]
- **Escala del negocio para Meta**: WhatsApp paid messaging >2.000 M$ de run-rate en Q4-2025; ingresos de click-to-message en EE. UU. +50 % en Q4-2025; "other revenue" +73 % en Q2-2026 impulsado por WhatsApp paid messaging y suscripciones. Un resumen atribuye a Q3-2025 un +60 % interanual de click-to-WhatsApp (no verificado en transcript). Meta está invirtiendo en el canal: espera novedades frecuentes. [OFFICIAL META] (earnings, vía resúmenes de transcripts)

## 1. Mapa de productos publicitarios de WhatsApp (2026)

| Producto | Dónde aparece | Qué consigue | Quién paga qué |
|---|---|---|---|
| **Click-to-WhatsApp (CTWA)** | Anuncios en FB, IG, Threads (y Status) | Abrir chat con la empresa | Subasta de anuncios (CPM) + mensajes (gratis en FEP) |
| **Status ads** | Entre Status en Updates | Chat o visita web | Subasta de anuncios |
| **Promoted channels** | Directorio de canales | Seguidores del canal | Subasta/pago por promoción |
| **Marketing messages (plantillas)** | Chat 1:1 con usuarios con opt-in | Re-engagement, ventas | Precio por mensaje entregado (o max price en MM API) |
| **Marketing messages con optimización en Ads Manager** | Chat 1:1 | Meta elige a qué suscriptores enviar según objetivo | Vía Marketing API/partners (desde 2024; en Marketing API desde 13-ago-2026 según AdsUploader) |
| **Botón de WhatsApp en Página de FB / Google Business Profile** | Página FB; Search/Maps de Google | Chats orgánicos | Página FB: abre FEP; Google: mensajes normales |

[OFFICIAL META] (productos) + [STRONG INFERENCE] (fecha Marketing API).

## 2. Configurar CTWA (Ads Manager, 2026)

| Objetivo | Conversion location | Performance goals disponibles | Comentario |
|---|---|---|---|
| **Engagement** | Messaging apps → WhatsApp | Conversations; **Leads** (fuera de UE/UK/JP/KR) | La configuración "por defecto" de CTWA |
| **Leads** | Messaging apps / Message destinations → WhatsApp | Leads | Ruta recomendada por Meta para lead optimization |
| **Sales** | Messaging apps → WhatsApp | Conversations; **Purchases** (con CAPI) | Meta recomienda setup manual para purchase optimization |
| **Traffic** | Messaging apps → WhatsApp | Conversations, link clicks… | Menos recomendado |
| **Awareness/Engagement con Status** | Placement WhatsApp Status | Según disponibilidad | Guías discrepan sobre qué objetivos desbloquean Status |

Fuentes: [Down-funnel optimizations](https://whatsappbusiness.com/resources/resource-library/down-funnel-optimizations-whatsapp/), [Lead generation strategies](https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/) [OFFICIAL META]; API: OUTCOME_ENGAGEMENT/LEADS/SALES/TRAFFIC [STRONG INFERENCE].

**Requisitos**: número de WhatsApp (app Business o Platform) conectado a la Página o al portfolio. "Once you've met the eligibility criteria" aparecen las optimizaciones down-funnel; Meta no publica los criterios. [OFFICIAL META]

**Cómo "sabe" Meta que hubo un lead o una compra** [HYPOTHESIS + OFFICIAL META parcial]:
- **Compras**: requiere eventos de CAPI for Business Messaging (Purchase con `ctwa_clid`) o pixel/CAPI web si la compra ocurre en la web. [OFFICIAL META]
- **Leads**: Meta define lead como alguien que "shares meaningful information" tras iniciar la conversación (contacto, preguntas por producto/servicio). No documenta el mecanismo de detección; plausiblemente combina señales de la conversación disponibles para la plataforma y eventos CAPI (LeadSubmitted). **No asumir** que la app Business sin API envía señales de calidad. [HYPOTHESIS]

## 3. Ventana gratuita (Free Entry Point, FEP)

| Aspecto | Detalle | Evidencia |
|---|---|---|
| Qué abre la FEP | Usuario escribe desde un CTWA o el CTA de WhatsApp de una Página de Facebook, usando la app Android/iOS (no web/escritorio) | [OFFICIAL META] |
| Condición | La empresa responde en ≤24 h; la ventana empieza con esa respuesta | [OFFICIAL META] |
| Duración | 72 h (doc. pricing); **CTWA "may remain open for up to 7 days"** desde 28-sep-2026; botón de Página sigue en 72 h | [OFFICIAL META] (72 h y, desde el 2026-11-09, 7 días; antes [CONTESTED], solo BSPs: [Spur](https://www.spurnow.com/en/blogs/whatsapp-free-entry-point-window), [Wati](https://support.wati.io/en/articles/16954666-whatsapp-business-platform-api-pricing-changes-service-messages-and-click-to-message-ads), [respond.io](https://respond.io/blog/whatsapp-pricing-change-2026)) · **2026-11-09**: ya oficial (página de precios releída: FEP de CTWA de hasta 7 días y 1.000 service messages gratis por número y mes; S10-118) |
| Qué es gratis dentro | Todos los mensajes (service, utility, marketing, authentication) | [OFFICIAL META] |
| Qué no | Tokens de Meta Business Agent; costes de IA de terceros | [STRONG INFERENCE] (BSPs) / [OFFICIAL META] (IA de terceros) |
| Relación con la CSW (24 h) | Independiente: la CSW determina qué tipo de mensaje puedes enviar (texto libre vs plantilla); la FEP determina el precio | [OFFICIAL META] |

**Implicación económica**: desde el 1-oct-2026 los service messages se cobran (por mensaje y sin tiers según la doc oficial; la franquicia de 1.000/número/mes, que el 16-oct solo citaban BSPs, es [OFFICIAL META] desde el 2026-11-09), así que **los chats que entran por CTWA son los más baratos de atender**: argumento adicional para CTWA frente a tráfico orgánico a wa.me. [STRONG INFERENCE] (Corrección 2026-11-09: la franquicia de 1.000 ya es oficial, S10-118.)

**Implicación operativa**: si tu equipo tarda >24 h en responder, pierdes la FEP (y el lead). Automatiza la primera respuesta. [OFFICIAL META] (regla) + [STRONG INFERENCE]

## 4. Status ads (pestaña Updates) y canales promocionados

- **Producto**: anuncios entre los Status; el usuario puede iniciar conversación desde el anuncio. Updates tab = 1.500 M usuarios/día. [OFFICIAL META] ([Newsroom 16-jun-2025](https://about.fb.com/news/2025/06/helping-you-find-more-channels-businesses-on-whatsapp/))
- **Privacidad/segmentación**: país o ciudad, idioma, canales que sigue, interacción con anuncios; si el usuario añadió WhatsApp al Accounts Center, también preferencias y datos de FB/IG. No se usan mensajes, llamadas ni grupos. Meta "never sell or share your phone number to advertisers". [OFFICIAL META]
- **Rollout**: gradual "over the next few months" desde jun-2025; tests en mercados seleccionados a finales de 2025; global feb–mar 2026, con controles para ocultar/bloquear anuncios de una empresa y, en algunas regiones, suscripción sin anuncios para Status/Canales. [STRONG INFERENCE] (prensa)
- **Configuración**: placement WhatsApp Status en Ads Manager; en API requiere Instagram Stories. Objetivos que lo habilitan: las guías discrepan (Engagement/Traffic vs mensajes). Creatividad 9:16, 1080×1920, safe zone similar a Stories. [OFFICIAL META] (dependencia API) + [CONTESTED] (objetivos)
- **Disponibilidad UE**: no he encontrado lista oficial de países; comprobar en Ads Manager. [HYPOTHESIS]
- **Qué esperar** [HYPOTHESIS]: inventario nuevo con CPM probablemente bajo y audiencia masiva, pero segmentación pobre → mejor para ofertas amplias/locales (país/ciudad) y para CTWA directo que para nichos.
- **Canales promocionados**: crecen seguidores de tu canal (broadcast unidireccional). Útil para medios, creadores, marcas con contenido frecuente; no sustituye a una lista de opt-in para mensajes 1:1. [STRONG INFERENCE]

## 5. Creatividad y mensaje de bienvenida

**El anuncio debe vender la conversación** [STRONG INFERENCE]:
- Promesa concreta de lo que pasa al escribir ("Te mandamos precios y disponibilidad en 2 minutos", "Reserva tu cita por WhatsApp").
- Prueba de que hay alguien (o algo) respondiendo: horario, "respuesta inmediata".
- En Status/Reels: vertical, 1 idea, CTA verbal.

**Mensaje prellenado y bienvenida** [OFFICIAL META] (mecánica de greeting/ice breakers común a CTM) + [STRONG INFERENCE]:
- El usuario llega con un mensaje prellenado editable: escríbelo para que identifique la oferta/anuncio ("Hola, quiero info de la promo de implantes de octubre").
- Preguntas frecuentes (ice breakers) que coincidan con las 3 dudas principales.
- Primera respuesta automática en segundos: confirma, entrega valor y hace **una** pregunta de cualificación con botones.
- Si usas la Cloud API, el webhook trae el objeto `referral` (anuncio de origen, titular, `ctwa_clid`): guárdalo en el CRM (ver `12-…`).

## 6. Cualificación en WhatsApp

| Herramienta | Qué es | Cuándo |
|---|---|---|
| Botones / listas (mensajes interactivos) | Respuestas rápidas | Siempre en el primer mensaje |
| **WhatsApp Flows** | Formularios nativos multi-pantalla dentro del chat (estáticos o con endpoint para datos en vivo, p. ej. huecos de agenda) | Cualificar y agendar sin salir de WhatsApp |
| Bot de BSP / ManyChat / Chatfuel | Flujos y reglas | Volumen medio/alto |
| **Meta Business Agent** | Agente IA de Meta (respuestas, catálogo, citas, cualificación, handoff) | Pymes y empresas fuera de verticales excluidos; coste por tokens |
| Agente IA de terceros | LLM propio vía BSP | Control total; atención a la política de "AI providers" (ver `13-…`) |
| Humano | Setter/comercial | Leads cualificados y high-ticket |

Evidencia de Flows (casos Meta, autoreportados): Learnwise 4x leads cualificados y −31 % coste por lead cualificado; Engelife +26 p.p. de tasa de cualificación y −37 % coste por lead cualificado. [OFFICIAL META, autoreportado] ([Spur, recopilación](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks), [Learnwise](https://whatsappbusiness.com/resources/success-stories/learnwise/))

## 7. Evidencia de rendimiento (resumen)

| Comparación | Resultado | Fuente / método |
|---|---|---|
| Leads vs conversaciones | −24 % coste por lead | Meta, 116K campañas / 43K empresas, 4–10 nov 2024 |
| Compras vs conversaciones | −10 % coste por compra | Meta, estudio de incrementalidad H2-2024 |
| Multi-destino vs solo WhatsApp | −9,5 % coste mediano por mensaje | Meta, 734K empresas, 3 semanas H2-2024 (vía terceros) |
| Casos de compra vs conversación (Confer On, Thành Vinh, VIP Leather) | −21 % a −79 % coste por compra | A/B Meta, casos de éxito |
| Casos de leads (Braip, Nutryfit) | −30 % y −12 % coste por lead | A/B Meta, casos de éxito |
| WhatsApp + web vs solo web (Arabian Automobiles) | 2x leads, −56 % CPL | Autoreportado, "no identificablemente repetible" |
| Benchmarks de coste por conversación | 1,5–8 €/conversación (vendor) | Sin muestra declarada; no fiable |

[OFFICIAL META] para estudios; casos = sesgo de supervivencia. **No existe benchmark público fiable de conversación→venta.** [STRONG INFERENCE] ([Spur](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks))

## 8. Cuándo CTWA y cuándo no

**Encaja** [STRONG INFERENCE]: negocios locales y de servicios (clínicas, inmobiliarias, formación, automoción, reformas), ventas consultivas, ticket medio-alto, mercados WhatsApp-first (España, LatAm, India, Brasil, Indonesia), ecommerce con dudas pre-compra (tallas, personalización), audiencias poco "de formulario".

**No encaja**: equipos sin capacidad de respuesta rápida; productos de impulso baratos con checkout web eficiente; campañas que necesitan volumen masivo de leads con coste mínimo y sin cualificación; mercados donde WhatsApp no es la app dominante (EE. UU.: preferir SMS/IG/Messenger; además, plantillas de marketing no se entregan a números +1).

## Implicaciones operativas

- En España/UE: CTWA con goal **Conversations** + CAPI de eventos de cualificación/compra para medir; si vendes por chat, probar **Purchases** con CAPI. Lead optimization nativa no disponible.
- SLA de primera respuesta <5 min (automática en segundos) para no perder la FEP ni el interés.
- Guardar `ctwa_clid` y `referral` de cada conversación desde el primer día.
- Probar Status ads con ofertas amplias/locales y CTA a chat cuando estén disponibles en la cuenta; medir coste por conversación cualificada frente a Reels/Stories.

## Errores frecuentes

- Medir el éxito por "conversaciones iniciadas" (incluye curiosos, spam, "hola" sin respuesta).
- Responder tarde: se pierde la FEP y el lead.
- No identificar el anuncio de origen en el CRM.
- Usar la app Business sin API para volúmenes altos (sin webhooks, sin CAPI, sin multiagente real).
- Planificar plantillas de marketing a números de EE. UU.

## Preguntas abiertas

- Texto oficial definitivo del cambio FEP a "hasta 7 días" y qué la cierra antes. Resuelto en parte el 2026-11-09: el texto oficial es "may remain open for up to 7 days" (S10-118); sigue sin documentarse qué la cierra antes.
- Mecanismo de detección de "lead" en la optimización de CTWA.
- Lista oficial de países con Status ads y si la UE está incluida.
- ¿Llegará la lead optimization de CTWA a la UE?

## Fuentes clave

- [Down-funnel optimizations on WhatsApp](https://whatsappbusiness.com/resources/resource-library/down-funnel-optimizations-whatsapp/) — 2025 — meta-oficial
- [Lead generation strategies for SMBs on WhatsApp](https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/) — 2025 — meta-oficial
- [Pricing on the WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — 2026 — meta-developers
- [Helping You Find More Channels and Businesses on WhatsApp](https://about.fb.com/news/2025/06/helping-you-find-more-channels-businesses-on-whatsapp/) — 2025-06-16 — meta-oficial
- [WhatsApp free entry point window (Spur)](https://www.spurnow.com/en/blogs/whatsapp-free-entry-point-window) — 2026-10 — vendor
- [Wati: service messages and CTM ads](https://support.wati.io/en/articles/16954666-whatsapp-business-platform-api-pricing-changes-service-messages-and-click-to-message-ads) — 2026-09 — vendor
- [Click to WhatsApp Ads Benchmarks](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks) — 2026-10 — vendor
- [WhatsApp Status Ads: Setup, Pricing & Ad Specs](https://www.ycloud.com/blog/whatsapp-status-ads) — 2026-09-12 — vendor
- [Storyboard18: global status ads](https://www.storyboard18.com/brand-makers/whatsapp-introduces-global-status-ads-promoted-channels-and-new-controls-for-users-in-updates-tab-91018.htm) — 2026 — prensa
- [Meta announces business messaging updates (Conversations 2025)](https://www.socialmediatoday.com/news/meta-announces-business-messaging-updates-conversations-2025-whatsapp/752250/) — 2025-07-02 — prensa

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- FEP y service messages: ver corrección en el README del área. Doc oficial (16-oct-2026): FEP 72 h; service messages cobrados desde 1-oct-2026 sin volume tiers ni franquicia. Etiquetas de los 7 días y de los 1.000 gratis cambiadas a [CONTESTED]. **Revertido el 2026-11-09**: la doc oficial ya recoge los 7 días y los 1.000 gratis (S10-118); etiquetas de vuelta a [OFFICIAL META].
