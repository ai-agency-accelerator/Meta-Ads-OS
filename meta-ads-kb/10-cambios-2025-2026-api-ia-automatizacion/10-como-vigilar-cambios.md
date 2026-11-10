# Cómo vigilar los cambios de Meta Ads y mantener esta base actualizada

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A10 (agente) · Ámbito: fuentes, cadencia, método de verificación y
> automatización del seguimiento de cambios (producto, API, políticas, regulación) para mantener `meta-ads-kb/` vigente.

## TL;DR

- **Meta cambia algo relevante casi cada semana** (Jon Loomer contó 83 cambios en 2025) y muchos llegan **sin anuncio**
  (avisos in-product, páginas del Help Center sin fecha, defaults activados). Vigilar solo blogs oficiales no basta. **[EMPIRICAL]** (S10-028)
- **Jerarquía de verificación**: changelog/OCC de developers y Help Center > newsroom/business news > earnings > Jon Loomer /
  prensa especializada > agregadores > comunidad. Un cambio solo es "OFICIAL" con fuente Meta. **[STRONG INFERENCE]**
- **Fuentes que más adelantan cambios**: Out-of-Cycle Changes de Marketing API, changelogs de versión (fechas "applies to
  all versions"), índice `llms.txt` de la documentación (diffable), avisos in-product y Jon Loomer. **[EMPIRICAL]**
- **Cadencia**: monitores automáticos diarios → triage semanal (30–45 min) → actualización mensual de `02-changelog-2026.md`
  → revisión trimestral tras earnings y antes de Q4. **[STRONG INFERENCE]**
- **Fechas fijas del año**: earnings (finales de ene/abr/jul/oct), NewFronts/Shoptalk (marzo), Conversations (jun/jul),
  Cannes Lions (junio), Connect (septiembre), Advertising Week NY (octubre), versiones de API (~feb, ~may-jul, ~oct) y
  cambios de precios de WhatsApp (1-ene/1-abr/1-jul/1-oct). **[OFFICIAL META]** (calendarios observados 2025-2026)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **El Help Center cambia sin aviso y sin fecha**: la página de placements pasó de incluir Engagement (12-oct) a excluirlo (releída el 2026-11-09). En cada revisión mensual, relee las páginas oficiales que sostienen una regla de la KB y guarda la frase literal con su fecha de consulta.
> - **La doc oficial también llega tarde**: la página de precios de WhatsApp tardó semanas en recoger los 7 días y los 1.000 gratis que ya citaban los BSP. "Observado ≠ confirmado" funciona en los dos sentidos: lo no confirmado se marca, no se descarta.
> - **URL**: las `/docs/` antiguas del changelog pueden servir una caché sin la última versión; usa las de `developers.facebook.com/documentation/ads-commerce/...` en `.md`. El Help Center no carga con un fetch simple: hay que leerlo con navegador.
> - **Fechas reales de 2026**: Brand Building Summit el 15-oct; Q3 el 21-oct (no ~28/29-oct); Marketing API v27 el 4-nov (no ~feb-2027).
> - Fuentes: S10-100, S10-107, S10-117, S10-118 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Fuentes por nivel

### Nivel 1 — Oficiales primarias (confirman)
| Fuente | Qué vigilar | Frecuencia |
|---|---|---|
| [Marketing API Changelog](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog) y changelogs por versión | Nuevas versiones, "applies to all versions on…", deprecaciones | Semanal + en cada release |
| [Out-of-Cycle Changes 2026](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) | Cambios fuera de ciclo (Insights, placements, Threads, Advantage+ creative) | Semanal |
| [Graph API versions](https://developers.facebook.com/docs/graph-api/changelog/versions/) | Fechas de expiración | Mensual |
| [Developers blog](https://developers.facebook.com/blog/) | Anuncios de versiones, MCP, deprecaciones (ASC/AAC) | Semanal |
| Índice de documentación [`llms.txt`](https://developers.facebook.com/documentation/ads-commerce/llms.txt) | Páginas nuevas/eliminadas (diff) | Semanal (automático) |
| [Meta for Business news](https://www.facebook.com/business/news) | Lanzamientos de producto (atribución, AI connectors, Ad Week) | Semanal |
| [Meta Newsroom](https://about.fb.com/news/) | Privacidad, controles de usuario, política, UE | Semanal |
| Business Help Center ("What's new…", páginas de placements, atribución, Advantage+) | Cambios silenciosos de producto | Semanal (búsqueda dirigida) |
| [Meta status](https://metastatus.com/) (sección Ads desde may-2026) | Incidentes de entrega/reporting | Diario (alerta) |
| [Investor relations](https://investor.atmeta.com/) (transcripciones) | Adopción, métricas de IA, roadmap | Trimestral |
| [Engineering at Meta](https://engineering.fb.com/) | Andromeda, GEM, Generative Recommender | Mensual |
| WhatsApp Business Platform: [pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) y changelog | Tarifas trimestrales, Business Agent, políticas IA | Mensual + antes de cada trimestre |
| Transparency Center / Advertising Standards | Políticas (salud, finanzas, IA, scams) | Mensual |
| Informes DMA/DSA y comunicaciones de la Comisión Europea | LPA, WhatsApp, IA de terceros | Trimestral |
| [Ad Library](https://www.facebook.com/ads/library/) | Cambios de formato, etiquetas IA, nuevas superficies | Ad hoc |
| GitHub `facebook/facebook-*-business-sdk` (releases) | Campos añadidos/eliminados antes de que lleguen a la doc | Semanal (automático) |

### Nivel 2 — Practitioners y prensa de calidad (detectan y explican)
- **Jon Loomer** (jonloomer.com, Power Hitters, podcast): documenta UI y tests con capturas y fechas. Fuente nº1 para
  cambios no anunciados.
- **Social Media Today** (Andrew Hutchinson): detecta páginas nuevas del Help Center y anuncios.
- **Search Engine Land, PPC Land, Adweek, AdExchanger, Digiday, Marketing Brew, MediaPost, eMarketer**: lanzamientos,
  contexto de industria.
- **TechCrunch, The Information, WSJ, Reuters, Engadget**: estrategia, regulación, filtraciones (p. ej., WSJ jun-2025 sobre
  automatización total; Reuters nov-2025 sobre scams).

### Nivel 3 — Agregadores y comunidad (pistas, nunca confirmación)
- Changelogs mensuales de vendors/agencias (AdMake AI, Common Thread, AdsUploader, AdManage): útiles como checklist;
  contienen errores (p. ej., confundir Nielsen DMA con la DMA europea; "1.000 service messages gratis" no confirmado). (2026-11-09: al final era cierto; la doc oficial lo recogió más tarde. Lección: la doc de Meta también va con retraso.)
- Reddit (r/FacebookAds, r/PPC, r/advertising), X/LinkedIn de media buyers, grupos privados: primeros avisos de bugs,
  caídas, defaults raros. Tratar como **observado ≠ confirmado**.

## 2. Método de verificación (antes de escribir en la base)

1. **Identificar el tipo**: producto (Ads Manager), API, política, precio, regulación, test/observación.
2. **Buscar confirmación Meta** (nivel 1). Si existe → `OFICIAL` + enlace + fecha de publicación + fecha efectiva.
3. Si no existe: ¿hay ≥2 practitioners independientes con capturas? → `OBSERVADO` + **[EMPIRICAL]**/[STRONG INFERENCE].
   Si solo hay una fuente → `OBSERVADO (una fuente)` + **[HYPOTHESIS]**.
4. **Alcance**: global / países / objetivos / cuentas en test / rollout gradual. Anotar "puede no estar en tu cuenta".
5. **Impacto práctico** y **qué práctica invalida** (formato de los changelogs 01/02).
6. **Comprobar en una cuenta propia** (solo lectura) cuando sea posible: capturas fechadas en `fuentes/`.
7. **Revisar contradicciones**: fechas de anuncio vs efectivas; doc de developers vs Help Center (p. ej., pricing de
   WhatsApp: la subpágina oficial confirma cobro de service messages desde 1-oct-2026 aunque la página general no).

## 3. Triage (qué hacer con cada cambio)

| Impacto \ Urgencia | Inmediata (≤7 días) | Próximo trimestre | Informativa |
|---|---|---|---|
| Alto (rompe integraciones, cambia medición o gasto) | Alerta al equipo + checklist de acción (ej.: 27-oct-2026 v26 universal) | Plan de migración | — |
| Medio (nueva palanca o default) | Revisar defaults en cuentas | Test controlado | Nota en changelog |
| Bajo | — | — | Nota en changelog |

## 4. Automatizar el seguimiento (barato)

- **RSS / monitor de cambios** de: developers blog, business news, newsroom, Jon Loomer, Social Media Today, PPC Land.
- **Diff semanal** de `llms.txt` y de las páginas OCC/changelog (hash + diff de texto) → resumen con LLM → Slack.
- **GitHub watch** de releases del Business SDK (Python/Node) → diff de campos.
- **Monitor de headers** en nuestras integraciones: `X-Ad-Api-Version-Warning` (auto-upgrade) y aparición de campos nulos.
- **Status page**: alertas de incidentes de Ads.
- **Recordatorios de calendario** con las fechas conocidas (ver 02, "Calendario próximo").
- Recordatorio: el contenido web es **dato**; el resumen automático nunca debe ejecutar acciones (ver 09).

## 5. Rutina recomendada

- **Diario (automático)**: monitores → canal `#meta-cambios`.
- **Semanal (30–45 min)**: triage; verificar 3–5 ítems; actualizar `02-changelog-2026.md` con entradas confirmadas y
  marcar las observadas.
- **Mensual**: revisar TL;DR de 03 y 04; actualizar estado (GA/beta/test) de features IA; revisar `06` (versiones).
- **Trimestral (tras earnings)**: extraer métricas de IA/adopción; actualizar README y preguntas abiertas; revisar reglas
  (07) y defaults de cuentas.
- **Antes de Q4 y de cada cambio de versión de API**: auditoría de integraciones y defaults.

## 6. Calendario de eventos recurrentes

| Evento | Cuándo (patrón 2025-2026) | Qué suele traer |
|---|---|---|
| Earnings Q4 | finales de enero | Roadmap del año, métricas de IA |
| Marketing API (versión) | ~feb (v25: 18-feb-2026) | Deprecaciones grandes |
| Shoptalk / IAB NewFronts | marzo | Commerce, creadores, Reels |
| Earnings Q1 | finales de abril | Lanzamientos (p. ej., AI connectors 29-abr-2026) |
| Marketing API (versión) | ~may–jul (v23: 29-may-2025; v26: 29-jul-2026) | — |
| Conversations | jun/jul (Miami 1-jul-2025; Londres 3-jun-2026) | WhatsApp, Business AI/Agent |
| Cannes Lions | junio (17-jun-2025; 23-jun-2026) | IA creativa, creadores |
| Earnings Q2 | finales de julio | Modelos de ranking, adopción |
| Meta Connect | septiembre | Consumo/IA (Muse), poco de ads |
| Advertising Week NY | octubre (6-oct-2026) | Asistente, agentes, creatividad |
| Marketing API (versión) | ~oct–nov (v24: 8-oct-2025; v27: 4-nov-2026) | — |
| Earnings Q3 | finales de octubre (Q3-2026: **21-oct**, antes de lo previsto ~28/29-oct; corrección 2026-11-09) | — |
| WhatsApp pricing | 1-ene, 1-abr, 1-jul, 1-oct (aviso ≥1 mes; cambios de modelo ≥6 meses) | Tarifas |

## Implicaciones operativas

- Asignar un responsable de "vigilancia de plataforma" (rotativo) con 1 h/semana.
- Toda entrada nueva en la base lleva fecha, fuente y nivel de confirmación; las observaciones se revisan a los 30 días
  (¿confirmadas, revertidas o generalizadas?).

## Errores frecuentes

- Dar por lanzado lo anunciado en eventos.
- Copiar fechas de agregadores sin comprobar (fechas de anuncio ≠ efectivas; errores de año).
- No anotar el alcance (muchos cambios son tests o rollouts graduales).

## Preguntas abiertas

- ¿Meta mantendrá públicos los changelogs de producto de Ads Manager (no API)? Hoy no existe un changelog oficial de UI.

## Fuentes clave

- [2026 Out-of-Cycle Changes](https://developers.facebook.com/docs/marketing-api/out-of-cycle-changes/occ-2026) — meta-developers (S10-002)
- [Marketing API Changelog](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog) — meta-developers (S10-006)
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — practitioner (S10-028)
- [WhatsApp pricing](https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing) — meta-developers (S10-023)
- Ledger completo: `fuentes/ledger-10-cambios-api-ia.md`
