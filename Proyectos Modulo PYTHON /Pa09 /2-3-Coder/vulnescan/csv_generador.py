import csv
from datetime import datetime
import os

def generar_csv_reporte(datos_hallazgos, directorio_salida="reportes"):
   
    if not datos_hallazgos or datos_hallazgos[0]['ID_VULN'] == 'CONEXION_FALLIDA':
        if datos_hallazgos and datos_hallazgos[0]['ID_VULN'] == 'CONEXION_FALLIDA':
            print(f"[AVISO] No se genera CSV por fallo de conexión.")
        else:
            print("[AVISO] La lista de hallazgos está vacía. No se generará el CSV.")
        return None

    fieldnames = ["ID_VULN", "URL_AFECTADA", "SEVERIDAD", "TIPO_FALLO"]
    
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)

    # formato del nombre del archivo 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"reporte_seguridad_{timestamp}.csv"
    ruta_completa = os.path.join(directorio_salida, nombre_archivo)

    try:
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(datos_hallazgos)

        print(f"[ÉXITO] Reporte CSV generado correctamente en: {ruta_completa}")
        return ruta_completa

    except Exception as e:
        print(f"[ERROR] No se pudo generar el archivo CSV: {e}")
        return None