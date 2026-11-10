# Modelo de negocio de Meta: cómo gana dinero y qué optimiza (2022-2026)

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A01 (agente) · Ámbito: economía publicitaria de Meta (impresiones × precio, ad load, ARPP, capex en IA) y qué implica para la subasta y el anunciante. Earnings Q3-2026 aún no publicados a esta fecha.

## TL;DR

- **Meta es, en la práctica, una empresa de publicidad**: ~97-98% de los ingresos totales son anuncios ($196,2B de $201,0B en 2025). Todo lo que Meta construye en ranking, IA o producto se justifica, en última instancia, por su efecto en el ingreso publicitario. **[OFFICIAL META]**
- **Ingreso publicitario = impresiones × precio medio por anuncio.** Las impresiones crecen con usuarios × tiempo × ad load; el precio crece cuando los anunciantes pagan más por impresión porque **cada impresión convierte más** (o porque hay más demanda). Meta lo reporta así cada trimestre. **[OFFICIAL META]**
- **2022 fue la crisis (ATT + Reels + macro): impresiones +18% pero precio −16%, ingresos −1%.** 2023: impresiones +28%, precio −9%. Desde 2024 el precio vuelve a subir: 2024 +10%, 2025 +9%, Q1-2026 +12%, Q2-2026 +12%. La recuperación del precio es el reflejo financiero de la mejora de los modelos de predicción de conversión. **[OFFICIAL META]**
- **Meta dice explícitamente que mejorar conversiones sube los CPM**: "cuando entregamos más conversiones por impresión… eso tiene el efecto de seguir elevando los CPM con el tiempo" (Susan Li, Q4-2024). Para el anunciante: **CPM al alza no es necesariamente mala noticia; la métrica que importa es coste por resultado incremental**. **[OFFICIAL META]**
- **El ad load ya no es la palanca principal.** Meta: en 2S-2025, redistribuir anuncios entre usuarios y sesiones (mostrar el anuncio "cuando la persona está más interesada") generó **casi 4× más impacto en ingresos que aumentar el ad load** en Facebook. Frecuencia y momento se optimizan por persona/sesión. **[OFFICIAL META]**
- **Inventario nuevo de menor precio** (Reels en 2022-23; Threads global desde 2025-26; WhatsApp Status 2025-26) entra con ad load bajo y precios inferiores; Meta lo optimiza antes de "subir el suministro". Para anunciantes con placements automáticos, esto significa CPMs medios más bajos pero calidad variable por superficie. **[OFFICIAL META]**
- **Apuesta de capital sin precedentes en IA**: capex 2024 $39,2B → 2025 $72,2B → guía 2026 $130-145B; el free cash flow de Q2-2026 cayó a $0,78B. Meta necesita que la IA eleve la monetización (precio por anuncio) para justificarlo → presión continua hacia automatización (Advantage+, creativos generados, agentes). **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Meta optimiza el valor a largo plazo, no la subasta de hoy**: equilibra (1) experiencia de usuario/retención (que sostiene impresiones futuras), (2) resultados del anunciante (que sostienen la demanda y el precio) y (3) ingresos. La "ad quality"/"user value" en la subasta es el mecanismo formal de ese equilibrio. **[OFFICIAL META]** (marco de dos drivers en cada earnings) + **[STRONG INFERENCE]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Q3-2026 (21-oct)**: impresiones +10 % y precio medio por anuncio +14 % interanual; partnership ads +97 % con más de 15.000 M$ de run-rate; Meta One con más de 15 M de suscripciones. **[OFFICIAL META]**
> - Fuentes: S10-117 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. La ecuación de ingresos

Meta abre cada call de resultados con la misma frase: hay **dos factores** que impulsan los ingresos: (1) "nuestra capacidad de ofrecer experiencias atractivas a nuestra comunidad" y (2) "nuestra eficacia monetizando ese engagement". El segundo se divide en (2a) "optimizar el nivel de anuncios dentro del engagement orgánico" (ad load, ubicación, momento) y (2b) "mejorar el rendimiento para los negocios" (modelos de ranking, productos como Advantage+, creatividad con IA, medición). **[OFFICIAL META]** (transcripciones 2024-2026)

