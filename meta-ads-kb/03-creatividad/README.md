# Área 03: Creatividad, estrategia creativa, testing, fatiga, analítica creativa, copy, oferta y competencia

> Última verificación: 2026-10-16 · Autor: A03 (agente) · Ledger: `../fuentes/ledger-03-creatividad.md` (115 fuentes)

## Índice

| # | Archivo | Pregunta que responde |
|---|---|---|
| 01 | [01-creative-es-targeting.md](01-creative-es-targeting.md) | ¿Hasta qué punto "el creativo es el targeting"? Mecanismo (Andromeda, GEM, Generative Recommender), similitud creativa, columna Creative diversity, límites |
| 02 | [02-taxonomia-angulo-concepto-hook-ejecucion.md](02-taxonomia-angulo-concepto-hook-ejecucion.md) | Definiciones operativas (oferta, ángulo, concepto, ejecución, hook, body…), nuevo creativo frente a iteración, escalera de iteración, naming |
| 03 | [03-estrategia-creativa-primeros-principios.md](03-estrategia-creativa-primeros-principios.md) | Deseo, dolor, identidad, mecanismo, prueba, objeciones; Schwartz (awareness y sofisticación) traducido a Meta 2026; matriz de ángulos |
| 04 | [04-formatos-y-estilos.md](04-formatos-y-estilos.md) | Catálogo de formatos, estático frente a vídeo, duración, 9:16 y sonido, lo-fi frente a producido, contenido de creadores |
| 05 | [05-testing-creativo.md](05-testing-creativo.md) | Estructuras de test, herramienta Creative Testing nativa, estadística de falsos negativos, reglas de kill/winner, volumen, nº de anuncios |
| 06 | [06-fatiga-creativa.md](06-fatiga-creativa.md) | Fatiga real frente a varianza y saturación, estados oficiales, curvas de fatiga, diagnóstico y remedios |
| 07 | [07-analitica-creativa-metricas.md](07-analitica-creativa-metricas.md) | Definiciones y fórmulas, qué métricas predicen negocio, árbol de diagnóstico, reporting |
| 08 | [08-copy-de-anuncios.md](08-copy-de-anuncios.md) | Primary text, headline, CTA, placements, variaciones e IA de texto (incl. rewriting en imágenes, jul-2026) |
| 09 | [09-oferta-y-diagnostico-ad-oferta-landing-ventas.md](09-oferta-y-diagnostico-ad-oferta-landing-ventas.md) | ¿Mal anuncio, mala oferta, mala landing o mal equipo de ventas? Message match y diseño de oferta |
| 10 | [10-investigacion-competencia-ad-library.md](10-investigacion-competencia-ad-library.md) | Ad Library (web y API), UE/UK frente al resto, señales y sus límites, herramientas |
| 11 | [11-sistema-investigacion-creativa-50-100-anuncios.md](11-sistema-investigacion-creativa-50-100-anuncios.md) | Procedimiento y ficha para analizar 50–100 anuncios y convertirlos en briefs |
| 12 | [12-comentarios-y-prueba-social.md](12-comentarios-y-prueba-social.md) | Comentarios como prueba social y señal; ocultar frente a borrar; moderación; post IDs |
| 13 | [13-produccion-y-feedback-loop-creativo.md](13-produccion-y-feedback-loop-creativo.md) | Ciclo semanal, roles, volumen y presupuesto de producción, learning log |
| 14 | [14-herramientas-ia-creativa-meta.md](14-herramientas-ia-creativa-meta.md) | Inventario de la IA creativa de Meta, cronología 2024-2026, evidencia, qué activar o desactivar, términos legales |
| 15 | [15-landing-pages-y-cro-trafico-meta.md](15-landing-pages-y-cro-trafico-meta.md) | Navegador in-app, velocidad y calidad de landing (bounce/dwell como señal de Meta), message match, formularios/VSL, checkout, destinos personalizados de Meta, diagnóstico post-clic, CRO con poco tráfico, checklists |
| 16 | [16-ia-generativa-en-anuncios-que-funciona.md](16-ia-generativa-en-anuncios-que-funciona.md) | ¿Qué formato hago en B2B y SaaS (ranking de 10 opciones, de fundador a cámara a avatar)? ¿Qué dice la evidencia sobre IA frente a humano? ¿Qué estáticos funcionan? ¿Cuándo hay que etiquetar la IA (art. 50) y cómo? |

