"""Unify master dataset placeholder.

This module exposes `unify_master_dataset()` used by the pipeline runner.
"""
def unify_master_dataset():
    print("Unifying master dataset (placeholder)")
# unify_master.py

import os
import pandas as pd
from pipelines.unify.unify_utils import standardize_columns


def unify_master_dataset():
    print("\n===== INICIANDO UNIFICACIÓN DEL DATASET MAESTRO =====")

    # ----------------------------------------------------------
    # 1) Unificar IMHPA (real-time)
    # ----------------------------------------------------------

    print("\n[1] Procesando IMHPA...")

    imhpa_path = "data_clean/imhpa"
    imhpa_files = [
        f"{imhpa_path}/{f}"
        for f in os.listdir(imhpa_path)
        if f.endswith(".csv")
    ]

    imhpa_frames = []

    for file in imhpa_files:
        try:
            df = pd.read_csv(file)
            df = standardize_columns(df, source="IMHPA")
            imhpa_frames.append(df)
        except Exception as e:
            print(f"[ERROR] No se pudo procesar IMHPA archivo {file}: {e}")

    if len(imhpa_frames) > 0:
        df_imhpa = pd.concat(imhpa_frames, ignore_index=True)
    else:
        df_imhpa = pd.DataFrame()
        print("[WARN] No hay archivos IMHPA para unificar.")

    print(f"[OK] IMHPA total registros: {len(df_imhpa)}")


    # ----------------------------------------------------------
    # 2) Unificar ETESA (histórico CSV → parquet)
    # ----------------------------------------------------------

    print("\n[2] Procesando ETESA...")

    etesa_path = "data_clean/etesa"
    etesa_files = [
        f"{etesa_path}/{f}"
        for f in os.listdir(etesa_path)
        if f.endswith(".parquet")
    ]

    etesa_frames = []

    for file in etesa_files:
        try:
            df = pd.read_parquet(file)

            # Crear timestamp desde columnas año/mes/día
            if {"year", "month", "day"}.issubset(df.columns):
                df["timestamp"] = pd.to_datetime(
                    df[["year", "month", "day"]],
                    errors="coerce"
                )

            df = standardize_columns(df, source="ETESA")
            etesa_frames.append(df)

        except Exception as e:
            print(f"[ERROR] No se pudo procesar ETESA archivo {file}: {e}")

    if len(etesa_frames) > 0:
        df_etesa = pd.concat(etesa_frames, ignore_index=True)
    else:
        df_etesa = pd.DataFrame()
        print("[WARN] No hay archivos ETESA para unificar.")

    print(f"[OK] ETESA total registros: {len(df_etesa)}")


    # ----------------------------------------------------------
    # 3) Unificar todo (IMHPA + ETESA)
    # ----------------------------------------------------------

    print("\n[3] Unificando datasets...")

    df_master = pd.concat([df_imhpa, df_etesa], ignore_index=True)

    # Ordenar por timestamp
    df_master.sort_values("timestamp", inplace=True)

    # Limpieza mínima: eliminar filas sin timestamp o value
    df_master = df_master.dropna(subset=["timestamp", "value"])

    print(f"[OK] Total registros unificados: {len(df_master)}")


    # ----------------------------------------------------------
    # 4) Guardar dataset maestro final
    # ----------------------------------------------------------

    output_path = "data_clean/master"
    os.makedirs(output_path, exist_ok=True)

    output_file = f"{output_path}/master_dataset.parquet"
    df_master.to_parquet(output_file, index=False)

    # Adicional: exportar CSV para inspección rápida / compatibilidad
    output_csv = f"{output_path}/master_dataset.csv"
    try:
        df_master.to_csv(output_csv, index=False)
    except Exception as e:
        print("Advertencia: no se pudo escribir master CSV:", e)

    print(f"[OK] Dataset maestro generado: {output_file}")
    print(f"[OK] Dataset maestro CSV (si se pudo generar): {output_csv}")
    print("\n===== UNIFICACIÓN COMPLETADA =====\n")