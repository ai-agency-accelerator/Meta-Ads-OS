# Estáticos, carruseles e informes en PDF

Con esta guía produces anuncios de imagen (1:1, 4:5 y 9:16), carruseles e informes de cliente en PDF con la marca de
cada cliente, sin Canva ni Figma: plantillas HTML + datos en JSON + `herramientas/render.py`.

## 1. Cuándo merece la pena un estático

- **Es la forma más barata de testear ángulos y ofertas.** En los benchmarks de 2025-2026 los estáticos de texto y
  los de producto con texto tienen el mejor *hit rate*, y su coste por compra es prácticamente igual al del vídeo
  (CPM más bajo, CTR más bajo). **[EMPIRICAL]** — `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` §1–2.
- **No lo juzgues por el CTR**: juzga por coste por resultado de la capa más baja que tengas (cita, demo, venta).
- **Testea el ángulo con un estático y escálalo con vídeo** (o al revés: lleva a un estático el gancho de un vídeo
  ganador). Alternar estático y vídeo del mismo mensaje cuenta como otra ejecución visual, no como otro concepto.
- **El carrusel no es un formato por defecto**: es el de peor *hit rate* en los benchmarks. Úsalo para contar una
  secuencia (caso de éxito, pasos, comparativa) o para catálogo. Meta admite de 2 a 10 tarjetas.
- En 2026 el copy que más pesa vive **dentro** de la imagen: en Reels y Stories el texto principal casi no se ve
  (`meta-ads-kb/03-creatividad/08-copy-de-anuncios.md`).

## 2. Instalación (una vez)

```bash
uv sync --extra render                              # instala Playwright en el entorno del proyecto
uv run --extra render playwright install chromium   # solo si no tienes Google Chrome ni Microsoft Edge
```

`render.py` usa el Chromium de Playwright y, si no está, el Chrome o el Edge que ya tengas instalado. Funciona igual en
Mac, Linux y Windows (Git Bash). Comprueba que todo está bien con el ejemplo:

```bash
uv run --extra render python -I herramientas/render.py png plantillas/html/estatico.html \
    --datos plantillas/html/ejemplos/estatico.json --marca plantillas/html/marca-ejemplo \
    --formatos 1x1,4x5,9x16 --salida /tmp/prueba-estatico
```

Si falta Playwright o un navegador, sale con código 2 y te dice el comando exacto para arreglarlo.

## 3. Prepara la marca del cliente

Cada cliente tiene su marca en `clientes/<slug>/marca/` (no se versiona; el producto no incluye ninguna marca real):

```
clientes/acme-automations/marca/
├── marca.json
├── logo.svg            # sobre fondo claro (SVG o PNG con transparencia)
├── logo-claro.svg      # versión para fondos oscuros o de color
└── fuentes/            # opcional: tipografías de la marca (.ttf, .otf, .woff2)
```

`marca.json` (todas las claves son opcionales; lo que falte se completa con una marca neutra y Montserrat):

```json
{
  "nombre": "Acme Automations",
  "colores": {"primario": "#1F4FD1", "secundario": "#0B1F3A", "acento": "#FFB020",
              "fondo": "#F7F8FB", "texto": "#0B1F3A", "texto_sobre_primario": "#FFFFFF"},
  "tipografias": {"titulos": {"familia": "Montserrat", "archivo": "fuentes/Montserrat-ExtraBold.ttf", "peso": 800},
                  "texto":   {"familia": "Montserrat", "archivo": "fuentes/Montserrat-Medium.ttf", "peso": 500}},
  "logo": {"principal": "logo.svg", "claro": "logo-claro.svg"},
  "subtitulos": {"color": "#FFFFFF", "resaltado": "#FFB020", "contorno": "#000000", "mayusculas": false},
  "cta_por_defecto": "Reserva tu diagnóstico",
  "etiqueta_ia": "Contenido generado con IA"
}
```

| Clave | Para qué sirve |
|---|---|
| `colores.primario` | Botones, realces y fondo de portada |
| `colores.secundario` | Fondos oscuros (tema `oscuro`, cierre del carrusel) |
| `colores.acento` | Detalles y botón sobre fondos oscuros; el texto del botón se elige solo (claro u oscuro) |
| `colores.fondo` y `colores.texto` | Tema claro |
| `tipografias.*.archivo` | Ruta relativa a la carpeta `marca/`. Sin archivo, se usa la familia instalada o Montserrat |
| `logo.principal` y `logo.claro` | Rutas relativas a `marca/`. Si solo hay uno, se usa en los dos casos |
| `subtitulos` | Lo usa el montaje de vídeo (cutkit) para los subtítulos quemados |
| `cta_por_defecto` | Texto del botón cuando los datos no traen `cta` |
| `etiqueta_ia` | Texto que se muestra si una pieza lleva imagen hecha con IA |

