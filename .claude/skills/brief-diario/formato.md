# Formato del brief diario

Lo usa `/brief-diario` en los pasos 3 y 4. Los ejemplos son de clientes ficticios.

## 1. Semáforo

Gana el color más grave que se cumpla. Las cifras sin fuente de la KB van marcadas `[HYPOTHESIS]`: son puntos de
partida razonables, ajústalos con lo que veas en tus cuentas.

**🔴 Roto: hay que actuar hoy** (cualquiera de estos)
- Cuenta no activa (deshabilitada, en revisión de riesgo, pago pendiente) o límite de gasto de la cuenta alcanzado.
  → `meta-ads-kb/08-cuenta-politicas-seguridad/01-account-quality-y-restricciones.md`,
  `meta-ads-kb/08-cuenta-politicas-seguridad/04-pagos-facturacion-limites.md`.
- Evento principal a 0 en el dataset en las últimas 24 h con campañas gastando, o uno de los dos orígenes (navegador
  o servidor) a 0 cuando los dos enviaban. Prioridad 1 según `04-operativa-diaria-semanal-mensual.md` §1.
- Anuncios con gasto rechazados, o todos los anuncios de una campaña activa rechazados o con problemas
  (`07-framework-diagnostico.md` §14).
- Gasto de ayer por encima del 175 % del presupuesto diario (210 % con presupuesto compartido), o a cero con campañas
  activas que deberían entregar (ni en revisión ni programadas para más tarde) (`07-framework-diagnostico.md` §6 y
  §15). Un día alto dentro de esos límites es normal: el tope es semanal.
- Meta cuenta 3 o más leads de ayer y el CRM no recibió ninguno de Meta: la integración está rota `[HYPOTHESIS]`.

**🟡 Vigilar: no se toca Meta** (cualquiera de estos)
- Resultado de ayer fuera de la banda de ruido (un día fuera → anotar y esperar; varios seguidos → investigar)
  (`04-operativa-diaria-semanal-mensual.md` §1).
- Desfase entre navegador y servidor muy distinto al habitual, sin llegar a cero.
- Gasto de ayer por debajo del 50 % del ritmo previsto sin motivo conocido `[HYPOTHESIS]`, o un «learning limited»
  nuevo.
- Anuncios en revisión desde hace más de 24 h `[HYPOTHESIS]`.
- Cambios en Meta que no están en el change log.
- Una regla automática del OS pausó algo ayer (`reglas_meta.py historial`): «revisa si acertó:
  `/reglas-automaticas <slug> revisar`». No se reactiva desde el brief.
- Evaluaciones que vencen hoy o que van atrasadas.
- Del alta a la reserva de la cita (`horas_hasta_cita_mediana` de `ghl.py por-anuncio`, 7 días): más del doble que
  en el último brief, o más de 48 h si no hay con qué comparar `[HYPOTHESIS]`. No es el speed to lead (minutos hasta
  el primer contacto, objetivo de menos de 5: `05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`):
  `ghl.py` no lee los mensajes salientes, así que ese se mira en GHL. No lo llames speed to lead en el informe.
- Falta un dato importante (sin dataset en la ficha, CRM sin leer) y hay gasto.

**🟢 En orden**: nada de lo anterior.

**⚪ Sin datos**: no se pudo leer Meta, la ficha no se lee o el cliente no tiene campañas activas. Una línea con el
motivo y cómo arreglarlo.

## 2. Informe por cliente: `clientes/<slug>/informes/diario/AAAA-MM-DD.md`

La cabecera la leen `/hoy` y el hook `contexto_sesion` sin interpretar el texto: respeta las claves y los valores.
- `semaforo` ∈ `verde | ambar | rojo | sin-datos` (🟢 🟡 🔴 ⚪);
- `acciones`: número de acciones de la sección «Acciones» (0 salvo en rojo);
- `fuente_meta` ∈ `mcp | meta_ads.py | ninguna`.

