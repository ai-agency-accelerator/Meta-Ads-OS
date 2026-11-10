# Oferta y diagnóstico: ¿mal anuncio, mala oferta, mala landing o mal equipo de ventas?

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: cómo interactúan mercado, oferta, creativo, funnel y ventas; patrones de métricas que distinguen cada cuello de botella; congruencia anuncio–landing (message match); diseño de oferta. El tracking lo cubre el área 04; lead gen y CRM, el área 05; e-commerce, el área 06.

## TL;DR

- **Primero se descarta el tracking.** Si los datos de Meta no cuadran con la fuente de verdad (Shopify/CRM/back-office), cualquier diagnóstico creativo es ficción. **[STRONG INFERENCE]** (área 04)
- **El diagnóstico se hace por etapas y en orden:** entrega (CPM/alcance) → atención (hook/hold) → clic (outbound CTR) → llegada (LPV/clic) → intención (ATC/IC o inicio de formulario) → conversión (compra/lead) → calidad (cualificación, cierre, LTV). **La primera etapa que falla frente a su referencia es el cuello de botella.** Cambiar varias cosas a la vez impide saber cuál era. **[EMPIRICAL]** (consenso de practicantes, p. ej. Jon Loomer)
- **Mal anuncio:** CPM normal, pero hook o outbound CTR bajos frente a la cuenta. Los que hacen clic convierten de forma normal. **Mala oferta:** atención y CTR normales o altos, la landing carga bien, pero ATC/IC o CVR bajos en **todos** los creativos y ángulos, y las objeciones de precio o valor dominan comentarios y chats. **Mala landing:** caída fuerte clic → LPV (web lenta), o LPV → ATC bajo con señales de UX (rebote, scroll), y mejora en cuanto se cambia la página sin tocar la oferta. **Mal equipo de ventas (lead gen):** CPL y volumen correctos y leads con datos válidos, pero bajas tasas de contacto, cita o cierre, sobre todo por tiempo de respuesta, y con diferencias grandes entre comerciales. **[STRONG INFERENCE]** (sección 2)
- **Velocidad de respuesta en lead gen:** en el análisis de ~1,25M leads asociado al artículo de HBR (2011), las empresas que intentaban contactar en la primera hora tenían casi **7 veces** más probabilidad de tener una conversación con un decisor que si esperaban una hora más, y **>60 veces** frente a 24 h o más. En la auditoría a 2.241 empresas, el 23% nunca respondió. Es un dato antiguo pero robusto como principio. **[EMPIRICAL]** (S03-054)
- **El message match multiplica:** la promesa, la oferta, la persona y el estilo visual del anuncio deben reaparecer arriba en la landing. Un anuncio de awareness baja que lleva a una página de descuento "carries a question your landing page never answers". **[STRONG INFERENCE]** (S03-032)
- **La oferta es la palanca de mayor magnitud y riesgo.** Ningún hook arregla una oferta que no compite. Antes de cambiarla hay que haber probado al menos 3–5 ángulos distintos con ejecuciones decentes. **[STRONG INFERENCE]**
- **Benchmarks externos solo como orientación:** Unbounce 2024 da una mediana de conversión de landing del 6,6% (todas las industrias; 41.000 páginas), con medianas por industria entre 3,8% y 12,3% y e-commerce en 4,2%. Lo útil es comparar con el histórico propio. **[EMPIRICAL]** (S03-055)

## 1. El sistema: mercado → oferta → creativo → funnel → ventas → negocio

| Capa | Pregunta | Si falla… |
|---|---|---|
| Mercado | ¿Existe demanda suficiente y alcanzable en Meta? | Nada escala; CPMs y CPAs altos en todos los ángulos; volumen de búsqueda/interés bajo |
| Oferta | ¿Es mejor (valor/riesgo/precio) que las alternativas, incluida "no hacer nada"? | Atención y clic sí, compra no; objeciones de precio y valor |
| Creativo | ¿Llega a la persona adecuada con el mensaje adecuado? | Clics baratos que no convierten (creativo que atrae a la persona equivocada) o poca atención |
| Funnel (landing, checkout, formulario) | ¿Confirma la promesa y reduce la fricción? | Fugas entre clic y conversión |
| Ventas / operación (lead gen, high-ticket) | ¿Se contacta, cualifica y cierra bien? | Leads "malos" que en realidad están mal atendidos |
| Negocio | ¿Margen, LTV y capacidad lo soportan? | Escalar pierde dinero aunque el CPA "esté bien" |

Las capas interactúan: un creativo muy agresivo puede "arreglar" el CTR y romper la calidad del lead; una oferta de lead gratis sube el volumen y hunde el cierre.

