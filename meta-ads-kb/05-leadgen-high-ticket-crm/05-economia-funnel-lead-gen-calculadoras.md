# Economía del funnel de lead gen y high-ticket: ¿cuánto puedo pagar por lead? (con calculadora)

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: fórmulas y ejemplos trabajados desde la inversión en Meta hasta el cash cobrado: break-even y target de CPL, coste por lead cualificado, por llamada agendada, por show y CPA; pago único vs cuotas, reembolsos, comisiones, IVA, LTV. Calculadora ejecutable: `herramientas/economia.py`, modo `leadgen` (solo librería estándar; desde la raíz del proyecto). Fuentes de benchmarks: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Fórmula maestra:** `CPL máximo = Contribución por venta × P(venta | lead)`, donde `P(venta | lead) = lead→cualificado × cualificado→agenda × show × cierre`. Todo lo demás es desglosar estos dos términos con honestidad. **[STRONG INFERENCE]** (aritmética)
- **La contribución por venta no es el precio:** quita IVA (si es B2C y está incluido), impagos de cuotas, reembolsos, comisión de pasarela, comisiones de setter/closer y coste de entrega. En los ejemplos, un coaching de 10.000 € deja **4.603 €** de contribución esperada por venta; un curso de 2.000 €, **1.070 €**. **[STRONG INFERENCE]**
- **Ejemplos (break-even / target con 50% de margen sobre la contribución):** curso 2.000 € vendido por llamada → CPL 19,26 € / 9,63 €; servicio B2B 5.000 € → CPL 71,62 € / 35,81 €; coaching 10.000 € → CPL 167,56 € / 83,78 €, o 598 € / 299 € por **llamada agendada**. Ver §4.
- **El show rate y el close rate pesan más que el CPL:** en el coaching, pasar de 50% a 70% de show (con 20% de cierre) sube el CPL de break-even de 128,89 € a 180,44 €. Arreglar ventas suele valer más que bajar el CPL un 20%. **[STRONG INFERENCE]**
- **Separa cash del día 0 y cash esperado.** Con 50% de clientes en 6 cuotas, el coaching cobra el día 0 solo el 62% del cash esperado; si financias la publicidad con caja, el límite real de inversión lo pone el cash del día 0 y el periodo de recuperación, no el ROAS "contrato". **[STRONG INFERENCE]**
- **Benchmarks externos solo como contraste:** coste por llamada agendada en coaching high-ticket 150-350 $ (agencia, 2026), show 60-85%, cierre 15-40% (agencias, sin metodología). Tu break-even sale de tu economía, no de un blog. **[EMPIRICAL]** débil (S05-041, S05-042)

---

## 1. Variables y fórmulas

### 1.1 Cash y contribución por venta

| Variable | Definición |
|---|---|
| P | Precio de lista (IVA incluido si B2C) |
| IVA | 21% en España para servicios digitales B2C; en B2B normalmente recuperable (precio sin IVA) |
| f_PIF | % de ventas al contado; descuento d por pago único |
| n, r, m | nº de cuotas, recargo del plan (p.ej. +10%), % del importe pendiente que no se cobra (impago) |
| R | Tasa de reembolsos + chargebacks (sobre cash) |
| k_pas | Comisión de pasarela/financiera sobre el cobro bruto (Stripe ~1,5-3%, financieras más) |
| k_ventas | Comisión de setter + closer (sobre cash neto) |
| k_entrega | Coste de entregar el producto (% del cash neto) |

```
Cash bruto esperado  = f_PIF·P·(1−d) + (1−f_PIF)·P·(1+r)·[1/n + (n−1)/n·(1−m)]
Cash día 0           = f_PIF·P·(1−d) + (1−f_PIF)·P·(1+r)/n
Cash neto            = Cash bruto / (1 + IVA)
Cash tras reembolsos = Cash neto · (1 − R)
Contribución (C)     = Cash tras reembolsos − Cash bruto·k_pas − Cash tras reembolsos·(k_ventas + k_entrega) − coste fijo por venta
```

### 1.2 Break-evens y targets

```
BE CPA                      = C
BE por show                 = C · cierre
BE por llamada agendada     = C · show · cierre
BE por lead cualificado     = C · show · cierre · cualificado→agenda
BE CPL                      = C · show · cierre · cualificado→agenda · lead→cualificado
Target X                    = BE X · (1 − margen objetivo)
```

