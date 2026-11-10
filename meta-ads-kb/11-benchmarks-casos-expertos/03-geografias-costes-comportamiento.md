# Geografías: costes, comportamiento y conversión

> Última verificación: 2026-10-15 · Autor: A11 (agente) · Ámbito: EE. UU., Canadá, Reino Unido, España, resto de Europa, LatAm (México, Colombia, Argentina, Chile, Perú, Brasil), Australia y Asia. Costes, comportamiento, pagos, idioma, regulación y qué implica vender a hispanohablantes en EE. UU., España o LatAm. El escalado operativo multi-país está en `04-escalado-internacional.md`.

## TL;DR

- **La inflación de subasta no es uniforme.** Q2 2026, precio por anuncio interanual según Meta: **EE. UU. y Canadá +20 %**, Europa +10 %, APAC +1 %, resto del mundo (incluye LatAm) +21 %. EE. UU. se encarece y APAC se mantiene. **[OFFICIAL META]**
- **Orden de magnitud del CPM (USD, e-commerce, Lebesgue 2026, sin metodología declarada):** EE. UU. ~16 $; Reino Unido, Australia y Canadá ~11–12 $; Alemania ~9 $; Francia y España ~6,7–7 $; Italia y Portugal ~6 $; México ~3,9 $; Brasil ~2,6 $; Chile ~2,4 $; Colombia ~2,0 $; India ~1,4 $. **El ranking es consistente entre fuentes; las cifras absolutas no** (AdAmigo da EE. UU. 23 $ y España 5,8 $). **[EMPIRICAL]** (débil)
- **Un CPM bajo no es eficiencia.** Cuando se optimiza para eventos baratos (clics, leads), Meta concentra entrega en países o segmentos que no compran. En el test de Jon Loomer, el **74 % de los registros venía de países que aportaban ~3 % de las ventas**. Separa o restringe por valor. **[EMPIRICAL]**
- **Desde el 1-jul-2026 hay "location fees"** sobre impresiones entregadas en **Reino Unido (2 %), España, Francia e Italia (3 %), Austria y Turquía (5 %)**. Van fuera del presupuesto y la CBO no las tiene en cuenta: tu "Amount spent" ya no cuadra con la factura. Incluye el fee en el ROAS de equilibrio. **[OFFICIAL META]** (anunciado en marzo de 2026; aplicación observada)
- **En la UE, desde enero de 2026, todo usuario que elige el servicio con anuncios debe escoger entre anuncios personalizados y "menos personalizados" (LPA),** que según Meta usan un 90 % menos de datos. No hay cifras públicas de adopción ni de impacto en rendimiento. Es un riesgo estructural de señal en la UE frente a EE. UU. **[OFFICIAL META]** / impacto **[HYPOTHESIS]**
- **Hispanohablantes en EE. UU.:** según Pew (2025), el uso de Instagram (62 %), TikTok (57 %) y **WhatsApp (56 %)** es mucho mayor que en adultos blancos (45 %, 28 % y 23 %). Facebook se usa de forma similar (74 % frente a 70 %). La audiencia es mayoritariamente bilingüe: lo que funciona son **anuncios multi-idioma**, no "solo español". **[EMPIRICAL]**
- **LatAm se juega en el checkout y en la mensajería:** en México el 23 % de los compradores online paga en efectivo en tiendas tipo OXXO (AMVO 2025), Pix domina en Brasil y click-to-WhatsApp es un canal de venta de primer orden. Con CPM de 2–4 $ y un checkout de EE. UU., el CPA real puede ser peor que en España. **[EMPIRICAL]**
- **España:** CPM medio-bajo para Europa occidental (~6–7 $), uso masivo de WhatsApp, Bizum como medio de pago creciente (entre el 20 % y el 30 % de los clientes lo usan en e-commerce, según estimaciones citadas por Stripe), fee de localización del 3 % y LPA de la UE. Datos públicos específicos de rendimiento escasos. **[EMPIRICAL]** (débil)

