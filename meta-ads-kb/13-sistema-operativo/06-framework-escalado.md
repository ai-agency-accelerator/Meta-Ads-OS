# Framework de escalado — condiciones, tipos, pasos y señales de fallo

> Última verificación: 2026-10-16 · Autor: agente principal · Fundamento en
> [09/03-escalado](../09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md),
> [09/04-presupuesto y duplicación](../09-bidding-escalado-economia-analitica/04-cambios-de-presupuesto-y-duplicacion.md),
> [09/01-pujas](../09-bidding-escalado-economia-analitica/01-estrategias-de-puja.md) y
> [02/06-presupuesto](../02-estructura-campanas/06-presupuesto-por-niveles.md).

## TL;DR

- **Escalar = comprar conversiones marginales más caras.** Decide con CPA/ROAS **marginal**, no medio. **[OFFICIAL META]**
  (Meta: el sistema toma primero las oportunidades más baratas) + **[STRONG INFERENCE]**
- **Antes de escalar presupuesto, las 7 condiciones** (sección 1). Si falta una, escalar amplifica el problema.
- **La palanca principal de escala en 2026 es creativa** (diversidad de ángulos/personas/formatos) y de **inventario nuevo**
  (países, ofertas, productos, eventos), no la fragmentación en ad sets. **[OFFICIAL META]** + **[EMPIRICAL]**
- **No hay "regla del 20 %" oficial.** Meta: los cambios de presupuesto pueden reiniciar learning según su magnitud
  (100→101 no; 100→1.000 puede). Ritmo prudente: subidas de 15–30 % cada 3–7 días en ad sets estables; saltos mayores
  aceptables si se asume re-learning y hay margen. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Duplicar para escalar está obsoleto**: solapamiento de subasta **[OFFICIAL META]**; además, la investigación de Meta
  apunta a eliminar la varianza aleatoria entre copias, aunque no está medido en ad sets reales **[STRONG INFERENCE]**.
- **Señales de fallo**: CPA marginal > break-even, CPM↑ con frecuencia↑ y alcance plano, % clientes nuevos↓,
  MER/contribución plano pese a más gasto, calidad de lead↓.

---

## 1. Condiciones necesarias (checklist)

| # | Condición | Cómo se verifica |
|---|---|---|
| 1 | Rentabilidad a nivel negocio, no solo en Ads Manager | MER/contribución/nCAC o coste por venta (lead gen) dentro de target ≥2 semanas |
| 2 | Volumen estable | ≥50 conversiones/semana en la unidad que se escala; fuera de learning o learning sin sobresaltos |
| 3 | Coste marginal con margen | CPA marginal estimado (sección 3) < break-even |
| 4 | Pipeline creativo | ≥1 lote nuevo/semana listo; ≥2–3 conceptos con gasto relevante (no dependencia de un único anuncio) |
| 5 | Tracking verificado | Atribución reconciliada con backend; CAPI/dedup ok; etapas CRM llegando |
| 6 | Capacidad operativa | Stock, equipo comercial (speed to lead), agenda, soporte, caja para el payback |
| 7 | Goal-based: ≥3 semanas estables | Meta lo pide antes de escalar con cost per result goal / ROAS goal **[OFFICIAL META]** |

## 2. Tipos de escalado y cuándo usar cada uno

| Tipo | Qué es | Cuándo funciona | Riesgo |
|---|---|---|---|
| **Vertical (presupuesto)** | Subir presupuesto de la unidad que funciona | Curva aún plana (CPA marginal < break-even) | Re-learning si el salto es grande; CPA medio sube |
| **Creativo** | Más ángulos/conceptos/personas → nuevos bolsillos de demanda | Siempre; es el motor principal en la era Andromeda/GEM | Producción insuficiente; microvariantes que no abren nada |
| **Inventario nuevo (horizontal real)** | Nuevo país/idioma, producto, oferta, evento, placement con assets nativos | Cuando la curva del mercado actual se aplana | Economía distinta: separar solo si difiere |
| **Oferta** | Bundle, garantía, precio, lead magnet, front-end | Cuando el CTR es bueno pero la CVR limita, o el mercado está saturado | Erosión de margen |
| **Puja** | Pasar a Highest value / ROAS goal / cost per result goal / bid cap para controlar eficiencia marginal | Con volumen (≥50–100 conv/semana) y cuando se necesita proteger margen | Infra-entrega si el objetivo es demasiado ambicioso; CTC: cost goal entregó ~140 % del objetivo de media, ROAS goal ~96,5 %, bid cap ~123 % |
| **Señal** | Value optimization, qualified leads, value rules, audience labels | Cuando el evento actual no distingue valor | Requisitos de datos (CAPI, valores distintos, etapas CRM) |
| **Audiencia por fragmentación** | Más ad sets de intereses/LAL solapados | **Casi nunca** en 2026 | Solapamiento, aprendizaje fragmentado |
| **Duplicación** | Copiar campañas/ad sets ganadores | Solo para cambiar algo no editable (p. ej., estructura legacy) | Overlap; nuevo learning |

