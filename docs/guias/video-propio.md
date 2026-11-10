# Vídeo propio: de tu grabación al anuncio

Con esta guía conviertes lo que grabas tú (el fundador hablando a cámara, alguien del equipo, un creador o una demo de
pantalla de tu SaaS) en anuncios 9:16 y 4:5 listos para Meta. Llevan el hook en los 2 primeros segundos, subtítulos,
la marca del cliente y todo el texto dentro de las zonas seguras. El montaje lo hace **cutkit**
(`modulos/cutkit/`), en tu ordenador, sin coste y sin enviar tu vídeo a ningún sitio.

## 1. Cuándo vídeo propio

| Situación | Vía |
|---|---|
| Hay alguien que puede salir en cámara (fundador, equipo, clientes con permiso) | **Propio**: esta guía |
| Tienes A-roll propio pero te faltan planos de contexto | **Híbrido**: tu A-roll y B-roll del motor (§8) |
| Nadie quiere salir en cámara | En este orden: estáticos y carruseles, demo de pantalla con la voz real, estático animado y, si tampoco hay voz, demo con voz IA genérica rotulada. Un caso de cliente va por delante de todo. **No saltes al avatar** (`meta-ads-kb/03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md` §2.1) |
| Necesitas volumen de hooks sobre una pieza que ya funciona | Variantes de hook, CTA o formato con el motor: `docs/guias/video-ia.md` |
| Quieres probar un ángulo al menor coste | Primero un estático (`docs/guias/estaticos.md`) |

Lo que dice la base de conocimiento:

- Lo que funciona es lo **nativo, claro y específico**. «Feo» funciona cuando hace la pieza más cercana, no por ser
  feo. **[CONTESTED]**, con consenso práctico. Fuente: `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` §4.
- En Reels, más del 75 % de las reproducciones son con sonido **[OFFICIAL META]**. La voz importa, y los subtítulos
  siguen haciendo falta para Feed y para quien ve en silencio. Mismo archivo, §3.3.
- La duración la decide el mensaje: el espectador mediano ve unos 4 s, así que producto, beneficio y oferta tienen
  que estar en los primeros 5–10 s **[STRONG INFERENCE]**. Mismo archivo, §3.1.

## 2. Instalación (una vez)

Lo más fácil es pedírselo a Claude: **`/producir-video <cliente> propio`** instala cutkit la primera vez. Si prefieres
hacerlo a mano, desde la raíz:

```bash
uv run --project modulos/cutkit ck instalar             # entorno, FFmpeg, libass, libx264, whisper.cpp y efectos de sonido
uv run --project modulos/cutkit ck instalar --whisper   # además, el modelo de subtítulos gratis (≈550 MB)
```

Necesitas **FFmpeg con libass y libx264**:

- Mac: `brew install ffmpeg`.
- Linux: `sudo apt install ffmpeg`.
- Windows: `winget install Gyan.FFmpeg`.

Para los subtítulos automáticos y gratis también hace falta whisper.cpp:

- Mac: `brew install whisper-cpp`.
- Linux y Windows: hay que compilarlo.

Sin whisper.cpp puedes pasar tu propio SRT.

`ck instalar` te dice qué falta y cómo arreglarlo en tu sistema.

## 3. Prepara la marca del cliente

cutkit usa el mismo `clientes/<cliente>/marca/marca.json` que los estáticos (`docs/guias/estaticos.md` §3). Para
vídeo hay que tener en cuenta cuatro cosas:

- **Logo en PNG con fondo transparente** (`logo.principal` o `logo.claro`). Un SVG solo no sirve para vídeo.
- **Tipografía en TTF u OTF estática**, el archivo del peso concreto (por ejemplo, `Marca-ExtraBold.ttf`):
  - una fuente variable sale con su peso por defecto, normalmente el más fino;
  - una WOFF o WOFF2, que son fuentes web, no sirve.

  Si no pones ninguna, se usa Montserrat.
