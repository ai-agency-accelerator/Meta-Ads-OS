# Checklist de QA de tracking y árboles de diagnóstico

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: procedimientos operativos para validar una implementación de Meta Pixel + CAPI y diagnosticar discrepancias o roturas. Se apoya en los archivos 01–15.

## TL;DR

- **Audita en este orden: eventos recibidos (Events Manager) → calidad (EMQ, dedup, coverage, freshness) → atribución (Ads Manager) → negocio (backend).** La mayoría de "problemas de atribución" son problemas de tracking o de expectativas sobre cómo atribuye Meta. [STRONG INFERENCE]
- **Herramientas:** Meta Pixel Helper, Test Events (`test_event_code`), Payload Helper, Events Manager (Overview, Diagnostics, Event details: freshness/dedup/EMQ), Dataset Quality API, Commerce Manager (match de catálogo), preview de GTM web/server, logs propios de CAPI. [OFFICIAL META] ([S04-009], [S04-016], [S04-056])
- **Umbrales de salud (referencia práctica):** Purchase recibidos ≈ pedidos online con consentimiento (±5 %); dedup de Purchase con overlap > 90 %; EMQ Purchase ≥ 8 (mínimo Meta 6); coverage CAPI ≥ 75 % (objetivo de ejemplo de Meta); freshness "real time"; `fbc` presente en la mayoría de compras con sesión de Meta. [OFFICIAL META] (6,0 y 75 %, [S04-056], [S04-016]) + [EMPIRICAL] (resto)
- **Cambios de definición que parecen "roturas" (2025–2026):** API ignora `action_report_time`/`use_unified_attribution_setting` (10-jun-2025); `7d_view`/`28d_view` devuelven vacío (12-ene-2026); click-through = solo link clicks y engage-through con vídeo ≥ 5 s (finales de mar-2026); `dma` → `comscore_market` (22-jun-2026); breakdowns `frequency_value`/`impression_device` con opt-in en algunas cuentas (6-ago-2026); custom conversions "flagged" dejan de emparejarse (desde 2-sep-2025). [OFFICIAL META] ([S04-048], [S04-001], [S04-003], [S04-049], [S04-095])

## 1. Checklist de QA

### 1.1 Antes de lanzar (o tras cualquier cambio de web/checkout/plugin)
- [ ] Inventario de emisores: ¿dónde vive cada `fbq` y cada envío CAPI? (theme, apps, plugins, GTM web, sGTM, backend, Gateway). Un emisor por evento y fuente.
- [ ] Un solo Pixel ID por sitio (salvo motivo documentado); `trackSingle` si hay varios.
- [ ] Pixel Helper: `PageView` en todas las páginas; eventos clave con parámetros (`value`, `currency`, `content_ids`, `content_type`, `contents`); `eventID` presente; advanced matching visible si aplica.
- [ ] Test Events: compra/lead de prueba aparece una vez como "Deduplicated" (navegador + servidor). Usar datos personales reales del tester.
- [ ] Payload Helper: JSON válido; `event_time` en segundos; `action_source` correcto; `event_source_url` real; `client_user_agent` presente.
- [ ] IP y UA de usuario (no de servidor/CDN) en CAPI; IPv6 cuando el navegador la tiene.
- [ ] `fbc`: probar landing con `?fbclid=TEST123` y verificar que el valor llega intacto (mayúsculas incluidas) al Purchase server-side tras navegar y pagar (incluidas redirecciones de pasarela).
- [ ] PII normalizada y hasheada una sola vez (vectores de prueba: `john_smith@gmail.com` → `62a14e44…`).
- [ ] Consentimiento: sin aceptar → no hay hits a `facebook.com/tr` ni envíos CAPI (si la base legal es consentimiento); tras aceptar → eventos fluyen (y, si la plataforma lo soporta, se re-emiten).
- [ ] LDU configurado si aplica (EE. UU.).
- [ ] Nombres de eventos/parámetros/URLs sin datos sensibles (salud, finanzas…).
- [ ] Catálogo: `content_ids` = IDs del catálogo; match rate > 90 % en Commerce Manager.
- [ ] Si se activa la "Meta-enabled Conversions API" (CAPI en un clic, abr-2026): comprobar que no existe otra CAPI (plugin, app, sGTM, Gateway) enviando los mismos eventos con `event_id` distinto.
- [ ] Revisar el aviso de "AI enrichment" del Pixel (activación por defecto tras 30 días) y decidir qué categorías de datos se permiten.
- [ ] Quitar `test_event_code` antes de publicar.

### 1.2 48–72 h después
- [ ] Events Manager > Overview: volúmenes por evento y por *connection method* (Browser/Server) coherentes.
- [ ] Event details: **Event Deduplication** (rate y overlap de `event_id`), **Event Freshness**, **EMQ**.
- [ ] Diagnostics sin alertas de severidad alta.
- [ ] Reconciliación diaria: Purchase server vs pedidos pagados (≥ 98 % con consentimiento).

