---
name: construir-landing
description: "Construye y valida las páginas de captación para Meta con paginas.py (landing, diagnóstico, reserva, gracias o webinar): marca del cliente, message match con el anuncio, consentimiento antes del píxel, UTMs, fbclid y event_id compartido con el webhook, y guía para publicarlas. No despliega; /landing audita una URL publicada."
argument-hint: "<cliente> [landing|diagnostico|reserva|gracias|webinar|todas] [--config <json>] | validar <carpeta>"
---

# /construir-landing

Entrada: `$ARGUMENTS`. Genera las páginas que reciben el tráfico de Meta como HTML estático:
- con la marca del cliente;
- rápidas en el navegador interno de Instagram y Facebook;
- con el consentimiento antes del píxel;
- con el tracking completo del contrato §16 y §17.

Valida las páginas y deja al usuario una guía para publicarlas. El OS **nunca despliega**: la carpeta la sube el usuario
a su hosting o la pega en GHL.

Reparto con otras skills:
- **Qué embudo** usar es de `/disenar-funnel`.
- **La oferta**, de `/oferta`.
- **El diagnóstico** (preguntas, cálculo, veredicto), de `/iman-de-leads`.
- **Auditar una página ya publicada** (la suya o la de otro), de `/landing`.
- **El webinar completo** lo coordina `/webinar`, que usa esta skill para sus páginas.

No escribe en Meta, GHL ni Stripe, y en las pruebas no envía datos a ningún webhook real.

`validar <carpeta>` solo comprueba una carpeta ya generada: salta al paso 6.

