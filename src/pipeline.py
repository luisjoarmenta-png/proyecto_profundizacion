"""Preprocesamiento y clasificador para predecir la viralidad de una canción."""

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERICAS = [
    "release_year",
    "duration_sec",
    "danceability",
    "energy",
    "valence",
    "tempo_bpm",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
    "loudness_db",
]
CATEGORICAS = ["genre"]
COLUMNAS_ENTRADA = NUMERICAS + CATEGORICAS


def crear_pipeline() -> Pipeline:
    """Construye un pipeline nuevo para ajustar con los datos de entrenamiento."""
    preprocesador = ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERICAS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAS),
        ]
    )
    return Pipeline(
        [
            ("preprocesador", preprocesador),
            ("modelo", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
