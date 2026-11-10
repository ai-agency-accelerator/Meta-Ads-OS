# Speed to lead, calendarios y show rate: la evidencia y cómo afecta a los resultados de campaña

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: tiempo de respuesta al lead, diseño de booking (página, disponibilidad, confirmación, recordatorios), show rate y su impacto en la economía y en la señal que recibe Meta. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **El estudio clásico (InsideSales/MIT, 2007): llamar en 5 minutos frente a 30 multiplica por 100 las probabilidades de contactar y por 21 las de cualificar; de 5 a 10 minutos ya caen ×5 (contacto) y ×4 (cualificación).** Muestra: 6 empresas, 3 años, >15.000 leads web, >100.000 llamadas. **No midió cierre.** **[EMPIRICAL]** sólido para lo que mide, antiguo (S05-037)
- **HBR 2011 (Oldroyd, McElheran, Elkington):** de 2.241 empresas auditadas, solo el 37% respondió en <1 h y el 23% nunca; en un dataset de 1,25 M de leads, responder en la primera hora hace ~7× más probable cualificar que en la segunda, y >60× que tras 24 h. **[EMPIRICAL]** (vía resúmenes; S05-038, S05-039)
- **No hay un estudio independiente 2025-2026 que actualice estas cifras**; los más recientes son de vendors (RevenueHero 2024: el 63,5% de 1.000 SaaS nunca respondió a una solicitud de demo). Las cifras clásicas son direccionalmente fiables, los multiplicadores exactos no se deben citar como ley. **[EMPIRICAL]** (S05-039)
- **Meta lo asume oficialmente:** recomienda integrar CRM para capturar leads al instante y **programar los anuncios en las horas en que puedes responder**. **[OFFICIAL META]** (S05-014, S05-013)
- **Show rate:** depende sobre todo de (1) cuánto tarda la cita (1 día ≈81% vs 14 días ≈60%, análisis secundario de 6.414 reuniones), (2) de cómo se reservó (booking instantáneo en el formulario ≈8% no-show vs lead form de paid social ≈33%, estimaciones de Focus Digital) y (3) de la secuencia de confirmación. **[EMPIRICAL]** débil-medio (S05-040, S05-089)
- **Recordatorios automáticos solos tienen efecto pequeño** (RCT de GSA con SMS: −1,6 pp, no significativo; ensayo clínico con dos recordatorios a 3 días y 1 día: 4,4% vs 5,8% de citas perdidas). Las cifras de "−88% de no-shows" son encuestas de vendors. **[EMPIRICAL]** (S05-047, S05-048, S05-089)
- **Impacto en Meta:** la velocidad y el show rate no solo cambian tu CPA: cambian **la señal** que devuelves (más leads llegan a "cualificado/agendado/show"), y por tanto lo que aprende qualified leads. Un equipo lento convierte buenos leads en "malos" y entrena a Meta con ruido. **[STRONG INFERENCE]**
- **Booking embebido en instant forms (2026)** reduce a cero el tiempo entre interés y cita; es la palanca más directa contra ambos problemas. Solo se embebe en la app móvil de Facebook y la reserva **no se reporta en Ads Manager** (devuélvela vía CAPI CRM). **[OFFICIAL META]** (S05-095, S05-059)

---

## 1. Speed to lead: qué dicen exactamente los estudios

### 1.1 InsideSales.com / MIT Lead Response Management Study (2007)
(Leído del PDF original resumido, S05-037.)
- Pregunta: ¿cuándo llamar a leads web para maximizar contacto y cualificación? **"Este estudio no abordó tasas de cierre."**
- Datos: 3 años, 6 empresas, >15.000 leads, >100.000 intentos de llamada. "Contacto" = llamada con persona real de duración mínima (2-6 min según empresa); "cualificado" = definición de cada empresa (a veces, agendar con un comercial).
- Hallazgos:
  - Las probabilidades de contactar caen **>10×** en la primera hora; las de cualificar **>6×**.
  - **5 vs 30 minutos: ×100 contacto, ×21 cualificación.** 5 vs 10 minutos: ×5 y ×4.
  - **Tras 20 horas, cada intento adicional *empeora* la probabilidad de contactar/cualificar.**
  - Mejores días: miércoles y jueves; mejores franjas: 16-18 h para contactar, 8-9 h y 16-17 h para cualificar (datos EE. UU., 2007).
