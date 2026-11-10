# Brief diario: tus cuentas revisadas cada mañana en Telegram

Para quién: cualquiera que lleve una o varias cuentas de Meta con Meta Ads OS, sobre todo agencias con varios clientes.
Qué consigues: que cada mañana, antes de abrir nada, te llegue al móvil un mensaje corto con el estado de cada cliente
(🔴 roto, 🟡 vigilar, 🟢 en orden, ⚪ sin datos) y, solo si algo está roto, qué hacer y con qué comando.

Lo que **no** hace: tocar nada. El brief solo lee Meta, GHL y Stripe y escribe sus propios informes. Ni pausa, ni sube
presupuestos, ni «arregla» nada por su cuenta, tampoco cuando se ejecuta solo de madrugada. Decides tú, después, con
`/diagnostico` o `/ejecutar-cambio`.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial a 2026-11-09: compruébalo en tu
pantalla. Los nombres de botones de Claude Desktop y de las rutinas en la nube cambian a menudo.

---

## El recorrido en cuatro pasos

| Paso | Qué haces | Tiempo |
|---|---|---|
| 1 | Lo pruebas a mano: `/brief-diario` | 3 min |
| 2 | Creas el bot de Telegram y lo conectas | 5 min |
| 3 | Lo programas: `/brief-diario programar` | 5 min |
| 4 | Mañana compruebas que ha llegado | 1 min |

Puedes hacer los pasos 2 y 3 con el asistente (`/brief-diario programar`), que te pregunta lo justo y comprueba cada
paso. Esta guía es la versión larga, por si quieres saber qué pasa por debajo o algo falla.

---

## 1. Qué te llega

Un mensaje así (el ejemplo es de tres clientes):

```
Brief diario · 2026-11-10 · 🔴 1 · 🟡 1 · 🟢 1

🔴 Clínica Sonrisa — Lead a 0 en el dataset desde ayer a mediodía (navegador y servidor) con 95 €/día activos.
→ Envía un lead de prueba desde la landing; si no aparece en Events Manager, /diagnostico clinica-sonrisa "tracking roto". No pauses nada.

🟡 Acme Automations — Presupuesto de un conjunto subido en Meta el 2026-11-09 sin anotar en el change log.
→ Averigua quién lo hizo y anótalo. Lo demás, en orden.

🟢 Nimbo — En ritmo (96 %), 14 pruebas iniciadas ayer (banda 8–21), señal bien.

Evaluaciones de hoy: Acme Automations · campaña 120200000000000000 (creativos nuevos) → /informe-semanal acme-automations.
No toques hoy: el CPA de 1–3 días de ningún cliente; Acme · conjunto 120200000000000001 hasta el 2026-11-16.
```

Para cada cliente activo, el brief mira:

- **gasto frente al ritmo** (lo gastado ayer y en la semana frente a los presupuestos activos);
- **errores y rechazos** de anuncios y de la cuenta (con el token avanzado, `meta_ads.py anuncios --estado` lista los
  anuncios rechazados, con problemas o en revisión y el motivo que da Meta);
- **resultados frente al ruido**: si los eventos de ayer caen dentro de la banda normal de los 14 días anteriores
  (`estadistica.py banda`); un día malo dentro de la banda no es noticia;
- **señal del dataset** en las últimas 24–48 h, por navegador y servidor;
- **cambios en la cuenta** desde el último brief que no están en tu change log (en una agencia, suele ser alguien del
  cliente tocando la cuenta);
- **leads, citas y pruebas de ayer**, si la ficha tiene GHL o Stripe, y con GHL cuánto tarda un lead en reservar
  cita (mediana de los últimos 7 días, «del alta a la cita»);
- **evaluaciones que vencen hoy** y **qué no tocar** (lo que cambió hace menos de 7 días).

Qué significa cada color (las reglas exactas están en `.claude/skills/brief-diario/formato.md` §1):

