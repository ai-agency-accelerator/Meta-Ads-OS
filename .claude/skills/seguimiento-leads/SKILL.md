---
name: seguimiento-leads
description: "Diseña el seguimiento comercial tras el lead en GHL: velocidad de respuesta, secuencias por canal, confirmaciones y recordatorios para subir la asistencia, recuperación de no-shows, propuestas abiertas, nurture con casos y reactivación con consentimiento. Deja workflows con textos listos; nunca envía mensajes. Mide con ghl.py y embudo.py."
argument-hint: "<cliente> [todo|respuesta|asistencia|no-show|propuestas|nurture|reactivar|taller|medir]"
---

# /seguimiento-leads

Entrada: `$ARGUMENTS` (cliente y, opcionalmente, la parte del ciclo). Sin parte, todo el ciclo, con el cuello más caro
primero. En venta consultiva (proyectos de miles de euros, pocos leads, semanas de ciclo), responder rápido, conseguir
que vengan a la llamada y cerrar las propuestas abiertas vale más que bajar el CPL: subir el show del 50 % al 80 %
aumenta en un 60 % lo que puedes pagar por lead sin tocar Meta (`meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md` §4).

- **Marco:** `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md` (§1 qué dicen los
  estudios, §2 SLA, §3 calendario, recordatorios y definición estricta del show, §4 valor en euros, §5 efecto en la
  señal), `meta-ads-kb/05-leadgen-high-ticket-crm/09-sales-feedback-loop.md` (§2 campos del CRM y lista cerrada de
  motivos de pérdida, §5 informe por anuncio, §6 rituales), `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`
  (§9 el ciclo comercial: primer mensaje, asistencia, propuesta investigada, ciclo largo),
  `meta-ads-kb/14-playbooks/playbook-high-ticket.md` §5 (setter y reconfirmación),
  `meta-ads-kb/05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md` §6 (reserva y nurturing en el formulario),
  `meta-ads-kb/07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md` §3 (plantillas
  marketing y utility, opt-in) y `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md`
  §2 (consentimiento; implementación, no asesoría legal).
- **Agentes:** `especialista-crm` (exportaciones, pipeline y workflows de GHL), `especialista-funnel` (proceso
  comercial y show), `analista-cuantitativo` (valor en euros de cada mejora y lectura de la prueba), `gestor-cliente`
  (si la ficha dice `relacion: cliente`: el equipo comercial es del cliente).
- **Herramientas:** `ghl.py` (`por-anuncio`, `citas`, `oportunidades`), `embudo.py cohortes`,
  `audiencias_meta.py etapas --sin-archivos` (recuento por etapa y antigüedad de las propuestas) y
  `audiencias_meta.py medir` (prueba de un workflow contra otro). Plantilla: `plantilla-seguimiento.md`.
- **Lee:** ficha (economía por etapa, `crm`, `zona_horaria`, horario y equipo si está), plan de funnel de
  `/disenar-funnel` en `planes/`, `cohortes-leads.md` y el último informe de `/embudo`.
- **Escribe:** `clientes/<slug>/planes/seguimiento-<AAAA-MM-DD>.md` y, con datos de personas, solo
  `clientes/<slug>/privado/`.

## Reglas

- **El OS nunca envía mensajes, emails ni WhatsApp a contactos.** Diseña los workflows y los textos; el usuario los
  monta y los activa en GHL. Tampoco los crea por el MCP de GHL: un workflow que escribe a personas lo enciende una
  persona.
- **Consentimiento** (implementación, no asesoría legal):
  - confirmaciones y recordatorios de una cita que la persona ha pedido son comunicación de servicio; nurture,
    reactivación y ofertas son comunicación comercial y piden consentimiento previo o relación previa con un servicio
    parecido, con baja sencilla en cada mensaje (LSSI art. 21 en España) **[STRONG INFERENCE]**;
  - WhatsApp iniciado por la empresa pide opt-in guardado y plantilla aprobada; una plantilla de utilidad con contenido
    promocional se cobra y se trata como marketing (`07-…/12-…` §3, **[OFFICIAL META]**);
  - el texto de consentimiento del formulario manda: si no cubre marketing, W6 y W7 se quedan fuera.
