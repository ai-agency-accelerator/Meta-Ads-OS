# META ADS — CURRENT STATE 2026

> **Estado a 9-nov-2026** (revisión de octubre–noviembre, bloque B21; la anterior es del 16-oct-2026) · Autor: agente
> principal (síntesis de las áreas 01–12; changelog completo en
> [10/01-changelog-2025](10-cambios-2025-2026-api-ia-automatizacion/01-changelog-2025.md) y
> [10/02-changelog-2026](10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md)).
> **Este documento debe actualizarse** cada mes y siempre que Meta publique cambios (ver §10). Si algo de aquí contradice
> un archivo de área más antiguo, manda este documento y hay que corregir el otro.
> **Correcciones del 2026-11-09** (detalle en §9): las ubicaciones manuales a nivel de conjunto se retiran en Ventas,
> Clientes potenciales y Promoción de aplicación, **no** en Interacción (Engagement); la ventana gratuita de CTWA de
> hasta 7 días y los 1.000 service messages gratis al mes **sí** están en la doc oficial de precios de WhatsApp; la
> Marketing API v24.0 expira el **10-nov-2026** (no el 6-oct); las condiciones comerciales nuevas **no** entraron en
> vigor (suspendidas); los resultados de Q3 fueron el **21-oct-2026**; el "sin mínimo de leads" de qualified leads vuelve
> a ser **[CONTESTED]** (developers sigue con 200/mes); la restricción de CTWA a leads en la UE y el Reino Unido sale
> de una guía de WhatsApp de 2025, mientras el Help Center actual solo da un aviso genérico para Europa (comprobar en
> la cuenta); la fecha 9-sep de Prohibited Commercial Practices no está en el registro oficial.

## 0. Resumen en 13 líneas

1. **El sistema de recomendación de Meta es el targeting.** Andromeda (retrieval) + Lattice + GEM (modelo central que
   enseña a los modelos de ranking) + Adaptive Ranking + **Meta Generative Recommender** (LLMs en retrieval desde Q2-2026).
   Meta declara +18,9 % de conversiones y +12 % de CTR en el último año por GEM. En Q3-2026: retrieval generativo en el
   Feed de Facebook (casi +2 % de conversiones en los segmentos objetivo), GEM en más superficies (+1,7 % de conversiones
   offsite, +9,6 % en apps) y Andromeda (+1,4 % en Facebook). **[OFFICIAL META]** (earnings Q3, 21-oct-2026)
2. **Advantage+ es el estado por defecto** de las campañas de Ventas, Leads y App (presupuesto de campaña + Advantage+
   audience + placements automáticos). ASC/AAC ya no existen. **[OFFICIAL META]**
3. **El control manual se ha convertido en control de valor**: value rules (−90 % a +1000 %), audience labels, exclusion-only
   audiences, Customer Lifecycle Strategy, ROAS goal / cost per result goal / bid cap. **[OFFICIAL META]**
4. **Los placements manuales se están retirando** a nivel de ad set en Sales, Leads y App promotion (rollout gradual
   desde ago–oct-2026); quedan exclusiones a nivel de cuenta por objetivo y value rules por placement. Awareness, Traffic
   y **Engagement** los conservan (Help Center releído el 2026-11-09; hasta esa fecha la KB incluía Engagement por
   fuentes secundarias de oct-2026). **[OFFICIAL META]**
5. **La atribución cambió de definición**: click-through = solo link clicks; el resto es engage-through (1 día; vídeo ≥5 s)
   desde marzo de 2026; 7d/28d view fuera de la API desde el 12-ene-2026. Y desde el **12-nov-2026** el ajuste del píxel
   *Measure conversions on customer devices* (activado por defecto; no activo para personas en la UE y el Reino Unido)
   empareja visualización y compra en el dispositivo: más conversiones reportadas sin cambiar ventana ni modelo. Hay que
   re-baselinar KPIs en cada discontinuidad. **[OFFICIAL META]**
6. **La creatividad es la palanca principal** y su diversidad real (ángulos, personas, formatos) importa: Meta dice que
   los creativos demasiado parecidos pueden tratarse como no distintos (página *creative differentiation*) **[OFFICIAL META]**;
   la columna *Creative diversity* aparece en la interfaz desde ago-2026, sin artículo de ayuda **[EMPIRICAL]**.
7. **La IA generativa de Meta viene activada por defecto** en varias mejoras. La reescritura de texto dentro de imágenes
   es una función oficial ("Enhance media text (AI)"); que venga activada por defecto se observa desde ~jul-2026. El
   anunciante responde del contenido generado. Hay que auditar los defaults. **[OFFICIAL META]** + **[EMPIRICAL]**
   En oct–nov-2026 hubo anunciantes que retiraron anuncios por ediciones de IA que no habían activado y ofertas de la web
   añadidas a anuncios copiados **[EMPIRICAL]**. Las condiciones nuevas que hacían al anunciante único responsable de lo
   que crean las funciones de IA de Meta están **suspendidas hasta nuevo aviso** (siguen las de 22-ago-2025) **[OFFICIAL META]**.
8. **Señal de calidad = ventaja competitiva**: CAPI (ya también "Meta-enabled" en un clic), CRM → CAPI para lead gen
   (qualified leads exige CAPI desde abr-2026), value optimization, Custom Attribution (beta 2026). **[OFFICIAL META]**
9. **Los costes suben**: precio medio por anuncio +12 % interanual en Q1 y Q2-2026 (+20 % EE. UU./Canadá en Q2) y
   **+14 % en Q3-2026** (impresiones +10 %); location fees del 2–5 % en UK/ES/FR/IT/AT/TR desde 1-jul-2026. **[OFFICIAL META]**
10. **Advantage+ no es universalmente superior en incrementalidad** (Haus, 640 tests: gana a manual en iROAS en el 42 % de
    las marcas). Medir incrementalidad sigue siendo responsabilidad nuestra. **[EMPIRICAL]**
11. **Agentes de IA**: MCP oficial de Meta + Ads CLI (beta abierta abr-2026; borradores con aprobación desde 6-oct-2026);
    asistente de IA en Ads Manager para todos (en Q3 Meta dice que está desplegando "acciones más agénticas" con
    aprobación; a 9-nov no hay confirmación de disponibilidad general). **Muse para pequeñas empresas** (29-sep-2026, solo
    EE. UU. y Canadá) se conecta a la cuenta publicitaria, analiza rendimiento y redacta campañas que no se publican sin
    aprobación. La "automatización total" anunciada para finales de 2026 no existe como producto. **[OFFICIAL META]** +
    **[STRONG INFERENCE]**