---

## 1. Tabla comparativa de costes por país (2026)

> Todas las cifras de esta tabla vienen de blogs de vendors **sin metodología verificable**. Úsalas solo para ordenar mercados y estimar órdenes de magnitud. Moneda: USD.

| País | CPM Lebesgue (e-commerce, jul-2026) | CPM AdAmigo ("proyección 2026") | CPC AdAmigo | Notas |
|---|---|---|---|---|
| EE. UU. | 16,08 | 23,00 (rango 18–28) | 2,69 | Biddyco: mediana de cuentas grandes 18,73; Triple Whale e-com 15,06; AdKit global 8,88 |
| Canadá | 11,47 | 13,40 | 1,75 | Quebec exige francés (ver §4) |
| Reino Unido | 11,81 | 10,31 | 1,95 | Fee de localización del 2 % |
| Australia | 11,63 | 18,50 | 2,10 | Picos en BF, Navidad, Boxing Day y EOFY (junio) |
| Alemania | 9,05 | 10,05 | 1,45 | — |
| Francia | 6,95 | 8,05 | 1,15 | Fee del 3 % |
| **España** | **6,65** | **5,80** (4,50–7,00) | 0,85 | Fee del 3 %; Superads: CPC mediano de 0,46 € (jul-25 a jul-26) |
| Italia | 6,06 | 7,20 | 1,05 | Fee del 3 % |
| Portugal | 6,02 | — | — | — |
| Japón | 6,73 | 11,50 | 1,85 | — |
| **México** | **3,92** | 4,50 | 0,45 | — |
| Brasil | 2,63 | 4,20 | 0,35 | — |
| Chile | 2,44 | 5,20 | 0,60 | Las fuentes no coinciden en su posición regional |
| **Colombia** | **2,00** | 4,00 | 0,42 | Financiación con USDC disponible (ago-2026) |
| Argentina | n/d | 3,80 | 0,38 | Financiación con USDC disponible; alta volatilidad cambiaria |
| Perú | n/d | 3,70 | 0,36 | — |
| India | 1,36 | 2,60 | 0,20 | — |

**Lo consistente entre fuentes:** EE. UU. > Australia, Canadá y Reino Unido > Europa nórdica y central > Europa del sur (España, Italia, Portugal) > LatAm > India y el norte de África. La relación EE. UU./España ronda **2,4–4×** y la de EE. UU./México **4–6×**. **[EMPIRICAL]**

**Lo que no es consistente:** el nivel absoluto (EE. UU. de 16 $ a 23 $) y la posición de Chile. Para LatAm, un agregador (fuelads) admite que las cifras de Argentina y Perú son **interpoladas**, es decir, estimadas y no medidas. **[EMPIRICAL]**

## 2. Lo que dice Meta por región (fuente fiable)

Variación interanual del precio medio por anuncio (presentaciones de resultados de Meta). Detalle en `01-benchmarks-2025-2026.md`. **[OFFICIAL META]**

| Región | Q3 2025 | Q4 2025 | Q1 2026 | Q2 2026 |
|---|---|---|---|---|
| EE. UU. y Canadá | +13 % | +9 % | +14 % | **+20 %** |
| Europa | +19 % | +12 % | +19 % | +10 % |
| Asia-Pacífico | +1 % | −2 % | +5 % | +1 % |
| Resto del mundo (LatAm, MEA…) | +20 % | +15 % | +18 % | **+21 %** |

**Lectura:** el "resto del mundo" (donde está LatAm) se encarece al mismo ritmo que EE. UU., aunque desde una base mucho más baja. El precio de APAC está plano porque crece mucho el inventario: las impresiones suben entre un 17 % y un 24 % interanual. **[OFFICIAL META]** / interpretación **[STRONG INFERENCE]**

## 3. El mecanismo: por qué el CPM barato atrae al algoritmo y engaña al anunciante

