# WordPress y WooCommerce: plugins oficiales y de terceros (estado 2026)

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: sitios WordPress (lead gen) y tiendas WooCommerce. Estado de plugins verificado vía API pública de wordpress.org y repositorio GitHub de Meta el 2026-10-16.

## TL;DR

- **WooCommerce: el plugin oficial "Meta for WooCommerce" (antes "Facebook for WooCommerce") es la opción por defecto en 2026.** v3.7.8 (5-oct-2026), 400.000+ instalaciones activas, mantenido por Meta en GitHub (`facebook/facebook-for-woocommerce`), con Pixel + CAPI integrados y deduplicación por `event_id`. [OFFICIAL META] ([S04-035])
- **Novedades relevantes del plugin oficial (2025–2026):** usa la *Parameter Builder Library* de Meta (`capi-param-builder`); envía margen (`net_revenue`) si hay COGS en WooCommerce o en WPFactory; controles **hold/release de señales** para integraciones de consentimiento (`window.fbwcsignal.hold()/release()`), que encolan eventos y los reenvían en un batch a CAPI al liberar; opción (opt-in) para enviar compras de tienda física como eventos offline; múltiples correcciones de duplicados (AddToCart por fragmentos AJAX, Purchase CAPI duplicado en checkout, renovaciones de suscripción). [OFFICIAL META] ([S04-035], [S04-036])
- **WordPress sin WooCommerce (lead gen): "Meta pixel for WordPress"** (plugin oficial, v5.2.2, jul-2026, 400.000+ instalaciones) instala Pixel y soporta CAPI para formularios populares. [OFFICIAL META] ([S04-086])
- **Terceros consolidados:** PixelYourSite (v11.4.2.1, sep-2026, 400.000+; CAPI de Meta incluida en la versión gratuita) y Pixel Manager for WooCommerce (v1.70.0, 13-oct-2026; CAPI solo en Pro). Ambos priorizan integración con CMPs y control fino del payload. [EMPIRICAL] (datos del repositorio wordpress.org, [S04-087], [S04-088])
- **Regla de oro: un solo sistema emisor por evento y por Pixel.** Oficial + PixelYourSite + GTM + theme a la vez es la causa nº 1 de duplicados en WooCommerce. El debug report de Pixel Manager ya lista otros plugins de tracking activos precisamente por esto. [EMPIRICAL] ([S04-088])
- **Caché de página completa** (WP Rocket, LiteSpeed, Varnish, Cloudflare APO) puede servir el mismo `eventID` o el mismo `fbq('init', {em: …})` a todos los visitantes: excluye checkout/thank-you de caché y genera IDs en cliente. [STRONG INFERENCE]

## 1. Estado de plugins (verificado 2026-10-16)

| Plugin | Mantenedor | Versión / fecha | Instalaciones | CAPI | Notas |
|---|---|---|---|---|---|
| Meta for WooCommerce (`facebook-for-woocommerce`) | Meta | 3.7.8 · 2026-10-05 | 400k+ | Sí, integrada | Catálogo, Shops, WhatsApp; Param Builder; `net_revenue`; hold/release; offline opt-in |
| Meta pixel for WordPress (`official-facebook-pixel`) | Meta | 5.2.2 · 2026-07-23/27 | 400k+ | Sí | Integraciones con formularios y WooCommerce/YITH |
| PixelYourSite (`pixelyoursite`) | PixelYourSite | 11.4.2.1 · 2026-09-27 | 400k+ | Sí (free) | Consent filters, `external_id` determinista por sitio (11.4.2), eventID persistido para Purchase |
| Pixel Manager for WooCommerce (`woocommerce-google-adwords-conversion-tracking-tag`) | SweetCode | 1.70.0 · 2026-10-13 | 40k+ | Solo Pro | Respeta estado previo del banner de CMPs (Complianz, Cookiebot, CookieYes, OneTrust, iubenda, Usercentrics) desde 1.70.0 |

Fuente: API de plugins de wordpress.org y changelogs (consultados 2026-10-16). [OFFICIAL META] para los dos oficiales; [EMPIRICAL] para terceros.

## 2. Meta for WooCommerce en detalle

