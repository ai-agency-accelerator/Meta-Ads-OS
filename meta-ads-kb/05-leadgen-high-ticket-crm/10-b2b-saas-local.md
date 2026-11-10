# B2B, SaaS y negocios locales en Meta: cuándo funciona y cómo montarlo

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: B2B (frente a LinkedIn), SaaS (trial, demo, self-serve vs sales-led), negocios locales (geo, lead ads, llamadas, WhatsApp, citas, ingresos offline), agencias y consultores. Los playbooks operativos están en `14-playbooks/`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **B2B en Meta funciona cuando el comprador es identificable por problema/rol más que por empresa** (pymes, autónomos, dueños de negocio, profesionales, decisores en empresas pequeñas y medianas) y cuando el ticket/LTV soporta un filtrado posterior. Para ABM sobre cuentas concretas y cargos en grandes empresas, LinkedIn sigue siendo más preciso. **[STRONG INFERENCE]** con datos de S05-044.
- **Datos B2B 2025 (Metadata, 153 anunciantes, 57,6 M$):** CPL Facebook 145 $, Instagram 138 $, LinkedIn 202 $, Google 524 $; CPC FB 1,95 $ vs LinkedIn 9,39 $; click-to-lead FB 2,6% vs LinkedIn 5,9%; en Meta el retargeting es más barato (120 $ vs 166 $ prospecting); imagen 136 $ vs vídeo 225 $. **No hay datos suficientes para comparar coste por cliente Meta vs LinkedIn.** **[EMPIRICAL]** (S05-044)
- **Coste por SQL: los vendors se contradicen** (LinkedIn 30-50% más barato por SQL según unos; Meta más barato en 7 de 11 cuentas según otro). **[CONTESTED]**: depende de ACV, definición de SQL y de si mides atribución last-click. Decide con tu propio test a nivel de pipeline.
- **SaaS:** self-serve → optimiza a `StartTrial`/registro activado o `Subscribe` con valor; sales-led → demo/`Schedule` o qualified leads con SQL. La métrica de decisión es LTV:CAC y payback, no CPL. En el ejemplo (99 €/mes, 80% margen, 4% churn), un trial que convierte al 15% vale como máximo 297 € (break-even LTV) y ~99 € con LTV:CAC 3:1. **[STRONG INFERENCE]** (archivo 05 §7.5)
- **Negocio local:** desde que Meta eliminó el selector "vive en / estuvo recientemente / está de viaje", el targeting por ubicación incluye a quien pasa por la zona; radio mínimo de ciudad +10 millas; "location expansion" puede estar activada. Filtra con la creatividad ("solo en Valencia ciudad"), con una pregunta de código postal en el formulario y mirando el breakdown geográfico. **[EMPIRICAL]** (S05-081, S05-092)
- **Categorías especiales** (vivienda, empleo, crédito/productos financieros): restricciones de edad, género, lookalikes y radio mínimo (15 millas/25 km en EE. UU./Canadá; 15 km en Europa según fuentes secundarias). Un negocio local de financiación, inmobiliaria o empleo debe planificar con ellas. **[OFFICIAL META]** vía secundarias (S05-080) — detalle en área 08.
- **Agencias y consultores** venden servicios B2B high-ticket: combinan los playbooks B2B y high-ticket; su prueba social (casos con números de clientes) es la creatividad principal y la integración CRM es además un argumento de venta para sus clientes. **[STRONG INFERENCE]**

---

## 1. B2B: Meta vs LinkedIn desde primeros principios

| Factor | Meta | LinkedIn |
|---|---|---|
| Precio del alcance | CPM ~15-18 $ (FB/IG B2B 2025) | CPM ~63 $ |
| Precisión firmográfica | Baja (intereses, sin cargo/empresa fiables) | Alta (empresa, cargo, sector, tamaño) |
| Calidad media del lead | Variable; filtra con work email, preguntas, CAPI CRM | Más alta de partida |
| Volumen | Alto | Limitado y caro |
| Señal de optimización | Muy buena con CAPI CRM (qualified leads) | Más limitada |
| Mejor para | Pymes, autónomos, decisores accesibles, retargeting barato de visitantes y de tráfico de LinkedIn/SEO | ABM, enterprise, cargos específicos |

Datos: Metadata 2026 (S05-044). Lectura: Meta compra atención B2B ~4× más barata por clic pero convierte peor el clic en lead; si tu filtro posterior (preguntas, setter, CAPI CRM) es bueno, la eficiencia puede ganar. **[STRONG INFERENCE]**

### Cuándo SÍ Meta en B2B
- Comprador = dueño/gerente de pyme o profesional (clínicas, despachos, e-commerce, agencias, restaurantes, constructoras).
- Oferta con dolor claro y comunicable en un anuncio (no "plataforma de orquestación de datos").
- Ticket ≥ 2-3 k€ o LTV alto que pague el filtrado.
- Tienes contenido/prueba para retargeting (Meta es barato para retargeting de visitantes B2B: 120 $ vs 166 $ prospecting, S05-044).

