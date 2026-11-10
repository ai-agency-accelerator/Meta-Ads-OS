# Páginas de captación (`paginas.py`)

Plantillas y referencia técnica de las páginas que genera `herramientas/paginas.py`:
- landing;
- diagnóstico interactivo;
- reserva de llamada;
- gracias;
- webinar.

Salen en HTML estático, con la marca del cliente, rápidas en el navegador interno de Instagram y Facebook, con el
consentimiento antes del píxel y el tracking completo (contrato §16 y §17). El OS **nunca despliega**: tú subes la
carpeta a tu hosting o pegas el fragmento en GHL.

Para el día a día no hace falta leer esto entero. Las skills `/iman-de-leads` (diseña la oferta y el diagnóstico) y
`/construir-landing` (genera, valida y te guía para publicar) escriben el config por ti. Las guías para personas son
`docs/guias/iman-de-leads.md` y `docs/guias/construir-landing.md`.

## Archivos

| Archivo | Qué es |
|---|---|
| `landing.html`, `diagnostico.html`, `reserva.html`, `gracias.html`, `webinar.html` | Una plantilla por tipo de página |
| `_inicio.html`, `_fin.html` | Cabecera (metas, enlace «Saltar al contenido», logo) y pie (legal, banner de cookies, scripts) |
| `_formulario.html`, `_secciones.html`, `_campo-diag.html`, `_grupo-item.html`, `_video.html`, `_reserva-cabecera.html`, `_reserva-detalles.html`, `_reserva-calendario.html` | Parciales (`{{> nombre}}`) |
| `paginas.css` | Estilos propios con *tokens* (`--c-…`, `--f-…`) que se sustituyen por los de la marca. Se incrusta minificado |
| `paginas.js` | Runtime común, sin dependencias (~35 KB legible, ~11 KB comprimido): atribución, consentimiento, píxel, formularios, webhook, calendario, barra de CTA, vídeo bajo demanda |
| `diagnostico.js` | Diagnóstico: pasos, fórmulas, resultado, recomendación y eventos (~10 KB comprimido). Necesita `paginas.js` |
| `ejemplos/acme-embudo.json` | Embudo completo: landing → diagnóstico → reserva → gracias (Acme Automations) |
| `ejemplos/nimbo-webinar.json` | Webinar → gracias con calendario, varias zonas y WhatsApp (Nimbo) |
| `ejemplos/acme-vsl-calendario.json` | Captación → VSL con calendario → gracias: los datos primero y, después, el vídeo con el calendario debajo (Acme Automations) |

Las plantillas usan la sintaxis de `herramientas/render.py` (`{{campo}}`, `{{#lista}}…{{/lista}}`, `{{#campo?}}` si
existe y no está vacío, `{{^campo}}` si no existe). Todo texto del config se escapa. El JSON de configuración que lee el
JS va en `<script type="application/json" id="pos-config">`, con `<`, `>` y `&` escapados.

## Uso

```bash
python3 -I herramientas/paginas.py generar todas --config clientes/acme/planes/2026-11-10_diagnostico.json \
    --salida clientes/acme/paginas/2026-11-10_diagnostico/ --cliente acme
python3 -I herramientas/paginas.py probar --config clientes/acme/planes/2026-11-10_diagnostico.json
python3 -I herramientas/paginas.py validar clientes/acme/paginas/2026-11-10_diagnostico/
```

- `generar <landing|diagnostico|reserva|gracias|webinar|todas>`: escribe las páginas y `recursos/` (JS, logo,
  imágenes, vídeos, fuentes y `.ics`). No borra nada; solo sobrescribe los archivos que genera.
  - `--cliente SLUG` toma la marca de `clientes/<slug>/marca/marca.json`, y `--marca RUTA` la de otra carpeta. Sin
    ninguna de las dos se usa `marca` del config y, si falta, una marca neutra.
  - `--en-linea` mete también el JS en cada HTML.
  - `--fragmento-ghl` escribe además `ghl/<página>.html` para el elemento «Custom code» de GHL.
- `probar`: calcula el diagnóstico con los `escenarios` del config (o con `--respuestas <json>`) y dice qué nivel sale.
  Código 1 si alguno no da el `espera_nivel`.
- `validar <carpeta>`: comprueba las páginas generadas (ver «Qué comprueba `validar`»). Código 1 si hay errores.
- Todos admiten `--json`. Códigos de salida (contrato §9): 0 ok, aunque haya avisos; 1 error del usuario o validación
  con errores; 2 error de configuración o de disco.

## El config

```json
{
  "version": 1,
  "marca": {"cliente": "acme"},
  "sitio": {"nombre": "…", "url": "https://…", "legal": {…}},
  "tracking": {"pixel_id": "…", "webhook": {"url": "https://…"}},
  "paginas": {"landing": {…}, "diagnostico": {…}, "reserva": {…}, "gracias": {…}}
}
```

Las rutas de archivos (imágenes, vídeos, `marca.ruta`) son relativas al config. Los enlaces aceptan `https://…`,
rutas relativas, `#ancla`, `mailto:`, `tel:` o `@tipo` (ver «Enlaces entre páginas»). `javascript:` y `data:` se
rechazan.

