# Conversions API: mandar eventos desde n8n, Make o tu backend

Para quién: quien construye la señal de vuelta a Meta. Puede ser para su propio negocio o como servicio para sus
clientes: es justo lo que vende una agencia de automatización.
Qué consigues: eventos de servidor que Meta acepta, que se deduplican con el píxel y que casan con la persona (buena
calidad de coincidencia). Y probarlos sin ensuciar el dataset.

El paso a paso con el cliente lo lleva `/implementar-capi`. Esta guía es la referencia técnica. El porqué de cada regla
está en `meta-ads-kb/04-tracking-atribucion-medicion/`:
- `01-arquitectura-senales-pixel-capi-datasets.md`, arquitectura;
- `02-implementacion-pixel-capi-paso-a-paso.md`, el paso a paso;
- `03-emq-advanced-matching-pii-hashing.md`, normalización y hash;
- `07-custom-builds-api-directa.md`, backend y Stripe;
- `08-eventos-offline-y-crm.md`, eventos de CRM.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09.

---

## 1. Lo que necesitas

- **El dataset** (el antiguo píxel) del cliente: Events Manager → Orígenes de datos. Su ID va en la ficha, en
  `meta.dataset`.
- **Un token de Conversions API** del dataset: Events Manager → el dataset → Configuración → Conversions API → Generar
  token de acceso. Pégalo tú en `.env` como `META_CAPI_TOKEN_<SLUG>`, o en el almacén de credenciales de n8n o Make.
  Nunca en el chat ni en código que se comparta.
- **El endpoint:** `POST https://graph.facebook.com/v27.0/<DATASET>/events`. La v27.0 (salió el 2026-11-04) es la
  versión que usa el sistema desde el 2026-11-10; para los eventos no cambia nada respecto a la v26.0. Las herramientas
  la leen de `META_API_VERSION` si la defines.

---

## 2. El evento, campo a campo

```json
{
  "data": [{
    "event_name": "Lead",
    "event_time": 1762851600,
    "action_source": "website",
    "event_source_url": "https://acme-automations.example/gracias",
    "event_id": "lead_8f3a2c",
    "user_data": {
      "em": ["<sha256 del email normalizado>"],
      "ph": ["<sha256 del teléfono normalizado>"],
      "external_id": ["<sha256 de tu ID de cliente>"],
      "client_ip_address": "203.0.113.7",
      "client_user_agent": "Mozilla/5.0 ...",
      "fbc": "fb.1.1762851500000.IwAR...",
      "fbp": "fb.1.1762851400000.1234567890"
    },
    "custom_data": {"value": 0, "currency": "EUR"}
  }],
  "test_event_code": "TEST12345"
}
```

| Campo | Regla |
|---|---|
| `event_name` | Estándar (`Lead`, `CompleteRegistration`, `Schedule`, `StartTrial`, `Subscribe`, `Purchase`…) o, para una etapa del CRM, el nombre exacto de la tabla del contrato §16 (`LeadCualificado`, `LlamadaAsistida`…) |
| `event_time` | **Segundos** Unix (no milisegundos), el momento real del evento, como mucho 7 días atrás |
| `action_source` | `website` para lo que pasa en la web; `system_generated` para etapas del CRM; `chat`, `phone_call`, `email`… |
| `event_source_url` y `client_user_agent` | **Obligatorios con `website`**: sin ellos Meta rechaza el evento |
| `event_id` | El mismo que el `eventID` del píxel para ese evento: así Meta deduplica navegador y servidor |
| `user_data` hasheado | `em`, `ph`, `fn`, `ln`, `ct`, `st`, `zp`, `country`, `db`, `ge` (y `external_id`, recomendado): normalizados y SHA-256 |
| `user_data` sin hashear | `client_ip_address`, `client_user_agent`, `fbc`, `fbp`, `lead_id`: tal cual. Si los hasheas, ya no casan |
| `custom_data` | `value` (número) y `currency` (3 letras) en `Purchase`; nada de datos personales aquí |
| Lote | Hasta 1.000 eventos por petición. **Un evento inválido descarta el lote entero**: valida antes |

**Normalización antes del hash** (`03-…` §2): email recortado y en minúsculas. Teléfono solo con dígitos y **con
prefijo de país**, sin `+` ni `00` (`+34 612 34 56 78` → `34612345678`). Nombre y apellido en minúsculas y sin
puntuación. Fecha de nacimiento como `AAAAMMDD`. País en ISO de 2 letras y en minúsculas, y mándalo siempre. Si un
valor ya viene hasheado (64 caracteres hexadecimales), no lo vuelvas a hashear.

**Comprueba que tu normalización da el mismo hash que la del sistema:**

```
python3 -I herramientas/capi.py hashear "John_Smith@Gmail.com " --tipo em
python3 -I herramientas/capi.py hashear "612 34 56 78" --tipo ph --prefijo 34
```

