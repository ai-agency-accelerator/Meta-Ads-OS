# Pipeline de entrega: de abrir Instagram a ver un anuncio (retrieval → ranking → subasta → entrega → feedback)

> Última verificación: 2026-10-15 · Autor: A01 (agente) · Ámbito: secuencia técnica de decisión de un anuncio en Meta, con lo que es público (Meta Engineering, earnings, papers de empleados) y lo que es inferencia razonable.

## TL;DR

- **El anuncio que ves es el resultado de una cascada en <1 segundo**: decisión de hueco publicitario (ad load/posición) → filtrado por elegibilidad → **retrieval** (decenas de millones → miles; Andromeda + otros generadores de candidatos, desde 2026 también LLM/generativos) → **early-stage ranking** (modelos ligeros) → **late-stage ranking** (modelos runtime destilados de GEM; Adaptive Ranking Model) → **subasta por total value** → reglas post-subasta (integridad, diversidad, experimentos) → impresión → **feedback** (clic, conversión vía pixel/CAPI) que reentrena modelos y ajusta pacing. **[OFFICIAL META]** para las etapas; orden fino y umbrales **[STRONG INFERENCE]**.
- **Cada etapa puede eliminarte**, y las primeras son las más "baratas" (modelos menos precisos). Meta reconoce que el early-stage puede descartar anuncios que el ranking final habría puntuado alto ("inconsistencia multi-etapa") y trabaja para reducirlo (fusión retrieval + early-stage en Facebook en Q3-2025). **[OFFICIAL META]**
- **Quién, cuándo, dónde, qué creativo y con qué frecuencia no los decide un único algoritmo**, sino la combinación de: modelo de ad load por sesión (cuándo/dónde hay hueco), retrieval+ranking (qué anuncio y qué creativo para esa persona), subasta (quién gana y a qué precio) y pacing (cuánto puede pujar tu ad set en ese momento para gastar su presupuesto). **[STRONG INFERENCE]** a partir de fuentes oficiales.
- **El placement no se "elige" de antemano**: cada superficie (IG Feed, IG Reels, Stories, FB Feed, Threads, WhatsApp Status…) genera peticiones de anuncio; tu ad set es elegible en las que permitas, y el reparto por placement emerge de ganar o perder subastas en cada una + pacing. **[STRONG INFERENCE]**
- **El presupuesto se gasta vía puja efectiva**: con lowest cost, el sistema ajusta continuamente tu puja (bid pacing) para gastar el presupuesto a lo largo del día/semana, entrando en las subastas de mayor valor esperado por euro. **[OFFICIAL META]** (Marketing API: pacing estándar "ajusta tu puja durante el día").
- **El bucle de feedback es la clave de todo**: las conversiones que envías entrenan los modelos (entrenamiento continuo online) y refrescan la representación del usuario (embeddings upstream disparados por conversiones). Mala señal = el sistema aprende a buscar lo equivocado. **[OFFICIAL META]**

---

## 1. Secuencia paso a paso (Instagram Feed como ejemplo)

### Paso 0 — Antes de abrir la app (offline/asíncrono)
- Modelos de usuario upstream (LLaTTE/GEM) han precalculado **embeddings del usuario** a partir de miles de eventos (orgánico + anuncios + conversiones). Se refrescan especialmente tras eventos de alto valor (conversiones). **[OFFICIAL META]** (LLaTTE; Engineering ago-2026)
- Los anuncios activos tienen representaciones precomputadas (embeddings, **Semantic IDs** derivados de texto/imagen/vídeo; desde 2026 atributos semánticos generados por LLM). Andromeda guarda embeddings de anuncios en memoria de GPU. **[OFFICIAL META]**
- Solaris (GEM 2026) precalcula de forma especulativa embeddings usuario-anuncio; si falta el exacto, usa el de usuarios similares. **[OFFICIAL META]**