- El sistema optimiza **coste y volumen del evento elegido**, no su valor. Si el evento es barato de conseguir (clic, lead, instalación), la entrega se desplaza hacia geografías o segmentos donde ese evento es barato. Loomer: "Quality is not part of the algorithm. Only cost and volume." (artículo de 2017, actualizado en 2025; el principio sigue vigente para eventos no-valor). **[EMPIRICAL]**
- **Datos del caso Loomer:** el 74 % de los registros venía de 12 países que suponían ~3 % de sus ventas. La ratio compra/visita era de 0,10 en Australia, 0,09 en EE. UU., 0,06 en Reino Unido y Canadá, y 0,01 en India: un visitante australiano valía unas 10 veces más que uno indio. Al restringir a los países de valor, el CPL pasó de 0,29 $ a 1,79 $ y el negocio mejoró. **[EMPIRICAL]**
- **RocketShip HQ (2026, apps):** "No metas mercados con más de 3× de diferencia de CPI en la misma CBO." La CBO desplaza presupuesto a los mercados de instalación barata. Agrupar por **ratio LTV/CPI** y no por geografía. **[EMPIRICAL]**
- **API (sept-2026):** los lookalikes creados por API ignoran el campo de país y la llamada se acepta con un aviso de deprecación. Un ad set multi-país puede acabar entregando a ubicaciones no previstas. Hay una nota oficial de Meta, pero el comportamiento lo observó un tercero (admakeai). **[OFFICIAL META]** / **[EMPIRICAL]**

## 4. Mercado por mercado

### 4.1 EE. UU.

- **Coste:** el mercado más caro y el que más se encarece (+20 % de precio por anuncio en Q2 2026). Tinuiti: Facebook +13 % e Instagram 0 % de CPM en Q2 2026. Reels ya es el 35 % de las impresiones de Instagram. **[OFFICIAL META]** / **[EMPIRICAL]**
- **Conversión:** los paneles de e-commerce dan una CVR de clic a compra del ~1,5 % (Triple Whale) y del ~2,2 % (DTC grandes, Biddyco). **[EMPIRICAL]**
- **Señal:** es el mercado con mejor señal (no hay LPA de la UE), aunque iOS/ATT sigue presente (véase área 04).
- **Calendario:** BFCM con CPM de +35–57 % frente a octubre. Segunda semana de diciembre peligrosa. Enero barato (−17 %). **[EMPIRICAL]**
- **Hispanos en EE. UU.:** ver §5.

### 4.2 Canadá

- CPM ~11–13 $. Meta lo agrupa con EE. UU. en su reporting, así que hereda la misma presión de precio. **[EMPIRICAL]** / **[OFFICIAL META]**
- **Quebec:** la Carta de la Lengua Francesa (Bill 96) obliga a informar y servir en francés, también en web y redes sociales, con versión francesa **al menos igual de prominente y comprensible por sí sola** (una mala traducción no cumple). Desde el 1-jun-2025 se endurecen las reglas de publicidad comercial y marcas no francesas. Fuentes: despachos y CMA, no el texto de la OQLF. **Consulta con un abogado** si segmentas Quebec. **[STRONG INFERENCE]**
- **Implicación operativa:** separa Quebec (FR) del resto de Canadá (EN), o usa anuncios multi-idioma con una versión francesa revisada por un nativo.

### 4.3 Reino Unido

- CPM ~10–12 $. **Fee de localización del 2 %** desde el 1-jul-2026. **[OFFICIAL META]**
- Fuera de la UE: el LPA de la UE no aplica, pero el marco de privacidad (UK GDPR) es similar. **[STRONG INFERENCE]**
- Mercado maduro en DTC. Suele ser la "segunda casa" de marcas de EE. UU., con creatividad compartida si se adapta ortografía, precio (£) y envío.

### 4.4 España

