# Hallazgos del EDA

El equipo editorial quiere priorizar qué canciones escuchar antes de su lanzamiento. El análisis explora cómo se distribuye la etiqueta `viral` y qué atributos disponibles en ese momento podrían ayudar a ordenar las pistas.

El [notebook de EDA](../notebooks/EDA.ipynb) analiza las 10.000 pistas y 16 columnas del [dataset limpio](../data/processed/viral_songs_limpio.csv). Cada fila representa una pista identificada por `track_id`. Las cifras siguientes describen el catálogo completo.

## Hallazgos e implicaciones para el modelo

| # | Hallazgo | Evidencia | Implicación para el modelo |
|---|---|---|---|
| 1 | Predomina la clase no viral. | 6.395 pistas con `viral = 0` y 3.605 con `viral = 1`. | Estratificar la partición y usar exactitud balanceada. La referencia que siempre predice la clase mayoritaria logra 0,50 en esa métrica. |
| 2 | Un grupo reducido de pistas acumula muchas reproducciones. | La mediana de `streams` es 329.058, la media ronda los 2,42 millones y el máximo es 443.068.342. | Reservar esta variable para el análisis descriptivo. Su asociación con la etiqueta (r = 0,27) involucra información posterior al momento de la decisión. |
| 3 | La bailabilidad y la energía presentan asociaciones positivas con la etiqueta. | Las medianas de `danceability`, `energy` y `valence` son 0,624, 0,669 y 0,582. Sus correlaciones de Pearson con `viral` son 0,39, 0,30 y 0,20, respectivamente. | Priorizar la evaluación de estos atributos y medir cuánto aporta cada uno en validación. |
| 4 | Los diez géneros tienen tamaños comparables. | Entre 942 y 1.084 pistas por género. | Tratar `genre` como categoría sin orden y comprobar si mejora la clasificación frente a usar solo atributos numéricos. |
| 5 | Hay poca información por artista. | 1.987 artistas, con una mediana de 5 canciones y un máximo de 15. | Empezar sin la identidad del artista. Si se explora su aporte, evaluar también con artistas ausentes del entrenamiento. |
| 6 | Varios atributos de audio se concentran en la parte baja de su escala y su relación con la etiqueta varía. | Medianas de 0,235 para `acousticness`, 0,154 para `instrumentalness`, 0,080 para `speechiness` y 0,180 para `liveness`. Sus correlaciones con `viral` son −0,36, −0,07, −0,02 y 0,01. | Conservar los valores bajos válidos. Dar prioridad a `acousticness` y contrastar el aporte conjunto de los demás atributos. |
| 7 | La regla de 1,5 veces el rango intercuartílico señala extremos. | Detecta 1.399 pistas en `streams` y 84 en `duration_sec`. Entre las cinco de mayor duración hay cuatro virales y una no viral. | Revisar la plausibilidad de las observaciones. La regla sirve para inspeccionar casos y, por sí sola, no justifica recortar duraciones o eliminar pistas. |

## Hipótesis del charter

| Hipótesis o criterio del charter | Resultado en el EDA | Evidencia y comprobación pendiente |
|---|---|---|
| Una selección basada en atributos previos al lanzamiento podría identificar más pistas virales que una selección al azar del mismo tamaño. | No concluyente. | Hay asociaciones con atributos de audio, pero una correlación individual no evalúa un ranking. Fijar el cupo editorial *k* y comparar la proporción de virales entre las primeras *k* pistas con la tasa global del conjunto de prueba. En el catálogo completo, la referencia descriptiva es 36,05 %. |
| Los atributos disponibles podrían distinguir ambas clases con exactitud balanceada superior a 0,50. | No concluyente. | Las asociaciones observadas justifican evaluar un clasificador. La comprobación requiere predicciones sobre pistas reservadas para prueba y comparar con la referencia de clase mayoritaria. |

## Variables candidatas y descartadas

| Tratamiento propuesto | Variables | Motivo |
|---|---|---|
| Priorizar en la evaluación | `danceability`, `acousticness`, `energy`, `valence` | Son atributos musicales disponibles al revisar la pista y muestran las mayores correlaciones absolutas con la etiqueta entre los atributos de audio. |
| Evaluar como complemento | `release_year`, `duration_sec`, `tempo_bpm`, `instrumentalness`, `speechiness`, `liveness`, `loudness_db`, `genre` | El año y las características de la pista pueden aportar información conjunta. El género requiere una representación categórica. |
| Dejar fuera de una primera evaluación | `artist` | La escasez de ejemplos por artista dificulta estimar patrones individuales estables. |
| Excluir de las entradas | `streams`, `track_id` | Las reproducciones se acumulan tras el lanzamiento. El identificador permite localizar una pista y vincular los resultados con ella. |
| Reservar como objetivo | `viral` | Es la etiqueta binaria que se busca estimar. |

Las asociaciones describen la etiqueta disponible en este catálogo. Para interpretar la puntuación editorial conviene documentar cómo se asignó `viral` y durante qué ventana se midió.
