# Advantage+ catalog ads (antes: Dynamic Ads / DPA)

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A06 (agente) · Ámbito: anuncios dinámicos de catálogo en Meta para e-commerce: prospección amplia vs retargeting, product sets, formatos, cuándo funcionan y evidencia 2024-2026. Catálogo/feeds en `01-…`; Advantage+ sales en `03-…`.

## TL;DR

- **Nomenclatura:** "Advantage+ catalog ads" (antes Dynamic Ads / DPA; "DABA" era el nombre coloquial de dynamic ads for broad audiences). No es un tipo de campaña: es un **tipo de creatividad/anuncio** que puede vivir en campañas Sales manuales, en Advantage+ sales campaigns y (con limitaciones) en Traffic, Leads y App. [OFFICIAL META]
- **Desde ene-2025 Meta retiró el selector "Audience Types" (broad / retargeting / cross-sell) en catalog ads con objetivo Ventas**: por defecto la entrega se reparte automáticamente entre prospección y remarketing. El retargeting explícito se hace ahora con **catalog custom audiences** (incluir/excluir por interacción con producto o product set). [OFFICIAL META vía Social Media Today 29-ene-2025; Jon Loomer]
- **El retargeting dinámico es el sitio donde más se infla el ROAS de plataforma.** Evidencia: Javvy (Haus, geo-lift) encontró que su campaña bottom-of-funnel (estáticos, testimonios, banners promo) tenía un coste por adquisición incremental un 250 % superior a lo que decía la atribución por clic, y la campaña TOF fue >13× más incremental. Cifras de terceros (40–70 % menos iROAS que el ROAS reportado en retargeting) circulan atribuidas a Haus, pero no las he podido verificar en fuente primaria. [EMPIRICAL] (Javvy) / [HYPOTHESIS] (rango 40–70 %)
- **Catalog ads en prospección amplia funcionan bien en catálogos grandes, visuales y de compra por impulso/precio** (moda, hogar, belleza, deporte, juguetes, marketplaces). Funcionan mal en monoproducto, productos que requieren explicación y tickets altos de larga consideración, donde manda la creatividad de concepto. [STRONG INFERENCE] + [EMPIRICAL, anecdótico de practitioners]
- **Optimizar catalog ads a valor puede ser más incremental que optimizar a volumen**: Cruise Critic reportó +22 % de ROAS incremental con value optimization frente a optimización por volumen (success story de Meta citado por terceros). [OFFICIAL META vía secundaria]
- **Mezcla catálogo + creadores**: Sephora US (ago–sep 2025) combinó partnership ads con creadores + Advantage+ catalog ads + Advantage+ audience → 1,56× ROAS incremental omnicanal (lift study de Meta, citado por terceros). [OFFICIAL META vía secundaria]
- **El catálogo ya es "por defecto" multimedia**: Dynamic Media (imagen o vídeo de catálogo según predicción) está en opt-in por defecto desde sep/oct-2025; sin vídeos en el feed no aporta nada. [OFFICIAL META]
- **Regla de presupuesto práctica**: el retargeting dinámico "puro" debería ser una fracción pequeña del gasto (Haus observó ~15 % del gasto en retargeting de media en su muestra, sin diferencia entre Advantage+ y manual); por encima de 20–25 % del gasto total, exige test de incrementalidad. [EMPIRICAL] (15 %) / [STRONG INFERENCE] (umbral)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Product showcase por defecto en la API v27 (4-nov)**: Meta puede añadir productos del catálogo a anuncios nuevos (`product_extensions`). Opt-out: `degrees_of_freedom_spec.creative_features_spec.product_extensions.enroll_status=OPT_OUT`; vista previa en `GET /{ad-account-id}/product_extensions/catalog_suggestions_preview`. **[OFFICIAL META]**
> - **"Añadir la navegación por productos"** figura en la lista oficial de mejoras de Advantage+ creative; se activó en anuncios existentes ~28-oct salvo opt-out. **[OFFICIAL META]** (mejora) + **[EMPIRICAL]** (fecha)
> - **Ofertas detectadas en la web** añadidas a anuncios copiados (6–8-nov), aunque las promociones estuvieran desactivadas: revisa Commerce Manager → Settings → Offer merchandising → "Detected offers". **[EMPIRICAL]**
> - `POST /{catalog-id}/batch` pasa a `items_batch` en la v27. **[OFFICIAL META]**
> - Fuentes: S10-099, S10-108, S10-125, S10-126, S10-129 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

