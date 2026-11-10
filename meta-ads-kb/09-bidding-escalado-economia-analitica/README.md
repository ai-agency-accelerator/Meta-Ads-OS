# Área 09 — Bidding, escalado, economía unitaria y analítica

> Última verificación: 2026-10-16 · Autor: A09 (agente) · Ledger: [fuentes/ledger-09-bidding-escalado-economia-analitica.md](../fuentes/ledger-09-bidding-escalado-economia-analitica.md) (115 fuentes; ≈50 páginas oficiales de Meta leídas directamente)

## Índice

| # | Archivo | Qué responde |
|---|---|---|
| 01 | [01-estrategias-de-puja.md](01-estrategias-de-puja.md) | Nombres vigentes, mecánica (bid × EAR), spend/goal/manual, cómo fijar objetivos, bid-limited vs budget-limited |
| 02 | [02-value-optimization-y-value-rules.md](02-value-optimization-y-value-rules.md) | Value optimization (purchase, profit, pLTV), ROAS goal, value rules y su cronología, cuándo pasar de volumen a valor |
| 03 | [03-escalado-tipos-y-condiciones.md](03-escalado-tipos-y-condiciones.md) | Curva de respuesta, CPA marginal vs medio, tipos de escalado, Andromeda, condiciones y señales de fallo |
| 04 | [04-cambios-de-presupuesto-y-duplicacion.md](04-cambios-de-presupuesto-y-duplicacion.md) | Significant edits, "regla del 20 %", +75 %/7×, budget sharing, scheduling, A+CB, duplicación |
| 05 | [05-cpm-que-lo-determina.md](05-cpm-que-lo-determina.md) | Factores del CPM, tendencias de precio 2023-2026, por qué un CPM alto no es malo, diagnóstico |
| 06 | [06-estacionalidad.md](06-estacionalidad.md) | BFCM, diciembre, enero, elecciones (midterms 2026), Mundial 2026, verticales, playbook de picos |
| 07 | [07-frecuencia.md](07-frecuencia.md) | Frecuencia como resultado mecánico, contexto, fatiga oficial (coste ≥2×), reglas sin umbrales mágicos |
| 08 | [08-economia-unitaria-calculadoras.md](08-economia-unitaria-calculadoras.md) | Break-even CPA/ROAS/MER, CPL/booked call/show, LTV y payback, incrementalidad; ejemplos ecommerce y high-ticket |
| 09 | [09-taxonomia-metricas-diagnostico-top-down.md](09-taxonomia-metricas-diagnostico-top-down.md) | BUSINESS → FUNNEL → ADS → CREATIVE; descomposición log del CPA; árbol de diagnóstico |
| 10 | [10-dashboards-reporting.md](10-dashboards-reporting.md) | Dashboards diario/semanal/mensual/creativo/negocio, cohortes de lead gen, change log |
| 11 | [11-cuando-no-tocar-una-campana.md](11-cuando-no-tocar-una-campana.md) | Paciencia por volumen y attribution lag; matriz toco/no toco |
| 12 | [12-razonamiento-estadistico.md](12-razonamiento-estadistico.md) | Tablas de ruido Poisson, MDE, comparaciones múltiples, regresión a la media, peeking (calculado con python) |
| 13 | [13-experimentacion-ab-tests.md](13-experimentacion-ab-tests.md) | A/B tests de Meta, creative testing tool, holdouts, diseño y errores |

## TL;DR del área