- Limitaciones: pre-smartphone y pre-WhatsApp; solo llamadas; 6 empresas; patrones que, según el propio autor, aparecen al agregar empresas y varían entre ellas.

### 1.2 HBR, "The Short Life of Online Sales Leads" (marzo 2011)
- Auditoría de 2.241 empresas de EE. UU. con leads de prueba: 37% responde en <1 h, 16% en 1-24 h, 24% en >24 h, **23% nunca**; respuesta media de 42 h (entre las que respondieron en 30 días).
- Dataset de 1,25 M leads (29 B2C, 13 B2B): contactar en la primera hora → "casi 7 veces" más probable cualificar que una hora después; >60× que tras ≥24 h.
- Ojo: los famosos "100× / 21×" son del estudio MIT/InsideSales, no de HBR (comparten autores). (S05-038, S05-039)

### 1.3 Datos posteriores (vendors)
- **Drift (2017, no 2018):** 433 empresas SaaS B2B; 7% respondió en ≤5 min; 55% no respondió en 5 días laborables.
- **Velocify/Leads360 (2012):** ~3,5 M leads de >400 empresas; llamar en <1 min +391% de conversión; **93% de los leads convertidos se alcanzan antes del 6º intento**; mejor cadencia: contacto rápido + 6 llamadas + 5 emails.
- **RevenueHero (2024):** 1.000 SaaS con solicitud de demo; 63,5% nunca respondió; media de quienes respondieron: 1 día y 5 h.
(S05-039; todos vendor, sin revisión académica.)

### 1.4 Qué implica para Meta lead gen (inferencias)
- Los leads de Meta son **más impulsivos** que un formulario web de "pide presupuesto": el interés decae más rápido. Que el lead "no recuerde haber rellenado el formulario" es casi siempre un problema de velocidad. **[STRONG INFERENCE]**
- El canal de primer contacto en España: WhatsApp (mensaje inmediato con nombre + contexto del anuncio) + llamada en los primeros 5 minutos. **[HYPOTHESIS]** (sin estudio español; coherente con el uso de WhatsApp y con Meta empujando "chat with leads").
- **Programa los anuncios** (ad scheduling con presupuesto de campaña) para no generar leads de madrugada si nadie responde; o automatiza la respuesta 24/7 con bot/agente (Meta testea un agente de nurturing en Messenger, S05-005). **[OFFICIAL META]**

## 2. Diseño del proceso de respuesta (SLA)

| Paso | Objetivo | Herramienta |
|---|---|---|
| Lead entra al CRM | <1 min tras el envío | Integración nativa/webhook (no CSV) |
| Mensaje automático personalizado | <1 min | WhatsApp API / SMS / email con nombre y referencia al anuncio |
| Primer intento humano | <5 min en horario | Asignación round-robin, alerta móvil al setter |
| Cadencia | 6 intentos en 48-72 h mezclando llamada/WhatsApp/email | Secuencia en CRM; no más allá de lo útil (MIT: tras 20 h, intentos extra restan) |
| Booking | En el primer contacto | Enlace de calendario o reserva directa por el setter |
| Etiqueta de resultado | Mismo día | Etapa + motivo (no contesta, no cualifica, agendado…) → CAPI CRM |

**Métricas:** mediana de tiempo a primer intento, % contactado en 1 h, % contactado en total, intentos hasta contacto, lead→agenda por setter y por franja horaria.

## 3. Calendario y booking: decisiones que mueven el show rate

