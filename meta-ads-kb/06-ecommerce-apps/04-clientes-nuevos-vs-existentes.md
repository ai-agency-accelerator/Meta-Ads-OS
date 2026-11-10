# Clientes nuevos vs existentes: adquisición, definiciones, exclusiones y nCAC

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: cómo define Meta clientes existentes/engaged/nuevos, herramientas de control (Customer lifecycle strategy, exclusiones, estructura con cap), cómo medir el % de nuevos y el nCAC, y cómo fijar objetivos de adquisición. Economía detallada: `05-…`.

## TL;DR

- **Meta optimiza al coste por conversión más barato, y las conversiones más baratas suelen ser de gente que ya iba a comprar** (clientes, visitantes recientes, suscriptores de email). Sin controles, un "buen ROAS" puede ser revenue de recurrentes que habrías tenido igual. [STRONG INFERENCE] + [EMPIRICAL] (Javvy/Haus, practitioners)
- **Tres definiciones distintas de "nuevo" conviven y no coinciden:** (1) segmento "Nuevo" de Meta = todo lo que no está en tus definiciones de *Clientes existentes* y *Audiencia con interacción*; (2) cliente nuevo en tienda = primer pedido de ese email/cliente; (3) cliente nuevo incremental = el que no habría comprado sin el anuncio (solo lo da un lift test). Gestiona con (2) y valida con (3). [OFFICIAL META] (1) + [STRONG INFERENCE]
- **Herramientas de control en 2026**: Customer lifecycle strategy = "Adquirir clientes nuevos" (GA anunciada 6/7-oct-2026), exclusión de custom audiences (control duro también en Advantage+), estructura oficial de 2 ad sets con min/max de gasto para replicar el antiguo cap, y reporting por segmentos. El "Existing customer budget cap" ya no existe. [OFFICIAL META]
- **Detalle clave de Customer lifecycle strategy** (Jon Loomer, 13-oct-2026): al activar "Adquirir clientes nuevos" se aplica una exclusión **automática y no desactivable** de quienes dispararon Purchase en los datos de conversión de la cuenta, con ventana **730 días por defecto** (opciones 730/180/90/60/30), más las custom audiences que añadas. Esto supera el límite de 180 días de las audiencias web, pero depende de que tu Purchase (Pixel+CAPI) sea fiable. CTC habla de 180 días → [CONTESTED], verificar en la cuenta. [EMPIRICAL]
- **El nCAC es la métrica de control de la adquisición; el ROAS no.** Fórmula operativa: nCAC = gasto de adquisición / clientes nuevos (tienda) del periodo. Objetivo derivado de la economía (CM2 del primer pedido + valor de recompra a 90–180 días), no de benchmarks. [STRONG INFERENCE]
- **La calidad de la lista de existentes determina todo.** Las audiencias web de Meta guardan como máximo 180 días; para "clientes existentes" combina Purchase 180 días + lista CRM de compradores de 2–3 años sincronizada. Con listas incompletas, el segmento "Nuevo" de Meta se infla. [OFFICIAL META] (180 días) + [EMPIRICAL]
- **Excluir existentes tiene coste**: Meta avisa de que puede aumentar el coste por resultado, y quitas retargeting barato que a veces sí es incremental (reactivación de inactivos, lanzamientos). La exclusión total es correcta para campañas de adquisición; no para toda la cuenta. [OFFICIAL META] (aviso) + [CONTESTED] (alcance)
- **Referencia de mix (Haus, 640 tests):** la parte del impacto incremental de Meta que va a clientes nuevos fue 65–70 % en campañas de conversión, 78 % en mid-funnel y 81 % en upper-funnel. Si tu reporting dice que el 50 % del revenue atribuido es de existentes, la parte incremental para nuevos es probablemente menor de lo que crees. [EMPIRICAL]
- **BFCM es el momento de máximo riesgo de "robo de crédito"**: en BFCM 2025 el revenue de clientes recurrentes creció +13,5 % interanual y email/SMS fueron el 42 % del revenue (datos Klaviyo citados por AdBeacon). Meta, con 1d view, reclama parte de esas compras. [EMPIRICAL vía vendor]

