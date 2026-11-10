# Pagos, facturación y límites de gasto

> Última verificación: 2026-10-15 · Autor: A08 (agente) · Ámbito: métodos de pago (foco España), automatic billing vs available funds (prepago) vs monthly invoicing, umbral de pago, daily spending limit y cómo sube, account/campaign spending limits, límites de prepago, fallos de pago y consecuencias, location fees 2026, IVA y facturas en España/UE (básico, sin consejo fiscal), límites de nº de cuentas.

## TL;DR

- **Hay tres modos de pago** y el primero que eliges al crear tu primer anuncio fija el modo de la cuenta:
  - **automatic billing:** tarjeta o PayPal con cobro recurrente; cobra al alcanzar el umbral y en la fecha mensual;
  - **available funds:** prepago; métodos manuales o locales;
  - **monthly invoicing:** línea de crédito con factura mensual a 30 días, solo para empresas elegibles.

  Algunas cuentas pueden combinar automatic billing y fondos. **[OFFICIAL META]** ([S08-113], [S08-117], [S08-040])
- **España acepta:** tarjetas de crédito o débito co-branded (Visa, Mastercard, Amex), PayPal y domiciliación (direct debit / online banking). **[OFFICIAL META]** ([S08-042])
- **Límites que pone Meta (no tú):**
  - **daily spending limit:** máximo diario por cuenta según el historial de anuncios y pagos;
  - **límites de prepago:** recarga diaria máxima y saldo máximo almacenado;
  - **umbral de pago inicial** bajo (el ejemplo oficial es USD 25), que sube con pagos exitosos.

  Todos suben si cumples políticas, pagas bien y gastas cerca del límite. Bajan con infracciones, baja calidad, feedback negativo o disputas. **[OFFICIAL META]** ([S08-035], [S08-036], [S08-037])
- **Para subir el límite diario más rápido**, Meta ofrece (si eres elegible):
  1. **verificar el método de pago:** OTP del banco o cargo temporal de USD 1 con código de 4 caracteres;
  2. **verificar la empresa:** de 10 minutos a 14 días hábiles.

  Si aun así necesitas más, se puede pedir a soporte. Con monthly invoicing no hay límite diario. **[OFFICIAL META]** ([S08-038], [S08-037])
- **Un pago fallido pausa todos los anuncios y deshabilita la cuenta hasta saldar la deuda.** Al pagar, Meta reanuda e "intenta recuperar el tiempo perdido". **Muchos pagos fallidos o disputados** son causa explícita de restricción de cuenta, no solo de pausa. **[OFFICIAL META]** ([S08-039], [S08-022])
- **Un mismo método de pago, típicamente en hasta 10 cuentas publicitarias.** Meta puede limitar cuántas cuentas lo usan. **[OFFICIAL META]** ([S08-039])
- **Desde el 1-jul-2026 hay location fees por impuestos digitales:** España 3 %, Francia 3 %, Italia 3 %, Austria 5 %, Türkiye 5 %, Reino Unido 2 %.
  - Se calculan según **dónde se entregan las impresiones**, no dónde está el anunciante.
  - Se cobran fuera del presupuesto y **el IVA se aplica sobre gasto + fee**.
  - No aparecen en Ads Manager, solo en facturación.
  - Reducen la línea de crédito de monthly invoicing y no se reembolsan si las impresiones son legítimas.

  **[OFFICIAL META]** ([S08-017])
- **Cuenta deshabilitada por política durante 6 meses** → el saldo prepago no usado puede perderse "donde la ley lo permita". No conviene tener mucho saldo prepago en cuentas de riesgo. **[OFFICIAL META]** ([S08-022])
- **IVA en España/UE (básico):** factura Meta Platforms Ireland. Si añades un NIF-IVA válido (registrado en VIES), lo habitual es que no se repercuta IVA y se aplique inversión del sujeto pasivo. Sin NIF-IVA válido, se cobra IVA. Confírmalo con tu asesor fiscal. **[STRONG INFERENCE]** a partir de la ayuda de Meta + prácticas reportadas ([S08-043])

## 1. Modos de pago y cuándo usar cada uno

