# Cómo usar benchmarks bien (y mal)

> Última verificación: 2026-10-15 · Autor: A11 (agente) · Ámbito: método para interpretar benchmarks de Meta Ads, sesgos de cada tipo de fuente y reglas de decisión. Datos concretos en `01-benchmarks-2025-2026.md`.

## TL;DR

- **Un benchmark no te dice si una campaña es rentable.** La rentabilidad depende de tu margen de contribución, tu AOV/LTV, la incrementalidad real y tus costes fijos. Un ROAS de 1,5 puede ser rentable (LTV alto, halo en Amazon) y uno de 4 puede perder dinero (margen del 20 %, devoluciones o mucha recompra no incremental). **[STRONG INFERENCE]**
- **El benchmark correcto es tu propio histórico,** ajustado por estacionalidad y por la inflación de subasta que publica Meta (+12 % de precio por anuncio global y +20 % en EE. UU./Canadá en Q2 2026). Los paneles externos solo sirven para detectar desviaciones de órdenes de magnitud. **[STRONG INFERENCE]**
- **Las cifras "de mercado" se contradicen entre fuentes serias según el panel.** Para el CPM de Q1 2026 frente a Q1 2025 en EE. UU.: Tinuiti dice **−3 %**, CTC (170+ marcas) **+28 %** y Meta (precio por anuncio en EE. UU./Canadá) **+14 %**. Para julio de 2026, Superads da **−12,7 %** interanual. Ninguna cifra "miente": miden universos distintos. **[EMPIRICAL]**
- **El sesgo más frecuente es definicional:** CTR all frente a CTR de enlace (en AdKit la mediana es 2,45 % frente a 1,00 %), CPL de formulario instantáneo frente a CPL de landing, ROAS 7d click/1d view frente a 1d click frente a iROAS, y media frente a mediana. **[EMPIRICAL]**
- **El sesgo de muestra decide el número.** Usuarios de una herramienta concreta (Triple Whale, Motion, Superads), clientes de una agencia (CTC, Biddyco), un país (WordStream es solo EE. UU.) o un tramo de gasto (Biddyco: cuentas de 100 k$–2,3 M$/mes). **[EMPIRICAL]**
- **Los benchmarks de incrementalidad (Haus, Stella)** son los únicos que acercan a "¿esto genera negocio?", pero tienen sesgo de autoselección: las marcas que testean son más grandes y sofisticadas. Además el IF no se puede predecir desde el ROAS de plataforma. **[EMPIRICAL]**
- **Regla operativa:** antes de decidir con un benchmark, rellena las 7 preguntas de la sección 4. Si no puedes contestar al menos 5, el benchmark no sirve para esa decisión. **[STRONG INFERENCE]**

---

## 1. Para qué sirve un benchmark y para qué no

| Uso legítimo | Uso ilegítimo |
|---|---|
| Detectar si algo está **roto** (CTR de enlace del 0,2 % en un e-commerce de moda, CPM de 80 $ en España en prospección) | Decidir si una campaña es **rentable** |
| Hacer un **primer presupuesto** de un mercado nuevo (orden de magnitud del CPM, inflación esperada) | Fijar un **objetivo de CPA** a un cliente sin conocer su margen |
| Explicar a un cliente o CFO que una subida de CPM es **de mercado** (dato oficial de Meta por región) | Justificar que "estamos por encima de la media" cuando el negocio pierde dinero |
| Priorizar **hipótesis de diagnóstico** (si el CTR está bien y la CVR mal, el problema está después del clic) | Comparar el **ROAS de plataforma entre objetivos** o entre cuentas con atribución distinta |
| Dimensionar el **volumen creativo** necesario por tramo de gasto (Motion) | Copiar la estructura de "los mejores" sin su contexto (vertical, gasto, oferta) |

## 2. Primeros principios: por qué los benchmarks engañan

### 2.1 La métrica es un ratio de dos cosas que cambian

