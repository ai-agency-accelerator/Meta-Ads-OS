# Anuncios por etapa del CRM, paso a paso

Para quién: consultoras, agencias de IA y automatización y SaaS con pipeline en GoHighLevel y ciclos de semanas.
Qué consigues: anuncios pequeños para quien no vino a la llamada, quien tiene una propuesta abierta, quien dijo «ahora
no» o tus clientes, con listas que salen de tu CRM sin que ningún dato viaje en claro y con un grupo de control que te
dice si esos anuncios suman algo.

```
[GHL] ── exportación ──▶ privado/ ── audiencias_meta.py etapas ──▶ CSV con hashes por etapa + grupo de control
                                                 │
                     operador-meta: crear + sincronizar --reemplazar (con --confirmo)
                                                 ▼
                           [Meta] audiencias ETAPA_… ──▶ campaña de alcance en pausa
                                                 │
       4–8 semanas después: exportación nueva ── audiencias_meta.py medir ──▶ ¿suma? (tratamiento contra control)
```

Lo decide `/anuncios-por-etapa`; las listas para excluir clientes o usar de semilla son `/audiencias`. El marco está en
`meta-ads-kb/02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md` y en el playbook
`meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §9.5.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09.

---

## 0. Antes de empezar

1. **Token de Meta** con `ads_management` en `.env` (`META_TOKEN` o `META_TOKEN_ACME`): `docs/guias/token-avanzado.md`.
2. **Condiciones de las listas de clientes** aceptadas en la cuenta publicitaria. Compruébalo:
   ```
   python3 -I herramientas/audiencias_meta.py listar --cliente acme
   ```
   Si avisa, el titular las acepta una vez en
   `https://business.facebook.com/ads/manage/customaudiences/tos/?act=<número de la cuenta sin act_>`.
3. **Seguimiento comercial montado** (`docs/guias/seguimiento-leads.md`). Un recordatorio o una llamada cuestan menos
   que un anuncio.
4. **Base legal:** tu aviso de privacidad tiene que cubrir el uso de los datos del CRM para publicidad. Con datos de
   salud o finanzas (una clínica como Clínica Sonrisa), no se suben listas sin revisión legal del cliente.

## 1. Exporta de GHL a `privado/`

```
python3 -I herramientas/ghl.py oportunidades --cliente acme --desde 2026-05-01 --hasta 2026-11-08
python3 -I herramientas/ghl.py contactos --cliente acme --desde 2026-05-01 --hasta 2026-11-08
```

El periodo es el de las oportunidades **creadas**; quién entra en `perdido-timing` lo decide la fecha de la pérdida:
de 60 a 180 días (`--dias-perdida 60-180`, por defecto). Un «ahora no» de hace 20 días espera fuera; uno de hace 7
meses, también. Exporta al menos 7 meses para no dejarte perdidos dentro de la ventana. También vale una exportación
de la interfaz de GHL guardada en `clientes/acme/privado/`, con columnas de etapa, estado, contacto y, mejor, motivo de
pérdida y fecha del cambio de estado (o, si no la hay, del último cambio de etapa). `ghl.py oportunidades` trae las
dos (`cambio_estado` y `cambio_etapa`), y `ghl.py contactos` trae el DND (`dnd`).

## 2. Prepara las listas

```
python3 -I herramientas/audiencias_meta.py etapas --cliente acme \
    --archivo clientes/acme/privado/ghl-oportunidades_2026-05-01_2026-11-08.csv \
    --contactos clientes/acme/privado/ghl-contactos_2026-05-01_2026-11-08.csv \
    --prefijo 34 --pais es --bajas
```

Qué hace:
- lleva cada oportunidad a su etapa (estado ganado o perdido primero; si no, el nombre de la etapa) y cada contacto a
  la más avanzada. Si dice «etapas sin reconocer», tradúcelas: `--mapa "Reunión hecha=asistio,Nurture=ignorar"`;
- separa `perdido-timing` (motivo «ahora no», «más adelante», «mal momento»… o etiqueta `mal-momento`, y pérdida de
  hace 60 a 180 días). Los demás siguen en `perdido`, para excluir, y el manifiesto los cuenta (`perdido_timing`);
- quita a quien tiene DND (columna `dnd` de `ghl.py contactos`; si falta, lo avisa) o una etiqueta de baja; con
  `--bajas` los deja en `bajas.csv` para una audiencia solo de exclusión;