### 3.1 Cuándo reservar
- **Ventana corta:** ofrece citas en las próximas 24-72 h. En el análisis secundario de 6.414 reuniones (Bohrt), las citas a 1 día se celebran ~81% y a 14 días ~60%; GrowthSpree (sin metodología) da 78-88% mismo día vs 22-35% a 14+ días. **[EMPIRICAL]** débil (S05-089)
- **Disponibilidad:** pocas franjas visibles (escasez real y coordinación del closer) pero suficientes para que el 80% encuentre hueco en 72 h. **[HYPOTHESIS]**

### 3.2 Cómo se reservó
Estimaciones de Focus Digital (2026), normalizadas como "ni asistió ni canceló" (sin muestra propia; confianza baja-media, S05-040):

| Canal de reserva | No-show | Citas celebradas por 10 |
|---|---|---|
| Booking instantáneo al rellenar el formulario | 8% | 9,2 |
| Referido/partner | 12% | 8,8 |
| Demo inbound autoagendada | 15% | 8,5 |
| Llamada inbound, el comercial agenda | 18% | 8,2 |
| Chat/chatbot | 21% | 7,9 |
| Descarga de contenido / seguimiento de webinar | 27% | 7,3 |
| **Formulario de paid search/social** | **33%** | **6,7** |
| Cold email (SDR) | 36% | 6,4 |
| Cold call (SDR) | 39% | 6,1 |
| Agencia externa de setting | 42% | 5,8 |

Lectura: el mismo lead de Meta puede rendir un 33% de no-show (formulario → te llamamos → agendamos) o mucho menos si **reserva en el momento** (booking embebido o calendario en la página de gracias). **[STRONG INFERENCE]** a partir de estimaciones.

### 3.3 Confirmación y recordatorios
- **Página de confirmación con vídeo** ("qué pasará en la llamada", quién te atenderá, casos, qué preparar) — práctica estándar en high-ticket; un vendor reporta show 75-85% con secuencia pre-llamada vs 45-55% sin ella (S05-087, baja). **[EMPIRICAL]** débil
- **Recordatorios:** a 24 h y 1-2 h, por WhatsApp/SMS + email + invitación de calendario. Evidencia controlada: el efecto de SMS automáticos solos es pequeño (GSA: 16,2% vs 17,8%, no significativo); dos recordatorios (3 días y 1 día) frente a uno redujeron citas perdidas de 5,8% a 4,4% en primaria (Steiner 2018). Recordatorio telefónico **humano** a pacientes de alto riesgo: 29,2% → 22,8% (MGH). **[EMPIRICAL]** (contexto sanitario, transferible solo como patrón)
- **Reconfirmación activa** (pedir respuesta "Sí, confirmo") y reprogramación fácil (un no-show que reprograma no es una pérdida).
- **Señales de compromiso previas:** pequeña tarea (ver vídeo, rellenar pre-cuestionario), depósito reembolsable en algunos servicios. **[HYPOTHESIS]**

### 3.4 Cómo medir el show rate (definición)
`Show rate = llamadas celebradas / llamadas agendadas en la misma ventana`, con cancelaciones y reprogramaciones en el denominador (si no, el número se infla). Separar por canal, por anuncio, por plazo de reserva y por setter. Con <30 agendas/mes, mira trimestres. (S05-089)

## 4. Cuánto vale mejorar velocidad y show (en euros)

Usando el coaching de 10.000 € del archivo 05 (contribución 4.603 €/venta; lead→cualificado 40%, cualificado→agenda 70%, cierre 20%):

| Escenario | Show | BE CPL | BE por agenda |
|---|---|---|---|
| Base | 65% | 167,56 € | 598,41 € |
| Calendario a 2 semanas, sin confirmación | 50% | 128,89 € | 460,32 € |
| Booking inmediato + secuencia de confirmación | 80% | 206,22 € | 736,51 € |

