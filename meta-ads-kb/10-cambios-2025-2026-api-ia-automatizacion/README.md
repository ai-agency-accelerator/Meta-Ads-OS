# Área 10 — Cambios 2025-2026, Marketing API, IA nativa de Meta y automatización

> Última verificación: 2026-11-09 (revisión de octubre–noviembre, B21; la anterior, 2026-10-15) · Autor: A10 (agente) · Ledger: `../fuentes/ledger-10-cambios-api-ia.md` (143 fuentes,
> IDs `S10-###`) · Convenciones: `../00-CONVENCIONES.md`

## Índice

| Archivo | Contenido |
|---|---|
| [01-changelog-2025.md](01-changelog-2025.md) | Cambios de 2025 mes a mes (fecha, alcance, confirmación, impacto, práctica invalidada) |
| [02-changelog-2026.md](02-changelog-2026.md) | Cambios de 2026 (ene → 9-nov) + calendario de fechas próximas |
| [03-tendencias-que-desaparece-que-controla-meta.md](03-tendencias-que-desaparece-que-controla-meta.md) | Qué desaparece, qué automatiza Meta, qué controla el anunciante, qué funciona, hacia dónde va |
| [04-ia-nativa-meta-advantage-creative-genai.md](04-ia-nativa-meta-advantage-creative-genai.md) | Inventario de Advantage+ creative/genAI y asistentes (GA/beta/test/anunciado) |
| [05-business-ai-y-agentes.md](05-business-ai-y-agentes.md) | Business AI → Meta Business Agent, precios WhatsApp 2025-2026, comercio agéntico |
| [06-marketing-api-versiones-y-automatizacion.md](06-marketing-api-versiones-y-automatizacion.md) | Versiones v22–v26, deprecaciones, Insights, rate limits, qué se automatiza, MCP oficial |
| [07-reglas-automaticas.md](07-reglas-automaticas.md) | Reglas útiles vs dañinas, marco estadístico, plantillas, API de reglas |
| [08-automatizacion-externa-n8n-make-sheets-slack-bi.md](08-automatizacion-externa-n8n-make-sheets-slack-bi.md) | Arquitecturas de reporting, alertas, QA, CRM→CAPI, agentes, riesgos |
| [09-ia-para-nuestro-workflow.md](09-ia-para-nuestro-workflow.md) | IA fuera de Meta: research, angle/comment mining, guiones, competencia, análisis, guardrails |
| [10-como-vigilar-cambios.md](10-como-vigilar-cambios.md) | Fuentes, método de verificación, cadencia y automatización del seguimiento |

## TL;DR del área

1. **El sistema de recomendación de Meta (Andromeda + GEM + Lattice + Generative Recommender) es el nuevo targeting**;
   Meta declara mejoras de conversión trimestrales del 1–15% y +18,9% en el último año (GEM, oct-2026). **[OFFICIAL META]**
2. **El control manual se transforma en ajustes de valor y señales**: sin exclusiones de intereses (mar-2025), Advantage+
   Audience por defecto (v23), sin placements manuales en ad sets de Sales/Leads/App (Engagement no; corrección 2026-11-09) (Help Center ~12-oct-2026,
   gradual), a cambio de value rules, audience labels, exclusion-only audiences y Customer Lifecycle Strategy. **[OFFICIAL META]**
3. **La medición se redefinió**: 7d/28d view fuera de la API (12-ene-2026); click-through = link clicks y nueva
   engage-through de 1 día (3-mar-2026); incremental attribution como opción (2025). Hay que re-baselinar KPIs. **[OFFICIAL META]**
4. **Advantage+ unificado y ASC muerto**: flujo único Sales/App/Leads (2025); ASC/AAC bloqueados en todas las versiones de
   API desde el 19-may-2026; >$75B de run-rate (Q2-2026). **[OFFICIAL META]**
5. **IA creativa masiva y con defaults activados**: 9 M de pymes con IA creativa; vídeo desde estáticos GA (6-oct-2026);
   reescritura de texto en imágenes ON por defecto (~jul-2026, observado); Muse Image anunciado, no confirmado. **[OFFICIAL META]**/[EMPIRICAL]
