# Webinars, eventos, challenges y lanzamientos (en directo, VSL launch y evergreen) con Meta Ads

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: estructurar campañas por fases, presupuesto por fase, retargeting, y medir registro → asistencia → permanencia → aplicación/llamada → venta → cash. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **El webinar tiene dos conversiones que Meta no ve por defecto: la asistencia y la permanencia hasta la oferta.** Meta optimiza registros (`CompleteRegistration`/`Lead`); si no devuelves "asistió" y "compró", el algoritmo te traerá registrantes baratos que no aparecen. **[STRONG INFERENCE]**
- **Benchmarks de asistencia (definiciones distintas, no se pueden promediar):** ON24 (plataforma B2B, directo + on-demand) 60% en 2025, 57% en 2024; mediana independiente ~41,6% en directo (~12.400 webinars B2B); rangos de guías 35-50% en directo. Para tráfico frío pagado B2C no hay benchmark público fiable; los practicantes suelen ver cifras **más bajas** → **[HYPOTHESIS]** planificar con 20-35% y medir. (S05-045, S05-046)
- **La matemática manda:** en un webinar que vende un curso de 497 € directamente, con 25% de show y 5% de compra entre asistentes, el coste por registro máximo es **4,20 €** (target 2,10 €). Si vendes un coaching de 10.000 € vía aplicación, el máximo es **17,40 €** (target 8,70 €). Archivo 05 §7. **[STRONG INFERENCE]**
- **Fases de un lanzamiento:** (1) pre-lanzamiento/captación de registros, (2) evento (webinar/challenge/serie de vídeos), (3) carrito abierto (retargeting a registrantes, asistentes y visitantes de la página de venta), (4) cierre (urgencia real), (5) post-lanzamiento (replay, evergreen). La mayor parte del presupuesto va a la fase 1; la fase 3 es barata y de ROAS alto. Repartos publicados (70-90% frío / 10-30% retargeting; 20-30% del total en pre-lanzamiento) son heurísticas de practicantes **[HYPOTHESIS]**.
- **Evergreen:** el "just-in-time" (empezar a los pocos minutos del registro) dispara la asistencia en casos publicados (un caso: de 20,56% a 75,62% con EverWebinar), a costa de un formato menos "en directo". Un caso, no benchmark. **[EMPIRICAL]** débil (S05-084)
- **Recordatorios:** la evidencia controlada sobre SMS automáticos es modesta (RCT de GSA: −1,6 pp de no-show, no significativo); las cifras grandes vienen de encuestas de vendors. Los recordatorios son higiene, no magia; la asistencia se gana con la promesa del evento y la cercanía temporal. **[EMPIRICAL]** (S05-047, S05-048)

---

## 1. Por qué el webinar es un funnel "de dos optimizaciones"

```
Impresión → clic → página de registro → REGISTRO (Meta lo ve) → asistencia (Meta NO lo ve) → permanencia hasta la oferta (NO) → aplicación/compra (lo ve si hay pixel/CAPI) → cash (CRM)
```

Problemas típicos:
- El algoritmo optimiza a registros baratos → audiencias que registran mucho y asisten poco (curiosos, buscadores de freebies).
- La compra ocurre días después y en volumen bajo → no sirve como evento de optimización salvo lanzamientos grandes.

Soluciones por orden de impacto:
1. **Devolver asistencia como evento**: la plataforma de webinar (Zoom, WebinarJam, EverWebinar, Livestorm…) envía webhook de "asistió" → CRM/Zapier/Make → CAPI con `em`/`ph` (+`fbc` si lo capturaste en el registro) como evento personalizado `WebinarAttended` (y `StayedToPitch` si la plataforma da minutos vistos). Son nombres de ejemplo: en Meta Ads OS, `WebinarAsistido` y `WebinarHastaOferta`, de la tabla del contrato §16 (`docs/desarrollo/contratos.md`). Con volumen (≥50/semana) puedes optimizar a asistencia; si no, úsalo para medir por anuncio y para audiencias. **[STRONG INFERENCE]** (no hay guía oficial de Meta específica para webinars; mecánica estándar de CAPI, área 04).
2. **Registro con instant form vs landing:** el instant form abarata el registro pero suele bajar la asistencia; mide coste por **asistente**, no por registro. **[HYPOTHESIS]** (sin estudio público; coherente con el test de Loomer donde la calidad fue similar).
3. **Señal de compromiso en el registro:** pregunta de segmentación ("¿qué quieres resolver?"), confirmación por WhatsApp/SMS, añadir al calendario.

