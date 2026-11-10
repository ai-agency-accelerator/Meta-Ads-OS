# Principios de razonamiento — cómo piensa un Head of Performance en Meta (2026)

> Última verificación: 2026-10-16 · Autor: agente principal (síntesis de las áreas 01–12) · Ámbito: los principios que
> gobiernan TODAS las decisiones del sistema operativo. Cada principio enlaza a la evidencia detallada.

## TL;DR

1. **Meta optimiza el evento que le das, no tu negocio.** Todo lo demás se deriva de esto. **[OFFICIAL META]** + **[STRONG INFERENCE]**
2. **El sistema de recomendación es el nuevo targeting**; nuestro trabajo es darle *inputs* (oferta, creatividad diversa,
   señales de valor/calidad, presupuesto, restricciones de negocio) y medir la verdad. **[OFFICIAL META]**
3. **Diagnostica de arriba abajo**: negocio → funnel → anuncios → creatividad. Nunca al revés. **[STRONG INFERENCE]**
4. **Decide con la capa más baja de verdad que tengas**: caja/beneficio > incremental > atribuido por Meta. **[EMPIRICAL]**
5. **Volumen de señal por unidad de presupuesto** es la restricción dominante en cuentas pequeñas; la **curva de
   rendimientos decrecientes** y la **incrementalidad** lo son en las grandes. **[OFFICIAL META]** + **[EMPIRICAL]**
6. **Consolidar es el default; separar exige una razón demostrada.** **[OFFICIAL META]**
7. **Con CPA solo se detectan diferencias grandes**: testea saltos grandes (ángulos, conceptos, ofertas). **[STRONG INFERENCE]**
8. **Paciencia estadística**: ninguna decisión de rendimiento con datos inmaduros (≥7 días, ≥30–50 eventos, ventana madurada). **[OFFICIAL META]** + **[STRONG INFERENCE]**
9. **Escala por coste marginal, no medio.** **[STRONG INFERENCE]**
10. **Meta cambia las reglas cada trimestre**: verifica nomenclatura, ventanas y defaults antes de actuar; anota los cambios
    en el change log. **[OFFICIAL META]**

---

## 1. Meta optimiza el evento que le das, no tu negocio

**Mecánica.** En cada subasta Meta calcula un *total value* ≈ puja × tasa de acción estimada (para TU evento de
optimización) + componentes de calidad/valor para el usuario; gana el anuncio de mayor total value, no el que más puja.
Las probabilidades calibradas de clic/conversión sirven para ordenar y para fijar el precio. **[OFFICIAL META]**
→ [01/02-subasta-total-value](../01-subasta-delivery-ml/02-subasta-total-value.md)

**Consecuencias:**
- Si optimizas a *Lead* barato, Meta busca **gente que rellena formularios**, no clientes. Si optimizas a *clic*, busca
  clicadores. El creativo y el evento juntos definen a quién se entrega. **[STRONG INFERENCE]**
  → [02/02-eventos-de-optimizacion](../02-estructura-campanas/02-eventos-de-optimizacion.md)
- La palanca estructural más cara es el **performance goal + evento**, no el número de ad sets. **[OFFICIAL META]**
- Regla: **el evento más cercano al dinero que alcance volumen útil** (~50/semana por ad set para estabilidad).
  Si no hay volumen: consolidar, subir presupuesto, bajar fricción con una oferta de entrada valiosa, o devolver señales
  de calidad (CRM → CAPI) antes que bajar a proxies baratos. Meta recomienda oficialmente LPV/ATC como alternativa cuando
  un ad set no llega a ~50 conversiones/semana; practitioners serios lo desaconsejan porque esos eventos atraen a quien
  hace la acción barata. **[CONTESTED]**: usarlos solo como puente consciente, validando la correlación proxy→venta.
- **Corolario de lead gen**: sin señal de calidad (qualified/conversion leads), Advantage+ amplifica el problema de leads
  basura. **[CONTESTED]** en la magnitud, **[STRONG INFERENCE]** en el mecanismo.

## 2. El sistema de recomendación es el nuevo targeting

**Qué ha pasado (2024–2026).** Andromeda (retrieval), Lattice (unificación de modelos), GEM (foundation model que enseña
a los modelos de ranking), Adaptive Ranking y, desde Q2-2026, Meta Generative Recommender (LLMs en retrieval que
"razonan sobre el contenido del anuncio y las preferencias del usuario"). Meta atribuye a estos modelos +1–15 % de
conversiones por trimestre y +18,9 % de conversiones en el último año (GEM, 13-oct-2026). **[OFFICIAL META]**
→ [01/04-sistemas-ml](../01-subasta-delivery-ml/04-sistemas-ml-andromeda-gem-lattice.md),
[10/03-tendencias](../10-cambios-2025-2026-api-ia-automatizacion/03-tendencias-que-desaparece-que-controla-meta.md)

