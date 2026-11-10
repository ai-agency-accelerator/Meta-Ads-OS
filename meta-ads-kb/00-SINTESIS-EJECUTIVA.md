# Síntesis ejecutiva — Meta Ads 2026

> Estado a 16-oct-2026 · Autor: agente principal · Resume la base de conocimiento (áreas 01–15, ~430.000 palabras,
> ~1.340 fuentes registradas). Cada sección enlaza al detalle. Etiquetas según [00-CONVENCIONES](00-CONVENCIONES.md).
> Lo que cambia rápido está en [00-ESTADO-ACTUAL-2026](00-ESTADO-ACTUAL-2026.md).

---

## Cómo funciona Meta Ads realmente

- **Negocio de Meta**: vende impresiones en un inventario con ad load decidido por persona y sesión. En 2026 sube a la vez
  el número de impresiones (+19 % interanual en Q1) y el precio medio por anuncio (+12 % en Q1 y Q2; +20 % en EE. UU. y
  Canadá en Q2). Meta gana más cuando los anuncios convierten más, porque así los anunciantes pujan más. Sus objetivos y
  los nuestros coinciden en el evento optimizado y no necesariamente en el beneficio. **[OFFICIAL META]**
  → [01/01](01-subasta-delivery-ml/01-modelo-negocio-meta.md)
- **La subasta**: gana el mayor **total value ≈ puja × tasa de acción estimada + calidad/valor para el usuario**, no la
  puja más alta. Las probabilidades calibradas de clic y de conversión sirven para ordenar y también para fijar el precio,
  que se parece a un segundo precio (VCG en la literatura, sin documentación actual de Meta). Por eso creatividad,
  oferta, landing y calidad de la señal pesan más que la puja. **[OFFICIAL META]** / **[STRONG INFERENCE]**
  → [01/02](01-subasta-delivery-ml/02-subasta-total-value.md)
- **El pipeline cuando alguien abre Instagram**: (1) *retrieval*: Andromeda y, desde Q2-2026, el Generative Recommender
  con LLMs reducen decenas de millones de anuncios elegibles a miles. (2) *Early ranking* con Lattice. (3) *Late ranking*
  con modelos que destila GEM más Adaptive Ranking a escala LLM. (4) Subasta. (5) Integridad, ad load, pacing y
  frecuencia. (6) Feedback: cada conversión actualiza el modelo y la representación del usuario. GEM no se ejecuta en
  cada subasta: es el modelo que enseña a los demás. **[OFFICIAL META]**
  → [01/03](01-subasta-delivery-ml/03-pipeline-retrieval-ranking-entrega.md), [01/04](01-subasta-delivery-ml/04-sistemas-ml-andromeda-gem-lattice.md)
- **Exploración vs explotación**: el sistema explora con anuncios y segmentos nuevos y explota lo que predice mejor. Hay
  ventaja del incumbente y dependencia de la trayectoria. Las señales rápidas y limpias valen doble: entrenan el modelo y
  refrescan la representación del usuario. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **El presupuesto diario funciona como una media semanal**: hasta 175 % en un día y como máximo 7× a la semana. Cada euro
  extra compra oportunidades marginalmente peores. **[OFFICIAL META]** → [01/06](01-subasta-delivery-ml/06-pacing-presupuesto-frecuencia.md)
- **La historia explica el presente**: 2015–2019 fue la época de la hipersegmentación manual. iOS 14.5/ATT (2021) trajo
  la pérdida de señal. 2022–2023 consolidaron objetivos y Advantage. 2024–2026 trajeron Andromeda, GEM, Advantage+ por
  defecto y la IA generativa. Las tácticas antiguas murieron porque el modelo predice mejor que la segmentación manual,
  pero **"broad siempre gana" es falso**: necesita volumen, señal limpia y un evento alineado con el valor.
  **[CONTESTED]** → [01/08](01-subasta-delivery-ml/08-historia-evolucion-2015-2026.md)

## Qué ha cambiado en 2025-2026

Los diez cambios que más afectan al trabajo diario (cronología completa en [00-ESTADO-ACTUAL-2026 §2](00-ESTADO-ACTUAL-2026.md)):

1. **Advantage+ unificado** (feb-2025 → may-2026): es el estado por defecto de las campañas de Ventas, Leads y App. ASC/AAC
   desaparecen y se elimina el tope de clientes existentes.
2. **El control se mueve a señales y valor**: value rules (2025), audience labels y exclusion-only audiences (2026),
   Customer Lifecycle Strategy (GA el 6-oct-2026).
3. **Fin de las exclusiones de intereses** (mar-2025) y consolidación de intereses (ad sets antiguos sin entrega desde
   15-ene-2026).
4. **Atribución redefinida**: 7d/28d view fuera de la API (12-ene-2026); click-through = solo link clicks y nueva
   engage-through de 1 día (3-mar-2026); incremental attribution como opción (2025); Custom Attribution en beta (2026).
5. **Placements manuales retirados** a nivel de ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09) (ago–oct-2026). Desde oct-2025, hasta
   un 5 % de gasto en placements excluidos.
6. **IA generativa por defecto**: vídeo desde estáticos (GA), reescritura de texto en imágenes (observada desde jul-2026).
   El anunciante responde del contenido generado.
