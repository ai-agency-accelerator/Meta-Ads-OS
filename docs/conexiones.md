# Conexiones

Qué se conecta, para qué y cómo. Todo se hace en conversación con `/conectar`, que comprueba cada paso. Esta página
te explica qué está pasando y dónde mirar si algo falla.

| Conexión | Para qué | Cómo | ¿Obligatoria? |
|---|---|---|---|
| MCP oficial de Meta | Leer cuentas, crear en pausa campañas, conjuntos, anuncios y creatividades de imagen, cambios, audiencias y experimentos | `/conectar meta` (inicio de sesión con Meta, sin claves) | Sí, para trabajar con cuentas |
| Token avanzado de Meta | Subir vídeo e imagen, creatividades con las mejoras automáticas desactivadas, planes enteros, brief sin nadie delante y tope total diario | `/conectar meta --avanzado` → `META_TOKEN` en `.env` | No |
| GoHighLevel | Leer contactos con su atribución, oportunidades, citas, asistencia y pagos | `/conectar ghl` (MCP con OAuth) y, para lecturas desatendidas, `GHL_TOKEN` | Si usas GHL |
| Stripe | Leer pruebas, suscripciones, pagos y MRR (SaaS) | `/conectar stripe` (MCP) y, para lecturas desatendidas, `STRIPE_KEY` | Si cobras con Stripe |
| Conversions API | Mandar eventos de servidor (web y mensajería) y probarlos con `test_event_code` | `/implementar-capi` → `META_CAPI_TOKEN` (y, para mensajería, `META_CAPI_MENSAJERIA_TOKEN`) | Para construir la señal |
| Canal del brief | Recibir el brief diario | `/brief-diario programar` → claves de Telegram, Slack o email | No |
| Motor de vídeo con IA | Producir vídeo con IA | `/motor instalar` → `GEMINI_API_KEY` | No |

Después de cualquier conexión, `/doctor` te dice si todo está en orden.

## Meta: dos vías

**1. El MCP oficial** (`meta-ads`, `https://mcp.facebook.com/ads`). Viene configurado en `.mcp.json`. Al abrir el
proyecto, Claude Code te pide aprobarlo; después lo autenticas en `/mcp` → `meta-ads` → *Authenticate* con Facebook
Login for Business. Entra con la persona que tiene acceso a las cuentas publicitarias: en una agencia, el usuario de
la agencia que tiene el acceso de partner, no el del cliente.

Lo que el MCP **no** hace (comprobado el 2026-11-09): no sube vídeo ni imagen, solo crea creatividades de imagen única
y no crea portfolios ni cuentas. Para eso está la segunda vía o Ads Manager.

**2. `herramientas/meta_ads.py`** con un token de usuario del sistema de tu Business Portfolio (o del de tu agencia con
acceso de partner). Es opcional y se configura con `/conectar meta --avanzado` siguiendo la
[guía del token avanzado](guias/token-avanzado.md). Sin él, todo funciona con el MCP y los vídeos se suben en Ads
Manager.

Con el mismo token funcionan `reglas_meta.py` (reglas automáticas), `formularios_meta.py` (formularios instantáneos;
necesita `pages_manage_ads` y `leads_retrieval`, o un `META_TOKEN_PAGINA` aparte) y `audiencias_meta.py` (audiencias
de lista de clientes por etapa; `ads_management`).

Las dos vías las usa solo `operador-meta` y pasan por las mismas guardas: confirmación en cada escritura, tope por
cambio, regla de paciencia y change log.

**Reglas del lado de Meta.** En Business Settings → Integrations → Ads MCP server puedes bloquear acciones por cuenta y
activar «Budgets set above this amount → Blocked». `/conectar meta` y `/configurar-meta` te guían para dejar ese
límite igual que el tope por cambio de la ficha, y el límite de gasto de la cuenta puesto. Así hay un tope que no
depende de este ordenador. No está verificado si esa regla compara el presupuesto diario o el total de la campaña o
del conjunto: compruébalo en el texto de ayuda de la pantalla antes de elegir la cifra. Las escrituras vienen permitidas por defecto, así que este paso importa.

