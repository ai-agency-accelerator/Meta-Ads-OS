# Escalado internacional en Meta Ads

> Última verificación: 2026-10-15 · Autor: A11 (agente) · Ámbito: moneda, idioma, localización, zona horaria, ofertas, píxel y datos, campañas por país o multi-país, Advantage+ y geografías, traducción automática de Meta y fees regulatorios. Contexto de costes en `03-geografias-costes-comportamiento.md`.

## TL;DR

- **Regla de estructura:** agrupa mercados por **valor esperado del evento** (LTV/CPA o AOV × CVR × cobro), no por cercanía geográfica. Separa en campañas propias los 3–5 mercados más importantes y no mezcles en la misma CBO/Advantage+ mercados con más de 3× de diferencia de coste por evento si optimizas por un evento sin valor. **[EMPIRICAL]** (RocketShip HQ 2026; Loomer)
- **Una sola campaña "todos los países" solo sirve para explorar.** El algoritmo persigue el evento más barato y oculta qué mercado es rentable. **[EMPIRICAL]**
- **La ubicación es una de las pocas restricciones "duras" que respeta Advantage+ Audience** (junto con la edad mínima y las exclusiones de custom audiences). Advantage+ no expande países que no hayas elegido, pero **sí reparte el presupuesto entre ellos sin control por país**. **[EMPIRICAL]** (Loomer, 2026)
- **Moneda y zona horaria** son propiedades de la cuenta publicitaria. Según guías de terceros, cambiarlas desactiva la cuenta y crea una nueva, sin poder reactivar la antigua. Decide antes de lanzar: **una cuenta por divisa de facturación y zona horaria del mercado principal**. **[STRONG INFERENCE]** (sin doc oficial verificada aquí)
- **Localiza el catálogo, no lo dupliques.** Meta soporta catálogos localizados con feeds de país (precio, moneda, URL, disponibilidad) y de idioma (título, descripción), con vuelta al feed principal si falta la versión local. Así se mantiene un único historial de aprendizaje. **[OFFICIAL META]** (developer docs, actualizado en nov-2025)
- **Multi-Language Ads** (antes *Dynamic Language Optimization*) permite un solo anuncio con versiones por idioma servidas según el idioma del usuario. Suele ser mejor que crear ad sets con filtro de idioma. **[OFFICIAL META]** / **[STRONG INFERENCE]**
- **La traducción automática de Meta** (Advantage+ Creative, "Translate text") traduce solo texto principal y titular a una lista de idiomas que decide Meta, sin poder editar el resultado (observado en 2025). **No la uses sin revisión nativa en mercados prioritarios.** **[EMPIRICAL]**
- **Coste regulatorio nuevo:** desde el 1-jul-2026 se aplican fees de localización del 2–5 % en 6 países según la ubicación de la audiencia (no la del anunciante). La CBO no los tiene en cuenta. **[OFFICIAL META]** (anuncio de mar-2026)
- **El nivel de localización es una decisión de ROI:** subtítulos → voz y texto → adaptación cultural → producción local. RocketShip estima entre un 15 % y un 80 % de mejora de CPI según el nivel, con un coste de 50–5 000 $ por pieza. Solo los niveles 3-4 se justifican por encima de unos 5 k$/día por mercado. **[EMPIRICAL]** (fuente de agencia de apps; cifras no auditadas)

---

## 1. Decisiones previas (antes de gastar el primer euro)