## 2. Tipos de evento y para qué sirven

| Formato | Duración | Mejor para | Métrica clave | Notas |
|---|---|---|---|---|
| Webinar en directo | 60-90 min | Lanzamientos, autoridad, ofertas 500-5.000 € con compra directa o aplicación | Coste por asistente en directo; % que se queda a la oferta | Show en directo bajo con tráfico frío; replay recupera parte |
| Webinar evergreen (automatizado) | 30-60 min | Captación continua, ofertas estables | Coste por asistente; ventas por cohorte semanal | Just-in-time sube asistencia (caso EverWebinar) |
| VSL launch / serie de vídeos | 3-4 vídeos en 7-10 días | Lanzamientos estilo "product launch" | % que ve vídeo 3; ventas en carrito abierto | Vídeos pueden ser anuncios (retargeting por visualización) |
| Challenge (3-5 días) | 5-7 días | Comunidad, compromiso progresivo, info-producto | Asistencia por día; ventas al final | Challenge de pago (7-47 €) filtra y da señal Purchase |
| Taller/workshop de pago | 2-3 h | Filtrar compradores; tripwire | Coste por comprador; ascenso a oferta principal | Señal Purchase optimizable |
| Evento presencial | 1-2 días | Ventas high-ticket en sala, B2B | Coste por asistente presencial; ventas en evento | Ubicación + geo; confirmaciones múltiples |

## 3. Estructura de campañas por fase (lanzamiento en directo)

| Fase | Duración típica | Objetivo / evento | Audiencia | Creatividad | Presupuesto (heurística) |
|---|---|---|---|---|---|
| 0. Calentamiento (opcional) | 2-4 semanas antes | Engagement/ThruPlay o tráfico a contenido | Frío amplio | Contenido de valor del experto, casos | 0-10% |
| 1. Registro | 7-21 días antes | Leads → `CompleteRegistration`/Lead (o asistencia si hay volumen) | Frío (Advantage+), lookalikes de compradores como sugerencia | Promesa del evento, 3 aprendizajes, para quién es | 50-70% |
| 1b. Recordatorio pre-evento | Últimos 3-5 días | Reach/awareness o engagement a registrantes | Registrantes (custom audience de lista o evento) | "Mañana a las 19:00", qué traer, bonus por asistir | 3-5% |
| 2. Evento | Día(s) del evento | — (o retargeting "estamos en directo") | Registrantes no asistentes | "Empieza en 15 min / replay disponible" | 1-3% |
| 3. Carrito abierto | 3-7 días | Sales/Leads → Purchase/aplicación | Asistentes, registrantes, visitantes de página de venta, viewers de vídeos | Testimonios, objeciones, desglose de la oferta, FAQ | 15-30% |
| 4. Cierre | Últimas 24-48 h | Sales → Purchase | Igual que 3 | Urgencia **real** (bonus que expira, cierre de plazas) | incluido en 3 |
| 5. Post-lanzamiento | Después | Evergreen/lista | No compradores | Replay limitado, contenido, siguiente evento | — |

Las proporciones son **[HYPOTHESIS]** construidas desde primeros principios y heurísticas publicadas (DigitalMarketer caso antiguo: ~60% frío en 5 ad sets, 30% cálido, 5% retargeting a visitantes, 10% consumo/objeciones/escasez; Stackmatix: 20-30% del total en pre-lanzamiento; Steve Bruce: 70-90% frío / 10-30% retargeting). Ninguna es un benchmark medido. Ajusta con tu calculadora: el presupuesto de registro está limitado por el **coste por asistente objetivo**.