- **Los leads de formulario instantáneo solo se pueden descargar de Meta durante 90 días** **[OFFICIAL META]**
  (verificado el 2026-11-09): la sincronización con GHL tiene que estar viva desde el primer día.
- Nada de datos personales fuera de `privado/`; en el chat y en el plan, solo recuentos y medianas.
- No inventes resultados en los mensajes: cifras y casos solo los aprobados en `/casos-y-creadores`.

## Pasos

1. **Contexto.** Quién responde y en qué horario, cuántas llamadas caben por semana, canales conectados en GHL
   (WhatsApp por API, SMS, email con dominio propio, llamada), cómo se reserva (calendario en el formulario o en la
   página de gracias, o «te llamamos»), qué dice el consentimiento del formulario, tuteo o usted con sus clientes.
   Pregunta solo lo que falte en la ficha y en el plan de funnel.
2. **Línea base** con 4–8 semanas completas y cohortes maduras (ventana de atribución de la ficha):
   - `python3 -I herramientas/ghl.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>` → leads,
     cualificados, citas, shows y clientes por anuncio, y `horas_hasta_cita_mediana`;
   - `ghl.py citas` con el mismo periodo → por estado. Calcula el show **estricto** a mano: celebradas / todas las
     agendadas, con canceladas y reprogramadas en el denominador (`08-…` §3.4). El `show_rate` de `ghl.py` excluye las
     canceladas y sale más alto;
   - `ghl.py oportunidades` (a `privado/`) y luego
     `python3 -I herramientas/audiencias_meta.py etapas --cliente <slug> --archivo <oportunidades> --contactos <contactos> --sin-archivos`
     → contactos por etapa del §16, no-shows abiertos, propuestas con más de 14 días **[HYPOTHESIS]** y perdidos por
     timing (si la exportación trae el motivo);
   - `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por semana --modelo servicios` → tasas entre etapas;
   - **velocidad de respuesta:** `ghl.py` no lee conversaciones. Toma 20 leads recientes, mira en GHL la hora del lead
     y la del primer mensaje automático y del primer intento humano, apúntalo en `privado/` y saca la mediana y el % en
     menos de 5 minutos en horario.
3. **Diagnóstico y objetivos.** Tabla etapa → hoy → objetivo → evidencia, con los objetivos del SLA de `08-…` §2
   **[STRONG INFERENCE]**: lead en el CRM y mensaje automático en menos de 1 minuto, primer intento humano en menos de
   5 en horario, 6 intentos en 48–72 h, reserva en el primer contacto, citas a 72 h o menos (`08-…` §3.1,
   **[EMPIRICAL]** débil) y etiqueta de resultado el mismo día. Pon cada hueco en euros con `analista-cuantitativo`
   (`08-…` §4) y ordénalos: el más caro primero. Con menos de 30 citas al mes, mira trimestres (`08-…` §3.4).
