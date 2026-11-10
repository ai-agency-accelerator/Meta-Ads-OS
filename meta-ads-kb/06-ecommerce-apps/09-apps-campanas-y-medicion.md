# Apps en Meta: Advantage+ app campaigns, SDK/App Events, AEO/VO y medición iOS (AEM, SKAN, AdAttributionKit) con MMPs

> Última verificación: 2026-10-15 · Autor: A06 (agente) · Ámbito: campañas de promoción de apps en Meta en 2026 (instalación y eventos posteriores), instrumentación (SDK, App Events, CAPI para apps, MMP), medición iOS post-ATT y elección del evento de optimización. Suscripciones y web-to-app en `10-…`.

## TL;DR

- **"Advantage+ app campaigns" (AAC) legacy desaparece igual que ASC**: la creación y actualización con `SMART_APP_PROMOTION` está bloqueada desde v25 (18-feb-2026; en todas las versiones antes del 19-may-2026) y el post oficial de v25 anunciaba que las AAC restantes se **pausarían con v26** (publicada 29-jul-2026; pausa prevista sep-2026, no confirmada en el changelog de v26). Ahora una campaña con objetivo `APP_INSTALLS` es "Advantage+" (`ADVANTAGE_PLUS_APP`) cuando tiene presupuesto, audiencia y placements Advantage+. Las AAC se pueden migrar pero no "copiar y migrar". [OFFICIAL META]
- **Instala SDK de Meta + MMP + (opcional) CAPI para App Events, sin duplicar.** Meta es un *self-attributing network*: el MMP recibe su atribución vía API, no "atribuye" Meta por sí mismo. CAPI para App Events permite enviar eventos server-side a un dataset vinculado a la app (una app por dataset) y requiere deduplicar por `event_id` + `event_name`. [OFFICIAL META]
- **iOS en 2026 = tres capas que no cuadran entre sí**: (1) **AEM para apps** de Meta (modelado, agregado, rápido; por defecto en la mayoría de apps de suscripción desde 2024-2025; Meta envía señal AEM a MMPs desde el 9-oct-2024), (2) **SKAdNetwork 4** (postbacks firmados de Apple, 3 ventanas 0–2/3–7/8–35 días, retrasos aleatorios, umbrales de privacidad) y (3) **AdAttributionKit** (sucesor de Apple desde iOS 17.4, re-engagement desde iOS 18). **No he podido confirmar en documentación de Meta que Meta optimice o reporte con AdAttributionKit**; un blog de 2026 lo afirma. [OFFICIAL META] (AEM/SKAN) / [HYPOTHESIS] (AAK en Meta)
- **Evento de optimización**: instalaciones (MAI) solo para aprender el CPI; para negocio, **AEO a un evento que ocurra en ≤ 24–72 h y prediga ingresos** (registro cualificado, trial cualificado, primera compra) y **VO/ROAS** cuando haya volumen de compras con valores variados. Meta necesita ~50 eventos/ad set/semana para salir de aprendizaje. [OFFICIAL META] (50) + [EMPIRICAL] (practitioners)
- **Umbrales de VO que circulan** (≥ 30 compras con ≥ 5 valores distintos en 14 días; o 50–100 compras/semana por ad set para que VO supere a AEO) **no están confirmados en doc oficial** y difieren entre fuentes. [CONTESTED]
- **Por presupuesto (Marcus Burke, RevenueCat, abr-2025)**: 0–20k $/mes → arreglar setup (que Meta vea los trials: casos con solo ~10 % atribuidos); 20–100k → grandes apuestas creativas; 100–500k → diversificar placements/audiencias, experimentos de pricing/onboarding y web-to-app. [EMPIRICAL]
- **Economía de app ≠ e-commerce**: comisión de Apple 30 % (15 % Small Business Program o tras el primer año del suscriptor), Google Play 15 % en suscripciones desde el día 1; cobros a 45–60+ días. El ROAS objetivo se calcula sobre ingresos **netos de tienda**. [EMPIRICAL — Adapty; RevenueCat]
- **Brecha normal entre fuentes**: 10–20 % entre Meta y MMP/backend es normal; más indica problema de eventos, CAPI o deduplicación (Adapty). Usa AEM para pacing diario y SKAN/backend para auditoría semanal (Segwise). [EMPIRICAL]

## 1. Estado de las campañas de app en Meta (2026)

