# Implicaciones para el anunciante: cómo pensar y decidir como Head of Performance con el sistema de Meta de 2026

> Última verificación: 2026-10-16 · Autor: A01 (agente) · Ámbito: síntesis accionable del área 01 (subasta, delivery, ML, historia). Remite a los archivos 01-08 para la evidencia.

## TL;DR

- **Tu trabajo ya no es decirle a Meta a quién mostrar el anuncio; es darle (1) un objetivo que represente valor real, (2) señal limpia y rápida de ese objetivo, (3) un inventario de creativos semánticamente diversos, (4) restricciones solo donde el negocio lo exige, y (5) medir si lo que Meta atribuye es incremental.** **[STRONG INFERENCE]** a partir de toda la evidencia oficial.
- **El coste por resultado lo decide sobre todo tu tasa de acción estimada (EAR) frente a la competencia por cada persona**, no tu puja. EAR = creativo × oferta × landing × calidad de señal. **[OFFICIAL META]** (componentes de total value; probabilidades usadas en pricing).
- **CPMs al alza son estructurales** (+12% precio medio por anuncio YoY en H1-2026). Presupuestar con ello y defender eficiencia vía CVR y creativo. **[OFFICIAL META]**
- **La creatividad es la nueva segmentación**, y "diversidad" significa diversidad semántica (ángulo, persona, problema, formato, contexto), no micro-variantes. **[OFFICIAL META]**
- **Menos estructura, más señal**: pocos ad sets, sin solapamientos, sin duplicados; dejar estabilizar. **[STRONG INFERENCE]**
- **El control manual se está retirando a gran velocidad** (exclusiones DT 2025, opciones DT ene-2026, placements por ad set oct-2026); los controles que quedan son de **valor** (value rules, ROAS goal, cost cap) y **restricciones duras a nivel de cuenta**. **[OFFICIAL META]**
- **La atribución de Meta es parte del sistema que optimiza**, no un juez neutral: validar con Lift/geo-holdouts y considerar *incremental attribution* como objetivo. **[OFFICIAL META]** + **[EMPIRICAL]**

---

## 1. El modelo mental en 12 principios

1. **Cascada, no algoritmo**: retrieval → early ranking → late ranking → subasta → reglas → feedback. Cada etapa puede excluirte por razones distintas. (03)
2. **Subasta por total value**: puja × EAR, ajustado por calidad; pagas lo mínimo para ganar. (02)
3. **EAR por persona**: Meta modela miles de eventos por usuario; tu segmentación aporta poca información incremental. (04, 05)
4. **El creativo opera en retrieval (semántica), ranking (EAR + calidad) y post-clic (CVR).** (03, 07)
5. **Similitud semántica = mismo público**: creativos demasiado parecidos se tratan como uno a efectos prácticos. (04)
6. **El sistema explota lo que predice bien**: concentración de gasto es normal; exploración sesgada por predicción. (05)
7. **El evento de optimización define lo que el sistema aprende** (Goodhart). (05)
8. **Las conversiones también actualizan la representación del usuario**: señal rápida y correcta tiene valor doble. (04, 05)
9. **Pacing**: lowest cost convierte presupuesto en puja; más presupuesto compra oportunidades marginalmente peores. (06)
10. **Presupuesto diario = semanal** (+75% día, 7× semana). (06)
11. **Calidad y feedback negativo encarecen todo y se contagian a la cuenta.** (07)
12. **Meta mejora el sistema cada trimestre**; los "updates" no se anuncian como eventos; la competencia recibe las mismas mejoras. (01, 04, 08)

## 2. Reglas de decisión (qué hacemos / qué evitamos / umbrales orientativos)