### `marca`

`{"cliente": "<slug>"}` o `{"ruta": "<carpeta con marca.json>"}`. El formato de `marca.json` es el de
`plantillas/html/README.md`. De ahí salen:
- colores: primario, texto sobre primario, fondo, texto, acento y secundario;
- tipografías: una fuente propia solo si `marca.json` trae el archivo (mejor `.woff2`, que se precarga; un `.ttf` u
  `.otf` da aviso de peso); si no, la pila del sistema, que es lo más rápido;
- el logo.

Los tokens se recalculan para que el contraste cumpla:
- texto ≥ 4,5:1;
- texto secundario ≥ 4,6:1;
- borde de los campos ≥ 3:1.

Si el texto de los botones no llega a 4,5:1 sobre el primario, se cambia y se avisa.

### `sitio`

| Clave | Para qué |
|---|---|
| `nombre`, `url` (https), `idioma` (`es`) | Título, enlaces absolutos y `og:url` |
| `moneda` | Código ISO de 3 letras de los `value` de los eventos y de las cifras en euros del diagnóstico (el símbolo de `eur`/`moneda`). Si falta, la de la ficha del cliente (con `--cliente` o `marca.cliente`); si tampoco, `EUR`. Si el config y la ficha no coinciden, `generar` avisa |
| `contacto` | Alternativa que se ofrece si el envío falla («o escríbenos a…») |
| `legal.responsable`, `legal.finalidad` | Primera capa informativa de protección de datos bajo cada formulario |
| `legal.privacidad`, `legal.aviso_legal`, `legal.cookies` | Enlaces del pie y del banner |
| `favicon` | Archivo local (si no, ninguno: no se pide `/favicon.ico`) |
| `recursos_url` | URL pública de `recursos/` para los fragmentos de GHL (p. ej. la biblioteca de medios) |

### `tracking`

| Clave | Por defecto | Para qué |
|---|---|---|
| `pixel_id` | — | Sin él no hay eventos del navegador («solo servidor»). El banner sigue saliendo si el webhook manda a la CAPI con `base_legal_servidor: consentimiento`: sin «Aceptar», `enviar_a_meta` sería siempre `false` |
| `eventos_navegador` | `true` | `false` si todos los eventos los manda tu servidor |
| `webhook.url` | — | Adónde va cada envío (n8n, Make, tu backend o el *Inbound Webhook* de GHL). Sin URL, **modo prueba**: no se envía nada y la página lo dice |
| `webhook.modo` | `json` | `json` (`Content-Type: application/json`, necesita CORS) o `texto` (`no-cors`, `text/plain`: para receptores sin CORS; no se puede leer la respuesta) |
| `webhook.timeout_ms` | `8000` | Tiempo máximo de espera del envío |
| `base_legal_servidor` | `consentimiento` | `consentimiento`: sin «Aceptar», el envío no lleva identificadores de Meta. `interes_legitimo`: lleva `event_id`, `fbclid` y `fbc` aunque no acepte (nunca `fbp`) `[CONTESTED]`: valídalo con tu asesor |
| `consentimiento.banner` | `true` | `false` si usas tu propio gestor: debe llamar a `PaginasOS.consentimiento('si'\|'no')`. Vale también en «solo servidor»: sin esa llamada nadie puede aceptar, y `validar` lo recuerda (`consentimiento.externo`) |
| `consentimiento.titulo`, `.texto`, `.aceptar`, `.rechazar` | textos neutros | Textos del banner. «Aceptar» y «Rechazar» tienen el mismo peso visual |
| `consentimiento.caducidad_dias` | `180` | Cuándo se vuelve a preguntar |
| `prefill_reserva` | `true` | Rellena el calendario con nombre y email del formulario (vía `sessionStorage`, se borra al usarlo) |
| `content_name` | — | Etiqueta de campaña o edición (p. ej. `webinar-conciliacion-2026-12-03`). Va en los datos de cada evento del navegador y en el envío, para separar ediciones en Meta |

### Claves comunes de cada página

| Clave | Para qué |
|---|---|
| `archivo` | Nombre del HTML (por defecto `index.html` para la landing y `<tipo>.html` para el resto; con una sola página en el config, `index.html`, para que `../gracias/` funcione en cualquier hosting) |
| `ruta_publica` | Cómo se llama la página una vez publicada (p. ej. `/diagnostico` o `https://acme.example/diagnostico`), si no coincide con `archivo` |
| `titulo_seo`, `descripcion_seo`, `og_imagen` | `<title>`, `description` y la imagen al compartir (necesita `sitio.url`) |
| `noindex` | Por defecto `true` en reserva y gracias |
| `content_name` | Igual que en `tracking`, solo para esta página |

### `landing`

