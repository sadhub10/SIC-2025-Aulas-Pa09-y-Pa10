import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import json
# Asegúrate de que utils/helpers.py exista y contenga append_record y ensure_records_file
from utils.helpers import append_record, ensure_records_file 
from pathlib import Path
import altair as alt # Usamos Altair para los gráficos
import os 
from google import genai
from dotenv import load_dotenv # Para cargar la clave API desde .env

# ===============================
# CONFIGURACIÓN INICIAL Y DE SEGURIDAD
# ===============================
# Carga las variables del archivo .env al inicio
load_dotenv() 

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best-classify.pt"
CATEGORIES_JSON = BASE_DIR / "data" / "categories.json"
RECORDS_CSV = BASE_DIR / "data" / "records.csv"

# Asegura que el archivo de registros exista
ensure_records_file(RECORDS_CSV)

# ===============================
# CONFIGURACIÓN DE GEMINI
# ===============================
client = None
try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
    else:
        st.warning("⚠️ Variable GEMINI_API_KEY no encontrada. El Análisis Avanzado de Gemini estará deshabilitado. Crea un archivo .env.")
except Exception as e:
    st.error(f"Error al inicializar Gemini: {e}")

# ===============================
# CARGA DE MODELO Y DATOS
# ===============================
@st.cache_resource
def load_model(path):
    """Carga el modelo YOLO de manera eficiente."""
    return YOLO(str(path))

model = load_model(MODEL_PATH)

st.set_page_config(page_title='Clasificador de Desechos', layout='wide')
st.title('Clasificación de Desechos del Hogar')

# Cargar la metadata de categorías
with open(CATEGORIES_JSON, "r", encoding="utf-8") as f:
    categories = json.load(f)

names = categories.get("names", [])

# Cargar los registros para que Gemini los use en el análisis
df = pd.read_csv(RECORDS_CSV)


# ===============================
# FUNCIONES DE SOPORTE PARA GEMINI
# ===============================
def get_data_summary(df, categories_json_data):
    """
    Genera un resumen de los datos relevantes para inyectar en el prompt de Gemini.
    """
    if df.empty:
        csv_summary = "Aún no hay registros de clasificación."
    else:
        # Frecuencia de clasificación de las 5 categorías más comunes
        top_classes = df["class"].value_counts().head(5)
        csv_summary = "Historial de clasificaciones (Top 5):\n"
        csv_summary += top_classes.to_string()
        
    # Información de todas las categorías del JSON
    categories_info = "Información de las categorías de desecho (JSON):\n"
    for name in categories_json_data.get("names", []):
        info = categories_json_data["info"].get(name, {})
        categories_info += f"- **{name}**: Descripción: {info.get('description', 'N/A')}. Reciclable: {info.get('recyclable', 'N/A')}\n"
    
    return f"{csv_summary}\n\n{categories_info}"

# Generar el resumen de los datos que se enviará a Gemini
data_summary = get_data_summary(df, categories) 


