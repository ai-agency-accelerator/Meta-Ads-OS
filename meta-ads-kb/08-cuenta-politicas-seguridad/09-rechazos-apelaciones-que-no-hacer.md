# Rechazos de anuncios: apelar, editar, crear nuevo, escalar — y qué no hacer nunca

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: flujo oficial ante un anuncio rechazado, cuándo editar o crear de nuevo o pedir revisión, efecto acumulativo de los rechazos en la salud de la cuenta, prácticas prohibidas (duplicar en masa, cuentas nuevas, cloaking, ofuscación), protocolo interno y métricas de control.

## TL;DR

- **Tres opciones oficiales ante un rechazo:**
  1. **Editar** el anuncio (vuelve a revisión automáticamente);
  2. **Crear uno nuevo**;
  3. **Pedir otra revisión** en Business Support Home si crees que es un error.

  **[OFFICIAL META]** ([S08-031])
- **Editar o borrar un anuncio rechazado no elimina la infracción del historial.** "You can be restricted from advertising for severe or repeat ad violations." **Borrar el anuncio puede impedir pedir la revisión.** **[OFFICIAL META]** ([S08-031])
- **Si la revisión te da la razón, el rechazo "no cuenta como infracción".** Por eso, ante un falso positivo, **apelar es mejor que rehacer**: limpia el historial. **[OFFICIAL META]** ([S08-031])
- **La re-revisión tiene más peso humano**, con objetivo de 48 h. **Solo se puede pedir una vez por anuncio**: si se confirma el rechazo, no hay segunda petición para ese anuncio. Pedir revisión "no perjudica tu reputación". **[OFFICIAL META]** ([S08-031])
- **Ediciones que vuelven a disparar la revisión:** targeting, creatividad (texto, imagen, vídeo, enlace), optimización y evento de facturación. **No la disparan:** puja, presupuesto, calendario. Cambiar el enlace de un anuncio aprobado lo manda de nuevo a revisión. **[OFFICIAL META]** ([S08-034])
- **Evasión = el error terminal:** crear cuentas o activos nuevos "con la intención de repetir infracciones" tras una deshabilitación, coordinar redes que publican anuncios iguales que infringen, cloaking o redirecciones engañosas, o comprar o alquilar accesos. **[OFFICIAL META]** ([S08-025], [S08-069], [S08-070], [S08-001])
- **Regla operativa:** un rechazo es información; dos rechazos del mismo tipo en 30 días son un patrón que hay que cortar en origen (copy, creatividad, landing); tres o más son riesgo de restricción. **[STRONG INFERENCE]**

## 1. Árbol de decisión ante un rechazo

```
Anuncio rechazado
│
├─ 1. Leer el motivo exacto en Business Support Home (no solo el email)
│
├─ ¿Es un error claro? (p. ej. "personal attributes" en un anuncio sin atributos; SIEP en un curso de Excel)
│     └─ SÍ → NO borrar. Request review (una vez). Mientras tanto, no duplicar el mismo anuncio.
│           ├─ Revocado → el anuncio entrega si la campaña está activa; NO cuenta como infracción.
│           └─ Confirmado → aceptar; corregir la causa en una versión nueva; no insistir con el mismo concepto.
│
├─ ¿Hay una infracción real o dudosa? (claims de ingresos, pregunta sobre atributos, antes/después sin matiz)
│     └─ Corregir el ORIGEN del problema (copy, creatividad o landing), no maquillarlo.
│           ├─ Si el cambio es pequeño → Editar (vuelve a revisión).
│           └─ Si cambia el concepto → Crear un anuncio nuevo y dejar el rechazado (o archivarlo) sin borrarlo de inmediato.
│
├─ ¿Es la landing o el dominio? ("restricted domain", funcionalidad, discrepancia de producto)
│     └─ Arreglar la landing. Si el dominio está bloqueado (60 días), entender por qué; NO cambiar de dominio para seguir con la misma práctica.
│
├─ ¿Es una Special Ad Category o una autorización? (crédito, empleo, vivienda, cripto, juego)
│     └─ Rehacer la campaña con la SAC correcta o pedir la autorización. Editar el anuncio no basta.
│
└─ ¿Es SIEP en la UE?
      └─ Quitar el tono de advocacy y el tema social (ver [07]); si es un error, pedir revisión.
```

Base oficial: [S08-031], [S08-030], [S08-061], [S08-064]. Árbol: **[STRONG INFERENCE]**

## 2. Editar vs crear nuevo vs apelar (tabla de decisión)