- **`hero`:**
  - `titular` (obligatorio: repite la promesa del anuncio), `entradilla`, `prueba` (una línea verificable);
  - `cta` y `cta_secundario`, cada uno `{texto, href}`;
  - `media`, uno de estos tres:

    | Tipo | Claves |
    |---|---|
    | `imagen` | `src`, `alt` (obligatorio; `""` si es decorativa), `ancho`, `alto`. Si faltan las medidas, se leen del archivo |
    | `video` | `proveedor` `youtube`, `vimeo` o `mp4`; `id` o `src`; `miniatura` propia; `subtitulos` `.vtt`; `titulo`; `duracion`; `vertical`. No se carga nada de terceros hasta que se pulsa |
    | `arranque` | La primera pregunta del diagnóstico (de opciones) como botones en el hero: cada uno abre el diagnóstico con esa respuesta marcada (`?r_<id>=<n>`). `ayuda` y `pie` opcionales |
- **`secciones`:** lista; ver la tabla de abajo.
- **`barra_cta`:** por defecto, la del hero. Es una barra fija en móvil que aparece al pasar el hero y se esconde
  sobre el formulario y el cierre. `false` la quita; `{texto, href}` pone otra.
- **`cabecera_cta`:** por defecto `true`, el botón en la cabecera.

**Secciones** (`tipo` y sus claves; todas admiten `id` para el ancla, `titulo`, `entradilla` y `oscura`):

| Tipo | Claves |
|---|---|
| `dolor`, `lista` | `puntos` (textos) |
| `pasos` | `pasos` `[{titulo, texto}]` |
| `beneficios` | `tarjetas` `[{titulo, texto}]`, `columnas` (2 o 3) |
| `casos` | `casos` `[{cifra, cifra_texto, cita, autor, cargo}]`, `aviso`. Con `"ejemplo": true` se pinta un aviso y `validar` da error hasta que pongas casos reales con permiso |
| `logos` | `logos` `[{src, alt}]` |
| `para_quien` | `si`, `no`, `titulo_si`, `titulo_no` |
| `oferta` | `incluye_titulo`, `incluye`, `precio`, `precio_nota`, `garantia`, `cta`, `no_incluye_titulo`, `no_incluye` |
| `ponentes` | `ponentes` `[{nombre, cargo, bio, foto}]` |
| `video` | `video` (como en el hero) |
| `texto` | `parrafos` |
| `faq` | `preguntas` `[{pregunta, respuesta}]` |
| `formulario` | `puntos` y `formulario` (ver «Formularios»). El ancla por defecto es `#registro` |
| `cierre` | `texto`, `cta` (sección oscura por defecto) |

Si un texto de la página tiene frases de promesa («garantizado», «ahorrarás», «100 %»…), `generar` avisa: pásalo por
`revisor-politicas`.

### Formularios

```json
{"campos": ["nombre", "email", "empresa", {"id": "telefono", "requerido": false}],
 "boton": "Enviar", "evento": "Lead", "siguiente": "@reserva", "marketing": true}
```

- **Campos predefinidos**, con su `autocomplete` y teclado correctos (el autorrelleno del navegador de Meta los usa):
  `nombre`, `apellidos`, `email`, `telefono`, `empresa`, `cargo`, `web`, `mensaje`. Cualquiera se puede ajustar con un
  objeto (`{"id": "telefono", "requerido": false, "ayuda": "…"}`).
- **Campos propios:** `{"id", "tipo", "etiqueta", "requerido", "ayuda", "placeholder", "maxlength", "opciones"}`.
  - `tipo`: `texto`, `email`, `tel`, `url`, `numero`, `select` (con `opciones`), `textarea` o `casilla`.
  - Están reservados los ids que empiezan por `acepta_` y los nombres de los campos del envío (`version`, `origen`,
    `momento`, `ref`, `utm_*`, `ad_id`, `event_id`, `enviar_a_meta`, `fbp`… y la trampa `web2`): pisarían los
    metadatos. `generar` los rechaza.
  - En `numero`, la persona puede escribir como escribe: «1.200», «1.500,50», «1 200» o «0,175». Se lee igual en la
    página y en `paginas.py` (`num_humano`), con la regla de `_comun.numero()`.
- **Obligatorio:** al menos `email` o `telefono` (el CRM los necesita para crear el contacto).
- **`evento`:** el evento del navegador y del servidor (`Lead` por defecto; `CompleteRegistration` por defecto en el
  webinar). Lleva un `event_id` nuevo por envío, que viaja también al webhook.
- **`siguiente`:** adónde va después. Sin él, se queda en la página con `mensaje_ok`.
- **`tipo_envio`:** etiqueta del envío para el receptor (`lead`, `diagnostico`, `registro_webinar`…).
- **`marketing`:** casillas de comunicaciones, siempre opcionales y sin marcar:
  - `true` (por defecto): una casilla de email (`acepta_comunicaciones`);
  - un texto: esa casilla con otro texto;
  - `false`: ninguna;
  - una lista `[{"id": "acepta_whatsapp", "texto": "…"}, …]`: una casilla por canal.

  Los recordatorios del evento al que alguien se inscribe forman parte de lo que pidió. Lo que necesita su propia
  casilla es lo demás: novedades y, en WhatsApp, cualquier mensaje.
- **Antispam:** un campo trampa invisible (`web2`) y un mínimo de 0,8 s entre abrir y enviar. Un bot «envía» sin que
  salga nada ni se dispare ningún evento.
- Debajo del botón va la primera capa de protección de datos (responsable, finalidad, legitimación, destinatarios,
  derechos y enlace a privacidad). Cámbiala con `legal`.