| Decisión | Opciones | Recomendación por defecto | Por qué |
|---|---|---|---|
| **Cuentas publicitarias** | Una global frente a una por región o divisa | Una por **divisa de facturación** y zona horaria principal (p. ej. EUR-Madrid, USD-Nueva York) | La moneda y la zona horaria no se cambian sin crear una cuenta nueva (guías de terceros). Los presupuestos diarios y los informes siguen la zona horaria de la cuenta. **[STRONG INFERENCE]** |
| **Píxel / dataset** | Uno por dominio frente a uno global | **Un dataset por web/tienda.** Si hay dominios por país (.es, .mx), valora un dataset por dominio o uno compartido con el parámetro de país | Mezclar dominios complica la deduplicación y la verificación de dominios (véase área 04). **[STRONG INFERENCE]** |
| **Moneda del evento Purchase** | Moneda local frente a USD | Envía `value` y `currency` (ISO 4217) **reales del pedido** | La documentación de Meta exige value y currency en Purchase. No se ha verificado aquí cómo convierte Meta divisas distintas a la de la cuenta: comprueba en Events Manager que los valores cuadran. **[OFFICIAL META]** / **[HYPOTHESIS]** |
| **Catálogo** | Uno por país frente a uno localizado | **Un catálogo principal + feeds de país e idioma** | Un solo historial de producto y menos fragmentación. **[OFFICIAL META]** |
| **Dominios / URLs** | Subcarpetas o dominios por país | Cualquiera, pero coherente con el catálogo (link por país en el country feed) | Evita enviar a usuarios de México a precios en euros. **[STRONG INFERENCE]** |
| **Oferta y precio** | Precio único convertido frente a precio local | **Precio local con paridad de poder adquisitivo y medios de pago locales** | RocketShip/RevenueCat: entre 2 y 3 veces más conversión con PPP en apps. **[EMPIRICAL]** |

## 2. Estructura de campañas: por país, por tier o multi-país

| Estructura | Cuándo usarla | Riesgo | Fuente |
|---|---|---|---|
| **Una campaña con todos los países** | Exploración inicial y barata para descubrir dónde hay demanda (RocketShip: unos 200 $/día como mínimo) | El presupuesto va a los países de evento barato; las métricas agregadas esconden mercados no rentables | RocketShip HQ 2026; Wevion |
| **Una campaña por tier** (mercados con economía parecida) | Mercados con ratio LTV/CPA similar (p. ej. EE. UU., Reino Unido, Canadá y Australia; o España y Portugal) | Algo de fuga a los países más baratos del tier | RocketShip HQ 2026 |
| **Una campaña por país** | Los 3–5 mercados principales y cualquier mercado con idioma, precio o regulación distintos | Fragmentación si el presupuesto por país no alcanza unos 50 eventos/semana | RocketShip (≥50–100 $/día por país); Loomer (50 eventos/semana) |
| **Ad sets geográficos en ABO** | Testear creatividades en 3–5 mercados con control de gasto | Más gestión y menos aprendizaje compartido | RocketShip (~30 $/día por ad set) |
| **Advantage+ (sales/app) por país** | Escalar un mercado **ya probado** | Sin control por país dentro de la campaña; caja negra | RocketShip; Meta |

**Heurística de umbral (deducida de la regla de unos 50 eventos semanales por ad set):** presupuesto diario mínimo por unidad ≈ CPA objetivo × 50 / 7 ≈ **7 × CPA**. Con un CPA de 40 €, unos 285 €/día por campaña de país. Si no llegas, agrupa mercados por tier o usa eventos de funnel más altos (add to cart, lead cualificado) durante el arranque. **[STRONG INFERENCE]**

**RocketShip HQ (apps, 2026):** presupuesto para unos 50 conversiones/semana. Tier 1 compra (CPA de 25–60 $): 180–430 $/día. Tier 2 compra (CPA de 5–15 $): 36–107 $/día. Tier 3 instalación: 0,70–2 $/día ("solo volumen"). **[EMPIRICAL]** (cifras de la agencia)

## 3. Idioma y localización

### 3.1 Herramientas de Meta

