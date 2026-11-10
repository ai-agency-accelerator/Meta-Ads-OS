# Historia y evolución de Meta Ads (2012-2026): por qué murieron las tácticas antiguas y cuándo broad NO gana

> Última verificación: 2026-10-16 · Autor: A01 (agente) · Ámbito: cronología técnica y de producto de Meta Ads, causas de los cambios, tácticas obsoletas y evaluación crítica de "broad siempre gana".

## TL;DR

- **La historia de Meta Ads es la historia de un desplazamiento de control: del anunciante (segmentación, estructura, puja) al sistema (predicción por persona).** Tres fuerzas lo explican: (1) **pérdida de señal** off-platform (2018 Partner Categories, 2021 ATT, 2026 LPA en la UE), (2) **presión regulatoria/reputacional** sobre la segmentación (2018-2022, 2025), y (3) **saltos de capacidad de ML** (2019 Power 5 → 2023 Lattice → 2024 Andromeda → 2025 GEM → 2026 LLMs). **[STRONG INFERENCE]** sobre hechos **[OFFICIAL META]**.
- **2015-2019 (hipersegmentación)**: intereses, LAL 1%, exclusiones finas, decenas de ad sets, "audience testing", pujas manuales. Funcionaba porque el modelo era débil y la señal off-platform (pixel sin restricciones) muy rica: la segmentación aportaba información que el modelo no tenía. **[STRONG INFERENCE]**
- **2021 es la bisagra (ATT/iOS 14.5, 26-abr-2021)**: pérdida de señal de conversión en iOS, ventanas de atribución recortadas (7d click/1d view por defecto desde ene-2021), AEM; Meta estimó ≈$10B de impacto en 2022. 2022: impresiones +18% pero **precio por anuncio −16%** e ingresos −1%. **[OFFICIAL META]**
- **2022-2023 (consolidación y automatización)**: ODAX (6 objetivos), portfolio "Meta Advantage" (mar-2022), Advantage+ shopping (ago-2022), Advantage+ audience (2023, intereses/LAL pasan a ser "sugerencias"), eliminación de miles de opciones de detailed targeting (19-ene-2022), Lattice (2023), herramientas generativas (2023). **[OFFICIAL META]**
- **2024-2026 (era de los modelos fundacionales)**: Andromeda (2S-2024), sequence learning (2024), GEM (2025), Advantage+ por defecto en Sales/App/Leads (2025), eliminación de exclusiones de detailed targeting (ene-2025), incremental attribution (2025), Adaptive Ranking Model (Q4-2025), LLMs en retrieval/ranking ("Meta Generative Recommender", Q2-2026), GEM central único (oct-2026). **[OFFICIAL META]**
- **Tácticas OUTDATED**: hipersegmentación por intereses como palanca principal, LAL 1% como "audiencia ganadora", decenas de ad sets por audiencia, duplicar ad sets para escalar, exclusiones de detailed targeting, "máximo 6 anuncios por ad set", micro-variaciones creativas como "testing". **[OUTDATED]** (con fechas y causas abajo).
- **¿Broad siempre gana? No. CONTEXT-DEPENDENT.** Gana (o empata con menos trabajo) cuando hay **volumen de conversiones, señal limpia y un evento alineado con el valor**. Pierde o es arriesgado con: señal escasa o nueva, evento proxy mal alineado (leads baratos), nichos B2B/alto ticket donde el comprador es una fracción minúscula, restricciones de negocio duras, y cuando se mide por atribución de plataforma en vez de incrementalidad (Haus: en 58% de marcas, campañas manuales dieron mejor iROAS que Advantage+). **[CONTESTED]** con evidencia de ambos lados.

---

## 1. Cronología

### 2012-2014: los cimientos de la segmentación con datos propios
- **2012**: Custom Audiences (subir listas de clientes; fecha exacta entre ago y dic-2012 según fuentes). **2013 (20-mar)**: Lookalike Audiences. **2013**: Partner Categories con brokers de datos (Acxiom, Epsilon, Experian, Oracle…). **[EMPIRICAL]** (prensa de la época)
- 2014: pacing de primer/último día proporcional a horas restantes (Marketing API, 9-abr-2014). **[OFFICIAL META]**

