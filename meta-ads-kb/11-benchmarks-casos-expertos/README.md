# Área 11: Benchmarks, geografías, casos, fracasos, expertos y Voice of Advertiser

> Última verificación: 2026-10-16 · Autor: A11 (agente) · Ledger: `../fuentes/ledger-11-benchmarks-casos-expertos.md` (más de 110 entradas)

## Índice

| Archivo | Contenido |
|---|---|
| [01-benchmarks-2025-2026.md](01-benchmarks-2025-2026.md) | Datos oficiales de Meta (precio por anuncio por región), paneles (WordStream, Triple Whale, Biddyco, AdKit, Gupta, Tinuiti, Skai, Superads), tablas por industria, dispersión, estacionalidad (BFCM 2025), placement, incrementalidad por objetivo, lead gen, mensajería, apps y benchmarks creativos (Motion) |
| [02-como-usar-benchmarks.md](02-como-usar-benchmarks.md) | Para qué sirve un benchmark y para qué no, catálogo de sesgos con ejemplos reales, las 7 preguntas previas, cómo construir el benchmark propio y la matriz de diagnóstico |
| [03-geografias-costes-comportamiento.md](03-geografias-costes-comportamiento.md) | CPM por país, inflación por región, EE. UU., Canadá (Quebec), Reino Unido, España, resto de Europa (LPA y fees), LatAm (pagos, WhatsApp), Australia, Asia; hispanohablantes en EE. UU., España y LatAm |
| [04-escalado-internacional.md](04-escalado-internacional.md) | Cuentas, divisa, zona horaria, dataset, catálogo localizado, Multi-Language Ads, traducción automática, estructura por país o tier, presupuestos mínimos, fees y secuencia de expansión |
| [05-biblioteca-casos-reales.md](05-biblioteca-casos-reales.md) | Unos 17 casos con ficha completa y nota de utilidad (e-commerce, lead gen, local, high-ticket, B2B, infoproductos, mensajería, idioma y metodológicos) |
| [06-biblioteca-fracasos.md](06-biblioteca-fracasos.md) | 10 patrones de fracaso con mecanismo, evidencia, señales y antídoto, más la matriz de diagnóstico |
| [07-expertos-mapa-y-discrepancias.md](07-expertos-mapa-y-discrepancias.md) | Mapa de expertos con fiabilidad A/B/C y 11 discrepancias con el contexto que da la razón a cada postura |
| [08-voice-of-advertiser-2025-2026.md](08-voice-of-advertiser-2025-2026.md) | Encuestas, 12 temas recurrentes (patrón frente a anécdota), cronología del sentimiento y sentimiento por segmento |
| [09-bugs-y-comportamientos-raros.md](09-bugs-y-comportamientos-raros.md) | Bugs y cambios silenciosos por nivel de confirmación (C1–C4), caídas de 2026, anomalías de rendimiento y protocolo ante anomalías |
| [10-espana-latam.md](10-espana-latam.md) | España y LatAm: benchmarks de CPM y CPL por país (con calidad de fuente), impuestos y recargos (España +3 %, Argentina hasta ~53 % con tarjeta), WhatsApp (CTWA→leads no disponible en la UE), pagos, COD y cuotas, regulación española (financiera, cripto, sanitaria, juego, AEPD, influencers), practitioners hispanohablantes y diferencias de enfoque |

## TL;DR del área

