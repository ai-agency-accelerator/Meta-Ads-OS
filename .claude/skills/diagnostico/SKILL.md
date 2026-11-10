---
name: diagnostico
description: "Diagnostica un síntoma concreto con datos reales y los árboles de decisión: sube el CPA o el CPM, CTR alto sin ventas, no gasta, learning limited, fatiga o varianza, leads que no cierran, ROAS bueno con pérdidas, Meta y CRM no cuadran, tracking roto, gasto por encima del presupuesto. Termina en una causa y una sola acción."
argument-hint: "<cliente> \"<síntoma>\""
---

# /diagnostico

Entrada: `$ARGUMENTS` (cliente y síntoma con sus palabras: «desde el martes los leads nos cuestan el doble»).

- **Marco:** `meta-ads-kb/13-sistema-operativo/07-framework-diagnostico.md` (protocolo general y árboles 1–15), tracking
  en `meta-ads-kb/04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md`, métricas en
  `meta-ads-kb/09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md`, estadística en
  `meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md`, cambios recientes de la plataforma
  en `meta-ads-kb/00-ESTADO-ACTUAL-2026.md`.
- **Agentes** según la rama: `analista-meta` (siempre), `especialista-tracking`, `especialista-funnel`,
  `especialista-crm`, `analista-cuantitativo`, `revisor-politicas`.
- **Herramientas:** `estadistica.py banda|ic-cpa|identicos|lag`, `meta_ads.py vigente|anuncios --por-dia|eventos`,
  `ghl.py`, `stripe_datos.py`, `embudo.py`.
- **Lee:** ficha, `change-log.md`, `logs/cambios.jsonl` (escrituras ejecutadas por el sistema), `informes/diario/` de los
  últimos días, último informe semanal.
- **Escribe:** `clientes/<slug>/informes/diagnosticos/<AAAA-MM-DD>_<sintoma>.md` y, si hay acción, la propuesta para
  `/ejecutar-cambio`.

## Pasos

1. **Concreta el síntoma:** métrica, unidad (campaña o conjunto donde vive el presupuesto), desde cuándo, frente a qué
   periodo, con qué ventana de atribución.
2. **Protocolo previo** (las cuatro preguntas, en este orden):
   1. **¿Es real?** Datos maduros (≥7 días, ventana madurada) y fuera de la banda de ruido:
      `python3 -I herramientas/estadistica.py banda --media <eventos medios por periodo>`; intervalo del CPA con
      `estadistica.py ic-cpa --gasto <g> --conversiones <n>`; ¿dos periodos son distinguibles?
      `estadistica.py identicos --conversiones <n>`; días recientes sin madurar: `estadistica.py lag`. Con <30 eventos,
      casi todo es ruido: dilo y para aquí si no es una rotura.
   2. **¿Es Meta o es el negocio?** Backend total y otros canales (`ghl.py`, `stripe_datos.py` o lo que tenga el
      cliente). Si cae en todos los canales, el problema está en la web, la oferta o el precio.
   3. **¿Es tracking?** Eventos recibidos (`meta_ads.py eventos --cliente <slug>` o `ads_get_dataset_stats`) frente a
      atribuidos, deduplicación y calidad (`ads_get_dataset_quality`).
   4. **¿Qué cambió?** `change-log.md`, `logs/cambios.jsonl`, historial de la cuenta
      (`ads_account_get_activity_logs`), briefs diarios recientes, filas `Meta (plataforma)` del change log y
      `00-ESTADO-ACTUAL-2026.md` (definiciones de atribución, ubicaciones, valores por defecto de IA). Con token, qué
      pausaron las reglas automáticas: `python3 -I herramientas/reglas_meta.py historial --cliente <slug> --todas`.
      Discontinuidades de 2026 que fabrican «síntomas»: medición en el dispositivo activada por defecto desde el
      2026-11-12 (más conversiones reportadas fuera de la UE y el Reino Unido), iOS 27.2 desde el 2026-10-26 (apps y
      atribución en la UE) y precio por anuncio +14 % en Q3-2026 (CPM al alza en toda la subasta).
3. **Elige el árbol** y recórrelo rama a rama con datos (cada rama descartada, con su dato):

   | Síntoma | Árbol (07) | Quién mira |
   |---|---|---|
   | Sube el CPA o el coste por lead | 1 (descomposición Δln CPA = Δln CPM − Δln CTR − Δln CVR) | `analista-meta` |
   | Baja el CTR pero el CPA sigue igual | 2 | `analista-meta` |
   | El CPM se dispara | 3 (descarta antes la subida general de Q3-2026) | `analista-meta` |
   | Muchos leads que no cierran | 4 (CPL → cualificado → cita → show → venta, por cohorte con `/embudo`) | `especialista-crm`, `especialista-funnel` |
   | CTR altísimo sin ventas | 5 | `especialista-funnel` |
   | Campaña nueva que no gasta | 6 | `analista-meta` (`ads_get_errors`, `meta_ads.py vigente`) |
   | Learning limited | 7 | `analista-meta`, `analista-cuantitativo` |
   | Todo el gasto en un creativo viejo | 8 (en anuncios multi-media, desglose por asset: Breakdown → Creative → Media; es lectura, no test) | `analista-meta` |
   | ¿Fatiga o varianza? | 9 (con `meta_ads.py anuncios --por-dia`; 14 días agregados) | `analista-meta` |
   | El backend ve más ventas que Meta | 10 | `especialista-tracking` (04/16 §2) |
   | Meta ve más ventas que Stripe o el CRM | 11 | `especialista-tracking` (04/16 §3) |
   | Buen ROAS y el negocio pierde dinero | 12 | `analista-cuantitativo` (`/economia`) |
   | Tracking roto tras una actualización | 13 | `especialista-tracking` (04/16 §4) |
   | Cuenta restringida o rechazos en cadena | 14 | **para aquí y pasa a `/rescate-cuenta`** |
   | Hoy se gasta mucho más que el presupuesto | 15 (hasta 175 % del diario es normal; el tope es semanal) | `analista-meta` |

   Si el síntoma no encaja en ninguno, aplica el protocolo y la descomposición de arriba abajo (negocio → funnel →
   anuncios → creatividad) y dilo.
4. **Conclusión:** causa más probable con etiqueta de evidencia ([OFFICIAL META], [EMPIRICAL], [STRONG INFERENCE],
   [HYPOTHESIS]), causas descartadas y por qué, qué dato falta para confirmarla y cómo conseguirlo.
5. **Una acción:** una hipótesis, una palanca, una métrica y una fecha de evaluación. «No tocar y esperar hasta <fecha>»
   es una acción válida y muchas veces la correcta. Si toca Meta → `/ejecutar-cambio`; si es creativa →
   `/siguiente-anuncio` o `/variantes`; si es post-clic → `/landing`, `/embudo` o `/seguimiento-leads` (leads sin
   contactar a tiempo); si es señal → `/implementar-capi`.
6. **Guarda** el diagnóstico en `clientes/<slug>/informes/diagnosticos/<AAAA-MM-DD>_<sintoma>.md` (síntoma, datos,
   árbol recorrido, conclusión, acción). Si contradice algo de la base de conocimiento, regístralo con
   `/novedades-meta aprendizaje <cliente> "<qué se observó>"`.

## Reglas

- Solo lectura: este comando no cambia nada en Meta, en el CRM ni en Stripe.
- Una hipótesis cada vez: varias palancas a la vez impiden saber qué funcionó.
