---
name: variantes
description: "Crea iteraciones de una pieza ya producida (vídeo con IA, vídeo propio, vídeo externo o estático) para testear: hooks de texto, CTA, subtítulos, formatos 4:5/9:16/1:1 y música, casi gratis, o voz e idioma, de pago y con confirmación, con nombres según la nomenclatura. No crea conceptos nuevos: para eso, /brief-creativo."
argument-hint: "<cliente> <carpeta del creativo o ID de proyecto del motor> [hooks|cta|formatos|idioma]"
---

# /variantes

Entrada: `$ARGUMENTS`.

- **Marco:** `meta-ads-kb/03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md` (cambiar el hook es una
  iteración), `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` (§2: hooks se juzgan con hook rate y
  CTR con CVR estable; §7: qué hacer con un ganador), `meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md`
  (§4: árbol de diagnóstico de un creativo), `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`
  §2 (fórmulas de hook).
- **Agentes:** `redactor-anuncios` (hooks y CTA), `productor-ugc` (motor), `editor-video` (cutkit o FFmpeg),
  `disenador-estaticos` (estáticos), `revisor-politicas`.
- **Lee:** `LEEME.md` de la pieza, su fila en `registro-creativo.csv` si ya está publicada, `lote.md`.
- **Escribe:** archivos nuevos en la misma carpeta `creativos/<nombre-base>/`, tabla de variantes del `LEEME.md` y filas
  nuevas en `lote.md`.

## Pasos

1. **Por qué iterar.** Lee el LEEME y, si la pieza ya tiene datos, su fila del registro creativo (árbol 07 §4):
   - hook rate bajo con buen hold → hooks nuevos;
   - buen hook rate, CTR bajo → cuerpo, oferta o CTA;
   - buen CTR, CVR mala → el problema está después del clic: `/landing` u `/oferta`, no variantes;
   - ganador confirmado (≥30–50 conversiones) → 3–5 iteraciones de hook y formato (05 §7).
2. **Propuesta** (`redactor-anuncios`): como máximo 2–3 hooks por concepto
   (`meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md` fase 5), de tipos distintos (pregunta de dolor,
   afirmación contraria, resultado con contexto, identidad «si llevas una agencia de…», demostración), con el lenguaje
   literal de `investigacion/voz-cliente/`; CTA alternativa; formatos que falten (9:16 y 4:5 siempre; 1:1 si se usa).
3. **Coste.** Hooks de texto, CTA en tarjeta, subtítulos, formato y música son casi gratis. **CTA hablada o idioma
   regeneran voz y son de pago**: estima el coste con `/motor` y pide un «sí» antes.
4. **Políticas:** si un hook o una CTA cambian la promesa, pásalos por `revisor-politicas` antes de generar.
5. **Generación** según el origen de la pieza:
   - **motor:** `uv run --project modulos/motor-ia motor variant <project_id> hook_text "<texto>"`, `cta "<texto>"`,
     `captions`, `aspect 4:5`, `music`; `spoken_cta` y `language` son órdenes de pago (`motor_guard` pide confirmación).
     Para encontrar el proyecto: `python3 -I herramientas/motor_proyectos.py`.
   - **cutkit, montaje directo:** vuelve a montar desde el mismo bruto con otro hook o CTA:
     `uv run --project modulos/cutkit ck anuncio <bruto> --cliente <slug> --slug <concepto> --nombre <nombre-base>_h2 --salida clientes/<slug>/creativos/<nombre-base>/ --hook "<hook nuevo>"`;
   - **cutkit, montaje avanzado:** `uv run --project modulos/cutkit ck edit <slug> <versión> --op '<op JSON>' --reason "<motivo>"`
     → `ck run <slug> <versión nueva>`.
   - **cualquier vídeo** (también uno que ya tenga el cliente): `python3 -I herramientas/editar_video.py texto-hook|subtitular|reformatear`.
   - **estático:** copia `datos.json` a `datos_h2.json`, cambia el texto y vuelve a renderizar con
     `uv run --extra render python -I herramientas/render.py png <plantilla> --datos <datos_h2.json> --salida <carpeta> --nombre <nombre-base>_h2 --cliente <slug>`.
6. **Nombres:** cada hook nuevo es un anuncio nuevo: `<nombre-base>_h2`, `_h3`; un cuerpo distinto añade `-c2`
   (`<nombre-base>_h2-c2`). El formato va en el archivo, no en el nombre del anuncio (`<nombre-base>_h2_4x5.mp4`). Valida
   con `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre>"`.
7. **Registro:** tabla «Variantes» del LEEME (variante, cambio, para qué test, archivo, veredicto) y una fila por anuncio
   nuevo en `lote.md` con `Estado` = `lista`.
8. **Test:** propón cómo medirlas con `/test-creativo` (herramienta nativa *Creative testing* para 2–5 variantes, o
   anuncio con varios textos). Cada variante necesita del orden de 1.000–2.000 impresiones para el filtro de atención
   (05 §2).

## Reglas

- Una variante no es un concepto nuevo: si todo el concepto está cansado, toca ángulo nuevo (`/brief-creativo`).
- Las «variaciones de texto» automáticas de Meta no sustituyen a esto: con `mejoras_automaticas: off` en la ficha, no
  cuentes con ellas.
