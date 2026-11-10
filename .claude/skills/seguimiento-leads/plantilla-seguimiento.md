# Plan de seguimiento comercial · <Cliente> · <AAAA-MM-DD>

> Lo monta y lo activa el usuario en GHL (Automation → Workflows). El OS no envía mensajes. Las variables entre `<…>`
> se sustituyen por el valor personalizado que corresponda en el selector de GHL. Ejemplos con Acme Automations
> (ficticia). Sin datos personales en este archivo.

## 1. Línea base (periodo AAAA-MM-DD → AAAA-MM-DD, semanas completas)

| Métrica | Hoy | Objetivo | Evidencia | Fuente |
|---|---|---|---|---|
| Mediana lead → primer mensaje automático | | < 1 min | [STRONG INFERENCE] | Muestra de 20 leads en GHL |
| Mediana lead → primer intento humano (en horario) | | < 5 min | [STRONG INFERENCE] | Muestra de 20 leads |
| % de leads con cita | | | | `ghl.py por-anuncio` |
| Mediana horas hasta la cita | | ≤ 72 h | [EMPIRICAL] débil | `ghl.py por-anuncio` |
| Show estricto (celebradas / agendadas, con canceladas) | | | | `ghl.py citas` |
| Asistió → propuesta | | | | `embudo.py cohortes` |
| Propuesta → ganado | | | [HYPOTHESIS] hasta 10 propuestas propias | `embudo.py cohortes` |
| Propuestas abiertas con más de 14 días | | 0 sin tarea | [HYPOTHESIS] | `audiencias_meta.py etapas --sin-archivos` |
| Perdidos con motivo de la lista cerrada | | 100 % | | Exportación de oportunidades |

Cuello más caro (en euros, con `analista-cuantitativo`): <etapa> · <cuánto vale +X pp>.

## 2. Consentimientos

| Uso | Base | Dónde consta | Workflows |
|---|---|---|---|
| Responder a su solicitud y gestionar la cita | Solicitud de la persona | Formulario | W1–W5, W8 |
| Comunicaciones comerciales (nurture, reactivación) | Consentimiento o relación previa | <texto exacto del formulario> | W6, W7 |
| WhatsApp iniciado por la empresa | Opt-in guardado | <campo o etiqueta en GHL> | Plantillas de W1, W3, W4 |

Supresión: contactos con DND, etiqueta de baja o que responden BAJA salen de todos los workflows comerciales.

## 3. Workflows

Formato de cada uno: **Disparador** · **Filtros** · **Pasos** (con esperas) · **Salida** · **Responsable** · **Métrica**.

### W1 · Primer contacto (velocidad de respuesta)
- **Disparador:** el de la fuente del lead (envío del formulario de la web o del formulario instantáneo sincronizado;
  elige el disparador en GHL y compruébalo con un lead de prueba propio).
- **Filtros:** etapa `lead`; no DND.
- **Pasos:**
  1. Crear o actualizar la oportunidad en la etapa `lead` del pipeline (§16).
  2. Asignar al comercial de guardia y notificación interna inmediata con el enlace al contacto.
  3. WhatsApp (si hay opt-in) o SMS + email, al momento.
  4. Tarea «Llamar antes de 5 minutos» al comercial asignado.
- **Salida:** responde, reserva o cambia de etapa.
- **Responsable:** <comercial de guardia>. **Métrica:** mediana lead → primer intento humano.

Texto (WhatsApp o SMS):
> Hola {{contact.first_name}}, soy <nombre del comercial>, de Acme Automations. Has pedido el diagnóstico de horas en
> facturas. Para revisarlo contigo te propongo 20 minutos: ¿<hueco 1> o <hueco 2>? Si prefieres elegir tú:
> <enlace de reserva>. Si no era para ti, responde NO y no te escribimos más.

Email (asunto «Tu diagnóstico de Acme Automations»):
> Hola {{contact.first_name}}: gracias por hacer el diagnóstico. Lo que nos cuentas sobre <proceso> tiene arreglo y
> queremos verlo contigo con tus números. Elige hueco aquí: <enlace de reserva> (20 minutos, por videollamada). Si
> ahora no es el momento, contesta a este email y lo dejamos para más adelante.

### W2 · Cadencia hasta contactar (6 intentos en 48–72 h)
- **Disparador:** W1 terminado sin respuesta ni reserva.
- **Pasos:** llamada a los 5 min · WhatsApp a las 2 h · llamada a las 24 h · email a las 26 h · llamada a las 48 h ·
  último mensaje a las 72 h. Solo en horario del equipo.
