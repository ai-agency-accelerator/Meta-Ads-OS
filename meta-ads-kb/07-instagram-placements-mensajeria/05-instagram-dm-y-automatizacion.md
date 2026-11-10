# Instagram DM: click-to-Direct, comment-to-DM y automatización (ManyChat y nativo)

> Última verificación: 2026-10-15 · Autor: A07 (agente) · Ámbito: cómo funcionan técnicamente los anuncios que abren un DM de Instagram, las reglas oficiales de la API de mensajería (ventanas, private replies, límites), la automatización tipo ManyChat y las alternativas nativas de Meta (Reply to Keywords, Business Agent), diseño de flujos y medición.

## TL;DR

- **Toda automatización de DM en Instagram tiene que ser iniciada por el usuario** (DM, respuesta a Story, comentario, mención o clic en anuncio de mensaje). Mensajes en frío = fuera de política. [OFFICIAL META] (API: el negocio solo puede escribir tras un mensaje entrante) + [STRONG INFERENCE] (consenso de proveedores)
- **Ventana estándar: 24 h desde el último mensaje del usuario.** Fuera de ella solo cabe la etiqueta *human agent* (respuesta humana, hasta 7 días según la documentación de etiquetas; requiere App Review). [OFFICIAL META] ([Messaging API](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api)) + [STRONG INFERENCE] (7 días)
- **Comment-to-DM = "private reply"**: **1 mensaje por comentario, dentro de 7 días** desde el comentario; vale para post, reel, story, Live (solo durante la emisión) y **"ad post"**. El seguimiento solo si el usuario responde, y dentro de 24 h. Si no te sigue, el DM cae en "Solicitudes". [OFFICIAL META] ([Private replies](https://developers.facebook.com/docs/instagram-platform/private-replies))
- **Límites técnicos** (compilación de terceros sobre docs de Meta, ago-2026): ~100 llamadas/s para texto, 10/s audio/vídeo, **750 private replies/hora** en posts y reels. La cifra de "200 DMs/hora" que circula es una convención de herramientas, no un límite publicado. [STRONG INFERENCE] ([Conferbot](https://www.conferbot.com/limits/instagram))
- **Click-to-Instagram Direct + ManyChat**: el anuncio debe ser un anuncio de mensaje ("Send Instagram message") con la app partner seleccionada y el flujo elegido (campo API `partner_app_welcome_message_flow_id`); el primer mensaje necesita al menos un quick reply; ManyChat debe ser la app por defecto en el enrutamiento de conversaciones. El flujo arranca cuando el usuario envía/pulsa. [OFFICIAL META] (campo API) + [EMPIRICAL] (comunidad ManyChat)
- **Meta está "nativizando" el comment-to-DM:** test **"Reply to Keywords"** en la creación de anuncios (25-ago-2026): hasta 5 keywords, un único DM (texto, link, teléfono o email), solo Instagram. Útil para casos simples; para cualificación sigue haciendo falta una herramienta. [EMPIRICAL] ([Jon Loomer](https://www.jonloomer.com/reply-to-keywords-meta-ads-feature/))
- **Meta Business Agent (jun-2026)** también responde en Instagram DMs (respuestas, recomendaciones de catálogo, citas, cualificación, handoff a humano). Coste por tokens para cuentas grandes/API y vía suscripción para pymes. Ver `13-…`. [OFFICIAL META]
- **Optimiza a leads, no a conversaciones**, y envía eventos de cualificación por CAPI (`messaging_channel=instagram`, `ig_sid`). Click-to-Instagram **no** admite optimización a compras. [OFFICIAL META] + [EMPIRICAL] (caso Spur: −35 % coste por lead cualificado al pasar de conversaciones a leads)

## 1. Anatomía de un anuncio click-to-Instagram Direct

1. **Campaña**: Engagement, Sales o Traffic (API: OUTCOME_ENGAGEMENT / OUTCOME_SALES / OUTCOME_TRAFFIC). Goals disponibles: CONVERSATIONS (y en Sales, OFFSITE_CONVERSIONS; en Traffic, LPV/clics…). Para leads en DM existe además Leads con conversion location Instagram. [OFFICIAL META] ([API click-to-Instagram](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-instagram))
2. **Destino**: `destination_type = INSTAGRAM_DIRECT` o multi-destino (Messenger/Instagram/WhatsApp según probabilidad de respuesta de cada persona). [OFFICIAL META]
3. **Creatividad**: imagen, vídeo, carrusel o slideshow; puede usar un post de Instagram existente (`source_instagram_media_id`). [OFFICIAL META]
4. **Mensaje de bienvenida** (`page_welcome_message`): greeting por defecto "Hello! Can I get more info on this?", personalizable con `{{user_first_name}}`; **ice breakers** (preguntas predefinidas con respuesta automática opcional); o **flujo de app partner** (ManyChat, Spur, etc.). [OFFICIAL META]
5. **Qué ve el usuario**: al tocar, Meta abre el hilo con el greeting y los ice breakers; el flujo del partner comienza cuando el usuario envía el mensaje o toca una opción. Hasta entonces no es "contacto" en la herramienta. [EMPIRICAL] (ManyChat community)

**Checklist de configuración ManyChat (o similar)** [EMPIRICAL]:
- Ads Manager → anuncio con "Send Instagram message" → *Partner app* = ManyChat → flujo correcto.
- Primer mensaje del flujo con ≥1 quick reply.
- Conversation routing: ManyChat como app por defecto para Instagram (si hay varias apps, el handover decide quién responde).
- Probar en móvil (los botones no se renderizan igual en escritorio).
- Problema conocido (sep-2026, sin confirmar por Meta/ManyChat): sugerencias generadas por IA de Instagram pueden tapar el quick reply en la primera conversación.

## 2. Reglas oficiales de la API de mensajería de Instagram

| Regla | Detalle | Evidencia |
|---|---|---|
| Quién inicia | El negocio solo puede enviar tras un mensaje entrante del usuario (o un private reply a su comentario) | [OFFICIAL META] |
| Ventana estándar | 24 h para responder a cada mensaje del usuario; se renueva con cada mensaje | [OFFICIAL META] |
| Fuera de ventana | Etiqueta *human agent* (solo humanos, App Review + verificación); 7 días según docs de etiquetas | [OFFICIAL META] (existencia) / [STRONG INFERENCE] (7 días) |
| Otras etiquetas (account update, event update…) | No disponibles en Instagram | [STRONG INFERENCE] |
| Private reply | 1 por comentario; ≤7 días desde el comentario; post, reel, story, Live (solo en emisión) y ad post | [OFFICIAL META] |
| Follow-up tras private reply | Solo si el usuario responde; dentro de 24 h | [OFFICIAL META] |
| Bandeja de destino | Inbox si el usuario sigue la cuenta; si no, Requests | [OFFICIAL META] |
| Requests inactivos | Conversaciones en Requests inactivas 30 días no se devuelven por API | [OFFICIAL META] |
| Tipo de cuenta | Profesional (Business o Creator) con "Allow access to messages" activado | [STRONG INFERENCE] |
| Límites | ~100 llamadas/s texto; 10/s media; 750 private replies/h posts y reels; inbox >72.000 mensajes deja de mostrar nuevos | [STRONG INFERENCE] (compilación Conferbot) |
| Contenido | Texto <1.000 caracteres; hasta 13 quick replies; carrusel hasta 10 elementos; 4 ice breakers | [STRONG INFERENCE] |

**Ventana ampliada en conversaciones desde anuncios**: una fuente de terceros cita un changelog del 28-sep-2026 según el cual la ventana estándar podría ampliarse hasta 7 días en conversaciones iniciadas desde click-to-Messenger/click-to-Direct. **No verificado** en documentación de Meta; sí está documentado el cambio equivalente en WhatsApp (FEP hasta 7 días, ver `11-…`). [HYPOTHESIS]

## 3. Comment-to-DM: cuándo es una buena estrategia

**Mecánica**: el usuario comenta una palabra clave ("GUÍA", "PRECIO") en un Reel/post/anuncio → la herramienta envía un private reply con el recurso o la primera pregunta → si el usuario responde, se abre la ventana de 24 h y continúa la cualificación.

**Por qué funciona** [STRONG INFERENCE]:
- Convierte la intención en una acción pública (comentario) que además es señal de engagement para la distribución del post.
- El DM llega con contexto (sabes qué contenido lo originó).
- En orgánico, multiplica comentarios; en pago, permite un "lead magnet" sin formulario.

**Riesgos y matices**:
- Percepción de spam y "comment bait" si el contenido no aporta. Loomer lo describe como "puede parecer spammy, pero puede funcionar". [EMPIRICAL]
- Solo 1 private reply por comentario: el primer mensaje debe pedir una respuesta (pregunta o botón) para abrir la ventana.
- En anuncios, los comentarios se acumulan en el post del anuncio; si es un *dark post* (creado en Ads Manager, no publicado en el perfil), comprueba que tu herramienta permite trigger sobre ese post (normalmente "cualquier post" o el ID del post del anuncio). [HYPOTHESIS] (comportamiento por herramienta, verificar)
- Comentarios con keyword en anuncios visibles para todos: algunos usuarios copian la keyword sin interés real → leads de baja intención. Cualifica en el DM.

**Nativo vs herramienta**:

| Necesidad | Reply to Keywords (test Meta, ago-2026) | Automatización respuestas de Meta Business Suite / Business Agent | ManyChat y similares |
|---|---|---|---|
| DM único con link a un recurso | Sí | Parcial | Sí |
| Mensajes distintos por keyword | No (un mensaje para todas) | — | Sí |
| Cualificación multi-paso con ramas | No | Business Agent (IA) | Sí (flujos) |
| Etiquetas, CRM, webhooks | No | Limitado | Sí |
| Orgánico + anuncios | Solo anuncios IG | Orgánico | Ambos |
| Coste | Incluido | Business Agent: suscripción/tokens | Suscripción del tool |

[EMPIRICAL] (Loomer) + [OFFICIAL META] (Business Agent) + [STRONG INFERENCE] (comparativa).

## 4. Diseño de flujos de DM que convierten

Plantilla para servicios / high-ticket (ver `14-…` para el funnel completo) [STRONG INFERENCE]:

1. **Apertura (≤3 s tras el clic)**: confirma lo que pidió ("¡Hola {{nombre}}! Aquí tienes la guía 👇") + entrega inmediata.
2. **Micro-compromiso**: 1 pregunta cerrada con quick replies ("¿Para ti o para tu negocio?").
3. **Cualificación** (2–4 preguntas máximo): necesidad, plazo, presupuesto/rango, ubicación. Captura email/teléfono si procede (prefill de Instagram no existe como en formularios; pídelo con validación).
4. **Bifurcación**: cualificado → enlace de calendario o paso a humano/WhatsApp; no cualificado → recurso + nurturing (dentro de las reglas de ventana).
5. **Handoff humano**: notificación al equipo; SLA de respuesta (objetivo <5 min en horario laboral).
6. **Registro**: guardar respuestas como campos; disparar evento CAPI (LeadSubmitted, QualifiedLead) con `ig_sid`.

**Copys del anuncio coherentes con el flujo**: el anuncio debe decir exactamente qué pasará ("Escríbenos y te mandamos el precio en 1 minuto"). Los ice breakers deben reflejar las 3 dudas principales.

## 5. Medición en Instagram Direct

- **Conversaciones iniciadas** (Ads Manager) = volumen, no calidad.
- **CAPI for Business Messaging (Instagram)**: dataset vinculado al usuario de IG, `action_source=business_messaging`, `messaging_channel=instagram`, `instagram_business_account_id` + `ig_sid`, permiso `instagram_manage_events`. Eventos útiles: LeadSubmitted, QualifiedLead, Purchase (para medir; la optimización a compra no está disponible en click-to-Instagram). Meta no deduplica estos eventos: hazlo tú. [OFFICIAL META] ([docs](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging))
- **Si la venta ocurre en web**: usa el pixel/CAPI web; la atribución se apoya en el clic del anuncio. [OFFICIAL META]
- **Caso de referencia** (vendor, una cuenta, 14 días, India): pasar de optimizar a conversaciones a optimizar a leads en anuncios a IG DM → coste por chat +9 %, cualificados de 22 % a 37 % de los chats, coste por lead cualificado −35 %. [EMPIRICAL, baja generalización] ([Spur](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks))

## Implicaciones operativas

- Elegir una sola "app dueña" del inbox de Instagram por cuenta (ManyChat, BSP o Business Agent) y documentar el enrutamiento; los conflictos de handover son la causa nº 1 de "el anuncio no dispara el flujo".
- Para cuentas con mucho volumen de comentarios en anuncios: activar Reply to Keywords (si disponible) o herramienta; ocultar spam (ver `08-…`).
- Medir coste por lead cualificado y por cita, no coste por conversación.
- Evitar automatizar seguimiento promocional fuera de ventana.

## Errores frecuentes

- Anuncio de vídeo normal (no de mensaje) esperando que dispare el trigger "user clicks Instagram ad".
- Primer mensaje sin pregunta ni botón: la ventana se cierra y el lead se pierde.
- Dejar los DMs en Requests sin revisar (no seguidores).
- Usar herramientas no oficiales que inician sesión con contraseña o hacen DMs en frío (riesgo de bloqueo de cuenta).
- Prometer "respuesta inmediata" y tener humanos respondiendo al día siguiente.

## Preguntas abiertas

- Confirmación oficial de la ampliación de ventana para conversaciones desde anuncios en Instagram/Messenger (sep-2026).
- ¿Reply to Keywords saldrá de test y admitirá mensajes por keyword o flujos?
- Comportamiento de los triggers de comentarios sobre dark posts en cada herramienta (verificar por herramienta).
- Límite real por hora de DMs salientes (Meta no publica un cap fijo).

## Fuentes clave

- [Private Replies – Instagram Platform](https://developers.facebook.com/docs/instagram-platform/private-replies) — vigente — meta-developers
- [Instagram Messaging API (Send Messages)](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api) — vigente — meta-developers
- [Click to Instagram Direct ads (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-instagram) — vigente — meta-developers
- [Conversions API for Business Messaging](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging) — vigente — meta-developers
- [Reply to Keywords Meta Ads Feature](https://www.jonloomer.com/reply-to-keywords-meta-ads-feature/) — 2026-08-25 — practitioner
- [Instagram Messaging API Limits 2026](https://www.conferbot.com/limits/instagram) — 2026-08-20 — vendor
- [ManyChat community: Instagram ads automation](https://community.manychat.com/general-q-a-43/instagram-ads-automation-sends-first-message-but-quick-reply-button-is-missing-10812) — 2024–2026 — comunidad
- [Click to WhatsApp Ads Benchmarks (incluye caso IG DM)](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks) — 2026-10 — vendor
- [Conversations 2026: Meta Business Agent](https://whatsappbusiness.com/blog/introducing-meta-business-agent-ai/) — 2026-06-03 — meta-oficial
