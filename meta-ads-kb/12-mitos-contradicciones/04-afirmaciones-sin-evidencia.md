# Afirmaciones muy repetidas sin evidencia (UNPROVEN) y cómo testearlas

> Última verificación: 2026-10-15 · Autor: A12 (agente adversarial) · Ámbito: claims frecuentes en 2025-2026 sin respaldo oficial ni experimento publicado; qué se buscó y diseño de test para validarlas o descartarlas.

## TL;DR

- Hay ~25 afirmaciones con **número concreto** que circulan como si fueran reglas de Meta y que no tienen fuente primaria: umbrales de similitud creativa (60/40%), "Entity ID", "N creatividades por semana", frecuencia 3, EMQ 8, "60% del retargeting no es incremental", "67% de fraude en Audience Network", learning con 10/15/25 eventos, etc. [UNPROVEN]
- **Patrón de contaminación:** un vendor publica una cifra sin metodología → otros blogs la citan → los LLM y cursos la repiten → aparece "en todas partes". Cuantas más fuentes secundarias idénticas, **menos** independiente es la evidencia.
- Varias son **testeables en una sola cuenta** con el A/B test de Meta o con geo-holdout; otras (fin de mes, cuentas nuevas) requieren **paneles multi-cuenta**.
- Prioridad de test para una agencia: (1) incrementalidad de retargeting y de view-through, (2) número de anuncios simultáneos por ad set vs presupuesto, (3) valor del lead por hora (dayparting), (4) efecto real de la diversidad creativa. Son las de mayor impacto económico.

## Cómo se ha buscado

Para cada afirmación: Help Center y developers de Meta (descarga directa de artículos), blog de ingeniería, earnings calls 2025-2026, Jon Loomer, Haus, Motion, CTC, Stella, prensa sectorial (PPC Land, Social Media Today, Search Engine Land), papers (arXiv/INFORMS). **Reddit no fue accesible** desde este entorno (bloqueo del agente), así que el pulso de comunidad viene de citas secundarias. Si una afirmación aparece solo en vendors sin metodología, se marca UNPROVEN.

---

## Catálogo

### U01 · "Meta gasta más / sube CPM a final de mes o trimestre (para cuadrar ingresos)"
- **Quién lo repite:** media buyers en foros y redes; teorías sobre presión de resultados trimestrales.
- **Qué se encontró:** nada publicado con datos. Meta reconoce "ajustes de subasta" genéricos (calidad, test de productos, costes regionales) sin cobrar más que la puja (S12-004). La estacionalidad (Q4, rebajas) es real y confunde.
- **Test:** panel de ≥30 cuentas, 24 meses de CPM y coste por resultado diario vía API; regresión con efectos fijos de cuenta, semana del año y día de la semana + dummies de "últimos 3 días de mes" y "últimos 7 días de trimestre". Decisión: efecto >5% y significativo en ≥2 años → considerar real.

### U02 · "Lanzar a medianoche / evitar fines de semana mejora el arranque"
- **Qué se encontró:** solo el origen histórico (programación antigua); el pacing actual reparte gasto (S12-005, S12-067).
- **Test:** 8-12 lanzamientos idénticos aleatorizados por hora/día en la misma cuenta (A/B de Meta o ad sets gemelos con presupuesto total); comparar coste por resultado acumulado a 7 días. Esperable: sin diferencia fuera de la varianza (ver U17).

### U03 · "El dayparting mejora el CPA"
- **Qué se encontró:** claims de +35-50% ROAS sin metodología; Meta advierte que los breakdowns horarios oscilan y se promedian (S12-011).
- **Test correcto:** primero medir en el CRM el **valor del lead por hora de entrada** (tasa de contacto, cita, cierre). Si difiere >20%, A/B de 4 semanas: ad set 24/7 vs ad set programado (presupuesto total igual), métrica = coste por oportunidad, no CPL.