1. **Nomenclatura 2026**: Highest volume, Highest value (spend-based); Cost per result goal (= cost cap), ROAS goal (= min ROAS) (goal-based); Bid cap (manual). Sin estrategias nuevas en 2025-2026. **[OFFICIAL META]**
2. **Goal-based trabaja sobre medias semanales**; Meta pide 50–100+ conv/semana, objetivo inicial CPA +10–20 % / ROAS −10–20 %, ajustes de 5–10 % y ≥7 días entre cambios. **[OFFICIAL META]**
3. **Evidencia de campo (CTC, 253 cuentas, 2025-2026)**: ROAS goal aterriza ~96 % del objetivo; CPR goal ~140 % (CPA 40 % por encima). **[EMPIRICAL]**
4. **No existe un % oficial de cambio de presupuesto que reinicie learning**: "puede o no, según magnitud". La regla del 20 % es un ritmo de practitioners, no un umbral técnico. **[OFFICIAL META]**/**[EMPIRICAL]**
5. **Overspend oficial**: hasta 175 % al día y 7× a la semana (210 %/8,4× con ad set budget sharing); budget scheduling ≤8× en franjas ≥3 h. **[OFFICIAL META]**
6. **Escala con CPA marginal**: CPA marginal ≈ CPA medio / elasticidad; el beneficio máximo está donde CPA marginal = break-even, con CPA medio muy por debajo. **[STRONG INFERENCE]**
7. **El motor de escala en la era Andromeda es la diversidad creativa y la consolidación**, no la fragmentación de audiencias ni duplicar ad sets (auction overlap). **[OFFICIAL META]**/**[EMPIRICAL]**
8. **El CPM es diagnóstico, no KPI** en campañas de conversión; Meta "subvenciona" la relevancia; precio por anuncio +12 % interanual en H1-2026 (+20 % EE. UU./Canadá en Q2). **[OFFICIAL META]**
9. **Estacionalidad**: BFCM sube CPM pero baja CPA (CVR compensa); la segunda semana de diciembre es la peligrosa; final de diciembre/enero barato; midterms EE. UU. 3-nov-2026 con bloqueo de anuncios políticos 27-oct→3-nov. **[EMPIRICAL]**/**[OFFICIAL META]**
10. **Frecuencia**: no hay umbral universal; la fatiga oficial se define por coste (≥2× tus anuncios previos), no por frecuencia. **[OFFICIAL META]**
11. **Economía**: break-even ROAS = 1/margen de contribución; CPL máximo = contribución × booking × show × close; decide con la capa más incremental disponible. **[STRONG INFERENCE]**
12. **Estadística**: con 30 conversiones el CPA real está entre 0,70× y 1,48× del observado; detectar un 20 % de diferencia exige ~470 conversiones por brazo; mirar a diario un test lleva a ~20 % de falsos positivos. **[STRONG INFERENCE]**
13. **Experimentación**: Meta desaconseja testear "a mano"; A/B con ≥80 % de estimated power, 1–30 días, hasta 5 versiones; creative testing tool solo con Highest volume. **[OFFICIAL META]**/**[EMPIRICAL]**

## Cambios 2025-2026 relevantes para el área (con fecha)

