# Recorrido por fases

Meta Ads OS no es un catálogo de comandos: es un camino. Cada cliente (o tu propio negocio) avanza por siete fases,
de **F0 Negocio y oferta** a **F6 Escalado**, y el sistema sabe en cuál está y qué le falta.

El orden importa: economía y señal antes que creatividad, y creatividad antes que presupuesto. Saltarse una fase es la
forma más cara de aprender (`meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md`).

## Cómo sabe el sistema en qué fase estás

Cada cliente tiene `clientes/<slug>/estado.md`: una cabecera con la fase y una checklist donde cada punto dice cómo se
verifica.

```markdown
---
fase: F1
actualizado: 2026-11-09
---
- [x] F0.economia — Break-even y target por etapa en la ficha (verifica: archivo)
- [ ] F1.dataset — Dataset con el evento principal recibiendo datos por navegador y servidor (verifica: mcp)
```

- **La fase actual es la primera con puntos sin marcar.** Un punto se marca cuando está verificado, no cuando «más o
  menos» está.
- `(verifica: …)` dice cómo: `mcp` (se comprueba en Meta), `ghl` o `stripe` (en el sistema de negocio), `archivo`
  (existe el entregable) o `usuario` (lo confirmas tú; por ejemplo, el dominio verificado).
- `herramientas/estado.py` lo calcula sin coste y sin llamar a nadie: fase, pendientes, evaluaciones vencidas del
  change log, si toca el informe semanal, si existe el brief de hoy y la cola de producción. Lo usan `/hoy`, el brief
  diario y el aviso de inicio de sesión.

## Las cuatro entradas

No hace falta saber qué skill toca. Con estas cuatro llegas a todo:

| Entrada | Cuándo |
|---|---|
| `/empezar` | La primera vez, o para retomar la configuración inicial |
| `/hoy` | Cada día: recorre tus clientes activos y acaba con 1–3 acciones ordenadas |
| `/pregunta` | Cualquier duda de Meta, respondida desde la base con fuente y etiqueta de evidencia |
| `/siguiente-anuncio` | Cuando toca decidir qué anuncio producir después |

Al abrir una sesión, el hook `contexto_sesion` te enseña en seis líneas como mucho el estado de la instalación, las
conexiones, las evaluaciones vencidas y si ya tienes el brief de hoy.

---

## F0 · Negocio y oferta

**Objetivo.** Saber cuánto puedes pagar por un cliente y qué camino de conversión vas a usar, antes de gastar un euro.

| Punto | Se da por cumplido cuando |
|---|---|
| `F0.ficha` | La ficha tiene oferta, precio, mercado y stack |
| `F0.economia` | Break-even y target por etapa (lead, cualificado, cita, show, venta; o registro, prueba, pago) en la ficha |
| `F0.oferta` | La oferta está revisada con `/oferta` |
| `F0.funnel` | El camino de conversión está elegido con `/disenar-funnel` |
| `F0.topes` | La ficha tiene el tope por cambio y el tope total diario |

**Skills.** `/cliente-nuevo` · `/economia` (con el modo `prevision` para planes y propuestas: inversión → leads,
citas, ventas y CAC esperables con bandas) · `/oferta` · `/disenar-funnel` · `/iman-de-leads` (un diagnóstico o una
calculadora que da valor y precualifica, con un veredicto honesto: no compensa, empieza por un proceso o hay
proyecto).

Si vendes proyectos con llamada y propuesta, el playbook del nicho
(`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`) dice qué evento optimizar según tu volumen y
cuántas llamadas puedes atender antes de que Meta sea el límite.

**Agentes.** `analista-cuantitativo` (los números), `estratega-creativo` (la oferta), `especialista-funnel` (el camino).

**Error típico.** Perseguir un CPL más bajo sin saber cuánto vale un lead. El CPL máximo sale de la contribución por
venta y de cada tasa del camino, y el show y el cierre suelen pesar más que el CPL
(`meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md`).

