# Google Tag Manager web y server-side (sGTM, Stape) para Meta Pixel + CAPI

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: Pixel en GTM web, CAPI vía server-side GTM con el tag oficial de Meta o el de Stape, deduplicación, cookies first-party, consentimiento y QA. Las plantillas se verificaron leyendo su código en GitHub.

## TL;DR

- **Arquitectura estándar documentada por Meta:** GTM web (GA4 config con `transport_url` a tu servidor + GA4 events) → servidor sGTM (cliente GA4) → **"Conversions API Tag" de facebookincubator** → `graph.facebook.com`. El Pixel sigue en GTM web disparando con el **mismo `event_id`** que el evento GA4 que alimenta al servidor. [OFFICIAL META] ([S04-054])
- **Tag oficial (2026):** usa Graph API **v25.0**, `partner_agent` `gtmss-1.0.0-0.0.10`, hashea con `trim().toLowerCase()`+SHA-256 si no viene ya hasheado, reconstruye `fbc` desde `fbclid` de `page_location`, y puede extender `_fbp`/`_fbc` 90 días como cookies HTTP (`extendCookies`). **No incluye lógica de consentimiento** y su normalización de teléfono solo quita la primera aparición de cada separador. [OFFICIAL META] (código, [S04-081]) + [STRONG INFERENCE]
- **Tag de Stape para sGTM (alternativa popular):** genera `_fbp` si no existe, opción de cookies HttpOnly, *Event Enhancement* (cookie HttpOnly `gtmeec` para enriquecer eventos posteriores con user data), mapeo automático de user data y **ajuste de consentimiento** ("abortar si no hay consentimiento de marketing": `ad_storage` de Consent Mode o parámetro del Data Tag). [EMPIRICAL] (código público, [S04-092])
- **Dominio first-party del contenedor (p. ej. `sst.tudominio.com`) importa:** con dominio propio, Meta indica que `_fbp`/`_fbc` se envían automáticamente; sin él, hay que pasarlos con `x-fb-ck-fbp`/`x-fb-ck-fbc`. Para que Safari no cape a 7 días las cookies puestas por el servidor, el subdominio no debe parecer "cloaking" de terceros (CNAME/IP de terceros). [OFFICIAL META] ([S04-054]) + [OFFICIAL WebKit] ([S04-073])
- **sGTM no elimina la necesidad de consentimiento:** los tags de Google en el servidor leen el estado de Consent Mode, los de terceros (Meta) no salvo que la plantilla lo implemente o tú condiciones el trigger. [STRONG INFERENCE] (inspección de plantillas) + [EMPIRICAL]
- **QA en dos depuradores a la vez:** preview de GTM web + preview de sGTM + Test Events de Meta (`test_event_code` en el tag). [OFFICIAL META] ([S04-054])

## 1. Por qué (y cuándo) sGTM

| Ventaja | Matiz |
|---|---|
| Un único flujo de datos (GA4 event) alimenta GA4, Meta, TikTok, etc. | Los datos de entrada siguen dependiendo del navegador (si el GA4 tag no dispara, el servidor no recibe nada) |
| Cookies first-party de servidor con más vida que las JS en Safari | Solo si el subdominio sGTM no se considera de terceros (WebKit) |
| Control y limpieza del payload (quitar PII, URL params sensibles) | Es responsabilidad tuya: sGTM no limpia nada por defecto |
| Menos JS de terceros en la página | El Pixel de Meta sigue siendo recomendable en paralelo (dedup) |

**Cuándo NO compensa:** tienda Shopify con app nativa en Maximum y sin necesidades especiales; WooCommerce con plugin oficial bien configurado. sGTM añade coste (hosting) y complejidad operativa. [STRONG INFERENCE]

**Limitación estructural:** sGTM alimentado desde el navegador **no captura** compras que no pasan por el navegador (pagos con redirección sin retorno, renovaciones, offline). Para esas, CAPI desde backend/webhook (o el Data Client de Stape/webhooks hacia sGTM). [STRONG INFERENCE]

## 2. Configuración paso a paso (patrón oficial de Meta)

