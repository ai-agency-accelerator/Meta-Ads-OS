# Mitos de Meta Ads verificados (edición 2026)

> Última verificación: 2026-10-15 · Autor: A12 (agente adversarial) · Ámbito: folklore operativo de Meta Ads (learning phase, presupuesto, estructura, audiencias, creatividad/Andromeda, pujas, medición, placements, cuenta/píxel, lead gen) contrastado con documentación oficial vigente y evidencia empírica 2025-2026.

## TL;DR

- **El learning phase es una etiqueta de estabilidad, no un castigo.** Meta sigue diciendo "unos 50 resultados en la semana posterior a la última edición significativa" y que *Learning limited* "no es una penalización". Lo que de verdad cuesta dinero es la fragmentación (muchos ad sets con poco volumen), no tocar una campaña. [OFFICIAL META] (S12-001, S12-003)
- **La "regla del 20%" está obsoleta como regla.** El Help Center habla de magnitud ("100→101 no; 100→1.000 puede"), no de un porcentaje; con Advantage+ campaign budget el propio presupuesto de campaña puede reactivar learning en varios ad sets. Gradualidad sí; dogma del 20% no. [OFFICIAL META] + [EMPIRICAL] (S12-002, S12-039)
- **"Meta sobre-reporta todo" es falso como enunciado universal.** En 640 experimentos de Haus, la atribución 7-day click *infra*-reportó el impacto incremental un 15% de media; Advantage+ sobre-reportó ~12 pp frente a manual; el retargeting es donde más se sospecha sobre-atribución, pero esa cifra concreta no está demostrada públicamente. [EMPIRICAL] (S12-031, S12-032)
- **"Advantage+ siempre gana a manual" es falso.** Meta reporta mejoras medias (p. ej. Advantage+ audience −7,2% coste por resultado en ventas; Advantage+ placements −10% en experimento), pero en tests de incrementalidad Advantage+ ganó a manual solo en el 42% de las marcas. [OFFICIAL META] vs [EMPIRICAL] → [CONTESTED] (S12-020, S12-012, S12-031)
- **Andromeda no "castiga" creatividades parecidas: las trata como redundantes.** Lo oficial: Meta escribe que "cuando la creatividad es demasiado parecida, nuestro sistema puede no reconocerla como distinta y entregarla a los mismos públicos" (página *creative differentiation*); Andromeda es la fase de *retrieval* (de decenas de millones de anuncios a unos miles); desde agosto de 2026 Ads Manager muestra una columna "Creative diversity" (Low/Medium/High, *estimated, in development*). "Entity ID", umbrales de similitud y "necesitas 50 creatividades" no tienen respaldo oficial. [OFFICIAL META] + [UNPROVEN] (S12-105, S12-026, S12-058)
- **Los placements manuales ya no son una opción en la mayoría de objetivos de conversión.** Meta está retirando la selección manual de placements a nivel de ad set en Sales, Leads y App promotion (Engagement no; corrección 2026-11-09) (despliegue gradual, 2026); quedan *placement value rules* y exclusiones a nivel de cuenta. Desde oct-2025 Meta además puede gastar hasta un 5% por placement excluido si no desmarcas la casilla. [OFFICIAL META] (S12-012, S12-053)
- **El cost cap no "mata la escala", pero no cumple el objetivo que pones.** CTC (253 cuentas, $200M analizados, mar-2025 a jul-2026): el *cost per result goal* entregó ~140% del objetivo; *min ROAS* ~96,5%; bid cap ~123% (muestra pequeña). [EMPIRICAL] (S12-036, S12-037)
- **Frecuencia >3, CTR >1%, EMQ >8, "3-6 anuncios por ad set", "50 creatividades", "píxel sazonado", "lanzar a medianoche"**: ninguna de estas cifras tiene respaldo oficial ni evidencia publicada sólida. Son heurísticas útiles en algún contexto, no reglas. [UNPROVEN] / [OUTDATED]
- **2026 cambió la medición:** desde el 12-ene-2026 la API ya no devuelve ventanas 7d_view ni 28d_view; desde marzo de 2026 el *click-through* solo cuenta clics en enlace y el resto pasa a *engage-through* (1 día; vídeo 5 s). Comparar ROAS "antes/después" sin ajustar ventanas es un error metodológico. [OFFICIAL META] (S12-009, S12-052, S12-054)

## Cómo leer este archivo