```markdown
---
fecha: 2026-11-10
cliente: acme-automations
semaforo: ambar
acciones: 0
generado: 2026-11-10 08:03
fuente_meta: mcp
ventana_atribucion: 7d_click_1d_view
---
# Brief diario · Acme Automations · 2026-11-10

🟡 **Sin roturas; un cambio de presupuesto en Meta que no está en el change log.**

| Bloque | Estado | Dato |
|---|---|---|
| Cuenta | 🟢 | Activa · límite de gasto al 42 % |
| Gasto frente al ritmo | 🟢 | Ayer 182 € de 200 €/día (91 %) · semana 1.130 € de 1.400 € (81 %) |
| Entrega, errores y rechazos | 🟢 | 2 campañas y 3 conjuntos entregando · 0 errores · 0 rechazados |
| Resultados frente al ruido | 🟢 | 9 Lead recibidos ayer · banda 4–17 (media 10,1/día en 14 días) |
| Señal del dataset (48 h) | 🟢 | Lead: 21 navegador · 20 servidor · ninguno a cero |
| Cambios desde el último brief | 🟡 | Presupuesto del conjunto 120200000000000001: 80 → 100 €/día (2026-11-09 18:12), sin fila en el change log |
| Negocio de ayer | 🟢 | GHL: 9 leads (8 de Meta) · 3 citas creadas · 2 citas hoy · del alta a la cita: mediana 20,5 h (7 días; antes 18 h) |
| Evaluaciones | 🟡 | Vence hoy: campaña 120200000000000000, creativos nuevos (2026-11-03) |

## Qué NO tocar hoy
- El conjunto 120200000000000001: cambió el 2026-11-09; no se evalúa antes del 2026-11-16.
- El CPA de ayer: con 7d_click_1d_view aún llegarán conversiones durante una semana.

## Vigila
- Pregunta al cliente quién subió el presupuesto el 2026-11-09 y anótalo en el change log.
- La evaluación de hoy se hace con `/informe-semanal acme-automations`.

## Acciones
Ninguna: no hay nada roto.

## Notas
- Periodo: ayer = 2026-11-09. Datos de ayer provisionales (ventana 7d_click_1d_view).
- Fuente: MCP de Meta, GHL (`ghl.py`). Sin Stripe en la ficha.
```

Cuando es 🔴, la sección «Acciones» lleva de 1 a 3 pasos numerados: qué hacer, dónde y con qué skill. Ejemplo:

```markdown
## Acciones
1. Envía un lead de prueba desde la landing y comprueba en Events Manager (Probar eventos) que llega el Lead.
2. Si no llega: `/diagnostico clinica-sonrisa "tracking roto"`.
3. No pauses la campaña por esto: el problema es la señal, no los anuncios.
```

## 3. Resumen global: `informes/diario/AAAA-MM-DD.md` (lo que se envía)

Reglas:
- Título con la fecha y el recuento por color, en el orden 🔴 🟡 🟢 ⚪ (omite los que valgan 0). Es el asunto del email.
- Primero los 🔴, luego los 🟡 (ámbar), luego los 🟢 y al final los ⚪. 🔴 y 🟡: titular de una línea y una
  línea «→» con la acción o lo que hay que vigilar. Verdes: una línea cada uno. Si todo está en verde, empieza con
  «🟢 Todo en orden en N clientes. Nada que hacer hoy.».
- Sin tablas, sin cabecera YAML, sin datos personales. Cifras con la moneda de la ficha.
- Que quepa en una pantalla de móvil hasta 5 clientes (unos 1.500 caracteres). Con más, los verdes van agrupados en
  una sola línea («🟢 Acme Automations, Nimbo y 6 más: en ritmo y con señal»).

```markdown
# Brief diario · 2026-11-10 · 🔴 1 · 🟡 1 · 🟢 1

🔴 **Clínica Sonrisa** — Lead a 0 en el dataset desde ayer a mediodía (navegador y servidor) con 95 €/día activos.
→ Envía un lead de prueba desde la landing; si no aparece en Events Manager, `/diagnostico clinica-sonrisa "tracking roto"`. No pauses nada.

🟡 **Acme Automations** — Presupuesto de un conjunto subido en Meta el 2026-11-09 sin anotar en el change log.
→ Averigua quién lo hizo y anótalo. Lo demás, en orden.

🟢 **Nimbo** — En ritmo (96 %), 14 pruebas iniciadas ayer (banda 8–21), señal bien.

**Evaluaciones de hoy:** Acme Automations · campaña 120200000000000000 (creativos nuevos) → `/informe-semanal acme-automations`.
**No toques hoy:** el CPA de 1–3 días de ningún cliente; Acme · conjunto 120200000000000001 hasta el 2026-11-16.

Detalle: `clientes/<slug>/informes/diario/2026-11-10.md` · generado 2026-11-10 08:03
```
