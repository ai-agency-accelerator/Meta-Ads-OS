# Advantage+ sales campaigns para e-commerce (antes: Advantage+ shopping campaigns, ASC)

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: qué es "Advantage+ sales" en 2026, qué automatiza, controles que quedan, tratamiento de clientes existentes, evidencia de rendimiento e incrementalidad, problemas reportados y cuándo usar campañas manuales. Clientes nuevos vs existentes en profundidad: `04-…`. Bidding y escalado general: carpeta 09 (otro agente).

## TL;DR

- **"Advantage+ shopping campaigns" (ASC) ya no existe como tipo de campaña.** Meta lo renombró y fusionó en "Advantage+ sales campaigns" (comunicación del 6-feb-2025, beta desde el 10-feb-2025, despliegue general previsto Q2-2025). Hoy una campaña de Ventas es "Advantage+" cuando tiene activadas tres palancas: **presupuesto Advantage+ (CBO), audiencia Advantage+ y placements Advantage+**. Si desactivas una, sigue siendo una campaña de Ventas, pero `advantage_state = DISABLED`. [OFFICIAL META]
- **Cronología API** [OFFICIAL META]: v24.0 (8-oct-2025) dejó de permitir crear ASC (`smart_promotion_type=AUTOMATED_SHOPPING_ADS`); v25.0 (18-feb-2026) impide crear o actualizar ASC/AAC vía API, extendido a todas las versiones antes del 19-may-2026, y depreca `existing_customer_budget_percentage`; v26.0 (publicada 29-jul-2026): el post de v25 anunciaba que **todas las ASC/AAC restantes se pausarían con v26 (previsto sep-2026)** y la doc de Advantage+ campaigns dice que las campañas con `existing_customer_budget_percentage` se pausan; el changelog de v26 no lo menciona → **verificar en la cuenta si quedan ASC legacy activas**.
- **El "existing customer budget cap" desapareció en la nueva experiencia (feb-2025).** La alternativa oficial de Meta: 2 ad sets bajo presupuesto de campaña — uno que incluye la custom audience de clientes (sin relajación) con `daily_min_spend_target`/`daily_spend_cap`, y otro idéntico que los excluye; misma creatividad en ambos. [OFFICIAL META] Y desde el 6-oct-2026 **Customer lifecycle strategy** ("New customer acquisition") está disponible para todos los anunciantes. [OFFICIAL META vía prensa]
- **Rendimiento: Meta dice que Advantage+ gana; los tests de incrementalidad dicen "depende".** Meta: 4,52 $ de revenue por dólar, +22 % ROAS vs campañas "business as usual" (cifra autodeclarada, metodología no pública). Haus (640 experimentos, 2024-2025): Advantage+ ganó en iROAS solo en el 42 % de marcas; de media **12 % menos iROAS DTC con 18 % menos gasto diario**; el ROAS de plataforma era 2,4 % mejor que el manual → la plataforma sobrerreporta Advantage+ ~12 puntos más que manual. [OFFICIAL META] (claim) / [EMPIRICAL] (Haus) → **[CONTESTED]**
- **Mezclar 50/50 Advantage+ y manual fue lo peor en Haus** (−18 % de iROAS frente a concentrar ≥75 % en el tipo ganador). La decisión de mix debe salir de un test propio, no de un reparto "equilibrado". [EMPIRICAL]
- **Riesgo estructural: sesgo hacia clientes existentes y compradores ya decididos.** Sin control, el sistema encuentra conversiones baratas en quien iba a comprar igual (clientes, visitantes recientes, tráfico de email/SMS). El ROAS sube y el nCAC también. Vigila el reporting por segmentos (Nuevos / Engaged / Existentes) y, sobre todo, tus datos de tienda. [STRONG INFERENCE] + [EMPIRICAL, practitioners]
- **Controles que quedan "duros"**: ubicación, edad mínima, exclusión de custom audiences, idioma; exclusiones de placement **solo a nivel cuenta** (desde ~ago-2026 se retiran los controles de placement a nivel ad set en Ventas); value rules para subir/bajar puja (+1.000 %/−90 %) por edad, género, ubicación, dispositivo, OS, placement y audience labels. Edad/género/intereses/custom audiences de inclusión son **sugerencias**. [OFFICIAL META] + [STRONG INFERENCE] sobre despliegue
- **Atribución 2026**: desde el 12-ene-2026 las ventanas 7-day view y 28-day view ya no están disponibles en Ads Insights API; desde mar-2026 interacciones que no son clic en enlace pasan a "engage-through" en vez de click-through. Esto baja el ROAS reportado sin cambiar las ventas reales. [EMPIRICAL — múltiples fuentes secundarias; verificar doc oficial]
- **Regla práctica**: usa Advantage+ sales como campaña principal de ventas cuando tengas ≥ ~50 compras/semana en la cuenta, catálogo/creatividad variados y control de clientes existentes; mantén campañas manuales (o Advantage+ desactivado en alguna palanca) cuando necesites aislar producto/mercado/margen, probar creatividad, o cuando un test de incrementalidad diga que manual gana. [STRONG INFERENCE]

