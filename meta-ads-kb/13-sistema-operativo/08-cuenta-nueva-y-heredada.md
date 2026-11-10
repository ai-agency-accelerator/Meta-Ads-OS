# Frameworks de cuenta nueva (sin histórico) y cuenta heredada (años de datos)

> Última verificación: 2026-10-16 · Autor: agente principal · Base: [02/10-cuenta-nueva-vs-heredada](../02-estructura-campanas/10-cuenta-nueva-vs-heredada.md),
> [08/01-account quality](../08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md),
> [08/03-seguridad](../08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md),
> [08/04-pagos y límites](../08-cuenta-politicas-seguridad/04-pagos-facturacion-limites.md),
> [04-tracking](../04-tracking-atribucion-medicion/README.md).

## TL;DR

- **Cuenta nueva**: límites reales (1 ad account hasta confirmar pago, límite de gasto diario fijado por Meta que sube con
  historial y pagos, más escrutinio). No se puede "arrancar a escala". El "warm-up" con engagement es un mito; el sistema
  aprende el evento que le pides. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Cuenta nueva ≠ cuenta en blanco** si se conectan dataset y Página con historial: reutilizar SIEMPRE el dataset de la web.
  **[STRONG INFERENCE]**
- **Cuenta heredada**: el activo valioso no es la "edad", sino dataset limpio con años de eventos, listas de clientes,
  anuncios con prueba social, aprendizajes creativos y límites ya elevados. Pero arrastra **deuda técnica** por los cambios
  2025–2026 que hay que limpiar en la primera semana. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Primero entender, luego tocar**: en una cuenta heredada que funciona, la primera semana es de auditoría y medición, no
  de reestructuración. "Si funciona, no lo toques" sigue siendo un buen principio. **[EMPIRICAL]**

---

## A. Cuenta nueva (sin histórico)

### A.1 Semana 0 — cimientos (antes de gastar)

- [ ] Business Portfolio **a nombre del negocio**, 2FA/passkeys para todos, 2–3 personas con *full control* (nunca una sola),
      agencias/freelancers como **partners** y no como admins personales. → [08/03](../08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md)
- [ ] Verificación del negocio y del dominio; verificación de anunciante si aplica (productos financieros en España
      requieren verificación). Meta quiere que el 90 % de sus ingresos venga de anunciantes verificados a final de 2026.
      **[OFFICIAL META]**
- [ ] Método de pago principal + respaldo; entender el límite de gasto diario inicial.
- [ ] Página de Facebook y cuenta de Instagram conectadas, con contenido coherente (la Página/perfil también se revisa).
- [ ] Dataset (Pixel + CAPI) instalado y validado (ver [03-framework-lanzamiento](03-framework-lanzamiento.md) Fase 2).
- [ ] Landing conforme a políticas (claims, privacidad, contacto, sin cloaking).

### A.2 Semanas 1–4 — arranque

1. **Una campaña de conversión desde el día 1** (Sales o Leads) optimizando a un evento real (compra; o lead/lead
   cualificado si el presupuesto es modesto). **[EMPIRICAL]** (Loomer). Meta sugiere eventos más frecuentes si se
   predicen cero conversiones → **[CONTESTED]**; usar oferta de entrada antes que ATC/LPV.
2. 1 ad set, Advantage+, conceptos distintos según presupuesto: 2–4 hasta 100 €/día, 3–6 por encima
   ([09 §A.2](09-presupuesto-pequeno-y-grande.md), regla 3).
3. Presupuesto dentro del límite de gasto de Meta; subirlo gradualmente conforme el límite aumente (pagar a tiempo y gastar
   cerca del límite ayuda a que suba). **[OFFICIAL META]**
4. Cuidar el historial de cumplimiento: pocos rechazos, nada de claims agresivos al principio (el historial modula cuánta
   revisión recibe cada anuncio). **[OFFICIAL META]**
5. Construir activos de datos: listas de clientes (para exclusiones y audience labels), audiencias de engagement, eventos
   con valor correcto.
6. Decisiones con la regla de paciencia; primera lectura de viabilidad en semana 4.

### A.3 Qué NO hacer

- Comprar o alquilar cuentas "antiguas" (prohibido; puede tumbar todos los activos del dueño). **[OFFICIAL META]**
- Abrir varias ad accounts para "diversificar subastas" (overlap; Meta identifica al anunciante). **[OFFICIAL META]**
- Campañas de engagement/tráfico para "sazonar el píxel" (sin evidencia; entrena hacia clicadores). **[UNPROVEN]**
- Crear un píxel nuevo para "empezar limpio" si ya existe uno con historial (mito M58).

---

## B. Cuenta heredada (años de datos)

### B.1 Día 1–2 — accesos y riesgo

- [ ] ¿Quién es dueño de cada activo? (Portfolio, ad accounts, Páginas, IG, dataset, catálogos, dominios). Los activos deben
      ser del cliente.