**Margen objetivo:** parte de la contribución que quieres que quede después de publicidad para pagar estructura y beneficio. 50% es un punto de partida conservador para ofertas con costes fijos altos; en fase de validación puedes aceptar 0-20%. Alternativa equivalente que usan las agencias de coaching: "gastar en adquisición el 25-35% del ingreso" (780 Marketing, S05-042) — ojo, sobre ingreso, no sobre contribución. **[EMPIRICAL]** débil.

### 1.3 Unidades que debes vigilar
- **CPL** (Ads Manager) → **CPQL** (coste por lead cualificado, CRM) → **coste por agenda** → **coste por show** → **CPA** → **ROAS de cash** (cash cobrado / inversión) a 0, 30, 60, 90 días.
- El "ROAS contrato" (valor firmado / inversión) engaña cuando hay cuotas e impagos.

## 2. Supuestos de los ejemplos

Los porcentajes son **supuestos ilustrativos** coherentes con los rangos públicos (S05-040 a S05-045), no benchmarks. Sustitúyelos por los tuyos.

| Parámetro | Curso 2.000 € (B2C) | Servicio B2B 5.000 € | Coaching 10.000 € (B2C) |
|---|---|---|---|
| IVA incluido | 21% | 0% (B2B) | 21% |
| Pago único | 60% | 100% | 50% |
| Plan de pagos | 4 cuotas, +10%, 15% impago | — | 6 cuotas, +10%, 20% impago |
| Reembolsos/chargebacks | 8% | 2% | 5% |
| Pasarela | 3% | 1% | 3% |
| Coste de entrega | 10% | 50% (servicio con equipo) | 20% |
| Comisiones ventas | closer 10% + setter 5% | closer 10% | closer 10% + setter 5% |
| Lead → cualificado | 40% | 40% | 40% (aplicación completa → cualificada) |
| Cualificado → agenda | 50% | 50% | 70% |
| Show | 60% | 75% | 65% |
| Cierre (sobre shows) | 15% | 25% | 20% |
| **Lead → venta** | **1,80%** | **3,75%** | **3,64%** |

## 3. Cash por venta (salida de la calculadora)

| Concepto (€/venta) | Curso 2.000 € | Servicio 5.000 € | Coaching 10.000 € |
|---|---|---|---|
| Contrato medio (IVA incl.) | 2.080,00 | 5.000,00 | 10.500,00 |
| Cash bruto esperado | 1.981,00 | 5.000,00 | 9.583,33 |
| Cash día 0 (bruto) | 1.420,00 | 5.000,00 | 5.916,67 |
| Cash neto sin IVA | 1.637,19 | 5.000,00 | 7.920,11 |
| Tras reembolsos | 1.506,21 | 4.900,00 | 7.524,10 |
| − Pasarela | 59,43 | 50,00 | 287,50 |
| − Comisiones ventas | 225,93 | 490,00 | 1.128,62 |
| − Coste de entrega | 150,62 | 2.450,00 | 1.504,82 |
| **= Contribución por venta** | **1.070,23** | **1.910,00** | **4.603,17** |

Lectura: del "precio de 10.000 €" quedan 4.603 € para pagar publicidad, estructura y beneficio. Si calculas el CPL máximo con 10.000 € estás sobrestimando tu capacidad de puja **más del doble**.

## 4. ¿Cuánto puedo pagar? Break-even y target (margen objetivo 50%)

| Unidad | Curso 2.000 € BE / target | Servicio 5.000 € BE / target | Coaching 10.000 € BE / target |
|---|---|---|---|
| CPA (por venta) | 1.070,23 / 535,12 | 1.910,00 / 955,00 | 4.603,17 / 2.301,58 |
| Por show | 160,53 / 80,27 | 477,50 / 238,75 | 920,63 / 460,32 |
| Por llamada agendada | 96,32 / 48,16 | 358,12 / 179,06 | 598,41 / 299,21 |
| Por lead cualificado | 48,16 / 24,08 | 179,06 / 89,53 | 418,89 / 209,44 |
| **CPL** | **19,26 / 9,63** | **71,62 / 35,81** | **167,56 / 83,78** |

Contraste con el mercado: la agencia 780 Marketing reporta 150-350 $ por llamada agendada desde Meta para coaching de 2-15 k$ (S05-042). Con nuestro coaching de 10.000 €, eso está **por debajo del target de 299 €** → la oferta aguanta ese mercado. Con el curso de 2.000 € (target 48 € por agenda, BE 96 €), 150 $ por agenda **pierde dinero**: un curso de 2.000 € vendido con setter + closer necesita un coste por agenda muy bajo o un cierre muy superior al 15% → señal de que esa oferta quizá deba venderse por webinar/VSL sin llamada o con llamada solo para cualificados. **[STRONG INFERENCE]**

