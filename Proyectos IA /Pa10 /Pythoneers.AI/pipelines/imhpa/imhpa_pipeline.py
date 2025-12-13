"""IMHPA pipeline orchestrator.

Exposes `run_all()` used by the top-level `pipeline_runner`.
"""
from pipelines.imhpa.realtime_temp import run as run_temp
from pipelines.imhpa.realtime_humedad import run as run_humidity
from pipelines.imhpa.realtime_lluvia import run as run_rain
from pipelines.imhpa.realtime_viento import run as run_wind


def run_all():
    """Ejecuta los sub-pipelines de IMHPA en secuencia."""
    print("Iniciando IMHPA - ejecución de sub-pipelines")
    try:
        run_temp()
    except Exception:
        print("Warning: fallo en temp, continuando...")
    try:
        run_humidity()
    except Exception:
        print("Warning: fallo en humedad, continuando...")
    try:
        run_rain()
    except Exception:
        print("Warning: fallo en lluvia, continuando...")
    try:
        run_wind()
    except Exception:
        print("Warning: fallo en viento, continuando...")

    print("IMHPA: ejecución completa")
from pipelines.imhpa.realtime_temp import run as run_temp
from pipelines.imhpa.realtime_humedad import run as run_humidity
from pipelines.imhpa.realtime_lluvia import run as run_rain
from pipelines.imhpa.realtime_viento import run as run_wind

def run_all():
    run_temp()
    run_humidity()
    run_rain()
    run_wind()