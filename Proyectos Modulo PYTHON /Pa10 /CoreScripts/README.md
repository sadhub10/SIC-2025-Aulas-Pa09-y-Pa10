<div align="center">

# **HeartRiskSystem**
### 🩺 *Sistema Predictivo de Riesgo Cardíaco Basado en Machine Learning*

<img src="assets/image.png" alt="HeartRiskSystem" width="260"/>

**Análisis inteligente, diagnóstico preventivo y apoyo clínico con datos médicos reales.**

</div>

---

## **Descripción General**

**HeartRiskSystem** es una plataforma analítica desarrollada en **Python**, enfocada en la **predicción del riesgo de enfermedad cardíaca** mediante algoritmos de *Machine Learning*.  

Este sistema utiliza información médica de pacientes (como edad, colesterol, presión arterial, frecuencia cardíaca y otros indicadores clínicos) para **evaluar automáticamente el nivel de riesgo cardiovascular**.  

Gracias al modelo predictivo entrenado, el sistema puede clasificar a cada paciente en categorías como **bajo, medio o alto riesgo**, generando **reportes automáticos y personalizados** en formato `.txt`.

---

## **Contexto del Problema**

Las enfermedades cardiovasculares son una de las principales causas de mortalidad en el mundo.  
La detección temprana es crucial para prevenir complicaciones graves y reducir la carga en los sistemas de salud.  

Sin embargo, muchos diagnósticos dependen del juicio médico y de datos dispersos.  
**HeartRiskSystem** aborda esta problemática mediante una herramienta que analiza de forma **objetiva, reproducible y automatizada** los factores de riesgo cardíaco, apoyando al personal médico en la toma de decisiones.

---

## **Objetivos del Proyecto**

### Objetivo General
Desarrollar un sistema inteligente que permita **predecir el riesgo de enfermedad cardíaca** a partir de variables clínicas de entrada.

### Objetivos Específicos
- 🧹 Implementar un proceso de **limpieza y normalización** de datos médicos.  
- 🤖 Entrenar un modelo predictivo robusto usando algoritmos de *Machine Learning*.  
- 📊 Automatizar la **generación de reportes individuales** para cada paciente.  
- 📈 Visualizar el comportamiento de las variables más relevantes en el diagnóstico.  

---

## ⚙️ **Tecnologías y Librerías Utilizadas**

| Categoría | Herramientas |
|------------|--------------|
| Lenguaje principal | **Python 3.12** |
| Procesamiento de datos | pandas, numpy |
| Visualización | matplotlib, seaborn |
| Machine Learning | scikit-learn, joblib |
| Estructura y modularidad | scripts Python (.py) |
| Control de versiones | Git / GitHub |
| Reportes automáticos | Archivos `.txt` generados dinámicamente |

---

## 🧩 **Estructura del Proyecto**

```bash
HeartRiskSystem/
│
├── README.md                # Documento principal del proyecto
├── requirements.txt         # Dependencias necesarias
│
├── assets/                  # Recursos gráficos
│   └── image.png
│
├── modelos/                 # Modelos entrenados (.joblib)
│   ├── modelo_rf.joblib
│   ├── scaler.joblib
│   └── feature_cols.joblib
│
├── datasets/                # Conjuntos de datos médicos
│   ├── dataset_cuantitativo.csv
│   ├── dataset_descriptivo.csv
│   ├── historial_pacientes.csv
│   └── Heart_disease_cleveland_new.csv
│
├── reportes/                # Reportes generados automáticamente
│   └── reporte_paciente_*.txt
│
└── src/                     # Código fuente principal
    ├── main.py              # Script principal
    ├── config.py
    ├── analysis/
    │   ├── preprocesing.py  # Limpieza y preparación de datos
    │   └── visualization.py # Gráficas e interpretación visual
    └── models/
        ├── eda.py           # Exploratory Data Analysis
        └── models_predictive.py  # Entrenamiento y predicción
