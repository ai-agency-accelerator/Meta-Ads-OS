# Catálogo, feeds y product sets (Commerce Manager)

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: catálogos de producto para Meta Ads (e-commerce), calidad de feed, variantes, product sets, media de catálogo (imagen, vídeo, overlays). La parte de anuncios dinámicos está en `02-advantage-plus-catalog-ads.md`.

## TL;DR

- **El catálogo ya no es "la cosa de los DPA": es inventario creativo y señal de producto para casi todo el e-commerce en Meta.** Alimenta Advantage+ catalog ads, product extensions ("Add catalog items") en anuncios estáticos, Shops ads, collection ads, partnership ads dinámicos y la generación IA de vídeo de producto. Un feed pobre limita todas esas superficies a la vez. [OFFICIAL META] (docs de Marketing API, ver Fuentes) + [STRONG INFERENCE] sobre el peso relativo.
- **El problema número uno no es el feed, es el *match* entre los `content_ids` del Pixel/CAPI y los IDs del catálogo.** Si no casan, no hay retargeting dinámico, no hay señal producto-nivel y el sistema recomienda peor. Meta pide coincidencia exacta de ID y de `content_type` (`product` vs `product_group`); en su documentación de Product Set Optimization fija >90 % como objetivo y 70 % como mínimo de match rate. [OFFICIAL META]
- **En Shopify el fallo clásico es variante vs producto padre**: el pixel envía el ID de producto y el catálogo usa el ID de variante (o al revés). Diagnóstico en Commerce Manager → Eventos → IDs inválidos. [EMPIRICAL] (hilos de comunidad Shopify, DataFeedWatch)
- **Campos que más mueven rendimiento (por orden práctico):** `availability` y `price`/`sale_price` exactos (si no, rechazos y mala experiencia), `image_link` + `additional_image_link` (hasta 20) con lifestyle, `video[n].url` (hasta 20 por producto, 200 MB), `title` legible (≤65 caracteres recomendado), `item_group_id` correcto e `internal_label` para segmentar. [OFFICIAL META] (límites) + [STRONG INFERENCE] (orden)
- **Usa `internal_label` (no `custom_label_0-4`) para construir product sets dinámicos** (margen, bestseller, stock, campaña): Meta lo recomienda porque se actualiza sin revisión de políticas y admite hasta 5.000 etiquetas por producto. [OFFICIAL META]
- **El vídeo de catálogo (Catalog Product Video) pasó a ser "por defecto"**: Dynamic Media se activó por defecto en Advantage+ catalog ads creados vía API desde el 1-sep-2025 y con opt-in forzado al 100 % desde el 20-oct-2025. Si no subes vídeos, el ajuste no hace nada; si los subes, Meta decide imagen vs vídeo por impresión. [OFFICIAL META]
- **Cobertura de vídeo recomendada por Meta:** apuntar a ~30 % de impresiones en vídeo; con 1–100 productos basta ~20 % de cobertura; con >50.000 productos ~500 vídeos (los más vendidos). [OFFICIAL META]
- **Overlays/frames: útiles para precio, descuento y señales de confianza, pero la evidencia pública es casi toda de vendors** (Confect, Cropink, Marpipe) y confundida con otros cambios. Testéalos con A/B controlado. [CONTESTED]/[HYPOTHESIS] en magnitud.
- **Octubre 2026:** Meta abrió en beta "catalog product video from product images" (imagen → vídeo a escala, desde Ads Manager y Commerce Manager) para anunciantes elegibles. Útil para catálogos grandes sin presupuesto de vídeo; calidad y control de marca por validar. [OFFICIAL META] (vía resumen de prensa del post de Advertising Week)

## 1. Por qué el catálogo importa más en 2026 que en 2020

Razonamiento desde primeros principios:

1. **El sistema de Meta ya decide casi todo menos qué productos y qué creatividades le das.** Con Advantage+ (presupuesto, audiencia y placements automatizados) y la retirada progresiva de controles manuales (placements a nivel ad set retirados en Sales/Leads/App promotion (Engagement no; corrección 2026-11-09) desde ~ago-2026; audiencias como "sugerencias"), las palancas del anunciante se concentran en: oferta, creatividad, señal (eventos) y **catálogo**. Ver `03-advantage-plus-sales-ecommerce.md`.
2. **El catálogo es creatividad a escala.** Un catálogo de 5.000 SKUs con 3–5 imágenes cada uno, vídeo en los top sellers y etiquetas limpias es, para el sistema de recuperación de anuncios, miles de "candidatos" relevantes. Meta lo llama *creative liquidity* en el anuncio del cambio de Dynamic Media (ago-2025). [OFFICIAL META]
3. **El catálogo es señal de producto.** Con `content_ids` correctos, cada ViewContent/AddToCart/Purchase queda vinculado a un SKU, precio y categoría. Eso permite retargeting dinámico, cross-sell y que el sistema aprenda qué productos convierten para qué personas. Sin match, el catálogo es un escaparate sin datos.
4. **El catálogo empieza a ser infraestructura para agentes de compra.** En 2026 Meta prueba checkout en Messenger (Meta Business Agent + Shopify) y en Meta AI (Adyen, PayPal, Shopify, Stripe), y recomendaciones de producto IA. Todos tiran de datos de catálogo. [OFFICIAL META] (anuncios oct-2026, en test) — implicación práctica: títulos y atributos legibles por máquina ganan valor. [STRONG INFERENCE]

## 2. Cómo se alimenta un catálogo

| Método | Cuándo usarlo | Notas operativas |
|---|---|---|
| Integración de plataforma (Shopify "Facebook & Instagram", WooCommerce, BigCommerce, etc.) | Tiendas estándar, < ~50k SKUs, pocos recursos técnicos | Rápido, pero hereda decisiones de ID (variante vs producto) difíciles de cambiar; algunos usuarios reportan que el Content ID del feed sincronizado de Shopify no se puede sobrescribir. [EMPIRICAL, fuente comunidad] |
| Feed programado (URL XML/CSV/TSV/TXT, comprimido zip/gzip/bz2) | Control total del feed, feeds transformados con herramienta (DataFeedWatch, Channable, Productsup…) | Meta recomienda < 5 millones de productos por feed y el archivo por feed tiene límite de 100 MB; dividir feeds grandes acelera la subida. Se aceptan feeds de Google Merchant Center (quitar parámetros de tracking de Google del `link`). [OFFICIAL META] |
| Feed suplementario | Añadir columnas (vídeo, labels, overrides) sin tocar el feed principal | Un feed principal solo puede enlazar 1 suplementario; un suplementario puede servir a varios principales. Los vídeos del suplementario no se borran al reemplazar el principal. [OFFICIAL META] |
| Batch API (`/{catalog_id}/items_batch`) | Precio/stock que cambian más de una vez por hora; catálogos grandes; flash sales | Meta lo recomienda para actualizaciones más frecuentes que horarias. [OFFICIAL META] |
| Auto catalog (catálogo construido desde el pixel) | Casos concretos (p. ej. destino "On-Facebook") | El destino On-Facebook de catalog ads solo funciona con auto catalogs (doc actualizada nov-2025). [OFFICIAL META] |

**Regla:** si tu precio o stock cambian intradía (rebajas, drops, BFCM), un feed programado diario provoca *price mismatch* y anuncios de productos agotados. Pasa a Batch API o feed horario antes de temporada alta.

## 3. Campos: requisitos y límites vigentes

Fuente: referencia de campos de catálogo para e-commerce en developers.facebook.com (consultada 2026-10-15). [OFFICIAL META]

### Obligatorios (Ads y Commerce)