Descomposición operativa:

```
Ingresos publicitarios = Impresiones × Precio medio por anuncio

Impresiones ≈ Personas activas × Tiempo/sesiones × Ad load (anuncios por unidad de contenido)
Precio medio ≈ f(demanda de anunciantes, valor esperado por impresión = P(conversión) × valor de la conversión, mix geográfico y de superficie)
```

- **Impresiones** dependen de engagement (Reels, recomendaciones de IA), usuarios y ad load. Meta reporta impresiones crecientes por "engagement y crecimiento de usuarios, y en menor grado optimizaciones de ad load" (Q4-2025, Q1-2026, Q2-2026).
- **Precio medio por anuncio** sube por (a) "mayor demanda de anunciantes, impulsada en gran parte por la mejora del rendimiento de los anuncios" (fórmula repetida en casi todos los trimestres 2024-2026), (b) macro y divisa, y baja por (c) "crecimiento de impresiones en regiones y superficies de menor monetización".

## 2. Serie histórica clave (datos oficiales)

| Periodo | Ingresos ads / total | Impresiones YoY | Precio medio por anuncio YoY | Comentario oficial |
|---|---|---|---|---|
| 2022 (año) | Total $116,61B (−1%) | +18% | **−16%** | Menor demanda, ATT, Reels de baja monetización, divisa |
| 2023 (año) | Total $134,90B (+16%) | **+28%** | −9% | Más anuncios en regiones/productos de baja monetización (Reels), demanda de anunciantes chinos |
| 2024 (año) | Ads $160,63B; total $164,50B (+22%) | +11% | **+10%** | Q4-2024: impresiones +6%, precio +14% |
| 2025 (año) | Ads $196,18B; total $200,97B (+22%) | +12% | +9% | Q4-2025: impresiones +18%, precio +6% |
| Q1-2025 | Total $42,31B (+16%) | +5% | +10% | GEM lanzado en Reels |
| Q2-2025 | Ads $46,6B (+21%) | +11% | +9% | |
| Q3-2025 | Ads $50,1B (+26%) | +14% | +10% | |
| Q4-2025 | Ads $58,1B (+24%) | +18% | +6% | Redistribución de ad load en FB ≈4× el impacto de subir ad load |
| Q1-2026 | Ads $55,0B (+33%) | +19% | +12% | |
| Q2-2026 | Ads $59,4B (+27%); total $60,8B (+28%) | +14% | +12% | US&Canadá y RoW ~+20/21% precio; APAC ~+1% (secundarias) |

Fuentes: notas de prensa y transcripciones de Meta (investor.atmeta.com, SEC 8-K/10-K). Las cifras por región de Q2-2026 proceden de resúmenes secundarios (dev.to, adsuploader) y la presentación oficial de Q2-2026 (gráfico) que no pude extraer limpiamente.

**Lectura de Head of Performance:**
- **2022-2023 (precio cae, impresiones suben):** Meta inundó el inventario de Reels (más barato) mientras perdía señal (ATT). Para el anunciante: CPMs bajos pero conversiones peor medidas y modelos peor alimentados.
- **2024-2026 (precio sube con fuerza):** los modelos (Andromeda, GEM, Lattice, sequence learning) predicen mejor la conversión → la impresión vale más → los anunciantes pujan más. Para el anunciante: **CPMs al alza estructurales**; la eficiencia viene de la tasa de conversión y del creativo, no de "encontrar inventario barato".
- **Q1-Q2-2026 (impresiones +14-19% y precio +12%):** ambas palancas a la vez; algo que no se veía desde antes de 2021. Parte es divisa y macro, pero Meta lo atribuye mayoritariamente a rendimiento de anuncios. **[OFFICIAL META]**

## 3. ARPP, usuarios y geografía

