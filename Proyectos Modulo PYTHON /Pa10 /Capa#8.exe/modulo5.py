"""Módulo 5 – Visualización y Reportes mejorado"""

# ======================================================
# MÓDULO 5: VISUALIZACIÓN Y REPORTES
# ======================================================
# Este módulo toma los horarios generados por el módulo 4
# y produce:
#   - Tablas de horarios y estadísticas
#   - Gráficos con pandas + matplotlib
#   - Exportación de resultados a CSV
#
# Entrada: Lista de horarios (del módulo 4)
# Salida: Archivos .csv y gráficos .png
# ======================================================pythoi

import pandas as pd
import numpy as np
from datetime import datetime

# Control de importaciones opcionales
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None
    print("⚠️ Matplotlib no está disponible. Los gráficos no se generarán.")

from modulo4 import GeneradorHorarios
from modulo1 import RUTAS, FLOTA_AUTOBUSES


class ReporteTransporte:
    def __init__(self, fecha=None):
        self.fecha = fecha or datetime.now()
        self.generador = GeneradorHorarios()
        self.df_horarios = None
        self.df_estadisticas = None

    # --------------------------------------------------
    # Generar el dataset principal de horarios
    # --------------------------------------------------
    def generar_dataset(self):
        print("\n📅 Generando horarios para todas las rutas...")
        horarios = self.generador.generar_todos_los_horarios(self.fecha)
        self.df_horarios = pd.DataFrame(horarios)
        print(f"✅ {len(self.df_horarios)} registros generados.")
        return self.df_horarios

    # --------------------------------------------------
    # Crear estadísticas generales
    # --------------------------------------------------
    def calcular_estadisticas(self):
        if self.df_horarios is None:
            raise ValueError("Primero debes generar los horarios.")
        print("📈 Calculando estadísticas...")

        self.df_horarios["hora_salida_num"] = self.df_horarios["salida"].apply(lambda x: int(x.split(":")[0]))
        self.df_estadisticas = (
            self.df_horarios.groupby("hora_salida_num")
            .agg({"ruta": "count", "demanda": "mean"})
            .rename(columns={"ruta": "salidas", "demanda": "demanda_prom"})
            .reset_index()
        )
        print("✅ Estadísticas calculadas.")
        return self.df_estadisticas

    # --------------------------------------------------
    # Graficar: salidas por hora
    # --------------------------------------------------
    def graficar_salidas_por_hora(self):
        if plt is None:
            print("⚠️ Matplotlib no está disponible. Saltando gráfico 1.")
            return
        if self.df_estadisticas is None:
            raise ValueError("Primero debes calcular las estadísticas.")

        try:
            plt.figure(figsize=(10, 5))
            plt.bar(self.df_estadisticas["hora_salida_num"], self.df_estadisticas["salidas"], color="#1f77b4")
            plt.title("Salidas de Autobuses por Hora", fontsize=14, fontweight="bold")
            plt.xlabel("Hora del día")
            plt.ylabel("Cantidad de salidas")
            plt.grid(axis='y', linestyle='--', alpha=0.6)
            plt.tight_layout()
            plt.savefig("salidas_por_hora.png")
            print("🖼️  Gráfico generado: salidas_por_hora.png")
            plt.close()
        except Exception as e:
            print(f"⚠️ Error al generar gráfico 1: {e}")

    # --------------------------------------------------
    # Graficar: demanda promedio
    # --------------------------------------------------
    def graficar_demanda_promedio(self):
        if plt is None:
            print("⚠️ Matplotlib no está disponible. Saltando gráfico 2.")
            return
        if self.df_estadisticas is None:
            raise ValueError("Primero debes calcular las estadísticas.")

        try:
            plt.figure(figsize=(10, 5))
            plt.plot(
                self.df_estadisticas["hora_salida_num"],
                self.df_estadisticas["demanda_prom"],
                marker="o",
                color="#ff7f0e"
            )
            plt.title("Demanda Promedio por Hora", fontsize=14, fontweight="bold")
            plt.xlabel("Hora del día")
            plt.ylabel("Demanda promedio (0.0 - 1.0)")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig("demanda_promedio.png")
            print("🖼️  Gráfico generado: demanda_promedio.png")
            plt.close()
        except Exception as e:
            print(f"⚠️ Error al generar gráfico 2: {e}")

    # --------------------------------------------------
    # Exportar a CSV
    # --------------------------------------------------
    def exportar_csv(self):
        if self.df_horarios is None:
            raise ValueError("No hay horarios generados para exportar.")

        try:
            self.df_horarios.to_csv("horarios_generados.csv", index=False)
            self.df_estadisticas.to_csv("estadisticas_generales.csv", index=False)
            print("💾 Archivos exportados:")
            print("   - horarios_generados.csv")
            print("   - estadisticas_generales.csv")
        except Exception as e:
            print(f"⚠️ Error al exportar CSV: {e}")

    # --------------------------------------------------
    # Ejecutar todo el flujo completo
    # --------------------------------------------------
    def generar_reportes_completos(self):
        print("\n=== 🚌 SISTEMA DE REPORTES DE TRANSPORTE ===")
        try:
            self.generar_dataset()
            self.calcular_estadisticas()
            self.graficar_salidas_por_hora()
            self.graficar_demanda_promedio()
            self.exportar_csv()
            print("\n✅ Reportes y gráficos generados exitosamente.\n")
        except Exception as e:
            print(f"❌ Error en el proceso general: {e}")


# ======================================================
# Ejemplo de ejecución directa
# ======================================================
if __name__ == "__main__":
    reporte = ReporteTransporte()
    reporte.generar_reportes_completos()