| Herramienta | Qué hace | Estado / limitaciones |
|---|---|---|
| **Multi-Language Ads** (API: `asset_feed_spec` con etiquetas de idioma y `asset_customization_rules`) | Un anuncio con imagen, vídeo y texto por idioma. Meta sirve la versión que corresponde al idioma del usuario | Oficial (developer docs). Sucesor de *Dynamic Language Optimization* (2017). **[OFFICIAL META]** |
| **Translate text** (Advantage+ Creative) | Traduce el primer texto principal y el titular a idiomas que Meta elige según la audiencia | Early Release en 2025, solo para imagen y vídeo individuales (no carrusel ni flexible). Loomer no pudo editar ni elegir idiomas. **[EMPIRICAL]** |
| **Translate voiceover** | Doblaje de voz con IA | Empezó como test EN→ES en 2024. Un vendor afirma que en junio de 2026 se añadieron más idiomas al texto sobre imagen y 11 a la voz en off: **no verificado con Meta**. **[HYPOTHESIS]** |
| **Catálogo localizado** (country/language feeds) | Precio, moneda, URL, disponibilidad y textos por país e idioma | Oficial; incluye una vía para Advantage+ catalog ads. **[OFFICIAL META]** |

### 3.2 Filtro de idioma en el ad set

- Restringe la entrega a quien tiene la interfaz en ese idioma. Las guías estiman reducciones de audiencia enormes: en EE. UU., añadir el filtro español deja ~10 % de la audiencia (dato antiguo) y **excluye a los bilingües con interfaz en inglés**. **[EMPIRICAL]** (débil)
- RocketShip (2026): Japón siempre en japonés (−3–5 % de alcance); Brasil en portugués (−5–8 %); India en inglés limita al ~35 %; Emiratos en árabe limita al 55–60 % (separar árabe e inglés); Alemania, probar con y sin filtro. **[EMPIRICAL]**
- **Regla:** en mercados monolingües, el filtro casi no cuesta alcance. En mercados bilingües o con expatriados (EE. UU., Canadá, Emiratos, India, Suiza, Bélgica), usa Multi-Language Ads en lugar del filtro. **[STRONG INFERENCE]**

### 3.3 Niveles de localización creativa (RocketShip HQ, 2026; cifras de agencia sin auditar)

| Nivel | Qué incluye | Mejora de CPI estimada | Coste por pieza | Cuándo |
|---|---|---|---|---|
| 1 | Subtítulos traducidos | −15–30 % | 50–150 $ | Mercados con más de 300 $/día |
| 2 | Voz en off y cambio de texto | −25–45 % | 200–500 $ | Mercados con más de 300 $/día |
| 3 | Adaptación cultural | −40–65 % | 800–2 000 $ | Más de 5 k$/día y ≥30 días de product-market fit |
| 4 | Producción local completa | −50–80 % | 2 000–5 000 $ | Solo por encima de 10 k$/día |

### 3.4 Errores de idioma típicos (hispanohablantes)

- **Español peninsular en LatAm o en EE. UU.** (vosotros, "coger", "ordenador", precios en €, envío desde España).
- **Español neutro "de doblaje"** en España: suena a marca extranjera.
- **Traducción automática sin revisión** en titulares con juegos de palabras, claims regulados (salud, finanzas) o tallas y medidas.
- **Quebec sin francés** o con una traducción de baja calidad (requisito legal, véase `03`).

## 4. Zona horaria, presupuesto y ritmo

- Los presupuestos diarios se reinician según la **zona horaria de la cuenta**. Una campaña con España y México en una cuenta de Madrid "cierra el día" a las 17–18 h de Ciudad de México. Para campañas con programación horaria (dayparting) necesitas presupuesto total y la programación se aplica a la zona del usuario o de la cuenta según la configuración (véase área 09). **[STRONG INFERENCE]**
- **Rolling budget** (2026): permite repartir un presupuesto diario a lo largo de 7 días. Foxwell recomienda probarlo antes de BFCM en un pico pequeño. Es útil en mercados con picos locales (Buen Fin, Hot Sale, El Corte Inglés, Singles Day). **[EMPIRICAL]** (Foxwell, Q3 2026)
- **Calendarios comerciales locales** que desplazan CPM y CVR: Buen Fin y Hot Sale (México), Black Friday (global), Cyber Day (Chile, Argentina), EOFY (Australia, junio), rebajas de enero y julio (España), Singles Day 11.11 (Asia). Planifica creatividades y presupuesto por mercado. **[STRONG INFERENCE]**

