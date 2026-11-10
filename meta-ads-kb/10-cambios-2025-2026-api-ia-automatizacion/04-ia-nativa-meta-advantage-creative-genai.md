# IA nativa de Meta para anunciantes (2026): Advantage+ creative, genAI, asistentes y agentes

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A10 (agente) · Ámbito: inventario de lo que existe realmente (GA / beta /
> test / anunciado) en IA generativa de anuncios, asistentes en Ads Manager, automatización de campañas y adopción
> declarada en earnings. Business AI/agentes de mensajería en `05-business-ai-y-agentes.md`.

## TL;DR

- **Adopción masiva declarada**: >8 M de anunciantes usan al menos una herramienta genAI (Q1-2026); 9 M de pequeñas
  empresas al menos una herramienta creativa IA (Q2-2026); el run-rate de las herramientas de **vídeo generativo** llegó a
  $10B en Q4-2025; la adopción de **generación de imagen** se duplicó en Q2-2026. **[OFFICIAL META]** (S10-018…S10-020)
- **Rendimiento declarado** (tests de Meta, sin auditoría externa): vídeo generativo >3% más conversión (Q1-2026); beta
  de vídeo UGC con IA +10% CTR / +8% CVR (NewFronts 2026, vía eMarketer); Advantage+ sales +22% ROAS medio (Cannes 2025).
  **[OFFICIAL META]** como claim; **[HYPOTHESIS]** como expectativa para una cuenta concreta.
- **Lo que está en GA y se usa a diario**: variaciones de texto, generación/expansión de imagen y fondos, image animation,
  video expansion/uncrop, vídeo desde estáticos (GA 6-oct-2026), música generada, traducción de texto, mejoras
  automáticas de vídeo, format display options, website highlights. **[OFFICIAL META]**/[EMPIRICAL]
- **Beta/test**: vídeo de producto desde catálogo, Brand Memory, Ads Creative Studio (rolling out), virtual try-on,
  CTA stickers, landing pages IA, sugerencias de respuesta en formularios, avatares/voiceover UGC.
- **Anunciado sin confirmar en cuentas**: Muse Image dentro de Advantage+ (7-jul-2026).
- **Asistente de Ads Manager (Meta AI business assistant)**: GA desde ~abril-2026 para recomendaciones, diagnóstico e
  incidencias; **acciones agénticas** (crear campañas, cambiar presupuesto/targeting) "coming soon" con preview y
  aprobación; tareas programadas en test. **[OFFICIAL META]** (S10-014, S10-019)
- **Riesgo clave**: Meta activa mejoras por defecto (incluida la reescritura del texto dentro de imágenes, ~27-jul-2026) y
  las nuevas condiciones (30-oct-2026) responsabilizan al anunciante del contenido IA. Hay que gobernar los defaults. **[EMPIRICAL]** (Actualización 2026-11-09: esas condiciones quedaron suspendidas antes de entrar en vigor; ver más abajo.)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Lista oficial de mejoras de Advantage+ creative** (Help Center 297506218282224): incluye "Añadir la navegación por productos", "Añadir animación (IA)" y "Mejorar el texto del contenido multimedia (IA)". **[OFFICIAL META]** La navegación por productos se activó en anuncios existentes ~28-oct salvo opt-out. **[EMPIRICAL]**
> - **API v27 (4-nov)**: product showcase por defecto (`product_extensions`; opt-out `OPT_OUT`). **[OFFICIAL META]**
> - **Incidentes**: anunciantes que retiran anuncios por ediciones de IA que no habían pedido (Adweek, 22-oct) y ofertas detectadas en la web añadidas a anuncios copiados aunque las promociones estuvieran desactivadas (6–8-nov; se controla en Commerce Manager → Settings → Offer merchandising → "Detected offers"). **[EMPIRICAL]**
> - **Q3-2026 (21-oct)**: ~10 M de anunciantes usan IA generativa; vídeo generado +25 % trimestral. **[OFFICIAL META]**
> - **Etiquetado**: Meta pone "AI info" a lo creado o muy editado con su IA y desde jun-2026 lo muestra en "About this ad"; en anuncios comerciales no obliga al anunciante a declararlo (sí en temas sociales, elecciones o política). La Graph v27 añade `is_ai_generated` a los posts de Página. **[OFFICIAL META]**
> - **Condiciones con términos de IA**: suspendidas antes de entrar en vigor (aviso del 5-nov); siguen las del 22-ago-2025. **[OFFICIAL META]**
> - **Para una consultora B2B de IA**: desactiva la navegación por productos y el product showcase si no hay un catálogo que tenga sentido enseñar; revisa "Detected offers" si la web publica precios o descuentos; audita las mejoras anuncio a anuncio y guarda qué aprobaste.
> - Fuentes: S10-099, S10-101, S10-108, S10-113, S10-117, S10-125 a S10-127, S10-138 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Inventario de Advantage+ creative y genAI (estado a 15-oct-2026)

