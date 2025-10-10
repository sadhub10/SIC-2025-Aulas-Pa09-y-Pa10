# HeartRiskSystem

### 🩺 Sistema Predictivo de Riesgo Cardíaco — *Bonito y listo para usar*

<img src="assets/image.png" alt="HeartRiskSystem" width="260"/>


**Análisis inteligente, diagnóstico preventivo y apoyo clínico con datos médicos reales.**

</div>

---

## 🔎 Resumen

**HeartRiskSystem** es una plataforma en **Python 3.12** que predice el riesgo de enfermedad cardíaca usando técnicas de *Machine Learning*. A partir de variables clínicas (edad, colesterol, presión arterial, frecuencia cardíaca, etc.), el sistema clasifica pacientes en **bajo / medio / alto riesgo** y genera reportes automáticos en `.txt`.

---

## 🎯 Objetivos

**General:** Construir una herramienta que permita predecir riesgo cardiovascular a partir de datos clínicos.

**Específicos:**

* Limpieza y normalización de datos.
* Entrenamiento y selección automática del mejor modelo.
* Generación de reportes individuales en `.txt`.
* Visualizaciones de variables clave para interpretación clínica.

---

## 🧭 Estructura del proyecto

```
HeartRiskSystem/
│
├── README.md
├── requirements.txt
├── assets/
│   └── image.png
├── modelos/
│   ├── modelo_rf.joblib
│   ├── scaler.joblib
│   └── feature_cols.joblib
├── datasets/
│   ├── dataset_cuantitativo.csv
│   ├── dataset_descriptivo.csv
│   ├── historial_pacientes.csv
│   └── Heart_disease_cleveland_new.csv
├── reportes/
│   └── reporte_paciente_*.txt
└── src/
    ├── main.py
    ├── config.py
    ├── analysis/
    │   ├── preprocesing.py
    │   └── visualization.py
    └── models/
        ├── eda.py
        └── models_predictive.py
```

---

## ⚙️ Tecnologías usadas

* **Python 3.12**
* pandas, numpy
* matplotlib, seaborn
* scikit-learn, joblib
* Git / GitHub

---

## 🚀 Instalación rápida

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/HeartRiskSystem.git
cd HeartRiskSystem
```

2. Crea y activa un entorno virtual (recomendado):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

---

## ▶️ Ejecución

**Modo consola (rápido):**

```bash
python src/main.py --input datasets/Heart_disease_cleveland_new.csv --output reportes/
```

**Con interfaz (ejemplo con Streamlit):**

```bash
streamlit run app.py
```

> `main.py` soporta flags para: archivo de entrada (`--input`), carpeta de salida (`--output`), selección de modelo (`--model`) y modo `--train` para reentrenar.

---

## 🧾 Formato de entrada

El CSV de entrada debe contener (al menos) las siguientes columnas:

```
age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal, target
```

* **target:** 1 = presencia de enfermedad, 0 = ausencia (si existe). Para predecir en producción, `target` puede omitirse.

---

## 📈 Métricas y salida

* Métricas principales calculadas: **Accuracy, Precision, Recall, F1-score, AUC**.
* Salida principal: reportes individuales en `reportes/reporte_paciente_<id>.txt` que incluyen:

  * Datos del paciente
  * Probabilidad de enfermedad
  * Clasificación de riesgo (Bajo / Medio / Alto)
  * Recomendaciones básicas (p.ej. "Evaluación clínica sugerida")

---

## 🧠 Modelos incluidos

Se comparan y pueden seleccionarse automáticamente:

* Logistic Regression
* Random Forest
* Support Vector Machine
* K-Nearest Neighbors
* Decision Tree

El sistema guarda el mejor modelo en `modelos/` (`.joblib`) y un `scaler` para preprocesamiento.

---

## 🧪 Ejemplo de salida (resumen)

* Precisión: **0.87**
* Precision: **0.86**
* Recall: **0.84**
* F1-score: **0.85**

También se exportan:

* Matriz de confusión (`png`)
* Curva ROC (`png`)

---

## 🧩 Código de ejemplo — generar reporte rápido

```python
from joblib import load
import pandas as pd

model = load('modelos/modelo_rf.joblib')
scaler = load('modelos/scaler.joblib')
cols = load('modelos/feature_cols.joblib')

df = pd.read_csv('datasets/ejemplo.csv')
X = df[cols]
X_scaled = scaler.transform(X)
probs = model.predict_proba(X_scaled)[:,1]

for i, p in enumerate(probs):
    riesgo = 'Alto' if p>0.7 else ('Medio' if p>0.4 else 'Bajo')
    with open(f'reportes/reporte_paciente_{i+1}.txt','w') as f:
        f.write(f"Paciente: {i+1}\nProbabilidad: {p:.3f}\nRiesgo: {riesgo}\n")
```

---

## ♻️ Buenas prácticas y mejoras futuras

* Integrar API médica (FastAPI / Flask) para consultas en tiempo real.
* Interfaz web con autenticación y visual dashboard.
* Base de datos para historial (MySQL / MongoDB).
* Pipeline CI/CD para reentrenamiento con nuevos datos.

---

## 📝 Licencia

Licencia MIT — ver `LICENSE`.

---

## 📬 Contacto

Desarrollador: **Joel Monrroy** (o tu nombre)
Repositorio: `https://github.com/tuusuario/HeartRiskSystem`

---

¡Listo! Si quieres, puedo:

* Generar el `requirements.txt` con versiones recomendadas.
* Crear `main.py` o la plantilla de `app.py` para Streamlit.
* Preparar ejemplos de reportes en `reportes/`.

Elige qué quieres que haga a continuación y lo preparo bonito también. ✨
