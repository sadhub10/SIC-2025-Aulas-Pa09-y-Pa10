# download_csv.py

import requests
import os
from datetime import datetime

BASE_URL = "https://www.imhpa.gob.pa/es/datos-diarios"


def should_download(station_id, year, month, raw_path):
    """Decide si descargar o no: evita duplicaciones salvo meses recientes."""

    filename = f"{raw_path}/etesa_{station_id}_{year}_{month}.csv"

    # Si el archivo NO existe → se descarga
    if not os.path.exists(filename):
        return True

    # Si existe → solo descargar nuevamente si es mes actual o anterior
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # Caso: año y mes actual
    if year == current_year and month == current_month:
        return True

    # Caso: mes anterior (actual-1)
    previous_month = current_month - 1 or 12
    previous_year = current_year if current_month > 1 else current_year - 1

    if year == previous_year and month == previous_month:
        return True

    # En cualquier otro caso, NO descargar
    return False



def download_etesa_csv(station_id, year, month, raw_path="data_raw/etesa"):
    """Descarga el CSV directo de ETESA para estación / año / mes."""

    os.makedirs(raw_path, exist_ok=True)

    filename = f"{raw_path}/etesa_{station_id}_{year}_{month}.csv"

    # --- lógica inteligente ---
    if not should_download(station_id, year, month, raw_path):
        print(f"[SKIP] Ya existe: {filename}")
        return filename

    params = {
        "estacion": station_id,
        "mes": month,
        "ano": year,
        "csv": 1
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=20)
        response.raise_for_status()

        with open(filename, "wb") as f:
            f.write(response.content)

        print(f"[OK] CSV descargado: {filename}")
        return filename

    except Exception as e:
        print(f"[ERROR] No se pudo descargar CSV ETESA: {station_id} {year}-{month}")
        print("Detalles:", e)
        return None