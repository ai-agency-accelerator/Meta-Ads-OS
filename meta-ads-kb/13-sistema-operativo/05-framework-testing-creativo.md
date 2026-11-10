# Framework de testing creativo — el sistema completo

> Última verificación: 2026-10-16 · Autor: agente principal · Ámbito: protocolo operativo que se aplica a cualquier
> cuenta. Fundamento y datos en [03/05-testing-creativo](../03-creatividad/05-testing-creativo.md),
> [03/02-taxonomía](../03-creatividad/02-taxonomia-angulo-concepto-hook-ejecucion.md),
> [03/06-fatiga](../03-creatividad/06-fatiga-creativa.md) y [03/13-feedback loop](../03-creatividad/13-produccion-y-feedback-loop-creativo.md).

## TL;DR

- **Testeamos ideas, no píxeles.** Niveles: oferta > ángulo > concepto > formato/ejecución > hook/body > copy. Cuanto más
  bajo el nivel, menor el efecto y menos útil el CPA para medirlo. **[STRONG INFERENCE]**
- **"Nuevo creativo" = nuevo ángulo o concepto** (otra razón de compra, otra persona, otra dramatización). Cambiar el hook
  es una **iteración**. **[STRONG INFERENCE]**
- **Estructura por defecto: híbrida.** BAU (campaña principal con 10–20 anuncios de conceptos distintos) + vía de gasto
  garantizado para conceptos nuevos (herramienta nativa *Creative testing*, ad set/campaña de test, o *push delivery*
  cuando esté disponible). **[CONTESTED]** entre practitioners; la elección depende de volumen. **[EMPIRICAL]**
- **Kill rule**: 0 conversiones tras **2–3× CPA objetivo** (5–13,5 % de falsos negativos), o CPA ≥2–3× la media con gasto
  relevante. **Nunca a 1× CPA** (37 % de falsos negativos). **[STRONG INFERENCE]** (Poisson)
- **Winner provisional** ≥10–20 conversiones con CPA ≤ objetivo y Meta le da gasto; **confirmado** ≥30–50 conversiones,
  ≥7 días y CPA estable al subir gasto. **[STRONG INFERENCE]**
- **Volumen**: anuncios nuevos cada semana; capacidad de test ≈ presupuesto semanal de test / (2–3 × CPA). Hit rate
  esperado ~5 %: más volumen diverso = más ganadores. **[EMPIRICAL]** (Motion 2026)

---

## 1. Taxonomía que usamos (para no engañarnos)

| Nivel | Definición | Ejemplo (almohada ergonómica) | ¿Cuenta como "nuevo creativo"? |
|---|---|---|---|
| **Oferta** | Qué se da a cambio de qué (precio, bundle, garantía, bonus) | 100 noches de prueba vs 2x1 | Sí (y cambia la economía) |
| **Ángulo** | La razón de compra / el "por qué" para un segmento | Dolor cervical al despertar vs dormir fresco en verano | Sí |
| **Concepto** | La idea que dramatiza el ángulo | "Mañana con y sin almohada" (split-screen) vs fisio explicando | Sí |
| **Formato / ejecución** | El envase: UGC, estático, demo, founder, carrusel, podcast clip | El mismo concepto como UGC selfie o como estático comparativo | Parcial (iteración de formato) |
| **Hook** | Primeros 1–3 s / primera línea | "Si te despiertas con el cuello rígido…" vs "Mi fisio me prohibió…" | No (iteración) |
| **Body** | Desarrollo: mecanismo, prueba, objeciones | Explicación del material vs testimonio | No (iteración) |
| **Copy / CTA** | Primary text, headline, description, botón | — | No |

Regla de nomenclatura: `AAAAMMDD_angulo_concepto_formato_h<n>[-c<n>]` (`h2` = hook 2; `h2-c1` = hook 2 con el cuerpo 1),
para poder agregar resultados por ángulo y concepto. Es el formato que valida `herramientas/nomenclatura.py`
(contrato §7, `docs/desarrollo/contratos.md`).

## 2. Qué test, con qué métrica, en qué estructura

| Pregunta | Métrica de decisión | Estructura | Volumen mínimo orientativo |
|---|---|---|---|
| ¿Esta oferta mejora la economía? | CPA/ROAS + AOV + margen; idealmente lift | A/B test (Experiments) o split por campaña/landing | Alto (≥100 conv/brazo para diferencias del 30–50 %) |
| ¿Este ángulo/concepto abre un bolsillo rentable? | CPA a volumen + capacidad de gasto | Gasto garantizado (test nativo o ad set de test) → luego BAU | 2–3× CPA para vivir/morir; ≥20–30 conv para confirmar |
| ¿Qué ejecución del concepto escala mejor? | CPA + spend share en BAU | BAU o test nativo | ≥10–20 conv |
| ¿Qué hook para y selecciona mejor? | Hook rate + CTR **con CVR estable** | Test nativo (2–5 variantes) o anuncio flexible | ≥1.000–2.000 impresiones por variante para el filtro de atención |
| ¿Qué body retiene y convence? | Hold rate, CTR, CVR | Test nativo | Idem |
| ¿Qué copy? | CTR, CVR | Variaciones de texto en el mismo anuncio | Alto en clics |

Tabla de potencia (conversiones por brazo, α=0,05, potencia 80 %): Δ10 % ≈ 1.700 · Δ20 % ≈ 470 · Δ30 % ≈ 230 ·
Δ50 % ≈ 95 · 2× ≈ 33 · 3× ≈ 13. **[STRONG INFERENCE]**