- **Contraste**:
  - el hook va en el color `primario` con el texto en `texto_sobre_primario`, y te avisa si no llega a 4,5:1;
  - la CTA va en el color `acento`.
- **Música, solo si tiene licencia para publicidad de pago.** Ponla en `clientes/<cliente>/marca/musica/`, con su
  licencia al lado (`<pista>.licencia.txt`). Sin música, el anuncio sale solo con la voz. Muchos anuncios de
  fundador funcionan así.

Para comprobar cómo la ve cutkit: `uv run --project modulos/cutkit ck marca <cliente>`.

## 4. Graba bien: es lo que más pesa

- **En vertical (9:16), a 1080×1920 o más y a 30 fps.** El 4:5 se saca del 9:16. Recortar un 16:9 a vertical pierde
  calidad y encuadre **[STRONG INFERENCE]**. Si solo puedes grabar en horizontal, pon la cara en el centro y deja
  aire alrededor: cutkit sigue la cara al recortar.
- **El sonido**:
  - micrófono de solapa o el del móvil a un palmo;
  - habitación sin eco;
  - nada de música de fondo mientras grabas (la música, si la hay, se pone después).
- **La luz**: de frente o de lado, nunca una ventana detrás.
- **Los 2 primeros segundos**: empieza directamente con el hook, sin «hola, soy…» ni logos. Graba 3–5 versiones del
  arranque: el hook es lo que más se testea.
- **Varias tomas completas.** Si te equivocas, repite la frase entera. No empalmes media frase de una toma con media
  de otra.
- **Demo de pantalla (SaaS)**:
  - zoom del navegador al 125–150 %;
  - un solo flujo, con el clic y el resultado visibles;
  - **nada de datos personales**: ni emails, ni teléfonos, ni nombres de leads del CRM. Usa una cuenta de demostración.
- **Si sale otra persona** que no eres tú, necesitas su permiso por escrito para usar su imagen y su voz en publicidad.

Deja los brutos en la carpeta de la pieza: `clientes/<cliente>/creativos/<nombre-base>/brutos/`. El `<nombre-base>`
sigue la nomenclatura del contrato §7, sin el hook. Por ejemplo, `20261110_leads-perdidos_whatsapp-ia_founder`. Para
generarlo:

```bash
python3 -I herramientas/nomenclatura.py generar --fecha 2026-11-10 --angulo "Leads perdidos" \
  --concepto "WhatsApp IA" --formato founder --hook 1
```

## 5. Monta con cutkit

```bash
uv run --project modulos/cutkit ck anuncio \
  clientes/acme/creativos/20261110_leads-perdidos_whatsapp-ia_founder/brutos/toma3.mp4 \
  --cliente acme --slug leads-perdidos \
  --salida clientes/acme/creativos/20261110_leads-perdidos_whatsapp-ia_founder/ \
  --nombre 20261110_leads-perdidos_whatsapp-ia_founder_h1 \
  --hook "¿Cuántos leads pierdes por contestar tarde?" --cta "Reserva tu llamada"
```

En medio minuto, más o menos, tienes en la carpeta de la pieza:

| Archivo | Para qué |
|---|---|
| `<nombre>_9x16.mp4` | Reels y Stories (1080×1920) |
| `<nombre>_4x5.mp4` | Feed (1080×1350) |
| `<nombre>.srt` | Subtítulos, por si quieres subirlos también en Ads Manager |
| `qa_anuncio.json` | El resultado de la QA, con la posición de cada texto |
| `LEEME.md` | La ficha de la pieza (plantilla del sistema) con el bloque de QA de cutkit. Si ya existía, solo se actualiza ese bloque |

Lo que hace por ti:

- Quita el silencio inicial y las pausas largas, para que la voz arranque ya.
- Saca los subtítulos: de un SRT que pongas junto al bruto (mismo nombre), o con whisper.cpp en tu ordenador. Se
  muestran en páginas de 1 a 3 palabras, con la que se está diciendo resaltada, en el tercio central.