| Campo | Requisito |
|---|---|
| `id` | Único, ≤100 caracteres. Si hay IDs duplicados Meta **ignora todas las instancias**. |
| `title` | ≤200 caracteres; Meta recomienda ≤65. |
| `description` | ≤9.999 caracteres, texto plano, sin enlaces, no todo en mayúsculas. |
| `availability` | `in stock` / `out of stock` (los agotados dejan de servirse automáticamente). |
| `condition` | `new`, `refurbished`, `used`. |
| `price` | Número + ISO 4217 (`29.99 EUR`). |
| `link` | URL del dominio propio, http(s). |
| `image_link` | JPEG/PNG, ≥500×500 px, ≤8 MB. |
| `brand` | ≤100 caracteres. |
| `size` | Solo obligatorio para Shops y ciertas categorías (ropa, calzado). |

### Recomendados que de verdad importan

| Campo | Para qué sirve | Detalle |
|---|---|---|
| `sale_price` + `sale_price_effective_date` | Tachados y overlays de descuento | `sale_price` < `price`. Sin fecha, el precio rebajado permanece hasta que lo quites (riesgo post-rebajas). |
| `item_group_id` | Agrupar variantes | Mismo valor en todas las tallas/colores. |
| `additional_image_link` | Lifestyle, detalle, UGC | Hasta 20 URLs. |
| `video[0..19].url` | Catalog Product Video | Hasta 20 vídeos por producto, ≤200 MB, URL de descarga directa (no YouTube). |
| `internal_label` | Product sets dinámicos | Hasta 5.000 etiquetas/producto, 110 caracteres/etiqueta, en minúsculas; **sin revisión de políticas al cambiar**. Meta recomienda migrar de `custom_label` a `internal_label` para filtrar product sets. |
| `custom_label_0..4` | Segmentación legacy | 5 campos de texto, ≤100 caracteres. |
| `custom_number_0..4` | Valores numéricos para filtros (p. ej. margen %, stock, rating) | Enteros 0–4.294.967.295. |
| `google_product_category` / `fb_product_category` | Categorización | Lo más específica posible; desbloquea campos por categoría. |
| `product_type` | Taxonomía propia | ≤750 caracteres. |
| `status` | `active`/`archived` | Antes `visibility`. |
| `quantity_to_sell_on_facebook` | Inventario | Antes `inventory`. |
| `rich_text_description` | HTML en Shops | No se usa en anuncios; `description` sigue siendo obligatoria. |
| `gtin`, `mpn`, `color`, `gender`, `age_group`, `material`, `pattern`, `shipping`, `unit_price` | Atributos | `unit_price` es relevante en la UE para precio por unidad. |

**Renombres a tener en cuenta** (los nombres antiguos siguen aceptándose): `visibility` → `status`, `product_tags` → `internal_label`, `inventory` → `quantity_to_sell_on_facebook`. [OFFICIAL META]

## 4. Calidad del feed: los problemas que realmente cuestan dinero

### 4.1 Match rate (Pixel/CAPI ↔ catálogo)

Requisitos oficiales (FAQ de Advantage+ catalog ads y guía de dynamic product audiences): [OFFICIAL META]

- El ID enviado en `content_ids` debe coincidir **exactamente** con el `id` del feed.
- `content_type` debe ser `product` o `product_group` y coherente con el tipo de ID enviado.
- El pixel debe estar **asociado al catálogo** (y la app, si hay eventos de app: los app events no llevan catalog ID, hay que asociar app y pixel a cada catálogo).
- Para AddToCart y Purchase se deben usar IDs de producto (variante), no de grupo.
- Las exclusiones de audiencias dinámicas operan a nivel `item_group_id`: comprar otra variante del mismo grupo excluye a la persona.

Umbrales: Meta usa >90 % como objetivo y 70 % como mínimo en su documentación de Product Set Optimization (contexto retail media, pero es el único umbral numérico oficial localizado). [OFFICIAL META] Algunos vendors usan ≥75 % como mínimo operativo. [EMPIRICAL, vendor]

