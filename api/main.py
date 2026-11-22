"""API de priorización de canciones para revisión editorial."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import joblib
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from src.pipeline import COLUMNAS_ENTRADA

RUTA_MODELO = (
    Path(__file__).resolve().parents[1] / "models/modelo_viral_logistica.joblib"
)
AtributoAudio = Annotated[float, Field(ge=0, le=1)]


class Cancion(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, strict=True)

    release_year: int
    duration_sec: Annotated[float, Field(gt=0)]
    danceability: AtributoAudio
    energy: AtributoAudio
    valence: AtributoAudio
    tempo_bpm: Annotated[float, Field(gt=0)]
    acousticness: AtributoAudio
    instrumentalness: AtributoAudio
    speechiness: AtributoAudio
    liveness: AtributoAudio
    loudness_db: float
    genre: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Prediccion(BaseModel):
    viral: Literal[0, 1]
    probabilidad_viral: Annotated[float, Field(ge=0, le=1)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    modelo = joblib.load(RUTA_MODELO)
    if list(modelo.feature_names_in_) != COLUMNAS_ENTRADA or list(modelo.classes_) != [
        0,
        1,
    ]:
        raise RuntimeError(
            "El modelo guardado es incompatible con el esquema de predicción."
        )
    app.state.modelo = modelo
    yield


app = FastAPI(title="Viralidad de canciones", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    """Confirma que el servicio ha cargado el modelo."""
    return {"status": "ok"}


@app.post("/predict", response_model=Prediccion)
def predict(cancion: Cancion, request: Request) -> Prediccion:
    """Estima la etiqueta viral y su puntuación para una pista."""
    fila = pd.DataFrame([cancion.model_dump()], columns=COLUMNAS_ENTRADA)
    modelo = request.app.state.modelo
    return Prediccion(
        viral=int(modelo.predict(fila)[0]),
        probabilidad_viral=float(modelo.predict_proba(fila)[0, 1]),
    )
