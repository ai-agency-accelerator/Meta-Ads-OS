# Pacing, presupuesto y frecuencia: cómo gasta Meta tu dinero y a cuántas personas/veces

> Última verificación: 2026-10-15 · Autor: A01 (agente) · Ámbito: mecánica de pacing (budget/bid pacing), presupuestos diarios/totales, Advantage+ campaign budget, budget sharing, programación y frecuencia. El "cómo escalar" detallado corresponde al área 09.

## TL;DR

- **Pacing = el sistema ajusta tu puja efectiva en cada subasta para gastar el presupuesto a lo largo del periodo, empezando por las oportunidades de mayor valor esperado por euro.** Meta (Marketing API): con pacing estándar, tu anuncio "entra en cada subasta relevante y ajusta tu puja a lo largo del día para producir una entrega suave y óptima respecto a tu objetivo y presupuesto". **[OFFICIAL META]**
- **El presupuesto diario es en realidad semanal**: desde nov-2023 Meta puede gastar **hasta un 75% más** del presupuesto diario en días con mejores oportunidades (antes 25%), sin superar **7× el diario en la semana** (domingo-sábado). **[OFFICIAL META]** (texto de Ads Manager citado por Jon Loomer).
- **Más presupuesto ≠ mismo CPA**: al subir presupuesto, el pacing tiene que entrar en oportunidades marginalmente peores (o pujar más alto en las mismas). Meta: el coste "puede subir a medida que se agotan las oportunidades más baratas". Rendimientos decrecientes son el comportamiento esperado. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Advantage+ campaign budget (antes CBO)** hace el pacing a nivel de campaña y reparte entre ad sets en tiempo real; **Ad set budget sharing** (doc. oct-2025) permite compartir hasta el **20%** del presupuesto diario de cada ad set con otros ad sets de la campaña (misma estrategia de puja). **[OFFICIAL META]**
- **Cambiar puja/presupuesto obliga al sistema a "reaprender la puja óptima"**: Meta recomienda no hacerlo más de 2-3 veces al día y preferiblemente al principio del día. Ads Manager muestra hasta cuánto puedes subir presupuesto sin re-entrar en aprendizaje (p. ej. de $100 a $179). **[OFFICIAL META]**
- **Accelerated delivery (no pacing)** puja al máximo en todas las subastas elegibles y puede agotar el presupuesto pronto; solo tiene sentido con bid cap y para picos temporales (flash sales, eventos en directo). Si infra-entregas por puja baja o segmentación estrecha, "no ayudará". **[OFFICIAL META]**
- **Frecuencia en campañas de rendimiento no se controla directamente**: la deciden el modelo de ad load por sesión, la redistribución de anuncios entre usuarios/sesiones (Meta, 2S-2025: ≈4× más impacto en ingresos que subir ad load) y el tamaño/diversidad de tu inventario creativo. Estudio de Meta (2022): rendimiento −45% cuando la frecuencia media llega a 4, pero no es un umbral universal (Loomer, sep-2025). **[OFFICIAL META]** / **[EMPIRICAL]**.

---

## 1. Cómo funciona el pacing (primeros principios + lo publicado)

### 1.1 Lo que dice Meta
Marketing API, *Pacing and scheduling* (vigente 2026):
- El pacing "controla cómo se gasta tu presupuesto en el tiempo" y busca "competencia uniforme en la subasta de Facebook entre todos los anunciantes cada día".
- **Standard pacing (por defecto)**: "entra en cada subasta relevante y ajusta tu puja a lo largo del día".
- **No pacing / accelerated**: "elimina todos los ajustes de pacing de tu puja"; entra en "todas las subastas elegibles con su puja máxima completa"; la entrega "no es suave" y el presupuesto puede agotarse antes de terminar el día. Usos: flash sales, eventos en directo, momentos estacionales clave.
- **Días parciales**: si un ad set con presupuesto diario empieza a las 18:00, Meta intenta entregar "solo el 25% del presupuesto diario entre las 18:00 y medianoche" (desde 9-abr-2014).
- **Con Advantage+ campaign budget**, "el pacing del presupuesto es a nivel de campaña"; si no, a nivel de ad set.
- Cambios de puja/presupuesto requieren "reaprender la puja óptima": "no deberías cambiar puja y presupuesto" a menudo; "2-3 veces al día y solo en la primera parte del día".
- **Infra-entrega** suele significar "puja demasiado baja o audiencia demasiado estrecha"; **sobre-entrega**, "una audiencia muy grande que agota rápido el presupuesto".

### 1.2 Modelo mental
El pacing es un **controlador de retroalimentación**: compara el gasto real con una curva objetivo de gasto (que sigue la distribución de oportunidades durante el día/semana) y ajusta un multiplicador sobre tu puja. Es el diseño estándar de la industria ("soft throttling" con multiplicador de puja, p. ej. *Mystique* de Yahoo, WWW 2024; controladores PID en la literatura). Meta no ha publicado su algoritmo de pacing. **[STRONG INFERENCE]** (análogo industrial) / **[HYPOTHESIS]** (detalles internos de Meta).

