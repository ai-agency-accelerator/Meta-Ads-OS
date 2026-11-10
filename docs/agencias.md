# Agencias con varios clientes

Meta Ads OS está pensado para llevar tu propia captación y la de tus clientes desde la misma instalación, con cada
cliente aislado en su carpeta, sus accesos, sus topes y su historial.

## Empieza por tu propia captación

Si aún no tienes clientes de Meta Ads, el primer cliente eres tú: `/cliente-nuevo` con `relacion: propio`. Aprendes el
sistema con tu dinero y sales con un caso propio que enseñar.

- Si eres una consultora o agencia de IA y automatización que vende proyectos a pymes (diagnóstico, llamada, propuesta
  y cierre), tu playbook es `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`: economía por etapa,
  oferta de entrada, embudos según volumen, qué evento optimizar, creatividad y ciclo comercial, con el ejemplo
  completo de Acme. Apunta la ruta en la ficha (línea «Playbook» bajo «Negocio») y las skills lo usan.
- La estrategia general para captar clientes de servicios con llamada está en
  `meta-ads-kb/14-playbooks/playbook-agencias-consultores.md` (parte A); la de llevar el lead gen de un cliente, en la
  parte B.

## Un espacio por cliente

Cada cliente vive en `clientes/<slug>/`, creado con `/cliente-nuevo`:

| Archivo | Para qué, en una agencia |
|---|---|
| `ficha.md` | Su negocio, su economía, sus IDs de Meta, su CRM y sus **topes**. `relacion: cliente` lo marca como cliente de la agencia |
| `estado.md` | En qué fase está y qué le falta: lo que verás en `/hoy` |
| `change-log.md` | Cada cambio con motivo y fecha de evaluación: tu defensa en cualquier reunión |
| `registro-creativo.csv` | Cada anuncio con sus resultados de negocio: qué ángulo vende en esa cuenta |
| `informes/`, `auditorias/`, `planes/`, `creativos/`, `investigacion/` | Entregables |
| `paginas/` | Las páginas de captación que genera `/construir-landing` (landing, diagnóstico, reserva, gracias, registro a un taller), listas para subir a su hosting o a su GHL |
| `marca/` | Logo, colores y tipografías del cliente para estáticos, vídeo y páginas (`marca.json` más los archivos). La de tu agencia va en la carpeta de tu propia ficha (`relacion: propio`) y la usan los informes para clientes y las auditorías express |
| `privado/` | Exportaciones con datos personales de sus leads. Nunca se comparte |

Los datos de un cliente nunca se mezclan con los de otro: las herramientas reciben `--cliente <slug>` y leen solo su
ficha, sus claves y su carpeta.

## Entrar en la cuenta de un cliente

La forma correcta es el **acceso de partner**, no que el cliente te haga administrador de su portfolio
(`meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` §2):

1. Tu agencia tiene su propio Business Portfolio, con tu equipo dentro.
2. El cliente añade a tu agencia como partner y le comparte la cuenta publicitaria, la Página, Instagram y el dataset
   con las tareas mínimas.
3. Desde tu portfolio, asignas esos activos a las personas de tu equipo.

Los activos (cuenta, dataset, Página, dominio, método de pago) se quedan **en el portfolio del cliente**. Si algún día
os separáis, el cliente conserva su historial y tú solo pierdes el acceso. Montarlo todo en el portfolio de la agencia
es uno de los errores más caros del sector.

Si todavía no tienes acceso, `/empezar` o `/configurar-meta <cliente> agencia` te preparan el mensaje para pedirlo
(lo redacta `gestor-cliente`) y la checklist de lo que hay que comprobar al recibirlo.

## Conexiones por cliente

| Qué | Cómo se separa por cliente |
|---|---|
| MCP de Meta | Una sola conexión, con el usuario de la agencia: ve todas las cuentas a las que tienes acceso de partner. `/conectar meta` te ayuda a asignar cada cuenta a su ficha (`meta.cuenta`) |
| Token avanzado | Un usuario del sistema en el portfolio de tu agencia con acceso a las cuentas que gestionas (`META_TOKEN`), o uno por cliente (`META_TOKEN_<SLUG>`) |
| GoHighLevel | Un servidor MCP por subcuenta, llamado `ghl-<slug>` (`crm.servidor_mcp: ghl-<slug>` en su ficha), y `GHL_TOKEN_<SLUG>` para las lecturas desatendidas |
| Stripe | `STRIPE_KEY_<SLUG>` con la clave restringida de cada cliente |
| Topes | `topes.cambio_dia` y `topes.total_dia` en cada ficha, y los límites del lado de Meta en cada cuenta |

