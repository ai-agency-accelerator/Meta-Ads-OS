# cutkit: reglas para el agente

Editor de vídeo propio de Meta Ads OS. Uso, opciones y variables: `README.md`. Licencias: `LICENCIAS.md`. Guía para
el usuario: `docs/guias/video-propio.md`.

## Cómo se usa

- Siempre desde la raíz del producto: `uv run --project modulos/cutkit ck <orden>`. Nunca con el Python de la raíz.
- El camino por defecto es `ck anuncio <bruto> --slug <slug> --cliente <cliente> --hook "…"`. El modo avanzado
  (`ck new` → `ck run`) solo si el usuario pide gráficos animados y tiene Node y el extra `avanzado`.
- Antes de montar por primera vez en un ordenador: `ck instalar`. Si dice que falta algo, explica el arreglo que
  propone, no lo rodees.
- Para crear o revisar la marca, usa `ck marca <cliente>`. El esquema está en `cutkit/marca.py`.

## Dinero y licencias

- Hay cuatro cosas de pago, y **ninguna se activa sin un «sí» explícito del usuario en esa conversación**:
  - `--subtitulos openai` o `CK_ASR=openai`;
  - `CK_MUSICA_IA=1`;
  - `--judge`;
  - `--budget` mayor que 0.

  Por defecto, todo es local y gratis.
- `CK_ALINEAR=mms` usa un modelo no comercial: no lo actives para anuncios.
- Música, solo con licencia para publicidad de pago (en `clientes/<cliente>/marca/musica/` con su licencia al lado).
  Si no hay, el anuncio va sin música.
- Si la pieza lleva imagen o voz generada con IA, monta con `--etiqueta-ia` y recuerda declararlo al publicar.
- No edites a mano `cutkit/motion/three/vendor/*.min.js` ni sus `LICENSE.*.txt`: se regeneran con `build.sh`.
- Si añades un archivo binario, una fuente o un asset de terceros, apúntalo en `LICENCIAS.md`. Lo comprueba un test.

## Entrega y QA

- Cada pieza vive en `clientes/<cliente>/creativos/<nombre-base>/` (contrato §6), así que monta con
  `--salida clientes/<cliente>/creativos/<nombre-base>/ --nombre <nombre-base>_h<n>`. Sin `--salida`, cutkit usa
  `<AAAA-MM-DD>_<slug>/`, que sirve para pruebas. Si no hay `LEEME.md`, cutkit lo crea con la plantilla del producto;
  si ya existe, solo actualiza su bloque de QA. Completa a mano:
  - el copy;
  - las afirmaciones y su fuente;
  - si lleva IA;
  - el nombre del anuncio según la nomenclatura.
- No des por bueno un vídeo con veredicto `fail`. Con `warn`, lee cada aviso y decide con el usuario.
- Antes de decir que está listo, mira un fotograma del hook y otro de la CTA:
  `ffmpeg -ss 0.5 -i <vídeo> -frames:v 1 hook.png`.
- Antes de publicar, el copy, la creatividad y la landing pasan por `revisor-politicas`. cutkit no publica: eso lo
  hace `/publicar-anuncios` (con el token avanzado) o el usuario en Ads Manager.
- No borres brutos ni versiones anteriores. Si sobra algo, pregúntale al usuario.