### Paso 1 — Petición de feed y decisión de huecos publicitarios
- La app pide contenido. El sistema orgánico rankea posts/Reels y el sistema de **ad load** decide cuántos anuncios y en qué posiciones de la sesión. Meta: personaliza "las ubicaciones óptimas en la profundidad del feed de cada persona" (Q4-2024) y redistribuye anuncios "entre usuarios y sesiones" según cuándo la persona está más interesada (Q4-2025: ≈4× el impacto en ingresos de subir ad load). **[OFFICIAL META]**
- **Implicación:** la frecuencia y el "momento" de exposición los decide Meta por persona y sesión, no el anunciante (salvo topes en Reach & Frequency/awareness).

### Paso 2 — Petición de anuncio y elegibilidad
- Cada hueco genera una petición con contexto (usuario, superficie, dispositivo, hora). Se filtran los anuncios que pueden mostrarse: segmentación (ubicación, edad, idioma, audiencias, exclusiones), placement permitido, presupuesto/pacing activo, estado de revisión, categorías especiales, experimentos (holdouts de Lift test), y si el usuario está en Less Personalized Ads (UE). **[STRONG INFERENCE]** (lista compuesta de documentación oficial dispersa).
- **GRACE (Meta, ago-2026)** muestra que, en retrieval generativo, la segmentación del anunciante se aplica como un filtro duro sobre lo que el modelo genera (Generative Target Matching). La segmentación estrecha es una restricción que el sistema debe satisfacer, no una "pista" que lo ayude. **[OFFICIAL META]** (paper) + **[STRONG INFERENCE]** (interpretación).

### Paso 3 — Retrieval (candidate generation)
- De "decenas de millones de anuncios candidatos" a "unos pocos miles" (Andromeda). Retrieval maneja ~3 órdenes de magnitud más anuncios que las etapas siguientes y tiene la latencia más ajustada. **[OFFICIAL META]**
- Hay **varios generadores de candidatos** (ensemble): two-tower, embeddings, grafos, y desde 2025-2026 LLM semántico (Llama) y el primer modelo generativo ("Meta Generative Recommender", Q2-2026). **[OFFICIAL META]** (paper 2605.21969 describe el baseline como ensemble; earnings Q2-2026).
- Andromeda: red neuronal + índice jerárquico entrenados conjuntamente; "elasticidad" (más complejidad para segmentos de anuncios de alto valor). En Q3-2025 se fusionaron retrieval y early-stage ranking en un único modelo en Facebook (+14% ads quality). **[OFFICIAL META]**
- **Qué te hace ser recuperado:** afinidad entre la representación del usuario y la del anuncio (contenido semántico + historial de rendimiento del anuncio/anunciante + valor potencial). Por eso **el creativo es la "segmentación"** en retrieval. **[STRONG INFERENCE]**

### Paso 4 — Early-stage ranking
- Modelos ligeros (multi-tarea) puntúan los miles de candidatos y pasan los mejores (del orden de cientos, cifra no publicada para anuncios) al ranking final. Se entrenan para imitar al ranking final (CTR + eventos de calidad) porque si no, "el early stage tiene un recall bajo, es decir, los mejores anuncios del ranking final quedan abajo en el early stage". Lattice se extendió a early-stage en abril-2025 (≈+4% conversiones FB Feed y Reels en Q2-2025). **[OFFICIAL META]** (paper 2307.11096; earnings Q2-2025)
- **Implicación:** anuncios con poca historia dependen de features semánticas para sobrevivir esta etapa; un creativo claro sobre qué es y para quién es tiene más opciones de pasar. **[STRONG INFERENCE]**

