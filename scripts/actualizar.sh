#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  Meta Ads OS · actualizar a la última versión
#  Trae la versión nueva con `git pull --ff-only` y aplica las migraciones de datos que declare
#  scripts/migraciones/. Nunca toca tu instancia (contexto/, clientes/, aprendizajes/, logs/, informes/, .env)
#  salvo esas migraciones, que copian antes lo que cambian.
#
#  Uso:
#    bash scripts/actualizar.sh               actualiza
#    bash scripts/actualizar.sh --comprobar   dice si hay versión nueva y qué trae, sin cambiar nada
#    bash scripts/actualizar.sh --ayuda
#
#  Salida con [OK], [AVISO], [ERROR] e [INFO], y al final «RESULTADO: …».
#  Código de salida: 0 bien (o ya al día) · 1 no se pudo actualizar (nada cambiado) · 2 uso incorrecto.
# ─────────────────────────────────────────────────────────────────────────────

if [ -z "${BASH_VERSION:-}" ]; then
    echo "[ERROR]  Ejecuta con bash: bash scripts/actualizar.sh"
    exit 2
fi
set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=scripts/_comun.sh
. "$RAIZ/scripts/_comun.sh"

COMPROBAR=false
for arg in "$@"; do
    case "$arg" in
        --comprobar) COMPROBAR=true ;;
        -h|--ayuda|--help) sed -n '3,14p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,2\}//'; exit 0 ;;
        *) error "Opción desconocida: $arg (usa --ayuda)"; exit 2 ;;
    esac
done

fallar() {
    echo "RESULTADO: no actualizado (no he cambiado nada)"
    exit 1
}

cd "$RAIZ" || exit 1
VERSION_ANTES="$(version_producto "$RAIZ")"
echo "Meta Ads OS ${VERSION_ANTES:+v$VERSION_ANTES }· actualizar"

# ── Comprobaciones previas ──────────────────────────────────────────────────
if ! command -v git >/dev/null 2>&1; then
    error "No encuentro git, que es lo que trae las versiones nuevas."
    como_instalar git "$(detectar_so)"
    fallar
fi
if [ ! -e "$RAIZ/.git" ]; then
    error "Esta carpeta no es un clon de git (¿descargaste un ZIP?), así que no puede actualizarse sola."
    sangria "Clona el repositorio en otra carpeta y copia allí tus datos: contexto/, clientes/, aprendizajes/,"
    sangria "logs/, informes/ y .env. Paso a paso en docs/primeros-pasos.md → «Si descargaste un ZIP»."
    fallar
fi
if ! detectar_python; then
    error "No encuentro Python 3.10 o superior (lo necesitan las migraciones)."
    como_instalar python "$(detectar_so)"
    fallar
fi
if ! git remote get-url origin >/dev/null 2>&1; then
    error "Este clon no tiene el remoto «origin», así que no sé de dónde traer la versión nueva."
    sangria "Añádelo con la URL del repositorio: git remote add origin https://github.com/ai-agency-accelerator/Meta-Ads-OS.git"
    fallar
fi

RAMA="$(git symbolic-ref --quiet --short HEAD 2>/dev/null || true)"
if [ -z "$RAMA" ]; then
    error "Estás en un commit suelto (detached HEAD), no en una rama."
    sangria "Vuelve a la rama principal con: git switch main   y repite."
    fallar
fi
DESTINO="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
[ -z "$DESTINO" ] && DESTINO="origin/$RAMA"

# Cambios tuyos en archivos del producto: el pull los pisaría o fallaría a medias.
CAMBIADOS="$(git status --porcelain --untracked-files=no 2>/dev/null)"
if [ -n "$CAMBIADOS" ]; then
    error "Has modificado archivos del producto; actualizar los pisaría. Archivos:"
    printf '%s\n' "$CAMBIADOS" | sed 's/^/           /'
    sangria "Tus datos (contexto/, clientes/, aprendizajes/…) no cuentan: esto son archivos del sistema."
    sangria "Opciones (ninguna borra nada):"
    sangria "  a) Guardarlos aparte, actualizar y recuperarlos:"
    sangria "       git stash push -m mis-cambios && bash scripts/actualizar.sh && git stash pop"
    sangria "  b) Mover tus personalizaciones a contexto/ o a .claude/settings.local.json, que no se versionan."
    sangria "Más en docs/solucion-de-problemas.md → «/actualizar dice que has modificado archivos»."
    fallar