| Decisión | Regla por defecto | Excepción / umbral | Evidencia |
|---|---|---|---|
| Segmentación | Broad/Advantage+ audience con controles duros (geo, idioma, edad mínima, exclusión de custom audiences cuando proceda) | Cuenta nueva o señal escasa: usar sugerencias como prior; B2B/alto ticket: testear segmentaciones con medición incremental | **[CONTESTED]** (08 §3) |
| Evento de optimización | El más cercano al valor con ~50 eventos/semana por ad set | Volumen insuficiente: subir de evento o consolidar; lead gen: CRM/conversion leads | **[OFFICIAL META]** + **[EMPIRICAL]** |
| Estructura | 1 campaña por objetivo/mercado/margen; pocos ad sets; sin solapamiento | Separar solo por diferencias de negocio reales (margen, geo, catálogo, idioma) o necesidad de lectura | **[STRONG INFERENCE]** |
| Creativos | Cadencia semanal/quincenal de conceptos nuevos; ≥20 anuncios diversificados en campañas Advantage+ sales (Meta 2024); 20-30% del presupuesto a testing | Volúmenes pequeños: menos anuncios pero muy distintos | **[OFFICIAL META]** |
| Testing creativo | Elegir entre consolidado (eficiente) o aislado (lectura limpia) según volumen y objetivo de aprendizaje | A/B de Meta mide "anuncio + algoritmo" (entrega divergente) | **[CONTESTED]** / **[OFFICIAL META]** |
| Puja | Highest volume (lowest cost) por defecto; cost cap/ROAS goal cuando hay margen conocido y volumen | Bid cap para eventos puntuales/accelerated | **[OFFICIAL META]** |
| Value rules | Usarlas para expresar diferencias de valor por segmento/placement conocidas (p. ej. márgenes por geo, LTV por edad) | No sirven para exclusión total (máx. −90%) | **[OFFICIAL META]** |
| Presupuesto | Juzgar en ventanas de 7 días; cambios agrupados, al inicio del día; respetar el máximo "sin re-entrar en aprendizaje" de Ads Manager | Picos estacionales: aceptar CPMs altos o planificar antes | **[OFFICIAL META]** |
| Placements | Advantage+ placements; adaptar creativos a 9:16/4:5/1:1 | Requisitos de brand safety/cumplimiento: controles de cuenta (el ad set ya no permite excluir en muchos objetivos) | **[OFFICIAL META]** |
| Calidad | Cero engagement bait, cero clickbait, landing coherente y rápida | — | **[OFFICIAL META]** |
| Medición | Lift test o geo-holdout al menos trimestral para el canal; evaluar incremental attribution | Cuentas pequeñas: holdouts geográficos simples o pruebas on/off | **[EMPIRICAL]** |

## 3. Diagnóstico por síntoma (razonando desde el sistema)

| Síntoma | Hipótesis por orden de probabilidad | Qué mirar | Acción |
|---|---|---|---|
| **El ad set no gasta** | (1) Restricción de puja/cost cap/ROAS por debajo del mercado; (2) audiencia/placements demasiado restringidos; (3) creativos poco recuperables o redundantes con otros ad sets (auction overlap); (4) problemas de revisión/calidad | Estrategia de puja, tamaño estimado, diagnóstico de solapamiento, estado de entrega | Relajar cap, ampliar restricciones, conceptos nuevos, consolidar ad sets |
| **Un anuncio se lleva el 80-90% del gasto** | Comportamiento esperado: EAR predicho superior y/o el resto es semánticamente redundante | ¿Los demás son micro-variantes? ¿CPA del ganador estable? | No apagar el ganador; añadir conceptos realmente distintos |
| **Anuncios nuevos no reciben impresiones** | Predicción inicial baja frente al ganador; redundancia semántica | Diferencias reales de concepto; ¿se parecen a algo que ya no funcionó? | Conceptos nuevos; si hace falta lectura, test aislado con presupuesto forzado |
| **CPM sube** | (1) Estacionalidad/competencia; (2) el sistema te sirve a personas de mayor intención (bueno si CPA aguanta); (3) audiencia efectiva pequeña; (4) calidad baja | CPM vs CPA vs CVR; relevance diagnostics; mix de placements | Si CPA estable: no tocar. Si CPA sube: creativo/oferta/calidad |
| **CPA sube al escalar** | Rendimientos decrecientes del pacing; re-entrada en aprendizaje | Magnitud de la subida, estado de aprendizaje, frecuencia | Subidas más graduales; ampliar techo con nuevos conceptos/mercados |
| **"Learning limited"** | Volumen de eventos insuficiente para el ad set | Eventos/semana, nº de ad sets, evento elegido | Consolidar, subir de evento o aceptar varianza |
| **"Creative fatigue/limited"** | Concepto agotado o creativos demasiado similares al mismo público | Antigüedad y diversidad del inventario creativo | Conceptos nuevos, no clones |
| **Broad "no funciona"** | Evento mal alineado, señal pobre, creativo genérico, cuenta sin historia | Calidad de leads/compras, EMQ, mensaje del creativo | Arreglar evento/señal/creativo antes de restringir |
| **ROAS de plataforma alto pero negocio plano** | Atribución de no incrementales (clientes existentes, demanda de marca) | % clientes existentes, Lift/geo test | Controles de clientes existentes, incremental attribution, holdouts |
| **A/B test con resultados raros** | Entrega divergente (cada celda se entrega a públicos distintos) | Balance de edad/género en el informe | Igualar configuraciones o usar Lift |
| **Cambio brusco sin tocar nada** | Lanzamiento trimestral de Meta, competencia, estacionalidad, tracking | Fechas, otras cuentas, Events Manager | No reaccionar en <3-7 días salvo rotura de tracking |

