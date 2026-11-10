# Casos e-commerce y apps con números (2023-2026)

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: casos publicados con datos (incrementalidad, catálogo, Advantage+, ventanas de atribución, omnicanal, web-to-app). Todos los casos son **publicados por un vendor o por Meta** (sesgo de selección: se publican los éxitos). Los campos que la fuente no da se marcan "no publicado". Ningún caso es auditado de forma independiente.

## TL;DR — lo que enseñan los casos en conjunto

- **La creatividad de arriba del embudo puede ser mucho más incremental que el retargeting "eficiente"** (Javvy: TOF >13× más incremental que BOF dentro de Advantage+ Shopping). [EMPIRICAL]
- **Los productos de ticket alto necesitan ventanas de lectura largas** (HexClad: el coste por adquisición incremental cayó 56–67 % al incluir 3 semanas post-test). [EMPIRICAL]
- **Meta mueve ventas fuera de la web** (Fresh Clean Threads: +23 % Amazon y +21 % DTC; Haus: ~32 % del impacto en omnicanal). Medir solo Shopify infravalora Meta en marcas omnicanal. [EMPIRICAL]
- **Las intuiciones sobre ventanas de optimización fallan** (Dr. Squatch: optimizar a 7d clic dio +6,51 % de revenue nuevo frente a 1d clic, al revés de lo que decían MTA y el equipo). [EMPIRICAL]
- **Lanzamientos y novedad recuperan incrementalidad en marcas saturadas** (Ridge: campaña de lanzamientos con iROAS > 4 $, 114 % sobre objetivo). [EMPIRICAL]
- **Upper-funnel bien medido aporta clientes nuevos con iROAS comparable** (Caraway: ~4 % del revenue de clientes nuevos; Mejuri: 11 % del revenue nuevo durante el test). [EMPIRICAL]
- **Catálogo: precio visible, marca y formatos nativos 9:16 mejoran resultados** según casos de vendors (Rock Luggage +35 % ROAS / −20 % CPA; Leroy Merlin Polonia +79 % ROAS interanual), pero sin aislar variables. [EMPIRICAL, vendor — baja-media]
- **Mover presupuesto a canales "de vista" por recomendación de un MMM correlacional salió caro** (OluKai: CAC 20 % por encima de lo previsto; al volver a Meta, CAC −20 %). [EMPIRICAL]

---

## Caso 1 — Javvy Coffee: TOF vs BOF dentro de Advantage+ Shopping

| Campo | Detalle |
|---|---|
| Fuente | Haus, customer story, 4-nov-2024 — vendor |
| Starting point | Dos campañas Advantage+ Shopping con presupuesto 50/50: TOF (vídeo problema-solución) y BOF (estáticos, packshots, testimonios, banners promo). |
| Mercado | EE. UU. (Shopify + Amazon) |
| Presupuesto | No publicado |
| Oferta | Café líquido concentrado; no publicada la oferta |
| Diseño | Dos geo-lift secuenciales (no simultáneos), cada uno 2 semanas + 1 semana post-tratamiento, con holdout. KPI: pedidos nuevos en Shopify; secundario: pedidos nuevos en Amazon (derivados por Haus). |
| Resultado | TOF >13× más incremental que BOF; TOF generó lift en Shopify y Amazon. CPIA de TOF 20 % menor que lo reportado por MTA de clic; CPIA de BOF **250 % mayor** que lo reportado. |
| Cambio | Mayoría del presupuesto de Meta a TOF; CAC y MER mejoraron "inmediatamente" (sin cifras). |
| Limitaciones | Tests en momentos distintos; ventanas cortas; cifras absolutas solo en imagen; publicado por el vendor. |
| Lección | El ROAS/CPA atribuido de BOF/retargeting puede ser la métrica más engañosa de la cuenta. Testear antes de "escalar lo eficiente". |

## Caso 2 — HexClad: producto caro, ventana post-test

