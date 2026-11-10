# Atribución en Meta: ventanas, tipos de interacción, modelos y cambios 2025–2026

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A04 (agente) · Ámbito: cómo atribuye Meta las conversiones, qué ventanas existen hoy (Ads Manager y API), qué se eliminó, *engage-through*, *incremental attribution*, *custom attribution* (AppendAttribution), fecha de reporte y cómo elegir configuración.

## TL;DR

- **Tres tipos de interacción atribuible (desde marzo de 2026):** *click-through* = **solo link clicks** (para conversiones web e in-store); *engage-through* (antes *engaged-view*) = interacciones sin link click (likes, shares, saves, comentarios, visitas al perfil…) y vistas de vídeo de **≥ 5 s** (antes 10 s); *view-through* = impresión sin interacción. Anuncio oficial de Meta: 3-mar-2026, despliegue "a finales de ese mes", sin cambio de facturación. [OFFICIAL META] ([S04-003])
- **Ventanas disponibles:** click 1 o 7 días (28 días click aún consultable en reporting/API), engage-through 1 día, view-through 1 día. **La API dejó de devolver `7d_view` y `28d_view` el 12-ene-2026** (incluidas combinaciones que los contengan); quedan `1d_click`, `7d_click`, `28d_click`, `1d_ev`, `1d_view` (+ `incrementality` y valores por defecto). [OFFICIAL META] ([S04-001], [S04-048], [S04-051]). En Ads Manager, 7d/28d view ya no eran configurables desde los cambios de iOS 14 (2021) [STRONG INFERENCE — conocimiento público del cambio de 2021, no reverificado aquí].
- **Configuración por defecto (web):** 7-day click + 1-day view, y tras marzo de 2026 con 1-day engage-through activado por defecto para campañas optimizadas a conversiones web/in-store (desactivable eligiendo "none"). La inclusión por defecto de engage-through procede de fuentes secundarias concordantes; Meta "recomienda encarecidamente" usarla. [OFFICIAL META] (recomendación, [S04-003]) + [EMPIRICAL] (default exacto, [S04-004])
- **La configuración de atribución no es solo de reporting: define qué conversiones "cuentan" para el aprendizaje de la entrega del ad set.** Cambiarla altera la señal de optimización (y puede reiniciar aprendizaje). [OFFICIAL META] (concepto de Meta desde 2021) + [STRONG INFERENCE]
- **Incremental attribution** (anunciada otoño 2024, despliegue primavera 2025, documentación ampliada sep-2025): alternativa a "Standard" en ad sets de conversiones; "optimiza la entrega para conversiones incrementales usando modelos que predicen si una conversión fue causada por un anuncio". También usable solo como columna de comparación. Evidencia independiente (Haus): 0,80× iROAS vs standard en jul-24/jun-25 → **1,26×** en jul-25/jun-26. [OFFICIAL META] ([S04-018]) + [EMPIRICAL] ([S04-022])
- **Custom Attribution / AppendAttribution (beta, 2026):** el anunciante (o Northbeam, Rockerbox, Triple Whale, Adobe) envía por CAPI su propio reparto de crédito por anuncio (≤ 48 h tras la compra) y Meta puede **optimizar** con ese modelo tras ~14 días de entrenamiento. Es el cambio estructural más importante de 2026 en atribución. [OFFICIAL META] ([S04-052], [S04-053])
- **Fecha del reporte:** las acciones off-Meta (p. ej. compras web) se reportan por **fecha de conversión**; las on-Meta (link clicks) por fecha de impresión (`action_report_time=mixed`, alineado entre API y Ads Manager desde 10-jun-2025; conversión-time para offsite desde 2021). La creencia de que "Meta reporta las compras en el día de la impresión" está **desactualizada** para web. [OFFICIAL META] ([S04-050], [S04-068]) + [OUTDATED]

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **"Mide las conversiones en los dispositivos de los clientes"** (Help Center 4237575203200036): ajuste del píxel activado por defecto desde el **12-nov-2026** (fecha según terceros); no activo para personas en la UE ni el Reino Unido; empareja en el dispositivo la visualización del anuncio y la compra con datos que ya compartes (p. ej. email) e información temporal del dispositivo; complementa píxel y CAPI y **no cambia ventana ni modelo**. Efecto esperado: más compras reportadas → marca la fecha y no compares a través de ella. **[OFFICIAL META]** Requisitos según terceros: web con login por email o teléfono, sin iframe ni píxel de imagen; solo compra. **[EMPIRICAL]** Si alimenta también la optimización: **[HYPOTHESIS]**.
> - **Ajustes de atribución** (Help Center 460276478298895, leído el 2026-11-09): 1 o 7 días tras clic en enlace, 1 día tras impresión y engage-through de 1 día; el despliegue sigue en curso en algunas cuentas; aparece un modelo **"custom"** además de estándar e incremental, sin más detalle. **[OFFICIAL META]**
> - Los cambios del 3-mar-2026 se refieren a conversiones web y en tienda; ninguna fuente oficial dice que afecten a los leads de instant form. **[HYPOTHESIS]**
> - iOS 27.2 (26-oct, aviso ATT alternativo en la UE): otra discontinuidad para apps con usuarios europeos. **[EMPIRICAL]**
> - Fuentes: S10-105, S10-110, S10-111, S10-130, S10-140 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. Cómo decide Meta a qué anuncio da crédito

