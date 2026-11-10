# Playbook: consultoras y agencias de IA y automatización que venden soluciones a pymes

> Última verificación: 2026-11-09 · Autor: B16 (agente) · Ámbito: consultoras, agencias, freelances de IA y
> automatización (y SaaS cercanos) que venden **soluciones a medida a pymes** con una oferta de entrada, una llamada,
> una propuesta y un cierre: integraciones entre herramientas, lectura de documentos con revisión humana, buscadores
> internos, generadores de presupuestos, asistentes con la documentación de la empresa, seguimiento automático de
> propuestas, entrada única y reparto de leads, confirmación y reprogramación de citas (voz o WhatsApp), facturación y
> cobros, informes y cuadros de mando, altas de clientes y formación in-company. Proyectos desde unos miles de euros,
> pocos leads y ciclos de semanas. Etapas del embudo: contrato §16 (`docs/desarrollo/contratos.md`).
> Base: [05/03](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md),
> [05/05](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md),
> [05/06](../05-leadgen-high-ticket-crm/06-high-ticket-funnels.md),
> [05/08](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md),
> [05/09](../05-leadgen-high-ticket-crm/09-sales-feedback-loop.md), [13](../13-sistema-operativo/README.md) y los
> playbooks [B2B](playbook-b2b.md), [high-ticket](playbook-high-ticket.md) y
> [agencias y consultores](playbook-agencias-consultores.md) (su parte B cubre gestionar Meta para clientes).
> Fuentes externas al final, con fecha y tipo.

## TL;DR

- **Meta es tu canal cuando el comprador es el dueño o el gerente de una pyme y tu solución se explica con un proceso
  suyo** («los albaranes que alguien teclea cada lunes»), no con tecnología («agentes de IA»). Para cargos concretos en
  empresas grandes, comités de compra o listas cerradas de cuentas, LinkedIn y el outbound van primero y Meta hace de
  cobertura barata. **[STRONG INFERENCE]** sobre datos B2B de [05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md).
- **La economía real incluye el tiempo de vender.** Una llamada de diagnóstico y una propuesta investigada cuestan horas
  del fundador por cada proyecto que *no* se firma. En el ejemplo de Acme Automations (proyecto de 9.000 €), ese coste
  es ~1.400 € por venta y la contribución queda en **3.382 €**: break-even de **93 € por lead, 592 € por llamada
  asistida y 1.184 € por propuesta**. **[STRONG INFERENCE]** (aritmética con `herramientas/economia.py`)
- **El techo de inversión casi nunca lo pone Meta, sino tu capacidad de diagnosticar y proponer.** Con 2 propuestas
  investigadas por semana, Acme no puede pasar de ~5.000 €/mes sin contratar o filtrar más antes de la propuesta.
  **[STRONG INFERENCE]**
- **La oferta de entrada tiene que dar valor y precualificar a la vez**: un diagnóstico de horas manuales por proceso,
  con supuestos explícitos y capaz de decir «con estos números no te compensa contratarnos». Filtra al curioso,
  genera confianza en un mercado saturado de promesas y te da los datos de la propuesta. **[STRONG INFERENCE]**
- **Evento de optimización según volumen semanal, no según deseo**: con menos de ~10 cualificados por semana optimiza
  a `Lead` (formulario de alta intención) o a `DiagnosticoCompletado` (web) y manda todas las etapas a Meta para medir.
  Conversion Leads (*Maximize number of qualified leads*) exige CAPI desde abril de 2026, una etapa con 1–40 % de
  conversión en ≤28 días y volumen suficiente para aprender; en la mayoría de consultoras pequeñas es una prueba de los
  meses 3–6, no del día 1. **[OFFICIAL META]** (requisitos, verificados el 2026-11-09) + **[STRONG INFERENCE]** (cuándo)
- **Estructura con poco volumen: una campaña, un conjunto, Advantage+, 3–8 anuncios de conceptos distintos.** Nada de
  conjuntos por sector ni campañas de retargeting de 10 €/día. Lo que separa es la economía, no el sector.
  **[OFFICIAL META]** + **[EMPIRICAL]** ([13/09](../13-sistema-operativo/09-presupuesto-pequeno-y-grande.md))
- **La creatividad que vende consultoría es prueba, no promesa**: fundador a cámara, demo del sistema con datos
  ficticios, antes y después del proceso, casos con cifras verificables y anuncios que responden objeciones
  («¿esto no lo hace ya ChatGPT?», privacidad, «mi equipo no lo va a usar», «ya probamos», precio). Las promesas de
  ahorro sin contexto son a la vez mal marketing y riesgo de política. **[STRONG INFERENCE]** + **[OFFICIAL META]**
  ([08/11](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md))
- **Después del lead se gana o se pierde casi todo**: respuesta en minutos, cita en ≤72 h, confirmación activa, una
  llamada que diagnostica (no que vende) y una propuesta con hallazgos comprobables, precio cerrado y lo que *no* se
  propone. Subir el show del 60 % al 80 % vale lo mismo que bajar el CPL un 25 %. **[STRONG INFERENCE]**
  ([05/08](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md))
- **Decide con la capa más baja de verdad que ya haya madurado**: anuncios por coste por diagnóstico o cualificado
  (días), embudos por coste por llamada asistida (2–3 semanas), presupuesto por CAC y pipeline de la cohorte
  (6–8 semanas). Con 2 proyectos al mes, un mes sin ventas tiene un 16 % de probabilidad aunque todo vaya bien: evalúa
  por trimestre. **[STRONG INFERENCE]** (Poisson)

---

## 0. Cómo se usa este playbook con el OS

Cada sección cita la skill, el agente o la herramienta que la ejecuta. El recorrido normal con un negocio propio
(`relacion: propio`, `tipo: servicios-high-ticket` en la ficha):

| Fase | Qué decides | Skill | Herramienta o agente |
|---|---|---|---|
| F0 Negocio | Economía por etapa, oferta de entrada y principal, embudo | `/cliente-nuevo`, `/economia`, `/oferta`, `/iman-de-leads`, `/disenar-funnel` | `economia.py leadgen` y `prevision`, `analista-cuantitativo`, `especialista-funnel` |
| F1 Señal | Cuenta, dataset, CAPI web y CRM, pipeline §16, páginas y formularios | `/configurar-meta`, `/implementar-capi`, `/construir-landing`, `/formulario-instantaneo`, `/landing`, `/audiencias` | `paginas.py generar diagnostico`, `formularios_meta.py`, `capi.py`, `ingeniero-capi`, `especialista-crm` |
| F2 Investigación | Lenguaje del comprador, competencia | `/voz-cliente`, `/competencia` | `ad_library.py`, `reddit_pulso.py`, `investigador-competencia` |
| F3 Creatividad | Conceptos, casos, pruebas, políticas | `/brief-creativo`, `/siguiente-anuncio`, `/casos-y-creadores`, `/organico-a-anuncios`, `/producir-video`, `/producir-estatico`, `/revisar-anuncio`, `/analisis-creativo` | `estratega-creativo`, `redactor-anuncios`, `critico-creativo`, `revisor-politicas`, `elementos_creativos.py` |
| F4 Lanzamiento | Campaña en pausa, lotes de test, taller o webinar | `/lanzar-campana`, `/publicar-anuncios`, `/test-creativo`, `/webinar` | `operador-meta`, `revisor-estrategia`, `meta_ads.py` |
| F5 Operación | Velocidad de respuesta, anuncios por etapa, cohortes, protección | `/seguimiento-leads`, `/anuncios-por-etapa`, `/brief-diario`, `/informe-semanal`, `/embudo`, `/diagnostico`, `/reglas-automaticas` | `audiencias_meta.py etapas`, `embudo.py cohortes`, `ghl.py por-anuncio`, `registro_creativo.py`, `reglas_meta.py` |
| F6 Escalado | Subir por coste marginal y capacidad | `/escalar`, `/revision-mensual` | `analista-cuantitativo`, `estadistica.py` |

Si además llevas Meta a tus clientes, la sección 14 y la [parte B del playbook de agencias](playbook-agencias-consultores.md)
son las tuyas.

---

## 1. El negocio que captamos y por qué es distinto

**Qué vendes.** No vendes «IA». Vendes menos horas en tareas que nadie quiere hacer, menos errores al copiar datos
entre programas, respuestas más rápidas a clientes y la tranquilidad de que algo que hoy depende de una persona no se
cae cuando esa persona se va de vacaciones. La IA es el cómo, y para tu comprador el cómo es un riesgo, no un beneficio.
**[STRONG INFERENCE]**

**A quién.** Dueños y gerentes de pymes (de 5 a 100 personas, sobre todo de 10 a 50), con un responsable de
administración u operaciones que sufre el proceso. Decide una persona o dos, sin departamento de compras, con dinero de
su empresa y con miedo a tres cosas: que sea complicado, que no funcione y que su equipo no lo use. Ha probado ChatGPT y
pregunta, con razón, «¿esto no lo hace ya ChatGPT?».

**Lo que dicen los datos del comprador español** (encuesta TIC del INE publicada el 2026-10-22; los datos de 2026 no son
comparables con años anteriores por el cambio a la CNAE-2025):

- Usan IA el **21,4 %** de las empresas de menos de 10 empleados, el **29,1 %** de las de 10–49 y el **48,9 %** de las
  de 50–249. Entre las de 10 o más que la usan, el **43,3 %** recurre a sistemas desarrollados por proveedores externos
  (38,7 % en las de 10–49): tu mercado existe y compra fuera. **[OFFICIAL — INE]**
- Entre las que se plantearon usarla y no lo hicieron, las barreras son la **falta de conocimientos** (~80 %), las
  **dudas legales** y la **privacidad** (~53 % cada una) y, en las de menos de 10, el **coste** (61 %); «no es útil»
  solo lo dice el 13–14 %. **[OFFICIAL — INE]** Eurostat da el mismo orden para la UE en 2025. Consecuencia: tu
  creatividad tiene que enseñar (cómo funciona), tranquilizar (datos, contrato) y dar precio, no convencer de que la IA
  sirve. **[STRONG INFERENCE]**
- El comprador B2B desconfía de lo que le cuenta la IA y quiere validarlo con una persona: en la encuesta de Gartner
  (645 compradores, publicada el 2026-05-20), el 69 % acude a un comercial para validar lo que le dice la IA y el 51 %
  cree más probable recibir información engañosa de la IA generativa. **[EMPIRICAL]**

**Cómo compra.** Rara vez por impulso. El patrón que mejor funciona es el de la venta consultiva:

```
Anuncio (un proceso suyo, con prueba)
 → Oferta de entrada que da valor y precualifica (diagnóstico, calculadora, auditoría, taller)
   → Llamada de diagnóstico (30–45 min, con sus números)
     → Propuesta investigada (hallazgos comprobables, precio cerrado, qué no se propone y por qué)
       → Cierre (a veces con un piloto pagado) → proyecto → mantenimiento
```

Las etapas canónicas que usan la ficha, GHL, la CAPI, las audiencias y los informes (contrato §16):

| Id | Etapa | Evento a Meta |
|---|---|---|
| `lead` | Deja sus datos (formulario, diagnóstico o mensaje) | `Lead` |
| `diagnostico` | Completa el diagnóstico o la calculadora | `DiagnosticoCompletado` (personalizado) |
| `cualificado` | Pasa el filtro escrito | `LeadCualificado` (personalizado) |
| `llamada` | Agenda la llamada | `Schedule` |
| `asistio` | Se presenta | `LlamadaAsistida` (personalizado) |
| `propuesta` | Recibe propuesta | `PropuestaEnviada` (personalizado) |
| `ganado` | Firma | `Purchase` con `value` y `currency` |
| `perdido` | Descartado o perdido | — (audiencias, exclusiones y motivo en el CRM) |

**Qué cambia frente al high-ticket de coaching** ([playbook-high-ticket](playbook-high-ticket.md)):

| Aspecto | Coaching o infoproducto high-ticket | Consultora de IA y automatización |
|---|---|---|
| Decisión | Personal, emocional, rápida | De empresa, racional, con miedo al riesgo operativo |
| Prueba que convence | Transformación de una persona | Proceso del cliente antes y después, con números de su negocio |
| Precio | Fijo y comunicado | A medida; rangos y precio cerrado tras el diagnóstico |
| Cuello de botella | Closer y show | Tiempo del fundador para diagnosticar y proponer |
| Ciclo | Días | 2–8 semanas (más si hay piloto) |
| Riesgo de política | Promesas de ingresos | Promesas de ahorro, «sustituye a tu equipo», falsos testimonios hechos con IA |
| Evento optimizable | `Schedule` o aplicación con volumen | Casi nunca la venta; casi siempre `Lead` o `DiagnosticoCompletado` al principio |

---

## 2. Cuándo Meta es el canal y cuándo no

### 2.1 Por tipo de comprador

| Situación | Meta | LinkedIn | Outbound (email, llamada, mensaje directo) | Referidos y alianzas |
|---|---|---|---|---|
| Dueños y gerentes de pymes de 5–100 personas | **Principal** | Apoyo (contenido del fundador) | Apoyo con listas muy concretas | **El que mejor cierra** |
| Cargos concretos (director de operaciones, CFO) en empresas de 200+ | Cobertura (retargeting) | **Principal** | **Principal** | Apoyo |
| Lista cerrada de 50–300 cuentas (ABM) | Cobertura de visitantes y vídeo | **Principal** | **Principal** | — |
| Un nicho vertical pequeño (p. ej. 400 empresas en tu provincia) | Funciona con creatividad del nicho, pero el bolsillo se agota rápido | Apoyo | **Principal** | Asociaciones del sector |
| Sector público o grandes cuentas con pliegos | ✘ | Apoyo | Licitaciones | ✘ |
| Formación in-company y talleres | **Principal** (dueños y RR. HH. de pymes) | **Principal** (RR. HH. de medianas) | Apoyo | Asociaciones, cámaras |

Razón de fondo: Meta compra atención B2B mucho más barata por clic que LinkedIn, pero convierte peor el clic en lead y
no te deja elegir empresa ni cargo; gana cuando el filtro posterior (oferta de entrada, preguntas, llamada) es bueno y
el comprador es identificable por un problema. **[EMPIRICAL]** (Metadata 2026, 153 anunciantes B2B, en
[05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md)) + **[STRONG INFERENCE]**

Lo que dicen los benchmarks y lo que no:

| Dato (B2B, 2025) | Facebook | Instagram | LinkedIn | Fuente y límites |
|---|---|---|---|---|
| CPL | 145 $ | 138 $ | 202 $ (mediana por anunciante 376 $) | Metadata 2026: 153 anunciantes, 57,6 M$, sobre todo SaaS de EE. UU. |
| CPC | 1,95 $ | 2,82 $ | 9,39 $ | Ídem |
| Clic → lead | 2,6 % | 4,0 % | 5,9 % | Ídem |
| Pipeline atribuido por dólar | 3,1× | 1,8× | 10,2× | 90 anunciantes con CRM; atribución, no incrementalidad |

**[EMPIRICAL]** El lead de Meta es más barato, pero en SaaS genera menos pipeline por euro. **No hay benchmark público
con metodología de coste por reunión o por cliente en Meta para servicios a pymes** (búsqueda del 2026-11-09): tu
referencia es tu propio coste por llamada asistida y por proyecto, por anuncio, en el CRM. No traslades CPL de EE. UU.
a España. **[STRONG INFERENCE]**

### 2.2 Señales de que todavía no toca Meta

- No tienes **3 casos** que puedas contar con cifras, permiso y contexto (o una demo potente con datos ficticios). Sin
  prueba, Meta amplifica tu falta de prueba. **[STRONG INFERENCE]**
- No sabes qué procesos vendes ni a qué sector: tu creatividad será genérica y el sistema de recomendación encontrará
  gente genérica ([03/01](../03-creatividad/01-creative-es-targeting.md)).
- Nadie puede responder a un lead en menos de una hora en horario laboral ni hacer 4–8 llamadas de diagnóstico por
  semana.
- La contribución por proyecto no llega a ~1.500 €: el filtrado (llamadas, propuestas) se come el margen
  (sección 3). En ese caso vende un producto más estandarizado o por otro canal. **[STRONG INFERENCE]**
- Tu presupuesto no llega a ~1.000–1.500 €/mes y no lo vas a sostener 3 meses (sección 3.5).

### 2.3 Cómo combinar canales (Meta como cobertura)

1. **Outbound con cobertura.** Quien recibe tu email o mensaje y entra en tu web pasa a una audiencia de visitantes;
   luego ve tu caso o tu demo en Instagram. **[HYPOTHESIS]** sobre el tamaño del efecto: no hay ningún test publicado
   con grupo de control (búsqueda del 2026-11-09). Diseño mínimo: divide la lista de outbound al azar en dos mitades que reciben la misma secuencia;
   solo la mitad A enlaza a una URL propia cuyas visitas entran en la audiencia de cobertura (la de la mitad B queda
   excluida) y compara respuestas y reuniones a 4–6 semanas. Solo mide el efecto sobre quien llegó a visitar.
