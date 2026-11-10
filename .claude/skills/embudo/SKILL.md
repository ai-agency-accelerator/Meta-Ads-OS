---
name: embudo
description: "Sigue el dinero después del clic: cruza Meta con GHL o Stripe y monta cohortes por semana o por anuncio (lead → cualificado → cita → show → venta → cash, o registro → prueba → activación → pago, con LTV y payback). Dice en qué etapa se rompe y si es un problema de marketing o de ventas."
argument-hint: "<cliente> [semana|anuncio] [AAAA-MM-DD AAAA-MM-DD]"
---

# /embudo

Entrada: `$ARGUMENTS`. Por defecto, cohortes por semana de las últimas 8–12 semanas completas.

- **Marco:** `meta-ads-kb/05-leadgen-high-ticket-crm/05-economia-funnel-lead-gen-calculadoras.md` (fórmulas y break-even
  por etapa), `meta-ads-kb/05-leadgen-high-ticket-crm/09-sales-feedback-loop.md` (§5 informes por anuncio hasta cash,
  §7 qué número usar para qué), `meta-ads-kb/05-leadgen-high-ticket-crm/08-speed-to-lead-calendarios-show-rate.md`,
  `meta-ads-kb/05-leadgen-high-ticket-crm/03-calidad-de-lead-y-conversion-leads.md`,
  `meta-ads-kb/05-leadgen-high-ticket-crm/10-b2b-saas-local.md` y `meta-ads-kb/14-playbooks/playbook-saas.md` §4
  (SaaS: CAC ≤ LTV/3 como criterio habitual y payback), plantilla de cohorte en
  `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §7.
- **Agentes:** `especialista-crm` (exportaciones de GHL y lectura del pipeline), `especialista-funnel` (si la rotura
  está en la landing, el formulario o el proceso comercial), `analista-cuantitativo` (LTV, payback, ruido).
- **Herramientas:** `ghl.py`, `stripe_datos.py`, `meta_ads.py anuncios`, `embudo.py cohortes`, `registro_creativo.py`.
- **Lee:** ficha (economía por etapa, `crm.tipo`, `stripe`, `tipo`), `cohortes-leads.md` anterior.
- **Escribe:** `clientes/<slug>/privado/` (exportaciones con datos personales), `clientes/<slug>/datos/cohortes_<por>.csv`,
  `cohortes-leads.md`, `registro-creativo.csv` y `clientes/<slug>/informes/embudo/<AAAA-MM-DD>.md`.

## Pasos

1. **Fuente de verdad** según la ficha:
   - `crm.tipo: ghl` → `especialista-crm` ejecuta
     `python3 -I herramientas/ghl.py por-anuncio --cliente <slug> --desde <AAAA-MM-DD> --hasta <AAAA-MM-DD>`, que deja
     una fila por lead en `clientes/<slug>/privado/leads-ghl_<desde>_<hasta>.csv` (la entrada de `embudo.py cohortes`)
     y los agregados por anuncio en `datos/ghl-por-anuncio_<desde>_<hasta>.csv`. La exportación de `ghl.py
     oportunidades` no sirve para `embudo.py`: no trae el anuncio ni las citas;
   - `stripe: true` → `stripe_datos.py suscripciones` (a `privado/clientes_<AAAA-MM-DD>.csv`) y `stripe_datos.py por-anuncio` (a `datos/`);
   - otro CRM o ninguno → pide una exportación con fecha de creación, `ad_id` o `utm_content` y etapa, y guárdala en
     `privado/`. Sin `ad_id` ni `utm_content` solo hay cohortes por semana: anota como tarea arreglar los UTMs
     (`meta-ads-kb/13-sistema-operativo/10-plantillas.md` §8).
2. **Meta del mismo periodo:** `python3 -I herramientas/meta_ads.py anuncios --cliente <slug> --desde <a> --hasta <b> --por-dia`
   (gasto por semana) y sin `--por-dia` (gasto por anuncio). Sin token, una exportación de Ads Manager en `datos/`.
3. **Cohortes:**
   - `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por semana --modelo <servicios|saas> --meta <csv por día> --guardar`;
   - `python3 -I herramientas/embudo.py cohortes --cliente <slug> --por anuncio --modelo <servicios|saas> --meta <csv por anuncio> --guardar`;
   - ajusta `--ciclo` al ciclo de venta real del cliente (30 días por defecto, [HYPOTHESIS]). En SaaS sin ≥10 bajas,
     pasa `--churn` con un supuesto marcado como [HYPOTHESIS].
   Solo agregados en pantalla y en los archivos; las filas de personas no salen de `privado/`.
4. **Registro creativo:** `python3 -I herramientas/registro_creativo.py actualizar --cliente <slug> --meta <csv por anuncio> [--ghl <csv>] [--stripe <csv>]`
   (el mismo periodo en todas), para que el veredicto de cada anuncio use la capa más profunda con datos.
5. **Lectura** (solo cohortes maduras; las jóvenes se enseñan aparte y sin conclusiones):
   - coste por etapa frente al break-even y al target de la ficha;
   - tasas entre etapas y su tendencia: dónde se rompe;
   - por anuncio: qué anuncios traen leads baratos que no avanzan y cuáles traen menos leads pero más ventas;
   - SaaS: CAC, LTV de contribución, LTV:CAC y payback por cohorte.
6. **¿Marketing o ventas?** Separa las causas antes de tocar Meta:
   - **marketing:** coste por lead fuera de rango, cualificación baja ligada a ciertos anuncios o formularios, promesa
     del anuncio que no casa con la oferta → `/brief-creativo`, `/landing`, cambio de evento (`/ejecutar-cambio`);
   - **ventas:** speed to lead lento, show rate bajo, cierre bajo con leads cualificados, seguimiento irregular → el
     problema está en el proceso comercial; Meta no lo arregla. Propón el ajuste (SLA de respuesta, recordatorios,
     guion) y quién lo hace;
   - **señal:** etapas del CRM que no vuelven a Meta → `/implementar-capi`.
7. **Guarda** el informe en `clientes/<slug>/informes/embudo/<AAAA-MM-DD>.md`: tabla de cohortes (10 §7), etapa que se
   rompe, marketing o ventas, una acción principal con métrica y fecha. Si `relacion: cliente` y el cuello está en
   ventas, prepara el mensaje para el cliente con `gestor-cliente`.

## Reglas

- No se decide con cohortes inmaduras ni con CPL solo cuando hay datos de etapas más profundas.
- Los archivos de `privado/` no se citan, no se copian y no se enseñan: solo sus agregados.
