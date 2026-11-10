# Comentarios y prueba social en anuncios de Meta

> Última verificación: 2026-10-15 · Autor: A03 (agente) · Ámbito: papel de los comentarios y reacciones como prueba social y como señal; moderación (ocultar, borrar, filtrar, desactivar); responder; acumular prueba social con post IDs; "relevant comments" de Advantage+; comentarios como fuente de investigación. Las políticas los cubre el área 08.

## TL;DR

- **Los comentarios son parte del creativo.** En Feed y Reels, el usuario ve el recuento de reacciones y comentarios, y a menudo los abre antes de hacer clic. Una sección de comentarios llena de quejas sin respuesta es "anti-prueba social"; una con preguntas bien respondidas es una FAQ que vende. **[STRONG INFERENCE]**
- **La retroalimentación negativa de los usuarios es una señal de calidad oficial.** Ocultar el anuncio, ocultar todos los anuncios del anunciante o reportarlo cuentan como feedback. Meta puede volver a revisar anuncios ya aprobados si la gente los oculta, bloquea o reporta, y si una Página o cuenta publica repetidamente anuncios de baja calidad, "our systems may start considering all ads from your Page, domain, ad account or other associated entities as lower quality". **[OFFICIAL META]** (citado por Jon Loomer, S03-061)
- **No hay evidencia pública de que el número de comentarios por sí mismo mejore la entrega.** Lo que sí está documentado es que el engagement bait (pedir likes o comentarios de forma artificial) se considera contenido de baja calidad. **No hay que fabricar comentarios ni pedirlos con engagement bait.** **[OFFICIAL META]** (S03-061)
- **Ocultar ≠ borrar.** Un comentario oculto deja de verse públicamente, pero su autor (y, según varias fuentes, sus amigos) lo siguen viendo, de modo que no escala el conflicto. Borrar lo elimina de forma permanente y el autor puede notarlo. Para trolls, spam y estafas, ocultar o borrar y bloquear. Para quejas legítimas, **responder** (y llevarlas a privado si hace falta). **[EMPIRICAL]** (fuentes secundarias concordantes)
- **Desde 2025-2026 hay controles de comentarios para anuncios** (permitir, limitar o desactivar), pero su disponibilidad varía por objetivo, placement y cuenta. Meta documenta además la vía de desactivar comentarios en Instagram y los filtros de palabras clave y blasfemias de la Página, que se aplican a sus anuncios. **[OFFICIAL META]**/**[EMPIRICAL]** (S03-062)
- **"Relevant comments"** (`inline_comment`) es una mejora de Advantage+ creative que muestra un comentario relevante bajo el anuncio. Es prueba social automática, pero sin control total sobre qué comentario se muestra. Algunos practicantes recomiendan desactivarla (Metalla) y otros la mantienen (varias guías 2026). **[OFFICIAL META]** función / **[CONTESTED]** uso (S03-007, S03-053)
- **Reutilizar el mismo post (post ID) en varios ad sets o campañas acumula reacciones y comentarios en un solo lugar.** Relanzar un ganador como anuncio nuevo los pierde. **[EMPIRICAL]** (práctica estándar; mecánica de Meta "use existing post")
- **Los comentarios son la mejor fuente gratuita de investigación de cliente**: objeciones, lenguaje literal e ideas de hooks y ángulos, tanto en anuncios propios como de la competencia (03, 11). **[STRONG INFERENCE]**

## 1. Cómo afectan los comentarios

| Efecto | Mecanismo | Evidencia |
|---|---|---|
| **Prueba social positiva** | Reacciones, testimonios espontáneos y respuestas útiles aumentan la credibilidad | Principio de persuasión; sin estudio público de Meta 2025-2026 que lo cuantifique. **[STRONG INFERENCE]** |
| **Prueba social negativa** | Quejas sin respuesta, acusaciones de estafa y comentarios de envío o atención al cliente reducen la confianza y la CVR | **[STRONG INFERENCE]** |
| **Señal de calidad (negativa)** | Hide/report del anuncio = feedback negativo usado en calidad y revisiones | **[OFFICIAL META]** (S03-061) |
| **Señal de entrega (positiva)** | El engagement es una de las acciones que el sistema puede predecir, pero en campañas de conversión se optimiza al evento elegido | No hay evidencia de que "más comentarios = más entrega" en campañas de conversión. **UNPROVEN** |
| **Atribución** | Desde mar-2026 las conversiones tras interacciones no-link (comentario, like, guardado) cuentan como engage-through (1 día), no como click-through | **[EMPIRICAL]** (S03-043; área 04) |
| **Investigación** | Fuente de objeciones y lenguaje | **[STRONG INFERENCE]** |

## 2. Moderación: opciones y cuándo usar cada una

| Acción | Qué pasa | Usar para | Evitar para |
|---|---|---|---|
| **Responder en público** | Visible para todos | Preguntas frecuentes (precio, envío, tallas, cómo funciona), objeciones razonables, elogios (agradecer) | Datos personales, disputas largas |
| **Responder y llevar a privado** | Respuesta pública breve + DM | Quejas de pedido o servicio | — |
| **Ocultar** | Invisible para el público; el autor (y según fuentes, sus amigos) aún lo ven; reversible | Trolls, insultos, competidores, spam leve, comentarios que generan conflicto | Quejas legítimas (es mejor responder) |
| **Borrar** | Eliminación permanente | Spam, estafas, datos personales, enlaces maliciosos, contenido ilegal | Críticas legítimas (el efecto Streisand es real) |
| **Bloquear/banear al usuario** | No puede volver a comentar en la Página | Reincidentes, bots | — |
| **Filtro de palabras clave y blasfemias** (ajustes de la Página) | Oculta automáticamente los comentarios con esas palabras; se aplica a los anuncios de la Página | Insultos, términos de estafa, competidores, "precio" (si se quiere responder por DM) | Bloquear términos legítimos que conviene responder |
| **Desactivar/limitar comentarios** (control a nivel de anuncio donde exista; vía Instagram según Meta) | Sin comentarios o limitados | Temas sensibles (salud, política, crisis), marcas con ataques sistemáticos | Por defecto: se pierde prueba social y feedback |
| **Herramientas de terceros** (auto-hide con IA) | Moderación 24/7 | Cuentas con mucho volumen | Sin supervisión (falsos positivos) |

**Disponibilidad (verificado en el Help Center el 2026-10-16, S03-062):** en Ads Manager → Edit → menú "..." junto al nombre del anuncio → *More options* → *Manage Facebook comments* / *Manage Instagram comments* / *Manage Threads replies*. Desde ahí, en Facebook se puede dar like y responder; en Facebook, Instagram y Threads se puede **ocultar o reportar** (no borrar). Los comentarios de Instagram no se pueden gestionar si el anuncio corre con la identidad de la Página de Facebook sin perfil de IG conectado, y lo mismo pasa con Threads. La moderación proactiva se hace con el **profanity filter** de la Página de Facebook y **Hidden Words** en Instagram/Threads; esos filtros "extend to ads from the Page or profile". **[OFFICIAL META]** Algunas guías describen además un ajuste *Comment controls* (permitir/limitar/desactivar) a nivel de anuncio con disponibilidad variable. **[EMPIRICAL]**: verificar en la cuenta.

## 3. Protocolo de gestión de comentarios (recomendado)

1. **SLA**: revisar los anuncios con más gasto al menos 1–2 veces al día; los nuevos con gasto alto, cada pocas horas en las primeras 48 h.
2. **Clasificar** cada comentario: pregunta / objeción / elogio / queja de servicio / troll-spam / estafa-suplantación.
3. **Plantillas de respuesta** por tipo, en tono de marca y con datos verificables (sin claims nuevos no aprobados).
4. **Escalado** a atención al cliente para pedidos y a legal para acusaciones graves.
5. **Registro de objeciones** (hoja compartida): cada objeción repetida es un candidato a ángulo (03) o a cambio de landing u oferta (09).
6. **Cuidado con las estafas**: los anuncios con mucho alcance atraen comentarios de suplantación ("escríbeme por WhatsApp…"); se ocultan o borran y se bloquea al autor.

## 4. Acumular prueba social sin perder diversidad

- **Post ID único por creativo ganador**: usar "publicación existente" o el mismo ID de creativo al duplicar en otras campañas, para que reacciones y comentarios se sumen.
- **Al iterar** (nuevo hook, nuevo formato) se empieza de cero en prueba social. Es un coste a tener en cuenta en la decisión de iterar frente a mantener (06).
- **Partnership ads / contenido de creadores**: el post del creador puede traer su propia prueba social (comentarios de su audiencia). Ver área 07.
- **Relevant comments** (Advantage+): muestra automáticamente un comentario relevante. Útil si la sección de comentarios es sana. Desactivarlo si hay riesgo de que muestre comentarios problemáticos o en sectores regulados. **[CONTESTED]**

## 5. Lo que no se debe hacer

- Pedir comentarios o reacciones con engagement bait ("comenta SÍ si…"): Meta lo cataloga como contenido de baja calidad (S03-061).
- Comentarios falsos, compra de engagement o "sembrar" comentarios con cuentas propias: infringe políticas y, en muchas jurisdicciones, la normativa de consumo (reseñas falsas).
- Borrar sistemáticamente toda crítica: lo nota la audiencia y elimina un feedback útil.
- Dejar sin respuesta preguntas de compra (precio, envío): cada una es una venta perdida y una señal de abandono para los demás.

## Implicaciones operativas

- La gestión de comentarios forma parte del **sistema creativo**, no de "community management" aparte.
- **KPI sugeridos**: tiempo medio de primera respuesta en anuncios con gasto, % de comentarios negativos sin respuesta, nº de objeciones nuevas registradas por semana.
- **Antes de escalar un anuncio**, revisar su sección de comentarios: si está tóxica, conviene limpiarla o lanzar otro post del mismo creativo con moderación activa desde el inicio.

## Errores frecuentes

- No mirar los comentarios de los anuncios con más gasto.
- Responder con plantillas robóticas o discutir en público.
- Relanzar ganadores con IDs nuevos y perder la prueba social acumulada.
- Activar "relevant comments" sin revisar qué comentarios hay.
- Tratar los comentarios negativos solo como un problema de imagen y no como un dato de oferta, producto o creativo.

## Preguntas abiertas

- No hay datos públicos que cuantifiquen el efecto de la prueba social de los comentarios en la CVR o en la entrega en 2025-2026.
- Disponibilidad exacta del control de comentarios a nivel de anuncio en 2026 (varía por cuenta).

## Fuentes clave

- [Jon Loomer — Low-quality ad content and post-click experiences (citas de Meta)](https://www.jonloomer.com/low-quality-ad-content-and-post-click-experiences/) — 2024-03-07 (mod. 2025-03-06) — practitioner
- [Meta Business Help Centre — Manage comments on your ads in Meta Ads Manager](https://en-gb.facebook.com/business/help/1129470964230971) — vigente — meta-oficial (contenido vía resultados de búsqueda)
- [NapoleonCat — Facebook ads comment moderation](https://napoleoncat.com/uses/facebook-ads-comment-moderation/) — 2026 — vendor
- [Superpower — How to turn off comments on Meta ads 2026](https://superpower.social/blogs/how-to-turn-off-comments-on-meta-ads-in-2026-and-why-most-advertisers-shouldnt) — 2026 — vendor
- [Meta for Developers — Advantage+ creative (inline_comment)](https://developers.facebook.com/docs/marketing-api/creative/advantage-creative/get-started) — vigente — meta-developers
- [Metalla — Advantage+ creative enhancements (relevant comments: off)](https://metalla.digital/meta-advantage-plus-creative-enhancements/) — 2025-08-26 — agencia
