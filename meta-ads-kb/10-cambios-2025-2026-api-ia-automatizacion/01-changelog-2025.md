# Changelog conceptual Meta Ads 2025 (mes a mes)

> Última verificación: 2026-10-15 · Autor: A10 (agente) · Ámbito: todo lo que cambió en 2025 en Ads Manager, objetivos,
> Advantage+, audiencias, placements, creatividad/IA, optimización, atribución, reporting, Pixel/CAPI, lead ads,
> WhatsApp/Threads/Instagram, Marketing API, políticas y regulación UE. Fuentes en `fuentes/ledger-10-cambios-api-ia.md` (IDs `S10-###`).

## TL;DR

- **2025 fue el año de la unificación Advantage+**: un único flujo de creación para Sales, App y Leads con la automatización
  encendida por defecto (completado Q2 para Sales/App y Q3 para Leads). Advantage+ Shopping (ASC) se convierte en
  "Advantage+ sales" y su API se bloquea en v24 (oct-2025). **[OFFICIAL META]** (S10-016, S10-017, S10-009)
- **El control manual se movió de "excluir" a "ajustar valor"**: value rules (mayo-2025) y, en API, "limited spend" de hasta
  5% en placements excluidos (v24). Las exclusiones de targeting detallado desaparecieron (31-mar-2025). **[OFFICIAL META]**
- **La medición se redefinió**: incremental attribution (abril-2025, global en Q2), Insights API alineada con Ads Manager
  (10-jun-2025), engaged-view a 5 s (observado ~oct-2025; comunicado oficialmente por Meta el 3-mar-2026) y anuncio de la retirada de ventanas 7d/28d view en API (efectiva 12-ene-2026).
  **[OFFICIAL META]** (S10-001, S10-016, S10-018)
- **Nuevos inventarios**: Threads ads abiertos a anunciantes globales (abril-mayo), WhatsApp Status/Channels en la pestaña
  Novedades (16-jun), placements de notificaciones y perfil de Facebook. **[OFFICIAL META]**
- **WhatsApp pasa a cobro por mensaje** (1-jul-2025) y arranca Business AI (México/Filipinas). **[OFFICIAL META]** (S10-023, S10-017)
- **Regulación**: fin de anuncios políticos/sociales/electorales en la UE (6-oct-2025), restricciones de audiencias con
  datos de salud/finanzas (2-sep-2025), multa DMA de 200 M€ (abr-2025) y acuerdo para nueva opción de anuncios menos
  personalizados (8-dic-2025, efectiva ene-2026). **[OFFICIAL META]** / prensa
- **Andromeda + GEM + Lattice** pasaron de anuncio técnico a realidad operativa: Meta atribuye a cada uno mejoras del 3–5%
  en conversiones por trimestre. Consecuencia práctica: la diversidad creativa sustituye a la segmentación como palanca
  principal. **[OFFICIAL META]** para las cifras; **[STRONG INFERENCE]** para la consecuencia.

## Leyenda de cada entrada

`Fecha · Qué cambió · Alcance · Confirmación · Impacto práctico · Qué práctica invalida · Fuente`

- **Confirmación**: OFICIAL (Meta lo publica) · OBSERVADO (anunciantes/practitioners lo ven, sin doc oficial) · TEST.
- Fechas "~" = aproximadas (aparición en cuentas, no anuncio).

---

## Enero 2025

- **14-ene · Categoría especial "Credit" pasa a "Financial products and services"** (`FINANCIAL_PRODUCTS_SERVICES`).
  Alcance: global vía API y Ads Manager. OFICIAL (S10-001). Impacto: más anunciantes financieros (no solo crédito) entran
  en categoría especial con restricciones de audiencia tipo vivienda/empleo. Invalida: segmentar seguros/inversión
  "fuera" de categoría especial.
- **21-ene · Marketing/Graph API v22.0**. OFICIAL (S10-007, S10-005). Elimina el opt-in/out del bundle
  `STANDARD_ENHANCEMENTS` de Advantage+ creative (cada mejora se controla por separado), limita exclusiones de targeting
  detallado, migra `instagram_actor_id`→`instagram_user_id`. v22 de Marketing API expiró el 19-feb-2026.
