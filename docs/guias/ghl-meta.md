# GoHighLevel ↔ Meta, paso a paso

Para quién: negocios de servicios y agencias que captan con Meta y venden desde GoHighLevel (HighLevel, «GHL»).
Qué consigues: que cada lead llegue a GHL con su anuncio, que GHL devuelva a Meta qué leads se cualificaron, agendaron
y pagaron, y que puedas leer todo eso por anuncio sin abrir GHL.

Hay tres tuberías distintas y conviene no confundirlas (`meta-ads-kb/05-leadgen-high-ticket-crm/04-integraciones-crm.md` §1):

```
[Anuncio]  ──(1) leads del formulario instantáneo ──▶ [GHL]                         §2
[Landing]  ──(2) píxel + CAPI web, con UTMs ─────────▶ [GHL] y [dataset web]       §3
[GHL]      ──(3) etapas del pipeline por CAPI ───────▶ [dataset CRM de Meta]       §4
```

Con (1) y (2) tienes los leads. Solo con (3) Meta aprende cuáles fueron buenos. Y lo que lee el sistema (brief diario,
informes, registro creativo) sale de GHL por la API de solo lectura (§1).

Las etiquetas `[OFFICIAL META]`, `[EMPIRICAL]`, `[CONTESTED]`… son las de la base de conocimiento. «No verificado»
quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09: compruébalo en tu pantalla.

---

## 1. Lectura desatendida: token de integración privada

El MCP de HighLevel (`/conectar ghl`) sirve para trabajar contigo delante. Para leer sin nadie (brief diario, informes),
`herramientas/ghl.py` usa un *Private Integration Token* de la sub-cuenta, **solo con permisos de lectura**.

1. En la sub-cuenta del cliente: **Settings → Private Integrations → Create new Integration**. Nombre:
   «Meta Ads OS (solo lectura)».
2. Permisos (scopes): marca solo los de lectura que usa `ghl.py`:
   - `contacts.readonly` (contactos y su atribución),
   - `opportunities.readonly` (oportunidades y pipelines),
   - `calendars.readonly` y `calendars/events.readonly` (calendarios y citas),
   - `payments/transactions.readonly` (pagos).
   Nada que termine en `.write`. Los nombres son los de la documentación de la API v2 de HighLevel; si la pantalla los
   agrupa de otra forma, elige siempre la variante «view» o «readonly».
3. Copia el token (solo se enseña una vez) y el **Location ID** de la sub-cuenta (Settings → Business Profile, o el
   trozo `/location/<ID>/` de la URL).
4. Pégalos tú en `.env`, nunca en el chat:
   ```
   GHL_TOKEN_ACME=...
   GHL_LOCATION_ACME=...
   ```
   (slug en mayúsculas y con guion bajo; sin sufijo valen para todos los clientes).
5. Prueba con un agregado que no saca datos personales:
   ```
   python3 -I herramientas/ghl.py contactos --cliente acme --json --sin-archivos
   ```
   - Salida 2 con «401»: el token está mal o revocado.
   - Salida 2 con «403»: falta un scope o el Location ID no es el de ese token.

`ghl.py` solo hace GET, más la búsqueda de contactos (`POST /contacts/search`, que solo lee). No puede escribir,
mandar mensajes ni borrar aunque el token pudiera. Límites de la API según HighLevel: ráfagas de 100 peticiones cada
10 segundos por sub-cuenta y un tope diario; `ghl.py` espera y reintenta si los toca. Rota el token si se filtra y,
según la recomendación de HighLevel, cada cierto tiempo (no verificado el plazo exacto).

---

## 2. Formularios instantáneos → GHL

1. **Conectar la Página.** En GHL: Settings → Integrations → Facebook/Instagram → conecta la Página del anuncio. Hazlo
   con una persona que sea administradora de la Página.
2. **Acceso a los leads en Meta.** Business Settings → Integraciones → **Acceso a clientes potenciales** (*Leads Access*):
   comprueba que la integración de GHL (LeadConnector) tiene acceso a la Página. Si alguien lo restringió, los leads
   no llegan y nadie avisa.
3. **Mapear los campos.** En GHL: Settings → Integrations → Facebook → *Form Fields Mapping*, formulario a formulario.
   Mapea email, teléfono y las preguntas de cualificación a campos del contacto.
4. **Guardar el ID del lead.** El ID del lead de Meta (*Facebook Lead ID*) es lo que luego permite devolver las etapas
   a Meta (§4). Comprueba que GHL lo guarda en el contacto.
