import pandas as pd
import numpy as np
import re

# cargamos los CSVs
archivos_csv = ['batch1_1.csv', 'batch1_2.csv', 'batch1_3.csv']
dataframes = []

for archivo in archivos_csv:
    df = pd.read_csv(archivo)
    dataframes.append(df)

dataset = pd.concat(dataframes, ignore_index=True)
columna_objetivo = 'OCRed Text' 

#función de limpieza
def limpiar_precio_complejo(texto):
    if not isinstance(texto, str):
        return 0.0
    
    # El formato que vi del csv es por  ejm : Total $ 87,94 $ 8,79 $ 96,73
    # Uso regex para buscar números que tengan decimales (con punto o coma)
    #Busco dígitos, seguidos opcionalmente de punto/coma y más dígitos
    patron = r'(\d+[\.,]\d+)'
    
    encontrados = re.findall(patron, texto)
    
    if encontrados:
        # Si encuentra por ejm ['87,94', '8,79', '96,73'], tomamos el ÚLTIMO [-1]
        precio_final = encontrados[-1]
        
        # Reemplazamos coma por punto para que Python entienda el decimal
        precio_final = precio_final.replace(',', '.')
        
        try:
            return float(precio_final)
        except ValueError:
            return 0.0
    return 0.0

# Verificamos si la columna existe antes de procesar
if columna_objetivo in dataset.columns:
    dataset['Total_Limpio'] = dataset[columna_objetivo].apply(limpiar_precio_complejo)
    
    # Filtro filas que hayan dado 0 (errores de lectura) para no ensuciar el modelo
    dataset = dataset[dataset['Total_Limpio'] > 0]
    
    # Calcular límites
    limite_bajo = dataset['Total_Limpio'].quantile(0.33)
    limite_alto = dataset['Total_Limpio'].quantile(0.66)
    
    print(f"Límites calculados -> BAJO: <{limite_bajo:.2f} | MEDIO: {limite_bajo:.2f}-{limite_alto:.2f} | ALTO: >{limite_alto:.2f}")

    def clasificar(valor):
        if valor <= limite_bajo: return 0
        elif valor <= limite_alto: return 1
        else: return 2

    dataset['Categoria'] = dataset['Total_Limpio'].apply(clasificar)
    print("Datos listos. Muestra:")
    print(dataset[['Total_Limpio', 'Categoria']].head())
    
    # se guarda el ds
    dataset.to_csv('dataset_listo_para_entrenar.csv', index=False)

else:
    print(f"ERROR: La columna '{columna_objetivo}' no existe.")
    print(f"Las columnas disponibles son: {dataset.columns.tolist()}")