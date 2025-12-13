import os
import pandas as pd

from pipelines.geo.rivers import distance_to_river, load_rivers
from pipelines.unify.unify_utils import standardize_columns
from processing.clean_climate_data import clean_climate
from processing.outlier_detection import detect_outliers
from pipelines.geo.elevation import enrich_with_elevation
from pipelines.geo.terrain_features import enrich_with_terrain
from pipelines.risk.risk_analysis import compute_flood_risk, compute_landslide_risk
from pipelines.geo.terrain_categories import classify_terrain


def merge_processed_dataset():
    print("\n===== INICIANDO PROCESAMIENTO FINAL =====")

    master_path = "data_clean/master/master_dataset.parquet"

    if not os.path.exists(master_path):
        print("[ERROR] No existe master_dataset.parquet")
        return

    df = pd.read_parquet(master_path)

    print(f"[OK] Cargado dataset maestro: {df.shape[0]} registros")

    #Limpieza
    df = clean_climate(df)

    df = detect_outliers(df, method="zscore", threshold=3)


    print("🔼 Enriqueciendo con elevación (OpenElevation)...")
    df = enrich_with_elevation(df)

    print("⛰️ Agregando terrain features...")
    df = enrich_with_terrain(df)

    rivers_gdf = load_rivers("Panama")
    df["distance_to_river_m"] = df.apply(lambda r: distance_to_river(r["lat"], r["lon"], rivers_gdf), axis=1)


    print("🌧️🔥 Calculando riesgos climáticos...")
    df["terrain_class"] = df["slope_deg"].apply(classify_terrain)
    df["flood_risk"] = df.apply(compute_flood_risk, axis=1)
    df["landslide_risk"] = df.apply(compute_landslide_risk, axis=1)

    output_path = "data_clean/master/master_dataset_final.parquet"
    df.to_parquet(output_path, index=False)

    # Además exportar CSV final para análisis rápido
    output_csv = "data_clean/master/master_dataset_final.csv"
    try:
        df.to_csv(output_csv, index=False)
    except Exception as e:
        print("Advertencia: no se pudo escribir CSV final:", e)

    print(f"[OK] Dataset final guardado: {output_path}")
    print(f"[OK] Dataset final CSV (si se pudo generar): {output_csv}")
    print("===== PROCESAMIENTO COMPLETADO =====\n")