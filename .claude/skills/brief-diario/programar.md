# /brief-diario programar

Asistente en el hilo principal: una pregunta cada vez, con la opción recomendada primero, y comprobando cada paso
antes de seguir. La guía para el usuario, con capturas de lo que verá, es `docs/guias/brief-diario.md`.

**Claves y `.env`**: nunca leas, muestres ni pidas que te peguen en el chat un token, una URL de webhook o una
contraseña. El usuario abre `.env` con su editor y pega la línea él mismo (Mac: `open -e .env`; Windows:
`notepad .env`; Linux: `nano .env`, desde su terminal). Si te pega una clave en el chat, dile que la revoque y cree
otra.

## 0. Punto de partida
1. Lee la cabecera de `contexto/preferencias.md` (bloque `brief:`). Si `programado_con` no está vacío, resume cómo
   está (canal, hora, clientes, método) y pregunta qué quiere hacer: cambiar canal, hora o clientes, cambiar de
   método, probar o desprogramar.
2. Comprueba que hay al menos un cliente `activo` con `meta.cuenta` en la ficha (`python3 -I herramientas/estado.py
   resumen --json` y las fichas). Si no hay, recomienda `/cliente-nuevo` antes: el brief solo diría que no hay clientes.

## 1. Canal

| Canal | Para quién | Tiempo |
|---|---|---|
| **Telegram** (recomendado) | Llega al móvil al momento, gratis, se lee bien | 5 min |
| Email | Si prefieres la bandeja de entrada | 5–10 min (contraseña de aplicación) |
| Slack | Si tu equipo vive en Slack | 5 min |

### Telegram
1. En Telegram abre **@BotFather** (cuenta oficial, con marca de verificación), envía `/newbot`, elige un nombre
   («Brief Meta Ads») y un usuario que acabe en `bot`. BotFather responde con un token `123456789:AA...`.
2. El usuario abre `.env` y añade `TELEGRAM_BOT_TOKEN=<token>`. Guarda.
3. En Telegram abre el bot (el enlace `t.me/<usuario_del_bot>` que dio BotFather), pulsa **Iniciar** y escríbele
   «hola». Para recibirlo en un grupo del equipo: añade el bot al grupo y escribe algo allí.
4. `python3 -I herramientas/notificar.py telegram-chat-id --guardar` → guarda `TELEGRAM_CHAT_ID` en `.env`.
   - Código 1 «aún no tiene mensajes» → que escriba al bot y repite.
   - Varios chats → enseña la lista y que añada él a mano `TELEGRAM_CHAT_ID=<número>` (el de un grupo empieza por `-`).
   - Código 2 → token mal copiado o bot con webhook: el mensaje dice qué hacer.
5. `python3 -I herramientas/notificar.py probar --canal telegram` y pregunta si ha llegado.

### Email
1. Necesita un servidor SMTP con contraseña de aplicación:
   - Gmail: verificación en dos pasos activada → contraseña de aplicación en la cuenta de Google →
     `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`;
   - Microsoft 365 de empresa: el SMTP con contraseña suele estar desactivado por el administrador; si da error de
     autenticación, mejor Telegram o Slack;
   - otro proveedor: sus datos SMTP (puerto 465 con SSL o 587 con STARTTLS; otros no se aceptan).
2. El usuario añade a `.env`: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USUARIO`, `SMTP_CLAVE` y `EMAIL_DESTINO`.
3. `python3 -I herramientas/notificar.py probar --canal email`. Si no llega, que mire en spam y marque «no es spam».

### Slack
1. En `api.slack.com/apps`: **Create New App** → *From scratch* → nombre y workspace → **Incoming Webhooks** →
   activar → **Add New Webhook to Workspace** → elegir el canal (mejor uno propio, p. ej. `#brief-diario`) → copiar la
   URL `https://hooks.slack.com/services/...`. Esa URL es una clave: quien la tenga puede escribir en el canal.
2. El usuario añade `SLACK_WEBHOOK_URL=<url>` a `.env`.
3. `python3 -I herramientas/notificar.py probar --canal slack`.

## 2. Hora y clientes
- Hora local, por defecto `08:00`. En una agencia, antes de la primera reunión del día.
- Clientes: `todos` (por defecto) o una lista de slugs separada por comas.

## 3. Método