## 1. Qué es exactamente y cómo decide

Componentes [OFFICIAL META — overview de Advantage+ catalog ads]:

1. **Feed de catálogo** → imágenes, precios, descripciones y vídeos se insertan en plantillas.
2. **Medición y audiencias** → Pixel/CAPI o App Events registran ViewContent, AddToCart, Purchase vinculados a `content_ids`.
3. **Entrega** → el sistema decide *a quién* mostrar el anuncio y *qué productos* del product set mostrarle a esa persona.

Implicación desde primeros principios: un catalog ad tiene **dos problemas de ranking** (persona y producto). El rendimiento depende de (a) la señal de eventos con IDs correctos y (b) la variedad y calidad del catálogo. Un catálogo de 30 productos con 1 imagen cada uno deja poco que optimizar en el segundo problema; ahí, un anuncio de concepto suele ganar.

Objetivos soportados vía API: `PRODUCT_CATALOG_SALES` (legacy), `CONVERSIONS`/`OUTCOME_SALES`, `LINK_CLICKS`, `APP_INSTALLS`; existe también variante de **catalog ads para leads** (`OUTCOME_LEADS`, `LEAD_GENERATION`) útil en automoción/inmobiliaria/viajes, y **catalog ads en Threads** (solo imagen y carrusel de imágenes). [OFFICIAL META]

## 2. El cambio de 2025: adiós al selector de audiencia

- **Antes (2017–2024):** al crear un catalog ad elegías *Retarget* (viewed/added to cart, ventana N días), *Cross-sell/Upsell* o *Broad audience* (DABA).
- **Desde ene-2025** (Social Media Today, 29-ene-2025): Meta elimina "Audience Types" en catalog ads con objetivo Ventas. La entrega se reparte automáticamente entre prospección y remarketing. Para controlar, se crean **catalog custom audiences** (fuente: catálogo; reglas por evento, product set y ventana) y se usan para incluir o excluir. Requiere Pixel/SDK. [OFFICIAL META vía prensa]
- **Estructura actual reportada** (terceros, 2026): en el flujo de Ventas se activa "Product data/catálogo" a nivel campaña (**un catálogo por campaña**) y en cada anuncio se elige "productos del catálogo" como fuente creativa y el product set. [STRONG INFERENCE — varias guías coinciden, sin confirmación en doc oficial localizada]
- Una fuente agregadora afirma que en ene/feb-2026 los catalog ads "perdieron targeting manual por completo"; contradice a Loomer/SEL/SMT, que mantienen que el retargeting sigue siendo posible con catalog custom audiences. [CONTESTED] — Verificar en la cuenta.

Desde ~ago-2026, además, se retiran los controles de placement a nivel ad set en Sales/Leads/App promotion (Engagement no; corrección 2026-11-09) (solo quedan exclusiones a nivel cuenta y value rules para bajar puja hasta −90 %). [OFFICIAL META vía Help Center citado por terceros; despliegue progresivo]

## 3. Prospección amplia con catálogo ("broad catalog")

### Cuándo funciona [STRONG INFERENCE + EMPIRICAL anecdótico]

| Condición | Por qué |
|---|---|
| Catálogo ≥ ~100–200 SKUs con demanda dispersa | El ranking de producto tiene donde elegir; cada persona ve algo relevante. |
| Productos que se entienden con la foto (moda, hogar, decoración, accesorios, juguetes) | El anuncio no necesita explicar un mecanismo. |
| Precio como argumento (outlet, marketplaces, retail) | Overlays de precio/descuento hacen el trabajo creativo. |
| Señal de eventos abundante y match rate alto | El sistema aprende afinidad persona-producto. |
| Ticket bajo-medio (< ~150 €) | Decisión rápida, visual. |

