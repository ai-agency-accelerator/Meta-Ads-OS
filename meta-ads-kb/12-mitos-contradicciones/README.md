# 12 · Mitos y contradicciones — índice

> Última verificación: 2026-10-16 · Autor: A12 (agente adversarial) · Ámbito: verificación del folklore de Meta Ads contra el Help Center vigente, Meta Engineering/earnings y evidencia empírica (Haus, CTC, Motion, Stella, Loomer, papers); mapa de debates entre expertos.

## Archivos

| Archivo | Qué contiene | Cuándo usarlo |
|---|---|---|
| [01-mitos-meta-ads-2026.md](01-mitos-meta-ads-2026.md) | Tabla maestra de **66 mitos** con veredicto (TRUE/FALSE/CONTEXT-DEPENDENT/OUTDATED/UNPROVEN) + ficha por mito (origen, qué dice Meta hoy, evidencia, contexto, qué hacer) | Antes de aplicar cualquier "regla" de media buying; en auditorías; para formar al equipo |
| [02-contradicciones-entre-expertos.md](02-contradicciones-entre-expertos.md) | 14 debates abiertos (Advantage+ vs manual, learning, volumen creativo, pujas, atribución incremental, ventanas, placements, testing, broad, producción, IA, retargeting, fiabilidad del reporting) y en qué contexto acierta cada postura | Cuando dos fuentes serias dicen lo contrario |
| [03-folklore-obsoleto-por-era.md](03-folklore-obsoleto-por-era.md) | Qué era cierto en 2015-2019, 2020-2021, 2022-2023, 2024, 2025 y 2026, y qué cambio lo dejó obsoleto (con fechas) | Auditar cuentas "arqueológicas" y cursos/SOPs antiguos |
| [04-afirmaciones-sin-evidencia.md](04-afirmaciones-sin-evidencia.md) | 25 claims UNPROVEN muy repetidos, qué se buscó y diseño de test para validarlos | Priorizar experimentos; filtrar contenido de vendors |
| [05-revision-adversarial-kb.md](05-revision-adversarial-kb.md) | **Revisión adversarial de toda la base (16-oct-2026)**: 35 hallazgos con archivo:línea, resolución de 16 discrepancias con fuente primaria, áreas abiertas, features omitidas y 20 correcciones propuestas para 00-*, 13-* y 15-* | Antes de usar 00-ESTADO/13 como verdad; lista de correcciones pendientes |
| [../fuentes/ledger-12-mitos-contradicciones.md](../fuentes/ledger-12-mitos-contradicciones.md) | 119 fuentes (~40 artículos del Help Center y páginas de developers leídos completos) | Trazabilidad |

## TL;DR

0. **Revisión adversarial (16-oct-2026):** la base es sólida en lo estratégico. Los errores eran de fechas, de etiquetas y de documentación oficial desfasada. Corregidos en las áreas: WhatsApp (7 días y 1.000 gratis no son oficiales; la doc dice 72 h y sin franquicia), ratio de Haus invertido (04/13), exclusiones de detailed targeting (01), AEM 2023 (06), requisitos de qualified leads (02/04/10). Pendiente de aplicar por el agente principal: 20 cambios en 00-*, 13-* y 15-* → [05](05-revision-adversarial-kb.md) §E. (Actualización 2026-11-09: lo de WhatsApp se revierte; la doc oficial de precios ya recoge los 7 días y los 1.000 gratis, S10-118.)

1. **Learning phase = etiqueta de estabilidad, no castigo.** Umbral oficial: ~50 resultados en la semana posterior a la última edición significativa; "Learning limited no es una penalización". Los rumores de 10/15/25 eventos no están confirmados en el Help Center (15-oct-2026). [OFFICIAL META]
2. **No existe la "regla del 20%"** en la documentación: Meta habla de magnitud (100→101 no; 100→1.000 puede). [OFFICIAL META]
3. **Fragmentar cuesta más que editar:** Meta pide combinar ad sets, usar breakdowns y evitar volúmenes altos de anuncios; duplicar ganadores crea solapamiento de subasta (aunque tus anuncios no pujan entre sí). [OFFICIAL META]
4. **Advantage+ no "siempre gana":** Meta publica mejoras medias (−7,2% a −14,8% CPR con Advantage+ audience; −10% con Advantage+ placements); Haus encuentra que gana en incrementalidad solo en el 42% de las marcas. [CONTESTED]
5. **Andromeda es retrieval, no "el algoritmo".** La diversidad creativa importa (Meta lo dice desde abr-2025 y hay columna *Creative diversity* desde ago-2026), pero "Entity ID", umbrales de similitud y "N creatividades por semana" no tienen respaldo. [OFFICIAL META] + [UNPROVEN]
6. **"Meta sobre-reporta todo" es falso como universal:** click-only infra-reporta un 15% de media en Haus; Advantage+ sobre-reporta más que manual; la única forma de saberlo en una cuenta es un experimento. [EMPIRICAL]
7. **El cost cap no es un control de precisión:** CTC 2026 → cost per result goal ~140% del objetivo; min ROAS ~96,5%. [EMPIRICAL]
8. **2026 cambió definiciones:** sin 7d/28d view en API (12-ene), click-through solo enlace + engage-through (mar), placements manuales retirados en objetivos de conversión (despliegue 2026), hasta 5% de gasto en placements excluidos (desde oct-2025). [OFFICIAL META]
9. **Cifras sin dueño:** frecuencia 3, CTR >1%, EMQ >8, "3-6 anuncios", "60% del retargeting no incremental", "67% fraude en AN", "score de similitud 60%": todas UNPROVEN.

