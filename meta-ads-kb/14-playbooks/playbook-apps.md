# Playbook: apps (instalación + eventos de valor) en Meta Ads

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: promoción de apps móviles (iOS/Android) con monetización por compras in-app, suscripción o publicidad. Suscripciones en detalle: `playbook-suscripciones.md`. Base técnica: `06-ecommerce-apps/09-apps-campanas-y-medicion.md`.

## TL;DR

- **Campañas de app 2026 = objetivo App promotion con las tres palancas Advantage+** (presupuesto, audiencia, placements) → estado `ADVANTAGE_PLUS_APP`. Las "Advantage+ app campaigns" legacy (`SMART_APP_PROMOTION`) ya no se crean ni actualizan (v25, todas las versiones desde may-2026) y Meta anunció su pausa con v26 (publicada 29-jul-2026; verificar); se migran (reinicia aprendizaje). [OFFICIAL META]
- **Stack mínimo**: SDK de Meta + MMP (AppsFlyer/Adjust/Branch/Singular…) + eventos server-side (CAPI para App Events o vía MMP/RevenueCat) **con deduplicación**. Meta es self-attributing: el MMP recibe su atribución, no la calcula. [OFFICIAL META]
- **iOS**: AEM para optimizar y leer creatividad casi en tiempo real; SKAN 4 (y AdAttributionKit cuando tu MMP/canales lo soporten) + backend para auditar. Que Meta use AdAttributionKit **no está verificado** en doc oficial. [OFFICIAL META] / [HYPOTHESIS]
- **Evento**: MAI solo para conocer CPI; AEO a un evento que ocurra en ≤ 24–72 h y prediga ingresos; VO/ROAS mínimo con volumen y valores variados. ~50 eventos/ad set/semana para salir de aprendizaje. [OFFICIAL META] + [EMPIRICAL]
- **Economía neta de tienda**: Apple 30 % (15 % SBP/año 2 de suscriptor), Google 15 % en suscripciones; cobro a 45–60+ días. CPI máximo = ingreso neto por pagador × tasa instalación→pago. [EMPIRICAL]

## 1. Cuándo usar Meta

| Sí | Con cautela |
|---|---|
| Apps de consumo masivo (juegos, fitness, idiomas, finanzas personales, IA, compras) | Apps B2B de nicho (mejor Search/LinkedIn) |
| Monetización temprana (día 0–7) o evento proxy fiable | Monetización a meses vista sin proxy |
| Producto que se demuestra en vídeo | Sin SDK/MMP correctamente instalado |
| E-commerce con app (catalog ads con deep links a producto) | Presupuesto < ~€50/día por SO (no hay señal) |

## 2. Arquitectura por presupuesto

| Presupuesto/día | Estructura | Evento | Creatividad | Medición |
|---|---|---|---|---|
| **€100** | 1 campaña por SO prioritario (a menudo Android o iOS-AEM), 1 ad set | Evento temprano de alto volumen (registro cualificado/trial/primera compra) | 4–6 conceptos; 2–3 nuevos/semana | Backend vs Meta (gap ≤ 20 %); CPI y coste por evento |
| **€500** | 2 campañas (iOS / Android) + test creativo | AEO; probar VO si hay compras con valores distintos | 8–12 nuevos/semana; formatos variados | Cohortes D7/D30; SKAN semanal |
| **€5.000** | Por SO y objetivo (AEO y VO en paralelo); catálogo para e-commerce con app; web-to-app si suscripción | AEO + VO/ROAS mínimo | Producción continua (20–40/semana), creadores | Geo-lift/Conversion Lift; reconciliación AEM/SKAN/backend |
| **€50.000** | Portafolio por SO, geo, puja; re-engagement con deep links | VO/ROAS + AEO de volumen | Industrial; localización | Programa de incrementalidad + MMM |

Regla de división: ad sets ≈ eventos de optimización semanales / 50. Separar iOS y Android siempre (medición y economía distintas). [OFFICIAL META] + [STRONG INFERENCE]

## 3. Evento de optimización (árbol)

1. ¿Ingresos en la primera semana? Sí → AEO a primera compra/StartTrial → VO cuando haya volumen. No → evento de activación validado con cohortes.
2. ¿≥ 50 eventos/ad set/semana? No → subir un nivel en el embudo o consolidar.
3. ¿El evento ocurre en ≤ 24–72 h? No → proxy anterior (Meta y la ventana 1 de SKAN no lo verán a tiempo).
4. ¿Correlaciona con ingresos a 30–90 días? Validar antes de escalar.
5. ¿Monetización por publicidad? Enviar `AdImpression` con valor (SDK, CAPI o MMP) y optimizar a valor. [OFFICIAL META — guía ago-2025]