**Patrón Shopify** [EMPIRICAL]: hilos de la comunidad Shopify documentan match rates del 0–40 % porque la app nativa envía el ID de producto padre (`content_type: product_group`) mientras el catálogo usa ID de variante, o al revés. Arreglos posibles: (a) alinear el feed al nivel que envía el pixel (merge de variantes en herramienta de feed); (b) alinear el pixel/CAPI al ID del catálogo (tag manager o app de tracking). Verificar con Meta Pixel Helper + Commerce Manager → Eventos → "IDs no válidos".

### 4.2 Precio y disponibilidad

- *Price mismatch* feed ↔ landing es causa típica de rechazo y de pérdida de confianza (el usuario ve 29 € y aterriza en 34 €). Causas: caché del feed, precios por mercado, `sale_price` sin fecha de fin, impuestos incluidos/excluidos según país. [EMPIRICAL]
- Disponibilidad: el feed debe reflejar el estado real del botón "añadir al carrito". Los agotados se dejan de servir automáticamente si `availability = out of stock`. [OFFICIAL META]
- **Regla operativa:** en BFCM/rebajas, programa `sale_price_effective_date` con fecha de fin y aumenta la frecuencia de actualización.

### 4.3 Imágenes

- Mínimo 500×500; en la práctica, imágenes cuadradas o 4:5 de ≥1080 px. Meta aplica *Image touch-ups* (adaptación a 4:5 y 9:16 por recorte/relleno) **activado por defecto** en Advantage+ creative for catalog. [OFFICIAL META] Si tu packshot es blanco y pequeño, el relleno se ve barato: aporta imágenes nativas 4:5 y 9:16 (hay documentación de *multi-ratio images*).
- Texto excesivo en la imagen, marcas de agua o collages provocan rechazos o peor entrega. [EMPIRICAL]

### 4.4 Errores vs advertencias

Los errores fatales impiden subir el producto (el resto del feed sigue subiendo); las advertencias no bloquean pero reducen calidad. Tras cada subida revisa `product_count` y el panel de diagnóstico (también disponible vía Diagnostics API `/{catalog-id}/diagnostics`). Para vídeos existe `video_fetch_status` (Fetched, Fetch_failed, Partial_fetch, Outdated). [OFFICIAL META]

## 5. Variantes

[OFFICIAL META] (guía de variantes):

- Cada variante es su propia fila; no crear una fila "padre" vacía.
- `item_group_id` idéntico en todas las variantes; todos los campos de variante rellenos (`size`, `color`, `gender`, `pattern`; `additional_variant_attribute` para otros).
- Mantén el **título igual** entre variantes; cambia imagen y link según color.
- Patrón de ID claro (p. ej. `camiseta-S-rojo`).

Decisión de diseño: **¿anunciar a nivel variante o a nivel grupo?** Para moda con muchas tallas, mostrar 8 variantes de la misma prenda en un carrusel desperdicia slots. Las herramientas de feed permiten "merge" de variantes (una fila por color, por ejemplo). Elige un nivel y **alinea el pixel** a ese nivel. [STRONG INFERENCE]

## 6. Product sets: cómo segmentar sin fragmentar

### 6.1 Principio

El product set más grande "suele rendir mejor" porque da más opciones al sistema; segmenta solo con un motivo económico o de mensaje. [EMPIRICAL, vendor — Marpipe] Coherente con el principio general de consolidación para dar señal (Haus recomienda consolidar campañas, segmentando lower-funnel solo cuando haga falta para vigilar eficiencia). [EMPIRICAL]

### 6.2 Motivos legítimos para separar product sets

| Motivo | Ejemplo de filtro | Por qué |
|---|---|---|
| Margen | `custom_number_0` (margen %) ≥ 50 o `internal_label = margen_alto` | El sistema optimiza a revenue, no a margen: si el mix vendido se va a productos de margen bajo, ROAS "bueno" puede ser pérdida (ver `05-economia…`). |
| Ticket | precio < 30 € vs ≥ 30 € | Productos baratos inflan conversiones y bajan AOV por debajo del break-even de envío. |
| Stock | `quantity_to_sell_on_facebook` > N | Evita empujar SKUs que se agotan en 48 h. |
| Estacionalidad/campaña | `internal_label = bfcm2026` | Product sets por tentpole; CTC recomienda mapear cada lanzamiento y tentpole a un product set. [EMPIRICAL, agencia] |
| Novedades | fecha de alta reciente | Lanzamientos con poca señal histórica necesitan empuje. |
| Exclusiones | `internal_label = no_ads` | Productos con devolución alta, margen negativo o sin stock fiable. |