| Modo | Cómo cobra | Ventajas | Riesgos | Para quién |
|---|---|---|---|---|
| **Automatic billing** (tarjeta/PayPal) | Al llegar al **umbral de pago** y en la **fecha de facturación mensual** | Simple; el umbral sube con el historial | Rechazos del banco (límites por transacción, 3DS, antifraude); muchos cobros pequeños al principio | Mayoría de anunciantes y cuentas nuevas |
| **Available funds** (prepago) | Descuenta del saldo; "auto-reload" opcional | Control de caja; útil si los bancos rechazan cargos recurrentes | Si se acaba el saldo, se para la entrega; saldo inmovilizado; puede perderse si la cuenta se deshabilita por política | Métodos locales; mercados donde la tarjeta falla |
| **Automatic + available funds** | Usa primero el saldo y luego la tarjeta | Colchón contra fallos de tarjeta | Saldo inmovilizado | Cuentas con gasto alto y bancos estrictos |
| **Monthly invoicing** (línea de crédito) | Factura mensual; pago a 30 días (o según la ley local); SEPA direct debit o transferencia | Sin límite diario de Meta; consolidado; sirve para verificar la empresa sin documentos | Línea compartible (vector de abuso si se compromete); al agotar el crédito "todos los servicios pueden pausarse"; los location fees consumen crédito | Empresas elegibles (banner en Billing & payments); algunas obligadas a pasarse |

Fuentes: [S08-113], [S08-117], [S08-040], [S08-017], [S08-046].

## 2. Los "límites" (que no son lo mismo)

| Concepto | Quién lo fija | Qué hace | Efecto al alcanzarlo |
|---|---|---|---|
| **Presupuesto diario** (ad set/campaña) | Tú | Media diaria, no tope duro | — |
| **Presupuesto total** | Tú | Tope duro del periodo | Para al agotarse |
| **Campaign spending limit** | Tú | Máximo por campaña | Para la campaña y avisa |
| **Ad account spending limit** | Tú (admin) | Tope acumulado de toda la cuenta; reseteo manual o automático el día 1 en algunos casos | Para toda la cuenta (los anuncios pueden seguir apareciendo como "activos") |
| **Daily spending limit** | **Meta** | Máximo diario de la cuenta según el historial | Pausa hasta el reset (00:00 o 12:00 hora de la cuenta) |
| **Umbral de pago** | **Meta** (puedes fijar un máximo) | Cuándo te cobra | **No pausa**: cobra y sigue |
| **Límite de recarga diaria / saldo máximo** (prepago) | **Meta** | Cuánto puedes recargar al día y cuánto acumular | No puedes recargar más |

Fuentes: [S08-036], [S08-037], [S08-041]. **[OFFICIAL META]**

Puntos finos oficiales:
- Puedes poner un presupuesto diario **mayor** que el daily spending limit: cuando el límite suba, se gastará automáticamente hasta el nuevo límite. **[OFFICIAL META]** ([S08-036])
- "Si tus anuncios siguen pausados tras pagar, puede que hayas alcanzado el daily spending limit fijado por Meta." **[OFFICIAL META]** ([S08-039])
- Puedes fijar un **umbral de pago máximo**. Bajarlo aplica al momento; subirlo es progresivo con pagos exitosos. Útil si la tarjeta tiene límite por transacción. **[OFFICIAL META]** ([S08-041])
- Meta revisa el umbral al alza o a la baja según el historial de pagos (**incluidas las disputas**) y el cumplimiento de los Self-Serve Ad Terms y Advertising Standards. Con los mismos datos decide si tienes **periodo de gracia** y si eres elegible para monthly invoicing o net 30. **[OFFICIAL META]** ([S08-036])
- Vía API: el `spend_cap` de la cuenta solo admite 10 cambios al día. **[OFFICIAL META]** ([S08-083])

## 3. Cómo suben los límites en cuentas nuevas (realidad vs mito)

**Oficial** ([S08-037], [S08-038], [S08-035]):
- La mayoría de los anunciantes tiene un **límite diario inicial**. Sube "automáticamente" si:
  1. construyes historial;
  2. sigues las políticas;
  3. **gastas hasta o cerca del límite**.
- Meta puede reajustarlo con **portfolio, cuenta, Página o app nuevos**, tras infracciones o con baja calidad o feedback.
- Aceleradores: verificar el método de pago (si te lo ofrece: "You've qualified for a higher ads daily spending limit") y verificar la empresa.
- El umbral de pago empieza bajo (ejemplo oficial: USD 25) y sube con cada cobro exitoso.

**No oficial:**
- Cifras concretas de límites iniciales (p. ej. "50 $" o "250 $/día"): no hay fuente de Meta. Varían por país, divisa, método de pago y señales de riesgo. **[UNPROVEN]**
- Escalado brusco del presupuesto en cuentas nuevas como causa de baneo: las agencias lo reportan, pero Meta solo documenta que el límite diario contiene el gasto. **[HYPOTHESIS]**

