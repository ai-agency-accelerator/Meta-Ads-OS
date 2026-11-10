# Reglas automáticas de Ads Manager: cuáles sirven, cuáles hacen daño y plantillas sensatas (2026)

> Última verificación: 2026-10-15 (bloque de actualización del 2026-11-09 tras el TL;DR) · Autor: A10 (agente) · Ámbito: Automated Rules de Ads Manager y Ad Rules Engine de la
> Marketing API (`adrules_library`), interacción con los cambios 2025-2026 (atribución, flexibilidad de presupuesto,
> Advantage+, MCP) y un marco estadístico para no matar anuncios buenos por ruido.

## TL;DR

- **Las reglas son útiles como alarmas y protecciones de gasto; son peligrosas como "media buyer automático"** que
  apaga/enciende por CPA diario con poco volumen. **[EMPIRICAL]** + **[STRONG INFERENCE]** (razonamiento estadístico abajo)
- **Con ~1–3 conversiones/día por ad set, el CPA diario es ruido**: un anuncio con CPA real = objetivo tiene un 37% de
  probabilidad de gastar 1× CPA sin conversiones, un 13,5% de gastar 2× y un 5% de gastar 3×. Reglas "pausa si gasto > 1–2×
  CPA y 0 resultados hoy" matan anuncios buenos a menudo. **[STRONG INFERENCE]** (Poisson)
- **Los cambios 2025-2026 rompen reglas antiguas**: la flexibilidad diaria del 75% (v24) hace que "gasto hoy > presupuesto"
  sea normal; el cambio a link clicks (mar-2026) sube el CPA "por clic" reportado; la latencia de atribución (7 días) hace
  que el CPA de "hoy" esté inflado; editar placements/audiencias desde reglas puede quitar el estado Advantage+. **[OFFICIAL META]** + **[STRONG INFERENCE]**
- **Reglas recomendadas por defecto**: alertas de entrega cero, de gasto anómalo, de CPM/CTR/frecuencia fuera de rango,
  "kill switch" por gasto acumulado (lifetime/7 días) sin resultados con umbral ≥3–4× CPA objetivo, apagados programados
  de promociones, y notificaciones de presupuesto agotado. **[EMPIRICAL]**
- **API**: las reglas son objetos `adrules_library` con `evaluation_spec` (SCHEDULE o TRIGGER), `execution_spec`
  (NOTIFICATION, PAUSE, UNPAUSE, CHANGE_BUDGET, CHANGE_CAMPAIGN_BUDGET, CHANGE_BID, ROTATE, REBALANCE_BUDGET,
  PING_ENDPOINT) y `schedule_spec`; `attribution_window` solo admite `ACCOUNT_DEFAULT`. **[OFFICIAL META]** (S10-012)
- **Límite duro**: 4 cambios de presupuesto por hora por ad set (si una regla y un agente compiten, el ad set queda
  bloqueado 1 h). **[OFFICIAL META]** (S10-011)
- **Nuevo en 2026**: el asistente de Ads Manager prueba "tareas programadas y alertas" (test, oct-2026) y los agentes
  externos vía MCP pueden actuar como "reglas inteligentes"; deben gobernarse con reglas MCP y borradores. **[OFFICIAL META]** (S10-014)

> **Actualización 2026-11-09** (revisión de octubre–noviembre, bloque B21; manda sobre lo de abajo si chocan)
> - **"Performance-based budget increase" (beta)**: subiría el presupuesto solo cuando el rendimiento acompaña, según una única agencia que cita una sesión de Meta sin enlace. **[HYPOTHESIS]** Si aparece en una cuenta, no la combines con reglas propias de escalado en el mismo conjunto sin vigilarlo.
> - **Medición en el dispositivo (12-nov; no en la UE ni el Reino Unido)**: puede subir las compras reportadas sin cambio real. Las reglas por CPA o ROAS atribuidos pueden dispararse: revisa umbrales tras esa fecha. **[OFFICIAL META]** (ajuste) + **[STRONG INFERENCE]** (efecto en reglas)
> - **API v27**: expansión de dispositivos por defecto en Ventas si segmentas por `user_device`/`user_os`; las reglas y scripts que asumen una segmentación por SO pueden ver entrega en otros dispositivos. **[OFFICIAL META]**
> - Fuentes: S10-099, S10-105, S10-124 en [ledger 10](../fuentes/ledger-10-cambios-api-ia.md).

