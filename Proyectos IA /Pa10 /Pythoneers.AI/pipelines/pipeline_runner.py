"""
P I P E L I N E   R U N N E R
---------------------------------------
Control maestro para ejecutar todos los pipelines del sistema:

    - IMHPA (real time)
    - ETESA (histórico / mensual vía CSV)
    - MASTER DATASET (unificación IMHPA + ETESA)
    - OpenWeather API (futuro)
    - ACP (omitido por ahora)

Permite correr:
    1. Todo el sistema
    2. Pipelines individuales
"""

import time
import traceback
from datetime import datetime
import os

# === Importaciones de pipelines ===

# IMHPA
from pipelines.imhpa.imhpa_pipeline import run_all as run_imhpa

# ETESA CSV
from pipelines.etesa.etesa_pipeline import run_etesa

# UNIFICADOR
from pipelines.unify.unify_master import unify_master_dataset

from processing.merge_all_sources import merge_processed_dataset


# -------------------------------------------------------------
# Funciones auxiliares
# -------------------------------------------------------------

def banner(text):
    print("\n" + "=" * 70)
    print(" " * 20 + text)
    print("=" * 70 + "\n")


def safe_run(name, func):
    """
    Ejecuta cada pipeline con manejo de errores para evitar
    que un fallo detenga la ejecución completa.
    """
    try:
        banner(f" Ejecutando: {name} ")
        func()
        print(f"[OK] {name} completado.\n")

    except Exception as e:
        print(f"[ERROR] Falló el pipeline {name}: {e}")
        traceback.print_exc()
        print("\nContinuando con el siguiente módulo...\n")
        time.sleep(2)


# -------------------------------------------------------------
# Ejecución completa
# -------------------------------------------------------------

def run_all_pipelines():
    """Ejecuta TODOS los pipelines disponibles."""
    start = datetime.now()
    banner(" INICIANDO PIPELINES COMPLETOS ")

    # Asegurar que las carpetas de datos existen antes de ejecutar pipelines
    def ensure_data_dirs():
        dirs = [
            "data_raw",
            os.path.join("data_raw", "imhpa"),
            os.path.join("data_raw", "etesa"),
            os.path.join("data_raw", "osm"),
            "data_clean",
            os.path.join("data_clean", "imhpa"),
            os.path.join("data_clean", "master"),
        ]
        for d in dirs:
            try:
                os.makedirs(d, exist_ok=True)
            except Exception:
                # no bloquear la ejecución si no se puede crear alguna carpeta
                print(f"[WARN] No se pudo crear la carpeta: {d}")

    ensure_data_dirs()

    # === 1. IMHPA ===
    safe_run("IMHPA (Tiempo Real)", run_imhpa)

    # === 2. ETESA ===
    safe_run("ETESA (Histórico CSV)", run_etesa)

    # === 3. MASTER DATASET ===
    safe_run("Unificación del Dataset Maestro", unify_master_dataset)

    safe_run("Procesamiento Final del Dataset", merge_processed_dataset)
    

    end = datetime.now()
    banner(" PROCESO COMPLETADO ")
    print(f"Tiempo total: {end - start}")
    print("Pipelines ejecutados correctamente.\n")


# -------------------------------------------------------------
# Menú interactivo
# -------------------------------------------------------------

def menu():
    """Menú para ejecutar pipelines individuales."""
    while True:
        banner("PIPELINE RUNNER")

        print("""
Seleccione una opción:

1) Ejecutar TODOS los pipelines
2) Ejecutar solo IMHPA
3) Ejecutar solo ETESA
4) Ejecutar solo UNIFICACIÓN MASTER
5) Procesamiento FINAL del dataset (limpieza avanzada + outliers)
0) Salir
""")

        choice = input("Ingrese opción: ").strip()

        if choice == "1":
            run_all_pipelines()

        elif choice == "2":
            safe_run("IMHPA (Tiempo Real)", run_imhpa)

        elif choice == "3":
            safe_run("ETESA (Histórico CSV)", run_etesa)

        elif choice == "4":
            safe_run("Unificación del Dataset Maestro", unify_master_dataset)

        elif choice == "5":
            safe_run("Procesamiento Final del Dataset", merge_processed_dataset)

        elif choice == "0":
            print("Saliendo del Pipeline Runner...")
            break

        else:
            print("Opción inválida. Intente nuevamente.")
            time.sleep(1)


if __name__ == "__main__":
    menu()