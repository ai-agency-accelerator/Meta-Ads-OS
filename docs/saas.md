# SaaS

Cómo usar Meta Ads OS si vendes software por suscripción, con prueba gratuita, freemium o demo. La estrategia completa
está en `meta-ads-kb/14-playbooks/playbook-saas.md`; aquí tienes cómo la aplica el sistema.

## La idea central

Un registro no es un cliente. Si Meta optimiza para registros, te traerá gente que se registra y no usa el producto.
En SaaS:

- **optimiza para el evento que predice ingresos y tiene volumen**: la prueba **activada** (el primer momento de valor
  del producto, enviado por la Conversions API) o la suscripción; en ventas con demo, la demo celebrada;
- **decide con la capa más baja de verdad que tenga datos suficientes**: cliente de pago > prueba activada > prueba >
  registro;
- **mide con LTV:CAC y payback**, no con el coste por registro ni por prueba.

| Modelo | Evento para Meta | Lo que mides |
|---|---|---|
| Freemium o prueba sin tarjeta | Activación por CAPI cuando haya unas 50 por semana; mientras, `StartTrial` o `CompleteRegistration` | Coste por activado, prueba → pago, payback |
| Prueba con tarjeta | `StartTrial` con valor previsto o `Subscribe` | CAC y payback |
| Ventas con demo | Demo celebrada o lead cualificado (`Schedule`, Conversion Leads) | Coste por demo celebrada y por oportunidad |
| Producto + ventas | Evento de lead cualificado por uso (PQL) por CAPI | Coste por PQL y conversión |

## El recorrido de un SaaS

| Fase | Qué cambia en un SaaS | Skills |
|---|---|---|
| F0 | El tipo de la ficha es `saas`. La economía sale de precio, margen, churn y conversión de prueba a pago: CAC máximo por prueba y por suscriptor con su payback | `/economia suscripcion` · `/economia prevision` · `/disenar-funnel` (prueba gratuita o demo) |
| F1 | La señal sale de **tu backend** o de Stripe, no solo del píxel: activación y pago llegan a Meta por la Conversions API, deduplicados con el navegador | `/implementar-capi <cliente> backend` o `stripe` · `/conectar stripe` · `/audiencias` (excluir clientes de pago) · `/construir-landing` (landing de prueba o de demo, con el `event_id` compartido con tu backend) · `/formulario-instantaneo` (demo B2B con filtro) |
| F2 | Reseñas de G2, Capterra y foros como voz del cliente; comparativas con la competencia y con «lo de siempre» (la hoja de cálculo) | `/voz-cliente` · `/competencia` |
| F3 | Demos de pantalla resolviendo una tarea concreta, comparativas, prueba social del mismo tipo de empresa, oferta de entrada clara | `/producir-video <cliente> <brief> propio` (demo grabada) · `/producir-estatico` · `/casos-y-creadores` (clientes con permiso y anuncios de colaboración; [guía](guias/casos-y-creadores.md)) · `/analisis-creativo` (qué elementos de tus demos se asocian a pagar) |
| F4 | Un taller o una demo en grupo como entrada para B2B con ciclo largo | `/lanzar-campana` · `/webinar` |
| F5 | Cohortes por semana o por anuncio de registro → prueba → activación → pago, con LTV y payback; protección con el ordenador apagado; en ventas con demo, seguimiento y anuncios por etapa | `/embudo <cliente>` · `/informe-semanal` · `/reglas-automaticas` · `/seguimiento-leads` · `/anuncios-por-etapa` |

## Stripe: unir pagos con anuncios

Para saber qué anuncio trajo a cada cliente de pago, el alta tiene que guardar en los **metadatos del cliente de
Stripe** de dónde viene: `utm_source`, `utm_campaign`, `utm_content`, `ad_id`, y los identificadores de Meta `fbc` y
`fbp`. `/implementar-capi <cliente> stripe` te dice dónde capturarlos en tu web y cómo pasarlos a Stripe
([guía de Stripe](guias/stripe.md)).

A partir de ahí:

- `herramientas/stripe_datos.py por-anuncio` agrega pruebas, activaciones, clientes de pago y MRR por anuncio en
  `clientes/<slug>/datos/`, sin datos personales;
- `herramientas/registro_creativo.py` lo cruza con Meta en `registro-creativo.csv`;
- `/siguiente-anuncio` elige ganadores por cliente de pago cuando hay datos suficientes, y por prueba activada mientras
  tanto.

Stripe es **siempre de solo lectura**: usa una clave restringida de lectura (`rk_...`) y el sistema bloquea cualquier
creación, cambio, reembolso o cancelación.

## La señal desde tu backend

Si tu producto tiene backend propio, es la mejor fuente de señal: sabe quién se registró, quién activó y quién pagó.
`ingeniero-capi` diseña contigo los eventos (nombre, valor, `event_id` para deduplicar con el píxel, datos hasheados
como pide Meta) y `herramientas/capi.py` los prueba con `test_event_code` antes de que llegue uno real
([guía de Conversions API](guias/capi.md)).

Si no tienes backend propio, la misma señal sale de los webhooks de Stripe a través de n8n o Make.

## Números de referencia

Del playbook, con el ejemplo de un plan de 99 €/mes, 80 % de margen y 4 % de churn mensual: con un 15 % de prueba a
pago, el máximo que puedes pagar por prueba es 297 € (break-even sobre el LTV), unos 99 € si quieres LTV:CAC de 3:1 y
unos 143 € con payback a 12 meses `[STRONG INFERENCE]`. Los benchmarks de conversión de prueba a pago (12–19 % de
mediana) vienen de proveedores y son débiles `[EMPIRICAL]`: calcula los tuyos con `/economia suscripcion`.

Meta encaja sobre todo en SaaS para pymes, profesionales y herramientas horizontales; en enterprise funciona mejor como
retargeting.
