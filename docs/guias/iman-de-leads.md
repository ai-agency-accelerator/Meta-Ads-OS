# Imán de leads: un diagnóstico que da valor y precualifica

Para quién: consultoras y agencias de IA y automatización, y SaaS, que venden proyectos a medida a pymes (varios miles
de euros, ciclo de semanas).

Qué consigues: una oferta de entrada que la gente quiere hacer aunque nunca te compre. Calcula con sus datos cuántas
horas y cuánto dinero se le van en tareas repetitivas, enseña los supuestos y le dice la verdad:
- **«hoy no te compensa contratarnos»**;
- **«empieza por un proceso»**;
- **«hay proyecto»**.

Solo en los dos últimos casos termina en la reserva de una llamada. A ti te llegan menos curiosos, llamadas con los
números ya hechos y una señal para Meta que distingue un lead bueno de uno cualquiera.

La skill es **`/iman-de-leads <cliente>`**: diseña el imán y deja el config probado. Las páginas las genera
**`/construir-landing`** (guía: `docs/guias/construir-landing.md`). Las etiquetas `[OFFICIAL META]`, `[EMPIRICAL]`,
`[STRONG INFERENCE]`, `[HYPOTHESIS]` y `[CONTESTED]` son las de la base de conocimiento.

```
/oferta (qué oferta de entrada) ─▶ /iman-de-leads (preguntas, supuestos, cálculo, veredicto, valor)
        ─▶ paginas.py probar (escenarios) ─▶ /construir-landing (páginas) ─▶ tú publicas ─▶ /landing
anuncio ─▶ landing ─▶ diagnóstico ─▶ datos (Lead) ─▶ resultado (DiagnosticoCompletado) ─▶ reserva (Schedule)
```

---

## 1. ¿Diagnóstico u otro imán?

El diagnóstico de horas manuales es la entrada por defecto para una consultora de automatización. No es la única:

| Imán | Cuándo | Riesgo |
|---|---|---|
| **Diagnóstico de horas manuales** (5–8 min) | Vendes automatización a medida | Que el resultado se lea como promesa: rango y supuestos a la vista |
| **Calculadora de un proceso** | Vendes 1–2 soluciones concretas (facturas, presupuestos, citas) | Atraer al que solo quiere precio |
| **Auditoría** | Ticket ≥ 15.000 € y pocos leads | Coleccionistas de auditorías: pide tamaño y decisor |
| **Test de madurez** | Volumen alto o retargeting | Leads de baja intención: nunca como única entrada |
| **Demo con sus documentos** | Lees documentos o haces presupuestos | Datos personales en los documentos: versiones sin datos |
| **Taller** | Mercado frío | Asistencia baja: va por `/webinar` |

Fuente: `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §4.2. Los datos de conversión de quizzes y
calculadoras que circulan son de quien vende la herramienta y miden captación, no ventas `[EMPIRICAL]` débil. Mide tú
el % de diagnósticos que llegan a cualificados.

Antes de seguir, el imán tiene que cumplir las cinco reglas del §4.1:
1. Da valor aunque nunca te compren.
2. Exige un dato que solo aporta quien tiene el problema.
3. Lleva supuestos explícitos y rango, no una cifra mágica.
4. Puede decir que no.
5. Lleva a la llamada sin forzarla.

## 2. Las preguntas

Entre 4 y 7 `[HYPOTHESIS]`. El ejemplo de Acme (`plantillas/paginas/ejemplos/acme-embudo.json`) usa cuatro:

| # | Pregunta | Tipo | Para qué |
|---|---|---|---|
| 1 | ¿Cuántas personas trabajáis? | Opciones | Encaje. Es fácil y va en el hero de la landing: un toque y ya está dentro |
| 2 | ¿Qué tareas repetitivas os quitan más tiempo? (tarea, personas, horas por semana, tipo de trabajo) | Grupo, hasta 5 | El dato que solo tiene quien sufre el problema |
| 3 | ¿Dónde está la información que usan? | Opciones | Encaje técnico: nube, mezcla o papel |
| 4 | ¿Cuándo te gustaría tenerlo resuelto? | Opciones | Urgencia, para la llamada |

- **La primera pregunta, también en el anuncio.** «¿Cuántas horas se le van a tu equipo en copiar y pegar?» es el
  gancho del anuncio, el titular de la landing y el arranque del diagnóstico (*message match*,
  `meta-ads-kb/03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md` §3).
- **Las opciones, con las palabras del cliente** (de `/voz-cliente`), no con las tuyas.
- **Nada sensible:** ni ingresos, ni salud, ni datos de sus clientes
  (`meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` §4.2).

## 3. Supuestos y cálculo

La estructura es la del playbook consultoras §4.3:

```
horas recuperables/año = Σ (personas × horas/semana × parte automatizable del tipo de tarea)
                         × encaje de las herramientas × adopción × 46 semanas