7. **Lead gen**: qualified leads exige CAPI (abr-2026); Advantage+ leads (oct-2025); reserva de citas dentro del instant
   form (jun-2026).
8. **Nuevo inventario**: Threads global (ene-2026) y WhatsApp Status (2025–2026). Messenger deja de ser inventario.
9. **Agentes**: MCP oficial de Meta y Ads CLI (abr–oct-2026), con borradores que requieren aprobación humana. Asistente de
   IA en Ads Manager para todos.
10. **Costes y Europa**: location fees del 2–5 % (1-jul-2026; 3 % en España). Apple rehace el aviso de ATT en la UE con
    iOS 27.2 (re-pregunta al año; obligatorio en DE, FR, IT, PL, RO). Anuncios menos personalizados en la UE
    (ene-2026). Fin de los anuncios políticos y de temas sociales en la UE (oct-2025). WhatsApp cobra por mensaje
    (jul-2025) y también los service messages (oct-2026).

## Qué controla Meta

A quién mostrar (Advantage+ audience), dónde (placements), cuándo y cuánto gastar cada día (pacing), cuánto pujar con
Highest volume/value, qué anuncio del ad set servir, variantes creativas (si las mejoras están ON) y la definición de qué
cuenta como clic o como interacción. **[OFFICIAL META]**
→ [10/03](10-cambios-2025-2026-api-ia-automatizacion/03-tendencias-que-desaparece-que-controla-meta.md)

## Qué debemos controlar nosotros

1. **Economía**: break-even y target por etapa del funnel.
2. **Evento de optimización**: el más cercano al dinero que tenga volumen.
3. **Calidad de la señal**: CAPI, deduplicación, EMQ, CRM, valor.
4. **Oferta.**
5. **Creatividad**: volumen *diverso* y una hipótesis detrás de cada pieza.
6. **Funnel post-clic y ventas**: landing, speed to lead, show rate, cierre.
7. **Arquitectura de presupuesto** según objetivos de negocio.
8. **Restricciones de negocio**: exclusiones de clientes, value rules, legales y de marca.
9. **Medición de verdad**: backend, cohortes, incrementalidad.
10. **Políticas y seguridad** de activos.
11. **Defaults de IA**: qué está activado y quién lo aprobó.

→ [13/01-principios](13-sistema-operativo/01-principios-de-razonamiento.md)

## Arquitectura de campañas

- **Default 2026**: 1 campaña por objetivo de negocio (Sales/Leads/App) con Advantage+ activado, 1 ad set y conceptos
  creativos distintos. Cada ad set necesita del orden de **50 × CPA por semana** para estabilizarse. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Separar solo con razón de negocio**: economía distinta (país, producto, margen), objetivo distinto (adquisición vs
  retención), restricción legal (categorías especiales), gasto garantizado (test o lanzamiento) o experimento con potencia.
- **No separar por audiencias**: separar ad sets por intereses o lookalikes ya no aísla audiencias. **Duplicar** genera
  solapamiento de subasta, y otra ad account no lo evita porque Meta identifica al anunciante. **[OFFICIAL META]**
- **Retargeting separado**: es la excepción. El remarketing ya ocurre dentro de la prospección (10–40 % del gasto según
  Loomer; ~15 % de media en Haus) y su incrementalidad suele ser menor; si se separa, que sea con holdout. **[EMPIRICAL]**
- **Advantage+ frente a manual** **[CONTESTED]**: Meta publica mejoras medias. En Haus (640 tests), Advantage+ ganó a
  manual en iROAS solo en el 42 % de las marcas, con −12 % de iROAS medio y +12 pp de sobre-reporte. Repartir 50/50 fue
  lo peor. Es un buen default operativo, pero hay que medirlo.

→ [02/05](02-estructura-campanas/05-arquitectura-de-campanas.md), [02/08](02-estructura-campanas/08-advantage-plus-ecosistema.md), [02/09](02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md)

## Budget

- **Reglas oficiales**:
  - el gasto puede llegar a 175 % un día y a 7× en la semana (210 % y 8,4× con budget sharing);
  - presupuesto ≥10× el coste del goal; ≥5× el objetivo con cost per result goal;
  - value optimization con presupuesto para ≥50 conversiones/semana;
  - budget scheduling hasta 8× en franjas de ≥3 h. **[OFFICIAL META]**
- **Regla práctica**: unos **7 × CPA al día por ad set**. Si no llegas, consolida y acepta la varianza, o usa un evento más
  barato que siga siendo valioso. **[EMPIRICAL]**
- **Por nivel** (supuestos en [02/06](02-estructura-campanas/06-presupuesto-por-niveles.md),
  [13/09](13-sistema-operativo/09-presupuesto-pequeno-y-grande.md)):
  - **100 €/día**: 1 campaña, 1 ad set, evento real, 3–8 anuncios; el apalancamiento está en oferta, landing y ventas.
  - **500 €/día**: 1 campaña, 1–2 ad sets con propósito, 10–20 anuncios; value optimization si hay ≥50 compras/semana;
    test nativo de creatividades.
  - **5.000 €/día**: 2–5 campañas con razón de negocio, pujas mixtas, testing con graduación, lift trimestral.
  - **50.000 €/día**: portfolio por mercado o entidad, testing industrializado, MMM y lift continuo, decisiones por iROAS
    marginal.

