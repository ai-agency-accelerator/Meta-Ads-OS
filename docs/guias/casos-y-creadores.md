# Casos y creadores: prueba social real en tus anuncios

Con esta guía conviertes los proyectos que ya entregaste en anuncios con cifras del cliente y su permiso, y trabajas
con clientes, expertos y creadores como **socios**: gente que sale contigo en el anuncio. Está pensada para
consultoras y agencias de IA y automatización y para SaaS que venden a pymes. En una venta de varios miles de euros, un
proyecto contado por quien lo vivió pesa más que cualquier pieza generada **[STRONG INFERENCE]**
(`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §8.2). El mismo playbook (§2.2) pone como
condición para invertir en Meta tener **3 casos** que puedas contar con cifras, permiso y contexto.

Todo pasa por una skill con tres modos:

```text
/casos-y-creadores <cliente> caso [proyecto]          # de proyecto entregado a anuncio
/casos-y-creadores <cliente> creadores [perfil|lote]  # socios y anuncios de colaboración
/casos-y-creadores <cliente> medir [lote]             # colaboración frente a Página
```

`<cliente>` es el anunciante: la marca que publica, con su carpeta en `clientes/<cliente>/`.

Lo que el OS **no hace**:

- **No envía nada ni contacta con nadie.** Peticiones, mensajes a creadores, permisos y contratos salen como borradores
  y los envías tú.
- **No crea anuncios de colaboración por API.** Hoy no lo permiten ni el MCP de Meta ni `meta_ads.py` (§6). Los creas
  en Ads Manager con una checklist, y el OS comprueba y registra.
- **No es asesoría legal.** Las plantillas de permiso y derechos son orientativas: revísalas con un profesional antes
  de firmarlas o enviarlas.
- **No inventa prueba.** Ningún testimonio, cifra ni caso que no exista. Tampoco una persona sintética dando un
  testimonio.

## 1. Qué camino te toca

| Situación | Empieza por |
|---|---|
| Has entregado proyectos con resultados y el cliente te conoce bien | `caso` (§2) |
| El cliente acepta salir, pero no tiene cuenta profesional en Instagram | `caso`, con testimonio publicado desde tu Página |
| El cliente acepta salir y tiene cuenta profesional | `caso` y después `creadores`, con el cliente como socio (§4) |
| Todavía no tienes casos | `creadores` con un experto que explica el problema, o el fundador y una demo con datos ficticios. No con un creador que cuente resultados que no ha vivido |
| Quieres volumen de piezas grabadas por otros | `creadores` con un creador UGC. Las piezas salen desde tu Página (`ugc`) |
| Ya tienes anuncios con un socio y quieres saber si compensa | `medir` (§7) |
| Quieres reutilizar contenido orgánico tuyo que funcionó | No es esta skill: `/organico-a-anuncios` |

## 2. La fábrica de casos, con un ejemplo

**Acme Automations** (consultora ficticia) montó para **Clínica Sonrisa** (cliente ficticio, cuatro sillones) un
sistema de recordatorios de cita por WhatsApp con confirmación automática. Lleva dos meses en producción.

### 2.1 Elegir el proyecto

La skill puntúa cada proyecto de los últimos 12 meses de 0 a 2 en seis criterios:

- resultado con un «antes»;
- cliente dispuesto;
- encaje con el ICP;
- se puede enseñar;
- madurez;
- representatividad.

Clínica Sonrisa saca 11 de 12: hay registro de llamadas de antes, la gerente está contenta, las clínicas son el ICP de
Acme y el flujo se puede enseñar con una agenda de demostración. El caso se llama `clinica-dental-recordatorios`, por
el sector y la palanca y nunca por el nombre del cliente, porque el nombre del anuncio viaja en `utm_content`.

### 2.2 Permiso antes de grabar

Primero se mira el contrato de servicios con la clínica, por si tiene una cláusula de confidencialidad. Después se
acuerda el **nivel de permiso**, que decide qué piezas pueden salir:

1. anónimo;
2. con nombre y logo;
3. con cara y voz;
4. además, como socio en anuncios de colaboración.

La clínica acepta el nivel 3. Firman dos documentos:

- **la gerente**, con facultades para obligar a la empresa, firma la autorización;
- **la gerente y la recepcionista**, que salen en la entrevista, firman cada una su consentimiento de imagen y voz.

Lo firmado se guarda en `clientes/acme-automations/privado/casos/clinica-dental-recordatorios/`, y el caso solo apunta
la ruta, el nivel y la caducidad. Plantilla: `.claude/skills/casos-y-creadores/permiso-cliente.md`.

Mejor sin contraprestación. Un descuento a cambio del testimonio lo convierte en testimonio retribuido, y eso hay que
decirlo (§8).

### 2.3 Cifras que se pueden comprobar

| Indicador | Antes (4 semanas de septiembre) | Después (4 semanas de oct.–nov., sin las 2 de implantación) | Método | Tipo |
|---|---|---|---|---|
| Horas de recepción confirmando citas | ≈11 h/semana: 220 llamadas × 3 min | ≈2 h/semana revisando las que no confirman | Volumen del registro de llamadas y del flujo × 15 llamadas cronometradas | Estimada |
| Ausencias | 14 % de las citas | 8 % | Agenda de la clínica | Medida |

Las dos cifras son de la clínica y las aprueba por escrito con el texto exacto (anexo A del permiso). El ahorro en
euros va en la landing, con el método al lado. En el anuncio van horas, errores o tiempos
(`meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md` §2) **[STRONG INFERENCE]**.

### 2.4 La entrevista

Son 35 minutos con el guion de `.claude/skills/casos-y-creadores/entrevista-caso.md`, que tiene 22 preguntas en 7
bloques: antes, desencadenante, dudas, proceso, después, recomendación y cierre. La regla de oro es no hacerle leer
nada: cuando suelta una buena frase («los lunes eran solo teléfono»), se le pide que la repita entera en una toma limpia.

La grabación se transcribe **en tu ordenador**, con cutkit, y la carpeta de trabajo se deja dentro de `privado/`:

```bash
CUTKIT_RUNS=clientes/acme-automations/privado/casos/clinica-dental-recordatorios/cutkit \
  uv run --project modulos/cutkit ck new entrevista --raw entrevista.mp4 --sin-cierre \
  --prompt "Clínica Sonrisa, recordatorios, WhatsApp, confirmación, ausencias"
```

El bruto se queda en `privado/`. En `investigacion/casos/clinica-dental-recordatorios/entrevista.md` va solo la
transcripción anonimizada, con las mejores frases marcadas con su minuto.

### 2.5 Afirmaciones aprobadas

La skill propone frases para la sección «Afirmaciones aprobadas» de la ficha, y solo las escribe cuando le confirmas
que el cliente las aprobó. Así se ve la diferencia:

| Texto | ¿Sirve? | Por qué |
|---|---|---|
| «En una clínica dental de 4 sillones, recepción pasó de unas 11 h semanales confirmando citas a unas 2» | Sí | Cuenta lo que pasó en un caso concreto, con contexto, y la cifra está redondeada |
| «Ahorra 9 horas a la semana con nuestros recordatorios» | No | Promete al espectador un resultado típico que no está demostrado |
| «Reduce las ausencias a la mitad» | No | 14 → 8 no es la mitad, y vuelve a ser una promesa |
| «¿Tu clínica pierde pacientes por las ausencias?» | Revísalo | Atributo personal en segunda persona (`meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md` §3) |

Cada afirmación lleva su fuente, si es medida o estimada, quién la aprobó y cuándo caduca. Ningún anuncio usa una
cifra que no esté en esa tabla.

## 3. Las piezas que salen de un caso

Con el nivel 3, el caso de Clínica Sonrisa da para cuatro piezas, cada una con su carpeta y su `LEEME.md`:

| Pieza | Nombre |
|---|---|
| Testimonio de la gerente, de 45 s, con cortes de 15 s | `20261116_horas-recuperadas_caso-clinica-dental-recordatorios_testimonio_h1` |
| Demo del flujo con la agenda de demostración | `20261116_horas-recuperadas_caso-clinica-dental-recordatorios_demo_h1` |
| Estático con el dato y una frase | `20261116_horas-recuperadas_caso-clinica-dental-recordatorios_estatico_h1` |
| Carrusel: problema → qué hicimos → resultado → cómo → CTA | `20261116_horas-recuperadas_caso-clinica-dental-recordatorios_carrusel_h1` |

- **El hook es la frase más concreta del cliente**, no su presentación. Grabar 3–5 arranques distintos da hooks `h2`,
  `h3`…
- **En la demo no puede aparecer ningún dato real.** Nada de nombres de pacientes, teléfonos ni importes. Si solo
  existe la cuenta real, `editor-video` desenfoca y se revisa fotograma a fotograma.
- **Producción:** con las herramientas de siempre, `/producir-video <cliente> <brief> propio` y `/producir-estatico`.
  Guías: `docs/guias/video-propio.md` y `docs/guias/estaticos.md`.
- **Prueba social y derechos:** la skill añade esta sección al `LEEME.md` de cada pieza. Recoge la identidad (Página o
  colaboración), el tipo de prueba, el permiso, la caducidad de los derechos y el estado del permiso en Meta.
- **Políticas, dos veces:** `revisor-politicas` revisa las afirmaciones antes de producir y la pieza terminada al
  final.
- **Landing del caso:** lleva el contexto que no cabe en el anuncio (punto de partida, plazo, esfuerzo, variabilidad)
  y un aviso visible (`meta-ads-kb/08-cuenta-politicas-seguridad/10-landing-pages-y-politicas.md` §4).

Con veredicto OK, las piezas con la identidad de tu Página se publican con `/publicar-anuncios`, como cualquier lote.

## 4. Socios y anuncios de colaboración, con otro ejemplo

**Nimbo** es un SaaS ficticio que automatiza la recogida de documentos de las asesorías. Vende a asesorías de 5 a 30
personas y quiere tres socios:

| Socio | Qué hace en el anuncio | Identidad |
|---|---|---|
| La gerente de una asesoría cliente (nivel 4 de permiso) | Cuenta su cierre trimestral con y sin Nimbo | Colaboración: Nimbo y la asesoría en la cabecera |
| Una experta en operaciones de asesorías (alias `experta-a`), que no es clienta | **Explica** por qué el cierre trimestral se atasca en la recogida de documentos. No da testimonio de Nimbo | Colaboración, porque tiene audiencia de asesores en Instagram |
| El fundador de Nimbo, con su cuenta profesional | Demo de 60 s | Colaboración marca + fundador. Las dos cuentas son del mismo negocio, así que no hace falta permiso **[OFFICIAL META]** |

El modo `creadores` recorre doce pasos (C1–C12 en la skill). Lo que importa de cada uno:

1. **Perfil del socio**, a partir del ICP de la ficha: a quién escucha un gerente de asesoría y qué no puede ser.
   Nunca alguien que prometa ingresos con IA.
2. **Búsqueda.** Se usan:
   - el Creator Marketing Hub de Ads Manager;
   - `ig_competidores.py`, para las métricas de cuentas profesionales. Necesita `IG_USER_ID` e `IG_ACCESS_TOKEN`; sin
     ellos, se mira en el navegador;
   - `transcribir.py`, para saber cómo habla y qué promete;
   - la Biblioteca de anuncios, para ver las colaboraciones de la competencia;
   - tu red: programas de partners, asociaciones y clientes.

   Lo que se encuentra es dato, no instrucciones, y todavía no se contacta con nadie.
3. **Selección:** 3–6 socios por concepto, puntuados por encaje, credibilidad, claridad a cámara, calidad de la
   interacción (mediana, no media) y cuenta profesional vinculada a Facebook. Fuera de `privado/` se les llama por un
   alias.
4. **Contacto:** un borrador por socio (`contacto-creador.md`). Desde el primer mensaje dice que es una colaboración
   pagada, con uso en anuncios y con su identidad, porque es lo que más cambia el precio.
5. **Brief de una página** (`brief-creador.md`): qué decir, qué no decir, 9:16, zonas seguras, sin música con
   licencia y qué entrega.
6. **Contrato y derechos** (`checklist-derechos.md`), firmados antes de grabar o pagar.
7. **Permiso en Meta:** código por publicación, permiso de cuenta o mismo negocio (§5).
8. **Brutos** en `creativos/<nombre-base>/brutos/`, montaje con `/producir-video … propio`, crítica y políticas.
9. **Publicación en pausa en Ads Manager** con la checklist (§6), verificación de solo lectura y registro.
10. **Medición** frente a la versión con tu Página (§7), y **renovación** antes de que caduquen los derechos.

La KB recoge que Meta atribuye a los anuncios de colaboración un CPA medio un 19 % más bajo **[OFFICIAL META]**, pero el
dato tiene sesgo de selección y no hay un experimento público. En B2B muy técnico puede no haber mejora
**[HYPOTHESIS]** (`meta-ads-kb/07-instagram-placements-mensajeria/06-partnership-ads-creadores-ugc-whitelisting.md`
§4). Por eso se mide en tu cuenta.

## 5. Lo que está verificado

Comprobado en la documentación oficial el **2026-11-09**. Lo que no se pudo leer está marcado.

| Hecho | Etiqueta | Fuente |
|---|---|---|
| Hay tres vías de permiso: código de anuncio por publicación, permiso de cuenta, o las dos cuentas del mismo negocio con acceso a ambas (en ese caso no hace falta permiso) | [OFFICIAL META] | Marketing API: Partner Permissions, Account-Level Permissioning y Partnership Ads Creation |
| Con permiso de cuenta puedes crear contenido nuevo con la identidad del socio sin que lo publique, e incluir o excluir su audiencia | [OFFICIAL META] | Account-Level Permissioning |
| Si publicas sin permiso, el anuncio queda pendiente de entrega y el socio recibe una solicitud | [OFFICIAL META] | Partnership Ads Creation |
| Sin una Página o un perfil profesional de Facebook vinculado a la cuenta de Instagram del socio, el anuncio no se entrega en Facebook | [OFFICIAL META] | Instagram Partnership Ads with a New Ad Creative y su equivalente de Facebook |
| La cabecera puede llevar las dos identidades, solo la primera, o elegirla Meta (esto último solo optimiza en Instagram) | [OFFICIAL META] | Instagram Partnership Ads (publicación existente), campo `ad_format` |
| Existe un formato de testimonio que muestra un comentario del socio como comentario destacado | [OFFICIAL META] | Supported Configurations › Testimonial Ads |
| Los formularios instantáneos de un anuncio de colaboración usan el formato «greeting card». El nombre exacto de esa opción en Ads Manager **no está verificado** | [OFFICIAL META] / sin verificar | Supported Configurations › Lead Ads |
| El desglose por creador (`pa_creator_ig_handle`) solo da impresiones, alcance, clics en el enlace y cuartiles de vídeo, sin gasto ni conversiones. Hay datos desde el 2026-09-24 y no se combina con otros desgloses | [OFFICIAL META] | Insights › Breakdowns |
| `branded_content_advertisable_medias` se retira el 2026-12-01. Lo sustituye la Content Discovery API | [OFFICIAL META] | Content Discovery API |
| El ejemplo oficial de creatividad nueva con la identidad del socio exige `standard_enhancements` en `OPT_IN`, lo que choca con `mejoras_automaticas: off` | [OFFICIAL META] | Instagram Partnership Ads with a New Ad Creative |
| Son elegibles reels, historias, publicaciones estáticas y secuencias. El contenido con música con licencia no es elegible. Si la marca sube el contenido, no aparece en el perfil del creador. El creador puede cobrar más por el uso ampliado | [OFFICIAL META] | Instagram for Creators, «Anuncios de colaboración» |
| Los anuncios con contenido de marca deben etiquetar al socio con la herramienta de contenido de marca | [OFFICIAL META] | `meta-ads-kb/08-cuenta-politicas-seguridad/06-advertising-standards-mapa-2026.md` |
| La lista oficial de herramientas del MCP de Meta no tiene ninguna de anuncios de colaboración. La documentación del Ads CLI tampoco los menciona | [OFFICIAL META] | Ads MCP Server › Available tools y Ad creation and management; Ads CLI |
| La prensa cuenta que Meta anunció en septiembre de 2026 los anuncios de colaboración en el MCP | [CONTESTED] | No aparece en la documentación oficial |
| La página de requisitos del Servicio de ayuda de Instagram sobre anuncios entre socios y contenido de marca | **Sin verificar** | Se renderiza con JavaScript y no se pudo leer. La skill se apoya en la KB y en la documentación de developers |
| Nombres y orden de los menús de Ads Manager | [STRONG INFERENCE] | Cambian a menudo. Si algo no está donde dice la checklist, búscalo por el nombre de la opción |

## 6. Publicar un anuncio de colaboración (hoy)

Como no hay vía por API, el anuncio se crea **a mano en Ads Manager**, con la checklist de
`.claude/skills/casos-y-creadores/publicar-colaboracion.md`:

1. **Comprobaciones previas.** Todo tiene que estar en «sí»:
   - veredicto de políticas OK en el LEEME;
   - nombre válido;
   - derechos vigentes y contrato que permita uso pagado con la identidad del socio;
   - permiso en Meta aprobado;
   - sin música con licencia, stickers ni encuestas.
2. **En Ads Manager lo haces tú, y Claude te guía anuncio a anuncio:**
   - conjunto de destino;
   - nombre exacto;
   - tu Página y tu Instagram como identidad;
   - «Anuncio de colaboración» con el socio o su código;
   - cabecera fija;
   - contenido;
   - textos;
   - UTMs en «Parámetros de URL», incluido `ad_id={{ad.id}}`;
   - mejoras automáticas según la ficha;
   - **interruptor apagado** antes de publicar.
3. **Después:**
   - le pasas el ID a Claude;
   - `operador-meta` comprueba en solo lectura el estado, el conjunto, el nombre y la vista previa en Feed y Reels;
   - se registra como en `/publicar-anuncios` (change log, `registro-creativo.csv` y LEEME), con una fila más en la
     tabla de identidades del LEEME. De esa tabla saca `registro_creativo.py actualizar` la columna `identidad`
     (`pagina` o `colaboracion`) de cada `ad_id`: así se separan las dos versiones, que comparten nombre y UTMs.
4. **Activar** es otra decisión: solo cuando lo confirmes en ese momento.

Cuando el MCP tenga la herramienta (compruébalo con `/mcp`), la creación irá por `/publicar-anuncios` y
`operador-meta`, con plan aprobado y en pausa, como cualquier otra escritura.

## 7. Medir: ¿compensa poner al socio en la cabecera?

Hay dos preguntas distintas, y mezclarlas invalida la lectura:

- **Identidad:** ¿el mismo vídeo rinde mejor con el socio en la cabecera? Se responde con el mismo archivo y el mismo
  texto en dos anuncios, uno desde tu Página y otro de colaboración, con la cabecera fija y con contenido nuevo (no con
  una publicación existente, cuya prueba social acumulada mezcla el efecto).
- **Fuente:** ¿lo que graba un socio gana a lo que grabas tú? Es un test de concepto normal (`/test-creativo`).

Por defecto, los dos anuncios van al mismo conjunto que el resto. Meta no reparte el gasto a partes iguales, así que la
lectura es **orientativa**. Para un A/B test de verdad hace falta volumen:

```bash
python3 -I herramientas/estadistica.py potencia --diferencia 0.2
# ≈ 473 conversiones por brazo para detectar un 20 % de diferencia de CPA
```

Ejemplo con Nimbo después de un mes, con 900 € por brazo:

```bash
python3 -I herramientas/estadistica.py comparar --gasto-a 900 --conv-a 18 --gasto-b 900 --conv-b 24
# A: CPA 50.00 (18 conv) · B: CPA 37.50 (24 conv)
# p-valor 0.441 · Veredicto: NO distinguible del ruido con estos datos
```

Con decenas de leads al mes, esto no se puede demostrar. Lo que sí se puede hacer:

- **Mirar la calidad**, no solo el coste: el porcentaje de leads cualificados y de llamadas en GHL por anuncio. Los dos
  anuncios comparten nombre y `utm_content`, así que la unión con el CRM va por `ad_id` (por eso la plantilla de UTMs
  lo incluye).
- **Sumar el coste de los derechos** al coste del brazo de colaboración.
- **Decidir con la capa más baja de verdad que tenga datos suficientes**, y apuntar la decisión como
  `[HYPOTHESIS]` en `aprendizajes-creativos.md`.
- **No fiarte del desglose por creador para el coste:** no da gasto ni conversiones. Si quieres coste por socio, haz un
  anuncio por socio.

La lectura se hace a los 7 días como mínimo, con la regla de paciencia del OS
(`meta-ads-kb/09-bidding-escalado-economia-analitica/12-razonamiento-estadistico.md` §3–4).

## 8. Derechos, en corto (no es asesoría legal)

Antes de grabar o de pagar, `.claude/skills/casos-y-creadores/checklist-derechos.md` repasa diez bloques. Lo que más se
olvida:

- **Uso pagado, canales, territorio y duración, por escrito.** Según la lectura no profesional del OS de la ley
  española de propiedad intelectual (art. 43), si una cesión no fija plazo ni territorio se limita a 5 años y al país
  **[STRONG INFERENCE]**. Pon fechas.
- **Imagen y voz:** cada persona que sale firma su propio consentimiento. Según la misma lectura de la LO 1/1982 (art. 2), ese
  consentimiento se puede revocar en cualquier momento, aunque quien lo revoca puede tener que indemnizar los daños
  **[STRONG INFERENCE]**. Ten un plan B para cada pieza.
- **Ediciones e IA:** sin cláusula expresa, nada de doblaje, voz clonada ni avatar a partir de la grabación.
- **Divulgación:** si hay pago o descuento, el testimonio es retribuido. Etiqueta de colaboración pagada y aviso en la
  landing. El Código de Conducta de Autocontrol sobre influencers y la normativa de usuarios de especial relevancia
  pueden aplicar **[STRONG INFERENCE]** (`meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md`
  §5).
- **Datos personales:** contratos, contactos y brutos solo en `privado/`. Fuera, alias y agregados.

Revisa todo con un profesional antes de firmar.

## 9. Problemas frecuentes

| Problema | Qué pasa y qué hacer |
|---|---|
| El anuncio está «pendiente de entrega» | El socio no ha aprobado el permiso. Avísale. No actives nada hasta que esté aprobado |
| No se entrega en Facebook | La cuenta de Instagram del socio no tiene una Página ni un perfil profesional de Facebook vinculado. Que lo vincule, o quédate en Instagram |
| No puedo cambiar el texto del anuncio | Usas una publicación existente: el texto es su pie. Pide al socio que lo edite o usa contenido nuevo con permiso de cuenta |
| La publicación no es elegible | Lleva música con licencia, stickers, GIF o encuestas. Pide una versión limpia |
| El socio no encuentra cómo generar el código | Los menús cambian. Que lo busque en la configuración de la publicación (también sirve una publicación archivada o una colaboración oculta **[OFFICIAL META]**, página `ad-codes`) o pídele un permiso de cuenta |
| El cliente retira el permiso | Pausa sus piezas en el plazo acordado, anótalo en el change log y lanza el mismo concepto con tu Página o con otro socio. Borrar está bloqueado en el OS |
| Las mejoras automáticas aparecen activas | Pasa si se creó con la configuración por defecto o por API (§5). Revísalo con `ads_get_creatives` y apágalas antes de activar |
| El hook `control_publicacion` no avisó | Solo vigila lo que se publica desde el OS. Lo que se crea a mano en Ads Manager depende de la checklist del §6 |
| `ig_competidores.py` falla con una cuenta | Solo lee cuentas profesionales (Business Discovery). Si es personal, revísala en el navegador |

## 10. Dónde queda cada cosa

```text
clientes/<cliente>/
├── ficha.md                                   # «Afirmaciones aprobadas» (solo con el sí del cliente)
├── investigacion/
│   ├── casos/<caso>/caso.md                   # ficha del caso: cifras, método, nivel, caducidad
│   ├── casos/<caso>/entrevista.md             # transcripción anonimizada
│   ├── casos/<caso>/evidencias/               # agregados y capturas sin datos personales
│   └── creadores/perfil.md                    # perfil y criterios, con alias
├── privado/                                   # nunca sale de aquí
│   ├── casos/<caso>/                          # permisos firmados, brutos, cutkit, exportaciones
│   └── creadores/                             # contratos, contactos, socios.md (alias → cuenta)
└── creativos/
    ├── _lotes/<AAAA-MM-DD>_caso-<caso>/       # lote.md y briefs/ (también <nombre-base>.socio.md)
    └── <nombre-base>/LEEME.md                 # con «Prueba social y derechos»
```

## Fuentes verificadas (2026-11-09)

Documentación de Meta para developers, en `developers.facebook.com/documentation/ads-commerce/`:

- `marketing-api/ad-creative/partnership-ads` y sus subpáginas:
  - `post-level-permissioning`;
  - `account-level-permissioning` y `fb-account-level-permissioning`;
  - `ad-codes`;
  - `ads-creation` (`boost-existing-post`, `boost-existing-fb-post`, `use-new-creative`, `new-fb-creative`);
  - `ads-creation/supported-configurations` (`lead-ads`, `testimonial-ads`, `advantage-creative`);
  - `content-discovery-api`.
- `marketing-api/guides/branded-content` y `marketing-api/guides/branded-content-permissions`.
- `marketing-api/insights/breakdowns`.
- `ads-ai-connectors/ads-mcp-server/ads-mcp-server-tools` y `ads-mcp-server-tools-ad-creation-and-management`.
- `ads-ai-connectors/ads-cli/ads-cli-overview`.

Instagram for Creators: `creators.instagram.com/earn-money/partnership-ads`, en español.

Base de conocimiento:

- `meta-ads-kb/07-instagram-placements-mensajeria/06-partnership-ads-creadores-ugc-whitelisting.md`;
- `meta-ads-kb/07-instagram-placements-mensajeria/07-organico-mas-pagado-post-ids-boost.md`;
- `meta-ads-kb/08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md`, `10-landing-pages-y-politicas.md` y
  `11-copy-persuasivo-compliant-patrones.md`;
- `meta-ads-kb/03-creatividad/04-formatos-y-estilos.md` y `12-comentarios-y-prueba-social.md`;
- `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md`.
