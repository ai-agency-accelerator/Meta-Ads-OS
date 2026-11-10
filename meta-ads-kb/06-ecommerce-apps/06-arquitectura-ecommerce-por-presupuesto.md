# Arquitectura de cuentas e-commerce por presupuesto, tipo de catálogo y ticket/margen

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: cómo estructurar campañas de e-commerce en Meta a €100, €500, €5.000 y €50.000/día; variaciones para hero product vs catálogo grande y por ticket/margen. Principios generales de estructura y bidding: carpetas 02 y 09 (otros agentes). Esto es la capa específica de e-commerce.

## TL;DR

- **La estructura la dicta la señal, no el gusto.** Meta necesita ~50 eventos de optimización por ad set en 7 días para salir de aprendizaje [OFFICIAL META]. Compras/semana = presupuesto diario × 7 / CPA. A €100/día y CPA 30 € son ~23 compras/semana: **una campaña, un ad set**. Cada división adicional debe justificarse con economía (margen, mercado, objetivo) o medición.
- **Desde 2025-2026 la estructura e-commerce estándar es: 1 campaña principal Advantage+ sales (adquisición) + 1 espacio de test creativo + (opcional) catálogo + (opcional) retención/reactivación acotada.** El resto (por mercado, por línea de producto, por puja) aparece al crecer. [STRONG INFERENCE] — coherente con la consolidación que promueve Meta y con la recomendación de Haus de consolidar y segmentar lower-funnel solo cuando haga falta.
- **El cuello de botella al escalar es creativo, no estructural.** Motion (550.000 anuncios, 6.000 anunciantes, sep-2025–ene-2026): solo el 5–8 % de los anuncios se convierten en ganadores y ~la mitad nunca recibe gasto relevante → para encontrar 2–3 ganadores al mes necesitas lanzar ~30–60 anuncios/mes. [EMPIRICAL, vendor]
- **Hero product / monoproducto**: catálogo casi irrelevante; todo el peso en conceptos creativos, ángulos y landing pages. **Catálogo grande**: catálogo como columna vertebral + creatividad de marca/tentpole. [STRONG INFERENCE]
- **Ticket y margen fijan el evento y la paciencia**: ticket bajo/margen bajo → necesitas AOV (bundles) antes que más presupuesto; ticket alto → ciclos largos, ventanas de atribución y post-treatment más largos (HexClad: el coste por adquisición incremental cayó 56–67 % al añadir 3 semanas de observación post-test). [EMPIRICAL]
- **A ≥ €5.000/día la medición deja de ser opcional**: test de incrementalidad al menos semestral (geo-lift o Conversion Lift), y concentrar ≥ 75 % del gasto en el tipo de campaña ganador (Haus: 50/50 Advantage+/manual rindió −18 % iROAS). [EMPIRICAL]
- **A ≥ €50.000/día entra el full-funnel medido**: mid/upper-funnel con 5–10 % del presupuesto (Haus: upper-funnel ~6–7 % del gasto, 81 % de impacto en clientes nuevos y halo omnicanal +138 %). Solo si mides omnicanal. [EMPIRICAL]

## 1. Aritmética de señal por presupuesto

| Presupuesto diario | CPA 15 € | CPA 30 € | CPA 60 € | CPA 120 € |
|---|---|---|---|---|
| €100 | 47 compras/sem | 23 | 12 | 6 |
| €500 | 233 | 117 | 58 | 29 |
| €5.000 | 2.333 | 1.167 | 583 | 292 |
| €50.000 | 23.333 | 11.667 | 5.833 | 2.917 |

Regla: nº máximo razonable de ad sets "de rendimiento" ≈ compras semanales / 50. Con 23 compras/semana → 1 ad set (y aun así en learning limited a menudo; acéptalo y no reinicies). [STRONG INFERENCE sobre la regla; el umbral de 50 es OFFICIAL META]

