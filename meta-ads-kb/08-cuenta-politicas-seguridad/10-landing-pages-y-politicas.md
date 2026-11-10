# Landing pages y políticas: funcionalidad, calidad, coherencia, cloaking y embudos de infoproductos

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: qué revisa Meta en el destino del anuncio, reglas oficiales (Relevance, Spam, checklist, dominios restringidos), páginas legales, formularios de Lead Ads, impacto de la landing en rechazos y re-revisiones, embudos de VSL, webinar y aplicación high-ticket; checklist de landing compliant.

## TL;DR

- **El destino forma parte del anuncio.** Meta revisa "Ad destination (where an ad directs people…)" junto con el texto, la creatividad y el targeting, y puede re-revisar en cualquier momento. **[OFFICIAL META]** ([S08-034])
- **Tres reglas de Relevance:**
  1. el anuncio representa claramente a la empresa o producto;
  2. todos los componentes se relacionan con la oferta;
  3. **lo que se anuncia debe coincidir con la landing**.

  **[OFFICIAL META]** ([S08-001])
- **Checklist oficial de la web:**
  - funciona correctamente;
  - sin contenido sexual, chocante, **engañoso** o **disruptivo** (pop-ups);
  - **volumen de publicidad no desproporcionado** respecto al contenido;
  - **accesible y relevante** para el anuncio.

  **[OFFICIAL META]** ([S08-027])
- **Prohibido (Spam):**
  - **cloaking**;
  - enlaces que prometen una cosa y entregan otra;
  - **redirecciones engañosas** (tras captcha o "clic aquí" cambia de dominio, o redirige solo);
  - funcionalidad falsa (botón de play que no reproduce);
  - pop-ups trampa al intentar salir, clickjacking;
  - **suplantación de dominio o marca** (typosquatting);
  - like/share-gating.

  **[OFFICIAL META]** ([S08-069])
- **Dominios restringidos:** si Meta identifica un dominio como infractor o sospechoso (por feedback o por **asociación con cuentas deshabilitadas por política o riesgo de pago**), **rechaza todos los anuncios que lleven a él durante 60 días**, plazo renovable si sigue la actividad. **[OFFICIAL META]** ([S08-030])
- **En infoproductos, la landing es el sitio donde más claims de ingresos se cuelan** (VSL, testimonios, capturas, contadores). Un anuncio "limpio" hacia una landing con "factura 10k/mes" se rechaza, o se aprueba y cae al escalar. **[STRONG INFERENCE]** sobre la base de la revisión del destino + re-revisión ([S08-034], [S08-032])
- **Páginas legales** (aviso legal, privacidad, cookies, condiciones de venta, desistimiento o reembolso, contacto): son obligación legal en España/UE para quien vende online, aunque Meta no las exige expresamente en los Ad Standards. Los practitioners las citan como causa frecuente de restricciones y apelaciones fallidas. La business verification exige una web HTTPS que cargue. **[STRONG INFERENCE]** (ley) + **[EMPIRICAL]** ([S08-092]) + **[OFFICIAL META]** (HTTPS) ([S08-055])
- **Lead Ads:**
  - enlace a la política de privacidad obligatorio para publicar el formulario;
  - **13 tipos de datos restringidos** que requieren permiso previo: información financiera, de salud, de seguros, antecedentes, identificadores oficiales, raza, religión, orientación sexual, afiliación política o sindical, cuentas, usuarios o contraseñas, preguntas prellenadas.

  **[OFFICIAL META]** ([S08-001]) + **[EMPIRICAL]** ([S08-125])

## 1. Qué mira Meta en el destino (modelo)

| Dimensión | Qué evalúa | Regla | Evidencia |
|---|---|---|---|
| **Funcionalidad** | Carga, no está rota, no exige descargas ni apps engañosas | Checklist | **[OFFICIAL META]** |
| **Coherencia** | El producto y la oferta de la landing coinciden con el anuncio | Relevance #3 | **[OFFICIAL META]** |
| **Contenido** | Claims (ingresos, salud, garantías), atributos personales, contenido sexual o chocante | Mismas políticas que el anuncio | **[OFFICIAL META]** (el destino se revisa) |
| **Experiencia** | Pop-ups intrusivos, pop-ups de salida "trampa", exceso de publicidad, clickjacking | Spam (deceptive landing functionality); checklist | **[OFFICIAL META]** |
| **Navegación** | Redirecciones, cambio de dominio, enlaces acortados que esconden el destino | Spam (deceptive redirects, misleading links) | **[OFFICIAL META]** |
| **Identidad** | Que la landing no suplante a una marca, medio o persona famosa ("falso artículo de El País") | Spam (domain impersonation) + PCP (brand/celeb-bait) | **[OFFICIAL META]** |
| **Reputación del dominio** | Asociación con cuentas deshabilitadas, feedback negativo | Restricted domains (60 días) | **[OFFICIAL META]** |
| **Datos** | Píxel o CAPI en páginas de salud, parámetros sensibles en URL | Restricciones de data sources (salud) y data use | **[EMPIRICAL]** + **[OFFICIAL META]** |

