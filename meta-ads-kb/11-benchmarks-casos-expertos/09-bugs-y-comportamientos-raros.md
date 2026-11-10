# Bugs, comportamientos raros y cambios no documentados (2025-2026)

> Última verificación: 2026-10-16 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A11 (agente) · Ámbito: comportamientos anómalos, bugs, cambios silenciosos y efectos colaterales reportados entre 2025 y 2026, clasificados por **nivel de confirmación**. No es un changelog completo de producto (eso está en el área 10): aquí interesa lo que rompe datos, gasto o control sin avisar.

## Escala de confirmación

| Nivel | Significado |
|---|---|
| **C1: Confirmado por Meta** | Documentación, changelog de desarrolladores, página de estado (metastatus), legal o comunicado |
| **C2: Observado por varias fuentes independientes** | Al menos 2–3 practitioners o medios sin relación entre sí |
| **C3: Observación aislada** | Una cuenta o un post (LinkedIn, Reddit, practitioner) |
| **C4: Rumor o no verificable** | Sin fuente localizable o contradicho por otra fuente |

## TL;DR

- **Lo más peligroso de 2026 son los fallos silenciosos de datos.** La API devuelve **HTTP 200 con datos vacíos** al pedir ventanas eliminadas (7d y 28d view desde el 12-ene-2026) o desgloses no activados (dispositivo, hora y frecuencia desde el 6-ago-2026). Las versiones de API caducadas se ejecutan como la siguiente versión. Los dashboards de terceros "caen" sin que haya cambiado nada. **C1** (docs) / **C2** (efectos)
- **Los controles desaparecen o cambian por defecto sin anuncio claro.** Hasta un 5 % del presupuesto **por cada** placement excluido puede gastarse en él: activado por defecto en Ads Manager y desactivado en la API, desde el 8-oct-2025. Retirada progresiva de exclusiones de placement en ad set (aviso del 20-ago-2026). Audiencias de compradores ampliadas de 180 a 730 días automáticamente (18-may-2026). **C1/C2**
- **La creatividad cambia sola.** Toggles de IA reactivados (Business Insider, 2025). Reescritura de texto en imagen por defecto con hasta 8 variantes (jul-2026). Duplicar un anuncio reactiva música y promos (sep-2026). Test de **landing pages generadas por IA** en menos del 5 % de impresiones tras el switch "test new AI generation features" (sep-2026). **C1 a C3**
- **Las caídas son frecuentes y no compensadas.** Al menos 6 incidentes de entrega o de Ads Manager confirmados entre junio y septiembre de 2026, uno con reportes de no poder pausar mientras se gastaba. **C1** (incidentes) / **C2** (pausa)
- **Discrepancias de facturación nuevas.** Los fees de localización (2–5 %) van fuera de "Amount spent". **C1**
- **Patrones de rendimiento anómalos sin explicar:** bajón percibido desde el 29-jul-2026 (anuncio del nuevo ranking) y CPM −30 % con CTR y compras a la baja desde ~17-sep-2026 en varios países. **C2/C3**, causa desconocida.
- **Regla operativa:** tras cualquier anomalía, comprobar en este orden: metastatus → changelogs (Meta, Loomer, PPC Land) → ajustes por defecto del nivel anuncio, ad set y cuenta → integridad de los datos de la API → solo entonces "el algoritmo". **[STRONG INFERENCE]**

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **22-oct**: anunciantes retiran anuncios por ediciones de IA que no habían pedido (Adweek). **[EMPIRICAL]**
> - **6–8-nov**: ofertas detectadas en la web añadidas a anuncios copiados aunque las promociones estuvieran desactivadas; se controla en Commerce Manager → Settings → Offer merchandising → "Detected offers". **[EMPIRICAL]**
> - **Cambio silencioso del Help Center** de placements: Engagement aparecía como afectado el 12-oct y ya no el 9-nov. **[OFFICIAL META]**
> - `total_video_consumption_rate` sin datos desde principios de nov-2026 (retirada oficial, no un bug). **[OFFICIAL META]**
> - Fuentes: S10-101, S10-107, S10-125 a S10-127 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Datos, reporting y API

