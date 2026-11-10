# Contradicciones entre expertos serios (Meta Ads 2025-2026)

> Última verificación: 2026-10-15 · Autor: A12 (agente adversarial) · Ámbito: debates abiertos entre Meta, practitioners que publican datos y empresas de medición; contexto en que cada postura acierta.

## TL;DR

- La mayoría de "contradicciones" no lo son: **miden cosas distintas** (coste por resultado atribuido vs incrementalidad; media de muchos anunciantes vs una cuenta concreta; gasto asignado vs rentabilidad). Antes de elegir bando, identificar la métrica. [STRONG INFERENCE]
- **Advantage+ vs manual** es el debate con más evidencia de ambos lados: Meta publica mejoras medias del 7-20% en coste por resultado; Haus encuentra que Advantage+ gana en incrementalidad solo en el 42% de las marcas. Ambos pueden ser ciertos a la vez. [CONTESTED] (S12-020, S12-031)
- **Volumen creativo:** Motion asocia más lanzamientos con más ganadores; Loomer sospecha que demasiados anuncios por ad set confunden la entrega; Meta dice ambas cosas (genera más creatividad / evita volúmenes altos). La variable que los reconcilia es **presupuesto por anuncio**. [CONTESTED] (S12-038, S12-043, S12-006)
- **Pujas:** los datos de CTC 2026 (min ROAS cumple ~96,5% del objetivo; cost cap se pasa ~40%) contradicen la idea de que el cost cap es la herramienta "de precisión". Lowest cost sigue siendo la opción con menor riesgo de infra-entrega. [EMPIRICAL] (S12-036)
- **Atribución incremental de Meta:** Haus pasó de "pierde frente a estándar" (2024-25) a "gana 1,26×" (2025-26). Una contradicción **temporal**: el producto cambió. [EMPIRICAL] (S12-033)
- **Learning phase:** Meta pide no editar en learning; Loomer lo llama "solo una etiqueta". Acierta Meta en ad sets de poco volumen; Loomer en cuentas con volumen y cambios con hipótesis clara. [CONTESTED] (S12-001, S12-039)
- **Placements:** Loomer (rara vez hace falta excluir, salvo AN con objetivos de clic) vs agencias que excluyen AN por defecto; en 2026 Meta zanja parte del debate retirando la exclusión por ad set en objetivos de conversión. [CONTESTED → resuelto parcialmente por producto] (S12-042, S12-012)

---

## 1. Advantage+ (sales/leads/app) vs campañas manuales

| | Postura A: "Advantage+ es mejor" | Postura B: "Manual sigue ganando a menudo" |
|---|---|---|
| Quién | Meta (Help Center, product pages, earnings) | Haus (640 tests), parte de agencias DTC |
| Evidencia | Advantage+ audience −7,2% CPR en ventas, −9,7% leads, −14,8% awareness; Advantage+ placements −10% CPR; Advantage+ sales "−20% CPR de media"; >75.000 M$ run-rate (Q2-2026) | A+ gana en iROAS solo en 42% de los head-to-head; iROAS medio 12% menor; +9% a mitad de test, −12% al final; lift post-tratamiento 17% vs 32%; sobre-reporta ~12 pp más |
| Métrica | Coste por resultado **atribuido**, media de muchos anunciantes | **Incrementalidad** (geo-tests), marcas de ~14 M$/año en Meta |

- **Cuándo acierta A:** cuentas con señal de conversión abundante y catálogo/mensaje homogéneo, equipos pequeños (menos errores de estructura), cuando la alternativa manual es una estructura fragmentada.
- **Cuándo acierta B:** cuando la estructura manual codifica conocimiento de negocio que el algoritmo no ve (márgenes por producto, exclusión de clientes, mercados con distinta economía), marcas omnicanal y con mucho tráfico orgánico/clientes existentes (riesgo de capturar demanda que ya existía).
- **Dato que suele omitirse:** en Haus, las configuraciones **50/50** (mitad A+, mitad manual) rindieron un 18% peor que las sesgadas hacia uno de los dos: el problema puede ser la **fragmentación**, no la tecnología. (S12-031)
- **Cómo decidirlo en una cuenta:** test con métrica incremental (conversion lift o geo-holdout) de ≥3-4 semanas + periodo post; no con ROAS de plataforma.

## 2. Learning phase: ¿regla o etiqueta?

