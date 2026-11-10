# Implementación Pixel + Conversions API paso a paso (con validación)

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: instalación custom o semi-custom de Pixel + CAPI para web (e-commerce y lead gen), eventos y parámetros, deduplicación, consentimiento, validación y debugging. Plataformas concretas en 04–07.

## TL;DR

- **Orden correcto:** (1) mapa de eventos y parámetros → (2) Pixel con `eventID` → (3) CAPI con el mismo `event_id`, IP/UA del usuario, `fbp`/`fbc`, PII hasheada → (4) consentimiento → (5) Test Events con `test_event_code` → (6) producción y monitorización de EMQ/dedup/coverage/freshness. [OFFICIAL META] ([S04-009], [S04-056])
- **`event_id` determinista y compartido:** para Purchase usa algo derivado del `order_id` (p. ej. `purchase_<order_id>`); para eventos sin ID natural, genera un UUID en el navegador y pásalo al servidor en la misma petición (dataLayer, campo oculto, header). [OFFICIAL META] ([S04-005])
- **Purchase exige `value` y `currency`** (ISO 4217); para catálogo/Advantage+ catalog ads, `content_ids` (o `contents`) que coincidan exactamente con los IDs del catálogo y `content_type` `product` o `product_group`. [OFFICIAL META] ([S04-017], [S04-037])
- **PII: normaliza y luego SHA-256 en hex minúsculas**; nunca hashees `fbc`, `fbp`, IP, UA, `lead_id`, `anon_id`, `madid`. El Pixel hashea automáticamente lo que pasas en `fbq('init', id, {em: …})`. [OFFICIAL META] ([S04-006])
- **Valida con 4 herramientas, no con una:** Pixel Helper (navegador), Test Events (`test_event_code`, ve dedup), Payload Helper (estructura del JSON), Diagnostics/Overview de Events Manager (errores agregados, EMQ, freshness, dedup). Los eventos de prueba **sí** entran en el dataset: retira el `test_event_code` en producción. [OFFICIAL META] ([S04-009], [S04-054])
- **Atajo 2026 para pymes:** la "Meta-enabled Conversions API" (abril de 2026) crea en un clic una conexión server-side que replica el Pixel con dedup automática. Sirve como base mínima, pero **no sustituye** a un Purchase server-side desde el sistema de pago ni permite controlar parámetros; no la actives encima de otra CAPI sin verificar dedup. [EMPIRICAL] ([S04-112], [S04-113])
- **Consentimiento:** `fbq('consent','revoke')` antes de `init` en cada página y `grant` tras aceptación; en servidor, **no envíes** a CAPI eventos de usuarios sin consentimiento cuando tu base legal lo exija — ni el Pixel ni el tag oficial de sGTM lo gestionan por ti. [OFFICIAL META] ([S04-040], [S04-081])

## 1. Paso 0 — Diseño: mapa de eventos y parámetros

Antes de tocar código, define una tabla única que usarán web, servidor, GTM y QA.

| Evento Meta | Cuándo dispara | Fuente | `event_id` | `custom_data` mínimo | Optimizable |
|---|---|---|---|---|---|
| `PageView` | Cada carga de página | Pixel (+CAPI opcional) | uuid por pageview | — | No (señal de contexto) |
| `ViewContent` | Ficha de producto/servicio | Pixel + CAPI | uuid | `content_ids`, `content_type`, `value`, `currency` | Sí |
| `AddToCart` | Añadir al carrito (también AJAX) | Pixel + CAPI | uuid | `content_ids`/`contents`, `value`, `currency` | Sí |
| `InitiateCheckout` | Inicio de checkout | Pixel + CAPI | uuid / `checkout_<id>` | `contents`, `num_items`, `value`, `currency` | Sí |
| `AddPaymentInfo` | Datos de pago | Pixel + CAPI | uuid | `value`, `currency` | Sí |
| `Purchase` | Pedido confirmado (idealmente pago confirmado) | Pixel + **CAPI obligatorio** | `purchase_<order_id>` | `value`, `currency`, `contents`, `content_type`, `order_id` | Sí |
| `Lead` | Formulario enviado y validado | Pixel + CAPI | `lead_<lead_uuid>` | (`value` opcional) | Sí |
| `CompleteRegistration`, `Subscribe`, `StartTrial`, `Schedule`, `Contact`, `SubmitApplication` | Según negocio | Pixel + CAPI | determinista | `value`/`predicted_ltv` si aplica | Sí |

