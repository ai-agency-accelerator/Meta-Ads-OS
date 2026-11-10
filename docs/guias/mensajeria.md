# Mensajería medida: Click to WhatsApp, Messenger e Instagram Direct que vuelven a Meta

**Para quién.** Consultoras y agencias de IA y automatización, y SaaS, que venden a pymes. Estos negocios llevan el
anuncio a una conversación, que atiende una persona o un asistente que cualifica y agenda.

**Qué consigues.** Que cada conversación que nace en un anuncio vuelva a Meta como lead, lead cualificado o venta,
verificada con eventos de prueba antes de tocar el dataset real. Sin esto, Meta solo ve «conversaciones iniciadas»: no
distingue al curioso del cliente que paga 6.000 €.

**De dónde sale cada regla.** El paso a paso con el cliente lo llevan `/disenar-funnel`, que decide si toca mensajería, y
`/implementar-capi`, que monta la señal. El porqué está en `meta-ads-kb/07-instagram-placements-mensajeria/`:
- `11-whatsapp-ads-ctwa.md`, el anuncio y la ventana gratuita;
- `12-whatsapp-business-platform-medicion-revenue.md`, la medición;
- `13-business-ai-agentes-mensajeria.md`, el agente de Meta;
- `14-funnels-de-mensajeria.md`, el funnel.

