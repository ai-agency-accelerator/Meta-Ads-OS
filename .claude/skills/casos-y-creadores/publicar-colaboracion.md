# Checklist: publicar un anuncio de colaboración (en pausa)

> Para `/casos-y-creadores creadores`, paso C10. A 2026-11-09 ni el MCP de Meta (según su lista oficial de
> herramientas) ni `herramientas/meta_ads.py` crean anuncios de colaboración. Por eso la vía normal es **Ads Manager,
> guiada**: el usuario hace los clics, el sistema comprueba antes y después, y registra. El orden y los nombres de los
> menús cambian a menudo **[STRONG INFERENCE]**: si algo no aparece donde dice, búscalo por el nombre de la opción.

## 1. Antes de abrir Ads Manager (todo tiene que estar en «sí»)

| Comprobación | Dónde | Si falla |
|---|---|---|
| `- **Veredicto de políticas:** OK` u `OK con cambios aplicados` | `LEEME.md` de la pieza | `/revisar-anuncio` |
| Nombre válido: `python3 -I herramientas/nomenclatura.py validar anuncio "<nombre>"` | Terminal | Corrige el nombre |
| Derechos vigentes más allá del final previsto de la campaña | «Prueba social y derechos» del LEEME | Renueva o acorta |
| El contrato permite uso pagado, el canal (Meta) y la identidad del socio | `checklist-derechos.md` firmado | No publiques |
| Socio con cuenta profesional de Instagram y, para Facebook, Página o perfil profesional vinculado | Pregúntale | Solo Instagram: sin vínculo no se entrega en Facebook **[OFFICIAL META]** |
| Permiso en Meta: código de la publicación o permiso de cuenta aprobado (o mismo negocio) | El socio o el hub de anuncios de colaboración | Puedes crearlo igual, pero quedará pendiente de entrega hasta que lo apruebe **[OFFICIAL META]** |
| Sin música con licencia, stickers, GIF ni encuestas | Mira la pieza o la publicación | No es elegible |
| Textos aprobados por el socio (si van con su identidad) | Brief y mensajes | Pide la aprobación |
| Conjunto de destino elegido con `/publicar-anuncios` paso 2 (mismo conjunto que los anuncios de la Página, salvo test A/B) | `lote.md` | Decídelo antes |

## 2. En Ads Manager (lo hace el usuario; tú le guías anuncio a anuncio)

1. Abre el **conjunto de destino** y crea un anuncio nuevo. Pon el **nombre exacto** del LEEME (mismo nombre base que
   la versión con la Página; se distinguen por `ad_id`).
2. **Identidad:** la Página y la cuenta de Instagram del anunciante (las de `meta.pagina` y `meta.instagram` de la
   ficha).
3. Activa **«Anuncio de colaboración»** y añade al socio por su cuenta o pega su **código de anuncio**.
4. **Cabecera:** con las dos identidades o con una sola. Durante un test de identidad, elige una y no dejes que Meta
   optimice entre ellas.
5. **Contenido:**
   - **publicación existente** del socio: el texto es su pie y no se edita desde el anuncio; conserva su prueba social
     (07/07 §2);
   - **contenido nuevo:** sube los archivos de `creativos/<nombre-base>/` (9:16 para Stories y Reels, 4:5 para Feed).
     Necesita permiso de cuenta y no aparece en el perfil del socio **[OFFICIAL META]**.