**Práctica recomendada para el lanzamiento:**
- Verificar el método de pago y la empresa *antes* del lanzamiento.
- Usar una tarjeta empresarial a nombre de la entidad verificada y con límite por transacción alto.
- Gastar de forma consistente cerca del límite durante los primeros días para "demostrar" uso.
- Evitar picos de cargos fallidos.

**[STRONG INFERENCE]** a partir de los criterios oficiales.

## 4. Fallos de pago: consecuencias y prevención

**Qué pasa** ([S08-039]):
- El método falla → **anuncios pausados + cuenta publicitaria deshabilitada hasta pagar lo debido**. No se acumulan más cargos.
- Con "Pay now" (Billing & payments → Payment methods) o "Add funds" se suele resolver. Con fondos puede tardar un poco en volver al estado normal.
- Tras el pago, Meta reanuda los anuncios activos o programados e intenta cumplir fechas y presupuestos originales.

**Causas comunes y soluciones oficiales:**
- método no soportado en el país o usado en demasiadas cuentas (~10 máx.);
- tarjeta inactiva o caducada;
- fallo de 3DS (CVV u OTP);
- rechazo del banco por reglas internas;
- error de conexión;
- fondos insuficientes;
- límite por transacción → bajar el umbral.

**Prevención (oficial):**
- método de **backup**;
- revisar caducidades;
- teléfono del OTP accesible;
- fondos cerca de la fecha mensual;
- fondos disponibles como colchón;
- auto-reload en prepago;
- pedir monthly invoicing si eres elegible.

**Disputas (chargebacks):** Meta lista "high rates of failed payments or disputed payments" como causa de **restricciones de anuncios**. Disputar un cargo legítimo para "forzar" una devolución es de las peores ideas operativas: daña umbral, límites y elegibilidad. **[OFFICIAL META]** ([S08-022], [S08-036])

**Señales de riesgo de pago reportadas por practitioners** (no oficiales):
- titular de la tarjeta distinto del negocio verificado;
- tarjeta de otro país que el negocio;
- tarjeta que estuvo en una cuenta deshabilitada;
- tarjetas virtuales o prepago de fintechs que rechazan cargos recurrentes.

**[EMPIRICAL — agencias]** ([S08-092])

## 5. Location fees (desde el 1-jul-2026)

Según [S08-017] (**[OFFICIAL META]**):
- **Tarifas:** Austria 5 %, Francia 3 %, Italia 3 %, **España 3 %**, Türkiye 5 %, Reino Unido 2 %. La lista "puede cambiar".
- **Base:** impresiones entregadas a audiencias en esas jurisdicciones. Una campaña ES+FR paga 3 % por las impresiones de cada país, desglosado por jurisdicción.
- **Fuera del presupuesto y del spend cap:** el total cobrado puede superar el presupuesto.
- **IVA:** se calcula sobre ad spend + location fee.
- **Formatos:** todos (imagen, vídeo); incluye click-to-WhatsApp y marketing messages facturados con anuncios.
- **Visibilidad:** no aparecen en las métricas de Ads Manager; sí en facturas y Billing & payments. En monthly invoicing se ven por campaña vía API (`business_invoices` → `invoice_campaigns` → `billed_amount_details`) o CSV.
- **Cupones:** se reparten proporcionalmente. **Reembolsos:** solo si el gasto subyacente es reembolsable.

**Implicación para el CPA/ROAS:** un anunciante español que entrega en España paga, como mínimo, +3 % sobre el gasto antes de IVA. Hay que ajustar los objetivos de CPA y ROAS de forma que el reporting de Ads Manager (sin fee) no infravalore el coste real. Esto es relevante para el área 09 (economía).

## 6. IVA y facturas en España/UE (lo básico, **no es consejo fiscal**)

- Meta pide añadir el **número de IVA** a la cuenta si el país lo exige. Sin él, se deja en blanco, pero hay que declarar si se compra "para fines empresariales" y la dirección del negocio. El presupuesto diario **no incluye IVA**. **[OFFICIAL META]** ([S08-043])
- Entidad emisora habitual para la UE: **Meta Platforms Ireland Ltd.** **[EMPIRICAL — fuentes contables]**
- Con un NIF-IVA válido (alta en el ROI/VIES), la práctica reportada es factura sin IVA e **inversión del sujeto pasivo** (autoliquidación en tu declaración). Si Meta no valida el número, puede repercutir IVA. **[STRONG INFERENCE]**
- Los location fees también entran en la base del IVA. **[OFFICIAL META]**
- Recibos y facturas: Billing & payments → Payment activity / Invoices. **[OFFICIAL META]**
- **Consultar al asesor:** tratamiento del IVA (autónomo vs sociedad, ROI), deducibilidad, modelo 349 y retenciones. Este documento no cubre esos aspectos.

