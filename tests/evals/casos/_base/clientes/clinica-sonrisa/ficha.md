---
slug: clinica-sonrisa
nombre: Clínica Sonrisa
estado: activo
tipo: negocio-local
relacion: cliente
moneda: EUR
zona_horaria: Europe/Madrid
meta:
  cuenta: act_000000000000021
  pagina: "000000000000022"
  instagram: "000000000000024"
  dataset: "000000000000023"
  catalogo: ""
  evento_principal: Lead
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 50
  total_dia: 60
crm:
  tipo: ghl
  servidor_mcp: ghl-clinica-sonrisa
stripe: false
mejoras_automaticas: off
explorar_explotar: 0.3
---

# Ficha: Clínica Sonrisa

> Última actualización: 2026-10-25 · La cabecera de arriba la leen las herramientas y los hooks: mantenla al día.

## Negocio
- Qué vende y a quién: clínica dental en Valencia; ortodoncia invisible para adultos de 25 a 55 años en 15 km.
- Oferta principal y precio: primera visita de valoración gratuita con escáner 3D; tratamiento medio de 3.200 €
  (exento de IVA), financiable.
- Mercados e idiomas: Valencia y área metropolitana, en español.
- Objetivo del trimestre: 10 tratamientos de ortodoncia aceptados al mes.
- Capacidad: 15 valoraciones por semana (una ortodoncista, martes y jueves).
- Categoría especial o sensible: salud (Health & Wellness). No se pregunta por salud en los formularios. Categoría del
  dataset sin revisar en Events Manager.
- Stack: formulario instantáneo (Higher intent) · sub-cuenta de GHL de la agencia (etapas lead, cita, asistió,
  aceptó) · la recepcionista llama a los leads y apunta las etapas.

## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC (tratamiento aceptado) | 1.300 € | 650 € | contribución por tratamiento |
| ROAS en Ads Manager (base: con/sin IVA) | — | — | |
| CPL | 101 € | 51 € | |
| Coste por cita / por show | 253 € / 390 € | 127 € / 195 € | |
| LTV (contribución) y payback máximo | 1.300 € (sin recurrencia) | — | |

Tasas del funnel usadas (cohortes de mayo a septiembre de 2026, 290 leads): lead→cita 40 %, cita→asistió 65 %,
asistió→acepta 30 %. Lead→tratamiento ≈ 7,8 %. Ciclo lead→aceptación: mediana 16 días.

## Medición
- Evento de optimización principal: `Lead` del formulario instantáneo en `ES_LEADS_ADQ_LOCAL`.
- Ventana de atribución con la que se decide (verificada en el ad set): 7 días clic + 1 día visualización.
- Fuente de verdad del negocio: GHL de la clínica (lo actualiza la recepción).
- Señal de vuelta a Meta: ninguna todavía (las etapas de GHL no vuelven a Meta).
- Incrementalidad: sin test.

## Política de mejoras automáticas de Meta (Advantage+ creative)
| Mejora | ON/OFF | Motivo / quién lo aprobó |
|---|---|---|
| Reescritura de texto en imágenes | OFF | salud: nada de afirmaciones no aprobadas |
| Variaciones de texto | OFF | |
| Doblaje o traducción de voz | OFF | |
| Música, vídeo generado, expansión de imagen | OFF | |

## Reglas del Ads MCP server (Business Settings → Integrations)
- Acciones bloqueadas: borrar.
- Presupuesto máximo permitido al agente: 50 €/día por cambio.
- Límite de gasto de la cuenta: 1.800 €/mes.

## Reglas propias del cliente
- Nada de antes y después ni de promesas de resultado; la gerente aprueba cada anuncio.
- Contrato de la agencia: fee mensual; la clínica se compromete a actualizar GHL en 48 h (cláusula de dependencia).

## Notas y aprendizajes clave
- Presupuesto actual: 40 €/día en una campaña (`ES_LEADS_ADQ_LOCAL`, un conjunto `LOCAL-15KM_LEAD`).
