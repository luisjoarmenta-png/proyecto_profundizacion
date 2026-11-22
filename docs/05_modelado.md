# Modelado (módulo 06)

## Tipo de problema y métrica principal (y por qué)

Es un problema de clasificación binaria supervisada. El modelo predice `viral`: 0 = no viral y 1 = viral. El objetivo operativo es ordenar canciones para priorizar cuáles pasarían a revisión editorial.

La métrica principal es balanced accuracy, porque promedia el recall de las dos clases y evita que el resultado dependa solo de la clase mayoritaria. El Project Charter propone que sea superior a 0,50. También se mide la proporción de canciones virales entre las primeras 100 recomendaciones, comparándola con la tasa global de viralidad.

Se usaron 11 variables numéricas de año y audio, junto con `genre`. Se excluyeron `streams` por posible fuga de información y `track_id` por ser un identificador. `track_name` ya se había quitado durante la limpieza.

## Comparación (línea base vs. modelos)

Se comparó un DummyClassifier de clase mayoritaria con regresión logística balanceada. Se utilizó validación cruzada estratificada de cinco pliegues en el conjunto de entrenamiento.

| Modelo | Balanced accuracy | Precisión | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Dummy, clase mayoritaria | 0,500 ± 0,000 | 0,000 ± 0,000 | 0,000 ± 0,000 | 0,000 ± 0,000 | 0,500 ± 0,000 |
| Regresión logística | 0,725 ± 0,007 | 0,568 ± 0,002 | 0,786 ± 0,023 | 0,659 ± 0,008 | 0,792 ± 0,010 |

El Dummy predice siempre la clase más frecuente, por eso no identifica canciones virales. La regresión logística supera esa referencia.

## Modelo elegido y justificado

Se eligió la regresión logística con `class_weight="balanced"`. En validación cruzada obtuvo balanced accuracy de 0,725, frente a 0,500 del Dummy, y ROC-AUC de 0,792, frente a 0,500. El preprocesamiento escala las variables numéricas y codifica `genre` con one-hot encoding.

## Métrica en prueba (una sola vez)

Se dividieron los datos en entrenamiento y prueba con proporción 80/20, estratificación y semilla 42. La prueba contiene 2.000 canciones: 1.279 no virales y 721 virales.

En la prueba, la regresión logística obtuvo balanced accuracy de 0,731, ROC-AUC de 0,808 y accuracy de 0,72. Para la clase viral obtuvo precisión de 0,58, recall de 0,78 y F1 de 0,67. Para la clase no viral obtuvo precisión de 0,85, recall de 0,68 y F1 de 0,76.

Con las probabilidades del modelo, se ordenaron las canciones de prueba. Entre las primeras 100, 79 eran virales (79 %). La tasa global fue 36 %, equivalente a unas 36 canciones virales por cada 100 seleccionadas al azar. La lista priorizada encontró 43 más por cada 100 revisadas.

## Análisis de errores y límites

El modelo detectó aproximadamente el 78 % de las canciones virales de prueba, aunque su precisión de 0,58 indica que también marca como virales algunas canciones que no tienen esa etiqueta. Entre las primeras 100 recomendaciones, 21 no eran virales.

Estos resultados corresponden a esta partición de los datos y no garantizan el mismo desempeño con canciones nuevas. El KPI de las primeras 100 solo representa la capacidad del equipo si 100 es realmente su cupo de revisión. El modelo predice la etiqueta disponible; no demuestra qué causa la viralidad.
