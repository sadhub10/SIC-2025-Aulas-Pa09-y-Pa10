# modulo6.py
import os
import numpy as np
import pandas as pd
from datetime import datetime
from modulo4 import GeneradorHorarios

class PlanificadorOperacional:
    def __init__(self):
        self.generador = GeneradorHorarios()

    def calcular_operacion(self, ruta_id: str, fecha: datetime):
        """
        Si hay un CSV llamado <ruta_id>.csv en la carpeta actual, lo usa.
        De lo contrario, genera los horarios con el simulador.
        """
        csv_path = f"{ruta_id}.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            # Si no trae 'buses', lo calculamos
            if "buses" not in df.columns:
                df["buses"] = np.clip(
                    np.ceil(df["demanda"] * (df["duracion"] / df["frecuencia"])),
                    1, 3
                ).astype(int)
            # Asegurar columnas necesarias
            df = df[["hora", "demanda", "frecuencia", "buses"]].copy()
            return df.sort_values("hora").reset_index(drop=True)

        # --- Ruta sin CSV: usar simulador y capar a 3 ---
        horarios = self.generador.generar_horarios_ruta(ruta_id, fecha)
        registros = []
        for h in horarios:
            demanda = h["demanda"]
            duracion = h["duracion_ruta_min"]
            frecuencia = max(1, h["frecuencia_min"])  # evitar división por cero

            ratio = duracion / frecuencia          # p.ej. 60/20 = 3
            buses = int(np.clip(np.ceil(demanda * ratio), 1, 3))  # CAPA A 3

            registros.append({
                "hora": int(h["salida"].split(":")[0]),
                "demanda": demanda,
                "frecuencia": frecuencia,
                "buses": buses
            })

        df = pd.DataFrame(registros)
        return df.groupby("hora", as_index=False).mean(numeric_only=True)

    def obtener_resumen_global(self, df: pd.DataFrame):
        return {
            "frecuencia_promedio": round(df["frecuencia"].mean(), 1),
            "flota_maxima": int(df["buses"].max()),
            "hora_pico": int(df.loc[df["demanda"].idxmax(), "hora"])
        }
