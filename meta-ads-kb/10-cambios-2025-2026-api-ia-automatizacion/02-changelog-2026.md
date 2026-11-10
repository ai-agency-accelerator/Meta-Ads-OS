# Changelog conceptual Meta Ads 2026 (enero → 9 de noviembre, + calendario)

> Última verificación: 2026-11-09 (revisión de octubre–noviembre, bloque B21; la anterior, 2026-10-15) · Autor: A10
> (agente), ampliado por B21 · Ámbito: cambios de 2026 en Ads Manager, Advantage+, audiencias,
> placements, IA creativa, atribución, reporting, señales, mensajería, Marketing API, políticas y UE.
> Fuentes: `fuentes/ledger-10-cambios-api-ia.md` (IDs `S10-###`). Convención de confirmación igual que en `01-changelog-2025.md`.

## TL;DR

- **La atribución cambió de definición el 3-mar-2026**: click-through = solo link clicks; el resto de interacciones
  (likes, guardados, compartidos, vídeo ≥5 s) pasa a **engage-through (1 día)**. Las conversiones "por clic" reportadas
  bajan sin que cambie el negocio. Antes, el 12-ene, desaparecieron 7d/28d view de la API. **[OFFICIAL META]** (S10-015, S10-001)
- **Meta abrió su sistema de anuncios a agentes de IA externos**: Meta Ads AI Connectors (MCP oficial en
  `mcp.facebook.com/ads` + Ads CLI, beta abierta 29-abr), abierto a cualquier app el 16-jul con "reglas de servidor MCP";
  desde Ad Week (6-oct) el trabajo de agentes llega como **borrador** que requiere aprobación. **[OFFICIAL META]** (S10-013, S10-014)
- **El asistente de IA dentro de Ads Manager (Meta AI business assistant) está desplegado para todos** (~abril) pero sus
  **acciones agénticas** (crear campañas, cambiar targeting/presupuesto por chat) siguen "coming soon"/en test a 15-oct.
  **[OFFICIAL META]** (S10-019, S10-014)
- **La creatividad generativa pasó a defaults**: vídeo desde estáticos (GA, 6-oct), imagen desde vídeo, reescritura de
  texto dentro de imágenes activada por defecto (~27-jul, observado), Muse Image anunciado (7-jul) pero no confirmado en
  cuentas. 9 M de pymes usan alguna herramienta creativa IA (Q2). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Se sigue recortando el control manual**: fin de placements manuales a nivel ad set en Sales, Leads y App
  promotion (aviso 20-ago; documentado en Help Center ~12-oct, rollout gradual; quedan exclusiones a nivel cuenta por
  objetivo y value rules; **Engagement no se ve afectado**, corrección 2026-11-09, S10-107), Explore feed y Messenger Stories eliminados en API v26, `advantage_audience` explícito
  obligatorio en categorías especiales. A cambio: value rules, audience labels, exclusion-only audiences, Customer
  Lifecycle Strategy. **[OFFICIAL META]** / **[EMPIRICAL]**
- **API**: ASC/AAC muertos en todas las versiones (19-may); v25 (18-feb) y v26 (29-jul); **el 27-oct-2026** la mayoría de
  retiradas de v26 se aplican a **todas** las versiones (incluidas llamadas sin versión). Marketing API v24 expira el
  **10-nov-2026** (corrección 2026-11-09: antes decía "expiró el 6-oct"; S10-100). **v27.0 el 4-nov-2026**: expansión de
  dispositivos por defecto en Ventas, `lookalike_spec` sin ubicación, product showcase por defecto, OTP en formularios.
  **[OFFICIAL META]** (S10-003, S10-004, S10-006, S10-099)
- **Coste**: location fees del 2–5% en UK, FR, IT, ES, AT, TR desde 1-jul; WhatsApp cobra service messages desde 1-oct
  (1.000 gratis por número y mes) y el Business Agent desde 1-ago ($2/1M tokens), también dentro de la ventana gratuita
  de CTWA, que ahora dura hasta 7 días; precio medio por anuncio +14 % en Q3. **[OFFICIAL META]** (S10-053, S10-118, S10-117)
- **Octubre–noviembre: más control y lectura a nivel de creativo** (audiencia por creativo, 19-oct; desglose por asset,
  27-oct) y **más defaults de Meta** (navegación por productos en anuncios existentes ~28-oct, product showcase en v27,
  medición en el dispositivo desde el 12-nov, ofertas detectadas en la web). Las condiciones comerciales con términos de
  IA quedaron **suspendidas** antes de entrar en vigor. **[OFFICIAL META]** + **[EMPIRICAL]** (S10-104, S10-106, S10-105,
  S10-113)
- **UE**: nueva elección "personalizados vs menos personalizados" desde enero; retirada del control "off-Meta activity"
  fuera de la UE (jun/jul); Status/Channels ads llegando a la UE (anunciado mar-2026). **[OFFICIAL META]**/prensa.
- **No existe** (a 15-oct-2026) publicidad dentro de las respuestas de Meta AI ni un "modo totalmente automático" que cree
  campañas de principio a fin desde imagen + presupuesto. Lo que hay: Advantage+ end-to-end, asistente con recomendaciones
  y tests de checkout en conversación. **[STRONG INFERENCE]** (ausencia de anuncio oficial; S10-014, S10-020)

---

## Enero 2026

- **6-ene · Restricciones de v24 se extienden a todas las versiones de API**: audiencias/conversiones marcadas (salud,
  finanzas) no se pueden actualizar ni usar; validación de `lookalike_spec`; consolidación de intereses. OFICIAL (S10-009).
- **12-ene · 7d_view y 28d_view dejan de devolver datos en Ads Insights API** (todas las versiones); unique/hourly
  limitados a 13 meses, frequency a 6 meses; breakdowns MMM solo async. OFICIAL (S10-001). Impacto: dashboards (Looker,
  Sheets, Supermetrics…) con esas columnas muestran vacío; comparativas históricas rotas. Invalida: reportar "7d click
  + 1d view" vs "28d click + 1d view" como en 2023-24 (la ventana de **28d click** solo queda en comparación, no para
  optimizar). **[OFFICIAL META]** + S10-029
- **15-ene · Ad sets con intereses consolidados/retirados dejan de entregar** si no se actualizaron. OFICIAL (S10-009).
- **15-ene · WhatsApp Business API: entra en vigor la prohibición de chatbots de IA de propósito general** (con
  posterior excepción UE por 12 meses y tarifa, mar-2026). OFICIAL/prensa (S10-057).
- **ene · UE: nuevos flujos de elección LPA** para todos los usuarios (ad-supported → personalizados vs menos
  personalizados, además de suscripción sin anuncios). Recordatorio no descartable previsto para ene-2027. OFICIAL/prensa (S10-036, S10-054).
