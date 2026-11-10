# Playbook: productos de consumo (CPG/FMCG y bienes de consumo omnicanal) en Meta Ads

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: marcas de consumo de ticket bajo-medio y compra frecuente (alimentación, bebidas, higiene, belleza masiva, mascotas, hogar) que venden sobre todo en retail físico, marketplaces (Amazon) y quick commerce, con DTC pequeño o inexistente. Para DTC puro ver `playbook-ecommerce-dtc.md`.

## TL;DR

- **El error número uno es juzgar Meta por el ROAS de la web propia.** En marcas omnicanal, Haus encontró que ~32 % del impacto de Meta cae fuera de DTC y que el break-even de iROAS DTC es ~0,68×; Fresh Clean Threads midió +23 % en Amazon y +21 % en DTC. [EMPIRICAL]
- **Meta en consumo = alcance eficiente + ventas incrementales en todos los canales**, medido con geo-lift/Conversion Lift con datos de ventas totales (retail, Amazon, DTC) y MMM calibrado con experimentos (OluKai: un MMM correlacional llevó a CAC +20 %; el causal lo revirtió). [EMPIRICAL]
- **Upper/mid-funnel tiene más sentido aquí que en DTC puro**: en Haus, upper-funnel tuvo −46 % de iROAS DTC pero +138 % de halo omnicanal y 81 % de impacto en nuevos; mid-funnel +70 % de halo. Con KPI omnicanal, un 39 % menos de iROAS DTC empata con campañas de conversión. [EMPIRICAL]
- **Herramientas específicas**: Collaborative Ads (CPAS) con catálogos de retailers/marketplaces (activo en 2025-2026, p. ej. quick commerce en India), optimización omnicanal (online + tienda), Advantage+ catalog ads de retailer y, para la parte DTC, packs/bundles/suscripción. [OFFICIAL META] (CPAS, omnicanal) + [EMPIRICAL]
- **La economía se calcula en contribución por canal**, no en "ventas de lineal": un iROAS de 4 sobre precio de lineal puede ser solo break-even en margen de la marca (ejemplo §8). [STRONG INFERENCE]

## 1. Cuándo usar Meta

| Sí | Con cautela / no |
|---|---|
| Lanzamientos de producto (novedad = incrementalidad, como Ridge) | Producto commodity sin diferenciación visible |
| Categorías con decisión en el lineal influida por saliencia (snacks, bebidas, cosmética) | Distribución débil (el anuncio genera demanda que no encuentra producto) |
| Marcas con presencia en Amazon/quick commerce medible | Sin acceso a datos de ventas por región (no se puede medir geo-lift) |
| Ocasiones de consumo/estacionalidad clara | Presupuestos < ~€1.000/día sin DTC: difícil medir nada |
| DTC como canal de packs, suscripción, ediciones limitadas | Pretender que el DTC de un CPG sea rentable en primer pedido con AOV < 25 € |

## 2. Arquitectura por presupuesto

| Presupuesto/día | Enfoque | Estructura | Medición |
|---|---|---|---|
| **€100** | Solo DTC de packs/suscripción o lanzamiento local | 1 campaña Ventas Advantage+ a Purchase (pack de prueba) | MER/nCAC DTC; no hay potencia estadística para omnicanal |
| **€500** | DTC + tráfico a marketplace con medición (p. ej. Amazon Attribution) | Ventas DTC (70 %) + campaña a marketplace (30 %) con UTM/etiquetas; Collaborative Ads si el retailer lo ofrece | DTC en tienda; marketplace con su herramienta de atribución; pre/post por región si es posible |
| **€5.000** | Omnicanal medido | Advantage+ sales DTC + Collaborative Ads con retailers clave + campaña de alcance/vídeo (5–15 %) para lanzamientos/ocasiones | Geo-lift con ventas totales (retail + Amazon + DTC) 2×/año; Brand Lift en lanzamientos |
| **€50.000** | Full-funnel por ocasiones y mercados | Portafolio: alcance/vídeo (Reach/ThruPlay), mid-funnel, conversión DTC y retail, CPAS por retailer; calendario de lanzamientos | MMM causal calibrado con geo-lifts trimestrales; Conversion Lift con datos offline |

## 3. Evento de optimización

| Objetivo | Evento | Comentario |
|---|---|---|
| Ventas DTC | Purchase con valor | Packs/bundles para AOV ≥ 30–40 € |
| Ventas en retailer online (CPAS) | Eventos del retailer (vía su pixel/catálogo compartido) | Depende del acuerdo con el retailer |
| Ventas en tienda física | Optimización omnicanal / conversiones offline (si disponible y con datos de ventas cargados) | Requiere datos de tienda; verificar elegibilidad |
| Marca/lanzamiento | Alcance, ThruPlay, Landing page views | Juzgar con geo-lift/Brand Lift, no con CPA |
| Mid-funnel | ViewContent / AddToCart | Haus: más nuevos y más halo; menos iROAS DTC |

## 4. Creatividades

