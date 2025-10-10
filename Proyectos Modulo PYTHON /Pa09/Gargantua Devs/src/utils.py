# Limpiar solo para el filtro (sin modificar el DataFrame)
def obtener_rangos_estandarizados(df):
    rangos_unicos = df['rango_de_edad'].dropna().unique()
    rangos_limpios = set()
    
    for rango in rangos_unicos:
        rango_str = str(rango).strip().lower()
        rango_limpio = (rango_str.replace('años', '')
                                .replace('año', '')
                                .replace(' ', '')
                                .replace('a', '-'))
        rangos_limpios.add(rango_limpio)
    
    return sorted(rangos_limpios)