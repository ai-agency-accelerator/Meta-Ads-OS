# Medición de apps: Meta SDK, App Events, SKAdNetwork/AdAttributionKit, AEM, MMPs y CAPI para apps

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: tracking técnico de campañas de app (instalaciones y eventos in-app) en iOS y Android. La estrategia de campañas de app la cubre el área 06; aquí, señales, frameworks de atribución y su estado 2025–2026.

## TL;DR

- **Tres vías de señal para apps:** (1) **Meta SDK** (App Events) en la app; (2) **MMP** (AppsFlyer, Adjust, Branch, Singular…) que reenvía eventos a Meta; (3) **Conversions API para app events** (`action_source=app`, servidor a servidor, dataset vinculado a una única app). Deduplican entre sí con `event_id` + `event_name`; las instalaciones se deduplican solas (Meta conserva la primera en 90 días). [OFFICIAL META] ([S04-044])
- **iOS:** ATT (opt-in medio global ~38 % en Q1-2026 según Adjust). Para usuarios sin ATT, Meta ofrece **AEM para apps** (vía SDK, con Universal Links/deep links) o **SKAdNetwork** (postbacks de Apple). En la API, cada ad set iOS 14+ declara `campaign_attribution = AEM` o `SKADNETWORK`. [OFFICIAL META] ([S04-043], [S04-071]) + [EMPIRICAL] ([S04-076])
- **SKAN 4.0 en Meta:** activación gradual con toggle en Events Manager (Data sources > Settings > Apple's SKAdNetwork > extra settings); nuevo empuje detectado en jun-2025 tras intentos en 2023–2024. **AdAttributionKit:** soporte de Meta afirmado por fuentes secundarias en 2026, **no verificado** en documentación oficial. [EMPIRICAL] ([S04-110]) + [HYPOTHESIS] (AAK)
- **SDK iOS ≥ 17 en iOS ≥ 17:** ya no hace falta `setAdvertiserTrackingEnabled`; el SDK lee el estado ATT del sistema (el setter está deprecado). En CAPI para apps sigue siendo obligatorio enviar `advertiser_tracking_enabled` (0/1). [OFFICIAL META] ([S04-072], [S04-044])
- **MMPs:** Meta **reactivó el 17-jun-2025 el reporting de Advanced Mobile Measurement (AMM)**: aceptando los términos AMM por app, el MMP accede a datos de atribución a nivel de dispositivo de Meta. En Android, el *Install Referrer* de Google Play (con clave de descifrado de Meta) y el *Meta install referrer* (`fb_referrer`, `ig_referrer`, clics e impresiones) enriquecen la atribución. [EMPIRICAL] (docs de AppsFlyer/Singular, [S04-046])
- **AEM para apps vs SKAN (según MMP):** con AEM, la campaña se mide con SKAN + datos adicionales y el rendimiento se ve en Ads Manager; ventana de atribución AEM fija de 1 día según Airbridge. [EMPIRICAL] ([S04-045])
- **La documentación de Meta sobre límites de campañas iOS 14 (9 campañas/5 ad sets por app, 8 eventos AEM) es legada** y convive con prácticas más nuevas; verifica en la interfaz antes de diseñar estructuras. [OUTDATED/CONTESTED] ([S04-071])

## 1. Arquitectura de señales en apps

```
App (Meta SDK y/o MMP SDK) ──► eventos in-app (fb_mobile_purchase, fb_mobile_complete_registration…)
        │                         │
        │                         └─► MMP ──► Meta (integración SRN / postbacks)
        │
Backend ──► CAPI (action_source=app, app_data.extinfo, advertiser_tracking_enabled, anon_id/madid)
        │
iOS (sin ATT) ──► SKAdNetwork/AdAttributionKit postbacks (Apple) ──► Meta / MMP
                   AEM (Meta) vía SDK + Universal Links
Android ──► Google Play Install Referrer (+ Meta install referrer) ──► MMP/Meta
```

### 1.1 CAPI para app events (requisitos clave)
- Dataset vinculado a la app (solo una app por dataset); dataset consolidado (`is_consolidated_container`). [OFFICIAL META] ([S04-044])
- Obligatorios: `action_source: "app"`, `event_id`, `app_data.advertiser_tracking_enabled` (0/1, iOS 14.5+), `app_data.extinfo` (array ordenado de 16 posiciones; `a2` Android / `i2` iOS en la posición 0; versión de SO en la 4; vacíos como `""`). Opcionales: `application_tracking_enabled`, `campaign_ids` (cadena cifrada del deep link, usada en AEM de apps), `install_referrer`, `installer_package`, `vendor_id`… [OFFICIAL META] ([S04-044])
- `user_data`: `anon_id` (install ID) y `madid` (IDFA/GAID) **sin hash**; email/teléfono hasheados; `client_ip_address` sin hash. [OFFICIAL META] ([S04-044])
- EMQ no disponible para app events (consultar con representante). [OFFICIAL META] ([S04-016])

```json
{
  "data": [{
    "event_name": "Purchase",
    "event_time": 1760610000,
    "event_id": "iap_9c1f2e",
    "action_source": "app",
    "user_data": {
      "madid": "AECE52E7-03EE-455A-B3C4-E57283966239",
      "anon_id": "XZ1234567890",
      "client_ip_address": "2a01:4f8::1",
      "em": ["<sha256>"]
    },
    "custom_data": { "currency": "EUR", "value": 9.99 },
    "app_data": {
      "advertiser_tracking_enabled": 1,
      "application_tracking_enabled": 1,
      "extinfo": ["i2","com.ejemplo.app","771","7.7.1","18.5","iPhone16,2","es_ES","CEST","","1290","2796","3.0","6","","","Europe/Madrid"]
    }
  }]
}
```
(Valores ficticios; estructura según la documentación de Meta.) [OFFICIAL META] ([S04-044])

### 1.2 Eventos de app
- Usa los eventos estándar de app (`fb_mobile_purchase`, `fb_mobile_add_to_cart`, `fb_mobile_complete_registration`, `fb_mobile_level_achieved`…); en CAPI los parámetros de app llevan prefijo `fb_` y `value` se mapea a `_valueToSum`. [OFFICIAL META] ([S04-037])
- Para Custom Attribution (AppendAttribution) en apps, el evento original debe ser `fb_mobile_purchase`, no `Purchase`. [OFFICIAL META] ([S04-052])

## 2. iOS: ATT, SKAdNetwork, AdAttributionKit y AEM

### 2.1 ATT
- Opt-in: ~38 % global Q1-2026 (Adjust), ~35 % Q1-2025; AppsFlyer ~50 % (vía secundaria); cifras muy dependientes de vertical y región. [EMPIRICAL] ([S04-076])
- SDK de Meta ≥ 17 en iOS ≥ 17: estado ATT leído del sistema; `setAdvertiserTrackingEnabled` deprecado. [OFFICIAL META] ([S04-072])

### 2.2 SKAdNetwork (SKAN)
- Postbacks agregados de Apple, con umbrales de privacidad (*crowd anonymity*): por debajo de cierto volumen solo llegan valores *coarse* (low/medium/high) o ninguno. SKAN 4: tres ventanas de postback; solo la primera puede llevar el valor fino (0–63); `lockWindow` permite cerrar antes. [EMPIRICAL] ([S04-110])
- Meta: configuración del esquema de valores de conversión en Events Manager; breakdowns SKAN en Insights (`skan_conversion_id`, `skan_campaign_id`, `is_conversion_id_modeled` — Meta indica si los `conversion_bits` son modelados). [OFFICIAL META] ([S04-051])
- Requisitos (doc. legada de Meta): `user_os` ≥ iOS 14 en el ad set, objeto promocionado obligatorio, SDK de Meta ≥ v8.0, sin TARGET_COST, sin facturación CPA de installs, no se puede editar el objeto promocionado ni el flag SKAN con la campaña activa; las consultas que mezclan campañas iOS 14 y no-iOS 14 no devuelven métricas de conversión no-inline. [OFFICIAL META] ([S04-071]) — algunos límites pueden haber cambiado; verificar.

### 2.3 AdAttributionKit (AAK)
- Sucesor de SKAN (iOS 17.4), con re-engagement (iOS 18) y, desde WWDC25/iOS 18.4, ventanas de conversión superpuestas para re-engagement, ventanas de atribución y *cooldowns* configurables por red/tipo de anuncio, código de país en postbacks (en contextos limitados, p. ej. tiendas alternativas en la UE) y herramienta de pruebas en Ajustes. [EMPIRICAL] ([S04-111])
- **Meta y AAK:** soporte afirmado por guías de 2026; no encontrado en documentación oficial de Meta. [HYPOTHESIS]

### 2.4 AEM para apps
- Mide eventos de usuarios iOS 14.5+ que no autorizaron tracking; requiere Universal Links y pasar el deep link al SDK (`ApplicationDelegate.shared.application(_:continue:)` en SDK ≥ 14.0.0; también en `SceneDelegate`). [OFFICIAL META] ([S04-043])
- Según MMPs: AEM es la selección por defecto si la app es elegible; con AEM la medición combina SKAN y datos adicionales; ventana AEM fija de 1 día (Airbridge). [EMPIRICAL] ([S04-045])

## 3. Android
- **Google Play Install Referrer:** Meta comparte metadatos de campaña cifrados; el MMP los descifra con la "Install Referrer decryption key" (App Dashboard de Meta > Settings > Basic). [EMPIRICAL] (AppsFlyer, [S04-046])
- **Meta install referrer:** datos de clic e impresión que pueden abarcar varias sesiones (`fb_referrer`, `ig_referrer`); requiere SDK de MMP reciente (AppsFlyer ≥ 5.4). [EMPIRICAL] ([S04-046])
- **GAID / Privacy Sandbox on Android:** el calendario de retirada del GAID se ha retrasado repetidamente; no se encontró confirmación primaria de una retirada en 2025–2026. [HYPOTHESIS] — vigilar anuncios de Google.

## 4. MMPs y datos a nivel de dispositivo
- **Restricción desde 29-oct-2021:** los datos de atribución a nivel de usuario de Meta se comparten con MMPs pero no con anunciantes (salvo aceptación de términos). [EMPIRICAL] ([S04-046])
- **AMM reactivado 17-jun-2025:** aceptar los términos de Advanced Mobile Measurement por app ID en la configuración de Meta permite al MMP acceder a datos de atribución a nivel de dispositivo de Meta. [EMPIRICAL] ([S04-046])
- **Discrepancias Meta vs MMP:** distintas ventanas (Meta 1d view/7d click vs ventanas del MMP), atribución SKAN/AEM vs determinista, modelado, reinstalaciones (Meta: primera install en 90 días). Reconciliar como en archivo 11. [STRONG INFERENCE]

## Implicaciones operativas

- **Hacemos:** decidir una fuente primaria de eventos por app (SDK de Meta o MMP o CAPI) y deduplicar con `event_id` si hay varias; esquema SKAN/valores coherente con el evento de optimización; aceptar AMM si el MMP lo necesita (revisión legal); medir incrementalidad de app con experimentos (geo o lift) dada la opacidad de SKAN/AEM.
- **Evitamos:** enviar el mismo evento por SDK y MMP sin `event_id`; cambiar el esquema SKAN con campañas activas; comparar ROAS iOS de Ads Manager con el del MMP sin normalizar ventanas.

## Errores frecuentes

1. `extinfo` con número de elementos incorrecto → evento rechazado.
2. Hashear `madid`/`anon_id`.
3. No pasar Universal Links al SDK → AEM no funciona.
4. Esquema de conversion values que nunca supera umbrales de privacidad (todo `null`).

## Preguntas abiertas

- Soporte oficial de AdAttributionKit por Meta y su papel frente a AEM.
- Vigencia de los límites de campañas iOS 14 de la documentación legada.
- Calendario real del GAID.

## Fuentes clave

- [Conversions API for App Events](https://developers.facebook.com/docs/marketing-api/conversions-api/app-events) — vigente — meta-developers (S04-044)
- [AEM for iOS apps](https://developers.facebook.com/docs/app-events/guides/aggregated-event-measurement/) — vigente — meta-developers (S04-043)
- [AEM and Limitations of SKAdNetwork](https://developers.facebook.com/documentation/app-ads/SKAdNetwork-aem-and-limitations) — legacy — meta-developers (S04-071)
- [Advertiser Tracking Enabled](https://developers.facebook.com/documentation/app-events/guides/advertising-tracking-enabled) — vigente — meta-developers (S04-072)
- [Insights breakdowns (SKAN)](https://developers.facebook.com/documentation/ads-commerce/marketing-api/insights/breakdowns) — vigente — meta-developers (S04-051)
- [AppsFlyer: Meta Ads integration setup](https://support.appsflyer.com/hc/en-us/articles/207033826) — 2025 — vendor (S04-046)
- [Airbridge: Meta Business FAQ](https://help.airbridge.io/en/guides/meta-business-faq) — 2025 — vendor (S04-045)
- [PPC Land: Meta activates SKAdNetwork 4.0](https://ppc.land/meta-activates-skadnetwork-4-0-for-advertisers-requiring-manual-configuration/) — 2025-06 — prensa (S04-110)
- [Adjust 2026 report (ATT)](https://www.businesswire.com/news/home/20260218837408/en/Adjust-Mobile-App-Use-Grew-Globally-In-2025-With-Continued-Move-To-Multi-Platform) — 2026-02-18 — vendor (S04-076)