### 1.3 Semanal / mensual
- [ ] Dataset Quality API: `composite_score`, `match_key_feedback`, `event_coverage`, `dedupe_key_feedback`, `data_freshness`.
- [ ] Reconciliación de 7 pasos (archivo 11).
- [ ] Revisar *Data source categories* y custom conversions "flagged" (sectores sensibles).
- [ ] Revisar changelog de Marketing API / out-of-cycle changes (trimestral).

## 2. Árbol: "Tenemos 8 ventas pero Ads Manager ve 3"

```
1. ¿Events Manager recibió ~8 Purchase (navegador o servidor) en ese periodo?
   ├─ NO (recibió ≤ 3–5) → PROBLEMA DE TRACKING
   │    ├─ ¿Pixel dispara en la confirmación? (Pixel Helper; pasarelas que no vuelven; SPA; consentimiento)
   │    ├─ ¿Hay CAPI para Purchase? (sin CAPI: ad blockers, ITP, cierre de pestaña → pérdidas del 10–30 % son habituales [EMPIRICAL])
   │    ├─ ¿Consentimiento rechazado en parte del tráfico (UE)? → esperado; cuantificar con CMP
   │    ├─ ¿Restricciones de categoría (core setup / eventos bloqueados)? → Settings > Data source categories
   │    └─ ¿Errores 4xx en CAPI (lote rechazado, token inválido, event_time > 7 días)? → logs
   └─ SÍ (≈ 8 recibidos) → PROBLEMA (o realidad) DE ATRIBUCIÓN
        ├─ ¿Cuántas de las 8 vinieron de personas que clicaron/interactuaron/vieron un anuncio en ventana?
        │    (backend con fbclid/UTM: si solo 3–4 tienen clic de Meta, Ads Manager probablemente está bien)
        ├─ ¿Lag > ventana? (compras a 10 días de un clic con 7d click no se atribuyen) → ver 28d click en columnas
        ├─ ¿EMQ bajo / sin fbc / IP de servidor? → eventos no emparejados no atribuyen → archivo 03
        ├─ ¿fbclid perdido en redirecciones (idioma, moneda, acortadores, checkout en otro dominio)?
        ├─ ¿Ventas de clientes recurrentes/orgánicos/email? → no son de Meta: correcto que no aparezcan
        ├─ ¿Ad set con Incremental attribution? → reporta menos por diseño
        ├─ ¿Cambio de definición (post-mar-2026 click = solo link click)? → mirar engage-through
        └─ ¿Fechas/zona horaria/datos recientes (< 72 h)? → esperar y comparar semanas
```
Referencias: [S04-005], [S04-010], [S04-003], [S04-050], [S04-082]; archivos 03, 09, 10, 12.

## 3. Árbol: "Ads Manager dice 20 ventas y Stripe 13"

```
1. Events Manager: ¿cuántos Purchase recibidos? 
   ├─ ≫ 13 (p. ej. 20–26) → DUPLICACIÓN O EVENTOS FALSOS
   │    ├─ Dedup: ¿navegador y servidor con mismo event_id/event_name? (Test Events; pestaña Event Deduplication)
   │    ├─ ¿Dos emisores del mismo lado? (app nativa + custom pixel/theme/GTM; plugin + plugin) → Pixel Helper muestra 2 Purchase
   │    ├─ ¿Recargas de la thank-you page con eventID nuevo cada vez?
   │    ├─ ¿Purchase disparado en pagos fallidos/pendientes (antes de confirmar el cobro)?
   │    ├─ ¿Upsells/ediciones de pedido que generan segundo Purchase?
   │    └─ ¿test_event_code o pedidos de prueba en producción?
   └─ ≈ 13 recibidos pero 20 atribuidos → imposible si cada compra se atribuye una vez…
        ├─ ¿Estás sumando varias cuentas/campañas que comparten conversiones? (cada campaña reporta con su configuración;
        │   una misma compra no se atribuye a dos anuncios de Meta, pero sí puede aparecer en informes con ventanas distintas)
        ├─ ¿"All conversions" con compras repetidas de la misma persona? → compara con "First conversion"
        ├─ ¿El evento optimizado es otro (p. ej. custom conversion que agrupa AddPaymentInfo)? 
        └─ ¿Periodo/zona horaria/moneda distintos? ¿Stripe neto de reembolsos/disputas vs Meta bruto?
2. Reconciliar valor: ¿Meta incluye impuestos/envío y Stripe no (o al revés)? ¿Conversión de moneda?
```
Referencias: [S04-005], [S04-084], [S04-100]; archivos 02, 04, 05, 11.

## 4. Árbol: "Tracking roto tras una actualización"

