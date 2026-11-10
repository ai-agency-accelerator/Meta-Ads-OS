#!/usr/bin/env bash
# Programa el brief diario en un Mac con launchd: basta con el Mac encendido y tu sesión iniciada; no hay que abrir
# nada. Lo usa /brief-diario programar (método «sistema»).
#
#   instalar-mac.sh HH:MM     instala o actualiza la tarea a esa hora (local)
#   instalar-mac.sh --probar  la lanza ahora por launchd, igual que cada mañana (tarda de 2 a 6 minutos)
#   instalar-mac.sh --estado  dice si está cargada, el último intento y el último envío
#   instalar-mac.sh --quitar  la descarga y borra su .plist de ~/Library/LaunchAgents (confírmalo antes)
set -euo pipefail

ETIQUETA="com.meta-ads-os.brief-diario"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(cd "$DIR/../../../.." && pwd)"
DESTINO="$HOME/Library/LaunchAgents/$ETIQUETA.plist"
DOMINIO="gui/$(id -u)"
MARCA="$RAIZ/logs/brief-diario.ultimo"

if [ "$(uname)" != "Darwin" ]; then
  echo "Esto es para Mac. En Linux usa instalar-linux.sh y en Windows instalar-windows.ps1." >&2
  exit 1
fi

case "${1:-}" in
  --probar)
    if ! launchctl print "$DOMINIO/$ETIQUETA" >/dev/null 2>&1; then
      echo "La tarea no está instalada: ejecuta primero instalar-mac.sh HH:MM" >&2
      exit 2
    fi
    mkdir -p "$RAIZ/logs"
    printf 'forzar\n' > "$MARCA"
    launchctl kickstart -k "$DOMINIO/$ETIQUETA"
    echo "Lanzado. En 2-6 minutos debería llegarte el brief. Comprueba la última línea de logs/notificaciones.jsonl"
    echo "y, si no llega, el final de logs/brief-diario-$(date +%Y-%m).log y de logs/brief-diario-launchd.log."
    exit 0
    ;;
  --estado)
    if launchctl print "$DOMINIO/$ETIQUETA" >/dev/null 2>&1; then
      echo "Tarea cargada: $ETIQUETA"
      launchctl print "$DOMINIO/$ETIQUETA" | grep -E '^\s*(state|last exit code|runs) ' || true
    else
      echo "La tarea no está cargada."
    fi
    echo "Último intento: $(cat "$MARCA" 2>/dev/null || echo 'ninguno')"
    echo "Último envío: $(tail -n 1 "$RAIZ/logs/notificaciones.jsonl" 2>/dev/null || echo 'ninguno')"
    exit 0
    ;;
  --quitar)
    launchctl bootout "$DOMINIO/$ETIQUETA" 2>/dev/null || true
    if [ -f "$DESTINO" ]; then
      rm "$DESTINO"
      echo "Tarea quitada y $DESTINO borrado."
    else
      echo "No había tarea instalada."
    fi
    exit 0
    ;;
esac

HORA="${1:-}"
if ! [[ "$HORA" =~ ^([01][0-9]|2[0-3]):[0-5][0-9]$ ]]; then
  echo "Uso: instalar-mac.sh HH:MM | --probar | --estado | --quitar   (p. ej. instalar-mac.sh 08:00)" >&2
  exit 1
fi

# macOS no deja que una tarea de fondo lea Escritorio, Documentos, Descargas ni iCloud Drive sin «Acceso total al disco»
case "$RAIZ/" in
  "$HOME/Desktop/"*|"$HOME/Documents/"*|"$HOME/Downloads/"*|"$HOME/Library/Mobile Documents/"*)
    if [ "${BRIEF_IGNORAR_CARPETA:-}" != "1" ]; then
      echo "La carpeta está en Escritorio, Documentos, Descargas o iCloud Drive: macOS no deja que una tarea" >&2
      echo "programada la lea y el brief fallaría con «Operation not permitted». Muévela (p. ej. a ~/meta-ads-os)" >&2
      echo "y vuelve a ejecutar esto. Si ya diste «Acceso total al disco» a /bin/bash, repite con BRIEF_IGNORAR_CARPETA=1." >&2
      exit 2
    fi
    ;;
esac

CLAUDE_BIN="$(command -v claude || true)"
PYTHON_BIN="$(command -v python3 || true)"
if [ -z "$CLAUDE_BIN" ]; then
  echo "No encuentro claude en tu PATH. Instala Claude Code o abre una terminal donde \`claude\` funcione." >&2
  exit 2
fi
if [ -z "$PYTHON_BIN" ]; then
  echo "No encuentro python3. Instálalo (el instalador de Meta Ads OS lo comprueba) y repite." >&2
  exit 2
fi
RUTA="$(dirname "$CLAUDE_BIN"):$(dirname "$PYTHON_BIN"):$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

mkdir -p "$HOME/Library/LaunchAgents" "$RAIZ/logs"
chmod +x "$DIR/brief.sh"
"$PYTHON_BIN" -I - "$DIR/$ETIQUETA.plist" "$DESTINO" "$RAIZ" "$HORA" "$CLAUDE_BIN" "$PYTHON_BIN" "$RUTA" <<'PY'
import html, sys
plantilla, destino, raiz, hora, claude, python, ruta = sys.argv[1:8]
h, m = (int(x) for x in hora.split(":"))
t = open(plantilla, encoding="utf-8").read()
valores = {"__RAIZ__": raiz, "__HORA__": hora, "__H__": str(h), "__M__": str(m), "__CLAUDE_BIN__": claude,
           "__PYTHON_BIN__": python, "__PATH__": ruta}
for marcador, valor in valores.items():
    t = t.replace(marcador, html.escape(valor, quote=False))
with open(destino, "w", encoding="utf-8") as f:
    f.write(t)
PY
plutil -lint "$DESTINO" >/dev/null

# Si hoy ya pasó la hora, la carga (RunAtLoad) no lanza un brief ahora: el primero será mañana o con --probar
if [ "$((10#$(date +%H%M)))" -ge "$((10#${HORA/:/}))" ]; then
  date +%Y-%m-%d > "$MARCA"
fi

launchctl bootout "$DOMINIO/$ETIQUETA" 2>/dev/null || true
launchctl bootstrap "$DOMINIO" "$DESTINO"
echo "Brief programado cada día a las $HORA con launchd ($DESTINO)."
echo "Pruébalo ahora por el mismo camino: bash .claude/skills/brief-diario/programacion/instalar-mac.sh --probar"
