---
name: iman-de-leads
description: "Construye el imán de leads de la oferta de entrada: diagnóstico o calculadora que da valor y precualifica, con preguntas, supuestos con fuente, fórmulas, veredicto honesto (no compensa, empieza por un proceso, hay proyecto) y valor del evento, probado con escenarios. Qué oferta elegir es de /oferta; publicarlo, de /construir-landing."
argument-hint: "<cliente> [diagnostico|calculadora|auditoria|test|demo] [<proceso o tema>]"
---

# /iman-de-leads

Entrada: `$ARGUMENTS`. Construye la pieza con la que una consultora, una agencia de IA y automatización o un SaaS capta
leads que valen la pena: un diagnóstico interactivo (o una variante) que da valor aunque nunca te compren, pide un dato
que solo aporta quien tiene el problema, enseña el cálculo con sus supuestos y dice la verdad. También dice «no nos
contrates» cuando los números no salen, y termina en la reserva de la llamada solo si hay caso.

Reparto con otras skills:
- **Qué oferta de entrada usar** (y la oferta principal) lo decide `/oferta`.
- **Qué embudo** (landing con diagnóstico, formulario instantáneo, webinar, mensajería), `/disenar-funnel`.
- **Esta skill** convierte la oferta de entrada en preguntas, cálculo, veredicto y valor del evento, y deja el config
  probado.
- **Las páginas** las genera y valida `/construir-landing`.
- **En formulario instantáneo**, las preguntas pasan a `/formulario-instantaneo`.
- **Si la entrada es un taller**, `/webinar`.

No escribe en Meta, GHL ni Stripe y no publica nada.

- **Marco:**
  - `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` (§4.1 las cinco reglas de una oferta de entrada,
    §4.2 catálogo, §4.3 cómo construir una calculadora honesta, §5.3 embudo B, §8.7 qué no decir, §10 medición);
  - `meta-ads-kb/03-creatividad/09-oferta-y-diagnostico-ad-oferta-landing-ventas.md` (§3 message match, §4 diseño de
    oferta);
  - `meta-ads-kb/03-creatividad/15-landing-pages-y-cro-trafico-meta.md` (§4.2 formulario web y multipaso);
  - `meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md`;
  - `meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md` (valor y cualificación);
  - `meta-ads-kb/08-cuenta-politicas-seguridad/11-copy-persuasivo-compliant-patrones.md`;
  - `meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`.

  En los pasos, «playbook consultoras §4.3» es el primero de la lista y «03/15 §4.2» significa área 03, archivo 15,
  sección 4.2.
- **Agentes:**
  - `especialista-funnel`: tipo de imán, preguntas, flujo y momento de pedir los datos;
  - `analista-cuantitativo`: supuestos, umbrales y valor del evento;
  - `estratega-creativo`: que la promesa del imán y la del anuncio sean la misma;
  - `revisor-politicas`: textos del resultado y de los veredictos;
  - `revisor-estrategia`: segunda opinión si el imán es nuevo para el cliente;
  - `gestor-cliente`: el OK del cliente si eres agencia.
- **Herramientas:**
  - `paginas.py probar`, que calcula los escenarios con las mismas fórmulas que la página;
  - `economia.py leadgen`, para la contribución por venta;
  - `embudo.py cohortes` y `ghl.py por-anuncio`, para recalibrar con datos.
- **Lee:**
  - la ficha: oferta y precio, economía, capacidad, `definicion_cualificado`, `umbral_no_compensa` si existe, y
    afirmaciones aprobadas;
  - `planes/*_oferta.md` y `planes/*_funnel.md`;
  - `investigacion/`: voz del cliente, matriz de ángulos y competencia;
  - casos medidos con permiso (`/casos-y-creadores`);
  - el formato del config: `plantillas/paginas/README.md` («diagnostico» y «Fórmulas»);
  - el ejemplo completo: `plantillas/paginas/ejemplos/acme-embudo.json`.