## 3. Estimar el coste marginal (método práctico)

1. Toma 4–8 semanas con gasto variable en la misma unidad (sin cambios estructurales grandes).
2. Ajusta conversiones = a × gasto^b (regresión log-log). b típico 0,6–0,8 (estimarlo; varía por cuenta).
3. CPA marginal ≈ CPA medio / b. Con b = 0,7, cada conversión extra cuesta ~1,4× el CPA medio.
4. Óptimo de beneficio: CPA marginal = CPA break-even (contribución por conversión).
5. Sin datos suficientes: escalar por escalones (+20–30 %), medir el CPA incremental del escalón:
   `CPA incremental = Δgasto / Δconversiones` entre la semana base y la escalada (misma estacionalidad).

**Ejemplo**: base 1.000 €/semana → 40 compras (CPA 25 €). Escalón 1.300 €/semana → 49 compras. CPA incremental =
300 / 9 = 33 €. Si el break-even es 36 €, el escalón es rentable pero casi en el límite: el siguiente escalón
probablemente no lo sea → priorizar escalado creativo/inventario antes que más presupuesto. **[STRONG INFERENCE]**

## 4. Protocolo de escalado vertical

1. Verificar condiciones (sección 1) y registrar baseline (semana completa).
2. Subir en la unidad de presupuesto (campaña con campaign budget o ad set), preferentemente al inicio del día.
   Ads Manager a veces indica "puedes subir hasta X sin re-aprendizaje": usarlo como referencia oficial.
3. Escalones de 15–30 % cada 3–7 días si se quiere estabilidad; saltos ≥50–100 % solo con margen amplio y aceptando
   re-learning. **[EMPIRICAL]**
4. Picos temporales (BFCM, lanzamientos): **budget scheduling** (hasta 8× el diario en franjas ≥3 h) en vez de duplicar
   campañas. **[OFFICIAL META]**
5. Evaluar cada escalón con la regla de paciencia (≥7 días, ≥30–50 eventos, ventana madurada) y con el CPA incremental.
6. Revertir solo si el CPA incremental del escalón > break-even en semana completa madurada (no por un día).

## 5. Escalado con pujas (cuentas con volumen)

| Situación | Estrategia | Ajuste inicial |
|---|---|---|
| Arranque / poco volumen | Highest volume (o Highest value si hay valores) | — |
| Volumen alto, necesidad de proteger margen | ROAS goal (ecommerce) o cost per result goal (lead gen) | CPA reciente +10–20 % / ROAS reciente −10–20 %; presupuesto ≥5× objetivo; ajustes de 5–10 % cada ≥7 días **[OFFICIAL META]** |
| Liquidez entre días/horas con control duro | Bid cap con presupuesto "inflado" | Patrón CTC para cuentas grandes **[EMPIRICAL]**; exige vigilancia |
| Ecommerce con márgenes heterogéneos | Value optimization + value rules | ≥50 conversiones/semana; ≥100 eventos con ≥5 valores distintos en 14 días recomendado |

Nota 2027: las value rules sustituyen a los bid multipliers. **[OFFICIAL META]**

## 6. Señales de que el escalado está fallando (semanas completas)

- CPA incremental del escalón > break-even.
- CPM↑ + frecuencia↑ + alcance plano → saturación del bolsillo creativo/audiencia.
- % de clientes nuevos↓ o gasto en "existing/engaged" ↑ (audience segments) → la campaña se come la base.
- MER/contribución total plana pese a más gasto → lo atribuido no es incremental.
- Lead gen: CPL estable pero cualificación/show/close↓.

Respuesta: volver al último escalón rentable, reforzar producción creativa y abrir inventario nuevo (ángulos, ofertas,
países) en lugar de seguir empujando presupuesto.

## 7. Escalado internacional (resumen)

- Separar por país solo si la economía (CPA objetivo, precio, margen, moneda, fees) o el idioma lo exigen; si no,
  multi-país en una campaña con value rules por ubicación. → [11/04](../11-benchmarks-casos-expertos/04-escalado-internacional.md)
- Location fees desde 1-jul-2026 (UK 2 %, ES/FR/IT 3 %, AT/TR 5 %) facturados aparte del presupuesto. **[OFFICIAL META]**
- Localización real (idioma, prueba social local, moneda, envío), no solo traducción automática.

## 8. Errores frecuentes

1. Escalar mirando el ROAS medio de Ads Manager.
2. Duplicar el ad set ganador 5 veces.
3. Subir presupuesto sin lote creativo nuevo.
4. Escalar justo antes de semanas de CPM alto sin ajustar expectativas (2.ª semana de diciembre: coste por compra +39 % en 2025).
5. Confundir escalar ventas atribuidas con escalar negocio (retargeting/existing customers).
6. Revertir un escalón por un día malo.
