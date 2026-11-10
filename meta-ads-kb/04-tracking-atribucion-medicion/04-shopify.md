# Shopify: Pixel, Conversions API, consentimiento y checkout extensibility

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: tiendas Shopify (Online Store y Plus) con Meta Ads: app "Facebook & Instagram by Meta", niveles de data sharing, web pixels, Customer Privacy API, migración de thank-you/order status, alternativas server-side y problemas frecuentes.

## TL;DR

- **Ruta por defecto recomendada:** canal/app **Facebook & Instagram by Meta** con *customer data sharing* en **Maximum** (Pixel + Conversions API) y **ningún otro Pixel de Meta** instalado (ni en el theme, ni como custom pixel, ni en otra app). La mayoría de los "Meta reporta 2–3× las compras de Shopify" vienen de implementaciones duplicadas sin `event_id` común. [OFFICIAL Shopify] (niveles, [S04-031]) + [EMPIRICAL] (duplicados, [S04-084])
- **Niveles de data sharing (Shopify Help Center 2026):** *Standard* = solo Pixel (bloqueable por ad blockers); *Enhanced* = Pixel + CAPI para el **evento Purchase** (comparte nombre, ubicación, email, teléfono); *Maximum* = Pixel + CAPI "con la tecnología publicitaria más reciente de Facebook", mismos datos que Enhanced. Las opciones visibles dependen de cuándo instalaste la app. [OFFICIAL Shopify] ([S04-031])
- **El valor de Purchase que envía la app es el total del pedido incluyendo impuestos, aranceles y descuentos.** Si comparas ROAS con un backend que usa ventas netas sin IVA, la diferencia es estructural. [OFFICIAL Shopify] ([S04-031])
- **Checkout extensibility es obligatorio:** desde el **28-ago-2025** los *additional scripts* son de solo lectura; las tiendas no-Plus tenían hasta el **26-ago-2026** para migrar las páginas Thank you / Order status (a fecha de hoy el plazo ha vencido; Shopify actualiza automáticamente). El tracking de compra debe vivir en **app pixels o custom pixels** (Web Pixels API). [OFFICIAL Shopify] ([S04-034])
- **Web pixels corren en sandbox:** app pixels en *strict sandbox* (web worker, sin DOM), custom pixels en *lax sandbox* (iframe, sin acceso al frame superior). No puedes "pegar" el snippet clásico del Pixel y esperar que lea el DOM; debes suscribirte a eventos estándar (`checkout_completed`, `product_added_to_cart`…) y usar `browser.cookie.get()` para leer cookies del frame superior. [OFFICIAL Shopify] ([S04-033])
- **Consentimiento:** los pixels gestionados por Shopify (app y custom) **respetan automáticamente** la Customer Privacy API: en regiones con consentimiento previo, los callbacks solo se ejecutan tras el consentimiento y se re-emiten los eventos anteriores; en regiones opt-out se ejecutan hasta que el usuario se opone (GPC respetado). [OFFICIAL Shopify] ([S04-032], [S04-033])
- **Server-side alternativo** (Stape, Elevar, Littledata, etc.) solo tiene sentido si necesitas algo que la app no cubre (eventos personalizados, margen/COGS, suscripciones, headless, multi-pixel, control de payload). Si lo usas, **pon la app nativa en el nivel que no envía CAPI** o desactiva su data sharing para no duplicar. [EMPIRICAL] ([S04-084]) + [STRONG INFERENCE]

## 1. Cómo funciona la integración nativa

### 1.1 Qué instala la app
- Conecta Business Manager, Pixel/dataset, catálogo (Facebook Shop/Instagram Shopping) y cuentas publicitarias. [OFFICIAL Shopify] ([S04-031])
- Eventos que la app documenta para el Pixel: `PageView`, `ViewContent`, `Search`, `AddToCart`, `InitiateCheckout`, `AddPaymentInfo`, `Purchase` (al ver la página de gracias). [OFFICIAL Shopify] ([S04-031])
- El Pixel se ejecuta como **app pixel** (Web Pixels API) — por eso funciona en checkout y thank-you sin acceso a `checkout.liquid`. [OFFICIAL Shopify] ([S04-033]) + [STRONG INFERENCE] (que la app de Meta use app pixel)
- En Enhanced/Maximum, Shopify envía eventos server-to-server con datos de cliente para el matching; la deduplicación con el Pixel la gestiona la integración (no requiere configurar `event_id`). [OFFICIAL Shopify] (data sharing) + [STRONG INFERENCE] (dedup interna)