### U04 · "Los anuncios nuevos reciben un 'boost de novedad' de 1-3 días"
- **Qué se encontró:** vídeos y blogs; ninguna documentación ni dato agregado. Explicación alternativa: exploración inicial + regresión a la media + breakdown effect (S12-015).
- **Test:** con la API, curva de coste por resultado por día de vida de cada anuncio en cientos de anuncios, normalizada por la media del ad set y controlando gasto diario; comparar con anuncios re-lanzados (mismo creativo, nuevo ID). Si la curva de re-lanzados también "sube y cae", es efecto de exploración/estadística, no novedad.

### U05 · "Los comentarios negativos hunden la entrega"
- **Qué se encontró:** Meta solo cita ocultar/reportar como feedback de calidad (S12-004); los diagnósticos no son inputs (S12-022); vendors de moderación dan cifras (+30-40% CPM) sin fuente.
- **Test:** dos anuncios idénticos vía Post IDs distintos; en uno, ocultar sistemáticamente comentarios negativos durante 2 semanas; comparar CPM, CTR, CVR y quality ranking. Separar efecto en el algoritmo (CPM/entrega) de efecto en la persona (CVR).

### U06 · "Pixel seasoning" / "un píxel nuevo rinde mejor"
- **Qué se encontró:** Meta nunca usó el término; Loomer y compradores lo llaman mito (S12-045).
- **Test:** en una marca nueva, dos ad sets optimizados a Purchase desde el día 1 vs "calentamiento" de 2 semanas a LPV y luego Purchase (mismo presupuesto total, 6 semanas); comparar coste por compra acumulado. Para "píxel nuevo", solo tiene sentido si hay contaminación demostrable de eventos.

### U07 · "Las cuentas nuevas sufren un castigo de rendimiento (no solo de límite de gasto)"
- **Qué se encontró:** límites de gasto diario para cuentas nuevas o con problemas (S12-068) y límite de una cuenta por portfolio hasta pago confirmado (S12-024). Nada sobre rendimiento.
- **Test:** imposible de aislar en una sola marca; requiere panel de agencia: misma creatividad/oferta lanzada en cuenta nueva vs cuenta con historial del mismo negocio (cuando legalmente sea posible), 4 semanas.

### U08 · "El EMQ tiene que ser ≥8"
- **Qué se encontró:** Meta pide "Good/Great" en el Help Center y "6,0 o más" en developers (S12-111); el 8 no aparece; el 8,5 es de Offline Data Quality (S12-013).
- **Test:** usar el propio indicador de Meta de "conversiones adicionales reportadas" y comparar coste por resultado antes/después de añadir parámetros (email/teléfono hasheados) con diseño de series temporales interrumpidas + cuenta de control.

### U09 · "Frecuencia > 3 = fatiga" (o "1-2/semana es óptimo")
- **Qué se encontró:** cifras contradictorias en blogs; Meta define fatiga por coste por resultado frente a tu histórico (S12-007).
- **Test:** por ad set de prospecting, regresión de CPA/CTR semanal sobre frecuencia acumulada por creatividad, con efectos fijos de creatividad; buscar punto de inflexión, que será distinto por audiencia y vertical. Nota: breakdowns de frecuencia en API requieren activación y solo 6 meses de retención (S12-052).

### U10 · "Entity ID" y umbrales de similitud ("score >60% suprime retrieval", "mantén <40%")
- **Qué se encontró:** término de la industria, sin documento de Meta; Andromeda no describe deduplicación (S12-026); existe la columna *Creative diversity* (Low/Medium/High), sin porcentajes (S12-058).
- **Test:** ad sets gemelos (mismo presupuesto y audiencia): A con 6 variantes casi idénticas (mismo plano, cambia texto), B con 6 conceptos visualmente distintos; 3-4 semanas, 3 réplicas; medir resultados totales, nº de anuncios con gasto significativo y la columna de diversidad.