**Qué significa para nosotros:**
- Las restricciones manuales (intereses, placements, edad) **solo ayudan cuando aportamos información que el sistema no
  tiene**: márgenes, calidad de lead, restricciones legales, brand safety, clientes existentes. Meta está convirtiendo
  las restricciones en **ajustes de valor** (value rules −90 % a +1000 %, audience labels, ROAS goal) y **sugerencias**.
  **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **El contenido del anuncio es input del modelo** (GEM usa una representación del creativo; el Generative Recommender
  razona sobre el contenido). Con targeting amplio, *a quién habla el anuncio* decide en gran parte *a quién se entrega*.
  **[OFFICIAL META]** → [03/01-creative-es-targeting](../03-creatividad/01-creative-es-targeting.md)
- **Creativos demasiado parecidos pueden tratarse como no distintos** y servirse a la misma audiencia. Diversidad real =
  ángulos/personas/formatos distintos, no microvariantes. "Entity ID" y umbrales de similitud del 40–65 % **no** son
  oficiales. **[OFFICIAL META]** / **[HYPOTHESIS]**
- **"Broad siempre gana" es falso como ley**: funciona con volumen, señal limpia y evento alineado con el valor; falla
  con señal escasa, proxies baratos, B2B nicho y alto ticket. **[CONTESTED]** → [12/01-mitos M20](../12-mitos-contradicciones/01-mitos-meta-ads-2026.md)

## 3. Diagnostica de arriba abajo

```
NEGOCIO  (caja, contribución, MER, nCAC, LTV)   ← ¿hay problema?
  └─ FUNNEL  (CVR web, AOV, lead→booking→show→close)   ← ¿dónde se rompe?
       └─ ANUNCIOS  (CPM, CTR, CVR, frecuencia, delivery)   ← ¿qué palanca?
            └─ CREATIVIDAD  (hook, hold, CTR por anuncio, spend share)   ← ¿qué pieza?
```

- Identidad base: **CPA = CPM / (1.000 × CTR × CVR)** → Δln CPA = Δln CPM − Δln CTR − Δln CVR. Descomponer cada cambio
  de CPA en sus tres factores antes de tocar nada. **[STRONG INFERENCE]** (aritmética)
- Lead gen: **coste por venta = CPL / (booking × show × close)**. **[STRONG INFERENCE]**
- Analizar al nivel donde vive el presupuesto (campaña con campaign budget, ad set con presupuesto propio) y en semanas
  completas; desconfiar de breakdowns (hora, placement, edad, anuncio) por el *breakdown effect*. **[OFFICIAL META]**
  → [09/09-taxonomia](../09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md)

## 4. Tres capas de verdad: atribuido → incremental → negocio

| Capa | Pregunta que responde | Fuente | Sesgo conocido |
|---|---|---|---|
| Atribuido (Ads Manager) | ¿Qué conversiones reclama Meta en su ventana? | Ads Manager / API | Depende de ventana y definición (link click desde mar-2026; engage-through 1 d; 1 d view). Puede infra-reportar (Haus: −15 % medio en 7d click) o sobre-reportar (retargeting, Advantage+ +12 pp vs manual). |
| Incremental | ¿Qué ventas CAUSÓ Meta? | Conversion Lift, geo-tests, holdouts, incremental attribution | Requiere volumen y diseño; incremental attribution **[CONTESTED]** (Haus 0,80× → 1,26× vs estándar entre 2025 y 2026). |
| Negocio | ¿Ganamos dinero? | Shopify/Stripe/CRM/contabilidad: MER, contribución, nCAC, cash | No atribuye por canal; necesita triangulación. |

**Regla**: decidir el **presupuesto total** con negocio + incrementalidad; decidir **reparto táctico** (anuncios, ad sets)
con atribución, sabiendo sus sesgos. **[EMPIRICAL]** → [04](../04-tracking-atribucion-medicion/README.md),
[09/08-economia](../09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md)

## 5. La restricción dominante cambia con el tamaño

| Tamaño | Restricción dominante | Riesgo principal | Respuesta |
|---|---|---|---|
| < 300 €/día | Volumen de señal | Fragmentar | 1 campaña, 1 ad set, evento real, creatividad diversa en lotes |
| 300–5.000 €/día | Producción creativa + calidad de señal | Fatiga, leads basura, optimizar a proxy | Sistema de testing, CAPI/CRM, value rules, segments |
| > 5.000 €/día | Rendimientos decrecientes e incrementalidad | Invertir en lo atribuido no incremental | Portfolio por mercado/objetivo/puja, lift/geo/MMM, coste marginal |