coste recuperable/año  = horas recuperables × coste por hora
ahorro neto/año        = coste recuperable − mantenimiento
meses de retorno       = inversión típica / (ahorro neto / 12)
```

Cada supuesto se ve debajo del resultado y dice de dónde sale. Los del cliente (coste por hora, semanas, adopción) se
pueden cambiar y todo se recalcula al momento; la inversión, el mantenimiento y el umbral, no (`"editable": false`).
En los campos de número, la persona escribe como quiera: «1.200», «1.500,50», «0,8». En el ejemplo de Acme `[HYPOTHESIS]`:

| Supuesto | Valor | Por qué |
|---|---|---|
| Parte automatizable por tipo | 60 % copiar datos · 50 % emails · 50 % informes · 25 % decidir | Dentro del 25–60 % de la regla (§4.3): nunca 100 %. Los ahorros altos solo se sostienen en tareas concretas y repetitivas (tabla de evidencia) |
| Encaje de herramientas | 100 % nube · 75 % mezcla · 45 % papel | Sin datos accesibles hay que construir antes de automatizar |
| Adopción | 80 % | Excepciones, revisión humana, adaptación |
| Coste por hora | 28 € | Perfil administrativo con cotizaciones; pon el tuyo |
| Semanas | 46 | Vacaciones, festivos y ausencias |
| Mantenimiento | 1.200 €/año, **no editable** | Servidores, licencias y ajustes |
| Inversión típica | 9.000 €, **no editable** | El proyecto medio de Acme (playbook §3.3) |
| Umbral | 4.000 €/año, **no editable** | Proyecto más pequeño (6.000 €) a 18 meses como mucho |

**Lo que dice la evidencia:** a nivel de puesto, la IA ahorra poco (≈ 3 % del tiempo en el estudio danés con 25.000
trabajadores). En tareas concretas y medidas, sí se nota (+15 % de consultas resueltas por hora en atención al
cliente). La percepción exagera el ahorro `[EMPIRICAL]` (playbook §4.3). Por eso el cálculo va por tarea y con rango,
nunca por puesto, y habla de **horas recuperadas, no de despidos**.

## 4. El veredicto honesto

| Nivel | Cuándo (Acme) | Título | Qué ofrece |
|---|---|---|---|
| `bajo` | Ahorro neto < umbral o retorno > 18 meses | «Hoy no te compensa contratarnos» | Una guía para empezar por su cuenta; «prefiero comentarlo igualmente» como segundo botón |
| `medio` | Retorno de 12–18 meses | «Empieza por una sola tarea: {la que más horas come}» | Llamada de 30 minutos |
| `alto` | Retorno ≤ 12 meses | «Hay proyecto: merece la pena estudiarlo» | Llamada, con el rango de coste en el texto |

- **El nivel `bajo` es lo que te diferencia.** Ahorra llamadas inútiles, y quien recibe un «no» honesto vuelve cuando
  crece `[HYPOTHESIS]` (playbook §4.1, regla 4). Si no hay nivel `bajo`, `generar` avisa.
- **El umbral, la inversión y el mantenimiento no se pueden editar en la página.** Así nadie consigue el «sí» bajando
  la inversión.
- **El resultado es una estimación con rango** (±25 % en el ejemplo) y lleva el aviso «no es una promesa de
  resultados». Los textos pasan por `revisor-politicas`
  (`meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md` §3.4).

## 5. El valor del evento

`DiagnosticoCompletado` lleva `value` = **valor esperado del lead**: lo que vale de media un diagnóstico de ese nivel
para tu negocio. **Nunca** el ahorro del cliente (contrato §16).

En Acme (playbook §3.3), una venta deja 3.382 € de contribución, y un diagnóstico completado vale de media unos 133 €:
- contribución × diagnóstico→cualificado × llamada × show × propuesta × ganado;
- 3.382 € × 0,5 × 0,6 × 0,75 × 0,5 × 0,35 ≈ 133 €.

Si suponemos que el 20 % sale `bajo`, el 40 % `medio` y el 40 % `alto`, y que `alto` cierra 2,3 veces más que `medio`:

| Nivel | `valor_evento` | P(ganar) implícita |
|---|---|---|
| `bajo` | 0 € | ~0 |
| `medio` | 100 € | ~3 % |
| `alto` | 230 € | ~7 % |

Todo `[HYPOTHESIS]` hasta que tengas cierres por nivel. La contribución sale de `economia.py leadgen` (`/economia`).

Con el volumen de una consultora pequeña no vas a optimizar por valor: hacen falta unas 100 conversiones en 14 días y
al menos 5 valores distintos `[OFFICIAL META]`
(`meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md` §5). Pero el valor te sirve para medir
qué anuncio trae diagnósticos buenos.

`LeadCualificado` **no** se dispara solo por defecto: la cualificación la marca el comercial en GHL. Actívalo
(`cualificado.activo`) solo si la definición de «cualificado» de la ficha es exactamente un nivel del diagnóstico.

## 6. ¿Datos antes o después del resultado?

| `captura` | Recorrido | Cuándo |
|---|---|---|
| `antes` (por defecto) | preguntas → datos → resultado | Lo normal: empieza por lo fácil y pide el contacto al final (03/15 §4.2) y deja más leads con datos completos. `Lead` y `DiagnosticoCompletado` salen a la vez |
| `despues` | preguntas → resultado → datos para la llamada | Si quieres dar el resultado gratis y quedarte solo con quien quiere hablar. Crea una audiencia útil: `DiagnosticoCompletado` sin `Lead` |

## 7. Probarlo antes de publicar

Escribe en el config al menos un escenario por nivel, más uno límite (el que **no** debe salir «hay proyecto»):

```bash
python3 -I herramientas/paginas.py probar --config clientes/acme/planes/2026-11-10_iman-horas.json
```

```
✓ Pequeña, una tarea ligera: nivel bajo (esperado: bajo), valor del evento 0. … ahorro_neto = -400; retorno_meses = —
✓ Mediana, dos tareas: nivel medio (esperado: medio), valor del evento 100. … ahorro_neto = 6900; retorno_meses = 15,65
✓ Equipo de operaciones: nivel alto (esperado: alto), valor del evento 230. … ahorro_neto = 28800; retorno_meses = 3,75
```

Si uno no da lo esperado, cambia los umbrales o los supuestos y apunta por qué; nunca cambies las respuestas para que
cuadre. `generar` repite la prueba y avisa si algo cambia.

## 8. Medir y recalibrar

Con 30–50 leads, o al mes si hay menos (`meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md` §8):
- **Tasas por nivel:** % `diagnostico` → `cualificado` → llamada → ganado, con `embudo.py cohortes` y
  `ghl.py por-anuncio`.
- **Si «hay proyecto» no cierra más que «empieza por un proceso»,** los umbrales no separan: súbelos.
- **Si casi todo sale «no compensa»,** mira primero el anuncio: quizá atrae empresas demasiado pequeñas.
- **Actualiza `valor_evento`** con los cierres reales y apunta el aprendizaje en la ficha.
- **Datos agregados y anónimos** («en 40 diagnósticos de distribuidoras, la tarea que más horas come es…») sirven como
  ángulo y prueba (playbook §4.3).

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `generar` dice «Variable desconocida» | Una fórmula usa un id que no existe o está mal escrito | Mira el id en preguntas, supuestos o cálculos anteriores (los cálculos van en orden) |
| «… es un grupo» | Usas una pregunta de tipo grupo como número | Dentro de `suma(grupo, …)`, `media`, `cuenta` o `mayor` |
| «… es una palabra reservada» | Un id es `y`, `o`, `no`, `min`, `max`… | Cambia el id |
| El resultado sale «—» | División por 0 o un texto en una cuenta | Protege con `max(x, 0)` o `si(…)`; es lo que pasa a propósito con ahorro neto ≤ 0 |
| Un escenario sale de otro nivel | Umbrales o supuestos | `probar`; ajusta y apunta el porqué |
| Casi nadie termina | Demasiadas preguntas o una difícil al principio | Quita preguntas; deja la fácil primero |

## Qué no está verificado (2026-11-10)

- **Los porcentajes automatizables por tipo de tarea, el coste por hora y la adopción del ejemplo:** son supuestos de
  partida `[HYPOTHESIS]`. Sustitúyelos por los de tus proyectos medidos.
- **El efecto en conversión de decir «no te compensa»:** no hay datos independientes `[HYPOTHESIS]`. El efecto sobre el
  filtro es una inferencia razonable `[STRONG INFERENCE]` (playbook §4.1).
- **Cuántas preguntas aguanta el tráfico frío de Meta antes de abandonar:** el rango de 4–7 es orientativo
  `[HYPOTHESIS]`.
