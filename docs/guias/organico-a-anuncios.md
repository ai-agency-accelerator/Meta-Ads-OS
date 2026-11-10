# Orgánico a anuncios: lo que ya funcionó, ahora en pago

Si tú o el fundador de tu cliente publicáis en Instagram, LinkedIn, YouTube o un pódcast, tenéis algo que ningún
brief da: mensajes que vuestro público ya ha visto, guardado y compartido. Con esta guía eliges cuáles merecen dinero y
los conviertes en anuncios por una de dos vías:
- **publicación existente**, que conserva la prueba social;
- **clip** montado con cutkit desde el original.

Lo hace la skill **`/organico-a-anuncios <cliente>`**: aquí tienes el porqué y el paso a paso. Para casos de clientes,
testimonios y creadores, `/casos-y-creadores`. Para iterar un anuncio que ya tienes, `/variantes`.

## 1. Por qué y cuándo

- **El orgánico es un pre-test barato.** Lo que retiene y se comparte en frío suele tener buenas métricas de atención
  como anuncio. **[STRONG INFERENCE]**. Fuente: `meta-ads-kb/07-instagram-placements-mensajeria/07-organico-mas-pagado-post-ids-boost.md`
  §1.
- **La atención no predice el negocio.** Un reel con mucha retención puede traer leads que no cualifican. La puntuación
  orgánica decide qué se prueba; el coste por llamada asistida, cualificado o venta decide qué gana. **[STRONG
  INFERENCE]**. Fuente: `meta-ads-kb/03-creatividad/07-analitica-creativa-metricas.md` §3.
- **La prueba social ayuda, pero menos de lo que se cree.** Un anuncio nuevo, sin los más de 6.000 comentarios del
  original, tuvo un coste por lead parecido en dos semanas. **[EMPIRICAL, n=1]**. Fuente: archivo 07/07 §3. No la
  protejas a costa de dejar de iterar.
- **En venta consultiva encaja especialmente bien.** Un post con un caso o un vídeo explicando un error es el mejor
  candidato a anuncio. **[STRONG INFERENCE]**. Fuente: `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`
  §2.3.

| Merece la pena | No merece la pena |
|---|---|
| El contenido habla del problema que resuelve tu oferta, al que compra (dueño o gerente de pyme) | Habla a colegas del sector o es humor sin relación con la oferta, aunque sea viral |
| Sigue siendo verdad: herramientas, precios y casos vigentes | Cita herramientas o precios que han cambiado (en IA, pasa en meses) |
| Tienes el original o el post es elegible | Lleva música de la biblioteca o salen personas sin permiso, y no hay original limpio |

## 2. Qué necesitas

- La Página y la cuenta profesional de Instagram en el portfolio, con acceso de anuncios (`/configurar-meta`).
- Las estadísticas de cada red: exportación de Meta Business Suite, YouTube Studio o LinkedIn. Lo ves en la sección 3.
- Para clips, los **originales** con la mejor calidad que tengas (no la descarga comprimida de la red) y cutkit
  instalado (`docs/guias/video-propio.md` §2).
- Si el fundador publica desde su cuenta: que sea profesional y que acepte anunciarse con su identidad.
- Si eres agencia: el OK escrito del cliente para usar su orgánico en anuncios.

## 3. Reúne el contenido

La skill monta `clientes/<slug>/investigacion/organico/<AAAA-MM-DD>/inventario.csv`, con una fila por publicación de
los últimos 6–12 meses. Solo guarda recuentos y frases literales, nunca usuarios ni comentarios con su autor.