### Cuándo NO (o no solo)

- **Monoproducto / hero product**: el catálogo no añade variedad; ganan los anuncios de concepto (problema-solución, demo, UGC). Un catalog ad puede servir como *formato adicional* de retargeting o con product extensions.
- **Producto que requiere educación** (suplementos con mecanismo, gadgets nuevos, cosmética activa, colchones): el packshot no vende; la creatividad de concepto sí.
- **Ticket alto con ciclo largo** (HexClad, 699,99 $, ciclo de consideración largo — caso Haus): la venta llega semanas después; un catalog ad de retargeting reclama crédito de una decisión ya tomada por otros estímulos.

### Evidencia de practitioners

- Un practitioner reporta haber pasado de ~70 % del gasto de catálogo en retargeting a ~70 % en Advantage+ broad en dos años: el retargeting sigue ganando en ROAS reportado, broad gana en revenue absoluto porque el pool es ~100× mayor. Anecdótico, una cuenta. [EMPIRICAL, baja]
- Benchmarks de ROAS de plataforma que circulan (broad 1,2–2,5×; retargeting DPA 2,5–6× o incluso 6–12×) son de vendors sin metodología y, sobre todo, **no son incrementales**. No los uses como objetivo. [HYPOTHESIS]

## 4. Retargeting dinámico: útil, pero el más sobreestimado

### Por qué se sobreestima (primeros principios)

La audiencia de retargeting (visitó, añadió al carrito) tiene una probabilidad base de compra alta **sin anuncio**. La atribución (7d clic + 1d vista) asigna al anuncio compras que habrían ocurrido igual. Cuanto más cerca de la compra está la audiencia, mayor la diferencia entre ROAS atribuido e incremental.

### Evidencia

| Fuente | Hallazgo | Etiqueta |
|---|---|---|
| Haus — Javvy Coffee (nov-2024; geo-lift, dos tests secuenciales de 2+1 semanas, KPI pedidos nuevos Shopify + Amazon) | Campaña BOF (estáticos, testimonios, banners de promo) vs TOF (vídeo problema-solución), ambas en Advantage+ Shopping con presupuesto 50/50: TOF >13× más incremental; CPIA de BOF 250 % mayor que lo reportado por MTA de clic; CPIA de TOF 20 % menor que lo reportado. Javvy movió la mayoría del presupuesto a TOF y mejoró CAC y MER. | [EMPIRICAL] (caso único, publicado por el vendor) |
| Haus — Meta Report (640 tests, 2024–2025) | Retargeting ≈15 % del gasto de media, plano entre Advantage+ y manual. Mid-funnel y upper-funnel tienen mayor % de clientes nuevos (78 % y 81 % vs 67 %). | [EMPIRICAL] |
| Blogs que citan "Haus 2025" | iROAS de retargeting 40–70 % por debajo del ROAS reportado; 1,5–3× de sobreestimación. | [HYPOTHESIS — no trazado a fuente primaria] |

### Reglas operativas para retargeting dinámico

1. **Ventanas cortas y por intención**: AddToCart/InitiateCheckout 1–7 días; ViewContent 3–14 días. Ventanas de 30–180 días convierten el "retargeting" en prospección cara de gente que ya decidió no comprar. [STRONG INFERENCE]
2. **Excluir compradores recientes** (Purchase 7–30 días según ciclo de recompra) — la exclusión opera a nivel `item_group_id` en audiencias dinámicas. [OFFICIAL META]
3. **Frecuencia**: vigilar frecuencia semanal; > 4–5 impresiones/semana a una audiencia pequeña suele indicar saturación. [STRONG INFERENCE]
4. **Presupuesto**: no "escalar" retargeting; su tamaño lo define el tráfico que genera la prospección.
5. **Mensaje**: en retargeting, el catálogo funciona mejor con señal de urgencia real (stock bajo, fin de promo), reseñas, garantía, envío/devolución — no con el mismo packshot que ya vieron.
6. **Medición**: antes de defender un retargeting con ROAS 8×, haz un holdout (10–20 % de audiencia o geo) o al menos compara con Conversion Lift. Ver `04-tracking-atribucion-medicion/` (otro agente).

