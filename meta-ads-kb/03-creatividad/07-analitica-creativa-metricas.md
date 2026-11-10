# Analítica creativa: métricas, fórmulas, qué predicen y qué engañan

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A03 (agente) · Ámbito: métricas de atención, clic, post-clic y negocio para evaluar creativos; definiciones exactas, fórmulas, trampas y árbol de diagnóstico. La atribución y la medición incremental las cubre el área 04; la economía (MER, márgenes), el área 09.

## TL;DR

- **Las métricas de atención diagnostican; no predicen negocio por sí solas.** En un análisis de 11 marcas (Spearman intra-cuenta, 90 días, 2026), hook rate (−0,19), hold rate (−0,10) y CTR (+0,02) no se correlacionaron con ROAS, mientras que la tasa de conversión post-clic (+0,39 ROAS / −0,46 CPA) y el AOV (+0,37) sí. **[EMPIRICAL]** (muestra pequeña, agencia; S03-042)
- **El CTR temprano no predice la longevidad**: el tercio de creatividades con mejor CTR en sus 3 primeros días tuvo *menos* impresiones de vida (mediana 168k) que el tercio con peor CTR (325k) (Interconnections, 2026). **[EMPIRICAL]** (S03-039)
- **"Hook rate" y "hold rate" no son métricas oficiales de Meta**: son ratios construidos con métricas oficiales (3-second video plays, ThruPlays, plays at X%), y cada equipo los define de forma distinta. Hay que fijar la fórmula y no comparar benchmarks de terceros con fórmulas distintas. **[EMPIRICAL]** (S03-044)
- **ThruPlay = reproducción completa o de al menos 15 s** (Meta habla de completar el 97% en vídeos cortos). Eso **infla el "hold rate" de los vídeos cortos** (≤15 s), que cuentan como ThruPlay al terminar. No es evidencia de que lo corto funcione mejor. **[OFFICIAL META]** definición / **[EMPIRICAL]** efecto (S03-036)
- **Jerarquía de clics:** link clicks (todos los enlaces del anuncio, incluidas experiencias dentro de Meta como lead forms o mensajes) ≥ outbound clicks (solo clics que salen de Meta) ≥ landing page views (la página cargó y el pixel se disparó). Para tráfico web, **outbound CTR y la ratio LPV/outbound** son más fiables que el CTR "all". **[OFFICIAL META]** (definiciones de Ads Manager reproducidas por Jon Loomer)
- **Desde mar-2026, el click-through solo cuenta conversiones tras un clic en enlace.** Likes, comentarios, compartidos y guardados pasan a "engage-through" (1 día) junto con las vistas de vídeo de ≥5 s. Configuración por defecto: 7d clic + 1d engage-through + 1d view. Las comparaciones de creativos que cruzan esa fecha mezclan definiciones. **[EMPIRICAL]** (S03-043; detalle en el área 04)
- **La métrica principal para decidir sobre un creativo es el coste por resultado de negocio** (CPA/ROAS con la atribución elegida, idealmente validado con datos propios, CRM o lift), **con un volumen suficiente** (05). Las de atención sirven para saber **qué parte** del anuncio arreglar. **[STRONG INFERENCE]**
- **Gasto como métrica de creativo:** con CBO/ASC, el gasto que Meta asigna es una predicción del sistema y Motion lo usa para definir "winner" (≥10x la mediana de gasto de la cuenta y ≥$500). Pero gasto ≠ rentabilidad: "a winner can still be ROAS-negative". **[EMPIRICAL]** (S03-010)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Desglose por asset** (Help Center 1822387965412520; público el 27-oct): Breakdown → Creative → **Media** (cada imagen o vídeo), **Dynamic creative element** (variantes de texto) y **Ad delivery** (medios retirados); no cubre *Show as carousel/collection*. **[OFFICIAL META]** Úsalo para hipótesis: el reparto lo decide el sistema y cada asset hereda la atribución del anuncio.
> - **API**: breakdown `pa_creator_ig_handle` (partnership ads por creador, 5-nov; no combinable); `total_video_consumption_rate` sin datos desde principios de nov-2026 (si sale a cero, no es un fallo tuyo). **[OFFICIAL META]**
> - Fuentes: S10-101, S10-102, S10-106, S10-128 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. Definiciones (métricas oficiales de Ads Manager)