## TL;DR del área (lo que el agente principal debe "pensar por defecto")

1. **El anuncio es la segmentación.** Meta usa el contenido del creativo como input de retrieval y ranking (GEM: "creative representation"; Generative Recommender desde el Q2 2026: LLMs que "reason about ad content and user preferences together"). Con targeting amplio, **a quién habla el anuncio decide a quién se entrega**. **[OFFICIAL META]**
2. **Diversificar por concepto, no por cosmética.** Meta dice que los creativos demasiado parecidos pueden tratarse como uno solo y mostrarse a las mismas personas. Existe una columna "Creative diversity" (Low/Medium/High, desde el 26-ago-2026, "en desarrollo"). El "Entity ID" es una metáfora de practicantes, no un término oficial. **[OFFICIAL META]** / **[HYPOTHESIS]** para el mecanismo exacto.
3. **El creativo segmenta hacia el evento de optimización, no hacia el negocio.** Con optimización a eventos baratos, creativos de curiosidad o "gratis" traen volumen de baja calidad. Hay que alinear el evento con el negocio y usar el creativo para cualificar. **[STRONG INFERENCE]**
4. **Los winners son raros y concentran el gasto.** Motion 2026 (578k creatividades, $1,29B): ~5% de winners que se llevan el 55% del gasto; ~la mitad de los anuncios apenas gasta. El volumen *diverso* es la palanca, limitado por el presupuesto de test. **[EMPIRICAL]**
5. **La estadística manda en el testing.** Matar a 1x CPA sin conversiones descarta ~37% de anuncios válidos; con 10 conversiones, dos anuncios idénticos difieren ≥30% en CPA ~58% de las veces. Solo se detectan diferencias grandes, así que los tests deben buscar saltos grandes (ángulos, conceptos, ofertas) y las métricas intermedias sirven para retoques. **[STRONG INFERENCE]**
6. **Herramienta nativa Creative Testing (2025):** 2–5 variantes, ≤20% del presupuesto, 7 días por defecto, sin solapamiento, solo Highest Volume, no testea anuncios existentes. Es buena para comparar variantes dentro del ad set real. **[OFFICIAL META]**
7. **Estáticos y vídeo, no uno u otro.** Los estáticos de texto o de producto con texto lideran el hit rate en Motion. En Biddyco (17 cuentas), los estáticos tienen CPM −15%, CTR −13% y CPA prácticamente igual. Para Reels: 9:16, audio (>75–80% con sonido) y safe zone. **[EMPIRICAL]/[OFFICIAL META]**
8. **La duración no predice el rendimiento; la apertura sí.** Espectador mediano ~4 s en cualquier duración; coste por resultado ±6% entre tramos. Meta (Creative Shop): la reacción a un anuncio móvil se forma en ~0,4 s. **[EMPIRICAL]**
9. **La fatiga es gradual y menos frecuente que el fracaso.** El 80% de creatividades nunca llega a 100k impresiones; en los ganadores el CPA sube ~9–20% con cientos de miles de impresiones y el CPM no sube con la edad. Las reglas de "frecuencia 2,5–3" no tienen origen verificable. **[EMPIRICAL]**
10. **Las métricas de atención diagnostican, no predicen.** Hook rate, hold y CTR no se correlacionaron con ROAS en un estudio de 11 marcas; la CVR post-clic y el AOV sí. El CTR temprano no predice la longevidad. **[EMPIRICAL]** (muestras pequeñas)
11. **Diagnóstico por etapas**: tracking → CPM → atención → clic → LPV → ATC/IC → conversión → calidad/negocio. La primera etapa rota es el cuello de botella; no se producen más creativos si la fuga está en la landing, la oferta o ventas. **[STRONG INFERENCE]**
12. **La IA de Meta multiplica ejecuciones, no ángulos, y parte viene activada por defecto** (p. ej., el rewriting de texto dentro de imágenes desde el 27-jul-2026). En tests, desactivar lo que cambia el mensaje; configurar Branding y *restricted words*. El anunciante es legalmente responsable del output (términos GenAI, incorporados a los Self-Serve Ad Terms el 30-oct-2026). **[OFFICIAL META]/[EMPIRICAL]**
13. **La competencia informa, no dicta.** Ad Library: sin datos de rendimiento fuera de la UE/UK; en la UE, alcance y targeting oficiales (el mejor proxy público de escala). La longevidad es señal, no prueba. Motion sitúa "lo hace la competencia" al final de su escala de confianza. **[OFFICIAL META]/[EMPIRICAL]**
14. **La landing es parte del anuncio y de la subasta.** El tráfico de Meta aterriza por defecto en el navegador in-app (sin cookies ni sesiones del navegador del sistema, con autofill de Meta y Meta AI). Meta usa el *landing page bounce rate* y el *dwell time* como señales de calidad del anuncio, y sus "personalized destinations" (optimize website destination, product browsing, browser add-ons) pueden cambiar a dónde va el clic. Hay que probar la página dentro de IG/FB y fijar los destinos en los tests (15). **[OFFICIAL META]**