12. **Europa**: anuncios "menos personalizados" como elección del usuario desde ene-2026, fin de anuncios políticos y de
    temas sociales (6-oct-2025), verificación obligatoria para productos financieros en España. Las condiciones
    comerciales nuevas quedaron suspendidas tras una cautelar en Noruega (28-oct), la investigación de la CMA británica
    (30-oct, nota oficial en gov.uk) y conversaciones con la Comisión Europea. **[OFFICIAL META]** (aviso en la página
    de condiciones)
13. **Más control a nivel de creativo** (oct-2026): **elegir una audiencia (edad y género) para cada contenido del
    anuncio** dentro del mismo conjunto (19-oct; orienta, no limita) y **desglose de resultados por cada imagen, vídeo y
    variante de texto** en Ads Manager (Breakdown → Creative → Media; 27-oct). **[OFFICIAL META]**

---

## 1. Qué funciona ahora (consenso 2026 con matices)

| Práctica | Por qué funciona | Matiz / cuándo no | Evidencia |
|---|---|---|---|
| Estructuras consolidadas (pocos ad sets con volumen) | Más señal por unidad de aprendizaje; menos solapamiento | Separar por economía distinta, objetivo distinto o restricción legal | [OFFICIAL META] + [EMPIRICAL] |
| Advantage+ en Ventas/App como punto de partida | Mejoras medias publicadas (p. ej. −7,2 % CPR con Advantage+ audience en ventas, −10 % con placements) | No siempre más incremental; lead gen sin señal de calidad → leads baratos | [OFFICIAL META] vs [EMPIRICAL] → [CONTESTED] |
| Diversidad creativa de conceptos | Retrieval/ranking basados en el contenido; similares = redundantes | Microvariantes no abren inventario | [OFFICIAL META] + [EMPIRICAL] |
| Estáticos + vídeo + UGC/creadores | Estáticos igualan al vídeo en hit rate (Motion 2026); partnership ads −19 % CPA (Meta) | Varía por vertical | [EMPIRICAL] |
| CAPI + Pixel deduplicados; señales de valor | El sistema aprende de lo que recibe | Calidad > cantidad (EMQ, frescura, cobertura) | [OFFICIAL META] |
| Lead gen optimizando a calidad (qualified leads vía CRM) | Meta: −10 % coste por lead cualificado, −9,5 % en web, −21 % instant forms | Requiere CAPI, etapa ≤28 días, 1–40 % de conversión | [OFFICIAL META] |
| Value rules en vez de exclusiones | Ajusta el valor sin cortar inventario | Bajan hasta −90 %, nunca apagan | [OFFICIAL META] |
| Medir incrementalidad (lift, geo, holdout; incremental attribution como lectura adicional) | Lo atribuido ≠ lo causado | Incremental attribution [CONTESTED] (Haus 0,80× → 1,26× vs estándar 2025→2026) | [EMPIRICAL] |
| Click-to-message (WhatsApp/Messenger/IG) optimizando a leads/compras | Meta: −24 % CPL y −10 % coste por compra frente a optimizar a conversaciones | Optimización a leads en CTWA no disponible en UE, UK, Japón y Corea del Sur según la guía de WhatsApp Business de 2025 ([07/11](07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md)). Matiz del 2026-11-09: el Help Center actual solo da un aviso genérico ("ciertas campañas y funciones de mensajería" no disponibles en Europa, Japón y Corea del Sur), sin nombrar esta optimización ni el Reino Unido; exige ≥10 eventos de lead o compra en 30 días. Comprueba en Ads Manager, con la cuenta del cliente, si aparece *Maximize number of leads through messaging* | [OFFICIAL META] (dos fuentes oficiales de fechas distintas; detalle no cerrado) |
| Leer qué pieza gana dentro de un anuncio multi-media con el desglose por asset (Breakdown → Creative → Media; texto en *Dynamic creative element*) | Ads Manager ya da resultados por cada imagen, vídeo y variante de texto (oct-2026) | No es un test: el sistema reparte la entrega según su predicción, así que solo genera hipótesis; los formatos *Show as carousel/collection* no salen en el desglose | [OFFICIAL META] |
| Personalizar el creativo por edad y género sin partir el conjunto (*Choose an audience for each ad creative*) | Mantiene la consolidación y deja que el creativo hable a cada grupo | Orienta, no limita: Meta "también puede llegar a gente que es probable que responda"; en B2B la edad y el género rara vez son el eje | [OFFICIAL META] + [EMPIRICAL] (Loomer) |

## 2. Cambios clave 2025–2026 (cronología compacta)

