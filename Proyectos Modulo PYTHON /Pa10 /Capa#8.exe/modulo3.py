"""
Módulo 3 – Calculador de tiempos de viaje reales
Versión extendida compatible con rutas personalizadas (CSV).
"""

from datetime import datetime, timedelta
from modulo1 import RUTAS, PARADAS
from modulo2 import SimuladorDemanda, SimuladorTrafico


class CalculadorTiempos:
    def __init__(self):
        self.sim_trafico = SimuladorTrafico()
        self.sim_demanda = SimuladorDemanda()

    def calcular_tiempo_ruta(self, ruta_id: str, hora_inicio: datetime) -> dict:
        """
        Devuelve un diccionario con:
        - tiempos reales entre paradas
        - tiempo total estimado de la ruta
        Soporta rutas oficiales y personalizadas cargadas desde CSV.
        """
        if ruta_id not in RUTAS:
            raise ValueError(f"Ruta {ruta_id} no encontrada en RUTAS.")

        ruta = RUTAS[ruta_id]
        paradas = ruta.get("paradas", [])

        if not paradas or len(paradas) < 2:
            raise ValueError(f"La ruta {ruta_id} no tiene suficientes paradas definidas.")

        resultados = []
        tiempo_total = 0.0
        hora_actual = hora_inicio

        for i in range(len(paradas) - 1):
            parada_actual = paradas[i]
            parada_siguiente = paradas[i + 1]

            # Obtención del tiempo base entre paradas
            tiempo_base = parada_actual.get("tiempo_transcurso", 0)
            if tiempo_base is None:
                tiempo_base = 0

            # Aplicar factores de tráfico y demanda
            factor_trafico = self.sim_trafico.obtener_factor(hora_actual)
            demanda = self.sim_demanda.obtener_demanda(ruta_id, hora_actual)

            # Ajuste de tiempo real: base × tráfico + congestión por demanda
            tiempo_real = tiempo_base * factor_trafico + (demanda * 0.5)

            # Obtener nombres de las paradas (según disponibilidad)
            id_actual = parada_actual.get("id")
            id_siguiente = parada_siguiente.get("id")

            if id_actual in PARADAS:
                nombre_desde = PARADAS[id_actual]["nombre"]
            else:
                nombre_desde = parada_actual.get("nombre", f"Parada {i+1}")

            if id_siguiente in PARADAS:
                nombre_hacia = PARADAS[id_siguiente]["nombre"]
            else:
                nombre_hacia = parada_siguiente.get("nombre", f"Parada {i+2}")

            # Registrar el segmento calculado
            resultados.append({
                "desde": nombre_desde,
                "hacia": nombre_hacia,
                "tiempo_base": tiempo_base,
                "factor_trafico": round(factor_trafico, 2),
                "demanda": round(demanda, 2),
                "tiempo_real": round(tiempo_real, 2)
            })

            # Avanzar la hora simulada
            hora_actual += timedelta(minutes=tiempo_real)
            tiempo_total += tiempo_real

        return {
            "ruta": ruta["nombre"],
            "tiempo_total_min": round(tiempo_total, 2),
            "segmentos": resultados
        }

    def calcular_todas_las_rutas(self, hora_inicio: datetime):
        """
        Calcula el tiempo total estimado para todas las rutas registradas.
        """
        resumen = []
        for ruta_id in RUTAS.keys():
            try:
                info = self.calcular_tiempo_ruta(ruta_id, hora_inicio)
                resumen.append({
                    "ruta": info["ruta"],
                    "tiempo_total_min": info["tiempo_total_min"]
                })
            except Exception as e:
                # Evita que un error en una ruta detenga el proceso global
                resumen.append({
                    "ruta": ruta_id,
                    "tiempo_total_min": None,
                    "error": str(e)
                })
        return resumen


# ==========================================================
# Ejemplo de uso directo
# ==========================================================
if __name__ == "__main__":
    print("=== Simulación de tiempos de viaje (ajustados por tráfico y demanda) ===")
    hora_simulada = datetime.now().replace(hour=8, minute=0)
    calculador = CalculadorTiempos()

    # Ruta de prueba (ajustar según exista)
    ruta_prueba = "T149"  # Puedes cambiar por M671 si ya la agregaste
    try:
        resultado = calculador.calcular_tiempo_ruta(ruta_prueba, hora_simulada)
        print(f"\nRuta: {resultado['ruta']}")
        print(f"Tiempo total estimado: {resultado['tiempo_total_min']} min\n")

        for seg in resultado["segmentos"]:
            print(
                f"{seg['desde']} -> {seg['hacia']} | "
                f"Base: {seg['tiempo_base']} min | "
                f"Tráfico: x{seg['factor_trafico']} | "
                f"Demanda: {seg['demanda']} | "
                f"Real: {seg['tiempo_real']} min"
            )
    except Exception as e:
        print(f"❌ Error al calcular ruta: {e}")