### 2015-2019: hipersegmentación y "Power 5"
- 2015: pixel unificado; *relevance score* 1-10. Optimización por conversión (oCPM) consolidada: se paga por impresión y el sistema busca la conversión. **[EMPIRICAL]**
- Práctica dominante: decenas de ad sets por intereses y LAL (1%, 1-3%, 3-5%), exclusiones, segmentación por "intereses apilados", pujas manuales, "audience testing" como palanca principal. **[EMPIRICAL]**
- **Mar-2018**: tras Cambridge Analytica, Meta cierra **Partner Categories** (datos de terceros) — UK/DE/FR en mayo, resto el 1-oct-2018. **[OFFICIAL META]** (vía TechCrunch/The Drum)
- **Mar-2019**: relevance score sustituido por **relevance diagnostics** (30-abr-2019). Acuerdos con organizaciones de derechos civiles → **Special Ad Categories** (vivienda, empleo, crédito) con segmentación restringida. **[OFFICIAL META]**
- **2019 — "Power 5"** (recomendaciones de Facebook): Account Simplification, Campaign Budget Optimization, Automatic Placements, Dynamic Ads, Auto Advanced Matching. Facebook planeó hacer CBO obligatorio (sept-2019/2020) y dio marcha atrás. **[EMPIRICAL]** (prensa y agencias)
- **Ali et al. (CSCW 2019)**: incluso con segmentación neutra, la entrega se sesga por género/raza debido a la optimización del sistema y a efectos de mercado (algunos públicos son más caros por competencia). Prueba temprana de que **el algoritmo, no la segmentación, decide a quién**. **[EMPIRICAL]** (académico)

### 2020: la calma antes de ATT
- COVID: caída y rebote de CPMs; boom de e-commerce. Jun-2020 Apple anuncia ATT; dic-2020 Meta anuncia AEM. Meta publica "Good Questions, Real Answers" explicando total value (jun-2020). **[OFFICIAL META]**

### 2021: ATT y la gran pérdida de señal
- **19-ene-2021**: ventana de atribución por defecto pasa a 7 días click / 1 día view; desaparecen 28d click y ventanas largas de view. **[EMPIRICAL]** (Loomer y otros; fechas con discrepancias menores)
- **26-abr-2021**: iOS 14.5 con **ATT**. AEM limita a 8 eventos priorizados por dominio para iOS; retrasos y modelado de conversiones. (El requisito de ranking de 8 eventos se relajó en 2023 según Loomer/Dept; algunas fuentes hablan de 2025.) **[OFFICIAL META]** / **[CONTESTED]** fecha de relajación.
- **9-nov-2021**: Meta anuncia la retirada de opciones de detailed targeting sobre temas sensibles (salud, orientación sexual, religión, política, etnia), efectiva **19-ene-2022**; en la práctica se retiraron miles de opciones (también por poco uso/redundancia). **[OFFICIAL META]**
- Oct-2021: Facebook pasa a llamarse Meta.

### 2022: crisis y consolidación
- Q4-2021 call: impacto de ATT estimado en **≈$10B en 2022** (Dave Wehner: "es una estimación"). **[OFFICIAL META]**
- **2022 (año)**: impresiones +18%, precio por anuncio **−16%**, ingresos $116,61B (−1%), por menor demanda, ATT, Reels de baja monetización y divisa. **[OFFICIAL META]**
- **ODAX** (anunciado dic-2021, desplegado en 2022): 11 objetivos → 6 (Awareness, Traffic, Engagement, Leads, App promotion, Sales). **[OFFICIAL META]**
- **Mar-2022**: portfolio **"Meta Advantage"** (lookalike expansion → Advantage lookalike; detailed targeting expansion → Advantage detailed targeting; automatic placements → Advantage+ placements; automated app ads → Advantage+ app campaigns). **[OFFICIAL META]** (vía Search Engine Land)
- **Ago-2022**: **Advantage+ shopping campaigns** (una campaña sin ad sets, hasta 150 anuncios, audiencia/placement/presupuesto automáticos). **[OFFICIAL META]** (prensa)

