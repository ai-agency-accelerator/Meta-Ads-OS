# Vídeo con IA: el motor de anuncios

Con esta guía produces anuncios de vídeo UGC con una presentadora sintética y tu producto real, sin grabar: del brief
al MP4 listo para Meta, con coste medido y un tope de gasto que tú decides. El motor vive en `modulos/motor-ia/`, es
opcional y gasta dinero real en tu cuenta de Google (Gemini) cada vez que genera imagen o vídeo.

## 1. Qué es y qué no es

- **Es** una cadena completa: guion → fotograma clave con identidad verificada → presentadora hablando en una toma
  continua → planos de corte con tu app o tu producto real → montaje con subtítulos, CTA y etiqueta de IA → control
  de calidad automático que regenera **solo** la escena mala → variantes (hook, CTA, formato, idioma).
- **La presentadora es persistente**: la creas una vez (retrato y hoja de vistas) y sale igual en todos tus anuncios.
- **El producto nunca se inventa**: en un SaaS, la pantalla es tu interfaz real (capturada o grabada); en producto
  físico, tus fotos o vídeos. Lo que la IA inventa se deforma (letras, rejillas, botones).
- **No es** un sustituto de los clientes reales: una persona sintética no puede contar «lo he probado» ni dar un
  testimonio. Presenta, explica y demuestra; no testifica.

## 2. Cuándo IA, cuándo vídeo propio

| Situación | Mejor vía |
|---|---|
| Nadie quiere salir en cámara | Antes que la IA, en este orden: estáticos, demo de pantalla con la voz real y estático animado. Si tampoco hay voz, **IA** para una demo o explicativo con voz IA genérica rotulada (`/producir-video <cliente> ia`). Avatar o presentadora, solo como experimento y rotulado (`meta-ads-kb/03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md` §2.1) |
| Necesitas volumen de hooks, CTA o formatos sobre una pieza que ya funciona | **Variantes con el motor** (§5, paso 5): baratas, sin regenerar el vídeo |
| Hay fundador, equipo o clientes dispuestos a salir en cámara | **Propio** (`/producir-video <cliente> propio`, guía `docs/guias/video-propio.md`) |
| Tienes A-roll propio pero te faltan planos de contexto (llegar a la oficina, el portátil, la calle) | **Híbrido**: A-roll propio + B-roll del motor |
| Quieres testear un ángulo al menor coste | Primero un estático (`docs/guias/estaticos.md`) y, si gana, vídeo |

Lo que dice la base de conocimiento:
- El UGC está cerca del top de *hit rate*, pero por detrás de los estáticos con texto; y el UGC con guion de anuncio
  tradicional pierde la ventaja nativa. **[EMPIRICAL]** — `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md`.
- El contenido con identidad de creador real (partnership ads) rinde mejor que el mismo UGC publicado desde la
  marca: si tienes creadores reales, úsalos. **[OFFICIAL META]** + **[EMPIRICAL]** — mismo archivo.
- Los avatares de IA en formato UGC son de riesgo alto si se presentan como clientes reales; el rótulo visible de IA
  es obligatorio por el art. 50 del Reglamento de IA (no lo pide Meta). —
  `meta-ads-kb/03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md`.

El motor sirve sobre todo para **iterar**: sacar el mismo anuncio con 5 hooks de texto distintos cuesta menos de un
céntimo (§7).
Recuerda que cambiar el hook, el color o la CTA es una iteración del mismo concepto, no un concepto nuevo.
**[STRONG INFERENCE]** — `meta-ads-kb/03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md`.

## 3. Instalación (una vez)

Pídeselo a Claude: **`/motor instalar`**. Hace esto, y puedes repetirlo a mano desde la raíz:

```bash
uv sync --project modulos/motor-ia --extra local     # entorno del motor en tu ordenador (Python ≥3.11 lo pone uv)
uv run --project modulos/motor-ia motor setup        # modelos locales gratuitos (caras, OCR, CLIP) y comprobación de FFmpeg
uv run --project modulos/motor-ia motor status       # proveedores, claves (✔/·), gasto y presupuesto
```

- **FFmpeg es obligatorio**: Mac `brew install ffmpeg` · Windows `winget install Gyan.FFmpeg` (y vuelve a abrir la
  terminal) · Linux `sudo apt install ffmpeg`. Tesseract es opcional (lee la etiqueta de IA y las pantallas).
- Funciona en Mac, Linux y Windows (Git Bash). El entorno se crea en cada ordenador: no copies la carpeta `.venv`.
- Prueba sin gastar: `MOTOR_MOCK=1 uv run --project modulos/motor-ia python -m pytest modulos/motor-ia/tests -q`
  recorre el pipeline entero con medios simulados (tarda unos minutos, 0 $).

## 4. Claves y presupuesto

- **Clave**: crea una en Google AI Studio y pégala tú en el `.env` de la raíz como `GEMINI_API_KEY=…`, con tu editor.
  Nunca la pegues en el chat. Recomendado: un proyecto de Google con facturación solo para el motor, para que otra app
  no te agote el saldo a mitad de un anuncio.
