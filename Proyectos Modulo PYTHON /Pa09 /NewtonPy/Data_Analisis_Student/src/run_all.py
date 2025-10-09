from data_prep import clean_data
from features import generate_plots
from data_audit import audit_data
from log import logger

def run_pipeline():
    try:
        logger.info("Iniciando el proceso de limpieza de datos.")
        df_cleaned = clean_data()

        logger.info("Generando gráficos.")
        generate_plots(df_cleaned)

        logger.info("Auditando los datos.")
        audit_data()

        logger.info("Proceso completado con éxito.")
    except Exception as e:
        logger.error(f"Error en el pipeline: {e}")
        
# Ejecutar el pipeline
if __name__ == "__main__":
    run_pipeline()
