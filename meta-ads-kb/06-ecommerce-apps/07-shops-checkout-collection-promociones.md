# Shops, checkout en Meta, collection ads / Instant Experience, Shops ads y promociones en anuncios

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: estado 2026 de Facebook/Instagram Shops y del checkout dentro de Meta (EE. UU. vs resto), Shops ads, colecciones/Instant Experience, nuevos flujos de compra (Muse, Messenger, Meta AI) y cómo comunicar ofertas en anuncios.

## TL;DR

- **El checkout nativo en Facebook/Instagram Shops (solo existió en EE. UU.) se retiró en 2025**: despliegue gradual desde junio-2025, la mayoría de tiendas migradas a finales de agosto-2025 (algunas fuentes dicen septiembre), con excepciones para integraciones de OMS de terceros. Las Shops siguen existiendo como escaparate; la compra termina en la web del comerciante (normalmente dentro del navegador in-app). [OFFICIAL META vía prensa — Value Added Resource cita el Help Center]
- **Fuera de EE. UU. nunca hubo checkout nativo general**: Shops en España/UE siempre fue *link-out* a la web (o checkout por mensajes). Así que para un anunciante europeo el cambio de 2025 casi no altera nada; lo que importa es la **experiencia de checkout en el navegador in-app** (velocidad, Shop Pay/Apple Pay/PayPal, autocompletado). [OFFICIAL META/Shopify Help] + [STRONG INFERENCE]
- **Meta reintroduce la compra "sin salir de la app" por otra vía (2026)**: checkout de un toque con Stripe y PayPal anunciado en Shoptalk (25-mar-2026, en test), Muse con Link by Stripe, Shop Pay y PayPal; y en oct-2026 tests de checkout en Messenger (Meta Business Agent + Shopify) y en Meta AI (Adyen, PayPal, Shopify, Stripe). Todo en **test**, sin calendario ni países confirmados. [OFFICIAL META vía TechCrunch y Relevant Audience]
- **Shops ads** hoy = mejora sobre campañas de Ventas con destino "web y tienda" (`WEBSITE_AND_SHOP`): Meta decide si enviar a la web o a la Shop; el checkout es offsite con navegador in-app. No admite formato colección. Requiere Shop con `OFFSITE_IAB_CHECKOUT` en países elegibles. [OFFICIAL META]
- **Collection ads / Instant Experience siguen vivos** (no hay deprecación localizada), pero desde mar-2026 se encuentran en "Opciones de visualización del formato" dentro de la creatividad, no como formato principal. Requisitos: Instant Experience, product set con ≥ 4 productos, solo móvil. Útiles para catálogos visuales; menos para monoproducto. [EMPIRICAL — varias guías 2026] / [OFFICIAL META] (portada por defecto = vídeo de catálogo generado)
- **Promociones**: Meta permite mostrar códigos y ofertas en anuncios ("Highlight your promotions"/Offers), detectándolos en la creatividad, la web o en ofertas sincronizadas (p. ej. desde Shopify). En 2024 añadió formatos de oferta en Reels (códigos, primera compra, descuentos personalizados). Úsalo, pero **controla qué códigos se exponen**: hay reportes de que Meta muestra ofertas sincronizadas que el comerciante creía desactivadas. [EMPIRICAL — practitioners/comunidad; doc oficial no localizada]
- **Implicación económica**: cada descuento mostrado por Meta baja el CM2 del pedido. Un código de bienvenida del 15 % sobre un CM2 del 45 % reduce el margen de contribución del pedido ~un tercio. Recalcula el break-even (ver `05-…`). [STRONG INFERENCE]

## 1. Cronología de Shops y checkout

