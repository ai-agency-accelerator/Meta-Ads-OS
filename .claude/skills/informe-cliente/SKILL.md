---
name: informe-cliente
description: "Convierte el informe interno (semanal, mensual, auditoría o diagnóstico) en un informe para el cliente de la agencia: su negocio primero, qué se hizo y por qué, qué viene y qué necesitamos de él, sin jerga y con la marca de la agencia, en Markdown y PDF. Nunca se envía solo."
argument-hint: "<cliente> [semanal|mensual|auditoria|diagnostico] [AAAA-Www | AAAA-MM | fecha]"
---

# /informe-cliente

Entrada: `$ARGUMENTS`. Solo para fichas con `relacion: cliente`. Parte siempre de un informe interno ya hecho: este
comando no analiza la cuenta.

- **Marco:** `meta-ads-kb/14-playbooks/playbook-agencias-consultores.md` (parte B, §6 contrato y reporting),
  `meta-ads-kb/09-bidding-escalado-economia-analitica/10-dashboards-reporting.md`, plantilla de informe en
  `meta-ads-kb/13-sistema-operativo/10-plantillas.md` §5, aprendizaje y esperas en
  `meta-ads-kb/02-estructura-campanas/03-learning-phase.md`.
- **Agentes:** `gestor-cliente` (redacción y PDF), `revisor-politicas` solo si el informe incluye piezas o textos
  nuevos para aprobar.
- **Herramientas:** `render.py pdf` con `plantillas/html/informe-cliente.html`.
- **Lee:** ficha (objetivo del trimestre, economía, `relacion`), el informe interno de origen
  (`informes/semanal/AAAA-Www.md`, `informes/mensual/AAAA-MM.md`, `auditorias/<AAAA-MM-DD>-auditoria.md` o
  `informes/diagnosticos/…`), `change-log.md`, `datos/` (agregados), `cohortes-leads.md`, la marca de la agencia.
- **Escribe:** `clientes/<slug>/informes/<AAAA-MM-DD>-informe-cliente.md`, `.json` y `.pdf`.

## Pasos

1. **Origen.** Localiza el informe interno del periodo pedido. Si no existe, haz antes `/informe-semanal`,
   `/revision-mensual` o `/auditoria`: un informe al cliente sin análisis detrás no se hace.
2. **Marca de la agencia:** `clientes/<slug-de-la-agencia>/marca/marca.json`, donde la agencia es la ficha con
   `relacion: propio`. Si hay varias o ninguna, pregunta cuál usar; sin marca, el PDF sale con la marca por defecto y
   se avisa.
3. **Redacción** (`gestor-cliente`), en este orden:
   - una frase de veredicto y 3–5 frases de resumen;
   - **su negocio:** citas, ventas, pruebas o clientes de pago y su coste frente al objetivo de la ficha (no CTR ni CPM
     salvo que expliquen algo);
   - el embudo de la cohorte (lead → cita → asistencia → venta, o registro → prueba → pago), separando lo que es de
     marketing de lo que depende de su proceso comercial (rapidez de respuesta, asistencia, cierre);
   - qué hicimos y por qué (del change log, con la fecha en que se evalúa cada cosa) y qué aprendimos;
   - qué viene y **qué necesitamos de él** (material, accesos, aprobaciones, cambios en ventas);
   - notas de medición: periodo, ventana de atribución, días que aún pueden cambiar, de dónde sale cada cifra.
   Tono: el tratamiento que use la agencia con ese cliente (tuteo por defecto), fechas legibles, sin jerga sin
   traducir, sin esconder errores propios (se explican con su arreglo) y sin prometer resultados.
4. **Datos para el PDF** en `clientes/<slug>/informes/<AAAA-MM-DD>-informe-cliente.json` con la forma de
   `plantillas/html/ejemplos/informe-cliente.json` (`titulo`, `cliente`, `agencia`, `periodo`, `ventana_atribucion`,
   `veredicto`, `resumen`, `kpis`, `embudo`, `tablas`, `decisiones`, `proximos_pasos`, `medicion`). Solo agregados:
   ningún dato personal de leads o pacientes; nombres de anuncio y campaña sí.
5. **PDF:**
   `uv run --extra render python -I herramientas/render.py pdf plantillas/html/informe-cliente.html --datos clientes/<slug>/informes/<AAAA-MM-DD>-informe-cliente.json --salida clientes/<slug>/informes/<AAAA-MM-DD>-informe-cliente.pdf --marca clientes/<slug-de-la-agencia>/marca/marca.json`.
   Guarda también la versión en texto (`.md`) para copiar en un email.
6. **Revisión:** abre el PDF y compruébalo contra el informe interno: cada cifra igual, mismo periodo y ventana, ninguna
   promesa, ningún dato de otro cliente. Corrige y vuelve a renderizar si hace falta.
7. **Entrega al operador:** rutas del PDF y del `.md`, y un borrador de email o WhatsApp para acompañarlo
   (`gestor-cliente`). **Nada se envía al cliente desde el sistema**: lo envías tú.

## Reglas

- Las cifras salen del informe interno; si al redactar aparece una incoherencia, se arregla primero allí.
- Nunca datos de otros clientes de la agencia ni comparaciones con ellos sin anonimizar y agregar.
