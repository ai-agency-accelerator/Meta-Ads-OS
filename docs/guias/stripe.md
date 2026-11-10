# Stripe para SaaS: leer los cobros y unirlos con los anuncios

Para quién: SaaS y negocios que cobran suscripciones o pagos con Stripe. Qué consigues: saber qué anuncio trae
registros, pruebas y clientes que pagan (y cuánto MRR), y devolver a Meta las conversiones que importan.

El sistema **nunca escribe en Stripe**: ni crea, ni cambia, ni reembolsa, ni cancela. Lee de dos formas:

- **El MCP de Stripe** (`/conectar stripe`, con OAuth) para trabajar contigo delante. `stripe_guard` bloquea cualquier
  escritura.
- **`herramientas/stripe_datos.py`** con una clave restringida de solo lectura, para leer sin nadie delante (brief
  diario, informes).

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09: compruébalo en
tu pantalla.

---

## 1. Clave restringida de solo lectura

1. Stripe → **Developers → API keys → Create restricted key** (crear clave restringida). Ponle de nombre
   «Meta Ads OS (lectura)».
2. Permisos: **Read** en
   - Customers (clientes),
   - Charges (cargos; puede aparecer como *Charges and Refunds*),
   - Subscriptions (suscripciones),
   - Prices y Products (precios y productos).

   Todo lo demás en **None**. Los nombres exactos de cada permiso pueden variar en el panel (no verificado el
   2026-11-09); la referencia oficial está en docs.stripe.com/keys/permissions-reference.
3. Prueba primero en **modo de prueba** (la clave empieza por `rk_test_`). Cuando funcione, crea la de modo real
   (`rk_live_`).
4. Pégala tú en `.env`, nunca en el chat:
   ```
   STRIPE_KEY_NIMBO=rk_live_...
   ```
5. Prueba con un agregado sin datos personales:
   ```
   python3 -I herramientas/stripe_datos.py suscripciones --cliente nimbo --json
   ```
   - Salida 2 con «401»: la clave está caducada o revocada.
   - Salida 2 con «403»: le falta un permiso de lectura. El mensaje dice cuál («customers», «charges»…).

`stripe_datos.py` **rechaza las claves secretas** (`sk_…`): una clave secreta puede mover dinero, y para leer no hace
falta. Solo hace GET. Fija la versión de la API (`2026-10-28.endive`, la vigente el 2026-11-09), así que un cambio de
versión en tu cuenta no le cambia los datos. Si alguna vez hace falta otra, se cambia con `STRIPE_API_VERSION`.

---

## 2. Qué mide cada orden

```
python3 -I herramientas/stripe_datos.py clientes      --cliente nimbo --desde 2026-11-02 --hasta 2026-11-08
python3 -I herramientas/stripe_datos.py suscripciones --cliente nimbo --desde 2026-11-02 --hasta 2026-11-08
python3 -I herramientas/stripe_datos.py pagos         --cliente nimbo --desde 2026-11-02 --hasta 2026-11-08
python3 -I herramientas/stripe_datos.py por-anuncio   --cliente nimbo --desde 2026-10-01 --hasta 2026-10-31
```

Sin fechas, cada orden coge los últimos 7 días completos (hasta ayer), en la zona horaria de la ficha.

| Orden | Qué te dice | Archivos |
|---|---|---|
| `clientes` | Altas del periodo, cuántas traen origen de Meta y en cuántas se identifica el anuncio | Detalle en `privado/` |
| `suscripciones` | Suscripciones nuevas por estado, pruebas iniciadas y convertidas, y el MRR de la cuenta hoy | Ninguno |
| `pagos` | Cobrado neto de reembolsos por moneda y clientes con cobro | Detalle en `privado/` |
| `por-anuncio` | Por anuncio: registros, pruebas, clientes de pago, cash, reembolsos y MRR | `datos/` y `privado/` |

Definiciones (las mismas en todo el sistema):

- **Cash** = cobrado (capturado) menos lo reembolsado, en la moneda de la ficha. Los cargos en otras monedas se cuentan
  aparte y se avisa.
- **MRR** = suscripciones activas o con el pago atrasado, con el precio por la cantidad, pasado a mes (un plan anual
  cuenta su doceava parte). No descuenta cupones ni impuestos. No incluye precios por uso ni por tramos.
- **Prueba** = suscripción con periodo de prueba. **Cliente de pago** = al menos un cargo cobrado con importe positivo.
- Monedas sin decimales (JPY, CLP…): Stripe da el importe en unidades, no en céntimos, y la herramienta lo tiene en
  cuenta.
- `por-anuncio` trabaja por **cohorte**: los clientes creados en el periodo y lo que pagaron hasta hoy. Las pruebas
  recientes aún no han tenido tiempo de convertir.

Salidas de `por-anuncio`:

- `clientes/<slug>/datos/stripe-por-anuncio_<desde>_<hasta>.csv`, con los agregados por anuncio. Lo lee
  `registro_creativo.py`.
