
# 🚀 OptiMax - Sistema de Extracción de Datos

**OptiMax** es un sistema modular de extracción de datos que utiliza tecnologías de OCR (Reconocimiento Óptico de Caracteres) y reconocimiento de voz para extraer información estructurada de múltiples fuentes: imágenes, documentos PDF y audio.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Requisitos del Sistema](#-requisitos-del-sistema)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Funcionamiento Detallado](#-funcionamiento-detallado)
- [Configuración](#-configuración)
- [Ejemplos](#-ejemplos)
- [Solución de Problemas](#-solución-de-problemas)

---

## ✨ Características

- 🖼️ **Extracción desde imágenes**: Procesa imágenes (PNG, JPG, JPEG, BMP) usando EasyOCR
- 📄 **Extracción desde PDFs**: Convierte PDFs a imágenes y extrae texto con Tesseract OCR
- 🎤 **Extracción desde audio**: Transcribe audio en tiempo real usando Vosk (modelo en español)
- 🔍 **Búsqueda inteligente**: Identifica automáticamente palabras clave y valores asociados
- 💾 **Almacenamiento persistente**: Guarda todos los datos extraídos en formato JSON
- 🎨 **Interfaz gráfica moderna**: UI desarrollada con PyQt5, diseño azul profesional
- 🔄 **Procesamiento modular**: Arquitectura fácil de expandir para nuevas fuentes de datos
- 🌐 **Soporte multilenguaje**: Configurado para español, expandible a otros idiomas

---

## 🛠️ Tecnologías Utilizadas

### OCR (Reconocimiento Óptico de Caracteres)

#### **EasyOCR** 
- Framework de deep learning para reconocimiento de texto
- Soporta más de 80 idiomas
- Detecta y extrae texto de imágenes con alta precisión
- Ideal para imágenes con texto en diferentes orientaciones y calidades

#### **Tesseract OCR** 
- Motor OCR de código abierto desarrollado por Google
- Altamente preciso para documentos escaneados
- Funciona en conjunto con `pytesseract` (wrapper de Python)
- Requiere instalación del motor Tesseract en el sistema

#### **pdf2image**
- Convierte páginas de PDF en imágenes PIL
- Permite procesar PDFs con Tesseract OCR
- Requiere la biblioteca Poppler instalada en el sistema

### Reconocimiento de Voz

#### **Vosk**
- Sistema de reconocimiento de voz offline
- No requiere conexión a internet
- Modelos ligeros y rápidos
- Soporta español con el modelo `vosk-model-small-es-0.42`
- Procesa audio en tiempo real con PyAudio

### Interfaz Gráfica

#### **PyQt5**
- Framework multiplataforma para interfaces gráficas
- Widgets modernos y personalizables
- Sistema de señales y slots para manejo de eventos
- Soporte para threading (procesamiento en segundo plano)

---

## 💻 Requisitos del Sistema

### Sistema Operativo
- ✅ El proyecto fue realizado en Arch Linux (Wayland/X11)

### Python
- Python 3.8 o superior

### Dependencias del Sistema

#### **Arch Linux**
```bash
sudo pacman -S tesseract tesseract-data-spa poppler python-pyqt5 portaudio
```

---

## 📦 Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/optimax.git
cd optimax
```

### 2. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias de Python
```bash
pip3 install -r requirements.txt
```

**requirements.txt**:
```txt
PyQt5>=5.15.0
easyocr>=1.7.0
pytesseract>=0.3.10
pdf2image>=1.16.3
vosk>=0.3.45
pyaudio>=0.2.13
```

### 4. Descargar Modelo de Vosk
El modelo de reconocimiento de voz debe descargarse manualmente:

```bash
# Crear directorio para el modelo
mkdir -p tools/audio

# Descargar modelo en español (pequeño - ~40MB)
cd tools/audio
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip

# Descomprimir
unzip vosk-model-small-es-0.42.zip
rm vosk-model-small-es-0.42.zip

# Volver al directorio raíz
cd ../..
```

**Modelos disponibles**:
- `vosk-model-small-es-0.42`: Ligero, rápido (~40MB)
- `vosk-model-es-0.42`: Completo, más preciso (~1.5GB)

---

## 🚀 Uso

### Iniciar la Aplicación
```bash
python3 app.py
```

### Interfaz de Usuario

#### **Panel Lateral Izquierdo**
- 🖼️ **Imagen**: Extracción de texto desde imágenes
- 📄 **Documento**: Extracción de texto desde PDFs
- 🎤 **Audio**: Transcripción de audio en tiempo real
- 📊 **Datos Guardados**: Visualización de extracciones previas

#### **Flujo de Trabajo**

##### 1️⃣ **Extracción desde Imagen**
1. Clic en "Imagen" en el panel lateral
2. Clic en "Cargar Imagen"
3. Seleccionar imagen (PNG, JPG, JPEG, BMP)
4. Clic en "Procesar y Guardar"
5. Los datos extraídos se muestran en pantalla y se guardan en `data.json`

##### 2️⃣ **Extracción desde Documento**
1. Clic en "Documento" en el panel lateral
2. Clic en "Cargar Documento PDF"
3. Seleccionar archivo PDF
4. Clic en "Procesar y Guardar"
5. El sistema convierte cada página a imagen y extrae el texto

##### 3️⃣ **Extracción desde Audio**
1. Clic en "Audio" en el panel lateral
2. Clic en "Iniciar Grabación"
3. Hablar claramente al micrófono
4. Clic en "Detener Grabación" cuando termine
5. Clic en "Procesar y Guardar"
6. El audio se transcribe y se extraen los valores

##### 4️⃣ **Visualizar Datos**
1. Clic en "Datos Guardados"
2. Ver todas las extracciones previas en formato JSON
3. Usar "Actualizar Datos" para recargar
4. Usar "Limpiar Datos" para eliminar todo

---

## 📁 Estructura del Proyecto

```
optimax/
│
├── app.py                          # Aplicación principal PyQt5
├── data.json                       # Datos extraídos (generado automáticamente)
├── requirements.txt                # Dependencias de Python
├── README.md                       # Este archivo
│
├── config/
│   └── keywords.py                 # Palabras clave configurables
│
├── interface/
│   ├── img_interface.py           # Interfaz para imágenes
│   ├── doc_interface.py           # Interfaz para documentos
│   ├── audio_interface.py         # Interfaz para audio
│   └── data_interface.py          # Interfaz para visualización
│
└── tools/
    ├── data_extraction.py         # Lógica de extracción de valores
    │
    ├── imgocr/
    │   └── img_extraction.py      # Extracción con EasyOCR
    │
    ├── dococr/
    │   └── doc_extraction.py      # Extracción con Tesseract
    │
    └── audio/
        └── vosk-model-small-es-0.42/ # Modelo de Vosk
```

---

## 🔧 Funcionamiento Detallado

### 🎯 Extracción de Palabras Clave

El módulo `tools/data_extraction.py` implementa un algoritmo robusto de búsqueda:

#### **Proceso**:
1. **Normalización**: Todos los tokens se convierten a minúsculas
2. **Búsqueda fuzzy**: Detecta coincidencias parciales de palabras clave
3. **Look-ahead**: Busca valores numéricos en los siguientes 6 tokens
4. **Validación**: Usa regex para validar números (enteros y decimales)
5. **Last-wins**: Si hay múltiples valores para la misma clave, se guarda el último

#### **Ejemplo**:
```python
Entrada: ["subtotal:", "150.50", "impuesto:", "15.05", "total:", "165.55"]
Salida: {
    "subtotal": 150.50,
    "impuesto": 15.05,
    "total": 165.55
}
```

### 🖼️ Procesamiento de Imágenes (EasyOCR)

**Flujo**:
```
Imagen → EasyOCR → Lista de textos → Split en tokens → Minúsculas → Extracción
```

**Características**:
- Detecta texto en múltiples idiomas (español e inglés configurados)
- Maneja texto en diferentes orientaciones
- Alta precisión con imágenes de calidad media-alta

### 📄 Procesamiento de PDFs (Tesseract)

**Flujo**:
```
PDF → pdf2image (300 DPI) → Imagen por página → Tesseract OCR → Tokens → Extracción
```

**Características**:
- Convierte cada página a imagen de alta resolución (300 DPI)
- Procesa página por página
- Ideal para documentos escaneados y facturas

### 🎤 Procesamiento de Audio (Vosk)

**Flujo**:
```
Micrófono → PyAudio → Chunks de audio → Vosk → Transcripción → Conversión → Extracción
```

**Características**:
- Reconocimiento en tiempo real
- Offline (no requiere internet)
- Convierte números hablados a dígitos ("ciento cincuenta" → "150")
- Usa gramática personalizada para mejorar precisión

**Gramática de números**:
```python
"cero" → "0"
"uno" → "1"
"dos" → "2"
...
"nueve" → "9"
"punto" → "."
"coma" → "."
```

---

## ⚙️ Configuración

### Palabras Clave Personalizadas

Editar `config/keywords.py`:

```python
keywords_list = [
    'subtotal',
    'sub',
    'impuesto',
    'tax',
    'itbms',
    'total',
    'venta',
    'previous',
    'current'
]
```

### Ajustar Ventana de Búsqueda

En `tools/data_extraction.py`:

```python
def extract_key_values(
    char_list: List[str],
    keywords: List[str],
    look_ahead: int = 6  # Cambiar este valor
)
```

- `look_ahead=3`: Búsqueda más restrictiva
- `look_ahead=10`: Búsqueda más amplia

### Cambiar Modelo de Vosk

Para mayor precisión, usar el modelo completo:

```bash
cd tools/audio
wget https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip
unzip vosk-model-es-0.42.zip
```

Actualizar en `tools/audio/audio_extraction.py`:
```python
MODEL_PATH = "tools/audio/vosk-model-es-0.42"
```

---

## 💡 Ejemplos

### Ejemplo 1: Factura Escaneada

**Entrada** (imagen de factura):
```
FACTURA #12345
Subtotal: $150.50
ITBMS (7%): $10.54
Total: $161.04
```

**Salida** (`data.json`):
```json
{
  "extracciones": [
    {
      "fuente": "imagen",
      "fecha": "2025-12-08T15:30:00",
      "datos": {
        "subtotal": 150.50,
        "itbms": 10.54,
        "total": 161.04
      }
    }
  ]
}
```

### Ejemplo 2: Audio de Ticket

**Entrada** (audio):
```
"Subtotal: ciento cincuenta punto cinco cero.
Impuesto: diez punto cinco cuatro.
Total: ciento sesenta y uno punto cero cuatro."
```

**Proceso**:
```
Vosk transcribe → "subtotal 150.50 impuesto 10.54 total 161.04"
```

**Salida**:
```json
{
  "subtotal": 150.50,
  "impuesto": 10.54,
  "total": 161.04
}
```

---

## 🐛 Solución de Problemas

### ❌ Error: "Tesseract no encontrado"

**Solución**:
```bash
# Linux
sudo pacman -S tesseract

# Verificar instalación
tesseract --version
```

### ❌ Error: "Poppler no instalado"

**Solución**:
```bash
# Arch Linux
sudo pacman -S poppler
```

### ❌ Error: "Modelo Vosk no encontrado"

**Solución**:
Descargar manualmente:
```bash
cd tools/audio
wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip
```

### ❌ Diálogos de archivo no responden (Wayland)

**Solución**:
Forzar XWayland en `app.py`:
```python
os.environ['QT_QPA_PLATFORM'] = 'xcb'
```

### ❌ PyAudio no se instala

**Solución**:
```bash
# Arch Linux
sudo pacman -S portaudio
pip3 install pyaudio
```

### ❌ EasyOCR no detecta texto

**Verificar**:
- Calidad de la imagen (mínimo 300 DPI)
- Contraste del texto
- Idioma configurado correctamente

**Ajustar**:
```python
reader = easyocr.Reader(['es', 'en'], gpu=False)  # Cambiar idiomas
```

---

## 🔮 Próximas Características

- [ ] Soporte para Excel (XLSX)
- [ ] Exportación a CSV
- [ ] API REST para integración
- [ ] Procesamiento batch de múltiples archivos
- [ ] Detección automática de idioma
- [ ] Historial de búsquedas
- [ ] Validación de datos extraídos
- [ ] Integración con bases de datos

---

## 🙏 Agradecimientos

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - Framework OCR
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - Motor OCR
- [Vosk](https://alphacephei.com/vosk/) - Reconocimiento de voz offline
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) - Framework GUI

---
