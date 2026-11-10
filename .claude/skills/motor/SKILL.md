---
name: motor
description: "Estado, mantenimiento e instalación del motor de vídeo con IA (modulos/motor-ia): proveedores y claves activas, gasto frente al presupuesto del guardián, proyectos pausados por saldo o cuota, costes por proyecto, prueba simulada sin gasto, limpieza de temporales y modo instalar. Consúltala antes de producir vídeo con IA."
argument-hint: "[estado|instalar|costes <proyecto>|proyectos|test|reanudar <proyecto>|limpiar]"
---

# /motor

Entrada: `$ARGUMENTS` (vacío = `estado`). Orden base del contrato §14: `uv run --project modulos/motor-ia motor <subcomando>`.
Todo lo de esta skill es gratis **salvo `reanudar`**, que es una orden de pago (la frena `motor_guard`). Producir
vídeo es `/producir-video`, no esta skill.

Reglas: nunca leas `.env` (las ✔ de las claves las enseña el propio motor); no cambies el presupuesto sin permiso
explícito; si el gasto está cerca del presupuesto, avísalo antes de cualquier producción.

## estado (por defecto)
1. Si no existe `modulos/motor-ia/.venv` → «el motor no está instalado» y ofrece `/motor instalar`. Fin.
2. `uv run --project modulos/motor-ia motor status`: proveedores, claves presentes, gasto total frente al presupuesto
   global y si está en modo simulado.
3. `python3 -I herramientas/motor_proyectos.py`: proyectos con estado (`done`, `needs_review`, `paused_billing`,
   `paused_budget`, `interrupted`…), coste real y exportación.
4. Disco: `du -sh modulos/motor-ia/data`.
5. Resumen en 5 líneas. Si el gasto supera el 80 % del presupuesto `[HYPOTHESIS]`, avisa. Proyectos pausados →
   explica la causa y ofrece `reanudar`.

## instalar
Módulo opcional; se instala en el ordenador del usuario (los entornos no se versionan ni se copian entre carpetas).
1. **Requisitos.** `uv --version` y `ffmpeg -version`. Falta FFmpeg → Mac `brew install ffmpeg`; Windows
   `winget install Gyan.FFmpeg` (y reabrir Git Bash); Linux, el gestor de paquetes. Python ≥3.11 no hace falta
   instalarlo a mano: uv lo descarga si no lo encuentra.
2. **Entorno.** `uv sync --project modulos/motor-ia` (crea `modulos/motor-ia/.venv`).
3. **Modelos locales.** `uv run --project modulos/motor-ia motor setup`: descarga unos 60 MB de modelos gratuitos
   (caras, OCR, CLIP) y comprueba `ffmpeg`, `ffprobe` y `tesseract`. No llama a modelos de pago.
4. **Claves.** El usuario abre `.env` con su editor y pega `GEMINI_API_KEY` (de Google AI Studio); el resto de
   variables del motor están en `plantillas/env.ejemplo`. Nunca en el chat.
5. **Presupuesto.** El guardián del motor viene con **5 $** de presupuesto global. Para cambiarlo, el usuario lo fija
   en la cabecera de `contexto/preferencias.md` (`motor:` → `presupuesto_usd: <cifra>`) o con `MOTOR_PRESUPUESTO_USD`
   en `.env`, que manda sobre la cabecera; cambiarlo tú solo
   con su permiso explícito y la cifra que diga. Explica que cada orden de pago pedirá confirmación con su coste
   estimado. Comprueba con `motor status` que el presupuesto mostrado es el que quería.
6. **Prueba sin gasto.** `MOTOR_MOCK=1 uv run --project modulos/motor-ia motor status` y la prueba completa simulada
   (`test`, abajo).
7. Si existe `contexto/instalacion.json`, marca `motor` → `hecho` (`python3 -I scripts/instalacion.py marcar motor
   hecho`).

## costes <proyecto>
`uv run --project modulos/motor-ia motor costs <proyecto>`: coste por etapa, modelo y escena. Sin proyecto, el total.

## proyectos
`python3 -I herramientas/motor_proyectos.py [--estado <estado>] [--max N]`.

## test
Prueba extremo a extremo simulada (0 $, usa un directorio temporal que se limpia solo):
`MOTOR_MOCK=1 uv run --project modulos/motor-ia --extra dev pytest modulos/motor-ia/tests/test_e2e_mock.py -q`.
Úsala tras instalar o actualizar.

## reanudar <proyecto>
Solo para proyectos en `paused_billing`, `paused_budget` o `interrupted`.
1. Explica la causa: saldo del proveedor agotado, presupuesto del guardián alcanzado o cuota diaria del proveedor
   (se libera con el tiempo).
2. Con su OK: `uv run --project modulos/motor-ia motor run <proyecto>`. Es reanudable: las escenas ya hechas salen de
   caché y no se vuelven a cobrar. `motor_guard` pedirá confirmación del coste.

## limpiar
1. `uv run --project modulos/motor-ia motor gc --dry-run`: enseña qué temporales de trabajo liberaría (QA, renders
   intermedios, capturas de depuración). Nunca toca assets ni exportaciones.
2. Solo con un sí explícito a esa lista: `uv run --project modulos/motor-ia motor gc`. La caché de segmentos de render
   (`--segments`) se pregunta aparte: borrarla obliga a volver a renderizar.