| Fecha | Cambio | Impacto práctico |
|---|---|---|
| 14-ene-2025 | Categoría especial "Credit" → **"Financial products and services"** | Más verticales financieros con targeting restringido |
| ~ene-2025 | Restricciones de datos para salud y bienestar (core setup, eventos lower-funnel) | Algunas campañas de salud no pueden optimizar a compra |
| feb-2025 | Flujo unificado Advantage+ (Sales/App/Leads) + Opportunity Score; fin del Existing Customer Budget Cap | El punto de partida es "automatizado"; CLS/exclusiones sustituyen al cap |
| 31-mar-2025 | **Fin de exclusiones de detailed targeting** (anunciado antes; efectivo en ad sets activos) | Excluir intereses ya no existe; excluir custom audiences sí |
| abr-2025 | **Incremental attribution** (global en Q2) | Nueva opción de atribución/optimización |
| may-2025 | Fin de Offline Conversions API → CAPI | Eventos offline vía CAPI |
| may–jun-2025 | **Value rules**; Opportunity Score global | Control de valor por segmento |
| 16-jun-2025 | Anuncios en WhatsApp Status y canales promocionados (rollout global feb–mar-2026) | Nuevo inventario |
| 1-jul-2025 | **WhatsApp cobra por mensaje** | Recalcular coste por conversación |
| jul–ago-2025 | Ad set budget sharing (20 %); renombre "Advantage" → "Advantage+"; *optimize website destination*; LPV medible sin píxel | Flexibilidad entre ad sets; Meta puede cambiar el destino del clic (fijarlo en tests) |
| 2-sep-2025 | Custom audiences/conversions "flagged" (salud, finanzas) inutilizables en campañas nuevas | Revisar nombres y reglas de URL |
| 6-oct-2025 | **Fin de anuncios políticos/sociales/electorales en la UE** | Afecta a anunciantes españoles |
| 29-may-2025 / 8-oct-2025 | Anuncio (may) y API v24 (oct): flexibilidad diaria del 25 % al 75 %, hasta 5 % de gasto en placements excluidos (por defecto), consolidación de intereses, no se crean ASC/AAC | "Excluir placement" ya no es 0 % |
| ~oct-2025 | Herramienta nativa **Creative testing** (2–5 variantes, ≤20 % presupuesto, 7 días) | Test limpio dentro del ad set |
| 30-oct-2025 | **Advantage+ leads** global; campañas híbridas web + instant form | Leads con automatización por defecto |
| 10-nov-2025 | Post de ingeniería GEM | — |
| 16-dic-2025 | Las conversaciones con Meta AI pasan a ser señal para anuncios | Más señal de intención |
| 12-ene-2026 | **7d_view y 28d_view dejan de devolverse en la API**; históricos limitados | Dashboards con columnas vacías |
| 15-ene-2026 | Ad sets con intereses consolidados sin actualizar dejan de entregar | Cuentas heredadas con ad sets "muertos" |
| ene-2026 | UE: elección de anuncios "menos personalizados" (LPA) | Señal más pobre en la UE |
| 21-ene-2026 | **Threads ads** para todos los usuarios del mundo (incluido en Advantage+ placements) | Nuevo inventario |
| 18-feb-2026 | API v25: ASC/AAC no se crean ni actualizan (todas las versiones desde 19-may-2026) | Recrear como Sales con Advantage+ |
| **3-mar-2026** | **Click-through = solo link clicks; engage-through 1 día; vídeo ≥5 s** | Re-baselinar KPIs; menos conversiones "por clic" |
| ~mar-2026 | Los anuncios de un solo medio en el Feed de Facebook dejan de mostrar la URL | Menos señal de destino visible: reforzar la promesa en el creativo |
| 10-mar-2026 | Anuncio de **location fees** (efectivos 1-jul-2026: UK 2 %, ES/FR/IT 3 %, AT/TR 5 %) | Coste real > Ads Manager |
| abr-2026 | **Qualified leads exige CAPI** (campañas nuevas; existentes afectadas desde ago-2026); Customer Lifecycle Strategy en beta; asistente de IA de Ads Manager para todos; CAPI "Meta-enabled" de un clic; Pixel enriquecido con IA | CRM → CAPI obligatorio para optimizar calidad |
| 29-abr-2026 | **Meta Ads AI Connectors** (MCP oficial + Ads CLI) en beta abierta | Agentes externos pueden gestionar campañas |
| 18-may-2026 | Audiencias de compradores web/app: retención 180 → 730 días | — |
| 3-jun-2026 | **Meta Business Agent** global (WhatsApp, Messenger, IG) | IA conversacional nativa |
| 24-jun-2026 | Reserva de citas dentro de Instant Forms (Calendly, LeadConnector/HighLevel; solo app móvil de Facebook; en Instagram abre el navegador de la app) | La cita no se reporta en Ads Manager: devolverla por CAPI. El Help Center menciona HubSpot pero no lo lista como calendario integrado; la disponibilidad global anunciada para octubre no está confirmada oficialmente (verificación del 2026-11-09) |
| 1-jul-2026 | Location fees facturados; subida de tarifas de marketing de WhatsApp en ES/IT/UK | — |
| 16-jul-2026 | MCP abierto a cualquier app + reglas MCP; Audiences reorganizado por labels | Gobernanza de agentes |
| ~20-jul-2026 | ROAS goal combinable con "maximizar conversiones" (observado) | — |
| ~27-jul-2026 | Advantage+ creative **reescribe el texto dentro de imágenes** ("Enhance media text (AI)", función oficial; activada por defecto según lo observado) | Riesgo de marca y de claims |
| 29-jul-2026 | API v26: pausa ASC/AAC restantes; lookalikes sin país (1-sep); fuera Explore Feed y Messenger Stories; fin del checkout de Shops; Q2 earnings: Generative Recommender | — |
| 1-ago-2026 | Business Agent facturado ($2 por millón de tokens) | — |
| 6-ago-2026 | Breakdowns device/hour/frequency en API solo con opt-in (sin él: vacío sin error) | Activar "Additional Breakdowns" |
| ~10-ago-2026 | Exclusion-only custom audiences | Exclusiones sin convertir la lista en sugerencia |
| 20-ago → ~12-oct-2026 | **Fin de placements manuales en ad sets** de Sales, Leads y App promotion (gradual). Awareness, Traffic y Engagement no se ven afectados (corrección 2026-11-09: antes incluía Engagement) | Assets por placement + value rules + exclusiones de cuenta |
| ~26-ago-2026 | Columna **Creative diversity** (Low/Medium/High, "estimada") | — |
| 28-ago-2026 | Verificación financiera obligatoria en Polonia (España ya la exigía) | — |
| 9-sep-2026 | Política unificada **Prohibited Commercial Practices** (fraude/estafas); retirada de "Unacceptable Business Practices" | Sanciones que se extienden a activos asociados. El nombre y la redirección están confirmados; la fecha no: el registro de cambios oficial de la norma muestra una versión del 2026-10-29 y ninguna de septiembre **[CONTESTED]** (verificación del 2026-11-09) |
| ~21-sep-2026 | Test de **landing pages generadas por IA** desde tu web (interruptor "test new AI generation features"; <5 % de impresiones observado) | Desactivar en tests y donde importe el control del mensaje |
| 16-sep-2026 | **Apple anuncia cambios de ATT en la UE con iOS 27.2**: nuevo aviso ("Allow"/"Reject", sin la palabra "track"), obligatorio en DE, FR, IT, PL y RO; las apps pueden volver a preguntar al año aunque el usuario rechazara **[OFFICIAL Apple]** | Cuando llegue iOS 27.2, más conversiones atribuidas en la UE sin cambio real de ventas: marcar la fecha y no comparar a través de ella |
| 21–23-sep-2026 | Shopify cambia la lógica de sesiones (30 min de inactividad) y excluye bots de sus informes (según terceros) | Series de sesiones/CVR de Shopify rotas en esa fecha |
| 15-sep-2026 | Meta One para negocios (soporte humano en planes de pago); Creator Marketing Hub global | — |
| 28-sep-2026 | WhatsApp: la ventana gratuita tras un anuncio click-to-WhatsApp pasa de 72 h a **hasta 7 días** (la página oficial de precios dice "may remain open for up to 7 days" **[OFFICIAL META]**; la fecha la dan BSPs **[EMPIRICAL]**) | Recalcular el coste por conversación de CTWA |
| 29-sep-2026 | **Muse para pequeñas empresas** (EE. UU. y Canadá): se conecta a la cuenta publicitaria, analiza y redacta campañas; "nada se publica, envía ni gasta" sin aprobación **[OFFICIAL META]** | Alternativa nativa a los agentes externos para pymes; no disponible en España |
| 1-oct-2026 | WhatsApp cobra los service messages, con **1.000 gratis por número y mes** (página oficial de precios; la subpágina de mensajes sin plantilla no los menciona). Los mensajes del Business Agent se cobran también dentro de la ventana gratuita **[OFFICIAL META]** | Modelar el coste de atención por WhatsApp |
| 6-oct-2026 | Ad Week: vídeo desde estáticos (GA), **Customer Lifecycle Strategy para todos**, Ads Creative Studio (rollout), MCP con borradores y aprobación. Cambio fuera de ciclo: vídeo en los resultados de búsqueda de Instagram (`ig_search`, gradual) | — |
| 8-oct-2026 | Meta deja de aceptar anuncios de ByteDance/que enlazan a TikTok en 7 países (no España) | — |
| 8–10-oct-2026 | Incidente reportado (cita del soporte de Meta en Reddit, una sola fuente): estimación errónea del CTR de algunos anuncios de Instagram por datos "stale"; resuelto el 10-oct | Tratar 8–10-oct como periodo anómalo en los análisis |
| 13-oct-2026 | GEM central único (+18,9 % conversiones, +12 % CTR en el último año) | — |
| 15-oct-2026 | Brand Building Summit: **Ads Super Burst** (picos de alcance de 3–24 h con exclusividad de categoría; Reach Planner; disponibilidad general por fases), First Impression Ads (test en EE. UU.), Reels trending ads (15 temas) y Aggregated View Time (alfa) **[OFFICIAL META]** | Formatos de marca con presupuesto alto; poco relevantes para B2B pequeño |
| 19-oct-2026 | **Audiencia por creativo** (*Choose an audience for each ad creative*): edad y género por pieza dentro del conjunto; en la API, `targeting_automation.creative_audience_pairing` **[OFFICIAL META]**. Activada por defecto en Ventas, desactivada en el resto de objetivos (Loomer) **[EMPIRICAL]** | Personalizar sin fragmentar el conjunto |
| 21-oct-2026 | Earnings Q3-2026: precio por anuncio +14 %, impresiones +10 %, partnership ads +97 % interanual, ~10 M de anunciantes usan IA generativa, el asistente de Ads Manager despliega acciones más agénticas con aprobación **[OFFICIAL META]** | Costes al alza; partnership ads como palanca |
| 22-oct-2026 | Adweek: anunciantes que retiran anuncios por ediciones de IA que no habían activado **[EMPIRICAL]**. Cambio fuera de ciclo: campo `is_pca_unified` en campañas de Ventas (inmutable; significado no documentado) **[OFFICIAL META]** | Auditar las mejoras de Advantage+ creative anuncio a anuncio |
| 24-oct → 5-nov-2026 | Condiciones comerciales nuevas con términos de IA: entrada en vigor prevista el 30-oct → aplazada al 20-nov → cautelar en Noruega (28-oct) → investigación de la CMA (30-oct) → **suspendidas hasta nuevo aviso** (aviso en la página oficial) **[OFFICIAL META]** + **[OFFICIAL CMA]** | Siguen vigentes las condiciones del 22-ago-2025 |
| 26-oct-2026 | Sale iOS 27.2 con el aviso ATT alternativo de la UE **[EMPIRICAL]** (la nota de Apple no se ha leído) | Discontinuidad en la atribución de la UE desde esa fecha |
| 27-oct-2026 | **Desglose por asset** en Ads Manager: Breakdown → Creative → Media (cada imagen o vídeo), *Dynamic creative element* (variantes de texto) y *Ad delivery* (medios retirados) **[OFFICIAL META]** | Leer qué pieza rinde dentro de un anuncio multi-media |
| ~28-oct-2026 | "Añadir la navegación por productos" activada en anuncios existentes salvo opt-out (aviso y agencias **[EMPIRICAL]**; la mejora sí está en la lista oficial de Advantage+ creative) | En servicios B2B sin catálogo, comprobar que está desactivada |
| 4-nov-2026 | **Marketing API v27.0**: expansión de dispositivos activada por defecto en conjuntos de Ventas con `user_device`/`user_os`; `lookalike_spec` con `country`/`location_spec` rechazado; product showcase por defecto; `phone_otp_verification_type` en formularios; Ads Burst y Ads Super Burst en reach & frequency **[OFFICIAL META]** | Ver §3 y [10/06](10-cambios-2025-2026-api-ia-automatizacion/06-marketing-api-versiones-y-automatizacion.md) |
| 5-nov-2026 | Cambio fuera de ciclo: breakdown `pa_creator_ig_handle` (resultados de partnership ads por creador) **[OFFICIAL META]** | — |
| 6–8-nov-2026 | Ofertas detectadas en la web añadidas a anuncios copiados (PPC Land, SMT) **[EMPIRICAL]**; se controla en Commerce Manager → Settings → Offer merchandising → "Detected offers" | Revisar si el cliente publica precios o descuentos en la web |
| 10-nov-2026 | Expira la Marketing API v24.0 **[OFFICIAL META]** | — |
| 12-nov-2026 | **Measure conversions on customer devices** activado por defecto en el píxel (no activo para personas en la UE ni el Reino Unido) **[OFFICIAL META]**; la fecha sale del panel de Events Manager según terceros **[EMPIRICAL]** | Re-baselinar conversiones de compra fuera de la UE |