**[OFFICIAL META]** + **[EMPIRICAL]** → [02/06-presupuesto-por-niveles](../02-estructura-campanas/06-presupuesto-por-niveles.md)

## 6. Consolidar por defecto

- Cada ad set necesita del orden de **50 × CPA por semana** para estabilizar el aprendizaje; cada ad set adicional que
  persigue el mismo objetivo multiplica el presupuesto necesario. **[OFFICIAL META]** + **[EMPIRICAL]**
- Separar ad sets o campañas solo por: economía distinta (país, producto, margen), objetivo distinto (adquisición vs
  retención), restricción legal (categorías especiales), necesidad de garantizar inversión (test, lanzamiento), o un
  experimento con potencia. **[STRONG INFERENCE]**
- **Duplicar** campañas/ad sets idénticos crea solapamiento de subasta (solo entra tu anuncio de mayor valor) y aprendizaje
  fragmentado; abrir otra ad account no lo evita (Meta identifica al anunciante). **[OFFICIAL META]**

## 7. Testear saltos grandes

- Con 10 conversiones por anuncio, dos anuncios **idénticos** difieren ≥30 % en CPA el ~58 % de las veces; detectar una
  mejora del 20 % exige ~470 conversiones por brazo; una de 2× ~33. **[STRONG INFERENCE]** (Poisson)
- Matar un anuncio con 0 conversiones tras 1× CPA descarta ~37 % de anuncios válidos; a 2× ~13,5 %; a 3× ~5 %.
- Por eso: testear **ángulos, conceptos y ofertas** con CPA; hooks/bodies/copy con métricas intermedias (hook rate, CTR,
  CVR) a condición de que el post-clic no empeore. → [03/05-testing-creativo](../03-creatividad/05-testing-creativo.md)
- Los ganadores son raros (~5 % en Motion, 578k creatividades) y concentran el gasto: **la producción es un juego de
  volumen × diversidad**. **[EMPIRICAL]**

## 8. Paciencia estadística

No evaluar un cambio hasta cumplir **las tres**: ≥7 días completos, ≥30–50 eventos de optimización desde el cambio, y
ventana de atribución madurada para los días evaluados. Excepciones (actuar ya): tracking roto, gasto fuera de límites,
rechazos/riesgo de cuenta, error de configuración, rotura web/stock, ≥3× CPA objetivo sin conversión en un evento
frecuente. **[OFFICIAL META]** + **[STRONG INFERENCE]** → [09/11-cuando-no-tocar](../09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md)

## 9. Coste marginal

Escalar = comprar conversiones marginales más caras (Meta lo documenta). Con conversiones ∝ gasto^b (b≈0,6–0,8), el CPA
marginal ≈ CPA medio / b. El beneficio máximo está donde **CPA marginal = CPA break-even**, con un CPA medio claramente
inferior. Escalar hasta que el CPA *medio* toque el break-even destruye casi todo el beneficio. **[STRONG INFERENCE]**
→ [09/03-escalado](../09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md)

## 10. Meta cambia las reglas: verificar antes de actuar

Entre 2025 y oct-2026 cambiaron: la definición de click-through (solo link clicks, 3-mar-2026), las ventanas view de la
API (12-ene-2026), los placements manuales por ad set (retirándose en Sales/Leads/App (Engagement no; corrección 2026-11-09) desde oct-2026), el
tope de clientes existentes, ASC/AAC, exclusiones de intereses, el precio de WhatsApp, recargos por país (1-jul-2026)…
Antes de aplicar una táctica: comprobar en [00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md) y en el
[changelog](../10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md). Anotar los cambios de plataforma en el
change log de cada cuenta. **[OFFICIAL META]**

## 11. Lo que sigue siendo 100 % nuestro

Oferta y economía unitaria · calidad y volumen de creatividad · calidad de la señal (CAPI, CRM, valor) · arquitectura de
presupuesto por objetivo de negocio · funnel post-clic (landing, ventas, speed to lead) · criterio de medición ·
cumplimiento de políticas y seguridad de activos. **[STRONG INFERENCE]**

## Errores de razonamiento que este sistema evita

- Optimizar campañas aisladas del negocio (CPL bajo con ventas cero).
- Leer el CPA de ayer como definitivo.
- Tratar un benchmark como criterio de rentabilidad.
- Llamar "nuevo creativo" a cambiar tres palabras del hook.
- Fragmentar para "recuperar control".
- Confundir correlación de un dataset de vendor con causalidad.
- Creer que una táctica de 2019 sigue vigente porque "funcionaba".
