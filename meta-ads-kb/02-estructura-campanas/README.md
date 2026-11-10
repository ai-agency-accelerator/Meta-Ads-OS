# Área 02 — Estructura de campañas, objetivos, eventos, learning, presupuesto, audiencias y Advantage+

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ledger: [`../fuentes/ledger-02-estructura-campanas.md`](../fuentes/ledger-02-estructura-campanas.md) (119 fuentes; 69 del Help Center/Developers de Meta descargadas y leídas directamente)

## Índice

| Archivo | Qué responde |
|---|---|
| [01-objetivos-campana-2026.md](01-objetivos-campana-2026.md) | Los 6 objetivos, conversion locations, performance goals, qué optimiza cada uno, cuándo sí/no |
| [02-eventos-de-optimizacion.md](02-eventos-de-optimizacion.md) | Qué evento elegir; volumen vs proximidad al dinero; qué pasa al optimizar mal; CRM, value, custom |
| [03-learning-phase.md](03-learning-phase.md) | Umbral oficial vigente, significant edits, learning limited, rumores de umbrales nuevos, cuánto importa |
| [04-business-portfolio-activos-estructura-cuenta.md](04-business-portfolio-activos-estructura-cuenta.md) | Portfolio, activos, permisos, límites, varias ad accounts, qué vive en campaña/ad set/anuncio |
| [05-arquitectura-de-campanas.md](05-arquitectura-de-campanas.md) | Patrones de arquitectura y matriz de decisión por presupuesto/volumen/modelo/país/evento/creatividad |
| [06-presupuesto-por-niveles.md](06-presupuesto-por-niveles.md) | Mecánica oficial del gasto y recomendaciones para 50-100 €, 500 €, 5.000 € y 50.000 €/día |
| [07-audiencias-2026.md](07-audiencias-2026.md) | Controles vs sugerencias vs restricciones vs value rules; DT, LAL, custom audiences, labels, segments |
| [08-advantage-plus-ecosistema.md](08-advantage-plus-ecosistema.md) | Cada producto Advantage+, cronología 2022-2026, API v24-v26, problemas reportados |
| [09-retargeting-duplicacion-exclusiones.md](09-retargeting-duplicacion-exclusiones.md) | Retargeting separado sí/no, exclusiones de clientes, duplicación y overlap |
| [10-cuenta-nueva-vs-heredada.md](10-cuenta-nueva-vs-heredada.md) | Arranque sin histórico; auditoría y limpieza de cuentas heredadas tras los cambios 2025-2026 |

## TL;DR del área (cómo razona un Head of Performance en 2026)

1. **La decisión estructural más importante es el evento de optimización, no el número de ad sets.** El performance goal es lo que se puja; el objetivo de campaña es un menú. Elige el evento más cercano al dinero que alcance volumen útil. **[OFFICIAL META]** + **[STRONG INFERENCE]**
2. **Umbral de learning oficial sin cambios: ~50 resultados en la semana posterior a la última significant edit** (Shops ads: 17+5). Los "25 para Advantage+" o "10 para Purchase" no tienen respaldo oficial. **[OFFICIAL META]** / **[HYPOTHESIS]**
3. **Consolidar es el default; separar exige una razón demostrada** (economía distinta, objetivo distinto, restricción legal, garantizar inversión, test con potencia). Cada ad set extra multiplica el presupuesto necesario (~50 × CPA/semana). **[OFFICIAL META]** + **[EMPIRICAL]**
4. **Advantage+ es un estado (campaign budget + Advantage+ audience + Advantage+ placements), no un tipo de campaña**; desde 2025 es el arranque por defecto en Sales/Leads/App. Es buen default operativo, pero la evidencia independiente (Haus, 640 geo-tests) no lo respalda como superior en incrementalidad para todas las marcas. **[OFFICIAL META]** + **[EMPIRICAL]** → medir.
5. **Targeting en 2026 = controles (duros) + sugerencias (blandas) + value rules (precio por segmento)**. Separar ad sets por intereses/lookalikes ya no aísla audiencias. Segmenta solo con información que Meta no tiene, y preferentemente vía value rules/exclusiones. **[OFFICIAL META]** + **[EMPIRICAL]**
6. **El remarketing ya ocurre dentro de la prospección** (≈10-40 % del gasto según cuenta); la campaña de retargeting separada es una excepción con propósito, audiencia restringida y holdout. **[EMPIRICAL]**
7. **Daily budget = media semanal**: hasta 175 % un día, ≤7× por semana dom-sáb (210 %/8,4× con budget sharing). Reglas oficiales: presupuesto diario ≥10× coste del goal; con cost per result goal ≥5× el objetivo; value optimization con ≥50 conversiones/semana. **[OFFICIAL META]**
8. **Cambios 2025-2026 que cualquier cuenta heredada debe absorber**: exclusiones de DT eliminadas, intereses consolidados (corte 15-ene-2026), ECBC retirado, ASC/AAC legacy bloqueados (v25) y pausados (v26), lookalikes countryless, qualified leads exige CAPI, attribution (link click; engage-through 1 d), value rules sustituyen a bid multipliers (2027). **[OFFICIAL META]**
9. **Separar ad accounts no evita competir contra uno mismo** (Meta identifica al anunciante; límite de anuncios por Página compartido; learnings ligados a la Página). **[OFFICIAL META]**
10. **"It depends" tiene variables concretas**: presupuesto/CPA (eventos por semana por ad set), modelo de negocio (compra única vs recompra; online vs CRM), heterogeneidad de mercados, calidad de señal, volumen creativo, y si mides incrementalidad. **[STRONG INFERENCE]**

