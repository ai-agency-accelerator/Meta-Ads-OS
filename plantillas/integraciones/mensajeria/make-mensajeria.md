# Make: mensajería → Conversions API

Son dos escenarios, con la misma lógica que el flujo de n8n. Lee antes el [README](README.md): recoge los campos del CRM,
la tabla de eventos y las reglas.

**Qué está verificado.** La firma de las funciones de Make se comprobó en la documentación oficial (Text and binary
functions) el 2026-11-09. Las opciones de los módulos, los menús y los nombres de los campos **no están verificados**:
los escribo como los conozco y pueden variar. Compruébalos en tu cuenta. Sintaxis de las funciones:
- `sha256(texto; [codificación]; [clave])`;
- con clave, devuelve el HMAC.

---

## Escenario 1 · Entrada de la conversación

**Objetivo:** guardar el origen del clic en el contacto cuando llega el primer mensaje desde un anuncio.

1. **Webhooks → Custom webhook.** Crea un webhook nuevo y activa sus opciones avanzadas:
   - **Get request headers**, para leer la firma.
   - **Get request HTTP method**, para separar la verificación (GET) de los avisos (POST).
   - **JSON pass-through**, para tener el cuerpo crudo como texto (`value`). La firma se calcula sobre ese texto.

   Copia la URL y pégala en la app de Meta: WhatsApp → Configuración → Webhook (o Messenger o Instagram → Webhooks).
   Suscribe el campo `messages`, y `messaging_referrals` en Messenger.
2. **Router** con dos rutas:
   - **Ruta A, verificación.** Filtro: método = `GET` y `hub.verify_token` = `<<VERIFY_TOKEN>>`. Después, **Webhooks →
     Webhook response**: estado `200` y cuerpo `{{hub.challenge}}`, sin comillas.
   - **Ruta B, avisos.** Filtro: método = `POST`.
3. **Ruta B → Tools → Set variable** `firma_ok`:
   ```
   {{ "sha256=" + sha256(value; "hex"; "<<APP_SECRET: guárdalo como variable de escenario o de equipo, no aquí>>") = get(headers; "x-hub-signature-256") }}
   ```
   Ahí, `value` es el cuerpo crudo de *JSON pass-through* y `headers` es la cabecera, que Make entrega como colección o
   como array según la versión.
   - Si `get()` no encuentra la cabecera, mapea a mano el elemento `x-hub-signature-256`.
   - El HMAC tiene que calcularse sobre el texto **exacto** que manda Meta. Lo es si no lo transformas antes.
     `[HYPOTHESIS]`: compruébalo con un aviso de prueba de la app (botón «Test» del campo `messages`).
4. **Filtro** `firma_ok = true`. Sin firma válida, el escenario termina en ese punto.
5. **JSON → Parse JSON** sobre `value`.
6. **Iterator** según el canal:
   - **WhatsApp** (`object = whatsapp_business_account`): itera
     `entry[1].changes[1].value.messages`. Si el mismo aviso trae varios, añade otro Iterator sobre `entry` y `changes`.
   - **Messenger e Instagram** (`object = page` o `instagram`): itera `entry[1].messaging`.
7. **Filtro: solo mensajes de anuncio.**
   - WhatsApp: `referral` existe.
   - Messenger e Instagram: `message.referral.source` (o `referral.source`) = `ADS` y `message.is_echo` no es `true`.
8. **Tools → Set multiple variables.** Los campos del README:

   | Variable | WhatsApp | Messenger / Instagram |
   |---|---|---|
   | `mensajeria_canal` | `whatsapp` | `messenger` si `object = page`, `instagram` si no |
   | `mensajeria_cuenta` | `entry[].id` (la WABA) | `recipient.id` |
   | `mensajeria_anuncio` | `referral.source_id` | `message.referral.ad_id` |
   | `mensajeria_clic` | `referral.ctwa_clid` (vacío en anuncios de Estados) | vacío |
   | `mensajeria_persona` | `from` (o `from_user_id` si no hay `from`) | `sender.id` |
   | `mensajeria_entrada` | `timestamp`: ya viene en segundos | `{{ floor(timestamp / 1000) }}`: viene en milisegundos |
   | `telefono` | `+{{from}}` | vacío |
9. **El módulo de tu CRM**, o **HTTP → Make a request**, que crea o actualiza el contacto con esos campos.
   - En GHL: *Create/Update Contact* con los campos personalizados.
   - Si el contacto ya existe y tiene `mensajeria_canal`, no lo pises: el primer anuncio manda.