6. **Agentes**: MCP oficial + CLI (beta abierta 29-abr-2026, abierto a cualquier app 16-jul, borradores con aprobación
   6-oct); el asistente de Ads Manager recomienda y diagnostica, pero sus acciones agénticas siguen "coming soon". **[OFFICIAL META]**
7. **La "automatización total para finales de 2026" (WSJ) no se ha lanzado como producto**; existen piezas. **[STRONG INFERENCE]**
8. **Mensajería monetizada**: WhatsApp por mensaje (jul-2025), Business Agent por tokens (ago-2026), service messages
   cobrados (oct-2026). **[OFFICIAL META]**
9. **Costes y regulación**: location fees 2–5% en 6 países (jul-2026), LPA en la UE (ene-2026), fin de anuncios políticos
   en la UE (oct-2025), restricción política EE. UU. 27-oct→3-nov-2026, veto a anuncios de ByteDance/TikTok en 7 países
   (8-oct-2026). **[OFFICIAL META]**/prensa
10. **API: 27-oct-2026** es la fecha a vigilar (retiradas de v26 en todas las versiones). Marketing API v24 expiró el 6-oct. **[OFFICIAL META]**
    **Corrección 2026-11-09**: la v24 expira el **10-nov-2026**; la **v27.0 salió el 4-nov-2026** (expansión de dispositivos
    por defecto en Ventas, `lookalike_spec` sin ubicación, product showcase por defecto; todo en todas las versiones a
    ~90 días). Novedades de oct–nov: audiencia por creativo, desglose por asset, medición en el dispositivo (12-nov),
    condiciones con términos de IA suspendidas. Ver [02-changelog-2026.md](02-changelog-2026.md). **[OFFICIAL META]**

## Cambios 2025-2026 más importantes (priorizados)

1. **3-mar-2026 — Click-through solo link clicks + engage-through (1 d) + engaged-view 5 s** (S10-015).
2. **Feb-2025 → 19-may-2026 — Advantage+ unificado; ASC/AAC eliminados; ECBC eliminado** (S10-050, S10-009, S10-003).
3. **12-ene-2026 — Fin de 7d_view/28d_view en Ads Insights API; límites de histórico 13/6 meses** (S10-001).
4. **ago→oct-2026 — Fin de placements manuales en ad sets (Sales/Leads/App (Engagement no; corrección 2026-11-09))** (S10-030, S10-093).
5. **8-oct-2025 — API v24: flexibilidad de presupuesto diario 75%, soft opt-out 5%, consolidación de intereses** (S10-009).
6. **29-abr/16-jul/6-oct-2026 — Meta Ads AI Connectors (MCP + CLI), reglas MCP, borradores** (S10-013, S10-014).
7. **Q2-2025 → oct-2026 — IA creativa a escala (vídeo desde estáticos GA; image gen ×2; defaults ON)** (S10-016…S10-020, S10-014).
8. **31-mar-2025 — Fin de exclusiones de targeting detallado** (S10-034).
9. **abr-2025 — Incremental attribution** (S10-016, S10-018).
10. **2-sep-2025 — Restricciones de audiencias/conversiones con datos de salud/finanzas** (S10-066, S10-009).
11. **jul-2025 / ago-2026 / oct-2026 — WhatsApp: cobro por mensaje, Business Agent por tokens, service messages cobrados** (S10-023, S10-024).
12. **Ene-2026 (UE) — Nueva elección de anuncios menos personalizados; 6-oct-2025 — fin de anuncios políticos en la UE** (S10-054, S10-001).
13. **1-jul-2026 — Location fees (UK 2%, FR/IT/ES 3%, AT/TR 5%)** (S10-053).
14. **jun-2025 / ene-2026 — Nuevos inventarios: WhatsApp Status, Threads global** (S10-056, S10-048).
15. **6-ago-2026 — Breakdowns device/hourly/frequency solo con opt-in (vacío sin error)** (S10-002).

## Contradicciones y afirmaciones que otras áreas deben contrastar