## F1 · Infraestructura y señal

**Objetivo.** Que Meta reciba el evento que de verdad te importa, por navegador y por servidor, sin duplicados, y que
haya topes de gasto en los dos lados.

| Punto | Se da por cumplido cuando |
|---|---|
| `F1.portfolio` | Business Portfolio con verificación en dos pasos y roles correctos |
| `F1.cuenta` | Cuenta publicitaria activa con método de pago |
| `F1.activos` | Página e Instagram vinculados a la cuenta |
| `F1.dominio` | Dominio verificado |
| `F1.dataset` | El dataset recibe el evento principal por navegador y servidor |
| `F1.dedup` | Deduplicación correcta y calidad de coincidencia revisada |
| `F1.crm` | Las etapas del CRM, Stripe o el backend llegan a Meta, si aplica |
| `F1.reglas-mcp` | Reglas del Ads MCP server y límite de gasto de la cuenta configurados en Meta |
| `F1.landing` | Landing revisada con `/landing` o formulario instantáneo probado con un lead de prueba en el CRM |

**Skills.** `/configurar-meta` (según tu situación: de cero, sin señal, cuenta heredada o agencia entrando como
partner) · `/implementar-capi` (web y mensajería: Click to WhatsApp, Messenger e Instagram Direct) · `/audiencias` ·
`/construir-landing` (landing, diagnóstico, reserva, gracias o registro a un taller como HTML estático, con
consentimiento antes del píxel y el mismo `event_id` para la CAPI) · `/formulario-instantaneo` (formulario de Meta con
preguntas de filtro, creado por API con tu confirmación o guiado en Ads Manager) · `/landing` (audita una página ya
publicada) · `/conectar`.

El sistema construye las páginas pero no las despliega: tú subes la carpeta a tu hosting o la pegas en GHL
([Páginas de captación](guias/construir-landing.md)).

**Agentes.** `especialista-tracking` (diagnostica la señal), `ingeniero-capi` (la construye y la prueba),
`especialista-crm` (decide qué etapas y valores devolver), `especialista-funnel`.

**Error típico.** Mandar eventos reales «para probar». Ensucian el dataset del cliente y lo que Meta optimiza: las
pruebas van siempre con `test_event_code` y el hook `eventos_guard` te lo recuerda
(`meta-ads-kb/04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md`).

## F2 · Investigación

**Objetivo.** Saber qué dice el mercado antes de escribir un solo anuncio: qué anuncia la competencia, con qué
palabras habla tu cliente y qué ángulos quedan libres.

| Punto | Se da por cumplido cuando |
|---|---|
| `F2.competencia` | Competencia analizada con `/competencia` |
| `F2.voz` | Voz del cliente extraída con `/voz-cliente` |
| `F2.angulos` | Matriz de ángulos guardada en `investigacion/` |

**Skills.** `/competencia` (con `vigilar` para una foto semanal de anuncios nuevos, retirados y los más longevos) ·
`/voz-cliente`. Modo profundo: workflow `investigacion-mercado`.

**Agentes.** `investigador-competencia`.

**Error típico.** Copiar el anuncio que más tiempo lleva activo de un competidor. La longevidad es una pista, no una
prueba de rentabilidad (`meta-ads-kb/03-creatividad/10-investigacion-competencia-ad-library.md`).

## F3 · Creatividad

**Objetivo.** Conceptos de verdad distintos, producidos, criticados y con veredicto de políticas: de 2 a 4 hasta
100 €/día, de 3 a 6 hasta 500 €/día y de 8 a 15 por encima (`meta-ads-kb/13-sistema-operativo/09-presupuesto-pequeno-y-grande.md` §A.2).

| Punto | Se da por cumplido cuando |
|---|---|
| `F3.briefs` | Al menos 2 conceptos distintos con brief hasta 100 €/día y 3 por encima |
| `F3.piezas` | Piezas producidas, criticadas y con veredicto de políticas en su `LEEME.md` |

