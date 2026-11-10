# Suscripciones (apps y e-commerce) y funnels web-to-app en Meta

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: trial → pago, modelado de LTV por cohortes, efecto del churn en el CPA objetivo, optimización a trial vs pago, suscripciones de e-commerce (subscribe & save, cajas) y funnels web-to-app, incluido el contexto legal de EE. UU. (Epic v. Apple) a oct-2026.

## TL;DR

- **El CPA objetivo de una suscripción es una función del churn**: con LTV ≈ margen × ARPU / churn mensual, pasar de 10 % a 15 % de churn recorta el LTV (y el CAC máximo) un 33 %. Un cambio de producto (onboarding, pricing, retención) mueve más el CPA permitido que cualquier ajuste de campaña. [STRONG INFERENCE — álgebra]
- **Optimiza al evento más profundo que Meta pueda ver a tiempo y en volumen**: en apps, normalmente *trial* (mejor "qualified trial" filtrando cancelaciones del día 0), no *paid* (llega 3–30 días después y fuera de la ventana útil). En web, el pago inicial (paid trial / primera cuota) vía Pixel + CAPI. [EMPIRICAL — Burke, Airbridge, Adapty]
- **Benchmarks 2026 (RevenueCat, >115.000 apps, 16.000 M$)**: trial→pago mediano 42,5 % (trials 17–32 días), 37,4 % (5–9 días), 25,5 % (≤ 4 días; ya el 46,5 % de apps usa trials ≤ 4 días); descarga→pago a 35 días 10,7 % en hard paywall vs 2,1 % freemium; RPI a 60 días 3,09 $ vs 0,38 $; el 55,4 % de cancelaciones de trials de 3 días ocurre el día 0. [EMPIRICAL]
- **El churn anual se está disparando en 2026**: ~72 % de suscriptores anuales cancela en el año 1 (vs ~56 % en 2025) y el mes 1 concentra el 35 % de las cancelaciones anuales; las apps de IA retienen peor en planes mensuales (−36 % a 12 meses). Usa cohortes recientes, no históricas, para el LTV. [EMPIRICAL — RevenueCat SOSA 2026]
- **Web-to-app**: comisiones de 2–6 % frente a 15–30 % en tiendas, señal más rápida y granular (Pixel/CAPI frente a SKAN/AEM), pricing flexible y cobro inmediato; a cambio, más fricción (conversión inicial menor), más fraude en trials gratuitos y ~50 % de pagos fallidos a gestionar (RevenueCat). RevenueCat: 41 % de las apps top ya generan ingresos web. [EMPIRICAL]
- **EE. UU., contexto legal a oct-2026**: tras el desacato del 30-abr-2025, Apple permite enlaces/botones de compra externa en la App Store de EE. UU. sin comisión; el 11-dic-2025 el Noveno Circuito confirmó el desacato pero permitió a Apple exigir paridad de prominencia y una comisión "razonable" ligada a costes (remitido al tribunal de distrito); el **30-jun-2026 el Supremo aceptó revisar el estándar de desacato** (no la comisión). Apple dice que sigue sin cobrar comisión en compras enlazadas mientras dure la revisión; en remand propuso hasta 15 % (fuente secundaria). Para web-to-app esto significa: hoy es más fácil enviar usuarios de la app al checkout web en EE. UU., pero la economía puede cambiar en 2027. [OFFICIAL — 10-Q de Apple; Fenwick; 9to5Mac] / [EMPIRICAL] (15 %)
- **Suscripción en e-commerce (subscribe & save, cajas)**: retención reportada ~45 % a 6 meses y ~33 % a 12 meses (Recharge, citado por terceros); churn mensual típico 5–9 % en consumibles y mayor en cajas de curación; ~1/3 de suscriptores cancela en 3 meses (McKinsey vía terceros). El descuento de primera caja infla la conversión y empeora la retención: mide LTV por oferta de entrada. [EMPIRICAL vía secundaria — baja-media]

## 1. Modelo de LTV para suscripciones

### 1.1 Fórmulas

- **Retención geométrica (aproximación)**: LTV = m × ARPU × (1 / churn), con m = margen de contribución por cobro (tras comisión de tienda/pasarela, coste de servicio/producto, envío en e-commerce).
- **Con horizonte H meses** (más prudente): LTV_H = m × ARPU × (1 − (1 − churn)^H) / churn.
- **Por cohortes (recomendado)**: LTV_H = Σ_{t=0..H} m × ARPU_t × S(t), con S(t) la supervivencia observada de la cohorte; la curva real tiene más caída al principio (mes 1) que después.
- **CAC por suscriptor máximo** = LTV_H aceptado (p. ej. 6 o 12 meses) × (1 − colchón de riesgo).
- **CAC por trial máximo** = CAC por suscriptor × tasa trial→pago.

