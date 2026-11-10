# Tendencias 2025-2026: qué desaparece, qué automatiza Meta, qué sigue bajo control del anunciante

> Última verificación: 2026-10-15 · Autor: A10 (agente) · Ámbito: lectura estratégica de los cambios 2025-2026 y hacia
> dónde va Meta Ads. Fuentes: `fuentes/ledger-10-cambios-api-ia.md`.

## TL;DR

- **Meta ha sustituido la segmentación por el sistema de recomendación.** Andromeda (retrieval), GEM (foundation model
  de ranking), Lattice (unificación de modelos) y, desde Q2-2026, **Meta Generative Recommender** (LLMs que razonan sobre
  contenido del anuncio + preferencias) deciden a quién se muestra cada anuncio. Meta atribuye a estos modelos mejoras
  trimestrales del 1–15% en conversiones. **[OFFICIAL META]** (S10-016…S10-022)
- **El control del anunciante se ha desplazado de "restricciones" a "inputs y señales"**: creatividad (variedad real),
  oferta, señales de conversión/valor (CAPI, value rules, audience labels), presupuesto, y medición. Las restricciones
  duras (intereses, exclusiones, placements, edad/género) se convierten en sugerencias o ajustes de valor. **[STRONG INFERENCE]**
  con base en la secuencia de cambios oficiales 2025-2026.
- **La automatización "de punta a punta" anunciada por WSJ (jun-2025) para finales de 2026 está a medias**: existe
  Advantage+ end-to-end (>$75B run-rate), generación de imagen/vídeo/texto, asistente con recomendaciones y MCP para
  agentes externos; **no** existe (a 15-oct-2026) un flujo GA de "imagen + presupuesto → campaña completa" ni el asistente
  que crea campañas por chat (está "coming soon"). **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Lo que funciona hoy (consenso practicante 2026)**: estructuras consolidadas, Advantage+ en Sales/App, diversidad
  creativa de conceptos (no microvariantes), CAPI bien implementada y señales de valor, value rules para corregir
  sesgos, y medición incremental (lift/incremental attribution) para cuentas con volumen. **[EMPIRICAL]**
- **Lo que está desapareciendo**: exclusiones de targeting detallado, ASC/ECBC, ventanas 7d/28d view en API, clic "social"
  como click-through, placements manuales en ad sets de Sales/Leads/App (Engagement no; corrección 2026-11-09) (documentado ~12-oct-2026, rollout
  gradual), placements menores (Explore feed, Messenger
  Stories/inbox, FB video feeds), poll ads, checkout nativo en Shops. **[OFFICIAL META]**
- **El precio sube por calidad, no solo por demanda**: precio medio por anuncio +12% interanual en Q1 y Q2-2026, con
  impresiones +19%/+14%. Más inventario de baja monetización (Threads, WhatsApp Status) + más competencia → los CPM de
  FB/IG en mercados ricos suben. **[OFFICIAL META]** para datos; **[STRONG INFERENCE]** para la lectura.
- **Riesgo de marca creciente por defaults de IA**: reescritura de texto en imágenes, música, traducciones, landing pages
  generadas. Meta empuja defaults "on"; el anunciante debe auditarlos. **[EMPIRICAL]**

---

## 1. La tesis de fondo: el sistema de recomendación es el nuevo targeting

### Qué ha dicho Meta (datos oficiales, ordenados)

| Trimestre | Componente | Mejora declarada | Fuente |
|---|---|---|---|
| Q2-2025 | Andromeda (retrieval) ampliado a FB Reels | ~4% más conversiones en FB Feed y Reels | S10-016 |
| Q2-2025 | GEM (ranking) + secuencias más largas | ~5% IG, ~3% FB Feed/Reels | S10-016 |
| Q2-2025 | Lattice en ranking temprano | ~4% conversiones FB Feed/Reels | S10-016 |
| Q3-2025 | Andromeda: retrieval + early ranking en un modelo | +14% calidad de anuncios en FB | S10-017 |
| Q3-2025 | Lattice en app ads | ~3% conversiones | S10-017 |
| Q4-2025 | GEM ×2 GPUs + sequence learning | +3,5% clics FB, >1% conv IG | S10-018 |
| Q4-2025 | Runtime model IG | +3% tasa de conversión | S10-018 |
| Q1-2026 | Lattice + GEM | >6% conversión en anuncios optimizados a LPV | S10-019 |
| Q1-2026 | Adaptive Ranking (LLM-scale en inferencia) a offsite | +1,6% conversión | S10-019 |
| Q2-2026 | Modelos de comprensión de usuario + GEM | +8,3% clics, +15,7% conversiones en FB | S10-020 |
| Q2-2026 | Meta Generative Recommender (LLM en retrieval) | "mejoras notables", sin cifra | S10-020 |
| oct-2026 | GEM central (ingeniería) | +18,9% conversiones, +12% CTR (último año, agregado) | S10-022 |

