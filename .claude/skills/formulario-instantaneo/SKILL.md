---
name: formulario-instantaneo
description: "Construye el formulario instantáneo de Meta de un cliente B2B: tipo, preguntas de cualificación con su ICP, lógica condicional, textos y privacidad; revisión de políticas, creación por API con confirmación o guía para Ads Manager, conexión con GHL y sus etapas, y lectura de la calidad de los leads por anuncio."
argument-hint: "<cliente> [diagnostico|llamada|recurso|taller|auditar <form_id>]"
disable-model-invocation: true
---

# /formulario-instantaneo

Entrada: `$ARGUMENTS`. En venta consultiva el formulario decide la calidad del lead más que el anuncio: es el filtro
entre «me interesa» y «una llamada que merece la pena». Esta skill **construye** el formulario de un camino ya elegido
(si aún no está claro si va formulario, landing, webinar o WhatsApp → `/disenar-funnel`). Crear un formulario no
gasta: no se usa hasta que un anuncio lo enlaza. Aun así, solo lo crea `operador-meta`, con el sí del usuario.

- **Marcos:** `meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md` (tipos, preguntas, intro, final,
  ajustes), `meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md`,
  `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`,
  `meta-ads-kb/05-leadgen-high-ticket-crm/09-sales-feedback-loop.md`, `meta-ads-kb/05-leadgen-high-ticket-crm/10-b2b-saas-local.md`,
  `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §5.2 (embudo A), §5.7 (etapas) y §6 (evento),
  `meta-ads-kb/14-playbooks/playbook-b2b.md` §4, datos restringidos en
  `meta-ads-kb/08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md` y
  `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md` §7, consentimiento en
  `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`. Guía práctica:
  `docs/guias/formularios.md`.
- **Agentes:** `revisor-politicas` (veredicto), `operador-meta` (el único que crea), `especialista-funnel` (fricción y
  final), `especialista-crm` (definición de cualificado y lectura por etapa), `ingeniero-capi` (etapas de vuelta a Meta),
  `redactor-anuncios` (si los textos necesitan la voz del cliente).
- **Herramientas:** `formularios_meta.py` (`crear --simular`, `guia`, `crear --confirmo`, `listar`, `ver`, `leads`),
  `ghl.py por-anuncio`, `embudo.py cohortes`, `economia.py`.
- **Lee:** ficha (Negocio, Economía, definición de `cualificado`, `meta.pagina`, `crm.tipo`, `zona_horaria`), `estado.md`,
  el plan de funnel si existe y el brief creativo (el formulario continúa la promesa del anuncio).
- **Escribe:** `clientes/<slug>/planes/<AAAA-MM-DD>_formulario-<oferta>.json` (y su guía `.md` si va por Ads Manager),
  `planes/formularios.json` (lo mantiene la herramienta), `change-log.md` y `estado.md` (`F1.landing`).

## Pasos

1. **Requisitos.** Ficha con quién compra (tamaño, sector, quién decide), precio de la oferta y la definición escrita
   de `cualificado`. Si falta: `/cliente-nuevo` o pregúntalo. Sin economía (coste máximo por lead cualificado) no
   se decide cuánta fricción poner → `/economia`. Con `auditar <form_id>` ve directo al paso 10.
2. **Tipo de formulario** (02 §2):

   | Situación | Tipo | Plantilla |
   |---|---|---|
   | Diagnóstico o llamada con un comercial detrás (lo normal en servicios a medida) | `mayor_intencion` (pantalla de revisión; solo Feed de Facebook e Instagram en móvil) | `diagnostico-corto` |
   | El comercial se ahoga en llamadas que no encajan, o el diagnóstico trae volumen sin calidad | `mayor_intencion` + teléfono verificado (+ email de trabajo si el ICP supera ~20 personas) | `llamada-cualificada` |
   | Guía, plantilla, checklist o taller para nutrir antes de vender | `mas_volumen` | `recurso-o-taller` |
   | Hace falta enseñar más antes de preguntar (portfolio, casos) | creatividad enriquecida: solo en Ads Manager (`guia`) | cualquiera, cambiando `tipo` |

   Si el anuncio será de colaboración con un creador (`/casos-y-creadores`), el formulario se muestra en formato
   «greeting card» (nota de B13; el nombre de la opción en Ads Manager no está verificado): revisa la vista previa así.
   Copia la plantilla de `.claude/skills/formulario-instantaneo/plantillas/` a la carpeta de planes del cliente con
   `nombre` según `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8 (`<cliente>_<oferta>_v1`).
