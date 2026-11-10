# Escenarios de validación F–J

> Última verificación: 2026-10-16 · Autor: agente principal · Continúa [01-casos-A-E](01-casos-A-E.md).

---

## F) Cuenta que gasta 5.000 €/día y quiere escalar

### Preguntas
¿Qué significa "escalar"? (más revenue, más clientes nuevos, más beneficio) · economía (CPA break-even, LTV, caja) ·
evolución del CPA al subir gasto en los últimos meses · % del gasto en clientes existentes/engaged (audience segments) ·
¿hay medición incremental? · pipeline creativo (anuncios nuevos/semana, hit rate) · capacidad (stock, equipo) ·
estructura actual · calendario (estamos a 16-oct: Q4 llega con CPM +35–57 % en BFCM).

### Cómo lo pensaría (números de ejemplo)
Últimos escalones de gasto semanal (misma estacionalidad):

| Semana | Gasto | Compras | CPA medio | CPA incremental del escalón |
|---|---|---|---|---|
| Base | 35.000 € | 700 | 50,0 € | — |
| +10 % | 38.500 € | 740 | 52,0 € | **87,5 €** |
| +9 % | 42.000 € | 770 | 54,5 € | **116,7 €** |

El CPA medio "solo" sube un 9 %, pero **cada compra extra cuesta 87–117 €**. Si el CPA break-even es 70 €, el segundo
escalón destruye valor aunque Ads Manager se vea "bien". **Escalar presupuesto aquí no es la palanca**. **[STRONG INFERENCE]**
→ [09/03](../09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md)

### Plan
1. **Medir antes de empujar**: curva gasto→conversiones (log-log) con 8–12 semanas; audience segments; geo-holdout o
   Conversion Lift para conocer el iROAS real del último tramo.
2. **Si hay margen marginal** (CPA incremental < break-even): escalones de 15–30 % cada semana en la campaña evergreen,
   budget scheduling para picos de Q4, evaluar cada escalón con CPA incremental en semana madurada.
3. **Si no hay margen marginal**: escalar por **creatividad** (de 10 a 20–50 anuncios nuevos/semana con diversidad real;
   graduación y campaña de underspend), **inventario nuevo** (países con economía propia, nuevos productos/ofertas,
   placements con assets nativos 9:16), **señal** (value optimization, value rules por margen, CAPI con margen/LTV) y
   **oferta** (bundles, AOV).
4. **Pujas**: proteger el margen del tramo marginal con ROAS goal o cost per result goal en parte del presupuesto
   (recordando que de media entregan ~96,5 % y ~140 % del objetivo en el dataset de CTC); bid cap con presupuesto inflado
   solo con disciplina de vigilancia.
5. **Retención vs adquisición**: si >30–40 % del gasto va a existentes con baja incrementalidad → CLS/exclusiones o
   campaña de retención con su propia economía.
6. **Riesgo**: admins de respaldo, métodos de pago, cumplimiento; con este gasto una restricción cuesta mucho.

### Qué cambiaría
Negocio con LTV alto demostrado y caja → aceptar CPA de primera compra mayor · mercado único saturado → expansión
geográfica antes que presupuesto · creatividad limitada → invertir primero en producción.

---

## G) Muchas leads pero pésima calidad

### Diagnóstico (árbol 4 de [13/07](../13-sistema-operativo/07-framework-diagnostico.md))
1. **Definir "pésima"** con datos: % contactables, % cualificados, % que agendan, por campaña/anuncio/formulario/placement/
   edad/país (cohortes de 2–4 semanas).
2. **Causas probables por orden**:
   - Optimización a "Lead" bruto con formulario "More volume" y autofill → el sistema busca rellenadores de formularios.
   - Creativo/oferta de curiosidad o "gratis" → atrae a quien no compra.
   - Segmentos de baja calidad (placements como Audience Network en algunas cuentas, edades fuera del ICP, países).
   - Bots/spam (teléfonos inválidos, patrones repetidos).
   - **Ventas** que tardan horas en llamar: el lead "malo" a veces es un lead frío por lentitud.

### Acciones (por impacto)
1. **Formulario**: Higher intent + 3–5 preguntas de opción múltiple que cualifican (necesidad, plazo, tipo de cliente);
   SMS/OTP; context card que diga para quién NO es y que habrá una llamada. Nada de ingresos, deudas o salud; preguntar
   por el presupuesto del proyecto/servicio es práctica común, pero revisar la política antes (no confundir con
   preguntar la situación financiera personal). → [05/02](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md)
2. **Señal**: CRM → CAPI con etapas (cualificado, agendado, asistió, venta) y *qualified leads* (obligatorio vía CAPI desde
   abr-2026); value rules para bajar puja en segmentos con calidad demostradamente mala.
3. **Creatividad pre-cualificadora**: decir precio o rango, requisitos, proceso; ángulos de dolor real en lugar de curiosidad.
4. **Placements/segmentos**: con la retirada de exclusiones a nivel de ad set (Leads), usar exclusiones a nivel de cuenta
   o value rules solo con evidencia de cohortes (no por intuición: *breakdown effect*).
5. **Ventas**: speed to lead <5 min y secuencia de contacto; medir contactabilidad antes de culpar a Meta.
6. **KPI**: coste por lead cualificado y por cita asistida; aceptar CPL más alto si baja el coste por venta.

---

## H) Buen CTR pero CPA malo