1. La conversión (evento emparejado con una persona) debe tener **una interacción elegible dentro de la ventana** configurada en el ad set que optimiza/reporta.
2. Modelo de **último toque dentro de Meta**: el crédito va a un único anuncio; los clics tienen prioridad sobre las visualizaciones y, entre clics, gana el más reciente. [EMPIRICAL] (Jon Loomer, "which ad gets credit") — Meta no publica un documento técnico detallado.
3. Solo cuenta lo que Meta puede ver: conversiones de personas emparejadas, con consentimiento y dentro de las restricciones de datos. Fuera de Meta (Google, email, orgánico) no existe para este modelo.
4. Cada ad set tiene su configuración; columnas de "Compare attribution settings" permiten ver el mismo periodo con otras ventanas sin cambiar la entrega. [EMPIRICAL] ([S04-004])

### 1.1 Reclasificación de marzo de 2026

| Interacción | Antes (hasta feb-2026) | Después (desde finales de mar-2026) |
|---|---|---|
| Link click | Click-through | Click-through |
| Like, share, save, comentario, visita a perfil | Click-through ("clicks (all)") | Engage-through (1 día) |
| Vídeo visto ≥ umbral sin clic | Engaged-view (umbral 10 s) | Engage-through (umbral 5 s) |
| Impresión sin interacción | View-through (1 día) | View-through (1 día) |

Fuentes: [OFFICIAL META] (link clicks, renombrado, 10 s → 5 s, [S04-003]); tabla y ventana de 1 día de engage-through: [EMPIRICAL] ([S04-004]).

Consecuencias:
- **Click-through baja** (parte pasa a engage-through) aunque el total pueda quedarse similar; conversiones de días 2–7 tras una interacción no-link que antes eran "7-day click" ahora quedan fuera (engage-through es de 1 día). [EMPIRICAL] ([S04-004])
- **Comparaciones interanuales** que crucen marzo de 2026 mezclan definiciones: usar baseline desde mediados de marzo de 2026 o comparar con totales de negocio. [EMPIRICAL] ([S04-004])
- **Justificación de Meta:** alinear "click" con la definición de herramientas como Google Analytics (solo link clicks) y reconocer que en social las interacciones no-link también influyen; Meta se asoció con **Northbeam y Triple Whale** para que incluyan clics y vistas en sus modelos. [OFFICIAL META] ([S04-003])

## 2. Ventanas: qué existe, qué se eliminó