- **~ene · Restricciones para anunciantes de salud y bienestar** (datos sensibles; Core Setup que recorta parámetros de
  URL y bloquea la optimización a eventos lower-funnel en algunos casos). Alcance: inicialmente EE. UU., cuentas marcadas.
  OBSERVADO con avisos en Events Manager; documentación de Meta parcial (S10-067). Impacto: campañas de salud optimizan a
  eventos superiores o a eventos personalizados "neutros". **[CONTESTED]** el alcance exacto. Lo detalla el área 08/04.
- **~ene · Engaged-view activado por defecto** en ad sets de conversión (se puede desactivar). OFICIAL (S10-028).
- **~ene · Chat con nuevos leads por Messenger** tras enviar un formulario instantáneo (con consentimiento). OBSERVADO/OFICIAL en producto (S10-028).
- **15-ene · Ad sets con opciones de targeting detallado retiradas en 2024 dejan de entregar** (si no se editaron).
  OFICIAL según Loomer (S10-028). Ojo: hubo una **segunda ola** con v24 (consolidación de intereses; esos ad sets dejan
  de entregar el 15-ene-**2026**, S10-009). No confundir ambas.
- **~ene · Verificaciones regionales**: verificación de servicios financieros en Australia y de beneficiario/pagador en
  Taiwán. OFICIAL (S10-028).
- **ene · Threads empieza a probar anuncios** en EE. UU. y Japón. OFICIAL (S10-048).

## Febrero 2025

- **~6-feb · Anuncio del flujo unificado Advantage+** (Sales, App, Leads): Advantage+ encendido por defecto; si cambias
  ajustes recomendados, el "estado Advantage+" se apaga; se presenta **Opportunity Score** (0–100). OFICIAL (S10-050).
  Meta reportó en tests ~10% menos coste por lead cualificado con Advantage+ en Leads. Impacto: el punto de partida pasa a
  ser "automatizado y luego restringir", no al revés. Invalida: elegir "manual vs Advantage+ Shopping" como decisión de
  tipo de campaña.
- **feb · Se elimina el Existing Customer Budget Cap (ECBC)** en la nueva configuración de ventas. OFICIAL (S10-028, S10-031).
  Impacto: el control de "% de presupuesto a clientes existentes" desaparece; Meta propone dos ad sets (clientes / excluir
  clientes) como workaround (S10-034). Invalida: usar ASC con tope de clientes existentes para forzar adquisición.
- **feb · Inventory filter por defecto en "expanded"** para in-content y Audience Network; **Facebook Profile Feed** como
  placement; **audience types en catálogo** retirados. OFICIAL/OBSERVADO (S10-028).

## Marzo 2025

- **10-mar (efectivo 10-jun) · Ads Insights API ignora `use_unified_attribution_setting` y `action_report_time`**; las
  respuestas reflejan Ads Manager; `reach` deja de devolverse en breakdowns con fecha de inicio >13 meses. OFICIAL (S10-001).
  Impacto: cualquier dashboard que forzaba otra configuración de atribución por API cambió sus números en junio.
- **31-mar · Exclusiones de targeting detallado eliminadas** de campañas activas (las nuevas ya no las tenían desde
  jul-2024; en posts promocionados desde 10-jun-2025). Meta cita −22,6% de coste mediano por conversión sin exclusiones.
  OFICIAL (S10-034 y secundarias). Invalida: excluir intereses ("excluir estudiantes", "excluir intereses de lujo").
  Se sigue pudiendo excluir **audiencias personalizadas** y usar controles de audiencia a nivel cuenta.
- **31-mar · Placement `notification` (notificaciones de Facebook)** añadido a `facebook_positions`. OFICIAL (S10-001).
- **~mar · Desactivar autofill en formularios instantáneos**; **Branding** en la creación de anuncios (logo, colores,
  fuentes para mejoras IA); **Signals Gateway** (enviar datos a destinos fuera de Meta). OBSERVADO/OFICIAL (S10-028).

## Abril 2025

