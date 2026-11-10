---
name: actualizar
description: "Actualiza Meta Ads OS a la última versión sin tocar tus datos: revisa cambios locales en archivos del producto, enseña qué llega, hace git pull --ff-only, aplica las migraciones declaradas, resume el CHANGELOG y pasa /doctor. Nunca fuerza ni pisa tu instancia (contexto, clientes, aprendizajes, informes, logs, .env)."
argument-hint: "[comprobar]"
disable-model-invocation: true
---

# /actualizar

`comprobar` solo enseña qué llegaría, sin actualizar. Tu instancia (`contexto/`, `clientes/`, `aprendizajes/`,
`informes/`, `logs/`, `.env`) está fuera de git: una actualización no la toca, salvo las migraciones que declare
`scripts/migraciones/` (y esas se enseñan antes).

## Pasos

1. **Cambios locales.** `git status --porcelain`. Lo que salga son archivos **del producto** que has modificado (la
   instancia no aparece porque git la ignora).
   - Nada → sigue.
   - Hay cambios → enséñalos y no sigas sin decisión. Lo recomendado es guardarlos aparte sin perder nada:
     `git stash push -m "cambios locales antes de actualizar AAAA-MM-DD"` (se recuperan con `git stash pop`). Solo con
     su sí. Nunca `git checkout -- <archivo>`, `git reset --hard` ni `--force`: eso descarta trabajo.
2. **Qué llega.** `bash scripts/actualizar.sh --comprobar` (no cambia nada); si hace falta más detalle, `git fetch`,
   `git log --oneline HEAD..@{u}` y la parte nueva de `CHANGELOG.md`. Resúmelo en
   lenguaje de usuario: qué skills, agentes o herramientas cambian, qué migraciones hay y si hace falta algo por su
   parte. Con `comprobar`, termina aquí.
3. **Punto de vuelta.** Apunta la versión actual: `git rev-parse --short HEAD`.
4. **Actualizar.** `bash scripts/actualizar.sh` (hace `git pull --ff-only` y aplica las migraciones declaradas).
   - Si falla porque la rama ha divergido (hay commits propios en archivos del producto), no fuerces: explica qué ha
     pasado y las opciones, y espera su decisión.
   - Si una migración falla, para y enseña el error tal cual; la instancia queda como estaba antes de esa migración.
5. **Después.**
   - `python3 -I herramientas/doctor.py --json` y resume solo lo que esté mal.
   - Si cambió `modulos/motor-ia/pyproject.toml` y el motor está instalado → ofrece `uv sync --project modulos/motor-ia`
     (descarga dependencias). Igual con `modulos/cutkit/`.
   - Si cambiaron `.claude/settings.json`, los hooks o `.mcp.json` → reinicia Claude Code para cargarlos.
   - Si `plantillas/env.ejemplo` trae variables nuevas, di sus **nombres** y que las añada él a `.env` si las necesita.
     No abras `.env`.
   - Si había cambios guardados con `git stash`, recuérdale que siguen ahí y cómo recuperarlos.
6. **Resumen.** Versión de → a, novedades principales, migraciones aplicadas y lo que tiene que hacer él.

## Si algo se rompe tras actualizar
Ofrece volver a la versión apuntada en el paso 3. Volver atrás descarta los archivos del producto de la versión nueva
(no tus datos): hazlo solo con un sí explícito a ese paso concreto y con la instancia intacta. Después, `/doctor`.
