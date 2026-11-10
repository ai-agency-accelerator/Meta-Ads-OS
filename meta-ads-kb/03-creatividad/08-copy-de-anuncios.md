# Copy de anuncios en Meta (2026): primary text, headline, description, CTA, variaciones y peso real del texto

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: texto fuera del creativo (primary text, headline, description, botón CTA) y texto dentro del creativo (overlays, hooks de texto); variaciones de texto y funciones de IA de texto de Advantage+; diferencias por placement.

## TL;DR

- **En 2026 el "copy" más importante vive dentro del creativo** (texto en pantalla, hook de texto, overlays de estático). En Reels y Stories el primary text apenas se ve; en Feed se trunca hacia los ~125 caracteres. Text-only y product-image-with-text lideran el hit rate en Motion, y el text overlay es el hook más común entre los anuncios con más gasto en Biddyco. **[EMPIRICAL]** (S03-010, S03-037)
- **El primary text sigue importando en Feed y para cualificar** (precio, para quién es, prueba, objeciones), sobre todo en lead gen y high-ticket. No hay evidencia robusta de que el largo o el corto ganen de forma universal: los datos observacionales disponibles son contradictorios. **[CONTESTED]**
- **Usar variaciones de texto en el mismo anuncio** (hasta 5 primary texts y 5 headlines; flexible format también admite 5 descripciones). Meta recomienda **texto único por anuncio** y diferencias "significant, not subtle", adaptadas a persona, dolor o ángulo. **[OFFICIAL META]** vía Jon Loomer (S03-005)
- **Las funciones de IA de texto de Meta están activas por defecto en varios casos y pueden cambiar el mensaje.** *Text improvements* ("text_optimizations") mezcla y reutiliza textos; *text generation* crea variantes. Desde el **27-jul-2026**, Advantage+ creative **reescribe el texto dentro de las imágenes subidas** (hasta 8 variantes de titular por imagen manteniendo tipografía y layout) por defecto en campañas elegibles. Se controla en Image Enhancements y con la sección Branding (lista de *restricted words*). **[EMPIRICAL]** (S03-052; ver 14)
- **Meta publica casos positivos de generación de texto** (Unilever vía Tinuiti +18% en volumen de compras con texto e imagen generados; ObjectsHQ +60% de ROAS con Text Generation) **y practicantes reportan casos negativos** (una agencia midió +26% de ROAS al *desactivar* text improvements en una cuenta). Ninguno es un estudio controlado y generalizable. **[CONTESTED]** (S03-003, S03-053)
- **El headline y el botón CTA trabajan como "message match" con la landing**: deben repetir la promesa o la oferta que la landing confirma (09). **[STRONG INFERENCE]**
- **Regla de compliance:** el texto (fuera y dentro del creativo) es lo que más a menudo dispara rechazos por atributos personales ("¿Tienes sobrepeso?"), afirmaciones de salud y finanzas o claims no sustentados. La IA de Meta no ve tus restricciones legales salvo que se configuren. **[OFFICIAL META]** (políticas; detalle en el área 08)

## 1. Componentes y su función

| Componente | Dónde se ve | Función principal | Longitud práctica |
|---|---|---|---|
| **Texto en el creativo** (overlay, hook de texto, subtítulos) | Todos los placements | Parar y seleccionar; transmitir el mensaje sin sonido | 3–10 palabras para el hook; subtítulos completos en vídeo |
| **Primary text** | Feed (encima del medio), parcialmente en Reels/Stories (superpuesto y truncado) | Ampliar: para quién es, prueba, objeciones, oferta, CTA | Lo crítico en las primeras ~125 caracteres (truncado "Ver más"); el resto puede ser largo si cualifica |
| **Headline** | Feed (debajo del medio), algunos formatos | Promesa u oferta en una línea; message match | ~27–40 caracteres visibles según placement (las fuentes discrepan) |
| **Description** | Solo algunos placements | Refuerzo (envío, garantía) | ~25–30 caracteres |
| **Botón CTA** | Todos | Expectativa del siguiente paso ("Comprar", "Más información", "Solicitar presupuesto") | Elegir el que fija bien la expectativa: "Comprar" cualifica más que "Más información" **[HYPOTHESIS]** |
| **Display link / URL parameters** | Algunos placements / tracking | Confianza / medición | — |