## 1. Cronología verificada

| Fecha | Cambio | Fuente / etiqueta |
|---|---|---|
| Ago-2022 | Lanzamiento de Advantage+ shopping campaigns (ASC) | Histórico |
| 29-ene-2025 | Se elimina "Audience Types" en catalog ads con objetivo Ventas | Social Media Today [OFFICIAL META vía prensa] |
| 6-feb-2025 / 10-feb-2025 | Meta comunica la consolidación de BAU + ASC en "Advantage+ sales"; beta el 10-feb, rollout previsto Q2-2025. Opportunity Score 0–100. | Foxwell Digital [EMPIRICAL] |
| Feb-2025 | Retirada del Existing Customer Budget Cap en la nueva experiencia | Jon Loomer, AdManage y otros [STRONG INFERENCE — múltiples secundarias coinciden; la doc API lo confirma indirectamente] |
| Jun-2025 | Value rules (ajuste de puja por segmento) | ppc.land, Jon Loomer [EMPIRICAL] |
| v23.0 (2025) | Experiencia "streamlined" Advantage+ para Sales y App en Marketing API | ppc.land [OFFICIAL META vía prensa] |
| 8-oct-2025 (v24.0) | No se pueden crear ASC/AAC con v24; métodos de migración `migrate_to_advantage_plus` disponibles | Meta for Developers [OFFICIAL META] |
| 18-feb-2026 (v25.0) | ASC/AAC no se pueden crear ni actualizar vía API; se extiende a todas las versiones antes del 19-may-2026; `existing_customer_budget_percentage` deprecado (campañas ECBC editables hasta v26; replicarlas duplicando en Ads Manager, vía API o migración masiva para partners); ASC con >50 anuncios por ad set no se pueden duplicar vía API | Meta for Developers (blog v25 y doc Advantage+) [OFFICIAL META] |
| 29-jul-2026 (v26.0) | Publicada v26. Según el post de v25, las ASC/AAC restantes se pausarían en v26 (previsto sep-2026) y la doc indica pausa de campañas con cap de existentes; el changelog de v26 no lo recoge. v26 además: API de gestión de pedidos de Commerce deprecada (bloqueo total 27-oct-2026), Shops ads por defecto `WEBSITE_AND_SHOP` (opt-out), Instagram Explore Feed no disponible como placement explícito, Messenger Stories eliminado | Meta for Developers (changelog v26) [OFFICIAL META] |
| 12-ene-2026 | Retiradas ventanas 7d view y 28d view en Ads Insights API (impacto discutido en Ads Manager) | ppc.land y otros [EMPIRICAL] |
| Mar-2026 | "Engage-through" separado de click-through; Flexible format movido a "Flexible media" dentro de Advantage+ creative | Varias secundarias [EMPIRICAL] |
| Inicio 2026 → 6-oct-2026 | Customer lifecycle strategy ("New customer acquisition") en ad sets de Ventas; GA para todos los anunciantes anunciada en Advertising Week NY | Spilno; Relevant Audience; AI Frontier Review [OFFICIAL META vía prensa] |
| 1-jul-2026 | "Location fees" que repercuten el impuesto digital: 2 % UK, 3 % Francia/Italia/España, 5 % Austria/Turquía (según ubicación de la audiencia) | Storyboard18, The Keyword [OFFICIAL META vía prensa] |
| ~19/21-ago-2026 | Se retiran controles de placement a nivel ad set en Sales/Leads/App promotion (Engagement no; corrección 2026-11-09); quedan exclusiones a nivel cuenta y value rules | CTC; Relevant Audience [OFFICIAL META vía Help Center citado] |