## 1. Definiciones

### 1.1 Las tres definiciones de Meta (Configuración de anuncios)

| Segmento | Cómo se define | Comentario |
|---|---|---|
| **Clientes existentes** | Custom audiences que tú eliges: compradores web (Pixel/CAPI Purchase, máx. 180 días), listas de clientes (CRM), compradores en app, offline | Calidad = cobertura de tu lista + match rate del hash |
| **Audiencia con interacción (engaged)** | Custom audiences de interacción: visitantes web, interacciones con página/perfil IG, vídeo, anuncios, etc. | Opcional, pero sin ella "nuevo" incluye visitantes calientes |
| **Nuevo** | Cualquiera fuera de las dos anteriores | Meta no lo define positivamente; es el residuo |
| *Desconocido* | Personas no clasificables | Aparece en algunos breakdowns |

[OFFICIAL META + practitioners (Jon Loomer)]

### 1.2 En la tienda

- **Cliente nuevo** = primer pedido de ese cliente (email/teléfono/ID). Shopify y similares lo marcan (*first-time* vs *returning*).
- **Cliente reactivado** = cliente con último pedido > X días (p. ej. 365). Conviene tratarlo como categoría propia: económicamente se parece más a un nuevo que a un recurrente activo. [STRONG INFERENCE]
- **GA4 "new users"** ≠ clientes nuevos (es un cookie/dispositivo nuevo). No usar para nCAC. [STRONG INFERENCE]

### 1.3 Incremental

El cliente nuevo incremental es el que **no habría comprado** sin la publicidad. Solo se estima con experimentos (Conversion Lift, geo-lift, holdouts). Haus mide con KPI "New Customers" o "New Orders" en muchos de sus tests (Javvy, Dr. Squatch usó "New revenue"). [EMPIRICAL]

## 2. Por qué el sistema tiende a los existentes (primeros principios)

1. La subasta ordena por *valor total* ≈ puja × probabilidad estimada de conversión + calidad.
2. Un cliente existente o un visitante reciente tiene una probabilidad de conversión 5–20× superior a un desconocido (orden de magnitud plausible; varía por negocio). [HYPOTHESIS en la cifra]
3. Con optimización a coste por compra mínimo, el sistema "aprende" que esas personas son baratas y les asigna gasto.
4. La atribución (7d clic + 1d vista) les asigna compras que en parte ocurrirían igual (email, búsqueda de marca, directo).
5. Resultado: ROAS de plataforma alto, nCAC alto, crecimiento de base de clientes bajo.

## 3. Herramientas de control (estado oct-2026)

| Herramienta | Nivel | Qué hace | Cuándo usar | Etiqueta |
|---|---|---|---|---|
| **Customer lifecycle strategy → "Adquirir clientes nuevos"** | Ad set (campañas de Ventas) | Excluye automáticamente a compradores de los datos de conversión de la cuenta (730 d por defecto; 180/90/60/30 opcionales; no desactivable) + exclusiones manuales opcionales; aviso de posible mayor CPA | Campañas de adquisición puras | [OFFICIAL META] (GA 6/7-oct-2026) + [EMPIRICAL] (mecánica observada por Jon Loomer, 13-oct-2026) |
| **Exclusión de custom audience** | Ad set (control duro incluso en Advantage+) | Excluye la lista que elijas | Cuando quieres controlar qué lista exactamente | [OFFICIAL META] |
| **2 ad sets (existentes con cap / resto con exclusión)** | Campaña CBO | Replica el antiguo cap con `daily_min_spend_target` y `daily_spend_cap` | Quieres algo de gasto en existentes pero acotado | [OFFICIAL META] |
| **Audience Label para excluir existentes con un clic** | Ad set | Exclusión simplificada | En test (oct-2026) | [OFFICIAL META vía prensa] |
| **Value rules** | Cuenta/campaña | Ajusta puja ±(hasta +1.000 % / −90 %) por edad, género, ubicación, dispositivo, OS, placement y *audience labels* | Pujar menos por segmentos con alta proporción de recurrentes | [EMPIRICAL] — su uso para nuevos vs existentes no está documentado |
| **Reporting por segmentos** | Ads Manager breakdown | Nuevos / Engaged / Existentes | Siempre | [OFFICIAL META] |
| **Parámetro URL de tipo de audiencia** | Cuenta | Etiqueta clics de "prospecting" vs "retargeting" en analítica | Leer en GA4/BI | [OFFICIAL META] |
| ~~Existing customer budget cap~~ | — | Retirado (feb-2025; `existing_customer_budget_percentage` deprecado en v25, campañas pausadas en v26) | — | [OUTDATED] |

