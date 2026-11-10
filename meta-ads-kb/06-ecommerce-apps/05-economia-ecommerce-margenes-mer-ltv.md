# Economía e-commerce para Meta Ads: márgenes, MER, ROAS break-even, nCAC, LTV y payback

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: las cuentas que convierten "ROAS de Ads Manager" en beneficio o pérdida. Fórmulas, convenciones y ejemplos numéricos completos. Bidding/escalado: carpeta 09; medición/incrementalidad: carpeta 04 (otros agentes).

## TL;DR

- **Revenue no es profit.** El único número que paga nóminas es el margen de contribución después de marketing (CM3). El ROAS de plataforma es un indicador de diagnóstico con tres sesgos: incluye ingresos no incrementales, suele incluir IVA/envío y no descuenta devoluciones ni costes variables. [STRONG INFERENCE] — coherente con CTC: "ROAS alone says nothing about profitability".
- **ROAS break-even = (1 + costes que escalan con la inversión) / CM2 %**, donde CM2 % se calcula **sobre la misma base de revenue que reporta Meta** (con o sin IVA, con o sin envío). Si te equivocas de base, te equivocas de break-even en un 20–30 %. [STRONG INFERENCE — derivación algebraica abajo]
- **CPA/nCAC break-even del primer pedido = CM2 por pedido / (1 + agencia % + fees %)**; el nCAC objetivo con recompra = CM2 del primer pedido + CM2 esperado de recompras dentro del payback aceptado. [STRONG INFERENCE]
- **Ajusta siempre por incrementalidad**: ROAS de plataforma exigido = ROAS break-even / factor de incrementalidad (IF). Con IF 0,7, un break-even de 2,7 exige 3,9 en Ads Manager. Haus encontró de media que Meta *infrarreporta* un 15 % en atribución 7d clic para DTC puro, pero el factor varía mucho por campaña (retargeting/BOF suele sobrerreportar). [EMPIRICAL] + [STRONG INFERENCE]
- **MER (revenue total / inversión total en marketing) es la métrica de control del negocio; aMER o nCAC, la de adquisición.** MER break-even = 1 / CM2 % (con la misma base). [EMPIRICAL — convención extendida entre operadores DTC]
- **España/UE 2026: dos costes que muchos olvidan**: IVA dentro del valor de compra (21 % en España → el 17,4 % del valor reportado no es tuyo) y el *location fee* de Meta del 3 % en España/Francia/Italia (2 % UK, 5 % Austria/Turquía) desde el 1-jul-2026. [OFFICIAL META vía prensa] (fee)
- **LTV se modela por cohortes y en margen, no en revenue**; payback = mes en que el CM2 acumulado por cliente ≥ nCAC. LTV:CAC 3:1 es una heurística de SaaS que en e-commerce solo tiene sentido con horizonte y coste de capital explícitos. [CONTESTED]
- **Devoluciones**: el NRF estimó para 2025 que se devuelve el 19,3 % del valor de las ventas online (15,8 % del total retail); en moda online el porcentaje suele ser mayor. Un ROAS de 3,5 en moda con 30 % de devoluciones puede ser pérdida. [EMPIRICAL vía secundaria] + ejemplo numérico abajo.

## 1. Definiciones (convención de esta KB)

Las agencias y vendors usan variaciones; esta es la que usaremos en toda la base. **Indica siempre la base** (con/sin IVA, con/sin envío).