## GoHighLevel

- **MCP oficial de HighLevel** (`https://services.leadconnectorhq.com/mcp/anthropic/v2`), con OAuth por subcuenta.
  `/conectar ghl` lo añade solo en tu ordenador (`claude mcp add --scope local`), sin tocar `.mcp.json`, así que
  cada persona conecta lo suyo. Después hay que **reiniciar Claude Code** y autenticar en `/mcp` → `ghl`.
- **Varias subcuentas** (agencias): un servidor por cliente llamado `ghl-<slug>`, con `crm.servidor_mcp: ghl-<slug>`
  en su ficha. El nombre tiene que empezar por `ghl` para que la guarda `ghl_guard` lo vigile.
- **Lecturas sin nadie delante** (brief diario, registro creativo): `herramientas/ghl.py` con un token de integración
  privada **de solo lectura** en `.env` (`GHL_TOKEN_<SLUG>` y `GHL_LOCATION_<SLUG>`).
- Devolver las etapas de GHL a Meta (Meta aprende quién compra) es otro paso: `/implementar-capi <cliente> ghl` y la
  [guía GoHighLevel y Meta](guias/ghl-meta.md).

### UTMs con GoHighLevel: `utm_source=fb_ad`

Para unir cada contacto con su anuncio, los anuncios llevan una plantilla de UTMs con `ad_id={{ad.id}}`. Con GHL hay un
matiz en la fuente:

