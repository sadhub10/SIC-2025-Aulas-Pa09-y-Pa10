import pandas as pd
import re
from typing import Any
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_imhpa_json(payload, sensor_name):
    """
    Parser oficial para IMHPA.
    Convierte JSON de estructura:
        {"estaciones": {id1: {...}, id2: {...}}}
    en un DataFrame limpio y estandarizado.
    """

    if "estaciones" not in payload:
        raise ValueError("JSON IMHPA no contiene la clave 'estaciones'.")

    estaciones = payload["estaciones"]

    rows = []

    def _process_station(est_id, info, sensor_name):
        # Extraer valor
        value = info.get("sensor_valor_sin_format") or None

        # Extraer fecha (formato: DD/MM/YYYY HH:MM AM/PM) con fallback
        fecha_raw = info.get("sensor_fecha")
        try:
            timestamp = pd.to_datetime(fecha_raw, format="%d/%m/%Y %I:%M %p")
        except Exception:
            timestamp = pd.to_datetime(fecha_raw, dayfirst=True, errors="coerce")

        # Nombre
        name = info.get("nombre", None)

        # Coordenadas
        try:
            lat = float(info.get("latitud", "0") or 0)
        except Exception:
            lat = 0.0
        try:
            lon = float(info.get("longitud", "0") or 0)
        except Exception:
            lon = 0.0

        return {
            "station_id": est_id,
            "station_name": name,
            "lat": lat,
            "lon": lon,
            "timestamp": timestamp,
            "value": value,
            "sensor": sensor_name,
        }

    # Ejecutar procesamiento por estación en paralelo
    max_workers = int(os.getenv("IMHPA_MAX_WORKERS", "8"))
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_process_station, est_id, info, sensor_name): est_id for est_id, info in estaciones.items()}
        for fut in as_completed(futures):
            try:
                row = fut.result()
                rows.append(row)
            except Exception as e:
                est = futures.get(fut)
                print(f"[WARN] Error procesando estación {est}: {e}")

    df = pd.DataFrame(rows)

    # Eliminar registros sin timestamp
    df = df.dropna(subset=["timestamp"])

    # Ordenar
    df = df.sort_values("timestamp")

    return df[
        [
            "timestamp",
            "station_id",
            "station_name",
            "lat",
            "lon",
            "sensor",
            "value",
        ]
    ]


def enrich_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Añade metadatos útiles al DataFrame:
      - `source`: indica que viene de IMHPA
      - `date`: fecha (sin hora)
      - `hour`: hora del registro
    Mantiene el resto de columnas intactas.
    """
    if df is None or df.empty:
        return df

    df = df.copy()
    df["source"] = "IMHPA"

    # Asegurar que timestamp es datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["date"] = df["timestamp"].dt.date
    df["hour"] = df["timestamp"].dt.time

    return df


def clean_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza la columna `value` extrayendo el número (si viene con unidades)
    y convirtiéndolo a `float`. Elimina filas sin valor numérico.
    """
    if df is None or df.empty:
        return df

    df = df.copy()

    def _extract_num(x: Any) -> Any:
        if x is None:
            return None
        # Si ya es numérico
        if isinstance(x, (int, float)):
            return x
        s = str(x)
        m = re.search(r"[+-]?\d*\.?\d+", s)
        if m:
            try:
                return float(m.group(0))
            except Exception:
                return None
        return None

    df["value"] = df["value"].apply(_extract_num)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Eliminar registros sin valor numérico
    df = df.dropna(subset=["value"]) 

    return df

def validate_json(payload):
    # Valida que el payload recibido tenga la estructura mínima esperada por IMHPA.
    # Lanza ValueError si la estructura es inválida.
    if not isinstance(payload, dict):
        raise ValueError("JSON IMHPA no contiene la clave 'estaciones'.")
    if 'estaciones' not in payload:
        raise ValueError("JSON IMHPA no contiene la clave 'estaciones'.")
    estaciones = payload['estaciones']
    if not isinstance(estaciones, dict):
        raise ValueError("Campo 'estaciones' debe ser un objeto/dict.")
    for k, v in estaciones.items():
        if not isinstance(v, dict):
            raise ValueError(f"Estación {k} no tiene la estructura esperada")
    return True
