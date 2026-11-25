# Registro de decisiones de limpieza  (módulo 04)

| Columna(s) | Problema | Decisión | Justificación | Responsable |
|---|---|---|---|---|
| track_name |   Al ser datos sinteticos   genera la misma informacion que track_id | Eliminar  la columna track_name | Porque esta data se encuentra tambien en la columna track_id | Santiago Giraldo |
| Todas | Valores nulos | No imputar ni eliminar filas | El diagnóstico de `src/limpieza.py` encontró 0 nulos en las 10.000 filas | Santiago Giraldo |
| Todas | Filas duplicadas y `track_id` repetidos | No eliminar filas | El diagnóstico encontró 0 filas duplicadas y 0 `track_id` repetidos | Santiago Giraldo |

