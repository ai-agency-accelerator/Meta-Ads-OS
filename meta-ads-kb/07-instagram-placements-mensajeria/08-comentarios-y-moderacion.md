# Comentarios en anuncios: moderación, negativos, ocultar vs borrar, respuestas y herramientas

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: gestión de comentarios en anuncios de Facebook, Instagram (y nota sobre Threads), herramientas nativas y de terceros, criterios de ocultar/borrar/responder, impacto (real y supuesto) en rendimiento, y uso comercial de comentarios (comment-to-DM).

## TL;DR

- **Los comentarios del anuncio viven en un post** (el post existente promocionado o el post no publicado que crea el anuncio). Si escalas con post ID, todos los anuncios comparten los mismos comentarios: la moderación es más fácil y más crítica. [EMPIRICAL]
- **Ocultar > borrar en casi todos los casos:** el comentario oculto sigue visible para su autor (y sus amigos en Facebook), no se le notifica y evita el "efecto Streisand"; borrar es para contenido ilegal, datos personales, estafas o amenazas. [STRONG INFERENCE] (comportamiento documentado por Instagram/FB y vendors)
- **Afirmaciones de que ocultar "no penaliza la entrega" o que borrar "quita señal de engagement" no están respaldadas por Meta.** Lo que sí está documentado: el *quality ranking* usa feedback sobre el anuncio (p. ej. ocultarlo/reportarlo) y la experiencia posterior al clic; no hay documentación pública sobre el peso del sentimiento de los comentarios. [CONTESTED]
- **Herramientas nativas:** gestión desde Ads Manager (ocultar/reportar; borrar desde "See post"), bandeja de Meta Business Suite, filtros de palabras/profanidad de la Página, **Hidden Words** en Instagram (lista personalizada), bloqueo/restricción de usuarios. **Moderation Assist** de Business Suite **no funciona en anuncios pagados** según Agorapulse. [OFFICIAL META] (Hidden Words) + [STRONG INFERENCE] (resto)
- **Desactivar comentarios en anuncios existe pero en disponibilidad limitada** (inventory filter "Public / No one" en anuncios de feed desde oct-2024, "limited number of businesses"). No es recomendable por defecto: los comentarios son FAQ pública, prueba social y fuente de leads. [OFFICIAL META] (anuncio del test) + [STRONG INFERENCE] (recomendación)
- **Los comentarios son un canal de venta:** responde preguntas de intención en público + DM (private reply). En Instagram, Meta prueba "Reply to Keywords" (auto-DM por keyword en anuncios, ago-2026). [EMPIRICAL]
- **SLA operativo recomendado:** revisión de comentarios de anuncios activos ≥2 veces/día en cuentas con gasto relevante; spam/estafas ocultados en <2 h; preguntas de intención respondidas en <1 h en horario comercial. [HYPOTHESIS] (estándar propio)

## 1. Dónde aparecen y cómo se gestionan

| Situación | Dónde se acumulan los comentarios | Quién modera |
|---|---|---|
| Anuncio nuevo (dark post) | Post no publicado de la Página/IG creado por el anuncio | Marca |
| Anuncio con post existente / post ID | El post original (visible también en orgánico) | Marca |
| Partnership ad con post del creador | Post del creador | Creador (y marca si tiene acceso); acordarlo por contrato |
| Partnership ad con contenido subido por la marca (identidad del creador) | Post no publicado asociado | Verificar acceso; acordarlo |
| Threads ad | Hilo del anuncio | Marca (documentación escasa) |

