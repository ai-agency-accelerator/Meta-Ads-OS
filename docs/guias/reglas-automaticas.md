# Reglas automáticas: tu cuenta protegida aunque nadie esté mirando

Para quién: cualquiera que lleve cuentas de Meta con Meta Ads OS, sobre todo con pocos leads y ciclos de venta largos
(consultoras y agencias de IA y automatización, SaaS B2B).

Qué consigues: unas pocas reglas que viven en los servidores de Meta y actúan solas, 24/7, también un viernes por la
noche:
- pausan lo que gasta sin convertir;
- pausan lo que gasta fuera de tus topes;
- te avisan cuando algo se rompe.

Lo que **no** hacen: subir presupuestos, encender anuncios, cambiar pujas ni «optimizar» nada. Eso se decide con datos
madurados y con tu «sí», en `/escalar` o `/ejecutar-cambio`.

Se monta con `/reglas-automaticas <cliente>`. Esta guía es la versión larga: qué reglas, por qué esas, y qué hacer si
algo falla.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial a 2026-11-09: compruébalo en tu
pantalla. Los nombres de los menús de Ads Manager cambian a menudo y dependen del idioma.

---

## El recorrido

| Paso | Qué haces | Cuándo |
|---|---|---|
| 1 | Auditas las reglas que ya tiene la cuenta | Hoy |
| 2 | Propones el conjunto por defecto desde la ficha y lo revisas | Hoy |
| 3 | Lo creas en **modo sombra**: las pausas por conversión solo avisan | Hoy |
| 4 | Revisas qué habrían hecho las reglas | A las 2 semanas |
| 5 | Pasas a activo las que acertaron y apagas las de sombra | A las 2 semanas |
| 6 | Revisión trimestral o tras un cambio de Meta o del CPA objetivo | Cada trimestre |

---

## 1. Por qué hacen falta

El OS ya tiene dos protecciones, pero ninguna cubre la noche:
- **`/brief-diario`** mira las cuentas una vez al día. Si algo se dispara a las 21:00, lo verás a la mañana siguiente.
- **Los hooks** (`meta_guard`) frenan lo que hace Claude: un presupuesto por encima del tope, una activación sin
  confirmar. No ven lo que pasa en Meta cuando Claude no está trabajando, ni lo que hace otra persona con acceso a la
  cuenta.

Las reglas automáticas se evalúan en Meta cada media hora o a la hora que elijas, aunque tengas el ordenador apagado.
Por eso son la tercera capa. Y por eso mismo son peligrosas si hacen algo más que avisar o pausar: una regla que sube
presupuesto se salta los topes de tu ficha y todos los hooks.

## 2. El conjunto por defecto

Ejemplo con Acme Automations: CPL objetivo de 80 € en la ficha, evento `Lead`, `topes.cambio_dia` de 100 € y 40 leads
por semana en su campaña (`--conversiones-semana 40`, una cuenta «grande» para la KB).

| Regla | Qué hace | Cuándo se evalúa |
|---|---|---|
| `PROTECT_OS_anuncio-sin-conversion` | Pausa el anuncio que ha gastado más de 240 € (3 × 80 €) sin ningún lead, sin contar el gasto de hoy, si tiene más de 72 h y más de 2.000 impresiones | Cada día a las 06:00 |
| `PROTECT_OS_conjunto-sin-conversion` | Lo mismo para el conjunto | Cada día a las 06:00 |
| `PROTECT_OS_gasto-hoy-fuera-de-tope` | Pausa el conjunto que hoy lleva más de 220 € (2,2 × 100 €) | Cada media hora |
| `ALERT_OS_gasto-hoy-alto` | Avisa si un conjunto lleva hoy más de 175 € (1,75 × 100 €) | A las 10, 14, 18 y 22 h |
| `ALERT_OS_sin-conversiones-3d` | Avisa si un conjunto lleva 3 días cerrados sin leads y con más de 240 € gastados | A las 07:00 |
| `ALERT_OS_cpa-disparado-14d` | Avisa si un conjunto tiene un CPL de más de 160 € (2×) con al menos 3 leads en 14 días cerrados | A las 07:00 |
| `ALERT_OS_sin-entrega-ayer` | Avisa si un conjunto activo ayer tuvo menos de 100 impresiones | A las 08:00 |

