"""
Módulo 2 _ Simulación de demanda y tráfico

Este módulo proporciona modelos simplificados pero realistas
para estimar la demanda de pasajeros y las condiciones del tráfico.
Estos datos se usarán en los módulos posteriores para calcular
frecuencias, tiempos de viaje y horarios.

"""
import random
from datetime import datetime


# Clase: SimuladorDemanda
# Representa el nivel de demanda de pasajeros (0.0 a 1.0)
# considerando el día de la semana, la hora del día y un factor
# aleatorio leve para dar realismo.

class SimuladorDemanda:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)

        # Factores base por día de la semana
        # 0 = lunes, 6 = domingo
        self.factor_dia = {
            0: 1.0,  # Lunes
            1: 1.0,
            2: 1.0,
            3: 1.0,
            4: 1.1,  # Viernes, mayor movilidad
            5: 0.8,  # Sábado, menor demanda
            6: 0.6   # Domingo, baja demanda
        }

        # Factores por hora (picos en horas laborales)
        self.factor_hora = {
            **{h: 0.3 for h in range(0, 5)},    # madrugada
            **{h: 0.8 for h in range(5, 7)},    # pre-hora pico
            **{h: 0.95 for h in range(7, 9)},   # hora pico mañana
            **{h: 0.6 for h in range(9, 12)},   # media mañana
            12: 0.7, 13: 0.7,                   # mediodía
            **{h: 0.5 for h in range(14, 17)},  # primeras horas tarde
            **{h: 0.95 for h in range(17, 20)}, # hora pico tarde
            **{h: 0.4 for h in range(20, 24)}   # noche
        }

        # Multiplicadores por ruta (por si alguna ruta es más usada)
        self.factor_ruta = {
            "C898": 1.0  # se puede ajustar en el futuro
        }

    def obtener_demanda(self, ruta_id: str, fecha_hora: datetime) -> float:
        """Calcula un valor de demanda entre 0.0 y 1.0."""
        dia = fecha_hora.weekday()
        hora = fecha_hora.hour

        base = (
            self.factor_dia.get(dia, 1.0)
            * self.factor_hora.get(hora, 0.5)
            * self.factor_ruta.get(ruta_id, 1.0)
        )

        # Ruido aleatorio para simular variabilidad natural
        ruido = 1 + self.rng.uniform(-0.1, 0.1)
        demanda = base * ruido

        # Limitar a [0.0, 1.0]
        return round(min(max(demanda, 0.0), 1.0), 2)



# Clase: SimuladorTrafico
# ---------------------------------------------------------------
# Representa el nivel de congestión del tráfico (1.0 = libre,
# 1.5 = 50% más lento).

class SimuladorTrafico:
    def __init__(self):
        # Factores por hora (aumenta en horas pico)
        self.factor_trafico = {
            **{h: 1.0 for h in range(0, 6)},   # madrugada
            **{h: 1.2 for h in range(6, 9)},   # tráfico leve a fuerte
            **{h: 1.0 for h in range(9, 16)},  # tráfico normal
            **{h: 1.3 for h in range(16, 20)}, # hora pico tarde
            **{h: 1.1 for h in range(20, 24)}  # noche
        }

    def obtener_factor(self, fecha_hora: datetime) -> float:
        """Devuelve un multiplicador de tiempo de viaje según la hora."""
        hora = fecha_hora.hour
        return self.factor_trafico.get(hora, 1.0)


# Función de prueba (solo se ejecuta si se corre este archivo)=
if __name__ == "__main__":
    sim_d = SimuladorDemanda()
    sim_t = SimuladorTrafico()

    print("=== Ejemplo de simulación de demanda y tráfico ===")
    ahora = datetime.now().replace(hour=8, minute=0)
    print(f"Hora simulada: {ahora.strftime('%H:%M')}")
    print(f"Demanda Ruta C898: {sim_d.obtener_demanda('C898', ahora)}")
    print(f"Factor de tráfico: {sim_t.obtener_factor(ahora)}x")