## Bidding

| Estrategia (nombre 2026) | Cuándo | Riesgo |
|---|---|---|
| Highest volume | Arranque, volumen bajo, test creativo nativo | Persigue conversiones baratas |
| Highest value | Ecommerce con valores distintos y ≥50 conv/semana | Requiere CAPI + valor fiable |
| Cost per result goal (antes cost cap) | Proteger CPA con volumen | Entregó de media ~140 % del objetivo (CTC, 253 cuentas); presupuesto ≥5× objetivo |
| ROAS goal (antes min ROAS) | Proteger margen en value optimization | ~96,5 % del objetivo de media (CTC); infra-entrega si es ambicioso |
| Bid cap | Control duro con disciplina (cuentas grandes) | No gasta si el cap es bajo |
| Value rules (−90 % a +1000 %) | Ajustar el valor por segmento con evidencia | Sustituyen a los bid multipliers en 2027 |

Para fijar objetivos: CPA reciente +10–20 % o ROAS reciente −10–20 %; ajustes de 5–10 % con ≥7 días entre cambios;
≥3 semanas antes de escalar. **[OFFICIAL META]** → [09/01](09-bidding-escalado-economia-analitica/01-estrategias-de-puja.md),
[09/02](09-bidding-escalado-economia-analitica/02-value-optimization-y-value-rules.md)

## Audiences

- **Tres instrumentos**: controles duros (ubicación, edad mínima, exclusiones de custom audiences), sugerencias blandas
  (intereses, lookalikes y custom audiences dentro de Advantage+ audience) y **value rules / audience labels** para dar
  precio a cada segmento. **[OFFICIAL META]**
- **Segmentar solo con información que Meta no tiene**: clientes existentes, calidad de lead, márgenes, restricciones
  legales o de marca. Restringir sin esa información suele perjudicar al algoritmo. **[STRONG INFERENCE]**
- **Lookalikes**: se expanden por defecto; desde sep-2026, los creados por API no tienen país. Los intereses funcionan
  sobre todo como sugerencia. El retargeting a listas tiene sentido en retención o en ventanas temporales (eventos,
  lanzamientos).
- **Categorías especiales** (empleo, vivienda, servicios financieros): targeting restringido.

→ [02/07](02-estructura-campanas/07-audiencias-2026.md)

## Creative strategy

- **El anuncio es la segmentación**: el contenido del creativo es input del retrieval y del ranking; a quién habla
  determina a quién se entrega. **[OFFICIAL META]**
- **Diversificar conceptos, no cosmética**: los creativos demasiado parecidos se tratan como no distintos. "Entity ID" y
  los umbrales de similitud no son oficiales. **[OFFICIAL META]** / **[HYPOTHESIS]**
- **Taxonomía**: oferta > ángulo > concepto > formato/ejecución > hook > body > copy/CTA. Cambiar tres palabras del hook
  es una **iteración**, no un creativo nuevo. → [03/02](03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md)
- **Primeros principios**: deseo, dolor, identidad, mecanismo, prueba y objeciones. Niveles de awareness (unaware → most
  aware) y de sofisticación del mercado (de mercado nuevo a mercado saturado) deciden qué abre el anuncio: problema,
  mecanismo nuevo, prueba, identidad u oferta. → [03/03](03-creatividad/03-estrategia-creativa-primeros-principios.md)
- **Formatos**: estáticos y vídeo, no uno u otro (los estáticos con texto lideran el hit rate en Motion 2026). La duración
  no predice resultados; la apertura sí. Para Reels: 9:16, sonido y safe zones. **[EMPIRICAL]**
- **Copy**: el visual manda en la parada de scroll; el copy cualifica y alinea con la landing. Las variaciones de texto
  automáticas exigen control de claims. → [03/08](03-creatividad/08-copy-de-anuncios.md)
- **Landing y CRO**: el clic se abre en el navegador in-app de Instagram/Facebook (sin cookies ni sesiones del navegador
  del sistema; autofill y pago exprés de Meta). Meta usa el *bounce rate* y el *dwell time* de la landing como señales de
  calidad. Con poco tráfico solo se testean cambios grandes. → [03/15](03-creatividad/15-landing-pages-y-cro-trafico-meta.md)
- **Oferta**: el mejor anuncio no arregla una mala oferta. El diagnóstico **ad vs oferta vs landing vs ventas** se hace
  por etapas. → [03/09](03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md)
- **Competencia**: Ad Library muestra alcance y targeting solo en la UE. Que un anuncio lleve tiempo activo es una señal,
  no una prueba de rentabilidad. Sistema para 50–100 anuncios en [03/11](03-creatividad/11-sistema-investigacion-creativa-50-100-anuncios.md).

## Creative testing

- **Estadística**: con CPA solo se detectan diferencias grandes. Detectar un 20 % de mejora exige ~470 conversiones por
  brazo; un 2× exige ~33. **Kill rule** a 2–3× el CPA sin conversión, nunca a 1× (eso descarta un 37 % de anuncios válidos).