| Fecha | Hecho | Etiqueta |
|---|---|---|
| 2019 | Checkout on Instagram en beta cerrada, solo EE. UU. | [OFFICIAL META vía prensa] |
| 10-ago-2023 | En EE. UU. ya no se pueden crear Shops sin checkout en FB/IG | [EMPIRICAL — Jon Loomer] |
| 24-abr-2024 | En EE. UU., Shops sin checkout dejan de ser accesibles | [EMPIRICAL — Jon Loomer; Value Added Resource] |
| Jun-2025 | Meta inicia la retirada del checkout nativo: Shops pasan a "website checkout" | [OFFICIAL META vía prensa] |
| Finales ago-2025 (algunas fuentes: sep-2025) | La mayoría de Shops migradas; las integradas con OMS de terceros (Magento/Adobe Commerce) más tarde | [OFFICIAL META vía prensa] |
| 26-ago-2025 | Meta deja de ser *marketplace tax facilitator* en pedidos de FB/IG (EE. UU.); el comerciante recauda impuestos | [OFFICIAL — Shopify Help] |
| 25-mar-2026 | Shoptalk: test de ventana IA con resumen de reseñas e info de producto tras clic; checkout de un toque con Stripe y PayPal (Adyen y Shopify "en camino"); el anunciante elige partner | [OFFICIAL META vía TechCrunch] |
| 29-jul-2026 (Graph/Marketing API v26.0) | Changelog oficial: "Checkout on Facebook and Instagram Shops has been discontinued"; la **Commerce Order Management API (47 endpoints) queda deprecada** (bloqueada en v26 desde 29-jul y en todas las versiones el **27-oct-2026**, sin sustituto). Además, desde v26 las creatividades elegibles de anunciantes con Shop pasan por defecto a destino `WEBSITE_AND_SHOP` (opt-out con `WEBSITE_AND_SHOP_OPT_OUT`) | [OFFICIAL META] |
| 26/29-sep-2026 | Muse: compra con Shop Pay en tiendas Shopify (incl. gafas IA); "Muse for Small Business" conecta cuentas publicitarias, Shopify, Klaviyo, Canva | [EMPIRICAL — CTC; verificar] |
| 6-oct-2026 | Advertising Week NY: checkout directo en Messenger (Meta Business Agent + Shopify) **en test**; checkout en Meta AI (Adyen, PayPal, Shopify, Stripe) **en test este otoño**; PayPal wallet añadido a Muse junto a Link by Stripe y Shop Pay | [OFFICIAL META vía Relevant Audience] |

### Qué perdieron los comerciantes de EE. UU. con la retirada (2025)

Procesamiento de pagos de Shops (acceso de solo lectura a saldos/pagos por un tiempo), gestión de pedidos en Commerce Manager (estado, gestión masiva, disputas/contracargos), devoluciones y mensajería de Inbox vinculada a pedidos. Shopify avisó de posible pérdida temporal de atribución de pedidos de FB/IG durante la transición. Para anuncios: cambian ubicaciones de conversión y eventos disponibles; el reporting de métricas de checkout "on-Meta" cambia o se discontinúa. [OFFICIAL META vía Value Added Resource]

## 2. Shops ads (estado 2026)

Documentación de Marketing API [OFFICIAL META]:

- Es una **mejora aditiva** para campañas de Ventas: el shopper descubre productos y arma carrito en FB/IG; **la compra ocurre en la web del anunciante** (offsite checkout con navegador in-app).
- Destino de creatividad `WEBSITE_AND_SHOP`: Meta elige entre web y Shop según rendimiento esperado.
- Requisitos: Shop con CTA `OFFSITE_IAB_CHECKOUT` y al menos un país en `offsite_iab_checkout_enabled_countries`; Página/IG conectados a la Shop y catálogo conectado; objetivo `OUTCOME_SALES` (basado en catálogo o en pixel); eventos soportados ADD_TO_WISHLIST, ADD_TO_CART, INITIATE_CHECKOUT, PURCHASE, VIEW_CONTENT; optimización `OFFSITE_CONVERSIONS` o `VALUE`; placements en FB/IG.
- Creatividades: carrusel; imagen/vídeo solo en campañas basadas en pixel; Advantage+ creative for catalog soportado. **No soporta colección**, CTAs de mensajería ni destinos app/evento/Instant Experience en pixel-based.
- Una Shop puede pasar de `ONSITE_CHECKOUT` a `OFFSITE_IAB_CHECKOUT` pero no al revés.
- **Desde Marketing API v26.0 (29-jul-2026)**, si el anunciante tiene Shop, las creatividades elegibles usan `WEBSITE_AND_SHOP` **por defecto**; para mantener solo web hay que hacer opt-out (`WEBSITE_AND_SHOP_OPT_OUT`). Revisa si tus anuncios están enviando tráfico a la Shop sin que lo hayas decidido. [OFFICIAL META — changelog v26]
- Integraciones que leían pedidos de Shops (OMS, ERPs) vía Commerce Order Management API dejan de funcionar en todas las versiones el 27-oct-2026. [OFFICIAL META]

**¿Merece la pena en 2026?** [STRONG INFERENCE] Shops ads es interesante cuando la Shop tiene buena experiencia de descubrimiento (colecciones, varios productos) y la web es lenta en móvil; si tu web es rápida y con checkout acelerado, la diferencia esperable es pequeña. Testéalo como A/B (destino web vs web+shop) y mide en tienda, no solo en Meta (la atribución de pedidos vía Shop ha tenido problemas en la transición).

