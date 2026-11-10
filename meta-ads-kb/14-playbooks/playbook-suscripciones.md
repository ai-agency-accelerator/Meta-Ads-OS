# Playbook: suscripciones (apps, web y e-commerce recurrente) en Meta Ads

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: negocios cuyo valor está en cobros recurrentes: apps de suscripción (iOS/Android), suscripciones vendidas por web (web-to-app) y e-commerce recurrente (subscribe & save, cajas). Detalle en `06-ecommerce-apps/09-…` y `10-…`.

## TL;DR

- **El CPA permitido lo fija el churn, no el algoritmo**: LTV ≈ margen × ARPU / churn; con ARPU 20 €/mes y 70 % de margen, el coste por trial máximo (12 meses, colchón 20 %, trial→pago 40 %) pasa de 32 € con churn 10 % a 26 € con churn 15 %. [STRONG INFERENCE — álgebra]
- **Optimiza al evento temprano más predictivo que Meta pueda ver a tiempo**: *qualified trial* en apps (filtra cancelaciones del día 0: 55 % de las cancelaciones de trials de 3 días ocurren ese día), pago inicial en web (Pixel + CAPI). [EMPIRICAL — RevenueCat, Airbridge, Adapty]
- **Hard paywall + trial** convierte ~5× más descarga→pago que freemium (10,7 % vs 2,1 % a 35 días; RPI 60 días 3,09 $ vs 0,38 $) con retención anual similar → es el modelo más "medible" en paid social. [EMPIRICAL — RevenueCat 2026]
- **Web-to-app** (comisión 2–6 % vs 15–30 %, señal rápida, cobro inmediato) gana con precio/LTV alto; en EE. UU. Apple no cobra comisión a compras enlazadas desde la app mientras el caso Epic sigue en el Supremo (revisión aceptada 30-jun-2026). Modela escenarios de comisión futura. [EMPIRICAL] + [OFFICIAL — 10-Q de Apple]
- **El churn anual empeoró en 2026** (~72 % de anuales cancela en el año 1 vs ~56 % en 2025): recalcula LTV con cohortes recientes. [EMPIRICAL — RevenueCat]

## 1. Cuándo usar Meta

| Sí | Con cautela |
|---|---|
| Producto con "momento aha" rápido (≤ 3 días) y paywall claro | Valor que tarda semanas en percibirse (la señal llega tarde) |
| Mercado amplio y visual (fitness, idiomas, bienestar, productividad, IA, citas, finanzas personales) | Nichos B2B pequeños |
| Capacidad de producir creatividad nativa (UGC, demos, comparativas) | Sin tracking server-side (trials invisibles para Meta) |
| LTV ≥ 3× el CPI razonable de la categoría | LTV bajo con monetización solo por publicidad (usar MAI/ROAS de AdImpression) |

## 2. Arquitectura por presupuesto (gasto mensual)

| Gasto | Prioridad | Estructura |
|---|---|---|
| **< 20k €/mes (~€100–650/día)** | Setup: que Meta vea ≥ 80–90 % de trials/pagos (Burke: casos con solo ~10 % atribuidos) | 1 campaña por SO (iOS con AEM, Android) o 1 campaña web; 1 ad set; evento qualified trial / pago web; 5–10 creatividades |
| **20–100k €/mes** | Grandes apuestas creativas (formatos, estilos, mensajes) | 1–2 campañas por SO + test creativo; evaluar calidad (trial→pago) por placement |
| **100–500k €/mes** | Diversificar placements/audiencias, experimentos de pricing/onboarding, web-to-app | AEO y VO en paralelo; W2A en campaña/cuenta separada (Blinkist); por encima de ~500k probablemente se necesita web + app (Burke) |
| **> 500k €/mes (~€16.000+/día)** | Incrementalidad y mix | Geo-lift/Conversion Lift; MMM; portafolio de pujas y geos |

Equivalencia con los tramos estándar de esta KB: €100/día ≈ 3k/mes (fase setup), €500/día ≈ 15k/mes (setup→creatividad), €5.000/día ≈ 150k/mes (diversificación + W2A), €50.000/día ≈ 1,5 M/mes (medición incremental y mix).

## 3. Evento

| Situación | Evento recomendado |
|---|---|
| App con trial y cancelación día 0 alta (> 30 %) | Qualified trial (retraso 2–4 h o trial no cancelado) |
| App con trial y ≥ 50 pagos/ad set/semana | Pago (Subscribe) o VO |
| Hard paywall sin trial / paid trial | Purchase/Subscribe con valor |
| Web-to-app | Purchase web (Pixel + CAPI, `event_id`), valor = primer cobro neto |
| E-commerce recurrente | Primera compra de suscripción con valor; opcional pLTV vía CAPI |
| Freemium | Evento de activación que prediga pago (validado con cohortes) |

Umbrales de VO que circulan (≥ 30 compras con ≥ 5 valores en 14 días) no están confirmados oficialmente. [CONTESTED]

## 4. Creatividades

