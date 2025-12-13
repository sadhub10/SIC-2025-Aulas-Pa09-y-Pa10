# Mental Health Monitoring

Sistema de clasificación básica de condiciones emocionales utilizando técnicas tradicionales de Procesamiento de Lenguaje Natural (NLP). El modelo identifica estados clínicos aproximados a partir de textos escritos por usuarios, como ansiedad, estrés, depresión, ideación suicida, entre otros.

## 1. Planteamiento del Problema

El aumento de trastornos emocionales como ansiedad, depresión y estrés ha puesto en evidencia la necesidad de herramientas que permitan analizar de manera rápida y automatizada señales tempranas de malestar psicológico.

Las soluciones existentes suelen ser costosas, propietarias o requieren infraestructura avanzada, lo que limita su uso en entornos educativos, académicos y organizaciones sociales.

Este proyecto propone un sistema accesible que, mediante análisis de texto, permita identificar patrones lingüísticos asociados a condiciones emocionales, funcionando como un apoyo inicial para monitoreo y estudio de tendencias en salud mental.

## 2. Objetivos del Proyecto

### Objetivo General

Desarrollar un prototipo funcional capaz de clasificar textos breves según estados emocionales o condiciones clínicas utilizando técnicas NLP de nivel básico e intermedio.

### Objetivos Específicos

1. Implementar un pipeline completo de preprocesamiento de texto (limpieza, tokenización, normalización).
2. Entrenar modelos tradicionales de Machine Learning (SVM, Naive Bayes) utilizando representaciones vectoriales como TF-IDF.
3. Mejorar el rendimiento del modelo aplicando balanceo de clases y técnicas de oversampling.
4. Construir un dashboard interactivo en Streamlit que permita ingresar textos y visualizar resultados de clasificación.
5. Documentar el proceso y generar una base para futuras fases más avanzadas basadas en modelos contextuales (Transformers).

## 3. Herramientas Utilizadas

### Lenguajes y Librerías

- **Python 3.12**
- **Scikit-learn**: modelos tradicionales de clasificación y vectorización con TF-IDF
- **NLTK**: limpieza y normalización de texto
- **Imbalanced-learn**: balanceo de clases mediante SMOTE
- **Joblib**: guardado y carga de modelos
- **Deep-Translator**: traducción automática de textos al inglés cuando es necesario
- **Streamlit**: construcción del dashboard interactivo

### Infraestructura y Organización

- Estructura modular basada en `src/`
- Jupyter Notebooks para experimentación
- GitHub para control de versiones y despliegue del repositorio

## 4. Resultado del Proyecto

El proyecto culmina con un sistema funcional capaz de:

1. Recibir textos escritos por un usuario.
2. Traducir automáticamente al inglés si el texto no está en ese idioma.
3. Procesar y vectorizar el texto mediante un modelo TF-IDF entrenado previamente.
4. Clasificar el texto en una de las categorías clínicas disponibles: **Anxiety**, **Stress**, **Depression**, **Suicidal**, **Bipolar**, **Personality disorder** o **Normal**.
5. Visualizar el resultado en un dashboard interactivo desarrollado en Streamlit.

El modelo utiliza un **SVM con balanceo de clases y TF-IDF con bigramas**, lo que mejora la sensibilidad hacia expresiones complejas y clases menos representadas. Aunque esta aproximación no sustituye modelos avanzados basados en Transformers, establece una base sólida para análisis lingüístico básico y demuestra el potencial de un sistema automatizado para detección temprana de señales emocionales.