### 2.1 GTM web
1. **GA4 Configuration/Google tag** con *Send to server container* (o campo `transport_url` = URL del servidor) y campo `first_party_collection = true` (necesario para pasar `user_data` a sGTM). [OFFICIAL META] ([S04-054])
2. Si el servidor **no** está en dominio propio: variables 1st-party cookie `_fbp` y `_fbc` y campos `x-fb-ck-fbp` / `x-fb-ck-fbc` en el Google tag. [OFFICIAL META] ([S04-054])
3. Variable de **event ID** compartida, por ejemplo (ejemplo de Meta):
```js
function() {
  var gtmData = window.google_tag_manager[{{Container ID}}].dataLayer.get('gtm');
  return gtmData.start + '.' + gtmData.uniqueEventId;
}
```
Para Purchase es preferible un ID derivado del pedido: `'purchase_' + {{DLV - transaction_id}}`. [OFFICIAL META] (patrón) + [STRONG INFERENCE] (ID de pedido)
4. **GA4 Event tags** (`purchase`, `add_to_cart`, `begin_checkout`, `view_item`, `generate_lead`…) con parámetro `event_id` = variable anterior y, si procede, `user_data` (email, phone, address) y parámetros Meta específicos (`x-fb-cd-content_ids`, `x-fb-cd-content_type`, `x-fb-cd-contents` en JSON.stringify, `x-fb-ud-external_id`…). [OFFICIAL META] ([S04-054])
5. **Meta Pixel** (Custom HTML o la plantilla web oficial de Meta en la galería, mantenida en GitHub en 2026 [S04-093]) disparando con **el mismo trigger** que el GA4 event y `fbq('track', 'Purchase', {...}, {eventID: {{FB Event ID}}})`. [OFFICIAL META] ([S04-054])

Mapeo automático GA4 → Meta del tag oficial: `add_payment_info`→AddPaymentInfo, `add_to_cart`→AddToCart, `add_to_wishlist`→AddToWishlist, `page_view`/`gtm.dom`→PageView, `purchase`→Purchase, `search`→Search, `begin_checkout`→InitiateCheckout, `generate_lead`→Lead, `view_item`→ViewContent, `sign_up`→CompleteRegistration. [OFFICIAL META] ([S04-054], [S04-081])

Mapeo de custom data: `value`→value, `currency`→currency, `search_term`→search_string, `transaction_id`→order_id, `items`→contents (id = `item_id` o `item_name`, `item_price` = `price`, `quantity`), `x-fb-cd-*` para el resto. [OFFICIAL META] ([S04-054], [S04-081])

### 2.2 Servidor (sGTM)
1. Contenedor server con dominio propio (`sst.tudominio.com`) — GCP (App Engine/Cloud Run), Stape u otro hosting.
2. **Cliente GA4** (viene por defecto; escucha `/g/collect`).
3. **Conversions API Tag** (galería, autor facebookincubator): Pixel ID, access token, `action_source = website`, trigger = eventos del cliente GA4 que quieras enviar.
4. (Recomendado) activar *extend cookies* para reescribir `_fbp`/`_fbc` como cookies HTTP de 90 días. [OFFICIAL META] ([S04-081])
5. **Trigger con consentimiento**: condiciona el tag a una variable de estado de consentimiento (p. ej. parámetro de consentimiento enviado desde web) — el tag oficial no lo hace solo.
6. Test: `test_event_code` en el tag (o en el evento), preview de sGTM, Test Events de Meta. Retirar al publicar. [OFFICIAL META] ([S04-054])

## 3. Tag oficial vs tag de Stape (comparativa por código)

| Característica | Conversions API Tag (facebookincubator) | Facebook CAPI tag (stape-io) |
|---|---|---|
| Versión API | v25.0 (constante en código) | Configurable/actualizada por Stape (no verificado valor exacto) |
| Hash de PII | Sí, `trim().toLowerCase()` + SHA-256 si no está hasheado | Sí (con auto-mapeo de muchas claves de eventData) |
| Normalización teléfono | `.replace()` de cadena (solo primera ocurrencia de `+ - espacio ( )`) | No auditado en detalle |
| `fbc` desde `fbclid` | Sí (desde `page_location`) | Sí (fbclid URL, cookie, eventData) |
| Generar `_fbp` si falta | No | Sí (opción) |
| Cookies HttpOnly | No (cookies `httpOnly:false`, 90 días) | Opción HttpOnly para `_fbc`/`_fbp` |
| Enriquecimiento de eventos posteriores | No | *Event Enhancement* (cookie `gtmeec`) |
| Consentimiento | **No** | Opción "send data only if marketing consent given" (ad_storage / Data Tag) |
| `partner_agent` | `gtmss-1.0.0-0.0.10` (+`-ee`) | `stape-gtmss-2.1.7` (+`-ee`) |

Fuentes: código de `template.tpl` de ambos repositorios (consultados 2026-10-16). [OFFICIAL META] ([S04-081]); [EMPIRICAL] ([S04-092]).

Ojo con **HttpOnly**: si marcas `_fbp`/`_fbc` como HttpOnly, el Pixel del navegador (`fbevents.js`) ya no puede leerlas; Stape lo ofrece como opción consciente. Si mantienes el Pixel web, valida que sigue enviando `fbp` coherente. [STRONG INFERENCE]

## 4. Consentimiento en sGTM