- **21-ene · Threads ads a todos los usuarios del mundo** (despliegue gradual desde la semana del 26-ene, incluido UE,
  UK y Brasil según Q4-2025). Threads incluido por defecto en Advantage+ placements. OFICIAL (S10-048, S10-018).
- **28-ene · Earnings Q4-2025**: incremental attribution con +24% conversiones incrementales vs modelo estándar y run-rate
  multimillonario; vídeo generativo $10B run-rate; Meta AI business assistant en test desde Q4; nuevos cambios LPA
  acordados con la Comisión para desplegar en Q1. OFICIAL (S10-018).
- **~ene · "Apply Website highlights"** y breakdown de **conversion count** en Ads Manager. OBSERVADO (agregadores).

## Febrero 2026

- **13-feb · Blog de deprecación ASC/AAC** y **18-feb · Marketing/Graph API v25.0**: ASC/AAC no se pueden crear ni
  actualizar desde v25 y en **todas** las versiones antes del **19-may**; v26 pausará los ASC/AAC restantes; las campañas
  con ECBC siguen editables hasta v26 y deben duplicarse (IDs nuevos). También: error fields en informes async;
  `metadata=1` ignorado; aviso de retirada (jun-2026) de métricas orgánicas de alcance/impresiones → "media views".
  OFICIAL (S10-003).
- **16-feb · WhatsApp: política de precios para AI Providers** (actualizada 12-may). OFICIAL (S10-026).
- **17-feb · App ads en Threads** (APP_INSTALLS, app events). OFICIAL (S10-002).
- **19-feb · Expira Marketing API v22.0.** OFICIAL (S10-007).
- **~21-feb · Manus aparece en Ads Manager** (menú Tools) y una opción de IA para construir informes e investigar
  audiencias. OBSERVADO (S10-062, S10-079).
- **~feb · WhatsApp Status/Channels ads y suscripciones se despliegan a nivel mundial** (fuera de la UE). Prensa (S10-056).
- **~feb · Ad sequencing en campañas de subasta** (antes solo reserva; Awareness/ThruPlay con frecuencia objetivo).
  OBSERVADO (S10-079).

## Marzo 2026

- **3-mar · Cambio de definición de atribución** (web e in-store): click-through solo con **link clicks**; shares, saves,
  likes y otros clics no-link → **engage-through** (renombre ampliado de engaged-view); engaged-view de vídeo 10 s → 5 s
  (Meta cita que el 46% de conversiones de compra online en Reels ocurren en los 2 primeros segundos de atención).
  Rollout desde finales de marzo; sin cambio de facturación; alianzas con Northbeam y Triple Whale. OFICIAL (S10-015).
  Defaults resultantes: **7d click + 1d engage-through + 1d view** (S10-029). Impacto: menos conversiones "click"
  reportadas, más alineación con GA4; los modelos de MTA/MMM deben re-baselinarse en marzo-abril. Invalida: comparar
  CPA de Q1 vs Q2 2026 sin ajustar por el cambio.
- **5-mar · WhatsApp admite chatbots IA de terceros en Europa durante 12 meses con tarifa por mensaje** (respuesta al
  procedimiento de la Comisión). Prensa (S10-057).
- **6-mar · Meta comunica a la Comisión que Status y Channels ads llegarán a la UE "en las próximas semanas".** Doc DMA (S10-036).
- **10-mar · Anuncio de "location fees"** para cubrir impuestos a servicios digitales: UK 2%; Francia, Italia, España 3%;
  Austria y Turquía 5%; según **ubicación de la audiencia**, no del anunciante; imagen y vídeo incl. CTWA. Efectivo 1-jul.
  OFICIAL (Help Center citado por S10-045) + prensa (S10-053). Impacto: CPM efectivo +2–5% en esos mercados; el importe
  facturado no cuadra con "Amount spent" de Ads Manager. **[OFFICIAL META]**
- **13-mar · Nielsen DMA → Comscore Markets** (aviso: automoción deja de entregar con `dma_codes` el 22-jun; breakdown
  `dma` retirado). OFICIAL (S10-045, S10-002).
- **18-mar · Conector Manus ↔ Ads Manager en beta (solo lectura)**: informes y análisis en lenguaje natural. OFICIAL (S10-062).
- **24–26-mar · Shoptalk / NewFronts**: Reels trending ads con nuevas categorías, rediseño del Partnership Ads Hub, hasta
  30 productos etiquetables en Reels, affiliate partnerships en Facebook. OFICIAL (S10-045).
- **25-mar · Threads**: moderación de respuestas a anuncios (ver/ocultar/responder) y app ads globales vía API. OFICIAL (S10-002).
- **30-mar · Partnership ads**: permisos a nivel cuenta filtrables por creador y códigos de anuncio generables por API. OFICIAL (S10-002).
- **31-mar · Webhooks mTLS firmados por la nueva CA de Meta** (servidores que no la confíen dejan de recibir webhooks,
  p. ej. leads). OFICIAL (S10-003).
- **~mar · Ads Manager**: se retira **Flexible format** de Ad setup (sustituido por anuncios multi-media); Collection pasa
  a "Format display options"; Facebook Feed incluye la pestaña Friends; Opportunity Score "Apply via API" a 14 tipos de
  recomendación; filtros de custom audience por frecuencia ("al menos X veces"). OFICIAL/Help Center vía S10-045.
- **~mar · Picos de CPM del 15–40%** reportados por anunciantes a principios de marzo. OBSERVADO, sin confirmación ni causa
  oficial. **[HYPOTHESIS]** cualquier explicación causal.

## Abril 2026

- **8-abr · Plantilla oficial del Meta Pixel para Google Tag Manager.** OFICIAL (S10-044).
- **15-abr · Pixel enriquecido con IA** (extrae nombre, precio, disponibilidad de la página; activo tras aviso de 30 días,
  desactivable en Events Manager) y **Conversions API "Meta-enabled" de un clic** (alojada por Meta, solo web, botón
  "Activate Conversions API"). Claim de Meta: −17,8% coste por resultado con CAPI web. OFICIAL/prensa (S10-063).
  Impacto: el umbral técnico para tener CAPI baja a cero; no sustituye a una CAPI server-side propia con datos de CRM.
- **21-abr · Threads ads desde cuentas respaldadas por Página y promoción de posts existentes de FB/IG como Threads ads.** OFICIAL (S10-002).
- **~24-abr · Meta AI business assistant para todos los anunciantes y agencias** (Ads Manager, Business Suite, Business
  Support Home): recomendaciones, resolución de incidencias de cuenta (+20% tasa de resolución), límites de gasto, pagos.
  OFICIAL (S10-019, S10-064).