## 5. Datos, píxel y señal por región

- **UE:** desde enero de 2026 el LPA es una opción obligatoria en el flujo de consentimiento y usa un 90 % menos de datos según Meta. Asume peor señal y refuerza CAPI con buenos parámetros de cliente y eventos de valor. **[OFFICIAL META]**
- **Eventos de cobro diferido** (OXXO, boleto, contra reembolso): decide si envías Purchase al crear el pedido o al cobrarlo. Si es al crearlo, el ROAS de plataforma se infla con pedidos impagados. Valora enviar un evento propio "Paid Purchase" vía CAPI y optimizar por él cuando tenga volumen. **[HYPOTHESIS]**
- **Lookalikes por API:** desde sept-2026 ignoran el campo de país (con aviso de deprecación). Revisa las automatizaciones que crean lookalikes multi-país. **[OFFICIAL META]** (changelog v26) / comportamiento **[EMPIRICAL]**
- **Exclusiones y audiencias de cliente:** en Advantage+ Sales, Meta decide el reparto entre clientes nuevos y existentes. El antiguo tope de "existing customer budget" de ASC dejó de estar disponible en la migración a Advantage+ Sales (Loomer cita a Meta: "is no longer available"). Revisa por país el % de gasto en clientes existentes (Audience Segments). **[EMPIRICAL]**

## 6. Fees, impuestos y facturación por país

| País | Fee de localización (desde 1-jul-2026) |
|---|---|
| Reino Unido | 2 % |
| España | 3 % |
| Francia | 3 % |
| Italia | 3 % |
| Austria | 5 % |
| Turquía | 5 % (el impuesto subyacente bajaría al 2,5 % en ene-2027 según un changelog de terceros) |

- Se aplica según **dónde está la audiencia**, no el anunciante: una marca de EE. UU. que anuncia en Francia paga el 3 %. Va **fuera del presupuesto** de la campaña, la CBO no lo considera y el IVA se calcula sobre el total (100 $ en Italia se facturan como 103 $). Cubre anuncios de imagen y vídeo, click-to-message de WhatsApp y mensajes de marketing. **[OFFICIAL META]** (comunicado de mar-2026 vía Reuters/eMarketer/Medianama)
- **Implicación:** el ROAS de equilibrio sube en esos países. Si optimizas con valores o ROAS mínimo, ajusta el objetivo (p. ej. objetivo de ROAS × 1,03 en España). **[STRONG INFERENCE]**
- **Financiación de cuentas con USDC** (ago-2026): disponible en Argentina y Colombia, útil frente a la volatilidad cambiaria. **[OFFICIAL META]** (vía changelog) / alcance por verificar.
- **Verificación de anunciante:** Meta quiere que los anunciantes verificados supongan el 90 % de los ingresos a finales de 2026. Ya es obligatoria en algunos casos, como servicios financieros dirigidos a Polonia o Singapur antes del 31-ene-2027. **[OFFICIAL META]** (vía changelog)

## 7. Secuencia recomendada de expansión

1. **Validar la economía unitaria local** (precio, envío, devoluciones, medios de pago, fee de Meta) antes de anunciar.
2. **Exploración controlada:** 2–4 semanas con un tier o grupo de mercados similares, optimizando por un evento con valor (purchase con value) y con un desglose por país semanal.
3. **Graduar** el mercado ganador a su propia campaña cuando sostenga unos 50 eventos/semana.
4. **Localización progresiva:** nivel 1-2 al graduar y nivel 3-4 cuando el mercado justifique más de 5 k$/día.
5. **Medición:** cuando un mercado supere un umbral relevante de gasto, haz un geo-holdout o conversion lift. Los geo-tests son naturales por país o región.
6. **Revisión trimestral** con la inflación por región publicada por Meta.

