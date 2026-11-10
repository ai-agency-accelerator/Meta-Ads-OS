---
name: test-creativo
description: "Diseña o lee un experimento en Meta con potencia estadística: test creativo (concepto, formato o hook), A/B test de estrategia, Conversion Lift o test geográfico de incrementalidad. Calcula conversiones, presupuesto y duración, fija reglas de parada y da veredicto: diferencia real, no distinguible o faltan datos."
argument-hint: "<cliente> diseñar|leer <creativo|ab|lift|geo> [detalles o ficha del test]"
---

# /test-creativo

Entrada: `$ARGUMENTS`.

- **Marco:** `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` (niveles §1, métrica y estructura §2–3,
  escalera de decisión §5, higiene §6), `meta-ads-kb/09-bidding-escalado-economia-analitica/13-experimentacion-ab-tests.md`
  (qué herramienta para qué pregunta §1, A/B §2–3, holdouts §5, errores §6),
  `meta-ads-kb/04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md` (Conversion Lift §2, geo §4,
  checklist §4.3), `meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md`.
- **Agentes:** `analista-cuantitativo` (diseño y lectura), `analista-meta` (datos por brazo), `especialista-crm` (capa de
  negocio), `revisor-estrategia`; la creación en Meta la hace `operador-meta` vía `/ejecutar-cambio` o `/publicar-anuncios`.
- **Herramientas:** `python3 -I herramientas/estadistica.py potencia|detectable|kill|comparar|ic-cpa|identicos|lag`.
- **Escribe:** `clientes/<slug>/planes/tests/<AAAA-MM-DD>_<test>.md` (ficha del test), `aprendizajes-creativos.md`,
  `registro-creativo.csv` (veredictos), `change-log.md` (resultado de la evaluación) y la ficha del cliente
  (incrementalidad).

## Diseñar

1. **Pregunta y nivel** (05 §1): oferta > ángulo > concepto > formato > hook > cuerpo > copy. Elige el tipo:

   | Pregunta | Tipo | Herramienta |
   |---|---|---|
   | ¿Este concepto o ángulo abre un bolsillo rentable? | `creativo` | Gasto garantizado: *Creative testing* nativa o conjunto de test |
   | ¿Qué hook o cuerpo para y retiene mejor? | `creativo` | *Creative testing* (2–5 variantes) o anuncio con varios textos |
   | ¿Qué estrategia es mejor (puja, evento, estructura, Advantage+ o manual)? | `ab` | A/B test de Experiments (`ads_experiment_check_eligibility`) |
   | ¿Cuánto vende de más Meta o una campaña? | `lift` | Conversion Lift (`ads_experiment_lift_create_test`; el acceso puede estar limitado) |
   | Lo mismo, midiendo todo el negocio y sin depender de la plataforma | `geo` | Geo-holdout (GeoLift u otra herramienta externa) |

2. **Métrica:** la capa más baja de verdad con n suficiente (servicios: venta > cita o show > cualificado > CPL; SaaS:
   cliente de pago > prueba activada > prueba > registro). Hooks y cuerpos: hook rate, hold y CTR **con CVR estable**.
   High-ticket: proxy validado por el CRM y confirmación con el coste por venta de la cohorte (05 §5).
3. **Potencia:** `python3 -I herramientas/estadistica.py potencia --diferencia <0.3>` → conversiones por brazo;
   presupuesto ≈ conversiones × CPA esperado × brazos; duración = presupuesto / gasto diario del test. Con el
   presupuesto que hay, `estadistica.py detectable --conversiones <n>` dice qué diferencia se podría ver. Si no cabe:
   test de un salto mayor o métrica intermedia. Referencia: Δ20 % ≈ 470 conversiones por brazo; 2× ≈ 33 (05 §2).
