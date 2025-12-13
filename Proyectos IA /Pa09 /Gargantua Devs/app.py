import streamlit as st
import tensorflow as tf
import pandas as pd
import numpy as np
import pickle
import re
import PyPDF2
from PIL import Image
import pytesseract

# --- CONFIGURACIÓN PARA WINDOWS ---
# Apunta al ejecutable de Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Sistema de Clasificación Documental",
    page_icon="💰",
    layout="wide"
)

# --- 1. CARGA DE RECURSOS ---
@st.cache_resource
def load_resources():
    try:
        model = tf.keras.models.load_model('modelo_facturas.keras')
        with open('scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except Exception as e:
        st.error(f"Error crítico cargando recursos: {e}")
        return None, None

model, scaler = load_resources()

# --- 2. FUNCIONES DE PROCESAMIENTO ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error leyendo PDF: {e}")
        return ""

def extract_text_from_image(file):
    try:
        image = Image.open(file)
        # 'spa+eng' para leer español e inglés
        text = pytesseract.image_to_string(image, lang='spa+eng')
        return text
    except Exception as e:
        st.error(f"Error en OCR: {e}")
        return ""

def limpiar_precio_complejo(texto):
    if not isinstance(texto, str): return 0.0
    
    patron = r'(\d+[\.,]\d+)'
    encontrados = re.findall(patron, texto)
    
    if encontrados:
        precio_final = encontrados[-1]
        precio_final = precio_final.replace(',', '.')
        if precio_final.count('.') > 1:
            partes = precio_final.split('.')
            precio_final = "".join(partes[:-1]) + '.' + partes[-1]
        try:
            return float(precio_final)
        except ValueError:
            return 0.0
    return 0.0

# --- 3. INTERFAZ GRÁFICA ---

st.title("📂 Sistema Inteligente de Clasificación de Gastos")
st.markdown("Herramienta de clasificación automática de facturas mediante IA.")
st.write("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.info("📄 **Paso 1: Carga de Documento**")
    
    uploaded_file = st.file_uploader("Seleccione archivo (PDF, JPG, PNG)", type=['pdf', 'jpg', 'jpeg', 'png'])

    extracted_amount = 0.0
    
    if uploaded_file is not None:
        text_content = ""
        
        # Procesamiento silencioso
        if uploaded_file.type == "application/pdf":
            st.caption("🔹 Documento PDF cargado.")
            text_content = extract_text_from_pdf(uploaded_file)
        else:
            st.caption("🔹 Imagen cargada.")
            # CORRECCIÓN AQUÍ: Cambiamos use_column_width por use_container_width
            st.image(uploaded_file, caption="Vista previa", use_container_width=True)
            text_content = extract_text_from_image(uploaded_file)

        # Extracción interna del monto (sin mostrar al usuario)
        extracted_amount = limpiar_precio_complejo(text_content)
        
        # Expansor técnico solo para debug (oculto por defecto)
        with st.expander("Ver detalles técnicos (Debug)"):
            st.write(f"Monto detectado internamente: {extracted_amount}")
            st.text(text_content[:500] + "...")

with col2:
    st.info("🧠 **Paso 2: Análisis Predictivo**")
    
    predict_btn = st.button("Ejecutar Clasificación", type="primary", disabled=(uploaded_file is None))
    
    if predict_btn and model is not None and scaler is not None:
        with st.spinner('Analizando documento...'):
            
            input_data = np.array([[extracted_amount]])
            
            try:
                # Transformación y Predicción
                input_scaled = scaler.transform(input_data)
                prediction = model.predict(input_scaled)
                
                class_idx = np.argmax(prediction)
                confidence = np.max(prediction) * 100
                
                labels = {
                    0: "🟢 Gasto BAJO",
                    1: "🟡 Gasto MEDIO",
                    2: "🔴 Gasto ALTO"
                }
                
                resultado_texto = labels.get(class_idx, "Indeterminado")
                
                # Mostrar resultado
                st.markdown(f"### Clasificación: {resultado_texto}")
                st.progress(int(confidence))
                
                if class_idx == 2:
                    st.warning("Este documento ha sido marcado como Gasto Alto.")
                
            except Exception as e:
                st.error(f"Error en el análisis: {e}")

st.write("---")