| Red | De dónde salen los datos | Qué hay que pedir a mano |
|---|---|---|
| Instagram y Facebook | El MCP de Meta lista tus publicaciones con su ID (`ads_get_ig_media`) | Guardados, compartidos y retención: el MCP no tiene el permiso de estadísticas de Instagram **[STRONG INFERENCE]**. Pide la exportación de Business Suite (Estadísticas → Contenido → Exportar) y, de los reels finalistas, el tiempo medio de visualización y la tasa de salto que da la app |
| Instagram, sin MCP | `python3 -I herramientas/ig_competidores.py <tu_usuario> --posts 100 --cliente <slug>` | Solo da likes y comentarios: sirve para listar publicaciones, no para puntuarlas |
| Cuenta personal del fundador | Si no está en el portfolio, sus estadísticas o capturas | Nunca pidas contraseñas |
| YouTube | Exportación de YouTube Studio y la curva de retención de cada vídeo largo | El texto, con `python3 -I herramientas/transcribir.py "<url>" --cliente <slug>` (solo subtítulos); con `--tiempos`, cada frase con su minuto y un `.srt` al lado |
| LinkedIn | Exportación de las analíticas de cada publicación (XLSX) | LinkedIn no tiene «publicación existente» en Meta: solo clip o estático |
| Pódcast, talleres, directos | La ruta del archivo original | Se trocean en la sección 7 |

## 4. Puntúa por lo que predice un anuncio

Cada señal se compara con la **mediana de la cuenta** para el mismo tipo de publicación y periodo:

| Frente a la mediana | Puntos |
|---|---|
| < 0,8× | 0 |
| 0,8–1,5× | 1 |
| 1,5–3× | 2 |
| > 3× | 3 |

Los puntos se multiplican por el peso de la señal. Escala y pesos son **[HYPOTHESIS]**: ajústalos cuando tengas datos
de qué orígenes ganan en pago.

| Señal | Peso | Por qué |
|---|---|---|
| Retención (tiempo medio ÷ duración; en YouTube, porcentaje medio visto) | ×3 | Es lo que más se parece a parar el scroll y quedarse |
| Compartidos ÷ alcance | ×2 | Alguien lo manda a un socio o a su jefe |
| Guardados ÷ alcance | ×2 | Lo quieren usar después |
| Comentarios con intención | ×2 | Preguntan cómo se hace, el precio o «¿sirve para mi sector?», piden la plantilla o etiquetan a quien decide. Emojis, felicitaciones y el propio equipo no cuentan; los provocados por «comenta X» cuentan la mitad |
| Seguidores y visitas al perfil | ×1 | Interés por quién lo dice |
| Likes | 0 | Solo desempatan |

El máximo es 30. Antes de puntuar, quedan fuera las publicaciones que no encajan con la oferta, las que ya no son
verdad, las que tienen derechos sin resolver y las que llegaron a menos de la mitad de la mediana de alcance o a menos
de 300 cuentas **[HYPOTHESIS]**.

**Ejemplo (Acme Automations, reels de los últimos 6 meses).** Las medianas de la cuenta son estas:
- alcance, 2.400;
- retención, 28 %;
- compartidos, 0,4 %;
- guardados, 0,6 %;
- comentarios con intención, 0,5 por cada 1.000 de alcance;
- seguidores ganados, 1,0 por cada 1.000 de alcance.

| Reel | Retención | Compartidos | Guardados | Intención | Seguidores | Puntos | Decisión |
|---|---|---|---|---|---|---|---|
| «El lunes de los albaranes» (fundador, 38 s, alcance 3.100) | 52 % → 2 | 1,4 % → 3 | 1,5 % → 2 | 2,3 → 3 | 1,8 → 2 | **24** | Publicación existente: arranca fuerte y el pie sirve |
| «Demo: el presupuesto que se hace solo» (pantalla, 52 s, alcance 1.900) | 31 % → 1 | 0,5 % → 1 | 1,9 % → 3 | 1,6 → 3 | 0,9 → 1 | **18** | Clip: los 6 primeros segundos son «hola, hoy os enseño…» |
| «Meme de ChatGPT» (alcance 18.000, 2.300 likes) | 35 % → 1 | 0,9 % → 2 | 0,2 % → 0 | 0,1 → 0 | 0,7 → 0 | 7 | Fuera: no encaja con la oferta, a pesar de los likes |
| «Nuestra cena de equipo» (alcance 900) | — | — | — | — | — | — | Fuera por encaje y por alcance mínimo |