## Cambios 2025-2026 detectados (con fecha)

| Fecha | Cambio | Etiqueta |
|---|---|---|
| 2025-02 (≈7-feb) | Anuncio ASC → Advantage+ sales; Advantage+ leads | [EMPIRICAL] (prensa) |
| 2025-03-31 | Exclusiones de detailed targeting eliminadas en Ads Manager (boosts: 10-jun-2025) | [OFFICIAL META] |
| 2025 (≤jun) | Existing customer budget cap retirado de la UI | [OFFICIAL META] (fecha exacta discrepante) |
| 2025-05/06 | Flujo unificado con Advantage+ on por defecto (Sales/App/Leads) | [EMPIRICAL] |
| 2025-05-22 | Value rules disponibles | [EMPIRICAL] |
| 2025-06 | Opportunity score global; campaign score | [EMPIRICAL] + [OFFICIAL META] |
| 2025-06-23 | Consolidación de intereses (campañas antiguas sin corregir dejan de entregar 15-ene-2026) | [OFFICIAL META] |
| 2025-07 | LPV disponible con problemas de pixel; ad set budget sharing visible; renombre "Advantage" → "Advantage+" | [OFFICIAL META] + [EMPIRICAL] |
| 2025-09/10 | Añadir anuncio no siempre reinicia learning (observado) | [EMPIRICAL] |
| 2025-10-06 | Lookalikes no restringibles en 9 goals | [EMPIRICAL] |
| 2025-10-08 | API v24: no se crean ASC/AAC legacy | [OFFICIAL META] |
| 2025-10/11 | Limited spend en placements excluidos (≤5 %); conversion count All/First (sin doc) | [OFFICIAL META] / [EMPIRICAL] |
| 2026-01 | Less personalized ads en la UE | [STRONG INFERENCE] (prensa) |
| 2026-02-18 | API v25: ASC/AAC no se crean ni actualizan; ECBC fuera; todas las versiones 19-may-2026 | [OFFICIAL META] |
| 2026-02 | Meta deja de prometer "priorizar" sugerencias | [EMPIRICAL] |
| 2026-03 | Atribución: click = link click; engage-through 1 d; nuevo default | [EMPIRICAL] |
| 2026-04 | Qualified leads exige CAPI (nuevas); Customer lifecycle strategy en beta | [OFFICIAL META] / [EMPIRICAL] |
| 2026-06 | "Legal and operational exclusions"; App install status; page likes goal retirado en algunas cuentas | [EMPIRICAL] |
| 2026-07-16 | Audiences rediseñado en torno a labels; value rules con audience labels | [EMPIRICAL] + [OFFICIAL META] |
| 2026-07-29 | API v26: pausa ASC/AAC restantes; lookalikes countryless (todas las versiones 1-sep-2026); fuera Explore Feed y Messenger Stories | [OFFICIAL META] |
| 2026-08 | Exclusion-only custom audiences; existentes con qualified leads sin CAPI afectadas; test de quitar exclusiones de placement en ad sets Sales/Leads | [OFFICIAL META] / [EMPIRICAL] |
| 2026-09 | Meta One (suscripciones con soporte) | [EMPIRICAL] |
| 2026-10 | Sequenced events (test); exclusión automática de compradores 730 d en "Acquire new customers" | [EMPIRICAL] |

