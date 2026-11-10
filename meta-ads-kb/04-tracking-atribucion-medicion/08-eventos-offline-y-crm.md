# Eventos offline y CRM: Conversions API para tienda física, call center y Conversion Leads

> Última verificación: 2026-10-16 · Autor: A04 (agente) · Ámbito: parte técnica de eventos offline (`physical_store`) y del CRM para lead ads (Conversion Leads). La estrategia de lead gen y high-ticket la cubre el área 05; aquí, payloads, requisitos, calidad y errores.

## TL;DR

- **La Offline Conversions API (OCAPI) está retirada como vía para nuevas integraciones:** Meta anunció su discontinuación con la expiración de Graph API v16.0 en **mayo de 2025** (tras retrasar el plan de Q3-2024); la documentación actual la llama "legacy API" y recomienda la Conversions API para web, app y offline en un único endpoint. [OFFICIAL META] ([S04-061], [S04-067]) — La página de versiones de Meta fecha la expiración general de v16.0 en feb-2024, lo que sugiere una prórroga específica para OCAPI; no se ha verificado si algún endpoint legado sigue respondiendo en 2026. [CONTESTED]
- **Offline vía CAPI:** `action_source=physical_store`, mismo dataset que la web, `POST /{DATASET_ID}/events`; deduplicación offline **solo contra otros eventos offline**, por `order_id` (fallback: datos de usuario) en ventana de **7 días**; subir en tiempo real o diario; "dentro de 62 días" de la conversión. [OFFICIAL META] ([S04-061])
- **Calidad offline (ODQ score 0–10):** frecuencia (días con datos en los últimos 14), frescura (retraso medio 28 días), cobertura de match keys, volumen, valores válidos, *basket splitting*… ≥ 8,5 es el nivel que Meta asocia a usar omnichannel ads con confianza; datos con > 3 días se consideran *stale*; ≥ 12 subidas en 14 días. [OFFICIAL META] ([S04-017])
- **CRM para lead ads (Conversion Leads):** `action_source=system_generated`, `custom_data.event_source="crm"`, `custom_data.lead_event_source="<nombre del CRM>"`, `user_data.lead_id` (15–17 dígitos) como clave de máxima prioridad, `event_name` libre = etapa del CRM; enviar **todas** las etapas (incluida la inicial). [OFFICIAL META] ([S04-058])
- **Requisitos Conversion Leads:** ≥ 200 leads/mes según la guía de developers (Meta anunció su eliminación el 30-oct-2025; tratar como orientación de volumen, no como bloqueo), subida ≥ 1 vez al día, la etapa a optimizar ocurre en ≤ 28 días desde el lead y tiene CVR entre 1 % y 40 %; mínimo 2 etapas (mejor 3) y 7 días de datos para pasar validación; entrenamiento de 1–2 meses tras configurar el embudo. **No cambies de Pixel después** (reinicia la integración). [OFFICIAL META] ([S04-059], [S04-060])
- **Contradicción en la documentación de Meta:** la página principal dice que Conversion Leads solo es compatible con Instant Forms; la FAQ menciona "Instant Forms o Website Forms". Trátalo como Instant Forms salvo confirmación de tu representante. [CONTESTED] ([S04-059], [S04-060])
- **Leads de formularios web** no usan este flujo; envía las etapas del CRM como eventos CAPI normales (`action_source` coherente, con `fbc`/`external_id`/email guardados en el lead) y valora optimizar a un evento intermedio de calidad (ver 12-attribution-lag). [STRONG INFERENCE]

## 1. Offline (tienda física, call center, ventas asistidas)

### 1.1 Payload

```json
{
  "data": [{
    "event_name": "Purchase",
    "event_time": 1760500000,
    "action_source": "physical_store",
    "user_data": {
      "em": ["<sha256 email>"],
      "ph": ["<sha256 phone>"],
      "external_id": ["loyalty_88231"],
      "fn": ["<sha256>"], "ln": ["<sha256>"], "zp": ["<sha256>"], "country": ["<sha256 'es'>"]
    },
    "custom_data": {
      "currency": "EUR",
      "value": 249.00,
      "order_id": "POS-2026-000918",
      "contents": [{"id": "SKU-123", "quantity": 1}],
      "content_type": "product"
    }
  }]
}
```

