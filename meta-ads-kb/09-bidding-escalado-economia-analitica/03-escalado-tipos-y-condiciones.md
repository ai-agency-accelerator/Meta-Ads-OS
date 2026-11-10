# Escalado: tipos, condiciones previas, rendimientos decrecientes y señales de fallo

> Última verificación: 2026-10-15 · Autor: A09 (agente) · Ámbito: escalado vertical, horizontal, creativo, geográfico, de oferta, audiencia, placements y presupuesto; curva de respuesta; CPA marginal vs medio; señales de que el escalado falla. Cambios de presupuesto concretos y duplicación: ver [04](04-cambios-de-presupuesto-y-duplicacion.md).

## TL;DR

- **Escalar = comprar conversiones marginales más caras.** Meta lo dice explícitamente: el sistema toma primero las oportunidades más baratas y, al agotarse, pasa a otras más caras; los costes suben a lo largo del calendario y con más presupuesto. **[OFFICIAL META]** ([Understand fluctuations](https://www.facebook.com/business/help/1364841787225722))
- **La decisión correcta se toma con el CPA (o ROAS) marginal, no con el medio.** Con una curva de respuesta típica (conversiones ∝ gasto^b, b≈0,6–0,8), **CPA marginal ≈ CPA medio / b**: con b=0,7, cada conversión extra cuesta ~1,4× el CPA medio. Escalar hasta que el CPA *medio* toque el break-even destruye casi todo el beneficio. **[STRONG INFERENCE]** (matemática estándar; b varía por cuenta y se estima con tus datos)
- **El beneficio máximo está donde CPA marginal = margen de contribución por conversión (CPA break-even), con un CPA medio claramente inferior** (en el ejemplo: CPA medio 25 $ vs break-even 36 $). **[STRONG INFERENCE]**
- **En la era Andromeda (retrieval desde dic-2024), la palanca principal de escala es la diversidad creativa, no la segmentación**: Meta afirma que la diversificación creativa es la mejor forma de encontrar audiencias relevantes; los anunciantes que más gastan lanzan 3–7× más creatividades/semana que los pequeños. **[OFFICIAL META]** + **[EMPIRICAL]** ([Meta Engineering](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/), [Motion 2026](https://motionapp.com/library/research/creative-benchmarks-2026/))
- **Escalado horizontal por fragmentación (más ad sets con audiencias solapadas) es contraproducente**: Meta solo deja competir a tu anuncio de mayor valor en cada subasta (auction overlap) y recomienda combinar ad sets; "too much auction overlap… less predictable performance – especially when scaling your budget". **[OFFICIAL META]** ([Auction overlap](https://www.facebook.com/business/help/537699989762051))
- **Horizontal sí funciona cuando abre inventario nuevo de verdad**: nuevo país/idioma, nueva oferta/producto, nuevo ángulo creativo dirigido a otro segmento de demanda, nuevo evento de optimización. **[STRONG INFERENCE]**
- **Condiciones mínimas antes de escalar presupuesto**: ≥2 semanas estables, ≥50 conversiones/semana en el ad set/campaña, CPA marginal estimado < break-even, pipeline creativo que aguante, tracking verificado y capacidad operativa (stock, equipo comercial). Para goal-based, Meta pide ≥3 semanas antes de escalar. **[OFFICIAL META]** (3 semanas en goal-based) + **[STRONG INFERENCE]** (resto)
- **Señales de que el escalado está fallando** (en semanas completas): CPA marginal > break-even; CPM↑ con frecuencia↑ y alcance plano; % nuevos clientes↓; MER/margen de contribución total plano o a la baja pese a más gasto; calidad de lead↓ (show/close rate). **[STRONG INFERENCE]**
- **Advantage+ vs manual a nivel incremental: no hay ganador universal.** Haus (640 tests, 2024-2025): Advantage+ con ROAS de plataforma +2,4 % pero iROAS −12 % frente a manual, y 58 % de marcas con mejor iROAS en manual. **[EMPIRICAL]** ([Haus](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))

---

## 1. Primeros principios: la curva de respuesta

### 1.1 Por qué el coste sube al escalar

1. **Agotamiento de oportunidades baratas**: el sistema "seeks the highest volume opportunities first"; más presupuesto obliga a entrar en subastas con mayor precio o menor probabilidad de conversión. **[OFFICIAL META]**
2. **Audiencia y frecuencia**: dentro de una audiencia finita, más gasto = más impresiones por persona; las impresiones repetidas tienen menor probabilidad marginal de convertir. **[STRONG INFERENCE]**
3. **Incrementalidad decreciente**: al escalar se alcanza a más gente que habría comprado igualmente (retargeting implícito, clientes existentes). Haus describe casos de iROAS que cae de 2,5 a 1,2 al aumentar el gasto (canal no especificado). **[EMPIRICAL]** ([Haus](https://www.haus.io/article/measuring-iroas-is-it-worth-it))
4. **Learning**: cambios grandes reabren exploración (ver [04](04-cambios-de-presupuesto-y-duplicacion.md)).

### 1.2 Modelo útil

Modelo de potencia (equivalente local a una curva Hill/saturación como la de Robyn):

```
Conversiones(S) = a · S^b      con 0 < b < 1  (b = elasticidad gasto→conversiones)
CPA_medio(S)    = S / C(S)
CPA_marginal(S) = dS/dC = CPA_medio(S) / b
Estimar b con dos niveles de gasto estables:  b = ln(C2/C1) / ln(S2/S1)
CPA marginal de un incremento discreto = (S2 − S1) / (C2 − C1)
```

**[STRONG INFERENCE]** — derivación estándar; Robyn (Meta) modela saturación con una función Hill y define la respuesta marginal como su primera derivada. Recast: la ROI media es para reporting; la marginal es para decidir presupuesto. ([Recast, ago-2025](https://getrecast.com/average-vs-marginal-roi-in-mmm-when-to-use-each-and-why-both-matter-for-your-budget/))

### 1.3 Ejemplo trabajado (verificado con python)

Ecommerce: margen de contribución por pedido (antes de ads) = **36 $** (= CPA break-even). Hoy: 1.000 $/día → 50 compras/día (CPA 20 $). Supongamos b = 0,7.

| Gasto/día | Compras/día | CPA medio | CPA marginal (punto) | Beneficio/día (36·C − S) |
|---|---|---|---|---|
| 1.000 | 50,0 | 20,00 | 28,57 | 800 |
| 1.500 | 66,4 | 22,59 | 32,27 | 890 |
| 2.000 | 81,2 | 24,62 | 35,18 | 924 |
| **2.161** | **85,7** | **25,20** | **36,00** | **926 (máximo)** |
| 4.000 | 134 | 30,31 | 43,3 | 750 |
| 6.000 | 175 | 34,24 | 48,9 | 309 |

Lecturas:
- El paso de 1.000 → 1.500 $ trae 16,4 compras extra a **30,47 $** cada una (no a 22,59 $).
- El óptimo de beneficio está a ~2.160 $/día con CPA medio **25 $**, muy por debajo del break-even de 36 $.
- Un equipo que escala "mientras el CPA medio esté por debajo de 36 $" llega a ~6.000 $/día y gana **un tercio** de lo que ganaba a 2.160 $.
- Si el objetivo es **crecimiento** (cuota, LTV, caja), se puede elegir operar por encima del óptimo de beneficio inmediato, pero de forma explícita, con el CPA marginal como métrica de coste del crecimiento. **[STRONG INFERENCE]**

### 1.4 Cómo estimar el marginal en la práctica

1. **Escalones de presupuesto** sostenidos ≥7 días cada uno (mismo setup), comparando semanas completas: CPA marginal = Δgasto / Δconversiones. Ruido: con pocas conversiones el Δ es muy incierto (ver [12](12-razonamiento-estadistico.md)).
2. **Test geo de dosis** (0×/1×/2× gasto por regiones) — es la recomendación de Haus para medir saturación con incrementalidad. **[EMPIRICAL]** ([Haus](https://www.haus.io/article/measuring-iroas-is-it-worth-it))
3. **MMM** (Robyn/Meridian/Recast) para curvas por canal; requiere variación de gasto (≥4–5 niveles distintos según vendors). **[EMPIRICAL]**
4. A nivel **negocio**: margen de contribución total vs gasto total por semana (cohortes de gasto). CTC argumenta que el aMER/MER medio puede ocultar que el gasto por encima de cierto nivel pierde dinero. **[EMPIRICAL]**

## 2. Tipos de escalado

| Tipo | Qué es | Abre inventario nuevo | Riesgo principal | Cuándo |
|---|---|---|---|---|
| **Vertical / presupuesto** | Subir presupuesto a la campaña/ad set existente | No (profundiza en el mismo) | CPA marginal creciente; learning si salto grande | Primer recurso cuando CPA marginal < break-even |
| **Creativo** | Más conceptos/ángulos/formatos | **Sí** (Andromeda recupera candidatos por anuncio) | Coste de producción; dilución si se lanzan demasiados a la vez | Siempre; es el motor de escala 2025-2026 |
| **Horizontal estructural** | Nuevas campañas/ad sets | Solo si cambia algo real (geo, oferta, evento) | Auction overlap, fragmentación, learning múltiple | Cuando hay una razón de negocio distinta |
| **Geográfico** | Nuevos países/regiones/idiomas | Sí | CPM/CVR distintos; logística; localización | Unit economics validadas por país |
| **Oferta** | Nuevos productos, bundles, precios, lead magnets, garantías | Sí (nueva demanda) | Margen; canibalización | Cuando la creatividad sola satura |
| **Audiencia** | Ampliar (broad/Advantage+ audience), quitar exclusiones | Parcial | Calidad media menor | Si la audiencia es la restricción (raro en 2026) |
| **Placements** | Advantage+ placements, Reels, Threads, WhatsApp Status | Sí (inventario más barato) | Calidad de conversión desigual | Casi siempre; controlar con value rules |
| **Evento de optimización** | Subir/bajar en el embudo (p. ej., Purchase → value; lead → conversion leads) | Cambia a quién se compra | Volumen vs calidad | Cuando el volumen o la calidad limitan |

### 2.1 Vertical (presupuesto)

- Detalles de magnitud, learning y Advantage+ campaign budget en [04](04-cambios-de-presupuesto-y-duplicacion.md).
- Para goal-based, Meta: correr ≥3 semanas antes de escalar, subir presupuesto gradualmente y **cambiar pujas solo tras una semana**; con CPR/ROAS goal la escala puede venir de **relajar el objetivo** más que de subir presupuesto (si está bid-constrained). **[OFFICIAL META]** ([CPR goal best practices](https://www.facebook.com/business/help/176339196621566))
- Loomer: Meta es "mucho más tolerante" con subidas de presupuesto que antes; espera costes más altos al escalar. **[EMPIRICAL]**

### 2.2 Creativo (el motor real en 2025-2026)

- **Andromeda** (Meta Engineering, 2-dic-2024): sistema de retrieval que selecciona de decenas de millones de anuncios unos pocos miles de candidatos para cada oportunidad; índice jerárquico pensado para "un gran volumen de creatividades"; +6 % recall y +8 % calidad de anuncios en segmentos seleccionados. **[OFFICIAL META]** ([Meta Engineering](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/))
- Implicación: **cada concepto creativo distinto es una "puerta" a un conjunto de personas distinto**. Variaciones mínimas (mismo concepto, otro color) tienden a agruparse; la afirmación de un "umbral de similitud del 60 %" circula en blogs **sin fuente de Meta** → **[UNPROVEN]**.
- **Datos Motion 2026** (550k+ anuncios, ~1,3 B$, 6.000+ cuentas, sep-2025→ene-2026): **[EMPIRICAL]** ([Motion](https://motionapp.com/library/research/creative-benchmarks-2026/), [resumen Sepia Lab](https://sepia-lab.com/en/blog/ad-creative-volume-benchmarks))

| Gasto mensual | Nuevas creatividades/semana (media) | Top 25 % |
|---|---|---|
| <10k $ | 2,80 | 4,83 |
| 10–50k $ | 4,10 | 8,09 |
| 50–200k $ | 6,67 | 15,95 |
| 200k–1M $ | 11,24 | 31,11 |
| >1M $ | 18,85 | 54,64 |

  - Hit rate (anuncio que gasta ≥10× la mediana de gasto por anuncio de la cuenta): ~5 % global, ~4 % en cuentas pequeñas → 8–9 % en enterprise. Con 20 anuncios esperas ~1–1,6 ganadores; con 50, ~2,5–4.
  - ~6 % de los anuncios concentran la mayor parte del gasto; ~50 % no reciben gasto relevante.
  - Ojo: "ganador" = acapara gasto, **no** ROAS/beneficio probado.
- Regla operativa (Loomer, jul-2026): no lanzar 20–50 anuncios a la vez en un ad set; Meta concentrará el gasto en unos pocos igualmente; que un anuncio se lleve ~50 % del gasto es normal. **[EMPIRICAL]**
- Ratio net-new vs iteración: Barry Hott propone 90/10 (heurística). **[HYPOTHESIS]**
- **Creative diversity score (desde ~26-ago-2026)**: columna en Ads Manager que califica cada ad set como Low/Medium/High según lo distintas que son sus imágenes/miniaturas de vídeo; Meta la etiqueta "estimated and in development" y no ha publicado el método ni si afecta a la entrega. CTC recomienda priorizar ad sets "Low" de mayor gasto y crear ≥4 "familias" creativas distintas antes de Q4; varios anunciantes reportan "Low" incluso con mezcla de formatos. Úsalo como indicador direccional, no como KPI. **[EMPIRICAL]** (existencia y etiqueta) / **[HYPOTHESIS]** (efecto en entrega) ([CTC, 9-sep-2026](https://commonthreadco.com/blogs/coachs-corner/metas-new-creative-diversity-score-is-live-in-ads-manager-what-ecommerce-brands-must-act-on-now))

### 2.3 Horizontal estructural

- Meta: combinar ad sets similares reduce tiempo en learning, mejora eficiencia y evita fragmentar la audiencia; usar **breakdowns** en vez de ad sets para ver segmentos. **[OFFICIAL META]** ([Combine ad sets](https://www.facebook.com/business/help/2419480091640105))
- Razones legítimas para separar (Loomer, jul-2026): objetivos de negocio distintos, productos/ubicaciones con mensajes distintos, estacionalidad; cada unidad debe tener presupuesto suficiente. **[EMPIRICAL]**
- Con Advantage+ campaign budget, los ad sets con audiencias más grandes recibirán más presupuesto; no pausar ad sets de baja entrega (impide encontrar oportunidades de mañana). **[OFFICIAL META]** ([A+CB best practices](https://www.facebook.com/business/help/2177212182495139))

### 2.4 Geográfico

- Abre inventario nuevo, pero cambia todo el funnel: CPM, CVR, AOV, devoluciones, logística, idioma.
- Regla: **validar unit economics por país** (break-even CPA por país con su AOV/margen/envío) antes de mezclar países en una misma campaña; en una campaña multipaís, Meta irá hacia los países con conversiones más baratas, que pueden no ser los más rentables (usar value rules por ubicación si el valor difiere). **[STRONG INFERENCE]** + value rules por ubicación **[OFFICIAL META]**.
- El precio por anuncio varía mucho por región: en Q2-2026 Meta reportó +20 % interanual en EE. UU./Canadá vs +1 % en Asia-Pacífico (dato de earnings por región, vía recopilación). **[OFFICIAL META]** vía [Adwize](https://adwize.ai/meta-ad-price-history)

### 2.5 Oferta

- Cuando creatividad y presupuesto saturan, la oferta (bundle, garantía, precio de entrada, lead magnet, trial) cambia la **tasa de conversión** de toda la curva → desplaza la curva entera hacia arriba (mejor que moverse por ella). **[STRONG INFERENCE]**
- Medir siempre el impacto en margen de contribución y LTV, no solo en CPA.

### 2.6 Audiencia y placements

- En 2026 la audiencia rara vez es la restricción (Advantage+ audience/broad). Si una audiencia restringida limita, ampliar es la palanca oficial contra learning limited. **[OFFICIAL META]**
- Advantage+ placements: Meta comunica en su Help Center (oct-2026) un experimento con **−10 % de coste por resultado medio** frente a placements manuales (PPC Land citaba −11,7 % en una versión anterior); sin muestra ni fechas publicadas. **[OFFICIAL META]** (afirmación) / metodología no verificable. ([What's new in placement settings](https://www.facebook.com/business/help/1546753450586085))
- **Oct-2026**: en Sales/Leads/App promotion (Engagement no; corrección 2026-11-09) ya no se eligen placements a nivel ad set (despliegue gradual); el control pasa a value rules por placement y exclusiones de cuenta por objetivo. El escalado por placements queda, en la práctica, en manos de Meta + creatividad adaptada por placement. **[OFFICIAL META]**
- Reels: inventario creciente y más barato; Tinuiti Q4-2025: Reels = 29 % de impresiones de anuncios en Instagram (18 % un año antes). **[EMPIRICAL]** ([Tinuiti Q4 2025](https://tinuiti.com/research-insights/research/digital-ads-benchmark-report-q4-2025/))

## 3. Condiciones necesarias antes de escalar (checklist)

| # | Condición | Umbral | Etiqueta |
|---|---|---|---|
| 1 | Estabilidad | ≥2 semanas completas sin significant edits; para goal-based ≥3 semanas | [OFFICIAL META] (3 semanas goal-based) / [STRONG INFERENCE] |
| 2 | Volumen | ≥50 conversiones/semana en la unidad que escalas (ad set o campaña A+CB) | [OFFICIAL META] |
| 3 | Economía | CPA marginal estimado < CPA break-even (o ROAS marginal > break-even ROAS) | [STRONG INFERENCE] |
| 4 | Medición | Tracking verificado (CAPI + pixel, deduplicación), atribución coherente; idealmente un dato de incrementalidad | [STRONG INFERENCE] |
| 5 | Creatividad | Pipeline de nuevas creatividades acorde al tramo de gasto (tabla Motion) | [EMPIRICAL] |
| 6 | Capacidad operativa | Stock, fulfilment, equipo de ventas/setters, capacidad de agenda | [STRONG INFERENCE] |
| 7 | Caja | Payback compatible con el ciclo de caja (ver [08](08-economia-unitaria-calculadoras.md)) | [STRONG INFERENCE] |
| 8 | Estacionalidad | No interpretar una semana de CVR estacional alto como "ganador escalable" | [STRONG INFERENCE] |

### 3.1 Un marco de practitioner con umbrales: Foxwell (2026)

Andrew Foxwell (Foxwell Digital, oct-2026) parte de que "your CPA is supposed to go up when you scale" y propone revisar **cinco números de negocio** (no el ROAS de plataforma) antes de cada movimiento de presupuesto: **[EMPIRICAL]** (opinión de practitioner con base en cientos de cuentas; umbrales no validados públicamente) ([Foxwell](https://www.foxwelldigital.com/blog/how-to-scale-meta-ads-without-blowing-up-your-cpa))

| Número | "Verde" orientativo |
|---|---|
| Margen de contribución tras ads | >15 % |
| nCAC vs beneficio bruto del primer pedido | nCAC ≤ ~70 % del beneficio bruto del 1.er pedido |
| Beneficio bruto 90 días / CAC | ≥ 2 |
| Payback | ≤ 30 días |
| Mix ingresos nuevos/recurrentes | ~60/40–70/30 (>80 % nuevos = "cubo agujereado"; <35 % = adquisición rota) |

Reglas de ritmo: 5 verdes → +20–30 % de gasto por semana; 4 verdes + 1 amarillo → +10–15 %; ≥2 amarillos → mantener; margen o payback en rojo → parar el escalado. Movimientos típicos de 20–25 % (hasta 25–30 % "agresivo"), no volver a subir en un par de días, y esperar 5–7 días antes de recortar. Presupuestar en euros/dólares de contribución, no en %, y prever CAC creciente. Coherente con el enfoque de CPA marginal de este documento. **[EMPIRICAL]**

Foxwell también argumenta (abr-2026) que el escalado se atasca por **señal pobre** (demasiadas campañas que fragmentan el aprendizaje, cambios creativos demasiado pequeños para que Meta los lea como nuevos, engagement de la audiencia equivocada), no por la escala en sí. **[EMPIRICAL]** ([Foxwell](https://www.foxwelldigital.com/blog/data-density-and-why-your-meta-ads-campaigns-arent-growing))

## 4. Señales de que el escalado está fallando

Evaluar en **semanas completas**, comparando contra la semana previa al cambio y contra la misma semana del año anterior si hay estacionalidad:

1. **CPA marginal del incremento > break-even** (aunque el medio parezca bueno).
2. **Frecuencia↑, alcance↗ plano, CPM↑**: estás profundizando en la misma audiencia. (Ver [07](07-frecuencia.md))
3. **% de nuevos clientes↓** (breakdown de Audience segments en Sales: new / engaged / existing). Loomer observa que Meta gasta típicamente 20–25 % del presupuesto de Sales en remarketing sin pedírselo (rango 10–40 %). **[EMPIRICAL]** ([Master Brief](https://www.jonloomer.com/meta-ads-master-brief/))
4. **MER o margen de contribución total plano** mientras el gasto en Meta sube → el incremento no es incremental (canibaliza orgánico/otros canales). **[STRONG INFERENCE]**
5. **Lead gen**: CPL estable pero show rate/close rate↓ → el sistema está comprando leads más baratos de peor calidad.
6. **Creative concentration**: un solo anuncio >70–80 % del gasto con frecuencia creciente y sin sustitutos → riesgo de caída brusca. **[HYPOTHESIS]** (umbral orientativo)
7. **Learning limited** tras escalar con goal-based (bid-constrained). **[OFFICIAL META]**

## 5. Matices de la era Andromeda / Advantage+ (2025-2026)

- **Consolidación** es consenso (Meta + practitioners). **[OFFICIAL META]**/**[EMPIRICAL]**
- **Advantage+ sales (antes ASC, cambio jun-2025)**: Tinuiti Q4-2025: las campañas Advantage+ sales eran el 27 % del gasto retail en Meta (38 % en Q1-2025). **[EMPIRICAL]**
- **Incrementalidad A+ vs manual** (Haus, 640 tests, publicado jul-2025): A+ ROAS de plataforma +2,4 %, pero iROAS DTC ~12 % inferior (con un 18 % menos de gasto diario); A+ ganaba a mitad del test (+9 %) y perdía al final (−12 %); A+ sobre-reportaba ~12 pp. 58 % de marcas con mejor iROAS en manual. **[EMPIRICAL]** — implica que "escalar lo que más ROAS reporta Ads Manager" no es lo mismo que escalar lo más incremental. **[CONTESTED]**: Haus añadió en jul-2026 una nota de que incremental attribution ya supera a la estándar (revierte otro hallazgo del informe), lo que muestra que estos resultados cambian con el producto.
- Afirmaciones de umbrales de learning más bajos en Advantage+ (25 conversiones; 15 en app) en 2026 provienen de blogs que citan otros blogs; **no hay confirmación oficial** → **[HYPOTHESIS]**. ([AdBeacon, ago-2026](https://www.adbeacon.com/meta-just-lowered-the-advantage-learning-threshold/))

## Implicaciones operativas

- Llevar en el reporting semanal una fila de **"incremento"**: Δgasto, Δconversiones, CPA marginal, vs break-even.
- Escalar presupuesto mientras CPA marginal < break-even (objetivo beneficio) o < CPA máximo de crecimiento aceptado (objetivo crecimiento, fijado por negocio).
- Antes de abrir campañas nuevas, preguntar: ¿abre inventario/demanda nueva o solo fragmenta?
- Dimensionar producción creativa según tramo de gasto; medir hit rate propio.
- Validar periódicamente con incrementalidad (geo/holdout) en la unidad que más escala.

## Errores frecuentes

1. Escalar mirando CPA/ROAS medio del periodo completo en lugar del incremento.
2. Duplicar ad sets "para escalar" con la misma audiencia (overlap).
3. Escalar una semana de pico estacional como si fuera la nueva normalidad.
4. Escalar sin pipeline creativo → fatiga a las 2–3 semanas.
5. Escalar lead gen sin capacidad comercial → caída de show/close rate atribuida erróneamente a "leads malos de Meta".
6. Comparar campañas A+ y manuales solo por ROAS de plataforma.

## Preguntas abiertas

- No hay datos públicos de elasticidad (b) típica de Meta por vertical; habría que construirlos con tests de dosis.
- ¿Cuánto del "hit rate" de Motion se traduce en rentabilidad? El informe no lo mide.
- ¿Afectan los umbrales de learning supuestamente más bajos en Advantage+ (no confirmados) a las reglas de escalado?

## Fuentes clave

- [Understand fluctuations in ad performance](https://www.facebook.com/business/help/1364841787225722) — Meta — meta-oficial
- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051), [Combine ad sets](https://www.facebook.com/business/help/2419480091640105), [Best practices A+CB](https://www.facebook.com/business/help/2177212182495139) — Meta — meta-oficial
- [Meta Andromeda](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — Meta Engineering, 2024-12-02 — meta-engineering
- [Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — Motion, 2026 — vendor
- [The Meta Report: 640 experiments](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 (nota jul-2026) — vendor
- [Average vs marginal ROI](https://getrecast.com/average-vs-marginal-roi-in-mmm-when-to-use-each-and-why-both-matter-for-your-budget/) — Recast, 2025-08-16 — vendor
- [Digital Ads Benchmark Q4 2025](https://tinuiti.com/research-insights/research/digital-ads-benchmark-report-q4-2025/) — Tinuiti, ene-2026 — agencia
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07-02 — practitioner
