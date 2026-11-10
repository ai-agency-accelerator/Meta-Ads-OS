# Eventos de optimización: qué señal le das al algoritmo y qué pasa cuando eliges mal

> Última verificación: 2026-10-15 · Autor: A02 (agente) · Ámbito: elección del evento/goal de optimización (estándar, custom conversions, custom events, CRM/offline, value), trade-off volumen vs proximidad al dinero. La implementación técnica (pixel, CAPI, deduplicación, EMQ) es del área 04; lead gen/CRM a fondo, área 05.

## TL;DR

- **El evento de optimización define a quién busca Meta.** El sistema estima P(evento | impresión) y puja por ello; no sabe si ese evento genera dinero. Optimizar a un proxy barato entrena al sistema a encontrar "gente que hace el proxy". **[OFFICIAL META]** (definición de performance goal, [HC 355670007911605](https://www.facebook.com/business/help/355670007911605)) + **[STRONG INFERENCE]** (consecuencia)
- **Regla por defecto: el evento más profundo (más cerca del dinero) que alcance volumen útil.** Meta recomienda un evento que ocurra "about 50 times per week at a minimum" y, si se predicen cero conversiones, subir a ATC o LPV. **[OFFICIAL META]** ([HC 197634954160445](https://www.facebook.com/business/help/197634954160445))
- **Pero bajar de Purchase a ATC/IC es [CONTESTED]**: Meta lo sugiere como remedio de volumen; practitioners serios (Loomer) lo desaconsejan porque "usually perform poorly" y prefieren aceptar menos volumen u optimizar a un producto/oferta de entrada más barato. La evidencia pública de ambos lados es anecdótica. ([Loomer, 2026-02-02](https://www.jonloomer.com/meta-advertising-budget/))
- **Solo cuentan para el aprendizaje las conversiones dentro de la ventana de atribución elegida** (p. ej. con 1-day click, una compra al tercer día no suma a las 50). **[OFFICIAL META]** ([HC 197634954160445](https://www.facebook.com/business/help/197634954160445))
- **Value optimization** requiere CAPI (obligatorio) + pixel, ≥5 valores distintos, ~100 conversiones en 14 días, y Meta recomienda presupuesto para ≥50 conversiones/semana (≥100 para pLTV/profit) y test de ≥3 semanas sin ROAS goal primero. **[OFFICIAL META]** ([HC 296463804090290](https://www.facebook.com/business/help/296463804090290), [HC 782657799338685](https://www.facebook.com/business/help/782657799338685))
- **Lead gen: el evento "lead" a secas es un proxy débil.** Qualified leads (eventos CRM vía CAPI) es la palanca oficial; desde abril 2026 no se puede crear sin CAPI. Criterios de Meta para conversion/qualified leads: subida diaria, etapa objetivo ≤28 días, tasa de conversión 1-40 %; el mínimo de 200 leads/mes **se eliminó** (Meta, 30-oct-2025) aunque la guía de developers aún lo lista como criterio de "buen encaje"; funciona con instant forms **y formularios web** (Help Center). **[OFFICIAL META]**
- **Custom conversions** = reglas sobre eventos (URL/parámetros) usables como goal "once we've received this custom conversion enough times"; útiles para optimizar a subconjuntos (categoría, valor > X) pero fragmentan volumen. **Custom events** con value optimization deben estar "reviewed" en Events Manager. **[OFFICIAL META]** ([HC 780705975381000](https://www.facebook.com/business/help/780705975381000))
- **Nuevos controles 2025-2026 que cambian "qué cuenta"**: *Conversion count* (All vs First conversion, visto en Sales/Website/Maximize conversions, nov 2025, sin doc oficial) y *Sequenced events* (lead → evento posterior, test oct 2026). Ambos alteran los datos con los que aprende el sistema. **[EMPIRICAL]** (Loomer)

---

## 1. Primeros principios: la señal tiene tres dimensiones

Para cada candidato a evento de optimización, evalúa:

1. **Volumen por ad set y semana** (¿llega el sistema a tener datos para estabilizar? ver archivo 03).
2. **Proximidad al dinero**: P(venta | evento) y, sobre todo, si *quien hace el evento* se parece a *quien compra*. Un proxy puede tener buena tasa media de conversión y aun así degradarse cuando el sistema lo optimiza (efecto Goodhart: el modelo encuentra a los "hiper-realizadores" del proxy, p. ej. gente que añade al carrito por hábito o que rellena formularios por premio).
3. **Latencia y medibilidad**: ¿ocurre dentro de la ventana de atribución (7-day click por defecto)? ¿llega con buena calidad (pixel + CAPI deduplicados)? Un evento que ocurre a los 20 días o que pierde 40 % de señal es peor de lo que su volumen sugiere.

Una heurística útil (no oficial): **señal efectiva ≈ volumen × correlación con valor × fracción medida en ventana**. Bajar en el funnel sube el volumen, pero si la correlación cae más de lo que sube el volumen, empeoras. **[STRONG INFERENCE]**

### Escalera típica (de lejos a cerca del dinero)

```
Impresión → Link click → Landing page view → ViewContent → AddToCart → InitiateCheckout → AddPaymentInfo → Purchase → (Purchase de valor alto / repetición / LTV)
Impresión → Click → LPV → Lead (form) → Lead cualificado (CRM) → Cita (Schedule) → Oportunidad → Venta
```

## 2. Catálogo de eventos y para qué sirve cada uno

| Evento | Dónde se puede optimizar (2026) | Cuándo tiene sentido | Riesgo principal |
|---|---|---|---|
| **Landing Page View** (goal) | Traffic, Engagement, Leads, Sales | Crear audiencias en cuentas sin señal; medios/afiliación; cuando el pixel falla (LPV modelado desde jul 2025) | Tráfico que no compra; placements de clic barato |
| **ViewContent** | Engagement, Leads, Sales (web/app) | Catálogos muy grandes con compra infrecuente (sólo como puente) | Optimiza a "mirones"; casi nunca correlaciona bien con compra |
| **Lead** | Leads (web, website & instant forms) | Servicios, B2B, high-ticket | Leads baratos de baja intención; spam; demografías que rellenan mucho |
| **CompleteRegistration** | Leads, Sales (web/app) | Registro gratuito, webinars, cuentas; Loomer lo usa en vez de Lead para poder usar Sales + audience segments | Igual que Lead si el registro no requiere intención |
| **AddToCart** | Sales (web/app) | Fallback de volumen en tiendas sin compras suficientes (posición de Meta) | Atrae "window shoppers"; **[CONTESTED]** |
| **InitiateCheckout** | Sales | Fallback más cercano que ATC | En Shopify/checkouts express puede disparar de forma irregular (área 04) |
| **AddPaymentInfo** | Sales | Raro; solo si Purchase está mal medido | Volumen similar a Purchase, poco que ganar |
| **Purchase** | Sales, App | Por defecto en e-commerce | Volumen bajo en cuentas pequeñas |
| **Schedule** | Engagement, Leads (web/app) | Clínicas, servicios con agenda online, demo B2B | Si se agenda fuera de la web no se mide sin CAPI |
| **Contact** | Engagement, Leads | Negocios donde el contacto (click-to-call/WhatsApp en web) es la conversión | Contactos poco cualificados |
| **SubmitApplication** | Engagement, Leads | Financiación, educación, empleo (special ad categories) | Calidad variable; restricciones de targeting |
| **StartTrial** | Engagement, Leads, Sales | SaaS/subscripciones | Trials que no convierten a pago; usar value/pLTV si es posible |
| **Subscribe** | Engagement, Leads, Sales | Suscripción de pago | Volumen bajo |
| **Custom conversion** | Donde esté el evento base | Optimizar a un subconjunto (categoría, valor > X, país) | Fragmenta el volumen del evento base |
| **Custom event** | Engagement/Leads/Sales (web) | KPIs propios (p. ej. "lead_calificado", "first_order_new_customer") enviados vía CAPI | Debe estar "reviewed" para value optimization; mal diseñado = señal ruidosa |
| **Eventos CRM / offline** | Leads (qualified leads), Sales (Website & in-store) | Ventas cerradas offline, tiendas físicas | Latencia (≤28 días), cobertura de match, integración |
| **Value (purchase value, pLTV, profit, custom values)** | Sales (web), App (purchase value), Leads (value of conversions) | Dispersión real de valor entre clientes | Más CPA, menos conversiones en learning; requiere ≥50/semana |

Fuentes de la columna "Dónde": [HC 2035196646663270](https://www.facebook.com/business/help/2035196646663270), [HC 355670007911605](https://www.facebook.com/business/help/355670007911605), [HC 782657799338685](https://www.facebook.com/business/help/782657799338685). **[OFFICIAL META]**

## 3. ¿Qué ocurre cuando optimizas al evento equivocado? Casos

### 3.1 Lead barato vs venta (lead gen)

- Mecanismo: el sistema encuentra a quien *rellena formularios* con menor coste. En instant forms con autocompletado, eso sesga hacia personas con mucha actividad y baja intención; Loomer documenta concentración de gasto en 65+ con leads baratos y de mala calidad (≈45 % del gasto en 65+, que redujo a <2 % con value rules −90 %). **[EMPIRICAL]** ([Loomer Master Brief, 2026-07-02](https://www.jonloomer.com/meta-ads-master-brief/))
- Síntoma: CPL baja, tasa de contacto/cita/cierre cae, el comercial se queja, el CAC real sube.
- Remedios (en orden): (1) medir calidad (CRM → CAPI) y optimizar a qualified leads; (2) fricción útil en el formulario (higher intent, preguntas, verificación SMS, email de trabajo), *solo cuando hay un problema demostrado* según Loomer; (3) value rules por edad/placement/conversion location; (4) cambiar a website form si el instant form da peor calidad. **[OFFICIAL META]** + **[EMPIRICAL]**
- Dato oficial: qualified leads con CAPI CRM → −21 % coste por lead de calidad (instant forms), −9,5 % (website forms). Cifras de Meta. **[OFFICIAL META]**

### 3.2 AddToCart en lugar de Purchase

- Posición de Meta: si se predicen cero compras, "instead of a performance goal for purchases, choose for adds-to-cart or page views". **[OFFICIAL META]** ([HC 197634954160445](https://www.facebook.com/business/help/197634954160445))
- Posición contraria: Loomer (feb 2026) desaconseja optimizar a ATC/IC porque "usually perform poorly"; prefiere consolidar en un ad set y aceptar menos compras, u optimizar a una acción más barata *que sea en sí misma valiosa* (producto de entrada, lead). **[EMPIRICAL]**
- Caso publicado: Tracksmith pasó de ATC a Purchase y reportó +24 % ROAS, +7 % ingresos, +14 % AOV (pre/post de 30 días, publicado por su agencia; sin control). **[EMPIRICAL]** baja confianza ([Accelerated Digital Media](https://accelerateddigitalmedia.com/insights/case-studies/optimizing-for-conversions-on-meta))
- Síntesis: **[CONTESTED]**. ATC puede tener sentido como *puente temporal* en una cuenta nueva con 0-5 compras/semana y AOV bajo, si se vigila la tasa ATC→compra de las cohortes atribuidas y se vuelve a Purchase en cuanto haya ~15-25 compras/semana (umbral propio, **[HYPOTHESIS]**). Si la tasa ATC→compra de la audiencia atribuida cae claramente por debajo de la del tráfico orgánico, el proxy se está "gamificando".

### 3.3 Landing Page Views

- Útil: medios, contenido, cuentas sin pixel funcional, construir audiencias.
- Problema: optimiza carga de página; no intención. En campañas Sales/Leads con LPV/link clicks, Loomer recomienda quitar Audience Network. **[EMPIRICAL]**
- Haus: Traffic tiene un "incrementality factor" ~2,4x el de lower-funnel (Meta infra-atribuye su impacto), pero en DTC el iROAS directo sigue por debajo del de conversiones. **[EMPIRICAL]** ([Haus, 2025](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))

### 3.4 Link clicks

- Peor que LPV: incluye clics accidentales; Meta señala que "we may prioritize higher-quality clicks", lo que confirma el problema. **[OFFICIAL META]**

### 3.5 Optimizar a Purchase pero con todos los compradores (incl. recurrentes)

- No es "evento equivocado", pero sí "población equivocada" para un objetivo de adquisición: el sistema prioriza a quien compra con más facilidad (clientes existentes y engaged). Remedios: audience segments para *ver* el reparto; Customer lifecycle strategy "Acquire new customers" (con exclusión automática de compradores de 730 días desde oct 2026) o value rules con audience labels para pagar menos por clientes existentes; evento custom "new_customer_purchase" vía CAPI. Ver archivos 07-09. **[OFFICIAL META]** + **[EMPIRICAL]**

## 4. Custom conversions, custom events, CRM y valor

### Custom conversions
- Reglas sobre un evento (URL contiene, valor > X, etc.); sirven como performance goal una vez acumulan suficientes eventos; permiten compartir solo esa conversión con partners. **[OFFICIAL META]** ([HC 780705975381000](https://www.facebook.com/business/help/780705975381000))
- Úsalas cuando el negocio *de verdad* quiere solo ese subconjunto (p. ej. una línea de producto con margen distinto que tiene su propia campaña) y hay volumen. No las uses para "afinar" sin volumen: partes la señal.

### Custom events
- KPIs propios enviados por pixel/CAPI. Meta los presenta como el valor no-purchase más común para value optimization (filtrar nuevos vs existentes, mercado, línea de producto) y afirma que crear un evento nuevo no afecta a las campañas que optimizan a Purchase. Para maximizar valor de un custom event debe estar revisado en Events Manager. **[OFFICIAL META]** ([HC 296463804090290](https://www.facebook.com/business/help/296463804090290))
- Patrón avanzado: **evento "calidad" diseñado por ti** (p. ej. `QualifiedLead` cuando el lead pasa un scoring, `NewCustomerPurchase` cuando el email no existe en CRM) disparado server-side dentro de la ventana de 7 días. Loomer experimenta con eventos más profundos vía CAPI cuando hay volumen (idealmente 50+/semana). **[EMPIRICAL]**

### Eventos CRM / offline
- Qualified leads: Meta recomienda conectar CRM y enviar cada cambio de estado del lead como evento durante el learning. **[OFFICIAL META]** ([HC 279369167153556](https://www.facebook.com/business/help/279369167153556))
- Requisitos conversion leads (Developers; parcialmente desactualizados: el Help Center ya admite formularios web y Meta retiró el mínimo de 200 leads/mes el 30-oct-2025): instant forms, Lead ID de Meta almacenado en CRM (o click ID/teléfono/email), ≥200 leads/mes, subida ≥1/día, etapa objetivo ≤28 días, tasa de conversión 1-40 %, time-to-value ~3-4 semanas (learning 2-4 semanas). **[OFFICIAL META]** ([Meta Developers](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration))
- Ventas en tienda: Sales → "Website & in-store" con los mismos eventos web. **[OFFICIAL META]**

### Value optimization
- Tipos de valor: purchase/non-purchase values, pLTV (enviado hasta 7 días tras la conversión; modelo validado con ≥5 valores únicos no negativos; ~2 semanas de integración), profit (~1 semana). **[OFFICIAL META]**
- Expectativas: CPA más alto, menos conversiones, mejor ROAS si el valor discrimina; "peak performance is typically reached after 2 weeks"; evaluar con A/B o lift, no con atribución sola. **[OFFICIAL META]**
- Ejemplo oficial: mismo presupuesto de 200 $, 4 compras/250 $ (ROAS 1,25) optimizando a número vs 3 compras/500 $ (ROAS 2,5) optimizando a valor. **[OFFICIAL META]** (ejemplo ilustrativo, no un resultado)
- CTC (2026) parte de "value optimized with minimum ROAS" en ~95 % de sus cuentas de e-commerce. **[EMPIRICAL]** ([CTC, 2026-07-07](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026))
- Cuándo NO: AOV casi constante (no hay nada que discriminar), <50 compras/semana, valor mal enviado (impuestos/envíos inconsistentes).

## 5. Ventana de atribución y "conversion count": lo que cuenta para aprender

- **Solo cuentan las conversiones dentro de la ventana** para el umbral de learning. **[OFFICIAL META]**
- **Cambios 2026 de atribución** (área 04): click-through ahora requiere un clic en enlace; los clics sociales pasan a "engage-through" con ventana de 1 día; default 7-day click, 1-day engage-through, 1-day view (efectivo marzo 2026, según Loomer). Implicación estructural: eventos con latencia >1 día que antes contaban por un "like" ya no cuentan; remarketing es el más afectado. **[EMPIRICAL]** ([Loomer, 2026-03-05](https://www.jonloomer.com/attribution-changes-remarketing-impact/))
- **Conversion count (All vs First conversion)**: visto en Sales → Website → Maximize number of conversions (nov 2025), sin documentación oficial; "First conversion" cambia los datos con los que aprende Meta y reduce el volumen de eventos. Úsese solo si hay volumen de sobra y un problema concreto (p. ej. recompras inflando resultados). **[EMPIRICAL]** ([Loomer, 2025-11-03](https://www.jonloomer.com/conversion-count-first-conversion-optimization/))
- **Sequenced events** (test, oct 2026): optimizar a quien hace evento A y después B (form → cita). Promete resolver el dilema volumen/proximidad en lead gen web sin CRM completo; aún sin doc oficial. **[EMPIRICAL]**

## 6. Árbol de decisión para elegir evento

1. ¿Existe un evento de dinero medible (compra, venta CRM) que llegue en ≤7 días? → Si no, arregla la medición antes de optimizar estructura (área 04).
2. ¿Ese evento alcanza, con el presupuesto consolidado en **un** ad set, ≥~30-50/semana? → Optimiza a él. Si hay dispersión de valor y ≥50/semana → valor.
3. ¿Alcanza 10-30/semana? → Sigue optimizando a él en una estructura de 1 campaña/1 ad set; acepta más varianza; evalúa en ventanas de 7 días tras 2+ semanas (Loomer). **[EMPIRICAL]**
4. ¿Alcanza <10/semana?
   - Lead gen: optimiza a lead con calificación en formulario + monta CAPI CRM para pasar a qualified leads.
   - E-commerce: opciones por orden de preferencia (**[STRONG INFERENCE]**): (a) oferta/producto de entrada más barato para subir volumen de compras reales; (b) subir presupuesto si la economía lo permite; (c) IC/ATC como puente temporal vigilando la tasa proxy→compra; (d) Traffic/LPV solo para construir audiencia y datos, nunca como estado permanente.
5. Revisa cada 2-4 semanas: si el proxy se "gamifica" (cae la tasa proxy→dinero de las conversiones atribuidas), vuelve a un evento más profundo.

## Implicaciones operativas

- Audita en cada cuenta heredada: goal, evento, ventana de atribución, conversion count, y si el evento está bien deduplicado (área 04).
- Un ad set = un evento de optimización. Mezclar ad sets con eventos distintos dentro de una campaña con Advantage+ campaign budget es posible pero Meta recomienda ad set budgets cuando hay "mixed optimization goals or bid strategies". **[OFFICIAL META]** ([HC 214319341922580](https://www.facebook.com/business/help/214319341922580))
- Para lead gen, el KPI de control es coste por lead cualificado / por venta, no CPL. Para e-commerce, nuevo-cliente CPA/nCAC, no ROAS de plataforma.
- No cambies de evento a menudo: "any change to optimization event" es significant edit y reinicia learning. **[OFFICIAL META]** ([HC 316478108955072](https://www.facebook.com/business/help/316478108955072))

## Errores frecuentes

1. Optimizar a ATC/LPV "para salir de learning" sin plan de vuelta.
2. Celebrar CPL bajo sin cruzar con CRM.
3. Crear 5 custom conversions por categoría y una campaña por cada una con 20 €/día.
4. Value optimization con AOV homogéneo o con valores mal enviados.
5. Ignorar la ventana de atribución al estimar si se llega al volumen.
6. Usar Lead en vez de CompleteRegistration y luego no poder usar Sales/segments (o viceversa sin entender la diferencia).
7. Montar qualified leads sin cobertura suficiente (Lead ID no guardado en CRM, subidas semanales en vez de diarias).

## Preguntas abiertas

- ¿Cuál es el umbral real de volumen a partir del cual un evento profundo con poco volumen supera a un proxy con mucho volumen? No hay estudio público controlado; solo casos y opiniones. Merece un experimento propio (A/B con mismo presupuesto, 4+ semanas, medido en ventas de backend).
- ¿Se oficializará "conversion count" y estará en Leads?
- ¿"Sequenced events" requerirá CAPI CRM y cuál será su ventana?

## Fuentes clave

- [Troubleshoot conversion optimization](https://www.facebook.com/business/help/197634954160445) — Meta HC — meta-oficial
- [About performance goals](https://www.facebook.com/business/help/355670007911605) — Meta HC — meta-oficial
- [About custom conversions for web](https://www.facebook.com/business/help/780705975381000) — Meta HC — meta-oficial
- [About maximizing the value of conversions](https://www.facebook.com/business/help/296463804090290) — Meta HC — meta-oficial
- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) — Meta HC (2026) — meta-oficial
- [Set up your CRM for qualified leads](https://www.facebook.com/business/help/279369167153556) — Meta HC — meta-oficial
- [Conversions API for CRM integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — Meta Developers — meta-developers
- [How to Think About Your Meta Advertising Budget](https://www.jonloomer.com/meta-advertising-budget/) — Jon Loomer, 2026-02-02 — practitioner
- [Conversion Count and First Conversion Optimization](https://www.jonloomer.com/conversion-count-first-conversion-optimization/) — Jon Loomer, 2025-11-03 — practitioner
- [Attribution Changes Could Hit Remarketing Hardest](https://www.jonloomer.com/attribution-changes-remarketing-impact/) — Jon Loomer, 2026-03-05 — practitioner
- [Optimizing for conversions on Meta (Tracksmith)](https://accelerateddigitalmedia.com/insights/case-studies/optimizing-for-conversions-on-meta) — Accelerated Digital Media — agencia (baja confianza)
- [How Meta Actually Works in 2026](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026) — CTC, 2026-07-07 — agencia

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Qualified/conversion leads: se presentaban como requisitos vigentes "≥200 leads/mes" e "instant forms". Meta for Business ("More quality leads this Q5…", 30-oct-2025) anuncia "removing the minimum monthly lead volume requirement" y el Help Center "About performance goals for lead ads" (782657799338685, leído 2026-10-16) dice que el objetivo "can be used with both website forms and instant forms". La guía de developers sigue listando 200/mes e instant forms: es documentación desfasada, no un requisito.