### Cross-sell / upsell

Con catalog custom audiences: "compró en product set A en los últimos N días" → mostrar product set B (complementos). Funciona en categorías con complementariedad clara (cámara → objetivos; cafetera → cápsulas; ropa → accesorios). Para recompra de consumibles, el email/SMS suele ser más barato que Meta para clientes existentes. [STRONG INFERENCE]

## 5. Product sets dentro de catalog ads

Ver `01-…` §6. Resumen para campañas:

- **Por defecto**: product set "todo menos exclusiones" en prospección.
- **Separar** cuando haya motivo económico: margen (el sistema optimiza revenue, no margen), ticket (para no hundir AOV), stock, tentpoles (BFCM), novedades.
- **No separar por categoría** salvo que la economía o el mensaje sean muy distintos: fragmenta señal.
- **Value optimization** con catálogo: requiere volumen de compras con valores variados; el caso Cruise Critic (+22 % iROAS vs volumen) sugiere probarlo cuando el AOV varía mucho entre productos. [OFFICIAL META vía secundaria]
- **Value rules** (bid +1000 %/−90 % por edad, género, ubicación, dispositivo, placement, OS, audience labels; lanzadas jun-2025): una fuente indica que a principios de 2026 no estaban disponibles para Advantage+ catalog ads. [HYPOTHESIS — no verificado]

## 6. Formatos

| Formato | Cuándo | Notas |
|---|---|---|
| Carrusel | Por defecto; varios productos relevantes por persona | Descripciones con template tags (hasta 3); end card opcional. Carrusel 1:1 en FB Feed, 4:5 en IG Feed. [OFFICIAL META] |
| Imagen única / vídeo | Producto concreto, retargeting de producto visto | Dynamic Media mezcla imagen y vídeo. |
| Colección (Instant Experience) | Móvil, catálogo visual, "tienda dentro del anuncio" | Mínimo 4 productos válidos en el set; portada por defecto = vídeo de catálogo generado; no soportado en Shops ads. [OFFICIAL META + EMPIRICAL] |
| Format automation | Dejar que Meta elija carrusel/colección por impresión | Opt-in. [OFFICIAL META] |

## 7. Catalog ads dentro de Advantage+ sales

- Advantage+ sales admite catalog ads junto a anuncios de concepto en el mismo ad set; con Dynamic Media y Advantage+ creative, la frontera entre "anuncio de catálogo" y "anuncio normal" se difumina (product extensions añade productos del catálogo bajo anuncios estáticos). [OFFICIAL META]
- **Riesgo**: en Advantage+ sales sin control de clientes existentes, los catalog ads tienden a capturar retargeting barato (gente que ya iba a comprar) → ROAS alto, incrementalidad baja. Mitigación: Customer lifecycle strategy / exclusiones, y reporting por segmentos (nuevos / engaged / existentes). Ver `03-…` y `04-…`. [STRONG INFERENCE]
- Práctica observada: muchas cuentas DTC separan "catálogo" en un ad set o campaña propia para poder leer su contribución, aunque Meta empuja a consolidar. [EMPIRICAL, practitioners] — decisión a validar con test, no con ROAS de plataforma.

## 8. Cuándo los catalog ads son la columna vertebral vs un complemento