## 5. Simulaciones con inversión real

| Métrica | Curso 2.000 € | Servicio 5.000 € | Coaching 10.000 € |
|---|---|---|---|
| Inversión | 10.000 € | 10.000 € | 20.000 € |
| CPL supuesto | 15 € | 40 € | 60 € (aplicación) |
| Leads | 666,7 | 250 | 333,3 |
| Cualificados | 266,7 | 100 | 133,3 |
| Agendas | 133,3 | 50 | 93,3 |
| Shows | 80,0 | 37,5 | 60,7 |
| Ventas | 12,0 | 9,4 | 12,1 |
| Coste por agenda | 75,00 € | 200,00 € | 214,29 € |
| CPA | 833,33 € | 1.066,67 € | 1.648,35 € |
| Cash esperado (bruto) | 23.772 € | 46.875 € | 116.278 € |
| Cash día 0 | 17.040 € | 46.875 € | 71.789 € |
| ROAS cash esperado / día 0 | 2,38 / 1,70 | 4,69 / 4,69 | 5,81 / 3,59 |
| Contribución total | 12.843 € | 17.906 € | 55.852 € |
| **Beneficio tras ads** | **2.843 €** | **7.906 €** | **35.852 €** |

Lecturas:
- **Curso 2.000 €:** CPA 833 € frente a BE 1.070 € → rentable pero con poco colchón (por encima del target de 535 €). Un ROAS de cash de 2,38 parece "bueno" y, sin embargo, deja solo 2.843 € por cada 10.000 € invertidos. Cualquier caída de show (60→50%) o cierre (15→12%) lo pone en pérdidas.
- **Servicio B2B:** el coste de entrega del 50% es lo que limita; el ROAS de cash de 4,69 deja 7.906 €.
- **Coaching:** la economía aguanta CPL de aplicación de 60 € con holgura; el riesgo está en el cash flow (solo 62% del cash entra el día 0) y en la calidad del equipo de ventas.

## 6. Sensibilidad: qué palanca mueve más el CPL que puedes pagar

BE CPL según show (filas) y cierre (columnas), resto del funnel constante:

**Coaching 10.000 €**

| show \ cierre | 10% | 15% | 20% | 25% | 30% |
|---|---|---|---|---|---|
| 50% | 64,44 | 96,67 | 128,89 | 161,11 | 193,33 |
| 60% | 77,33 | 116,00 | 154,67 | 193,33 | 232,00 |
| 70% | 90,22 | 135,33 | 180,44 | 225,56 | 270,67 |
| 80% | 103,11 | 154,67 | 206,22 | 257,78 | 309,33 |

**Curso 2.000 €**

| show \ cierre | 10% | 15% | 20% | 25% | 30% |
|---|---|---|---|---|---|
| 50% | 10,70 | 16,05 | 21,40 | 26,76 | 32,11 |
| 60% | 12,84 | 19,26 | 25,69 | 32,11 | 38,53 |
| 70% | 14,98 | 22,47 | 29,97 | 37,46 | 44,95 |
| 80% | 17,12 | 25,69 | 34,25 | 42,81 | 51,37 |

**Servicio 5.000 €**

| show \ cierre | 10% | 15% | 20% | 25% | 30% |
|---|---|---|---|---|---|
| 50% | 19,10 | 28,65 | 38,20 | 47,75 | 57,30 |
| 60% | 22,92 | 34,38 | 45,84 | 57,30 | 68,76 |
| 70% | 26,74 | 40,11 | 53,48 | 66,85 | 80,22 |
| 80% | 30,56 | 45,84 | 61,12 | 76,40 | 91,68 |

Regla: el BE CPL es **lineal** en cada tasa. Subir el show del 50% al 70% (+40% relativo) aumenta el CPL pagable un 40%, exactamente igual que bajar el CPL un 29%. Antes de pelearte con Meta por 2 € de CPL, mira si con recordatorios, confirmación y booking inmediato ganas 10 puntos de show (archivo 08). **[STRONG INFERENCE]**

## 7. Otros funnels trabajados