2. **Listas de prospección como audiencias: con mucho cuidado en la UE.** Subir a Meta los emails de una lista
   comprada o extraída de LinkedIn es un tratamiento de datos personales que necesita base legal y deber de informar
   (RGPD, arts. 6 y 14). Las Directrices 8/2020 del Comité Europeo de Protección de Datos tratan al anunciante y a la
   plataforma como corresponsables del targeting por listas, y en Alemania un tribunal administrativo (Bayreuth, 2018,
   con la ley anterior al RGPD) avaló a la autoridad que declaró ilegal subir listas sin consentimiento.
   **[OFFICIAL — reguladores]** No he encontrado resolución de la AEPD sobre este punto. Usa listas de personas que te
   han dado sus datos (leads, asistentes a talleres, clientes, suscriptores con consentimiento) y, para lo demás,
   audiencias de visitantes, de vídeo y de interacción. **[STRONG INFERENCE]** (no es asesoría legal; confírmalo con quien
   lleve tu protección de datos)
   - **Además, casan mal:** con emails solo de trabajo, las tasas de coincidencia publicadas rondan el 10–20 % (datos
     de vendors, la mayoría de 2014–2019, sin cifras recientes). Una lista de 500 prospectos daría 50–100 personas,
     demasiado pocas para entregar. **[EMPIRICAL]** débil + **[STRONG INFERENCE]**
3. **LinkedIn para el fundador, Meta para amplificar a pymes.** Lo que funciona en orgánico (un post con un caso, un
   vídeo explicando un error) es el mejor candidato a anuncio: `/organico-a-anuncios` lo convierte en concepto y brief.
   **[STRONG INFERENCE]** ([07/07](../07-instagram-placements-mensajeria/07-organico-mas-pagado-post-ids-boost.md))
4. **Referidos y partners** (gestorías, integradores de ERP, asociaciones): cierran mejor que cualquier anuncio. Meta
   les da soporte: retargeting de quien entra por su enlace y casos del mismo sector. **[STRONG INFERENCE]**
5. **Buscador**: si la gente ya busca «automatizar facturas de proveedores», Google captura esa demanda; Meta la crea en
   quien aún no la busca. No son sustitutos. **[STRONG INFERENCE]**

---

## 3. Economía: cuánto puedes pagar en cada etapa

### 3.1 La fórmula y cómo se mapea a la calculadora

```
Coste máximo por etapa X = contribución por proyecto × P(ganar | ha llegado a X)
```

`herramientas/economia.py leadgen` trabaja con cuatro tasas. Para el embudo consultivo, mapea así:

| Parámetro | Etapas §16 | Qué pones |
|---|---|---|
| `--cualif` | `lead` → `cualificado` (pasa por `diagnostico`) | (lead→diagnóstico) × (diagnóstico→cualificado) |
| `--agenda` | `cualificado` → `llamada` | % de cualificados que reservan |
| `--show` | `llamada` → `asistio` | % que se presenta (cancelaciones en el denominador) |
| `--cierre` | `asistio` → `ganado` | (asistió→propuesta) × (propuesta→ganado) |

Los break-even por diagnóstico y por propuesta no salen directos: divide el BE por lead entre lead→diagnóstico, y
multiplica la contribución por propuesta→ganado.

### 3.2 La contribución de una consultora

| Concepto | Cómo se trata | Error habitual |
|---|---|---|
| Precio | Sin IVA en B2B (`--iva 0`): el IVA se recupera | Calcular con el precio con IVA |
| Cobro en hitos (50 % firma, 50 % entrega) | `--pct-pago-unico 0 --cuotas 2 --recargo-cuotas 0 --impago-cuotas <x>` | Suponer que se cobra todo |
| Coste de entrega | Horas del equipo + herramientas + APIs de modelos durante el proyecto (`--entrega-pct`) | Olvidar el coste de las APIs y el soporte post-entrega |
| **Coste de vender** | Horas de llamadas y propuestas por cada proyecto ganado (`--coste-fijo`) | **Ignorarlo**: es lo que hunde a las consultoras que regalan diagnósticos |
| Comisiones | Si hay comercial (`--closer-pct`) | — |
| Mantenimiento recurrente | Contribución extra esperada (fuera de la calculadora: súmalo y usa `prevision --contribucion-venta`) | Contarlo desde el primer día sin datos de retención |

**El coste de vender.** Si cada proyecto ganado exige 1/0,175 ≈ 5,7 llamadas asistidas de 1 h y 1/0,35 ≈ 2,9
propuestas investigadas de 8 h, son ~28 h del fundador; a 50 €/h, ~1.400 € por venta. Si esas horas tienen coste de
oportunidad (podrían ser horas facturables), es un coste real. **[STRONG INFERENCE]** (aritmética; las horas son
supuestos que debes medir)

**Mantenimiento.** Cuenta el recurrente solo cuando tengas al menos 6 meses de datos de retención y tu caja aguante el
periodo de recuperación ([05/05 §8](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md)). Hasta
entonces decide con el proyecto solo y usa el recurrente como colchón. **[STRONG INFERENCE]**

### 3.3 Tabla de control (ejemplo Acme, detalle en la sección 13)

Proyecto medio 9.000 € sin IVA, entrega 45 %, 5 % de impago del segundo pago, coste de vender 1.400 €; tasas iniciales
**[HYPOTHESIS]**: lead→diagnóstico 70 %, diagnóstico→cualificado 50 %, cualificado→llamada 60 %, show 75 %,
asistió→propuesta 50 %, propuesta→ganado 35 %. Margen objetivo 50 % sobre la contribución.

| Etapa | Break-even (solo proyecto) | Target | Break-even con mantenimiento | Target |
|---|---|---|---|---|
| `lead` | 93 € | 47 € | 149 € | 74 € |
| `diagnostico` | 133 € | 67 € | 213 € | 106 € |
| `cualificado` | 266 € | 133 € | 425 € | 213 € |
| `llamada` | 444 € | 222 € | 709 € | 354 € |
| `asistio` | 592 € | 296 € | 945 € | 472 € |
| `propuesta` | 1.184 € | 592 € | 1.889 € | 945 € |
| `ganado` (CAC) | 3.382 € | 1.691 € | 5.398 € | 2.699 € |

```
python3 -I herramientas/economia.py leadgen --precio 9000 --iva 0 --pct-pago-unico 0 --cuotas 2 \
    --recargo-cuotas 0 --impago-cuotas 0.05 --pasarela-pct 0.005 --entrega-pct 0.45 --coste-fijo 1400 \
    --cualif 0.35 --agenda 0.60 --show 0.75 --cierre 0.175 --inversion 3000 --cpl 45
```

Lectura: una consultora que regala propuestas investigadas a todo el que llama tiene un break-even por llamada mucho más
bajo del que cree. Por eso el filtro va **antes** de la propuesta (sección 9.3). **[STRONG INFERENCE]**

### 3.4 Las palancas, ordenadas por lo que valen

El break-even por lead es lineal en cada tasa ([05/05 §6](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md)).
En Acme, subir propuesta→ganado del 35 % al 45 % (+29 % relativo) sube lo que puedes pagar por lead de 93 € a 120 €,
exactamente igual que bajar el CPL un 22 %. La propuesta investigada y el show suelen ser más baratos de mejorar que el
CPL. **[STRONG INFERENCE]**

| Palanca | Dónde actúa | Skill |
|---|---|---|
| Show (plazo de la cita, confirmación, recordatorios) | `llamada` → `asistio` | `/seguimiento-leads` |
| Filtro antes de la llamada | `diagnostico` → `cualificado` | `/iman-de-leads`, `/formulario-instantaneo` |
| Propuesta investigada | `propuesta` → `ganado` | sección 9.3 |
| Velocidad de respuesta | `lead` → `llamada` | `/seguimiento-leads` |
| CPL | `lead` | creatividad y oferta (secciones 4 y 8) |

### 3.5 Presupuestos mínimos realistas

Eventos por semana = presupuesto semanal / coste por evento. Con las tasas de Acme y un CPL de 45 €:

| Presupuesto/mes | Leads/semana | Cualificados/semana | Llamadas asistidas/semana | Proyectos/mes (base) | Qué puedes leer y cada cuánto |
|---|---|---|---|---|---|
| < 1.000 € | < 5 | < 2 | < 1 | < 0,6 | Casi nada: usa Meta como cobertura (retargeting de visitantes, vídeo, casos) y vende por otros canales |
| 1.500 € | 8 | 3 | 1,2 | 0,9 | CPL y coste por diagnóstico, mensualmente; ventas, por trimestre |
| 3.000 € | 15 | 5 | 2,4 | 1,8 | Coste por cualificado cada 2 semanas; coste por llamada asistida, mensual; CAC, trimestral |
| 6.000 € | 31 | 11 | 4,9 | 3,7 (lineal; menos con rendimientos decrecientes) | Test de embudo o de oferta con potencia razonable a 6–8 semanas |
| 12.000 € | 62 | 22 | 9,7 | 7,4 (lineal) | Prueba seria de Conversion Leads; varios ángulos a la vez |

**[STRONG INFERENCE]** (aritmética; las tasas son de ejemplo). Regla práctica: si no puedes sostener al menos
**1.500 €/mes durante 3 meses**, Meta no te dará una lectura útil como canal de captación principal. **[HYPOTHESIS]**
(umbral derivado de la tabla, no de un estudio)

Previsión con rango (para planificar o justificar el presupuesto), con la curva de rendimientos decrecientes de la KB
([13/06 §3](../13-sistema-operativo/06-framework-escalado.md)) y el 3 % de recargo por país en España:

```
python3 -I herramientas/economia.py prevision --modelo servicios --inversion 3000,4500,6000 --inversion-ref 3000 \
    --cpl 38-52 --cualif 0.30-0.40 --agenda 0.5-0.7 --show 0.65-0.85 --cierre 0.13-0.22 \
    --contribucion-venta 3382 --fee-pais 0.03
```

Con 3.000 €/mes salen 1,8 proyectos de base (0,7–4,1 entre el peor y el mejor supuesto) y un **16 % de probabilidad de
cero ventas en un mes** solo por azar. En un trimestre (9.000 €) la base es 5,5 proyectos (3–9 por azar) y la
probabilidad de cero baja al 0,4 %. **Por eso los proyectos se evalúan por trimestre.** **[STRONG INFERENCE]** (Poisson)

### 3.6 El techo de capacidad

Calcula el gasto máximo que tu equipo puede atender antes de mirar el de Meta:

```
Gasto máximo/semana ≈ propuestas que puedes investigar por semana / (lead→propuesta) × CPL
```

Acme: 2 propuestas/semana ÷ (0,35 × 0,6 × 0,75 × 0,5 = 7,9 % de los leads) × 45 € ≈ 1.140 €/semana ≈ **4.950 €/mes**.
Por encima, o contrata, o sube el filtro antes de la llamada, o cobra el diagnóstico. Escalar más rápido que tu
capacidad alarga el plazo de las citas, baja el show y empeora las propuestas. **[STRONG INFERENCE]**
([playbook-high-ticket §9](playbook-high-ticket.md))

---

## 4. Ofertas: la de entrada y la principal

### 4.1 Cinco reglas de una oferta de entrada que precualifica

1. **Da valor aunque nunca te compren.** El dueño sale sabiendo algo de su empresa que no sabía (cuántas horas se van en
   un proceso, dónde está el error, qué podría hacer él solo). **[STRONG INFERENCE]**
2. **Exige un dato que solo aporta quien tiene el problema.** Volúmenes, minutos por tarea, herramientas que usa. El
   curioso abandona; el que tiene el problema lo rellena con gusto. **[STRONG INFERENCE]**
3. **Supuestos explícitos y rango, no una cifra mágica.** Cada número del resultado dice de dónde sale y se puede
   cambiar. **[STRONG INFERENCE]**
4. **Puede decir que no.** «Con estos números no te compensa contratarnos; esto es lo que puedes hacer tú gratis». Es
   honesto, ahorra llamadas inútiles y te diferencia de quien promete milagros. Quien recibe un «no» honesto vuelve
   cuando crece. **[HYPOTHESIS]** sobre el efecto en conversión; **[STRONG INFERENCE]** sobre el filtro.
5. **Lleva a la llamada sin forzarla y te cuesta poco.** El resultado termina en «revisemos tu diagnóstico en 30
   minutos» solo si hay caso; tu coste por diagnóstico completado es casi cero (automático) o acotado (30 min).

### 4.2 Catálogo de ofertas de entrada

| Oferta | Qué recibe el cliente | Qué filtra | Tu coste | Evento | Cuándo usarla | Riesgo |
|---|---|---|---|---|---|---|
| **Diagnóstico de horas manuales** (web, 5–8 min) | Horas/año y coste por proceso, rango de ahorro con supuestos, veredicto (caso claro, dudoso, no compensa) | Tamaño, volumen real, decisor | Casi nulo | `Lead` al enviar los datos de contacto, `DiagnosticoCompletado` al ver el resultado (sección 5.3) | Por defecto para consultoras de automatización | Que el resultado se lea como promesa: rango y supuestos visibles |
| **Calculadora de ahorro de un proceso** (facturas, presupuestos, citas) | Igual que el anterior para un solo proceso | Volumen de ese proceso | Casi nulo | Igual | Cuando vendes 1–2 soluciones muy concretas | Atraer a quien ya está en la fase de «quiero precio» |
| **Auditoría gratuita** (revisas su stack y sus procesos en una llamada o con capturas) | Informe corto con 3 acciones | Poco, si no pones requisitos | Alto (1–3 h) | `Lead` → `cualificado` | Ticket alto (≥15 k€) con pocos leads; con requisitos visibles | Curiosos que coleccionan auditorías: exige tamaño y decisor |
| **Test de madurez** (scorecard de 10–15 preguntas) | Puntuación, comparación y siguiente paso | Débil: lo rellena cualquiera | Casi nulo | `Lead`, `DiagnosticoCompletado` | Volumen alto o como imán de retargeting; formación | Leads de baja intención; no lo uses como única entrada |
| **Piloto acotado de pago** (2–4 semanas, un proceso, criterio de éxito medible) | Un proceso funcionando con sus datos | Muy fuerte: paga | Alto, pero cobrado | `Purchase` (valor del piloto) | Tras la llamada, para quien «ya probó y no funcionó» o duda del equipo | Que el piloto se convierta en el proyecto a precio de piloto: alcance escrito |
| **Taller** (60–90 min, en abierto o in-company) | Método y plantilla para detectar qué automatizar; alfabetización del equipo | Medio: dedica una hora | Medio | Registro → asistencia → `diagnostico` | Cuando el mercado está frío o vendes formación (ver la nota sobre el artículo 4 en la sección 4.4) | Asistencia baja si es gratuito y en abierto ([05/07](../05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md)) |
| **Demo con sus documentos** («mándanos 3 albaranes y te enseñamos el resultado») | Ver su caso funcionando | Fuerte | Medio | `Lead` → `cualificado` | Lectura de documentos, presupuestos | Datos personales en documentos: pide versiones sin datos o firma un encargo de tratamiento antes |

**Lo que se sabe de estos formatos (poco):** los benchmarks de quizzes y calculadoras son de quienes venden la
herramienta y miden captación, no calidad: un 11,3 % de visitante a lead en landings con quiz frente a un 7,9 % de media
de todos los formatos (ConvertFlow, 1.063 embudos, 2026-09) o un ~40 % de quienes empiezan el quiz que dejan sus datos
(Interact, sin muestra declarada). **No hay ningún dato independiente sobre cuántos de esos leads llegan a reunión o
compran en B2B**, ni sobre auditorías gratuitas. **[EMPIRICAL]** débil. Que «lo gratis sin requisitos atrae curiosos»
es una inferencia razonable, no un dato: mídelo con tu % de `diagnostico` → `cualificado` por oferta. Lo que sí apunta
en la misma dirección: más de la mitad de los compradores B2B usarán una prueba (piloto, demo con sus datos) como paso
decisivo (previsión de Forrester para 2026). **[EMPIRICAL]** (analista)

Herramientas: `/iman-de-leads` diseña la oferta y sus preguntas; `/construir-landing` la publica con
`paginas.py generar diagnostico` (o `landing`, `reserva`, `gracias`, `webinar`); `/formulario-instantaneo` si va en un
formulario de Meta.

### 4.3 Cómo construir una calculadora honesta

Estructura mínima (para cada proceso que el usuario elige):

```
Horas/año         = veces por semana × minutos por vez / 60 × semanas laborables (≈ 46)
Coste/año         = horas/año × coste por hora cargado (sueldo + cotizaciones; por defecto editable)
Automatizable     = rango por tipo de tarea (p. ej. copiar datos entre programas: alto; redactar respuestas: medio;
                    decisiones con criterio: bajo), nunca 100 %
Revisión humana   = minutos que siguen haciendo falta por documento o caso (se restan)
Ahorro bruto/año  = (horas automatizables − revisión) × coste por hora
Ahorro neto/año   = ahorro bruto − mantenimiento anual estimado
Payback (meses)   = coste estimado del proyecto / (ahorro neto / 12)
Veredicto         = caso claro (payback ≤ 12 meses) · dudoso (12–18) · no compensa (> 18 o ahorro < umbral)
```

