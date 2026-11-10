# Análisis creativo: qué elementos de tus anuncios funcionan

El registro creativo te dice qué anuncio gana. Esta guía va un paso más allá: qué tienen dentro los anuncios que ganan
(quién habla, qué se ve en el primer fotograma, si hay texto desde el segundo 0, cuánto dura, el ritmo, si se ve el
sistema funcionando, la prueba, la cifra, la llamada a la acción, los subtítulos…), cómo retiene cada vídeo, qué
anuncios son en realidad el mismo concepto y cuántos conceptos nuevos tienes que producir al mes.

Todo lo hace `/analisis-creativo <cliente>`. Aquí tienes qué pasa por dentro y cómo leer lo que sale. La herramienta es
`herramientas/elementos_creativos.py`; solo escribe archivos locales y solo lee de Meta.

## 1. Cuándo usarlo

- **Una vez al mes**, o cuando lleves 10 anuncios nuevos con gasto desde el último análisis **[HYPOTHESIS]**.
- **Con menos de 8 anuncios con gasto**, casi todo saldrá «n insuficiente». Es la respuesta honesta: etiqueta igual
  (servirá el mes que viene) y quédate con la diversidad y el plan de suministro.
- **No es para** elegir el próximo anuncio (`/siguiente-anuncio`, que sí lee lo que deja esta skill) ni para diseñar o
  leer un test (`/test-creativo`).

## 2. Lo que necesitas

| Qué | Para qué | Si no lo tienes |
|---|---|---|
| Ficha con targets en la tabla «Economía» | Capa de decisión y plan de suministro | `/economia` |
| Registro creativo actualizado | Gasto y resultados por anuncio | La skill lo actualiza (paso 1) |
| Las piezas en `clientes/<slug>/creativos/<nombre-base>/` | Fotogramas del vídeo o la imagen | `--api`: miniatura y duración desde Meta |
| FFmpeg | Sacar fotogramas, cortes y huella visual | `/doctor` te dice cómo instalarlo |
| Token avanzado (`docs/guias/token-avanzado.md`) | `fotogramas --api` y la retención por API | Exportación de Ads Manager |

## 3. El esquema de etiquetas

Cada anuncio con gasto tiene una fila en `clientes/<slug>/datos/elementos-creativos.csv`. El esquema es fijo para que
los meses se puedan comparar: `python3 -I herramientas/elementos_creativos.py etiquetas esquema` lo muestra entero con
sus definiciones.