Leyenda de estado: **GA** (disponible general) · **Rolling** (despliegue progresivo) · **Beta** (elegibles) · **Test**
(pocas cuentas/experimento) · **Anunciado** (sin confirmación en cuentas). "Default" = suele venir activado.

### 1.1 Texto

| Feature | Qué hace | Estado | Default | Notas / fuente |
|---|---|---|---|---|
| Text variations / text generation | Variantes de primary text y titular a partir del original, landing y anuncios previos | GA | A menudo ON | Tono de marca, personas (2025) — S10-028 |
| Persona-tailored text | Variantes orientadas a perfiles de cliente | GA/Rolling | — | S10-028 |
| Restricted words and phrases | Lista de términos que la IA no puede usar | GA | — | Imprescindible en sectores regulados — S10-028 |
| Translate text | Traduce copy y muestra preview por idioma | GA (10 idiomas en test Q2-2025) | — | S10-016 |
| Reword identified phrases / highlight image text / reveal details over time / swap selling points | Overlays animados o reescritos sobre la creatividad | GA/Rolling 2025 | Variable | S10-028 |
| Comments keywords / review keywords | Usa comentarios o reseñas positivas como overlay | Test/Rolling | — | Riesgo de citar mal — S10-028 |
| **Reescritura del titular dentro de imágenes subidas** | Genera hasta 8 variantes del texto incrustado manteniendo tipografía/colores | Rolling desde ~27-jul-2026 | **ON (preseleccionado)** | OBSERVADO (Loomer 28-jul; agencias). Controles en Branding y por creatividad — S10-040 |

### 1.2 Imagen

| Feature | Estado | Default | Notas |
|---|---|---|---|
| Background generation (fondos para producto) | GA | Variable | Desde 2024 |
| Image expansion / crop & expand (adaptar a ratios) | GA | Suele ON | Muy adoptado por pymes (S10-016) |
| Image generation (variaciones completas) | GA | Opt-in en creación | Adopción ×2 en Q2-2026; ahora también **imágenes desde vídeo** (S10-020) |
| Visual touch-ups, brillo/contraste, templates | GA | Suele ON | — |
| Promotional text with product repositioning | Rolling (fin 2025) | — | S10-028 |
| Branding (logo, colores, fuentes) para generación | GA | — | Base para "on-brand" (S10-028) |
| Brand Memory (aprende identidad y tono de anuncios previos) | Test limitado (Cannes 2026) | — | S10-052 |
| Muse Image (modelo propio de Meta) | **Anunciado** 7-jul-2026, "coming weeks" | — | No confirmado en cuentas (S10-060, S10-041) |
| Virtual try-on (ropa en modelos virtuales) | Test | — | S10-051, S10-028 |
| CTA stickers personalizados (Stories/Reels) | Test | — | S10-051 |

### 1.3 Vídeo y audio

| Feature | Estado | Default | Notas |
|---|---|---|---|
| Image animation (imagen → vídeo corto) | GA; API por creatividad (28-jun-2026) | Suele ON | S10-002 |
| Video expansion / **video uncrop** (ratios verticales) | GA; API 28-jun-2026 | Suele ON | S10-002 |
| Video filter (mejora color, SDR→HDR) | GA; API 28-jun-2026 | Variable | S10-002 |
| Video generation desde varias imágenes (multi-escena con texto y música) | GA; **vídeo desde estáticos GA 6-oct-2026** | Opt-in | ~2M anunciantes usaban vídeo gen en Q2-2025; +20% QoQ Q3-2025 (S10-016/017/014) |
| Vídeo de producto desde imágenes de catálogo | Beta (Ads Manager y Commerce Manager) | — | S10-014 |
| Ads Creative Studio: conceptos y edición de vídeo (cambiar hook, audio, duración, textos, subtítulos, cierre) | Rolling (desde verano-2026, selected partners → más anunciantes) | — | S10-014 |
| Video highlights (momentos clave) | GA/Rolling | — | S10-028 |
| Música generada por IA acorde al anuncio | GA (desde Q3-2025) | Variable | S10-017 |
| Traducción de voz / voiceover (dubbing) | GA/Rolling; +11 idiomas en Cannes 2026 | — | Lip-sync de Reels (orgánico) existe desde ago-2025; en anuncios, voiceover traducido (S10-052) |
| Traducción de media (subtítulos, overlays) | Test/Rolling (2025); +5 idiomas texto en imagen 2026 | — | S10-028, S10-052 |
| IG Audio Swap (música con copyright → audio libre) | GA vía API (1-jun-2026) | — | S10-002 |
| Vídeos estilo UGC con avatares y voiceover | Anunciado (NewFronts 2026) / beta | — | Meta claim beta +10% CTR, +8% CVR (eMarketer) |
| Muse Video | Solo preview; sin uso publicitario confirmado | — | S10-020 |