- **Coste:** CPM ~5,8–6,7 $ (estimaciones de vendors). CPC mediano de 0,46 € en el periodo jul-2025 a jul-2026 (Superads, serie muy volátil). **Fee de localización del 3 %.** **[EMPIRICAL]** (débil) / **[OFFICIAL META]**
- **Plataformas:** según IAB Spain (2025), el 83 % de la población de 12 a 74 años usa redes (~32,4 M). Preferencias: WhatsApp 37 %, Instagram 16 %, YouTube 14 %. **[EMPIRICAL]**
- **Pagos:** Bizum gana peso. Entre enero y septiembre de 2025, 18 600 empresas de e-commerce lo implementaron, y se estima que lo usa entre el 20 % y el 30 % de los clientes (Stripe, citando estimaciones). El Banco de España (nov-2025) indica que el efectivo sigue siendo el medio principal en tienda física para el 57 %. **[EMPIRICAL]**
- **Señal:** UE, con LPA obligatorio en el flujo de consentimiento desde enero de 2026. **[OFFICIAL META]**
- **Hueco:** no hay benchmarks públicos fiables de CVR, CPA o CPL específicos de España en 2025-2026. Usa el histórico propio. **[STRONG INFERENCE]**

### 4.5 Resto de Europa

- **Norte y centro** (Alemania, Países Bajos, nórdicos, Suiza, Austria): CPM de 7,3–9 $, más caros que el sur. **Austria tiene un fee del 5 %.** Alemania suele mostrar CVR de e-commerce relativamente alta en estudios de agregadores, aunque sin una fuente primaria verificada aquí. **[EMPIRICAL]** (débil)
- **Sur** (Italia, Portugal, Grecia): CPM de 4,9–6 $. Italia y Francia tienen un fee del 3 %. **[OFFICIAL META]**
- **Este** (Polonia, Chequia, Rumanía, Hungría): CPM de 5,2–5,7 $. En Polonia, Meta exige verificación de anunciante a quien hace publicidad financiera (ago-2026). **[OFFICIAL META]** (vía changelog)
- **UE en general:** LPA obligatorio en el consentimiento desde enero de 2026. En diciembre de 2025, Meta alineó con la Comisión nuevos cambios en su modelo de consentimiento. La CFO advirtió de una posible "experiencia materialmente peor" en el EEE si los reguladores exigen más. **[OFFICIAL META]**

### 4.6 LatAm

| País | CPM (rango de fuentes) | Señales de comportamiento | Notas |
|---|---|---|---|
| **México** | 3,9–4,5 $ | 77 M de compradores digitales (AMVO 2025). Pago: débito 69 %, crédito 54 %, **efectivo en tiendas (OXXO) 23 %**, transferencia 20 %. Valoran los meses sin intereses y el envío gratis | Tarifa de mensaje *marketing* de WhatsApp: 0,0397 $ desde oct-2026 (+30 % frente a julio). Buen Fin 2025: ventas online de 45 900 M MXN (+31 %) |
| **Brasil** | 2,6–4,2 $ | Pix: >160 M de usuarios. Mercado de WhatsApp muy maduro | Tarifa *marketing* de WhatsApp: 0,0625 $, cara frente a su CPM |
| **Colombia** | 2,0–4,0 $ | — | Financiación de cuenta con USDC disponible (ago-2026) |
| **Chile** | 2,4–5,2 $ | Mercado más pequeño y con más poder adquisitivo | Las fuentes discrepan sobre si es el más caro de la región |
| **Argentina** | 1,4–3,8 $ | Volatilidad cambiaria (precios en ARS frente a gasto publicitario) | USDC disponible; los CPM agregados son estimaciones interpoladas |
| **Perú** | 1,4–3,7 $ | — | CPM estimado/interpolado |

