# Webhook propio: mensajería → Conversions API

Es para quien monta la integración en su propio backend: un servidor, funciones *serverless* o el backend del agente de
IA que vendes. Esto es pseudocódigo con los contratos, no un servicio listo para desplegar. Los campos del CRM, la tabla
de eventos y las reglas están en el [README](README.md).

Si tu backend es Python, puedes importar `herramientas/capi.py` en lugar de reescribirlo:
- `parsear_webhook(payload)` extrae el origen de los tres canales;
- `evento_de_etapa(etapa, cualifica_en)` da el evento de cada etapa;
- `evento_mensajeria(...)` construye el evento;
- `validar({"data": [ev]})` lo revisa antes de enviarlo.

Los tests cubren esas cuatro funciones.

---

## 1. Verificación de la URL (GET)

Meta la llama una vez, al guardar el webhook en la app.

```
GET /meta/mensajeria?hub.mode=subscribe&hub.verify_token=…&hub.challenge=…
  si hub.mode == "subscribe" y hub.verify_token == VERIFY_TOKEN (variable de entorno):
      responder 200, cuerpo = hub.challenge (texto tal cual)
  si no:
      responder 403
```

## 2. Avisos entrantes (POST)

```
POST /meta/mensajeria
  crudo = cuerpo SIN parsear (bytes)
  firma = cabecera "X-Hub-Signature-256"            # "sha256=<hex>"
  esperada = "sha256=" + hex(HMAC_SHA256(clave=APP_SECRET, mensaje=crudo))
  si no comparacion_en_tiempo_constante(firma, esperada):
      responder 401 y registrar "firma no válida" (sin el cuerpo)
      terminar
  responder 200 YA y procesar después (cola o tarea en segundo plano)
  # Meta reintenta los avisos que no reciben 200 a tiempo: el procesado tiene que ser idempotente.

procesar(json(crudo)):
  para cada m en parsear_webhook(payload):           # misma lógica que capi.py parsear_webhook
      si m.anuncio está vacío: seguir                # orgánico o mensaje posterior al primero
      si ya_procesado(m.mensaje_id): seguir           # wamid en WhatsApp, mid en Messenger/IG
      contacto = crm.buscar_o_crear(canal=m.canal, persona=m.identidad, telefono=m.telefono)
      si contacto.mensajeria_canal está vacío:        # el primer anuncio manda; no pises un origen anterior
          crm.guardar(contacto, {
              mensajeria_canal:   m.canal,            # whatsapp | messenger | instagram
              mensajeria_cuenta:  m.cuenta,           # WABA (entry.id) | Página | cuenta IG (recipient.id)
              mensajeria_anuncio: m.anuncio,          # referral.source_id | referral.ad_id
              mensajeria_clic:    m.ctwa_clid o "",   # solo WhatsApp; vacío en anuncios de Estados
              mensajeria_persona: m.identidad,        # wa_id o BSUID | PSID | IGSID
              mensajeria_entrada: m.momento,          # epoch en SEGUNDOS (Messenger/IG llegan en ms)
          })
      # si es la primera vez, aquí arranca tu bot o tu agente de IA
```

Detalles que rompen la integración si se ignoran:
- **WhatsApp.** `entry[].changes[].value.messages[].referral` solo existe en el primer mensaje tras el clic.
  - El `timestamp` es un texto con segundos.
  - Las personas con nombre de usuario pueden llegar sin `from`. Usa `from_user_id` o `contacts[].user_id` (BSUID).
- **Messenger e Instagram.** `entry[].messaging[].message.referral`, con `source = "ADS"` y `ad_id`. El `timestamp` va en
  milisegundos.
  - Descarta los mensajes con `is_echo: true`: los ha escrito el negocio.
  - En Messenger, si la persona ya tenía un hilo abierto, el clic llega como evento `messaging_referrals`. Suscríbelo.
- **Estados de entrega** (`statuses`): no son mensajes. Ignóralos.

## 3. Cambio de etapa (lo llama tu CRM)

