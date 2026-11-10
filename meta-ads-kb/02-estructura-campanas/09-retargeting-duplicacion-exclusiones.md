# Retargeting, exclusiones y duplicación en 2026: cuándo separar, cuándo dejar que Meta lo haga y qué rompe duplicar

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ámbito: campañas de retargeting/remarketing y retención, exclusiones de clientes y engaged, Customer lifecycle strategy, solapamiento (auction overlap), duplicación de campañas/ad sets. Medición de incrementalidad: área 04. Catálogo/e-commerce: área 06.

## TL;DR

- **Meta ya hace remarketing dentro de las campañas de prospección**: con Advantage+ audience prioriza a personas con actividad en pixel, conversiones e interacciones. Loomer observa típicamente **20-30 % del presupuesto de Sales en engaged/existentes sin ningún input** (rango 10-40 %); Haus midió **~15 % de gasto en retargeting** tanto en Advantage+ como en manual. **[EMPIRICAL]** ([Loomer 19 Rules](https://www.jonloomer.com/19-rules-of-successful-meta-advertising/), [Haus](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))
- **Por tanto, una campaña de retargeting separada ya no es "obligatoria"**; por defecto crea auction overlap, audiencias pequeñas con frecuencia alta y resultados inflados por view-through y por gente que compraría igual. **[EMPIRICAL]** + **[OFFICIAL META]** (overlap)
- **Pero no es "nunca"**: tiene sentido cuando (1) quieres **garantizar** inversión/mensaje para un segmento de alto valor que Meta infra-atiende (carritos en catálogos grandes, high-ticket con objeciones, upsell "tiered"), (2) la **retención/reactivación** tiene economía propia en una base de clientes grande, o (3) el reporting de audience segments muestra que Meta gasta **demasiado poco** en engaged para tu ciclo de venta. Si lo haces, Meta **no recomienda Advantage+ audience para retargeting**: restringe la audiencia. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Mide antes de separar**: define *audience segments* (engaged / existing) y mira qué % de gasto y resultados va a cada uno; decide con incrementalidad (holdout/lift), no con ROAS atribuido. Los cambios de atribución de marzo 2026 (engage-through a 1 día; click requiere link click) golpean más a remarketing. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Exclusiones de clientes en 2026**: Customer lifecycle strategy → "Acquire new customers" (Sales) con exclusión **automática** de compradores de 730 días (no desactivable en ese modo; ventanas 730/180/90/60/30) desde oct 2026 + custom audiences adicionales (útil para ventas offline) + opción de excluir también engaged. Exclusiones "legales y operativas" en el bloque de audiencia. Alternativa sin excluir: **value rule** −X % sobre clientes (audience labels). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Excluir no siempre es mejor**: en productos de recompra, los clientes pueden ser rentables e incrementales; Loomer recomienda excluir solo ante un problema demostrado (sobre-frecuencia, AOV menor, compras que habrían ocurrido igual) y recuerda que es "virtually impossible to successfully exclude everyone". **[CONTESTED]** frente a CTC, que separa adquisición/retención por defecto en marcas grandes.
- **Duplicar**: crea un objeto nuevo → learning nuevo; si la audiencia coincide, Meta solo deja entrar en cada subasta el anuncio de mayor valor del anunciante ("your ads will not bid against one another"), así que duplicar no "gana más subastas": reparte las mismas y fragmenta aprendizaje. **[OFFICIAL META]** ([HC 537699989762051](https://www.facebook.com/business/help/537699989762051))
- **Duplicar sí tiene sentido** para: tests A/B formales, cambiar ajustes no editables (p. ej. >70 ad sets con campaign budget, migrar ECBC), abrir una "superficie de puja" con otra bid strategy en cuentas grandes, o lanzar un mercado nuevo. **No** para "escalar" un ganador ni "resetear" fatiga. Ojo: duplicar una campaña manual en Ads Manager la crea con Advantage+ on. **[OFFICIAL META]** + **[EMPIRICAL]**

---

## 1. Por qué cambió el retargeting

1. **Advantage+ audience incorpora la intención**: "Past conversions, Meta Pixel data, Interactions with previous ads" son señales explícitas. **[OFFICIAL META]** ([HC 273363992030035](https://www.facebook.com/business/help/273363992030035))
2. **Audiencias de retargeting más pequeñas y peor medidas** (iOS/ATT, cookies, consentimiento, y en la UE la opción "less personalized ads" desde enero 2026). **[STRONG INFERENCE]**
3. **Atribución**: el retargeting históricamente "se llevaba" conversiones view-through y de clics sociales; desde marzo 2026 los clics sociales son "engage-through" con ventana de 1 día y el click-through exige link click. Loomer: "Attribution changes could hit remarketing hardest". **[EMPIRICAL]** ([Loomer, 2026-03-05](https://www.jonloomer.com/attribution-changes-remarketing-impact/))
4. **Incrementalidad**: varias fuentes secundarias reportan que el iROAS del retargeting suele estar muy por debajo de su ROAS atribuido (cifras dispares: 30-70 % de sobre-reporte; un caso geo-lift con prospección iROAS 3,8 vs retargeting 3,2 pese a ROAS de plataforma 4,5 vs 7,8). **[EMPIRICAL]** baja confianza (cifras no reconciliadas; principio robusto: el retargeting atribuido sobreestima).

## 2. ¿Separar retargeting? Árbol de decisión

1. **¿Tienes audience segments definidos?** Si no → defínelos (engaged = visitantes/ATC/engagement/leads no compradores; existing = compradores 730 d + CRM). **[OFFICIAL META]** ([HC 1212227546879178](https://www.facebook.com/business/help/1212227546879178))
2. **Mira 4 semanas de breakdown por segmento** en Sales: % gasto y % conversiones en new / engaged / existing.
3. Casos:
   - **Engaged + existing reciben 10-40 % del gasto y el negocio es de compra única o de bajo ciclo** → no separar; si existing es alto, excluir/ value rule.
   - **Engaged recibe muy poco (<5-10 %) y tu ciclo de consideración es largo** (high-ticket, B2B, viajes) → considerar ad set/campaña de retargeting con presupuesto acotado y mensajes específicos (objeciones, prueba social, garantía).
   - **Existing recibe mucho y el negocio es de recompra** → decidir entre (a) campaña de retención propia con su KPI (coste por recompra/reactivación, margen), (b) value rule a la baja, (c) excluir en adquisición. Medir con holdout.
   - **Catálogo grande con mucho abandono** → Advantage+ catalog ads ya hace remarketing dinámico en la campaña de ventas; separar solo si quieres garantizar presupuesto para carritos recientes y lo pruebas con holdout.
4. **Presupuesto**: si el retargeting separado no alcanzaría ~50 eventos/semana, probablemente es mejor no separarlo (learning limited + overlap). **[STRONG INFERENCE]**

## 3. Cómo montar retargeting cuando sí procede

| Paso | Recomendación | Etiqueta |
|---|---|---|
| Audiencia | Custom audiences con "Further limit the reach" + **desmarcar "Use as a suggestion"** (Advantage+ audience off; Meta no lo recomienda para retargeting) | [OFFICIAL META] |
| Objetivo | Sales (conversiones) si hay volumen; **Awareness + Maximize reach + frequency cap** para modelos "tiered" o audiencias pequeñas (patrón Loomer) | [EMPIRICAL] |
| Prospección | Excluir la audiencia de retargeting en el ad set de prospección **solo si** quieres separar limpiamente el gasto; si no, deja que la prospección también remarketee | [EMPIRICAL] (Loomer) |
| Presupuesto | Acotado (ad set con max spend dentro de campaign budget, o ad set budget); Meta: con campaign budget los ad sets de audiencia pequeña reciben poco | [OFFICIAL META] |
| Creatividad | Específica para la etapa (objeciones, reseñas, oferta, recordatorio del producto visto) | [STRONG INFERENCE] |
| Ventanas | Ajustadas al ciclo (p. ej. 7-30 d e-commerce; 30-180 d high-ticket) | [STRONG INFERENCE] |
| Medición | Holdout (excluir 10-20 % de la audiencia aleatoria vía lista) o conversion lift; mirar resultados por click vs view/engage | [STRONG INFERENCE] |

## 4. Exclusiones de clientes y engaged

### 4.1 Herramientas (estado oct 2026)

| Herramienta | Qué hace | Notas |
|---|---|---|
| **Customer lifecycle strategy** (Sales) | "Get conversions from all audiences" vs **"Acquire new customers"** (excluye existentes; opcionalmente engaged) | Meta: "specialized treatments to enhance exclusion coverage"; CPA puede subir; evaluar con métricas de nuevo cliente. **[OFFICIAL META]** ([HC 1740191093676743](https://www.facebook.com/business/help/1740191093676743)) |
| **Exclusión automática "Customers from your conversion data (730 days)"** | Excluye quienes dispararon Purchase en la cuenta; ventanas 730/180/90/60/30 d; fija en modo "Acquire new customers" | Oct 2026. No permite excluir solo compradores de un producto. **[EMPIRICAL]** ([Loomer, 2026-10-13](https://www.jonloomer.com/meta-automatic-customer-exclusions/)) |
| **"Legal and operational custom audience exclusions"** | Exclusiones en el bloque de audiencia (controles) | Tooltip redirige a CLS para clientes; ambas vías coexisten. **[EMPIRICAL]** ([Loomer, 2026-06-04](https://www.jonloomer.com/customer-lifecycle-strategy-not-what-advertisers-thought/)) |
| **Exclusion-only custom audiences** | Listas que solo pueden excluir (opt-outs, obligaciones legales) | No LAL, no value rules. **[OFFICIAL META]** |
| **Controles de cuenta** | Exclusiones de marca/empleados para todas las campañas | No aplican a SAC/política. **[OFFICIAL META]** |
| **Value rules con audience labels** | Pagar menos (o más) por clientes en vez de excluirlos | Meta: "Include lower-value audiences… with a reduced bid". **[OFFICIAL META]** |
| **App install status** | "Any" / "Not installed" en controles | Visto en 2026; sustituiría exclusiones por app activity. **[EMPIRICAL]** |

### 4.2 ¿Excluir o no? (de qué depende)

| Factor | Inclina a excluir | Inclina a NO excluir (o value rule) |
|---|---|---|
| Tipo de compra | Única (colchón, curso, servicio puntual) | Recurrente (consumibles, moda, alimentación) |
| Objetivo de negocio | nCAC / crecimiento de base | Ingresos totales / LTV |
| Incrementalidad medida en existentes | Baja (comprarían igual vía email/orgánico) | Alta |
| Calidad de la lista | Completa (online + offline + marketplace) | Incompleta (excluir mal crea falsa sensación de control) |
| Tamaño de la base | Grande | Pequeña (excluir apenas cambia nada) |
| Prueba social | Irrelevante | Los clientes comentan/positivan los anuncios (Loomer) |

Patrones:
- **Adquisición pura**: CLS "Acquire new customers" + lista CRM offline + ventana acorde al ciclo de recompra.
- **Todo en uno con control**: "Get conversions from all audiences" + value rule −20/−50 % en "General customers" + segments para vigilar.
- **Grandes marcas (CTC)**: evergreen dividido en adquisición (con exclusiones) y retención (existentes) con objetivos distintos. **[EMPIRICAL]**

**[CONTESTED]**: Loomer (excluir solo ante problema probado; preferir value rules) vs CTC (separar ACQ/RET por defecto en cuentas grandes). Ambos coherentes con su contexto: la separación compensa cuando la base es grande y la economía de retención es claramente distinta y medible.

## 5. Duplicación: qué hace y qué rompe

### 5.1 Hechos oficiales
- Duplicar crea nuevos objetos (campaña/ad set/anuncio) con la misma configuración; se puede **conservar el engagement** (reacciones/comentarios) en anuncios duplicados (una sola vez si hay creatividad personalizada por placement). **[OFFICIAL META]** ([HC 209669919072999](https://www.facebook.com/business/help/209669919072999))
- **Campañas creadas con ajustes manuales se duplican con Advantage+ on**; "Duplicate with recommendations" puede aplicar cambios. **[OFFICIAL META]**
- Un objeto nuevo entra en learning (es "un nuevo ad set"). **[OFFICIAL META]** ([HC 112167992830700](https://www.facebook.com/business/help/112167992830700))
- **Auction overlap**: si dos ad sets del mismo anunciante entran en la misma subasta, se elige el de mayor valor total; los otros no participan → "ensures that your ads will not bid against one another", pero puede impedir gastar el presupuesto o salir de learning; separar en otra ad account no lo evita. **[OFFICIAL META]** ([HC 537699989762051](https://www.facebook.com/business/help/537699989762051))

### 5.2 Mitos y realidades

| Creencia | Veredicto | Explicación |
|---|---|---|
| "Duplicar un ad set ganador escala sin tocar el original" | **FALSE / OUTDATED** | Nuevo learning + overlap con el original; mejor subir presupuesto (o budget scheduling) del existente. Foxwell: "scaling in place… tends to hold performance more steadily than duplicating a winning campaign". [EMPIRICAL] |
| "Duplicar resetea la fatiga creativa" | **FALSE** | La fatiga es de la audiencia con la creatividad; el duplicado muestra lo mismo a la misma gente |
| "Mis ad sets compiten y suben mi CPM" | **CONTEXT-DEPENDENT** | Meta dice que no pujan entre sí, pero el overlap limita la entrega y el aprendizaje; el efecto neto suele ser peor CPA |
| "Duplicar campañas en otra ad account evita el overlap" | **FALSE** | Meta puede identificar que son el mismo anunciante |
| "Duplicar para probar otra bid strategy" | **CONTEXT-DEPENDENT** | Patrón de cuentas grandes (CTC "bid surface expansion") con el mismo pool creativo; en cuentas pequeñas, fragmenta |
| "Duplicar ad sets con distintos intereses para encontrar la audiencia" | **OUTDATED** | Intereses = sugerencias; Meta recomienda combinar ([HC 2419480091640105](https://www.facebook.com/business/help/2419480091640105)) |

### 5.3 Cuándo sí duplicar
1. **A/B tests** (herramienta Experiments) con hipótesis y potencia.
2. **Cambios no editables**: campaña con >70 ad sets y campaign budget (no se puede apagar CBO ni cambiar bid strategy), migración de campañas legacy ECBC a Advantage+ (solo por duplicación en Ads Manager). **[OFFICIAL META]**
3. **Nuevo mercado/idioma** con economía distinta (o mejor, nuevo ad set).
4. **Superficie de puja** en cuentas grandes (mismo creativo, distinta bid strategy) con vigilancia de overlap.
5. **Plantillas**: reutilizar configuración para campañas de calendario.

### 5.4 Diagnóstico de solapamiento
- Recomendaciones de opportunity score (fragmentación/overlap), reglas automáticas para detectar y combinar ad sets fragmentados, herramienta de audience overlap. **[OFFICIAL META]**
- Síntomas: varios ad sets "Learning limited" con el mismo goal; CPM al alza al añadir ad sets; gasto que no se consume.

## Implicaciones operativas

- Por defecto: **sin campaña de retargeting separada**; audience segments activos; revisión mensual del reparto.
- Si separas retargeting: audiencia restringida, presupuesto acotado, creatividad específica y **holdout**.
- Exclusiones: completar la definición de clientes (pixel 730 d + CRM + offline); elegir entre excluir y value rule según la tabla de 4.2.
- Duplicar solo con uno de los 5 motivos de 5.3; escalar en sitio.

## Errores frecuentes

1. Campaña de retargeting de 7 días de visitantes con 30 €/día "porque siempre se ha hecho".
2. Medir retargeting con ROAS 1-day view incluido y decidir presupuesto con ello.
3. Excluir compradores solo vía pixel cuando el 40 % de ventas es offline/marketplace.
4. Duplicar el ad set ganador 3 veces "para escalar".
5. Usar Advantage+ audience (sugerencias) en una campaña que se cree "de retargeting".
6. No mirar el breakdown new/engaged/existing de Advantage+ sales.

## Preguntas abiertas

- Magnitud real de la incrementalidad del retargeting en 2026 tras los cambios de atribución y la opción LPA en la UE (no hay estudio público reciente con método claro).
- ¿Permitirá Meta exclusiones automáticas por producto/categoría (Loomer lo echa en falta)?
- ¿Cuánto "remarketing implícito" hace Advantage+ en lead gen (audience segments solo están en Sales)?

## Fuentes clave

- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051) — Meta HC — meta-oficial
- [How to duplicate ad campaigns](https://www.facebook.com/business/help/209669919072999) — Meta HC — meta-oficial
- [Create a campaign to acquire new customers](https://www.facebook.com/business/help/1740191093676743) — Meta HC — meta-oficial
- [Create audience segments](https://www.facebook.com/business/help/1212227546879178) — Meta HC — meta-oficial
- [About Advantage+ audience](https://www.facebook.com/business/help/273363992030035) — Meta HC — meta-oficial
- [Combine ad sets and campaigns](https://www.facebook.com/business/help/2419480091640105) — Meta HC — meta-oficial
- [Meta Adds Automatic Customer Exclusions](https://www.jonloomer.com/meta-automatic-customer-exclusions/) — Jon Loomer, 2026-10-13 — practitioner
- [Customer Lifecycle Strategy Is Not What Advertisers Thought](https://www.jonloomer.com/customer-lifecycle-strategy-not-what-advertisers-thought/) — Jon Loomer, 2026-06-04 — practitioner
- [A Guide to Meta Ads Targeting in 2026](https://www.jonloomer.com/meta-ads-targeting-2026/) — Jon Loomer, 2026-03-24 — practitioner
- [Attribution Changes Could Hit Remarketing Hardest](https://www.jonloomer.com/attribution-changes-remarketing-impact/) — Jon Loomer, 2026-03-05 — practitioner
- [The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
- [How Meta Actually Works in 2026](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026) — CTC, 2026-07-07 — agencia
- [The 9 Most Pressing Meta Ad Topics for Q3 2026](https://www.foxwelldigital.com/blog/the-9-most-pressing-topics-for-meta-advertisers-in-q3-2026) — Foxwell, 2026-07-03 — agencia
