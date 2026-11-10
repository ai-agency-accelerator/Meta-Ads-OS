---
name: revision-mensual
description: "Revisión mensual de un cliente (y trimestral cuando toca): economía vigente, coste marginal y presupuesto total, incrementalidad, aprendizajes creativos por ángulo, oferta y funnel, estructura, señal, cambios de Meta y riesgo de cuenta. Termina en un plan del mes con 3–5 prioridades, presupuesto, calendario creativo y tests."
argument-hint: "<cliente> [AAAA-MM]"
---

# /revision-mensual

Entrada: `$ARGUMENTS`. Sin mes, el último mes natural cerrado. Se apoya en los informes semanales de ese mes: si falta
alguno, hazlo antes con `/informe-semanal` o di qué semanas no están cubiertas.

- **Marco:** `meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md` §3 (bloques y salida) y §4
  (trimestral), `meta-ads-kb/13-sistema-operativo/06-framework-escalado.md` §3 (coste marginal),
  `meta-ads-kb/09-bidding-escalado-economia-analitica/06-estacionalidad.md`,
  `meta-ads-kb/04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md`,
  `meta-ads-kb/13-sistema-operativo/02-framework-auditoria.md` (revisión trimestral de arquitectura).
- **Agentes** (los cuatro primeros en paralelo, un mensaje con varias llamadas): `analista-meta`, `analista-cuantitativo`,
  `especialista-tracking`, `especialista-crm` (si hay CRM); después `estratega-creativo` (calendario) y
  `revisor-estrategia` (plan).
- **Herramientas:** `estado.py`, `meta_ads.py anuncios --mes`, `embudo.py`, `registro_creativo.py`, `economia.py`,
  `estadistica.py`.
- **Lee:** ficha, `informes/semanal/` y `informes/diario/` del mes, `change-log.md`, `registro-creativo.csv`,
  `aprendizajes-creativos.md`, `cohortes-leads.md`, `planes/tests/`, `aprendizajes/novedades/`, la revisión mensual anterior.
- **Escribe:** `clientes/<slug>/informes/mensual/AAAA-MM.md` y, si cambian, la economía de la ficha (con tu sí) y
  `aprendizajes-creativos.md`.

## Pasos

1. **Material del mes:** `python3 -I herramientas/estado.py resumen --cliente <slug> --json`; informes semanales y
   briefs diarios del mes (roturas, decisiones y su resultado); exportación de Meta del mes
   `python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --mes <AAAA-MM>` (o el MCP sin token).
2. **Economía** (`analista-cuantitativo`): ¿siguen valiendo break-even y target? Precio, margen, tasa de cierre,
   devoluciones o bajas, comisión de Meta por país. Cohortes maduras:
   `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por semana --modelo <servicios|saas> --guardar`
   (en SaaS, LTV y payback con el churn medido o `--churn`). Si cambia algo → `/economia` y propuesta de cambio en la
   ficha.
3. **Presupuesto total:** CPA o coste por venta incremental entre semanas con gasto distinto (Δgasto ÷ Δconversiones,
   misma estacionalidad) o ajuste log-log con 4–8 semanas (06 §3). Subir, mantener o bajar el gasto total según el
   coste marginal frente al break-even. Calendario del mes que viene (09/06): picos, festivos, cierres de trimestre.
4. **Incrementalidad:** qué parte de lo atribuido es incremental (último test en la ficha, «Medición →
   Incrementalidad»). Si hay volumen y no hay test reciente, propón uno con `/test-creativo diseñar lift|geo`.
5. **Creatividad** (`registro_creativo.py actualizar` con el mes completo y `aprendizajes-creativos.md`): hit rate
   (ganadores ÷ conceptos testeados), qué ángulos, personas y formatos ganan, volumen producido frente a capacidad de
   test, conceptos en fatiga. Ejecuta `/analisis-creativo <slug>` (o lee su informe en `informes/analisis-creativo/`
   si tiene menos de 2 semanas) e incluye qué repetir, qué probar, qué dejar y el plan de suministro del mes.
   `estratega-creativo` propone el calendario creativo del mes (lotes y fechas).
6. **Oferta y funnel:** ¿el cuello de botella es la oferta, la landing o ventas? Con la cohorte, separa marketing de
   ventas (`/embudo`). Elige el test de oferta o landing del mes, si toca.
7. **Estructura** (`analista-meta` con `ads_get_ad_entities`): fragmentación, conjuntos en learning limited permanente,
   duplicados, campañas zombi, mejoras automáticas que no cuadran con la ficha (`meta_ads.py creatividades` con token).
8. **Señal** (`especialista-tracking`: `ads_get_dataset_quality`, `ads_get_dataset_stats`): calidad de coincidencia,
   cobertura del servidor, deduplicación, etapas del CRM devueltas, valores correctos.
9. **Plataforma:** cambios de Meta del mes que afectan a este cliente (`aprendizajes/novedades/` y filas `Meta
   (plataforma)` del change log; si no hay nada reciente, `/novedades-meta`). Revisa también qué hicieron las reglas
   automáticas en el mes (`reglas_meta.py historial --cliente <slug> --dias 31 --todas`, con token) y si alguna pausa
   fue un falso positivo (`/reglas-automaticas <slug> revisar`).
10. **Riesgo:** rechazos y errores (`ads_get_errors`), Account Quality, admins y accesos (bajas de personas que ya no
    deben entrar), método de pago de respaldo y límite de gasto. Lo que no se ve con el MCP se pregunta al usuario.
11. **Trimestral** (si el mes cierra trimestre): arquitectura completa contra el framework de auditoría (o `/auditoria`),
    test de incrementalidad o, como mínimo, análisis antes y después, y re-baseline de KPIs si Meta cambió definiciones.
12. **Plan del mes:** 3–5 prioridades (cada una con hipótesis, responsable, métrica y fecha), presupuesto propuesto
    dentro de los topes de la ficha, calendario creativo y tests con su potencia (`estadistica.py potencia`).
    `revisor-estrategia` lo revisa. Guárdalo en `clientes/<slug>/informes/mensual/AAAA-MM.md` con una tabla de
    estado por bloque (bien / vigilar / actuar). Los cambios en Meta se ejecutan después con `/ejecutar-cambio`.
13. Si `relacion: cliente`, ofrece `/informe-cliente` con el resumen del mes.
