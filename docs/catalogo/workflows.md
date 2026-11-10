# Workflows (5): los modos profundos

Un workflow coordina a varios agentes en paralelo y en fases, con verificación cruzada entre ellos. Da mejores
resultados que una skill sola cuando hay mucho en juego, a cambio de **bastante más uso de Claude**. Viven en
`.claude/workflows/<nombre>.js`.

- **Siempre se lanzan desde su skill** con la palabra `profundo` (o `--lote`). La skill te dice antes cuántos agentes
  usará y el coste aproximado, y espera tu sí.
- **Ninguno escribe en Meta, GoHighLevel ni Stripe** ni ejecuta órdenes de pago del motor de vídeo. Terminan en un
  informe, unos briefs, unas piezas o un plan que apruebas tú.
- Con el plan Pro, resérvalos para lo que lo merece: una cuenta heredada, un lanzamiento, un lote importante.

| Workflow | Se lanza con | Qué orquesta | Agentes y coste |
|---|---|---|---|
| `auditoria-profunda` | `/auditoria profundo <cliente>` | Cuenta, señal, políticas y funnel (más negocio si hay CRM o Stripe) en paralelo; otro agente intenta refutar cada hallazgo P0/P1 con sus propias consultas; informe único con scorecard y plan 30/60/90 | ≈7–13 · alto |
| `investigacion-mercado` | `/competencia profundo <cliente>` · `/voz-cliente profundo <cliente>` | Ad Library, landings y ofertas, voz del cliente y economía del nicho en paralelo → matriz de ángulos priorizada, huecos e hipótesis de test, verificada por `revisor-estrategia` | ≈5–8 · medio |
| `estudio-creativo` | `/siguiente-anuncio <cliente> profundo` · `/brief-creativo profundo <cliente>` | Ganadores con la capa más baja de verdad (y `analista-cuantitativo` intentando tumbarlos) → ángulos para explotar y explorar → jueces de estrategia y de espectador → briefs con guion → políticas | ≈11–17 con 3 conceptos · alto |
| `lote-creativo` | `/producir-video <cliente> <lote> --lote` · `/producir-estatico <cliente> <lote> --lote` | Producción en paralelo sin gastar (el motor en simulado o con las órdenes listas para confirmar) → crítica y políticas por pieza → arreglos → piezas con `LEEME.md` | ≈9–14 con 3 piezas · medio-alto |
| `lanzamiento-completo` | `/lanzar-campana <cliente> profundo` | Gates de economía, funnel y señal en paralelo (uno en rojo para el lanzamiento) → textos → políticas → plan de campaña dentro de los topes → revisión de `revisor-estrategia` | ≈8–9, hasta ≈30 si tiene que generar investigación y briefs · alto |

## Cuándo merece la pena

| Situación | Normal | Profundo |
|---|---|---|
| Revisión trimestral de una cuenta que va bien | `/auditoria` | — |
| Cuenta heredada o con problemas, antes de escalar o de proponer un cambio grande a un cliente | — | `auditoria-profunda` |
| Echar un vistazo a dos competidores | `/competencia` | — |
| Nicho nuevo o cliente nuevo sin investigación previa | — | `investigacion-mercado` |
| Siguiente anuncio de una cuenta con datos | `/siguiente-anuncio` | `estudio-creativo` si el lote es grande o la cuenta está estancada |
| Una o dos piezas | `/producir-video` · `/producir-estatico` | — |
| Lote de varias piezas para publicar juntas | — | `lote-creativo` |
| Campaña nueva en una cuenta que ya conoces | `/lanzar-campana` | — |
| Primer lanzamiento de un cliente nuevo | — | `lanzamiento-completo` |
