# Arquitectura de señales: Pixel, Conversions API, datasets e identificadores

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A04 (agente) · Ámbito: cómo llegan las señales de conversión a Meta, qué identificadores existen, cómo se emparejan, cómo se miden calidad y cobertura. Base conceptual para los archivos 02–08 y 16.

## TL;DR

- **Un "dataset" es el contenedor único de eventos** (antes "pixel", "offline event set" y "app" por separado). El mismo ID recibe eventos de navegador (Pixel), servidor (CAPI), app y tienda física; el endpoint de CAPI sigue siendo `POST /{PIXEL_ID o DATASET_ID}/events`. [OFFICIAL META] ([S04-009], [S04-061], [S04-044])
- **La configuración recomendada sigue siendo redundante: Pixel + CAPI enviando los mismos eventos, deduplicados con `event_id` + `event_name` idénticos** en ventana de 48 h. El Pixel aporta cookies y contexto de navegador en tiempo real; CAPI aporta resiliencia (ad blockers, ITP, errores de carga) y datos que el navegador no ve (pagos confirmados, CRM, offline). [OFFICIAL META] ([S04-005], [S04-010])
- **Lo que determina si un evento sirve para optimizar y atribuir no es "que llegue", sino que se pueda emparejar con una cuenta de Meta.** Los eventos no emparejados solo sirven para medición básica; "solo los eventos emparejados se usan para atribución y optimización". [OFFICIAL META] ([S04-010])
- **Los identificadores con más peso son email, teléfono, IP, user agent, `fbp`, `fbc`, nombre y apellido.** `external_id` es el pegamento entre canales: Meta recuerda la asociación `external_id` → usuario y la reutiliza en eventos posteriores (con caducidad). [OFFICIAL META] ([S04-017], [S04-055])
- **`fbc` (click ID) es el identificador más valioso para atribución de clic y el más frágil.** Se pierde por redirecciones que quitan `fbclid`, por cookies JS capadas a 24 h en Safari tras navegación con link decoration desde un dominio rastreador, y por modificar su valor (es case-sensitive). Capturarlo en servidor en la landing y persistirlo es la mejora de mayor retorno. [OFFICIAL META] + [STRONG INFERENCE] ([S04-007], [S04-073], [S04-074])
- **Calidad de señal = cobertura + frescura + matching + deduplicación.** Meta lo expone en Events Manager y en la Dataset Quality API: EMQ (0–10), *event coverage* (objetivo de referencia 75 % de eventos del Pixel cubiertos por CAPI con claves de dedup compartidas), *data freshness* (real time / hourly…), *dedupe key feedback* y ACR (conversiones adicionales reportadas). [OFFICIAL META] ([S04-016])
- **"Gateway products" (2025–2026):** Conversions API Gateway (espejo servidor del Pixel, solo Meta) y Signals Gateway (GA desde v2.0.0, 15-ene-2025: pipelines multi-fuente/multi-destino, píxel propio `cbq()`, BigQuery, destinos HTTPS). Ambos se autoalojan en la nube del anunciante o vía partner. [OFFICIAL META] ([S04-062], [S04-063])
- **Abril de 2026: "Meta-enabled Conversions API" (CAPI en un clic) y "AI enrichment" del Pixel.** Desde Events Manager (Connect Data > Web > See other ways to set up > Set up with Meta) Meta crea una conexión servidor que replica los eventos y parámetros del Pixel con dedup automática, sin servidor propio ni configuración (solo web). El enriquecimiento con IA añade al Pixel título, descripción, tipo de página, atributos de producto y datos del negocio; se activa por defecto tras un aviso de 30 días y no aplica a fuentes con restricciones de categorías especiales. [EMPIRICAL — prensa especializada que cita a Meta] ([S04-112], [S04-113], [S04-115])
- **CAPI no es un "bypass" de privacidad ni de políticas:** respeta consentimiento solo si tú lo programas, y las restricciones de categorías sensibles (core setup, bloqueo de eventos) se aplican igual a Pixel y a CAPI. [OFFICIAL META] (consentimiento: [S04-040]) + [EMPIRICAL] (restricciones: [S04-082])

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Nueva vía de señal: medición en el dispositivo** (activada por defecto en el píxel desde el 12-nov-2026; no en la UE ni el Reino Unido). Complementa píxel y CAPI, no los sustituye. Meta no documenta cómo se deduplica con los eventos de píxel y CAPI. **[OFFICIAL META]** + **[HYPOTHESIS]** (deduplicación). Detalle en [10-atribucion-ventanas-y-modelos.md](10-atribucion-ventanas-y-modelos.md).
> - Fuentes: S10-105, S10-110 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. Modelo mental: de la acción del usuario a la señal que aprende el algoritmo