### Cuándo NO (o solo como apoyo)
- ABM a 200 cuentas enterprise con comité de compra.
- Cargos muy específicos en grandes empresas.
- No tienes CRM ni proceso de cualificación (el volumen de Meta te ahogará en leads no cualificados).

### Configuración B2B en Meta
- Instant form Higher intent + **Require work email** (Meta, 2025-2026) + preguntas de tamaño de empresa/rol/urgencia; o landing con formulario + calendario.
- Qualified leads con etapa SQL/demo agendada vía CAPI CRM (HubSpot/Salesforce, archivo 04).
- Lookalikes de **clientes** (lista CRM) como sugerencias; exclusión de clientes.
- Creatividad: problema específico del rol, prueba entre pares (logos/casos de su sector), oferta de diagnóstico concreto. Imágenes estáticas pueden superar a vídeo en CPL (S05-044).
- Benchmarks de coste por SQL por ACV (GrowthSpree, sin metodología): 400-1.200 $ (ACV 5-30 k$) hasta 2.500-6.500 $ (150 k$+) (S05-076). **[EMPIRICAL]** débil.

## 2. SaaS: trial, demo, self-serve vs sales-led

| Modelo | Conversión en Meta | Evento de optimización | KPI de decisión |
|---|---|---|---|
| Self-serve con free trial (sin tarjeta) | Landing → registro | `StartTrial` o evento CAPI "trial activado" (p.ej. completó onboarding) cuando haya volumen | Coste por trial activado; trial→pago; LTV:CAC; payback |
| Self-serve con tarjeta / freemium | Landing → registro/pago | `Subscribe`/`Purchase` con valor | CAC, payback |
| Sales-led (demo) | Landing o instant form → demo | `Schedule` / qualified leads (demo celebrada, SQL) | Coste por demo celebrada, por oportunidad, CAC |
| Híbrido (PLG + ventas) | Registro + cualificación (PQL) | Evento PQL vía CAPI | Coste por PQL, conversión a pago |

Benchmarks (vendors, débiles, S05-077): trial→pago mediana 12-19% (sales-assisted vs product-led); coste por trial self-serve 15-40 €; Meta cold → demo 0,5-1,5%, retargeting 3-7%; "no-credit-card trials convierten 60-70% más" (sin metodología). Trials retienen peor que demos según la misma fuente (65% vs 84% a 12 meses) → medir por cohorte de **revenue retenido**, no por registros. **[EMPIRICAL]** débil

Ejemplo (archivo 05 §7.5): LTV de contribución 1.980 € → coste por trial máximo 198/297/396 € para trial→pago de 10/15/20%; con LTV:CAC 3:1, 66/99/132 €; con payback de 12 meses, 95/143/190 €.

**Clave SaaS:** optimizar a "registro" en Meta suele traer registros de baja activación; envía por CAPI un evento de **activación** (primer valor del producto) y optimiza a él cuando llegue a ~50/semana. **[STRONG INFERENCE]**

## 3. Negocios locales

### 3.1 Targeting geográfico (2025-2026)
- El selector "vive en / estuvo recientemente / de viaje" desapareció: solo queda "living in or recently in" (cambio detectado por practicantes; Meta no lo anunció). **[EMPIRICAL]** (S05-092)
- Motivos de entrega fuera de zona: "recently in", radio por defecto (+25 millas en ciudades; mínimo +10 millas), *location expansion* activada por defecto en algunos casos, y engagement orgánico. Recomendación de Loomer: desactivar expansión, reducir radio, revisar el breakdown geográfico, y filtrar con el mensaje ("solo atendemos en…") y con una pregunta de código postal. **[EMPIRICAL]** (S05-081)
- Pin con radio (coordenadas) admite radios menores que una ciudad (1 km según documentación de terceros) → **[HYPOTHESIS]** verificar en Ads Manager.
- Con Advantage+ audience, la ubicación es un **control** (se respeta), la edad máxima/género son sugerencias. **[EMPIRICAL]** (S05-086)

### 3.2 Canal según tipo de negocio local

| Negocio | Canal principal | Evento | Notas |
|---|---|---|---|
| Urgencias (cerrajero, fontanero, grúa) | Calls | Calls | Programar anuncios en horario con alguien al teléfono |
| Citas (clínica, estética, dentista, fisio) | Instant form Higher intent + SMS + booking embebido o WhatsApp | Qualified leads (cita/asistió) | Preguntas prohibidas sobre salud: no preguntar dolencias (S05-016) |
| Presupuestos (reformas, placas solares, climatización) | Instant form con código postal + tipo de proyecto + plazo | Qualified leads (visita técnica) | Fuerte problema de leads basura; SMS + velocidad |
| Restauración / retail | Awareness/Traffic o mensajes; ofertas | Visitas, reservas | Lead ads poco útiles salvo eventos/promos |
| Servicios profesionales (abogados, asesorías) | Instant form o WhatsApp | Qualified leads (consulta) | Categorías especiales si financiero |

