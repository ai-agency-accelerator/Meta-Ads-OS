# Plantillas operativas

> Última verificación: 2026-10-16 · Autor: agente principal · Plantillas para copiar en cada cuenta (Sheets/Notion/markdown).

## 1. Ficha de cuenta (una por cliente)

```markdown
# Cuenta: <nombre>  ·  Última actualización: AAAA-MM-DD
## Negocio
- Modelo: ecommerce / lead gen / high-ticket / local / SaaS / app / infoproducto
- Oferta principal y precio (sin IVA):
- Mercados e idiomas:
- Objetivo del trimestre (resultado de negocio):
- Capacidad operativa (stock, agenda comercial, plazas):
## Economía (ver calculadora)
- Contribución por venta: ____ € → CPA break-even: ____ € · target: ____ €
- Ecommerce: ROAS break-even (base que ve Meta, con/sin IVA, + fee por país): ____
- Lead gen: CPL BE/target ____/____ · coste por cita BE/target ____/____ · por show ____/____
- LTV por cohorte (contribución) y payback máximo aceptado:
## Señal
- Dataset ID · CAPI (método) · dedup ok (S/N) · EMQ evento principal · eventos CRM devueltos
- Ventana de atribución usada para decidir (verificada en el ad set; el default no está documentado): 7d click + 1d view ± 1d engage-through / otra
## Arquitectura vigente
- Campañas (objetivo, evento, puja, presupuesto, razón de existir):
## Riesgos
- Categoría especial/sensible · verificaciones · admins (≥2) · método de pago de respaldo
## Política de IA creativa
- Enhancements ON/OFF (y quién lo aprobó):
```

## 2. Change log (obligatorio)

| Fecha/hora | Quién | Nivel (cuenta/campaña/ad set/anuncio) | Objeto | Cambio (de → a) | Motivo / hipótesis | Métrica de éxito | Fecha de evaluación | Resultado |
|---|---|---|---|---|---|---|---|---|

Incluir también **cambios de plataforma** (p. ej. "2026-03-03 Meta: click-through = solo link clicks"), incidencias de
web/stock/precios y promociones.

## 3. Brief creativo

```markdown
## Brief <AAAAMMDD>_<ángulo>_<concepto>
- Nivel de test: oferta / ángulo / concepto / ejecución / hook
- Hipótesis: "Para <persona> con <nivel de awareness>, el ángulo <X> dramatizado como <concepto> producirá <métrica> porque <razón>"
- Persona y awareness:
- Ángulo (razón de compra):
- Concepto (idea que lo dramatiza):
- Formato(s): UGC / estático / demo / founder / testimonial / carrusel / podcast clip
- Hooks (2–3) — primeros 2–3 s / primera línea:
- Body: mecanismo · prueba · objeciones resueltas
- Oferta y CTA:
- Prueba disponible (testimonios con permiso, datos, demos):
- Compliance: claims permitidos / prohibidos (ver 08/11)
- Specs: 9:16 (safe zones 14 % arriba / 35 % abajo / 6 % laterales) + 4:5 · subtítulos · duración
- Landing / message match:
- Criterio de éxito y kill rule:
```

## 4. Ficha de test (creativo o de media)

| Campo | Valor |
|---|---|
| Pregunta | |
| Variable única | |
| Estructura (BAU / test nativo / ad set de test / A/B test) | |
| Métrica principal y ventana | |
| Diferencia mínima que nos importa | |
| Conversiones necesarias por brazo (tabla de potencia) | |
| Presupuesto y duración | |
| Reglas de parada | |
| Resultado | |
| Decisión y aprendizaje | |

## 5. Informe semanal (cliente o interno)

