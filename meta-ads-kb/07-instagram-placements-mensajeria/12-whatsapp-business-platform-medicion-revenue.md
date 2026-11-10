# WhatsApp Business Platform: app vs Cloud API, precios 2025–2026, plantillas, BSPs y cómo medir revenue de verdad

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: arquitectura (WhatsApp Business app, Cloud API, coexistencia, BSPs, fin del On-Premises API), modelo de precios por mensaje y cambios de 2025–2026, plantillas y Marketing Messages API, y el sistema de medición de ingresos desde anuncios CTWA (referral, `ctwa_clid`, CAPI for Business Messaging, CRM).

## TL;DR

- **On-Premises API está muerto desde el 23-oct-2025** (último cliente v2.61.1). Todo es **Cloud API** (directo o vía BSP/tech provider). [OFFICIAL META] ([sunset](https://developers.facebook.com/docs/whatsapp/on-premises/sunset))
- **Precio por mensaje desde el 1-jul-2025** (adiós conversaciones de 24 h): se cobran plantillas entregadas de **marketing**, **utility** y **authentication** según país del destinatario; tiers de volumen para utility/auth; cambios de tarifas solo el 1.º de cada trimestre. [OFFICIAL META] ([pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing))
- **Desde el 1-oct-2026 Meta cobra también los *service messages*** (mensajes libres dentro de la ventana de 24 h) a la tarifa utility/auth de cada mercado, sin tiers; y la **utility dentro de la ventana vuelve a cobrarse** (fue gratis jul-2025 → sep-2026). Varios BSP reportan **1.000 service messages gratis por número y mes**. Mensajes dentro de la FEP siguen gratis. [OFFICIAL META] (cobro y, desde el 2026-11-09, franquicia de 1.000; antes [STRONG INFERENCE]) **Corrección 2026-11-09**: la página oficial de precios de WhatsApp, releída, ya dice que la FEP de CTWA "may remain open for up to 7 days" y que hay **1.000 service messages gratis por número y mes**; los mensajes del Business Agent se cobran también dentro de la FEP. Pasa a [OFFICIAL META] (la fecha del 28-sep la dan BSPs; la subpágina de mensajes sin plantilla no cita los 1.000). Fuente: S10-118 en `fuentes/ledger-10-cambios-api-ia.md`.
- **Marketing Messages API (antes MM Lite)**: endpoint `/marketing_messages`, entrega optimizada por probabilidad de engagement, TTL, benchmarks; **max price por entrega** (beta limitada 15-may-2026, beta abierta oct-2026, **obligatorio en geografías elegibles en Q2-2027**; las tarifas fijas quedarán solo en Cloud API). [OFFICIAL META] ([MM pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/marketing-messages/pricing))
- **Plantillas de marketing a números de EE. UU. (+1) no se entregan desde el 1-abr-2025** (error 131049); y hay límites por usuario de mensajes de marketing en todos los mercados. [STRONG INFERENCE] (BSPs; sin página Meta leída)
- **Medición de revenue**: guarda el objeto `referral` del primer mensaje (ID del anuncio en `source_id`, `ctwa_clid`), asocia la conversación a un contacto en tu CRM y envía **LeadSubmitted / QualifiedLead / Purchase (con value y currency)** por **CAPI for Business Messaging** (`action_source=business_messaging`, `messaging_channel=whatsapp`, `whatsapp_business_account_id` + `ctwa_clid`). Meta **no deduplica**: hazlo tú. [OFFICIAL META] ([CAPI BM](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging))
- **Trampa crítica**: para conversaciones que vienen de **anuncios en WhatsApp Status, `ctwa_clid` se omite** del webhook → no puedes atribuir por CAPI con click ID esas conversaciones. [OFFICIAL META] ([webhook text](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/text))
- **La app WhatsApp Business (sin API) es gratis pero ciega para medición**: sin webhooks, sin `ctwa_clid`, sin CAPI. Vale para empezar; para medir revenue y escalar hace falta Cloud API (posible con **coexistencia**: mismo número en app y API). [STRONG INFERENCE]

## 1. Arquitectura: qué opción elegir

| Opción | Coste plataforma | Pros | Contras | Para quién |
|---|---|---|---|---|
| **WhatsApp Business app** | Gratis (mensajes gratis; marketing messages de pago en algunos países) | Rápida, catálogo, etiquetas, respuestas rápidas, CTWA desde la app/Ads Manager, Business Agent | Sin webhooks/CAPI; multiagente limitado; difusiones limitadas; medición pobre | Autónomos y micro-pymes, validación |
| **Cloud API directa** | Por mensaje (Meta) | Control total, webhooks, CAPI, Flows, MM API | Requiere desarrollo | Empresas con equipo técnico |
| **Cloud API vía BSP / tech provider** (Twilio, 360dialog, Gupshup, Infobip, Wati, respond.io, SleekFlow, YCloud…) | Meta + cuota BSP | Bandeja multiagente, bots, CRM, integraciones, plantillas | Coste y dependencia del proveedor | Mayoría de pymes y medianas que venden por WhatsApp |
| **Coexistencia** (mismo número en app + API) | App gratis + API por mensaje | Mantener número y uso de la app mientras automatizas | Sincronización y funciones limitadas; app abierta cada ~13 días; sin badge verificado (según proveedores) | Pymes que migran sin cambiar de número |
| **On-Premises API** | — | — | **Sunset 23-oct-2025** | Nadie [OUTDATED] |

[OFFICIAL META] (On-Prem, Cloud API) + [STRONG INFERENCE] (coexistencia: [Kapso](https://kapso.ai/blog/whatsapp-business-app-coexistence-cloud-api) y otros BSP; lanzamiento ~2025).

Otros hitos de plataforma: Embedded Signup v4 (v2 y v3 deprecados el 15-oct-2026); WhatsApp Business Tools MCP (sep-2026); Calling API (llamadas iniciadas por el usuario gratis; las iniciadas por la empresa se cobran por pulsos de 6 s, con permiso del usuario; restricciones por país). [STRONG INFERENCE] (AdsUploader) + [OFFICIAL META] (pricing de llamadas, act. 9-jul-2026, vía YCloud/terceros)

## 2. Precios: cronología y reglas vigentes

| Periodo | Modelo | Qué se cobra |
|---|---|---|
| Hasta 30-jun-2025 | Por conversación (ventanas de 24 h por categoría) | Conversaciones de marketing/utility/auth/service (service gratis desde nov-2024) [OUTDATED] |
| 1-jul-2025 → 30-sep-2026 | **Por mensaje** | Plantillas entregadas de marketing, utility (fuera de CSW) y auth. Gratis: service, utility dentro de CSW, todo en FEP |
| **Desde 1-oct-2026** | Por mensaje | Lo anterior **+ service messages** (tarifa = utility/auth del mercado, sin tiers; el 16-oct la doc oficial no recogía franquicia gratuita y los "1.000 gratis/número/mes" solo los citaban BSPs; desde el 2026-11-09 es [OFFICIAL META]) **+ utility dentro de CSW**. Gratis: todo dentro de FEP; mensajes entrantes · **2026-11-09**: ya oficial (página de precios releída: FEP de CTWA de hasta 7 días y 1.000 service messages gratis por número y mes; S10-118) |

**Reglas clave** [OFFICIAL META]:
- La tarifa depende de la **categoría de la plantilla** y del **prefijo del país del destinatario**. Revisa la categoría que Meta asigna a tus plantillas: pagas la que aplique en el momento del envío.
- **Tiers de volumen** (solo utility y authentication), agregados por portfolio y mercado; se reinician cada mes; webhook de cambio de tier desde 1-oct-2025.
- **Calendario**: cambios de tarifas solo el 1-ene, 1-abr, 1-jul y 1-oct; aviso mínimo 1 mes (tarifas), 3 meses (add-ons), 6 meses (cambios de modelo).
- **Authentication-international**: tarifa distinta para autenticación en ciertos países (nuevos mercados 1-oct-2026).
- **Monedas locales**: INR (localización desde 1-ene-2026; WABAs no INR dejan de entregar desde 1-ene-2027), BRL (desde 1-jul-2026; migración hasta 30-jun-2027), y 8 monedas nuevas desde 1-abr-2026 (ARS, CLP, COP, MYR, PEN, SAR, SGD, AED).

**Tarifas orientativas** (USD por mensaje entregado; verificar en el rate card vigente):

| Mercado | Marketing | Utility/Auth | Fuente |
|---|---|---|---|
| España | ~0,0707 (desde 1-jul-2026; antes 0,0615) | ~0,0135 utility / ~0,0298 auth (pre-jul-2026) | [STRONG INFERENCE] (YCloud, SetSmart) |
| México | 0,0397 (1-oct-2026; antes 0,0305) | 0,0085 | [STRONG INFERENCE] (Spur, YCloud) |
| Norteamérica | 0,0250 (no se entregan a +1 EE. UU.) | 0,0034 | [STRONG INFERENCE] |
| Brasil | 0,0625 | 0,0068 | [STRONG INFERENCE] |
| India | 0,0118 | 0,0014 | [STRONG INFERENCE] |
| Reino Unido | 0,0635 | 0,0220 | [STRONG INFERENCE] |

**Política de "AI Providers"**: en oct-2025 Meta cambió los términos para vetar desde el 15-ene-2026 a proveedores de **asistentes de IA de propósito general** (tipo ChatGPT) en la Business API; los bots de atención/negocio siguen permitidos. Tras la investigación antimonopolio de la Comisión Europea (dic-2025), Meta propuso una tarifa para estos proveedores (mar-2026, ~0,049–0,13 € por mensaje) y la página de precios menciona una "pricing policy for AI Providers" (efectiva 16-feb-2026, act. 12-may-2026). El **9-jun-2026** la Comisión dictó medidas cautelares obligando a restaurar el acceso gratuito previo para asistentes rivales en el EEE; Meta recurrió. **Para un anunciante que usa un agente de IA de negocio (ventas/soporte) esto no prohíbe nada**, pero conviene que el BSP confirme cómo clasifica tu caso. [OFFICIAL META] (existencia de la política) + [STRONG INFERENCE] (cronología vía [TechCrunch](https://techcrunch.com/2025/12/04/eu-investigating-meta-over-policy-change-that-bans-rival-ai-chatbots-from-whatsapp/), [TechTimes](https://www.techtimes.com/articles/320553/20260715/eu-antitrust-order-reopens-whatsapp-chatgpt-setting-precedent-ai-markets.htm))

**Meta Business Agent**: facturación por tokens desde el 1-ago-2026 (~2 $/M tokens; ~4–5 céntimos por respuesta típica según BSPs), adicional a los cargos de mensajes y **no cubierto por la FEP**. [STRONG INFERENCE] (Wati, YCloud, SleekFlow). Ver `13-…`. · **2026-11-09**: [OFFICIAL META] (la página de precios dice que los mensajes del Business Agent se cobran también dentro de la FEP; S10-118)

## 3. Plantillas y mensajes de marketing

- **Categorías**: marketing (promoción, ofertas, reactivación), utility (transaccional sobre algo que el usuario ha hecho/pedido), authentication (OTP). Meta re-categoriza; una "utility" con contenido promocional se cobra como marketing. [OFFICIAL META]
- **Opt-in**: necesitas consentimiento para enviar mensajes iniciados por la empresa; un clic en CTWA abre la conversación pero no equivale a opt-in de marketing indefinido. Guarda evidencia del opt-in. [STRONG INFERENCE] (política de WhatsApp Business; no re-verificada en 2026)
- **Límites por usuario**: Meta limita cuántas plantillas de marketing recibe cada usuario según engagement (error 131049 "healthy ecosystem"/per-user limit). Plantillas de marketing **no se entregan a +1 (EE. UU.) desde el 1-abr-2025**. [STRONG INFERENCE] ([Zoho](https://help.zoho.com/portal/en/kb/marketing-automation-2-0/faqs/marketing-campaigns/whatsapp/articles/what-is-the-pause-on-whatsapp-marketing-messages-for-us-numbers), Spur oct-2026)
- **Marketing Messages API** [OFFICIAL META] ([overview](https://developers.facebook.com/documentation/business-messaging/whatsapp/marketing-messages/overview)):
  - Envío a `/marketing_messages`; mismo número y plantillas; facturación similar a Cloud API.
  - Optimización de entrega hacia quienes probablemente lean/hagan clic (test India ene-2025, ~12 M mensajes; vendors citan +9 % entregas en contenido de alto engagement).
  - TTL para campañas sensibles al tiempo; GIFs; benchmarks frente a negocios similares; optimización creativa automática **desactivada por defecto** a nivel WABA desde 2026 (activable).
  - Métricas de conversión offsite en WhatsApp Manager y Template Analytics API (changelog). Ads Manager: no está claro que muestre estas conversiones. [CONTESTED]
  - **Max price** por entrega: `optimization_spec.bid_amount` (por 1.000 entregas), multiplicadores por país; beta limitada 15-may-2026 → beta abierta oct-2026 → GA Q2-2027 obligatorio en geos elegibles. Plantillas con max price no se pueden enviar por `/messages` (error 131061).
- **Marketing messages en Ads Manager** (desde Conversations 2024): subes una lista de suscriptores y la IA de Meta elige destinatarios según el objetivo (conversiones o awareness); disponible vía partners/Marketing API (en Marketing API desde 13-ago-2026 según AdsUploader). [OFFICIAL META] + [STRONG INFERENCE]

## 4. Cómo medir revenue de verdad (sistema completo)

### 4.1 Datos que hay que capturar en el primer mensaje (Cloud API)

Objeto `referral` del webhook (solo si el mensaje viene de un CTWA) [OFFICIAL META]:

| Campo | Contenido | Uso |
|---|---|---|
| `source_id` | ID del anuncio | Atribución por anuncio en CRM |
| `source_type` | "ad" | Filtro |
| `source_url` | URL del anuncio | Referencia |
| `headline`, `body` | Titular y texto principal | Análisis creativo |
| `media_type`, `image_url`/`video_url`/`thumbnail_url` | Creatividad | Análisis creativo |
| `ctwa_clid` | Click ID del anuncio | **Clave para CAPI**; **omitido en anuncios de WhatsApp Status** |
| `welcome_message.text` | Greeting del anuncio | Contexto |

### 4.2 Pipeline recomendado

```
Anuncio CTWA → 1.er mensaje (webhook con referral) → BSP/CRM crea contacto + guarda source_id, ctwa_clid, timestamp
   → Bot/humano cualifica → CRM cambia etapa: Lead → Cualificado → Cita → Venta (con importe)
   → Cada cambio de etapa dispara evento CAPI for Business Messaging:
        LeadSubmitted (al dar datos) · QualifiedLead (al cualificar) · Purchase {value, currency} (al cobrar)
        user_data: whatsapp_business_account_id + ctwa_clid ; action_source=business_messaging ; messaging_channel=whatsapp
   → Ads Manager: columnas de eventos por anuncio + optimización a Purchase (CTWA admite purchase optimization)
   → Si la venta ocurre en web/tienda: evento web/offline por CAPI estándar (el clic sigue siendo la base de atribución)
```

[OFFICIAL META] (campos, eventos, optimización) + [STRONG INFERENCE] (diseño del pipeline).

### 4.3 Requisitos técnicos de CAPI for Business Messaging (WhatsApp)

- Dataset vinculado a la WABA: `POST/GET /{WABA_ID}/dataset`. El dataset es de la empresa; los partners reciben acceso. [OFFICIAL META]
- Permisos: `whatsapp_business_management` y `whatsapp_business_manage_events` (advanced access); integración con Embedded Signup o Facebook Login for Business. [OFFICIAL META]
- Eventos soportados: Purchase, LeadSubmitted, QualifiedLead, InitiateCheckout, AddToCart, ViewContent, OrderCreated/Shipped/Delivered/Canceled/Returned, CartAbandoned, RatingProvided, ReviewProvided. Proveedores reportan que eventos web estándar como `Lead` o `Schedule` son rechazados en este endpoint. [OFFICIAL META] (lista) + [STRONG INFERENCE] (rechazo)
- `Purchase` requiere `currency` y `value`. [STRONG INFERENCE]
- **Sin deduplicación por parte de Meta**: envía cada hito una sola vez. [OFFICIAL META]
- Problema frecuente: el token de sistema de la WABA no puede publicar en un pixel/dataset de **otro** Business Manager (error 100). Alinea propiedad de activos. [STRONG INFERENCE] (Zernio)

**Ampliación 2026-11-09 (Messenger, Instagram y WhatsApp sin clic)**, leída en la documentación de desarrolladores de
CAPI for Business Messaging por el bloque de mensajería del OS (detalle y fuentes en `docs/guias/mensajeria.md`):
- **Messenger:** identifica a la persona con `page_id` + `page_scoped_user_id` (el PSID); permiso `page_events`.
  [OFFICIAL META]
- **Instagram Direct:** `instagram_business_account_id` + `ig_sid`; permiso `instagram_manage_events`. La lista general
  de parámetros cita `ig_account_id` en su lugar. [CONTESTED] (dos nombres en páginas oficiales; el OS usa el de la
  página de mensajería)
- **WhatsApp sin clic** (anuncios de Estados, que no llevan `ctwa_clid`, o un CRM que no lo reenvía): `page_id` + WABA
  + al menos un dato de cliente hasheado (p. ej. el teléfono). `external_id` no cuenta para emparejar. [OFFICIAL META]
- **Optimización a compras por mensajería:** solo Messenger y WhatsApp, no Instagram. [OFFICIAL META]
- **BSUID** (`from_user_id`): las personas con nombre de usuario de WhatsApp pueden llegar en el webhook sin número
  (`from`); entonces se identifican por su BSUID. Guárdalo en el CRM con el resto de datos del contacto.
  [OFFICIAL META]
- Solo tres eventos de la lista cerrada encajan en un embudo consultivo: `LeadSubmitted`, `QualifiedLead` y `Purchase`
  (contrato §16 del OS). [STRONG INFERENCE]

### 4.4 Atribución y lectura

- Ventanas estándar de clic (1 o 7 días); algunos vendors afirman que en 2026 desaparecieron las ventanas de view para CTWA — **no verificado**. [HYPOTHESIS]
- Los eventos CAPI de mensajería solo deben representar acciones dentro del hilo; si la conversión es en web, usa CAPI web. [OFFICIAL META]
- Para **Status ads** (sin `ctwa_clid`): atribución por `source_id` en tu CRM (informes propios) y por modelos/lift; no por CAPI con click ID. [STRONG INFERENCE]
- KPIs de negocio: coste por conversación → % cualificación → coste por lead cualificado → % cita → coste por cita → % cierre → CAC y ROAS de caja. Ver `14-…`.

### 4.5 Sin API (app Business)

- Etiquetas manuales ("Nuevo lead", "Pagado"), catálogo y pedidos dentro del chat. No hay forma documentada de enviar esas etiquetas como eventos a Meta. [HYPOTHESIS]
- Alternativa mínima: registrar manualmente cada venta con fecha y anuncio de origen (el usuario llega con mensaje prellenado que identifique la campaña) y cargar conversiones offline (si tienes teléfono/email) por CAPI estándar. [STRONG INFERENCE]

## 5. BSPs: criterios de selección

| Criterio | Pregunta |
|---|---|
| CAPI for Business Messaging | ¿Envía LeadSubmitted/QualifiedLead/Purchase con `ctwa_clid` automáticamente desde etapas del CRM? |
| Referral | ¿Guarda `source_id` y creatividad por contacto e informa por anuncio? |
| CRM | ¿Integración nativa con tu CRM (HubSpot, Kommo, Pipedrive, Salesforce…) o lo es él mismo? |
| IA | ¿Agente propio, Meta Business Agent o ambos? ¿Cómo factura tokens? |
| Flows | ¿Editor de WhatsApp Flows? |
| Precios | Cuota fija + recargo por mensaje (algunos añaden margen sobre Meta) |
| Coexistencia | ¿Soporta onboarding con el número de la app? |
| MM API y max price | ¿Soporta `/marketing_messages` y `optimization_spec`? |

[STRONG INFERENCE].

## Implicaciones operativas

- Presupuestar desde oct-2026 el coste de service messages (desde el primero, salvo que la factura confirme una franquicia) y utility dentro de ventana; priorizar CTWA (FEP gratis) como entrada. (2026-11-09: la franquicia de 1.000 por número y mes ya es oficial, S10-118; comprobarla igualmente en la primera factura.)
- Migrar cualquier resto de On-Premises (si existiera) y Embedded Signup v2/v3.
- Implementar CAPI for Business Messaging con eventos de etapa del CRM antes de escalar CTWA: sin eso, el algoritmo optimiza a "gente que chatea".
- Planificar la migración a max price en marketing messages antes de Q2-2027.
- Para Status ads, preparar atribución por `source_id` (no hay `ctwa_clid`).

## Errores frecuentes

- Pensar que "WhatsApp es gratis" en 2026 para empresas con API.
- Enviar `Lead` (evento web) en vez de `LeadSubmitted` al endpoint de mensajería.
- Enviar Purchase sin `value`/`currency` o duplicado desde dos sistemas.
- Etiquetar plantillas promocionales como utility (Meta re-categoriza y cobra marketing).
- Usar un número personal o la app Business para volúmenes altos y luego no poder medir.

## Preguntas abiertas

- Confirmación en documentación de Meta de la franquicia de 1.000 service messages/número/mes (la página de precios leída no la mostraba). Resuelto el 2026-11-09: sí aparece en la página general de precios (S10-118), no en la subpágina de mensajes sin plantilla (S10-119).
- Texto exacto y condiciones del FEP de hasta 7 días. Resuelto en parte el 2026-11-09: "may remain open for up to 7 days" para CTWA (S10-118).
- ¿Se levantará la pausa de marketing a números +1 de EE. UU.?
- Estado final del caso de la Comisión Europea sobre "AI providers" y su efecto en precios.
- ¿Ads Manager mostrará conversiones de marketing messages de WhatsApp?

## Fuentes clave

- [Pricing on the WhatsApp Business Platform](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — vigente 2026 — meta-developers
- [Non-template message pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages) — 2026 — meta-developers
- [Marketing Messages API overview](https://developers.facebook.com/documentation/business-messaging/whatsapp/marketing-messages/overview) — 2026 — meta-developers
- [Marketing Messages API pricing (max price)](https://developers.facebook.com/documentation/business-messaging/whatsapp/marketing-messages/pricing) — 2026 — meta-developers
- [On-Premises API sunset](https://developers.facebook.com/docs/whatsapp/on-premises/sunset) — 2025 — meta-developers
- [Webhook messages – text (referral object)](https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/text) — vigente — meta-developers
- [Conversions API for Business Messaging](https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging) — vigente — meta-developers
- [YCloud: pricing update 1-oct-2026](https://www.ycloud.com/blog/whatsapp-api-message-pricing-update-effective-october-1-2026) — 2026-09-04 — vendor
- [Wati: service messages and CTM ads](https://support.wati.io/en/articles/16954666-whatsapp-business-platform-api-pricing-changes-service-messages-and-click-to-message-ads) — 2026-09 — vendor
- [EU investigating Meta over WhatsApp AI chatbot ban](https://techcrunch.com/2025/12/04/eu-investigating-meta-over-policy-change-that-bans-rival-ai-chatbots-from-whatsapp/) — 2025-12-04 — prensa
- [EU antitrust order reopens WhatsApp to ChatGPT](https://www.techtimes.com/articles/320553/20260715/eu-antitrust-order-reopens-whatsapp-chatgpt-setting-precedent-ai-markets.htm) — 2026-07-15 — prensa
- [WhatsApp Business App coexistence with Cloud API](https://kapso.ai/blog/whatsapp-business-app-coexistence-cloud-api) — 2025–2026 — vendor

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Service messages: la franquicia de 1.000/número/mes no aparece en la doc oficial de precios para mensajes no plantilla ("Volume tiers: None"); presupuestar sin ella hasta verla en la factura. Fuente: developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages (leída 2026-10-16). **Actualización 2026-11-09**: la página general de precios sí la recoge (S10-118); la subpágina de no plantilla no (S10-119).
