# Webinar o taller: de la idea al proyecto firmado

Un taller práctico, como «cómo quitar las horas de trabajo manual de facturas y albaranes con automatización», es la
forma más honesta de captar en un mercado frío. El dueño de la pyme ve cómo piensas antes de darte una llamada. Pero
tiene una trampa: Meta optimiza registros, y un registro no es un cliente. Esta guía explica cómo montarlo para que
cada euro se mida hasta el proyecto firmado.

Lo hace la skill **`/webinar <cliente>`**, que prepara la edición, y **`/webinar medir <cliente> <edición>`**, que la
lee después. El OS prepara todo y deja la ejecución en tus manos:
- tú publicas las páginas, activas los mensajes y das el taller;
- las campañas las crea `/lanzar-campana`, en pausa y con tu aprobación.

## 1. Cuándo sí y cuándo no

| Sí | No |
|---|---|
| El dueño no sabe que su proceso se puede automatizar, o desconfía tras años de promesas de IA | Tu oferta se entiende en una página: ve directo a diagnóstico (`/disenar-funnel`) |
| Vendes formación in-company o necesitas educar antes de vender | Nadie puede atender las llamadas de los 10 días siguientes |
| Alguien explica bien y puede repetirlo cada mes | La plataforma no te dice quién asistió |

Fuente: `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §4.2 y §5.5.

## 2. El recorrido completo

```
Anuncio → registro (CompleteRegistration) → recordatorios → asistió (WebinarAsistido)
        → [se quedó hasta la oferta] → llamada (Schedule) → llamada asistida (LlamadaAsistida)
        → propuesta (PropuestaEnviada) → ganado (Purchase con valor)
```

Meta solo ve el registro si no le devuelves lo demás. Si no le devuelves la asistencia, optimizará a gente que se
registra y no aparece **[STRONG INFERENCE]**
(`meta-ads-kb/05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md` §1).

## 3. Tema y promesa

El tema es **un proceso del comprador**, no una tecnología. Fórmula: «<formato> (<duración>): cómo <resultado
concreto> en <proceso>, <sin objeción>, con <entregable>».

| Flojo | Mejor |
|---|---|
| «Webinar: la IA que transformará tu empresa» | «Taller en directo (45 min): cómo detectar qué parte de la gestión de albaranes y facturas de proveedor puedes automatizar este trimestre, sin cambiar de ERP, con la plantilla para calcular las horas que hoy se van en teclear» |
| «Ahorra 20 horas a la semana con agentes de IA» | «Qué automatizar primero en una clínica dental: recordatorios, reprogramaciones y presupuestos, con casos reales de Clínica Sonrisa» (con su permiso) |
| «Masterclass de automatización» | «Los 5 procesos que una gestoría pequeña puede dejar de teclear, y los 2 que no compensa tocar» |

La promesa lleva:
- 3 aprendizajes concretos;
- para quién es y para quién no;
- un entregable que se usa al día siguiente (plantilla de horas, checklist, mapa del proceso).

Nada de ahorros ni ingresos garantizados. Las cifras, solo las aprobadas en la ficha: es mal marketing y riesgo de
política a la vez (`meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`; playbook
consultoras §8.7).

## 4. Formato

| Formato | Para qué | Ojo con |
|---|---|---|
| **Directo en abierto**, 45–60 min con preguntas | Las primeras ediciones: oyes las objeciones en vivo | La franja: para dueños de pymes, entre semana a media mañana o a primera hora de la tarde **[HYPOTHESIS]** |
| **Grabado a horario** (evergreen) | Captación continua cuando ya sabes que convierte | Nunca lo anuncies como directo |
| **Taller de pago**, 2–3 h con ejercicio | Filtrar a quien paga: el `Purchase` es la mejor señal para Meta (05/07 §2) | Menos registros; factura y reembolso |
| **In-company** | Formación de un equipo concreto | No se capta con anuncios: se ofrece al final del taller abierto |

Elige una plataforma (Zoom, Meet, Livestorm, YouTube…) que te dé **quién asistió y cuántos minutos**, en una
exportación o en un webhook. Sin ese dato, nada de lo que sigue funciona.

## 5. Economía: cuánto puedes pagar por registro y por asistente

Primero calcula el coste máximo por asistente. El coste por registro sale de ahí, con una asistencia realista (playbook
webinars, TL;DR). `herramientas/economia.py leadgen` no tiene modo de webinar, pero sus cuatro tasas encajan:

| Parámetro | Paso del taller | En la salida, la línea… | …significa |
|---|---|---|---|
| `--cualif` | Registro → asistió en directo | `BE_CPL` | Máximo por registro |
| `--agenda` | Asistió → llamada agendada | `BE_por_lead_cualificado` | Máximo por asistente |
| `--show` | Llamada agendada → asistida | `BE_por_llamada_agendada` | Máximo por llamada |
| `--cierre` | Llamada asistida → ganado | `BE_por_show` | Máximo por llamada asistida |

**Ejemplo (Acme Automations).** Proyecto de 9.000 € sin IVA, con la contribución del playbook consultoras §3.3. Las
tasas son supuestos **[HYPOTHESIS]**:
- asistencia del 30 %;
- el 15 % de los asistentes reserva;
- el 75 % de las llamadas se celebra;
- el 17,5 % de las llamadas asistidas acaba en proyecto (50 % a propuesta × 35 % de cierre).

```bash
python3 -I herramientas/economia.py leadgen --precio 9000 --iva 0 --pct-pago-unico 0 --cuotas 2 \
    --recargo-cuotas 0 --impago-cuotas 0.05 --pasarela-pct 0.005 --entrega-pct 0.45 --coste-fijo 1400 \
    --cualif 0.30 --agenda 0.15 --show 0.75 --cierre 0.175 --inversion 1500 --cpl 12
