---
name: producir-video
description: "Produce un vídeo de anuncio a partir de un brief por una de tres vías: ia (motor de vídeo con IA, gasta dinero real), propio (guion de grabación y montaje con cutkit) o híbrido (A-roll propio con B-roll del motor), con crítica, revisión de políticas y entrega con LEEME en la carpeta del cliente. Modo lote con lote-creativo."
argument-hint: "<cliente> <brief o carpeta del lote> [ia|propio|hibrido] [--lote]"
disable-model-invocation: true
---

# /producir-video

Entrada: `$ARGUMENTS`. **La vía `ia` y las escenas del motor en `hibrido` gastan dinero real** con las claves del
usuario: cada orden de pago (`run`, `regen`, `demo`, `actor create`, `edit --yes`, `variant` con voz o idioma y los
scripts de `modulos/motor-ia/scripts/`) la frena `motor_guard` y pide confirmación. El presupuesto global del guardián
es de 5 $ por defecto (se sube en `contexto/preferencias.md` o con `MOTOR_PRESUPUESTO_USD`).

- **Marco:** `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` (duración, vertical, sonido §3; lo-fi frente a
  producción §4), `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md` (specs §1, zonas
  seguras §2, kit mínimo §4), `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md` (IA y mejoras
  automáticas), `meta-ads-kb/03-creatividad/13-produccion-y-feedback-loop-creativo.md`.
- **Agentes:** `productor-ugc` (motor), `editor-video` (cutkit o FFmpeg), `estratega-creativo` y `redactor-anuncios`
  (guion), `critico-creativo`, `revisor-politicas`.
- **Herramientas:** `uv run --project modulos/motor-ia motor <subcomando>`, `uv run --project modulos/cutkit ck <subcomando>`,
  `herramientas/editar_video.py`, `herramientas/motor_proyectos.py`, `herramientas/nomenclatura.py`.
- **Lee:** ficha (reglas propias: cara y voz reales, afirmaciones aprobadas, política de IA), el brief y `lote.md`,
  `clientes/<slug>/marca/marca.json`, LEEME de piezas anteriores.
- **Escribe:** `clientes/<slug>/creativos/<nombre-base>/` (vídeos, `LEEME.md`, `brutos/`, guion), `planes/` (plan del
  motor), la fila de la pieza en `lote.md` y `estado.md` (`F3.piezas`).

## Pasos

1. **Contexto.** Lee la ficha, el brief (de `creativos/_lotes/<lote>/briefs/`) y la marca. Sin brief → `/brief-creativo`.
   Sin `clientes/<slug>/marca/marca.json` → pide logo, colores y tipografías al usuario y créalo según
   `docs/guias/video-propio.md`.
2. **Vía** (si no viene en la entrada, recomienda una y confírmala con una pregunta):
   - **propio:** el fundador, el equipo o un creador graban, o es una demo de pantalla. Suele ser la mejor vía en
     servicios high-ticket, agencias y SaaS (confianza y producto real). Cuesta tiempo, no dinero.
   - **ia:** nadie puede grabar o hace falta volumen. Solo si la ficha lo permite. La persona sintética presenta,
     enseña y reacciona; nunca testimonio falso en primera persona.
   - **hibrido:** A-roll propio con B-roll del motor (contexto de uso, escenas que no se pueden grabar).

   Enseña coste y tiempo estimados de cada vía antes de decidir.
3. **Guion** (`estratega-creativo` con `redactor-anuncios`): hook visual y de texto en los 2 primeros segundos,
   cuerpo (mecanismo, prueba, objeción), CTA; duración según el brief; subtítulos; texto dentro de las zonas seguras.
   - `ia`: en el formato de plan del motor (esquema en el agente `productor-ugc`), guardado en
     `clientes/<slug>/planes/<AAAA-MM-DD>_<nombre-base>.motor.json`.
   - `propio` e `hibrido`: guion de grabación y lista de planos en `creativos/<nombre-base>/guion-grabacion.md`
     (frases de A-roll, B-roll, capturas de pantalla, encuadre vertical, luz y sonido, 2–3 tomas por hook).
