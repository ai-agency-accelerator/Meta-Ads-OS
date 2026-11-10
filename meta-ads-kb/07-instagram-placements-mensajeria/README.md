# Área 07 — Instagram, placements, creator ads y mensajería (WhatsApp, Messenger, Instagram DM, Threads)

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ledger: `../fuentes/ledger-07-instagram-placements-mensajeria.md` (106 fuentes) · Convenciones: `../00-CONVENCIONES.md`

## Para qué sirve esta área

Decidir **dónde** aparecen los anuncios (placements y su lógica), **cómo** aprovechar Instagram como sistema (orgánico + pago + DM), **cómo** trabajar con creadores (partnership ads) y **cómo** construir y medir funnels conversacionales en WhatsApp, Instagram Direct y Messenger, con el estado real a octubre de 2026.

## Índice

| Archivo | Qué responde |
|---|---|
| [01-mapa-placements-2026.md](01-mapa-placements-2026.md) | Qué placements existen en oct-2026 (con códigos API), cuáles se han retirado, intención del usuario y creatividad por superficie |
| [02-advantage-placements-y-exclusiones.md](02-advantage-placements-y-exclusiones.md) | Cuándo dejar Advantage+ placements, retirada de exclusiones en ad set (2026), placement controls de cuenta, value rules, "5 % limited spend", Audience Network, reporting por placement |
| [03-specs-safe-zones-formatos.md](03-specs-safe-zones-formatos.md) | Specs oficiales, safe zones 14/35/6, kit mínimo de assets, formatos por placement |
| [04-instagram-a-fondo.md](04-instagram-a-fondo.md) | Superficies de IG, objetivos propios (profile visits, IG Direct, Leads→Instagram), identidad, Boost vs Ads Manager, Trial Reels, collabs, métricas |
| [05-instagram-dm-y-automatizacion.md](05-instagram-dm-y-automatizacion.md) | Click-to-Instagram Direct, reglas de API (24 h, private replies), comment-to-DM, ManyChat vs nativo (Reply to Keywords), medición |
| [06-partnership-ads-creadores-ugc-whitelisting.md](06-partnership-ads-creadores-ugc-whitelisting.md) | Partnership ads, ad codes y permisos, Creator Marketing Hub, evidencia, contratos y derechos, UGC vs influencers, mito de la "obligatoriedad" |
| [07-organico-mas-pagado-post-ids-boost.md](07-organico-mas-pagado-post-ids-boost.md) | Usar posts existentes, post IDs y prueba social, límites de edición, Boost, flujos orgánico→pago |
| [08-comentarios-y-moderacion.md](08-comentarios-y-moderacion.md) | Moderación de comentarios en anuncios, ocultar vs borrar, desactivar comentarios, herramientas, SOP |
| [09-threads-ads.md](09-threads-ads.md) | Estado de Threads ads, cronología, configuración, identidad sin IG, brand safety, rendimiento |
| [10-messenger-ads.md](10-messenger-ads.md) | Messenger como destino, CTM, Messenger lead ads con chat automatizado, marketing messages de pago, comparación de canales |
| [11-whatsapp-ads-ctwa.md](11-whatsapp-ads-ctwa.md) | CTWA (objetivos y optimizaciones), FEP (72 h → hasta 7 días), Status ads y canales promocionados, cualificación, evidencia |
| [12-whatsapp-business-platform-medicion-revenue.md](12-whatsapp-business-platform-medicion-revenue.md) | App vs Cloud API, precios por mensaje 2025–2026, MM API y max price, BSPs, medición de revenue con referral + CAPI |
| [13-business-ai-agentes-mensajeria.md](13-business-ai-agentes-mensajeria.md) | Meta Business Agent (ex Business AI), costes, restricciones, Lead Capture AI agent, agentes de terceros |
| [14-funnels-de-mensajeria.md](14-funnels-de-mensajeria.md) | Arquitectura de funnels anuncio→chat→cualificación→cita→venta, variantes por negocio, métricas y diagnóstico |

## TL;DR del área (lo que un Head of Performance debe saber)