- No hay `event_source_url` ni IP/UA en offline (el tag oficial de sGTM incluso omite `event_source_url` si `action_source` es `physical_store`). [OFFICIAL META] ([S04-081])
- `store_data` (store page ID, brand page ID, store code) es opcional; `item_number` distingue líneas de un mismo pedido. [OFFICIAL META] ([S04-061])
- **Una fila/evento por pedido**, con todos los artículos en `contents` (no dividir la cesta: *basket splitting* penaliza la calidad). Valor > 0; no enviar devoluciones como valores negativos. [OFFICIAL META] ([S04-017])
- **No envíes datos web como offline** (Meta lo pide explícitamente). [OFFICIAL META] ([S04-017])

### 1.2 Tiempo y frecuencia
- Tiempo real o al menos diario; preferiblemente cada hora. ≥ 12 subidas en los últimos 14 días; > 3 días de antigüedad = *stale*; para elegibilidad a Omnichannel Ads, 14 días de datos. [OFFICIAL META] ([S04-017])
- `event_time` ≤ 7 días en el envío estándar; Meta pide además subir transacciones en ≤ 62 días. Diseña para enviar en < 24 h y no dependas de backfills largos. [OFFICIAL META] ([S04-008], [S04-061]) — la compatibilidad 7 vs 62 días no está aclarada (ver archivo 01).

### 1.3 Matching offline
- Claves: email y teléfono (hasheados) son las más útiles; `external_id` (programa de fidelización); `madid`, `lead_id` sin hash. Captar email en el ticket digital aumenta volumen emparejable. [OFFICIAL META] ([S04-061], [S04-017])
- EMQ no se calcula para offline; se usa el **Offline Data Quality score** (Dataset Quality API con el campo `offline`: `composite`, `match_key`, `frequency`, `freshness`). [OFFICIAL META] ([S04-098])

### 1.4 Atribución y uso
- Los eventos offline se emparejan con quien vio/clicó anuncios y se reportan en campañas que tengan el dataset asignado ("auto-tracking" para campañas futuras). Para optimizar en omnicanal se usa **una sola fuente offline**; varias fuentes solo para medición. [OFFICIAL META] ([S04-017])
- La atribución de offline suele ser mayoritariamente *view-through*/engage (no hay clic en tienda): interprétala con incrementalidad (archivo 13), no como prueba causal. [STRONG INFERENCE]

## 2. CRM para lead ads (Conversion Leads)

### 2.1 Flujo
1. Descargar leads de Meta al CRM (webhook `leadgen` o integración nativa), **guardando `leadgen_id`** como `lead_id`. [OFFICIAL META] ([S04-058])
2. Crear/elegir el dataset (Pixel) para eventos CRM en Events Manager.
3. Enviar a CAPI cada cambio de etapa (incluida la creación del lead) con el payload de abajo.
4. Meta valida datos (~1–2 días tras 7 días de datos), el anunciante configura el embudo en Events Manager (qué etapa optimizar), y empieza el entrenamiento (1–2 meses según la FAQ; 2–4 semanas según la tabla de plazos de la página principal). [OFFICIAL META] ([S04-059], [S04-060]) — discrepancia interna de Meta en plazos.
5. En Ads Manager: objetivo Leads, Instant Forms, meta de rendimiento **Conversion leads** (nombre exacto de la UI puede variar; ver área 05).

### 2.2 Payload (especificación oficial)

```json
{
  "data": [{
    "event_name": "Marketing Qualified Lead",
    "event_time": 1760601234,
    "action_source": "system_generated",
    "user_data": {
      "lead_id": 1234567890123456,
      "em": ["<sha256 email>"],
      "ph": ["<sha256 phone>"]
    },
    "custom_data": {
      "event_source": "crm",
      "lead_event_source": "HubSpot"
    }
  }]
}
```

Reglas: `event_time` = momento del cambio de etapa en el CRM, ≤ 7 días de antigüedad y **posterior** a la creación del lead (si no, puede descartarse); al menos un parámetro de cliente; `lead_id` inválido → rechazo; `click_id` inválido no da error de API pero un volumen alto dispara alertas. Lotes ≤ 1.000 eventos (usa lotes pequeños: un error descarta el lote). [OFFICIAL META] ([S04-058], [S04-059])

### 2.3 Diseño del embudo
| Buenas prácticas | Por qué |
|---|---|
| 3–5 etapas con nombres estables (`Lead`, `MQL`, `SQL`, `Opportunity`, `Won`) | Meta necesita ≥ 2 etapas y analiza el embudo completo |
| Optimizar a la etapa más profunda que cumpla CVR 1–40 % y ocurra en ≤ 28 días | Fuera de esos rangos el modelo no tiene señal suficiente o llega tarde |
| Enviar también la etapa inicial para el 100 % de leads | La validación exige eventos para (casi) todos los leads generados |
| Subida diaria mínima; ideal en tiempo real | Requisito de Meta |
| No cambiar de dataset | Reinicia el entrenamiento |

