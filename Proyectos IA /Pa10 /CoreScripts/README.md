# 🎓 Sistema de Predicción de Deserción Escolar

Sistema web basado en **Streamlit** para predecir el **riesgo de deserción escolar** utilizando **Machine Learning**, orientado a apoyar la toma de decisiones en contextos educativos mediante el análisis de variables académicas y socioeconómicas.

---

## 📌 Resumen

El **Sistema de Predicción de Deserción Escolar** permite cargar datos de estudiantes en formato CSV, procesarlos y generar predicciones sobre el riesgo de abandono escolar.  
El sistema utiliza un modelo entrenado con **CatBoost**, integrando visualizaciones y validaciones automáticas para facilitar su uso por docentes, investigadores y personal administrativo.

---

## 🎯 Objetivo

- Predecir el nivel de riesgo de deserción escolar en estudiantes.
- Identificar factores clave asociados al abandono escolar.
- Facilitar la intervención temprana mediante alertas de riesgo.
- Proveer una herramienta accesible, visual e intuitiva basada en web.

---

## 🧠 Tecnología Usada

- **Python 3.8+**
- **Streamlit** – Interfaz web interactiva
- **Pandas** – Manipulación y análisis de datos
- **NumPy** – Cálculo numérico
- **Scikit-learn** – Procesamiento y utilidades de Machine Learning
- **CatBoost** – Modelo de clasificación
- **Plotly** – Visualización de resultados
- **Git / GitHub** – Control de versiones

---

## 📋 Requisitos Previos

- Python **3.8 o superior**
- pip (gestor de paquetes de Python)

---

## 🚀 Instalación

### 1️⃣ Clonar o descargar el proyecto

```bash
# Si tienes el proyecto en Git
git clone <url-del-repositorio>
cd desercion-escolar
O bien:

bash
Copiar código
# Crear carpeta manualmente
mkdir desercion-escolar
cd desercion-escolar
2️⃣ Crear entorno virtual
En Windows:

bash
Copiar código
python -m venv venv
venv\Scripts\activate
En Linux / Mac:

bash
Copiar código
python3 -m venv venv
source venv/bin/activate
Deberías ver (venv) al inicio de tu línea de comandos.

3️⃣ Instalar dependencias
bash
Copiar código
pip install --upgrade pip
pip install -r requirements.txt
📦 Estructura del Proyecto
text
Copiar código
desercion-escolar/
│
├── venv/                          # Entorno virtual (no subir a Git)
├── app.py                         # Aplicación principal de Streamlit
├── mi_modelo_final.cbm            # Modelo de CatBoost entrenado
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Este archivo
│
└── data/                          # (Opcional) Datos de ejemplo
    └── ejemplo_estudiantes.csv
📄 Archivo requirements.txt
Crea un archivo llamado requirements.txt con el siguiente contenido:

txt
Copiar código
streamlit==1.31.0
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
plotly==5.18.0
catboost==1.2.2
▶️ Ejecutar la Aplicación
bash
Copiar código
streamlit run app.py
La aplicación se abrirá automáticamente en tu navegador en:
👉 http://localhost:8501

📊 Uso de la Aplicación
🥇 Paso 1: Preparar tu archivo CSV
Tu archivo CSV debe contener al menos las siguientes columnas (los nombres pueden variar):

Columna	Descripción
edad	Edad del estudiante (8–18 años)
genero	M o F
zona_residencia	Urbana o Rural
nivel	Primaria, Premedia o Media
grado	1–12
tipo_escuela	Oficial o Particular
veces_repitio_grado	0–5
sobre_edad	0–5
promedio_actual	1.0–5.0
promedio_anterior	1.0–5.0
materias_reprobadas	0–10
porcentaje_asistencia	0–100
tercil_socioeconomico	1, 2 o 3
nivel_educacion_padres	Primaria_Incompleta, Primaria_Completa, Secundaria_Incompleta, Secundaria_Completa, Universidad
trabaja_estudiante	0 o 1

Ejemplos:

entrada_esperada.csv

entrada_no_esperada.csv

🥈 Paso 2: Cargar el archivo
Haz clic en "Selecciona tu archivo CSV"

Elige tu archivo

Verifica la vista previa de los datos

🥉 Paso 3: Mapear columnas
Asigna cada columna de tu archivo a la columna esperada por el modelo

El sistema validará automáticamente que todas estén mapeadas

🚀 Paso 4: Ejecutar predicción
Haz clic en "🚀 Ejecutar Predicción"

Espera el procesamiento

Visualiza resultados y descarga el informe

🔧 Configuración del Modelo
Usar tu modelo entrenado
Asegúrate de que el archivo mi_modelo_final.cbm esté en la carpeta raíz del proyecto.

En app.py, localiza la sección de predicción y descomenta:

python
Copiar código
# Importar CatBoost
import catboost as cb

model = cb.CatBoostClassifier()
model.load_model("mi_modelo_final.cbm")

probabilidades = model.predict_proba(data_to_predict)[:, 1]
predicciones = np.where(probabilidades >= 0.5, 1, 0)
❗ Elimina o comenta cualquier simulación de predicción previa.

🐛 Solución de Problemas
❌ Error: ModuleNotFoundError
bash
Copiar código
pip install -r requirements.txt
❌ Error: Command 'streamlit' not found
Windows

bash
Copiar código
venv\Scripts\activate
Linux / Mac

bash
Copiar código
source venv/bin/activate
❌ Error al cargar el modelo CatBoost
bash
Copiar código
ls mi_modelo_final.cbm
pip show catboost
❌ Puerto 8501 ya en uso
bash
Copiar código
streamlit run app.py --server.port 8502
📈 Interpretación de Resultados
Nivel de Riesgo	Probabilidad	Acción
🟢 Bajo	0.0 – 0.3	Seguimiento estándar
🟡 Medio	0.3 – 0.6	Atención preventiva
🔴 Alto	0.6 – 1.0	Intervención inmediata

🔍 Factores de Riesgo Principales
El modelo considera principalmente:

Rendimiento académico (16–22%)

Promedios

Materias reprobadas

Repetición de grado

Asistencia (12%)

Porcentaje de asistencia

Factores socioeconómicos (14–45%)

Tercil socioeconómico

Educación de los padres

Trabajo estudiantil

🔒 Desactivar el Entorno Virtual
bash
Copiar código
deactivate
🧾 Información del Proyecto
Versión: 1.0.0

Última actualización: Diciembre 2025
