# ======================================================
# PROYECTO PRINCIPAL: SISTEMA DE PLANIFICACIÓN DE TRANSPORTE
# ======================================================
# Este archivo integra todos los módulos:
#   1️⃣ modulo1.py → Red de transporte
#   2️⃣ modulo2.py → Demanda y tráfico
#   3️⃣ modulo3.py → Tiempos reales
#   4️⃣ modulo4.py → Generador de horarios
#   5️⃣ modulo5.py → Visualización y reportes
#
# Ejecútalo directamente para generar toda la simulación.
# ======================================================

from datetime import datetime
from modulo1 import RUTAS, PARADAS, FLOTA_AUTOBUSES
from modulo2 import SimuladorDemanda, SimuladorTrafico
from modulo3 import CalculadorTiempos
from modulo4 import GeneradorHorarios
from modulo5 import ReporteTransporte

# ======================================================
# ETAPA 1: Mostrar información base de la red
# ======================================================
print("=== SISTEMA DE PLANIFICACIÓN DE TRANSPORTE ===\n")

print("📍 Paradas cargadas:", len(PARADAS))
print("🚌 Rutas disponibles:", len(RUTAS))
print("🚐 Flota de autobuses:", len(FLOTA_AUTOBUSES))
print("\n------------------------------------------------------")

# ======================================================
# ETAPA 2: Prueba de simuladores (demanda y tráfico)
# ======================================================
sim_d = SimuladorDemanda()
sim_t = SimuladorTrafico()
hora_prueba = datetime.now().replace(hour=8, minute=0)
print("📊 Simulación de condiciones a las 8:00 a.m.")
print("Demanda estimada:", sim_d.obtener_demanda("C898", hora_prueba))
print("Factor de tráfico:", sim_t.obtener_factor(hora_prueba))
print("------------------------------------------------------")

# ======================================================
# ETAPA 3: Calcular tiempos reales de una ruta
# ======================================================
calc = CalculadorTiempos()
resultado_tiempos = calc.calcular_tiempo_ruta("C898", hora_prueba)
print(f"🕒 Tiempo estimado total de la ruta C898: {resultado_tiempos['tiempo_total_min']} min")
print("------------------------------------------------------")

# ======================================================
# ETAPA 4: Generar horarios dinámicos
# ======================================================
gen = GeneradorHorarios()
fecha = datetime.now().replace(hour=6, minute=0)
horarios = gen.generar_todos_los_horarios(fecha)
print(f"🗓️ Total de horarios generados: {len(horarios)}")
print("Ejemplo:")
for h in horarios[:3]:
    print(f"Ruta {h['ruta']} | Salida {h['salida']} | Llegada {h['llegada']} | Demanda {h['demanda']} | Freq {h['frecuencia_min']} min")
print("------------------------------------------------------")

# ======================================================
# ETAPA 5: Generar reportes y gráficos
# ======================================================
print("📈 Generando reportes finales...")
reporte = ReporteTransporte()
reporte.generar_reportes_completos()

print("✅ Sistema completado. Archivos generados:")
print(" - horarios_generados.csv")
print(" - estadisticas_generales.csv")
print(" - salidas_por_hora.png")
print(" - demanda_promedio.png")
print("\n🚀 Prototipo listo para demostración y pitch.")
