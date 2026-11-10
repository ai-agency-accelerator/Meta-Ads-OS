# Builds custom: Conversions API directa (JS + backend), batching, latencia y errores

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: equipos de desarrollo que integran CAPI sin plugin ni GTM: arquitectura, contrato de datos, colas, reintentos, versionado de API, pagos (Stripe) y monitorización.

## TL;DR

- **Arquitectura de referencia:** navegador (Pixel + captura de `fbclid`/`_fbp`/`_fbc`/IP/UA) → backend (persistencia en sesión/pedido) → **cola** → worker CAPI (batch pequeño, reintentos idempotentes con el mismo `event_id`) → `POST /v25.0/{DATASET_ID}/events`. [OFFICIAL META] (endpoint, límites, [S04-009]) + [STRONG INFERENCE] (patrón)
- **Versión de API:** a 2026-10-16 la página de versiones de Meta lista **v25.0** (18-feb-2026, expiración TBD) como única versión vigente tras la expiración de v24.0 el 6-oct-2026. Fija la versión en configuración y revisa el changelog cada trimestre. [OFFICIAL META] ([S04-094]) **Corrección 2026-11-09**: la tabla oficial da el **10-nov-2026** como fin de la v24; v25 dura hasta el 23-feb-2027 y v27.0 salió el 4-nov-2026 (S10-100 en `fuentes/ledger-10-cambios-api-ia.md`).
- **Límites duros:** 1.000 eventos por request; un evento inválido rechaza el lote; `event_time` ≤ 7 días; no hay rate limit específico de CAPI más allá de los de Marketing API. Timeout recomendado 1.500 ms, respuesta típica < 600 ms; reintentar en errores no-cliente. [OFFICIAL META] ([S04-009], [S04-057])
- **Latencia objetivo: segundos, no horas.** Meta mide *data freshness* (real time, hourly, daily…) y recomienda real time; los eventos tardíos llegan pero optimizan peor y aparecen tarde en reporting. [OFFICIAL META] ([S04-016], [S04-056])
- **Pagos (Stripe, Redsys, PayPal…):** el Purchase server-side debe dispararse desde el webhook de pago confirmado, con `fbc`/`fbp`/`external_id`/IP/UA guardados **antes** del redirect a la pasarela (en el pedido o en `metadata` de la sesión de pago). Sin eso, el evento llega sin click ID y con IP del proveedor de pagos. [STRONG INFERENCE]
- **Observabilidad mínima:** log por evento (`event_id`, `event_name`, status, `fbtrace_id`), métrica diaria de eventos enviados vs pedidos, alertas de caída, y consulta semanal de la Dataset Quality API (EMQ, coverage, dedup, freshness). [OFFICIAL META] ([S04-016]) + [STRONG INFERENCE]

## 1. Contrato de datos (lo que el backend debe guardar)

| Momento | Qué capturar | Dónde guardarlo |
|---|---|---|
| Primera request de la sesión | `fbclid` (query), UTMs, `ad_id` si lo pasas por macro, referrer, IP (IPv6 si es posible), UA | Sesión servidor + cookie first-party HTTP (`_fbc` construida, 90 días) |
| Cada request | Cookies `_fbp`, `_fbc` | Leer del header Cookie |
| Login/registro | `external_id`, email, teléfono (normalizados) | Usuario |
| Checkout / lead | Todo lo anterior + `event_id` generado | Pedido / lead (columnas dedicadas) |
| Antes de redirigir a pasarela | `fbc`, `fbp`, IP, UA, `consent_state` | Pedido y/o `metadata` del pago |
| Webhook de pago | Leer del pedido, construir evento | Cola CAPI |

Por qué guardar IP y UA del navegador: CAPI exige `client_user_agent` para web y la IP es identificador de alto peso; el webhook de pago trae la IP del proveedor, no la del cliente. [OFFICIAL META] ([S04-010]) + [STRONG INFERENCE]

## 2. Worker CAPI (Python con requests; sin SDK)