## 2. Matriz de diagnóstico (patrones de métricas)

| Síntoma principal | Patrón que lo confirma | Culpable probable | Primera acción |
|---|---|---|---|
| Hook rate y outbound CTR bajos frente a la cuenta en **algunos** creativos | CVR de los que hacen clic normal | **Creativo** (apertura/promesa) | Iterar hook/ángulo (02, 05) |
| CTR bajo en **todos** los creativos, también en ángulos distintos | CPM normal | **Oferta o mercado** (la promesa no interesa) o creativos todos parecidos | Revisar diversidad (01); probar oferta/ángulo radicalmente distinto |
| CTR alto, CVR muy baja | Comentarios "¿precio?", rebote alto | **Desalineación** anuncio–landing (clickbait, promesa que la página no confirma) o **oferta** | Message match; si persiste con match correcto → oferta |
| Clics → LPV < ~70–80% | Tiempo de carga alto, móvil | **Landing técnica** (velocidad, redirecciones, pixel) | Velocidad/tracking (umbral **[HYPOTHESIS]**) |
| LPV normal, ATC/IC bajo en todos los creativos | Mapas de calor, scroll bajo, objeciones | **Landing (contenido/UX) u oferta** | Test de landing con la misma oferta; si no mejora → oferta |
| ATC normal, compra baja | Abandono en envío/pago | **Checkout / costes ocultos / confianza** | Revisar envío, métodos de pago, sorpresas de precio |
| Todo empeora a la vez en todos los anuncios | CPM o CVR web cae en toda la cuenta | **Externo**: tracking, web, stock, estacionalidad, competidor | Área 04/09; no tocar creativos |
| Lead gen: CPL bueno, cualificación baja | Ciertos creativos u ofertas traen peores leads | **Creativo/oferta atraen a la persona equivocada** (lead magnet gratis, formulario sin fricción) | Añadir fricción y cualificación al copy y al formulario (área 05) |
| Lead gen: leads válidos, contacto/cita bajos | Tiempo de respuesta alto, variación entre comerciales | **Ventas / operación** | SLA de respuesta <5–60 min, scripts, seguimiento (S03-054) |
| Lead gen: citas sí, cierre bajo | Objeciones repetidas en llamadas | **Oferta/precio o ventas** | Analizar grabaciones; reforzar la prueba y la oferta; formación |
| Funciona pequeño, se rompe al escalar | CPA sube con el gasto en todos los ángulos | **Tamaño del bolsillo/mercado** o similitud creativa | Nuevos ángulos y personas (01, 06); revisar economía (área 09) |

### 2.1 Pruebas de aislamiento

- **Test de oferta con el mismo creativo**: mismo anuncio, dos landings con ofertas distintas (A/B a nivel de landing o campaña). Si el CVR cambia mucho, el cuello de botella era la oferta.
- **Test de landing con la misma oferta**: aísla UX/contenido.
- **Test de creativo con la misma landing**: aísla el anuncio (05).
- **Auditoría "mystery shopper"** en lead gen: enviar leads de prueba y medir tiempo y calidad de respuesta (así se hizo la auditoría de HBR).
- **Cohortes de calidad por creativo**: en CRM, calidad de lead y cierre por anuncio/ángulo (área 05).

## 3. Message match (congruencia anuncio–landing)

**Elementos que deben coincidir** (por orden de importancia):
1. **Promesa principal / ángulo** (si el anuncio habla de dolor cervical, la landing abre con el dolor cervical, no con "la almohada más vendida").
2. **Oferta y precio** (si el anuncio dice "100 noches de prueba", la landing lo muestra arriba).
3. **Persona** (si el anuncio es para oficinistas, la landing lo menciona y muestra el contexto).
4. **Prueba** (la reseña o el experto del anuncio aparecen).
5. **Estilo visual** (continuidad de imágenes, colores, talento).
6. **Nivel de awareness** (anuncio de awareness baja → advertorial/educación; most aware → PDP o checkout) (03, S03-032).

**Operativo:**
- Mapear cada **ángulo** a una landing (o a una variante de cabecera dinámica). Con muchos ángulos, crear 3–5 landings por grandes ángulos o awareness en vez de una sola página para todo.
- Revisar el message match tras activar funciones de IA que reescriben texto (08, 14): pueden romperlo sin avisar (S03-052).
- Meta permite probar varias URLs en algunos formatos. CTC incluye "multiple URL testing" en su estructura de anuncios (S03-022). Su disponibilidad y su funcionamiento los cubre el área 06.

## 4. Diseño de oferta (lo que el creative strategist debe proponer)

**Componentes:** producto/servicio, precio y forma de pago, bonus, garantía/riesgo invertido, urgencia/escasez *legítimas*, prueba/trial, bundle, envío, onboarding.