## Reglas de decisión rápidas (heurísticas de trabajo)

- **Nuevo creativo de verdad** = cambia ángulo, persona, mecanismo o formato/visual de forma reconocible en la miniatura y los primeros 3 s. Si no, es iteración (02).
- **Kill por cero conversiones**: no antes de 2–3x el CPA objetivo (05).
- **Winner provisional**: ≥10–20 conversiones con CPA ≤ objetivo y gasto asignado. **Confirmado**: ≥30–50 conversiones, ≥7 días, y que aguante al escalar (05).
- **Refresh**: por el CPA del anuncio frente al objetivo con tendencia y cohortes, no por días ni por frecuencia sola (06).
- **Capacidad de test semanal** ≈ presupuesto semanal de test ÷ (2–3 × CPA objetivo) conceptos (05, 13).
- **Antes de cambiar la oferta**: ≥3–5 ángulos distintos testeados y message match verificado (09).

## Cambios 2025-2026 detectados (área creativa)

| Fecha | Cambio | Archivo |
|---|---|---|
| 2025 (API v22.0) | "Standard enhancements" deprecado como paquete | 14 |
| 2025-04-22 | Meta: guía "Creative Advantage… diversification with Andromeda" | 01 |
| 2025 (mediados) | Desaparece la recomendación de "máx. 6 anuncios por ad set" | 01, 05 |
| 2025-06-17 | Cannes Lions: video generation (beta), branding a escala, virtual try-on (test), sticker CTAs | 14 |
| 2025-07 | Creative breakdown por asset (flexible format) | 04, 14 |
| 2025-07-30 | Q2 2025: Andromeda +~4% conversiones en FB Feed/Reels; ~2M anunciantes con vídeo generativo | 01, 14 |
| 2025-07 | *Optimize website destination* (Meta elige la URL de destino); LPV optimization para anunciantes con problemas de pixel (LPV medibles vía in-app browser) | 15 |
| ~2025 (oct, aprox.) | Herramienta nativa Creative Testing a nivel de anuncio | 05 |
| Q4 2025 | Métricas de Creative fatigue / Creative similarity en reporting (según practicantes) | 01, 06 |
| 2025-11-10 | Meta Engineering publica GEM (creative representation como input) | 01 |
| 2026-03-03/16 | Atribución: click-through solo clics en enlace; engage-through (1 día) para interacciones y vistas ≥5 s | 07 |
| 2026-03-26 | NewFronts: voiceover/traducción, UGC con avatares (test), vídeo de catálogo (test) | 14 |
| 2026-03 | Los anuncios de media única y colecciones de catálogo en Feed de FB dejan de mostrar la URL en el pie | 15 |
| 2026-04-29 | Q1 2026: >8M anunciantes con GenAI creativa; video generation >3% CVR en tests | 14 |
| 2026-07-27 | Rewriting de texto en imágenes por defecto (hasta 8 variantes) | 08, 14 |
| 2026-07-29 | Q2 2026: Meta Generative Recommender (LLMs sobre contenido del anuncio + preferencias); >9M pymes con IA creativa | 01, 14 |
| 2026-08-26 | Columna "Creative diversity" (Low/Medium/High) | 01, 06 |
| 2026-09 | Límite de anuncios por Página no bloquea en algunas cuentas (sin anuncio oficial) | 05 |
| 2026-09-15 | Creator Marketing Hub (une Creator Marketplace + Partnership Ads Hub) | 04 |
| 2026-09-21 | Test observado de landing generada por IA que puede sustituir a la web (<5% impresiones) | 15 |
| 2026-10-06 | Advertising Week: vídeo desde estáticos GA; Ads Creative Studio ampliándose | 14 |
| ~2026-10-28 | *Product browsing* ON por defecto en anuncios existentes salvo opt-out (aviso del 14-oct; sin doc pública) | 15 |
| 2026-10-30 | Términos GenAI incorporados a los Self-Serve Ad Terms (responsabilidad del anunciante) | 14 |

