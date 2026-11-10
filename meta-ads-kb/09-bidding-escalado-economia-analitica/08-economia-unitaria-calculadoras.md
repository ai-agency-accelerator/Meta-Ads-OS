# Economía unitaria y calculadoras: ¿cuánto puedo pagar por un lead, una llamada o una venta?

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: margen de contribución, break-even CPA/ROAS/MER, target CPA, LTV y payback, incrementalidad, lead gen high-ticket (CPL, CPQL, booked call, show, venta). Fórmulas + ejemplos trabajados verificados con python.

## TL;DR

- **Todo parte del margen de contribución por conversión (antes de publicidad)**: ingreso neto (sin IVA, menos devoluciones/impagos) − costes variables (producto, envío, pasarela, comisiones, fulfilment). Ese número es tu **CPA break-even**. **[STRONG INFERENCE]** (contabilidad estándar)
- **ROAS break-even = 1 / margen de contribución %** (40 % → 2,5; 25 % → 4,0). Un ROAS goal de 1,0 en Meta es break-even de *ingresos*, no de negocio. **[STRONG INFERENCE]** + **[OFFICIAL META]** (escala del ROAS goal)
- **CPL máximo = P(venta | lead) × contribución por venta × (1 − margen objetivo)**; equivalentemente, se encadena por etapas: CPL = coste/booked call × tasa de booking = coste/show × show rate × booking… **[STRONG INFERENCE]**
- **Ejemplo high-ticket** (5.000 $, contribución 3.015 $/venta, lead→booking 30 %, show 70 %, close 20 %): break-even **CPL ≈ 127 $**, **booked call ≈ 422 $**, **show ≈ 603 $**. Para dejar el 50 % de la contribución como beneficio: CPL objetivo ≈ 63 $. Si el show rate cae a 55 %, el CPL break-even cae a ≈ 100 $. **[STRONG INFERENCE]**
- **Ejemplo ecommerce** (AOV 80 € sin IVA, CM1 ≈ 39 €/pedido = 49 %): CPA break-even ≈ 39 €, ROAS break-even ≈ 2,04 sobre neto, **pero ≈ 2,46 si Meta recibe el valor con IVA**. Valor enviado a Meta y break-even deben estar en la misma base. **[STRONG INFERENCE]**
- **Tres capas de "ROAS"**: plataforma (atribuido por Meta) → incremental (ajustado por lift; Haus: Meta infra-reporta ~15 % en click-only de media, pero Advantage+ sobre-reporta ~12 pp frente a manual) → negocio (MER / margen de contribución total). Decide con la capa más baja que tengas. **[EMPIRICAL]** ([Haus](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))
- **MER = ingresos totales / gasto total en marketing; MER break-even = 1 / CM%** sobre ingresos totales. Sirve de ancla de negocio, pero el MER medio puede ocultar que el último tramo de gasto pierde dinero (ver CPA marginal en [03](03-escalado-tipos-y-condiciones.md)). **[EMPIRICAL]** (CTC/vendors) + **[STRONG INFERENCE]**
- **LTV solo cuenta si es contribución (no ingresos) y si la caja aguanta el payback**. La regla LTV/CAC ≥ 3 es una heurística SaaS; en ecommerce y servicios es más útil fijar **payback máximo** (p. ej., ≤ 3–6 meses) según caja. **[STRONG INFERENCE]**
- **En lead gen high-ticket, el KPI de Meta (CPL) es el menos fiable de la cadena**: decide con coste por llamada cualificada que asiste y coste por venta por cohorte de leads (los cierres llegan semanas después). **[STRONG INFERENCE]**

---

## 1. Definiciones y fórmulas

### 1.1 Margen de contribución por conversión

```
Ingreso neto por pedido   = precio bruto / (1 + IVA) − descuentos
Coste variable por pedido = COGS + envío + picking/packaging + pasarela (% + fijo)
                            + devoluciones esperadas (tasa × pérdida por devolución)
                            + comisiones variables (afiliados, marketplace, closers)
CM1 (antes de ads)        = ingreso neto − coste variable
CM1 %                     = CM1 / ingreso neto
```

### 1.2 Break-even y objetivos