```
Usuario ve/clica anuncio ──► llega a la web con ?fbclid=… (y UTMs)
        │                                  │
        │                    Pixel (fbevents.js) escribe _fbp / _fbc (1st-party, JS)
        │                    Servidor puede escribir _fbc vía Set-Cookie o guardar fbclid
        ▼                                  ▼
  Meta registra impresión/clic    Eventos: PageView → ViewContent → AddToCart → Purchase
                                            │                         │
                                  Navegador (Pixel)           Servidor (CAPI)  ← misma event_id
                                            └──────────► Dataset ◄──┘
                                                          │
                          Matching (em, ph, fbc, fbp, IP, UA, external_id…) → cuenta Meta
                                                          │
                       Dedup (event_name+event_id, 48 h) → Atribución (ventanas) → Reporting
                                                          └──────────► Optimización (delivery)
```

Tres decisiones distintas ocurren después de recibir el evento y conviene no mezclarlas:

1. **Matching**: ¿a qué persona (Accounts Center account) corresponde este evento? Depende de los parámetros de cliente (`user_data`).
2. **Atribución**: ¿a qué anuncio se le da crédito? Depende de que esa persona tenga una interacción elegible (link click, engage-through, view) dentro de la ventana configurada (ver `10-atribucion-ventanas-y-modelos.md`).
3. **Optimización**: el sistema de entrega aprende de las conversiones atribuidas/emparejadas que recibe a tiempo (ver `12-attribution-lag.md`).

Un evento puede llegar (se ve en Events Manager), no emparejarse (no atribuye ni optimiza), o emparejarse pero no atribuirse a ningún anuncio (no había interacción en ventana). Por eso "Events Manager ve 100 compras" y "Ads Manager reporta 40" no es en sí un bug.

## 2. Componentes

### 2.1 Dataset (Events Manager)

- **Qué es:** el ID único que agrupa todas las fuentes de eventos de un negocio. Meta habla de "dataset" desde 2023; históricamente el Pixel ID, el *offline event set* y la app eran fuentes separadas. Hoy el ID del Pixel *es* el dataset ID para web, y offline/app se conectan a ese dataset. [OFFICIAL META] ([S04-061], [S04-044])
- **Comprobación técnica:** `GET /{ads-pixel-id}?fields=is_consolidated_container` indica si el dataset está consolidado y es elegible para recibir eventos de app/offline. [OFFICIAL META] ([S04-044])
- **Restricción importante para apps:** solo **una app** puede vincularse a un dataset. [OFFICIAL META] ([S04-044])
- **Implicación de arquitectura:** un dataset por negocio/dominio principal es lo normal. Varios datasets para el mismo sitio fragmentan señal (audiencias, aprendizaje y dedup solo funcionan dentro del mismo Pixel ID: la deduplicación exige "mismo Pixel ID"). [OFFICIAL META] ([S04-005])

### 2.2 Meta Pixel (navegador)

- JavaScript (`fbevents.js`) que escribe cookies de primera parte (`_fbp`, `_fbc`), envía `PageView` por defecto y los eventos que programes con `fbq('track'|'trackCustom'|'trackSingle', …)`. Añade automáticamente IP y user agent del navegador. [OFFICIAL META] ([S04-006])
- **Advanced matching:** manual (objeto de datos del usuario como tercer argumento de `fbq('init', PIXEL_ID, {...})`; el Pixel hashea en el navegador) o automático (activado en Events Manager: el Pixel detecta campos de formulario). Detalle en `03-emq-advanced-matching-pii-hashing.md`.
- **Debilidades estructurales:** ad blockers, fallos de carga, ITP de Safari (cookies JS capadas a 7 días, o 24 h en landings con link decoration desde dominios rastreadores), consentimiento denegado, pestañas cerradas antes de disparar, pasarelas de pago externas (el usuario no vuelve a la thank-you page). [OFFICIAL META]/[OFFICIAL WebKit] ([S04-073], [S04-074]) + [EMPIRICAL]

