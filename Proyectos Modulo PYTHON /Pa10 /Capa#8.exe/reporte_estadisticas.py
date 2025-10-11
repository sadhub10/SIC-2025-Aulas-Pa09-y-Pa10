# ======================================================
# REPORTE ESTADÍSTICO DEL SISTEMA DE TRANSPORTE
# ======================================================
# Este módulo utiliza pandas para analizar los horarios
# generados en el sistema, extrayendo métricas clave
# para evaluar eficiencia, demanda y frecuencia de operación.
# ======================================================

import pandas as pd
import numpy as np
# ------------------------------------------------------
# 1. Cargar los datos generados
# ------------------------------------------------------
try:
    df = pd.read_csv("horarios_generados.csv")
    print("✅ Archivo 'horarios_generados.csv' cargado correctamente.")
except FileNotFoundError:
    print("❌ No se encontró 'horarios_generados.csv'. Ejecuta primero modulo5.py.")
    exit()

# ------------------------------------------------------
# 2. Estadísticas generales del sistema
# ------------------------------------------------------
print("\n=== 📊 ESTADÍSTICAS GENERALES DEL SISTEMA ===")

total_rutas = df["ruta"].nunique()
total_salidas = len(df)
promedio_demanda = df["demanda"].mean()
promedio_frecuencia = df["frecuencia_min"].mean()
promedio_duracion = df["duracion_ruta_min"].mean()

print(f"🚌 Total de rutas activas: {total_rutas}")
print(f"🚍 Total de salidas programadas: {total_salidas}")
print(f"📈 Demanda promedio del día: {promedio_demanda:.2f}")
print(f"⏱️ Frecuencia promedio: {promedio_frecuencia:.2f} minutos")
print(f"🕒 Duración promedio de viaje: {promedio_duracion:.2f} minutos")

# ------------------------------------------------------
# 3. Agrupación por hora de salida
# ------------------------------------------------------
df["hora_salida_num"] = df["salida"].apply(lambda x: int(x.split(":")[0]))
estadisticas_por_hora = df.groupby("hora_salida_num").agg({
    "ruta": "count",
    "demanda": ["mean", "max"],
    "frecuencia_min": "mean"
}).reset_index()

estadisticas_por_hora.columns = [
    "Hora",
    "Salidas",
    "Demanda_Prom",
    "Demanda_Max",
    "Frecuencia_Prom"
]

# Detectar hora pico (mayor cantidad de salidas)
hora_pico = estadisticas_por_hora.loc[estadisticas_por_hora["Salidas"].idxmax(), "Hora"]

print(f"\n🕓 Hora pico detectada: {hora_pico}:00 h ({estadisticas_por_hora['Salidas'].max()} salidas)")
print("\n📋 Resumen por hora:\n")
print(estadisticas_por_hora.head(10))

# ------------------------------------------------------
# 4. Agrupación por ruta
# ------------------------------------------------------
estadisticas_por_ruta = df.groupby("ruta").agg({
    "salida": "count",
    "demanda": ["mean", "max", "min"],
    "duracion_ruta_min": "mean",
    "frecuencia_min": "mean"
}).reset_index()

estadisticas_por_ruta.columns = [
    "Ruta",
    "Total_Salidas",
    "Demanda_Prom",
    "Demanda_Max",
    "Demanda_Min",
    "Duracion_Prom",
    "Frecuencia_Prom"
]

print("\n🚏 Estadísticas por ruta:\n")
print(estadisticas_por_ruta)

# ------------------------------------------------------
# 5. Exportar resultados
# ------------------------------------------------------
estadisticas_por_hora.to_csv("estadisticas_por_hora.csv", index=False)
estadisticas_por_ruta.to_csv("estadisticas_por_ruta.csv", index=False)

print("\n💾 Archivos exportados:")
print("   - estadisticas_por_hora.csv")
print("   - estadisticas_por_ruta.csv")
print("\n✅ Reporte estadístico generado correctamente.")