## 2. Cloaking y técnicas prohibidas (cómo se ven en la práctica)

**Cloaking (prohibido):** servir contenido distinto según el visitante. Ejemplos:
- landing "blanca" (blog de recetas) para IPs o user-agents de Meta y VSL con claims para los usuarios;
- contenido condicionado por país u hora para "esquivar" la revisión;
- JavaScript que cambia la página tras unos segundos o tras detectar un clic real.

**Por qué Meta lo detecta y lo castiga:**
1. revisión desde múltiples orígenes y re-revisión tras feedback;
2. los reportes de usuarios ven la página real;
3. es "circunvención", que convierte un rechazo en una restricción de cuenta y en una asociación del dominio.

**[OFFICIAL META]** que está prohibido; **[STRONG INFERENCE]** sobre los mecanismos de detección.

**Zonas que no son cloaking pero conviene manejar con cuidado:**
- *Personalización legítima* (idioma, moneda, precio por país): permitida si la oferta y los claims son los mismos. **[STRONG INFERENCE]**
- *Tests A/B de landing:* todas las variantes deben cumplir. Si una variante con claims agresivos recibe el tráfico de Meta, es un incumplimiento aunque "solo sea un test". **[STRONG INFERENCE]**
- *Cambiar la landing tras aprobar el anuncio:* el anuncio no se re-revisa automáticamente si no cambias la URL, pero puede re-revisarse por feedback o muestreo. Si los cambios introducen claims prohibidos, se considera evasión. **[OFFICIAL META]** sobre la re-revisión; **[STRONG INFERENCE]** sobre la evasión.

## 3. Embudos de infoproductos: riesgos por tipo de página

| Página | Riesgos típicos | Versión compliant |
|---|---|---|
| **Landing de lead magnet** (guía, checklist) | Promesa del título ("La guía para facturar 10k/mes"); pop-ups agresivos | Título orientado al contenido ("Guía: 7 pasos para validar tu oferta"); un solo CTA; política de privacidad visible |
| **Registro a webinar o masterclass** | "Gratis" que oculta una venta; "solo hoy" falso; testimonios con cifras | Aclarar que al final se presenta una oferta de pago; fecha real; testimonios centrados en la experiencia |
| **VSL / página de ventas** | Claims de ingresos en el vídeo; capturas de pagos; "resultados no típicos" en letra pequeña; contadores falsos; urgencias reiniciables | Describir el programa (módulos, horas, soporte, para quién no es), precio y condiciones claras, garantía de satisfacción con condiciones, sección de resultados con contexto y variedad, aviso de que los resultados dependen de cada persona |
| **Página de aplicación high-ticket** (formulario + llamada) | Preguntas sobre ingresos personales, deudas o salud; "solo para quien quiere ganar 10k" | Preguntas de negocio (facturación de la empresa, rol, objetivo, presupuesto para el programa); explicar el proceso de la llamada |
| **Advertorial / pre-landing tipo noticia** | Aparentar ser un medio real; famosos; "descubrimiento" sensacionalista | Etiquetar como publicidad; sin suplantar medios; sin famosos sin autorización |
| **Grupo de WhatsApp o Telegram como destino** | En inversión, la interacción por mensajería es la firma de un scam (prohibida en EE. UU. para inversión); en general aumenta los reportes | Para inversión, evitarlo. Para otras ofertas, que el anuncio y la landing expliquen el porqué y qué ocurrirá |
| **Checkout** | Suscripción recurrente oculta, upsells premarcados, precio final distinto | Precio y recurrencia claros antes de pagar (PCP: precios y suscripciones engañosos) |

Base: PCP ([S08-067]), Spam ([S08-069]), Financial (mensajería en EE. UU.) ([S08-066]), regulador UK sobre "gratis" y urgencia ([S08-080]). Tabla: **[STRONG INFERENCE]**.

## 4. Testimonios, resultados y disclaimers en la landing

- **Dónde va cada cosa:**
  - en el anuncio, prueba de proceso y experiencia (no cifras de ingresos);
  - en la landing, casos de éxito con contexto (punto de partida, tiempo, esfuerzo, variabilidad) y un **aviso de resultados visible**, no escondido. **[STRONG INFERENCE]** + regulador ([S08-080])
- **El disclaimer no "compensa" un titular engañoso:**
  - el ASA lo dice explícitamente (abr-2026): los disclaimers que "contradicen en lugar de aclarar" el titular no sirven;
  - la FTC sostiene lo mismo para los testimonios no representativos.

  **[OFFICIAL — reguladores]** ([S08-080], [S08-081])
- **Ejemplo de aviso (ES):** "Los resultados que ves son de alumnos concretos y no son típicos ni están garantizados. Dependen de tu punto de partida, tu dedicación y factores de mercado. La mayoría de alumnos [dato real si se tiene: p. ej. completa el programa en 10 semanas]."
- **(EN):** "Results shown are from specific students and are not typical or guaranteed. Outcomes depend on your starting point, effort and market conditions."
- **Consentimiento y veracidad:** solo testimonios reales con permiso escrito. En la UE, presentar reseñas como verificadas sin comprobarlo o publicar reseñas falsas es práctica desleal (asesoría legal). **[STRONG INFERENCE]**