### Paso 5 — Late-stage (final) ranking
- Modelos runtime más pesados predicen probabilidades calibradas: CTR, CVR (por ventanas de atribución, Lattice Zipper), valor (value optimization) y **eventos de calidad** (ocultar, "no quiero ver esto", encuestas ASQ). Reciben conocimiento destilado de GEM (no se sirve GEM directamente). **[OFFICIAL META]**
- **Adaptive Ranking Model** (IG desde Q4-2025; offsite conversions Q1-2026): enruta peticiones a modelos más intensivos en cómputo "cuando determina que hay mayor probabilidad de conversión"; latencia acotada ~O(100 ms). **[OFFICIAL META]**
- Restricción de tiempo: "rankear miles de anuncios en unos pocos cientos de milisegundos" (Engineering, nov-2024). **[OFFICIAL META]**
- **El número de candidatos rankeados y el modelo usado varían según la capacidad sobrante** (Engineering, 12-oct-2026, *Turning Opportunistic AI Inference Capacity Into Better Ads Recommendations*): con capacidad ociosa, **Rank More Ads** amplía el conjunto de candidatos que evalúan las etapas de ranking (más carga también en retrieval y features) y **Serve Better Models** aumenta la fracción de peticiones puntuadas por un modelo más potente, priorizando las peticiones con mayor probabilidad predicha de engagement. Cuando la capacidad cae, se recorta primero el trabajo opcional de menor valor. Sin cifras de impacto publicadas. **[OFFICIAL META]**
- **Implicación:** la "profundidad" con la que Meta evalúa tu anuncio no es constante: depende de la hora, la región y el valor predicho de la petición. Las oportunidades de alto valor reciben más cómputo (coherente con ARM). **[STRONG INFERENCE]**
- **Selección de creativo dentro de un anuncio** (Flexible format, Dynamic creative, Advantage+ creative enhancements, catálogo): el sistema elige la combinación/variante por persona y placement; los "enhancements" no siempre se aplican, solo cuando se predice que mejoran el resultado (Loomer citando a Meta). **[OFFICIAL META]** vía practitioner.

### Paso 6 — Subasta
- Cada candidato superviviente obtiene un **total value** = f(puja efectiva × EAR, calidad). La puja efectiva la calcula el sistema de pacing según tu estrategia y presupuesto restante. Gana el mayor total value; el precio se fija con lógica tipo segundo precio/VCG (lo mínimo para ganar). **[OFFICIAL META]** (componentes) / **[STRONG INFERENCE]** (mecanismo de precio). Ver `02-subasta-total-value.md`.
- Auction overlap: si varios ad sets tuyos son elegibles, solo entra el de mayor total value. **[STRONG INFERENCE]**

### Paso 7 — Reglas post-subasta e integridad
- Reglas de negocio y de integridad (análogas a las del ranking orgánico de Explore: filtrar o degradar contenido dañino, diversidad para no mostrar seguidos del mismo autor). En anuncios, ejemplos documentados: **holdouts de Lift tests** ("justo antes de mostrar el anuncio, los anuncios del Lift test se retiran y se muestra el siguiente mejor anuncio de la subasta", Burtch et al. 2025 con investigadores de Meta) y el **Variance Reduction System** para anuncios de vivienda/empleo/crédito en EE. UU. (ajusta la entrega para reducir sesgos demográficos; acuerdo con el DOJ). **[OFFICIAL META]**

### Paso 8 — Impresión, interacción y feedback
- Se registra la impresión (billing) y cualquier interacción (clic, engaged view, like…). Las conversiones llegan después vía pixel/Conversions API/SDK/SKAdNetwork-AEM y se atribuyen según ventanas. **[OFFICIAL META]**
- Esas etiquetas: (a) entrenan los modelos de forma continua (GEM tiene entrenamiento online continuo), (b) actualizan los embeddings del usuario (disparados por conversiones), (c) alimentan el pacing (cuánto llevas gastado y a qué CPA), y (d) alimentan los diagnósticos (learning phase, relevance diagnostics). **[OFFICIAL META]** (a, b) + **[STRONG INFERENCE]** (c, d).

## 2. Diagrama mental (resumen)