6. **Textos:** texto principal, titular y CTA de `lote.md`, en la voz del socio si va con su identidad.
7. **Destino y URL** sin UTMs. Los UTMs van en «Parámetros de URL», con la plantilla de
   `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8 (incluye `ad_id={{ad.id}}`, la clave para separar las dos
   identidades en el CRM).
8. **Mejoras automáticas** según `mejoras_automaticas` de la ficha (con `off`, todas apagadas) y **etiqueta de IA** si
   la pieza la lleva.
9. **Formulario instantáneo** (si el objetivo es clientes potenciales): tiene que ser de la Página del conjunto. Según la
   documentación de la API, con anuncios de colaboración usa el formato de tarjeta de bienvenida («greeting card»)
   **[OFFICIAL META]**; comprueba en Ads Manager cómo se llama esa opción.
10. **En pausa:** apaga el interruptor del anuncio antes de pulsar «Publicar», o publícalo en un conjunto en pausa.
    Pide al usuario el **ID del anuncio** (y de la creatividad, si lo ve).

## 3. Después (lo haces tú)

- **Verificación** (`operador-meta`, solo lectura):
  - `ads_get_ad_entities` con el ID: estado en pausa, conjunto correcto, nombre exacto;
  - `ads_get_ad_preview` en Feed y en Reels o Stories: la cabecera muestra la identidad acordada, el texto es el
    aprobado y nada queda tapado por las zonas seguras.
- **Pendiente de entrega:** el socio aún no ha aprobado el permiso. Avísale; no actives nada hasta que esté aprobado.
- **Registro** igual que `/publicar-anuncios` paso 7:
  - una fila en `change-log.md` con `Quién` = `usuario en Ads Manager (verificado por operador-meta)`;
  - una fila por `ad_id` en `registro-creativo.csv`;
  - `Estado: publicado` en el LEEME.

  Añade además la fila del anuncio a la tabla de identidades de «Prueba social y derechos» (ad_id, identidad, alias del
  socio, cabecera, publicación existente o contenido nuevo).
- **Activación:** solo con confirmación específica en el momento («activa estos N anuncios»), como en
  `/publicar-anuncios` paso 8.
- **Moderación:** quien acordasteis revisa los comentarios de las primeras 48 h y después a diario
  (`meta-ads-kb/03-creatividad/12-comentarios-y-prueba-social.md` §3).

## 4. Por API (referencia para cuando el OS lo soporte o si tu equipo usa la Marketing API)

Verificado en la documentación de la Marketing API el 2026-11-09 **[OFFICIAL META]**. No lo ejecutes a mano desde
aquí: cualquier escritura en Meta va por `operador-meta` con plan aprobado y en pausa.

| Qué | Campo o permiso |
|---|---|
| Permisos de la app | `ads_management`, `business_management`, `instagram_basic`, `instagram_branded_content_ads_brand`, `pages_read_engagement`, `pages_show_list` |
| Identidad del socio en la creatividad | `instagram_branded_content.sponsor_id` (Instagram) y `facebook_branded_content.sponsor_page_id` (Facebook) |
| Identidad principal | `object_story_spec.page_id`: tu Página (tú principal) o la del socio (socio principal) |
| Publicación existente | `source_instagram_media_id` + `object_id` (tu Página) |
| Con código del socio | `branded_content.instagram_boost_post_access_token` = el código |
| Cabecera | `branded_content.ad_format`: `1` las dos identidades (por defecto), `2` solo la primera, `3` Meta elige (solo optimiza en Instagram) |
| Testimonio destacado | `branded_content.testimonial`: un testimonio del socio como comentario destacado |
| Anuncio | `/act_<cuenta>/ads` con `status: PAUSED` |
| Permisos de cuenta | `/<ID de tu cuenta profesional de Instagram>/branded_content_ad_permissions` (pedir, listar, retirar) |
| Desglose por creador | `breakdowns=pa_creator_ig_handle`: solo impresiones, alcance, clics en el enlace y cuartiles de vídeo, desde el 2026-09-24 |
| Descubrir contenido | `branded_content_advertisable_medias` desaparece el 2026-12-01; lo sustituye la Content Discovery API |

Ojo: el ejemplo oficial de creatividad nueva con identidad del socio incluye `degrees_of_freedom_spec` con
`standard_enhancements` en `OPT_IN` como campo obligatorio. Eso choca con `mejoras_automaticas: off`. Si se crea por
API, comprueba después qué mejoras quedaron activas (`meta_ads.py creatividades` o `ads_get_creatives`) y no lo actives
sin resolverlo.
