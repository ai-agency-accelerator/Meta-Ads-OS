---
fase: F0
actualizado: AAAA-MM-DD
---
# Estado del cliente

Marca cada punto cuando esté verificado. La fase actual es la primera con puntos sin marcar; los que acaban en
«Opcional.» no la retienen. `/hoy` y `/empezar` leen este archivo; `herramientas/estado.py` lo calcula.

## F0 · Negocio y oferta
- [ ] F0.ficha — Ficha completa: oferta, precio, mercado, stack (verifica: archivo)
- [ ] F0.economia — Break-even y target por etapa en la ficha (verifica: archivo)
- [ ] F0.oferta — Oferta revisada con `/oferta` (verifica: archivo)
- [ ] F0.funnel — Camino de conversión elegido con `/disenar-funnel` (verifica: archivo)
- [ ] F0.topes — Topes de gasto por cambio y total en la ficha (verifica: archivo)
- [ ] F0.iman — Imán de entrada diseñado y probado con `/iman-de-leads` (verifica: archivo). Opcional.

## F1 · Infraestructura y señal
- [ ] F1.portfolio — Business Portfolio del cliente con 2FA y roles correctos (verifica: usuario)
- [ ] F1.cuenta — Cuenta publicitaria activa con método de pago (verifica: mcp)
- [ ] F1.activos — Página e Instagram vinculados a la cuenta (verifica: mcp)
- [ ] F1.dominio — Dominio verificado (verifica: usuario)
- [ ] F1.dataset — Dataset con el evento principal recibiendo datos por navegador y servidor (verifica: mcp)
- [ ] F1.dedup — Deduplicación píxel/CAPI correcta y calidad de coincidencia revisada (verifica: mcp)
- [ ] F1.crm — Etapas del CRM, Stripe o backend llegando a Meta si aplica (verifica: mcp)
- [ ] F1.reglas-mcp — Reglas del Ads MCP server y límite de gasto configurados (verifica: usuario)
- [ ] F1.landing — Landing revisada con `/landing` o formulario instantáneo probado con un lead de prueba en el CRM (verifica: archivo)

## F2 · Investigación
- [ ] F2.competencia — Competencia analizada con `/competencia` (verifica: archivo)
- [ ] F2.voz — Voz del cliente con `/voz-cliente` (verifica: archivo)
- [ ] F2.angulos — Matriz de ángulos en `investigacion/` (verifica: archivo)

## F3 · Creatividad
- [ ] F3.briefs — Al menos 2 conceptos distintos con brief hasta 100 €/día y 3 por encima, 13/09 §A.2 (verifica: archivo)
- [ ] F3.piezas — Piezas producidas, criticadas y con veredicto de políticas en su LEEME (verifica: archivo)
- [ ] F3.prueba — Al menos 1 caso con permiso y afirmaciones aprobadas, o un socio con derechos firmados (verifica: archivo). Opcional.

## F4 · Lanzamiento
- [ ] F4.plan — Plan de campaña aprobado en `planes/` (verifica: archivo)
- [ ] F4.creada — Campaña creada en pausa con previsualizaciones revisadas (verifica: mcp)
- [ ] F4.activa — Campaña activada con confirmación y anotada en el change log (verifica: mcp)

## F5 · Operación
- [ ] F5.cadencia — Brief diario e informe semanal en marcha (verifica: archivo)
- [ ] F5.registro — Registro creativo actualizado en los últimos 7 días (verifica: archivo)
- [ ] F5.evaluaciones — Sin evaluaciones vencidas en el change log (verifica: archivo)
- [ ] F5.reglas — Reglas automáticas del OS creadas y revisadas tras el modo sombra (verifica: archivo)

## F6 · Escalado
- [ ] F6.condiciones — Condiciones de `/escalar` cumplidas (verifica: archivo)
