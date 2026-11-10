# La subasta de Meta: elegibilidad, total value, precio y qué controla el anunciante

> Última verificación: 2026-10-15 · Autor: A01 (agente) · Ámbito: mecánica de la subasta de anuncios de Meta (Facebook, Instagram, Messenger, Threads, WhatsApp Status, Audience Network), desde primeros principios y con lo publicado por Meta.

## TL;DR

- **Cada vez que hay una oportunidad de impresión se celebra una subasta entre los anuncios elegibles para esa persona** (Meta-authored paper, 2025). Gana el anuncio con mayor **total value**, no la puja más alta. **[OFFICIAL META]**
- **Total value = valor para el anunciante (puja × tasa de acción estimada) combinado con calidad del anuncio.** Meta lo describe como "una combinación de valor para el anunciante y calidad del anuncio" (2020) y como "combinación de tres factores: puja, tasas de acción estimadas y calidad del anuncio" (paper de ingenieros de Meta, 2023). La forma funcional exacta y los pesos **no son públicos**; las fórmulas que circulan (× o +) son aproximaciones. **[OFFICIAL META]** para los componentes / **[HYPOTHESIS]** para la forma exacta.
- **La "puja" casi nunca la pone el anunciante.** Con *Highest volume / lowest cost* (la estrategia por defecto) el sistema calcula una puja efectiva en cada subasta según presupuesto, pacing y probabilidad de conseguir el evento optimizado. Cost cap, bid cap y ROAS goal solo acotan ese cálculo. **[OFFICIAL META]** (Marketing API docs).
- **La tasa de acción estimada (EAR) es una predicción por persona × anuncio × contexto** de modelos de ranking (GEM destilado, Adaptive Ranking Model…). Las probabilidades calibradas de CTR/CVR se usan **tanto para ordenar como para fijar el precio** (paper LLaTTE de Meta, 2026). Duplicar la tasa de conversión esperada equivale, a efectos de subasta, a duplicar la puja. **[OFFICIAL META]**
- **Calidad del anuncio = modelos que predicen eventos negativos** (cerrar/ocultar el anuncio, "no quiero ver esto"), encuestas de calidad a usuarios (ASQ) y atributos de baja calidad (clickbait, engagement bait, sensacionalismo, landing pages pobres). Penaliza el total value; reincidir puede contaminar a toda la página/dominio/cuenta. **[OFFICIAL META]**
- **Lo que pagas ≈ lo mínimo necesario para ganar** (diseño tipo Vickrey/VCG). Hal Varian (2014) afirma que Facebook usa VCG; Meta ha dicho a anunciantes que "a menudo se cobra menos que la puja". No he encontrado documentación actual de Meta que nombre el mecanismo. **[STRONG INFERENCE]**
- **Consecuencia central:** mejorar CVR, CTR "de calidad" y señales de calidad **baja el precio por resultado sin pujar más**; pujar más solo compra inventario marginal más caro. El anunciante compite en predicción (creativo + oferta + landing + señal), no en puja. **[STRONG INFERENCE]** coherente con la documentación oficial.
- **Relevance diagnostics (quality / engagement rate / conversion rate ranking) NO entran en la subasta**: son informes comparativos frente a anuncios que compiten por el mismo público, con >500 impresiones. Útiles para diagnóstico, no para "optimizar un score". **[OFFICIAL META]** (anuncio 2019, vía prensa especializada).

---

## 1. Primeros principios: por qué una subasta por "total value"

Meta vende **atención** (impresiones) y cobra mayoritariamente **por impresión** (billing event = impressions es el caso general, incluso cuando optimizas para compras). Pero los anunciantes valoran **resultados** (clics, leads, compras). Para comparar a un anunciante que paga por compra con otro que paga por clic o por alcance, Meta necesita convertir todo a **valor esperado por impresión**:

```
Valor esperado para el anunciante por impresión ≈ Puja por acción × P(acción | esta persona ve este anuncio, ahora, aquí)
```