| Elemento | Estado | Etiqueta |
|---|---|---|
| Objetivo | Promoción de la app (`APP_INSTALLS` en API) | [OFFICIAL META] |
| Advantage+ | Estado `ADVANTAGE_PLUS_APP` con 3 palancas activas (presupuesto de campaña, Advantage+ audience o solo geo o relajación, placements sin exclusiones a nivel ad set) | [OFFICIAL META] |
| AAC legacy (`SMART_APP_PROMOTION`) | Creación/actualización bloqueadas (v25, todas las versiones antes del 19-may-2026); pausa de las restantes anunciada para v26 (prevista sep-2026; verificar); migración disponible (no copy+migrate) | [OFFICIAL META] |
| Optimización | Instalaciones, eventos de app (AEO), valor (VO), con estrategias lowest cost, cost cap, bid cap, ROAS mínimo | [OFFICIAL META] (estrategias en Advantage+); [EMPIRICAL] (uso) |
| Placements | Retirada de controles de placement a nivel ad set también en App promotion (~ago-2026); exclusiones a nivel cuenta y value rules | [OFFICIAL META vía Help Center citado por terceros] |
| Value rules | Disponibles en objetivos Ventas y App promotion (jun-2025); desde nov-2025 pueden incluir la ubicación de conversión (web, app, formulario) | [EMPIRICAL] |
| Catalog ads para apps | Advantage+ catalog ads con deep links a producto en app (e-commerce con app) | [OFFICIAL META] |
| Limitaciones históricas SKAN | Doc de Meta: por App ID, 9 campañas SKAN repartidas en hasta 9 cuentas y 5 ad sets; no editar el objeto promocionado una vez lanzado; una app no puede promocionarse con campañas SKAN en más de una cuenta a la vez | [OFFICIAL META — página antigua, puede estar desactualizada] |

**Implicación**: igual que en e-commerce, las palancas del anunciante son evento, creatividad, producto (onboarding/paywall) y medición; la estructura se simplifica.

## 2. Instrumentación correcta (orden de prioridades)

1. **SDK de Meta (iOS/Android)** actualizado, con App Events estándar: `fb_mobile_activate_app` (instalación/aperturas), registro, `StartTrial`, `Subscribe`, `Purchase` (con valor y divisa), y para apps con publicidad `AdImpression` con valor (guía de Meta de ago-2025 para ingresos publicitarios vía SDK, CAPI o MMP). [OFFICIAL META]
2. **Universal Links / deep linking** configurados (requisito de AEM en iOS). [OFFICIAL META]
3. **MMP** (AppsFlyer, Adjust, Branch, Singular, Airbridge, Tenjin) con la integración de Meta activada: el MMP reporta la vista de todos los canales; Meta le comparte su atribución (y AEM desde oct-2024). [OFFICIAL META + EMPIRICAL]
4. **Eventos server-side** (CAPI para App Events, directamente o vía MMP/RevenueCat) para renovaciones, conversiones trial→pago y reembolsos que ocurren fuera de la app. Dataset vinculado a la app (1 app por dataset); deduplicación `event_id` + `event_name` si el mismo evento llega por SDK y CAPI. [OFFICIAL META]
5. **Una sola fuente por evento**: RevenueCat recomienda desactivar el tracking de compras del SDK de Meta si las mismas compras se envían server-to-server, para no contar doble. [EMPIRICAL — doc RevenueCat]
6. **Validación**: comparar trials/compras que ve Meta con backend y con encuesta in-app ("¿cómo nos conociste?"). Burke: con < 20k $/mes, la prioridad es que no falte el 40–50 % de los trials en Meta; documentó un caso con solo ~10 % atribuidos. [EMPIRICAL]

## 3. Medición iOS post-ATT: AEM, SKAN y AdAttributionKit

### 3.1 Comparativa

