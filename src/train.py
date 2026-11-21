"""Entrena y evalua clasificadores de viralidad para el proyecto.

Uso: uv run python src/train.py [--csv data/raw/viral_songs.csv]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import kagglehub
import pandas as pd
from kagglehub import KaggleDatasetAdapter
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERICAS = [
    "release_year", "duration_sec", "danceability", "energy", "valence",
    "tempo_bpm", "acousticness", "instrumentalness", "speechiness",
    "liveness", "loudness_db",
]
CATEGORICAS = ["genre", "artist"]
OBJETIVO = "viral"


def cargar_datos(ruta_csv: str | None) -> pd.DataFrame:
    """Carga un CSV local o el dataset publico utilizado en el EDA."""
    if ruta_csv:
        return pd.read_csv(ruta_csv)
    return kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS,
        "vedauv/what-makes-a-song-go-viral-10000-tracks",
        "viral_songs.csv",
    )


def construir_pipeline(modelo) -> Pipeline:
    preprocesamiento = ColumnTransformer(
        transformers=[
            ("numericas", Pipeline([
                ("imputar", SimpleImputer(strategy="median")),
                ("escalar", StandardScaler()),
            ]), NUMERICAS),
            ("categoricas", Pipeline([
                ("imputar", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]), CATEGORICAS),
        ],
        remainder="drop",
    )
    return Pipeline([("preprocesamiento", preprocesamiento), ("modelo", modelo)])


def entrenar(df: pd.DataFrame, directorio_salida: Path) -> dict:
    requeridas = NUMERICAS + CATEGORICAS + [OBJETIVO]
    faltantes = sorted(set(requeridas) - set(df.columns))
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {faltantes}")
    datos = df[requeridas].dropna(subset=[OBJETIVO])
    X = datos[NUMERICAS + CATEGORICAS]
    y = datos[OBJETIVO].astype(int)
    if y.nunique() != 2:
        raise ValueError("La variable viral debe tener exactamente dos clases.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    candidatos = {
        "baseline_clase_mayoritaria": DummyClassifier(strategy="most_frequent"),
        "regresion_logistica": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=42
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, class_weight="balanced",
            n_jobs=-1, random_state=42,
        ),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    resultados_cv = {}
    for nombre, estimador in candidatos.items():
        puntajes = cross_val_score(
            construir_pipeline(estimador), X_train, y_train,
            cv=cv, scoring="average_precision", n_jobs=1,
        )
        resultados_cv[nombre] = {
            "average_precision_media": float(puntajes.mean()),
            "average_precision_desv": float(puntajes.std()),
        }

    seleccionado = max(
        resultados_cv, key=lambda nombre: resultados_cv[nombre]["average_precision_media"]
    )
    modelo = construir_pipeline(candidatos[seleccionado]).fit(X_train, y_train)
    probabilidades = modelo.predict_proba(X_test)[:, 1]
    predicciones = (probabilidades >= 0.5).astype(int)
    metricas = {
        "roc_auc": float(roc_auc_score(y_test, probabilidades)),
        "average_precision": float(average_precision_score(y_test, probabilidades)),
        "precision": float(precision_score(y_test, predicciones, zero_division=0)),
        "recall": float(recall_score(y_test, predicciones, zero_division=0)),
        "f1": float(f1_score(y_test, predicciones, zero_division=0)),
        "accuracy": float(accuracy_score(y_test, predicciones)),
        "matriz_confusion": confusion_matrix(y_test, predicciones).tolist(),
    }
    baseline = construir_pipeline(candidatos["baseline_clase_mayoritaria"]).fit(
        X_train, y_train
    )
    prob_baseline = baseline.predict_proba(X_test)[:, 1]
    pred_baseline = baseline.predict(X_test)
    metricas_baseline = {
        "roc_auc": float(roc_auc_score(y_test, prob_baseline)),
        "average_precision": float(average_precision_score(y_test, prob_baseline)),
        "precision": float(precision_score(y_test, pred_baseline, zero_division=0)),
        "recall": float(recall_score(y_test, pred_baseline, zero_division=0)),
        "f1": float(f1_score(y_test, pred_baseline, zero_division=0)),
        "accuracy": float(accuracy_score(y_test, pred_baseline)),
        "matriz_confusion": confusion_matrix(y_test, pred_baseline).tolist(),
    }
    directorio_salida.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelo, directorio_salida / "modelo_viral.joblib")
    reporte = {
        "objetivo": OBJETIVO,
        "variables": NUMERICAS + CATEGORICAS,
        "variables_excluidas": {
            "streams": "posible fuga: popularidad ya observada",
            "track_id": "identificador sin valor predictivo generalizable",
            "track_name": "nombre de pista no usado como atributo",
        },
        "semilla": 42,
        "tamano_total": int(len(datos)),
        "tamano_entrenamiento": int(len(X_train)),
        "tamano_prueba": int(len(X_test)),
        "proporcion_viral": float(y.mean()),
        "validacion_cruzada_entrenamiento": resultados_cv,
        "modelo_seleccionado": seleccionado,
        "metricas_baseline_prueba": metricas_baseline,
        "metricas_prueba_umbral_0_5": metricas,
    }
    (directorio_salida / "metricas_modelo.json").write_text(
        json.dumps(reporte, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return reporte


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", help="CSV local; si se omite, descarga con KaggleHub.")
    parser.add_argument("--salida", default="models", help="Carpeta para modelo y metricas.")
    args = parser.parse_args()
    reporte = entrenar(cargar_datos(args.csv), Path(args.salida))
    print(json.dumps(reporte, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
