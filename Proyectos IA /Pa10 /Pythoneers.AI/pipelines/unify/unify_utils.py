# unify_utils.py

import pandas as pd

def standardize_columns(df, source):
    """
    Normaliza columnas para el dataset maestro.
    """

    # Asegurar timestamp en datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    elif "fecha" in df.columns:
        df["timestamp"] = pd.to_datetime(df["fecha"], errors="coerce")

    # Nombre estándar
    if "station" in df.columns:
        df.rename(columns={"station": "station_name"}, inplace=True)

    if "station_id" not in df.columns:
        df["station_id"] = None

    if "sensor" not in df.columns:
        df["sensor"] = None

    if "value" not in df.columns:
        # ETESA usa columnas como temperatura_promedio, lluvia, etc.
        # Aquí mapeamos dinámicamente:
        value_cols = [c for c in df.columns if c not in 
                      ["timestamp", "station_name", "station_id", "year", "month", "day"]]

        if len(value_cols) == 1:
            df["value"] = df[value_cols[0]]
        else:
            df["value"] = None

    df["source"] = source

    # Extraer partes de fecha
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["day"] = df["timestamp"].dt.day

    return df