## Implicaciones operativas

- **Hacemos:** cuentas por divisa; catálogo localizado; Multi-Language Ads en mercados bilingües; campañas por país para los mercados principales; desglose semanal por país; fees en el cálculo de equilibrio.
- **Evitamos:** campañas "worldwide" con eventos baratos; filtros de idioma en mercados bilingües; traducción automática sin revisión; un mismo precio convertido en todos los mercados; Purchase disparado en pagos diferidos sin control.
- **Umbral:** si un mercado está por encima de 3× la diferencia de CPA con el resto de su campaña, sepáralo.

## Errores frecuentes

- Duplicar el catálogo por país y fragmentar el aprendizaje.
- Lanzar Advantage+ con 10 países y no mirar nunca el desglose por país.
- Crear la cuenta en USD para vender en euros (reporting y facturación con conversión), o con la zona horaria de la agencia.
- Asumir que "Meta traduce solo" es suficiente en mercados prioritarios.
- Olvidar los fees de localización y no cuadrar las facturas.

## Preguntas abiertas

- ¿Cómo maneja exactamente Meta los valores de Purchase en divisas distintas a la de la cuenta (conversión en la ingesta o en el reporting, y con qué tipo de cambio)? No verificado en la documentación oficial durante esta investigación.
- ¿Advantage+ Sales con varios países reparte de forma demostrablemente distinta a una CBO manual? No hay tests públicos.
- Lista oficial actual de idiomas de la traducción automática (texto, texto sobre imagen, voz) en octubre de 2026: no verificada.

## Fuentes clave

- [RocketShip HQ: How to run Meta app ads in multiple countries (2026)](https://www.rocketshiphq.com/meta-app-ads-multiple-countries-3/): 7-abr-2026, agencia
- [Meta Developers: Multi-Language Ads](https://developers.facebook.com/docs/marketing-api/multi-language-ads): vigente, meta-developers
- [Meta Developers: Localized Catalogs](https://developers.facebook.com/documentation/ads-commerce/catalog/guides/localized-catalog): actualizado el 24-nov-2025, meta-developers
- [Meta Developers blog: Dynamic Language Optimization (2017)](https://developers.facebook.com/ads/blog/post/2017/03/22/dynamic-language-optimization/): 2017, meta-developers (histórico)
- [Jon Loomer: Translate Text Feature](https://www.jonloomer.com/qvt/translate-text-feature/): 2025, practitioner
- [Jon Loomer: Advantage+ Sales replaces Advantage+ Shopping](https://www.jonloomer.com/qvt/advantage-sales-replaces-advantage-shopping/): 2025, practitioner
- [Jon Loomer: The Master Brief](https://www.jonloomer.com/meta-ads-master-brief/): 2-jul-2026, practitioner
- [Jon Loomer: Geography and Facebook Ads Optimization](https://www.jonloomer.com/facebook-ads-optimization/): 2017/2025, practitioner
- [Foxwell Digital: 9 pressing topics Q3 2026](https://www.foxwelldigital.com/blog/the-9-most-pressing-topics-for-meta-advertisers-in-q3-2026): jul-2026, agencia
- [Medianama: Meta location fees](https://www.medianama.com/2026/03/223-meta-advertisers-location-fees-digital-service-taxes/): mar-2026, prensa
- [eMarketer: Meta passes location fees](https://www.emarketer.com/content/meta-passes-location-fees-onto-businesses-raising-ad-costs-across-europe): 2026, prensa
- [Feedoptimise: country/local feeds](https://www.feedoptimise.com/blog/meta-catalogues-how-to-set-up-country-local-feeds): 2025, vendor
- [admakeai: changelog sept-2026](https://admakeai.com/blog/meta-ads-updates-september-2026): 2026, vendor
- [Optmyzr: timezone settings (Meta)](https://help.optmyzr.com/en/articles/3074849-timezone-in-optmyzr-s-tools): vigente, vendor