- **Meta:** "espera a editar hasta que salga de learning"; "evita volúmenes altos de anuncios"; "el learning es necesario, no intentes evitarlo del todo". (S12-001)
- **Jon Loomer (oct-2025):** "es solo una etiqueta… el algoritmo siempre está aprendiendo"; un anuncio nuevo en un ad set rentable **no** reinició learning, contra la documentación. (S12-039, S12-040)
- **Reconciliación:** ambos coinciden en "no toquetear"; discrepan en el peso de la etiqueta. Meta escribe para el anunciante medio (pequeño, que edita a diario); Loomer para anunciantes que editan con hipótesis.
- **Cuándo acierta Meta:** <15-20 eventos/semana por ad set, donde cada reinicio cuesta días; ediciones múltiples y descoordinadas.
- **Cuándo acierta Loomer:** ad sets con volumen, cambios necesarios (creatividad fatigada, oferta caducada), cuando la alternativa es "esperar" mientras se pierde dinero.

## 3. Volumen creativo: ¿más anuncios o menos?

- **Motion (Creative Benchmarks 2026):** más creatividades lanzadas → más ganadores absolutos; cuartil superior del tramo 50-200 K$/mes: 15,9 creatividades/semana y 2,0 ganadores/mes vs 6,6 y 0,7 de media. La tasa por creatividad (~5%) no cambia. (S12-038)
- **Jon Loomer (may-2026):** "hay señales de que puedes crear demasiados anuncios… el algoritmo puede perderse con demasiadas opciones para el presupuesto"; es una intuición, no ciencia probada. (S12-043)
- **Meta:** retiró el "≤6 anuncios por ad set" (2025) pero mantiene "demasiados anuncios pueden empeorar el rendimiento"; a la vez, empuja herramientas para "producir más creatividades a escala" (Q2-2026). (S12-006, S12-028)
- **Variable que reconcilia:** *presupuesto por concepto*. Motion mide cuentas que lanzan muchos anuncios a lo largo del tiempo (rotación), no cuántos conviven en un ad set; Loomer habla de anuncios simultáneos por ad set con presupuesto limitado. Además, el "ganador" de Motion se define por gasto asignado por Meta, no por rentabilidad.
- **Cuándo acierta Motion:** cuentas con presupuesto para financiar señal en cada concepto; ciclos de test con corte rápido.
- **Cuándo acierta Loomer:** presupuestos pequeños/medios, muchos anuncios simultáneos en un mismo ad set, conceptos poco diferenciados.

## 4. Diversidad creativa y Andromeda: ¿qué cuenta como "distinto"?

- **Meta:** diversificación creativa como "mejor palanca" (abr-2025); "cuando la creatividad es demasiado parecida, nuestro sistema puede no reconocerla como distinta y entregarla a los mismos públicos" (página *creative differentiation*, S12-105); creatividad "materialmente distinta" contra la fatiga; columna *Creative diversity* (Low/Medium/High, *estimated, in development*, ago-2026 según medios). (S12-070, S12-007, S12-058)
- **Vendors/agencias (p. ej. CTC):** la puntuación "determina cuántos segmentos puede alcanzar ASC", "Entity ID", "doble penalización en Q4". Sin respaldo de Meta. (S12-058)
- **Testimonios en contra:** anunciantes con mezcla de estáticos, vídeo, UGC y carruseles siguen viendo *Low* → la métrica parece visual/estructural, no de formato. (S12-058)
- **Cuándo acierta cada uno:** la dirección (diversificar conceptos y estilos visuales) está respaldada; las cifras y mecanismos de castigo no. Tratar la columna como diagnóstico.

## 5. Estrategias de puja: lowest cost vs cost cap vs bid cap vs min ROAS

- **CTC (ago-2026; 253 cuentas/200 M$ y 320 cuentas/~1.500 M$):** min ROAS ≈ 96,5% del objetivo en agregado (67% de cuentas >5% por debajo de su objetivo); cost per result goal ≈ 140% del objetivo; bid cap ≈ 123% (muestra 3 M$) y es su control por defecto. Taylor Holiday: min ROAS es lo más fiable; Andrew Faris: "bid cap guy", pero los controles importan menos que otros factores. (S12-036, S12-037)
- **Meta:** cost per result goal es una **media** que puede superarse (sobre todo en learning); bid cap no controla el coste por resultado reportado; presupuesto ≥5× el objetivo con cost cap. (S12-011, S12-017)
- **Defensores de lowest cost (muchos practitioners y la propia configuración por defecto):** menos infra-entrega, menos mantenimiento.
- **Cuándo acierta cada uno:** lowest cost para cuentas pequeñas, lanzamientos y cuando el volumen manda; min ROAS cuando el valor por pedido varía y hay volumen; bid cap cuando el negocio prefiere no gastar a gastar caro (y tiene presupuesto amplio para que el cap no ahogue); cost cap como palanca direccional, calibrada con el sesgo observado.

## 6. Atribución incremental de Meta vs atribución estándar

