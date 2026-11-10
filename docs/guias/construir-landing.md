# Páginas de captación para Meta, paso a paso

Para quién: consultoras, agencias de IA y automatización y SaaS que llevan tráfico de Meta a una web propia.

Qué consigues: las páginas del embudo como archivos HTML estáticos:
- landing, diagnóstico, reserva, gracias o webinar;
- con tu marca;
- rápidas en el navegador interno de Instagram y Facebook;
- con el píxel solo tras aceptar las cookies;
- con cada envío llegando a tu CRM con sus UTMs, su `ad_id` y el mismo `event_id` que el píxel, para que Meta no
  cuente doble.

La skill es **`/construir-landing <cliente>`**. El diagnóstico (preguntas, cálculo y veredicto) se diseña antes con
**`/iman-de-leads`** (`docs/guias/iman-de-leads.md`). El OS genera y valida, pero **no publica**: la carpeta la subes
tú. Ya publicada, **`/landing <url>`** la audita en el dominio real.

Referencia técnica completa (todas las claves del config, el formato del envío y las fórmulas):
`plantillas/paginas/README.md`. «No verificado» quiere decir que no se ha podido comprobar en la documentación oficial
el 2026-11-10: compruébalo en tu pantalla.

```
config JSON ──paginas.py generar──▶ carpeta (HTML + recursos/) ──paginas.py validar──▶ 0 errores
      └──▶ tú publicas (hosting o GHL) ──▶ prueba de punta a punta (Probar eventos) ──▶ /landing <url> ──▶ anuncios
visita ─▶ formulario ─▶ píxel (si aceptó) + webhook (mismo event_id) ─▶ n8n/Make/GHL ─▶ CRM + CAPI ─▶ Meta deduplica
```

---

## 1. Qué páginas necesitas