- **Supuestos por defecto conservadores y visibles** (p. ej. 25–60 % automatizable **por tarea**, según su tipo) y un
  rango pesimista–base, nunca un único número. **[HYPOTHESIS]** (rangos por tarea; cámbialos con tus casos medidos)
- **Lo que dice la evidencia sobre el ahorro de tiempo**, para que no prometas de más:

  | Estudio | Qué midió | Resultado | Lectura |
  |---|---|---|---|
  | Humlum y Vestergaard (NBER, 2025): 25.000 trabajadores en Dinamarca con datos administrativos | IA generativa genérica en el trabajo | ~3 % del tiempo ahorrado; sin efecto en salarios ni horas | A nivel de puesto el ahorro es pequeño |
  | Fed de St. Louis (encuesta de nov-2024) | Usuarios de IA generativa | 5,4 % de sus horas (~2,2 h en una semana de 40); 1,4 % sobre todos los trabajadores | Autodeclarado |
  | Brynjolfsson, Li y Raymond (QJE, 2025): 5.172 agentes de atención al cliente | Asistente integrado en el puesto | +15 % de consultas resueltas por hora, más en los menos expertos | Integrado en un proceso concreto, sí se nota |
  | METR (2025): ensayo controlado con 16 desarrolladores expertos | Herramientas de IA en su trabajo | Tardaron un 19 % más y creían haber ido un 20 % más rápido | La percepción sobreestima el ahorro: mide |

  **[EMPIRICAL]** Conclusión: los porcentajes altos solo son defendibles en **tareas concretas, repetitivas y medidas
  antes y después** (pasar los datos de un albarán al programa de gestión), nunca a nivel de puesto ni de empresa; y
  «tiempo ahorrado» no es «coste ahorrado» si esas horas no se reasignan. **[STRONG INFERENCE]**
- **Facturas:** la memoria de impacto del real decreto de factura electrónica cita ahorros de 2,8–5 € por factura
  (estudio privado de 2021-22) y 10 € por factura recibida (cifra tomada de una propuesta europea). Usa el rango bajo
  por defecto y el alto como techo. **[OFFICIAL — regulador]** (cifras que cita, no que mide) + **[HYPOTHESIS]**
  (rango para la calculadora)
- **El umbral de «no compensa»** sale de tu precio mínimo: si tu proyecto más pequeño cuesta 6.000 € y quieres payback
  ≤ 18 meses, un ahorro neto < ~4.000 €/año no es un caso para ti. Dilo en pantalla y ofrece algo útil (plantilla,
  taller, «vuelve cuando el volumen se duplique»). **[STRONG INFERENCE]**
- **Habla de horas recuperadas, no de despidos.** «Sustituye a una persona» asusta al equipo que va a usarlo y es mal
  argumento para el dueño que no quiere despedir. **[STRONG INFERENCE]**
- **Lo que devuelves a Meta no es el ahorro.** `DiagnosticoCompletado` puede llevar `value` = valor esperado del lead
  (contribución × P(ganar | diagnóstico), p. ej. 133 € de media en Acme, más si el veredicto es «caso claro»), nunca el
  ahorro bruto del cliente (contrato §16). Con el volumen de una consultora pequeña no optimizarás por valor (hacen
  falta ~100 conversiones en 14 días y ≥5 valores distintos), pero el valor te sirve para medir.
  **[OFFICIAL META]** (requisitos, [05/03 §5](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md))
  + **[HYPOTHESIS]** (valores)
- **El diagnóstico alimenta la propuesta y la creatividad.** Los datos agregados y anónimos («en 40 diagnósticos de
  distribuidoras, la tarea que más horas come es…») son ángulos y prueba. **[STRONG INFERENCE]**

### 4.4 La oferta principal

| Forma | Cuándo | Cómo se presenta | Riesgo |
|---|---|---|---|
| **Proyecto a precio cerrado** | Alcance claro tras el diagnóstico | Fases, entregables, criterios de aceptación, precio y plazo; 50/50 o 40/40/20 | Alcance que crece: lista de lo que **no** incluye |
| **Piloto pagado deducible** | Duda sobre la adopción o mala experiencia previa | 2–4 semanas, un proceso, criterio de éxito medible; si sigue, se descuenta del proyecto | Piloto infinito: fecha y decisión escritas |
| **Mantenimiento** | Todo lo que toca APIs y modelos que cambian | Cuota mensual con horas, monitorización, cambios menores y coste de APIs explicado | Venderlo como seguro vacío: informe mensual de uso y errores |
| **Formación in-company** | Equipos que ya usan IA sin criterio o antes de un proyecto | Sesiones con casos de su empresa, normas de uso y plantilla | Que sea un curso genérico: casos suyos |
| **Bolsa de horas** | Clientes con mantenimiento que piden cambios | Precio por bloque | Que se convierta en tu modelo principal |

Garantías honestas: de cumplimiento (lo que se entrega, plazos, correcciones hasta que funcione según los criterios
escritos), no de resultados de negocio que no controlas. **[STRONG INFERENCE]**
([08/11](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md))

**Formación y el artículo 4 del Reglamento europeo de IA.** El artículo 4 (alfabetización en IA) se aplica desde el
2025-02-02, pero el Ómnibus Digital de IA (Reglamento (UE) 2026/1744, en vigor desde el 2026-07-27) lo suavizó: ahora
proveedores y empresas que usan sistemas de IA deben **adoptar medidas para apoyar** la alfabetización de su personal,
sin garantizar un nivel concreto, y el artículo no tiene multa propia. **[OFFICIAL — regulador]** Es un buen motivo para
ordenar el uso de la IA en un equipo; no lo vendas como «obligatorio, o te multan»: es falso y es justo el miedo que tu
voz anti-hype debe evitar. **[STRONG INFERENCE]**

**Ayudas públicas (estado a 2026-11-09).** Muchas pymes preguntan si pueden pagarte con un programa público:

| Programa | Estado | Qué puedes decir en un anuncio |
|---|---|---|
| Kit Digital | Convocatorias finalizadas (Acelera Pyme); la Orden TDF/39/2026 mantiene las bases y permite convocatorias nuevas, pero no abre plazo | Nada que lo presente como disponible |
| Kit Consulting (incluía «Asesoramiento en IA», hasta 6.000 € por categoría) | Convocatoria finalizada; la Orden TDF/38/2026 tampoco abre plazo | Ídem |
| Bono IA (Plan IA360, presentado el 2026-09-21: 600 M€, pagos por hitos, diagnóstico de madurez previo) | Anunciado, **sin bases ni convocatoria**; piloto previsto para el primer semestre de 2027, calendario incierto tras la disolución de las Cortes | Como mucho, «te ayudamos a preparar el diagnóstico de madurez si se abre», revisado por `revisor-politicas` |

**[OFFICIAL — regulador]** (BOE, Acelera Pyme, sede de Red.es y el PDF del plan). Un anuncio tipo «consigue tu Kit
Digital» hoy sería publicidad engañosa, y usar los logos oficiales sin estar adherido sugiere una relación con la
Administración que no existe; cuando un programa está abierto, los agentes adheridos tienen además obligaciones de
comunicación propias (mención de la financiación europea, manual de identidad). **[STRONG INFERENCE]** (no es asesoría
legal) Comprueba el estado el mismo día que escribas el anuncio.

`/oferta` aplica estos criterios a tu caso y deja la oferta en la ficha.

---

## 5. Embudos según volumen y presupuesto

### 5.1 Los cinco embudos

| Embudo | Cuándo | Evento inicial | Ventajas | Riesgos |
|---|---|---|---|---|
| **A. Formulario instantáneo de alta intención con calendario** | Poco presupuesto, audiencia móvil, oferta fácil de entender («diagnóstico de 30 min con tus números») | `Lead` (formulario) | CPL bajo, aprendizaje rápido, reserva en el pico de interés | Poco contexto; la reserva no se reporta en Ads Manager; exige respuesta en minutos |
| **B. Landing con diagnóstico** | Por defecto si puedes construirla; tu oferta de entrada es el diagnóstico | `Lead` al enviar los datos de contacto, `DiagnosticoCompletado` al ver el resultado | Filtra con datos, controla la señal, te da los números de la propuesta | CPL más alto; depende del tracking web y del consentimiento |
| **C. VSL y llamada** | Tickets altos (≥15 k€), soluciones difíciles de explicar | `Lead` (aplicación) o `Schedule` si hay volumen | La VSL vende antes de la llamada | Producción; CPL alto; tracking web |
| **D. Webinar o taller** | Mercado frío, formación, o volumen alto que quieres educar | Registro → asistencia → diagnóstico | Escala y educa | Asistencia; el algoritmo optimiza registros si no le devuelves la asistencia |
| **E. Mensajería (WhatsApp, Instagram Direct, Messenger)** | Retargeting, LatAm, públicos que no rellenan formularios | Conversación | Intención y velocidad si respondes | En Europa, optimizar click-to-WhatsApp a leads no está disponible o está limitado (sección 5.6) |

Elige por tu cuello de botella y por la señal que Meta puede aprender, no por el CPL
([05/01](../05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md)). Ruta recomendada:

| Presupuesto/mes | Embudo principal | Segundo embudo |
|---|---|---|
| 1.000–3.000 € | A o B (uno) | Ninguno: concentra |
| 3.000–8.000 € | B (o A si no puedes construir la landing) | El otro como test controlado a 4–6 semanas; anuncios por etapa con el 5–10 % |
| 8.000–20.000 € | B + A | D mensual (taller) o C si el ticket lo pide |
| > 20.000 € | Por línea de servicio con economía distinta | D y E con medición |

**[STRONG INFERENCE]** (los cortes son orientativos).

### 5.2 Embudo A: formulario instantáneo de alta intención

`/formulario-instantaneo` lo deja creado y sin usar hasta que un anuncio lo enlace (`formularios_meta.py crear
--simular` primero y después con confirmación), o listo para montarlo en Ads Manager con `formularios_meta.py guia`.
Un formulario no tiene estado de pausa: lo que se crea en pausa es el anuncio que lo usa.
Configuración base ([05/02](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md)):

- **Tipo:** *Higher intent* (contexto bajo los campos de contacto y pantalla de revisión). Solo se entrega en el feed de
  Facebook e Instagram en móvil, no en ordenador. **[OFFICIAL META]**
- **Intro (la tarjeta de contexto, el filtro más barato):** «Diagnóstico de 30 minutos por videollamada para ver qué
  tareas repetitivas de tu empresa se pueden automatizar y si te compensa. Lo hacemos con tus números. Si no hay caso,
  te lo decimos. No es para empresas de menos de 5 personas.»
- **Preguntas (4–5, de opción múltiple):**

| # | Pregunta | Opciones | Para qué |
|---|---|---|---|
| 1 | ¿Cuántas personas trabajan en tu empresa? | 1–4 · 5–20 · 21–100 · más de 100 | Tamaño; 1–4 → final de «no es para ti» con un recurso (lógica condicional) |
| 2 | ¿Qué proceso os quita más horas? | Facturas y albaranes · Presupuestos y su seguimiento · Responder siempre lo mismo · Citas y recordatorios · Informes · Otro | Ángulo y preparación de la llamada |
| 3 | ¿Con qué lo hacéis hoy? | Programa de gestión o ERP · Hojas de cálculo · CRM · Correo y papel · No lo sé | Complejidad |
| 4 | ¿Cuándo querrías tenerlo resuelto? | Este trimestre · Este año · Solo estoy mirando | Urgencia (la KB la trata como predictor fuerte de cierre) |
| 5 | ¿Decides tú esta inversión? | Sí · La decido con otra persona · No | Autoridad |
| 6 (opcional) | «Los proyectos como este cuestan entre 6.000 y 15.000 €. ¿Encaja en vuestro presupuesto?» | Sí · Necesitaríamos hacerlo por fases · No | Filtra por precio sin pedir datos financieros; es tu voz anti-hype en el formulario |

- **No preguntes** datos financieros personales (prohibido) ni la facturación de la empresa (zona gris); el tamaño en
  empleados filtra igual y la pregunta 6 habla de tu oferta, no de sus ingresos. **[OFFICIAL META]** + **[HYPOTHESIS]**
  (interpretación del revisor) ([05/02 §4](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md))
- **Email de trabajo obligatorio:** según el anuncio de Meta del 2025-10-30, solo está disponible en Instagram o por la
  Marketing API **[OFFICIAL META]**. Úsalo solo si tu cliente ideal tiene más de ~20 personas: muchas pymes pequeñas
  usan correos personales y perderías leads buenos. **[STRONG INFERENCE]**
- **Verificación del teléfono:** actívala si aparecen teléfonos falsos o bots. El código llega por WhatsApp o SMS (Meta
  elige el canal), quien no verifica no cuenta como lead y un fijo no puede verificar. **[OFFICIAL META]**
- **Final:** *Book time* con el enlace directo de tu calendario (Calendly o LeadConnector/HighLevel; solo enlaces
  directos del partner, no URLs propias), o «Chat on WhatsApp» si tu equipo trabaja ahí. Lo que debes saber
  **[OFFICIAL META]** (Help Center, leído el 2026-11-09):
  - el calendario embebido **solo funciona en la app de Facebook para móvil**; en Instagram, el botón abre un navegador
    dentro de la app;
  - **las reservas no se reportan en Ads Manager**: devuélvelas por la CAPI como `Schedule` desde GHL (una sola
    fuente, sección 5.7);
  - la página menciona HubSpot de forma incoherente y no confirma la disponibilidad global anunciada por la prensa:
    compruébalo en tu cuenta.
- **Parámetros de seguimiento** (oferta, ángulo, versión del formulario) y el Lead ID guardado en el contacto
  ([05/09 §3](../05-leadgen-high-ticket-crm/09-sales-feedback-loop.md)).
- **Sincroniza o descarga los leads cada día:** Meta solo los guarda 90 días y no deja descargar nada anterior.
  `formularios_meta.py leads` los guarda en `privado/`. **[OFFICIAL META]**
- **Respuestas preferidas** (marcar en una pregunta qué respuestas prefieres) y el **agente de IA dentro del
  formulario** están en prueba sin documentación oficial (practitioner, 2026-07 y 2026-08): no los des por disponibles.
  **[EMPIRICAL — practitioner]**

### 5.3 Embudo B: landing con diagnóstico

`/construir-landing` genera la página con `paginas.py generar diagnostico --config <json> --salida <dir>` (estática,
rápida en el navegador interno de Instagram y Facebook, consentimiento antes del píxel, UTMs, `fbclid` y `event_id`
compartido con el webhook, contrato §17) y `paginas.py validar` la comprueba. Estructura:

1. **Arriba:** «¿Cuántas horas se van en [proceso] en tu empresa? Calcúlalo en 6 minutos y te decimos si compensa
   automatizarlo. También si no compensa.» Botón al diagnóstico. El mismo proceso y la misma imagen que el anuncio
   (*message match*, [03/09](../03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md)).
2. **Cómo funciona** en 3 pasos, qué recibes (informe con supuestos), quién lo hace (el fundador, con cara y nombre) y
   para quién **no** es.
3. **Prueba:** 2–3 casos con cifras verificables y una demo de 60–90 s.
4. **Objeciones** en preguntas frecuentes (ChatGPT, datos, equipo, precio con rangos).
5. **El diagnóstico:** primero las preguntas (sector, tamaño, procesos y volúmenes), después los datos de contacto y
   el resultado con veredicto: empezar por lo fácil y pedir el contacto al final
   ([03/15 §4.2](../03-creatividad/15-landing-pages-y-cro-trafico-meta.md)). **`Lead` es siempre el momento en que la
   persona envía sus datos de contacto** (contrato §16). `paginas.py` lo configura con `captura`
   (`plantillas/paginas/README.md`):
   - `captura: antes` (por defecto): preguntas → datos de contacto → resultado. Al enviar los datos salen a la vez
     `Lead` y `DiagnosticoCompletado` (con el `valor_evento` del nivel).
   - `captura: despues`: preguntas → resultado → datos para reservar. `DiagnosticoCompletado` sale al ver el resultado
     y `Lead` al enviar los datos.
   - Si construyes un diagnóstico que pide el contacto en el primer paso (`paginas.py` no tiene esa variante), `Lead` va
     en ese primer paso y `DiagnosticoCompletado` al ver el resultado.

   Calendario solo para «caso claro» y «dudoso» con tamaño suficiente; «no compensa» → recurso útil y suscripción
   opcional con consentimiento. **[STRONG INFERENCE]** (el orden; Meta no publica una recomendación)
6. **Página de gracias** (`paginas.py generar gracias`): vídeo de 60 s «qué pasará en la llamada», qué preparar y botón
   para añadir al calendario ([05/08 §3.3](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md)).