| Métrica | Definición | Notas |
|---|---|---|
| Impressions | Veces que el anuncio estuvo en pantalla | Incluye repeticiones |
| Reach | Personas únicas (estimadas) que vieron el anuncio al menos una vez | Estimación; no se puede sumar entre periodos |
| Frequency | Impressions / Reach | Media; esconde distribuciones muy sesgadas |
| CPM | Coste / impresiones × 1.000 | Lo mueven la subasta, la audiencia, el placement y la calidad estimada |
| 3-second video plays | Reproducciones de ≥3 s (o casi la duración total si el vídeo dura <3 s) | Base del "hook rate" |
| ThruPlays | Reproducciones completas o de al menos 15 s (Meta: 97% de la duración para vídeos cortos) | Existe también un objetivo de ThruPlay de 6 s en algunos contextos; hay discrepancia entre páginas de Meta según terceros (S03-044) |
| Video plays at 25/50/75/95/100% | Reproducciones que alcanzaron ese % de la duración, "including plays that skipped to this point" | Útiles para curvas de retención |
| Video average play time | Tiempo medio de reproducción | El espectador mediano ve ~4 s (Biddyco) |
| Link clicks | Clics en enlaces del anuncio hacia destinos especificados por el anunciante, **dentro o fuera** de Meta (web, app, lead form, mensajes, etc.) | No equivale a "visitas a la web" |
| Outbound clicks | Clics que llevan **fuera** de Meta (web, app store, deep link) | Mejor base para tráfico web |
| Landing page views (LPV) | Clics que acabaron en la carga de la landing con el pixel disparado | Requiere pixel; filtra clics accidentales y abandonos rápidos |
| CTR (all) | Clics de cualquier tipo / impresiones | Incluye clics en perfil, "ver más", expandir; inflado y poco útil |
| Link CTR / Outbound CTR | Link (u outbound) clicks / impresiones | La versión útil |
| Unique CTR / unique outbound CTR | Personas únicas que hicieron clic / reach | Reduce el efecto de clicadores repetidos |
| CPC (link / outbound) | Coste / link (outbound) clicks | Combina CPM y CTR: CPC = CPM / (1.000 × CTR) |
| Conversions / results | Eventos atribuidos según la ventana elegida | Ver atribución (área 04) |
| CPA / Cost per result | Coste / resultados | Ruido alto con poco volumen |
| ROAS (purchase ROAS) | Valor de conversión atribuido / gasto | Atribución del propio Meta; sobreestima la incrementalidad (área 04) |
| Ad relevance diagnostics (quality, engagement rate, conversion rate ranking) | Ranking del anuncio frente a otros que compiten por la misma audiencia (desde 2019) | Meta dijo que no se usan en la subasta; disponibilidad y umbral (~500 impresiones) no verificados en 2026 |

Fuentes: definiciones de Ads Manager reproducidas por Jon Loomer y terceros (link/outbound/LPV), Dema (ThruPlay, 2025) y guías 2026. **No se ha podido descargar el Help Center oficial**; las definiciones coinciden entre fuentes.

## 2. Métricas derivadas (fórmulas recomendadas para esta KB)

| Métrica | Fórmula (esta KB) | Variantes en el sector | Qué mide |
|---|---|---|---|
| **Hook rate / thumbstop** | 3-second video plays / impressions | Algunos usan plays/impressions o 2 s | Capacidad de parar el scroll en los primeros segundos |
| **Hold rate** | ThruPlays / 3-second video plays | 15-s views / 3-s plays; plays at 50% / 3-s plays; avg watch time / duración | Retención tras el hook. **Ojo:** en vídeos ≤15 s está inflado por definición |
| **Retención por cuartiles** | plays at 25/50/75/95% / 3-second plays | — | Dónde se cae la gente |
| **Outbound CTR** | outbound clicks / impressions | Link CTR | Capacidad de generar visitas |
| **Click-to-LPV rate** | landing page views / outbound clicks | — | Calidad del clic + velocidad de la landing; <70–80% suele indicar web lenta o clics accidentales (**[HYPOTHESIS]** como umbral) |
| **CVR post-clic** | conversiones / LPV (o / outbound clicks) | conversiones / link clicks | Encaje anuncio–landing–oferta (message match) |
| **Cost per LPV** | gasto / LPV | — | Coste de tráfico real |
| **ATC rate / IC rate** | add to cart (o initiate checkout) / LPV | — | Intención post-clic |
| **CPA** | gasto / conversiones | — | Eficiencia |
| **AOV por creativo** | valor / compras | — | Algunos ángulos traen tickets mayores (S03-042) |
| **Share of spend** | gasto del anuncio / gasto del ad set | — | Lo que Meta "cree" del anuncio |
| **Descomposición del CPA** | CPA = CPM / (1.000 × CTR × CVR) | — | Ver qué factor explica la diferencia entre dos creativos |

