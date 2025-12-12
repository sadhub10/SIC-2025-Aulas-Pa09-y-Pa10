# Análisis Inteligente de Documentos Multimodal (Gemini 2.5 Flash)

Este sistema es una solución de vanguardia para el análisis de documentos e imágenes. Utiliza el modelo **Gemini 2.5 Flash** de Google para procesar PDFs y fotos, extrayendo información con precisión humana, identificando objetos visuales (Modo Lens) y permitiendo búsquedas semánticas con razonamiento profundo.

## 🚀 Características Principales

*   **Análisis Multimodal**: Sube **PDFs** (nativos o escaneados) o **Imágenes** (JPG, PNG, WEBP). El sistema lee todo.
*   **Visual Search (Modo Lens)**: Si subes la foto de un coche, producto o lugar, el sistema usa **Google Search Grounding** para identificar la Marca, Modelo y Año exacto.
*   **Búsqueda Semántica con Razonamiento**: No busca solo por palabras clave.
    *   *Ejemplo*: Si buscas "documentos de deuda", el sistema lee el contenido real y te explica: *"💡 Análisis: Este documento es relevante porque contiene una tabla de amortización..."*.
    *   **Full Context**: Lee el documento completo (50k+ caracteres), no solo resúmenes, para encontrar detalles ocultos.
*   **Prevención de Duplicados**: Sistema inteligente que bloquea la subida de archivos ya existentes para mantener limpia tu base de datos.
*   **Clasificación Dinámica**: No usa categorías fijas. El modelo determina profesionalmente de qué trata el documento (ej: "Factura Electrónica", "Contrato de Arrendamiento").

## 📂 Estructura del Proyecto

```
/
├── backend/                # El "Cerebro" del sistema
│   ├── main.py             # API Principal (FastAPI)
│   ├── gemini_service.py   # Integración Gemini (Vision + Search)
│   ├── vector_store.py     # Base de datos vectorial (FAISS)
│   ├── embeddings.py       # Generador de Embeddings Locales
│   └── requirements.txt    # Todas las dependencias (Backend + Frontend)
│
├── frontend/               # La "Interfaz"
│   └── app.py              # Aplicación Web (Streamlit)
│
├── data/                   # Almacenamiento
│   ├── uploads/            # PDFs/Imágenes subidos y sus .txt extraídos
│   └── faiss_index.bin     # Índice de búsqueda rápida
└── README.md
```

## 🛠️ Instalación y Configuración
> **¡Importante!** Sigue estos pasos para aislar el proyecto y que todo funcione perfecto.

### 1️⃣ Crear el Entorno Virtual (La "Burbuja")
Esto crea una carpeta `.venv` donde vivirán las librerías del proyecto.

```bash
# En la carpeta raíz del proyecto:
python -m venv .venv
```

### 2️⃣ Activar el Entorno
Dependiendo de qué terminal uses, el comando varía:

*   **PowerShell (Windows / VS Code por defecto):**
    ```powershell
    .\.venv\Scripts\activate
    ```
*   **Git Bash / Linux / Mac:**
    ```bash
    source .venv/Scripts/activate
    ```
*(Sabrás que funcionó porque verás `(.venv)` en verde al inicio de tu línea de comandos).*

### 3️⃣ Instalar Dependencias
Una vez activado el entorno, instala todo lo necesario de una sola vez:
```bash
pip install -r backend/requirements.txt
```

### 4️⃣ Configurar la Clave Secreta (API Key)
Este proyecto necesita una llave de Google Gemini para funcionar.
1.  **Obtén tu API KEY gratis aquí:** [Google AI Studio](https://aistudio.google.com/app/apikey)
2.  Copia el archivo de ejemplo:
    *   Renombra `.env.example` a `.env` (o crea uno nuevo llamado `.env`).
3.  Edítalo y pega tu clave real:
    ```env
    GEMINI_API_KEY=Tu_Clave_Secreta_Aqui
    ```
*(El archivo `.env` es ignorado por Git para proteger tu seguridad).*

---

## ⚡ Guía de Ejecución

Debes abrir **DOS terminales** (y activar el entorno `.venv` en AMBAS).

### Terminal 1: Iniciar el Backend (Cerebro)
```bash
python backend/main.py
```
*Espera a ver: `Application startup complete`.*

### Terminal 2: Iniciar el Frontend (Interfaz)
```bash
streamlit run frontend/app.py
```
*Tu navegador se abrirá automáticamente en `http://localhost:8501`.*

## 🔍 Cómo Usar

1.  **Cargar**: Arrastra un PDF o una Foto al recuadro de carga.
    *   *Si es duplicado, el sistema te avisará inmediatamente.*
2.  **Analizar**: Haz clic en el botón azul.
    *   Verás la clasificación, el resumen y el texto extraído.
    *   Si es una imagen de un objeto, verás su identificación precisa.
3.  **Buscar**: Ve a la barra lateral izquierda "Búsqueda Semántica".
    *   Escribe algo complejo como *"¿Qué coche aparece en las fotos?"* o *"contratos mayores a 1000 pesos"*.
    *   El sistema leerá los documentos y te dará una respuesta razonada.

---
**Tecnologías**: Python, FastAPI, Streamlit, Google Gemini 2.5 Flash, FAISS, Sentence-Transformers.