| Métrica | Fórmula | Comentario |
|---|---|---|
| CPA break-even (1.er pedido) | `CM1` | Pagar más = perder dinero en el 1.er pedido |
| ROAS break-even | `ingreso / CM1 = 1 / CM1%` | Usar la misma base de ingreso que el `value` enviado a Meta |
| Target CPA (beneficio p % sobre ventas) | `CM1 − p × ingreso neto` | p = beneficio objetivo tras ads |
| Target ROAS | `ingreso / target CPA` = `1 / (CM1% − p)` | |
| CPA máximo con LTV | `LTV_contribución(h) × (1 − m)` | h = horizonte; m = margen exigido |
| Payback (meses) | mín. t tal que contribución acumulada(t) ≥ CAC | Restricción de caja |
| MER | `ingresos totales / gasto total marketing` | Métrica de negocio, "blended" |
| MER break-even | `1 / CM1%` (sobre ingresos totales) | |
| aMER / nMER | `ingresos de clientes nuevos / gasto` | Aísla adquisición |
| nCAC | `gasto en adquisición / clientes nuevos` | No mezclar recompras |
| Contribución tras marketing | `ingresos × CM1% − gasto marketing` | El número que paga la estructura |
| iROAS | `ROAS plataforma × factor de incrementalidad` | Factor de lift/geo tests |

### 1.3 Lead gen / high-ticket

```
P(venta | lead) = booking_rate × show_rate × close_rate     (× cualificación si aplica)
Contribución por venta = precio × (1 − reembolsos) × (1 − impagos)
                         × (1 − pasarela − comisión closer − setter − fulfilment variable)
BE coste por venta   = contribución por venta
BE coste por show    = contribución × close_rate
BE coste por booking = contribución × close_rate × show_rate
BE CPL               = contribución × close × show × booking
BE CPQL              = BE CPL / % leads cualificados
Objetivo             = BE × (1 − m)      m = parte de la contribución que quieres quedarte
```

## 2. Ejemplo trabajado: ecommerce

Supuestos (ilustrativos): precio con IVA 96,80 € (IVA 21 % → 80,00 € neto), COGS 30 % (24,00 €), envío 7,00 €, picking 1,50 €, pasarela 2,5 % + 0,25 € (2,67 €), devoluciones 8 % de pedidos con reembolso total, coste logístico de devolución 6 € y 70 % del producto revendible.

| Concepto | € por pedido |
|---|---|
| Ingreso neto | 80,00 |
| COGS | −24,00 |
| Envío + picking | −8,50 |
| Pasarela | −2,67 |
| Devoluciones (esperado) | −5,54 |
| **CM1** | **39,29 (49,1 %)** |

- **CPA break-even** = 39,29 €.
- **ROAS break-even** = 80 / 39,29 = **2,04** sobre neto; **2,46** si el `value` enviado a Meta incluye IVA (96,80 / 39,29).
- **Target CPA** con 10 % de beneficio sobre ventas: 39,29 − 8 = **31,29 €** → target ROAS **2,56** (neto).
- **Con LTV**: 1,6 pedidos/cliente en 12 meses → LTV de contribución 12 m ≈ 62,9 €. Con la heurística LTV/CAC = 3 el CAC máximo sería 21 € (más estricto que el break-even del primer pedido: esta heurística no siempre tiene sentido en ecommerce). Con un CAC de 40 € el payback llega en ~1 mes gracias a la recompra. **[STRONG INFERENCE]**
- **Incrementalidad**: ROAS de plataforma 3,0 × factor 0,7 = iROAS 2,1 → apenas por encima del break-even 2,04. Una campaña "con ROAS 3" puede estar en el límite. **[STRONG INFERENCE]**
- **MER**: 500.000 € de ventas / 120.000 € de marketing = 4,17 frente a MER break-even 2,04 → contribución tras marketing ≈ 125.600 €.

### 2.1 Qué valor mandar a Meta

- Enviar **valor neto de IVA y descuentos** (o, mejor, profit si cumples requisitos, ver [02](02-value-optimization-y-value-rules.md)) y calcular el ROAS break-even en esa base. Si se envía bruto, ajustar break-even y objetivos. **[STRONG INFERENCE]**
- Coherencia de ventana: el ROAS objetivo se fija en la ventana de atribución con la que optimizas (7-day click por defecto). **[OFFICIAL META]**

## 3. Ejemplo trabajado: high-ticket (servicio/formación 5.000 $)

Supuestos: reembolsos 8 %, impagos de planes 5 %, pasarela 3 %, comisión closer 10 %, setter 3 %, fulfilment variable 15 %. Funnel: lead→booking 30 %, show 70 %, close 20 %; 60 % de leads cualificados.

| Concepto | Valor |
|---|---|
| Ingreso neto esperado por venta | 5.000 × 0,92 × 0,95 = **4.370 $** |
| Contribución por venta (antes de ads) | 4.370 × (1 − 0,31) = **3.015 $** (60 % del precio) |
| P(venta | lead) | 0,30 × 0,70 × 0,20 = **4,2 %** (≈ 24 leads por venta) |

