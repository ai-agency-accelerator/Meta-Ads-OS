---
name: analisis-creativo
description: "Analiza qué elementos de tus anuncios (quién habla, primer fotograma, texto inicial, duración, ritmo, demo, prueba, cifra, CTA, subtítulos) se asocian a ganar con la capa más baja de verdad, lee la retención del vídeo, detecta conceptos casi iguales y fija cuántos conceptos nuevos producir al mes. No elige el próximo anuncio ni diseña tests."
argument-hint: "<cliente> [etiquetar|analizar|diversidad|suministro] [--desde AAAA-MM-DD --hasta AAAA-MM-DD]"
---

# /analisis-creativo

Cliente: primer argumento de `$ARGUMENTS`. Sin modo, haz todo (pasos 0–9). Con modo:
- `etiquetar`: pasos 0–3 (fotogramas y etiquetas de los anuncios nuevos);
- `analizar`: pasos 0–1 y 4–9 con las etiquetas que ya hay;
- `diversidad` o `suministro`: paso 0, 1, ese paso y la entrega reducida del paso 8.

Herramienta: `python3 -I herramientas/elementos_creativos.py` (en adelante `ec`). Guía para el usuario:
`docs/guias/analisis-creativo.md`.

Marcos:
- `meta-ads-kb/03-creatividad/01-creative-es-targeting.md` (similitud, dimensiones de diversidad, prueba de la frase y
  de la cuadrícula, concentración);
- `meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md` (hook rate, hold rate, cuartiles, árbol de
  diagnóstico; la atención diagnostica y no predice negocio);
- `meta-ads-kb/03-creatividad/13-produccion-y-feedback-loop-creativo.md` §4 (volumen y mezcla de producción);
- `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` (capacidad de test, escalera de decisión,
  iteraciones de un ganador);
- `meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md` §8 (comparaciones múltiples y
  gasto que no se reparte al azar);
