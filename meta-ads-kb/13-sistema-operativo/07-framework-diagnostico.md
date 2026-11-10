# Framework de diagnóstico — árboles de decisión por síntoma

> Última verificación: 2026-10-16 · Autor: agente principal · Base: [09/09-taxonomía y diagnóstico top-down](../09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md),
> [04/16-checklist QA y árboles de tracking](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md),
> [03/09-diagnóstico ad/oferta/landing/ventas](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md),
> [03/06-fatiga](../03-creatividad/06-fatiga-creativa.md), [02/03-learning](../02-estructura-campanas/03-learning-phase.md),
> [11/09-bugs](../11-benchmarks-casos-expertos/09-bugs-y-comportamientos-raros.md).

## Protocolo general (antes de cualquier árbol)

1. **¿Es real?** Datos maduros (≥7 días, ventana madurada), fuera de la banda de ruido, mismo periodo comparable
   (estacionalidad, misma semana ISO del año anterior). Con <30 eventos, casi todo es ruido.
2. **¿Es Meta o es el negocio?** Mirar backend total y otros canales. Si cae la CVR de la web en TODOS los canales, el
   problema está en web/oferta/precio/stock.
3. **¿Es tracking?** Events Manager (recibidos, dedup, EMQ, diagnósticos) antes que Ads Manager (atribuidos).
4. **¿Cambió algo?** Change log propio (presupuesto, puja, anuncios, landing, precio) y de plataforma (definiciones de
   atribución, retirada de placements, defaults de IA, incidentes en la status page).
5. **Descomponer**: Δln CPA = Δln CPM − Δln CTR − Δln CVR (y AOV para ROAS). Lead gen: coste por venta = CPL /
   (booking × show × close).
6. **Una hipótesis, una palanca, una fecha de evaluación.**

---

## 1. "El CPA ha subido"

```
¿Real? (semana completa, ≥30 eventos, ventana madurada, comparable estacional)
 ├─ No → esperar; anotar.
 └─ Sí → ¿Events Manager recibe el mismo volumen de eventos que el backend?
      ├─ No → tracking (árbol 10/11 abajo).
      └─ Sí → Descomponer:
           ├─ CPM ↑ (CTR y CVR estables) → árbol 3 (CPM).
           ├─ CTR ↓ → ¿en los anuncios que llevan el gasto? → fatiga/saturación (árbol 9) o cambio de mix de placement.
           ├─ CVR ↓ (CTR estable) → post-clic: landing, precio, stock, velocidad, checkout, oferta; calidad del tráfico
           │                          (¿nuevo placement/país? ¿creativo que atrae curiosos?).
           ├─ AOV ↓ (ROAS) → mix de producto, descuentos, volumen vs valor.
           └─ Todo estable pero gasto ↑ → rendimientos decrecientes: CPA marginal > medio (escalado) → árbol de escalado.
```
También revisar: learning reiniciado por ediciones, cambio de definición de atribución (link click desde mar-2026),
gasto desplazado a clientes existentes (audience segments), competidor/promoción del sector.

## 2. "El CTR ha bajado pero el CPA sigue igual"

**Lectura por defecto: no es un problema.** El sistema optimiza a conversión, no a clic.
- Causas habituales: más gasto en placements de menor CTR pero buena conversión (Reels/Stories, Audience Network en
  conversión), creatividad que filtra mejor (menos clics curiosos, más intención), cambio de definición de clic.
- Acción: ninguna sobre el CTR. Vigilar que CVR y calidad se mantengan. Si el CTR baja en el anuncio principal y la
  frecuencia sube, preparar relevo creativo (puede anticipar fatiga).

## 3. "El CPM ha subido un 40 %"

