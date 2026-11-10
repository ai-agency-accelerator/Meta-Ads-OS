# Calidad del anuncio y diagnósticos de relevancia (quality / engagement rate / conversion rate ranking)

> Última verificación: 2026-10-16 · Autor: A01 (agente) · Ámbito: qué es "ad quality" en la subasta, qué la degrada (feedback negativo, clickbait, engagement bait, landing pages pobres), efectos a nivel cuenta, y cómo leer los relevance diagnostics.

## TL;DR

- **La calidad del anuncio es un componente del total value**: modelos de ML predicen la probabilidad de eventos negativos (pulsar "×"/"No quiero ver esto", ocultar, denunciar) y la valoración en encuestas de calidad (Ads Survey for Quality, ASQ), más evaluaciones de atributos de baja calidad. Penaliza (o premia) el total value con el que compites. **[OFFICIAL META]** (Meta 2020; paper de ingenieros de Meta 2023).
- **Tres atributos oficiales de contenido de baja calidad**: *withholding information* (clickbait que oculta información para forzar el clic), *sensationalized language* y *engagement bait* (pedir likes/comentarios/compartidos). **Cinco de experiencia post-clic**: falta de contenido sustantivo u original, volumen desproporcionado de anuncios, pop-ups/intersticiales, contenido inesperado, experiencias engañosas. **[OFFICIAL META]** (Help Center vía Jon Loomer, 2024-2025).
- **La mala calidad se contagia**: "si publicas repetidamente anuncios que infringen políticas o de menor calidad, nuestros sistemas pueden empezar a considerar todos los anuncios de tu página, dominio, cuenta publicitaria u otras entidades asociadas como de menor calidad"; la recuperación "puede llevar tiempo". **[OFFICIAL META]**
- **Relevance diagnostics no entran en la subasta** ("no se tienen en cuenta en el rendimiento del anuncio en la subasta", Facebook, mar-2019). Son **percentiles relativos** frente a anuncios que compiten por el mismo público (y, en conversion rate ranking, con el mismo objetivo de optimización); requieren >500 impresiones. Niveles: Above average, Average (≈percentil 35-55), Below average (bottom 35% / 20% / 10%). **[OFFICIAL META]** (definiciones) / **[EMPIRICAL]** (percentiles, fuentes secundarias).
- **"Ads quality" en earnings ≠ quality ranking**: cuando Meta reporta "+8% / +12% / +14% ads quality" (Andromeda, Lattice) habla de una métrica interna agregada del sistema, no de tu diagnóstico. **[STRONG INFERENCE]**
- **La calidad no es estética: es la experiencia que predice el usuario.** Un anuncio "feo" (UGC, lo-fi) puede tener calidad alta; uno pulido con promesa engañosa, baja. **[STRONG INFERENCE]**
- **Diagnóstico combinado** útil: quality bajo + engagement/conversion medio → el creativo genera rechazo (promesa, tono, repetición); engagement alto + conversion bajo → atrae curiosos o la landing no cumple; quality y engagement altos + conversion bajo → problema post-clic/oferta. **[EMPIRICAL]** (práctica habitual) coherente con las definiciones oficiales.

---

## 1. Qué es "ad quality" desde dentro

- **Meta (11-jun-2020)**: la puntuación de calidad refleja "feedback de las personas que ven u ocultan un anuncio, más evaluaciones de atributos de baja calidad como exceso de texto, lenguaje sensacionalista o engagement bait"; se genera con machine learning. **[OFFICIAL META]**
- **Ingenieros de Meta (arXiv 2307.11096, 2023)**: la calidad "captura el feedback del usuario sobre su experiencia con anuncios… determinada por modelos de calidad de anuncios que predicen puntuaciones de múltiples eventos de calidad (p. ej. tachar anuncios, ocultar anuncios)". Métricas: **Ads cross-out (Xout)** —pulsar "×" y "No quiero ver esto"— y **ASQ (Ads Survey for Quality)**, "una métrica basada en encuestas… estima la valoración del usuario sobre los anuncios". Los modelos de calidad son uno de los dos grandes costes de serving junto al modelo de CTR (es decir, se calculan para **cada** candidato en el ranking). **[OFFICIAL META]**
- **Por qué existe** (primeros principios): un anuncio que monetiza hoy pero provoca rechazo reduce sesiones futuras y, por tanto, impresiones futuras (para todos los anunciantes). La calidad internaliza ese coste en la subasta. **[STRONG INFERENCE]**

**Señales que alimentan la calidad (consolidado):**
| Señal | Tipo | Evidencia |
|---|---|---|
| Ocultar anuncio / "No quiero ver esto" / ocultar todos los anuncios del anunciante / "lo veo demasiado" | Feedback explícito negativo | Oficial (2020, 2023) |
| Denuncias | Feedback explícito negativo | Oficial (política) |
| Encuestas de calidad (ASQ) | Feedback declarado | Oficial (paper 2023) |
| Atributos de contenido de baja calidad (clickbait, sensacionalismo, engagement bait) | Clasificadores de contenido | Oficial (Help Center) |
| Experiencia post-clic (landing) | Clasificadores + comportamiento | Oficial (Help Center; newsroom 2017) |
| Velocidad de carga móvil | Factor de entrega (2016) | Oficial vía prensa (2016) — no reconfirmado en 2025-2026 |
| Comentarios negativos / sentimiento | Probable señal | **[HYPOTHESIS]** — no he encontrado confirmación oficial explícita |