## 2. Qué es técnicamente una campaña Advantage+ sales hoy

Documentación oficial (Advantage+ campaigns, Marketing API) [OFFICIAL META]:

- **Objetivo** `OUTCOME_SALES`. Estado resultante `advantage_state = ADVANTAGE_PLUS_SALES` (análogos: `ADVANTAGE_PLUS_APP` con `APP_INSTALLS`, `ADVANTAGE_PLUS_LEADS` con `OUTCOME_LEADS`). Es de solo lectura: se obtiene configurando las tres palancas. `smart_promotion_type = GUIDED_CREATION`.
- **Presupuesto**: a nivel campaña. Estrategias admitidas: `LOWEST_COST_WITHOUT_CAP` (recomendada), `COST_CAP`, `LOWEST_COST_WITH_BID_CAP`, `LOWEST_COST_WITH_MIN_ROAS`.
- **Audiencia**: Advantage+ audience (`advantage_audience: 1`) **o** solo geo **o** opciones individuales con relajación (Advantage lookalike, Advantage custom audience, Advantage detailed targeting, edad/género como sugerencia). `advantage_audience_state` sigue ENABLED si la edad es por defecto o ≤25 o sugerencia, género por defecto o sugerencia, y no hay inclusión de custom audiences (o solo Advantage custom audience).
- **Placements**: sin targeting ni exclusiones de placement a nivel ad set; las exclusiones a nivel cuenta sí se permiten.
- **Estructura**: ya no está limitado a un ad set; hasta **50 anuncios por ad set** (Meta desaconseja más de ~6 según Jon Loomer). [OFFICIAL META + practitioner]
- **Migración**: copiar-y-migrar o migrar-solo; **ambas reinician la fase de aprendizaje**, sin workaround. [OFFICIAL META]

### Qué automatiza vs qué controlas

| Automatiza Meta | Controlas tú |
|---|---|
| Reparto de presupuesto entre ad sets | Presupuesto total y estrategia de puja (incl. ROAS mínimo / cost cap) |
| Audiencia (todo lo que no sea control duro) | Geo, edad mínima, idioma, **exclusiones** de custom audiences, Customer lifecycle strategy |
| Placements | Exclusiones de placement a nivel cuenta; value rules (bajar hasta −90 %) |
| Variaciones creativas (Advantage+ creative: texto, touch-ups, generación, Dynamic Media) | Qué creatividades/conceptos subes; opt-out de mejoras individuales; palabras restringidas en Branding |
| Qué productos del catálogo enseñar | Product sets, feed, exclusiones de SKUs |
| Rotación de anuncios | Qué anuncios activos/pausados; número de anuncios por ad set |

## 3. Clientes existentes en Advantage+ sales

(Detalle completo en `04-clientes-nuevos-vs-existentes.md`.)

### 3.1 Qué desapareció

El **Existing Customer Budget Cap** (porcentaje máximo del presupuesto para clientes existentes, definido en Configuración de la cuenta → "existing customers") se retiró al consolidar ASC en Advantage+ sales (feb-2025). En API, `existing_customer_budget_percentage` está deprecado desde v25 y en v26 las campañas que lo usan se pausan. [OFFICIAL META]

Un artículo de terceros atribuye a Meta un estudio interno según el cual quitar el cap daba un 13 % menos de coste por compra. No localizado en fuente primaria. [HYPOTHESIS] — y en cualquier caso "coste por compra" incluye compras de clientes existentes: es exactamente la métrica que se ve favorecida al gastar en ellos.

### 3.2 Cómo replicarlo (método oficial)

[OFFICIAL META — doc Advantage+ campaigns]

1. Campaña con presupuesto Advantage+ (CBO).
2. **Ad set A (existentes)**: incluye la custom audience de clientes con `targeting_relaxation_types.custom_audience = 0` (no relajable); fija `daily_min_spend_target` y `daily_spend_cap`.
3. **Ad set B (resto)**: duplicado de A, con la audiencia de clientes en `excluded_custom_audiences`.
4. Misma creatividad en ambos.

Ejemplo: presupuesto 1.000 €/día, quieres ≤15 % en existentes → ad set A con cap diario 150 € (y mínimo, p. ej., 50 €). Lo que no gaste A lo asigna CBO a B.

### 3.3 Customer lifecycle strategy (2026)

