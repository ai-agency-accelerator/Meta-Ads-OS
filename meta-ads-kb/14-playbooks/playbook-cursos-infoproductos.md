# Playbook: Cursos e infoproductos (27 € - 3.000 €)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: formaciones online, membresías, programas grupales; venta directa, por webinar/VSL o con llamada. High-ticket (>3.000 €) en `playbook-high-ticket.md`. Base: `05-leadgen-high-ticket-crm/05`, `06`, `07`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **El precio decide el funnel:** <100 € → venta directa (Sales/Purchase) o tripwire; 100-1.000 € → webinar/VSL con compra directa; 1.000-3.000 € → webinar/VSL + llamada corta o aplicación; >3.000 € → playbook high-ticket. **[STRONG INFERENCE]**
- **Cuando hay compra, optimiza a compra (`Purchase`)**, no a lead: es la señal más limpia que existe. Usa lead gen solo cuando la compra requiere un paso intermedio (webinar, llamada). **[STRONG INFERENCE]**
- **Webinars de low-ticket con tráfico frío raramente cuadran sin back-end:** un curso de 497 € vendido en webinar (25% show, 5% compra) solo soporta **4,20 €** por registro (target 2,10 €). **[STRONG INFERENCE]** (archivo 05 §7.2)
- **Curso de 2.000 € con setter+closer es frágil:** BE de 96 € por llamada agendada; con 150 $ por llamada (rango de agencias) pierde dinero. Mejor: VSL/webinar con compra directa + llamada solo para quien la pida. **[STRONG INFERENCE]**
- **Riesgo de cuenta alto en "make money"/oportunidades de negocio:** describe el modelo, nada de ingresos fáciles, mismo tono en anuncio y landing. **[OFFICIAL META]** (S05-071)

---

## 1. Cuándo usar Meta

- Tema con audiencia amplia y dolor/deseo claro (idiomas, oposiciones, fitness, oficios digitales, habilidades profesionales).
- Prueba social y contenido orgánico que sirvan de creatividad.
- Margen alto (coste de entrega bajo) que permita CPA de 30-60% del precio en front-end si hay back-end.
- **No** si el único argumento es "gana dinero" sin producto/método describible (política y reembolsos).

## 2. Funnel según precio

| Precio | Funnel | Evento de optimización | KPI |
|---|---|---|---|
| 7-97 € | Anuncio → página de venta → checkout (+ order bump + upsell) | `Purchase` (valor) | ROAS front-end ≥1 (autoliquidable) + % que asciende |
| 97-497 € | Anuncio → VSL/página larga → checkout; o webinar evergreen | `Purchase`; si <50/semana, `InitiateCheckout` o registro a webinar | CPA vs contribución; ROAS cash 7/30 días |
| 497-1.500 € | Webinar/VSL → compra directa (+ llamada opcional) | Registro → `Purchase`; asistencia vía CAPI | Coste por asistente, % compra |
| 1.500-3.000 € | VSL/webinar → aplicación corta → llamada de 20-30 min (setter-closer) o checkout | Qualified leads / `Schedule` | Coste por agenda vs BE |

## 3. Arquitectura por presupuesto

| Presupuesto/mes | Estructura |
|---|---|
| < 2.000 € | 1 campaña Sales (o Leads si webinar), 1 ad set, 4-6 anuncios; retargeting a través de Advantage+ |
| 2.000-10.000 € | Prospección + testing creativo + retargeting (visitantes de venta, registrantes, viewers de vídeo) |
| 10.000-50.000 € | Evergreen estable + lanzamientos puntuales (playbook webinars) + upsells medidos por cohorte |
| > 50.000 € | Varios productos/ángulos, control de frecuencia, lift tests |

## 4. Creatividades

- El experto enseñando algo útil en 30-60 s (demuestra método y credibilidad).
- Transformación de **habilidad o situación**, no de ingresos ("pasé de no saber X a hacer Y").
- Testimonios en vídeo, capturas de comunidad/resultados de aprendizaje.
- Para retargeting: FAQ, garantía real, contenido del temario, bonus con fecha.

## 5. Ejemplos numéricos

