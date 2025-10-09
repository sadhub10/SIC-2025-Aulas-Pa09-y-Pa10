import pandas as pd
import json
from config import RAW_DATA, MAPPING_FILE

def generate_column_mapping(df):
    # Renombramos las columnas para mayor claridad
    column_mapping = {
        'Beca': 'Ingreso_Beca',
        'Trabajo': 'Ingreso_Trabajo',
        'Apoyo_Familiar': 'Ingreso_Apoyo_Familiar',
        'Ingresos Totales': 'Total_Ingresos',
        'Gastos Totales': 'Total_Gastos',
        'Balance': 'Diferencia_Ingresos_Gastos',
        'Meta_Ahorro': 'Monto_Meta_Ahorro',
        'Alimentacion': 'Gasto_Alimentacion',
        'Transporte': 'Gasto_Transporte',
        'Vivienda': 'Gasto_Vivienda',
        'Matricula': 'Gasto_Matricula',
        'Material_Escolar': 'Gasto_Material_Escolar',
        'Ocio': 'Gasto_Ocio',
        'Cuidado_Personal': 'Gasto_Cuidado_Personal',
        'Salud': 'Gasto_Salud',
        'Tecnologia': 'Gasto_Tecnologia',
        'Miscelanea': 'Gasto_Miscelanea'
    }
    
    # Aplicamos el mapeo a las columnas del dataframe
    df.rename(columns=column_mapping, inplace=True)
    
    # Guardamos el mapeo como JSON
    with open(MAPPING_FILE, 'w') as f:
        json.dump(column_mapping, f, indent=4)
    
    return df

# Función para cargar el dataset y generar el mapeo
def process_mapping():
    # Leer el archivo Excel directamente con pd.read_excel()
    df = pd.read_excel(RAW_DATA)  # Asegúrate de que RAW_DATA esté correctamente configurado
    # Después de leer el archivo, generamos el mapeo
    df_mapped = generate_column_mapping(df)
    return df_mapped