**[OUTDATED]**: "Pon el existing customer budget cap al 10–20 % en ASC" — consejo de 2023-2024 que ya no se puede aplicar desde la consolidación en Advantage+ sales (feb-2025) y queda bloqueado en API (v25/v26).

## 4. Construir bien la lista de clientes existentes

1. **Purchase web 180 días** (máximo de retención de audiencias web) vía Pixel + CAPI.
2. **Lista CRM de todos los compradores de 2–3 años** (email, teléfono, nombre, país, ciudad, CP para mejorar match), sincronizada automáticamente (Shopify/Klaviyo/CDP) al menos semanalmente; AdBeacon recomienda subir una lista fresca a principios de noviembre que cubra ≥2 años de compradores. [EMPIRICAL, vendor]
3. **Compradores en app y offline/tienda física** si existen.
4. **Suscriptores activos** (si vendes suscripción) — normalmente deben excluirse de adquisición.
5. **Engaged**: visitantes web 30–180 días, interacciones IG/FB 90–365 días.

Control de calidad: compara el % de revenue atribuido a "existentes" en Meta con el % de pedidos de recurrentes en tu tienda en el mismo periodo. Si Meta dice 15 % y la tienda 45 %, la lista está incompleta o el match es bajo. [EMPIRICAL — método AdBeacon]

## 5. Medir el % de nuevos y el nCAC

### 5.1 Cuatro nCAC, de más optimista a más honesto

| Métrica | Fórmula | Uso |
|---|---|---|
| nCAC de plataforma | Gasto Meta / compras atribuidas a segmento "Nuevo" | Diagnóstico diario; sobreestima nuevos si la lista es mala |
| nCAC Meta (tienda) | Gasto Meta / pedidos de primeros clientes con último clic o UTM de Meta | Atribución por clic; subestima view-through |
| **nCAC blended** | Gasto total de marketing / clientes nuevos de tienda | **Métrica de gestión principal** (conservadora) |
| nCAC incremental | Gasto testado / clientes nuevos incrementales (lift) | Calibración semestral |

### 5.2 Ejemplo trabajado: ROAS "bueno", adquisición cara

Semana de una marca de cosmética (datos ilustrativos):

- Gasto Meta: 20.000 €.
- Revenue atribuido por Meta (7d clic + 1d vista): 80.000 € → **ROAS 4,0**.
- Breakdown de segmentos: 65 % del revenue atribuido de "Existentes" (52.000 €) y 35 % "Nuevos" (28.000 €).
- AOV nuevos: 56 € → 500 compras nuevas atribuidas.
- Gasto que fue a existentes según breakdown: 7.000 €; a nuevos/engaged: 13.000 €.