## 4. Creatividades

- Mostrar la app en uso (pantalla real) + resultado para el usuario.
- Gameplay real (juegos) y "fail/win" hooks; comparativas; text-wall/infografías; UGC en formatos nuevos (Burke).
- Formatos separados si quieres controlar entrega: los estáticos tienden a Facebook Feed (Burke).
- Localización por idioma/mercado.
- Evaluar por placement y audiencia, no solo por "mejor anuncio".

## 5. Funnel

Anuncio → store (o landing en W2A) → instalación → primer arranque (consentimiento ATT en iOS) → onboarding → evento de valor (registro, trial, compra) → retención/monetización → re-engagement (deep links; AdAttributionKit contempla re-engagement en iOS 18+, uso en Meta no verificado).

## 6. Métricas y umbrales

| Métrica | Regla |
|---|---|
| CPI | Solo diagnóstico; nunca objetivo único |
| Coste por evento AEO | ≤ (ingreso neto por pagador × tasa evento→pago) |
| ROAS D7/D30 neto de comisión | Calibrado con la curva histórica D7→D180 de tus cohortes |
| Gap Meta vs backend/MMP | 10–20 % normal; > 20–30 % → revisar SDK/CAPI/dedup |
| Volumen para comparar campañas iOS | ≥ 200 instalaciones/semana; diferencias ≤ 100 instalaciones = ruido; esperar ~72 h tras cambios (Segwise) |
| Escalado | +~20 % cada 1–3 días tras 3–7 días estables; con ROAS ~101 % no hay margen para escalar (Adapty) |

## 7. Errores frecuentes

- Escalar instalaciones baratas sin mirar pagos.
- Doble conteo (SDK + CAPI sin `event_id`; SDK de Meta + RevenueCat enviando la misma compra).
- Varias librerías actualizando conversion values de SKAN.
- Decidir con datos SKAN de menos de 3 días.
- ROAS con ingresos brutos (antes de la comisión de Apple/Google).
- Tratar postbacks sin valor como ingresos cero.
- Mantener AAC legacy sin migrar hasta que Meta las pause (anunciado para v26).

## 8. Ejemplo numérico completo

**App de fitness, iOS, EE. UU.** Plan anual 59,99 $ (Small Business Program: 15 %) → neto 50,99 $; reembolsos 5 % → **48,44 $ por pagador** (primer año).

- Instalación→trial 12 %; trial→pago 40 % → instalación→pago **4,8 %**.
- **CPI máximo** (payback 12 meses solo con el primer cobro) = 48,44 × 0,048 = **2,33 $**.
- **Coste por trial máximo** = 48,44 × 0,40 = **19,38 $**.
- Con colchón del 20 % para riesgo de cohortes: CPI objetivo **1,86 $**, coste por trial objetivo **15,50 $**.

**Semana real (ilustrativa)**: gasto 7.000 $; Meta (AEM) reporta 480 trials (14,58 $/trial); backend registra 520 trials atribuibles a la campaña por encuesta + MMP (gap 8 %, normal). A 40 % de conversión → ~192–208 pagadores → CAC por pagador 33,7–36,5 $ frente a un máximo de 48,44 $ → **rentable en el primer cobro**; escalar +20 % y vigilar que trial→pago no caiga por placement.

**Si la conversión trial→pago cae al 30 %** (p. ej. al escalar a placements de menor calidad): CAC por pagador = 14,58 / 0,30 = 48,6 $ → **break-even** → frenar escalado y separar creatividades por formato para controlar entrega.

## Fuentes clave

- [Advantage+ Campaigns (APP_INSTALLS)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
- [Conversions API for App Events](https://developers.facebook.com/docs/marketing-api/conversions-api/app-events) — Meta for Developers — meta-developers
- [AEM for iOS apps](https://developers.facebook.com/docs/app-events/guides/aggregated-event-measurement) — Meta for Developers — meta-developers
- [App Events: maximize in-app ad revenue](https://developers.facebook.com/documentation/app-events/guides/maximize-in-app-ad-revenue) — 2025-08 — meta-developers
- [What's new in AdAttributionKit (WWDC25)](https://developer.apple.com/videos/play/wwdc2025/221/) — 2025 — Apple
- [Meta AEM vs SKAN in 2026 (Segwise)](https://segwise.ai/blog/meta-aem-vs-skan-2025-ios-attribution) — 2026-04 — vendor
- [Meta Ads in 2025 (RevenueCat/Burke)](https://www.revenuecat.com/blog/growth/meta-ads-in-2025-tips-for-apps) — 2025-04-08 — practitioner
- [Paid UA for apps (Adapty)](https://adapty.io/blog/meta-ads-subscription-apps/) — 2026-06-22 — practitioner