| | Cuándo | Qué haces |
|---|---|---|
| 🔴 | Algo está roto: cuenta deshabilitada, evento principal a 0 con gasto, gasto muy por encima del presupuesto, anuncios principales rechazados, leads en Meta que no llegan al CRM | La acción que dice el mensaje, hoy |
| 🟡 | Algo raro que aún no es una rotura: gasto por debajo del ritmo, resultado fuera de la banda, un cambio sin anotar | Vigilar; mañana el brief lo vuelve a mirar |
| 🟢 | En ritmo, con señal y sin rechazos | Nada. Con el CPA de ayer no se decide nada |
| ⚪ | Sin campañas activas o sin acceso a los datos | Si debería tener datos, mira «Solución de problemas» |

**El speed to lead no está en el brief.** El de verdad son los minutos hasta el primer contacto con el lead (el
objetivo es menos de 5: `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`), y para
eso hace falta la hora del primer mensaje o llamada saliente, que la lectura de GHL del sistema no lee. Lo que sí da
el brief es «del alta a la cita» (horas desde que entra el lead hasta que reserva): si sube mucho, algo se ha frenado
en el seguimiento. El speed to lead míralo en GHL (en las conversaciones, o con un informe o un campo de tiempo
hasta el primer contacto si tu cuenta lo tiene).

Dónde queda todo:

- el resumen que te llega: `informes/diario/AAAA-MM-DD.md`;
- el informe completo de cada cliente: `clientes/<slug>/informes/diario/AAAA-MM-DD.md`. `/hoy` lo lee al empezar el día.

Ni los archivos ni el mensaje llevan datos personales de leads o clientes finales: solo IDs de Meta y cifras agregadas.

---

## 2. Antes de empezar

1. **Claude Code** instalado y con tu sesión iniciada (la misma suscripción con la que trabajas).
2. **La carpeta de Meta Ads OS abierta al menos una vez** en Claude Code, aceptando la confianza de la carpeta y la
   conexión `meta-ads` (te lo pregunta la primera vez).
3. **Al menos un cliente activo** con su cuenta de Meta en la ficha. Si no, `/cliente-nuevo`.
4. **Meta conectado**: `/conectar meta`. Si el cliente usa GHL o Stripe, `/conectar ghl` o `/conectar stripe` (la
   lectura sin nadie delante usa los tokens de solo lectura de `.env`: `docs/guias/ghl-meta.md` §1).
5. **Pruébalo a mano** en Claude Code:

   ```
   /brief-diario
   ```

   Tarda de 2 a 6 minutos según el número de clientes. Al final te enseña el resumen y te dice que aún no hay canal
   configurado: es lo normal. Si algún cliente sale ⚪ sin motivo, arréglalo ahora (§9): lo que falla contigo delante
   también fallará a las 8 de la mañana.

Otras formas de lanzarlo cuando quieras: `/brief-diario acme-automations` (un solo cliente, aunque esté en pausa) y
`/brief-diario probar` (lo ejecuta y lo envía ahora).

---

## 3. Telegram (recomendado)

Gratis, llega al momento y se lee bien en el móvil.

### Crea el bot

1. En Telegram, busca **@BotFather** (la cuenta oficial, con la marca de verificación) y envíale `/newbot`.
2. Ponle un nombre (lo que verás en el chat, p. ej. «Brief Meta Ads») y un usuario que termine en `bot`
   (p. ej. `brief_acme_bot`).
3. BotFather te responde con un **token** del tipo `123456789:AAH...`. Es la clave del bot: quien la tenga puede enviar
   mensajes como el bot y leer lo que le escriban. No la pegues en el chat de Claude ni en ningún otro sitio.

### Guarda el token en `.env`

Abre `.env` (en la carpeta de Meta Ads OS) con tu editor:

- Mac: `open -e .env`
- Windows: `notepad .env`
- Linux: `nano .env`

Y añade una línea (o quita el `#` de la que ya está):

```
TELEGRAM_BOT_TOKEN=123456789:AAH...
```

Guarda y cierra. Claude nunca lee ni enseña `.env`: las herramientas cargan sus claves solas.

### Saca tu chat_id