```
¿Toda la cuenta o un ad set/anuncio?
 ├─ Toda la cuenta → ¿estacionalidad? (Q4/BFCM: CPM +35–57 % en 2025; 2.ª semana de dic. muy cara; enero baja)
 │                  ¿mercado? (precio por anuncio de Meta +12 % interanual Q1–Q2-2026; +20 % EE. UU./Canadá)
 │                  ¿mix geográfico/placement? (más EE. UU., más IG Feed) → breakdown por geo/placement
 │                  ¿cambio de evento/objetivo? (optimizar a compra cuesta más CPM que a clic: es normal)
 │                  ¿fees por país? (location fees 2–5 % desde 1-jul-2026 se facturan aparte, no en CPM de Ads Manager)
 └─ Un ad set/anuncio → ¿audiencia más pequeña/restricciones? ¿calidad (feedback negativo, ocultaciones)?
                        ¿saturación (frecuencia ↑ con alcance plano)?
¿Ha subido el CPA en la misma proporción?
 ├─ No (CTR/CVR compensan) → aceptar; el CPM es diagnóstico, no KPI en conversión.
 └─ Sí → ajustar expectativas (estacionalidad) o actuar sobre lo controlable: creatividad (CTR), oferta/landing (CVR),
          diversidad para abrir inventario; no perseguir CPM bajo a costa de calidad.
```
**[OFFICIAL META]**: con optimización a conversión el sistema puede pagar CPM más alto para bajar el coste por conversión.

## 4. "Tenemos muchos leads pero no cierran"

```
1. Medir por cohorte: lead → cualificado → cita → show → cierre (por campaña, anuncio, formulario, placement, edad, país).
2. ¿Dónde cae?
   ├─ Cualificación baja (leads falsos, no contestan, no encajan)
   │    ├─ Formulario demasiado fácil (more volume, autofill) → Higher intent, preguntas de cualificación (3–5),
   │    │   SMS/OTP, aviso de llamada; no preguntar ingresos/salud (prohibido)
   │    ├─ Creativo/oferta que atrae curiosos ("gratis", curiosidad) → ángulos que pre-cualifican (precio, para quién NO es)
   │    ├─ Optimización a "Lead" bruto → qualified leads con CAPI CRM (exige CAPI desde abr-2026)
   │    ├─ Placements/segmentos de baja calidad (Audience Network en algunos casos, edades) → value rules / exclusión a
   │    │   nivel cuenta solo con evidencia de cohortes
   │    └─ Spam/bots → OTP, honeypot en web, revisar fuentes
   ├─ Cualifican pero no agendan → speed to lead (>5 min mata contacto), secuencias de seguimiento, reserva directa
   ├─ Agendan pero no se presentan → recordatorios (SMS/WhatsApp/email), confirmación, plazo corto hasta la cita,
   │    contenido pre-llamada
   └─ Se presentan pero no compran → problema de oferta/precio/encaje o de ventas (guion, closer, seguimiento) — NO de Meta
3. Devolver a Meta las etapas (CAPI CRM) para que optimice a calidad; juzgar campañas por coste por venta de la cohorte.
```
→ [05/03-calidad de lead](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md),
[05/08-speed to lead](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md)

## 5. "Un anuncio tiene un CTR brutal pero no vende"

Hipótesis por orden de probabilidad:
1. **Promesa ≠ landing** (message match roto, precio sorpresa, oferta distinta) → comparar la promesa con lo que ve el
   usuario above the fold.
2. **Atrae curiosos, no compradores** (hook de curiosidad, polémica, "gratis", meme) → el creativo segmenta hacia
   clicadores; el CVR del tráfico es bajo. Mirar LPV rate (clics accidentales), tiempo en página, ATC.
3. **Placement/segmento** con clics baratos y baja intención (algunos placements de AN o in-stream) → breakdown con cautela.
4. **Tracking del evento final roto solo en ese recorrido** (landing distinta, dominio distinto, `fbclid` perdido).
5. **Muestra pequeña** (pocas compras esperadas): con 3 compras esperadas, 0 es probable (5 %).
Acción: no escalar por CTR; arreglar message match o usar el insight del hook con una promesa más cualificada.

## 6. "Una campaña nueva no gasta"

