# Área 01 — Subasta, delivery system, machine learning e historia de Meta Ads

> Última verificación: 2026-10-16 · Autor: A01 (agente) · Ledger: `../fuentes/ledger-01-subasta-delivery-ml.md`

## Para qué sirve esta carpeta

Para que el agente principal entienda **cómo decide Meta qué anuncio ve cada persona, a qué precio y por qué**, y traduzca eso en decisiones de cuenta. Todo lo demás (estructura, creatividad, bidding, medición) se apoya en este modelo mental.

## Índice

| Archivo | Contenido | Palabras aprox. |
|---|---|---|
| [01-modelo-negocio-meta.md](01-modelo-negocio-meta.md) | Cómo gana dinero Meta (impresiones × precio), serie 2022-2026, ad load, ARPP, capex en IA, automatización, regulación (LPA) | ~2.700 |
| [02-subasta-total-value.md](02-subasta-total-value.md) | Elegibilidad, total value (puja × EAR + calidad), estrategias de puja, value rules, precio tipo VCG, ejemplo numérico | ~3.400 |
| [03-pipeline-retrieval-ranking-entrega.md](03-pipeline-retrieval-ranking-entrega.md) | Paso a paso desde abrir Instagram hasta el feedback; quién decide a quién/cuándo/dónde/qué creativo/frecuencia | ~2.600 |
| [04-sistemas-ml-andromeda-gem-lattice.md](04-sistemas-ml-andromeda-gem-lattice.md) | Andromeda, sequence learning, GEM (2025 y 2026), Lattice, Adaptive Ranking Model, LLaTTE, Semantic ID, retrieval con LLM, Generative Recommender, MTIA | ~5.300 |
| [05-exploracion-explotacion-senales-feedback.md](05-exploracion-explotacion-senales-feedback.md) | Cold start, learning phase, concentración de gasto, predicción de conversión, cantidad/calidad de señal, bucles de feedback | ~2.600 |
| [06-pacing-presupuesto-frecuencia.md](06-pacing-presupuesto-frecuencia.md) | Pacing (bid/budget), presupuesto diario como semanal, CBO y budget sharing, escalado, frecuencia | ~2.000 |
| [07-calidad-anuncio-y-diagnosticos-relevancia.md](07-calidad-anuncio-y-diagnosticos-relevancia.md) | Ad quality en la subasta, atributos de baja calidad, contagio de cuenta, relevance diagnostics | ~1.900 |
| [08-historia-evolucion-2015-2026.md](08-historia-evolucion-2015-2026.md) | Cronología 2012-2026, por qué murieron tácticas antiguas, ¿broad siempre gana? | ~3.900 |
| [09-implicaciones-para-el-anunciante.md](09-implicaciones-para-el-anunciante.md) | Síntesis accionable: principios, reglas de decisión, diagnóstico por síntoma, auditoría, radar 2026-2027 | ~1.800 |

## TL;DR del área (lo que un Head of Performance debe tener interiorizado)

