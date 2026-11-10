# Objetivos de campaña en 2026: taxonomía, performance goals, conversion locations y cuándo usar cada uno

> Última verificación: 2026-10-15 · Autor: A02 (agente) · Ámbito: objetivos de campaña de Meta Ads Manager (Facebook, Instagram, Messenger, WhatsApp, Threads, Audience Network), su relación con conversion location, performance goal y evento. No cubre pujas en detalle (ver área 09) ni medición (área 04).

## TL;DR

- **Hay 6 objetivos** (Awareness, Traffic, Engagement, Leads, App promotion, Sales) desde la simplificación "ODAX" de 2022; siguen vigentes en 2026. **[OFFICIAL META]** ([HC 1438417719786914](https://www.facebook.com/business/help/1438417719786914))
- **El objetivo es un "filtro de menú", no lo que optimiza el sistema.** Lo que se puja en la subasta es el **performance goal** (+ evento de conversión) del ad set. Meta lo dice literalmente: "your performance goal is the desired outcome that our system bids on in the ad auction" y "the performance goal of your ad set can be different from your ad objective". **[OFFICIAL META]** ([HC 355670007911605](https://www.facebook.com/business/help/355670007911605))
- **Cada campaña se decide con tres capas**: objetivo → conversion location (dónde ocurre la acción) → performance goal / evento. Si el negocio gana dinero con ventas web, la configuración por defecto es Sales → Website → Maximize number of conversions (Purchase) o Maximize value of conversions. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Sales, Leads y App promotion arrancan en el "Advantage+ campaign setup"** (Advantage+ on en presupuesto, audiencia y placements) desde la unificación de 2025; los controles manuales siguen existiendo pero "apagan" la etiqueta Advantage+. En 2026 Meta está extendiendo un "recommended setup" equivalente a Traffic, Awareness y Engagement. **[OFFICIAL META]** ([HC 1292656978738967](https://www.facebook.com/business/help/1292656978738967), [HC 1212225059146059](https://www.facebook.com/business/help/1212225059146059))
- **El algoritmo es literal**: optimiza la acción elegida aunque no tenga valor de negocio (clicks accidentales, leads baratos de baja calidad, ATC de curiosos). Elegir mal el objetivo/goal es el error estructural más caro. **[EMPIRICAL]** (Loomer, 2025-2026; ver archivo 02)
- **Upper/mid funnel no es "tirar dinero" por definición, pero casi nunca debe quitar presupuesto al objetivo primario.** Haus (640 tests, 2025): campañas upper-funnel con DTC iROAS 46 % inferior durante el test (22 % tras ventana post-test) pero con efecto omnicanal muy superior; mid-funnel 14 % peor en iROAS DTC. **[EMPIRICAL]** ([Haus](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))
- **Leads en 2026**: el goal "Maximize number of qualified leads" (antes "conversion leads") **ya no está disponible para nuevas campañas sin integración de Conversions API desde abril 2026**; campañas existentes afectadas desde agosto 2026. **[OFFICIAL META]** ([HC 782657799338685](https://www.facebook.com/business/help/782657799338685))
- **Novedades 2026 en test**: "Sequenced events" para leads web (optimizar a personas que hacen A y luego B, p. ej. formulario → cita), visto en test por Jon Loomer en octubre 2026; no documentado aún en Help Center. **[EMPIRICAL]** (no verificado oficialmente)
- **Objetivo Engagement con conversion location Website** permite optimizar eventos de "consideración" (Contact, Schedule, SubmitApplication, StartTrial, Subscribe, ViewContent…) sin pasar por Sales/Leads: útil como herramienta, peligrosa como sustituto del objetivo real. **[OFFICIAL META]** ([HC 2035196646663270](https://www.facebook.com/business/help/2035196646663270))

---

## 1. Modelo mental: objetivo ≠ optimización

Meta separa tres decisiones (y una cuarta implícita):

| Capa | Dónde se elige | Qué controla | Ejemplo |
|---|---|---|---|
| **Objetivo** | Campaña | Qué menú de conversion locations y performance goals ves; qué setup Advantage+ aplica; algunas compatibilidades (catálogo, Advantage+ leads/sales/app) | Sales |
| **Conversion location** | Ad set | Dónde quieres que ocurra la acción: Website, App, Website & app, Website & in-store, Website & calls, Messenger, WhatsApp, Instagram Direct, Instant forms, Calls… | Website |
| **Performance goal** | Ad set | Lo que el sistema puja y optimiza en la subasta | Maximize number of conversions |
| **Evento de conversión** | Ad set | La señal concreta (dataset/pixel/SDK/CAPI) que define "éxito" | Purchase |

Meta lo documenta así: el performance goal es "the desired outcome that our system bids on in the ad auction", y "you can select Sales as your ad objective, but optimize for link clicks within an ad set". **[OFFICIAL META]** ([HC 355670007911605](https://www.facebook.com/business/help/355670007911605)). También documenta cómo los "ad goals" simplificados de Facebook Ad Center / Instagram Boost se traducen en combinaciones objetivo + location + goal (p. ej. "Get more website visitors (with the Meta Pixel)" = Traffic/Engagement/Leads/Sales → Website → Landing page views). **[OFFICIAL META]** ([HC 2513967775738161](https://www.facebook.com/business/help/2513967775738161))

**Implicación de primeros principios:** el sistema de entrega (retrieval + ranking, ver área 01) estima para cada impresión la probabilidad de que *esa persona* realice *ese evento* dentro de la ventana de atribución, y la multiplica por la puja. Si el evento elegido está poco correlacionado con el dinero, el sistema se vuelve muy bueno encontrando gente que hace el evento… y no compra. Por eso la elección de objetivo/goal/evento es **la decisión de estructura con más impacto**, por encima del número de ad sets o del tipo de presupuesto. **[STRONG INFERENCE]**

> Matiz práctico: el objetivo sí importa por lo que habilita. Sales habilita Advantage+ sales, catálogo en todas las campañas de ventas, Customer lifecycle strategy, audience segments reporting y value optimization web; Leads habilita instant forms, qualified leads, Advantage+ leads; App promotion habilita SKAN/app events. **[OFFICIAL META]**

## 2. La taxonomía actual (verificada 2026-10-15)

Tabla oficial de equivalencias con los objetivos antiguos (pre-2022): **[OFFICIAL META]** ([HC 1438417719786914](https://www.facebook.com/business/help/1438417719786914))

| Objetivo actual | Objetivos antiguos que absorbe |
|---|---|
| Awareness | Brand awareness, Reach, Video views, Store traffic |
| Traffic | Traffic (y Messages vía location Messenger/WhatsApp) |
| Engagement | Engagement, Video views, Messages, Conversions (location Website/App) |
| Leads | Lead generation, Messages, Conversions |
| App promotion | App installs |
| Sales | Conversions, Catalog sales (y Messages vía Messenger/WhatsApp) |

### 2.1 Conversion locations y eventos disponibles por objetivo

Fuente: [HC 2035196646663270](https://www.facebook.com/business/help/2035196646663270) (consultado 2026-10-15). **[OFFICIAL META]**

| Objetivo | Conversion locations | Eventos optimizables |
|---|---|---|
| **Awareness** | On your ad | No requiere evento |
| **Traffic** | Website, App, Messenger, WhatsApp, Calls, Instagram profile | No requiere evento |
| **Engagement** | On your ad (video views, post engagement, event responses); Messaging apps (Messenger, WhatsApp, IG Direct); Website; App; Facebook Page | Website: Add to wishlist, Contact, Customize product, Donate, Find location, Schedule, Search, Start trial, Submit application, Subscribe, View content. App: lista amplia incl. Achieve level, Complete tutorial, In-app ad click/impression, Rate, Spent credits… |
| **Leads** | Website; Website & calls; Website & instant forms; Instant forms; Messenger; Instagram; Calls; Instant forms & Messenger; WhatsApp; App | Website: Complete registration, Contact, Find location, Lead, Schedule, Search, Start trial, Submit application, Subscribe, View content. Website & instant forms: Lead |
| **App promotion** | App (automático) | Todos los app events estándar y custom |
| **Sales** | Website; App; Website & app; Website & in-store; Website & calls; Messenger; WhatsApp | Website: Add payment info, Add to cart, Add to wishlist, Complete registration, Donate, Initiate checkout, Purchase, Search, Start trial, Subscribe, View content (Shops ads: solo ATC, wishlist, IC, Purchase, ViewContent). Website & app: solo eventos trackeados por AEM y SDK |

Observaciones útiles:
- **Lead no aparece en la lista de Sales**, pero Complete registration sí. Jon Loomer usa CompleteRegistration en vez de Lead precisamente para poder usarlo en campañas Sales (y aprovechar audience segments). **[EMPIRICAL]** ([Loomer, jul 2026](https://www.jonloomer.com/meta-ads-lead-generation/))
- **Purchase no aparece en Engagement ni en Leads**: si optimizas a compra, es Sales (o App promotion). **[OFFICIAL META]**

### 2.2 Performance goals por objetivo

Lista oficial (resumen; [HC 355670007911605](https://www.facebook.com/business/help/355670007911605)). **[OFFICIAL META]**

- **Awareness**: Maximize reach, impressions, ad recall lift, ThruPlay views, 2-second continuous video views.
- **Traffic**: Landing page views, link clicks, daily unique reach, conversations, impressions, Instagram profile visits, calls.
- **Engagement**: conversations, link clicks, impressions, ThruPlay, 2-sec views, post engagement, daily unique reach, event responses, conversions (web), landing page views, app events, reminders set, calls, page likes.
- **Leads**: conversions (web), landing page views, link clicks, daily unique reach, impressions, **leads**, **qualified leads**, **leads through messaging** (en despliegue gradual), calls, app events; y **Maximize value of conversions** para lead ads ([HC 782657799338685](https://www.facebook.com/business/help/782657799338685)).
- **App promotion**: app events, app installs, value of conversions (incl. in-app ad impressions solo Android), link clicks.
- **Sales**: conversions, **value of conversions**, landing page views, link clicks, **purchases through messaging**, daily unique reach, impressions, conversations, calls, app events.

Cambios recientes a tener en cuenta:
- **Page likes**: en junio 2026 Loomer vio en una cuenta el aviso "Page likes performance goal is no longer available". No confirmado como global. **[EMPIRICAL]** (una cuenta; [Loomer, 2026-06-04](https://www.jonloomer.com/customer-lifecycle-strategy-not-what-advertisers-thought/))
- **Landing page views**: desde julio 2025 Meta permite LPV a anunciantes con problemas de pixel ("pixel sharing challenges"), y puede modelar LPV cuando faltan datos. **[OFFICIAL META]** ([HC 417293491972212](https://www.facebook.com/business/help/417293491972212))
- **Qualified leads requiere CAPI** (abril 2026 para nuevas campañas; agosto 2026 para existentes). **[OFFICIAL META]**

## 3. Objetivo por objetivo

### 3.1 Sales

- **Qué optimiza realmente**: el evento elegido (Purchase, ATC, IC, etc.) o el valor de conversión (value optimization), en la ventana de atribución elegida. Con Advantage+ on, audiencia, placements y presupuesto se reparten automáticamente.
- **Señales**: dataset (pixel + CAPI), catálogo, señales on-platform (interacciones con anuncios, perfil), historial de conversiones de la cuenta; con value optimization, el valor enviado (purchase value, pLTV, profit). **[OFFICIAL META]** ([HC 296463804090290](https://www.facebook.com/business/help/296463804090290))
- **Cuándo usarlo**: e-commerce, suscripciones con pago web, servicios con checkout online, cualquier negocio con un evento de compra fiable. También lead gen B2C de bajo ticket cuando el "lead" es en realidad una compra (trial de pago) o cuando se quiere CompleteRegistration con audience segments.
- **Cuándo NO**: si el evento de dinero no se puede medir (sin pixel/CAPI fiables) o el volumen es tan bajo (p. ej. <5-10 compras/semana con todo el presupuesto) que el sistema no tiene señal; ahí valora un evento proxy *con alta correlación* (ver archivo 02) o un objetivo Leads con calificación.
- **Evento**: Purchase por defecto. Value optimization si hay dispersión real de valor de pedido (AOV) y ≥50 conversiones/semana (Meta: 50+ conversiones/semana, 100+ para pLTV/profit; test mínimo 3 semanas). **[OFFICIAL META]** ([HC 296463804090290](https://www.facebook.com/business/help/296463804090290))
- **Errores típicos**: Sales + goal "Landing page views" pensando que "es Sales"; optimizar a ATC por defecto; no definir audience segments (pierdes el reporting nuevo/engaged/existente); ignorar que Advantage+ sales mezcla prospección y remarketing (ROAS inflado, ver archivos 08-09).
- **Shops ads**: Meta exige mínimo 17 compras web + 5 vía Meta para salir de learning. **[OFFICIAL META]** ([HC 112167992830700](https://www.facebook.com/business/help/112167992830700))

### 3.2 Leads

- **Qué optimiza**: Leads (envío de instant form o evento web), qualified leads (personas con más probabilidad de convertir *después* del lead, según eventos CRM vía CAPI), leads through messaging, value of conversions (valor que envías por lead).
- **Conversion locations**: Instant forms; Website; **Website & instant forms (default en Advantage+ leads)**; Messenger/Instagram/WhatsApp; Calls; App; combinaciones. El default "Website and Instant Forms" deja a Meta repartir entre ambos; Loomer recomienda value rules por conversion location si un canal da peor calidad. **[OFFICIAL META]** + **[EMPIRICAL]** ([Loomer, jul 2026](https://www.jonloomer.com/meta-ads-lead-generation/))
- **Cuándo usarlo**: servicios, B2B, high-ticket, inmobiliaria, educación, salud (con restricciones), cualquier venta que ocurre offline/CRM.
- **Cuándo NO**: si en realidad hay compra online medible (usa Sales); si no tienes capacidad de seguimiento comercial rápido (los leads se enfrían y el problema no es Meta).
- **Evento**: el más profundo con volumen. Orden preferente: qualified lead / evento CRM (requiere CAPI; Meta exige ≥200 leads/mes, subida diaria, etapa objetivo dentro de 28 días y tasa de conversión 1-40 % para conversion leads) → lead con formulario "higher intent" / preguntas → lead simple. **[OFFICIAL META]** ([Meta Developers](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration))
- **Errores típicos**: optimizar a "lead" barato y celebrar el CPL (los leads más baratos suelen concentrarse en demografías que rellenan mucho y compran poco; Loomer documenta exceso de 65+ en lead forms y lo corrige con value rules −90 % en 65+, −20 % en 55-64). **[EMPIRICAL]** ([Loomer Master Brief, jul 2026](https://www.jonloomer.com/meta-ads-master-brief/))
- **Dato oficial (claim de Meta)**: qualified leads + CAPI para CRM con instant forms → 21 % menor coste por lead de calidad vs "Maximize number of leads"; en website forms −9,5 %. Advantage+ leads → −14 % CPL y −10 % coste por lead cualificado vs Advantage+ off. Son cifras de Meta, no auditadas. **[OFFICIAL META]**
- **Novedad (test, 2026)**: *Sequenced events* en Leads → Website con "Maximize number of qualified leads": eliges dos eventos en orden (p. ej. Lead → Schedule) y Meta optimiza a quien hace ambos. Solo atribución Standard según Loomer. **[EMPIRICAL]** ([Loomer, 2026-10-06](https://www.jonloomer.com/meta-sequenced-events/), no verificado en Help Center). Contradicción a vigilar: la doc de developers dice que conversion leads "solo es compatible con instant forms", mientras el Help Center 2026 dice que qualified leads funciona "with both website forms and instant forms". **[CONTESTED]** (documentación desalineada; la de Help Center es más reciente)

Detalle completo de lead gen y CRM: área 05.

### 3.3 App promotion

- **Qué optimiza**: installs, app events (incl. compras in-app), value (in-app purchase value; in-app ad impressions solo Android).
- **Estado 2025-2026**: Advantage+ app campaigns (antes AAC/"Advantage+ app campaigns" legacy) se integran en el flujo unificado: objetivo App promotion arranca con Advantage+ on; la API legacy de AAC quedó bloqueada (ver archivo 08). **[OFFICIAL META]** ([Meta Developers](https://developers.facebook.com/docs/marketing-api/advantage-campaigns))
- **Cuándo NO**: si tu negocio monetiza en web (web-to-app o web checkout): Sales con location Website/Website & app suele ser más directo.
- **Errores**: optimizar a installs cuando el negocio depende de suscripción/compra (instalaciones baratas sin valor); confiar en SKAN como verdad sin MMP/incrementalidad. Detalle: área 06.

### 3.4 Traffic

- **Qué optimiza**: LPV (carga de la página), link clicks, conversaciones, calls, visitas al perfil de Instagram, reach/impresiones.
- **Cuándo usarlo**: construir audiencias de remarketing en cuentas sin señal; contenido editorial/afiliación donde la visita *es* el negocio; tests de mensaje muy baratos (con cautela).
- **Cuándo NO**: como sustituto barato de Sales/Leads. Meta encuentra a quien hace clic (incl. clics accidentales en Audience Network); Loomer recomienda quitar Audience Network si optimizas a link clicks/LPV en Sales/Leads. **[EMPIRICAL]** ([Loomer, jun 2025](https://www.jonloomer.com/advantage-plus-campaign/))
- **Evento**: LPV > link click (LPV exige que la página cargue). **[OFFICIAL META]** ([HC 197634954160445](https://www.facebook.com/business/help/197634954160445))
- **Dato Haus**: el "incrementality factor" (incremental vs atribuido 7dc/1dv) de Traffic es ~2,4x el de campañas lower-funnel: Meta *infra-atribuye* el valor de tráfico, pero en DTC el iROAS directo sigue siendo inferior. **[EMPIRICAL]** ([Haus, 2025-07-28](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments))

### 3.5 Engagement

- **Qué optimiza**: interacción en el anuncio (post engagement, video views), mensajes (Messenger/WhatsApp/IG Direct), eventos web/app "de consideración", llamadas, page likes (posiblemente retirado en algunas cuentas).
- **Cuándo usarlo**: negocios cuya conversión ocurre en conversación (click-to-WhatsApp en LatAm/España/India para servicios y retail local), generación de audiencias de vídeo para negocios con ciclo largo, eventos.
- **Cuándo NO**: para "calentar" una cuenta antes de vender (no hay evidencia de que el engagement transfiera señal útil de compra; el algoritmo aprende quién da likes). **[STRONG INFERENCE]**
- **Ojo**: en 2026 Meta cambió "Post engagement" por "Interactions" en reporting (Loomer, ene 2026) y la atribución "engage-through" pasó a ventana de 1 día (marzo 2026). **[EMPIRICAL]** ([Loomer, 2026-03-05](https://www.jonloomer.com/attribution-changes-remarketing-impact/))

### 3.6 Awareness

- **Qué optimiza**: alcance, impresiones, ad recall lift estimado, vistas de vídeo.
- **Cuándo usarlo**: lanzamientos, marcas con distribución omnicanal (retail físico, Amazon), mercados nuevos, campañas de frecuencia controlada a audiencias pequeñas (remarketing "tiered" de Loomer: Awareness + Maximize reach + solo custom audiences + frequency cap). **[EMPIRICAL]**
- **Cuándo NO**: DTC pequeño con presupuesto limitado y objetivo de ventas a corto plazo.
- **Datos Haus 2025**: upper-funnel = ~6 % del gasto de plataforma de sus clientes; iROAS DTC −46 % vs bottom-funnel durante el test, −22 % tras la ventana post-test; efecto omnicanal +138 % vs +46 % de campañas de conversión; nuevos clientes 81 % vs 67 %. Interpretación: Awareness puede ser rentable para marcas omnicanal y en reach/awareness Meta infra-atribuye hasta 6x; para un DTC puro y pequeño, raramente es la primera prioridad. **[EMPIRICAL]**

## 4. Tabla de decisión: modelo de negocio → configuración por defecto

| Negocio | Objetivo | Location | Goal / evento por defecto | Cuándo cambiaría |
|---|---|---|---|---|
| E-commerce con ≥50 compras/semana | Sales | Website (o Website & app) | Maximize value of conversions (Purchase) o number of conversions | Si AOV homogéneo → conversiones; si hay margen muy distinto por producto → valor/profit |
| E-commerce pequeño (<20 compras/semana) | Sales | Website | Purchase igualmente (aceptar menos estabilidad) | Solo bajar a ATC/IC si Purchase no entrega nada; preferir antes producto de entrada más barato (ver archivo 02) |
| SaaS / suscripción con trial | Sales o Leads | Website / App | StartTrial o Subscribe; value con pLTV si hay modelo | Si trial→pago <10 % y muy variable, optimizar a evento más profundo (activación) vía CAPI |
| Servicios locales / high-ticket | Leads | Instant forms o Website & instant forms | Leads → qualified leads (con CAPI CRM) | Si el negocio cierra por teléfono → Calls; si cierra por chat → Messaging |
| Negocio conversacional (WhatsApp) | Sales o Leads (o Engagement) | WhatsApp / Messenger | Conversations → purchases/leads through messaging | Si hay evento de compra vía CAPI de mensajería, Sales con evento |
| App con monetización in-app | App promotion | App | App events (purchase) o value | Installs solo en fase de volumen inicial o apps ad-monetizadas |
| Marca omnicanal / retail | Sales + Awareness | Website & in-store / On your ad | Purchase + reach con frecuencia | Medir con lift/geo-tests, no con atribución de plataforma |
| Medios / afiliación | Traffic | Website | LPV (o conversiones web si hay evento de valor) | Si hay evento de monetización medible, Sales/Engagement con ese evento |

Todo lo anterior es **[STRONG INFERENCE]** a partir de la documentación oficial + práctica documentada; los umbrales numéricos se discuten en archivos 02, 03 y 06.

## 5. Advantage+ "por defecto" según objetivo (estado 2026)

- Sales, App promotion y Leads: al crear campaña aparece "Advantage+ on" arriba a la derecha; budget/audience/placements con Advantage+ on. Si estrechas demasiado (ABO con varios ad sets, desmarcar "Use as a suggestion", excluir placements) se marca "Advantage+ off" en esa sección. **[OFFICIAL META]** ([HC 906206294602874](https://www.facebook.com/business/help/906206294602874), [HC 830005979993164](https://www.facebook.com/business/help/830005979993164))
- Traffic, Awareness y Engagement: Meta está desplegando un "recommended setup" similar (campaign score 100, Advantage+ on en algunas opciones). **[OFFICIAL META]** ([HC 1212225059146059](https://www.facebook.com/business/help/1212225059146059))
- Special ad categories (vivienda, empleo, finanzas, política) y farmacéuticas pueden no tener todas las funciones Advantage+. **[OFFICIAL META]**

## Implicaciones operativas

- **Decide primero el evento de dinero y su volumen semanal esperado**, después el objetivo. Si el evento con dinero tiene volumen suficiente (orientativo: ≥30-50/semana por ad set, ver archivo 03), objetivo = el que lo contiene (Sales/Leads/App).
- **No uses objetivos "baratos" (Traffic/Engagement) para "ayudar" a Sales** salvo que tengas presupuesto excedente sobre la escala rentable del objetivo primario y un método para probar que aporta (lift test, geo-holdout). **[EMPIRICAL]** ([Loomer, 2026-06-16](https://www.jonloomer.com/how-many-meta-ads-campaigns/); Haus)
- **Revisa siempre el performance goal del ad set** al heredar cuentas: es muy común encontrar campañas Sales optimizando a LPV o link clicks.
- **Leads**: si no tienes CAPI para CRM antes de 2027, estás limitado a "Maximize number of leads" → prioriza montar CAPI CRM (área 04/05).
- **Umbral de decisión**: si en 4 semanas un ad set no genera ni ~10 eventos/semana del evento objetivo con todo el presupuesto disponible, el problema no es la estructura: es el evento, la oferta, el embudo o el presupuesto.

## Errores frecuentes

1. Elegir objetivo por "etapa del funnel" en vez de por evento de negocio (p. ej. Awareness para "prospección" y Sales para "retargeting"). En 2026 Sales ya prospecta y remarketea dentro de la misma campaña.
2. Sales con goal LPV/link clicks "porque las compras son caras": entrenas al sistema a buscar clicadores.
3. Leads con instant form sin preguntas de calificación ni CAPI CRM, optimizando CPL.
4. Engagement para mensajes sin conectar el resultado de la conversación (venta) al dataset.
5. No conocer qué eventos acepta cada objetivo (p. ej. intentar Lead en Sales; usar CompleteRegistration es la vía).
6. Dejar "Website & instant forms" por defecto sin mirar el breakdown por conversion location.
7. Asumir que el objetivo de la campaña es lo que optimiza; heredar campañas y no auditar goal/evento/ventana.

## Preguntas abiertas

- ¿Retirará Meta definitivamente el goal "Page likes" y otros goals de engagement de bajo valor? (señales en junio 2026, no confirmado).
- ¿Cuándo saldrá "Sequenced events" de test y si exigirá CAPI CRM?
- ¿Se unificarán Traffic/Engagement/Awareness con el mismo modelo de "Advantage+ state" (API `advantage_state`) que hoy solo devuelve SALES/APP/LEADS?
- Desalineación entre la doc de Developers (conversion leads solo instant forms) y Help Center (qualified leads también en web).

## Fuentes clave

- [How to choose the right ad objective](https://www.facebook.com/business/help/1438417719786914) — Meta HC, consultado 2026-10-15 — meta-oficial
- [About performance goals](https://www.facebook.com/business/help/355670007911605) — Meta HC — meta-oficial
- [Available conversion locations and events by objective](https://www.facebook.com/business/help/2035196646663270) — Meta HC — meta-oficial
- [About ad goals and Ads Manager settings](https://www.facebook.com/business/help/2513967775738161) — Meta HC — meta-oficial
- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) — Meta HC (2026) — meta-oficial
- [About maximizing the value of conversions](https://www.facebook.com/business/help/296463804090290) — Meta HC — meta-oficial
- [About the Advantage+ campaign experience](https://www.facebook.com/business/help/1292656978738967) — Meta HC — meta-oficial
- [Conversions API for CRM integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — Meta Developers — meta-developers
- [The Meta Report: 640 incrementality experiments](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — Haus, 2025-07-28 — vendor
- [The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/) — Jon Loomer, 2026-07-02 — practitioner
- [Meta Sequenced Events](https://www.jonloomer.com/meta-sequenced-events/) — Jon Loomer, 2026-10-06 — practitioner (leído vía resúmenes de búsqueda; acceso directo bloqueado)