## Contradicciones y afirmaciones para contrastar con otras áreas

- **Área 01 (subasta/ML)**: cuánto "aprendizaje" se transfiere entre ad sets/cuentas/dataset/Página; si existe umbral de learning distinto por tipo de campaña (rumores 2026). Aquí se trata como no verificado.
- **Área 03 (creatividad)**: CTC habla de "150 ads per ad set"; la API documenta 50. Revisar si existe el límite ampliado. También el impacto real de Advantage+ creative enhancements y de Muse Image (jul 2026).
- **Área 04 (medición)**: cambios de atribución de marzo 2026 y cambio de métrica de impresión a "media view" (jul 2026) afectan a comparativas y a qué cuenta para el learning; Haus dice que Incremental Attribution ahora supera a la estándar (nota editorial jul 2026), lo que invierte su hallazgo de 2025.
- **Área 05 (lead gen)**: desalineación Developers (conversion leads solo instant forms) vs Help Center (qualified leads también web) y sequenced events.
- **Área 09 (bidding/escalado)**: "rolling budget" (Foxwell) no encontrado en documentación; patrón CTC de presupuestos inflados + cost controls; Foxwell observó gasto concentrado antes del mediodía con caps.
- **Área 12 (mitos)**: "regla del 20 %" (no oficial), "50 conversiones/semana obligatorias" (guía, no requisito), "broad siempre gana" (CONTESTED), "duplicar para escalar" (FALSE), "cuentas nuevas rinden más" (HYPOTHESIS), "calentar la cuenta con engagement" (sin evidencia).
- **Área 08 (cuentas/seguridad)**: riesgo y escrutinio de cuentas nuevas; uso legítimo de cuentas de respaldo.

## Preguntas abiertas del área

1. ¿Se mantienen los resultados de Haus (manual > Advantage+ en iROAS en el 58 % de marcas) con el Advantage+ de 2026 (multi-ad set, CLS, value rules) y Andromeda/GEM? Falta un estudio 2026 con método publicado.
2. ¿Meta tiene umbrales de learning diferenciados por tipo de campaña? Sin evidencia oficial.
3. ¿Qué hace Customer lifecycle strategy además de excluir ("specialized treatments")?
4. ¿Tienen efecto medible las sugerencias de audiencia en 2026?
5. ¿Cuándo se generalizará la eliminación de exclusiones de placement a nivel de ad set y la eventual desaparición de lookalikes como input?
6. Umbral práctico a partir del cual un evento profundo con poco volumen supera a un proxy con mucho volumen (requiere experimento propio).
7. Adopción de "less personalized ads" en la UE y su efecto en CPM/CPA y en retargeting en España/UE.
8. Confirmación oficial de "rolling budget", "push delivery" y "sequenced events".

## Recomendaciones de Meta sobre simplificación (verificación de la pista "Performance 5")

- "Performance 5" fue un marco de Meta publicado en junio de 2023: simplificar la cuenta, automatizar (Advantage+), diversificar creatividad, Conversions API, medir con conversion lift/MMM/A-B. **[OFFICIAL META]** vía prensa ([Social Media Today, 2023-06-06](https://www.socialmediatoday.com/news/meta-new-tips-maximize-ad-campaign-performance/652231/)). No se ha encontrado una página vigente con ese nombre en 2026.
- Su equivalente operativo actual está repartido en: Advantage+ campaign experience por defecto, opportunity score/campaign score (recomendaciones "experimentally proven", incluida la de combinar ad sets fragmentados), "About managing ad volume" y "Combine ad sets". **[OFFICIAL META]**