### 2.3 Conversions API (servidor)

- `POST https://graph.facebook.com/{API_VERSION}/{DATASET_ID}/events` con un array `data` (máx. **1.000 eventos por petición**; si uno es inválido se rechaza el lote entero). La versión de ejemplo en la documentación actual es **v25.0**. [OFFICIAL META] ([S04-009])
- `event_time` en segundos UNIX; **hasta 7 días en el pasado** (si un solo evento del lote excede, falla toda la petición). Para `physical_store` Meta indica además "subir transacciones dentro de 62 días": la documentación no aclara si el límite de 7 días deja de aplicarse para ese `action_source` → **no verificado**; diseña para 7 días. [OFFICIAL META] ([S04-008], [S04-009], [S04-061])
- `action_source` obligatorio: `website`, `app`, `physical_store`, `system_generated`, `business_messaging`, `email`, `phone_call`, `chat`, `other`. Declaras que es correcto. [OFFICIAL META] ([S04-008])
- Para web son obligatorios `event_source_url` y `client_user_agent`; Meta recomienda `external_id` y `event_id` en todos los eventos. [OFFICIAL META] ([S04-010])
- Respuesta: 2xx si válido, 4xx con detalle mínimo si no. Reintentar errores no-cliente; timeout recomendado 1.500 ms; respuesta típica < 600 ms. [OFFICIAL META] ([S04-057])
- `opt_out: true` → el evento solo se usa para atribución, no para optimización de entrega. [OFFICIAL META] ([S04-008])

### 2.4 App events (SDK / CAPI para apps / MMP)

Eventos de app vía SDK de Meta, App Events API (legado), MMP o CAPI con `action_source=app` (exige `app_data.extinfo` y `advertiser_tracking_enabled`). Detalle en `15-apps-sdk-skan-mmp.md`. [OFFICIAL META] ([S04-044])

### 2.5 Offline y CRM

- Offline (tienda, call center): CAPI con `action_source=physical_store`. La Offline Conversions API está retirada desde mayo de 2025 (descontinuada con la expiración de Graph API v16.0). [OFFICIAL META] ([S04-061], ver `08-eventos-offline-y-crm.md`)
- CRM para lead ads (Conversion Leads): CAPI con `action_source=system_generated` y `custom_data.event_source=crm`. [OFFICIAL META] ([S04-058])

### 2.6 Gateway products (Conversions API Gateway y Signals Gateway)

| | Conversions API Gateway (CAPIG) | Signals Gateway |
|---|---|---|
| Qué hace | Recibe los eventos del Pixel (configurado con el endpoint del Gateway) y los reenvía server-to-server a CAPI con `event_id` generado automáticamente para dedup | Plataforma de pipelines: fuentes (Signals Gateway Pixel `cbq()`, SDK, ficheros, Meta Pixel) → destinos (Meta CAPI, BigQuery, HTTPS custom) |
| Hosting | Cuenta cloud propia (AWS EKS, AWS ECS Express, GCP; App Runner en migración) o partner (p. ej. Stape) | Igual; requiere DNS/endpoint propio; GCP con setup guiado desde 2025 |
| Fecha clave | Producto desde 2022; multi-cuenta para agencias | GA en **v2.0.0 (15-ene-2025)**; v2.3.0 (11-sep-2025): onboarding vía GTM, custom conversions y Website Custom Audiences |
| Coste | Solo cloud o fee del partner (Stape: desde ~10 $/pixel/mes) | Solo cloud o partner (Stape: ~17 $/millón de eventos) |
| Para quién | Quien quiere CAPI sin desarrollo y ya tiene Pixel | Quien quiere un hub de datos de primera parte (incluso sin cookies/código de Meta en el navegador) |

Fuentes: [OFFICIAL META] ([S04-012], [S04-013], [S04-062], [S04-063]); precios [EMPIRICAL — vendor] ([S04-014]).

- **Signals Gateway Pixel** se describe como código "desplegado y gestionado por la empresa", que "no depende de cookies de terceros ni de código de los servidores de Meta", y Meta recomienda **convivir con el Meta Pixel**, no sustituirlo. [OFFICIAL META] ([S04-063])
- Afirmaciones de "+25–33 % de conversiones" con Signals Gateway proceden de contenido patrocinado y no están verificadas. [HYPOTHESIS] ([S04-015])

