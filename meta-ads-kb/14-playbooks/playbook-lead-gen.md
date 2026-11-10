# Playbook: Lead generation para servicios (genérico)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: negocios que venden un servicio tras contactar al lead (presupuestos, visitas, consultas, matrículas). Base de conocimiento: `05-leadgen-high-ticket-crm/` (archivos 01-09). Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Usa Meta cuando** tu cliente se puede describir por problema/situación y la demanda no es solo de búsqueda (si la gente ya busca "fontanero urgente", Google va primero). **[STRONG INFERENCE]**
- **Evento:** empieza con *Maximize leads* solo mientras montas la integración; en cuanto tengas CAPI CRM, pasa a **Maximize number of qualified leads** con la etapa "cualificado" o "visita/cita agendada". Desde abril de 2026 qualified leads exige integración CAPI en campañas nuevas. **[OFFICIAL META]** (S05-007)
- **Formulario:** instant form **Higher intent + SMS verification + 3-5 preguntas de opción múltiple** (zona/código postal, tipo de servicio, plazo, capacidad) + intro con "qué pasa después". **[OFFICIAL META]** + **[STRONG INFERENCE]** (S05-009, S05-010, S05-013)
- **Proceso:** contacto <5 min, 6 intentos en 48-72 h, cita en ≤72 h; sin esto ninguna campaña "da leads buenos". **[EMPIRICAL]** (S05-037, S05-038)
- **Métrica de decisión:** coste por cita/visita y por venta según tu calculadora (archivo 05), nunca el CPL solo.

---

## 1. Cuándo usar Meta (y cuándo no)

| Sí | No / con cuidado |
|---|---|
| Servicio con dolor latente (no urgente) que se activa con un buen anuncio: placas solares, reformas, academias, clínicas, seguros (categoría especial) | Urgencias puras → Google/llamadas primero; Meta como apoyo con call ads |
| Ticket o LTV que soporta un CPL de 15-150 € | Ticket bajo sin recurrencia (el CPL no cabe) |
| Equipo capaz de contactar en minutos | Equipo que llama "cuando puede" |

## 2. Arquitectura por presupuesto

| Presupuesto/mes | Estructura | Notas |
|---|---|---|
| < 1.500 € | 1 campaña Leads (Advantage+ por defecto), 1 ad set, 3-6 anuncios, 1 formulario Higher intent | Ad scheduling en horario de respuesta |
| 1.500-6.000 € | + 1 campaña de testing creativo (ABO pequeño o ad set separado) | Qualified leads en la principal cuando haya ≥20-30 eventos/semana de la etapa |
| 6.000-25.000 € | Prospección consolidada + retargeting (abrió formulario y no envió, visitantes web) + test de canal (WhatsApp o landing) | Breakdown por placement en coste por cita antes de tocar exclusiones de cuenta |
| > 25.000 € | Varias ofertas/zonas; capacidad comercial como límite | Contratar setters antes de subir presupuesto |

Advantage+ leads es el modo por defecto: ubicación, edad mínima, idiomas y exclusiones de custom audiences son **controles**; edad máxima, género, intereses y audiencias son **sugerencias**. (S05-066, S05-086)

## 3. Evento de optimización (decisión)

1. Sin CRM integrado → Maximize leads + filtros (SMS, Higher intent) **y** monta la integración en la primera semana (Make/Zapier).
2. Con CAPI CRM → Qualified leads; etapa objetivo = la más profunda con 1-40% de conversión, ≤28 días y ≥~50 eventos/semana (o lo más cercano posible). (S05-001, archivo 03)
3. Funnel web → `Lead` → `Schedule`/evento CRM; probar Sequenced Events cuando aparezca.

## 4. Creatividades

- Ángulos por **situación del cliente** ("factura de luz > 150 €/mes", "baño de más de 20 años"), no por demografía.
- Prueba local: casos de la zona, fotos reales, nombre del barrio/ciudad (ayuda a filtrar geografía, S05-081).
- Oferta concreta: "estudio gratuito en 48 h", "presupuesto cerrado", "visita sin compromiso".
- Filtros en el copy: "solo [zona]", "viviendas unifamiliares", "desde X €".
- 3-6 anuncios por ángulo; renovar cuando suba la frecuencia y caiga el coste por cita (área 03).

## 5. Funnel y proceso

```
Anuncio → instant form (Higher intent + SMS + preguntas) → ending: WhatsApp/booking
→ CRM en <1 min → WhatsApp automático + llamada <5 min → cualificación → cita/visita (≤72 h)
→ confirmación + recordatorios 24 h/2 h → visita → presupuesto → seguimiento → venta
→ etapas a Meta (CAPI CRM) + informe por anuncio
```