**Skills.** `/brief-creativo` (cuenta u oferta nueva) o `/siguiente-anuncio` (ya hay datos) · `/casos-y-creadores`
(casos con permiso del cliente, socios y anuncios de colaboración) · `/organico-a-anuncios` (publicaciones propias que
ya funcionaron) · `/producir-video` (`ia`, `propio` o `hibrido`) · `/producir-estatico` · `/variantes` ·
`/revisar-anuncio` · `/analisis-creativo` (qué elementos de tus anuncios se asocian a ganar y cuántos conceptos nuevos
producir al mes). Modos profundos: `estudio-creativo` y `lote-creativo`.

En venta consultiva, la prueba real (un cliente con nombre de sector y cifras aprobadas) suele pesar más que cualquier
pieza generada. Las cifras y citas solo salen de la sección «Afirmaciones aprobadas» de la ficha.

**Agentes.** `estratega-creativo`, `redactor-anuncios`, `productor-ugc`, `editor-video`, `disenador-estaticos`,
`critico-creativo` y `revisor-politicas`.

Cada pieza se entrega en `clientes/<slug>/creativos/<nombre-base>/` con un `LEEME.md` que recoge QA, crítica, coste,
afirmaciones, etiqueta de IA y veredicto de políticas (y, si la hay, la prueba social y sus derechos). El nombre sigue la nomenclatura (`herramientas/nomenclatura.py`):
sin él, el registro creativo no sabe qué ángulo o qué hook ganó.

**Error típico.** Llamar «conceptos» a tres variantes con otro color o tres palabras distintas en el hook. Eso son
iteraciones: un concepto nuevo cambia el ángulo, la persona, el argumento central o el formato hasta que la miniatura y
los primeros 3 segundos no se reconocen (`meta-ads-kb/03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md`).

## F4 · Lanzamiento

**Objetivo.** Un plan aprobado, creado en pausa, revisado en las previsualizaciones y activado con tu confirmación.

| Punto | Se da por cumplido cuando |
|---|---|
| `F4.plan` | Plan de campaña aprobado en `planes/` |
| `F4.creada` | Campaña creada en pausa con previsualizaciones revisadas |
| `F4.activa` | Campaña activada con confirmación y anotada en el change log |

**Skills.** `/lanzar-campana` (con gates de economía, señal, oferta, funnel y creatividad) · `/publicar-anuncios`
(sube un lote a una campaña existente) · `/test-creativo` · `/webinar` (un taller de captación de punta a punta:
páginas, campañas por fase, recordatorios, oferta y medición hasta el proyecto firmado). Modo profundo:
`lanzamiento-completo`.

**Agentes.** `revisor-estrategia` revisa el plan antes de enseñártelo; `operador-meta` lo ejecuta, y es el único
agente que puede escribir en Meta.

**Error típico.** Una campaña por anuncio «para controlarlo mejor». Consolidar es la regla; separar necesita una razón
de negocio (`meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`, principio 5).

## F5 · Operación

**Objetivo.** Una cadencia que se cumple sola y decisiones con paciencia y con la capa más baja de verdad disponible.

| Punto | Se da por cumplido cuando |
|---|---|
| `F5.cadencia` | Brief diario e informe semanal en marcha |
| `F5.registro` | Registro creativo actualizado en los últimos 7 días |
| `F5.evaluaciones` | Sin evaluaciones vencidas en el change log |
| `F5.reglas` | Reglas automáticas del OS creadas y revisadas tras el modo sombra |