1. En Telegram, abre tu bot (el enlace `t.me/<usuario_del_bot>` que te dio BotFather), pulsa **Iniciar** y escríbele
   «hola».
   - Para recibirlo en un **grupo del equipo**: añade el bot al grupo y escribe en él `/start@<usuario_del_bot>` (los
     bots de grupo solo ven los comandos dirigidos a ellos).
2. En la terminal, desde la carpeta de Meta Ads OS (o pídeselo a Claude):

   ```
   python3 -I herramientas/notificar.py telegram-chat-id --guardar
   ```

   Añade `TELEGRAM_CHAT_ID=...` al final de `.env` sin tocar lo demás. Si el bot ve varios chats (tú y un grupo), te
   los enseña y no guarda nada: copia tú el que quieras a `.env` (el de un grupo empieza por `-`).
   En Windows, si `python3` no existe, usa `python` o `py -3` con los mismos argumentos.
3. Manda una prueba:

   ```
   python3 -I herramientas/notificar.py probar --canal telegram
   ```

   Si te llega «✅ Meta Ads OS · prueba del brief diario», ya está. Si no, mira §9.

### Dile al sistema que use Telegram

`/brief-diario programar` lo hace por ti. A mano: en `contexto/preferencias.md`, en la cabecera, deja el bloque así:

```yaml
brief:
  canal: telegram
  hora: "08:00"
  clientes: todos
  programado_con: ""
```

`clientes` puede ser `todos` o una lista de slugs separados por comas (`acme-automations, nimbo`).

---

## 4. Alternativas: email y Slack

Solo necesitas un canal. Si tienes credenciales de varios, manda el que diga `brief.canal`.

### Email

Necesitas un buzón que permita enviar por SMTP con una contraseña de aplicación (no la contraseña normal):

| Proveedor | Qué hacer | `.env` |
|---|---|---|
| Gmail o Google Workspace | Activa la verificación en dos pasos y crea una **contraseña de aplicación** en tu cuenta de Google (Seguridad) | `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587` |
| Microsoft 365 de empresa | El envío SMTP con contraseña suele estar desactivado por el administrador. Si tu administrador no lo activa para tu buzón, usa Telegram o Slack | `SMTP_HOST=smtp.office365.com`, `SMTP_PORT=587` |
| Otro | Sus datos SMTP. Solo se acepta el puerto 465 (SSL) o 587 (STARTTLS): nada sin cifrar | Los de tu proveedor |

Y además:

```
SMTP_USUARIO=tu-buzon@example.com
SMTP_CLAVE=la-contraseña-de-aplicación
EMAIL_DESTINO=donde-quieres-el-brief@example.com
```

Prueba: `python3 -I herramientas/notificar.py probar --canal email`. El asunto del brief es su título
(«Brief diario · 2026-11-10 · 🔴 1 · 🟡 1 · 🟢 1»). El primer día mira en spam y márcalo como «no es spam».

### Slack

1. En `api.slack.com/apps`: **Create New App** → *From scratch* → nombre y workspace.
2. **Incoming Webhooks** → actívalo → **Add New Webhook to Workspace** → elige el canal (mejor uno propio, p. ej.
   `#brief-diario`).
3. Copia la URL `https://hooks.slack.com/services/...`. Es una clave: quien la tenga puede escribir en ese canal.
4. En `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...`
5. Prueba: `python3 -I herramientas/notificar.py probar --canal slack`.

---

## 5. Prográmalo

```
/brief-diario programar
```

El asistente te pregunta la hora (por defecto `08:00`, hora de tu ordenador), qué clientes y el método. Hay tres:

| | **desktop** (por defecto) | **sistema** | **nube** (ligero, experimental) |
|---|---|---|---|
| Qué es | Una tarea programada de Claude Desktop | El programador de tu sistema (launchd en Mac, cron en Linux, Programador de tareas en Windows) lanzando Claude Code sin ventana | Una rutina de Claude Code en los servidores de Anthropic |
| Necesitas | Claude Desktop abierto y el ordenador despierto | El ordenador encendido y tu sesión iniciada; no hace falta abrir nada | Tu copia de Meta Ads OS en GitHub y Meta como conector de claude.ai |
| Brief completo | Sí | Sí | No: sin fichas, change log, evaluaciones ni archivos guardados |
| Si algo pide permiso | La tarea se queda esperando a que respondas | Se deniega sin preguntar | Modo automático |
| Elígelo si | Usas Claude Desktop a diario | Trabajas en la terminal o no quieres depender de la app | Tu ordenador suele estar apagado por la mañana y te basta un aviso |