| Fecha | Cambio | Evidencia |
|---|---|---|
| nov-2023 (→ vigente) | Flexibilidad diaria 25 % → 75 % | [OFFICIAL META] + Loomer |
| feb-2025 | Fin del tope de presupuesto a clientes existentes en ASC | [EMPIRICAL] |
| may-2025 → dic-2025 | Value rules: lanzamiento, placements (jul/ago), todos los objetivos (ago), device y conversion location (nov), breakdown (dic) | [EMPIRICAL] |
| jun/jul-2025 | Advantage+ sales sustituye a ASC; "Advantage" → "Advantage+" (campaign budget) | [EMPIRICAL] |
| jul-2025 | Ad set budget sharing (hasta 20 %) | [OFFICIAL META] (Help Center) |
| ago-2025 | Spending limits de ad set en A+CB pasan a ser media, no tope | [EMPIRICAL] |
| oct-2025 | Hasta 5 % del presupuesto a placements excluidos (oficial en el changelog v24, 8-oct-2025); engaged-view 10 s → 5 s (observado; comunicado oficialmente el 3-mar-2026); creative testing tool | [OFFICIAL META] / [EMPIRICAL] |
| 2025-2026 | Requisito value optimization: de ~30 conv/5 valores/14 d a ≥100 eventos/5 valores/14 d (recomendado); profit y pLTV documentados | [OFFICIAL META] (texto actual) |
| 12-ene-2026 | Retirada de ventanas 7d/28d view en Ads Insights API | [EMPIRICAL] |
| mar-2026 | Click-through = solo link clicks; nueva engage-through (1 día) | [EMPIRICAL] (AdExchanger) |
| H1-2026 | Precio por anuncio Meta +12 % interanual (Q1 y Q2) | [OFFICIAL META] |
| jun–jul-2026 | Mundial 2026; CPM DTC >17 $ (repreciación estructural según CTC) | [EMPIRICAL] |
| ago-2026 | Creative diversity score (Low/Medium/High) "estimated and in development"; agentes IA con control de cambios de presupuesto; opt-in obligatorio para breakdowns de frecuencia/hora/dispositivo en API | [EMPIRICAL] |
| ago→oct-2026 | Fin de la selección manual de placements en ad sets de Sales/Leads/App promotion (Engagement no; corrección 2026-11-09); value rules por placement + exclusiones de cuenta | [OFFICIAL META] |
| 2026 (Help Center) | Bid multipliers → value rules obligatorio "by 2027" | [OFFICIAL META] |
| 27-oct→3-nov-2026 | Bloqueo de nuevos anuncios políticos/sociales en EE. UU. (midterms) | [OFFICIAL META] vía PPC Land |

## Contradicciones y puntos a contrastar con otras áreas

- **Umbral de learning**: Meta documenta ~50 resultados/semana (oct-2026); blogs 2026 afirman 25 (Advantage+ sales) o 15 (app) sin fuente oficial → áreas 01, 10 y 12.
- **Docs de Meta inconsistentes**: Marketing API sigue diciendo "+25 %" de overspend diario (Help Center: 75 %); Help Center llama "goal-based" a ROAS goal en una página y "manual" en la de value rules.
- **Incrementalidad A+ vs manual** (Haus 2025) y nota de Haus (jul-2026) de que incremental attribution ya supera a la estándar → área 04 (medición) y 02 (estructura).
- **Cambios de atribución 2026** (click-through/engage-through, ventanas view en API) solo verificados vía fuentes secundarias → área 04 debe confirmar con fuente primaria.
- **"Frecuencia 4 = −45 %" atribuido a Meta**: sin fuente primaria → área 12 (mitos).
- **CPR goal sobre-entrega coste (~140 %)** vs recomendación oficial de fijarlo +10–20 % sobre CPA histórico: tensión real; área 11 (benchmarks/expertos) podría buscar más datos.
- **Lebesgue**: afirma CAC 10 % más bajo dentro del learning que fuera (sin metodología) — contradice el folklore; área 12.

## Huecos y preguntas abiertas

- No hay datos públicos controlados sobre el efecto de subidas de presupuesto de distinto tamaño (10/20/50/100 %) en CPA y learning.
- Elasticidad gasto→conversiones típica por vertical en Meta: no publicada; solo construible con tests de dosis/MMM.
- Efecto real de las midterms 2026 sobre CPM no político (solo previsiones a 16-oct-2026).
- Si budget scheduling o adjuntar value rules reinician learning: no documentado.
- Umbral de confianza con el que Meta declara "winner" en A/B tests: no documentado en lo consultado.
- Benchmarks fiables de show/close rate high-ticket por vertical: inexistentes con metodología sólida.
- Metodología del creative diversity score y si afecta a la entrega.

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Fila oct-2025: el 5 % en placements excluidos está documentado en el changelog oficial de la Marketing API v24.0 (8-oct-2025, `placement_soft_opt_out`, Sales y Leads); el cambio de engaged-view a 5 s lo comunicó Meta el 3-mar-2026. Etiqueta ajustada.