5. **Guardar el anuncio.** La atribución de HighLevel no tiene un campo para el ID del anuncio (comprobado en su API el
   2026-11-09). Si al mapear el formulario GHL te deja guardar el nombre o el ID del anuncio en un campo personalizado,
   hazlo. Después dile a `ghl.py` cuál es con `--campo-anuncio <id del campo>`. Si no te deja, el cruce por anuncio de
   los leads de formulario quedará incompleto (no verificado qué ofrece cada versión de la integración).
6. **Probar sin gastar.** Con la herramienta de prueba de anuncios de clientes potenciales de Meta
   (developers.facebook.com/tools/lead-ads-testing) creas un lead de prueba en el formulario. Comprueba que llega a
   GHL en menos de un minuto, con sus campos, el Lead ID y el anuncio. Es la base del *speed to lead*.
7. **Disparar el seguimiento.** Un workflow con el disparador del formulario de Facebook (o *Contact Created* con filtro
   de origen) que avise al comercial y mande el primer mensaje. Lo que diga ese mensaje lo decides tú.

---

## 3. Landing → GHL: UTMs y atribución

### La plantilla de UTMs

`meta_ads.py crear` pone a cada anuncio esta plantilla cuando la ficha dice `crm.tipo: ghl`:

```
utm_source=fb_ad&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adset.name}}
&utm_content={{ad.name}}&campaign_id={{campaign.id}}&adset_id={{adset.id}}&ad_id={{ad.id}}
&placement={{placement}}&site={{site_source_name}}
```

(en Ads Manager va en una sola línea: Anuncio → Seguimiento → Parámetros de URL).

- **`utm_source=fb_ad`, no `facebook`.** HighLevel clasifica como *Paid Social* lo que trae `fb_ad` en `utm_source`
  (comprobado en su documentación el 2026-11-09). La plantilla general de la base (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8)
  usa `facebook`; con GHL, mejor `fb_ad`.
- **GA4.** Su agrupación de canales por defecto no reconoce `fb_ad` como fuente social, y ese tráfico puede caer en
  «Paid Other». Si usas GA4, crea un grupo de canales personalizado con la regla «fuente contiene fb_ad → Paid Social».
- **`ad_id={{ad.id}}`** es lo que permite a `ghl.py` unir cada contacto con su anuncio aunque cambies el nombre. GHL
  guarda la URL de llegada en la atribución del contacto, y `ghl.py` saca de ahí el `ad_id`.
- No pongas datos personales en la URL, nunca: ni email ni teléfono.

### Para que GHL se quede con las UTMs

- Formularios y calendarios de GHL **dentro de páginas de GHL** (funnels o websites): la atribución se guarda sola.
  No está verificado que un campo oculto de un formulario de GHL se rellene desde un parámetro del enlace, ni que el
  formulario permita redirigir a una página distinta según la respuesta: no construyas el embudo contando con ello
  sin probarlo en tu cuenta.
- Formularios de GHL **incrustados en otra web**: añade el script de seguimiento externo de GHL a esa web, o las UTMs
  se pierden por el camino (no verificado en todos los constructores de páginas: pruébalo con un clic real).
- Formularios propios (no de GHL): pasa las UTMs y el `ad_id` a campos ocultos y créalos en GHL como campos
  personalizados.
- Páginas de `paginas.py` que mandan el envío a un *Inbound Webhook* de GHL (`docs/guias/construir-landing.md`): si
  ese workflow manda algo a Meta, pon la acción de Conversions API detrás de un *If/Else*: `enviar_a_meta` es `true`
  y, con `base_legal_servidor: consentimiento`, `consentimiento_marketing` es `si`. Sin esa condición, GHL mandaría a
  Meta a quien pulsó «Rechazar». Y elige una sola fuente para `Lead` (el píxel y la CAPI web, o GHL), nunca las dos.

### Comprobar la cobertura

```
python3 -I herramientas/ghl.py contactos --cliente acme --desde 2026-11-02 --hasta 2026-11-08
```

Te dice cuántos contactos vienen de Meta y en cuántos se identifica el anuncio. Por debajo del 60 % no te fíes del
cruce por anuncio: revisa la plantilla de UTMs y la atribución antes de sacar conclusiones.

---

## 4. Etapas de GHL → Meta (Conversions API para CRM)

Es lo que permite optimizar a leads cualificados (*Conversion Leads*) en vez de a leads a secas. `[OFFICIAL META]`
(`meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md`, `04-integraciones-crm.md` §3).

### Antes de empezar

- **Un pipeline con etapas estables**, escritas y que el equipo marque igual. Por ejemplo: Nuevo → Contactado →
  Cualificado → Cita agendada → Show → **Purchase** → Perdido. No las renombres con campañas activas.