- **CPA = CPM ÷ (1 000 × CTR × CVR).** Un CPM un 30 % más caro con una CVR que se triplica (Black Friday) da un CPA más bajo. Biddyco midió en BF 2025 un CPM de +57 % y un coste por compra de −42 %. Juzgar por un solo factor es un error de razonamiento. **[EMPIRICAL]**
- WordStream (2026) lo formula así para leads: CPC y CVR se mueven juntos, y el CPL solo mejora si la bajada de CPC compensa la caída de conversión. **[EMPIRICAL]**

### 2.2 El denominador de la rentabilidad no está en el benchmark

- **ROAS de equilibrio = 1 ÷ margen de contribución** (después de COGS, envío, comisiones de pago, devoluciones y, si aplica, los fees de localización de Meta del 2–5 % en algunos países europeos y Turquía desde el 1-jul-2026). Con un margen del 40 %, el equilibrio está en 2,5. La mediana de Triple Whale (1,88) estaría por debajo. **[STRONG INFERENCE]**
- **En recompra/suscripción** el criterio correcto es el nCAC frente al LTV a 90/180/365 días. En lead gen, el coste por **venta** (o por oportunidad cualificada) frente al valor del cliente. Ningún panel público publica eso por industria de forma fiable. **[STRONG INFERENCE]**

### 2.3 Atribución ≠ causalidad

- **Haus** (640 tests): la relación entre lo que reporta la plataforma y lo incremental cambia según el objetivo (multiplicador ×1,3 mid-funnel, ×2,4 tráfico, ×6 alcance frente a conversión). Advantage+ sobre-reportó **12 puntos** frente a Manual. **[EMPIRICAL]**
- **Stella** (46 geo-tests): IF medio de 1,21, pero **sin relación lineal** con el ROAS de plataforma. Hubo marcas con ROAS >4 e IF <1. **[EMPIRICAL]**
- **Conclusión:** un benchmark de ROAS de plataforma mide la **contabilidad de Meta**, no el negocio. Úsalo para comparar periodos dentro de la misma cuenta y con la misma configuración, no para decidir inversión entre canales. Ver área 04. **[STRONG INFERENCE]**

## 3. Catálogo de sesgos (con ejemplos reales de 2025-2026)

| Sesgo | Qué pasa | Ejemplo verificado |
|---|---|---|
| **Muestra de usuarios de una herramienta** | Solo marcas que pagan esa herramienta (más maduras, más e-commerce, más EE. UU.) | Triple Whale (>40 000 marcas e-commerce), Motion (6 015 cuentas), Superads (">3 000 M$") |
| **Muestra de una agencia** | Clientes de un perfil concreto y gestión homogénea | CTC (253 cuentas, cost controls), Biddyco (23 cuentas grandes de EE. UU.) |
| **País** | Mezclar EE. UU. con LatAm hunde el CPM medio | WordStream = solo EE. UU.; AdKit = todos los países (mediana de CPM 8,88 $ frente a 15–19 $ en paneles de EE. UU.) |
| **Objetivo** | Campañas de alcance con CPM de 4–5 $ arrastran las medias | Biddyco: CPG con 1,8–2,3 M$/mes a 4,60–4,80 $ de CPM |
| **Media frente a mediana** | La media se dispara por outliers | WordStream aclara que sus "medias" son medianas; Biddyco: CPM ponderado por gasto ~14–15 $ frente a mediana de 18,73 $ |
| **Definición de métrica** | CTR all frente a enlace; "lead" de formulario frente a cualificado | AdKit: CTR all 2,45 % frente a saliente 1,00 % |
| **Atribución** | 7dc/1dv frente a 1dc frente a píxel de terceros frente a iROAS | Triple Whale no declara ventana; Stella normaliza a 7dc/1dv; Haus usa iROAS |
| **Ventana temporal** | Un trimestre con BFCM no se parece a uno sin él | Motion (sep-25 a ene-26 incluye BFCM); Biddyco jun-ago 2026 (verano) |
| **Supervivencia** | Solo sobreviven en el panel las cuentas que siguen gastando | Cualquier panel basado en clientes actuales |
| **Vendedor con interés** | El benchmark apoya el producto que se vende | Confect (vende catálogo): "el catálogo gana +23 % de ROAS"; CTC (vende servicio creativo): "20+ ads/mes = +65 % de ROAS" |
| **Cifra de Meta autodeclarada** | Media de tests elegidos por Meta, sin dispersión | "+22 % ROAS con Advantage+", "−11,7 % CPA con Advantage+ placements", "−10 % coste por lead cualificado" |
| **Blogs SEO "benchmarks 2026"** | Recombinan cifras de terceros sin fuente | AdAmigo publica "proyecciones 2026" con un rango de EE. UU. contradictorio en la propia página; Lebesgue no declara muestra ni periodo |
| **Muestras diminutas por segmento** | Saltos interanuales absurdos | WordStream: CTR de leads en Muebles +155 %, con ≥4 campañas por subcategoría |