### Primero: ¿qué optimiza la campaña?
Si el objetivo es Tráfico/LPV/engagement, **esa es la causa**: Meta encontró clicadores. Pasar a Sales/Leads con el evento
real. **[OFFICIAL META]** (el performance goal define qué se busca)

### Si ya optimiza a conversión
Descomponer: CPA = CPM / (1.000 × CTR × CVR). CTR alto con CPA malo ⇒ **CVR baja** (o CPM muy alto).
1. **LPV rate** (LPV / link clicks) bajo → web lenta, clics accidentales (placements), redirecciones.
2. **Message match**: la promesa del anuncio no es lo que ve el usuario (precio sorpresa, oferta distinta, producto
   distinto) → alinear anuncio y landing above the fold.
3. **Calidad del tráfico**: hook de curiosidad/polémica → muchos clics sin intención. Mirar ATC/IC rate, tiempo en página,
   y CVR de Meta frente a la de otros canales en la misma landing.
4. **Checkout/funnel**: si ATC es bueno y compra no → coste de envío, métodos de pago, fricción, confianza.
5. **Tracking**: ¿el evento final se registra bien en ese recorrido? (dominio distinto, `fbclid` perdido, dedup).
6. **Muestra**: ¿hay suficientes conversiones esperadas como para concluir? (con 3 esperadas, 0 ocurre un 5 % de las veces).
Acción: no escalar por CTR; arreglar post-clic o cualificar la promesa, conservando lo que hace que el hook pare el scroll.

---

## I) Buen ROAS en Ads Manager pero el negocio pierde dinero

### Ejemplo numérico (supuestos)
Gasto 10.000 €; ROAS de Meta 3,0 sobre valor **con IVA** → 30.000 € atribuidos → 24.793 € netos de IVA. Margen de
contribución 45 %, devoluciones 8 %, location fee 3 %. Si solo el **60 %** de lo atribuido es incremental:
contribución incremental ≈ 24.793 × 0,6 × 0,92 × 0,45 ≈ **6.160 €** frente a un coste de **10.300 €** → **−4.140 €**.

ROAS break-even (sobre valor con IVA, sin ajustar incrementalidad) = 1,21 × 1,03 / (0,45 × 0,92) ≈ **3,0** → el "buen"
ROAS 3,0 ya era break-even antes de mirar incrementalidad; ajustado al 60 % incremental, el break-even real es **≈ 5,0**.

### Checklist
1. **Base del valor**: ¿IVA, envío, descuentos incluidos? ¿devoluciones y cancelaciones restadas? (Meta no las resta).
2. **Duplicados** en eventos de compra (dedup, emisores dobles) → valor inflado.
3. **Incrementalidad**: % de conversiones de clientes existentes/engaged (segments), retargeting, view/engage-through;
   holdout o geo-test. El retargeting/BOF es donde más se infla (Haus); Advantage+ sobre-reporta ~12 pp frente a manual.
4. **Doble conteo entre canales**: la suma de lo reclamado por plataformas supera las ventas.
5. **Coste marginal** del último tramo de gasto.
6. **Costes ocultos**: fees por país, agencia, creatividad, devoluciones, chargebacks.
### Decisión
Gestionar con **MER, contribución y nCAC**; fijar el target de ROAS de plataforma a partir del break-even real y de un
factor de incrementalidad medido; reasignar presupuesto de retargeting/existentes a adquisición si el test lo confirma.

---

## J) Tracking roto después de una actualización

### Protocolo ([04/16 §4](../04-tracking-atribucion-medicion/16-checklist-qa-y-diagnostico-tracking.md))
1. **Congelar decisiones de rendimiento**: con la señal rota, el CPA de Ads Manager no significa nada; no apagar campañas
   por "CPA disparado".
2. **Cuantificar**: eventos recibidos en Events Manager (navegador vs servidor) vs backend, desde la fecha del cambio.
3. **Delimitar qué cambió**: deploy web, tema/plugin/app, checkout (Shopify: scripts adicionales de la thank-you page en
   solo lectura), CMP de consentimiento, CSP, dominio/CDN, token de CAPI, versión de API (v24 expiró el 6-oct-2026; las
   retiradas de v26 llegan a todas las versiones el 27-oct-2026), sGTM.
4. **Ramas**: solo navegador ↓ → Pixel; solo servidor ↓ → CAPI; ambos ↓ → dataset/dominio/consentimiento/restricción de
   categoría; volumen OK pero Ads Manager ↑ → dedup rota (`event_id` dejó de coincidir) → duplicados.
5. **Corregir una cosa cada vez**, validar con Test Events y una compra real, monitorizar 72 h.
6. **Después**: anotar el periodo afectado en el change log y en los informes; la entrega puede tardar 1–2 semanas en
   normalizarse (el sistema aprendió con señal incompleta); no "reiniciar campañas" ni crear un píxel nuevo.
7. **Prevención**: checklist de QA en cada release; alerta automática si el evento principal cae por debajo de la banda
   de ruido; responsable único del tracking.

---

## Autoevaluación: dependencias que estos casos ponen a prueba

| Dependencia | Casos |
|---|---|
| Economía → target → criterio de decisión | A, B, C, D, E, I |
| Evento de optimización ↔ calidad de negocio | A, D, G, H |
| Funnel post-clic y ventas > CPL | A, C, E, G |
| Estructura según volumen | A, B, C, F |
| Coste marginal e incrementalidad | B, F, I |
| Tracking como prerequisito | I, J |
| Políticas como restricción de diseño | A, C |
| Calendario/estacionalidad | B, E, F |