Reglas de diseño:
- **Usa eventos estándar** siempre que el significado encaje; los custom events sirven, pero los estándar tienen soporte nativo en optimización, catálogos y reporting. [OFFICIAL META] (lista estándar en [S04-063]) + [STRONG INFERENCE]
- **Purchase en servidor debe salir del sistema que confirma el pago** (webhook de la pasarela, `order.paid`), no de la thank-you page, para evitar compras fallidas o duplicadas. El Pixel en la thank-you page queda como respaldo con el mismo `event_id`. [STRONG INFERENCE]
- **Valor coherente:** decide (y documenta) si `value` incluye impuestos/envío, en qué moneda y si es bruto o neto. Shopify, por ejemplo, envía el total del pedido incluyendo impuestos y descuentos aplicados. [OFFICIAL Shopify] ([S04-031]) — si optimizas por valor, la definición debe ser estable en el tiempo.
- **Margen:** existe el parámetro `net_revenue` ("margin value of a conversion event") en `custom_data`; la optimización por margen ("Profit margin") se anunció en test el 4-jun-2025 ([S04-039]) y seguía en beta cerrada según Stape (ago-2026). [OFFICIAL META] (parámetro, [S04-037]) + [EMPIRICAL] (estado beta, [S04-038], [S04-039])

## 2. Paso 1 — Pixel con `eventID` (y consentimiento)

```html
<script>
  !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;
  n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,
  document,'script','https://connect.facebook.net/en_US/fbevents.js');

  // 1) Consentimiento (UE/EEE u otras jurisdicciones opt-in): bloquear por defecto
  fbq('consent', 'revoke');

  // 2) (Opcional, EE. UU.) Limited Data Use: explícitamente desactivado…
  fbq('dataProcessingOptions', []);
  // …o activado con geolocalización automática:
  // fbq('dataProcessingOptions', ['LDU'], 0, 0);

  // 3) Init con advanced matching manual (el Pixel hashea con SHA-256 en el navegador)
  fbq('init', 'PIXEL_ID', {
    em: 'john_smith@gmail.com',   // solo si el usuario está identificado
    external_id: 'cust_12345'     // mismo valor que enviarás por CAPI
  });

  // 4) PageView con eventID para poder deduplicar si también lo envías por CAPI
  fbq('track', 'PageView', {}, { eventID: window.__pvEventId });
</script>
```

```js
// Cuando el CMP confirma consentimiento de marketing:
fbq('consent', 'grant');

// Purchase en la página de confirmación (respaldo del evento servidor)
fbq('track', 'Purchase', {
  value: 129.90,
  currency: 'EUR',
  content_type: 'product',
  contents: [{ id: 'SKU-123', quantity: 2, item_price: 49.95 },
             { id: 'SKU-777', quantity: 1, item_price: 30.00 }],
  content_ids: ['SKU-123', 'SKU-777'],
  num_items: 3,
  order_id: 'ORD-100045'
}, { eventID: 'purchase_ORD-100045' });

// Varios píxeles en la página: evita fbq('track') que dispara en todos
fbq('trackSingle', 'PIXEL_ID', 'Lead', {}, { eventID: 'lead_7f3c…' });
```

