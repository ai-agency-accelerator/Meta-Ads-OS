---
name: siguiente-anuncio
description: "Decide los próximos 1–3 anuncios de un cliente con datos: actualiza el registro creativo cruzando Meta con GHL o Stripe, elige ganadores con la capa más baja de verdad que tenga n suficiente, lee fatiga y huecos de ángulo, y propone qué iterar o probar con hipótesis, test, vía de producción y coste, revisado por revisor-estrategia."
argument-hint: "<cliente> [profundo]"
---

# /siguiente-anuncio

Cliente: primer argumento de `$ARGUMENTS`. `profundo` lanza el modo multiagente (ver al final).

Marcos: `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` (niveles, kill rules, escalera de
decisión, qué hacer con los resultados), `meta-ads-kb/03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md`,
`meta-ads-kb/03-creatividad/06-fatiga-creativa.md`, `meta-ads-kb/03-creatividad/13-produccion-y-feedback-loop-creativo.md`,
`meta-ads-kb/05-leadgen-high-ticket-crm/09-sales-feedback-loop.md` (informe por anuncio hasta cash) y
`meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md`.

## 0. Antes de empezar
- Sin ficha → `/cliente-nuevo`. Sin economía en la ficha → `/economia` primero: sin target no hay veredicto.
- Sin anuncios con gasto todavía (registro vacío y nada en Meta) → no es esta skill: el primer lote sale de
  `/brief-creativo <cliente>`.
- Si `F1.dataset` o `F1.crm` están sin marcar en `estado.md`, avisa: las capas de negocio pueden estar ciegas y la
  decisión subirá a una capa peor.

## 1. Actualizar el registro (solo lectura)
Periodo: las últimas 4–8 semanas completas (lunes a domingo). `registro_creativo.py actualizar` ya aplica la paciencia:
no juzga una capa de negocio antes de su madurez (citas, shows o ventas; mira `madurez` en la salida y cámbiala con
`--madurez capa=días`) ni da un ganador por confirmado con menos de 7 días. Lo de los últimos 7 días es provisional
para el coste y sirve sobre todo para descartar por métricas antes del clic.

1. **Meta.** Con token avanzado: `python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`
   (deja el CSV por anuncio en `clientes/<slug>/datos/`). Sin token: `analista-meta` con `ads_get_ad_entities` a
   nivel de anuncio, o una exportación de Ads Manager que deje el usuario. Guárdala en
   `clientes/<slug>/datos/meta-anuncios_<desde>_<hasta>.csv` con las columnas que pide
   `python3 -I herramientas/registro_creativo.py actualizar --help`.
2. **Negocio** (agregados por `ad_id`; lo personal, solo en `privado/`):
   - GHL (`crm.tipo: ghl`): `python3 -I herramientas/ghl.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`.
     Sin token de GHL pero con el MCP conectado: `especialista-crm` lee por MCP y deja el mismo agregado en `datos/`.
   - Stripe (`stripe: true`): `python3 -I herramientas/stripe_datos.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`.
3. Propuesta sin escribir: `python3 -I herramientas/registro_creativo.py actualizar --cliente <slug> --meta <csv> [--ghl <csv>] [--stripe <csv>] --simular --json`
   (veredictos y motivos propuestos; no toca el CSV). Enséñaselos al usuario y, **con su OK**, ejecuta la misma orden
   sin `--simular` ni `--json`: eso escribe el registro y deja la última exportación para `/analisis-creativo`.
4. `python3 -I herramientas/registro_creativo.py sin-nomenclatura --cliente <slug>`. Los anuncios sin nomenclatura no se
   pueden agregar por ángulo ni concepto: lístalos, propón su clasificación y, con el OK del usuario, rellena `angulo`
   y `concepto` en el CSV respetando la cabecera exacta (contrato §6).
5. Citas y ventas llegan con retraso: `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por anuncio --modelo servicios|saas`
   (toma el CSV de leads más reciente de `privado/`) para leer cada anuncio por cohorte de captación, no por fecha de
   venta. Las cohortes inmaduras (menos de `--ciclo` días) no deciden.

