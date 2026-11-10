# Meta vs GA4 vs Shopify vs CRM vs Stripe vs servidor: por qué no coinciden y qué fuente usar

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: reconciliación de cifras entre plataformas, causas estructurales de discrepancia, tabla de decisión "qué fuente responde a qué pregunta" y procedimiento de reconciliación.

## TL;DR

- **No deben coincidir.** Meta *reclama* conversiones de personas que interactuaron con sus anuncios (clic de enlace, engage-through, view-through) dentro de su ventana; GA4 *modela sesiones* y reparte crédito entre canales que ve por URL/cookies (sin impresiones de Meta); Shopify *cuenta pedidos* y los atribuye por defecto con *last non-direct click* a 30 días; el CRM/Stripe *cuentan dinero real* (con cancelaciones, reembolsos, impuestos). [EMPIRICAL] ([S04-080]) + [OFFICIAL Google] ([S04-079]) + [OFFICIAL META] ([S04-003])
- **Dirección típica:** Meta ≥ GA4 en conversiones atribuidas a Meta (view/engage-through, cross-device con login, matching por email); backend ≥ Meta en total de pedidos (Meta solo ve una parte); Meta ≥ backend → **sospecha de duplicados** o de valor mal definido. [STRONG INFERENCE]
- **La suma de lo que reclaman todas las plataformas supera las ventas reales** porque cada una atribuye con su propia ventana y sin ver a las demás. [EMPIRICAL] ([S04-080])
- **Pregunta → fuente:** "¿Cuánto vendí?" → backend (Shopify/ERP/Stripe neto). "¿Qué ad set rinde mejor *dentro* de Meta?" → Ads Manager (misma configuración de atribución). "¿Qué ventas *causó* Meta?" → experimento (lift/geo) o, en su defecto, Incremental attribution + MMM. "¿Cómo se reparten canales en el sitio?" → GA4 con cautela. "¿Calidad de leads/LTV?" → CRM. [STRONG INFERENCE]
- **Reconciliar siempre en el mismo eje:** misma zona horaria, misma moneda, misma definición de valor (bruto/neto, con/sin IVA y envío), mismo universo (online vs total, con consentimiento), y comparando **Events Manager (recibidos)** con backend antes de comparar **Ads Manager (atribuidos)**. [STRONG INFERENCE]

## 1. Cómo cuenta cada sistema

| Dimensión | Meta Ads Manager | GA4 | Shopify | CRM | Stripe | Servidor/logs CAPI |
|---|---|---|---|---|---|---|
| Unidad | Conversión atribuida a un anuncio | Key event en sesión/usuario | Pedido | Lead/oportunidad/venta | Pago/cargo | Evento enviado |
| Quién recibe crédito | Último anuncio de Meta con interacción elegible (clic > vista) | Data-driven (por defecto) entre canales; lookback 30 d (adquisición) / 90 d (resto) | Last non-direct click, 30 días (por defecto) | Según el CRM (UTM, primera fuente, manual) | Nadie (no atribuye) | Nadie |
| Ve impresiones de Meta | Sí | No | No | No | No | No |
| View-through | Sí (1 día) | No | No | No | — | — |
| Engage-through (likes, vídeo ≥5 s) | Sí (1 día) | No | No | No | — | — |
| Cross-device | Fuerte (usuarios logueados en Meta) | Limitado (User-ID / Google signals) | Limitado | Si hay ID de cliente | — | Según IDs enviados |
| Fecha | Conversión (offsite) en zona horaria de la cuenta publicitaria | Evento, zona horaria de la propiedad | Pedido, zona horaria de la tienda | Cambio de etapa | Cargo (zona configurable; verificar) | `event_time` (UTC) |
| Moneda | Moneda de la cuenta publicitaria (convierte) | Moneda de la propiedad | Moneda de tienda/presentación | Variable | Moneda del cargo | La enviada |
| Consentimiento | Solo eventos permitidos | Consent Mode + modelado | Pedidos siempre | Siempre | Siempre | Según tu filtro |
| Modelado | Sí (ATT/AEM, agregados) | Sí (Consent Mode, DDA) | No | No | No | No |
| Reembolsos/cancelaciones | No restan | No (salvo eventos `refund`) | Sí (ventas netas) | Sí | Sí | No |

Fuentes: GA4 lookback y modelos [OFFICIAL Google] ([S04-079]); Shopify modelo/ventana [EMPIRICAL] ([S04-080]); Meta tipos de interacción y fecha [OFFICIAL META] ([S04-003], [S04-050]); resto [STRONG INFERENCE].