Audiencia de retargeting que sale gratis, según la variante: con `captura: despues`, quien disparó
`DiagnosticoCompletado` y no `Lead` (vio su resultado y no dejó sus datos); con `captura: antes`, quien visitó la página
del diagnóstico y no disparó `Lead` (empezó y no terminó); con el contacto en el primer paso, quien disparó `Lead` y no
`DiagnosticoCompletado`.

### 5.4 Embudo C: VSL y llamada

Para tickets de 15.000 € o más o soluciones que necesitan 10 minutos de explicación. VSL de 6–12 minutos del
fundador: el problema en su proceso, los tres tipos de proyecto que haces, cuánto cuestan (rangos), cómo es un proyecto
semana a semana, para quién no es, un caso. Después, una aplicación corta y calendario solo para cualificados
([05/06](../05-leadgen-high-ticket-crm/06-high-ticket-funnels.md)). Evento: `Lead` (aplicación); `Schedule` solo si
llegas a volumen. **[STRONG INFERENCE]**

### 5.5 Embudo D: webinar o taller

Taller práctico de 60 minutos («cómo detectar qué se puede automatizar en tu empresa, con plantilla») en abierto
mensual, o in-company como producto de pago. `/webinar` monta registro, recordatorios, asistencia y oferta. Quien pide
diagnóstico al final pasa a `diagnostico` o `cualificado`. Devuelve la asistencia a Meta: si no, optimizarás a
registrantes que no aparecen ([playbook-webinars](playbook-webinars-eventos-lanzamientos.md)).

Asistencia sobre registrados en B2B: ~60 % en el informe de ON24 con datos de 2025 (grandes empresas, directo +
diferido; leído en fuente secundaria), 47,7 % en el de Livestorm de 2026 y en torno al 20–33 % en organizadores pequeños
según otras plataformas (cifras no verificadas en la fuente). **[EMPIRICAL]** débil. Con tráfico frío de Meta y un taller
gratuito, planifica con un 25–35 % y mide el tuyo. **[HYPOTHESIS]** De asistente a reunión no hay ningún benchmark
fiable: es tu métrica a medir.

### 5.6 Embudo E: mensajería

- **España y la UE:** el Help Center avisa de que ciertas métricas, campañas y funciones de mensajería no están
  disponibles para anuncios entregados a o desde Europa; con objetivo Leads y destino WhatsApp, la opción por defecto es
  maximizar conversaciones, y la optimización a leads por mensajería se introduce de forma gradual (donde existe, pide
  ≥ 10 leads o compras en 30 días). **[OFFICIAL META]** (aviso genérico, leído el 2026-11-09) La KB lo da como no
  disponible para leads en la UE, Reino Unido, Japón y Corea del Sur según una página de WhatsApp Business
  ([07/11](../07-instagram-placements-mensajeria/11-whatsapp-ads-ctwa.md)); el Help Center no lo dice con esas palabras,
  así que compruébalo en Ads Manager con tu cuenta antes de planificar. En la práctica: úsalo para
  retargeting (quien ya vio tu caso o empezó el diagnóstico) o como final del formulario, y mide conversación → lead →
  llamada en el CRM. Para devolver a Meta qué conversaciones fueron lead, cualificado o venta (`LeadSubmitted`,
  `QualifiedLead`, `Purchase`), `capi.py construir --canal` y la [guía de mensajería](../../docs/guias/mensajeria.md).
- **LatAm:** sí puedes optimizar a leads en click-to-WhatsApp, con mejoras declaradas por Meta frente a optimizar a
  conversaciones. **[OFFICIAL META]** ([11/10](../11-benchmarks-casos-expertos/10-espana-latam.md))
- **Instagram Direct:** sirve para marca personal del fundador; no se puede optimizar por eventos posteriores vía la CAPI
  de mensajería. **[OFFICIAL META]** ([05/01 §2.4](../05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md))
- Si automatizas la respuesta con un agente (lo que vendes), di que es un asistente automático y deriva a una persona
  cuando el lead lo pida. Desde el 2026-08-02 el artículo 50.1 del Reglamento de IA obliga al **proveedor** de un
  sistema que conversa con personas a informar de que es una IA (salvo que sea evidente). **[OFFICIAL — regulador]**
  Ojo con quién es el proveedor: una pyme que pone en servicio con su marca el asistente que le has construido puede
  serlo ella, no tú (art. 3.3); déjalo resuelto en el contrato de cada proyecto. **[STRONG INFERENCE]** (no es asesoría
  legal)
- Meta también ofrece su propio agente de mensajería para negocios (Business AI), ampliado en 2026 a negocios de todos
  los tamaños y anunciado como de pago; la página oficial no menciona lead ads ni la UE. **[OFFICIAL META]** Para un
  cliente es una alternativa que debes conocer y comparar con honestidad
  ([07/13](../07-instagram-placements-mensajeria/13-business-ai-agentes-mensajeria.md)).

### 5.7 Las etapas del §16 en GHL

El pipeline de GHL usa las etapas del §16 en ese orden (los nombres visibles pueden traducirse; el evento enviado es el
de la tabla). Paso a paso técnico: [`docs/guias/ghl-meta.md`](../../docs/guias/ghl-meta.md) y
[`docs/guias/capi.md`](../../docs/guias/capi.md); `/implementar-capi` y `especialista-crm` lo montan contigo.

| Etapa | Quién la marca | Cuándo | Evento | Origen | Para qué sirve |
|---|---|---|---|---|---|
| `lead` | El formulario | Al enviar | `Lead` | Web: navegador + servidor con el mismo `event_id`. Formulario instantáneo: lo cuenta Meta y GHL manda la primera etapa por la CAPI de CRM | Optimizar al principio; cobertura de la CAPI de CRM |
| `diagnostico` | La herramienta | Al terminar | `DiagnosticoCompletado` | Navegador + servidor, mismo `event_id` | Optimizar en web con poco volumen; audiencias |
| `cualificado` | Regla escrita + revisión humana (tamaño, volumen, decisor, plazo) | ≤ 48 h | `LeadCualificado` | Servidor (workflow de GHL) | Candidato a Conversion Leads; audiencias |
| `llamada` | El calendario | Al reservar | `Schedule` | **Una sola fuente**, o las dos con `event_id` común (si no, se duplica) | Medir; optimizar en web con volumen |
| `asistio` | Quien hace la llamada | El mismo día | `LlamadaAsistida` | Servidor | Decidir embudos y ángulos |
| `propuesta` | Quien la envía | Al enviarla | `PropuestaEnviada` | Servidor | Anuncios por etapa; pipeline |
| `ganado` | Al firmar | — | `Purchase` con `value` (importe del proyecto) y `currency` | Servidor (en GHL, la etapa se llama «Purchase») | CAC, valor, futuro |
| `perdido` | Quien descarta | — | — | — | Motivo obligatorio de una lista cerrada; audiencias y exclusiones |

Reglas que más se rompen: workflow sin «Allow Multiple» (solo llega la primera etapa), `Schedule` duplicado entre la
página de gracias y GHL, moneda vacía en `Purchase` (GHL pone USD), definiciones de etapa que cambian según quién marca
y cambiar de dataset de CRM a mitad (reinicia el aprendizaje). **[EMPIRICAL]** + **[OFFICIAL META]**
([`docs/guias/ghl-meta.md`](../../docs/guias/ghl-meta.md) §4 y §5)

**Definición de `cualificado` (escríbela en la ficha y no la cambies con campañas activas):** por ejemplo «5–100
personas, un proceso con ≥ 5 h/semana, decide o codecide, quiere resolverlo este año y ha respondido al primer
contacto». No marques `cualificado` solo por las respuestas del formulario: eso Meta ya lo ve; el valor está en lo que
pasa después. **[STRONG INFERENCE]** ([05/03 §4](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md))

**Motivos de pérdida** (lista cerrada): no contesta · datos falsos · no es decisor · tamaño o volumen insuficiente ·
no compensa (diagnóstico) · lo hará con ChatGPT o internamente · precio · eligió a otro · mal momento · no se presentó
sin reprogramar · desconfianza o privacidad. Cada motivo tiene dueño (creatividad, oferta, seguimiento, propuesta).

---

## 6. Qué evento optimizar y cuándo pasar a Conversion Leads

### 6.1 Decisión por volumen semanal

Regla de la KB: la etapa más profunda que ocurra en ≤28 días, convierta entre el 1 % y el 40 % de los leads y tenga
~50 eventos por semana; con 20–50, consolida o sube una etapa; con menos de 20, optimiza a la anterior y usa la
profunda solo para medir ([05/03](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md), «Implicaciones
operativas»). Para una consultora:

| Volumen semanal (lo que de verdad tienes) | Optimiza a | Mide con | Siguiente paso |
|---|---|---|---|
| < 8 leads | `Lead` (embudo A) aceptando *learning limited*; o Meta solo como cobertura | Coste por diagnóstico y por cualificado, mensual | Sube presupuesto, baja fricción o cambia de canal |
| 8–20 leads, < 10 diagnósticos | `Lead` | Coste por diagnóstico y por cualificado | Si ≥ 8–10 diagnósticos/semana, prueba `DiagnosticoCompletado` |
| ≥ 8–10 `DiagnosticoCompletado` (web) | `DiagnosticoCompletado` (conversión personalizada) | Coste por cualificado y por llamada asistida | Si `cualificado` ≥ 15–20/semana sostenido, prepara Conversion Leads |
| ≥ 15–20 cualificados | Prueba Conversion Leads a `cualificado` frente a la campaña actual | Coste por llamada asistida y por propuesta | Si gana en 4–6 semanas, pasa a principal |
| ≥ 30–50 llamadas o cualificados | Conversion Leads a `llamada` o `cualificado`; en web, `Schedule` o eventos en secuencia si los tienes | Coste por propuesta y CAC | Etapa más profunda cuando el volumen lo permita |

**[STRONG INFERENCE]** (los 8–10 eventos por semana como mínimo útil para presupuestos pequeños vienen de
[13/09](../13-sistema-operativo/09-presupuesto-pequeno-y-grande.md) §A.2; los 15–20 para probar Conversion Leads son
**[HYPOTHESIS]**). La venta (`ganado`) casi nunca es optimizable: pocos eventos y, a menudo, fuera de los 28 días.

`LPV` o clics «para que aprenda» no: atraen a quien hace la acción barata. Si no llegas a ningún evento útil, el problema
es de presupuesto, oferta o canal, no de evento. **[CONTESTED]** frente a la recomendación de Meta de usar LPV como
alternativa ([00-ESTADO-ACTUAL-2026 §6](../00-ESTADO-ACTUAL-2026.md)).

### 6.2 Conversion Leads: requisitos verificados

Revisados en el Help Center y en la documentación de developers el 2026-11-09. Base de la KB:
[05/03 §3](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md).

| Requisito | Qué dice Meta | Estado |
|---|---|---|
| Integración por Conversions API | Desde abril de 2026, sin CAPI no puedes crear campañas nuevas con este objetivo; las existentes están afectadas desde agosto de 2026 | **[OFFICIAL META]** |
| Origen de los leads | Help Center: formularios instantáneos **y** formularios web (un 21 % menos de coste por lead de calidad con formulario + CAPI de CRM y un 9,5 % menos con formularios web, cifras de Meta). Developers (actualizado el 2026-10-27): solo formularios instantáneos | **[CONTESTED]** entre dos páginas oficiales: manda lo que te deje elegir Ads Manager |
| Identificador | Guardar en el CRM el lead ID de Meta (15–17 dígitos); si falta, clic ID, teléfono o email | **[OFFICIAL META]** |
| Frecuencia | Subir datos al menos una vez al día; durante el aprendizaje, un evento por cada cambio de estado del lead | **[OFFICIAL META]** |
| Etapa objetivo | Ocurre en ≤ 28 días desde el lead y la alcanza entre el 1 % y el 40 % de los leads | **[OFFICIAL META]** |
| Qué etapas enviar | Todas, a medida que cambian, incluida la del lead inicial (especificación del payload) | **[OFFICIAL META]** |
| Cobertura ≥ 60 % de los leads y ≥ 2 etapas (mejor 3) | La KB las cita de la guía de Meta para partners; no aparecen en las páginas leídas el 2026-11-09 | Trátalo como requisito práctico: sin cobertura, el modelo no aprende |
| Volumen mínimo | El anuncio del 2025-10-30 eliminó el mínimo mensual; la guía de developers, actualizada el 2026-10-27, sigue pidiendo 200 leads al mes (GHL cita 250) | **[CONTESTED]**: la KB da prioridad al anuncio, pero con pocos eventos el sistema aprende mal igualmente |
| Tiempo | 2–4 semanas de aprendizaje; 3–4 semanas hasta ver valor | **[OFFICIAL META]** |
| Optimizar por valor en leads | ≥ 5 valores distintos, más de 100 conversiones en 14 días y 3 semanas de prueba | **[OFFICIAL META]** |
| Eventos en secuencia (*Sequenced Events*) | En Leads con ubicación web y *Maximize number of qualified leads*: eliges dos eventos (p. ej. `Lead` y luego `Schedule`) y solo cuenta si ocurren los dos y en orden; umbral estimado ~30 eventos en 7 días; solo atribución estándar | **[EMPIRICAL — practitioner]**: sin documentación oficial a 2026-11-09 |

**Lo que significa para una consultora:**

1. **Monta la CAPI de CRM desde el día 1** aunque no vayas a usar Conversion Leads: te da el informe por etapa, las
   audiencias de etapa y la opción de pasar cuando el volumen llegue. Coste: un workflow de GHL
   ([`docs/guias/ghl-meta.md`](../../docs/guias/ghl-meta.md) §4).
2. **Elige la etapa por la regla del 1–40 % y por volumen.** En Acme, `cualificado` es el 35 % de los leads (válido) y
   `llamada` el 21 % (válido); `asistio` (15,8 %) y `propuesta` (7,9 %) también están dentro del rango, pero sin
   volumen. `contactado` no sirve: lo alcanza casi todo el mundo.
3. **No lo actives con 5 cualificados por semana** aunque el sistema te deje: el aprendizaje durará más de lo que
   aguanta tu presupuesto. Con 15–20 por semana sostenidos, prueba; con ≥ 50, es la opción por defecto.
   **[HYPOTHESIS]** (15–20) + **[STRONG INFERENCE]** (≥ 50, regla de la KB)
4. **Etiqueta las audiencias de etapa** (`QUALIFIED_LEADS`, `DISQUALIFIED_LEADS`, `HIGH_VALUE_CUSTOMERS`): Meta las
   admite en reglas de valor y te servirán cuando tengas volumen. **[OFFICIAL META]**
   ([09/02](../09-bidding-escalado-economia-analitica/02-value-optimization-y-value-rules.md))

### 6.3 Cómo cambiar de evento sin romper nada

1. **No edites la campaña que funciona:** crea la nueva en pausa (`/lanzar-campana` o `/ejecutar-cambio`) con los
   mismos anuncios (mismo ID de publicación para conservar la prueba social) y repártete el presupuesto o haz un A/B de
   Meta si el volumen lo permite ([09/13](../09-bidding-escalado-economia-analitica/13-experimentacion-ab-tests.md)).
2. **Mínimo 2–4 semanas** sin tocar la etapa objetivo: el aprendizaje de Conversion Leads tarda.
   **[OFFICIAL META]** ([05/03 §3](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md))
3. **Compara por coste por llamada asistida y por propuesta de la cohorte**, no por CPL: Meta advierte que con
   Conversion Leads el CPL puede subir mientras baja el coste por lead de calidad. **[OFFICIAL META]**
4. Anota el cambio en el `change-log.md` con fecha de evaluación; `estado.py` te lo recordará.

---

## 7. Estructura de cuenta y presupuesto con poco volumen

### 7.1 La estructura por defecto

```
ES_LEADS_ADQ_HV                       (campaña Leads, presupuesto de campaña, Advantage+)
└── BROAD-A+_LEAD  o  BROAD-A+_DIAGNOSTICO     (un conjunto; el evento según la sección 6)
    ├── 3–8 anuncios de 2–4 conceptos distintos (fundador, demo, caso, objeción)
    └── formulario Higher intent (embudo A) o la landing del diagnóstico (embudo B)
```

Nomenclatura: `herramientas/nomenclatura.py` y [13/10 §8](../13-sistema-operativo/10-plantillas.md).

- **Controles** (límites duros): ubicación (país o países donde vendes), idioma si hace falta, exclusión de clientes y
  de leads de los últimos 60–90 días. **Sugerencias** (pistas): tu lista de clientes, visitantes de la web, quien ha
  visto tus vídeos. No añadas intereses de «inteligencia artificial» o «emprendimiento»: traen curiosos del tema, no
  compradores del proceso. **[OFFICIAL META]** (controles y sugerencias, [02/07](../02-estructura-campanas/07-audiencias-2026.md))
  + **[STRONG INFERENCE]**
- **Advantage+ placements.** Antes de excluir algo a nivel de cuenta, mira el desglose por ubicación de leads →
  cualificados → llamadas a 30 días (no de CPL). **[OFFICIAL META]** + **[EMPIRICAL]**
  ([05/02 §7](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md))