- **28-abr · Política de desarrolladores sobre transparencia en la compra de anuncios** (obligación de divulgar gasto al
  anunciante final desde el 3-feb-2027). OFICIAL (S10-044). Relevante para agencias/reselling.
- **29-abr · Meta Ads AI Connectors (beta abierta)**: MCP server oficial y Ads CLI; reporting, gestión de campañas,
  catálogos, diagnóstico de señales. OFICIAL (S10-013, S10-019).
- **29-abr · Earnings Q1-2026**: impresiones +19%, precio por anuncio +12%; Lattice+GEM >6% conv. en LPV; Adaptive Ranking
  a conversiones offsite +1,6%; >8 M anunciantes con genAI; vídeo generativo >3% más conversión en tests; Business AIs
  10 M conversaciones/semana; value optimization $20B run-rate; partnership ads $10B run-rate; Status ads vistos por
  "cientos de millones" a diario. OFICIAL (S10-019).
- **30-abr · `audience_labels` en custom audiences** (p. ej. HIGH_VALUE_CUSTOMERS, QUALIFIED_LEADS). OFICIAL (S10-002).
  Base de Customer Lifecycle y de value rules por etiqueta.

## Mayo 2026

- **4-may · Marketing API Access Tier** (antes "Ads Management Standard Access"): Limited/Full; auto-aprobación con 500
  llamadas en 15 días (antes 1.500) y sin vídeo de screen recording. OFICIAL (S10-006, S10-011).
- **4-may · `lift_estimate` de recomendaciones** incorpora nueva fuente de datos. OFICIAL (S10-002).
- **8-may · Anuncio: breakdowns `impression_device`, hourly y `frequency_value` pasan a opt-in** (efectivo 6-ago). OFICIAL (S10-002).
- **18-may · Audiencias de compra web/app: retención máxima 180 → 730 días** (actualización automática salvo opt-out
  previo). OBSERVADO por aviso in-product (S10-078). Doc dev aún citaba 365/180 en julio → **[CONTESTED]** documentalmente.
- **18-may · Listas de bloqueo de brand safety ampliadas a Threads Feed; sección "Ads" en la status page de Meta.** OFICIAL (S10-044).
- **19-may · ASC/AAC: fin de creación/edición en todas las versiones de API.** OFICIAL (S10-003).
- **21-may · Graph API v19 eliminada.** OFICIAL (S10-005).
- **27-may · Meta One** (suscripciones de consumo; planes business en septiembre). Prensa (S10-070).
- **~may · Auto-añadir productos de la web al catálogo** (opt-out en Commerce Manager). OBSERVADO (S10-078).

## Junio 2026

- **1-jun · IG Audio Swap por API** (sustituir música con copyright en Reels por audio libre de Sound Collection). OFICIAL (S10-002).
- **~1-jun · Detección automática (C2PA) de anuncios hechos con IA de terceros y etiquetado** ("AI info"). Prensa/agregador
  (S10-039); base oficial: política de transparencia de IA. **[STRONG INFERENCE]** fecha exacta.
- **3-jun · Meta Conversations (Londres): Meta Business Agent global** en WhatsApp, Messenger e Instagram (más de 1 M de
  negocios) y anuncio de **Business Agent Platform** (enterprise; Shopify/Zendesk). OFICIAL/prensa (S10-058, S10-020).
- **~8-jun · Anuncios post-view en Reels** (tras Reels orgánicos >60 s) abiertos globalmente dentro de placements
  automáticos. Prensa/agregador (S10-039).
- **9-jun · Se retira el control "Your activity off Meta technologies"** y se amplía "Activity from other businesses"
  (Meta usará también esos datos para Feed y respuestas de Meta AI; no recoge datos nuevos). Rollout EE. UU. desde julio;
  UE tratada aparte. OFICIAL (S10-027). Impacto probable: más usuarios "emparejables" para retargeting/lookalikes fuera de
  la UE. **[HYPOTHESIS]** la magnitud.
- **9-jun · Expira Marketing API v23.0.** OFICIAL (S10-006).
- **11-jun · Creator Marketplace API ampliada** (filtros de seguidores, estado de EE. UU., recomendaciones, búsqueda por
  audiencia guardada/lookalike). OFICIAL (S10-002).
- **12-jun · Incidente grave** (Ads Manager ~4 h caído). OFICIAL status page (S10-039).
- **~15-jun · Métricas orgánicas legacy de alcance/impresiones dejan de actualizarse** (→ Media Views / Viewers). OFICIAL (S10-003).
- **16–17-jun · Live Video Ads en Instagram y escalado global en Facebook; tarjetas virtuales de un solo uso (Visa,
  Mastercard) en checkout.** OFICIAL/prensa (S10-080).
- **22-jun · Nielsen DMA retirado; `breakdowns=dma` → `comscore_market`.** OFICIAL (S10-002). Ojo: el "DMA deprecation"
  de algunos blogs es esto, **no** la Digital Markets Act (S10-080).
- **23-jun · Cannes Lions 2026**: suite creativa end-to-end en Ads Manager (revisar qué funciona → generar → testear),
  **Brand Memory** (aprende identidad y tono de anuncios previos; test limitado), integración con **WPP Open**, traducción
  +5 idiomas en texto sobre imagen y +11 en voiceover, Creative Approval Flow en test, Creator Marketing Hub (lanzado
  15-sep). Meta cita $4,13 de ingresos por $1 de publicidad (estudio encargado por Meta). OFICIAL/prensa (S10-052).
- **~23-jun · Reserva de citas ("Book time") dentro de Instant Forms** (Calendly, HighLevel; app móvil de Facebook).
  OBSERVADO (Loomer vía S10-039). Global "esperado en octubre" — sin confirmar.
- **28-jun · Advantage+ creative por API: Image Animation, Video Filter (mejora/HDR), Video Uncrop**, opt-in/out por
  creatividad. OFICIAL (S10-002).
- **~30-jun · Developer Tools MCP** (solo lectura de docs/herramientas para desarrolladores). OFICIAL/prensa (S10-035).

## Julio 2026

- **1-jul · Location fees facturados** (línea aparte, fuera del presupuesto). OFICIAL (S10-053).
- **1-jul · Cambios de tarifas WhatsApp** (marketing sube en IT, ES, UK; BRL en Brasil). OFICIAL (S10-023).
- **7-jul · Muse Image** (primer modelo de imagen de Meta Superintelligence Labs) anunciado para Advantage+ creative:
  fondos, variaciones lifestyle, estáticos desde vídeo; "en las próximas semanas". OFICIAL/prensa (S10-060). **No
  confirmado en cuentas a 30-sep** (S10-041). Estado a 15-oct: **sin confirmar**.