## 3. Qué está desapareciendo o ya desapareció

| Elemento | Estado | Sustituto |
|---|---|---|
| Exclusiones de intereses | Eliminadas (mar-2025) | Custom audiences de exclusión, exclusion-only audiences |
| Intereses granulares | Consolidados; ad sets antiguos parados (15-ene-2026) | Advantage+ audience + sugerencias |
| ASC / AAC | Muertos (API bloqueada 19-may-2026; pausados v26) | Campaña Sales/App con Advantage+ |
| Existing customer budget cap | Eliminado (2025) | Customer Lifecycle Strategy, exclusiones, 2 ad sets con min/max |
| 7d view / 28d view (API) | Vacíos desde 12-ene-2026 | 1d view, comparaciones con 28d click |
| Click-through con likes/shares/saves | Fuera desde mar-2026 | Engage-through (1 día) |
| Placements manuales en ad sets (Sales/Leads/App promotion; Engagement no, corrección 2026-11-09) | Retirándose (ago–oct-2026) | Value rules por placement, exclusiones de cuenta, assets por placement |
| Placements: Explore feed, Messenger inbox/Stories, FB video feeds | Retirados | — |
| "Excluir un placement = 0 % de gasto" | Ya no (hasta 5 % por defecto desde oct-2025) | Desmarcar la opción o exclusión de cuenta |
| Bid multipliers | Se sustituyen por value rules (2027) | Value rules |
| Offline Conversions API | Retirada (may-2025) | CAPI |
| Checkout nativo en Shops / Commerce Order API | Retirados (2025 / 27-oct-2026) | Web; checkouts en Messenger/Meta AI en test |
| Conversion leads sin CAPI | No disponible en campañas nuevas (abr-2026); las existentes, afectadas desde ago-2026 (aviso del Help Center, releído el 2026-11-09) | Qualified leads con CAPI CRM |
| `lookalike_spec` con `country` o `location_spec` | Rechazado en la API v27 (4-nov-2026); en todas las versiones unos 90 días después | Lookalikes sin ubicación (sin país desde 1-sep-2026) |
| Métrica `total_video_consumption_rate` | Sin datos desde principios de nov-2026, sin reemplazo | Métricas estándar de reproducción |
| Funciones legacy de la Graph API (`ids`, `date_format`, `method`, `.as()`, `callback`, `asyncbatch`) | Cerradas a apps nuevas en todas las versiones; eliminadas en v28 | Llamadas estándar |
| `POST /{catalog-id}/batch` y `meta_moment_maker_spec` | Sustituidos en la API v27 | `items_batch`; `product_type` `ADS_BURST`/`ADS_SUPER_BURST` en `reachfrequencypredictions` |
| Recomendación "≤6 anuncios por ad set" | Retirada (2025) | Sin cifra oficial; práctica 10–20 en BAU |
| Anuncios políticos/sociales en la UE | Prohibidos (6-oct-2025) | — |
| Flexible format en Ad setup | Sustituido por anuncios multi-media (~mar-2026) | Multi-media (hasta 10 assets) |
| Nielsen DMA | Comscore Markets (22-jun-2026) | `comscore_market` |
| Políticas "Unrealistic outcomes", "Misleading claims", "Circumventing systems" (páginas) | Reorganizadas (404 desde fin-2025); principios vigentes en otras normas | Prohibited Commercial Practices y demás estándares |