## Escenario 2 · Cambio de etapa → evento

**Objetivo:** mandar a Meta `LeadSubmitted`, `QualifiedLead` o `Purchase`, una sola vez por hito.

1. **El disparador.** Puede ser el **Custom webhook** que llama tu CRM, con el cuerpo de `ejemplos/crm-etapa.json`.
   Ponle una cabecera secreta y fíltrala en el primer paso. También puede ser el disparador de cambio de etapa del
   módulo de tu CRM.
2. **Filtro:** `mensajeria_canal` es `whatsapp`, `messenger` o `instagram`. Si no, el contacto no vino de un anuncio de
   mensajes y no toca nada.
3. **Tools → Set variable** `evento`. `<<CUALIFICA_EN>>` es la etapa que cuenta como cualificado (`cualificado` por
   defecto):
   ```
   {{ switch(etapa; "lead"; "LeadSubmitted"; "ganado"; "Purchase"; "<<CUALIFICA_EN>>"; "QualifiedLead"; "") }}
   ```
4. **Filtro:** `evento` no está vacío **y** `mensajeria_enviados` no contiene `evento`.
   - Usa el operador «Text operators: Does not contain».
   - Meta no deduplica la mensajería: este filtro es lo único que impide que cuente dos veces.
5. **Filtro de datos.** Mejor que un filtro, un **Router** con una ruta de error que te avise por email o Slack:
   - `Purchase` sin `valor` mayor que 0: falta el importe del proyecto en la oportunidad;
   - WhatsApp sin `mensajeria_clic` y sin teléfono: no hay con qué emparejar;
   - Messenger o Instagram sin `mensajeria_persona`.
6. **Tools → Set variable** `user_data`. Elige la rama según el canal y el clic:

   | Caso | `user_data` |
   |---|---|
   | WhatsApp con clic | `{"whatsapp_business_account_id":"{{mensajeria_cuenta}}","ctwa_clid":"{{mensajeria_clic}}"}` |
   | WhatsApp sin clic (Estados) | `{"whatsapp_business_account_id":"{{mensajeria_cuenta}}","page_id":"<<PAGE_ID>>","ph":["{{sha256(replace(telefono; /\D/g; emptystring))}}"]}` |
   | Messenger | `{"page_id":"{{mensajeria_cuenta}}","page_scoped_user_id":"{{mensajeria_persona}}"}` |
   | Instagram | `{"instagram_business_account_id":"{{mensajeria_cuenta}}","ig_sid":"{{mensajeria_persona}}"}` |

   El hash del teléfono va sin `+` ni espacios y con el prefijo del país. Compáralo con
   `python3 -I herramientas/capi.py hashear --tipo ph "+1 650 555 1212"`, que da `e323ec62…3176`: tienen que coincidir.
7. **HTTP → Make a request:**
   - URL: `https://graph.facebook.com/v27.0/<<DATASET_ID>>/events`
   - Método: `POST`. Body type: Raw, JSON.
   - Autenticación: una **API key** del keychain de Make, en la query, con nombre `access_token`. El token no va
     escrito en la URL ni en el cuerpo.
   - Cuerpo:
     ```json
     {
       "data": [{
         "event_name": "{{evento}}",
         "event_time": {{floor(now / 1000)}},
         "action_source": "business_messaging",
         "messaging_channel": "{{mensajeria_canal}}",
         "user_data": {{user_data}}
       }],
       "test_event_code": "<<TEST_EVENT_CODE>>"
     }
     ```
     En `Purchase`, añade `"custom_data": {"value": {{valor}}, "currency": "{{upper(moneda)}}"}`.
   - En los ajustes del módulo, **sin reintentos**: «Evaluate all states as errors» activado y ningún gestor *Retry*.
     Un reintento duplicaría el evento.
8. **El módulo de tu CRM** guarda `mensajeria_enviados` = `{{mensajeria_enviados}},{{evento}}`. Hazlo solo si la
   respuesta trae `events_received: 1`.

### Antes del envío real

- Deja `test_event_code` mientras pruebas y comprueba la llegada (sección 6 de la guía).
- Para producción hacen falta tres cosas:
  1. el sí del cliente;
  2. **quitar la línea `test_event_code`**;
  3. anotarlo en `clientes/<slug>/change-log.md`.
- Make no tiene un candado como el de n8n (`ENVIO_REAL_APROBADO`). El candado aquí es esa línea: no la borres antes de
  tiempo.
- `event_time` no puede tener más de 7 días. Manda el evento cuando cambia la etapa, no en lotes semanales.
