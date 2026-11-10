# Escenarios de validación A–E

> Última verificación: 2026-10-16 · Autor: agente principal · Propósito: comprobar que la base de conocimiento permite
> razonar casos completos con sus dependencias. No hay una única respuesta correcta: se explicita qué preguntaría, qué
> números haría, qué decidiría y qué cambiaría la decisión. Cálculos reproducibles con
> `python3 -I herramientas/economia.py leadgen` desde la raíz del proyecto (break-even, target y simulación).

---

## A) Curso de 2.000 € · 100 €/día · leads → llamadas → ventas

### Lo que preguntaría primero (cambia la respuesta)
1. ¿Precio con IVA? ¿Cuánto se cobra al contado vs en cuotas? ¿Impagos y reembolsos?
2. ¿Quién vende? Comisiones de closer/setter. ¿Cuántas llamadas puede atender el equipo?
3. ¿Tasas reales del funnel (cualificación, agenda, show, cierre) o son supuestos?
4. ¿De qué trata el curso? Si es "ganar dinero", "negocio online", trading o IA para facturar → riesgo de política alto.
5. ¿Hay histórico de ventas orgánicas o de lista? (prueba social, ángulos que ya venden).

### Números (supuestos explícitos)
Oferta: 2.000 € IVA incl., 60 % al contado, 4 cuotas con +10 %, 15 % de impago en cuotas, 8 % de reembolsos, pasarela
3 %, entrega 10 %, closer 10 %, setter 5 % → **contribución ≈ 1.070 € por venta**.

| Funnel | Lead→venta | CPL break-even | CPL target (50 % margen) | Coste por llamada agendada BE/target |
|---|---|---|---|---|
| Base (40 % cualif · 50 % agenda · 60 % show · 15 % cierre) | 1,8 % | **19 €** | 10 € | 96 € / 48 € |
| Mejorado (50 % · 60 % · 75 % · 20 %) | 4,5 % | **48 €** | 24 € | 161 € / 80 € |

Simulación con 3.000 €/mes:

| CPL | Leads | Ventas (base) | Beneficio tras ads (base) | Ventas (mejorado) | Beneficio (mejorado) |
|---|---|---|---|---|---|
| 15 € | 200 | 3,6 | +853 € | 9,0 | +6.632 € |
| 25 € | 120 | 2,2 | −688 € | 5,4 | +2.779 € |
| 40 € | 75 | 1,4 | −1.555 € | 3,4 | +612 € |

**Lectura**: a este precio, vender por llamada es frágil. **El funnel post-lead pesa más que el CPL**: pasar del funnel
base al mejorado multiplica el CPL pagable ×2,5. Antes de gastar más en anuncios, trabajar show rate (recordatorios,
cita en <48 h) y cierre. **[STRONG INFERENCE]**

### Plan
- **Arquitectura**: 1 campaña Leads, 1 ad set, Advantage+ (audience + placements), España (o mercados hispanohablantes con
  economía propia). Nada de retargeting separado ni campaña de test.
- **Destino**: instant form **Higher intent** con 3–4 preguntas de opción múltiple que cualifican (situación, objetivo,
  disponibilidad para empezar, compromiso con la llamada) y reserva embebida (Calendly/HighLevel) si se usa; o landing
  corta + aplicación + calendario. No preguntar ingresos, deudas ni salud. → [05/02](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md)
- **Evento**: Lead al inicio (es el único con volumen: 75–200/mes). Integrar **CRM → CAPI** desde el día 1 (lead ID, etapas
  cualificado/agendado/asistió/venta). En cuanto haya volumen y requisitos, pasar a *qualified leads* optimizando a
  "cualificado" o "agendado" (la etapa más profunda con volumen razonable; nunca la venta, con 3–9 al mes).
- **Creatividad**: 4–6 conceptos: profesor/founder explicando el método, testimonios de **proceso** (no de ingresos), demo
  del contenido, objeciones ("no tengo tiempo"), estático con oferta. Si el curso toca dinero: vender programa y proceso,
  no resultado económico. → [08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md)