---

## 1. Qué son y cómo funcionan

- **Ads Manager → Reglas automatizadas**: condición(es) sobre métricas o metadatos + periodo (time range) + acción +
  frecuencia de comprobación (continua ~cada 30 min, diaria o personalizada) + notificación. El límite de reglas por cuenta
  que citan terceros (250) no lo he verificado en doc oficial. **[EMPIRICAL]**
- **API (Ad Rules Engine)** (S10-012):
  - `evaluation_type`: `SCHEDULE` (cada día/hora/media hora/custom en la zona horaria de la cuenta) o `TRIGGER` (evaluación
    en tiempo real cuando cambian metadatos o insights; solo presets que incluyen `TODAY`).
  - Filtros combinados con AND; `time_preset` obligatorio si hay métricas (`TODAY`, `YESTERDAY`, `LAST_3D`, `LAST_7D`,
    `LAST_14D`, `LIFETIME`, presets ROAS como `LAST_ND_14_8`…).
  - `attribution_window`: solo `ACCOUNT_DEFAULT` (la regla usa la configuración de atribución de la cuenta; tras el cambio
    a link clicks del 3-mar-2026, el CPA que ve la regla cambió).
  - Acciones: `NOTIFICATION`, `PAUSE`, `UNPAUSE` (schedule y trigger); `CHANGE_BUDGET`, `CHANGE_CAMPAIGN_BUDGET`,
    `CHANGE_BID`, `ROTATE`, `REBALANCE_BUDGET` (solo schedule); `PING_ENDPOINT` (solo trigger → webhook a tu app).
  - Opciones: `change_spec` (amount, limit, unit), `execution_count_limit` (máx. veces por objeto), `action_frequency`
    (minutos mínimos entre acciones), `user_ids` (destinatarios).
  - Filtros avanzados: `daily_ratio_spent` (gasto hoy / presupuesto diario), `hours_since_creation`,
    `estimated_budget_spending_percentage`, `audience_reached_percentage`.
  - Importes en unidad base de la moneda (USD: 1000 = 10,00 $).

## 2. Por qué las reglas por CPA diario hacen daño (primeros principios)

Las conversiones de un ad set en un periodo corto se comportan aproximadamente como un proceso de Poisson. Si el CPA real
del anuncio es igual al objetivo (C) y gasta k×C, el número esperado de conversiones es k y la probabilidad de **cero**
conversiones es e^(−k):

| Gasto acumulado sin conversiones | Probabilidad de que un anuncio "bueno" (CPA real = objetivo) no haya convertido |
|---|---|
| 1× CPA objetivo | 37% |
| 2× | 13,5% |
| 3× | 5,0% |
| 4× | 1,8% |
| 5× | 0,7% |

Además:
- **Latencia de atribución**: con 7d click, parte de las conversiones de hoy se atribuyen días después; el CPA de "hoy" o
  "ayer" está sesgado al alza. **[STRONG INFERENCE]**
- **Varianza del CPA con pocas conversiones**: con 3 conversiones, el intervalo de confianza del 95% para la tasa real va
  aproximadamente de 0,6 a 8,8 conversiones → el CPA "verdadero" puede estar entre ~0,35× y ~5× el observado. Decidir con
  eso es lanzar una moneda. **[STRONG INFERENCE]**
- **Coste de apagar/encender**: interrumpe el aprendizaje del ad set y la exploración del sistema; encender "ganadores" de
  ayer genera bucles. **[EMPIRICAL]** (consenso practicante; Meta documenta que ediciones significativas reinician
  aprendizaje — ver área 01/02).

**Regla práctica**: decidir sobre ventanas de ≥3–7 días (excluyendo hoy) o sobre gasto acumulado lifetime, con umbrales
≥3× CPA objetivo para "kill switches", y solo actuar automáticamente cuando el volumen es suficiente (p. ej., ≥20–30
conversiones en la ventana para decisiones de escalado). **[STRONG INFERENCE]**

## 3. Cambios 2025-2026 que obligan a revisar reglas existentes