Usa **un solo método**. Con dos a la vez te llegará el brief dos veces.

Cada brief gasta uso de tu suscripción de Claude, como una conversación de unos minutos (más cuantos más clientes).
Por eso las ejecuciones programadas usan Sonnet. Leer Meta, GHL y Stripe y enviar por Telegram, Slack o email no
cuesta nada.

### Método desktop

Si estás en Claude Desktop, el asistente puede crear la tarea por ti; si no, te guía. Los pasos, por si los haces tú:

1. Claude Desktop actualizado. Pestaña **Code** → **Scheduled** → **New task** (si pregunta, *Local*, no *Cloud*).
2. **Name**: `brief-diario`. **Instrucciones**: `/brief-diario todos`.
3. **Only on this computer** → **Local folder**: la carpeta de Meta Ads OS.
4. **Trigger**: *Daily* a tu hora. Modelo: Sonnet.
5. **Create**. No actives **Worktree**: trabajaría en una copia limpia sin tus `clientes/` ni `contexto/`.
6. **Run now** y quédate mirando la primera vez. Si te pide permiso, acepta solo: lecturas, escribir en
   `informes/diario/` y `clientes/*/informes/diario/`, y `notificar.py enviar`. Cualquier otra cosa, deniégala.
   Si cada día se para al escribir el informe, cambia el modo de permisos de la tarea a *Accept edits* (acepta
   ediciones de archivos de la carpeta; Meta, GHL y Stripe siguen pidiendo permiso, y el brief no escribe en ellos).
7. En los ajustes de la app, activa **Keep computer awake**. Cerrar la tapa del portátil lo duerme igualmente.

No verificado: que las instrucciones de una tarea de Desktop acepten un comando con `/`. Si la tarea no lo reconoce,
escribe en su lugar «Ejecuta la skill brief-diario para todos los clientes».

### Método sistema

El asistente comprueba los requisitos y ejecuta el instalador (te pedirá permiso: es una escritura en tu sistema, y
está bien). Por debajo:

| Sistema | Instalar a las 08:00 | Probar ahora por el mismo camino |
|---|---|---|
| Mac | `bash .claude/skills/brief-diario/programacion/instalar-mac.sh 08:00` | `bash .claude/skills/brief-diario/programacion/instalar-mac.sh --probar` |
| Linux | `bash .claude/skills/brief-diario/programacion/instalar-linux.sh 08:00` | `bash .claude/skills/brief-diario/programacion/brief.sh` |
| Windows | `powershell -NoProfile -ExecutionPolicy Bypass -File .claude/skills/brief-diario/programacion/instalar-windows.ps1 -Hora 08:00` | El mismo con `-Probar` en lugar de `-Hora 08:00` |

La prueba tarda de 2 a 6 minutos. Haz siempre la prueba: es la única forma de saber que la ejecución sin nadie
encuentra tu sesión de Claude y tus conexiones.

Antes de instalar en un **Mac**: la carpeta de Meta Ads OS no puede estar en Escritorio, Documentos, Descargas ni
iCloud Drive. macOS no deja que una tarea de fondo lea esas carpetas y el brief fallaría con «Operation not
permitted». Muévela (p. ej. a `~/meta-ads-os`) antes de instalar; el instalador te avisa si no lo has hecho.

Qué usa la ejecución sin nadie:

- leer archivos de la carpeta (menos `.env`, que está bloqueado);
- escribir solo en `informes/diario/` y `clientes/*/informes/diario/`;
- los subcomandos de lectura de `estado.py`, `estadistica.py`, `meta_ads.py`, `ghl.py` y `stripe_datos.py`, y
  `notificar.py enviar`;
- las lecturas del MCP de Meta.