### 7.1 Webinar → aplicación → llamada (coaching 10.000 €)
Supuestos: coste por registro 10 €, show en directo 30%, asistente → aplicación 12%, aplicación → agenda 60%, show llamada 70%, cierre 25%.
- 15.000 € → 1.500 registros → 450 asistentes → 54 aplicaciones → 32,4 agendas → 22,7 shows → **5,67 ventas**; CPA 2.646 €; coste por asistente 33,3 €; coste por agenda 463 €; contribución 26.100 € → beneficio 11.100 €.
- **Coste por registro máximo:** BE 17,40 €, target 8,70 € (lead→venta = 0,378%). Si el show cae al 20%, el BE baja a 11,60 €. La asistencia es la variable crítica del webinar (archivo 07).

### 7.2 Webinar con venta directa (curso 497 € IVA incl., sin llamada)
Contribución por venta 336,3 € (10% reembolsos, 5% entrega). Asistente → compra 5%.
- Show 20% → BE coste por registro 3,36 € (target 1,68 €); show 25% → 4,20 € (2,10 €); show 35% → 5,88 € (2,94 €).
- Añadir replay (10 pp más de registrantes lo ven, convirtiendo a la mitad) sube el BE de 4,20 € a 5,04 €. **[STRONG INFERENCE]**
- Implicación: un curso de 497 € vendido por webinar exige registros de 2-5 €. Con CPL de registro de 8-15 € (rango que reporta una agencia para coaching, S05-042) **no cuadra** sin upsell/back-end.

### 7.3 Low-ticket front-end / tripwire → llamada (servicio 5.000 € IVA incl.)
Supuestos: CPA del front-end 45 € y ticket medio 45 € (autoliquidable, ROAS 1,0 bruto), 8% de compradores agenda, show 70%, cierre 25%, contribución del servicio 2.255 €.
- 10.000 € → 222 compradores (8.017 € netos de IVA y pasarela) → 17,8 llamadas → 12,4 shows → 3,1 ventas → contribución total 15.032 € → **beneficio 5.032 €**; coste neto por llamada 111,6 €.
- La ventaja: el front-end financia la adquisición y el comprador es una señal de **compra** (Purchase) que Meta optimiza mejor que un lead. El riesgo: si el 8% de agenda no se cumple, el beneficio depende solo de que el front-end se autoliquide. **[STRONG INFERENCE]**

### 7.4 Negocio local (clínica estética, tratamiento 600 € IVA incl.)
Contribución primera venta 288,5 € (40% coste de entrega); lead → venta 17,3% (70% contactado, 55% agenda, 75% show, 60% compra).
- BE CPL **primera venta: 50 €**; con LTV de 2,2 visitas (contribución 634,7 €): **110 €**. La decisión de cuánto pagar depende de si financias con la primera venta o con el LTV; muchos negocios locales "pierden dinero" en el primer servicio y ganan en la recurrencia. **[STRONG INFERENCE]**

### 7.5 SaaS (99 €/mes B2B, margen bruto 80%, churn mensual 4%)
LTV de contribución = 99 × 0,8 / 0,04 = 1.980 €.

| Trial → pago | BE coste por trial | Target LTV:CAC 3:1 | Coste por trial con payback 12 meses |
|---|---|---|---|
| 10% | 198 € | 66 € | 95 € |
| 15% | 297 € | 99 € | 142,6 € |
| 20% | 396 € | 132 € | 190,1 € |

Benchmarks públicos (vendors, sin metodología): coste por trial self-serve 15-40 €, trial→pago mediana 12-19% (S05-077). En SaaS el criterio habitual es LTV:CAC ≥3 y payback ≤12-18 meses, no el break-even. **[EMPIRICAL]** débil.

## 8. LTV, upsells y cuándo pagar por encima del break-even de la primera venta

- **LTV de contribución** = C₁ + Σ(probabilidad de compra adicional × contribución de cada compra). En coaching: renovaciones, mastermind, done-for-you.
- Paga por encima del BE de la primera venta **solo** si: (a) tienes datos de cohortes reales (≥6 meses), (b) tu caja aguanta el periodo de recuperación, (c) el LTV no depende de una sola persona (el fundador) que no escala.
- En infoproducto, el "back-end" suele concentrar el beneficio; mide el LTV por **cohorte de mes de adquisición y por campaña**, porque distintos ángulos atraen clientes con LTV distinto. **[STRONG INFERENCE]**

## 9. Cash flow y límites de inversión

