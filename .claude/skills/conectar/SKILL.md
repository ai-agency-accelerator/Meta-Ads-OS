---
name: conectar
description: "Conecta y verifica tus integraciones en conversación contigo: el MCP oficial de Meta (OAuth, cuentas, mapa a clientes y reglas del Ads MCP server), GoHighLevel y Stripe como MCP local de solo lectura y, con --avanzado, el token de usuario del sistema para meta_ads.py. Úsala la primera vez, al sumar un cliente o si una conexión falla."
argument-hint: "[meta|ghl|stripe] [--avanzado] [cliente]"
---

# /conectar

Entrada: `$ARGUMENTS`. Sin argumentos: enseña en una tabla el estado de las tres conexiones (Meta, GHL, Stripe) y
pregunta cuál toca.

**Se ejecuta en el hilo principal**: es una conversación con pasos que hace el usuario en su navegador. No la
delegues en un subagente.

Reglas comunes:
- **Ninguna clave ni token en el chat.** Las claves van en `.env` (creado desde `plantillas/env.ejemplo`) y las pega
  el usuario con su editor. Tú nunca lees, imprimes ni copias `.env`. Si pega una clave en el chat: que la revoque y
  la regenere; no la repitas ni la guardes.
- Solo se verifica con **lecturas**. Esta skill no escribe en Meta, GHL ni Stripe.
- Al terminar, si existe `contexto/instalacion.json`, actualiza la fase correspondiente (`meta`, `integraciones` o
  `avanzado`) con fecha y detalle.
- Referencias: `meta-ads-kb/10-cambios-2025-2026-api-ia-automatizacion/11-mcp-meta-inventario-y-conexion.md`,
  `meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` §2 y §4,
  `meta-ads-kb/05-leadgen-high-ticket-crm/04-integraciones-crm.md` y las guías `docs/guias/ghl-meta.md`,
  `docs/guias/stripe.md` y `docs/guias/token-avanzado.md`.

## meta

1. **Configuración.** `.mcp.json` ya trae el servidor `meta-ads` (`https://mcp.facebook.com/ads`). Si al abrir el
   proyecto Claude Code pidió aprobar sus servidores MCP, hay que aprobar `meta-ads`.
2. **Autenticación** (la hace el usuario): `/mcp` → `meta-ads` → *Authenticate* → Facebook Login for Business con la
   persona que tiene acceso a las cuentas publicitarias. En una agencia, el usuario de la agencia que recibe el acceso
   de partner, no el del cliente. Acepta los permisos que pide (`ads_management`, `ads_read`, `business_management`,
   Páginas, Instagram, catálogo y `ads_mcp_management`). No hace falta app de desarrollador: el servidor usa registro
   dinámico de cliente `[OFFICIAL META]`.
   - Si Meta exige una app propia: crear una app en developers.facebook.com con el caso de uso de anuncios con el Ads
     MCP server y añadir el servidor en local con su ID:
     `claude mcp add --transport http --client-id <ID_DE_APP> --scope local meta-ads https://mcp.facebook.com/ads`
     (si la app exige una URI de redirección fija, añade `--callback-port <puerto>`). El de ámbito local tiene
     prioridad sobre el de `.mcp.json`. Reiniciar Claude Code y autenticar de nuevo.
3. **Prueba de lectura.** `ads_get_ad_accounts` → tabla con nombre, ID, moneda, zona horaria y estado. Después,
   `ads_get_ad_entities` de una cuenta (últimos 7 días, nivel campaña) para confirmar que llegan datos.
   - Lista vacía → esa persona no tiene acceso a cuentas. Agencia → falta el acceso de partner:
     `/configurar-meta <cliente> agencia`.
4. **Mapa de cuentas a clientes.** Por cada cliente de `clientes/`, pregunta qué cuenta es la suya y escribe
   `meta.cuenta` en la cabecera de su ficha. Después `ads_get_ad_account_pages`, `ads_get_ig_accounts` y
   `ads_get_datasets` para `meta.pagina`, `meta.instagram` y `meta.dataset`; confirma con el usuario cuál es cuál, no
   lo adivines. Cuenta sin cliente → `/cliente-nuevo`.