### 2.7 Meta-enabled Conversions API (CAPI "en un clic", abril de 2026)

| Aspecto | Detalle | Evidencia |
|---|---|---|
| Qué es | Conexión server-side creada y alojada por Meta que entrega los datos web "junto a tu Meta Pixel" | [EMPIRICAL] (cita del Help Center vía PPC Land, [S04-112]) |
| Qué envía | Lo mismo que el Pixel (eventos y parámetros), deduplicado automáticamente | [EMPIRICAL] ([S04-112]) |
| Qué no hace | No permite elegir eventos/parámetros; no cubre app, offline ni mensajería; no aporta datos que el navegador no ve (pago confirmado en backend, CRM) | [EMPIRICAL] ([S04-112]) |
| Para quién | Pymes sin CAPI o con baja cobertura; quien ya tiene CAPI propia o de partner no necesita cambiar | [EMPIRICAL] ([S04-112], [S04-113]) |
| Riesgos | Duplicados si se activa además de un plugin que ya envía CAPI con otros `event_id` (reportado por practicantes); sin filtrado de parámetros (minimización de datos UE) | [EMPIRICAL] / [STRONG INFERENCE] |
| Afirmación de Meta | −17,8 % de coste por resultado de media en anunciantes con CAPI web frente a sin CAPI (no es un resultado del producto en un clic; metodología no publicada) | [EMPIRICAL] ([S04-112]) |

Lectura: es una mejora de **resiliencia** (llegan eventos que el navegador de Meta pierde por red/bloqueo parcial), no de **cobertura de negocio**: si el Pixel no se ejecuta (ad blocker que bloquea el script, consentimiento denegado), tampoco hay nada que replicar. Para Purchase fiable sigue haciendo falta CAPI desde el backend. [STRONG INFERENCE] — la documentación técnica detallada no estaba publicada en abril de 2026 según PPC Land.


## 3. Identificadores: qué son, quién los genera, cómo se rompen

| Parámetro | Origen | ¿Hash? | Rol | Cómo se rompe |
|---|---|---|---|---|
| `fbc` | `_fbc` (Pixel) o construido desde `fbclid` de la URL: `fb.{subdomainIndex}.{creationTimeMs}.{fbclid}` | **No** | Vincula la conversión al clic del anuncio | Redirecciones que eliminan `fbclid`; modificar mayúsculas/minúsculas; cookie JS caducada (Safari 24 h / 7 días); dominios distintos (landing ≠ checkout) |
| `fbp` | `_fbp` (Pixel): `fb.{subdomainIndex}.{creationTimeMs}.{random}` | **No** | ID de navegador; clave de dedup alternativa; actúa como `external_id` si no hay otro | Borrado de cookies, ITP, cambio de dispositivo/navegador, consentimiento denegado |
| `external_id` | Tu ID de usuario/cliente | Recomendado | Unir canales; Meta reutiliza la asociación cuando ya la emparejó | Inconsistencia entre Pixel/CAPI/app; IDs efímeros |
| `em`, `ph` | Formularios, checkout, CRM | **Sí (SHA-256 tras normalizar)** | Matching determinista de alto peso | Normalización errónea (espacios, mayúsculas, prefijo país en teléfono) |
| `fn`, `ln`, `ct`, `st`, `zp`, `country`, `db`, `ge` | Checkout/CRM | **Sí** | Matching complementario | Combinaciones débiles rechazadas desde v13 (p. ej. solo `fn`+`ge`) |
| `client_ip_address` | Request del navegador | **No** | Matching probabilístico, geolocalización, LDU | Usar la IP del servidor/proxy en lugar de la del usuario; IPv4 cuando el Pixel envía IPv6 |
| `client_user_agent` | Request del navegador | **No** | Obligatorio en web | Enviar el UA del servidor |
| `lead_id` | Lead Ads (15–17 dígitos) | **No** | Matching determinista de leads | Perderlo al pasar al CRM |
| `ctwa_clid` | Click-to-WhatsApp | **No** | Atribución de conversaciones | — |
| `anon_id`, `madid` | App (install ID, IDFA/GAID) | **No** | Matching de app | ATT denegado (IDFA vacío) |