## 6. Métricas y umbrales

| Métrica | Fuente | Umbral de acción |
|---|---|---|
| CPL | Ads Manager | Solo diagnóstico; si sube >30% sin cambio en coste por cita, no actuar |
| % contactado en 1 h | CRM | < 60% → problema de proceso, no de campaña |
| % cualificado | CRM | Caída >10 pp en una semana → revisar anuncio/placement/formulario |
| Coste por cita | CRM | > BE durante 2 semanas con ≥10 citas esperadas → pausar/cambiar ángulo |
| Show de visitas | CRM | < 70% → confirmaciones, plazo de cita |
| Coste por venta (cohorte madura) | CRM | > target → revisar oferta/precio/cierre |
| Cobertura CAPI CRM | Events Manager | < 60% → revisar lead ID y envío del raw lead |

## 7. Ejemplo numérico: placas solares (7.000 € IVA incl.)

Supuestos: margen bruto 30% (coste de instalación 70%), comisión comercial 5% → **contribución 1.446 €/venta**. Funnel: 65% contactado y cualifica, 40% acepta visita técnica, 85% asiste, 35% compra → lead→venta 7,74%.
- **BE CPL 111,87 €; target (50%) 55,93 €.** BE por visita agendada 430 €, target 215 €.
- Con 5.000 € a CPL 30 €: 167 leads → 108 cualificados → 43 visitas → 37 celebradas → **12,9 ventas**, CPA 388 €, coste por visita 115 €, contribución 18.645 € → beneficio 13.645 €.
- **Estrés** (leads de peor calidad: 45% cualifica, 30% visita, 80% show, 30% cierre → lead→venta 3,24%): **BE CPL cae a 46,85 €**. Con CPL 30 € sigue siendo rentable, con CPL 50 € ya no. Por eso hay que vigilar % cualificado y % visita por anuncio, no solo el CPL.

## 8. Plan de arranque (primeros 30 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 (preparación) | Calculadora con tu economía (BE/target por cita y CPL); CRM conectado a lead ads; campo `meta_lead_id`; tracking parameters; SLA de respuesta; formulario Higher intent + SMS | Lead de prueba (Lead Ads Testing Tool) llega al CRM en <1 min con IDs |
| 1 | Lanzar 1 campaña, 3-6 anuncios de 2-3 ángulos, Maximize leads; integrar CAPI CRM (Make/Zapier/nativo) enviando la etapa inicial y las siguientes con los nombres del contrato §16 (`docs/desarrollo/contratos.md`: `Lead`, `LeadCualificado`, `Schedule`…) | ≥60% de leads con `Lead` desde el CRM en Events Manager |
| 2 | Revisar % contactado, % cualificado y coste por cita por anuncio; pausar anuncios con 0 citas tras ≥2× su coste por cita objetivo | Coste por cita medio ≤ BE |
| 3 | Si la etapa objetivo tiene ≥20-30 eventos/semana: duplicar a Maximize qualified leads (no editar la original) | Cobertura y diagnóstico del dataset en verde |
| 4 | Comparar qualified leads vs maximize leads en coste por cita/venta; nuevo lote de creatividades desde objeciones reales | Decidir campaña principal; escalar +20-30% cada 3-4 días si coste por cita < target |

## 9. Reglas de decisión rápidas

- Coste por cita < target y capacidad comercial libre → escalar.
- CPL baja pero % cualificado cae >10 pp → revisar placement/anuncio/formulario antes de celebrar.
- % contactado en 1 h < 60% → parar de escalar y arreglar el proceso.
- Coste por cita > BE durante 2 semanas con muestra suficiente → cambiar ángulo/oferta, no solo el presupuesto.

## 10. Errores frecuentes

- More volume + autofill + Maximize leads en un servicio con visita técnica.
- Descargar CSVs y llamar al día siguiente (los leads caducan a 90 días y el interés en horas).
- No preguntar zona/código postal (leads fuera de área por "recently in" y radio mínimo).
- Escalar por CPL mientras el comercial se queja de "basura".
- Cambiar de dataset CRM al cambiar de proveedor (reinicia aprendizaje).

## Preguntas abiertas

- Efecto de la retirada de exclusiones de placement por ad set (ago-oct 2026) en la calidad media de leads de servicios en España.

## Fuentes clave

- Archivos `05-leadgen-high-ticket-crm/01` a `09`.
- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) — meta-oficial (S05-007)
- [Enable SMS verification](https://www.facebook.com/business/help/898260175547909) — meta-oficial (S05-010)
- [InsideSales/MIT Lead Response Management Study](https://www.mortech.com/hs-fs/hub/25649/file-13535879-pdf/docs/mit_study.pdf) — 2007 (S05-037)