## 3. Collection ads e Instant Experience

| Aspecto | Estado 2026 |
|---|---|
| Existencia | Sigue disponible; no hay anuncio de retirada localizado. [EMPIRICAL] |
| Ubicación en UI | Desde mar-2026, en "Opciones de visualización del formato" dentro de la creatividad (junto a Flexible). [EMPIRICAL — guía may-2026] |
| Requisitos | Instant Experience; product set ≥ 4 productos válidos; solo móvil; una Instant Experience terminada no se edita in situ. [EMPIRICAL] |
| Portada | Por defecto "Advantage catalog video" generado por usuario; o imagen/vídeo propio. Con Allow product video, la portada "Dynamic Video" se sustituye por vídeo de producto. [OFFICIAL META] |
| Format automation | Meta puede elegir carrusel o colección por impresión. [OFFICIAL META] |

**Cuándo usar colección** [STRONG INFERENCE]:
- Catálogos visuales (moda, decoración) donde ver 4 productos a la vez ayuda.
- Lanzamientos de colección/temporada con vídeo de portada fuerte.
- Retail con muchas referencias y web lenta (la Instant Experience carga rápido).

**Cuándo no**: monoproducto, productos que requieren explicación, o cuando la landing es el diferencial (quiz, bundles, comparativas).

## 4. Promociones y ofertas en anuncios

### 4.1 Funciones de Meta

| Función | Qué hace | Estado/fuente |
|---|---|---|
| **Offers / "Highlight your promotions"** | A nivel anuncio; muestra un código/oferta. Meta puede detectar códigos en la creatividad, el inventario de anuncios, la web o ofertas sincronizadas en Commerce Manager; si hay varios, muestra el que predice mejor | [EMPIRICAL — Jon Loomer (2024), Birch]; detalle actual no verificado en Help Center |
| **Ofertas en Reels (holiday 2024)** | Códigos promocionales, ofertas de primera compra y descuentos personalizados en anuncios de Reels | [OFFICIAL META vía prensa, 17-sep-2024] |
| **Sincronización de ofertas desde Shopify** | Comunidad: Account Center → Promociones → Ofertas → sincronizar con Shopify (cada ~15 min) | [EMPIRICAL, comunidad — baja] |
| **Dynamic overlays de catálogo** | Superponer precio/descuento del feed (`sale_price`) | [OFFICIAL META] |
| **Reminder ads** | Recordatorios de lanzamientos/ventas; desde 2024 pueden llevar a apps | [OFFICIAL META vía prensa] |
| **Site links** | Varios enlaces en un anuncio de Facebook Feed | [OFFICIAL META vía prensa] |

**Riesgo operativo** [EMPIRICAL, comunidad Shopify]: comerciantes reportan que Meta mostraba ofertas sincronizadas de Shopify que creían desactivadas o que la app de Facebook generaba cupones. Revisa periódicamente qué ofertas tiene Meta y no sincronices descuentos de retención/VIP.

### 4.2 Diseño de ofertas desde la economía

Fórmula: CM2 tras descuento = CM2 sin descuento − d × revenue (base coherente).

Ejemplo (pedido de 40 € sin IVA, CM2 22 € = 55 %):
- Descuento 10 % → CM2 18 € (−18 %) → el CPA break-even baja de 22 € a 18 € (antes de f).
- Descuento 20 % → CM2 14 € (−36 %).
- **Para que un 20 % sea neutro en margen, la tasa de conversión o el AOV deben subir lo suficiente para compensar ~36 % de CM2 por pedido**, o la oferta debe traer clientes con mejor LTV. [STRONG INFERENCE]

Jerarquía de ofertas preferible (de mayor a menor protección de margen) [STRONG INFERENCE + práctica DTC]:
1. Valor añadido (regalo de bajo coste, envío gratis por encima de umbral que sube AOV).
2. Bundles (2× / 3× con descuento escalonado: sube AOV y diluye el coste de envío).
3. Descuento de primera compra condicionado (suscripción, email).
4. Descuento porcentual general (BFCM).

## 5. Nuevos flujos de compra dentro de Meta (2026): qué hacer ya

[STRONG INFERENCE sobre recomendaciones; hechos de estado en §1]