| Campo | Detalle |
|---|---|
| Fuente | Haus, 17-jun-2024 — vendor |
| Starting point | Cookware premium; set de 12 piezas a 699,99 $; ciclo de consideración largo; fuerte inversión en Meta; ventas en Shopify y Amazon. |
| Mercado | EE. UU. |
| Presupuesto | No publicado (celda BAU vs celda escalada) |
| Diseño | Geo-lift de 3 celdas: A BAU (45 % de EE. UU.), B gasto escalado (45 %), C control sin Meta (10 %). 2 semanas + 3 semanas post-tratamiento. KPI: pedidos nuevos y revenue en Shopify y Amazon. |
| Resultado | Ambas celdas superaron al control; CPIA alto durante las 2 semanas; al incluir las 3 semanas post-test el CPIA bajó **56 % (BAU) y 67 % (escalado)**. |
| Cambio | Optimizar mix contra revenue total (Shopify + Amazon); vigilar efectos retardados. |
| Limitaciones | Sin valores absolutos; caso de 2024. |
| Lección | En tickets altos, juzgar a 7 días subestima Meta; el escalado no fue peor que BAU en coste incremental cuando se mide completo. |

## Caso 3 — Fresh Clean Threads: halo en Amazon

| Campo | Detalle |
|---|---|
| Fuente | Haus, 30-abr-2024 — vendor |
| Starting point | Camisetas premium DTC + Amazon; conocían el efecto de Meta en DTC, no en Amazon. |
| Diseño | Geo-lift, holdout 10 %, 3 semanas. KPI principal: pedidos Amazon. |
| Resultado | **+23 % ventas Amazon, +21 % ventas DTC**; iROAS total +14 % al incluir omnicanal. |
| Cambio | Meta como palanca para escalar Amazon; alineación con dirección. |
| Limitaciones | Sin iROAS absoluto ni intervalos; un solo test. |
| Lección | En marcas con marketplace, el break-even de Meta debe calcularse sobre ventas totales (Haus: break-even DTC iROAS 0,68× en omnicanales). |

## Caso 4 — Dr. Squatch: 1-day click vs 7-day click

| Campo | Detalle |
|---|---|
| Fuente | Haus, 22-may-2025 — vendor |
| Starting point | Marca de cuidado personal masculino (Unilever); MTA (Northbeam) e intuición apuntaban a optimizar a 1DC. |
| Diseño | Geo-test de 2 celdas sin holdout: 80 % EE. UU. con 1DC (BAU) vs 20 % con campañas duplicadas a 7DC; 2 semanas + 1 semana post. KPI: revenue nuevo. |
| Resultado | **7DC +6,51 % de revenue nuevo** frente a 1DC; también mejor en revenue total y pedidos DTC (sin cifras). |
| Cambio | Reconstruir la cuenta a 7DC; recalibrar el MTA con un nuevo factor de incrementalidad. |
| Limitaciones | Celdas desiguales; sin significación; ambiguo si es relativo o puntos. |
| Lección | La ventana de optimización es una decisión empírica; no la deduzcas de MTA. Relevante tras los cambios de ventanas de 2026. |

## Caso 5 — Ridge: lanzamientos para recuperar incrementalidad

| Campo | Detalle |
|---|---|
| Fuente | Haus, 5-ago-2025 — vendor |
| Starting point | Marca de carteras saturada en su categoría; incrementalidad de Meta en descenso. |
| Diseño | Fase 1: añadir upper-funnel (lift notable, sin cifra). Fase 2: campaña centrada en lanzamientos (inspirada por anuncios del Año Nuevo Lunar); test de 2 celdas con holdout, 3 semanas. KPI: ventas de carteras EDC. |
| Resultado | **iROAS > 4 $, 114 % sobre objetivo.** |
| Cambio | Más gasto en lanzamientos; lanzamientos como herramienta de merchandising y de medios. |
| Limitaciones | Objetivo no publicado; fases no separadas. |
| Lección | La novedad (producto/creatividad) es una fuente de incrementalidad en cuentas maduras; planifica el calendario de lanzamientos con la cuenta. |

## Caso 6 — Caraway: upper-funnel optimizado a visitas

| Campo | Detalle |
|---|---|
| Fuente | Haus, 15-dic-2023 — vendor |
| Starting point | Cookware DTC que se expandió a Amazon y Target; nunca había comprado Meta no optimizado a conversión. |
| Diseño | Geo-lift 50/50; campaña adicional optimizada a visitas al sitio; duración no publicada. KPI: ventas/revenue. |
| Resultado | ~**4 % del revenue de clientes nuevos** durante el test; iROAS "comparable" a canales de performance (sin cifra). |
| Cambio | Upper-funnel en Meta pasó a ser evergreen. |
| Limitaciones | Sin duración ni iROAS numérico. |
| Lección | Con medición, una pequeña parte del presupuesto en upper-funnel puede aportar clientes nuevos a coste comparable (coherente con Haus 2025: 81 % de impacto en nuevos). |