Cálculos:
- ROAS de nuevos (plataforma) = 28.000 / 13.000 = **2,15**.
- nCAC plataforma = 13.000 / 500 = **26 €**.
- En tienda, la semana tuvo 380 clientes nuevos totales (todas las fuentes) y el resto del marketing de adquisición (Google no-marca, TikTok) costó 6.000 €. nCAC blended = (20.000 + 6.000) / 380 = **68,4 €** (incluyendo los 7.000 € gastados en existentes, que no son de adquisición). Excluyéndolos: (13.000 + 6.000)/380 = **50 €**.
- Si el margen CM2 del primer pedido es 56 € × 55 % = 30,8 €, cada cliente nuevo cuesta 50–68 € y aporta 30,8 € en el primer pedido: **se pierde dinero en el primer pedido** pese al ROAS 4,0. Solo compensa si la recompra a 90–180 días aporta > 20–38 € de CM2 adicional.

Lección: el ROAS 4,0 era sobre todo revenue de recurrentes (probablemente muy poco incremental si email/SMS ya los activaba).

### 5.3 Cómo medir el % de nuevos sin engañarte

1. **Tienda**: % de pedidos y revenue de primeros clientes por semana (verdad contable).
2. **Meta**: breakdown por segmentos (requiere definiciones de cuenta bien hechas).
3. **Encuesta post-compra** ("¿Dónde nos conociste?") para nuevos: señal de canal de descubrimiento que la atribución no ve. [EMPIRICAL, práctica DTC extendida]
4. **Lift test** con KPI "clientes nuevos" 1–2 veces al año (y antes de BFCM).

## 6. Fijar objetivos de adquisición

(Desarrollo completo en `05-economia-ecommerce-margenes-mer-ltv.md`.)

- **nCAC objetivo (first-order break-even)** = CM2 del primer pedido (revenue neto − COGS − envío − pago − devoluciones − descuentos).
- **nCAC objetivo (con recompra)** = CM2 primer pedido + CM2 esperado de recompras en la ventana de payback aceptada (p. ej. 90 o 180 días), ajustado por riesgo.
- **Regla de escalado** (8x, vendor de finanzas DTC): ratio CM2/nCAC > 1,0 → rentable en el primer pedido; 0,7–1,0 → se recupera con recompra; < 0,7 → no escalar hasta cambiar la economía. [EMPIRICAL, vendor — útil como heurística]

## 7. ¿Cuándo sí invertir en Meta para clientes existentes?

| Caso | Por qué | Cómo |
|---|---|---|
| Reactivación de inactivos (último pedido > 180–365 días) | Email/SMS ya no les llega (bajas, apertura baja) | Audiencia de lista CRM segmentada; holdout 10–20 % |
| Lanzamiento de producto nuevo a la base | Alcance rápido de una novedad | Ventana corta, presupuesto acotado |
| Consumibles con recompra predecible | Recordatorio en el momento de agotamiento | Mejor por email/SMS; Meta solo si demuestra incrementalidad |
| Cross-sell de alto valor | Complementos con margen | Catalog custom audiences por product set comprado |
| Clientes de alto LTV (VIP) | Retención de alto valor | Presupuesto pequeño, creatividad específica |

**[CONTESTED]**: algunos practitioners (inspirados en Byron Sharp / Ehrenberg-Bass) defienden no excluir clientes para mantener disponibilidad mental y porque la mayoría de las marcas crecen por compradores ligeros que ya compraron alguna vez. Otros (enfoque de unit economics, CTC/AdBeacon) separan estrictamente adquisición y retención. Ambas posturas aciertan en su contexto: excluir en **campañas de adquisición** y financiar **retención** con presupuesto y KPI propios (incrementalidad), no dejar que se mezcle en la campaña principal.

## Implicaciones operativas