- `clientes/<slug>/privado/clientes-stripe_<desde>_<hasta>.csv`, con una fila por cliente de Meta: IDs, fechas y sí/no,
  sin nombre ni email. Lo lee `embudo.py cohortes --modelo saas`.

Con `--json --sin-archivos` (lo que usa el brief diario) solo saca agregados por pantalla y no guarda nada.

---

## 3. Guardar el origen en el alta (lo hace tu producto)

Stripe no sabe de qué anuncio viene nadie. Para unirlo, **el código de registro de tu producto** guarda el origen en
los metadatos del cliente de Stripe cuando lo crea. El sistema no escribe en Stripe: esto es código tuyo (o de tu
equipo), y `/implementar-capi <cliente> stripe` te ayuda a escribirlo.

1. **En la landing**, lee de la URL `utm_source`, `utm_campaign`, `utm_content` y `ad_id`. Los pone la plantilla de
   UTMs de los anuncios (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8). Lee también las cookies `_fbc` y
   `_fbp` del píxel. Guárdalo todo en una cookie propia o en `localStorage` para que sobreviva hasta el registro.
2. **En el registro**, al crear el cliente de Stripe:
   ```js
   await stripe.customers.create({
     email,
     metadata: {
       ad_id: origen.ad_id || '',              // 1202… (solo dígitos)
       utm_source: origen.utm_source || '',
       utm_campaign: origen.utm_campaign || '',
       utm_content: origen.utm_content || '',  // nombre del anuncio
       fbc: origen.fbc || '',
       fbp: origen.fbp || ''
     }
   });
   ```
   Si el cliente lo crea un Checkout de Stripe, pasa lo mismo en `metadata` de la sesión o de la suscripción
   (`subscription_data.metadata`). `stripe_datos.py` busca primero en el cliente y, si no lo encuentra, en sus
   suscripciones.
3. **Límites de los metadatos** según Stripe: hasta 50 claves, nombres de hasta 40 caracteres y valores de hasta 500.
   `fbc` cabe de sobra.
4. **Nada de datos personales en los metadatos** más allá del email, que ya es del cliente: ni teléfono, ni respuestas
   de formularios.
5. **Comprueba la cobertura:**
   ```
   python3 -I herramientas/stripe_datos.py clientes --cliente nimbo
   ```
   Te dice cuántas altas traen metadatos de origen. Si ninguna los trae, el alta no los está guardando.

---

## 4. Devolver las conversiones a Meta (webhooks → Conversions API)

El patrón está en `meta-ads-kb/04-tracking-atribucion-medicion/07-custom-builds-api-directa.md` §3. Resumen:

| Momento en Stripe | Webhook | Evento a Meta | `event_id` (igual que el del píxel, si lo hay) |
|---|---|---|---|
| Empieza la prueba | `customer.subscription.created` con `trial_end` | `StartTrial` | `trial_<id de suscripción>` |
| Primer cobro de la suscripción | el primer `invoice.paid` de esa suscripción con `amount_paid` > 0 (con prueba, la factura de alta va a 0 y no cuenta) | `Subscribe` con `value` y `currency` | `sub_<id de suscripción>` |
| Pago único | `checkout.session.completed` o `payment_intent.succeeded` | `Purchase` con `value` y `currency` | `purchase_<id del pedido>` |

- Envía con `action_source=website` y los datos que guardaste en el alta: `fbc`, `fbp`, la IP y el user agent del
  registro, y `em` hasheado. Sin `event_source_url` ni `client_user_agent`, Meta rechaza los eventos de web.
- **Renovaciones**: no las mandes como `Purchase`, porque contaminan la optimización de adquisición. Si quieres
  medirlas, como evento personalizado (por ejemplo `SubscriptionRenewal`) `[STRONG INFERENCE]` (`07-…` §3).
- **Reembolsos**: Meta no tiene un mecanismo estándar para restar una conversión `[HYPOTHESIS]` (`07-…` §3). Se ven en
  la reconciliación (`meta-ads-kb/04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md`) y en el cash
  de `stripe_datos.py`.
- Respeta el consentimiento: si el usuario no aceptó el marketing, no envíes su evento
  (`04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`).
- Prueba siempre con código de prueba y con tu propia identidad, nunca con clientes reales: `docs/guias/capi.md`.

---

## 5. Avisos

- **Modo de prueba frente a modo real.** Con `rk_test_` la herramienta lo dice en cada salida por pantalla. Los datos
  de prueba no son tus clientes.
- **Varias monedas.** Cash y MRR van en la moneda de la ficha. Si cobras en varias, lo demás se cuenta aparte: no lo
  sumes a mano sin convertir.
- **El MCP de Stripe.** Stripe ha anunciado cambios en la autenticación de su servidor MCP (comprobado el 2026-11-09).
  Si `/conectar stripe` falla, mira docs.stripe.com/mcp antes de crear otra clave.
- **Si se filtra la clave** (chat, captura, repositorio): revócala en Developers → API keys y crea otra. Con una clave
  restringida de lectura nadie puede mover dinero, pero sí leer tus clientes.