- **Ventas**: llamada/WhatsApp en <5 min (×21 cualificación en el estudio clásico), recordatorios 24 h y 1 h, setter que
  filtra antes del closer.
- **Kill rules**: por coste por llamada agendada (target 48 € base) y por cohorte; anuncio sin lead tras 2–3× CPL target.

### Calendario de decisión
Semana 1–2: entrega, CPL, % cualificación. Semana 3–4: coste por llamada agendada y show. Mes 2: coste por venta de la
cohorte del mes 1 (3–9 ventas: decisiones de dirección, no de precisión). Con ~4 ventas/mes la estadística del CPA es
pobre: se gestiona con indicadores adelantados validados (coste por llamada asistida).

### Qué cambiaría la recomendación
- Cierre por llamada < 10 % o comisiones altas → probar **VSL + checkout directo** con plan de pagos (sin llamada) y
  optimizar a Purchase; o webinar.
- Si hay producto de entrada (27–97 €) que liquida el CPA → funnel low-ticket + llamada para upsell.
- Presupuesto < 50 €/día → la señal será muy escasa: evaluar mensualmente o subir presupuesto.

---

## B) E-commerce · 500 €/día

### Preguntas
AOV y margen real (COGS, envío, pasarela, devoluciones) · recompra/LTV por cohorte · tamaño del catálogo y hero products ·
¿el valor que recibe Meta lleva IVA? · % de clientes nuevos que exige el negocio · estacionalidad (estamos a mediados de
octubre: BFCM en 5 semanas).

### Números (supuestos)
AOV 85 € IVA incl. (70,25 € sin IVA), COGS 30 %, envío 6 €, pasarela 2 %, devoluciones 5 % → **CM1 ≈ 38 € (54 %)**.
Con location fee del 3 % en España: **CPA break-even ≈ 36,9 €**; **ROAS break-even ≈ 2,31 sobre valor con IVA** (1,91 sin
IVA). [Ver 06/05](../06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md).

| CPA | Compras/semana (3.500 €) | Contribución tras ads/semana |
|---|---|---|
| 25 € | 140 | ≈ +1.710 € |
| 30 € | 117 | ≈ +820 € |
| 35 € | 100 | ≈ +190 € |

Con CPA 30 € el negocio gana poco en primera compra: **la recompra decide** si se puede escalar.

### Plan
- **Arquitectura**: 1 campaña Sales con Advantage+ (campaign budget, audience, placements). 1 ad set; segundo ad set solo
  con propósito (p. ej. otro mercado con economía distinta). Si el KPI es nCAC: **Customer Lifecycle Strategy** "adquirir
  clientes nuevos" o exclusión de compradores; si importa la venta total, no excluir y vigilar **audience segments**.
- **Puja**: Highest volume → con ≥50 compras/semana y valores distintos, test de **Highest value** 3 semanas; ROAS goal
  solo con histórico estable.
- **Creatividad**: 10–20 anuncios activos de conceptos distintos (estático producto+texto, UGC, demo, comparativa,
  reseñas, founder); Advantage+ catalog ads dentro del mismo ad set si hay surtido. Lote nuevo semanal; herramienta
  *Creative testing* (≤20 %) para variantes.
- **Q4**: preparar creatividades y oferta BFCM ya; **budget scheduling** para los picos en vez de duplicar campañas;
  descuento compatible con margen (con 25 % de descuento la primera compra puede perder dinero); la 2.ª semana de
  diciembre fue la más cara en 2025 (+39 % coste por compra).
- **Medición**: MER y nCAC semanales; Ads Manager 7d click y 1d click; % de gasto en existentes; geo-holdout trimestral
  cuando haya volumen.

### Qué cambiaría
AOV < 40 € con margen bajo → bundles/upsell antes de escalar · recompra alta (suscripción, consumibles) → LTV permite pagar
más y no excluir existentes · catálogo grande → catalog ads con product sets por margen y value rules.

---

## C) Clínica dental local · 50 €/día