## 4. Las 7 preguntas antes de usar un benchmark

1. **¿Qué universo?** País, vertical, tamaño de cuenta y quién está en la muestra (y por qué).
2. **¿Qué periodo?** ¿Incluye Q4 o BFCM? ¿Antes o después de cambios grandes de Meta (Andromeda completo en oct-2025, cambios de atribución de ene/mar-2026)?
3. **¿Qué objetivo y evento de optimización?** Tráfico, leads, compra, alcance, app.
4. **¿Qué definición exacta de la métrica?** CTR all o de enlace, CPL de instant form o de web, ROAS con qué ventana y modelo.
5. **¿Media o mediana? ¿Hay percentiles?** Sin dispersión, la cifra sirve de poco.
6. **¿Quién lo publica y qué vende?**
7. **¿Qué decisión concreta vas a tomar con él?** Si la respuesta es "decidir si invertir más", necesitas tu economía unitaria y una prueba de incrementalidad, no un benchmark.

## 5. Cómo construir tu propio benchmark (lo que sí funciona)

1. **Línea base interna:** 13 meses de datos por semana ISO, con CPM, CTR de enlace, CVR (clic → compra o lead), CPA, AOV, % de nuevos clientes y MER/aMER del negocio.
2. **Ajuste de mercado:** normaliza tu CPM con el dato oficial de Meta de precio por anuncio de tu región. Si tu CPM sube +25 % en EE. UU. y el mercado sube +20 %, tu desviación real es de unos +5 %. **[STRONG INFERENCE]**
3. **Ajuste estacional:** compara la misma semana del año anterior (BFCM no se compara con octubre).
4. **Umbrales de negocio, no de panel:** CPA máximo = margen de contribución × % de incrementalidad asumido (o el valor del lead × tasa de cierre).
5. **Triangulación:** plataforma (Ads Manager) frente a backend (Shopify/CRM) frente a encuesta post-compra frente a test de incrementalidad periódico (conversion lift o geo-holdout, véase área 04).
6. **Paneles externos solo como "test de cordura":** si tu CTR de enlace está por debajo del p25 de tu vertical, el problema probablemente es creativo o de oferta. Si tu CPM está por encima del p75 de tu país, revisa el objetivo, la calidad del anuncio y las restricciones de audiencia.

## 6. Interpretación de señales combinadas (diagnóstico rápido)

| Patrón frente a tu histórico y frente al panel | Hipótesis prioritaria | Siguiente paso |
|---|---|---|
| CPM ↑, CTR =, CVR =, CPA ↑ en línea con el mercado | Inflación de subasta (Q4, EE. UU. 2026) | Revisar el margen; no tocar la estructura |
| CPM =, CTR ↓, CVR = | Fatiga creativa o pérdida de "hook" | Nuevos conceptos (no variaciones) |
| CTR ↑, CVR ↓ | Tráfico de menor intención (Reels, placements, creatividades "clicables"), cambios en la landing o en la definición de clic | Desglose por placement; revisar la landing; comparar con backend |
| CPA plataforma ↓, backend = | Atribución inflada (duplicados, view-through, recompra) | Auditar la deduplicación y el % de nuevos clientes |
| CPL ↓ mucho, ventas = | Leads baratos de baja calidad (edad 65+, Audience Network, formularios sin fricción) | Optimizar por evento de calidad vía CAPI/CRM y value rules por edad |
| Todo "en benchmark", negocio en pérdidas | Economía unitaria rota u oferta no competitiva | Revisar precio, margen y LTV antes que los anuncios |

