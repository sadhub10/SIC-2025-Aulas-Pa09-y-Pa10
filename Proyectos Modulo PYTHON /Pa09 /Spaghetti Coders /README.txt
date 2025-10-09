SISTEMA DE ANÁLISIS Y VISUALIZACIÓN DE DATOS FINANCIEROS DE COMPAÑÍAS
Equipo: Spaghetti Coders

PLANTEAMIENTO
El proyecto surge ante la dificultad que enfrentan muchas personas al interpretar los datos financieros de las empresas antes de invertir. Aunque los reportes 10-K y balances generales ofrecen información valiosa, suelen presentarse en formatos técnicos y poco accesibles.

El Sistema de Análisis y Visualización de Datos Financieros de Compañías busca simplificar este proceso mediante un programa que analiza datos financieros reales (2009–2023) y los presenta de forma visual, clara e intuitiva. Con esto, se ayuda al usuario a evaluar el desempeño económico de distintas compañías y a tomar decisiones de inversión más seguras y fundamentadas.

OBJETIVOS
Objetivo general:
Desarrollar una herramienta interactiva que facilite el análisis financiero y apoye la toma de decisiones de inversión basadas en datos reales y métricas clave.

Objetivos específicos:
- Automatizar el cálculo e interpretación de indicadores como ROE, ROA, margen neto, ratio de deuda y liquidez corriente.
- Presentar los resultados mediante gráficos e indicadores visuales fáciles de comprender.
- Permitir la comparación entre empresas de manera rápida y efectiva.
- Promover la educación financiera entre usuarios sin experiencia técnica en análisis económico.


HERRAMIENTAS UTILIZADAS
Lenguaje: Python
Librerías principales:
- pandas: procesamiento y análisis de datos.
- matplotlib y seaborn: visualización gráfica de indicadores.
- Streamlit: creación de una interfaz web interactiva.

Fuente de datos:
Archivo CSV con estados financieros históricos de diversas compañías (2009–2023).


EXPLICACIÓN DEL RESULTADO DEL PROYECTO
El sistema desarrollado permite analizar y visualizar el rendimiento financiero de distintas empresas a partir de sus datos históricos. Una vez cargado el archivo CSV, el programa procesa la información y calcula automáticamente métricas clave como el margen bruto, margen neto, ROE, ROA, ratio de deuda y liquidez corriente.

Los resultados se presentan mediante tablas y gráficos interactivos dentro de una interfaz construida con Streamlit, lo que facilita su interpretación. Además, el sistema clasifica cada indicador con etiquetas como “Excelente”, “Bueno” o “Bajo”, ayudando al usuario a comprender de manera rápida el desempeño de cada compañía.

Este enfoque permite que incluso usuarios sin experiencia en finanzas puedan interpretar la situación económica de una empresa y tomar decisiones de inversión informadas basadas en datos reales.


INSTRUCCIONES DE EJECUCIÓN
Para ejecutar el programa, es necesario tener instalada Python 3 junto con las siguientes librerías:
- streamlit
- pandas
- numpy
- matplotlib
- seaborn

Si alguna de estas librerías no está instalada, puede hacerlo desde la terminal (CMD) ejecutando el siguiente comando:

pip install streamlit pandas numpy matplotlib seaborn

Una vez completada la instalación, navegue hasta la carpeta donde se encuentra el proyecto y ejecute el siguiente comando para iniciar la aplicación:

streamlit run app_analisis_financiero.py

Esto abrirá automáticamente la interfaz del sistema en el navegador predeterminado, donde podrá visualizar y analizar los datos financieros.

En caso de que desee detener la ejecución del programa, presione Ctrl + C en la terminal (CMD).