```python
import json, time, uuid, logging, requests

GRAPH = "https://graph.facebook.com/v25.0"
SESSION = requests.Session()
log = logging.getLogger("capi")

def send_batch(dataset_id: str, token: str, events: list[dict], test_code: str | None = None):
    """events: lista de server events ya construidos (<= 1000; recomendado 50–200)."""
    payload = {"data": events}
    if test_code:
        payload["test_event_code"] = test_code
    for attempt in range(5):
        try:
            r = SESSION.post(f"{GRAPH}/{dataset_id}/events",
                             params={"access_token": token},
                             json=payload, timeout=1.5)          # Meta recomienda 1500 ms
        except requests.Timeout:
            r = None
        if r is not None and r.status_code < 300:
            body = r.json()
            log.info("capi ok received=%s trace=%s ids=%s",
                     body.get("events_received"), body.get("fbtrace_id"),
                     [e["event_id"] for e in events])
            return body
        if r is not None and 400 <= r.status_code < 500:
            # Error de cliente: NO reintentar a ciegas; el lote entero fue rechazado.
            log.error("capi 4xx %s %s", r.status_code, r.text[:500])
            if len(events) > 1:              # aislar el evento culpable
                mid = len(events) // 2
                send_batch(dataset_id, token, events[:mid], test_code)
                send_batch(dataset_id, token, events[mid:], test_code)
            return None
        time.sleep(min(2 ** attempt, 30))    # 5xx/timeout: backoff y reintento con el MISMO event_id
    raise RuntimeError("CAPI no disponible tras reintentos")

def purchase_event(order) -> dict:
    return {
        "event_name": "Purchase",
        "event_time": int(order.paid_at.timestamp()),       # segundos, no ms
        "event_id": f"purchase_{order.id}",                 # determinista: igual que el Pixel
        "action_source": "website",
        "event_source_url": order.checkout_url,
        "user_data": {
            "em": [order.email_sha256], "ph": [order.phone_sha256],
            "external_id": [order.customer_id],
            "client_ip_address": order.client_ip, "client_user_agent": order.client_ua,
            "fbc": order.fbc, "fbp": order.fbp,
        },
        "custom_data": {
            "currency": order.currency, "value": float(order.total),
            "order_id": str(order.id), "content_type": "product",
            "contents": [{"id": li.sku, "quantity": li.qty, "item_price": float(li.price)}
                         for li in order.lines],
        },
    }
```

Notas:
- El "split del lote" ante 4xx es una técnica para localizar el evento inválido; en producción conviene validar eventos antes de encolarlos (esquema JSON) para no llegar a ese punto. [STRONG INFERENCE]
- Si el reintento ocurre con el mismo `event_id` dentro de 48 h, Meta deduplica (Método 1). [OFFICIAL META] ([S04-005])
- No mezcles en un mismo lote eventos de días muy distintos: si uno supera 7 días, cae todo. [OFFICIAL META] ([S04-008])
- Business SDK oficial (Python/Node/PHP/Java/Ruby) hashea automáticamente y gestiona la estructura; útil si no quieres mantener normalización propia (aun así, normaliza el teléfono tú). [OFFICIAL META] ([S04-010])

## 3. Stripe (patrón)

```js
// 1) Al crear la Checkout Session / PaymentIntent, guarda contexto de atribución
const session = await stripe.checkout.sessions.create({
  mode: 'payment',
  line_items, success_url, cancel_url,
  client_reference_id: order.id,
  metadata: {
    order_id: order.id,
    fbc: req.cookies._fbc ?? buildFbc(req.session.fbclid),
    fbp: req.cookies._fbp ?? '',
    client_ip: clientIp(req),            // IP real del usuario (X-Forwarded-For / CF-Connecting-IP)
    client_ua: req.get('user-agent'),
    consent_marketing: req.session.consentMarketing ? '1' : '0'
  }
});

// 2) Webhook checkout.session.completed (o payment_intent.succeeded)
//    → si consent_marketing==='1', encola Purchase con event_id `purchase_${order_id}`
//    → la thank-you page dispara fbq('track','Purchase',…,{eventID:`purchase_${order_id}`})
```

- Stripe `metadata` admite pares clave-valor de longitud limitada; `fbc` y UA caben normalmente, pero valida longitudes (límite de Stripe no verificado aquí). [STRONG INFERENCE]
- Reembolsos y disputas **no** restan conversiones en Meta: Meta no tiene un mecanismo estándar de "refund" en CAPI (no verificado que exista); se gestiona en reconciliación (archivo 11) o con eventos custom de reporting. [HYPOTHESIS] (ausencia de mecanismo documentado en las páginas consultadas)
- Suscripciones: la primera compra es la señal de adquisición; las renovaciones (`invoice.paid`) pueden enviarse como evento custom (`SubscriptionRenewal`) para medir LTV sin contaminar la optimización de Purchase. [STRONG INFERENCE]

## 4. Latencia y frescura: cuánto importa