- **Presupuesto del guardián: 5 $ por defecto.** Es un tope global: el motor bloquea cualquier llamada que no quepa
  **antes** de enviarla. Para subirlo, en la cabecera de `contexto/preferencias.md`:

  ```yaml
  ---
  motor:
    presupuesto_usd: 25
  ---
  ```

  o `MOTOR_PRESUPUESTO_USD=25` en el `.env` (manda sobre las preferencias). `motor status` te dice el presupuesto
  efectivo y de dónde sale. Con 5 $ puedes crear la presentadora y probar planos sueltos; un anuncio completo de
  20–30 s necesita más (§7).
- **Cada orden de pago pide confirmación** (hook `motor_guard`) con lo que va a hacer. Antes, Claude te da el coste
  estimado. Pagan: `run`, `regen`, `demo`, `actor create`, `edit … --yes`, variantes con voz o idioma y los scripts
  que generan imagen o vídeo. Todo lo demás es gratis.

## 5. El flujo completo

1. **Brief y guion.** `/brief-creativo` (o el workflow `estudio-creativo` para varios ángulos con jueces y crítico)
   te da guiones en el formato del motor. `revisor-politicas` revisa el texto **antes** de producir.
2. **Plan.** `/producir-video <cliente> ia` guarda el plan en `clientes/<slug>/planes/` y prepara marca, producto y
   presentadora en el motor (marca y producto, gratis; presentadora nueva, ≈0,3 $ con tu sí). Al importar el plan,
   el motor corrige lo que rompería el vídeo (hook demasiado largo, cortes encima del hook) y te da el **coste
   estimado**.
3. **Producción.** Con tu sí, `motor run`. La generación de vídeo es lo más lento: cuenta con un buen rato por
   anuncio. Si algo se para (saldo, cuota, presupuesto), lo hecho se conserva y se reanuda sin volver a pagarlo.
4. **QA.** El motor da un veredicto (`APROBADO`, `RECHAZADO`, `REVISAR ANTES DE PUBLICAR`, `SIN REVISIÓN VISUAL`) y
   `productor-ugc` revisa además los fotogramas del hook, de cada cambio de plano y de la CTA. Lo que esté mal se
   arregla **por escena** («regenera la escena 3»), nunca rehaciendo el anuncio.
5. **Variantes.** `/variantes <cliente> <carpeta o proyecto>`: hooks de texto, CTA, subtítulos, 4:5 y música casi
   gratis; voz o idioma, de pago.
6. **Entrega.** En `clientes/<slug>/creativos/<carpeta-del-anuncio>/`: los MP4 9:16 y 4:5, la miniatura y un
   `LEEME.md` (plantilla `.claude/skills/producir-video/plantilla-leeme.md`) con guion, afirmaciones y su fuente, QA,
   coste real y etiqueta de IA.
7. **Revisión y publicación.** `/revisar-anuncio` sobre la pieza terminada y `/publicar-anuncios` para crearla en
   pausa. El MCP de Meta no sube vídeos: el MP4 se sube en Ads Manager con el rótulo de IA ya dentro de la pieza.

Formato y zonas seguras: el motor exporta 9:16 (1080×1920) y 4:5 (1080×1350) con subtítulos y rótulos dentro de la
zona segura de Reels y Stories (14 % arriba, 35 % abajo, 6 % a los lados libres de texto).
**[OFFICIAL META]** — `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md`.

## 6. Estilos que funcionan

**Presentadora (por defecto).** Habla a cámara en su contexto (despacho, salón, calle), con cortes cortos a la
pantalla real o al producto en los tramos de demostración. Reglas que el motor hace cumplir: hook solo y de ≤9
palabras, ningún tramo de más de 17, como mucho 3 planos de corte de 1,5–3 s y nunca encima del hook ni de la CTA.

**Estilo Flow (producto en uso, varios planos por generación).** La presentadora usa el producto en su contexto real
y la cámara cambia de plano dentro de la misma generación de vídeo, como un anuncio rodado. Se describe en una
**receta** JSON (personaje, producto, lugar, luz, vestuario, voz, segmentos y planos):

```bash
cp modulos/motor-ia/examples/flow_receta_nimbo.json clientes/<slug>/planes/flow_<concepto>.json   # y la editas
S=modulos/motor-ia/scripts
uv run --project modulos/motor-ia python $S/flow_style.py validar --receta clientes/<slug>/planes/flow_<concepto>.json
uv run --project modulos/motor-ia python $S/flow_style.py plan    --receta clientes/<slug>/planes/flow_<concepto>.json
```

`validar` te dice en claro qué falla (hook largo, testimonio en primera persona, referencia de producto que no
existe…) y `plan` enseña los prompts y el coste estimado sin llamar a nadie. Los pasos de pago (`keyframe`, `gen_a`,
`gen_b`, `stills`, `animate`) los lanza `productor-ugc` con tu sí; con `--simular` los pruebas gratis.