### 2.1 Qué envía
- Eventos de Pixel y CAPI para el embudo (ViewContent, AddToCart, InitiateCheckout, Purchase, Search…), deduplicados por `event_id` único. [OFFICIAL WooCommerce docs] (citado en búsqueda; doc. "Meta for WooCommerce Documentation")
- Purchase con `contents` (corregido en 3.7.8 un caso de Purchase sin contents al crear pedidos). [OFFICIAL META] ([S04-035])
- **Margen**: si todas las líneas del pedido tienen COGS (WooCommerce COGS nativo o WPFactory), calcula el margen y lo envía en `net_revenue` en Purchase y AddToCart (prioriza COGS nativo). [OFFICIAL META] (PR #3730, [S04-036]) — útil si Meta te habilita optimización por margen (beta). Revisa que el COGS esté completo: si falta en un producto, no se envía para ese pedido.
- **Offline**: opt-in para reportar compras de tienda física como eventos offline (3.7.8). [OFFICIAL META] ([S04-035])

### 2.2 Hold/release de señales (consentimiento)
PR #3914 (2026): API JS pública `window.fbwcsignal.hold()`, `release()`, `getState()`. Mientras está en *hold*, los eventos de frontend se encolan en el navegador y se suprimen los envíos CAPI de peticiones públicas (los de admin/cron siguen); al *release*, se envían en una única llamada batch a CAPI, se escriben `_fbp`/`_fbc` con el mismo dominio que usa el Param Builder PHP y se rearma el Pixel. Incluye rate-limit (80 eventos/5 min por IP por defecto). [OFFICIAL META] ([S04-036])

Implicación: permite integrar un CMP de forma que **no se pierdan los eventos previos al consentimiento si el usuario acepta**, y que no se envíen si no acepta. Si tu CMP no llama a `release()`, nada se envía → verifica la integración. [STRONG INFERENCE]

### 2.3 Configuración recomendada
1. Instalar el plugin oficial, conectar con Meta (FBE) eligiendo Business, Pixel/dataset y catálogo.
2. Verificar en Events Manager que hay eventos "Browser" y "Server" con dedup alto.
3. Desactivar cualquier otro Pixel de Meta (theme, PixelYourSite, GTM) **o** desactivar el Pixel del plugin oficial si mantienes otra solución (no ambos).
4. Excluir carrito/checkout/thank-you de caché.
5. Probar pago con cada pasarela (Stripe, PayPal, Redsys, Bizum…): muchas redirigen fuera y el usuario puede no volver a la página de pedido recibido → el Purchase server-side es el que cuenta.

### 2.4 Trampas específicas de WooCommerce

| Trampa | Por qué rompe el tracking | Mitigación |
|---|---|---|
| Pasarelas con redirección (TPV bancarios, PayPal, Bizum vía TPV, Klarna) | El usuario puede no volver a "pedido recibido" → no hay Purchase de navegador; si el Purchase server-side se dispara solo al cargar esa página, también se pierde | Disparar Purchase server-side al cambiar el pedido a *processing/completed* (hook de estado o webhook), con `event_id` = ID de pedido |
| Estados de pedido | Contar *pending* o *on-hold* (transferencias) infla Purchase; no contar *completed* manuales lo infra-cuenta | Definir qué estados = venta y alinear el evento con esa regla |
| Checkout por bloques (Cart/Checkout Blocks) y Store API | Eventos AJAX distintos al checkout clásico; algunos plugins no los cubrían | Versiones recientes del plugin oficial añadieron soporte de Store API para AddToCart [OFFICIAL META] ([S04-035]); probar ambos flujos |
| Plugins de caché/minificación JS | Retrasan o rompen `fbq` y scripts del Pixel | Excluir scripts de Meta de la combinación/diferido o probar tras cada cambio |
| Varios dominios (tienda + subdominio de pago o landing externa) | `_fbp`/`_fbc` no se comparten; `fbclid` se pierde | Persistir `fbc` en servidor y pasarlo al dominio de pago |
| Pedidos de prueba y manuales desde el admin | Purchase de pedidos que no proceden de anuncios ni del navegador | Excluir por origen del pedido o enviar con `action_source` veraz |

[STRONG INFERENCE] salvo donde se indica; los nombres de pasarelas son ejemplos habituales en España.

## 3. WordPress para lead gen

- **Meta pixel for WordPress** detecta envíos de formularios de plugins populares (Contact Form 7, Gravity Forms, WPForms, Ninja Forms, etc., según su documentación histórica — verifica tu plugin de formularios) y envía `Lead` por Pixel y CAPI. [OFFICIAL META] (plugin) + [STRONG INFERENCE] (lista de integraciones no reverificada en 2026)
- **Calidad del Lead:** dispara `Lead` solo tras validación del formulario (no en el clic del botón) y pasa email/teléfono para EMQ. Si el lead se cualifica en un CRM, el evento valioso es posterior (ver `08-eventos-offline-y-crm.md`).
- Alternativa: GTM web + sGTM (archivo 06) cuando hay varios formularios, landings externas o necesitas controlar consentimiento centralizado.

## 4. Matriz de decisión

| Situación | Recomendación |
|---|---|
| WooCommerce estándar, catálogo en Meta | Meta for WooCommerce (Pixel+CAPI) y nada más |
| Necesitas multi-plataforma (Meta+TikTok+Pinterest+GA4) desde un plugin | PixelYourSite o Pixel Manager Pro **en lugar** del Pixel del oficial (el oficial puede seguir gestionando catálogo con su Pixel desactivado — verificar en la versión actual que la sincronización de catálogo no dependa del Pixel) |
| Equipo técnico, consent centralizado, varios dominios | GTM web + sGTM (Stape/propio) con el tag oficial de CAPI |
| Lead gen sin WooCommerce | Meta pixel for WordPress o GTM; CRM → CAPI para etapas posteriores |

[STRONG INFERENCE] salvo donde se indica.

## Implicaciones operativas

- **Hacemos:** inventario de plugins de tracking; un emisor por evento; pruebas por pasarela de pago; caché excluida en checkout; revisar changelog del plugin oficial en cada actualización mayor (Meta corrige duplicados con frecuencia).
- **Evitamos:** actualizar plugins de tracking en caliente sin una compra de prueba posterior; dejar dos plugins con CAPI activa al mismo dataset.
- **Umbral:** pedidos WooCommerce "completados/procesando" (con consentimiento) ≈ Purchase server en Events Manager ± 5 %.

## Errores frecuentes

1. Purchase disparado en `thankyou` con recargas → duplicados si el `eventID` no se persiste (PixelYourSite 11.4.2 corrigió precisamente la persistencia del eventID en la primera vista de thank-you). [EMPIRICAL] ([S04-087])
2. AddToCart duplicado por fragments AJAX (corregido en Meta for WooCommerce #3939). [OFFICIAL META] ([S04-035])
3. Pedidos de suscripción renovados que no envían Purchase por CAPI (corregido en #3946) o, al revés, renovaciones que inflan el ROAS de prospecting. [OFFICIAL META] ([S04-035]) + [STRONG INFERENCE]
4. Caché que congela PII o `eventID`.
5. Token CAPI inválido que bloquea CAPI silenciosamente (el oficial ahora bloquea CAPI de forma incondicional si el token es inválido, #3966): revisa avisos del plugin. [OFFICIAL META] ([S04-035])

## Preguntas abiertas

- ¿El plugin oficial permite elegir nivel de PII compartida como Shopify? No verificado.
- Rendimiento comparado (EMQ, cobertura) oficial vs PixelYourSite vs Pixel Manager: no hay benchmarks independientes.

## Fuentes clave

- [Meta for WooCommerce (wordpress.org)](https://wordpress.org/plugins/facebook-for-woocommerce/) — v3.7.8 2026-10-05 — meta-oficial (S04-035)
- [PR #3914 Signal state controls](https://github.com/facebook/facebook-for-woocommerce/pull/3914) — 2026 — meta-developers (S04-036)
- [Meta pixel for WordPress](https://wordpress.org/plugins/official-facebook-pixel/) — v5.2.2 2026-07 — meta-oficial (S04-086)
- [PixelYourSite](https://wordpress.org/plugins/pixelyoursite/) — v11.4.2.1 2026-09-27 — vendor (S04-087)
- [Pixel Manager for WooCommerce](https://wordpress.org/plugins/woocommerce-google-adwords-conversion-tracking-tag/) — v1.70.0 2026-10-13 — vendor (S04-088)