Para consultoras, además, `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §5.6.

Las plantillas están en [`plantillas/integraciones/mensajeria/`](../../plantillas/integraciones/mensajeria/README.md):
un flujo de n8n, una guía de Make, pseudocódigo de backend y ejemplos.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial de Meta el 2026-11-09. Las
fuentes están al final.

---

## 1. ¿Merece la pena la mensajería?

En venta consultiva, el anuncio de mensajes compite con el formulario instantáneo y con la landing con diagnóstico.

| Elige… | Cuando… | Lo que pagas |
|---|---|---|
| **Mensajería** (WhatsApp, Messenger, Instagram Direct) | El comprador tiene dudas antes de dar sus datos («¿esto sirve para mi caso?»). Tienes a alguien o algo que responde en minutos, también fuera de horario. El mercado vive en WhatsApp (LatAm, sur de Europa). Haces retargeting de quien ya vio un caso. | Conversaciones que no llevan a nada. Sin la señal de esta guía, Meta optimiza a conversar, no a cualificar. |
| **Formulario instantáneo** | Quieres volumen y tienes un proceso comercial rápido para filtrar. Conversion Leads necesita el Lead ID: es la vía más madura para optimizar a cualificados. | Leads de baja intención si el formulario es fácil. |
| **Landing con diagnóstico** | La oferta necesita explicación, prueba y una calculadora. Quieres píxel más CAPI web con `event_id` y la cita en tu calendario. | Más fricción y menos volumen. |

**Reglas de decisión** `[STRONG INFERENCE]` (`14-funnels-de-mensajeria.md` §1 y playbook de consultoras §5):

1. **Si nadie responde en 5 minutos en horario, no hay mensajería.** Si la primera respuesta tarda más de 24 horas, se
   pierde además la ventana gratuita. `[OFFICIAL META]` (regla de las 24 h, `11-…` §3)
2. **Si el cliente no puede guardar el `ctwa_clid`** (solo usa la app de WhatsApp Business sin API ni BSP), la
   mensajería se mide con etiquetas a mano o no se mide (§3, vía D). Dilo antes de vender la campaña.
3. **En España y el resto de la UE no prometas optimizar a leads.**
   - El Help Center avisa de que ciertas funciones de mensajería no están disponibles para anuncios entregados a o
     desde Europa (y Japón, y Corea del Sur según la página). Con objetivo Clientes potenciales y destino WhatsApp, la
     opción por defecto es **maximizar conversaciones**. `[OFFICIAL META]`
   - Una página de WhatsApp Business dice que la optimización a leads «no está disponible en la UE, Reino Unido, Japón
     o Corea del Sur». El Help Center no lo dice con esas palabras ni menciona el Reino Unido. `[CONTESTED]`
   - **Compruébalo en Ads Manager con la cuenta del cliente** antes de planificar.
   - La señal sigue valiendo en la UE: mides el coste por cualificado por anuncio y decides creatividades con él.
4. **Instagram Direct sirve para medir, no para optimizar a ventas.** La optimización a compras por mensajería existe
   para Messenger y WhatsApp, no para Instagram. `[OFFICIAL META]`

---

## 2. Qué puede recibir Meta

La Conversions API para mensajería empresarial es un endpoint aparte del web.

| | WhatsApp (CTWA) | Messenger (CTM) | Instagram Direct |
|---|---|---|---|
| `action_source` | `business_messaging` | `business_messaging` | `business_messaging` |
| `messaging_channel` | `whatsapp` | `messenger` | `instagram` |
| Identidad (`user_data`) | `whatsapp_business_account_id` + `ctwa_clid` | `page_id` + `page_scoped_user_id` (PSID) | `instagram_business_account_id` + `ig_sid` (IGSID) |
| Sin click ID | `page_id` + WABA + un dato de cliente hasheado (teléfono) | No aplica | No aplica |
| Permiso del token | `whatsapp_business_manage_events` | `page_events` | `instagram_manage_events` |
| Optimizar a compras | Sí | Sí | No |

**Eventos admitidos (lista cerrada).**
- `LeadSubmitted`, `QualifiedLead`, `Purchase`, `InitiateCheckout`, `AddToCart`, `ViewContent`;
- `OrderCreated`, `OrderShipped`, `OrderDelivered`, `OrderCanceled`, `OrderReturned`;
- `CartAbandoned`, `RatingProvided`, `ReviewProvided`.

`Lead`, `Schedule` y los nombres propios **no valen**. Proveedores reportan el rechazo con el subcódigo 2804066
`[EMPIRICAL]`. `Purchase` lleva `value` y `currency`. `[OFFICIAL META]`

**Meta no deduplica estos eventos.** Cada hito se manda una sola vez y el control lo llevas tú, en el CRM.
`[OFFICIAL META]`

**El `ctwa_clid` no siempre llega.**
- Meta lo omite en los anuncios de **Estados** de WhatsApp. `[OFFICIAL META]`
- Los usuarios con nombre de usuario pueden llegar sin número (`from`): usa su BSUID (`from_user_id`). `[OFFICIAL META]`

En el primer caso la vía es la de «sin click ID» (teléfono hasheado). En el segundo, sin `ctwa_clid` no hay con qué
emparejar.

**Detección automática (Automatic Events API).** Meta puede detectar `LeadSubmitted` y `Purchase` en las conversaciones
de los partners que la activan. **No está disponible en la UE, Reino Unido, Japón ni Corea del Sur.** `[OFFICIAL META]`
Fuera de esos mercados, pregunta a tu BSP si la tiene. Aun así, `QualifiedLead` con tu criterio solo lo mandas tú.

---

## 3. Elige la arquitectura

| Vía | Cuándo | Señal |
|---|---|---|
| **A. BSP con CAPI de mensajería integrada** | El cliente ya atiende WhatsApp con un proveedor que lo ofrece: guarda el `ctwa_clid` y manda eventos por etiqueta o etapa. | Completa. Comprueba qué eventos manda y que no duplica con los tuyos. |
| **B. Cloud API propia con estas plantillas** | Construyes tú el asistente o la integración: es lo que vende una consultora de automatización. | Completa y bajo tu control (§4–§8). |
| **C. GHL sin `ctwa_clid`** | El cliente vive en GoHighLevel. GHL no reenvía el `ctwa_clid` `[EMPIRICAL]`: es una petición abierta en su tablero de ideas, no documentación oficial. | WhatsApp: teléfono hasheado + `page_id` + WABA (menos precisa). La acción CAPI nativa de GHL **no cubre mensajería**. |
| **D. Solo la app de WhatsApp Business** | Pyme pequeña, sin API. | Etiquetas de chat («lead», «pagado») dentro de la app. Meta las cuenta para optimizar a leads donde esa opción existe: ≥10 eventos de lead o compra en 30 días y chats etiquetados en ≤7 días `[OFFICIAL META]`. No llegan a tu CRM. |

**La vía C, en detalle.** Si el cliente usa GHL y quieres el `ctwa_clid`, hay una opción `[HYPOTHESIS]`, no
verificada con GHL: suscribir tu propia app a los webhooks de la WABA en paralelo y guardar el origen con la plantilla.
- Antes de proponerlo, prueba que GHL sigue recibiendo los mensajes con las dos suscripciones.
- Si no, quédate con la vía sin clic: el teléfono que guarda GHL, hasheado, más `page_id` y WABA.

**Coexistencia** (la misma línea en la app de WhatsApp Business y en la Cloud API, a través de un BSP). Los mensajes
llegan por webhook. No está verificado que el `referral` llegue igual que en la Cloud API pura: compruébalo con tu propio
clic (§7).

---

## 4. Requisitos

**Cuentas y app**
- **WhatsApp:**
  - una WABA con el número en la Cloud API, propia o a través de un BSP;
  - una app de Meta for Developers de tipo empresa con el producto WhatsApp y el webhook suscrito al campo `messages`.
- **Messenger:** la Página conectada a la app, con el webhook `messages` y `messaging_referrals`. Este último trae el
  clic cuando la persona ya tenía un hilo abierto.
- **Instagram:** la cuenta profesional conectada a la app, con el webhook `messages`.
- **El secreto de la app** sirve para comprobar la firma `X-Hub-Signature-256` de cada aviso. Va en una variable de
  entorno del servidor o de n8n, nunca en el flujo.

**Dataset**
- El dataset tiene que estar **vinculado** a la WABA (`POST /{WABA_ID}/dataset` lo crea o lo devuelve), a la Página o a
  la cuenta de Instagram. El dataset es del negocio: los partners reciben acceso. `[OFFICIAL META]`
- **Usa el dataset que devuelve la vinculación.** Si es distinto del dataset del píxel, anótalo en la ficha como
  `meta.dataset_mensajeria`. `capi.py` lo prefiere a `meta.dataset`.
- **Error 100** si la WABA y el dataset están en Business Managers distintos `[STRONG INFERENCE]` (`12-…` §4.3).
  Alinea quién es el dueño de cada activo antes de pedir más permisos.

**Token**
- Un token de usuario del sistema con los activos asignados (WABA, Página, cuenta de Instagram, dataset) y el permiso
  del canal (tabla del §2).
- Si atiendes a clientes que no son tuyos, la app necesita acceso avanzado a esos permisos (revisión de la app).
  `[OFFICIAL META]`
- **Dónde va:**
  - lo pega el usuario en `.env` como `META_CAPI_MENSAJERIA_TOKEN_<SLUG>` o en el almacén de credenciales de n8n o
    Make;
  - `capi.py` prueba con `META_CAPI_TOKEN` si no existe y avisa;
  - nunca en el chat.

**Ficha del cliente** (`clientes/<slug>/ficha.md`, bloque `meta`). Todas son opcionales, y la orden de `capi.py` las
puede pasar:
- `waba`: ID de la cuenta de WhatsApp Business;
- `pagina`: ya existe;
- `instagram`: el **ID numérico** de la cuenta profesional, no el @;
- `dataset_mensajeria`.

**Versión de la API.** El sistema usa la `v27.0` desde el 2026-11-10, la misma que los ejemplos de la documentación de
mensajería. Las plantillas de `plantillas/integraciones/mensajeria/` ya la llevan; si montaste un flujo antes, cambia la
`v26.0` de su URL (la v26.0 sigue funcionando mientras Meta no fije su fin).

---

## 5. Capturar el origen del clic

El `referral` solo llega **en el primer mensaje** tras el clic. Si no lo guardas en ese momento, se pierde para
siempre. Guárdalo en el contacto del CRM, en los campos `mensajeria_*` del
[README de las plantillas](../../plantillas/integraciones/mensajeria/README.md).

**Para comprobar que tu webhook trae lo que hace falta**, guarda un aviso real (o el ejemplo) en `privado/` y léelo:

```
python3 -I herramientas/capi.py origen clientes/acme/privado/webhook.json
```
```
whatsapp  cuenta 100000000000001 · wa_id ***12 · anuncio 120000000000000123 · ctwa_clid ARAkEj… · 2025-11-11T09:00:00+00:00
1 mensaje(s) entrante(s), 1 con el anuncio de origen.
```

- **La salida tapa** el número y el clic.
- **`--salida clientes/acme/privado/origen.json`** guarda los datos completos, y solo dentro de `privado/`.
- **`--json`** da la salida para otro programa.
- **Avisos que verás:**
  - «sin referral»: es orgánico o no es el primer mensaje;
  - «referral sin ctwa_clid»: es un anuncio de Estados, así que vía sin clic;
  - «nombre de usuario»: no hay número.
- **Los ejemplos de los tres canales** están en `plantillas/integraciones/mensajeria/ejemplos/`.

Messenger e Instagram mandan la hora en milisegundos y WhatsApp en segundos: `capi.py` y las plantillas lo convierten.

---

## 6. De la etapa al evento

Las etapas son las del contrato §16, las mismas que el pipeline de GHL (playbook de consultoras §5.7).

| Etapa | Evento de mensajería | Comentario |
|---|---|---|
| `lead` | `LeadSubmitted` | La persona deja lo mínimo para hablar con ella. Defínelo con exigencia: es lo que Meta optimiza donde puede optimizar a leads `[STRONG INFERENCE]`. |
| `diagnostico` | — | Se queda en el CRM. |
| `cualificado` | `QualifiedLead` | Tu criterio escrito: encaje, presupuesto y urgencia. |
| `llamada`, `asistio`, `propuesta` | — | Si la llamada se reserva en tu web, `Schedule` va por la CAPI web, con el `event_id` del píxel. |
| `ganado` | `Purchase` + `value` + `currency` | El importe del proyecto. |
| `perdido` | — | Sirve para medir; no se manda. |

Son nombres distintos de los de la web y el CRM (`Lead`, `LeadCualificado`…, la tabla canónica del contrato §16)
porque mensajería solo admite la lista cerrada de Meta. `capi.py construir --etapa` pone el que toca: con `--canal`,
el de mensajería; sin él, el del §16.

**Si tu filtro de calidad es la llamada** y no una etiqueta, porque el asistente agenda dentro del chat:
`--cualifica-en llamada` (o `CUALIFICA_EN` en n8n). Entonces `llamada` se manda como `QualifiedLead` y `cualificado` ya
no manda nada, para no contar dos veces. Solo puede haber una etapa así por cliente.

```
python3 -I herramientas/capi.py construir --canal whatsapp --etapa cualificado --cliente acme \
    --desde-webhook clientes/acme/privado/webhook.json --salida clientes/acme/privado/ev-mensajeria.json