| Término | Definición |
|---|---|
| **Ventas brutas (GMV)** | Lo que paga el cliente, IVA incluido, antes de devoluciones |
| **Revenue neto** | Ventas brutas − IVA − descuentos − devoluciones (± envío cobrado, según criterio) |
| **AOV** | Revenue (indicar base) / nº de pedidos |
| **COGS** | Coste del producto vendido (fabricación/compra + aranceles + flete de entrada) |
| **CM1** | Revenue neto − COGS (margen de producto) |
| **CM2** | CM1 − costes variables de fulfilment: envío de salida, pick & pack, packaging, comisiones de pago, coste logístico de devoluciones, comisiones de marketplace, apps por pedido. **Es el margen disponible para marketing.** (8x lo define igual: "CM2 es la capa antes de marketing") |
| **CM3** | CM2 − marketing variable: inversión publicitaria, fees de agencia, location fees, producción creativa, comisiones de afiliados/creadores |
| **EBITDA** | CM3 − costes fijos (equipo, software, oficina) |
| **MER** | Revenue total (todas las fuentes) / inversión total en marketing |
| **aMER** | Revenue de clientes nuevos / inversión total en marketing (concepto popularizado por operadores DTC; útil para medir adquisición) |
| **ROAS de plataforma** | Valor de conversión atribuido por Meta / gasto en Meta |
| **Blended ROAS** | A menudo sinónimo de MER; aquí: revenue total / gasto en ads (sin agencia ni creativo) |
| **nCAC** | Gasto de adquisición / clientes nuevos (ver `04-…`) |
| **LTV (contribución)** | CM2 acumulado por cliente de una cohorte en un horizonte (6, 12, 24 meses) |
| **Payback** | Meses hasta que CM2 acumulado por cliente ≥ nCAC |

## 2. Derivación del ROAS break-even

Sea:
- R = revenue que reporta Meta (con la base que use tu pixel/CAPI).
- c = CM2 como fracción de R (misma base).
- S = gasto en Meta.
- f = costes que escalan con el gasto, como fracción de S (fee de agencia % sobre gasto, location fee, coste creativo prorrateado).

Contribución tras marketing: CM3 = c·R − S·(1 + f).

- **Break-even** (CM3 = 0): R/S = **(1 + f) / c**.
- **ROAS objetivo para un margen m sobre R**: c·R − S(1+f) = m·R → R/S = **(1 + f) / (c − m)**.
- **CPA break-even** (por pedido de valor medio A): S/pedido = **c·A / (1 + f)**.
- **Ajuste por incrementalidad**: si solo una fracción IF de lo atribuido es incremental, ROAS de plataforma exigido = **(1 + f) / (c · IF)**.

## 3. Ejemplo A — Cosmética DTC en España (primer pedido)

Supuestos por pedido (ilustrativos pero realistas):

| Concepto | Valor |
|---|---|
| Pagado por el cliente (IVA 21 % incluido, tras descuento, envío gratis) | 48,40 € |
| Valor que recibe Meta (pixel/CAPI envía total con IVA) | 48,40 € |
| Revenue sin IVA | 40,00 € |
| Devoluciones (3 % del revenue) | −1,20 € |
| **Revenue neto** | **38,80 €** |
| COGS (25 % de 40 €; devoluciones de cosmética no revendibles) | −10,00 € |
| **CM1** | **28,80 €** |
| Envío salida 4,20 + pick & pack 0,90 + packaging 0,40 | −5,50 € |
| Pago (1,5 % de 48,40 + 0,25 €) | −0,98 € |
| Apps/otros por pedido | −0,30 € |
| **CM2** | **22,02 €** |

- CM2 % sobre el valor que ve Meta: 22,02 / 48,40 = **45,5 %**.
- ROAS break-even "desnudo" = 1 / 0,455 = **2,20**.
- Con agencia 10 % del gasto + location fee España 3 % + creativo prorrateado 10 % del gasto → f = 0,23 → ROAS break-even = 1,23 / 0,455 = **2,70**.
- CPA break-even (primer pedido) = 22,02 / 1,23 = **17,90 €** de gasto en Meta por pedido.
- Si un lift test indica IF = 0,7 para esa campaña → ROAS de plataforma exigido = 2,70 / 0,7 = **3,86**.
- Para ganar un 10 % de CM3 sobre ventas brutas (m = 0,10): ROAS = 1,23 / (0,455 − 0,10) = **3,46** (antes de ajuste por incrementalidad).