### 1.2 Configurar el nivel
Shopify admin > **Sales channels > Facebook & Instagram > Settings > Data sharing settings** > activar *Customer data sharing* > elegir nivel > conectar Pixel. Requisito: política de privacidad que describa el intercambio de datos. [OFFICIAL Shopify] ([S04-031])

### 1.3 Qué nivel elegir

| Situación | Nivel recomendado | Motivo |
|---|---|---|
| Tienda estándar, sin otra herramienta server-side | **Maximum** | Máxima cobertura con mínima complejidad |
| Ya usas Stape/Elevar/otra solución que envía Purchase por CAPI al **mismo** dataset | Standard (o la app sin data sharing) | Evitar doble envío server-side con `event_id` distintos |
| Requisitos legales que impiden compartir PII con Meta | Standard (y revisa si incluso el Pixel procede) | Decisión jurídica, no de marketing |

Nota: algunas guías de terceros llaman "Conservative" al antiguo nivel *Standard*; el Help Center actual usa Standard/Enhanced/Maximum. [EMPIRICAL] (nomenclatura antigua) + [OFFICIAL Shopify] (nomenclatura actual)

## 2. Web Pixels API y custom pixels

### 2.1 Eventos estándar disponibles (Shopify)
`page_viewed`, `product_viewed`, `collection_viewed`, `search_submitted`, `product_added_to_cart`, `product_removed_from_cart`, `cart_viewed`, `checkout_started`, `checkout_contact_info_submitted`, `checkout_address_info_submitted`, `checkout_shipping_info_submitted`, `payment_info_submitted`, `checkout_completed`, `alert_displayed`, `ui_extension_errored`. [OFFICIAL Shopify] ([S04-089])

### 2.2 Custom pixel de Meta (solo si NO usas la app para el Pixel)

```js
// Shopify admin > Settings > Customer events > Add custom pixel
// Corre en un iframe sandbox: no hay acceso al DOM de la página.
// Quita las etiquetas <script>/<noscript> del snippet de Meta (el sandbox solo ejecuta JS) [S04-091].
// Limitaciones conocidas: el parámetro "dl" (URL) que envía fbevents.js puede ser la URL
// del sandbox, y no está claro que _fbp/_fbc escritas desde el iframe persistan en el
// dominio de la tienda (HIPÓTESIS). Lee las cookies del top frame con browser.cookie
// y, si necesitas fiabilidad, envía el Purchase también por CAPI con el mismo event.id.

!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
document,'script','https://connect.facebook.net/en_US/fbevents.js');
fbq('init', 'PIXEL_ID');

analytics.subscribe('page_viewed', (event) => {
  fbq('track', 'PageView', {}, { eventID: event.id });
});

analytics.subscribe('checkout_completed', (event) => {
  const c = event.data.checkout;
  fbq('track', 'Purchase', {
    value: c.totalPrice?.amount,
    currency: c.currencyCode,
    content_type: 'product',
    contents: c.lineItems.map(li => ({ id: li.variant?.id, quantity: li.quantity })),
    order_id: c.order?.id
  }, { eventID: event.id });   // event.id: ID único del evento Shopify → úsalo también en tu CAPI
});
```

- `event.id` de `checkout_completed` es un identificador único por evento que sirve como ancla de dedup si tu servidor (p. ej. vía webhook o sGTM alimentado por el mismo pixel) usa el mismo valor. [EMPIRICAL] ([S04-085])
- Problemas reportados por la comunidad con custom pixels de Meta: Purchase que no dispara en algunos checkouts, URL del sandbox en el parámetro `dl`, triggers que dependen de eventos del banner de cookies que el sandbox nunca recibe. [EMPIRICAL] (hilos de Shopify Community y Stape Community, 2024–2025) — otra razón para preferir la app nativa.
- Los IDs de producto deben coincidir con los del catálogo (la app nativa usa sus propios IDs de catálogo; si mezclas custom pixel + catálogo de la app, verifica el *match rate* en Commerce Manager). [STRONG INFERENCE]
- Nombres de campos (`totalPrice.amount`, `lineItems`, `variant.id`) según la estructura de los eventos de checkout de la Web Pixels API; verifica en tu tienda con el modo de prueba de Customer events. [STRONG INFERENCE]

