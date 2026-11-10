# Playbook: B2B en Meta

> Última verificación: 2026-10-16 · Autor: A05 (agente) · Ámbito: servicios y productos para empresas (pymes y mid-market); comparación con LinkedIn. SaaS en `playbook-saas.md`; agencias en `playbook-agencias-consultores.md`. Base: `05-leadgen-high-ticket-crm/10-b2b-saas-local.md`. Fuentes: `fuentes/ledger-05-leadgen-high-ticket-crm.md`.

## TL;DR

- **Meta para B2B cuando el decisor es accesible por problema/rol** (dueños, gerentes, profesionales de pymes) y el filtro posterior es bueno; LinkedIn para ABM y cargos en grandes empresas. **[STRONG INFERENCE]**
- **Datos 2025 (Metadata, 57,6 M$):** CPL Facebook 145 $, Instagram 138 $, LinkedIn 202 $; CPC 1,95 $ vs 9,39 $; click-to-lead 2,6% vs 5,9%; retargeting en Meta más barato (120 $ vs 166 $). No hay datos para comparar coste por cliente. **[EMPIRICAL]** (S05-044)
- **Coste por SQL Meta vs LinkedIn: [CONTESTED].** Decide con tu pipeline.
- **Configuración:** instant form Higher intent + **Require work email** + preguntas de tamaño/rol/urgencia, o landing + calendario; qualified leads con SQL/demo vía CAPI CRM (HubSpot/Salesforce). **[OFFICIAL META]** (S05-005, S05-007)
- **Ejemplo (servicio 5.000 €):** contribución 1.910 €/venta → BE CPL 71,62 €, target 35,81 €; BE por agenda 358 €. **[STRONG INFERENCE]**

---

## 1. Cuándo usar Meta vs LinkedIn

| Situación | Meta | LinkedIn |
|---|---|---|
| ICP = pymes, autónomos, profesionales | ✔ principal | apoyo |
| ICP = cargos concretos en empresas >500 empleados | apoyo (retargeting) | ✔ principal |
| ACV < 10 k€ | ✔ | caro |
| ABM sobre lista cerrada de cuentas | ✘ | ✔ |
| Retargeting de visitantes web B2B | ✔ barato | caro |

## 2. Arquitectura por presupuesto

| Presupuesto/mes | Estructura |
|---|---|
| 2.000-6.000 € | 1 campaña Leads (Advantage+, lookalikes de clientes como sugerencia), instant form con work email o landing; retargeting incluido |
| 6.000-20.000 € | + campaña de retargeting de contenido (casos, comparativas) + test de canal (landing vs IF) |
| > 20.000 € | Por segmento/vertical; integración CRM completa (oportunidad, valor); lift tests |

## 3. Evento de optimización

- Qualified leads con etapa **SQL** o **demo/diagnóstico celebrado** (CAPI CRM). Si el ciclo hasta SQL > 28 días, usa "MQL aceptado por ventas" o "reunión agendada". (S05-001)
- Web: `Schedule` o evento CRM; Sequenced Events `Lead → Schedule` si está disponible.

## 4. Formulario y oferta

- Oferta: diagnóstico, auditoría, benchmark sectorial, plantilla útil (para retargeting), demo.
- Preguntas: tamaño de empresa (empleados), rol, problema principal, plazo, presupuesto del proyecto (en rangos; evita "facturación personal"). Work email obligatorio si el ICP lo permite.
- Intro: para quién es y qué pasa después.

## 5. Creatividades

- Problema específico del rol y del sector, con lenguaje del cliente.
- Prueba entre pares (logos, casos del mismo sector con métricas).
- Imagen estática con titular fuerte: en B2B 2025, imagen 136 $ vs vídeo 225 $ de CPL en Facebook (S05-044).
- Document/carrusel con "framework" para retargeting.

## 6. Métricas y umbrales

| Métrica | Umbral |
|---|---|
| % leads con email corporativo | > 70% si exiges work email |
| MQL → SQL | Medir por anuncio; un vendor cita 5-10% de MQL→SQL en leads B2B de Meta (sin verificar) |
| Coste por SQL / oportunidad | Contra BE por agenda/SQL de tu calculadora |
| Pipeline generado / inversión | Por cohorte trimestral |

## 7. Ejemplo numérico: servicio B2B de 5.000 €

Contribución 1.910 €/venta (50% coste de entrega, 10% comisión, 2% reembolsos). Funnel: 40% cualifica, 50% agenda, 75% show, 25% cierre → lead→venta 3,75%.
- **BE CPL 71,62 € / target 35,81 €**; BE por agenda 358 € / target 179 €; BE por lead cualificado 179 €.
- 10.000 € a CPL 40 € → 250 leads → 50 agendas (200 €/agenda) → 37,5 shows → **9,4 ventas**, CPA 1.067 €, beneficio 7.906 €.
- Frente a los CPL B2B de Metadata (138-145 $), un CPL de 40 € exige oferta y audiencia de pyme; con CPL de 140 € este servicio **no** es rentable salvo que el cierre suba o haya recurrencia. Haz la cuenta antes de copiar benchmarks.

## 8. Plan de arranque (primeros 45 días)

| Semana | Acciones | Criterio de paso |
|---|---|---|
| 0 | ICP escrito; definición de MQL/SQL con ventas; calculadora (BE por SQL/agenda); CRM (HubSpot/Salesforce) con lead ID e IDs de anuncio; work email y preguntas de tamaño/rol | Lead de prueba con todos los campos y la etapa inicial (`Lead`, contrato §16 en `docs/desarrollo/contratos.md`) en Events Manager |
| 1-2 | 1 campaña Leads, lookalike de clientes como sugerencia, 4-6 anuncios (problema del rol, prueba entre pares); retargeting de visitantes | % leads en ICP ≥ 50-60% |
| 3-4 | Pausar anuncios con 0 SQL tras gasto ≥ BE por SQL; test landing vs instant form | Coste por SQL medido |
| 5-6 | Qualified leads con etapa SQL/reunión si ≥20-30/semana; comparar con LinkedIn a nivel de oportunidad | Coste por oportunidad ≤ target |

## 9. Reglas de decisión rápidas

- % de leads fuera de ICP > 40% → work email, preguntas de descalificación, creatividad más específica.
- Coste por SQL en Meta ≤ LinkedIn y calidad de oportunidad similar → mover presupuesto a Meta; si las oportunidades de Meta son más pequeñas, compara por pipeline en €, no por nº de SQL.

## 10. Errores frecuentes

- More volume sin work email → leads de estudiantes/autónomos fuera de ICP.
- Medir por CPL contra LinkedIn sin mirar SQL.
- Optimizar a una etapa que tarda >28 días.
- No conectar HubSpot/Salesforce correctamente (verifica cobertura en Events Manager, archivo 04).

## Preguntas abiertas

- Comparativa con metodología pública de coste por cliente Meta vs LinkedIn.

## Fuentes clave

- [Meta ads for B2B (2026 B2B Paid Media Benchmark)](https://metadata.io/resources/blog/fb-ad-strategies) — 2026-09-11 (S05-044)
- [Meta Ads B2B Lead Generation Strategy 2026](https://www.involvedigital.com/insights/meta-ads-b2b-lead-generation-strategy) (S05-075)
- `05-leadgen-high-ticket-crm/04-integraciones-crm.md`, `10-b2b-saas-local.md`