Sin ficha, primero `/cliente-nuevo`. Sin saber qué cuesta el proyecto más pequeño, no hay umbral honesto: pídelo.

## Pasos

1. **Elige el tipo de imán** (playbook consultoras §4.2) con `especialista-funnel`:

   | Si… | Imán |
   |---|---|
   | Vende automatización a medida (lo normal) | Diagnóstico de horas manuales (por defecto) |
   | Vende 1–2 soluciones muy concretas | Calculadora de un solo proceso (facturas, presupuestos, citas) |
   | El ticket es ≥ 15.000 € y hay pocos leads | Auditoría con requisitos visibles (tamaño, decisor) |
   | Hay volumen alto o es para retargeting | Test de madurez; nunca como única entrada |
   | Lee documentos o hace presupuestos | Demo con sus documentos, sin datos personales |
   | El mercado está frío | Taller → `/webinar` |

   Comprueba las cinco reglas de §4.1:
   - da valor aunque no compren;
   - exige un dato que solo tiene quien sufre el problema;
   - lleva supuestos y rango;
   - puede decir que no;
   - lleva a la llamada sin forzarla.

   Si alguna falla, cámbialo antes de seguir.
2. **Escribe las preguntas** (4–7 `[HYPOTHESIS]`; cada una de más baja la finalización):
   - la primera, de opciones y fácil: con ella arranca el hero de la landing (`media.tipo: arranque`) y es la misma
     pregunta que puede hacer el anuncio;
   - tamaño o encaje (filtra sin preguntar el presupuesto);
   - los procesos como `grupo` (qué tarea, cuántas personas, horas por semana, tipo de trabajo), que es el dato que solo
     da quien tiene el problema;
   - dónde están los datos o las herramientas (encaje técnico);
   - plazo o quién decide.

   Nada de preguntas sensibles: ingresos, salud ni datos de sus clientes (03/15 §4.2). Las palabras de las opciones
   salen de la voz del cliente, no de la jerga de la consultora.
3. **Fija los supuestos** con `analista-cuantitativo`.
   - Cada uno lleva valor conservador, `explicacion` y `fuente`.
   - Valores de partida del playbook consultoras §4.3:
     - parte automatizable **por tipo de tarea**, entre el 25 y el 60 %, nunca 100 % `[HYPOTHESIS]`;
     - coste por hora cargado (sueldo más cotizaciones), con su fuente;
     - 46 semanas;
     - revisión humana o adopción;
     - mantenimiento anual;
     - inversión típica.
   - Lee la tabla de evidencia de §4.3 antes de poner un porcentaje alto: los ahorros grandes solo se sostienen en
     tareas concretas, repetitivas y medidas.
   - El **umbral** («ahorro neto mínimo para que tenga sentido un proyecto») sale del proyecto más pequeño y del
     retorno máximo aceptable. Enséñalo con `editable: false`, y también la inversión y el mantenimiento: son
     precios tuyos, no datos del cliente, y si se pudieran bajar cualquiera «compraría» el sí.
   - Las cifras en dinero van en la moneda de la ficha (`--cliente <slug>` al generar, o `sitio.moneda`).
4. **Escribe los cálculos y el veredicto** con la estructura de §4.3:
   - horas al año → coste → automatizable → ahorro neto → meses de retorno.
   - Niveles, en este orden:

     | `tono` | Cuándo | Qué dice y ofrece |
     |---|---|---|
     | `bajo` | Ahorro neto bajo el umbral o retorno de más de 18 meses | «Hoy no te compensa contratarnos». Algo útil a cambio: guía, plantilla, «vuelve cuando el volumen se duplique» |
     | `medio` | 12–18 meses | «Empieza por un proceso: {tarea_top}». Llamada |
     | `alto` | El resto | «Hay proyecto». Llamada, con el rango `{x_min}`–`{x_max}` |

   - Rango de incertidumbre en el resultado principal (`incertidumbre: 0.25`).
   - Habla de horas recuperadas, nunca de despidos ni de «sustituir a una persona» (playbook consultoras §4.3 y §8.7).
