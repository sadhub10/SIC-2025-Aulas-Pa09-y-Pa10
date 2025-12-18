# 📡 Clasificador de Modulaciones Digitales 

**Sistema Inteligente de Clasificación de Modulaciones Digitales mediante CNN**

## Descripción General

El **Clasificador de Modulaciones Digitales** es un sistema de inteligencia artificial diseñado para **identificar y clasificar automáticamente tipos de modulación digital** (ASK, PSK, QAM) a partir de imágenes de señales. Utiliza una Red Neuronal Convolucional (CNN) inspirada en ResNet para lograr una precisión del 82% en la clasificación de 16 tipos diferentes de modulación.

Este proyecto está orientado a aplicaciones en:
- Análisis de espectro radioeléctrico
- Seguridad en comunicaciones
- Investigación en telecomunicaciones
- Monitoreo de señales RF

 ## Características Principales

- **Clasificación de imagenes** de diferentes tipos de modulaciones
- **Interfaz web intuitiva** desarrollada con Streamlit
- **Arquitectura ResNet** para señales RF
- **Estimación de nivel SNR** basada en confianza del modelo
- **Visualización de probabilidades** por tipo de modulación
  
### Modulaciones Soportadas

| Familia | Órdenes (M) |
|---------|-------------|
| **ASK** | 2, 4, 8, 16, 32, 64 |
| **PSK** | 2, 4, 8, 16, 32, 64 |
| **QAM** | 4, 8, 16, 64 |

---
## Arquitectura del Sistema

### Modelo CNN

```
Input (96x96x1)
    ↓
Conv2D + BatchNorm + ReLU (32 filtros)
    ↓
BasicBlock Residual (64 filtros) → MaxPool
    ↓
BasicBlock Residual (128 filtros) → MaxPool
    ↓
BasicBlock Residual (256 filtros) → MaxPool
    ↓
Flatten → FC(512) → Dropout(0.5) → FC(16)
    ↓
Softmax → Predicción
```

### Métricas del Modelo

- **Accuracy Global**: 82%
- **Épocas de Entrenamiento**: 8
- **Tamaño de Entrada**: 96×96 píxeles (escala de grises)
- **Clases**: 16 (ASK, PSK, QAM con órdenes M variados)

  
```
Proyecto-IA-PyBrAIn-2025-SIC/
│
├── 📂 src/                              # Código fuente principal
│   └── app.py                           # Aplicación web Streamlit
│
├── 📂 notebook/                         # Notebooks de entrenamiento
│   ├── modelo_senalesIA.pth             # Modelo CNN entrenado (ResNet)
│   ├── signal_generator.ipynb           # Generador de señales
│   ├── signal_generator_original.ipynb  # Versión original del generador
│   └── train_modulation_cnn.ipynb       # Entrenamiento del modelo
│
├── 📂 assets/                           # Recursos visuales y estilos
│   ├── logo.png                         # Logo PyBrAIn
│   ├── styles.css                       # Estilos personalizados CSS        
│
├── 📂 data/                             # Señales de ejemplo
│   ├── ask_sample.png                   # Muestra de modulación ASK
│   ├── psk_sample.png                   # Muestra de modulación PSK
│   └── qam_sample.png                   # Muestra de modulación QAM
│
├── 📄 requirements.txt                  # Dependencias Python
├── 📄 README.md                         # Documentación del proyecto
└── 📄 .gitignore                        # Archivos ignorados por Git

## 🚀 Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/digital-modulation-classifier.git
cd digital-modulation-classifier
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

**Activar el entorno:**
- Windows: `.venv\Scripts\activate`
- Linux/Mac: `source .venv/bin/activate`

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

---

## 📦 Dependencias Principales

```txt
streamlit>=1.28.0
torch>=2.0.0
torchvision>=0.15.0
Pillow>=10.0.0
plotly>=5.17.0
```

---

##  Uso de la Aplicación

### Paso 1: Cargar Imagen
Sube una imagen de señal (waveform, constelación o espectro) en formato PNG/JPG.

### Paso 2: Analizar
Presiona el botón **"ANALIZAR SEÑAL"** para clasificar la modulación.

### Paso 3: Resultados
El sistema mostrará:
- ✅ Tipo de modulación detectada (ej: PSK_16)
- ✅ Nivel de confianza (%)
- ✅ Estimación de SNR (Alto/Medio/Bajo)
- ✅ Distribución de probabilidades (Top 5)

---





---