1. **La subasta se encarece de forma estructural y desigual:** +12 % de precio por anuncio global en Q1 y Q2 2026, **+20 % en EE. UU. y Canadá**, +21 % en el resto del mundo y +1 % en APAC (Q2 2026). **[OFFICIAL META]**
2. **No existe "el" benchmark:** el CPM mediano va de ~9 $ (AdKit, global) a ~15 $ (Triple Whale, e-commerce) o ~19 $ (cuentas grandes de EE. UU.), y el rango p25–p75 del CPA abarca casi 10 veces. Usa tu histórico ajustado por la inflación oficial. **[EMPIRICAL]**
3. **Un benchmark nunca dice si eres rentable.** El ROAS mediano de e-commerce (1,88) está por debajo del equilibrio de muchas marcas, y el ROAS de plataforma no predice el incremental (Stella: marcas con ROAS superior a 4 e IF inferior a 1). **[EMPIRICAL]**
4. **Estacionalidad real (BFCM 2025):** CPM +57 % con coste por compra −42 % en Black Friday; la trampa es la semana del 8 al 14 de diciembre (CPA +39 %). **[EMPIRICAL]**
5. **Geografía:** un CPM bajo atrae entrega hacia eventos baratos sin valor. Agrupa mercados por valor esperado. Desde el 1-jul-2026 hay **fees de localización del 2–5 %** (España 3 %) fuera del presupuesto, y en la UE el LPA es obligatorio en el consentimiento desde enero de 2026. **[OFFICIAL META]** / **[EMPIRICAL]**
6. **Hispanohablantes:** en EE. UU., audiencia bilingüe con WhatsApp al 56 % e Instagram al 62 % (Pew 2025); mejor multi-idioma que filtro de idioma. En LatAm, pagos locales y WhatsApp. No reutilizar creatividades de España tal cual. **[EMPIRICAL]** / **[STRONG INFERENCE]**
7. **Los casos valiosos miden el halo o reconcilian con el backend** (Amazon con +23 %, el 57,9 % de los pedidos incrementales en Amazon, ROMI de "no rentable" a 204 %). **[EMPIRICAL]**
8. **Fracaso n.º 1: optimizar o juzgar por un evento que no es el negocio** (clics sin conversaciones, leads de 65+, retargeting no incremental, clientes existentes). **[EMPIRICAL]**
9. **Expertos:** las mejores fuentes publican método y corrigen. Haus revirtió su conclusión sobre la IA y CTC documentó su evolución de 2023 a 2026. Las discrepancias serias se explican por el contexto (tamaño, AOV, recompra, método de medición). **[EMPIRICAL]**
10. **Voice of Advertiser:** el 76 % cita el CPM como su principal preocupación; el 52 % ve "mixtos" los anuncios con IA; el 38 % dice que Andromeda complicó el testing. Pérdida de control, baneos y caídas son patrones reales; "el CPM se ha duplicado esta semana" es anécdota. **[EMPIRICAL]**
11. **Lo más peligroso de 2026 son los fallos silenciosos:** API con datos vacíos sin error, controles y ajustes por defecto que cambian (5 % en placements excluidos, audiencias de 730 días, IA creativa activada) y facturas que no cuadran. **[OFFICIAL META]** / **[EMPIRICAL]**

## Cambios 2025-2026 detectados en esta área (con fecha)

| Fecha | Cambio | Evidencia |
|---|---|---|
| ene-2025 | Retirada de las exclusiones de detailed targeting | [OFFICIAL META] (vía PPC Land) |
| 2025 | Advantage+ Sales sustituye a ASC; el tope de "existing customer budget" deja de estar disponible | [OFFICIAL META] (vía Loomer) |
| jul-2025 | Haus: 58 % de las marcas con mejor iROAS en Manual que en Advantage+ | [EMPIRICAL] |
| 8-oct-2025 | Hasta un 5 % del gasto por placement excluido (activado por defecto en Ads Manager y desactivado en la API) | [OFFICIAL META] |
| oct-2025 | Despliegue de Andromeda "completo" (según agencias y vendors) | [STRONG INFERENCE] |
| 12-ene-2026 | Retirada de 7d view y 28d view en Ads Insights API (datos vacíos sin error) | [EMPIRICAL] / anunciado |
| ene-2026 | La UE obliga a elegir entre anuncios personalizados y LPA | [OFFICIAL META] |
| mar-2026 | Anuncio de los fees de localización; redefinición del clic en atribución | [OFFICIAL META] / [EMPIRICAL] |
| 18-may-2026 | Audiencias de compradores de 180 a 730 días automáticamente | [EMPIRICAL] |
| 1-jul-2026 | Fees de localización en vigor (Reino Unido 2 %; España, Francia e Italia 3 %; Austria y Turquía 5 %) | [OFFICIAL META] |
| 16-jul-2026 | Haus: la IA ya supera a la atribución standard (1,26×) | [EMPIRICAL] |
| 29-jul-2026 | Q2 2026: precio por anuncio +12 %, EE. UU./Canadá +20 %; nuevo ranking (GEM) | [OFFICIAL META] |
| 6-ago-2026 | Desgloses de dispositivo, hora y frecuencia en la API pasan a opt-in | [OFFICIAL META] |
| 6-ago-2026 | CTC: el cost cap entrega el 140 % del objetivo; el bid cap pasa a ser su default | [EMPIRICAL] |
| 20-ago-2026 → | Retirada progresiva de exclusiones de placement en ad set; value rules hasta −90 % | [OFFICIAL META] (parcial) |
| 26-ago-2026 | Columna "Creative diversity" (en desarrollo) | [OFFICIAL META] |
| 15-sep-2026 | Meta One (soporte humano de pago) | [OFFICIAL META] |
| ~17-sep-2026 | CPM −30 % con CTR y compras a la baja en varios países (sin causa confirmada) | [EMPIRICAL] (C2) |
| 7-oct-2026 | Customer Lifecycle Strategy (solo clientes nuevos) para todos, según CTC | [EMPIRICAL] |
| 30-oct-2026 | Nuevos términos que incorporan la IA generativa | [OFFICIAL META] (fecha) |