| Etapa | Break-even | Objetivo (te quedas 50 % de la contribución) | Objetivo (te quedas 67 %) |
|---|---|---|---|
| Coste por venta | 3.015 $ | 1.508 $ | 995 $ |
| Coste por show | 603 $ | 302 $ | 199 $ |
| Coste por booked call | 422 $ | 211 $ | 139 $ |
| **CPL** | **126,6 $** | **63,3 $** | **41,8 $** |
| CPQL (60 % cualificados) | 211 $ | 106 $ | 70 $ |

**Sensibilidad del CPL break-even al funnel** (misma contribución):

| Booking | Show | Close | CPL break-even |
|---|---|---|---|
| 30 % | 70 % | 20 % | 126,6 $ |
| 30 % | 55 % | 20 % | 99,5 $ |
| 30 % | 70 % | 15 % | 95,0 $ |
| 40 % | 60 % | 18 % | 130,3 $ |

Lección: **mejorar show rate o close rate vale tanto como bajar el CPL un 20–25 %**; y un "CPL barato" con peor show/close puede ser más caro por venta. **[STRONG INFERENCE]**

**Versión de caja** (cash collected a 30 días): si se cobra el 60 % por adelantado (menos pasarela) y las comisiones se pagan al cierre sobre el total, la caja neta a 30 días ≈ 2.260 $/venta → **CPL máximo para recuperar caja en 30 días ≈ 95 $**. Útil cuando la restricción es la tesorería, no el beneficio. **[STRONG INFERENCE]**

