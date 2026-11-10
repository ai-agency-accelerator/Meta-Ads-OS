# Cuándo NO tocar una campaña: reglas de paciencia según volumen y attribution lag

> Última verificación: 2026-10-16 · Autor: A09 (agente) · Ámbito: por qué las decisiones con 24 h de datos son casi siempre ruido; retraso de atribución; learning; reglas de espera por volumen de eventos; excepciones (cuándo sí actuar ya).

## TL;DR

- **Posición oficial de Meta**: analizar "al menos una semana completa"; en goal-based, "wait at least 7 days after any adjustment before re-evaluating" y usar medias semanales; esperar a salir de learning para editar; "only edit… when you have reason to believe that the edit should improve performance". **[OFFICIAL META]** ([Understand fluctuations](https://www.facebook.com/business/help/1364841787225722), [About CPR goal](https://www.facebook.com/business/help/272336376749096), [Learning phase](https://www.facebook.com/business/help/112167992830700))
- **Los últimos días siempre se ven peor de lo que son**: Ads Manager imputa la conversión a la fecha de la impresión/clic (la API lo controla con `action_report_time` = impression/conversion/mixed), y con 7-day click las conversiones siguen llegando hasta 7 días después. **[OFFICIAL META]** (parámetro API) + **[EMPIRICAL]** (comportamiento por defecto según Loomer)
- **El tamaño del retraso depende del ciclo de compra**: en un ejemplo de Loomer solo ~1,4 % de las conversiones 7d click llegaron después del día 1; en compras consideradas puede ser un 20–35 %+. **Mídelo en tu cuenta** (columna 1d click vs 7d click, o breakdown por ventana). **[EMPIRICAL]**
- **Con <30 conversiones, el CPA de un día o de una unidad pequeña es casi puro ruido** (IC del CPA de 0,7× a 1,5× con 30 conversiones; de 0,5× a 2,1× con 10). **[STRONG INFERENCE]** (ver [12](12-razonamiento-estadistico.md))
- **Regla de paciencia**: no evaluar un cambio hasta cumplir **las tres**: (1) ≥7 días completos desde el cambio, (2) ≥30–50 eventos de optimización desde el cambio, (3) la ventana de atribución madurada para los días evaluados. Lo que llegue antes, se espera al resto (con tope práctico de 14–21 días para cuentas de bajo volumen). **[STRONG INFERENCE]**
- **Excepciones (actuar ya)**: rotura de tracking/píxel, gasto desbocado o fuera de límites, anuncios rechazados/riesgo de cuenta, error de configuración (país, URL, oferta, precio), roturas de stock/web, o gasto ≥3–4× el CPA objetivo sin ninguna conversión en un evento frecuente. **[STRONG INFERENCE]**
- **"Nunca toques nada en learning" es CONTEXT-DEPENDENT**: Meta dice que el learning es necesario y que hay que seguir testeando; lo dañino es encadenar ediciones. Si la configuración es errónea, corrígela aunque esté en learning. **[OFFICIAL META]** + **[STRONG INFERENCE]**

---

## 1. Por qué 24 horas no bastan (cuatro fuentes de error)

1. **Ruido de Poisson**: con 20 conversiones/día de media, el 95 % de los días cae entre 12 y 29 (−40 %/+45 %) sin que nada haya cambiado. **[STRONG INFERENCE]**
2. **Atribución tardía**: las conversiones se imputan al día de la impresión/clic; con 7-day click, el día de ayer seguirá sumando conversiones hasta 7 días. Además, eventos de usuarios iOS con opt-out pueden tardar hasta ~72 h en procesarse (fuente vendor). **[EMPIRICAL]**
3. **Pacing intra-semanal**: el presupuesto diario es una media semanal; Meta gasta más algunos días y menos otros (hasta 175 %); un día "caro" puede compensarse con otros. Los goal-based compensan dentro de la semana. **[OFFICIAL META]**
4. **Learning y exploración**: tras un cambio, el sistema explora (entrega "más agresiva"), con costes más altos y menos estables. **[OFFICIAL META]**

## 2. Cuánto esperar: tabla por volumen

| Conversiones de optimización/día (unidad de presupuesto) | Mínimo para evaluar un cambio | Comentario |
|---|---|---|
| ≥ 20 | 7 días completos | n≈140; la limitación es el ciclo semanal y la atribución, no la muestra |
| 7–20 | 7 días | n≈50–140 |
| 3–7 | 10–14 días | n≈30–100; usar ventana 7d click madurada |
| 1–3 | 14–21 días | n≈20–60; considerar subir de evento o consolidar |
| < 1 | No evaluar por CPA; usar evento proxy de mayor volumen o métricas de funnel | Learning limited casi seguro ([04](04-cambios-de-presupuesto-y-duplicacion.md)) |

**[STRONG INFERENCE]** — derivado de: Meta (semanas completas, 7 días tras ajustes, ~50 eventos/semana para estabilidad) y de las tablas de ruido de [12](12-razonamiento-estadistico.md).

### 2.1 Ventana madurada

Si optimizas con 7-day click, un día está "maduro" 7 días después. Para evaluar la semana pasada con precisión, espera a que termine la siguiente; en la práctica:
- Lectura provisional: semana cerrada, ajustando con tu ratio histórico 7d/1d (ver 2.2).
- Lectura definitiva: 7 días después.

### 2.2 Medir tu propio lag (procedimiento)

1. Toma 4–8 semanas estables.
2. Compara resultados con 1-day click vs 7-day click (columnas comparativas o breakdown por ventana de atribución).
3. Ratio de maduración r = conv(7d click) / conv(1d click).
4. Para días recientes: CPA estimado ≈ CPA(1d click) / r.
5. En lead gen high-ticket, haz lo mismo con el CRM: % de ventas de una cohorte de leads a 7/30/60/90 días.

Ejemplo: r = 1,25 → si ayer el CPA 1d click fue 50 $, el CPA 7d click esperado tras maduración ≈ 40 $. **[STRONG INFERENCE]**

## 3. Matriz de decisión "¿toco o no toco?"

| Situación | Acción |
|---|---|
| CPA de ayer +40 % con 15 conversiones | **No tocar**. Dentro de la banda de ruido. |
| CPA de la semana +25 % con 150 conversiones, CPM +20 % y semana de BFCM | **No tocar la estructura**; revisar si el pico compensa (CVR/AOV). |
| CPA de la semana +30 % con 150 conversiones, CTR del anuncio principal −30 % y frecuencia ↑ | **Actuar**: nuevas creatividades (fatiga). |
| 0 eventos Purchase en Events Manager desde hace 6 h en horario de venta | **Actuar ya**: rotura de tracking/web. |
| Gasto de hoy 3× el presupuesto diario | **Revisar ya** (el máximo oficial es 1,75× salvo budget sharing/scheduling). |
| Ad set en learning, configuración correcta, día 3 | **No tocar**. |
| Ad set en learning con país/URL/evento equivocado | **Corregir ya** (el learning sobre un error no sirve). |
| Learning limited persistente | **Actuar estructuralmente** (consolidar, ampliar, subir presupuesto/puja, cambiar evento), no micro-ediciones. **[OFFICIAL META]** |
| Nuevo anuncio con 2× CPA objetivo gastado y 0 conversiones (evento frecuente) | Probabilidad de 0 conversiones si su CPA real fuera el objetivo: e^−2 ≈ 14 %. Esperar a ~3× (≈5 %). |
| CPR goal cambiado hace 3 días | **No tocar**: Meta pide ≥7 días. |

## 4. Mitos y veredictos

| Afirmación | Veredicto |
|---|---|
| "No toques nada durante el learning" | **CONTEXT-DEPENDENT** — no hagas ediciones evitables; sí corrige errores. Meta: el learning "no debe evitarse por completo" porque testear es esencial. |
| "Si un día va mal, baja presupuesto" | **FALSE** como regla — un día es ruido + atribución incompleta. |
| "Hay que revisar la cuenta 3 veces al día" | **CONTEXT-DEPENDENT** — revisar sí (salud, roturas); **decidir** sobre rendimiento, no. |
| "Si funciona, no lo toques" (Loomer) | **TRUE** en lo esencial — las ediciones tienen coste; pero escalar un ganador también es "tocarlo" y es necesario (ver [03](03-escalado-tipos-y-condiciones.md)). |
| "Evalúa siempre a los 3 días" | **UNPROVEN** — depende del volumen y del lag; con <5 conv/día, 3 días no informan. |

## 5. Disciplina operativa

1. **Ventanas de edición fijas** (p. ej., martes): todas las decisiones de rendimiento se toman ahí, agrupadas. **[STRONG INFERENCE]**
2. **Toda edición con hipótesis y fecha de evaluación** en el change log ([10](10-dashboards-reporting.md)).
3. **Revisión diaria = salud**, con bandas de control ([12](12-razonamiento-estadistico.md)).
4. **Una palanca por vez** en la misma unidad, salvo cambios agrupados intencionadamente.
5. **Evitar cambios tarde en el día** (Meta: pueden no aplicarse a tiempo). **[OFFICIAL META]**

## Implicaciones operativas

- Política escrita de "tiempo mínimo para evaluar" por cuenta según su volumen (tabla 2).
- Mostrar en dashboards el estado de maduración de cada día (provisional/definitivo).
- Alertas automáticas solo para roturas, no para oscilaciones de CPA.

## Errores frecuentes

1. Leer el CPA de ayer a primera hora de la mañana como definitivo.
2. Encadenar cambios cada 2 días y no saber cuál funcionó.
3. Pausar anuncios nuevos tras 1× CPA sin conversión.
4. Confundir "estar en learning" con "estar roto".
5. No ajustar por estacionalidad al comparar la semana con la anterior.

## Preguntas abiertas

- Meta no publica la latencia típica de reporting; la estimación de ~72 h para ciertos eventos iOS viene de vendors.
- Confirmación oficial actual del modo de imputación por defecto en Ads Manager (impresión vs conversión): solo verificado el parámetro API `action_report_time`.

## Fuentes clave

- [Understand fluctuations in ad performance](https://www.facebook.com/business/help/1364841787225722) — Meta — meta-oficial
- [About the learning phase](https://www.facebook.com/business/help/112167992830700) — Meta — meta-oficial
- [About cost per result goal](https://www.facebook.com/business/help/272336376749096) — Meta — meta-oficial
- [Ad Account Insights (action_report_time)](https://developers.facebook.com/docs/graph-api/reference/adaccount/insights/) — Meta Developers — meta-developers
- [Which ad gets credit for a conversion](https://www.jonloomer.com/qvt/which-ad-gets-credit-for-a-conversion/) — Jon Loomer — practitioner
- [Compare attribution settings](https://www.jonloomer.com/compare-attribution-settings-get-the-most-of-meta-conversion-data/) — Jon Loomer — practitioner
- [Do not touch a Facebook ad that's working](https://www.jonloomer.com/do-not-touch-a-facebook-ad-thats-working/) — Jon Loomer — practitioner
- [How long until conversions show up](https://weltpixel.com/blogs/news/how-long-until-conversions-show-up-reporting-delays-by-platform) — WeltPixel — vendor
