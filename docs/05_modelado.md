# Modelado de viralidad

## Objetivo

Predecir la clase `viral` (0/1) usando variables de audio, año, género y artista. El uso previsto es estimar la etiqueta a partir de atributos de la canción, no inferir causalidad.

## Variables y preparación

- Numéricas: `release_year`, `duration_sec`, `danceability`, `energy`, `valence`, `tempo_bpm`, `acousticness`, `instrumentalness`, `speechiness`, `liveness` y `loudness_db`. Los faltantes se imputan con mediana y se escalan.
- Categóricas: `genre` y `artist`. Los faltantes se imputan con la categoría más frecuente y se aplica one-hot encoding; categorías nuevas se ignoran al predecir.
- Se excluyen `streams`, `track_id` y `track_name`. `streams` puede filtrar información de popularidad ya observada y producir una evaluación engañosa para predicción basada en atributos de la canción.
- Se hace una partición estratificada 80/20 con semilla 42.

## Modelos y evaluación

Como referencia se usa un baseline que siempre predice la clase mayoritaria. Se compara con regresión logística y Random Forest, estos dos con pesos balanceados. La selección se hace por `average_precision` media en validación cruzada estratificada de cinco pliegues sobre el conjunto de entrenamiento; el conjunto de prueba queda reservado para una evaluación final.

Se reportan ROC-AUC, average precision (resumen del desempeño precisión-recall), precisión, recall, F1, accuracy y matriz de confusión usando umbral 0.5 para el modelo elegido y el baseline. Por el desbalance observado en el EDA, accuracy no se debe interpretar sola. Average precision permite comparar el balance entre precision y recall sin fijar un umbral; recall es útil si interesa no dejar pasar canciones potencialmente virales, mientras precision refleja cuántas alertas de viralidad son correctas. El umbral 0.5 es inicial y puede ajustarse al conocer el costo de falsos positivos y falsos negativos.

## Resultado de la corrida

Con 10.000 registros (8.000 entrenamiento y 2.000 prueba), la validación cruzada seleccionó Random Forest: average precision media de 0.629 frente a 0.613 para regresión logística y 0.360 para el baseline. En la prueba, Random Forest obtuvo ROC-AUC 0.800, average precision 0.633, precisión 0.570, recall 0.798, F1 0.665 y accuracy 0.710. El baseline alcanzó average precision 0.361 y accuracy 0.640; su recall es 0 porque siempre predice no viral. El modelo identifica más canciones virales, aunque genera falsos positivos (434 en la prueba), por lo que su umbral debe leerse según el uso previsto.

## Ejecución

Con CSV local:

```powershell
uv run python src/train.py --csv data/raw/viral_songs.csv
```

Sin CSV local, el script intenta descargar el dataset público con KaggleHub, como en el notebook:

```powershell
uv run python src/train.py
```

Se generan `models/modelo_viral.joblib` y `models/metricas_modelo.json`. El archivo JSON conserva las métricas completas de la corrida.

## Limitaciones

Los nombres anonimizados/sintéticos (`Track_00001`, `Artist_1519`) limitan lo que se puede concluir sobre música real. Una partición aleatoria también puede dejar artistas repetidos entre entrenamiento y prueba. Para una validación de robustez se recomienda evaluar con particiones agrupadas por artista y explicar la definición de `viral` que utiliza la fuente.