- **Sin campaña de retargeting separada** por defecto: Advantage+ ya dedica una parte del gasto a gente que te conoce.
  La excepción es la sección 9.5 (anuncios por etapa), con presupuesto pequeño y mensaje distinto.
  **[EMPIRICAL]** ([02/09](../02-estructura-campanas/09-retargeting-duplicacion-exclusiones.md))
- **Un conjunto por sector, no.** El mismo comprador (dueño de pyme) en dos sectores no necesita dos conjuntos: necesita
  anuncios que hablen de cada sector. El anuncio segmenta ([03/01](../03-creatividad/01-creative-es-targeting.md)).
  Separa solo por economía distinta (otro país, otra línea de servicio con otro ticket) o por una restricción.
  **[STRONG INFERENCE]**
- **Mejoras automáticas de Advantage+ creative apagadas** (`mejoras_automaticas: off` en la ficha): la reescritura de
  texto con IA puede inventarse cifras de ahorro que no puedes defender. `meta_ads.py` las desactiva y lo verifica.
  **[OFFICIAL META]** + **[EMPIRICAL]** ([00-ESTADO-ACTUAL-2026 §0](../00-ESTADO-ACTUAL-2026.md))

### 7.2 Presupuesto y ritmo

- **Presupuesto diario estable** durante el primer mes; cambios espaciados ≥ 7 días y con fecha de evaluación. La
  «regla del 20 %» no es una ley: es un ritmo prudente ([12/01](../12-mitos-contradicciones/01-mitos-meta-ads-2026.md)).
- **Horario:** si nadie responde de noche, valora programar los anuncios en horario laboral (requiere presupuesto
  total) o automatizar la primera respuesta 24/7 (es tu oficio: demuéstralo). Compara la calidad de los leads nocturnos
  en el CRM antes de decidir. **[OFFICIAL META]** + **[HYPOTHESIS]**
  ([05/08 §1.4](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md))
- **Topes** en la ficha (`topes.cambio_dia`, `topes.total_dia`) y **reglas de protección** con `/reglas-automaticas`
  (pausar si se gasta X sin un solo lead en un día, avisar si el CPL se dispara): protegen de roturas, no optimizan.
  **[STRONG INFERENCE]** ([10/07](../10-cambios-2025-2026-api-ia-automatizacion/07-reglas-automaticas.md))
- **Recargo por país:** en España, +3 % fuera del importe gastado. Súmalo al comparar con el break-even.
  **[OFFICIAL META]**
- **Novedades de octubre–noviembre de 2026 que tocan a este nicho** ([00-ESTADO](../00-ESTADO-ACTUAL-2026.md) §2, §6 y §8):
  - *Measure conversions on customer devices* viene activado por defecto desde el 2026-11-12, pero **no aplica a
    personas en la UE ni el Reino Unido**: con público español no cambia tus cifras; si llevas cuentas de LatAm, marca
    la fecha en los informes antes de comparar. **[OFFICIAL META]**
  - **Audiencia por creativo** (edad y género por pieza dentro del conjunto): en B2B casi nunca aporta, porque tu filtro
    es el cargo y el tamaño de empresa, no la edad, y no sirve para testear creatividades. Déjala apagada salvo razón
    concreta. **[STRONG INFERENCE]**
  - **Expansión de dispositivos** de la API v27 (conjuntos de Ventas que segmentan por dispositivo): no te afecta si
    optimizas a leads; si algún día segmentas por dispositivo en Ventas, desactívala de forma explícita.
    **[OFFICIAL META]**

### 7.3 Testing creativo con poco volumen

- **Lotes de 2–4 conceptos cada 2 semanas** dentro del mismo conjunto; la herramienta nativa de testing solo si el
  presupuesto permite ≥ 2–3× el coste objetivo por variante ([13/05](../13-sistema-operativo/05-framework-testing-creativo.md)).
- **Métrica de test:** coste por diagnóstico o por lead con un control de calidad (% que pasa a `cualificado`). Un
  anuncio con CPL bajo y 0 cualificados tras 10 leads no es un ganador. **[STRONG INFERENCE]**
- **Regla de corte:** 0 diagnósticos tras 2–3× el coste objetivo por diagnóstico; nunca a 1×. Para cualificados, el
  mismo criterio con su target. **[STRONG INFERENCE]** (Poisson, [13/05](../13-sistema-operativo/05-framework-testing-creativo.md))
- **Folklore que no aplicamos:** frecuencia > 3 = fatiga (Meta mide fatiga por coste frente a su histórico), «necesitas
  50 creativos», «píxel nuevo para empezar de cero», retargeting obligatorio
  ([12/01](../12-mitos-contradicciones/01-mitos-meta-ads-2026.md)).

---

## 8. Creatividad para venta consultiva

### 8.1 Principios

1. **El proceso del cliente, en sus palabras, no tu tecnología.** «Los albaranes que alguien teclea cada lunes» encuentra
   a la persona correcta; «agentes de IA con RAG» encuentra a otros consultores. **[STRONG INFERENCE]**
   ([03/01](../03-creatividad/01-creative-es-targeting.md))
2. **Prueba antes que promesa:** casos con contexto, demos reales, cifras que puedes enseñar. **[STRONG INFERENCE]**
3. **El anuncio filtra:** tamaño de empresa, rango de precio, «no es para ti si…». Menos leads, mejores llamadas.
4. **Anti-hype como diferencial:** «no te vamos a vender un robot», «a veces la respuesta es una hoja de cálculo mejor
   hecha». En un mercado lleno de promesas, la honestidad es posicionamiento. **[HYPOTHESIS]** sobre su efecto en
   conversión ([08/11 §1](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md), principio 10).
   Apunta en esa dirección: en experimentos con más de 1.000 adultos de EE. UU. (Cicek, Gursoy y Lu, 2024), mencionar
   «inteligencia artificial» en la descripción de un producto **bajó** la intención de compra por menor confianza, y más
   en compras de riesgo; es consumo, no B2B, pero tu comprador también compra con miedo. **[EMPIRICAL]** (transferencia
   a B2B: **[HYPOTHESIS]**) Prueba un concepto que no diga «IA» en los tres primeros segundos frente a uno que sí.
5. **Diversidad real:** conceptos distintos (otra persona, otro proceso, otro formato), no tres versiones del mismo
   vídeo con otro titular ([00-ESTADO-ACTUAL-2026 §0](../00-ESTADO-ACTUAL-2026.md)).

### 8.2 Formatos que funcionan en este nicho

| Formato | Qué es | Por qué funciona | Cómo hacerlo bien | Skill |
|---|---|---|---|---|
| **Fundador a cámara** | 30–60 s explicando un error frecuente, un caso o cómo trabajas | La pyme compra a personas; reduce el miedo al proveedor desconocido | Un mensaje por vídeo; subtítulos; el proceso en los 3 primeros segundos | `/producir-video` (vídeo propio) |
| **Demo del sistema** | Pantalla real: el albarán entra, la línea aparece en el programa de gestión, alguien revisa | Vuelve tangible lo abstracto; responde «¿esto qué es?» | Datos ficticios; tiempo real o acelerado y marcado; enseña la revisión humana | `/producir-video`, `editor-video` |
| **Antes y después del proceso** | Diagrama o vídeo: 7 pasos y 3 personas → 2 pasos y una revisión | Se entiende sin saber de IA | Pasos concretos, tiempos medidos | `/producir-estatico`, `disenador-estaticos` |
| **Caso con cifras verificables** | Punto de partida, qué se hizo, plazo, resultado medido, quién lo midió, con permiso | Es la prueba más fuerte en B2B | El cliente con nombre y cara si acepta; si no, sector y tamaño | `/casos-y-creadores` |
| **Testimonio de quien lo usa** | La administrativa o el jefe de taller, no solo el dueño | Responde a «mi equipo no lo va a usar» | Grabado en su puesto | `/casos-y-creadores` |
| **Estático con titular** | Una frase del dolor y una prueba | El formato más barato para testear ángulos; en B2B suele competir con el vídeo en CPL | Texto grande, una idea | `/producir-estatico` |
| **Carrusel de pasos o de objeciones** | «Qué preguntamos antes de tocar tus datos» | Educa y filtra | 5–7 tarjetas, una idea por tarjeta | `/producir-estatico` |
| **Clip de podcast o conversación** | Fundador con un cliente o un experto | Autoridad sin vender | 30–60 s con un insight concreto | `/organico-a-anuncios` |

En B2B los estáticos compiten con el vídeo en coste por lead: en el benchmark de Metadata, imagen 136 $ frente a vídeo
225 $ de CPL en Facebook. **[EMPIRICAL]** ([05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md)) Prueba los dos
formatos con el mismo mensaje.

**Vídeo con IA en este nicho:** útil para animar diagramas o crear escenas de producto; **nunca** para fabricar clientes,
testimonios o «empleados» que no existen. Además de engañoso, destruye la credibilidad de quien vende IA.
**[STRONG INFERENCE]** Sobre el etiquetado:

- **Meta** añade por su cuenta «AI info» a los anuncios creados o editados de forma significativa con sus herramientas de
  IA generativa y detecta las de terceros por señales estándar del sector; desde junio de 2026 lo muestra en «Sobre este
  anuncio». Para anuncios comerciales (no de temas sociales o políticos) sus políticas **no obligan** al anunciante a
  declararlo. **[OFFICIAL META]** (post de transparencia del 2025-02-03, actualizado el 2026-06-01)
- **El Reglamento de IA**, en cambio, obliga desde el 2026-08-02 a quien usa un sistema que genera imagen, audio o vídeo
  que imita personas, lugares o hechos reales y podría pasar por auténtico (*deepfake*) a declarar que es artificial
  (art. 50.4). Un «cliente» o un «empleado» realista generado con IA en un anuncio entra de lleno.
  **[OFFICIAL — regulador]** + **[STRONG INFERENCE]** (aplicación a la publicidad; no es asesoría legal)
- La política de IA de cada cliente va en la ficha y en el `LEEME.md` de cada pieza (etiqueta de IA incluida).
- Ranking completo de formatos (de fundador a cámara a avatar), evidencia y tabla de qué hay que etiquetar:
  [03/16](../03-creatividad/16-ia-generativa-en-anuncios-que-funciona.md).

### 8.3 Objeciones convertidas en ángulos

| Objeción | La respuesta honesta | Concepto de anuncio | Prueba que necesitas |
|---|---|---|---|
| **«¿Esto no lo hace ya ChatGPT?»** | Un asistente de chat ayuda a una persona en una conversación; tu problema es un proceso entre programas y personas: datos que llegan en PDF o correo y tienen que acabar en tu sistema, con control, permisos, registro y alguien que lo mantenga. A veces la respuesta correcta **sí** es ChatGPT bien usado: entonces vende formación o di que no | Fundador: «Lo que ChatGPT sí puede hacer en tu empresa (y lo que no)»; pantalla dividida copiar-pegar frente a flujo integrado; «3 tareas que no necesitan un proyecto: hazlas hoy» | Demo del flujo integrado con revisión y registro |
| **Privacidad y RGPD** | Qué datos se tocan, dónde se procesan, con qué proveedor y contrato (encargo de tratamiento), si el proveedor entrena con tus datos (configuración), revisión humana, permisos y registro de accesos (lo mínimo, debajo de la tabla) | Carrusel «Lo que preguntamos antes de tocar tus datos»; fundador explicando el mapa de datos de un caso | Una hoja de «mapa de datos» por proyecto (también va en la propuesta) |
| **«Mi equipo no lo va a usar»** | Se diseña con quien lo usa (un día observando el puesto), cambia lo mínimo su forma de trabajar (su correo, su WhatsApp, su programa), tiene revisión humana y formación; la adopción se mide en la semana 4 | Testimonio de la persona que lo usa a diario; «Lo diseñamos con quien lo va a usar» | Métrica de adopción de un caso (% de documentos que pasan por el sistema) |
| **«Ya probamos y no funcionó»** | Pregunta qué falló: alcance demasiado grande, chatbot genérico, nadie a cargo, sin mantenimiento. La salida es un piloto acotado con criterio de éxito y fecha | Fundador: «Por qué fallan los proyectos de IA en pymes (y qué hacemos distinto)» | Un caso de rescate; el formato del piloto |
| **Precio** | Rangos públicos, precio cerrado tras el diagnóstico, fases, piloto deducible, mantenimiento transparente; el ahorro calculado con sus números, con rango | «Cuánto cuesta automatizar [proceso] en una pyme: rangos reales» | Tabla de rangos; el diagnóstico |
| **«¿Y si desaparecéis?»** | Todo en sus cuentas, documentado, sin bloqueo: si mañana cambia de proveedor, sigue funcionando | «Todo queda en tus cuentas» | Lista de entregables de documentación |
| **«No tengo tiempo para un proyecto»** | Cuántas horas le pide a él (p. ej. 3 reuniones de 45 min) y a su equipo | «Lo que te pedimos a ti: 3 reuniones» | Calendario tipo de un proyecto |

**Lo mínimo para responder a «¿y la privacidad?»** (la duda la tiene más de la mitad de tus compradores, sección 1):

1. **Papeles:** el cliente es el responsable del tratamiento; tú (si operas el sistema) y el proveedor del modelo por
   API sois encargados o subencargados. Hace falta contrato de encargo (RGPD, art. 28). **[OFFICIAL — regulador]**
2. **Contratación del modelo:** modalidad empresarial, no la gratuita; cláusula de que los datos no se reutilizan ni se
   usan para entrenar; retención, registros y ubicación de los datos revisados; funciones de riesgo desactivables
   (resumen de obligaciones de la AEPD sobre IA generativa, enero de 2026). **[OFFICIAL — regulador]**
3. **Transferencias fuera de la UE:** el marco de privacidad UE-EE. UU. sigue vigente (el Tribunal General desestimó el
   recurso contra él el 2025-09-03; hay casación pendiente); si el proveedor no está adherido, cláusulas contractuales
   tipo. **[OFFICIAL — regulador]** (estado de la casación no verificado a 2026-11-09)
4. **Minimización, base jurídica e información** a las personas afectadas (arts. 13 y 14); **evaluación de impacto**
   (art. 35) si el tratamiento es de alto riesgo; **supervisión humana real** si hay decisiones automatizadas con
   efectos sobre personas (art. 22). **[OFFICIAL — regulador]**
5. **Para sistemas agénticos** (que actúan solos en el correo, el CRM o el programa de gestión), la AEPD publicó
   orientaciones específicas el 2026-02-18: léelas antes de proponer uno. **[OFFICIAL — regulador]**

Prepara una hoja de «mapa de datos» por proyecto con estos cinco puntos: es contenido de anuncio (carrusel), argumento de
la propuesta y protección tuya. Los cambios del RGPD que negocia la UE (Ómnibus de datos) no estaban aprobados el
2026-11-09. Nada de esto es asesoría legal: si el proyecto toca datos sensibles, que lo revise un especialista.

Las objeciones reales salen de tus llamadas: `transcribir.py` y `/voz-cliente` las convierten en lenguaje literal y
ángulos; los motivos de pérdida del CRM te dicen cuál pesa más.

### 8.4 Ángulos por proceso

| Proceso | Dolor en palabras del cliente | Concepto | Prueba |
|---|---|---|---|
| Integraciones entre herramientas | «Tecleamos lo mismo en tres programas» | Contador de copiar-pegar de un día | Diagrama antes y después |
| Lectura de documentos (facturas, albaranes, pedidos) con revisión humana | «El lunes se va entero en albaranes» | Demo: foto del albarán → línea en el programa → revisión | Precisión medida y minutos por documento |
| Buscador interno | «¿Dónde estaba ese contrato o esa ficha técnica?» | Pregunta y respuesta con la fuente citada | Demo con documentos ficticios |
| Generador de presupuestos | «Un presupuesto tarda dos días y lo pierde el más rápido» | Cronómetro: de la petición al PDF | Tiempo medio antes y después |
| Asistente de preguntas repetidas con su documentación | «Contestamos las mismas 20 preguntas cada semana» | La respuesta con enlace a la fuente y derivación a una persona | % de consultas resueltas sin intervención y % derivadas |
| Seguimiento automático de propuestas | «Mandamos presupuestos y nadie los persigue» | Secuencia de seguimiento que suena humana | % de presupuestos con seguimiento y tasa de respuesta |
| Entrada única y reparto de leads | «Los contactos entran por cinco sitios y nadie responde en una hora» | «Así respondemos nosotros a tu formulario en un minuto» (vívelo en tu propio embudo) | Tu propio tiempo de respuesta |
| Confirmación y reprogramación de citas (voz o WhatsApp) | «Huecos vacíos por gente que no avisa» | Llamada o mensaje de confirmación real (con permiso) | Show antes y después |
| Facturación y cobros | «Cobramos tarde porque nadie reclama» | Recordatorio de cobro amable y automático | Días medios de cobro antes y después (ver la nota sobre Verifactu debajo) |
| Informes y cuadros de mando | «El informe del lunes nos come media mañana» | El informe que llega solo a las 8:00 | Horas ahorradas medidas |
| Altas de clientes | «El papeleo de alta tarda una semana» | Alta guiada con documentos validados | Plazo de alta |
| Formación in-company | «Mi equipo usa ChatGPT sin criterio» | «Dos sesiones y normas de uso con casos de tu empresa» | Programa y materiales (sin vender miedo al artículo 4, sección 4.4) |