- **Haus 2025 (640 tests):** IA solo superó a la estándar en el 43% de los casos. (S12-031)
- **Haus 2026 (16-jul-2026):** jul-2025/jun-2026, IA **1,26×** el retorno incremental de la estándar (DTC 1,38×; omnicanal ~1,02×); muestra modesta y sesgada a DTC. (S12-033)
- **Lectura:** contradicción temporal, no metodológica; el modelo de Meta cambió. Para omnicanal, empate.
- **Qué hacer:** si se adopta IA, que sea con un test externo propio y sin comparar sus resultados con estándar en la misma tabla (Meta lo desaconseja). (S12-009)

## 7. Ventanas de atribución: ¿1-day click o 7-day click + 1-day view?

- **Stella (46 geo-tests, ene-abr 2025):** marcas <20 M$ a menudo con mejor iROAS usando 7dc/1dv; marcas >400 K$/mes con 1dc mostraron iROAS más alto (correlacional, no causal). (S12-034)
- **Haus:** solo-clic (7d) infra-reporta un 15% de media. (S12-031)
- **CTC:** min ROAS con 7dc/1dv cumplió el 101% del objetivo; con 1dc falló más a menudo. (S12-036)
- **Contexto en que cada uno acierta:** 1dc en marcas grandes con mucha demanda propia (reduce atribución de lo que ocurriría igual); 7dc/1dv en marcas pequeñas o productos de consideración donde el efecto sin clic pesa. Desde 2026 la ventana de visualización máxima es 1 día y aparece engage-through (cambia la comparación histórica). (S12-009, S12-052)

## 8. Exclusión de placements y Audience Network

- **Jon Loomer (ago-2026):** la mayoría que excluye placements no lo necesita; excepción: cuando Meta obtiene acciones baratas y de baja calidad (sobre todo Audience Network con objetivos de clic/LPV/ThruPlay); para conversiones, value rules "rara vez" necesarias y "no universalmente". (S12-042)
- **Agencias de performance y lead gen:** excluyen AN por defecto por fraude/clics accidentales (cifras de fraude sin fuente primaria). (S12-069)
- **Meta (2026):** retira la selección manual en Sales/Leads/App (Engagement no; corrección 2026-11-09); −10% CPR con Advantage+ placements en experimento; exclusiones solo a nivel de cuenta. (S12-012)
- **Cuándo acierta cada uno:** Loomer en objetivos de conversión con buena señal; las agencias en objetivos de tráfico/engagement o en verticales con incentivos de fraude (apps, lead gen barata). La exclusión de cuenta es ahora la herramienta para restricciones duras.

## 9. ¿Dónde se testean las creatividades nuevas?

- **Postura "campaña/ad set de test separado (ABO)":** garantiza gasto al anuncio nuevo y lectura limpia; evita que el ganador acapare entrega.
- **Postura "dentro del ad set que escala":** el sistema decide con más señal; Meta lanzó en 2025 una herramienta de test creativo dentro de Ads Manager; Loomer observó que añadir anuncios ya no reinicia necesariamente learning. (S12-040, S12-039)
- **Cuándo acierta cada una:** si la pregunta es "¿este concepto puede funcionar?", entorno con gasto forzado; si es "¿mejora el rendimiento total?", dentro del sistema que escala. Mezclar ambas preguntas produce conclusiones falsas.

## 10. Broad vs inputs de audiencia

- **Meta:** Advantage+ audience mejor de media, pero **no recomendado para retargeting**; sugerencias guían sin restringir. (S12-020)
- **Loomer (tests):** Advantage+ audience ≈ detailed targeting (diferencia no significativa), > lookalikes; gran varianza entre ad sets idénticos. (S12-046)
- **Practitioners B2B/local/high-ticket:** con evento raro y audiencia direccionable pequeña, los inputs y la creatividad que nombra al segmento siguen marcando diferencia (evidencia anecdótica, sin test público encontrado). [HYPOTHESIS]
- **Cuándo acierta cada uno:** broad en DTC con volumen; inputs/sugerencias y controles en nichos con señal escasa o restricciones.

## 11. Calidad de producción: "ugly ads" vs producción alta

- **Barry Hott:** lo que no parece anuncio detiene el scroll; no todo debe ser feo, pero hay que perder el miedo a lo no pulido. Sin test controlado publicado. (S12-061)
- **Motion 2026:** text-only, producto con texto y UGC lideran tasa de acierto; alta producción es media pero *table stakes* en automoción, tecnología, finanzas y viajes. (S12-038)
- **Cuándo acierta cada uno:** validación rápida de ángulos y DTC de impulso → bajo coste/alta iteración; categorías de confianza/alto ticket → producción como señal de credibilidad.

## 12. ¿La IA generativa rinde peor?

