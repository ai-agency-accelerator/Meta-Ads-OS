# 13 · Sistema operativo de Meta Ads

> Última verificación: 2026-10-16 · Autor: agente principal · Convierte las áreas 01–12 en metodología aplicable a
> cualquier cuenta. Cuando el usuario entregue una cuenta, se trabaja con estos documentos en este orden.

## Cómo usarlo

| Situación | Documento de entrada | Después |
|---|---|---|
| "Mira mi cuenta" / cuenta heredada | [02-framework-auditoria](02-framework-auditoria.md) | [08-cuenta-nueva-y-heredada](08-cuenta-nueva-y-heredada.md) §B → [07-diagnostico](07-framework-diagnostico.md) |
| Negocio sin campañas / nueva oferta o mercado | [03-framework-lanzamiento](03-framework-lanzamiento.md) | [08](08-cuenta-nueva-y-heredada.md) §A → playbook del modelo en [14](../14-playbooks/) |
| Gestión continua | [04-operativa-diaria-semanal-mensual](04-operativa-diaria-semanal-mensual.md) | [10-plantillas](10-plantillas.md) |
| Producción y test de creatividades | [05-framework-testing-creativo](05-framework-testing-creativo.md) | [03-creatividad](../03-creatividad/README.md) |
| "Quiero escalar" | [06-framework-escalado](06-framework-escalado.md) | [09-bidding](../09-bidding-escalado-economia-analitica/README.md) |
| "Algo va mal" | [07-framework-diagnostico](07-framework-diagnostico.md) | Árboles de tracking en [04/16](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md) |
| "Tengo X €/día, ¿qué hago?" | [09-presupuesto-pequeno-y-grande](09-presupuesto-pequeno-y-grande.md) | [02/06](../02-estructura-campanas/06-presupuesto-por-niveles.md) |
| "¿Cuánto puedo pagar por lead/venta?" | Calculadora `python3 -I herramientas/economia.py` (desde la raíz del proyecto; `/economia`) | [09/08](../09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md), [06/05](../06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md) |

## Índice

| # | Archivo | Qué contiene |
|---|---|---|
| 01 | [principios-de-razonamiento](01-principios-de-razonamiento.md) | Los 10 principios que gobiernan todas las decisiones |
| 02 | [framework-auditoria](02-framework-auditoria.md) | Auditoría completa con severidades P0–P3 y entregable |
| 03 | [framework-lanzamiento](03-framework-lanzamiento.md) | Fases con gates: objetivo → economía → tracking → oferta/funnel → research → producción → arquitectura → presupuesto → lanzamiento → medición |
| 04 | [operativa-diaria-semanal-mensual](04-operativa-diaria-semanal-mensual.md) | Qué mirar y qué no tocar cada día/semana/mes/trimestre |
| 05 | [framework-testing-creativo](05-framework-testing-creativo.md) | Taxonomía, estructuras por tamaño, kill rules, graduación, ciclo semanal |
| 06 | [framework-escalado](06-framework-escalado.md) | Condiciones, tipos, coste marginal, protocolo, señales de fallo |
| 07 | [framework-diagnostico](07-framework-diagnostico.md) | 15 árboles de decisión por síntoma |
| 08 | [cuenta-nueva-y-heredada](08-cuenta-nueva-y-heredada.md) | Arranque sin histórico y limpieza de deuda técnica 2025–2026 |
| 09 | [presupuesto-pequeno-y-grande](09-presupuesto-pequeno-y-grande.md) | ≤100 €/día vs ≥5.000 €/día |
| 10 | [plantillas](10-plantillas.md) | Ficha de cuenta, change log, brief, ficha de test, informe semanal, cohortes, nomenclatura |

## Reglas de seguridad del sistema

- **Nunca** se modifican campañas, presupuestos, anuncios ni activos de una cuenta real sin instrucción explícita del
  usuario para esa acción concreta. Auditar = solo lectura.
- Si se usa la Marketing API o el MCP oficial de Meta: tokens con el mínimo permiso, reglas MCP que bloqueen escrituras no
  autorizadas, y todo cambio como borrador con aprobación humana.
- Antes de aplicar cualquier táctica, comprobar vigencia en [00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md).