Detalle en [Conexiones](conexiones.md).

## El día a día con varios clientes

| Cuándo | Qué | Qué ganas |
|---|---|---|
| Cada mañana | El brief diario de todos tus clientes en un solo mensaje (`/brief-diario programar`, con `brief.clientes: todos` o una lista de slugs) | Saber en dos minutos si algo está roto en alguna cuenta |
| Al empezar a trabajar | `/hoy` | La lista de lo que toca en cada cliente, ordenada |
| Cada semana | `/informe-semanal <cliente>` y, para el cliente, `/informe-cliente <cliente> semanal` | El análisis interno y el informe en su lenguaje, con tu marca |
| Cada mes | `/revision-mensual <cliente>` y `/informe-cliente <cliente> mensual` | El plan del mes y la reunión preparada |
| Una vez por cuenta | `/reglas-automaticas <cliente>` | Que Meta pause o avise con tu ordenador apagado: primero en modo sombra, después activas |
| Antes de una reunión | Pide a `gestor-cliente` que la prepare | Qué ha pasado, qué viene, qué necesitas del cliente y cómo recalibrar expectativas |

`/informe-cliente` nunca envía nada: deja el informe en Markdown y PDF para que lo revises y lo mandes tú. Habla del
negocio del cliente primero (citas, ventas, coste por cliente), no del CPM.

**El KPI del contrato.** Acuerda con el cliente el coste por cita, por lead cualificado o por venta, no el CPL, y deja
por escrito que la calidad depende de que su equipo conteste a tiempo y actualice el CRM
(`playbook-agencias-consultores.md` §6). El sistema mide las dos cosas: `/embudo` dice si el problema es de marketing o
de ventas.

## Vender con el sistema

| Para | Usa |
|---|---|
| Abrir conversación con un prospecto | `/auditoria-express "<prospecto>"`: auditoría con fuentes públicas (sus anuncios, su landing, su oferta y su competencia) y un PDF con tu marca, sin acceso a su cuenta |
| La propuesta | `/economia prevision`: escenarios de inversión → leads, citas, ventas y CAC esperables, con bandas y supuestos marcados |
| Un servicio de implementación | La señal de vuelta (Conversions API desde GHL, n8n, Make o el backend, y la de mensajería para Click to WhatsApp, Messenger e Instagram Direct) con `/implementar-capi` e `ingeniero-capi`. Para una agencia de automatización es un servicio que encaja de forma natural |
| Montar la captación del cliente | `/iman-de-leads` (diagnóstico o calculadora), `/construir-landing` (las páginas) y `/formulario-instantaneo` (el formulario de Meta con filtro), y después `/seguimiento-leads` para que su equipo conteste a tiempo |
| Prueba social que vende | `/casos-y-creadores`: tus proyectos entregados convertidos en casos con permiso, y anuncios de colaboración con clientes, expertos o creadores ([guía](guias/casos-y-creadores.md)) |
| Una cuenta heredada | `/auditoria <cliente>` (o `profundo`) en la primera semana, con plan 30/60/90 |
| Los primeros 30 días con un cliente nuevo | La secuencia semana a semana de `playbook-agencias-consultores.md` §9 |
| Poner precio a tu servicio | Los modelos de precio (fijo con puesta en marcha, % de la inversión, por lead o cita, fijo con bonus por cohortes maduras), cuándo encaja cada uno y su riesgo: `playbook-agencias-consultores.md` §10 |

## Trabajar en equipo

Cada persona del equipo tiene su propia instalación (su clon y su instancia). Para que el historial no se divida:

- **Cada cliente lo lleva una persona** en el sistema: su change log y su registro creativo son la fuente de verdad.
- Si necesitáis compartir carpetas de clientes, haced de `clientes/` un repositorio **privado** aparte (git ignora esa
  carpeta en el producto, así que no choca) y dejad fuera las carpetas `privado/`.
- Las reglas comunes de la agencia (tono de los informes, umbrales propios, qué no se toca sin el responsable) van en
  `contexto/operador.md` → «Reglas propias», igual en cada instalación.

## Cuando dejas de llevar a un cliente

1. Pon `estado: pausa` en su ficha: deja de salir en `/hoy` y en el brief.
2. Revoca el token de usuario del sistema que usabas para su cuenta y quita su servidor `ghl-<slug>`
   (`claude mcp remove ghl-<slug>`).
3. Pide al cliente que retire el acceso de partner de tu agencia (o retíralo tú desde tu portfolio).
4. Entrégale lo que sea suyo (informes, creativos, change log) y archiva su carpeta. Lo que hay en `privado/` se trata
   según vuestro contrato y el RGPD.