### 6.3 Product Set Optimization (beta)

Meta tiene en beta "product set optimization" para Retail Media Networks: optimizar rendimiento por marca/grupo de producto dentro de un catálogo, compatible con optimización omnicanal. Requiere aprobación de Meta y match rate ≥70 % (ideal >90 %). No es una función general para un DTC medio. [OFFICIAL META]

## 7. Creatividad dentro del catálogo

### 7.1 Funciones nativas de Advantage+ creative for catalog [OFFICIAL META]

| Función | Qué hace | Defecto |
|---|---|---|
| Format automation (carrusel/colección) | Meta elige formato por impresión | Opt-in |
| Collection cover media | Por defecto vídeo de catálogo generado por usuario; o imagen/vídeo propio | — |
| Image touch-ups (`adapt_to_placement`) | Adapta imágenes a 4:5 y 9:16 (recorte/relleno) | **Opt-in por defecto** |
| Allow product video / Dynamic Media (`media_type_automation`) | Mezcla imágenes y vídeos del catálogo | **Opt-in por defecto en API desde 1-sep-2025** |
| Dynamic partnership ads | Muestra partnership ads activos junto a ítems del catálogo en colección | Opt-in/out |
| Dynamic overlays (`add_text_overlay`) | Superpone info del catálogo (precio, descuento, envío) | Opt-in/out |
| Carousel descriptions con template tags | Hasta 3 descripciones con `{{product.price}}` etc. | — |
| End card de carrusel | On/off | — |

Fuera del catálogo, **Product extensions** ("Add catalog items") muestra productos del catálogo bajo un anuncio estático (imagen/vídeo) en campañas Sales o Traffic cuando Meta predice mejora; desde API v20 hay que declarar opt-in/opt-out explícito. [OFFICIAL META]

Otras funciones IA citadas por terceros en 2025-2026 (background generation para imágenes de producto; Casetify +13 % ROAS con fondos generados según un success story de Meta citado por terceros). [OFFICIAL META vía secundaria, no verificado directamente]

### 7.2 Overlays y frames de terceros

Herramientas (Confect, Hunch, Marpipe, Cropink, etc.) generan plantillas con precio, descuento, reseñas, logo, fondo de color, lifestyle. Evidencia:

- Confect afirma que sus catalog ads tuvieron **76 % mejor ROAS que anuncios "regulares"** (ene-2024–abr-2025, 1.040 M$ de inversión, 71 M compras). Comparación no controlada, de vendor y con sesgo de selección (los anunciantes que más usan catálogo bien montado no son aleatorios). [EMPIRICAL, vendor — baja-media confianza]
- Cropink reporta para Leroy Merlin Polonia (+99.000 productos, feed actualizado cada 2 h, tachados y señales promocionales) **+79 % ROAS interanual** (mar–jul 2025). Antes/después interanual, no controlado. [EMPIRICAL, vendor]
- No he encontrado en 2025-2026 un estudio independiente que aísle "overlay vs packshot limpio". [HYPOTHESIS] sobre magnitud.

**Cuándo suelen funcionar los overlays** [STRONG INFERENCE]: precio/descuento visible cuando el precio es ventaja competitiva; "envío gratis"/"devolución 30 días" cuando la fricción es logística; estrellas de reseñas cuando la categoría es de confianza. **Cuándo no**: marcas premium donde el overlay abarata, o cuando el overlay tapa el producto en 9:16.

**Nota de placement:** un recurso de terceros afirma que los dynamic overlays nativos solo se muestran en Facebook Feed y solo en imagen única/carrusel. [HYPOTHESIS — no verificado en doc oficial]

