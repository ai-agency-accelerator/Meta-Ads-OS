# Playbook: Webinars, eventos, challenges y lanzamientos

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: lanzamientos en directo, evergreen, challenges, eventos presenciales. Base: `05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Calcula primero el coste por asistente máximo** (contribución × % compra de asistentes × (1 − margen)); el coste por registro máximo = coste por asistente × show rate realista. **[STRONG INFERENCE]**
- **Devuelve asistencia y compra a Meta por CAPI** (`WebinarAsistido` y `Purchase`, con los nombres del contrato §16 en `docs/desarrollo/contratos.md`): sin eso, Meta optimiza a registrantes que no asisten. **[STRONG INFERENCE]**
- **Asistencia:** ON24 60% (B2B, directo + on-demand); mediana independiente ~41,6% en directo; tráfico frío B2C pagado probablemente menor → planifica con 20-35% y mide. **[EMPIRICAL]** / **[HYPOTHESIS]** (S05-046, S05-045)
- **Presupuesto:** la mayoría en registro; el retargeting de carrito abierto es la parte más rentable y no debe quedarse sin presupuesto; las proporciones publicadas son heurísticas. **[HYPOTHESIS]**
- **Evergreen just-in-time** puede disparar la asistencia (un caso: 20,56% → 75,62%). **[EMPIRICAL]** débil (S05-084)

---

## 1. Cuándo usar Meta para eventos

- Cuando la venta necesita educación (método nuevo, precio medio-alto) y tienes un presentador que convierte.
- Lanzamientos con fecha (cohortes, programas grupales) y evergreen para captación continua.
- No para vender algo que se entiende en una página (vende directo).

## 2. Arquitectura por fase (lanzamiento en directo)

| Fase | Duración | Campaña / evento | Audiencia | Presupuesto (heurística) |
|---|---|---|---|---|
| Registro | 7-21 días | Leads/Sales → `CompleteRegistration` (o asistencia si volumen) | Frío Advantage+, sugerencias de compradores | 50-70% |
| Recordatorio | últimos 3-5 días | Reach/engagement | Registrantes | 3-5% |
| Directo | día del evento | Reach "empieza en 15 min" | Registrantes no conectados | 1-3% |
| Carrito abierto | 3-7 días | Sales → `Purchase`/aplicación | Asistentes, registrantes, visitantes de venta, viewers | 15-30% |
| Cierre | 24-48 h | Sales | Igual | incluido |
| Post | — | Evergreen/replay | No compradores | — |

**Evergreen:** 1 campaña de registro estable + 1 de retargeting continuo; cohortes semanales; refresco creativo cada 2-4 semanas.

**Challenge (3-5 días):** registro (gratuito o de pago 7-47 € → `Purchase`, mejor señal), retargeting diario a inscritos ("hoy: día 2"), oferta al final con carrito 3-5 días.

**Evento presencial:** geo + radio; registro con pago/depósito si es posible (reduce no-show); recordatorios múltiples; medir asistentes reales (check-in) → CAPI.

## 3. Evento de optimización

| Volumen semanal | Optimiza a |
|---|---|
| < 50 asistentes | Registro (`CompleteRegistration`), con preguntas de compromiso y confirmación WhatsApp |
| ≥ 50 asistentes | Probar `WebinarAsistido` (CAPI, contrato §16) vs registro |
| ≥ 50 compras (lanzamientos grandes) | `Purchase` en carrito abierto |

## 4. Creatividades

- Registro: promesa del evento en una frase, 3 aprendizajes concretos, quién lo imparte, fecha/hora, "plazas"/"directo" solo si es verdad.
- Recordatorio: "mañana 19:00", bonus por asistir en directo.
- Carrito: testimonios, desglose de la oferta, objeciones, FAQ, cierre real.
- Retargeting de no asistentes: replay limitado.

## 5. Métricas y umbrales

| Métrica | Fórmula / umbral |
|---|---|
| Coste por registro | Diagnóstico |
| Show rate | Asistentes en directo / registros (separar replay) |
| **Coste por asistente** | Inversión / asistentes → comparar con el máximo |
| % permanencia hasta la oferta | De la plataforma |
| % compra o aplicación por asistente | Clave del presentador/oferta |
| Cash a 7 y 30 días por cohorte | Decisión de reinversión |

## 6. Ejemplos numéricos

**A) Coaching 10.000 € con aplicación tras el webinar:** show 30%, 12% de asistentes aplica, 60% agenda, 70% show de llamada, 25% cierre; contribución 4.603 €/venta.
- BE coste por registro **17,40 €**, target 8,70 €; con show 20%, BE 11,60 €.
- 15.000 € a 10 €/registro → 1.500 registros → 450 asistentes (33,3 €/asistente) → 54 aplicaciones → 32,4 agendas (463 €/agenda) → 22,7 shows → **5,67 ventas**, CPA 2.646 €, contribución 26.100 € → **beneficio 11.100 €**.

**B) Curso 497 € con venta en el webinar:** contribución 336,3 €; 5% de asistentes compra → BE por registro 3,36 € (show 20%), 4,20 € (25%), 5,88 € (35%); con replay +10 pp, 5,04 €.

## 7. Calendario tipo de un lanzamiento de 4 semanas

| Día | Acción |
|---|---|
| D-28 a D-21 | Calculadora (coste por asistente máximo); página de registro; webhooks de asistencia → CAPI; secuencia de recordatorios (email + WhatsApp) |
| D-21 | Lanzar campaña de registro (Advantage+, 4-6 anuncios); presupuesto estable |
| D-14 | Revisar coste por registro y % confirmación por anuncio; nuevas creatividades si frecuencia alta |
| D-5 a D-1 | Campaña de recordatorio a registrantes; subir urgencia real ("plazas en directo", bonus de asistencia) |
| D0 | Evento; anuncio "empieza en 15 min" a registrantes; medir asistencia y permanencia |
| D0 a D+5 | Carrito abierto: retargeting a asistentes, registrantes, visitantes de venta; testimonios y objeciones; excluir compradores |
| D+5 a D+7 | Cierre con urgencia real; replay limitado |
| D+14 | Post-mortem por anuncio: coste por asistente, por venta, cash 7 días; decidir evergreen |

## 8. Reglas de decisión rápidas

- Coste por asistente > máximo a mitad de la fase de registro → cambiar ángulo/creatividad o recortar presupuesto (no esperar al evento).
- Show < 20% → revisar confirmación, recordatorios y franja horaria; considerar evergreen just-in-time.
- Carrito: si el retargeting a asistentes rinde, protege su presupuesto aunque el ROAS global del lanzamiento aún no se vea.

## 9. Errores frecuentes

- Juzgar por coste por registro y sorprenderse por la asistencia.
- Registro de 1 clic sin confirmación ni calendario.
- No excluir compradores del retargeting de carrito.
- Urgencia falsa (riesgo de política y de confianza).
- Cambiar presupuestos a diario en una campaña de registro de 10 días (learning).

## Preguntas abiertas

- Asistencia real de tráfico frío de Meta en webinars B2C en España.
- ¿Optimizar a asistencia supera a optimizar a registro? Sin estudios públicos.

## Fuentes clave

- `05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md`, `05-economia-funnel-lead-gen-calculadoras.md`
- [Webinar registration & attendance statistics 2026](https://stealthagents.com/research/webinar-registration-attendance-statistics-2026) (S05-046)
- [Webinar Conversion Rate Benchmarks](https://assetacademy.io/funnels/webinars/webinar-conversion-rate-benchmarks/) (S05-045)
- [Venture Harbour EverWebinar case](https://ventureharbour.com/boost-webinar-attendance-rate/) (S05-084)