```
[Usuario abre IG] → [Ranking orgánico + modelo de ad load: ¿hay hueco aquí? ¿en qué posición?]
      → [Petición de anuncio: usuario + contexto + superficie]
      → [Elegibilidad: segmentación, placement, presupuesto/pacing, política, experimentos, LPA]
      → [Retrieval: decenas de millones → miles (Andromeda, LLM/generativo, otros)]
      → [Early-stage ranking: miles → ~cientos (Lattice, modelos ligeros)]
      → [Late-stage ranking: CTR, CVR, valor, calidad (runtime models destilados de GEM, ARM)]
      → [Subasta: total value = f(puja efectiva × EAR, calidad); precio ≈ mínimo para ganar]
      → [Post-subasta: integridad, diversidad, holdouts, VRS]
      → [Impresión] → [Clic/conversión vía pixel/CAPI] → [Reentrenamiento continuo + embeddings + pacing]
```

## 3. Cómo se decide cada dimensión

| Dimensión | Quién/qué lo decide | Control del anunciante |
|---|---|---|
| **A quién** | Retrieval + ranking (EAR por persona) + subasta + segmentación como filtro | Indirecto: creativo (semántica), evento de optimización, señal; directo: restricciones duras (geo, edad mínima, exclusiones de custom audiences, idioma) |
| **Cuándo** | Modelo de ad load por sesión + pacing (puja efectiva varía durante el día/semana) | Programación horaria solo con presupuesto total; presupuesto diario se gasta como media semanal (hasta +75% un día, ≤7× semanal) |
| **Dónde (placement)** | Subastas por superficie + pacing | Cada vez menos: desde oct-2026 sin selección manual a nivel de ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09); quedan exclusiones a nivel de cuenta, value rules por placement (hasta −90%) y "limited spend" en excluidos (hasta 5% por placement, por defecto en Sales/Leads) |
| **Qué creativo** | Ranking por persona/placement; selección de assets en Flexible/Dynamic/Advantage+ creative | Qué creativos existen y cuán distintos son entre sí |
| **Con qué frecuencia** | Ad load + redistribución entre usuarios/sesiones + competencia de tus propios anuncios | Topes solo en objetivos de alcance/R&F; indirectamente vía tamaño de audiencia y diversidad creativa |
| **Cómo se gasta el presupuesto** | Pacing (bid pacing a nivel ad set o campaña con Advantage+ campaign budget) | Presupuesto, estrategia de puja, límites de gasto por ad set |
| **Qué explorar / explotar** | Ranking + learning phase + asignación de impresiones a anuncios nuevos | Volumen de anuncios nuevos y su diversidad; no tocar demasiado (las ediciones significativas reinician aprendizaje) |

## 4. Consecuencias prácticas del pipeline

1. **El creativo opera en tres etapas a la vez**: retrieval (¿me recuperan?), ranking (¿cuánto EAR y calidad?) y post-clic (¿convierte?). Un creativo bonito con poca claridad semántica falla en la primera; uno clickbait falla en la segunda (calidad) y la tercera (CVR). **[STRONG INFERENCE]**
2. **La concentración de gasto en 1-3 anuncios es el comportamiento esperado**, no un bug: el ranking predice EAR alto para ellos en la mayoría de personas y el pacing gasta donde el valor esperado por euro es mayor. Si el resto no recibe gasto, o son semánticamente redundantes (mismo "lugar" en retrieval) o su EAR predicho es inferior. Solución: conceptos realmente distintos, no apagar el ganador. CTC observa que el 3-5% de los anuncios concentra el 70-80% del gasto (observación propia de agencia). **[STRONG INFERENCE]** + **[EMPIRICAL]** (agencia).
3. **Cambios frecuentes rompen el bucle de feedback**: editar segmentación, creativos u optimización reinicia aprendizaje y altera la puja efectiva (Meta recomienda cambiar puja/presupuesto como mucho 2-3 veces al día y al principio del día). **[OFFICIAL META]** (Marketing API pacing).
4. **Las primeras etapas castigan lo nuevo sin historial**, pero 2025-2026 trae mitigación vía semántica (Semantic ID, LLM retrieval, features de contenido). Un anuncio nuevo "parecido en concepto" a un ganador hereda parte de su predicción; uno totalmente nuevo necesita exploración. **[OFFICIAL META]** + **[STRONG INFERENCE]**
5. **A/B tests de Meta reflejan entrega divergente**: cada variante se entrega a públicos distintos (181.890 A/B tests analizados por Meta + academia). Para aislar el efecto del creativo hay que igualar objetivo (reach), presupuesto, puja, calendario, audiencia y placements manuales; para medir impacto real, Lift tests (holdout). **[OFFICIAL META]**