**Conclusión:** un ROAS de 3,0 en Ads Manager parece "bueno" y en esta marca puede ser pérdida en el primer pedido una vez descontados IVA, costes variables, agencia, fee y no-incrementalidad.

**Error típico:** calcular break-even como 1 / margen bruto de producto (1 / 75 % = 1,33). Ignora IVA, envío, pago, devoluciones y marketing variable: error de ×2.

## 4. Ejemplo B — Moda con devoluciones altas

| Concepto | Valor |
|---|---|
| Pagado (IVA incl.) y valor reportado a Meta | 90,00 € |
| Sin IVA | 74,38 € |
| Devoluciones 30 % del valor | −22,31 € |
| **Revenue neto** | **52,07 €** |
| COGS 30 % sobre lo que se queda el cliente (lo devuelto se revende) | −15,62 € |
| Envío salida | −6,00 € |
| Logística inversa (30 % de pedidos con devolución × 7 €) | −2,10 € |
| Pago (1,5 % × 90 + 0,25) | −1,60 € |
| **CM2** | **26,75 €** |

- CM2 % sobre valor reportado = 26,75 / 90 = **29,7 %**.
- Break-even desnudo = **3,36**; con f = 0,23 → **4,14**.
- Un ROAS de plataforma de 3,5 → **pérdida** en primer pedido (y Meta cuenta el pedido completo aunque luego se devuelva parte).

Palancas: reducir devoluciones (guía de tallas, fotos realistas, vídeo en catálogo), excluir de los product sets SKUs con devolución > 40 %, enviar a Meta el valor neto esperado (valor × (1 − tasa de devolución por categoría)) en vez del bruto, o subir AOV con bundles. [STRONG INFERENCE]

## 5. Cuándo un buen ROAS de Ads Manager significa pérdidas (checklist)

| Mecanismo | Efecto típico | Cómo detectarlo |
|---|---|---|
| IVA incluido en el valor | Infla revenue 21 % (ES) | Revisa qué envía el pixel/CAPI (`value`) |
| Envío cobrado incluido | Infla revenue | Ídem |
| Devoluciones no descontadas | 3–35 % según categoría | Tasa de devolución por categoría |
| Descuentos (BFCM, códigos de bienvenida) | Baja AOV y CM2 | AOV y CM2 por campaña/periodo |
| Mix de productos de bajo margen | El sistema optimiza revenue, no margen | Margen por SKU en ventas atribuidas |
| Clientes existentes y no incrementales | ROAS alto, nCAC alto | Segmentos + nuevos en tienda + lift |
| View-through (1d vista) | Atribuye compras de otros canales | Comparar 7d clic vs 7d clic + 1d vista |
| Agencia, creativo, herramientas | 10–25 % del gasto | Incluir en f |
| Location fees (desde jul-2026, 2–5 %) | +2–5 % coste | Facturas de Meta |
| Cohortes sin recompra | LTV < CAC | Tabla de cohortes |
| Fraude / pedidos cancelados | Revenue fantasma | Pedidos cancelados vs atribuidos |

## 6. MER: la métrica de control del negocio

- **MER = revenue total / inversión total en marketing.** No necesita atribución, por eso es robusto. [EMPIRICAL — práctica DTC]
- **MER break-even** = (1 + f) / c (misma base de revenue). En el ejemplo A: 2,70.
- **Lectura**: el MER cae al escalar (rendimientos decrecientes) y sube en BFCM (demanda) y con base de clientes grande (recurrentes). Por eso conviene seguir también **aMER** (revenue de nuevos / inversión) o **nCAC**.
- Rangos que publican agencias (MER "saludable" 2,5–5×) son orientativos y dependen de margen y recurrencia; no los uses como objetivo sin tu CM2. [HYPOTHESIS]

### Ejemplo de P&L mensual con MER

| Línea | € |
|---|---|
| Ventas brutas (IVA incl.) | 500.000 |
| CM2 (45,5 % de ventas brutas, como ejemplo A) | 227.500 |
| Inversión ads (todas las plataformas) | 100.000 |
| Agencia + creativo + fees | 23.000 |
| **CM3** | **104.500** |
| Costes fijos | 80.000 |
| **EBITDA** | **24.500** |

