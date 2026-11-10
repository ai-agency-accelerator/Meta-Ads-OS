# "El creativo es el targeting": mecanismo, evidencia y límites

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: cómo usa Meta el contenido del anuncio y la respuesta a él para decidir a quién se entrega; similitud creativa y diversificación; qué cambia en la estrategia.

## TL;DR

- **El contenido del anuncio es una variable de entrada de los modelos que deciden a quién se le muestra.** Los modelos de ranking de Meta usan como features la "creative representation" y el formato del anuncio junto con el historial de cada usuario (GEM, nov-2025), y desde el Q2 2026 un "Meta Generative Recommender" usa LLMs para "reason about ad content and user preferences together". **[OFFICIAL META]** (S03-019, S03-016)
- **Con targeting amplio, el creativo selecciona de facto a la audiencia.** Meta lo dice ("the focus has shifted from niche targeting to creative diversification as the main lever for finding relevant audiences", abr-2025) y ya existía evidencia experimental independiente de que con el mismo targeting el contenido del anuncio cambia la demografía de entrega (Ali et al., 2019). **[OFFICIAL META] + [EMPIRICAL]** (S03-002, S03-021)
- **Las creatividades demasiado parecidas se tratan como si fueran una sola.** Meta afirma que si las creatividades se parecen demasiado, sus sistemas "pueden no tratarlas como distintas" y mostrarlas a las mismas audiencias, lo que limita el alcance. Desde el 26-ago-2026, Ads Manager tiene una columna **Creative diversity** (Low/Medium/High, nivel ad set, "estimated and in development") que mide similitud visual. **[OFFICIAL META]** para el efecto y la columna (S03-004, S03-012, S03-013).
- **El "Entity ID" es una metáfora de practicantes, no un término de Meta.** No hay documentación pública de que Meta asigne IDs de entidad a clusters de anuncios ni de umbrales del tipo "60% de similitud = supresión". Las cifras que circulan de ese tipo no tienen fuente primaria. **[HYPOTHESIS]** el mecanismo exacto; **[STRONG INFERENCE]** el efecto práctico, que es que los anuncios casi duplicados compiten por el mismo hueco y no amplían alcance. (S03-009)
- **Límite 1: el creativo segmenta hacia quien responde al evento que optimizas, no hacia quien te hace ganar dinero.** Si optimizas a lead, a clic o a ATC, un creativo que atrae a gente que convierte barato pero mal será "premiado". El targeting por creativo amplifica cualquier sesgo de la señal de conversión. **[STRONG INFERENCE]**
- **Límite 2: el creativo no crea demanda que no existe ni arregla una oferta mala.** Lo que hace es encontrar más rápido y mejor a quien ya está en el mercado o puede estarlo. **[STRONG INFERENCE]**
- **Límite 3: diversidad sin presupuesto equivale a ruido.** Cada concepto necesita gasto suficiente para generar señal; más conceptos de los que el presupuesto puede alimentar = la mayoría sin entrega (en el dataset de Motion, ~50% de los anuncios reciben gasto mínimo o nulo). **[EMPIRICAL]** (S03-010, S03-011)
- **Cambio de estrategia: planificar el portafolio creativo como si fuera un portafolio de audiencias.** Cada concepto es una hipótesis "persona × deseo/dolor × nivel de awareness × contexto" y debe parecer y sonar distinto al resto en los primeros segundos y en la miniatura. **[STRONG INFERENCE]** derivada de lo anterior y coherente con la guía de Meta (S03-002, S03-003).
- **Para leer a quién ha encontrado cada creativo hay que mirar breakdowns por anuncio** (edad, género, región, placement, plataforma), no solo CPA. Es la forma de comprobar si la diversidad creativa está abriendo segmentos distintos o si todos los anuncios caen en el mismo bolsillo. **[STRONG INFERENCE]**

## 1. Cómo funciona la entrega y dónde entra el creativo

### 1.1 El pipeline (versión 2026)

Simplificando, el sistema publicitario de Meta funciona en etapas (detalle en el área 01-subasta-delivery-ml):

1. **Elegibilidad y retrieval.** De decenas de millones de anuncios candidatos se seleccionan "unos pocos miles" relevantes para esa persona y esa oportunidad de impresión. Esto lo hace **Andromeda** (desplegado desde el 2S 2024), con un índice jerárquico entrenado junto al modelo de retrieval. Meta reportó +6% de recall y +8% de calidad de anuncios en segmentos seleccionados, y en el Q2 2025 atribuyó a Andromeda "nearly 4% higher conversions on Facebook mobile Feed and Reels". **[OFFICIAL META]** (S03-001, S03-018)
2. **Ranking.** Se estiman las tasas de acción (probabilidad de clic, conversión, etc.) de cada anuncio para esa persona. Aquí intervienen **GEM** (Generative Ads Recommendation Model, el modelo fundacional que transfiere conocimiento a cientos de modelos más pequeños), **Lattice** (arquitectura que unifica modelos) y el **Adaptive Ranking Model** (inferencia a escala LLM, 2S 2025). **[OFFICIAL META]** (S03-017, S03-019, S03-020)
3. **Subasta.** Valor total = puja × tasa de acción estimada + calidad/experiencia del usuario (ver área 01).

**Desde el Q2 2026**, Meta describe un cambio de paradigma: *"Rather than scoring every possible ad individually, we are now using LLMs to reason about ad content and user preferences together, and predict the best ad for each person"* ("Meta Generative Recommender"), con un primer modelo generativo ya desplegado en retrieval. **[OFFICIAL META]** (S03-016, 29-jul-2026)

### 1.2 Las tres vías por las que el creativo condiciona a quién llega

| Vía | Qué significa | Evidencia |
|---|---|---|
| **A. Contenido como feature** | El modelo "entiende" el anuncio (representación del creativo, formato, texto) y lo cruza con el historial de cada persona. Un anuncio con una enfermera, un uniforme y un turno de noche se parece, en el espacio de representación, a contenidos que consumen ciertas personas. | GEM lista "creative representation" y "ad format" como inputs no secuenciales (S03-019); el post de oct-2026 habla de "ad content representations" (S03-020); el Generative Recommender razona sobre "ad content and user preferences together" (S03-016). **[OFFICIAL META]**. Cómo se construye exactamente esa representación (visión, texto, audio) no se ha publicado. GEM habla de multimodalidad como algo futuro. **[HYPOTHESIS]** el grado exacto de comprensión visual. |
| **B. Respuesta observada** | Quién se para, mira, hace clic y convierte con ese anuncio realimenta las predicciones. El creativo filtra a quien responde, y el sistema busca más gente parecida a quien ha respondido. | Mecánica estándar de los sistemas de recomendación con aprendizaje online; Meta habla de "sequence learning" e historiales de interacción (S03-016, S03-020). **[STRONG INFERENCE]** sobre el detalle por anuncio. |
| **C. Similitud entre anuncios** | Si varios anuncios son casi iguales, el sistema no tiene motivo para llevarlos a personas distintas: compiten por el mismo hueco. | Meta: si los creativos se parecen demasiado, "may not treat them as distinct and may show them to the same audiences", lo que limita el alcance (S03-004). Columna Creative diversity (ago-2026). **[OFFICIAL META]** |

### 1.3 Evidencia independiente: el creativo ya "segmentaba" en 2019

Ali, Sapiezynski, Bogen, Korolova, Mislove y Rieke (2019) lanzaron anuncios con targeting idéntico y neutro y vieron sesgos fuertes de género y raza en la entrega según el contenido del anuncio, imágenes incluidas. Los atribuyeron a las predicciones de relevancia de la propia plataforma y a efectos de mercado. Fue años antes de Andromeda, así que el fenómeno no es nuevo. Lo que ha cambiado es que el targeting amplio y Advantage+ lo convierten en la palanca principal. **[EMPIRICAL]** (S03-021)

### 1.4 Lo que dice Meta oficialmente sobre diversificación

- **Nov-2024**, "Three steps…": lanzar anuncios nuevos **cada semana**, mantener **≥20 anuncios diversificados** en campañas Advantage+ shopping, dedicar **20–30% del presupuesto** a testear anuncios nuevos, hacer una reunión semanal entre buyers y creativos con brief basado en insights, y crear variantes para "different customer needs and purchase blockers" (personas). **[OFFICIAL META]** (S03-003)
- **Abr-2025**, "The Creative Advantage… with Meta Andromeda": define la diversificación como "a wide range of ad creatives with different themes, messages, and visuals"; dice que el foco ha pasado del targeting nicho a la diversificación creativa como palanca principal para encontrar audiencias, y que *"The biggest constraint you can put on your Meta strategy is the constraints you place on your creative process"*. **No da un número de anuncios.** **[OFFICIAL META]** (S03-002)
- **Página "Creative differentiation"** (vigente en 2026): anuncios demasiado parecidos reducen interacción y ventas, pueden mostrarse a las mismas audiencias y acabar en estado "Creative limited" o "Creative fatigue" en la columna Delivery. **[OFFICIAL META]** (S03-004)
- **La recomendación histórica de "máximo 6 anuncios por ad set"** desapareció de la documentación en 2025 (Jon Loomer). El límite técnico sigue siendo de **50 anuncios no archivados por ad set** en la referencia de la Marketing API. **[OFFICIAL META]** para el límite (S03-027) · **[EMPIRICAL]** para la retirada de la recomendación (S03-005). Algunos practicantes hablan de 150 anuncios por ad set en 2026 (CTC, S03-022). No lo hemos podido verificar: el 150 aparece en documentación de Advantage+ shopping como "creative combinations", no como límite de anuncios. **[CONTESTED]/no verificado**.

## 2. Similitud creativa: qué es oficial y qué es folclore

| Afirmación | Veredicto | Comentario |
|---|---|---|
| "Meta trata anuncios muy similares como uno solo / los muestra a las mismas personas" | **TRUE** [OFFICIAL META] | Lo dice la página de creative differentiation (S03-004). El efecto práctico es menos alcance incremental por anuncio adicional. |
| "Existe una columna que mide la similitud" | **TRUE** [OFFICIAL META, vía practicantes que citan la UI] | "Creative diversity", Low/Medium/High, nivel ad set, desde finales de ago-2026, "estimated and in development". Se basa en la similitud visual de imágenes y miniaturas de vídeo (S03-012, S03-013, S03-014). En el Q4 2025 varios practicantes ya informaban de métricas "Creative fatigue" y "Creative similarity" en el reporting de Account Insights (S03-015). Su disponibilidad varía por cuenta. **[EMPIRICAL]** |
| "Tras Andromeda, Meta agrupa anuncios similares en un mismo Entity ID" | **UNPROVEN** como mecanismo literal | Origen: blogs de herramientas y agencias. Uno de ellos reconoce que es "an explanatory device… rather than an official term Meta publishes" (S03-009). Sirve como modelo mental, no como dato. |
| "Por encima del 60% (o 40%) de similitud hay supresión activa" | **UNPROVEN** | No hay documentación de Meta. Circulan cifras contradictorias (40%, 60%) sin metodología. |
| "Cambiar el color del botón o tres palabras del hook crea un anuncio 'nuevo' para el algoritmo" | **FALSE** en la práctica [STRONG INFERENCE] | Meta pide diferencias "noticeably different"; Loomer: "two different image files that look very similar… unlikely to make a meaningful impact" (S03-005). Las iteraciones de hook sí son útiles, pero como optimización de un concepto, no como diversificación. Ver 02-taxonomía. |
| "Un score de diversidad bajo penaliza la puja/entrega" | **UNPROVEN** | Ni Meta ni CTC lo confirman: "a visible signal, not a confirmed algorithmic penalty" (S03-013). No se deben pausar anuncios ganadores para subir el score (S03-012). |

### 2.1 ¿Cuánto cambió realmente Andromeda? [CONTESTED]

- **Postura "cambio de paradigma"** (CTC, muchas agencias): "Meta moved from an audience-first world to a creative-first world" (S03-022). CTC afirma, con datos propios (170+ marcas) que no se pueden verificar, que en el Q1 2026 los CPM subieron un 28% interanual, el CTR un 43% y la conversión bajó. También cita un estudio de terceros no enlazado (3.014 anunciantes, −7% de ROAS durante el despliegue) (S03-023).
- **Postura escéptica**: en BFCM 2025, compradores con mucho gasto declararon no haber cambiado nada por Andromeda ("What are we doing about Andromeda for BFCM? Absolutely nothing", Jess Bachman), y Aazar Shad (The Performers) llegó a llamarlo "snake oil" antes de publicar su propia guía post-Andromeda en dic-2025. El autor de Motion concluye que Andromeda "mainly exposed brands that were not testing with purpose" y que la oferta y el contexto económico siguen mandando (S03-077, S03-024).
- **Síntesis:** las dos posturas son compatibles. El mecanismo (el contenido del anuncio como input, la penalización práctica de los casi duplicados) está respaldado por Meta. Lo que se discute es la **magnitud** del cambio para cuentas que ya trabajaban con conceptos diversos: para ellas cambió poco; para las que vivían de "un ganador + 20 variaciones", mucho. **[STRONG INFERENCE]**

**Cómo usar la columna Creative diversity (2026).** Es una señal de diagnóstico, no un objetivo. Si un ad set sale "Low" y además (a) el gasto se concentra en 1–2 anuncios, (b) la frecuencia sube y (c) el CPA de los anuncios nuevos no mejora, el problema probablemente es falta de diversidad real. Si sale "Low" y el ad set rinde, se registra como baseline y no se toca. **[STRONG INFERENCE]**

## 3. Límites de "el creativo es el targeting"

1. **El creativo segmenta hacia el evento de optimización, no hacia el negocio.** El modelo busca a quien tiene alta probabilidad de completar *el evento que le das*. Un creativo de "consigue tu guía gratis" con optimización a lead encontrará a quien rellena formularios gratis, no a quien compra un servicio de 5.000 €. En lead gen y high-ticket esto es el riesgo principal (área 05). **[STRONG INFERENCE]**
2. **El creativo puede segmentar mal.** Los ganchos de curiosidad, sorteo o polémica atraen a una audiencia barata y poco cualificada. Que el creativo cualifique o descualifique es una decisión de diseño: nombrar el precio, decir para quién NO es o mostrar la complejidad del producto reduce el volumen y mejora la calidad. **[EMPIRICAL]** (patrón ampliamente reportado por practicantes de lead gen; ver 09-oferta)
3. **El creativo no sustituye a la señal de conversión.** Con un pixel/CAPI pobre (eventos perdidos, poco volumen), el sistema aprende peor quién convierte, haga lo que haga el creativo. Varios practicantes señalan como palancas reales del anunciante "creative volume and diversity, conversion signal quality, and budget structure". **[STRONG INFERENCE]** (ver área 04)
4. **Las restricciones duras siguen mandando.** Geo, idioma, edad mínima, exclusiones de clientes, categorías especiales (vivienda, empleo, crédito) y políticas acotan el universo antes de que el creativo actúe. **[OFFICIAL META]** (ver áreas 02 y 08)
5. **Diversidad sin presupuesto es ruido.** El sistema concentra el gasto: en el dataset de Motion los "winners" (≈5–8% de las creatividades) se llevan el 55% del gasto, y en cuentas Enterprise el 64% (S03-010). Lanzar 30 conceptos con 50 €/día no da 30 aprendizajes, da 3 anuncios con gasto y 27 sin señal. **[EMPIRICAL]**
6. **Los anuncios nicho no escalan por sí solos.** Un creativo que habla solo a "madres veganas de gemelos" se entregará bien a ese bolsillo, pero tendrá techo. La diversificación sirve para cubrir varios bolsillos, y cada uno tiene su propio techo. **[STRONG INFERENCE]**
7. **El creativo no crea mercado.** Encuentra demanda latente o explícita. Si el producto no tiene mercado o la oferta no compite, más creativos solo dan más datos de que no funciona (ver 09-oferta). **[STRONG INFERENCE]**
8. **Las audiencias siguen sirviendo como restricción o pista en ciertos contextos.** Retargeting con oferta específica, exclusiones de clientes en adquisición, mercados B2B muy estrechos y lanzamientos con poca señal inicial. Ver área 02 para la evidencia sobre Advantage+ audience frente a targeting manual. **[CONTESTED]** (lo cubre el área 02)

## 4. Qué cambia en la estrategia creativa

### 4.1 Planificar el portafolio por "bolsillos de demanda"

Cada concepto creativo debe responder a: **¿a qué persona concreta, en qué momento de awareness y con qué deseo o dolor dominante le habla?** Las dimensiones que de verdad cambian quién se detiene son:

| Dimensión | Ejemplos de valores distintos | Por qué cambia la entrega |
|---|---|---|
| Persona / identidad | madre primeriza, deportista >40, dueño de clínica | Quién aparece en pantalla y a quién se nombra en el hook atrae a perfiles distintos |
| Problema / deseo | dormir mejor, dolor cervical, regalo | Activa intereses distintos en el historial de la persona |
| Nivel de awareness | unaware → most aware (ver 03) | Cambia qué grado de familiaridad necesita el espectador |
| Contexto / uso | oficina, viaje, post-parto | El escenario es parte de la "representación" visual |
| Portavoz / talento | fundador, cliente, experto, creador, sin persona | Los rasgos del portavoz influyen en quién se identifica |
| Formato | estático texto, UGC, demo, carrusel, founder | Cambia placement natural y tipo de consumidor |
| Tono / emoción | humor, miedo, aspiración, alivio | Cambia el tipo de respuesta y de público |

Regla práctica (inspirada en CTC, S03-023, y coherente con Meta): **si todos los anuncios activos de un ad set se pueden describir con la misma frase, no hay diversificación**. **[STRONG INFERENCE]**

### 4.2 Diversificar por concepto, no por "variaciones cosméticas"

- **Sí cuenta como diversificación**: cambiar de persona, de problema, de nivel de awareness, de formato y estilo visual, de portavoz o de mecanismo explicado.
- **No cuenta como diversificación (aunque sea útil)**: cambiar 3 palabras del hook, el color del fondo, el CTA, el orden de escenas o el texto superpuesto sobre el mismo plano. Es **iteración** dentro del concepto (ver 02).
- **Zona gris**: el mismo guion con otro creador de perfil muy distinto (edad, género, contexto) puede funcionar como diversificación, porque cambia la representación visual y a quién atrae. **[HYPOTHESIS]**: no hay datos públicos que cuantifiquen el efecto del cambio de talento por separado.

### 4.3 Usar el creativo como "callout" explícito

Si el creativo segmenta, conviene hacerlo **a propósito**: nombrar a la audiencia en el hook ("Si tienes una clínica dental y…"), mostrar el contexto del comprador ideal y descualificar ("No es para ti si…"). Esto sustituye a la segmentación por intereses que antes hacía el media buyer. **[STRONG INFERENCE]**, coherente con la práctica de direct response clásica.

### 4.4 Leer a quién ha encontrado cada creativo

Para cada concepto con gasto relevante:

1. Breakdown por **edad y género**: ¿se distribuye distinto que el resto?
2. Breakdown por **placement y plataforma** (Reels vs Feed vs Stories, IG vs FB).
3. Breakdown por **región**.
4. Si hay CRM: ¿qué calidad de lead o de cliente (LTV, tasa de cierre) trae cada concepto? Ver área 05.

Si todos los conceptos tienen la misma distribución, o son demasiado parecidos o el modelo aún no ha separado audiencias. Si un concepto abre un bolsillo nuevo (por ejemplo, 45–64 cuando el resto va a 25–34), es un activo aunque su CPA sea algo peor, porque amplía el alcance incremental. **[STRONG INFERENCE]**

### 4.5 Estructura: menos segmentación, más conceptos por ad set

Con targeting amplio, lo habitual en 2025-2026 es consolidar (pocos ad sets, varios conceptos por ad set) en vez de "un ad set por persona". Hay matices: los practicantes discrepan sobre si testear dentro de la campaña principal o en una campaña separada (ver 05-testing). La consolidación no es un fin en sí mismo. El objetivo es que cada ad set tenga **señal suficiente** y **conceptos suficientemente distintos**. **[EMPIRICAL]**/**[CONTESTED]** en los detalles (ver área 02).

## Implicaciones operativas

- **Brief**: cada brief nuevo debe declarar persona, deseo/dolor, nivel de awareness, ángulo y formato, y explicar en una línea **en qué se diferencia de los conceptos activos**.
- **Auditoría de similitud** (semanal):
  1. Prueba de la frase: ¿se describen todos los anuncios con la misma frase?
  2. Prueba de la cuadrícula: poner las miniaturas o primeros fotogramas en una cuadrícula. Si a 1 m de distancia parecen el mismo anuncio, lo son para el usuario y probablemente para el sistema.
  3. Columna Creative diversity (si está disponible).
  4. Concentración de gasto: ¿cuántos anuncios se llevan el 80% del gasto?
- **Umbral orientativo**: si el 1–2 anuncios superiores concentran más del 80% del gasto del ad set durante más de 2–3 semanas y su frecuencia y CPA suben, toca introducir **conceptos** nuevos, no variaciones. **[HYPOTHESIS]** (umbral de trabajo, no publicado por Meta)
- **No perseguir el score de diversidad** a costa de pausar ganadores.
- **Alinear el evento de optimización con el negocio** antes de culpar al creativo (áreas 04/05).

## Errores frecuentes

- Llamar "diversificación" a 10 versiones del mismo plano con distinto texto superpuesto.
- Montar 6 ad sets por intereses con los mismos 3 anuncios: ni diversificación creativa ni señal consolidada.
- Creer que "creative = targeting" significa que da igual a quién habla el anuncio. Es justo lo contrario: **a quién habla el anuncio ES el targeting**.
- Optimizar a un evento barato (lead, clic) con creativos de curiosidad y luego quejarse de la calidad.
- Citar umbrales de "similarity score" o "Entity IDs" como hechos oficiales.
- Juzgar un concepto nuevo solo por su CPA de 3 días sin mirar si abre un segmento nuevo.

## Preguntas abiertas

- ¿Qué peso tiene cada modalidad (imagen, texto superpuesto, audio, copy) en la representación del creativo que usan retrieval y ranking? Meta no lo ha publicado; GEM habla de multimodalidad como trabajo en curso o futuro.
- ¿La columna Creative diversity influye en la entrega o solo la describe? Sin datos públicos.
- ¿Cuál es el número óptimo de conceptos activos por ad set según presupuesto? No hay recomendación oficial vigente (la de 6 se retiró). Ver 05 y 13 para heurísticas.
- ¿Existe un límite actual distinto de 50 anuncios por ad set en 2026? Hay afirmaciones de 150 sin verificar.

## Fuentes clave

- [Meta Engineering — Andromeda](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — 2024-12-02 — meta-engineering
- [Meta for Business — The Creative Advantage… Andromeda](https://www.facebook.com/business/news/the-creative-advantage-unlocking-the-power-of-diversification-with-meta-andromeda) — 2025-04-22 — meta-oficial
- [Meta for Business — Three steps… creative diversification](https://www.facebook.com/business/news/three-steps-to-optimize-your-performance-with-creative-diversification) — 2024-11-19 — meta-oficial
- [Meta for Business — Creative differentiation](https://www.facebook.com/business/m/small-business/creative-differentiation) — vigente 2026 — meta-oficial
- [Meta Q2 2026 earnings call transcript](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q2/META-Q2-2026-Earnings-Call-Transcript.pdf) — 2026-07-29 — meta-investors
- [Meta Q1 2026 earnings call transcript](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q1/META-Q1-2026-Earnings-Call-Transcript.pdf) — 2026-04-29 — meta-investors
- [Meta Engineering — GEM (2025)](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) — 2025-11-10 — meta-engineering
- [Meta Engineering — GEM (2026)](https://engineering.fb.com/2026/10/13/ml-applications/metas-generative-ads-model-gem-scaling-the-central-model-and-compute-engine-for-frontier-ads-ai) — 2026-10-13 — meta-engineering
- [Ali et al. — Discrimination through optimization](https://arxiv.org/abs/1904.02095) — 2019 — academico
- [Jon Loomer — Andromeda and Creative Diversification](https://www.jonloomer.com/meta-andromeda-creative-diversification/) — 2025-10-20 — practitioner
- [note.com (しぃ～ま) — Creative Diversity score](https://note.com/sheeema_meta/n/ne771abb2a8b6?hl=en) — 2026-09-07 — practitioner
- [Common Thread — Creative Diversity Score](https://commonthreadco.com/blogs/coachs-corner/metas-new-creative-diversity-score-is-live-in-ads-manager-what-ecommerce-brands-must-act-on-now) — 2026-09-09 — agencia
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor (dataset)
- Ledger completo: `fuentes/ledger-03-creatividad.md`