**Patrones LatAm:**
- **Mensajería como canal de conversión.** Meta muestra tests oficiales en México y Brasil donde optimizar por compra o por lead (en vez de por conversación) mejora resultados. Art di Cacao (México): +56 % de compras. Braip (Brasil): −30 % de CPL y +45 % de leads cualificados. **[OFFICIAL META]** (casos autodeclarados)
- **Checkout local:** las fuentes de pagos (vendors de PSP) reportan un abandono del 5–10 % con Pix frente al 20–30 % con OXXO, con OXXO liquidando en 1–3 días. Son cifras de vendors sin verificar, pero plantean una pregunta clave: **¿le envías a Meta el evento Purchase al generar el voucher o al cobrarlo?** Si es al generarlo, el ROAS se infla con pedidos que nunca se pagan. **[HYPOTHESIS]** (no documentado como caso)
- **Precio local:** RocketShip HQ recomienda precios por paridad de poder adquisitivo antes de escalar en mercados Tier 2-3. Ejemplo de apps: 9,99 $/mes en EE. UU. → ~29,90 R$ en Brasil en lugar de ~55 R$ por conversión directa. Cita a RevenueCat: conversión entre 2 y 3 veces mayor y trial-to-paid 2,4 veces mayor con precios PPP. **[EMPIRICAL]** (secundaria)
- **Inflación de subasta "resto del mundo":** +21 % en Q2 2026. Los CPM bajos de LatAm se están encareciendo deprisa. RocketShip cita un crecimiento del gasto en mercados emergentes del +28 % interanual frente al +8 % en Tier 1. **[OFFICIAL META]** / **[EMPIRICAL]**

### 4.7 Australia

- CPM ~11,6–18,5 $ según la fuente. Es Tier 1 en coste. **[EMPIRICAL]** (débil)
- Calendario propio: **EOFY (fin del año fiscal, junio)**, además de BF, Navidad y Boxing Day.
- **Ley de menores:** Meta eliminó **756 000 cuentas de menores de 16 años** entre el 1-dic-2025 y el 30-jun-2026 por la prohibición australiana. Si tu target es joven, el inventario disponible ha cambiado. **[OFFICIAL META]** (vía changelog)

### 4.8 Asia

- **Japón:** CPM de 6,7–11,5 $. Fija siempre el idioma japonés (RocketShip: reducción de alcance de solo el 3–5 %). La localización cultural es imprescindible. **[EMPIRICAL]**
- **India:** el CPM más bajo (1,4–2,6 $) con un LTV muy bajo: RocketShip le da un índice de LTV de 8–20 frente a 100 en EE. UU. Segmentar solo en inglés limita el alcance al ~35 %. Las tarifas de WhatsApp son muy bajas (*marketing* 0,0118 $). **[EMPIRICAL]**
- **SEA** (Indonesia, Malasia, Filipinas): casos oficiales de Meta donde optimizar por compra frente a por conversación multiplica las compras (Confer On, Indonesia: ×3,9 compras y −79 % de coste por compra). **[OFFICIAL META]** (autodeclarado)
- **APAC en conjunto:** el precio por anuncio está plano (+1 % en Q2 2026) con un inventario que crece >17 %. Es la región con menos inflación. **[OFFICIAL META]**

## 5. Vender a hispanohablantes: EE. UU. frente a España frente a LatAm

| Dimensión | Hispanos en EE. UU. | España | LatAm |
|---|---|---|---|
| CPM | Precios de EE. UU. (~15–23 $); el filtro de idioma reduce la audiencia ~90 % (estimación de guías antiguas) | ~6–7 $ (+3 % de fee) | ~2–5 $ |
| Poder adquisitivo | Alto (USD) | Medio-alto (EUR) | Medio-bajo; muy variable |
| Idioma | Bilingüe mayoritario; el inglés crece en jóvenes (Pew, datos de 2013–2015, sin actualizar) | Español peninsular (vosotros, léxico propio) | Variantes regionales (ustedes, voseo en Argentina, léxico) |
| Plataformas | Facebook 74 %, Instagram 62 %, **WhatsApp 56 %**, TikTok 57 % (Pew 2025) | WhatsApp líder, Instagram 2.º en preferencia | WhatsApp central, Facebook fuerte en México y Brasil |
| Pagos | Tarjeta, BNPL | Tarjeta, Bizum, PayPal | Débito, crédito a meses, OXXO, Pix, transferencia |
| Regulación de datos | EE. UU. (estatal) | UE: LPA y RGPD | Variable; menos restrictiva en ads |