python3 -I herramientas/capi.py construir --canal whatsapp --etapa ganado --waba 100000000000001 \
    --ctwa-clid <clid> --valor 4800 --moneda EUR
python3 -I herramientas/capi.py construir --canal messenger --etapa lead --pagina <id> --psid <psid>
python3 -I herramientas/capi.py validar clientes/acme/privado/ev-mensajeria.json
```

**Lo que hace `capi.py` por ti.**
- WhatsApp sin clic pasa a la vía del teléfono (`page_id` + `ph` hasheado).
- Rechaza lo que no va en mensajería: URL, IP, *user agent*, `fbc`/`fbp`, Lead ID, `--crm` y `external_id` (este no
  sirve para emparejar aquí).
- Avisa si el evento llega más de 7 días después de la entrada (`--entrada-conversacion`).
- `validar` detecta:
  - un hito repetido en el mismo lote;
  - un identificador hasheado que no debía hashearse;
  - un lote que mezcla mensajería y web: se envían por separado.

---

## 7. Probar con eventos de prueba

**Regla del sistema:** primero con `test_event_code`, luego producción con el sí del cliente. Meta tampoco descarta los
eventos de prueba (dice que los usa para segmentación y medición). Por eso, prueba con **tu** identidad, no con leads
reales.

1. **En local, sin red.** `origen`, `construir` y `validar` con los ejemplos. Así compruebas la forma, no el
   emparejamiento.
2. **El código de prueba.** Events Manager → el dataset → *Probar eventos* → copia el código.
3. **Tu propio clic:**
   - **Messenger e Instagram:** escribe desde tu cuenta personal a la Página o a la cuenta del cliente a través del
     anuncio. Así obtienes tu PSID o IGSID en el webhook.
   - **WhatsApp:** necesitas un `ctwa_clid` real, y solo sale de un clic en un anuncio. Puede salir de dos sitios:
     - la vista previa del anuncio en tu móvil, que es gratis (no verificado que genere `ctwa_clid`);
     - el anuncio ya activo, que cuesta un clic. Va **en pausa** por `/lanzar-campana`, y para activarlo hace falta el
       sí explícito.
4. **Enviar la prueba:**
   ```
   python3 -I herramientas/capi.py enviar clientes/acme/privado/ev-mensajeria.json --cliente acme --test-code TEST12345
   ```
   - Responde con `events_received: 1` y el `fbtrace_id`.
   - Si Meta rechaza el evento, `capi.py` explica el subcódigo. 2804066 es un evento que no existe en mensajería.
5. **Dónde mirarlo.** En *Probar eventos* tiene que aparecer como mensajería empresarial, con el canal. No está
   verificado que esa pestaña muestre siempre los eventos de mensajería. Si no aparece pero `events_received` es 1:
   - espera 20–30 minutos y revisa la vista general del dataset;
   - antes de pasar a producción, comprueba que no ha llegado como evento web por un `action_source` equivocado.
6. **En n8n o Make**, el mismo recorrido:
   - pega el ejemplo de `ejemplos/crm-etapa.json` en el webhook de cambio de etapa, con `TEST_EVENT_CODE` relleno;
   - después, haz un cambio de etapa real de tu contacto de prueba en el CRM.

---

## 8. Automatizar

| Herramienta | Plantilla |
|---|---|
| n8n | `plantillas/integraciones/mensajeria/n8n-mensajeria-capi.json`. Se importa tal cual, con tres tramos: verificación, entrada y cambio de etapa. Sin código de prueba no envía, y para el envío real hace falta `ENVIO_REAL_APROBADO`. |
| Make | `plantillas/integraciones/mensajeria/make-mensajeria.md`: dos escenarios módulo a módulo. |
| Backend propio o tu agente de IA | `plantillas/integraciones/mensajeria/webhook-propio.md`. En Python, importa `capi.py`. |
| GHL | Webhook de salida del workflow *Pipeline Stage Changed* (con «Allow Multiple») hacia el tramo «cambio de etapa» de n8n o Make, con el cuerpo de `crm-etapa.json`. No uses la acción CAPI nativa para estos contactos. |

**Lo que no se negocia en ninguna versión:**
- se comprueba la firma de Meta;
- el origen del primer anuncio no se sobrescribe;
- cada hito sale una vez (`mensajeria_enviados`);
- no hay reintentos automáticos;
- una venta sin importe para el flujo con un error a la vista, no se pierde en silencio;
- los registros no llevan teléfonos.

---

## 9. La campaña

Se crea con `/lanzar-campana`, siempre **en pausa**. Aquí solo lo que cambia con mensajería. Los nombres de los menús
pueden variar y no están verificados.

- **Objetivo:** Clientes potenciales (Leads). Ubicación de la conversión: apps de mensajes, ya sea WhatsApp, Messenger,
  Instagram o varias.
- **Objetivo de rendimiento.** Elige según lo que ofrezca la cuenta:
  - **fuera de la UE**, «maximizar clientes potenciales por mensajes» cuando tengas ≥10 `LeadSubmitted` o compras en 30
    días `[OFFICIAL META]`;
  - **en la UE**, normalmente solo «maximizar conversaciones» (§1).
  - **No cambies el objetivo cada semana.** La señal se acumula en el dataset aunque optimices a conversaciones.
- **Mensaje de bienvenida y mensaje predefinido.**
  - Un saludo que diga quién responde. Si es un asistente, dilo: art. 50 del Reglamento de IA, playbook de
    consultoras §5.6.
  - Un mensaje predefinido con un código corto del anuncio, por ejemplo «Quiero el diagnóstico (DX-NOV)».
  - El código identifica la campaña donde no llega el `referral`: app sin API o anuncios de Estados.
- **Preguntas frecuentes (*ice breakers*).** 3–4 preguntas que ya cualifican, por ejemplo «¿Cuántas horas a la semana
  se van en esto?». Sirven para medir la intención, no para rellenar.
- **Varios destinos** (WhatsApp más Messenger más Instagram). Meta reparte según la persona. Los tres canales tienen que
  estar en el webhook y en el flujo, o perderás el origen de una parte. `[STRONG INFERENCE]`
- **La ventana gratuita.** La página oficial de precios dice que, si respondes en 24 horas, la conversación desde CTWA
  queda gratis hasta 7 días. También dice que cada número tiene 1.000 mensajes de servicio gratis al mes. `[OFFICIAL
  META]`, leído el 2026-11-09; la KB todavía lo marca como `[CONTESTED]`. Los tokens del agente de Meta se cobran
  también dentro de la ventana.

---

## 10. Verificar en producción (48–72 horas)

| Comprobación | Bien si… | Si no |
|---|---|---|
| Origen guardado | Los contactos nuevos de anuncios de WhatsApp tienen `mensajeria_anuncio`, y los de no-Estados también `mensajeria_clic`. Objetivo: casi todos `[HYPOTHESIS]`. | El webhook no llega, falta el campo suscrito, otro sistema sobrescribe el contacto o es la vía C. |
| Eventos frente al CRM | Los `LeadSubmitted`, `QualifiedLead` y `Purchase` de Events Manager cuadran con los cambios de etapa de esos días. | Revisa errores del flujo y `mensajeria_enviados`. |
| Sin duplicados | Ningún contacto tiene el mismo evento dos veces. | Un reintento o dos flujos mandando a la vez. Apaga uno. |
| Puntualidad | Cada evento sale minutos después del cambio de etapa. | Envíos por lotes: Meta rechaza `event_time` de más de 7 días. |
| Canal correcto | Cada evento lleva el canal por el que entró la persona. | `mensajeria_canal` mal mapeado. |
| Envío real aprobado | Ya no hay `test_event_code`, con el cambio anotado en `clientes/<slug>/change-log.md`. | — |

---

## 11. Leer por anuncio: el coste por cualificado

Las conversaciones de Meta no son la métrica de negocio. Decide creatividades con el **coste por lead cualificado del
CRM** (CPQL) por anuncio. El orden de lectura, de arriba abajo, es este (`14-…` §4):
1. coste por conversación;
2. porcentaje de cualificación;
3. CPQL;
4. porcentaje de llamadas;
5. coste por cliente.

```
python3 -I herramientas/ghl.py por-anuncio --cliente acme --desde 2026-10-01 --hasta 2026-10-31 \
    --campo-anuncio <ID del campo mensajeria_anuncio>