- **Estructura**: híbrida.
  - BAU con 10–20 anuncios de conceptos distintos.
  - Gasto garantizado para conceptos nuevos: herramienta nativa *Creative testing* (2–5 variantes, ≤20 % del presupuesto,
    7 días, solo Highest volume) o un ad set o campaña de test.
- **Volumen**: anuncios nuevos cada semana. El hit rate es de ~5 %, así que más volumen diverso da más ganadores.
- **Ganadores**: *provisional* con ≥10–20 conversiones; *confirmado* con ≥30–50 conversiones y ≥7 días con gasto creciente.
- **Fatiga**:
  - es gradual y menos frecuente que el fracaso: el 80 % de los anuncios nunca llega a 100.000 impresiones;
  - Meta la define por coste (≥2× el histórico = *Creative fatigue*), no por frecuencia;
  - el CPM no sube con la edad del creativo.

→ [13/05](13-sistema-operativo/05-framework-testing-creativo.md), [03/05](03-creatividad/05-testing-creativo.md), [03/06](03-creatividad/06-fatiga-creativa.md)

## Tracking

**Dataset** = Pixel + CAPI + eventos offline/CRM/app. Solo los eventos emparejados atribuyen y optimizan, y la señal
determina el aprendizaje. Lo que más mejora la señal:

- `fbc` persistido en el servidor (sobreviviendo a las redirecciones);
- email y teléfono normalizados y hasheados;
- IP/UA reales del usuario;
- `external_id`;
- frescura en tiempo real. **[OFFICIAL META]**

Además:
- **Categorías sensibles** (salud, finanzas): *core setup* y bloqueo de eventos de mitad o final de funnel; custom
  conversions/audiences "flagged" desde sep-2025. No renombrar eventos para esquivarlo (riesgo de circunvención).
- **Privacidad UE**: consentimiento (`fbq('consent', ...)` y filtrar CAPI en servidor). Meta no tiene un "consent mode"
  con modelado. AEM web ya no requiere los 8 eventos (desde 2023). En EE. UU., LDU por estado.

→ [04/01](04-tracking-atribucion-medicion/01-arquitectura-senales-pixel-capi-datasets.md), [04/09](04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md)

## Pixel + CAPI

Pasos de implementación:

1. **Un emisor por evento y fuente.**
2. **Deduplicación** con el mismo `event_id` + `event_name` (ventana de 48 h).
3. **Purchase** desde el sistema que confirma el pago.
4. **Parámetros**: `value`, `currency`, `content_ids` = catálogo, y datos de cliente.
5. **Validación**: Test Events, Payload Helper, Diagnostics y Dataset Quality API.
6. **Umbrales**: EMQ "Good/Great" y ≥6,0 recomendado por Meta (developers); el ≥8 es práctica sin respaldo oficial. Cobertura CAPI ≥75 %, dedup overlap >90 %.

Por plataforma:

| Plataforma | Implementación |
|---|---|
| Shopify | App de Facebook & Instagram, nivel "Maximum" |
| WordPress | Plugin oficial o PixelYourSite |
| GTM | Plantilla oficial del Pixel (abr-2026) y sGTM con tag de CAPI (no comprueba consentimiento y normaliza mal los teléfonos) |
| Custom | Endpoint `/{dataset_id}/events` |

- **CAPI "Meta-enabled" de un clic** (abr-2026): replica lo que envía el Pixel; **no sustituye** a una CAPI desde el backend
  con datos de CRM.

→ [04/02](04-tracking-atribucion-medicion/02-implementacion-pixel-capi-paso-a-paso.md) a [04/07](04-tracking-atribucion-medicion/07-custom-builds-api-directa.md),
[04/16](04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md)

## Attribution

- **Tipos de interacción desde mar-2026**:
  - *click-through* = solo link clicks;
  - *engage-through* (1 día) = likes, shares, saves, comentarios, visitas al perfil y vídeo de ≥5 s;
  - *view-through* (1 día).
- **Ventanas**: click de 1 o 7 días (28d click solo para comparar). 7d/28d view eliminados de la API.
- **Default web**: 7d click + 1d view, con 1d engage-through probablemente activado **[STRONG INFERENCE]**: verificarlo en el ad set. Con click + view + engage, la columna Results suma solo click + view **[OFFICIAL META]**.
- **Las conversiones offsite se reportan por fecha de conversión.**
- **La ventana define el aprendizaje**: una venta fuera de ventana no existe para la optimización.
- **Crédito**: último toque dentro de Meta (clic > vista).
- **Incremental attribution**: optimiza a conversiones incrementales modeladas. **[CONTESTED]**: Haus midió 0,80× → 1,26× de
  iROAS frente a la estándar entre 2025 y 2026.
- **Custom Attribution** (beta 2026): Meta puede optimizar con tu modelo externo.

→ [04/10](04-tracking-atribucion-medicion/10-atribucion-ventanas-y-modelos.md), [04/12](04-tracking-atribucion-medicion/12-attribution-lag.md)

## Measurement

Tres capas de verdad: **atribuido** (Ads Manager) → **incremental** (Conversion Lift, geo-tests, holdouts, incremental
attribution) → **negocio** (backend, MER, contribución, cohortes).

- **Haus** (640 tests): Meta es incremental de media (+19 % de lift). La atribución 7d click infra-reporta un 15 % en DTC,
  y el retargeting/BOF es donde más se infla.