Notas verificadas:
- `eventID` va en el **cuarto argumento**; si no hay parámetros, pasa `{}` como tercero. Con image pixel, el parámetro es `eid`. [OFFICIAL META] ([S04-005])
- `fbq('consent','revoke')` debe llamarse **en cada página**, antes de `init`; `grant` reanuda el envío. La documentación no detalla si los eventos durante `revoke` se encolan o descartan → asume que **no se envían** y no los "recuperes" por CAPI sin base legal. [OFFICIAL META] ([S04-040])
- `fbq('dataProcessingOptions', …)` va **antes** de `fbq('init')`. [OFFICIAL META] ([S04-067])
- Advanced matching manual debe ir en el `init` del código base, o no se trata como manual. [OFFICIAL META] (doc. Advanced Matching del Pixel)
- SPAs: el Pixel no detecta cambios de ruta de forma fiable en todos los frameworks; dispara `PageView`/`ViewContent` en cada cambio de ruta y evita dobles disparos al rehidratar. [STRONG INFERENCE]

## 3. Paso 2 — CAPI: payload de referencia

```http
POST https://graph.facebook.com/v25.0/{DATASET_ID}/events?access_token={SYSTEM_USER_TOKEN}
Content-Type: application/json
```

```json
{
  "data": [
    {
      "event_name": "Purchase",
      "event_time": 1760600000,
      "event_id": "purchase_ORD-100045",
      "action_source": "website",
      "event_source_url": "https://www.ejemplo.es/checkout/thank-you",
      "user_data": {
        "em": ["62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f"],
        "ph": ["11f976ff0fae9007051c1c0be7821b65f86e69e36f63542ae8c72dbf3b9cd9dc"],
        "fn": ["08e1996b5dd49e62a4b4c010d44e4345592a863bb9f8e3976219bac29417149c"],
        "ct": ["1579a6e3112caba1b6031ef7c507f3014d7b0a408fefd1b4d4a2c8c32d2274ff"],
        "zp": ["eec0f56d183812143f5033837f803b90e14052a6a24678c1046fa841d06fa74e"],
        "country": ["c0bc1e08f9743b2d50d5f1607503bf4e849af0e729fca896515bea955d70a33e"],
        "external_id": ["cust_12345"],
        "client_ip_address": "2a01:4f8:c17:1234::1",
        "client_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
        "fbc": "fb.1.1760599000123.IwZXh0bgNhZW0BMABhZGlkAasdFgh1234",
        "fbp": "fb.1.1759000000000.1234567890"
      },
      "custom_data": {
        "currency": "EUR",
        "value": 129.90,
        "content_type": "product",
        "contents": [
          {"id": "SKU-123", "quantity": 2, "item_price": 49.95},
          {"id": "SKU-777", "quantity": 1, "item_price": 30.00}
        ],
        "content_ids": ["SKU-123", "SKU-777"],
        "num_items": 3,
        "order_id": "ORD-100045"
      }
    }
  ],
  "test_event_code": "TEST12345"
}
```

Explicación de valores: los hashes corresponden a `john_smith@gmail.com`, `34612345678`, `valéry`, `madrid`, `28001`, `es` (normalizados y SHA-256). Los hashes de email y teléfono US coinciden con los ejemplos oficiales de Meta (`john_smith@gmail.com` → `62a14e44…`, `16505551212` → `e323ec62…`), útil para probar tu función de hash. [OFFICIAL META] ([S04-053]) — el `fbc`/`fbp`/IP de ejemplo son ficticios.

Reglas del payload:
- `event_time` en **segundos** (no milisegundos) y en GMT; ≤ 7 días de antigüedad. [OFFICIAL META] ([S04-008])
- `event_source_url` debe ser la URL real del navegador donde ocurrió el evento (Meta pide que coincida con el dominio verificado). [OFFICIAL META] ([S04-008])
- `client_ip_address` y `client_user_agent`: los del **usuario** (captúralos en el request del navegador y pásalos al job que envía a CAPI). Si usas Cloudflare/CDN, lee `CF-Connecting-IP`/`X-Forwarded-For` correctamente. [OFFICIAL META] ([S04-006]) + [STRONG INFERENCE]
- `test_event_code` a nivel raíz, **solo** en pruebas. [OFFICIAL META] ([S04-009])
- Combinaciones de `user_data` que Meta **rechaza** desde v13 si son lo único enviado: `ct+country+st+zp+ge+client_user_agent`, `db+client_user_agent`, `fn+ge`, `ln+ge` (o subconjuntos). [OFFICIAL META] ([S04-010])
- Agencias/plataformas: añade `partner_agent` con el nombre de tu plataforma. [OFFICIAL META] ([S04-010])