3. **Preguntas con su ICP** (02 §4, playbook §5.2). 3–5 de opción múltiple, cada una cambia lo que hará el comercial:
   tamaño (en personas, no en facturación), proceso que más horas les quita, urgencia, papel en la decisión y, si el
   ticket lo pide, el rango de inversión **del proyecto** («un proyecto así suele empezar en X €; ¿qué rango encaja?»).
   - Si el cliente ya tiene un imán de entrada (`/iman-de-leads`, paso 2), reutiliza sus preguntas de cualificación y
     sus opciones, para que la web y Meta pidan lo mismo y los leads de las dos vías se comparen.
   - Marca en `encaje` las opciones que encajan con el ICP de la ficha. Es encaje **declarado**: sirve para priorizar
     llamadas y leer anuncios, no es `cualificado` (§16; ese lo marca el comercial tras hablar).
   - Prohibido: ingresos, patrimonio o deudas de la persona, salud, DNI, ideología, religión, orientación, contraseñas
     (la herramienta lo para). Zona gris: facturación (si la pides, de la empresa y en rangos). Nunca una pregunta
     personalizada que repita una prellenada.
   - Como mucho una respuesta corta (contexto para el comercial). Más de 5 preguntas de opción múltiple resta envíos.
   - **Lógica condicional** para quien no encaja: otro final con un recurso (`logica` + `finales_alternativos`), no un
     rechazo seco. Solo se monta en Ads Manager.
4. **Contacto y filtros.** `nombre_completo` + `email` + `telefono` por defecto. `email_trabajo` con
   `exigir_email_trabajo` solo si el ICP es de más de ~20 personas (muchas pymes usan correos personales; Meta solo lo
   aplica en Instagram o por API). `verificar_telefono` si llegan teléfonos falsos: el código va por WhatsApp o SMS,
   quien no verifica no cuenta como lead. `solo_anuncios: true` (sin leads orgánicos ni compartidos). `parametros`
   con oferta, formulario y versión: llegan al CRM y separan versiones.
5. **Textos** (02 §5–6; con `redactor-anuncios` si hace falta). Intro: qué pasa después, cuánto dura, para quién no
   es. Final principal: `reservar` con el enlace directo del calendario del partner (Calendly o HighLevel) o
   `whatsapp` si el equipo trabaja ahí. Avisa al usuario: la reserva embebida solo funciona en la app de Facebook en
   móvil y **no se reporta en Ads Manager** (vuelve por el CRM como `Schedule`). `privacidad.url` = la del cliente,
   obligatoria. `aviso_legal` con casilla opcional de comunicaciones comerciales si va a recibir algo más que la
   respuesta a su solicitud (04/09).
6. **Revisión sin red:** `python3 -I herramientas/formularios_meta.py crear <json> --simular --cliente <slug>` hasta que
   no haya errores. Lee los avisos con el usuario y decide cada uno.
7. **Políticas:** `revisor-politicas` (o `/revisar-anuncio`) sobre intro, preguntas, opciones, finales y aviso legal.
   Anota el veredicto en `revision_politicas` (`OK · AAAA-MM-DD · revisor-politicas`). `NO publicar` bloquea;
   cualquier valor que no sea `OK` u `OK con cambios aplicados` deja el formulario pendiente.