- **Salida:** responde o reserva (pasa a W3); al sexto intento sin respuesta, etapa `perdido` con motivo «no
  contesta» y, si hay consentimiento comercial, a W6.
- **Métrica:** % contactado en total e intentos hasta contacto.

Último mensaje:
> {{contact.first_name}}, te escribo por última vez sobre el diagnóstico de <proceso>. Si más adelante quieres
> verlo, reserva aquí cuando te venga bien: <enlace de reserva>. Un saludo.

### W3 · Confirmación y recordatorios (asistencia)
- **Disparador:** «Customer Booked Appointment» (calendario de la llamada). Reprogramar crea una cita nueva y vuelve
  a disparar el workflow.
- **Pasos:**
  1. Al momento: confirmación con vídeo corto y tarea previa; mover la oportunidad a `llamada`.
  2. Espera relativa a la cita: 24 h antes → recordatorio con reconfirmación activa («responde SÍ»).
  3. Si a las 4 h no hay respuesta: tarea de llamada humana de reconfirmación.
  4. Espera relativa a la cita: 1–2 h antes → recordatorio con el enlace de la videollamada.
  Si la cita se reserva con menos de 24 h, el paso 2 se salta (opción de GHL para cuando la hora ya ha pasado).
- **Salida:** cita cancelada (pasa a W4 si no reprograma) o celebrada.
- **Métrica:** show estricto, por anuncio y por plazo de reserva.

Confirmación:
> Hecho, {{contact.first_name}}: hablamos el {{appointment.start_time}}. Antes, mira este vídeo de 2 minutos sobre qué
> haremos en la llamada: <enlace al vídeo>. Si puedes, trae <tarea previa, p. ej. cuántas facturas de proveedor
> entraron el mes pasado>. ¿Necesitas cambiar la hora? <enlace para reprogramar>.

24 h antes:
> {{contact.first_name}}, mañana hablamos ({{appointment.start_time}}). ¿Me confirmas con un SÍ? Si te viene mal,
> cámbiala aquí en un clic: <enlace para reprogramar>.

1–2 h antes:
> En un rato nos vemos: <enlace a la videollamada>. Si se te complica, dímelo y buscamos otro hueco.

### W4 · No se presentó (recuperación)
- **Disparador:** «Appointment Status» con el estado No-show (lo marca el comercial al acabar la hora).
- **Pasos:** mensaje a los 10 min · llamada humana el mismo día · mensaje a las 24 h · último a las 72 h. Mover la
  oportunidad a la etapa de no-show del pipeline.
- **Salida:** reserva de nuevo (vuelve a W3) o, tras el último, `perdido` con motivo «no-show sin reprogramar».
- **Métrica:** % de no-shows que reprograman y asisten.

A los 10 min:
> {{contact.first_name}}, te esperábamos a las <hora de la cita>. Pasa a todo el mundo: ¿te va mejor otro momento esta
> semana? <enlace de reserva>

72 h:
> Te dejo el enlace por si quieres retomarlo cuando te venga bien: <enlace de reserva>. No te escribo más sobre esta
> cita.

### W5 · Propuesta abierta
- **Disparador:** «Pipeline Stage Changed» a `propuesta`.
- **Pasos:** día 0 resumen y siguiente paso con fecha (idealmente acordado en la llamada) · día 2 dudas · día 7 caso
  del mismo tipo de proyecto · día 14 opción de piloto o cierre amable · tarea humana en cada paso. Alerta interna si
  sigue abierta a los 21 días [HYPOTHESIS].
- **Salida:** etapa `ganado` o `perdido` (con motivo).
- **Métrica:** propuesta → ganado y días hasta la decisión.

Día 2:
> {{contact.first_name}}, ¿has podido ver la propuesta? Si alguna parte del alcance o del plazo no encaja, dímelo y la
> ajustamos. ¿Te va bien comentarla 15 minutos el <día>?

Día 7 (con un caso aprobado en `/casos-y-creadores`):
> Te paso cómo lo hicimos en <sector>: <resultado aprobado, con su rango>. Es muy parecido a lo que te proponemos para
> <proceso>. ¿Lo vemos?

Día 14:
> No quiero insistir más de la cuenta. Si ahora no es el momento, lo dejamos aparcado y te escribo en unos meses. Si
> prefieres empezar con algo más pequeño, podemos hacer un piloto de <alcance del piloto>. ¿Qué prefieres?