El primero tiene que dar `62a14e44f765419d10fea99367361a727c12365e2520f32218d505ed9aa0f62f`, el vector oficial de
Meta (`03-…` §2).

### Eventos de CRM (Conversion Leads)

Las etapas del pipeline van a un dataset de CRM con esta forma (`meta-ads-kb/05-leadgen-high-ticket-crm/04-integraciones-crm.md` §1 y §3.3):

```json
{
  "event_name": "LeadCualificado",
  "event_time": 1762938000,
  "action_source": "system_generated",
  "user_data": {"lead_id": 1234567890123456, "em": ["<sha256>"], "ph": ["<sha256>"]},
  "custom_data": {"event_source": "crm", "lead_event_source": "GHL"}
}
```

- `lead_id` es el ID del lead del formulario instantáneo (15–17 dígitos). En leads de la web, `fbc` más `em`/`ph`.
- **El `event_name` es el de la tabla canónica del contrato §16, tal cual:**

  | Etapa | `event_name` |
  |---|---|
  | lead | `Lead` |
  | diagnóstico | `DiagnosticoCompletado` |
  | cualificado | `LeadCualificado` |
  | llamada agendada | `Schedule` |
  | asistió a la llamada | `LlamadaAsistida` |
  | propuesta enviada | `PropuestaEnviada` |
  | ganado | `Purchase` (con `value` y `currency`) |
  | perdido (opcional, no se optimiza) | `LeadPerdido` |
  | taller: registro, asistencia, hasta la oferta | `CompleteRegistration`, `WebinarAsistido`, `WebinarHastaOferta` |

  - Nunca el nombre visible de la etapa en GHL («Cualificado», «Cita agendada»), ni en minúscula, ni los ejemplos
    de la KB (`raw_lead`, `qualified`, `booked_call`…). Meta deja el nombre libre, pero con dos nombres para el mismo
    hito se reparte la señal y el embudo del dataset no coincide con lo que llega.
  - `capi.py construir --etapa cualificado --crm GHL` pone el nombre exacto, y `validar` avisa si no lo es.
- **Todas las etapas, a medida que ocurren**, con nombres estables. Con formulario instantáneo, la primera es `Lead`
  (con `lead_id`). Con formulario web, `Lead` ya lo mandan el píxel y la CAPI web con el mismo `event_id`, así que el
  CRM empieza en la siguiente (la acción de CAPI de GHL no lleva `event_id` y contaría el lead dos veces).
- `event_time`, siempre posterior a la creación del lead.
- La etapa ganada lleva `value` y `currency` (la moneda de la ficha).
- **Optimizar a leads de calidad** (*Conversion Leads*, `optimizar: "QUALITY_LEAD"` en un conjunto de formulario de
  `meta_ads.py crear`) necesita este dataset de CRM recibiendo etapas y volumen. El mínimo es `[CONTESTED]`: la
  documentación de desarrolladores (2026-10-27) pide 200 leads al mes y otra página oficial (2025-10-30) no pone mínimo;
  el Help Center dice que vale con formularios web y la de desarrolladores, que solo con formularios instantáneos.
  Planifica con ≥200 leads al mes y no lo prometas con formularios web hasta verlo en la cuenta.

**Eventos de conversaciones que empiezan en un anuncio de mensajes:** `action_source=business_messaging` →
`docs/guias/mensajeria.md`. Ahí está también lo que cuesta atender por WhatsApp: la ventana gratuita (FEP) de un
anuncio de Click to WhatsApp dura hasta 7 días, cada número tiene 1.000 mensajes de servicio gratis al mes y el
agente de IA de Meta (Business Agent) se cobra aparte también dentro de la FEP `[OFFICIAL META]` (la fecha de entrada,
el 2026-09-28 según los BSP, es `[EMPIRICAL]`).

---

## 3. Desde n8n

1. **Disparador:** el webhook de tu formulario, CRM o pasarela de pago.
2. **Normalizar:** un nodo *Code* que recorte y pase a minúsculas el email y deje el teléfono solo con dígitos y con
   prefijo.
3. **Hashear:** el nodo *Crypto* (acción *Hash*, tipo SHA256, salida en hexadecimal) para cada dato de `user_data` que
   lo necesite.
4. **Enviar:** un nodo *HTTP Request*:
   - `POST https://graph.facebook.com/v27.0/<DATASET>/events`;
   - cuerpo JSON con `data` (la lista de eventos) y, mientras pruebas, `test_event_code`;
   - el token como credencial de n8n, en el parámetro `access_token`. Nunca escrito en el flujo exportado.
5. **Errores:** activa *Retry on fail* y una rama de error que te avise. Meta responde `events_received` si todo fue
   bien, o un error con el motivo.