- **~9-jul · Lead Capture AI agent para Instant Forms** documentado. OFICIAL (S10-044). Poco testado públicamente.
- **~10-jul · "Push delivery to this ad"** (forzar ~20–30% del presupuesto del ad set a un anuncio). OBSERVADO (Loomer
  vía S10-039, S10-044). Útil para dar tracción a una creatividad nueva sin sacarla a otro ad set.
- **16-jul · Ads MCP abierto a cualquier aplicación** (app propia, caso de uso "Create and manage ads with ads MCP server";
  agencias necesitan Advanced Access a `ads_mcp_management` con App Review) y **reglas de servidor MCP** para que el
  admin del portfolio permita/bloquee acciones de agentes (presupuesto, creación, catálogo…). OFICIAL (S10-013, S10-035).
- **~16-jul · Audiencias reorganizadas por labels** (Customer / Engaged); las labels condicionan value rules. OBSERVADO (S10-040).
- **~20-jul · ROAS goal seleccionable con "maximizar número de conversiones"** (antes solo con valor). OBSERVADO (S10-033).
- **~21-jul · Webhooks a nivel cuenta publicitaria** (estado de entrega `effective_status`; sustituto del polling). OFICIAL docs (S10-044).
- **~27-jul · Advantage+ creative reescribe el titular dentro de imágenes subidas** (hasta 8 variantes preseleccionadas;
  controles en Branding y por creatividad). OBSERVADO (Loomer 28-jul y agencias; S10-040). **[EMPIRICAL]** riesgo de marca.
- **27-jul · Holiday Insights Center** (guía Q4; encuesta 14.473 personas). OFICIAL (S10-040).
- **29-jul · Graph/Marketing API v26.0** (ver 06-marketing-api). Bloqueo Commerce Order Management API (47 endpoints),
  WhatsApp Status ads ampliados (optimización offsite y LPV, carrusel 10 tarjetas), `advantage_audience` explícito en
  vivienda/empleo/finanzas, Explore feed eliminado, Messenger Stories eliminado, poll ads deprecados, Shop ads por defecto
  WEBSITE_AND_SHOP. OFICIAL (S10-004).
- **29-jul · Earnings Q2-2026**: **Meta Generative Recommender** (LLMs en retrieval, "cambio de paradigma"); +8,3% clics y
  +15,7% conversiones en Facebook por modelos de comprensión de usuario + GEM; Advantage+ >$75B; 9 M pymes con IA
  creativa; image generation ×2 QoQ e imágenes desde vídeo; Business Agent >1 M negocios/semana; Threads ads globales
  completados. OFICIAL (S10-020).

## Agosto 2026

- **1-ago · Mensajes del Meta Business Agent facturados**: $2 por 1 M de tokens (~4–5 céntimos por mensaje). OFICIAL (S10-024).
- **~4-ago · Financiación de cuentas con USDC** (solo Argentina y Colombia según Help Center). OFICIAL parcial (S10-041).
- **6-ago · Breakdowns device/hourly/frequency solo para cuentas con opt-in** (sin opt-in devuelven 200 vacío). OFICIAL (S10-002).
  Impacto: informes de frecuencia y dayparting rotos silenciosamente → activar "Additional Breakdowns".
- **~10-ago · Exclusion-only custom audiences** (tipo de audiencia solo para excluir; no convertible). OFICIAL vía MediaPost (S10-041).
- **11-ago · Panel "Ads MCP Server" en Business Settings > Integrations** (Allowed/Blocked por acción y cuenta). Observado con
  **7/7 acciones de escritura permitidas por defecto**. Feature OFICIAL; default OBSERVADO (S10-084, S10-041).
- **~13-ago · Marketing messages de WhatsApp en Marketing API.** Reportado como OCC (S10-041). Sin verificar directamente.
- **20-ago · Aviso in-product: "Excluding placements, platforms, devices and operating systems will no longer be available
  for your ad sets."** Test en Sales/Leads, sin fecha; sustituto = placement value rules (bajar hasta −90%, nunca apagar) y
  Placement Controls a nivel cuenta. OBSERVADO, sin anuncio oficial en agosto (S10-030). **Actualización 12-oct:** Meta
  lo documenta en el Help Center (ver entrada de octubre).
- **~26-ago · Creative Diversity rating (Low/Medium/High)** por ad set, "estimado y en desarrollo" según Help Center. OBSERVADO (S10-041).
- **26/27-ago · Acuerdo con 52 fiscales generales sobre adolescentes** (límite diario por defecto, bloqueo 0–6 h; fecha
  límite 27-feb-2027). OFICIAL (S10-041). Impacto indirecto en inventario 13–17.
- **~27-ago · Messenger Stories retirado como placement** en Ads Manager (API universal el 27-oct). OFICIAL/agregador (S10-004, S10-043).
- **28-ago · Verificación obligatoria para anunciantes de servicios financieros que segmentan Polonia.** OFICIAL (S10-041).

## Septiembre 2026

- **~1-sep · Lookalikes creados por API ignoran el campo país** y entregan según la ubicación del ad set. Reportado
  (Loomer/agregador) como cambio de v26; **no localizado** en el changelog v26 consultado → sin confirmar (S10-042).
- **~1-sep · "Automatic Events" en ajustes del dataset** (Events Manager). OBSERVADO (S10-042).
- **4-sep · Ads MCP acepta tokens de system user con rol Employee** (no Admin). OFICIAL docs (S10-042).
- **8-sep · Muse (agente personal de Meta) en EE. UU.**; compras con checkout (Link by Stripe, Shop Pay, PayPal); Zuckerberg
  confirma pequeña comisión por transacción (Connect, 23-sep); Amazon lo bloquea. OFICIAL/prensa (S10-061). No es un
  producto publicitario, pero abre la vía de "comercio agéntico" (ver 05-business-ai).
- **15-sep · Meta One para negocios** (Essential $14,99 → Max $499 por perfil/mes; soporte humano solo en tiers altos).
  OFICIAL según agregadores (S10-042, S10-070). **[CONTESTED]** asignación de casos de soporte.
- **15-sep · Creator Marketing Hub global** (une Creator Marketplace y Partnership Ads Hub); partnership ads llegarán al MCP. OFICIAL (S10-042).
- **21–22-sep · Threads ads sin necesidad de perfil de Instagram; permisos propios; etiqueta "Ad"**. OFICIAL Help Center, gradual (S10-042).
- **~21-sep · Test de landing pages generadas por IA** desde tu web ("test new AI generation features"). OBSERVADO (Loomer, S10-042).
- **24-sep · Graph API v20 eliminada.** OFICIAL (S10-005).
- **~29-sep · Live video ads en Instagram en disponibilidad general.** Anunciado (S10-043); confirmar en cuenta.

## Octubre 2026 (hasta el 15)