Las cifras de caracteres vienen de guías de terceros de 2026 que no coinciden del todo. Hay que comprobarlas en la vista previa de cada placement en Ads Manager. **[EMPIRICAL]**

## 2. Diferencias por placement

| Placement | Qué se lee | Implicación |
|---|---|---|
| Feed FB/IG | Primary text (truncado), creativo, headline, CTA | El copy completo funciona; la primera línea es un "segundo hook" |
| Reels FB/IG | Creativo y texto en pantalla; primary text superpuesto y muy truncado; CTA | El mensaje debe estar en el vídeo (texto + voz); el primary text es casi decorativo |
| Stories | Creativo a pantalla completa; CTA | Igual que Reels; respetar safe zones (texto fuera de los márgenes superior/inferior) |
| Marketplace, búsqueda, columna derecha | Miniatura + titular | Titular y miniatura claros |
| Audience Network / Threads | Variable | Ver área 07 |

## 3. Cómo escribir el primary text (estructura de direct response)

1. **Primera línea = segundo hook**: callout de persona o de dolor, o el resultado. Debe tener sentido por sí sola antes del "Ver más".
2. **Mecanismo o razón para creer** (1–2 frases).
3. **Prueba** (reseña concreta, cifra, autoridad).
4. **Objeción principal y respuesta**.
5. **Oferta + riesgo invertido** (garantía, prueba).
6. **CTA explícito** coherente con el botón y la landing.

Plantillas por nivel de awareness (03):
- **Unaware/problem aware:** historia o situación → nombre del problema → mecanismo del problema → "por eso creamos…".
- **Solution aware:** "Si ya probaste X y Y, esto es distinto porque…" → comparación → prueba.
- **Product aware:** testimonio largo o lista de objeciones respondidas.
- **Most aware:** oferta en la primera línea + plazo + garantía.

## 4. Largo frente a corto

| Postura | Cuándo tiene sentido | Evidencia |
|---|---|---|
| Corto (≤125 caracteres) | Impulso, precio bajo, most aware, Reels/Stories | Datos observacionales de terceros (AdSpyder: cuerpo <50 caracteres sobrerrepresentado en anuncios longevos; segundo pico en 250–500) |
| Largo (300–1.500+ caracteres) | High-ticket, mercados escépticos, lead gen que necesita cualificar, productos con mecanismo | Práctica de direct response; sin estudios públicos controlados en Meta 2025-2026 |
| Variaciones | Por defecto | Meta permite 5 primary texts por anuncio; Loomer recomienda probar corto, medio y largo en el mismo anuncio |

**Veredicto:** **CONTEXT-DEPENDENT**. Probar variantes de longitud dentro del mismo anuncio con multi-texto y decidir por coste por resultado y calidad (en lead gen, calidad en CRM). **[STRONG INFERENCE]**

## 5. Variaciones de texto y funciones de IA de Meta

| Función | Qué hace | Riesgo | Recomendación |
|---|---|---|---|
| **Múltiples textos (hasta 5 primary + 5 headlines; flexible: + 5 descripciones)** | Meta combina y elige por persona/placement | Pérdida de control sobre combinaciones; aprendizaje difuso | Usar con variantes **distintas de verdad** (ángulo, longitud, prueba vs oferta), no sinónimos (S03-005) |
| **Text improvements** (`text_optimizations`) | Muestra tus textos en otros campos (primary ↔ headline ↔ description) y puede usar frases "de alto rendimiento" | Mensajes fuera de contexto; ruido en tests | Desactivar en tests controlados; activar en BAU solo si se revisa (S03-007) |
| **Text generation / AI text variations** | Genera variantes de texto con IA a partir de tus textos | Claims, tono, compliance | Revisar todo; prohibido en sectores regulados sin revisión legal |
| **Rewriting de texto en imágenes**: en el Help Center se llama "Enhance media text (AI)" y reformula el texto superpuesto de imágenes únicas en Feed, Reels y Stories de FB/IG, con previews revisables (S03-090) (desde 27-jul-2026, por defecto en campañas Advantage+ elegibles) | Hasta 8 variantes del titular dentro de la imagen, manteniendo el diseño; sirve más la variante que predice mejor | Puede contradecir promociones, landing o claims legales; los originales pueden dejar de servirse | Configurar Branding (restricted words) y revisar el Creative Report; desactivar en campañas con ofertas o claims sensibles (S03-052) |
| **Translate text** (`text_translation`) / **Translate image text** | Traduce copy o texto de imagen | Calidad y matices | Útil para multi-mercado con revisión nativa |
| **Enhance CTA** (`enhance_cta`) | Combina frases clave con el CTA | Menor | Probar |

