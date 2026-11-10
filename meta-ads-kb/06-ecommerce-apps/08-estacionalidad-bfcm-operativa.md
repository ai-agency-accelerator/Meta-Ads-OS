# Estacionalidad e-commerce en Meta: BFCM, Navidad/Reyes, enero, rebajas y verano (operativa)

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: planificación operativa de creatividades, ofertas, catálogo y presupuesto en picos estacionales para e-commerce. La dinámica de subasta/CPM estacional en profundidad la cubre otro agente (carpetas 01/09); aquí se usan los datos solo para decidir.

## TL;DR

- **Calendario 2026**: Thanksgiving 26-nov, **Black Friday 27-nov**, **Cyber Monday 30-nov**. En España, el ciclo de regalos se extiende hasta **Reyes (6-ene)** y las rebajas de invierno arrancan tradicionalmente el 7-ene. [Calendario]
- **BFCM sube el CPM pero baja el CPA**: en cuentas grandes de EE. UU. (oct-2025 → ene-2026, Biddy Co), el CPM de marcas de consumo subió +35 % la semana de BFCM y +57 % en Black Friday, pero la tasa de conversión subió +226 % en BF y el CPA bajó −42 % en BF y −20 % en la semana. **Juzga BFCM por CPA/ROAS y margen, no por CPM.** [EMPIRICAL]
- **La semana peor es la segunda de diciembre**: 8–14 dic 2025 → CPA +39 %, conversión −13 %, ROAS −27 % frente a octubre, con CPM aún +6 %. Cambia a mensajes de regalo y fechas límite de envío, o baja presupuesto. [EMPIRICAL]
- **Finales de diciembre y enero son baratos para prospectar**: CPM −24 % (29-dic a 4-ene) y −17 % en enero; CPA −24 % y −7 %. Momento para testear creatividad y adquirir clientes para el año. [EMPIRICAL]
- **Triple Whale BFCM 2025** (>33.000 tiendas): CPM de Meta +7,8 % (22,26 $), ROAS 2,26 (+3,18 % vs 2024), AOV mediano 77,79 $, Meta = 67,6 % del gasto rastreado. Distinto método que Biddy Co (media del periodo vs día concreto). [EMPIRICAL vía resumen secundario — página original bloqueada]
- **Meta divide la temporada en 4 fases** — descubrimiento (oct–inicio nov), ofertas (BFCM), regalos (diciembre), "fresh start" (finales dic–enero) — y recomienda lanzar pronto para completar el aprendizaje antes del pico, con Advantage+ y varios formatos creativos. [OFFICIAL META vía Social Media Today, 13-ago-2026]
- **Un CPA más bajo en BFCM no garantiza más beneficio**: el descuento comprime el CM2. En el ejemplo de §4, un 25 % de descuento baja el CPA break-even de 30 € a 19,45 €; con una caída de CPA del −20 % (de 25 € a 20 €) la semana de BFCM, **el primer pedido pasa a perder dinero**, mientras que el día de BF (−42 %) sí gana. [STRONG INFERENCE — cálculo]
- **Riesgo de atribución máximo**: en BFCM 2025 el revenue de recurrentes creció +13,5 % y email/SMS fueron el 42 % del revenue (Klaviyo vía AdBeacon). Meta reclama parte de esas compras vía view-through. Refresca la lista de clientes existentes antes de noviembre y fija techo de nCAC. [EMPIRICAL vía vendor]

## 1. Datos de referencia (BFCM 2025 y post-temporada)

### 1.1 Biddy Co — cuentas grandes de EE. UU. (≥ 30.000 $ de gasto en oct-2025; ~6,9 M$/mes combinados), cada cuenta vs su propio octubre, mediana [EMPIRICAL]

| Periodo | CPM | CPA | Otras |
|---|---|---|---|
| Oct → inicio nov | ≈ plano | — | — |
| 17–23 nov | +9 % | −16 % | — |
| **24–30 nov (BFCM)** | **+35 %** | **−20 %** | — |
| 1–7 dic | +27 % | −8 % | — |
| **8–14 dic** | +6 % | **+39 %** | CVR −13 %, ROAS −27 % |
| 15–21 dic | +3 % | +8 % | — |
| 22–28 dic | −8 % | −26 % | — |
| 29 dic–4 ene | −24 % | −24 % | — |
| Enero (5-ene–1-feb) | −17 % | −7 % | — |

