#!/usr/bin/env bash
# Brief diario sin nadie delante (Mac y Linux). Lo lanzan launchd (instalar-mac.sh) y cron (instalar-linux.sh).
#
#   brief.sh                    ejecuta el brief ahora (prueba manual)
#   brief.sh --si-falta HH:MM   solo si ya es esa hora y hoy aún no se ha intentado (lo usan las tareas programadas,
#                               que lo llaman varias veces para recuperar el brief si el ordenador estaba dormido)
#
# Qué hace:
#   1. Lanza `claude -p "/brief-diario todos"` en modo dontAsk con la lista cerrada de herramientas-permitidas.txt
#      (lecturas, subcomandos de lectura, notificar.py enviar y escribir solo en los informes) y las denegaciones de
#      herramientas-denegadas.txt. Sin nadie delante, cualquier otra cosa se deniega sin preguntar.
#   2. Si el resumen de hoy no consta como enviado en logs/notificaciones.jsonl, manda un aviso corto con notificar.py
#      para que sepas que hoy no hay brief y dónde mirar.
#
# Registro: logs/brief-diario-AAAA-MM.log. Último intento: logs/brief-diario.ultimo (fecha, o «forzar» para --probar).
# Variables opcionales (las pone el instalador): CLAUDE_BIN, PYTHON_BIN, BRIEF_MODELO (sonnet),
# BRIEF_TIEMPO_MAX (segundos, 1800). En .env, opcional: CLAUDE_CODE_OAUTH_TOKEN (de `claude setup-token`), solo si
# la ejecución programada no encuentra tu sesión. Este script nunca lo imprime.
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$DIR/../../../.." && pwd)"
cd "$RAIZ" || exit 2

# launchd y cron no cargan tu shell: rutas habituales de claude y python3
export PATH="$HOME/.local/bin:$HOME/.claude/local:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin${PATH:+:$PATH}"

HOY="$(date +%Y-%m-%d)"
MES="$(date +%Y-%m)"
mkdir -p logs informes/diario
LOG="logs/brief-diario-$MES.log"
MARCA="logs/brief-diario.ultimo"
anotar() { printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

if [ "${1:-}" = "--si-falta" ]; then
  HORA="${2:-08:00}"
  if ! [[ "$HORA" =~ ^([01][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
    anotar "hora no válida: $HORA (usa HH:MM)"
    exit 1
  fi
  ULTIMO="$(tr -d '[:space:]' < "$MARCA" 2>/dev/null || true)"
  if [ "$ULTIMO" != "forzar" ]; then
    [ "$ULTIMO" = "$HOY" ] && exit 0                                   # hoy ya se intentó
    [ "$((10#$(date +%H%M)))" -lt "$((10#${HORA/:/}))" ] && exit 0     # aún no es la hora
  fi
fi
printf '%s\n' "$HOY" > "$MARCA"

CLAUDE="${CLAUDE_BIN:-$(command -v claude 2>/dev/null || true)}"
PYTHON="${PYTHON_BIN:-$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)}"
[ -n "$PYTHON" ] && export PATH="$(dirname "$PYTHON"):$PATH"   # que `python3` sea el mismo para Claude

# Token de larga duración (opcional): solo la línea CLAUDE_CODE_OAUTH_TOKEN de .env, sin mostrarla
if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && [ -f .env ]; then
  TOKEN="$(grep -E '^[[:space:]]*CLAUDE_CODE_OAUTH_TOKEN[[:space:]]*=' .env | tail -n 1 | cut -d= -f2- | tr -d '\r' \
           | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'$/\1/")"
  if [ -n "$TOKEN" ]; then
    export CLAUDE_CODE_OAUTH_TOKEN="$TOKEN"
    unset ANTHROPIC_API_KEY   # en -p, una clave de API presente tendría prioridad sobre el token
  fi
  unset TOKEN
fi

leer_lista() { grep -v -E '^[[:space:]]*(#|$)' "$1" | tr -d '\r' | sed -e 's/[[:space:]]*$//'; }
PERMITIDAS=()
while IFS= read -r regla; do PERMITIDAS+=("$regla"); done < <(leer_lista "$DIR/herramientas-permitidas.txt")
DENEGADAS=()
while IFS= read -r regla; do DENEGADAS+=("$regla"); done < <(leer_lista "$DIR/herramientas-denegadas.txt")

anotar "inicio del brief · claude: ${CLAUDE:-no encontrado} · python: ${PYTHON:-no encontrado}"
CODIGO=0
if [ -z "$CLAUDE" ] || [ ! -x "$CLAUDE" ]; then
  anotar "No encuentro el ejecutable de claude. Vuelve a ejecutar el instalador o pon CLAUDE_BIN con la ruta de \`command -v claude\`."
  CODIGO=127
else
  # El encargo va antes de --allowedTools: ese parámetro admite varios valores seguidos.
  "$CLAUDE" -p "/brief-diario todos" \
    --permission-mode dontAsk \
    --model "${BRIEF_MODELO:-sonnet}" \
    --allowedTools ${PERMITIDAS[@]+"${PERMITIDAS[@]}"} \
    --disallowedTools ${DENEGADAS[@]+"${DENEGADAS[@]}"} \
    < /dev/null >> "$LOG" 2>&1 &
  PID=$!
  # Vigía: corta a claude si se pasa de tiempo. Al terminar claude se le avisa y se lleva su `sleep` consigo
  # (sin descriptores abiertos, para no dejar colgado a quien lea la salida de este script).
  ( sleep "${BRIEF_TIEMPO_MAX:-1800}" & S=$!
    trap 'kill "$S" 2>/dev/null; exit 0' TERM
    wait "$S" && kill -TERM "$PID" 2>/dev/null ) </dev/null >/dev/null 2>&1 &
  VIGIA=$!
  wait "$PID"
  CODIGO=$?
  kill "$VIGIA" 2>/dev/null
  wait "$VIGIA" 2>/dev/null
fi
anotar "fin de claude · código $CODIGO"

# ¿Se envió el resumen de hoy? (notificar.py escribe las claves en este orden)
if grep -qF "\"archivo\": \"informes/diario/$HOY.md\", \"ok\": true" logs/notificaciones.jsonl 2>/dev/null; then
  anotar "brief enviado"
  exit 0
fi

AVISO="informes/diario/$HOY-aviso.md"
{
  printf '# ⚠️ Brief diario · %s · no se ha generado\n\n' "$HOY"
  printf 'La ejecución programada de las %s terminó sin enviar el brief (código %s).\n\n' "$(date +%H:%M)" "$CODIGO"
  printf -- '- Mira el final de `%s`.\n' "$LOG"
  printf -- '- En Claude Code, `/brief-diario probar` lo lanza y enseña qué falla.\n'
  printf -- '- Guía: `docs/guias/brief-diario.md`, apartado «Solución de problemas».\n'
} > "$AVISO"
if [ -n "$PYTHON" ]; then
  "$PYTHON" -I herramientas/notificar.py enviar --archivo "$AVISO" --canal auto >> "$LOG" 2>&1
  anotar "aviso de fallo enviado · código $?"
else
  anotar "no hay python3 para enviar el aviso de fallo"
fi
exit 1