## 3. Estructura operativa por tamaño de cuenta

| Gasto | Estructura | Anuncios activos | Nuevos/semana (orientativo) |
|---|---|---|---|
| < 100 €/día | Todo en el ad set único; lotes de 2–4 conceptos cada 1–2 semanas; apagar a 2–3× CPA sin conversión | 3–8 | 2–4 (conceptos o iteraciones) |
| 100–500 €/día | BAU + herramienta *Creative testing* (≤20 % del presupuesto, 7 días) para variantes; o ad set de test ABO para conceptos realmente nuevos | 8–15 | 4–8 |
| 500–5.000 €/día | Híbrido: BAU 10–20 anuncios + campaña/ad set de test con criterios de graduación; campaña de "underspend" opcional | 10–20 por ad set | 8–20 |
| > 5.000 €/día | Testing industrializado: pipeline de briefs, test semanal, graduación, underspend, análisis por ángulo | 15–30+ | 20–50+ |

Referencias: Meta (nov-2024) recomendaba anuncios nuevos cada semana, ≥20 anuncios diversificados en la campaña
Advantage+ y 20–30 % del presupuesto a testing; la herramienta nativa recomienda ≤20 %. Motion 2026 (media → top 25 %
de anuncios nuevos/semana): <10K$/mes 2,8→4,8; 10–50K 4,1→8,1; 50–200K 6,7→16; 200K–1M 11,2→31; >1M 18,9→54,6.
**[OFFICIAL META]** + **[EMPIRICAL]**

Límites: 50 anuncios no archivados por ad set y 5.000 ad sets por cuenta (referencia oficial de la Marketing API); los
"150" que circulan eran el límite de las antiguas ASC. Límite de anuncios activos por Página según gasto pico
(250 / 1.000 / 5.000 / 20.000). **[OFFICIAL META]**

## 4. Ciclo semanal

```
Lunes      Análisis: qué ganó/perdió y POR QUÉ (ángulo, hook, prueba, formato) → registro de aprendizajes
Martes     Ventana de edición: apagar perdedores (kill rules), graduar ganadores, lanzar lote nuevo
Miércoles  Briefs del siguiente lote (2–3 iteraciones de ganadores + 2–5 conceptos nuevos)
Jue–Vie    Producción
Siguiente  Lanzamiento del lote en la ventana de edición
```

## 5. Escalera de decisión por anuncio (prospección, optimizando a compra/lead cualificado)

| Momento | Señal | Acción |
|---|---|---|
| 1.000–2.000 impresiones | Hook rate < 50 % de la mediana de la cuenta **y** CTR muy bajo | Candidato a apagar o a iterar el hook (sin "confirmar" con CPA) |
| ~1× CPA gastado | Cualquier resultado | No decidir por CPA |
| 2–3× CPA | 0 conversiones | Apagar |
| 2–3× CPA | 1–3 conversiones y CPA ≤1,5× objetivo | Mantener; mirar CTR/CVR/ATC |
| ≥10–20 conversiones | CPA ≤ objetivo y Meta le asigna gasto | Winner provisional → escalar/mover a BAU |
| ≥30–50 conversiones y ≥7 días | CPA estable con gasto creciente | Winner confirmado → iterar hooks/formatos + ángulos adyacentes |
| Cualquier momento | CPA ≥2–3× media con gasto relevante | Apagar |

High-ticket: usar un evento proxy validado por CRM (lead cualificado, cita) y confirmar con coste por venta de la cohorte.

## 6. Higiene del test (separar creatividad de ruido de media buying)

- Mismo objetivo, evento, ventana, targeting, placements y puja entre variantes; mismo periodo (cohortes por fecha).
- No subir/bajar presupuesto a mitad de un test.
- Documentar qué *Advantage+ creative enhancements* están activas por anuncio; desactivar las que alteran el mensaje en tests
  controlados.
- No comparar periodos que cruzan cambios de definición (link click desde mar-2026).
- Un anuncio **sin gasto** en BAU **no está testeado**: darle gasto garantizado o asumir que no sabemos.
- Exigir confirmación al escalar: los ganadores con 5–10 conversiones regresan a la media.

## 7. Qué hacer con los resultados

| Resultado | Acción |
|---|---|
| Concepto gana | 3–5 iteraciones (hooks, formatos, personas) + buscar ángulos adyacentes |
| Ángulo gana con un concepto y pierde con otros | El ángulo vale; el concepto ganador es la mejor dramatización → nuevos conceptos del mismo ángulo |
| Todo pierde | Revisar oferta y landing antes que seguir produciendo (¿CTR bien y CVR mal? → post-clic) |
| CTR altísimo, CPA malo | Promesa que atrae curiosos o desalineada con la landing → revisar message match y calidad del tráfico |
| Ganador se fatiga | Iterar si el concepto está cansado; nuevo ángulo si el bolsillo está agotado; nueva oferta si es la oferta |

## 8. Registro de aprendizajes (obligatorio)

| Fecha | Ángulo | Concepto | Formato | Hook | Gasto | Conv | CPA | Hook rate | CTR | CVR | Veredicto | Por qué creemos que ganó/perdió | Siguiente test |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

Un aprendizaje no es un anuncio ganador: es una hipótesis sobre el mercado que guía el siguiente brief.