### 1.2 Efecto del churn en el CPA objetivo (ejemplo)

ARPU 20 €/mes, margen m = 70 % (14 € de contribución por cobro), horizonte 12 meses.

| Churn mensual | LTV₁₂ | CAC/suscriptor máx. (80 % de LTV₁₂) | Con trial→pago 40 %: coste/trial máx. |
|---|---|---|---|
| 5 % | 14 × (1 − 0,95¹²)/0,05 = 128,7 € | 103,0 € | 41,2 € |
| 10 % | 14 × (1 − 0,90¹²)/0,10 = 100,5 € | 80,4 € | 32,2 € |
| 15 % | 14 × (1 − 0,85¹²)/0,15 = 80,1 € | 64,1 € | 25,6 € |
| 20 % | 14 × (1 − 0,80¹²)/0,20 = 65,2 € | 52,2 € | 20,9 € |

Lectura: pasar de 10 % a 15 % de churn baja el coste por trial permitido de 32 € a 26 € (−20 % en 12 meses; −33 % en horizonte infinito). Si la campaña se juzga con un objetivo de coste por trial fijo y el churn empeora, la cuenta pierde dinero sin que Ads Manager lo muestre.

### 1.3 Ajustes que suelen olvidarse

- **Reembolsos y contracargos** (más altos en web y en planes anuales).
- **Pagos fallidos / churn involuntario**: 31 % de las cancelaciones en Google Play vs 14 % en App Store son fallos de cobro (RevenueCat 2026); en web, RevenueCat estima ~50 % de pagos fallidos recuperables con reintentos y herramientas. [EMPIRICAL]
- **Mes 1** concentra el grueso de la caída (en anuales, el 35 % de las cancelaciones del año 1). [EMPIRICAL]
- **Comisiones**: Apple 30 % (15 % SBP o tras el año 1 del suscriptor); Google 15 % suscripciones; web 2–6 % todo incluido (RevenueCat da 2–3 % de procesador, ~5–6 % blended). [EMPIRICAL]
- **IVA** incluido en precios al consumidor en la UE.

## 2. Trial vs pago como evento de optimización

| Evento | Ventajas | Riesgos | Cuándo |
|---|---|---|---|
| Instalación | Volumen | Calidad baja | Solo para aprender CPI |
| Registro / onboarding completo | Temprano, volumen | Débil correlación con pago en algunas apps | Freemium sin trial |
| **Trial (StartTrial)** | Ocurre en minutos; volumen suficiente | Trials "basura" (cancelación día 0), varía por placement | Por defecto en apps con trial |
| **Qualified trial** (trial no cancelado tras 2–4 h, o con señal de uso) | Mejor correlación con pago, sigue siendo temprano | Requiere server-side y un pequeño retraso | Cuando cancelación de trial > ~30 % |
| Pago (Subscribe/Purchase) | Es dinero | Llega tarde (3–30 días), poco volumen; AEM ventana ~7 días post-clic | Hard paywall sin trial, paid trial, web checkout |
| Valor (VO/ROAS) | Prioriza alto valor | Volumen y varianza necesarios | Varios planes/precios, upsells |

Notas [EMPIRICAL]:
- Burke (abr-2025): optimizar a StartTrial; el CPA "parece" bueno, pero la conversión trial→pago varía por placement → evaluar calidad por placement/audiencia.
- Adapty (jun-2026): si la cancelación del trial > 30 %, enviar el evento solo de quien no canceló.
- Airbridge (mar-2026): Qualified Trial con retraso de 2–4 h; Subscribe con valor real para la conversión trial→pago y trial con valor 0 como eventos separados si se usa VO.
- **[CONTESTED]**: algunos practitioners prefieren optimizar a pago en web (CAPI) porque la señal es "dinero real"; otros prefieren trial por volumen. Depende de: volumen semanal de pagos por ad set (≥ 50 → pago viable) y del retraso trial→pago.

## 3. Diseño de oferta: trials, paywalls y precios