### `diagnostico`

El diagnóstico es la oferta de entrada que da valor y precualifica. Va paso a paso, calcula con supuestos visibles y
editables, recomienda con honestidad y termina en la reserva.

| Clave | Qué es |
|---|---|
| `nombre`, `intro` | `intro`: `titulo`, `entradilla`, `promesas` (lista), `boton`, `duracion` (por defecto «Son N preguntas y tardas unos M minutos»), `nota`. `"intro": false` empieza directamente por la primera pregunta |
| `preguntas` | Lista (4–7 recomendado `[HYPOTHESIS]`). Cada una lleva `id`, `pregunta`, `tipo`, `ayuda` y `corta` (etiqueta breve para el resumen) |
| `supuestos` | `[{id, etiqueta, valor, formato, unidad, explicacion, fuente, editable, visible}]`. Se enseñan bajo el resultado y, salvo `editable: false`, la persona los cambia y todo se recalcula. Di siempre de dónde sale el valor |
| `calculos` | `[{id, etiqueta, formula, formato, unidad, redondeo, explicacion, mostrar}]`, en orden: cada fórmula puede usar respuestas, supuestos y cálculos anteriores |
| `resultado` | `principal` (el cálculo grande), `etiqueta`, `incertidumbre` (0,25 = rango ±25 %), `desglose` (ids), `aviso`, `titulo_supuestos`, `supuestos_abiertos` |
| `niveles` | La recomendación: `[{id, tono, si, titulo, texto, cta, cta_secundario}]`. Gana el primero cuyo `si` se cumple; el último, sin `si`, es el de por defecto. `tono`: `bajo`, `medio` o `alto`. En `titulo` y `texto`, `{id}` pone el valor formateado, y `{id_min}` y `{id_max}` los extremos del rango |
| `valor_evento` | `{nivel: euros}`: `value` de `DiagnosticoCompletado` = **valor esperado del lead** (contribución × probabilidad de ganar), nunca el ahorro del cliente `[HYPOTHESIS]` |
| `cualificado` | `{"activo": true, "niveles": ["alto"]}` dispara también `LeadCualificado`. Por defecto no: la cualificación la marca el comercial en el CRM (contrato §16) |
| `captura` | `antes` (por defecto: preguntas → datos → resultado) o `despues` (preguntas → resultado → datos para reservar). En los dos, `Lead` sale **al enviar los datos de contacto**, sea cual sea el paso en que se piden. No hay variante que pida el contacto en el primer paso (antes de las preguntas) |
| `formulario` | Como en «Formularios». Por defecto: nombre, email, empresa y teléfono |
| `escenarios` | `[{nombre, respuestas, supuestos, espera_nivel}]`: casos de prueba para `probar` y `generar` |

**Tipos de pregunta:**

| Tipo | Claves | Valor en las fórmulas |
|---|---|---|
| `opciones` | `opciones` `[{etiqueta, valor}]`, `columnas` (2) | el `valor` de la opción elegida |
| `numero` | `min`, `max`, `paso`, `defecto`, `unidad`. Admite coma decimal y botones − y + | el número |
| `texto` | `placeholder`, `maxlength`. Opcional por defecto | el texto (para `mayor` o los mensajes) |
| `grupo` | `campos` (de tipo `opciones`, `numero` o `texto`), `etiqueta_item`, `min_items`, `max_items`, `inicial`, `texto_anadir` | lista de elementos, solo dentro de `suma`, `media`, `cuenta` y `mayor` |

**Formatos:** `numero`, `eur` (o `moneda`), `horas`, `pct` (el 0,8 se escribe y se enseña como 80 %), `meses` y
`texto`. Un valor que no se puede calcular se enseña como «—».