| | **desktop** (por defecto) | **sistema** | **nube** (ligero, experimental) |
|---|---|---|---|
| Qué es | Tarea programada de Claude Desktop | launchd (Mac), cron (Linux) o Programador de tareas (Windows) lanzando `claude -p` | Tarea programada en la nube de Claude Code |
| Ordenador | Encendido, despierto y con la app abierta | Encendido; no hace falta abrir nada | Puede estar apagado |
| Si estaba apagado o dormido | Al abrir la app o despertar, una ejecución de recuperación | Mac: al despertar o al iniciar sesión; Linux: en la siguiente hora en punto hasta 4 h después o al arrancar; Windows: en cuanto se pueda | No aplica |
| Brief completo (fichas, change log, evaluaciones, archivos) | Sí | Sí | No: solo Meta, GHL y Stripe y el aviso |
| Permisos | Los del proyecto; si algo pide permiso, la ejecución espera | Lista cerrada de herramientas; lo demás se deniega | Modo automático de la nube |

Recomienda **desktop** si usa Claude Desktop; **sistema** si trabaja en la terminal o no quiere depender de la app;
**nube** solo si el ordenador suele estar apagado por la mañana y le basta un aviso sin historial.

### desktop
Si estás dentro de Claude Desktop y puedes crear tareas programadas, créala tú con estos datos y enséñaselos; si no,
guía al usuario:
1. Claude Desktop actualizado. Pestaña **Code** → **Scheduled** (en la barra lateral o en *More*; en versiones
   anteriores se llama *Routines*) → **New task** (si aparece un menú, *Set up manually*; si pregunta Local o Cloud,
   *Local*).
2. **Name**: `brief-diario`. **Instrucciones**: `/brief-diario todos`.
3. **Advanced settings** → *General* → activa **Only on this computer** → **Local folder**: la carpeta de Meta Ads OS.
4. **Trigger**: *Daily* a la hora elegida.
5. Modo de permisos: el normal (pide permiso). Modelo: Sonnet basta y gasta menos cuota.
6. **Create**. En la ficha de la tarea, **no** actives *Worktree*: la carpeta de trabajo tiene `clientes/` y
   `contexto/`, que no están en git, y una copia limpia no los vería.
7. **Run now** y quédate mirando: si pide permiso, acepta siempre solo lecturas, escribir en `informes/diario/` y
   `clientes/*/informes/diario/`, y `notificar.py enviar`; deniega cualquier otra cosa. Si se para cada día al escribir
   el informe, pon el modo de permisos de la tarea en *Accept edits* (acepta solo ediciones de archivos de la carpeta;
   Meta, GHL y Stripe siguen pidiendo permiso y el brief no los usa para escribir).
8. En **Settings → Desktop app** (o *This computer → System*), activa **Keep computer awake**. Cerrar la tapa del
   portátil lo duerme igualmente.

### sistema
1. Requisitos (compruébalos tú):
   - Meta responde: una llamada a `ads_get_ad_accounts`. Si el MCP pide iniciar sesión, que haga `/mcp` → `meta-ads`
     ahora: `claude -p` conecta los servidores de `.mcp.json` y ejecuta los hooks sin preguntar por la confianza de la
     carpeta, pero no puede abrir el navegador para iniciar sesión;
   - en Mac, la carpeta **no** está en Escritorio, Documentos ni Descargas (macOS no deja que una tarea de fondo lea ahí
     sin «Acceso total al disco»). Si lo está, propón moverla (p. ej. a `~/meta-ads-os`) antes de seguir.
2. Instala (es una escritura en el sistema: pedirá permiso, y está bien):
   - Mac: `bash .claude/skills/brief-diario/programacion/instalar-mac.sh <HH:MM>`
   - Linux: `bash .claude/skills/brief-diario/programacion/instalar-linux.sh <HH:MM>`
   - Windows (Git Bash o PowerShell): `powershell -NoProfile -ExecutionPolicy Bypass -File
     .claude/skills/brief-diario/programacion/instalar-windows.ps1 -Hora <HH:MM>`
3. Prueba de punta a punta, por el mismo camino que usará cada mañana:
   - Mac: `bash .claude/skills/brief-diario/programacion/instalar-mac.sh --probar`
   - Linux: `bash .claude/skills/brief-diario/programacion/brief.sh`
   - Windows: `... instalar-windows.ps1 -Probar`

   Tarda de 2 a 6 minutos. Luego mira la última línea de `logs/notificaciones.jsonl` (debe ser de hoy con
   `"ok": true`) y, si no, las últimas líneas de `logs/brief-diario-AAAA-MM.log`.
