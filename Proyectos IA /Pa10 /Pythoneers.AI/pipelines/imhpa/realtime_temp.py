import requests
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from pipelines.imhpa.parse_imhpa import parse_imhpa_json, enrich_metadata, clean_values

load_dotenv()

RAW_PATH = os.getenv("DATA_RAW_PATH", "data_raw")

URL_TEMP = "https://www.imhpa.gob.pa/es/estaciones-satelitales-data2?sensor=TEMP_PROM"


def fetch_realtime_temperature():
    """Descarga datos de temperatura IMHPA en tiempo real (JSON)."""
    try:
        response = requests.get(URL_TEMP, timeout=15)

        if response.status_code != 200:
            print("Error descargando datos IMHPA:", response.status_code)
            return None

        data = response.json()
        return data

    except Exception as e:
        print("Error en la solicitud:", str(e))
        return None


def save_raw_data(data):
    """Guarda los datos crudos en /data_raw/imhpa/ con timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = f"{RAW_PATH}/imhpa"
    os.makedirs(folder, exist_ok=True)

    filename = f"{folder}/temp_realtime_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Datos guardados en {filename}")





def run():
    print("Descargando datos de temperatura en tiempo real...")

    data = fetch_realtime_temperature()
    if not data:
        print("No se pudieron obtener datos.")
        return

    # Guardar crudo
    save_raw_data(data)

    # Normalizar usando el parser común
    try:
        df = parse_imhpa_json(data, sensor_name="TEMP")
        df = enrich_metadata(df)
        df = clean_values(df)
    except Exception as e:
        print("Error parsing IMHPA payload:", e)
        return

    os.makedirs("data_clean/imhpa", exist_ok=True)
    out_path_csv = "data_clean/imhpa/temp_realtime_clean.csv"
    out_path_parquet = "data_clean/imhpa/temp_realtime_clean.parquet"

    df.to_csv(out_path_csv, index=False)
    try:
        df.to_parquet(out_path_parquet, index=False, engine="pyarrow")
    except Exception as e:
        print("Advertencia: no se pudo escribir Parquet:", e)

    print(f"[OK] Archivo limpio generado: {out_path_csv} (CSV)")
    print(f"[OK] Archivo Parquet generado: {out_path_parquet}")


if __name__ == "__main__":
    run()