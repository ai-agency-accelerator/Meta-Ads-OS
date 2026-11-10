---
slug: <slug>
nombre: <nombre>
estado: prospecto
tipo: servicios-high-ticket
relacion: propio
moneda: EUR
zona_horaria: Europe/Madrid
mercados: ""  # opcional: países donde se anuncia (ISO: ES, FR…); economia.py aplica su tasa por ubicación
meta:
  cuenta: ""
  pagina: ""
  instagram: ""  # ID numérico de la cuenta profesional, no el @usuario
  dataset: ""
  dataset_mensajeria: ""  # opcional: dataset de la WABA, la Página o Instagram si no es el de arriba
  waba: ""  # opcional: ID de la cuenta de WhatsApp Business (mensajería)
  catalogo: ""
  evento_principal: ""
  ventana_atribucion: 7d_click_1d_view
topes:
  cambio_dia: 0
  total_dia: 0
crm:
  tipo: ninguno
  servidor_mcp: ghl
stripe: false
mejoras_automaticas: off
explorar_explotar: 0.3
capacidad:  # opcional (servicios y consultoría): techo comercial por semana, antes que el de Meta
  llamadas_semana: 0
  propuestas_semana: 0
coste_vender_por_venta: 0  # opcional: horas de venta × coste/hora; va a economia.py --coste-fijo
etapa_objetivo_cl: ""  # opcional: etapa (contrato §16) candidata a Conversion Leads
definicion_cualificado: ""  # opcional: qué es «cualificado»; no se cambia con campañas activas
umbral_no_compensa: 0  # opcional: ahorro neto anual mínimo para que el diagnóstico diga «compensa»
---

# Ficha: <nombre>

> Última actualización: AAAA-MM-DD · La cabecera de arriba la leen las herramientas y los hooks: mantenla al día.
> Los topes a 0 significan «sin definir»: el sistema no deja crear ni subir presupuestos hasta que los fijes.

## Negocio
- Playbook: `meta-ads-kb/14-playbooks/<archivo>`
- Qué vende y a quién (servicio, SaaS, producto):
- Oferta principal y precio (con o sin IVA):
- Mercados e idiomas:
- Objetivo del trimestre (resultado de negocio, no métrica de Meta):
- Capacidad (agenda comercial, plazas, onboarding de clientes):
- Ciclo de venta (días de la primera llamada a la firma; cuántos deciden):
- Categoría especial o sensible (finanzas, salud, empleo, vivienda): sí/no — cuál
- Stack: web · CRM · pagos · calendario · automatizaciones (n8n, Make…)

## Economía (con `herramientas/economia.py`)
| Métrica | Break-even | Target | Fuente o supuesto |
|---|---|---|---|
| Coste por venta / CAC | | | |
| ROAS en Ads Manager (base: con/sin IVA) | | | |
| CPL | | | |
| Coste por lead cualificado | | | |
| Coste por cita / por show | | | |
| Coste por prueba / por activación (SaaS) | | | |
| LTV (contribución) y payback máximo | | | |

Tasas del funnel usadas (marca [HYPOTHESIS] las que no salgan de datos):

## Medición
- Evento de optimización principal:
- Ventana de atribución con la que se decide (verificada en el ad set):
- Fuente de verdad del negocio (CRM, Stripe, backend):
- Señal de vuelta a Meta (CAPI desde CRM, Stripe o backend) y estado:
- Incrementalidad: último test y resultado:

## Política de mejoras automáticas de Meta (Advantage+ creative)
| Mejora | ON/OFF | Motivo / quién lo aprobó |
|---|---|---|
| Reescritura de texto en imágenes | OFF | riesgo de afirmaciones no aprobadas |
| Variaciones de texto | OFF | |
| Doblaje o traducción de voz | OFF | |
| Música, vídeo generado, expansión de imagen | OFF | |

## Reglas del Ads MCP server (Business Settings → Integrations)
- Acciones bloqueadas:
- Presupuesto máximo permitido al agente:
- Límite de gasto de la cuenta:

## Reglas propias del cliente
- (lo que no se negocia: tono, cara y voz reales, afirmaciones prohibidas, horarios…)

## Afirmaciones aprobadas
Solo lo que está aquí puede salir en un anuncio como cifra, resultado o testimonio (`/brief-creativo`,
`redactor-anuncios` y `revisor-politicas` leen de esta tabla; los casos, de `investigacion/casos/<caso>/caso.md`).

| Afirmación (texto exacto) | Fuente | Medida o estimada | Aprobada (fecha · por quién) | Caduca | Uso |
|---|---|---|---|---|---|

## Audiencias
Inventario de `/audiencias` (IDs de Meta; nunca datos personales).

| Audiencia | ID | Uso (incluir o excluir, en qué conjuntos) | Origen y actualización |
|---|---|---|---|

## Notas y aprendizajes clave
-