### U11 · "Con Andromeda necesitas N creatividades por semana" (10, 20, 50…)
- **Qué se encontró:** Motion muestra correlación volumen→ganadores (con "ganador" definido por gasto) y tasa por creatividad constante (S12-038); Loomer sospecha lo contrario a nivel de ad set (S12-043). Ningún número de Meta.
- **Test:** diseño por bloques en 8-12 semanas: cadencia baja (2/semana) vs media (5) vs alta (10) en mercados/geo comparables, con presupuesto igual; métrica = coste por resultado y MER del mercado, no "ganadores".

### U12 · "Los vídeos largos no funcionan"
- **Qué se encontró:** estudio Meta/Nielsen antiguo (<15 s mejor para promociones) y opiniones; nada 2025-2026 sólido.
- **Test:** mismo guion en 15 s, 30 s y 60-90 s; A/B de Meta con presupuesto igual; métrica = coste por resultado y retención; repetir en 2 ofertas (simple vs compleja).

### U13 · "El 60% de las conversiones de retargeting no son incrementales" / "el retargeting está sobre-reportado un 40-70%"
- **Qué se encontró:** atribuidas a Haus o Measured en blogs; no localicé la fuente primaria. Haus solo publica que el retargeting fue ~15% del gasto en su muestra (S12-031).
- **Test:** conversion lift de Meta o holdout de audiencia (excluir aleatoriamente 20-50% de la audiencia de retargeting) durante 4 semanas; iROAS = (ventas test − control) / gasto.

### U14 · "Audience Network tiene un 67% de tráfico inválido"
- **Qué se encontró:** cifra repetida sin estudio primario localizable; contradicha por otro vendor que dice "100%". Lo consistente es la anécdota de clics de baja calidad con objetivos de clic (S12-069).
- **Test:** con objetivo de conversión, breakdown por placement de tasa de rebote/tiempo en página/conversión post-clic (GA4 + UTMs con `{{placement}}`); con objetivo de tráfico, comparar LPV/clic por placement.

### U15 · "El learning ahora sale con 10 (o 15, o 25) eventos"
- **Qué se encontró:** Madgicx (jun-2024), AdBeacon (ago-2026), Loomer (test temporal "10 en 3 días"); Help Center a 15-oct-2026 sigue en ~50/semana (S12-001, S12-044, S12-050, S12-051).
- **Test:** registrar, por ad set, eventos acumulados desde la última edición significativa en el momento en que la etiqueta pasa de *Learning* a *Active* (API `learning_stage_info` o snapshots diarios). Con 50-100 ad sets se obtiene el umbral empírico por tipo de campaña.

### U16 · "La puntuación de Creative diversity limita cuántos segmentos alcanza ASC / doble penalización en Q4"
- **Qué se encontró:** afirmaciones de una agencia (CTC) explícitamente sin respaldo de Meta (S12-058).
- **Test:** correlacionar la columna con alcance incremental y CPM por ad set en ≥50 ad sets; experimento como U10.

### U17 · "Las diferencias de 10-20% entre dos ad sets en una semana significan algo"
- **Qué se encontró:** Loomer documentó ad sets idénticos con hasta 25% de diferencia en conversiones (S12-046). Esta afirmación implícita (que cualquier diferencia es señal) es la base de muchos mitos.
- **Test:** "A/A test": lanzar 3 ad sets idénticos y medir la dispersión; usarla como umbral mínimo de decisión en la cuenta.

### U18 · "Hay que reiniciar las campañas cada X semanas"
- **Qué se encontró:** nada; Meta diagnostica fatiga por creatividad (S12-007).
- **Test:** cuando una campaña "se cansa", dividir: (A) relanzar copia exacta, (B) mantener y añadir 2 creatividades nuevas, (C) mantener y ampliar audiencia; 3 semanas.

### U19 · "Meta favorece a los anunciantes grandes"
- **Qué se encontró:** sin evidencia de trato preferente; sí más ganadores en cuentas grandes por volumen (S12-038) y límites por página por gasto (S12-010).
- **Test:** no testeable en una cuenta; útil reformular como "¿cuál es el presupuesto mínimo eficiente para mi CPA?" (ver M14).