5. **Inventario de herramientas.** Compara las herramientas que muestra `/mcp` con los permisos de
   `.claude/settings.json` (lectura permitida, escritura con confirmación, borrados bloqueados). Si Meta ha añadido o
   renombrado herramientas, avisa y propón anotarlo en `aprendizajes/`; no edites `settings.json`.
6. **Reglas del lado de Meta** (las pone quien tiene control total del portfolio): Business Settings → Integrations →
   **Ads MCP server** → por cuenta: bloquear las acciones que no vaya a usar y activar «Budgets set above this amount →
   Blocked» con el `topes.cambio_dia` de la ficha. No está verificado si la regla compara el presupuesto diario o el
   total (de por vida) de la campaña o del conjunto: dile que lo mire en el texto de ayuda de la pantalla y, si es el
   total, que ponga una cifra acorde. Se ha observado que las escrituras vienen permitidas por defecto `[EMPIRICAL]`. Si los topes están a 0, primero se fijan (`/configurar-meta`). Apunta las reglas en la sección
   «Reglas del Ads MCP server» de la ficha y marca `F1.reglas-mcp` en `estado.md` solo cuando el usuario confirme que
   están puestas.

## ghl

1. **Requisito.** Una sub-cuenta (location) de GoHighLevel del cliente y alguien que pueda autorizarla. La conexión es
   por sub-cuenta (OAuth).
2. **Añadir el servidor** (con su OK; queda solo en su ordenador y no toca `.mcp.json`):
   `claude mcp add --transport http --scope local ghl https://services.leadconnectorhq.com/mcp/anthropic/v2`.
3. **Reiniciar y autenticar.** Cierra y vuelve a abrir Claude Code en esta carpeta; `/mcp` → `ghl` → *Authenticate* →
   elige la sub-cuenta. Si venías de `/empezar`, al volver escribe `/empezar`.
4. **Prueba de lectura.** Enumera las herramientas `mcp__ghl__*` y haz una lectura que no devuelva datos personales
   (describir una operación o listar pipelines). `ghl_guard` deja pasar las lecturas, pide confirmación en las
   escrituras y **bloquea** mensajes a contactos, borrados y facturas.
5. **Ficha.** `crm.tipo: ghl` y `crm.servidor_mcp: ghl`.
6. **Varias sub-cuentas** (agencias). Un servidor por sub-cuenta, con nombre `ghl-<slug>`:
   `claude mcp add --transport http --scope local ghl-<slug> https://services.leadconnectorhq.com/mcp/anthropic/v2`,
   autenticado con la sub-cuenta de ese cliente, y en su ficha `crm.servidor_mcp: ghl-<slug>`. Así `ghl_guard` sabe
   de qué cliente es cada llamada. El nombre **tiene que empezar por `ghl`**: con otro nombre las llamadas quedarían
   fuera de las guardas. Para leer sin nadie delante (brief diario, registro creativo), `herramientas/ghl.py` con un
   token por cliente (paso 7).
   - **Permisos del servidor nuevo.** Los de `.claude/settings.json` solo nombran `ghl` (en `allow` el nombre del
     servidor no admite comodines). Con su OK, añade a `permissions.allow` de `.claude/settings.local.json` (créalo si
     no existe; suma a lo que haya, no quites nada; la escritura pide confirmación) las lecturas de ese servidor:
     `mcp__ghl-<slug>__search_operations`, `mcp__ghl-<slug>__describe_operation`, `mcp__ghl-<slug>__list_locations`,
     `mcp__ghl-<slug>__search` y `mcp__ghl-<slug>__fetch`. Y en `permissions.ask`,
     `mcp__ghl-<slug>__execute_operation`: cada operación pregunta (también las lecturas), y además `ghl_guard` bloquea
     mensajes a contactos, borrados y pagos, y en subagentes todo lo que no sea una lectura reconocida.
7. **Lectura desatendida (opcional).** En la sub-cuenta, crea una *Private Integration* con permisos **solo de
   lectura** (contactos, oportunidades, calendarios y pagos; detalle en `docs/guias/ghl-meta.md`). El usuario añade a
   `.env` `GHL_TOKEN_<SLUG>` y `GHL_LOCATION_<SLUG>` (slug en mayúsculas con guion bajo). Prueba con un agregado sin
   datos personales: `python3 -I herramientas/ghl.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`.
