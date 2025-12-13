# 📂 Sistema Inteligente de Clasificación de Gastos

Este proyecto es una aplicación web construida con **Streamlit** que utiliza Inteligencia Artificial para automatizar la contabilidad de gastos.

**Funcionalidades:**
1.  **Lectura de Documentos:** Extrae texto de PDFs y realiza OCR (Reconocimiento Óptico de Caracteres) en imágenes (JPG, PNG).
2.  **Extracción de Datos:** Localiza automáticamente el monto total de la factura usando expresiones regulares (Regex).
3.  **Clasificación AI:** Utiliza una Red Neuronal (TensorFlow/Keras) para clasificar el gasto en Bajo, Medio o Alto.

---

## 🛠️ Requisitos del Sistema (Pre-instalación)

Antes de ejecutar el código Python, necesitas instalar el motor de OCR en tu computadora:

### 1. Instalar Tesseract OCR (Obligatorio)
El código necesita un software externo para leer imágenes.

* **Windows:**
    1.  Descarga el instalador aquí: [Tesseract at UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) (baja la versión `w64-setup`).
    2.  Durante la instalación, asegúrate de instalar los idiomas **English** y **Spanish**.
    3.  **IMPORTANTE:** Instálalo en la ruta por defecto: `C:\Program Files\Tesseract-OCR`.
    *Nota: Si lo instalas en otra ruta, deberás modificar la línea 13 del archivo `app.py`.*

---

## 🚀 Instalación del Proyecto

### 1. Clonar o descargar el repositorio
Descarga los archivos en una carpeta local.

### 2. Archivos necesarios
Asegúrate de que los siguientes archivos estén en la carpeta principal:
* `app.py` (El código principal).
* `modelo_facturas.keras` (Tu modelo entrenado).
* `scaler.pkl` (Tu escalador numérico).

### 3. Instalar librerías de Python
Abre tu terminal (Símbolo del sistema o PowerShell), navega hasta la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt