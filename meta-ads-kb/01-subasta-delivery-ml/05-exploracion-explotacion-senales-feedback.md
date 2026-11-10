# Exploración vs explotación, predicción de conversión, señales y bucles de feedback

> Última verificación: 2026-10-15 · Autor: A01 (agente) · Ámbito: cómo aprende el sistema de Meta (cold start, learning phase, concentración de gasto), cómo predice conversiones y qué hace la cantidad/calidad de señal con los resultados.

## TL;DR

- **El sistema es un aprendiz que optimiza el evento que tú le das**, por persona y por anuncio. Si el evento es barato y malo (lead basura, clic, add-to-cart sin intención), el sistema se vuelve excelente encontrando eso. La elección y la calidad del evento de optimización es la decisión con más palanca de una cuenta. **[OFFICIAL META]** (el optimization goal decide a quién se muestra) + **[STRONG INFERENCE]**.
- **Exploración sí, pero sesgada por predicción.** Los anuncios nuevos no reciben un reparto igualitario: reciben impresiones según su EAR predicho (que en 2025-2026 se apoya en features semánticas del contenido) y según la incertidumbre. Por eso un ganador establecido absorbe el gasto y los nuevos "no arrancan". **[STRONG INFERENCE]** coherente con papers de Meta.
- **Meta trabaja activamente contra el cold start y la sub-exploración**: Semantic ID (los anuncios nuevos heredan conocimiento de anuncios semánticamente similares), features de contenido que "doblan la curva de escala", y retrieval con LLM para que variantes menores tengan entrega consistente. Meta cita explícitamente "cold start" y "under-exploration" como problemas "perceptibles por el anunciante". **[OFFICIAL META]**
- **Learning phase** (oficial, vía fuentes secundarias del Help Center): ~**50 eventos optimizados en 7 días** tras el lanzamiento o la última edición significativa; antes de eso el rendimiento es menos estable; si no se espera alcanzar, "Learning limited". Meta probó temporalmente "10 eventos en 3 días" con algunos anunciantes (Loomer), sin cambio oficial. **[OFFICIAL META]** (umbral) / **[EMPIRICAL]** (test temporal).
- **Más señal, más rápida y más limpia = mejor predicción**: pixel + Conversions API (Meta Blueprint: −13% CPA medio al usar ambos), Event Match Quality alta, deduplicación, eventos de valor, CRM (conversion leads: −15% coste por lead cualificado y +44% tasa lead→cualificado, cifras de un PMM de Meta en 2024 no verificadas en documento oficial). **[OFFICIAL META]** / **[EMPIRICAL]**.
- **Las conversiones también actualizan la "foto" del usuario**: los embeddings upstream (LLaTTE) se recalculan disparados por eventos de alto valor, sobre todo conversiones. Señal de conversión rápida y correcta mejora el modelo para ti y para el ecosistema. **[OFFICIAL META]**
- **Bucle peligroso: atribución ≠ incrementalidad.** Un sistema que optimiza conversiones atribuidas tiende a encontrar a quien iba a comprar igual (retargeting implícito). Meta lanzó *incremental attribution* (global Q2-2025; +24% conversiones incrementales vs atribución estándar con el modelo de Q4-2025). Haus (640 tests, 2025) halló que Advantage+ sobre-reporta ~12 pp más que manual; nota editorial de jul-2026: la atribución incremental ya supera a la estándar en sus tests. **[OFFICIAL META]** + **[EMPIRICAL]**.
- **Optimizar más arriba del embudo no es siempre peor**: Haus halló que optimizar a mid-funnel (add-to-cart, quiz) dio −14% iROAS DTC pero +9% lift post-tratamiento y más clientes nuevos; para marcas con <5.000 compras/semana la pérdida de eficiencia fue solo −5%. **[EMPIRICAL]** (vendor, muestra sesgada a marcas grandes: gasto medio $14M/año en Meta).

---

## 1. Primeros principios: qué problema de aprendizaje resuelve Meta

Para cada oportunidad, el sistema necesita estimar `P(evento optimizado | persona, anuncio, contexto)` y el valor del evento. Tres dificultades:

1. **Escasez de positivos**: las compras son eventos raros (fracciones de un %). Los modelos aprenden la mayoría de la estructura de eventos densos (clics, vistas) y la trasladan a eventos raros (Lattice Partitioner separa feedback denso y rápido del retrasado y escaso; GEM/Lattice comparten aprendizaje entre objetivos). **[OFFICIAL META]**
2. **Retraso del feedback**: una conversión puede llegar "de minutos a días" tras la impresión. Lattice Zipper entrena cabezas por ventana (90 min, 1 día, 7 días) y sirve con la más larga. **[OFFICIAL META]**
3. **Rotación del inventario**: "la mitad del corpus original [de anuncios] sale del sistema tras 6 días", y entra la misma cantidad de anuncios nuevos (paper Semantic ID). Con IDs aleatorios, los anuncios nuevos empezaban con embeddings "esencialmente aleatorios". **[OFFICIAL META]**

De aquí sale el dilema **exploración/explotación**: para saber si un anuncio nuevo convierte, hay que mostrarlo (coste de oportunidad frente al ganador conocido). Cuanto mejor predice el sistema a partir del **contenido** del anuncio (sin historia), menos exploración "a ciegas" necesita.

## 2. Cómo explora Meta (lo público y lo inferido)

| Mecanismo | Evidencia | Qué implica |
|---|---|---|
| **Learning phase** por ad set: periodo de mayor incertidumbre tras lanzar o tras una "edición significativa" (segmentación, creativo, evento de optimización, estrategia de puja, cambios grandes de presupuesto, añadir anuncios, pausar >7 días) | Help Center (vía secundarias: ~50 eventos/7 días); Marketing API: cambiar puja/presupuesto obliga a "reaprender la puja óptima" | Cada edición significativa reinicia exploración y desestabiliza el CPA. Agrupar cambios; no tocar a diario |
| **Predicción con features semánticas para anuncios nuevos** | Semantic ID (−43% diferencia de predicción entre copias; ganancias sobre todo en cola larga y anuncios nuevos); Engineering ago-2026: features semánticas ayudan a anuncios/anunciantes nuevos | Un anuncio nuevo parecido a un ganador hereda su predicción (y también su "lugar" en retrieval) |
| **Retrieval semántico con LLM** para que pequeñas variantes tengan entrega consistente | arXiv 2605.21969: −8,62% diferencia A/A', −45% MAD de impresiones | Las micro-variantes no son exploración independiente; el sistema las trata como el mismo concepto |
| **Enrutamiento de cómputo** hacia peticiones con alta probabilidad de conversión | Adaptive Ranking Model (Q1-2026) | Más precisión donde hay más valor; menos en inventario marginal |
| **Concentración del gasto** en pocos anuncios por ad set | Observación generalizada; CTC: 3-5% de anuncios = 70-80% del gasto | Comportamiento esperado de un ranking que explota predicciones confiadas |

**Lo que no es público:** la política exacta de exploración (si hay "bonus de incertidumbre", cuotas de impresiones para anuncios nuevos, o Thompson sampling). Cualquier afirmación concreta sobre "Meta da X impresiones a cada anuncio nuevo" es **UNPROVEN**.

## 3. Learning phase: qué dice Meta y qué es folklore

- **Oficial (Help Center, vía múltiples fuentes secundarias consistentes):** el ad set sale de aprendizaje tras ~50 eventos optimizados en un periodo de 7 días desde la última edición significativa; durante el aprendizaje, el rendimiento es menos estable y el CPA suele ser peor; "Learning limited" cuando no se espera alcanzar el umbral (presupuesto bajo, audiencia pequeña, evento raro, puja/cost cap restrictivo). **[OFFICIAL META]**
- **Test temporal:** Jon Loomer vio durante "unos meses" un learning phase de 10 eventos en 3 días y luego volvió a 50/7 sin explicación; también observó que añadir un anuncio a un ad set vivo no reinició aprendizaje, pese a que la documentación dice lo contrario. **[EMPIRICAL]** (un practitioner fiable, sin confirmación de Meta).
- **Folklore:** "cambios de presupuesto >20% reinician el aprendizaje" → **UNPROVEN** como regla oficial (Meta habla de cambios "significativos" sin umbral publicado que haya podido verificar). Regla práctica razonable, no ley.
- **Interpretación desde primeros principios:** el learning phase es una **etiqueta de diagnóstico** para el anunciante sobre la incertidumbre del ad set; los modelos subyacentes son globales (GEM/Lattice) y no "empiezan de cero" con cada ad set. Lo que se reinicia es sobre todo el **pacing y la calibración** específica de esa combinación (presupuesto, puja, audiencia, creativos). **[STRONG INFERENCE]**

## 4. Predicción de conversión: cómo funciona y qué la mueve

- **Factorización**: el modelo de CTR "es esencial para estimar las tasas de acción de diversas conversiones post-clic" (Meta, 2023). Conversiones view-through y engage-through existen como caminos adicionales (y desde 2026 Meta separa click-through de engage-through en atribución; ver área 04). **[OFFICIAL META]**
- **Entradas**: secuencias del usuario (miles de eventos, mezcla de vistas/clics/conversiones), features del anuncio (creativo, landing, metadatos del anunciante), interacción usuario-anuncio, contexto (hora, dispositivo, superficie). **[OFFICIAL META]** (LLaTTE)
- **Salidas calibradas**: se usan para ranking **y para el precio** en la subasta. **[OFFICIAL META]**
- **Valor**: con *value optimization* (ROAS goal/highest value) el sistema predice también el valor de la conversión; la suite supera $20B de run-rate (Q1-2026). Requiere enviar valores fiables. **[OFFICIAL META]**

**Qué mueve tu predicción (de mayor a menor palanca, inferido):**
1. **Evento de optimización** correcto (cercano al valor de negocio pero con volumen suficiente).
2. **Calidad de la señal**: pixel + CAPI con buena Event Match Quality, deduplicación, latencia baja, valores correctos.
3. **Creativo y oferta** que atraen a compradores (no a curiosos).
4. **Landing/experiencia post-clic** (CVR post-clic).
5. **Historia acumulada** del anuncio/ad set (no reiniciar sin motivo).
**[STRONG INFERENCE]**

## 5. Cantidad y calidad de señal

### 5.1 Cantidad
- 50 eventos/semana por ad set es la referencia oficial del learning phase, **no** un mínimo para que el sistema "funcione": gracias al aprendizaje compartido (Lattice, GEM), el sistema puede optimizar con menos, pero con más varianza. **[STRONG INFERENCE]**
- Con poco volumen: consolidar ad sets, subir de evento (p. ej. de Purchase a AddToCart/InitiateCheckout o a un evento de CRM más frecuente), o aceptar más varianza. Haus: optimizar mid-funnel no es necesariamente peor en incrementalidad (ver TL;DR). **[EMPIRICAL]**
- Meta (benchmark para Conversion Leads/CRM, vía Make.com): ≥50 leads/semana, optimizar a una etapa alcanzada por el 10-30% de los leads y que ocurra en ≤28 días. **[OFFICIAL META]** vía secundaria.

### 5.2 Calidad
- **Pixel + Conversions API**: −13% CPA medio (Meta Blueprint, sin fecha). One-click CAPI: −17,8% coste por resultado vs sin CAPI (cifra reportada por terceros, 2026). **[OFFICIAL META]** / **[EMPIRICAL]**.
- **Event Match Quality** (Poor/OK/Good/Great): Meta asocia mejor EMQ con más conversiones atribuidas a menor coste, sin cifra pública. **[OFFICIAL META]**
- **Lead quality**: optimizar "leads" (envío de formulario) enseña al sistema a encontrar gente que rellena formularios. Conversion leads con CRM: −15% coste por lead cualificado y +44% tasa lead→cualificado (evento HubSpot-Meta, oct-2024). **[EMPIRICAL]** (no hay documento oficial verificado).
- **Valor**: enviar valor real (margen o LTV predicho si es posible) permite que value optimization discrimine. Enviar precios de catálogo con descuentos/devoluciones ignorados sesga hacia compradores de bajo margen. **[STRONG INFERENCE]**

### 5.3 Pérdida de señal y su compensación
- **ATT (iOS 14.5, 26-abr-2021)**: pérdida de señal off-platform en iOS; Meta estimó ≈$10B de impacto en 2022; AEM limitó eventos (8 eventos priorizados, restricción luego relajada). **[OFFICIAL META]** (CNBC citando a Meta)
- **Respuesta de Meta**: modelos que extraen más de la señal **on-platform** (secuencias de comportamiento, contenido) y modelado de conversiones; sequence learning y GEM son, en parte, la respuesta estructural a ATT. **[STRONG INFERENCE]**
- **UE – LPA (2026)**: menos señal para una parte de usuarios europeos. **Meta AI chats (dic-2025)**: más señal de intereses en mercados no-UE. **[OFFICIAL META]**

## 6. Bucles de feedback (dónde se rompe el sistema)

1. **Goodhart del evento**: optimizas lo que mides. Leads baratos → leads basura; compras de primera vez con descuento → clientes de bajo LTV; clics → curiosos. Solución: subir el evento hacia el valor (CRM, valor, eventos post-compra) o filtrar en la fuente (formularios con fricción, preguntas cualificadoras). **[STRONG INFERENCE]**
2. **Bucle de atribución**: el sistema recibe "recompensa" por conversiones atribuidas, incluidas las que habrían ocurrido igual (clientes existentes, buscadores de marca). Puede sesgarse hacia retargeting implícito. Contramedidas: exclusión/limitación de clientes existentes donde exista el control, *incremental attribution* como objetivo de optimización, Lift tests/geo-holdouts periódicos. **[OFFICIAL META]** (producto) + **[EMPIRICAL]** (Haus).
3. **Bucle de creativo**: el sistema concentra gasto en el ganador; los nuevos no aprenden; el ganador se fatiga ("Creative fatigue": coste por resultado aumentado frente al histórico); el anunciante entra en pánico y duplica. Solución: cadencia de conceptos nuevos realmente distintos (Meta: anuncios nuevos semanales, 20-30% del presupuesto a testing). **[OFFICIAL META]**
4. **Bucle de edición**: tocar a diario reinicia aprendizaje y pacing → volatilidad → más ediciones. Solución: ventanas de decisión (p. ej. 3-7 días según volumen) y cambios agrupados. **[STRONG INFERENCE]**
5. **Bucle de audiencia pequeña**: segmentación estrecha → menos oportunidades → puja efectiva más alta para gastar → CPM alto y frecuencia alta → peor rendimiento → "la audiencia está quemada". **[STRONG INFERENCE]**

## 7. Debate abierto: ¿testear creativos en el mismo ad set o en campaña separada?

**[CONTESTED]**
- *Postura A (consolidar)*: añadir conceptos nuevos al ad set/campaña principal aprovecha la señal acumulada y deja que el sistema decida; el gasto bajo de un anuncio nuevo es información (predicción baja), no injusticia.
- *Postura B (aislar)*: campañas de testing con presupuesto forzado (ABO, 1-2 anuncios por ad set) dan lecturas más limpias y evitan que el ganador ahogue a los nuevos; luego se "gradúa" el ganador.
- *Lectura de primeros principios*: B mide mejor el potencial del creativo **fuera** de la competencia con el ganador, pero (a) cada ad set nuevo paga su propio aprendizaje, (b) el resultado sigue afectado por entrega divergente (Burtch et al. 2025), y (c) al graduar, la competencia con el ganador vuelve. A es más eficiente cuando el volumen de conversiones es alto. Ningún bando aporta datos controlados publicados. Recomendación: decidir según volumen de conversiones y necesidad de aprendizaje creativo (ver área 03-creatividad y 09-bidding-escalado).

## Implicaciones operativas

- **Elegir el evento más cercano al valor que tenga volumen suficiente** (~50/semana por ad set como referencia, no dogma).
- **Invertir en señal antes que en hacks de estructura**: CAPI + pixel deduplicados, EMQ alta, valores reales, integración CRM en lead gen.
- **Cadencia de conceptos nuevos** semanal o quincenal, con diversidad semántica real; aceptar que la mayoría no recibirá gasto.
- **Ventanas de decisión** acordes al volumen y al retraso de conversión; no editar a diario.
- **Medir incrementalidad** al menos trimestralmente (Lift/geo) para recalibrar la confianza en la atribución de plataforma.

## Errores frecuentes

- Optimizar a "Leads" sin cualificación y juzgar la campaña por CPL.
- Interpretar "Learning limited" como penalización (es un aviso de volumen insuficiente).
- Duplicar ad sets para "reiniciar la suerte" (la varianza A/A está en retroceso; y duplicar divide señal).
- Cambiar a un evento más arriba del embudo sin medir incrementalidad ni calidad.

## Preguntas abiertas

- Política exacta de exploración de anuncios nuevos (no pública).
- Cuánto pesa el embedding upstream del usuario frente a señales en tiempo real en decisiones de conversión.
- Si *incremental attribution* como objetivo de optimización cambia materialmente la mezcla prospecting/retargeting (datos independientes escasos; Haus 2026 sugiere que sí mejora).

## Fuentes clave

- [Semantic ID (arXiv 2504.02137)](https://arxiv.org/abs/2504.02137) — 2025-04 — academico (Meta)
- [LLM Retrieval for Stable and Predictable Ad Recommendations (arXiv 2605.21969)](https://arxiv.org/abs/2605.21969) — 2026-05 — academico (Meta)
- [Meta Lattice (arXiv 2512.09200)](https://arxiv.org/html/2512.09200v2) — 2025-12 — academico (Meta)
- [LLaTTE (arXiv 2601.20083)](https://arxiv.org/abs/2601.20083) — 2026-01 — academico (Meta)
- [From User Sequences to Scaling Laws](https://engineering.fb.com/2026/08/05/ml-applications/from-user-sequences-to-scaling-laws-a-multi-stage-architecture-for-metas-ads-ranking/) — 2026-08-05 — meta-engineering
- Earnings Q2-2025 (incremental attribution global), Q4-2025 (+24%), Q1-2026 (ARM, value optimization) — meta-investors
- [Haus – The Meta Report (640 experimentos)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 (nota jul-2026) — vendor
- [Jon Loomer – Is the Learning Phase 10 or 50 Events?](https://www.jonloomer.com/qvt/learning-phase-10-or-50-events/) — s.f. — practitioner (no descargable; resumido vía búsqueda)
- [Vaizle – Meta might have quietly changed how the learning phase works](https://insights.vaizle.com/news/meta-might-have-quietly-changed-how-the-learning-phase-works) — 2025 — prensa/practitioner
- [HubSpot x Meta – Reach more valuable leads](https://events.hubspot.com/events/details/hubspot-central-london-presents-reach-more-valuable-leads-maximize-conversions-with-hubspot-and-meta) — 2024-10 — vendor/meta
- [Make.com – Meta Conversions API for CRM](https://www.make.com/en/blog/meta-make-conversions-api-for-crm) — s.f. — vendor
- [Meta Blueprint – Conversions API (13% CPA)](https://certification.facebookblueprint.com/student/path/514683/activity/466137) — s.f. — meta-oficial
- [Characterizing and Minimizing Divergent Delivery (arXiv 2508.21251)](https://arxiv.org/abs/2508.21251) — 2025-08 — academico (Meta)
- [CNBC – Facebook says Apple iOS privacy change will cost $10B](https://www.cnbc.com/2022/02/02/facebook-says-apple-ios-privacy-change-will-cost-10-billion-this-year.html) — 2022-02-02 — prensa
