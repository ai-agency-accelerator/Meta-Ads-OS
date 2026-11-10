# Mapa completo de placements de Meta (estado octubre 2026)

> Última verificación: 2026-10-15 · Autor: A07 (agente) · Ámbito: inventario de placements de Facebook, Instagram, Threads, Messenger, WhatsApp y Audience Network; qué existe, qué se ha retirado en 2025–2026, comportamiento del usuario y diferencias creativas. Specs detalladas en `03-specs-safe-zones-formatos.md`; decisión de incluir/excluir en `02-advantage-placements-y-exclusiones.md`.

## TL;DR

- **El inventario "vivo" en API (oct-2026) tiene ~25 posiciones** repartidas en 6 plataformas: Facebook (11), Instagram (8), Messenger (2, ambas en retirada), Audience Network (2), Threads (1) y WhatsApp (1: Status). [OFFICIAL META] ([placement targeting reference](https://developers.facebook.com/docs/marketing-api/audiences/reference/placement-targeting))
- **Retiradas recientes que debes asumir como hechas:** Messenger inbox (11-nov-2025), Messenger Stories (27-ago-2026; API en todas las versiones 27-oct-2026), Sponsored Messages (jun-2024). Messenger sigue existiendo como **destino** de anuncios (click-to-Messenger), no como superficie de inventario relevante. [STRONG INFERENCE] (avisos de Meta a anunciantes recogidos por agencias; la referencia de API todavía lista `messenger story` y `sponsored_messages`, desfasada).
- **Altas recientes:** Threads Feed (global para anunciantes abr-2025, para todos los usuarios desde ene-2026, sin necesidad de cuenta IG desde sep-2026) y WhatsApp Status en la pestaña Updates (anunciado 16-jun-2025, rollout global feb–mar 2026). [OFFICIAL META] para los anuncios; fechas de rollout [STRONG INFERENCE].
- **En la API, Threads (`threads_stream`) exige seleccionar Instagram Feed y WhatsApp Status exige seleccionar Instagram Stories**: no son placements "independientes" a efectos de configuración manual. [OFFICIAL META]
- **El consumo se ha desplazado a vídeo vertical a pantalla completa** (Reels/Stories/Status). Meta incluso prueba desde finales de 2026 un Facebook que abre directamente en vídeo, con el Feed como segunda pestaña. Diseña primero para 9:16 y adapta a 4:5, no al revés. [OFFICIAL META] (anuncio del test 24-jul-2026) + [STRONG INFERENCE] (implicación creativa).
- **Las superficies de "intención" (búsqueda en FB/IG, Marketplace, Explore) tienen poco volumen pero usuarios en modo exploración/compra**; las superficies de "pasatiempo" (Reels, Stories, Status) tienen volumen enorme y CPM bajos, con mucha atención efímera. No se compran por separado: el sistema las mezcla. [STRONG INFERENCE]
- **Audience Network sigue existiendo (classic y rewarded video)** y es la fuente principal de resultados "baratos pero falsos" cuando el objetivo es clic, LPV o ThruPlay. En objetivos de conversión casi no gasta. [EMPIRICAL] (Jon Loomer, 2024–2026).
- **Placements emergentes/de pago "premium":** Reels trending ads (junto al top 5 % de Reels de creadores, self-serve desde nov-2025 para anunciantes con rep), Instagram Live partnership ads (GA anunciada 29-sep-2026). [OFFICIAL META]/[STRONG INFERENCE]

## 1. Cómo organiza Meta el inventario

En Ads Manager los placements se agrupan por "familias" (Feeds; Stories, Status y Reels; In-stream; Search results; Messages; Apps and sites). En la API, cada plataforma tiene su lista de posiciones. La lista vigente según la referencia de Marketing API consultada el 2026-10-15:

| Plataforma (`publisher_platforms`) | Posiciones (código API) | Notas de dependencia |
|---|---|---|
| `facebook` | `feed`, `right_hand_column`, `marketplace`, `video_feeds`, `story`, `search`, `instream_video`, `facebook_reels`, `facebook_reels_overlay`, `profile_feed`, `notification` | `marketplace`, `search`, `profile_feed` y `notification` requieren `feed`; `story` requiere otro placement; `right_hand_column` solo imagen/vídeo/carrusel y ciertos objetivos |
| `instagram` | `stream` (Feed), `story`, `explore`, `explore_home`, `reels`, `profile_feed`, `ig_search`, `profile_reels` | — |
| `threads` | `threads_stream` | Requiere Instagram `stream` |
| WhatsApp | `status` | Requiere Instagram `story` |
| `messenger` | `sponsored_messages`, `story` | Ambas retiradas/en retirada (ver §6) |
| `audience_network` | `classic`, `rewarded_video` | — |

Fuente: [Placement targeting reference](https://developers.facebook.com/docs/marketing-api/audiences/reference/placement-targeting) [OFFICIAL META]. La propia página advierte de que Meta "may also automatically consider new positions or platforms as they become available". **Trampa:** esta referencia no está sincronizada con las retiradas (sigue listando Messenger Stories y Sponsored Messages). Usa Ads Manager y los avisos de cuenta como verdad operativa.

## 2. Tabla maestra: superficie → mentalidad → creatividad

Columna "mentalidad" = razonamiento desde primeros principios sobre qué está haciendo el usuario cuando ve el anuncio; no es dato de Meta salvo que se indique. [STRONG INFERENCE] salvo indicación.

| Superficie | Qué es | Mentalidad del usuario | Ratio principal | Qué funciona creativamente | Estado 2026 |
|---|---|---|---|---|---|
| **Facebook Feed** | Anuncio entre publicaciones del feed principal | Scroll mixto (amigos, grupos, páginas, vídeo recomendado); público de más edad | 4:5 (imagen y vídeo) | Copy más largo funciona; prueba social (comentarios/likes) visible; vídeo nativo con subtítulos | Vigente. Test de "Facebook video-first" (Feed como 2.ª pestaña) desde finales de 2026 fuera de EE. UU. |
| **Facebook Profile Feed** | Anuncio dentro del feed de un perfil/página que el usuario visita | Navegación dirigida (mira a alguien concreto) | 4:5 | Igual que Feed; poco volumen | Vigente; requiere `feed` |
| **Facebook Video Feeds** | Feeds de solo vídeo (pestaña Vídeo) | Lean-back, consumo de vídeo | 4:5 / 9:16 según superficie | Vídeo nativo con hook | Vigente |
| **Facebook Marketplace** | Anuncio en la home y resultados de Marketplace | Intención de compra/compraventa local | 1:1–4:5 | Producto claro, precio, oferta; estética "listing" | Vigente; requiere `feed` |
| **Facebook Search results** | Anuncios en resultados de búsqueda de Facebook | Búsqueda activa | 1:1 | Mensaje directo, relevancia con la consulta (sin keywords: la segmentación no es por búsqueda) | Vigente, poco volumen |
| **Facebook Notifications** | Anuncio en la pestaña de notificaciones | Revisión de actividad propia | — | Muy poco inventario; no verificado su volumen real | Listado en API; requiere `feed`. No verificado en 2026 cuánto entrega |
| **Facebook Right column** | Columna derecha en escritorio | Escritorio, baja atención | 1:1 (aunque Meta pide 1.91:1) | Imagen simple, retargeting | Vigente; residual |
| **Facebook Stories** | Entre Stories de amigos/páginas | Toque rápido, efímero | 9:16 | Primeros 1–2 s; texto dentro de safe zone | Vigente |
| **Facebook Reels** | Anuncio a pantalla completa entre Reels | Entretenimiento, swipe | 9:16 | Nativo "creator-style", sonido, hook visual | Vigente; CPM muy bajos en awareness |
| **Ads on Facebook Reels (overlay / post-loop)** | Banner o sticker superpuesto a Reels de creadores; post-loop al final | Atención en el contenido del creador, no en el anuncio | Cuadrado pequeño (banner ~30 caracteres) | Logo + mensaje mínimo; no es un formato de respuesta directa | Sigue en API (`facebook_reels_overlay`). Meta no ha anunciado su retirada; poca documentación 2025–2026 [STRONG INFERENCE] |
| **Facebook In-stream** | Anuncio dentro de vídeos largos (mid-roll) | Vídeo largo con sonido | 16:9 / 4:5 | Funciona como TV: marca y recuerdo | Vigente |
| **Instagram Feed (`stream`)** | Entre publicaciones del feed | Scroll social y de creadores | 4:5 (el grid de perfil se ve 3:4 desde ene-2025) | Estética cuidada pero nativa; carruseles | Vigente |
| **Instagram Profile feed** | Anuncio en el feed que aparece al entrar en un perfil y hacer scroll | Curiosidad por una cuenta concreta | 4:5 | — | Vigente (desde 2022) |
| **Instagram Explore** | Feed que se abre al tocar un contenido de Explorar | Descubrimiento | 4:5 | Contenido que "parece Explore" (interés, novedad) | Vigente |
| **Instagram Explore home** | Tiles en la propia cuadrícula de Explorar | Descubrimiento, primera impresión en miniatura | 4:5 o 9:16 (miniatura recortada) | La miniatura es el anuncio: legible en pequeño | Vigente (desde oct/nov-2022) |
| **Instagram Search results (`ig_search`)** | Anuncios en el feed al que se entra desde un resultado de búsqueda (no en la cuadrícula) | Búsqueda/exploración | 4:5 | — | Vigente (desde mayo-2023) |
| **Instagram Stories** | Entre Stories | Toque rápido; también reacción por DM | 9:16 | Stickers/encuestas no aplican a anuncios; hook en 1 s; CTA "Enviar mensaje" funciona bien para DM | Vigente |
| **Instagram Reels** | Entre Reels (pestaña Reels y Reels en Feed/Explore) | Entretenimiento, sonido encendido | 9:16 | Estilo creador/UGC; subtítulos; nada en el 35 % inferior | Vigente; principal superficie de crecimiento |
| **Instagram Profile reels** | Anuncio entre Reels de un perfil | Navegación dirigida por una cuenta | 9:16 | — | Vigente |
| **Threads Feed** | Entre publicaciones de Threads | Lectura de texto, conversación, tono informal | 4:5 o 1:1 (imagen/vídeo/carrusel/catálogo) | Copy conversacional; no hashtags/URLs en texto | Global usuarios ene-2026; solo móvil |
| **WhatsApp Status (Updates)** | Anuncio entre Status de contactos/canales | Pasatiempo breve, contexto privado | 9:16 | Vertical, mensaje simple; CTA a chat de WhatsApp o web | Anunciado jun-2025; global feb–mar 2026; segmentación limitada |
| **Audience Network classic** | Banners, nativos, intersticiales en apps de terceros | Ajeno a Meta; mucho clic accidental | Varios | Solo con objetivos de conversión y control de calidad | Vigente |
| **Audience Network rewarded video** | Vídeo que el usuario ve a cambio de premio en una app/juego | Incentivado, sin interés real | 9:16 / 16:9 | Inflará ThruPlays | Vigente |
| **Messenger inbox** | Anuncio en la bandeja de Messenger | — | — | — | **Retirado 11-nov-2025** |
| **Messenger Stories** | Entre Stories de Messenger | — | — | — | **Retirado 27-ago-2026** |
| **Sponsored messages** | Mensaje patrocinado a quien ya conversó con la página | — | — | — | **Retirado jun-2024** (sustitutos: marketing messages de pago) |

Fuentes clave de la tabla: [placement reference](https://developers.facebook.com/docs/marketing-api/audiences/reference/placement-targeting), [Instagram Reels Ads Guide](https://www.facebook.com/business/ads-guide/update/video/instagram-reels), [TechCrunch Threads 21-ene-2026](https://techcrunch.com/2026/01/21/threads-rolls-out-ads-to-all-users-worldwide), [Meta Newsroom WhatsApp 16-jun-2025](https://about.fb.com/news/2025/06/helping-you-find-more-channels-businesses-on-whatsapp/), [TechCrunch IG search ads 2023](https://techcrunch.com/2023/05/25/instagram-ads-search-results-via-marketing-api/), [SEJ Explore home 2022](https://searchenginejournal.com/meta-announces-instagram-explore-home-ads-placement-via-marketing-api/471006), [Jon Loomer ratios](https://www.jonloomer.com/recommended-aspect-ratios-by-placement-for-meta-ad-creative/).

## 3. Facebook en detalle

**Feed sigue siendo el placement "universal" pero ya no es la puerta de entrada.** El 24-jul-2026 Meta anunció (Tom Alison, head of Facebook) un test en el que Facebook abre en vídeo a pantalla completa y el Feed clásico pasa a una segunda pestaña, empezando "later this year" en países "video-heavy" no nombrados y quizá en EE. UU. en 2027. El post no incluía novedades publicitarias. [OFFICIAL META] vía [PPC Land](https://ppc.land/meta-drops-facebook-feed-to-second-tab-in-full-screen-video-test/).
Implicación: si tu cuenta depende de creatividades 1:1/4:5 estáticas, en los mercados del test verás más inventario de vídeo vertical que de feed. [HYPOTHESIS] hasta que haya datos.

**Reels de Facebook:** Jon Loomer documentó una campaña de awareness en EE. UU. donde el 99 % de las impresiones fue a "Ads on Facebook Reels" con CPM de 0,22 $ (overlay/post-loop), es decir, el sistema optimiza literalmente a la métrica pedida y encuentra la impresión más barata. [EMPIRICAL] ([Loomer, 25-ago-2025](https://www.jonloomer.com/spot-problematic-meta-ad-placements/)). Si tu objetivo es alcance "de calidad", revisa el breakdown antes de celebrar el CPM.

**Marketplace, búsqueda, notificaciones y profile feed** son placements "satélite" del Feed (en API dependen de `feed`). Aportan poco volumen; no tiene sentido optimizar creatividades específicas para ellos salvo Marketplace en ecommerce/local con producto claro. [STRONG INFERENCE]

**Right column** es escritorio puro; Meta pide 1.91:1 al subir pero recomienda 1:1. Volumen marginal en 2026 porque la mayoría del consumo es móvil. [STRONG INFERENCE] + [EMPIRICAL] (Loomer sobre ratios).

## 4. Instagram en detalle

Ver `04-instagram-a-fondo.md` para la estrategia. Resumen de superficies:

- **Feed (`stream`)**: el grid de perfil pasó a mostrarse 3:4 en enero de 2025, pero el feed sigue mostrando 4:5. Los anuncios no se ven en el grid, así que para anuncios 4:5 sigue siendo el estándar. [EMPIRICAL] (guías de terceros coinciden; Meta no ha publicado nota específica para ads).
- **Stories**: 9:16. Muy buen placement para CTA de mensaje (click-to-Instagram Direct) porque el gesto de "responder" ya es nativo. [STRONG INFERENCE]
- **Reels**: 9:16, especificación oficial 1440×2560 recomendada, duración hasta 15 min en la guía de anuncios, safe zone 14 % arriba / 35 % abajo / 6 % lados. [OFFICIAL META] ([Ads Guide](https://www.facebook.com/business/ads-guide/update/video/instagram-reels)). Meta afirma que los Reels acumulan 4.500 millones de reshares diarios (NewFronts 2025). [OFFICIAL META]
- **Explore / Explore home**: Explore home muestra el anuncio como tile 2×2 en la cuadrícula; el anuncio "vive" de la miniatura. [OFFICIAL META] (anuncio 2022).
- **Search results**: el anuncio aparece en el feed al que se entra tras tocar un resultado, no en la cuadrícula de resultados. No hay segmentación por palabra clave. [OFFICIAL META] (2023).
- **Profile feed / profile reels**: inventario que aparece cuando el usuario navega dentro de un perfil ajeno. Bajo volumen, alta atención. [STRONG INFERENCE]
- **Ad breaks (test 2024)**: Instagram probó "ad breaks" no saltables con cuenta atrás en junio de 2024; no he encontrado confirmación de despliegue en 2025–2026. [OUTDATED/no verificado]

## 5. Threads

- Cronología: test en EE. UU. y Japón (24-ene-2025) → abierto a anunciantes globales (23-abr-2025) → vídeo en test (NewFronts may-2025) → carrusel (6-oct-2025) → Advantage+ catalog (28-oct-2025) → anuncios a todos los usuarios del mundo (anuncio 21-ene-2026, rollout desde la semana del 26-ene, entrega inicial "low") → sin necesidad de cuenta de Instagram (sep-2026, gradual). [OFFICIAL META] para anuncios principales; algunas fechas intermedias vía [Postory](https://postory.io/blog/meta-threads-ads) [STRONG INFERENCE].
- Formatos: imagen, vídeo, carrusel, catálogo, app; 4:5 recomendado. Solo Threads Feed (no búsqueda ni DMs). Solo móvil. Sin lead forms nativos según guías de terceros. [STRONG INFERENCE]
- Detalle completo en `09-threads-ads.md`.

## 6. Messenger: de placement a destino

- **Sponsored messages**: Meta desactivó las campañas desde el 1-jun-2024 y la creación vía API desde v20. [OFFICIAL META] (citado por [Jon Loomer](https://www.jonloomer.com/qvt/meta-to-deprecate-sponsored-messages/)).
- **Messenger inbox**: retirado el 11-nov-2025; las campañas siguieron sin esa opción, incluidas las que usaban Advantage+ placements. [STRONG INFERENCE] (Embryo, SocialBee, DataSlayer; sin página pública de Meta encontrada).
- **Messenger Stories**: retirado el 27-ago-2026; deprecación en todas las versiones de Graph API el 27-oct-2026; el presupuesto se redistribuye automáticamente. [STRONG INFERENCE] (avisos de Meta a anunciantes según PROHED, AdsUploader, Common Thread).
- **Lo que queda**: Messenger como **destino** (click-to-Messenger, Messenger lead ads con plantilla de chat automatizado, click-to-subscribe para marketing messages). Ver `10-messenger-ads.md`.
- Contexto de producto: Meta cerró las apps de escritorio de Messenger en oct-2025 y messenger.com en abril de 2026 (redirige a facebook.com/messages). [OFFICIAL META] vía [TechCrunch 19-feb-2026](https://www.techcrunch.com/2026/02/19/meta-is-shutting-down-messengers-standalone-website/). Señal estratégica: Messenger se repliega dentro de Facebook.

## 7. WhatsApp: Status (Updates tab) y canales promocionados

- **Status ads**: anuncios entre los Status en la pestaña Updates, desde los que el usuario puede iniciar un chat con la empresa. Anunciado el 16-jun-2025 junto con canales promocionados y suscripciones a canales; Updates tab = 1.500 millones de usuarios diarios según Meta. [OFFICIAL META] ([Newsroom](https://about.fb.com/news/2025/06/helping-you-find-more-channels-businesses-on-whatsapp/))
- **Segmentación limitada** por diseño: país/ciudad, idioma, canales seguidos, interacción con anuncios; si el usuario vinculó WhatsApp al Accounts Center, también preferencias y datos de otras apps de Meta. Mensajes, llamadas y grupos personales no se usan. [OFFICIAL META]
- **Rollout global**: feb–mar 2026, con controles para ocultar/bloquear anuncios de empresas concretas y, en algunas regiones, opción de suscripción sin anuncios. [STRONG INFERENCE] (prensa: Storyboard18, The Keyword).
- **Configuración**: en API `status` requiere Instagram `story`; en Ads Manager se gestiona como un placement más del grupo Stories/Status. [OFFICIAL META]
- **Canales promocionados**: pago por aparecer en el directorio de canales; mide seguidores. Seguir un canal **no** da permiso para enviar mensajes privados de marketing. [STRONG INFERENCE] ([YCloud](https://www.ycloud.com/blog/whatsapp-status-ads))
- Detalle en `11-whatsapp-ads-ctwa.md`.

## 8. Audience Network

- Dos posiciones: `classic` (banner, nativo, intersticial) y `rewarded_video`. [OFFICIAL META]
- Comportamiento: el anunciante no compra "apps de calidad"; compra impresiones en apps de terceros donde abundan clics accidentales e incentivados. Cuando el objetivo es clic/LPV/ThruPlay, el sistema puede concentrar gasto ahí y producir métricas imposibles (más ThruPlays que alcance). [EMPIRICAL] ([Loomer](https://www.jonloomer.com/spot-problematic-meta-ad-placements/)).
- En objetivos de conversión (compra, lead con evento de calidad) suele gastar poco porque no convierte; la discusión de excluirlo es de matiz. Ver `02-advantage-placements-y-exclusiones.md`.

## 9. Superficies "premium" y nuevas (2025–2026)

| Producto | Qué es | Estado | Evidencia |
|---|---|---|---|
| **Reels trending ads** | Anuncios junto al top 5 % de Reels de creadores (ranking diario por vistas, engagement, viralidad, brand safety, calidad); por tema (belleza, moda, coches, deportes, mascotas…) | Test abr-2025 → self-serve en Ads Manager desde nov-2025 para anunciantes con rep de Meta; más lineups de momentos (Fashion Week, F1, Black Friday, NFL) | Meta: +20 % unaided awareness en tests (vs YouTube Select +20 %, TikTok Pulse +14 %) [OFFICIAL META vía prensa] |
| **Instagram Live partnership ads** | Promocionar como partnership ad el directo de un creador | GA anunciada 29-sep-2026; algunos lo ven aún como beta el 15-oct | [OFFICIAL META] vía [Marketing Dive](https://www.marketingdive.com/news/meta-streamlines-creator-brand-tie-ups-with-new-marketing-hub/830593/) |
| **Facebook Live partnership ads** | Igual en Facebook | Test may-2025, ya disponible en 2026 según Marketing Dive | [OFFICIAL META] |
| **Threads (vídeo y carrusel)** | — | Global | Ver §5 |
| **WhatsApp Status** | — | Global 2026 | Ver §7 |

## 10. Cómo leer la "intención" por superficie (marco de decisión)

Razonamiento de primeros principios [STRONG INFERENCE]:

1. **Contexto de sesión**: Reels/Stories/Status = sesión de entretenimiento → el anuncio compite con contenido de creadores; si no parece contenido, se salta en <1 s. Feed/Threads = scroll con lectura → admite más texto. Search/Marketplace/Explore = exploración → admite mensajes de producto directos.
2. **Coste marginal de la acción**: en Stories/Reels el gesto de "responder/enviar mensaje" está a un toque; por eso los anuncios de mensaje (CTM/CTWA/IG Direct) suelen encajar con placements verticales. En Audience Network el gesto de clic es accidental.
3. **Calidad de la señal**: el sistema optimiza a lo que pides. Si pides clics, encontrará el clic más barato (a menudo Audience Network o overlays). Si pides compras/leads cualificados, la diferencia entre placements la arbitra el propio modelo.
4. **Creatividad por superficie**: no se trata de hacer 15 piezas distintas, sino de 2–3 formatos maestros (9:16, 4:5, 1:1) bien hechos y con safe zones, más personalización de assets por placement cuando hay conflicto (Facebook Feed 4:5, Facebook Reels 9:16).

## Implicaciones operativas

- **Por defecto**: Advantage+ placements con creatividades 9:16 + 4:5 (+1:1 si hay catálogo/right column). Revisar breakdown semanal.
- **Retirar de tus checklists y plantillas**: Messenger inbox, Messenger Stories, Sponsored messages. Si una plantilla de cliente o un script de API aún los referencia, corrígelo antes del 27-oct-2026.
- **Añadir a la checklist**: Threads Feed y WhatsApp Status (ambos activados por defecto con Advantage+ placements donde estén disponibles). Revisar que la identidad (perfil de Threads, número/negocio WhatsApp) esté correcta.
- **Reservar presupuesto de prueba** para Reels trending ads solo si hay objetivo de marca y acceso vía rep.
- **Umbral de alerta**: si un placement concentra >60–70 % del gasto con coste por resultado <50 % de la media y el objetivo es TOFU, investiga calidad antes de escalar. [HYPOTHESIS] (umbral propio, no de Meta).

## Errores frecuentes

- Diseñar en 1:1 y "dejar que Meta recorte" a 9:16: el texto acaba bajo la UI de Reels.
- Pensar que "Search results" de Meta es búsqueda por keyword tipo Google: no hay pujas por términos.
- Leer el CPM de Facebook Reels overlay como "awareness barato" sin mirar calidad de atención.
- Seguir referenciando Messenger Stories/Inbox en APIs o informes.
- Creer que WhatsApp Status permite la segmentación granular de Facebook/Instagram: es limitada por diseño de privacidad.

## Preguntas abiertas

- ¿Cuánto inventario real entregan `notification` (Facebook) y `profile_reels` (Instagram)? No hay datos públicos.
- ¿Facebook Reels overlay/post-loop seguirá existiendo tras el test "video-first"? Sin comunicación de Meta.
- ¿El test de Facebook video-first cambiará la mezcla de placements en Advantage+ en los países del test? Por medir.
- ¿Disponibilidad exacta de WhatsApp Status ads por país (UE incluida)? No hay lista oficial pública.

## Fuentes clave

- [Placement targeting reference](https://developers.facebook.com/docs/marketing-api/audiences/reference/placement-targeting) — vigente 2026 — meta-developers
- [Meta Ads Guide: Instagram Reels](https://www.facebook.com/business/ads-guide/update/video/instagram-reels) — vigente 2026 — meta-oficial
- [Threads rolls out ads to all users worldwide](https://techcrunch.com/2026/01/21/threads-rolls-out-ads-to-all-users-worldwide) — 2026-01-21 — prensa
- [Helping You Find More Channels and Businesses on WhatsApp](https://about.fb.com/news/2025/06/helping-you-find-more-channels-businesses-on-whatsapp/) — 2025-06-16 — meta-oficial
- [Meta at IAB NewFronts 2025](https://www.facebook.com/business/news/meta-at-iab-newfronts-2025) — 2025-05-08 — meta-oficial
- [How to Spot Problematic Meta Ad Placements](https://www.jonloomer.com/spot-problematic-meta-ad-placements/) — 2025-08-25 — practitioner
- [Meta drops Facebook Feed to second tab in full-screen video test](https://ppc.land/meta-drops-facebook-feed-to-second-tab-in-full-screen-video-test/) — 2026-07 — prensa
- [Meta Update v26.0: Instagram & Messenger Ads Change](https://www.prohed.com/blog/meta-update-v26-instagram-messenger-ads/) — 2026-08-20 — agencia
- [Meta is shutting down Messenger's standalone website](https://www.techcrunch.com/2026/02/19/meta-is-shutting-down-messengers-standalone-website/) — 2026-02-19 — prensa
- [Reels trending ads broader rollout](https://www.socialsamosa.com/news-2/meta-broader-rollout-reels-trending-ads-with-ad-features-10445703) — 2025-09 — prensa