| Día | CPM | CVR | CPA |
|---|---|---|---|
| Thanksgiving | +30 % | +87 % | −10 % |
| **Black Friday** | **+57 %** | **+226 %** | **−42 %** (AOV +11 %, ROAS +82 %) |
| Sábado | +57 % | +88 % | −16 % |
| Domingo | +45 % | +71 % | −22 % |
| Cyber Monday | +41 % | +153 % | −32 % |

Apps y servicios: CPM +16 % en semana BFCM, +60 % en BF, pico +35 % en 15–21 dic (para ellos, mitad de diciembre es lo peor). [EMPIRICAL]

### 1.2 Otras referencias

- Triple Whale BFCM 2025 retrospective: ver TL;DR. Año completo 2025: CPM +~20 % interanual con CPA solo +1 % (panel Triple Whale). [EMPIRICAL vía secundaria]
- Adobe: 44,2 mil M$ de gasto online en la Cyber Week 2025 en EE. UU. (+7,7 %). [EMPIRICAL vía AdBeacon]

**Límite**: datos de EE. UU. Para España/UE no he encontrado un dataset público equivalente 2025 con esta granularidad; el patrón cualitativo (CPM↑, CVR↑↑ en BFCM; caída de CPM tras Navidad) es consistente con lo que reportan agencias europeas, pero **el pico de regalo en España se desplaza hacia Reyes** y enero no es "muerto" (rebajas). [HYPOTHESIS para la magnitud en España]

## 2. Las fases y qué hacer en cada una

| Fase (Meta) | Fechas 2026 orientativas | Objetivo | Creatividad | Oferta | Presupuesto |
|---|---|---|---|---|---|
| **Preparación** | Ago–sep | Producción y tests | Probar ángulos y formatos; producir variantes BFCM | Definir ofertas y márgenes | Base |
| **Descubrimiento** | Oct–~15 nov | Llenar el embudo; capturar emails/SMS para BFCM; terminar aprendizaje | Producto, regalo, creadores; Meta recomienda creatividades de creadores en Advantage+ lanzadas a mediados de octubre (Holiday Insights Center, según CTC) | Lead magnets / acceso anticipado | Base → +20–50 % |
| **Pre-BFCM** | 16–25 nov | Calentar; early access | Teasers, cuenta atrás, "early access" | Early access a lista | +50–100 % (CPA aún favorable: −16 % en 17–23 nov) |
| **Ofertas (BFCM)** | 26-nov → 1-dic | Conversión máxima | Oferta clara en los primeros 2 s; precio tachado; overlays de catálogo | Descuento/bundles | ×2–3 sobre base mientras CPA marginal ≤ break-even con descuento |
| **Regalos** | 2–~18 dic (UE: hasta ~3-ene por Reyes) | Regalo + fechas de envío | Guías de regalo, "llega antes de…", tarjetas regalo | Envío exprés, packs regalo | Bajar en la semana 8–14 dic si CPA se dispara; reasignar a tarjetas regalo |
| **Fresh start** | 26-dic → enero | Adquisición barata; rebajas | Propósitos de año nuevo, rebajas (España 7-ene) | Rebajas | Subir prospección: CPM −17 a −24 % |

## 3. Operativa por bloque

### 3.1 Creatividad (el cuello de botella)

- Calendario: briefs a T−8/10 semanas, producción a T−6, testeo en octubre a T−4/6, **anuncios BFCM listos antes del 17-nov** (los costes empiezan a subir esa semana). [EMPIRICAL — Biddy Co recomienda creatividad de temporada activa a principios de noviembre]
- Tres capas de creatividad: (1) evergreen ganadores (mantener), (2) temporada (regalo, invierno), (3) oferta BFCM (precio/descuento muy visible).
- Lanzar los anuncios de oferta en **ad sets/campañas que ya están fuera de aprendizaje** cuando sea posible (añadir anuncios no reinicia el aprendizaje del mismo modo que cambiar la estructura; ver carpeta 02/09) — evita crear estructuras nuevas el mismo día de BF. [STRONG INFERENCE]
- Volumen: a gasto ×2–3, la fatiga se acelera; prepara 2× los anuncios de un mes normal.