La lista exacta está en `.claude/skills/brief-diario/programacion/herramientas-permitidas.txt`, y lo prohibido
expresamente (crear, cambiar o activar en Meta, GHL o Stripe, leer `.env`, escribir fuera de los informes) en
`herramientas-denegadas.txt`. Cualquier cosa que contigo delante te pediría permiso se deniega sin preguntar.

Si la prueba dice que no hay sesión (en el registro verás «login», «not logged in» o «authentication»):

1. En **tu** terminal (no dentro de Claude), ejecuta `claude setup-token` y sigue los pasos.
2. Copia el token que te da y añádelo a `.env`: `CLAUDE_CODE_OAUTH_TOKEN=...`
3. Repite la prueba.

Ese token lo usa solo el lanzador del brief y dura un año: apunta en el calendario cuándo caduca. Si lo tienes, el
lanzador quita `ANTHROPIC_API_KEY` de su entorno para que el brief no se cobre de una clave de API.

### Método nube (ligero, experimental)

Las rutinas de Claude Code están en *research preview*: pueden cambiar o fallar. El brief en la nube es **ligero**:
se ejecuta en una copia limpia de tu repositorio, sin `clientes/`, `contexto/` ni `logs/`, así que no ve tus fichas,
tu change log ni tus evaluaciones, y no guarda nada. Te avisa de roturas en Meta, GHL y Stripe y poco más.

Además, la sesión corre en modo automático. La protección de verdad contra escrituras en Meta es la regla del Ads MCP
server en Business Settings, que deja puesta `/configurar-meta`: compruébala antes.

1. Requisitos: plan Pro o superior, tu copia de Meta Ads OS en GitHub accesible desde claude.ai, y Meta añadido como
   conector en `claude.ai/customize/connectors` con la URL `https://mcp.facebook.com/ads` (y GHL o Stripe si los usas).
2. `/brief-diario programar` → método *nube*: te genera el encargo con la lista de clientes (sin ninguna clave).
3. En `claude.ai/code/routines` (o `/schedule` en Claude Code): **New** → nombre `brief-diario-nube` → pega el encargo.
4. **Repository**: tu copia.
5. **Cloud environment**: crea uno **solo tuyo** con:
   - **Network access** *Custom* y `api.telegram.org` (o `hooks.slack.com`) en *Allowed domains*;
   - las variables `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` (o `SLACK_WEBHOOK_URL`). Quien use ese entorno las ve.
6. **Connectors**: deja solo Meta (y GHL o Stripe si los usas).
7. **Trigger**: *Schedule* → *Daily* a tu hora. **Run now** para probar.

El email por SMTP no está verificado en la nube: usa Telegram o Slack.

---

## 6. Mañana: comprueba que ha llegado

- Te ha llegado → listo. Échale un ojo unos días: si un cliente sale siempre 🟡 por algo que sabes que es normal
  (p. ej. gasto bajo a propósito), díselo a Claude para ajustar la ficha.
- No te ha llegado → §9. Lo primero, la última línea de `logs/notificaciones.jsonl` y el estado de la tarea (§8).

Si el brief no se pudo generar, el método sistema te manda igualmente un aviso corto
(«⚠️ Brief diario · 2026-11-10 · no se ha generado») con dónde mirar. Un día sin mensaje y sin aviso quiere decir que
la tarea no llegó a ejecutarse.

---

## 7. ¿Y si el ordenador estaba apagado o dormido?

El brief nunca sale antes de tu hora y solo una vez al día (lo controla `logs/brief-diario.ultimo`). Si a esa hora el
ordenador no podía, se recupera así:

| Método | Dormido a la hora | Apagado a la hora | Sin tu sesión iniciada |
|---|---|---|---|
| desktop | Una ejecución de recuperación al despertar, con la app abierta | Al abrir Claude Desktop | No se ejecuta hasta que abras la app |
| sistema · Mac | Al despertar (launchd junta en una las ejecuciones perdidas) | Al iniciar sesión, si ya pasó la hora | Al iniciar sesión |
| sistema · Linux | En la siguiente hora en punto, hasta 4 horas después de tu hora | 2 minutos después de arrancar | No hace falta sesión |
| sistema · Windows | Lo despierta para ejecutarse (si tu plan de energía permite temporizadores de activación); si no, en cuanto se pueda | Al iniciar sesión o en cuanto se pueda | Al iniciar sesión |
| nube | No depende de tu ordenador | No depende de tu ordenador | No depende de tu ordenador |