- **1-oct · WhatsApp cobra los service messages** (respuestas no-plantilla de humanos o IA de terceros) a tarifa
  utility/auth, sin tramos de volumen; siguen gratis dentro de la ventana FEP de 72 h de anuncios CTWA. OFICIAL (S10-024).
  Nota: la página general de precios aún no lo refleja (inconsistencia documental, S10-023). La cifra de "1.000 mensajes
  gratis al mes" y la "ventana FEP de 7 días" que citan algunos blogs **no aparecen** en la doc oficial consultada.
  **[OUTDATED] desde el 2026-11-09**: la página oficial de precios, releída, dice que la FEP de CTWA puede durar
  **hasta 7 días** (desde el 28-sep según BSPs) y que hay **1.000 service messages gratis por número y mes**; los
  mensajes del Business Agent se cobran también dentro de la FEP. La subpágina de mensajes sin plantilla sigue sin citar
  los 1.000 (S10-118, S10-119, S10-121).
- **6-oct · Advertising Week New York** (S10-014, S10-046):
  - GA: **vídeo desde estáticos** en Advantage+ creative; **Customer Lifecycle Strategy** para todos (adquisición →
    Meta recomienda excluir clientes existentes; test de exclusión por una sola Audience Label).
  - Rolling out: **Ads Creative Studio** (qué creatividad funciona y por qué + generación/edición de vídeo: hooks, audio,
    duración, textos, subtítulos, cierres).
  - Beta: vídeo de producto desde imágenes de catálogo.
  - Test: tareas programadas y alertas del asistente; importar estrategia/voz de marca; checkout de Shopify dentro de
    Business Agent en Messenger.
  - Coming soon: **acciones agénticas del asistente** (crear campañas, generar imagen/texto, cambiar targeting y
    presupuesto con preview y aprobación); **audience discovery en Detailed Targeting** con lenguaje natural (fin de 2026);
    checkout directo en Meta AI (Adyen, PayPal, Shopify, Stripe; "este otoño").
  - MCP ampliado: subida de creatividades, previews, tendencias; **todo lo que hace un agente llega como borrador** que
    requiere aprobación explícita; 10 partners (AdManage.ai, Birch, Databricks, Kochava, Perplexity, Snowflake, Triple Whale…).
- **6-oct · Personal Agent Protocol (Meta + Sierra)**: estándar abierto para que agentes personales se autentiquen con
  negocios (OAuth, permisos read/write). Prensa (S10-061 contexto); spec v0.1 en borrador. No es producto publicitario.
- **6-oct · Expira Marketing API v24.0** (llamadas a endpoints no afectados se auto-actualizan). OFICIAL (S10-006, S10-010).
  **[OUTDATED] desde el 2026-11-09**: la tabla oficial de versiones da el **10-nov-2026** como fin de la v24 (S10-100).
- **~6-oct · EE. UU.: periodo de restricción de anuncios políticos/sociales/electorales del 27-oct al 3-nov-2026**
  (midterms): no se pueden lanzar anuncios nuevos; los que ya sirvieron impresiones siguen con edición limitada;
  autorización necesaria antes del 13-oct. OFICIAL vía Social Media Today/Developers Blog (S10-095).
- **8-oct · Meta deja de aceptar anuncios de ByteDance y de terceros que enlazan a TikTok** (u otras propiedades de
  ByteDance) en **EE. UU., Canadá, Egipto, Indonesia, Japón, Tailandia y Vietnam**, con efecto inmediato. Confirmado por
  portavoz de Meta; **sin página de política publicada** → alcance provisional (S10-096). Impacto: campañas de creadores o
  apps que dirigían a perfiles de TikTok quedan bloqueadas en esos mercados.
- **9-oct · Se retira "Access Verification" para apps Tech Provider.** OFICIAL (Developers Blog vía S10-097).
- **~8-oct · Aviso de nuevas Commercial Terms / Self-Serve Ad Terms, efectivas el 30-oct-2026**; incorporan las Ad Creative
  Generative AI Terms. OFICIAL la fecha (S10-069). Detalles ("Meta puede hacer tests de entrega/creatividad sin aviso",
  "el anunciante responde del contenido IA aunque lo genere Meta", prohibición de quitar marcas de agua) **solo en
  terceros** → **[STRONG INFERENCE]** hasta leer el texto final. **Actualización 2026-11-09**: no llegaron a entrar en
  vigor; se aplazaron al 20-nov y luego se suspendieron hasta nuevo aviso (ver noviembre; S10-113).
- **~12-oct · Help Center oficial "What's new in placement settings in Meta Ads Manager"**: en **Sales, Leads,
  Engagement y App promotion** ya no se eligen placements manualmente a nivel de ad set; **Awareness y Traffic** los
  conservan. **Corrección 2026-11-09**: la página releída en inglés y en español dice que solo Leads, App promotion y
  Sales pierden la elección manual y que Awareness, Traffic **y Engagement** no se ven afectados; el "−10 %" se ha
  suavizado a "puede ayudarte a reducir el coste por resultado". Meta cambió la página sin aviso (S10-107). Alternativas documentadas: personalización de assets por placement (hasta 10 imágenes/vídeos en un anuncio
  multi-media; sin asset compatible no se entrega en ese placement), **placement value rules**, y **exclusiones de
  placements a nivel cuenta por objetivo** (nuevo) además de los controles de cuenta para Audience Network, Marketplace
  y columna derecha. Rollout gradual. Meta cita −10% coste por resultado medio con Advantage+ placements (experimento no
  descrito). OFICIAL (S10-093, S10-094). No menciona exclusiones de plataforma/dispositivo/SO → **[CONTESTED]** ese punto.
  Invalida: excluir placements en el ad set en objetivos de conversión (Ventas, Clientes potenciales, App; en
  Engagement sigue siendo posible, corrección 2026-11-09).
- **6-oct · Customer Lifecycle Strategy disponible para todos** (anuncio de Meta en Advertising Week; algunos medios dicen 7-oct), toggle a nivel ad set "Get conversions from all audiences" / "Acquire new customers". El Help Center (1740191093676743) no define ventana; en la UI se observa una exclusión automática "Customers from your conversion data (730 days)" con opciones 730/180/90/60/30 días (Loomer, 13-oct-2026). La "ventana de 180 días" que citan agregadores y CTC no tiene fuente de Meta. [OFFICIAL META] (GA y toggle) / [EMPIRICAL] (730 d por defecto)
- **13-oct · Post de ingeniería GEM 2026**: modelo central único, +18,9% conversiones y +12% CTR en el último año
  (agregado de Meta). OFICIAL (S10-022).
- **~14-oct · Aviso a anunciantes: "product browsing" se activará por defecto en anuncios existentes desde el 28-oct**
  salvo opt-out. El aviso y el enlace de opt-out existen; no hay Help Center/changelog/newsroom público a 15-oct y la
  fecha no está confirmada públicamente. PARCIALMENTE CONFIRMADO (S10-097). **[STRONG INFERENCE]** que llegue en esa fecha.