### 3.2 Catálogo y feed

- `sale_price` + `sale_price_effective_date` programados con inicio y fin; Batch API o feed horario durante BFCM. [OFFICIAL META]
- Product set "BFCM" con `internal_label` (productos en promoción con stock suficiente). [OFFICIAL META — internal_label se actualiza sin revisión de políticas]
- Excluir SKUs con stock bajo para no pagar por clics a productos agotados.
- Overlays de descuento en catálogo; revisar que el precio del overlay = precio en web (price mismatch = rechazos).

### 3.3 Ofertas y margen

- Calcula CM2 con descuento y el nuevo CPA break-even **antes** de decidir la profundidad del descuento (ver §4).
- Prefiere bundles y regalos a descuento porcentual puro cuando el margen es justo.
- Si usas "Highlight your promotions"/ofertas sincronizadas, revisa qué códigos expone Meta.

### 3.4 Clientes existentes

- Lista de clientes existentes fresca (≥ 2 años) subida a principios de noviembre. [EMPIRICAL, vendor]
- Decide explícitamente: ¿la campaña principal de BFCM es de adquisición (excluir existentes / Customer lifecycle = nuevos) y la base se trabaja por email/SMS + campaña de retención acotada? Es lo recomendable si email/SMS es fuerte. [STRONG INFERENCE]
- Fija **techo diario de nCAC** y recorta prospección si se supera.

### 3.5 Presupuesto y puja

- Escalar presupuesto mientras el **CPA marginal** (no el medio) esté por debajo del break-even con descuento.
- Cost cap / ROAS mínimo: útiles para proteger margen en días de CPM extremo, pero con riesgo de infra-entrega; prepáralos con histórico. Ver carpeta 09.
- Evita cambios estructurales (nuevas campañas, migraciones de ASC legacy, cambio de evento) en noviembre: la migración a Advantage+ reinicia aprendizaje. [OFFICIAL META]

### 3.6 Medición

- Ventanas: compara 7d clic vs 7d clic + 1d vista durante BFCM (el view-through se dispara con los recurrentes).
- Nuevos vs recurrentes en tienda diario.
- Meta recomienda Conversion Lift para medir la temporada; si no hay presupuesto, al menos un holdout geográfico de retargeting. [OFFICIAL META vía prensa]

## 4. Ejemplo numérico: ¿compensa el CPA bajo de BFCM con el descuento?

Base (octubre), por pedido (sin IVA):
- Revenue 60 €; COGS 15 €; fulfilment 8 €; pago 1 €; provisión devoluciones 6 € → **CM2 = 30 € (50 %)**.
- CPA break-even (sin f) = 30 €; CPA real octubre = 25 € → beneficio 5 €/pedido en el primer pedido.

BFCM (25 % de descuento; cesta de valor de lista +11 %, como el AOV +11 % de BF en Biddy Co):
- Valor de lista 66,60 € → revenue 49,95 €.
- COGS 16,65 €; fulfilment 8 €; pago 0,85 €; devoluciones (10 % del revenue, sube en temporada) 5,00 € → **CM2 = 19,45 € (38,9 %)**.
- CPA break-even = **19,45 €** (antes 30 €).

| Escenario | CPA (vs oct 25 €) | Resultado por pedido |
|---|---|---|
| Black Friday (−42 %) | 14,50 € | **+4,95 €** |
| Cyber Monday (−32 %) | 17,00 € | +2,45 € |
| Media semana BFCM (−20 %) | 20,00 € | **−0,55 €** |
| 1–7 dic (−8 %) | 23,00 € | −3,55 € |
| 8–14 dic (+39 %) con oferta aún activa | 34,75 € | −15,30 € |