**Descomposición útil:** CPA = CPM ÷ (1.000 × outbound CTR × CVR por clic). Si el creativo A tiene mejor CPA que B, esta identidad dice si es porque llega más barato (CPM), porque atrae más clics (CTR) o porque trae clics que convierten (CVR). Las tres son palancas distintas: audiencia/placement, hook/promesa y message match/cualificación. **[STRONG INFERENCE]** (identidad aritmética)

## 3. ¿Qué métricas predicen negocio y cuáles engañan?

| Métrica | Predice | Engaña cuando… | Uso correcto |
|---|---|---|---|
| Hook rate | Que el anuncio para a gente | Hooks de curiosidad o polémica paran a quien no compra; varía mucho por placement (Reels > Feed); no se correlacionó con ROAS en S03-042 | Diagnóstico de los primeros segundos; comparar hooks **del mismo concepto** con CVR estable |
| Hold rate / retención | Que el body interesa | Vídeos cortos inflados por la definición de ThruPlay; retención alta en contenido entretenido que no vende | Diagnóstico de guion |
| CTR (all) | Poco | Incluye clics no-link | No usar |
| Outbound CTR | Interés en saber más | Clickbait; estáticos con CTR bajo y CPA igual (S03-035); temprano no predice longevidad (S03-039) | Diagnóstico de promesa/hook; nunca solo |
| CPC | Coste del tráfico | CPC bajo con tráfico malo | Con CVR |
| CPM | Coste de llegar | No es "calidad" del anuncio: depende de la audiencia que el creativo atrae (algunos ángulos llegan a audiencias caras, The Performers S03-024) | Contexto; comparar dentro del mismo ad set |
| LPV rate | Calidad del clic y de la web | — | Higiene técnica |
| CVR post-clic | **Sí** (la señal más consistente en S03-042) | Volumen bajo; retargeting infla | Métrica clave de calidad del tráfico que trae el creativo |
| AOV | **Sí** para ROAS | — | Diferenciar ángulos que traen tickets altos |
| CPA/ROAS de plataforma | Sí, con sesgos | Atribución (view-through, engage-through), retargeting, poco volumen | Decisión, con validación externa (área 04) |
| Gasto asignado | Predicción de escalabilidad del sistema | Incumbencia y trayectoria; "winner" por gasto puede perder dinero | Combinado con CPA |
| Ad relevance diagnostics | Señal relativa | Comparan con anuncios de otros; no entran en la subasta | Secundario |
| Calidad en CRM (lead cualificado, cierre, LTV) | **Sí**, la mejor para lead gen/high-ticket | Retraso temporal | Imprescindible en lead gen (área 05) |

**Principio:** cuanto más cerca del dinero, más predictiva y más ruidosa (menos eventos). Cuanto más arriba en el embudo, más volumen y menos predictiva. La analítica creativa profesional **combina** ambas: decide con las de abajo cuando hay volumen y usa las de arriba para diagnosticar y para tests de componentes (05). **[STRONG INFERENCE]**

## 4. Árbol de diagnóstico de un creativo

```
¿Tiene gasto suficiente para juzgar? (≥2–3x CPA objetivo o ≥20 conversiones)
 ├─ No → mirar señales tempranas (hook rate, outbound CTR, LPV rate) solo para descartar desastres
 └─ Sí → ¿CPA ≤ objetivo?
      ├─ Sí → escalar/iterar; vigilar la curva de fatiga (06)
      └─ No → descomponer CPA = CPM / (CTR × CVR)
           ├─ CPM alto vs ad set → ¿el ángulo atrae una audiencia cara? ¿placement? (aceptable si CVR/AOV compensan)
           ├─ CTR bajo:
           │    ├─ hook rate bajo → problema de apertura (iteración de hook)
           │    ├─ hook OK, hold bajo → problema de body/guion
           │    └─ hook y hold OK, CTR bajo → promesa/oferta/CTA débil o contenido "entretenido" sin intención
           └─ CVR baja (CTR OK):
                ├─ LPV/outbound bajo → velocidad web, clics accidentales
                ├─ ATC bajo → message match, landing, precio/oferta (09)
                └─ ATC OK, compra baja → checkout, envío, confianza, pagos (09)
```