**Facturación electrónica y Verifactu: fechas con fuente o nada** (estado a 2026-11-09). Es un ángulo potente para
procesos de facturas, y también donde más anuncios mienten por miedo. **[OFFICIAL — regulador]**

| Obligación | Fecha vigente | Matiz |
|---|---|---|
| Verifactu (sistemas de facturación adaptados), contribuyentes del Impuesto sobre Sociedades | 2027-01-01 (RDL 15/2025) | Hacienda anunció el 2026-10-05 la «previsión» de aplazarlo a octubre de 2028; no estaba en el BOE el 2026-11-09 |
| Verifactu, resto (incluidos autónomos) | 2027-07-01 | Ídem |
| Factura electrónica B2B, empresas con más de 8 M€ de volumen de operaciones | 2027-10-06 (RD 238/2026 y Orden HAC/1028/2026) | Emitir, recibir e informar del estado de factura y pago |
| Factura electrónica B2B, resto | 2028-10-06 | — |

Dato de partida que sí puedes usar: en 2025, el 61,6 % de las empresas de 10 o más empleados envió facturas en papel y
solo el 14,2 % mandó facturas electrónicas estructuradas en al menos la mitad de sus facturas (INE).
**[OFFICIAL — INE]** Ángulo honesto: «prepara tu facturación con calma y aprovecha para quitar el tecleo», no «multas
desde enero». Vuelve a comprobar las fechas antes de cada lote.

### 8.5 Ángulos por sector

| Sector | Procesos que más duelen | Prueba que convence | Ojo con |
|---|---|---|---|
| Distribución y mayoristas | Albaranes, pedidos por correo o WhatsApp, stock | Minutos por pedido | Integración con el programa de gestión |
| Asesorías y despachos | Documentos de clientes, preguntas repetidas, plazos | Horas en campaña de impuestos | Confidencialidad y secreto profesional |
| Clínicas y centros de salud | Citas, recordatorios, preguntas frecuentes | Show antes y después | Datos de salud: nunca en eventos, formularios ni anuncios ([04/09](../04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md)); políticas de salud ([08/07](../08-cuenta-politicas-seguridad/07-categorias-especiales-y-sensibles.md)) |
| Instaladores y servicios técnicos | Presupuestos, partes de trabajo, seguimiento | Presupuestos enviados en el día | Trabajo de campo, móvil |
| Inmobiliarias | Leads de portales, visitas, documentación | Tiempo de respuesta | Categoría especial si anuncias vivienda (no si anuncias tu servicio a la agencia) |
| Academias y formación | Matrículas, dudas, recordatorios | Respuestas en horario de cierre | Menores |
| Comercio online pequeño | Atención al cliente, devoluciones, catálogo | Consultas resueltas | Picos de campaña |
| Industria pequeña | Pedidos, calidad, documentación técnica | Errores de transcripción | Sistemas antiguos |

`/competencia` (con `ad_library.py`, incluido `vigilar`) te dice qué prometen los demás en tu sector y dónde está el
hueco; casi siempre es la especificidad y la prueba.

### 8.6 Cuántos conceptos al mes según gasto

```
Conceptos nuevos testables/mes ≈ presupuesto/mes × explorar_explotar (ficha, 0,3 por defecto)
                                 / (2,5 × coste objetivo de la métrica de test)
```

Con los targets de Acme (67 € por diagnóstico, 133 € por cualificado):

| Presupuesto/mes | Para explorar (30 %) | Conceptos/mes juzgando por diagnóstico | Juzgando por cualificado |
|---|---|---|---|
| 1.500 € | 450 € | 2–3 | 1 |
| 3.000 € | 900 € | 5 | 2–3 |
| 6.000 € | 1.800 € | 10 | 5 |
| 12.000 € | 3.600 € | 20 | 10 |

Más las iteraciones de los ganadores (otros hooks, otros formatos), que no cuentan como conceptos. **[STRONG INFERENCE]**
(aritmética sobre la regla de corte de [13/05](../13-sistema-operativo/05-framework-testing-creativo.md)).
`/siguiente-anuncio` elige el próximo con la capa más baja de verdad; `/analisis-creativo` (con
`elementos_creativos.py`) te dice qué elementos ganan, no solo qué anuncio.

### 8.7 Qué no decir

| No | Por qué | Mejor |
|---|---|---|
| «Ahorra 20 horas a la semana» sin un caso detrás | Expectativa irreal; atrae a quien quiere milagros | «Un distribuidor de 25 personas pasó de 9 a 2 horas semanales en albaranes (caso medido; los tuyos dependen de tu volumen)» o «Calcula cuántas horas se te van» |
| «Reduce costes un 70 %», «sustituye a dos empleados» | Promesa no defendible; asusta al equipo | Horas recuperadas y errores evitados, con caso |
| «100 % automático», «sin errores», «garantizado» | Falso en sistemas con revisión humana; riesgo de política | «Con revisión humana en los casos dudosos» |
| «En 7 días tienes tu IA» | Plazo engañoso | Plazos reales por fase |
| Capturas de tu facturación o «facturamos X gracias a…» | Promesa de ingresos implícita; riesgo de cuenta | Resultados del cliente con contexto |
| Testimonios inventados, avatares de IA como clientes, logos sin permiso | Engañoso; políticas de prácticas comerciales | `/casos-y-creadores` con permisos escritos |
| «¿Estás harto de…?», «¿Tu negocio va mal?» dirigidos a atributos de la persona | Atributos personales | «Para empresas que…» o «Si quieres…» |
| «Tu competencia ya usa IA y te vas a quedar atrás» (miedo) | Sensacionalismo; baja calidad | El coste real de seguir igual, con sus números |

Las políticas que aplican: prácticas comerciales prohibidas, atributos personales y coherencia anuncio–landing
([08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md),
[08/11](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md)). Lo verificado el 2026-11-09
**[OFFICIAL META]**:

- *Prohibited commercial practices* está en la categoría de contenido engañoso de las Advertising Standards y remite a la
  norma comunitaria del mismo nombre (la KB fecha la unificación el 2026-09-09; el registro de cambios visible muestra
  una versión del 2026-10-29). Prohíbe ofrecer una recompensa económica irreal a cambio de un esfuerzo mínimo o poco
  claro y, por las quejas de usuarios, sanciona el producto que no coincide con lo anunciado y los precios engañosos,
  con riesgo de deshabilitar la cuenta.
- No existe una norma específica sobre IA o automatización, ni una lista general de «resultados irreales» fuera de
  salud y bienestar. «Ahorra X € garantizado» o «sustituye a dos empleados» se acercan a la recompensa irreal y al
  producto que no coincide con lo anunciado. **[STRONG INFERENCE]**

Antes de publicar:
`/revisar-anuncio` con `revisor-politicas`, que escribe el veredicto en el `LEEME.md` (sin él, `control_publicacion`
pide confirmación).

---

## 9. Después del lead: el ciclo comercial

### 9.1 Velocidad de respuesta

- **Lead en el CRM en < 1 minuto; primer mensaje automático en < 1 minuto; primer intento humano en < 5 minutos** en
  horario; 6 intentos en 48–72 h mezclando llamada, WhatsApp y email; después, a nurture. **[STRONG INFERENCE]**
  ([05/08](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md))
- **Qué hay detrás de esa regla:** el estudio más sólido sigue siendo el de HBR de 2011 (auditoría de 2.241 empresas y
  1,25 millones de leads): contactar en la primera hora daba ~7 veces más probabilidad de cualificar que hacerlo una hora
  después y ~60 veces más que esperar 24 horas o más; es correlacional. **[EMPIRICAL]** No hay ningún estudio
  independiente de 2024–2026 que lo actualice, y las cifras que más circulan («21 veces más a 5 minutos», «+391 % en el
  primer minuto») no tienen fuente primaria localizable: no las uses en tus anuncios. Lo que sí está medido es que casi
  nadie responde: en una prueba con 1.000 webs B2B, el 63,5 % no contestó nunca una petición de demo (vendor).
  **[EMPIRICAL]** Responder en minutos es barato y te diferencia; cuánto sube el cierre, mídelo tú.
- **El primer mensaje** dice quién eres, por qué escribes («has hecho el diagnóstico de horas de facturas»), qué
  propones (dos huecos concretos) y cómo decir que no. Nada de «¿tienes 5 minutos para hablar de IA?».
- **Vende con tu propio embudo:** si vendes respuesta automática y reparto de leads, tu lead tiene que recibir la mejor
  respuesta automática que haya visto. Es tu demo más convincente. **[STRONG INFERENCE]**
- `/seguimiento-leads` te ayuda a fijar el SLA, las secuencias de primer contacto y asistencia y el seguimiento de
  propuestas abiertas. Mide la velocidad real en GHL: `ghl.py` no lee los mensajes salientes, así que el brief diario no
  puede calcularla por ti.
- **Un sistema que manda mensajes a contactos lo enciendes tú** en GHL: el OS nunca envía mensajes, emails ni WhatsApp a
  contactos (regla de seguridad del producto).

### 9.2 Asistencia a la llamada

- **Citas en ≤ 72 h** (a 1 día se celebran bastante más que a 14 días en los análisis disponibles; en los datos de una
  plataforma de ventas, un 6,9 % de ausencias en reuniones del mismo día frente a un 23 % a 8 días o más), confirmación
  activa («responde SÍ para confirmar»), recordatorios a 24 h y 1–2 h por WhatsApp y email, reprogramación en un clic.
  **[EMPIRICAL]** débil-medio ([05/08 §3](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md))
- **Pide una pequeña tarea previa** que también cualifica: «trae el número de facturas de proveedor del último mes» o
  «mándanos un documento de ejemplo sin datos personales». **[HYPOTHESIS]**
- **Mide el show con cancelaciones en el denominador** y por anuncio, plazo de reserva y canal.

### 9.3 La llamada y la propuesta investigada

**La llamada de diagnóstico (30–45 min) no es una presentación.** Estructura: confirmar los números del diagnóstico,
entender el proceso paso a paso (quién, con qué programa, cuánto tarda, qué falla), qué han probado, quién decide y
cuándo, y cerrar con uno de tres finales honestos: «hay caso, te preparo una propuesta» · «no hay caso, esto es lo que
puedes hacer tú» · «falta un dato, te lo pido». **[STRONG INFERENCE]**

**Solo propuesta investigada para quien la merece** (decide, hay caso, hay fecha). Lo que lleva:

1. **Hallazgos comprobables del cliente antes de cobrar:** su proceso dibujado tal como es hoy, sus volúmenes y tiempos
   (del diagnóstico y la llamada), 2–3 cosas que has comprobado (un documento de ejemplo procesado con datos ficticios,
   un error recurrente que has detectado, una integración que su programa permite o no). Es lo que convierte una
   propuesta en una prueba. **[STRONG INFERENCE]**
2. **Qué se propone:** alcance por fases, entregables, criterios de aceptación medibles, plazo, quién hace qué.
3. **Qué no se propone y por qué:** «no automatizamos la aprobación de pagos: el riesgo no compensa», «no hace falta un
   asistente para esto; basta con una plantilla». Da credibilidad y evita discusiones de alcance.
4. **Precio cerrado** con opciones (piloto, proyecto, proyecto + mantenimiento) y forma de pago.
5. **Ahorro estimado con rango y supuestos**, los mismos del diagnóstico, y el payback en rango.
6. **Mapa de datos y riesgos:** qué datos, dónde, con qué proveedor, qué pasa si falla, quién revisa.
7. **Siguiente paso con fecha** y validez de la oferta (real).

Envía la propuesta en una llamada corta (o un vídeo de 5 minutos), no solo por email, y agenda el seguimiento en ese
momento. Mide propuesta→ganado por tipo de proyecto y por fuente.

Referencia externa: en 742.137 propuestas enviadas en 2025 con una herramienta de propuestas, se cerró el 34 % (valor
medio de las ganadas, 16.388 $), y un 15 % más con firma electrónica. Son usuarios de esa herramienta (sesgo de
selección) y de todos los sectores. **[EMPIRICAL]** (vendor) No hay datos públicos con metodología para consultoras de
automatización en España: el 35 % de Acme es **[HYPOTHESIS]** hasta que tengas 10 propuestas propias.

**Coste de la propuesta:** si investigarla cuesta 8 h, solo vale para leads cualificados que han asistido a la llamada.
Si el volumen sube, cobra el diagnóstico profundo (piloto o auditoría de pago deducible) antes de investigar.
**[STRONG INFERENCE]**

### 9.4 Ciclo largo y nurture

- **Perdido no es para siempre.** «Mal momento», «no compensa todavía» y «lo hará internamente» vuelven: secuencia de
  email (con consentimiento) cada 2–4 semanas con un caso, una idea aplicable y una invitación al taller mensual; re-
  diagnóstico a los 6 meses. **[STRONG INFERENCE]**
- **Propuesta abierta:** seguimiento a los 2, 7 y 14 días con algo nuevo cada vez (respuesta a una duda, un caso del
  mismo sector, una opción de piloto). Después, a nurture. **[HYPOTHESIS]** sobre la cadencia.
- **Contenido que sirve en ciclos largos:** casos del mismo sector, demos cortas, el «qué no automatizar», comparativas
  honestas (hacerlo internamente frente a contratarlo).
- **Por qué merece la pena:** la heurística 95:5 del B2B Institute dice que, en cada momento, solo ~5 % de tus
  compradores potenciales está en el mercado; el resto comprará más adelante y recordará a quien le enseñó algo útil.
  Es una heurística, no una medida. **[EMPIRICAL]** débil. En empresas medianas y grandes, el comprador contacta al
  proveedor cuando ya lleva el 61 % de su proceso (6sense, 2025): en pymes el ciclo es más corto, pero el patrón de
  «investigo solo y luego llamo» es el mismo. **[EMPIRICAL]** + **[STRONG INFERENCE]** Tus anuncios de prueba y tu
  contenido orgánico trabajan en esa fase invisible.

### 9.5 Anuncios por etapa

`/anuncios-por-etapa` crea audiencias por etapa a partir del CRM (`audiencias_meta.py etapas` genera los CSV
hasheados desde `privado/`; `crear` y `sincronizar` exigen confirmación) y los anuncios que tocan a cada una:

| Etapa | Audiencia | Mensaje | Presupuesto orientativo | Excluir |
|---|---|---|---|---|
| Visitó la web o vio el 50 % de un vídeo, sin lead | Web 180 días, vídeo 50 % 365 días | Caso del sector, demo, objeción ChatGPT | Dentro de la campaña principal (Advantage+ ya lo hace) o 5 % | Leads |
| Diagnóstico sin terminar | Según la variante (sección 5.3): `DiagnosticoCompletado` sin `Lead` (`captura: despues`), visita a la página del diagnóstico sin `Lead` (`antes`) o `Lead` sin `DiagnosticoCompletado` (contacto en el primer paso); 30 días | «Te quedan 3 minutos», el resultado de ejemplo | 2–3 % | Quien ya hizo el paso que falta |
| `cualificado` o `llamada` | Lista del CRM | Vídeo «qué pasará en la llamada», un caso | 1–3 % | Asistió |
| `propuesta` | Lista del CRM | Caso del mismo tipo de proyecto, objeción del precio, «todo queda en tus cuentas» | 2–5 % | Ganado |
| `perdido` por «mal momento» o «no compensa todavía» | Lista del CRM, 60–180 días | Taller mensual, re-diagnóstico | 1–2 % | Ganado |
| `ganado` | Clientes | Mantenimiento, formación, otro proceso | Aparte, si hay economía | — |

Total orientativo del 5–15 % del presupuesto. **[HYPOTHESIS]** (heurística, [05/06 §3](../05-leadgen-high-ticket-crm/06-high-ticket-funnels.md))
Para saber si estos anuncios suman, deja un grupo de control: `audiencias_meta.py etapas --control 0.2` aparta una
fracción fija de cada segmento (siempre la misma persona en cada refresco) y `medir` compara grupo y control. Para
excluir usa la lista `<segmento>-completa.csv` (todos, también el control), nunca la del tratamiento, o el control
verá tus otros anuncios. Las bajas y los «no me contactéis» salen de todas las listas; con `--bajas` van a `bajas.csv`,
para una audiencia solo de exclusión. Detalle: [guía de anuncios por etapa](../../docs/guias/anuncios-por-etapa.md).
Ojo: las audiencias de pocas decenas de personas casi no entregan y la frecuencia se dispara; con volúmenes pequeños,
agrupa etapas (p. ej. «cualificado + llamada + propuesta» en una sola audiencia «pipeline abierto»). Meta no publica un
tamaño mínimo para las listas de clientes ni una tasa de coincidencia esperada; más identificadores (email, teléfono,
nombre, ciudad) suben la coincidencia. **[OFFICIAL META]** + **[STRONG INFERENCE]** Para quien te ha pedido no recibir
publicidad o no ser contactado, usa una audiencia de lista **solo de exclusión** (desde agosto de 2026; no sirve como
semilla de similares ni en reglas de valor). **[OFFICIAL META]**
([02/07](../02-estructura-campanas/07-audiencias-2026.md)) Las listas del CRM se usan solo con base legal y si tu
aviso de privacidad lo cubre.