## 4. Qué automatiza Meta vs qué controlamos nosotros

| Decisión | Quién decide | Nuestra palanca |
|---|---|---|
| A quién mostrar | Meta (Advantage+ audience por defecto) | Señales (CAPI, valor, CRM), exclusiones de custom/exclusion-only audiences, controles de cuenta, value rules por edad/género/ubicación, audience labels, CLS, audiencia por creativo (edad y género por pieza; orienta, no limita) |
| Dónde | Meta | Value rules por placement, exclusiones de cuenta por objetivo, assets por placement, block lists |
| Cuánto gastar por día | Meta (175 % un día, 7× semana) | Presupuesto semanal efectivo, spend caps, budget scheduling |
| Cuánto pujar | Meta (Highest volume/value) | Cost per result goal, ROAS goal, bid cap, value rules |
| Qué creatividad | Meta (dentro del ad set) | Conceptos distintos, test nativo, gasto garantizado, push delivery (observado); leer el desglose por asset (Media, Dynamic creative element) |
| Variantes creativas | Meta si las mejoras están ON | Opt-out por mejora, Branding, palabras restringidas, "Detected offers" en Commerce Manager, opt-out de product showcase (`product_extensions`) |
| Qué cuenta como conversión | Nosotros (evento, ventana), con definiciones de Meta | Ajustes de atribución, incremental attribution, conversion count, CRM |
| Verdad de negocio | Nosotros | Backend, CRM, lift, geo-tests, MMM |
| **100 % nuestro** | — | Oferta, economía, creatividad, calidad de señal, funnel post-clic, ventas, medición, políticas, seguridad |

## 5. Nomenclatura vigente (antes → ahora)

| Antes | Ahora (2026) |
|---|---|
| Business Manager | **Business Portfolio** (Meta Business Suite / Business Settings) |
| Pixel (como contenedor) | **Dataset** (Pixel + CAPI + offline + app) |
| CBO (Campaign Budget Optimization) | **Advantage+ campaign budget** ("campaign budget") |
| ASC (Advantage+ shopping campaigns) | **Advantage+ sales campaigns** = campaña Sales con Advantage+ activado |
| AAC (Advantage+ app campaigns) | Campaña App con Advantage+ |
| DPA (Dynamic Product Ads) | **Advantage+ catalog ads** |
| Cost cap | **Cost per result goal** |
| Minimum ROAS | **ROAS goal** |
| Lowest cost | **Highest volume** (o **Highest value** si optimiza valor) |
| Conversion leads optimization | **Maximize number of qualified leads** (qualified leads) |
| Conversions API for CRM / Offline Conversions API | **Conversions API** (eventos CRM/offline) |
| Engaged-view attribution | **Engage-through attribution** (ampliada) |
| Branded content ads / whitelisting | **Partnership ads** (ad codes, Creator Marketing Hub) |
| Dynamic creative / flexible format | **Anuncios multi-media / flexibles** con Advantage+ creative |
| Special ad category "Credit" | **Financial products and services** |
| "Beneficiary" (transparencia UE) | **Advertiser** |
| Business AI | **Meta Business Agent** |
| Unacceptable Business Practices (anuncios) | **Prohibited Commercial Practices** (Community Standards) |
| — | **Choose an audience for each ad creative** (audiencia por creativo; API `creative_audience_pairing`, oct-2026) |
| Meta Moment Maker (reach & frequency) | **Ads Burst / Ads Super Burst** (API v27) |
| Engaged-view / clic de cualquier tipo | Además de estándar e incremental, el Help Center muestra un modelo de atribución **"custom"** (sin detalle; verificación del 2026-11-09) |

## 6. Números y reglas oficiales vigentes (para no repetir folklore)

