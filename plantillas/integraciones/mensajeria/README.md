# Plantillas: mensajería → Conversions API

Sirven para que una conversación que empieza en un anuncio vuelva a Meta como lead, lead cualificado o venta. Valen
para Click to WhatsApp, Click to Messenger e Instagram Direct. Explicación completa, pruebas y campaña:
[`docs/guias/mensajeria.md`](../../../docs/guias/mensajeria.md).

| Archivo | Para quién |
|---|---|
| `n8n-mensajeria-capi.json` | Quien usa n8n. Se importa tal cual: Workflows → Import from File. |
| `make-mensajeria.md` | Quien usa Make. Son dos escenarios montados a mano, módulo a módulo. |
| `webhook-propio.md` | Quien tiene backend propio, sea un servidor o funciones *serverless*. Es pseudocódigo con los contratos. |
| `ejemplos/*.json` | Webhooks de Meta de muestra y el cuerpo que manda el CRM. Sirven para probar sin un clic real. |

Las tres versiones tienen la misma lógica que `herramientas/capi.py`, y los tests comparan n8n con la herramienta:
- lo que se extrae del webhook;
- la tabla etapa → evento;
- el hash del teléfono;
- el bloqueo sin código de prueba.

## Las dos piezas

1. **Entrada.** Llega el primer mensaje desde un anuncio y el webhook de Meta trae el `referral`.
   - En WhatsApp trae el `ctwa_clid` y el ID del anuncio.
   - En Messenger e Instagram trae el ID del anuncio y el identificador de la persona.
   - **Solo llega en ese primer mensaje.** Si no lo guardas en ese momento, se pierde.
2. **Cambio de etapa.** El CRM avisa cuando el contacto cambia de etapa. Las etapas son las del contrato §16.
   - Si a esa etapa le toca evento y aún no se ha mandado, se envía una vez a `POST /{dataset}/events`.
   - La petición lleva `action_source=business_messaging` y el canal.

## Campos que guardas en el contacto del CRM

Créalos como campos personalizados. En GHL: Settings → Custom Fields, tipo texto.

| Campo | Qué guarda | De dónde sale |
|---|---|---|
| `mensajeria_canal` | `whatsapp`, `messenger` o `instagram` | Entrada |
| `mensajeria_cuenta` | WABA (WhatsApp), Página (Messenger) o cuenta profesional (Instagram) | Entrada (`entry[].id` o `recipient.id`) |
| `mensajeria_anuncio` | ID del anuncio | Entrada (`source_id` o `ad_id`) |
| `mensajeria_clic` | `ctwa_clid`. Va vacío en Messenger, Instagram y anuncios de Estados | Entrada |
| `mensajeria_persona` | `wa_id` o BSUID, PSID o IGSID | Entrada |
| `mensajeria_entrada` | Hora del primer mensaje (epoch en segundos) | Entrada |
| `mensajeria_enviados` | Eventos ya mandados, separados por comas | Lo escribe el flujo tras cada envío |

Además usa los campos normales del contacto: teléfono con prefijo y, en la oportunidad, el importe y la moneda.
`ejemplos/crm-etapa.json` es el cuerpo exacto que el CRM debe mandar al webhook de cambio de etapa.

## Tabla etapa → evento

| Etapa del §16 | Evento de mensajería |
|---|---|
| `lead` | `LeadSubmitted` |
| `cualificado` (o la que fijes en `CUALIFICA_EN`: `llamada`, `asistio` o `propuesta`) | `QualifiedLead` |
| `ganado` | `Purchase`, con `value` y `currency` obligatorios |
| `diagnostico`, `llamada`, `asistio`, `propuesta`, `perdido` | Ninguno. Se quedan en el CRM y se miden allí. |

`Lead`, `Schedule` y los nombres propios **no existen en mensajería**: Meta los rechaza. Si una llamada se reserva en la
web, va por la CAPI web, con el `event_id` del píxel.

## Marcadores

Todo lo que tienes que rellenar va entre `<<` y `>>`. Ninguna plantilla trae credenciales:
- el token de la Conversions API va en el almacén de credenciales (de n8n, de Make o el tuyo);
- el secreto de la app va en una variable de entorno;
- nada de eso va en el flujo ni en el chat.

## Reglas de las tres versiones

- **Sin `TEST_EVENT_CODE` no sale nada.** Para enviar de verdad hacen falta dos cosas:
  - cambiar `ENVIO_REAL_APROBADO` a `true`;
  - el sí del cliente, después de verificar las pruebas.
- **Sin reintentos automáticos.** Meta no deduplica la mensajería y un reintento cuenta doble. Si falla, revisa a mano
  el error y vuelve a lanzar ese contacto.
- **Firma comprobada.** Un aviso sin `X-Hub-Signature-256` válida se descarta.
- **Sin datos personales en los registros.** Guarda los IDs y el resultado de Meta, no los teléfonos.