## 2. Atributos de baja calidad (oficiales)

**Contenido del anuncio** (Help Center 1767120243598011, vía Loomer):
1. **Withholding information (clickbait)**: ocultar información a propósito para que la persona tenga que hacer clic para entender el contexto ("No creerás lo que pasó…").
2. **Sensationalized language**: lenguaje exagerado o sensacionalista que no se corresponde con la realidad del producto/landing.
3. **Engagement bait**: pedir explícitamente likes, comentarios, compartidos, etiquetas o votos con reacciones.

**Experiencia post-clic (landing page):**
1. Falta de contenido sustantivo u original (páginas delgadas, copiadas).
2. Volumen desproporcionado de anuncios respecto al contenido.
3. Pop-ups o intersticiales.
4. Contenido inesperado (la landing no corresponde a lo prometido).
5. Experiencias engañosas (p. ej. ocultar costes de envío o condiciones).

**Efectos (Meta, vía Loomer):** demasiados elementos de baja calidad "pueden impactar negativamente la entrega y los costes"; en extremo, rechazo (política *Low Quality or Disruptive Content*); reincidencia → contagio a página/dominio/cuenta; tras corregir, el rendimiento mejora "con el tiempo". **[OFFICIAL META]**

**Histórico relevante:** mayo-2017 Meta empezó a degradar enlaces a páginas con poco contenido cubiertas de anuncios disruptivos/maliciosos y advirtió que esas páginas "pueden no ser elegibles como anuncio" (newsroom). 2016: velocidad de la web móvil como factor de entrega. 2018: endurecimiento contra clickbait y sensacionalismo en anuncios. **[OFFICIAL META]**

## 3. Relevance diagnostics

### 3.1 Qué son (oficial)
- Introducidos en 2019 (sustituyen al *relevance score* 1-10 de 2015 a partir del 30-abr-2019). Facebook: "estos diagnósticos de relevancia no se tienen en cuenta en el rendimiento del anuncio en la subasta". **[OFFICIAL META]** (vía Social Media Today, 13-mar-2019)
- **Quality ranking**: "cómo se compara la calidad percibida de tu anuncio con la de los anuncios que compiten por el mismo público".
- **Engagement rate ranking**: "cómo se compara la tasa de engagement esperada de tu anuncio con la de los anuncios que compiten por el mismo público" (clics, reacciones, comentarios, compartidos, expansiones).
- **Conversion rate ranking**: "cómo se compara la tasa de conversión esperada de tu anuncio con la de anuncios con el mismo objetivo de optimización que compiten por el mismo público".
- Disponibles a nivel de anuncio con **>500 impresiones**; no disponibles para ciertas optimizaciones (p. ej. alcance, impresiones, ad recall, algunas de valor/custom conversions) ni quality ranking para dynamic creative (según fuentes secundarias). Datos de los últimos ~35 días (secundaria). **[OFFICIAL META]** / **[EMPIRICAL]**.
- Niveles: **Above average**, **Average** (≈ percentiles 35-55), **Below average — bottom 35%**, **bottom 20%**, **bottom 10%**. **[EMPIRICAL]** (consistente en múltiples fuentes secundarias; no he podido descargar la página oficial).

### 3.2 Cómo leerlos sin engañarse
- **Son relativos al "mismo público"**, que en campañas broad/Advantage+ es enorme y heterogéneo: un "Below average" en engagement puede ser normal para un anuncio de conversión directa que compite con contenido de entretenimiento. **[STRONG INFERENCE]**
- **Son expectativas del modelo**, no resultados observados: "expected engagement rate", "expected conversion rate". **[OFFICIAL META]**
- **Matriz de diagnóstico práctica** (EMPIRICAL, coherente con definiciones):

| Quality | Engagement | Conversion | Lectura probable | Acción |
|---|---|---|---|---|
| Bajo | Medio/alto | Medio | El anuncio llama la atención pero genera rechazo (clickbait, tono, promesa, repetición) | Revisar promesa/tono; eliminar engagement bait; comprobar comentarios |
| Medio/alto | Alto | Bajo | Atrae a curiosos o la landing/oferta no cumple | Ajustar mensaje hacia el comprador; revisar landing y oferta |
| Medio/alto | Bajo | Medio/alto | Anuncio "aburrido" pero eficaz con quien convierte | No tocar si el CPA es bueno |
| Bajo | Bajo | Bajo | Creativo no conecta con el público elegido por el sistema | Nuevo concepto |
| Todos altos | — | — | Buen anuncio; si el CPA es malo, mirar oferta, precio, competencia o señal | Revisar fuera del creativo |

