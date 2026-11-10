#!/usr/bin/env bash
# Reconstruye los bundles vendorizados (sin CDN en render). Uso: bash cutkit/motion/three/vendor/build.sh
#   three.ck.min.js   ← three@0.181.2 + addons (entry_three.js)
#   fontkit.ck.min.js ← fontkit@2.0.4 (entry_fontkit.js)
#   LICENSE.three.txt, LICENSE.dependencias.txt ← avisos de licencia de todo lo que entra en los bundles
# Requisitos: node + npm (descarga los paquetes a un directorio temporal) y esbuild (npx esbuild).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE"
HERE="${OUT:-$HERE}"   # OUT=/tmp/x para validar sin sobrescribir los bundles probados
mkdir -p "$HERE"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
npm init -y >/dev/null
npm install --no-audit --no-fund --silent three@0.181.2 fontkit@2.0.4 esbuild@0.25 >/dev/null
cp "$SRC/entry_three.js" "$SRC/entry_fontkit.js" .
npx esbuild entry_three.js --bundle --minify --format=iife --platform=browser --target=chrome120 \
  --legal-comments=eof --outfile="$HERE/three.ck.min.js"
npx esbuild entry_fontkit.js --bundle --minify --format=iife --platform=browser --target=chrome120 \
  --legal-comments=eof --define:process.env.NODE_ENV='"production"' --outfile="$HERE/fontkit.ck.min.js"
cp node_modules/three/LICENSE "$HERE/LICENSE.three.txt"
# fontkit arrastra dependencias (MIT y una Apache-2.0) que esbuild mete en el bundle: sus avisos tienen que viajar con él
node "$SRC/avisos_licencias.cjs" node_modules fontkit "$HERE/LICENSE.dependencias.txt"
ls -la "$HERE"/*.min.js