```
POST /crm/etapa        cabecera X-Secreto == CRM_SECRET; cuerpo = ejemplos/crm-etapa.json
  c = cuerpo
  si c.mensajeria_canal no está en (whatsapp, messenger, instagram): responder 200 y terminar
  evento = evento_de_etapa(c.etapa, CUALIFICA_EN)    # lead→LeadSubmitted, CUALIFICA_EN→QualifiedLead, ganado→Purchase
  si no hay evento: responder 200 y terminar         # diagnóstico, llamada, asistencia, propuesta, perdido
  si evento está en c.mensajeria_enviados: responder 200 y terminar     # Meta NO deduplica la mensajería

  con bloqueo(contacto_id + evento):                  # dos cambios casi a la vez no deben mandar dos veces
      momento = c.momento o ahora                     # segundos; rechaza > 7 días o en el futuro
      user_data = según canal:
          whatsapp con clic:   {whatsapp_business_account_id: c.mensajeria_cuenta, ctwa_clid: c.mensajeria_clic}
          whatsapp sin clic:   {whatsapp_business_account_id, page_id: PAGE_ID, ph: [sha256(solo_digitos(c.telefono))]}
          messenger:           {page_id: c.mensajeria_cuenta, page_scoped_user_id: c.mensajeria_persona}
          instagram:           {instagram_business_account_id: c.mensajeria_cuenta, ig_sid: c.mensajeria_persona}
      ev = {event_name: evento, event_time: momento, action_source: "business_messaging",
            messaging_channel: c.mensajeria_canal, user_data}
      si evento == "Purchase":
          exigir c.valor > 0 y moneda ISO de 3 letras; si falta → alerta a una persona, NO enviar
          ev.custom_data = {value: c.valor, currency: c.moneda}
      errores = validar({data: [ev]})                 # capi.validar o tus propias reglas
      si errores: alerta y terminar

      cuerpo = {data: [ev]}
      si TEST_EVENT_CODE: cuerpo.test_event_code = TEST_EVENT_CODE
      si no, y ENVIO_REAL_APROBADO != true: alerta "sin código de prueba" y terminar

      r = POST https://graph.facebook.com/v27.0/{DATASET_ID}/events?access_token={token del almacén de secretos}
               JSON cuerpo, timeout 30 s
      si r.status == 200 y r.events_received == 1:
          crm.guardar(contacto, mensajeria_enviados += evento)
          registrar(contacto_id, evento, fbtrace_id)  # sin teléfonos ni hashes
      si no:
          registrar(contacto_id, evento, código y subcódigo de error)
          alerta a una persona                        # NUNCA reintento automático
```

## 4. Reglas

- **Ningún reintento a ciegas.** Si la petición agota el tiempo, no sabes si Meta la recibió. Márcala como «pendiente de
  revisar» y que una persona decida. Un duplicado en mensajería no se puede deshacer.
- **Secretos en el entorno o en un gestor de secretos:**
  - `APP_SECRET`, `VERIFY_TOKEN`, `CRM_SECRET`;
  - el token de la CAPI, con el permiso `whatsapp_business_manage_events`, `page_events` o `instagram_manage_events`
    según el canal.

  Ninguno va en el repositorio ni en los registros.
- **Registros sin datos personales.** Guarda IDs de contacto, eventos, `fbtrace_id` y errores; nada de teléfonos,
  hashes ni cuerpos completos. El hash de un teléfono también es un dato personal.
- **Un dataset por negocio.**
  - El dataset tiene que estar vinculado a la WABA (`POST /{WABA_ID}/dataset`) o a la Página.
  - Si la WABA y el dataset están en Business Managers distintos, Meta devuelve el error 100. Es un problema de quién
    es el dueño de cada activo: resuélvelo ahí, no con más permisos.
- **Versión de la API:** el sistema usa la `v27.0` desde el 2026-11-10 (`META_API_VERSION` en las herramientas). Si
  cambia, cambia en todo el sistema a la vez: herramientas, plantillas y flujos ya montados.