- **~abr · Incremental attribution** (modelo de atribución que optimiza y reporta conversiones "que no habrían ocurrido
  sin el anuncio"). Disponible para objetivos con maximizar conversiones/valor en web; columnas comparables desde
  1-abr-2025. OFICIAL; despliegue global completado en Q2 (S10-016). Ver área 04 para el análisis de medición.
- **~abr · Threads abre anuncios a anunciantes globales** (imagen y vídeo; "as of May… most countries including the US").
  OFICIAL (S10-016, S10-048).
- **23-abr · Comisión Europea declara no conforme el modelo "pay or consent" (DMA) y multa a Meta con 200 M€**; Meta
  recurre el 2-jul. OFICIAL/prensa (S10-036).
- **~abr · Lead ads**: chat por WhatsApp con nuevos leads, plantillas de formulario, flexible form delivery, respuestas
  múltiples, entrega por email, verificación SMS. OBSERVADO (S10-028). Detalle en área 05.
- **~abr · Integración GA4 en Events Manager** y **formato condicional** dentro de Ads Manager. OBSERVADO (S10-028).

## Mayo 2025

- **~may · Value rules**: ajuste de puja por edad, género, ubicación y SO móvil (más tarde placements, dispositivo,
  conversion location). OFICIAL (S10-028). Impacto: es la nueva forma de "segmentar" sin restringir. Invalida: duplicar
  ad sets por edad/género para controlar CPA.
- **~may · Placement de notificaciones de Facebook** en delivery; **Threads Feed** pasa de test a disponible. OFICIAL (S10-028).
- **29-may · Marketing/Graph API v23.0**. OFICIAL (S10-008). Advantage+ Audience por defecto en nuevos ad sets; edad y
  género como **sugerencias** (`individual_setting`); `advantage_state` de solo lectura. v23 de Marketing API expiró el 9-jun-2026.
- **may · Offline Conversions API discontinuada**; los eventos offline van por Conversions API con `action_source` físico.
  OFICIAL (changelog v20 citado en S10-032). Invalida: integraciones OCAPI/Zapier antiguas.
- **~may · Tests creativos**: CTA sticker, traducción de voz (voiceover). TEST (S10-028).

## Junio 2025

- **2-jun · WSJ: Meta quiere automatizar por completo creación y targeting de anuncios para finales de 2026**
  (subir imagen de producto + presupuesto → anuncio completo, personalización por usuario). Prensa con fuentes internas,
  **no anuncio oficial** (S10-049). Ver 03-tendencias para qué se ha lanzado realmente.
- **5-jun → ago · Fin del checkout nativo en Facebook/Instagram Shops**: compra en la web del comerciante; se retira la
  opción híbrida "Website and shop" (S10-068). Consecuencia en 2026: Commerce Order Management API bloqueada en v26 (S10-004).
- **~9-jun · Opportunity Score global** y flujo Advantage+ para Sales/App completado en Q2. OFICIAL (S10-016, S10-028).
  Matiz: un score alto no predice rendimiento; aceptar recomendaciones a ciegas (p. ej., subir presupuesto, quitar
  restricciones) no siempre conviene. **[EMPIRICAL]**
- **10-jun · Exclusiones de targeting detallado retiradas de posts promocionados**; Insights API alineada con Ads Manager.
  OFICIAL (S10-001).
- **16-jun · WhatsApp: anuncios en Status, canales promocionados y suscripciones a canales** (pestaña Novedades, separada de
  los chats). Señales limitadas: país, ciudad, idioma, actividad en Novedades (y, si se vincula en Accounts Center, datos
  de FB/IG). Despliegue gradual 2025–2026. OFICIAL (S10-056, S10-016).
- **17-jun · Cannes Lions 2025**: vídeo multi-escena desde hasta ~20 imágenes con texto y música, Video Highlights,
  CTA stickers, virtual try-on, voces IA, Branding en Advantage+ creative. **Mayoría en TEST** al anunciarse (S10-051).
- **~jun · Crop and expand with AI** para adaptar a placements. OBSERVADO (S10-028).
- **Q2 · Omnichannel ads global** (optimiza ventas online + tienda en una campaña; −15% mediana coste por compra en tests
  de Meta). OFICIAL (S10-016).

## Julio 2025

- **1-jul · WhatsApp Business Platform pasa de cobro por conversación a cobro por mensaje** (plantillas por categoría y
  país; utility dentro de la ventana de servicio gratis; nuevos tramos de volumen para utility/auth; marketing sin
  tramos). OFICIAL (S10-023). Invalida: cálculos de coste "por conversación de 24 h".
- **1-jul · Meta Conversations (Miami)**: WhatsApp gestionable en Ads Manager junto a FB/IG, Business AI en test
  (México), llamadas de voz/vídeo para empresas. OFICIAL/prensa (S10-059).
- **~jul · Ad set budget sharing** (hasta 20% del presupuesto entre ad sets en campañas con presupuesto de ad set);
  API el 18-ago. OFICIAL (S10-001, S10-028).
- **~jul · "Optimize website destination"**: Meta puede enviar a otra URL de tu web. En API desde v24. OFICIAL (S10-009).
- **~jul · Meta anuncia en su Newsroom que dejará de servir anuncios políticos, electorales y sociales en la UE** (por el
  reglamento TTPA). Aviso técnico a developers el 18-sep; efectivo 6-oct. OFICIAL (S10-001 para el aviso técnico y la
  fecha efectiva; la fecha exacta del post de Newsroom no se ha re-verificado).
- **30-jul · Earnings Q2-2025**: ~2M anunciantes usan vídeo generativo (Image Animation, Video Expansion); traducción
  automática de copy a 10 idiomas en test; incremental attribution global; CTM +40% en EE. UU. OFICIAL (S10-016).

## Agosto 2025

- **15-ago · Threads admite anuncios de vídeo** y se añade a `customization_spec`. OFICIAL (S10-001).
- **19-ago · Comscore Markets como fuente de geotargeting** junto a DMA. OFICIAL (S10-001). Preludio a la retirada de
  Nielsen DMA (22-jun-2026).
- **~ago · Value rules para placements** (bajar puja en placements problemáticos en vez de excluir). OBSERVADO (S10-028).
- **~ago · Límites de gasto de ad set pasan de tope duro a media**; **palabras restringidas** para texto IA; **traducción
  de media** (subtítulos/overlays). OBSERVADO (S10-028).

## Septiembre 2025

- **2-sep · Restricciones proactivas sobre custom audiences y custom conversions** que sugieran condiciones de salud o
  situación financiera: se marcan, dejan de alimentarse y no se pueden usar en campañas nuevas; v24 hace fallar
  updates con objetos marcados (todas las versiones desde 6-ene-2026). OFICIAL (S10-066, S10-009). Invalida: audiencias por
  URL tipo `/diabetes-tratamiento` o conversiones personalizadas con nombres sensibles.
- **2-sep · `live_special_price` en Catalog API** (precios solo para live shopping). OFICIAL (S10-001).
- **18-sep (efectivo 6-oct) · Anuncios de temas sociales, electorales y políticos dejan de estar permitidos en la UE**
  (todas las versiones de API). OFICIAL (S10-001).
- **~sep · Landing page views sin Pixel**; métrica de **follows de Instagram** desde anuncios; "swap selling points" IA.
  OFICIAL/OBSERVADO (S10-028).

## Octubre 2025

- **~1-oct (efectivo 16-dic) · Meta usará las conversaciones con Meta AI como señal para anuncios y contenido**
  (excluye temas sensibles; UE/UK/Corea del Sur más tarde). OFICIAL/prensa (S10-055).
- **6-oct · Threads admite carruseles de imagen**. OFICIAL (S10-001).
- **6-oct · Fin efectivo de anuncios políticos/sociales en la UE.** OFICIAL (S10-001).
- **8-oct · Marketing/Graph API v24.0** — la versión más disruptiva de 2025. OFICIAL (S10-009, S10-034):
  - Bloqueo de creación/duplicación/edición de ASC y AAC (`AUTOMATED_SHOPPING_ADS`, `SMART_APP_PROMOTION`) → migración a
    campañas Advantage+ (`migrate_to_advantage_plus`, `advantage_state`).
  - **Flexibilidad del presupuesto diario 25% → 75%** (gasto semanal ≤ 7× diario).
  - `is_adset_budget_sharing_enabled` obligatorio con presupuesto de ad set.
  - `placement_soft_opt_out`: hasta **5% del gasto en placements excluidos** (Sales y Leads).
  - Retirada del placement **Facebook video feeds**.
  - **Consolidación de intereses de targeting detallado**: ad sets con intereses retirados dejan de entregar el 15-ene-2026.
  - Website destination optimization; fin de creación de lead ads de Messenger por API.
  Invalida: "un día malo no gasta más del 125%"; scripts que crean ASC; listas de intereses guardadas.
- **13-oct · Anuncio: el 12-ene-2026 desaparecen 7d_view y 28d_view de Ads Insights API**; unique y hourly limitados a
  13 meses, frequency a 6 meses; breakdowns MMM solo async. OFICIAL (S10-001). (La pista "ene-2025" era incorrecta: es ene-2026.)
- **~oct · Redefinición de clic y engaged-view**: umbral 10 s → 5 s y solo vídeo (imágenes fuera). Observado y documentado por Loomer en oct-2025; Meta lo comunica oficialmente en "Simplifying Ad Measurement for a Social-First World" (3-mar-2026: "we have updated the definition for an engaged view for a video ad from 10 seconds to 5 seconds")
  (S10-028); en mar-2026 se formaliza el gran cambio (link clicks + engage-through).
- **~oct · WhatsApp prohíbe chatbots de IA de propósito general en la Business API** (efectivo 15-ene-2026). OFICIAL/prensa
  (S10-057). Los negocios que usan IA para atención al cliente no se ven afectados.
- **28-oct · Advantage+ catalog ads en Threads** (imágenes y carruseles). **29-oct · métrica `instagram_profile_visits`**. OFICIAL (S10-001).
- **29-oct · Earnings Q3-2025**: Advantage+ end-to-end $60B run-rate; flujo Leads completado; música generada por IA;
  Business AI ampliado a todos los negocios elegibles en México (WA) y Filipinas (Messenger). OFICIAL (S10-017).
- **~oct · Format display options** (carruseles/colecciones desde un solo asset). OBSERVADO (S10-028).

## Noviembre 2025

- **10-nov · Opportunity Score en Marketing API** ("Apply via API"; ampliado a 14 tipos de recomendación en mar-2026).
  OFICIAL (S10-045).
- **10-nov · Post de ingeniería sobre GEM** (foundation model de ranking). OFICIAL (S10-021).
- **11-nov · Se retira el placement de bandeja de Messenger (`messenger_home`)**. OFICIAL (S10-001).
- **~nov · Creative testing tool** (duplicar un anuncio y probar hasta 5 variantes con presupuesto dedicado); **conversion
  count / optimización a primera conversión**; **value rules por dispositivo y por conversion location**; **website +
  instant forms en un mismo anuncio**; virtual try-on y sugerencias de respuesta en formularios en test. OBSERVADO/OFICIAL (S10-028).
- **~6-nov · Reuters: documentos internos estiman que hasta el 10% de los ingresos 2024 procedían de anuncios de estafa o
  productos prohibidos** (Meta lo disputa). Meta acelera la verificación de anunciantes (objetivo 90% de ingresos
  verificados a finales de 2026). Prensa + declaración oficial (S10-065).

## Diciembre 2025

- **8-dic · Acuerdo con la Comisión Europea (DMA)**: desde enero-2026 los usuarios de la UE que elijan la versión con
  anuncios deberán escoger entre anuncios personalizados y **anuncios menos personalizados (LPA)**. OFICIAL/prensa (S10-054).
- **8-dic · `BRAZIL_REGULATION`** (beneficiario/pagador) para ad sets dirigidos a Brasil. OFICIAL (S10-001).
- **16-dic · Entran en vigor las señales de chats con Meta AI** para anuncios (fuera de UE/UK/Corea). OFICIAL/prensa (S10-055).
- **~dic · Breakdowns DMA/Comscore desactivados por defecto; breakdown de value rules; "Spotlights" con Website
  Highlights; Quick Views**. OBSERVADO (S10-028).
- **~dic · Meta compra Manus** (agentes autónomos; >2.000 M$ según prensa). Prensa (S10-062).
- **dic · Investigación antimonopolio de la Comisión y medida cautelar italiana** sobre la exclusión de chatbots rivales en WhatsApp. Prensa (S10-057).

---

## Implicaciones operativas (lo que 2025 dejó obsoleto)

| Práctica antigua | Estado | Desde | Por qué |
|---|---|---|---|
| Elegir ASC vs campaña manual de ventas | **[OUTDATED]** | feb–oct 2025 | Flujo único Advantage+; ASC bloqueada en API v24 |
| Excluir intereses en targeting detallado | **[OUTDATED]** | 31-mar-2025 | Opción eliminada; usar exclusión de custom audiences o controles de cuenta |
| Tope de presupuesto a clientes existentes (ECBC) | **[OUTDATED]** | feb-2025 | Eliminado; workaround con audiencias/Customer Lifecycle (2026) |
| "El presupuesto diario puede pasarse como mucho un 25%" | **[OUTDATED]** | 8-oct-2025 | Flexibilidad del 75% (media semanal) |
| Exclusión dura de placements en Sales/Leads | **[CONTESTED]→[OUTDATED] en curso** | v24 (5%) y test ago-2026 | Soft opt-out y value rules |
| Reportar con 7d/28d view vía API | **[OUTDATED]** | 12-ene-2026 | Ventanas retiradas |
| Offline Conversions API | **[OUTDATED]** | may-2025 | Migrar a CAPI |
| Audiencias/conversiones basadas en URLs de salud/finanzas | **[OUTDATED]** | 2-sep-2025 | Marcadas y bloqueadas |
| Coste WhatsApp "por conversación" | **[OUTDATED]** | 1-jul-2025 | Cobro por mensaje |
| Anuncios políticos/sociales en la UE | **Prohibido** | 6-oct-2025 | TTPA |

## Errores frecuentes al leer 2025

- Confundir la **primera** retirada de targeting detallado (ad sets parados el 15-ene-2025) con la **consolidación de
  intereses de v24** (ad sets parados el 15-ene-2026).
- Fechar en 2025 la retirada de 7d/28d view: se anunció en oct-2025 y entró en vigor el **12-ene-2026**.
- Pensar que "Advantage+ sales" es un renombre de ASC: cambia la estructura (Advantage+ Audience, ad sets ilimitados,
  sin ECBC) y el "estado Advantage+" depende de tres palancas (presupuesto de campaña, audiencia, placements).
- Tomar los anuncios de Cannes como lanzamientos: la mayoría eran tests.

## Preguntas abiertas

- ¿Cuál fue la fecha exacta y el alcance oficial de las restricciones a salud/bienestar de enero-2025? Documentación
  dispersa; contrastar con área 08.
- ¿Qué porcentaje real de anunciantes ve diferencias materiales entre incremental attribution y estándar? (Seer vio
  87% incremental según Meta; Loomer, poca diferencia). Sin datos independientes amplios.

## Fuentes clave

- [2025 Out-of-Cycle Changes](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2025) — 2025 — meta-developers (S10-001)
- [Marketing API v24.0](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog/version24.0) — 2025-10-08 — meta-developers (S10-009)
- [Q2 2025](https://s21.q4cdn.com/399680738/files/doc_financials/2025/q2/META-Q2-2025-Earnings-Call-Transcript.pdf), [Q3 2025](https://s21.q4cdn.com/399680738/files/doc_financials/2025/q3/META-Q3-2025-Earnings-Call-Transcript.pdf) — meta-investors (S10-016, S10-017)
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — 2025-12 — practitioner (S10-028)
- [Meta simplifies Advantage+ campaign setup](https://searchengineland.com/meta-advantage-campaign-setup-leads-campaigns-451713) — 2025-02 — prensa (S10-050)
- [WhatsApp pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — vigente — meta-developers (S10-023)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Engaged-view 10 s → 5 s: la etiqueta "OFICIAL según Loomer" (oct-2025) se matiza. El anuncio oficial que lo documenta es el post de Meta for Business del 3-mar-2026 (leído 2026-10-16); el Help Center actual de engage-through confirma 5 s o 97 % si el vídeo dura menos. Ambas fechas son compatibles: despliegue observado en oct-2025 y comunicación oficial en mar-2026.