### W6 · Nurture con prueba (solo con consentimiento comercial)
- **Disparador:** entrada en `perdido` con motivo «mal momento» o «no compensa todavía», o fin de W2/W4 sin respuesta.
- **Pasos:** un email cada 2–4 semanas [STRONG INFERENCE]: caso del sector, demo corta, respuesta a una objeción
  («¿y si lo hacemos internamente?», «¿qué pasa con los datos?»), invitación al taller mensual. Re-diagnóstico a los
  6 meses.
- **Salida:** responde, reserva, se da de baja o pasan 12 meses.
- **Métrica:** % que vuelve a `llamada` en 6 meses.

### W7 · Reactivación de antiguos (una tanda, la lanza una persona)
- **Quién entra:** perdidos por timing o sin respuesta hace 3–12 meses, con consentimiento comercial vigente y sin DND.
- **Cómo:** el usuario selecciona la lista en GHL y lanza una sola tanda; no hay disparador automático.
- **Texto:**
> Hola {{contact.first_name}}, hace unos meses hablamos de automatizar <proceso>. Desde entonces lo hemos hecho en
> <sector> con este resultado: <resultado aprobado>. ¿Quieres que lo revisemos con tus números de ahora? Si no te
> interesa, responde BAJA y no te escribimos más.
- **Métrica:** respuestas, citas y propuestas de la tanda (por separado del resto).

### W8 · Higiene del pipeline
- Al pasar a `perdido`: motivo obligatorio de la lista cerrada (no contesta · no cualifica · sin presupuesto · no
  decide · mal momento · eligió a otro · lo hará internamente · no-show sin reprogramar).
- Al acabar la hora de una cita sin estado: tarea al comercial para marcar asistió o no-show ese mismo día.
- Lead sin primer intento humano a los 15 min: aviso interno al responsable.
- Cada cambio de etapa envía su evento a Meta por la CAPI de CRM (`/implementar-capi`).

### W9 · Taller (si el cliente capta con talleres o webinars)
- **Pipeline:** «Taller» de `/webinar` (Registrado → Asistió al taller → Se quedó a la oferta → Cualificado → Llamada
  agendada → …), con la etiqueta `taller-<AAAA-MM-DD>` de la edición.
- **Disparadores:** «Pipeline Stage Changed» a Registrado (confirmación y recordatorios) y, al acabar el taller, la
  etapa o la etiqueta que deja la importación de asistentes (repetición y D+1).
- **Pasos:** confirmación al registrarse (añadir al calendario y tarea previa) · D-1 · 1–2 h antes · al empezar, con el
  enlace · al acabar, repetición a quien no vino (etiqueta `taller-repeticion` si la ve) · D+1 a quien asistió, con la
  invitación a la llamada.
- **Salida:** reserva la llamada (pasa a W3), pide la baja o pasan 7 días tras el taller.
- **Métrica:** registro → asistió (en directo), asistió → llamada, y llamada → propuesta por edición.

Al registrarse:
> Hecho, {{contact.first_name}}: estás dentro del taller «<título>» el <fecha y hora con zona horaria>. Añádelo al
> calendario: <enlace al calendario>. Si puedes, trae <tarea previa>. Te mando el enlace el mismo día.

Al empezar:
> Empezamos: <enlace a la sala>. Si llegas tarde, entra igual.

D+1 a quien asistió:
> Gracias por venir ayer, {{contact.first_name}}. Si quieres ver cómo quedaría <proceso> en tu empresa, reserva
> 20 minutos con nosotros: <enlace de reserva>.

Repetición a quien no vino:
> Ayer no pudiste venir: aquí tienes la repetición hasta el <fecha de caducidad>: <enlace a la repetición>.

## 4. Qué se monta primero

1. <workflow> — porque <cuello más caro>.
2. <workflow>.
3. <workflow>.

## 5. Cómo se mide

| Cambio | Diseño | Éxito | Cuándo se evalúa | Orden |
|---|---|---|---|---|
| <W3 con reconfirmación humana> | Reparto aleatorio 50/50 con etiquetas `<flujo>` y `<rama-antigua>` | asistio | 4 semanas y ≥ 30 citas por rama [HYPOTHESIS] | `audiencias_meta.py medir --archivo <oportunidades> --contactos <contactos> --etiqueta-grupo … --etiqueta-control … --exito asistio` |

Fecha de evaluación: AAAA-MM-DD. Anotado en el change log: sí / no.
