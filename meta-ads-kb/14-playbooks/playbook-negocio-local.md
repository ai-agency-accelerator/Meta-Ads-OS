# Playbook: Negocio local (clínicas, estética, reformas, academias, servicios a domicilio, urgencias)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: negocios que atienden en una zona geográfica y venden con cita, visita o llamada. Base: `05-leadgen-high-ticket-crm/01`, `02`, `08`, `10`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Canal según urgencia:** urgencias → call ads (con alguien al teléfono); citas → instant form Higher intent + SMS + reserva embebida o WhatsApp; presupuestos → instant form con código postal y tipo de proyecto. **[STRONG INFERENCE]**
- **La geografía se escapa:** Meta solo ofrece "living in or recently in"; radio mínimo de ciudad +10 millas, por defecto +25; location expansion puede estar activa. Pregunta código postal, menciona la zona en el anuncio y revisa el breakdown geográfico. **[EMPIRICAL]** (S05-081, S05-092)
- **Mide la cita y la venta y devuélvelas a Meta** (CAPI CRM; la Offline Conversions API ya no existe). Si no tienes CRM, hoja + Make (gratis hasta 2028). **[OFFICIAL META]** + **[EMPIRICAL]** (S05-052, S05-030)
- **Clínicas:** prohibido preguntar por salud en el formulario. **[OFFICIAL META]** (S05-016)
- **Ejemplo:** clínica estética, tratamiento 600 € → BE CPL 50 € con la primera venta, 110 € con LTV de 2,2 visitas. **[STRONG INFERENCE]**

---

## 1. Cuándo usar Meta

| Sí | Con cuidado |
|---|---|
| Servicio "deseable" que se activa con un anuncio (estética, dental estético, fitness, academias, reformas, solar) | Urgencias (la demanda está en búsqueda) |
| Zona con población suficiente (radio pequeño = audiencia pequeña) | Pueblos pequeños con radio mínimo grande |
| Capacidad de atender leads en el día | Negocio que no coge el teléfono |
| Categorías especiales (financiación, inmobiliaria, empleo) → restricciones de radio/edad/lookalikes | Ver área 08 |

## 2. Arquitectura por presupuesto

| Presupuesto/mes | Estructura |
|---|---|
| 300-1.000 € | 1 campaña Leads, 1 ad set (ubicación como control, expansión desactivada), 3-5 anuncios, 1 formulario; ad scheduling en horario |
| 1.000-4.000 € | + call ads o WhatsApp como segundo canal; retargeting de quien abrió el formulario |
| 4.000-15.000 € | Varias sedes/zonas (un ad set o campaña por zona si los presupuestos y la capacidad difieren); qualified leads con "asistió a la cita" |

## 3. Evento de optimización

- Instant form: Maximize leads al principio → **qualified leads** (cita agendada o asistió) cuando el CRM/agenda envíe etapas.
- Calls: Calls (y llamadas largas si la opción existe en tu cuenta, **[HYPOTHESIS]** S05-083).
- WhatsApp: leads through messaging o Leads con destino WhatsApp; en instant forms, "Meta source + Leads with WhatsApp conversations" si está disponible. (S05-007)

## 4. Formulario recomendado (citas/presupuestos)

1. Código postal o barrio (filtra fuera de zona).
2. Servicio de interés (opción múltiple).
3. ¿Cuándo quieres empezar? (esta semana / este mes / informándome).
4. Preferencia de contacto + franja (WhatsApp/llamada).
5. Nombre + teléfono (SMS verification) + email.
Intro: "Te escribimos por WhatsApp en menos de 15 minutos (L-V 9-20 h)". Ending: reserva embebida (Calendly/HighLevel, solo Facebook) o "Chat on WhatsApp". (S05-059, S05-010)

## 5. Creatividades