- **Marco:**
  - `meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` (§1.2 navegador interno, §2.4 checklist
    técnico, §3 message match y anatomía, §4.2 formulario, §4.3 calendario y gracias, §4.4 VSL);
  - `meta-ads-kb/03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md` (§3 message match);
  - `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` (§5.3 embudo B, §5.5 embudo D, §5.7 etapas
    en GHL, §8.7 qué no decir);
  - `meta-ads-kb/04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md` (§2 píxel con `eventID`,
    §4 deduplicación);
  - `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md` (§2.2 consentimiento);
  - `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md` (§3 calendario y
    confirmación);
  - `meta-ads-kb/08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md` (§4 testimonios y resultados, §5
    checklist);
  - `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8 (UTMs).

  «03/15 §3.1» significa área 03, archivo 15, sección 3.1.
- **Agentes:**
  - `especialista-funnel`: estructura, copy de la página y recorrido;
  - `estratega-creativo`: que la página continúe el anuncio (ángulo, promesa, imagen);
  - `especialista-tracking`: eventos, consentimiento y deduplicación;
  - `ingeniero-capi`: el receptor del webhook y la CAPI del servidor;
  - `especialista-crm`: campos personalizados y workflows de GHL;
  - `revisor-politicas`: antes de publicar;
  - `gestor-cliente`: el OK del cliente si eres agencia.
- **Herramientas:**
  - `paginas.py generar`, `paginas.py validar` y `paginas.py probar`;
  - `landing_check.py`, ya publicada;
  - `capi.py validar`, para el receptor.
- **Lee:**
  - la ficha: `meta.dataset`, que es el ID del píxel; `crm`; mercados e idioma; afirmaciones aprobadas; reglas
    propias;
  - `clientes/<slug>/marca/marca.json` (formato en `plantillas/html/README.md`);
  - `planes/*_funnel.md`, `planes/*_oferta.md` y `planes/*_iman-*.json`;
  - el lote o brief creativo que llevará tráfico a la página;
  - los casos con permiso de `/casos-y-creadores`;
  - el formato del config: `plantillas/paginas/README.md`;
  - los ejemplos: `plantillas/paginas/ejemplos/`.

## Pasos

1. **Decide las páginas** según el embudo del plan:

   | Embudo | Páginas |
   |---|---|
   | Landing con diagnóstico (playbook consultoras §5.3) | `landing` → `diagnostico` → `reserva` → `gracias` |
   | Webinar o taller (§5.5, con `/webinar`) | `webinar` → `gracias` con calendario |
   | VSL y llamada (03/15 §4.4): el vídeo antes de los datos | `landing` con vídeo en el hero → `reserva` → `gracias` |
   | **Captación → VSL con calendario**: los datos antes del vídeo, sin formularios instantáneos (ejemplo `plantillas/paginas/ejemplos/acme-vsl-calendario.json`) | `landing` con el formulario de captación (`siguiente: "@reserva"`) → `reserva` con `video` y `texto_calendario` → `gracias` |
   | Solo reserva (tráfico caliente o retargeting) | `reserva` → `gracias` |

   **Eventos en «Captación → VSL con calendario»:**
   - `Lead`, al enviar los datos de contacto en la captación: el píxel y la CAPI web con el mismo `event_id` (o una sola
     fuente, ruta B del paso 3). La página del vídeo no lo repite.
   - La cita reservada (`Schedule`), por defecto desde el workflow «cita reservada» de GHL por CAPI
     (`evento_schedule: "servidor"`).
   - Ver el vídeo no es un evento de Meta. Quien deja sus datos y no reserva es un lead en el CRM: le escribe o le
     llama el equipo (`/seguimiento-leads`).

   Si la captación es un formulario de GHL en vez del de `paginas.py`, dos cosas no están verificadas: que un campo
   oculto se rellene desde el enlace y que el formulario permita redirigir según la respuesta (para enseñar el
   calendario solo a quien encaja, 05/06 §1). Compruébalas en la cuenta antes de prometerlas.

   Sin marca del cliente, pídela o usa la neutra y avisa. Sin URL de la política de privacidad y de cookies, no se
   publica: díselo.
2. **Escribe el copy** con `especialista-funnel`, mirando el anuncio con `estratega-creativo`.
   - **Hero** (03/15 §3.1):
     - el titular repite la promesa del anuncio;
     - la imagen o la primera pregunta del diagnóstico es la misma que el anuncio;
     - una prueba verificable;
     - un único CTA.
   - **Página del VSL** (03/15 §4.4): el arranque del vídeo repite la promesa del anuncio y del titular; el vídeo,
     subtitulado y con `miniatura` propia; el calendario justo debajo, visible sin terminar el vídeo, con
     `texto_calendario` encima; sin menús ni enlaces que saquen de la página.
   - **Cuerpo, en orden de objeciones** (03/15 §3.2):
     - cómo funciona en 3 pasos;
     - qué recibe;
     - para quién **no** es;
     - prueba;
     - preguntas frecuentes con las objeciones reales;
     - cierre.
   - **Prueba:** solo casos reales con permiso y cifras verificables (08/10 §4). Mientras no los haya, la sección de
     casos va con `"ejemplo": true`; `validar` no deja pasar la página hasta que se cambie.
   - Nada de promesas («ahorrarás», «garantizado», «100 %») ni de lo que lista playbook consultoras §8.7. `generar`
     avisa si las detecta.
3. **Monta el tracking** con `especialista-tracking`:
   - `pixel_id` = el dataset de la ficha. Sin él, solo eventos de servidor, y dilo. El banner de consentimiento sale
     igual («solo servidor»): no lo quites, o el servidor no podrá mandar nada a Meta.
   - **Webhook, ruta A** (recomendada): n8n, Make o el backend del cliente reciben el envío, crean el contacto en GHL y
     mandan la CAPI con el mismo `event_id`. Va con `ingeniero-capi`; contrato del envío en `plantillas/paginas/README.md`
     («El envío al webhook»). Parte de la plantilla `plantillas/integraciones/paginas/`: ya trae la regla del
     consentimiento (a la CAPI solo con `enviar_a_meta: true` y, con base `consentimiento`, `consentimiento_marketing:
     "si"`).
   - **Webhook, ruta B:** el *Inbound Webhook* de GHL directo. Es premium, no tiene campo de `event_id` en su CAPI y no
     está verificado que acepte CORS (si falla, `webhook.modo: "texto"`). Elige una sola fuente para `Lead`
     (`docs/guias/ghl-meta.md` §5) y pon la acción de CAPI detrás de un *If/Else* sobre `enviar_a_meta`.
   - `base_legal_servidor: "consentimiento"` por defecto. `interes_legitimo` solo con el visto bueno del asesor legal
     del cliente `[CONTESTED]`.
   - Con GHL, la cita (`Schedule`) la manda el workflow «cita reservada» por CAPI (`evento_schedule: "servidor"`); con
     Calendly puede ir desde el navegador.
   - Pon `content_name` si hay ediciones o campañas que separar.
   - UTMs: la plantilla única de 10-plantillas §8, que trae `ad_id={{ad.id}}`. Con GHL, `utm_source=fb_ad`
     (`docs/guias/ghl-meta.md` §3).
4. **Escribe el config**, juntando lo anterior y el JSON de `/iman-de-leads` si hay diagnóstico:
   - va en `clientes/<slug>/planes/<AAAA-MM-DD>_<tema>.paginas.json`;
   - las claves están en `plantillas/paginas/README.md`;
   - las rutas de las imágenes son relativas al config: WebP o AVIF, ≤ 200 KB y con `alt`.
5. **Genera:**

   ```bash
   python3 -I herramientas/paginas.py generar todas --config clientes/<slug>/planes/<AAAA-MM-DD>_<tema>.paginas.json \
       --salida clientes/<slug>/paginas/<AAAA-MM-DD>_<tema>/ --cliente <slug>
   ```

   - `--cliente <slug>` siempre: además de la marca, toma de la ficha la moneda de los `value` (si el config no pone
     `sitio.moneda`) y la zona horaria del webinar;
   - `--fragmento-ghl` si se publica en GHL (y `sitio.recursos_url` para las imágenes);
   - `--en-linea` si el constructor no admite archivos `.js`;
   - un solo tipo en vez de `todas` si solo cambia una página.

   Lee todos los avisos y resuelve los que tengan arreglo.
6. **Valida** hasta que no haya errores:

   ```bash
   python3 -I herramientas/paginas.py validar clientes/<slug>/paginas/<AAAA-MM-DD>_<tema>/
   ```

   Con diagnóstico, también `paginas.py probar --config …`. Explica cada aviso que quede y por qué se acepta.
7. **Revisa como lo verá la persona.**
   - Abre `index.html` en el navegador a 390 px de ancho (o pide al usuario que lo haga).
   - Sin webhook, la página está en **modo prueba**: no envía nada y lo dice. No pongas la URL real hasta este paso, y
     nunca la uses para pruebas.
   - Recorre el camino entero:
     - aceptar y rechazar cookies;
     - formulario con un error;
     - diagnóstico con un caso de cada nivel;
     - reserva (con VSL: que el vídeo solo se cargue al pulsar y que el calendario se vea debajo).
   - Después, `revisor-politicas` con la checklist de 08/10 §5 y, si eres agencia, el OK del cliente
     (`gestor-cliente`).
8. **Entrega la guía para publicar** (`docs/guias/construir-landing.md` §5):
   - qué carpeta subir y dónde (hosting o «Custom code» de GHL);
   - qué rutas públicas poner si cambian;
   - el receptor del webhook y los campos de GHL que hay que crear (`especialista-crm`);
   - la prueba de punta a punta con el código de *Probar eventos* (`/implementar-capi`):
     - un envío;
     - el contacto en GHL con su `ad_id`;
     - el evento en Events Manager, deduplicado.

   En el plan del funnel (`planes/*_funnel.md`), apunta la carpeta generada y qué falta para publicar.
9. **Ya publicadas:**
   - `/landing <url> <cliente>` (y `landing_check.py`) en el dominio real. Esa revisión es la que marca `F1.landing`
     en `estado.md`;
   - luego los anuncios con la plantilla de UTMs (`/lanzar-campana` o `/publicar-anuncios`).

   Si cambias una página con campañas activas, regenera solo esa, valida y anótalo en el change log del cliente con
   la fecha para leer el efecto.

## Reglas

- **El OS no publica ni sube nada.** No pongas webhooks, píxeles ni calendarios reales en ejemplos o pruebas.
- **Vídeo:** con la clave `video` (hero, sección, reserva o gracias), nunca con el código de inserción de YouTube o
  Vimeo pegado en la página: ese se carga al abrirla, antes de pulsar y del consentimiento (`validar` avisa con
  `video.terceros`).
- **Prueba social:** sin testimonios ni cifras inventadas; los casos de ejemplo no se publican.
- **Privacidad:** el píxel solo tras «Aceptar», y la primera capa de privacidad bajo cada formulario.
- No borres páginas ni archivos del cliente: `generar` solo sobrescribe lo que genera.