- **Hard paywall** convierte 5× más descarga→pago a 35 días (10,7 % vs 2,1 %) y genera ~8× RPI a 60 días; la retención anual a 1 año es similar (27 % vs 28 %). [EMPIRICAL — RevenueCat 2026] → para paid social, hard paywall + trial suele dar mejor ROAS medible.
- **Duración del trial**: trials largos convierten más (42,5 % vs 25,5 %) pero retrasan la señal y el cobro; trials ≤ 4 días se imponen (46,5 % de apps). Elegir según el tiempo que necesita el usuario para "ver valor". [EMPIRICAL]
- **Web**: los trials gratuitos convierten peor (fraude, baja intención) → alternativas: paid trial (p. ej. 7 días por 1 $), garantía de devolución, descuento web exclusivo; un único plan anual en web y mensual en app (RevenueCat). [EMPIRICAL]

## 4. Funnels web-to-app (W2A)

### 4.1 Por qué (y por qué no)

| Ventaja | Desventaja |
|---|---|
| Comisión 2–6 % vs 15–30 % | Fricción del paso web → app (descarga, login) |
| Señal rápida y granular (Pixel + CAPI, sin SKAN) → optimización a compra real | Trials gratuitos con más fraude/baja intención |
| Precios, bundles, upsells y tests de pricing libres | Más infraestructura (pagos, impuestos, reembolsos, soporte) |
| Cobro inmediato (vs 45–68 días de tiendas) | Pagos fallidos (~50 %) a recuperar |
| Llega a audiencias distintas (Blinkist: web ~80 % en FB Feed, público mayor y con más disposición a pagar); solapamiento app/web ~15 % | Riesgo de canibalizar búsqueda de marca si se monta mal (RocketShip HQ) |
| Permite campañas de Ventas (objetivo Sales) para app de suscripción | Dos sistemas de medición a reconciliar |

Fuentes: RevenueCat (guía W2A dic-2025/may-2026; Burke abr-2025), Admiral Media (jun-2026), RocketShip HQ. [EMPIRICAL]

**Cuándo W2A suele ganar** (Admiral Media, jun-2026): AOV/precio alto y payback largo, suscripciones de alto LTV, facturación de suscripciones en la UE, usuarios que necesitan quiz/oferta/checkout antes. **Cuándo gana la instalación directa**: precio bajo/impulso, volumen y alcance, monetización rápida. Muchos anunciantes corren ambos (W2A para intención alta, instalación directa para prospección amplia). [EMPIRICAL]

### 4.2 Arquitectura W2A en Meta

1. **Anuncio** → **landing/quiz** (mobile web, rápida, misma promesa que la app) → **paywall web** (Stripe/Paddle/RevenueCat Web Billing; Apple Pay/Google Pay) → **descarga con deep link y auto-login** → app.
2. **Campaña de Ventas** con ubicación de conversión Web, optimizando a **Purchase/Subscribe web** (Pixel + CAPI con `event_id`), con valor = primer cobro o valor neto esperado. Si el volumen es bajo, eventos intermedios (quiz completado, InitiateCheckout) como custom events — RevenueCat envía eventos de interacción del funnel como custom events que **no** se usan para atribución/optimización por defecto. [EMPIRICAL — doc RevenueCat]
3. **Separación**: Blinkist llevaba web y app en cuentas publicitarias distintas (Burke); como mínimo, campañas distintas y deduplicación entre eventos web y app para no contar dos veces al mismo pagador. [EMPIRICAL]
4. **Renovaciones** (y reembolsos) enviadas server-side a Meta para que el valor refleje la realidad; RevenueCat advierte de que enviar la compra 7 días después es delicado para la atribución. [EMPIRICAL]
5. **Medición**: payback ajustado y ARPU/LTV:CAC por cohorte, no tasas de conversión iniciales; test durante 3–6 meses para tener retención; no testear in-app y W2A a la vez con equipos pequeños (RevenueCat). [EMPIRICAL]

### 4.3 El contexto legal en EE. UU. (relevante para "app → web" dentro de la app)

| Fecha | Hecho | Fuente |
|---|---|---|
| 2021 | Injunction: Apple no puede impedir enlaces/botones a compras externas | Apple 10-Q |
| 30-abr-2025 | Desacato: Apple violó la injunction; prohíbe comisión sobre compras fuera de la app y restricciones de estilo/ubicación | Apple 10-Q; Fenwick |
| 3-may-2025 | Apple actualiza las App Review Guidelines: enlaces externos de pago permitidos en el storefront de EE. UU. | Prensa/Wikipedia (secundaria) |
| 11-dic-2025 | Noveno Circuito: confirma desacato; permite a Apple exigir que los enlaces externos no sean más prominentes que sus opciones y cobrar una comisión "razonable" ligada a costes de coordinación (excluyendo costes de seguridad/privacidad); remite al tribunal de distrito | Fenwick; Apple 10-Q |
| Abr-2026 | El Noveno Circuito levanta la suspensión para que avance el remand (secundaria) | Prensa |
| 4-may-2026 | Apple pide al Supremo suspender el mandato; dice que seguirá sin cobrar comisión en compras enlazadas durante la revisión | 9to5Mac |
| 21-may-2026 / 30-jun-2026 | Apple presenta petición; el Supremo **acepta revisar el estándar de desacato civil**, no la comisión | Apple 10-Q (trimestre a 27-jun-2026) |
| 2026 (remand) | Apple propone hasta 15 % para apps estándar (10 % y 5 % en programas) | iClarified (secundaria) |