Con menos de 30 conversiones por semana y campaña, o si no dices cuántas hay, la propuesta es la de cuenta pequeña
(KB 07, «Implicaciones operativas»): 4 × 80 € = 320 € en la pausa del anuncio y, en el conjunto entero, solo un aviso
(`ALERT_OS_conjunto-sin-conversion`), porque pausar el conjunto apaga también a los anuncios que aún están aprendiendo.

Las horas son las de la zona horaria de la cuenta. Las reglas de conversión solo miran los conjuntos cuyo objetivo de
optimización encaja con el evento: conversiones en la web y, para `Lead`, también formularios instantáneos. La regla
no distingue qué evento de la web optimiza cada conjunto: si tienes campañas con otro evento (por ejemplo, una de
`Purchase` junto a las de `Lead`), limítalas con `--campanas`.

### Pausa sin conversión: por qué 3× o 4× y nunca 1×

Si un anuncio tiene un CPA real igual a tu objetivo, la probabilidad de que no haya convertido aún depende de cuánto
lleva gastado (KB `meta-ads-kb/10-cambios-2025-2026-api-ia-automatizacion/07-reglas-automaticas.md` §2):

| Gasto sin conversión | Anuncios buenos que matarías |
|---|---|
| 1× el CPA objetivo | 37 % |
| 2× | 13,5 % |
| 3× | 5 % |
| 4× | 1,8 % |

- **El mínimo es 2×.** La herramienta no acepta menos. Entre 2× y 3×, avisa del porcentaje de anuncios buenos que
  caerían.
- **4× es el valor por defecto**, salvo que digas que la campaña tiene 30 conversiones por semana o más
  (`--conversiones-semana 40`): entonces es **3×**. Con menos de 30, que es lo normal en B2B de ticket alto, la KB
  aconseja 4× para las pausas automáticas (07, «Implicaciones operativas»). Si no lo sabes, la herramienta supone la
  cuenta pequeña y te lo dice. Cada pausa te avisa y la puedes deshacer, pero un anuncio bueno pausado es un anuncio que
  no aprende.
- **3× con volumen** es la excepción a la regla de paciencia que permite actuar sin esperar 7 días: «≥3× CPA objetivo
  sin conversión en un evento frecuente» (`meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md` §8).
  `[STRONG INFERENCE]`
- **El anuncio necesita más de 2.000 impresiones** antes de que la regla lo pause (07 §4.B.1): con menos, el gasto
  todavía no dice nada de él.
- **Si la propuesta sale absurda, avisa.** Un CPA mal escrito en la ficha («1 200 €» leído como 1) daría una regla que
  pausa a 4 €. Los números se leen ya con miles y decimales en español, y si `k × CPA` queda por debajo del 5 % del
  tope por cambio, `proponer` avisa y cita la celda de la ficha de la que lo ha sacado.
- **72 horas de edad mínima** antes de juzgar nada (07 §4.B.1). `[EMPIRICAL]`
- **A las 06:00**, para que Meta haya atribuido lo de ayer y la regla actúe antes del grueso del gasto del día.
  `[HYPOTHESIS]`

### Gasto fuera de tope: seguridad de dinero, no estadística

Meta puede gastar hasta el 175 % del presupuesto diario de un conjunto en un día, y el 210 % con *ad set budget
sharing* (`meta-ads-kb/02-estructura-campanas/06-presupuesto-por-niveles.md` §1). `[OFFICIAL META]`

- **Si todos tus presupuestos respetan `topes.cambio_dia`**, ningún conjunto puede gastar más de 2,1 veces el tope en
  un día.
- **Si lo hace, el problema es otro**: un presupuesto con un cero de más, un acceso que no debía tocar la cuenta o un
  presupuesto total con un ritmo raro.
- **Por eso esta regla pausa desde el primer día, también en modo sombra.** Mira el gasto de hoy (aquí sí tiene
  sentido, porque es dinero y no rendimiento) cada media hora. El margen del 2,2 en lugar de 2,1 es `[HYPOTHESIS]`:
  cubre los redondeos de facturación.
- **Antes de crearla**, la herramienta comprueba que no tengas ya un presupuesto activo por encima del tope. Si lo
  tienes, no crea nada: o bajas ese presupuesto o subes el tope de la ficha, y esa decisión es tuya.