Benchmarks externos (solo como referencia, metodología débil): no-show ≈ 25 % en una muestra de 273 empresas high-ticket (show ≈ 75 %), estable 2023-2026; close rate de leads cualificados en llamada ≈ 25,7 % para tickets 500–10.000 $ (Focus Digital 2025). **[EMPIRICAL]** baja confianza ([Instarecruiter](https://instarecruiter.notion.site/The-State-of-High-Ticket-Sales-Recruiting-A-Market-Intelligence-Report-317e7975a432809da7c5e0e81495cb58), [Focus Digital](https://focus-digital.co/average-sales-call-conversion-rate-by-industry/)). **Usa siempre tus tasas reales de CRM.**

## 4. "¿Cuánto puedo pagar por lead?" — procedimiento

1. Calcula la **contribución por venta** con datos reales (precio cobrado, reembolsos, impagos, comisiones, fulfilment).
2. Calcula las tasas por etapa con **cohortes de leads** (leads creados en la semana X → cuántos reservaron, asistieron y compraron a 30/60/90 días). No mezcles leads de este mes con ventas de este mes.
3. BE CPL = contribución × P(venta | lead).
4. Elige la política: break-even (crecimiento agresivo), objetivo con margen, o restricción de caja/payback.
5. Si hay segmentos con tasas distintas (edad, país, placement, formulario vs web), calcula BE CPL por segmento → value rules o valores por lead (ver [02](02-value-optimization-y-value-rules.md)).
6. Revisa con intervalos de confianza: con 10 ventas, el close rate estimado es muy incierto (ver [12](12-razonamiento-estadistico.md)).

## 5. LTV, payback y política de CAC

- **LTV de contribución** (no de ingresos): `Σ contribución esperada por cliente en horizonte h`, idealmente por cohorte de adquisición y canal.
- **Horizonte**: el que tu caja pueda financiar. Política habitual: CAC ≤ contribución del 1.er pedido (payback inmediato) para marcas sin caja; CAC ≤ LTV 90/180 días para marcas con recompra probada y caja. **[STRONG INFERENCE]**
- **pLTV en Meta**: si la contribución a 12 meses varía mucho por cliente y no la predice el primer pedido, enviar pLTV (requisitos en [02](02-value-optimization-y-value-rules.md)). **[OFFICIAL META]**
- **Clientes nuevos vs recurrentes**: el ROAS de Meta incluye recompras de clientes existentes (Meta gasta 10–40 % en remarketing sin pedirlo). Para adquisición, usar nCAC/aMER o el breakdown de audience segments. **[EMPIRICAL]** (Loomer)

## 6. Incrementalidad en la economía

- Haus (640 tests, 2024-2025, anunciante medio 14 M$/año en Meta): Meta generó de media ~19 % de lift en el KPI principal; con atribución click-only, Meta **infra-reporta** ~15 % su incrementalidad; para marcas omnicanal, ~32 % del impacto de Meta va a ventas no-DTC (Amazon/retail) → iROAS DTC break-even podría ser 0,68× del que crees. **[EMPIRICAL]**
- Stella (63 tests geo de Meta, ago-2024→dic-2025): iROAS mediano 2,92× (IQR 2,25–3,30), con sesgo de muestra (usuarios sofisticados; recomiendan descontar 15–20 %). **[EMPIRICAL]** ([Stella](https://www.stellaheystella.com/blog/2025-dtc-digital-advertising-incrementality-benchmarks))
- Uso práctico: `objetivo de ROAS en plataforma = ROAS break-even / factor de incrementalidad`. Con BE 2,04 y factor 0,7 → necesitas ROAS de plataforma ≥ 2,9. **[STRONG INFERENCE]** (el detalle de medición está en el área 04).

## 7. Plantilla de calculadora (columnas)

| Entrada | Ejemplo |
|---|---|
| Precio bruto, IVA, descuento medio | 96,80 €, 21 %, 0 % |
| COGS %, envío, picking, pasarela (%/fijo) | 30 %, 7 €, 1,5 €, 2,5 %/0,25 € |
| Tasa devolución, pérdida por devolución | 8 %, (neto − 70 % COGS + 6 €) |
| Pedidos/cliente 12 m | 1,6 |
| Factor de incrementalidad Meta | 0,7 |
| Beneficio objetivo | 10 % |
| **Salidas** | CM1, CM1 %, BE CPA, BE ROAS (neto/bruto), target CPA/ROAS, LTV12, payback, ROAS plataforma necesario |

Para high-ticket: precio, % reembolso, % impago, % pasarela, % comisiones, % fulfilment, booking/show/close/cualificación, % cobro adelantado → contribución, BE por etapa, objetivos por política, CPL de caja a 30 días.

## Implicaciones operativas

- Todo objetivo de puja ([01](01-estrategias-de-puja.md)) y todo umbral de escalado ([03](03-escalado-tipos-y-condiciones.md)) se deriva de estas cifras; revisarlas trimestralmente (COGS, devoluciones, comisiones cambian).
- En high-ticket, reportar **coste por show y por venta por cohorte** semanalmente; el CPL solo como indicador adelantado.
- Alinear la base del `value` enviado a Meta (neto/bruto/profit) con el break-even.
- Ajustar por incrementalidad cuando haya datos de lift.

## Errores frecuentes

1. Break-even ROAS calculado con margen bruto de producto (ignorando envío, pasarela, devoluciones).
2. ROAS con IVA comparado con break-even sin IVA.
3. Usar LTV de ingresos en lugar de LTV de contribución.
4. Juzgar CPL sin show/close rate; "leads baratos" que no asisten.
5. Mezclar periodos: ventas de este mes / leads de este mes en ciclos de 30–60 días.
6. Escalar con MER medio sano mientras el tramo marginal pierde dinero.
7. Considerar ROAS de plataforma = ROAS incremental.

## Preguntas abiertas

- Factores de incrementalidad por tipo de campaña/vertical con muestras amplias y metodología publicada (Haus y Stella son los mejores disponibles).
- Benchmarks fiables de show/close rate por vertical y ticket (los públicos tienen metodología pobre).

## Fuentes clave

- [The Meta Report: 640 Haus incrementality experiments](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
- [2025 DTC Digital Advertising Incrementality Benchmarks](https://www.stellaheystella.com/blog/2025-dtc-digital-advertising-incrementality-benchmarks) — Stella, 2026-05-26 — vendor
- [About ROAS goal](https://www.facebook.com/business/help/1113453135474912), [Best practices ROAS goal](https://www.facebook.com/business/help/288309751798466) — Meta — meta-oficial
- [MER (Marketing Efficiency Ratio)](https://www.polaranalytics.com/post/mer-marketing-efficiency-ratio) — Polar Analytics — vendor
- [ROAS vs contribution margin](https://eightx.co/blog/roas-vs-contribution-margin) — Eightx — agencia
- [Average sales call conversion rate by industry](https://focus-digital.co/average-sales-call-conversion-rate-by-industry/) — Focus Digital, 2025 — agencia (baja confianza)
- [State of High-Ticket Sales Recruiting](https://instarecruiter.notion.site/The-State-of-High-Ticket-Sales-Recruiting-A-Market-Intelligence-Report-317e7975a432809da7c5e0e81495cb58) — Instarecruiter, 2026-03 — vendor (baja confianza)
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07 — practitioner