| | AEM para apps (Meta) | SKAdNetwork 4 (Apple) | AdAttributionKit (Apple) |
|---|---|---|---|
| Qué es | Protocolo de Meta para medir eventos de usuarios iOS 14.5+ que no dan consentimiento; agregado y modelado | Framework de atribución de instalaciones con postbacks firmados | Sucesor de SKAN (iOS 17.4+), postbacks firmados, también en marketplaces alternativos |
| Latencia | Horas | Ventanas 0–2, 3–7, 8–35 días + retraso aleatorio (0–24 h y más); la última puede llegar tras el día 41 | Mismas ventanas de instalación que SKAN 4 |
| Granularidad | Nivel anuncio/creatividad (reporting en tiempo casi real) | Campaña; conversion values fine/coarse sujetos a "crowd anonymity" | Igual; re-engagement (iOS 18+) con hasta 3 postbacks, solo clic |
| Ventanas | Burke: 7 días post-clic | — | Clic 30 días; view-through 24 h (≥ 2 s) |
| Configuración en Meta | `campaign_attribution = AEM` en el ad set | `campaign_attribution = SKADNETWORK` | **No documentado por Meta (no verificado)** |
| Uso real 2025-2026 | Mayoría de apps de suscripción (Burke, abr-2025) | Auditoría/reconciliación | Adopción incipiente; requiere MMP compatible |

Fuentes: Meta for Developers (AEM, SKAN y limitaciones), Apple WWDC24/25, Admiral Media (may-2026), Segwise (jun-2025, act. abr-2026), RevenueCat (jun-2024). [OFFICIAL META/Apple + EMPIRICAL]

### 3.2 Reglas prácticas

- **AEM para el día a día** (pacing, creatividad), **SKAN/AAK + backend para auditoría semanal** y reconciliación de cohortes maduras. [EMPIRICAL — Segwise]
- **Volumen mínimo para leer diferencias**: Segwise sugiere comparar campañas con 200+ instalaciones/semana y tratar diferencias ≤ 100 instalaciones como ruido; esperar ~72 h tras lanzar/parar antes de decidir. [EMPIRICAL, vendor]
- **No trates un postback sin valor como "0 €"**: en niveles bajos de anonimato Apple omite el valor (Admiral Media). [EMPIRICAL]
- **Una sola fuente llama a `updateConversionValue`** (SDK de Meta, MMP u otro), nunca varias. [EMPIRICAL — Branch]
- **Mapping de conversion values**: ventana 1 (0–2 días) con eventos tempranos que predigan valor (trial, registro cualificado, primera compra por tramos); ventanas 2–3 con coarse values (pago, renovación). Valida que el canal admite pujar a ese valor antes de diseñar el esquema. [EMPIRICAL]
- **Un caso citado (Segwise, feb-2025)**: en una campaña de trials, SKAN dio 49 $ de coste por trial frente a 71 $ con AEM en 14 días → no asumas que AEM siempre gana; pruébalo. [EMPIRICAL, caso único]

### 3.3 Android

Atribución determinista vía Install Referrer de Google Play y del propio Meta, sin equivalente ATT; señal más rica y rápida que iOS. Por eso muchas apps escalan antes en Android y usan iOS con AEM. [STRONG INFERENCE] (No he verificado el estado 2026 de Privacy Sandbox en Android.)

## 4. Elegir el evento de optimización

### 4.1 Árbol de decisión

1. **¿Ingresos dentro de la app en los primeros días?**
   - No (freemium, monetización tardía) → AEO a un evento proxy temprano que correlacione con retención/pago (registro completado + acción clave; "qualified trial").
   - Sí → AEO a primera compra/StartTrial; VO cuando haya volumen y valores variados.
2. **¿Volumen ≥ 50 eventos/ad set/semana?** No → sube un nivel en el embudo o consolida ad sets. [OFFICIAL META — umbral de aprendizaje]
3. **¿El evento ocurre en ≤ 24–72 h desde la instalación?** No → Meta (y SKAN ventana 1) no lo ve a tiempo; usa un proxy anterior. Burke: Meta necesita la señal idealmente en ~24 h. [EMPIRICAL]
4. **¿El evento correlaciona con ingreso a 30–90 días?** Valídalo con cohortes antes de comprometer presupuesto.

### 4.2 Install (MAI) vs downstream

| Optimización | Pros | Contras | Cuándo |
|---|---|---|---|
| Instalaciones (MAI) | CPI bajo, volumen, aprendizaje rápido | Usuarios de baja calidad; poco predictivo de ingresos | Lanzamiento, apps con monetización por publicidad muy masiva, para estimar CPI |
| AEO (evento) | Calidad; alinea con negocio | CPI mayor; necesita volumen | Por defecto en apps con monetización |
| VO / ROAS mínimo | Prioriza usuarios de alto valor | Requiere volumen y varianza de valores; resultados más volátiles | Apps con compras de valores distintos (juegos, e-commerce con app) o suscripciones con planes |