Las cifras de intención y seguidores son por cada 1.000 de alcance.

## 5. Publicación existente o clip

| | Publicación existente | Clip |
|---|---|---|
| Prueba social | Se conserva y se acumula entre todos los anuncios que usen el mismo post | Empieza de cero |
| Texto principal | El pie del post: no se edita mientras haya un anuncio conectado | Libre: 2–3 textos y titulares |
| Hooks | El que tiene | Los que quieras (`_h1`, `_h2`…) |
| Formatos | El del post | 9:16 y 4:5 |
| Botón, URL y UTMs | Sí, en el anuncio | Sí |
| Mejoras automáticas | Qué se aplica no está documentado: míralo en la pantalla | Según `mejoras_automaticas` de la ficha |
| Cómo se publica hoy con el OS | Ads Manager, guiado (sección 6), o con el token avanzado, `meta_ads.py crear` (`publicacion_ig` / `publicacion_fb`) | `/publicar-anuncios`, como cualquier vídeo |

Elige **publicación existente** cuando el post es de una cuenta que puede ser la identidad del anuncio, es elegible,
engancha en los 2 primeros segundos, su pie funciona como texto de anuncio y sus comentarios suman.

Elige **clip** en los demás casos:
- viene de YouTube, LinkedIn, un pódcast o un taller;
- es horizontal o dura más de 60–90 s;
- arranca lento o lleva música con licencia;
- el pie dice «enlace en la bio» o tiene fechas caducadas;
- quieres probar varios hooks.

Si haces las dos cosas con el mismo contenido, son dos anuncios del **mismo concepto** (una iteración), no dos
conceptos.

## 6. Publicación existente, paso a paso

**Antes de abrir Ads Manager:**
1. Apunta el ID en el LEEME. En Instagram es el `id` que da `ads_get_ig_media`; en Facebook, `<pagina>_<post>`. En
   Ads Manager también lo ves en la columna de ID del listado de publicaciones.
2. Mira los 2 primeros segundos tal y como saldrán: imagen y voz desde el primer fotograma, y texto fuera de las zonas
   que tapa la interfaz (`meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md` §2).
3. Lee los comentarios. Los negativos sin responder y el spam se acumularán en el anuncio.
4. Pasa la revisión de políticas (sección 10): el pie del post es tu texto principal.

**En Ads Manager** (lo haces tú, y Claude te guía):
1. Abre el conjunto de destino del lote y pon el nombre exacto del anuncio (validado con `nomenclatura.py`).
2. Identidad: la Página y la cuenta de Instagram de la ficha.
3. «Usar publicación existente» → Instagram o Facebook → la del ID del LEEME.
4. Destino web, botón, URL sin UTMs y la plantilla de UTMs en «Parámetros de URL»
   (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8).
5. Mejoras automáticas según la ficha.
6. Previsualiza en Feed, Reels y Stories y crea el anuncio **en pausa**.
7. Pasa el ID del anuncio a Claude: `operador-meta` comprueba en solo lectura que la creatividad apunta al post del
   LEEME (`source_instagram_media_id` u `object_story_id`) y lo registra en el change log y el registro creativo.

**Si el post es de la cuenta del fundador:** es un anuncio de colaboración con la marca. Necesitas su código del post
o un permiso de cuenta. Si las dos cuentas son del mismo negocio y tienes acceso de anuncios a ambas, no hace falta
permiso **[OFFICIAL META]**. La checklist completa está en `.claude/skills/casos-y-creadores/publicar-colaboracion.md`.

**Por API, con el token avanzado** (`docs/guias/token-avanzado.md`). En el plan de `meta_ads.py crear`, el anuncio
lleva el ID de la publicación en vez de `video` o `imagen`:

```json
{"nombre": "20261116_tiempo-perdido_post-fundador_founder_h1", "publicacion_ig": "17900000000000123",
 "cta": "LEARN_MORE", "url": "https://acme-automations.example/diagnostico"}
```

