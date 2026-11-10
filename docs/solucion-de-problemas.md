# Solución de problemas

Antes de nada, escribe `/doctor` en Claude Code: revisa la instalación y las conexiones y te da el arreglo concreto de
cada fallo para tu sistema. Si el problema es de la instalación, `bash scripts/instalar.sh` se puede repetir siempre:
repara sin pisar nada.

## Instalación

### «No encuentro Python 3» o `python3` abre la Microsoft Store

En Windows, el `python3` que viene con el sistema es un atajo a la Microsoft Store, no Python. Instala Python desde
[python.org](https://www.python.org/downloads/) y marca **«Add python.exe to PATH»** en el instalador (o, en
PowerShell, `winget install -e --id Python.Python.3.12`). Cierra y vuelve a abrir Git Bash y Claude Code. El
instalador y los hooks prueban `python3`, `python` y `py -3`, así que cualquiera de los tres sirve.

### «No encuentro uv» justo después de instalarlo

El instalador de uv lo deja en `~/.local/bin`, que tu terminal aún no conoce. Cierra y vuelve a abrir la terminal (y
Claude Code) y repite `bash scripts/instalar.sh`. También puedes dejar que lo instale el propio instalador:
`bash scripts/instalar.sh --instalar-uv`.

### Aviso de OneDrive, iCloud, Dropbox o Google Drive

