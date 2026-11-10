# Anuncios por etapa · <Cliente> · <AAAA-MM-DD>

> Plan para aprobar antes de crear nada. Ejemplo con Acme Automations (ficticia). Sin datos personales: solo
> recuentos, nombres de audiencia e IDs de Meta.

## 1. Requisitos

| Requisito | Estado |
|---|---|
| Topes de la ficha (`cambio_dia` / `total_dia`) | <100 / 300> |
| Condiciones de listas de clientes aceptadas (`audiencias_meta.py listar`) | sí / no |
| Etapas del §16 mapeadas, sin «sin reconocer» | sí / no (`--mapa` usado: <…>) |
| Motivo de pérdida en la exportación | sí / no |
| Seguimiento comercial activo (W3, W4, W5 de `/seguimiento-leads`) | <cuáles> |
| Base legal para usar la lista en publicidad | <dónde consta> |

## 2. Segmentos

Exportación: <oportunidades de AAAA-MM-DD a AAAA-MM-DD> + contactos. Control: <0.2>, semilla `<slug>:etapas`.

| Segmento | Total | Tratamiento | Control | Audiencia (ID) | Mensaje y prueba | CTA | Métrica (`medir`) |
|---|---|---|---|---|---|---|---|
| no-show | | | | ETAPA_NO-SHOW_GHL (<id>) | | | asistió |
| propuesta | | | | ETAPA_PROPUESTA_GHL (<id>) | | | ganado |
| perdido-timing | | | | ETAPA_PERDIDO-TIMING_GHL (<id>) | | | reabierto |

Exclusiones: `EXCL_GANADO_GHL` (<id>), `EXCL_BAJAS_GHL` (solo de exclusión, <id>), `EXCL_PROPUESTA_GHL` (lista
completa, <id>) en captación si se decide.

Segmentos descartados y por qué: <p. ej. «llamada»: citas a menos de 48 h; «perdido» por precio: exclusión>.

## 3. Estructura y presupuesto

- Campaña `ES_AWARENESS_RET_HV` · Reconocimiento (alcance) · ABO · todo en pausa.
- Presupuesto semanal por conjunto ≈ frecuencia × personas alcanzables × CPM / 1.000.

| Conjunto | Personas que Meta encontró | Frecuencia semanal buscada [HYPOTHESIS] | CPM supuesto | €/día |
|---|---|---|---|---|
| ETAPA-PROPUESTA_REACH | | 2 | | |
| ETAPA-NO-SHOW_REACH | | 2 | | |
| ETAPA-PERDIDO-TIMING_REACH | | 1 | | |
| **Total** (≤ `topes.cambio_dia`; 5–15 % del gasto [HYPOTHESIS]) | | | | |

Plan para `meta_ads.py crear` (copia a `clientes/<slug>/planes/AAAA-MM-anuncios-por-etapa.json`; los IDs con ceros son
de ejemplo y `crear` se niega hasta cambiarlos). Sin `evento` en el plan: el objetivo de alcance no optimiza a
conversiones. `frequency_control_specs` y `targeting_automation` son campos de la API de Marketing que van tal cual:
compruébalos con `--simular` y en la previsualización.

```json
{
  "campana": {"nombre": "ES_AWARENESS_RET_HV", "objetivo": "OUTCOME_AWARENESS", "categorias_especiales": []},
  "conjuntos": [
    {
      "nombre": "ETAPA-PROPUESTA_REACH",
      "presupuesto_diario": 5,
      "segmentacion": {
        "geo_locations": {"countries": ["ES"]},
        "custom_audiences": [{"id": "000000000000000"}],
        "excluded_custom_audiences": [{"id": "000000000000000"}],
        "targeting_automation": {"advantage_audience": 0}
      },
      "api": {"frequency_control_specs": [{"event": "IMPRESSIONS", "interval_days": 7, "max_frequency": 2}]},
      "anuncios": [
        {
          "nombre": "20261116_propuesta-abierta_caso-mismo-proyecto_testimonio_h1",
          "video": "creativos/20261116_propuesta-abierta/h1.mp4",
          "texto": "Texto aprobado por el cliente y revisado por revisor-politicas.",
          "titulo": "Así lo hicimos en una gestoría de 12 personas",
          "cta": "LEARN_MORE",
          "url": "https://acme-automations.example/casos/gestoria"
        }
      ]
    }
  ]
}
```

## 4. Montaje (lo ejecuta `operador-meta` tras el sí)

1. `audiencias_meta.py etapas … [--bajas]` → `privado/audiencias/<fecha>/`.
2. `crear` por audiencia → IDs en la tabla de arriba.
3. `sincronizar <id> --archivo … --reemplazar --confirmo` (con `--exclusion` las `-completa` y `bajas.csv`).
4. `listar` a las 24–48 h.
5. Creatividades: `/brief-creativo`, `/casos-y-creadores`, `/revisar-anuncio`.
6. `meta_ads.py crear <plan> --simular` → `/lanzar-campana` → todo en pausa.
7. Filas en el change log.

## 5. Refresco y medición

- Refresco: cada <día de la semana>, misma semilla y fracción, `--reemplazar`.
- Medición: `audiencias_meta.py medir` el <AAAA-MM-DD> (4–8 semanas o el ciclo de venta).
- Regla de parada: <p. ej. «no distinguible» con el tamaño pedido, o coste por éxito de más por encima de lo que vale
  la etapa en la ficha>.