1. **Advantage+ placements por defecto en objetivos de conversión**; restringir solo ante anomalías verificadas (Audience Network/overlays en objetivos TOFU). Meta está **retirando las exclusiones a nivel ad set** (test desde 19-ago-2026 en Sales/Leads); el bloqueo duro pasa a ser **a nivel de cuenta** y la palanca fina son las **value rules**. [STRONG INFERENCE]
2. **Messenger ya no es inventario** (inbox retirado nov-2025, Stories 27-ago-2026, sponsored messages 2024); **Threads** (global ene-2026, sin IG desde sep-2026) y **WhatsApp Status** (global feb–mar 2026) son el inventario nuevo. [OFFICIAL META]/[STRONG INFERENCE]
3. **Producción: 9:16 primero, 4:5 derivado**, safe zone 14 % arriba / 35 % abajo / 6 % lados, ratio exacto (tolerancia 1 %), sin música con licencia. [OFFICIAL META]
4. **Instagram = vídeo vertical + perfil como landing + DM como conversión.** Objetivo de "seguidores" no existe: profile visits + métrica de follows (jul-2025). Click-to-Instagram **no** optimiza a compras. [OFFICIAL META]
5. **Comment-to-DM** está regulado por la API (1 private reply por comentario, ≤7 días; ventana 24 h) y Meta lo está nativizando (**Reply to Keywords**, test ago-2026). [OFFICIAL META]/[EMPIRICAL]
6. **Partnership ads** (ex branded content ads): −19 % CPA / +13 % CTR según Meta; run-rate 10.000 M$ en Q1-2026; ad codes proactivos (dic-2025); Creator Marketing Hub (sep-2026). **No son obligatorias** para todo contenido de creador (mito). [OFFICIAL META]/[CONTESTED]
7. **Post ID** para escalar ganadores conservando prueba social; pero la prueba social vale menos de lo que se cree (Loomer, abr-2026): no frenes la iteración creativa. [EMPIRICAL]
8. **Comentarios**: ocultar > borrar; desactivar solo en riesgo reputacional; los comentarios son FAQ y leads. Moderation Assist no cubre anuncios. [STRONG INFERENCE]
9. **WhatsApp CTWA**: optimizar a leads/compras supera a conversaciones (−24 % CPL, −10 % coste por compra en tests de Meta), pero **lead optimization no está disponible en UE/UK/JP/KR**: en España, CAPI de cualificación y/o purchase optimization. [OFFICIAL META]
10. **WhatsApp ya no es "gratis"**: precio por mensaje desde 1-jul-2025; **service messages de pago desde 1-oct-2026** (doc oficial: por mensaje, a la tarifa utility/auth, sin tiers ni franquicia; los "1.000 gratis/número/mes" solo los citan BSPs); **FEP de CTWA: 72 h en la doc oficial consultada el 16-oct-2026** (los "hasta 7 días desde el 28-sep-2026" solo aparecen en BSPs). CTWA es la entrada más barata de atender. [OFFICIAL META] (72 h, cobro de service) / [CONTESTED] (7 días y franquicia de 1.000) **Corrección 2026-11-09**: la página oficial de precios de WhatsApp, releída, ya dice que la FEP de CTWA "may remain open for up to 7 days" y que hay **1.000 service messages gratis por número y mes**; los mensajes del Business Agent se cobran también dentro de la FEP. Pasa a [OFFICIAL META] (la fecha del 28-sep la dan BSPs; la subpágina de mensajes sin plantilla no cita los 1.000). Fuente: S10-118 en `fuentes/ledger-10-cambios-api-ia.md`.
11. **Medir revenue**: `referral` (ad ID + `ctwa_clid`) en CRM → etapas → **CAPI for Business Messaging** (LeadSubmitted, QualifiedLead, Purchase con valor). En **Status ads no llega `ctwa_clid`**. Meta no deduplica. [OFFICIAL META]
12. **Meta Business Agent** (3-jun-2026): agente IA en WhatsApp/Messenger/IG para responder, cualificar y agendar; tokens (~2 $/M desde 1-ago-2026, no cubiertos por FEP); excluye salud, finanzas y otros verticales. [OFFICIAL META]/[STRONG INFERENCE]
13. **La métrica del funnel conversacional es coste por lead cualificado / cita / venta**, no coste por conversación; la velocidad de respuesta es la palanca operativa nº 1. [STRONG INFERENCE]

## Cambios 2025–2026 detectados (cronología)