La sincronización de esas carpetas choca con git y con los entornos de Python de los módulos de vídeo (archivos
bloqueados, duplicados «en conflicto»). Clona el proyecto en una carpeta normal de tu usuario y copia allí tu instancia
como se explica en [Si descargaste un ZIP](primeros-pasos.md#si-descargaste-un-zip) (los pasos son los mismos).

### `$'\r': command not found` al ejecutar un script

El script tiene finales de línea de Windows (CRLF). El repositorio fija los de Unix con `.gitattributes`, así que con un
clon normal no pasa; suele venir de una descarga en ZIP, de una copia anterior o de un editor que guardó el archivo con
CRLF. Vuelve a clonar y copia tu instancia a la carpeta nueva como en
[Si descargaste un ZIP](primeros-pasos.md#si-descargaste-un-zip):

```bash
git clone --config core.autocrlf=false https://github.com/ai-agency-accelerator/Meta-Ads-OS.git meta-ads-os-nuevo
```

Si solo es un archivo que has editado tú, vuelve a guardarlo con finales de línea LF (en VS Code, abajo a la derecha:
«CRLF» → «LF»).

### `bash: scripts/instalar.sh: No such file or directory`

Estás en otra carpeta. Entra primero en la del proyecto (`cd ~/meta-ads-os`) y repite.

### «contexto/instalacion.json estaba dañado»

Alguien lo editó a mano y quedó con un error. El instalador ya ha guardado una copia
(`contexto/instalacion.json.danado-<fecha>`) y lo ha rehecho; `/empezar` retoma desde lo que pueda comprobar.

## Claude Code

### `/empezar` (o cualquier skill) no aparece

Claude Code tiene que estar abierto **en la carpeta del proyecto**, no en una superior. Comprueba también que
aceptaste confiar en la carpeta: sin eso no carga la configuración del proyecto. Cierra Claude Code, ábrelo en
`meta-ads-os` y vuelve a probar.

### Los hooks no se ejecutan

Si no ves el resumen de seis líneas al abrir la sesión, o `/doctor` dice que los hooks no arrancan:

1. Comprueba que confiaste en la carpeta del proyecto (sin eso, Claude Code no ejecuta sus hooks).
2. Escribe `/hooks` en Claude Code: deberían aparecer los del proyecto.
3. En una terminal (en Windows, Git Bash), desde la carpeta del proyecto: `python3 --version`, `python --version` y
   `py -3 --version`. Para los hooks basta con que uno dé 3.8 o superior; las herramientas piden 3.10. Si ninguno,
   instala Python como arriba.
4. Mira `logs/hooks.jsonl`: cada fallo interno de un hook deja ahí una línea con `"decision": "error"` y su traza
   (`/doctor` la resume).
5. Reinicia Claude Code después de cualquier cambio.

### Una guarda me pide confirmación o me bloquea

Es su trabajo: lee el motivo que da. Las más habituales:

| Mensaje | Por qué | Qué hacer |
|---|---|---|
| El presupuesto supera el tope por cambio | `meta_guard` compara con `topes.cambio_dia` de la ficha | Si el tope se ha quedado corto, súbelo en la ficha con criterio (`/escalar`) |
| La entidad cambió hace menos de 7 días | Regla de paciencia | Espera a que madure el cambio anterior salvo que algo esté roto |
| El nombre no cumple la nomenclatura | `control_publicacion` | Usa el nombre que te propone: sin él, el registro creativo no sabe qué ganó |
| Falta el veredicto de políticas | `control_publicacion` | `/revisar-anuncio` sobre la carpeta de la pieza |
| Envío a la Conversions API sin `test_event_code` | `eventos_guard` | Añade el código de prueba de Events Manager |
| Emails o teléfonos fuera de `privado/` | `datos_personales` | Guarda ese archivo en `clientes/<slug>/privado/` o usa agregados |

## Conexiones

### El MCP de Meta no aparece o no se autentica

Escribe `/mcp`: debería aparecer `meta-ads`. Si no está aprobado, apruébalo; si está pero sin autenticar, *Authenticate*
e inicia sesión con la persona que tiene acceso a las cuentas publicitarias. Si Meta te pide una app propia, `/conectar
meta` te guía para crearla y añadir el servidor con su ID.

### La lista de cuentas sale vacía

La persona con la que iniciaste sesión no tiene acceso a ninguna cuenta publicitaria. En una agencia, casi siempre es
que falta el acceso de partner a la cuenta del cliente: `/configurar-meta <cliente> agencia`.

### GoHighLevel o Stripe no aparecen después de `/conectar`

Un servidor MCP nuevo solo se carga al reiniciar Claude Code. Ciérralo, ábrelo de nuevo en la carpeta del proyecto,
autentica en `/mcp` y, si venías de `/empezar`, escribe `/empezar` para seguir donde estabas.

### Una herramienta dice que falta una variable

La variable no está en `.env` o está comentada. Ábrelo con tu editor ([cómo](conexiones.md#el-archivo-env)), quita la
`#` del principio y comprueba el nombre: por cliente es `<VARIABLE>_<SLUG>` con el slug en mayúsculas y guiones bajos
(`GHL_TOKEN_CLINICA_SONRISA` para `clinica-sonrisa`).

### El brief diario no llega

`python3 -I herramientas/notificar.py probar` manda un mensaje de prueba al canal de tus preferencias y dice qué falla.
Para Telegram, recuerda escribir primero a tu bot. La [guía del brief](guias/brief-diario.md) cubre cada canal y cada
forma de programarlo.

## Actualizar

### /actualizar dice que has modificado archivos

Has editado archivos del producto (una skill, un agente, `CLAUDE.md`…) y actualizar los pisaría. Tus datos no cuentan:
git no los ve. Dos opciones, ninguna borra nada:

- **Guardarlos aparte, actualizar y recuperarlos:**
  ```bash
  git stash push -m mis-cambios && bash scripts/actualizar.sh && git stash pop
  ```
  Si al recuperarlos alguno choca con la versión nueva, git te lo dice y tus cambios siguen guardados en `git stash
  list` hasta que lo resuelvas.
- **Mover tus personalizaciones** a donde no chocan: tus reglas a `contexto/operador.md` → «Reglas propias»; tus
  permisos a `.claude/settings.local.json`. Después, `git stash push -m mis-cambios` para apartar las ediciones
  originales y actualiza.

### Tu copia tiene commits propios

Has hecho commits en esta carpeta, así que tu historia y la del repositorio se han separado y no se puede avanzar en
línea recta. Guarda tus commits en una rama y alinea la tuya con la del repositorio:

```bash
git branch mis-cambios
git reset --keep @{u}
bash scripts/actualizar.sh
```

Tus commits siguen en la rama `mis-cambios` (`git log mis-cambios` para verlos) y puedes recuperar lo que necesites.
`--keep` se niega a seguir si eso pisara algún cambio sin guardar.

### Una migración ha fallado

`/actualizar` se para en la migración que falla y te enseña el error. Lo que esa migración iba a cambiar está copiado
en `logs/copias-migracion/<fecha>_<migración>/` y las siguientes no se han aplicado. Copia el mensaje en Claude Code
para que te ayude a ver qué dato tiene un formato inesperado; cuando lo arregles, `bash scripts/actualizar.sh` la
vuelve a intentar.

### Algo dejó de funcionar después de actualizar

Primero `/doctor`. Si cambiaron `.claude/settings.json`, los hooks o `.mcp.json`, reinicia Claude Code. Si un módulo de
vídeo cambió de dependencias: `uv sync --project modulos/motor-ia` (o `modulos/cutkit`). Si aun así necesitas volver a
la versión anterior, pídeselo a `/actualizar`: apuntó la versión de partida y te lo propone con tu confirmación.

## Vídeo

### «No encuentro FFmpeg»

Solo hace falta para montar o editar vídeo. Mac: `brew install ffmpeg`. Windows (PowerShell):
`winget install -e --id Gyan.FFmpeg` y vuelve a abrir Git Bash. Linux: `sudo apt install ffmpeg`.

### El motor dice que no queda presupuesto

El guardián del motor se ha parado en tu tope (5 $ por defecto). Si quieres seguir, súbelo en la cabecera de
`contexto/preferencias.md` (`motor.presupuesto_usd`) o con `MOTOR_PRESUPUESTO_USD` en `.env`, y consulta `/motor`
antes de producir más.

## Clientes

### Un cliente no sale en `/hoy` ni en el brief

En `/hoy` salen todos los clientes con ficha salvo los que tienen `estado: pausa` (los `prospecto`, en una línea al
final). En el brief, solo los `activo`. Si el estado es el correcto, su ficha puede tener un error en la cabecera:
`/doctor` dice qué campo arreglar.

### «FichaInvalida»

La cabecera YAML de `clientes/<slug>/ficha.md` falta o tiene un campo mal escrito. El mensaje dice cuál. Compárala con
`plantillas/cliente/ficha.md` o pide a Claude que la revise con `/cliente-nuevo`.
