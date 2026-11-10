# Primeros pasos

De cero a tu primer cliente situado en una fase y con un entregable útil, en unos 30 minutos.

## 1. Lo que necesitas

| Qué | Cómo saber si lo tienes | Notas |
|---|---|---|
| Claude Code con plan **Pro o superior** | Inicia sesión en Claude Code con tu cuenta de Claude (`/login`) | En la terminal o en la app de escritorio |
| Git | `git --version` | En Windows, [Git para Windows](https://git-scm.com/download/win): trae **Git Bash**, que también usa Claude Code |
| Python 3.10 o superior | `python3 --version` (en Windows, `python --version` o `py -3 --version`) | No uses el Python de la Microsoft Store |
| [uv](https://docs.astral.sh/uv/) | `uv --version` | Gestiona los entornos de los módulos de vídeo y de las herramientas que lo necesitan |
| FFmpeg | `ffmpeg -version` | Opcional: solo para montar o editar vídeo |
| Una cuenta de Meta Business con una cuenta publicitaria | — | Opcional para instalar. Si empiezas de cero, `/configurar-meta` te guía |

No te preocupes si te falta algo: el instalador lo detecta y te da la orden exacta para tu sistema.

**Dónde ponerlo.** En una carpeta normal de tu usuario, por ejemplo `~/meta-ads-os` en Mac y Linux o
`C:\Users\<tu usuario>\meta-ads-os` en Windows. **No** dentro de OneDrive, iCloud Drive, Dropbox ni Google Drive: la
sincronización choca con git y con los entornos de Python, y el instalador te avisará si lo detecta.

## 2. Instalar

### Mac y Linux

```bash
cd ~
git clone https://github.com/ai-agency-accelerator/Meta-Ads-OS.git meta-ads-os
```

Después abre Claude Code en la carpeta `meta-ads-os` (en la
terminal: `cd meta-ads-os && claude`) y escribe `/empezar`.

### Windows

1. Instala [Git para Windows](https://git-scm.com/download/win) con las opciones por defecto.
2. Abre **Git Bash** (búscalo en el menú Inicio) y ejecuta:
   ```bash
   cd ~
   git clone https://github.com/ai-agency-accelerator/Meta-Ads-OS.git meta-ads-os
   ```
3. Abre Claude Code en la carpeta `meta-ads-os` y escribe `/empezar`.

Todas las órdenes `bash scripts/...` de esta documentación se ejecutan desde Git Bash, nunca desde cmd ni PowerShell.
Si Python no aparece después de instalarlo, cierra y vuelve a abrir Git Bash y Claude Code para que lean el `PATH`
nuevo.

### La primera vez que abres la carpeta en Claude Code

Te hará dos preguntas. Responde que sí a las dos:

- **Confiar en la carpeta.** Activa la configuración del proyecto: permisos, guardas de seguridad y estilos.
- **Aprobar el servidor MCP `meta-ads`.** Es el conector oficial de Meta (`https://mcp.facebook.com/ads`). Aprobarlo no
  da acceso a nada todavía: el acceso lo das tú al iniciar sesión con Meta en `/conectar meta`.

### Qué hace el instalador

`/empezar` lo ejecuta por ti. Si prefieres lanzarlo a mano, desde la carpeta del proyecto:

```bash
bash scripts/instalar.sh
```

1. **Requisitos.** Comprueba Python, git, uv, FFmpeg y Claude Code. Si falta algo obligatorio, se para sin escribir
   nada y te dice cómo instalarlo.
2. **Tu espacio de trabajo.** Crea `contexto/` (desde `plantillas/contexto/`), `clientes/`, `aprendizajes/`, `logs/` e
   `informes/diario/`, y copia `plantillas/env.ejemplo` a `.env` con permisos 600. Lo que ya existe no lo toca.
3. **Comprobación final.** Registra la fase técnica en `contexto/instalacion.json` y prueba una herramienta.

| Opción | Para qué |
|---|---|
| `--comprobar` | Solo revisa los requisitos; no escribe nada |
| `--instalar-uv` | Instala uv con su instalador oficial si no lo tienes (necesita red) |
| `--ayuda` | Muestra la ayuda |

Cada línea de la salida empieza por `[OK]`, `[AVISO]` (sigue, con una limitación), `[ERROR]` (bloquea) o `[INFO]`, y
la última dice `RESULTADO: listo` o `RESULTADO: faltan requisitos`. Puedes repetirlo siempre que quieras: sirve
también para reparar una instalación.

### Si descargaste un ZIP

Sin git, `/actualizar` no puede traer versiones nuevas. Pásate a un clon sin perder nada:

1. Clona el repositorio en una carpeta **nueva**, por ejemplo `meta-ads-os-git` (sección 2).
2. Con el explorador de archivos, copia de la carpeta antigua a la nueva las carpetas que existan de tu instancia:
   `contexto/`, `clientes/`, `aprendizajes/` e `informes/`, y el archivo `.env` (es oculto: en Mac, `Cmd+Mayús+.` los
   muestra; en Windows, «Vista → Elementos ocultos»).
3. En la carpeta nueva, ejecuta `bash scripts/instalar.sh` y después `/doctor` en Claude Code.
4. Cuando compruebes que todo está, puedes archivar la carpeta antigua. No la borres hasta entonces.

## 3. `/empezar`

Es una conversación, una pregunta cada vez. Guarda al cerrar cada paso, así que puedes parar cuando quieras y
retomarla escribiendo `/empezar` otra vez: sigue donde lo dejaste.

| Paso | Qué te pregunta o hace | Dónde lo guarda |
|---|---|---|
| Técnica | Instalador y `/doctor` | `contexto/instalacion.json` |
| Perfil | Tu empresa (sin datos de contacto), si eres agencia, consultora, SaaS o negocio, para qué lo usas, tu nivel y tu stack | `contexto/operador.md` y la cabecera de `contexto/preferencias.md` |
| Meta | Si tienes portfolio y cuenta publicitaria; si sí, `/conectar meta` | — |
| Integraciones | GoHighLevel y Stripe si los usas (opcional; añadir un MCP obliga a reiniciar Claude Code) | — |
| Primer cliente | `/cliente-nuevo` en modo rápido: tu negocio o el de un cliente | `clientes/<slug>/ficha.md` y `estado.md` |
| Primer entregable | Uno, según su situación (abajo) | Carpeta del cliente |

| Situación | Tu primer entregable |
|---|---|
| No sabes cuánto puedes pagar por un cliente | Break-even y target por etapa con `/economia`, en la ficha |
| Sabes tu economía pero no tienes cuenta, o no tiene señal | Plan de configuración de Meta para tu situación |
| Ya hay gasto en la cuenta | Foto inicial: 4 semanas por campaña, coste por resultado frente al break-even, 3 hallazgos y qué no tocar todavía |
| Eres agencia y aún no tienes acceso a la cuenta del cliente | El mensaje para pedir acceso como partner y la checklist |

Al terminar te dice qué ha quedado hecho, dónde está y **un** siguiente paso. Con `/empezar reiniciar` vuelve a
preguntar perfil, cliente y entregable; no borra nada: te enseña lo que hay y te pregunta qué cambiar.

**Claves y tokens nunca en el chat.** Cuando haga falta una clave, la pegas tú en `.env` con tu editor. Si alguna vez
pegas una en el chat, revócala y crea otra (ver [Seguridad](seguridad.md#si-se-filtra-una-clave)).

## 4. Después de `/empezar`

| Cuándo | Qué |
|---|---|
| Cada día | `/hoy` (qué toca en cada cliente) y, si la programaste, el brief en tu móvil |
| Cuando tengas una duda de Meta | `/pregunta "¿cuánto tarda en salir de aprendizaje un conjunto?"` |
| Cuando no sepas qué existe | `/menu` o `/menu F3` |
| Para elegir cómo te habla | `/config` → estilo de salida → `profesor` (explica el porqué y enlaza la base) u `operador` (directo). Para dejarlo fijo: [estilos de salida](catalogo/agentes.md#estilos-de-salida-2) |
| Para el brief diario | `/brief-diario programar` ([guía](guias/brief-diario.md)) |
| Para vídeo con IA | `/motor instalar` ([guía](guias/video-ia.md)) |
| Para subir vídeos desde el sistema | `/conectar meta --avanzado` ([guía](guias/token-avanzado.md)) |
| Si algo falla | `/doctor` |

El recorrido completo de un cliente está en [Recorrido por fases](recorrido.md).

## 5. Actualizar

```
/actualizar
```

Te enseña qué trae la versión nueva antes de tocar nada, actualiza con `git pull --ff-only`, aplica las migraciones de
datos que declare esa versión (copiando antes lo que cambian a `logs/copias-migracion/`) y pasa `/doctor`. Para ver
solo si hay versión nueva: `/actualizar comprobar` o `bash scripts/actualizar.sh --comprobar`.

Nunca toca tu instancia salvo esas migraciones. Si has editado archivos del producto, se para y te explica cómo
guardarlos aparte: [solución de problemas](solucion-de-problemas.md#actualizar-dice-que-has-modificado-archivos).

**Si quieres adaptar algo**, no edites los archivos del producto: tus reglas van en `contexto/operador.md` (apartado
«Reglas propias»), que se carga en cada sesión. Así las actualizaciones nunca chocan con tus cambios.

## 6. Copias de seguridad

Git no guarda tu instancia, así que la copia es cosa tuya:

| Qué copiar | Por qué |
|---|---|
| `clientes/` | Fichas, change logs, registro creativo, informes y creativos de cada cliente |
| `contexto/` | Tu perfil, preferencias y estado de la instalación |
| `aprendizajes/` | Lo que has aprendido en tus cuentas |
| `informes/` | Los briefs diarios globales |

- Una copia periódica de esas carpetas en tu nube o en un repositorio **privado** propio es suficiente. `logs/` es
  opcional (registros de llamadas).
- `clientes/<slug>/privado/` contiene datos personales de leads: si lo copias, que sea a un sitio cifrado y con acceso
  restringido, o déjalo fuera.
- No copies `.env` a ningún sitio compartido: guarda tus claves en un gestor de contraseñas y, si cambias de ordenador,
  vuelve a pegarlas en un `.env` nuevo.