Consecuencias:
- **Lowest cost**: la puja efectiva sube o baja hasta gastar el presupuesto; el CPA resultante es una **salida**, no un input. Si el presupuesto es grande respecto a las oportunidades de calidad, el sistema gastará en oportunidades peores.
- **Cost cap**: el controlador tiene dos objetivos (gastar y no superar un CPA medio). Si el mercado no ofrece suficientes oportunidades bajo el cap, **gasta menos** ("puede no gastar todo el presupuesto una vez alcanzado el cap"). La adherencia "no está garantizada".
- **Bid cap**: limita la puja por subasta; entrega muy sensible a la competencia del día (Q4, festivos).
- **ROAS goal**: suelo de ROAS medio; un suelo alto → infra-entrega.

### 1.3 Presupuesto diario vs total
- **Diario**: media semanal con flexibilidad +75% por día y tope 7× semanal (desde nov-2023). "En días en que hay mejores oportunidades disponibles para ti, podemos gastar hasta un 75% más de tu presupuesto diario" (texto de Meta citado por Loomer). **[OFFICIAL META]**
- **Total (lifetime)**: el pacing distribuye el gasto a lo largo del periodo y permite programación horaria (dayparting) en la **zona horaria del usuario**, no de la cuenta. **[OFFICIAL META]**
- **Daily budget scheduling** (2023): programar subidas de presupuesto por franjas (hasta 50 por ad set) que vuelven al importe original fuera de la franja. **[OFFICIAL META]** vía Loomer.

### 1.4 Reparto entre ad sets
- **Advantage+ campaign budget (antes Campaign Budget Optimization)**: un único presupuesto y pacing de campaña; el sistema asigna a ad sets según oportunidades. Tiende a concentrar en el ad set con más oportunidades de bajo coste (críticos desde 2019 señalan que favorece audiencias grandes aunque las pequeñas rindan mejor en CPA). **[OFFICIAL META]** (mecanismo) + **[EMPIRICAL]** (sesgo observado).
- **Ad set budget sharing** (Marketing API, actualizado 7-oct-2025): hasta un 20% del presupuesto diario de cada ad set se comparte con otros ad sets en tiempo real según rendimiento; requiere misma estrategia de puja; solo campañas nuevas/duplicadas y con presupuesto diario. Término medio entre ABO y CBO. **[OFFICIAL META]**
- **Límites de gasto por ad set** dentro de CBO: útiles para forzar exploración mínima o contener ad sets, a costa de interferir con el optimizador. **[STRONG INFERENCE]**

## 2. Escalar presupuesto: qué pasa por dentro

1. Subes presupuesto → el controlador de pacing necesita gastar más → puja efectiva más alta y/o entra en oportunidades con menor EAR → **CPM y CPA marginales suben**. **[STRONG INFERENCE]** consistente con "el coste puede subir a medida que se agotan las oportunidades más baratas" (Meta, Bid strategy).
2. Si la subida es "significativa", el ad set puede re-entrar en learning phase. Meta muestra el máximo recomendado sin reinicio en Ads Manager (ej. $100 → $179/día en una campaña con Advantage campaign budget, nov-2023). **[OFFICIAL META]**
3. La regla del "20% cada 3 días" es **folklore útil**, no regla oficial publicada. **UNPROVEN**.
4. **Lo que de verdad amplía el techo**: más oportunidades de alto EAR (nuevos conceptos creativos que conectan con personas distintas, nuevas geos, placements, ofertas), no la "técnica" de subida. **[STRONG INFERENCE]**

## 3. Frecuencia

### 3.1 Quién la decide
- **Ad load por persona y sesión** (Meta decide cuántos anuncios ve cada persona y cuándo). **[OFFICIAL META]**
- **Redistribución** de anuncios entre usuarios y sesiones (2S-2025) → la exposición a anuncios se concentra en momentos de mayor interés predicho. **[OFFICIAL META]**
- **Tu inventario creativo**: si tienes 1-2 conceptos, las personas a las que el sistema elige verán los mismos; con conceptos diversos, la misma frecuencia de campaña se reparte entre anuncios distintos. **[OFFICIAL META]** (página de creative differentiation: creativos demasiado similares → mismo público → solapamiento y fatiga).
- **Topes explícitos** solo en Reach & Frequency y objetivos de alcance/awareness. **[OFFICIAL META]**

### 3.2 Evidencia sobre frecuencia y rendimiento
- Meta (estudio 2022, citado por Jon Loomer): el rendimiento cae ~45% cuando la frecuencia media alcanza 4. Loomer (24-sep-2025) advierte que no es umbral mágico: depende del nivel (ad vs campaña), placement, periodo, producto (compras de alta implicación necesitan más exposiciones). **[EMPIRICAL]**
- Investigación de Meta/Nielsen sobre frecuencia efectiva de marca: ~1 exposición/semana captura gran parte del lift de recuerdo; ~2,25/semana como óptimo en un estudio Nielsen-Meta (citas secundarias). **[EMPIRICAL]** (no verificado en fuente primaria).
- **Estados de entrega** "Creative limited" (coste por resultado aumentado frente a anuncios previos, menos del doble) y "Creative fatigue" (coste por resultado aproximadamente duplicado) — definiciones vía fuentes secundarias; Meta confirma ambos estados en su página oficial de diferenciación creativa. **[OFFICIAL META]** (existencia) / **[EMPIRICAL]** (umbrales).