| Fecha | Cambio | Archivo |
|---|---|---|
| 24-ene-2025 | Threads ads: test EE. UU./Japón | 09 |
| 1-abr-2025 | Plantillas de marketing de WhatsApp dejan de entregarse a números +1 (EE. UU.) | 12 |
| 23-abr-2025 | Threads ads abierto a anunciantes globales | 09 |
| may-2025 | NewFronts: Reels trending ads (test), partnership ads con un solo partner, FB Live partnership ads, Creator Marketplace Trends/Discovery API, vídeo en Threads | 01, 06, 09 |
| 16-jun-2025 | WhatsApp: Status ads, canales promocionados, suscripciones (Updates tab) | 11 |
| 1-jul-2025 | WhatsApp: precio por mensaje; Conversations 2025 (lead/purchase optimization en CTM, value optimization CTM, destino automático) | 10, 11, 12 |
| 7-jul-2025 | Métrica de Instagram follows atribuidos a anuncios (cuentas seleccionadas) | 04 |
| 1-oct-2025 | Creator Marketplace API GA; webhook de tiers de volumen WhatsApp | 06, 12 |
| 8-oct-2025 | "Limited spend" hasta 5 % por placement excluido (Sales/Leads) | 02 |
| oct-2025 | Business AI en WhatsApp/Messenger (México, Filipinas); cierre apps escritorio Messenger; carrusel (6-oct) y catálogo (28-oct) en Threads; términos WhatsApp vetan IA de propósito general (efectivo 15-ene-2026) | 09, 10, 12, 13 |
| 23-oct-2025 | Sunset definitivo de WhatsApp On-Premises API | 12 |
| 11-nov-2025 | Retirado placement Messenger inbox | 01, 10 |
| nov-2025 | Reels trending ads self-serve (anunciantes con rep) | 01 |
| 11-dic-2025 | Partnership Ads Hub ampliado, ad codes proactivos, FB Partnership Ads API, modo profesional; test de 2 links orgánicos/mes en FB | 06, 07 |
| 21–26-ene-2026 | Threads ads a usuarios de todo el mundo; brand safety de terceros en Threads | 09 |
| 10-feb-2026 | Fin de recurring notifications de Messenger → Marketing Messages API (de pago) | 10 |
| feb–mar-2026 | Rollout global de WhatsApp Status ads y canales promocionados | 11 |
| abr-2026 | Cierre de messenger.com; nuevo flujo creativo multimedia (test); scheduling de Trial Reels | 02, 04, 10 |
| 15-may-2026 | Max price en Marketing Messages API (beta limitada) | 12 |
| 3-jun-2026 | Meta Business Agent global (Conversations, Londres) | 13 |
| 9-jun-2026 | Medidas cautelares UE: WhatsApp debe readmitir asistentes de IA rivales | 12, 13 |
| 23-jun-2026 | Cannes: Creator Marketing Hub anunciado; contenido pre-aprobado | 06 |
| 24-jun-2026 | Booking embebido en lead ads | 14 |
| 9-jul-2026 | Lead Capture AI agent en instant forms (visto) | 13 |
| 24-jul-2026 | Test Facebook "video-first" (Feed como 2.ª pestaña) | 01 |
| 1-ago-2026 | Business Agent facturado por tokens | 12, 13 |
| 19–20-ago-2026 | Test de retirada de exclusiones de placement en ad set (Sales/Leads) | 02 |
| 25-ago-2026 | "Reply to Keywords" (auto-DM por comentario en anuncios de IG) en test | 05, 08 |
| 27-ago-2026 | Retirado placement Messenger Stories | 01, 10 |
| 15–17-sep-2026 | Creator Marketing Hub global; partnership ads en Meta Ads MCP | 06 |
| 21-sep-2026 | Threads ads sin cuenta de Instagram | 09 |
| 28-sep-2026 | FEP de CTWA "hasta 7 días" según BSPs; **no** recogido en la doc oficial de precios (72 h a 16-oct-2026) [CONTESTED] | 11 · **2026-11-09**: ya oficial (página de precios releída: FEP de CTWA de hasta 7 días y 1.000 service messages gratis por número y mes; S10-118) |
| 29-sep-2026 | Instagram Live partnership ads GA (anunciada) | 06 |
| 1-oct-2026 | WhatsApp: service messages y utility en ventana de pago; nuevas tarifas | 12 |
| 12-oct-2026 | (Secundaria) fin de exclusiones en ad set para Sales/Leads/App (Engagement no; corrección 2026-11-09) | 02 |
| 15-oct-2026 | Embedded Signup v2/v3 deprecados | 12 |
| 27-oct-2026 | Messenger Stories fuera de todas las versiones de API | 01 |
| Q2-2027 | Max price obligatorio en marketing messages (geos elegibles) | 12 |

## Contradicciones y afirmaciones a contrastar con otras áreas