Lecturas:
1. El pico de BF/CM es rentable incluso con descuento fuerte; la semana completa con descuento del 25 % roza la pérdida en primer pedido.
2. Mantener el descuento en diciembre a CPA creciente destruye margen: es el momento de quitar descuento y vender por regalo/envío.
3. Si los clientes captados en BFCM recompran como los de octubre, el LTV puede justificar pérdidas de primer pedido; si son "cazadores de ofertas" (recompra menor), no. **Mide la recompra a 90 días de la cohorte de BFCM vs la de octubre.** [STRONG INFERENCE]

## 5. Otros picos (España/UE)

| Evento | Fecha | Notas operativas |
|---|---|---|
| Rebajas de invierno | Desde ~7-ene | CPM bajo + intención alta: buen momento de adquisición y liquidación; actualizar `sale_price` |
| San Valentín | 14-feb | Regalo; plazos de envío |
| Día del Padre (ES) | 19-mar | Regalo masculino |
| Día de la Madre (ES) | 1.er domingo de mayo (3-may-2026; 2-may-2027) | Uno de los picos de regalo más fuertes en belleza/joyería |
| Rebajas de verano / Prime Day | Julio | Competencia de Amazon; precio |
| Vuelta al cole | Septiembre | Papelería, moda infantil, tecnología |
| Singles' Day | 11-nov | Arranque de temporada en algunos verticales |
| Black Friday / Cyber Monday | 27–30 nov 2026 | Ver arriba |
| Navidad / Reyes | 24–25 dic / 6-ene | En España el gasto en regalos se extiende hasta Reyes: el "fresh start" de Meta (EE. UU.) llega más tarde |

## Implicaciones operativas

- Creatividad BFCM lista antes del 17-nov; estructura congelada desde principios de noviembre.
- Presupuesto por CPA marginal con el break-even **con descuento**, no el habitual.
- Segunda semana de diciembre: quitar descuento o bajar inversión; mensajes de regalo/envío.
- Enero: aprovechar CPM bajo para adquisición y test creativo (y rebajas en España).
- Lista de clientes fresca, techo de nCAC y lectura nuevos vs recurrentes diaria.

## Errores frecuentes

- Juzgar BFCM por CPM.
- Lanzar campañas nuevas el mismo día de Black Friday.
- Mantener el descuento de BFCM hasta mediados de diciembre.
- No actualizar `sale_price` en el feed (overlays con precio incorrecto, rechazos).
- Atribuir a Meta el pico de recurrentes que trajo el email.
- Ignorar que en España la campaña de regalos dura hasta Reyes.

## Preguntas abiertas

- Datos públicos de CPM/CPA estacional 2025 específicos de España/UE.
- Confirmación oficial del "Holiday Insights Center" (ago-2026) y de sus recomendaciones de calendario.
- Calidad (recompra) de cohortes de BFCM vs cohortes normales: no hay estudio público reciente; medir en cada cuenta.

## Fuentes clave

- [Meta Ads During Black Friday: What Happened to CPM and CPA in 2025 (Biddy Co)](https://www.biddyco.com/blog-posts/meta-ads-black-friday-cpm) — 2026-10-05 — agencia
- [Black Friday Facebook Ads: Data, Strategies… (Triple Whale)](https://www.triplewhale.com/blog/facebook-ads-bfcm) — 2025-2026 — vendor (consultado vía resumen de búsqueda; acceso bloqueado)
- [Meta publishes holiday marketing guides (Social Media Today)](https://www.socialmediatoday.com/news/meta-publishes-holiday-marketing-guides/827856/) — 2026-08-13 — prensa
- [Every Meta Ads Change in 2026 (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-ads-changes-2026) — 2026 — agencia
- [Is Meta Taking Credit for Your Holiday Repeat Buyers (AdBeacon)](https://www.adbeacon.com/meta-attribution-new-vs-returning-customers-bfcm/) — 2026-10-07 — vendor
- [Catalog fields reference (sale_price_effective_date)](https://developers.facebook.com/docs/marketing-api/catalog/reference) — Meta for Developers — meta-developers
- [Advantage+ Campaigns (migración reinicia aprendizaje)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