4. Si el registro dice que no hay sesión o pide `/login`: el usuario ejecuta `claude setup-token` **en su terminal**
   (no aquí), copia el token y añade a `.env` `CLAUDE_CODE_OAUTH_TOKEN=<token>`. Lo usa solo el lanzador. Dura un año:
   que lo apunte en el calendario.
5. Lo que permite la ejecución sin nadie está en `programacion/herramientas-permitidas.txt`: lecturas, los
   subcomandos de lectura de las herramientas, `notificar.py enviar` y escribir solo en las carpetas de informes.
   Suma con el `allow` de `.claude/settings.json`; lo que pediría permiso se deniega sin preguntar, y
   `herramientas-denegadas.txt` cierra además lo que escribe, descarga o toca `.env`.

### nube (ligero, experimental)
Avísalo claro: es una función en *research preview* de Claude Code, el brief es ligero (sin fichas, change log,
evaluaciones ni archivos guardados) y la sesión corre en modo automático, así que la protección real contra
escrituras en Meta es la regla del Ads MCP server en Business Settings (la deja `/configurar-meta`).
1. Requisitos: plan Pro o superior; una copia del repositorio de Meta Ads OS en su GitHub, accesible desde su cuenta
   de claude.ai; Meta añadido como conector en claude.ai (`claude.ai/customize/connectors`, URL
   `https://mcp.facebook.com/ads`) y, si los usa, GHL y Stripe.
2. Genera el encargo con los datos de las fichas activas (nada de `.env`) y enséñaselo para que lo pegue:

   ```text
   /brief-diario todos

   Ejecución en la nube (modo ligero). Clientes:
   - <slug> · <nombre> · cuenta <meta.cuenta> · dataset <meta.dataset> · evento <meta.evento_principal> · <moneda> · <zona_horaria> · CRM <crm.tipo> · Stripe <sí|no>
   Solo lectura en Meta, GHL y Stripe: no crees, cambies, actives ni borres nada. Sin commits, push ni ramas.
   ```
3. Pasos en `claude.ai/code/routines` (o `/schedule` en la CLI): **New** → nombre `brief-diario-nube` → el encargo →
   **Repository**: su copia → **Cloud environment**: crea uno propio con **Network access** *Custom* y
   `api.telegram.org` (o `hooks.slack.com`) en *Allowed domains*, y las variables `TELEGRAM_BOT_TOKEN` y
   `TELEGRAM_CHAT_ID` (o `SLACK_WEBHOOK_URL`). Las variables las ve cualquiera que use ese entorno: que sea solo suyo.
   Los *network secrets* no sirven aquí porque el token de Telegram va en la URL, no en una cabecera.
4. **Connectors**: deja solo Meta (y GHL o Stripe si los usa); quita el resto.
5. **Trigger**: *Schedule* → *Daily* a la hora elegida (hora local). **Run now** para probar.
6. El email por SMTP no está verificado en la nube: usa Telegram o Slack.

## 4. Guardar las preferencias
Edita solo las líneas del bloque `brief:` de la cabecera de `contexto/preferencias.md`, respetando el formato (dos
espacios de sangría, hora entre comillas):

```yaml
brief:
  canal: telegram
  hora: "08:00"
  clientes: todos
  programado_con: desktop
```

## 5. Cierre
En cinco líneas: canal, hora, clientes, método, cuándo llega el primero y cómo cambiarlo (`/brief-diario programar`).
Recuérdale que el brief nunca toca nada: solo avisa.

## Desprogramar
Pide confirmación por escrito antes de quitar nada y di exactamente qué se quita:
- desktop: el usuario pausa o borra la tarea en **Scheduled** (el borrado solo se hace desde su ficha);
- sistema: Mac `instalar-mac.sh --quitar` (descarga la tarea y borra su `.plist` de `~/Library/LaunchAgents`), Linux
  `instalar-linux.sh --quitar` (quita sus líneas del crontab), Windows `instalar-windows.ps1 -Quitar`;
- nube: pausar o borrar la tarea en `claude.ai/code/routines`.

Después pon `programado_con: ""` en `contexto/preferencias.md`.
