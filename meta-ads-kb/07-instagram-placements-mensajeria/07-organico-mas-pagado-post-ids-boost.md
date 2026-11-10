# Orgánico + pagado: usar posts como anuncios, post IDs, prueba social y Boost

> Última verificación: 2026-10-16 · Autor: A07 (agente) · Ámbito: cuándo y cómo convertir publicaciones orgánicas (Instagram/Facebook) en anuncios, cómo consolidar prueba social con post IDs, qué se pierde al editar, Boost vs Ads Manager, y cómo encaja con Trial Reels, collabs y partnership ads.

## TL;DR

- **Promocionar un post existente conserva likes, comentarios y compartidos** y los acumula entre todos los anuncios que usen ese mismo post (mismo post ID). Duplicar un anuncio "normal" o editar su creativo crea un post nuevo y empieza de cero. [EMPIRICAL] (Loomer; técnica estándar)
- **Un post conectado a un anuncio (activo o inactivo) no se puede editar.** Para editar sin perder la prueba social hay que desconectar los anuncios, editar y volver a conectar. [EMPIRICAL] ([Loomer](https://www.jonloomer.com/how-to-edit-a-facebook-ad-and-retain-social-proof/), act. mar-2025; documentado para Facebook)
- **La prueba social vale menos de lo que se cree:** Loomer (abr-2026) duplicó un anuncio con >6.000 comentarios; el nuevo, sin prueba social, tuvo CPL 46 $ vs 50 $ del original en dos semanas ("dentro de la aleatoriedad"). Conclusión: no dejes que el miedo a perder engagement bloquee la iteración creativa. [EMPIRICAL, n=1] ([pubcast](https://pubcast.jonloomer.com/social-proof-might-not-matter-after-all/))
- **Regla de decisión:** usa post existente cuando el post ya tiene prueba social **relevante y positiva** o cuando quieres concentrar comentarios (FAQ, testimonios); usa anuncio "nuevo" (dark post) cuando necesites variantes de texto, Advantage+ creative completo, URLs/UTMs específicas o probar muchos hooks. [STRONG INFERENCE]
- **Boost** crea un anuncio real con opciones recortadas (en IG: visitas al perfil, web, mensajes); bueno para validar rápido; malo para medir negocio. El flujo eficiente es: orgánico/Trial Reel → Boost corto (opcional) → **mismo post en Ads Manager** con objetivo de conversión. [STRONG INFERENCE]
- **Bloqueadores típicos para convertir un orgánico en anuncio:** música con licencia, Reels anteriores al 15-oct-2021, efectos de cámara/GIFs, ciertos elementos interactivos, contenido de terceros sin permiso. [OFFICIAL META] (Ads Guide Reels)
- **Facebook está limitando enlaces orgánicos** (test desde dic-2025: algunas Páginas y perfiles profesionales limitados a 2 posts con link al mes salvo Meta Verified). Refuerza el uso de pago para distribuir enlaces. [OFFICIAL META] (test confirmado por portavoz; estado 2026 no verificado)

## 1. Por qué combinar orgánico y pago

Desde primeros principios [STRONG INFERENCE]:
1. **El orgánico es un pre-test barato**: los posts que retienen y se comparten en frío (Trial Reels, Explore) suelen tener buenas métricas de atención como anuncio.
2. **El pago acumula prueba social visible** en un post que luego también ve el tráfico orgánico (perfil, grid): sinergia de "landing page" en Instagram.
3. **La identidad y el tono orgánico reducen la ceguera publicitaria** en Reels/Stories.
4. **Riesgo**: lo que funciona en orgánico (entretenimiento, tendencia) no siempre vende; mide en conversión, no en vistas.

## 2. Cómo usar un post existente (FB e IG)

| Paso | Ads Manager | API |
|---|---|---|
| Seleccionar | En el anuncio: "Use existing post" → elegir publicación de la Página o de Instagram (listado con columna de post ID) | Facebook: `object_story_id` = `pageID_postID`; Instagram: `source_instagram_media_id` |
| CTA y destino | En posts de IG puedes añadir botón y URL del anuncio; en posts de FB con link, el destino es el del post | — |
| Texto | Es el caption del post (no editable desde el anuncio) | — |
| Reutilizar | Copiar el post ID desde el anuncio ganador ("Post with comments" / vista previa) y usarlo en nuevos ad sets/campañas | Mismo ID |
| Advantage+ creative | Algunas mejoras no aplican o están limitadas en posts existentes (verificar en el anuncio) | — |

[OFFICIAL META] (campos API, [click-to-Instagram docs](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-instagram)) + [EMPIRICAL] (flujo de Ads Manager). Detalle de qué mejoras de Advantage+ funcionan con posts existentes: **no verificado** en documentación 2026.

**Técnica de consolidación de prueba social ("post ID strategy")**:
1. Lanzar el creativo como anuncio nuevo en el ad set de testing.
2. Cuando gana, obtener su post ID (el anuncio genera un post no publicado de la Página/IG).
3. En escalado (otros ad sets, campañas, audiencias), crear anuncios con "existing post" = ese ID, en lugar de duplicar.
4. Resultado: todos los anuncios comparten comentarios/likes. [EMPIRICAL]

**Trampas**:
- Si el post acumula comentarios negativos o spam, también se acumulan (ver `08-…`).
- Un post conectado a anuncios no se puede editar; planifica el copy antes. [EMPIRICAL]
- En mensajería (CTM), el API indica que los anuncios creados con `object_story_id` no están soportados en algunos casos (Click to Messenger). Verifica antes de planificar post IDs en campañas de mensaje. [OFFICIAL META] ([docs CTM](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-messenger))

## 3. ¿Cuánto vale la prueba social? (debate)

| Postura | Argumento | Evidencia |
|---|---|---|
| Vale mucho | Comentarios positivos y muchos likes aumentan confianza y CTR; el sistema podría favorecer anuncios con engagement | Test de Agorapulse citado por vendors (comentarios positivos → mayor CTR); vendors de moderación; no hay dato público de Meta sobre ranking. [CONTESTED] |
| Vale menos de lo que se cree | El contenido manda; un anuncio nuevo sin prueba social puede rendir igual | Loomer abr-2026: CPL 46 $ (nuevo) vs 50 $ (original con >6.000 comentarios), n=1, 2 semanas. [EMPIRICAL] |

**Postura de trabajo** [STRONG INFERENCE]: la prueba social es un *plus* que no debe frenar la iteración. Prioriza el ritmo de testeo creativo; usa post IDs para escalar ganadores (gratis), no para "proteger" anuncios cansados.

## 4. Boost vs Ads Manager (Instagram y Facebook)

| Criterio | Boost | Ads Manager |
|---|---|---|
| Velocidad | 2 minutos desde la app | 10–20 minutos |
| Objetivos (IG) | Visitas al perfil, visitas a web, mensajes (WhatsApp/IG Direct/Messenger) | Todos |
| Optimización a conversiones con pixel/CAPI | No | Sí |
| Edición tras aprobación | Audiencia, presupuesto, duración | Completa |
| Testing (A/B, varias creatividades) | No | Sí |
| Atribución y breakdowns | Limitados | Completos |
| Encaje | Creadores, pymes sin estructura, validar un post | Cualquier objetivo de negocio |

[STRONG INFERENCE] ([Relevant Audience](https://www.relevantaudience.com/facebook-ads/what-is-a-boosted-post/), Metricool 2026). Nota: el Boost corre en la misma subasta; no es "peor dinero", es dinero con menos control. Un Boost de "mensajes" a WhatsApp o IG Direct es una forma legítima de CTM para pymes sin Ads Manager.

## 5. Flujos recomendados orgánico → pago

**A. Creador/infoproducto con DMs**
1. Publicar 3–5 Trial Reels con hooks distintos (ver `04-…`).
2. Ganador (compartidos/vista, retención) → "share with everyone".
3. Activar comment-to-DM orgánico con keyword.
4. Promocionar el **mismo post** en Ads Manager (Engagement → Messaging o Leads → Instagram), con la misma keyword en el copy si usas Reply to Keywords/herramienta.

**B. Ecommerce**
1. Orgánico/UGC con producto → identificar posts con guardados y comentarios de intención ("¿precio?", "¿talla?").
2. Promocionar como post existente en campaña de ventas, con product tags/catálogo si aplica.
3. Responder comentarios de intención (son FAQ públicas).

**C. Negocio local/servicios**
1. Post de testimonio o antes/después (dentro de políticas) con buen engagement local.
2. Promocionar con CTA a WhatsApp/IG Direct (CTWA o multi-destino).
3. El post acumula comentarios de vecinos/clientes = prueba social local.

## 6. Restricciones de elegibilidad frecuentes

| Restricción | Detalle | Evidencia |
|---|---|---|
| Música con licencia | Reels/partnership ads con música comercial no son promocionables | [OFFICIAL META] |
| Reels antiguos | Reels publicados antes del 15-oct-2021 no son elegibles | [OFFICIAL META] (Ads Guide) |
| Efectos/GIFs/product labels | No admitidos en Reels ads | [OFFICIAL META] |
| Elementos interactivos (encuestas, preguntas) en Stories/Reels | Pueden impedir la promoción | [HYPOTHESIS] (vendor) |
| Contenido de terceros | Requiere permiso (partnership ad o licencia) | [OFFICIAL META] |
| Posts editados conectados a anuncios | No editables mientras estén conectados | [EMPIRICAL] |
| Facebook: 2 posts con link/mes en test | Afecta a Páginas y perfiles profesionales en el test; Meta Verified lo levanta; links en comentarios siguen permitidos | [OFFICIAL META] (test dic-2025, [Press Gazette](https://pressgazette.co.uk/news/facebook-tests-charging-creators-and-businesses-to-post-more-than-two-links-per-month/)) |

## Implicaciones operativas

- Estándar de cuenta: ganadores escalados **siempre** con post ID (no duplicar).
- Calendario editorial con hueco para "posts candidatos a anuncio" (sin música comercial, con safe zones de anuncio).
- Revisar comentarios de los posts usados como anuncio a diario (la prueba social puede volverse negativa).
- Boost solo como herramienta de validación o para clientes sin capacidad de Ads Manager.

## Errores frecuentes

- Duplicar el anuncio ganador 10 veces → 10 posts distintos con prueba social dispersa.
- Editar el texto del anuncio ganador para "mejorarlo" y perder la acumulación (y el aprendizaje del anuncio).
- Promocionar orgánicos virales que no tienen relación con la oferta.
- Esperar que el Boost optimice a ventas.
- Tratar la prueba social como intocable y no renovar creatividades fatigadas.

## Preguntas abiertas

- Qué mejoras de Advantage+ creative se aplican a posts existentes en 2026 (docs no claras).
- Estado en oct-2026 del test de límite de links orgánicos en Facebook.
- ¿Se mantiene la acumulación de prueba social igual en Threads y en Status? (sin documentación).

## Fuentes clave

- [How to Edit a Facebook Ad and Retain Social Proof](https://www.jonloomer.com/how-to-edit-a-facebook-ad-and-retain-social-proof/) — 2018 (mod. 2025-03-01) — practitioner
- [Social proof might not matter after all](https://pubcast.jonloomer.com/social-proof-might-not-matter-after-all/) — 2026-04-06 — youtube/podcast
- [Click to Instagram Direct ads (API: source_instagram_media_id, object_story_id)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/messaging-ads/click-to-instagram) — vigente — meta-developers
- [Meta Ads Guide – Instagram Reels](https://www.facebook.com/business/ads-guide/update/video/instagram-reels) — vigente — meta-oficial
- [What Is a Boosted Post?](https://www.relevantaudience.com/facebook-ads/what-is-a-boosted-post/) — 2026 — agencia
- [Facebook tests charging to post more than two links per month](https://pressgazette.co.uk/news/facebook-tests-charging-creators-and-businesses-to-post-more-than-two-links-per-month/) — 2025-12 — prensa
- [Trial Reels](https://about.fb.com/news/2024/12/trial-reels-try-content-non-followers-first/) — 2024-12-10 — meta-oficial
