import pandas as pd


def eliminar_columna(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve un nuevo DataFrame con todas las columnas salvo track_name."""
    return df.drop(columns=["track_name"])