| Tema | Regla vigente | Fuente/área |
|---|---|---|
| Learning phase | ~50 resultados en la semana tras la última edición significativa; *learning limited* "no es una penalización" | [02/03](02-estructura-campanas/03-learning-phase.md) [OFFICIAL META] |
| Ediciones significativas | Targeting, creatividad, evento, añadir anuncio (observado que no siempre reinicia), pausa ≥7 días, cambio de bid strategy; presupuesto/bid "según magnitud" | [02/03] |
| Gasto diario | Hasta 175 % un día; ≤7× por semana (210 %/8,4× con budget sharing) | [02/06] |
| Presupuesto mínimo recomendado | ≥10× coste del goal/día; ≥5× el objetivo con cost per result goal | [02/06] |
| Value optimization | CAPI + ≥5 valores distintos, ~100 conversiones en 14 días; presupuesto para ≥50/semana. En Leads, *Maximize value of conversions*: ≥5 valores únicos, >100 conversiones en 14 días y 3 semanas de prueba (Help Center, leído el 2026-11-09) | [02/02], [09/02] |
| Goal-based bidding | Objetivo inicial CPA +10–20 % / ROAS −10–20 %; ajustes 5–10 % cada ≥7 días; ≥3 semanas antes de escalar | [09/01] |
| Qualified leads (CRM) | CAPI obligatorio (campañas nuevas desde abr-2026; existentes desde ago-2026); lead ID de 15–17 dígitos (o click ID, teléfono o email); subida ≥1/día; etapa ≤28 días; 1–40 % de conversión; enviar todas las etapas a medida que cambian; learning 2–4 semanas (guía) o 1–2 meses (FAQ) **[OFFICIAL META]**. **Dos contradicciones entre fuentes oficiales [CONTESTED]** (verificación del 2026-11-09): (1) **mínimo de leads**: el anuncio del 30-oct-2025 lo elimina, pero la guía de developers actualizada el 2026-10-27 sigue pidiendo **≥200 leads/mes**; planificar con 200 y probar con menos; (2) **formularios web**: el Help Center dice que funciona con formularios web e instant forms, y developers y la especificación del payload, que solo con instant forms. Los "≥2–3 etapas" y la "cobertura ≥60 %" no aparecen en ninguna fuente oficial **[HYPOTHESIS]** | [05/03] |
| Atribución por defecto (web) | 7d click + 1d view, con 1d engage-through probablemente activado **[STRONG INFERENCE]** (el Help Center no fija el default: verificarlo en cada ad set). Con click + view + engage, la columna Results suma solo click + view **[OFFICIAL META]**. Los cambios del 3-mar-2026 se refieren a conversiones web y en tienda; ninguna fuente oficial dice que afecten a los leads de instant form **[HYPOTHESIS]**. El Help Center muestra un modelo de atribución "custom" además de estándar e incremental, sin más detalle | [04/10] |
| Fecha de reporting | Conversiones offsite por fecha de conversión | [04/10] |
| Creative testing nativo | 2–5 variantes, ≤20 % presupuesto, 7 días, sin solapamiento, solo Highest volume | [03/05] |
| Anuncios por ad set | Límite técnico 50 no archivados (API); sin recomendación oficial de nº | [03/05] |
| Anuncios por Página | 250 / 1.000 / 5.000 / 20.000 activos según gasto pico mensual | [03/05] |
| Fatiga oficial | *Creative limited* (<2× coste histórico) y *Creative fatigue* (≥2×); Meta cuenta las exposiciones del mismo asset en otras campañas de la Página y aconseja mantener activo el original | [03/06] |
| Calidad de la landing | Meta usa *landing page bounce rate* y *dwell time* como señales de calidad; páginas de baja calidad repetida hacen los anuncios "less competitive in auctions" | [03/15](03-creatividad/15-landing-pages-y-cro-trafico-meta.md) [OFFICIAL META] |
| Evento si no hay volumen | Meta recomienda LPV como alternativa si un ad set no llega a ~50 conversiones/semana; nosotros preferimos un evento de valor (oferta de entrada, lead cualificado) y usar LPV solo como puente consciente | [02/02], [03/15] |
| Value rules | −90 % a +1000 % | [09/02] |
| Placements excluidos | Hasta 5 % de gasto por placement excluido salvo desmarcar | [07/02] |
| Safe zones 9:16 | 14 % arriba, 35 % abajo, 6 % laterales | [07/03] |
| WhatsApp | Precio por mensaje (jul-2025); service messages cobrados desde el 1-oct-2026, con **1.000 gratis por número y mes**; la ventana gratuita tras un anuncio CTWA puede durar **hasta 7 días** (desde el 28-sep-2026 según BSPs); los mensajes del Business Agent se cobran también dentro de esa ventana (2 $ por millón de tokens) **[OFFICIAL META]** (página de precios releída el 2026-11-09; corrige la versión del 16-oct, que daba 72 h y marcaba los 1.000 como [CONTESTED]). La subpágina de mensajes sin plantilla no menciona los 1.000: incoherencia interna de Meta | [07/12] |
| Versiones de la Marketing API | v27.0 (4-nov-2026) es la última; v26.0 sin fecha de fin publicada; v25.0 hasta el 23-feb-2027; **v24.0 hasta el 10-nov-2026**. Graph API: v21 se elimina el 21-ene-2027 y v22 el 20-may-2027 **[OFFICIAL META]** | [10/06] |
| Expansión de dispositivos (API v27) | En conjuntos de Ventas nuevos que segmentan por `user_device`/`user_os`, `targeting_automation.individual_setting.device` viene activado; opt-out con `0`; llega a todas las versiones ~90 días después (≈feb-2027, fecha exacta por confirmar) **[OFFICIAL META]** | [10/06] |
| Audiencia por creativo | Solo edad (mínima, según Loomer) y género; oculta la edad y el género del conjunto; el sistema puede llegar a otras personas con probabilidad de responder **[OFFICIAL META]** | [02/07], [03/07] |
| Leads de instant forms | Meta guarda los leads 90 días: lo anterior no se puede descargar. Verificación de teléfono por código de un solo uso **por WhatsApp o SMS** (lo elige Meta; sin verificar no cuenta como lead; un fijo no verifica). *Higher intent* solo se entrega en el feed móvil de Facebook e Instagram **[OFFICIAL META]** | [05/02] |
| Etiquetado de IA en anuncios | Meta añade "AI info" a los anuncios creados o muy editados con su IA generativa y detecta herramientas de terceros con señales estándar; desde jun-2026 se ve en "About this ad". Para anuncios comerciales **no hay obligación** del anunciante de declararlo (sí en anuncios de temas sociales, elecciones o política) **[OFFICIAL META]** | [08/06] |
| Location fees | UK 2 %; ES, FR, IT 3 %; AT, TR 5 % (por ubicación de la audiencia, fuera del presupuesto) | [11/03] |
| Cuentas deshabilitadas | 6 meses para pedir reinstauración; una re-revisión por anuncio | [08/09] |