### 7.3 Vídeo de catálogo (CPV) y Dynamic Media

Hechos [OFFICIAL META]:

- 25-ago-2025: Meta anuncia que desde el **1-sep-2025** `media_type_automation` pasa a `OPT_IN` por defecto en Advantage+ catalog ads (imagen única, carrusel, colección) creados por API; según PPC Land, el opt-in se impone al 100 % desde el **20-oct-2025**. Se puede hacer opt-out con `OPT_OUT`.
- El sistema muestra imagen o vídeo según lo que prediga más eficaz; el ranking **sigue optimizando al objetivo de campaña** (no prioriza vídeo por ser vídeo).
- Meta solo descarga y revisa vídeos cuando hay un evento de pixel/app sobre ese producto o cuando el producto entra en recomendación → **los vídeos de productos sin tráfico no se procesan**.
- Ratios preferidos: 9:16 en Reels/Stories; 4:5 en feed (single/collection); carrusel 1:1 en Facebook Feed y 4:5 en Instagram Feed.
- No hay todavía breakdown de entrega imagen vs vídeo en reporting.
- Meta recomienda empezar apuntando a ~30 % de impresiones en vídeo; tabla de cobertura según tamaño del set (1–100 productos → ~20 % de cobertura; >50.000 → ~500 vídeos). Alternativa: un product set con 100 % de cobertura de vídeo en su propio ad set.
- `preferred_video_tags` permite indicar qué vídeo preferir.

Rendimiento: una cifra circulante ("+20 % conversiones por dólar con CPV") no la he podido trazar a un documento original de Meta. [HYPOTHESIS/no verificado]

**Implicación:** prioriza vídeo para los top 20–50 SKUs por revenue (que concentran la mayoría de impresiones). Formato: 6–15 s, producto en uso, 9:16 nativo y versión 4:5. [STRONG INFERENCE]

### 7.4 Vídeo generado desde imágenes (oct-2026)

En Advertising Week NY (6-oct-2026) Meta anunció como **GA** la generación de vídeo desde estáticos en Advantage+ creative y como **beta para anunciantes elegibles** la conversión de imágenes de producto del catálogo en vídeo de producto (Ads Manager y "product video creator" en Commerce Manager). [OFFICIAL META, vía Relevant Audience/AI Frontier Review] Riesgos: artefactos, representación incorrecta del producto (problema legal en cosmética/alimentación), coherencia de marca. Recomendación: activar en un product set de prueba y revisar muestras antes de escalar. [STRONG INFERENCE]

## 8. El feed como palanca de rendimiento (no solo de cumplimiento)

Palancas en orden de impacto esperado [STRONG INFERENCE, consistente con práctica de agencias de feed]:

1. **Precio competitivo y visible** (`sale_price` correcto, tachado).
2. **Imagen principal** que funcione en móvil: producto grande, fondo con contraste, 4:5.
3. **Imágenes adicionales y vídeo** (lifestyle, en uso, escala).
4. **Títulos**: tipo de producto + atributo diferencial + marca, ≤65 caracteres visibles. Con la llegada de checkout en agentes IA, títulos y atributos estructurados tienen valor adicional. [HYPOTHESIS]
5. **Etiquetas de negocio** (`internal_label`, `custom_number`) para margen, stock y estacionalidad.
6. **Exclusiones** (productos con devoluciones > X %, margen negativo, rotura de stock frecuente).

## Implicaciones operativas

- **Auditoría mínima antes de gastar en catálogo** (en este orden): (1) match rate por evento (ViewContent, AddToCart, Purchase) ≥ 90 %; (2) % de productos con errores < 2 %; (3) precio/stock feed = web en una muestra de 20 SKUs; (4) ≥ 3 imágenes por top SKU; (5) vídeo en top 20–50 SKUs; (6) `item_group_id` correcto; (7) etiquetas de margen.
- **Frecuencia de actualización:** diaria como mínimo; horaria o Batch API en promociones y si el stock rota rápido.
- **Product sets:** empieza con "todo el catálogo menos exclusiones"; añade sets por margen/tentpole solo si hay motivo económico.
- **Umbral de alarma:** match rate < 70 % → no lances retargeting dinámico hasta corregir; los catalog ads en prospección también sufren porque el sistema aprende peor qué productos convierten.