### 1.4 Destino, formato y otros

| Feature | Estado | Default | Notas |
|---|---|---|---|
| Optimize website destination (Meta elige URL de tu web) | GA (API v24) | Variable | S10-009 |
| Format display options (carrusel/colección desde un asset; sustituye Flexible format) | GA | — | S10-045 |
| Website highlights / Spotlights | GA/Rolling | — | S10-028 |
| Add site links, relevant comments, enhance CTA, catalog items | GA | Variable | — |
| AI landing pages generadas desde tu web | Test (sep-2026) | — | S10-042 |
| Creative testing tool (hasta 5 variantes con presupuesto) | GA (nov-2025) | — | S10-028 |
| Push delivery to this ad | Rolling (jul-2026) | — | S10-039 |
| Creative Diversity rating (Low/Med/High) | Rolling, "estimado y en desarrollo" | — | S10-041 |
| Creative Approval Flow | Test (Cannes 2026) | — | S10-052 |

### 1.5 Etiquetado y transparencia

- Meta etiqueta como "AI info" los anuncios creados o editados significativamente con IA y, en 2026, detecta metadatos
  C2PA de herramientas de terceros; las imágenes de Muse llevan marca de agua invisible. **[OFFICIAL META]** (política) /
  **[STRONG INFERENCE]** (fechas). Las condiciones efectivas el 30-oct-2026 incorporan los Ad Creative Generative AI Terms. **Actualización 2026-11-09**: las condiciones nuevas **no entraron en vigor**: se aplazaron al 20-nov y el 5-nov Meta las suspendió hasta nuevo aviso (cautelar en Noruega el 28-oct, investigación de la CMA el 30-oct). Siguen las del 22-ago-2025, que ya permiten a Meta acceder, indexar y rastrear los dominios del anunciante. [OFFICIAL META] (S10-113, S10-114 en `fuentes/ledger-10-cambios-api-ia.md`)
  (S10-069)
- Leyes locales: Nueva York exige divulgar "synthetic performers" (2026). Contrastar con área 08.

## 2. Asistentes y automatización de campaña dentro de Meta

| Producto | Qué hace hoy | Estado | Fuente |
|---|---|---|---|
| **Meta AI business assistant** (Ads Manager, Business Suite, Business Support Home) | Recomendaciones personalizadas, insights, resolución de incidencias de cuenta (+20% tasa de resolución), límites de gasto, pagos | GA para elegibles (~abr-2026) | S10-019, S10-064 |
| — memoria (trimestres previos, estacionalidad, objetivos) + creative insights | — | Lanzándose (oct-2026) | S10-014 |
| — importar estrategia/voz de marca de otras IAs | — | Test | S10-014 |
| — tareas programadas y alertas (informes semanales, monitorización, recordatorios de presupuesto) | — | Test | S10-014 |
| — acciones agénticas (crear campaña, generar imagen/texto, cambiar targeting y presupuesto) con preview y aprobación | — | **Coming soon** | S10-014 |
| **Opportunity Score + recomendaciones** | Puntuación 0–100 y recomendaciones aplicables (también por API) | GA (jun-2025; API nov-2025) | S10-050, S10-045 |
| **Manus en Ads Manager** | Informes y análisis en lenguaje natural; conector read-only | Beta (mar-2026) | S10-062 |
| **Meta Ads AI Connectors (MCP + CLI)** | Agentes externos crean/leen/editan; borradores + aprobación | Beta abierta (abr-2026; ampliado jul y oct) | S10-013, S10-014 |
| **Advantage+ end-to-end** (Sales/App/Leads) | Audiencia, placements, presupuesto automáticos | GA | S10-016, S10-017 |
| **Audience discovery en lenguaje natural (Detailed Targeting)** | Describir cliente ideal → audiencias sugeridas | Fin de 2026 | S10-014 |
| **Customer Lifecycle Strategy** | Declarar foco (adquisición, etc.) → exclusiones/recomendaciones coherentes | GA (6-oct-2026) | S10-014 |
| **Incremental attribution** | Optimiza a conversiones incrementales | GA (Q2-2025); +24% incrementales vs estándar (Q4-2025) | S10-016, S10-018 |

Meta declara: anunciantes que usan el asistente ven ~5% más conversiones al mismo coste por conversión, y −12% de coste por
resultado al aplicar recomendaciones de Opportunity Score (presentación Ad Week, vía MediaPost). **[OFFICIAL META]** claim
sin auditoría; tratar como **[HYPOTHESIS]** para una cuenta concreta. (S10-086)