| Fecha | Comportamiento | Nivel | Impacto | Qué hacer | Fuente |
|---|---|---|---|---|---|
| 12-ene-2026 | Retirada de las ventanas **7d view y 28d view** de Ads Insights API (también en consultas históricas). Las peticiones devuelven **datos vacíos sin error** | C1 (anunciado en oct-2025) / C2 (efecto silencioso) | Caídas reportadas del 15–40 % de conversiones en dashboards de terceros "de la noche a la mañana" | Revisar conectores, rehacer series históricas con las ventanas disponibles (1d click, 7d click, 28d click, 1d view, 1d engaged-view) | [PPC Land](https://ppc.land/meta-restricts-attribution-windows-and-data-retention-in-ads-insights-api/); Dataslayer |
| mar-2026 | Redefinición del **clic** en atribución: solo los clics en enlace cuentan como click-through; el resto pasa a *engage-through* (1 día); el umbral de vídeo de engaged-view baja de 10 a 5 s | C2 (Search Engine Land, Loomer) | Ruptura de comparabilidad interanual; caídas de conversiones "por clic" | Anotar el cambio en los informes; comparar con el backend | Vía [goodmorningco](https://goodmorningco.com/blog/meta-ads-update-may-2026) (ver área 04) |
| 6-ago-2026 | Los desgloses `impression_device`, horario y `frequency_value` pasan a **opt-in**. Sin opt-in, HTTP 200 con `data` vacío, sin aviso | C1 | Dashboards de frecuencia o dispositivo a cero | Activar en Ads Manager ("Additional Breakdowns") o vía `POST /act_<ID>/insights/feature-settings`; los datos vuelven en ~1 día | [admakeai ago-2026](https://admakeai.com/blog/meta-ads-updates-august-2026) (cita docs de Meta) |
| 2026 | Las versiones de Marketing API caducadas **se ejecutan como la siguiente versión** sin aviso (v24.0 → v25.0, oct-2026) | C3 (tests del autor del changelog) | Cambios de comportamiento inesperados en automatizaciones | Fijar versiones y monitorizar los avisos de deprecación | admakeai |
| 25-ago-2026 | facebook-business-sdk 26.0.1 con notas de versión vacías; eliminó 14 campos de ad set (`time_start`, `budget_schedule_specs`…) | C3 | Scripts que rompen | Pinear el SDK y probar antes de actualizar | admakeai |
| 1-sep-2026 | **Lookalikes creados por API ignoran el campo de país** (con aviso de deprecación; la llamada tiene éxito) | C1 (changelog v26) / C3 (efecto) | Entrega a ubicaciones no previstas en ad sets multi-país | Auditar lookalikes creados por herramientas | [admakeai oct-2026](https://admakeai.com/blog/meta-ads-updates-october-2026) |
| 8–17 y 23-ago-2026 | Reporting de ingresos de Audience Network caído | C4 (sin fuente) | — | — | admakeai (sin fuente) |
| jul-2026 → | **Fees de localización** fuera de "Amount spent": las facturas no cuadran con Ads Manager | C1 | Gasto real entre un 2 % y un 5 % mayor en Reino Unido, España, Francia, Italia, Austria y Turquía | Conciliar con la factura y ajustar el ROAS de equilibrio | Medianama, eMarketer |
| 26-ago-2026 | Columna **Creative diversity** (Baja, Media o Alta), "estimada y en desarrollo". Cuentas con estáticos, vídeo, UGC y carrusel puntuadas como **Baja** | C1 (help) / C3 (puntuación) | Señal poco fiable aún | No optimizar contra ella todavía | Search Engine Land vía admakeai |
| 25-ago-2026 | Métrica de **"estimated spend"** basada en 2 días de campañas similares | C3 | — | Tomarla como orientativa | PPC Land |
| 2024 | Meta contaba como "primera compra" alrededor del 25 % de compras que no lo eran (setting de first conversions) | C3 (un anunciante, Search Engine Land) | % de nuevos clientes inflado | Medir los nuevos clientes en el backend | Search Engine Land (2024) |
| En curso | Durante las caídas, Ads Manager muestra **datos congelados o antiguos** | C2 | Decisiones con datos viejos | No optimizar durante incidentes | statusbird (mar-2026); admakeai |

## 2. Entrega, controles y ajustes por defecto

| Fecha | Comportamiento | Nivel | Impacto | Qué hacer | Fuente |
|---|---|---|---|---|---|
| ene-2025 | Retirada de las **exclusiones de detailed targeting** | C1 | Menos control de audiencia | Usar exclusiones de custom audiences o value rules | PPC Land |
| 8-oct-2025 | **"Limited spend on excluded placements":** hasta un 5 % del gasto **por cada** placement excluido. **Activado por defecto en Ads Manager** (Sales y Leads) y **desactivado por defecto en la API** | C1 (blog de desarrolladores) / C2 (default en la UI, Loomer y PPC Land) | Con varias exclusiones, bastante más del 5 % del presupuesto puede ir a placements no deseados | Desmarcar la casilla en cada ad set con exclusiones críticas (brand safety o compliance) | [Meta Developers](https://developers.facebook.com/blog/post/2025/10/08/introducing-limited-spend-on-excluded-placements-in-marketing-api/); [PPC Land](https://ppc.land/meta-pushes-spending-5-on-excluded-placements-for-sales-and-leads-campaigns/) |
| feb-2026 | La estructura unificada de Advantage+ impide exclusiones de placement a nivel de campaña | C2 | — | — | PPC Land |
| 18-may-2026 | **Audiencias de compradores ampliadas de 180 a 730 días automáticamente** salvo opt-out previo. En alguna cuenta, una exclusión se convirtió en "compradores de los últimos 730 días" | C2 (SocialBee, Loomer, vía changelog) | La prospección excluye a más gente; el remarketing apunta a compradores antiguos | Revisar cada audiencia y exclusión | [goodmorningco](https://goodmorningco.com/blog/meta-ads-update-may-2026) |
| may-2026 | Alta automática de productos de la web en el catálogo (títulos, precios, imágenes) salvo opt-out en Commerce Manager | C2 (SwipeInsight, vía changelog) | Productos no deseados en anuncios de catálogo | Revisar Commerce Manager | goodmorningco |
| 22-jun-2026 | Retirada inmediata de los desgloses DMA (Nielsen) "sin ventana de deprecación"; targeting de automoción migrado a códigos Comscore. Reportes no confirmados de campañas que dejaron de entregar | C1 / C4 | Campañas geo de automoción paradas | Migrar los códigos | admakeai jul-2026 |
| 16-jul-2026 | Audiencias reagrupadas bajo etiquetas "Customer" y "Engaged" sin anuncio. Las etiquetas condicionan las value rules | C3 (Loomer) | Value rules que no aplican como se espera | Revisar las etiquetas de audiencia | admakeai ago-2026 |
| 20-jul-2026 | El **ROAS goal** pasa a poder elegirse con optimización de volumen (no solo de valor) | C3 (Loomer) | Cambia la lógica de puja | Testear antes de usar | admakeai ago-2026 |
| 20-ago-2026 → | **Retirada progresiva de exclusiones de placement, plataforma, dispositivo y SO a nivel de ad set** (aviso en el producto; empieza por Sales y Leads; los sectores sensibles, exentos según Loomer). El sustituto son las value rules de placement (+1 000 % a −90 %; nunca 0). La única exclusión dura es **Account-level Placement Controls** | C1 (value rules, aviso en el producto) / C2 (alcance) | Imposible excluir al 100 % un placement por campaña | Usar block lists y placement controls a nivel de cuenta; value rules a −90 % | [PPC Land](https://ppc.land/some-meta-advertisers-lose-placement-controls-with-bid-cuts-capped-at-90/); Loomer |
| 22-sep-2026 | Límite de **250 anuncios por página** no aplicado en una cuenta (286 activos, "36 over limit" pero entregando) | C3 | Posible relajación de límites | No contar con ello | [PPC Land](https://ppc.land/meta-drops-250-ad-page-cap-in-some-accounts-as-286-ads-keep-running/) |
| 2025 | Añadir un anuncio nuevo a un ad set activo **no reinició el aprendizaje**, en contra de lo que daba a entender la documentación | C3 (Loomer) | Más libertad para añadir anuncios | Verificarlo en tu cuenta | Jon Loomer (qvt) |
| 7/11-oct-2026 | **Customer Lifecycle Strategy** (solo clientes nuevos, sin compra en 180 días) en ad sets de Sales manuales, "disponible para todos" según CTC; despliegue gradual según otras fuentes | C2/C3 | Herramienta contra el gasto en clientes existentes | Verificar en Ads Manager; medir el % de nuevos en el backend | CTC; Flightdeck |
| 2025 | **El tope de "existing customer budget" de ASC deja de estar disponible** al migrar a Advantage+ Sales | C1 (Meta citada por Loomer) | Más gasto potencial en clientes existentes | Ad sets con y sin clientes, o el nuevo ajuste de ciclo de vida | [Loomer](https://www.jonloomer.com/qvt/advantage-sales-replaces-advantage-shopping/) |

## 3. Creatividad automatizada e IA

| Fecha | Comportamiento | Nivel | Qué hacer | Fuente |
|---|---|---|---|---|
| finales de 2025 / ene-2026 | Toggles de generación de imágenes y "automatic adjustments" **reactivados solos** tras desactivarlos (3 anunciantes). Sustitución de un anuncio ganador por una imagen de IA incoherente (True Classic) | C2 (Business Insider más varias marcas) | Auditar las mejoras a nivel de anuncio **y** de cuenta cada semana | [Shopifreaks/BI](https://www.shopifreaks.com/meta-advantage-is-forcing-unwanted-ai-creative-on-brands/) |
| abr-2026 | Redimensionados, fondos alterados y cambios de formato de vídeo no pedidos; "reimaginaciones completas" | C2 (Marketing Brew, agencias) | Desactivar en categorías sensibles | [Marketing Brew](https://www.marketingbrew.com/stories/2026/04/21/meta-ai-creative-tools-marketer-response) |
| jun-2026 | La **adaptación automática a placements** generó errores visuales (producto "físicamente imposible"). Post en r/PPC con 227 votos sobre una variación de un anuncio de servicios locales "destrozada" por la IA | C2/C3 | Previsualizar todas las variantes por placement | admakeai jul-2026; PPC Land |
| 27/28-jul-2026 | Advantage+ **reescribe el texto dentro de imágenes subidas**: hasta 8 variantes de titular, **activado por defecto** | C3 (Loomer) | Desactivar si hay claims regulados o branding estricto | admakeai ago-2026 |
| 3-ago-2026 (visto el 1-sep) | Los píxeles nuevos traen activada por defecto la opción de que **la IA añada eventos "que faltan"**; en píxeles antiguos estaba desactivada | C1 (help) / C3 (ubicación) | Riesgo de eventos no deseados o duplicados | Revisar los ajustes del píxel | admakeai oct-2026 |
| sep-2026 | **Duplicar un anuncio reactivó música, navegación de productos y promociones** | C3 (un anunciante en Reddit) | Revisar tras cada duplicado | admakeai oct-2026 |
| 21-sep-2026 | Test de **landing pages generadas por IA** tras el switch "test new AI generation features": quien toca el anuncio puede ver una página de IA en lugar de la web. Meta dice que afecta a menos del 5 % de impresiones | C1 (descripción del switch) / C3 (test) | Desactivar si la landing tiene requisitos legales (salud, finanzas) | admakeai oct-2026 (Loomer) |
| 30-oct-2026 | Nuevos términos que incorporan las condiciones de IA generativa a los Self-Serve Ad Terms. Se dice (no verificado) que permiten tests sin aviso y que el anunciante responde del contenido de IA. Seguir anunciando = aceptación | C1 (fecha) / C4 (alcance) | Revisión legal en categorías reguladas | [Meta legal](https://www.facebook.com/legal/terms/ad_creative_generative_ai_terms); CTC · **2026-11-09**: suspendidas antes de entrar en vigor; siguen las del 22-ago-2025 (S10-113) |

## 4. Caídas, gasto y facturación

| Fecha (2026) | Incidente | Nivel | Notas |
|---|---|---|---|
| 8-ene | Incidente de entrega | C2 (adstatus) | — |
| 3-mar / 16-mar | Interrupción de unas 17 h (postmortem de un vendor); sin acceso a Ads Manager las primeras horas, las campañas siguieron gastando | C2 (vendors) | No confirmado en metastatus en las fuentes revisadas |
| 12-jun | Ads Manager caído unas 4 h; más de 100 000 reportes en Downdetector en una hora; las campañas siguieron gastando | C1 (metastatus) | Sin crédito automático |
| 23/24-jun | Incidente de entrega de varios días | C1 | — |
| 16-jul | Entrega caída 2 h 07 min (el inicio real fue anterior al publicado) | C1 | — |
| 19-jul | Entrega caída 2 h 32 min (más de 23 000 reportes); **imposible pausar mientras se gastaba** | C1 / C2 | — |
| 21-ago | Entrega caída 1 h 49 min | C1 | Reddit "contó" 8 caídas en agosto; solo esta se confirmó |
| 22-sep | Unas 1,5 h | C1 | Reddit "contó" 7 tramos más en septiembre; 3 eran problemas ajenos (p. ej. Shopify) |

- **Gasto por encima del presupuesto:** la regla de hasta un **75 % más** del presupuesto diario con compensación semanal es la más citada. Las afirmaciones de "50× en 7 días" o de un gasto de 22 000 $ en 8 h con un presupuesto de 80 $/día proceden de blogs **sin verificar** (C4). En 2024 hubo un bug real de sobregasto (9 200 $ en horas) con créditos para algunos afectados (Marketing Brew). **C2**
- **Sin SLA ni compensación pública** por caídas. Documentar el gasto durante los incidentes para reclamar. **C2**

## 5. Políticas, enforcement y cuentas

| Fecha | Comportamiento | Nivel | Fuente |
|---|---|---|---|
| 2025 | Olas de desactivaciones masivas; Meta Verified sin soporte efectivo; peticiones con decenas de miles de firmas | C2 | TechCrunch, NBC, Change.org |
| mar-2026 | Meta amplía el papel de la IA en el enforcement (según prensa) | C2 | NBC DFW / vendors |
| 4-jun-2026 | La Oversight Board: las apelaciones que repiten el mismo proceso automatizado "no son efectivas"; pide revisión humana en casos límite | C1 (Board) | Medianama, Oversight Board |
| ago-2026 | Perfil vinculado a un cliente desactivado **68 minutos** después de un email de verificación con plazo de 48 h | C3 (r/PPC vía changelog) | admakeai sep-2026 |
| 15-sep-2026 | Meta One (soporte de pago): **incoherencia entre la página de ayuda y el post de lanzamiento** sobre qué plan incluye soporte humano; no aclara si recupera cuentas publicitarias | C1 (incoherencia oficial) | admakeai oct-2026; Dooley |
| 25/26-sep-2026 | Anuncios del tráiler de un documental (Musk) rechazados como "contenido político" y restaurados por "un error" | C1 (TechCrunch, Meta admitió el error) | admakeai oct-2026 |

## 6. Anomalías de rendimiento sin causa confirmada

| Fecha | Observación | Nivel | Hipótesis (no verificadas) |
|---|---|---|---|
| 29-jul-2026 → | "Censo" en un subreddit que fecha un bajón (CPA ×2, CTR que colapsa) en el día del anuncio del nuevo sistema de ranking (Generative Recommender / GEM) en el call de Q2 | C3 | Despliegue de ranking; estacionalidad de verano; coincidencia |
| ~17-sep-2026 → | Miembros de Foxwell: **CPM −30 % en varios países con CTR y compras a la baja**. Caso polaco en Reddit: CPM de 80–100 zł → 13–20 zł, CTR del 2,5–3 % → 0,5 %, add to cart a 0 | C2 | Retirada de exclusiones de placement (desde el 20-ago) que lleva entrega a inventario barato; test de landings con IA; cambios de ranking |
| jul-2026 | Tasas de rebote del 57 % → 88 % en landings sin cambios | C4 | Tráfico de menor calidad (placements, bots) |
| 2026 | Divergencias entre trackers de CPM (Superads jul-2026 −12,7 % interanual frente a Meta +12 % de precio por anuncio; Tinuiti Q1 −3 % frente a CTC +28 %) | C2 | Mix de muestra y placements (ver `02`) |

**Lectura de patrón:** el dúo **"CPM cae + CTR y CVR caen"** es la firma típica de una entrega que se desplaza a inventario o usuarios más baratos y de menor intención. En 2025-2026 coincide con la pérdida de controles de placement y con más automatización. Que el CPM baje no es una buena noticia si cae la calidad. **[STRONG INFERENCE]**

## 7. Protocolo ante anomalías (checklist)

1. **metastatus.com** (Ads Manager, Ads Delivery, API) y la hora exacta del cambio.
2. **Changelogs:** Meta Developers, Jon Loomer, PPC Land y el changelog mensual de algún vendor serio.
3. **Ajustes por defecto:** Advantage+ Creative (anuncio y cuenta), placements (casilla del 5 %), audiencias (730 días, etiquetas), switch de "AI generation features", Customer Lifecycle.
4. **Integridad de datos:** deduplicación, eventos por hora, ventanas de atribución y opt-in de desgloses en la API, versión de la API.
5. **Desgloses:** placement, país, edad, dispositivo. Buscar desplazamientos de entrega.
6. **Backend:** pedidos y leads reales frente a la plataforma; factura frente a "Amount spent".
7. **Solo entonces:** hipótesis de "cambio de algoritmo". Documentar la fecha y comparar con otras cuentas o la comunidad.

## Implicaciones operativas

- Monta **alertas** de caída o subida de eventos, de gasto por hora y de "datos vacíos" en la API.
- Haz una **revisión semanal de ajustes por defecto** como tarea fija en las cuentas gestionadas.
- **No tomes decisiones estructurales durante una anomalía** sin confirmar su causa.
- Mantén un **registro interno de incidencias** con la fecha, el síntoma, la confirmación y la resolución. Es valioso para reclamar y para aprender.

## Preguntas abiertas

- ¿Qué causó la anomalía de septiembre de 2026 (CPM a la baja con la calidad a la baja)? Sin confirmación.
- ¿Se extenderá la retirada de exclusiones de placement a todos los objetivos y cuentas? Meta no ha dado fecha.
- ¿Qué cambia exactamente en los términos del 30-oct-2026? Falta un análisis línea a línea del texto oficial. (2026-11-09: suspendidos; si vuelven, comparar con las del 22-ago-2025.)

## Fuentes clave

- [Meta Developers: limited spend on excluded placements](https://developers.facebook.com/blog/post/2025/10/08/introducing-limited-spend-on-excluded-placements-in-marketing-api/): 8-oct-2025, meta-developers
- [PPC Land: 5 % en placements excluidos](https://ppc.land/meta-pushes-spending-5-on-excluded-placements-for-sales-and-leads-campaigns/): oct-2025, prensa
- [PPC Land: placement controls / value rules −90 %](https://ppc.land/some-meta-advertisers-lose-placement-controls-with-bid-cuts-capped-at-90/): ago-2026, prensa
- [PPC Land: límite de 250 anuncios por página](https://ppc.land/meta-drops-250-ad-page-cap-in-some-accounts-as-286-ads-keep-running/): sep-2026, prensa
- [PPC Land: attribution windows API](https://ppc.land/meta-restricts-attribution-windows-and-data-retention-in-ads-insights-api/): oct-2025, prensa
- [admakeai: changelogs de julio, agosto, septiembre y octubre de 2026](https://admakeai.com/blog/meta-ads-updates-october-2026): 2026, vendor (con estado de confirmación por item)
- [goodmorningco: Meta Ads update May 2026](https://goodmorningco.com/blog/meta-ads-update-may-2026): may-jul 2026, agencia
- [CTC: Every Meta Ads change in 2026](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026): 2026, agencia
- [Jon Loomer: Advantage+ Sales replaces Advantage+ Shopping](https://www.jonloomer.com/qvt/advantage-sales-replaces-advantage-shopping/): 2025, practitioner
- [Shopifreaks/BI: unwanted AI creative](https://www.shopifreaks.com/meta-advantage-is-forcing-unwanted-ai-creative-on-brands/): ene-2026, prensa
- [Marketing Brew: AI creative tools](https://www.marketingbrew.com/stories/2026/04/21/meta-ai-creative-tools-marketer-response): abr-2026, prensa
- [Statusbird: Meta Ads March 2026 outage](https://statusbird.io/blog/meta-ads-march-2026-outage-postmortem): 2026, vendor
- [Inc: Meta went down twice in 11 days](https://www.inc.com/temilola-agbede/meta-went-down-twice-in-11-days-the-outages-exposed-a-risk-many-businesses-ignore/91370415): 2026, prensa
- [Techtimes: outage del 12-jun-2026](https://www.techtimes.com/articles/318282/20260612/facebook-down-100000-plus-users-instagram-meta-ads-hit-global-outage.htm): jun-2026, prensa
- [Marketing Brew: bugs de Meta (2024)](https://www.marketingbrew.com/stories/2024/09/19/it-can-crush-our-business-ad-buyers-estimate-major-losses-from-meta-ad-platform-bugs): 2024, prensa
- [Meta: Ad Creative Generative AI Terms](https://www.facebook.com/legal/terms/ad_creative_generative_ai_terms): oct-2026, meta-oficial
- [Foxwell: post-Andromeda member reports](https://foxwelldigital.com/blog/is-detailed-targeting-dead-what-foxwell-members-are-seeing-post-andromeda): oct-2026, agencia

---

## Actualización desde el barrido de Reddit (Arctic Shift, 16-oct-2026)

> Añadido por el agente principal. Detalle y método en [08 §Barrido directo de Reddit](08-voice-of-advertiser-2025-2026.md).

| Fecha | Incidencia | Nivel de confirmación | Fuente |
|---|---|---|---|
| ~5–6-sep-2026 en adelante | Episodios repetidos de caída brusca de conversiones con gasto normal (6, 8, 11, 15–16, 20, 28–30-sep; 3–4 y 11-oct) | C3 (patrón de anunciantes, sin confirmación de Meta) | r/FacebookAds (ver 08) |
| 21–23-sep-2026 | Shopify cambia la lógica de sesiones (30 min de inactividad) y excluye bots de los informes por defecto; las series de sesiones y CVR se rompen en esa fecha | C2 (blog técnico; sin doc oficial localizada) | WeltPixel; r/FacebookAds 1ws863r |
| 22-sep-2026 | "Outage" citado por anunciantes | C4 (rumor) | r/FacebookAds 1ws863r |
| 8–10-oct-2026 | Meta (vía chat de soporte, según un anunciante) reconoce una estimación errónea del CTR de algunos anuncios de Instagram por datos "stale"; resuelto el 10-oct a las 11:21 PDT | C3 (cita de soporte en un único post; no figura en la status page) | r/FacebookAds 1x6fzvx |
| 3-oct-2026 | La app de Meta Ads Manager (Android 496.0.0.19.107) se cierra al abrirla tras actualizar | C3 (varios usuarios en el mismo hilo) | r/FacebookAds 1wwg0ma |
| oct-2026 | La interfaz muestra "Unpublished edits" en cada apertura del anuncio | C4 | r/FacebookAds 1x6g7wa |