```

| Etapa | Break-even | Target (margen del 50 %) |
|---|---|---|
| Registro | 19,98 € | 9,99 € |
| Asistente | 66,59 € | 33,30 € |
| Llamada agendada | 443,94 € | 221,97 € |
| Llamada asistida | 591,92 € | 295,96 € |
| Proyecto (CAC) | 3.382,38 € | 1.691,19 € |

El break-even por registro depende sobre todo de la asistencia y de cuántos asistentes reservan:

| Asistencia \ reservan | 10 % | 15 % | 20 % |
|---|---|---|---|
| 20 % | 8,88 € | 13,32 € | 17,76 € |
| 30 % | 13,32 € | 19,98 € | 26,64 € |
| 40 % | 17,76 € | 26,64 € | 35,51 € |

Para la misma Acme, el break-even por lead del embudo directo de diagnóstico es de 93 € (playbook consultoras §3.3).
Un registro es mucho más barato, pero vale mucho menos.

**Cuánto da una edición.** Con un coste por registro de 10–15 €:

```bash
python3 -I herramientas/economia.py prevision --modelo servicios --inversion 1000,1500,3000 --cpl 10-15 \
    --cualif 0.30 --agenda 0.15 --show 0.75 --cierre 0.175 --contribucion-venta 3382