## Implicaciones operativas

- Prohibido fijar un KPI de cliente con "el benchmark de la industria". El KPI sale de la economía unitaria y se valida con incrementalidad.
- En los informes, presenta siempre: tu cifra, tu histórico, el ajuste de mercado (dato oficial de Meta) y, solo como contexto, el p25–p75 de un panel comparable.
- Cuando cites un benchmark, añade **fuente, periodo, muestra, estadístico y definición**. Si falta alguno, márcalo como orientativo.
- Para lead gen, el único benchmark que importa es **coste por venta o por oportunidad cualificada**. Monta el circuito de CRM antes de discutir el CPL.

## Errores frecuentes

- "Nuestro CTR es 2 %, por encima del benchmark de 1,5 %": probablemente comparas CTR all con CTR de enlace.
- "Nuestro ROAS es 3 y la media es 1,88, vamos bien": con un margen del 25 % pierdes dinero (equilibrio en 4), y además no sabes cuánto es incremental.
- Tomar la cifra de Meta "+22 % ROAS con Advantage+" como expectativa propia. Es una media autodeclarada y Haus encontró que el 58 % de las marcas tuvo mejor iROAS con Manual.
- Pensar que un CPM más bajo en un país equivale a eficiencia. Ver `03-geografias-costes-comportamiento.md` (el caso de Loomer: el 74 % de los registros venía de países con el 3 % de las ventas).
- Reaccionar a variaciones diarias. Evalúa ventanas de 7 días con al menos 2 semanas de datos (Loomer, 2026).

## Preguntas abiertas

- ¿Hay algún panel público con **coste por venta o por oportunidad** en lead gen por industria y con metodología transparente? No se ha encontrado en 2025-2026.
- ¿Cómo afectan los cambios de atribución de 2026 (retirada de ventanas view de 7 y 28 días en la API en enero de 2026 y redefinición de clic en marzo de 2026, véase área 04) a la comparabilidad interanual de los paneles que usan la API?
- ¿Por qué divergen tanto los paneles sobre el CPM de 2026 (Tinuiti −3 % en Q1 frente a CTC +28 %)? Hipótesis: el mix Instagram/Reels (CPM plano) frente a Facebook (+13 %) y el mix de objetivos.

## Fuentes clave

- [WordStream: Facebook Ads Benchmarks 2026](https://www.wordstream.com/blog/facebook-ads-benchmarks-2026): 2026, vendor
- [Triple Whale: Facebook Ad Benchmarks](https://www.triplewhale.com/blog/facebook-ads-benchmarks): ago-2026, vendor
- [AdKit Benchmarks](https://adkit.so/benchmarks): oct-2026, vendor
- [Biddyco: Meta Ads Benchmarks 2026](https://www.biddyco.com/blog-posts/meta-ads-benchmarks): 2026, agencia
- [Biddyco: Black Friday 2025 CPM/CPA](https://www.biddyco.com/blog-posts/meta-ads-black-friday-cpm): oct-2026, agencia
- [Haus: The Meta Report](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments): jul-2025, vendor
- [Stella: incrementality study](https://www.stellaheystella.com/blog/incrementality-study-how-incremental-is-meta-really): 2025, vendor
- [CTC: Meta Andromeda Killed Your ROAS](https://commonthreadco.com/blogs/coachs-corner/meta-andromeda-roas-creative-strategy-2026): 6-may-2026, agencia
- [CPA.RIP: análisis de Tinuiti Q2 2026](https://cpa.rip/en/facebook/analysing-ads-q2-2026/): 2026, prensa/blog
- [admakeai: changelogs mensuales (datos de Superads y Tinuiti)](https://admakeai.com/blog/meta-ads-updates-august-2026): ago-2026, vendor
- [Meta Q2 2026 results](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/): 29-jul-2026, meta-investors
- [AdAmigo CPM/CPC por país 2026](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026): 2026, vendor (ejemplo de fuente débil)
