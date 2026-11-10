---
slug: nimbo
nombre: Nimbo
estado: activo
tipo: saas
relacion: cliente
moneda: EUR
zona_horaria: Europe/Madrid
meta:
  cuenta: act_000000000000011
  pagina: "000000000000012"
  instagram: "000000000000014"
  dataset: "000000000000013"
  catalogo: ""
  evento_principal: StartTrial
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 250
  total_dia: 350
crm:
  tipo: ninguno
  servidor_mcp: ghl
stripe: true
mejoras_automaticas: off
explorar_explotar: 0.3
---

# Ficha: Nimbo

> Última actualización: 2026-10-28 · La cabecera de arriba la leen las herramientas y los hooks: mantenla al día.

## Negocio
- Qué vende y a quién: SaaS que automatiza facturas y documentos (lectura con IA, conciliación, envío al programa de
  contabilidad) para gestorías y pymes.
- Oferta principal y precio: 89 €/mes sin IVA (plan único) o 890 €/año; prueba gratis de 14 días sin tarjeta.
- Mercados e idiomas: España, en español.
- Objetivo del trimestre: +60 clientes de pago netos en el Q4 de 2026.
- Capacidad: alta en autoservicio; soporte de 2 personas.
- Categoría especial o sensible: no.
- Stack: web en Webflow · app propia · Stripe (suscripciones) · sin CRM · n8n.

## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC (cliente de pago) | 1.891 € | 630 € | LTV de contribución; target con LTV:CAC 3:1 (payback 8,3 meses) |
| ROAS en Ads Manager (base: con/sin IVA) | — | — | no se optimiza a valor |
| Coste por prueba (StartTrial) | 340 € | 113 € | |
| Coste por prueba activada | 851 € | 284 € | |
| LTV (contribución) y payback máximo | 1.891 € (89 € × 85 % / 4 % de churn mensual) | 12 meses | |

Tasas del funnel usadas (cohortes de junio a septiembre de 2026, 512 pruebas): prueba→activada 40 %,
activada→pago 45 %, prueba→pago 18 %. Activación = 10 o más documentos procesados en los 7 primeros días.

## Medición
- Evento de optimización principal: `StartTrial` (alta de la prueba) en `ES_TRIAL_ADQ_LC`.
- Ventana de atribución con la que se decide (verificada en el ad set): 7 días clic + 1 día visualización.
- Fuente de verdad del negocio: base de datos de la app (pruebas y activaciones) y Stripe (pagos).
- Señal de vuelta a Meta: `StartTrial` por píxel y por CAPI desde el backend con `event_id`; `Subscribe` con valor desde
  el webhook de Stripe por CAPI. La activación se registra en la app pero todavía no se envía a Meta.
- Incrementalidad: sin test.

## Política de mejoras automáticas de Meta (Advantage+ creative)
| Mejora | ON/OFF | Motivo / quién lo aprobó |
|---|---|---|
| Reescritura de texto en imágenes | OFF | |
| Variaciones de texto | OFF | |
| Doblaje o traducción de voz | OFF | |
| Música, vídeo generado, expansión de imagen | OFF | |

## Reglas del Ads MCP server (Business Settings → Integrations)
- Acciones bloqueadas: borrar.
- Presupuesto máximo permitido al agente: 250 €/día por cambio.
- Límite de gasto de la cuenta: 9.000 €/mes.

## Reglas propias del cliente
- El fundador aprueba cualquier cambio de presupuesto.

## Notas y aprendizajes clave
- Presupuesto actual: 200 €/día (`ES_TRIAL_ADQ_LC`, un conjunto `BROAD-A+_TRIAL`), coste por prueba medio de 45 € en
  septiembre y octubre (unas 31 pruebas, 12 activadas y 5–6 clientes de pago por semana).
