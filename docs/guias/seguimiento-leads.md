# Seguimiento de leads en GHL, paso a paso

Para quién: consultoras, agencias de IA y automatización y SaaS que venden con llamada y propuesta (proyectos de miles
de euros, pocos leads, ciclos de semanas) y trabajan en GoHighLevel («GHL»).
Qué consigues: que cada lead reciba respuesta en minutos, que más gente venga a la llamada, que las propuestas no se
queden olvidadas y que los «ahora no» vuelvan, con los textos ya escritos y una forma de saber si cada cambio funciona.

Lo diseña `/seguimiento-leads`; lo montas y lo activas tú en GHL. **El sistema nunca envía mensajes a tus contactos.**
El porqué está en `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md` y en el
playbook `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §9.

Las etiquetas `[OFFICIAL META]`, `[EMPIRICAL]`, `[HYPOTHESIS]`… son las de la base de conocimiento. «No verificado»
quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09: compruébalo en tu pantalla.

---

## 0. Antes de empezar

- **Pipeline con las etapas del embudo** (`lead → diagnostico → cualificado → llamada → asistio → propuesta → ganado /
  perdido`), con los nombres visibles que quieras, y una lista cerrada de motivos de pérdida. Si aún no lo tienes:
  `docs/guias/ghl-meta.md` §4.
- **Lectura de GHL** con `ghl.py` (token de solo lectura): `docs/guias/ghl-meta.md` §1.
- **Canales conectados en GHL:** email con tu dominio, SMS o WhatsApp por la API (con plantillas aprobadas) y un
  calendario para la llamada.
- **El texto de consentimiento de tu formulario.** Decide qué puedes enviar: responder a lo que la persona ha pedido y
  recordarle su cita es servicio; nurture y reactivación son comunicación comercial y piden consentimiento o relación
  previa, con baja en cada mensaje (en España, LSSI art. 21). Esto es implementación, no asesoría legal.
- **Formularios instantáneos:** Meta solo guarda los leads 90 días para descargarlos **[OFFICIAL META]**. Conecta la
  sincronización con GHL antes de lanzar (`docs/guias/ghl-meta.md` §2).

## 1. Saca la línea base

Con semanas completas y un periodo de 4 a 8 semanas:

```
python3 -I herramientas/ghl.py por-anuncio --cliente acme --desde 2026-09-14 --hasta 2026-11-08
python3 -I herramientas/ghl.py citas --cliente acme --desde 2026-09-14 --hasta 2026-11-08
python3 -I herramientas/ghl.py oportunidades --cliente acme --desde 2026-03-01 --hasta 2026-11-08
python3 -I herramientas/ghl.py contactos --cliente acme --desde 2026-03-01 --hasta 2026-11-08
python3 -I herramientas/audiencias_meta.py etapas --cliente acme \
    --archivo clientes/acme/privado/ghl-oportunidades_2026-03-01_2026-11-08.csv \
    --contactos clientes/acme/privado/ghl-contactos_2026-03-01_2026-11-08.csv --sin-archivos --por-anuncio
