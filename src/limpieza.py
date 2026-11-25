"""Limpieza de datos: del CSV crudo al CSV limpio listo para modelar.

Uso (desde la raíz del proyecto):
    uv run python -m src.limpieza
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUTA_CRUDO = ROOT / "data" / "raw" / "viral_songs.csv"
RUTA_LIMPIO = ROOT / "data" / "processed" / "viral_songs_limpio.csv"

KAGGLE_DATASET = "vedauv/what-makes-a-song-go-viral-10000-tracks"
ARCHIVO_KAGGLE = "viral_songs.csv"


def cargar_crudo() -> pd.DataFrame:
    """Lee el CSV crudo; si no existe, lo descarga de Kaggle y lo guarda."""
    if RUTA_CRUDO.exists():
        return pd.read_csv(RUTA_CRUDO)

    # Se importa aquí para que importar este módulo no exija red ni kagglehub.
    import kagglehub
    from kagglehub import KaggleDatasetAdapter

    df = kagglehub.dataset_load(
        KaggleDatasetAdapter.PANDAS, KAGGLE_DATASET, ARCHIVO_KAGGLE
    )
    RUTA_CRUDO.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RUTA_CRUDO, index=False)
    return df


def eliminar_columna(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un nuevo DataFrame con todas las columnas salvo track_name."""
    return df.drop(columns=["track_name"])


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica las decisiones de limpieza de docs/03_decisiones_limpieza.md."""
    return eliminar_columna(df)


def diagnostico(df: pd.DataFrame) -> None:
    """Imprime nulos y duplicados para decidir si hace falta limpiar más."""
    print(f"Filas: {len(df)}, columnas: {df.shape[1]}")
    print(f"Valores nulos en total: {int(df.isna().sum().sum())}")
    print(f"Filas duplicadas: {int(df.duplicated().sum())}")
    if "track_id" in df.columns:
        print(f"track_id repetidos: {int(df['track_id'].duplicated().sum())}")


def main() -> None:
    """Genera data/processed/viral_songs_limpio.csv a partir de los datos crudos."""
    crudo = cargar_crudo()
    print("— Datos crudos")
    diagnostico(crudo)

    limpio = limpiar(crudo)
    RUTA_LIMPIO.parent.mkdir(parents=True, exist_ok=True)
    limpio.to_csv(RUTA_LIMPIO, index=False)

    print("\n— Datos limpios")
    diagnostico(limpio)
    print(f"\nGuardado en {RUTA_LIMPIO.relative_to(ROOT)}")


if __name__ == "__main__":
    main()