**Diagnóstico honesto.** Al menos un nivel de tono `bajo` («hoy no te compensa contratarnos»), con algo útil a cambio
(guía, plantilla, «vuelve cuando crezca el volumen»). Si falta, `generar` avisa. El ejemplo de Acme sigue la calculadora
de `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §4.3:

| Veredicto | Condición |
|---|---|
| no compensa | ahorro neto bajo el umbral, o más de 18 meses de retorno |
| dudoso, «empieza por una tarea» | 12–18 meses |
| caso claro, «hay proyecto» | 12 meses o menos |

El umbral, la inversión y el mantenimiento se enseñan sin dejar editarlos (`"editable": false`), para que nadie
«compre» el sí bajando la inversión. Los números del config (`valor`, `min`, `defecto`, `valor_evento`…) admiten
también «1.200» o «0,6».

### Fórmulas

Las evalúan dos intérpretes propios, sin `eval`: `paginas.py` al generar y `diagnostico.js` en la página. Dan lo mismo,
y lo comprueban los vectores compartidos de `tests/herramientas/paginas_vectores.json`. `generar` comprueba cada
fórmula antes de escribir nada: variables que existen, grupos bien usados y número de argumentos.

- **Números:** `12`, `0.8` (punto decimal en la fórmula).
- **Operadores:** `+ - * / %`, `^` (potencia, asociativa por la derecha), comparaciones `< <= > >= == !=`, lógicos
  `y`/`and`, `o`/`or`, `no`/`not`. Una comparación vale 1 o 0.
- **Funciones:**

  | Función | Qué hace |
  |---|---|
  | `min(…)`, `max(…)` | El menor o el mayor de los valores |
  | `abs(x)` | Valor absoluto |
  | `redondear(x, decimales)` | Redondeo comercial (0,5 hacia arriba) |
  | `limitar(x, minimo, maximo)` | Recorta x al intervalo |
  | `si(condicion, si_verdadero, si_falso)` | Elige un valor según la condición |
  | `suma(grupo, expresion)`, `media(grupo, expresion)` | Suma o media de la expresión en cada elemento del grupo |
  | `cuenta(grupo)` | Número de elementos del grupo |
  | `mayor(grupo, expresion, campo)` | El `campo` del elemento con la expresión más alta (p. ej. el nombre de la tarea que más horas come) |
- **Vacíos:**
  - dividir por 0 o hacer cuentas con un texto da vacío («—»);
  - una comparación con un vacío da 0;
  - `min` y `max` ignoran los vacíos.
- **Palabras reservadas:** no se pueden usar como id `y`, `o`, `no`, `and`, `or`, `not` ni los nombres de las
  funciones.

### `reserva`

| Clave | Qué es |
|---|---|
| `calendario.proveedor` | `ghl` (por defecto), `calendly`, `calcom` u `otro` |
| `calendario.url` | La del widget de reserva (https). Sin ella, la página enseña un aviso de modo prueba |
| `calendario.parametros` | Cómo se llaman en la URL del calendario los datos que se rellenan. Por defecto, en GHL `first_name`, `last_name`, `email` y `phone`, y en Calendly y Cal.com `name` y `email`. GHL: sin verificar, compruébalo |
| `calendario.prefill`, `calendario.titulo`, `calendario.alto` | Rellenar sí o no; título del iframe; alto (`46rem`) |
| `calendario.origen` | Origen del que se aceptan los mensajes del iframe (por defecto `https://calendly.com` con Calendly) |
| `evento_schedule` | `servidor` (por defecto con GHL: lo manda el workflow «cita reservada» con CAPI) o `navegador` (solo Calendly, que avisa al reservar con `calendly.event_scheduled`) |
| `notificar_webhook` | Con `navegador`, además envía la reserva al webhook con el mismo `event_id` |
| `siguiente` | Adónde ir al detectar la reserva (por defecto `@gracias`) |
| `titulo`, `entradilla`, `puntos_titulo`, `puntos`, `anfitrion` `{nombre, cargo, foto}`, `nota` | Textos de la página |
| `mensajes_nivel` | `{nivel: texto}`: un mensaje distinto según el resultado del diagnóstico (`?nivel=` en la URL) |
| `video` | Opcional: el VSL, con las mismas claves que el vídeo del hero (`proveedor` `youtube`, `vimeo` o `mp4`; `id` o `src`; `miniatura` propia; `subtitulos` `.vtt`; `titulo`; `duracion`; `vertical`). No se carga nada de terceros hasta que se pulsa. Con vídeo, la página pasa a una columna: titular y entradilla → vídeo → calendario → `puntos`, `anfitrion` y `nota`, para que el calendario se vea sin terminar el vídeo (`meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` §4.4). El `titulo` por defecto pasa a ser «Antes de elegir hora, mira este vídeo» |
| `texto_calendario` | Texto que va encima del calendario. Por defecto, con `video`, «Elige día y hora para la llamada»; sin vídeo, ninguno |

**Embudo «Captación → VSL con calendario»** (`ejemplos/acme-vsl-calendario.json`): `landing` con el formulario de
captación (`siguiente: "@reserva"`) → `reserva` con `video` y `texto_calendario` → `gracias`. `Lead` sale al enviar los
datos de contacto en la captación; la reserva no lo repite. La cita reservada (`Schedule`) la manda por defecto el
workflow «cita reservada» de GHL por CAPI (`evento_schedule: "servidor"`). Para que quien no encaja no vea el calendario,
mira «Sin verificar» en `docs/guias/construir-landing.md`.

La URL del calendario recibe también toda la atribución: las `utm_*`, `campaign_id`, `adset_id`, `ad_id` (o
`utm_content` si es un número), `placement`, `site` y `ref`, y el `fbclid` solo si `enviar_a_meta` lo permite. Así, la
cita queda atribuida en el CRM aunque la persona llegue directa a esta página.

### `gracias`

| Clave | Qué es |
|---|---|
| `titulo`, `texto`, `pasos_titulo`, `pasos` `[{titulo, texto}]` | Qué pasa ahora y qué preparar (la «tarea previa») |
| `video` | Vídeo corto («qué pasará en la llamada»), como en el hero |
| `recurso` | Un botón principal `{texto, href}` |
| `botones` | Más botones `[{texto, href}]`. Un enlace a `https://wa.me/…` abre WhatsApp en otra pestaña («Confírmame por WhatsApp») |
| `anadir_calendario` | `true` toma `paginas.webinar.evento` del mismo config. Con un objeto de evento (las mismas claves que `webinar.evento`), sirve cuando gracias se genera con su propio config. Crea el `.ics` y el enlace de Google Calendar |
| `evento` | Evento del navegador al llegar (p. ej. `Schedule` si nada más lo manda). Vacío por defecto. Nunca `Lead`: ya lo disparó el formulario. Con las cookies aceptadas, una recarga no lo repite |
| `notificar_webhook` | Envía también ese evento al webhook con el mismo `event_id` |