**Cómo leer estas cifras**: son medias de Meta en sus propios experimentos, no garantías para una cuenta. Son
consistentes en dirección y explican por qué el rendimiento medio de la plataforma mejora mientras el control manual
pierde valor. **[OFFICIAL META]** para las cifras; **[STRONG INFERENCE]** para la implicación.

### Implicación primera-principios

Si el sistema puede estimar para cada impresión la probabilidad de conversión con miles de señales, cualquier restricción
manual (intereses, edad, placement) solo ayuda cuando el anunciante tiene **información que el sistema no tiene**
(márgenes, calidad de lead, restricciones legales, brand safety). Por eso Meta convierte restricciones en **ajustes de
valor** (value rules, ROAS goal, audience labels) y en **sugerencias** (edad/género sugeridos desde v23). El anunciante
gana cuando inyecta información de negocio, no cuando estrecha el inventario. **[STRONG INFERENCE]**

Consecuencia creativa: con Andromeda/GEM, la creatividad funciona como "targeting": anuncios distintos alcanzan
segmentos distintos. Meta lo hace explícito con el **Creative Diversity rating** (ago-2026) y con la retirada de la
recomendación de "máximo 6 anuncios por ad set". **[OFFICIAL META]** (S10-028) + **[EMPIRICAL]** (S10-041).

## 2. Qué está desapareciendo (y desde cuándo)

| Elemento | Estado a 15-oct-2026 | Fecha | Etiqueta |
|---|---|---|---|
| Exclusiones de targeting detallado | Eliminadas | 31-mar-2025 (ad sets), 10-jun-2025 (boosts) | [OUTDATED] |
| Intereses granulares | Consolidados; ad sets antiguos parados | 8-oct-2025 / 15-ene-2026 | [OUTDATED] |
| Advantage+ Shopping (ASC) / App (AAC) | Muertos en API; Advantage+ sales/app | feb-2025 → 19-may-2026 | [OUTDATED] |
| Existing Customer Budget Cap | Eliminado | feb-2025 (ECBC editable hasta v26) | [OUTDATED] |
| Ventanas 7d view / 28d view (API) | Vacías | 12-ene-2026 | [OUTDATED] |
| 28d click para optimizar | Solo comparación | 2025 | [OUTDATED] |
| Click-through con clics sociales | Solo link clicks | 3-mar-2026 | [OUTDATED] |
| Breakdowns device/hourly/frequency sin opt-in | Devuelven vacío | 6-ago-2026 | cambio operativo |
| Placements manuales en ad set (Sales, Leads, App promotion (Engagement no; corrección 2026-11-09)) | Retirándose (rollout gradual); Awareness/Traffic los conservan; quedan exclusiones a nivel cuenta por objetivo | aviso 20-ago; Help Center ~12-oct-2026 | [OFFICIAL META] (S10-093) |
| Exclusión de plataformas/dispositivos/SO en ad set | Mencionada en el aviso de agosto, no en el Help Center | ago-oct 2026 | [CONTESTED] |
| Placements: FB video feeds, Messenger inbox, Messenger Stories, IG Explore feed | Retirados | oct-2025 → oct-2026 | [OUTDATED] |
| Poll ads | Deprecados | 27-oct-2026 (todas las versiones) | [OUTDATED] |
| Checkout nativo en Shops / Commerce Order API | Retirados | jun-ago 2025 / jul-oct 2026 | [OUTDATED] |
| Offline Conversions API | Retirada | may-2025 | [OUTDATED] |
| Nielsen DMA | Sustituido por Comscore Markets | 22-jun-2026 | [OUTDATED] |
| Anuncios políticos/sociales en la UE | Prohibidos | 6-oct-2025 | regulatorio |
| Control "off-Meta activity" (fuera UE) | Retirado | jun/jul-2026 | privacidad |
| Flexible format en Ad setup | Sustituido por multi-media | ~mar-2026 | [OUTDATED] |

## 3. Qué automatiza Meta hoy vs qué controla el anunciante