**Implicaciones** [STRONG INFERENCE]:
- Hoy (oct-2026) una app en EE. UU. puede enlazar al checkout web sin comisión de Apple; eso abarata el "app → web" (usuarios que ya instalaron) y no solo el "web → app" (adquisición desde anuncios).
- No construyas un modelo de negocio que dependa de 0 % de comisión para siempre: modela escenarios 0 %, 10–15 % y 27 %.
- Fuera de EE. UU. (UE con DMA y otros países) las reglas difieren; verificar por mercado (no investigado en detalle aquí). [HYPOTHESIS en detalle]

## 5. Suscripciones en e-commerce (subscribe & save, cajas, réplica)

### 5.1 Datos de contexto (baja-media confianza)

- Recharge (citado por terceros): ~45 % de clientes retenidos a 6 meses y ~33 % a 12 meses (>15.000 comerciantes). [EMPIRICAL vía secundaria]
- Churn mensual: 5–8 % típico en consumo; reposición 3–6 %; cajas de curación 6–12 %; belleza/merchandising 8–15 %; Focus Digital 9,1 % medio en 2025 (100+ negocios). [EMPIRICAL, vendors — discrepantes]
- > 1/3 de suscriptores cancela en 3 meses (McKinsey vía terceros); 20–40 % del churn es involuntario (pagos fallidos). [EMPIRICAL vía secundaria]

### 5.2 Ejemplo trabajado — café de especialidad por suscripción (España)

- Caja mensual 24 € (IVA 10 % incl.) → 21,82 € sin IVA. Primera caja al 50 %: 10,91 € sin IVA.
- Coste producto 7,50 €; envío + preparación 4,50 €; pago 0,50 € → contribución por caja normal = 21,82 − 12,50 = **9,32 €**; primera caja = 10,91 − 12,50 = **−1,59 €**.
- Supervivencia observada (cohorte): pagan caja 2 el 70 %, caja 3 el 58 %, y después churn ~8 %/mes.
- LTV₁₂ (contribución) ≈ −1,59 + 9,32 × (0,70 + 0,58 × Σ_{k=0..9} 0,92^k) = −1,59 + 9,32 × (0,70 + 0,58 × 7,07) = −1,59 + 9,32 × 4,80 = **≈ 43,2 €** (cajas 3 a 12 con churn del 8 %/mes).
- CAC máximo por suscriptor con colchón del 25 %: **~32 €**. Si Meta reporta el "Purchase" de la primera caja (10,91 € sin IVA, 12 € con IVA), un CPA de 30 € equivale a un **ROAS de plataforma de ~0,4** — y aun así es rentable a 12 meses. **Juzgar esta campaña por ROAS de primer pedido sería un error; hay que juzgarla por coste por suscriptor y supervivencia.**
- Sensibilidad: si el descuento del 50 % atrae cazadores de ofertas y la caja 2 cae del 70 % al 50 % (con el resto proporcional), el LTV₁₂ cae a ~30 € y el CAC máximo a ~23 €.

### 5.3 Cómo optimizar en Meta una suscripción e-commerce

- Evento: "Subscribe"/primera compra de suscripción (con valor). Opción avanzada: enviar vía CAPI un **valor predicho** (pLTV) en lugar del valor del primer pedido para VO; requiere modelo validado y consistencia. [STRONG INFERENCE]
- Excluir suscriptores activos de adquisición; campañas de reactivación de cancelados con oferta específica y holdout.
- Comparar ofertas de entrada (50 % primera caja vs regalo vs envío gratis) por **supervivencia a 3 meses**, no por CPA.

## 6. Métricas y umbrales