## 7. Prácticas antiguas que NO debemos aplicar

| Práctica | Por qué murió | Veredicto |
|---|---|---|
| Hipersegmentación por intereses en muchos ad sets | Señal fragmentada; intereses consolidados; sistema de retrieval/ranking supera a la segmentación manual | [OUTDATED] |
| "Regla del 20 %" de subida de presupuesto | Meta habla de magnitud, no de %; es un ritmo prudente, no una ley | [OUTDATED] |
| Duplicar ad sets ganadores para escalar | Solapamiento de subasta **[OFFICIAL META]**; además, la investigación de Meta apunta a eliminar la varianza aleatoria entre copias (no medido en ad sets reales) **[STRONG INFERENCE]** | [OUTDATED] |
| Lookalike 1 % como base | LAL se expanden y pierden contra Advantage+ audience en tests | [OUTDATED] |
| Campaña de retargeting obligatoria | Advantage+ ya remarketea (10–40 % del gasto según Loomer; ~15 % de media en Haus) **[EMPIRICAL]**; incrementalidad menor | [OUTDATED] como default |
| "3–6 anuncios por ad set" | Recomendación retirada en 2025 | [OUTDATED] |
| Frecuencia > 3 = fatiga | Meta mide fatiga por coste vs histórico | FALSE |
| Excluir intereses | Ya no existe | [OUTDATED] |
| Configurar 8 eventos de AEM / verificar dominio para eventos | No necesario desde 2023 | [OUTDATED] |
| 7d/28d view en dashboards | Retiradas de la API | [OUTDATED] |
| "Click" = cualquier interacción | Desde mar-2026 solo link clicks | [OUTDATED] |
| Placements manuales en campañas de conversión | Retirándose; −10 % CPR con Advantage+ placements (Meta) | [OUTDATED] |
| "Sazonar el píxel" / píxel nuevo / warm-up de cuenta | Sin mecanismo documentado | UNPROVEN |
| Lanzar a medianoche / evitar fines de semana | Pacing actual | UNPROVEN |
| ASC con tope de clientes existentes | Tope eliminado | [OUTDATED] |
| Offline Conversions API | Retirada | [OUTDATED] |

Mitos completos (66): [12/01-mitos](12-mitos-contradicciones/01-mitos-meta-ads-2026.md).

## 8. Calendario próximo

Pasado desde la revisión anterior (para leer series): retiradas de la API v26 en todas las versiones (27-oct), veda de
anuncios políticos nuevos en EE. UU. (27-oct → 3-nov), navegación por productos por defecto (~28-oct), Q3 (21-oct),
iOS 27.2 (26-oct). Las condiciones del 30-oct **no** entraron en vigor (ver §2).

| Fecha | Qué |
|---|---|
| **10-nov-2026** | Expira la Marketing API v24.0 |
| **12-nov-2026** | *Measure conversions on customer devices* activado por defecto (fuera de la UE y el Reino Unido): marcar la fecha en los informes |
| 1-dic-2026 | Se retira `branded_content_advertisable_medias` de la Marketing API (anuncios de colaboración); lo sustituye la Content Discovery API **[OFFICIAL META]** ([07/06 §2.6](07-instagram-placements-mensajeria/06-partnership-ads-creadores-ugc-whitelisting.md)) |
| ~~20-nov-2026~~ | Fecha aplazada de las condiciones nuevas: **anulada** al suspenderse (aviso del 5-nov) |
| fin de 2026 | Audience discovery en lenguaje natural (Ad Week); exclusiones de audiencias personalizadas en Reels trending ads; objetivo 90 % de ingresos de anunciantes verificados; Muse Image (anunciado); checkout en Meta AI (test "este otoño") |
| ene-2027 | UE: recordatorio no descartable de la elección de anuncios menos personalizados; India: cuentas de WhatsApp Business en INR (ver [10/02](10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md)) |
| sin fecha | Decisión de la CMA y de la Comisión Europea sobre las condiciones; nueva fecha de las condiciones, si la hay |
| 21-ene-2027 | Se elimina la Graph API v21 |
| ~feb-2027 (≈90 días tras v27) | Expansión de dispositivos por defecto y rechazo de `lookalike_spec` con ubicación en **todas** las versiones de la API |
| 23-feb-2027 | Expira la Marketing API v25.0 |
| 20-may-2027 | Se elimina la Graph API v22 |
| v28 (2027) | Se eliminan las funciones legacy de la Graph API (`ids`, `date_format`, `method`, `.as()`, `callback`, `asyncbatch`) |
| 2027 | Value rules sustituyen a bid multipliers |

**Regulación que cambia lo que se puede decir en anuncios de consultoras de IA y automatización** (España y UE; estado
a 2026-11-09, detalle y fuentes en el
[playbook de consultoras](14-playbooks/playbook-consultoras-ia-automatizacion.md) §4.4, §5.6 y §8.4). Datos de
reguladores, no de Meta:

| Fecha | Qué | Evidencia |
|---|---|---|
| desde 2-ago-2026 | Art. 50 del Reglamento de IA: quien ofrece un sistema que conversa con personas tiene que informar de que es una IA (salvo que sea evidente) | [OFFICIAL — regulador] |
| hasta 2-dic-2026 | Plazo para el marcado del contenido generado por sistemas de IA que ya estaban en el mercado antes de aplicarse el art. 50 (Ómnibus Digital de IA, Reglamento (UE) 2026/1744) | [STRONG INFERENCE] (recogido en la investigación del playbook; falta citar el artículo en el ledger) |
| 1-ene-2027 | Verifactu para contribuyentes del Impuesto sobre Sociedades (RDL 15/2025). Hacienda anunció el 2026-10-05 la previsión de aplazarlo a octubre de 2028; no estaba en el BOE el 2026-11-09 | [OFFICIAL — regulador] (fecha vigente) + [CONTESTED] (aplazamiento anunciado, no publicado) |
| 1-jul-2027 | Verifactu para el resto (incluidos autónomos); mismo aplazamiento anunciado | Ídem |
| 6-oct-2027 | Factura electrónica B2B para empresas con más de 8 M€ de volumen de operaciones (RD 238/2026 y Orden HAC/1028/2026) | [OFFICIAL — regulador] |
| 2-dic-2027 | Obligaciones de los sistemas de IA de alto riesgo, aplazadas por el Ómnibus Digital de IA (Reglamento (UE) 2026/1744) | [STRONG INFERENCE] (ídem) |
| 6-oct-2028 | Factura electrónica B2B para el resto | [OFFICIAL — regulador] |
| sin fecha | Kit Digital y Kit Consulting: convocatorias cerradas, sin plazo abierto. Bono IA (Plan IA360): anunciado, sin bases ni convocatoria | [OFFICIAL — regulador] |

