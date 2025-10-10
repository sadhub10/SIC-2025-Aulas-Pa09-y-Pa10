import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    """Carga los datos del archivo CSV y los devuelve como un DataFrame de pandas."""
    try:
        crimenes = pd.read_csv("data/dataset_homicidios.csv") # Ruta del archivo CSV
        return crimenes
    except FileNotFoundError:
        st.error("Archivo CSV no encontrado. Por favor, verifica la ruta.")
        return None
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None