Fuentes: [OFFICIAL META] ([S04-006], [S04-007], [S04-010], [S04-055], [S04-058], [S04-044]).

### 3.1 `fbclid` → `fbc`: reglas operativas

- El `fbclid` llega en la query de la URL de destino. Meta indica: "ClickID value is case sensitive – do not apply any modifications". [OFFICIAL META] ([S04-007])
- Si no hay cookie `_fbc` pero la URL actual trae `fbclid`, **puedes construir `fbc` en servidor** (`subdomainIndex` = 1 si lo generas tú; `creationTime` = momento en que recibiste el `fbclid`). Si guardas la cookie tú, hazlo como cookie HTTP con caducidad 90 días y solo si no existe o si el `fbclid` cambió. [OFFICIAL META] ([S04-007])
- **Safari/WebKit:** cookies creadas por JavaScript se borran tras 7 días sin interacción, y en la landing a la que se llega con link decoration desde un dominio clasificado como rastreador quedan capadas a **24 h**; las cookies HTTP servidas desde un subdominio con CNAME/IP de terceros quedan capadas a 7 días. Esto afecta directamente a `_fbc`/`_fbp` creadas por `fbevents.js`. [OFFICIAL WebKit] ([S04-073], [S04-074])
- Implicación: para ciclos de compra > 1 día en Safari, **persistir `fbclid`/`fbc` en servidor** (sesión, base de datos de usuario/carrito, campo oculto del lead) es más fiable que depender de la cookie. [STRONG INFERENCE]
- iOS 26: Advanced Fingerprinting Protection activo por defecto en todo Safari; la eliminación de parámetros de seguimiento en URL está documentada para enlaces en Mail, Mensajes y navegación privada (y en pestañas normales solo si el usuario lo activa para "All Browsing"). [EMPIRICAL] ([S04-075]) — vigilar caídas de cobertura de `fbc` en tráfico iOS.

### 3.2 Parameter Builder Library (Meta)

SDK open source de Meta para generar/normalizar `fbc`, `fbp`, IP (IPv6 preferente) y hashear PII; versión cliente (JS) y servidor (PHP, Java, Python, Node.js, Ruby). Añade un sufijo ("appendix") de 8 caracteres que identifica versión/lenguaje del SDK; **no lo elimines**, y no vuelvas a poner en minúsculas lo que devuelve (es case-sensitive). Recomendación: capturar `_fbp`/`_fbc` lo antes posible en la landing, normalizar y hashear **una sola vez** (cliente o servidor). [OFFICIAL META] ([S04-011]) — El plugin oficial Meta for WooCommerce ya lo usa (dependencia `capi-param-builder`). [OFFICIAL META] ([S04-035])

## 4. Browser vs server: qué aporta cada uno

| Dimensión | Pixel (browser) | CAPI (server) |
|---|---|---|
| Latencia | Tiempo real | Tan rápida como la programes (Meta: "ideally within an hour"; óptimo real time) |
| Cookies `_fbp/_fbc` | Las crea y lee | Debes leerlas del request o construirlas |
| IP/UA | Automáticos | Debes pasarlos (los del usuario, no los del servidor) |
| Bloqueo | Ad blockers, ITP, fallos JS, consentimiento | No bloqueable por el navegador (pero sí por tu lógica de consentimiento y por restricciones de Meta) |
| Eventos no-web | No | Sí: pagos confirmados, suscripciones renovadas, reembolsos (como evento custom), CRM, offline |
| Riesgo típico | Infra-conteo | Doble conteo si la dedup falla; datos tardíos; IP/UA del servidor |

[OFFICIAL META] ([S04-009], [S04-010]) + [STRONG INFERENCE].

**Server-only (sin Pixel)** es posible pero pierde la creación nativa de `_fbp`/`_fbc` y el contexto de navegador; solo tiene sentido si construyes `fbc` desde `fbclid` y generas un ID de navegador propio. Meta recomienda la configuración redundante. [OFFICIAL META] ([S04-010])

## 5. Deduplicación (resumen; detalle en 02)