- Desplegable a nivel ad set en campañas de Ventas: "Obtener conversiones de todas las audiencias" (defecto) vs **"Adquirir clientes nuevos"** (Meta avisa de que "puede aumentar el coste por resultado"). Despliegue gradual desde inicios de 2026 (Spilno, 24-jun-2026); en Advertising Week (6/7-oct-2026) Meta dijo que está "disponible para todos los anunciantes"; una exclusión con un solo *Audience Label* sigue en test. [OFFICIAL META vía prensa]
- **Cómo funciona (Jon Loomer, 13-oct-2026, observado en Ads Manager)**: al elegir "Adquirir clientes nuevos" aparece una exclusión **automática y no desactivable**: "Customers from your conversion data (730 days)", es decir, quienes dispararon Purchase en los datos de conversión de la cuenta (no tus custom audiences). Ventanas disponibles: **730 (defecto), 180, 90, 60 o 30 días**. Puedes añadir exclusiones manuales de custom audiences (p. ej. lista CRM). [EMPIRICAL — practitioner fiable]
- **[CONTESTED]**: CTC (11-oct-2026) describe "nuevo" como sin compra en 180 días y opciones "solo nuevos / engaged no compradores / todos", y afirma que en ASC existe un "slider de presupuesto para nuevos" (incoherente con la doc oficial, que dice que Advantage+ no soporta el cap de existentes). Prioriza lo observado por Loomer y verifica en tu cuenta.
- Limitaciones señaladas por Loomer: la exclusión fija impide casos como "nuevos para el producto X aunque hayan comprado Y"; ventanas fijas; depende de que el evento Purchase sea fiable.

### 3.4 Reporting por segmentos

Si defines en Configuración de anuncios las audiencias de **Clientes existentes** (compradores web, listas CRM) y **Audiencia con interacción** (engaged), Ads Manager permite desglosar resultados en *Nuevos / Engaged / Existentes* (y a veces *Desconocido*). "Nuevo" = todo lo que no está en las otras dos definiciones → si tu lista está incompleta, clientes reales se cuentan como "nuevos". [OFFICIAL META + practitioner] Meta también permite añadir un parámetro de URL de tipo de audiencia (p. ej. `audience_type=prospecting|retargeting`) para leerlo en analítica. [OFFICIAL META]

## 4. Evidencia de rendimiento

### 4.1 Lo que dice Meta

- "Por cada dólar invertido en productos Advantage+ con IA, los anunciantes generan de media 4,52 $ de revenue", +22 % frente a campañas business-as-usual (2024-2025, repetido en materiales de Meta y earnings). [OFFICIAL META — autodeclarado, metodología no publicada]
- Meta mostró en la interfaz "hasta un 33 % menos de coste por resultado" con Advantage+ audience (captura en Foxwell, feb-2025). [OFFICIAL META — claim de interfaz]
- Run-rate de soluciones end-to-end Advantage+ > 60.000 M$ en Q3-2025 (citado por terceros a partir de la call de resultados). [OFFICIAL META vía secundaria] — indica adopción masiva, no eficiencia para un anunciante concreto.
- Oct-2026: Meta dice que quienes adoptan recomendaciones de su asistente IA ven "un 5 % más de conversiones al mismo coste por conversión". [OFFICIAL META, sin metodología]

### 4.2 Lo que dicen los tests de incrementalidad (Haus, 640 experimentos, publicado 28-jul-2025)

[EMPIRICAL — muestra sesgada a anunciantes grandes: gasto medio ~14 M$/año en Meta]

| Métrica | Advantage+ | Manual |
|---|---|---|
| Marcas con mejor iROAS head-to-head | 42 % | 58 % |
| iROAS DTC medio | −12 % vs manual (con −18 % de gasto diario) | referencia |
| Ventaja a mitad de test | +9 % | — |
| Lift en ventana post-tratamiento | +17 % | +32 % |
| % del impacto en clientes nuevos | 70 % | 65 % |
| Halo omnicanal (retail/Amazon) | +51 % | +43 % |
| ROAS de plataforma | +2,4 % vs manual | — |
| Sobrerreporte relativo | ~12 pp más que manual (por cada 100 $ reportados, manual aporta ~12 $ más de negocio) | — |