---

## 10. Medición y reglas de decisión

### 10.1 Las capas de verdad de una consultora

```
cash cobrado y contribución por proyecto (facturas, Stripe)      ← decide el presupuesto total
  > ganado (CRM, por ad_id del lead)                               ← decide ofertas y embudos, por trimestre
    > propuesta enviada y pipeline ponderado                       ← indicador adelantado mensual
      > llamada asistida                                           ← decide embudos y ángulos (2–3 semanas)
        > cualificado                                              ← decide anuncios (1–2 semanas)
          > diagnóstico completado → lead                          ← decide anuncios con poco volumen (días)
            > métricas antes del clic (hook, CTR)                  ← solo descartan perdedores
```

Decide con la capa más baja **que ya haya madurado con muestra suficiente**
([13/01 §4](../13-sistema-operativo/01-principios-de-razonamiento.md)). **[STRONG INFERENCE]**

### 10.2 Ventanas que maduran

Las tuyas, medidas con `embudo.py cohortes --por semana`. Valores de partida **[HYPOTHESIS]**:

| Paso | El 80–90 % ocurre en | Cohorte semanal legible a partir de |
|---|---|---|
| `lead` → `diagnostico` | Minutos (web) o 1–3 días (formulario + enlace) | 3 días |
| `diagnostico` → `cualificado` | 1–2 días | 1 semana |
| `cualificado` → `llamada` | 1–5 días | 1 semana |
| `llamada` → `asistio` | ≤ 72 h si el calendario es corto | 2 semanas |
| `asistio` → `propuesta` | 3–10 días | 3–4 semanas |
| `propuesta` → `ganado` | 2–6 semanas (más con piloto) | 6–10 semanas |

Consecuencia: **la cohorte de la semana pasada solo dice algo hasta `llamada`**. «Este mes no ha cerrado nada» con
leads de hace 10 días no es información. Y Meta solo aprende de lo que pasa dentro de su ventana: una firma a 40 días
no existe para la optimización ([04/12](../04-tracking-atribucion-medicion/12-attribution-lag.md)). Indica siempre la
ventana de atribución con la que lees Ads Manager; para decidir, usa el CRM por `ad_id`.

Desde el 2026-03-03, en conversiones **web**, el clic de la atribución cuenta solo los clics en enlace (compartir o
guardar pasan a *engage-through*, de 1 día) y han aparecido modelos de atribución estándar, incremental y
personalizado; algunas cuentas aún ven la versión anterior. Los leads de formulario instantáneo son conversiones dentro de
Meta y no hay fuente oficial de que el cambio les afecte. **[OFFICIAL META]** Si comparas un embudo web con uno de
formulario, hazlo en el CRM, no en las columnas de Ads Manager.

### 10.3 Reglas de decisión

| Decisión | Métrica | Umbral (Acme como ejemplo) | Mínimo antes de decidir | Cadencia |
|---|---|---|---|---|
| Apagar un anuncio | Coste por diagnóstico (o lead) | 0 diagnósticos tras 2–3× el target (134–200 €) | Ese gasto | Semanal |
| Apagar un anuncio «barato que no cualifica» | % a `cualificado` | 0 cualificados con ≥ 10 diagnósticos | 10 diagnósticos | Semanal |
| Ganador provisional | Coste por cualificado | ≤ target (133 €) con ≥ 5–8 cualificados | 2 semanas | Quincenal |
| Cambiar de ángulo u oferta | Coste por llamada asistida | > BE (592 €) 4 semanas seguidas con ≥ 10 llamadas esperadas | 4 semanas | Mensual |
| Cambiar de embudo (A ↔ B) | Coste por llamada asistida y por propuesta | Test con el mismo anuncio, ≥ 4–6 semanas | Ambas cohortes maduras hasta `asistio` | Mensual |
| Pasar a Conversion Leads | Volumen de `cualificado` y cobertura | ≥ 15–20/semana 3 semanas, cobertura ≥ 60 %, definición estable | Sección 6.2 | Cuando se cumpla |
| Subir presupuesto | Coste por llamada asistida y capacidad | ≤ target 3 semanas, capacidad libre (sección 3.6), pipeline sano | 3 semanas | +20–30 % cada ≥ 7 días |
| Bajar o pausar | CAC de la cohorte madura | > BE (3.382 €) en el trimestre sin pipeline que lo compense | 8–10 semanas | Trimestral |
| «Es de ventas, no de Meta» | Coste por llamada estable y propuesta→ganado cayendo | Caída ≥ 10 puntos con ≥ 10 propuestas | 10 propuestas | Mensual |

**[STRONG INFERENCE]** (umbrales derivados de [13/05](../13-sistema-operativo/05-framework-testing-creativo.md),
[13/01 §8](../13-sistema-operativo/01-principios-de-razonamiento.md) y [05/05](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md));
los mínimos de muestra concretos son **[HYPOTHESIS]**. `estadistica.py` te dice si una diferencia es ruido.

**Separa marketing de ventas** ([playbook-high-ticket §9](playbook-high-ticket.md)):

- Coste por llamada asistida estable y CAC subiendo → propuesta, precio o seguimiento, no Meta.
- Coste por cualificado subiendo con show y cierre estables → creatividad, fatiga u oferta de entrada.
- Un ángulo con muchas llamadas y cero propuestas → promesa demasiado fácil: reescríbelo aunque su coste por llamada sea
  bueno.

### 10.4 Rituales y herramientas

| Frecuencia | Qué | Con qué |
|---|---|---|
| Diario (2 min) | Solo roturas: gasto anómalo, rechazos, señal del dataset, leads y citas de ayer | `/brief-diario` |
| Semanal | Cohortes por anuncio hasta la etapa madura; 1–3 decisiones con fecha de evaluación | `/informe-semanal`, `/embudo`, `ghl.py por-anuncio`, `registro_creativo.py actualizar` |
| Mensual | Tasas reales → recalcular break-even; motivos de pérdida → nuevos ángulos | `/revision-mensual`, `/economia`, `/voz-cliente` |
| Trimestral | Presupuesto con CAC, contribución y capacidad; oferta y precio | `/escalar`, `analista-cuantitativo` |

**Incrementalidad con poco presupuesto:** no tendrás volumen para un *conversion lift*. Usa lo que tienes: la pregunta
«¿cómo nos conociste?» en el formulario o en la llamada (atribución declarada, útil en B2B porque mucho ocurre fuera de
lo medible), la evolución de las búsquedas de tu marca y las pausas planificadas con antes y después, sabiendo que son
lecturas débiles. **[HYPOTHESIS]** ([04/13](../04-tracking-atribucion-medicion/13-incrementalidad-lift-geo-tests.md))

---

## 11. Errores frecuentes

1. **Vender «IA» en vez del proceso del cliente.** El anuncio encuentra curiosos de la IA, no compradores.
2. **«Consultoría gratuita» como oferta de entrada.** No filtra, no da valor y llena la agenda de gente que no comprará.
3. **Una calculadora que promete** (una cifra, sin supuestos) o mandar el ahorro bruto como `value` a Meta.
4. **Formulario *More volume* optimizado a `Lead` y celebrado por el CPL.**
5. **Fragmentar 2.000 €/mes en cuatro conjuntos por sector.**
6. **Lanzar Conversion Leads el primer día** sin volumen, sin definición estable de `cualificado` o con cobertura < 60 %.
7. **Calendario abierto a todos:** la agenda del fundador llena de curiosos y las buenas citas a 10 días.
8. **Responder al día siguiente.** El lead ya no se acuerda y el sistema aprende que era «malo».
9. **Propuestas de plantilla** (cierre bajo) o **propuestas investigadas para todos** (coste oculto).
10. **Decidir con cohortes inmaduras** o con un mes de 2 ventas esperadas.
11. **Avatares de IA como clientes, testimonios inventados o logos sin permiso.**
12. **Subir a Meta listas de prospección sin base legal.**
13. **Escalar por encima de la capacidad de diagnosticar y proponer.**
14. **Mejoras automáticas de Meta encendidas** que reescriben el texto con cifras que no puedes defender.
15. **Olvidar el 3 % de recargo por país y el coste de vender** al comparar con el break-even.

---

## 12. Plan de 90 días

| Semanas | Qué haces | Skills y herramientas | Criterio para pasar |
|---|---|---|---|
| 0 (preparación) | Ficha (`servicios-high-ticket`), economía por etapa con tus números, oferta de entrada y principal, definición de `cualificado`, capacidad semanal | `/cliente-nuevo`, `/economia`, `/oferta`, `/iman-de-leads`, `/disenar-funnel` | Break-even y target por etapa en la ficha; techo de capacidad calculado |
| 0 (señal) | Cuenta y topes, dataset, píxel con consentimiento + CAPI (`Lead`, `DiagnosticoCompletado`), pipeline §16 en GHL con CAPI de CRM, landing o formulario, SLA de respuesta, reglas de protección | `/configurar-meta`, `/implementar-capi`, `/construir-landing` o `/formulario-instantaneo`, `/seguimiento-leads`, `/reglas-automaticas` | Lead de prueba en GHL en < 1 min con `ad_id`; eventos en *Probar eventos* sin duplicar |
| 0 (investigación) | Lenguaje del comprador y competencia | `/voz-cliente`, `/competencia` | 3–4 ángulos con prueba disponible |
| 1–2 | Primer lote: 3–4 conceptos (fundador, demo, caso o antes/después, objeción ChatGPT) en estático y vídeo; revisión de políticas; campaña en pausa y activación | `/brief-creativo`, `/producir-video`, `/producir-estatico`, `/revisar-anuncio`, `/lanzar-campana`, `/publicar-anuncios` | Gasto estable; diagnósticos llegando |
| 3–4 | Primera lectura: coste por diagnóstico y % a `cualificado` por anuncio; cortes a 2–3×; segundo lote (iteraciones del que cualifica + 2 conceptos nuevos); auditoría de velocidad de respuesta | `/informe-semanal`, `/test-creativo`, `/siguiente-anuncio`, `/embudo` | Coste por cualificado medido; mediana de primer contacto < 15 min |
| 5–6 | Primeras llamadas asistidas y propuestas; primer caso documentado; anuncios por etapa si hay audiencia | `/casos-y-creadores`, `/anuncios-por-etapa` | Show ≥ 65–70 %; coste por llamada asistida ≤ break-even |
| 7–8 | Recalcula la economía con tasas reales; decide el test de embudo (A frente a B) si el presupuesto llega; análisis de elementos creativos | `/economia`, `/analisis-creativo`, `/organico-a-anuncios` | Tasas reales sustituyen a las supuestas |
| 9–10 | Primeras cohortes maduras hasta `ganado`; valora Conversion Leads (sección 6.2); taller mensual si el mercado está frío | `/revision-mensual`, `/webinar` | Coste por propuesta ≤ target |
| 11–13 | Decisión trimestral: escalar (por coste marginal y capacidad), arreglar ventas o cambiar oferta; aprendizajes a `aprendizajes/` | `/escalar`, `/auditoria` si algo no cuadra | CAC trimestral ≤ break-even y pipeline sano |

---

## 13. Ejemplo completo: Acme Automations (ficticia)

**Quién es.** Consultora de tres personas (el fundador vende y dirige; dos técnicos) que automatiza procesos de
administración en pymes de 10–80 personas de distribución, servicios técnicos y despachos profesionales en España.
Vende tres cosas: lectura de albaranes y facturas de proveedor con revisión humana y volcado al programa de gestión,
seguimiento automático de presupuestos, y un asistente interno que responde con la documentación de la empresa.

**Oferta principal.** Proyecto a precio cerrado de 6.000–15.000 € (media 9.000 € sin IVA), 50 % a la firma y 50 % a la
entrega, en 4–8 semanas. Mantenimiento opcional de 400 €/mes (supuesto: lo contrata el 60 % durante 12 meses de media,
con un 70 % de margen → +2.016 € por proyecto; **no se usa para decidir hasta tener 6 meses de datos**). Taller
in-company de 1.200 € para quien «aún no compensa» y para equipos que necesitan criterio.

**Oferta de entrada.** «Diagnóstico de horas manuales» web (6 minutos): el usuario elige hasta tres procesos y pone
volúmenes y minutos; la herramienta devuelve horas al año, coste, rango de ahorro con supuestos visibles (25–60 %
automatizable según el tipo de tarea, revisión humana restada, mantenimiento restado), payback en rango y un veredicto.
Si el payback base supera 18 meses o el ahorro neto no llega a 4.000 €/año: «Con estos números no te compensa
contratarnos. Esto es lo que puedes hacer tú» (plantilla y taller). Si hay caso: calendario para revisar el
diagnóstico en 30 minutos.

**Economía** (sección 3.3): contribución 3.382 € por proyecto; break-even 93 € por lead, 133 € por diagnóstico, 266 €
por cualificado, 444 € por llamada agendada, 592 € por llamada asistida, 1.184 € por propuesta; targets a la mitad.
Techo de capacidad: 2 propuestas investigadas por semana → ~4.950 €/mes.

**Arranque (semana 0).** Ficha con `topes.cambio_dia: 120`, `topes.total_dia: 150`, `crm.tipo: ghl`,
`mejoras_automaticas: off`, evento principal `DiagnosticoCompletado`; pipeline §16 en GHL; landing generada con
`paginas.py generar diagnostico`; `Lead` y `DiagnosticoCompletado` por navegador y servidor con `event_id` común;
etapas por CAPI de CRM desde GHL con «Allow Multiple»; una regla de protección (pausar y avisar si en 3 días gasta
300 € sin un solo lead: con 6–7 leads esperados, cero por azar es casi imposible, así que es una rotura); SLA de 5
minutos con mensaje automático por WhatsApp y email.

**Campaña.** `ES_LEADS_ADQ_HV` → `BROAD-A+_DIAGNOSTICO` a 100 €/día (3.000 €/mes). Primer lote de 4 conceptos:

| Anuncio | Ángulo | Concepto | Formato |
|---|---|---|---|
| `20261116_albaranes-lunes_demo-albaran-erp_demo_h1` | Albaranes | Foto del albarán → línea en el programa → revisión | Demo 35 s |
| `20261116_chatgpt-no-basta_que-si-que-no_founder_h1` | Objeción ChatGPT | «Lo que ChatGPT sí puede hacer en tu empresa (y lo que no)» | Fundador 50 s |
| `20261116_presupuestos-perdidos_cronometro_estatico_h1` | Presupuestos | «De la petición al PDF: 2 días frente a 15 minutos» | Estático |
| `20261116_cuanto-cuesta_rangos-reales_carrusel_h1` | Precio | «Cuánto cuesta automatizar un proceso en una pyme: rangos reales» | Carrusel |

**Mes 1 (simulación base, CPL 45 €).** 67 leads → 47 diagnósticos (64 € cada uno) → 23 cualificados (129 €) →
14 llamadas (214 €) → 10,5 asistidas (286 €) → 5,3 propuestas (571 €) → **1,8 proyectos**, CAC 1.633 € (por debajo del
target de 1.691 €). Contribución 6.215 € → **3.125 € tras anuncios y el 3 % de recargo**. Rango honesto con
`prevision`: de 0,7 a 4,1 proyectos según los supuestos y un 16 % de probabilidad de cero proyectos en el mes por puro
azar.

**Lo que pasa de verdad (ilustrativo).** En la semana 3, el anuncio de precio tiene el CPL más alto (61 €) pero el 55 %
de sus diagnósticos cualifica; el de la objeción ChatGPT, el más barato (32 €), solo cualifica el 20 %. Coste por
cualificado: 111 € frente a 160 €. Acme no apaga el de ChatGPT por CPL: lo reescribe para filtrar («si sois menos de 5,
esto no es para vosotros») y duplica la apuesta por el ángulo de precio con un vídeo del fundador. En la semana 5 el
show es del 62 %: las citas se daban a 6–8 días. Acme corta el calendario a 72 h y añade un vídeo de confirmación; el
show sube al 78 % en dos semanas (cohortes pequeñas: lo confirma en la semana 9).

**Mes 3 (decisión trimestral).** Con 9.000 € invertidos, la base esperada es 5,5 proyectos (3–9 por azar). Si sale en
ese rango y el coste por llamada asistida se ha mantenido por debajo del target, Acme valora subir a 4.500 €/mes:
`prevision` dice que ese escalón da +0,6 proyectos al mes con un CAC marginal de ~2.500 € (por debajo del break-even de
3.382 €, por encima del target) y que el beneficio crece de 3.125 € a 3.620 €. Es rentable, pero se acerca al techo de
capacidad de ~4.950 €/mes. La decisión correcta: subir a 4.500 € **y** cobrar el diagnóstico profundo (piloto de 1.500 €
deducible) a los leads de «caso dudoso» para no investigar propuestas que no cierran. Conversion Leads no se prueba
todavía: con ~7–8 cualificados por semana no llega al mínimo práctico de la sección 6.1.