**Skills.** `/brief-diario` · `/informe-semanal` · `/revision-mensual` · `/diagnostico` · `/ejecutar-cambio` ·
`/embudo` · `/rescate-cuenta` (rechazos en cadena, cuenta restringida, hackeo o fallo de pago) ·
`/reglas-automaticas` (protección 24/7 dentro de Meta: pausa sin conversión a 4× el CPA, o 3× con volumen, gasto fuera de tope y
alertas, primero en modo sombra) · `/seguimiento-leads` (respuesta en minutos, recordatorios, no-shows y propuestas
abiertas en GHL; el sistema nunca envía mensajes) · `/anuncios-por-etapa` (anuncios pequeños para quien no vino, tiene
una propuesta abierta o dijo «ahora no», con grupo de control).

**Agentes.** `analista-meta`, `especialista-crm`, `revisor-estrategia` y `operador-meta`.

**La cadencia** (`meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md`):

| Cada | Qué | Para qué |
|---|---|---|
| Día | Brief diario (programado) y `/hoy` | Detectar roturas: gasto fuera de ritmo, rechazos, señal caída. **No** para optimizar |
| Semana | `/informe-semanal` sobre la última semana natural completa | Evaluar los cambios que vencen y decidir como mucho 3 cosas |
| Mes | `/revision-mensual` | Economía vigente, coste marginal, incrementalidad, aprendizajes por ángulo y plan del mes |

**Error típico.** Tocar una campaña cada dos días. Un cambio no se evalúa con menos de 7 días, menos de 30–50 eventos
o con la ventana de atribución sin madurar, salvo que algo esté roto. El hook `meta_guard` te avisa si vuelves a
cambiar algo que se cambió hace menos de 7 días
(`meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md`).

## F6 · Escalado

**Objetivo.** Crecer mientras el coste del siguiente cliente siga por debajo del break-even.

| Punto | Se da por cumplido cuando |
|---|---|
| `F6.condiciones` | Se cumplen las condiciones de `/escalar` |

**Skills.** `/escalar` (condiciones previas, CPA incremental por escalón, coste marginal, palanca correcta y plan por
escalones dentro de los topes) · `/auditoria` (revisión completa P0–P3 cuando algo no cuadra o cada trimestre).

**Agentes.** `analista-cuantitativo` y `auditor-cuenta`.

**Error típico.** Escalar mirando el CPA medio. El que importa es el del último euro
(`meta-ads-kb/13-sistema-operativo/06-framework-escalado.md`).

---

## El circuito del siguiente anuncio

Con la cuenta en marcha, la creatividad deja de ser intuición y se convierte en un circuito cerrado:

1. **Meta + GoHighLevel o Stripe → registro creativo.** `herramientas/registro_creativo.py` cruza cada anuncio con sus
   resultados de negocio en `clientes/<slug>/registro-creativo.csv`. La clasificación (ángulo, concepto, formato, hook)
   sale del nombre del anuncio. `/analisis-creativo` va un paso más allá: qué elementos (quién habla, primer
   fotograma, demo, prueba, CTA…) tienen los anuncios que ganan.
2. **Decisión.** `/siguiente-anuncio` elige ganadores con la capa más baja de verdad que tenga datos suficientes:
   - servicios: venta > cita o show > cualificado > CPL;
   - SaaS: cliente de pago > prueba activada > prueba > registro.

   Las métricas antes del clic (CTR, hook rate) solo sirven para descartar perdedores.
3. **Producción.** `/producir-video` o `/producir-estatico`, con crítica y políticas.
4. **Publicación.** `/publicar-anuncios`, en pausa y con las mejoras automáticas desactivadas.
5. **Lectura.** El brief y el informe semanal alimentan otra vez el registro.

## Agencia y aprendizaje

Fuera de las fases, para el día a día de una agencia o consultora:

- `/informe-cliente`: el informe interno convertido en uno para el cliente, con tu marca.
- `/auditoria-express`: auditoría de un prospecto sin acceso a su cuenta, para venderle.
- `/entrenar`: escenarios prácticos con corrección para ti o tu equipo.
- `/novedades-meta`: qué ha cambiado en Meta y a qué clientes afecta.

Más en [Agencias con varios clientes](agencias.md).
