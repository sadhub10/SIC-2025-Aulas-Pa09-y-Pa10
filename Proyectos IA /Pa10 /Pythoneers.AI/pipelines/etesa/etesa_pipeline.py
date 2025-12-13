# etesa_pipeline.py

import os
from pipelines.etesa.etesa_stations import ETESA_STATIONS, YEARS_AVAILABLE, MONTHS_AVAILABLE
from pipelines.etesa.download_csv import download_etesa_csv
from pipelines.etesa.parse_csv import parse_etesa_csv


def run_etesa():
    print("\n===== INICIANDO PIPELINE ETESA (CSV DIRECTO) =====")

    raw_path = "data_raw/etesa"
    clean_path = "data_clean/etesa"
    os.makedirs(clean_path, exist_ok=True)

    for station_id, station_name in ETESA_STATIONS.items():

        print(f"\n--- Estación: {station_id} {station_name} ---")

        for year in YEARS_AVAILABLE:
            for month in MONTHS_AVAILABLE:

                # Descargar CSV (o saltar inteligentemente)
                csv_file = download_etesa_csv(station_id, year, month, raw_path=raw_path)

                if not csv_file:
                    continue

                # Parsear limpio
                df = parse_etesa_csv(csv_file)
                if df is None:
                    continue

                df["station_id"] = station_id
                df["station_name"] = station_name
                df["year"] = year
                df["month"] = month
                df["day"] = df.get("day", None)

                output = f"{clean_path}/etesa_{station_id}_{year}_{month}.parquet"
                df.to_parquet(output, index=False)

                print(f"[OK] Guardado limpio: {output}")

    print("\n===== PIPELINE ETESA COMPLETADO =====\n")