Referencia de practicantes coherente con este árbol: CTR bajo sugiere ángulo equivocado; hook rate bajo, primeros 3 s; hold bajo, storytelling; LPV rate bajo, curiosidad débil o web; CPC alto, anuncio poco competitivo (The Performers, S03-024). **[EMPIRICAL]**

## 5. Benchmarks: cómo usarlos (y por qué casi nunca)

- Los benchmarks de terceros de hook rate (p. ej., Feed ~18–28%, Reels ~24–36%) **no tienen metodología homogénea** y varían con la fórmula, el placement, el vertical y la temperatura de la audiencia (S03-044). **[EMPIRICAL]**
- **Usa la mediana de tu propia cuenta** (por placement y tipo de audiencia) como referencia. Un anuncio es "bueno en hook" si está, por ejemplo, en el cuartil superior de tu cuenta con CVR igual o mejor.
- Separa siempre **frío vs caliente** (retargeting infla CVR y ROAS) y **por placement**.

## 6. Reporting creativo recomendado

**Nivel anuncio (semanal):** gasto, % del gasto del ad set, impresiones, CPM, hook rate, hold rate, outbound CTR, LPV rate, CVR post-clic, CPA, ROAS, AOV, frecuencia 7d, días activo, impresiones acumuladas, etiquetas de taxonomía (ángulo, concepto, formato, hook ID, tipo NC/IT…).

**Nivel agregado (mensual):** por **ángulo**, por **formato**, por **hook ID**, por **persona** y por **cohorte de lanzamiento**: gasto, CPA, hit rate (winners / lanzados), % del gasto en anuncios <30 días.

**Herramientas:** Motion, Atria, Foreplay y similares automatizan el tagging y los informes por atributos (ver 10). El naming estructurado (02) permite hacerlo con hojas de cálculo.

## Implicaciones operativas

- Fijar fórmulas internas (sección 2) y no cambiarlas.
- Decidir sobre creativos con **CPA/ROAS + volumen**; diagnosticar con atención y post-clic.
- Para lead gen, evaluar creativos con **calidad en CRM** y no con el CPL (área 05).
- Revisar si las comparaciones cruzan el cambio de atribución de mar-2026.
- Usar breakdowns (edad, género, placement, plataforma, región) por anuncio para saber a quién encuentra (01).

## Errores frecuentes

- Optimizar el hook rate como objetivo (paran los que no compran).
- Comparar el "hold rate" de un vídeo de 10 s con el de uno de 45 s.
- Usar CTR (all).
- Matar estáticos por CTR bajo (CPA comparable al vídeo).
- Mezclar prospección y retargeting en el mismo benchmark.
- Leer ROAS de plataforma como incrementalidad (área 04).

## Preguntas abiertas

- Hay pocas correlaciones publicadas entre métricas creativas y resultados (solo n=11 marcas en S03-042). Conviene replicarlo en las cuentas propias.
- Estado en 2026 de los ad relevance diagnostics y de las definiciones exactas de ThruPlay (6 s vs 15 s, 97%): verificar en Ads Manager.

## Fuentes clave

- [Sweat Pants Agency — What actually predicts ROAS](https://sweatpantsagency.com/blog/what-is-a-good-roas-on-meta-ads) — 2026-07 — agencia (dataset)
- [Interconnections — Creative fatigue benchmark](https://www.theinterconnections.com/benchmarks/meta-creative-fatigue) — 2026-08 — agencia (dataset)
- [Biddyco — Video length](https://www.biddyco.com/blog-posts/meta-video-ad-length) — 2026-10-05 — agencia (dataset)
- [Jon Loomer — The difference between Facebook clicks](https://www.jonloomer.com/facebook-clicks/) — practitioner
- [Jon Loomer Pubcast — Click attribution isn't what it used to be](https://pubcast.jonloomer.com/click-attribution-isnt-what-it-used-to-be/) — 2026-03-16 — practitioner
- [Jetfuel — Creative performance metrics 2026](https://jetfuel.agency/creative-performance-metrics-for-dtc-video-ads-hold-rate-thumbstop-and-thruplay-benchmarks-2026/) — 2026-08-20 — agencia
- [Dema — New Meta metrics and dimensions](https://www.dema.ai/changelog/new-meta-metrics-and-dimensions) — 2025-06-02 — vendor
- [Motion — Creative Benchmarks 2026 (methodology)](https://motionapp.com/library/research/creative-benchmarks-2026/methodology) — 2026 — vendor
- [Marketing Dive — Facebook replaces relevance score](https://www.marketingdive.com/news/facebook-replaces-relevance-score-changes-ad-metrics/550331/) — 2019 — prensa