5. **Pon el valor del evento** con `analista-cuantitativo`.
   - `valor_evento` por nivel = contribución por venta (`economia.py leadgen`) × probabilidad de ganar desde ese nivel
     `[HYPOTHESIS]` hasta tener datos.
   - Es el valor **esperado del lead**, nunca el ahorro del cliente (contrato §16).
   - `cualificado.activo` se queda en `false` salvo que la ficha diga que un nivel ya es «cualificado»: lo normal es
     que lo marque el comercial.
6. **Decide cuándo pedir los datos** (`captura`) con `especialista-funnel`:
   - **`antes`** (por defecto): preguntas → datos → resultado. Con el sistema multipaso, que empieza por lo fácil y pide
     el contacto al final (03/15 §4.2), es el que más leads con datos completos deja.
   - **`despues`**: resultado sin datos → «revisemos tu resultado» → datos y reserva. Da más valor gratis y crea una
     audiencia útil: `DiagnosticoCompletado` sin `Lead` (vio el resultado y no pidió llamada). Úsalo si el CPL está
     bien y faltan llamadas de calidad, o en retargeting.

   El formulario lleva email, nombre, empresa y teléfono si la venta es por llamada (03/15 §4.2), y las casillas de
   comunicaciones separadas por canal, siempre opcionales.
7. **Prueba con escenarios.**
   - Escribe al menos tres, uno por nivel y sacados de clientes reales o del ICP, más uno límite: el caso que **no**
     debe salir «hay proyecto».
   - Ejecuta `python3 -I herramientas/paginas.py probar --config <json>` hasta que cada uno dé su `espera_nivel`.
   - Si uno falla, ajusta los umbrales o los supuestos con su porqué, nunca las respuestas.
   - Apunta el resultado de `probar` en el plan.
8. **Revisa los textos** con `revisor-politicas` (08/11 §3.4, coaching y consultoría de negocio):
   - sin «ahorrarás», «garantizado» ni cifras de casos sin permiso;
   - el aviso de que es una estimación, visible.

   Si eres agencia, el cliente aprueba umbrales y textos (`gestor-cliente`).
9. **Entrega:**
   - `clientes/<slug>/planes/<AAAA-MM-DD>_iman-<tema>.md`:
     - tipo e hipótesis;
     - preguntas y por qué cada una;
     - supuestos con fuente;
     - veredictos y umbral;
     - valor por nivel y cómo se calculó;
     - escenarios y salida de `probar`;
     - qué medir;
   - `clientes/<slug>/planes/<AAAA-MM-DD>_iman-<tema>.json`: el config con `paginas.diagnostico` (y el `hero` de la
     landing si ya lo tienes), validado por `probar`.

   Siguiente:
   - `/construir-landing <cliente> todas --config <ese json>`;
   - para los anuncios, `/brief-creativo` con la misma promesa y la primera pregunta como gancho.
10. **Recalibra con datos** cuando haya 30–50 leads, o al mes si hay menos (principios de razonamiento §8):
    - % `diagnostico` → `cualificado` → llamada → ganado por nivel, con `embudo.py cohortes` o `ghl.py por-anuncio`;
    - si «hay proyecto» no cierra más que «empieza por un proceso», los umbrales no discriminan: súbelos;
    - si casi todo sale «no compensa», mira si el anuncio atrae al tamaño equivocado antes de tocar el cálculo.

    Actualiza `valor_evento` y anota el aprendizaje en la ficha.

## Reglas

- **Nunca inventes cifras, casos ni porcentajes.** Un supuesto sin fuente se marca `[HYPOTHESIS]` en el plan y se
  enseña como orientativo en la página.
- El resultado es una estimación con rango y supuestos visibles y editables, no una promesa.
- Ninguna respuesta del diagnóstico es un dato sensible, y los ejemplos usan empresas ficticias.