Un brief recuperado a mediodía mira los mismos datos (ayer completo y la señal de las últimas horas): sigue valiendo.
Un día que se pierde entero no se recupera al día siguiente; el brief de ese día ya cuenta los cambios desde el último
brief que se hizo.

---

## 8. Dónde mirar y cómo ver el estado

| Archivo | Qué tiene |
|---|---|
| `logs/notificaciones.jsonl` | Una línea por envío: fecha, canal, archivo, si salió bien y el motivo si no. Nunca el contenido ni las claves |
| `logs/brief-diario-AAAA-MM.log` | Método sistema: lo que hizo cada ejecución, de principio a fin |
| `logs/brief-diario-launchd.log` | Solo Mac: errores antes de que arranque el brief (p. ej. «Operation not permitted») |
| `logs/brief-diario.ultimo` | Fecha del último intento (o `forzar` si lo lanzaste con «probar») |
| `informes/diario/AAAA-MM-DD-aviso.md` | El aviso de fallo, si lo hubo |

Estado de la tarea:

- desktop: la ficha de la tarea en **Scheduled** (historial de ejecuciones);
- Mac: `bash .claude/skills/brief-diario/programacion/instalar-mac.sh --estado`;
- Linux: `bash .claude/skills/brief-diario/programacion/instalar-linux.sh --estado`;
- Windows: `... instalar-windows.ps1 -Estado` (con el mismo `powershell -NoProfile -ExecutionPolicy Bypass -File`);
- nube: las sesiones de la rutina en `claude.ai/code/routines`.

---

## 9. Solución de problemas

### Lo primero

1. ¿Hay una línea de hoy en `logs/notificaciones.jsonl`?
   - Sí, con `"ok": true` → el mensaje salió: el problema está en el canal (chat equivocado, spam, canal de Slack).
   - Sí, con `"ok": false` → el `detalle` dice por qué.
   - No → la tarea no se ejecutó o se cortó antes de enviar: mira el estado de la tarea (§8) y el final del registro.
2. Lanza `/brief-diario probar` contigo delante: verás en qué paso falla.
3. `/doctor` revisa la instalación y las conexiones.

### Envío

`notificar.py` sale con **2** cuando falta configurar algo (te dice qué variable, nunca su valor) y con **1** cuando el
envío falló (red, o el servicio lo rechazó).

| Síntoma | Causa | Arreglo |
|---|---|---|
| «Falta TELEGRAM_BOT_TOKEN» (o `TELEGRAM_CHAT_ID`, `SLACK_WEBHOOK_URL`, `SMTP_...`) | La línea no está en `.env` o tiene un espacio o comillas de más | Revisa la línea en `.env`: `NOMBRE=valor`, sin espacios alrededor del `=` |
| «No hay canal configurado» | Ni `brief.canal` en las preferencias ni credenciales completas de ningún canal | `/brief-diario programar` |
| Telegram: «el bot aún no tiene mensajes» | No le has escrito, o hace más de 24 horas (Telegram solo guarda los mensajes pendientes un día) | Escríbele otra vez y repite `telegram-chat-id` |
| Telegram: «webhook activo» | Ese bot se usa en otra herramienta con webhook | Crea con @BotFather un bot nuevo solo para el brief |
| Telegram: token no válido | Token mal copiado o revocado | Cópialo otra vez de @BotFather (`/mybots` → el bot → *API Token*) |
| Telegram: «chat not found» o «bot was blocked» | No pulsaste **Iniciar**, bloqueaste el bot o lo sacaron del grupo | Abre el bot, pulsa **Iniciar** (o vuelve a añadirlo al grupo) |
| Telegram: «el grupo pasó a supergrupo» | Al cambiar ajustes del grupo, Telegram lo convierte en supergrupo y su chat_id cambia | El mensaje trae el número nuevo: cámbialo tú en `TELEGRAM_CHAT_ID` de `.env` (`--guardar` nunca sobrescribe) |
| Llega en varios mensajes `(1/3)` | Muchos clientes: Telegram corta a 4096 caracteres | Normal |
| Email: error de autenticación | Contraseña normal en lugar de contraseña de aplicación, o SMTP desactivado (Microsoft 365) | Contraseña de aplicación; en Microsoft 365, pide al administrador que active el SMTP autenticado para tu buzón o usa otro canal |
| Email: la prueba dice «enviado» pero no llega | Spam | Márcalo como «no es spam» o añade el remitente a contactos |
| Slack: webhook revocado o no encontrado | La app se desinstaló o el canal se borró o archivó | Crea un webhook nuevo y cambia `SLACK_WEBHOOK_URL` |
| «El archivo parece contener una clave» | El informe trae algo con forma de token y el envío se bloquea para no filtrarlo | Abre el archivo que dice, quita la clave y revoca esa clave |