```

| Inversión | Registros | Asistentes | Llamadas | Proyectos | Probabilidad de 0 proyectos |
|---|---|---|---|---|---|
| 1.000 € | 80 | 24 | 3,6 | 0,5 | 62 % |
| 1.500 € | 106 | 32 | 4,8 | 0,6 | 53 % |
| 3.000 € | 173 | 52 | 7,8 | 1,0 | 36 % |

**Lectura:**
- Una edición de 1.500 € tiene más de la mitad de probabilidades de no traer ningún proyecto aunque todo funcione
  **[STRONG INFERENCE: Poisson]**.
- Por eso se decide por **bloques de 3 ediciones** y por coste por llamada asistida, no por la venta de una edición.
- Comprueba también que las 4–8 llamadas caben en el calendario de quien las hace.

## 6. Medición: etapas, eventos y GHL

| Paso | Evento a Meta | Desde dónde |
|---|---|---|
| Registro | `CompleteRegistration` | La página: navegador + servidor con el mismo `event_id` |
| Asistió en directo | `WebinarAsistido` (personalizado) | GHL, al mover la etapa |
| Se quedó hasta la oferta | `WebinarHastaOferta` (personalizado, si la plataforma da minutos) | GHL |
| Cualificado, llamada, llamada asistida, propuesta, ganado | `LeadCualificado`, `Schedule`, `LlamadaAsistida`, `PropuestaEnviada`, `Purchase` con `value` y `currency` | GHL (contrato §16; `Schedule`, desde una sola fuente) |

**Por qué `CompleteRegistration` y no `Lead`:**
- el `Lead` de tu embudo principal no se mezcla con registros;
- es el evento que recomienda la KB para eventos (playbook webinars §3).

La KB usa los nombres `WebinarAttended` y `StayedToPitch`: son los mismos eventos.

**En GHL, un pipeline propio «Taller»**, con estas etapas en este orden:

```
Registrado → Asistió al taller → [Se quedó a la oferta] → Cualificado → Llamada agendada
→ Llamada asistida → Propuesta enviada → Purchase → Perdido
```

- **Workflows.** Cada etapa manda su evento con un workflow con «Allow Multiple» (`docs/guias/ghl-meta.md` §4).
  De Cualificado en adelante son los mismos eventos y el mismo dataset que tu pipeline principal.
- **Una sola fuente para el registro.** El evento de servidor del registro lo manda quien recibe el webhook de la
  página con su `event_id` (`docs/guias/capi.md` §3–5). No lo repitas desde la etapa Registrado sin ese `event_id`:
  Meta contaría cada registro dos veces.
- **La oportunidad no cambia de pipeline:** así no se pierde quién asistió.
- **Asistencia.** Llega por un webhook de la plataforma (con Zapier, Make o n8n) o importando su exportación el mismo
  día del taller. Usa la etiqueta `taller-<AAAA-MM-DD>`, y `taller-repeticion` para quien solo vio la grabación: eso
  no es asistencia en directo.
- **Prueba de punta a punta** antes de lanzar, con `/implementar-capi` y el código de *Probar eventos*. Un registro de
  prueba tiene que llegar a GHL con su `ad_id`, moverse de etapa y verse en Events Manager.

**Qué optimizar.** Con menos de 50 asistentes a la semana, que es lo normal en una consultora, optimiza a
`CompleteRegistration` y usa la asistencia para medir y para audiencias. Con 50 o más, prueba a optimizar a
`WebinarAsistido` (playbook webinars §3).

## 7. Páginas de registro y gracias

**Registro:**
- [ ] la promesa como título;
- [ ] fecha, hora con zona horaria (una por país si vendes en varios), duración y plataforma;
- [ ] quién lo da, con una prueba verificable;
- [ ] los 3 aprendizajes, para quién es y para quién no, y el entregable;
- [ ] formulario corto: nombre, email, teléfono, una pregunta de compromiso («¿qué proceso te gustaría quitarte de
      encima?») y una de cualificación (tamaño de empresa);
- [ ] consentimientos separados para recibir recordatorios por email y por WhatsApp; el píxel, solo tras aceptar
      cookies (contrato §17).

**Gracias:**
- [ ] botón para añadir al calendario;
- [ ] confirmación por WhatsApp (si dio permiso);
- [ ] la tarea previa («trae cuántos albaranes entran por semana»). El entregable completo se da en el taller: si lo
      regalas aquí, quien solo quería el archivo ya no tiene motivo para venir **[HYPOTHESIS]**;
- [ ] qué va a pasar en el taller.

```bash
python3 -I herramientas/paginas.py generar webinar --config clientes/acme/planes/2026-12-10_webinar-albaranes.registro.json \
    --salida clientes/acme/paginas/2026-12-10_webinar-albaranes/registro/ --cliente acme
python3 -I herramientas/paginas.py generar gracias --config clientes/acme/planes/2026-12-10_webinar-albaranes.gracias.json \
    --salida clientes/acme/paginas/2026-12-10_webinar-albaranes/gracias/ --cliente acme
