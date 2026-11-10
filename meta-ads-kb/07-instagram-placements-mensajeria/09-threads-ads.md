# Threads ads: estado octubre 2026

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A07 (agente) · Ámbito: disponibilidad, cronología, formatos, configuración, identidad, brand safety, rendimiento reportado y recomendaciones de uso de anuncios en Threads.

## TL;DR

- **Threads ads es global** para anunciantes (desde abril de 2025) y para usuarios de todos los mercados (anuncio 21-ene-2026, rollout gradual desde la semana siguiente con entrega inicial "low"). [OFFICIAL META] ([Meta for Business, "Ads on Threads: One Year In"](https://www.facebook.com/business/news/ads-on-threads-one-year-in))
- **Escala**: >400 M MAU y ~150 M DAU (ene-2026, Meta); 500 M MAU reportados a mediados de 2026. [OFFICIAL META] (400 M/150 M) + [STRONG INFERENCE] (500 M)
- **Formatos**: imagen, vídeo, carrusel, 4:5, Advantage+ catalog y app ads. Placement único: **Threads Feed**, solo móvil. [OFFICIAL META]
- **Se añade automáticamente** a campañas Advantage+ y manuales que tengan Advantage+ placements; en configuración manual vía API, `threads_stream` **requiere** Instagram Feed (`stream`). Si no quieres Threads, tendrás que excluirlo (cada vez más difícil a nivel ad set; ver `02-…`). [OFFICIAL META]
- **Identidad**: desde septiembre de 2026 ya **no hace falta cuenta de Instagram** ni usernames coincidentes; las empresas pueden anunciarse con su perfil nativo de Threads (rollout gradual). [OFFICIAL META] ([SMT, 21-sep-2026](https://www.socialmediatoday.com/news/threads-advertisers-will-no-longer-need-an-instagram-account/830967/))
- **Brand safety**: verificación de terceros (Meta Business Partners) extendida al feed de Threads en ene-2026; block lists de Threads reportadas desde mayo-2026. [OFFICIAL META] (verificación) + [STRONG INFERENCE] (block lists)
- **Rendimiento**: no hay datos públicos fiables. Los "CPM 30–40 % más bajos que Instagram" proceden de blogs sin datos verificables. Meta no ha publicado casos. Trátalo como **inventario incremental barato de calidad desconocida**: mide por breakdown y por conversiones aguas abajo. [HYPOTHESIS]
- **Sin segmentación nativa de Threads** (por temas, cuentas seguidas): usa la segmentación general de Meta. Sin lead forms nativos según guías; sin anuncios en búsqueda ni DMs de Threads. [STRONG INFERENCE]

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Threads como ubicación por defecto en todas las campañas** (19–26-oct-2026): solo lo dicen agregadores y agencias; Threads ya estaba en Advantage+ placements desde el 21-ene-2026, y no hay fuente de Meta de que se active en campañas con ubicaciones manuales. **[CONTESTED]**
> - Fuentes: S10-132 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. Cronología verificada

| Fecha | Hito | Evidencia |
|---|---|---|
| 24-ene-2025 | Test con anunciantes seleccionados en EE. UU. y Japón | [OFFICIAL META] (citado por TechCrunch/Postory) |
| 23-abr-2025 | Abierto a "all eligible advertisers globally" (entrega solo a usuarios de mercados seleccionados) | [OFFICIAL META] |
| 8-may-2025 | NewFronts: test de vídeo 16:9 / 1:1 entre posts orgánicos con grupo pequeño de anunciantes | [OFFICIAL META] ([NewFronts](https://www.facebook.com/business/news/meta-at-iab-newfronts-2025)) |
| sep-2025 | Crear anuncios de Threads a partir de posts existentes de FB/IG en Ads Manager | [STRONG INFERENCE] (prensa) |
| sep–oct-2025 | Carrusel (6-oct según Postory), formato de imagen ampliado, catálogo (28-oct) | [STRONG INFERENCE] (fechas exactas difieren entre fuentes: SMT dice septiembre) |
| 21-ene-2026 | Anuncio de expansión a usuarios de todos los mercados; 4:5; catalog y app ads; verificación de brand safety en Threads | [OFFICIAL META] |
| 26-ene-2026 (semana) | Inicio del rollout global a usuarios | [OFFICIAL META] |
| may-2026 | Block lists de brand safety para Threads | [STRONG INFERENCE] (AdsUploader) |
| jul-2026 | Un blog afirma "expansión global de carrusel y vídeo" | [CONTESTED] (contradice lo publicado por Meta en enero; probablemente erróneo) |
| sep-2026 | Anuncios en Threads sin cuenta de Instagram | [OFFICIAL META] |

## 2. Cómo se activa

1. **Identidad**: perfil de Threads de la empresa gestionado en Meta Business Settings (junto a FB, IG, WhatsApp). Desde sep-2026 no necesita IG. [OFFICIAL META]
2. **Campaña**: cualquier campaña con Advantage+ placements incluye Threads donde esté disponible. En manual: seleccionar Threads Feed (requiere IG Feed seleccionado según la referencia de API). [OFFICIAL META]
3. **Objetivos**: guías de terceros indican Awareness, Traffic, Leads (destino web; sin instant forms nativos) y Sales; app ads y catálogo confirmados por Meta. [STRONG INFERENCE]
4. **Creatividad**: 4:5 recomendado (1080×1350), 1:1 soportado; vídeo con subtítulos; texto principal 80–160 caracteres, titular ~40, sin hashtags ni URLs en el texto. [STRONG INFERENCE] (Postory/Metricool)
5. **Posts existentes**: desde sep-2025 se pueden crear anuncios de Threads a partir de posts de FB/IG. [STRONG INFERENCE]

## 3. Por qué (y cuándo) Threads puede valer la pena

Primeros principios [STRONG INFERENCE]:
- **Inventario nuevo + baja competencia + ad load inicial bajo** → CPM probablemente menor durante la fase de adopción.
- **Contexto de lectura y conversación** → creatividades con más texto y tono informal; el comentario negativo es más visible (cultura de réplica).
- **Audiencia** sesgada hacia usuarios de Instagram adultos jóvenes, tecnología, medios, creadores (según agencias; no hay demografía oficial reciente).
- **Riesgo**: impresiones de baja atención si el creativo es un Reel recortado; frecuencia acumulada con Instagram si usas la misma pieza.

**Encajes probables**: D2C visual, apps, medios/tecnología/creadores, marcas con voz conversacional. **Encajes débiles**: servicios locales, audiencias >45, lead gen con formulario nativo. [HYPOTHESIS] (agencias)

## 4. Medición y reporting

- Threads aparece como placement en el breakdown; algunas herramientas indican que los informes por defecto no lo desglosan: añade breakdown por placement. [STRONG INFERENCE]
- No hay optimización ni reporting específico de Threads (mismos eventos/pixel/CAPI). [STRONG INFERENCE]
- **Test recomendado**: si la cuenta aún permite exclusión a nivel ad set, A/B "con/sin Threads" 2–4 semanas con presupuesto igual; si no, compara coste por resultado y calidad aguas abajo del placement Threads frente a IG Feed en el breakdown, sabiendo que es correlacional. [HYPOTHESIS]

## 5. Brand safety en Threads

- Verificación de terceros (IAS, DoubleVerify, Zefr vía Meta Business Partners) extendida al feed de Threads (ene-2026). [OFFICIAL META]
- Block lists específicas (may-2026). [STRONG INFERENCE]
- Comentarios y respuestas públicas en Threads pueden ser más críticos: prepara respuestas (ver `08-…`). [HYPOTHESIS]

## 6. Creatividad para Threads

Threads es una superficie de lectura: el usuario está escaneando texto y conversaciones, no viendo vídeo a pantalla completa. Implicaciones [STRONG INFERENCE]:

| Elemento | Recomendación | Por qué |
|---|---|---|
| Texto principal | 80–160 caracteres, primera frase con opinión o dato; tono de persona, no de marca | Compite con posts de texto; el texto se lee antes que la imagen |
| Imagen | 4:5 o 1:1, limpia, con poco texto quemado; capturas, gráficos simples, producto en contexto | Lo vertical se recorta/centra |
| Vídeo | Corto, subtitulado, que funcione sin sonido; versión 4:5 del Reel, no el 9:16 directo | Solo Feed, sin pantalla completa |
| Carrusel | 3–5 tarjetas como "hilo visual" (problema → idea → prueba → oferta) | Encaja con la lógica de hilo |
| Hashtags/URLs en el texto | No (usar CTA y URL del anuncio) | Recomendación de guías de formato |
| Comentarios | Preparar respuestas; la réplica pública es parte de la cultura | Más visibilidad de críticas |

**Fuente de creatividades**: los mejores carruseles de Instagram y los posts de texto con más respuestas en el perfil orgánico de Threads de la marca suelen ser mejores candidatos que los Reels. [HYPOTHESIS]

## 7. Plan de test de 4 semanas (si la cuenta aún permite aislar placements)

1. **Semana 0**: preparar 3 conceptos en 4:5 con copy conversacional + 1 carrusel; definir KPI de negocio (CPA, coste por lead cualificado) y KPI de atención (CTR de enlace, tiempo en web).
2. **Semanas 1–2**: ad set A con Advantage+ placements (incluye Threads) vs ad set B igual pero sin Threads (si la exclusión está disponible en tu objetivo; si no, usar una cuenta de test con Placement Controls de cuenta). Mismo presupuesto.
3. **Semanas 3–4**: mantener y leer: diferencia de CPA total entre A y B (no solo el CPA del placement Threads en el breakdown).
4. **Decisión**: si A ≤ B en CPA con calidad igual, dejar Threads; si A empeora de forma consistente, aplicar value rule a la baja (si Threads es elegible) o excluir a nivel cuenta.

[HYPOTHESIS] (diseño propio; Meta no publica un protocolo para Threads). Con la retirada de exclusiones en ad set (ver `02-…`) este test será cada vez más difícil en Sales/Leads; hazlo mientras puedas o mediante cuentas separadas.

## Implicaciones operativas

- Por defecto, dejar Threads dentro de Advantage+ placements en campañas de conversión y vigilar el breakdown mensual.
- Crear una variante 4:5 con más texto y tono conversacional para que Threads no reciba un Reel recortado.
- Clientes sin Instagram (B2B, medios): ahora pueden probar Threads con identidad propia.
- No vender a clientes "CPM un 40 % más barato": no hay datos verificados.

## Errores frecuentes

- Pensar que Threads es una compra separada con su propia segmentación.
- Usar creatividades verticales 9:16 sin adaptar (se recortan/centran).
- Ignorar los comentarios de los anuncios de Threads.
- Concluir que Threads "funciona" porque el CPM es bajo, sin mirar conversiones.

## Preguntas abiertas

- ¿Habrá lead forms nativos o anuncios de mensaje en Threads?
- Demografía y rendimiento por vertical: sin datos de Meta.
- ¿Ad load creciente en 2026–2027 hará subir el CPM? Probable, sin datos.
- Comprobar si `threads_stream` sigue requiriendo IG Feed tras el desacople de identidad de sep-2026.

## Fuentes clave

- [Ads on Threads: One Year In](https://www.facebook.com/business/news/ads-on-threads-one-year-in) — 2026-01-21 — meta-oficial
- [Threads rolls out ads to all users worldwide](https://techcrunch.com/2026/01/21/threads-rolls-out-ads-to-all-users-worldwide) — 2026-01-21 — prensa
- [Meta announces global expansion of Threads ads](https://www.socialmediatoday.com/news/meta-announces-global-expansion-of-threads-ads/810151/) — 2026-01-21 — prensa
- [Threads advertisers will no longer need an Instagram account](https://www.socialmediatoday.com/news/threads-advertisers-will-no-longer-need-an-instagram-account/830967/) — 2026-09-21 — prensa
- [Meta at IAB NewFronts 2025](https://www.facebook.com/business/news/meta-at-iab-newfronts-2025) — 2025-05-08 — meta-oficial
- [Placement targeting reference](https://developers.facebook.com/docs/marketing-api/audiences/reference/placement-targeting) — vigente — meta-developers
- [Threads Ads in 2026](https://postory.io/blog/meta-threads-ads) — 2026 — vendor
- [Incisive Growth: Threads ads 2026](https://incisivegrowth.com/blogs/should-you-be-running-ads-on-threads-yet-here-is-what-just-changed/) — 2026 — agencia (afirmaciones no verificadas)
