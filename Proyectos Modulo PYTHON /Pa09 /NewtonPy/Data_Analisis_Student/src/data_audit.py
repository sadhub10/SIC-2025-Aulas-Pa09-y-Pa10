import pandas as pd
from config import INTERIM_CSV

def audit_data():
    # Cargar los datos limpios
    df = pd.read_csv(INTERIM_CSV)
    
    # Resumen de las estadísticas de los datos
    print(df.describe())
    
    # Mostrar las columnas procesadas
    print("Columnas procesadas:")
    print(df.columns)
    
    return df