### Datos

| Síntoma | Causa | Arreglo |
|---|---|---|
| Todos los clientes ⚪ «sin acceso a Meta» | La sesión del MCP de Meta caducó o nunca se aprobó la conexión `meta-ads` de la carpeta | Abre Claude Code en la carpeta → `/mcp` → `meta-ads` → inicia sesión (o `/conectar meta`). Sin nadie delante no se puede iniciar sesión |
| Un cliente ⚪ con «ficha» en el motivo | La ficha no se lee o le falta `meta.cuenta` | Abre `clientes/<slug>/ficha.md` con Claude y complétala; el motivo del informe dice qué falta |
| «sin dato (falta credencial…)» en GHL o Stripe | Falta el token de solo lectura del cliente en `.env` | `docs/guias/ghl-meta.md` §1 o `/conectar stripe` |
| Un cliente siempre 🟡 por algo normal | La regla no sabe lo que tú sabes (gasto bajo a propósito, campaña de temporada) | Díselo a Claude para anotarlo en la ficha |
| Un cliente que no quieres no aparece, o al revés | `brief.clientes` en `contexto/preferencias.md`, o el `estado` de la ficha (solo entran los `activo`) | Ajusta la lista o el estado |

### Desktop

| Síntoma | Causa | Arreglo |
|---|---|---|
| La ejecución se queda «en curso» y no llega nada | Está esperando a que aceptes un permiso | Abre la tarea y responde (§5, paso 6). Si es escribir el informe, pon *Accept edits* |
| No se ejecutó | App cerrada u ordenador dormido | **Keep computer awake**; la recuperación sale al abrir la app |
| El informe no está en tu carpeta | La tarea tiene **Worktree** activado | Desactívalo |

### Sistema

| Síntoma | Causa | Arreglo |
|---|---|---|
| Mac: «Operation not permitted» en `logs/brief-diario-launchd.log` | La carpeta está en Escritorio, Documentos, Descargas o iCloud Drive | Muévela (p. ej. a `~/meta-ads-os`) y vuelve a ejecutar `instalar-mac.sh 08:00`. Dar «Acceso total al disco» a `/bin/bash` también lo arregla, pero se lo da a cualquier script: no lo recomendamos |
| «login», «not logged in» o «authentication» en el registro | La ejecución sin nadie no encuentra tu sesión de Claude | `claude setup-token` en tu terminal → `CLAUDE_CODE_OAUTH_TOKEN=...` en `.env` (§5) |
| Funcionaba y deja de funcionar al cabo de un año | Caducó `CLAUDE_CODE_OAUTH_TOKEN` | Genera otro con `claude setup-token` y cámbialo en `.env` |
| «No encuentro el ejecutable de claude» | Claude Code se reinstaló en otra ruta | Vuelve a ejecutar el instalador con tu hora desde una terminal donde `claude` funcione |
| El registro corta con «código 143» | El brief pasó de 30 minutos y se cortó | Muchos clientes o Meta muy lento: prueba a mano y, si es lo normal, sube `BRIEF_TIEMPO_MAX` (segundos) |
| Linux: nunca se ejecuta | cron no está instalado o no está en marcha | `sudo apt install cron` (o lo de tu distribución) y comprueba con `--estado` que están las líneas |
| Windows: «la ejecución de scripts está deshabilitada» | Política de PowerShell | Lanza los scripts siempre con `powershell -NoProfile -ExecutionPolicy Bypass -File ...`, como en la tabla de §5 |
| Windows: no encuentra Python | Solo tienes el acceso directo de la Microsoft Store | Instala Python desde python.org y vuelve a ejecutar el instalador |
| Llegan dos briefs | Dos métodos programados a la vez | Quita uno (§10) |
| Tras actualizar Claude Code, el registro dice que no conoce `/brief-diario` o no hay herramientas de Meta | Anthropic ha anunciado que el modo `--bare` (sin skills, hooks ni MCP del proyecto) será el predeterminado de `claude -p` | Actualiza Meta Ads OS (`/actualizar`); mientras tanto, usa el método desktop |