Otros hallazgos útiles:
- Reparto 50/50 Advantage+/manual: −18 % de iROAS vs concentrar en uno (más de una docena de marcas).
- Haus recomienda "usar Advantage+ selectivamente para victorias rápidas (p. ej. promociones) y manual para rendimiento sostenido" — recomendación del vendor, no ley universal.
- Contexto 2026: Haus publicó (16-jul-2026) que el ajuste de **Incremental Attribution** de Meta pasó de perder frente a la atribución estándar (0,80× en jul-2024–jun-2025) a ganar (1,26× en jul-2025–jun-2026; 1,38× en marcas solo DTC; ~1,02× en omnicanal). Es decir, el sistema de Meta ha mejorado en 2025-2026 y los resultados de 2025 sobre Advantage+ podrían no ser extrapolables. [EMPIRICAL]

### 4.3 Otras evidencias y claims

- Wicked Reports publicita un análisis de 55.661 campañas según el cual "las campañas manuales superan a Advantage+" en coste de adquisición de clientes nuevos; la cifra que circula (nCAC de Advantage+ de 257 $ en may-2024 a 528 $ en may-2025) no aparece en la página pública (informe tras formulario). Vendor de atribución con interés comercial. [HYPOTHESIS — no verificado]
- Caso único publicado de practitioner con manual 4,77 vs Advantage+ 1,36 de ROAS: anecdótico. [EMPIRICAL, baja]

**Conclusión [CONTESTED]:** Advantage+ sales es, de media, comparable a manual en eficiencia incremental, mejor en algunas cuentas y peor en otras; su ROAS de plataforma está más inflado que el de manual. La única forma de decidir en una cuenta concreta es un test (geo-lift o Conversion Lift) con la métrica correcta (nuevos clientes / revenue incremental / margen).

## 5. Problemas reportados (2025-2026)

| Problema | Mecanismo | Mitigación |
|---|---|---|
| Sobreentrega a clientes existentes y visitantes recientes | El sistema minimiza coste por compra; los ya-casi-compradores son los más baratos | Customer lifecycle strategy; exclusiones; 2 ad sets con cap; leer segmentos y datos de tienda |
| ROAS inflado por view-through y por canales propios (email/SMS) | 1d view atribuye compras de gente que vio el anuncio y compró por email | Comparar ROAS 7d clic vs 7d clic+1d view; nuevo vs recurrente en Shopify; incrementalidad |
| Concentración del gasto en 1–2 anuncios | El sistema explota el anuncio con mejor predicción temprana | Separar test creativo (ad set/campaña de test) y graduar ganadores; vigilar "creative diversity score" (Meta lo introdujo en ago-2026 según CTC, no verificado en doc oficial) |
| Pérdida de control de placements | Retirada de controles a nivel ad set (ago-2026) | Exclusiones a nivel cuenta; value rules −90 %; creatividades nativas para cada placement |
| Reinicio de aprendizaje al migrar ASC legacy | Doc oficial: migración reinicia learning sin workaround | Migrar fuera de picos (no en BFCM), con presupuesto estable |
| Opacidad | Menos breakdowns, más modelado | MER, nCAC y tests de incrementalidad como verdad de negocio |
| Mezcla de productos de bajo margen | Optimiza revenue, no margen | Product sets por margen; ROAS mínimo; value rules; feed con margen en `custom_number` |
| Costes extra en Europa | Location fees 2–5 % desde jul-2026 | Incluir el fee en el cálculo de CAC/ROAS break-even (ver `05-…`) |

## 6. ¿Advantage+ sales o campañas manuales? Matriz de decisión

| Situación | Recomendación | Etiqueta |
|---|---|---|
| Cuenta nueva o < ~20–30 compras/semana | Una sola campaña de Ventas con Advantage+ activado, pocas creatividades fuertes, evento Purchase (o AddToCart si no hay volumen, con cautela) | [STRONG INFERENCE] |
| ≥ 50 compras/semana, catálogo amplio, creatividad variada | Advantage+ sales como campaña principal + control de clientes existentes | [STRONG INFERENCE] |
| Necesitas aislar mercado, producto o margen (p. ej. lanzamiento, línea de alto margen) | Campaña separada (Advantage+ o manual) con product set/ofertas propias | [STRONG INFERENCE] |
| Test creativo estructurado | Ad set o campaña de test separada (presupuesto fijo), luego mover ganadores | [EMPIRICAL, práctica común] |
| Marca con fuerte base de clientes y email/SMS potente | Obligatorio excluir o limitar existentes; medir nCAC | [EMPIRICAL] |
| Omnicanal (Amazon/retail ≥ 25 % ventas) | Evaluar con KPI omnicanal (Haus: ~32 % del impacto de Meta va fuera de DTC; break-even DTC iROAS 0,68×) | [EMPIRICAL] |
| Test de incrementalidad muestra que manual gana claramente en tu cuenta | Concentrar ≥ 75 % en manual (no 50/50) y retestear cada 6 meses | [EMPIRICAL] |
| Promociones cortas / BFCM | Advantage+ suele captar demanda rápido; aun así excluye compradores recientes si el objetivo es adquisición | [EMPIRICAL — Haus recomienda Advantage+ para "quick wins"] |