### `webinar`

- **`hero`**, como en la landing, con el formulario de registro a la derecha (debajo en móvil).
- **`evento`:**
  - `titulo`, `descripcion` y `plataforma`;
  - `inicio`, en ISO, mejor sin desfase: `2026-12-03T18:00:00`. El desfase se calcula para esa fecha con la zona,
    horario de verano incluido. Si lo escribes (`+01:00`), tiene que ser el de esa fecha: si no, `generar` para y te
    dice el bueno;
  - `zona_horaria`, el nombre IANA (`Europe/Madrid`, `America/Mexico_City`…). Sin ella, la de la ficha (con
    `--cliente`) y, si no, `Europe/Madrid`;
  - `duracion_min` y `zona`, el texto que se enseña («Hora peninsular española»). Sin `zona`, sale de `zona_horaria`.
    Con un `zona` propio y sin `zona_horaria`, no se puede comprobar el desfase: `generar` avisa;
  - `enlace`, que va al `.ics`;
  - `otras_zonas`: `[{"nombre": "Canarias", "zona": "Atlantic/Canary"}]`, la hora en cada país, calculada con su
    zona IANA y su horario de verano.

  Debajo de la fecha, la página dice cuántos días faltan, por días de calendario en la zona del evento («Es hoy.»,
  «Es mañana.», «Faltan 3 días.»), y nada una vez empezado.
- **`formulario`:** como en «Formularios». Por defecto lleva nombre, email y empresa, el evento
  `CompleteRegistration` (el registro no es un lead: así se separa en Meta) y `siguiente` a `@gracias`.
- **`secciones`:** como en la landing. Lo típico:
  - `lista` con lo que van a aprender;
  - `ponentes`;
  - `para_quien`;
  - `oferta` o `texto` con el entregable;
  - `faq`.

## Enlaces entre páginas

`@landing`, `@diagnostico`, `@reserva`, `@gracias` y `@webinar` (más `?…` o `#…` si hace falta) se convierten en el
`archivo` o la `ruta_publica` de esa página. Los enlaces entre tus páginas arrastran los parámetros de atribución de la
URL de llegada:
- `utm_*`;
- `campaign_id`, `adset_id` y `ad_id`;
- `placement`, `site` y `fbclid`.

Después del formulario se añade también `ref` (el `event_id` del lead), para unir la reserva con el envío. Los enlaces
externos y los marcados con `data-pos-sin-atribucion` no se tocan.

**Páginas en carpetas distintas** (p. ej. `registro/` y `gracias/`, el flujo de `/webinar`): genera cada una con su
config y pon el enlace a mano (`"siguiente": "../gracias/"`). Con una sola página, el config la escribe como
`index.html`, que es lo que sirve `../gracias/`. En gracias, pon el evento en `anadir_calendario` en vez de `true`. Si
un `@tipo` no está en el config, `generar` avisa y deja `#`. Valida la carpeta madre
(`validar clientes/<slug>/paginas/<edicion>/`): así se comprueba que `../gracias/` tiene su `index.html`.

## Tracking

### Eventos de cada página (contrato §16)

| Página | Evento | Cuándo | `value` |
|---|---|---|---|
| landing | `Lead` (o el de `formulario.evento`) | Al enviar el formulario | — |
| webinar | `CompleteRegistration` (o el de `formulario.evento`) | Al enviar el registro | — |
| diagnóstico | `Lead` + `DiagnosticoCompletado` | `Lead`, siempre al enviar los datos de contacto, sea cual sea el paso. `DiagnosticoCompletado`, a la vez que `Lead` con `captura: antes`, o al ver el resultado con `despues` | El de `valor_evento` en el segundo |
| diagnóstico | `LeadCualificado` | Solo con `cualificado.activo` | — |
| reserva | `Schedule` | Con Calendly y `evento_schedule: navegador`; si no, desde el servidor. Con VSL, igual: `Lead` ya salió en la captación | — |
| gracias | `gracias.evento` | Al llegar, si lo configuras | — |
| todas | `PageView` | Al aceptar las cookies | — |

`LlamadaAsistida`, `PropuestaEnviada` y `Purchase` salen del CRM (etapas de GHL → CAPI), no de estas páginas. Los
nombres son los de la tabla canónica del contrato §16: no los cambies, que el píxel, la CAPI y el CRM tienen que usar
el mismo.

### Consentimiento

- `fbevents.js` **no se descarga** hasta que la persona pulsa «Aceptar». Entonces se llama a
  `fbq('consent', 'grant')`, `init` y `PageView`, y se disparan los eventos que esperaban en cola en esa página.
- Es más estricto que el patrón de Meta (`revoke` antes de `init`, `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`
  §2.2): sin aceptar, Meta no recibe ni la petición `[STRONG INFERENCE]`.