## Implicaciones operativas

- Diseñar creativos pensando en **retrieval** (claridad semántica: producto, problema, persona, contexto) y en **ranking** (predicción de la acción optimizada, no del clic barato).
- Estructuras con **pocos ad sets y mucha señal**; evitar solapamientos.
- **No interpretar "no gasta" como "es malo"** sin mirar elegibilidad, retrieval (redundancia semántica) y competencia interna.
- Usar Lift/holdouts para decisiones de valor; usar A/B de Meta sabiendo que mide "anuncio + algoritmo", no "anuncio aislado".

## Errores frecuentes

- Pensar que la segmentación decide "a quién" y el algoritmo solo "cuánto pagar".
- Creer que el sistema prueba todos los anuncios por igual (no lo hace; explora de forma sesgada por predicción).
- Apagar el anuncio que concentra gasto para "forzar" a los demás: suele empeorar el CPA medio.

## Preguntas abiertas

- Número de candidatos que pasan del early-stage al late-stage en anuncios (Meta no lo publica; en Explore orgánico, ~100 al segundo stage).
- Cómo se combina exactamente la decisión de ad load (posición) con la subasta (¿subasta por posición o por hueco ya fijado?). Un email interno de 2020 sugiere precios dependientes de posición.
- Qué fracción del retrieval es ya generativo/LLM a finales de 2026.

## Fuentes clave

- [Meta Andromeda (Engineering)](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — 2024-12-02 — meta-engineering
- [Sequence learning (Engineering)](https://engineering.fb.com/2024/11/19/data-infrastructure/sequence-learning-personalized-ads-recommendations/) — 2024-11-19 — meta-engineering
- [Adaptive Ranking Model (Engineering)](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads/) — 2026-03-31 — meta-engineering
- [From User Sequences to Scaling Laws (Engineering)](https://engineering.fb.com/2026/08/05/ml-applications/from-user-sequences-to-scaling-laws-a-multi-stage-architecture-for-metas-ads-ranking/) — 2026-08-05 — meta-engineering
- [GEM 2026 (Engineering)](https://engineering.fb.com/2026/10/13/ml-applications/metas-generative-ads-model-gem-scaling-the-central-model-and-compute-engine-for-frontier-ads-ai) — 2026-10-13 — meta-engineering
- [Towards the Better Ranking Consistency (arXiv 2307.11096)](https://arxiv.org/abs/2307.11096) — 2023 — academico (Meta)
- [GRACE (arXiv 2608.00938)](https://arxiv.org/abs/2608.00938) — 2026-08 — academico (Meta)
- [LLM Retrieval for Stable and Predictable Ad Recommendations (arXiv 2605.21969)](https://arxiv.org/abs/2605.21969) — 2026-05 — academico (Meta)
- [Characterizing and Minimizing Divergent Delivery (arXiv 2508.21251)](https://arxiv.org/abs/2508.21251) — 2025-08 — academico (Meta)
- [Scaling the Instagram Explore recommendations system](https://engineering.fb.com/2023/08/09/ml-applications/scaling-instagram-explore-recommendations-system/) — 2023-08-09 — meta-engineering (análogo orgánico)
- [An Update on Our Ads Fairness Efforts (VRS)](https://about.fb.com/news/2023/01/an-update-on-our-ads-fairness-efforts/) — 2023-01 — meta-oficial
- [Marketing API – Pacing and scheduling](https://developers.facebook.com/docs/marketing-api/bidding/overview/pacing-and-scheduling) — vigente — meta-developers
- Earnings Q4-2024, Q2-2025, Q3-2025, Q4-2025, Q1-2026, Q2-2026 — meta-investors