- `publicacion_ig`: el ID numérico del medio de Instagram. La creatividad lleva `object_id` (la Página),
  `instagram_user_id` (`meta.instagram` de la ficha) y `source_instagram_media_id` **[OFFICIAL META]**.
- `publicacion_fb`: `<pagina>_<post>`, de la Página del plan o la ficha. La creatividad lleva `object_story_id` y, si
  la ficha tiene Instagram, `instagram_user_id` para que salga también allí.
- `url` y `cta` ponen el botón; las UTMs van en `url_tags`, como en el resto de anuncios. `texto`, `titulo`,
  `descripcion` y `miniatura` se ignoran (el anuncio enseña el pie y el medio de la publicación) y `--simular` lo avisa.
- Con destino formulario instantáneo no se admite: la vía por API no está verificada. Ese caso, en Ads Manager.
- Si Meta responde «Creative Must Provide enroll_status for Standard Enhancements» o «Creative is missing DOF spec»,
  Meta pide el bloque de mejoras automáticas: `off` y `revisar` lo mandan y `on` no, así que con `on` prueba con
  `revisar` (`mejoras_automaticas` de la ficha). Es un error documentado por Meta, no probado aún en una cuenta.
- No valen las publicaciones de IGTV ni los reels con música con derechos.

`boost_eligibility_info` dice si un medio de Instagram se puede promocionar **[OFFICIAL META]**. Lo que `crear` deja
en pausa se comprueba igual que en Ads Manager: el paso 7 de arriba.

**Nada de «Promocionar» desde la app para captar.** El Boost tiene opciones recortadas y no optimiza a lead,
registro ni cita (archivo 07/07 §4). Usa el mismo post dentro de un conjunto de tu campaña.

## 7. Clip, paso a paso

1. **Encuentra el tramo.** En un vídeo corto suele ser el vídeo entero. En uno largo (pódcast, taller) busca en la
   transcripción el resultado, la afirmación contraria o la pregunta de un cliente. Para tener tiempos por palabra:
   ```bash
   uv run --project modulos/cutkit ck new podcast-gestoria --cliente acme --raw episodio-12.mp4 --fmt anuncio
   ```
   Deja `creativos/<AAAA-MM-DD>_podcast-gestoria/edicion/transcript.md` con cada palabra y su segundo. Es gratis y
   local con whisper.cpp (`ck instalar --whisper`). Esa carpeta es de trabajo: sin LEEME no cuenta como pieza.
   Si el vídeo es público y tiene subtítulos, sin descargarlo:
   `python3 -I herramientas/transcribir.py "<url>" --cliente acme --tiempos` da cada frase con su minuto
   (`[14:02] …`) y un `.srt` al lado. Los tiempos son los de los subtítulos, por frase y no por palabra (en los
   automáticos, aproximados): bastan para encontrar el tramo y cortarlo con margen.
2. **Criterio del tramo:** 20–60 s **[HYPOTHESIS]**, que se entienda sin contexto y que arranque con la frase más
   fuerte, no con «como decía antes…».
3. **Corta:**
   ```bash
   python3 -I herramientas/editar_video.py cortar episodio-12.mp4 --desde 842 --hasta 889 \
       --salida clientes/acme/creativos/20261116_horas-perdidas_gestoria-que-no-teclea_podcast/brutos/tramo.mp4
   ```
4. **Monta** con el hook en los 2 primeros segundos, subtítulos y marca:
   ```bash
   uv run --project modulos/cutkit ck anuncio clientes/acme/creativos/20261116_horas-perdidas_gestoria-que-no-teclea_podcast/brutos/tramo.mp4 \
       --cliente acme --slug gestoria-que-no-teclea --nombre 20261116_horas-perdidas_gestoria-que-no-teclea_podcast_h1 \
       --salida clientes/acme/creativos/20261116_horas-perdidas_gestoria-que-no-teclea_podcast/ \
       --hook "Esta gestoría ya no teclea facturas" --cta "Pide tu diagnóstico" --foco 0.3
   ```
   El encuadre se elige con `--foco`:
   - `--foco auto` para una persona en plano horizontal;
   - `--foco <0–1>` para un pódcast a dos, sobre quien habla (0 es el borde izquierdo);
   - `--foco centro` para una demo de pantalla.