### Preguntas
¿Qué tratamiento queremos llenar? (revisiones/limpiezas vs ortodoncia invisible/implantes, 1.500–4.000 €) · radio real de
captación · capacidad de agenda y quién llama · ticket medio y tasa de aceptación de presupuestos · software de agenda
(¿exporta citas/asistencias?) · normativa sanitaria aplicable (publicidad sanitaria en España: consultar asesoría).

### Números (supuestos)
1.500 €/mes. CPL 15–30 € → 50–100 leads/mes. Supuestos: 70 % contactado, 55 % agenda primera visita, 75 % asiste, 35 %
acepta tratamiento de ticket medio 1.800 € con contribución 45 % (810 €). P(tratamiento | lead) ≈ 0,70 × 0,55 × 0,75 ×
0,35 ≈ 10 % → **CPL break-even ≈ 81 €** con la primera venta. Con CPL 25 €, cada euro invertido devuelve ≈ 3,2 € de
contribución si las tasas se cumplen. El cuello de botella suele ser **contactar y que asistan**, no el CPL.

### Plan
- **Política primero**: no preguntar por salud/síntomas en el formulario; no hooks que impliquen un atributo personal
  ("¿Te faltan dientes?", "¿Te avergüenza tu sonrisa?"); 18+ si es estético; cuidado con antes/después y claims;
  normativa española de publicidad sanitaria. Copy compliant: "Valoración de ortodoncia invisible en [barrio]: plan y
  presupuesto en la primera visita". → [08/07](../08-cuenta-politicas-seguridad/07-categorias-especiales-y-sensibles.md)
  Comprobar en Events Manager la categoría de la fuente de datos de la clínica: puede quedar como salud y bienestar
  (URLs recortadas, eventos de mitad/final de funnel bloqueados). Por eso conviene Lead de instant form (on-Meta) + etapas
  devueltas por CAPI CRM sin datos de salud, y en el formulario "servicio de interés" con opciones neutras, nunca síntomas.
- **Arquitectura**: 1 campaña Leads, 1 ad set, ubicación por radio/código postal realista (8–15 km urbano), Advantage+
  audience, placements automáticos.
- **Destino**: instant form Higher intent (nombre, teléfono, tratamiento de interés, franja horaria) + SMS/OTP; reserva
  embebida si la agenda lo permite. Alternativa: click-to-WhatsApp (en la UE la optimización a leads de CTWA no está
  disponible; se optimiza a conversaciones → filtrar con mensajes de bienvenida y preguntas rápidas).
- **Creatividad**: dentista real hablando a cámara, recorrido de la clínica, paciente explicando la experiencia (con
  consentimiento), estático con oferta de valoración y ubicación. 3–5 anuncios.
- **Oferta**: valoración/diagnóstico con valor claro; "gratis" sube volumen y baja calidad: si se usa, compensar con
  preguntas de cualificación.
- **Operativa**: llamada en <5 min en horario, recordatorio 24 h por WhatsApp, lista de espera para huecos.
- **Señal**: subir citas/asistencias/tratamientos al dataset por CAPI (CRM/offline). Si el dataset queda categorizado como
  salud, algunas optimizaciones lower-funnel pueden estar restringidas: no renombrar eventos para esquivarlo (riesgo de
  circunvención).
- **KPI**: coste por primera visita asistida y por tratamiento aceptado; ingresos por euro invertido (mensual).