- **El dataset CRM** en Events Manager: Conectar fuente de datos → CRM, y elige o crea el dataset. No lo cambies
  después: el aprendizaje va con él (`04-…` §3.4).

### El workflow, etapa a etapa

1. **Disparador:** *Pipeline Stage Changed*, filtrado por el pipeline y la etapa.
2. **«Allow Multiple» activado** en los ajustes del workflow. Sin eso, cada contacto solo dispara la primera vez y se
   pierden transiciones (`04-…`, «Errores frecuentes»).
3. **Acción:** la de Conversions API de Meta de GHL (evento de lead). Rellena el dataset y el token de CAPI, el nombre
   del evento y el **Facebook Lead ID** del contacto (en web, el email y el teléfono). El nombre del evento es el
   exacto de la tabla del contrato §16 (`LeadCualificado`, `Schedule`, `LlamadaAsistida`, `PropuestaEnviada`,
   `Purchase`), escrito a mano y con sus mayúsculas, **nunca el nombre visible de la etapa** («Cualificado», «Cita
   agendada»): con dos nombres para el mismo hito, el volumen se reparte y el embudo del dataset no coincide.
4. **La etapa ganada se llama «Purchase»** y lleva valor (el de la oportunidad) y moneda. Pon la moneda a mano: si la
   dejas vacía, GHL usa la suya por defecto (USD según su documentación).
5. **Mientras pruebas**, pon el código de *Probar eventos* de Events Manager en el campo de código de prueba de la
   acción. Quítalo al terminar.
6. **La primera etapa (`Lead`), solo con formulario instantáneo** (con el `lead_id`): confirma la recepción y es la
   base de la cobertura. Con formulario web, `Lead` ya lo mandan el píxel y la CAPI web con el mismo `event_id`, y el
   workflow empieza en la etapa siguiente: la acción de GHL no lleva `event_id` y Meta lo contaría dos veces
   (contrato §16, «Etapa inicial»). Las etapas van con `action_source=system_generated` (`04-…` §1): GHL lo pone por
   ti.

### En Meta

- En los ajustes del dataset, configura el **embudo** (el orden de las etapas).
- En la campaña: Clientes potenciales → **Maximizar el número de clientes potenciales de conversión** → elige la etapa
  objetivo y no la toques en 2–4 semanas (`04-…` §3.4). Con `meta_ads.py crear`, es `"optimizar": "QUALITY_LEAD"` en un
  conjunto de formulario, con este dataset en `dataset_crm` (del conjunto o del plan).
- **Volumen.** GHL cita al menos 250 leads al mes y 50 eventos en 7 días para que la integración deje de estar «en
  espera» `[EMPIRICAL]`, del propio proveedor. Meta anunció el 30-10-2025 que quitaba el mínimo de volumen mensual, y
  su guía de desarrolladores aún cita 200 al mes (revisada el 2026-10-27) `[CONTESTED]` (`03-…`, TL;DR). Tampoco
  coinciden en si vale con formularios web (el Help Center dice que sí; la de desarrolladores, solo formularios
  instantáneos). Planifica con ≥200 leads al mes: con pocos eventos el sistema aprende mal igualmente.
- GHL puede tardar hasta un día en mostrar los eventos en Events Manager `[EMPIRICAL]`.

---

## 5. Citas: el punto donde más se rompe la señal

- **La reserva incrustada en el formulario instantáneo no se reporta en Ads Manager.** La cita solo llega a Meta si
  GHL la envía como etapa por CAPI (`04-…`, «Preguntas abiertas»).
- **El doble conteo de `Schedule`.** Si la página de gracias dispara `Schedule` con el píxel y GHL manda también
  `Schedule` por el servidor sin un `event_id` común, Meta cuenta dos citas por cada una. `[EMPIRICAL]`, observado en
  una cuenta de servicios high-ticket. Elige una sola fuente para cada evento o comparte el `event_id`.
  Para verlo:
  ```
  python3 -I herramientas/meta_ads.py eventos --cliente acme
  ```
  saca los eventos por día con las columnas navegador/servidor. Si las citas de Meta doblan las del calendario,
  tienes este problema.
- **Una reserva no es una llamada.** Las citas de Meta no son las llamadas reales: decide con el coste por cita
  celebrada (*show*) que da `ghl.py por-anuncio`, no con el evento de Meta `[EMPIRICAL]`.
- Para optimizar a cita, la reserva tiene que guardar los datos de contacto (email y teléfono) antes de mandarse:
  sin ellos no se puede casar con el clic.

---