| Columna | Valores | Qué mira |
|---|---|---|
| `soporte` · auto | video, imagen, carrusel | Sale del formato del nombre o de los fotogramas |
| `relacion_aspecto` · auto | 9x16, 4x5, 1x1, 16x9, otro | Del archivo |
| `duracion_s` · auto | segundos | FFmpeg o la API |
| `ritmo` · vídeo | lento, medio, rapido | Duración media de plano: < 2,5 s, 2,5–6 s, > 6 s **[HYPOTHESIS]** |
| `persona` | ninguna, real, ia | ¿Sale alguien? ¿Filmado o generado? |
| `quien_habla` | nadie, fundador, equipo, cliente, creador, experto, voz-en-off, avatar-ia | Quién lleva el mensaje |
| `primer_fotograma` | cara, pantalla, texto, dato, antes-despues, escena, marca, meme | Qué domina el fotograma 0 |
| `texto_0s` | no, si | Texto legible desde el primer fotograma |
| `gancho` | problema, resultado, pregunta, contraintuitivo, historia, llamada-audiencia, demo, prueba, oferta | Mecanismo de los 3 primeros segundos |
| `audiencia_nombrada` | no, sector, rol, ambos | ¿Nombra a quién va en los 3 primeros segundos? |
| `consciencia` | inconsciente, problema, solucion, producto, total | Nivel de consciencia (`meta-ads-kb/03-creatividad/03-estrategia-creativa-primeros-principios.md` §3) |
| `estructura` | caso, demo, antes-despues, testimonio, dato, lista, explicacion, comparativa, opinion, oferta, detras-de-camaras | La idea que sostiene la pieza |
| `demo` | no, breve, central | ¿Se ve el sistema funcionando? |
| `cifra` | no, gancho, cuerpo | Cifra concreta y dónde aparece |
| `menciona_ia` | no, gancho, cuerpo | ¿Dice «IA», «agente», «ChatGPT»…? (`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §8.1) |
| `filtro` | no, si | ¿Dice para quién no es? (`meta-ads-kb/03-creatividad/01-creative-es-targeting.md` §4.3) |
| `prueba_social` | ninguna, resultado-cliente, testimonio, logos, volumen, resenas, medios | La prueba más fuerte que se ve |
| `cta` | diagnostico, auditoria, llamada, demo, recurso, prueba-gratis, presupuesto, mensaje, ninguno | El siguiente paso que pide la pieza |
| `subtitulos` · vídeo | no, completos, clave | Subtítulos quemados |
| `acabado` | casero, pulido, plantilla | Estilo de producción |
| `tono` | didactico, cercano, provocador, humor, inspirador | Tono dominante |

Además: `huella_visual` (dHash del primer fotograma), `fuente_visual` (local, api-video o api-miniatura),
`etiquetado_por`, `fecha_etiquetado` y `notas`. Dos comodines valen en cualquier elemento: **`duda`** (no estoy seguro:
esa pieza no cuenta para ese elemento) y **`no-aplica`** (elemento de vídeo en un estático o un carrusel; se pone solo).

Ejemplo (Acme Automations, un vídeo del fundador contando el caso de una gestoría):

```csv
ad_id,nombre,soporte,relacion_aspecto,duracion_s,ritmo,persona,quien_habla,primer_fotograma,texto_0s,gancho,...
120000000000101,20261102_tiempo-perdido_caso-gestoria_founder_h1,video,9x16,38.4,medio,real,fundador,cara,si,resultado,...
```

## 4. Cómo se etiqueta

1. `fotogramas` saca de cada pieza el primer fotograma (`f0.jpg`), el arranque de 0–3 s a 4 fps (`arranque.jpg`), una
   hoja con 15 momentos del vídeo (`hoja.jpg`) e `indice.json` con la duración, los cortes, el ritmo sugerido y el
   segundo de cada casilla (sin el nombre del anuncio ni el del archivo: llevan ángulo y concepto). Solo trabaja con
   los anuncios de la última exportación de `registro_creativo.py actualizar`; `--todos` incluye el resto del
   registro, mezclando periodos. Con `--cuadricula`, monta además la «prueba de la cuadrícula» con todos los primeros
   fotogramas.
2. `critico-creativo` etiqueta **a ciegas**: no ve gasto, resultados, veredicto ni el nombre del anuncio. Lo que se dice
   lo toma del SRT o del guion del `LEEME.md`; si no hay, lo que dependa del audio va como `duda`.
3. **Criterio de duda**: si duda entre dos valores o no se ve en los fotogramas, `duda`. Mejor un hueco que una etiqueta
   inventada: una etiqueta inventada contamina la comparación; un hueco solo resta n.
4. **Control de calidad**: otra pasada independiente sobre 5 anuncios al azar **[HYPOTHESIS]**. Si en un elemento no
   coinciden en 2 de 5, la definición no es lo bastante clara para tu cuenta: esos valores pasan a `duda` hasta que la
   aclaréis.
5. Tú corriges lo que quieras:
   `python3 -I herramientas/elementos_creativos.py etiquetas poner --cliente acme --ad 120000000000101 cifra=gancho --por usuario`.
   Si un valor no existe en el esquema, no se escribe nada.

## 5. Cómo se lee el análisis

`analizar` cruza las etiquetas con el registro y hace tres lecturas. **Ninguna es causal**: el gasto no se reparte al
azar y los elementos viajan juntos con el concepto, la oferta y el momento
(`meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md` §8.3). Que los anuncios con el
fundador a cámara tengan mejor coste por cita no prueba que el fundador sea la causa; para eso, `/test-creativo`.

**1. Coste en la capa de decisión.** La capa más cercana al dinero (cliente de pago > show > cita > cualificado > lead
en servicios; cliente de pago > activación > prueba > lead en SaaS) con al menos 20 eventos en anuncios maduros. La
madurez va por capa: en servicios, 14 días para citas, 21 para shows y 56 para clientes de pago; en SaaS, 7 para
pruebas, 14 para activaciones y 28 para clientes de pago **[HYPOTHESIS]** (`--madurez capa=días` las cambia). Un anuncio
sin fecha fiable no cuenta como maduro en esas capas. Para cada valor de cada elemento:

```
razón de costes = (gasto con el valor / eventos con el valor) ÷ (gasto sin él / eventos sin él)
```

Menos de 1 es mejor. El IC 95 % se calcula en escala logarítmica con la variación real entre anuncios (cuasi-Poisson:
si los anuncios de un mismo lado difieren mucho entre sí, el intervalo se ensancha). Las q corrigen por haber hecho
muchas comparaciones a la vez (Benjamini-Hochberg, `12-razonamiento-estadistico.md` §8.2).

**2. Ganadores frente a perdedores.** Con los veredictos del registro: qué proporción de ganadores y de perdedores
tiene el valor, la diferencia con su IC 95 % (Newcombe) y la p exacta de Fisher.

**3. Atención (solo diagnostica).** Hook rate = vistas de 3 s ÷ impresiones; hold rate = ThruPlays ÷ vistas de 3 s
(sin vídeos de ≤ 15 s, que lo inflan); CTR. La atención no predice negocio por sí sola
(`meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md`, TL;DR): una señal aquí va a «qué probar», nunca a
«qué repetir».

| Estado | Qué significa | Qué haces |
|---|---|---|
| Señal a favor / en contra | q < 0,10 **[HYPOTHESIS]** | Repetir / dejar, `[EMPIRICAL]` de esta cuenta |
| Pista | p < 0,05 pero no pasa la corrección | Probar, `[HYPOTHESIS]` |
| Sin diferencia distinguible | No se distingue del resto con estos datos | Nada. No es «da igual»: puede faltar n |
| N insuficiente | < 10 eventos o < 2 anuncios en un lado | Esperar |
| Confundido | El valor solo aparece en un concepto | Probarlo en otro concepto |
| Va siempre junto a | Dos valores están en los mismos anuncios | No se pueden separar: se informan juntos |

Umbrales y de dónde salen:

| Umbral | Valor | Evidencia |
|---|---|---|
| Eventos por lado para comparar costes | 10 | `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` §5 (ganador provisional con 10–20) |
| Eventos para usar una capa | 20 | **[HYPOTHESIS]** (dos lados de 10) |
| Anuncios por lado | 2 | **[HYPOTHESIS]** |
| Ganadores y perdedores etiquetados | 3 y 3 | **[HYPOTHESIS]** |
| Impresiones por lado para hook rate y CTR | 2.000 | `05-framework-testing-creativo.md` §2 (1.000–2.000 por variante) |
| Vistas de 3 s por lado para hold rate | 500 | **[HYPOTHESIS]** |
| Días para que madure cada capa (servicios: citas, shows, clientes de pago) | 14, 21 y 56 | **[HYPOTHESIS]**; mídelo con `embudo.py cohortes` y pásalo con `--madurez capa=días` |

## 6. Retención del vídeo

`python3 -I herramientas/meta_ads.py anuncios` trae ahora, además de hook rate y hold rate:

| Columna | Fórmula | Campo de la Marketing API |
|---|---|---|
| `video_p25` … `video_p100` | Reproducciones hasta el 25/50/75/95/100 % | `video_p25_watched_actions` … `video_p100_watched_actions` |
| `retencion_p25` … `retencion_p100` | `video_pXX` ÷ vistas de 3 s × 100 | — |
| `reproducciones` | Inicios de reproducción | `video_play_actions` |
| `vistas_2s_continuas` | Vistas de 2 s seguidos | `video_continuous_2_sec_watched_actions` |
| `tiempo_medio_s` | Tiempo medio de visualización | `video_avg_time_watched_actions` |
| `curva_retencion` | % de quien empezó que sigue en cada punto, separado por «\|»: segundos 0–14, luego tramos de 15–20, 20–25, 25–30, 30–40, 40–50, 50–60 y más de 60 s | `video_play_curve_actions` |

Nombres comprobados en la referencia de Insights de la Marketing API el 2026-11-09 **[OFFICIAL META]**. Meta marca
algunos como «en desarrollo»: si tu cuenta rechaza la petición por un campo no válido (error 100), la herramienta
repite sin los campos nuevos, te avisa y esas columnas salen vacías (no a cero).

`retencion` lee ese CSV y da por anuncio la mayor caída de la curva en los primeros 15 s y un diagnóstico contra la
mediana de tu cuenta, siguiendo el árbol de `07-analitica-creativa-metricas.md` §4: hook rate por debajo del 50 % de
la mediana es un problema de apertura; buen gancho con hold rate por debajo del 50 % de la mediana, de cuerpo **[HYPOTHESIS]**
para este segundo corte. Dos cuidados: el hold de los vídeos de ≤ 15 s está inflado por cómo se define ThruPlay, y los
cuartiles solo se comparan entre vídeos de duración parecida (el 25 % de un vídeo de 12 s es el segundo 3; el de uno
de 60 s, el 15).

Si usas anuncios multi-media (formato flexible), el *Creative breakdown* de Ads Reporting da resultados por imagen,
vídeo y texto (`meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` §6, **[EMPIRICAL]** de fuentes secundarias). Meta
elige la combinación por persona, así que cada recurso llega a un público distinto: tómalo como pista, no como
comparación justa. La herramienta no lo descarga.

## 7. Conceptos casi iguales

Meta dice que los anuncios demasiado parecidos pueden mostrarse a las mismas personas y no tratarse como distintos
**[OFFICIAL META]**; el mecanismo exacto y cualquier porcentaje de similitud no son oficiales
(`meta-ads-kb/03-creatividad/01-creative-es-targeting.md` §2). `diversidad` une dos anuncios en un grupo si:

- comparten ángulo y concepto en el nombre y el soporte (cambiar el hook es iterar, no diversificar; un estático y un
  vídeo del mismo mensaje sí cuentan como ejecuciones distintas);
- sus etiquetas de concepto coinciden en un 80 % o más, ponderadas (ángulo 3, estructura 2, quién habla 1,5,
  consciencia 1,5, audiencia nombrada, soporte y primer fotograma 1, persona y tono 0,5) **[HYPOTHESIS]**;
- o su primer fotograma es casi idéntico: huella dHash a 10 bits o menos de 64 **[HYPOTHESIS]**. Es una aproximación a
  la similitud visual, no la columna de Meta. La miniatura de la API no siempre es el fotograma 0: compara con cautela
  huellas de fuentes distintas.

Después calcula los **conceptos efectivos por gasto** = 1 ÷ Σ (cuota de gasto de cada grupo)². Diez anuncios donde dos
grupos se llevan el 60 % y el 30 % del gasto y el 10 % restante se reparte entre otros 8 equivalen a unos 2,2
conceptos. Si en un conjunto
los 2 anuncios con más gasto se llevan más del 80 % durante 2–3 semanas y suben coste y frecuencia, toca meter
conceptos nuevos, no variaciones (umbral orientativo **[HYPOTHESIS]** de la KB). Y lista las dimensiones sin variedad
(por ejemplo, el 90 % del gasto con el fundador a cámara). Si Ads Manager te muestra la columna *Creative diversity*
del conjunto, contrástala. No pauses ganadores para subir la diversidad.

## 8. Plan de suministro

```
conceptos nuevos al mes = gasto mensual × explorar_explotar ÷ (2–3 × coste objetivo del evento que optimizas)
```

Es la regla de capacidad de `05-framework-testing-creativo.md` (TL;DR) y de
`meta-ads-kb/03-creatividad/13-produccion-y-feedback-loop-creativo.md` §4.2 **[STRONG INFERENCE]**: cada concepto
necesita gastar 2–3 veces el coste objetivo para que su veredicto valga algo. `explorar_explotar` sale de la ficha
(0,3 por defecto, **[HYPOTHESIS]**).

Ejemplo con Acme Automations: 3.000 € al mes, `explorar_explotar` 0,3 y un target de 67 € por diagnóstico (el lead que
optimiza): 900 € para explorar → entre 4,5 (con 3×) y 6,7 (con 2×) conceptos al mes; recomienda 4, uno por semana.
Aparte, cada ganador nuevo pide 3–5 iteraciones (otros hooks, formatos o personas; `05-framework-testing-creativo.md`
§7), que no cuentan como conceptos, y el total no debería pasar del techo orientativo por gasto de §3 (con unos
100 € al día, 2–4 anuncios nuevos por semana). Sin ganadores todavía, la KB sugiere que el 70–90 % de lo que produzcas
sean conceptos nuevos (`13-produccion-y-feedback-loop-creativo.md` §4.3).

Si sale menos de un concepto al mes, no lances más de los que puedes leer: acepta decisiones más lentas, sube
`explorar_explotar` o descarta antes con el filtro de atención.

## 9. Archivos que deja

| Archivo | Qué es |
|---|---|
| `clientes/<slug>/datos/elementos-creativos.csv` | Etiquetas por anuncio |
| `clientes/<slug>/creativos/_fotogramas/<ad_id>/` | Fotogramas e `indice.json` (no es una pieza: empieza por `_`) |
| `clientes/<slug>/creativos/_fotogramas/cuadricula_<fecha>.jpg` y `.md` | Prueba de la cuadrícula y su índice |
| `clientes/<slug>/datos/analisis-creativo/<fecha>_elementos.json` | Análisis de elementos |
| `clientes/<slug>/datos/analisis-creativo/<fecha>_diversidad.json` | Grupos y conceptos efectivos |
| `clientes/<slug>/datos/analisis-creativo/<fecha>_suministro.json` | Plan de suministro (lo lee `/siguiente-anuncio`) |
| `clientes/<slug>/informes/analisis-creativo/<fecha>.md` | Informe: qué repetir, qué probar, qué dejar |

## 10. Límites que conviene tener presentes

- **Asociación, no causa.** Siempre. Lo que «repetir» dice es «sigue usándolo mientras nada lo contradiga».
- **Con poco gasto, la mayoría de elementos no se pueden leer.** No es un fallo de la herramienta.
- **Las etiquetas son juicios.** Por eso el esquema es cerrado, el etiquetado es a ciegas y existe `duda`.
- **El ritmo sugerido** cuenta cortes con el detector de escenas de FFmpeg, que no ve los cortes de salto en un plano
  fijo a cámara: el agente lo confirma con la hoja.
- **La duración por API** sale del campo `length` del vídeo, que la referencia que consultamos no lista entre sus
  campos: si Meta no lo devuelve, queda vacía y la rellena `fotogramas` con el archivo.
- **Elementos que van juntos**: si en tu cuenta todos los vídeos del fundador abren con su cara y cuentan un caso, el
  análisis no puede decirte cuál de las tres cosas funciona. Rompe esa coincidencia a propósito en los próximos
  conceptos.
