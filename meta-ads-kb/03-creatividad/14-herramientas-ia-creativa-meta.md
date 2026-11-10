# Herramientas de IA creativa nativas de Meta (2025-2026): qué existe, qué activar y qué evidencia hay

> Última verificación: 2026-10-16 · Autor: A03 (agente) · Ámbito: uso creativo de Advantage+ creative (enhancements), generación de imágenes, fondos, expansión, vídeo, música, traducción/voz, texto, Ads Creative Studio y términos de IA. El changelog general de IA lo cubre el área 10; las políticas, el área 08.

## TL;DR

- **La IA creativa de Meta está en todas partes y parte de ella viene activada por defecto.** Más de 8M de anunciantes usaban al menos una herramienta GenAI de creativo en el Q1 2026 y más de 9M de pequeñas empresas en el Q2 2026; la adopción de image generation se duplicó en un trimestre. **[OFFICIAL META]** (S03-017, S03-016)
- **La evidencia de rendimiento procede casi entera de Meta** y está formulada como "en tests" o "frente a campañas que no lo usan" (sin metodología pública): video generation ">3% higher conversion rates in tests" (Q1 2026); image generation +11% CTR y +7,6% CVR (abr-2025); +7% conversiones (dic-2024); "22% increase in ROAS" con targeting por IA en Advantage+ creative (dic-2024). **[OFFICIAL META]** con sesgo de selección probable (quien activa una herramienta no es comparable con quien no la activa). (S03-017, S03-002, S03-001)
- **Las pruebas independientes son escasas y mixtas.** Una agencia midió +26% de ROAS al **desactivar** text improvements en una cuenta (A/B, sin tamaño de muestra). Las guías de practicantes de 2026 coinciden en desactivar las mejoras que reescriben texto o generan visuales durante tests controlados. Kantar (nov-2025, cientos de anuncios con GenAI de su base LINK, encuesta + facial coding) concluye que "the key isn't whether you use GenAI, but how you use it": el uso no obvio rinde mejor en *branded cut-through*, el obvio pierde branding, y al 41% de los consumidores les molestan los anuncios generados con IA. **[EMPIRICAL]/[CONTESTED]** (S03-053, S03-066)
- **Cambios clave 2025-2026 (con fecha):** "standard enhancements" deprecado como paquete desde la API v22.0 (2025); Creative breakdown por asset (jul-2025); Cannes Lions (17-jun-2025): branding a escala, video generation (beta), video highlights, virtual try-on (test), sticker CTAs; NewFronts (26-mar-2026): voiceover con traducción, vídeos tipo UGC con avatares, generación de vídeo de catálogo (test); **27-jul-2026**: Advantage+ creative reescribe el texto *dentro de las imágenes* por defecto (hasta 8 variantes); Muse Image (Meta Superintelligence Labs, jul-2026) en despliegue hacia anuncios; **6-oct-2026** (Advertising Week): vídeo a partir de imágenes estáticas **GA** en Advantage+ creative, Ads Creative Studio ampliándose, asistente con importación de brand voice (test). **[OFFICIAL META]**/**[EMPIRICAL]** según el ítem (sección 2)
- **Responsabilidad legal: el anunciante responde de lo que genera la IA de Meta.** Los términos de GenAI para creativos (desde mayo-2024) dicen que el anunciante es "solely responsible" de evaluar los outputs, que debe indicar que el contenido está generado o modificado por IA, que no puede eliminar marcas de agua ni metadatos de autenticidad y que los outputs solo pueden usarse en productos de Meta. Se incorporan a los Self-Serve Ad Terms el **30-oct-2026**. **[OFFICIAL META]** (S03-067) **Matiz 2026-11-09**: el post oficial de transparencia de IA (act. 2026-06-01) dice que Meta pone "AI info" por su cuenta a lo creado o muy editado con su IA y que no obliga al anunciante a declararlo en anuncios comerciales (sí en temas sociales, elecciones o política); la obligación de los términos se refiere a los outputs de las herramientas de Meta y a lo que exija la ley **[STRONG INFERENCE]** (S10-138). Las condiciones nuevas del 30-oct quedaron suspendidas (S10-113).
- **Política recomendada (STRONG INFERENCE):** (1) en **tests controlados**, desactivar las mejoras que cambian el mensaje (text improvements, text generation, rewriting de texto en imágenes, overlays, background generation, expansiones generativas) o registrar cuáles están activas; (2) en **BAU**, activar las de bajo riesgo de adaptación (encuadre/flex media, brillo y contraste, enhance CTA) y testear con holdout las generativas; (3) en **sectores regulados** (salud, finanzas, alcohol, claims legales), texto generativo y traducción automática desactivados salvo revisión; (4) configurar **Branding** (logo, colores, fuentes, *restricted words*) antes de usar cualquier generador.
- **La IA multiplica ejecuciones, no ángulos.** Su valor está en producir variaciones, adaptaciones de formato y placement, traducciones y versiones en vídeo de estáticos ganadores. Las variaciones automáticas de un mismo asset añaden poca diversificación real (01) y pueden subir la similitud. **[STRONG INFERENCE]**
- **La señal de Meta sobre los primeros segundos:** el responsable global de Creative Shop dijo en NewFronts 2026 que la gente registra una respuesta positiva o negativa a un anuncio móvil en ~0,4 s ("six is the new 60"). Es una declaración de principio, no un estudio publicado. **[OFFICIAL META]** (declaración; S03-068)

## 1. Inventario de funciones (2026)

| Función (etiqueta Ads Manager / API) | Qué hace | Tipo | Riesgo para el mensaje | Recomendación |
|---|---|---|---|---|
| Visual touch-ups / Image touch-ups (`image_touchups`, `adapt_to_placement`) | Recorta/expande para adaptar a placements | Estándar | Bajo-medio (recortes) | ON en BAU; revisar previews |
| Flex media (`pac_relaxation`) | Usa un medio de una relación de aspecto en todos los placements | Estándar | Bajo | ON si no hay assets por placement |
| Adjust brightness and contrast (`image_brightness_and_contrast`) | Ajustes de imagen | Estándar | Bajo (color de marca) | ON salvo exigencia estricta de color |
| Video auto-crop / uncrop (`video_auto_crop`, `video_uncrop`) | Adapta o expande vídeo (uncrop es generativo) | Estándar / generativo | Medio (bordes, logos) | Mejor entregar 9:16 nativo; uncrop solo con test |
| Expand image (`image_uncrop`) | Añade píxeles generados | Generativo | Medio (producto deformado) | Test con holdout; OFF en producto técnico |
| Generate backgrounds (`image_background_gen`) | Fondos alternativos para producto | Generativo | Medio | Útil en catálogo/fondo liso; Meta cita un caso de Ben & Jerry's (+7% clics) y +2–3% de conversiones en catálogo (vía resumen) |
| Add overlays / image templates (`image_templates`) | Superpone texto o plantillas | Generativo | Alto (genérico, claims) | OFF salvo test |
| Image animation / 3D animation (`image_animation`) | Movimiento sobre imagen estática | Generativo | Bajo-medio | Test; útil para cubrir placements de vídeo |
| Video generation (de estáticos a vídeo multi-escena) | Crea vídeo con animación, texto y música | Generativo | Medio | GA desde 6-oct-2026; Meta: >3% CVR en tests (Q1 2026); test frente a vídeo propio |
| Music (`asset_feed_spec.audios`) | Añade música | Estándar | Medio (choque con la voz, tono) | OFF si el vídeo ya tiene audio diseñado; probar en estáticos/Reels |
| Video filtering (`video_filtering`) | Mejoras visuales (p. ej. SDR→HDR) | Estándar | Bajo | Probar |
| Text improvements (`text_optimizations`) | Reutiliza tus textos en otros campos y frases "de alto rendimiento" | Estándar/IA | **Alto** | OFF en tests; en BAU solo con revisión (Metalla: +26% ROAS al desactivarlo en una cuenta) |
| Text generation / AI text variations | Genera variantes de copy | Generativo | **Alto** (claims, compliance) | Revisión obligatoria; OFF en regulados |
| Rewriting de texto en imágenes = "Enhance media text (AI)" en el Help Center (jul-2026) | Hasta 8 variantes del titular dentro de la imagen | Generativo | **Muy alto** (ofertas, claims) | Branding + restricted words; revisar el Creative Report; OFF en campañas con promociones o claims sensibles (S03-052) |
| Translate text / Translate image text (`text_translation`, `image_text_translation`) | Traduce copy o texto de imagen | IA | Medio-alto | Con revisión nativa |
| Translate voiceover (`translate_voiceover`) / AI voiceover | Voz traducida (API: EN→ES, vídeo único); NewFronts 2026 amplió voiceover y traducción | Generativo | Medio | Muy útil para multi-mercado; revisar pronunciación y tono |
| Enhance CTA (`enhance_cta`) | Combina frases clave con el CTA | IA | Bajo | ON/probar |
| Creative stickers (`creative_stickers`) | Stickers CTA generados | Generativo | Bajo-medio | Probar en Stories/Reels |
| Relevant comments (`inline_comment`) | Muestra un comentario relevante bajo el anuncio | Estándar | Medio (comentario mostrado) | Según el estado de los comentarios (12) |
| Reveal details over time (`reveal_details_over_time`) | Muestra información de la página de producto mientras se ve el anuncio | Estándar | Bajo-medio | Probar |
| Site links / product extensions / dynamic description | Enlaces e items adicionales | Estándar | Medio (dispersa el clic) | Según el funnel; Metalla recomienda OFF en site links |
| Virtual try-on (Cannes 2025, test) | Prendas sobre modelos virtuales | Generativo | Medio | Solo moda y cuando esté disponible |
| UGC-style con avatares de IA (NewFronts 2026, test) | Vídeos tipo UGC con avatares a partir de imágenes de producto | Generativo | **Alto** (autenticidad, testimonios falsos, disclosure) | Prudencia: no presentarlo como testimonio real; disclosure obligatoria |
| Catalog-to-video (test) | Vídeos de producto desde el catálogo | Generativo | Medio | Probar en e-commerce (área 06) |
| Ads Creative Studio | Generación de conceptos de vídeo y variaciones con edición de hooks, audio, duración, overlays y escenas finales; insights de rendimiento | Generativo | Medio | En despliegue (partners → más marcas, oct-2026) |
| Muse Image (jul-2026) | Modelo de imagen de Meta que "can analyze images, improve its own work, and produce better ad variations" | Generativo | Medio | En despliegue; verificar disponibilidad por cuenta |

Fuentes: lista oficial de la API (S03-007); Social Media Today sobre Advertising Week 2026 (S03-069); Marketing Brew sobre NewFronts 2026 (S03-068); CTC sobre rewriting (S03-052); Q2 2026 transcript sobre Muse Image (S03-016); Metalla (S03-053); Flighted (S03-070).

**Control a nivel de cuenta:** fuentes secundarias indican que algunas mejoras solo se pueden desactivar en "Advanced preview" y que existe un ajuste "Test new creative features" en la configuración de publicidad que controla si se aplican funciones nuevas a tus anuncios. **[EMPIRICAL]** (no verificado en el Help Center)

## 2. Cronología 2024-2026 (uso creativo)

| Fecha | Cambio | Fuente / evidencia |
|---|---|---|
| 2024-05-06 | Entran en vigor los términos de GenAI para creativos | Términos de Meta (S03-067) |
| 2024-12-02 | Post de Andromeda: >1M anunciantes y >15M anuncios/mes con GenAI; +7% conversiones con image generation; +22% ROAS con targeting por IA en Advantage+ creative | Meta Engineering (S03-001) |
| 2025 (API v22.0) | "Standard enhancements" deprecado como paquete: cada función se activa por separado | Meta Developers (S03-007) |
| 2025-04-22 | Image generation: +11% CTR, +7,6% CVR (Meta, sin metodología visible) | Meta for Business (S03-002) |
| 2025-06-17 | Cannes Lions: branding a escala, video generation (beta), video highlights, virtual try-on (test), sticker CTAs | Prensa (PPC Land, Adweek) |
| 2025-07-11 | Creative breakdown por asset en Ads Reporting | Fuentes secundarias (S03-049) |
| 2025-07-30 | Q2 2025: casi 2M de anunciantes usan funciones de vídeo generativo (Image Animation y Video Expansion); test de traducción automática de captions a 10 idiomas; "a meaningful percent of our ad revenue" viene de campañas con alguna función GenAI | Transcript Q2 2025 (S03-018) |
| 2026-03-26 | NewFronts: voiceover y traducción, vídeos UGC con avatares, vídeo de catálogo (test), Reels trending ads; "0,4 s" y "six is the new 60" | Marketing Brew (S03-068) |
| 2026-04-29 | Q1: >8M anunciantes con ≥1 herramienta GenAI; video generation >3% CVR en tests | Transcript Q1 (S03-017) |
| 2026-07 | Muse Image (MSL) lanzado; despliegue hacia anuncios | Transcript Q2 (S03-016) |
| 2026-07-27 | Rewriting de texto en imágenes por defecto (hasta 8 variantes) | CTC, Loomer (S03-052) |
| 2026-07-29 | Q2: >9M pequeñas empresas con ≥1 herramienta; image generation x2 de adopción; nueva "end-to-end creative solution" con integraciones de agencias | Transcript Q2 (S03-016) |
| 2026-08-26 | Columna Creative diversity (Low/Medium/High) | Practicantes (S03-012, S03-013) |
| 2026-10-06 | Advertising Week: vídeo desde estáticos **GA**; Ads Creative Studio ampliándose; asistente con brand voice (test) y acciones agénticas (anunciadas); vídeo desde catálogo | Social Media Today (S03-069) |
| 2026-10-30 | Self-Serve Ad Terms incorporan los términos de GenAI; las fuentes secundarias añaden que Meta puede hacer tests que afecten a la entrega y a los creativos sin aviso | Términos de Meta (S03-067) + CTC (S03-028) |

## 3. Evidencia de rendimiento: cómo leerla

| Afirmación | Origen | Problema metodológico | Etiqueta |
|---|---|---|---|
| Video generation >3% CVR "in tests" | Meta, Q1 2026 | Sin detalle del diseño | [OFFICIAL META] |
| Image generation +11% CTR / +7,6% CVR | Meta, abr-2025 | "Campañas que lo usan vs que no": sesgo de selección | [OFFICIAL META] (débil como causalidad) |
| +22% ROAS con targeting por IA en Advantage+ creative | Meta, dic-2024 | Sin metodología | [OFFICIAL META] (débil) |
| Text generation: Unilever +18% compras (Tinuiti); ObjectsHQ +60% ROAS | Meta, nov-2024 | Casos elegidos | [OFFICIAL META] (anecdótico) |
| Desactivar text improvements: +26% ROAS | Metalla, ago-2025 | Una cuenta, sin muestra | [EMPIRICAL] (anecdótico) |
| Rangos de "peor CPA" por enhancement (10–35% con text improvements) | Recopilación de comunidades (vendor) | Sin metodología; Meta no publica lift por enhancement | [HYPOTHESIS] |
| Lo que importa es cómo se usa la IA: uso no obvio mejor en branded cut-through (>40% en el tier superior); IA obvia, peor branding; 41% de consumidores molestos con anuncios de IA | Kantar (nov-2025, "cientos" de anuncios LINK) | Mide eficacia de marca, no conversión; muestra no especificada | [EMPIRICAL] |

**Conclusión:** **CONTEXT-DEPENDENT**. No hay base para "activar todo" ni para "desactivar todo". La única forma fiable es un **holdout propio**: el mismo anuncio con la mejora ON frente a OFF (test nativo, 05), midiendo el CPA y el impacto en el mensaje.

## 4. Cómo usar la IA de Meta dentro del sistema creativo

1. **Estrategia humana, ejecución asistida**: ángulos, personas y ofertas los decide el equipo (03). La IA produce variantes y adaptaciones.
2. **Del estático ganador al vídeo**: usar la generación de vídeo para llevar un estático ganador a placements de vídeo y compararlo con un vídeo producido.
3. **Multi-mercado**: traducción de texto y voiceover para testear mercados nuevos rápido, con revisión nativa.
4. **Producción de estáticos**: generación de fondos e imágenes (y Muse Image cuando esté disponible) para multiplicar contextos de uso del producto, que es diversidad visual real (01).
5. **Branding primero**: configurar logo, colores, fuentes y *restricted words* antes de activar cualquier generador o rewriting.
6. **Revisar previews y el Creative Report** cada semana; desactivar las variantes que rompan el message match (09) o los claims.
7. **Disclosure**: lo hecho o muy editado con las herramientas de Meta recibe la etiqueta «AI info», que desde el 2026-06-01 va dentro de «About this ad». En anuncios comerciales Meta no exige declarar la IA de terceros **[OFFICIAL META]**, y con vídeo reencodado su detección casi nunca salta **[EMPIRICAL]**. Quien obliga es el art. 50 del Reglamento de IA: voz clonada, lip-sync, clon o avatar realista llevan rótulo visible desde el primer segundo. Detalle y tabla en [16](16-ia-generativa-en-anuncios-que-funciona.md) §5 (verificado el 2026-11-10; corrige la versión anterior, que pedía «declaración manual» según fuentes secundarias).

## Implicaciones operativas

- **Checklist pre-lanzamiento**: qué enhancements están activos (captura o registro por anuncio), Branding configurado, restricted words, preview por placement, revisión legal en sectores regulados.
- **Tests**: mejoras de texto y generativas OFF (o una variable a la vez con holdout).
- **BAU**: activar por bloques y medir con test nativo (ON vs OFF) cada trimestre.
- **Equipo**: asignar a alguien la revisión semanal de las variantes generadas por Meta en campañas Advantage+.

## Errores frecuentes

- Dejar activadas las opciones por defecto y no saber qué está viendo el usuario.
- Atribuir a "la creatividad" un resultado que depende de la variante generada por Meta.
- Usar avatares de IA como si fueran clientes reales (riesgo legal y de política).
- Creer que 20 variaciones generadas del mismo asset equivalen a 20 creativos.
- Usar outputs de la IA de Meta fuera de Meta (lo prohíben los términos).

## Preguntas abiertas

- Meta no publica el lift por enhancement ni metodologías de sus cifras.
- Disponibilidad real de Muse Image, Brand Memory y Ads Creative Studio por cuenta y país (no confirmada en fuentes primarias; Brand Memory solo aparece en blogs).
- Alcance exacto de "Meta puede hacer tests que afecten a la entrega y a los creativos sin aviso" (términos del 30-oct-2026): confirmar en el texto legal completo (área 08/10). · **2026-11-09**: suspendidas antes de entrar en vigor; siguen las del 22-ago-2025 (S10-113)

## Fuentes clave

- [Meta for Developers — Advantage+ creative: get started](https://developers.facebook.com/docs/marketing-api/creative/advantage-creative/get-started) — vigente — meta-developers
- [Meta — Ad Creative Generative AI Terms](https://www.facebook.com/legal/terms/ad_creative_generative_ai_terms) — 2024-05-06 (actualización 2026-10-30) — meta-oficial
- [Meta Q1 2026 transcript](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q1/META-Q1-2026-Earnings-Call-Transcript.pdf) — 2026-04-29 — meta-investors
- [Meta Q2 2026 transcript](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q2/META-Q2-2026-Earnings-Call-Transcript.pdf) — 2026-07-29 — meta-investors
- [Social Media Today — Meta introduces new AI-powered tools at Advertising Week](https://www.socialmediatoday.com/news/meta-introduces-new-ai-powered-tools-at-ad-week-2026/832288/) — 2026-10-06 — prensa
- [Marketing Brew — Meta at NewFronts 2026](https://www.marketingbrew.com/stories/2026/03/27/meta-pitches-advertisers-on-tools-to-help-with-shrinking-user-attention-spans-at-newfronts) — 2026-03-27 — prensa
- [Common Thread — Meta is rewriting your ad images by default](https://commonthreadco.com/blogs/coachs-corner/meta-advantage-plus-creative-image-text-rewriting-ecommerce-2026) — 2026-08-18 — agencia
- [Metalla — Advantage+ creative enhancements](https://metalla.digital/meta-advantage-plus-creative-enhancements/) — 2025-08-26 — agencia
- [Flighted — Advantage+ AI creative enhancements explained](https://www.flighted.co/blog/metas-advantage-plus-ai-creative-enhancements-each-one-explained) — 2026-07-16 — agencia
- [Kantar — Rethinking AI-generated advertising](https://www.kantar.com/inspiration/advertising-media/rethinking-ai-generated-advertising) — 2025-11-04 — vendor (investigación)
- [PPC Land — Meta announces generative AI advances at Cannes Lions](https://ppc.land/meta-announces-generative-ai-advances-for-advertisers-at-cannes-lions/) — 2025-06 — prensa
