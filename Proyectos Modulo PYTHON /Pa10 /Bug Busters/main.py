"""
BusPredict - Sistema de Predicción de Transporte Público
Interfaz gráfica principal (Tkinter)
Samsung Innovation Campus 2025
"""

from pathlib import Path
from buspredict.analizador import AnalizadorDescriptivo
from buspredict.predictor import PredictorHeadway
from buspredict.buscador import BuscadorRutas
from interfaz.ventana_principal import VentanaPrincipal
import sys


def main():
    """Punto de entrada principal del sistema BusPredict (Interfaz Gráfica)."""
    print("\n🚌 Iniciando BusPredict - Interfaz Gráfica")

    # -------------------------------
    # Verificación de archivos base
    # -------------------------------
    ruta_eventos = Path("data/transformed-data/eventos_buses.csv")
    ruta_resumen = Path("data/transformed-data/resumen_eventos.csv")

    if not ruta_eventos.exists() or not ruta_resumen.exists():
        print("\n❌ Archivos de datos no encontrados.")
        print("   Asegúrate de haber ejecutado los scripts previos:")
        print("   → python scripts/generate_events.py")
        print("   → python scripts/analyze_dataset.py\n")
        sys.exit(1)

    try:
        # -------------------------------
        # Inicialización de componentes
        # -------------------------------
        analizador = AnalizadorDescriptivo(str(ruta_eventos), str(ruta_resumen))
        predictor = PredictorHeadway(str(ruta_eventos), str(ruta_resumen))
        buscador = BuscadorRutas(str(ruta_resumen))

        # -------------------------------
        # Lanzar la interfaz principal
        # -------------------------------
        app = VentanaPrincipal(analizador, predictor, buscador)
        app.mainloop()

    except Exception as e:
        print(f"\n⚠️ Error al iniciar la aplicación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