**Ventana de aprendizaje:** una campaña de registro de 10-14 días necesita llegar a ~50 registros/semana por ad set para estabilizarse (regla general de learning de Meta). Con presupuestos pequeños, un solo ad set Advantage+ y 3-6 anuncios. **[STRONG INFERENCE]**

## 4. Evergreen: estructura continua

- 1 campaña de prospección siempre activa → registro (o asistencia si hay volumen) con presupuesto estable; refresco creativo cada 2-4 semanas según frecuencia y fatiga (área 03).
- 1 campaña de retargeting continuo a registrantes no asistentes (replay), asistentes no compradores (objeciones/casos), visitantes de página de venta.
- Cohortes semanales: registros de la semana N → asistencia → ventas a 7/14/30 días → cash.
- Ventaja: datos limpios por cohorte; Meta estable. Riesgo: el webinar envejece; revisa conversión asistente→venta cada mes.

## 5. Benchmarks con fuente

| Métrica | Valor | Fuente | Confianza |
|---|---|---|---|
| Registro → asistencia (directo + on-demand) | 60% (2025), 57% (2024), 56% (2023) | ON24 Digital Engagement Benchmarks 2026 (plataforma, B2B) | media (sesgo de plataforma) |
| Asistencia en directo, mediana | 41,6% (~12.400 webinars B2B) | Agregador citado en S05-046 | media-baja |
| Asistencia en directo, rango | 35-50% | Asset Academy 2026 (varias fuentes) | baja-media |
| Asistencia B2B (Goldcast) | 33% titular (21% agregado calculado) | Goldcast 2025 vía secundaria | baja |
| Visita → registro | 20-30% medio; tráfico frío pagado 10-20%; lista caliente >40% | Asset Academy 2026 | baja-media |
| Asistente → venta | High-ticket 5-20%; low-ticket 5-15%; blended 2-10% | Asset Academy 2026 | baja |
| Coste por registro cualificado (coaching, Meta) | 8-15 $ | 780 Marketing 2026 | baja |
| "Show 60-70% con recordatorios" (webinar coaching) | 60-70% | 780 Marketing 2026 | baja (probablemente incluye replay) |
| Just-in-time evergreen | 20,56% → 75,62% | Venture Harbour (un caso) | baja |
| Efecto de SMS automáticos (RCT, citas) | −1,6 pp, no significativo | GSA OES | media-alta (otro contexto) |

## 6. Ejemplo numérico: ¿cuánto puedo pagar por registro?

(Calculadora, archivo 05 §7.)

**A) Curso 497 € IVA incl. vendido en el webinar** (contribución 336,3 € por venta; 5% de asistentes compra):

| Show en directo | BE coste por registro | Target (50%) |
|---|---|---|
| 20% | 3,36 € | 1,68 € |
| 25% | 4,20 € | 2,10 € |
| 35% | 5,88 € | 2,94 € |
| 25% + 10 pp viendo replay (mitad de conversión) | 5,04 € | 2,52 € |

**B) Coaching 10.000 € con aplicación tras el webinar** (show 30%, 12% de asistentes aplica, 60% agenda, 70% show de llamada, 25% cierre): BE 17,40 € por registro, target 8,70 €; con 15.000 € de inversión a 10 €/registro → 5,67 ventas, CPA 2.646 €, beneficio 11.100 €. Con show del 20%, el BE cae a 11,60 €.

Lectura: los webinars de low-ticket con tráfico frío pagado rara vez cuadran sin upsells o back-end; los de high-ticket aguantan registros de 8-15 € si el equipo de ventas convierte. **[STRONG INFERENCE]**

## 7. Medición: el cuadro de mando del webinar