- Caras reales del equipo y del local; antes/después **permitidos** según la política de cada vertical (área 08).
- Mención explícita de la zona ("en Valencia", "a 5 min de…").
- Oferta concreta (primera consulta, valoración gratuita, precio cerrado).
- Prueba local: reseñas de Google, casos de vecinos.

## 6. Métricas y umbrales

| Métrica | Umbral |
|---|---|
| % leads fuera de zona | > 10% → revisar expansión, radio, copy |
| % contactado en 1 h | ≥ 70% |
| Lead → cita | Comparar contra el supuesto de tu calculadora |
| Show de citas | ≥ 70-80% con recordatorios (sanidad: 0% no-show en datos de scheduler B2B, pero en citas de pacientes ~23% de media en meta-análisis; S05-089) |
| Coste por cita y por cliente | Contra BE/target |

## 7. Ejemplos numéricos

**A) Clínica estética, tratamiento 600 € IVA incl.**, coste de entrega 40%, pasarela 1,5% → **contribución 288,5 €** primera venta; LTV 2,2 visitas → 634,7 €. Funnel: 70% contactado, 55% agenda, 75% asiste, 60% compra → lead→venta 17,3%.
- BE CPL **50 €** (primera venta) / **110 €** (LTV). Si la caja manda, decide con 50 €; si tienes datos de recurrencia de ≥6 meses, puedes pagar más.

**B) Cerrajero 24 h (call ads)**, servicio medio 120 € IVA incl., margen 60% → contribución 59,5 €.
- Coste por llamada máximo = contribución × % llamadas atendidas × % que se convierten en servicio: 80% × 50% → **23,80 €**; si solo atiendes el 60% → 17,85 €; si convierte el 35% → 16,66 €. Coger el teléfono vale tanto como la campaña.

## 8. Plan de arranque (primeros 30 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 | Calculadora (primera venta y LTV); agenda/CRM con origen del lead; formulario con código postal + servicio + plazo + SMS; ubicación como control, expansión desactivada; ad scheduling en horario | Lead de prueba llega al móvil del responsable en <1 min |
| 1 | 1 campaña, 3-5 anuncios con la zona en el copy; respuesta por WhatsApp <5 min | % fuera de zona < 10% |
| 2 | Medir lead→cita y show; añadir reserva embebida o enlace de agenda si la cita se pierde en la conversación | Coste por cita ≤ BE |
| 3-4 | Conectar CAPI CRM (Make/Zapier) con etapas cita/asistió/compró; probar call ads o WhatsApp como segundo canal | Coste por cliente ≤ target |

## 9. Reglas de decisión rápidas

- Muchos leads fuera de zona → expansión, radio, copy, pregunta de código postal (en ese orden).
- Citas que no asisten → recordatorio humano la víspera y citas en ≤72 h.
- Si el negocio no puede atender más citas, no escales: sube precio o filtra más.

## 10. Errores frecuentes

- Radio por defecto + expansión activada → leads a 40 km.
- Preguntar por síntomas o salud (prohibido).
- Leads a las 23:00 sin respuesta hasta el día siguiente (programar anuncios o responder automáticamente).
- No registrar asistencia real a la cita (no puedes optimizar ni saber qué anuncio trae clientes).

## Preguntas abiertas

- Radio mínimo efectivo en España para pins/coordenadas en 2026.
- Disponibilidad de optimización a llamadas largas.

## Fuentes clave

- `05-leadgen-high-ticket-crm/10-b2b-saas-local.md`
- [4 Reasons Meta Ads Reach People Outside of the Targeted Location](https://www.jonloomer.com/meta-ads-reach-people-outside-of-the-targeted-location/) — 2025-03-31 (S05-081)
- [Questions prohibited on your instant form](https://www.facebook.com/business/help/219356599612120) (S05-016)
- [Meta launches integrated booking for lead ads](https://www.socialmediatoday.com/news/meta-launches-integrated-booking-for-lead-ads/823711/) — 2026-06-24 (S05-059)