### Nube

| Síntoma | Causa | Arreglo |
|---|---|---|
| La rutina no puede enviar | `api.telegram.org` (o `hooks.slack.com`) no está en *Allowed domains* del entorno | Edita el entorno: *Network access* → *Custom* → añade el dominio |
| «sin acceso a Meta» | El conector de Meta no está añadido o no está marcado en la rutina | Añádelo en `claude.ai/customize/connectors` y márcalo en la rutina |
| Faltan evaluaciones o «qué no tocar» | Es el modo ligero: la nube no ve tus fichas ni tu change log | Normal. Si los necesitas, usa desktop o sistema |

---

## 10. Cambiar o quitar el brief

- **Cambiar hora, canal o clientes**: `/brief-diario programar` y elige qué cambiar. Con el método sistema puedes
  también volver a ejecutar el instalador con la hora nueva: sustituye la tarea anterior.
- **Pausar unos días**: en `contexto/preferencias.md`, `canal: ninguno`. El brief se sigue generando y guardando,
  pero no se envía.
- **Quitarlo**: `/brief-diario programar` → desprogramar. Te dice exactamente qué va a quitar y te pide que lo
  confirmes por escrito:
  - desktop: pausas o borras la tarea en **Scheduled**;
  - Mac: `instalar-mac.sh --quitar` (descarga la tarea y borra su archivo de `~/Library/LaunchAgents`);
  - Linux: `instalar-linux.sh --quitar` (quita solo las líneas del brief del crontab);
  - Windows: `instalar-windows.ps1 -Quitar` (quita la tarea del Programador de tareas);
  - nube: pausas o borras la rutina en `claude.ai/code/routines`.

Los informes que ya se guardaron no se tocan.

---

## 11. Seguridad y privacidad

- El brief **solo lee**. Con el método sistema, la lista de lo que puede hacer está cerrada y lo demás se deniega sin
  preguntar. Además, las reglas de `.claude/settings.json` bloquean escrituras en Meta sin tu confirmación y la lectura
  de `.env`.
- **Claves**: `TELEGRAM_BOT_TOKEN`, `SLACK_WEBHOOK_URL`, `SMTP_CLAVE` y `CLAUDE_CODE_OAUTH_TOKEN` van solo en `.env`. Si
  alguna acaba en un chat, un correo o un repositorio, revócala y crea otra: en Telegram, @BotFather → `/revoke`; en
  Slack, borra el webhook; en tu correo, borra la contraseña de aplicación.
- **Qué viaja**: nombres de tus clientes, cifras de gasto y resultados, e IDs de Meta. Nunca datos de leads. Los chats
  con bots de Telegram no van cifrados de extremo a extremo: si tus contratos con clientes no permiten que esa
  información pase por Telegram, usa el email de tu empresa o el Slack de tu equipo.
- **Solo a ti**: el brief se envía al canal que tú configuras. No lo configures para enviarlo a un cliente: para eso
  está `/informe-cliente`.