MER = 5,0. Si al escalar a 150.000 € de inversión el MER cae a 4,0 (ventas 600.000 €): CM2 = 273.000; CM3 = 273.000 − 150.000 − 34.500 = 88.500 → **EBITDA baja a 8.500 €** aunque las ventas suban un 20 %. Escalar con MER decreciente solo compensa si los clientes nuevos adicionales tienen LTV que lo justifique.

## 7. nCAC objetivo y LTV por cohortes

### 7.1 Construir la tabla de cohortes (lo mínimo)

Por mes de adquisición (y si se puede, por canal de adquisición): clientes nuevos, y para M0, M1, M3, M6, M12: pedidos acumulados por cliente, revenue neto acumulado por cliente, **CM2 acumulado por cliente**.

### 7.2 Ejemplo C — Suplementos (compra única + recompra)

- Primer pedido: CM2 15 € (con descuento de bienvenida). Pedidos de recompra: CM2 18 €.
- Pedidos acumulados por cliente: M3 = 1,45; M6 = 1,80; M12 = 2,30.
- CM2 acumulado por cliente: M0 15,0 € · M3 15 + 0,45×18 = **23,1 €** · M6 15 + 0,80×18 = **29,4 €** · M12 15 + 1,30×18 = **38,4 €**.

| nCAC | Payback | LTV₁₂:CAC (en CM2) | Decisión |
|---|---|---|---|
| 40 € | > 12 meses | 0,96 | No escalar: no recupera en 12 meses |
| 30 € | ~6 meses | 1,28 | Aceptable si hay caja y la cohorte es estable |
| 25 € | ~4 meses | 1,54 | Escalar con control |
| 15 € | M0 | 2,56 | Rentable en primer pedido: escalar agresivamente hasta que nCAC suba |

### 7.3 Reglas para fijar el nCAC objetivo

1. **Primer pedido break-even** (negocios sin recompra fuerte o con caja limitada): nCAC ≤ CM2 del primer pedido / (1 + f).
2. **Payback objetivo** (negocios con recompra probada): nCAC ≤ CM2 acumulado a 3–6 meses de cohortes recientes, con descuento por riesgo (p. ej. usar 80 % del valor).
3. **Heurística 8x** (vendor): CM2/nCAC > 1 → rentable primer pedido; 0,7–1 → se recupera con recompra; < 0,7 → parar escalado. [EMPIRICAL, vendor]
4. **LTV:CAC** — 3:1 viene de SaaS; en e-commerce lo relevante es payback y coste de capital. Usa LTV a 12 meses en CM2 y exige ≥ 1,5–2× si el payback es > 6 meses. [CONTESTED/HYPOTHESIS en umbral]

## 8. Costes que hay que imputar al marketing

| Coste | Rango orientativo | Etiqueta |
|---|---|---|
| Fee de agencia | 5–15 % del gasto o fijo mensual | [HYPOTHESIS — varía mucho] |
| Producción creativa (UGC, creadores, shootings, IA) | 5–20 % del gasto en cuentas DTC creativas | [HYPOTHESIS] |
| Location fee de Meta | 2 % UK; 3 % FR/IT/ES; 5 % AT/TR (desde 1-jul-2026, por ubicación de la audiencia) | [OFFICIAL META vía prensa] |
| Comisiones de pago | Shopify Payments Basic EE. UU. 2,9 % + 0,30 $; UK 2 % + 0,25 £; ejemplos UE ~1,5–2,1 % + 0,25–0,30 € | [EMPIRICAL — tarifas varían por país/plan; verificar] |
| Herramientas (atribución, feeds, creative analytics) | Fijo; prorratear si es material | — |
| Descuentos de adquisición (welcome 10–15 %) | Restan del revenue del primer pedido | — |

## 9. Señales de que la economía, no Meta, es el problema