6. **El `event_id`:** genéralo una vez (en la web, junto al píxel) y pásalo por el flujo. No lo inventes en n8n si el
   navegador ya mandó el evento, o no se deduplicará.

`ingeniero-capi` entrega el flujo listo para importar en `clientes/<slug>/planes/capi/`. Los nombres de los nodos
pueden cambiar entre versiones de n8n (no verificado en la última).

## 4. Desde Make

- **Etapas de CRM:** el módulo **«Create a Lead Event»** de la app de Conversions API de Meta. Make lo da gratis del
  27-02-2026 a febrero de 2028. Desde octubre de 2025 el Lead ID no es obligatorio si mandas el email `[OFFICIAL META]`
  + `[EMPIRICAL]` (`05-…/04-…`, TL;DR y §2).
- **Eventos de web** (o cualquier otro): el módulo HTTP *Make a request* con el mismo cuerpo que en n8n. Para hashear
  en el propio mapeo, la función `sha256()` de Make, aplicada al valor ya normalizado (`lower(trim(email))`).
- El token, en una conexión o en una variable de Make, nunca en el texto del escenario.

## 5. Desde tu backend

El patrón completo es el worker de `07-custom-builds-api-directa.md` §2:

- una cola con reintentos y espera creciente;
- lotes de hasta 1.000 eventos;
- `event_time` real;
- validar antes de enviar;
- registrar los errores sin datos personales en claro.

Para Stripe, `07-…` §3 y `docs/guias/stripe.md` §4.

Reglas que más se rompen:
- **IP y user agent del usuario**, no los de tu servidor. Detrás de un proxy, sácalos de `X-Forwarded-For` o
  `CF-Connecting-IP`.
- **`fbc`**: la cookie `_fbc`. Si no existe pero tienes el `fbclid` de la URL, constrúyelo como
  `fb.1.<milisegundos del clic>.<fbclid>`, sin cambiar las mayúsculas del `fbclid`.
- **Consentimiento** (UE): si el usuario no aceptó la medición, no mandes su evento
  (`09-privacidad-att-gdpr-consentimiento-aem.md`). Con las páginas de `paginas.py`, el envío ya trae la decisión:
  manda a la CAPI solo los que llegan con `enviar_a_meta: true` (plantilla `plantillas/integraciones/paginas/`).
- **Nunca datos sensibles** de salud o finanzas en `custom_data` ni en la URL.

---

## 6. Probar sin ensuciar el dataset

1. Copia el código de **Probar eventos** (*Test Events*) de Events Manager.
2. Construye y valida un evento con **tus propios datos** (tu email, tu teléfono), nunca con los de un lead real:
   ```
   python3 -I herramientas/capi.py construir --evento Lead --origen website \
       --url https://acme-automations.example/gracias --email tu@email.example --ip 203.0.113.7 \
       --ua "Mozilla/5.0 ..." --event-id lead_prueba_1 --salida clientes/acme/privado/evento-prueba.json
   python3 -I herramientas/capi.py validar clientes/acme/privado/evento-prueba.json
   python3 -I herramientas/capi.py enviar clientes/acme/privado/evento-prueba.json --cliente acme --test-code TEST12345
   ```
   Para un evento de CRM: `construir --etapa cualificado --crm GHL --lead-id <id> --email …` (sale
   `LeadCualificado`, el nombre del contrato §16).
3. En *Probar eventos*, mira que llega, con qué parámetros y si se deduplica con el del navegador.

Ojo: **Meta no descarta los eventos con `test_event_code`.** No cuentan en tus informes, pero según Meta se usan para
segmentación y medición. Por eso se prueba con tu identidad. Sin código de prueba, `capi.py` exige `--real --confirmo`,
y el hook `eventos_guard` pide confirmación. No lo uses salvo que el cliente lo pida para ese envío concreto: un
evento real de prueba ensucia su optimización.

En GHL, n8n o Make, el código de prueba va en el campo `test_event_code` de la acción mientras pruebas, y se quita
después.

---

## 7. Verificar en producción (48–72 horas)

Con `meta-ads-kb/04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md` §1.2:

- **Deduplicación.** El mismo evento llega por navegador y por servidor y Meta lo cuenta una vez. Los eventos por día,
  separados por origen:
  ```
  python3 -I herramientas/meta_ads.py eventos --cliente acme
  ```
  Si servidor + navegador ≈ el doble de lo real, falta el `event_id` común.
- **Calidad de coincidencia** «Buena» o mejor en el evento principal (Events Manager → el evento → calidad). Si es
  baja: falta `em`/`ph`, `fbc`, IP o user agent (`03-…` §4).