| Métrica | Por qué | Umbral orientativo |
|---|---|---|
| Coste por trial / por suscriptor | Control diario | ≤ máximos derivados del LTV (§1) |
| Trial → pago por cohorte y placement | Calidad | Comparar con mediana de tu categoría y duración de trial (§3) |
| Cancelación día 0 | Calidad del trial | Si > 30 %, pasar a qualified trial |
| Supervivencia M1/M3/M6/M12 | LTV | Cohortes recientes; alerta si cae > 10 % relativo |
| Reembolsos y pagos fallidos | LTV real | Recuperación de fallidos con reintentos |
| Payback (contable y de caja) | Caja | Explícito por negocio (p. ej. ≤ 6–12 meses) |
| ROAS D7/D30 neto de comisión | Lectura temprana | Calibrar con la curva histórica D7→D365 |

## Implicaciones operativas

- Recalcula el coste por trial/suscriptor máximo cada mes con cohortes recientes; el churn manda.
- Optimiza al evento temprano más predictivo (qualified trial) y valida por placement.
- W2A: empieza simple (mini landing + paywall + deep link), mide 3–6 meses, separa campañas/cuentas y deduplica.
- En EE. UU., aprovecha la ventana sin comisión para app → web, pero modela escenarios de comisión futura.
- En e-commerce de suscripción, evalúa ofertas de entrada por retención, no por CPA.

## Errores frecuentes

- Usar un LTV de 2024 con churn de 2026.
- Optimizar a trial y juzgar por coste por trial sin mirar trial→pago por placement.
- Contar el mismo pagador en web y en app.
- Medir W2A por la tasa de conversión de la landing en vez de por ARPU/LTV:CAC.
- Juzgar suscripciones e-commerce por ROAS del primer pedido con descuento.
- Ignorar pagos fallidos (churn involuntario) como palanca de LTV.

## Preguntas abiertas

- Resultado del Supremo (estándar de desacato) y comisión final que fije el tribunal de distrito en el remand.
- Datos independientes 2025-2026 de conversión y LTV W2A vs in-app en Meta (RevenueCat no publica comparativa directa).
- Reglas de enlaces externos y comisiones bajo la DMA en la UE para W2A (no investigado aquí).
- Benchmarks primarios de Recharge 2025-2026 (cifras citadas de segunda mano).

## Fuentes clave

- [State of Subscription Apps 2026 en 10 minutos (RevenueCat)](https://www.revenuecat.com/blog/growth/subscription-app-trends-benchmarks-2026) — 2026-03-19 — vendor
- [Web-to-app funnels: the complete 2026 guide (RevenueCat)](https://www.revenuecat.com/blog/growth/web-to-app-funnels) — 2025-12-11 (act. 2026-05-01) — vendor
- [Meta Ads in 2025: tips from Marcus Burke (RevenueCat)](https://www.revenuecat.com/blog/growth/meta-ads-in-2025-tips-for-apps) — 2025-04-08 — practitioner
- [Meta Web-to-App vs Direct App Install (Admiral Media)](https://admiral.media/web-to-app-vs-app-install-ads/) — 2026-06-15 — agencia
- [The 12 questions… paid UA for apps (Adapty)](https://adapty.io/blog/meta-ads-subscription-apps/) — 2026-06-22 — practitioner
- [Install, Trial, Subscribe (Airbridge)](https://www.airbridge.io/en/blog/app-event-optimization-subscription-apps) — 2026-03-20 — vendor
- [Ninth Circuit Largely Upholds Ruling in Epic v. Apple (Fenwick)](https://www.fenwick.com/insights/publications/ninth-circuit-largely-upholds-ruling-in-epic-v-apple) — 2025-12-22 — legal
- [Apple Inc. Form 10-Q (trimestre a 27-jun-2026)](https://www.sec.gov/Archives/edgar/data/0000320193/000032019326000020/aapl-20260627.htm) — 2026 — oficial (SEC)
- [Apple files for Supreme Court stay in Epic case (9to5Mac)](https://9to5mac.com/2026/05/04/apple-files-for-supreme-court-stay-in-epic-case-over-off-app-store-commission-dispute/) — 2026-05-04 — prensa
- [Apple seeks court approval for 15% commission (iClarified)](https://www.iclarified.com/101778/apple-seeks-court-approval-for-15-commission-on-external-app-purchases) — 2026 — prensa
- [Epic v. Apple, No. 25-2935 (9th Cir. 2025) (Justia)](https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html) — 2025-12-11 — legal
- [The web-to-app funnel mistake… (RocketShip HQ)](https://www.rocketshiphq.com/web-to-app-funnel-subscription-apps/) — 2025 — practitioner
- [Subscription churn benchmarks (Darkroom / Farabiulder / Focus Digital)](https://www.darkroomagency.com/observatory/subscription-churn) — 2025-2026 — agencia/vendor
