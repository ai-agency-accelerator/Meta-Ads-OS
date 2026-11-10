# aprendizajes/

Lo que aprendes tú en tus cuentas y lo que no es de un cliente concreto. Es parte de **tu instancia**: git no lo sube
(salvo este archivo) y `/actualizar` no lo toca. Si quieres copia de seguridad, guarda esta carpeta junto con
`clientes/` y `contexto/` en un repositorio **privado** propio o en tu nube.

La base de conocimiento del producto (`meta-ads-kb/`) se sustituye con cada versión. Lo que descubres en tus cuentas va
aquí, para que no se pierda al actualizar y para que Claude lo tenga en cuenta.

## Qué va aquí

| Archivo o carpeta | Qué es | Quién lo escribe |
|---|---|---|
| `AAAA-MM-DD-<tema>.md` | Un aprendizaje de tus cuentas que confirma o contradice la base, con su muestra y su ventana | `curador-conocimiento`, desde `/novedades-meta aprendizaje`, `/test-creativo leer` o `/diagnostico` (o tú) |
| `novedades/AAAA-MM-DD.md` | Qué ha cambiado en Meta, verificado, y a qué clientes afecta | `/novedades-meta` |
| `investigacion/<tema>-AAAA-MM-DD/` | Investigación de mercado o de nicho que no es de un cliente (si es de uno, va en `clientes/<slug>/investigacion/`) | `investigador-competencia`, `/competencia`, `/voz-cliente`, workflow `investigacion-mercado` |

Las carpetas se crean la primera vez que hacen falta.

## Formato de un aprendizaje

Un archivo por aprendizaje, `AAAA-MM-DD-<tema>.md` (tema en minúsculas con guiones), con estos campos y una versión
anonimizada al final:

```markdown
# 2026-11-24 · Hooks en ABO, uno por conjunto

- **Negocio:** servicios high-ticket · España
- **Contexto:** cuenta con unas 40 citas al mes, una campaña de captación
- **Cambio o test:** 3 hooks del mismo concepto en ABO, un conjunto por hook con el mismo presupuesto
- **Resultado:** el hook de dolor ganó en coste por cita (61 € frente a 94 €)
- **Muestra y ventana:** 38 citas · 14 días · 7 días clic
- **Etiqueta:** [EMPIRICAL]
- **Confirma o contradice:** confirma `meta-ads-kb/13-sistema-operativo/05-framework-testing-creativo.md`

## Versión anonimizada
En una cuenta de servicios high-ticket, probar hooks del mismo concepto en ABO con un conjunto por hook y el mismo
presupuesto dio un ganador claro en coste por cita con unas 40 citas en 14 días. [EMPIRICAL] (un caso)
```

- **Nada que identifique al cliente ni a personas** en la versión anonimizada: tipo de negocio y mercado, sin nombres,
  sin IDs y sin cifras que permitan reconocer la cuenta.
- **Etiqueta**: `[EMPIRICAL]` si sale de tus datos con muestra suficiente; `[HYPOTHESIS]` si aún no la tiene. Con un
  solo caso es una anécdota: dilo.
- **Confirma o contradice**: el archivo de `meta-ads-kb/` al que afecta. Si lo contradice, `curador-conocimiento` te
  dice si es ruido, un caso particular o algo que ha cambiado en Meta.
- Con CPA solo se detectan diferencias grandes (`meta-ads-kb/13-sistema-operativo/01-principios-de-razonamiento.md`):
  antes de generalizar, que haya pasado en más de una cuenta o con una muestra grande.

## Cómo lo usa el sistema

- `/pregunta` y `mentor-meta` leen las notas más recientes además de la base (pueden ser posteriores a ella) y te dicen
  cuándo tu experiencia y la base no coinciden.
- `/siguiente-anuncio`, `estratega-creativo` y `revisor-estrategia` las tienen en cuenta para no repetir tests ni
  ignorar lo que ya sabes de tus cuentas.
- `/revision-mensual` repasa `novedades/` para ver qué cambios de Meta del mes afectan a cada cliente.
- `/novedades-meta` deja aquí sus notas en lugar de modificar `meta-ads-kb/`.
- Las versiones anonimizadas son las que se pueden compartir con el equipo del producto para que, una vez
  verificadas, entren en la base (`meta-ads-kb/16-aprendizajes-propios/`).
