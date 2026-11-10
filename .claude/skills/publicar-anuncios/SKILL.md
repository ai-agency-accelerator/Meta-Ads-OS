---
name: publicar-anuncios
description: "Sube a Meta un lote de piezas ya producidas y aprobadas a una campaña que ya existe: vídeo con meta_ads.py o guiando la subida en Ads Manager, imagen con el MCP; todo en pausa y con las mejoras automáticas desactivadas. Verifica previsualizaciones y lo anota en el change log y el registro creativo. Activar exige confirmación."
argument-hint: "<cliente> <lote> [ID del conjunto o campaña de destino]"
disable-model-invocation: true
---

# /publicar-anuncios

Entrada: `$ARGUMENTS` (`<lote>` = carpeta `creativos/_lotes/<AAAA-MM-DD>_<lote>/` o su nombre). Para una campaña nueva,
usa `/lanzar-campana`.

- **Marco:** `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` (§3 estructura por tamaño, §6 higiene
  del test), `meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md` (§5 disciplina: ventana de
  edición fija), `meta-ads-kb/09-bidding-escalado-economia-analitica/13-experimentacion-ab-tests.md` §4 (añadir
  anuncios a un conjunto vivo es una edición significativa), `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md`
  (mejoras automáticas), `meta-ads-kb/10-cambios-2025-2026-api-ia-automatizacion/11-mcp-meta-inventario-y-conexion.md`
  (qué puede crear el MCP).
- **Agentes:** `operador-meta` (el único que escribe), `revisor-politicas` (si falta un veredicto), `revisor-estrategia`.
- **Herramientas:** `nomenclatura.py`, `meta_ads.py` (`crear --simular`, `crear`, `creatividades`, `activar --confirmo`).
- **Lee:** `lote.md`, `LEEME.md` de cada pieza, ficha (cuenta, topes, `mejoras_automaticas`), `change-log.md`.
- **Escribe:** `planes/<AAAA-MM-DD>_publicar-<lote>.json`, `change-log.md`, `registro-creativo.csv`, `lote.md` y LEEME.

## Pasos

1. **Comprobación del lote**, pieza a pieza (solo pasan las que cumplen todo):
   - `LEEME.md` con `- **Veredicto de políticas:** OK` u `OK con cambios aplicados` (contrato §6). `OK con cambios`
     (aún sin aplicar), `pendiente` o `NO publicar` → fuera, o `/revisar-anuncio`;
   - nombres válidos: `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre>"` (y `registro_creativo.py
     sin-nomenclatura` no debe listarlos después);
   - archivos 9:16 y 4:5 presentes; texto principal, titular, CTA y URL en `lote.md`; crítica hecha.
   - **Dos casos que no se suben con archivos** (contrato §6):
     - LEEME con `- **Origen orgánico:** … publicacion-existente …`: no necesita archivos 9:16 ni 4:5, se publica
       con la publicación original. Con token, en el plan del paso 3 el anuncio lleva `publicacion_ig` (ID numérico
       del medio de Instagram) o `publicacion_fb` (`<pagina>_<post>`) en lugar de `video` o `imagen`; sin token, el
       usuario lo crea en Ads Manager con la «Checklist de publicación existente (Ads Manager)» de
       `/organico-a-anuncios`. En los dos casos `operador-meta` lo verifica (`ads_get_creatives`:
       `source_instagram_media_id` u `object_story_id` igual al ID del LEEME);
     - LEEME con `- **Identidad:** colaboracion` en «Prueba social y derechos»: no se sube con la Página. Va por
       `/casos-y-creadores` (paso C10, `.claude/skills/casos-y-creadores/publicar-colaboracion.md`): alta guiada en Ads
       Manager, en pausa, y verificación en solo lectura.

     Las de colaboración (y las publicaciones existentes sin token) salen del plan JSON, pero siguen en el lote, en la
     aprobación del paso 4 y en el registro del paso 7.
2. **Destino** (con `ads_get_ad_entities`): campaña y conjunto existentes de la ficha o del lote. Elige con el usuario
   la estructura del test (05 §3 y `/test-creativo`): añadir al conjunto principal, herramienta nativa *Creative
   testing* o conjunto de test. Agrupa la publicación en la ventana de edición: todo el lote junto, no anuncio a anuncio
   durante días. Si el conjunto cambió hace menos de 7 días, `meta_guard` lo avisará: explica el motivo de la espera o
   de no esperar.