## 5. Checklist de landing compliant (infoproductos y servicios)

**Técnico**
- [ ] HTTPS, carga rápida en móvil, sin errores 404 ni enlaces rotos.
- [ ] Sin redirecciones intermedias ni cambios de dominio; URL del anuncio = URL final (salvo parámetros UTM).
- [ ] Sin pop-ups de salida "trampa", sin pop-unders, sin autoplay con sonido intrusivo.
- [ ] Dominio verificado en el portfolio; sin historial de restricciones.
- [ ] Píxel o CAPI sin parámetros sensibles (salud, finanzas) en URL ni en eventos.

**Contenido**
- [ ] El producto y la oferta coinciden con el anuncio (mismo programa, mismo precio o "desde").
- [ ] El titular describe el programa o el beneficio de proceso, no una cifra de ingresos.
- [ ] Sin capturas de pagos, banco o broker ni imágenes de estilo de vida de lujo.
- [ ] Sin preguntas o afirmaciones sobre atributos del lector (deudas, salud, edad).
- [ ] Testimonios reales, con permiso, con contexto; aviso de resultados visible.
- [ ] Garantía (si la hay) con condiciones claras; nada de "garantía de ingresos".
- [ ] Urgencia o escasez **reales** (fecha de cierre de cohorte real, plazas reales).
- [ ] Sin logos de medios, de Meta o de Google ni fotos con famosos que no se puedan acreditar.
- [ ] Si es salud o fitness: sin curas, sin pellizco de grasa, sin "inferioridad", plazos con matices, 18+.
- [ ] Si toca inversión o crédito: textos de riesgo, sin rentabilidades, revisión legal (CNMV/Banco de España).

**Legal (España/UE; validar con un abogado)**
- [ ] Aviso legal (titular, NIF, domicilio, contacto), política de privacidad y cookies (con banner conforme), condiciones de contratación.
- [ ] Información de desistimiento o reembolso (contenido digital: requisitos específicos).
- [ ] Datos de la empresa coherentes con el portfolio verificado (nombre legal, dirección).

**Lead Ads**
- [ ] Enlace a la política de privacidad.
- [ ] Sin preguntas restringidas (finanzas personales, salud…) sin permiso.
- [ ] Preguntas de cualificación de negocio, no personales.

## Implicaciones operativas

- **Auditar la landing antes que el anuncio.** En cuentas de formación, la mayoría de los problemas graves (rechazos tardíos, dominio restringido) vienen del destino. **[STRONG INFERENCE]**
- **Dos versiones del embudo:** una "Meta-safe" (sin cifras de ingresos ni claims extremos) para tráfico pagado de Meta, y, si se quiere, contenido distinto para tráfico orgánico o email. **Pero el tráfico de Meta debe ir siempre a la versión compliant, sin condicionarlo por user-agent** (eso sería cloaking).
- **Dominio propio y estable**, verificado y con historial limpio. No rotar dominios.

## Errores frecuentes

- Usar el mismo VSL que en YouTube o en email (con ingresos explícitos) para tráfico de Meta.
- Pre-landings que imitan noticias de medios conocidos.
- Formularios de aplicación que preguntan "¿cuánto ganas al mes?" o "¿cuántas deudas tienes?".
- Cambiar la página de ventas tras aprobar los anuncios para "subir la conversión" con claims agresivos.

## Preguntas abiertas

- ¿Con qué frecuencia vuelve Meta a rastrear las landings de anuncios activos sin cambios? (No documentado.)
- ¿Existe una lista pública o un indicador de "reputación de dominio" en BSH? (Solo se ve vía rechazo "restricted domain".)

## Fuentes clave

- [Introduction to the Advertising Standards (Relevance, Lead Ads, Things you should know)](https://transparency.meta.com/policies/ad-standards/) — Meta — meta-oficial
- [Advertising policy basics checklist](https://www.facebook.com/business/help/757209948405699) — Meta — meta-oficial
- [Spam (Community Standard)](https://transparency.meta.com/policies/community-standards/spam/) — Meta — meta-oficial
- [Why ads may face restrictions when using certain domains](https://www.facebook.com/business/help/733029810936140) — Meta — meta-oficial
- [About ads in review](https://www.facebook.com/business/help/204798856225114) — Meta — meta-oficial
- [Prohibited Commercial Practices](https://transparency.meta.com/policies/community-standards/prohibited-commercial-practices/) — Meta — meta-oficial
- [A Guide to Instant Forms](https://www.jonloomer.com/instant-forms/) — Jon Loomer — practitioner
- [Money making courses – stick to the facts](https://www.asa.org.uk/news/money-making-courses-stick-to-the-facts.html) — ASA/CAP, 2026-04-09 — regulador
