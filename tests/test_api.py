"""Pruebas del contrato HTTP y de la predicción con el modelo guardado."""

import joblib
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from api.main import RUTA_MODELO, app

CANCION = {
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
    "genre": "Pop",
}


@pytest.fixture(scope="module")
def cliente():
    with TestClient(app) as client:
        yield client


def test_health(cliente):
    respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


@pytest.mark.parametrize("genero", ["Pop", "Genero nuevo"])
def test_predict_reproduce_modelo(cliente, genero):
    cancion = {**CANCION, "genre": genero}
    respuesta = cliente.post("/predict", json=cancion)
    assert respuesta.status_code == 200
    modelo = joblib.load(RUTA_MODELO)
    fila = pd.DataFrame([cancion])
    resultado = respuesta.json()
    assert resultado["viral"] == modelo.predict(fila)[0]
    assert resultado["probabilidad_viral"] == pytest.approx(
        modelo.predict_proba(fila)[0, 1]
    )


@pytest.mark.parametrize(
    "cambios", [{"energy": 1.2}, {"duration_sec": 0}, {"genre": " "}, {"streams": 500}]
)
def test_rechaza_datos_invalidos(cliente, cambios):
    assert cliente.post("/predict", json={**CANCION, **cambios}).status_code == 422


def test_requiere_tempo(cliente):
    datos = CANCION.copy()
    del datos["tempo_bpm"]
    assert cliente.post("/predict", json=datos).status_code == 422