Esto es el clásico eCPM. Pero si Meta solo maximizara eso, llenaría el feed de anuncios que monetizan hoy y espantan a los usuarios mañana (menos sesiones = menos impresiones futuras). Por eso añade un término que representa el **coste/beneficio para el usuario** (calidad). La subasta ordena por:

```
Total value ≈ f( Puja × EAR , Calidad del anuncio )
```

Meta (Good Questions, Real Answers, 11-jun-2020): el total value es "una combinación de valor para el anunciante y calidad del anuncio"; "Facebook usa machine learning para generar la tasa de acción estimada y la puntuación de calidad". El paper de ingenieros de Meta *Towards the Better Ranking Consistency* (arXiv 2307.11096, AdKDD'23) lo describe así: "Para asegurar que el anuncio ganador maximiza el valor tanto para el usuario como para los negocios, usamos total value para ordenar los anuncios en la subasta. El total value es una combinación de tres factores principales: 1) la puja… 2) tasas de acción estimadas que representan la probabilidad del resultado deseado (p. ej. clic, conversión)… 3) calidad del anuncio, que captura el feedback del usuario sobre su experiencia con anuncios… determinada por modelos de calidad que predicen puntuaciones de múltiples eventos de calidad (p. ej. tachar anuncios, ocultar anuncios)". **[OFFICIAL META]**

> **Sobre "× o +":** materiales antiguos de Facebook (infografía de Blueprint) presentaban "Advertiser bid × Estimated action rates + Ad quality = Total value". Algunas guías escriben "× calidad". Meta no publica coeficientes. Lo operativamente relevante es: (a) la calidad puede hacer ganar a una puja menor; (b) EAR multiplica la puja. **[CONTESTED]** la forma exacta; irrelevante para decisiones.

## 2. Elegibilidad: quién entra en la subasta

Antes de que la subasta compare valores, un anuncio tiene que ser **elegible** para esa oportunidad concreta:

1. **Restricciones del anunciante:** ubicación, edad, idioma, audiencias (incluidas exclusiones), placements, horario (solo con presupuesto total), presupuesto disponible y pacing, límites de gasto de cuenta, frecuencia (solo en Reach & Frequency/awareness con tope).
2. **Revisión y política:** anuncio aprobado; restricciones de categorías especiales (vivienda, empleo, crédito, temas sociales/políticos) que limitan la segmentación. Fuera de mi alcance detallarlo (ver área 08).
3. **Retrieval:** de decenas de millones de anuncios, Andromeda (y desde 2026 un primer modelo generativo) recupera unos pocos miles **relevantes para esa persona**. Un anuncio elegible por segmentación que no es recuperado no compite. Ver `03-pipeline…` y `04-sistemas-ml…`.
4. **Early-stage ranking:** modelos ligeros reducen los candidatos y pasan los mejores al ranking final. Meta reconoce el problema de "consistencia": el early stage puede descartar anuncios que el final stage habría puntuado alto (paper 2023); por eso entrena el early stage para imitar al final (CTR + eventos de calidad) y en Q3-2025 fusionó retrieval y early-stage en Facebook. **[OFFICIAL META]**
5. **Auction overlap (solapamiento con tus propios ad sets):** cuando varios ad sets del mismo anunciante son elegibles para la misma persona, Meta evita que pujes contra ti mismo y deja entrar al de mayor total value; los demás pueden infra-entregar. Descrito por Meta en Ads Manager (diagnóstico "auction overlap") y por practitioners como Jon Loomer; no he podido descargar la página oficial actual. **[STRONG INFERENCE]**
6. **Usuarios en "Less Personalized Ads" (UE, desde ene-2026)** reciben anuncios elegidos con señales contextuales mínimas: para ellos la elegibilidad/ranking funciona con mucha menos información. **[OFFICIAL META]**

**Implicación:** "mi anuncio no gasta" puede ser un problema de **elegibilidad/retrieval** (público estrecho, creativo poco recuperable, solapamiento interno, puja/coste objetivo demasiado bajo) antes que de subasta.

## 3. Componente 1 — La puja (lo que realmente controlas)

Fuente: Marketing API, *Bid strategy* y *Bidding overview* (Meta Developers, vigente 2026):
- Meta "evalúa tu `bid_strategy`, `bid_amount` y la probabilidad de conseguir tu `optimization_goal`" para calcular una **puja efectiva**; el objetivo es que "solo ganes subastas y tus anuncios se entreguen" cuando es probable conseguir el objetivo dentro de tus restricciones de coste.
- **Highest volume (LOWEST_COST_WITHOUT_CAP):** "Meta puja automáticamente por ti… puede aumentar tu puja efectiva según sea necesario"; útil si "quieres gastar todo tu presupuesto"; "sin control sobre tu coste".
- **Bid cap (LOWEST_COST_WITH_BID_CAP):** sube la puja "pero no supera tu límite" por subasta; "puede no gastar todo el presupuesto"; "la puja no es el coste que verás en informes".
- **Cost per result goal (COST_CAP):** "obtener el máximo de resultados mientras Meta se esfuerza por cumplir el CPA fijado"; "no se garantiza"; "puede no gastar todo el presupuesto"; "el coste puede subir a medida que se agotan las oportunidades más baratas"; requiere pacing estándar y billing por impresiones.
- **ROAS goal (LOWEST_COST_WITH_MIN_ROAS):** suelo de ROAS medio; "fijarlo demasiado alto puede llevar a infra-entrega".
- El **billing event** (impresión vs clic) "no impacta directamente en `bid_amount` ni en tu puja efectiva"; lo que determina a quién se muestra es el **optimization goal**.

**Desde primeros principios:**
- Con presupuesto como restricción y lowest cost, el sistema actúa como un **controlador de pacing**: ajusta un multiplicador de puja para gastar el presupuesto a lo largo del día, empezando por las oportunidades de mayor valor esperado por euro. Por eso **subir presupuesto = comprar oportunidades marginalmente peores** (CPA medio sube si el inventario de alta probabilidad ya estaba cubierto). **[STRONG INFERENCE]** (consistente con "el coste puede subir a medida que se agotan las oportunidades más baratas").
- **Cost cap/bid cap** recortan la cola de oportunidades caras; a cambio, entrega menos y más volátil. Útiles cuando el margen por conversión es conocido y estricto; peligrosos con poca señal (el sistema tiene menos confianza en su EAR y se retrae). **[STRONG INFERENCE]**

**Value rules (desde 4-jun-2025; todos los objetivos desde ago-2025 según terceros):** ajustes de puja de **+1.000% a −90%** por edad, género, ubicación, sistema operativo y placement (hasta 10 reglas por conjunto, 2 criterios por regla; solo se aplica la primera regla que coincide). Meta advierte que el coste por resultado "puede aumentar". Desde la óptica de la subasta, son **multiplicadores sobre el componente "puja"** del total value para segmentos concretos: la forma moderna de expresar "este público vale más/menos para mi negocio" sin excluirlo. No permiten excluir (el recorte máximo es −90%), por lo que no sirven para requisitos de cumplimiento de "cero entrega". Con la retirada de controles de placement por ad set (ago-oct-2026), son la herramienta residual de control por placement. **[OFFICIAL META]** (vía PPC Land / Social Media Today) + **[STRONG INFERENCE]** (interpretación en el total value).

Detalle de bid strategies y escalado: ver área 09 (bidding-escalado). Aquí solo importa el papel en la subasta.

## 4. Componente 2 — Tasas de acción estimadas (EAR)

- Definición oficial (2020): modelos que predicen "cuán probable es que una persona concreta realice la acción elegida por el anunciante", usando comportamiento dentro y fuera de la plataforma, contenido del anuncio, hora del día e interacciones pasadas con anuncios. **[OFFICIAL META]**
- Arquitectura actual (2025-2026): modelos runtime destilados de GEM; secuencias de miles de eventos del usuario; features semánticas del creativo; Adaptive Ranking Model que dedica más cómputo cuando la probabilidad de conversión es alta. **[OFFICIAL META]** (ver archivo 04).
- **Calibración y precio:** LLaTTE (Meta, 2026): "Estas probabilidades calibradas se utilizan tanto para el ranking aguas abajo como para el pricing de la subasta". **[OFFICIAL META]**
- **Cascada de predicción:** el modelo de CTR "es esencial para estimar las tasas de acción de diversas conversiones post-clic" (paper Meta 2023). Las conversiones se predicen típicamente como P(clic) × P(conversión | clic) más caminos view-through. **[OFFICIAL META]** (CTR como base) + **[STRONG INFERENCE]** (factorización exacta).
- **Feedback retrasado:** Lattice Zipper entrena cabezas de predicción por ventana de atribución (90 min, 1 día, 7 días) y sirve con la de ventana más larga. **[OFFICIAL META]**

**Por qué EAR domina en la práctica:**
Supón dos anunciantes con la misma puja de 50 € por compra. A predice P(compra) = 0,2% para una persona; B predice 0,4%. El valor para el anunciante por impresión es 0,10 € vs 0,20 €. B gana con la misma puja, o puede pujar la mitad y empatar. En la vida real, la diferencia entre un creativo/oferta mediocre y uno excelente en EAR es mucho mayor que cualquier diferencia razonable de puja. **[STRONG INFERENCE]** (aritmética del modelo oficial).

**Qué mueve tu EAR (palancas reales):**
1. Creativo que atrae a quien compra (no solo a quien hace clic): Meta predice el evento optimizado, no el clic.
2. Oferta y precio (afectan P(conversión|clic)).
3. Landing page/experiencia post-clic (velocidad, coherencia con el anuncio).
4. Evento de optimización bien elegido y bien medido (pixel + CAPI, deduplicación, valor).
5. Historial del anuncio/cuenta (datos acumulados) y similitud semántica con anuncios que funcionaron (cold start).

## 5. Componente 3 — Calidad del anuncio

- Oficial (2020): la calidad refleja "feedback de las personas que ven u ocultan un anuncio, más evaluaciones de atributos de baja calidad como exceso de texto, lenguaje sensacionalista o engagement bait". **[OFFICIAL META]**
- Meta-authored (2023): determinada por modelos que predicen **eventos de calidad** (p. ej. "cross-out": pulsar "×" y "No quiero ver esto"; ocultar anuncios) y métricas de encuesta (**Ads Survey for Quality, ASQ**: valoración estimada del usuario). **[OFFICIAL META]**
- Atributos de contenido de baja calidad (Help Center vía Jon Loomer, mar-2024/2025): **withholding information (clickbait), sensationalized language, engagement bait**. Experiencias post-clic de baja calidad: contenido sin sustancia u original, volumen de anuncios desproporcionado, pop-ups/intersticiales, contenido inesperado, experiencias engañosas. Efecto: peor entrega y costes; en extremo, rechazo; reincidencia → "nuestros sistemas pueden empezar a considerar todos los anuncios de tu página, dominio, cuenta publicitaria u otras entidades asociadas como de menor calidad". **[OFFICIAL META]** (cita del Help Center 423781975167984, verificada vía fuente secundaria).
- Velocidad de la landing: desde 2016 Meta declaró que la velocidad del sitio móvil es un factor que su sistema de entrega usa para decidir qué anuncios mostrar a quién (prefetching incluido). **[OFFICIAL META]** (2016, vía prensa) — sigue siendo plausible, no reconfirmado en 2025-2026.

Detalle completo y relevance diagnostics: ver `07-calidad-anuncio-y-diagnosticos-relevancia.md`.

## 6. Cómo se fija el precio

- Meta no publica un documento actual que nombre el mecanismo. Evidencia:
  - Varian & Harris (*The VCG Auction in Theory and Practice*, AER P&P 2014): "Facebook usa una subasta Vickrey-Clarke-Groves (VCG)". Otros papers académicos lo repiten. **[STRONG INFERENCE]** (fuente externa autorizada pero de 2014).
  - Charla de Eric Sodomka (Facebook) en Simons Institute (2015): "El ranking y el pricing de los anuncios dependen de la probabilidad predicha de clics y conversiones". **[OFFICIAL META]** (empleado, 2015).
  - Materiales de Facebook citados por AdEspresso: "a menudo se te cobra menos que tu puja". **[OFFICIAL META]** vía secundaria.
  - Paper LLaTTE (2026): probabilidades calibradas usadas en "auction pricing". **[OFFICIAL META]**
- **Intuición VCG:** el ganador paga el "daño" que causa a los demás (el total value que habrían obtenido sin él), no su puja. Con una sola posición, se reduce a "lo mínimo necesario para superar al segundo", convertido a tu unidad de cobro con tu EAR. Si tu EAR es alto, el mismo umbral de total value se alcanza con menos dinero → pagas menos por impresión ganada. **[STRONG INFERENCE]**
- **Posición y contexto:** un email interno de Facebook (2020) aportado en el caso DOJ v. Google menciona que los precios de los anuncios se fijan en la subasta según la posición en que aparecen. Coherente con que ad load y posición en el feed son decisiones de Meta por sesión. **[STRONG INFERENCE]** (fuente única).

**Implicación clave:** como pagas el umbral marcado por la competencia, tu CPM refleja **cuánto valen otros anunciantes esa misma atención**. En Q4/Black Friday la competencia sube el umbral para todos; ninguna puja "inteligente" te exime. Lo único que baja tu coste efectivo es un EAR/calidad mayor que el de la competencia para esa persona.

## 7. Competencia, inventario y estacionalidad

- **Precio medio por anuncio** global 2025: +9%; Q1-Q2-2026: +12% YoY (Meta). La mejora de predicción y la demanda presionan los CPMs al alza; el crecimiento de inventario en superficies/regiones de menor monetización (Reels 2022-23; Threads, WhatsApp Status 2025-26) los presiona a la baja en la media. **[OFFICIAL META]**
- **La competencia es por persona, no por "audiencia".** Un público "barato" en el agregado puede contener personas carísimas (alta intención, objetivo de muchos anunciantes). Por eso el CPM de un ad set broad baja o sube según a quién decide servir el sistema. **[STRONG INFERENCE]**
- **Placements:** el sistema compara oportunidades entre superficies con el mismo marco de total value; restringir placements elimina oportunidades baratas sin mejorar EAR en las restantes. Excepción legítima: un creativo inadecuado para un placement bajará su EAR/calidad allí y el sistema lo infra-entregará igualmente. **[STRONG INFERENCE]**

## 8. Ejemplo numérico (ilustrativo)

| Anunciante | Puja/acción | EAR (P de compra por impresión) | Valor anunciante por impresión | Ajuste calidad (ilustrativo) | Total value (ilustrativo) |
|---|---|---|---|---|---|
| A — puja alta, creativo genérico | 60 € | 0,10% | 0,060 € | −0,010 € (feedback negativo) | 0,050 € |
| B — puja menor, creativo y oferta fuertes | 40 € | 0,20% | 0,080 € | +0,000 € | 0,080 € |
| C — puja media, clickbait | 50 € | 0,15% | 0,075 € | −0,030 € | 0,045 € |

B gana pese a pujar menos. Con un mecanismo tipo segundo precio, B pagaría aproximadamente lo necesario para superar a A (0,050 € de total value), es decir, ≈0,050 € por esa impresión (≈50 € de CPM), muy por debajo de su valor (0,080 €). **Cifras inventadas para ilustrar el mecanismo; no son datos de Meta.** **[HYPOTHESIS]** (ilustración)

## Implicaciones operativas

- **La palanca #1 de coste es la tasa de conversión esperada** (creativo + oferta + landing + señal), no la puja. Antes de tocar bid caps, mejora CVR y calidad.
- **No pongas cost caps "aspiracionales"**: un CPA objetivo por debajo de lo que el mercado permite produce infra-entrega, no CPAs mágicos.
- **Evita la canibalización interna**: estructuras con muchos ad sets solapados reparten señal y activan auction overlap.
- **Vigila feedback negativo** (comentarios, ocultaciones) y engagement bait: encarecen todas las impresiones del anuncio y, si reincides, de la cuenta.
- **Lee el CPM como precio de mercado**, y el CPA como resultado de tu EAR frente a ese mercado.

## Errores frecuentes

- "Gana quien más puja" → FALSE.
- "El relevance score/quality ranking decide la subasta" → FALSE (diagnóstico informativo).
- "Bajar la puja abarata los resultados" → CONTEXT-DEPENDENT: puede abaratar el CPA medio a costa de volumen (recortas la cola cara), pero no cambia tu competitividad por impresión.
- "El CPM alto significa que el anuncio es malo" → CONTEXT-DEPENDENT: puede significar que el sistema te está sirviendo a personas de alta intención disputadas.

## Preguntas abiertas

- Forma funcional y pesos exactos del total value (y si varían por superficie/objetivo).
- Si existe precio de reserva por superficie/posición y cómo se fija.
- Cómo se valora "ad quality" en usuarios LPA de la UE y en WhatsApp Status (menos señal).

## Fuentes clave

- [Good Questions, Real Answers: How Does Facebook Use Machine Learning to Deliver Ads?](https://www.facebook.com/business/news/good-questions-real-answers-how-does-facebook-use-machine-learning-to-deliver-ads) — 2020-06-11 — meta-oficial
- [Towards the Better Ranking Consistency: A Multi-task Learning Framework for Early Stage Ads Ranking (arXiv 2307.11096)](https://arxiv.org/abs/2307.11096) — 2023-07 — academico (Meta)
- [LLaTTE (arXiv 2601.20083)](https://arxiv.org/abs/2601.20083) — 2026-01 — academico (Meta)
- [Marketing API – Bid strategy](https://developers.facebook.com/documentation/ads-commerce/marketing-api/bidding/overview/bid-strategy.md) y [Bidding overview](https://developers.facebook.com/docs/marketing-api/bidding/overview) — vigente 2026 — meta-developers
- [Marketing API – Pacing and scheduling](https://developers.facebook.com/docs/marketing-api/bidding/overview/pacing-and-scheduling) — vigente 2026 — meta-developers
- [Varian & Harris, The VCG Auction in Theory and Practice](https://courses.cs.washington.edu/courses/cse490z/20sp/slides/Varian.pdf) — 2014 — academico
- [On How Machine Learning and Auction Theory Power Facebook Advertising (Simons Institute)](https://simons.berkeley.edu/talks/how-machine-learning-auction-theory-power-facebook-advertising) — 2015-11-17 — academico/meta
- [Characterizing and Minimizing Divergent Delivery in Meta Advertising Experiments (arXiv 2508.21251)](https://arxiv.org/abs/2508.21251) — 2025-08 — academico (Meta)
- [Jon Loomer – Low-Quality Ad Content and Post-Click Experiences](https://www.jonloomer.com/low-quality-ad-content-and-post-click-experiences/) — 2024-03 (act. 2025-03) — practitioner
- [AdEspresso – Everything you need to know about Facebook ads bidding](https://adespresso.com/blog/everything-need-know-facebook-ads-bidding) — antiguo — practitioner