**POV para SaaS.** En un SaaS el producto es la interfaz, y la interfaz siempre es real (captura o grabación). Lo que
aporta la IA es el **contexto sin personas**: llegar a la oficina, abrir el portátil, el móvil vibrando en la mesa.
Esos planos POV se describen en `modulos/motor-ia/examples/pov_planos_ejemplo.json` y se generan con
`scripts/pov_broll.py` (de pago salvo `list`); el validador rechaza planos con caras o gente. Combínalos con la
grabación real de tu producto: contexto IA + pantalla real + presentadora.

## 7. Cuánto cuesta (medido en octubre de 2026)

| Pieza | Coste aproximado |
|---|---|
| Presentadora nueva (una vez) | ≈0,3 $ |
| Anuncio de 20–30 s con QA y arreglos | ≈4–6,5 $ |
| Segundo de vídeo generado (Omni 720p) | ≈0,10 $ |
| Imagen (fotograma clave o plano de producto) | ≈0,07 $ |
| Variante de hook de texto, CTA, subtítulos, 4:5 o música | ≈0,0004 $ |
| CTA hablada nueva | ≈0,6–0,8 $ |
| El mismo anuncio en otro idioma | ≈3–4 $ |

Los precios son de Google y cambian: el motor estima con su tabla (`modulos/motor-ia/motor/config/prices.yaml`) y
registra lo que realmente cobra el proveedor. Tu gasto real: `/motor costes <proyecto>`.

## 8. Etiqueta de IA y políticas

Qué formato elegir antes que la IA, la evidencia y la tabla completa de etiquetado:
`meta-ads-kb/03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md`. En resumen:

| Caso | ¿Rótulo de IA en la pieza? |
|---|---|
| Voz real, montaje con IA, gráficos y capturas reales | No |
| Presentadora del motor, avatar realista, clon digital, voz clonada o lip-sync que hace decir algo nuevo | Sí, obligatorio (art. 50 del Reglamento de IA), visible desde el primer segundo |
| Voz IA genérica o planos realistas de lugares generados (B-roll del motor) | Zona gris: rotúlalo |

- **El rótulo va en la pieza, no en Meta.** El anuncio lleva «Creado con IA» visible por defecto. Meta no exige
  declarar la IA en anuncios comerciales y su «AI info» (dentro de «About this ad» desde el 2026-06-01) solo salta con
  sus herramientas o si detecta señales estándar, casi nunca con vídeo reencodado. **[OFFICIAL META]** +
  **[EMPIRICAL]**. Quien obliga es el art. 50 del Reglamento de IA, desde el 2026-08-02: consúltalo con tu asesoría
  antes de quitar el rótulo visible. — `meta-ads-kb/03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md` §5.
- **Tú respondes de lo que genera la IA**, también de la de Meta, y no puedes quitar marcas de agua ni metadatos de
  autenticidad (los vídeos de Google llevan SynthID). **[OFFICIAL META]** —
  `meta-ads-kb/03-creatividad/14-herramientas-ia-creativa-meta.md`.
- **Sin testimonios falsos**: nada de «lo he probado», «llevo meses usándolo» ni resultados personales en boca de la
  presentadora. Ni cifras ni afirmaciones que no estén en las afirmaciones aprobadas de la marca.
- **Sin personas reales** (ni famosos, ni «expertos» inventados que parezcan reales, ni la cara o la voz de alguien
  sin su permiso por escrito). — `meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md`.
- **Música**: la genera el motor o la aportas con licencia comercial. Nunca música de catálogo con derechos: Reels Ads
  no la admite. — `meta-ads-kb/07-instagram-placements-mensajeria/03-specs-safe-zones-formatos.md`.

## 9. Problemas frecuentes

| Ves | Qué pasa | Qué haces |
|---|---|---|
| `402 … prepayment credits are depleted` · proyecto en `paused_billing` | Se acabó el saldo prepago de tu cuenta de Google | Recarga en Google AI Studio y `/motor reanudar <proyecto>`: sigue donde se quedó, sin volver a pagar lo hecho |
| `429` en vídeo | Cuota diaria de peticiones de vídeo de tu nivel de Gemini (ventana móvil de 24 h) | Espera unas horas y reanuda; si te pasa a menudo, sube de nivel en Google |
| Proyecto en `paused_budget` o «presupuesto agotado» | Llegaste al tope del guardián (§4) | Decide si lo subes; mira antes `/motor` para ver cuánto llevas gastado |
| Veredicto `SIN REVISIÓN VISUAL` | El juez multimodal no pudo correr (saldo, caída o simulado) | Revisa los fotogramas a mano o repite el QA cuando haya saldo |
| `falta ffmpeg` | FFmpeg no está instalado o no está en el PATH | Instálalo (§3) y vuelve a abrir la terminal |
| La cara cambia entre escenas o sale un segundo móvil | Deriva de identidad u objeto inventado | El QA lo detecta y regenera esa escena; si persiste, «regenera la escena N» |
| El producto o la interfaz salen deformados | Se generó con IA en vez de usar material real | Añade capturas, grabaciones o fotos reales al producto y regenera esa escena |

Más detalle técnico: `modulos/motor-ia/docs/RUNBOOK.md`. Estado de lo probado: `modulos/motor-ia/docs/ESTADO.md`.