## Contradicciones y puntos para contrastar con otras áreas

- **Límite de anuncios por ad set**: 50 (Marketing API) frente a 150 (CTC, jul-2026) o 250 (blogs). Sin verificar → áreas 02/10.
- **¿Añadir anuncios reinicia el aprendizaje?** La documentación dice que sí; Jon Loomer observó que no (oct-2025) → áreas 01/02.
- **Testear en BAU o en campaña separada**: [CONTESTED] entre practicantes serios → área 02.
- **Umbrales de "similarity score" (40%/60%)** sin fuente oficial → área 12 (mitos).
- **"Entity ID"** como mecanismo literal → área 12 (mitos) y área 01 (subasta).
- **Cifras de impacto de Andromeda** (−7% ROAS, CPM +28%) de fuentes no verificables → áreas 09/11.
- **Efecto de las mejoras de Advantage+ creative**: Meta reporta lifts; agencias reportan pérdidas → área 10.
- **Definición de ThruPlay** (15 s frente a 6 s, 97%): verificar en Ads Manager → área 04.
- **Términos del 30-oct-2026** ("tests sin aviso" que afectan a creativos): leer el texto legal completo → áreas 08/10. · **2026-11-09**: suspendidas antes de entrar en vigor; siguen las del 22-ago-2025 (S10-113)

## Huecos y preguntas abiertas del área

- El Help Center de Meta devuelve login a las herramientas normales. El 2026-10-16 se leyó con el user-agent `facebookexternalhit/1.1`, lo que permitió verificar directamente creative fatigue, comentarios, LPV, in-app browser, calidad del anuncio y destinos (archivos 06, 12 y 15). Siguen sin verificar directamente ThruPlay y la herramienta Creative Testing.
- Reddit no fue accesible desde la herramienta, así que falta la voz de comunidad de primera mano (se usaron citas recogidas por Motion).
- Faltan datos independientes y rigurosos sobre: founder ads, podcast clips, screen recordings; efecto de los comentarios en CVR/entrega; lift por enhancement de IA; relación frecuencia-respuesta en 2026; peso del copy frente al visual.
- Los datasets clave (Motion, Biddyco, Interconnections, Sweat Pants) son de vendors o agencias, con periodos cortos (a veces con BFCM) y métricas de gasto en vez de beneficio.
- ¿Qué peso tienen imagen, texto en imagen, audio y copy en la "representación del creativo" que usan los modelos de Meta? No hay información pública.