- **Método 1 (recomendado):** `eventID` del Pixel (cuarto argumento de `fbq`) == `event_id` de CAPI **y** `event` == `event_name`, mismo Pixel ID, recibidos dentro de 48 h. Funciona en cualquier orden de llegada. [OFFICIAL META] ([S04-005])
- **Método 2:** `event_name` + `fbp` y/o `external_id` coherentes. Solo funciona si el evento de navegador llega primero; si el de servidor llega antes y no había evento de navegador en las 48 h previas, no se descarta. [OFFICIAL META] ([S04-005])
- **No deduplica dentro de la misma fuente**: dos Purchase de navegador con el mismo `eventID` NO se fusionan por el método 2; dos Purchase de servidor duplicados tampoco. Para compras, usa el `order_id` como base del `event_id` y evita dobles disparos. [OFFICIAL META] ([S04-005])
- Si los eventos de navegador y servidor llegan con < 5 minutos de diferencia, se favorece el de navegador. [OFFICIAL META] ([S04-008])
- **Sin dedup** (o con `event_id` distintos): Meta cuenta el doble → CPA aparentemente mitad, ROAS inflado, y el algoritmo optimiza hacia patrones de doble disparo. Síntoma: Events Manager con ratio de dedup bajo y Ads Manager > backend. [OFFICIAL META] (concepto) + [EMPIRICAL] (síntomas, [S04-084])

## 6. Calidad de señal: las cuatro métricas que importan

| Métrica | Definición | Dónde | Umbral orientativo |
|---|---|---|---|
| **Event Match Quality (EMQ)** | Puntuación 0–10 de lo bien que los parámetros de cliente pueden emparejar el evento (por evento, web) | Events Manager > Overview; Dataset Quality API `event_match_quality.composite_score` | Meta: "aim for 6.0 or higher" [OFFICIAL META] ([S04-056]); en la práctica Purchase ≥ 8 es alcanzable con email+teléfono+fbc+fbp+IP+UA [EMPIRICAL] |
| **Event coverage** | Media 7 días del % de eventos del Pixel también cubiertos por CAPI con claves de dedup compartidas | Dataset Quality API `event_coverage` | `goal_percentage` 75 en el ejemplo oficial [OFFICIAL META] ([S04-016]) |
| **Data freshness** | Retraso entre `event_time` y recepción | Events Manager > Event details > Event Freshness; API `data_freshness.upload_frequency` | Real time [OFFICIAL META] ([S04-016], [S04-056]) |
| **Dedup key feedback** | % de eventos de navegador y servidor con cada clave (`event_id`, `external_id`, `fbp`) y overlap | Events Manager > Event Deduplication; API `dedupe_key_feedback` | "Higher is better"; overlap bajo = claves no compartidas [OFFICIAL META] ([S04-056]) |
| **ACR** | Additional Conversions Reported estimadas por usar CAPI junto al Pixel (7 días) | API `acr`, `event_potential_aly_acr_increase` | Informativo |

- La Dataset Quality API se amplió el **28-may-2025** con ACR, event coverage, deduplicación, freshness y diagnósticos de EMQ. [OFFICIAL META] ([S04-016])
- **EMQ es solo para eventos web**; offline, app, CRM y betas requieren al representante de Meta (para offline existe un "Offline Data Quality" 0–10 donde ≥ 8,5 se describe como nivel para omnicanal). [OFFICIAL META] ([S04-016], [S04-017])
- Diagnóstico frecuente en la API: "pasar de IPv4 a IPv6" y enviar en CAPI una `client_ip_address` coherente con la del Pixel. [OFFICIAL META] ([S04-016])

## 7. First-party data, UTMs y parámetros dinámicos

- **UTMs ≠ señal de Meta.** Las UTMs sirven a GA4/Shopify/CRM; Meta atribuye con sus propios identificadores (`fbc`, matching de usuario). Aun así son imprescindibles para la reconciliación (archivo 11). [STRONG INFERENCE]
- Parámetros dinámicos en "URL parameters" del anuncio: `{{campaign.id}}`, `{{adset.id}}`, `{{ad.id}}`, `{{campaign.name}}`, `{{adset.name}}`, `{{ad.name}}`, `{{placement}}`, `{{site_source_name}}`. Recomendación práctica: `utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.id}}&utm_content={{ad.id}}&utm_term={{adset.id}}` (IDs, no nombres, para que renombrar no rompa el histórico). [EMPIRICAL] — verifica la lista de macros en la interfaz de tu cuenta.
- **Persistencia de primera parte:** guarda en tu backend `fbclid`, `fbc`, `fbp`, UTMs y `ad_id` (si lo pasas por macro) asociados al usuario/lead/pedido. Es lo que permite: CAPI con buen matching, conversiones offline/CRM atribuibles, reconciliación con Meta y AppendAttribution (archivo 10). [STRONG INFERENCE]
- **Restricción en sectores sensibles:** con *core setup* activo, Meta elimina todo lo que va después del dominio en las URLs (incluidas UTMs) y los parámetros custom. [EMPIRICAL] ([S04-082], [S04-083]) — ver archivo 09.