No presentes ninguna ayuda como disponible ni ninguna obligación como «o te multan» sin comprobar la fecha el día del
anuncio: es justo lo que revisa `revisor-politicas`.

## 9. Contradicciones abiertas que hay que vigilar

- **Umbral de learning**: oficial ~50/semana; rumores de 25 (Advantage+) o 10–15 (app/purchase) sin fuente oficial.
- **Incremental attribution**: Meta +24 % de conversiones incrementales vs estándar; Haus pasó de 0,80× a 1,26× de iROAS
  frente a estándar entre 2025 y 2026; practicantes escépticos. **[CONTESTED]**
- **Qualified leads: mínimo de leads y formularios web** (dos fuentes oficiales que se contradicen; ver §6). **[CONTESTED]**
- **Qualified leads: cobertura ≥ 60 % y ≥ 2–3 etapas**: la KB ([05/03](05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md)) lo cita de la guía
  de partners; no aparece en las páginas oficiales releídas el 2026-11-09. El playbook de consultoras lo trata como
  requisito práctico, no oficial. **[CONTESTED]**
- **Sequenced Events** (optimizar a dos eventos en orden dentro de *Maximize number of qualified leads* con ubicación
  web): solo lo describe Loomer (2026-08-07 como prueba, 2026-10-06); parece exigir eventos por CAPI y unos 30 eventos
  en 7 días; solo atribución estándar. Sin documentación de Meta. **[EMPIRICAL]**/**[HYPOTHESIS]**
- **Agente de IA dentro del instant form** (*lead capture AI agent*) y *Preferred lead answers*: pruebas descritas por
  Loomer (jul–ago-2026), sin fuente oficial. **[HYPOTHESIS]**
- **Flexible ROAS goal** y **Performance-based budget increase** (beta): una sola fuente de agencia (2026-11-06) que cita
  una sesión de Meta sin enlace. **[HYPOTHESIS]**
- **Threads como ubicación por defecto en todas las campañas** (19–26-oct-2026): solo agencias; Threads ya estaba en
  Advantage+ placements desde ene-2026. **[CONTESTED]**
- **Si la medición en dispositivo alimenta la optimización** o solo el reporting: el Help Center habla de medir; no
  dice nada de la entrega. **[HYPOTHESIS]**
- **Facturación del Business Agent en Instagram y Messenger**: la doc oficial de precios solo habla de WhatsApp.
  **[HYPOTHESIS]**
- **Fecha de Prohibited Commercial Practices** (9-sep-2026 en la KB; el registro de cambios oficial muestra 2026-10-29).
  **[CONTESTED]**
- **Si añadir un anuncio reinicia el learning**: la documentación dice que sí; la observación desde 2025, que no siempre.
- **Default real de atribución en ad sets web nuevos** (engage-through ON u OFF): solo se cierra mirando una cuenta.
- **Episodios de volatilidad desde ~6-sep-2026 y sobre todo desde mediados de septiembre** (patrón en r/FacebookAds con
  ≥10 hilos independientes; tráfico bot al alza; un incidente de CTR en Instagram del 8–10-oct citado por soporte). Causa
  general no confirmada por Meta. Ver [11/08](11-benchmarks-casos-expertos/08-voice-of-advertiser-2025-2026.md) y [11/09](11-benchmarks-casos-expertos/09-bugs-y-comportamientos-raros.md).

**Resueltas en la revisión del 2026-11-09** (B21): ventana gratuita de CTWA de hasta 7 días y 1.000 service messages
gratis al mes, ahora en la página oficial de precios (se revierte la corrección del 16-oct) · ubicaciones manuales: la
retirada no afecta a Engagement · v24.0 expira el 10-nov-2026 · condiciones del 30-oct suspendidas · Q3 publicado el
21-oct. Sigue abierta, con matiz: la restricción de CTWA a leads en la UE y el Reino Unido (guía de WhatsApp de 2025)
frente al aviso genérico del Help Center actual (Europa, Japón y Corea del Sur, sin nombrar el Reino Unido).

**Resueltas en la revisión adversarial del 16-oct-2026** ([12/05](12-mitos-contradicciones/05-revision-adversarial-kb.md)):
engaged-view 5 s (observado desde oct-2025, comunicado oficialmente el 3-mar-2026) · qualified leads sin mínimo de leads
desde el 30-oct-2025 y válido en web (**reabierta el 2026-11-09**: la guía de developers del 2026-10-27 sigue con 200
leads/mes y solo instant forms) · Customer Lifecycle Strategy: la interfaz muestra 730 días por defecto (opciones 180,
90, 60, 30; los 180 de CTC no tienen fuente de Meta) · límite de 50 anuncios no archivados por ad set (los 150 eran de las
antiguas ASC) · flexibilidad del 75 % anunciada el 29-may-2025 · AEM sin 8 eventos desde mayo de 2023 · exclusiones de
detailed targeting retiradas por fases (ad sets nuevos ~jul-2024, API v22 21-ene-2025, activos 31-mar-2025, boosts
10-jun-2025) · ThruPlay = 15 s (o 97 % si el vídeo es más corto; existe también objetivo de 6 s).

## 10. Cómo mantener este documento

Fuentes de vigilancia (detalle y método en [10/10-como-vigilar-cambios](10-cambios-2025-2026-api-ia-automatizacion/10-como-vigilar-cambios.md)):
Graph/Marketing API changelog y out-of-cycle changes · facebook.com/business/news · Meta Newsroom · earnings trimestrales ·
Meta Engineering · Jon Loomer · Social Media Today · Search Engine Land · status page de Meta. Regla: **observado ≠
confirmado**; cada cambio entra con fecha, fuente y etiqueta.
