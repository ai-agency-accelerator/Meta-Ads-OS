# Cuenta nueva sin histórico vs cuenta heredada con años de datos: estructura y señales

> Última verificación: 2026-10-16 · Autor: A02 (agente) · Ámbito: cómo cambia la estructura recomendada según el historial de la cuenta (ad account, dataset/pixel, Página, catálogo, audiencias), cómo arrancar sin datos y cómo auditar/limpiar una cuenta heredada tras los cambios 2025-2026. Seguridad/restricciones de cuentas nuevas: área 08. Tracking: área 04.

## TL;DR

- **Lo que sabemos oficialmente sobre "dónde vive el historial"**: Advantage+ audience usa "past conversions, Meta Pixel data, interactions with previous ads"; el sistema "uses learnings from your Page"; y puede identificar varias ad accounts como el mismo anunciante. No hay documentación sobre cuánto aprendizaje vive en la *ad account* vs en el *dataset* vs en la *Página*. **[OFFICIAL META]** (lo citado) + **[HYPOTHESIS]** (el reparto)
- **Cuenta nueva = restricciones operativas reales**: límite de creación de 1 ad account hasta pago confirmado; daily spending limit fijado por Meta que sube con historial y pagos; mayor escrutinio en cuentas/portfolios/Páginas nuevos. No se puede "arrancar a escala" aunque haya presupuesto. **[OFFICIAL META]** ([HC 1026272311098874](https://www.facebook.com/business/help/1026272311098874), [HC 563129151097553](https://www.facebook.com/business/help/563129151097553))
- **Cuenta nueva con dataset/Página existentes ≠ cuenta "en blanco"**: si conectas el dataset y la Página con historial, el sistema tiene señales de conversión y engagement desde el día 1. Reutiliza siempre el dataset de la web (no crees uno nuevo). **[STRONG INFERENCE]**
- **Arranque sin señal (pixel nuevo, sin ventas)**: Meta recomienda, si ningún evento ocurre con frecuencia, "first focus on building up website traffic and a customer base", y elegir un evento más frecuente (ATC, LPV) si se predicen cero conversiones. Practitioners (Loomer) recomiendan empezar directamente con Sales/Leads optimizando a una conversión real (lead si el presupuesto es modesto), 1 campaña/1 ad set, 2 anuncios, 10-20 $/día. **[OFFICIAL META]** vs **[EMPIRICAL]** → **[CONTESTED]** en el matiz del evento.
- **No existe "calentar" una cuenta con engagement/tráfico para que luego venda mejor**: no hay evidencia; el sistema aprende el evento que le pides. **[STRONG INFERENCE]**
- **"Clean account theory" (2026)**: una agencia afirma que 5 cuentas nuevas (1 campaña/1 ad set) superaron >100 % en leads a cuentas legacy de 5+ años. Anecdótico y con un confusor obvio (estructura simple vs compleja). **[HYPOTHESIS]** — antes de abrir cuenta nueva, simplifica y limpia la heredada.
- **Cuenta heredada en 2026 = deuda técnica acumulada por los cambios de Meta**: saved audiences con intereses retirados (dejaron de entregar el 15-ene-2026), exclusiones de detailed targeting eliminadas (31-mar-2025), lookalikes por país (countryless desde 1-sep-2026), placements retirados (Explore, Messenger Stories), ASC/AAC legacy pausados (v26), existing customer budget cap retirado, ventanas de atribución cambiadas (mar 2026), qualified leads sin CAPI (bloqueado desde abril/agosto 2026), bid multipliers → value rules (obligatorio en 2027). **[OFFICIAL META]**
- **El activo más valioso de una cuenta heredada no es la "edad", sino**: dataset con años de eventos bien deduplicados, listas de clientes completas (para exclusiones, segments, value-based LAL, labels), anuncios con prueba social (post IDs), conocimiento de qué conceptos/ofertas funcionan, y límites de gasto/anuncios por Página ya elevados. **[STRONG INFERENCE]**

---

## 1. Qué cambia entre cuenta nueva y heredada

| Dimensión | Cuenta nueva (sin histórico) | Cuenta heredada (años de datos) |
|---|---|---|
| Límite de gasto diario | Bajo, sube con historial/pagos ([HC 563129151097553](https://www.facebook.com/business/help/563129151097553)) | Alto o facturación mensual |
| Límite de anuncios por Página | 250 si la Página nunca superó 100k $/mes | Puede estar en 1.000/5.000/20.000 |
| Señal de conversión | Ninguna o escasa; Advantage+ audience con poco que aprender | Conversiones pasadas, pixel, interacciones: señal para Advantage+ audience |
| Audiencias propias | Inexistentes o pequeñas | Customer lists, compradores 730 d, engaged; base para segments, exclusiones, value rules, LAL |
| Riesgo de restricción | Mayor escrutinio (área 08) | Menor si hay buen historial de políticas |
| Riesgo de "ruido" | Bajo | Eventos obsoletos, pixels duplicados, campañas legacy, audiencias rotas |
| Estructura recomendada | 1 campaña / 1 ad set | Consolidar lo heredado; mantener solo separaciones justificadas |

## 2. Cuenta nueva: plan de arranque

### 2.1 Antes de gastar
1. Portfolio propiedad del negocio; ad account con moneda/zona horaria correctas; método de pago fiable (los pagos fallidos frenan los límites). **[OFFICIAL META]**
2. Dataset único por web: pixel + CAPI (o, como mínimo, pixel; Loomer admite empezar con pixel y llegar a CAPI después); eventos estándar verificados (Purchase/Lead/CompleteRegistration); dominio verificado. **[EMPIRICAL]** + **[OFFICIAL META]**
3. Página + Instagram conectados con algo de contenido (prueba social, identidad). **[STRONG INFERENCE]**
4. Controles de cuenta: países, edad mínima si aplica. Audience segments definidos (aunque al principio estén vacíos). **[OFFICIAL META]**
5. Si existe historial en otro lugar (web con tráfico, CRM con clientes): **sube listas de clientes** (para exclusión/segments/sugerencias) y conecta el dataset existente en vez de crear otro. **[STRONG INFERENCE]**

### 2.2 Primera estructura

```
Campaña Sales (o Leads) — Advantage+ on
└── Ad set único — país(es); controles mínimos; Advantage+ placements;
    goal: conversión real (Purchase / Lead / CompleteRegistration); 7-day click
    └── 2-6 anuncios distintos (vídeo + estático; varios textos)
Presupuesto: el que puedas sostener 4-8 semanas; idealmente ≥7× CPA esperado/día (archivo 06)
```

- **Evento**: [CONTESTED]. Meta sugiere bajar a ATC/LPV si se predicen cero conversiones; Loomer prefiere una conversión real y, con presupuesto modesto, una acción más barata como lead. Propuesta: empezar con la conversión real; si en 2-3 semanas hay <5 conversiones/semana y la tasa de conversión de la web es razonable, usar un evento puente (IC/ATC o un lead magnet) con fecha de revisión; si la web convierte mal, el problema no es el evento. **[STRONG INFERENCE]**
- **Sugerencias de audiencia**: en cuenta nueva, una sugerencia (LAL de lista de clientes, intereses amplios) es inocua y quizá útil; no crear ad sets separados por ellas. **[EMPIRICAL]**
- **Escalado**: el daily spending limit irá subiendo "as you spend up to or near your limits"; planifica subidas graduales. **[OFFICIAL META]**
- **Qué NO hacer**: campañas de engagement "para calentar"; 5 ad sets de intereses; retargeting separado sin audiencia; tests ABO de 10 €/anuncio; abrir varias cuentas "por si acaso" (aumenta riesgo, área 08).

### 2.3 Hitos de transición
| Hito | Cambio de estructura |
|---|---|
| ≥30-50 conversiones/semana sostenidas | Plantear value optimization (si hay dispersión de AOV) o segundo ad set con propósito |
| Base de clientes ≥ varios miles | Audience segments útiles; exclusiones/value rules; CLS |
| ≥200 leads/mes + CRM | Qualified leads con CAPI CRM |
| Gasto estable cerca del límite diario | Pedir/recibir aumento automático; facturación mensual cuando sea elegible |
| Producción ≥10 conceptos/mes | Creative testing tool / lotes |

## 3. Cuenta heredada: auditoría y limpieza (checklist 2026)

### 3.1 Activos y propiedad
- ¿Quién es propietario del portfolio, ad account, dataset, Página, catálogo? ¿Agencia anterior con full access? ¿System users con tokens antiguos? **[OFFICIAL META]** (permisos) — riesgo de seguridad (área 08).
- ¿Cuántas ad accounts, Páginas y datasets hay para el mismo negocio y por qué? Consolidar si no hay razón legal/operativa (archivo 04).

### 3.2 Señal
- Dataset: eventos duplicados, eventos obsoletos, pixels múltiples en la web, deduplicación pixel/CAPI, EMQ (área 04).
- Eventos de optimización por ad set: ¿coinciden con el dinero? ¿Hay campañas Sales optimizando a LPV/clicks? (archivo 02).
- Ventanas de atribución y "conversion count" (cambios de marzo 2026).

### 3.3 Objetos afectados por cambios 2025-2026 **[OFFICIAL META]**
| Elemento heredado | Estado 2026 | Acción |
|---|---|---|
| Ad sets/saved audiences con intereses consolidados | Dejaron de entregar el 15-ene-2026 si no se corrigieron | Revisar avisos; sustituir o eliminar ([HC 458835214668072](https://www.facebook.com/business/help/458835214668072)) |
| Exclusiones de detailed targeting | Eliminadas desde 31-mar-2025; no duplicables | Sustituir por exclusión de custom audiences o controles de cuenta |
| ASC/AAC legacy (API) | No editables desde v25 (todas las versiones 19-may-2026); pausados en v26 | Recrear como Advantage+ sales/app (duplicar en Ads Manager para ECBC) |
| Existing customer budget cap | Retirado | Replicar con 2 ad sets o CLS |
| Lookalikes con país | Countryless desde 1-sep-2026 (API) | Eliminar duplicados por país |
| Placements Instagram Explore Feed, Messenger Stories | Retirados (v26) | Revisar placements manuales |
| Qualified leads sin CAPI | No disponible para nuevas desde abr-2026; existentes afectadas desde ago-2026 | Montar CAPI CRM ([HC 782657799338685](https://www.facebook.com/business/help/782657799338685)) |
| Bid multipliers | Deberán sustituirse por value rules en 2027 | Migrar ([HC 535014515741813](https://www.facebook.com/business/help/535014515741813)) |
| Dynamic creative en Sales/App | No disponible para nuevos ad sets desde jun-2024 | Flexible format / nuevo flujo creativo |
| Campañas duplicadas recientemente | Pueden haberse creado con Advantage+ on | Verificar configuración |

### 3.4 Estructura
- Inventario: nº de campañas activas, ad sets por campaña, eventos/semana por ad set, % en learning/learning limited, overlap (opportunity score: fragmentación).
- Plan de consolidación: agrupar ad sets con mismo goal y economía; mantener separados solo los que resuelven un problema (archivo 05). Hacer los cambios **en lote** y asumir 1-3 semanas de inestabilidad. **[OFFICIAL META]** (edits en lote) + **[STRONG INFERENCE]**
- **No apagar de golpe lo que funciona**: migrar presupuesto progresivamente al nuevo esqueleto y comparar en semanas naturales. **[STRONG INFERENCE]**

### 3.5 Lo que conviene conservar
- Anuncios con mucho engagement (reutilizar post IDs o "carry over engagement" al duplicar). **[OFFICIAL META]**
- Ad sets estables y rentables (aunque estén "learning limited").
- Custom audiences con historia (compradores, leads cualificados), etiquetadas con audience labels.
- Conocimiento: mejores conceptos/ofertas/ángulos históricos (área 03).

## 4. ¿Abrir cuenta nueva o arreglar la heredada?

| Situación | Recomendación | Etiqueta |
|---|---|---|
| Cuenta heredada con estructura caótica pero sin restricciones | Arreglar (consolidar, limpiar señal); el historial de dataset/Página/listas vale más que una cuenta "limpia" | [STRONG INFERENCE] |
| "Rendimiento hundido" sin causa identificada | Diagnóstico (tracking, oferta, creatividad, estacionalidad, cambios de atribución/métricas de 2026) antes que cuenta nueva | [EMPIRICAL] |
| Cuenta con restricciones, deuda de pago, políticas | Ver área 08; una cuenta nueva puede ser necesaria, nunca para eludir políticas | [OFFICIAL META] |
| Cambio de moneda/zona horaria/entidad | Cuenta nueva obligada; reutilizar dataset, Página, catálogo y listas | [STRONG INFERENCE] |
| "Clean account theory" (cuenta nueva rinde más) | No probado; el confusor es la estructura. Si se prueba, hacerlo en paralelo con misma estructura/creatividad/presupuesto y mismo dataset | [HYPOTHESIS] |

## Implicaciones operativas

- En cuentas nuevas, el cuello de botella es **señal y límites**; en heredadas, **ruido y deuda técnica**. La estructura óptima converge (consolidada), pero el camino es distinto.
- Nunca crear un dataset nuevo para una web que ya tiene uno con historial.
- Tras cualquier limpieza grande, comparar por semanas naturales y con métricas de negocio; la atribución de 2026 no es comparable 1:1 con la de 2025 (cambios de marzo 2026; cambios de métricas de impresión/"media view" reportados en julio 2026, área 04).

## Errores frecuentes

1. Abrir una cuenta nueva para "resetear el algoritmo" sin cambiar estructura ni señal.
2. Crear un pixel nuevo con la cuenta nueva.
3. Lanzar una cuenta nueva con 5 campañas y presupuesto alto (choque con spending limit y escrutinio).
4. Heredar una cuenta y aplicar todas las recomendaciones de opportunity score sin criterio (el score mide adopción, no rendimiento).
5. Borrar audiencias antiguas que eran la base de exclusiones/segments.

## Preguntas abiertas

- ¿Cuánto aprendizaje transfiere Meta entre ad accounts que comparten dataset y Página? No documentado; experimento propio recomendado.
- ¿Tienen las cuentas nuevas algún "boost" de exploración (como sugiere la anécdota de 2026) o es solo el efecto de estructuras simples?
- ¿Cómo afecta el cambio de métricas de julio 2026 ("media view") a comparativas históricas? (área 04)

## Fuentes clave

- [Ad account limits](https://www.facebook.com/business/help/1026272311098874) — Meta HC — meta-oficial
- [About daily spending limits set by Meta](https://www.facebook.com/business/help/563129151097553) — Meta HC — meta-oficial
- [Troubleshoot conversion optimization](https://www.facebook.com/business/help/197634954160445) — Meta HC — meta-oficial
- [About Advantage+ audience](https://www.facebook.com/business/help/273363992030035) — Meta HC — meta-oficial
- [Ad limits per Page](https://www.facebook.com/business/help/766697140509126) — Meta HC — meta-oficial
- [Updates to detailed targeting](https://www.facebook.com/business/help/458835214668072) — Meta HC — meta-oficial
- [Marketing API v26.0 changelog](https://developers.facebook.com/documentation/ads-commerce/marketing-api/marketing-api-changelog/version26.0) — Meta Developers — meta-developers
- [A Beginner’s Checklist for Meta Advertising](https://www.jonloomer.com/beginner-checklist-meta-advertising/) — Jon Loomer, 2026-02-09 — practitioner
- [The Clean Account Theory](https://sysloventures.com/the-clean-account-theory-why-new-meta-ad-accounts-may-be-outperforming-legacy-accounts-after-march-2026/) — Syslo Ventures, 2026-07-01 — agencia (anecdótico)