**Rutas de moderación nativas** [STRONG INFERENCE] (guías de terceros; Meta no ofrece una página única 2026 accesible):
- **Ads Manager**: editar anuncio → "More options" → "Manage Facebook comments" / "Manage Instagram comments" → ocultar o reportar. Para borrar, abrir el post ("See post").
- **Meta Business Suite**: la bandeja unifica comentarios de anuncios y orgánicos de FB e IG; permite responder, ocultar, borrar y mover a DM.
- **Página de Facebook**: filtro de profanidad y palabras bloqueadas; según terceros también aplican a anuncios de esa Página.
- **Instagram**: Hidden Words (filtro de comentarios ofensivos, filtrado avanzado, lista personalizada de palabras/frases/emojis que oculta comentarios y solicitudes de mensaje), restringir y bloquear cuentas, acciones en lote (hasta ~25 comentarios por lote según terceros). [OFFICIAL META] ([Help Center](https://help.instagram.com/iphone-app/700284123459336))
- **API (Graph)**: ocultar/mostrar y borrar comentarios programáticamente; base de las herramientas de terceros.
- **Moderation Assist (Business Suite)**: oculta por criterios (perfil sin foto, cuenta nueva, links, imágenes, keywords) pero "does not work on paid ads". [STRONG INFERENCE] ([Agorapulse](https://agorapulse.com/social-media-lab/facebook-ad-comments-test))

## 2. Desactivar comentarios: estado y criterio

- **Estado**: Meta anunció en octubre de 2024 un control para desactivar comentarios en anuncios de feed (filtro de inventario en el ad set: "Public" por defecto / "No one"), disponible para "a limited number of businesses". No he encontrado anuncio de disponibilidad general en 2025–2026; varias guías 2026 dicen que el toggle aparece en algunas cuentas y no en otras. [OFFICIAL META] (test) + [CONTESTED] (alcance actual) ([PPC Land](https://ppc.land/meta-introduces-comment-controls-for-facebook-and-instagram-advertisers/), [eMarketer](https://www.emarketer.com/content/meta-strengthens-brand-safety-with-new-ad-controls-comment-muting-tools))
- **Las restricciones de comentarios del post orgánico no se trasladan al anuncio.** [STRONG INFERENCE]
- **Cuándo tiene sentido desactivar** [STRONG INFERENCE]: categorías con ataques coordinados o riesgo reputacional alto (política, salud sensible, crisis), anuncios de marca que no buscan conversación, campañas con mucho spam de estafas imposibles de moderar a tiempo.
- **Cuándo no**: lead gen y ventas consultivas (los comentarios son preguntas de intención), ecommerce con FAQ (talla, envío), partnership ads (el contexto social es parte del valor).

## 3. Ocultar vs borrar vs responder: matriz de decisión

| Tipo de comentario | Acción | Por qué |
|---|---|---|
| Spam, bots, links a estafas, suplantación de la marca | **Ocultar** (y reportar/bloquear si es estafa o suplantación) | Protege a usuarios; ocultar no alerta al spammer |
| Insultos, odio, acoso | **Ocultar** + bloquear/restringir; **borrar** si es ilegal o amenaza | Brand safety; cumplimiento |
| Datos personales (teléfono, dirección, datos de salud) | **Borrar** y contactar por DM | Privacidad |
| Pregunta de intención ("¿precio?", "¿hacéis envíos a…?") | **Responder en público** (breve) + DM o private reply | Es FAQ pública y lead |
| Queja legítima (pedido, servicio) | **Responder en público** con empatía y mover a DM; no ocultar salvo insultos | Ocultar quejas legítimas se percibe como censura si se nota |
| Crítica de producto argumentada | Responder con datos; no borrar | Credibilidad |
| Comentario de competidor / link a competidor | Ocultar | — |
| Testimonio positivo | "Me gusta" + respuesta breve; fijarlo si la superficie lo permite | Prueba social |
| Keyword de comment-to-DM ("GUÍA") | Automatizar DM; opcional respuesta pública "¡Enviado por DM!" | Conversión; señal de respuesta visible |

[STRONG INFERENCE]; prácticas consistentes entre agencias y vendors, sin estudio controlado público.

## 4. ¿Afectan los comentarios al rendimiento?

| Afirmación | Evidencia | Estado |
|---|---|---|
| Comentarios positivos aumentan el CTR | Test de Agorapulse citado por vendors (comentarios positivos → mayor CTR significativo; comentarios vs sin comentarios no significativo) — no he podido leer el informe original | [CONTESTED] |
| Ocultar comentarios dañinos mejora ROAS y CPA | Estudio de campo HBS (De Freitas et al.) citado por vendors: ROAS 0,459→0,678; intención de compra 36,9→47,2 al ocultar; responder sin efecto significativo. No localizado el paper original | [HYPOTHESIS] hasta verificar |
| Ocultar "no afecta a la entrega" / borrar "quita señal" | Afirmaciones de vendors sin documento de Meta | [UNPROVEN] |
| El feedback negativo sobre el anuncio (ocultar anuncio, reportar) penaliza | Meta documenta que el quality ranking usa feedback sobre el anuncio y experiencia post-clic | [OFFICIAL META] (concepto general de ad quality) |
| La prueba social (muchos comentarios) es imprescindible | Loomer abr-2026: anuncio nuevo sin prueba social rinde igual (n=1) | [CONTESTED] (ver `07-…`) |

**Postura de trabajo** [STRONG INFERENCE]: moderar por **experiencia del usuario y protección de la marca**, no por supuestos efectos algorítmicos. Un hilo lleno de estafas o insultos reduce la confianza de quien lee; eso sí afecta a conversión.

## 5. Comentarios como canal de conversión

- **Respuesta pública + privada**: en FB e IG, responder a una pregunta en público y enviar private reply (1 por comentario, ≤7 días en IG) para continuar en DM. [OFFICIAL META] (private replies)
- **Reply to Keywords (test, ago-2026)**: auto-DM nativo para comentarios con keywords en anuncios de Instagram (hasta 5 keywords, un único mensaje). [EMPIRICAL] ([Loomer](https://www.jonloomer.com/reply-to-keywords-meta-ads-feature/))
- **Business Agent / herramientas**: pueden responder automáticamente comentarios/DMs; vigilar el tono y los errores de IA en público. [STRONG INFERENCE]
- **Señal de intención para optimización**: los comentarios no se envían como evento de conversión; si un comentario se convierte en lead en DM, envía el evento por CAPI (ver `12-…`).

## 6. Herramientas de terceros (cuándo merecen la pena)

| Necesidad | Nativo suficiente | Tercero recomendable |
|---|---|---|
| <50 comentarios/día, 1–2 cuentas | Sí (Business Suite + Hidden Words) | — |
| Muchos anuncios/cuentas, spam constante, horario 24/7 | Parcial | NapoleonCat, Agorapulse, BrandBastion, Replient, CommentGuard u otros con auto-ocultado por IA |
| Analítica de sentimiento por anuncio | No | Herramientas que cruzan comentarios con gasto/CPM |
| Partnership ads con muchos creadores | No | Herramientas con acceso delegado o acuerdos con creadores |

Ninguna recomendación de proveedor concreto está validada con datos independientes. [HYPOTHESIS]. Umbral de vendor citado: >20.000 $/mes de gasto en Meta (sin fuente). [UNPROVEN]

## 7. Procedimiento operativo estándar (SOP)

1. **Antes de lanzar**: Hidden Words y lista de palabras bloqueadas (insultos, "estafa", palabras de spam habituales, nombres de competidores), FAQ de respuestas aprobadas, responsables y horarios.
2. **Lanzamiento**: revisar comentarios a las 2 h y 24 h del primer anuncio de cada post.
3. **Rutina**: 2 revisiones diarias (mañana/tarde); en picos (lanzamientos, rebajas), cada 1–2 h.
4. **Escalado**: amenazas, temas legales o de salud → responsable de marca/legal.
5. **Registro**: anotar preguntas repetidas → nuevas creatividades/landing que las respondan (los comentarios son research gratis).
6. **Mensual**: revisar si algún anuncio acumula sentimiento negativo y si conviene rotar creativo o cambiar de post ID.

## Implicaciones operativas

- Escalar con post ID obliga a tener moderación diaria: un único hilo concentra toda la conversación.
- Incluir en contratos de creadores quién modera los partnership ads.
- No usar "desactivar comentarios" como solución por defecto; reservarlo para riesgo reputacional.

## Errores frecuentes

- Borrar críticas legítimas (se nota y genera más críticas).
- Dejar comentarios de estafas ("escríbeme por WhatsApp a este número") en anuncios de marca: riesgo para los usuarios y para la reputación.
- Responder con plantillas idénticas que parecen bots.
- No mirar los comentarios de los partnership ads porque "están en el perfil del creador".
- Asumir que Moderation Assist cubre los anuncios.

## Preguntas abiertas

- ¿Comment controls (desactivar comentarios) está ya disponible de forma general en 2026? Evidencia contradictoria.
- Paper original del estudio HBS sobre moderación y ROAS: pendiente de localizar y validar.
- Moderación de comentarios en anuncios de Threads: documentación escasa.

## Fuentes clave

- [Meta introduces comment controls for Facebook and Instagram advertisers](https://ppc.land/meta-introduces-comment-controls-for-facebook-and-instagram-advertisers/) — 2024-10 — prensa
- [Meta strengthens brand safety with new ad controls, comment muting tools](https://www.emarketer.com/content/meta-strengthens-brand-safety-with-new-ad-controls-comment-muting-tools) — 2024-10 — prensa
- [Instagram Help: Hidden Words / comment filters](https://help.instagram.com/iphone-app/700284123459336) — vigente — meta-oficial
- [Agorapulse: Facebook comments / Moderation Assist](https://agorapulse.com/social-media-lab/facebook-ad-comments-test) — s.f. — vendor
- [Private Replies – Instagram Platform](https://developers.facebook.com/docs/instagram-platform/private-replies) — vigente — meta-developers
- [Reply to Keywords Meta Ads Feature](https://www.jonloomer.com/reply-to-keywords-meta-ads-feature/) — 2026-08-25 — practitioner
- [Jetfuel: spam comments and Meta ads 2026](https://jetfuel.agency/meta-ads-spam-comments-algorithm-2026/) — 2026 — agencia (baja confianza)
- [Social proof might not matter after all](https://pubcast.jonloomer.com/social-proof-might-not-matter-after-all/) — 2026-04-06 — youtube/podcast