- normaliza y hashea emails y teléfonos (y el país) con las reglas de Meta. **Solo escribe hashes**;
- aparta un **grupo de control** del 20 % en `no-show`, `propuesta` y `perdido-timing` (cámbialo con `--control` y
  `--control-en`). Siempre los mismos, refresco tras refresco;
- para esos segmentos escribe además `<segmento>-completa.csv`, con el control dentro, **solo para excluir**.

Deja en `clientes/acme/privado/audiencias/AAAA-MM-DD/` un CSV por segmento, `asignacion.csv` (quién está en
tratamiento y quién en control, con la clave hasheada) y `manifiesto.json` (recuentos, sin datos personales). Por
pantalla verás cuántos hay en cada segmento y el nombre de audiencia sugerido (`ETAPA_PROPUESTA_GHL`).

Con pocas personas (menos de ~100 en tratamiento **[HYPOTHESIS]**; en B2B Meta encuentra bastantes menos de las que
subes), junta etapas: `--agrupar pipeline-abierto=cualificado,llamada,propuesta`.

## 3. Crea y sincroniza (lo hace `operador-meta` con el plan aprobado)

Prueba primero sin tocar Meta:

```
python3 -I herramientas/audiencias_meta.py crear "ETAPA_PROPUESTA_GHL" --cliente acme --simular
python3 -I herramientas/audiencias_meta.py sincronizar 23850000000001 --cliente acme \
    --archivo clientes/acme/privado/audiencias/2026-11-09/propuesta.csv --reemplazar --simular
```

Y con el sí:

```
python3 -I herramientas/audiencias_meta.py crear "ETAPA_PROPUESTA_GHL" --cliente acme --confirmo
python3 -I herramientas/audiencias_meta.py sincronizar <id que te ha dado crear> --cliente acme \
    --archivo clientes/acme/privado/audiencias/2026-11-09/propuesta.csv --reemplazar --confirmo
```

- `crear` deja la audiencia vacía; si ya existe una con ese nombre, te da su ID y no crea otra.
- `sincronizar` solo acepta archivos de `privado/` del mismo cliente y con todas las celdas hasheadas; sube en lotes
  de 10.000 dentro de una sesión. Las listas `-completa` y `bajas.csv` piden además `--exclusion`.
- Cada orden imprime la fila para `clientes/acme/change-log.md`: pégala con el motivo, la métrica y la fecha de
  evaluación.
- Para la audiencia de bajas, mejor una audiencia **solo de exclusión** creada en Ads Manager (Públicos → Crear
  público → Lista de clientes) con `bajas.csv`: no sirve como semilla ni en reglas de valor.

## 4. Comprueba el tamaño a las 24–48 h

```
python3 -I herramientas/audiencias_meta.py listar --cliente acme --buscar ETAPA
```

Si una sale «demasiado pequeña», agrúpala con otra o déjala.

## 5. Monta la campaña (en pausa)

Con la plantilla de `/anuncios-por-etapa` (`plantilla-plan.md`): campaña `ES_AWARENESS_RET_HV` de alcance, un conjunto
por segmento (`ETAPA-PROPUESTA_REACH`…) con la audiencia, sin ampliar (Advantage+ audience desactivada), límite de
frecuencia y exclusiones (`EXCL_GANADO_GHL`, bajas). Presupuesto semanal ≈ frecuencia × personas alcanzables × CPM /
1.000; el total, un 5–15 % del gasto **[HYPOTHESIS]** y dentro de los topes de la ficha.

```
python3 -I herramientas/meta_ads.py crear clientes/acme/planes/2026-11-anuncios-por-etapa.json --cliente acme --simular
```

Después, `/lanzar-campana` lo crea todo en pausa. Activar es otra decisión, con tu sí en ese momento. Las
creatividades: `/brief-creativo` y `/casos-y-creadores`, y `/revisar-anuncio` antes de publicar (que no digan que la
persona está en una lista).

## 6. Refresca cada semana

Mismo día, exportación nueva y la misma orden de `etapas` (la misma semilla y fracción de control, que son las de por
defecto). Luego `sincronizar <id> --reemplazar --confirmo` en cada audiencia. Reemplazar cambia la lista entera **sin
reiniciar el aprendizaje** de los conjuntos; añadir con `users`, sí lo reinicia **[OFFICIAL META]**.