**A) Curso 2.000 € vendido por llamada** (archivo 05): contribución 1.070 €; funnel 40% cualifica, 50% agenda, 60% show, 15% cierre → lead→venta 1,8%.
- BE CPL 19,26 €, target 9,63 €; BE por agenda 96,32 €, target 48,16 €.
- 10.000 € a CPL 15 € → 12 ventas, CPA 833 €, **beneficio 2.843 €** (margen fino; ROAS de cash 2,38 / día 0 1,70).
- Conclusión: con llamadas, este precio exige show y cierre altos; considerar venta directa por VSL/webinar con llamada opcional.

**B) Curso 497 € vendido en webinar** (contribución 336,3 €; 5% de asistentes compra):

| Show | BE coste por registro | Target |
|---|---|---|
| 20% | 3,36 € | 1,68 € |
| 25% | 4,20 € | 2,10 € |
| 35% | 5,88 € | 2,94 € |

Si tus registros cuestan 6-10 €, necesitas upsells, back-end o subir show/conversión; si no, el webinar es una forma cara de vender un curso barato.

**C) Tripwire autoliquidable → servicio/programa de 5.000 €**: 10.000 € a CPA 45 € → 222 compradores (8.017 € netos) → 8% agenda → 17,8 llamadas → 3,1 ventas → **beneficio 5.032 €**; coste neto por llamada 111,6 €. (Archivo 05 §7.3.)

## 6. Métricas y umbrales

| Métrica | Umbral |
|---|---|
| ROAS front-end (cash, 7 días) | ≥ 1,0 en tripwire; ≥ BE de contribución en producto principal |
| Coste por asistente (webinar) | ≤ contribución × % compra de asistentes × (1 − margen objetivo) |
| % reembolso | > 10% → revisar promesa del anuncio/VSL y onboarding |
| Chargebacks | Cualquier tendencia al alza → riesgo con pasarela y cuenta |
| % que asciende al back-end | Medir por cohorte de mes y por campaña |

## 7. Plan de arranque (primeros 30 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 | Elegir funnel por precio; calculadora (contribución, BE CPA y BE por registro si webinar); pixel+CAPI `Purchase` con valor y dedupe; order bump/upsell listos | Compra de prueba registrada con valor correcto |
| 1-2 | 1 campaña Sales a `Purchase` (o registro si webinar), 4-6 anuncios del experto enseñando | CPA ≤ BE en los primeros 20-30 compras, o coste por asistente ≤ máximo |
| 3 | Retargeting (visitantes de venta, viewers de vídeo, registrantes) y nuevas creatividades desde comentarios/preguntas | ROAS cash 7 días ≥ objetivo |
| 4 | Medir upsell y back-end por cohorte; decidir si el front-end puede ser autoliquidable y escalar con el back-end | % ascenso al back-end medido |

## 8. Reglas de decisión rápidas

- Tripwire: escala si el ROAS front-end ≥ 1,0 y el ascenso al back-end se cumple en la cohorte.
- Webinar: decide por coste por asistente, no por registro.
- Reembolsos > 10% o chargebacks al alza → revisa la promesa antes de escalar (riesgo de cuenta y de pasarela).

## 9. Errores frecuentes

- Optimizar a lead cuando puedes optimizar a compra.
- Webinars de 497 € con registros de 10 € y sin back-end.
- Promesas de ingresos o "sin esfuerzo" (rechazos, bloqueos, reembolsos).
- Medir el lanzamiento solo con la ventana de atribución de Meta (las ventas llegan por email/WhatsApp).
- Contadores de urgencia falsos.

## Preguntas abiertas

- Tasas de reembolso y chargeback típicas de infoproductos en España: sin datos públicos fiables.

## Fuentes clave

- `05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md`, `07-webinars-eventos-lanzamientos.md`
- [Webinar Conversion Rate Benchmarks](https://assetacademy.io/funnels/webinars/webinar-conversion-rate-benchmarks/) — 2026-08-02 (S05-045)
- [Unrealistic outcomes](https://transparency.meta.com/policies/ad-standards/deceptive-content/unrealistic-outcomes) (S05-071)