**Evidencia sobre idioma en EE. UU.:**
- **Pearmill** (2023, un cliente, sin datos de muestra): los anuncios **multi-idioma** (un anuncio con versiones EN y ES servidas según el idioma del dispositivo) lograron un **CPA un 21 % menor** que los de solo inglés. Los de solo español tuvieron un CTR un 20 % mayor y un CPM menor. Es útil como hipótesis, débil como prueba. **[EMPIRICAL]** (débil)
- **Facebook IQ** (estudio antiguo): la mayoría de los hispanos de EE. UU., sean dominantes en español (79 %), bilingües (82 %) o dominantes en inglés (60 %), quiere que las marcas anuncien en ambos idiomas. **[OFFICIAL META]** (antiguo; sin fecha verificada)
- Afirmaciones de blogs del tipo "el CPM en español es un 15–25 % menor" no tienen metodología. **No las uses.** **[HYPOTHESIS]**

**Implicaciones:**
1. **No reutilices tal cual las creatividades de España en EE. UU. ni en LatAm (ni al revés).** El léxico, el "vosotros", los precios, el envío y los medios de pago rompen la confianza. Es un error de localización típico de marcas españolas. **[STRONG INFERENCE]**
2. **En EE. UU., prioriza anuncios multi-idioma** (Meta *Multi-Language Ads*, `asset_feed_spec` con etiquetas de idioma) sobre ad sets con el filtro de idioma español, que recortan la audiencia y excluyen a los bilingües. **[STRONG INFERENCE]**
3. **En LatAm, diseña el embudo alrededor de WhatsApp y de pagos locales.** Optimiza por compra o lead cualificado, no por conversación, si tienes señal. **[OFFICIAL META]** (casos) / **[STRONG INFERENCE]**
4. **El mismo producto puede necesitar tres precios y tres ofertas.** Un CPA "barato" en LatAm puede tener un payback peor que un CPA "caro" en España si el AOV es menor y el cobro es incierto. **[STRONG INFERENCE]**

## Implicaciones operativas

- **Presupuesta inflación por región** con el dato oficial de Meta: EE. UU./Canadá +20 % y resto del mundo +21 % (Q2 2026).
- **Añade los fees de localización** (Reino Unido 2 %, España, Francia e Italia 3 %, Austria y Turquía 5 %) al cálculo de ROAS de equilibrio y concilia las facturas fuera de Ads Manager.
- **No agrupes países con más de 3× de diferencia de CPM o CPA en una misma CBO** si optimizas por un evento sin valor. Agrupa por valor esperado.
- **Comprueba el desglose por país cada semana** en cualquier campaña multi-país, sobre todo de leads o tráfico.
- **En la UE, asume menos señal** (LPA) y refuerza CAPI, eventos de valor y medición por incrementalidad.
- **En LatAm, decide conscientemente cuándo dispara el Purchase** con métodos de pago diferidos (OXXO, boleto).

## Errores frecuentes

- Elegir un mercado "porque el CPM es 4 veces más barato" sin modelar AOV, CVR, cobro y logística.
- Mezclar España y LatAm (o España y EE. UU.) en el mismo ad set con la misma creatividad "en español".
- Usar el filtro de idioma español en EE. UU. y concluir que "los hispanos no convierten" con una audiencia diminuta.
- Ignorar el francés en Quebec.
- Comparar el ROAS de Ads Manager entre la UE y EE. UU. sin considerar las diferencias de señal (LPA, consentimiento) ni los fees.

## Preguntas abiertas