- `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §8 (formatos y principios para este público).

## 0. Antes de empezar
- Sin ficha → `/cliente-nuevo`. Sin targets en la tabla «Economía» de la ficha → `/economia`: sin target no hay plan de
  suministro.
- Qué no es esta skill: elegir los próximos 1–3 anuncios es `/siguiente-anuncio` (que leerá lo que dejes aquí); diseñar
  o leer un experimento es `/test-creativo`; el seguimiento semanal es `/informe-semanal`.
- Cadencia: una vez al mes o cuando haya ≥10 anuncios nuevos con gasto desde el último análisis `[HYPOTHESIS]`. Con
  menos de 8 anuncios con gasto, la lectura de elementos saldrá casi entera «n insuficiente»: dilo, etiqueta igualmente
  (sirve para la próxima vez) y entrega solo diversidad y suministro.
- Si `F1.dataset` o `F1.crm` están sin marcar en `estado.md`, avisa: la capa de decisión puede quedarse en leads.

## 1. Actualizar el registro (solo lectura)
Periodo: las últimas 8–12 semanas completas (más anuncios dan más n; más de un trimestre mezcla contextos)
`[HYPOTHESIS]`. Si `/siguiente-anuncio` o `/informe-semanal` actualizaron el registro con ese periodo hace menos de
7 días, reutilízalo.
1. **Meta**: `python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`.
   El CSV de `datos/` trae hook rate, hold rate y la retención por cuartiles, el tiempo medio y la curva de los
   primeros segundos (fórmulas en la cabecera de `herramientas/meta_ads.py`). Sin token: `analista-meta` por MCP o una exportación de Ads
   Manager con el identificador del anuncio y las columnas de reproducciones de vídeo (3 s, ThruPlay, 25/50/75/95/100 %).
2. **Negocio**: igual que el paso 1.2 de `/siguiente-anuncio` (`ghl.py por-anuncio` o `stripe_datos.py por-anuncio`).
3. `python3 -I herramientas/registro_creativo.py actualizar --cliente <slug> --meta <csv> [--ghl <csv>] [--stripe <csv>]`.
   Deja `datos/registro-creativo_ultima-exportacion.json` (periodo y anuncios de esa exportación): los pasos 2–4 solo
   miran esos anuncios. Sin él (registro de una versión anterior), repite este paso.

## 2. Fotogramas
1. `ec etiquetas preparar --cliente <slug>`: una fila por anuncio con gasto **en la última exportación** en
   `clientes/<slug>/datos/elementos-creativos.csv` (conserva lo ya etiquetado; el soporte sale del formato del
   nombre). Los del registro que no están en ella se cuentan en el aviso y no se mezclan; `--todos` los incluye, pero
   mezcla periodos distintos.
2. `ec fotogramas --cliente <slug> --cuadricula` (los 30 de más gasto; `--ad <id>` para otros). Saca de cada pieza el
   primer fotograma, el arranque de 0–3 s a 4 fps y una hoja del vídeo entero en
   `clientes/<slug>/creativos/_fotogramas/<ad_id>/`, con `indice.json` (duración, aspecto, cortes, ritmo sugerido,
   segundo de cada casilla y huella visual; sin el nombre del anuncio ni el archivo de origen, para que el etiquetado
   sea a ciegas), y rellena los campos automáticos del CSV.
   - Busca la pieza en `ruta_creativo` o en `creativos/<nombre-base>/`. Si no está en local: `--api` (miniatura y
     duración desde Meta, solo lectura) y, si hay que ver el vídeo entero, `--api --descargar-video` (temporal que la
     herramienta borra al acabar).
   - Sin FFmpeg sale con código 2: `/doctor` dice cómo instalarlo; mientras, solo `--api`.
3. Lo que se dice no está en los fotogramas: úsalo del SRT o del guion del `LEEME.md` de la pieza si existen. Si no,
   los elementos que dependan del audio van como `duda`.

## 3. Etiquetar a ciegas con `critico-creativo`
1. `ec etiquetas esquema --json` (esquema fijo: valores, definiciones y criterio de duda) y
   `ec etiquetas pendientes --cliente <slug> --json`.
2. Llama a `critico-creativo` en lotes de hasta 10 anuncios `[HYPOTHESIS]`. Pásale el esquema entero, el criterio de
   duda tal cual, y por anuncio solo: `ad_id`, las imágenes de `_fotogramas/<ad_id>/`, su `indice.json` y el SRT o el
   guion si existen. **No le pases gasto, resultados, veredicto ni nombre del anuncio** (el nombre lleva ángulo y
   concepto y sesga). Pídele «devuelve solo JSON, no edites ningún archivo»: una lista de objetos con `ad_id` y las
   columnas manuales, solo con valores del esquema, `duda` cuando no esté seguro o no se vea, y `ritmo` confirmado con la
   hoja (el `ritmo_sugerido` falla con cortes de salto en un plano fijo).
3. Guarda la respuesta en `clientes/<slug>/datos/analisis-creativo/etiquetas_<AAAA-MM-DD>.json` y escríbela con
   `ec etiquetas poner --cliente <slug> --archivo <json> --por critico-creativo`. Si un valor no vale, no se escribe
   nada: corrige ese valor (o ponlo en `duda`) y repite.
4. Control de calidad: otra llamada independiente a `critico-creativo` con 5 anuncios al azar ya etiquetados
   `[HYPOTHESIS]`. En los elementos donde no coincidan en 2 o más de los 5, revisa la definición con el usuario y, mientras,
   cambia esos valores dudosos a `duda`. El usuario corrige lo que quiera con
   `ec etiquetas poner --cliente <slug> --ad <id> campo=valor --por usuario`.
5. `ec etiquetas validar --cliente <slug>` sin errores antes de seguir.

## 4. Qué elementos se asocian a ganar
`ec analizar --cliente <slug> --guardar` (y `--json` para leer el detalle). Cómo leerlo:
- **Capa de decisión**: la más cercana al dinero con ≥20 eventos en anuncios maduros. La madurez va por capa y por
  modelo (en servicios, citas 14 días, shows 21 y clientes de pago 56; sale en `madurez` del JSON) **[HYPOTHESIS]**:
  cámbiala con `--madurez capa=días` (repetible) o `--dias-madurez N` para todas. Un anuncio sin fecha fiable no
  cuenta como maduro en las capas de negocio. Si baja a leads, todo lo que salga es provisional: dilo.
- **Tres lecturas**: coste en la capa (razón de costes con IC 95 % que ya incluye la variación entre anuncios),
  ganadores frente a perdedores del registro (Fisher e IC de Newcombe) y atención (hook, hold y CTR; solo diagnostica).
  Las q son de Benjamini-Hochberg sobre todas las comparaciones de cada lectura.
- **Estados**: señal (q < 0,10), pista (p < 0,05 sin pasar la corrección), sin diferencia distinguible (no es «da
  igual»: puede faltar n), n insuficiente, confundido (el valor vive en un solo concepto) y «va siempre junto a» (dos
  valores en los mismos anuncios: con estos datos no se pueden separar).
- **Nunca causal**: el gasto no se reparte al azar y los elementos viajan con el concepto, la oferta y el momento
  (`12-razonamiento-estadistico.md` §8.3). «Repetir» quiere decir «sigue usándolo mientras no haya prueba en contra»;
  para saber si causa, `/test-creativo`.
- Si un elemento tiene muchas `duda`, no se puede leer: dilo en vez de forzarlo.

## 5. Retención del vídeo
`ec retencion --cliente <slug> --meta <csv del paso 1>`: hook rate, hold rate, retención por cuartiles, tiempo medio y
mayor caída de la curva por anuncio, contra las medianas de la cuenta, con el diagnóstico del árbol de
`07-analitica-creativa-metricas.md` §4 (apertura, cuerpo o «sigue el árbol por CTR, promesa y landing»).
- El hold de vídeos de ≤15 s está inflado por la definición de ThruPlay: compáralos por segundos, no por hold.
- Los cuartiles solo se comparan entre vídeos de duración parecida.
- **Anuncios multi-media (formato flexible)**: si la cuenta los usa, el *Creative breakdown* de Ads Reporting da
  resultados por imagen, vídeo y texto (`04-formatos-y-estilos.md` §6, `[EMPIRICAL]` de fuentes secundarias). Meta
  elige la combinación por persona: cada recurso llega a un público distinto, así que es una pista, no una comparación
  justa. Anótalo como pista en «Qué probar».

## 6. Conceptos casi iguales
`ec diversidad --cliente <slug> --guardar`:
- grupos que el sistema probablemente trata como uno (mismo ángulo y concepto en el nombre y mismo soporte, etiquetas
  de concepto iguales en ≥80 % o primer fotograma casi idéntico; umbrales `[HYPOTHESIS]`, el efecto es
  `[OFFICIAL META]`);
- conceptos efectivos por gasto, concentración por conjunto y dimensiones sin variedad (portavoz, estructura,
  consciencia, soporte, primer fotograma, audiencia nombrada, persona).
- Haz la prueba de la frase: una frase por grupo; si dos grupos caben en la misma frase, son el mismo concepto.
- Mira la cuadrícula (`creativos/_fotogramas/cuadricula_<fecha>.jpg`) y, si Ads Manager muestra la columna *Creative
  diversity* del conjunto, contrástala (`01-creative-es-targeting.md` §2).
- No propongas pausar ganadores para subir la diversidad.

## 7. Plan de suministro
`ec suministro --cliente <slug> --meta <csv del paso 1> --guardar` (o `--gasto-mensual`):
conceptos nuevos al mes = gasto mensual × `explorar_explotar` ÷ (2–3 × coste objetivo del evento que se optimiza)
`[STRONG INFERENCE]`, con `explorar_explotar` de la ficha `[HYPOTHESIS]`. Da la cadencia semanal, las 3–5 iteraciones
de cada ganador nuevo (no cuentan como conceptos), el techo orientativo por gasto y avisos de mezcla (sin ganadores,
70–90 % de conceptos nuevos: `13-produccion-y-feedback-loop-creativo.md` §4.3). Si sale menos de 1 al mes, explica las
salidas: decisiones más lentas, subir `explorar_explotar` o descartar antes con el filtro de atención.

## 8. Entregar: qué repetir, qué probar, qué dejar
Escribe `clientes/<slug>/informes/analisis-creativo/<AAAA-MM-DD>.md`:
1. **Datos**: periodo, ventana de atribución, capa de decisión y n, anuncios con gasto, etiquetados y con dudas,
   quién etiquetó y el control de calidad.
2. **Qué repetir** (máximo 5): elemento · evidencia (razón de costes o diferencia con IC, n por lado) · `[EMPIRICAL]`
   de esta cuenta · con qué va siempre junto.
3. **Qué probar** (máximo 5): pistas, confundidos («pruébalo en otro concepto»), señales de atención y huecos del
   playbook nunca probados, todos `[HYPOTHESIS]`, cada uno con el test que lo resolvería.
4. **Qué dejar** (máximo 5): mismo formato que repetir.
5. **Retención**: 3 líneas con los patrones (aperturas que fallan, dónde cae la curva).
6. **Diversidad**: grupos duplicados con su frase, conceptos efectivos, concentración y dimensiones sin variedad.
7. **Plan de suministro**: conceptos nuevos al mes y a la semana, iteraciones, techo y mezcla.
8. **Límites**: asociación, no causa; elementos ilegibles por dudas; anuncios inmaduros fuera.
Cada afirmación con su etiqueta de evidencia. Rutas relativas, fechas `AAAA-MM-DD`.

## 9. Revisión y cierre
1. `revisor-estrategia` revisa el informe: que nada se venda como causa, que los «repetir» tengan señal y no solo
   pista, que no haya folclore (`meta-ads-kb/12-mitos-contradicciones/01-mitos-meta-ads-2026.md`). Corrige o quita lo
   que tumbe y di por qué.
2. Por cada «repetir» o «dejar» con señal, propón una fila en `clientes/<slug>/aprendizajes-creativos.md`
   (Concepto = `elemento: <elemento> = <valor>`, Gasto y Conv del lado «con», CPA = coste en la capa, Veredicto =
   repetir|dejar, Por qué = razón con IC y q, Siguiente test). Escríbela solo con su OK.
3. Si algo contradice la KB, apúntalo para `curador-conocimiento` en `meta-ads-kb/16-aprendizajes-propios/`.
4. Siguiente paso: `/siguiente-anuncio <slug>` elige los próximos anuncios usando este informe y el plan de suministro.
   Esta skill no escribe en Meta, no produce ni borra nada.