| Decisión | Quién decide hoy | Palanca del anunciante | Evidencia |
|---|---|---|---|
| A quién mostrar | Meta (Advantage+ Audience por defecto desde v23) | Señales (CAPI, valor), custom audiences como sugerencia, exclusiones de custom/exclusion-only audiences, controles de cuenta, value rules por edad/género/ubicación, audience labels | [OFFICIAL META] |
| Dónde mostrar | Meta (Advantage+ placements; hasta 5% en excluidos vía soft opt-out; sin placements manuales en ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09) desde oct-2026, rollout gradual) | Value rules por placement (−90% máx.), exclusiones de cuenta por objetivo, assets por placement, block lists de brand safety | [OFFICIAL META] (S10-093) |
| Cuánto gastar por día | Meta (75% de flexibilidad diaria; budget sharing 20%) | Presupuesto semanal efectivo, spend caps, reglas | [OFFICIAL META] |
| Cuánto pujar | Meta (lowest cost) | Cost cap, bid cap, ROAS goal (ahora también con volumen), value rules | [OFFICIAL META]/[EMPIRICAL] |
| Qué creatividad servir | Meta (dinámica dentro del ad set, multi-media, flexible) | Conceptos distintos, "push delivery to this ad", creative testing tool | [EMPIRICAL] |
| Variantes creativas | Meta si las mejoras están activadas (texto, imagen, vídeo, música, traducción, reescritura de texto en imagen) | Opt-out por mejora, Branding, palabras restringidas, aprobación | [OFFICIAL META]/[EMPIRICAL] |
| Página de destino | Meta si "optimize website destination" o landing IA (test) | Desactivar; URL fija | [OFFICIAL META] |
| Qué cuenta como conversión | Anunciante (evento, ventana) pero Meta redefine clics y ventanas | Ajustes de atribución (7d/1d click, engage-through on/off, view on/off), incremental attribution, first conversion | [OFFICIAL META] |
| Medición de verdad | Compartida | Conversion Lift, GeoLift/MMM, CRM | [OFFICIAL META]/[EMPIRICAL] |
| Respuesta a conversaciones | Meta Business Agent (si se activa) | Instrucciones, conocimiento, handoff, verticales excluidas | [OFFICIAL META] |

**Lo que sigue siendo 100% del anunciante y define el resultado**: oferta y economía unitaria, calidad y volumen de
creatividad, calidad de la señal de conversión (incluida calidad de lead desde CRM), estructura de presupuesto por
objetivo de negocio, y criterio de medición. **[STRONG INFERENCE]**

## 4. Qué funciona ahora (2026) — con matices

1. **Consolidación + Advantage+ en Sales/App** con suficiente volumen de conversiones. Earnings citan casos (+13% lift
   incremental en compras en Underneat tras pasar a Advantage+ sales + audience + placements + budget, S10-020). **[OFFICIAL META]**
   caso; **[EMPIRICAL]** como patrón general. Matiz: en lead gen sin señal de calidad, Advantage+ Audience optimiza a
   leads baratos → **[CONTESTED]** (Loomer, S10-050).
2. **Diversidad creativa real** (ángulos, formatos, personas, ganchos distintos), no 20 variantes del mismo anuncio. La
   recuperación "Andromeda" premia conceptos diferentes. **[EMPIRICAL]** (S10-028, S10-041).
3. **Señales de valor y calidad**: CAPI server-side, value optimization (run-rate $20B, Q1-2026), conversion leads/CRM,
   audience labels (HIGH_VALUE_CUSTOMERS, QUALIFIED_LEADS). **[OFFICIAL META]** (S10-019, S10-002)
4. **Value rules en vez de exclusiones** para placements de baja calidad (Audience Network en objetivos de tráfico,
   rewarded video en ThruPlay). **[EMPIRICAL]** (S10-030)
5. **Customer Lifecycle Strategy / exclusiones de clientes** para que la adquisición no se coma recompras. **[OFFICIAL META]** (S10-014)
6. **Medir incrementalidad** (incremental attribution con volumen alto; Conversion Lift; partners como Northbeam/Triple
   Whale que incluyen vistas). **[OFFICIAL META]** + **[CONTESTED]** sobre cuánto difiere de la atribución estándar.
7. **Mensajería**: click-to-message (US +40–50% interanual 2025), CTWA (+60% Q3-2025), Website-to-Message. **[OFFICIAL META]**

## 5. ¿Automatización total en 2026? Lanzado vs anunciado

| Pieza del "end-to-end" del WSJ (jun-2025) | Estado a 15-oct-2026 | Fuente |
|---|---|---|
| Advantage+ por defecto en Sales/App/Leads | **Lanzado** (2025) | S10-016, S10-017 |
| Generación de imagen, fondos, expansión, texto | **Lanzado** (adopción image gen ×2 en Q2-2026) | S10-020 |
| Vídeo desde imágenes/estáticos | **GA** (6-oct-2026) | S10-014 |
| Vídeo de producto desde catálogo | **Beta** | S10-014 |
| Modelo de imagen propio (Muse Image) | **Anunciado** (7-jul), no confirmado en cuentas | S10-060 |
| Personalización creativa por usuario | Parcial (variantes servidas dinámicamente; persona-based text) | S10-028 |
| Asistente que recomienda y diagnostica | **Lanzado** (abr-2026) | S10-019, S10-064 |
| Asistente que crea campañas/cambia presupuesto por chat | **Coming soon** (preview + aprobación) | S10-014 |
| Audience discovery en lenguaje natural | **Fin de 2026** | S10-014 |
| Agentes externos (Claude, ChatGPT…) gestionando campañas | **Lanzado en beta** (MCP + CLI; borradores con aprobación) | S10-013, S10-014 |
| "Sube imagen + presupuesto y Meta hace todo" | **No lanzado** como producto | — |

