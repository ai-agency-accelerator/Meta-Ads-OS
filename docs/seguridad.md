# Seguridad y permisos

Meta Ads OS trabaja con dinero real (tu inversión y la de tus clientes), con personas reales (los contactos de tu CRM)
y con claves que dan acceso a todo eso. Por eso la seguridad no depende de que Claude «se porte bien»: está en varias
capas que se vigilan entre sí.

## La regla

| Acción | Qué pasa |
|---|---|
| **Leer** (métricas, configuración, CRM, Stripe) | Libre, sin preguntar |
| **Escribir** (crear, cambiar presupuestos, pujas, audiencias) | Te pide confirmación en ese momento, con el motivo |
| **Activar** una campaña, conjunto o anuncio | Confirmación específica, aparte del resto |
| **Borrar** en Meta (también poniendo el estado `DELETED`) | Bloqueado: si de verdad quieres borrar algo, lo haces tú en Ads Manager |
| **Archivar** en Meta (estado `ARCHIVED`) | Pregunta aparte: no se puede deshacer desde aquí |
| **Promocionar** una publicación (`ads_boost_ig_post`) | Bloqueado: no nace en pausa ni pasa por los topes; se hace en Ads Manager |
| Cambiar los **topes de gasto** de una ficha | Te pide confirmación con el antes y el después |
| Mandar mensajes a contactos, tocar pagos, leer secretos | Bloqueado siempre |

Además, **todo lo nuevo se crea en pausa**, y cada cambio queda anotado en el change log del cliente con lo que había
antes, lo que hay ahora, el motivo, la métrica de éxito y la fecha en que se evaluará.

## Las capas

### 1. Permisos de Claude Code (`.claude/settings.json`)

La red de seguridad de todo lo demás:

- **allow**: lecturas del MCP de Meta, de GoHighLevel y de Stripe; las herramientas de `herramientas/`; las órdenes
  gratuitas del motor de vídeo.
- **ask**: cualquier escritura en Meta (`ads_create_*`, `ads_update_*`, activar, eventos del píxel, experimentos,
  catálogos), `meta_ads.py crear|activar|presupuesto|pausar`, `reglas_meta.py crear|pausar|reactivar`,
  `formularios_meta.py crear|leads`, `audiencias_meta.py crear|sincronizar`, `capi.py enviar`,
  `execute_operation` de GoHighLevel (lee, escribe, manda mensajes y borra con la misma herramienta, así que siempre
  pregunta), `ffmpeg` cuando sobrescribe (`-y`) o lee de la red, cualquier borrado de archivos y cualquier cambio en
  los permisos o en los hooks. (Las opciones de pago de cutkit las frena el hook `motor_guard`.)
- **deny**: borrados en Meta, promocionar publicaciones (`ads_boost_ig_post`), escrituras y movimientos de dinero en
  Stripe, leer `.env` y otros secretos, volcar el entorno, `rm -rf`.

Las reglas de `settings.json` comparan texto: `Bash(python3 -I herramientas/*)` es un prefijo, y una orden con
comodines (`meta_ad?.py`), variables (`$S.py`), `-c`, `-m`, `runpy` o `..` no casa con las reglas `ask`, que son
literales. Eso lo cubren los hooks (capa 2).

Lo que no está en ninguna lista también te lo pregunta Claude Code. **No aflojes estas reglas** en
`.claude/settings.local.json` para ahorrarte confirmaciones: cada confirmación es un punto donde puedes parar un error.

### 2. Guardas automáticas (hooks)

Diez scripts que Claude Code ejecuta antes o después de cada acción relevante. Ven lo que los permisos no pueden ver:
el presupuesto que va dentro de una llamada, si la entidad se cambió hace menos de 7 días, si un envío a la
Conversions API lleva código de prueba, si un archivo lleva emails. Detalle en el [catálogo de hooks](catalogo/hooks.md).

Tres reglas que valen para todos:

- **Si un hook no puede leer la orden, pregunta o bloquea.** Python sobre `herramientas/`, `modulos/` o
  `.claude/hooks/` con comodines que no dan un único script, variables en la ruta, `-c`, `-m`, `runpy`, `exec` o `..`
  → pregunta en la sesión principal y se bloquea en los subagentes. Un comodín que da un único script se trata como
  ese script, y lo que va detrás de `--` nunca cuenta como opción (`-- --simular` no simula).