- [ ] Usuarios y partners: eliminar accesos de ex-empleados/agencias; mínimo 2 *full control* del cliente; 2FA.
- [ ] Account Quality: restricciones, rechazos recientes, anuncios en revisión; historial de pagos y límite de gasto.
- [ ] Métodos de pago y facturación (incluidos location fees desde jul-2026 en UK/ES/FR/IT/AT/TR).

### B.2 Semana 1 — auditoría sin tocar

Aplicar el [framework de auditoría](02-framework-auditoria.md) completo. Prioridades específicas de cuentas heredadas en
2026 (deuda técnica por cambios de Meta):

| Deuda | Desde | Síntoma | Acción |
|---|---|---|---|
| Saved audiences con intereses consolidados/retirados | Ad sets sin corregir dejaron de entregar el 15-ene-2026 | Ad sets "activos" sin entrega | Rehacer con Advantage+ audience/sugerencias |
| Exclusiones de detailed targeting | Eliminadas (31-mar-2025) | Ad sets que "excluían" intereses ya no lo hacen | Sustituir por custom audiences de exclusión / exclusion-only audiences (ago-2026) |
| ASC/AAC legacy | Bloqueados (19-may-2026) y pausados (v26) | Campañas ASC paradas o no editables | Recrear como campaña Sales con Advantage+ |
| Existing customer budget cap | Retirado (2025) | — | Customer Lifecycle Strategy / exclusiones / estructura con max spend |
| Lookalikes por país | Countryless desde 1-sep-2026 (vía API) | LAL entregando fuera de lo esperado | Revisar ubicación del ad set |
| Placements manuales en ad sets de Sales/Leads/App (Engagement no; corrección 2026-11-09) | Retirándose desde ago–oct-2026 | Exclusiones que dejan de aplicarse | Exclusiones a nivel cuenta + value rules por placement + assets por placement |
| Qualified leads sin CAPI | Bloqueado en campañas nuevas (abr-2026) y afectadas las existentes (ago-2026) | Optimización de calidad caída | Integrar CRM → CAPI |
| Bid multipliers | Value rules los sustituyen (2027) | — | Migrar a value rules |
| Atribución | 7d/28d view fuera de la API (ene-2026); click = link click (mar-2026) | Dashboards con columnas vacías; ROAS histórico no comparable | Re-baseline y anotar discontinuidades |
| Breakdowns device/hour/frequency | Opt-in obligatorio (6-ago-2026) | Informes API vacíos | Activar "Additional Breakdowns" |
| Placements retirados (Explore feed, Messenger Stories/inbox) | 2025–2026 | Arrays de placements con valores inválidos (integraciones) | Limpiar integraciones |
| Advantage+ creative enhancements | Varias ON por defecto (2025–2026) | Texto reescrito en imágenes, música, traducciones | Auditar y decidir política |

**[OFFICIAL META]** en las fechas (ver [10/02-changelog-2026](../10-cambios-2025-2026-api-ia-automatizacion/02-changelog-2026.md)).

### B.3 Semana 2–4 — simplificar con cuidado

1. **No reestructurar lo que funciona** el primer mes; tocar primero lo roto (tracking, deuda técnica, fragmentación obvia).
2. **Consolidar** ad sets que persiguen el mismo objetivo con <50 eventos/semana cada uno (Meta lo recomienda con
   "Combine ad sets"/opportunity score). Hacerlo por fases y midiendo.
3. **Conservar** anuncios con prueba social (post IDs), audiencias de clientes y el dataset.
4. **Separar lo que mezcla economías distintas** (países, adquisición/retención) si los segments muestran canibalización.
5. **Retargeting heredado**: si existe, holdout antes de mantenerlo; su incrementalidad suele ser menor de lo que reporta.
6. **Teoría de la "cuenta limpia"** (abrir cuenta nueva porque la vieja "está quemada"): anecdótica y con confusores
   (estructura simple vs compleja). Primero simplificar la heredada. **[HYPOTHESIS]**

### B.4 Mes 2+ — usar el histórico como ventaja

- Analizar 12–24 meses: estacionalidad propia, ángulos/conceptos ganadores, curvas de fatiga, CPA marginal por nivel de gasto.
- Listas de clientes de alto valor → audience labels, value rules, value-based lookalikes (como sugerencia).
- Primer test de incrementalidad con volumen suficiente.

## C. Diferencias clave en una tabla

| Aspecto | Nueva | Heredada |
|---|---|---|
| Riesgo dominante | Límites de gasto, escrutinio, sin señal | Deuda técnica, fragmentación, retargeting inflado, accesos sin control |
| Primera semana | Cimientos + campaña de conversión simple | Auditoría sin tocar + seguridad |
| Datos | Construirlos | Limpiarlos y explotarlos |
| Ritmo de cambios | Lento por falta de señal | Lento por respeto a lo que funciona |