python3 -I herramientas/paginas.py validar clientes/acme/paginas/2026-12-10_webinar-albaranes/
```

- **Cada carpeta, su `index.html`.** Un config con una sola página la escribe como `index.html`: así `registro/` y
  `gracias/` funcionan en cualquier hosting.
- **El salto a gracias, a mano:** `"siguiente": "../gracias/"` en el formulario del registro (`@gracias` solo vale
  cuando las dos páginas están en el mismo config).
- **Valida la carpeta madre**, no solo `registro/`: así `validar` comprueba que `../gracias/` existe y tiene su
  `index.html`. Una carpeta sin él es un 404 al publicar, y es error.
- **Fecha y hora.** En `webinar.evento`, `inicio` sin desfase (`2026-12-10T18:00:00`) y `zona_horaria` con su nombre
  IANA (`Europe/Madrid`); sin ella, la de la ficha (`--cliente`). El desfase se calcula para esa fecha, con el horario
  de verano. Si escribes uno que no es el de esa fecha (`+01:00` en julio), `generar` para y te dice el bueno. En
  gracias, el mismo evento en `anadir_calendario`.
- **Moneda.** Las cifras y el `value` de los eventos van en la de la ficha (con `--cliente`), salvo que el config ponga
  `sitio.moneda`.

Las claves del JSON están en `plantillas/paginas/README.md`. Tú subes la carpeta a tu hosting o a GHL; el OS nunca
despliega. Con la página publicada, `/landing` la revisa en móvil.

**¿Y un formulario instantáneo?** El registro sale más barato y suele asistir menos gente **[HYPOTHESIS]** (05/07 §1).
Si lo pruebas (`/formulario-instantaneo`), ponlo en un conjunto aparte y compáralo por coste por asistente. En Meta, el
registro contará como lead.

## 8. Campañas por fase

Calendario de una edición, adaptado del playbook webinars §7:

| Cuándo | Qué |
|---|---|
| D-28 a D-21 | Economía, señal probada, páginas publicadas, secuencia de recordatorios lista, lote de anuncios aprobado |
| D-21 | Arranca la campaña de registro (`/lanzar-campana`) |
| D-14 | Primera lectura: coste por registro frente al break-even, respuestas a la pregunta de compromiso, frecuencia |
| D-10 a D-1 | Concentra el gasto: quien se registra cerca de la fecha asiste más **[HYPOTHESIS]** |
| D-3 a D0 | Recordatorio a registrados |
| D0 | «Empieza en 15 minutos»; el taller; la asistencia a GHL ese mismo día |
| D0 a D+7 | Repetición con caducidad, llamadas, campaña de después |
| D+14 | `/webinar medir`: asistencia, llamadas |
| D+45 | `/webinar medir`: propuestas y proyectos; decisión sobre la siguiente edición |

| Fase | Campaña / conjunto | Optimiza a | Audiencia | Presupuesto **[HYPOTHESIS]** |
|---|---|---|---|---|
| Registro | `ES_LEADS_TALLER_HV` / `BROAD-A+_COMPLETEREGISTRATION`, con `fin` a la hora de inicio | `COMPLETE_REGISTRATION` | Advantage+ amplia; excluye clientes y registrados | 50–70 % |
| Recordatorio y directo | `ES_AWARENESS_RECORDATORIO-TALLER_HV` / `REGISTRADOS-TALLER_REACH` | Alcance | Registrados (audiencia de sitio web con `CompleteRegistration`, o lista de `privado/`) | 4–8 % |
| Después | `ES_LEADS_TALLER-POST_HV` / `REGISTRADOS-TALLER_SCHEDULE` | `SCHEDULE`, o alcance si la audiencia es pequeña | Registrados, sin ganados ni quien ya tiene llamada | 15–30 % |

Los nombres están validados con `nomenclatura.py`. Los repartos salen de 05/07 §3 y son heurísticas, no benchmarks.

- **Si la audiencia es pequeña.** Con pocos cientos de registrados, las campañas a registrados pueden no entregar o
  salir caras **[HYPOTHESIS]**. Entonces bastan email y WhatsApp, y ese dinero va al registro.
- **Una campaña de registro para todas las ediciones.** Cada edición es un conjunto nuevo con `inicio` y `fin`, dentro
  de la misma campaña (`"campana": {"id": …}` en el plan, ver `plantillas/plan-campana.json`), con anuncios fechados.
- **No la toques a diario.** Una campaña de registro necesita 10–21 días estables (05/07, «Implicaciones operativas»).
- **Anuncios de recordatorio de Instagram.** Van ligados a un evento próximo de Instagram y dejan de entregarse cuando
  el evento pasa **[OFFICIAL META]** (Marketing API, consultada el 2026-11-09). Son opcionales, se crean en Ads
  Manager y no hay datos de que suban la asistencia en B2B.

**Anuncios del lote** (`/brief-creativo` → `/producir-video` o `/producir-estatico` → `/revisar-anuncio`):
- **para el registro**, 4–6 piezas de al menos 3 conceptos:
  - el ponente con el aprendizaje 1;
  - una demo de 20 s del entregable;
  - el antes y el después del proceso;
  - la objeción «¿esto no lo hace ya ChatGPT?»;
  - un clip de una edición anterior (`/organico-a-anuncios`);
- **para el recordatorio**, «mañana a las 10:00» y «empieza en 15 minutos»;
- **para después**, la repetición, un caso y una objeción.

En todos, fecha y hora. «Directo» y «plazas», solo si es verdad.

## 9. Recordatorios y asistencia

`/seguimiento-leads` diseña la secuencia y la deja lista en GHL; tú la activas. El OS nunca manda mensajes.

| Cuándo | Canal | Qué |
|---|---|---|
| Al registrarse | Email + WhatsApp (con permiso) | Confirmación, enlace de calendario, la tarea previa |
| D-1 | Email + WhatsApp | Qué te vas a llevar y qué tienes que traer |
| 1–2 h antes | WhatsApp o email | El enlace directo (05/08) |
| Al empezar | WhatsApp | «Estamos dentro» con el enlace |
| D0, al terminar | Email | A quien no vino: la repetición, con su fecha de caducidad real |
| D+1 | Email + WhatsApp | A quien vino: el siguiente paso y el enlace de reserva |

**Qué mueve de verdad la asistencia:**
- Los recordatorios son higiene. La única prueba controlada con recordatorios automáticos dio −1,6 puntos de
  ausencias, no significativo **[EMPIRICAL]** (05/07, TL;DR).
- La asistencia se gana con una promesa concreta, con la cercanía de la fecha y con compromiso: la pregunta del
  formulario, la tarea previa, el calendario.
- Un mensaje personal del ponente a quien encaja con tu cliente ideal. Lo escribes tú.
- **Con menos del 20 % de asistencia:** revisa confirmación, recordatorios, franja y promesa, y valora pasar a
  grabado (playbook webinars §8).

## 10. El guion: enseñar primero, ofrecer al final

| Minutos | Bloque |
|---|---|
| 0–3 | Quién eres en una frase, qué se van a llevar y que al final contarás cómo trabajáis. Anunciarlo al principio es honesto y no espanta |
| 3–10 | El problema en su proceso, con números que puedan comprobar en la plantilla |
| 10–35 | Los 3 aprendizajes. Cada uno con una demo con datos ficticios, un ejercicio en la plantilla y un caso con permiso |
| 35–42 | Qué **no** automatizar y cuándo no compensa: es lo que más credibilidad da (playbook consultoras §4.1) |
| 42–50 | La oferta: el siguiente paso, para quién es y para quién no, qué pasa en la llamada y cuántos huecos reales hay esta semana |
| 50–60 | Preguntas. El enlace de reserva en el chat y en pantalla |

| Oferta del final | Cuándo |
|---|---|
| Diagnóstico de 30 min con el ponente | La opción por defecto: es la llamada de tu embudo |
| Piloto acotado (un proceso, precio cerrado) | Cuando el taller ya demostró el método y el ticket del proyecto asusta |
| Formación in-company | Cuando quien asiste es RR. HH. o el dueño quiere formar a su equipo |

- **Escasez, solo la real:** los huecos del calendario de quien hace las llamadas. Nada de cuentas atrás falsas.
- **Grabación:** graba al ponente y la pantalla, no a los asistentes, y avisa al principio. La grabación da la
  repetición y los clips de la próxima edición.
- **Día D:**
  - enlace probado;
  - alguien atendiendo el chat;
  - una encuesta final de una pregunta («¿quieres el diagnóstico?»);
  - huecos abiertos en el calendario.
- **Al terminar:** a quien pidió llamada se le contacta en menos de una hora
  (`meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`).

## 11. Después del taller: a cada uno, su mensaje

| Quién | Qué le enseñas | Cómo | Hasta |
|---|---|---|---|
| Se registró y no vino | La repetición y un clip con la idea clave | Email y WhatsApp; anuncios si la audiencia da | 7 días; después, la siguiente edición |
| Vino y no reservó | Un caso, una objeción, el diagnóstico | `/anuncios-por-etapa` y `/seguimiento-leads` | 14–30 días **[HYPOTHESIS]** |
| Se quedó hasta la oferta y no reservó | Un mensaje personal del ponente | Tú, a mano | 48 h |
| Llamada, propuesta abierta o perdido por «mal momento» | El ciclo normal; el perdido, al taller de dentro de 2–6 meses | `/anuncios-por-etapa` (playbook consultoras §9.5) | — |
| Ganado | Nada: exclúyelo de todo | — | — |

Las listas por etapa salen de `privado/` con `audiencias_meta.py etapas`. Fuera de esa carpeta, solo agregados.

## 12. Repetición y evergreen

- **Cadencia mensual en directo** mientras aprendes: cada edición mejora tema, franja, anuncios y guion.
- **Tras 2–3 ediciones con conversión medida**, valora el grabado a horario. La campaña de registro queda siempre
  activa y lees cohortes semanales (05/07 §4). Es honesto si dices que es una sesión grabada.
- **Los mejores minutos de cada grabación** son anuncios: `/organico-a-anuncios <cliente> archivo <grabación>`.
- **Para** si, tras 3 ediciones, el coste por llamada asistida sigue por encima del break-even y ni el tema ni la
  oferta lo han movido. Vuelve al embudo directo.

## 13. Leer los resultados

```bash
python3 -I herramientas/ghl.py por-anuncio --cliente acme --desde 2026-09-24 --hasta 2026-10-15 --cualificado "Asistió al taller"
python3 -I herramientas/meta_ads.py anuncios --cliente acme --campana TALLER --desde 2026-09-24 --hasta 2026-10-22
python3 -I herramientas/embudo.py cohortes --cliente acme --por anuncio \
    --leads clientes/acme/privado/leads-ghl_2026-09-24_2026-10-15.csv --meta <CSV que deja meta_ads.py anuncios>
