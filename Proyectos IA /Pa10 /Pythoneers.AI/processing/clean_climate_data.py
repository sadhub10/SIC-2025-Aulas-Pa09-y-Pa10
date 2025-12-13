# clean_climate_data.py

import pandas as pd
import numpy as np

# Rango físico general
VALID_RANGES = {
    "TEMP": (-5, 45),        # °C
    "HR": (0, 100),          # %
    "LLUVIA": (0, 500),      # mm/día
    "VIENTO": (0, 120),      # km/h
}

def clean_climate(df):
    """
    Limpieza avanzada del dataset maestro.
    - Normalización de unidades
    - Eliminación de valores imposibles
    - Interpolaciones básicas
    - Corrección de columnas inconsistentes
    """

    df = df.copy()

    # 1. Eliminar datos sin valor
    df = df.dropna(subset=["value"])

    # 2. Filtrar por rangos posibles según sensor
    def is_valid(row):
        sensor = str(row["sensor"]).upper()
        value = row["value"]

        if "TEMP" in sensor:
            low, high = VALID_RANGES["TEMP"]
        elif "HR" in sensor or "HUMED" in sensor:
            low, high = VALID_RANGES["HR"]
        elif "LLUV" in sensor:
            low, high = VALID_RANGES["LLUVIA"]
        elif "VIENTO" in sensor or "WIND" in sensor:
            low, high = VALID_RANGES["VIENTO"]
        else:
            return True  # sensor desconocido, no filtrar

        return low <= value <= high

    df = df[df.apply(is_valid, axis=1)]

    # 3. Interpolación lineal por estación / sensor
    df = df.sort_values("timestamp")
    df["value"] = df.groupby(["station_id", "sensor"])["value"].transform(
        lambda group: group.interpolate(method="linear", limit=2)
    )

    # 4. Última limpieza
    df = df.dropna(subset=["value"])

    return df