### U20 · "El cost cap da el mismo volumen con un 15-25% menos de coste"
- **Qué se encontró:** vendors sin metodología; los datos de CTC 2026 muestran que el cost cap entrega ~140% del objetivo de media (S12-036).
- **Test:** A/B de Meta lowest cost vs cost cap (cap = CPA actual × 0,9) 3-4 semanas, presupuesto ≥5× cap; medir volumen y CPA real.

### U21 · "La atribución incremental reporta un volumen entre 1d click y 7d click"
- **Qué se encontró:** cifra de "datos tempranos" citada por un vendor sin fuente (búsqueda sobre IA).
- **Test:** usar "compare attribution settings" en la misma cuenta y periodo; no requiere experimento, solo lectura.

### U22 · "Los formularios higher intent mejoran lead→reunión un 15-25% a cambio de +10-20% CPL"
- **Qué se encontró:** blogs sin fuente; el dato de Meta disponible es −15% de coste por lead cualificado con conversion leads en Advantage+ leads (dato del vendedor) (S12-025).
- **Test:** A/B more volume vs higher intent, 4 semanas, ≥200 leads por brazo; métrica = coste por reunión/oportunidad en CRM.

### U23 · "Las value rules permiten subir hasta +1.000% / bajar hasta −90% / máximo 10 reglas"
- **Resuelto en la revisión adversarial:** el Help Center "About value rules" (535014515741813), citado por las áreas 02 y 09, confirma +1.000 % / −90 %. El número máximo de reglas sigue sin confirmar en fuente oficial.

### U24 · "La prueba social (likes/comentarios) mejora la entrega"
- **Qué se encontró:** plausible vía tasa de conversión del usuario; Meta no la cita como señal de calidad; vendors afirman "Meta agrega aprendizaje por post" sin confirmación (S12-064).
- **Test:** mismo creativo como post nuevo vs post con alta prueba social (Post ID), A/B 2-3 semanas; medir CTR, CVR y CPM por separado.

### U25 · "Desde la actualización de Andromeda de abril de 2026, más ediciones reinician learning y el learning dura 7-14 días"
- **Qué se encontró:** un único blog; sin corroboración ni anuncio de Meta (búsqueda de learning phase 2026).
- **Test:** como U15, comparando la duración media de learning por trimestre en el histórico de la agencia.

## Implicaciones operativas

- Mantener en la base de conocimiento un **registro de claims no verificados** con fecha de primera aparición y fuente; revisarlo cada trimestre.
- Antes de convertir una heurística en SOP, exigir al menos: fuente oficial **o** experimento con control **o** panel multi-cuenta con método descrito.
- Usar A/A tests para conocer el ruido natural de la cuenta (U17): muchos "aprendizajes" no lo superan.

## Errores frecuentes

- Confundir *consistencia entre blogs* con *evidencia independiente*.
- Diseñar tests sin potencia estadística (10-20 conversiones por brazo) y declarar ganadores.
- Testear en Meta con métricas de Meta (ROAS atribuido) preguntas que son de incrementalidad.

## Preguntas abiertas

- ¿Publicará Meta la metodología de la columna *Creative diversity*?
- ¿Hay acceso programático al umbral de salida de learning por ad set para medir U15 a escala?

## Fuentes clave

- [About the learning phase](https://www.facebook.com/business/help/112167992830700) — consultado 2026-10-15 — meta-oficial
- [About creative fatigue recommendations](https://www.facebook.com/business/help/1346816142327858) — consultado 2026-10-15 — meta-oficial
- [Best practices for Conversions API](https://www.facebook.com/business/help/308855623839366) — consultado 2026-10-15 — meta-oficial
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor
- [Haus — The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [CTC — cost controls](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers) — 2026-08-06 — agencia
- Ledger: `../fuentes/ledger-12-mitos-contradicciones.md`

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- U08: Meta sí da un número orientativo (EMQ ≥6,0, developers).
- U23: los límites +1.000 % / −90 % están confirmados en el Help Center (S09-035 / S02-051); queda pendiente el número máximo de reglas.