- **Demostración del resultado** (antes/después de uso, pantalla real de la app, progreso).
- **Text-wall, infografías, comparativas** (formatos en auge en 2025 según Burke; comparativas con moderación).
- **UGC en nuevos formatos** (el talking head genérico está sobreexplotado según Burke).
- **Editorial / advertorial** hacia artículo → app/checkout (Blinkist).
- **Precio y garantía** visibles en W2A (reduce trials de baja intención).
- IA generativa para estáticos/animación (Burke cita Midjourney, Flux, Runway, Kling, Veo) con control de calidad.

## 5. Funnel

**App directa**: anuncio → store → instalación → onboarding → paywall (trial) → conversión trial→pago → renovaciones.
**Web-to-app**: anuncio → landing/quiz → paywall web (Apple/Google Pay) → pago → descarga con deep link y auto-login → uso → renovaciones (enviadas server-side a Meta).
**E-commerce recurrente**: anuncio → PDP con opción suscripción → primera caja (oferta de entrada) → cajas sucesivas → gestión de pagos fallidos.

## 6. Métricas y umbrales

| Métrica | Regla |
|---|---|
| Coste por trial / suscriptor | ≤ máximo derivado del LTV de cohortes recientes (tabla §8) |
| Trial→pago | Comparar con mediana por duración de trial: 42,5 % (17–32 d), 37,4 % (5–9 d), 25,5 % (≤ 4 d) |
| Cancelación día 0 | > 30 % → qualified trial |
| Gap Meta vs backend | 10–20 % normal; más → revisar SDK/CAPI/dedup (Adapty) |
| Supervivencia M1/M3/M12 | Alerta si cae > 10 % relativo vs cohortes anteriores |
| Pagos fallidos | Recuperación con reintentos; web ~50 % fallidos iniciales (RevenueCat) |
| Payback de caja | Explícito (Apple paga ~45 días tras cierre de mes; Google ~día 15 del mes siguiente) |
| Escalado | +~20 % cada 1–3 días con 3–7 días estables (Adapty) |

## 7. Errores frecuentes

- LTV con churn antiguo.
- Optimizar a trial y no mirar trial→pago por placement.
- Contar dos veces al mismo pagador (web + app, SDK + CAPI).
- ROAS sobre ingresos brutos antes de comisión de tienda.
- Ofertas de entrada (50 % primera caja, trials largos gratis en web) que atraen baja intención.
- Evaluar W2A por conversión de landing en vez de LTV:CAC.

## 8. Ejemplo numérico completo

**App de idiomas, iOS + web, EE. UU./UE.** ARPU equivalente 20 €/mes; margen tras comisiones, IVA y servicio: 70 % (14 €/mes).

**Tabla de CAC permitido (horizonte 12 meses, colchón 20 %)**

| Churn mensual | LTV₁₂ | CAC/suscriptor máx. | Coste/trial máx. (trial→pago 40 %) |
|---|---|---|---|
| 10 % | 100,5 € | 80,4 € | 32,2 € |
| 15 % | 80,1 € | 64,1 € | 25,6 € |

**Situación**: campaña iOS a qualified trial con coste/trial 28 € y trial→pago 40 % → CAC/suscriptor 70 €.
- Si el churn real es 10 % → CAC máx. 80,4 € → **rentable**, margen para escalar ~15 %.
- Si las cohortes recientes muestran 15 % → CAC máx. 64,1 € → **pierde** ~6 € por suscriptor; no escalar; acciones: onboarding, plan anual por defecto, recuperación de pagos fallidos.

**Web-to-app**: misma app, plan anual 79,99 € en web (comisión ~5 %) vs 79,99 € en App Store (15–30 %). Ingreso neto por anual: web ~76 € vs app 56–68 €. Si la conversión web es un 20 % menor pero el neto un 12–36 % mayor y la renovación algo mejor, el LTV:CAC puede favorecer W2A — **decídelo con 3–6 meses de cohortes**, no con la tasa de conversión de la landing.

## Fuentes clave

- [State of Subscription Apps 2026 (RevenueCat)](https://www.revenuecat.com/blog/growth/subscription-app-trends-benchmarks-2026) — 2026-03-19 — vendor
- [Web-to-app funnels: complete 2026 guide (RevenueCat)](https://www.revenuecat.com/blog/growth/web-to-app-funnels) — 2025-12-11 — vendor
- [Meta Ads in 2025: Marcus Burke (RevenueCat)](https://www.revenuecat.com/blog/growth/meta-ads-in-2025-tips-for-apps) — 2025-04-08 — practitioner
- [Paid UA for apps: 12 questions (Adapty)](https://adapty.io/blog/meta-ads-subscription-apps/) — 2026-06-22 — practitioner
- [Install, Trial, Subscribe (Airbridge)](https://www.airbridge.io/en/blog/app-event-optimization-subscription-apps) — 2026-03-20 — vendor
- [Meta Web-to-App vs Direct Install (Admiral Media)](https://admiral.media/web-to-app-vs-app-install-ads/) — 2026-06-15 — agencia
- [Apple 10-Q (Epic v. Apple)](https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000020/aapl-20260627.htm) — 2026 — oficial (SEC)