- **Adopción y efecto del LPA en la UE:** Meta no publica el porcentaje de usuarios ni el impacto en CPM y CVR. Es un hueco crítico para anunciantes europeos.
- **Benchmarks reales de España y LatAm:** CVR, CPA y CPL por vertical con metodología transparente no encontrados para 2025-2026.
- **Datos actualizados sobre el idioma de los hispanos de EE. UU.:** los datos de Pew sobre dominancia de idioma son de 2013–2015.
- **¿Cómo se comporta la CBO/Advantage+ entre España y LatAm en el mismo conjunto?** No hay tests públicos. Hipótesis: el presupuesto fluye a LatAm si el evento es barato.

## Fuentes clave

- [Meta price per ad by region (recopilación de las slides de Meta)](https://adwize.ai/meta-ad-price-history): 2026, vendor (datos oficiales)
- [Meta Q2 2026 results](https://investor.atmeta.com/investor-news/press-release-details/2026/Meta-Reports-Second-Quarter-2026-Results/): 29-jul-2026, meta-investors
- [Lebesgue: Facebook CPM by Country 2026](https://lebesgue.io/facebook-ads/facebook-cpm-by-country): 27-jul-2026, vendor
- [AdAmigo: CPM & CPC by Country 2026](https://www.adamigo.ai/blog/meta-ads-cpm-cpc-benchmarks-by-country-2026): 2026, vendor
- [Superads: CPC España](https://www.superads.ai/facebook-ads-costs/cpc-cost-per-click/spain): 2026, vendor
- [Jon Loomer: Geography and the Problem with Facebook Ads Optimization](https://www.jonloomer.com/facebook-ads-optimization/): 2017, actualizado en mar-2025, practitioner
- [RocketShip HQ: Meta app ads in multiple countries (2026)](https://www.rocketshiphq.com/meta-app-ads-multiple-countries-3/): 7-abr-2026, agencia
- [eMarketer: Meta passes location fees](https://www.emarketer.com/content/meta-passes-location-fees-onto-businesses-raising-ad-costs-across-europe) y [Yahoo/Reuters](https://finance.yahoo.com/news/meta-charge-advertisers-fee-offset-182506077.html): mar-2026, prensa
- [PPC Land: Meta 2026 DMA report](https://ppc.land/metas-2026-dma-report-reveals-whatsapp-ads-a-eu200m-fine-and-a-defiant-stance-on-personalized-advertising/): 2026, prensa
- [Meta Q4 2025 follow-up call transcript](https://s21.q4cdn.com/399680738/files/doc_financials/2025/q4/META-Q4-2025-Follow-Up-Call-Transcript.pdf): ene-2026, meta-investors
- [Pew Research: Social Media Fact Sheet (2025)](https://www.pewresearch.org/internet/fact-sheet/social-media/): 2025, académico
- [Pearmill: Spanish ads reduced CPA by 20%](https://pearmill.com/blog/how-spanish-ads-reduced-cpa-by-20-and-connected-with-a-new-audience): 3-jul-2023, agencia
- [Milenio: AMVO 2025, 77 M de compradores digitales](https://www.milenio.com/negocios/mexico-supera-77-millones-compradores-digitales-2025-amvo): 2025, prensa
- [Stripe: Bizum para empresas](https://stripe.com/resources/more/bizum-for-buisinesses-spain): 2025, vendor
- [Marketing4ecommerce: Estudio de Redes Sociales España 2025 (IAB)](https://marketing4ecommerce.net/estudio-redes-sociales-en-espana-2025/): 2025, prensa
- [Spur: CTWA benchmarks + tarifas de WhatsApp](https://www.spurnow.com/en/blogs/click-to-whatsapp-ads-benchmarks): 2026, vendor
- [Bill 96 Quebec (Miller Thomson)](https://www.millerthomson.com/en/insights/publications/bill-96-quebec-french-language-law-overhaul/): 2022–2025, despacho
- [admakeai: changelog sept-2026 (Australia <16, USDC, verificación en Polonia, lookalikes por API)](https://admakeai.com/blog/meta-ads-updates-september-2026): 2026, vendor