| Situación | Mejor opción | Por qué | Evidencia |
|---|---|---|---|
| Falso positivo evidente | **Request review** | Si se revoca, no cuenta como infracción; humanos con más peso | **[OFFICIAL META]** |
| Infracción leve (una palabra o frase) | **Editar** | Rápido; se re-revisa; la infracción original queda registrada igualmente | **[OFFICIAL META]** |
| Concepto entero problemático (ángulo de ingresos) | **Anuncio nuevo** con otro concepto + análisis de por qué falló | Iterar microcambios sobre un concepto prohibido acumula rechazos | **[STRONG INFERENCE]** |
| Formato que no se puede editar | **Crear nuevo** | Meta: no todos los tipos de anuncio son editables | **[OFFICIAL META]** |
| Rechazo de un anuncio que llevaba días aprobado | Revisar feedback y comentarios; pedir revisión solo si de verdad cumple | La re-revisión suele venir de reportes o engagement anómalo | **[OFFICIAL META]** ([S08-032]) |
| Rechazo en Advantage+ creative o variaciones generadas por IA | Revisar qué ha generado Meta (texto o imagen) antes de apelar | Las variaciones automáticas pueden introducir claims; tú respondes por ellas | **[HYPOTHESIS]**; relevante para el área 03 (creatividad) |

**Sobre borrar anuncios rechazados:** Meta advierte que, si borras, "puedes perder la capacidad de pedir otra revisión" porque ya no puede acceder a la información. Además, borrar no limpia el historial. Recomendación: **no borrar hasta haber decidido no apelar**; después se pueden archivar o borrar por higiene. **[OFFICIAL META]** ([S08-031])

## 3. Impacto acumulado en la salud de la cuenta

- **Oficial:** ante infracciones "graves o repetidas", Meta puede ir más allá del rechazo y restringir el business account, la cuenta publicitaria, la Página o el usuario. **[OFFICIAL META]** ([S08-031], [S08-025])
- **Oficial:** el historial de cumplimiento influye en cuánta revisión recibe cada anuncio, y el límite diario de gasto puede bajar con infracciones. **[OFFICIAL META]** ([S08-034], [S08-037])
- **Oficial (sep-2026):** por infracciones repetidas de PCP, las sanciones pueden extenderse a usuarios, Páginas y portfolios asociados. **[OFFICIAL META]** ([S08-068])
- **No oficial:**
  - cuántos rechazos llevan a restricción: Meta no publica umbrales. **[UNPROVEN]** cualquier cifra concreta;
  - si los rechazos revocados "no cuentan": **[OFFICIAL META]** que no cuentan como infracción;
  - si caducan con el tiempo: **[HYPOTHESIS]** (parece que sí, pero no hay documentación).

**Indicadores a vigilar (por cuenta, ventana móvil de 30 y 90 días):**
- nº de anuncios rechazados y tasa de rechazo (rechazados / publicados);
- rechazos por política (personal attributes, PCP, health…);
- rechazos revocados en apelación (señal de falsos positivos);
- anuncios rechazados tras aprobación (señal de feedback negativo);
- cambios en el daily spending limit o en el umbral de pago;
- avisos de verificación.

## 4. Qué NO hacer (lista negra operativa)

| Práctica | Por qué está prohibida o es peligrosa | Evidencia |
|---|---|---|
| **Duplicar en masa un anuncio rechazado** con microcambios (cambiar un emoji, una palabra) | Acumula rechazos; parece una prueba de límites del sistema; en redes de cuentas encaja con la "coordinación… de anuncios iguales que infringen" | **[OFFICIAL META]** (evasión) + **[STRONG INFERENCE]** |
| **Crear cuentas publicitarias o portfolios nuevos** para seguir con lo mismo tras una restricción | Evasión de enforcement; Meta puede deshabilitar cuentas del mismo dueño o con contenido común | **[OFFICIAL META]** ([S08-025], [S08-070]) |
| **Cloaking**: mostrar al revisor una landing distinta de la del usuario (por IP, user-agent, geolocalización, horario) | Prohibido explícitamente en Spam ("intentionally showing integrity systems different off-platform content") | **[OFFICIAL META]** ([S08-069]) |
| **Cambiar la landing tras la aprobación** para introducir claims prohibidos (o cambiar el destino de un enlace acortado) | Evasión de la revisión; la re-revisión y el feedback lo detectan; agrava la sanción | **[STRONG INFERENCE]** ([S08-069], [S08-070]) |
| **Redirecciones engañosas** (pasar por un dominio "limpio" que redirige al real) | Prohibido ("deceptive redirects") | **[OFFICIAL META]** ([S08-069]) |
| **Ofuscar palabras** (G4N4R, d1n3ro, Unicode, emojis en lugar de letras) o meter el claim prohibido solo en la imagen o el audio | Intento de esquivar clasificadores; los modelos leen OCR y audio; se considera circunvención | **[EMPIRICAL]** ([S08-092]) + **[STRONG INFERENCE]** |
| **Usar cuentas "alquiladas"**, "agency accounts" de terceros o perfiles de otras personas | Prohibido vender, alquilar o comprar privilegios; asociación con redes infractoras | **[OFFICIAL META]** ([S08-001], [S08-069]) |
| **Cambiar de dominio para esquivar un bloqueo** de dominio por infracción | El bloqueo de 60 días se renueva si la actividad continúa; el nuevo dominio hereda la asociación | **[OFFICIAL META]** ([S08-030]) + **[STRONG INFERENCE]** |
| **Apelar en bucle** con mensajes genéricos | Las revisiones de cuenta son limitadas; la de anuncio, única | **[OFFICIAL META]** |
| **"Recuperadores" que piden credenciales** o ejecutar scripts | Vector de hackeo; dar acceso full a terceros desconocidos es un riesgo de asociación | **[EMPIRICAL]** ([S08-084]) |
| **Esconder los términos** (suscripción recurrente, precio real) para "convertir más" | PCP: suscripciones engañosas, precios engañosos | **[OFFICIAL META]** ([S08-067]) |