```
1. Delimitar: ¿qué cambió y cuándo? (deploy web, plugin/app actualizada, checkout, CMP, dominio, CDN, sGTM, token, API version)
2. ¿Cayó el volumen en Events Manager?
   ├─ Solo navegador ↓ → Pixel: ¿script eliminado/duplicado? ¿CMP bloquea? ¿CSP bloquea connect.facebook.net? ¿SPA sin PageView?
   │                       Shopify: ¿migración de Thank you/Order status dejó de ejecutar additional scripts? (desde 28-ago-2025 solo lectura;
   │                       non-Plus obligados antes de 26-ago-2026) → usar app pixel/custom pixel
   ├─ Solo servidor ↓ → CAPI: token caducado/revocado; versión de API expirada (v24 expiró 2026-10-06); errores 4xx por cambio de payload;
   │                     cola parada; webhook de pagos cambiado; sGTM sin trigger
   ├─ Ambos ↓ → cambio de dataset/Pixel ID; dominio nuevo; restricción de Meta (categoría sensible); consentimiento por defecto "deny"
   └─ Volumen OK pero dedup ↓ / Ads Manager ↑ → event_id dejó de coincidir (nueva variable, nuevo plugin) → duplicados
3. ¿Bajó EMQ o fbc? → IP/UA ahora del servidor (nuevo proxy/CDN), cookies con otro dominio, normalización cambiada
4. ¿Ads Manager cambió pero Events Manager no? → cambio de definición/ventana (ver TL;DR) o configuración de atribución del ad set
5. Corregir → verificar con Test Events → monitorizar 72 h → documentar en changelog interno
```
Referencias: [S04-034], [S04-094], [S04-057], [S04-048]; archivos 04–07, 09, 10.

## 5. Otros diagnósticos rápidos

| Síntoma | Hipótesis principal | Prueba |
|---|---|---|
| EMQ Purchase cae de 8 a 5 | PII ya no se envía (cambio de checkout) o IP/UA de servidor | `match_key_feedback` por clave |
| Coverage CAPI < 75 % | CAPI solo para Purchase, o fallos de envío | Dataset Quality API `event_coverage` |
| Freshness "daily" en web | CAPI en batch nocturno | Pasar a cola en tiempo real |
| ROAS de API ≠ Ads Manager | Pipeline aún pide ventanas eliminadas o cuenta con supuestos antiguos | Revisar `action_attribution_windows` (sin 7d_view/28d_view) |
| Caída de click-through en marzo-abril 2026 con total estable | Reclasificación a engage-through | Columnas por tipo de atribución |
| Custom conversion sin datos desde sep-2025 | Flagged por términos (salud/finanzas) | `is_unavailable`; Events Manager > custom conversions |
| Breakdown DMA vacío en informes EE. UU. | Sustituido por Comscore Markets (22-jun-2026) | Usar `comscore_market` |
| Conversiones de app iOS "desaparecen" | SKAN bajo umbral de privacidad / AEM vs SKAN | Breakdowns SKAN; MMP |

## Implicaciones operativas

- **Hacemos:** checklist 1.1 en cada release relevante; dashboard con los umbrales; changelog interno de tracking (fecha, cambio, responsable); responsable único del tracking por cliente.
- **Evitamos:** diagnosticar desde Ads Manager sin mirar Events Manager; tocar varias cosas a la vez al arreglar (no sabrás qué funcionó).

## Errores frecuentes

1. Validar solo con Pixel Helper (no ve CAPI).
2. Dar por bueno un test con una sola compra (no detecta duplicados intermitentes).
3. Olvidar que los eventos de prueba entran en el dataset.
4. Confundir cambios de definición de Meta con roturas.

## Preguntas abiertas

- Tasa "normal" de pérdida del Pixel frente a CAPI por sector/país en 2026 (no hay benchmark público fiable).

## Fuentes clave

- [Verifying Your Setup](https://developers.facebook.com/documentation/ads-commerce/conversions-api/verifying-setup) — vigente — meta-developers (S04-056)
- [Dataset Quality API](https://developers.facebook.com/docs/marketing-api/conversions-api/dataset-quality-api) — 2025 — meta-developers (S04-016)
- [Handling Duplicate Events](https://developers.facebook.com/docs/marketing-api/conversions-api/deduplicate-pixel-and-server-events) — vigente — meta-developers (S04-005)
- [2025 Out-of-cycle changes](https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2025) — 2025 — meta-developers (S04-048)
- [2026 Out-of-cycle changes](https://developers.facebook.com/documentation/ads-commerce/marketing-api/out-of-cycle-changes/occ-2026) — 2026 — meta-developers (S04-049)
- [Shopify checkout upgrade](https://help.shopify.com/en/manual/checkout-settings/checkout-extensibility/checkout-upgrade) — vigente — vendor (S04-034)