- **15-oct · WhatsApp Embedded Signup v2/v3 retirados** (v4). OFICIAL (S10-044, S10-097).
- **15-oct · Instagram Live video ads siguen marcados como beta** en la página de live shopping pese al objetivo de GA del
  29-sep. OFICIAL/estado incierto (S10-097).
- **15-oct · FTC (EE. UU.) abre consulta pública sobre herramientas publicitarias de plataformas y estafas por suplantación**
  (comentarios hasta 30-nov). Gobierno, no Meta (S10-097). Señal regulatoria a vigilar.
- Status page de Meta: **sin incidentes de Ads Manager/entrega entre el 1 y el 15-oct-2026** (S10-097).

> **Añadido el 2026-11-09 (antes del 16-oct, no recogido en la revisión anterior):**
> - **13-ago · Mensajes de marketing de WhatsApp en la Marketing API** (cambio fuera de ciclo). OFICIAL (S10-102).
> - **28-sep · FEP de CTWA de hasta 7 días** (la página oficial de precios lo dice; la fecha la dan BSPs). OFICIAL +
>   OBSERVADO (S10-118, S10-121).
> - **29-sep (act. 8-oct) · Muse para pequeñas empresas** en EE. UU. y Canadá: se conecta a cuentas publicitarias,
>   analiza el rendimiento y redacta campañas; nada se publica, envía ni gasta sin aprobación. OFICIAL (S10-123).
> - **6-oct · `ig_search`**: los anuncios de vídeo pueden salir en los resultados de búsqueda de Instagram (gradual).
>   OFICIAL (S10-102).
> - **15-oct · Brand Building Summit**: Ads Super Burst (picos de alcance de 3–24 h con exclusividad de categoría,
>   Reach Planner, GA por fases), First Impression Ads (test en EE. UU., una marca al día), Reels trending ads (15 temas;
>   exclusiones de audiencias personalizadas "más adelante este año") y Aggregated View Time (alfa). OFICIAL (S10-116).

## Octubre 2026 (desde el 16)