Notas:
- GA4 retiró first click, linear, time decay y position-based en **nov-2023**; quedan data-driven y last click (paid & organic / Google paid). [OFFICIAL Google] ([S04-079])
- Shopify retiró en **abril de 2025** los informes "conversion by first/last interaction" y "attribution model comparison" en favor del informe de rendimiento por canal; los modelos se eligen por informe (last non-direct click, last click, first click, any click, linear). [EMPIRICAL] ([S04-080])

## 2. Causas de discrepancia (y en qué dirección empujan)

| Causa | Efecto típico | Cómo comprobar |
|---|---|---|
| View-through 1 día y engage-through 1 día | Meta > GA4/Shopify en conversiones "de Meta" | Columnas por tipo de atribución en Ads Manager |
| Ventana 7d click vs 30/90 d en GA4/Shopify | Para compras tras 8–30 días: GA4/Shopify pueden dar crédito a Meta y Meta no | Comparar con 28d click (columna) |
| Cross-device (clic en móvil en app de Instagram, compra en desktop) | Meta lo atribuye (usuario logueado + matching), GA4 lo ve como "direct"/otro canal | — |
| In-app browser de Instagram/Facebook → cookies separadas del navegador del sistema | GA4 parte sesiones; Shopify ve "direct" si el usuario termina en otro navegador | — |
| Pérdida de UTMs/`fbclid` en redirecciones | GA4/Shopify: direct/referral; Meta mantiene parte vía matching | Prueba de cadena de redirecciones |
| Consentimiento rechazado (UE) | Meta y GA4 infra-cuentan (GA4 modela parte); backend completo | Tasa de consentimiento del CMP |
| Ad blockers | Pixel/GA4 pierden; CAPI no | Ratio Pixel/CAPI en Events Manager |
| Duplicados (dos Pixels, recargas, dedup roto) | Meta > backend | Events Manager por "connection method"; Test Events |
| Valor distinto (impuestos, envío, descuentos, moneda) | ROAS difiere aunque coincidan conversiones | Comparar valor medio por pedido |
| Zona horaria (cuenta Meta vs tienda vs GA4) | Desplazamiento de pedidos entre días | Comparar semanas/meses, no días |
| Fecha de reporte (conversión vs impresión, datos tardíos) | Días recientes incompletos en Meta | Esperar 3–7 días; ver 12-attribution-lag |
| Reembolsos, cancelaciones, fraude, pedidos de prueba | Meta > neto real | Backend neto vs bruto |
| Modelado (ATT/AEM, Consent Mode) | Cifras no enteras/estimadas | — |
| Pedidos sin sesión (POS, borradores, suscripciones) | Backend > Meta/GA4 | Filtrar por canal de venta |
| Incremental attribution activada | Meta < standard | Columnas de comparación |

[STRONG INFERENCE] salvo referencias en otros archivos (03, 09, 10).

## 3. Tabla de decisión: qué fuente responde a qué pregunta

| Pregunta | Fuente principal | Fuente de contraste | Advertencia |
|---|---|---|---|
| ¿Cuántos pedidos/ingresos tuve? | Backend (Shopify/ERP), Stripe neto | — | Define bruto vs neto |
| ¿Funciona Meta (causalmente)? | Conversion Lift / geo test / holdout | Incremental attribution, MMM | Ver archivos 13–14 |
| ¿Qué campaña/ad set/creativo rinde mejor dentro de Meta? | Ads Manager (misma configuración de atribución) | Incremental attribution (columna) | Comparar dentro de Meta, no contra GA4 |
| ¿Cuánto presupuesto total y mix de canales? | MMM calibrado con experimentos | Atribución de plataformas | MMM requiere historial (archivo 14) |
| ¿Está bien instalado el tracking? | Events Manager vs backend (eventos recibidos) | Pixel Helper, Test Events | No uses Ads Manager para QA de tracking |
| ¿Cuál es el CAC/LTV real por cohorte? | CRM/backend con `fbclid`/`ad_id`/UTM persistidos | Meta (first conversion) | Atribución propia ≠ causalidad |
| ¿Calidad de leads por campaña? | CRM (etapas) | Meta (eventos CRM vía CAPI) | Ciclos largos (archivo 12) |
| ¿Comportamiento en el sitio (embudo, UX)? | GA4 | Shopify analytics | GA4 no es árbitro de atribución de Meta |
| ¿Ventas en Amazon/retail por Meta? | Geo test / MMM | Haus-like experiments | Meta no lo ve (Haus: ~32 % del impacto fuera de DTC en marcas omnicanal) [EMPIRICAL] ([S04-021]) |