| Etapa | Fuente del dato | Evento a Meta |
|---|---|---|
| Registro | Pixel + CAPI (o instant form) | `CompleteRegistration` / `Lead` |
| Confirmación (doble opt-in / WhatsApp) | Email/CRM | personalizado (opcional) |
| Asistencia en directo | Webhook plataforma | `WebinarAttended` (CAPI; ejemplo, en Meta Ads OS `WebinarAsistido`) |
| Permanencia hasta la oferta | Minutos vistos | `StayedToPitch` (CAPI; ejemplo, en Meta Ads OS `WebinarHastaOferta`) |
| Visita página de venta / aplicación | Pixel + CAPI | `ViewContent` / `Lead` |
| Agenda | Calendario | `Schedule` |
| Compra | Pasarela/CRM | `Purchase` con valor |
| Cash cobrado | CRM/pasarela | (informe interno; valor en Purchase) |

En Meta Ads OS, los eventos personalizados del taller o webinar se llaman como en la tabla del contrato §16
(`docs/desarrollo/contratos.md`), con sus mayúsculas.

Informe por anuncio: coste por registro, por asistente, por asistente-a-la-oferta, por aplicación, por venta, cash a 7/30 días.

## Implicaciones operativas

- Calcula el **coste por asistente objetivo** antes de lanzar; el coste por registro se deriva de ahí con tu show rate realista.
- Envía asistencia y compra por CAPI desde el primer evento, aunque no optimices por ellos todavía.
- Mantén campañas de registro estables 10-21 días; evita reinicios de learning por cambios diarios.
- En carrito abierto, el retargeting a asistentes y a visitantes de la página de venta suele ser lo más rentable del lanzamiento; protege su presupuesto. **[STRONG INFERENCE]**
- Usa urgencia real (bonus que expira, plazas reales); la urgencia falsa es riesgo de política y de reembolsos.

## Errores frecuentes

- Juzgar el lanzamiento por coste por registro.
- Optimizar a registros con un formulario de 1 clic y quejarse de asistencia del 15%.
- No tener replay ni secuencia de recordatorios por el canal que el usuario abre (WhatsApp en España).
- Lanzar retargeting de carrito abierto sin excluir compradores.
- Medir ventas solo en la ventana de atribución de Meta (las ventas de lanzamiento llegan por email/WhatsApp, fuera del clic).

## Preguntas abiertas

- Benchmarks de asistencia en webinars B2C con tráfico frío de Meta en España (no hay datos públicos fiables).
- ¿Optimizar a asistencia (`WebinarAttended` en el ejemplo; `WebinarAsistido` en Meta Ads OS, contrato §16) por CAPI supera a optimizar a registro? Sin estudios públicos.
- Efecto de recordatorios por WhatsApp vs email en asistencia (sin estudios controlados encontrados).

## Fuentes clave

- [Webinar Conversion Rate Benchmarks](https://assetacademy.io/funnels/webinars/webinar-conversion-rate-benchmarks/) — 2026-08-02 — practitioner (S05-045)
- [Webinar registration & attendance statistics 2026 (incl. ON24 2026)](https://stealthagents.com/research/webinar-registration-attendance-statistics-2026) — 2026 — vendor (S05-046)
- [Cost Per Booked Call Benchmarks for High-Ticket Coaches](https://www.780marketing.ca/articles/cost-per-booked-call-benchmarks) — 2026-07-03 — agencia (S05-042)
- [Boost webinar attendance rate (EverWebinar case)](https://ventureharbour.com/boost-webinar-attendance-rate/) — s.f. — practitioner (S05-084)
- [OES/GSA automated text reminders evaluation](https://oes.gsa.gov/assets/abstracts/2313-abstract.pdf) — s.f. — academico (S05-048)
- [How to Launch a Product with Facebook Ads (case study)](https://digitalmarketer.com/podcast/perpetual-traffic/launch-a-product-with-facebook-ads) — antiguo (~2017) — practitioner (S05-082)