`render.py` avisa si un color no es hexadecimal, si falta un archivo o si el contraste entre texto y fondo baja de 4,5:1
(WCAG AA). La marca de ejemplo completa está en `plantillas/html/marca-ejemplo/`.

**Tipografías:** usa fuentes con licencia que permita incrustarlas en imágenes y PDF (las de Google Fonts, con licencia
OFL, lo permiten). No metas en el repositorio fuentes comerciales de un cliente: viven en su carpeta, que no se versiona.

## 4. Haz un estático

1. Escribe los datos (los textos los propone `redactor-anuncios` a partir del brief). Copia
   `plantillas/html/ejemplos/estatico.json` en la carpeta de la pieza y edítalo. Claves: `titular`, `resaltado`,
   `etiqueta`, `subtitulo`, `beneficios`, `imagen` (foto o captura **real** del producto, ruta relativa al JSON),
   `prueba`, `cta`, `pie`, `etiqueta_ia` y `estilo` (`claro`, `oscuro` o `color`). Detalle en
   `plantillas/html/README.md`.
2. Renderiza los tres formatos con el nombre del anuncio (nomenclatura del contrato: `<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook>`,
   ver `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8):

```bash
uv run --extra render python -I herramientas/render.py png plantillas/html/estatico.html \
    --datos clientes/acme-automations/creativos/2026-11-10_respuesta-lenta/datos.json \
    --formatos 1x1,4x5,9x16 --cliente acme-automations \
    --nombre 20261110_respuesta-lenta_panel-leads_estatico_h1 \
    --salida clientes/acme-automations/creativos/2026-11-10_respuesta-lenta/
```

   Sale `20261110_respuesta-lenta_panel-leads_estatico_h1_1x1.png`, `…_4x5.png` y `…_9x16.png` con el tamaño exacto
   (1080×1080, 1080×1350 y 1080×1920).
3. Lee los avisos (sección 7) y corrige hasta que no quede ninguno de zona segura.
4. Para una variante de gancho, duplica el JSON, cambia el titular y usa `_h2` en `--nombre`.

**Zonas seguras.** En 9:16 deja libre el 14 % de arriba, el 35 % de abajo y el 6 % de cada lado, y además la franja de
botones de Reels (abajo a la derecha). En 9:16 la plantilla coloca todo lo que se lee en esa zona y deja que la imagen
baje por detrás de la interfaz: lo importante de la captura, arriba. Fuente:
`meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md`. En 1:1 y 4:5 se usa un margen del
5 % **[HYPOTHESIS]**.

## 5. Haz un carrusel

```bash
uv run --extra render python -I herramientas/render.py png plantillas/html/carrusel.html \
    --datos <datos.json> --formatos 4x5 --cliente <slug> --nombre <nombre-del-anuncio> --salida <carpeta>
```

Sale un PNG por tarjeta (`<nombre>_4x5_01.png`, `_02.png`…). Estructura de datos: `portada`, `tarjetas` (lista) y
`cierre` con CTA. Úsalo para casos de éxito, pasos o comparativas, con una idea por tarjeta. En la nomenclatura, el
formato es `carrusel`.

## 6. Informe de cliente en PDF

```bash
uv run --extra render python -I herramientas/render.py pdf plantillas/html/informe-cliente.html \
    --datos clientes/clinica-sonrisa/informes/2026-11-03_datos.json --cliente clinica-sonrisa \
    --salida clientes/clinica-sonrisa/informes/2026-11-03_informe-octubre.pdf
```

- `/informe-cliente` y `gestor-cliente` preparan el JSON a partir del informe semanal o mensual: veredicto, resumen,
  KPIs con su lectura (buena, mala o neutra), embudo, tablas de campañas y anuncios, decisiones con fecha de evaluación,
  próximos pasos y notas de medición.
- Indica siempre el periodo, la comparación y la **ventana de atribución**.
- Nunca pongas datos personales (nombres, emails o teléfonos de leads): solo agregados, campañas y anuncios.
- Con `--cliente`, la portada lleva la marca del cliente; para un informe con la marca de tu agencia, usa
  `--marca clientes/<tu-slug>/marca` y escribe el nombre de tu agencia en `agencia`.

## 7. Cómo leer los avisos

Con `--json` tienes el informe completo (archivos, tamaños y avisos). Los avisos no paran el render:

| Aviso | Qué hacer |
|---|---|
| `«titular» fuera de la zona segura` | Acorta el texto o quita un elemento: la interfaz de Meta lo tapará |
| `pisa la franja de botones de Reels` | Aleja ese elemento de la esquina inferior derecha en 9:16 |
| `«contenido» reducido al 80 %` | El texto se ha encogido para caber. Por debajo del 85 % suele ser señal de que sobra texto |
| `no cabe ni al 72 %` | Hay que recortar: quita el subtítulo, un beneficio o la imagen |
| `Falta el dato «x»` | La plantilla usa una clave que tus datos no traen |
| `imagen que no carga` / `No encuentro el logo` | La ruta es relativa al JSON de datos (o a `marca/` en el caso del logo) |
| `Contraste bajo` | Cambia `texto` o `texto_sobre_primario` en `marca.json` |
| `N tarjetas: un carrusel de Meta admite de 2 a 10` | Ajusta el número de tarjetas |

## 8. Del render a la entrega

1. `/producir-estatico` coordina el proceso: `disenador-estaticos` elige plantilla y composición, `redactor-anuncios`
   escribe los textos y `render.py` produce los PNG.
2. Revisión antes de entregar: `critico-creativo` mira la pieza como un espectador (primeros segundos de atención,
   legibilidad en el móvil, zonas seguras, coherencia con la landing, claridad de la oferta) y `revisor-politicas`
   revisa afirmaciones y copy (`/revisar-anuncio`; patrones en
   `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`).
3. Entrega en `clientes/<c>/creativos/<AAAA-MM-DD>_<slug>/` con los PNG, el JSON de datos y un `LEEME.md` con QA, crítica,
   coste, afirmaciones usadas, etiqueta de IA y **veredicto de políticas**.
4. `/publicar-anuncios` sube las imágenes en pausa y con las mejoras automáticas desactivadas. Revisa sobre todo
   «Enhance media text (AI)», que reescribe el texto de dentro de la imagen y puede contradecir una oferta o una
   afirmación legal (`meta-ads-kb/03-creatividad/08-copy-de-anuncios.md`).

## 9. Imágenes con IA

- Prioriza siempre fotos y capturas **reales** del producto: son más creíbles y no se deforman.
- Una imagen generada con IA (con el motor, ver `docs/guias/video-ia.md`) **gasta dinero**: pide antes la
  confirmación del coste. La IA solo para fondos, escenas u objetos, nunca para inventar resultados, testimonios ni
  personas que pasen por clientes.
- Si la pieza lleva imagen hecha con IA, pon `"etiqueta_ia": true` en los datos y decláralo en el `LEEME.md`. Las
  reglas de declaración de contenido generado están en `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md`.

## 10. Crea tus plantillas

Copia `plantillas/html/estatico.html` a la carpeta del cliente o a `plantillas/html/` y adáptala. Reglas:

- Todo lo que se lee lleva `data-zona-segura="nombre"`; el contenedor que puede encoger su texto, `data-ajustar` (y los
  tamaños con `calc(var(--escala, 1) * 80px)`); cada imagen de un carrusel, `data-tarjeta`.
- Usa las variables CSS de la marca (`var(--color-primario)`, `var(--fuente-titulos)`…), nunca colores fijos de un
  cliente.
- Nada externo: ni Google Fonts ni imágenes de internet. Todo local o en los datos con `|uri`.
- `<meta name="formatos" content="1x1,4x5">` limita los formatos que admite.

La sintaxis completa (secciones, listas, filtros) está en `plantillas/html/README.md` y en la cabecera de
`herramientas/render.py`.

## 11. Problemas frecuentes

| Problema | Solución |
|---|---|
| Código 2 «Falta Playwright» | `uv sync --extra render` y ejecuta con `uv run --extra render python -I herramientas/render.py …` |
| Código 2 «No puedo abrir ningún navegador» | `uv run --extra render playwright install chromium` o instala Chrome o Edge |
| Código 1 | Plantilla, datos o marca que no existen, JSON mal formado o formato que la plantilla no admite: lee el mensaje |
| La tipografía no es la de la marca | Revisa `tipografias.*.archivo` (relativa a `marca/`) o instala la familia en el sistema |
| El logo sale pixelado | Usa SVG o un PNG de al menos 600 px de ancho |
| En Windows las rutas fallan | Usa barras `/` y comillas si hay espacios: `"clientes/mi cliente/…"` |
| Un PDF corta una tabla | Es normal entre páginas; las filas no se parten y la cabecera se repite |