### 2023: "año de la eficiencia" y modelos unificados
- **Lattice** empieza a desplegarse en late-stage ranking (Meta, Q2-2025 y Q3-2025 calls). **[OFFICIAL META]**
- **Advantage+ audience** se convierte en el default: edad, género, intereses, custom audiences y LAL pasan a ser **sugerencias**; controles duros solo para ubicación, edad mínima, exclusiones de custom audiences e idioma. Meta cita −33% coste por resultado en un experimento mar-jun 2023 (vía Loomer). **[OFFICIAL META]** (vía practitioner)
- AI Sandbox y primeras herramientas generativas (fondos, expansión de imagen, variaciones de texto) integradas en Advantage+ creative. **[OFFICIAL META]**
- **2-nov-2023**: flexibilidad de presupuesto diario +75% (antes +25%), tope 7× semanal; programación de presupuesto. **[OFFICIAL META]** (vía Loomer)
- 2023 (año): impresiones +28%, precio −9% (Reels y regiones de baja monetización). **[OFFICIAL META]**
- **Variance Reduction System** para anuncios de vivienda en EE. UU. (acuerdo con DOJ; ene-2023). **[OFFICIAL META]**

### 2024: Andromeda, sequence learning y gen AI masivo
- MTIA en inferencia de ranking/recomendación. **[OFFICIAL META]**
- **19-nov-2024**: sequence learning (event-based features) "ampliamente adoptado". **2-dic-2024**: **Andromeda** (introducido en 2S-2024): retrieval con 10.000× capacidad, +8% ads quality. **[OFFICIAL META]**
- Image Animation (oct-2024); >4M anunciantes con herramientas generativas (Q4-2024); ASC >$20B run-rate (+70%). **[OFFICIAL META]**
- 19-nov-2024: Meta recomienda ≥20 anuncios diversificados en ASC y 20-30% del presupuesto a testing. **[OFFICIAL META]**
- 2024 (año): impresiones +11%, precio +10%. **[OFFICIAL META]**

### 2025: GEM, Advantage+ por defecto y medición incremental
- **Exclusiones de detailed targeting (calendario completo)**: desaparecen en ad sets nuevos de Ads Manager hacia jul-ago-2024 (Meta avisó de que las existentes seguirían hasta ene-2025); **21-ene-2025** = Marketing API v22 (error al añadir exclusiones nuevas; todas las versiones desde 21-abr-2025); **31-mar-2025** = retiradas de las campañas activas en Ads Manager; **10-jun-2025** = boosts. Meta cita un test con −22,6 % de coste mediano por conversión sin exclusiones. **[OFFICIAL META]** (Help Center "Updates to detailed targeting" y changelog v22)
- **Feb-2025**: Meta retira la recomendación de "máximo 6 anuncios por ad set" (Loomer). **[EMPIRICAL]**
- **Q1-2025 (call 30-abr-2025)**: Meta presenta **GEM** ("2× más eficiente para una cantidad dada de datos y cómputo"; hasta +5% conversiones en Facebook Reels); tests de incremental attribution con +46% de conversiones incrementales medias vs business-as-usual; inicio (abril) del flujo simplificado de Sales/App/Leads con Advantage+ activado desde el principio; anuncios de Threads abiertos en >30 mercados; impresiones +5%, precio +10%. Zuckerberg: los negocios declararán objetivo y precio máximo por resultado "y nosotros hacemos el resto"; la publicidad como "un agente de IA que entrega resultados de negocio medibles a escala". **[OFFICIAL META]**
- **Q2-2025**: GEM ~+5% IG, ~+3% FB; Andromeda a Facebook Reels (~+4%); Lattice en early-stage (abr-2025); **Advantage+ sales** (antes Advantage+ shopping) con flujo simplificado: Advantage+ activado desde el principio en Sales y App; **incremental attribution** global; Omnichannel ads. **[OFFICIAL META]**
- **22-abr-2025**: Meta publica "The Creative Advantage… with Meta Andromeda": la palanca pasa "de la segmentación de nicho a la diversificación creativa". **[OFFICIAL META]**
- **May-2025**: ads en Threads para la mayoría de países; **16-jun-2025**: anuncios en **WhatsApp Status** (Updates tab) con señales limitadas (país/ciudad, idioma, canales seguidos, interacción con anuncios). **[OFFICIAL META]**
- **1-may-2025 (entrevista en Stratechery)**: Zuckerberg describe el destino: "eres un negocio, vienes a nosotros, nos dices cuál es tu objetivo, conectas tu cuenta bancaria, no necesitas ningún creativo, ni segmentación demográfica, ni medición, salvo para leer los resultados que te damos". **[OFFICIAL META]** (declaración del CEO, vía prensa; transcripción original no consultada).
- **2-jun-2025 (WSJ)**: Meta querría permitir automatizar por completo creación y segmentación de anuncios a finales de 2026. **[OFFICIAL META]** no confirmado; reportado por prensa.
- **4-jun-2025**: **Value rules** (ajustes de puja de +1.000% a −90% por edad, género, ubicación, sistema operativo y placement; hasta 10 reglas con 2 criterios; solo aplica la primera que coincide) para Sales y App; ampliadas a todos los objetivos en ago-2025 según terceros. Meta advierte que el coste por resultado "puede aumentar". Es el sustituto conceptual de segmentar/excluir: **decir a la subasta cuánto vale cada segmento** en lugar de prohibirlo. **[OFFICIAL META]** (vía PPC Land / Social Media Today)
- **Ago-2025**: Meta combina/retira más opciones de detailed targeting; **desde el 15-ene-2026 los ad sets con opciones no disponibles dejan de entregar** (aviso en Ads Manager). **[OFFICIAL META]** (vía The Keyword)
- **2025 (oct, año no confirmado en fuentes)**: opción "Allow limited spend to excluded placements", activada por defecto en Sales y Leads: hasta un 5% del presupuesto por cada placement excluido cuando se predice que mejora el rendimiento. **[OFFICIAL META]** (texto de la interfaz citado por Loomer/PPC Land)
- **Q3-2025**: Advantage+ leads con flujo simplificado (todos los Sales/App/Leads con automatización end-to-end); $60B run-rate; Andromeda fusiona retrieval y early-stage en Facebook (+14% ads quality); Lattice a app ads (~+3%); ~100 modelos eliminados desde 2023. **[OFFICIAL META]**
- **1-oct-2025 / 16-dic-2025**: conversaciones con Meta AI como señal de personalización de anuncios (excl. UE, UK, Corea del Sur). **[OFFICIAL META]** (vía prensa)
- **Oct-2025**: anuncio de cambios de atribución para 2026 (ver abajo). **[EMPIRICAL]** (agencias)
- **Q4-2025**: nuevo modelo runtime en IG Feed/Stories/Reels (+3% CVR) = Adaptive Ranking Model; GEM en todas las superficies; Andromeda en Nvidia/AMD/MTIA; redistribución de ad load ≈4× impacto vs subir ad load; incremental attribution +24% conversiones incrementales. **[OFFICIAL META]**
- 2025 (año): ingresos $200,97B, impresiones +12%, precio +9%, capex $72,2B. **[OFFICIAL META]**