## 2. Elegir ganadores con la capa más baja de verdad que tenga n suficiente

| Tipo de negocio (`tipo`) | Capas, de mejor a peor |
|---|---|
| `servicios-high-ticket`, `lead-gen`, `local`, `infoproducto` | venta o cash > cita o show > cualificado > lead (CPL) |
| `saas` | cliente de pago > prueba activada > prueba > registro |
| `ecommerce`, `app` | compra con valor (contribución) > compra > inicio de pago |

- Usa la capa más cercana al dinero en la que los anuncios comparados tengan **≥10–20 eventos** (ganador provisional);
  para darlo por **confirmado**, ≥30–50 eventos y ≥7 días (`13-sistema-operativo/05-framework-testing-creativo.md` §5).
- Si ningún anuncio llega, agrega por concepto o ángulo. Si aun así no llega, sube una capa **y dilo**: «decidimos con
  CPL porque solo hay 4 citas: es provisional».
- Las métricas antes del clic (hook rate, hold, CTR) **solo descartan**: hook rate < 50 % de la mediana de la cuenta y
  CTR muy bajo tras 1.000–2.000 impresiones. Nunca coronan un ganador.
- Comprueba que las diferencias son reales: `python3 -I herramientas/estadistica.py comparar --gasto-a .. --conv-a .. --gasto-b .. --conv-b ..`.
  Anuncios sin conversiones: `python3 -I herramientas/estadistica.py kill --cpa-objetivo <target de la capa> --gasto <gasto>`
  (kill a 2–3× el target, nunca a 1×).
- La propuesta de `n_suficiente`, `veredicto` (`ganador|perdedor|sin-datos|en-test`), `fecha_veredicto` y `motivo`
  es la salida de `actualizar --simular --json` (paso 1.3). Si corriges alguno a mano, dilo, y se escribe solo con su
  OK.

## 3. Leer el contexto
- **Concentración del gasto**: % del gasto en el primer y en los tres primeros anuncios. Un anuncio sin gasto no está
  probado (`05-framework-testing-creativo.md` §6).
- **Fatiga por cohorte**: coste de la capa elegida frente a impresiones acumuladas y semanas activo, y los avisos de
  Meta *Creative limited* / *Creative fatigue* (`meta-ads-kb/00-ESTADO-ACTUAL-2026.md` §6). No uses «frecuencia > 3».
- **Huecos**: la matriz de ángulos de `clientes/<slug>/investigacion/` frente a los ángulos, personas y formatos ya
  probados en el registro. Usa también `/competencia` y `/voz-cliente` si están en `investigacion/`; si faltan, apúntalo.
- **Reparto explorar/explotar**: `explorar_explotar` de la ficha (0,3 por defecto, `[HYPOTHESIS]`) decide cuántas
  propuestas son conceptos nuevos frente a iteraciones.
- **Capacidad de test**: presupuesto semanal de test ÷ (2–3 × target de la capa) = anuncios que de verdad puedes probar.
  Eso limita el número de propuestas.
- **Elementos y suministro** (si existen; si no, sigue y sugiere `/analisis-creativo <slug>`): el último
  `clientes/<slug>/informes/analisis-creativo/<AAAA-MM-DD>.md` (qué repetir, qué probar, qué dejar, conceptos casi
  iguales), las etiquetas de `clientes/<slug>/datos/elementos-creativos.csv` de los ganadores y el plan de suministro de
  `datos/analisis-creativo/<AAAA-MM-DD>_suministro.json`, que sustituye al cálculo de capacidad de arriba para el
  número de conceptos nuevos. Las propuestas no repiten un elemento de «qué dejar» sin decir por qué, no caen en un grupo
  de conceptos casi iguales y dicen en la evidencia qué elemento aprovechan (con su etiqueta). Si el análisis tiene más
  de 6 semanas, dilo.