- **`utm_source=fb_ad` en lugar de `facebook`.** La documentación de HighLevel dice que clasifica como *Paid Social* el
  tráfico con `fb_ad` en `utm_source`. Es un artículo de 2022 que no hemos verificado con datos: compruébalo en tus
  primeros contactos. `herramientas/meta_ads.py` ya pone `fb_ad` cuando la ficha dice `crm.tipo: ghl`; si creas los
  anuncios por el MCP o en Ads Manager, copia la plantilla de la
  [guía](guias/ghl-meta.md#la-plantilla-de-utms).
- **Si además usas GA4**, su agrupación de canales por defecto no reconoce `fb_ad` como red social y ese tráfico cae en
  «Paid Other». Arréglalo con un grupo de canales personalizado: Administrar → Visualización de datos → Grupos de
  canales → nuevo grupo, con un canal «Paid Social» cuya regla sea *Fuente coincide exactamente con `fb_ad`* y *Medio
  coincide exactamente con `paid_social`*, colocado por encima de «Paid Other» (GA4 evalúa las reglas en orden).
  Después usa ese grupo en tus informes.
- Sin GHL, la plantilla general usa `utm_source=facebook`
  (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8).

Pase lo que pase, el sistema **nunca** manda mensajes, emails, SMS ni WhatsApp a tus contactos, ni borra nada en GHL:
`ghl_guard` lo bloquea.

## Stripe

- **MCP oficial** (`https://mcp.stripe.com`), añadido en local por `/conectar stripe`. Reinicia Claude Code y autentica
  con la cuenta correcta (cuidado con modo de prueba frente a modo real).
- **Lecturas sin nadie delante**: `herramientas/stripe_datos.py` con una clave **restringida de solo lectura**
  (`rk_...`), nunca la clave secreta completa.
- Para unir pagos con anuncios, el alta tiene que guardar `utm_*`, `ad_id`, `fbc` y `fbp` en los metadatos del cliente
  de Stripe: lo deja `/implementar-capi <cliente> stripe` ([guía de Stripe](guias/stripe.md)).

Stripe es de solo lectura en todo el sistema: `stripe_guard` bloquea cualquier creación, cambio, reembolso o
cancelación.

## Conversions API

`/implementar-capi` construye la señal de vuelta desde tu web, GoHighLevel, n8n, Make, Stripe o tu backend, y
`herramientas/capi.py` la prueba. Las pruebas van **siempre** con el `test_event_code` de Events Manager: un evento
real enviado «para probar» se queda en el dataset y Meta optimiza con él. Si alguna vez falta el código, `eventos_guard`
te para. Paso a paso: [guía de Conversions API](guias/capi.md).

**Mensajería.** Si tus anuncios abren una conversación (Click to WhatsApp, Messenger o Instagram Direct), la misma
CAPI devuelve a Meta qué conversaciones fueron lead, cualificado o venta (`LeadSubmitted`, `QualifiedLead`,
`Purchase`). La ficha necesita `meta.waba` (WhatsApp) y, si el dataset es otro, `meta.dataset_mensajeria`. Paso a
paso: [guía de mensajería](guias/mensajeria.md).

## El archivo `.env`

Todas las claves viven en `.env`, en la raíz del proyecto. Lo crea el instalador desde `plantillas/env.ejemplo`, con
permisos que solo te dejan leerlo a ti, y git no lo sube nunca.

**Cómo editarlo.** Ábrelo tú con tu editor (Claude no puede leerlo):

| Sistema | Orden |
|---|---|
| Mac | `open -e .env` |
| Windows (Git Bash) | `notepad .env` |
| Linux | `nano .env` |

Quita la `#` del principio de la variable que vas a usar y pon el valor justo después del `=`, sin comillas ni espacios.

**Por cliente.** Añade `_<SLUG>` al nombre, con el slug en mayúsculas y guiones bajos. Si existe, manda sobre la
global:

```
META_TOKEN_CLINICA_SONRISA=...
GHL_TOKEN_CLINICA_SONRISA=...
GHL_LOCATION_CLINICA_SONRISA=...
```

**Variables**

| Variable | Para qué |
|---|---|
| `META_TOKEN` · `META_APP_SECRET` | Token de usuario del sistema para `meta_ads.py`, `reglas_meta.py`, `formularios_meta.py` y `audiencias_meta.py` y, opcional, la clave secreta de su app |
| `META_TOKEN_PAGINA` | Opcional: token con la Página asignada para `formularios_meta.py`, si no usas `META_TOKEN` |
| `META_CAPI_TOKEN` · `META_CAPI_MENSAJERIA_TOKEN` | Token de la Conversions API del dataset, para `capi.py`. El segundo, opcional, es el de mensajería, con `whatsapp_business_manage_events`, `page_events` o `instagram_manage_events` según el canal; sin él, `capi.py` prueba con el primero |
| `META_API_VERSION` | Versión de la Graph API; déjala sin tocar salvo que una guía lo pida |
| `GHL_TOKEN` · `GHL_LOCATION` | Token de integración privada de solo lectura y su subcuenta, para `ghl.py` |
| `STRIPE_KEY` | Clave restringida de solo lectura, para `stripe_datos.py` |
| `GEMINI_API_KEY` · `MOTOR_PRESUPUESTO_USD` | Clave del motor de vídeo con IA y su tope de gasto (5 $ por defecto). El tope también se fija en `contexto/preferencias.md` (`motor.presupuesto_usd`); si están los dos, manda el de `.env` |
| `TELEGRAM_BOT_TOKEN` · `TELEGRAM_CHAT_ID` | Brief por Telegram |
| `SLACK_WEBHOOK_URL` | Brief por Slack |
| `SMTP_HOST` · `SMTP_PORT` · `SMTP_USUARIO` · `SMTP_CLAVE` · `EMAIL_DESTINO` | Brief por email (con contraseña de aplicación) |
| `META_ADLIBRARY_TOKEN` · `META_ACCESS_TOKEN` · `IG_USER_ID` · `IG_ACCESS_TOKEN` · `PAGESPEED_API_KEY` | Herramientas de investigación, opcionales |

**Reglas.** Nunca pegues una clave en el chat; si lo haces, revócala y crea otra. Cuando una versión nueva trae
variables nuevas, `/actualizar` te dice sus nombres y las añades tú.
