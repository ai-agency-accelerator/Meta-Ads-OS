# Arquitectura de campañas en 2026: patrones, cuándo usar cada uno y de qué depende

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ámbito: diseño de la estructura de campañas/ad sets: single campaign, multi-campaña, prospecting/retargeting, Advantage+ (sales/leads/app), campaign budget vs ad set budget vs budget sharing, broad vs intereses vs lookalikes vs listas, exclusiones de clientes, separación por geo/idioma/producto/oferta/funnel. Presupuestos concretos: archivo 06. Audiencias: archivo 07. Retargeting y duplicación: archivo 09. Pujas: área 09. Testing creativo: área 03.

## TL;DR

- **Default 2026 (si no hay razón demostrada para otra cosa): 1 campaña por objetivo de negocio, Advantage+ on (campaign budget + Advantage+ audience + Advantage+ placements), 1 ad set (o pocos), creatividad diversa.** Es lo que Meta recomienda en múltiples páginas y lo que defienden practitioners de referencia con cuentas reales (Loomer, CTC, Foxwell). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Pero "automatizado" no implica "mejor" en incrementalidad.** Haus (640 tests geo-lift, 2024-2025, anunciantes medianos-grandes): Advantage+ ganó a manual solo en el 42 % de marcas, con iROAS DTC 12 % menor de media y más sobre-reporte (+12 pp); era mejor a mitad de test y peor al final. Su recomendación: no dividir 50/50 por defecto (los setups equilibrados tuvieron −18 % iROAS vs sesgados) y testar. **[EMPIRICAL]** ([Haus, 2025-07-28](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments); [AdExchanger, 2025-10-29](https://www.adexchanger.com/measurement/for-meta-marketers-automation-isnt-always-the-advantage-but-its-complicated/)). Nota: en 2025 "manual" ya no era el manual de 2020 (broad, CBO, Advantage+ placements casi siempre), y los datos son pre-Andromeda completo.
- **Cada ad set adicional multiplica el presupuesto necesario.** Si cada ad set necesita ~50 eventos/semana, presupuesto semanal ≈ 50 × CPA × nº ad sets (regla práctica). Por eso la arquitectura depende primero del **presupuesto relativo al CPA**. **[EMPIRICAL]** ([Loomer, 2026-02-02](https://www.jonloomer.com/meta-advertising-budget/))
- **Separar ad sets por intereses/lookalikes ya no tiene sentido en objetivos de conversión**: son sugerencias; los ad sets acaban compitiendo por la misma gente (auction overlap) y la diferencia de resultados es mayormente ruido. **[EMPIRICAL]** + **[OFFICIAL META]** (sugerencias)
- **Separar sí tiene sentido para resolver problemas concretos**: economía distinta por país/producto, objetivos de negocio distintos, restricciones legales, garantizar inversión mínima en un segmento, controlar el gasto en clientes existentes, tests con potencia, campañas de calendario. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Campaign budget (Advantage+ campaign budget) por defecto; ad set budget cuando necesitas control por ad set, bid strategies/goals mixtos o tamaños de audiencia muy distintos; "ad set budget sharing" (hasta 20 %) como término medio.** **[OFFICIAL META]** ([HC 458847204894307](https://www.facebook.com/business/help/458847204894307))
- **ABO "testing" + CBO "scaling" es [CONTESTED]**: unos lo defienden para forzar gasto en conceptos nuevos; otros lo consideran fragmentación. Foxwell (Q3 2026) lo deja en "depende de la cuenta"; Loomer prefiere el creative testing tool dentro del ad set principal.
- **Grandes cuentas (CTC)**: Sales ~95 % de las veces, value optimization con ROAS mínimo, estructura evergreen (adquisición + retención) + "marketing moments", presupuestos inflados con cost controls para mover liquidez. Es una arquitectura de cuentas grandes, no de 100 €/día. **[EMPIRICAL]** ([CTC, 2026-07-07](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026))

---

## 1. Por qué la consolidación se volvió el default (primeros principios)

1. **Learning por ad set**: cada ad set necesita su propio volumen; fragmentar = más tiempo/presupuesto en learning. **[OFFICIAL META]** ([HC 2419480091640105](https://www.facebook.com/business/help/2419480091640105))
2. **Auction overlap**: cuando varios ads del mismo anunciante entran en la misma subasta, Meta elige solo el de mayor valor total; los demás no participan → under-delivery y learning limited. **[OFFICIAL META]** ([HC 537699989762051](https://www.facebook.com/business/help/537699989762051))
3. **Targeting = sugerencia**: con Advantage+ audience, edad/género/intereses/lookalikes/custom audiences de inclusión son sugerencias; el sistema llega a "otros" cuando cree que rinde mejor. Separar por audiencias ya no aísla audiencias. **[OFFICIAL META]** ([HC 938372127764391](https://www.facebook.com/business/help/938372127764391))
4. **La creatividad hace el targeting** (Andromeda, área 01/03): el sistema de retrieval selecciona anuncios por relevancia para cada persona; la diversidad creativa dentro del ad set amplía los "públicos" alcanzables sin fragmentar presupuesto. Meta: "the focus has shifted from niche targeting to creative diversification" (citado por fuentes secundarias). **[STRONG INFERENCE]**
5. **Presupuesto en tiempo real**: campaign budget mueve dinero entre ad sets según oportunidad marginal; con ad set budgets fuerzas reparto. **[OFFICIAL META]**

Contrapeso: el sistema optimiza **el evento que le das dentro de la ventana de atribución**, no tu margen, tu LTV ni la incrementalidad. Cuando esas cosas difieren mucho entre segmentos, la consolidación ciega puede destruir valor (p. ej. gastar en clientes que comprarían igual). Por eso hay excepciones legítimas. **[STRONG INFERENCE]** (consistente con Haus)

## 2. Catálogo de patrones

### Patrón A — "Monocampaña" (default para presupuestos pequeños y medianos)

```
Campaña Sales (Advantage+ on, campaign budget, highest volume o value)
└── Ad set: país(es) objetivo, Advantage+ audience sin sugerencias (o con pocas), Advantage+ placements,
            Purchase / value, 7-day click (1-day view/engage por defecto)
    └── 4-15 anuncios con conceptos realmente distintos (formatos y ángulos diversos)
```
- **Cuándo**: presupuesto < ~10-20 × CPA diario; un mercado o mercados con economía similar; un producto/oferta principal; cuentas nuevas.
- **Cuándo no**: economía muy distinta por país/producto; necesidad de controlar inversión por segmento; base de clientes grande con recompra donde Meta sobre-invierte en existentes.
- **Fuentes**: Loomer (1 campaña/1 ad set como punto de partida, jun 2026), Meta (combinar, managing ad volume). **[EMPIRICAL]** + **[OFFICIAL META]**

### Patrón B — "Una campaña, varios ad sets con propósito" (campaign budget)

```
Campaña Sales (campaign budget)
├── Ad set 1: mercado A (o tema/persona A con su bloque creativo)
├── Ad set 2: mercado B
└── Ad set 3: clientes existentes (custom audience, "Use as a suggestion" desmarcado) con max spend limit
```
- **Cuándo**: hay 2-5 razones reales para separar y presupuesto para que cada ad set tenga volumen (o se acepta que el campaign budget concentre en uno).
- **Mecánica oficial**: el campaign budget "may not spend your budget equally"; evaluar a nivel campaña; spending limits min/max por ad set "sparingly"; no pausar ad sets con baja entrega; añadir ad sets en bloque (re-ajuste ~2 h). **[OFFICIAL META]** ([HC 2177212182495139](https://www.facebook.com/business/help/2177212182495139))
- **Uso especial**: replicar el antiguo *existing customer budget cap* con 2 ad sets (existentes con max spend + nuevos excluyendo existentes), método documentado por Meta tras retirar el cap. **[OFFICIAL META]** ([HC 1142614290190459](https://www.facebook.com/business/help/1142614290190459))

### Patrón C — "Evergreen adquisición + retención" (cuentas medianas-grandes con base de clientes)

```
Campaña ADQ (Sales, Customer lifecycle strategy = Acquire new customers → excluye compradores 730 d + listas)
Campaña RET (Sales, clientes existentes/engaged; restringido; objetivo y ROAS distintos)
```
- **Cuándo**: base de clientes grande (decenas de miles), recompra frecuente, y diferencia clara de economía (nCAC vs coste de reactivación). Cuando el reporting de audience segments muestra que Meta gasta demasiado en existentes con baja incrementalidad.
- **Cuándo no**: base pequeña (las audiencias de retención no sostienen una campaña); producto de compra única (basta excluir).
- **Evidencia**: CTC usa evergreen dividido en adquisición y retención, con exclusiones ACQ/retention configuradas a nivel de cuenta. Loomer prefiere no separar salvo problema demostrado y usar value rules para pagar menos por existentes. **[CONTESTED]** — ambos tienen razón en su contexto (CTC: marcas grandes con mucha recompra y presupuestos altos; Loomer: cuentas pequeñas-medianas).
- **Novedad oct 2026**: "Acquire new customers" incluye ahora una exclusión automática "Customers from your conversion data (730 days)" basada en eventos Purchase, no desactivable en ese modo; ventanas 730/180/90/60/30 días. **[EMPIRICAL]** ([Loomer, 2026-10-13](https://www.jonloomer.com/meta-automatic-customer-exclusions/)); el Help Center describe "specialized treatments to enhance exclusion coverage" y que el CPA puede subir. **[OFFICIAL META]** ([HC 1740191093676743](https://www.facebook.com/business/help/1740191093676743))

### Patrón D — "Evergreen + marketing moments"

- Campaña evergreen siempre activa + campañas de calendario (rebajas, lanzamiento, BFCM) con creatividad y oferta específicas, presupuesto propio y fecha de fin. **[EMPIRICAL]** (CTC)
- Alternativa más simple: añadir los anuncios de la promoción al ad set evergreen + budget scheduling para subir presupuesto en fechas (hasta 50 periodos, ≤8x presupuesto diario, ≥3 h). **[OFFICIAL META]** ([Meta Developers budget schedules](https://developers.facebook.com/documentation/ads-commerce/marketing-api/reference/ad-campaign/budget_schedules.md)) + **[STRONG INFERENCE]**
- Elegir según: si la promo cambia mucho el CPA/AOV (no quieres que contamine el aprendizaje del evergreen) → campaña aparte; si es una variación de oferta → mismo ad set.

### Patrón E — "Testing (ABO) + Scaling (CBO/Advantage+)" **[CONTESTED]**

- **A favor**: fuerza gasto en conceptos nuevos que el campaign budget ignoraría; datos limpios por concepto. Foxwell: ABO "gives an account clean, forced data on every test" pero financia perdedores; CBO "capable of starving a promising concept". **[EMPIRICAL]** ([Foxwell, 2026-07-03](https://www.foxwelldigital.com/blog/the-9-most-pressing-topics-for-meta-advertisers-in-q3-2026))
- **En contra**: fragmenta presupuesto y aprendizaje; tests infra-potenciados ("cinco anuncios repartiendo 50 $/día no generan datos de compra significativos"); el ganador del test a menudo no gana al moverse. Loomer prefiere el **creative testing tool** dentro del ad set activo (2-5 anuncios, gasto parejo, sin overlap). **[EMPIRICAL]** ([Loomer Master Brief](https://www.jonloomer.com/meta-ads-master-brief/))
- **Cuándo tiene sentido**: presupuesto ≥ ~5.000 €/día, producción creativa alta (decenas de conceptos/semana), y un criterio de graduación con potencia (p. ej. ≥1-2x CPA de gasto por concepto antes de juzgar). Por debajo, la versión ligera (testing tool / añadir en lotes al ad set principal) suele ser mejor. **[STRONG INFERENCE]**

### Patrón F — "Superficie de puja" (grandes cuentas)

- Duplicar la campaña evergreen con distintas bid strategies (highest volume, cost per result goal, bid cap, ROAS goal) compartiendo el mismo pool creativo; presupuestos "inflados" con cost controls para que el gasto fluya hacia los días/horas baratos. **[EMPIRICAL]** (CTC 2026; Foxwell describe el patrón de presupuesto muy por encima del gasto real + cap estricto)
- Riesgos: overlap entre campañas, gasto concentrado en mañanas (Foxwell reportó que Meta gastaba >80 % del presupuesto antes del mediodía ET en muchas cuentas, sobre todo con cost/bid cap — fecha no clara), necesidad de reglas automáticas de seguridad. Detalle de pujas: área 09.

### Patrón G — "Separación geográfica"

| Situación | Estructura recomendada |
|---|---|
| Varios países con precio, margen y CPA similares, mismo idioma | 1 ad set multi-país (Meta: combinar geos; "set multiple languages in a single ad set") |
| Países con economía muy distinta (p. ej. ES vs MX) | Campañas o ad sets separados (o value rules por ubicación si se quiere mantener consolidado) |
| Mercado nuevo que quieres "forzar" | Ad set con min spend limit dentro del campaign budget (ejemplo oficial California/NY) o campaña propia |
| Objetivos de ingresos por país impuestos por dirección | Campaña por país (coste: menos eficiencia) |
| Negocio local (radio) | 1 ad set por ubicación física solo si mensajes distintos; Loomer: incluir el área local en vez de excluir alrededores; la localización no distingue residentes de viajeros |

Fuentes: [HC 2720085414702598](https://www.facebook.com/business/help/2720085414702598), [HC 454681230514942](https://www.facebook.com/business/help/454681230514942), [Loomer targeting 2026](https://www.jonloomer.com/meta-ads-targeting-2026/). **[OFFICIAL META]** + **[EMPIRICAL]**

### Patrón H — "Funnel clásico TOFU/MOFU/BOFU con campañas separadas" **[OUTDATED]** como default

- Por qué ya no: Sales con Advantage+ audience prospecta y remarketea a la vez (Loomer ve ~20-30 % del presupuesto yendo a remarketing sin inputs; Haus ~15 % de gasto en retargeting tanto en Advantage+ como manual); las campañas de remarketing separadas suelen inflar resultados vía view-through y crean overlap. **[EMPIRICAL]**
- Cuándo sigue valiendo una variante: (1) modelo "tiered" (producto de entrada → upsell high-ticket a compradores, con Awareness/Reach + frecuencia controlada); (2) ciclos de venta largos B2B donde el contenido de nutrición es distinto; (3) catálogos con remarketing dinámico donde quieres garantizar presupuesto. Ver archivo 09.

### Patrón I — Lead gen

```
Campaña Leads (Advantage+ leads: campaign budget + Advantage+ audience + placements)
└── Ad set: Website & instant forms (default) o una sola location si la calidad difiere
    goal: leads → qualified leads (con CAPI CRM) ; value rules por edad/location si hay problema demostrado
```
- Separar por location (instant form vs web) solo si el breakdown muestra calidad muy distinta y quieres controlar inversión; si no, value rules por conversion location. **[EMPIRICAL]** (Loomer)
- Separar por servicio/producto cuando el valor del lead difiere mucho y no se expresa con value. Detalle: área 05.

### Patrón J — Catálogo y app
- **Catálogo**: Advantage+ catalog ads dentro de Sales (el catálogo se elige en el setup de campaña en el nuevo flujo); un mismo anuncio hace prospección y remarketing dinámico. **[OFFICIAL META]** ([HC 397103717129942](https://www.facebook.com/business/help/397103717129942))
- **App**: App promotion con Advantage+ on; separar campañas por OS/evento/mercado cuando cambian los eventos o la economía. Área 06.

## 3. Campaign budget vs ad set budget vs budget sharing

| Opción | Usa cuando… (Meta) | Riesgos |
|---|---|---|
| **Advantage+ campaign budget** | Flexibilidad entre ad sets; mides a nivel campaña; quieres simplificar; "value all ad sets the same"; mejor con ≥2 ad sets | Concentra gasto en el ad set de audiencia mayor o más barato; ad sets pequeños (retargeting) pueden no recibir nada; pausar ad sets rompe el reparto |
| **Ad set budget** | Controlar gasto por ad set; valor muy distinto entre ad sets no expresable con puja; tamaños de audiencia muy distintos; goals o bid strategies mixtos | Fuerza presupuesto a ad sets malos; más overlap; Advantage+ off si hay varios ad sets |
| **Ad set budget sharing** (2025) | Quieres control por ad set pero permitir que hasta un 20 % se mueva a otros ad sets en tiempo real | No compatible con campaign budget; poca evidencia pública de impacto |

Fuente: [HC 458847204894307](https://www.facebook.com/business/help/458847204894307), [HC 1388266028979935](https://www.facebook.com/business/help/1388266028979935). **[OFFICIAL META]**

Detalles oficiales a recordar:
- Con campaign budget, una campaña de **un solo ad set funciona igual que ad set budget**. **[OFFICIAL META]** ([HC 1602924913861363](https://www.facebook.com/business/help/1602924913861363))
- **Advantage+ on en Budget** se mantiene con campaign budget (uno o varios ad sets) y spending limits opcionales; se apaga con varios ad sets sin campaign budget. **[OFFICIAL META]**
- Min y max spend limits a la vez: "we don't recommend"; si se usan, diferencia ≥0,9 % y ≥1 $. Max spend limit se gestiona semanal (puede superarse un día). Min spend es objetivo, no garantía. **[OFFICIAL META]** ([HC 454681230514942](https://www.facebook.com/business/help/454681230514942))

## 4. Audiencias dentro de la arquitectura (resumen; detalle en archivo 07)

- **Broad + Advantage+ audience**: default para objetivos de conversión. Meta: −7,2 % coste por resultado en Sales/App, −9,7 % en Traffic/Engagement/Leads, −14,8 % en Awareness frente a… (comparativas internas de Meta). **[OFFICIAL META]** ([HC 273363992030035](https://www.facebook.com/business/help/273363992030035))
- **Intereses / detailed targeting**: casi siempre sugerencia; para 11 goals comunes no se puede restringir (Loomer, mar 2026). Exclusiones de detailed targeting eliminadas (31-mar-2025). **[EMPIRICAL]** + **[OFFICIAL META]**
- **Lookalikes**: sugerencia por defecto; desde oct 2025 no se pueden restringir en 9 goals de conversión/tráfico; desde la API v26 (sept 2026) los lookalikes son "countryless" y siguen la ubicación del ad set. **[EMPIRICAL]** + **[OFFICIAL META]** ([Marketing API v26 changelog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version26.0))
- **Customer lists / custom audiences**: inclusión = sugerencia (salvo "Further limit" + desmarcar); exclusión = control duro.
- **Implicación**: la única forma fiable de "segmentar" hoy es (a) controles (ubicación, edad mínima, idioma, exclusiones), (b) value rules, (c) creatividad/oferta, (d) evento de optimización.

## 5. Matriz de decisión

| Variable | Valor | Implicación de arquitectura |
|---|---|---|
| **Presupuesto semanal / CPA** | < 50 | 1 campaña, 1 ad set; aceptar learning limited o evento más frecuente (archivo 02) |
| | 50-150 | 1 campaña, 1-2 ad sets |
| | 150-500 | 1-3 campañas (objetivos/mercados), 2-5 ad sets con propósito |
| | > 500 | Arquitecturas C/D/E/F posibles; testing estructurado; incrementalidad |
| **Volumen de eventos del evento-dinero** | < 10/semana | Revisar evento/oferta antes que estructura |
| **Modelo de negocio** | E-commerce recompra alta | Considerar C (adq/ret) cuando base grande; value rules/CLS |
| | Compra única / high-ticket | Excluir compradores; leads cualificados; ciclos largos → patrón H variante |
| | Lead gen local | 1 campaña Leads; geos juntas salvo mensajes distintos |
| | App | Advantage+ app; campañas por OS/evento |
| **País/mercado** | Economía homogénea | Juntar |
| | Heterogénea | Separar o value rules por ubicación |
| **Evento** | Purchase con ≥50/semana | Value optimization posible |
| | Lead sin CRM | Montar CAPI CRM; structure simple |
| **Volumen creativo** | < 5 conceptos/mes | 1 ad set; no testing separado |
| | 5-20 | Testing tool / lotes en el ad set principal |
| | > 20-50/semana | Considerar campaña de testing (E) y límite de anuncios por Página |

Todos los umbrales son **[STRONG INFERENCE]** derivados de la regla de ~50 eventos/semana/ad set; no son oficiales.

## Implicaciones operativas

- **Empieza simple y añade complejidad solo con una hipótesis escrita** ("separo X porque Y; lo daré por bueno si Z en N semanas"). Loomer: "Create separate ad sets to solve a specific problem."
- **Revisa trimestralmente el balance Advantage+/manual y adquisición/retención con incrementalidad** (lift, geo-holdout), no con ROAS de plataforma.
- **No dividas 50/50 Advantage+ vs manual "para diversificar"**: Haus vio −18 % iROAS en setups equilibrados frente a sesgados.
- **Usa audience segments como instrumento de control** de cuánto va a remarketing/existentes antes de decidir separar.

## Errores frecuentes

1. Estructuras heredadas de 2019-2021: TOFU/MOFU/BOFU + 10 ad sets por intereses + LAL 1 %/3 %/5 % separados.
2. Duplicar campañas ganadoras para escalar (overlap + learning nuevo).
3. Campaign budget con ad sets de tamaños muy distintos (retargeting pequeño + broad) esperando que el pequeño gaste.
4. Ad set budgets con 6 ad sets de 15 €/día.
5. Una campaña por producto con catálogos pequeños, en vez de catálogo + product sets en un ad set.
6. Separar países por costumbre cuando la economía es la misma.
7. Leer el CPA por ad set dentro de un campaign budget y "castigar" al que gasta más (breakdown effect; Meta pide mirar a nivel campaña).

## Preguntas abiertas

- ¿Los datos de Haus (manual > Advantage+ en iROAS en el 58 % de marcas) se mantienen tras Andromeda/GEM y la unificación de 2025? El propio CEO de Haus lo dejó abierto. Necesita réplica 2026.
- ¿Qué parte del "manual" de Haus era realmente manual (intereses) frente a broad con CBO? No desagregado.
- Impacto real de "ad set budget sharing" y del supuesto "rolling budget" (Foxwell, 2026; no verificado en documentación oficial).

## Fuentes clave

- [About campaign budgets and ad set budgets](https://www.facebook.com/business/help/458847204894307) — Meta HC — meta-oficial
- [Best practices for Advantage+ campaign budget](https://www.facebook.com/business/help/2177212182495139) — Meta HC — meta-oficial
- [About ad set spend limits with campaign budget](https://www.facebook.com/business/help/454681230514942) — Meta HC — meta-oficial
- [How to replicate existing customer budget cap](https://www.facebook.com/business/help/1142614290190459) — Meta HC — meta-oficial
- [Create a campaign to acquire new customers](https://www.facebook.com/business/help/1740191093676743) — Meta HC — meta-oficial
- [Understand auction overlap](https://www.facebook.com/business/help/537699989762051) — Meta HC — meta-oficial
- [The Meta Report (640 experiments)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
- [For Meta Marketers, Automation Isn’t Always The Advantage](https://www.adexchanger.com/measurement/for-meta-marketers-automation-isnt-always-the-advantage-but-its-complicated/) — AdExchanger, 2025-10-29 — prensa
- [How Meta Actually Works in 2026](https://commonthreadco.com/blogs/ecommerce-playbook/how-meta-actually-works-in-2026) — CTC, 2026-07-07 — agencia
- [The 9 Most Pressing Meta Ad Topics for Q3 2026](https://www.foxwelldigital.com/blog/the-9-most-pressing-topics-for-meta-advertisers-in-q3-2026) — Foxwell, 2026-07-03 — agencia
- [How Many Active Ad Sets Should You Have](https://www.jonloomer.com/active-ad-sets-meta-ads-campaign/) — Jon Loomer, 2026-06-23 — practitioner
- [How Many Meta Ads Campaigns Should You Have at Once?](https://www.jonloomer.com/how-many-meta-ads-campaigns/) — Jon Loomer, 2026-06-16 — practitioner
- [Meta Adds Automatic Customer Exclusions](https://www.jonloomer.com/meta-automatic-customer-exclusions/) — Jon Loomer, 2026-10-13 — practitioner