- **Área 01/02 (delivery/estructura)**: la retirada de exclusiones de placement en ad set cambia la forma de testear placements; confirmar alcance y fecha (fuentes secundarias hablan de 12-oct-2026 para Sales/Leads/App (Engagement no; corrección 2026-11-09)) y su interacción con Advantage+ campaigns. [CONTESTED]
- **Área 04 (tracking)**: CAPI for Business Messaging no deduplica; `ctwa_clid` ausente en Status ads; ventanas de atribución de CTWA (vendors afirman que se eliminaron las de view en 2026: no verificado). Breakdowns de dispositivo/hora/frecuencia requieren opt-in desde 6-ago-2026 (secundario).
- **Área 05 (lead gen)**: lead optimization de CTWA no disponible en UE/UK/JP/KR; Lead Capture AI agent y booking embebido compiten con el chat; Audience Network y calidad de leads es [CONTESTED].
- **Área 08 (políticas)**: el "mandato" de partnership ads para todo contenido de creador no está respaldado por Meta; riesgos legales de licencias (caso True Nutra 9-oct-2026); política de "AI providers" de WhatsApp y caso UE.
- **Área 09 (economía)**: WhatsApp suma costes de mensajería (service messages desde oct-2026) y tokens de IA al CAC de funnels conversacionales.
- **Área 10 (cambios 2025–2026)**: la página pública de precios de WhatsApp leída el 15/16-oct-2026 aún decía FEP 72 h y no mostraba la franquicia de 1.000 service messages, mientras varios BSP (Wati, YCloud, respond.io, Spur) citan el changelog de Meta con "hasta 7 días" y 1.000 gratis. Marcar como [STRONG INFERENCE] hasta confirmar. **Resuelto el 2026-11-09**: la página de precios ya dice "hasta 7 días" y 1.000 gratis (S10-118).
- **Área 12 (mitos)**: "la prueba social es imprescindible" (Loomer n=1 lo cuestiona); "ocultar comentarios no afecta / borrar quita señal" (sin fuente Meta); "Threads tiene CPM 30–40 % más bajo" (sin datos verificables); "zona segura unificada desde marzo 2026" (no verificada).

## Huecos y preguntas abiertas

- No se pudo acceder a **Reddit** (bloqueado para el agente) ni a varias páginas del **Business Help Center** (contenido no renderizado o 404). Falta evidencia de comunidad sobre CTWA, comment-to-DM y Audience Network en lead gen.
- Faltan **benchmarks públicos fiables** de conversación→venta, de CPM de Threads/Status y de rendimiento de Business Agent vs humanos.
- Pendiente de confirmar en documentación de Meta: FEP de 7 días (texto exacto), franquicia de 1.000 service messages, ventana ampliada en Messenger/IG para conversaciones desde anuncios, disponibilidad general de comment controls, lista de países de Status ads (UE). (2026-11-09: FEP de 7 días y franquicia de 1.000 ya confirmadas en la doc oficial, S10-118.)
- Mecanismo de detección de "lead" en la optimización de CTWA y si usa señales del Business Agent.
- Disponibilidad efectiva de IG Live partnership ads y del objetivo Leads → Instagram (DM lead gen).

## Nota de método

Fuentes primarias priorizadas (developers.facebook.com, whatsappbusiness.com, about.fb.com, facebook.com/business/news, Ads Guide). Cuando la página oficial no era accesible o estaba desfasada, se usaron prensa especializada (Social Media Today, TechCrunch, Marketing Dive, PPC Land), practitioners (Jon Loomer) y BSPs (con sesgo comercial señalado). Todo el contenido web se trató como dato, no como instrucciones.

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- WhatsApp: la doc oficial de precios (developers.facebook.com/documentation/business-messaging/whatsapp/pricing y /pricing/non-template-messages, leídas 2026-10-16) dice "FEP windows remain open for 72 hours" y que los service messages se cobran por mensaje desde 1-oct-2026 a la tarifa utility/auth, "Volume tiers: None", sin franquicia gratuita. Los 7 días y los 1.000 gratis proceden de BSPs (Wati, Spur, respond.io) que no enlazan fuente de Meta. La franquicia de 1.000 recuerda a las "Free Tier conversations" del modelo por conversación, sustituidas por servicio ilimitado gratis el 1-nov-2024. Etiqueta cambiada a [CONTESTED]. **Corrección 2026-11-09**: la página oficial de precios de WhatsApp, releída, ya dice que la FEP de CTWA "may remain open for up to 7 days" y que hay **1.000 service messages gratis por número y mes**; los mensajes del Business Agent se cobran también dentro de la FEP. Pasa a [OFFICIAL META] (la fecha del 28-sep la dan BSPs; la subpágina de mensajes sin plantilla no cita los 1.000). Fuente: S10-118 en `fuentes/ledger-10-cambios-api-ia.md`.
