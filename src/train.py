from pathlib import Path
import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    make_scorer,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "processed" / "viral_songs_limpio.csv")

numericas = [
    "release_year", "duration_sec", "danceability", "energy", "valence",
    "tempo_bpm", "acousticness", "instrumentalness", "speechiness",
    "liveness", "loudness_db",
]
categoricas = ["genre"]

X = df[numericas + categoricas]
y = df["viral"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

preprocesador = ColumnTransformer([
    ("num", StandardScaler(), numericas),
    ("cat", OneHotEncoder(handle_unknown="ignore"), categoricas),
])

modelos = {
    "Dummy": DummyClassifier(strategy="most_frequent"),
    "Regresión logística": Pipeline([
        ("preprocesador", preprocesador),
        ("modelo", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ]),
}

metricas_cv = {
    "balanced_accuracy": "balanced_accuracy",
    "precision": make_scorer(precision_score, zero_division=0),
    "recall": "recall",
    "f1": make_scorer(f1_score, zero_division=0),
    "roc_auc": "roc_auc",
}
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
resumen_cv = {}

for nombre, modelo in modelos.items():
    scores = cross_validate(
        modelo, X_train, y_train, cv=cv, scoring=metricas_cv
    )
    resumen_cv[nombre] = {}
    print(f"\n{nombre} — validación cruzada")
    for metrica in metricas_cv:
        valores = scores[f"test_{metrica}"]
        media, desv = float(valores.mean()), float(valores.std())
        resumen_cv[nombre][metrica] = {"media": media, "desv": desv}
        print(f"{metrica}: {media:.3f} ± {desv:.3f}")

def evaluar(y_real, y_pred, probabilidades):
    return {
        "balanced_accuracy": float(balanced_accuracy_score(y_real, y_pred)),
        "precision": float(precision_score(y_real, y_pred, zero_division=0)),
        "recall": float(recall_score(y_real, y_pred, zero_division=0)),
        "f1": float(f1_score(y_real, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_real, y_pred)),
        "roc_auc": float(roc_auc_score(y_real, probabilidades)),
    }

# Comparación final en prueba
dummy = modelos["Dummy"].fit(X_train, y_train)
pred_dummy = dummy.predict(X_test)
prob_dummy = dummy.predict_proba(X_test)[:, 1]
metricas_dummy = evaluar(y_test, pred_dummy, prob_dummy)

modelo_final = modelos["Regresión logística"].fit(X_train, y_train)
pred = modelo_final.predict(X_test)
prob = modelo_final.predict_proba(X_test)[:, 1]
metricas_logistica = evaluar(y_test, pred, prob)

print("\nPrueba — Dummy:", metricas_dummy)
print("Prueba — Regresión logística:", metricas_logistica)

# KPI de negocio para las primeras 100 recomendaciones
k = 100
ranking = pd.DataFrame({
    "viral_real": y_test.to_numpy(),
    "probabilidad": prob,
})
top_k = ranking.nlargest(k, "probabilidad")
kpi = {
    "k": k,
    "virales_recomendadas": int(top_k["viral_real"].sum()),
    "proporcion_viral_top_k": float(top_k["viral_real"].mean()),
    "tasa_global_prueba": float(y_test.mean()),
}

print(f"\nKPI top-{k}:", kpi)


carpeta_modelos = ROOT / "models"
carpeta_modelos.mkdir(parents=True, exist_ok=True)
joblib.dump(modelo_final, carpeta_modelos / "modelo_viral_logistica.joblib")

salida = {
    "validacion_cruzada": resumen_cv,
    "prueba_dummy": metricas_dummy,
    "prueba_logistica": metricas_logistica,
    "kpi_top_k": kpi,
}
(carpeta_modelos / "metricas_train.json").write_text(
    json.dumps(salida, indent=2, ensure_ascii=False),
    encoding="utf-8",
)