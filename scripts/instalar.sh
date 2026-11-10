#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Meta Ads OS · instalador
#  Mac, Linux y Windows (desde Git Bash). Idempotente: puedes ejecutarlo las veces que quieras;
#  nunca pisa ni borra nada tuyo (contexto/, clientes/, aprendizajes/, logs/, informes/, .env).
#
#  Uso:
#    bash scripts/instalar.sh                instala o repara
#    bash scripts/instalar.sh --comprobar    solo comprueba los requisitos; no escribe nada
#    bash scripts/instalar.sh --instalar-uv  además instala uv con su instalador oficial (necesita red)
#    bash scripts/instalar.sh --ayuda
#
#  Salida: una línea por paso con [OK], [AVISO] (sigue con una limitación), [ERROR] (bloquea) o [INFO].
#  Al final, «RESULTADO: listo» o «RESULTADO: faltan requisitos».
#  Código de salida: 0 listo (aunque haya avisos) · 1 falta un requisito obligatorio · 2 uso incorrecto.
# ─────────────────────────────────────────────────────────────────────────────

if [ -z "${BASH_VERSION:-}" ]; then
    echo "[ERROR]  Ejecuta el instalador con bash: bash scripts/instalar.sh"
    exit 2
fi
set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/_comun.sh
. "$RAIZ/scripts/_comun.sh"

COMPROBAR=false
INSTALAR_UV=false
for arg in "$@"; do
    case "$arg" in
        --comprobar) COMPROBAR=true ;;
        --instalar-uv) INSTALAR_UV=true ;;
        -h|--ayuda|--help) sed -n '3,15p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,2\}//'; exit 0 ;;
        *) error "Opción desconocida: $arg (usa --ayuda)"; exit 2 ;;
    esac
done

SO="$(detectar_so)"
VERSION="$(version_producto "$RAIZ")"
FALTA_OBLIGATORIO=false

echo "════════════════════════════════════════════════════════════"
echo "  Meta Ads OS ${VERSION:+v$VERSION }· instalador"
echo "════════════════════════════════════════════════════════════"

# ── 1. Requisitos ────────────────────────────────────────────────────────────
paso "1/3 · Requisitos"

case "$SO" in
    macos|linux) ok "Sistema: $SO ($(uname -m 2>/dev/null))" ;;
    windows) ok "Sistema: Windows con Git Bash" ;;
    *) aviso "Sistema no reconocido ($(uname -s 2>/dev/null)); sigo, pero solo está probado en Mac, Linux y Windows" ;;
esac

case "$RAIZ" in
    *OneDrive*|*"Mobile Documents"*|*Dropbox*|*"Google Drive"*|*GoogleDrive*)
        aviso "La carpeta está dentro de una nube sincronizada (OneDrive, iCloud, Dropbox o Drive)."
        sangria "Funciona, pero los entornos de los módulos de vídeo pueden corromperse al sincronizar."
        sangria "Mejor fuera de ella, p. ej. en tu carpeta de usuario: ~/meta-ads-os" ;;
esac

# Python ≥ 3.10 (obligatorio: herramientas, hooks y este instalador)
if detectar_python; then
    ok "Python $PY_VERSION (${PY[*]})"
else
    if [ -n "$PY_VIEJO" ]; then
        error "Python demasiado antiguo ($PY_VIEJO). Meta Ads OS necesita Python 3.10 o superior."
    else
        error "No encuentro Python 3. Meta Ads OS necesita Python 3.10 o superior."
    fi
    como_instalar python "$SO"
    FALTA_OBLIGATORIO=true
fi

# git (obligatorio: /actualizar y las copias de seguridad dependen de él)
if GIT_V="$(version_de git --version)"; then
    GIT_V="${GIT_V#git version }"; GIT_V="${GIT_V%% *}"
    ok "git $GIT_V"
    if ! git -C "$RAIZ" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        aviso "Esta carpeta no es un clon de git (¿descargaste un ZIP?): /actualizar no podrá traer versiones nuevas."
        sangria "Solución en docs/primeros-pasos.md → «Si descargaste un ZIP»."
    fi
else
    GIT_V=""
    error "No encuentro git."
    como_instalar git "$SO"
    FALTA_OBLIGATORIO=true
fi

# uv (obligatorio: gestiona los entornos de los módulos de vídeo, el render de estáticos y los tests)
UV_V=""
if UV_V="$(version_de uv --version)"; then
    UV_V="${UV_V#uv }"; UV_V="${UV_V%% *}"
    ok "uv $UV_V"