# ===============================
# FUNCIÓN CENTRAL DE INFERENCIA Y ANÁLISIS
# ===============================
def run_inference_and_gemini_analysis(img, source_type, file_name):
    """Ejecuta YOLO, guarda el registro y llama a Gemini para el análisis."""
    
    # 1. Ejecutar Inferencia (YOLO)
    results = model(np.array(img))[0]
    cls_id = int(results.probs.top1)
    conf = float(results.probs.top1conf)
    class_name = model.names[cls_id]

    st.subheader(f"Predicción: {class_name} ({conf*100:.2f}%)")

    # 2. Guardar registro
    append_record(
        RECORDS_CSV,
        source_type,
        file_name,
        class_name,
        conf
    )
    
    # 3. Análisis Avanzado con Gemini
    st.markdown("---")
    
    if client:
        st.subheader("Análisis Avanzado y Predicciones")
        
        # --- PREPARACIÓN DEL PROMPT ---
        tarea = (
            f"Analiza la clasificación obtenida ('{class_name}') con el 'Historial de clasificaciones' "
            f"y la 'Información de las categorías' proporcionada a continuación.\n\n"
            f"Responde con 3 puntos clave, utilizando un formato Markdown claro (ej: viñetas o números):\n"
            f"1. **Probabilidad Histórica**: ¿Qué tan común es este desecho ('{class_name}') según el historial?.\n"
            f"2. **Estimación de Peso**: Basándote en la descripción de la categoría (en el JSON) y en un peso promedio razonable para el tipo de desecho, **estima un peso probable en gramos (g)** para el ítem clasificado. (Solo la estimación, ejemplo: '150g').\n"
            f"3. **Sugerencia Experta**: Da un consejo de reciclaje no trivial basado en si es reciclable o no (según el JSON) y su impacto ambiental."
        )
        
        prompt_completo = f"CONTEXTO DE DATOS:\n{data_summary}\n\nTAREA:\n{tarea}"
        
        try:
            with st.spinner('Generando análisis avanzado con Gemini...'):
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt_completo
                )
            st.success(response.text)
        except Exception as e:
            st.warning(f"No se pudo generar el análisis avanzado. Error: {e}")
    else:
        st.info("El análisis avanzado con Gemini está deshabilitado (clave API no configurada).")


# ===============================
# SECCIONES DE INTERFAZ DE USUARIO
# ===============================
st.header("Clasificación mediante carga de imagen")
col1, col2 = st.columns([1,1])

with col1:
    uploaded = st.file_uploader(
        "Sube una imagen de un desecho",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded is not None:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, caption="Imagen cargada", use_column_width=True)
        
        run_inference_and_gemini_analysis(
            img, 
            "upload", 
            getattr(uploaded, "name", "uploaded_image")
        )


with col2:
    st.header("Clasificación mediante webcam")
    camera_image = st.camera_input("Toma una fotografía")

    if camera_image is not None:
        img = Image.open(camera_image).convert("RGB")
        st.image(img, caption="Imagen capturada", use_column_width=True)

        run_inference_and_gemini_analysis(
            img, 
            "webcam", 
            "webcam_capture"
        )


# ===============================
# HISTORIAL Y ESTADÍSTICAS
# ===============================
st.markdown("---")
st.header("Historial y estadísticas de clasificación")

# Recargar df para incluir el registro actual después de la inferencia
df = pd.read_csv(RECORDS_CSV) 

st.subheader("Registros recientes")
st.dataframe(df.tail(50), use_container_width=True)

st.subheader("Cantidad total por categoría")

if not df.empty:
    counts = df["class"].value_counts().reset_index()
    counts.columns = ["class", "count"]

    # Generación de gráfico de barras con Altair
    chart = (
        alt.Chart(counts)
        .mark_bar(
            cornerRadiusTopLeft=6,
            cornerRadiusTopRight=6,
            opacity=0.85
        )
        .encode(
            x=alt.X("class:N", title="Categoría", sort="-y"),
            y=alt.Y("count:Q", title="Cantidad"),
            color=alt.Color(
                "class:N",
                scale=alt.Scale(scheme="set2"),
                legend=None
            ),
            tooltip=[
                alt.Tooltip("class:N", title="Categoría"),
                alt.Tooltip("count:Q", title="Cantidad")
            ]
        )
        .properties(width="container", height=400, title="")
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Aún no hay registros suficientes para generar la gráfica.")


# ===============================
# INFORMACIÓN DE CATEGORÍAS
# ===============================
st.markdown("---")
st.header("Información sobre las categorías de desechos")

for nm in names:
    info = categories["info"].get(nm, {})

    with st.expander(f"Información sobre {nm}"):
        st.write("**Descripción:**", info.get("description", "N/A"))
        st.write("**Cómo desecharlo:**", info.get("handling", "N/A"))
        st.write("**¿Es reciclable?:**", info.get("recyclable", "N/A"))

st.markdown("---")
st.write("Archivo de registros:", str(RECORDS_CSV))