Adapty (jun-2026): empezar con instalaciones para conocer CPI, pasar a compras y luego a valor; tROAS/VO/cost cap pueden convivir pero objetivos agresivos no gastan. [EMPIRICAL]

### 4.3 "Qualified trial" (suscripciones)

Airbridge (mar-2026) propone enviar "Qualified Trial" con un retraso de 2–4 h que filtra cancelaciones impulsivas (RevenueCat: 55,4 % de las cancelaciones de trials de 3 días ocurren el día 0 y el 84 % entre el día 0 y 1). Ejemplo: 200 trials/semana y 70 suscriptores en 4 ad sets → ~17 Subscribe/ad set/semana (insuficiente); un Qualified Trial que filtra ~30 % da ~140 eventos/semana, suficiente para 2–3 ad sets. Adapty: si la cancelación de trial > 30 %, envía el evento solo de quien no ha cancelado. [EMPIRICAL]

## 5. Arquitectura por presupuesto (apps)

| Gasto mensual | Prioridad | Estructura |
|---|---|---|
| < 20k $/€ | Setup: SDK + MMP + eventos; que Meta vea ≥ 80–90 % de trials/compras | 1 campaña Advantage+ app por SO (iOS AEM / Android), 1 ad set, AEO a trial/compra; 5–10 creatividades |
| 20–100k | Grandes apuestas creativas (formatos, estilos, mensajes), no micro-tests | 1–2 campañas por SO; test creativo separado; evaluar por placement y audiencia, no solo por "mejor anuncio" (Burke) |
| 100–500k | Diversificación: placements, audiencias, pricing/onboarding, web-to-app (Burke: para pasar de ~500k probablemente hacen falta flujos web y app) | Campañas por SO y objetivo (AEO y VO en paralelo), web-to-app en cuenta/campaña separada (Blinkist lo separó en otra cuenta; la web entregó ~80 % en Facebook Feed a público mayor) |
| > 500k | Medición incremental + MMM; geos; creatividad industrial | Programa de tests (geo-lift), portafolio de pujas |

[EMPIRICAL — RevenueCat/Burke; Adapty]

Escalado (Adapty): escalar cuando el rendimiento es estable 3–7 días con varias creatividades; subidas de ~20 % cada 1–3 días; a ROAS ~101 % casi no hay margen para escalar; a 200 % se puede tolerar bajar a 150 %. [EMPIRICAL]

## 6. Economía de apps: fórmulas y ejemplo

- **Ingreso neto** = bruto × (1 − comisión tienda) × (1 − IVA si aplica en precio) − reembolsos.
- Comisiones: Apple 30 % estándar, 15 % (Small Business Program o tras el primer año de un suscriptor); Google Play 15 % en suscripciones desde el día 1. [EMPIRICAL — Adapty, jun-2026]
- **CAC objetivo por pagador** = LTV neto (en contribución) en el horizonte de payback aceptado.
- **CPI máximo** = CAC por pagador × tasa instalación→pago.

**Ejemplo** (app de fitness iOS, EE. UU.):
- Plan anual 59,99 $; neto tras 15 % (Small Business) = 50,99 $; reembolsos 5 % → 48,44 $ por pagador en año 1 (sin renovaciones).
- Instalación → trial 12 %; trial → pago 40 % → instalación → pago 4,8 %.
- Para payback en 12 meses solo con el primer cobro: CAC por pagador ≤ 48,44 $ → **CPI máximo = 48,44 × 0,048 = 2,33 $**; **coste por trial máximo = 48,44 × 0,40 = 19,38 $**.
- Si en vez de anual es semanal (2,99 $/semana) y la retención decae, el payback depende de la curva; Adapty pone el ejemplo de CAC 10 $ con suscripción de 3 $/semana → break-even en 4–5 semanas tras comisión.

Cash flow: Apple paga ~45 días tras el cierre del mes fiscal; Google Play hacia el día 15 del mes siguiente → un payback "contable" de 30 días puede ser de 75 días de caja. [EMPIRICAL — Adapty]