Pasar de 50% a 80% de show aumenta un **60%** lo que puedes pagar por lead, sin tocar Meta. Además, más shows → más eventos de etapa profunda → mejor señal para qualified leads. **[STRONG INFERENCE]**

Para speed to lead el efecto es sobre **lead→cualificado y cualificado→agenda**: si responder en 5 min en vez de 2 h sube el contacto del 50% al 70%, el lead→agenda sube un 40% relativo y el BE CPL también. El tamaño exacto depende de tu negocio; mídelo con un test (alternar semanas o setters). **[HYPOTHESIS]** sobre el tamaño; **[EMPIRICAL]** sobre la dirección.

## 5. Efecto en la optimización de Meta

- Con qualified leads, Meta aprende de qué leads llegan a la etapa objetivo. Si el 30% de leads buenos nunca llega a "cualificado" porque se contactaron tarde, el sistema recibe etiquetas falsas negativas y aprende a evitar perfiles que en realidad eran buenos. **[STRONG INFERENCE]**
- Al revés: mejorar velocidad/show **sube el volumen** de la etapa objetivo, lo que permite optimizar más abajo en el funnel (archivo 03 §4).
- Programar anuncios en horario de respuesta reduce entrega en franjas baratas; el coste de entrega puede subir. Compáralo con la caída de calidad nocturna en tu CRM antes de decidir. **[HYPOTHESIS]**

## Implicaciones operativas

- SLA: primer contacto <5 min en horario; cadencia de 6 intentos en 48-72 h; no insistir indefinidamente.
- Ofrece reserva en el momento de mayor interés (booking embebido, calendario en página de gracias, setter que agenda en la primera llamada).
- Citas en ≤72 h; confirmación activa; recordatorios a 24 h y 1-2 h por WhatsApp + email.
- Mide show por canal, anuncio, plazo y setter; usa la definición estricta.
- Antes de pedir más presupuesto a Meta, calcula cuánto vale +10 pp de show.

## Errores frecuentes

- Descargar CSVs una vez al día.
- Medir el show rate sin cancelaciones en el denominador.
- Citar los "100×/21×" como si fueran de Harvard o como si midieran cierre.
- Calendarios abiertos a 2-3 semanas vista "para dar flexibilidad".
- Recordatorios solo por email.

## Preguntas abiertas

- Estudio independiente reciente (2024-2026) sobre speed to lead en leads de redes sociales, y en mercados WhatsApp-first.
- Efecto medido del booking embebido de Meta en show y cierre.
- Peso relativo de velocidad vs plazo de cita vs recordatorios en high-ticket.

## Fuentes clave

- [InsideSales.com/MIT Lead Response Management Study (resumen PDF)](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf) — 2007 — academico/vendor (S05-037)
- [The Short Life of Online Sales Leads (HBR)](https://hbr.org/2011/03/the-short-life-of-online-sales-leads) — 2011-03 — academico (S05-038)
- [Lead Response Time: Every Study](https://ainora.lt/blog/lead-response-time-statistics-every-study-2026) — 2026 — vendor (S05-039)
- [Best practices to respond to leads](https://www.facebook.com/business/help/2246428158756947) — meta-oficial (S05-014)
- [Average No-Show Rate by Booking Channel 2026](https://focus-digital.co/average-no-show-rate-for-booked-sales-meetings-by-booking-channel/) — 2026-09-14 — agencia (S05-040)
- [Good Sales Call Show Rate: Benchmarks by Industry, Lead Time](https://leadsnow.ai/good-sales-call-show-rate-benchmarks/) — 2026-09-27 — vendor (S05-089)
- [GSA OES text reminders evaluation](https://oes.gsa.gov/assets/abstracts/2313-abstract.pdf) — academico (S05-048)
- [Meta launches integrated booking for lead ads](https://www.socialmediatoday.com/news/meta-launches-integrated-booking-for-lead-ads/823711/) — 2026-06-24 — prensa (S05-059)