Ver 14 para la lista completa de enhancements, su evidencia y qué activar.

## 6. ¿Cuánto importa el copy frente al visual?

- **El visual (incluido el texto en pantalla) decide la atención y, con ello, la entrega** (01, 04). El primary text casi no participa en placements de vídeo vertical, que concentran una parte creciente del inventario. **[STRONG INFERENCE]**
- **El texto de fuera del creativo importa sobre todo para:** (a) Feed; (b) cualificar o descualificar (precio, requisitos, "no es para ti si…"), clave en lead gen; (c) message match; (d) compliance.
- **No hay estudios públicos de Meta 2025-2026 que cuantifiquen el peso del copy frente al visual.** La afirmación "el copy ya no importa" es **UNPROVEN** y, en lead gen y high-ticket, probablemente **FALSE**: el copy es el filtro de calidad más barato. **[STRONG INFERENCE]**

## Implicaciones operativas

- Escribir primero el **hook de texto en pantalla**, luego la **primera línea** del primary text y después el resto.
- Por anuncio: 2–3 primary texts realmente distintos (ángulo/longitud) y 2–3 headlines (promesa, oferta, prueba).
- Antes de lanzar: revisar el estado de **text improvements**, **text generation** y **rewriting de imágenes**; rellenar **Branding → restricted words** con claims prohibidos, términos legales y promociones que no se pueden alterar.
- Revisar cada semana el Creative Report de variantes generadas en campañas Advantage+.
- En lead gen: el copy debe incluir los filtros de cualificación (zona, presupuesto mínimo, requisitos) aunque suba el CPL (área 05).

## Errores frecuentes

- Poner lo importante después de los 125 caracteres.
- 5 primary texts que son sinónimos.
- Dejar la IA reescribiendo ofertas o claims regulados sin revisión.
- Headline genérico ("Compra ahora") que no repite la promesa de la landing.
- Escribir con el vocabulario de la marca en vez del del cliente (03).
- Primary text largo en campañas 100% Reels/Stories pensando que se lee.

## Preguntas abiertas

- Meta no publica datos de rendimiento por enhancement de texto; los casos publicados (positivos de Meta, negativos de agencias) no son generalizables.
- Alcance real del rewriting de texto en imágenes (qué campañas o cuentas, controles exactos): verificar en la cuenta.

## Fuentes clave

- [Jon Loomer — Andromeda and creative diversification (texto único por anuncio, 5+5 variaciones)](https://www.jonloomer.com/meta-andromeda-creative-diversification/) — 2025-10-20 — practitioner
- [Meta for Developers — Advantage+ creative (text_optimizations, text_translation, enhance_cta)](https://developers.facebook.com/docs/marketing-api/creative/advantage-creative/get-started) — vigente — meta-developers
- [Common Thread — Meta is rewriting your ad images by default](https://commonthreadco.com/blogs/coachs-corner/meta-advantage-plus-creative-image-text-rewriting-ecommerce-2026) — 2026-08-18 — agencia
- [Meta for Business — Three steps… (casos de text generation)](https://www.facebook.com/business/news/three-steps-to-optimize-your-performance-with-creative-diversification) — 2024-11-19 — meta-oficial
- [Metalla — Advantage+ creative enhancements: what to turn off](https://metalla.digital/meta-advantage-plus-creative-enhancements/) — 2026 — agencia
- [AdSpyder — Ad copy length best practices 2026](https://adspyder.io/blog/ad-copy-length-best-practices/) — 2026 — vendor (dataset observacional)
- [Jon Loomer — Recommended ad copy length](https://www.jonloomer.com/qvt/recommended-ad-copy-length/) — practitioner