### 2.3 Limitaciones del sandbox
- Sin DOM, sin `window.document` en app pixels; en custom pixels el iframe no accede al frame superior (`window.location` devuelve la URL del sandbox). [OFFICIAL Shopify] ([S04-033])
- Cookies y storage del frame superior solo vía `browser.cookie.get/set`, `browser.localStorage`, asíncronos. [OFFICIAL Shopify] ([S04-090])
- Peticiones cross-origin deben soportar CORS; usa `fetch(..., {keepalive: true})` (sendBeacon deprecado). [OFFICIAL Shopify]

## 3. Checkout extensibility y fechas

| Fecha | Qué pasó | Impacto en tracking |
|---|---|---|
| 2024–2025 | Migración Plus de `checkout.liquid` a checkout extensibility | Scripts en checkout sustituidos por pixels/extensions |
| **2025-08-28** | *Additional scripts* de Thank you/Order status pasan a solo lectura | No se pueden editar scripts de conversión heredados |
| **2026-08-26** | Fecha límite non-Plus para actualizar Thank you/Order status | Scripts heredados dejan de ejecutarse tras el upgrade; tracking solo vía app/custom pixels |

[OFFICIAL Shopify] ([S04-034]). Cuidado: si durante la transición convivieron *additional scripts* y un custom pixel, hubo **doble conteo** de Purchase. [EMPIRICAL] (comunidad/agencias)

## 4. Customer Privacy API y consentimiento

- Categorías: `preferences`, `analytics`, `marketing`, `sale_of_data`. Métodos recomendados para decidir si procesar: `marketingAllowed()`, `analyticsProcessingAllowed()`, `saleOfDataAllowed()` (combinan configuración del comerciante, ubicación y consentimiento registrado). [OFFICIAL Shopify] ([S04-032])
- En regiones con banner (p. ej. UE), sin consentimiento **no** se permiten propósitos no esenciales; en el resto, todo permitido por defecto salvo opt-out. GPC se respeta automáticamente en regiones opt-out y fija `sale_of_data=false`. [OFFICIAL Shopify] ([S04-032])
- Los pixels de Shopify "honran" el consentimiento sin llamar a la API; en regiones con consentimiento requerido los eventos se re-emiten tras aceptar. [OFFICIAL Shopify] ([S04-033])
- **CMP de terceros** (Cookiebot, OneTrust, Pandectes…): deben escribir el consentimiento en la Customer Privacy API (`setTrackingConsent`) para que los pixels lo respeten. Si el CMP bloquea scripts del theme pero no informa a Shopify, los web pixels pueden ejecutarse con un estado distinto al del banner. [OFFICIAL Shopify] (API) + [STRONG INFERENCE] (riesgo de desalineación)
- Server-side por webhooks de pedido: el webhook no "sabe" el consentimiento del navegador; guarda el estado de consentimiento en el pedido (atributos de carrito/checkout) y fíltralo antes de enviar a CAPI. [STRONG INFERENCE]

## 5. Casos especiales

| Caso | Problema | Solución |
|---|---|---|
| **Upsells post-compra** (apps de one-click upsell) | Pedido adicional o edición del pedido que no siempre dispara `checkout_completed` | Verificar si la app emite evento propio; si no, enviar Purchase/valor adicional por CAPI desde webhook `orders/create`/`orders/edited` con `event_id` distinto y controlado |
| **Suscripciones (renovaciones)** | No hay sesión de navegador | CAPI server-only desde la plataforma de suscripción (evento `Purchase` o custom `SubscriptionRenewal`); decidir si se optimiza con renovaciones (normalmente no) |
| **Pedidos borrador / POS / B2B** | Sin navegador; Shopify los etiqueta como "Direct" | Offline (`physical_store`) o excluir de comparativas web |
| **Headless (Hydrogen/custom)** | La app nativa no cubre el storefront headless | Implementación propia: Pixel + CAPI, Customer Privacy API en el storefront, mismo `event_id` |
| **Multi-moneda (Markets)** | Valor en moneda de presentación vs moneda de tienda | Comprobar en Test Events qué `currency` llega y que coincide con `value`; Meta convierte a la moneda de la cuenta publicitaria (no verificado el tipo de cambio aplicado) |
| **Shop Pay / pasarelas externas** | El usuario puede no volver a la thank-you page | El Purchase server-side (Enhanced/Maximum) cubre el hueco; con Standard se pierden compras |