4. **Workflows.** Rellena los que toquen de `plantilla-seguimiento.md` (W1 primer contacto, W2 cadencia, W3
   confirmación y recordatorios, W4 no-show, W5 propuesta abierta, W6 nurture con prueba, W7 reactivación, W8 higiene
   del pipeline y, si el cliente capta con talleres, W9 taller con el pipeline «Taller» de `/webinar`). Cada uno con disparador de GHL, filtros, pasos y esperas, canal, texto listo, condición de salida,
   responsable humano y métrica. Reglas:
   - un workflow por objetivo; salida en cuanto la persona responde, reserva, cambia de etapa o pide la baja;
   - el humano entra donde más rinde: primer intento en minutos, reconfirmación de citas sin respuesta, no-show del
     mismo día y propuestas (playbook de consultoras §9);
   - propuestas: seguimiento a los 2, 7 y 14 días con algo nuevo cada vez (una duda resuelta, un caso del mismo tipo de
     proyecto, una opción de piloto) y, después, nurture **[HYPOTHESIS]** sobre la cadencia;
   - perdidos: el motivo es obligatorio y de la lista cerrada (`09-sales-feedback-loop.md` §2); los de «mal momento»
     pasan a nurture, nunca a una reactivación agresiva;
   - variables: `{{contact.first_name}}` y `{{appointment.start_time}}` existen en GHL; lo demás va entre `<…>` para
     que el usuario elija el valor en el selector de GHL;
   - leads de las páginas de `/construir-landing`: el envío trae las casillas `acepta_*` (por ejemplo,
     `acepta_whatsapp` y `acepta_novedades`, `true`/`false`) y, en un diagnóstico, `diagnostico.nivel`
     (`plantillas/paginas/README.md`, envío v1). Úsalos para etiquetar y elegir secuencia; sin la casilla de WhatsApp
     en `true`, nada por WhatsApp.
5. **Textos.** Cortos, en el tono del cliente, con quién escribe, por qué (lo que pidió), qué propones (dos huecos
   concretos) y cómo decir que no. Nada de presión ni de urgencia falsa. Clasifica cada plantilla de WhatsApp como
   utilidad o marketing antes de pedir su aprobación.
6. **Anuncios.** Si una etapa merece anuncios además del seguimiento (no-show, propuesta, perdido por timing,
   clientes), apúntalo y deriva a `/anuncios-por-etapa`. Los anuncios no arreglan un seguimiento roto: primero W3–W5.
7. **Medición** (modo `medir`):
   - mejor que antes y después, una prueba: rama A y rama B con el reparto aleatorio de GHL, cada rama con una etiqueta,
     y `python3 -I herramientas/audiencias_meta.py medir --cliente <slug> --archivo <oportunidades nuevas> --contactos <contactos nuevos> --etiqueta-grupo <etiqueta del flujo> --etiqueta-control <etiqueta de la rama antigua> --exito asistio`
     (o `--exito propuesta` / `ganado`). `--contactos` es obligatorio con `ghl.py`: las etiquetas van en los contactos,
     no en las oportunidades (sin ellas, `medir` se niega a medir). Sin reparto aleatorio, alterna semanas (`08-…` §4) y dilo en el informe;
   - evalúa a 4 semanas o más y con 30 citas o más por rama **[HYPOTHESIS]**; por anuncio, con menos de 10 shows no
     concluyas (`09-…` §5);
   - tiempo hasta la llamada, asistencia, propuesta y cierre por anuncio: `ghl.py por-anuncio`,
     `audiencias_meta.py etapas --sin-archivos --por-anuncio` (cuántos llegaron a propuesta y a ganado, también los
     perdidos después) y `embudo.py cohortes --por anuncio`.
8. **Guarda** el plan en `clientes/<slug>/planes/seguimiento-<AAAA-MM-DD>.md` con la plantilla: línea base,
   objetivos, workflows con textos, consentimientos, qué se monta primero, cómo se mide y fecha de evaluación. Cuando el
   usuario active un workflow, anótalo en `clientes/<slug>/change-log.md` (nivel `crm`, de → a, métrica y fecha de
   evaluación). Si `relacion: cliente`, `gestor-cliente` prepara el mensaje para su equipo comercial.

## Qué no verificamos

Comprobado en la ayuda oficial de GHL el 2026-11-09: los disparadores «Customer Booked Appointment», «Appointment
Status» (con el filtro No-show) y «Pipeline Stage Changed»; las acciones Wait (también relativa a la hora de la cita),
If/Else, Goal Event, Send SMS, Email, WhatsApp, Internal Notification, Assign to User, Add Task y Create/Update
Opportunity. Sin verificar: el disparador «Stale Opportunities», los porcentajes del reparto aleatorio (solo terceros),
los disparadores de formulario y el resto de valores personalizados. Si el selector de GHL no los muestra, el plan dice
cómo sustituirlos.