| Embudo | Páginas | Cuándo |
|---|---|---|
| Landing con diagnóstico | `landing` → `diagnostico` → `reserva` → `gracias` | La entrada por defecto en servicios a medida (`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §5.3) |
| Webinar o taller | `webinar` → `gracias` con calendario | Mercado frío; lo coordina `/webinar` (`docs/guias/webinar.md`) |
| VSL y llamada | `landing` con vídeo → `reserva` → `gracias` | Tickets altos que necesitan explicación; el vídeo va antes de los datos |
| **Captación → VSL con calendario** | `landing` con el formulario de captación → `reserva` con `video` y `texto_calendario` → `gracias` | Lo mismo, pero pidiendo los datos antes del vídeo y sin formularios instantáneos (abajo) |
| Solo reserva | `reserva` → `gracias` | Tráfico caliente o retargeting |

Los ejemplos completos están en `plantillas/paginas/ejemplos/`:
- `acme-embudo.json`, el embudo con diagnóstico;
- `nimbo-webinar.json`, el webinar con varias zonas horarias y WhatsApp;
- `acme-vsl-calendario.json`, la captación con VSL y calendario.

### Captación → VSL con calendario

El anuncio lleva a una captación corta (nombre, email y una o dos preguntas de cualificación). Al enviarla, la persona
pasa a la página del vídeo, con el calendario de GHL debajo, y al reservar, a gracias. Nada de formularios
instantáneos: la captación es tu página.

| Paso | Página y claves | Evento |
|---|---|---|
| Captación | `landing` con una sección `formulario` y `"siguiente": "@reserva"` | `Lead` al enviar los datos de contacto: píxel y webhook con el mismo `event_id` (o una sola fuente, ruta B de §3) |
| VSL y calendario | `reserva` con `video` (las mismas claves que el del hero: `proveedor`, `id`, `miniatura`, `titulo`, `duracion`) y `texto_calendario` (el texto encima del calendario) | Ninguno de Meta. Ver el vídeo no cuenta como evento |
| Cita reservada | El calendario de GHL dentro de la `reserva` | `Schedule`, por defecto desde el workflow «cita reservada» de GHL por CAPI (`evento_schedule: "servidor"`) |
| Gracias | `gracias` | Ninguno por defecto (`evento: ""`) |

- **El vídeo no carga nada de YouTube ni de Vimeo hasta que la persona pulsa** (como en el hero). Pon una `miniatura`
  propia: sin ella se ve un fondo liso con el botón de reproducir (`generar` avisa).
- **Con `video`, la reserva pasa a una columna**: titular → vídeo → calendario → puntos y anfitrión. Así el calendario
  se ve sin terminar el vídeo (03/15 §4.4). Sin `video`, la reserva queda como siempre, en dos columnas.
- Si no pones `titulo`, con vídeo sale «Antes de elegir hora, mira este vídeo». Si no pones `texto_calendario`, con
  vídeo sale «Elige día y hora para la llamada» (sin vídeo, nada: el titular ya lo dice).
- Con `tracking.prefill_reserva: true`, el calendario llega relleno con el nombre y el email de la captación.
- **No pegues el código de inserción de YouTube o Vimeo** en la página ni en GHL: se carga al abrirla, antes de que la
  persona pulse y de que acepte las cookies. `validar` avisa con `video.terceros`.
- Quien deja sus datos y no reserva es un lead normal en el CRM: al equipo le toca escribirle o llamarle
  (`/seguimiento-leads`).
- Si la captación es un formulario de GHL en vez del de estas páginas, no está verificado que un campo oculto se
  rellene desde el enlace ni que el formulario permita redirigir según la respuesta (abajo, «Qué no está
  verificado»). Sin eso, no puedes enseñar el calendario solo a quien encaja.

## 2. Marca y textos

- **Marca.** Va en `clientes/<slug>/marca/marca.json` (formato en `plantillas/html/README.md`), con colores, logo y
  tipografía. Si tus colores no dan contraste suficiente, `generar` los ajusta y te avisa. Una fuente propia solo se
  carga si traes el archivo (mejor `.woff2`); si no, se usa la del sistema, que es la más rápida.
- **El hero continúa el anuncio** (`meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` §3.1):
  - mismo titular o promesa;
  - misma imagen o la misma primera pregunta;
  - una prueba breve y verificable;
  - un CTA.

  En la landing con diagnóstico, la primera pregunta va como botones en el hero (`media.tipo: arranque`): un toque y
  ya está dentro.
- **El cuerpo, en orden de objeciones** (§3.2):
  - cómo funciona;
  - qué recibe;
  - para quién **no** es;
  - prueba;
  - preguntas frecuentes;
  - cierre.

  En móvil, una barra fija repite el CTA cuando se pasa el hero y se esconde sobre el formulario.
- **Prueba social, solo real.**
  - Casos con permiso y cifras verificables (`meta-ads-kb/08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md`
    §4; `/casos-y-creadores`).
  - Mientras no los tengas, la sección de casos va marcada como ejemplo, y `validar` no te deja dar la página por buena
    hasta que la cambies o la quites.
- **Sin promesas** («ahorrarás», «garantizado», «100 %»). `generar` avisa si las encuentra, y `revisor-politicas`
  revisa la página antes de publicar.
- **Legal.** Necesitas las URLs de privacidad, aviso legal y cookies, y quién es el responsable del tratamiento. Bajo
  cada formulario va la primera capa informativa. Las casillas de comunicaciones (email, WhatsApp…) van separadas,
  son opcionales y salen sin marcar.

## 3. Tracking

### Los eventos (contrato §16)

| Página | Evento | Cuándo |
|---|---|---|
| Landing | `Lead` | Al enviar el formulario |
| Diagnóstico | `Lead` y `DiagnosticoCompletado` (con `value` = valor esperado del lead) | `Lead`, al enviar los datos de contacto, en el paso que sea; `DiagnosticoCompletado`, con `Lead` o al ver el resultado (abajo) |
| Webinar | `CompleteRegistration` | Al registrarse |
| Reserva | `Schedule` | Con GHL, desde el workflow «cita reservada» (servidor); con Calendly puede ir desde el navegador. Con VSL, la reserva no manda `Lead`: ya salió en la captación |
| Gracias | El que configures (vacío por defecto) | Al llegar |

`LeadCualificado`, `LlamadaAsistida`, `PropuestaEnviada` y `Purchase` salen de las etapas de GHL por CAPI
(`docs/guias/ghl-meta.md` §4), no de las páginas.

`Lead` es el momento en que la persona envía sus datos de contacto (contrato §16). En el diagnóstico, con
`captura: "antes"` se piden tras las preguntas y antes del resultado, y con `"despues"`, tras el resultado para
reservar: `Lead` sale en ese envío, `DiagnosticoCompletado` a la vez (con `antes`) o al ver el resultado (con
`despues`). Hoy no hay variante que pida el contacto en el primer paso, antes de las preguntas.

### Consentimiento

- El píxel (`fbevents.js`) no se descarga hasta que la persona pulsa «Aceptar». Es más estricto que el patrón que
  documenta Meta, `revoke` antes de `init` (`meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`
  §2.2).
- «Rechazar» tiene el mismo peso visual y borra las cookies `_fbp` y `_fbc`. «Preferencias de cookies», en el pie,
  reabre la decisión.
- Sin «Aceptar», el envío al webhook lleva igualmente los datos del formulario y las UTMs (el CRM los necesita), pero
  no lleva `event_id`, `fbclid`, `fbc` ni `fbp`, y marca `enviar_a_meta: false`. Tu servidor no debe mandar ese
  envío a la CAPI.
- **El banner sale en todos los modos en que hay algo que pedir**, también sin píxel («solo servidor»: el webhook
  manda los eventos a la CAPI con `base_legal_servidor: "consentimiento"`). En ese modo el texto no habla de píxel ni
  de cookies de Meta: pide permiso para mandar a Meta los datos del formulario. Sin banner, `enviar_a_meta` saldría
  siempre `false` y el servidor no podría mandar nada; `validar` lo marca como error (`consentimiento.banner`).
- Cada envío lleva el estado (`consentimiento_marketing`: `si`, `no` o `pendiente`) y la decisión (`enviar_a_meta`).
  La plantilla del receptor (`plantillas/integraciones/paginas/`) solo manda a la CAPI con `enviar_a_meta: true` y,
  con base `consentimiento`, `consentimiento_marketing: "si"`.
- Si el cliente usa su propio gestor de cookies, pon `consentimiento.banner: false` y haz que el gestor llame a
  `PaginasOS.consentimiento('si')` o `('no')`. Vale para los dos modos.
- **No añadas el píxel por otro lado**: ni en los ajustes de seguimiento del funnel de GHL, ni con GTM. Se cargaría
  sin consentimiento y contaría doble.

### El webhook: adónde va cada envío

Cada formulario hace un `POST` con un JSON (formato en `plantillas/paginas/README.md`, «El envío al webhook»), con:
- los campos del formulario;
- las respuestas y el resultado del diagnóstico;
- las UTMs, `ad_id`, `campaign_id` y `adset_id`;
- el estado del consentimiento;
- los eventos con su `event_id`.

Sin `tracking.webhook.url`, las páginas están en **modo prueba**: no envían nada y lo dicen.

**Ruta A, recomendada: n8n, Make o tu backend → GHL + CAPI.** Plantilla lista: `plantillas/integraciones/paginas/`
(un flujo de n8n para importar, el escenario de Make y el pseudocódigo de un backend, con la regla del consentimiento
ya puesta y probada).
1. Un webhook recibe el envío. Responde `200` y permite el origen de tu dominio (CORS). En n8n se hace en las opciones
   del nodo Webhook (no verificado en todas las versiones).
2. Crea o actualiza el contacto en GHL con los campos, las UTMs, el `ad_id`, el nivel y el resumen del diagnóstico.
3. Si `enviar_a_meta` es `true`, manda cada elemento de `eventos` a la CAPI con el mismo `event_name` y `event_id`,
   más:
   - `event_time`, `event_source_url` y `client_user_agent`;
   - `fbc` y `fbp`;
   - email y teléfono con hash.

   Guía: `docs/guias/capi.md`. Comprueba el payload con `python3 -I herramientas/capi.py validar`.

**Ruta B: GHL directo con su *Inbound Webhook*.** Más simple, con tres límites:
- es una función premium;
- no está documentado que acepte CORS: si la página dice «no hemos podido enviar», pon `webhook.modo: "texto"`;
- su acción de CAPI no tiene campo `event_id`, así que no puede deduplicar con el píxel.

Pasos:
1. Workflow nuevo con disparador *Inbound Webhook*. Copia su URL en `tracking.webhook.url`.
2. Haz un envío de prueba desde tu página ya publicada para que GHL vea los campos. Después, acción *Create/Update
   Contact*. Mapea:
   - nombre, email, teléfono y empresa;
   - `utm_*` y `ad_id` a campos personalizados (`docs/guias/ghl-meta.md` §3);
   - el nivel del diagnóstico a una etiqueta.
3. Elige **una sola fuente** para `Lead`:
   - o el píxel (y GHL solo manda las etapas posteriores);
   - o `tracking.eventos_navegador: false` y todo desde GHL.

   Si los dos mandan `Lead`, Meta lo cuenta dos veces (`docs/guias/ghl-meta.md` §5).
4. Si GHL manda algo a Meta desde este workflow, pon la acción de CAPI detrás de un *If/Else*: `enviar_a_meta` es
   `true` y, con base `consentimiento`, `consentimiento_marketing` es `si`. Sin esa condición, GHL mandaría a Meta a
   quien pulsó «Rechazar».

**Base legal.** `base_legal_servidor: "consentimiento"` por defecto. `interes_legitimo` manda `event_id` y `fbc` al
servidor sin «Aceptar» (nunca `fbp`): solo con el visto bueno de tu asesor legal `[CONTESTED]`.

### UTMs

Usa la plantilla única de `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8, que trae `ad_id={{ad.id}}`. Con GHL,
`utm_source=fb_ad` (`docs/guias/ghl-meta.md` §3).

Las páginas leen los parámetros de la URL de llegada y los pasan de una página a otra, hasta la reserva:
- `utm_*`;
- `campaign_id`, `adset_id` y `ad_id`;
- `placement`, `site` y `fbclid`.

El calendario recibe toda esa atribución (`utm_*`, `campaign_id`, `adset_id`, `ad_id`, `placement`, `site`) y `ref`, el
`event_id` del lead. El `fbclid` solo va si `enviar_a_meta` lo permite.

## 4. Generar y validar

```bash
python3 -I herramientas/paginas.py generar todas --config clientes/acme/planes/2026-11-10_diagnostico.paginas.json \
    --salida clientes/acme/paginas/2026-11-10_diagnostico/ --cliente acme
python3 -I herramientas/paginas.py validar clientes/acme/paginas/2026-11-10_diagnostico/
```

- `generar` escribe:
  - `index.html` y el resto de páginas;
  - `recursos/`: el JS, el logo, las imágenes, el vídeo, las fuentes y el `.ics`.

  No borra nada de la carpeta: solo sobrescribe lo que genera.
- **`--cliente acme`** toma la marca del cliente y, de su ficha, la moneda (si el config no pone `sitio.moneda`) y la
  zona horaria del webinar. Sin ficha, `EUR` y `Europe/Madrid`. Si config y ficha no coinciden, `generar` avisa.
- **Opciones:**
  - `--fragmento-ghl`: además, `ghl/<página>.html` para pegar en GHL;
  - `--en-linea`: el JS dentro de cada HTML, para constructores que no aceptan archivos `.js`.
- **Avisos.** Léelos todos: faltan medidas de una imagen, falta la política de privacidad, un escenario del
  diagnóstico no da el nivel esperado…
- **`validar`** revisa cada página (lista completa en `plantillas/paginas/README.md`):
  - el documento (idioma, título, `h1`, zoom permitido);
  - la accesibilidad (etiquetas, textos de botones y enlaces, contraste);
  - el peso (aviso por encima de 600 KB por página con sus recursos, error por encima de 2 MB `[HYPOTHESIS]`);
  - las imágenes (`alt`, medidas, peso);
  - el tracking (configuración, webhook https, ningún píxel fuera del consentimiento);
  - los formularios;
  - los enlaces;
  - el contenido de ejemplo sin sustituir.

  Termina con código 1 si hay errores.

Después ábrela en tu navegador a 390 px de ancho y recorre el camino entero:
- aceptar y rechazar cookies;
- un error en el formulario;
- el diagnóstico con un caso de cada nivel;
- la reserva (con VSL: que el vídeo solo se cargue al pulsar y que el calendario se vea debajo).

Sin webhook, nada sale de tu ordenador.

## 5. Publicar

El OS no sube nada: lo haces tú.

**En tu hosting** (Netlify, Cloudflare Pages, Vercel, un FTP):
1. Sube la carpeta tal cual: `index.html` en la raíz del dominio o del subdirectorio.
2. Si tu hosting quita el `.html` de las URLs (muchos lo hacen), pon `ruta_publica` en cada página
   (`"ruta_publica": "/diagnostico"`) y vuelve a generar. Así te ahorras una redirección en cada clic.
3. Usa tu dominio con HTTPS y verificado en el Business Manager (`F1.dominio`). Nada de acortadores.

**En GHL:**
1. Genera con `--fragmento-ghl`.
2. Sube las imágenes y el logo de `recursos/` a la biblioteca de medios. Pon la URL base en `sitio.recursos_url` y
   vuelve a generar.
3. Crea un paso de funnel con una página en blanco, añade el elemento de código personalizado (*Custom code*; el
   nombre exacto en tu versión no está verificado) y pega `ghl/<página>.html`.
   - El fragmento solo da estilo dentro de su bloque y no toca el resto de la página.
   - Lleva el JS incrustado.
4. En los ajustes de seguimiento del funnel, **no** pongas el píxel de Meta (ver §3).
5. Ajusta `ruta_publica` (o los enlaces) a las rutas que te dé GHL y regenera.

## 6. Probar de punta a punta y revisar

1. Antes de la primera campaña, pon el código de *Probar eventos* de Events Manager en tu servidor (ruta A) o en la
   acción de CAPI de GHL (ruta B). Lo explica `/implementar-capi`.
2. Abre tu página publicada con parámetros de prueba:
   `https://tu-dominio/?utm_source=fb_ad&utm_medium=paid_social&utm_campaign=prueba&ad_id=120000000000000&fbclid=prueba123`.
3. Acepta las cookies y completa el formulario con tus propios datos.
4. Comprueba:
   - **el envío** llegó a tu webhook con `event_id`, `fbc` y `ad_id`;
   - **el contacto** está en GHL con el `ad_id` y las UTMs;
   - **en *Probar eventos***, el `Lead` aparece del navegador y del servidor con el mismo `event_id`, deduplicado.
5. En una ventana privada, pulsa «Rechazar» y vuelve a enviar. En las herramientas de desarrollo (pestaña Red) no debe
   aparecer ninguna petición a `connect.facebook.net`, y el envío debe llevar `enviar_a_meta: false`.
6. Quita el código de prueba y pasa `/landing <url> <cliente>`: tracking, velocidad móvil, message match y CTA en el
   dominio real. Esa revisión marca `F1.landing`. `landing_check.py` reconoce las páginas de `paginas.py` y da su
   píxel como «tras consentimiento (paginas.py)»: no se ve en el HTML porque no se descarga hasta «Aceptar», y no es
   un fallo. Si dice «página de paginas.py sin `tracking.pixel_id`», falta el ID en el JSON de la página.
7. Ya puedes poner la URL en los anuncios (`/lanzar-campana` o `/publicar-anuncios`).

Si cambias una página con campañas activas, regenera solo esa, valida y anota el cambio en el change log del cliente
con la fecha para leer el efecto.

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| «No hemos podido enviar tus datos» | El receptor no permite CORS desde tu dominio, está caído o responde con error | Ruta A: permite el origen en el webhook. GHL: `webhook.modo: "texto"`. Mira la consola del navegador |
| Llegan contactos sin `ad_id` | La plantilla de UTMs del anuncio no trae `ad_id`, o el receptor no lo guarda | 10-plantillas §8; mapea el campo en GHL |
| Meta cuenta el doble de leads | Píxel y GHL mandan `Lead` sin `event_id` común | Una sola fuente (§3, ruta B) o ruta A |
| No sale ningún evento del navegador | La persona no aceptó, `pixel_id` vacío o un bloqueador | Es lo esperado sin «Aceptar»; revisa `pixel_id` con el Pixel Helper |
| El calendario no se rellena con nombre y email | Los nombres de los parámetros no coinciden con los del proveedor | `calendario.parametros` (los de GHL no están verificados) |
| La reserva no lleva a gracias | Con GHL la página no se entera de la reserva | Pon la redirección de gracias en los ajustes del calendario de GHL, o deja que el workflow mande `Schedule` |
| `validar` da `contenido.ejemplo` | Casos de ejemplo sin sustituir | Pon casos reales con permiso o quita la sección |
| `validar` da `peso.total` o `img.peso` | Imágenes grandes | WebP o AVIF, ≤ 200 KB, a su tamaño de pantalla |
| El fragmento se ve raro en GHL | Estilos de la página de GHL | Página en blanco, sin plantillas de sección alrededor |

## Qué no está verificado (2026-11-10)

- **GHL:**
  - si el *Inbound Webhook* acepta peticiones con CORS desde otro dominio (por eso existe `webhook.modo: "texto"`);
  - los nombres exactos de los parámetros para rellenar su calendario (`first_name`, `last_name`, `email`, `phone`);
  - si su widget, dentro de un iframe, avisa a la página al reservar, o si su redirección tras la reserva funciona
    dentro del iframe;
  - el nombre del elemento de código personalizado en el editor;
  - si un campo oculto de un formulario de GHL se rellena desde un parámetro del enlace (por ejemplo, el `ad_id` o
    las UTMs);
  - si un formulario de GHL permite una redirección condicional, distinta según la respuesta (por ejemplo, el
    calendario solo para quien encaja).

  Los dos últimos solo importan si la captación es un formulario de GHL: con las páginas de `paginas.py`, las UTMs y
  el `ad_id` ya van en el envío y la redirección es `siguiente`.
- **Calendly:** que `embed_domain` siga siendo necesario para recibir el aviso `calendly.event_scheduled`.
- **n8n:** dónde está la opción de orígenes permitidos (CORS) en tu versión del nodo Webhook.
- **Umbrales:** los de peso de `validar`, orientativos `[HYPOTHESIS]`. Contrástalos con datos de campo (PageSpeed,
  CrUX) cuando tengas tráfico.
