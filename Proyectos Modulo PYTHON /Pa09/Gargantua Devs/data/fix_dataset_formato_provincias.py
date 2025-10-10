import pandas as pd

# --- CONFIGURACIÓN ---
archivo_entrada = 'data/dataset_homicidios.csv' 
archivo_salida = 'data/dataset_mejorado_joder.csv'

# --- INICIO DEL SCRIPT ---
print(f"Iniciando la simplificación de la columna 'provincia' en '{archivo_entrada}'...")

try:
    df = pd.read_csv(archivo_entrada)

    # --- LÓGICA DE SIMPLIFICACIÓN Y NORMALIZACIÓN ---

    # 1.Si 'provincia' contiene "San Miguelito", se convierte en "Panamá".
    # Uso dek .str.contains() para encontrar todas las variaciones. 'na=False' maneja celdas vacías.
    mascara_san_miguelito = df['provincia'].str.contains('San Miguelito', na=False)
    df.loc[mascara_san_miguelito, 'provincia'] = 'Panamá'
    
    # 2. aplciacion el resto de las normalizaciones para las comarcas.
    #Kuna o Guna?
    #Guna es correcto
    mapa_normalizacion = {
        'Comarca_Ngäbe_Buglé': 'Comarca Ngäbe-Buglé',
        'Comarca Ngäbe Buglé': 'Comarca Ngäbe-Buglé',
        'Emberá Wounaan': 'Comarca Emberá-Wounaan',
        'Comarca Emberá Wounaan': 'Comarca Emberá-Wounaan',
        'Comarca Kuna Yala': 'Comarca Guna Yala'
    }
    df['provincia'] = df['provincia'].replace(mapa_normalizacion)
    
    # 3.elimino espacios extra y aseguro la tilde en Panamá.
    df['provincia'] = df['provincia'].str.strip().replace({'Panama': 'Panamá'})
    
    print("Simplificación y normalización de provincias completada.")

    # --- GUARDAR Y VERIFICAR ---
    df.to_csv(archivo_salida, index=False, encoding='utf-8-sig')

    print("-" * 40)
    print("Proceso finalizado")
    print(f"El dataset simplificado se ha guardado como: '{archivo_salida}'")
    print("\n--- Verificación: Conteo de valores en la columna 'provincia' ---")
    print(df['provincia'].value_counts().to_string())
    print("-" * 40)

except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{archivo_entrada}'. necesito revisar el nomre en la sección de CONFIGURACIÓN.")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")