| Retraso del evento | Efecto |
|---|---|
| Segundos–minutos | Óptimo: freshness "real time"; el evento compite en igualdad con el Pixel en dedup |
| 1 hora | Aceptable ("ideally within an hour") |
| Horas–1 día | Peor freshness; conversiones visibles tarde en Ads Manager; señal más tardía para el algoritmo |
| > 7 días | Rechazado (`event_time` fuera de rango) |

[OFFICIAL META] ([S04-009], [S04-016]). Efecto sobre optimización en `12-attribution-lag.md`.

**Regla del primero en llegar:** si navegador y servidor llegan con < 5 min de diferencia, se favorece el de navegador; en general se conserva el primero. Un CAPI muy lento no "pisa" al Pixel, pero sí le quita al sistema la información extra que solo llevaba el server event (p. ej. PII) si el Pixel llegó antes con menos datos — por eso conviene enviar PII también por el Pixel (advanced matching) o enviar CAPI en tiempo real. [OFFICIAL META] ([S04-008]) + [HYPOTHESIS] (sobre fusión de parámetros entre eventos deduplicados: Meta no documenta si combina `user_data` de ambos)

## 5. Tokens, permisos y seguridad

- Usa un **System User** del Business Manager con acceso al dataset y token sin caducidad; guarda el token en un secret manager; rota si se filtra. [STRONG INFERENCE]
- Si eres agencia/plataforma: `partner_agent` identificable; para clientes múltiples, Meta tiene guías "Conversions API as a Platform" y "CAPI Gateway for Multiple Accounts". [OFFICIAL META] ([S04-010], índice de docs)
- No registres PII en claro en logs (solo hashes o nada).
- Token inválido: algunos plugins bloquean CAPI silenciosamente (Meta for WooCommerce lo hace de forma explícita desde 2026). Monitoriza volumen. [OFFICIAL META] ([S04-035])

## 6. Monitorización recomendada

1. **Diario:** eventos Purchase enviados (2xx) vs pedidos pagados con consentimiento → ratio ≥ 0,98.
2. **Diario:** % de Purchase con `fbc` y con `fbp`; % con email/teléfono.
3. **Semanal:** Dataset Quality API (`composite_score`, `event_coverage.percentage` vs `goal_percentage`, `dedupe_key_feedback`, `data_freshness`).
4. **Por release:** test end-to-end con `test_event_code` en staging (dataset de pruebas o el real con código de test).
5. **Trimestral:** changelog de Marketing API y out-of-cycle changes (p. ej. cambios de breakdowns y ventanas en 2025–2026).

[OFFICIAL META] ([S04-016], [S04-048], [S04-049]) + [STRONG INFERENCE] (umbrales)

## Implicaciones operativas

- **Hacemos:** guardar contexto de atribución en el pedido antes del pago; cola + worker idempotente; versión de API configurable; tests de payload con vectores conocidos; dashboards de cobertura.
- **Evitamos:** enviar CAPI de forma síncrona en el request del usuario (añade latencia y fallos visibles); lotes de 1.000 sin validación; IP del servidor; reintentos con `event_id` nuevo.

## Errores frecuentes

1. Webhook de pago que envía Purchase sin `fbc`/`fbp` porque nunca se guardaron.
2. Doble envío (thank-you server-side + webhook) con IDs distintos.
3. `event_time` = momento del envío en lugar del momento real de la conversión (distorsiona lag y reporting).
4. Errores 4xx ignorados por un `try/except` genérico → semanas sin CAPI.
5. Versión de API caducada en código heredado.

## Preguntas abiertas

- ¿Combina Meta los `user_data` de los eventos navegador/servidor deduplicados o se queda con uno? (no documentado).
- ¿Existe una vía soportada para "retractar" conversiones (refunds) en CAPI? (no encontrada en la documentación consultada).

## Fuentes clave

- [Using the Conversions API](https://developers.facebook.com/docs/marketing-api/conversions-api/using-the-api) — vigente — meta-developers (S04-009)
- [Troubleshooting CAPI](https://developers.facebook.com/documentation/ads-commerce/conversions-api/support) — vigente — meta-developers (S04-057)
- [Server Event Parameters](https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/server-event) — vigente — meta-developers (S04-008)
- [Marketing API versions](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/versions) — consultado 2026-10-16 — meta-developers (S04-094)
- [Dataset Quality API](https://developers.facebook.com/docs/marketing-api/conversions-api/dataset-quality-api) — 2025 — meta-developers (S04-016)