[OFFICIAL META] ([S04-059], [S04-060]) + [STRONG INFERENCE] (nombres de etapas)

### 2.4 Integraciones
- Meta documenta Zapier como integración de partner y guías para Salesforce (webhooks) y "CAPI for CRM for Platforms". Para HubSpot y otros CRMs existen integraciones nativas o de terceros; verifica que envían `lead_id`, `event_source` y `lead_event_source`. [OFFICIAL META] (índice de docs, [S04-047])

## 3. Leads web y ventas de ciclo largo (no Instant Forms)

- Guarda en el lead: `fbc` (o `fbclid`), `fbp`, `external_id`, email, teléfono, IP, UA, `event_id` del Lead inicial y UTMs con `ad_id`.
- Envía etapas posteriores (`QualifiedLead`, `Purchase`…) por CAPI como eventos del dataset web (`action_source` = `system_generated` o el que corresponda con veracidad; Meta exige que sea preciso). Para atribución de clic, `fbc` es lo que vincula al anuncio; recuerda la ventana máxima (7 días click por defecto, 28 días click si se elige; ver archivo 10).
- Si el ciclo supera la ventana, ese evento **no** se atribuirá a ninguna campaña: sirve para audiencias y medición propia, pero no para optimizar. De ahí la estrategia de proxies (archivo 12). [OFFICIAL META] (ventanas) + [STRONG INFERENCE]

## Implicaciones operativas

- **Hacemos:** offline y CRM al mismo dataset que la web (salvo casos avanzados), `order_id`/`lead_id` como claves, subidas diarias como mínimo con monitorización, embudo CRM con etapas estables y CVR medida antes de activar Conversion Leads.
- **Evitamos:** reenviar ventas web como offline; dividir cestas; cambiar de Pixel a mitad de entrenamiento; enviar etapas con `event_time` anterior al lead.
- **Umbrales:** ODQ ≥ 8,5 para omnicanal; ~200 leads/mes como orientación para Conversion Leads (ya no es requisito oficial desde 30-oct-2025); etapa objetivo con CVR 1–40 % en ≤ 28 días.

## Errores frecuentes

1. Seguir usando integraciones OCAPI/"offline event sets" heredadas sin migrar (riesgo de pérdida silenciosa de datos).
2. Lotes de miles de filas offline con una fila corrupta → nada se procesa.
3. CRM que solo envía "Won" → falla la validación (mínimo 2 etapas).
4. `lead_id` almacenado como número en coma flotante en hojas de cálculo (se corrompen los últimos dígitos).
5. Esperar a fin de mes para subir ventas offline (stale, fuera de 7 días).

## Preguntas abiertas

- ¿Siguen operativos endpoints legados de OCAPI en 2026 para cuentas antiguas? (no verificado).
- ¿Website Forms es compatible con Conversion Leads o solo Instant Forms? (documentación contradictoria).
- ¿Cuál es el plazo real de entrenamiento: 2–4 semanas o 1–2 meses? (Meta da ambos).

## Fuentes clave

- [Conversions API for Offline Events](https://developers.facebook.com/documentation/ads-commerce/conversions-api/offline-events) — vigente — meta-developers (S04-061)
- [Omni Optimal Setup Guide](https://developers.facebook.com/documentation/ads-commerce/marketing-api/best-practices/omni-optimal-setup-guide) — vigente — meta-developers (S04-017)
- [Conversions API for CRM Integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — vigente — meta-developers (S04-060)
- [Conversion Leads — Payload Specification](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration/payload-specification) — vigente — meta-developers (S04-058)
- [Conversion Leads — FAQ](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration/faq) — vigente — meta-developers (S04-059)
- [Offline Conversions (legacy)](https://developers.facebook.com/docs/marketing-api/offline-conversions) — legacy — meta-developers
- [Zapier: Changes impacting Facebook Offline Conversions users](https://help.zapier.com/hc/en-us/articles/26967162052493-Changes-impacting-Facebook-Offline-Conversions-users) — 2025 — vendor (S04-097)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Mínimo de 200 leads/mes: matizado como orientación (Meta lo eliminó el 30-oct-2025; la guía de developers no se ha actualizado). La FAQ de developers ya menciona "Instant Forms or Website Forms" y un entrenamiento de 1–2 meses; la página principal habla de 2–4 semanas: Meta da ambos plazos.