```markdown
# Semana <ISO> · <cuenta>
## 1. Negocio (lo primero)
Revenue neto · cash · contribución tras marketing · MER · nCAC / coste por venta (cohorte) — vs target y vs semana anterior
## 2. Qué ha pasado (3 bullets, con causa)
## 3. Funnel
Ecommerce: LPV rate · ATC · checkout · CVR · AOV · % nuevos
Lead gen (cohortes): CPL · % cualificado · coste por cita · show · close · cash
## 4. Meta
Gasto · CPA/ROAS (7d click y 1d click) · CPM · CTR link · CVR · frecuencia · segments (nuevos/engaged/existentes)
Descomposición del cambio de CPA: CPM __ % · CTR __ % · CVR __ %
## 5. Creatividad
Conceptos lanzados · con gasto relevante · winners provisionales/confirmados · aprendizajes por ángulo
## 6. Decisiones tomadas (del change log) y próxima evaluación
## 7. Próxima semana: lote creativo, tests, riesgos
## Notas de medición
Días aún no madurados · cambios de plataforma que afectan a la comparación
```

## 6. Registro de aprendizajes creativos

| Fecha | Ángulo | Persona | Concepto | Formato | Hook | Gasto | Conv | CPA | Hook rate | Hold | CTR | CVR | Veredicto | Por qué | Siguiente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 7. Cohorte de leads (lead gen / high-ticket)

| Semana de creación | Campaña | Anuncio | Leads | Cualificados | Citas | Shows | Ventas | Cash 30d | Cash 60d | Cash 90d | Gasto | CPL | Coste por venta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 8. Nomenclatura

- Campaña: `<mercado>_<objetivo>_<propósito>_<puja>` → `ES_SALES_ADQ_HV`
- Ad set: `<audiencia/estrategia>_<evento>` → `BROAD-A+_PURCHASE`
- Anuncio: `<AAAAMMDD>_<angulo>_<concepto>_<formato>_<hook>` → `20261020_dolor-cervical_split-manana_ugc_h2`, con
  `<hook>` = `h<n>` y un sufijo opcional `-c<n>` para el cuerpo (`_h2-c1`). Lo valida `herramientas/nomenclatura.py`
  (contrato §7).
- UTMs (plantilla única): `utm_source=facebook&utm_medium=paid_social&utm_campaign={{campaign.name}}&utm_term={{adset.name}}&utm_content={{ad.name}}&campaign_id={{campaign.id}}&adset_id={{adset.id}}&ad_id={{ad.id}}&placement={{placement}}&site={{site_source_name}}`
  - Los **IDs** son la clave para unir con CRM/backend (los nombres cambian); los nombres, para leer informes.
  - Mantener `utm_source`/`utm_medium` coherentes con la agrupación de canales de GA4 en toda la cuenta (ver también [05/09](../05-leadgen-high-ticket-crm/09-sales-feedback-loop.md)).
  - **Con GoHighLevel como CRM**, `utm_source=fb_ad` en lugar de `facebook` (el resto igual). La documentación de
    HighLevel dice que clasifica como *Paid Social* el tráfico con `fb_ad` en `utm_source`; es un artículo de 2022 que
    no hemos verificado con datos **[HYPOTHESIS]**. `herramientas/meta_ads.py` ya pone `fb_ad` cuando la ficha dice
    `crm.tipo: ghl`. Paso a paso en [la guía de GoHighLevel y Meta](../../docs/guias/ghl-meta.md#la-plantilla-de-utms).
  - **Si además usas GA4**: su agrupación de canales por defecto no reconoce `fb_ad` como red social, así que ese
    tráfico (con `utm_medium=paid_social`) cae en «Paid Other». Crea un grupo de canales personalizado (Administrar →
    Visualización de datos → Grupos de canales) con un canal «Paid Social» cuya regla sea *Fuente coincide exactamente
    con `fb_ad`* **y** *Medio coincide exactamente con `paid_social`*, colócalo por encima de «Paid Other» (las reglas se
    evalúan en orden) y usa ese grupo en los informes **[STRONG INFERENCE]**.
