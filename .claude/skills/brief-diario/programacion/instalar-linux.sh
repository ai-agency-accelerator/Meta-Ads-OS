#!/usr/bin/env bash
# Programa el brief diario en Linux con cron. Lo usa /brief-diario programar (método «sistema»).
#
#   instalar-linux.sh HH:MM     instala o actualiza las líneas del crontab
#   instalar-linux.sh --estado  enseña las líneas instaladas, el último intento y el último envío
#   instalar-linux.sh --quitar  quita solo las líneas del brief del crontab (confírmalo antes)
#
# cron no recupera lo que no ejecutó con el ordenador dormido o apagado. Por eso se instalan dos líneas:
#   - cada hora en punto (al minuto elegido) desde la hora del brief hasta 4 horas después;
#   - al arrancar el ordenador (@reboot), con 2 minutos de margen.
# brief.sh --si-falta hace que solo se ejecute una vez al día y nunca antes de la hora.
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$DIR/../../../.." && pwd)"
INICIO="# >>> meta-ads-os brief-diario >>> (lo gestiona instalar-linux.sh; no edites entre estas marcas)"
FIN="# <<< meta-ads-os brief-diario <<<"

if ! command -v crontab >/dev/null 2>&1; then
  echo "No encuentro crontab. Instala cron (p. ej. sudo apt install cron) o usa el método desktop." >&2
  exit 2
fi

sin_bloque() { crontab -l 2>/dev/null | sed '/^# >>> meta-ads-os brief-diario >>>/,/^# <<< meta-ads-os brief-diario <<</d'; }

case "${1:-}" in
  --estado)
    crontab -l 2>/dev/null | sed -n '/^# >>> meta-ads-os brief-diario >>>/,/^# <<< meta-ads-os brief-diario <<</p'
    echo "Último intento: $(cat "$RAIZ/logs/brief-diario.ultimo" 2>/dev/null || echo 'ninguno')"
    echo "Último envío: $(tail -n 1 "$RAIZ/logs/notificaciones.jsonl" 2>/dev/null || echo 'ninguno')"
    exit 0
    ;;
  --quitar)
    sin_bloque | crontab -
    echo "Líneas del brief quitadas del crontab."
    exit 0
    ;;
esac

HORA="${1:-}"
if ! [[ "$HORA" =~ ^([01][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
  echo "Uso: instalar-linux.sh HH:MM | --estado | --quitar   (p. ej. instalar-linux.sh 08:00)" >&2
  exit 1
fi
H=$((10#${HORA%%:*}))
M=$((10#${HORA##*:}))
HASTA=$(( H + 4 > 23 ? 23 : H + 4 ))

CLAUDE_BIN="$(command -v claude || true)"
PYTHON_BIN="$(command -v python3 || true)"
FALTA=""
if [ -z "$CLAUDE_BIN" ]; then FALTA="claude"; fi
if [ -z "$PYTHON_BIN" ]; then FALTA="${FALTA:+$FALTA y }python3"; fi
if [ -n "$FALTA" ]; then
  echo "Necesito $FALTA en el PATH de esta terminal. Instálalo o abre una terminal donde funcione y repite." >&2
  exit 2
fi
case "$DIR$CLAUDE_BIN$PYTHON_BIN" in
  *"'"*|*"%"*) echo "La ruta contiene ' o %, que cron no admite aquí: mueve la carpeta." >&2; exit 2 ;;
esac

chmod +x "$DIR/brief.sh"
mkdir -p "$RAIZ/logs"
ENTORNO="CLAUDE_BIN='$CLAUDE_BIN' PYTHON_BIN='$PYTHON_BIN'"
ORDEN="/bin/bash '$DIR/brief.sh' --si-falta $HORA >/dev/null 2>&1"
{
  sin_bloque
  echo "$INICIO"
  echo "$M $H-$HASTA * * * $ENTORNO $ORDEN"
  echo "@reboot sleep 120 && $ENTORNO $ORDEN"
  echo "$FIN"
} | crontab -

if [ "$((10#$(date +%H%M)))" -ge "$((10#${HORA/:/}))" ]; then
  date +%Y-%m-%d > "$RAIZ/logs/brief-diario.ultimo"   # hoy no: el primero será mañana o al probarlo a mano
fi
echo "Brief programado cada día a las $HORA con cron (y recuperación hasta las $HASTA:$(printf '%02d' "$M") y al arrancar)."
echo "Pruébalo ahora: bash .claude/skills/brief-diario/programacion/brief.sh"