### 3.3 Medir ingresos offline
- CRM o agenda del negocio con el lead ID/teléfono → CAPI con etapas (`cita`, `asistió`, `compró`, valor) → qualified leads y medición. La Offline Conversions API ya no existe (mayo 2025); todo va por CAPI. **[OFFICIAL META]** vía secundarias (S05-052)
- Si no hay CRM: hoja compartida + Make/Zapier "Create a Lead Event" (gratis en Make hasta 2028). **[EMPIRICAL]** (S05-030)
- Ejemplo (archivo 05 §7.4): clínica estética, tratamiento de 600 € IVA incl., lead→venta 17,3% → BE CPL 50 € con la primera venta, 110 € con LTV de 2,2 visitas.

### 3.4 Categorías especiales de anuncios
Financiación, crédito, seguros, inmobiliaria, empleo: radio mínimo (15 millas/25 km EE. UU./Canadá; 15 km Europa según fuentes secundarias), edad y género fijos, sin lookalikes; "Financial products and services" sustituyó a "Credit" (14-01-2025 en EE. UU.). **[OFFICIAL META]** vía secundarias (S05-080). Ver área 08 para el alcance en la UE.

## 4. Agencias y consultores (como anunciantes)

- **Oferta:** diagnóstico/auditoría o "sesión estratégica" con resultado tangible; precio o rango visible para filtrar; nicho declarado (agencias generalistas atraen peor lead). **[STRONG INFERENCE]**
- **Funnel:** VSL o caso de estudio → aplicación → llamada (playbook agencias). Volumen bajo → optimizar a aplicación cualificada/`Schedule`; retargeting con casos.
- **Prueba social:** casos con métricas del **cliente** (coste por cita, ventas), no capturas de ingresos de la agencia (riesgo de política y de credibilidad).
- **Ventaja competitiva vendible:** saber montar CAPI CRM + qualified leads + informe hasta cash para sus clientes (la mayoría de pymes no lo tiene).
- **Agencias que gestionan clientes:** usar Business Manager del cliente, datasets del cliente (no cambiar de dataset al cambiar de agencia: reinicia el aprendizaje, S05-002).

## Implicaciones operativas

- B2B: empieza en Meta si tu ICP es pyme/profesional; añade LinkedIn para cuentas objetivo. Mide por SQL y oportunidad, no por lead.
- SaaS: optimiza a activación, no a registro; decide con LTV:CAC y payback.
- Local: controla geografía con creatividad, pregunta de código postal y breakdown; mide la cita y la venta en el CRM y devuélvela a Meta.

## Errores frecuentes

- B2B con instant form More volume sin work email ni preguntas: avalancha de autónomos/estudiantes.
- SaaS optimizando a "Lead" de una newsletter y esperando trials.
- Local con radio por defecto de 40 km y location expansion activada.
- Clínicas preguntando por síntomas en el formulario (prohibido).

## Preguntas abiertas

- Comparativa Meta vs LinkedIn a nivel de coste por cliente con metodología pública (Metadata no pudo publicarla).
- Radio mínimo real por tipo de ubicación en España en 2026 (fuentes secundarias contradictorias).
- Alcance exacto de las categorías especiales en la UE para servicios financieros locales.

## Fuentes clave

- [Meta ads for B2B (2026 B2B Paid Media Benchmark)](https://metadata.io/resources/blog/fb-ad-strategies) — 2026-09-11 — vendor (S05-044)
- [Meta Ads Benchmarks 2026 for B2B SaaS](https://www.growthspreeofficial.com/blogs/meta-ads-benchmarks-2026-b2b-saas-b2b-cpm-cpc-cpl-vertical) — 2026-05-22 — agencia (S05-076)
- [B2B SaaS Free Trial vs Demo Framework 2026](https://www.growthspreeofficial.com/blogs/b2b-saas-free-trial-vs-demo-decision-framework-2026-conversion-rates-by-acv-product-type) — 2026 — agencia (S05-077)
- [4 Reasons Meta Ads Reach People Outside of the Targeted Location](https://www.jonloomer.com/meta-ads-reach-people-outside-of-the-targeted-location/) — 2025-03-31 — practitioner (S05-081)
- [Big change to Meta Ads location targeting](https://www.jonloomer.com/big-change-to-meta-ads-location-targeting/) — practitioner (S05-092)
- [Special Ad Categories: A Guide for Meta Ads](https://www.jonloomer.com/special-ad-categories-meta-ads/) — practitioner (S05-080)
- [Meta Ads B2B Lead Generation Strategy 2026](https://www.involvedigital.com/insights/meta-ads-b2b-lead-generation-strategy) — 2026-09-28 — agencia (S05-075)