- **Google Consent Mode** viaja con las peticiones GA4 (parámetro `gcs`/`gcd`) y los tags de Google en el servidor lo interpretan; los tags de terceros necesitan que el estado se pase como parámetro de evento o que la plantilla lo lea. [EMPIRICAL] (guías de implementación 2025–2026)
- Patrón recomendado: en GTM web, enviar en cada GA4 event un parámetro `consent_marketing` (`granted`/`denied`) leído del CMP; en sGTM, el trigger del tag de Meta exige `consent_marketing equals granted`. Con Stape, usar su ajuste nativo de consentimiento. [STRONG INFERENCE]
- Con **Advanced Consent Mode**, Google envía pings sin cookies aunque el usuario rechace: esos eventos llegan a sGTM; **no los reenvíes a Meta** si tu base legal es el consentimiento. [STRONG INFERENCE]
- Consejo jurídico: fuera de alcance; ver archivo 09.

## 5. Signals Gateway / CAPI Gateway con GTM

- Desde Gateway v2.3.0 (sep-2025) hay onboarding del **Signals Gateway Pixel vía Google Tag Manager** y una guía específica. Es una alternativa a sGTM cuando el objetivo es solo Meta (+BigQuery). [OFFICIAL META] ([S04-062])
- No mezcles CAPI Gateway y sGTM-CAPI enviando los mismos eventos al mismo dataset sin verificar dedup: CAPIG genera su propio `event_id` a partir del Pixel; si sGTM usa otro ID, duplicarás. [OFFICIAL META] (CAPIG genera event_id, [S04-013]) + [STRONG INFERENCE]

## 6. QA específico de GTM

1. **GTM web preview:** el GA4 event y el Pixel disparan en el mismo evento de dataLayer y con el mismo valor de `{{FB Event ID}}`.
2. **sGTM preview:** request entrante `/g/collect` con `event_id`, `user_data`, `x-fb-*`; tag "Conversions API Tag – Succeeded"; en la pestaña de requests salientes, respuesta 200 de `graph.facebook.com`. Si "Failed", leer el *response body*. [OFFICIAL META] ([S04-054])
3. **Test Events:** evento "Deduplicated" con navegador+servidor. Si los IDs difieren: los dos tags no comparten trigger o la variable se evalúa dos veces con resultados distintos. [OFFICIAL META] ([S04-054])
4. **Cookies:** en el navegador, `_fbp`/`_fbc` con dominio raíz y caducidad ~90 días (si extendCookies); en Safari, comprobar a los 8 días en una sesión de prueba si persisten (test manual sugerido por practicantes). [EMPIRICAL]
5. **Teléfono:** enviar a sGTM ya normalizado (`34612345678`) o hasheado, para esquivar la normalización parcial del tag oficial.

## Implicaciones operativas

- **Hacemos:** dominio propio para sGTM con IP/infra que no dispare la defensa de cloaking de WebKit (contrastar con el proveedor); variable de event ID única reutilizada por Pixel y GA4; consentimiento explícito en el trigger; teléfono normalizado en el dataLayer; monitorizar coste del contenedor.
- **Evitamos:** activar sGTM-CAPI y además la CAPI nativa de la plataforma (Shopify/Woo) al mismo dataset; HttpOnly sin comprobar efectos en el Pixel; depender de sGTM para eventos que nunca pasan por el navegador.
- **Umbral:** ratio dedup Purchase > 90 %; 100 % de Purchase server con `fbp`, > 80 % con `fbc` cuando la sesión vino de Meta (referencia práctica [EMPIRICAL]).

## Errores frecuentes

1. `transport_url` configurado pero `first_party_collection` no → `user_data` no llega al servidor.
2. `x-fb-cd-contents` enviado como objeto (no string JSON) → el tag lo ignora (comprueba `[object Object]`, caso que el código oficial descarta).
3. Variable de event ID tipo "Random Number" evaluada por separado en dos tags → IDs distintos.
4. Pixel en GTM web + Pixel en el CMS → doble navegador.
5. Contenedor server en dominio por defecto (`*.appspot.com`, `*.stape.io`) → cookies de terceros, menor persistencia.

## Preguntas abiertas

- ¿Corregirá Meta la normalización de teléfono del tag oficial? (no hay evidencia de issue).
- Umbral exacto de "IP de terceros" en WebKit para cookies HTTP (las fuentes secundarias discrepan; la página de WebKit no lo detalla).

## Fuentes clave

- [Conversions API for Server-Side GTM](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/gtm-server-side) — vigente — meta-developers (S04-054)
- [ConversionsAPI-Tag-for-GoogleTagManager (template.tpl)](https://github.com/facebookincubator/ConversionsAPI-Tag-for-GoogleTagManager) — push 2026-06-03 — meta-developers (S04-081)
- [stape-io/facebook-tag (template.tpl)](https://github.com/stape-io/facebook-tag) — push 2026-09-03 — vendor (S04-092)
- [CAPI & Signals Gateway changelog](https://developers.facebook.com/documentation/ads-commerce/gateway-products/changelog) — 2025 — meta-developers (S04-062)
- [WebKit Tracking Prevention](https://webkit.org/tracking-prevention/) — vigente — WebKit (S04-073)