- **Área 04 (tracking/atribución)**: (a) la retirada de 7d/28d view es de **ene-2026**, no ene-2025; (b) desde mar-2026 la
  ventana por defecto es 7d click + 1d engage-through + 1d view, y el 28d click solo sirve para comparar; (c) el umbral de
  engaged-view es 5 s; (d) incremental attribution: Meta dice +24% incrementales vs estándar, practicantes ven poca
  diferencia → **[CONTESTED]**.
- **Área 02/09 (estructura, bidding)**: flexibilidad diaria del **75%** (no 25%); ROAS goal ya combinable con maximizar
  conversiones (observado jul-2026); 4 cambios de presupuesto/hora por ad set en API.
- **Área 07 (placements/mensajería)**: el "fin de exclusiones de placements" afecta a ad sets de Sales/Leads/App (Engagement no; corrección 2026-11-09)
  (Awareness y Traffic conservan manual); exclusiones de plataforma/dispositivo/SO sin confirmar. Explore feed, Messenger
  Stories y Messenger inbox ya no son placements. WhatsApp: la ventana FEP oficial es **72 h** (no 7 días) y la doc oficial
  **no** recoge "1.000 service messages gratis". **Corrección 2026-11-09**: la página de precios releída ya dice "hasta 7 días" para CTWA y 1.000 service messages gratis por número y mes (S10-118).
- **Área 08 (políticas)**: "DMA deprecation" en algunos blogs = **Nielsen DMA** (geografía), no la Digital Markets Act;
  verticales excluidas del Business Agent (finanzas, salud, alcohol, juego…); nuevas condiciones 30-oct-2026 (detalle solo
  en terceros); veto a anuncios que enlazan a TikTok (sin página de política).
- **Área 06 (ecommerce)**: fin del checkout en Shops (2025) y de la Commerce Order Management API (v26); Shop ads por
  defecto WEBSITE_AND_SHOP en v26; "product browsing" ON por defecto desde 28-oct (aviso, sin doc pública).
- **Área 01 (subasta/ML)**: Meta dice que Generative Recommender usa LLMs en retrieval (Q2-2026); el post de ingeniería GEM
  de oct-2026 no menciona Andromeda ni Generative Recommender → la arquitectura exacta es inferencia de terceros.
- **Área 03 (creatividad)**: Meta dejó de recomendar "máx. 6 anuncios por ad set"; Creative Diversity rating "estimado y en
  desarrollo"; reescritura de texto en imágenes por defecto (riesgo de marca).
- **Área 05 (lead gen/CRM)**: requisitos oficiales de Conversion Leads (≥200 leads/mes, etapa ≤28 días, tasa 1–40%,
  subida diaria, Lead ID).
- **Fechas mal citadas en la web**: varias fuentes fechan v25 en 2025 (es 18-feb-2026); la retirada de targeting detallado
  tuvo dos olas (15-ene-2025 y 15-ene-2026).

## Huecos y preguntas abiertas (del área)

- ¿Muse Image está activo en Advantage+? ¿Qué modelo reescribe hoy el texto de las imágenes?
- Texto final de las condiciones del 30-oct-2026 (tests sin aviso, responsabilidad sobre contenido IA, scraping).
- Lista oficial y estable de herramientas del MCP de Meta; cuota de rate limit que consume.
- Fecha de expiración de Marketing API v25 y llegada de v27.
- Impacto medido de LPA en el rendimiento en la UE (Meta no publica adopción).
- Fecha y alcance oficial de las restricciones a salud/bienestar de enero-2025.
- Si la retirada de placements se extiende a Awareness/Traffic y a plataformas/dispositivos/SO.
- Evidencia independiente sobre Ads Creative Studio, Brand Memory, vídeo generativo y Business Agent (todo lo publicado
  son claims de Meta o casos elegidos).
- No se pudo acceder a Reddit directamente (bloqueado); la señal comunitaria se ha obtenido de forma indirecta.

## Fuentes clave

Ver `../fuentes/ledger-10-cambios-api-ia.md`. Las más usadas: S10-001/002 (OCC 2025/2026), S10-003/004 (v25/v26),
S10-013/014/015 (AI connectors, Ad Week, atribución), S10-016…S10-020 (earnings), S10-028/029/030 (Jon Loomer).