- **El tope total de la cuenta** no se protege con una regla, sino con el límite de gasto de la cuenta, que se
  configura en `/configurar-meta` (07 §4.B.4).

El aviso a 1,75 × el tope es el máximo legal sin *budget sharing*: si salta, mira el presupuesto antes de que actúe la
pausa.

### Sin conversiones recientes: lo que se rompe en una cuenta que funcionaba

- **Qué detecta:** un píxel o una CAPI caídos, un formulario o un webhook rotos, una landing caída.
- **Por qué hace falta aparte:** la pausa por conversión no lo ve si el conjunto convirtió alguna vez.
- **Qué hace:** solo avisa. Mira el dataset antes de tocar nada (07 §4.A.3). `[EMPIRICAL]`
- **Su ventana se adapta.** Es la más corta (3, 7 o 14 días) en la que un conjunto con el presupuesto del tope podría
  gastar 3 veces el CPA. Con menos gasto, 0 conversiones no es señal, así que la regla solo vigila conjuntos que gastan
  más de cierta cifra al día; la propuesta te dice cuál. Si ni con el tope se llega, la regla no se crea: en conjuntos
  pequeños, el tracking roto lo detecta antes `/brief-diario`, que mira la señal del dataset.

### CPA disparado: solo una alerta

- **Cuándo salta:** el doble del CPA objetivo con al menos 3 resultados en 14 días cerrados ya es señal, no ruido.
- **Por qué no pausa:** con 3 resultados, el CPA real puede estar entre 0,35× y 5× el observado (07 §2). Por eso la
  decisión la tomas tú, en `/diagnostico`. `[STRONG INFERENCE]`
- **Cómo se calcula:** `gasto − 2 × CPA × resultados > 0`, que no divide por cero.
- **Su ventana también se adapta** (14, 28 o 30 días). Hacen falta 3 resultados a más de 2 veces el CPA, o sea, haber
  gastado 6 veces el CPA en la ventana. Si un conjunto con el presupuesto del tope no llega ni en 30 días, el CPA no se
  puede juzgar por conjunto y la regla no se crea.

### Sin entrega

- **Qué detecta:** un pago rechazado, anuncios rechazados o una audiencia agotada dejan de traer leads sin hacer ruido.
  Un viernes, eso es un fin de semana perdido (07 §4.A.1). `[EMPIRICAL]`
- **Por qué mira ayer:** se usa el día cerrado en lugar de «hoy a mediodía» para que no salte con presupuestos pequeños
  y CPM altos. `[HYPOTHESIS]`
- **Falsas alarmas posibles:** un conjunto activo con fecha de inicio futura o con todos sus anuncios en pausa también
  dispara el aviso.

## 3. La madurez: no se mata lo que aún no ha tenido tiempo de convertir

El lead de un formulario llega en minutos. Una cita con Nimbo (SaaS B2B) llega días después del clic, y una propuesta
enviada, semanas. Ads Manager imputa la conversión al día del clic o de la impresión, así que los últimos días siempre
se ven peor de lo que son (`meta-ads-kb/09-bidding-escalado-economia-analitica/11-cuando-no-tocar-una-campana.md`).

Por eso cada propuesta tiene una **madurez**: los días que tarda en llegar el evento. Las reglas restan el gasto de esos
últimos días antes de comparar con el umbral:

```
gasto madurado = gasto de por vida − gasto de los últimos días sin madurar
```

| Evento | Madurez por defecto | Fila de la ficha con su coste |
|---|---|---|
| `Lead`, `Contact`, `SubmitApplication`, `CompleteRegistration`, `DiagnosticoCompletado`, `StartTrial` | 0 días | CPL, o coste por prueba |
| `LeadCualificado`, `Schedule` (cita) | 3 días | Coste por lead cualificado, o por cita |
| `LlamadaAsistida` | 7 días | — (pásalo con `--cpa`) |
| `PropuestaEnviada` | 14 días | — (pásalo con `--cpa`) |
| `Purchase`, `Subscribe` | 0 en ecommerce, 14 en SaaS, 28 en servicios | Coste por venta |