| Cambio | Efecto en reglas | Acción |
|---|---|---|
| Flexibilidad diaria 25% → 75% (v24, oct-2025) | "Gasto hoy > presupuesto diario" o `daily_ratio_spent > 1,25` se dispara sin problema real | Usar gasto semanal o `daily_ratio_spent > 1,8` solo como alerta |
| Click-through solo link clicks (3-mar-2026) | CPA/ROAS "click" peor que antes; umbrales calibrados en 2025 disparan más | Recalibrar umbrales con datos post-abril-2026 |
| Fin de 7d/28d view en API (12-ene-2026) | Reglas/dashboards externos que usaban view-through largo devuelven vacío | Revisar fórmulas |
| Breakdowns device/hourly/frequency opt-in (6-ago-2026) | Alertas por hora/dispositivo en herramientas externas reciben vacío sin error | Activar opt-in |
| Advantage+ state (tres palancas) | Reglas o scripts que tocan placements/audiencia quitan el estado Advantage+ | No automatizar ediciones de targeting/placements |
| Sin placements manuales en ad set en Sales/Leads/App (Engagement no; corrección 2026-11-09) (Help Center ~12-oct-2026, gradual) | Scripts/reglas que editan placements del ad set fallarán o no tendrán efecto | Value rules por placement o exclusiones de cuenta por objetivo |
| Límite 4 cambios de presupuesto/hora/ad set | Reglas cada 30 min + agente MCP + humano → bloqueo | `action_frequency` ≥ 60–1440 min |
| Agentes MCP con escritura (2026) | Un agente puede actuar como regla sin límites | Reglas MCP: bloquear presupuesto o limitar importe; borradores |

## 4. Reglas útiles (plantillas sensatas)

Sustituir `C` por CPA objetivo, `P` por presupuesto diario. Ajustar a la moneda y al volumen de la cuenta.

### A. Alertas (solo notificación) — recomendadas en todas las cuentas
1. **Entrega cero**: ad sets activos con `impressions < 100` en `TODAY` a partir de las 12:00 → notificar. (Detecta
   rechazos, problemas de pago, audiencias agotadas.)
2. **Gasto anómalo**: `daily_ratio_spent > 1,8` antes de las 18:00 → notificar (no pausar; la flexibilidad del 75% es legal).
3. **Kill switch de alerta**: `spent (LAST_3D) > 3×C` y `results = 0` → notificar.
4. **CPM fuera de rango**: `cpm (LAST_3D) > 1,5 × mediana de la cuenta` → notificar (subasta, audiencia estrecha, rechazos parciales).
5. **Frecuencia en prospección**: `frequency (LAST_7D) > umbral` (p. ej., 3–4 en prospección amplia; distinto en
   retargeting) → notificar. (El campo `frequency` del ad set no depende del breakdown opt-in.)
6. **Caída de CTR/link CTR**: `link_ctr (LAST_3D) < 50% de su media 14D` → notificar (fatiga creativa).
7. **Lead gen sin leads**: formularios activos con `results = 0` en `LAST_2D` y gasto > 2×C → notificar (formulario roto,
   webhook caído, mTLS sin la nueva CA).

### B. Protecciones de gasto (acción automática, conservadoras)
1. **Kill switch lifetime**: `entity_type = AD`, `lifetime spent > 4×C`, `results = 0`, `impressions > 2.000`,
   `hours_since_creation > 72` → PAUSE. Probabilidad de matar un anuncio "bueno" ≈ 1,8%. **[STRONG INFERENCE]**
2. **Tope de pruebas**: anuncios en ad sets de testing con `spent (LIFETIME) > 6×C` y `cpa > 2×C` con ≥3 resultados → PAUSE.
3. **Fin de promoción**: por nombre/label (`adlabel_ids`) a fecha fija → PAUSE (mejor que depender de memoria humana).
4. **Protección de presupuesto total**: preferir **spend cap de cuenta/campaña** a reglas (10 cambios/día de spend cap por API).
5. **Webhook a tu sistema** (`PING_ENDPOINT`, trigger): cuando `spent TODAY > X` en una cuenta de cliente → tu app decide
   (Slack, aprobación humana). Ver 08.

### C. Escalado (solo con volumen y con techo)
- `CHANGE_BUDGET +15–20%` si `cpa (LAST_7D) < 0,8×C` **y** `results (LAST_7D) ≥ 30`, `action_frequency = 4320` (3 días),
  `execution_count_limit = 3`, techo `limit`. **[CONTESTED]**: hay practicantes que prefieren escalar a mano o con
  campañas nuevas; Meta afirma que cambios significativos reinician aprendizaje. Con Advantage+ campaign budget y la
  flexibilidad del 75%, el beneficio marginal de reglas de escalado es menor que en 2022-23. **[STRONG INFERENCE]**