3. **Plan de publicación** en `clientes/<slug>/planes/<AAAA-MM-DD>_publicar-<lote>.json` (formato de
   `plantillas/plan-campana.json`, apuntando al conjunto existente; UTMs con la plantilla de
   `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8) y tabla resumen: anuncio, archivo por ubicación, texto,
   CTA, URL, conjunto de destino. Valida sin red:
   `python3 -I herramientas/meta_ads.py crear clientes/<slug>/planes/<AAAA-MM-DD>_publicar-<lote>.json --simular --cliente <slug>`.
4. **Aprobación:** `revisor-estrategia` revisa el plan (estructura del test, paciencia). Enséñalo y **espera un «sí»
   explícito**.
5. **Subida en pausa** (`operador-meta`; cada escritura pide confirmación y el hook `control_publicacion` comprueba
   nombre y veredicto: si bloquea, se corrige la causa, no se rodea):
   - **vídeo, con token** (`/conectar meta --avanzado`): `python3 -I herramientas/meta_ads.py crear <plan.json> --cliente <slug>`
     sube los vídeos, crea las creatividades con las mejoras automáticas desactivadas y los anuncios en pausa (si
     `--simular` no acepta el conjunto existente en el plan, usa la ruta sin token para los vídeos);
   - **vídeo, sin token:** el MCP no sube vídeo. Guía al usuario en Ads Manager con una checklist por anuncio (conjunto
     correcto, nombre exacto, archivo 9:16 para Stories y Reels y 4:5 para Feed, textos, URL y parámetros de URL, mejoras
     automáticas según la ficha, etiqueta de IA si la pieza la lleva, **en pausa**) y que te pase los IDs;
   - **imagen única:** MCP `ads_create_creative` + `ads_create_ad` (en pausa), o `meta_ads.py crear` si hay token;
   - **carrusel:** `meta_ads.py` si lo admite el plan; si no, Ads Manager con la misma checklist.
6. **Verificación:** previsualizaciones en Feed y Reels/Stories (`ads_get_ad_preview`); mejoras automáticas realmente
   apagadas (`python3 -I herramientas/meta_ads.py creatividades --plan <plan.json> --cliente <slug>` con token, o
   `ads_get_creatives`); URL y UTMs; estado en pausa. Lo que no cuadre con la ficha se corrige antes de activar.
7. **Registro:**
   - `change-log.md`: una fila por anuncio (o una por lote con la lista de IDs), `Quién` = `operador-meta (aprobado por
     <operador>)` (o `usuario en Ads Manager (verificado por operador-meta)` en lo creado a mano: publicaciones
     existentes, anuncios de colaboración y vídeos sin token), motivo = hipótesis del lote, métrica y fecha de
     evaluación (kill rule a 2–3× CPA y regla de paciencia);
   - `registro-creativo.csv`: una fila por `ad_id` con `nombre`, `fecha`, `campana`, `conjunto`, `angulo`, `concepto`,
     `formato`, `hook`, `via`, `identidad` (`pagina` o `colaboracion`), `ruta_creativo` = `creativos/<nombre-base>` y
     `veredicto` = `en-test`;
   - `lote.md`: `Estado` = `publicada` y `ad_id`; cada LEEME: `- **Estado:** publicado` y la sección «Publicación». Si
     tiene «Prueba social y derechos», añade la fila del anuncio a su tabla de identidades (ad_id, identidad, alias del
     socio, cabecera, publicación existente o contenido nuevo): la misma pieza publicada con la Página y como
     colaboración comparte nombre y solo la separa el `ad_id`.
8. **Activación**, solo con confirmación específica en el momento («activa estos N anuncios»): `ads_activate_entity` o
   `python3 -I herramientas/meta_ads.py activar <ids> --confirmo --cliente <slug>`. Anota la activación en el change log.

## Reglas

- Nada se publica sin veredicto de políticas ni con nombres fuera de la nomenclatura: el registro y `/siguiente-anuncio`
  se quedarían ciegos.
- No dupliques anuncios rechazados ni recrees anuncios con prueba social sin motivo (se pierde el post ID).
- Borrar está bloqueado: lo que sobre se pausa.