- Procesa la voz y la deja a −14 LUFS, el nivel habitual en redes **[HYPOTHESIS]**.
- Pone el hook arriba durante los primeros 2,5 s (en 3 líneas como máximo, equilibradas), la CTA y el logo al final, y
  la etiqueta de IA si se la pides.
- Encuadra el 9:16 siguiendo la cara.
- Comprueba con la QA que **ningún texto pisa la interfaz de Meta**:
  - en 9:16, el 14 % de arriba, el 35 % de abajo, el 6 % de los lados y la columna de botones de la derecha
    **[OFFICIAL META]**;
  - en 4:5, un margen del 5 % **[HYPOTHESIS]**.

  Fuente: `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md`.

Opciones útiles (todas en `ck anuncio --help`):

| Opción | Qué hace |
|---|---|
| `--subtitulos archivo.srt` | Usa tus subtítulos |
| `--subtitulos openai` | Transcribe con OpenAI (de pago, ≈0,006 $/min, con tu `OPENAI_API_KEY`) |
| `--subtitulos no` | Sin subtítulos |
| `--broll 4.0-6.5:pantalla.mp4` | Pone un plano a pantalla completa entre esos segundos del montaje final. Se puede repetir |
| `--musica pista.mp3` | Añade música (con licencia para publicidad) por debajo de la voz |
| `--etiqueta-ia` | Rótulo de contenido generado con IA, para los vídeos híbridos |
| `--formatos 9x16` | Solo un formato |
| `--sin-quitar-silencios` | Respeta las pausas, por ejemplo si forman parte del ritmo |
| `--foco centro` | Encuadre fijo, por ejemplo en una demo de pantalla sin cara |
| `--logo siempre` | Logo durante todo el vídeo, no solo al final |

## 6. Lee la QA

El veredicto sale en la terminal, en `LEEME.md` y en `qa_anuncio.json`:

- `pass`: todo bien;
- `warn`: hay avisos y tienes que leerlos y decidir;
- `fail`: no se entrega. La orden sale con código 1.

| Aviso | Qué significa | Qué haces |
|---|---|---|
| `texto.zona_segura` | Un texto pisa la interfaz de Meta | Acorta el hook o la CTA. Si persiste, revisa la tipografía de la marca |
| `hook.tarde` | El hook entra después de los 2 s | No debería pasar con `ck anuncio`. Revisa el perfil si lo has cambiado |
| `hook.texto_largo` / `cta.texto_largo` | No cabe en 3 líneas (hook) o 2 (CTA) ni con el cuerpo mínimo | Déjalo en unas 6–8 palabras para el hook y una acción corta para la CTA |
| `hook.silencio` | La voz empieza tarde y el arranque queda mudo | Recorta el principio del bruto o graba el arranque otra vez |
| `subtitulos.faltan` / `subtitulos.cobertura` | No hay subtítulos o cubren poco de lo que se dice | Instala whisper.cpp o pasa un SRT |
| `subtitulos.rapidos` | Hay páginas de menos de 0,3 s | Revisa el SRT (tiempos solapados) o habla un poco más despacio |
| `audio.sonoridad` / `audio.pico` | El nivel se sale del objetivo | Normalmente es un micro saturado: graba con menos ganancia |
| `imagen.arranque_negro` | El primer fotograma es negro | Empieza el bruto ya con imagen: el primer fotograma tiene que enganchar |
| `ritmo.duracion` | Pasa de 60 s | Pruébalo frente a una versión más corta **[HYPOTHESIS]** |

**Mira siempre el vídeo**. Saca un fotograma del hook y otro de la CTA:

```bash
ffmpeg -ss 0.5 -i <vídeo>_9x16.mp4 -frames:v 1 hook.png
ffmpeg -sseof -1 -i <vídeo>_9x16.mp4 -frames:v 1 cta.png
```

Y compruébalo en un móvil antes de dar la pieza por buena.

## 7. Entrega

