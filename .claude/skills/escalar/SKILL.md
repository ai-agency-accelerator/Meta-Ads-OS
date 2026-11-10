---
name: escalar
description: "Decide si una cuenta o campaña puede escalar y cómo: las 7 condiciones previas, CPA incremental por escalón y coste marginal frente al break-even, palanca correcta (creatividad, inventario nuevo, oferta, señal, puja o presupuesto) y plan por escalones dentro de los topes, con métrica de control y condición de reversión."
argument-hint: "<cliente> [campaña o conjunto]"
---

# /escalar

Entrada: `$ARGUMENTS`. La unidad que se escala es donde vive el presupuesto (campaña con presupuesto de campaña o
conjunto con presupuesto propio).

- **Marco:** `meta-ads-kb/13-sistema-operativo/06-framework-escalado.md` (§1 las 7 condiciones, §2 tipos, §3 coste
  marginal, §4 protocolo vertical, §5 pujas, §6 señales de fallo, §8 errores),
  `meta-ads-kb/09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md`,
  `meta-ads-kb/09-bidding-escalado-economia-analitica/04-cambios-de-presupuesto-y-duplicacion.md`,
  `meta-ads-kb/09-bidding-escalado-economia-analitica/06-estacionalidad.md`,
  `meta-ads-kb/13-sistema-operativo/09-presupuesto-pequeno-y-grande.md`.
- **Agentes:** `analista-meta` (datos), `analista-cuantitativo` (coste marginal y plan), `especialista-crm` (capacidad
  comercial y cohortes), `revisor-estrategia`.
- **Herramientas:** `meta_ads.py anuncios`, `ghl.py` / `stripe_datos.py por-anuncio`, `embudo.py`, `estadistica.py`.
- **Lee:** ficha (economía, topes), `change-log.md`, `informes/semanal/` de las últimas 4–12 semanas, `registro-creativo.csv`,
  `creativos/_lotes/` (cola de producción), `cohortes-leads.md`.
- **Escribe:** `clientes/<slug>/planes/<AAAA-MM-DD>_escalado.md` y `estado.md` (`F6.condiciones`).

## Pasos

1. **Las 7 condiciones** (06 §1), cada una con su dato y «cumple / no cumple / no se puede saber»:

   | # | Condición | Cómo se comprueba aquí |
   |---|---|---|
   | 1 | Rentable a nivel de negocio ≥2 semanas | Coste por venta o CAC de la cohorte (`/embudo`) dentro del target de la ficha |
   | 2 | Volumen estable | ≥50 conversiones por semana en la unidad; aprendizaje sin sobresaltos |
   | 3 | Coste marginal con margen | Paso 2: CPA marginal estimado < break-even |
   | 4 | Pipeline creativo | Un lote nuevo por semana listo y ≥2–3 conceptos con gasto relevante (`registro-creativo.csv`) |
   | 5 | Tracking verificado | Atribución reconciliada con el CRM o Stripe; deduplicación y etapas del CRM llegando |
   | 6 | Capacidad operativa | Agenda comercial, speed to lead, onboarding, soporte y caja para el payback (pregunta al usuario) |
   | 7 | Puja con objetivo: ≥3 semanas estables | Solo si usa coste por resultado u objetivo de ROAS |

   Si falla una, escalar presupuesto amplifica el problema: el plan empieza por arreglarla.
2. **Coste marginal** (`analista-cuantitativo`, 06 §3): semanas completas con gasto distinto
   (`python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --desde <a> --hasta <b>` por semana, o los informes
   semanales). CPA incremental = Δgasto ÷ Δconversiones entre semana base y escalada (misma estacionalidad); con 4–8
   semanas, ajuste log-log (CPA marginal ≈ CPA medio ÷ b). En servicios, el mismo cálculo con citas o ventas de la
   cohorte, no con leads. Revisa el % de gasto en clientes existentes (audience segments).
3. **Palanca** (06 §2):
   - margen marginal amplio → **vertical**: escalones de 15–30 % cada 3–7 días, o saltos mayores aceptando reaprendizaje;
     budget scheduling para picos en vez de duplicar;
   - margen justo o curva plana → **creativa** (ángulos y personas nuevos, `/brief-creativo`), **inventario nuevo**
     (país, idioma, oferta, producto, evento), **oferta** (`/oferta`) o **señal** (optimizar a un evento más profundo o
     con valor, `/implementar-capi`);
   - con volumen (≥50–100 conversiones por semana) y margen que proteger → **puja** (objetivo de coste o de ROAS, tope
     de puja) con 06 §5;
   - nunca duplicar campañas para escalar ni fragmentar en conjuntos por intereses.
4. **Plan por escalones** en `clientes/<slug>/planes/<AAAA-MM-DD>_escalado.md`: escalón, presupuesto (siempre dentro de
   `topes.cambio_dia` y `topes.total_dia`; si el plan los supera, el usuario decide si cambia sus topes en la ficha),
   fecha, métrica de control (CPA incremental del escalón en semana completa madurada), condición para seguir y
   **condición de reversión** (CPA incremental > break-even en semana completa, no por un día). Señales de fallo de
   06 §6 que se vigilarán. Calendario (09/06): BFCM, la segunda semana de diciembre cara, enero más barato.
5. **Incrementalidad:** si el salto es grande o el gasto ya es alto, propón medir antes con `/test-creativo diseñar lift`
   o `geo`.
6. **Revisión y siguiente paso:** `revisor-estrategia` revisa el plan. Marca `F6.condiciones` solo si las 7 se cumplen.
   Cada escalón se ejecuta por separado con `/ejecutar-cambio` y se evalúa en `/informe-semanal`.

## Reglas

- Se decide con el coste marginal, no con el medio. No hay «regla del 20 %» oficial (06 TL;DR).
- Este comando no cambia nada en Meta.
