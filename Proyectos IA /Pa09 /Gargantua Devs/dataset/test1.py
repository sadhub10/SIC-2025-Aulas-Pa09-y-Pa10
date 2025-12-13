import pandas as pd

# Carga solo el primer archivo para inspeccionar
df = pd.read_csv('batch1_1.csv') 

print("--- NOMBRES DE LAS COLUMNAS ---")
print(df.columns.tolist())

print("\n--- PRIMERAS FILAS ---")
print(df.head())