### 2026 (hasta 16-oct)
- **Ene-2026**: **Less Personalized Ads** en la UE (todos los usuarios con anuncios deben elegir). **12-ene-2026**: eliminación de ventanas view de 7 y 28 días (máximo view: 1 día). **3-mar-2026**: click-through pasa a contar solo **link clicks**; likes/comentarios/compartidos/saves pasan a **engage-through** (1 día). **[OFFICIAL META]** (LPA) / **[EMPIRICAL]** (atribución, múltiples agencias; detalle en área 04).
- **Q1-2026**: Lattice + GEM >+6% CVR en anuncios de landing page view; ARM a conversiones offsite (+1,6%); Meta AI business assistant para todos los anunciantes elegibles; **Meta Ads AI Connectors** (beta abierta: conectar la cuenta a agentes de IA); MTIA para entrenamiento de ranking. **[OFFICIAL META]**
- **17-mar-2026**: REA (agente que itera modelos de ranking). **31-mar-2026**: blog del Adaptive Ranking Model. **[OFFICIAL META]**
- **May-2026**: reducción de ~8.000 empleados. **[OFFICIAL META]**
- **Q2-2026**: **Meta Generative Recommender** (LLMs en retrieval; +8,3% clics y +15,7% conversiones en Facebook con GEM + sequence learning); Threads con anuncios en todo el mundo; Advantage+ >$75B run-rate; Muse Image para generación creativa; capex 2026 $130-145B. **[OFFICIAL META]**
- **5-ago-2026**: arquitectura multi-etapa de secuencias (LLaTTE). **13-oct-2026**: GEM 2026 (modelo central único, +18,9% conversiones). **[OFFICIAL META]**
- **Feb-2026**: flujo de creación unificado (Advantage+ activado por defecto en audiencia, placements y presupuesto, desactivables uno a uno) según agencias; Marketing API v25.0 con estructura Advantage+ unificada en la que exclusiones de placement solo se permiten a nivel de cuenta. **[EMPIRICAL]** (fuentes secundarias)
- **20-24-ago-2026**: aviso en algunas cuentas: "Excluir placements, plataformas, dispositivos y sistemas operativos dejará de estar disponible para tus ad sets"; sustitutos: value rules por placement/dispositivo/SO (recorte máximo −90%, no exclusión) y control de placements a nivel de cuenta. **[EMPIRICAL]** (Loomer, Coinis, PPC Land; despliegue parcial)
- **13-oct-2026**: Meta elimina la selección manual de placements a nivel de ad set en **Leads, App promotion y Sales** (Engagement no; corrección 2026-11-09) (se mantiene en Awareness y Traffic); exclusiones de placement a nivel de cuenta por objetivo en los seis objetivos; Meta cita un experimento con −11,7% CPA medio (≈−10% coste por resultado según otra fuente) para Advantage+ placements frente a manual. **[OFFICIAL META]** (vía Social Samosa/PPC Land; metodología no publicada)
- **~17-sep-2026 (anecdótico)**: miembros de Foxwell reportan CPMs −30% en varios países con caída de CTR y compras. Sin confirmación de Meta. **[HYPOTHESIS]**