[STRONG INFERENCE] salvo donde se indica; la casuística de upsells y suscripciones depende de cada app.

## 6. Diagnóstico de discrepancias Shopify ↔ Meta

1. **¿Meta > Shopify?** Busca Purchase duplicados: Pixel Helper en la thank-you page (¿dos `Purchase`? ¿dos Pixel IDs?), Events Manager por "connection method", Customer events (¿custom pixel de Meta además de la app?), theme (`theme.liquid` con `fbq`), apps de reviews/upsell que inyectan Pixel. [EMPIRICAL] ([S04-084])
2. **¿Meta < Shopify?** Normal en parte (Meta solo cuenta compras atribuibles en ventana a personas emparejadas y con consentimiento). Revisa nivel de data sharing (Standard pierde ad-blocked), consentimiento UE, `fbclid` perdido en redirecciones de apps de idioma/moneda, Purchase sin `value`. Ver árbol completo en `16-checklist-qa-y-diagnostico-tracking.md`.
3. **Modelos distintos:** Shopify atribuye por defecto con *last non-direct click* (30 días) y solo ve sesiones; Meta cuenta clics de enlace, engage-through y view-through según la ventana. [EMPIRICAL] ([S04-080]) — ver archivo 11.

## Implicaciones operativas

- **Hacemos:** app nativa en Maximum como base; inventario de todos los lugares donde vive un `fbq` (theme, apps, custom pixels) y eliminación de duplicados; CMP integrado con Customer Privacy API; prueba de compra real tras cada cambio de app de checkout/upsell/idioma.
- **Evitamos:** instalar "apps de CAPI" encima de la app nativa en Maximum; pegar scripts en `theme.liquid` para eventos que la app ya envía; asumir que un custom pixel ve el DOM.
- **Umbral:** Purchase en Meta (Events Manager, no Ads Manager) ≈ pedidos online con consentimiento ± 5 %; si Events Manager > pedidos → duplicación.

## Errores frecuentes

1. Doble Pixel (app + custom pixel/theme) con `event_id` distinto → doble conteo.
2. Herramienta server-side de terceros + app en Maximum → dos Purchase server con IDs diferentes.
3. Asumir que el valor es neto (es total con impuestos/descuentos aplicados).
4. CMP que no comunica el consentimiento a Shopify.
5. Ignorar upsells y suscripciones en la reconciliación.

## Preguntas abiertas

- Qué eventos exactos envía por CAPI el nivel Maximum frente a Enhanced (Shopify solo dice "Purchase" para Enhanced y "la tecnología más reciente" para Maximum; las guías de terceros afirman que Maximum envía más eventos server-side — no verificado oficialmente).
- Moneda que envía la app en tiendas multi-moneda (no verificado).
- Si la app nativa permite ya enviar margen (`net_revenue`) o solo lo hacen soluciones de terceros (no verificado).

## Fuentes clave

- [Meta customer data-sharing (Shopify Help Center)](https://help.shopify.com/en/manual/promoting-marketing/analyze-marketing/meta-data-sharing) — vigente 2026 — vendor (S04-031)
- [Customer Privacy API](https://shopify.dev/docs/api/customer-privacy) — vigente — vendor (S04-032)
- [Web pixels](https://shopify.dev/docs/apps/build/marketing-analytics/pixels) — vigente — vendor (S04-033)
- [Upgrading Thank you and Order status pages](https://help.shopify.com/en/manual/checkout-settings/checkout-extensibility/checkout-upgrade) — vigente — vendor (S04-034)
- [Web Pixels API standard events](https://shopify.dev/docs/api/web-pixels-api/standard-events) — vigente — vendor (S04-089)
- [Web Pixels API browser](https://shopify.dev/docs/api/web-pixels-api/standard-api/browser) — vigente — vendor (S04-090)
- [Create custom pixel code](https://help.shopify.com/en/manual/promoting-marketing/pixels/custom-pixels/code) — vigente — vendor (S04-091)
- [Hilo comunidad Shopify: Meta 2–3× compras](https://community.shopify.com/t/meta-has-2-3x-times-purchases-shopify-data-in-meta-is-wrong-and-i-need-help-to-fix-it/404737) — 2025 — comunidad (S04-084)
- [Event Deduplication on Shopify](https://www.weltpixel.com/blogs/news/event-deduplication-on-shopify-how-event-id-prevents-double-counting) — 2026 — vendor (S04-085)