## Implicaciones operativas

- **Qué hacemos:** un dataset por negocio; Pixel + CAPI con los mismos eventos clave (como mínimo Purchase/Lead y los eventos que optimizas) y `event_id` determinista; capturar `fbclid` en servidor y persistir `fbc`; enviar `external_id` estable; IP/UA del usuario (no del servidor); real time; monitorizar EMQ, coverage, freshness y dedup semanalmente (o vía Dataset Quality API).
- **Qué evitamos:** varios Pixels para el mismo sitio sin necesidad; dos implementaciones del mismo evento (app + GTM + theme) sin coordinación de `event_id`; "server-only" sin construir `fbc`; enviar eventos con > 7 días; lotes grandes sin lógica de reintento (un error tumba 1.000 eventos).
- **Umbrales de decisión:** EMQ Purchase < 6 → prioridad alta; coverage < 75 % → revisar CAPI; dedup rate bajo con overlap bajo → `event_id` no compartido; freshness distinta de real time para web → revisar colas/batching.

## Errores frecuentes

1. Enviar en CAPI la IP del servidor/CDN o el UA de la librería HTTP → matching pobre y dedup por `fbp` inútil.
2. Generar `event_id` aleatorio distinto en navegador y servidor (dos `uuid()` independientes).
3. Hashear `fbc`, `fbp`, IP o UA (no se hashean) o no hashear `em`/`ph` (se rechazan).
4. Reescribir `fbclid` a minúsculas o perderlo en redirecciones (acortadores, geolocalizadores, redirecciones http→https mal configuradas, apps de idioma).
5. Confundir "evento recibido" con "evento atribuido".
6. Suponer que CAPI evita la necesidad de consentimiento o las restricciones de categorías sensibles.

## Preguntas abiertas

- ¿El límite de 7 días de `event_time` se relaja realmente a 62 días para `physical_store`? La documentación es ambigua (no verificado).
- ¿Cuánto pesa exactamente cada identificador en el EMQ? Meta solo publica prioridades cualitativas.
- Impacto real de Signals Gateway Pixel frente a Meta Pixel + CAPI en cobertura: no hay datos independientes.

## Fuentes clave

- [Using the Conversions API](https://developers.facebook.com/docs/marketing-api/conversions-api/using-the-api) — vigente 2026 — meta-developers (S04-009)
- [Server Event Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/server-event) — vigente — meta-developers (S04-008)
- [Customer Information Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters) — vigente — meta-developers (S04-006)
- [fbp and fbc Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/fbp-and-fbc) — vigente — meta-developers (S04-007)
- [Handling Duplicate Pixel and CAPI Events](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events) — vigente — meta-developers (S04-005)
- [Dataset Quality API](https://developers.facebook.com/docs/marketing-api/conversions-api/dataset-quality-api) — actualizado 2025-05-28 — meta-developers (S04-016)
- [External ID](https://developers.facebook.com/documentation/ads-commerce/conversions-api/parameters/external-id) — vigente — meta-developers (S04-055)
- [Parameter Builder Library](https://developers.facebook.com/docs/marketing-api/conversions-api/parameter-builder-feature-library) — vigente — meta-developers (S04-011)
- [Gateway Products changelog](https://developers.facebook.com/documentation/ads-commerce/gateway-products/changelog) — 2025 — meta-developers (S04-062)
- [Signals Gateway Pixel onboarding](https://developers.facebook.com/documentation/ads-commerce/gateway-products/signals-gateway/signals-gateway-pixel-onboarding) — vigente — meta-developers (S04-063)
- [WebKit Tracking Prevention](https://webkit.org/tracking-prevention/) — vigente — WebKit (S04-073)