### Qué cambiaría
Agenda llena → subir ticket (tratamientos de mayor valor) en vez de volumen · leads fuera de zona → revisar ubicación ("vive
en" vs "estuvo en") · muchos no-shows → señal/depósito o cita más próxima.

---

## D) SaaS B2B con demo

### Preguntas
ACV y margen bruto · ICP (pymes/profesionales vs enterprise de nicho) · ciclo de venta y tasas lead→demo→oportunidad→cierre ·
¿hay self-serve/trial? · CRM (HubSpot/Salesforce) y si guarda fbclid/ad_id · capacidad de SDRs.

### Cuándo Meta sí y cuándo no
**Sí** cuando el comprador es una persona identificable por problema más que por cargo (dueños de pyme, profesionales,
equipos pequeños) y el ACV permite un CAC de cientos o pocos miles de euros. **No como canal principal** para enterprise
de nicho con comité de compra (LinkedIn/ABM/outbound encajan mejor); Meta puede seguir aportando retargeting de cuentas
que ya nos conocen y awareness. → [05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md), [14/playbook-b2b](../14-playbooks/playbook-b2b.md)

### Números (supuestos)
ACV 6.000 € (500 €/mes), margen bruto 80 %, payback objetivo ≤12 meses → **CAC máx ≈ 4.800 €**. Demo agendada → asiste
70 % → cierra 20 % → **coste por demo agendada máx ≈ 672 €**; si el formulario de demo convierte a demo agendada un 40 %,
**CPL máx ≈ 270 €**.

### Plan
- **Evento**: no optimizar a descargas de lead magnets salvo que el CRM demuestre conversión a pipeline. Optimizar a
  **demo agendada** (Schedule) o a una etapa de CRM ≤28 días (SQL) vía CAPI con *qualified leads*.
- **Destino**: landing con propuesta de valor + formulario corto con email de empresa y tamaño, enrutado a calendario
  (o instant form Higher intent con email de trabajo). Enriquecimiento y routing en CRM.
- **Arquitectura**: 1 campaña Leads, 1 ad set Advantage+ en el país objetivo; restricciones solo si son de negocio
  (idioma, país). Presupuesto suficiente para ≥10–20 demos/mes (con 300–400 € por demo, 4.000–8.000 €/mes).
- **Creatividad**: demo del producto en pantalla, founder explicando el problema, caso de cliente con métricas de
  proceso, comparativa honesta, "para quién no es".
- **Medición**: pipeline y CAC payback por cohorte; atribución por UTM/ad_id en CRM + pregunta "¿cómo nos conociste?";
  coherencia con la ventana de 7 días (el cierre llega después: decidir con SQL/demos).
- **Self-serve**: si existe trial, optimizar a un evento de activación (no al registro vacío).

---

## E) Evento / webinar en dos semanas

### Preguntas
¿Gratuito o con entrada? · oferta posterior (precio, contribución) · tasas de asistencia y conversión de eventos
previos · plataforma (¿exporta asistentes?) · lista propia y orgánico.

### Números (supuestos)
Contribución por venta del programa 1.500 €; registro→asistencia 35 %; asistencia→llamada 15 %; show 70 %; cierre 25 % →
P(venta | registro) ≈ 0,92 % → **coste por registro break-even ≈ 13,8 €**, target ≈ 6,9 €. Juzgar por **cash**, no por CPL.

### Plan por fases
| Fase | Días | Campaña | Evento | Presupuesto |
|---|---|---|---|---|
| Registro | 1–12 | Leads (instant form o landing) o Sales si hay entrada | CompleteRegistration/Lead | Lifetime budget; 1 ad set Advantage+; 4–8 anuncios; budget scheduling para intensificar los últimos 3–4 días |
| Recordatorios | 10–14 | Pequeña campaña a registrados (vídeo del ponente, "mañana en directo") | Alcance/ThruPlay o engagement | 5–10 % del total; justificada por ser temporal |
| Recuperación | 11–14 | Visitantes que no se registraron | Registro | 5–10 % |
| Post-evento | 15–21 | Replay + oferta con fecha límite a registrados/asistentes | Lead cualificado/compra | Según cohortes |

Claves: SMS/WhatsApp/email de recordatorio (el show-up es la palanca principal); entrada de pago baja (p. ej. 7–27 €)
sube la asistencia y la calidad a costa de volumen; con 2 semanas el learning debe salir rápido → registro como evento
(volumen) y CAPI con eventos de asistencia y citas para futuras ediciones; nada de cambios diarios.

**Medición**: registros → asistentes (plataforma) → llamadas → shows → ventas → cash, por anuncio y por día de
registro. Lección típica: los registros tardíos asisten más; los tempranos necesitan más nurturing.

**Qué cambiaría**: evergreen (webinar automatizado) → campaña continua optimizando a registro y, con volumen, a etapas
CRM; lanzamiento con lista grande → más presupuesto a audiencias calientes durante la ventana de carrito abierto.