4. **Estructura y condiciones** según el tipo:
   - `creativo`: estructura por tamaño de cuenta (05 §3). *Creative testing* nativa: 2–5 anuncios, ≤20 % del
     presupuesto, 7 días, solo Highest volume. [EMPIRICAL] En una cuenta de servicios high-ticket funcionó separar
     hooks en conjuntos ABO con el mismo presupuesto para forzar gasto comparable; tiene el solapamiento que señala
     09/13 §6, así que úsalo como filtro, no como experimento.
   - `ab`: hasta 5 versiones, 1–30 días, mismo presupuesto, potencia estimada ≥80 % en la pantalla de Meta, ninguna
     edición durante el test.
   - `lift`: ≥7 días y ≥10 % de audiencia por celda; ventana de observación posterior; puede subir el CPM; una vez
     iniciado no se cambian `start_time` ni el porcentaje de tratamiento.
   - `geo`: checklist de 04/13 §4.3: pregunta única; KPI de negocio por región sacado del CRM o de Stripe (agregado
     por provincia o región; nunca direcciones fuera de `privado/`); pre-periodo de varias veces la duración; diseño
     *go-dark* o *heavy-up*; congelar otras palancas; ventana posterior; umbral de iROAS escrito antes. El análisis de
     potencia y de resultados con GeoLift (R) se hace fuera del sistema con los CSV que prepares en `clientes/<slug>/datos/`.
5. **Reglas escritas antes de lanzar:** kill a 2–3× CPA sin conversión (`estadistica.py kill --cpa-objetivo <x> --gasto <y>`),
   ganador provisional con ≥10–20 conversiones, confirmado con ≥30–50 y ≥7 días; misma ventana y periodo; mejoras
   automáticas documentadas; sin tocar presupuesto a mitad; sin mirar resultados antes de la fecha (peeking).
6. **Ficha del test** con la plantilla de `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §4 en
   `clientes/<slug>/planes/tests/<AAAA-MM-DD>_<test>.md`. `revisor-estrategia` la revisa.
7. **Montaje:** anuncios nuevos → `/publicar-anuncios`; A/B, lift, conjunto de test o exclusiones geográficas →
   `/ejecutar-cambio` con la ficha como plan.

## Leer

1. Abre la ficha del test y comprueba que se ha cumplido la duración pactada y que no hubo ediciones (revisa el change
   log). Si no, «faltan datos» y nueva fecha.
2. **Datos:** `analista-meta` por brazo; `ads_experiment_abtest_get_test` o `ads_experiment_lift_get_test`; capa de
   negocio con `/embudo` o `ghl.py` / `stripe_datos.py por-anuncio`. Madurez de los últimos días:
   `estadistica.py lag --conv-1d <a> --conv-7d <b>`.
3. **Cálculo:**
   - creativo y A/B: `python3 -I herramientas/estadistica.py comparar --gasto-a <g> --conv-a <n> --gasto-b <g> --conv-b <n>`
     e `ic-cpa` por brazo; con muchas variantes, cuidado con los falsos positivos (09/13 §6.4);
   - lift: conversiones incrementales, iCPA y factor de incrementalidad (IF = incrementales ÷ reportadas);
   - geo: lift frente al control sintético y iROAS frente al umbral pre-registrado.
4. **Veredicto:** diferencia real, no distinguible o faltan datos (cuántas conversiones y días más). Decide con la regla
   escrita en la ficha, no con la que apetezca al ver el resultado.
5. **Registro:** resultado, decisión y aprendizaje en la ficha del test; fila en `aprendizajes-creativos.md` (qué creemos
   sobre el mercado, no solo qué anuncio ganó); `veredicto`, `fecha_veredicto` y `motivo` en `registro-creativo.csv`
   con `motivo` empezando por `manual:` (p. ej. `manual: test 2026-11-02, Δ coste por cita −31 %, 41 vs 28 citas`) para
   que `registro_creativo.py actualizar` no lo recalcule;
   `Resultado` en la fila del change log. Incrementalidad: anota el IF en la ficha («Medición → Incrementalidad») y
   recalibra el objetivo (ROAS objetivo en plataforma = ROAS break-even ÷ IF, 09/13 §5). Si el resultado confirma o
   contradice la base de conocimiento, `/novedades-meta aprendizaje <cliente> "<resultado>"`.
