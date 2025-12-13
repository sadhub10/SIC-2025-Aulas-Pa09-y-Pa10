# 🎓 Sistema de Predicción de Deserción Escolar

Sistema web basado en Streamlit para predecir el riesgo de deserción escolar utilizando Machine Learning.

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
# Si tienes el proyecto en Git
git clone <url-del-repositorio>
cd desercion-escolar

# O simplemente crea una carpeta y coloca los archivos
mkdir desercion-escolar
cd desercion-escolar
```

### 2. Crear entorno virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

Deberías ver `(venv)` al inicio de tu línea de comandos.

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📦 Estructura del Proyecto

```
desercion-escolar/
│
├── venv/                          # Entorno virtual (no subir a Git)
├── app.py                         # Aplicación principal de Streamlit
├── mi_modelo_final.cbm            # Modelo de CatBoost entrenado
├── requirements.txt               # Dependencias del proyecto
├── README.md                      # Este archivo
│
└── data/                          # (Opcional) Carpeta para datos de ejemplo
    └── ejemplo_estudiantes.csv
```

## 📄 Archivo requirements.txt

Crea un archivo llamado `requirements.txt` con el siguiente contenido:

```txt
streamlit==1.31.0
pandas==2.1.4
numpy==1.24.3
scikit-learn==1.3.2
plotly==5.18.0
catboost==1.2.2
```

## ▶️ Ejecutar la Aplicación

Una vez instaladas las dependencias, ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📊 Uso de la Aplicación

### Paso 1: Preparar tu archivo CSV

Tu archivo CSV debe contener al menos las siguientes columnas (pueden tener nombres diferentes):

- `edad`: Edad del estudiante (8-18 años)
- `genero`: M o F
- `zona_residencia`: Urbana o Rural
- `nivel`: Primaria, Premedia o Media
- `grado`: 1-12
- `tipo_escuela`: Oficial o Particular
- `veces_repitio_grado`: 0-5
- `sobre_edad`: 0-5
- `promedio_actual`: 1.0-5.0
- `promedio_anterior`: 1.0-5.0
- `materias_reprobadas`: 0-10
- `porcentaje_asistencia`: 0-100
- `tercil_socioeconomico`: 1, 2 o 3
- `nivel_educacion_padres`: Primaria_Incompleta, Primaria_Completa, Secundaria_Incompleta, Secundaria_Completa, Universidad
- `trabaja_estudiante`: 0 o 1

**Ejemplo de CSV:**

entrada_esperada.csv
entrada_no_esperada.csv

### Paso 2: Cargar el archivo

1. Haz clic en "Selecciona tu archivo CSV"
2. Elige tu archivo
3. Verifica la vista previa de los datos

### Paso 3: Mapear columnas

- Asigna cada columna de tu archivo a la columna correspondiente del modelo
- El sistema validará que todas las columnas estén mapeadas

### Paso 4: Ejecutar predicción

- Haz clic en "🚀 Ejecutar Predicción"
- Espera a que se procesen los datos
- Visualiza los resultados y descarga el informe

## 🔧 Configuración del Modelo

### Usar tu modelo entrenado

1. Asegúrate de tener tu archivo `mi_modelo_final.cbm` en la carpeta del proyecto

2. En el archivo `app.py`, localiza la sección de predicción y descomenta:

```python
# Importar CatBoost
import catboost as cb

# En la función de predicción, reemplaza la simulación con:
model = cb.CatBoostClassifier()
model.load_model("mi_modelo_final.cbm")
probabilidades = model.predict_proba(data_to_predict)[:, 1]
predicciones = np.where(probabilidades >= 0.5, 1, 0)
```

3. Elimina o comenta las líneas de predicción simulada

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
# Asegúrate de que el entorno virtual esté activado
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: "Command 'streamlit' not found"

```bash
# El entorno virtual no está activado
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Error al cargar el modelo CatBoost

```bash
# Verifica que el archivo existe
ls mi_modelo_final.cbm

# Verifica la versión de CatBoost
pip show catboost
```

### Puerto 8501 ya en uso

```bash
# Usa un puerto diferente
streamlit run app.py --server.port 8502
```

## 📈 Interpretación de Resultados

- **Riesgo Bajo (0-0.3)**: Probabilidad baja de deserción, seguimiento estándar
- **Riesgo Medio (0.3-0.6)**: Requiere atención preventiva
- **Riesgo Alto (0.6-1.0)**: Requiere intervención inmediata

### Factores de Riesgo Principales

El modelo considera:
- **Rendimiento académico** (16-22%): Promedios, materias reprobadas, repetición
- **Asistencia** (12%): Porcentaje de asistencia
- **Factores socioeconómicos** (14-45%): Tercil, educación padres, trabajo estudiantil

## 🔒 Desactivar el Entorno Virtual

Cuando termines de trabajar:

```bash
deactivate
```




---

**Versión:** 1.0.0  
**Última actualización:** Diciembre 2025
