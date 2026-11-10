---
slug: acme
nombre: Acme Automations
estado: activo
tipo: servicios-high-ticket
relacion: propio
moneda: EUR
zona_horaria: Europe/Madrid
meta:
  cuenta: act_000000000000001
  pagina: "000000000000002"
  instagram: "000000000000004"
  dataset: "000000000000003"
  catalogo: ""
  evento_principal: Lead
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 300
  total_dia: 400
crm:
  tipo: ghl
  servidor_mcp: ghl
stripe: false
mejoras_automaticas: off
explorar_explotar: 0.3
---

# Ficha: Acme Automations

> Última actualización: 2026-10-30 · La cabecera de arriba la leen las herramientas y los hooks: mantenla al día.

## Negocio
- Qué vende y a quién: proyectos de automatización con IA (atención al cliente, facturación, agenda, informes) para
  pymes de servicios de 10 a 100 empleados (asesorías, despachos, clínicas, inmobiliarias).
- Oferta principal y precio: diagnóstico gratuito de 30 minutos con cuestionario previo → propuesta → proyecto medio de
  9.000 € sin IVA en dos pagos; mantenimiento opcional de 350 €/mes.
- Mercados e idiomas: España, en español.
- Objetivo del trimestre: 6 proyectos firmados en el Q4 de 2026.
- Capacidad: 12 llamadas de diagnóstico por semana (dos consultores); como mucho 3 proyectos nuevos al mes.
- Categoría especial o sensible: no.
- Stack: web propia con landing y cuestionario de diagnóstico · GoHighLevel (pipeline «Ventas Meta») · Stripe para
  cobrar (no conectado al sistema) · calendario de GHL · n8n.

## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC (proyecto ganado) | 3.382 € | 1.691 € | economia.py leadgen, contribución del proyecto sin mantenimiento |
| ROAS en Ads Manager (base: con/sin IVA) | — | — | no se optimiza a valor |
| CPL | 93 € | 47 € | |
| Coste por diagnóstico completado | 133 € | 67 € | |
| Coste por lead cualificado | 266 € | 133 € | |
| Coste por llamada agendada | 444 € | 222 € | |
| Coste por llamada asistida | 592 € | 296 € | |
| Coste por propuesta enviada | 1.184 € | 592 € | |
| LTV (contribución) y payback máximo | 4.860 € sin mantenimiento | — | |

Tasas del funnel usadas (cohortes maduras de abril a agosto de 2026, 412 leads): lead→diagnóstico 70 %,
diagnóstico→cualificado 50 %, cualificado→llamada 60 %, llamada→asistió 75 %, asistió→propuesta 50 %,
propuesta→ganado 35 %. Lead→ganado ≈ 2,8 %. Ciclo lead→ganado: mediana 38 días, p80 60 días.

## Medición
- Evento de optimización principal: `Lead` (formulario de la landing) en `ES_LEADS_ADQ_HV`.
- Ventana de atribución con la que se decide (verificada en el ad set): 7 días clic + 1 día visualización (2026-10-01).
- Fuente de verdad del negocio: GHL (pipeline «Ventas Meta», etapas del contrato §16).
- Señal de vuelta a Meta: CAPI desde GHL con `LeadCualificado`, `Schedule`, `LlamadaAsistida`, `PropuestaEnviada` y
  `Purchase` con valor, activa desde 2026-09-15. `Lead` llega por píxel y por servidor con `event_id` compartido.
- Incrementalidad: sin test todavía.

## Política de mejoras automáticas de Meta (Advantage+ creative)
| Mejora | ON/OFF | Motivo / quién lo aprobó |
|---|---|---|
| Reescritura de texto en imágenes | OFF | riesgo de afirmaciones no aprobadas |
| Variaciones de texto | OFF | |
| Doblaje o traducción de voz | OFF | |
| Música, vídeo generado, expansión de imagen | OFF | |

## Reglas del Ads MCP server (Business Settings → Integrations)
- Acciones bloqueadas: borrar.
- Presupuesto máximo permitido al agente: 300 €/día por cambio.
- Límite de gasto de la cuenta: 12.000 €/mes.

## Reglas propias del cliente
- Nada de cifras de ahorro inventadas: solo los casos con permiso (asesoría fiscal de Valencia, 31 h/mes ahorradas).
- Los cambios en Meta los aprueba el socio director por escrito.

## Notas y aprendizajes clave
- Presupuesto actual: 250 €/día en una campaña (`ES_LEADS_ADQ_HV`, un conjunto `BROAD-A+_LEAD`).
- Los anuncios de caso real traen menos leads pero más llamadas que los de demo.