### 3.3 Cómo leer la frecuencia
- Frecuencia alta + CPA estable = el sistema está encontrando valor en re-exposición (normal en productos de consideración).
- Frecuencia alta + CPA subiendo + "Creative fatigue" = falta de conceptos nuevos o audiencia efectiva demasiado pequeña.
- Frecuencia alta en broad = señal de que el sistema solo encuentra EAR alto en un subconjunto pequeño (creativo de nicho o evento raro), no de que "broad se ha agotado". **[STRONG INFERENCE]**

## 4. Estacionalidad y competencia
- El umbral de precio lo fija la competencia por la misma persona (subasta tipo segundo precio). En picos (BFCM, Navidad) la puja efectiva necesaria sube; lowest cost seguirá gastando, cost/bid cap entregarán menos. **[STRONG INFERENCE]**
- El precio medio por anuncio de Meta creció +12% YoY en Q1 y Q2-2026, con fuertes diferencias regionales (US & Canadá ≈+20%, APAC ≈+1% en Q2-2026 según resúmenes secundarios). Presupuestar con CPMs crecientes. **[OFFICIAL META]** (global) / **[EMPIRICAL]** (regional, secundarias).

## Implicaciones operativas

- Tratar el **presupuesto diario como semanal**: evaluar gasto y CPA en ventanas de 7 días, no día a día.
- **Agrupar cambios** de presupuesto/puja, al principio del día, y respetar el máximo sin reinicio que sugiere Ads Manager.
- **Cost cap** solo con volumen suficiente y un CPA objetivo realista (cercano al histórico); si no, lowest cost con control por presupuesto.
- **Accelerated** solo para eventos acotados y con bid cap.
- **Frecuencia**: diagnosticar con estados de entrega + tendencia de CPA, y responder con conceptos creativos nuevos antes que con exclusiones o audiencias nuevas.
- **Budget sharing / CBO**: elegir según necesidad de control vs eficiencia; con ad sets heterogéneos (geos, productos con márgenes distintos), ABO o budget sharing limitado conservan control.

## Errores frecuentes

- Alarmarse porque un día se gasta +60% del diario (es la flexibilidad semanal).
- Subir presupuesto ×3 de golpe en un ad set con poca señal y esperar el mismo CPA.
- Usar accelerated delivery para "forzar" gasto en ad sets que infra-entregan por puja/segmentación.
- Poner topes de frecuencia mentales universales (2, 3, 4) sin mirar producto, placement y periodo.

## Preguntas abiertas

- Algoritmo exacto de pacing de Meta (multiplicador de puja vs throttling; horizonte de planificación) — no publicado.
- Cómo interactúan la redistribución de ad load por sesión de Meta y el pacing del anunciante (¿el sistema prioriza a nivel plataforma antes que a nivel anunciante?).
- Si la flexibilidad del 75% se aplica igual en todos los objetivos y con Advantage+ sales (no verificado).

## Fuentes clave

- [Marketing API – Pacing and Scheduling](https://developers.facebook.com/docs/marketing-api/bidding/overview/pacing-and-scheduling) — vigente 2026 — meta-developers
- [Marketing API – Bid Strategy](https://developers.facebook.com/documentation/ads-commerce/marketing-api/bidding/overview/bid-strategy.md) — vigente 2026 — meta-developers
- [Marketing API – Ad set budget sharing](https://developers.facebook.com/documentation/ads-commerce/marketing-api/bidding/guides/adset-budget-sharing) — act. 2025-10-07 — meta-developers
- [Jon Loomer – Updates to Meta Ads Budgeting](https://www.jonloomer.com/updates-to-meta-ads-budgeting/) — 2023-11-02 (act. 2025-03-01) — practitioner
- [Jon Loomer – Ad Set Budget Sharing](https://www.jonloomer.com/qvt/ad-set-budget-sharing/) — 2025 — practitioner
- [Jon Loomer – Frequency is not your problem](https://pubcast.jonloomer.com/frequency-is-not-your-problem/) — 2025-09-24 — practitioner
- [Mystique: A Budget Pacing System (Yahoo Research, WWW 2024)](https://yahooinc.com/research/publications/mystique-a-budget-pacing-system-for-performance-optimization-in-online-advertising) — 2024 — academico (no Meta; análogo)
- [A Practical Guide to Budget Pacing Algorithms in Digital Advertising (arXiv 2503.06942)](https://arxiv.org/html/2503.06942v2) — 2025-03 — academico (no Meta)
- Earnings Meta Q4-2024, Q4-2025 (ad load y redistribución) — meta-investors
- [Maximize conversions with differentiated ad creative](https://www.facebook.com/business/m/small-business/creative-differentiation) — vigente 2026 — meta-oficial