- **Métodos observacionales**: no recuperan el efecto causal (Gordon et al.).
- **MMM**: tiene sentido con gasto multicanal significativo y ≥2 años de datos. Meridian (v2.0, sep-2026) está muy activo;
  Robyn, en mantenimiento bajo.
- **Meta vs GA4/Shopify/CRM/Stripe**: no deben coincidir.
  - Meta reclama interacciones con sus anuncios.
  - GA4 modela sesiones.
  - Shopify cuenta pedidos (last non-direct click, 30 días).
  - CRM y Stripe cuentan dinero real.
  - Cada pregunta tiene su fuente.

→ [04/11](04-tracking-atribucion-medicion/11-meta-vs-ga4-shopify-crm-stripe.md), [04/13](04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md), [04/14](04-tracking-atribucion-medicion/14-mmm-robyn-meridian.md)

## Lead Generation

- **Canales**: instant forms (Higher intent con 3–5 preguntas de opción múltiple y SMS/OTP), formularios web,
  click-to-WhatsApp/Messenger/IG Direct, llamadas y reserva directa.
- **Qué preguntar**: lo que cualifica. No preguntar ingresos, deudas ni salud.
- **Señal de calidad**: *Maximize number of qualified leads* (antes conversion leads).
  - Requiere CAPI desde abr-2026, guardar el lead ID y subir datos al menos una vez al día.
  - La etapa objetivo debe ocurrir en ≤28 días y alcanzarla entre el 1 % y el 40 % de los leads.
  - Hay que enviar ≥2–3 etapas.
  - No hay mínimo oficial de leads desde el 30-oct-2025 y admite formularios web (la cifra de 200 leads/mes de la guía de developers está desfasada).
  - Meta publica −10 % de coste por lead cualificado; −9,5 % en web y −21 % en instant forms.
- **Optimizar** a la etapa más profunda con ~50 eventos/semana: en high-ticket suele ser "cualificado" o "agendado".
- **Speed to lead**: <5 min multiplica el contacto y la cualificación (estudio clásico de 2007, sin réplica reciente). Los
  recordatorios mueven el show rate.
- **CRM**: HubSpot, Salesforce y GoHighLevel integran con distinto grado (la sincronización nativa de HubSpot no envía el
  lead ID). Zapier/Make o CAPI propia como puente.

→ [05](05-leadgen-high-ticket-crm/README.md), [14/playbook-lead-gen](14-playbooks/playbook-lead-gen.md)

## High-Ticket

- **Funnels**: ad → VSL → aplicación → calendario → setter → closer. Alternativas: DM setting por IG/WhatsApp, webinar,
  low-ticket de entrada o challenge.
- **Economía con matemática**: **CPL máx = contribución por venta × P(venta | lead)**. Calculadora:
  `herramientas/economia.py leadgen` (y `prevision` para escenarios de inversión).

| Oferta | Contribución por venta | CPL break-even | CPL target |
|---|---|---|---|
| Coaching 10.000 € | ≈ 4.600 € | 168 € | 84 € |
| Servicio B2B 5.000 € | — | 72 € | 36 € |
| Curso de 2.000 € por llamada | ≈ 1.070 € | 19 € | 10 € (frágil) |

- **Show rate y cierre mueven más que el CPL**: pasar de 50 % a 80 % de show sube un 60 % el CPL pagable.
- **Benchmarks** de show (60–85 %) y cierre (15–40 %): agencias sin metodología. **[EMPIRICAL] débil**

→ [05/06](05-leadgen-high-ticket-crm/06-high-ticket-funnels.md), [05/05](05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md), [14/playbook-high-ticket](14-playbooks/playbook-high-ticket.md)

## Ecommerce

- **Campaña**: Advantage+ sales es una campaña Sales con Advantage+. Clientes nuevos con CLS o exclusiones, y adquisición
  gestionada por **nCAC de la tienda**, no por el segmento "Nuevo" de Meta.
- **Catálogo**: match ≥90 % y product sets por margen; vídeo de catálogo.
- **Revenue no es profit**: **ROAS break-even = (1 + fees) / CM %**, en la misma base que el valor enviado. Con IVA en
  España, el break-even sube.
- **BFCM**: CPM +35–57 % y CPA −20 a −42 %; la 2.ª semana de diciembre, CPA +39 %. Un 25 % de descuento puede hacer perder
  dinero en el primer pedido.
- **Apps**: evento temprano y predictivo, AEM para optimizar, SKAN/backend para auditar.
- **Suscripciones**: el churn fija el CPA permitido.

→ [06](06-ecommerce-apps/README.md), [14/playbook-ecommerce-dtc](14-playbooks/playbook-ecommerce-dtc.md)

## Instagram

- **Producción**: vídeo vertical (9:16 primero, 4:5 derivado). Safe zones: 14 % arriba, 35 % abajo y 6 % laterales. El
  perfil funciona como landing y el DM como conversión.
- **Optimización**: no hay objetivo de seguidores (se optimiza a profile visits; la métrica de follows existe desde
  jul-2025). Click-to-Instagram Direct no optimiza a compras.
