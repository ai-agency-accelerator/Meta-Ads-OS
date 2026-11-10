# Playbook: e-commerce DTC en Meta Ads (2026)

> Última verificación: 2026-10-16 · Autor: A06 (agente) · Ámbito: marcas que venden en su propia web (Shopify u otra), ticket 20–300 €, España/UE/EE. UU. Profundidad en `06-ecommerce-apps/` (01–11). Estructura general y bidding: carpetas 02 y 09; creatividad: carpeta 03; medición: carpeta 04.

## TL;DR

- Meta es el canal de adquisición principal para la mayoría de DTC (Triple Whale BFCM 2025: Meta = 67,6 % del gasto publicitario rastreado en >33.000 tiendas). Pero el ROAS de plataforma no es beneficio: gestiona con **CM3, MER, nCAC y % de clientes nuevos**. [EMPIRICAL] + [STRONG INFERENCE]
- Estructura 2026 por defecto: **1 campaña Advantage+ sales de adquisición** (Customer lifecycle = nuevos o exclusión de clientes) + **test creativo** + catálogo si > 100 SKUs + retención acotada con holdout. Escala con creatividad, no con estructura. [STRONG INFERENCE] + [OFFICIAL META] (herramientas)
- Evento: **Purchase con valor**, Pixel + CAPI deduplicados; ojo con IVA y envío dentro del valor. [OFFICIAL META] (dedup) + [STRONG INFERENCE]
- Antes de gastar 1 €: calcula **ROAS break-even = (1 + agencia% + location fee% + creativo%) / CM2 %** sobre la base de valor que ve Meta. [STRONG INFERENCE]
- Valida al menos una vez al año (y antes de BFCM) con un **test de incrementalidad**; Haus (640 tests): Meta aporta ~19 % de lift medio, Advantage+ gana a manual solo en el 42 % de marcas, 50/50 es la peor mezcla. [EMPIRICAL]

## 1. Cuándo usar Meta (y cuándo no)

| Usar Meta como canal principal | Meta como secundario o no todavía |
|---|---|
| Producto visual o demostrable en 3–15 s | Producto sin diferenciación con precio peor que Amazon |
| CM2 ≥ ~40 % sobre ventas brutas o AOV ≥ ~40 € | CM2 < 30 % y AOV < 30 € (no escala ningún canal de pago en primer pedido) |
| Demanda latente (la gente no lo busca, pero lo compra al verlo) | Demanda puramente de búsqueda con intención explícita (Google primero) |
| Capacidad de producir 5–20 conceptos creativos/mes | Sin capacidad creativa |
| Tracking funcionando (Pixel + CAPI, match de catálogo ≥ 90 %) | Tracking roto: arreglar primero |

## 2. Arquitectura por presupuesto

| Presupuesto/día | Campañas | Clientes existentes | Catálogo | Creatividad nueva/semana | Medición |
|---|---|---|---|---|---|
| **€100** | 1 Ventas Advantage+ (1 ad set) | Definir en cuenta; excluir si email fuerte | Solo como formato si > 50 SKUs | 3–5 | MER, nCAC blended, CPA vs break-even |
| **€500** | Principal Advantage+ (80–90 %) + test creativo (10–20 %) | Customer lifecycle = nuevos o 2 ad sets con cap | Dentro de la principal | 8–15 | + breakdown de segmentos semanal |
| **€5.000** | 1–2 principales (por mercado/margen) + test + catálogo prospección (si catálogo grande) + retención 3–8 % | Separación estricta adquisición/retención | Product sets por margen y tentpole | 20–40 | Geo-lift / Conversion Lift ×2/año |
| **€50.000** | Varias por mercado/categoría; pujas mixtas (lowest cost + cost cap/ROAS mínimo); mid/upper-funnel 5–10 % medido | Igual + reactivación | Columna vertebral si catálogo grande | 50–150 | Programa continuo: geo-lift trimestral + MMM causal |

Regla de señal: nº de ad sets ≈ compras semanales / 50 como máximo. [OFFICIAL META] (umbral ~50) + [STRONG INFERENCE]

## 3. Evento y puja

- **Purchase con valor**; deduplicación Pixel/CAPI con `event_id`; EMQ alto.
- Si < ~15 compras/semana y la cuenta no estabiliza: probar ATC con cautela y medir con nCAC [CONTESTED — ver `06-…` §1].
- Puja: lowest cost hasta tener 4+ semanas estables; luego cost cap o ROAS mínimo en una campaña paralela para proteger margen.
- Ventana: 7d clic por defecto; Dr. Squatch (Haus) encontró +6,51 % de revenue nuevo optimizando a 7DC vs 1DC. Considera probar Incremental Attribution (Haus 2026: 1,38× vs estándar en DTC puro, jul-2025–jun-2026). [EMPIRICAL]

## 4. Creatividades

| Tipo | Uso | Nota |
|---|---|---|
| Concepto problema-solución / demo (vídeo 9:16) | Prospección (TOF) | Javvy: TOF >13× más incremental que BOF |
| UGC / creadores / partnership ads | Prospección y prueba social | Sephora: creadores + catálogo 1,56× iROAS omnicanal |
| Estático con oferta/beneficio | Captura de demanda | Riesgo de ser "BOF caro" no incremental |
| Catálogo (carrusel/colección, vídeo de producto) | Catálogos > 100 SKUs | Precio visible y 9:16 nativo (Rock Luggage +35 % ROAS, vendor) |
| Lanzamientos / novedades | Recuperar incrementalidad | Ridge: iROAS > 4 $ (114 % sobre objetivo) |