5. **Revisa:** la QA de cutkit (`pass`, o `warn` leído y aceptado) y los fotogramas a 0, 0,5, 1 y 2 s
   (`docs/guias/video-propio.md` §6).
6. **Hooks alternativos** del mismo clip: `/variantes`.

## 8. Derechos: si algo falla, la pieza no sigue

- [ ] **Música:** la de la biblioteca de Instagram impide promocionar el post y no vale en anuncios **[OFFICIAL META]**.
      Solo valen el audio original, la Sound Collection de Meta o una pista con licencia para publicidad de pago,
      guardada con su `<pista>.licencia.txt` en `clientes/<slug>/marca/musica/`.
- [ ] **Personas:** quien sale o habla y no es el anunciante (invitado, cliente, empleado) firma un permiso de uso
      publicitario con plataformas, territorio, duración y revocación. Sin permiso, se recorta o se descarta.
- [ ] **Pantallas:** sin emails, teléfonos, nombres de leads ni datos de clientes. Se desenfocan o se quitan.
- [ ] **Logos:** los de clientes, solo con permiso. Las herramientas de terceros pueden salir, pero sin sugerir que
      te avalan.
- [ ] **Elementos del post:**
      - los efectos y GIF no se admiten en anuncios de reels **[OFFICIAL META]**;
      - los reels con elementos que se tocan (encuestas, preguntas) no se pueden usar en anuncios, según la
        documentación de anuncios de colaboración **[OFFICIAL META]**; en el resto de casos, lo confirma Ads Manager;
      - los reels anteriores al 2021-10-15 y los vídeos de IGTV no son elegibles **[OFFICIAL META]**. Fuente: archivo
        07/07 §6 y la documentación de la Marketing API, consultada el 2026-11-09.
- [ ] **Contenido de terceros** (clips ajenos, capturas de noticias): fuera.
- [ ] **IA:** si hay voz, persona o escena sintética, la pieza lleva etiqueta de IA y se marca la de Meta al publicar.

## 9. Nombres, LEEME y lote

- **Nombre base:**
  ```bash
  python3 -I herramientas/nomenclatura.py generar --fecha 2026-11-16 --angulo "Horas perdidas" \
      --concepto "lunes de albaranes" --formato founder --hook 1
  # → 20261116_horas-perdidas_lunes-de-albaranes_founder_h1
  ```
  La carpeta es `creativos/20261116_horas-perdidas_lunes-de-albaranes_founder/`. El formato del nombre depende del
  contenido: `founder`, `podcast`, `demo`, `carrusel` o `estatico`.
- **LEEME** con la plantilla de `/producir-video` (`Vía: propio`), más una línea de origen bajo «Ángulo»:
  ```
  - **Origen orgánico:** instagram · publicacion-existente · <permalink> · publicado 2026-09-22 · <ID del medio>
  ```
  En una publicación existente, la tabla «Archivos» lleva una fila
  `(publicación existente) <ID> | <nombre-base>_h1 | original | Feed, Reels, Stories`.
- **Lote:** `creativos/_lotes/<AAAA-MM-DD>_organico/lote.md`, con la tabla de `/brief-creativo`. En las publicaciones
  existentes, `Texto principal` es «texto de la publicación».

## 10. Políticas y publicación

- `critico-creativo` mira cada pieza como un espectador en el móvil, también la publicación existente tal y como
  saldrá.
- `revisor-politicas` revisa el pie del post o los textos del anuncio, el texto en pantalla, lo que se dice y la
  landing, y escribe la línea de veredicto en el LEEME. Solo valen las afirmaciones aprobadas en la ficha o un caso con
  permiso; nada de ahorros ni ingresos garantizados
  (`meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`).