- Meta dejó de reportar DAU/MAU por app en 2024 y reporta **Family Daily Active People (DAP)** y **ARPP** (ingresos FoA del trimestre / DAP medio). DAP: 3,58B (dic-2025, +7%); 3,60B (jun-2026, +3%). Instagram alcanzó 2.000 millones de DAU (Q2-2026). **[OFFICIAL META]**
- ARPP Q2-2026 ≈ **$16,9** vs ≈ $13,65 en Q2-2025 (cifra de fuente secundaria, consistente con FoA revenue $60,4B / DAP ≈ 3,58B). **[STRONG INFERENCE]** (cálculo de consistencia)
- La monetización por usuario es mucho mayor en US & Canadá que en APAC/RoW; el crecimiento de usuarios viene de mercados de baja monetización, lo que **reduce el precio medio global por anuncio** aunque los precios en EE. UU. suban. **[OFFICIAL META]** (comentarios recurrentes).

**Implicación:** comparar CPMs entre países o "medias del sector" sin controlar mix geográfico/superficie no dice nada. Un CPM global de Meta que sube un 12% puede esconder +20% en EE. UU. y +1% en APAC.

## 4. Ad load, frecuencia y el equilibrio usuario-anunciante-Meta

Citas oficiales relevantes:
- Q4-2024: "seguimos personalizando mejor cuándo aparecen los anuncios, incluidas las ubicaciones óptimas en la profundidad del feed de cada persona, para introducir anuncios cuando es óptimo para el usuario y para los ingresos".
- Q4-2025: "una parte cada vez más importante de este trabajo es encontrar oportunidades de impulsar **conversiones incrementales dentro del mismo nivel global de ad load** determinando cuándo una persona está más interesada en ver un anuncio. De hecho, en la segunda mitad de 2025, nuestras iniciativas en Facebook para **redistribuir anuncios entre usuarios y sesiones** generaron un impacto en ingresos casi **4× mayor** que los aumentos de ad load en Facebook".
- Q2-2025: los anuncios de WhatsApp Status tendrán "un precio medio menor que Facebook o Instagram en el futuro previsible, en parte por… información más limitada que puede usarse para la segmentación".
- Q1/Q2-2026: Threads con anuncios en todo el mundo (expansión completada en Q2-2026); WhatsApp Status con "cientos de millones de personas viéndolos a diario" y más destinos/objetivos de rendimiento.

**Qué intenta optimizar Meta (síntesis):**
1. **Usuario**: que vuelva mañana. Los anuncios son un coste para la experiencia; Meta mide engagement a largo plazo (holdouts de ad load, feedback negativo). Por eso existe el componente de "ad quality"/"user value" en la subasta y el ad load se decide por persona y sesión.
2. **Anunciante**: que obtenga resultados y siga invirtiendo; Meta lo mide en conversiones, tasa de conversión y, cada vez más, incrementalidad (incremental attribution, Q2-2025).
3. **Meta**: maximizar ingresos a largo plazo sujeto a 1 y 2. El mecanismo formal es una subasta que ordena por "total value" (valor para el anunciante ajustado por calidad/valor para el usuario), no por puja pura. **[OFFICIAL META]** (marco) + **[STRONG INFERENCE]** (la forma exacta de la función objetivo no es pública).

**Implicaciones para el anunciante:**
- La frecuencia no la controlas tú en campañas de rendimiento: el sistema redistribuye impresiones a las personas y momentos de mayor valor esperado. Los topes de frecuencia solo existen de forma explícita en objetivos de alcance/awareness. **[OFFICIAL META]** (para ad load) + **[STRONG INFERENCE]**.
- Un anuncio que genera feedback negativo o baja satisfacción **cuesta más** porque el sistema "cobra" el coste para la experiencia de usuario vía calidad. Ver `07-calidad-anuncio-y-diagnosticos-relevancia.md`.

## 5. Capex, IA y por qué Meta empuja la automatización

| Año | Capex (incl. arrendamientos financieros) | Comentario |
|---|---|---|
| 2024 | $39,23B | MTIA en inferencia de ranking; Andromeda con Nvidia |
| 2025 | $72,22B | GEM, Lattice, Meta Superintelligence Labs |
| 2026 (guía Q2-2026) | **$130-145B** | Guía enero: $115-135B → abril: $125-145B → julio: $130-145B; gastos totales $165-169B |

