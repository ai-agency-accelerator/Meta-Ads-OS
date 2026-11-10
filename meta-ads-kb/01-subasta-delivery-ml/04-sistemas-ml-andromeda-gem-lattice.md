# Sistemas de ML de Meta Ads: Andromeda, GEM, Lattice, Adaptive Ranking, sequence learning, Semantic ID y Generative Recommender

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A01 (agente) · Ámbito: arquitectura pública del sistema de recomendación de anuncios de Meta (retrieval → ranking → subasta), cifras publicadas por Meta 2024-2026 y su traducción a decisiones de anunciante.

## TL;DR

- **El sistema es una cascada de modelos, no "un algoritmo".** Retrieval (Andromeda; desde Q2-2026 también un primer modelo generativo/LLM) reduce "decenas de millones" de anuncios candidatos a "unos pocos miles"; después varios modelos de ranking (early-stage y late-stage) predicen CTR/CVR/calidad y alimentan la subasta. Los modelos gigantes (GEM) **no** sirven anuncios en tiempo real: enseñan (destilan) a modelos runtime más ligeros. **[OFFICIAL META]** (Engineering dic-2024; earnings Q2-2025, Q4-2025).
- **Andromeda = retrieval, no ranking.** Decide qué anuncios llegan a competir, no cuál gana. Si un anuncio no sobrevive retrieval para una persona, ni la puja ni la calidad en la subasta importan para esa impresión. **[OFFICIAL META]**
- **GEM = foundation model "cerebro central" del ranking**, entrenado con datos de anuncios y orgánico de Facebook+Instagram; Meta atribuye +5% conversiones en Instagram y +3% en Facebook Feed/Reels en Q2-2025, y en su versión 2026 (+18,9% conversiones y +12% CTR "a través de superficies y objetivos", cifra agregada interna). **[OFFICIAL META]** (cifras autoinformadas, sin metodología externa).
- **Lattice = consolidación de modelos** (multi-dominio, multi-objetivo): Meta ha eliminado ~100 modelos de ranking desde 2023 y planea consolidar ~200 más. Consecuencia práctica: lo que aprende el sistema en un objetivo/superficie se transfiere a otros; la fragmentación del anunciante pierde valor relativo. **[OFFICIAL META]** + **[STRONG INFERENCE]** para la implicación.
- **Las predicciones de los modelos de ranking se usan directamente para el precio de la subasta.** El paper LLaTTE (Meta, 2026) lo dice explícito: probabilidades calibradas de CTR/CVR "se utilizan tanto para el ranking como para el pricing de la subasta". Mejor predicción de conversión ⇒ el sistema puede cobrar más por impresión de alto valor (CPM sube, CPA puede bajar). **[OFFICIAL META]** (paper de autores de Meta).
- **"Entity ID"/"creative similarity" no es folklore puro, pero el nombre sí lo es.** Meta confirma oficialmente que "cuando los creativos son demasiado parecidos, nuestro sistema puede no reconocerlos como creativos distintos" y los entrega al mismo público (Meta for Business, página de *creative differentiation*). La base técnica pública es **Semantic ID** (Meta, RecSys'25): agrupa anuncios por similitud de contenido (texto/imagen/vídeo) y reduce en un 43% la diferencia de predicción entre copias casi idénticas. El término "Entity ID" no aparece en documentación pública de Meta que haya podido verificar. **[OFFICIAL META]** para el mecanismo; **[HYPOTHESIS]** para umbrales concretos (p. ej. "65% similarity score" reportado por practitioners tras reunión con Meta, feb-2026).
- **Duplicar anuncios para "sacar otra tirada" es una táctica en vías de extinción.** Meta documentó que con hashing aleatorio de IDs, una copia exacta de un anuncio recibía predicciones y entrega distintas ("A/A variance") y está eliminando activamente esa varianza (Semantic ID −43% AAR; retrieval con LLM −8,62% diferencia A/A' y −45% MAD de impresiones). **[OFFICIAL META]** (papers 2025-2026).
- **Más contexto del usuario = más poder del sistema, menos del segmentador.** Secuencias de comportamiento de miles de eventos (orgánico + anuncios), con leyes de escala tipo LLM "sin señales de saturación". La ventaja del anunciante ya no está en saber "quién" sino en dar al sistema creativos semánticamente distintos y señales de conversión de calidad. **[OFFICIAL META]** + **[STRONG INFERENCE]**.
- **2026 es el año de los LLM dentro del sistema de anuncios**: Adaptive Ranking Model (modelo runtime "LLM-scale", Instagram desde Q4-2025, offsite conversions Q1-2026), GEM 2026 (arquitectura Kunlun), y "Meta Generative Recommender" (Q2-2026: LLMs razonando sobre contenido del anuncio + preferencias del usuario, primer modelo generativo en retrieval). **[OFFICIAL META]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Q3-2026 (21-oct)**: retrieval generativo en el Feed de Facebook (~+2 % de conversiones en los segmentos objetivo); GEM en más superficies (+1,7 % de conversiones offsite, +9,6 % en apps); Andromeda +1,4 % en Facebook. **[OFFICIAL META]**
> - Fuentes: S10-117 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Mapa general: qué sistema hace qué

| Sistema | Etapa | Qué hace | Desde | Cifras publicadas por Meta | Fuente |
|---|---|---|---|---|---|
| **Andromeda** | Retrieval (y desde Q3-2025 fusionado con early-stage ranking en Facebook) | Selecciona miles de candidatos de entre decenas de millones con una red neuronal + índice jerárquico entrenados conjuntamente | 2S-2024 | +6% recall, +8% ads quality (segmentos seleccionados), 10.000× capacidad de modelo; Q2-2025 ~+4% conversiones FB mobile Feed y Reels; Q3-2025 +14% ads quality en Facebook al combinar retrieval + early-stage ranking; Q4-2025 ~3× eficiencia de cómputo (Nvidia/AMD/MTIA) | Engineering dic-2024; earnings Q4-2024, Q2/Q3/Q4-2025 |
| **Sequence learning** (EBFs, transformers sobre eventos) | Ranking | Sustituye features agregadas a mano (p. ej. "clics en últimos N días") por secuencias ordenadas de eventos | 2024 | +2-4% conversiones en segmentos seleccionados | Engineering nov-2024 |
| **GEM** (Generative Ads Recommendation Model) | Ranking (foundation model "profesor") | Modelo base gigante que transfiere conocimiento a los modelos verticales/runtime | Q1-2025 (Reels), todas las superficies FB+IG en Q4-2025 | Q2-2025: ~+5% conv. IG, ~+3% FB Feed/Reels; 4× eficiencia vs. modelos previos; 2× eficacia de transferencia; Q4-2025 (con sequence learning): +3,5% clics FB, >+1% conv. IG; 2026: +18,9% conv., +12% CTR | Engineering nov-2025 y oct-2026; earnings |
| **Lattice** | Ranking (late-stage desde 2023, early-stage desde abr-2025) | Unifica modelos de múltiples dominios (superficies) y objetivos; maneja ventanas de atribución y feedback retrasado | 2023 | Paper: +10% métricas top-line de ingresos, +11,5% ads quality/satisfacción, hasta +6% CVR, −20% capacidad; Q2-2025 ~+4% conv. FB Feed/Reels; Q3-2025 app ads ~+3% conv.; Q4-2025 +12% ads quality (consolidación Facebook Stories); Q1-2026 (con GEM) >+6% CVR en anuncios de landing page view | arXiv 2512.09200; earnings |
| **Run-time model nuevo / Adaptive Ranking Model** | Ranking en inferencia | Modelo de inferencia "LLM-scale" que enruta peticiones a modelos más caros cuando la probabilidad de conversión es alta | Piloto Q3-2025; IG Feed/Stories/Reels Q4-2025; offsite conversions Q1-2026 | Q3-2025 piloto >+2% conv. IG; Q4-2025 +3% CVR IG; blog: +3% conv. y +5% CTR en "targeted users"; Q1-2026 +1,6% CVR FB+IG offsite | Earnings; Engineering mar-2026 |
| **LLaTTE** (multi-stage sequence model) | Ranking (modelo de usuario upstream + ranker online) | Transformer profundo offline que precalcula embeddings de usuario, refrescados tras eventos de alto valor (conversiones) | 2025-2026 | ~0,25% NE ⇒ +4,3% conversiones FB Feed y Reels; acumulado con otras mejoras: +6% conv. IG, +3% conv. FB, +3,5% clics FB | arXiv 2601.20083; Engineering ago-2026 |
| **Semantic ID** | Ranking (features) | Sustituye IDs aleatorios de anuncio por IDs semánticos derivados del contenido | 2024-2025 | +0,15% métrica top-line online; −43% diferencia de predicción entre copias (AAR) | arXiv 2504.02137 (RecSys'25) |
| **LLM retrieval semántico** | Retrieval | LLM (Llama 3-8B) extrae atributos semánticos jerárquicos del creativo; grafo de anuncios similares | 2025-2026 | +0,45% métrica top-line; +1,2% recall final; −8,62% diferencia A/A'; −45% MAD de impresiones entre pares | arXiv 2605.21969 (SIGIR'26 workshop) |
| **Meta Generative Recommender** | Retrieval (primer despliegue) | LLMs que razonan conjuntamente sobre contenido del anuncio y preferencias del usuario para "predecir el mejor anuncio" en vez de puntuar cada anuncio individualmente | Q2-2026 | Pilotos: +1% conversiones de app events en IG; combinado con GEM + sequence learning: +8,3% clics y +15,7% conversiones en Facebook (Q2-2026) | Earnings Q2-2026 |
| **GRACE** | Retrieval generativo (serving) | Motor de inferencia para retrieval generativo con Semantic IDs que respeta la segmentación del anunciante (Generative Target Matching) | ago-2026 (paper) | Pass rate de segmentación 23,55% → 40,42%; latencia decoder −11,1× | arXiv 2608.00938 |
| **REA** (Ranking Engineer Agent) | Ingeniería interna | Agente autónomo que ejecuta ciclos de experimentación ML de ranking | mar-2026 | "Duplicó la precisión media del modelo sobre baseline" en 6 modelos | Engineering mar-2026 |
| **MTIA** | Hardware | Chip propio para inferencia (2024) y entrenamiento de ranking/recomendación (2026) | 2024 | Andromeda corre en Nvidia, AMD y MTIA desde Q4-2025 | Earnings Q4-2024, Q4-2025 |

> **Nota de rigor:** todas las cifras de lift son **autoinformadas por Meta** (earnings, blogs, papers de empleados). No hay auditoría externa. Suelen medirse en "targeted users", "segmentos seleccionados" o superficies concretas, y no son sumables. Úsalas como **dirección y orden de magnitud**, nunca como expectativa para una cuenta concreta.

---

## 2. Andromeda (retrieval) — qué es y qué no es

### 2.1 Qué publicó Meta (Engineering, 2-dic-2024)

- Retrieval es "el primer paso" del sistema multi-etapa: selecciona de "decenas de millones de anuncios candidatos" a "unos pocos miles". Maneja ~3 órdenes de magnitud más anuncios que las etapas posteriores y tiene latencia muy ajustada.
- Arquitectura: red neuronal profunda propia con "coste de inferencia sublineal"; **índice jerárquico** de anuncios entrenado conjuntamente con el modelo (mejor que two-tower + ANN clásicos); "elasticidad" de modelo: los segmentos de anuncios de alto valor reciben modelos más complejos y la complejidad se ajusta en tiempo real según recursos disponibles.
- Hardware: NVIDIA Grace Hopper + MTIA. Features de usuario-anuncio reconstruidas "on the fly" en GPU en vez de depender de features diseñadas a mano.
- Resultados: +6% recall, +8% ads quality en segmentos seleccionados, 10.000× capacidad de modelo, 10× eficiencia de inferencia, >3× QPS.
- Motivación declarada explícitamente: Advantage+ (automatización de audiencia/presupuesto/puja) **aumenta el número de anuncios elegibles por petición**, y la IA generativa multiplica el volumen de creativos. Retrieval era el cuello de botella.
- Dirección futura: pasar a una pérdida autoregresiva que "podría producir un conjunto más diverso de candidatos".

### 2.2 Evolución posterior (earnings)

- **Q4-2024:** "aumento de 10.000× en la complejidad de los modelos de retrieval", "+8% en la calidad de los anuncios que la gente ve en los objetivos probados".
- **Q2-2025:** mejoras para seleccionar candidatos "más relevantes y más personalizados" y expansión a Facebook Reels: "casi +4% conversiones en Facebook mobile Feed y Reels".
- **Q3-2025:** "combinando modelos de retrieval y early stage ranking en un único modelo, +14% ads quality en superficies de Facebook". → Importante: la frontera entre "retrieval" y "ranking" se está difuminando.
- **Q4-2025:** Andromeda funciona en Nvidia, AMD y MTIA; "casi triplicar la eficiencia de cómputo".

### 2.3 Qué significa para el anunciante

1. **La primera barrera es semántica, no de puja.** Si tus anuncios no son recuperados para una persona, no compiten. Retrieval decide a partir de la representación del anuncio (contenido, señales históricas) y del usuario. Un creativo que "habla" a un tipo de persona concreto es recuperado para personas parecidas; diez variaciones casi idénticas ocupan esencialmente el mismo lugar en ese espacio. **[STRONG INFERENCE]** a partir del diseño de índice jerárquico + Semantic ID + página oficial de creative differentiation.
2. **Andromeda no "mató" la segmentación por decreto**, pero hace que la segmentación manual sea, en la práctica, un **filtro de elegibilidad** sobre un sistema que ya personaliza a nivel individuo. **[STRONG INFERENCE]**
3. **"Andromeda update" como evento único de 2025 es folklore.** Meta lo introdujo en 2S-2024 y lo ha ido iterando trimestralmente (Q2, Q3, Q4-2025). Los cambios de rendimiento que practitioners atribuyen a "la actualización de Andromeda de octubre de 2025" pueden coincidir con alguna de esas iteraciones, pero Meta no ha anunciado un "update" con fecha concreta que yo haya podido verificar. Jon Loomer (ago-2025) advierte que "Andromeda" se usa como cajón de sastre. **[CONTESTED]** / **UNPROVEN** como evento puntual.
4. **Andromeda no elige ganadores.** El ganador lo deciden los modelos de ranking + subasta. Atribuir a Andromeda la concentración de gasto en un anuncio es impreciso (eso es ranking + pacing + exploración). **[OFFICIAL META]** (separación de etapas).

---

## 3. Sequence learning (nov-2024) y LLaTTE (2026)

### 3.1 Qué cambió

- Antes (DLRM clásico): features dispersas agregadas en ventanas (p. ej. "anuncios clicados en los últimos N días", "páginas visitadas con conteos"). Pierden **orden**, **detalle** de atributos del mismo evento y patrones no intuitivos.
- Ahora: **Event-Based Features** (stream de eventos + longitud de secuencia + información del evento: categoría del anuncio, timestamp…), modelo de eventos (embeddings tipo "palabra") y modelo de secuencia con atención **condicionada al anuncio que se está puntuando**. Meta: +2-4% conversiones en segmentos seleccionados (nov-2024). Plan: escalar secuencias 100×.
- **Q2-2025:** se duplicó la longitud de secuencias de eventos usadas en GEM. **Q1-2026:** se duplicó la longitud de secuencias de interacción en Instagram. **Q2-2026:** se enriquecen las secuencias con descripción más granular del contenido (vía LLMs).
- **LLaTTE (arXiv 2601.20083, Meta):** el rendimiento sigue leyes de potencia como los LLM; las **features semánticas de contenido "doblan la curva de escala"** (son prerequisito para aprovechar modelos más grandes). En producción: modelo de usuario upstream (secuencias de 500-5.000 acciones en experimentos), ejecutado en clúster H100 de forma asíncrona y **disparado por eventos de alto valor, principalmente conversiones**; el ranker online usa ~400 eventos por fuente + el embedding cacheado. Resultado: +4,3% conversiones en Facebook Feed y Reels, "del orden de cientos de millones de dólares de ingresos anuales".
- **Engineering (5-ago-2026):** una mezcla equilibrada de tipos de acción (views, clicks, conversions) supera a secuencias de un solo tipo; la curva "no muestra señales de saturación"; las features semánticas de foundation models ayudan a anuncios nuevos/anunciantes con poco engagement (cold start).

### 3.2 Implicaciones

- **El sistema modela la trayectoria de cada persona (orgánico + anuncios + conversiones), no "segmentos".** Un interés declarado en Ads Manager es una señal pobre comparada con miles de eventos ordenados. Por eso la segmentación por intereses aporta cada vez menos información incremental al modelo. **[STRONG INFERENCE]**
- **Las conversiones refrescan la representación del usuario.** El embedding upstream se recalcula tras conversiones: cada evento de conversión que envías (pixel/CAPI) no solo entrena el modelo, sino que actualiza la "foto" del usuario para todos los anunciantes. Señales de conversión limpias, deduplicadas y rápidas tienen más valor que nunca. **[OFFICIAL META]** (mecanismo) + **[STRONG INFERENCE]** (implicación).
- **El contenido del creativo entra como feature semántica.** El sistema "entiende" de qué va el anuncio (texto, imagen, vídeo; desde 2026 también vía LLM). Esto es lo que permite que un anuncio nuevo arranque sin historial (cold start más corto si se parece semánticamente a anuncios que funcionaron) — y también lo que hace que clones superficiales no añadan cobertura. **[OFFICIAL META]** + **[STRONG INFERENCE]**.

---

## 4. GEM (Generative Ads Recommendation Model)

### 4.1 Versión 2025 (Engineering, 10-nov-2025; earnings)

- "El foundation model de anuncios más avanzado de Meta, construido sobre un paradigma inspirado en LLM y entrenado en miles de GPUs"; según Meta, "el mayor foundation model para RecSys de la industria".
- Arquitectura: features secuenciales (historial) y no secuenciales (edad, ubicación, formato del anuncio, representación del creativo) con atención propia; Wukong + factorization machines apilables; **InterFormer** (alterna aprendizaje de secuencia e interacción cruzada sin comprimir el historial a un vector pequeño). Secuencias de "hasta miles de eventos".
- **Aprendizaje multi-dominio:** "el engagement con vídeo de Instagram puede ayudar a predecir resultados en Facebook Feed".
- **No sirve en tiempo real.** Susan Li (Q4-2025): "No usamos normalmente nuestras arquitecturas grandes como GEM para inferencia porque su tamaño y complejidad lo harían prohibitivo… transferimos conocimiento a modelos ligeros usados en runtime". Transferencia directa e **jerárquica** (GEM → foundation models de dominio → modelos verticales), **Student Adapter** que corrige al "profesor" con datos recientes; "2× la eficacia de la destilación estándar".
- **Entrenamiento continuo online** (a diferencia de LLMs).
- Cifras: Q1-2025 en Reels "hasta +5% conversiones" (prensa, Marketing Dive); Q2-2025 ~+5% conversiones IG y ~+3% Facebook Feed y Reels; 4× más eficiente por unidad de datos/cómputo; Q3-2025 cambios de arquitectura "duplicaron el beneficio" de añadir datos/cómputo; Q4-2025 se extiende a Facebook Reels (ya cubre "todas las superficies principales de FB e IG") y se duplica el clúster de GPUs.
- Dirección declarada: multimodal (texto, imagen, audio, vídeo), modelo unificado orgánico + anuncios, razonamiento con escalado en inferencia, "automatización agéntica del anunciante".

### 4.2 Versión 2026 (Engineering, 13-oct-2026)

- Pasa de modelos por dominio (Facebook, Instagram, Reels) a **un único foundation model central** que predice conjuntamente CTR en todas las superficies y CVR en los principales objetivos de optimización.
- Cifras: +18,9% conversiones y +12% CTR "a través de superficies y objetivos"; uplift de conversiones en usuarios objetivo en el último año: +5,8% Facebook, +4,1% Instagram, +1,6% off-site. Arquitectura **Kunlun** (2× rendimiento vs InterFormer a igual cómputo), complejidad 2,5×, contexto largo 2× en producción (demostrado hasta 25×), **LoopFM** (transferencia post-training que duplica la "transferencia de inteligencia" sin coste de latencia), **Solaris** (precomputación especulativa de embeddings usuario-anuncio; si falta el exacto, usa embeddings de usuarios similares).

- **Entrenamiento (Engineering, 3-ago-2026, *GEM Training: How Meta Doubled the Efficiency…*)**: GEM entrena "a escala LLM" en varios miles de GPUs de última generación; la eficiencia se duplicó hasta 20-25% de MFU mientras los FLOPs de entrenamiento se multiplicaron por 4 en 12 meses (kernels propios, MXFP8, paralelismo 5D). Meta subraya que la infraestructura de LLMs "no se transfiere directamente" a modelos de recomendación. **[OFFICIAL META]**
- **Malinterpretación frecuente:** titulares como "GEM ahora ejecuta cada subasta con un solo modelo" (prensa especializada, oct-2026) confunden el foundation model "profesor" con los modelos runtime que puntúan cada petición. Meta (Q4-2025) dice explícitamente que no sirve GEM en inferencia por coste. **[OFFICIAL META]**

### 4.3 Implicaciones de GEM para el anunciante

- **Un foundation model compartido entre todos los anunciantes reduce la ventaja de "datos propios en la plataforma".** Lo que el sistema aprende de millones de anunciantes y miles de millones de usuarios ya está en el profesor; tu cuenta aporta (a) señales de conversión propias, (b) creativos, (c) restricciones. **[STRONG INFERENCE]**
- **Multi-superficie = placements automáticos ganan sentido.** Si el modelo aprende de IG para predecir FB y viceversa, restringir placements te quita inventario sin quitar al modelo información. Excepciones: creativos inadecuados para un formato, brand safety, o cuando un placement trae calidad de conversión peor demostrada con incrementalidad. **[STRONG INFERENCE]**
- **Los lifts de "conversiones" no implican necesariamente CPA más bajo para ti.** Si todos los anunciantes mejoran su tasa de conversión, el precio por impresión sube (subasta). Meta lo dijo en Q4-2024: mejorar conversiones "tiene el efecto de seguir elevando los CPM… porque entregamos más conversiones por impresión". **[OFFICIAL META]**

---

## 5. Lattice (paper arXiv 2512.09200, dic-2025; earnings)

- Problema: miles de pares dominio-objetivo ("portfolios") con un modelo dedicado cada uno; datos fragmentados; feedback retrasado (las conversiones llegan "de minutos a días" después de la impresión).
- Componentes:
  - **Partitioner:** agrupa portfolios; separa feedback denso y rápido (clic, like, follow) del retrasado y escaso (compra, conversión).
  - **Zipper:** asigna cada impresión a **una ventana de atribución** (aleatoriamente vía hashing) con cabezas de predicción por ventana (90 minutos, 1 día, 7 días); en serving usa la cabeza "oráculo" de ventana más larga. → El sistema está diseñado explícitamente para equilibrar frescura vs corrección de la etiqueta de conversión.
  - **Filter:** selección de features Pareto-óptima (~2K de 12K).
  - **Networks** y **KTAP** (profesores que precalculan embeddings usuario-ítem con TTL ~6h).
- Resultados: +10% métricas top-line de ingresos, +11,5% satisfacción/ads quality, hasta +6% CVR, −20% capacidad.
- Earnings: Lattice desplegado en late-stage ranking desde 2023, en early-stage desde abril 2025; Q3-2025 "hemos reducido el número de modelos de ranking y recomendación de anuncios en ~100" y se consolidarán "otros 200 en los próximos años"; Q4-2025 consolidación de Facebook Stories en el modelo general de Facebook (+12% ads quality); "en 2026 esperamos consolidar más modelos que en los dos años anteriores".

**Implicaciones:**
- **Ventanas de atribución ≠ ventanas de aprendizaje.** Lattice entrena con varias ventanas (90 min, 1 día, 7 días). Cambiar la ventana de atribución del ad set cambia qué conversiones cuentan para la optimización, pero el modelo interno ya contempla conversiones retrasadas. **[OFFICIAL META]** (mecanismo del paper) + **[HYPOTHESIS]** sobre cuánto influye exactamente la ventana elegida por el anunciante.
- **Eventos raros se benefician del aprendizaje compartido.** Un objetivo con pocas conversiones (p. ej. lead cualificado) toma prestado aprendizaje de objetivos densos. Esto explica por qué el sistema puede optimizar con menos de "50 conversiones/semana" mejor que en 2019, aunque el volumen sigue importando para el ajuste fino de tu cuenta. **[STRONG INFERENCE]**

---

## 6. Run-time models y Adaptive Ranking Model (ARM)

- Q3-2025: piloto de un nuevo modelo runtime "que usa más cómputo y datos" → >+2% conversiones en IG en test.
- Q4-2025: lanzado en IG Feed, Stories y Reels → +3% tasa de conversión.
- Engineering (31-mar-2026): **ARM** sirve modelos de ranking de complejidad "LLM-scale" (~O(10 GFLOPs) por token, escala O(1T) parámetros) con latencia acotada ~O(100 ms). Clave: **enrutamiento inteligente de peticiones** y cálculo de señales de usuario una vez por petición (no por anuncio candidato). +3% conversiones, +5% CTR en "targeted users" de IG.
- **Q1-2026 (Susan Li):** ARM "mejora el ROI de inferencia enrutando las peticiones a modelos de inferencia más intensivos en cómputo **cuando determina que hay una mayor probabilidad de conversión**". Cobertura ampliada a conversiones off-site: +1,6% CVR en las principales superficies de FB e IG.

**Implicación:** Meta gasta más cómputo en las impresiones con mayor probabilidad de conversión. Es decir, la precisión del sistema no es uniforme: es mayor justo donde hay más dinero en juego. Para el anunciante, las oportunidades de alta intención están mejor evaluadas (y probablemente mejor preciadas) que el inventario marginal. **[OFFICIAL META]** (mecanismo) + **[STRONG INFERENCE]** (consecuencia).

---

## 7. Semantic ID, A/A variance y la base técnica de la "creative similarity"

### 7.1 El problema que Meta documentó

Paper **"Enhancing Embedding Representation Stability in Recommendation Systems with Semantic ID"** (Zheng et al., Meta + Columbia, arXiv 2504.02137, abr-2025, RecSys'25):
- **ID drifting:** en el corpus de anuncios, "la mitad del corpus original sale del sistema tras 6 días" y entra un número igual de anuncios nuevos.
- **Impression skew:** pocos anuncios concentran la mayoría de impresiones/conversiones.
- Con **random hashing**, varios anuncios comparten embedding de forma aleatoria → "contaminación", aprendizaje perdido al rotar anuncios, embeddings de anuncios nuevos "esencialmente aleatorios".
- **A/A variance:** "se puede crear una copia de un anuncio con un ID distinto… como los embeddings serán distintos tras el hashing, las predicciones del modelo y el comportamiento del sistema de entrega también diferirán". Y la variante **A/A'**: "dos imágenes con el mismo objeto en primer plano pero fondos de distinto color".
- Solución: **Semantic ID** — IDs derivados de clustering jerárquico del contenido (texto, imagen, vídeo). "Copias exactas o ítems muy similares a menudo tendrán el mismo prefijo de Semantic ID". Resultado en producción: features de Semantic ID entre las de mayor importancia, +0,15% métrica top-line online y **−43% en la diferencia relativa de predicción entre copias (AAR)**. Las ganancias vienen sobre todo de la cola larga (anuncios con pocas impresiones) y de anuncios nuevos.

### 7.2 Retrieval con LLM para estabilidad (arXiv 2605.21969, Meta, may-2026)

- Meta define formalmente **predictibilidad = diferencia A/A'** entre un anuncio "primario" y una copia "sombra" con una perturbación menor, y la usa como guardarraíl de desarrollo.
- Llama 3-8B extrae atributos semánticos jerárquicos de los creativos; se construye un grafo de anuncios (similitud Jaccard) y se expanden candidatos desde anuncios semilla.
- Objetivo explícito: "garantizar que **pequeñas variantes creativas del anunciante produzcan resultados de entrega consistentes y explicables**".
- Resultados A/B online: +0,45% métrica top-line, +1,2% recall final, **−8,62% diferencia A/A'** y **−45% en MAD de la diferencia diaria de impresiones** entre pares.

### 7.3 Lo que dice Meta oficialmente a los anunciantes

- Página *Maximize conversions with differentiated ad creative* (Meta for Business, vigente 2026): "Cuando los creativos son demasiado parecidos, nuestro sistema puede no reconocerlos como creativos distintos" y puede mostrarlos al mismo público; "este solapamiento limita tu alcance" y puede activar los estados **"Creative limited"** o **"Creative fatigue"** en la columna de Entrega.
- *The Creative Advantage: Unlocking the Power of Diversification with Meta Andromeda* (22-abr-2025): la palanca principal se ha desplazado "de la segmentación de nicho a la diversificación creativa"; "la mayor restricción que puedes poner a tu estrategia en Meta es la que pones a tu proceso creativo".
- *Three steps to optimize your performance with creative diversification* (19-nov-2024): mantener **al menos 20 anuncios diversificados** en Advantage+ shopping, dedicar **20-30% del presupuesto a testar anuncios nuevos**, lanzar anuncios nuevos semanalmente, "olvida la idea del anuncio perfecto".

### 7.4 Veredicto sobre el folklore

| Afirmación de practitioners | Veredicto | Comentario |
|---|---|---|
| "Meta agrupa anuncios similares y los trata como uno (Entity ID)" | **CONTEXT-DEPENDENT / parcialmente TRUE** | El mecanismo (similitud semántica → predicciones y entrega parecidas al mismo público) está documentado. "Entity ID" no es término público verificado de Meta; no hay evidencia pública de que se fusionen literalmente en "un ticket" de subasta. |
| "Hay un similarity score y por encima del 65% se canibalizan" | **UNPROVEN** | Reportado por Growth Collective (11-feb-2026) tras reunión con reps de Meta; según el autor, solo accesible vía rep para cuentas gestionadas y "direccional". No verificable públicamente. |
| "Duplicar el ad set/anuncio ganador da otra oportunidad" | **OUTDATED** (en declive) | Funcionaba en parte por varianza aleatoria A/A. Meta la está reduciendo deliberadamente (−43% AAR, −8,62% A/A'). Foxwell (oct-2026) reporta que duplicar con retoques menores da ~5-10% más entrega, no escala (anecdótico). |
| "Cambiar el color de fondo / el hook mínimo crea un anuncio nuevo para el sistema" | **FALSE** como estrategia de diversificación | Es literalmente el ejemplo de A/A' de Meta. |
| "Hay que lanzar 50 anuncios por ad set" | **UNPROVEN / CONTEXT-DEPENDENT** | Meta recomienda ≥20 diversificados en ASC (2024) y retiró el límite recomendado de 6 anuncios por ad set (feb-2025, según Loomer). Volumen sin diversidad semántica no añade cobertura. |

---

## 8. Meta Generative Recommender y LLMs en el sistema (2026)

- **Q2-2026 (earnings, 29-jul-2026):** "Introdujimos Meta Generative Recommender, un cambio de paradigma en cómo funciona nuestro sistema de anuncios. En vez de puntuar cada anuncio posible individualmente, usamos LLMs para razonar sobre el contenido del anuncio y las preferencias del usuario conjuntamente, y predecir el mejor anuncio para cada persona. Desplegamos el primer modelo generativo en nuestro sistema de retrieval". Pilotos con LLMs para entender preferencias: +1% conversiones de app events en IG. Modelos de comprensión de usuario (orgánico + anuncios) + GEM + sequence learning: **+8,3% clics y +15,7% conversiones en Facebook**.
- Zuckerberg (Q2-2026): "Usamos LLMs para mejorar cómo nuestros sistemas predicen y rankean los anuncios… hemos ampliado el contexto que podemos tener en cuenta sobre la actividad orgánica y de anuncios de una persona".
- Orgánico (relevante porque comparte infraestructura): todo post público de Reels y Feed en Instagram se procesa con un LLM (temas, tono…); en IG Feed más de la mitad del contenido recomendado tiene <1 día; Meta trabaja en foundation models que sirvan **orgánico y anuncios simultáneamente** y en "recomendadores LLM-nativos" (primer hito: preentrenamiento continuo con datos de recomendación con leyes de escala sanas).
- **GRACE** (arXiv 2608.00938, Meta, ago-2026): retrieval generativo con Semantic IDs; el reto explícito es que cada anuncio generado **cumpla la segmentación del anunciante** (Generative Target Matching). → La segmentación manual sigue existiendo como restricción dura que el sistema debe respetar, y es un coste para el sistema.

**Implicaciones:**
- La comprensión del **contenido** del anuncio por un LLM es ya una entrada de retrieval. El copy, la promesa, el producto y el "para quién" explícitos del creativo pasan a ser señales de targeting. **[OFFICIAL META]** (dirección) + **[STRONG INFERENCE]**.
- Restricciones de segmentación estrechas reducen el espacio que el retrieval generativo puede explorar (GRACE trata la elegibilidad como filtro). **[STRONG INFERENCE]**

---

## 9. Infraestructura y capex (por qué todo esto se acelera)

- Capex 2024 ≈ $39B; 2025 = $72,2B (con arrendamientos financieros); guía 2026 = **$130-145B** (Q2-2026; antes $115-135B en enero y $125-145B en abril). **[OFFICIAL META]**
- MTIA en inferencia de ranking y recomendación desde 2024; entrenamiento de ranking/recomendación desde Q1-2026; **MTIA 300** presentado el 24-ago-2026 como "primer chip de entrenamiento de Meta con NICs integradas" (Engineering). **[OFFICIAL META]**
- Capacidad oportunista (Engineering, 12-oct-2026): la capacidad de inferencia ociosa se usa para rankear más anuncios por petición o servir modelos más potentes en peticiones de alto valor. **[OFFICIAL META]**
- Susan Li (Q4-2025): "Es la primera vez que encontramos una arquitectura de modelo de recomendación que escala con una eficiencia similar a los LLMs". **[OFFICIAL META]**

**Implicación estratégica:** la mejora del sistema es un proceso continuo (lanzamientos trimestrales), no "updates" discretos. Las cuentas verán cambios de comportamiento (concentración de gasto, CPMs, distribución por placement) sin anuncio público. Diagnosticar "cambió el algoritmo" sin aislar factores propios (creativo, oferta, estacionalidad, tracking) es un error. **[STRONG INFERENCE]**

---

## Implicaciones operativas

1. **Diversidad creativa semántica > volumen.** Cada anuncio nuevo debe cambiar al menos una de: ángulo/promesa, persona/motivación, formato, escena/contexto de uso, prueba (demo, testimonio, UGC, comparativa). Variaciones de color, fondo, hook mínimo o titular no cuentan como "nuevo anuncio" para el sistema. **[OFFICIAL META]**
2. **No duplicar ad sets/anuncios como táctica de escalado.** Si necesitas más entrega, sube presupuesto en la estructura existente o añade conceptos nuevos. **[OFFICIAL META]** (A/A variance en declive) + **[EMPIRICAL]** anecdótico.
3. **Consolidar estructura**: menos ad sets con más señal cada uno; el sistema aprende transversalmente (Lattice/GEM). **[STRONG INFERENCE]**
3b. **Consolidar cuentas publicitarias**: repartir el mismo negocio en varias cuentas no crea "aprendices independientes": los modelos son globales, las features de anunciante (página, dominio, pixel, historial) y la calidad se evalúan también a nivel de página/dominio (contagio de baja calidad oficial), y las campañas de varias cuentas del mismo negocio compiten entre sí por las mismas personas. Separar cuentas solo tiene sentido por razones operativas, legales, de facturación o de riesgo de cuenta (área 08). **[STRONG INFERENCE]** (no hay documentación pública sobre deduplicación entre cuentas del mismo anunciante → **[HYPOTHESIS]** sobre si Meta evita la auto-competencia entre cuentas).
4. **Señales de conversión: calidad, rapidez y valor.** Conversiones disparan la actualización de embeddings del usuario; los modelos predicen CVR por ventana. Enviar eventos tarde, duplicados o de baja calidad (leads basura) enseña al sistema a buscar lo que no quieres. **[STRONG INFERENCE]**
5. **Placements y audiencias amplias como default**, y restricciones solo con razón de negocio demostrada (incrementalidad, brand safety, operativa). **[STRONG INFERENCE]**
6. **No sobre-interpretar los lifts de Meta.** Son medias en segmentos; tu CPA depende también de la competencia (que recibe las mismas mejoras). **[OFFICIAL META]** + **[STRONG INFERENCE]**

## Errores frecuentes

- Llamar "Andromeda" a todo cambio de rendimiento.
- Creer que GEM "decide en tiempo real" (decide a través de modelos destilados).
- Interpretar "creative diversification" como "subir 50 variaciones del mismo vídeo".
- Usar el lift publicado por Meta (+5%, +15,7%…) como previsión de mejora de CPA propia.
- Asumir que segmentar estrecho "ayuda al algoritmo": en un sistema con secuencias de miles de eventos, suele restar inventario sin añadir información.

## Preguntas abiertas

- ¿Cómo se pondera exactamente la similitud semántica entre anuncios del **mismo anunciante** frente a anunciantes distintos? ¿Hay deduplicación explícita en retrieval o solo efecto emergente? (No publicado.)
- ¿Existe un "similarity score" accesible para anunciantes gestionados y cómo se calcula? (Solo testimonio de practitioners, feb-2026.)
- ¿Qué fracción de la mejora de "conversiones" se traduce en conversiones **incrementales** para el anunciante y no en atribución a Meta de conversiones que habrían ocurrido igual?
- ¿Cuánto del Generative Recommender está desplegado en Q3-2026 y en qué superficies? (Earnings Q3-2026 aún no publicados a 15-oct-2026.) **Actualización 2026-11-09**: publicados el 21-oct-2026 (precio por anuncio +14 %, impresiones +10 %; GEM +1,7 % offsite y +9,6 % apps; Andromeda +1,4 %; retrieval generativo en el Feed de FB ~+2 %). [OFFICIAL META] (S10-117 en `fuentes/ledger-10-cambios-api-ia.md`)

## Fuentes clave

- [Meta Andromeda: Supercharging Advantage+ automation…](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — 2024-12-02 — meta-engineering
- [Sequence learning: A paradigm shift for personalized ads recommendations](https://engineering.fb.com/2024/11/19/data-infrastructure/sequence-learning-personalized-ads-recommendations/) — 2024-11-19 — meta-engineering
- [Meta's Generative Ads Model (GEM): the central brain…](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) — 2025-11-10 — meta-engineering
- [Meta's GEM: Scaling the Central Model and Compute Engine for Frontier Ads AI](https://engineering.fb.com/2026/10/13/ml-applications/metas-generative-ads-model-gem-scaling-the-central-model-and-compute-engine-for-frontier-ads-ai) — 2026-10-13 — meta-engineering
- [Meta Adaptive Ranking Model](https://engineering.fb.com/2026/03/31/ml-applications/meta-adaptive-ranking-model-bending-the-inference-scaling-curve-to-serve-llm-scale-models-for-ads/) — 2026-03-31 — meta-engineering
- [From User Sequences to Scaling Laws](https://engineering.fb.com/2026/08/05/ml-applications/from-user-sequences-to-scaling-laws-a-multi-stage-architecture-for-metas-ads-ranking/) — 2026-08-05 — meta-engineering
- [Meta Lattice (arXiv 2512.09200)](https://arxiv.org/html/2512.09200v2) — 2025-12 — academico (Meta)
- [LLaTTE (arXiv 2601.20083)](https://arxiv.org/abs/2601.20083) — 2026-01 — academico (Meta)
- [Semantic ID (arXiv 2504.02137)](https://arxiv.org/abs/2504.02137) — 2025-04 — academico (Meta)
- [LLM Retrieval for Stable and Predictable Ad Recommendations (arXiv 2605.21969)](https://arxiv.org/abs/2605.21969) — 2026-05 — academico (Meta)
- [GRACE (arXiv 2608.00938)](https://arxiv.org/abs/2608.00938) — 2026-08 — academico (Meta)
- [Ranking Engineer Agent (REA)](https://engineering.fb.com/2026/03/17/developer-tools/ranking-engineer-agent-rea-autonomous-ai-system-accelerating-meta-ads-ranking-innovation/) — 2026-03-17 — meta-engineering
- Transcripciones de earnings Q4-2024, Q2-2025, Q3-2025, Q4-2025, Q1-2026, Q2-2026 (investor.atmeta.com / s21.q4cdn.com) — meta-investors
- [Maximize conversions with differentiated ad creative](https://www.facebook.com/business/m/small-business/creative-differentiation) — vigente 2026 — meta-oficial
- [The Creative Advantage… Meta Andromeda](https://www.facebook.com/business/news/the-creative-advantage-unlocking-the-power-of-diversification-with-meta-andromeda) — 2025-04-22 — meta-oficial
- [Three steps… creative diversification](https://www.facebook.com/business/news/three-steps-to-optimize-your-performance-with-creative-diversification) — 2024-11-19 — meta-oficial