## Caso 7 — OluKai: el coste de seguir un MMM correlacional

| Campo | Detalle |
|---|---|
| Fuente | Haus, 15-ene-2026 — vendor |
| Starting point | Calzado premium; un MMM anterior recomendó canales de vista (TikTok, Snap, YouTube) antes de Q4; se recortó Meta → CAC ~20 % por encima de lo previsto. |
| Cambio | MMM causal calibrado con experimentos: ~50 % del gasto de canales de vista pasó a Meta y el gasto total bajó ~15 % antes del pico. |
| Resultado | **CAC −20 %** poco después; previsiones de pedidos y CAC alineadas con la realidad. |
| Limitaciones | Cambios simultáneos (no separables); cifras aproximadas. |
| Lección | Las decisiones de mix deben calibrarse con experimentos, no solo con correlaciones; Meta salió más incremental que TikTok/Snap en sus geo-lifts. |

## Caso 8 — Sephora US: creadores + catálogo + Advantage+ audience

| Campo | Detalle |
|---|---|
| Fuente | Meta success story (citada por Cropink), ago–sep 2025 — meta-oficial vía secundaria |
| Diseño | Partnership ads con creadores + Advantage+ catalog ads + Advantage+ audience en Feed/Stories/Reels de Instagram; medición omnicanal (online, tienda, app); lift study de Meta. |
| Resultado | **1,56× ROAS incremental omnicanal**; 1,04× ROAS en tienda física; +3 % de alcance incremental vs campañas omnicanal habituales. |
| Limitaciones | Página original con login; métricas de Meta sobre su propio producto. |
| Lección | Mezclar contenido de creadores con catálogo y medir omnicanal es el patrón de retailers grandes. |

## Caso 9 — Cruise Critic: catálogo optimizado a valor

| Campo | Detalle |
|---|---|
| Fuente | Meta success story (citada por Cropink) — meta-oficial vía secundaria; fecha no publicada |
| Diseño | Advantage+ catalog ads optimizados a valor de compra vs a volumen de conversiones; Advantage+ placements y presupuesto. |
| Resultado | **+22 % de ROAS incremental** frente a optimización por volumen. |
| Limitaciones | Fecha y mercado no publicados. |
| Lección | Con valores de pedido muy dispersos, la optimización a valor puede ser más incremental. |

## Caso 10 — Rock Luggage (Incubeta): plantillas de catálogo con marca y precio

| Campo | Detalle |
|---|---|
| Fuente | Confect, 7-nov-2025 — vendor |
| Starting point | Catalog ads con packshots en blanco, estética inconsistente con marca premium, mal 9:16. |
| Mercado | Probablemente Reino Unido (precios en £) |
| Cambio | Plantillas con logo, tipografía, colores, USPs, reseñas; versiones 9:16; precio visible vs no; franja roja en rebajas; campañas temáticas ligadas a TV (Love Island, Big Brother). Tests A/B en 3 fases con variante blanca de control. |
| Resultado | **ROAS +35 %, CPA −20 %** (base ambigua: plantilla estándar vs blanca). Mostrar precio mejoró resultados. |
| Limitaciones | Sin gasto, duración ni significación; variables no aisladas. |
| Lección | Precio visible + formatos nativos de placement son las mejoras de catálogo con más soporte anecdótico. |

## Caso 11 — Leroy Merlin Polonia: feed enriquecido

| Campo | Detalle |
|---|---|
| Fuente | Cropink (vendor), mar–jul 2025 |
| Escala | > 99.000 productos; feed actualizado cada 2 h; tachados y señales promocionales en creatividad |
| Resultado | **+79 % ROAS interanual**; CVR +353 % en el primer mes completo; ROAS de julio +514 % interanual. |
| Limitaciones | Comparación interanual (estacionalidad, precios, cambios de cuenta); vendor. |
| Lección | En catálogos enormes, frescura del feed y precio visible importan; las magnitudes del vendor no son extrapolables. |