| Tipo de negocio | Rol del catálogo | Rol de la creatividad de concepto |
|---|---|---|
| Moda/retail multimarca, >1.000 SKUs | Columna vertebral (prospección + retargeting) | Campañas de marca, lanzamientos, tentpoles |
| Hogar/decoración, 200–2.000 SKUs | Alto | Medio-alto (estilo de vida, colecciones) |
| Belleza/cosmética con hero products | Medio (retargeting, cross-sell) | Alto (demo, antes/después, creadores) |
| Monoproducto / pocos SKUs | Bajo (formato de apoyo) | Columna vertebral |
| Ticket alto, ciclo largo | Bajo-medio (recordatorio) | Alto + medición con ventanas largas |
| Marketplace/outlet con precio como ventaja | Muy alto (precio + overlays) | Bajo-medio |

[STRONG INFERENCE]

## Implicaciones operativas

- Lanza catalog ads **solo** con match rate ≥ 90 % (mínimo 70 %).
- Prospección con catálogo: product set amplio, Advantage+ audience, formatos automáticos, vídeo en top SKUs; juzga con nCAC y MER, no con ROAS de plataforma.
- Retargeting dinámico: ventanas cortas, exclusión de compradores, tope de presupuesto implícito por tamaño de audiencia, y un holdout al menos una vez al año (o antes de BFCM).
- Si el reporting por segmentos muestra que > 30–40 % del gasto de una campaña con catálogo va a clientes existentes, activa estrategias de adquisición (Customer lifecycle strategy / exclusiones) y compara nCAC. [STRONG INFERENCE]
- Para tickets altos o productos que requieren explicación, el catálogo es complemento; invierte primero en creatividad de concepto.

## Errores frecuentes

- Defender el retargeting por su ROAS atribuido sin test de incrementalidad.
- Ventanas de retargeting de 180 días "para tener volumen".
- No excluir compradores recientes (pagas por anunciar lo que ya compraron).
- Catálogo con IDs que no casan → "retargeting dinámico" que muestra productos genéricos.
- Fragmentar product sets por categoría y dejar ad sets en learning limited.
- Asumir que "broad catalog" sustituye a la creatividad en monoproducto.

## Preguntas abiertas

- Estado exacto (oct-2026) del targeting manual en catalog ads de Ventas: ¿solo catalog custom audiences o también desapareció eso en algunas cuentas? Reportes contradictorios.
- Disponibilidad de value rules en Advantage+ catalog ads en 2026.
- Cuantificación independiente de la incrementalidad del retargeting dinámico en 2025-2026 (el rango 40–70 % no está trazado).
- Efecto de la generación de vídeo desde imágenes de catálogo (beta oct-2026) en rendimiento.

## Fuentes clave

- [Advantage+ Catalog Ads overview](https://developers.facebook.com/docs/marketing-api/advantage-catalog-ads) — Meta for Developers — meta-developers
- [Advantage+ catalog ads for lead generation](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-catalog-ads-for-leadgen) — Meta for Developers — meta-developers
- [Threads ads: Advantage+ catalog ads](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-creative/threads-ads/creation/advantage-catalog-ads) — Meta for Developers — meta-developers
- [Meta Updates Audience Targeting Options for Advantage+ Catalog Ads](https://www.socialmediatoday.com/news/meta-advantage-plus-catalog-ad-targeting-update/738671/) — 2025-01-29 — prensa
- [Audience Types Going Away for Advantage+ Catalog Ads](https://www.jonloomer.com/qvt/audience-types-advantage-plus-catalog-ads/) — 2025 — practitioner
- [Haus customer story: Javvy Coffee](https://www.haus.io/customer/javvy) — 2024-11-04 — vendor
- [The Meta Report: Lessons from 640 Haus Incrementality Experiments](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Facebook Advertising Case Studies (Sephora US, Cruise Critic vía Meta success stories)](https://cropink.com/meta-ads-examples) — 2025-2026 — vendor (cita Meta)
- [Value Rules: A Deep Dive](https://www.jonloomer.com/value-rules/) — 2025 — practitioner
- [Dynamic product audiences](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/guides/dynamic-product-audiences.md) — Meta for Developers — meta-developers
