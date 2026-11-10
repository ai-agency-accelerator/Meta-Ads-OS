# Plantillas HTML de estáticos e informes

Se renderizan con `herramientas/render.py` (Playwright, extra `render`). Guía completa: `docs/guias/estaticos.md`.

```bash
uv run --extra render python -I herramientas/render.py png plantillas/html/estatico.html \
    --datos plantillas/html/ejemplos/estatico.json --formatos 1x1,4x5,9x16 \
    --salida clientes/<slug>/creativos/<AAAA-MM-DD>_<slug-pieza>/ --cliente <slug>
uv run --extra render python -I herramientas/render.py pdf plantillas/html/informe-cliente.html \
    --datos <datos.json> --salida clientes/<slug>/informes/<AAAA-MM-DD>_informe.pdf --cliente <slug>
```

| Archivo | Qué es |
|---|---|
| `estatico.html` | Anuncio de una imagen en 1:1, 4:5 y 9:16 |
| `carrusel.html` | Carrusel 1:1 o 4:5: portada + tarjetas + cierre con CTA (un PNG por tarjeta) |
| `informe-cliente.html` | Informe de cliente en PDF A4 |
| `ejemplos/*.json` | Datos de ejemplo (empresas y cifras ficticias) |
| `marca-ejemplo/` | Marca ficticia (Acme Automations) con el esquema de `marca.json` |
| `fuentes/` | Montserrat (SIL Open Font License 1.1, ver `OFL-Montserrat.txt`): tipografía por defecto |

Todas las rutas de imágenes de los datos son **relativas al JSON de datos**. La marca (colores, tipografías, logo, CTA
por defecto y etiqueta de IA) sale de `clientes/<slug>/marca/marca.json` con `--cliente`, o de `--marca <ruta>`.

## Datos de `estatico.html`

| Clave | Obligatoria | Qué es |
|---|---|---|
| `titular` | sí | Mensaje principal (≤ 12 palabras funciona mejor) |
| `resaltado` | no | Continuación del titular en color de realce |
| `etiqueta` | no | Antetítulo corto (a quién va dirigido) |
| `subtitulo` | no | Una o dos frases de apoyo |
| `beneficios` | no | Lista de 2–4 beneficios con check (mejor sin `imagen`) |
| `imagen` | no | Foto o captura **real** del producto; `imagen_cubrir: true` la recorta para llenar el hueco; `imagen_alt` |
| `prueba` | no | `{"cifra": "2 min", "texto": "de primera respuesta"}` |
| `cta` | no | Texto del botón (si falta, `cta_por_defecto` de la marca) |
| `pie` | no | Texto legal o aclaración breve |
| `etiqueta_ia` | no | `true` si la imagen está hecha con IA: muestra `etiqueta_ia` de la marca |
| `estilo` | no | `claro` (por defecto), `oscuro` (fondo secundario) o `color` (fondo primario) |

En 9:16 la imagen baja por detrás de la interfaz de Stories y Reels: lo que deba leerse de la captura, arriba.

## Datos de `carrusel.html`

- `portada`: `titular` (obligatorio), `etiqueta`, `subtitulo`, `desliza` (por defecto «Desliza»).
- `tarjetas`: lista de `{titulo, texto, cifra, cifra_texto, imagen, imagen_alt}`; solo `titulo` es obligatorio.
- `cierre`: `titular`, `texto`, `cta` (por defecto, el de la marca).
- Meta admite de 2 a 10 tarjetas en total (portada y cierre incluidos).

## Datos de `informe-cliente.html`

- `titulo`, `cliente`, `agencia`, `fecha`, `etiqueta`, `periodo` (`desde`, `hasta`, `comparado_con`), `ventana_atribucion`.
- `veredicto` (una frase) y `resumen` (lista de 3–5 frases).
- `kpis`: `{nombre, valor, variacion, tendencia: sube|baja|igual, lectura: buena|mala|neutra, nota}`. La `lectura`
  colorea la variación (un CPL que sube es `mala`).
- `embudo` (+ `embudo_titulo`): `{etapa, valor, pct}` con `pct` de 0 a 100.
- `tablas` (+ `tablas_titulo`): `{titulo, columnas: [...], filas: [[...]], nota}`; la primera columna es texto y el
  resto se alinea a la derecha.
- `decisiones`: `{decision, motivo, metrica, fecha_evaluacion}` (las mismas que el change log).
- `proximos_pasos`: `{accion, responsable, fecha}`; `medicion`: lista de notas de medición.
- Sin datos personales: solo agregados, nombres de campaña y de anuncio.

## Crear tu propia plantilla

Sintaxis (sin dependencias): `{{clave}}`, `{{a.b}}`, `{{.}}`, `{{#lista}}…{{/lista}}` (con `{{@indice}}` y
`{{@total}}`), `{{^clave}}…{{/clave}}`, `{{#lista?}}…{{/lista?}}` (solo comprueba que no esté vacía) y filtros
`|uri`, `|mayusculas`, `|num`, `|eur`, `|pct`. Disponibles siempre: `marca.*`, `formato.*` y `hoy`.

`render.py` inyecta las variables CSS `--color-primario`, `--color-secundario`, `--color-acento`, `--color-fondo`,
`--color-texto`, `--color-texto-sobre-primario`, `--color-texto-sobre-acento`, `--color-texto-sobre-secundario`,
`--fuente-titulos`, `--fuente-texto`, `--peso-titulos`, `--peso-texto`, `--ancho`, `--alto` y la zona segura
`--zs-arriba`, `--zs-abajo`, `--zs-izquierda`, `--zs-derecha`. Marca con `data-zona-segura="nombre"` todo lo que deba
leerse, con `data-ajustar` el contenedor cuyo texto puede encogerse (usa `calc(var(--escala, 1) * 80px)` en los
tamaños) y con `data-tarjeta` cada imagen de un carrusel. `<meta name="formatos" content="1x1,4x5">` limita los
formatos.