## Para la revisión adversarial del resto de la base (lista de vigilancia)

Afirmaciones que otras áreas probablemente estén repitiendo y que hay que comprobar:

- "Necesitas 50 conversiones/semana **o no funciona**" (es umbral de etiqueta, no de rendimiento) y "Meta bajó el umbral a 10/25".
- "Regla del 20%" o cualquier porcentaje fijo de escalado.
- "Advantage+ siempre rinde más" / "ASC solo retargetea".
- "Andromeda agrupa por Entity ID", "score de similitud >60%", "8-15 anuncios por ad set es guía de Meta", "necesitas 20-50 creatividades".
- "3-6 anuncios por ad set" (recomendación retirada en 2025).
- "Frecuencia >3 = fatiga" (Meta usa coste por resultado vs histórico).
- "EMQ ≥8" (Meta pide Good/Great y recomienda ≥6,0 en developers; 8,5 es de Offline Data Quality).
- "Excluye Audience Network / elige placements en el ad set" (ya no posible en Sales/Leads/App (Engagement no; corrección 2026-11-09)).
- "Si excluyes un placement no gastas ahí" (opción del 5% por defecto).
- "View-through es falso" o "7d view disponible".
- "Click-through incluye cualquier clic" (cambio mar-2026).
- "El cost cap controla el CPA".
- "Pixel seasoning", "píxel nuevo", "cuentas nuevas castigadas", "lanzar a medianoche", "dayparting mejora el CPA".
- Cifras de retargeting no incremental y de fraude de AN sin fuente primaria.
- Cualquier cifra cuyo único origen sea un vendor sin metodología (comprobar el ledger de cada área).

## Preguntas abiertas (prioridad para experimentos)

1. ¿Umbral real de salida de learning por tipo de campaña en 2026? (medible con snapshots de `learning_stage_info`).
2. ¿Añadir anuncios a un ad set activo reinicia learning? Documentación (sí) vs observación 2025 (a menudo no).
3. ¿Cómo se calcula la columna *Creative diversity* y si influye en la entrega?
4. ¿Qué parte del view-through/engage-through de 1 día es incremental por vertical?
5. ¿Se mantiene fuera de DTC la mejora de la atribución incremental (1,26× en Haus 2025-26)?
6. ¿Cuántos anuncios simultáneos por ad set son óptimos controlando presupuesto?
7. ~~Fechas no verificadas~~ resueltas en la revisión: +75 % anunciado el 29-may-2025 y formalizado en la API v24 el 8-oct-2025; AEM web sin 8 eventos desde mayo de 2023.
8. Nuevas abiertas tras la revisión: default real de atribución en ad sets web; FEP de WhatsApp de 7 días y franquicia de 1.000 (solo BSPs); deterioro de rendimiento sep-oct-2026 reportado en Reddit; cálculo de la columna Creative diversity. (2026-11-09: la de WhatsApp queda resuelta a favor de los 7 días y los 1.000 gratis, S10-118.)

## Limitaciones de esta investigación

- Reddit no accesible directamente; en la revisión adversarial se usó el archivo Arctic Shift (S12-113) para muestrear hilos de sep-oct-2026.
- Artículos completos de jonloomer.com bloqueados (Cloudflare): se usaron extractos de búsqueda y su Pubcast.
- El Help Center no muestra fechas de publicación; las fechas de cambios proceden de prensa sectorial, changelogs y Loomer.
- Haus, Motion, CTC, Stella y Agentio son empresas con interés comercial; sus datos se usan con esa etiqueta y nunca como única base de un veredicto TRUE/FALSE sin contraste.