## 5. Protocolo interno recomendado (agencia o equipo)

1. **Pre-flight check** de cada anuncio (2 minutos) con el checklist de [11](11-copy-persuasivo-compliant-patrones.md): ingresos, garantías, atributos, salud, finanzas, famosos, urgencia, landing.
2. **Registro de rechazos:** fecha, cuenta, ID del anuncio, motivo literal, decisión (apelar/editar/nuevo), resultado, aprendizaje.
3. **Responsable de cumplimiento** que decide las apelaciones (evita apelaciones impulsivas del media buyer).
4. **Biblioteca de "frases prohibidas" y "alternativas aprobadas"** por cliente y nicho, actualizada con cada rechazo o aprobación.
5. **Escalado:**
   - más de 3 rechazos en 30 días en una cuenta → pausa de lanzamientos nuevos en esa cuenta, auditoría de copy y landing, revisión de seguridad;
   - cualquier restricción de cuenta → protocolo de [01](01-account-quality-y-restricciones.md) §4-5.
6. **No escalar presupuesto** en anuncios de ángulos sensibles sin al menos unos días de entrega estable: el aumento de alcance multiplica reportes y re-revisiones. **[STRONG INFERENCE]**

## Implicaciones operativas

- La pregunta correcta tras un rechazo no es "¿cómo lo hago pasar?" sino "¿qué parte de mi mensaje o de mi landing está fuera de política, y cómo comunico lo mismo de forma compliant?". Iterar para "colarlo" es exactamente lo que el sistema penaliza.
- Ante falsos positivos repetidos de un mismo tipo (p. ej. SIEP en la UE o personal attributes), apelar todos y documentarlo. Si se revocan, la cuenta mejora su historial.

## Errores frecuentes

- Borrar el anuncio rechazado y crear una copia inmediatamente.
- Apelar anuncios que sí infringen, gastando la única re-revisión del anuncio.
- Editar el anuncio en vez de arreglar la landing cuando el problema está en el destino.
- Reaccionar a un rechazo cambiando de cuenta publicitaria.

## Preguntas abiertas

- ¿Se "olvidan" los rechazos antiguos para el cálculo de riesgo? (No documentado.)
- ¿Cuenta como infracción del anunciante un rechazo causado por una variación automática de Advantage+ creative? (No documentado.)

## Fuentes clave

- [How to troubleshoot a rejected ad](https://www.facebook.com/business/help/1210227555661027) — Meta — meta-oficial
- [Why some ads are approved, then rejected](https://www.facebook.com/business/help/133691315402558) — Meta — meta-oficial
- [About ads in review](https://www.facebook.com/business/help/204798856225114) — Meta — meta-oficial
- [Common examples of Meta advertising policy violations](https://www.facebook.com/business/help/3858246497787265) — Meta — meta-oficial
- [Why ads may face restrictions when using certain domains](https://www.facebook.com/business/help/733029810936140) — Meta — meta-oficial
- [Spam (cloaking, redirects)](https://transparency.meta.com/policies/community-standards/spam/) / [Account Integrity](https://transparency.meta.com/policies/community-standards/account-integrity/) — Meta — meta-oficial
- [Meta Ad Account Disabled in 2026? Appeal & Recovery Guide](https://techniqco.com/meta-ads-account-disabled-business-manager-restricted-appeal-recovery-2026/) — TechniqCo, 2026-08-25 — agencia