- Nunca escalar con `time_preset = TODAY` ni con <20 conversiones en la ventana.

## 5. Reglas dañinas (evitar)

| Regla | Por qué daña | Etiqueta |
|---|---|---|
| Pausar si CPA de hoy > objetivo | Ruido + latencia de atribución; mata ganadores | [STRONG INFERENCE] / [EMPIRICAL] |
| Pausar a las X h y reactivar a las Y h (dayparting por on/off) | Reinicia dinámica de entrega; hay ad scheduling con presupuesto lifetime | [EMPIRICAL] |
| "Encender ayer los anuncios que ayer tuvieron buen CPA" | Bucle de ruido; regresión a la media | [STRONG INFERENCE] |
| Subir presupuesto cada hora si ROAS de hoy > X | ROAS intradía no fiable; choca con 4 cambios/hora | [OFFICIAL META] límite + [STRONG INFERENCE] |
| REBALANCE_BUDGET agresivo entre ad sets con poco volumen | Concentra presupuesto en el ruido | [STRONG INFERENCE] |
| Reglas que editan targeting/placements | Pierden estado Advantage+ y aprendizaje | [OFFICIAL META] (estado) |
| Reglas sobre ROAS con view-through en remarketing | Inflan éxito de audiencias calientes | [EMPIRICAL] |
| Reglas que compiten con un agente MCP o con otra regla | Acciones contradictorias, bloqueos | [STRONG INFERENCE] |

## 6. Gobierno de reglas (proceso)

1. **Inventario por cuenta**: nombre normalizado (`ALERT_`, `PROTECT_`, `SCALE_`), dueño, fecha, justificación, umbrales.
2. **Modo sombra**: toda regla nueva arranca como notificación 1–2 semanas; se revisa cuántas veces habría actuado y si
   habría acertado.
3. **Revisión trimestral** y tras cambios de Meta (atribución, presupuesto, placements).
4. **Exclusión de periodos especiales**: lanzamientos creativos, BFCM, rebajas, cambios de oferta (umbrales "normales"
   no aplican).
5. **Log**: el "Activity log" (también accesible por MCP) muestra cambios hechos por reglas; revisarlo semanalmente.

## Implicaciones operativas

- En cuentas pequeñas (<30 conversiones/semana por campaña): **solo alertas + kill switch lifetime ≥4×C**.
- En cuentas medianas/grandes: añadir escalado con techo y `execution_count_limit`, y mover lógica compleja a sistema
  externo con aprobación humana (08).
- Recalibrar todos los umbrales de CPA/ROAS calculados antes de abril-2026.

## Errores frecuentes

- Copiar umbrales genéricos ("pausa a 50 $ sin conversión") sin relación con el CPA de la cuenta.
- Usar "hoy" en reglas de decisión.
- Olvidar la zona horaria de la cuenta (`TODAY` empieza a medianoche de la cuenta).
- No revisar las reglas tras la migración ASC → Advantage+ (IDs nuevos al duplicar campañas ECBC).

## Preguntas abiertas

- ¿Las "tareas programadas y alertas" del asistente (test) sustituirán a las reglas clásicas? ¿Tendrán API?
- ¿Las reglas podrán usar `attribution_window` distinto de `ACCOUNT_DEFAULT` en el futuro? (hoy no)

## Fuentes clave

- [Ad Rules Engine — Evaluation Spec](https://developers.facebook.com/documentation/ads-commerce/marketing-api/ad-rules/overview/evaluation-spec.md) — meta-developers (S10-012)
- [Execution Spec](https://developers.facebook.com/docs/marketing-api/ad-rules/overview/execution-spec) — meta-developers (S10-012)
- [Rate Limiting](https://developers.facebook.com/docs/marketing-api/overview/rate-limiting) — meta-developers (S10-011)
- [Marketing API v24.0](https://developers.facebook.com/docs/marketing-api/marketing-api-changelog/version24.0) — meta-developers (S10-009)
- [Click attribution update](https://www.facebook.com/business/news/click-attribution) — meta-oficial (S10-015)
- [Advertising Week New York 2026](https://www.facebook.com/business/news/advertising-week-new-york-2026) — meta-oficial (S10-014)
