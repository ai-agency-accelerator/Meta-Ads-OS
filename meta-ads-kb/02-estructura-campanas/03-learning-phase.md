# Learning phase: qué dice Meta hoy, qué la reinicia, y cuánto importa de verdad

> Última verificación: 2026-10-15 · Autor: A02 (agente) · Ámbito: learning phase y learning limited a nivel de ad set; significant edits; impacto de presupuesto, puja, creatividades, audiencia y pausas; evidencia empírica. La teoría de la subasta/ML está en el área 01; el escalado de presupuesto en el área 09.

## TL;DR

- **Posición oficial vigente (texto del Help Center a 2026-10-15)**: un ad set sale de learning "as soon as they can deliver stably", lo que "usually occurs after about **50 results in the week after the ad set's last significant edit**". **No hay cambio oficial de umbral en 2025-2026.** **[OFFICIAL META]** ([HC 112167992830700](https://www.facebook.com/business/help/112167992830700))
- **Excepción documentada**: Shops ads necesitan ≥17 compras web + ≥5 vía Meta. **[OFFICIAL META]**
- **Afirmaciones de umbrales rebajados** (25/semana para Advantage+ sales, 15 para app, "10 en 3 días", "10 para Purchase desde 2024") circulan en blogs de 2025-2026 **sin documento de Meta que las respalde**. **[HYPOTHESIS]** — no usar como regla.
- **Learning limited** = "unlikely to receive about 50 optimization events in the week after your last significant edit". "Isn't a penalty". Causas oficiales: audiencia pequeña, presupuesto bajo, puja/cost control bajo, alto auction overlap, evento infrecuente, demasiados anuncios. **[OFFICIAL META]** ([HC 269269737396981](https://www.facebook.com/business/help/269269737396981))
- **Significant edits (lista oficial)**: cualquier cambio de targeting; cualquier cambio de creatividad; cambio de evento de optimización; **añadir un anuncio nuevo**; pausar el ad set ≥7 días; cambiar bid strategy; cambiar el disclaimer de anuncios políticos. "Pueden o no" serlo según magnitud: presupuesto, spending limit, importe de bid cap / cost per result goal / ROAS goal. **[OFFICIAL META]** ([HC 316478108955072](https://www.facebook.com/business/help/316478108955072))
- **La "regla del 20 %" no es de Meta.** Meta solo da ejemplos extremos (100→101 $ probablemente no; 100→1.000 $ puede). En producto, Meta ha recomendado subidas de +79 % (100→179 $) "sin volver a learning" en ad sets concretos. **[OUTDATED]** como regla mecánica / **[EMPIRICAL]** el ejemplo ([Loomer](https://www.jonloomer.com/updates-to-meta-ads-budgeting/amp/))
- **Con Advantage+ campaign budget**: redistribuir presupuesto entre ad sets NO reinicia learning; añadir un ad set nuevo NO reinicia a los demás; editar un ad set no afecta a los otros; pero **cambiar el presupuesto o la bid strategy de la campaña puede reiniciar varios ad sets a la vez**. **[OFFICIAL META]**
- **Evidencia empírica 2025**: Loomer añadió un anuncio a un ad set activo (22 anuncios) y no reinició learning, contra lo que dice la documentación. Conclusión práctica: el reinicio depende de la magnitud relativa del cambio. **[EMPIRICAL]** (un caso; [Vaizle, 2025-09-29](https://insights.vaizle.com/news/meta-might-have-quietly-changed-how-the-learning-phase-works); [Loomer pubcast, 2025-10-15](https://pubcast.jonloomer.com/the-learning-phase-is-just-a-label/))
- **Cuánto importa**: es una etiqueta de *inestabilidad esperada*, no de "no funciona". Un ad set "Learning limited" rentable no se toca; uno no rentable sí. Lo que sí está bien establecido es que **fragmentar en muchos ad sets que nunca llegan a volumen** sube CPA y varianza; la solución estructural es consolidar. **[OFFICIAL META]** + **[EMPIRICAL]**
- **Migrar o copiar a Advantage+ por API reinicia learning ("there is no workaround")**. **[OFFICIAL META]** ([Meta Developers](https://developers.facebook.com/docs/marketing-api/advantage-campaigns))

---

## 1. Qué es (y qué no es) la learning phase

Texto oficial: es "the period when the delivery system still needs to learn about how an ad set may deliver and perform… when you either create a new ad or ad set or make a significant edit". "While the delivery system never stops learning… ad sets exit the learning phase as soon as they can deliver stably." Durante learning "ad sets are less stable and usually have a higher CPA". **[OFFICIAL META]** ([HC 112167992830700](https://www.facebook.com/business/help/112167992830700))

Interpretación de primeros principios **[STRONG INFERENCE]**:
- El sistema necesita estimar, para *esta combinación concreta* de audiencia/creatividades/evento/puja, las tasas de conversión predichas por impresión y su calibración. Con pocos eventos, las predicciones a nivel de ad set tienen alta varianza → exploración más agresiva (Meta: "may deliver your ads more aggressively to learn", [HC 190490051321426](https://www.facebook.com/business/help/190490051321426)) → CPA más alto y errático.
- Los modelos de fondo (de usuario, de anuncio, de anunciante) **no** empiezan de cero con cada ad set: hay transferencia desde la historia de la cuenta, el pixel/dataset, la Página y los anuncios. Por eso un ad set nuevo en una cuenta madura suele aprender más rápido que en una cuenta nueva. Meta lo insinúa: "The delivery system uses learnings from your Page to improve your ad performance" ([HC 766697140509126](https://www.facebook.com/business/help/766697140509126)). **[OFFICIAL META]** (Página) + **[STRONG INFERENCE]** (resto)
- "Salir de learning" ≠ "rendimiento óptimo". Es "estabilidad suficiente". El sistema sigue aprendiendo siempre.

### Nivel al que aplica
- Ad set (columna Delivery: "Learning", "Learning limited", "Active"). Meta recomienda revisar la columna **"Last significant edit"** y los **"Results"** desde esa edición para saber si se va a llegar. **[OFFICIAL META]**
- Con Advantage+ campaign budget, el learning inicial "will take the same time as ad set budgets". **[OFFICIAL META]** ([HC 316478108955072](https://www.facebook.com/business/help/316478108955072))

### Qué cuenta como "result"
- El performance goal del ad set (no el objetivo de campaña).
- **Solo dentro de la ventana de atribución elegida.** Ejemplo oficial: con 1-day click, una compra 3 días después del clic no cuenta para las 50. **[OFFICIAL META]** ([HC 197634954160445](https://www.facebook.com/business/help/197634954160445)). Implicación: acortar ventana (p. ej. 1-day click) reduce el volumen que cuenta para salir de learning.

## 2. ¿Cambió el umbral en 2025-2026? Verificación

| Afirmación que circula | Fuente | Estado |
|---|---|---|
| "~50 resultados en la semana tras la última significant edit" | Help Center Meta (consultado 2026-10-15) | **[OFFICIAL META]** vigente |
| Shops ads: 17 compras web + 5 vía Meta | Help Center Meta | **[OFFICIAL META]** |
| "Meta bajó a 10 eventos para Purchase/app installs el 9-jun-2024 aunque la UI siga diciendo 50" | Blogs 2025-2026 sin enlace a Meta | **[HYPOTHESIS]** no verificado; contradice el Help Center actual |
| "Advantage+ sales: umbral 25/semana; Advantage+ app: 15 (2026)" | AdBeacon (ago 2026), que cita a Benly/Webhooters, sin documento de Meta; el propio artículo admite "no consistent public confirmation" | **[HYPOTHESIS]** |
| "Algunos salen con 10 conversiones en 3 días" / "20-30 eventos" | Reportes anecdóticos (Dataslayer, Aimerce) | **[EMPIRICAL]** anecdótico; plausible porque el criterio real es "deliver stably", no un contador fijo |
| "Andromeda endureció los reinicios en 2026" / "exit 7-14 días" | Un blog | **[HYPOTHESIS]** |

Búsquedas realizadas: Help Center (versión en inglés descargada directamente), Developers, blogs de Loomer, AdBeacon, Dataslayer, Benly, Pigeon Digital, ScaleMate. Conclusión: **el umbral oficial sigue siendo "about 50"**; que algunos ad sets salgan antes es coherente con la redacción ("as soon as they can deliver stably… usually after about 50"), no con un cambio documentado.

## 3. Significant edits: qué reinicia y qué no

### Lista oficial ([HC 316478108955072](https://www.facebook.com/business/help/316478108955072)) **[OFFICIAL META]**

**Siempre significant:**
- Cualquier cambio de targeting.
- Cualquier cambio de ad creative.
- Cualquier cambio de evento de optimización.
- Añadir un anuncio nuevo al ad set.
- Pausar el ad set **7 días o más** (re-entra en learning al reactivar).
- Cambiar la bid strategy (con Advantage+ campaign budget, puede afectar a varios ad sets).
- Cambiar el disclaimer de anuncios de temas sociales/política.

**Depende de la magnitud:**
- Importe del spending limit del ad set.
- Importe de bid control, cost per result goal o ROAS goal.
- Importe del presupuesto (con Advantage+ campaign budget, cambiar el presupuesto de campaña puede reiniciar varios ad sets).

**No reinicia (Advantage+ campaign budget):**
- Que el sistema redistribuya presupuesto entre ad sets.
- Añadir un ad set nuevo a la campaña (no reinicia los demás).
- Editar un ad set (no afecta a los otros ad sets).

### Matices empíricos
- **Añadir anuncios**: el caso de Loomer (ad set con 22 anuncios + 1 nuevo, sin reinicio) sugiere que el sistema evalúa la magnitud del cambio. **[EMPIRICAL]** Hipótesis razonable: añadir 1 anuncio a un ad set grande y estable no reinicia; añadir 5 a un ad set pequeño sí. **[HYPOTHESIS]**
- **Presupuesto**: Meta ha mostrado recomendaciones in-product de subida de 100 a 179 $ (+79 %) "sin re-entrar en learning" en un ad set activo, y según Loomer los ad sets marcados como "high performing" admiten subidas grandes sin reinicio. **[EMPIRICAL]**
- **Pausas cortas** (<7 días) no reinician por definición oficial, pero con Advantage+ campaign budget Meta desaconseja pausar/reactivar ad sets porque el presupuesto se reasigna a los activos y al reactivar "there might not be any budget left". **[OFFICIAL META]** ([HC 2177212182495139](https://www.facebook.com/business/help/2177212182495139))
- **Ediciones en lote**: Meta recomienda "input changes in bulk" para no re-entrar en learning varias veces. **[OFFICIAL META]**
- **Copiar/migrar a Advantage+** (API `migrate_to_advantage_plus` o copies): resetea learning, sin workaround. Duplicar en Ads Manager crea un objeto nuevo → learning nuevo. **[OFFICIAL META]**

### La "regla del 20 %"
- **[OUTDATED]/[UNPROVEN]** como regla: Meta nunca ha publicado un porcentaje; su documentación habla de magnitud con ejemplos extremos. La regla nace de prácticas de 2017-2019 y se repite sin fuente. Lo correcto en 2026: cambios moderados y espaciados en ad sets estables; cambios grandes cuando la economía lo justifica y se asume un periodo de inestabilidad; preferir subir presupuesto en Advantage+ campaign budget a duplicar.

## 4. Learning limited: diagnóstico y tratamiento

Definición oficial: "unlikely to receive about 50 optimization events in the week after your last significant edit… Learning limited isn't a penalty – it's an indication that your budget isn't being spent effectively because the ad delivery system can't optimize performance with your current setup". **[OFFICIAL META]** ([HC 269269737396981](https://www.facebook.com/business/help/269269737396981))

| Causa (oficial) | Cómo detectarla | Tratamiento |
|---|---|---|
| Presupuesto bajo | Presupuesto semanal < ~50 × CPA esperado | Consolidar ad sets; subir presupuesto si la economía lo permite |
| Audiencia pequeña | Retargeting o geos pequeñas; frecuencia alta | Ampliar audiencia (Advantage+ audience), juntar geos |
| Puja / cost control bajo | Tooltip en el estado; under-delivery | Subir cost per result goal / bid cap o quitarlo |
| Auction overlap | Varios ad sets similares; recomendaciones en opportunity score | Combinar ad sets |
| Evento infrecuente | <50 del evento por semana a nivel de cuenta | Evento más frecuente (ver archivo 02, **[CONTESTED]** para ATC) |
| Demasiados anuncios a la vez | Muchos anuncios con impresiones bajas | Menos anuncios por ad set, más diversidad por anuncio (flexible/multi-asset) |

Fuente de causas y tratamientos: [HC 269269737396981](https://www.facebook.com/business/help/269269737396981). **[OFFICIAL META]**

**Cuándo NO tratarlo**: si el ad set es rentable en el KPI de negocio (CPA/ROAS de backend, coste por lead cualificado) y estable en ventanas de 7 días, dejarlo. Loomer: "the inability to exit learning is not fatal… if results are acceptable, don't worry too much about the label". **[EMPIRICAL]**

## 5. ¿Cuánto importa realmente? Evidencia y matices

- **Lo que Meta afirma**: durante learning, CPA más alto y menos estable; demasiados anuncios/ad sets → menos aprendizaje por objeto; "By combining similar ad sets, you also combine learnings". **[OFFICIAL META]**
- **Lo que observan practitioners**: la etiqueta es un indicador de estabilidad, no de calidad; ad sets rentables en "Learning limited" son comunes en cuentas pequeñas. Loomer: "It's just a label, after all, and advertisers have historically run in fear from it". **[EMPIRICAL]**
- **El problema real no es "estar en learning", es la fragmentación crónica**: 6 ad sets × 8 conversiones/semana nunca estabilizan y además compiten (auction overlap). 1 ad set × 48 sí. Meta lo dice en varias páginas (combinar ad sets, managing ad volume) y es consistente con la práctica dominante 2024-2026 (Loomer, CTC, Foxwell). **[OFFICIAL META]** + **[EMPIRICAL]**
- **Variabilidad aleatoria**: Loomer documentó 3 ad sets idénticos con una diferencia del 25 % entre el mejor y el peor. Implicación: decisiones con pocos eventos (p. ej. matar un ad set con 3 compras vs 5) son ruido. **[EMPIRICAL]** ([19 Rules, 2025-07-21](https://www.jonloomer.com/19-rules-of-successful-meta-advertising/))
- **Value optimization** tiene su propio ritmo: Meta indica que el "peak performance is typically reached after 2 weeks" y recomienda tests de ≥3 semanas. **[OFFICIAL META]**
- **Qualified leads / CRM**: learning de 2-4 semanas según Meta Developers. **[OFFICIAL META]**

## 6. Reglas operativas (umbrales de decisión)

| Situación | Acción recomendada | Etiqueta |
|---|---|---|
| Ad set nuevo, <7 días | No tocar salvo error grave (tracking roto, política, gasto desbocado) | [OFFICIAL META] + [EMPIRICAL] |
| Ad set nuevo, 7-14 días, CPA 1,5-2x objetivo pero tendencia a la baja | Esperar; evaluar en ventana de 7 días | [EMPIRICAL] |
| Ad set "Learning limited" rentable | Mantener; no hacer ediciones menores | [EMPIRICAL] |
| Ad set "Learning limited" no rentable tras 2-3 semanas | Consolidar con otros, ampliar audiencia, subir presupuesto o cambiar evento | [OFFICIAL META] |
| Escalar un ad set estable | Subidas moderadas y espaciadas (p. ej. cada 3-7 días) o seguir recomendaciones in-product; preferir Advantage+ campaign budget a duplicar | [EMPIRICAL] / [STRONG INFERENCE] |
| Refrescar creatividades | Añadir en lote (no de uno en uno cada día); en ad sets grandes el impacto es menor; alternativa: creative testing tool dentro del ad set | [OFFICIAL META] + [EMPIRICAL] |
| Necesidad de pausar >7 días (estacionalidad, stock) | Asumir reinicio; mejor bajar presupuesto que pausar si se volverá pronto | [OFFICIAL META] + [STRONG INFERENCE] |
| Cambiar evento de optimización | Hacerlo una vez, en lote con otros cambios, y medir 2+ semanas | [OFFICIAL META] |

## Implicaciones operativas

- **Presupuestar para el learning**: presupuesto semanal ≈ 50 × CPA esperado por ad set como referencia (Loomer, feb 2026), sabiendo que es una regla práctica, no un requisito (ver archivo 06).
- **Diseña la estructura para minimizar ediciones**: campañas con Advantage+ campaign budget + pocos ad sets + creatividades añadidas en lotes.
- **Lee siempre "Last significant edit" antes de juzgar** un ad set heredado.
- **No uses learning como excusa ni como dogma**: el KPI manda; la etiqueta informa de estabilidad.

## Errores frecuentes

1. Pausar y reactivar ad sets a diario (con Advantage+ campaign budget es especialmente dañino).
2. Duplicar ad sets ganadores para "escalar" en vez de subir presupuesto (nuevo learning + overlap).
3. Repetir la regla del 20 % como si fuera de Meta.
4. Cambiar 5 cosas en 5 días distintos (5 reinicios) en vez de en lote.
5. Matar ad sets en learning con 2-3 conversiones de diferencia.
6. Elegir 1-day click para "limpiar" atribución sin entender que reduce los eventos que cuentan para el learning.

## Preguntas abiertas

- ¿Meta ajusta el umbral por tipo de campaña (Advantage+ sales/app) internamente? Sin evidencia oficial; solo rumores de 2026.
- ¿Cuál es exactamente el criterio de "magnitud" para presupuesto y anuncios nuevos? Solo hay ejemplos in-product.
- ¿Cuánto "conocimiento" se transfiere a un ad set nuevo en una cuenta madura? No documentado.

## Fuentes clave

- [About the learning phase](https://www.facebook.com/business/help/112167992830700) — Meta HC, texto consultado 2026-10-15 — meta-oficial
- [Significant edits and learning phase](https://www.facebook.com/business/help/316478108955072) — Meta HC — meta-oficial
- [About learning limited](https://www.facebook.com/business/help/269269737396981) — Meta HC — meta-oficial
- [Best practices for Advantage+ campaign budget](https://www.facebook.com/business/help/2177212182495139) — Meta HC — meta-oficial
- [Troubleshoot conversion optimization](https://www.facebook.com/business/help/197634954160445) — Meta HC — meta-oficial
- [Advantage+ campaigns (Marketing API)](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta Developers — meta-developers
- [The learning phase is just a label](https://pubcast.jonloomer.com/the-learning-phase-is-just-a-label/) — Jon Loomer, 2025-10-15 — youtube/podcast
- [Meta Might Have Quietly Changed How the Learning Phase Works](https://insights.vaizle.com/news/meta-might-have-quietly-changed-how-the-learning-phase-works) — Vaizle, 2025-09-29 — prensa
- [Updates to Meta ads budgeting](https://www.jonloomer.com/updates-to-meta-ads-budgeting/amp/) — Jon Loomer — practitioner (ejemplo 100→179 $, leído vía resumen)
- [Meta Just Lowered the Advantage+ Learning Threshold](https://www.adbeacon.com/meta-just-lowered-the-advantage-learning-threshold/) — AdBeacon, 2026-08-12 — vendor (baja confianza; afirmación no verificada)