- **Activos de marca distintivos** desde el primer segundo (envase, color, logo): la venta ocurre lejos del anuncio, la memoria es el puente. [STRONG INFERENCE]
- **Ocasión y uso** (desayuno, gimnasio, fiesta), no especificaciones.
- **Formatos cortos 6–15 s 9:16**, con versión 4:5; subtítulos.
- **Creadores** para prueba social y recetas/rutinas; partnership ads.
- **Novedad**: sabores, ediciones limitadas, colaboraciones — principal fuente de incrementalidad en marcas maduras (Ridge). [EMPIRICAL]
- **"Dónde comprar"**: retailer/marketplace visible cuando la venta es en retail.

## 5. Funnel

Anuncio (ocasión/novedad) → (a) **retailer/marketplace** (CPAS, store locator, Amazon con etiquetado de atribución) o (b) **DTC** (pack de prueba, suscripción, edición limitada) → recompra en el canal habitual del consumidor (lineal), que Meta no verá directamente → por eso la medición es por experimento.

## 6. Métricas y umbrales

| Métrica | Uso | Regla |
|---|---|---|
| iROAS total (todas las ventas) en contribución | Decisión de presupuesto | ≥ 1 sobre contribución de la marca (no sobre precio de lineal) |
| iROAS DTC | Diagnóstico | Puede ser < 1 y aun así rentable en total (Haus: break-even DTC 0,68× en omnicanales) |
| Coste por unidad incremental | Comparar con margen unitario de la marca | Unidades incrementales × margen ≥ gasto |
| Alcance y frecuencia en público objetivo | Lanzamientos | Frecuencia efectiva semanal acordada con el equipo de marca |
| Brand Lift (recuerdo, consideración) | Lanzamientos | Usar para creatividad, no para presupuesto |
| nCAC DTC | Parte DTC | Igual que en DTC (`05-…`) |

## 7. Errores frecuentes

- Recortar Meta porque "el ROAS de la web es 1,2" sin medir Amazon/retail.
- Mandar tráfico a Amazon sin etiquetado de atribución.
- Sobreinvertir en retargeting de visitantes de la web (pequeña y poco incremental) en vez de alcance cualificado.
- Calcular iROAS sobre precio de lineal en vez de sobre ingresos y margen de la marca.
- Seguir un MMM no calibrado (OluKai).
- Lanzar campañas donde la distribución es débil.

## 8. Ejemplo numérico completo

**Marca de snacks saludables**, España. Ventas: 60 % retail, 25 % Amazon, 15 % DTC. Gasto Meta: 30.000 €/mes.

1. **Lectura ingenua**: Meta atribuye 45.000 € de ventas DTC → ROAS 1,5. Con CM2 DTC del 40 %: 18.000 € de contribución vs 30.000 € de gasto → "pierde 12.000 €/mes".
2. **Geo-lift (holdout 20 % de provincias, 4 semanas + 2 post)** con datos de ventas totales: ventas incrementales por mes ≈ 30.000 € DTC + 30.000 € Amazon + 60.000 € en lineal (precio de venta al público). iROAS "de lineal" = 120.000 / 30.000 = **4,0**.
3. **En contribución de la marca**:
   - DTC: 30.000 × 40 % = 12.000 €.
   - Amazon: 30.000 × 25 % (tras comisiones y logística FBA) = 7.500 €.
   - Retail: la marca ingresa ~55 % del PVP → 33.000 € × 35 % de margen = 11.550 €.
   - **Total: 31.050 €** vs 30.000 € de gasto + 3 % de location fee (900 €) = 30.900 € → **≈ break-even** (+150 €).
4. **Decisión**: Meta no "pierde 12.000 €" (lectura DTC) ni "gana 4×" (lectura de lineal): está en break-even en contribución el primer mes. Si el lift persiste en las 2 semanas post-test y hay recompra en lineal (no medida), es rentable; el siguiente paso es mejorar creatividad/novedad y testear upper-funnel con KPI omnicanal.
5. **Palancas**: subir AOV DTC (packs 6–12 uds.), priorizar regiones con distribución alta, campañas de lanzamiento con iROAS medido.

## Fuentes clave

- [The Meta Report (Haus) — omnicanal, upper/mid-funnel](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Optimizing Meta Ads: A Playbook for Brands (Haus)](https://www.haus.io/blog/optimizing-meta-ads-a-playbook-for-brands) — 2025-08-15 — vendor
- [Haus — Fresh Clean Threads](https://www.haus.io/customer/fresh-clean-threads) — 2024-04-30 — vendor
- [Haus — Ridge](https://www.haus.io/customer/ridge) — 2025-08-05 — vendor
- [Haus — OluKai](https://www.haus.io/customer/olukai) — 2026-01-15 — vendor
- [Haus — Caraway](https://www.haus.io/customer/caraway) — 2023-12-15 — vendor
- [How Meta's Collaborative Ads Are Fueling Quick Commerce Boom In India](https://about.fb.com/news/2025/12/how-metas-collaborative-ads-are-fueling-quick-commerce-boom-in-india/) — 2025-12 — meta-oficial
- [Product set optimization (compatible con optimización omnicanal)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/product-set-optimization/product-set-optimization-overview.md) — Meta for Developers — meta-developers
- [Meta location fees](https://www.storyboard18.com/digital/meta-to-charge-advertisers-2-5-location-fee-in-select-countries-to-offset-digital-service-taxes-91778.htm) — 2026 — prensa