## Caso 12 — Blinkist: separar web y app

| Campo | Detalle |
|---|---|
| Fuente | RevenueCat, entrevista a Marcus Burke, 8-abr-2025 — practitioner |
| Diseño | Campañas web (web-to-app) en cuenta publicitaria separada de las de app; anuncios editoriales que llevaban a un artículo y luego a la App Store. |
| Resultado | Las campañas web entregaban ~80 % de impresiones en Facebook Feed, con público mayor y más dispuesto a pagar. Sin cifras de CAC. |
| Lección | Web-to-app abre audiencias distintas; separa medición y presupuesto. |

## Caso 13 — Casetify: fondos generados por IA en imágenes de producto

| Campo | Detalle |
|---|---|
| Fuente | Meta for Business (2025), citado por terceros — meta-oficial vía secundaria |
| Resultado | **+13 % ROAS** con generación de fondos IA en anuncios de producto. |
| Limitaciones | No he podido acceder a la página original (login). |
| Lección | Las mejoras creativas IA de Meta pueden aportar, pero conviene testearlas con control. |

---

## Plantilla para documentar casos propios (recomendada)

| Campo | Contenido mínimo |
|---|---|
| Starting point | Gasto diario, CPA/ROAS de plataforma, MER, nCAC, % nuevos, CM2 % |
| Presupuesto | Antes/después y duración |
| Mercado | País(es), idioma, IVA y location fee aplicable |
| Oferta | Precio, descuento, bundle, envío |
| Arquitectura | Campañas, ad sets, evento, puja, exclusiones de clientes |
| Creativo | Conceptos, formatos, número de anuncios nuevos/semana |
| Cambio | Una variable principal (si son varias, decláralo) |
| Resultado | Métrica de negocio (CM3, nCAC, clientes nuevos) + métrica de plataforma |
| Medición | Atribución usada; test de incrementalidad sí/no |
| Limitaciones | Estacionalidad, cambios simultáneos, tamaño de muestra |

## Implicaciones operativas

- Usa estos casos como **hipótesis a testear**, no como benchmarks.
- Los patrones más robustos (aparecen en varios casos independientes del mismo método): sobrevaloración de BOF/retargeting, efectos retardados en tickets altos, halo omnicanal, valor de la novedad.
- Documenta los casos propios con la plantilla para construir evidencia interna.

## Preguntas abiertas

- Faltan casos públicos europeos (España) con números completos de margen y nCAC.
- Faltan casos con fracasos documentados de Advantage+ sales (más allá de agregados de Haus).
- Faltan casos de suscripción e-commerce con cohortes por oferta de entrada.

## Fuentes clave

- [Haus — Javvy](https://www.haus.io/customer/javvy) — 2024-11-04 — vendor
- [Haus — HexClad](https://www.haus.io/customer/hexclad) — 2024-06-17 — vendor
- [Haus — Fresh Clean Threads](https://www.haus.io/customer/fresh-clean-threads) — 2024-04-30 — vendor
- [Haus — Dr. Squatch](https://www.haus.io/customer/dr-squatch) — 2025-05-22 — vendor
- [Haus — Ridge](https://www.haus.io/customer/ridge) — 2025-08-05 — vendor
- [Haus — Caraway](https://www.haus.io/customer/caraway) — 2023-12-15 — vendor
- [Haus — OluKai](https://www.haus.io/customer/olukai) — 2026-01-15 — vendor
- [Optimizing Meta Ads: A Playbook for Brands (Haus; Mejuri)](https://www.haus.io/blog/optimizing-meta-ads-a-playbook-for-brands) — 2025-08-15 — vendor
- [Facebook Advertising Case Studies (Sephora US, Cruise Critic, Leroy Merlin)](https://cropink.com/meta-ads-examples) — 2025-2026 — vendor (cita Meta)
- [Confect — Incubeta & Rock Luggage](https://confect.io/cases/how-incubeta-and-rock-luggage-increased-roas-by-35-with-confect) — 2025-11-07 — vendor
- [RevenueCat — Meta Ads in 2025 (Blinkist)](https://www.revenuecat.com/blog/growth/meta-ads-in-2025-tips-for-apps) — 2025-04-08 — practitioner
