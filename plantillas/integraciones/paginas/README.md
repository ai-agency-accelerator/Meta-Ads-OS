# Plantillas: páginas de `paginas.py` → CRM + Conversions API

El receptor del webhook de las páginas generadas (`/construir-landing`, `/iman-de-leads`, `/webinar`). Cada envío
(el **payload v1** de [`plantillas/paginas/README.md`](../../paginas/README.md)) entra siempre en el CRM. **Solo si la
persona dio permiso**, sus eventos van también a la Conversions API, con el mismo `event_name` y `event_id` que el
píxel para que Meta deduplique. Es la «ruta A» de [`docs/guias/construir-landing.md`](../../../docs/guias/construir-landing.md) §3.

| Archivo | Para quién |
|---|---|
| `n8n-paginas-capi.json` | Quien usa n8n. Se importa tal cual: Workflows → Import from File. |
| Este README, «Make» | Quien usa Make: un escenario montado a mano, módulo a módulo. |
| Este README, «Backend propio» | Quien tiene servidor o funciones *serverless*: pseudocódigo con la regla. |
| `ejemplos/*.json` | Dos envíos reales de `paginas.js` (con y sin consentimiento), con datos ficticios, para probar sin la web. |

Los tests (`tests/herramientas/test_paginas_integracion.py`) ejecutan el código de los nodos de n8n con Node y
comprueban con `capi.py validar` que lo que sale es un payload válido.

## La regla del consentimiento (contrato §17)

Manda a la CAPI un envío **solo si** se cumplen las dos cosas:

1. `enviar_a_meta` es `true`. La página lo pone cuando la persona pulsa «Aceptar» en el banner o cuando
   `base_legal_servidor` es `interes_legitimo`.
2. Con `base_legal_servidor: "consentimiento"` (lo normal), además `consentimiento_marketing` es `"si"`. Si algo llega
   incoherente, no sale.

Si no se cumplen, el envío no va a Meta: el contacto ya está en el CRM con sus UTMs y su `ad_id`. Sus etapas
posteriores irán por la CAPI de CRM con las reglas de la ficha.

El banner sale en todas las páginas que lo necesitan, también sin píxel («solo servidor»). Sin él, `enviar_a_meta`
saldría siempre `false` y esta puerta no dejaría pasar nada.

## Qué se manda a Meta

Un evento por cada elemento de `eventos` (p. ej. `Lead` y `DiagnosticoCompletado`):

| Campo de la CAPI | De dónde sale |
|---|---|
| `event_name`, `event_id` | Tal cual del envío. Son los nombres del contrato §16: **no los cambies** o no deduplica |
| `event_time`, `event_source_url` | `event_time` y `event_source_url` del envío |
| `action_source` | `website` |
| `user_data.em`, `.ph` | `email` y `telefono`, normalizados y con SHA-256 (como `capi.py hashear`). El teléfono sin `+` lleva el prefijo de la configuración |
| `user_data.fn`, `.ln` | Solo si el formulario tiene `nombre` y `apellidos` por separado |
| `user_data.client_user_agent` | `client_user_agent` del envío |
| `user_data.client_ip_address` | La IP de la petición (`CF-Connecting-IP` o `X-Forwarded-For`), no la de tu servidor |
| `user_data.fbc`, `.fbp` | Si vienen. `fbp` solo llega con «Aceptar» |
| `custom_data.value`, `.currency` | Los del evento (el `valor_evento` del diagnóstico, en la moneda de la página) |
| `custom_data.content_name` | El del envío, si lo hay (p. ej. la edición del webinar) |

## n8n

1. Importa `n8n-paginas-capi.json` y rellena los `<<…>>`: la URL del CRM y «Configuración (rellena esto)».
2. Credencial: Query Auth con el nombre `access_token` en «Enviar a la Conversions API». El token, solo ahí.
3. Entorno de n8n: `NODE_FUNCTION_ALLOW_BUILTIN=crypto` (el hash).
4. CORS: en «Páginas · envío», opción «Allowed Origins (CORS)» con el dominio de tus páginas. Si tu n8n no la tiene,
   pon `tracking.webhook.modo: "texto"` en el config de las páginas: el nodo «Leer envío» entiende las dos formas.
5. La URL de producción del webhook va en `tracking.webhook.url` del config de las páginas. Vuelve a generarlas.
6. Prueba con `TEST_EVENT_CODE` y tus propios datos. Sin código de prueba no sale nada hacia Meta: el envío real exige
   `ENVIO_REAL_APROBADO: true`, con el sí del cliente.

## Make

Un escenario:

1. **Webhooks → Custom webhook.** Su URL va en `tracking.webhook.url`. Pásale `ejemplos/envio-con-consentimiento.json`
   para que aprenda la estructura.
2. **Router** con dos rutas:
   - **Ruta 1, siempre:** el módulo de tu CRM (en GHL, *Create/Update Contact* con los campos, las UTMs y el `ad_id`).
   - **Ruta 2, con este filtro:** `enviar_a_meta` = `true` **y** (`base_legal_servidor` = `interes_legitimo` **o**
     `consentimiento_marketing` = `si`).
3. En la ruta 2, **Iterator** sobre `eventos` y, por cada uno, **HTTP → Make a request**:
   - `POST https://graph.facebook.com/v27.0/<DATASET_ID>/events?access_token=<token en una conexión o variable>`;
   - cuerpo con `event_name` y `event_id` del iterador, `event_time`, `event_source_url`, `action_source: website` y
     `user_data`;
   - el email con `sha256(lower(trim(email)))`;
   - el teléfono solo con dígitos y prefijo de país antes del `sha256`.
4. Mientras pruebas, `test_event_code` en el cuerpo. Quítalo solo con el sí del cliente.

Los nombres de los módulos de Make pueden cambiar: están sin verificar a fecha de 2026-11-10.

## Backend propio

```text
recibir POST (JSON, o texto con un JSON dentro si la página usa modo «texto»)
si envio.origen != "meta-ads-os/paginas" o envio.version != 1 → 400
guardar en el CRM (siempre): campos, utm_*, ad_id, respuestas, diagnostico
permitido = envio.enviar_a_meta == true y
            (envio.base_legal_servidor == "interes_legitimo" o envio.consentimiento_marketing == "si")
si permitido:
    user_data = {em: [sha256(email normalizado)], ph: [sha256(teléfono con prefijo)],
                 client_user_agent, client_ip_address: IP de la petición, fbc?, fbp?}
    data = [{event_name, event_id, event_time: envio.event_time, action_source: "website",
             event_source_url: envio.event_source_url, user_data, custom_data?} por cada envio.eventos]
    validar (python3 -I herramientas/capi.py validar) y POST /{dataset}/events
responder 2xx (con modo json, otra respuesta hace que la página diga «no hemos podido enviar»)
```

Normaliza igual que `herramientas/capi.py` (`docs/guias/capi.md` §2). Para comprobar tu hash:
`python3 -I herramientas/capi.py hashear "<valor>" --tipo em`.
