# SAMSUNG-INNOVATION-CAMPUS-PROJECT-1
Proyecto dedicado a el analisis de datos

# Proyecto de Análisis de Datos - Samsung Innovation Campus

Este es un proyecto desarrollado como parte del curso **Samsung Innovation Campus**, con el objetivo de analizar los datos financieros de los estudiantes para proporcionar recomendaciones sobre ingresos, gastos y ahorro.

## Integrantes

- **Aula**: PA09
- **Nombre del equipo**: Newton.py

### Integrantes del equipo:

1. Isaac Delgado
2. Milagros Alonzo
3. Sebastián Rodriguez
4. Carlos Roseman
5. Liseth Abrego

## Introducción

Este proyecto tiene como objetivo analizar los datos financieros de los estudiantes, específicamente su relación entre ingresos y gastos, y su capacidad de ahorro. El análisis se centra en la distribución de los ingresos, las categorías de gastos más comunes y la capacidad de los estudiantes para ahorrar. La herramienta generada tiene una visualización interactiva y un dashboard donde los usuarios pueden explorar estos datos de manera gráfica.

## Herramientas y Librerías

A continuación, se enumeran las herramientas y librerías utilizadas para llevar a cabo el análisis:

### **Librerías utilizadas**:

- **Pandas**: Para la manipulación y análisis de datos (leer archivos CSV/Excel, limpieza de datos, etc.).
- **Matplotlib**: Para la creación de gráficos estáticos (barras, dispersión, pie chart).
- **Streamlit**: Para crear la interfaz de usuario interactiva, incluyendo la visualización de los gráficos y el dashboard.
- **Plotly** (opcional si se desea usar gráficos más avanzados y dinámicos): Para la creación de gráficos interactivos.

### **Otras herramientas**:

- **Jupyter Notebooks** (opcional para exploración de datos previa).
- **VS Code o cualquier IDE de Python** para el desarrollo.

Aquí está el contenido formateado para un README bonito en GitHub:
markdown## 📁 Estructura del Proyecto

### 📝 Descripción de cada archivo

| Archivo | Descripción |
|---------|-------------|
| `config.py` | Contiene la configuración global del proyecto, incluidas las rutas a los archivos de datos y los directorios de salida |
| `data_prep.py` | Realiza la limpieza de datos, como eliminar valores nulos, renombrar columnas, y guardar el archivo limpio en `interim/` |
| `features.py` | Contiene las funciones que generan los gráficos (dispersión, barras apiladas, pie chart) y los visualiza a través de Streamlit |
| `log.py` | Implementa un sistema de logging para monitorear los pasos del pipeline |
| `mapping_builder.py` | Realiza el mapeo de las columnas de ingreso y gasto en el dataset |
| `data_audit.py` | Realiza una auditoría de los datos procesados, mostrando las estadísticas y las columnas utilizadas |
| `app.py` | Crea la interfaz de usuario interactiva utilizando Streamlit, mostrando un landing page y el dashboard |
| `run_all.py` | Orquestador para ejecutar todo el pipeline de procesamiento de datos y generación de gráficos |


## 📦 Requerimientos

A continuación se muestra el archivo `requirements.txt`, que contiene todas las dependencias necesarias para levantar el proyecto:
```txt
pandas==1.3.3
matplotlib==3.4.3
streamlit==1.3.0
plotly==5.3.1
```

**Mejoras aplicadas:**
- ✅ Emojis para hacer el README más atractivo y visual
- ✅ Tabla para la descripción de archivos (más ordenado)
- ✅ Separadores horizontales (`---`) para dividir secciones
- ✅ Numeración con emojis en las instrucciones
- ✅ Bloques de código correctamente formateados
- ✅ Estructura jerárquica clara con encabezados apropiados

El proyecto está estructurado de la siguiente manera:
```text
data_analisis_student/
├── data/                        # Datos crudos, procesados y finales
│   ├── raw/                     # Datos crudos (dataset.xlsx)
│   ├── interim/                 # Datos procesados (dataset_clean.csv)
│   └── processed/               # Datos finales procesados
├── docs/                        # Documentación y recursos adicionales
│   └── figures/                 # Gráficos generados
├── src/                         # Código fuente
│   ├── __init__.py              # este no lo logre
│   ├── config.py                # Configuración del proyecto (rutas, etc.)
│   ├── data_prep.py             # Preprocesamiento de datos
│   ├── features.py              # Generación de gráficos y análisis
│   ├── log.py                   # Sistema de logging
│   ├── mapping_builder.py       # Mapeo de columnas
│   ├── data_audit.py            # Auditoría de datos
    └── run_all.py               # Orquestador para ejecutar todo el pipeline
├── app.py                   # Streamlit app (landing page + dashboard)
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Este archivo
```