```
¿Estado de entrega?
 ├─ En revisión / rechazada → políticas (08/09); no duplicar en masa anuncios rechazados.
 ├─ Problema de pago / límite de gasto de cuenta o de campaña → Billing; cuentas nuevas tienen límite diario.
 ├─ Bid/cost limited → objetivo de coste/ROAS demasiado ambicioso o bid cap bajo; presupuesto < 5× objetivo.
 │     → relajar objetivo o pasar a Highest volume.
 ├─ Audiencia pequeña / restricciones (geo, edad, exclusiones, categoría especial, idioma) → ampliar.
 ├─ Solapamiento con otra campaña propia (auction overlap) → consolidar.
 ├─ Programación (lifetime con horario, fechas), anuncios pausados, URL rota, evento sin datos (custom conversion
 │     "flagged" por términos de salud/finanzas desde sep-2025 deja de emparejar).
 ├─ Placement sin asset compatible (tras la retirada de placements manuales, sin asset compatible no se entrega en ese
 │     placement) → assets 9:16 y 4:5.
 └─ Nada de lo anterior y <24–48 h → esperar; Meta explora. Si persiste: añadir conceptos distintos, revisar calidad
       (feedback negativo previo de la Página), incidentes de Meta.
```

## 7. "Un ad set está en Learning Limited"

- **No es una penalización** (Meta). Significa que no se prevé llegar a ~50 resultados en la semana tras la última
  edición significativa. **[OFFICIAL META]**
- Causas: presupuesto bajo respecto al CPA, audiencia pequeña, puja/objetivo restrictivo, solapamiento con otros ad sets,
  evento raro.
- Acciones estructurales (no micro-ediciones): consolidar ad sets del mismo objetivo; ampliar audiencia/placements;
  subir presupuesto (≈7× CPA/día); relajar objetivo de coste; elegir un evento más frecuente **valioso**; o aceptarlo si
  el CPA está dentro de target (muchas cuentas pequeñas viven bien en learning limited).

## 8. "Meta está gastando casi todo en un creativo viejo"

- **Si el creativo viejo cumple target**: es lo esperado (ventaja del incumbente; el sistema predice mejor respuesta).
  No pausarlo para "forzar" a los nuevos.
- **Si los nuevos no reciben gasto**: ¿son realmente distintos o variaciones del viejo? (creativos parecidos se tratan como
  redundantes). Dar gasto garantizado: herramienta *Creative testing* (≤20 % del presupuesto), ad set de test con
  presupuesto propio, o "push delivery" donde esté disponible; campaña "underspend" para anuncios infra-gastados.
- **Si el viejo se está fatigando** (CPA del anuncio sube por cohortes de impresiones, CTR ↓, *Creative fatigue* en Delivery
  = coste ≥2× histórico): preparar relevo con conceptos nuevos e iteraciones del ganador.

## 9. "¿Fatiga creativa o varianza?"

| Señal | Fatiga real | Varianza / otra causa |
|---|---|---|
| Alcance | Afecta a 1 anuncio/concepto | Afecta a toda la cuenta |
| CTR y hook rate del anuncio | ↓ sostenido por impresiones acumuladas | Oscila sin tendencia |
| CPM | No sube con la edad del creativo (Interconnections 2026: 15 cuentas DTC, 368 creatividades; evidencia débil) | ↑ en toda la cuenta → subasta/estacionalidad |
| Frecuencia | ↑ con alcance plano | — |
| Delivery | *Creative limited/fatigue* | — |
| Con 14 días agregados | La tendencia persiste | Desaparece |

Remedio según causa: concepto fatigado → iterar hooks/formatos; bolsillo agotado → nuevo ángulo/persona; oferta
cansada → nueva oferta.

## 10. "Tenemos 8 ventas pero Ads Manager solo ve 3"

Árbol completo en [04/16 §2](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md). Resumen:
1. ¿Events Manager recibió ~8 Purchase? **No** → tracking (Pixel en confirmación, CAPI ausente, consentimiento UE,
   restricciones de categoría, errores 4xx). **Sí** → atribución: ¿cuántas de las 8 vinieron de personas con interacción
   de Meta en ventana? (backend con `fbclid`/UTM), lag > ventana (mirar 28d click), EMQ bajo / sin `fbc`, `fbclid`
   perdido en redirecciones, compras de recurrentes/email (correcto que no aparezcan), incremental attribution,
   cambio de definición de clic (mirar engage-through), datos < 72 h.