Veredicto: Meta avanza hacia el objetivo por capas, pero mantiene al humano en el bucle de aprobación (drafts, previews,
reglas MCP). **[STRONG INFERENCE]**

## 6. Hacia dónde va (12–18 meses)

- **Agentes como interfaz**: asistente en Ads Manager con memoria, tareas programadas y acciones; agentes externos vía MCP
  con borradores. El trabajo del media buyer se desplaza a definir objetivos, guardrails, creatividad y medición. **[STRONG INFERENCE]**
- **Comercio conversacional y agéntico**: Business Agent con checkout (Shopify en Messenger), Meta AI con checkout
  (Adyen/PayPal/Shopify/Stripe), Muse con comisión por transacción, Personal Agent Protocol. Posible nuevo "canal" donde
  la visibilidad no la compra un anuncio sino la calidad del catálogo/datos estructurados. **[HYPOTHESIS]**
- **Monetización de mensajería por resultados**: Meta dice que tiende a modelos donde "los negocios solo pagan cuando
  conseguimos resultados" (Q2-2026). Hoy: tokens del Business Agent y mensajes. **[OFFICIAL META]** (S10-020)
- **Publicidad en Meta AI**: no hay anuncios en respuestas de Meta AI a 15-oct-2026; Meta usa los chats como señal de
  ranking (desde 16-dic-2025). Que haya inventario patrocinado en Meta AI es plausible pero no anunciado. **[HYPOTHESIS]**
- **Más presión regulatoria en la UE** (LPA, DMA, DSA, TTPA, impuestos digitales repercutidos): señales más pobres y
  costes mayores en Europa. **[STRONG INFERENCE]**

## Implicaciones operativas

- Invertir el tiempo ahorrado en targeting en **producción y análisis creativo** (conceptos, no variantes).
- Construir **pipeline de señales**: CAPI con datos de CRM (calidad de lead, margen, LTV), audience labels, value rules.
- **Política de defaults**: checklist por cuenta de qué mejoras IA están ON/OFF y quién lo aprobó (ver 04).
- **Medición con dos ojos**: Ads Manager (con su nueva definición de clic) + verdad de negocio (CRM/ventas) + test de lift periódico.
- En UE: presupuestar +2–5% de location fees donde aplique y asumir menor personalización.

## Errores frecuentes

- Intentar "recuperar el control" fragmentando en muchos ad sets pequeños: rompe el aprendizaje y no compensa la pérdida
  de restricciones. **[EMPIRICAL]**
- Confundir "Meta automatiza" con "Meta optimiza para tu negocio": optimiza para el evento que le das. Si el evento es
  barato y de baja calidad, la automatización amplifica el problema. **[STRONG INFERENCE]**
- Creer que la automatización total ya existe o, al contrario, que todo es humo: hay piezas en GA, otras en test.

## Preguntas abiertas

- ¿Cuánto del +12% de precio por anuncio es inflación de CPM para el anunciante medio vs mix de inventario? Meta no lo desglosa.
- ¿Qué impacto real tiene Generative Recommender en la importancia de copy/texto del anuncio (señal LLM)? Sin datos.
- ¿Se retirará también el control de placements en Awareness y Traffic, y las exclusiones de plataforma/dispositivo/SO?

## Fuentes clave

- Transcripciones de earnings Q2-2025 → Q2-2026 (S10-016 a S10-020) — meta-investors
- [GEM 2026](https://engineering.fb.com/2026/10/13/ml-applications/metas-generative-ads-model-gem-scaling-the-central-model-and-compute-engine-for-frontier-ads-ai) — 2026-10-13 — meta-engineering (S10-022)
- [Advertising Week New York 2026](https://www.facebook.com/business/news/advertising-week-new-york-2026) — 2026-10-06 — meta-oficial (S10-014)
- [WSJ vía Verdict](https://www.verdict.co.uk/meta-automate-ad-creation/) — 2025-06-02 — prensa (S10-049)
- [83 Changes to Meta Advertising in 2025](https://www.jonloomer.com/meta-advertising-changes-2025/) — practitioner (S10-028)