- **Cobertura del CRM:** al menos el 60 % de los leads de Meta con eventos de etapa.
- **Reconciliación:** tres conversiones de prueba casadas con el backend.
- **Medición en el dispositivo** (*Mide las conversiones en los dispositivos de los clientes*, en la configuración del
  dataset). Desde el 2026-11-12 viene activada por defecto en los píxeles con compras, pero no se aplica a personas
  de la UE ni del Reino Unido `[OFFICIAL META]`; la fecha es `[EMPIRICAL]`. Comprueba si está activada y si el cliente
  la quiere. Si vende fuera de la UE y el Reino Unido, anota la fecha en el change log y **vuelve a fijar la línea
  base**: no compares compras de antes y de después como si fueran lo mismo. A los leads no les afecta (Meta solo
  describe la compra). Cómo se deduplica con el píxel y la CAPI, y si entra en la optimización o solo en los
  informes, no está verificado el 2026-11-10.

## 8. Listas de clientes para públicos

Para excluir clientes o usarlos de semilla, la lista se hashea en tu ordenador. No sale ningún dato en claro:

```
python3 -I herramientas/capi.py hashear --archivo clientes/acme/privado/clientes.csv \
    --columnas email,telefono --prefijo 34
```

- Escribe `clientes/acme/privado/clientes-hash.csv` con las columnas de la plantilla de listas de clientes de Meta
  (`email`, `phone`, `fn`, `ln`, `ct`, `st`, `zip`, `country`, `gen`, `doby`/`dobm`/`dobd`, `extern_id`), solo con
  hashes.
- Normaliza según Meta: sin tildes en nombre, apellido, ciudad y provincia; la fecha de nacimiento en año, mes y día.
- Entrada y salida van en `privado/`: los hashes siguen siendo datos personales. La herramienta no escribe fuera de
  ahí, y avisa si la entrada está fuera.
- Por pantalla solo salen recuentos: válidos, vacíos y no válidos por columna.
- `--conservar valor` copia una columna sin datos personales, por ejemplo el valor del cliente para un público
  similar por valor.
- Sin `--columnas`, coge las que reconoce por el nombre (correo, móvil, nombre…). «Estado» no la coge, porque suele ser
  el estado del lead. Para otra columna, `--columnas dni=external_id`.

Las cabeceras salen de la guía de formato de listas de clientes. Que Ads Manager acepte la lista ya hasheada con esas
cabeceras no está verificado en la ayuda oficial el 2026-11-09: pruébalo con una lista pequeña. Después,
`/audiencias`.

---

## Interfaz de `capi.py`

`python3 -I herramientas/capi.py --help` (y `<orden> --help`) es la referencia de cada opción. La interfaz es estable:
la usan `/implementar-capi`, `/audiencias`, `/construir-landing`, `/webinar`, las plantillas de
`plantillas/integraciones/` y `audiencias_meta.py`, así que una opción o una salida solo cambia con nota en
`CHANGELOG.md`. En resumen:

| Orden | Para qué |
|---|---|
| `construir` | Un evento: `--evento` o `--etapa` (el nombre exacto del §16 del contrato), `--origen`, datos de la persona (`--email`, `--telefono`… en claro: se hashean al construir), `--event-id` (el del píxel; sin él no se inventa ninguno), `--valor`/`--moneda`, `--crm`/`--lead-id` para etapas del CRM, o `--entrada` con eventos ya montados. Escribe `{"data": [eventos]}` (en `--salida`, mejor dentro de `privado/`). En mensajería, `--canal` y `--etapa` |
| `hashear` | Un valor (`--tipo em\|ph\|fn…`, `--prefijo`) o una lista entera con `--archivo` (§8) |
| `validar` | Revisa un payload sin red: lo que Meta rechazaría |
| `origen` | Lee un webhook de WhatsApp, Messenger o Instagram (solo local) y dice si trae el anuncio y el clic |
| `enviar` | Lo manda: con `--test-code` (prueba) o con `--real --confirmo` (y el hook pregunta) |

El código de prueba no va en `construir`: va en `enviar --test-code`. Los códigos de salida son los del contrato §9
(0 bien, 1 error del usuario, como un evento inválido o falta de confirmación, y 2 configuración: ficha o token).

---

## Errores frecuentes

| Síntoma | Causa |
|---|---|
| «Invalid parameter» en todo el lote | Un solo evento mal (por ejemplo, `event_time` en milisegundos): valida con `capi.py validar` |
| Eventos de web rechazados | Falta `event_source_url` o `client_user_agent` |
| Calidad de coincidencia baja | Teléfono sin prefijo, `fbc`/`fbp` hasheados por error, IP de tu servidor |
| Compras duplicadas | Píxel y servidor sin el mismo `event_id` |
| Etapas de CRM que no sirven para optimizar | Sin `action_source=system_generated` o sin `lead_event_source` |
| `event_time` antiguo rechazado | Más de 7 días: envía en tiempo real o al menos a diario |