**Evento de optimización con poco volumen** [CONTESTED]:
- Opción A (mayoría de practitioners 2025-2026): optimizar a Purchase incluso con 15–30 compras/semana; el sistema actual aprende con menos señal que en 2019 y los eventos intermedios atraen "clicadores".
- Opción B: AddToCart/InitiateCheckout si < ~10–15 compras/semana. Haus encontró que la optimización mid-funnel tuvo −14 % de iROAS DTC frente a lower-funnel (a 85 % menos gasto), pero en marcas con < 5.000 compras/semana la diferencia era solo −5 %, con más clientes nuevos (78 % vs 67 %). Ojo: son marcas grandes.
- Recomendación: Purchase por defecto; probar ATC solo si la cuenta no sale de "learning limited" y el CPA es errático, y medir con nCAC, no con CPA de ATC.

## 2. €100/día (~3.000 €/mes): validar oferta y creatividad

**Objetivo**: encontrar 1–3 conceptos que conviertan a CPA ≤ break-even (ver `05-…`).

| Elemento | Recomendación |
|---|---|
| Campañas | 1 campaña de Ventas Advantage+ (presupuesto de campaña, audiencia Advantage+, placements Advantage+) |
| Ad sets | 1 (opcional: Customer lifecycle strategy = nuevos si ya hay base de clientes y email activo) |
| Anuncios activos | 4–8 conceptos distintos (no variaciones) |
| Nuevos anuncios | 3–5 por semana, sustituyendo los que no gastan o no convierten tras ~2× CPA objetivo de gasto |
| Catálogo | Solo si > ~50 SKUs y match ≥ 90 %; como un anuncio más dentro del ad set |
| Retargeting | No separado: a este gasto, la campaña principal ya cubre visitantes. Email/SMS hace el retargeting barato |
| Puja | Lowest cost (sin cap) |
| Medición | Pedidos y clientes nuevos en tienda, MER, CPA vs break-even; no hay presupuesto para lift tests |
| Errores a evitar | 5 ad sets por intereses; cambiar presupuesto a diario; juzgar un anuncio con 20 € gastados |

**Benchmark de contexto**: CPA mediano de Meta en e-commerce ~39 $ y ROAS mediano ~1,9 (Triple Whale, ago-2025–jul-2026; agregados de miles de tiendas con atribución de plataforma). [EMPIRICAL vía secundaria] — útil para no esperar milagros, no como objetivo.

## 3. €500/día (~15.000 €/mes): sistema mínimo de crecimiento

| Elemento | Recomendación |
|---|---|
| Campañas | (1) **Principal Advantage+ sales** — 80–90 % del gasto. (2) **Test creativo** — 10–20 % (ad set con presupuesto propio o campaña separada; los ganadores se duplican a la principal) |
| Clientes existentes | Definidos en cuenta; si el breakdown muestra > 20–30 % del gasto en existentes y email/SMS es fuerte → Customer lifecycle strategy = nuevos o estructura de 2 ad sets con cap (ver `03-…`) |
| Catálogo | Si catálogo > 100 SKUs: catalog ads dentro de la principal; si > 1.000 SKUs, considerar ad set de catálogo propio para leerlo |
| Anuncios nuevos | 8–15 por semana |
| Puja | Lowest cost; probar cost cap o ROAS mínimo solo con 4+ semanas estables |
| Medición | Semanal: MER, nCAC blended, % nuevos (tienda), breakdown de segmentos. Trimestral: holdout simple (p. ej. pausar retargeting en un 20 % de geos si existe) |
| Estacionalidad | Presupuesto BFCM ×1,5–3 sobre base (ver `08-…`) |

## 4. €5.000/día (~150.000 €/mes): portafolio con medición

| Bloque | % gasto orientativo | Notas |
|---|---|---|
| Advantage+ sales — adquisición (Customer lifecycle = nuevos o exclusión de clientes) | 55–70 % | Campaña principal; puede haber 2 (p. ej. España y resto de UE, o líneas de producto con economía distinta) |
| Test creativo | 10–15 % | 20–40 anuncios nuevos/semana; graduación con criterios (CPA, hook rate, nCAC) |
| Catálogo (prospección amplia) | 0–20 % | Solo catálogos grandes; medir con incrementalidad |
| Retención / reactivación (listas de clientes inactivos 180–365 d, cross-sell) | 3–8 % | Con holdout permanente 10–20 % |
| Mid-funnel / lanzamientos / marca | 0–10 % | Solo si hay KPI omnicanal o de nuevos |

