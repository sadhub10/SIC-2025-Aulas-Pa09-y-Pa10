"""
Módulo 4 _ Visualización y análisis
Gráficos, resumen y exportación

"""
# MÓDULO 4: GENERADOR DE HORARIOS Y FRECUENCIAS
# Este módulo utiliza los cálculos de demanda, tráfico y tiempos reales
# para generar un horario operativo dinámico para cada ruta del sistema.
#
# Entrada:  Datos de módulos 1, 2 y 3
# Salida:   Diccionario con horarios de salida y llegada por ruta

from datetime import datetime, timedelta, time
from modulo1 import RUTAS, FLOTA_AUTOBUSES
from modulo2 import SimuladorDemanda
from modulo3 import CalculadorTiempos

class GeneradorHorarios:
    def __init__(self, hora_inicio: time = time(6, 0), hora_fin: time = time(22, 0)):
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.sim_demanda = SimuladorDemanda()
        self.calc_tiempos = CalculadorTiempos()

    def determinar_frecuencia(self, demanda: float) -> int:
        """
        Determina la frecuencia de salida (minutos entre buses) según la demanda.
        Cuanto mayor la demanda, menor el intervalo.
        """
        if demanda >= 0.85:
            return 10
        elif demanda >= 0.65:
            return 15
        elif demanda >= 0.40:
            return 20
        elif demanda >= 0.20:
            return 30
        else:
            return 45

    def generar_horarios_ruta(self, ruta_id: str, fecha_base: datetime):
        """
        Genera el horario de una ruta específica para todo el día.
        """
        if ruta_id not in RUTAS:
            raise ValueError(f"Ruta {ruta_id} no encontrada.")

        # Tiempo total estimado del recorrido
        info_tiempo = self.calc_tiempos.calcular_tiempo_ruta(ruta_id, fecha_base)
        duracion_ruta = info_tiempo["tiempo_total_min"]

        # Crear cronograma
        horarios = []
        hora_actual = datetime.combine(fecha_base.date(), self.hora_inicio)
        hora_fin = datetime.combine(fecha_base.date(), self.hora_fin)

        while hora_actual <= hora_fin:
            demanda = self.sim_demanda.obtener_demanda(ruta_id, hora_actual)
            frecuencia = self.determinar_frecuencia(demanda)

            # Registrar salida
            salida = hora_actual.strftime("%H:%M")
            llegada_dt = hora_actual + timedelta(minutes=duracion_ruta)
            llegada = llegada_dt.strftime("%H:%M")

            horarios.append({
                "ruta": ruta_id,
                "salida": salida,
                "llegada": llegada,
                "demanda": demanda,
                "frecuencia_min": frecuencia,
                "duracion_ruta_min": round(duracion_ruta, 2)
            })

            # Avanzar a la siguiente salida
            hora_actual += timedelta(minutes=frecuencia)

        return horarios

    def generar_todos_los_horarios(self, fecha_base: datetime):
        """
        Genera los horarios de todas las rutas registradas.
        """
        todos = []
        for ruta_id in RUTAS.keys():
            lista = self.generar_horarios_ruta(ruta_id, fecha_base)
            todos.extend(lista)
        return todos


# ======================================================
# Ejemplo de uso
# ======================================================
if __name__ == "__main__":
    print("=== Generación de Horarios Dinámicos ===")
    fecha = datetime.now().replace(hour=6, minute=0)
    generador = GeneradorHorarios()

    horarios = generador.generar_todos_los_horarios(fecha)

    print(f"Rutas procesadas: {len(RUTAS)}")
    print(f"Autobuses disponibles: {len(FLOTA_AUTOBUSES)}")
    print(f"Total de salidas generadas: {len(horarios)}\n")

    # Mostrar las primeras 5 salidas
    for h in horarios[:5]:
        print(f"{h['ruta']} | Salida: {h['salida']} | Llegada: {h['llegada']} | Demanda: {h['demanda']} | Freq: {h['frecuencia_min']} min")
