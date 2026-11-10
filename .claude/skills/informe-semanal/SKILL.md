---
name: informe-semanal
description: "Informe semanal interno de un cliente de arriba abajo (negocio y CRM o Stripe, funnel por cohortes, anuncios, creatividad) sobre la última semana natural completa: actualiza el registro creativo, evalúa los cambios que vencen y propone como máximo 3 decisiones con hipótesis y fecha de evaluación."
argument-hint: "<cliente> [AAAA-Www]"
---

# /informe-semanal

Entrada: `$ARGUMENTS`. Sin semana, la última semana natural completa (lunes a domingo). Nunca una semana a medias.

- **Marco:** `meta-ads-kb/13-sistema-operativo/04-operativa-diaria-semanal-mensual.md` §2 (orden y decisiones) y §5
  (disciplina), plantilla `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §5, descomposición en
  `meta-ads-kb/13-sistema-operativo/07-framework-diagnostico.md` (protocolo general, paso 5), lag de atribución en
  `meta-ads-kb/04-tracking-atribucion-medicion/12-attribution-lag.md`, paciencia en
  `meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md`, cohortes en
  `meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md`.
- **Agentes:** `analista-meta` (lectura de Meta), `especialista-crm` (GHL o CRM), `analista-cuantitativo` (si hay que
  estimar coste marginal o ruido), `revisor-estrategia` (decisiones).
- **Herramientas:** `estado.py`, `meta_ads.py anuncios`, `ghl.py por-anuncio`, `stripe_datos.py por-anuncio`,
  `registro_creativo.py`, `embudo.py`, `estadistica.py`.
- **Lee:** ficha (economía, ventana de atribución, evento), `change-log.md`, `informes/diario/` de la semana,
  `informes/semanal/` anterior, `investigacion/vigilancia/` (último resumen), `creativos/_lotes/`.
- **Escribe:** `clientes/<slug>/informes/semanal/AAAA-Www.md`, `registro-creativo.csv`, `cohortes-leads.md`, columna
  `Resultado` del change log, `aprendizajes-creativos.md` y `estado.md` (`F5.registro`, `F5.evaluaciones`, `F5.cadencia`).

## Pasos

1. **Situación:** `python3 -I herramientas/estado.py resumen --cliente <slug> --json` (fase, evaluaciones vencidas,
   cola de producción). Semana analizada, la anterior y, si hay estacionalidad, la misma semana ISO del año pasado.
2. **Negocio primero** (la capa más baja de verdad):
   - servicios: `python3 -I herramientas/ghl.py por-anuncio --cliente <slug> --desde <lunes> --hasta <domingo>` (leads,
     cualificados, citas, shows, ventas, cash);
   - SaaS o cobros con Stripe: `python3 -I herramientas/stripe_datos.py por-anuncio --cliente <slug> --desde <lunes> --hasta <domingo>`;
   - sin CRM conectado: pide al usuario las cifras de la semana o un CSV en `privado/`. Sin negocio, el informe lo dice
     en la primera línea y las decisiones de presupuesto quedan en suspenso.
   ¿Hay problema frente al target de la ficha? Si no lo hay, no se fuerza ninguna optimización.
3. **Funnel por cohortes:** `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por semana --guardar`
   (con `--modelo servicios` o `saas`; usa el CSV de leads de `privado/` y, si existe, la exportación de Meta por día).
   Señala qué cohortes son maduras y qué etapa se rompe (CPL → cualificado → cita → show → venta; o registro → prueba
   → activación → pago).
4. **Meta** (`analista-meta`):
   - con token: `python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --desde <lunes> --hasta <domingo>`
     (guarda el CSV en `clientes/<slug>/datos/`); sin token, el MCP o una exportación de Ads Manager guardada en `datos/`;
   - CPA o coste por resultado en la ventana de la ficha y lectura conservadora a 1d click; descomposición
     Δln CPA = Δln CPM − Δln CTR − Δln CVR; frecuencia y alcance; gasto frente a presupuesto; learning;
   - ¿el cambio sale de la banda de ruido? `python3 -I herramientas/estadistica.py banda --media <conversiones medias>`;
   - días sin madurar: `estadistica.py lag --conv-1d <a> --conv-7d <b>`;
   - discontinuidades de plataforma que rompen la comparación (`meta-ads-kb/00-ESTADO-ACTUAL-2026.md`): medición en el
     dispositivo activada por defecto desde el 2026-11-12 (más conversiones reportadas fuera de la UE y el Reino Unido
     sin cambio real), iOS 27.2 desde el 2026-10-26 (apps y atribución en la UE) y CPM al alza desde Q3-2026 (precio
     por anuncio +14 % interanual): no compares a través de esas fechas sin decirlo;
   - qué pausaron o avisaron las reglas automáticas: `python3 -I herramientas/reglas_meta.py historial --cliente <slug>
     --dias 7 --todas` (con token).
5. **Registro creativo:** `python3 -I herramientas/registro_creativo.py actualizar --cliente <slug> --meta <csv de Meta> [--ghl <csv>] [--stripe <csv>]`
   (mismo periodo en las tres) y `registro_creativo.py sin-nomenclatura --cliente <slug>`. Revisa los veredictos
   propuestos (ganador provisional o candidato a confirmado, perdedor, en test) antes de darlos por buenos; para fijar
   uno a mano, `motivo` empieza por `manual:`. Marca `F5.registro`.
6. **Creatividad:** reparto del gasto por anuncio y concepto; hook rate, hold y CTR de los que llevan el gasto;
   anuncios nuevos con y sin gasto; fatiga por cohorte de antigüedad (CPA por impresiones acumuladas, no frecuencia
   sola, `meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md`); lote en cola y si llega a tiempo.
   Novedades de la vigilancia de competencia, si las hay.
   - Si hay un `informes/analisis-creativo/` de las últimas 4 semanas, enlázalo y no lo rehagas. Las columnas
     `retencion_pXX` y `curva_retencion` del CSV de `meta_ads.py anuncios` explican caídas de hook o hold; el
     diagnóstico completo es `elementos_creativos.py retencion` (`/analisis-creativo`).
   - En anuncios con varios medios o textos, el desglose por asset de Ads Manager (Breakdown → Creative → Media o
     *Dynamic creative element*) dice qué pieza se lleva la entrega: es una lectura para hipótesis, no un test.
7. **Evaluaciones del change log:** filas con fecha de evaluación ≤ domingo analizado. Evalúa cada una con la regla de
   paciencia (≥7 días, 30–50 eventos, ventana madurada) y escribe el `Resultado` (cumplió / no cumplió / no
   concluyente y por qué). Si quedan vencidas sin evaluar, el informe lo dice. Marca `F5.evaluaciones` si no queda
   ninguna.
8. **Briefs diarios** de la semana (`clientes/<slug>/informes/diario/`): roturas detectadas, si se resolvieron y si
   alguna sigue abierta.
9. **Decisiones:** como máximo 3 palancas por unidad de presupuesto (04 §2.5): lote creativo nuevo, apagar anuncios a
   ≥2–3× CPA sin conversión (`estadistica.py kill`), presupuesto solo si el coste marginal lo permite y hay ≥2 semanas
   estables (`/escalar`), pujas en ajustes de 5–10 %. Cada una con hipótesis, métrica de éxito y fecha de evaluación.
   `revisor-estrategia` las revisa. **Nada se ejecuta desde aquí:** las que tocan Meta van por `/ejecutar-cambio` en la
   ventana de edición; las creativas, por `/siguiente-anuncio` o `/brief-creativo`.
10. **Guarda** el informe con la plantilla 10 §5 en `clientes/<slug>/informes/semanal/AAAA-Www.md`: negocio, qué ha
    pasado (3 puntos con causa), funnel, Meta, creatividad, decisiones y próxima evaluación, próxima semana y **notas de
    medición** (ventana y periodo, días sin madurar, cambios de plataforma que afectan a la comparación). Aprendizajes
    nuevos a `aprendizajes-creativos.md`. Marca `F5.cadencia` si el brief diario también está en marcha.
11. Si la ficha dice `relacion: cliente`, ofrece `/informe-cliente` para la versión que verá el cliente. Si
    `contexto/preferencias.md` tiene canal configurado, ofrece mandarte el resumen con
    `python3 -I herramientas/notificar.py enviar --archivo clientes/<slug>/informes/semanal/AAAA-Www.md` (solo con tu sí).

## Reglas

- Semanas completas y la misma ventana de atribución en todas las comparaciones; dila siempre.
- Una semana mala no es una tendencia: sin salir de la banda de ruido, la decisión es no tocar.
- Ningún dato personal en el informe: solo agregados e IDs.
