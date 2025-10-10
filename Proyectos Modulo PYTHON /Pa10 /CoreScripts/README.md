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



## 🚀 Instalación y Ejecución

### 1️⃣ Clona este repositorio
```bash
git clone https://github.com/tuusuario/HeartRiskSystem.git
cd HeartRiskSystem
2️⃣ Instala las dependencias
bash
Copiar código
pip install -r requirements.txt
3️⃣ Ejecuta el sistema
Si es una versión de consola:

bash
Copiar código
python main.py
O si incluye interfaz (ejemplo con Streamlit):

bash
Copiar código
streamlit run app.py
🧮 Datos de Entrada
El sistema requiere un conjunto de datos con las siguientes columnas (ejemplo):

age	sex	cp	trestbps	chol	fbs	restecg	thalach	exang	oldpeak	slope	ca	thal	target
63	1	3	145	233	1	0	150	0	2.3	0	0	1	1

📍 El atributo target indica 1 = presencia de enfermedad, 0 = ausencia.

📊 Ejemplo de Resultados
Precisión del modelo: 0.87

Matriz de confusión:

Curva ROC:

🧠 Modelos de Machine Learning
Los modelos comparados incluyen:

Logistic Regression

Random Forest Classifier

Support Vector Machine

K-Nearest Neighbors

Decision Tree

El mejor modelo se selecciona automáticamente según su rendimiento (accuracy y AUC).

🖼️ Capturas de Pantalla (si aplica)
Predicción	Visualización

🧪 Evaluación del Modelo
Métrica	Valor
Accuracy	0.87
Precision	0.86
Recall	0.84
F1-Score	0.85

💡 Posibles Mejoras Futuras
Integración con API médica.

Versión web con Flask o FastAPI.

Almacenamiento en base de datos (MySQL / MongoDB).

Entrenamiento automático con nuevos datos.

Dashboard interactivo de resultados.