## 2. Por qué murieron las tácticas antiguas

| Táctica | Estado | Desde | Por qué murió (primeros principios) |
|---|---|---|---|
| Hipersegmentación por intereses como palanca principal | **[OUTDATED]** | 2021-2023 | Los intereses son señales pobres (≈30% inexactos según NC State 2022) frente a secuencias de miles de eventos; con conversión como objetivo, el sistema expande igualmente (Advantage detailed targeting) y la restricción solo quita inventario. Muchos intereses eliminados (ene-2022). |
| LAL 1% como "audiencia ganadora" | **[OUTDATED]** (útil como sugerencia) | 2022-2023 | El LAL era un atajo para dar al sistema "a quién se parecen mis compradores"; hoy el modelo lo aprende directamente de la señal de conversión. En Advantage+ audience es una sugerencia, no un límite. |
| Decenas de ad sets por audiencia ("audience testing") | **[OUTDATED]** | 2019 (Power 5) → 2023 | Fragmenta la señal, multiplica learning phases, crea auction overlap. Lattice/GEM aprenden transversalmente: la granularidad del anunciante ya no aporta información. |
| Duplicar ad sets/anuncios para escalar o "resetear" | **[OUTDATED]** | 2024-2026 | Dependía en parte de varianza aleatoria (A/A variance por hashing de IDs) que Meta está eliminando (Semantic ID −43%; LLM retrieval −8,62% A/A'). Divide la señal. |
| Exclusiones de detailed targeting | **[OUTDATED]** (eliminadas) | ene-2025 | Retiradas por Meta; usar controles de cuenta y exclusión de custom audiences. |
| "Máximo 6 anuncios por ad set" | **[OUTDATED]** | feb-2025 | Retrieval de Andromeda escala a más candidatos; Meta recomienda más diversidad (≥20 en ASC). |
| Micro-variaciones creativas (color, fondo, hook mínimo) como testing | **[OUTDATED]** | 2024-2026 | Meta: creativos demasiado parecidos no se reconocen como distintos y van al mismo público. |
| Pujas manuales como palanca de rendimiento por defecto | **CONTEXT-DEPENDENT** | 2018+ | Siguen útiles con márgenes estrictos y volumen alto; como palanca general, el EAR (creativo/oferta/señal) domina. |
| Restringir placements por defecto (solo Feed/IG) | **[OUTDATED]** en conversión (desde oct-2026 ya no es posible a nivel de ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09)) | 2019 (Power 5) → 2026 | Quita inventario; GEM aprende entre superficies. Para control residual: value rules por placement (hasta −90%) y exclusiones a nivel de cuenta. |
| Ventanas de 28 días click / 7 días view | **[OUTDATED]** | 2021 / 2026 | Eliminadas por ATT (2021) y por Meta (view 7d/28d en ene-2026). |

## 3. ¿Broad siempre gana? Evaluación crítica