```

**Ventana de 7 días tras el clic.** Un `Purchase` que llega 5 semanas después de la conversación queda fuera de la
ventana: Meta no lo atribuirá al anuncio. `[STRONG INFERENCE]`
(`meta-ads-kb/04-tracking-atribucion-medicion/10-atribucion-ventanas-y-modelos.md`)
- En consultoría el ciclo suele ser más largo: `QualifiedLead` es la señal útil para Meta, y `Purchase` sirve sobre
  todo para tu informe de caja.
- `capi.py construir --entrada-conversacion` avisa cuando ocurre.
- Con pocas ventas al mes, optimizar a compras no es viable: no hay volumen para aprender.

---

## 12. Frente al agente de Meta (Meta Business Agent)

Tu cliente va a preguntar por qué pagarte si Meta ya tiene un agente.

**Lo que es** `[OFFICIAL META]` (`13-…` §2):
- responde, cualifica, agenda y vende en WhatsApp, y en Messenger según el blog, que también anuncia Instagram;
- puede llamar a tus APIs y webhooks;
- pasa a suscripción de pago, y sus tokens se cobran dentro de la ventana gratuita.

**Lo que no es:**
- **Excluye verticales:** salud, finanzas, administración pública, alcohol, juego, medicamentos sin receta y
  matrimonio. Una Clínica Sonrisa no puede usarlo.
- **Bloqueo por agente de terceros.** Si en el número hay un agente de terceros autorizado y activo, el agente de Meta
  queda bloqueado. Hay que elegir arquitectura por número.
- **No documenta eventos de Conversions API.** Que cualifique en el chat no significa que Meta lo use como señal.
  `[HYPOTHESIS]`

**Cómo posicionarte** `[STRONG INFERENCE]`:
1. **No vendas «un bot».** Responder es la parte que Meta ya regala o cobra barata. Lo que vendes es:
   - conversaciones cualificadas **medidas**;
   - el CPQL por anuncio;
   - la señal de vuelta a Meta;
   - la integración con su agenda, su CRM y su programa.
2. **Sé honesto con el caso pequeño.** Poco volumen, preguntas simples y sin CRM: el agente de Meta puede bastar
   (`13-…` §6). Ganas confianza para el proyecto grande.
3. **El híbrido.** Si el cliente elige el agente de Meta, puedes vender la capa de medición: el agente llama a tu
   webhook al cualificar o agendar y tu sistema manda `QualifiedLead`. No está verificado que tu app siga recibiendo el
   `referral` con el agente de Meta activo: pruébalo con tu clic antes de prometerlo.
4. **Lo regulado.** En salud y finanzas, la IA hace triaje y agenda y la venta la hace una persona.
   - En los eventos solo van `value` y `currency`: nunca el motivo de la consulta ni datos de salud.
   - El asistente es del negocio. WhatsApp veta los asistentes de IA de propósito general, no los de atención o venta
     del propio negocio (`12-…` §2).

---

## Errores frecuentes

| Síntoma | Causa probable |
|---|---|
| Meta rechaza el evento (2804066) | `Lead`, `Schedule` o un nombre propio. En mensajería: `LeadSubmitted`, `QualifiedLead`, `Purchase`… |
| Contactos de anuncio sin `ctwa_clid` | Anuncio de Estados, `referral` buscado en un mensaje posterior al primero, BSP o GHL que no lo reenvía |
| Error 100 al enviar | Dataset no vinculado a la WABA o la Página, o en otro Business Manager |
| Permisos insuficientes | Token sin `whatsapp_business_manage_events`, `page_events` o `instagram_manage_events`, o sin el activo asignado |
| Ventas que no salen en Ads Manager | Más de 7 días entre el clic y la venta, o `Purchase` sin `value`/`currency` |
| Leads dobles en Meta | Reintentos, dos flujos (BSP y el tuyo) o el CRM que dispara dos veces la etapa |
| Messenger sin origen en contactos con hilo previo | Falta suscribir `messaging_referrals` |
| La firma no cuadra | Se calcula sobre el JSON reformateado en vez del cuerpo crudo, o con otro secreto de app |
| `event_time` rechazado | Hora en milisegundos (Messenger o Instagram) sin pasar a segundos, o más de 7 días |

## Lo que no está verificado

- Que *Probar eventos* muestre siempre los eventos de mensajería.
- Que la vista previa de un anuncio genere un `ctwa_clid` válido.
- Que el `referral` llegue en coexistencia y con el agente de Meta activo en el número.
- Que una segunda app pueda suscribirse a la WABA de un cliente de GHL sin cortar a GHL.
- El nombre de la clave de Instagram. La página de mensajería usa `instagram_business_account_id`; la lista general de
  parámetros cita `ig_account_id`. `capi.py` usa la primera y avisa si ve la segunda. `[CONTESTED]`
- Los menús de Ads Manager y de Make, que pueden variar por cuenta y región.

## Fuentes (leídas el 2026-11-09)

- Conversions API for Business Messaging: <https://developers.facebook.com/documentation/ads-commerce/conversions-api/business-messaging>
- Webhooks de WhatsApp (mensajes, `referral`): <https://developers.facebook.com/documentation/business-messaging/whatsapp/webhooks/reference/messages/text>
- Webhooks de Messenger: <https://developers.facebook.com/docs/messenger-platform/reference/webhook-events/messages> y `messaging_referrals`
- Webhooks de Instagram: <https://developers.facebook.com/documentation/business-messaging/instagram-messaging/webhooks>
- Parámetros de cliente: <https://developers.facebook.com/docs/marketing-api/conversions-api/parameters/customer-information-parameters>
- Precios de WhatsApp: <https://developers.facebook.com/documentation/business-messaging/whatsapp/pricing>
- Automatic Events API: <https://developers.facebook.com/documentation/business-messaging/whatsapp/embedded-signup/automatic-events-api>
- Meta Business Agent: <https://developers.facebook.com/documentation/meta-business-agent/overview>
- Optimización a leads en mensajería y restricción europea: <https://www.facebook.com/business/help/575610661605746> y
  <https://www.facebook.com/business/help/447934475640650>
- WhatsApp Business, leads en la UE: <https://whatsappbusiness.com/resources/resource-library/lead-generation-strategies-smb-whatsapp/>
- GHL y `ctwa_clid` (petición de usuarios, no documentación): <https://ideas.gohighlevel.com/ad-reporting-and-attribution/p/capturing-ctwa-clid-for-click-to-whatsapp-campaign-attribution>
- Make, funciones de hash: <https://help.make.com/text-and-binary-functions>