- **Veredictos:** TRUE / FALSE / CONTEXT-DEPENDENT / OUTDATED / UNPROVEN. "FALSE" significa falso *en la formulación que circula*; muchas veces hay un núcleo verdadero que se explica en la ficha.
- **Etiquetas de evidencia:** según `00-CONVENCIONES.md`. Cuando cito el Help Center, el texto se descargó y leyó el 2026-10-15 (los artículos de ayuda de Meta no muestran fecha de publicación; se indica "consultado").
- **IDs de fuente (S12-###)** → `fuentes/ledger-12-mitos-contradicciones.md`.
- **Regla de esta área:** una cifra que solo aparece en blogs de vendors que se citan entre sí se trata como no verificada, aunque esté en 20 blogs.
- **Orden:** las fichas M63-M65 (cambios de medición 2026) están dentro del Bloque F por tema; M66 en el Bloque J.

## Tabla maestra

| # | Mito (formulación que circula) | Veredicto | Resumen en una línea | Fuente clave |
|---|---|---|---|---|
| M01 | "Nunca toques una campaña en learning" | CONTEXT-DEPENDENT | Evita ediciones innecesarias, pero no congeles un ad set que está quemando dinero; el learning es etiqueta, no castigo. | S12-001, S12-039 |
| M02 | "Necesitas 50 conversiones por semana" | CONTEXT-DEPENDENT | ~50 resultados/semana *por ad set* es el umbral oficial para salir de learning, no para obtener resultados; hubo tests de 10 eventos/3 días no confirmados. | S12-001, S12-044, S12-050 |
| M03 | "Learning limited es fatal" | FALSE | Meta: "no es una penalización"; es un diagnóstico de volumen (presupuesto, audiencia, puja, solapamiento, evento raro). | S12-003 |
| M04 | "Cualquier cambio de presupuesto resetea el learning" | FALSE | Depende de la magnitud; cambios pequeños no; con Advantage+ campaign budget la redistribución entre ad sets no lo resetea. | S12-002 |
| M05 | "Regla del 20%: nunca subas más de un 20%" | OUTDATED | Heurística de 2017-2020 sin respaldo oficial actual; Meta habla de magnitud y Loomer documenta subidas mayores sin re-learning. | S12-002, S12-049 |
| M06 | "Apagar/encender anuncios resetea el learning" | CONTEXT-DEPENDENT | Solo es edición significativa pausar el **ad set** ≥7 días; pausar un anuncio no está en la lista oficial (pero cambia la delivery). | S12-002 |
| M07 | "Editar un anuncio resetea el learning y pierde la prueba social" | CONTEXT-DEPENDENT | Cambiar la creatividad sí es edición significativa; la prueba social normalmente se transfiere al editar (con excepciones). | S12-002, S12-064 |
| M08 | "Añadir un anuncio a un ad set ganador lo destroza" | CONTEXT-DEPENDENT | Oficialmente es edición significativa; desde 2025 practitioners observan que a menudo no reinicia learning. | S12-002, S12-039, S12-040 |
| M09 | "El algoritmo necesita 3 días antes de juzgar" | CONTEXT-DEPENDENT | Meta recomienda analizar al menos una semana completa; el número correcto depende de volumen de eventos y retraso de conversión. | S12-011 |
| M10 | "Duplica los ganadores" | OUTDATED (como táctica por defecto) | Duplicar crea solapamiento de subasta y nuevo learning; útil solo para cambiar algo que no se puede editar. | S12-008, S12-016 |
| M11 | "CBO siempre gana a ABO" (o al revés) | CONTEXT-DEPENDENT | CBO reduce riesgo de infra-entrega; ABO sirve para pujas/audiencias muy distintas; el *budget sharing* (20%) difumina la frontera. | S12-014, S12-018 |
| M12 | "Un ad set por audiencia" | OUTDATED | Meta recomienda combinar ad sets y usar breakdowns para reporting. | S12-016 |
| M13 | "Escalar siempre mata el rendimiento" | FALSE | El coste marginal sube al escalar (oficial), pero "matar" depende de margen, creatividad y puja. | S12-011 |
| M14 | "Meta favorece presupuestos grandes / con poco presupuesto no funciona" | FALSE | No hay evidencia de favoritismo; con poco presupuesto el problema es estadístico (pocos eventos), no de trato. | S12-017 |
| M15 | "Hay que reiniciar campañas cada X semanas" | UNPROVEN | No hay mecanismo documentado de "envejecimiento" de campaña; sí hay fatiga creativa medible. | S12-007 |
| M16 | "Meta gasta más de mi presupuesto diario (me roba)" | FALSE | Diseño documentado: hasta +75% en un día, nunca >7× el diario en la semana. | S12-014 |
| M17 | "Meta frena el gasto / gasta más a final de mes o trimestre" | UNPROVEN | Ninguna evidencia publicada; la estacionalidad de CPM (Q4) sí existe. | — |
| M18 | "Lanza a medianoche / no lances en fin de semana" | UNPROVEN (origen OUTDATED) | Venía de limitaciones antiguas de programación; el pacing actual reparte el gasto. | S12-067, S12-005 |
| M19 | "El dayparting mejora resultados" | UNPROVEN | Solo con presupuesto total; Meta advierte que los breakdowns horarios oscilan y se promedian. | S12-011 |
| M20 | "Usa siempre broad" | CONTEXT-DEPENDENT | Advantage+ audience rinde mejor de media según Meta, pero Meta no lo recomienda para retargeting y hay nichos donde las restricciones son de negocio. | S12-020 |
| M21 | "Los intereses ya no funcionan" | FALSE (en absoluto) | Hoy funcionan sobre todo como sugerencias; en tests de Loomer, diferencias no significativas frente a Advantage+. | S12-021, S12-046 |
| M22 | "El lookalike 1% es el mejor" | OUTDATED | Lookalikes se expanden por defecto en muchos objetivos y en tests pierden contra Advantage+ audience. | S12-040, S12-046 |
| M23 | "Las campañas de retargeting son obligatorias" | FALSE | Advantage+ ya incluye remarketing; ~15% del gasto va a retargeting en la muestra de Haus; su incrementalidad suele ser menor. | S12-031 |
| M24 | "Excluye siempre a los compradores" | CONTEXT-DEPENDENT | Correcto para captación pura y productos de compra única; incorrecto para recompra, suscripción o cuando te importa el negocio total. | S12-031, S12-048 |
| M25 | "Advantage+ Sales (ASC) solo retargetea a tus clientes" | FALSE (riesgo real) | En Haus, 70% del impacto de Advantage+ fue de clientes nuevos (vs 65% manual); hay que medirlo con segmentos de audiencia. | S12-031, S12-029 |
| M26 | "Advantage+ siempre gana a manual" | FALSE | Meta publica mejoras medias; Haus: Advantage+ gana en el 42% de los head-to-head y su iROAS medio fue 12% menor. | S12-031, S12-020 |
| M27 | "La creatividad es el nuevo targeting" (versión absoluta) | CONTEXT-DEPENDENT | Meta (abr-2025) dice que el foco pasó a la diversificación creativa; pero ubicación, exclusiones, evento y oferta siguen definiendo a quién llegas. | S12-047 |
| M28 | "Necesitas 3-6 anuncios por ad set" / "muchos anuncios perjudican" | OUTDATED / CONTEXT-DEPENDENT | Meta retiró en 2025 la recomendación de ≤6; sigue diciendo que demasiados anuncios reducen el aprendizaje por anuncio. | S12-006, S12-043 |
| M29 | "Con Andromeda necesitas 50 creatividades (o 20+/semana)" | FALSE / UNPROVEN | Ningún documento de Meta fija un número; más volumen = más ganadores en Motion, pero la tasa de acierto no cambia. | S12-038, S12-043 |
| M30 | "Andromeda castiga las creatividades similares (Entity ID)" | CONTEXT-DEPENDENT | Meta confirma que creatividades demasiado parecidas pueden no reconocerse como distintas y entregarse al mismo público (no es un castigo); "Entity ID" y umbrales de similitud no son oficiales. | S12-105, S12-026, S12-058 |
| M31 | "Andromeda es el nuevo algoritmo / cambió la subasta" | FALSE | Andromeda es *retrieval*; la subasta sigue siendo valor total = puja × tasas estimadas + calidad. | S12-026, S12-004 |
| M32 | "Meta odia los anuncios duplicados / compites contra ti mismo" | FALSE (parcialmente) | No pujas contra ti mismo: solo entra tu anuncio de mayor valor total; el coste real es fragmentar aprendizaje y entrega. | S12-008 |
| M33 | "Los estáticos están muertos" | FALSE | En Motion 2026, "text only" y "product image with text" lideran tasa de acierto. | S12-038 |
| M34 | "El UGC siempre gana" | FALSE | UGC está en la parte alta, no en la cima; depende de vertical. | S12-038 |
| M35 | "Los vídeos largos no funcionan" | UNPROVEN (evidencia débil en contra) | El único dataset 2026 encontrado (421 anuncios) no ve relación entre duración y coste por resultado (±6 %); la retención importa más que la duración. | S12-119 |
| M36 | "Los anuncios nuevos reciben un 'boost' de novedad" | UNPROVEN | Explicable por exploración/explotación; no hay documentación ni test público. | — |
| M37 | "Frecuencia > 3 = fatiga" | FALSE (como regla) | Meta define fatiga por coste por resultado frente a tu histórico (≥2× = *Creative fatigue*), no por frecuencia. | S12-007 |
| M38 | "El CTR tiene que ser > X%" | FALSE | No hay umbral oficial; los CTR medios varían ×4 entre sectores y objetivos. | S12-063, S12-004 |
| M39 | "Las creatividades con IA rinden peor" | CONTEXT-DEPENDENT / [CONTESTED] | Estudio con 16.000 M de impresiones: igualan o superan si no "parecen IA"; estudio Ipsos con 20 anuncios dice lo contrario. | S12-059, S12-060 |
| M40 | "Las mejoras de Advantage+ creative siempre ON (u OFF)" | CONTEXT-DEPENDENT | Meta reportó −4% CPR (test 2022) con standard enhancements; el riesgo es de marca y de mensaje, no de rendimiento medio. | S12-030, S12-040 |
| M41 | "Usar el Post ID siempre conserva la prueba social" | CONTEXT-DEPENDENT | Funciona con anuncios de un solo post; formatos dinámicos/multimedia generan variaciones y no siempre consolidan. | S12-064 |
| M42 | "Meta castiga los anuncios con comentarios negativos" | UNPROVEN | Lo oficial es que ocultar/reportar el anuncio baja la calidad; los comentarios no aparecen como señal explícita. | S12-004 |
| M43 | "Lowest cost siempre es lo mejor" | CONTEXT-DEPENDENT | Buen punto de partida; con objetivos de margen, min ROAS cumplió mejor el objetivo en el dataset de CTC. | S12-036, S12-037 |
| M44 | "Los bid caps son solo para expertos" | FALSE (como tabú) | Son exigentes (pueden no gastar), pero CTC los usa por defecto como control de coste. | S12-036 |
| M45 | "El cost cap mata la escala" | CONTEXT-DEPENDENT | Puede infra-entregar si el cap es bajo; y además se pasa del objetivo ~40% de media. | S12-036, S12-011 |
| M46 | "CPM alto = mala audiencia" | FALSE | Meta: si optimizas a conversión, el sistema puede pagar CPM más altos para bajar el coste por conversión. | S12-011 |
| M47 | "Las conversiones view-through son falsas" | CONTEXT-DEPENDENT | Parte es incremental (click-only infra-reporta de media), parte no; hoy solo existe 1-day view. | S12-009, S12-031 |
| M48 | "Meta sobre-reporta todo" | FALSE (universal) | Depende de campaña, embudo y canal: infra-reporta prospecting/upper funnel, sobre-reporta más Advantage+ y probablemente retargeting. | S12-031, S12-032, S12-035 |
| M49 | "El EMQ tiene que ser > 8" | UNPROVEN | Meta recomienda "6,0 o más" (developers) y "Good" o "Great" (Help Center); el 8 no tiene respaldo. | S12-111, S12-013 |
| M50 | "Con server-side (CAPI) solo es suficiente" | FALSE | Meta recomienda configuración redundante píxel + CAPI con deduplicación y ≥75% de cobertura CAPI/píxel. | S12-013 |
| M51 | "Los UTMs rompen el tracking" | FALSE | UTMs y fbclid son independientes; lo que rompe es una redirección que elimina parámetros. | S12-062 |
| M52 | "La atribución incremental de Meta siempre es mejor (o peor)" | [CONTESTED] | Haus: 0,80× (jul-24/jun-25) → 1,26× (jul-25/jun-26) frente a estándar; muestra modesta. | S12-033 |
| M53 | "Quality ranking bajo te penaliza en la subasta" | FALSE | Meta: los diagnósticos de relevancia "no son inputs de la subasta"; son espejo de los componentes que sí lo son. | S12-022 |
| M54 | "Un Opportunity score alto = buen rendimiento" | FALSE | Meta lo dice textualmente: no refleja ni garantiza rendimiento. | S12-007, S12-016 |
| M55 | "Los placements manuales rinden mejor" | FALSE (en general) | Advantage+ placements: −10% coste por resultado en experimento de Meta; el "breakdown effect" explica la ilusión. | S12-012, S12-015 |
| M56 | "Audience Network es pura basura" | CONTEXT-DEPENDENT | Con objetivos de clic/LPV/ThruPlay suele traer tráfico malo; con optimización a conversión el sistema lo valora por resultado. | S12-069, S12-042 |
| M57 | "Si excluyo un placement no gasto ahí" | OUTDATED | Desde oct-2025, opción por defecto de gastar hasta 5% por placement excluido (Sales/Leads); en 2026 desaparecen exclusiones por ad set. | S12-053, S12-012 |
| M58 | "Un píxel nuevo / fresco funciona mejor" | UNPROVEN | Ningún mecanismo documentado; perder historial de eventos es un coste, no una ventaja. | S12-045 |
| M59 | "Hay que 'sazonar' el píxel" | UNPROVEN | Meta nunca ha usado el término; optimizar a clics para "calentar" puede enseñar al sistema a buscar clicadores. | S12-045 |
| M60 | "Las cuentas nuevas son castigadas / necesitan warm-up" | CONTEXT-DEPENDENT | Los límites de gasto de cuentas nuevas existen; un castigo de rendimiento no está demostrado. | S12-068, S12-024 |
| M61 | "Abrir otra página/cuenta evita límites y rinde más" | FALSE | Meta: las páginas compiten en las mismas subastas y se dividen los aprendizajes. | S12-010, S12-008 |
| M62 | "Los leads de formulario instantáneo siempre son malos" | FALSE | La calidad depende de fricción del formulario y de optimizar a etapas del CRM (qualified leads: −21 % coste por lead de calidad en instant forms con CAPI CRM, según Meta). | S12-083, S12-025 |
| M63 | "El click-through incluye cualquier clic (likes, comentarios...)" | OUTDATED | Desde marzo de 2026 solo cuenta clics en enlace; el resto es engage-through (1 día). | S12-009, S12-054 |
| M64 | "Si una métrica de Ads Manager no cuadra con GA4, Meta miente" | FALSE | Modelos, ventanas, deduplicación y fechas distintos (Meta reporta las conversiones web por fecha de conversión y las acciones en el anuncio por fecha de impresión); comparar requiere homogeneizar. | S12-009 |
| M65 | "Las ventanas 7d/28d view siguen disponibles en informes y API" | OUTDATED | Retiradas de la Ads Insights API desde el 12-ene-2026. | S12-052 |
| M66 | "Los partnership ads (creadores) siempre ganan" | CONTEXT-DEPENDENT | Meta: −19% CPA y +13% CTR de media; white paper oct-2026 (20 lift studies EMEA) −45% coste por compra incremental; vendor independiente: solo −5% CPA vs UGC licenciado. | S12-071, S12-072 |

---

## Fichas detalladas

Formato de cada ficha: **Formulación** (tal como circula) · **Origen** · **Qué dice Meta hoy** · **Evidencia empírica** · **Veredicto** · **Cuándo podría ser cierto** · **Qué hacer**.

### Bloque A — Learning phase y ediciones

#### M01 · "Nunca toques una campaña mientras está en learning"

- **Formulación:** "Si tocas algo durante el learning lo reseteas; espera siempre 7 días sin hacer nada."
- **Origen:** 2018-2020, cuando Meta empezó a mostrar el estado *Learning* y a listar las ediciones significativas. Se convirtió en dogma de agencia para evitar que clientes y juniors "tocaran" a diario.
- **Qué dice Meta hoy (consultado 2026-10-15):** recomienda "esperar a editar el ad set hasta que salga del learning" y "editar solo cuando tengas motivos para creer que la edición mejorará el rendimiento"; a la vez dice que el learning "es necesario" y que "no deberías intentar evitarlo por completo" porque testear creatividad es esencial. [OFFICIAL META] (S12-001)
- **Evidencia empírica:** Jon Loomer (15-oct-2025) defiende que es "solo una etiqueta", que "el algoritmo siempre está aprendiendo" y que se pueden obtener buenos resultados en learning; resume: "no toquetees constantemente, pero no evites cambios importantes". No aporta test controlado, es criterio experto. [EMPIRICAL — opinión experta] (S12-039)
- **Veredicto:** **CONTEXT-DEPENDENT.** Núcleo verdadero: cada edición significativa compra otra ronda de inestabilidad. Falso como prohibición absoluta.
- **Cuándo es cierto:** ad sets con poco volumen (≤10-15 conversiones/semana), donde cada reinicio retrasa días el aprendizaje; ediciones cosméticas o "por ansiedad".
- **Qué hacer:** definir *de antemano* criterios de corte (p. ej. gasto ≥2-3× CPA objetivo sin conversión → apagar), agrupar las ediciones en una sola ventana, y no sacrificar dinero por proteger una etiqueta. Ver M02-M08.

#### M02 · "Necesitas 50 conversiones por semana" (o "si no llegas a 50 no funciona")

- **Formulación:** "Meta necesita 50 conversiones semanales por ad set; por debajo, el algoritmo no optimiza."
- **Origen:** documentación oficial desde ~2018 ("about 50 optimization events in 7 days").
- **Qué dice Meta hoy:** "las ad sets salen del learning en cuanto pueden entregar de forma estable; normalmente ocurre tras **unos 50 resultados en la semana posterior a la última edición significativa**". En *Learning limited* mantiene "unos 50 eventos de optimización". Para Shops ads: mínimo 17 compras en web + 5 en Meta. [OFFICIAL META] (S12-001, S12-003). Nota: el artículo principal pasó a hablar de "results" en lugar de "optimization events"; en la práctica coinciden.
- **Evidencia empírica:** (1) Vendors afirmaron en jun-2024 que Meta bajó el umbral a **10 eventos** para compras y app installs (Madgicx, 9-jun-2024), sin fuente oficial (S12-050). (2) Loomer documentó que algunas cuentas vieron "10 eventos en 3 días", luego volvieron a 50 y que lo trató como **test**, no como cambio oficial (S12-044). (3) En ago-2026 AdBeacon afirma "25/semana para Advantage+ Shopping" y "15 para App" sin cita directa (S12-051). Ninguna de estas cifras está en el Help Center a 2026-10-15. [UNPROVEN]
- **Veredicto:** **CONTEXT-DEPENDENT.** El "~50/semana por ad set" es real *como umbral de la etiqueta*; es falso que por debajo "no funcione". Ad sets en learning limited pueden ser rentables.
- **Cuándo es cierto:** si la pregunta es "¿saldrá de learning?" o "¿será estable el CPA día a día?".
- **Qué hacer:** dimensionar con la aritmética oficial (presupuesto semanal ≈ 50 × CPA esperado si quieres estabilidad) y, si no llegas, *consolidar* ad sets u optimizar a un evento más frecuente; mirar en Ads Manager el umbral que muestra cada ad set (puede haber tests por cuenta).

#### M03 · "Learning limited es fatal"

- **Formulación:** "Si sale *Learning limited*, la campaña está muerta; apágala y relánzala."
- **Origen:** la etiqueta apareció hacia 2019-2020 con tono de alerta; muchos la leyeron como penalización.
- **Qué dice Meta hoy:** "Learning limited **no es una penalización**; es una indicación de que tu presupuesto no se gasta de forma eficaz porque el sistema no puede optimizar con tu configuración actual". Causas: audiencia pequeña, presupuesto bajo, puja/coste bajo, solapamiento de subasta, evento infrecuente, demasiados anuncios. Si recibe suficientes eventos, pasa de *Learning limited* a *Active*. [OFFICIAL META] (S12-003)
- **Evidencia empírica:** Loomer: "no es una sentencia de muerte"; en muchos negocios es irreal alcanzar 50/semana (S12-039).
- **Veredicto:** **FALSE.**
- **Cuándo podría parecer cierto:** cuando la causa es un bid/cost cap demasiado bajo (el tooltip lo indica) o una audiencia minúscula; ahí sí hay que actuar.
- **Qué hacer:** leer el tooltip; consolidar, ampliar audiencia, subir presupuesto o cap, o cambiar a un evento más frecuente. **Relanzar un duplicado no arregla la causa** y reinicia el aprendizaje.

#### M04 · "Cualquier cambio de presupuesto resetea el learning"

- **Formulación:** "No toques el presupuesto: cualquier cambio vuelve a learning."
- **Origen:** listas antiguas de "significant edits" que incluían "budget change" sin matizar.
- **Qué dice Meta hoy:** el presupuesto está en la lista de cambios que "**pueden o no** ser significativos según su magnitud" (junto con el límite de gasto del ad set y el importe de bid/cost/ROAS goal). Ejemplo oficial: 100→101 USD no; 100→1.000 USD puede. Con Advantage+ campaign budget, ajustar el presupuesto de campaña "puede" hacer que varios ad sets vuelvan a learning, pero **la redistribución automática entre ad sets no lo provoca**, ni añadir un ad set nuevo a la campaña. [OFFICIAL META] (S12-002)
- **Evidencia empírica:** Loomer: los ad sets con etiqueta *High performing* aceptan subidas grandes sin volver a learning (S12-049, S12-039).
- **Veredicto:** **FALSE** (en su formulación absoluta).
- **Qué hacer:** cambios de presupuesto moderados y espaciados; registrar en el *changelog* de la cuenta cada cambio con fecha; usar la columna "Last significant edit" para comprobarlo en vez de suponerlo.

#### M05 · "La regla del 20%"

- **Formulación:** "Nunca subas el presupuesto más de un 20% cada 24-72 h o resetearás el learning."
- **Origen:** heurística de media buyers 2016-2019, coherente con la vieja lógica de "significant edit" y con la observación real de que los saltos grandes desestabilizan el pacing.
- **Qué dice Meta hoy:** no existe ningún porcentaje en el Help Center; solo "magnitud" (ver M04) y "evita cambios frecuentes de presupuesto". [OFFICIAL META] (S12-001, S12-002)
- **Evidencia empírica:** Loomer (posts 2024-2025): "puedes subir más que antes sin volver a learning"; con ad sets *High performing* "bastante"; para el resto propone subidas pequeñas automatizadas (≈1% diario) como opción conservadora, advirtiendo que **el coste sube casi siempre al subir presupuesto** (S12-049). No hay test público que fije el 20% como frontera.
- **Veredicto:** **OUTDATED** como regla; la idea de fondo (subidas graduales = menos volatilidad) sigue siendo razonable.
- **Cuándo podría ser cierto:** ad sets con poco volumen o recién salidos de learning, donde un salto grande sí suele reabrir learning y empeorar CPA marginal.
- **Qué hacer:** escalar por *escalones con hipótesis* (p. ej. +20-50% y medir 3-7 días de coste marginal), no por dogma; para saltos grandes, mejor nueva campaña/ad set con presupuesto realista que cuadruplicar uno pequeño.

#### M06 · "Apagar y encender anuncios resetea el learning"

- **Formulación:** "Si pausas un anuncio o un ad set, al reactivarlo empieza de cero."
- **Qué dice Meta hoy:** en la lista de ediciones significativas aparece "**pausar el ad set siete días o más** (vuelve a learning al reactivarlo)". Pausar un anuncio concreto no figura como edición significativa; "cualquier cambio en la creatividad" y "añadir un anuncio nuevo" sí. [OFFICIAL META] (S12-002)
- **Evidencia empírica:** sin tests públicos sobre pausas cortas de anuncios. Loomer recomienda incluso pausar anuncios que Meta casi no sirve como palanca de troubleshooting (S12-043). Meta, en fatiga creativa, sugiere *mantener* el anuncio original activo al añadir otro porque "puede maximizar resultados" (S12-007).
- **Veredicto:** **CONTEXT-DEPENDENT** (ad set ≥7 días: TRUE; anuncio individual o pausa corta: no documentado).
- **Qué hacer:** evitar pausas largas de ad sets que quieres conservar; si hay que pausar >7 días, asumir re-learning y presupuestarlo.

#### M07 · "Editar un anuncio resetea el learning y pierde la prueba social"

- **Formulación:** "Nunca edites un anuncio: vuelves a learning y pierdes los likes y comentarios."
- **Origen:** años 2015-2017, cuando editar creaba un post nuevo sin engagement.
- **Qué dice Meta hoy:** "cualquier cambio en la creatividad del anuncio" es edición significativa (re-learning: **TRUE**). Sobre la prueba social, la documentación de Meta reproducida por terceros dice que al cambiar la creatividad "el *social feedback* del post anterior se comparte con el nuevo post", salvo excepciones (misma creatividad usada en varios anuncios, post reutilizado en varios anuncios, post ya publicado/programado). [OFFICIAL META vía terceros, confianza media] (S12-002, S12-064)
- **Evidencia empírica:** Loomer documentó desde 2017-2018 flujos para editar sin perder engagement (S12-064). Practitioners siguen reportando pérdidas en duplicados (que es otra operación: duplicar crea un post nuevo).
- **Veredicto:** **CONTEXT-DEPENDENT** — learning: cierto; prueba social: mayoritariamente **OUTDATED** para ediciones, cierto para duplicados.
- **Qué hacer:** comprobar en la vista previa si conserva reacciones antes de publicar; para escalar a otros ad sets, usar "usar post existente"/Post ID (ver M41).

#### M08 · "Añadir un anuncio nuevo a un ad set ganador lo destroza"

- **Formulación:** "Nunca metas creatividades nuevas en el ad set que funciona; lanza siempre en un ad set nuevo."
- **Qué dice Meta hoy:** "añadir un anuncio nuevo al ad set" sigue en la lista oficial de ediciones significativas (consultado 2026-10-15). [OFFICIAL META] (S12-002)
- **Evidencia empírica:** Loomer (Pubcast, oct-2025, y repaso de cambios 2025, ~sep-2025): publicó un anuncio nuevo en un ad set activo y rentable y **no reinició el learning**, "contrario a la documentación"; lo incluye como cambio observado de 2025 (S12-039, S12-040). Otros practitioners recomiendan testear en un ad set/campaña aparte para que el anuncio nuevo reciba gasto (el ganador acapara entrega). Meta lanzó en ~nov-2025 una herramienta de *creative testing* dentro de Ads Manager (duplicar un anuncio y probar hasta 5 nuevos) (S12-040).
- **Veredicto:** **CONTEXT-DEPENDENT / [CONTESTED].** La documentación y la práctica observada divergen; el riesgo real suele ser que el anuncio nuevo **no reciba gasto**, no que "destroce" el ad set.
- **Qué hacer:** si el objetivo es *evaluar* creatividad, usar un entorno con gasto forzado (herramienta de test, ad set de test, A/B); si el objetivo es *refrescar* un ad set que fatiga, añadir dentro y vigilar la columna de última edición significativa.

#### M09 · "El algoritmo necesita 3 días antes de juzgar"

- **Formulación:** "No mires nada hasta el día 3" (o "el 4", o "72 horas").
- **Qué dice Meta hoy:** "analiza el rendimiento durante **al menos una semana completa**"; los breakdowns horarios oscilan y se promedian; los presupuestos diarios son una media semanal. [OFFICIAL META] (S12-011, S12-014)
- **Evidencia empírica:** en los tests de Haus, el 96% de los estudios a nivel de cuenta detectaron lift significativo a mitad de test (≈9 días), y Advantage+ pasó de +9% a −12% frente a manual entre la mitad y el final: **los juicios tempranos pueden invertirse**. [EMPIRICAL] (S12-031)
- **Veredicto:** **CONTEXT-DEPENDENT.** "3 días" no tiene base; el horizonte correcto depende del volumen de eventos y del retraso de conversión (B2B o high-ticket: semanas).
- **Qué hacer:** fijar reglas de corte en *eventos y gasto* (no en días): p. ej. "si gasto ≥ X·CPA objetivo y 0 conversiones → off"; para decisiones de escalar, mínimo una semana completa.

### Bloque B — Presupuesto, estructura y escalado

#### M10 · "Duplica los ganadores"

- **Formulación:** "Cuando un ad set funciona, duplícalo (con más presupuesto o a otra audiencia) en vez de subirle el presupuesto."
- **Origen:** 2017-2020 ("horizontal scaling", "surfing"): se evitaba reabrir learning en el original y se "reiniciaba la suerte" del pacing. Tenía sentido con audiencias segmentadas y sin redistribución automática.
- **Qué dice Meta hoy:** cuando dos ad sets del mismo anunciante entran en la misma subasta, solo compite el de mayor valor total; el solapamiento "puede impedir gastar el presupuesto o salir de learning" y empeora la previsibilidad "especialmente al escalar". Recomienda **combinar** ad sets, no multiplicarlos. [OFFICIAL META] (S12-008, S12-016)
- **Evidencia empírica:** no hay estudio público reciente que muestre ventaja sistemática del duplicado. Los defensores actuales lo usan como "reroll" de un ad set que arrancó mal; Loomer documentó que ad sets idénticos dan resultados distintos (hasta +25% de conversiones entre copias idénticas), lo que muestra **varianza**, no ventaja de duplicar (S12-046).
- **Veredicto:** **OUTDATED** como táctica por defecto; **CONTEXT-DEPENDENT** como herramienta puntual.
- **Cuándo es cierto:** cambiar algo no editable (objetivo, evento de optimización, ventana de atribución, modelo incremental), separar mercado/idioma, o aislar un test.
- **Qué hacer:** escalar primero en vertical (presupuesto) y en creatividad; si se duplica, apagar o reducir el original para no crear solapamiento.

#### M11 · "CBO siempre gana a ABO" (y su inverso "ABO siempre gana")

- **Formulación:** "CBO/Advantage+ campaign budget siempre rinde más" vs "ABO para tener control; CBO es una caja negra que se gasta todo en un ad set".
- **Qué dice Meta hoy:** todos los presupuestos de campaña son Advantage+ campaign budget, que reparte en tiempo real a los ad sets con mejores oportunidades y "funciona mejor si eres flexible"; los presupuestos por ad set son útiles con "objetivos y estrategias de puja mezclados o grandes diferencias de tamaño de audiencia". Con CBO "el riesgo de infra-entrega es menor". Desde 2025 existe **ad set budget sharing**: con ABO puede moverse hasta el 20% del presupuesto entre ad sets. [OFFICIAL META] (S12-014, S12-017, S12-018)
- **Breakdown effect:** cuando CBO "da más presupuesto al ad set con peor CPA medio", suele ser porque optimiza coste marginal, no medio; Meta pide evaluar CBO a nivel de campaña. [OFFICIAL META] (S12-015)
- **Evidencia empírica:** no he encontrado tests públicos controlados 2025-2026 CBO vs ABO con datos (solo opiniones de agencias). [UNPROVEN la superioridad general]
- **Veredicto:** **CONTEXT-DEPENDENT.**
- **Cuándo cada uno acierta:** CBO cuando los ad sets son intercambiables (mismo evento, misma puja) y lo que importa es el total; ABO cuando necesitas garantizar gasto mínimo por segmento (testing creativo, mercados, retención), o mezclas pujas/eventos.
- **Qué hacer:** decidir por *qué quieres controlar* (gasto por segmento vs resultado total), no por fe; si usas CBO, juzgar a nivel de campaña.

#### M12 · "Un ad set por audiencia (o por interés, edad, placement)"

- **Origen:** era del targeting manual (2014-2019): segmentar para "controlar" y para leer resultados por segmento.
- **Qué dice Meta hoy:** "dividir ad sets en estos segmentos podría reducir el rendimiento porque el tamaño total de audiencia se reparte"; recomienda combinarlos y usar **breakdowns** para el reporting; en idioma, geo y placement da la misma instrucción. [OFFICIAL META] (S12-016, S12-006)
- **Veredicto:** **OUTDATED.**
- **Excepción legítima:** cuando el segmento tiene economía distinta (precio, margen, LTV), restricción legal o un mensaje que solo tiene sentido para él; o cuando necesitas presupuesto garantizado.
- **Qué hacer:** segmentar por **economía y mensaje**, no por intereses; reporting con breakdowns.

#### M13 · "Escalar siempre mata el rendimiento"

- **Qué dice Meta hoy:** "el sistema busca primero las oportunidades de mayor volumen/menor coste; cuando se agotan puede pasar a opciones más caras", por lo que **los costes pueden subir a lo largo de la campaña**. [OFFICIAL META] (S12-011)
- **Evidencia empírica:** Loomer: subir presupuesto casi siempre sube el coste por resultado (S12-049). Haus: en sus tests, el lift y el iROAS varían por tipo de campaña y embudo; el rendimiento marginal decreciente es la norma en cualquier canal. [EMPIRICAL] (S12-031)
- **Veredicto:** **FALSE** en "siempre mata"; **TRUE** en "el coste marginal sube".
- **Qué hacer:** decidir el escalado con **CPA/ROAS marginal** (incremento de resultados / incremento de gasto) frente al margen de contribución, no con el CPA medio.

#### M14 · "Meta favorece presupuestos grandes / con poco presupuesto no funciona"

- **Qué dice Meta hoy:** pide "presupuestos realistas"; un presupuesto "muy pequeño o inflado" da al sistema un indicador inexacto; con cost cap, presupuesto diario ≥5× el objetivo de coste. Los mínimos dependen de vertical, moneda, objetivo y puja. [OFFICIAL META] (S12-001, S12-017)
- **Evidencia empírica:** en Motion 2026 la tasa de "ganadores" sube con el tamaño de cuenta (≈3,8% <10K$/mes vs ≈8,2% >1M$/mes), pero un "ganador" allí se define por *gasto* (≥10× la mediana de la cuenta), no por rentabilidad; no prueba trato preferente (S12-038).
- **Veredicto:** **FALSE** como "favoritismo"; **CONTEXT-DEPENDENT** como restricción estadística (pocos eventos = más ruido y menos optimización).
- **Qué hacer:** con poco presupuesto, una sola campaña, un ad set, pocos anuncios diversos, y evento de optimización alcanzable; aceptar más varianza.

#### M15 · "Hay que reiniciar las campañas cada X semanas"

- **Origen:** "las campañas se queman"; confusión entre fatiga creativa y "fatiga de campaña".
- **Qué dice Meta hoy:** la fatiga se diagnostica por **creatividad**: Ads Manager muestra *Creative limited* cuando el coste por resultado supera tu histórico (sin llegar a 2×) y *Creative fatigue* cuando es ≥2×; considera exposiciones de la imagen/vídeo en todas tus campañas de la página. Recomienda creatividad "materialmente distinta" o ampliar audiencia. [OFFICIAL META] (S12-007)
- **Veredicto:** **UNPROVEN** (no hay mecanismo documentado de envejecimiento de campaña; relanzar además pierde historial y reabre learning).
- **Qué hacer:** rotar creatividad y ampliar audiencia antes de relanzar; relanzar solo para cambiar algo no editable.

#### M16 · "Meta gasta más de mi presupuesto diario (me roba)"

- **Qué dice Meta hoy:** el presupuesto diario es una **media semanal**; en días con mejores oportunidades puede gastar **hasta un 75% más**; nunca más de **7× el diario por semana** (flexibilidad del 25 % al 75 % anunciada el 29-may-2025 y formalizada en la Marketing API v24 el 8-oct-2025, S12-088/S12-089) (domingo-sábado); con campañas <7 días, nunca más de diario × duración. El presupuesto total (lifetime) sí es un tope duro. Con budget sharing, máximo diario del ad set = (diario + compartido) × 1,75. [OFFICIAL META] (S12-014, S12-018)
- **Veredicto:** **FALSE** (es el diseño documentado).
- **Qué hacer:** si el negocio necesita un tope diario estricto, usar presupuesto total o límites de gasto; no bajar presupuesto a última hora del día (Meta advierte que puede no dar tiempo a aplicarse) (S12-017).

#### M17 · "Meta frena el gasto / gasta más a final de mes (o de trimestre) para cuadrar ingresos"

- **Origen:** observaciones anecdóticas de CPM más altos a final de trimestre y de "días raros".
- **Qué dice Meta:** nada que lo confirme. El texto oficial sí reconoce "ajustes de subasta" por calidad, test de productos, costes regionales, cumplimiento legal, etc., "sin cobrar más que tu puja". [OFFICIAL META] (S12-004)
- **Evidencia:** no encontré ningún análisis publicado con datos que muestre un patrón de fin de mes independiente de la estacionalidad de demanda (Q4, festivos, rebajas). Busqué en blogs de practitioners, prensa y estudios de agencias. [UNPROVEN]
- **Veredicto:** **UNPROVEN.**
- **Cómo testearlo:** ver `04-afirmaciones-sin-evidencia.md` (regresión de CPM diario con dummies de día del mes en un panel multi-cuenta, controlando estacionalidad).

#### M18 · "Lanza a medianoche / nunca lances en fin de semana"

- **Origen:** limitaciones antiguas de programación (inicio a medianoche) y del pacing con presupuesto diario que "arrancaba" a las 00:00 de la zona horaria de la cuenta; leyendas de "los lunes el algoritmo está más fresco".
- **Qué dice Meta hoy:** el *standard pacing* entra en todas las subastas relevantes y ajusta la puja a lo largo del día; el pacing existe precisamente para no gastar todo en las primeras horas caras. [OFFICIAL META] (S12-005, S12-067)
- **Evidencia:** ninguna publicada a favor de la hora/día de lanzamiento. [UNPROVEN]
- **Veredicto:** **UNPROVEN** (el origen técnico está **OUTDATED**).
- **Cuándo puede importar:** si un ad set de presupuesto diario empieza tarde, el primer día gasta menos; si el negocio tiene picos fuertes por día (restauración, eventos), el lanzamiento puede coincidir con un día atípico y sesgar la lectura inicial.
- **Qué hacer:** lanzar cuando el equipo pueda vigilar las primeras horas (rechazos, errores de tracking), y comparar periodos completos de 7 días.

#### M19 · "El dayparting mejora resultados"

- **Qué dice Meta hoy:** la programación por horas solo funciona con **presupuesto total** a nivel de ad set; los breakdowns horarios "oscilan y se promedian con el tiempo"; Meta ya gasta más o menos según oportunidades por hora. [OFFICIAL META] (S12-011, S12-014)
- **Evidencia:** no hay tests controlados publicados en Meta con resultados; los +35-50% ROAS que circulan provienen de blogs sin metodología. [UNPROVEN]
- **Veredicto:** **UNPROVEN** como mejora general.
- **Cuándo puede ser cierto:** negocios con capacidad de respuesta limitada (llamadas atendidas en horario comercial, citas, mensajería sin bot), donde un lead fuera de horario vale menos. Ahí el valor no es "mejor CPA" sino **mejor tasa de contacto**; Meta incluso sugiere combinar anuncios de llamada programados con formularios fuera de horario.
- **Qué hacer:** antes de dayparting, cuantificar el valor del lead por hora de llegada en el CRM; si no cambia, no programes.

### Bloque C — Audiencias y targeting

#### M20 · "Usa siempre broad"

- **Formulación:** "Abre la audiencia del todo: país, 18-65+, sin intereses. Broad siempre gana."
- **Origen:** 2021-2023, tras iOS 14.5/ATT y el lanzamiento de Advantage+ shopping (2022) y Advantage+ audience (2023): broad empezó a ganar a stacks de intereses en muchas cuentas DTC.
- **Qué dice Meta hoy:** Advantage+ audience logra de media **−14,8%** coste por resultado en Awareness, **−9,7%** en Traffic/Engagement/Leads y **−7,2%** en Sales/App; Meta "recomienda hacer A/B test con Advantage+ audience en casi todos los tipos de campaña" **pero "si haces retargeting, no se recomienda"**. [OFFICIAL META] (S12-020)
- **Evidencia empírica:** Loomer (test de 30 días, ~2.250 $): Advantage+ audience sin sugerencias ganó en volumen; frente a detailed targeting la diferencia **no fue estadísticamente significativa**, frente a lookalikes sí (según resúmenes de su post) (S12-046). Otro test suyo: tres ad sets idénticos difirieron hasta un 25% en conversiones → mucha "victoria" de broad en tests pequeños es ruido.
- **Veredicto:** **CONTEXT-DEPENDENT.** "Siempre" es falso; "por defecto en prospecting con eventos de conversión" es una buena regla de partida.
- **Dónde falla:** retargeting explícito; B2B o nichos con audiencia direccionable minúscula y evento de optimización raro (el sistema no tiene señal para encontrar a quien compra); restricciones legales/geográficas; ofertas que solo sirven a un segmento (p. ej. edad mínima).
- **Qué hacer:** broad + *audience controls* para restricciones duras (edad mínima, geo, exclusiones de custom audiences) + creatividad que "auto-segmente"; validar con test A/B cuando el negocio no sea DTC masivo.

#### M21 · "Los intereses ya no funcionan"

- **Origen:** reducción del catálogo de detailed targeting (eliminación de categorías sensibles en 2022, consolidaciones posteriores), expansión automática por defecto y retirada de **exclusiones** de detailed targeting (anuncio ene-2025, retiradas del ad set el 31-mar-2025; las ad sets que dependían de opciones eliminadas dejaron de entregar el 15-ene-2026, según prensa sectorial). [OFFICIAL META vía prensa] (S12-055)
- **Qué dice Meta hoy:** con Advantage+ detailed targeting, los intereses son un **punto de partida** que el sistema puede ampliar "cuando determine que puede mejorar el rendimiento"; edad, sexo, ubicación e idioma siguen aplicando como límites. [OFFICIAL META] (S12-021)
- **Evidencia empírica:** en el test de Loomer, detailed targeting quedó muy cerca de Advantage+ audience (≈36% de probabilidad estimada de ganar si se repetía) (S12-046).
- **Veredicto:** **FALSE** como enunciado absoluto; **TRUE** que ya no "controlan" la entrega como en 2018.
- **Qué hacer:** usar intereses como **sugerencia** en cuentas sin historial o nichos, y medir si cambian *quién* compra (breakdowns, segmentos de audiencia), no solo el CPA.

#### M22 · "El lookalike 1% es el mejor"

- **Origen:** 2016-2020, cuando los lookalikes eran el mejor proxy de "personas parecidas a mis clientes" y el 1% era el más preciso.
- **Qué dice Meta hoy:** los lookalikes se usan sobre todo como **sugerencias** dentro de Advantage+ audience; la expansión de lookalike pasó a aplicarse por defecto en más objetivos de rendimiento en 2025; según un changelog de terceros, en sep-2026 la Marketing API retiró los campos geo (`country`, `location_spec`) del `lookalike_spec` (no verificado en la fuente de Meta). [OFFICIAL META vía Loomer] + [UNPROVEN el detalle de API] (S12-040, S12-056)
- **Evidencia empírica:** en el test de Loomer, Advantage+ audience batió a lookalikes con diferencia significativa (S12-046).
- **Veredicto:** **OUTDATED.**
- **Cuándo aún tiene sentido:** lookalike de *clientes de alto valor* como sugerencia en cuentas nuevas o con poca señal; mercados pequeños.
- **Qué hacer:** si lo usas, que sea de una semilla de valor (LTV, margen), no de "todos los compradores", y como sugerencia, no como restricción.

#### M23 · "Las campañas de retargeting son obligatorias"

- **Origen:** el funnel clásico TOF/MOF/BOF de 2015-2020 y el ROAS atribuido espectacular del retargeting.
- **Qué dice Meta hoy:** Advantage+ (sales) y Advantage+ audience incluyen a personas que ya interactuaron; la herramienta de **audience segments** separa en el reporting nuevos / engaged / clientes existentes. Meta **no recomienda** Advantage+ audience para campañas de retargeting (si decides hacerlas). [OFFICIAL META] (S12-020, S12-029)
- **Evidencia empírica:** en la muestra de Haus (640 tests), el retargeting fue ~15% del gasto tanto en Advantage+ como en manual (S12-031). Que el retargeting tenga peor incrementalidad que el prospecting es consenso de la industria, pero **las cifras que circulan ("60% de conversiones de retargeting no incrementales", "40-70% sobre-reportado") no tienen fuente primaria verificable**. [UNPROVEN la magnitud]
- **Veredicto:** **FALSE** como obligación universal.
- **Cuándo tiene sentido una campaña aparte:** ciclos de compra largos, carritos de alto valor, mensajes que solo tienen sentido para quien ya conoce la oferta (objeciones, garantías, urgencia real), catálogo dinámico con mucho SKU.
- **Qué hacer:** si existe, presupuestarla pequeña, con ventana corta y **test de holdout**; mirar el % de gasto en clientes existentes en los segmentos.

#### M24 · "Excluye siempre a los compradores"

- **Qué dice Meta hoy:** las exclusiones de **custom audiences** siguen disponibles (las de detailed targeting no). En 2025 desapareció el *existing customer budget cap* de Advantage+ Shopping; Meta indica que se puede replicar manualmente (ad set que excluye clientes, o dos ad sets con límite de gasto). En ago-2026 aparecen las custom audiences "solo para exclusión". [OFFICIAL META vía Loomer/changelog] (S12-048, S12-056)
- **Evidencia empírica:** Meta afirma en su página de Advantage+ sales un **5% menor coste por compra sin cap de clientes existentes** (dato del vendedor, sin metodología pública) (S12-029). Haus: Advantage+ obtuvo el 70% de su impacto de clientes nuevos (S12-031).
- **Veredicto:** **CONTEXT-DEPENDENT.**
- **Cuándo es cierto:** producto de compra única; KPI = nuevos clientes (nCAC); cuando el CRM/email ya captura la recompra a coste ~0.
- **Cuándo es falso:** consumibles/suscripción, lanzamientos para base existente, marcas donde Meta impulsa ventas omnicanal de clientes recurrentes.
- **Qué hacer:** decidirlo por el KPI (nCAC vs MER/contribución), y medir con segmentos de audiencia; nunca excluir a ciegas por "higiene".

#### M25 · "Advantage+ Sales (antes ASC) solo retargetea a tus clientes existentes"

- **Origen:** 2022-2024: ASC mezclaba prospecting y remarketing y su ROAS atribuido inflado por clientes existentes era visible en cuentas con mucha base.
- **Qué dice Meta hoy:** recomienda definir audience segments para ver nuevos/engaged/existentes; el renombrado a **Advantage+ sales campaigns** (2025) unificó la configuración con campañas manuales. [OFFICIAL META] (S12-029, S12-040)
- **Evidencia empírica:** Haus: **70%** del impacto incremental de Advantage+ vino de clientes nuevos (65% en manual); el retargeting representó ~15% del gasto en ambos; pero Advantage+ **sobre-reportó ~12 pp más** que manual (S12-031).
- **Veredicto:** **FALSE** como regla; el riesgo de canibalización existe y se mide.
- **Qué hacer:** configurar segmentos, mirar el % de gasto/conversiones en "existing customers", y si es alto con KPI de captación, aplicar exclusión o test de holdout.

#### M26 · "Advantage+ siempre gana a manual" (y el inverso "Advantage+ es una estafa")

- **Qué dice Meta hoy:** mejoras medias en sus propios experimentos: Advantage+ audience −7,2% a −14,8% coste por resultado; Advantage+ placements −10%; Advantage+ sales "−20% coste por resultado de media" (página de producto); en el call de Q2-2026, Advantage+ "supera los 75.000 M$ de run-rate anual" y un caso con +13% de compras incrementales. [OFFICIAL META] (S12-020, S12-012, S12-029, S12-028)
- **Evidencia empírica (independiente):** Haus (640 tests, 2024-2025): Advantage+ ganó en **42%** de los head-to-head; iROAS DTC **12% menor** de media con 18% menos gasto diario; +9% a mitad de test pero −12% al final; lift post-tratamiento +17% vs +32% manual; ROAS de plataforma 2,4% mayor (es decir, **más atribución, no más incrementalidad**). [EMPIRICAL] (S12-031)
- **Veredicto:** **FALSE** (ambas versiones absolutas). Meta mide medias de *coste por resultado atribuido*; Haus mide *incrementalidad*; no se contradicen tanto como parece.
- **Qué hacer:** tratar Advantage+ como hipótesis a testear con métrica incremental (geo-holdout, conversion lift) en cuentas con volumen; ver `02-contradicciones-entre-expertos.md` §1.

### Bloque D — Creatividad y Andromeda

#### M27 · "La creatividad es el nuevo targeting" (versión absoluta)

- **Formulación:** "El targeting ya no importa; la creatividad hace todo el targeting."
- **Origen:** consigna de agencias DTC desde 2022; Meta la hizo suya en abril de 2025: "con el auge de las herramientas de publicidad con IA, el foco ha pasado del targeting de nicho a la **diversificación creativa** como la mejor palanca para encontrar las audiencias más relevantes". [OFFICIAL META, citado por Social Media Today y Loomer] (S12-070, S12-047)
- **Qué dice la mecánica oficial:** la subasta combina puja × tasas de acción estimadas + calidad (S12-004); las tasas estimadas dependen de la interacción persona-anuncio, así que la creatividad **sí** cambia a quién se le muestra cada anuncio. Pero ubicación, edad mínima, idioma, exclusiones, evento de optimización, puja y la oferta/landing siguen siendo inputs duros.
- **Evidencia empírica:** Loomer (tests 2024-2025) observó que la distribución de remarketing fue casi idéntica con o sin inputs de audiencia y que la creatividad/oferta movía más el resultado que los intereses; no he visto un test público que cuantifique cuánto "segmenta" la creatividad. [EMPIRICAL limitado] (S12-046)
- **Veredicto:** **CONTEXT-DEPENDENT.** Dirección correcta en prospecting con broad y conversión; falso como "el targeting no importa".
- **Dónde falla:** B2B de nicho, local, cumplimiento legal, ofertas restringidas por edad/país, cuentas sin señal de conversión.
- **Qué hacer:** diseñar creatividades que *nombren* al segmento (dolor, contexto, objeción) y mantener controles duros donde el negocio lo exige.

#### M28 · "Necesitas 3-6 anuncios por ad set" / "demasiados anuncios perjudican"

- **Origen:** Meta recomendó durante años "6 o menos creatividades por ad set" en su artículo de volumen de anuncios.
- **Qué dice Meta hoy:** esa cifra **ya no aparece** (retirada en 2025, sin anuncio; el texto actual dice "reduce anuncios por ad set pero mantén activos creativos diversos; un anuncio puede contener hasta diez activos"). Mantiene: "cuando un anunciante ejecuta demasiados anuncios a la vez, cada uno se entrega menos… **demasiados anuncios pueden empeorar el rendimiento**", y en learning: "evita volúmenes altos de anuncios". Límites por página: 250 / 1.000 / 5.000 / 20.000 anuncios activos según gasto mensual máximo. Desde junio de 2024 no se puede crear dynamic creative en ventas/app (se recomienda flexible format). [OFFICIAL META] (S12-006, S12-001, S12-010, S12-043)
- **Evidencia empírica:** Loomer (6-may-2026): "creo que hay señales de que puedes crear demasiados anuncios", pero lo califica de **intuición**, "no es ciencia probada"; empieza con un par de anuncios diversos y añade si hace falta (S12-043).
- **Veredicto:** el número 3-6: **OUTDATED**; "demasiados anuncios perjudican": **CONTEXT-DEPENDENT** (depende de presupuesto por anuncio).
- **Qué hacer:** dimensionar anuncios por **presupuesto y eventos**: si cada anuncio no puede recibir gasto suficiente para generar señal, sobran anuncios; agrupar variantes en un anuncio multi-activo cuando sean del mismo concepto.

#### M29 · "Con Andromeda necesitas 50 creatividades (o 20 nuevas a la semana)"

- **Origen:** 2025, interpretación de la publicación de Andromeda (Meta habla de que el volumen de creatividades "crecerá significativamente" con IA generativa) más vendors de producción creativa.
- **Qué dice Meta hoy:** ningún documento fija un número de creatividades. El blog de Andromeda dice que el sistema se diseñó para escalar a más anuncios elegibles; el Help Center dice que demasiados anuncios a la vez reducen el aprendizaje por anuncio. [OFFICIAL META] (S12-026, S12-006)
- **Evidencia empírica:** Motion 2026 (1.290 M$ de gasto, 578.750 creatividades, 6.015 cuentas, sep-2025 a ene-2026): las cuentas que lanzan más creatividades obtienen más "ganadores" en términos absolutos, pero **la probabilidad por creatividad no cambia** (~5%); en el tramo 50-200 K$/mes, el cuartil superior lanza 15,9/semana vs 6,6 de media. Ojo: "ganador" = creatividad que gasta ≥10× la mediana de la cuenta y ≥500 $; es una métrica de **asignación de gasto por Meta**, no de rentabilidad ni incrementalidad. Correlacional. [EMPIRICAL con sesgo de definición] (S12-038)
- **Veredicto:** **FALSE** como requisito; **UNPROVEN** cualquier número concreto.
- **Qué hacer:** fijar la cadencia creativa por presupuesto (anuncios que puedes *financiar* hasta tener señal) y por fatiga observada; priorizar conceptos distintos sobre variantes.

#### M30 · "Andromeda castiga las creatividades parecidas" / "Entity ID"

- **Formulación:** "Andromeda agrupa anuncios parecidos en un mismo Entity ID y te penaliza; por encima de un 60% de similitud se suprime la entrega."
- **Qué dice Meta hoy:**
  - El blog de ingeniería (2-dic-2024) describe Andromeda como fase de *retrieval* con índice jerárquico entrenado junto al modelo; **no** describe deduplicación ni penalizaciones por similitud. [OFFICIAL META] (S12-026)
  - En fatiga creativa, Meta considera "todas las exposiciones recientes de la imagen o vídeo del anuncio, también de otras campañas de tu página" y pide una creatividad "**materialmente distinta**". [OFFICIAL META] (S12-007)
  - Página oficial *Maximize conversions with differentiated ad creative*: "When creative is too similar, our system may not recognise it as different and could deliver it to the same sets of audiences. This overlap limits your reach and ultimately leads to creative limited or creative fatigue status." [OFFICIAL META] (S12-105, leída 2026-10-16)
  - Según varios medios, desde el 26-ago-2026 Ads Manager tiene una columna **Creative diversity** (Low/Medium/High por ad set, etiquetada *estimated, in development*) que mide la diversidad visual de imágenes y vídeos. No pude localizar el artículo del Help Center (búsqueda en el propio Help Center y en buscadores, 16-oct-2026); lo trato como oficial vía UI reportada por terceros. [OFFICIAL META vía terceros] (S12-058)
- **Evidencia empírica:** consistente entre practitioners que variantes casi idénticas reciben poco gasto; ninguna medición pública de umbrales. El término "Entity ID" **no aparece en documentación de Meta** que haya encontrado. Las afirmaciones "score >60% suprime retrieval" o "mantener <40%" no tienen fuente primaria. [UNPROVEN]
- **Veredicto:** **CONTEXT-DEPENDENT.** Que las variantes casi idénticas se traten como una sola y lleguen al mismo público está **confirmado por Meta**; "castigo" es un encuadre erróneo: no hay evidencia de que reduzcan la entrega del resto.
- **Qué hacer:** diversificar por **concepto, ángulo, persona, formato y escenario**; tratar la columna como diagnóstico direccional, no como KPI; no inventar umbrales.

#### M31 · "Andromeda es el nuevo algoritmo / ha cambiado la subasta"

- **Qué dice Meta hoy:** Andromeda es la **primera fase** (retrieval) del sistema multi-etapa: reduce decenas de millones de candidatos a unos miles antes del ranking; Meta reportó +6% de recall y +8% de calidad de anuncios en segmentos seleccionados. El ranking lo hacen modelos posteriores (GEM, presentado el 10-nov-2025: +5% conversiones en Instagram y +3% en Facebook Feed en Q2-2025). La subasta sigue siendo **valor total = puja + tasas de acción estimadas + calidad**. En Q2-2026 Meta atribuyó +8,3% de clics y +15,7% de conversiones en Facebook a sus modelos de comprensión de usuario combinados con GEM y sequence learning, y por separado presentó el *Meta Generative Recommender* ("el primer modelo generativo en el sistema de retrieval"). Atribuir el +15,7% al Generative Recommender, como hacen algunos blogs y hilos de Reddit, es incorrecto. [OFFICIAL META] (S12-026, S12-027, S12-028, S12-004)
- **Veredicto:** **FALSE.** Hay varios modelos en cadena; atribuir cada cambio de rendimiento a "Andromeda" es un error de diagnóstico.
- **Qué hacer:** en auditorías, separar hipótesis: ¿problema de elegibilidad/retrieval (poca entrega, anuncios sin gasto) o de ranking/subasta (CPM, tasas estimadas, calidad)?

#### M32 · "Meta odia los anuncios duplicados" / "pujas contra ti mismo"

- **Qué dice Meta hoy:** "cuando dos o más anuncios del mismo anunciante entran en la misma subasta, elegimos el de mayor valor total… así **tus anuncios no pujan unos contra otros**". También: varias cuentas del mismo anunciante pueden ser identificadas como tal y el solapamiento ocurre entre cuentas; crear páginas extra hace que **sí** compitan entre sí y dividan aprendizajes. [OFFICIAL META] (S12-008, S12-010)
- **Veredicto:** **FALSE** en "pujas contra ti mismo" (dentro de una página/anunciante); **TRUE** que la duplicación fragmenta aprendizaje y entrega.
- **Qué hacer:** consolidar; usar las recomendaciones de solapamiento del *Opportunity score* como pista (no como verdad).

#### M33 · "Los estáticos están muertos"

- **Origen:** 2020-2023, auge de Reels/TikTok y del "video-first".
- **Evidencia empírica:** Motion 2026: por tasa de acierto, los tipos de activo líderes son **text only**, **product image with text** y **lifestyle-product image**, por delante de UGC y alta producción; *Offer-First Banner* es el formato visual con mejor combinación de tasa de acierto (8,6%) y uso de gasto (1,3). Carrusel y animación quedan abajo en uso de gasto. Recordatorio: "acierto" = Meta les asignó mucho gasto. [EMPIRICAL] (S12-038)
- **Veredicto:** **FALSE.**
- **Qué hacer:** mezclar estáticos de oferta/prueba con vídeo; en placements Reels/Stories, preparar versiones nativas 9:16 (desde 2026 los placements se gestionan por activo, ver M55).

#### M34 · "El UGC siempre gana" (y su primo "los anuncios feos siempre ganan")

- **Evidencia empírica:** Motion 2026: UGC está en la parte alta (4º por tasa de acierto, 4º por uso de gasto), pero no en la cima; "alta producción" tiene tasa media y es *table stakes* en automoción, tecnología, finanzas y viajes. Barry Hott (defensor de "ugly ads") matiza que no todo debe ser feo, solo que hay que perder el miedo a lo no pulido; no hay test controlado publicado. [EMPIRICAL] (S12-038, S12-061)
- **Veredicto:** **FALSE** como "siempre".
- **Qué hacer:** elegir formato por vertical y por etapa (validar ángulo barato → escalar con producción si el ángulo está probado).

#### M35 · "Los vídeos largos no funcionan"

- **Evidencia:** el único dataset 2026 localizado (Biddyco, 5-oct-2026: 421 anuncios, 17 cuentas) no encuentra que la duración prediga gasto ni coste por resultado (diferencias de ±6 % entre tramos; espectador mediano ~4 s en cualquier duración) (S12-119). Un estudio Meta/Nielsen (CPG, APAC, sin fecha clara) favorecía vídeos <15 s para promociones; vendors defienden 15-30 s en Reels pero reconocen que vídeos largos con buena retención funcionan. ThruPlay se define como vídeo completo si dura <15 s o ≥15 s vistos (S12-023). [UNPROVEN]
- **Veredicto:** **UNPROVEN.**
- **Qué hacer:** decidir duración por la tarea del anuncio (oferta simple vs objeción compleja/high-ticket) y medir retención por segundo y conversiones, no por regla.

#### M36 · "Los anuncios nuevos reciben un 'boost' de novedad"

- **Origen:** observación habitual de que un anuncio nuevo rinde bien 1-3 días y luego cae.
- **Qué dice Meta:** nada explícito. El sistema explora al principio (learning) con poca muestra, y la regresión a la media explica gran parte del patrón; el *breakdown effect* muestra cómo las primeras cifras engañan (S12-015).
- **Veredicto:** **UNPROVEN** ([HYPOTHESIS]). Ver test propuesto en `04`.
- **Qué hacer:** no decidir escalados por los 2-3 primeros días.

#### M37 · "Frecuencia > 3 = fatiga"

- **Origen:** heurísticas de reach & frequency de TV/display trasladadas a Meta (2015-2019).
- **Qué dice Meta hoy:** la fatiga se detecta por **coste por resultado** frente a tus anuncios previos (*Creative limited* <2×; *Creative fatigue* ≥2×), considerando exposiciones de la misma imagen/vídeo en todas tus campañas. No hay umbral de frecuencia. [OFFICIAL META] (S12-007)
- **Evidencia:** estudios académicos de display muestran CTR decreciente con la frecuencia, mitigado con más creatividades distintas; las cifras "1-2/semana" o "5-7" que circulan son contradictorias y sin datos. En retargeting y audiencias pequeñas, frecuencias altas son normales y pueden ser rentables. [UNPROVEN el umbral]
- **Veredicto:** **FALSE** como regla.
- **Qué hacer:** vigilar la *tendencia* de CPA/CTR por creatividad frente a frecuencia acumulada, por audiencia. Nota operativa 2026: los breakdowns de frecuencia vía API requieren activación por cuenta (ago-2026) y solo tienen 6 meses de retención (S12-052, S12-056).

#### M38 · "El CTR tiene que estar por encima de X%"

- **Qué dice Meta hoy:** la subasta usa tasas estimadas de la **acción que optimizas**; con link clicks, Meta "puede priorizar clics de mayor calidad". No hay umbral de CTR. [OFFICIAL META] (S12-004, S12-023)
- **Evidencia:** WordStream/LocaliQ 2025: CTR medio de tráfico 1,71% y de leads 2,59%, con rangos por sector de ~0,8% a >4%; otras fuentes dan medias de 0,89% a 2,19% para el mismo año según definición. [EMPIRICAL, benchmarks heterogéneos] (S12-063)
- **Veredicto:** **FALSE.**
- **Qué hacer:** usar CTR (link) como diagnóstico relativo dentro de tu cuenta y concepto; decidir por coste por resultado y calidad post-clic.

#### M39 · "Las creatividades generadas con IA rinden peor"

- **Evidencia empírica:**
  - TUM + Columbia + Harvard (working paper, 21-feb-2025): >16.000 M de impresiones, ~7.000 anunciantes (display): los anuncios generados con IA **igualan o superan** a los humanos; los percibidos como hechos por humanos tienen CTR claramente mayor; ~59% de los de IA pasan por humanos. (S12-059)
  - Ipsos + Syracuse (27-may-2026): 20 anuncios, 3.000 encuestados: humanos +11 sobre benchmark de ventas, IA −5; IA mejor en briefs de producto directo, peor en storytelling. Muestra pequeña y métrica declarativa. (S12-060)
  - Meta: +7% conversiones estimadas con generación de imágenes (blog Andromeda), +11% CTR con fondos generados (abr-2025); >9 M de pequeñas empresas usan alguna herramienta creativa IA (Q2-2026). Datos del vendedor. (S12-026, S12-070, S12-028)
- **Contexto regulatorio 2026:** obligaciones de transparencia de contenido IA en la UE (AI Act art. 50, desde ago-2026) y California (SB 1050, desde 1-ene-2027, intérpretes sintéticos) pueden cambiar el efecto "disfraz". (S12-056) [STRONG INFERENCE sobre el impacto]
- **Veredicto:** **CONTEXT-DEPENDENT / [CONTESTED].** Lo que penaliza es *parecer* IA y los briefs emocionales; el origen en sí no.
- **Qué hacer:** usar IA para variantes y ángulos de producto; control humano de "aspecto IA" (colores hipersaturados, caras imposibles); cumplir etiquetado donde aplique.

#### M40 · "Las mejoras de Advantage+ creative hay que tenerlas siempre ON (u OFF)"

- **Qué dice Meta:** en 2023 publicó que las *standard enhancements* redujeron un **4%** el coste por resultado (experimento de un mes, 154.000 cuentas, mayo 2022) en link clicks, LPV y conversiones. Desde entonces el catálogo creció mucho (2025: traducción, reformular frases, texto destacado, música, "optimize website destination", etc.). [OFFICIAL META] (S12-030, S12-040)
- **Evidencia empírica:** Loomer apaga algunas por defecto (p. ej. cambio de destino de la web) por riesgo de mensaje; en 2026 algunos anunciantes reportan activaciones por defecto en anuncios existentes (p. ej. "product browsing" a partir del 28-oct-2026, según aviso compartido por anunciantes, sin página pública de Meta a 15-oct). [EMPIRICAL / UNPROVEN] (S12-040, S12-056)
- **Veredicto:** **CONTEXT-DEPENDENT.** La media favorece activarlas; el riesgo está en sectores regulados, marca y precisión del mensaje.
- **Qué hacer:** activar por mejora y por familia de anuncios, revisar las vistas previas generadas, auditar cada trimestre qué se ha activado por defecto.

#### M41 · "Usar el Post ID siempre conserva la prueba social"

- **Qué es cierto:** crear anuncios desde un post existente acumula reacciones y comentarios en un solo post. [EMPIRICAL amplio]
- **Límites:** formatos que generan variaciones (dynamic creative, multi-activo/flexible, mejoras creativas) no se reducen a un único post; un post reutilizado no se puede editar; si el post viola políticas, todos los anuncios caen. Las afirmaciones de que Meta "agrega aprendizaje a nivel de post" son de vendors sin confirmación. (S12-064)
- **Veredicto:** **CONTEXT-DEPENDENT.**
- **Qué hacer:** usar Post ID para escalar ganadores de formato simple; para formatos dinámicos, aceptar engagement repartido o consolidar en un único anuncio multi-activo.

#### M42 · "Meta castiga los anuncios con comentarios negativos"

- **Qué dice Meta hoy:** la *calidad del anuncio* se mide con "feedback de las personas que ven u **ocultan** el anuncio" y evaluaciones de atributos de baja calidad (clickbait, retener información, lenguaje sensacionalista). Los comentarios negativos no aparecen como señal explícita. Los diagnósticos de relevancia "no son inputs de la subasta". [OFFICIAL META] (S12-004, S12-022)
- **Evidencia:** solo anécdotas y vendors de moderación con cifras sin fuente. [UNPROVEN]
- **Veredicto:** **UNPROVEN** (ocultar/reportar: **TRUE** que afecta a la calidad).
- **Qué hacer:** moderar por experiencia de marca y conversión (los comentarios visibles afectan a la tasa de conversión de quien los lee), no por miedo a una penalización algorítmica no demostrada.

### Bloque E — Estrategias de puja

#### M43 · "Lowest cost (máximo volumen) es siempre lo mejor"

- **Qué dice Meta hoy:** *highest volume/lowest cost* gasta el presupuesto buscando el máximo de resultados; *cost per result goal* (antes cost cap) es una media que Meta intenta no superar "pujando tan alto como haga falta"; *bid cap* fija la puja máxima en subasta y **no controla el coste por resultado** reportado; ambos pueden superarse en learning. [OFFICIAL META] (S12-011)
- **Evidencia empírica:** CTC (6-ago y 25-ago-2026; 253 cuentas y 200 M$ analizados en detalle de mar-2025 a jul-2026, y un corte de 320 cuentas / ~1.500 M$ mar-jun-2026): *min ROAS* entregó ~96,5% del objetivo en agregado (pero 67% de cuentas >5% por debajo de su objetivo individual); *cost per result goal* ~140% del objetivo (se pasa ~40%; 75% de cuentas >5% por encima). [EMPIRICAL; fuente con interés comercial y sin metodología completa] (S12-036, S12-037)
- **Veredicto:** **CONTEXT-DEPENDENT.** Lowest cost es el mejor *punto de partida* y la opción con menos riesgo de infra-entrega; no es lo mejor cuando el margen exige un suelo de eficiencia y hay volumen suficiente.
- **Qué hacer:** empezar en lowest cost; pasar a value/min ROAS cuando el valor por conversión varía mucho y hay volumen; calibrar el objetivo con el sesgo observado (no poner el CPA real deseado como cap).

#### M44 · "Los bid caps son solo para expertos"

- **Evidencia:** CTC declara el bid cap su control de coste por defecto (entregó ~123% del objetivo en una muestra pequeña de 3 M$); Andrew Faris se define como "the bid cap guy" pero matiza que los controles de coste importan menos que otros factores y que con poco volumen pueden ahogar la entrega. [EMPIRICAL, opinión con datos parciales] (S12-036)
- **Veredicto:** **FALSE** como tabú; **TRUE** que exigen disciplina (vigilar infra-entrega, recalibrar con CPM).
- **Qué hacer:** usar bid caps cuando el negocio tolera gastar menos a cambio de no pagar caro; presupuesto amplio y revisión semanal del cap.

#### M45 · "El cost cap mata la escala"

- **Qué dice Meta:** con cost per result goal, presupuesto diario ≥5× el objetivo (S12-017); el learning limited puede deberse a cap bajo (tooltip) (S12-003).
- **Evidencia:** según CTC, el problema medio no es infra-entrega sino lo contrario: **el cost cap tiende a superar el objetivo** (~40%). Cuando el cap está por debajo del coste de mercado, sí limita volumen. (S12-036)
- **Veredicto:** **CONTEXT-DEPENDENT.** "Mata" si el cap es irreal; si no, el riesgo es creer que controla el CPA.
- **Qué hacer:** leer el cap como palanca de *dirección*, no de precisión; medir CPA real vs cap por cuenta y ajustar con un factor de calibración propio.

#### M46 · "Un CPM alto significa que la audiencia es mala"

- **Qué dice Meta hoy:** "si optimizas para conversiones, el CPM puede no ser un buen indicador… el sistema puede ir a por impresiones más caras si así consigue conversiones más baratas". [OFFICIAL META] (S12-011)
- **Contexto 2026:** CPM también sube por factores ajenos a la audiencia: precio medio por anuncio +12% interanual en Q2-2026 (Meta), estacionalidad Q4, y nuevos *location fees* desde 1-jul-2026 (UK 2%, FR/IT/ES 3%, AT/TR 5%) que encarecen la factura aunque no sean CPM de subasta. (S12-028, S12-056)
- **Veredicto:** **FALSE.**
- **Qué hacer:** diagnosticar con coste por resultado y tasa de conversión; usar CPM solo para descomponer variaciones (CPM × 1/CTR × 1/CVR).

### Bloque F — Medición, tracking y atribución

#### M47 · "Las conversiones view-through son falsas"

- **Origen:** escepticismo legítimo (2016-2021) ante ventanas 1d/28d view que se atribuían compras que iban a ocurrir igualmente.
- **Qué dice Meta hoy:** en atribución estándar, view-through cuenta eventos **dentro de 1 día** tras una impresión; las ventanas 7d_view y 28d_view se retiraron de la Ads Insights API el **12-ene-2026** (anuncio 13/16-oct-2025). Desde marzo de 2026 existe *engage-through* (antes *engaged-view*, ampliado: 1 día tras un clic que no es de enlace o un visionado de vídeo de 5 s). [OFFICIAL META] (S12-009, S12-052)
- **Evidencia empírica:** Haus: la atribución de solo clic (7d) **infra-reporta** el impacto incremental un 15% de media → parte del efecto de Meta ocurre sin clic. Stella (46 geo-tests, ene-abr 2025): con ventana 7d click + 1d view normalizada, el ROAS incremental medio (2,87) superó al de plataforma (2,37). Ninguna de las dos aísla el view-through. [EMPIRICAL] (S12-031, S12-034)
- **Veredicto:** **CONTEXT-DEPENDENT.** Ni "falsas" ni "reales": una parte es incremental y otra no, y varía por campaña (más dudosa en retargeting y marcas con mucha demanda orgánica).
- **Qué hacer:** decidir la ventana con un experimento propio (lift o geo); usar la misma ventana para comparar periodos.

#### M48 · "Meta sobre-reporta todo"

- **Evidencia empírica:**
  - Haus (640 tests, 2024-2025): Meta generó de media +19% de lift en el KPI principal; por cada 100 $ atribuidos con 7d click, ~115 $ incrementales; Advantage+ sobre-reporta ~12 pp más que manual; upper/mid funnel infra-reportados si solo se mira DTC; 32% del impacto de marcas omnicanal fue fuera del DTC. (S12-031, S12-032)
  - Stella (46 geo-tests): factor de incrementalidad medio 1,21, pero con marcas de ROAS >4 y factor <1 (S12-034).
  - Gordon, Moakler y Zettelmeyer (Marketing Science, 2023; 663 experimentos de Facebook): los métodos observacionales, incluso con ML, **fallan** al estimar el efecto real (errores medianos de decenas a >100%); los autores tenían relación laboral con Meta. (S12-035)
- **Veredicto:** **FALSE** como universal. Meta puede sobre- o infra-reportar según tipo de campaña, embudo, ventana y canal de venta.
- **Qué hacer:** calibrar el ROAS de plataforma con un factor de incrementalidad propio por tipo de campaña (lift/geo), y re-medir tras cambios de atribución (2026).

#### M49 · "El EMQ tiene que estar por encima de 8"

- **Qué dice Meta hoy:** en developers, "we typically recommend that you aim for an Event Match Quality score of **6.0 or higher**" (Verifying setup, S12-111); en el Help Center, "aspira a un event match quality **Good o Great**"; mejor EMQ "puede aumentar las conversiones adicionales reportadas"; prioriza parámetros de cliente (email, teléfono, IP, user agent, fbc/fbp…) y su cobertura. Meta no publica el corte numérico de "Great". El 8,5 que a veces se cita es el umbral recomendado de **Offline Data Quality**, no de EMQ. [OFFICIAL META] (S12-111, S12-013)
- **Veredicto:** **UNPROVEN** (el umbral oficial orientativo es 6,0, no 8; y el EMQ alcanzable depende del tipo de evento: un PageView anónimo nunca tendrá email).
- **Qué hacer:** mejorar cobertura de parámetros en eventos de conversión (Purchase, Lead) y medir "conversiones adicionales reportadas" en Events Manager, no perseguir un número.

#### M50 · "Con Conversions API (solo server-side) es suficiente"

- **Qué dice Meta hoy:** recomienda **configuración redundante**: los mismos eventos por píxel y CAPI, deduplicados (event_id), con un objetivo de **≥75% de cobertura de eventos CAPI respecto a píxel**; enviar en tiempo real. [OFFICIAL META] (S12-013)
- **Contexto 2026:** Safari 26 activó por defecto protecciones contra fingerprinting en toda la navegación; la eliminación de click IDs (fbclid) está confirmada en navegación privada y enlaces de Mail/Messages, y es dudosa en navegación normal (tests mixtos). Esto **refuerza** CAPI con parámetros de cliente, pero no sustituye al píxel (señales del navegador, fbp/fbc, eventos de página). (S12-062) En abr-2026 Meta anunció píxel "enriquecido con IA" y CAPI en un clic (según changelog de terceros) (S12-056).
- **Veredicto:** **FALSE.**
- **Qué hacer:** píxel + CAPI deduplicados, con email/teléfono hasheados en eventos clave.

#### M51 · "Los UTMs rompen el tracking de Meta"

- **Mecánica:** los UTMs etiquetan el tráfico para tu analítica; Meta atribuye con fbclid/_fbc, fbp y parámetros de cliente. Son sistemas independientes. Lo que sí rompe ambos es una **redirección** (acortadores, landing intermedias, apps) que elimina parámetros. WebKit exime a los parámetros de campaña tipo UTM de la protección de enlaces de Safari. (S12-062)
- **Veredicto:** **FALSE.**
- **Qué hacer:** UTMs dinámicos (`{{campaign.name}}`, `{{ad.id}}`…), evitar redirecciones, comprobar que fbclid llega a la landing.

#### M52 · "La atribución incremental de Meta siempre es mejor (o siempre peor)"

- **Qué dice Meta hoy:** modelo de atribución que "optimiza la entrega para conversiones incrementales usando modelos que predicen si una conversión fue causada por un anuncio"; los resultados no son comparables con estándar en la tabla. [OFFICIAL META] (S12-019, S12-009)
- **Evidencia empírica:** Haus: en tests jul-2024/jun-2025, la atribución incremental (IA) rindió 0,80× el retorno incremental de la estándar (ganó el 43% de las veces); en jul-2025/jun-2026, **1,26×** (DTC 1,38×; omnicanal ~1,02×). Muestra "modesta" y sesgada hacia DTC. [EMPIRICAL] (S12-033, S12-031)
- **Veredicto:** **[CONTESTED]**, con tendencia reciente favorable a IA en DTC.
- **Qué hacer:** testear IA vs estándar con experimento externo (no con el reporting de Meta), por tipo de negocio.

#### M53 · "Un quality ranking bajo te penaliza en la subasta"

- **Qué dice Meta hoy:** quality, engagement rate y conversion rate ranking son diagnósticos comparativos con anuncios que compiten por la misma audiencia; "los diagnósticos de relevancia **no son inputs de la subasta**"; requieren ≥500 impresiones. [OFFICIAL META] (S12-022)
- **Veredicto:** **FALSE** (la calidad sí entra en la subasta, pero el *ranking* es solo un espejo).
- **Qué hacer:** usarlos para diagnosticar (creatividad vs post-clic vs audiencia), no como objetivo.

#### M54 · "Un Opportunity score alto significa que la cuenta rinde bien"

- **Qué dice Meta hoy:** "el opportunity score (incluido uno alto) no refleja tu rendimiento actual ni futuro… no garantiza rendimiento". Loomer lo describe como una medida de **disposición a aceptar recomendaciones** de Meta (0-100), global desde ~jun-2025. [OFFICIAL META] (S12-007, S12-016, S12-040)
- **Veredicto:** **FALSE.**
- **Qué hacer:** evaluar cada recomendación como hipótesis; algunas son "experimentalmente probadas" según Meta (combinar ad sets, fatiga), otras empujan más automatización por defecto.

#### M63 · "El click-through incluye cualquier clic en el anuncio"

- **Qué dice Meta hoy:** click-through "cuenta eventos en 1 o 7 días tras un **clic en enlace**"; engage-through, eventos en 1 día tras un clic que no es de enlace o un visionado de 5 s (o 97% si el vídeo dura <5 s). Algunas cuentas aún tienen la versión anterior mientras dura el despliegue. Anunciado en marzo de 2026 según prensa sectorial; antes, cualquier clic (likes, comentarios, perfil, expandir imagen) podía contar como click-through. [OFFICIAL META] (S12-009, S12-054)
- **Veredicto:** **OUTDATED.**
- **Qué hacer:** al comparar periodos que cruzan marzo de 2026, esperar caída de conversiones "por clic" sin cambio real; separar click y engage-through en columnas.

#### M64 · "Si Ads Manager no cuadra con GA4/Shopify, Meta miente"

- **Mecánica:** Ads Manager reporta las conversiones fuera de Meta (p. ej. compras web) por **fecha de conversión** y las acciones en el anuncio (clics) por fecha de impresión (`action_report_time=mixed`, que la API replica desde el 10-jun-2025), con ventanas propias (incluye view/engage-through); GA4 usa otros modelos, fecha de sesión, y pierde usuarios sin consentimiento o con bloqueo. Meta advierte que no se comparan modelos distintos en la misma tabla y que, con herramientas externas, se evalúe en ellas. [OFFICIAL META] (S12-009)
- **Veredicto:** **FALSE.** La discrepancia es esperable; la pregunta útil es cuál se acerca más al efecto incremental (ver M48).

#### M65 · "Puedo seguir sacando 7d/28d view por API para mis informes"

- **Qué dice Meta:** desde el 12-ene-2026 la Ads Insights API no devuelve `7d_view` ni `28d_view` (incluido histórico); también limita retención de breakdowns: 13 meses para métricas *unique* y horarias, 6 meses para frecuencia; los totales se mantienen 37 meses. [OFFICIAL META vía PPC Land] (S12-052)
- **Veredicto:** **OUTDATED.**
- **Qué hacer:** revisar dashboards y modelos MMM que dependían de esas ventanas; almacenar histórico propio si se necesita.

### Bloque G — Placements

#### M55 · "Los placements manuales rinden mejor"

- **Origen:** 2016-2020, cuando Audience Network y la columna derecha arrastraban CPAs malos y se separaban ad sets por placement.
- **Qué dice Meta hoy:** "en un experimento, los ad sets con Advantage+ placements obtuvieron un **10% menos de coste por resultado** de media" frente a placements manuales (en otras páginas cita 11,7%). Y lo más importante para 2026: en **Leads, App promotion y Sales (Engagement no; corrección 2026-11-09) ya no se eligen placements manualmente a nivel de ad set** (despliegue gradual; Awareness y Traffic conservan el control). Alternativas: personalización de activos por placement, *placement value rules* (subir/bajar puja por placement) y exclusiones a nivel de cuenta por objetivo. [OFFICIAL META] (S12-012) **Actualización 2026-11-09**: la página releída ya no da el −10 %; dice que Advantage+ placements "puede ayudarte a reducir el coste por resultado" (S10-107 en `fuentes/ledger-10-cambios-api-ia.md`).
- **Breakdown effect:** el placement con peor CPA medio puede ser el que más resultados marginales aporta; Meta pide juzgar placements a nivel de ad set. (S12-015, S12-041)
- **Veredicto:** **FALSE** en general; la pregunta ya es casi irrelevante en objetivos de conversión.
- **Cuándo había razón:** objetivos de clic/LPV/ThruPlay, donde algunos placements dan acciones baratas y de baja calidad (ver M56).
- **Qué hacer:** creatividad nativa por placement; value rules solo con datos que demuestren diferente valor por placement (Loomer: "no aplicar value rules de forma universal") (S12-042).

#### M56 · "Audience Network es pura basura"

- **Evidencia:** Loomer: AN es "notorio por tráfico de baja calidad por clics accidentales, fraude y bots" sobre todo en campañas de tráfico; con objetivos de conversión es menos problemático. Cifras de fraude que circulan (p. ej. "67% de tráfico inválido") no tienen fuente primaria localizable. [EMPIRICAL / UNPROVEN cifras] (S12-069)
- **Qué dice Meta:** AN sigue dentro de Advantage+ placements; se puede excluir **a nivel de cuenta** (AN nativo/banner/intersticial y rewarded video) y bajar puja con value rules. [OFFICIAL META] (S12-012)
- **Veredicto:** **CONTEXT-DEPENDENT.**
- **Qué hacer:** con optimización a clics/LPV, excluir AN a nivel de cuenta o no usar esos objetivos; con conversión, comprobar calidad post-clic por placement antes de excluir.

#### M57 · "Si excluyo un placement, Meta no gasta ahí"

- **Qué dice Meta / prensa:** desde ~oct-2025, en Sales y Leads aparece por defecto la casilla "Allow limited spend to excluded placements": hasta **5% del presupuesto por cada placement excluido** si Meta cree que mejora resultados (sin datos públicos de soporte). En 2026, para esos objetivos desaparecen directamente las exclusiones por ad set. [OFFICIAL META] (changelog Marketing API v24.0, 8-oct-2025: `placement_soft_opt_out`, "up to 5% of your spend", Sales y Leads) (S12-089, S12-053, S12-042, S12-012)
- **Veredicto:** **OUTDATED.**
- **Qué hacer:** usar exclusiones a nivel de cuenta para restricciones reales (marca, legal); desmarcar la casilla donde aún exista si la exclusión es dura.

### Bloque H — Cuenta, píxel y "confianza"

#### M58 · "Un píxel nuevo (fresco) funciona mejor"

- **Origen:** creencia de que un píxel "contaminado" por malos eventos o audiencias sesga la optimización.
- **Qué dice Meta:** la optimización se basa en eventos del dataset y señales de la cuenta/página; Meta recomienda **conectar más píxeles a la integración CAPI y compartir más eventos**, no fragmentar. No encontré documentación que hable de "contaminación" ni de reinicio beneficioso. [OFFICIAL META indirecto] (S12-013)
- **Veredicto:** **UNPROVEN** (y con coste probable: pierdes historial y audiencias).
- **Cuándo cambiar de píxel/dataset tiene sentido:** errores graves de configuración imposibles de limpiar, cambio de dominio/negocio, separación legal entre empresas.

#### M59 · "Hay que sazonar (seasoning) el píxel"

- **Formulación:** "Antes de optimizar a compras, corre campañas de tráfico/engagement para calentar el píxel."
- **Evidencia:** Loomer: Meta "nunca ha usado la expresión" en su documentación; el peor rendimiento de píxeles nuevos puede venir de marca nueva, no de "píxel frío"; optimizar a clics puede enviar tráfico de baja calidad. Practitioners en grupos de compradores lo llaman mito. [EMPIRICAL / opinión] (S12-045)
- **Veredicto:** **UNPROVEN.**
- **Qué hacer:** optimizar desde el principio al evento más profundo que puedas alcanzar con volumen (Add to cart/Initiate checkout si Purchase es muy raro), no a clics para "calentar".

#### M60 · "Las cuentas nuevas son castigadas / necesitan warm-up"

- **Qué es cierto:** Meta impone **límites de gasto diario** a cuentas, negocios, páginas o apps nuevos o con problemas de calidad/políticas, que suben con el tiempo si la cuenta está en regla; además, un business portfolio empieza con límite de **una** cuenta publicitaria hasta un pago confirmado. [OFFICIAL META / EMPIRICAL] (S12-068, S12-024)
- **Qué no está demostrado:** que el algoritmo de entrega "castigue" el rendimiento de cuentas nuevas más allá de la falta de historial de eventos y de confianza de integridad.
- **Veredicto:** **CONTEXT-DEPENDENT.**
- **Qué hacer:** planificar el arranque con presupuestos dentro del límite, historial de pago limpio, verificación del negocio y cumplimiento de políticas; no "calentar" con objetivos baratos.

#### M61 · "Abro otra página/cuenta para saltarme límites y me irá mejor"

- **Qué dice Meta hoy:** si creas más páginas para esquivar el límite de anuncios, "podrías perjudicar tu propio rendimiento": compiten en las mismas subastas, se dividen los aprendizajes; el solapamiento puede ocurrir también entre cuentas del mismo anunciante. [OFFICIAL META] (S12-010, S12-008)
- **Veredicto:** **FALSE.**

### Bloque I — Lead generation

#### M62 · "Los leads de formulario instantáneo siempre son malos"

- **Origen:** formularios pre-rellenados sin fricción optimizados a volumen de leads (2017-2022).
- **Qué dice Meta hoy:** existe el objetivo **Maximise number of qualified leads** (antes conversion leads), que optimiza hacia etapas del CRM enviadas por CAPI y "puede usarse con formularios web e instant forms"; desde abril de 2026 no se puede crear sin integración CAPI. Meta reporta −21 % de coste por lead de calidad en instant forms con CAPI CRM y −9,5 % en formularios web frente a optimizar a leads (Help Center), −19 % de media al combinar CAPI CRM y conversion leads y −10 % en Advantage+ leads (30-oct-2025). Ese mismo anuncio retiró el mínimo de 200 leads/mes; la guía de developers aún lo lista junto a etapa ≤28 días y conversión 1-40 %. Los formularios "higher intent" añaden un paso de revisión. [OFFICIAL META] (S12-083, S12-082, S12-085, S12-025)
- **Veredicto:** **FALSE** como "siempre"; **TRUE** que optimizar a "lead" a secas con formulario sin fricción tiende a traer volumen de baja intención.
- **Qué hacer:** fricción deliberada (preguntas cualificadoras), higher intent, integración CRM y optimización a etapa cualificada; comparar con formulario web por **coste por oportunidad**, no por CPL.


### Bloque J — Formatos y tácticas de moda 2025-2026

#### M66 · "Los partnership ads (anuncios con creadores) siempre ganan"

- **Formulación:** "Pasa todo a partnership ads: siempre bajan el CPA."
- **Qué dice Meta:** cifras propias de −19% CPA y +13% CTR frente a anuncios de marca (citadas por prensa; el dato más antiguo con APAC usa tests de jun-2021 a ene-2022). White paper del 7-oct-2026: en **20 conversion lift studies** de anunciantes EMEA (ene-jun 2025), las celdas con ≥30% de activos en formato partnership tuvieron una **mediana** de −45% en coste por compra incremental y +35% de iROAS; confianza declarada del 92% y análisis de la propia Meta. [OFFICIAL META, autoevaluado] (S12-071)
- **Evidencia independiente/vendor:** Agentio (13-ago-2026; 130 M$, 65.000 anuncios, 137 marcas): frente a UGC licenciado publicado desde la cuenta de marca, +19% CTR, +10% CVR, **−5% CPA** y +19% CPM; peor CPA en Stories (+25%). Vendor con interés comercial, método no descrito. [EMPIRICAL débil] (S12-072)
- **Veredicto:** **CONTEXT-DEPENDENT.** Hay señal consistente a favor, pero el tamaño del efecto depende de contra qué se compara (anuncio de marca genérico vs UGC ya bueno) y del placement.
- **Qué hacer:** testear con lift o A/B frente a la *mejor* alternativa (UGC licenciado), no frente a creatividades de marca débiles; vigilar CPM.

---

## Implicaciones operativas

- **Regla de oro anti-mito:** antes de aplicar una "regla" con número (20%, 50, 3, 1%, 8, 6 anuncios), preguntar: ¿aparece en el Help Center actual?, ¿hay un experimento con grupo de control?, ¿en qué tipo de cuenta? Si las tres respuestas son "no", es una heurística local.
- **Estructura:** consolidar por economía (margen/LTV/mercado) y mensaje; no por intereses ni placements. Juzgar CBO a nivel de campaña y placements/anuncios a nivel de ad set (breakdown effect).
- **Ediciones:** agrupar cambios, registrar fecha de cada edición significativa (columna "Last significant edit") y decidir por eventos y gasto, no por días.
- **Escalado:** decidir con coste marginal; subidas graduales cuando el ad set tiene poco volumen; saltos grandes → nueva entidad con presupuesto realista.
- **Creatividad:** priorizar diversidad de concepto sobre volumen de variantes; dimensionar el número de anuncios por presupuesto (que cada anuncio pueda generar señal).
- **Pujas:** lowest cost para arrancar; value/min ROAS cuando hay variación de valor y volumen; caps calibrados con el sesgo observado (el cost cap tiende a pasarse).
- **Medición:** calibrar el ROAS de plataforma con factores de incrementalidad por tipo de campaña; re-calibrar tras los cambios de 2026 (fin de 7d/28d view en API, click-through solo enlace, engage-through).
- **Placements y exclusiones:** en 2026 las restricciones duras se gestionan a nivel de cuenta; revisar casillas por defecto (gasto limitado en excluidos, mejoras creativas activadas automáticamente).

## Errores frecuentes

1. Matar ad sets "Learning limited" rentables por la etiqueta (M03).
2. Comparar CPA de placements o ad sets dentro de CBO y apagar el "peor" (breakdown effect, M11/M55).
3. Duplicar ganadores en paralelo y crear solapamiento de subasta (M10/M32).
4. Leer el ROAS de Advantage+ como prueba de superioridad sin test incremental (M26).
5. Fijar cost caps iguales al CPA deseado y sorprenderse de que el CPA real lo supere (M45).
6. Comparar periodos que cruzan ene/mar-2026 sin homogeneizar ventanas de atribución (M63/M65).
7. Perseguir un EMQ numérico o un CTR "mínimo" en vez del coste por resultado y la calidad post-clic (M38/M49).
8. Tratar el "Creative diversity: Low" o el "Opportunity score" como KPI (M30/M54).
9. Reciclar cifras de vendors ("60% del retargeting no es incremental", "score de similitud >60%") como si fueran de Meta (M23/M30).

## Preguntas abiertas

- ¿Cuál es hoy el umbral real de salida de learning por tipo de campaña? El Help Center dice ~50 resultados/semana; los tests de 10-25 eventos no están confirmados.
- ¿Añadir un anuncio a un ad set activo sigue reiniciando learning (documentación) o ya no (observación 2025)? ¿Depende de la etiqueta *High performing*?
- ¿Cómo calcula Meta la columna *Creative diversity* y afecta a la entrega o solo es diagnóstico?
- ¿Qué parte del view-through/engage-through de 1 día es incremental por vertical?
- ¿La mejora de la atribución incremental en 2025-2026 (Haus) se mantiene fuera de DTC?
- ¿Qué impacto real tiene la eliminación de exclusiones de placement a nivel de ad set en verticales con problemas de calidad (lead gen local, apps)?

## Fuentes clave

- [About the learning phase](https://www.facebook.com/business/help/112167992830700) — sin fecha, consultado 2026-10-15 — meta-oficial
- [Significant edits and learning phase](https://www.facebook.com/business/help/316478108955072) — consultado 2026-10-15 — meta-oficial
- [About learning limited](https://www.facebook.com/business/help/269269737396981) — consultado 2026-10-15 — meta-oficial
- [About ad auctions](https://www.facebook.com/business/help/430291176997542) — consultado 2026-10-15 — meta-oficial
- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051) — consultado 2026-10-15 — meta-oficial
- [About creative fatigue recommendations](https://www.facebook.com/business/help/1346816142327858) — consultado 2026-10-15 — meta-oficial
- [About managing ad volume](https://www.facebook.com/business/help/2720085414702598) — consultado 2026-10-15 — meta-oficial
- [What's new in placement settings](https://www.facebook.com/business/help/1546753450586085) — consultado 2026-10-15 — meta-oficial
- [About Advantage+ audience](https://www.facebook.com/business/help/273363992030035) — consultado 2026-10-15 — meta-oficial
- [About attribution models and settings](https://www.facebook.com/business/help/460276478298895) — consultado 2026-10-15 — meta-oficial
- [The "breakdown effect"](https://www.facebook.com/business/help/770303663944673) — consultado 2026-10-15 — meta-oficial
- [Meta Andromeda (Engineering)](https://engineering.fb.com/2024/12/02/production-engineering/meta-andromeda-advantage-automation-next-gen-personalized-ads-retrieval-engine/) — 2024-12-02 — meta-engineering
- [Meta GEM (Engineering)](https://engineering.fb.com/2025/11/10/ml-applications/metas-generative-ads-model-gem-the-central-brain-accelerating-ads-recommendation-ai-innovation/) — 2025-11-10 — meta-engineering
- [Haus — The Meta Report: 640 experiments](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — practitioner/vendor
- [Haus — Incremental vs standard attribution](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — practitioner/vendor
- [CTC — Taylor and Andrew debate cost controls](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers) — 2026-08-06 — agencia
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor
- [Jon Loomer — The learning phase is just a label](https://pubcast.jonloomer.com/the-learning-phase-is-just-a-label/) — 2025-10-15 — practitioner
- [Jon Loomer — Meta is removing placement controls from ad sets](https://www.jonloomer.com/meta-removing-placement-controls-ad-sets/) — 2026-08-20 — practitioner
- [Gordon, Moakler & Zettelmeyer — Close Enough?](https://pubsonline.informs.org/doi/10.1287/mksc.2022.1413) — 2023 — académico
- Ledger completo: `../fuentes/ledger-12-mitos-contradicciones.md`

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- M30 / TL;DR: añadida la cita oficial de la página *creative differentiation* (S12-105). El veredicto se mantiene, pero la redundancia de creatividades parecidas pasa de [STRONG INFERENCE] a [OFFICIAL META].
- M31: el +15,7 % de conversiones en Facebook (Q2-2026) se atribuye a modelos de comprensión de usuario + GEM + sequence learning, no al Generative Recommender (transcripción verificada).
- M35: añadido el dataset de Biddyco (5-oct-2026), localizado en el ledger del área 03. Es evidencia débil, pero existe.
- M49: corregido "Meta no publica un corte numérico". La guía de developers recomienda EMQ ≥6,0 (S12-111). El mito del 8 sigue siendo UNPROVEN.
- M62: el ≥200 leads/mes se presentaba como recomendación vigente y −15 % como dato de Meta. Sustituido por los datos oficiales: Help Center 782657799338685 y anuncio del 30-oct-2025, que además retira el mínimo.
- M64: decía que Meta atribuye a la fecha de impresión/clic. Es incorrecto para las conversiones web, que se reportan por fecha de conversión (`mixed`; área 04, S04-048/S04-050).
- M57: el 5 % en placements excluidos pasa de "oficial vía prensa" a oficial (changelog v24.0).
- M16: añadida la fecha del cambio de flexibilidad del 25 % al 75 %.