- «Rechazar» borra `_fbp` y `_fbc`. La decisión se guarda en `localStorage` (`pos_consentimiento_v1`) y caduca a los
  `caducidad_dias`. «Preferencias de cookies», en el pie, la reabre.
- Las UTMs y el `ad_id` sí viajan siempre al webhook: no son identificadores de Meta y el CRM los necesita para atribuir.
- Con tu propio gestor de cookies (`banner: false`), llama a `PaginasOS.consentimiento('si')` o `('no')`.
- El banner sale en todos los modos en que hay algo que pedir: con píxel, y también sin él («solo servidor») si el
  webhook manda a la CAPI con `base_legal_servidor: consentimiento`. En «solo servidor» no habla de píxel: pide
  permiso para mandar a Meta los datos del formulario. Cada envío lleva el estado (`consentimiento_marketing`) y la
  decisión (`enviar_a_meta`).

### El envío al webhook (formato v1)

Un `POST` por envío con este JSON. Los campos del formulario van en la raíz con su id: `nombre`, `email`,
`telefono`, `empresa`…, y las casillas `acepta_*` como `true`/`false`.

| Campo | Qué lleva |
|---|---|
| `version`, `origen` | `1`, `"meta-ads-os/paginas"` |
| `tipo_envio`, `pagina` | `lead`, `diagnostico`, `registro_webinar`, `reserva` o `evento`; el tipo de página |
| `url`, `event_source_url` | La URL completa sin `fbclid` (con UTMs, para el CRM) y la URL sin query (para la CAPI) |
| `momento`, `event_time` | ISO 8601 y segundos Unix (el `event_time` de la CAPI) |
| `ref` | `event_id` del lead anterior, cuando el envío viene de otra página (reserva → lead) |
| `content_name` | El de `tracking` o de la página |
| `utm_source`…`utm_id`, `campaign_id`, `adset_id`, `placement`, `site` | De la URL de la página (los enlaces entre tus páginas los arrastran desde la de llegada) |
| `ad_id` | El parámetro `ad_id` de la plantilla de UTMs (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8); si falta, `utm_content` cuando es un número |
| `respuestas`, `diagnostico` | Solo del diagnóstico: respuestas legibles; `{nivel, principal, valor_principal, resultados, supuestos, supuestos_editados, resumen, cualificado_automatico}` |
| `consentimiento_marketing` | Estado de las cookies de medición: `si`, `no` o `pendiente` (no confundir con las casillas `acepta_*`) |
| `base_legal_servidor`, `enviar_a_meta` | La configurada; `true` si el servidor puede mandar este envío a la CAPI |
| `event_name`, `event_id` | El evento principal (vacío el `event_id` si `enviar_a_meta` es `false`) |
| `eventos` | `[{event_name, event_id, value, currency}]`: todos los eventos del envío (p. ej. `Lead` y `DiagnosticoCompletado`) |
| `fbclid`, `fbc`, `fbp` | Solo si `enviar_a_meta`. `fbc` = cookie `_fbc` o `fb.1.<ms del clic>.<fbclid>`. `fbp` solo con «Aceptar» |
| `client_user_agent` | El del navegador (la CAPI lo pide en eventos web) |

La IP no va en el cuerpo: tu receptor la toma de la petición si la base legal lo permite.

### Qué hace tu servidor con el envío

1. Crea o actualiza el contacto en el CRM con los campos, las UTMs, el `ad_id` y las respuestas (en GHL, a campos
   personalizados; `docs/guias/ghl-meta.md` §3).
2. **Si `enviar_a_meta` es `true`**, manda cada elemento de `eventos` a la CAPI:
   - el mismo `event_name` y `event_id`, para deduplicar con el píxel;
   - `action_source: "website"`, `event_time`, `event_source_url` y `client_user_agent`;
   - `fbc` y `fbp` si vienen;
   - email y teléfono normalizados y con hash (`python3 -I herramientas/capi.py construir` y `validar`).
3. **Si es `false`**, no lo mandes a Meta. El lead entra en el CRM igualmente y sus etapas posteriores podrán ir por
   CAPI de CRM con las reglas de la ficha.
4. Responde `2xx`. Con `modo: json`, cualquier otra respuesta hace que la página diga «no hemos podido enviar» y deje
   reintentar.

**Ruta A (recomendada): n8n, Make o tu backend → GHL + CAPI.** Controlas el `event_id` y la regla de `enviar_a_meta`.
La plantilla lista para importar (n8n), el escenario de Make y el pseudocódigo de un backend están en
[`plantillas/integraciones/paginas/`](../integraciones/paginas/README.md). Ver también `docs/guias/capi.md`.

**Ruta B: *Inbound Webhook* de GHL directo.**
- Sale más sencilla, pero:
  - es una función premium;
  - no está documentado si acepta CORS (si falla, usa `webhook.modo: "texto"`);
  - la acción de CAPI de GHL no tiene campo `event_id`.
- Así que el `Lead` del navegador y el de GHL no deduplican. Elige una sola fuente para ese evento:
  - o `eventos_navegador: false` y todo desde GHL;
  - o el píxel para `Lead` y GHL solo para las etapas posteriores.