**Framework útil (criterio, no evidencia empírica):** la "value equation" de Alex Hormozi (*$100M Offers*, 2021): valor percibido ∝ (resultado deseado × probabilidad percibida de lograrlo) / (tiempo hasta el resultado × esfuerzo y sacrificio). Cada término es una palanca creativa y de oferta:
- Resultado deseado → ángulo y promesa.
- Probabilidad percibida → prueba, mecanismo, garantía.
- Tiempo → "en 7 días", onboarding, quick wins.
- Esfuerzo → "sin…", hecho por ti, facilidad.

**Ofertas que suelen cambiar la economía** (más que el descuento): garantía fuerte (riesgo invertido), trial, bundle con mayor AOV, bonus de alto valor percibido y bajo coste, financiación, envío o devolución gratis, oferta de entrada (tripwire) para captar y monetizar después. **[STRONG INFERENCE]**

**Datos de contexto:** en el dataset de Motion (con BFCM), los hooks promocionales (sale, price anchor, urgency, offer only) y el formato offer-first banner lideran el hit rate, lo que confirma que una oferta clara mueve mucho en temporada (S03-010). En Biddyco (sep-2026), el peso de la oferta en el gasto top va de ≤5% en unas cuentas a >50% en otras (5 de 7 de apps y servicios por encima) (S03-037). **[EMPIRICAL]**

## 5. Señales cualitativas que acompañan a cada problema

| Fuente | Señal de oferta | Señal de creativo | Señal de landing | Señal de ventas |
|---|---|---|---|---|
| Comentarios del anuncio | "Muy caro", "¿cuánto cuesta?", "en Amazon está más barato" | "No entiendo qué es", "¿esto para qué sirve?" | "El link no funciona", "no encuentro X" | "Nadie me contestó" |
| Chat/soporte | Objeciones de valor y garantía | Expectativas equivocadas | Dudas que la página debería resolver | Quejas de seguimiento |
| Llamadas de venta | Precio, comparativas | Leads que no sabían qué pedían | — | Variación grande entre comerciales |
| Encuesta post-compra / no compra | "Casi no compro por el precio" | "Os vi en un anuncio de…" | "Me costó encontrar…" | — |

## Implicaciones operativas

- **Checklist de diagnóstico semanal** (en este orden): tracking ↔ fuente de verdad → CPM de la cuenta → hook/CTR por ángulo → clic→LPV → LPV→ATC/IC (o inicio de formulario) → CVR → (lead gen) contacto, cita, cierre por creativo → margen.
- **No producir más creativos** si el cuello de botella está aguas abajo (landing, oferta, ventas). Primero se arregla la fuga.
- **Antes de cambiar la oferta**: ≥3–5 ángulos distintos testeados con volumen razonable y el message match verificado.
- **Lead gen**: SLA de primer contacto (ideal <5–15 min, máx. 1 h en horario), registro del tiempo de respuesta en el CRM e informe de calidad por anuncio (área 05).

## Errores frecuentes

- Producir 30 hooks nuevos cuando el problema es la landing o el precio.
- Cambiar oferta, landing y creativo a la vez.
- Culpar al "algoritmo" o al creativo de leads que nadie llamó en 24 h.
- Una sola landing genérica para ángulos y niveles de awareness muy distintos.
- Ofertas "gratis" en lead gen high-ticket sin fricción ni cualificación.
- Profundizar el descuento como única palanca de oferta.

## Preguntas abiertas

- No hay datos públicos recientes que cuantifiquen el efecto del message match en Meta. Se mide con tests propios de landing.
- Velocidad de respuesta: los datos de referencia son de 2011. Faltan estudios recientes comparables (área 05).

## Fuentes clave

- [Jon Loomer — What to check when Meta ads aren't converting](https://www.jonloomer.com/meta-ads-arent-converting/) — practitioner
- [HBR — The Short Life of Online Sales Leads (registro BYU)](https://scholarsarchive.byu.edu/facpub/9711) — 2011 — academico/prensa
- [Unbounce — Conversion Benchmark Report (ecommerce)](https://unbounce.com/conversion-benchmark-report/ecommerce-conversion-rate/) — 2024 — vendor (dataset)
- [AdLibrary — Awareness stages in Facebook ads](https://adlibrary.com/posts/awareness-stages-facebook-ads) — 2026-08-08 — vendor
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor (dataset)
- [Biddyco — Best-performing Meta ads 2026](https://www.biddyco.com/blog-posts/best-performing-meta-ads) — 2026-09-27 — agencia (dataset)
- Alex Hormozi, *$100M Offers* (2021) — libro — framework de oferta