- **Comment-to-DM**: 1 private reply por comentario en ≤7 días. Meta está nativizando *Reply to Keywords* (en test).
- **Partnership ads**: −19 % CPA y +13 % CTR según Meta (no son obligatorias). Creator Marketing Hub global desde sep-2026.
  Post IDs para conservar prueba social (vale menos de lo que se cree).
- **Comentarios**: ocultar es mejor que borrar.

→ [07/04](07-instagram-placements-mensajeria/04-instagram-a-fondo.md), [07/06](07-instagram-placements-mensajeria/06-partnership-ads-creadores-ugc-whitelisting.md)

## WhatsApp

- **Optimización**: CTWA optimizando a leads/compras supera a optimizar a conversaciones (−24 % CPL, −10 % coste por
  compra). La optimización a leads **no está disponible en UE/UK**.
- **Precios**:
  - por mensaje desde jul-2025;
  - service messages de pago desde oct-2026;
  - service messages cobrados por mensaje, sin tramos ni franquicia según la doc oficial;
  - ventana gratuita desde anuncios: 72 h según la doc oficial (los BSPs citan 7 días y "1.000 mensajes gratis", sin fuente de Meta) **[CONTESTED]**; **Corrección 2026-11-09**: ya oficial; la página de precios dice hasta 7 días para CTWA y 1.000 service messages gratis por número y mes (S10-118).
  - Business Agent a ~$2 por millón de tokens.
- **Revenue**: guardar `referral` (ad ID, `ctwa_clid`) → etapas del CRM → CAPI for Business Messaging (LeadSubmitted,
  QualifiedLead, Purchase). En Status ads no llega `ctwa_clid`.
- **Métrica**: coste por lead cualificado, por cita y por venta. La palanca nº 1 es la velocidad de respuesta.

→ [07/11](07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md), [07/12](07-instagram-placements-mensajeria/12-whatsapp-business-platform-medicion-revenue.md), [07/14](07-instagram-placements-mensajeria/14-funnels-de-mensajeria.md)

## Scaling

- **Coste marginal**: escalar = comprar conversiones marginales más caras. **CPA marginal ≈ CPA medio / b** (b ≈ 0,6–0,8).
  El óptimo está donde el CPA marginal iguala al break-even.
- **Condiciones para escalar presupuesto**:
  - rentabilidad de negocio sostenida ≥2 semanas;
  - ≥50 conversiones/semana;
  - CPA marginal < break-even;
  - pipeline creativo;
  - tracking verificado;
  - capacidad operativa;
  - ≥3 semanas estables en goal-based.
- **Palancas**: creatividad diversa e inventario nuevo (países, ofertas, productos, eventos) antes que más presupuesto.
  Subidas de 15–30 % cada 3–7 días o saltos mayores aceptando re-learning (no existe una "regla del 20 %" oficial).
  Budget scheduling para picos. **No duplicar.**

→ [13/06](13-sistema-operativo/06-framework-escalado.md)

## Analytics

- **Jerarquía**: BUSINESS (revenue, cash, contribución, MER, nCAC, LTV, payback) → FUNNEL (CVR, AOV; CPL → CPQL → coste por
  cita/show/venta por cohorte) → ADS (CPM, CTR, CPC, CPA, ROAS, frecuencia) → CREATIVE (hook, hold, CTR, spend share).
- **Descomposición**: CPA = CPM / (1.000 × CTR × CVR). Coste por venta = CPL / (booking × show × close).
- **Ruido**: con 30 conversiones, el CPA real está entre 0,7× y 1,5× del observado. Mirar a diario genera ~20 % de falsos
  positivos.
- **Dashboards**: diario para salud, semanal para decisiones, mensual para estrategia. Change log obligatorio.

→ [09/09](09-bidding-escalado-economia-analitica/09-taxonomia-metricas-diagnostico-top-down.md), [09/10](09-bidding-escalado-economia-analitica/10-dashboards-reporting.md), [09/12](09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md)

## Troubleshooting

**Protocolo**:

1. ¿Es real? Datos maduros y fuera de la banda de ruido.
2. ¿Es Meta o el negocio?
3. ¿Es tracking? Events Manager antes que Ads Manager.
4. ¿Qué cambió? Change log propio y de plataforma.
5. Descomponer CPM/CTR/CVR.
6. Una palanca cada vez.

**Árboles por síntoma**: CPA sube, CTR baja con CPA estable, CPM +40 %, leads que no cierran, CTR alto sin ventas, campaña
que no gasta, learning limited, gasto concentrado en un creativo viejo, fatiga vs varianza, "8 ventas vs 3", "20 vs 13 en
Stripe", ROAS bueno con negocio en pérdidas, tracking roto, cuenta restringida y overspend.

→ [13/07](13-sistema-operativo/07-framework-diagnostico.md)

## Policies

- **Base**: los Advertising Standards descansan en los Community Standards. El 9-sep-2026 se consolidaron las
  **Prohibited Commercial Practices** (fraude y estafas); las sanciones por reincidencia pueden extenderse a activos
  asociados.
- **Infoproductos**: no hay una política única; el riesgo combina get-rich-quick, rendimiento pasado, empleo garantizado,
  expectativas irreales, **atributos personales** (situación financiera, salud, edad) y coherencia anuncio-landing.
  **Vender programa y proceso, no resultado económico.**