- En el workflow de GHL, la acción de CAPI va detrás de un *If/Else* sobre `enviar_a_meta` = `true` (y, con base
  `consentimiento`, `consentimiento_marketing` = `si`). Sin esa condición, GHL mandaría a Meta a quien pulsó
  «Rechazar».

## Publicar

- **Hosting propio** (Netlify, Vercel, Cloudflare Pages, un FTP): sube la carpeta tal cual. Pon `ruta_publica` si las
  URLs no acaban en `.html`.
- **GHL:** con `--fragmento-ghl`, pega `ghl/<página>.html` en un elemento «Custom code» de una página en blanco de un
  funnel. El fragmento lleva el CSS limitado a `.pos` (no toca el resto de la página de GHL) y el JS incrustado. Sube
  las imágenes a la biblioteca de medios y pon su URL base en `sitio.recursos_url`.
- `--en-linea` deja cada página en un solo HTML (más imágenes), para constructores que no admiten archivos `.js`.
- Después de publicar: `/landing <url>` (y `herramientas/landing_check.py`) la revisa en el dominio real, y una prueba
  de punta a punta con el código de *Probar eventos*. `landing_check.py` reconoce estas páginas (por el `generator`
  y el `pos-config`) y da el píxel como «tras consentimiento (paginas.py)», no como ausente: en el HTML no hay
  `fbq('init')` porque `paginas.js` lo carga al aceptar. Para verlo en *Probar eventos*, acepta el banner.

## Qué comprueba `validar`

Sobre cada `.html` generado (los demás se ignoran). Los umbrales de peso son `[HYPOTHESIS]`, orientativos para móvil:

| Grupo | Ids | Ejemplos |
|---|---|---|
| Documento | `doc.idioma`, `doc.titulo`, `doc.viewport`, `doc.zoom`, `doc.h1`, `meta.generador` | Sin `lang`, sin `<title>`, zoom bloqueado, sin un único `h1` |
| Accesibilidad | `a11y.saltar`, `a11y.ids`, `a11y.etiquetas`, `a11y.botones`, `a11y.enlaces`, `a11y.contraste` | Campos sin `<label>`, botones o enlaces sin texto, ids repetidos, tokens de marca con contraste bajo |
| Peso | `peso.html`, `peso.total` | HTML > 150 KB (aviso); página con recursos > 600 KB (aviso) o > 2 MB (error) |
| Imágenes | `img.alt`, `img.dimensiones`, `img.falta`, `img.peso`, `img.lazy` | Sin `alt`, sin `width`/`height` (saltos), > 300 KB (aviso) o > 1 MB (error) |
| Scripts | `js.falta`, `js.terceros`, `js.bloqueante`, `css.terceros`, `video.terceros` | Scripts o CSS de terceros, scripts sin `defer`, un vídeo de YouTube, Vimeo, Wistia, Loom o Vidyard pegado con su código de inserción (se carga al abrir la página, antes de pulsar y del consentimiento: usa la clave `video`) |
| Tracking | `pixel.sin_consentimiento`, `tracking.config`, `tracking.runtime`, `tracking.webhook`, `tracking.pixel` | `fbevents.js`, `fbq(` o el `<noscript>` del píxel en el HTML (se cargarían sin consentimiento), config ilegible, falta `paginas.js`, webhook sin https o vacío |
| Consentimiento | `consentimiento.banner`, `consentimiento.externo` | Píxel o envío a la CAPI con base `consentimiento` («solo servidor») sin banner ni gestor propio |
| Formularios | `form.email`, `form.tel`, `form.sin_tracking`, `form.evento`, `form.trampa`, `form.reservado` | Email sin `type="email"`, formulario sin `data-evento` o sin trampa antispam, un campo con el nombre de un campo del envío |
| Páginas | `diag.config`, `diag.formulas`, `reserva.calendario`, `gracias.noindex` | Fórmulas que no compilan, reserva sin calendario, gracias indexable |
| Contenido | `enlaces.ancla`, `enlaces.rotos`, `contenido.ejemplo` | Anclas que no existen, enlaces a archivos que no están, casos de ejemplo sin sustituir |

`enlaces.rotos` mira los `<a>`, el `siguiente` de los formularios (`data-siguiente`) y de la página, y los CTA de los
niveles del diagnóstico. Un enlace a una carpeta (`../gracias/`) necesita su `index.html`: si la carpeta está dentro de
lo que validas y no lo tiene, es error; si queda fuera, es aviso (valida la carpeta madre).

## Sin verificar (2026-11-10)

- **GHL:**
  - si el *Inbound Webhook* acepta peticiones con CORS desde otro dominio;
  - los nombres exactos de los parámetros con los que su calendario se rellena (`first_name`, `email`…);
  - si su widget, dentro de un iframe, avisa a la página al reservar (hoy no se detecta: por eso `Schedule` va por
    servidor).
- **Calendly:** que `embed_domain` siga siendo necesario para que lleguen sus mensajes `postMessage`.
- **Umbrales:** los de peso de `validar` y los rangos de preguntas, `[HYPOTHESIS]`. Ajústalos con datos de campo
  (CrUX, PageSpeed) cuando los tengas.