1. **Meta vende atención y cobra por impresión, pero subasta valor esperado**: total value = puja × tasa de acción estimada, ajustado por calidad/experiencia del usuario. Gana el mayor total value, no la mayor puja; se paga ≈ lo mínimo para ganar. **[OFFICIAL META]** / precio **[STRONG INFERENCE]**
2. **La tasa de acción estimada (por persona, anuncio y contexto) domina el coste**: probabilidades calibradas de CTR/CVR se usan para rankear y para fijar precio. Creativo + oferta + landing + señal mueven más el CPA que cualquier puja. **[OFFICIAL META]**
3. **Cascada**: retrieval (Andromeda; desde Q2-2026 también LLM/generativo) → early ranking → late ranking (modelos runtime destilados de GEM; Adaptive Ranking Model) → subasta → reglas → feedback. GEM no sirve anuncios en tiempo real: enseña. **[OFFICIAL META]**
4. **El creativo es la segmentación**: Meta confirma que creativos demasiado parecidos no se reconocen como distintos y se entregan al mismo público; la base técnica (Semantic ID, retrieval semántico con LLM) está publicada. "Entity ID" y "65% similarity" no son verificables públicamente. **[OFFICIAL META]** / **[HYPOTHESIS]**
5. **Duplicar para escalar y micro-variar para testear son tácticas muertas**: Meta está eliminando la varianza aleatoria entre copias (−43% en predicción; −8,62% A/A'). **[OFFICIAL META]**
6. **Más contexto del usuario, menos valor de la segmentación manual**: secuencias de miles de eventos con leyes de escala sin saturación; GEM central único (oct-2026). **[OFFICIAL META]**
7. **El evento de optimización y la calidad de la señal son la palanca #1** (y las conversiones refrescan la representación del usuario). **[OFFICIAL META]** + **[STRONG INFERENCE]**
8. **CPMs estructuralmente al alza** (precio medio por anuncio +12% YoY en Q1 y Q2-2026) porque la impresión vale más al predecir mejor la conversión; Meta lo dice abiertamente. **[OFFICIAL META]**
9. **El control manual desaparece** (exclusiones DT 2025, opciones DT ene-2026, placements por ad set oct-2026); los controles que quedan son de valor (value rules, cost cap, ROAS goal) y de cuenta. **[OFFICIAL META]**
10. **Broad no siempre gana**: gana con volumen, señal limpia y evento alineado; es arriesgado con señal escasa, proxies baratos, nichos B2B/alto ticket o cuando se mide incrementalidad (Haus: 58% de marcas con mejor iROAS en manual vs Advantage+). **[CONTESTED]**
11. **La atribución de plataforma es parte del bucle de optimización**: validar con Lift/geo-holdouts; incremental attribution existe desde 2025. **[OFFICIAL META]** + **[EMPIRICAL]**
12. **Meta mejora el sistema cada trimestre y su objetivo declarado es la automatización total** ("conecta tu cuenta bancaria, no necesitas creativo, ni segmentación, ni medición", Zuckerberg 2025). Capex 2026: $130-145B. **[OFFICIAL META]**

## Cambios 2025-2026 detectados (con fecha)

- Exclusiones de detailed targeting: ad sets nuevos ~jul-2024; API v22 21-ene-2025; campañas activas 31-mar-2025; boosts 10-jun-2025. 2025 (sin fecha exacta; aún presente en una captura de feb-2025): retirada de la recomendación "máx. 6 anuncios por ad set".
- Q1-2025: GEM en Reels. Abr-2025: Lattice en early-stage ranking. 22-abr-2025: Meta posiciona la diversificación creativa como palanca principal (Andromeda).
- Q2-2025: Andromeda en Facebook Reels; GEM +5% IG/+3% FB; Advantage+ por defecto en Sales y App; incremental attribution global; 4-jun-2025 value rules; 16-jun-2025 anuncios en WhatsApp Status; Threads ads ampliado.
- Ago-2025: consolidación de opciones de DT (ad sets con opciones retiradas dejan de entregar el 15-ene-2026).
- Q3-2025: Advantage+ leads por defecto; retrieval + early-stage fusionados en Facebook (+14% ads quality); ~100 modelos consolidados.
- 10-nov-2025: blog de GEM. 16-dic-2025: chats con Meta AI como señal de anuncios (fuera de UE/UK/Corea).
- Q4-2025: Adaptive Ranking Model en IG (+3% CVR); GEM en todas las superficies; Andromeda en Nvidia/AMD/MTIA; redistribución de ad load ≈4× impacto vs subir ad load.
- Ene-2026: Less Personalized Ads en la UE; fin de ventanas view 7d/28d (12-ene). Mar-2026: engage-through separado de click-through (3-mar); blog ARM (31-mar); REA (17-mar).
- Q1-2026: Lattice+GEM >+6% CVR (LPV); ARM offsite +1,6%; Meta AI business assistant general; AI connectors (beta).
- Q2-2026: **Meta Generative Recommender** (LLMs en retrieval); por separado, +8,3 % clics y +15,7 % conversiones FB atribuidos por Meta a modelos de comprensión de usuario + GEM + sequence learning (no al Generative Recommender); Advantage+ >$75B run-rate; Threads global; FCF $0,78B.
- 3-ago-2026 y 5-ago-2026: posts de entrenamiento de GEM y arquitectura multi-etapa (LLaTTE). 20-24-ago-2026: aviso de retirada de exclusiones de placement por ad set. 24-ago-2026: MTIA 300.
- 12/13-oct-2026: capacidad oportunista de inferencia; **GEM 2026 central único** (+18,9% conv.); retirada de selección manual de placements por ad set en Leads/App/Sales (Engagement no; corrección 2026-11-09).

## Preguntas abiertas del área

1. Forma funcional y pesos del total value; existencia de precios de reserva por superficie/posición.
2. Política exacta de exploración de anuncios nuevos y si existen cuotas o bonus de incertidumbre.
3. Cómo se deduplican/agrupan anuncios semánticamente similares del mismo anunciante en retrieval (¿efecto emergente o regla explícita?).
4. Qué fracción de las mejoras de "conversiones" que reporta Meta es incremental para el anunciante.
5. Impacto real de LPA (UE), iOS 26 y los cambios de atribución de 2026 sobre la calidad de la señal y el rendimiento.
6. Alcance real (superficies, % de tráfico) del Generative Recommender a finales de 2026; resultados de Q3-2026 (pendientes a 16-oct-2026). **Actualización 2026-11-09**: publicados el 21-oct-2026 (precio por anuncio +14 %, impresiones +10 %; GEM +1,7 % offsite y +9,6 % apps; Andromeda +1,4 %; retrieval generativo en el Feed de FB ~+2 %). [OFFICIAL META] (S10-117 en `fuentes/ledger-10-cambios-api-ia.md`)
7. Si la retirada de controles de placement se extenderá a Awareness/Traffic y cómo afectará a brand safety.

## Cómo usar esta carpeta

- Para **diagnóstico** de cuentas: empezar por `09` (tabla de síntomas) y bajar a `02`/`05`/`06` para el mecanismo.
- Para **explicar a clientes** por qué cambió algo: `08` (historia) y `01` (economía de Meta).
- Para **evaluar afirmaciones de gurús**: `04` §7.4 (veredictos sobre creative similarity/Entity ID) y `08` §3 (broad).

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Fecha de fin de exclusiones de detailed targeting: sustituido "21-ene-2025" por el calendario completo (ver 08-historia).
- "+15,7 % conversiones FB" junto a Generative Recommender: en la transcripción de Q2-2026 Susan Li atribuye +8,3 % clics y +15,7 % conversiones a "user understanding models" combinados con GEM y sequence learning; el Generative Recommender se menciona en otra frase. Redacción separada para evitar la atribución errónea que circula en Reddit y blogs.