elif $INSTALAR_UV && ! $COMPROBAR; then
    info "Instalando uv con su instalador oficial (necesita conexión)…"
    if [ "$SO" = "windows" ]; then
        powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" \
            && PATH="$HOME/.local/bin:$PATH"
    else
        { curl -LsSf https://astral.sh/uv/install.sh | sh; } && PATH="$HOME/.local/bin:$PATH"
    fi
    if UV_V="$(version_de uv --version)"; then
        UV_V="${UV_V#uv }"; UV_V="${UV_V%% *}"
        ok "uv $UV_V instalado. Cierra y vuelve a abrir la terminal (y Claude Code) para que lo encuentre."
    else
        UV_V=""
        error "No he podido instalar uv. Hazlo a mano:"
        como_instalar uv "$SO"
        FALTA_OBLIGATORIO=true
    fi
else
    UV_V=""
    error "No encuentro uv (gestiona los entornos de Python de los módulos, los estáticos y los tests)."
    como_instalar uv "$SO"
    FALTA_OBLIGATORIO=true
fi

# FFmpeg (recomendado: vídeo)
FFMPEG_V=""
if FFMPEG_V="$(version_de ffmpeg -version)"; then
    FFMPEG_V="$(printf '%s' "$FFMPEG_V" | awk '{print $3}')"
    ok "FFmpeg $FFMPEG_V"
else
    FFMPEG_V=""
    aviso "No encuentro FFmpeg. Solo hace falta para producir o editar vídeo (/producir-video, /variantes)."
    como_instalar ffmpeg "$SO"
fi

# Claude Code (informativo)
CLAUDE_V=""
if CLAUDE_V="$(version_de claude --version)"; then
    ok "Claude Code ${CLAUDE_V%% *}"
else
    CLAUDE_V=""
    info "No encuentro la orden «claude». Si usas Claude Code desde la app de escritorio o el editor, ignóralo."
fi

if $COMPROBAR; then
    paso "Resultado"
    if $FALTA_OBLIGATORIO; then
        echo "RESULTADO: faltan requisitos"
        exit 1
    fi
    echo "RESULTADO: listo (solo comprobación; no he escrito nada)"
    exit 0
fi

if $FALTA_OBLIGATORIO; then
    paso "Resultado"
    error "Falta un requisito obligatorio: instálalo y vuelve a ejecutar: bash scripts/instalar.sh"
    echo "RESULTADO: faltan requisitos"
    exit 1
fi

# ── 2. Tu instancia (tus datos; git no los sube) ────────────────────────────
paso "2/3 · Tu espacio de trabajo"

for dir in contexto clientes aprendizajes logs informes/diario; do
    if [ -d "$RAIZ/$dir" ]; then
        ok "$dir/ ya existía"
    elif mkdir -p "$RAIZ/$dir"; then
        ok "$dir/ creada"
    else
        error "No he podido crear $dir/ (¿permisos de la carpeta?)"
        FALTA_OBLIGATORIO=true
    fi
done

for archivo in operador.md preferencias.md; do
    destino="$RAIZ/contexto/$archivo"
    if [ -e "$destino" ]; then
        ok "contexto/$archivo ya existía (no lo toco)"
    elif cp "$RAIZ/plantillas/contexto/$archivo" "$destino"; then
        ok "contexto/$archivo creado desde la plantilla"
    else
        error "No he podido crear contexto/$archivo"
        FALTA_OBLIGATORIO=true
    fi
done

# .env: se crea una vez desde la plantilla y nunca se lee aquí.
if [ -e "$RAIZ/.env" ]; then
    ok ".env ya existía (no lo toco ni lo leo)"
elif cp "$RAIZ/plantillas/env.ejemplo" "$RAIZ/.env"; then
    ok ".env creado desde plantillas/env.ejemplo (todas las claves vacías)"
else
    error "No he podido crear .env"
    FALTA_OBLIGATORIO=true
fi
if [ -e "$RAIZ/.env" ]; then
    chmod 600 "$RAIZ/.env" 2>/dev/null
    if [ "$SO" = "windows" ]; then
        info "En Windows los permisos de .env los gestiona el sistema: no compartas esta carpeta con nadie."
    else
        ok ".env con permisos 600 (solo tu usuario puede leerlo)"
    fi
fi

# ── 3. Estado de la instalación ─────────────────────────────────────────────
paso "3/3 · Comprobación final"

SISTEMA_JSON="$(printf '{"so":"%s","python":"%s","git":"%s","uv":"%s","ffmpeg":"%s","claude":"%s"}' \
    "$SO" "$PY_VERSION" "$GIT_V" "$UV_V" "$FFMPEG_V" "${CLAUDE_V%% *}" | tr -d '\\')"

if $FALTA_OBLIGATORIO; then
    "${PY[@]}" -I "$(ruta_nativa "$RAIZ/scripts/instalacion.py")" --raiz "$(ruta_nativa "$RAIZ")" preparar \
        --sistema "$SISTEMA_JSON" --tecnica fallo --detalle "No se pudo crear el espacio de trabajo" >/dev/null 2>&1
    error "La instalación no ha terminado. Revisa los errores de arriba y vuelve a ejecutar: bash scripts/instalar.sh"
    echo "RESULTADO: faltan requisitos"
    exit 1
fi

if "${PY[@]}" -I "$(ruta_nativa "$RAIZ/scripts/instalacion.py")" --raiz "$(ruta_nativa "$RAIZ")" preparar \
        --sistema "$SISTEMA_JSON" --tecnica hecho \
        --detalle "Requisitos comprobados y espacio de trabajo creado"; then
    ok "contexto/instalacion.json: fase técnica hecha (el resto lo hace /empezar)"
else
    error "No he podido escribir contexto/instalacion.json"
    echo "RESULTADO: faltan requisitos"
    exit 1
fi

# Prueba de humo: una herramienta sin red ni claves.
if [ -f "$RAIZ/herramientas/estado.py" ]; then
    if (cd "$RAIZ" && "${PY[@]}" -I herramientas/estado.py resumen --json >/dev/null 2>&1); then
        ok "Las herramientas responden (herramientas/estado.py)"
    else
        aviso "herramientas/estado.py no ha respondido bien. Tras /empezar, ejecuta /doctor para ver el motivo."
    fi
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Listo. Siguiente paso:"
echo "    1. Abre Claude Code en esta carpeta."
echo "    2. Escribe /empezar (unos 30 minutos: perfil, conexión con Meta,"
echo "       tu primer cliente y su primer entregable)."
echo "  Si algo falla: /doctor (dentro de Claude Code) o vuelve a ejecutar este instalador."
echo "════════════════════════════════════════════════════════════"
echo "RESULTADO: listo"
exit 0