4. **Políticas del guion** (`revisor-politicas`) antes de gastar o grabar. Aplica los cambios.
5. **Producción por vía.**

   **ia** (`productor-ugc`):
   1. `uv run --project modulos/motor-ia motor status`: proveedores y presupuesto restante. Sin motor → `/motor instalar`.
      Si el presupuesto no cubre la estimación, para.
   2. Marca y producto en el motor (`motor brand add`, `motor product add`, gratis). Actor nuevo (`motor actor create`)
      es de pago: confirma antes.
   3. `uv run --project modulos/motor-ia motor plan-import <plan.motor.json> <brand_id> <product_id> --actor @<handle> --duration <s> --locale es-ES`
      → coste estimado. **Enséñalo y espera un «sí».**
   4. `uv run --project modulos/motor-ia motor run <project_id>` (el hook vuelve a pedir confirmación). Con 429 (cuota)
      o 402 (saldo) para: se reanuda después con el mismo `run` sin pagar lo ya hecho.
   5. QA: veredicto del motor y fotogramas revisados a mano. Arreglos selectivos (`motor regen <id> <escena>` o
      `motor edit <id> "<orden>" --yes`), cada uno con confirmación. Nunca regeneres el anuncio entero si basta una
      escena.

   **propio** (`editor-video`):
   1. **Primera vez:** `uv run --project modulos/cutkit ck instalar` (comprueba el entorno y prepara los recursos; guía
      en `docs/guias/video-propio.md`). Necesita FFmpeg (`/doctor` lo comprueba).
   2. El usuario graba siguiendo el guion y deja los brutos en `clientes/<slug>/creativos/<nombre-base>/brutos/`. Crea
      antes el `LEEME.md` de la pieza con la plantilla (paso 8): cutkit respeta lo que haya y solo añade su bloque de QA.
   3. **Montaje directo** (lo normal, sin red ni coste): 9:16 y 4:5 con hook en pantalla, subtítulos, CTA, logo y QA
      técnica (zonas seguras, sonoridad, arranque sin negro):
      `uv run --project modulos/cutkit ck anuncio clientes/<slug>/creativos/<nombre-base>/brutos/<toma>.mp4 --cliente <slug> --slug <concepto> --nombre <nombre-base>_h1 --salida clientes/<slug>/creativos/<nombre-base>/ --hook "<hook>" --cta "<cta>"`
      (B-roll con `--broll INICIO-FIN:ruta`; subtítulos `auto` locales; `--subtitulos openai` es de pago y se confirma).
   4. **Montaje avanzado** (motion graphics, cortes por palabra; necesita Node y el extra `avanzado`):
      `ck new <nombre-base> --cliente <slug> --raw <bruto> --fmt anuncio` → plan con `ck context` → `ck run` →
      ajustes con `ck edit … --op '<op JSON>' --reason "<motivo>"`.
   5. Si cutkit no se puede instalar, alternativa mínima con FFmpeg:
      `python3 -I herramientas/editar_video.py cortar|subtitular|reformatear|texto-hook` (opciones con `--help`).

   **hibrido:** A-roll como en `propio`; las escenas de B-roll salen del motor como en `ia` (solo planos de recurso,
   con su estimación y confirmación) y se montan con `ck anuncio … --broll INICIO-FIN:<escena.mp4> --etiqueta-ia`.
6. **Crítica** (`critico-creativo`): la mira como un espectador en el móvil: primeros 2 s, legibilidad, zonas seguras,
   coherencia con la landing y claridad de la oferta. Corrige los problemas mayores antes de entregar.
7. **Políticas de la pieza final** (`revisor-politicas`): texto en pantalla, voz y afirmaciones → veredicto.
8. **Entrega** en `clientes/<slug>/creativos/<nombre-base>/`:
   - archivos `<nombre-base>_h1_9x16.mp4` y `<nombre-base>_h1_4x5.mp4` (más miniatura); valida cada nombre de anuncio
     con `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre-base>_h1"`;
   - `LEEME.md` con la plantilla `.claude/skills/producir-video/plantilla-leeme.md`: `Estado: listo` y la línea
     `Veredicto de políticas` rellenada; coste real con `motor costs <id>` si hubo motor;
   - actualiza la fila de la pieza en `lote.md` (`Estado` = `lista`).
9. Marca `F3.piezas` cuando haya al menos 3 conceptos (2 si el lote es de 2 conceptos, hasta 100 €/día; 13/09 §A.2)
   con LEEME, crítica y veredicto OK u OK con cambios aplicados. Siguiente paso: `/variantes` (hooks y formatos) y `/publicar-anuncios <cliente> <lote>`.

## Modo `--lote`

1. **Avisa del coste:** el workflow `lote-creativo` produce N piezas en paralelo con crítica, políticas y arreglos:
   de 3 a 5 subagentes por pieza más 3 fijos (9–14 con 3 piezas). El motor corre en simulado o deja las órdenes de pago preparadas;
   **el dinero del motor solo se gasta cuando confirmes cada orden después**. Da la estimación de uso de Claude y la de
   dólares del motor por separado.
2. Con un «sí», lánzalo con la herramienta Workflow y args
   `{"cliente": "<slug>", "lote": "creativos/_lotes/<AAAA-MM-DD>_<lote>/", "via": "<ia|propio|hibrido>"}` (si los
   briefs vienen del modo profundo de `/brief-creativo`, añade `"estudio": "creativos/<AAAA-MM-DD>-estudio/estudio.json"`).
   Para probar la cadena sin gastar nada, `"modo": "simulado"`.
3. Ejecuta tú las órdenes de pago que deje pendientes en `ORDENES.md`, una a una y con confirmación. Después, en vez de
   repetir a mano los pasos 6–9, relanza `lote-creativo` con
   `{"cliente": "<slug>", "modo": "revisar", "lote": "creativos/_lotes/<AAAA-MM-DD>_<lote>/"}`: hace la crítica, las
   políticas y el LEEME sobre los medios reales. Revisa su resultado antes de dar las piezas por listas.

## Reglas

- El producto de verdad sale de fotos o vídeos reales; un producto o una interfaz generados por IA se deforman.
- Nada de afirmaciones fuera de las aprobadas en la ficha. Nada de testimonios falsos.
- Etiqueta de IA en toda pieza con personas, voces o escenas sintéticas, y la etiqueta de Meta al publicar.
- El MCP de Meta no sube vídeo: lo sube `/publicar-anuncios` (con `meta_ads.py` o guiando la subida en Ads Manager).
- Nunca se leen ni imprimen claves (`.env`).
