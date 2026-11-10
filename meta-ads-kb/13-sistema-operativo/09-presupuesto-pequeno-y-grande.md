# Frameworks de presupuesto pequeño (≤100 €/día) y grande (≥5.000 €/día)

> Última verificación: 2026-10-16 · Autor: agente principal · Base: [02/06-presupuesto-por-niveles](../02-estructura-campanas/06-presupuesto-por-niveles.md),
> [02/05-arquitectura](../02-estructura-campanas/05-arquitectura-de-campanas.md), [06/06-arquitectura ecommerce](../06-ecommerce-apps/06-arquitectura-ecommerce-por-presupuesto.md),
> [09/03-escalado](../09-bidding-escalado-economia-analitica/03-escalado-tipos-y-condiciones.md), playbooks en [14](../14-playbooks/).

## TL;DR

- **Pequeño (50–100 €/día)**: el enemigo es la falta de señal. 1 campaña, 1 ad set, Advantage+, evento real, 3–8 anuncios
  de conceptos distintos, nada de retargeting separado ni campañas de test, decisiones semanales/quincenales. El mayor
  apalancamiento está en oferta, landing y velocidad comercial, no en la estructura. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Grande (≥5.000 €/día)**: el enemigo es el coste marginal y lo no incremental. Portfolio de campañas con razón de
  negocio (mercado, adquisición/retención, momentos), mezcla de pujas, testing industrializado, medición con lift/geo/MMM.
  **[EMPIRICAL]**
- **La complejidad debe venir de la heterogeneidad del negocio, no del tamaño del presupuesto.** **[STRONG INFERENCE]**

---

## A. Framework de presupuesto pequeño (≤100 €/día ≈ ≤3.000 €/mes)

### A.1 Matemática de partida

Eventos/semana = presupuesto semanal / CPA. Con 70 €/día (490 €/semana):

| CPA real | Eventos/semana | Lectura |
|---|---|---|
| 10 € (lead local) | ~49 | Aprendizaje estable posible |
| 25 € (ecommerce barato) | ~20 | Learning limited probable pero funcional |
| 60 € (lead B2B) | ~8 | Muy poca señal: evaluar mensualmente |
| 150 € (high-ticket cualificado) | ~3 | No se puede optimizar a ese evento con fiabilidad |

### A.2 Reglas

1. **1 campaña, 1 ad set.** Advantage+ (campaign budget, audience, placements). Nada de intereses en capas salvo como
   sugerencia mínima.
2. **Evento**: el más cercano al dinero que tenga ≥ ~8–10 eventos/semana; si no, aceptar learning limited o usar un evento
   intermedio **valioso** (lead cualificado por instant form Higher intent, cita, oferta de entrada) — no ATC/LPV por
   defecto (**[CONTESTED]**).
3. **3–8 anuncios** de 2–4 conceptos distintos (estático + vídeo + UGC/testimonio). Más anuncios que presupuesto = la
   mayoría sin señal. Es el primer escalón del **criterio único de conceptos por lote** del sistema operativo (lo usan
   `/brief-creativo`, `/lanzar-campana` y el hito `F3.briefs`):

   | Presupuesto diario de la campaña | Conceptos distintos por lote | Anuncios activos | Fuente |
   |---|---|---|---|
   | ≤ 100 €/día (≈ 3.000 €/mes) | 2–4 | 3–8 | Esta regla; [05 §3](05-framework-testing-creativo.md) |
   | 100–500 €/día | 3–6 | 8–15 | [03 Fase 5](03-framework-lanzamiento.md) («cuentas pequeñas»); 05 §3 |
   | > 500 €/día | 8–15 | 10–20 por ad set | 03 Fase 5 («medianas»); 05 §3 |

   Mínimo para dar un lote por hecho: 2 conceptos distintos hasta 100 €/día y 3 por encima. El tope lo pone la
   capacidad de test ≈ presupuesto semanal de test / (2–3 × CPA objetivo) ([05, TL;DR](05-framework-testing-creativo.md)):
   con 70 €/día y un lead B2B de 60 € salen ~2,7–4 conceptos por semana. **[STRONG INFERENCE]**
4. **Sin retargeting separado** (ya ocurre dentro de la prospección: 10–40 % del gasto según Loomer; ~15 % de media en Haus). **Sin campaña de test**
   separada; usar lotes en el mismo ad set o la herramienta *Creative testing* solo si el presupuesto permite ≥2–3× CPA
   por variante.
5. **Kill rule**: 2–3× CPA sin conversión; nunca a 1×.
6. **Ritmo de decisión**: semanal como mínimo; con <10 eventos/semana, quincenal o mensual. Un mes = ~4 lecturas.
7. **Escalado**: subir cuando haya 2–3 semanas dentro de target; subidas espaciadas; el límite de gasto de cuentas nuevas
   puede impedir saltos grandes.
8. **Dónde está el apalancamiento**: oferta (garantía, bundle, front-end), landing (CVR), velocidad comercial (speed to lead,
   recordatorios), creatividad de concepto. Mejorar la CVR del 2 % al 3 % baja el CPA un 33 %.
9. **Medición**: backend/CRM semanal + Ads Manager (7d click y 1d click). Sin presupuesto para lift: pre/post y holdouts
   geográficos naturales si existen.

### A.3 Por modelo de negocio (≤100 €/día)