- Q2-2026: free cash flow **$784M** (vs $14,1B en Q4-2025); compromisos contractuales +$107B en Q1-2026 por acuerdos de cloud e infraestructura; reducción de plantilla de ~8.000 empleados en mayo-2026. **[OFFICIAL META]**
- Meta justifica este gasto en parte por los ingresos del negocio central: "estos invertimos de IA están dando resultado" (Zuckerberg, Q2-2026, afirmando que su negocio de anuncios crece más rápido en dólares que cualquier otro negocio publicitario reportado).

**Productos de automatización como motor de ingresos (run-rates oficiales):**
- Advantage+ shopping: >$20B run-rate y +70% YoY (Q4-2024).
- Soluciones end-to-end automatizadas (Sales/App/Leads con Advantage+ activado por defecto): $60B run-rate (Q3-2025) → **>$75B (Q2-2026)**.
- Value optimization suite: >$20B run-rate, más del doble YoY (Q1-2026).
- Partnership ads: $10B run-rate, más del doble YoY (Q1-2026).
- Herramientas de vídeo generativo: $10B run-rate combinado (Q4-2025).
- Incremental attribution: "multi-billion dollar" run-rate siete meses tras su lanzamiento; +24% conversiones incrementales vs atribución estándar con el modelo de Q4-2025.
- WhatsApp paid messaging: >$2B run-rate (Q4-2025); "Family of Apps other revenue" alcanza $1B en Q2-2026.

**Zuckerberg sobre el destino del producto (entrevista en Stratechery, 1-may-2025, vía prensa):** "eres un negocio, vienes a nosotros, nos dices cuál es tu objetivo, conectas tu cuenta bancaria, no necesitas ningún creativo, ni segmentación demográfica, ni medición, salvo para leer los resultados que te damos". Es la declaración más explícita del objetivo de Meta: capturar la función completa de agencia/performance. **[OFFICIAL META]** (cita del CEO vía fuentes secundarias; transcripción original no consultada).

**Meta sobre la automatización total (WSJ, 2-jun-2025, vía Verdict, Campaign Asia y otros):** Meta trabajaría para que, a finales de 2026, una marca pueda dar una imagen de producto y un presupuesto y la IA genere imagen, vídeo, texto, elija audiencias y sugiera presupuesto. Zuckerberg lo describió en la junta de accionistas como un futuro en el que el negocio declara objetivo y presupuesto y Meta hace el resto. **Estado a oct-2026:** parcialmente materializado (Advantage+ por defecto; Meta AI business assistant para todos los anunciantes elegibles en Q1-2026; "Meta Ads AI Connectors" en beta abierta; solución creativa end-to-end y Muse Image en Q2-2026), pero **no he encontrado confirmación oficial de un producto "de imagen + presupuesto a campaña completa" lanzado globalmente**. **[OFFICIAL META]** (piezas) / **UNPROVEN** (automatización completa a fin de 2026).

## 6. Riesgos regulatorios que afectan al delivery

- **UE – Less Personalized Ads (LPA):** desde enero-2026, todos los usuarios del servicio con anuncios en la UE deben elegir entre anuncios personalizados y "menos personalizados" (basados en señales contextuales mínimas). Meta reconoce en su 10-Q que la opción LPA es "menos relevante y efectiva" que su oferta premium. Para anunciantes con peso en la UE: parte del inventario europeo se sirve con mucha menos señal → CPMs y rendimiento distintos por usuario, y menos datos de entrenamiento. **[OFFICIAL META]** (10-Q / Q4-2025 call) + **[HYPOTHESIS]** sobre magnitud.
- **Uso de conversaciones con Meta AI para personalizar anuncios** (anunciado 1-oct-2025, efectivo 16-dic-2025, excluidos UE, Reino Unido y Corea del Sur; temas sensibles excluidos): nueva fuente de señal de intereses. **[OFFICIAL META]** (vía prensa que cita el anuncio).
- Juicios de menores en EE. UU. (2026) y cargos legales ($2,4B en Q2-2026). **[OFFICIAL META]**

## Implicaciones operativas