| Ventana | Ads Manager (configurar ad set) | Ads Manager (comparar/columnas) | Insights API (`action_attribution_windows`) |
|---|---|---|---|
| 1-day click | Sí | Sí | `1d_click` |
| 7-day click | Sí (default) | Sí | `7d_click` |
| 28-day click | No (desde 2021) [STRONG INFERENCE] | Sí (según guías 2026; otras dicen que ya no está en la UI estándar, [S04-101]) [CONTESTED] | `28d_click` [OFFICIAL META] |
| 1-day engage-through (antes engaged-view) | Sí (1 día fijo) | Sí | `1d_ev` [OFFICIAL META] |
| 1-day view | Sí (o "none") | Sí | `1d_view` |
| 7-day view | No (desde 2021) | No | **Eliminada 12-ene-2026** |
| 28-day view | No (desde 2021) | No | **Eliminada 12-ene-2026** |
| Incremental | Sí ("Incremental attribution", en lugar de Standard) | Sí | `incrementality` [OFFICIAL META] |

Fuentes API: [OFFICIAL META] ([S04-001], [S04-051]). Comportamiento ante ventanas eliminadas: devuelven datos vacíos, no error, según PPC Land ([S04-002]); el changelog de Meta dice "will return no data". [OFFICIAL META] ([S04-048])

Otros cambios de la API ligados a atribución:
- **10-jun-2025:** `use_unified_attribution_setting` y `action_report_time` se ignoran; la API replica Ads Manager (valores según la configuración del ad set; acciones inline incluidas en `1d_click`/`1d_view`; desaparece la ventana `inline` independiente; `action_report_time=mixed`). [OFFICIAL META] ([S04-048], [S04-050])
- **12-ene-2026:** límites de histórico (breakdowns de métricas únicas y horarios 13 meses, frecuencia 6 meses; totales 37 meses). [OFFICIAL META] ([S04-001])
- Los insights se refrescan cada ~15 min y **no cambian tras 28 días** de reportados. [OFFICIAL META] ([S04-050])

## 3. Fecha de reporte (conversion time vs impression time)

- Desde el despliegue de iOS 14 (2021) Meta reporta las conversiones offsite **en la fecha en que ocurre la conversión**, no en la de la impresión, para que coste y conversiones del mismo periodo sean comparables. [OFFICIAL META] ([S04-068])
- Desde el 10-jun-2025 la API lo explicita como `mixed`: on-Meta por impresión, off-Meta por conversión. [OFFICIAL META] ([S04-050])
- Implicación: una compra 5 días después del clic aparece en el día de la compra (no "rellena" el día del clic). Pero los **datos recientes siguen incompletos** por llegada tardía de eventos (CAPI tardío, AEM con retraso, modelado, offline, CRM) — ver `12-attribution-lag.md`. [STRONG INFERENCE]
- Herramientas de terceros (Supermetrics, etc.) aún ofrecen "report time" como opción; si muestran otra cosa que Ads Manager, comprueba qué piden a la API. [EMPIRICAL]

## 4. "All conversions" vs "First conversion"

- Ads Manager permite reportar **todas** las conversiones (por defecto) o solo la **primera** de cada tipo de evento por persona (disponible desde 2024; datos desde jul-2023 según fuentes secundarias). Es solo de reporting; no cambia la entrega. Útil para CAC y para leads duplicados. [EMPIRICAL] ([S04-100]) — enlaces a Help Center 458681590974355 y 460276478298895 (no descargados).

## 5. Incremental attribution

### 5.1 Qué es
- Meta: "Incremental attribution optimizes delivery for incremental conversions using models that predict whether a conversion is caused by an ad"; Standard "optimizes delivery for selected time windows and user behaviors". [OFFICIAL META] ([S04-018])
- Base académica coherente: el método PIE (Gordon, Moakler [Meta], Zettelmeyer) predice la incrementalidad de campañas a partir de 2.226 RCTs de Meta con R² 0,88 fuera de muestra frente a 0,19 del last-click 7 días. Que el producto use exactamente PIE no está confirmado. [STRONG INFERENCE] ([S04-077])
- Fuentes secundarias afirman que el modelo se entrena con datos de Conversion Lift de Meta; plausible pero no verificado en texto oficial. [HYPOTHESIS]