## Errores frecuentes

- Duplicar IDs en el feed (Meta descarta **todas** las instancias).
- Feed sincronizado de Shopify con IDs de variante y pixel con IDs de producto (o al revés).
- `sale_price` sin fecha de fin tras BFCM: sigues anunciando un descuento que ya no existe.
- Un solo packshot sobre blanco por producto en 2026 (se recorta/rellena mal a 9:16).
- Segmentar en 15 product sets por categoría sin motivo económico → ad sets sin señal.
- Subir vídeos a productos sin tráfico (no se procesan) y concluir que "el vídeo no funciona".
- Overlays que tapan el producto o cambian de precio en el feed más lento que la web.

## Preguntas abiertas

- Magnitud real de overlays vs imagen limpia: falta estudio independiente.
- Impacto medido del vídeo de catálogo (Meta no ofrece breakdown imagen/vídeo).
- Calidad y riesgo de la generación de vídeo desde imágenes de catálogo (beta oct-2026).
- Si los dynamic overlays nativos están limitados a Facebook Feed (afirmación de un tercero, no verificada).
- Peso real de títulos/atributos en checkout por agentes IA (Meta AI, Messenger) cuando salga de test.

## Fuentes clave

- [Catalog fields reference (e-commerce)](https://developers.facebook.com/docs/marketing-api/catalog/reference) — Meta for Developers, consultado 2026-10-15 — meta-developers
- [Advantage+ catalog ads FAQ](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-catalog-ads/faq.md) — Meta for Developers — meta-developers
- [Product-level video FAQ (Allow product video)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-catalog-ads/allow-product-video/faq.md) — Meta for Developers — meta-developers
- [Advantage+ creative for catalog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-creative-for-catalog.md) — Meta for Developers — meta-developers
- [Product variants](https://developers.facebook.com/documentation/ads-commerce/catalog/guides/product-variants.md) — Meta for Developers — meta-developers
- [Dynamic product audiences](https://developers.facebook.com/documentation/ads-commerce/marketing-api/audiences/guides/dynamic-product-audiences.md) — Meta for Developers — meta-developers
- [Product set optimization overview](https://developers.facebook.com/documentation/ads-commerce/marketing-api/product-set-optimization/product-set-optimization-overview.md) — Meta for Developers — meta-developers
- [Product extensions](https://developers.facebook.com/documentation/ads-commerce/marketing-api/advantage-catalog-ads/product-extensions) — Meta for Developers — meta-developers
- [Marketing API: upcoming change to Dynamic Media default opt-in](https://developers.facebook.com/blog/post/2025/08/25/marketing-api-upcoming-change-to-dynamic-media-default-opt-in/) — 2025-08-25 — meta-developers
- [Meta enables dynamic media by default for catalog ads](https://ppc.land/meta-enables-dynamic-media-by-default-for-catalog-ads-starting-september-2025/) — 2025 — prensa
- [Meta Advertising Week NY 2026 ad tools: live vs testing](https://www.relevantaudience.com/meta/meta-advertising-week-new-york-2026-ad-tools/) — 2026-10 — agencia
- [0 % catalog match rate (Shopify community)](https://community.shopify.com/t/0-catalog-match-rate-facebook-instagram-app-sends-parent-product-id-as-content-ids-but-catalog-uses-variant-id/653321) — 2025-2026 — comunidad
- [Confect by the numbers](https://confect.io/about-confect) — 2025 — vendor
- [Leroy Merlin Poland case (Cropink)](https://cropink.com/case-studies/leroy-merlin) — 2025 — vendor
- [The Complete Meta Advantage+ Catalog Ads Guide (Marpipe)](https://www.marpipe.com/blog/meta-advantage-catalog-ads) — 2024-11 — vendor
