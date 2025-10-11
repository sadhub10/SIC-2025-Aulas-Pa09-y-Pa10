
# 🚌 MOVILIDAD 4.0 – Sistema Inteligente de Gestión Operativa del Transporte Público

**Desarrollado por:**  
Omar Jaramillo · Haneff Botello · César Garzón · Oliver Santana  
Universidad Tecnológica de Panamá (UTP)

---

## 📘 Descripción General

**MOVILIDAD 4.0** es un sistema inteligente de análisis y gestión operativa del transporte público urbano.  
Su objetivo principal es **optimizar la frecuencia, demanda y uso de flota de buses** mediante el análisis de datos provenientes de **datasets GTFS** y rutas personalizadas.

El sistema está diseñado especialmente para **operadores y planificadores del transporte**, no para usuarios finales, permitiendo la toma de decisiones basadas en métricas de eficiencia y visualizaciones dinámicas.

---

## ⚙️ Funcionalidades Principales

- Carga automática de datasets GTFS (`agency.txt`, `routes.txt`, `trips.txt`, etc.)
- Integración de rutas personalizadas mediante archivos CSV.
- Cálculo de demanda, frecuencia y flota requerida por hora.
- Visualización mediante gráficas:
  - 📊 Barras → Buses requeridos por hora  
  - 📈 Línea → Demanda promedio por hora  
  - 🥧 Pastel → Distribución de flota operativa (%)  
  - 🧩 Mapa de calor → Correlación entre demanda, frecuencia y flota  
- Exportación automática de reportes en PDF.
- Interfaz moderna con colores contrastantes y navegación lateral.

---

## 🧠 Estructura del Proyecto

```
MOVILIDAD_4.0/
│
├── main.py                   # Punto de entrada del sistema
├── movilidad4.py              # Interfaz gráfica principal (Tkinter + Matplotlib)
│
├── modulo1.py                 # Definición de rutas y paradas (GTFS base)
├── modulo2.py                 # Simuladores de tráfico y demanda
├── modulo3.py                 # Cálculo de tiempos de viaje reales
├── modulo4.py                 # Generador de horarios de salida
├── modulo5.py                 # Métricas y validaciones estadísticas
├── modulo6.py                 # Planificador operacional (control de flota y demanda)
│
├── datasets/
│   ├── agency.txt
│   ├── routes.txt
│   ├── trips.txt
│   ├── stop_times.txt
│   ├── stops.txt
│   └── M671.csv               # Ejemplo de ruta personalizada
│
└── README_MOVILIDAD4.0.md
```

---

## 💻 Requisitos del Sistema

- **Python 3.11+**
- **Bibliotecas necesarias:**  
  ```bash
  pip install matplotlib pandas numpy reportlab tk
  ```
- **Entorno recomendado:** Visual Studio Code o PyCharm

---

## 🧩 Funcionamiento General

1. **Carga de datasets:** El sistema integra automáticamente los archivos GTFS base y permite agregar rutas CSV desde la interfaz mediante el botón “➕ Agregar Ruta”.
2. **Procesamiento:** Los módulos analizan cada ruta y generan una tabla horaria con la demanda y frecuencia operativa.
3. **Cálculo:** `modulo6` determina el número óptimo de buses por hora (máximo 3 por cada 30 min según parámetros operativos).
4. **Visualización:** Se generan gráficos dinámicos para interpretar las condiciones del sistema.
5. **Reporte:** El usuario puede exportar los resultados como PDF con gráficos y resumen operativo.

---

## 🧭 Descripción de Módulos

| Módulo | Descripción |
|--------|--------------|
| **modulo1** | Define la estructura base de rutas y paradas a partir del GTFS. |
| **modulo2** | Simula las condiciones de tráfico y la demanda horaria. |
| **modulo3** | Calcula los tiempos de recorrido reales entre paradas según tráfico y demanda. |
| **modulo4** | Genera los horarios de salida de buses según la ruta y la hora del día. |
| **modulo5** | Calcula métricas estadísticas y verificaciones de consistencia. |
| **modulo6** | Planificador operativo: estima la cantidad de buses, frecuencia y flota necesaria. |

---

## 🎨 Diseño de Interfaz

- Interfaz **Tkinter** con panel lateral para navegación.
- Paleta de colores oscuros (modo nocturno profesional).
- Gráficos integrados con **Matplotlib** y exportación directa a PDF.
- Responsive horizontal con prioridad de visualización completa (sin scroll).

---

## 📈 Métricas Principales

- **Frecuencia promedio (minutos)**  
- **Flota máxima requerida (unidades)**  
- **Hora pico (hora de mayor demanda)**  
- **Tiempo total estimado del recorrido (minutos)**

Estas métricas son calculadas automáticamente y se actualizan en tiempo real al seleccionar cada ruta.

---

## 📊 Ejemplo de Dataset Personalizado (M671.csv)

```csv
hora,demanda,frecuencia,buses,duracion
5,0.35,20,2,60
6,0.70,20,3,60
7,0.90,20,3,60
8,0.85,20,3,60
9,0.55,20,2,60
10,0.45,20,2,60
11,0.50,20,2,60
12,0.60,20,2,60
13,0.55,20,2,60
14,0.50,20,2,60
15,0.45,20,2,60
16,0.65,20,2,60
17,0.80,20,3,60
18,0.85,20,3,60
19,0.75,20,2,60
20,0.50,20,2,60
21,0.35,20,2,60
```

---

## 🚀 Objetivo del Prototipo

Reducir la ineficiencia operativa del transporte público mediante la optimización de la frecuencia de buses, generando reportes visuales y decisiones estratégicas para los planificadores de movilidad.

---

## 🧾 Licencia

Este proyecto fue desarrollado con fines académicos en la **Universidad Tecnológica de Panamá (UTP)**.  
Su distribución está permitida únicamente para propósitos educativos o de investigación con el debido reconocimiento al equipo desarrollador.

---

## 👥 Créditos

**Equipo de desarrollo MOVILIDAD 4.0**  
- Omar Jaramillo  
- Haneff Botello  
- César Garzón  
- Oliver Santana  

---