fi

# ── ¿Hay versión nueva? ─────────────────────────────────────────────────────
if ! git fetch --quiet origin 2>/dev/null; then
    error "No he podido conectar con el repositorio (sin conexión o sin acceso)."
    sangria "Comprueba la conexión y que tu cuenta de GitHub sigue teniendo acceso al repositorio."
    fallar
fi
if ! git rev-parse --verify --quiet "$DESTINO" >/dev/null; then
    error "La rama $DESTINO no existe en el repositorio."
    fallar
fi

NUEVOS="$(git rev-list --count "HEAD..$DESTINO" 2>/dev/null || echo 0)"
PROPIOS="$(git rev-list --count "$DESTINO..HEAD" 2>/dev/null || echo 0)"
if [ "$PROPIOS" != "0" ]; then
    error "Tu copia tiene $PROPIOS commit(s) propios que no están en el repositorio, así que no se puede avanzar"
    sangria "en línea recta (fast-forward). Es lo que pasa si has hecho commits en esta carpeta."
    sangria "Solución sin perder nada en docs/solucion-de-problemas.md → «Tu copia tiene commits propios»."
    fallar
fi

VERSION_NUEVA="$(git show "$DESTINO:pyproject.toml" 2>/dev/null \
    | sed -n 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)"

if [ "$NUEVOS" = "0" ]; then
    ok "Ya tienes la última versión (v$VERSION_ANTES)"
else
    ok "Hay $NUEVOS cambio(s) nuevos: v$VERSION_ANTES → v${VERSION_NUEVA:-?}"
    git log --oneline --no-decorate -n 15 "HEAD..$DESTINO" | sed 's/^/           /'
fi

if $COMPROBAR; then
    if [ "$NUEVOS" != "0" ]; then
        info "Para actualizar: /actualizar en Claude Code o bash scripts/actualizar.sh"
        echo "RESULTADO: hay versión nueva (solo comprobación)"
    else
        echo "RESULTADO: al día (solo comprobación)"
    fi
    exit 0
fi

# ── Actualizar ──────────────────────────────────────────────────────────────
if [ "$NUEVOS" != "0" ]; then
    ANTES="$(git rev-parse HEAD)"
    if ! git pull --ff-only --quiet origin "$RAMA"; then
        error "git pull --ff-only ha fallado. No he cambiado nada más."
        sangria "Copia este mensaje en Claude Code o mira docs/solucion-de-problemas.md."
        fallar
    fi
    ok "Producto actualizado a v$(version_producto "$RAIZ")"
    if [ -f "$RAIZ/CHANGELOG.md" ] && [ -n "$VERSION_ANTES" ]; then
        info "Novedades (CHANGELOG.md):"
        awk -v antes="[$VERSION_ANTES]" '/^## / { if (index($0, antes)) exit; dentro = 1 } dentro' "$RAIZ/CHANGELOG.md" \
            | head -n 40 | sed 's/^/           /'
    fi
    if git diff --name-only "$ANTES" HEAD -- .claude/ 2>/dev/null | grep -q .; then
        aviso "Han cambiado skills, agentes o hooks: cierra y vuelve a abrir Claude Code para cargarlos."
    fi
fi

# ── Migraciones de datos ────────────────────────────────────────────────────
if [ -d "$RAIZ/scripts/migraciones" ]; then
    if ! "${PY[@]}" -I "$(ruta_nativa "$RAIZ/scripts/migrar.py")" --raiz "$(ruta_nativa "$RAIZ")" aplicar; then
        error "Una migración ha fallado. El producto está actualizado, pero tus datos necesitan atención."
        sangria "Vuelve a ejecutar bash scripts/actualizar.sh cuando lo arregles: retoma donde se quedó."
        echo "RESULTADO: actualizado con una migración pendiente"
        exit 1
    fi
fi

echo "RESULTADO: listo"
exit 0
