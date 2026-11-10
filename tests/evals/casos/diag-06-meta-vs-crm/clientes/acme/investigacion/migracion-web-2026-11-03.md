# Migración de la web (2026-11-03)

- La landing pasó del CMS antiguo al constructor nuevo. El formulario ahora envía los datos a GHL por webhook.
- El píxel se instaló con la plantilla del constructor: el evento `Lead` se dispara al pulsar «Enviar» (antes, en la
  página de gracias tras el envío correcto).
- El evento de servidor `Lead` lo envía GHL al crear el contacto (integración CAPI de GHL). Tras la migración nadie
  revisó qué identificador se pasa al webhook.
- Errores de validación del formulario nuevo (teléfono con prefijo): el 22 % de los envíos fallan al primer intento
  (dato del constructor, semana del 2026-11-09).