## Para contrastar con otras áreas

- **Área 01 (subasta/ML):** ¿qué es exactamente GEM/"Generative Recommender" frente a Andromeda, y hay confirmación oficial de que los anuncios similares se agrupan como una "entidad"? CTC lo afirma sin fuente oficial. ¿Umbral actual de aprendizaje (50 o 25 eventos por semana en Advantage+)?
- **Área 02 (estructura):** discrepancia D1 consolidar frente a segmentar y D11 escalado; la "regla del 20 %" no tiene fuente oficial verificada.
- **Área 03 (creatividad):** D2 volumen frente a diversidad; los datos de Motion y CTC son correlacionales; el claim de "lifespan de 2–4 semanas" no tiene fuente.
- **Área 04 (tracking/medición):** retirada de ventanas en la API, redefinición del clic de mar-2026, reversión de Haus sobre la IA y discrepancia D5 (Loomer frente a Haus); que el 7dc infra-reporte ~20 % (CTC) frente al +15 % de Haus para solo-clic.
- **Área 05 (lead gen):** el debate de instant forms (D7); las cifras de Meta para conversion leads varían (10/15/16/19/21 %) según el documento.
- **Área 06 (e-commerce/apps):** Customer Lifecycle Strategy (eficacia sin datos); los umbrales de trial frente a pago de RocketShip.
- **Área 08 (cuenta/políticas):** decisión de la Oversight Board de jun-2026, Meta One y el alcance real de los términos del 30-oct-2026.
- **Área 09 (bidding):** el estudio de CTC sobre cost controls frente a Foxwell y Loomer (D3); la puja como selector de AOV del cliente.
- **Área 10 (cambios):** la cronología de esta área debería cruzarse con su changelog; la retirada de exclusiones de placement por objetivo.

## Huecos y preguntas abiertas

- ~~Reddit no accesible~~ → **resuelto el 16-oct-2026**: barrido directo de 18.304 posts vía Arctic Shift (frecuencia de temas y patrones R1–R11 en [08](08-voice-of-advertiser-2025-2026.md); incidencias en [09](09-bugs-y-comportamientos-raros.md)).
- **Benchmarks de coste por venta u oportunidad** en lead gen por industria: no existen públicamente con método.
- **España y LatAm:** sin benchmarks fiables de CVR, CPA o CPL ni casos públicos con ficha completa. Sin practitioners hispanohablantes con evidencia pública comparable.
- **LPA en la UE:** adopción e impacto en rendimiento no publicados.
- **Apps de suscripción y SaaS con CRM a cierre:** sin casos completos.
- **Q3 2026 de Meta:** se publica a finales de octubre de 2026; hay que actualizar la inflación por región.
- **Causa de las anomalías de jul y sep de 2026:** sin confirmar.
