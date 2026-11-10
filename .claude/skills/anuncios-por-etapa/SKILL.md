---
name: anuncios-por-etapa
description: "Decide y monta anuncios para etapas del CRM (no se presentó, propuesta enviada, perdido por timing, clientes para referidos o ampliaciones): mensaje y prueba por etapa, exclusiones, presupuesto pequeño y grupo de control para medir si suma. Audiencias con audiencias_meta.py vía operador-meta; todo en pausa y en el change log."
argument-hint: "<cliente> [disenar|montar|refrescar|medir] [etapa]"
disable-model-invocation: true
---

# /anuncios-por-etapa

Entrada: `$ARGUMENTS` (cliente, modo y, opcionalmente, una etapa). Por defecto `disenar`. En un ciclo de semanas,
quien no vino a la llamada, quien tiene una propuesta encima de la mesa o quien dijo «ahora no» vale más que un lead
nuevo, y unos anuncios pequeños con la prueba adecuada pueden acompañar el seguimiento comercial. **Pueden**: sin grupo
de control no se afirma que suman. Las listas como tal (excluir clientes, semillas, etiquetas para value rules) son
`/audiencias`.

- **Marco:** `meta-ads-kb/02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md` (§2 cuándo separar el
  retargeting, §3 cómo hacerlo con audiencias pequeñas, §4.2 excluir o no),
  `meta-ads-kb/02-estructura-campanas/07-audiencias-2026.md` (§5 listas de clientes, etiquetas y audiencias solo de
  exclusión, §6 cuándo segmentar), `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §9.5 (tabla de
  etapas, mensaje y presupuesto), `meta-ads-kb/14-playbooks/playbook-agencias-consultores.md` §2 (retargeting de casos
  y objeciones), `meta-ads-kb/05-leadgen-high-ticket-crm/06-high-ticket-funnels.md` §8,
  `meta-ads-kb/09-bidding-escalado-economia-analitica/07-frecuencia.md` (frecuencia sin folklore),
  `meta-ads-kb/04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md` §5 (holdout de audiencia),
  `meta-ads-kb/13-sistema-operativo/09-presupuesto-pequeno-y-grande.md` §A y
  `meta-ads-kb/04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md` §2 y §4.
- **Agentes:** `especialista-crm` (exportación y etapas de GHL), `operador-meta` (único que crea y sincroniza),
  `estratega-creativo` y `redactor-anuncios` (mensaje por etapa), `revisor-politicas`, `analista-cuantitativo`
  (tamaño del control y lectura de `medir`).
- **Herramientas:** `audiencias_meta.py` (`etapas`, `listar`, `crear`, `sincronizar`, `medir`), `ghl.py
  oportunidades` y `contactos`, `meta_ads.py crear --simular`, `nomenclatura.py`. Plantilla: `plantilla-plan.md`.
- **Escribe:** `clientes/<slug>/planes/anuncios-por-etapa-<AAAA-MM-DD>.md`, los CSV en
  `clientes/<slug>/privado/audiencias/<AAAA-MM-DD>/` (los genera la herramienta) y el change log.

## Reglas

- **Todo se crea en pausa** y activar exige la confirmación expresa del usuario en ese momento. `crear` y
  `sincronizar` llevan `--confirmo` y solo los ejecuta `operador-meta` con el plan aprobado. Borrar audiencias está
  bloqueado: si sobra una, se anota y la borra el usuario en Ads Manager.
- **Datos:** solo exportaciones en `privado/`; a Meta solo van hashes; en el chat y en el plan, solo recuentos. Sin base
  legal para usar la lista del CRM en publicidad (aviso de privacidad) o con datos de salud o finanzas (Clínica Sonrisa,
  por ejemplo), no se hace (`04-…/09-…` §4). Quien pidió la baja o tiene DND no entra: `etapas` lo quita por la
  columna `dnd` (la exporta `ghl.py contactos`; pásala con `--contactos`) o por una etiqueta de baja, y avisa si la
  columna falta. Con `--bajas` deja la lista para una audiencia **solo de exclusión** (no sirve como semilla ni en
  value rules, `07-…` §5).
- **Grupo de control siempre** que se quiera decir si suma. La misma semilla y la misma fracción durante toda la
  prueba.
- Los anuncios no dicen ni insinúan que la persona está en una lista ni en qué etapa está («como no viniste a la
  llamada…»): `revisor-politicas` lo revisa antes de publicar.

## Pasos

1. **Requisitos** (si falla alguno, para y di qué falta):
   - `topes` de la ficha distintos de 0 y condiciones de listas de clientes aceptadas (lo dice `listar`);
   - pipeline con las etapas del §16 y motivo de pérdida de una lista cerrada: `audiencias_meta.py etapas
     --sin-archivos` no tiene que dejar etapas «sin reconocer» (tradúcelas con `--mapa`);
   - seguimiento comercial montado (W3–W5 de `/seguimiento-leads`): un recordatorio o una llamada valen más y cuestan
     menos que un anuncio;
   - volumen: cuántas personas hay hoy en cada etapa y cuántas entran por semana.
2. **¿Separar o no?** (`09-…` §2). Advantage+ ya enseña anuncios a quien conoce la marca (10–40 % del gasto, según la
   KB, **[EMPIRICAL]**): visitas web y vídeo se quedan dentro de la campaña principal. Se separan las etapas del CRM
   cuando el mensaje cambia de verdad por etapa y la lista tiene tamaño.
3. **Inventario:** `python3 -I herramientas/audiencias_meta.py listar --cliente <slug> --buscar ETAPA` (lo que ya
   existe, tamaño y estado) y `etapas --sin-archivos` con la exportación del periodo que marca la ventana (p. ej.
   oportunidades de los últimos 180 días para perdidos por timing).
4. **Tabla de segmentos** (rellena la de `plantilla-plan.md`; punto de partida, **[HYPOTHESIS]** salvo cita):

   | Segmento | Cuándo sí | Mensaje y prueba | CTA | Excluir |
   |---|---|---|---|---|
   | `no-show` | Más de ~20 al mes y W4 ya activo | Vídeo «qué pasa en la llamada», caso corto | Reservar otro hueco | Ganado, asistió |
   | `propuesta` | Ciclo de más de 2 semanas | Caso del mismo tipo de proyecto, objeción de precio, «tus datos se quedan en tus cuentas» | Hablar de la propuesta o del piloto | Ganado, perdido |
   | `perdido-timing` | Motivo en la exportación y 60–180 días desde la pérdida (`etapas` lo aplica: `--dias-perdida 60-180`) | Taller mensual, re-diagnóstico, novedad del sector | Re-diagnóstico | Ganado |
   | `ganado` (referidos y ampliaciones) | Hay oferta de mantenimiento, formación u otro proceso | Otro proceso automatizado, programa de referidos | Hablar de la ampliación | — |
   | `cualificado` o `llamada` | Citas a más de 48 h y sincronización diaria | «Qué preparar», quién te atenderá | Confirmar | Asistió |

   Perdidos por otros motivos (no cualifica, eligió a otro) no reciben anuncios: van a exclusión. Cada segmento lleva su
   métrica del CRM (la de `medir`: no-show → asistió, propuesta → ganado, perdido → reabierto).

   **Talleres** (pipeline «Taller» de `/webinar`): sus primeras etapas no son del §16 y se declaran como segmentos
   propios. «Asistió al taller» no se toma nunca por la llamada: sin `--mapa` sale como «sin reconocer».
   `etapas --pipeline taller --mapa "Registrado=propio:registrado-sin-asistir,Asistió al taller=propio:asistio-sin-llamada,Se quedó a la oferta=propio:hasta-oferta-sin-reserva" --control-en registrado-sin-asistir,asistio-sin-llamada,hasta-oferta-sin-reserva`
   (después de la fecha del taller, quien sigue en Registrado no vino). Mensajes: la repetición para quien no vino, un
   caso y la invitación a la llamada para quien asistió, la oferta resumida para quien se quedó hasta el final. Para
   medirlos, `medir --exito llamada`.
5. **Tamaño.** Meta no publica un mínimo para listas de clientes ni una tasa de coincidencia esperada
   **[OFFICIAL META]** (verificado el 2026-11-09); sí marca una audiencia como demasiado pequeña para entregar
   (`listar` lo enseña). Con menos de ~100 personas en tratamiento **[HYPOTHESIS]** (en B2B coinciden muchas menos que
   las subidas), une etapas con `--agrupar pipeline-abierto=cualificado,llamada,propuesta` o no lo hagas: con 15
   propuestas al mes rinde más la llamada del W5.
6. **Grupo de control.** `etapas --control 0.2` (por defecto en `no-show`, `propuesta` y `perdido-timing`; añade
   `--control-en ganado` si haces anuncios a clientes) aparta a uno de cada cinco al azar, siempre los mismos
   (`09-…` §3: holdout del 10–20 % **[STRONG INFERENCE]**; `13-incrementalidad-…` §5: válido si es aleatorio y se mide
   en el CRM). Para excluir se usa siempre la lista `-completa` (con el control dentro): si excluyeras solo el
   tratamiento, el control vería tus otros anuncios y la comparación se rompe. Con grupos pequeños, `medir` dirá
   cuántos harían falta; si no vas a llegar nunca, dilo en el plan: la decisión será de criterio, no de datos.
7. **Mensajes y creatividades.** Un concepto por segmento, con la prueba que resuelve la duda de esa etapa:
   `/brief-creativo` (ángulos por etapa), `/casos-y-creadores` (casos con permiso y cifras aprobadas) y
   `/revisar-anuncio` antes de publicar.
8. **Estructura y presupuesto** (`09-…` §3 y `07-…` §6):
   - campaña `ES_AWARENESS_RET_HV` con objetivo Reconocimiento (alcance) y límite de frecuencia **[EMPIRICAL]**;
     un conjunto por segmento (`ETAPA-PROPUESTA_REACH`, `ETAPA-NO-SHOW_REACH`, `ETAPA-PERDIDO-TIMING_REACH`) en ABO;
     audiencia restringida a la lista, sin ampliar (Advantage+ audience desactivada) **[OFFICIAL META]**; valida los
     nombres con `nomenclatura.py`;
   - presupuesto semanal ≈ frecuencia buscada × personas alcanzables × CPM / 1.000 (`07-frecuencia.md`); no hay una
     frecuencia ideal y en ciclos largos se tolera más que en captación; empieza con 1–3 impresiones por persona y
     semana **[HYPOTHESIS]** y juzga por `medir`, no por la frecuencia;
   - total orientativo del 5–15 % del gasto de la cuenta **[HYPOTHESIS]** (playbook de consultoras §9.5), y la suma
     del plan dentro de `topes.cambio_dia`;
   - exclusiones: `EXCL_GANADO_<CRM>` y la de bajas en todos; en las campañas de captación, las listas `-completa` de
     los segmentos con control si quieres que no reciban captación (y entonces tampoco el control).
9. **Montar** (modo `montar`, con el plan aprobado por escrito), por `operador-meta`:
   1. `python3 -I herramientas/audiencias_meta.py etapas --cliente <slug> --archivo <oportunidades> --contactos <contactos> --prefijo 34 --pais es [--bajas]`;
   2. una audiencia por segmento y por exclusión: `audiencias_meta.py crear "ETAPA_PROPUESTA_GHL" --cliente <slug> --confirmo`
      (si ya existe, da su ID y no crea otra);
   3. `audiencias_meta.py sincronizar <id> --cliente <slug> --archivo clientes/<slug>/privado/audiencias/<fecha>/propuesta.csv --reemplazar --confirmo`
      (las `-completa` y `bajas.csv`, con `--exclusion`);
   4. a las 24–48 h, `listar`: si sale «demasiado pequeña», agrupa o para;
   5. plan de campaña de `plantilla-plan.md` → `meta_ads.py crear <plan> --cliente <slug> --simular` y, tras el sí,
      `/lanzar-campana` (todo en pausa); activar, solo con la confirmación del momento;
   6. cada `crear` y `sincronizar` imprime su fila: pégala en `clientes/<slug>/change-log.md` con motivo, métrica y
      fecha de evaluación.

   Vía GHL nativa (alternativa): acciones «Add to Custom Audience (Facebook)» y «Remove from Custom Audience
   (Facebook)» en un workflow con «Pipeline Stage Changed», con un reparto aleatorio que etiqueta el control
   (`holdout-etapas`) y no lo añade. Va en tiempo real, pero no sabemos qué campos manda GHL ni cómo los hashea, y el
   control depende del reparto de GHL; se mide con `medir --etiqueta-grupo <etiqueta del flujo> --etiqueta-control holdout-etapas`.
10. **Refrescar** (modo `refrescar`, cada semana el mismo día): exportación nueva → `etapas` con la misma semilla y
    fracción → `sincronizar <id> --reemplazar --confirmo` en cada audiencia. Reemplazar no reinicia el aprendizaje de
    los conjuntos; añadir con `users`, sí **[OFFICIAL META]**. Una fila corta en el change log por refresco.
11. **Medir** (modo `medir`, a las 4–8 semanas o al cumplirse el ciclo de venta **[HYPOTHESIS]**):
    `audiencias_meta.py medir --cliente <slug> --manifiesto <primera subida> --manifiesto <refrescos…> --archivo <exportación nueva>`.
    - **suma** → se mantiene; con coste incremental por éxito (gasto / éxitos de más) por debajo de lo que vale esa
      etapa en la ficha, se puede ampliar a una etapa parecida;
    - **no distinguible** con el tamaño que pide `medir` → se para: ese dinero rinde más en captación o en el W5;
    - **faltan datos** → sigue hasta el tamaño necesario o para si no se va a alcanzar;
    - **resta** → se para y se revisa el mensaje.
    La comparación es por intención de tratar (incluye a quien Meta no encontró): el efecto en quien vio los anuncios es
    mayor. Lo que contradiga la KB va a `meta-ads-kb/16-aprendizajes-propios/` para `curador-conocimiento`.
12. **Cierre.** Guarda el plan en `clientes/<slug>/planes/anuncios-por-etapa-<AAAA-MM-DD>.md` y anota en «Notas y
    aprendizajes clave» de la ficha las audiencias activas (nombre, ID, uso y día de refresco).