8. La dirección GHL → Meta (devolver etapas por CAPI) no es esta skill: `/implementar-capi <cliente> ghl`.

## stripe

1. Solo para SaaS o negocios que cobran con Stripe. Es **solo lectura**: `stripe_guard` bloquea cualquier creación,
   cambio, reembolso o cancelación.
2. **Añadir el servidor** (con su OK): `claude mcp add --transport http --scope local stripe https://mcp.stripe.com`.
3. **Reiniciar y autenticar.** Reabre Claude Code; `/mcp` → `stripe` → *Authenticate* con la cuenta de Stripe
   correcta (ojo con modo de prueba frente a modo real).
4. **Prueba de lectura** sin datos personales: la cuenta o el saldo.
5. **Ficha.** `stripe: true`.
6. **Lectura desatendida (opcional).** Clave **restringida** con permiso de solo lectura en clientes, suscripciones,
   pagos y facturas (detalle en `docs/guias/stripe.md`). El usuario la añade a `.env` como `STRIPE_KEY_<SLUG>`. Prueba:
   `python3 -I herramientas/stripe_datos.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`.
7. Para unir pagos con anuncios hace falta que el alta guarde `utm_*`, `ad_id`, `fbc` y `fbp` en los metadatos del
   cliente de Stripe: eso lo deja `/implementar-capi <cliente> stripe`.
8. **Varias cuentas de Stripe** (agencias): un servidor por cliente, con nombre `stripe-<slug>` (tiene que empezar por
   `stripe` para que `stripe_guard` lo cubra):
   `claude mcp add --transport http --scope local stripe-<slug> https://mcp.stripe.com`. Con su OK, añade a
   `.claude/settings.local.json` (suma a lo que haya; la escritura pide confirmación), con el servidor escrito entero
   porque el nombre no admite comodines:
   - `permissions.deny`: `mcp__stripe-<slug>__stripe_api_write`, `__send_money`, `__transfer_money`,
     `__convert_currency`, `__setup_recipient`, `__atlas_company_formation`, `__send_stripe_feedback`, `__create_*`,
     `__update_*`, `__cancel_*`, `__finalize_*` y `__delete_*` (cada una con el prefijo `mcp__stripe-<slug>`);
   - `permissions.allow`: las mismas lecturas que tiene `stripe` en `.claude/settings.json` (`stripe_api_read`,
     `stripe_api_search`, `stripe_api_details`, `get_stripe_account_info`, `get_balance_summary`,
     `search_stripe_documentation`, `stripe_analytics`, `search_stripe_resources`, `fetch_stripe_resources`,
     `retrieve_balance` y `list_*`), con el prefijo `mcp__stripe-<slug>__`.

   `stripe_guard` sigue bloqueando todo lo que no sea lectura aunque falte una regla; estas reglas son la segunda capa.

## meta --avanzado

Para `herramientas/meta_ads.py`: subir vídeo e imagen, crear creatividades con todas las mejoras automáticas
desactivadas, planes idempotentes, el brief sin nadie delante y el tope diario total del hook `meta_guard`. No forma
parte de los 30 minutos de `/empezar`; sin él se trabaja con el MCP y los vídeos se suben en Ads Manager.

1. **Usuario del sistema** en el portfolio dueño del negocio o, en una agencia, en el portfolio de la agencia con
   acceso de partner a la cuenta del cliente (`08-cuenta-politicas-seguridad/03-…` §2).
2. Asígnale solo los activos que necesita (cuenta publicitaria para gestionar campañas, Página, dataset) y genera su
   token con los permisos que indica `docs/guias/token-avanzado.md`.
3. El usuario lo añade a `.env`: `META_TOKEN_<SLUG>` por cliente o `META_TOKEN` global; `META_APP_SECRET` es opcional.
4. Verifica: `python3 -I herramientas/meta_ads.py cuentas --cliente <slug>` y
   `python3 -I herramientas/meta_ads.py activos --cliente <slug>`.
5. Seguridad: los tokens de usuario del sistema no caducan cuando sale una persona del equipo. Cuando termines con un
   cliente, revócalo en Business Settings.
6. Marca `avanzado` → `hecho` en `contexto/instalacion.json`.
