import pandas as pd
from config import INTERIM_CSV
from mapping_builder import process_mapping

def clean_data():
    # Cambiar: Leemos el archivo en process_mapping() y solo obtenemos el DataFrame limpio.
    df = process_mapping()  # No es necesario llamar a pd.read_excel nuevamente.
    
    # Limpiar datos: eliminamos filas con valores nulos en los ingresos y gastos
    df.dropna(subset=['Ingreso_Beca', 'Ingreso_Trabajo', 'Ingreso_Apoyo_Familiar', 'Total_Gastos'], inplace=True)
    
    # Reemplazar valores erróneos o negativos (si es necesario, por ejemplo, gastos negativos)
    df.loc[df['Total_Ingresos'] < 0, 'Total_Ingresos'] = 0
    df.loc[df['Total_Gastos'] < 0, 'Total_Gastos'] = 0
    
    # Guardamos el archivo limpio
    cleaned_file_path = INTERIM_CSV
    df.to_csv(cleaned_file_path, index=False)
    
    return df