Más:
- **Pujas**: mezcla de lowest cost (volumen) y cost cap / ROAS mínimo (eficiencia) en campañas paralelas; ver carpeta 09.
- **Mercados**: separar campañas por país solo si difieren precio, IVA, logística, idioma o economía. Recuerda location fees (3 % ES/FR/IT, 2 % UK, 5 % AT/TR).
- **Partnership ads / creadores**: línea fija de producción (Sephora US combinó creadores + catálogo + Advantage+ audience con 1,56× ROAS incremental omnicanal, lift study de Meta). [OFFICIAL META vía secundaria]
- **Medición**: geo-lift o Conversion Lift **al menos 2 veces/año** (Advantage+ vs manual, retargeting on/off, 1DC vs 7DC); Dr. Squatch: 7DC dio +6,51 % de revenue nuevo vs 1DC. [EMPIRICAL]
- **Regla Haus**: tras el test, concentra ≥ 75 % en la configuración ganadora; no 50/50.

## 5. €50.000/día (~1,5 M€/mes): full-funnel medido

| Elemento | Recomendación |
|---|---|
| Campañas | Varias Advantage+ sales por mercado/categoría con economía distinta; campañas con cost cap/ROAS mínimo para proteger margen; catálogo por regiones si el surtido difiere |
| Creatividad | Producción industrial: 50–150 anuncios nuevos/semana, varios formatos, creadores, partnership ads, vídeo de catálogo, IA generativa con control de marca |
| Full-funnel | Mid-funnel (ATC/ViewContent) y upper-funnel (reach/vídeo) con 5–10 % del gasto **solo** con medición omnicanal; Haus: upper-funnel −46 % iROAS DTC en test pero 81 % de nuevos y +138 % de halo fuera de DTC; mid-funnel 78 % nuevos y +70 % halo |
| Medición | Programa continuo: geo-lift trimestral, MMM (Meta Robyn u otros), Incremental Attribution como opción a testear (Haus 2026: 1,26× vs estándar en jul-2025–jun-2026) |
| Omnicanal | Si ≥ 25 % de ventas fuera de DTC (Amazon, retail): ~32 % del impacto de Meta cae fuera de DTC; break-even DTC iROAS 0,68× (Haus) |
| Gobernanza | Presupuesto por nCAC marginal (no medio): ¿cuánto cuesta el siguiente cliente? |

## 6. Variaciones por tipo de catálogo

### 6.1 Hero product / monoproducto (1–10 SKUs)

- **Catálogo**: secundario (formato de retargeting y product extensions).
- **Palanca**: conceptos creativos (problema-solución, demostración, comparativa, prueba social, creador), landing pages por ángulo, ofertas (bundles 2×/3×, suscripción).
- **Estructura**: 1 campaña principal + test creativo agresivo; ad sets por ángulo no aportan (Advantage+ ya "encuentra" la audiencia por la creatividad).
- **Métrica**: CPA del primer pedido vs CM2 del bundle medio; AOV por oferta.
- **Riesgo**: fatiga creativa rápida (un solo producto). Necesitas más volumen de conceptos que un catálogo grande.

### 6.2 Catálogo medio (10–500 SKUs, varias colecciones)

- Catálogo dentro de la principal + 3–5 product sets con motivo (bestsellers, margen alto, novedades, tentpole).
- Creatividad de colección y lifestyle; vídeo en top 20 SKUs.

### 6.3 Catálogo grande (> 500–1.000 SKUs, moda/hogar/retail)

- **Catálogo como columna vertebral** (prospección amplia + retargeting acotado); feed y product sets por margen/stock son el trabajo diario.
- Creatividad de concepto para marca, temporadas y lanzamientos.
- Batch API/feed horario en rebajas.
- Medición de incrementalidad del retargeting dinámico (el más inflado).

## 7. Variaciones por ticket y margen