Cadencia: con 5–8 % de anuncios ganadores (Motion 2026), lanzar 30–60 anuncios/mes para encontrar 2–3 ganadores. [EMPIRICAL, vendor]

## 5. Funnel

1. **Anuncio** (concepto) → 2. **Landing** coherente con el ángulo (PDP, landing por ángulo, quiz en categorías complejas) → 3. **Checkout acelerado** (Shop Pay/Apple Pay/PayPal; probado en navegador in-app de IG/FB) → 4. **Captura** email/SMS (pop-up, quiz) → 5. **Post-compra** (email/SMS, cross-sell) → 6. **Recompra** (retención propia; Meta solo para reactivación con holdout).

## 6. Métricas y umbrales

| Métrica | Umbral / regla |
|---|---|
| ROAS de plataforma | ≥ ROAS break-even / factor de incrementalidad (si IF desconocido, asume 0,7–0,8 para prospección y menor para retargeting) [HYPOTHESIS en IF] |
| MER | ≥ MER break-even (= ROAS break-even con revenue total) |
| nCAC blended | ≤ CM2 del primer pedido (sin recompra probada) o ≤ CM2 acumulado a 90–180 días (con recompra) |
| CM2 / nCAC (8x) | > 1 escalar; 0,7–1 solo con recompra; < 0,7 parar |
| % gasto en existentes (breakdown) | > 20–30 % en adquisición → restringir |
| Match rate catálogo | ≥ 90 % (mínimo 70 %) [OFFICIAL META] |
| Frecuencia prospección | Alerta si > 2,5–3/semana con CTR cayendo |
| Escalado | +20–30 % por paso en campañas estables; parar si el nCAC marginal supera el objetivo |

## 7. Errores frecuentes

- Break-even = 1 / margen bruto (ignora IVA, envío, pago, devoluciones, agencia, location fees).
- Celebrar ROAS alto con 50–70 % del revenue de clientes existentes.
- Fragmentar en muchos ad sets por intereses.
- Mezcla 50/50 Advantage+ y manual "por diversificar".
- No producir creatividad al ritmo del presupuesto.
- Retargeting con ventanas de 180 días.
- Cambios estructurales en noviembre.

## 8. Ejemplo numérico completo

**Marca**: cosmética DTC, España. Pedido medio 48,40 € con IVA (40 € sin IVA). CM2 por pedido 22,02 € (45,5 % sobre el valor con IVA). Agencia 10 %, creativo 10 %, location fee 3 % → f = 0,23.

1. **ROAS break-even** (plataforma, valor con IVA) = 1,23 / 0,455 = **2,70**. CPA break-even = 22,02 / 1,23 = **17,90 €**.
2. **Recompra**: cohortes muestran +0,5 pedidos a 180 días con CM2 de 24 € → CM2 a 180 días = 22,02 + 12 = 34,02 € → **nCAC objetivo a 180 días** = 34,02 / 1,23 = **27,66 €** (con colchón 80 %: **22 €**).
3. **Presupuesto €500/día**: a nCAC 22 € → ~23 clientes nuevos/día → ~159/semana → suficiente para 2–3 ad sets; estructura: principal Advantage+ con Customer lifecycle = nuevos (85 %) + test creativo (15 %).
4. **Lectura de la semana**: gasto 3.500 €; Meta reporta ROAS 3,6 (12.600 €); breakdown: 25 % existentes. Tienda: 140 clientes nuevos de todas las fuentes; otros gastos de adquisición 600 € → nCAC blended = (3.500 × 0,75 + 600) / 140 = **23,0 €** (incluyendo en el numerador solo el gasto que fue a adquisición). Ligeramente por encima del objetivo con colchón (22 €) y por debajo del máximo (27,66 €) → mantener, no escalar; trabajar creatividad para bajar nCAC.
5. **Decisión de escalado**: subir a €650/día solo si dos semanas seguidas el nCAC ≤ 22 € y el MER no cae por debajo de 2,7 + margen objetivo.

## Fuentes clave

- Ver `06-ecommerce-apps/03-advantage-plus-sales-ecommerce.md`, `04-…`, `05-…`, `06-…`, `11-…` (fuentes completas).
- [The Meta Report (Haus)](https://www.haus.io/blog/the-meta-report-lessons-from-640-haus-incrementality-experiments) — 2025-07-28 — vendor
- [Is Meta's Incremental Attribution Outperforming… (Haus)](https://www.haus.io/blog/is-metas-incremental-attribution-outperforming-standard-attribution-what-the-data-shows) — 2026-07-16 — vendor
- [Advantage+ Campaigns](https://developers.facebook.com/docs/marketing-api/advantage-campaigns) — Meta for Developers — meta-developers
- [Meta Advertising Week 2026 tools](https://www.relevantaudience.com/meta/meta-advertising-week-new-york-2026-ad-tools/) — 2026-10 — agencia
- [2026 creative benchmarks (Motion)](https://motionapp.com/events/2026-creative-strategy-bootcamp/homebase/2026-creative-benchmarks) — 2026 — vendor
- [Black Friday Facebook Ads (Triple Whale)](https://www.triplewhale.com/blog/facebook-ads-bfcm) — 2025-2026 — vendor (vía resumen)