- CM2 % < 30 % sobre ventas brutas y AOV < 30 €: casi ningún canal de pago escala rentable en primer pedido. Soluciones: bundles, umbral de envío gratis, subir precio, otro mix.
- nCAC estable pero CM3 negativo: el problema es margen o costes variables.
- MER cae al escalar con nCAC subiendo rápido: saturación de audiencia/creatividad (ver carpeta 03/09).
- Cohortes recientes con recompra inferior a las antiguas: los nuevos clientes son de peor calidad (descuentos agresivos, producto de entrada) → el LTV histórico ya no vale para justificar el nCAC.

## Implicaciones operativas

- Calcula y documenta **CM2 por pedido y CM2 %** sobre la base que ve Meta antes de fijar cualquier objetivo de ROAS/CPA.
- Publica en el equipo cuatro números: ROAS break-even (plataforma), CPA/nCAC break-even primer pedido, nCAC objetivo con recompra, MER break-even.
- Ajusta por incrementalidad con un IF por tipo de campaña (prospección vs retargeting) obtenido de tests; revísalo cada 6 meses.
- Revisa margen por SKU en lo que vende Meta; excluye o separa productos de bajo margen.
- Si el pixel envía valor con IVA, puedes (a) mantenerlo y ajustar objetivos, o (b) enviar valor neto (sin IVA, menos devolución esperada) para que la optimización a valor sea fiel al margen. (b) cambia la comparación histórica: hazlo con un corte claro. [STRONG INFERENCE]

## Errores frecuentes

- Break-even = 1 / margen bruto.
- Comparar ROAS con IVA de España con benchmarks de EE. UU. (sin sales tax en el value en muchos setups).
- Tomar el LTV de clientes de hace 3 años para justificar el nCAC de hoy.
- Calcular LTV en revenue en vez de en margen.
- No imputar agencia, creativo y location fees.
- Escalar porque "el ROAS aguanta" mientras el MER y el CM3 caen.

## Preguntas abiertas

- Si Meta permitirá optimizar a margen (beneficio) de forma nativa (hoy se aproxima con valores personalizados enviados vía CAPI y value rules).
- Factor de incrementalidad típico por tipo de campaña en 2026 tras la mejora de Incremental Attribution (Haus 2026 sugiere mejoras, sin desglose por campaña).
- Tasas de devolución por categoría en Europa 2025-2026 de fuente primaria.

## Fuentes clave

- [What is CM2 (8x)](https://eightx.co/blog/what-is-cm2-contribution-margin-after-fulfillment) — 2026 — vendor (finanzas DTC)
- [DTC unit economics end-to-end (8x)](https://eightx.co/blog/dtc-unit-economics-end-to-end) — 2026 — vendor
- [Breakeven ROAS (Triple Whale)](https://www.triplewhale.com/blog/breakeven-roas) — 2025 — vendor
- [Ecommerce ROAS (Retentionly)](https://retentionly.io/post/ecommerce-roas) — 2025-2026 — vendor
- [CTC — contribution margin](https://commonthreadco.com/blogs/coachs-corner/loftie-founder-contribution-margin-changed-everything) — 2025 — agencia
- [The Meta Report (Haus)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Meta to charge advertisers 2–5% location fee](https://www.storyboard18.com/digital/meta-to-charge-advertisers-2-5-location-fee-in-select-countries-to-offset-digital-service-taxes-91778.htm) — 2026 — prensa
- [Returns & shrink totaled nearly $800B in 2025 (Chain Store Age)](https://chainstoreage.com/study-returns-shrink-totaled-nearly-800b-2025) — 2025-2026 — prensa
- [Shopify transaction fees 2026 (Qualimero)](https://qualimero.com/en/blog/shopify-transaction-fees) — 2026 — vendor
- [Is Meta Taking Credit for Your Holiday Repeat Buyers (AdBeacon)](https://www.adbeacon.com/meta-attribution-new-vs-returning-customers-bfcm/) — 2026-10-07 — vendor