1. **Completa el `LEEME.md`**:
   - el guion real (lo que se dice);
   - el copy (texto principal, titular, CTA);
   - **cada afirmación con su fuente** (la ficha del cliente, un caso con permiso o un dato);
   - si lleva IA.

   Respeta el formato exacto de las líneas «Estado» y «Veredicto de políticas», porque las leen las herramientas.
2. **Revisa el nombre**: `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre>"`.
3. **Pasa la pieza por `critico-creativo` y `revisor-politicas`.** `/producir-video` lo hace solo; el veredicto de
   políticas lo escribe el revisor.
4. **Publica** con `/publicar-anuncios`. Con el token avanzado sube los vídeos; sin él, te guía para subirlos en Ads
   Manager.

## 8. Variantes de hook e híbridos

- **Otro hook es otra pasada de `ck anuncio`** sobre el mismo bruto, con otro `--hook` y el nombre siguiente
  (`…_h2`). Tarda medio minuto y no cuesta nada. Si tienes grabados varios arranques, monta uno por toma. Recuerda
  que otro hook es una iteración del mismo concepto, no un concepto nuevo **[STRONG INFERENCE]**
  (`meta-ads-kb/03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md`).
- **Híbrido.** Pide a `productor-ugc` solo los planos que te falten. Son de pago: te enseña la estimación y espera tu
  sí. Luego móntalos con `--broll INICIO-FIN:escena.mp4 --etiqueta-ia`. Nunca van encima del hook ni de la CTA.

## 9. Sin cutkit: la alternativa mínima

Si no puedes instalar cutkit, `herramientas/editar_video.py` hace lo básico con FFmpeg, también con la marca y las
zonas seguras:

```bash
python3 -I herramientas/editar_video.py cortar bruto.mp4 --quitar-silencios --salida corte.mp4
python3 -I herramientas/editar_video.py reformatear corte.mp4 --formato 9x16 --modo desenfoque --salida v_9x16.mp4
python3 -I herramientas/editar_video.py subtitular v_9x16.mp4 --srt v.srt --cliente acme --salida v_subs.mp4
python3 -I herramientas/editar_video.py texto-hook v_subs.mp4 --texto "¿Cuántos leads pierdes?" --cliente acme
python3 -I herramientas/editar_video.py info v_subs_hook.mp4 --json
```

No transcribe, no procesa la voz ni hace la QA de cajas. Para eso está cutkit.

## 10. Montaje avanzado (opcional)

Para piezas con gráficos animados (cifras, pasos, comparativas), B-roll resuelto automáticamente y efectos de sonido
sincronizados, cutkit tiene un modo por decisiones: `ck new` → `ck context` → plan → `ck run`.

Necesita:

- **Node 20+**;
- **el extra `avanzado`**: `uv sync --project modulos/cutkit --extra avanzado` y después
  `uv run --project modulos/cutkit playwright install chromium`.

Es más lento. Los detalles están en `modulos/cutkit/README.md`. Las piezas de anuncio normales no lo necesitan.

## 11. Problemas frecuentes

| Problema | Arreglo |
|---|---|
| `ck instalar` dice que falta libass o libx264 | Tu FFmpeg es mínimo: instala el completo (§2) |
| Los subtítulos salen con otra tipografía | La fuente de la marca es variable o WOFF. Mira los avisos de `ck marca <cliente>` y usa el TTF estático |
| «sin subtítulos: no hay SRT/JSON junto al bruto…» | Instala whisper.cpp y el modelo (`ck instalar --whisper`) o pasa `--subtitulos archivo.srt` |
| La palabra resaltada no va a tiempo | El SRT reparte las palabras por longitud dentro de cada línea. Con whisper.cpp el tiempo es por palabra |
| No aparece el logo | Es un SVG sin PNG al lado: añade `logo.png` con fondo transparente |
| El encuadre corta la cabeza | `--foco centro` o un valor de 0 a 1 (posición horizontal del recorte) |
| Código de salida 2 | Falta una herramienta del sistema: el mensaje dice cuál y cómo instalarla |