- **TUM/Columbia/HBS (feb-2025, >16.000 M impresiones):** IA iguala o supera si no parece IA. (S12-059)
- **Ipsos/Syracuse (may-2026, 20 anuncios, 3.000 personas):** humanos +11 vs IA −5 en un benchmark de ventas declarativo; IA mejor en briefs de producto, peor en emoción. (S12-060)
- **Meta:** mejoras medias con herramientas IA (+7% conversiones con generación de imágenes; +11% CTR fondos IA). (S12-026, S12-070)
- **Reconciliación:** métricas distintas (CTR de campo vs eficacia declarada), tipos de brief distintos; el "aspecto IA" es la variable común.

## 13. Retargeting: ¿campaña aparte o integrado?

- **Industria/medición:** retargeting con menor incrementalidad; Haus: ~15% del gasto en retargeting en su muestra; Meta no recomienda Advantage+ audience para retargeting. (S12-031, S12-020)
- **Practitioners de ciclos largos:** campañas de objeciones/garantías para quienes ya conocen la oferta.
- **Problema:** las cifras de "60% no incremental" o "40-70% sobre-reportado" no tienen fuente primaria localizable. [UNPROVEN]
- **Cuándo acierta cada uno:** integrado en DTC de compra rápida; separado y pequeño con holdout en high-ticket/B2B.

## 14. ¿Cuánto creer al reporting de plataforma?

- **Gordon, Moakler, Zettelmeyer (2023, 663 experimentos de Facebook):** los métodos observacionales no aproximan bien el efecto real ni con ML; la solución son experimentos. (S12-035)
- **Haus/Stella:** el reporting de Meta puede infra- o sobre-estimar; de media, en sus muestras DTC, infra-estima con clic y queda cerca/por debajo con 7dc/1dv. (S12-031, S12-034)
- **Lectura:** el que dice "Meta miente" y el que dice "Meta infra-reporta" pueden tener razón en cuentas distintas; la única forma de saberlo en una cuenta es un experimento.

## Implicaciones operativas

- Ante un debate, escribir explícitamente: métrica, unidad de análisis (cuenta/ad set/anuncio), horizonte, tamaño de cuenta y vertical de cada fuente.
- Priorizar evidencia experimental (lift, geo) sobre atribución, y atribución sobre opinión.
- Desconfiar de cifras únicas que solo aparecen en vendors que se citan entre sí.

## Errores frecuentes

- Elegir bando por autoridad ("lo dice Meta" / "lo dice X gurú") sin mirar la métrica.
- Tratar resultados de una muestra DTC USA de AOV <150 $ como universales.
- Confundir "gasto asignado por Meta" con "ganador rentable".

## Preguntas abiertas

- ¿La ventaja de la atribución incremental de 2025-26 se replica fuera de DTC y fuera de EE. UU.?
- ¿Existe un tamaño de cuenta a partir del cual Advantage+ gana sistemáticamente en incrementalidad?
- ¿Cuál es la relación real entre número de anuncios simultáneos por ad set y rendimiento, controlando presupuesto?

## Fuentes clave

- [Haus — The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — practitioner/vendor
- [Haus — IA vs standard](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — practitioner/vendor
- [CTC — cost controls data](https://commonthreadco.com/blogs/ecommerce-playbook/taylor-and-andrew-debate-cost-controls-we-ran-the-numbers) — 2026-08-06 — agencia
- [Motion — Creative Benchmarks 2026](https://motionapp.com/library/research/creative-benchmarks-2026/) — 2026 — vendor
- [Jon Loomer — Pubcast: does adding more ads hurt](https://pubcast.jonloomer.com/does-adding-more-ads-actually-hurt-performance/) — 2026-05-06 — practitioner
- [Jon Loomer — Learning phase is just a label](https://pubcast.jonloomer.com/the-learning-phase-is-just-a-label/) — 2025-10-15 — practitioner
- [Meta — About Advantage+ audience](https://www.facebook.com/business/help/273363992030035) — consultado 2026-10-15 — meta-oficial
- [Meta — What's new in placement settings](https://www.facebook.com/business/help/1546753450586085) — consultado 2026-10-15 — meta-oficial
- [Stella — How incremental is Meta really?](https://www.stellaheystella.com/blog/incrementality-study-how-incremental-is-meta-really) — 2025-08-11 — vendor
- [Gordon et al. — Close Enough?](https://pubsonline.informs.org/doi/10.1287/mksc.2022.1413) — 2023 — académico
- Ledger: `../fuentes/ledger-12-mitos-contradicciones.md`

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- §4: añadida la cita oficial de la página *creative differentiation*, que confirma la redundancia de creatividades parecidas.