- **Los valores por defecto son `[HYPOTHESIS]`.** Si tienes CRM, mide los tuyos con `embudo.py cohortes`: los días
  hasta que llega la gran mayoría de los eventos. Después pásalo con `--madurez`.
- **Con 30 días o más, la herramienta se niega.** Ninguna regla sabrá a tiempo si un anuncio funciona. Protege un
  evento anterior (lead cualificado o cita) con su coste, y decide las ventas por cohortes en el informe semanal.
- **Con madurez, las alertas usan ventanas más largas o no caben.** Las ventanas de Meta llegan hasta 30 días, y de
  ellas solo cuentan los días ya madurados. Ejemplo: una cita de Nimbo de 300 € con 3 días de madurez y un tope de
  100 €/día. La alerta de «sin conversiones» pasa a 14 días y la de «CPA disparado», a 28. Con 28 días de madurez, las
  dos se omiten, y la propuesta lo dice.
- **En Ads Manager, las pausas por conversión con madurez solo avisan.** La interfaz no puede restar el gasto reciente.
  Con token, la versión de la API sí lo hace y puede pausar.

## 4. Modo sombra y paso a activo

Toda regla nueva arranca solo avisando durante 1–2 semanas (07 §6.2):
1. **`proponer`** sale en sombra por defecto. Las pausas por conversión se crean como notificación, con el nombre
   terminado en `-sombra`. La pausa por gasto fuera de tope, no: esa pausa desde el primer día.
2. **A las 2 semanas**, `/reglas-automaticas <cliente> activo` revisa cada aviso con
   `reglas_meta.py historial --dias 14 --todas`: ¿ese anuncio de verdad no convertía, mirado con la ventana ya
   madurada?
3. **Si habría pausado algo que convirtió después**, sube el multiplicador o la madurez y repite la sombra.
4. **Si acertó**, o si no habría pausado nada (también vale: es una protección contra lo raro), crea la versión activa
   con `proponer --activo` y desactiva las de sombra. `crear` te da el `pausar <ids>` exacto. En una cuenta pequeña, la
   del conjunto entero sigue siendo un aviso también en activo.
5. **Marca `F5.reglas`** en `clientes/<slug>/estado.md` cuando las reglas activas estén creadas y anotadas en el change
   log (`Nivel` = `regla`): así `/hoy` deja de proponerlas.

## 5. Lo que el OS no automatiza nunca

| Regla típica | Por qué no |
|---|---|
| Frecuencia > 3 → pausar o avisar | Folklore: Meta mide la fatiga por coste por resultado frente a tu histórico (`meta-ads-kb/12-mitos-contradicciones/01-mitos-meta-ads-2026.md` M37) |
| Subir presupuesto un 20 % (o cualquier cifra) si el CPA es bueno | El 20 % es un mito (M05), y la regla actuaría sin tus topes ni los hooks. Se escala por coste marginal con `/escalar` |
| Pausar si el CPA de hoy o de ayer supera el objetivo | Ruido y latencia de atribución: mata ganadores (07 §2 y §5) |
| Encender lo que ayer fue bien, o apagar y encender por horas | Bucles de ruido y regresión a la media; reinicia la entrega (07 §5) |
| Reequilibrar presupuesto entre conjuntos | Con poco volumen, concentra el dinero en el ruido (07 §5) |
| CPM sobre la mediana, caída del CTR | Necesitan la banda normal de la cuenta: los mira el brief con `estadistica.py banda` |
| Reglas por disparador (*trigger*) | Solo existen por API y no se ven en Ads Manager: nadie sabría que están ahí |

`crear` rechaza cualquier propuesta que traiga una de estas reglas, aunque edites el JSON a mano. `reactivar` tampoco
enciende una regla que haga algo distinto de avisar o pausar.

## 6. Auditar las reglas que ya tiene la cuenta

Con token, `python3 -I herramientas/reglas_meta.py listar --cliente <slug>` enseña cada regla en claro (qué hace, con
qué periodo, cuándo y a quién avisa) y la marca así:

- **PROHIBIDA**:
  - sube presupuesto, enciende, cambia pujas, rota o rebalancea;
  - pausa por frecuencia (una regla que solo **avisa** por frecuencia queda como AVISO: la KB 07 §4.A.5 la admite
    como señal para revisar, no como prueba de fatiga);
  - pausa por el rendimiento de hoy o de ayer;
  - mata por debajo de 2× el CPA;
  - pausa si el gasto de hoy pasa de menos de 1,75× el presupuesto (eso es legal desde 2025);
  - es una regla por disparador.
- **AVISO**:
  - mata entre 2× y 3×;
  - pausa por CPA en una ventana larga (mejor como alerta);
  - no tiene edad mínima;
  - no tiene destinatarios;
  - Meta la marca «con problemas»;
  - tiene umbrales calibrados antes del 2026-03-03, cuando la atribución por clic pasó a contar solo clics en el
    enlace: recalíbralos con datos posteriores a abril de 2026.

Las reglas de otras personas no se tocan sin su permiso. Si una PROHIBIDA está activa, se propone desactivarla, nunca
borrarla.

Sin token, pega en la conversación lo que ves en Ads Manager → Reglas automatizadas, y la skill aplica los mismos
criterios.

## 7. Con token o en Ads Manager

**Con token** (`META_TOKEN`, modo avanzado: `docs/guias/token-avanzado.md`):
1. **Prepara la propuesta.** `operador-meta` lanza `crear <json> --simular`, te lo enseña y, con tu sí, ejecuta
   `crear <json> --confirmo`. El permiso te pedirá confirmación: es intencionado.
2. **Antes de escribir, la herramienta comprueba cuatro cosas:**
   - que la moneda de la cuenta coincida con la de la ficha;
   - que no haya presupuestos activos por encima del tope, contando el presupuesto de la campaña (CBO) y los
     presupuestos totales por su ritmo diario;
   - que las reglas no existan ya: si existen, no las duplica;
   - que no queden reglas `_OS_` antiguas sobre las mismas campañas, de un CPA, un tope o un evento anteriores. Si
     las hay, no crea nada y te da la orden para desactivarlas (`pausar <ids> --cliente <slug> --confirmo`). Con tu
     sí, `operador-meta` la ejecuta y relanza `crear`.
3. **Elige a quién avisa.** Una regla creada por API avisa al usuario del token, que es un usuario del sistema y no lee
   nada. Por eso hacen falta destinatarios: `reglas_meta.py destinatarios --cliente <slug>` da los IDs de las personas
   de la cuenta, y se pasan con `--avisar`. Los nombres no se guardan en ningún archivo.
4. **Lo creado queda guardado** en `<json>.estado.json`. Si Meta rechaza una regla (por ejemplo, una fórmula con
   madurez), el error dice cuál. Lo ya creado no se duplica al relanzar.

**Sin token**: el MCP de Meta no tiene herramientas de reglas, así que se crean a mano.
1. **Genera los pasos.** `crear <json> --simular --pasos` da los pasos regla por regla. Sin token, la herramienta no
   puede comprobar dos cosas y te las pide antes:
   - **los presupuestos:** en Ads Manager (columna Presupuesto de campañas y conjuntos) o con `analista-meta`
     (`ads_get_ad_entities`), que ningún conjunto ni campaña activa tenga más de `topes.cambio_dia` al día; un
     presupuesto total cuenta por lo que queda dividido entre los días que faltan. Si alguno pasa, la regla de gasto
     lo pausaría: bájalo o sube el tope antes de crearla;
   - **las reglas antiguas:** en Reglas automatizadas, desactiva las `PROTECT_OS_…` y `ALERT_OS_…` de otro CPA, tope o
     evento que miren las mismas campañas.
2. **En Ads Manager:** menú → Reglas automatizadas → Crear regla → Regla personalizada. Eliges a qué se aplica, la
   acción, las condiciones, el intervalo de tiempo, la programación, a quién avisar y el nombre. Los nombres de los
   campos son no verificado.
3. **Elige los suscriptores.** En Ads Manager se eligen en la propia regla: añade a quien lleve la cuenta.

En los dos casos queda una fila por regla en el change log del cliente, con `Nivel` = `regla`. La fecha de
evaluación es el final del modo sombra.

## 8. Comandos