## 7. Mide

A las 4–8 semanas o al cumplirse tu ciclo de venta **[HYPOTHESIS]**:

```
python3 -I herramientas/audiencias_meta.py medir --cliente acme \
    --manifiesto clientes/acme/privado/audiencias/2026-11-09/manifiesto.json \
    --manifiesto clientes/acme/privado/audiencias/2026-11-16/manifiesto.json \
    --archivo clientes/acme/privado/ghl-oportunidades_2026-05-01_2026-12-31.csv
```

Para cada segmento compara tratamiento y control con el éxito que toca (no-show → asistió, propuesta → ganado, perdido
→ reabierto; otro con `--exito`), con el test exacto de Fisher y un veredicto: **suma**, **resta**, **no distinguible**
o **faltan datos** (con cuántos harían falta). Es una comparación por intención de tratar: el tratamiento incluye a
quien Meta no encontró, así que el efecto real en quien vio los anuncios es mayor.

## Alternativa: la sincronización de GHL

En un workflow con «Pipeline Stage Changed», las acciones «Add to Custom Audience (Facebook)» y «Remove from Custom
Audience (Facebook)» meten y sacan a cada contacto en tiempo real. Para tener control, pon antes un reparto aleatorio
que etiquete a una parte como `holdout-etapas` y no la añada, y mide con
`audiencias_meta.py medir --archivo … --contactos … --etiqueta-grupo <etiqueta del flujo> --etiqueta-control holdout-etapas --exito ganado`.
No verificado: qué campos manda GHL a Meta, cómo los hashea y si cada alta reinicia el aprendizaje.

## Problemas frecuentes

| Mensaje | Qué pasa | Qué hacer |
|---|---|---|
| «La cuenta no ha aceptado las condiciones de las listas de clientes» | Falta aceptar los términos (error 1870090 de Meta) | El titular las acepta en el enlace que da la orden |
| «hay celdas sin hashear, no se envía nada» | El CSV no sale de `etapas` ni de `capi.py hashear --archivo` | Prepara el archivo con una de las dos |
| «incluye al grupo de control: solo sirve para EXCLUIR» | Has elegido la lista `-completa` para una audiencia de anuncios | Sube `<segmento>.csv`; la completa, solo con `--exclusion` |
| «Meta aún está procesando un reemplazo» | Hay un reemplazo en curso (estado 414) | Espera y mira `listar` |
| «La sesión caducó» | Más de 90 minutos entre lotes | Repite la misma orden: con `--reemplazar` si la llevaba; si era para añadir, **sin** `--reemplazar` (Meta deduplica; reemplazar dejaría la audiencia solo con ese archivo) |
| «perdidos por timing sin fecha de pérdida» | La exportación no trae la fecha del cambio de estado ni de etapa | Exporta con `ghl.py oportunidades` o indica la columna con `--columna-fecha` |
| «no trae la columna DND» | Falta la exportación de contactos | Añade `--contactos` con `ghl.py contactos` |
| «demasiado pequeña» en `listar` | Pocas coincidencias | `--agrupar` o deja ese segmento |
| «teléfonos sin prefijo de país» | Teléfonos sin `+34` | Repite con `--prefijo 34` |
| «ya hay audiencias preparadas» | Ya generaste las de hoy | `--sobrescribir` o `--fecha` |
| «no hay columna de email ni de teléfono» | La exportación de oportunidades no trae datos de contacto | Añade `--contactos` |

## Lo que no está verificado

Verificado en developers.facebook.com el 2026-11-09: crear la audiencia (`subtype=CUSTOM`, `customer_file_source`,
`retention_days` de 1 a 180), el esquema multiclave, SHA-256, hasta 10.000 por llamada, la sesión de 90 minutos,
`usersreplace` sin reinicio del aprendizaje, los estados (414 reemplazo en curso, 471 marcada) y la comprobación de las
condiciones; sin tamaño mínimo publicado para listas; etiquetas `QUALIFIED_LEADS`, `DISQUALIFIED_LEADS` y
`HIGH_VALUE_CUSTOMERS` en `audience_labels`. Sin verificar: el formato exacto con el que la API acepta
`audience_labels` al crear, el mínimo de unas 100 personas que repiten terceros, la URL oficial del anuncio de las
audiencias solo de exclusión (la cita la prensa) y lo que hace GHL al sincronizar.
