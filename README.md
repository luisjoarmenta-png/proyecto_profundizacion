# proyecto profundizacion

## Equipo

|integrantes | Rol principal | Github| 
| --- | --- |--- | 
 | Santiago Giraldo| Datos y limpieza | @giraldocortees98 |
 | Nicolas Hidalgo | EDA y visualización | @nicolas-hidalgo123 |
 | Maiyan Yarce| Modelado | @maiyanyarce122-crypto |
 | luis Armenta | Api | @luisarmenta-png |

## Problema de negocio
¿que hace que una canción sea viral, su ritmo, genero, duración, artista?

## como ejecutar

uv sync 
uv run jupyter lab

## API de viralidad

```powershell
uv sync
uv run uvicorn api.main:app --reload
```

Abre [la documentación interactiva](http://127.0.0.1:8000/docs). La API carga una vez el modelo entrenado en `models/modelo_viral_logistica.joblib`. Para regenerarlo con el CSV limpio, ejecuta `uv run python -m src.train` antes de iniciar el servicio.

| Método y ruta | Uso |
|---|---|
| `GET /health` | Devuelve `{"status":"ok"}` cuando el servicio está listo. |
| `POST /predict` | Recibe una pista y devuelve `viral` (0 o 1) y `probabilidad_viral` (puntuación del modelo entre 0 y 1 para priorizar la revisión). |

En `POST /predict`, selecciona **Try it out**, pega los datos de esta pista del CSV limpio y pulsa **Execute**.

```json
{
  "release_year": 2013,
  "duration_sec": 237,
  "danceability": 0.76,
  "energy": 0.703,
  "valence": 0.747,
  "tempo_bpm": 140.8,
  "acousticness": 0.115,
  "instrumentalness": 0.103,
  "speechiness": 0.206,
  "liveness": 0.272,
  "loudness_db": -9.41,
  "genre": "Pop"
}
```

Los 12 campos son obligatorios. Los atributos de audio normalizados aceptan valores de 0 a 1, la duración se expresa en segundos, el tempo en BPM y el volumen en decibelios. Las solicitudes con campos faltantes, adicionales o fuera de los rangos definidos reciben HTTP 422.

Para verificar el servicio y comparar sus predicciones con el modelo guardado, ejecuta `uv run python -m pytest -q tests/test_api.py`.