| | Margen alto (CM2 ≥ 50 %) | Margen bajo (CM2 < 30 %) |
|---|---|---|
| **Ticket bajo (< 40 €)** | Escala bien; cuida el AOV (umbral de envío gratis, bundles); Purchase como evento; volumen creativo alto | Difícil en primer pedido: subir AOV antes que presupuesto; nCAC por recompra solo si hay cohortes probadas; considerar marketplaces |
| **Ticket alto (> 150 €)** | Paciencia: ciclos de 2–6 semanas; ventanas 7d clic; creatividad educativa; financiación (BNPL) como mensaje; medir con ventana post-test (HexClad) | Peligroso: CPA alto con margen pequeño en € — exigir ROAS de plataforma alto y probar ROAS mínimo; foco en producto de entrada |

Notas:
- **Ticket alto**: el CPA tiene más varianza por compra (cada venta cuenta mucho) → evaluar en ventanas de 14–28 días, no diarias. [STRONG INFERENCE]
- **Ticket bajo + margen bajo**: el envío se come el margen; el gasto en ads no lo arregla. [STRONG INFERENCE]

## 8. Ritual operativo semanal (cualquier presupuesto)

1. Revisar P&L de la semana: MER, CM3, nCAC blended, % nuevos.
2. Breakdown de segmentos en Meta (nuevos/engaged/existentes) y comparar con tienda.
3. Creatividad: qué gastó, qué ganó, qué se fatigó; lanzar la tanda nueva.
4. Feed: errores, match rate, precios/stock en promociones.
5. Solo entonces: ajustes de presupuesto (±20–30 % por paso en campañas estables) y de puja. Ver carpeta 09.

## Implicaciones operativas

- Calcula compras/semana por ad set antes de dividir nada.
- Separa campañas solo por economía distinta (mercado, margen, objetivo nuevo vs existente) o por necesidad de medición.
- Dimensiona el presupuesto de test creativo según la tasa de acierto (5–8 % de ganadores): a más presupuesto, más anuncios nuevos por semana.
- A partir de €5.000/día, presupuesto anual para 2–4 tests de incrementalidad.
- Hero product → invierte en creatividad y landing; catálogo grande → invierte en feed y product sets.

## Errores frecuentes

- Replicar a €100/día la estructura de una cuenta de €50.000/día.
- Separar prospección/retargeting en campañas pequeñas que nunca salen de learning.
- Mantener 50/50 Advantage+ y manual "para diversificar".
- Escalar presupuesto sin escalar producción creativa.
- Medir campañas de ticket alto día a día.

## Preguntas abiertas

- Umbral real en 2026 a partir del cual separar campañas por país dentro de la UE (con location fees diferenciados y Advantage+ que ya reparte).
- Efecto del "Creative Diversity Score" (reportado ago-2026) en el número óptimo de conceptos por ad set.
- Datos públicos de incrementalidad de mid/upper-funnel en cuentas pequeñas (< €1.000/día): la evidencia de Haus es de marcas grandes.

## Fuentes clave

- [The Meta Report (Haus)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Optimizing Meta Ads: A Playbook for Brands (Haus)](https://www.haus.io/blog/optimizing-meta-ads-a-playbook-for-brands) — 2025-08-15 — vendor
- [Haus customer story: HexClad](https://www.haus.io/customer/hexclad) — 2024-06-17 — vendor
- [Haus customer story: Dr. Squatch](https://www.haus.io/customer/dr-squatch) — 2025-05-22 — vendor
- [2026 creative benchmarks (Motion)](https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/2026-creative-benchmarks) — 2026 — vendor
- [Facebook Ad Benchmarks by Industry (Triple Whale)](https://www.triplewhale.com/blog/facebook-ads-benchmarks) — 2026 (datos ago-2025–jul-2026) — vendor (consultado vía resúmenes de búsqueda; acceso directo bloqueado)
- [Advantage+ Campaigns (Marketing API)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
- [Facebook Advertising Case Studies — Sephora US (vía Meta success story)](https://cropink.com/meta-ads-examples) — 2025 — vendor