| Modelo | Evento | Destino | Nota |
|---|---|---|---|
| Ecommerce AOV 50–70 € | Purchase | Producto/oferta | Aunque quede learning limited; si <8–10 compras/semana con CPA viable tras 3–4 semanas → revisar oferta/landing/precio antes que estructura |
| Negocio local (clínica, reformas) | Lead (instant form Higher intent) o CTWA optimizando a leads donde esté disponible | Formulario 3–5 preguntas / WhatsApp | Radio geográfico realista; llamada en <5 min; medir citas y facturación |
| Servicios/high-ticket | Lead cualificado o cita | Instant form + llamada / aplicación | Con <10 leads/semana: subir presupuesto, bajar fricción o asumir evaluación mensual |
| Infoproducto bajo ticket | Purchase | Página de venta | Si CPA > ticket, el front-end no se sostiene sin upsells |
| SaaS self-serve | Trial con señal de activación | Landing | Optimizar a evento de activación si hay volumen |

### A.4 Errores típicos (pequeño)

5 ad sets de intereses × 15 €/día; campaña de retargeting de 10 €/día; tests de 10 € por anuncio; cambiar algo cada día;
optimizar a tráfico "para que aprenda"; copiar estructuras de cuentas grandes; abandonar a los 5 días.

---

## B. Framework de presupuesto grande (≥5.000 €/día ≈ ≥150.000 €/mes)

### B.1 Restricciones dominantes

- **Rendimientos decrecientes**: el CPA marginal puede ser 1,3–1,7× el medio. Decidir con coste marginal/incremental.
- **Incrementalidad**: Advantage+ y retargeting pueden inflar lo atribuido; Haus (640 tests): Advantage+ ganó a manual en
  iROAS solo en el 42 % de las marcas; en marcas con ≥25 % de negocio no-DTC ~32 % del impacto de Meta cae fuera de DTC.
  **[EMPIRICAL]**
- **Saturación creativa** y límites de anuncios por Página (5.000 activos si el pico mensual < 10 M$; 20.000 si ≥10 M$).
  **[OFFICIAL META]**
- **Riesgo operativo**: una restricción de cuenta o un pago fallido cuesta decenas de miles al día.

### B.2 Arquitectura tipo (por mercado)

```
Mercado X (ad account propia si moneda/entidad/facturación lo requieren)
├─ Evergreen adquisición — Sales, Advantage+, value optimization, CLS "adquirir nuevos" o exclusiones
│    portfolio de pujas: Highest value + ROAS goal (+ bid cap con presupuesto inflado si hay disciplina)
├─ Retención / existentes — solo si la base es grande y la economía distinta (o ad set con max spend)
├─ Momentos — promociones/lanzamientos con budget scheduling (no duplicar 5 días antes)
├─ Testing — graduación semanal de conceptos; campaña "underspend" para anuncios sin gasto
└─ (Lead gen) qualified leads por línea de servicio con CAPI CRM; value rules por segmento
```

### B.3 Reglas

1. **Separar por economía, no por audiencia**: mercado, producto/línea con margen distinto, adquisición vs retención.
2. **Testing industrializado**: 20–50+ anuncios nuevos/semana; briefs desde un registro de aprendizajes; hit rate y
   tiempo-a-ganador como KPIs del equipo creativo.
3. **Pujas**: mezcla; con cost per result goal recordar que de media entrega ~140 % del objetivo (CTC, 253 cuentas);
   ROAS goal ~96,5 %. Presupuesto ≥5× el objetivo de coste. Reglas automáticas de seguridad (no de optimización).
4. **Medición**: MMM (Robyn/Meridian o vendor) + geo-lift/Conversion Lift trimestral + incremental attribution como
   lectura adicional (**[CONTESTED]**); decisiones de presupuesto con iROAS marginal.
5. **Señal**: CAPI server-side con datos de CRM/margen; value rules y audience labels (HIGH_VALUE_CUSTOMERS,
   QUALIFIED_LEADS); Customer Lifecycle Strategy.
6. **Gobernanza**: change log estricto, ventanas de edición, revisiones con finanzas, plan de continuidad (admins de
   respaldo, métodos de pago, cuentas de respaldo legítimas, contacto con partner/rep de Meta).
7. **Agentes IA/MCP**: si se usan, reglas MCP por cuenta (bloquear escrituras no necesarias, topes de presupuesto) y
   flujo de borradores con aprobación humana. **[OFFICIAL META]**

### B.4 Errores típicos (grande)

Medir el éxito con ROAS de plataforma; fragmentar en decenas de campañas por audiencia; escalar sin pipeline creativo;
canibalizar clientes existentes; ignorar fees por país (2–5 %) y el IVA en la comparación con break-even; no tener
plan B ante restricciones; automatizar reglas de pausa por CPA diario.

---

## C. Respuestas rápidas por nivel (con supuestos)

| Presupuesto | Arquitectura | Creatividad | Medición |
|---|---|---|---|
| 100 €/día | 1 campaña, 1 ad set, evento real | 3–8 anuncios, 2–4 conceptos, lote nuevo cada 1–2 semanas | Backend semanal; Ads Manager 7d/1d click |
| 500 €/día | 1 campaña, 1–2 ad sets con propósito; value optimization si ≥50 compras/semana | 10–20 anuncios; test nativo para variantes | + audience segments, cohortes CRM |
| 5.000 €/día | 2–5 campañas con razón de negocio | 20–50 nuevos/semana; testing con graduación | + lift/geo trimestral, MER/nCAC |
| 50.000 €/día | Portfolio por mercado/entidad; pujas mixtas | Testing industrializado | MMM + lift continuo; iROAS marginal |

Detalle y supuestos de CPA de cada nivel: [02/06](../02-estructura-campanas/06-presupuesto-por-niveles.md).