### 3.1 Evidencia a favor de broad/Advantage+ audience
- **Teoría**: el sistema predice EAR por persona con mucha más información que cualquier segmentación manual; restringir solo puede quitar oportunidades (con la salvedad de que la restricción aporte información que el modelo no tiene). **[STRONG INFERENCE]**
- **Meta**: Advantage+ audience −33% coste por resultado (experimento mar-jun 2023; −28% en coste por clic/lead/LPV; −13% coste mediano por venta de catálogo; −7% coste mediano por conversión web, vía Loomer). Eliminar exclusiones de DT: ~22% mejor coste por conversión. Advantage+ sales: −9% CPA medio con el flujo nuevo (abr-2025). **[OFFICIAL META]** (autoinformado)
- **Practitioner**: Jon Loomer (sept-2024, 30 días, $2.250, A/B en Experiments): Advantage+ audience sin sugerencias ≥ detailed targeting y > lookalikes en registros y en calidad de registros; diferencia vs DT no significativa, vs LAL sí. Cuenta con 10 años de pixel y >100k visitas/mes. **[EMPIRICAL]**
- **Investigación**: intereses inferidos ≈30% inexactos (NC State, 2022). **[EMPIRICAL]** (académico, muestra pequeña)

### 3.2 Evidencia y condiciones en contra (o "depende")
1. **Señal escasa o cuenta nueva**: sin historial de conversiones, el sistema tiene menos con qué discriminar; las sugerencias de audiencia actúan como prior. Loomer advierte que sus resultados dependen de una cuenta con mucha historia. **[STRONG INFERENCE]**
2. **Evento proxy mal alineado** (leads de formulario, registros gratuitos, add-to-cart): broad encuentra muy bien a quien completa el proxy, no a quien genera valor. Una audiencia restringida puede contener información de calidad que el evento no transmite. Solución preferible: mejorar el evento (CRM/conversion leads, valor). **[STRONG INFERENCE]** + **[EMPIRICAL]** (consenso de practitioners en lead gen).
3. **Nichos B2B y alto ticket**: comprador = fracción minúscula de la plataforma; pocos positivos; ciclo largo. Varios practitioners sostienen que segmentaciones por cargo/empresa + custom audiences rinden mejor en estos casos (sin datos controlados publicados). **[CONTESTED]**
4. **Incrementalidad**: Haus (640 tests, marcas con gasto medio $14M/año): Advantage+ +2,4% ROAS de plataforma vs manual, pero −12% iROAS DTC; 58% de marcas con mejor iROAS en manual; Advantage+ por delante a mitad de test (+9%) y por detrás al final. **No es "broad vs intereses"** (manual puede ser broad), pero sí muestra que **más automatización no garantiza más incrementalidad**. **[EMPIRICAL]** (vendor)
5. **Retargeting implícito**: broad/Advantage+ gastan una parte en clientes existentes (Loomer: ~9% del gasto en remarketing en todos los tipos de audiencia). Para objetivos de adquisición, hay que usar controles (exclusión de custom audiences, ajustes de clientes existentes donde estén disponibles). **[EMPIRICAL]**
6. **Restricciones de negocio duras**: área de servicio, idioma, edad legal, categorías especiales. No son "segmentación para rendimiento", son límites. **[OFFICIAL META]**
7. **Mercados/segmentos donde se quiere aprender algo específico** (test de un nuevo segmento): la segmentación sirve para responder preguntas de negocio aunque cueste eficiencia. **[STRONG INFERENCE]**

### 3.3 Veredicto
- "Broad siempre gana" → **FALSE** como afirmación universal; **TRUE en la mayoría de cuentas de e-commerce/app con volumen, señal limpia y evento alineado**; **CONTEXT-DEPENDENT** en lead gen, B2B, alto ticket, cuentas nuevas y cuando se mide incrementalidad.
- Lo que sí es casi universal en 2026: **la segmentación manual aporta poca información al sistema; el creativo y el evento aportan mucha.** Si una restricción mejora resultados, suele ser porque compensa un evento mal definido o una señal pobre; arreglar eso suele dar más que mantener la restricción. **[STRONG INFERENCE]**

## Implicaciones operativas

- Partir de broad/Advantage+ audience con controles duros solo donde el negocio lo exige; usar sugerencias como prior en cuentas con poca señal.
- Si broad "no funciona", diagnosticar en este orden: (1) evento de optimización y calidad de señal, (2) creativo (¿habla al comprador correcto?), (3) volumen/estructura, (4) solo entonces, restricciones de audiencia como experimento con medición incremental.
- Retirar de los playbooks: estructuras por intereses, duplicación para escalar, micro-variantes como testing.
- Releer cualquier "best practice" anterior a 2023 con sospecha: probablemente asumía modelos débiles y señal abundante.

