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
🔍 Detalles Técnicos
🧬 Modelo de Aprendizaje Automático

El modelo utilizado es un Random Forest Classifier, seleccionado por su capacidad de manejar datos no lineales y alta interpretabilidad.

Durante el entrenamiento, se evaluaron múltiples algoritmos (Logistic Regression, Decision Tree, KNN, SVM), concluyendo que Random Forest ofrecía el mejor equilibrio entre precisión y estabilidad.

Precisión: ~87%

Recall: 0.85

F1-Score: 0.86

Validación cruzada: K-Fold (k=5)

📈 Variables más influyentes

Edad

Colesterol sérico

Presión arterial en reposo

Frecuencia cardíaca máxima

Nivel de glucosa y angina inducida por ejercicio

🧪 Flujo de Funcionamiento

Ingreso de datos del paciente
El usuario introduce las variables médicas en el sistema (edad, presión, colesterol, etc.).

Preprocesamiento de datos
Se estandarizan las variables mediante el scaler.joblib y se aplican transformaciones de limpieza.

Predicción del modelo
El modelo modelo_rf.joblib predice el nivel de riesgo cardíaco (0 = bajo, 1 = alto).

Generación de reporte personalizado
Se crea un archivo de texto con el resultado del diagnóstico, incluyendo:

Fecha y hora del análisis

Identificación del paciente

Nivel de riesgo

Recomendación general basada en el resultado

📊 Ejemplo de Salida del Sistema
-----------------------------------------
REPORTE DE ANÁLISIS — HeartRiskSystem
-----------------------------------------
Paciente: Joel Monrroy
Cédula: 81345353
Fecha: 2025-10-08 23:41:56

Resultado del modelo: RIESGO ALTO ⚠️

Interpretación:
El paciente presenta factores clínicos que elevan el riesgo de enfermedad cardíaca.
Se recomienda seguimiento médico y análisis cardiovascular especializado.

-----------------------------------------
Modelo: Random Forest Classifier
Precisión: 87%
-----------------------------------------

🚀 Guía de Ejecución
1️⃣ Clonar el repositorio
git clone https://github.com/usuario/HeartRiskSystem.git
cd HeartRiskSystem

2️⃣ Instalar dependencias
pip install -r requirements.txt

3️⃣ Ejecutar el sistema
python src/main.py


Los resultados se guardarán automáticamente en la carpeta reportes/.

🔮 Posibles Mejoras Futuras

💻 Implementar una interfaz gráfica (GUI) con Tkinter o PyQt.

🌐 Desplegar una versión web interactiva con Flask o Streamlit.

🩸 Integrar análisis en tiempo real desde sensores biomédicos.

📊 Ampliar el dataset con fuentes hospitalarias reales.

🧠 Añadir explicabilidad del modelo con SHAP o LIME.