python3 -I herramientas/embudo.py cohortes --cliente acme --por semana --modelo servicios
```

- `por-anuncio` te da leads, citas, asistencias y ventas por anuncio y la mediana de horas hasta la cita.
- El **show** que cuenta es el estricto: llamadas celebradas / todas las agendadas, con canceladas y reprogramadas en
  el denominador. `ghl.py citas` lo da como `show_rate_estricto` (las canceladas y reprogramadas cuya fecha ya pasó
  cuentan); su `show_rate` de siempre deja fuera las canceladas.
- `ghl.py oportunidades` añade el **motivo de pérdida** de HighLevel (`motivo_perdida`) y el recuento por motivo. Va en
  el CSV de `privado/`, y `etapas` lo usa para separar los perdidos por timing.
- `etapas --sin-archivos` no escribe nada: cuenta cuántos hay en cada etapa, cuántos no se presentaron, cuántas
  propuestas llevan más de 14 días paradas y, por anuncio, cuántos llegaron a propuesta y a ganado.
- **Velocidad de respuesta:** `ghl.py` no lee conversaciones. Abre 20 leads recientes en GHL, apunta la hora del lead,
  la del primer mensaje automático y la del primer intento humano en una hoja dentro de `clientes/acme/privado/` y
  saca la mediana. Así sabes de dónde partes.

## 2. Pide el plan

```
/seguimiento-leads acme
```

Te deja `clientes/acme/planes/seguimiento-AAAA-MM-DD.md` con la línea base, los objetivos ordenados por lo que valen en
euros y los workflows (W1 primer contacto, W2 cadencia, W3 confirmación y recordatorios, W4 no-show, W5 propuesta
abierta, W6 nurture, W7 reactivación, W8 higiene) con los textos escritos. Para una sola parte:
`/seguimiento-leads acme asistencia`.

## 3. Monta cada workflow en GHL

1. **Automation → Workflows → Create Workflow → Start from scratch.** Ponle el nombre del plan («W3 · Confirmación y
   recordatorios»).
2. **Add New Trigger** y elige el del plan:
   - W3: «Customer Booked Appointment», con el filtro del calendario de la llamada;
   - W4: «Appointment Status», con el estado No-show;
   - W5: «Pipeline Stage Changed», con el pipeline y la etapa de propuesta.
3. **Añade los pasos** con «+»: Send SMS, Email o WhatsApp con el texto del plan, Wait, If/Else, Add Task, Internal
   Notification, Assign to User, Create/Update Opportunity.
   - Para los recordatorios, el **Wait** relativo a la cita: «24 horas antes» y «1 hora antes» de la hora de la cita.
     Activa la opción para cuando esa hora ya ha pasado (si alguien reserva para dentro de 3 horas, el de 24 h se
     salta).
   - Las variables: `{{contact.first_name}}` y `{{appointment.start_time}}` existen. Lo que va entre `<…>` en el plan
     lo eliges tú en el selector de valores personalizados (el enlace de reserva, el de la videollamada…).
4. **Condición de salida:** un Goal Event (respondió, reservó, cambió de etapa) para que nadie reciba un recordatorio
   de algo que ya hizo.
5. **Prueba con tu propio contacto** (tu email, tu teléfono) y un calendario de prueba. Nunca con leads reales.
6. **Publica** el workflow (de borrador a publicado) y anota en `clientes/acme/change-log.md` qué has activado, la
   métrica y la fecha de evaluación.

Monta primero el que ataca el cuello más caro; uno por semana es un buen ritmo para poder ver qué hace cada uno.

## 4. WhatsApp: plantillas y opt-in

- Fuera de la ventana de 24 h desde el último mensaje de la persona, WhatsApp solo deja enviar **plantillas
  aprobadas**. Los recordatorios de cita son de utilidad; nurture y reactivación, de marketing. Si una de utilidad lleva
  contenido promocional, Meta la trata y la cobra como marketing **[OFFICIAL META]**
  (`meta-ads-kb/07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md` §3).
- Sin opt-in de WhatsApp guardado en el contacto, usa SMS o email.

## 5. Mide si funciona

Antes y después engaña: cambian los anuncios, la época y el equipo. Mejor una prueba:

1. En el workflow, un reparto aleatorio: la mitad recibe la versión nueva y la otra mitad la de siempre. Cada rama pone
   una etiqueta (`w3-nuevo`, `w3-antiguo`) y las dos la del flujo (`w3`).
2. A las 4 semanas y con al menos 30 citas por rama **[HYPOTHESIS]**, exporta de nuevo y compara:
   ```
   python3 -I herramientas/audiencias_meta.py medir --cliente acme \
       --archivo clientes/acme/privado/ghl-oportunidades_2026-11-09_2026-12-13.csv \
       --contactos clientes/acme/privado/ghl-contactos_2026-11-09_2026-12-13.csv \
       --etiqueta-grupo w3 --etiqueta-control w3-antiguo --exito asistio
   ```
   Te da la tasa de cada rama, la diferencia, el test exacto de Fisher y un veredicto (suma, resta, no distinguible o
   faltan datos), con el tamaño que haría falta para verlo.
3. Sin reparto aleatorio, alterna semanas (una con la versión nueva, otra con la antigua) y dilo en el informe.
4. Por anuncio, con menos de 10 asistencias no saques conclusiones
   (`meta-ads-kb/05-leadgen-high-ticket-crm/09-sales-feedback-loop.md` §5).

## Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Llegan recordatorios a quien ya canceló | Falta la condición de salida | Goal Event «cita cancelada» o If/Else antes de cada envío |
| El recordatorio de 24 h llega después de la cita | Cita reservada con menos de 24 h | Activa la opción del Wait para cuando la hora ya ha pasado |
| Dos workflows escriben a la vez a la misma persona | Disparadores que se solapan (W2 y W3) | Al reservar, que W2 termine (Goal Event) |
| El show sale más alto que en la llamada semanal | Canceladas fuera del denominador | Cuenta estricta (§1) |
| `etapas` dice «etapas sin reconocer» | Nombres de etapa propios | `--mapa "Reunión hecha=asistio,Nurture=ignorar"` |
| `etapas` no separa perdidos por timing | La exportación no trae el motivo | Usa la de `ghl.py oportunidades` (trae `motivo_perdida`; necesita el scope `opportunities.readonly`) o etiqueta «mal-momento» al perder |
| `medir` dice «faltan datos» | Menos de 30 en el grupo de comparación o menos de 10 éxitos | Espera o junta varias semanas |

## Lo que no está verificado

Comprobado en la ayuda oficial de GHL el 2026-11-09: los disparadores «Customer Booked Appointment», «Appointment
Status» (con No-show) y «Pipeline Stage Changed», y las acciones Wait (también relativa a la cita), If/Else, Goal
Event, Send SMS, Email, WhatsApp, Internal Notification, Assign to User, Add Task y Create/Update Opportunity.
Sin verificar:
- el disparador «Stale Opportunities» (solo lo describen terceros);
- los porcentajes del reparto aleatorio (la ayuda oficial menciona el reparto, los porcentajes solo terceros);
- los disparadores de formulario y el resto de valores personalizados;
- qué columnas trae la exportación de oportunidades desde la interfaz (el motivo de pérdida puede no salir).