- **Salud**: 18+ en dieta/cosmética; prohibiciones específicas (pellizcar grasa, curas); restricciones de datos.
- **Finanzas**: categoría especial y verificación obligatoria en España.
- **UE**: sin anuncios SIEP; "economía" y "salud" cuentan como temas sociales.
- **Patrones de copy compliant**: [08/11](08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md).

→ [08/06](08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md), [08/08](08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md)

## Account Health

- **Rechazos**: editar o borrar no limpia la infracción; borrar puede impedir la revisión; cada anuncio tiene una sola
  re-revisión; si la revisión te da la razón, no cuenta.
- **Cuentas deshabilitadas**: 6 meses para pedir la reinstauración.
- **Error terminal = evasión**: cuentas nuevas para repetir, cuentas alquiladas, cloaking, ofuscar.
- **Seguridad**:
  - el cliente es dueño de los activos y la agencia entra como partner;
  - una ad account por cliente;
  - 2FA/passkeys y entre 2 y 10 personas con full control;
  - peer approval.
- **Ataques**: el dominante abusa de funciones reales de Meta (solicitudes de partner, falsas apelaciones con malware,
  robo de sesión).
- **Verificaciones**: verificar empresa, dominio y anunciante antes de escalar.
- **Soporte**: IA en primera línea; humano garantizado solo de pago (Meta Verified / Meta One), con cobertura de cuentas
  publicitarias no documentada.
- **MCP oficial**: sin riesgo de baneo según Meta; reglas por cuenta.

→ [08/01](08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md), [08/03](08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md), [08/09](08-cuenta-politicas-seguridad/09-rechazos-apelaciones-que-no-hacer.md)

## Principales Mitos

| Mito | Veredicto |
|---|---|
| "Nunca toques una campaña en learning" | CONTEXT-DEPENDENT (corrige errores; evita ediciones innecesarias) |
| "50 conversiones/semana o no funciona" | CONTEXT-DEPENDENT (umbral de estabilidad, no de rendimiento) |
| "Learning limited es fatal" | FALSE |
| "Regla del 20 %" | OUTDATED |
| "Duplica los ganadores" | OUTDATED |
| "Siempre broad" / "Advantage+ siempre gana" | CONTEXT-DEPENDENT / FALSE |
| "Las campañas de retargeting son obligatorias" | FALSE |
| "Frecuencia > 3 = fatiga" | FALSE |
| "CTR > X %" | FALSE |
| "Necesitas un píxel nuevo / sazonar el píxel / calentar la cuenta" | UNPROVEN |
| "Meta odia los anuncios duplicados" | FALSE en parte (no pujas contra ti mismo; fragmentas) |
| "Andromeda castiga creativos similares / Entity ID" | CONTEXT-DEPENDENT (redundancia, no castigo; término no oficial) |
| "Meta sobre-reporta todo" | FALSE como universal |
| "EMQ > 8 obligatorio" | UNPROVEN |
| "Los placements manuales rinden mejor" | FALSE en general (y además se retiran) |
| "Los leads de instant form siempre son malos" | FALSE |

66 mitos con fichas: [12/01](12-mitos-contradicciones/01-mitos-meta-ads-2026.md) · contradicciones entre expertos:
[12/02](12-mitos-contradicciones/02-contradicciones-entre-expertos.md) · revisión adversarial de la base (35 hallazgos y 16
discrepancias resueltas): [12/05](12-mitos-contradicciones/05-revision-adversarial-kb.md).

## Benchmarks

- **No hay un benchmark único**: el CPM mediano va de ~9 $ (global) a ~15 $ (ecommerce) y ~19 $ (cuentas grandes de EE. UU.).
  El rango central del CPA abarca ~10×. El ROAS mediano de ecommerce (1,88) está por debajo del break-even de muchas marcas.
- **Inflación oficial**: precio por anuncio +12 % (+20 % EE. UU./Canadá, +21 % resto del mundo, +1 % APAC en Q2-2026).
- **Para qué sirven**: un benchmark **nunca** dice si eres rentable. Sirve para situar el orden de magnitud y detectar
  anomalías; las decisiones se toman con la economía propia.

- **España y LatAm**: no hay benchmark público fiable con metodología. Los recargos fiscales pesan más que la subasta
  (España +3 % de location fee; Argentina hasta ~53 % pagando con tarjeta). En la UE no se puede optimizar CTWA a leads; en
  LatAm sí. → [11/10](11-benchmarks-casos-expertos/10-espana-latam.md)

→ [11/01](11-benchmarks-casos-expertos/01-benchmarks-2025-2026.md), [11/02](11-benchmarks-casos-expertos/02-como-usar-benchmarks.md), [11/03](11-benchmarks-casos-expertos/03-geografias-costes-comportamiento.md)

## Playbooks

Playbooks separados por modelo en [14-playbooks](14-playbooks/):

- lead gen;
- high-ticket;
- cursos/infoproductos;
- webinars/eventos/lanzamientos;
- negocio local;
- B2B;
- SaaS;
- agencias/consultores;
- ecommerce/DTC;
- productos de consumo;
- suscripciones;
- apps.