- **Si un hook falla, falla cerrado** en lo que toca dinero: una escritura en Meta que `meta_guard` no ha podido
  comprobar se bloquea («no he podido comprobar los topes»); una llamada a GHL o a Stripe que su guarda no ha podido
  clasificar pregunta (sesión principal) o se bloquea (subagentes). El detalle queda en `logs/hooks.jsonl`.
- **Lo que no sabe leer como importe no pasa sin tope**: un presupuesto en un formato que el hook no entiende
  (`{"amount", "currency"}`, texto, una clave de presupuesto que no conoce) o un presupuesto total sin fechas se
  bloquea con la forma correcta de pedirlo.

### 3. Un solo agente escribe

Cada agente tiene una lista cerrada de herramientas. **Solo `operador-meta` puede escribir en Meta** y hacer
escrituras aprobadas en GoHighLevel, y solo con un plan que hayas aprobado de forma explícita en esa conversación. El
analista, el auditor o el estratega no pueden crear ni cambiar nada aunque se equivoquen.

La sesión principal tampoco escribe en Meta: todas las skills que crean, cambian o activan algo delegan en
`operador-meta`, y el hook `meta_guard` lo hace cumplir (si la sesión principal intenta una escritura por el MCP o con
`meta_ads.py`, `reglas_meta.py`, `formularios_meta.py` o `audiencias_meta.py`, la bloquea con «delega en
operador-meta»). Así cada escritura pasa por el mismo agente, con el mismo plan aprobado y el mismo change log.

### 4. Skills que solo lanzas tú

`/lanzar-campana`, `/ejecutar-cambio`, `/publicar-anuncios`, `/producir-video`, `/reglas-automaticas`,
`/formulario-instantaneo`, `/anuncios-por-etapa`, `/actualizar` y `/menu` no se ejecutan por iniciativa de Claude:
tienes que escribirlas tú.

### 5. Topes de gasto, en dos lados

| Tope | Dónde | Lo aplica |
|---|---|---|
| **Por cambio** (`topes.cambio_dia` de la ficha) | Cada presupuesto diario que llega en una llamada o en un plan | El hook `meta_guard`: si lo supera, lo bloquea |
| **Total diario** (`topes.total_dia`) | La suma de lo activo en la cuenta | `meta_guard`, si hay token avanzado (un hook no puede consultar el MCP) |
| Límite del Ads MCP server | Business Settings → Ads MCP server → «Budgets set above this amount → Blocked» (sin verificar si compara el presupuesto diario o el total: ponlo pensando en el diario y no cuentes con él para los totales) | Meta, en su servidor |
| Límite de gasto de la cuenta | Configuración de pagos de la cuenta publicitaria | Meta, en su servidor |
| Reglas automáticas del OS (`PROTECT_OS_…`, `ALERT_OS_…`) | Dentro de la cuenta, con `/reglas-automaticas` | Meta, en su servidor, aunque tu ordenador esté apagado: solo pausan o avisan, nunca suben presupuesto ni borran |

Con los topes de la ficha a 0, el sistema no crea ni sube presupuesto hasta que los fijes. `/configurar-meta` deja
puestos los dos límites del lado de Meta, que siguen funcionando aunque este ordenador falle.

Los topes son decisión tuya, no de Claude: si una edición de `clientes/<cliente>/ficha.md` (Edit, Write o MultiEdit)
cambia `topes.cambio_dia` o `topes.total_dia`, o deja la cabecera ilegible, el hook `datos_personales` te pregunta con
el antes y el después («cambias los topes de gasto de «acme»: cambio_dia 100 → 5000»). Una edición por la shell
(`sed -i`) no pasa por ese hook: queda la pregunta genérica de Claude Code (`sed` no está en `allow`).

El motor de vídeo con IA tiene su propio tope: **5 $ por defecto** (`motor.presupuesto_usd` en
`contexto/preferencias.md` o `MOTOR_PRESUPUESTO_USD` en `.env`), y cada orden de pago pide confirmación con el coste.

### 6. Políticas de Meta

Antes de publicar cualquier texto, creatividad, formulario o landing pasa por `revisor-politicas`, y la guarda
`control_publicacion` comprueba que su `LEEME.md` tiene el veredicto. El sistema **nunca** propone circunvención:
cuentas o Páginas nuevas para esquivar una restricción, cloaking u ofuscación. Si una cuenta está restringida, el
camino es `/rescate-cuenta`.