### 3.1 Normalización y hash (Node.js)

```js
import crypto from 'node:crypto';

const sha256 = (s) => crypto.createHash('sha256').update(s, 'utf8').digest('hex');
const isHashed = (s) => /^[a-f0-9]{64}$/i.test(s);

export function normEmail(v) { return v.trim().toLowerCase(); }

// Teléfono: solo dígitos, con prefijo país, sin ceros iniciales ni '+'
export function normPhone(v, defaultCountryCode = '34') {
  let d = String(v).replace(/\D/g, '');        // quita TODO lo que no sea dígito
  d = d.replace(/^00/, '');                      // 0034… → 34…
  if (d.length <= 9) d = defaultCountryCode + d.replace(/^0+/, ''); // nacional → E.164 sin '+'
  return d;
}
export function normName(v) {                    // fn / ln
  return v.trim().toLowerCase().replace(/[\s'’.,-]/g, ''); // sin puntuación; UTF-8 permitido
}
export function normCity(v) { return v.trim().toLowerCase().replace(/[^\p{L}\p{N}]/gu, ''); } // sin espacios
export function normZip(v)  { return v.trim().toLowerCase().replace(/[\s-]/g, ''); }
export function normCountry(iso2) { return iso2.trim().toLowerCase(); } // ISO 3166-1 alpha-2
export function normDob(yyyy, mm, dd) { return `${yyyy}${String(mm).padStart(2,'0')}${String(dd).padStart(2,'0')}`; }

export const h = (v, norm) => (v == null || v === '') ? undefined : (isHashed(v) ? v.toLowerCase() : sha256(norm(v)));

// Uso
const user_data = {
  em: [h('  John_Smith@Gmail.com ', normEmail)],
  ph: [h('+34 612 34 56 78', normPhone)],
  external_id: ['cust_12345'],          // hash recomendado pero no obligatorio; sé consistente entre canales
  client_ip_address: req.ip,            // NUNCA hash
  client_user_agent: req.get('user-agent'),
  fbc: cookies._fbc ?? buildFbc(req.query.fbclid), // NUNCA hash, NUNCA lowercase
  fbp: cookies._fbp
};

function buildFbc(fbclid) {
  if (!fbclid) return undefined;
  return `fb.1.${Date.now()}.${fbclid}`;  // subdomainIndex=1 si lo generas en servidor
}
```

Fuente de reglas: [OFFICIAL META] ([S04-006], [S04-007]). Las expresiones concretas son implementación propia [STRONG INFERENCE]: contrástalas con la Payload Helper. Detalle de normalización por campo en `03-emq-advanced-matching-pii-hashing.md`.

### 3.2 Envío robusto

- **Real time o casi** (cola con worker que envía en segundos). Meta: "ideally within an hour"; la métrica de freshness premia real time. [OFFICIAL META] ([S04-009], [S04-016])
- **Lotes pequeños** (p. ej. 50–200 eventos) con reintento exponencial ante 5xx/timeout; un evento inválido tumba el lote de hasta 1.000. Registra `fbtrace_id` y el cuerpo de error para depurar. [OFFICIAL META] (límites, [S04-009], [S04-057]) + [STRONG INFERENCE] (tamaño de lote)
- **Idempotencia:** si reintentas, reenvía el **mismo** `event_id`; Meta deduplica (48 h). [OFFICIAL META] ([S04-005])
- **Token:** System User token de Business Manager con permisos sobre el dataset; no uses tokens de usuario personal que caducan. [STRONG INFERENCE]
- **SDKs oficiales** (Business SDK: Python, Java, Ruby, PHP, Node) hashean automáticamente. [OFFICIAL META] ([S04-010])

## 4. Paso 3 — Deduplicación en la práctica