"Manual" en 2026 significa en la práctica: campaña de Ventas con alguna palanca Advantage+ desactivada (p. ej. presupuesto a nivel ad set, audiencia con controles más estrictos). Ya no existe un "manual puro" como en 2021. [STRONG INFERENCE]

## 7. Configuración recomendada (e-commerce, 2026)

1. **Configuración de cuenta**: definir *Clientes existentes* (compradores 180–730 días vía Pixel/CAPI + lista CRM actualizada, idealmente sincronizada) y *Audiencia con interacción*; exclusiones de placement a nivel cuenta solo si hay motivo de marca; países y edad mínima.
2. **Evento**: Purchase con valor, deduplicado Pixel+CAPI, EMQ alto. Si el volumen es bajo, ver bidding/learning en carpeta 09.
3. **Campaña principal**: Advantage+ sales, presupuesto de campaña, lowest cost al inicio; ROAS mínimo o cost cap cuando haya histórico estable y margen conocido.
4. **Ad sets**: 1 (simple) o 2 (nuevos vs existentes con cap) o 1 con Customer lifecycle strategy = New customer acquisition si el objetivo es adquisición pura.
5. **Creatividad**: 6–15 conceptos distintos (no variaciones del mismo); mezcla de vídeo, estático, carrusel, catálogo; partnership ads/creadores. Ver carpeta 03 (creatividad).
6. **Catálogo**: activado si hay catálogo sano (match ≥ 90 %).
7. **Medición**: reporting por segmentos + nuevos vs recurrentes en tienda + MER + nCAC semanales; test de incrementalidad al menos semestral.

## 8. Lectura de resultados: qué mirar y en qué orden

1. **MER y margen de contribución** de la semana (verdad de negocio).
2. **Nuevos clientes (tienda) y nCAC** = gasto en adquisición / clientes nuevos (definición en `05-…`).
3. **% de gasto e ingresos atribuidos a existentes** (breakdown de segmentos) vs % de recurrentes en tienda.
4. **ROAS 7d clic** y **ROAS 1d clic** (sensibilidad a la ventana; Dr. Squatch encontró con Haus que optimizar a 7DC dio +6,51 % de revenue nuevo frente a 1DC, contra la intuición del equipo). [EMPIRICAL]
5. **Frecuencia, CPM, CTR de enlace, CVR** para diagnóstico.

## Implicaciones operativas

- Da por hecho que ASC legacy no existe: migra fuera de temporada alta (reinicia aprendizaje).
- Sustituye el cap de existentes por: Customer lifecycle strategy **o** la estructura oficial de 2 ad sets **o** exclusión total si el objetivo es solo adquisición.
- Mide Advantage+ vs manual con incrementalidad y concentra (≥ 75 %) en lo que gane; evita el 50/50 "por si acaso".
- Incluye location fees (2–5 % en UK/FR/IT/ES/AT/TR) en el CPA objetivo de Europa desde jul-2026.
- Con las ventanas de vista recortadas (ene-2026) y el engage-through (mar-2026), recalibra objetivos de ROAS de plataforma comparando con periodos previos en ventanas equivalentes.

## Errores frecuentes

- Comparar el ROAS de Advantage+ con el de manual sin mirar % existentes ni incrementalidad.
- Dejar que la campaña principal gaste 40–60 % en clientes existentes mientras email/SMS ya los está convirtiendo.
- Lanzar 40 variaciones casi idénticas del mismo anuncio (el sistema las trata como una).
- Migrar o reestructurar la campaña principal en noviembre.
- Usar ROAS mínimo agresivo sin histórico → la campaña no gasta.
- Asumir que "Advantage+ = sin control": exclusiones, product sets, ofertas y creatividad siguen siendo palancas fuertes.

