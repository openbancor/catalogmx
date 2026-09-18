# Tasas de recargos por mora

`RecargosMoraCatalog` expone la tasa efectiva mensual de recargos por mora
para contribuciones federales. La tasa se conserva por ejercicio fiscal con
su vigencia, tasa base de la LIF, fundamento, fecha de publicación y URL de la
fuente.

```python
from catalogmx.catalogs.mexico import RecargosMoraCatalog

registro = RecargosMoraCatalog.get_por_anio(2026)
tasa = RecargosMoraCatalog.get_tasa_mensual(2026)
```

La tasa `tasa_mora_mensual` es la tasa efectiva que el SAT publica para mora:

| Ejercicio | Tasa efectiva mensual | Tasa base LIF |
| --- | ---: | ---: |
| 2024 | 1.47% | 0.98% |
| 2025 | 1.47% | 0.98% |
| 2026 | 2.07% | 1.38% |

No debe confundirse con las tasas de pagos en parcialidades o pagos diferidos.
Los consumidores deben conservar la procedencia del registro junto con cada
cálculo y no extrapolar la tasa a ejercicios que no estén en el catálogo.