## 4. Procedimiento de reconciliación (mensual, o al detectar alarma)

1. **Normaliza el eje:** periodo semanal o mensual; misma zona horaria; misma moneda; definición de valor (p. ej. "total pedido con IVA, sin reembolsos").
2. **Backend online** (pedidos web con consentimiento, si puedes segmentarlo) = universo máximo.
3. **Events Manager — Purchase recibidos** (no atribuidos), por canal (browser/server) → debe ser ≈ backend online con consentimiento. Desviación > 5 % = problema de tracking (duplicados o pérdidas).
4. **Ads Manager — Purchase atribuidos** (7d click + 1d view + engage-through, y por separado 1d/7d click) → proporción del backend que Meta reclama.
5. **GA4 — conversiones con fuente/medio de Meta** (y "direct" sospechoso) → orden de magnitud.
6. **Backend con `ad_id`/UTM** (si persistes `fbclid`/UTM en el pedido) → ventas con clic de Meta trazable.
7. **Ratio de inflación de plataforma:** Meta atribuido ÷ ventas con clic de Meta en backend. Úsalo como *factor de ajuste* hasta tener un experimento; con experimento, usa el **incrementality factor** (incrementales ÷ reportadas). [EMPIRICAL] (definición usada por Haus/Recast, [S04-021])

### 4.1 Ejemplos

- **"Shopify dice 100 pedidos, Events Manager 104 Purchase, Ads Manager 61":** tracking sano (±5 %); Meta reclama el 61 % — normal para cuentas con mucho tráfico pagado; compáralo con el % de sesiones de Meta. Decide inversión con incrementalidad, no con el 61 %.
- **"Stripe 13 ventas, Ads Manager 20":** revisa (a) Events Manager: ¿20+ Purchase recibidos para 13 pagos? → duplicados (Pixel + CAPI sin dedup, recargas de thank-you, dos píxeles); (b) ¿eventos de prueba o pagos fallidos que disparan Purchase en la thank-you? (c) ¿reembolsos/disputas restados en Stripe? (d) ¿zona horaria? (e) ¿view-through/engage-through de compras de otro producto/ciclo? Árbol completo en archivo 16.
- **"Tenemos 8 ventas pero Ads Manager ve 3":** puede ser normal (5 sin interacción con Meta en ventana o sin match) o pérdida de señal (`fbclid` perdido, CAPI ausente, consentimiento). Ver archivo 16.

## Implicaciones operativas

- **Hacemos:** un "contrato de métricas" por cliente (definición de valor, zona horaria, fuente de verdad por pregunta); persistir `fbclid`/`ad_id`/UTMs en pedidos y leads; informe mensual de reconciliación con los 7 pasos; incrementality factor por canal actualizado con cada experimento.
- **Evitamos:** "arreglar" la atribución cambiando ventanas para que Meta = GA4; usar GA4 como verdad absoluta sobre Meta; sumar conversiones de plataformas.
- **Umbrales:** Events Manager vs backend ±5 %; si Meta atribuido > ventas totales de la tienda en el periodo → incidencia crítica.

## Errores frecuentes

1. Comparar días sueltos (zonas horarias y datos tardíos).
2. Comparar Ads Manager (atribuido) con backend para auditar tracking (deberías comparar Events Manager).
3. Ignorar el cambio de definición de click de marzo de 2026 en series temporales.
4. Considerar "direct" de GA4/Shopify como no-Meta.

## Preguntas abiertas

- Cuánto del "direct" de Shopify/GA4 es tráfico de Meta in-app no trazable (no hay cifra pública fiable).
- Tipo de cambio y momento de conversión de moneda que aplica Meta a `value` (no documentado en las páginas consultadas).

## Fuentes clave

- [GA4 Attribution settings](https://support.google.com/analytics/answer/10597962) — vigente — vendor (S04-079)
- [How Shopify Attribution Works](https://weltpixel.com/blogs/news/how-shopify-attribution-works-first-click-last-click-and-direct-orders) — 2026-06-15 — vendor (S04-080)
- [Simplifying Ad Measurement (Meta)](https://www.facebook.com/business/news/click-attribution) — 2026-03-03 — meta-oficial (S04-003)
- [Insights API — discrepancy with Ads Manager](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/best-practices) — vigente — meta-developers (S04-050)
- [Haus: The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor (S04-021)