- Define *Clientes existentes* y *Engaged* en la cuenta **antes** de leer cualquier breakdown.
- Elige la ventana de la exclusión automática de Customer lifecycle strategy según tu ciclo de recompra: 730 días = adquisición estricta (también excluye inactivos); 90–180 días = los clientes inactivos vuelven a contar como "nuevos" (útil si la reactivación es parte del objetivo, pero entonces no llames "nCAC" a ese coste sin separar reactivados en tienda). [STRONG INFERENCE]
- Campaña(s) de adquisición: Customer lifecycle strategy = nuevos o exclusión de la lista de clientes. Campaña de retención/reactivación separada con presupuesto acotado y holdout.
- KPI semanal de adquisición: **clientes nuevos (tienda) y nCAC blended**; ROAS de plataforma solo como diagnóstico.
- Si el % de gasto en existentes en la campaña principal > 20–30 % y email/SMS es fuerte → restringir. [STRONG INFERENCE]
- Antes de BFCM: lista de clientes fresca (≥ 2 años), techo de nCAC por día, y decidir conscientemente si se pagará por llegar a existentes durante la promoción.

## Errores frecuentes

- Confiar en el segmento "Nuevo" de Meta con una lista de clientes de 3 meses.
- Medir "nuevos" con GA4 new users.
- Excluir solo compradores de 30 días y llamar "nuevos" a los de hace 60.
- Celebrar un ROAS récord en BFCM sin mirar que el 70 % fue de recurrentes.
- Excluir existentes en **todas** las campañas y luego extrañarse de la caída de recompra de lanzamientos.
- Usar el antiguo cap del 10–20 % como si siguiera existiendo.

## Preguntas abiertas

- Confirmación oficial de la mecánica de Customer lifecycle strategy (exclusión automática por Purchase 730 d según Loomer vs 180 d según CTC) y del Audience Label en test.
- Si Meta usa las definiciones de cuenta también para optimizar (no solo para reportar) cuando no se activa Customer lifecycle strategy.
- Magnitud media del sobrecoste por resultado al activar adquisición pura (no hay datos públicos).
- Interacción entre value rules con audience labels y Customer lifecycle strategy.

## Fuentes clave

- [Advantage+ Campaigns — replicar existing customer budget](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
- [Audience type URL parameters](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-shopping-campaigns/audience-type-url-parameters.md) — Meta for Developers — meta-developers
- [Meta Ads' New Setting: "New Customer Acquisition"](https://spilnoagency.com.ua/en/news-en/meta-ads-new-customer-acquisition) — 2026-06-24 — agencia
- [Meta Adds Automatic Customer Exclusions (Jon Loomer)](https://www.jonloomer.com/meta-automatic-customer-exclusions/) — 2026-10-13 — practitioner
- [Meta's Customer Lifecycle Strategy Is Now Live for All Advertisers (CTC)](https://commonthreadco.com/blogs/coachs-corner/meta-customer-lifecycle-strategy-all-advertisers-bfcm-2026) — 2026-10-11 — agencia
- [Meta Advertising Week 2026 Ad Tools: Live vs Testing](https://www.relevantaudience.com/meta/meta-advertising-week-new-york-2026-ad-tools/) — 2026-10 — agencia
- [Meta Opens Customer Lifecycle Strategy to All Advertisers](https://aifrontierreview.com/articles/2026-10-09-meta-rolls-out-net-new-customer-targeting-and-ai-video-ads-to-all-advertisers-at/) — 2026-10-09 — prensa
- [Is Meta Taking Credit for Your Holiday Repeat Buyers (AdBeacon)](https://www.adbeacon.com/meta-attribution-new-vs-returning-customers-bfcm/) — 2026-10-07 — vendor
- [The Meta Report (Haus)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Get Started with Advantage+ Shopping Campaigns (Jon Loomer)](https://www.jonloomer.com/advantage-plus-shopping-campaigns/) — 2023-2025 — practitioner (histórico del cap)
- [DTC unit economics / CM2 (8x)](https://eightx.co/blog/what-is-cm2-contribution-margin-after-fulfillment) — 2026 — vendor
- [Value Rules: A Deep Dive (Jon Loomer)](https://www.jonloomer.com/value-rules/) — 2025 — practitioner
