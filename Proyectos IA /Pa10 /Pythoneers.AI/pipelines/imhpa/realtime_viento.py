import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

RAW_PATH = os.getenv("DATA_RAW_PATH", "data_raw")

URL_VIENTO = "https://www.imhpa.gob.pa/es/estaciones-satelitales-data2?sensor=VEL_VIENTO"


def fetch_realtime_wind():
    try:
        response = requests.get(URL_VIENTO, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Error obteniendo viento:", e)
        return None


def save_raw_data(data):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"{RAW_PATH}/imhpa"
    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/viento_realtime_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Datos crudos guardados: {filename}")


from pipelines.imhpa.parse_imhpa import parse_imhpa_json, enrich_metadata, clean_values


def convert_to_dataframe(data):
    df = parse_imhpa_json(data, sensor_name="VIENTO")
    df = enrich_metadata(df)
    df = clean_values(df)
    return df


def run():
    print("Descargando viento en tiempo real...")

    data = fetch_realtime_wind()
    if not data:
        return

    save_raw_data(data)

    df = convert_to_dataframe(data)
    os.makedirs("data_clean/imhpa", exist_ok=True)
    out_csv = "data_clean/imhpa/viento_realtime_clean.csv"
    out_parquet = "data_clean/imhpa/viento_realtime_clean.parquet"
    df.to_csv(out_csv, index=False)
    try:
        df.to_parquet(out_parquet, index=False, engine="pyarrow")
    except Exception as e:
        print("Advertencia: no se pudo escribir Parquet:", e)

    print(f"[OK] Archivo limpio generado: {out_csv} (CSV)")
    print(f"[OK] Archivo Parquet generado: {out_parquet}")


if __name__ == "__main__":
    run()