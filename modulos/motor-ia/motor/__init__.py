"""Motor autónomo de anuncios en vídeo.

Capas principales:
- models      → contratos de datos (marca, producto, actor, brief, plan, timeline, QA, costes)
- store       → base de datos SQLite + almacén de assets direccionado por contenido
- costs       → libro de costes, tabla de precios y guardián de presupuesto
- providers   → adaptadores intercambiables (Gemini, fal, OpenAI, mock, …)
- pipeline    → estrategia, guion, storyboard, router, actores, escenas, voz, producto
- editing     → timeline no destructiva y render con FFmpeg
- qa          → comprobaciones deterministas + revisión multimodal + veredictos
- orchestrator→ ejecución extremo a extremo con regeneración selectiva y variantes
"""

__version__ = "0.1.0"