```

En `ghl.py`, las columnas se leen así en la campaña del taller:
- `leads` = registros;
- `cualificados` = asistentes o más avanzados;
- `citas` = llamadas;
- `shows` = llamadas asistidas;
- `clientes_pago` = proyectos.

Las propuestas salen de `ghl.py oportunidades`. Dos cosas a tener en cuenta:
- quien ya era contacto antes del periodo no entra en la cohorte: cuéntalo aparte;
- quien reservó desde la repetición sin asistir también cae en `cualificados`: sepáralo con la etiqueta.

**Ejemplo: edición `2026-10-15_webinar-albaranes` de Acme, a D+14.** Datos ficticios.

| Anuncio | Gasto | Registros | € / registro | Asistentes | Asistencia | € / asistente | Llamadas | Asistidas |
|---|---|---|---|---|---|---|---|---|
| `20260924_horas-perdidas_lunes-de-albaranes_founder_h1` | 620 € | 52 | 11,92 € | 19 | 37 % | 32,63 € | 3 | 3 |
| `20260924_horas-perdidas_plantilla-horas_demo_h1` | 410 € | 41 | 10,00 € | 9 | 22 % | 45,56 € | 1 | 1 |
| `20260924_objecion-chatgpt_chatgpt-no-basta_founder_h1` | 300 € | 18 | 16,67 € | 7 | 39 % | 42,86 € | 1 | 0 |
| `20260924_antes-despues_albaran-a-erp_estatico_h1` | 170 € | 6 | 28,33 € | 0 | 0 % | — | 0 | 0 |
| **Total** | **1.500 €** | **117** | **12,82 €** | **35** | **30 %** | **42,86 €** | **5** | **4** |

**Lectura frente al ejemplo de la sección 5:**
- **El total es viable pero no está en target.** 42,86 € por asistente queda entre el target (33,30 €) y el
  break-even (66,59 €). 375 € por llamada asistida también queda entre los dos (295,96 € y 591,92 €).
- **El estático, fuera la próxima edición.** Gastó más de 2–3 veces el target por asistente sin ningún asistente
  (`meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md` §5).
- **La demo trae el registro más barato y la asistencia más baja.** Su promesa («descarga la plantilla») atrae a
  quien solo quiere el archivo **[HYPOTHESIS]**. En la próxima edición, que venda el taller y entregue la plantilla en
  directo, diciéndolo.
- **El del fundador gana en coste por asistente.** Haz 2 hooks nuevos con `/variantes`. Con 7–19 asistentes por
  anuncio, la diferencia con el de la objeción es orientativa: suma ediciones antes de dar un ganador.
- **A D+45** toca la segunda lectura: propuestas y proyectos. Un proyecto firmado o ninguno son, los dos, resultados
  compatibles con esta economía (sección 5).

La skill deja el informe en `clientes/<slug>/informes/webinars/<edición>.md`, con lo que cambia en la siguiente
edición. Lo aprendido va a `aprendizajes-creativos.md`, y a `aprendizajes/` si contradice la KB.

## 14. Errores frecuentes

- Juzgar el taller por coste por registro (05/07, «Errores frecuentes»).
- Optimizar a registros sin devolver la asistencia y extrañarse de un 15 % de asistencia.
- Mandar `CompleteRegistration` por el navegador y por GHL sin `event_id` común: cada registro cuenta dos veces.
- Anunciar «en directo» una grabación, o «últimas plazas» con 300 plazas libres.
- Dar el entregable completo en la página de gracias y esperar que vengan al taller.
- Vender durante 20 minutos: la oferta va al final y dura 8.
- No tener huecos en el calendario la semana del taller.
- Cambiar presupuestos a diario en una campaña de registro de 2–3 semanas.
- No excluir a clientes y ganados de la campaña de después.