## Errores frecuentes

- Explicar todo cambio de rendimiento con "la actualización de Andromeda" (Andromeda es de 2S-2024 y se itera trimestralmente).
- Usar resultados de plataforma (ROAS atribuido) para concluir que Advantage+/broad es mejor.
- Asumir que porque una táctica funcionó en 2019 "el algoritmo la castiga" ahora: más bien dejó de aportar información.

## Preguntas abiertas

- ¿Se materializará en 2026 la automatización completa (imagen + presupuesto → campaña) reportada por WSJ?
- Efecto real de LPA en la UE sobre rendimiento y sobre la utilidad de la segmentación (¿vuelve a importar el contexto/creativo aún más?).
- ¿Qué parte del cambio de CPMs de sep-2026 reportado por practitioners es real y a qué se debe?

## Fuentes clave

- Earnings Meta Q4-2021 (vía CNBC), Q4-2024, Q2-2025, Q3-2025, Q4-2025, Q1-2026, Q2-2026 — meta-investors
- [Meta FY2022 10-K](https://www.sec.gov/Archives/edgar/data/1326801/000132680123000013/meta-20221231.htm) — 2023 — meta-investors
- [TechCrunch – Facebook will cut off access to third party data for ad targeting](https://techcrunch.com/2018/03/28/facebook-will-cut-off-access-to-third-party-data-for-ad-targeting) — 2018-03-28 — prensa
- [Jon Loomer – Facebook Removed Thousands of Detailed Targeting Options](https://www.jonloomer.com/facebook-removed-thousands-of-detailed-targeting-options/) — 2022-01 — practitioner
- [Search Engine Land – Meta rebrands automated ad products](https://searchengineland.com/meta-advantage-suite-383020) — 2022-03 — prensa
- [Jon Loomer – Advantage+ Sales Replaces Advantage+ Shopping](https://www.jonloomer.com/qvt/advantage-sales-replaces-advantage-shopping/) — 2025 — practitioner
- [Jon Loomer – Test Results: Advantage+ Audience vs. Detailed Targeting and Lookalikes](https://www.jonloomer.com/test-results-advantage-plus-audience-detailed-targeting-lookalikes/) — 2024-09-09 — practitioner
- [Jon Loomer – Advantage+ Audience Best Practices Guide](https://www.jonloomer.com/advantage-plus-audience-best-practices-guide/) — 2024-2025 — practitioner
- [Ali et al. – Discrimination through Optimization (arXiv 1904.02095)](https://arxiv.org/abs/1904.02095) — 2019 — academico
- [Search Engine Land – Facebook interest categories may be up to 33% inaccurate](https://searchengineland.com/study-facebook-ads-interest-categories-may-be-up-to-33-inaccurate-383295) — 2022-03 — prensa (estudio NC State)
- [Haus – The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [PPC Land – Meta removes detailed targeting exclusions](https://ppc.land/meta-removes-detailed-targeting-exclusions-for-ad-accounts/) — 2025-01 — prensa
- [TechCabal – WhatsApp Status ads](https://techcabal.com/2025/06/16/whatsapp-status-ads/) — 2025-06-16 — prensa
- [Jetfuel – Meta Attribution 2026: 1-Day vs 7-Day (Jan 12 Update)](https://jetfuel.agency/meta-ads-attribution-settings-2026/) — 2026 — agencia
- [An Update on Our Ads Fairness Efforts](https://about.fb.com/news/2023/01/an-update-on-our-ads-fairness-efforts/) — 2023-01 — meta-oficial
- [Social Media Examiner / Disruptive / Wpromote – Facebook Power 5](https://disruptiveadvertising.com/ppc/facebook-power-5/) — 2019 — agencia

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Línea "21-ene-2025: eliminación de exclusiones de detailed targeting": la fecha corresponde al changelog de la Marketing API v22, no a la retirada en Ads Manager. El Help Center (Updates to detailed targeting, 458835214668072, leído 2026-10-16) fecha la retirada en campañas activas el 31-mar-2025 y en boosts el 10-jun-2025; Social Media Today (5-ago-2024) documenta la retirada en ad sets nuevos en 2024. Corregido con el calendario completo.