```
python3 -I herramientas/reglas_meta.py listar --cliente acme                    # reglas actuales, auditadas
python3 -I herramientas/reglas_meta.py proponer --cliente acme --conversiones-semana 40   # sombra, desde la ficha
python3 -I herramientas/reglas_meta.py proponer --cliente nimbo --evento Schedule --cpa 300  # cuenta pequeña: 4×
python3 -I herramientas/reglas_meta.py crear clientes/acme/planes/reglas-2026-11-09.json --cliente acme --simular --pasos
python3 -I herramientas/reglas_meta.py destinatarios --cliente acme             # IDs para --avisar
python3 -I herramientas/reglas_meta.py crear <json> --cliente acme --avisar <id> --confirmo   # solo operador-meta
python3 -I herramientas/reglas_meta.py historial --cliente acme --dias 14 --todas            # qué habrían hecho
python3 -I herramientas/reglas_meta.py pausar <id> --cliente acme --confirmo                 # desactiva, no borra
```

Códigos de salida:
- **0:** bien.
- **1:** error tuyo, o algo pendiente que hay que resolver antes: falta `--confirmo`, faltan destinatarios, una regla
  está prohibida, hay un presupuesto por encima del tope o quedan reglas `_OS_` antiguas activas.
- **2:** falta configuración: ficha, topes, CPA objetivo o token, o la moneda de la cuenta no coincide con la de la
  ficha.

## 9. Problemas frecuentes

- **«No me llega ningún aviso».** La regla no tiene destinatarios, o la creó el usuario del sistema. Mira la columna
  «avisa a» de `listar`, o los suscriptores en Ads Manager.
- **«Me ha pausado un conjunto por gasto».** Mira qué presupuesto tenía: si estaba por encima del tope, alguien lo
  cambió. Averigua quién (el registro de actividad de la cuenta) y decide con `/ejecutar-cambio` si se reactiva y con
  qué presupuesto. Si el tope se te ha quedado corto, súbelo en la ficha y vuelve a proponer: el umbral sale de ahí.
- **«Me ha pausado un anuncio que luego habría convertido».** Con la ventana ya madurada, compruébalo en el CRM. Si
  pasa más de una vez, sube el multiplicador o la madurez. Reactivarlo es una decisión de `/ejecutar-cambio`.
- **Presupuesto total (*lifetime*).** La regla de gasto puede pausar un conjunto con presupuesto total si su ritmo
  diario supera 2,2 veces el tope. `crear` lo cuenta por su ritmo diario (lo que queda entre los días que faltan) y se
  para si pasa del tope.
- **Has cambiado el CPA objetivo, los topes o el evento.** Las reglas no se actualizan solas: vuelve a proponer. Las
  nuevas llevan el umbral en el nombre, y `crear` no las crea mientras sigan activas las antiguas de las mismas
  campañas: te da el `pausar <ids>` para desactivarlas primero.
- **Cambios de Meta.** Tras cualquier cambio de atribución, presupuesto o medición, revisa los umbrales. Por ejemplo, la
  medición en el dispositivo desde el 12 de noviembre de 2026, fuera de la UE y el Reino Unido, puede subir las
  conversiones reportadas (KB 07, «Actualización 2026-11-09»).

## 10. Lo no verificado

- **Fórmulas con madurez.** La documentación de la API muestra fórmulas con campos con prefijo de tiempo y de nivel,
  como `today_spent / adset.daily_budget`. No he podido comprobar que Meta acepte cada combinación que genera la
  herramienta, como `lifetime_spent - last_7_days_spent` o restas entre ventanas cerradas. Si alguna falla, `crear`
  lo dice al crearla.
- **Fecha de imputación en las reglas.** Se supone que el motor de reglas imputa las conversiones igual que Ads
  Manager, al día de la impresión o el clic. Si las imputara al día de la conversión, la resta del gasto reciente
  sería menos precisa en eventos lentos.
- **Historial.** El contenido de cada entrada (`results`, `actions`) no está documentado en detalle. Tampoco si las
  reglas que solo avisan aparecen en el historial: `historial` lo lee de forma defensiva. Comprueba también los avisos
  que te lleguen por correo.
- **Personas de la cuenta.** El listado que usa `destinatarios` (`act_…/users`) puede no estar disponible para todos
  los tokens. Si falla, elige los suscriptores en Ads Manager.
- **Ads Manager.** Los nombres de los menús y de los campos de la interfaz.
