---
fase: F1
actualizado: 2026-10-30
---
# Estado del cliente

Marca cada punto cuando esté verificado. La fase actual es la primera con puntos sin marcar. `/hoy` y `/empezar` leen
este archivo; `herramientas/estado.py` lo calcula.

## F0 · Negocio y oferta
- [x] F0.ficha — Ficha completa: oferta, precio, mercado, stack (verifica: archivo)
- [x] F0.economia — Break-even y target por etapa en la ficha (verifica: archivo)
- [x] F0.oferta — Oferta revisada con `/oferta` (verifica: archivo)
- [x] F0.funnel — Camino de conversión elegido con `/disenar-funnel` (verifica: archivo)
- [x] F0.topes — Topes de gasto por cambio y total en la ficha (verifica: archivo)

## F1 · Infraestructura y señal
- [x] F1.portfolio — Business Portfolio del cliente con 2FA y roles correctos (verifica: usuario)
- [x] F1.cuenta — Cuenta publicitaria activa con método de pago (verifica: mcp)
- [x] F1.activos — Página e Instagram vinculados a la cuenta (verifica: mcp)
- [x] F1.dominio — Dominio verificado (verifica: usuario)
- [x] F1.dataset — Dataset con el evento principal recibiendo datos por navegador y servidor (verifica: mcp)
- [x] F1.dedup — Deduplicación píxel/CAPI correcta y calidad de coincidencia revisada (verifica: mcp)
- [ ] F1.crm — Etapas del CRM, Stripe o backend llegando a Meta si aplica (verifica: mcp)
- [x] F1.reglas-mcp — Reglas del Ads MCP server y límite de gasto configurados (verifica: usuario)
- [x] F1.landing — Landing o formulario revisado con `/landing` (verifica: archivo)

## F2 · Investigación
- [x] F2.competencia — Competencia analizada con `/competencia` (verifica: archivo)
- [x] F2.voz — Voz del cliente con `/voz-cliente` (verifica: archivo)
- [x] F2.angulos — Matriz de ángulos en `investigacion/` (verifica: archivo)

## F3 · Creatividad
- [x] F3.briefs — Al menos 2 conceptos distintos con brief hasta 100 €/día y 3 por encima, 13/09 §A.2 (verifica: archivo)
- [x] F3.piezas — Piezas producidas, criticadas y con veredicto de políticas en su LEEME (verifica: archivo)

## F4 · Lanzamiento
- [x] F4.plan — Plan de campaña aprobado en `planes/` (verifica: archivo)
- [x] F4.creada — Campaña creada en pausa con previsualizaciones revisadas (verifica: mcp)
- [x] F4.activa — Campaña activada con confirmación y anotada en el change log (verifica: mcp)

## F5 · Operación
- [x] F5.cadencia — Brief diario e informe semanal en marcha (verifica: archivo)
- [x] F5.registro — Registro creativo actualizado en los últimos 7 días (verifica: archivo)
- [x] F5.evaluaciones — Sin evaluaciones vencidas en el change log (verifica: archivo)

## F6 · Escalado
- [ ] F6.condiciones — Condiciones de `/escalar` cumplidas (verifica: archivo)