### 5.2 Dónde y cómo
- Ad set de conversiones (Sales/Leads/Engagement con ubicación web y meta "maximize conversions"; algunos guías añaden "maximize value") → "Attribution setting" → *Standard* o *Incremental*. No disponible en Traffic/Awareness. Despliegue gradual: elegibilidad variable por cuenta. [EMPIRICAL] ([S04-019], [S04-020])
- Con Incremental no se eligen ventanas y el desglose por configuración de atribución no funciona. [EMPIRICAL] ([S04-019])
- **Modo medición:** columnas "Compare attribution settings" > Incremental, sin cambiar la entrega. [EMPIRICAL] ([S04-020])

### 5.3 Evidencia
| Fuente | Resultado | Lectura |
|---|---|---|
| Haus (jul-2025, tests hasta jun-2025) | IA ganó a standard en 43 % de tests; geo-mean 0,80× iROAS | Al lanzarse, no mejor que standard [EMPIRICAL] ([S04-021], [S04-022]) |
| Haus (jul-2026, tests jul-25/jun-26) | IA/standard iROAS geo-mean **1,26×** (DTC 1,38×; omnicanal 1,02×); muestra "modesta" | Mejora clara en el último año, sobre todo DTC [EMPIRICAL] ([S04-022]) |
| Jon Loomer (sep-2025) | En sus pruebas, CPA más alto sin mejora clara de calidad; la mayoría de conversiones standard también aparecen como incrementales | Usar IA como contexto; testear antes de migrar [EMPIRICAL] ([S04-019]) |

**Interpretación:** IA reporta menos conversiones (filtra no incrementales) y puede subir el CPA aparente mientras mejora el iROAS real; solo un experimento (holdout/geo) lo demuestra para tu cuenta. [STRONG INFERENCE]

## 6. Custom Attribution vía AppendAttribution (beta 2026)

- **Qué es:** "enables advertisers to optimize Meta ad campaigns using their own attribution model's credit assignments". Se envía un evento CAPI estándar `AppendAttribution` que añade crédito a una conversión original (p. ej. Purchase) ya recibida. [OFFICIAL META] ([S04-052])
- **Requisitos:** cobertura completa de Purchase (web) o `fb_mobile_purchase` (app) en el dataset; enviar AppendAttribution **< 48 h** tras el evento original (si no, "low quality"); crear una *Custom Attribution Source* (CAS) en Events Manager; ciclo Pending → In Training (14 días desde el primer evento de calidad) → Setup Complete → Ready to Use. Beta con acceso limitado. [OFFICIAL META] ([S04-052])
- **Payload:**
```json
{
  "event_name": "AppendAttribution",
  "event_time": 1760603000,
  "event_id": "aa_ORD-100045_ad6283824241739",
  "action_source": "website",
  "event_source_url": "https://www.ejemplo.es/checkout/thank-you",
  "attribution_data": {
    "ad_id": 6283824241739,
    "touchpoint_ts": 1760590000,
    "attribution_share": 0.3,
    "attribution_value": 38.97
  },
  "original_event_data": {
    "event_name": "Purchase",
    "event_time": 1760600000,
    "order_id": "ORD-100045"
  },
  "custom_data": { "currency": "EUR" },
  "user_data": { "fbc": "fb.1.…", "client_user_agent": "…", "client_ip_address": "…",
                 "em": ["<sha256>"], "ph": ["<sha256>"], "external_id": ["…"] }
}
```
`attribution_value` = `attribution_share` × valor; las shares de una conversión deben sumar 1; `touchpoint_ts` < `original_event_data.event_time`; `event_id` único por evento de passback. Validación: exportar `attributed_value`/`attributed_share` por campaña/día y comparar con tu sistema (0–5 % normal; > 5 % investigar). [OFFICIAL META] ([S04-052], [S04-053])
- **Por qué importa:** es la primera vía oficial para que la **optimización** de Meta use un modelo de atribución externo (p. ej. multi-touch o calibrado con experimentos). Riesgo: si tu modelo externo está sesgado, Meta optimizará hacia ese sesgo. [STRONG INFERENCE]

