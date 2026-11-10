---
name: doctor
description: "Diagnostica la instalación y las conexiones de Meta Ads OS en Mac, Linux o Windows (Git Bash): Python, uv, git, FFmpeg, Claude Code, MCP de Meta, GHL y Stripe, contexto, fichas, permisos de .env, hooks y módulos de vídeo, y explica cada fallo con su arreglo concreto. Úsala si algo falla o tras actualizar."
argument-hint: "[rapido]"
---

# /doctor

Solo lectura salvo los arreglos seguros que el usuario apruebe. `rapido` se salta las pruebas de conexión en vivo.

## Pasos

1. **Entorno.** `python3 -I herramientas/doctor.py --json` (en Windows, si `python3` no existe: `python` o `py -3`;
   si no hay ninguno, el arreglo es instalar Python 3.10+ y reabrir la terminal). Devuelve una lista
   `{id, ok, detalle, arreglo}`. Código de salida 2 = configuración rota: sigue igualmente con lo que puedas leer.
2. **Hooks.** Con Glob, comprueba que existen los 10 de `.claude/hooks/` (`meta_guard`, `motor_guard`, `ghl_guard`,
   `stripe_guard`, `eventos_guard`, `control_publicacion`, `datos_personales`, `secretos`, `registro_obligatorio`,
   `contexto_sesion`) y, con Grep, que `.claude/settings.json` los referencia. Si falta alguno, es un fallo crítico:
   sin guardas no se trabaja en cuentas reales.
3. **Instalación.** Lee `contexto/instalacion.json`: fases requeridas pendientes → «`/empezar` lo retoma».
4. **Conexiones en vivo** (lecturas sin coste; sáltalo con `rapido`):
   - **Meta**: `ads_get_ad_accounts`. Error de autenticación → `/conectar meta`. Lista vacía → el usuario autenticado
     no tiene acceso a cuentas (si es agencia, falta el acceso de partner → `/configurar-meta <cliente> agencia`).
   - **GHL**: si hay herramientas `mcp__ghl__*`, una lectura mínima que no devuelva datos personales (describir una
     operación o listar pipelines). Si no aparecen pero el usuario usa GHL → `/conectar ghl`.
   - **Stripe**: si hay herramientas `mcp__stripe__*`, una lectura sin datos personales (la cuenta o el saldo).
   - **Nombres de las herramientas del MCP de Meta.** Con Grep, saca los `mcp__meta-ads__*` de las líneas `tools:` de
     `.claude/agents/*.md` y de los `allowed-tools` de `.claude/skills/*/SKILL.md`, y compáralos con las herramientas que
     expone el servidor conectado (las que tienes cargadas o las que lista `/mcp` → `meta-ads`). Un nombre que el
     servidor no expone no se carga en el subagente, sin error visible: lístalo con el agente o la skill que lo usa y
     propón `/actualizar` (o anotarlo para `curador-conocimiento`). No edites agentes ni `settings.json` desde aquí.
     Lo mismo con `mcp__ghl__*` y `mcp__stripe__*` si esos servidores están conectados.
   - **Token avanzado**: si alguna ficha lo usa, `python3 -I herramientas/meta_ads.py cuentas --cliente <slug>`.
   - **Motor de vídeo**: si existe `modulos/motor-ia/.venv`, `MOTOR_MOCK=1 uv run --project modulos/motor-ia motor status`
     (no gasta). Si no existe y quiere vídeo con IA → `/motor instalar`.
   - **cutkit**: si existe `modulos/cutkit/.venv`, `uv run --project modulos/cutkit ck --help`.
5. **Informe.**
   - Tabla `Estado | Comprobación | Detalle | Arreglo`, críticos primero (ids de `doctor.py`: `python`, `uv`, `git`,
     `claude`, `mcp_json`, `settings`, `contexto`, `env`, `logs`, `clientes`, más los hooks del paso 2), después
     `instalacion`, las conexiones y los nombres de herramientas que no existen en el servidor, y al final lo opcional (`ffmpeg`, `motor_ia`, `cutkit`: `doctor.py` los da por
     buenos si no están instalados y dice cómo instalarlos).
   - **Lo que puedo arreglar yo** (con tu OK, uno a uno): crear carpetas de la instancia que falten desde
     `plantillas/`, poner `.env` con permisos 600 (`chmod 600 .env`, sin leerlo), crear `.env` copiando
     `plantillas/env.ejemplo` si no existe, `uv sync --project modulos/motor-ia` si el entorno del motor está roto.
   - **Lo que tienes que hacer tú**: instalar software (con el comando para tu sistema), autenticarte por OAuth en
     `/mcp`, pegar claves en `.env`, reiniciar Claude Code tras añadir un MCP o cambiar `settings.json`.
6. Si todo está bien: una línea («Todo en orden») y la fecha.

## Lo que nunca hace
- Leer, imprimir o copiar `.env` (solo se comprueban sus permisos y si existe).
- Borrar nada, ni «arreglar» algo desactivando hooks o relajando permisos de `.claude/settings.json`: si una guarda
  molesta, se explica por qué existe.
- Escribir en Meta, GHL o Stripe.

## Notas por sistema
- **Windows**: todo va por Git Bash. Rutas con `/`. Si un comando falla con `python3`, prueba `python`.
- **Mac**: si falta FFmpeg, `brew install ffmpeg`; si falta uv, el instalador oficial de uv.
- **Linux**: FFmpeg con el gestor de paquetes de la distribución.