- **19-oct · Audiencia por creativo** ("Choose an audience for each ad creative" / "Cómo elegir una audiencia para cada
  contenido del anuncio"): dentro del mismo conjunto, cada pieza puede orientarse a una edad y un género; la edad y el
  género del conjunto se ocultan y Meta puede llegar también a personas con probabilidad de responder (orienta, no
  limita). API: `targeting_automation.creative_audience_pairing` (0/1) y `creative_audience_pairing_persona` en el
  anuncio o en el medio de `media_sourcing_spec`. OFICIAL (S10-103, S10-104). Loomer (20-oct): activado por defecto en
  Ventas si se elige *further limit*, desactivado en los demás objetivos, solo edad mínima y género. OBSERVADO (S10-109).
  Para B2B: la edad y el género rara vez son el eje; útil sobre todo para no fragmentar conjuntos.
- **21-oct · Resultados de Q3-2026**: impresiones +10 %, precio medio por anuncio +14 %; retrieval generativo en el Feed
  de Facebook (~+2 % de conversiones en los segmentos objetivo); GEM en más superficies (+1,7 % offsite, +9,6 % apps);
  Andromeda +1,4 %; el asistente de Ads Manager da ~5 % más conversiones al mismo CPA a quien lo usa, con +9 % de
  inversión, y despliega "acciones más agénticas" con aprobación; ~10 M de anunciantes usan IA generativa; vídeo
  generado +25 % trimestral; partnership ads +97 % y >15.000 M$ de run-rate; Creator Marketing Hub global con el
  asistente; Meta One >15 M de suscripciones; Muse para pequeñas empresas; Personal Agent Protocol con Sierra, Walmart,
  Stripe y Shopify. OFICIAL (S10-117). La KB esperaba Q3 el ~29-oct.
- **22-oct · Ediciones de IA no pedidas**: anunciantes retiran anuncios por retoques de IA que no habían activado
  (Adweek). OBSERVADO (S10-127). Mismo día, cambio fuera de ciclo: campo `is_pca_unified` en campañas OUTCOME_SALES
  (inmutable; Meta no define "PCA"). OFICIAL (S10-102).
- **24-oct → 5-nov · Condiciones comerciales con términos de IA**: la entrada en vigor del 30-oct se aplaza al 20-nov
  (24-oct); un tribunal noruego dicta una cautelar a petición de diez grupos de medios y Meta pausa el despliegue (28-oct);
  la CMA británica abre una investigación bajo la Competition Act 1998, Chapter II (30-oct); un tribunal de São Paulo
  suspende la cláusula (3-nov, prensa); aviso de suspensión hasta nuevo aviso (5-nov). Las condiciones vigentes siguen
  siendo las del 22-ago-2025, que ya permiten a Meta acceder, indexar y rastrear los dominios del anunciante para
  publicidad, investigación y formación. OFICIAL (S10-113, S10-114) + prensa (S10-112, S10-115).
- **26-oct · Sale iOS 27.2** (build 24B119) con el aviso ATT alternativo de la UE, obligatorio en FR, DE, IT, PL y RO, y
  re-petición anual. OBSERVADO (S10-130; la nota de Apple no se pudo leer).
- **27-oct · Desglose por asset en Ads Manager**: Breakdown → Creative → Media (cada imagen o vídeo), *Dynamic creative
  element* (variantes de texto) y *Ad delivery* (medios retirados); no cubre *Show as carousel/collection*. OFICIAL
  (S10-106) + prensa (S10-128). No es un test: el reparto lo decide el sistema.
- **~28-oct · "Añadir la navegación por productos" en anuncios existentes** salvo opt-out. La mejora figura en la lista
  oficial de Advantage+ creative (S10-108); la activación masiva en esa fecha solo consta en el aviso y en agencias.
  **[STRONG INFERENCE]**/OBSERVADO.
- **19–26-oct · Threads como ubicación por defecto en todas las campañas**: solo agregadores y agencias (S10-132).
  **[CONTESTED]**. Threads ya estaba en Advantage+ placements desde el 21-ene.

## Noviembre 2026 (hasta el 9)

- **4-nov · Graph API y Marketing API v27.0** (S10-099, S10-101):
  - expansión de dispositivos activada por defecto en conjuntos de Ventas nuevos que segmentan por `user_device` o
    `user_os` (`targeting_automation.individual_setting.device`; opt-out con `0`); a todas las versiones unos 90 días
    después (~feb-2027, fecha por confirmar);
  - `lookalike_spec` con `country` o `location_spec` se rechaza (todas las versiones a los ~90 días);
  - product showcase por defecto (`product_extensions`; opt-out con
    `degrees_of_freedom_spec.creative_features_spec.product_extensions.enroll_status=OPT_OUT`; vista previa en
    `GET /{ad-account-id}/product_extensions/catalog_suggestions_preview`);
  - `POST /{catalog-id}/batch` → `items_batch`; `meta_moment_maker_spec` → `product_type` `ADS_BURST`/`ADS_SUPER_BURST`
    en `reachfrequencypredictions`;
  - formularios: `phone_otp_verification_type` (`NOT_ENABLED`/`OTP_REQUIRED`/`OTP_OPTIONAL`; `OTP_OPTIONAL` exige un
    `ad_account_id` elegible; el legacy `is_phone_sms_verify_enabled` sigue; en formularios antiguos puede venir `null`);
  - Graph: funciones legacy (`ids`, `date_format`, `method`, `.as()`, `callback`, `asyncbatch`) cerradas a apps nuevas en
    todas las versiones y eliminadas en v28; `is_ai_generated` en posts de Página.
  OFICIAL.
- **principios de nov · `total_video_consumption_rate` deja de devolver datos**, sin reemplazo. OFICIAL (S10-101).
- **5-nov · Breakdown `pa_creator_ig_handle`** (partnership ads por creador; no se combina con otros breakdowns). OFICIAL (S10-102).
- **6–8-nov · Ofertas detectadas en la web añadidas a anuncios copiados**, incluso con las promociones desactivadas; se
  controla en Commerce Manager → Settings → Offer merchandising → "Detected offers". OBSERVADO (S10-125, S10-126).
- **6-nov · "Flexible ROAS goal" y "Performance-based budget increase" (beta)**: una sola agencia, que cita una sesión de
  Meta sin enlace (S10-124). **[HYPOTHESIS]**.
- **9-nov · Sin cambios de estado** en lo anunciado en Ad Week: audience discovery "a fin de año", checkout en Meta AI
  "este otoño" (test), Ads Creative Studio desplegándose (S10-131).
- **10-nov · Expira la Marketing API v24.0** (S10-100).
- **12-nov · "Mide las conversiones en los dispositivos de los clientes"** activado por defecto en el píxel: empareja en
  el dispositivo la visualización del anuncio y la compra con datos que el negocio ya comparte (p. ej. email) e
  información temporal del dispositivo; no está activo para personas en la UE ni en el Reino Unido; complementa píxel y
  CAPI y no cambia ventana ni modelo. OFICIAL (S10-105). Fecha (panel de Events Manager) y requisitos (web con login por
  email o teléfono; sin iframe ni píxel de imagen; solo compra): OBSERVADO (S10-110, S10-111). Si alimenta también la
  optimización: **[HYPOTHESIS]**.

---

## Calendario próximo (desde 9-nov-2026)

> Ya pasado desde la revisión del 15-oct: restricción política en EE. UU. (27-oct → 3-nov), retiradas de v26 en todas
> las versiones (27-oct), navegación por productos por defecto (~28-oct). Las condiciones del 30-oct **no** entraron en
> vigor. La API v27 llegó el 4-nov, antes de lo que se esperaba (~feb-2027).

| Fecha | Qué | Confirmación |
|---|---|---|
| **10-nov-2026** | Expira la Marketing API v24.0 | Oficial (S10-100) |
| **12-nov-2026** | Medición en el dispositivo activada por defecto (fuera de la UE y el Reino Unido) | Oficial el ajuste (S10-105); fecha según terceros (S10-110, S10-111) |
| ~~20-nov-2026~~ | Fecha aplazada de las condiciones nuevas: anulada por la suspensión | Oficial (S10-113) |
| sin fecha | Reserva de citas en Instant Forms global; HubSpot como calendario integrado | Esperado para oct-2026, **no confirmado** a 9-nov |
| sin fecha | Decisión de la CMA y conversaciones con la Comisión Europea sobre las condiciones | Oficial (S10-114) |
| fin de 2026 | Audience discovery en Detailed Targeting; exclusiones en Reels trending ads; 90% ingresos de anunciantes verificados; Muse Image en Advantage+; checkout en Meta AI | Anunciado (S10-131, S10-116) |
| 21-ene-2027 | Graph API v21 eliminada | Oficial (S10-005, S10-101) |
| ene-2027 | UE: recordatorio no descartable de elección LPA; India: WABA en INR | Oficial/doc DMA |
| 31-ene-2027 | Verificación de identidad de anunciantes en Singapur | Agregador |
| 3-feb-2027 | Divulgación obligatoria de gasto al anunciante final (política dev) | Oficial (S10-044) |
| ~feb-2027 | Expansión de dispositivos por defecto y rechazo de `lookalike_spec` con ubicación en **todas** las versiones (~90 días tras v27) | Oficial el plazo; fecha exacta por confirmar (S10-099) |
| 23-feb-2027 | Expira la Marketing API v25.0 | Oficial (S10-100) |
| 27-feb-2027 | Cambios para adolescentes (límite diario, bloqueo nocturno) | Oficial (consent judgment) |
| 20-may-2027 | Graph API v22 eliminada | Oficial (S10-101) |
| v28 (2027) | Se eliminan las funciones legacy de la Graph API | Oficial (S10-101) |

## Implicaciones operativas

- **Re-baselinar KPIs** a partir de marzo-2026 (link clicks) y de enero-2026 (sin 7d/28d view en API). Documentar en el
  informe de cliente la discontinuidad.
- **Activar opt-in de breakdowns** (device/hourly/frequency) en cada cuenta y revisar conectores.
- **Auditar defaults de Advantage+ creative** (reescritura de texto en imágenes, música, traducción, landing pages IA) en
  cada cuenta antes de Q4; registrar qué está activado y por qué. Ver 04.
- **Revisar el panel de reglas del MCP** en cada portfolio: si no se usa, bloquear escrituras; si se usa, limitar presupuesto.
- **Adaptarse a la retirada de placements manuales en ad sets** (Sales/Leads/App; Engagement no, corrección 2026-11-09): value rules por placement,
  exclusiones a nivel cuenta por objetivo solo para brand safety o problemas demostrados, y assets por placement
  (multi-media) para controlar el formato en cada superficie.
- **Actualizar integraciones a v26** antes del 27-oct (enviar siempre `advantage_audience` en categorías especiales; quitar
  Explore y Messenger Stories de arrays de placements; verificar valores guardados tras escribir).
- **WhatsApp**: recalcular coste por conversación con service messages cobrados (1.000 gratis por número y mes), FEP de
  CTWA de hasta 7 días y Business Agent por tokens incluso dentro de la FEP.
- **Marcar el 12-nov-2026** en los informes de clientes fuera de la UE y el Reino Unido (medición en el dispositivo) y
  el 26-oct en los de la UE con apps (iOS 27.2): no comparar compras atribuidas a través de esas fechas sin avisar.
- **Integraciones a v27**: enviar `targeting_automation.individual_setting.device=0` si el plan segmenta por dispositivo
  o SO en Ventas y no se quiere la expansión; quitar `country`/`location_spec` de `lookalike_spec`; mantener el opt-out
  de `product_extensions`; leer `phone_otp_verification_type` tolerando `null`.
- **Auditar anuncio a anuncio** las mejoras de Advantage+ creative (navegación por productos, animación, texto del
  medio), las "Detected offers" de Commerce Manager y la audiencia por creativo en Ventas.
- **Leer el desglose por asset** para generar hipótesis de creatividad, no para declarar ganadores.

## Errores frecuentes

- Tratar los anuncios de Ad Week/Cannes como funcionalidades disponibles: a 15-oct, las acciones agénticas del asistente,
  la audience discovery y el checkout en Meta AI **no** están en GA.
- Creer que la API "da error" al usar versiones expiradas: muchas llamadas se **auto-actualizan en silencio** a la versión
  siguiente (con header de aviso) y algunas retiradas son **silenciosas** (Messenger Stories) → validar lo guardado.
- Confundir Nielsen DMA (geografía) con la DMA europea.
- Asumir que "menos conversiones atribuidas" desde marzo = peor rendimiento.

## Preguntas abiertas

- ¿Muse Image está realmente activo en Advantage+? ¿Qué modelo hay detrás de la reescritura de texto en imágenes?
- Texto final de las condiciones del 30-oct (tests sin aviso, responsabilidad sobre contenido IA). A 9-nov están
  suspendidas y la página preview ya no existe.
- ¿Cuándo termina el rollout de la retirada de placements manuales (Sales/Leads/App) y caen también las
  exclusiones de plataforma, dispositivo y SO? (La expansión de dispositivos por defecto de la v27 apunta a que sí.)
- ¿La medición en el dispositivo alimenta la optimización o solo el reporting? ¿Llegará a eventos distintos de la compra?
- ¿Qué es "PCA" en `is_pca_unified`? ¿Existen de verdad Flexible ROAS goal y Performance-based budget increase?
- ¿Se cobra el Business Agent en Instagram y Messenger igual que en WhatsApp?
- ¿Threads es ubicación por defecto en todas las campañas desde finales de octubre?
- ¿Cuántos usuarios de la UE eligen LPA y cuánto cae el rendimiento en esos usuarios? Meta no publica cifras.

## Fuentes clave

- [Click attribution update](https://www.facebook.com/business/news/click-attribution) — 2026-03-03 — meta-oficial (S10-015)
- [Meta Ads AI Connectors](https://www.facebook.com/business/news/meta-ads-ai-connectors) — 2026-04-29 / 07-16 — meta-oficial (S10-013)
- [Advertising Week New York 2026](https://www.facebook.com/business/news/advertising-week-new-york-2026) — 2026-10-06 — meta-oficial (S10-014)
- [Graph/Marketing API v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) — 2026-07-29 — meta-developers (S10-004)
- [2026 Out-of-Cycle Changes](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) — 2026 — meta-developers (S10-002)
- [Q1 2026](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q1/META-Q1-2026-Earnings-Call-Transcript.pdf) y [Q2 2026](https://s21.q4cdn.com/399680738/files/doc_financials/2026/q2/META-Q2-2026-Earnings-Call-Transcript.pdf) — meta-investors (S10-019, S10-020)
- [Meta Is Removing Placement Controls From Ad Sets](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/) — 2026-08-20 — practitioner (S10-030)
- [WhatsApp non-template messages pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing/non-template-messages) — 2026 — meta-developers (S10-024)
- [Marketing API v27.0](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version27.0.md) y [versiones](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/versions.md) — 2026-11-04 — meta-developers (S10-099, S10-100)
- [Choose an audience for each ad creative](https://developers.facebook.com/blog/post/2026/10/19/choose-an-audience-for-each-ad-creative/) — 2026-10-19 — meta-developers (S10-103)
- [Mide las conversiones en los dispositivos de los clientes](https://www.facebook.com/business/help/4237575203200036) — Help Center — meta-oficial (S10-105)
- [What's new in placement settings](https://www.facebook.com/business/help/1546753450586085) — releído 2026-11-09 — meta-oficial (S10-107)
- [Q3 2026](https://s21.q4cdn.com/399680738/files/content_files/META-Q3-2026-Earnings-Call-Transcript.pdf) — 2026-10-21 — meta-investors (S10-117)
- [WhatsApp pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — releída 2026-11-09 — meta-developers (S10-118)
- [Condiciones de autoservicio](https://www.facebook.com/legal/self_service_ads_terms) y [CMA](https://www.gov.uk/government/news/cma-opens-investigation-into-metas-commercial-terms--2) — 2026-10-30/11-05 — meta-oficial y regulador (S10-113, S10-114)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Customer Lifecycle Strategy: la entrada decía "~11-oct… ventana 180 días" (agregador). Fecha de disponibilidad general: 6-oct-2026 (Meta for Business, Advertising Week New York 2026). El Help Center oficial no fija ventana; la UI muestra 730 días por defecto con opciones 730/180/90/60/30 (Jon Loomer, 2026-10-13, con capturas). Coherente con el área 02 (05-arquitectura, 07-audiencias).

## Correcciones de la revisión 2026-11-09

> Revisor: B21 (agente). No se borra el texto anterior: se marca con fecha. Fuentes en `fuentes/ledger-10-cambios-api-ia.md`
> (S10-099 a S10-143).

- **Placements (~12-oct)**: Engagement no pierde la elección manual de ubicaciones; solo Sales, Leads y App promotion.
  El Help Center se modificó después del 12-oct (S10-107 corrige S10-093).
- **WhatsApp (1-oct)**: la FEP de CTWA de hasta 7 días y los 1.000 service messages gratis por número y mes están en la
  página oficial de precios (S10-118). Revierte el criterio del 16-oct, que los trataba como afirmaciones de terceros.
- **Marketing API v24.0**: expira el 10-nov-2026, no el 6-oct (S10-100).
- **Condiciones del 30-oct (~8-oct)**: no entraron en vigor; suspendidas hasta nuevo aviso (S10-113).
- **Q3**: los resultados se publicaron el 21-oct (S10-117), no el ~29-oct.
- **Calendario**: la v27 llegó el 4-nov (no "~feb-2027"); la expiración de la v25 es el 23-feb-2027.
- **Qualified leads** (verificación de lead ads del mismo día, S10-135 y S10-136): el "sin mínimo de leads desde el
  30-oct-2025" vuelve a ser **[CONTESTED]** porque la guía de developers actualizada el 2026-10-27 sigue pidiendo
  200 leads/mes y solo instant forms; el Help Center dice que funciona también con formularios web.
