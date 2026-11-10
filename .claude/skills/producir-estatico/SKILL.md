---
name: producir-estatico
description: "Produce estáticos y carruseles para Meta (4:5, 9:16 y 1:1) a partir de un brief con plantillas HTML y render.py, usando fotos o capturas reales y la marca del cliente; imagen con IA solo con confirmación de coste. Incluye crítica, revisión de políticas y entrega con LEEME. Modo lote con lote-creativo."
argument-hint: "<cliente> <brief o carpeta del lote> [estatico|carrusel] [--lote]"
---

# /producir-estatico

Entrada: `$ARGUMENTS`.

- **Marco:** `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` (catálogo de formatos §1, estáticos frente a vídeo
  §2), `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md` (specs y zonas seguras),
  `meta-ads-kb/03-creatividad/08-copy-de-anuncios.md`, `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`
  §6 (elementos visuales).
- **Agentes:** `disenador-estaticos`, `redactor-anuncios`, `critico-creativo`, `revisor-politicas`.
- **Herramientas:** `herramientas/render.py`, plantillas en `plantillas/html/`, `herramientas/nomenclatura.py`.
- **Lee:** ficha, brief y `lote.md`, `clientes/<slug>/marca/` (`marca.json` + archivos), material real del cliente.
- **Escribe:** `clientes/<slug>/creativos/<nombre-base>/` (`datos.json`, PNG, `LEEME.md`), fila en `lote.md`,
  `estado.md` (`F3.piezas`).

## Pasos

1. **Contexto.** Lee el brief y la marca. Sin `marca.json` → pídele colores, tipografías y logo y créalo en `clientes/<slug>/marca/` partiendo del
   esquema de `plantillas/html/marca-ejemplo/marca.json` (guía: `docs/guias/estaticos.md`). Reúne el
   material real en `creativos/<nombre-base>/fuentes/`: fotos del equipo o del producto, capturas de la herramienta o
   del dashboard, resultados de clientes **con permiso**, testimonios con permiso. Nada de capturas con datos
   personales de leads o clientes finales.
2. **Concepto visual** (`disenador-estaticos`), según el brief: comparativa del proceso antes/después (del proceso,
   nunca del cuerpo), captura de resultado con contexto, cita de testimonio, lista de errores del nicho, nota estilo
   publicación, oferta clara, foto del fundador con frase. Carrusel: pasos de un proceso, caso de estudio por
   diapositivas u objeciones respondidas una a una.
3. **Textos** (`redactor-anuncios`): texto en la imagen (pocas palabras, legible en el móvil a primera vista), texto
   principal, titular y CTA, en la voz del cliente.
4. **Datos y render.** Escribe `creativos/<nombre-base>/datos.json` con las claves de la plantilla (tabla en
   `plantillas/html/README.md`; rutas de imágenes relativas al JSON, `etiqueta_ia: true` si hay imagen con IA) y
   renderiza con la marca del cliente:
   `uv run --extra render python -I herramientas/render.py png plantillas/html/estatico.html --datos clientes/<slug>/creativos/<nombre-base>/datos.json --formatos 4x5,9x16,1x1 --salida clientes/<slug>/creativos/<nombre-base>/ --nombre <nombre-base>_h1 --cliente <slug>`.
   Carrusel: `plantillas/html/carrusel.html` con `--formatos 4x5` (o `1x1`); una sola pasada saca un PNG por tarjeta
   (2–10 tarjetas con portada y cierre). Los avisos de zona segura o texto desbordado se corrigen antes de seguir.
5. **Imagen con IA** (opcional): solo si la ficha lo permite, nunca para fingir resultados, personas reales o el
   producto, y **con confirmación de coste** antes de cada generación (el coste por imagen lo muestra `/motor`).
6. **Revisión visual:** abre cada PNG y míralo a tamaño de móvil: jerarquía, contraste, erratas, zonas seguras en 9:16
   (14 % arriba, 35 % abajo y 6 % a los lados), marca correcta. Luego `critico-creativo` como espectador.
7. **Políticas** (`revisor-politicas`): afirmaciones de resultados o ingresos, antes/después, atributos personales,
   urgencia falsa, capturas de resultados sin contexto → veredicto.
8. **Entrega** en `clientes/<slug>/creativos/<nombre-base>/`: `<nombre-base>_h1_4x5.png`, `_9x16.png`, `_1x1.png`
   (carrusel: `<nombre-base>_h1_4x5_01.png`, `_02.png`…), validando el nombre de anuncio con
   `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre-base>_h1"`, y `LEEME.md` con la plantilla
   `.claude/skills/producir-video/plantilla-leeme.md` (`Vía: estatico`, `Estado: listo`, veredicto rellenado).
   Actualiza la fila en `lote.md` (`Estado` = `lista`).
9. Marca `F3.piezas` cuando haya al menos 3 conceptos listos (2 si el lote es de 2 conceptos, hasta 100 €/día;
   13/09 §A.2) con veredicto OK u OK con cambios aplicados. Siguiente paso: `/variantes` para otros hooks y `/publicar-anuncios`. La imagen única se publica con el MCP; el carrusel necesita
   `meta_ads.py` o Ads Manager (lo resuelve `/publicar-anuncios`).

## Modo `--lote`

Avisa del coste (workflow `lote-creativo`: de 3 a 5 subagentes por pieza más 3 fijos, 9–14 con 3 piezas; la imagen
con IA, si la hay, se confirma aparte) y, con un «sí», lánzalo con la herramienta Workflow y args
`{"cliente": "<slug>", "lote": "creativos/_lotes/<AAAA-MM-DD>_<lote>/", "via": "estatico"}`. Si deja órdenes
pendientes en `ORDENES.md` (imagen con IA), ejecútalas una a una con confirmación y relanza `lote-creativo` con
`{"cliente": "<slug>", "modo": "revisar", "lote": "creativos/_lotes/<AAAA-MM-DD>_<lote>/"}` para la crítica, las
políticas y el LEEME sobre las imágenes reales. Revisa tú cada pieza (pasos 6–9) antes de darla por lista.

## Reglas

- Fotos y capturas reales antes que imagen generada.
- Resultados de clientes solo con permiso y con contexto (plazo, punto de partida); nunca ingresos propios como promesa.
- Ningún dato personal en las piezas ni en `datos.json`.