Cada uno incluye: cuándo usar Meta, arquitectura por presupuesto, evento, creatividades, funnel, métricas y umbrales,
errores y un ejemplo numérico.

## Framework De Auditoría

1. Negocio y economía.
2. Seguridad y riesgo (P0).
3. Señal/tracking (la mitad de las auditorías se resuelve aquí).
4. Medición.
5. Estructura.
6. Presupuesto y pujas.
7. Audiencias.
8. Creatividad.
9. Funnel y ventas.
10. Políticas.

Cada hallazgo lleva evidencia, severidad P0–P3, impacto y acción. → [13/02](13-sistema-operativo/02-framework-auditoria.md)

## Framework De Lanzamiento

Objetivo → **economía (gate)** → **tracking (gate)** → oferta y funnel (gate) → investigación creativa → producción (gate) →
arquitectura (1 campaña, 1 ad set, Advantage+, evento real) → presupuesto (≈7 × CPA/día) → lanzamiento con revisión
cruzada → medición por fases (semana 1, semana 2–4, mes 2, mes 3+). → [13/03](13-sistema-operativo/03-framework-lanzamiento.md)

## Framework De Optimización

- **Diario**: salud (tracking, gasto, entrega, rechazos, leads sin atender), sin decisiones de rendimiento.
- **Semanal**: en una ventana fija, de arriba abajo (negocio → funnel → anuncios → creatividad), 1–3 palancas, change log.
- **Mensual**: economía, presupuesto total, incrementalidad, roadmap creativo y cambios de Meta.
- **Regla de paciencia**: ≥7 días, ≥30–50 eventos y ventana madurada.

→ [13/04](13-sistema-operativo/04-operativa-diaria-semanal-mensual.md)

## Framework De Escalado

Siete condiciones → tipo de escalado (creativo/inventario/oferta/señal antes que presupuesto) → CPA incremental por
escalón → señales de fallo (CPA marginal > break-even, CPM y frecuencia ↑ con alcance plano, % nuevos ↓, MER plano). →
[13/06](13-sistema-operativo/06-framework-escalado.md)

## Framework De Diagnóstico

Protocolo de 6 pasos más 15 árboles de decisión por síntoma. → [13/07](13-sistema-operativo/07-framework-diagnostico.md).
Casos de validación A–J: [15](15-escenarios-validacion/README.md).

## Fuentes Fundamentales

Ledger maestro: [fuentes/00-SOURCE-LEDGER-MAESTRO](fuentes/00-SOURCE-LEDGER-MAESTRO.md). Las imprescindibles:

- **Meta Help Center**: learning phase, presupuestos, performance goals, fluctuaciones, auction overlap, value optimization.
- **Meta Business News**: click attribution 2026, AI Connectors, Ad Week 2026.
- **API**: changelog de v26 y out-of-cycle changes 2026.
- **Meta Engineering**: Andromeda, GEM 2025/2026, Adaptive Ranking.
- **Earnings**: transcripciones de Q1–Q2 2026.
- **Transparency Center**: Advertising Standards.
- **Evidencia externa**: Haus (640 tests), CTC 2026, Jon Loomer, Motion 2026.

## Preguntas Que Siguen Sin Tener Una Respuesta Clara

1. **Forma exacta del total value** (pesos de calidad, precios de reserva) y política de exploración de anuncios nuevos.
2. **¿Cuánto aprendizaje vive en la ad account, el dataset o la Página?** No está documentado.
3. **Umbrales reales de learning en 2026** por tipo de campaña (rumores de 10/15/25 sin fuente) y si añadir un anuncio
   reinicia el learning.
4. **¿Cómo mide Meta la similitud creativa?** (Creative diversity "estimada y en desarrollo") ¿Y cuánto pesan imagen,
   audio y texto en la representación del anuncio?
5. **¿Los resultados de Haus** (manual > Advantage+ en el 58 % de las marcas) se mantienen con el Advantage+ de 2026 (CLS,
   value rules, Generative Recommender)?
6. **Metodología de incremental attribution** y por qué cambió su rendimiento relativo entre 2025 y 2026.
7. **Impacto real de los anuncios menos personalizados en la UE** (Meta no publica adopción).
8. **Curvas de rendimientos decrecientes por vertical** y efecto de las subidas de presupuesto del 10/20/50/100 % (no hay
   datos controlados públicos).
9. **Benchmarks fiables** de show y cierre en high-ticket, y de conversación → venta en WhatsApp, sobre todo en España y
   LatAm.
10. **Efecto medido de las mejoras de IA de Meta** (texto reescrito, vídeo generado, Muse Image) y de Ads Creative Studio,
    Brand Memory y Business Agent: solo hay claims de Meta.
11. **Detalle de las condiciones del 30-oct-2026** (tests sin aviso, responsabilidad sobre contenido de IA). · **2026-11-09**: suspendidas antes de entrar en vigor; siguen las del 22-ago-2025 (S10-113)
12. **Si la retirada de placements llegará a Awareness/Traffic** y a las exclusiones de plataforma, dispositivo y SO.
13. **Anomalías de entrega de ~29-jul y ~17-sep-2026** (CPM −30 % con peor CTR y menos compras) sin explicación oficial.
14. **Requisito concreto** de la verificación de anunciantes financieros en España (CNMV/Banco de España).