## 4. Auditoría de cuenta "desde el sistema" (checklist)

1. **Objetivo/evento**: ¿representa valor? ¿volumen suficiente? ¿valores reales?
2. **Señal**: pixel + CAPI deduplicados, EMQ, latencia, eventos de CRM en lead gen.
3. **Estructura**: nº de campañas/ad sets, solapamientos, duplicados, fragmentación por audiencias.
4. **Restricciones**: ¿cada restricción responde a una necesidad de negocio? ¿se usan value rules en vez de exclusiones?
5. **Inventario creativo**: nº de conceptos distintos (no anuncios), formatos, antigüedad, cadencia, % del gasto en el top-1.
6. **Calidad**: engagement bait, clickbait, landing (5 atributos), feedback negativo, comentarios.
7. **Pacing**: estrategia de puja, frecuencia de ediciones, uso de caps.
8. **Medición**: última prueba de incrementalidad, atribución configurada (cambios 2026), uso de incremental attribution.
9. **Contexto**: estacionalidad, mercado (UE/LPA), cambios recientes de Meta.

## 5. Qué vigilar en 2026-2027 (radar)

- **Meta Generative Recommender / LLMs en retrieval** (Q2-2026): el contenido semántico del creativo pesa aún más; vigilar si cambia la concentración de gasto y la entrega de anuncios nuevos.
- **GEM central único** (oct-2026): aprendizaje transversal FB/IG/Reels y objetivos; más razones para placements y estructuras abiertas.
- **Retirada de controles** (placements por ad set oct-2026, opciones DT ene-2026): adaptar procesos de brand safety a nivel de cuenta.
- **Automatización end-to-end** (objetivo declarado: "conecta tu cuenta bancaria"): Advantage+ por defecto, creativos generados (Muse Image), agentes (AI connectors, business assistant). Decidir qué se delega y cómo se audita.
- **Atribución 2026** (fin de ventanas view largas, engage-through): reportes con menos conversiones; no confundir con caída real.
- **UE/LPA** y nuevas señales (chats con Meta AI fuera de la UE): rendimiento heterogéneo por mercado.
- **Earnings Q3-2026** (finales de oct-2026): nuevas cifras de modelos y de precio por anuncio. **Actualización 2026-11-09**: publicados el 21-oct-2026 (precio por anuncio +14 %, impresiones +10 %; GEM +1,7 % offsite y +9,6 % apps; Andromeda +1,4 %; retrieval generativo en el Feed de FB ~+2 %). [OFFICIAL META] (S10-117 en `fuentes/ledger-10-cambios-api-ia.md`)

## 6. Afirmaciones que otras áreas deben contrastar

- **Área 03 (creatividad)**: umbrales concretos de "similarity score" (65%) y número óptimo de anuncios por ad set no son públicos; solo hay recomendaciones oficiales genéricas (≥20 en ASC, nuevos semanales).
- **Área 04 (tracking/atribución)**: cambios de ventanas (12-ene-2026) y engage-through (3-mar-2026) proceden de agencias; verificar en documentación de Meta. iOS 26 (Link Tracking Protection) y su impacto real en fbclid.
- **Área 09 (bidding/escalado)**: "20% cada 3 días" es folklore; la referencia oficial es el aviso de Ads Manager de máximo sin re-aprendizaje.
- **Área 11 (benchmarks)**: los lifts de Meta (+5%, +15,7%, +18,9%) no son benchmarks para cuentas individuales.
- **Área 12 (mitos)**: "Andromeda update de oct-2025" como evento único; "Entity ID" como término oficial; "broad siempre gana".

## Errores frecuentes (síntesis)

- Luchar contra el sistema (micro-segmentar, duplicar, editar a diario) en lugar de alimentarlo.
- Confundir volumen de anuncios con diversidad.
- Optimizar un proxy barato y juzgar por atribución de plataforma.
- Reaccionar a CPM en vez de a CPA incremental.

## Fuentes clave

Ver archivos 01-08 de esta carpeta y el ledger `fuentes/ledger-01-subasta-delivery-ml.md` (S01-001 a S01-0xx).