- **Cash día 0 / inversión** es el ratio que determina si puedes reinvertir en el mismo mes. Coaching ejemplo: 3,59; curso: 1,70.
- **Payback:** meses hasta que el cash acumulado cubre la inversión + comisiones + entrega. Con planes de 6-12 cuotas puede ser de 3-6 meses.
- **Impagos y chargebacks** suben con planes largos y ventas agresivas; en infoproductos "make money" además elevan el riesgo de cuenta de pagos y de anuncios (archivo 06 §7). Mide impago por closer y por campaña.
- **Comisiones sobre cash cobrado, no sobre contrato,** alinean al equipo con el cash (ofertas de empleo de closers mencionan 5-20%, con 10-20% como rango habitual para closers experimentados; fuentes de baja calidad, S05-072). **[EMPIRICAL]** débil.

## 10. Cómo usar la calculadora

Desde la raíz del proyecto (o con `/economia`, que la ejecuta por ti). Este comando reproduce el ejemplo del coaching de
10.000 € (contribución por venta de 4.603 €):

```
python3 -I herramientas/economia.py leadgen --precio 10000 --iva 0.21 --pct-pago-unico 0.5 --cuotas 6 \
    --recargo-cuotas 0.10 --impago-cuotas 0.20 --reembolsos 0.05 --pasarela-pct 0.03 --entrega-pct 0.20 \
    --closer-pct 0.10 --setter-pct 0.05 --cualif 0.40 --agenda 0.70 --show 0.65 --cierre 0.20 \
    --inversion 20000 --cpl 60
```
- La oferta (`--precio`, `--iva`, `--pct-pago-unico`, `--cuotas`, `--recargo-cuotas`, `--impago-cuotas`, `--reembolsos`,
  `--pasarela-pct`, `--entrega-pct`, `--closer-pct`, `--setter-pct`, `--coste-fijo`) da la contribución por venta; las
  tasas (`--cualif`, `--agenda`, `--show`, `--cierre`), los break-even y targets por etapa; `--inversion` y `--cpl`, la
  simulación. Imprime también la sensibilidad del BE CPL según show y cierre. `--json` para reutilizar la salida.
- Para escenarios de inversión con bandas (planificar o preparar una propuesta): modo `prevision`. Todas las opciones:
  `python3 -I herramientas/economia.py leadgen --help`.
- Mete **tus** tasas de los últimos 60-90 días por canal y por campaña; recalcula cada mes.
- Usa el target por **etapa** que puedas medir antes: si tu ciclo de venta es de 30 días, decide con coste por agenda/show (que ves en 3-7 días) contra su target, y valida con CPA cuando cierre la cohorte.

## Implicaciones operativas

- Define antes de lanzar: contribución por venta, tasas esperadas, BE y target por **agenda** y por **lead cualificado**. Esas son las métricas de corte de los primeros 7-14 días.
- Regla de corte orientativa (high-ticket): ad set con coste por agenda > BE durante 2× el ciclo lead→agenda y ≥10 agendas esperadas → pausar o cambiar ángulo; < target → escalar 20-30% cada 3-4 días (detalle de escalado: área 09). **[STRONG INFERENCE]**
- Revisa trimestralmente impagos y reembolsos: cambian el BE más de lo que parece.

## Errores frecuentes

- Calcular el CPL máximo sobre el precio con IVA y sin comisiones.
- Usar close rate sobre agendas en lugar de sobre shows (o mezclar ambos).
- Comparar CPL entre ofertas con economías distintas.
- Escalar por ROAS de contrato con planes de pago largos (cash flow negativo).
- Ignorar el coste del equipo comercial (setter/closer) que crece con el volumen de leads basura.

## Preguntas abiertas

- No existen benchmarks públicos fiables de impago en planes de pago de infoproductos/coaching en España.
- Tasas de reembolso por tipo de oferta y canal de venta: sin datos públicos verificables.

## Fuentes clave

- [Cost Per Booked Call Benchmarks for High-Ticket Coaches](https://www.780marketing.ca/articles/cost-per-booked-call-benchmarks) — 2026-07-03 — agencia (S05-042)
- [High-Ticket Sales Metrics](https://www.inflopartners.com/blog/high-ticket-sales-metrics-tracking) — 2026-09-05 — agencia (S05-041)
- [Webinar Conversion Rate Benchmarks](https://assetacademy.io/funnels/webinars/webinar-conversion-rate-benchmarks/) — 2026-08-02 — practitioner (S05-045)
- [B2B SaaS Free Trial vs Demo Framework 2026](https://www.growthspreeofficial.com/blogs/b2b-saas-free-trial-vs-demo-decision-framework-2026-conversion-rates-by-acv-product-type) — 2026 — agencia (S05-077)
- Calculadora: `herramientas/economia.py` (modo `leadgen`)
