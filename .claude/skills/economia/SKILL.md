---
name: economia
description: "Calcula cuánto puedes pagar en Meta: CPA y ROAS break-even y target (IVA y location fee), coste máximo por lead, cita, show y venta en servicios, CAC por prueba en SaaS con churn y payback, y modo prevision con escenarios de inversión → leads, citas, ventas y CAC esperables con bandas. Guarda la tabla en la ficha."
argument-hint: "[leadgen|suscripcion|ecommerce|prevision] [cliente] [datos]"
---

# /economia

Entrada: `$ARGUMENTS`. Marcos: `meta-ads-kb/09-bidding-escalado-economia-analitica/08-economia-unitaria-calculadoras.md`,
`meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md`,
`meta-ads-kb/06-ecommerce-apps/05-economia-ecommerce-margenes-mer-ltv.md`, `meta-ads-kb/06-ecommerce-apps/10-suscripciones-y-web2app.md`
y la Fase 1 de `meta-ads-kb/13-sistema-operativo/03-framework-lanzamiento.md`. Consultoras y agencias de IA y
automatización: `meta-ads-kb/14-playbooks/playbook-consultoras-ia-automatizacion.md` §3 (el coste de vender como
`--coste-fijo` por venta, con `coste_vender_por_venta` de la ficha, y el techo de capacidad de `capacidad.*`, que
limita el gasto antes que Meta).

## Pasos

1. **Datos.** Con cliente, lee la cabecera y las secciones «Negocio» y «Economía» de su ficha y usa lo que haya. Pide
   solo lo que falte (como mucho 6 preguntas, agrupadas). Sin cliente, calcula igual y ofrece guardarlo en uno.
2. **Modo** según `tipo`:
   - `servicios-high-ticket`, `lead-gen`, `local`, `infoproducto` con llamada → `leadgen`;
   - `saas` → `suscripcion` (y además `leadgen` con el valor del contrato si la venta es con demo);
   - `ecommerce` → `ecommerce`; `app` → `suscripcion` o `ecommerce` según cobre;
   - planificar inversión o preparar una propuesta → `prevision`.
3. **Cálculo** (añade `--cliente <slug>` si hay cliente y `--json` si vas a guardar):
   - `python3 -I herramientas/economia.py leadgen --precio .. --iva .. [--pct-pago-unico .. --cuotas .. --impago-cuotas .. --reembolsos ..] [--entrega-pct .. --closer-pct .. --setter-pct .. --coste-fijo ..] --cualif .. --agenda .. --show .. --cierre .. [--margen-objetivo 0.5] [--fee-pais ..] [--inversion .. --cpl ..]`
   - `python3 -I herramientas/economia.py suscripcion --precio-mes .. --iva .. --margen .. --churn .. --trial-a-pago .. --payback-meses .. [--fee-pais ..]`
   - `python3 -I herramientas/economia.py ecommerce --aov .. --iva .. --cogs-pct .. --envio .. --pasarela-pct .. --devoluciones-pct .. --fee-pais .. --valor-meta con_iva|sin_iva [--pedidos-ltv ..] [--incrementalidad ..] [--cpa ..]`
   - `python3 -I herramientas/economia.py prevision --modelo servicios|saas|ecommerce --inversion 3000,6000,12000 [--inversion-ref ..] --cpl 30-45|--cpa .. [--curva 0.6-0.8] [--fee-pais ..]`
     más las tasas en rango de su modelo (servicios: `--cualif --agenda --show --cierre` y `--precio` o
     `--contribucion-venta`; SaaS: `--activacion --pago --precio-mes --margen --churn`; e-commerce:
     `--contribucion-pedido`). Detalle con `--help`. Salida: leads, cualificados, citas, ventas (o pruebas y clientes
     de pago) y CAC por escenario, con bandas.
   - **Supuestos.** La salida empieza por el bloque «supuestos»: pasarela, IVA y fee país, cada uno con su origen
     (opción, ficha o por defecto) y cómo cambiarlo. Léelo y dilo en la respuesta; si alguno es «por defecto» y el
     cliente puede saberlo, pregúntalo.
   - **Location fee de Meta** (ES, FR e IT 0,03; UK 0,02; AT y TR 0,05; `00-ESTADO-ACTUAL-2026.md` §6): con
     `--cliente`, `economia.py` la toma de `mercados` en la ficha (la mayor si hay varios, con aviso). Sin `mercados`,
     pregunta dónde se anuncia, apúntalo en la ficha (códigos ISO separados por comas: `mercados: ES, FR`) y repite.
     `--fee-pais` manda sobre la ficha. Los números admiten coma decimal y miles en español («0,175», «4.800»).
   - **Pasarela:** `ecommerce` supone 0,02. En `leadgen` y `prevision` de servicios, 0 con aviso (cobro por
     transferencia, venta B2B, igual que el IVA 0 de esos modos), o 0,03 si la ficha dice `stripe: true`. Si cobra con
     tarjeta, Stripe o financiera, pásala con `--pasarela-pct` (Stripe ~0,015–0,03; financieras, más; 05/05).
   - **IVA:** sin `--iva`, `ecommerce` y `suscripcion` suponen 0,21 y `leadgen` y `prevision`, 0; el bloque
     «supuestos» lo dice: dilo siempre explícito.
4. **Reglas.**
   - Target = break-even × (1 − margen objetivo). Pagar por encima del break-even de la primera venta solo si hay LTV
     demostrado por cohortes **y** la caja aguanta el payback.
   - El IVA en la misma base que el valor que recibe Meta: si mandas valor con IVA, el ROAS break-even sube.
   - Toda tasa que no salga de datos reales va como `[HYPOTHESIS]`, con la fuente que la sustituirá (cohortes de
     `/embudo` tras 2–4 semanas).
   - En `prevision`: el coste esperado sale del histórico de la cuenta (4 semanas completas) si existe; si no, del
     rango conservador, marcado `[HYPOTHESIS]`. **No extrapoles en línea recta**: el coste marginal sube con el gasto
     (conversiones ∝ gasto^b con b≈0,6–0,8, `[STRONG INFERENCE]`, `13-sistema-operativo/01-principios-de-razonamiento.md`
     §9). Las bandas, con `python3 -I herramientas/estadistica.py ic-cpa`. La capacidad comercial (citas que el equipo
     puede atender) es un techo.
   - Para propuestas a clientes (agencias): rangos y supuestos explícitos, nunca promesas de resultado.
5. **Explicación** en lenguaje de negocio: qué puedes pagar por lead, cita, show y venta (o por prueba y cliente de
   pago), qué palanca mueve más la cifra (sensibilidad: `05-leadgen-high-ticket-crm/05-…` §6) y, en SaaS, LTV:CAC y
   payback.
6. **Guardar.**
   - Ficha, sección «Economía»: break-even, target y fuente o supuesto por fila, más las tasas del funnel usadas.
     Marca `F0.economia` en `estado.md` (verifica: archivo).
   - `prevision` → `clientes/<slug>/planes/AAAA-MM-DD_prevision.md` con escenarios, supuestos y bandas.