## 7. Elegir configuración (guía de decisión)

| Negocio | Recomendación inicial | Por qué |
|---|---|---|
| E-commerce impulso, AOV bajo, ciclo corto | 7d click + 1d engage-through + 1d view (default) | Más señal para aprender; validar con lift |
| E-commerce AOV alto / ciclo de consideración | 7d click (+ engage-through), evaluar quitar view | Reduce crédito a impresiones en usuarios que comprarían igual |
| Retargeting/audiencias calientes | Considerar quitar view y/o probar Incremental | View-through en audiencias calientes es el más inflado [EMPIRICAL] (Haus/práctica) |
| Lead gen formularios | 1d o 7d click; engage-through a valorar | Leads rápidos; view-through aporta poco |
| Marca con mucho offline/Amazon | Standard + medición externa (geo/MMM) | Meta no ve el halo fuera de DTC (Haus: ~32 % del impacto fuera de DTC) [EMPIRICAL] ([S04-021]) |
| Equipo con MTA/MMM calibrado y volumen | Probar Custom Attribution (beta) o Incremental | Alinear optimización con la métrica de negocio |

Principios: (1) no cambies la configuración a menudo (cambia la señal); (2) compara configuraciones con columnas antes de cambiar; (3) decide con experimentos, no con el ROAS que cada configuración "reclama". [STRONG INFERENCE]

## Implicaciones operativas

- **Hacemos:** documentar la configuración de atribución por ad set; añadir columnas de comparación (1d click, 7d click, engage-through, 1d view, incremental) a la vista estándar; anotar el corte de marzo de 2026 en dashboards; migrar integraciones API que pedían `7d_view`/`28d_view`.
- **Evitamos:** comparar ROAS de periodos con definiciones distintas; usar 7d_view/28d_view en código (devuelve vacío); juzgar Incremental por el número de conversiones reportadas.

## Errores frecuentes

1. Pensar que "click" en Meta = clic de enlace antes de marzo de 2026 (incluía likes/shares). [OUTDATED]
2. Asumir que las compras se fechan en el día de la impresión. [OUTDATED para offsite]
3. Pipelines de BI que siguen pidiendo `7d_view` y muestran ceros desde enero de 2026.
4. Cambiar de 7d click a 1d click "para que cuadre con GA4" sin entender que cambia la optimización.

## Preguntas abiertas

- Texto oficial del Help Center sobre el default exacto post-marzo-2026 y la ventana de engage-through (fuentes secundarias concordantes, no verificado en Help Center por bloqueo de descarga).
- Metodología concreta de Incremental attribution (¿PIE? ¿entrenado con Conversion Lift?).
- Disponibilidad general (no beta) de Custom Attribution.

## Fuentes clave

- [Simplifying Ad Measurement for a Social-First World](https://www.facebook.com/business/news/click-attribution) — 2026-03-03 — meta-oficial (S04-003)
- [Ads Insights API Metric Availability Updates](https://developers.facebook.com/blog/post/2025/10/16/ads-insights-api-metric-availability-updates/) — 2025-10-16 — meta-developers (S04-001)
- [Insights API best practices — discrepancy with Ads Manager](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/best-practices) — vigente — meta-developers (S04-050)
- [2025 Out-of-cycle changes](https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2025) — 2025 — meta-developers (S04-048)
- [AppendAttribution integration guide](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/append-attribution) — 2026 — meta-developers (S04-052)
- [Haus: IA vs standard (2026)](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — vendor (S04-022)
- [Social Media Today: incremental attribution](https://www.socialmediatoday.com/news/meta-updates-information-incremental-attribution-conversion-tracking/) — 2025-09-03 — prensa (S04-018)
- [Dataslayer: engage-through](https://www.dataslayer.ai/blog/meta-attribution-change-2026-what-engage-through-attribution-is-and-why-your-numbers-look-different) — 2026-03 — vendor (S04-004)
- [PIE for Ad Measurement](https://pubsonline.informs.org/doi/10.1287/mnsc.2023.01108) — 2023–2026 — academico (S04-077)