- **Si todo pierde**, no propongas más anuncios: revisa oferta y landing antes (`05-framework-testing-creativo.md` §7)
  → `/oferta` o `/landing`.

## 4. Proponer 1–3 anuncios
Cada propuesta, con estos campos:
- **Tipo**: iteración de un ganador (hook, formato o persona) o concepto nuevo (otro ángulo u otra dramatización).
- **Hipótesis** con la plantilla de `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §3.
- **Evidencia**: capa usada, n, coste frente al target y etiqueta.
- **Diseño del test**:
  - hooks: un hook por conjunto en ABO con el mismo presupuesto, para que cada uno tenga gasto garantizado.
    `[EMPIRICAL]` observado en una cuenta de servicios high-ticket: con varios hooks en el mismo conjunto, el sistema
    concentró el gasto en uno y el resto quedó sin probar;
  - conceptos: gasto garantizado con la herramienta nativa *Creative testing* (2–5 variantes, ≤20 % del presupuesto,
    7 días) o un conjunto de test (`05-framework-testing-creativo.md` §2–3);
  - métrica de decisión y ventana, kill rule (2–3× el target) y fecha de evaluación (≥7 días y n suficiente).
- **Vía de producción**: `ia` (motor de vídeo; coste real con `/motor`), `propio` (guion de grabación; coste = tiempo),
  `hibrido` o `estatico` (casi sin coste).
- **Nombre** según la nomenclatura (`<AAAAMMDD>_<angulo>_<concepto>_<formato>_h<n>`), validado con
  `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre>"`.
- **Coste estimado**: producción más presupuesto del test (€/día × días), dentro de `topes` de la ficha.

## 5. Revisión antes de enseñarlo
1. `revisor-estrategia` revisa las propuestas con el resumen del registro y los targets: principios
   (`13-sistema-operativo/01-principios-de-razonamiento.md`), mitos (`12-mitos-contradicciones/01-mitos-meta-ads-2026.md`),
   regla de paciencia y solidez estadística. Si tumba una, corrígela o quítala y explica por qué.
2. Si el ángulo toca ingresos, salud, finanzas o resultados prometidos, pasada rápida de `revisor-politicas`.

## 6. Enseñar, guardar y parar
- Guarda en `clientes/<slug>/planes/AAAA-MM-DD_siguiente-anuncio.md`: datos usados (periodo, ventana, capa, n),
  propuestas, veredicto de `revisor-estrategia`.
- Pregunta cuáles aprueba. **Aquí paras**: nada se produce ni se publica sin su sí.

## 7. Con la aprobación
1. `estratega-creativo` escribe el brief de cada propuesta aprobada (plantilla `10-plantillas.md` §3) dentro del plan.
2. Dile el comando exacto para producir, que escribe él: `/producir-video <slug> ia|propio|hibrido` o
   `/producir-estatico <slug>` (producir gasta y por eso no se lanza sola).
3. Después: `/publicar-anuncios` para subir en pausa y `/test-creativo` para montar y leer el test.

## Modo profundo
Con `profundo`: avisa antes de que lanza el workflow `estudio-creativo` (datos del registro → ángulos → jueces → briefs
→ crítica → políticas, unos 11–17 agentes con 3 briefs `[HYPOTHESIS]`) y que consume bastante más uso de tu plan que
el modo normal; no gasta en el motor ni escribe en Meta. Solo con su sí, lánzalo con la herramienta Workflow y args
`{"cliente": "<slug>", "n": <1–6>, "contexto": "<capa de verdad elegida, huecos detectados, explorar_explotar, restricciones>", "origen": "siguiente-anuncio"}`
(añade `formatos`, `vias` o `forzar_angulos` solo si hay que limitarlos). Deja la salida en
`clientes/<slug>/creativos/<AAAA-MM-DD>-estudio/` (`estudio.md`, `estudio.json`, `briefs/`); revísala igualmente con
los pasos 5 y 6 antes de proponer producir.
