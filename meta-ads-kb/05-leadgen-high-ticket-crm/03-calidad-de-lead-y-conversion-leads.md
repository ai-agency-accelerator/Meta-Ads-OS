# Calidad de lead y señales hacia Meta: qualified leads (antes conversion leads), Conversions API for CRM y qué evento optimizar

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A05 (agente) · Ámbito: optimización por calidad de lead en Meta (instant forms, web, mensajería), requisitos, configuración, elección del evento según volumen. Fuentes en `fuentes/ledger-05-leadgen-high-ticket-crm.md` (IDs S05-xxx).

## TL;DR

- **El objetivo de rendimiento se llama ahora "Maximize number of qualified leads"** (antes "conversion leads"; Meta y los partners siguen usando ambos nombres). Optimiza hacia personas con más probabilidad de *convertir después* de dejar sus datos, usando las etapas que tu CRM devuelve a Meta. **[OFFICIAL META]** (S05-007, S05-008)
- **Cambio crítico 2026: desde abril de 2026 ya no se puede crear una campaña nueva con qualified leads sin integración de Conversions API; las campañas existentes se ven afectadas desde agosto de 2026.** Si no devuelves etapas del CRM, en la práctica solo te queda "Maximize number of leads". **[OFFICIAL META]** (S05-007)
- **Requisitos documentados** para la integración CAPI for CRM: leads de instant forms con el *Meta Lead ID* guardado, subida al menos diaria, la etapa objetivo ocurre en ≤28 días desde el lead, y esa etapa convierte entre el 1% y el 40% de los leads; enviar ≥2 etapas (incluido el lead bruto), mejor ≥3; cobertura de leads ≥60%. **[OFFICIAL META]** (S05-001, S05-002)
- **El "mínimo de 200 leads/mes" está en disputa:** la guía de desarrolladores lo sigue listando, pero el anuncio oficial de Meta del 30-10-2025 dice que "se eliminó el requisito mínimo de volumen mensual de leads" y que ya se puede optimizar a un único evento (venta o booking) sin mapear todo el funnel. **Resolución (revisión A12, 16-oct-2026):** prevalece el anuncio oficial más reciente (30-oct-2025): ya no es requisito; la guía de developers no se ha actualizado (sigue diciendo también "solo instant forms", contradicha por el Help Center). Con pocos eventos el sistema aprende mal igualmente. (S05-001, S05-005)
- **Ahorros declarados por Meta** (autorreportados, no auditados): −21% coste por lead de calidad con instant forms + CAPI CRM + qualified leads frente a "maximize leads"; −9,5% en formularios web; −19% (oct-2025). **[OFFICIAL META]** como dato publicado; **[HYPOTHESIS]** que se reproduzca en tu cuenta. (S05-005, S05-007)
- **Qualified leads ya funciona también con formularios web** (Meta lo documenta) y en octubre de 2026 se está desplegando **Sequenced Events**: Meta solo atribuye la conversión si ocurren dos eventos en orden (p.ej. Lead → Schedule). Sin documentación oficial todavía; en algunas cuentas aparece gris con "requiere integración CRM". **[OFFICIAL META]** (web) / **[EMPIRICAL]** (sequenced events, reportes de practicantes) (S05-007, S05-033, S05-034, S05-035)
- **Regla de elección del evento:** optimiza por la etapa más profunda que (a) ocurra en ≤28 días, (b) tenga ≥~50 eventos/semana a nivel de ad set o campaña, y (c) correlacione con dinero. En high-ticket casi nunca es la venta: suele ser "cualificado", "llamada agendada" o "show". **[STRONG INFERENCE]** basada en S05-001 + guía general de learning phase de Meta.
- **Mensajería:** existe "Maximize number of leads through messaging" (despliegue gradual) y la CAPI de business messaging admite eventos `LeadSubmitted` y `QualifiedLead`, pero la *optimización* por eventos downstream vía CAPI solo está documentada para compras en click-to-Messenger y click-to-WhatsApp; Instagram Direct no es optimizable así. **[OFFICIAL META]** (S05-020, S05-025)
- **Europa:** varias funciones de mensajería (métricas, ciertos tipos de campaña, detección automática de eventos en WhatsApp) no están disponibles para anuncios entregados a/desde la UE, Reino Unido o Japón. Comprueba disponibilidad en tu cuenta antes de diseñar un funnel que dependa de ellas. **[OFFICIAL META]** (S05-021, S05-026)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **Dos contradicciones entre fuentes oficiales [CONTESTED]**: (1) la guía de developers de *conversion leads* (actualizada el 2026-10-27) sigue pidiendo **≥200 leads/mes**, mientras el anuncio del 30-oct-2025 eliminó el mínimo; (2) el Help Center dice que *qualified leads* funciona con formularios web e instant forms (−9,5 % y −21 %), y developers y la especificación del payload, que solo con instant forms. Planifica con 200 leads/mes y prueba con menos si la interfaz lo deja.
> - Confirmado en developers: lead ID de 15–17 dígitos (o click ID, teléfono o email), subida ≥1/día, etapa ≤28 días, 1–40 % de conversión, enviar todas las etapas a medida que cambian, 3–4 semanas hasta obtener valor. Las "≥2–3 etapas" y la "cobertura ≥60 %" no aparecen en ninguna fuente oficial. **[HYPOTHESIS]**
> - Desde abr-2026 no se crean campañas nuevas sin CAPI; las existentes, afectadas desde ago-2026. *Maximize value of conversions* en Leads: ≥5 valores únicos, >100 conversiones en 14 días, 3 semanas de prueba. **[OFFICIAL META]**
> - **Sequenced Events** (dos eventos en orden dentro de *Maximize number of qualified leads* con ubicación web; parece exigir eventos por CAPI y ~30 eventos en 7 días; solo atribución estándar): solo Loomer. **[EMPIRICAL]**/**[HYPOTHESIS]**
> - Fuentes: S10-135, S10-136, S10-143 (verificación oficial de lead ads del mismo día) en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Por qué "lead" es una señal pobre (primeros principios)

Meta optimiza hacia el evento que le pides. Si el evento es "envió el formulario", el sistema encuentra a la gente con mayor probabilidad de enviar formularios: personas que rellenan todo, que pulsan rápido con autofill, que están en placements donde el clic accidental es frecuente, y en el peor caso bots o "granjas" de formularios. Nada en esa señal distingue a quien tiene dinero, urgencia y encaje del que no.

Por eso en lead gen el KPI de plataforma (CPL) y el KPI de negocio (coste por venta o por cash cobrado) pueden moverse en direcciones opuestas: Meta te "premia" con un CPL más bajo mientras te manda gente que nunca coge el teléfono. La única forma estructural de arreglarlo es **cambiar la señal**: decirle a Meta qué leads acabaron siendo buenos. Esa es la función de qualified leads + Conversions API for CRM. Todo lo demás (preguntas, verificación SMS, higher intent) son filtros que ayudan pero no cambian el objetivo del algoritmo.

## 2. Qué es exactamente "Maximize number of qualified leads"

Según Meta (S05-007), en un Leads campaign, nivel ad set, sección *Conversion*, existen hoy estos *performance goals*:

| Performance goal | Qué optimiza | Cuándo usarlo |
|---|---|---|
| Maximize number of leads | Personas con más probabilidad de dejar sus datos | Arranque, volumen, cuando no hay CRM integrado |
| Maximize number of qualified leads | Personas con más probabilidad de **convertir después** de dejar sus datos (según etapas del CRM) | Siempre que tengas integración CAPI CRM y volumen suficiente en la etapa objetivo |
| Maximize number of leads through messaging | Personas con probabilidad de convertirse en lead por mensajería | Funnels en Messenger/IG/WhatsApp (despliegue gradual) |
| Maximize value of conversions | Leads de alto valor según el valor que envías | Cuando los leads tienen valores diferenciados y hay mucho volumen |

Notas oficiales clave:
- **Abril 2026:** qualified leads deja de estar disponible para creación de nuevas campañas sin integración CAPI; campañas existentes afectadas desde agosto 2026. **[OFFICIAL META]**
- Se puede usar con **website forms e instant forms**. **[OFFICIAL META]**
- Existe un "signal source" (fuente de señal). Con instant forms, si eliges **"Meta source"** como fuente, Meta recomienda escoger **"Leads with WhatsApp conversations"** como evento de follow-up: el anuncio usa señales de conversación de WhatsApp para llegar a gente que además chatea, no solo que rellena. **[OFFICIAL META]** (S05-007, S05-014). Es la única vía documentada de "calidad" sin CRM, y la misma página dice que sin integración CAPI ya no se puede crear qualified leads: la convivencia de ambas frases no está aclarada → **[CONTESTED]**, verifícalo en tu Ads Manager.
- En la combinación **Website and instant forms** (campaña híbrida), el único objetivo disponible es Maximize number of leads con el evento Lead; para qualified leads hay que elegir web o instant forms por separado. **[OFFICIAL META]** (help 1438863853809586)

### Fuentes de datos (data sources)

En abril de 2025 Jon Loomer vio brevemente un selector de "Data Source" para conversion leads con opciones **CRM, Calls, Messages, None**, que luego desapareció de su cuenta (S05-031). Es coherente con lo que hoy documenta Meta (CRM, Meta source / WhatsApp), pero **la opción "Calls" no está documentada oficialmente a fecha 2026-10-15** → **[HYPOTHESIS]** que exista en tu cuenta.

## 3. Requisitos de la integración (lo verificable)

De la guía de integración y la guía para plataformas de Meta (S05-001, S05-002), más la guía Salesforce (S05-003):

**Encaje (eligibility):**
1. Leads de Facebook/Instagram Lead Ads (instant forms) — para la variante web ver §6.
2. Guardar el **Meta Lead ID** (15-17 dígitos, `leadgen_id`) en el CRM. Si no lo hay, enviar parámetros de cliente (click ID, teléfono, email). Make documenta que desde octubre de 2025 el Lead ID ya no es obligatorio si se envía email, aunque sigue recomendado (S05-030). **[OFFICIAL META]** + **[EMPIRICAL]**
3. **Volumen:** "al menos 200 leads al mes" en la guía; GoHighLevel cita 250 (S05-029). **[CONTESTED]** con el anuncio de oct-2025 (ver TL;DR).
4. **Frecuencia:** subir al menos una vez al día (ideal tiempo real; por horas o diario aceptable).
5. **Ventana:** la etapa objetivo ocurre en ≤28 días desde la creación del lead.
6. **Selectividad:** la etapa objetivo convierte entre el **1% y el 40%** de los leads.
7. **Cobertura:** "deberías alcanzar al menos el 60% de lead coverage" (porcentaje de leads de Meta para los que llega al menos un evento del CRM).

**Payload (resumen técnico; el detalle de CAPI lo cubre el área 04):**
- `action_source = "system_generated"`, `custom_data.event_source = "crm"`, `custom_data.lead_event_source = "<nombre del CRM>"`. Sin `lead_event_source`/`event_source`, "los eventos no serán reconocidos para la optimización de Conversion Leads" (S05-003).
- `user_data.lead_id` (máxima prioridad de matching), más `em`/`ph` hasheados si los tienes.
- `event_name` = nombre de la etapa (p.ej. `raw_lead`, `qualified`, `booked_call`, `showed`, `won`). Envía **todas** las etapas a medida que ocurren, empezando por el lead bruto; varias filas con el mismo `lead_id`. Meta deja el nombre libre: en Meta Ads OS, usa los nombres exactos de la tabla del contrato §16 (`docs/desarrollo/contratos.md`), de `Lead` a `Purchase` (`LeadCualificado`, `Schedule`, `LlamadaAsistida`, `PropuestaEnviada`…).
- `event_time` posterior al timestamp de creación del lead (si no, se descarta); backfill hasta 7 días; batches de hasta 1.000 eventos y **un error descarta el batch entero**.
- **Cambiar de dataset reinicia la integración y el aprendizaje.** Decide bien el dataset CRM antes de empezar.

**Tiempos reales** (Meta): integración con partner <1 día; a medida 3-4 semanas; verificación de datos 1-2 días; configuración del funnel en Events Manager; **learning de 2-4 semanas** (S05-001) o 3-4 semanas (S05-002); "time to value" ≈1 mes. Durante el learning puedes usar el objetivo pero el beneficio completo llega al final. GoHighLevel añade que hace falta acumular ≥50 eventos en 7 días para salir del estado "waiting" (S05-029). **[OFFICIAL META]** + **[EMPIRICAL]**

## 4. Qué etapa elegir como objetivo (decisión por volumen)

La pregunta correcta no es "¿qué etapa es más valiosa?" sino "¿cuál es la etapa más profunda de la que Meta puede aprender con mis números?". Tres filtros:

1. **Tiempo:** ¿ocurre en ≤28 días desde el lead? (requisito documentado).
2. **Selectividad:** ¿la alcanza entre el 1% y el 40% de los leads? (requisito documentado). Si el 60% de tus leads llega a "contactado", esa etapa no discrimina nada.
3. **Volumen:** ¿cuántos eventos/semana genera? La guía general de Meta para salir de learning es del orden de 50 resultados por semana por ad set (área 01/09 lo detalla). Para qualified leads Meta no publica un umbral distinto; GHL habla de 50 eventos en 7 días. **[STRONG INFERENCE]**

**Ejemplo trabajado (coaching de 10.000 €, ver archivo 05):** 330 leads/mes (≈77/semana), 40% cualificados, 70% de cualificados agendan, 65% show, 20% cierre.

| Etapa | Tasa sobre leads | Eventos/semana | ¿≤28 días? | ¿1-40%? | ¿Optimizable? |
|---|---|---|---|---|---|
| Lead bruto | 100% | 77 | sí | no (100%) | solo como "Maximize leads" |
| Cualificado (setter/aplicación) | 40% | 31 | sí | sí (justo en el borde) | **sí, mejor candidato hoy** |
| Llamada agendada | 28% | 22 | sí | sí | sí si concentras presupuesto en 1-2 ad sets |
| Show | 18,2% | 14 | sí | sí | arriesgado: volumen bajo |
| Venta | 3,6% | 2,8 | a menudo no (ciclos >28 días con cuotas/seguimiento) | sí | **no**: volumen insuficiente |

Lectura: con este volumen, empieza optimizando a **cualificado** o **agendado**, sigue enviando todas las etapas (incluida la venta y su valor) para medir y para el futuro, y cambia a una etapa más profunda solo cuando el volumen semanal lo permita. Si escalas a 1.000 leads/mes, "show" pasa a ~42/semana y se vuelve viable. **[STRONG INFERENCE]**

**Reglas prácticas:**
- Define "cualificado" con criterios **objetivos y estables** (p.ej. "respondió y cumple presupuesto + plazo + encaje"), no con la opinión del setter del día. Si la definición cambia, la señal se ensucia y Meta aprende ruido. **[STRONG INFERENCE]**
- No marques "cualificado" en el momento del formulario por las respuestas autodeclaradas: eso ya lo ve Meta. El valor de la señal está en lo que pasa **después** (contacto real, conversación, show). **[STRONG INFERENCE]**
- La etapa "descalificado/basura" también es información: envíala como evento propio (p.ej. `disqualified`) para tu análisis, aunque no optimices por ella. Meta pide enviar *todas* las etapas. **[OFFICIAL META]** (S05-002)

## 5. Valor: cuándo usar "Maximize value of conversions" en leads

Meta documenta optimización por valor para leads con estos requisitos (S05-007): pixel + CAPI con valor y moneda, **≥5 valores únicos por evento**, **100+ conversiones en 14 días**, campañas de ≥3 semanas con **50+ conversiones/semana**, presupuesto que cubra ≥50 conversiones/semana. **[OFFICIAL META]**

En high-ticket con 10-30 ventas/mes esto **no es viable** para la venta. Puede serlo para una etapa intermedia a la que asignes un **valor esperado** (p.ej. lead cualificado de "presupuesto alto" = 900 €, "presupuesto medio" = 300 €), calculado con la economía del archivo 05: valor esperado de una etapa = contribución por venta × P(venta | etapa). Es una técnica avanzada; requiere que tu CRM calcule y envíe ese valor. **[HYPOTHESIS]** (no hay casos públicos verificados en high-ticket).

## 6. Qualified leads en formularios web y Sequenced Events (lo nuevo de 2026)

- **Oficial:** "Este objetivo puede usarse con website forms e instant forms" y Meta da un −9,5% de coste por lead de calidad en web frente a maximize leads (S05-007). **[OFFICIAL META]**
- **En despliegue (agosto-octubre 2026):** *Sequenced Events*. En Leads → Website (y en test con instant forms) → Maximize number of qualified leads, eliges un dataset y una secuencia de dos eventos (p.ej. `Lead` → `Schedule`, o `Lead` → evento CRM `BookedVisit`). "Tu anuncio solo recibe crédito si ambos eventos ocurren en el orden definido." Reportes: solo atribución estándar (7 días clic), umbral de elegibilidad aparente ~30 eventos optimizados en 7 días, eventos iniciales con etiqueta CAPI, y en algunas cuentas opción gris "se requiere integración CRM" (S05-033, S05-034, S05-035). **[EMPIRICAL]** (fuentes de practicantes, sin documentación de Meta).
- **Preferred lead answers (test, agosto 2026):** marcar en preguntas de opción múltiple qué respuestas prefieres; no cambia la experiencia del usuario, pero informaría al sistema (S05-033). **[HYPOTHESIS]** sobre su efecto.

**Implicación:** para funnels web de high-ticket (VSL → formulario → calendario), la ruta que se está abriendo es enviar `Lead` (formulario) y `Schedule` (booking) por pixel + CAPI con buena deduplicación, y cuando aparezca Sequenced Events en la cuenta, probar `Lead → Schedule` contra `Schedule` a secas. Hasta entonces, la alternativa clásica es optimizar directamente por `Schedule` (o un evento personalizado de "aplicación cualificada") si tiene volumen. **[STRONG INFERENCE]**

## 7. Mensajería: qué se puede y qué no

- **Leads objective con destino Messenger / Instagram / WhatsApp** y plantillas *Start conversations*, *Automated chat* (preguntas con ramas Question / Completion / **Disqualification**) o *Partner app* (Manychat, etc.). Start conversations y Partner app requieren elegibilidad para "Maximize number of leads through messaging". **[OFFICIAL META]** (S05-020, S05-021)
- **CAPI for Business Messaging** admite `LeadSubmitted` y `QualifiedLead` (además de Purchase, etc.) con `action_source = business_messaging` y `ctwa_clid` para WhatsApp; pero la optimización por eventos vía esta CAPI está documentada para **compras** en click-to-Messenger y click-to-WhatsApp, **no para Instagram**. Para leads por mensajería, la optimización sigue siendo la del propio objetivo (leads through messaging). **[OFFICIAL META]** (S05-025)
- **Caso oficial Braip (Brasil, marzo 2025):** CTWA optimizado por *leads* en lugar de *mensajes* (A/B de Meta, chatbot Manychat con 4 preguntas): +45% leads cualificados y −30% CPL (el titular dice −44%: inconsistencia en la propia fuente). Menos conversaciones, más calidad. **[OFFICIAL META]** caso publicado por WhatsApp Business; tamaño de efecto no generalizable.
- **Detección automática de eventos en WhatsApp** (Meta analiza hilos con regex+NLP y marca LeadSubmitted/Purchase): **no disponible en UE, Reino Unido ni Japón** (S05-026). **[OFFICIAL META]**

## 8. Qué hacer si no puedes integrar el CRM todavía

Orden de preferencia (de más a menos señal útil):
1. **Integración CAPI CRM vía partner** (Zapier, Make, HubSpot, GHL, Salesforce Webhooks, Datahash, Stape, LeadsBridge…): <1 día de setup según Meta. Zapier ofrecía hasta 100.000 eventos gratis y Make tiene su app gratis hasta febrero 2028 → el coste ya no es excusa. **[OFFICIAL META]** + **[EMPIRICAL]** (S05-005, S05-030)
2. **Funnel web** optimizando por un evento más profundo que el lead (`Schedule`, aplicación cualificada) con pixel + CAPI.
3. **Instant form con fricción** (higher intent + SMS + preguntas de cualificación) y "Maximize leads": mejora la calidad de entrada pero el algoritmo sigue persiguiendo envíos. Ver archivo 02.
4. **"Meta source" + Leads with WhatsApp conversations** si está disponible en tu cuenta y país.

## Implicaciones operativas

- **Haz la integración CRM antes de escalar.** Desde abril 2026 es condición para usar qualified leads en campañas nuevas. Sin ella estás optimizando a envíos de formulario.
- **Guarda el Meta Lead ID siempre** (campo personalizado en el CRM) y envía el lead bruto como primer evento: la baja cobertura suele deberse a falta de lead ID o a no enviar el raw lead (S05-003).
- **Elige una etapa objetivo con 1-40% de conversión y ≤28 días;** revisa cada mes si el volumen permite bajar un escalón en el funnel.
- **Umbrales de decisión:** ≥50 eventos/semana de la etapa → optimiza por ella; 20-50 → consolida ad sets o sube una etapa; <20 → optimiza por la etapa anterior y usa la profunda solo para medir.
- **No cambies de dataset CRM** una vez empezado (reinicia aprendizaje).
- **Mide en tu CRM, no en Ads Manager:** coste por lead cualificado, por agenda, por show, por venta y cash por anuncio (archivo 09).

## Errores frecuentes

- Definir "cualificado" como "rellenó el formulario con presupuesto alto" (señal que Meta ya tiene) en vez de un hecho posterior verificable.
- Enviar solo la etapa final ("won"): Meta pide ≥2 etapas incluyendo el lead bruto, recomienda ≥3.
- Etapas con timestamps anteriores al lead o en batches con un evento erróneo (se descarta el batch entero).
- Usar HubSpot "lifecycle stage sync" creyendo que manda el lead ID: según la comunidad y la KB de HubSpot, el matching es por click ID/email/teléfono; reportes de "configuración CRM incompleta" en Meta (S05-027, S05-028). Verifica cobertura en Events Manager.
- Juzgar qualified leads por CPL: Meta advierte que el CPL puede subir mientras baja el coste por lead de calidad; la métrica correcta es coste por etapa objetivo y coste por venta.
- Cortar la campaña durante el learning de 2-4 semanas porque el CPL subió.

## Preguntas abiertas

- ¿Sigue existiendo un mínimo de volumen efectivo tras el anuncio de oct-2025 ("se eliminó el requisito mínimo")? La documentación de desarrolladores y GHL siguen citando 200-250 leads/mes.
- ¿Cómo convive "Meta source + Leads with WhatsApp conversations" con la regla de abril 2026 (qualified leads solo con CAPI)?
- Sequenced Events: ventana entre eventos, umbral real, si se generaliza a instant forms y si exige CRM.
- ¿Existe hoy la fuente "Calls" para qualified leads con call ads?
- Efecto real de Preferred lead answers.

## Fuentes clave

- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) — vigente 2026-10-15 — meta-oficial (S05-007)
- [Set up your CRM for qualified leads](https://www.facebook.com/business/help/279369167153556) — vigente 2026-10-15 — meta-oficial (S05-008)
- [Conversions API for CRM integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) — 2025-12 — meta-developers (S05-001)
- [Conversions API for CRM: Integrate as a Platform](https://developers.facebook.com/documentation/ads-commerce/conversions-api/guides/conversions-api-crm-for-platforms) — vigente 2026 — meta-developers (S05-002)
- [More quality leads this Q5 with Meta's latest AI-enabled updates](https://www.facebook.com/business/news/more-quality-leads-this-q5-with-metas-latest-ai-enabled-updates) — 2025-10-30 — meta-oficial (S05-005)
- [Conversions API for Business Messaging](https://developers.facebook.com/docs/marketing-api/conversions-api/business-messaging/) — vigente 2026 — meta-developers (S05-025)
- [Meta Tests Sequenced Events and Preferred Lead Answers](https://www.jonloomer.com/meta-tests-sequenced-events-preferred-lead-answers/) — 2026-08-07 — practitioner (S05-033)
- [Facebook Ads Can Now Optimize for Leads That Book](https://digitalvibes.design/blog/facebook-ads-qualified-leads) — 2026-10-07 — practitioner (S05-034)
- [Braip success story (WhatsApp Business)](https://whatsappbusiness.com/resources/success-stories/braip/) — 2025 — meta-oficial (S05-053)

## Correcciones de la revisión adversarial (2026-10-16)

> Revisor: A12 (agente adversarial). Cambios mínimos sobre el texto original; fuentes en `fuentes/ledger-12-mitos-contradicciones.md`.

- Mínimo de 200 leads/mes: [CONTESTED] → resuelto. El anuncio oficial del 30-oct-2025 elimina el requisito; la guía de developers está desfasada (también en "solo instant forms", que el Help Center 782657799338685 contradice).