Benchmarks de conversión (RevenueCat, SOSA 2026, >115.000 apps): trial→pago mediano 42,5 % (trials 17–32 días), 37,4 % (5–9 días), 25,5 % (≤ 4 días); descarga→pago a 35 días 10,7 % en hard paywall vs 2,1 % freemium; RPI a 60 días 3,09 $ vs 0,38 $. [EMPIRICAL] Ver `10-…`.

## Implicaciones operativas

- Si tienes AAC legacy activas, migra fuera de picos (la migración reinicia aprendizaje).
- Antes de gastar: auditar que Meta ve ≥ 80–90 % de los eventos clave (comparar con backend).
- Elegir un evento temprano y predictivo; consolidar ad sets hasta tener ~50 eventos/semana.
- Separar iOS y Android (medición y economía distintas).
- AEM para optimizar; SKAN/AAK + backend + cohortes para decidir presupuesto.
- Calcular CPI/coste por trial máximos desde LTV neto de comisión y reembolsos.

## Errores frecuentes

- Optimizar a instalaciones por "CPI barato" y escalar sin mirar pagos.
- Enviar el mismo evento por SDK y CAPI sin `event_id` (doble conteo) o por SDK de Meta y por RevenueCat a la vez.
- Varias librerías llamando a `updateConversionValue`.
- Evaluar campañas iOS a 24 h con SKAN (los postbacks no han llegado).
- Usar ingresos brutos (antes de comisión de Apple/Google) en el ROAS.
- Tratar postbacks sin valor como cero ingresos.

## Preguntas abiertas

- ¿Usa Meta AdAttributionKit (postbacks, re-engagement) para reporting u optimización? No hay doc oficial de Meta localizada; un blog 2026 dice que sí.
- Umbrales oficiales actuales de elegibilidad para VO en apps.
- Vigencia de los límites de campañas SKAN de la página antigua de Meta.
- Efecto de la retirada de controles de placement (2026) en apps que excluían Audience Network.

## Fuentes clave

- [Advantage+ Campaigns (APP_INSTALLS, migración AAC)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
- [Aggregated Event Measurement for iOS apps](https://developers.facebook.com/docs/app-events/guides/aggregated-event-measurement) — Meta for Developers — meta-developers
- [AEM and limitations of SKAdNetwork](https://developers.secure.facebook.com/documentation/app-ads/SKAdNetwork-aem-and-limitations) — Meta for Developers — meta-developers
- [Conversions API for App Events](https://developers.facebook.com/docs/marketing-api/conversions-api/app-events) — Meta for Developers — meta-developers
- [App Events: maximize in-app ad revenue](https://developers.facebook.com/documentation/app-events/guides/maximize-in-app-ad-revenue) — 2025-08 — meta-developers
- [Meet AdAttributionKit (WWDC24)](https://developer.apple.com/videos/play/wwdc2024/10060/) y [What's new in AdAttributionKit (WWDC25)](https://developer.apple.com/videos/play/wwdc2025/221/) — Apple — oficial Apple
- [AdAttributionKit: post-SKAN playbook (Admiral Media)](https://admiral.media/adattributionkit-ios-measurement-playbook/) — 2026-05-22 — agencia
- [Meta AEM vs SKAN in 2026 (Segwise)](https://segwise.ai/blog/meta-aem-vs-skan-2025-ios-attribution) — 2025-06 (act. 2026-04) — vendor
- [Meta Ads in 2025: tips from Marcus Burke (RevenueCat)](https://www.revenuecat.com/blog/growth/meta-ads-in-2025-tips-for-apps) — 2025-04-08 — practitioner
- [The 12 questions I get asked most about paid UA for apps (Adapty)](https://adapty.io/blog/meta-ads-subscription-apps/) — 2026-06-22 — practitioner
- [Install, Trial, Subscribe: which event to send (Airbridge)](https://www.airbridge.io/en/blog/app-event-optimization-subscription-apps) — 2026-03-20 — vendor (MMP)
- [Meta Ads integration (RevenueCat docs)](https://www.revenuecat.com/docs/integrations/attribution/meta-ads) — 2025-2026 — vendor
- [Meta & iOS 14 FAQ (Branch)](https://help.branch.io/marketer-hub/docs/meta-ios-faq) — 2021 (histórico) — vendor (MMP)
- [AdAttributionKit: what is it (RevenueCat)](https://www.revenuecat.com/blog/growth/adattributionkit-what-is-it) — 2024-06-25 — vendor