## 11. "Ads Manager dice 20 ventas y Stripe 13"

Árbol completo en [04/16 §3](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md). Resumen:
Events Manager ≫ 13 → duplicación (dedup roto, dos emisores, recargas de thank-you page, Purchase en pagos fallidos,
upsells, pedidos de prueba). ≈ 13 recibidos → sumas de campañas/ventanas distintas, "all conversions" vs "first
conversion", custom conversion que agrupa otros eventos, zona horaria/moneda, Stripe neto de reembolsos.

## 12. "Buen ROAS en Ads Manager pero el negocio pierde dinero"

```
1. ¿El ROAS break-even está bien calculado? (contribución, no revenue; IVA en la misma base que el valor enviado;
   devoluciones; fees por país; agencia; creatividad) → muchas veces el "buen ROAS" está por debajo del break-even real.
2. ¿Lo atribuido es incremental? → % gasto en clientes existentes/engaged (audience segments), retargeting, view/engage-
   through; holdout o geo-test. (Haus: el retargeting/BOF es donde más se infla; Advantage+ sobre-reporta ~12 pp vs manual.)
3. ¿Doble conteo entre plataformas? → la suma de lo que reclaman todas supera las ventas reales.
4. ¿Valor enviado inflado? (duplicados, valor con IVA/envío, pedidos cancelados que no se restan)
5. ¿Coste marginal? → el ROAS medio oculta que el último tramo de gasto pierde.
6. ¿Economía post-venta? (LTV, devoluciones, chargebacks, coste de servir)
Decisión: gestionar con MER/contribución/nCAC y coste marginal; reasignar a adquisición incremental.
```

## 13. "Tracking roto después de una actualización"

Árbol completo en [04/16 §4](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md): delimitar
qué cambió → ¿cayó navegador, servidor o ambos? → token/versión de API (v24 expiró el 6-oct-2026; retiradas de v26 en (Corrección 2026-11-09: la v24 expira el 10-nov-2026; v27.0 desde el 4-nov.)
todas las versiones el 27-oct-2026), CMP, CSP, plugin/app, checkout de Shopify (scripts adicionales de thank-you page
en solo lectura) → dedup → EMQ → corregir una cosa, verificar con Test Events, monitorizar 72 h.

## 14. "Cuenta restringida / anuncios rechazados en cadena"

→ [08/09-rechazos y apelaciones](../08-cuenta-politicas-seguridad/09-rechazos-apelaciones-que-no-hacer.md),
[08/01-account quality](../08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md)
1. Account Quality: qué activo está restringido (perfil, ad account, Portfolio, Página, dominio) y por qué política.
2. Rechazo puntual: pedir revisión si creemos que es error (una re-revisión por anuncio; borrar el anuncio puede impedir
   la revisión; editarlo no borra la infracción); si el anuncio sí incumple, corregir copy/landing y crear uno nuevo.
3. Patrón de rechazos → revisar claims (ingresos, salud, atributos personales), landing y coherencia anuncio-landing.
4. **Nunca**: crear cuentas nuevas para seguir igual, cuentas alquiladas, cloaking, ofuscar palabras (circunvención →
   puede tumbar todos los activos del dueño).
5. Cuenta deshabilitada: 6 meses para pedir la reinstauración; solo un admin; revisiones limitadas y finales.

## 15. "El gasto de hoy es muy superior al presupuesto"

- Normal hasta 175 % del diario (210 % con budget sharing); el tope es semanal (7×). Revisar la semana, no el día.
- Anómalo si supera esos límites, si hay budget scheduling activo olvidado o reglas/agentes (MCP) que modificaron el
  presupuesto → revisar el historial de actividad y las reglas MCP del portfolio.