## Preguntas abiertas

- Confirmación oficial de la lógica de Customer lifecycle strategy (Loomer observa exclusión automática por Purchase con 730/180/90/60/30 días; CTC habla de 180 días) y si afecta solo a entrega o también a reporting.
- Si las ASC/AAC legacy restantes se han pausado ya con v26 (anunciado en el post de v25, no recogido en el changelog de v26).
- Si la mejora 2025-2026 de Incremental Attribution (Haus) se traslada a Advantage+ sales frente a manual: no hay estudio head-to-head actualizado a 2026.
- Confirmación oficial del "Creative Diversity Score" y de su efecto en entrega.
- Estado de value rules en catalog ads y su interacción con Customer lifecycle strategy.
- Cifras de Wicked Reports sobre nCAC (informe cerrado).

## Fuentes clave

- [Advantage+ Campaigns (Marketing API)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers, consultado 2026-10-15 — meta-developers
- [Introducing Graph API v25.0 and Marketing API v25.0](https://developers.facebook.com/blog/post/2026/02/18/introducing-graph-api-v25-and-marketing-api-v25) — 2026-02-18 — meta-developers
- [Graph API changelog v26.0](https://developers.facebook.com/docs/graph-api/changelog/version26.0/) — 2026-07-29 — meta-developers
- [Meta Adds Automatic Customer Exclusions (Jon Loomer)](https://www.jonloomer.com/meta-automatic-customer-exclusions/) — 2026-10-13 — practitioner
- [Meta's Customer Lifecycle Strategy Is Now Live for All Advertisers (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-customer-lifecycle-strategy-all-advertisers-bfcm-2026) — 2026-10-11 — agencia
- [Meta deprecates legacy campaign APIs for Advantage+ structure](https://ppc.land/meta-deprecates-legacy-campaign-apis-for-advantage-structure/) — 2025-10 — prensa
- [Meta Updates Marketing API To Align With Latest Ad Shifts](https://www.socialmediatoday.com/news/meta-updates-marketing-api-to-align-with-latest-ad-shifts/812648/) — 2026 — prensa
- [Meta's New ASC System (Foxwell Digital)](https://www.foxwelldigital.com/blog/metas-new-ad-campaign-type-what-it-is-why-it-matters-and-how-to-make-it-perform) — 2025-02-10 — agencia
- [Advantage+ Sales Replaces Advantage+ Shopping (Jon Loomer)](https://www.jonloomer.com/qvt/advantage-sales-replaces-advantage-shopping/) — 2025 — practitioner
- [Advantage+ Campaign Creation: A Complete Guide (Jon Loomer)](https://www.jonloomer.com/advantage-plus-campaign/) — 2025 — practitioner
- [The Meta Report (Haus)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Is Meta's Incremental Attribution Outperforming Standard Attribution? (Haus)](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — vendor
- [Haus customer story: Dr. Squatch](https://www.haus.io/customer/dr-squatch) — 2025-05-22 — vendor
- [Meta's New Ad Tools at Advertising Week 2026: Live vs Testing](https://www.relevantaudience.com/meta/meta-advertising-week-new-york-2026-ad-tools/) — 2026-10 — agencia
- [Meta Ads' New Setting: "New Customer Acquisition"](https://spilnoagency.com.ua/en/news-en/meta-ads-new-customer-acquisition) — 2026-06-24 (act. 2026-10-10) — agencia
- [Every Meta Ads Change in 2026 (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026) — 2026 — agencia
- [Meta restricts attribution windows in Ads Insights API](https://ppc.land/meta-restricts-attribution-windows-and-data-retention-in-ads-insights-api/) — 2026-01 — prensa
- [Meta to charge advertisers 2–5% location fee](https://www.storyboard18.com/digital/meta-to-charge-advertisers-2-5-location-fee-in-select-countries-to-offset-digital-service-taxes-91778.htm) — 2026 — prensa
- [Wicked Reports — Meta Advantage+ Report (landing)](https://www.wickedreports.com/meta-advantage-report) — 2026 — vendor
- [Audience type URL parameters](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-shopping-campaigns/audience-type-url-parameters.md) — Meta for Developers — meta-developers
