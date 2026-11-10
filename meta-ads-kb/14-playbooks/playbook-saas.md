# Playbook: SaaS (self-serve, trial, demo, sales-led)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: software B2B/B2C por suscripción captado con Meta. Base: `05-leadgen-high-ticket-crm/05` §7.5 y `10-b2b-saas-local.md`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Optimiza al evento que predice ingresos y tiene volumen:** self-serve → trial **activado** (evento CAPI de primer valor) o `Subscribe`; sales-led → demo celebrada/SQL vía qualified leads. Registro a secas atrae baja activación. **[STRONG INFERENCE]**
- **Decide con LTV:CAC y payback,** no con CPL ni coste por trial. Ejemplo (99 €/mes, 80% margen, 4% churn): con trial→pago 15%, máximo **297 €** por trial (BE LTV), **~99 €** con LTV:CAC 3:1, **~143 €** con payback de 12 meses. **[STRONG INFERENCE]**
- **Benchmarks (vendors, débiles):** trial→pago mediana 12-19%; coste por trial self-serve 15-40 €; Meta frío → demo 0,5-1,5%, retargeting 3-7%; trials retienen peor que demos (65% vs 84% a 12 meses). **[EMPIRICAL]** débil (S05-077)
- **Meta encaja en SaaS para pymes, prosumers y herramientas horizontales**; para enterprise, como retargeting. **[STRONG INFERENCE]**

---

## 1. Modelo → funnel → evento

| Modelo | Funnel en Meta | Evento | KPI |
|---|---|---|---|
| Freemium / trial sin tarjeta | Anuncio → landing → registro → onboarding | Evento de activación (CAPI) cuando ≥50/semana; mientras, `StartTrial`/`CompleteRegistration` | Coste por activado, trial→pago, payback |
| Trial con tarjeta | Anuncio → landing → checkout de trial | `StartTrial` con valor previsto / `Subscribe` | CAC, payback |
| Sales-led (demo) | Anuncio → landing o IF (work email) → demo | Qualified leads (demo celebrada/SQL) o `Schedule` | Coste por demo celebrada, por oportunidad |
| PLG + ventas | Registro → PQL (uso) → ventas | Evento PQL vía CAPI | Coste por PQL, conversión |

## 2. Arquitectura por presupuesto

| Presupuesto/mes | Estructura |
|---|---|
| 2.000-10.000 € | 1 campaña Sales/Leads Advantage+ hacia el evento elegido; lookalike de clientes de pago como sugerencia; 4-8 anuncios (demos de producto, casos) |
| 10.000-50.000 € | + retargeting de visitantes de pricing/docs; testing creativo; test trial vs demo |
| > 50.000 € | Por segmento/caso de uso; value optimization con valor de plan; lift tests |

## 3. Creatividades

- Demostración del producto resolviendo una tarea concreta (pantalla + voz).
- Comparativa con la forma actual de hacerlo (hoja de cálculo, competidor).
- Prueba social por segmento (logos del mismo tipo de empresa).
- Oferta de entrada clara: trial X días sin tarjeta, plantilla, demo de 15 min.

## 4. Métricas y umbrales

| Métrica | Umbral |
|---|---|
| Activación (registro → primer valor) | Definirla y medir por anuncio; caída fuerte = anuncio atrae curiosos |
| Trial → pago | Por cohorte semanal y por campaña |
| CAC | ≤ LTV/3 (criterio habitual) |
| Payback | ≤ 12-18 meses según caja |
| Coste por demo celebrada (sales-led) | Contra BE por agenda de tu calculadora |

## 5. Ejemplos numéricos

**A) Self-serve 99 €/mes, margen bruto 80%, churn mensual 4%** → LTV de contribución 1.980 €.

| Trial → pago | BE coste por trial | LTV:CAC 3 | Payback 12 m |
|---|---|---|---|
| 10% | 198 € | 66 € | 95 € |
| 15% | 297 € | 99 € | 142,6 € |
| 20% | 396 € | 132 € | 190,1 € |

**B) Sales-led, ACV 6.000 €/año**, margen 80%, vida media 3 años, comisión AE 600 € → contribución de vida ~13.800 €; funnel 50% cualifica, 50% agenda demo, 80% asiste, 20% cierra → lead→cliente 4%.
- BE CPL (vida) 552 €; **con solo el primer año** (4.800 € − 600 € = 4.200 €) → BE CPL 168 €. Decide con el escenario que tu caja soporte.
- 10.000 € a CPL 80 € → 125 leads → 31 demos (320 €/demo) → 25 celebradas → **5 clientes**, CAC publicitario 2.000 € (+600 € de comisión = 2.600 €) frente a 400 €/mes de margen bruto (6.000 × 0,8 / 12) → **payback ≈ 6,5 meses**.

## 6. Plan de arranque (primeros 45 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 | Definir evento de activación (primer valor) y enviarlo por CAPI con `em`/`external_id`; LTV y payback objetivo; UTMs con `{{ad.id}}` en registros | Activación de prueba visible en Events Manager |
| 1-2 | 1 campaña a registro/`StartTrial` (o demo), 4-8 anuncios de demostración | Coste por trial y % activación por anuncio |
| 3-4 | Pausar anuncios con activación baja aunque el coste por trial sea bueno; retargeting a pricing/docs | Coste por trial activado ≤ target |
| 5-6 | Si activaciones ≥50/semana, optimizar a activación; cohortes trial→pago | CAC ≤ LTV/3 y payback dentro del objetivo |

## 7. Reglas de decisión rápidas

- Evalúa por coste por **activado** y por cliente de pago de la cohorte, no por registro.
- Si trial→pago de Meta < resto de canales, revisa promesa del anuncio vs onboarding antes de culpar a la audiencia.

## 8. Errores frecuentes

- Optimizar a registros y celebrar un "coste por trial" bajo con activación del 10%.
- Mezclar trials de cohortes distintas al evaluar campañas.
- Ignorar la retención: un canal con más trials pero peor retención puede ser peor.
- Forzar instant forms en un producto que necesita ver la landing/pricing.

## Preguntas abiertas

- Benchmarks fiables de SaaS en Meta con metodología pública (los disponibles son de agencias).

## Fuentes clave

- `05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md` §7.5, `10-b2b-saas-local.md`
- [B2B SaaS Free Trial vs Demo Framework 2026](https://www.growthspreeofficial.com/blogs/b2b-saas-free-trial-vs-demo-decision-framework-2026-conversion-rates-by-acv-product-type) (S05-077)
- [Meta Ads Benchmarks 2026 for B2B SaaS](https://www.growthspreeofficial.com/blogs/meta-ads-benchmarks-2026-b2b-saas-b2b-cpm-cpc-cpl-vertical) (S05-076)