- **Esperar CPMs estructuralmente al alza** mientras Meta siga mejorando la predicción de conversión y la demanda crezca. Presupuestar con +10-15% de precio por impresión YoY en mercados maduros es razonable para 2026 (**[STRONG INFERENCE]** a partir de la serie oficial). La defensa no es "buscar inventario barato" sino mejorar CVR (oferta, landing, creativo) y la calidad de la señal.
- **Leer los CPMs con el mix**: placements automáticos que se desplazan a Threads/WhatsApp/Reels bajan el CPM medio sin que eso sea mejor ni peor; mirar coste por resultado y, cuando sea posible, incrementalidad.
- **Asumir que Meta empujará defaults automáticos** (Advantage+ activado, creativos generados, agentes): conviene saber exactamente qué palancas quedan bajo control humano y medir con tests de incrementalidad antes de ceder control (ver archivo 09).
- **Para la UE**, planificar que una fracción de usuarios recibe anuncios menos personalizados; medir por país.

## Errores frecuentes

- Interpretar la subida de CPM como "Meta se ha vuelto más cara para mí" sin mirar CVR/CPA.
- Creer que la frecuencia alta es solo culpa de audiencias pequeñas: también la decide el sistema de ad load por sesión.
- Tomar los run-rates de Advantage+ como prueba de que Advantage+ es mejor para todos (es en parte efecto de haberlo activado por defecto).

## Preguntas abiertas

- ¿Qué parte del +12% de precio por anuncio de 2026 es rendimiento real del anunciante vs macro/divisa? (Meta no lo desglosa.)
- ¿Cómo afectará la monetización de Threads y WhatsApp Status a los placements automáticos de anunciantes de rendimiento (calidad de conversión por superficie)?
- ¿Cuánto inventario UE está en LPA y cómo rinde? (No hay datos públicos.)

## Fuentes clave

- Transcripciones de earnings Meta Q4-2024 (29-ene-2025), Q2-2025 (30-jul-2025), Q3-2025 (29-oct-2025), Q4-2025 (28-ene-2026), Q1-2026 (29-abr-2026), Q2-2026 (29-jul-2026) — https://s21.q4cdn.com/399680738/files/doc_financials/… — meta-investors
- [Meta Q4/FY2025 press release (8-K exhibit 99.1)](https://www.sec.gov/Archives/edgar/data/1326801/000162828026003832/meta-12312025xexhibit991.htm) — 2026-01-28 — meta-investors
- [Meta FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680123000013/meta-20221231.htm) — 2023-02 — meta-investors
- [Meta Q4/FY2023 results](https://investor.atmeta.com/investor-news/press-release-details/2024/Meta-Reports-Fourth-Quarter-and-Full-Year-2023-Results-Initiates-Quarterly-Dividend/) — 2024-02-01 — meta-investors
- [Meta Q4/FY2024 results](https://investor.atmeta.com/investor-news/press-release-details/2025/Meta-Reports-Fourth-Quarter-and-Full-Year-2024-Results/default.aspx) — 2025-01-29 — meta-investors
- [Earnings Presentation Q2-2026](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q2/Earnings-Presentation-Q2-2026.pdf) — 2026-07-29 — meta-investors
- [Meta aims to fully automate advertising with AI by 2026 (exchange4media, citando WSJ)](https://www.exchange4media.com/digital-news/meta-aims-to-fully-automate-advertising-with-ai-by-2026-144037.html) — 2025-06-02 — prensa
- [Meta plans to use AI chat data for ad targeting (ppc.land)](https://ppc.land/meta-plans-to-use-ai-chat-data-for-ad-targeting-starting-december/) — 2025-10 — prensa
- [Meta's 2026 DMA report… (ppc.land)](https://ppc.land/metas-2026-dma-report-reveals-whatsapp-ads-a-eu200m-fine-and-a-defiant-stance-on-personalized-advertising/) — 2026 — prensa
- [How Meta's ad prices moved quarter by quarter 2021-2026 (dev.to)](https://dev.to/nacim_lahouioui_8a468ac06/how-metas-ad-prices-moved-quarter-by-quarter-2021-2026-from-metas-own-earnings-reports-29bg) — 2026 — comunidad
