# shellcheck shell=bash
# Funciones compartidas de instalar.sh y actualizar.sh. Se carga con `source`; no se ejecuta sola.
# Compatible con bash 3.2 (el de macOS) y con Git Bash en Windows: sin arrays asociativos ni ${var,,}.

# ── Salida con etiquetas que Claude puede leer ──
ok()     { printf '[OK]     %s\n' "$*"; }
aviso()  { printf '[AVISO]  %s\n' "$*"; }
error()  { printf '[ERROR]  %s\n' "$*"; }
info()   { printf '[INFO]   %s\n' "$*"; }
paso()   { printf '\n── %s ──\n' "$*"; }
sangria() { printf '         %s\n' "$*"; }

# ── Sistema operativo: macos | linux | windows ──
detectar_so() {
    case "$(uname -s 2>/dev/null)" in
        Darwin*) echo "macos" ;;
        Linux*) echo "linux" ;;
        MINGW*|MSYS*|CYGWIN*) echo "windows" ;;
        *) echo "desconocido" ;;
    esac
}

# Ruta que entienden los programas nativos de Windows (C:/Users/...) cuando estamos en Git Bash.
ruta_nativa() {
    if [ -n "${MSYSTEM:-}" ] && command -v cygpath >/dev/null 2>&1; then
        cygpath -m "$1"
    else
        printf '%s\n' "$1"
    fi
}

# ── Python ≥ 3.10 ──
# Deja en PY (array) la orden que funciona: python3, python o `py -3` (lanzador de Windows).
# Descarta el atajo de la Microsoft Store, que existe pero no es Python.
PY=()
PY_VERSION=""
PY_VIEJO=""
detectar_python() {
    local cand v
    for cand in python3 python py; do
        command -v "$cand" >/dev/null 2>&1 || continue
        if [ "$cand" = "py" ]; then
            v="$(py -3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null | tr -d '\r')"
        else
            v="$("$cand" -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])' 2>/dev/null | tr -d '\r')"
        fi
        case "$v" in
            3.*.*) ;;
            *) continue ;;
        esac
        if version_ge "$v" "3.10.0"; then
            if [ "$cand" = "py" ]; then PY=(py -3); else PY=("$cand"); fi
            PY_VERSION="$v"
            return 0
        fi
        [ -z "$PY_VIEJO" ] && PY_VIEJO="$cand $v"
    done
    return 1
}

# version_ge A B → 0 si A >= B (versiones x.y.z numéricas).
version_ge() {
    local a1 a2 a3 b1 b2 b3
    IFS=. read -r a1 a2 a3 <<EOF
$1
EOF
    IFS=. read -r b1 b2 b3 <<EOF
$2
EOF
    a1=${a1:-0}; a2=${a2:-0}; a3=${a3%%[!0-9]*}; a3=${a3:-0}
    b1=${b1:-0}; b2=${b2:-0}; b3=${b3:-0}
    [ "$a1" -gt "$b1" ] && return 0; [ "$a1" -lt "$b1" ] && return 1
    [ "$a2" -gt "$b2" ] && return 0; [ "$a2" -lt "$b2" ] && return 1
    [ "$a3" -ge "$b3" ]
}

# Versión del producto (pyproject.toml), sin depender de Python.
version_producto() {
    sed -n 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' "$1/pyproject.toml" 2>/dev/null | head -n 1
}

# Primera línea de `<programa> <args>` o vacío si no está.
version_de() {
    command -v "$1" >/dev/null 2>&1 || return 1
    "$@" 2>&1 | head -n 1 | tr -d '\r'
}

# Instrucciones para instalar cada requisito según el sistema.
como_instalar() {
    local que="$1" so="$2"
    case "$que:$so" in
        python:macos)   sangria "Instálalo con Homebrew: brew install python@3.12"
                        sangria "o descárgalo de https://www.python.org/downloads/ (instalador para macOS)." ;;
        python:windows) sangria "Descárgalo de https://www.python.org/downloads/ y, en el instalador, marca"
                        sangria "«Add python.exe to PATH». No uses la versión de la Microsoft Store."
                        sangria "O, en PowerShell: winget install -e --id Python.Python.3.12"
                        sangria "Después cierra y vuelve a abrir Git Bash (y Claude Code)." ;;
        python:*)       sangria "Instálalo con tu gestor de paquetes, p. ej.: sudo apt install python3" ;;
        git:macos)      sangria "Ejecuta: xcode-select --install   (o: brew install git)" ;;
        git:windows)    sangria "Descarga Git para Windows (incluye Git Bash): https://git-scm.com/download/win" ;;
        git:*)          sangria "Instálalo con tu gestor de paquetes, p. ej.: sudo apt install git" ;;
        uv:windows)     sangria "En PowerShell: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\""
                        sangria "o: winget install -e --id astral-sh.uv   · o repite: bash scripts/instalar.sh --instalar-uv" ;;
        uv:macos)       sangria "Ejecuta: curl -LsSf https://astral.sh/uv/install.sh | sh   (o: brew install uv)"
                        sangria "o repite: bash scripts/instalar.sh --instalar-uv" ;;
        uv:*)           sangria "Ejecuta: curl -LsSf https://astral.sh/uv/install.sh | sh"
                        sangria "o repite: bash scripts/instalar.sh --instalar-uv" ;;
        ffmpeg:macos)   sangria "Ejecuta: brew install ffmpeg" ;;
        ffmpeg:windows) sangria "En PowerShell: winget install -e --id Gyan.FFmpeg   y vuelve a abrir Git Bash." ;;
        ffmpeg:*)       sangria "Ejecuta: sudo apt install ffmpeg   (o el equivalente de tu distribución)" ;;
    esac
}