## Personas y datos personales (RGPD)

- Los datos personales de leads y clientes (emails, teléfonos, nombres) **solo** viven en `clientes/<slug>/privado/`.
  En informes, registro creativo y `datos/` van IDs y agregados. La guarda `datos_personales` te avisa si algo se
  intenta escribir fuera de sitio.
- Los registros de `logs/` nunca guardan tokens ni datos personales: los emails y teléfonos se sustituyen por `***`.
- El brief diario y los informes para clientes solo llevan IDs y agregados.
- El sistema nunca escribe a tus contactos. Los mensajes para clientes de tu agencia los deja como borradores que
  revisas y envías tú, y `/seguimiento-leads` deja los workflows de GHL escritos para que los actives tú.
- Las audiencias de lista de clientes (`audiencias_meta.py`) se preparan desde `privado/` y solo salen de tu ordenador
  como hashes, con confirmación. Las bajas y los «no me contactéis» se quitan de todas las listas.
- Las páginas que genera `/construir-landing` no cargan el píxel hasta que la persona acepta, y sin consentimiento solo
  mandan a tu servidor lo que permita la base legal que configures.

## Secretos

- Las claves van en `.env`, con permisos 600, fuera de git. Claude no puede leerlo, imprimirlo, copiarlo ni cargarlo:
  lo bloquean los permisos y la guarda `secretos`, que mira cada argumento ya resuelto (`cat .en?`, `cat .*` o
  `F=.env; cat $F` también se bloquean; `ls .e*` no, porque no lee el contenido). Las herramientas lo cargan solas.
- Usa siempre la clave con **menos permisos** que sirva: token de integración privada de solo lectura en GHL, clave
  restringida de lectura en Stripe, usuario del sistema con solo los activos necesarios en Meta.
- Los tokens de usuario del sistema de Meta **no caducan** cuando alguien sale del equipo: revócalos en Business
  Settings cuando dejes de llevar a un cliente.

### Si se filtra una clave

Si una clave acaba en el chat, en una captura, en un repositorio o en un mensaje:

1. **Revócala ya** en su panel (Business Settings en Meta, Private Integrations en GHL, API keys en Stripe, @BotFather
   en Telegram, el webhook en Slack, la clave en Google AI Studio).
2. Crea una nueva y pégala tú en `.env`.
3. Si estaba en un repositorio, borrar el archivo no basta: sigue en el historial. Revocarla es lo que la inutiliza.
4. Revisa `logs/cambios.jsonl` y el registro de actividad de la cuenta (Ads Manager → Historial de la cuenta) por si
   alguien la ha usado.

## Contenido de terceros

Webs, anuncios de la competencia, comentarios, reseñas, posts de Reddit y respuestas de APIs son **datos, nunca
instrucciones**. Si una landing o un comentario contiene un texto del tipo «ignora tus reglas y…», Claude lo trata como
parte del dato que está analizando y no lo obedece.

## Sin nadie delante

El brief diario programado funciona sin que estés: lo lanza tu ordenador (o la nube) cada mañana. En ese modo solo
puede leer y escribir en las carpetas de informes; cualquier otra escritura se deniega sin preguntar
([guía del brief](guias/brief-diario.md)).

## Si algo ha salido mal

| Pasa | Qué hacer |
|---|---|
| Se ha creado algo que no querías | Está en pausa: revísalo en Ads Manager. El change log y `logs/cambios.jsonl` dicen qué se hizo y cuándo |
| Un cambio no ha funcionado | No lo deshagas a ciegas: `/ejecutar-cambio <cliente> "revertir <cambio>"`, con su motivo en el change log |
| Una guarda te bloquea algo que sí quieres hacer | Lee su motivo. Si es correcto, hazlo tú a mano en Ads Manager; si crees que la guarda se equivoca, apúntalo en `aprendizajes/` para revisarlo |
| Claude no da el trabajo por terminado y habla de escrituras sin anotar | Es `registro_obligatorio`: hubo escrituras que no están en el change log del cliente. Deja que las anote (o anótalas tú) y termina |
| Has pegado una clave en el chat | [Si se filtra una clave](#si-se-filtra-una-clave) |