## 6. Click-to-WhatsApp y DM

- La señal de mensajería se monta con `docs/guias/mensajeria.md`. La acción CAPI de GHL no cubre mensajería y GHL
  no reenvía el `ctwa_clid` `[EMPIRICAL]`.
- En WhatsApp, usa la vía sin clic (teléfono hasheado + `page_id` + WABA) o una suscripción propia al webhook (§3 de
  esa guía). El cambio de etapa sale por un webhook del workflow (*Pipeline Stage Changed*, «Allow Multiple») hacia
  la plantilla.

Contexto: `meta-ads-kb/07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md` y
`12-whatsapp-business-platform-medicion-revenue.md`.

---

## 7. Verificar y leer por anuncio

1. **En el momento:** Events Manager → dataset → *Probar eventos*. Mira que llega cada etapa, con qué parámetros y que
   no se duplica con el navegador.
2. **A las 48–72 horas** (`meta-ads-kb/04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md`
   §1.2): cobertura de al menos el 60 % de los leads de Meta con eventos de CRM, `event_time` siempre posterior a la
   creación del lead y las etapas en el orden del embudo.
3. **Por anuncio, del lead al cobro:**
   ```
   python3 -I herramientas/ghl.py por-anuncio --cliente acme --desde 2026-10-01 --hasta 2026-10-31
   ```
   - Agregados en `clientes/acme/datos/ghl-por-anuncio_<desde>_<hasta>.csv`: leads, cualificados, citas, shows,
     clientes de pago y cash por anuncio. Lo lee `registro_creativo.py`.
   - Una fila por lead (IDs, fechas y sí/no, sin nombres) en `clientes/acme/privado/leads-ghl_<desde>_<hasta>.csv`.
     Lo lee `embudo.py cohortes`.
   - Trabaja por **cohorte**: los contactos creados en el periodo y lo que les pasó hasta hoy. Los leads recientes
     aún no han tenido tiempo de cerrar.
   - «Cualificado» = oportunidad ganada o en la etapa que contiene «cualific» (o «qualif») o en una posterior. Si tu
     etapa se llama de otra forma: `--cualificado "Apto"`.
   - `embudo.py cohortes --por semana|anuncio` lee las etapas del contrato (§16): lead, diagnóstico, cualificado,
     cita, show, no show, propuesta, venta y perdido, en español o en inglés. Las columnas de diagnóstico y propuesta
     solo salen si tu pipeline las tiene; una etapa que no reconoce cuenta como lead y te lo avisa.
4. **Por qué se pierden y quién falta a la llamada:**
   ```
   python3 -I herramientas/ghl.py oportunidades --cliente acme --desde 2026-10-01 --hasta 2026-10-31
   python3 -I herramientas/ghl.py citas --cliente acme --desde 2026-10-01 --hasta 2026-10-31
   ```
   - `oportunidades` añade el **motivo de pérdida** de HighLevel a cada oportunidad (`motivo_perdida`) y los cuenta
     (`por_motivo_perdida`; las perdidas sin motivo salen como «(sin motivo)»). Necesita el scope
     `opportunities.readonly`; si no puede leer los nombres, lo avisa. Si muchas se pierden por «no cualifica»,
     el problema está antes de la llamada: el formulario o el anuncio.
   - `citas` da dos *show rates*: el de siempre (shows entre citas ya celebradas, sin canceladas) y el estricto
     (`show_rate_estricto`, que cuenta también las canceladas y reprogramadas cuya fecha ya pasó). Si los dos se
     separan mucho, la gente cancela en vez de faltar: mira los recordatorios y el tiempo hasta la cita.
5. **Checklist antes de escalar** (`04-…` §5): Lead ID en cada lead de Meta (muestra de 20), primera etapa llegando
   en al menos el 60 %, alertas si falla el envío y definición de etapas escrita.

## Si algo falla

| Síntoma | Causa probable |
|---|---|
| Los leads del formulario no llegan a GHL | Acceso a clientes potenciales restringido o la Página reconectada por otra persona |
| `ghl.py` sale con 2 y «403» | Falta un scope de lectura o el Location ID no es de ese token |
| Contactos de Meta sin anuncio | URL sin la plantilla de UTMs, formulario incrustado sin script de GHL o formulario instantáneo sin campo de anuncio |
| Solo llega la primera etapa a Meta | Workflow sin «Allow Multiple» |
| `Purchase` sin valor o en USD | Valor de la oportunidad vacío o moneda sin poner en la acción |
| Citas de Meta ≈ el doble que las del calendario | `Schedule` por navegador y por servidor sin `event_id` común |