- **No optimizar "para el diagnóstico"**: el objetivo es CPA/ROAS (idealmente incremental). Los rankings sirven para encontrar el **cuello de botella** (pre-clic vs post-clic vs rechazo). **[STRONG INFERENCE]**

## 4. "Ads quality" en los earnings de Meta

Meta reporta mejoras de "ads quality" del sistema: Andromeda +8% (Q4-2024), +14% en Facebook al fusionar retrieval y early-stage (Q3-2025); Lattice +12% (Q4-2025), +11,5% en el paper. Es una métrica interna agregada (relevancia/satisfacción con los anuncios mostrados), **no** el quality ranking de tu anuncio. Lectura: Meta está mejorando su capacidad de mostrar anuncios que la gente no rechaza; lo que eleva el listón competitivo de calidad para todos. **[STRONG INFERENCE]**

## 5. Calidad, creatividad y la era Andromeda/GEM
- Creativos casi idénticos al mismo público aumentan fatiga y feedback negativo por repetición ("ocultar: lo veo demasiado"); Meta advierte que creativos demasiado parecidos se muestran al mismo público y pueden activar "Creative limited"/"Creative fatigue". **[OFFICIAL META]**
- Contenido generado con IA: la calidad la juzga el usuario; Meta reporta mejoras de CVR con sus herramientas generativas (p. ej. +3% CVR con vídeo generado en tests, Q1-2026), lo que sugiere que no hay penalización por ser IA per se. **[OFFICIAL META]** (cifra autoinformada) / sin evidencia pública de penalización específica a contenido IA → **UNPROVEN** cualquier afirmación en contra.

## Implicaciones operativas

- **Auditar la landing** con la lista oficial de 5 atributos post-clic antes de escalar.
- **Eliminar engagement bait** ("comenta SÍ", "etiqueta a…") de anuncios de rendimiento: el posible engagement extra no compensa la penalización de calidad.
- **Moderar comentarios** y responder: no está confirmado que el sentimiento de comentarios entre en calidad, pero sí afecta a la conversión social (prueba social). **[HYPOTHESIS]**
- **Rotar conceptos** para evitar ocultaciones por repetición.
- **Proteger la cuenta/dominio**: una campaña agresiva de clickbait puede degradar la calidad percibida de todas tus campañas; separar experimentos arriesgados no protege si comparten página/dominio.

## Errores frecuentes

- Creer que los relevance diagnostics deciden la subasta.
- Comparar diagnósticos entre campañas con públicos distintos.
- Pensar que "calidad" = producción cara.
- Ignorar la landing como parte de la calidad del anuncio.

## Preguntas abiertas

- Peso relativo de la calidad en el total value (no publicado).
- Si el sentimiento de comentarios es señal de calidad (no confirmado).
- Cuánto dura el "contagio" de baja calidad a nivel de cuenta/dominio (Meta solo dice "puede llevar tiempo").
- Estado actual exacto de los relevance diagnostics en 2026 (no he podido verificar cambios recientes en la página oficial).

## Fuentes clave

- [Good Questions, Real Answers: How Does Facebook Use Machine Learning to Deliver Ads?](https://www.facebook.com/business/news/good-questions-real-answers-how-does-facebook-use-machine-learning-to-deliver-ads) — 2020-06-11 — meta-oficial
- [Towards the Better Ranking Consistency (arXiv 2307.11096)](https://arxiv.org/abs/2307.11096) — 2023-07 — academico (Meta)
- [Jon Loomer – Low-Quality Ad Content and Post-Click Experiences](https://www.jonloomer.com/low-quality-ad-content-and-post-click-experiences/) — 2024-03-07 (act. 2025-03-06) — practitioner (cita Help Center 423781975167984, 1767120243598011, 617541753336634)
- [Reducing Links to Low-Quality Web Page Experiences](https://about.fb.com/news/2017/05/reducing-links-to-low-quality-web-page-experiences/) — 2017-05-10 — meta-oficial
- [Social Media Today – Facebook's phasing out its ad relevance score](https://www.socialmediatoday.com/news/facebooks-phasing-out-its-ad-relevance-score-removing-six-ad-metrics/550343/) — 2019-03-13 — prensa
- [PPC Land – Facebook replaces relevance score with ad relevance diagnostics](https://ppc.land/facebook-replaces-relevance-score-with-a-new-ad-relevance-diagnostics/) — 2019 — prensa
- [Interest Explorer – Facebook Ad Quality Ranking](https://interestexplorer.io/facebook-ad-quality-ranking/) — s.f. — vendor
- [MarTech – Facebook pressures advertisers to cut mobile page load speeds](https://martech.org/facebook-pressures-advertisers-cut-mobile-page-load-speeds-itll-cut-reach/) — 2016 — prensa
- [Maximize conversions with differentiated ad creative](https://www.facebook.com/business/m/small-business/creative-differentiation) — vigente 2026 — meta-oficial
- Earnings Meta Q4-2024, Q3-2025, Q4-2025, Q1-2026 — meta-investors