## 3. Existe realmente vs anunciado (resumen)

- **Existe y se puede usar hoy**: todo lo marcado GA en 1.x; asistente para recomendaciones y soporte; MCP/CLI en beta
  abierta; Customer Lifecycle; incremental attribution; vídeo desde estáticos.
- **Existe solo para algunos**: Ads Creative Studio, vídeo desde catálogo, Brand Memory, virtual try-on, CTA stickers,
  AI landing pages, push delivery (casi general), avatares UGC.
- **Anunciado, no verificable en cuentas a 15-oct-2026**: Muse Image en Advantage+, acciones agénticas del asistente,
  audience discovery, checkout en Meta AI.
- **No anunciado**: anuncios dentro de respuestas de Meta AI; un "generador total" desde imagen + presupuesto.

## 4. Cómo usar la IA nativa sin quemar la marca (protocolo recomendado)

1. **Auditoría de defaults por cuenta** (cada trimestre y antes de Q4): listar mejoras ON/OFF a nivel cuenta, anuncio y
   catálogo (los toggles pueden estar en varios niveles). **[EMPIRICAL]**
2. **Branding y restricted words** configurados antes de activar generación; en sectores regulados (salud, finanzas,
   alcohol) restringir claims y desactivar reescrituras de texto. **[STRONG INFERENCE]**
3. **Testear mejoras como variables**: usar el creative testing tool o A/B para comparar "mejoras ON vs OFF" en conceptos
   ganadores; no asumir que el claim medio de Meta aplica. **[EMPIRICAL]**
4. **Generación para volumen de conceptos, no para el concepto**: la IA de Meta es buena multiplicando formatos y ratios;
   el ángulo, la oferta y la prueba social siguen siendo trabajo humano (ver 09). **[STRONG INFERENCE]**
5. **Revisión humana obligatoria** de traducciones, música y texto reescrito en mercados nuevos. **[EMPIRICAL]**
6. **Registro**: guardar qué variantes generó Meta y cuáles se aprobaron (responsabilidad contractual desde 30-oct). **[STRONG INFERENCE]** (2026-11-09: la responsabilidad contractual nueva quedó suspendida, pero registrar sigue siendo buena práctica: hubo anuncios retirados por ediciones de IA no pedidas y ofertas añadidas, S10-127, S10-125.)

## Implicaciones operativas

- Activar por defecto: expansión/uncrop de imagen y vídeo, image animation en estáticos de producto, traducción con
  revisión, vídeo desde estáticos en cuentas sin producción de vídeo. **[EMPIRICAL]**
- Revisar caso a caso: reescritura de texto en imagen, música, comentarios/reseñas como overlay, destino de web optimizado,
  landing pages IA. **[EMPIRICAL]**
- Desactivar por defecto en sectores regulados o marcas premium con guía visual estricta, salvo test controlado. **[STRONG INFERENCE]**

## Errores frecuentes

- Pensar que "Advantage+ creative" es un único interruptor: desde v22 (ene-2025) no existe el bundle estándar; cada
  mejora va por separado, y las nuevas pueden llegar activadas. (S10-007)
- Medir el efecto de las mejoras comparando periodos en vez de testear.
- Dejar que la IA genere claims o precios: las variantes de texto pueden inventar beneficios.

## Preguntas abiertas

- ¿Qué modelo genera hoy las imágenes de Advantage+ (Muse Image vs anteriores)? ¿Cambia la calidad?
- ¿Los vídeos UGC con avatar de Meta tienen restricciones por vertical y etiquetado específico?
- ¿Hay datos independientes del impacto de Ads Creative Studio? (Ninguno a 15-oct-2026.)

## Fuentes clave

- Earnings Q2-2025 → Q2-2026 (S10-016 a S10-020) — meta-investors
- [Advertising Week New York 2026](https://www.facebook.com/business/news/advertising-week-new-york-2026) — 2026-10-06 — meta-oficial (S10-014)
- [2026 Out-of-Cycle Changes](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) — meta-developers (S10-002)
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — practitioner (S10-028)
- [Cannes Lions 2026 recap](https://www.shopifreaks.com/meta-unveils-new-ai-creative-and-creator-tools-at-cannes-lions-2026-heres-a-recap-of-whats-new/) — 2026-06-23 — prensa (S10-052)
- [Muse Image](https://www.investing.com/news/stock-market-news/meta-to-integrate-muse-image-model-into-ad-creative-tools-93CH-4779856) — 2026-07-07 — prensa (S10-060)
- [Meta ramps up genAI-powered ad creation](https://www.emarketer.com/content/meta-ramps-up-genai-powered-ad-creation-marketers-weigh-consumer-trust) — 2026 — prensa