| Escenario | Cómo generar `event_id` | Riesgo |
|---|---|---|
| Purchase con pedido | `purchase_${order_id}` en web y servidor | Ninguno si ambos leen el mismo `order_id` |
| Lead con formulario | UUID generado en el navegador, enviado al backend en el POST del formulario; Pixel dispara con ese UUID | Doble envío del formulario → dos UUID; bloquea doble submit |
| AddToCart AJAX | UUID por acción; el endpoint de carrito devuelve/recibe ese UUID | Fragments AJAX re-ejecutados disparan dos veces (bug real corregido en Meta for WooCommerce, #3939) [OFFICIAL META] ([S04-035]) |
| PageView/ViewContent | UUID por carga, inyectado en el HTML y usado por el servidor | Caché de página completa que sirve el mismo UUID a todos → colisiones; genera el ID en el cliente |

- Con **GTM web**, Meta documenta como ejemplo un ID `gtm.start + '.' + gtm.uniqueEventId` expuesto como variable y pasado al Pixel (`eventID`) y al GA4 event (`event_id`) que alimenta sGTM. [OFFICIAL META] ([S04-054])
- Comprueba en **Test Events** que el evento aparece como "Deduplicated" y en **Events Manager > Event details > Event Deduplication** que el *overlap* de `event_id` es alto. Overlap bajo = claves que no coinciden o que solo una fuente envía. [OFFICIAL META] ([S04-056])

## 5. Paso 4 — Consentimiento y LDU

- **UE/EEE (y otras jurisdicciones opt-in):** sin consentimiento de marketing, ni Pixel (`revoke`) ni CAPI (filtro en servidor). El tag oficial de CAPI para sGTM **no contiene lógica de consentimiento** (inspección del código `template.tpl`, 2026): debes condicionarlo con triggers o variables de estado de consentimiento. [OFFICIAL META] ([S04-040], [S04-081])
- **EE. UU.:** Limited Data Use (`data_processing_options: ["LDU"]`, país `1`, estado `1000…1013` o `0/0` para geolocalizar) en 14 estados a 2026. [OFFICIAL META] ([S04-067])
- **Shopify:** la Customer Privacy API y los web pixels aplican el consentimiento a los pixels gestionados por Shopify (incluida la app de Meta). [OFFICIAL Shopify] ([S04-032], [S04-033])
- No es consejo jurídico: la base legal (consentimiento vs interés legítimo para el servidor, DPA, etc.) la decide el responsable del tratamiento con su asesoría. Ver `09-privacidad-att-gdpr-consentimiento-aem.md`.

## 6. Paso 5 — Validación (checklist de puesta en marcha)

1. **Pixel Helper** (extensión de Chrome): un único Pixel ID esperado; `PageView` sin errores; en compra, `Purchase` con `value`, `currency`, `content_ids` y `eventID`; advanced matching visible ("Advanced Matching Parameters Sent"; `external_id` solo se ve aquí, no en Test Events). [OFFICIAL META] ([S04-055])
2. **Test Events** (Events Manager > dataset > Test Events): abre la web desde la URL de prueba, haz una compra real o de prueba y envía el server event con `test_event_code`. Debe aparecer **una** fila "Deduplicated" con navegador y servidor. Usa datos de cliente reales tuyos: eventos de prueba no emparejados pueden descartarse. [OFFICIAL META] ([S04-009], [S04-010])
3. **Payload Helper**: pega tu JSON para validar estructura y parámetros recomendados. [OFFICIAL META] ([S04-010])
4. **Respuesta de la API**: `events_received` = número enviado; sin `messages` de error. [OFFICIAL META] (formato observado) — guarda `fbtrace_id`.
5. **Events Manager > Overview** (tras ~20 min): eventos por "Connection method" (Browser / Server), EMQ por evento, freshness, dedup. [OFFICIAL META] ([S04-056])
6. **Diagnostics**: avisos de parámetros inválidos, `fbc` modificado, IP de servidor, eventos duplicados sin dedup, dominio no coincidente, etc. Resuelve los de severidad alta antes de lanzar.
7. **Catálogo** (si aplica): Commerce Manager > Catalog > Events: *match rate* de `content_ids` > 90 %. [OFFICIAL META] ([S04-017])
8. **Reconciliación 7 días**: compras CAPI vs pedidos backend (debe ser ~100 % de pedidos con consentimiento); compras Pixel vs CAPI (el ratio te da la pérdida del navegador).

## 7. Debugging: árbol rápido

| Síntoma | Causa probable | Comprobación |
|---|---|---|
| Server events no aparecen | Token sin permisos, dataset equivocado, `event_time` > 7 días o en ms, un evento inválido en el lote | Respuesta 4xx; reenviar un solo evento con `test_event_code` |
| Aparecen pero no deduplican | `event_id` distinto o ausente en una fuente; `event_name` distinto (`purchase` vs `Purchase`); Pixel ID distinto | Test Events; pestaña Event Deduplication |
| EMQ bajo en server | Falta `fbc`/`fbp`, IP/UA del servidor, PII no normalizada | Dataset Quality API `match_key_feedback` y `diagnostics` |
| Compras duplicadas en Ads Manager | Dos implementaciones (app + GTM + theme), Purchase en recarga de thank-you page, dedup roto | Pixel Helper (¿2 Purchase?), Events Manager por connection method |
| Purchase sin valor | `value` como string con coma (`"129,90"`), variable vacía | Pixel Helper / Test Events |
| Atribución de clic baja vs. GA4 | Pérdida de `fbclid` en redirecciones o checkout en otro dominio | Probar URL con `?fbclid=test` y seguir la cadena de redirecciones |

## Implicaciones operativas

- **Hacemos:** documento de especificación de eventos versionado; `event_id` determinista; Purchase server-side desde el sistema de pago; normalización+hash centralizados (una librería); test end-to-end en cada release; alertas sobre volumen diario de Purchase CAPI vs pedidos.
- **Evitamos:** "instalar CAPI" con un plugin encima de otra implementación existente; enviar todo el dataLayer a Meta (PII o datos sensibles en parámetros custom); confiar solo en la Pixel Helper.
- **Umbrales:** ≥ 95 % de pedidos con consentimiento llegando por CAPI; dedup overlap Purchase > 90 %; EMQ Purchase ≥ 8 (objetivo práctico), ≥ 6 (mínimo Meta).

## Errores frecuentes

1. `event_time` en milisegundos → evento rechazado o fechado en el futuro.
2. `currency` ausente o no ISO (`€`, `eur ` con espacio).
3. Hashear dos veces (hash de un hash) al combinar Pixel advanced matching y una librería que ya hashea.
4. Lowercase de `fbc` en la normalización genérica de "todos los campos".
5. Dejar `test_event_code` en producción (los eventos siguen contando, pero ensucian Test Events y confunden el QA). [OFFICIAL META] ([S04-009])
6. Disparar Purchase en la thank-you page sin control de recarga (cada F5 = nueva compra si el `eventID` cambia).

## Preguntas abiertas

- Comportamiento exacto de eventos disparados durante `consent revoke` (¿descartados o en cola?): no documentado.
- Peso real de `net_revenue` en la optimización por margen fuera de la beta: no verificado.

## Fuentes clave

- [Handling Duplicate Pixel and CAPI Events](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events) — vigente — meta-developers (S04-005)
- [Using the Conversions API](https://developers.facebook.com/docs/marketing-api/conversions-api/using-the-api) — vigente — meta-developers (S04-009)
- [Best Practices](https://developers.facebook.com/docs/marketing-api/conversions-api/best-practices) — vigente — meta-developers (S04-010)
- [Verifying Your Setup](https://developers.facebook.com/documentation/ads-commerce/conversions-api/verifying-setup) — vigente — meta-developers (S04-056)
- [Custom Data Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/custom-data) — vigente — meta-developers (S04-037)
- [Meta Pixel GDPR](https://developers.facebook.com/docs/meta-pixel/implementation/gdpr) — vigente — meta-developers (S04-040)
- [Data Processing Options (LDU)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/overview/data-processing-options) — vigente — meta-developers (S04-067)
- [Omni Optimal Setup Guide](https://developers.facebook.com/documentation/ads-commerce/marketing-api/best-practices/omni-optimal-setup-guide) — vigente — meta-developers (S04-017)
