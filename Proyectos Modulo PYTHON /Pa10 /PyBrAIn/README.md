BioVisión: Prototipo Analítico de Riesgo de Diabetes

Este repositorio contiene el código y los recursos del proyecto BioVisión, un prototipo analítico desarrollado en Python para identificar los factores de riesgo clave asociados a la diabetes a partir de un dataset clínico.

Objetivo del Proyecto
El objetivo principal es realizar un Análisis Exploratorio de Datos (EDA) para descubrir patrones, correlaciones y tendencias en los datos clínicos. Buscamos responder preguntas como:
- ¿Qué variables clínicas tienen una mayor correlación con el diagnóstico de diabetes?
- ¿Cómo varía la prevalencia de la diabetes según la edad y el género?
- ¿Cuál es el perfil de un paciente con alto riesgo de diabetes?

Dataset Utilizado
El análisis se basa en el archivo DiabetesPrediccion.csv, un dataset que contiene información demográfica y clínica anonimizada de pacientes, incluyendo:
- Variables demográficas: gender, age.
- Historial médico: hypertension, heart_disease, smoking_history.
- Métricas clínicas: bmi, HbA1c_level, blood_glucose_level.
- Variable objetivo: diabetes (0: No diabético, 1: Diabético).

Estructura del Notebook (BioVision_Colab_Notebook.ipynb)
El notebook está organizado en una secuencia lógica de pasos para garantizar la reproducibilidad del análisis:
- Configuración del Entorno: Importación de las librerías necesarias para el análisis y la visualización (pandas, numpy, matplotlib).
- Carga y Limpieza de Datos:
	Se carga el dataset DiabetesPrediccion.csv.
	Se realiza una limpieza inicial, que incluye la estandarización de nombres de columnas y la conversión de variables categóricas 	(como gender y smoking_history) a formatos numéricos para facilitar el análisis.
- Análisis Descriptivo: Se calculan las estadísticas fundamentales (media, mediana, desviación estándar) para obtener una primera    comprensión de la distribución de los datos.
- Análisis de Prevalencia:
	Se agrupan los datos por edad y género para calcular la tasa de prevalencia de diabetes.
	Se generan visualizaciones (gráficos de barras) para ilustrar cómo el riesgo de diabetes cambia a través de diferentes grupos 	demográficos.
- Análisis de Correlación:
	Se calcula la matriz de correlación (usando el método de Pearson) entre todas las variables numéricas y la variable objetivo 	diabetes.
	Se visualiza esta matriz a través de un mapa de calor (heatmap) para identificar de forma rápida e intuitiva los factores con 	mayor impacto.
- Exportación de Resultados:
	Los resultados clave del análisis (como las tasas de prevalencia y las correlaciones) se exportan a archivos .csv.
	Todas las visualizaciones generadas se guardan como archivos de imagen (.png) para su uso en informes y presentaciones.

Cómo Ejecutar el Código
- Abre el archivo BioVision_Colab_Notebook.ipynb en Google Colab o un entorno Jupyter.
- Asegúrate de que el archivo DiabetesPrediccion.csv esté en el mismo directorio o súbelo a la sesión de Colab.
- Ejecuta las celdas en orden secuencial.