- **No hay nada que activar a escala en España/UE a oct-2026**: los checkouts en Messenger y Meta AI están en test; el checkout de un toque con Stripe/PayPal no tiene calendario público.
- **Prepararse**: catálogo con títulos/atributos claros (los agentes recomiendan desde datos de catálogo), métodos de pago acelerados en tu web (Shop Pay, Apple Pay, Google Pay, PayPal, Link), políticas de envío/devolución claras en el feed.
- **Medición**: cuando la compra ocurra dentro de Meta, el evento de conversión puede no pasar por tu web; exige que la plataforma de e-commerce/partner de pago devuelva el pedido a tu OMS y a Meta (CAPI) para no duplicar ni perder conversiones.
- **CTC** sugiere testear el botón de compra dentro del anuncio primero en productos < 50 $ de decisión simple; tickets altos seguirán necesitando landing. [EMPIRICAL, agencia]

## Implicaciones operativas

- Para cuentas europeas: trata Shops como escaparate opcional; el trabajo de conversión está en la landing/checkout in-app de tu web.
- Antes de temporada alta: auditar velocidad móvil del navegador in-app, métodos de pago acelerados y que los códigos promocionales funcionen desde el navegador de IG/FB.
- Si usas Shops ads, haz A/B de destino y mide en tienda.
- Controla las ofertas que Meta muestra; documenta qué descuentos son públicos.
- Recalcula CPA/ROAS break-even para cada nivel de descuento.

## Errores frecuentes

- Esperar que "Instagram Shopping" resuelva la conversión en Europa.
- Activar sincronización de ofertas sin revisar qué códigos se exponen.
- Hacer descuentos del 20–30 % sin recalcular el break-even.
- Usar colección para un monoproducto que necesita explicación.
- No probar el checkout desde el navegador in-app (cookies, login, pasarelas que fallan).

## Preguntas abiertas

- Calendario y países del checkout de un toque (Stripe/PayPal) y de los checkouts en Messenger/Meta AI.
- Cómo se atribuirán y reportarán compras completadas dentro de Meta (¿evento on-Meta o CAPI del comerciante?).
- Estado oficial actual de "Offers"/"Highlight your promotions" (no localizada doc oficial 2026).
- Si la retirada del checkout de 2025 tuvo excepciones definitivas (pre-orders de Shopify, OMS de terceros).

## Fuentes clave

- [Meta Phases Out Native Checkout For Facebook & Instagram Shops](https://www.valueaddedresource.net/meta-phases-out-native-checkout-facebook-instagram-shops/) — 2025-06-04 — prensa (cita Help Center)
- [Meta Is Dropping Native Checkout on Facebook and Instagram Shops (GoDataFeed)](https://www.godatafeed.com/blog/meta-is-dropping-native-checkout-on-facebook-and-instagram) — 2025 — vendor
- [Meta turns to AI to make shopping easier on Instagram and Facebook (TechCrunch)](https://techcrunch.com/2026/03/25/meta-turns-to-ai-to-make-shopping-easier-on-instagram-and-facebook/) — 2026-03-25 — prensa
- [Meta Advertising Week NY 2026 Ad Tools: Live vs Testing](https://www.relevantaudience.com/meta/meta-advertising-week-new-york-2026-ad-tools/) — 2026-10 — agencia
- [Shops ads (Marketing API)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/shops-ads.md) — Meta for Developers — meta-developers
- [Graph API changelog v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) — 2026-07-29 — meta-developers
- [Advantage+ creative for catalog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-creative-for-catalog.md) — Meta for Developers — meta-developers
- [Facebook & Instagram by Meta requirements (Shopify Help)](https://help.shopify.com/en/manual/online-sales-channels/facebook-instagram-by-meta/requirements) — 2025-2026 — vendor (plataforma)
- [Shops in the US after April 24th (Jon Loomer)](https://www.jonloomer.com/qvt/shops-in-the-us-after-april-24th/) — 2024 — practitioner
- [Meta Collection Ads Guide 2026 (AdLibrary)](https://adlibrary.com/posts/meta-collection-ads-guide) — 2026 — vendor
- [Highlight Promo Codes in Your Ads (Jon Loomer)](https://www.jonloomer.com/qvt/highlight-promo-codes-in-your-ads/) — 2024 — practitioner
- [Meta adds new ad formats that display promotional offers on Instagram Reels](https://www.thekeyword.co/news/meta-introduces-new-promotion-features-for-advertisers) — 2024-09-17 — prensa
- [Every Meta Ads Change in 2026 (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026) — 2026 — agencia
- [Meta Advantage+ Shopping Campaigns in 2026 (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-advantage-shopping-campaigns-in-2026) — 2026 — agencia