**Lo que Acme registra.** Cada cambio en `change-log.md` con métrica y fecha de evaluación; cada pieza en
`registro-creativo.csv` con ángulo, concepto y veredicto; las tasas reales en la ficha; los aprendizajes («el ángulo de
precio cualifica el doble») en `aprendizajes-creativos.md`.

---

## 14. Cuando la consultora gestiona Meta para sus clientes

Muchas consultoras de automatización acaban llevando también la captación de sus clientes: montan la respuesta
automática, el reparto de leads y la CAPI, y es natural que lleven los anuncios. Es un buen negocio si se hace con las
reglas de la [parte B del playbook de agencias](playbook-agencias-consultores.md) (onboarding, contrato, reporting y
decisiones) y con estas particularidades:

### 14.1 Onboarding (semanas 1–2)

- [ ] **Ficha con `relacion: cliente`**, su `tipo` real (una clínica es `local`; un despacho que vende con propuesta es
  `servicios-high-ticket`), sus topes y su ventana de atribución (`/cliente-nuevo`).
- [ ] **Activos del cliente, en su Business Portfolio y su dataset**; tú entras como partner. Si te vas, el aprendizaje
  se queda con él ([`/configurar-meta`](../../.claude/skills/configurar-meta/SKILL.md), situación «agencia»).
- [ ] **Encargo de tratamiento firmado** (RGPD, art. 28): vas a tocar los datos personales de sus leads en GHL, en la
  CAPI y en las audiencias. Sus avisos de privacidad y de cookies tienen que cubrir el píxel, la CAPI y las audiencias de
  lista ([04/09](../04-tracking-atribucion-medicion/09-privacidad-att-gdpr-consentimiento-aem.md)).
  **[OFFICIAL — regulador]**
- [ ] **Su embudo con sus etapas.** Para un cliente local (Clínica Sonrisa: `lead` → cita → asistió → tratamiento) no
  hace falta el §16 completo; para un cliente que vende con propuesta, sí.
- [ ] **La automatización que vendes es parte del servicio de anuncios:** respuesta en < 1 minuto, reparto, recordatorios
  y CAPI de CRM. Es lo que separa tu resultado del de una agencia que solo lleva campañas. **[STRONG INFERENCE]**
- [ ] **Economía del cliente** con `/economia` y su capacidad comercial: sin ellos no recomiendas presupuesto (regla del
  OS).
- [ ] **Servidor de GHL por sub-cuenta** (`ghl-<slug>` y `crm.servidor_mcp` en su ficha) y token de solo lectura para
  los informes ([`docs/agencias.md`](../../docs/agencias.md), [`docs/guias/ghl-meta.md`](../../docs/guias/ghl-meta.md) §1).

### 14.2 Reporting

`/informe-cliente` (con `gestor-cliente`) en tres bloques: Meta (inversión, coste por lead y por cualificado, estado de
aprendizaje), CRM (cualificados, citas, asistencias, ventas por anuncio con `ghl.py por-anuncio`, motivos de pérdida,
velocidad de respuesta del cliente medida en GHL) y economía (coste por venta frente al target, cash). Siempre con el
periodo, la ventana de atribución y qué cohortes aún no han madurado (`embudo.py cohortes`). El detalle de contrato,
KPI y cadencia está en la [parte B del playbook de agencias](playbook-agencias-consultores.md) §6.

### 14.3 Reglas de decisión con clientes

- **Si el cliente no responde en el SLA o no marca etapas, no hay diagnóstico de calidad posible:** primero proceso,
  luego presupuesto. Ponlo en el contrato.
- **Coste por cita estable y ventas a la baja** → reunión con quien vende en el cliente, no cambios de campaña.
- **No escales a un cliente más allá de su capacidad de atender** (sección 3.6 aplicada a su agenda).
- **Una regla de protección por cuenta** (`/reglas-automaticas`) y topes en su ficha: el día que algo se dispare con tu
  ordenador apagado, Meta lo frena.
- **Precio de tu servicio:** fijo mensual + puesta en marcha; evita cobrar por lead si no controlas su proceso
  comercial (incentiva leads baratos y malos). Más opciones en la parte B del playbook de agencias, §10.
  **[STRONG INFERENCE]**
- **Si el cliente usa el asistente que le construiste para responder a sus leads**, recuerda el aviso de IA del
  artículo 50 y el encargo de tratamiento (secciones 5.6 y 8.3): deja escrito en el contrato quién es el proveedor del
  sistema y quién el responsable de los datos.

---

## 15. Preguntas abiertas

- ¿Desde qué volumen semanal de `cualificado` mejora Conversion Leads a una campaña optimizada a
  `DiagnosticoCompletado` en consultoría B2B? No hay datos públicos; registra tus pruebas en `aprendizajes/`.
- Efecto real de la reserva dentro del formulario instantáneo sobre el show y el cierre en B2B.
- Efecto de la cobertura de Meta sobre la tasa de respuesta del outbound: sin estudio público fiable.
- Tasas típicas de propuesta→ganado en consultoras de automatización para pymes en España: sin fuente con metodología.
- ¿Admite Conversion Leads formularios web en tu cuenta? El Help Center dice que sí; la guía de developers del
  2026-10-27, que no. Y la misma guía mantiene los 200 leads al mes que el anuncio de 2025 eliminó.
- ¿Funciona el calendario embebido del formulario fuera de la app de Facebook y con HubSpot? La página oficial no lo
  aclara.
- ¿Se puede optimizar click-to-WhatsApp a leads con una cuenta española? El aviso oficial es genérico.
- Calendario regulatorio pendiente: el aplazamiento de Verifactu (anunciado, no publicado en el BOE), las bases del Bono
  IA y la nueva ley española de IA (el proyecto caducó con la disolución de las Cortes en octubre de 2026). Revísalo
  antes de usar cualquiera de estos temas en un anuncio.

## Fuentes

**De la base de conocimiento:** [05/01](../05-leadgen-high-ticket-crm/01-canales-captacion-comparativa.md) ·
[05/02](../05-leadgen-high-ticket-crm/02-instant-forms-a-fondo.md) ·
[05/03](../05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md) ·
[05/04](../05-leadgen-high-ticket-crm/04-integraciones-crm.md) ·
[05/05](../05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md) ·
[05/06](../05-leadgen-high-ticket-crm/06-high-ticket-funnels.md) ·
[05/07](../05-leadgen-high-ticket-crm/07-webinars-eventos-lanzamientos.md) ·
[05/08](../05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md) ·
[05/09](../05-leadgen-high-ticket-crm/09-sales-feedback-loop.md) ·
[05/10](../05-leadgen-high-ticket-crm/10-b2b-saas-local.md) · [13/01](../13-sistema-operativo/01-principios-de-razonamiento.md) ·
[13/05](../13-sistema-operativo/05-framework-testing-creativo.md) · [13/09](../13-sistema-operativo/09-presupuesto-pequeno-y-grande.md) ·
[08/08](../08-cuenta-politicas-seguridad/08-infoproductos-claims-ingresos.md) ·
[08/11](../08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md) ·
[11/10](../11-benchmarks-casos-expertos/10-espana-latam.md) · [00-ESTADO-ACTUAL-2026](../00-ESTADO-ACTUAL-2026.md).
Guías del producto: [`docs/guias/ghl-meta.md`](../../docs/guias/ghl-meta.md), [`docs/guias/capi.md`](../../docs/guias/capi.md).
Calculadora: `herramientas/economia.py` (`leadgen` y `prevision`).

**Externas (consultadas el 2026-11-09).** Las páginas del Help Center no muestran fecha: la indicada es la de lectura.

*Meta (oficial):*

- [About performance goals for lead ads](https://www.facebook.com/business/help/782657799338685) · leído 2026-11-09 ·
  oficial (CAPI obligatoria desde abril de 2026, web e instant forms, valor en leads)
- [Set up your CRM for qualified leads](https://www.facebook.com/business/help/279369167153556) · leído 2026-11-09 · oficial
- [Conversion leads integration](https://developers.facebook.com/documentation/ads-commerce/conversions-api/conversion-leads-integration) ·
  actualizado 2026-10-27 · developers (lead ID, subida diaria, 28 días, 1–40 %, 200 leads al mes)
- [More quality leads this Q5 with Meta's latest AI-enabled updates](https://www.facebook.com/business/news/more-quality-leads-this-q5-with-metas-latest-ai-enabled-updates) ·
  2025-10-30 · oficial (fin del mínimo mensual, email de trabajo)
- [Embedded appointment booking in instant forms](https://www.facebook.com/business/help/1743939330255391) · leído
  2026-11-09 · oficial
- [Higher intent forms](https://www.facebook.com/business/help/252352181957512) y
  [verificación del teléfono](https://www.facebook.com/business/help/898260175547909) · leídos 2026-11-09 · oficial
- [Mensajería en Europa](https://www.facebook.com/business/help/575610661605746) y
  [objetivo Leads con WhatsApp](https://www.facebook.com/business/help/447934475640650) · leídos 2026-11-09 · oficial
- [Descarga de leads (90 días)](https://www.facebook.com/business/help/734933888443065) · leído 2026-11-09 · oficial
- [Etiquetas de audiencia](https://www.facebook.com/business/help/706325895111530) · leído 2026-11-09 · oficial
- [Click attribution update](https://www.facebook.com/business/news/click-attribution) · 2026-03-03 · oficial; y
  [ajustes de atribución](https://www.facebook.com/business/help/460276478298895) · leído 2026-11-09 · oficial
- [Gen AI transparency in Meta's ads products](https://about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products/) ·
  2025-02-03, actualizado 2026-06-01 · oficial
- [Prohibited commercial practices (Advertising Standards)](https://transparency.meta.com/policies/ad-standards/deceptive-content/prohibited-commercial-practices/) ·
  registro de cambios de la norma comunitaria 2026-10-29 · oficial
- [Meta Business Agent](https://about.fb.com/news/2026/06/meta-business-agent/) · 2026-06-03 · oficial
- Eventos en secuencia, respuestas preferidas y agente de captación en formularios: artículos de Jon Loomer de
  2026-07-09, 2026-08-07 y 2026-10-06 en jonloomer.com · practitioner (sin documentación oficial)

*Regulación y estadística (UE y España):*

- [INE, Encuesta TIC en empresas 2025-T1 2026](https://ine.es/dyngs/Prensa/ETICCE20251T2026.htm) · 2026-10-22 · oficial
- [Eurostat, Use of artificial intelligence in enterprises](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Use_of_artificial_intelligence_in_enterprises) ·
  2025-12 · oficial
- [Reglamento (UE) 2026/1744 (Ómnibus Digital de IA)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng) · 2026-07-24 ·
  oficial; el Reglamento (UE) 2024/1689 (arts. 3.3, 4, 50 y 99)
- [EDPB, Guidelines 8/2020 on the targeting of social media users](https://www.edpb.europa.eu/documents/guideline/guidelines-82020-on-the-targeting-of-social-media-users_en) ·
  2021-04 · oficial
- [AEPD, resumen de obligaciones y recomendaciones para la IA generativa](https://www.aepd.es/guias/sumario-recomendaciones-iag-aepd.pdf) ·
  2026-01 · oficial; [orientaciones sobre IA agéntica](https://www.aepd.es/prensa-y-comunicacion/notas-de-prensa/la-agencia-publica-unas-orientaciones-sobre-inteligencia) ·
  2026-02-18 · oficial
- [Acelera Pyme, Kit Digital](https://www.acelerapyme.gob.es/kit-digital) y
  [Kit Consulting](https://www.acelerapyme.gob.es/kit-consulting) · consultados 2026-11-09 · oficial; Órdenes
  TDF/38/2026 y TDF/39/2026 (BOE del 2026-01-28)
- [Plan IA360 (PDF)](https://www.lamoncloa.gob.es/presidente/actividades/Documents/2026/20260920%20Plan%20IA360.pdf) ·
  2026-09-20 · oficial
- [RDL 15/2025 (Verifactu)](https://www.boe.es/boe/dias/2025/12/03/pdfs/BOE-A-2025-24446.pdf) · 2025-12-03 · oficial;
  [nota de Hacienda sobre el aplazamiento](https://www.hacienda.gob.es/sgt/gabsehacienda/nota-informativa-verifactu.pdf) ·
  2026-10-05 · oficial; [AEAT, Verifactu](https://sede.agenciatributaria.gob.es/Sede/iva/sistemas-informaticos-facturacion-verifactu.html) ·
  2026-11-03 · oficial
- [RD 238/2026 (factura electrónica B2B)](https://www.boe.es/boe/dias/2026/03/31/pdfs/BOE-A-2026-7295.pdf) · 2026-03-31 ·
  oficial; [Orden HAC/1028/2026](https://www.boe.es/boe/dias/2026/10/05/pdfs/BOE-A-2026-20587.pdf) · 2026-10-05 · oficial
- [Memoria de impacto del real decreto de factura electrónica](https://technical-regulation-information-system.ec.europa.eu/es/notification/25464/text/I/ES) ·
  2024-01-30 · oficial (cita cifras de terceros)

*Estudios, encuestas y benchmarks:*

- [Metadata, B2B Benchmark Report 2026](https://www.metadata.io/benchmark/metadata-b2b-benchmark-report-2026.pdf) ·
  2026-09 · vendor con metodología publicada
- [Gartner: 69 % de los compradores B2B validan con un comercial lo que les dice la IA](https://www.gartner.com/en/newsroom/press-releases/2026-05-20-gartner-survey-finds-sixty-nine-percent-of-b-two-b-buyers-turn-to-sales-reps-to-validate-ai-generated-insights) ·
  2026-05-20 · encuesta de analista
- [Forrester: B2B buyers demand proof, not promises (vía Digital Commerce 360)](https://www.digitalcommerce360.com/2025/10/28/forrester-b2b-buyers-demand-proof-not-promises/) ·
  2025-10-28 · analista
- [Cicek, Gursoy y Lu: mencionar «IA» reduce la intención de compra (nota de la universidad)](https://news.wsu.edu/press-release/2024/07/30/using-the-term-artificial-intelligence-in-product-descriptions-reduces-purchase-intentions/) ·
  2024-07-30 · estudio académico
- [Humlum y Vestergaard, NBER WP 33777](https://econpapers.repec.org/RePEc:nbr:nberwo:33777) · 2025 · estudio académico
- [Fed de St. Louis, impacto de la IA generativa en la productividad](https://www.stlouisfed.org/on-the-economy/2025/feb/impact-generative-ai-work-productivity) ·
  2025-02 · estudio
- [Brynjolfsson, Li y Raymond, QJE 2025](https://econpapers.repec.org/RePEc:oup:qjecon:v:140:y:2025:i:2:p:889-942.) · 2025 ·
  estudio académico
- [METR, ensayo con desarrolladores (vía InfoWorld)](https://www.infoworld.com/article/4020931/ai-coding-tools-can-slow-down-seasoned-developers-by-19.html) ·
  2025-07 · ensayo controlado (muestra pequeña)
- [HBR, The Short Life of Online Sales Leads](https://hbr.org/2011/03/the-short-life-of-online-sales-leads) · 2011-03 ·
  estudio
- [RevenueHero, Lead response times report](https://www.revenuehero.io/resources/lead-response-times-report) · sin
  fecha · vendor
- [Reply.io, no-shows de demos](https://reply.io/fight-demo-no-shows/) · sin fecha · vendor (datos internos)
- [Proposify, State of Proposals 2026](https://www.proposify.com/state-of-proposals-2026) · 2026 · vendor
- [ConvertFlow, quiz funnel benchmark](https://www.convertflow.com/benchmark-reports/lead-generation-quiz-funnel-benchmark-september-2026) ·
  2026-09 · vendor; [Interact, quiz conversion rate report](https://www.tryinteract.com/blog/quiz-conversion-rate-report/) ·
  2026-09 · vendor
- [Dreamdata, la regla 95:5](https://dreamdata.io/blog/the-95-5-rule-john-dawes) · 2021+ · heurística académica
- [6sense 2025 (vía CustomerThink)](https://customerthink.com/research-round-up-6sense-study-provides-critical-insights-on-b2b-buyer-behavior/) ·
  2025-11 · vendor (encuesta)
- Asistencia a webinars: ON24 (datos de 2025, leído en fuente secundaria) y Livestorm 2026 · vendors

*Cifras muy citadas que no uso por falta de fuente primaria localizable:* «21 o 100 veces más si respondes en 5
minutos», «+391 % en el primer minuto», «20 % de cierre medio de propuestas», «30–50 % de visitante a lead con
scorecards», «+2 puntos de ausencias por cada día de espera».