- Con las piezas en `lista`: `/publicar-anuncios <cliente> <AAAA-MM-DD>_organico`. Los clips se suben como cualquier
  vídeo. Las publicaciones existentes, con la sección 6.
- Van en los mismos conjuntos que el resto de conceptos y se miden con `/test-creativo`. No hace falta una campaña
  de «orgánico».

## 11. Después

- **Decide con la capa más baja que tenga datos suficientes:** llamadas asistidas, cualificados o ventas. Nunca con
  la puntuación orgánica.
- **Para escalar un ganador**, reutiliza su ID de publicación en otros conjuntos: el post acumula la prueba social.
  Duplicarlo crea posts nuevos que empiezan de cero (archivo 07/07 §2).
- **Revisa los comentarios a diario.** Los que muestran intención son preguntas frecuentes públicas y leads
  (`/seguimiento-leads`). La moderación la haces tú en la app: el OS no borra ni oculta comentarios
  (`meta-ads-kb/03-creatividad/12-comentarios-y-prueba-social.md`).
- **Ojo al comparar el post antes y después:** sus estadísticas orgánicas no cuentan las interacciones del anuncio;
  las métricas `total_*` sí **[OFFICIAL META]**.
- **Repite la skill cada mes** y apunta en `aprendizajes-creativos.md` qué origen gana (existente o clip) y qué
  señal orgánica acertó.

## 12. Publica pensando en el anuncio

Lo que publiques a partir de hoy puede ser el anuncio del mes que viene. Para que sea elegible y se pueda montar:
- [ ] audio original o de la Sound Collection, sin canciones de la biblioteca;
- [ ] sin stickers, GIF, encuestas ni efectos de cámara;
- [ ] hook dicho y escrito en los 2 primeros segundos, sin «hola, soy…»;
- [ ] texto importante dentro de las zonas seguras (archivo 07/03 §2);
- [ ] grabado en vertical con aire arriba y abajo, para poder recortar a 4:5;
- [ ] pie que funcione como texto de anuncio: sin «enlace en la bio» ni fechas;
- [ ] el original guardado en máxima calidad, en `clientes/<slug>/creativos/<…>/brutos/` o donde lo encuentres;
- [ ] permisos firmados de quien sale, antes de publicar.

**Trial Reels como pre-test.** Instagram enseña primero un Trial Reel a no seguidores y da sus métricas a las ~24 h
**[OFFICIAL META]**. Publica 3–5 hooks como Trial Reels y quédate con el que más se comparte por vista y más retiene.
Compártelo con todos para que acumule prueba social y llévalo a anuncio como publicación existente. Es un filtro de
creatividad, no de conversión: su audiencia no la controlas **[STRONG INFERENCE]**
(`meta-ads-kb/07-instagram-placements-mensajeria/04-instagram-a-fondo.md` §6). Los requisitos de elegibilidad no
están verificados.

## 13. Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El post no aparece en «Usar publicación existente» | La cuenta de Instagram no es la identidad del anuncio, lleva música con licencia o es un reel anterior a 2021-10-15 | Revisa la identidad; si no es elegible, clip desde el original |
| No puedo cambiar el texto | El post tiene un anuncio conectado (activo o no) | Si el texto no sirve, es clip |
| El anuncio de colaboración queda «pendiente de entrega» | El fundador no ha aprobado el permiso | Que lo apruebe; no actives nada antes |
| Gana el post viral y luego no trae leads | Se saltó el filtro de encaje | Vuelve a la sección 4: la atención no es negocio |
| No tengo guardados, compartidos ni retención | El MCP no los da | Exportación de Business Suite y datos de la app |
| `ck new` no transcribe | Falta whisper.cpp | `ck instalar --whisper`. La alternativa `CK_ASR=openai` es de pago: avisa antes |
| Los comentarios del anuncio se vuelven negativos | Prueba social que resta | Responde y modera en la app; si no mejora, clip nuevo |