8. **Vía de creación.** El MCP oficial de Meta no tiene herramientas de formularios (comprobado el 2026-11-09):

   | Vía | Cuándo | Cómo |
   |---|---|---|
   | API | Hay token de Página (`META_TOKEN_PAGINA_<SLUG>`, o `META_TOKEN_<SLUG>` con la Página asignada) y no hay lógica, o se acepta perderla; obligatoria para exigir email de trabajo en Facebook | `operador-meta`: `formularios_meta.py crear <json> --cliente <slug> --confirmo [--sin-logica]` tras el sí explícito del usuario a ese formulario |
   | Ads Manager | Sin token, con lógica condicional o creatividad enriquecida | `formularios_meta.py guia <json> --cliente <slug> --salida clientes/<slug>/planes/<AAAA-MM-DD>_formulario-<oferta>.md`; el usuario lo monta y te da el ID |

   Enseña antes el resumen de `--simular` y la vía elegida. Después: la fila que imprime `crear` en
   `change-log.md`, `F1.landing` en `estado.md` y el ID en el plan de campaña (`destino: formulario`,
   `formulario_id`) para `/lanzar-campana`. Un formulario publicado no se edita: cada cambio es una versión nueva
   (`_v2`) y su propia fila en el change log.
9. **Conexión con el CRM** (`docs/guias/ghl-meta.md` §2 y §4; con `crm.tipo: ghl`):
   - Página conectada en GHL, acceso a clientes potenciales concedido a LeadConnector, campos mapeados (cada `clave`
     de pregunta a un campo del contacto, el *Facebook Lead ID* guardado y el anuncio en un campo personalizado).
   - Workflow con el disparador del formulario de Facebook que avise al comercial y mande el primer mensaje: objetivo
     ≤5 minutos en horario (05/08).
   - **Lead de prueba** con la herramienta de pruebas de Meta (developers.facebook.com/tools/lead-ads-testing): tiene
     que llegar a GHL en menos de un minuto con respuestas, Lead ID y anuncio. Sin esto no se lanza.
   - Etapas del §16 de vuelta a Meta (`/implementar-capi`, `ingeniero-capi`): `lead` → `Lead`, `cualificado` →
     `LeadCualificado`, `llamada` → `Schedule`, `asistio` → `LlamadaAsistida`, `propuesta` → `PropuestaEnviada`,
     `ganado` → `Purchase` con valor. Qué evento optimizar lo decide el volumen semanal (playbook §6.1); Conversion
     Leads exige la CAPI del CRM desde abril de 2026, el Lead ID en el CRM, subidas diarias y una etapa en ≤28 días con
     el 1–40 % de los leads (playbook §6.2, con los requisitos aún en disputa).
10. **Leer la calidad** (con ≥7 días y 30–50 leads; principio 7 de
    `meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`):
    - `formularios_meta.py leads <form_id> --cliente <slug> [--desde --hasta]`: encaje declarado y reparto de
      respuestas por anuncio, orgánicos y leads fuera de horario. Detalle con datos personales en `privado/`, agregados en
      `datos/`. Descárgalos al menos cada semana: Meta solo los guarda 90 días.
    - `ghl.py por-anuncio --cliente <slug> --campo-anuncio <id>` y `embudo.py cohortes --cliente <slug> --por anuncio`:
      cualificados, citas, asistencias y ventas reales por anuncio (`especialista-crm` lo interpreta).
    - Lectura: encaje alto y cualificado bajo → la definición o el comercial, no el formulario; mucho «solo me estoy
      informando» → la promesa del anuncio atrae curiosos (`/brief-creativo`); pocos leads con buen encaje → quita una
      pregunta o pasa a `email` en la versión siguiente; leads fuera de horario sin respuesta → SLA, no Meta.
    - `formularios_meta.py ver <form_id>` audita un formulario heredado contra la KB (tipo, preguntas, privacidad,
      parámetros, final, leads caducados).

Cierra con: formulario (nombre, ID o «pendiente de montar»), vía, veredicto de políticas, estado del lead de prueba y de
las etapas, y la fecha en la que se leerá la calidad.