## 7. Límites de número de cuentas publicitarias

- Todo anunciante: **1 cuenta publicitaria hasta confirmar un pago**. **[OFFICIAL META]** ([S08-101])
- Portfolio nuevo: **1 cuenta**, que pasa a **3** cuando una campaña entrega y se hace un pago. Después crece "según el gasto". Las cuentas **cerradas siguen contando** para el límite. **[OFFICIAL META]** ([S08-100])
- Las cuentas publicitarias **no se pueden borrar** de un portfolio, solo desactivar: se cobra el saldo pendiente y se retiran los métodos de pago. **[OFFICIAL META]** ([S08-103])
- Implicación: no crear cuentas "por si acaso". Cada cuenta abandonada es superficie de ataque ([03](03-seguridad-business-portfolio-roles-partners.md)) y consume cupo.

## Implicaciones operativas

- **Setup por defecto para un cliente de infoproductos en España:**
  - tarjeta empresarial a nombre de la sociedad o autónomo verificado, con 3DS operativo;
  - tarjeta de backup del mismo titular;
  - umbral máximo ajustado al límite por transacción de la tarjeta;
  - NIF-IVA cargado;
  - **account spending limit** mensual como cortafuegos;
  - pedir monthly invoicing cuando aparezca el banner.
- **Presupuesto real = gasto de Ads Manager × (1 + location fee) × (1 + IVA si aplica).** Documentarlo en los modelos de unit economics.
- **No mover saldos grandes a prepago** en cuentas de ofertas sensibles (riesgo de pérdida si hay deshabilitación por política).
- **Lanzamientos:** confirmar el daily spending limit 72 h antes. Si no basta para el plan de medios, verificar el método de pago o la empresa y pedir aumento por soporte con antelación.

## Errores frecuentes

- Interpretar "Active, sin gasto" como problema de subasta cuando es el daily spending limit o el account spending limit.
- Usar la tarjeta personal del fundador en una cuenta de la sociedad, o una tarjeta de otro país.
- Reutilizar en una cuenta nueva la tarjeta de una cuenta deshabilitada por política.
- Abrir disputas con el banco por cargos de anuncios que sí se entregaron.
- Olvidar que los location fees y el IVA no salen en Ads Manager (desfase con contabilidad).

## Preguntas abiertas

- Cifras de límite diario inicial por país y método (Meta no las publica).
- Criterios de elegibilidad para monthly invoicing y "net 30" (Meta solo dice que dependen del historial y del cumplimiento).
- Si la verificación de anunciante financiero en España requiere coherencia entre el titular del pago y la entidad con licencia (probable, no verificado).

## Fuentes clave

- [How budgets, spending limits, prepaid balance limits and your payment threshold differ](https://www.facebook.com/business/help/998181913623584) — Meta — meta-oficial
- [About daily spending limits set by Meta](https://www.facebook.com/business/help/563129151097553) — Meta — meta-oficial
- [How to increase your Meta daily spending limit](https://www.facebook.com/business/help/468638042183410) — Meta — meta-oficial
- [About payment thresholds](https://www.facebook.com/business/help/776240779095515) / [Adjust your payment threshold](https://www.facebook.com/business/help/1342874532544030) — Meta — meta-oficial
- [Fix a failed payment issue on Meta](https://www.facebook.com/business/help/268196136699959) — Meta — meta-oficial
- [About monthly invoicing](https://www.facebook.com/business/help/2086865811541431) — Meta — meta-oficial
- [Accepted payment options](https://www.facebook.com/business/help/212763688755026) / [Spain](https://www.facebook.com/business/help/122345525064994) — Meta — meta-oficial
- [About location fees for ads on Meta platforms](https://www.facebook.com/business/help/1238737454289085) — Meta, desde 2026-07-01 — meta-oficial
- [About value-added tax (VAT)](https://www.facebook.com/business/help/155641834501332) — Meta — meta-oficial
- [Add an ad account to your business portfolio](https://www.facebook.com/business/help/910137316041095) — Meta — meta-oficial
