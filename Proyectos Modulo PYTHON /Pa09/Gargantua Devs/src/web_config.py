# src/web_config.py
import streamlit as st

# Diccionario reutilizable para configuración de página
PAGE_CONFIG = {
    "page_title": "Panama Safe - Análisis de Delitos",
    "page_icon": "PA",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://www.streamlit.io',
        'Report a bug': None,
        'About': """
        # Panama Safe
        Sistema de análisis geográfico e inteligente de delitos en Panamá.

        Versión: 2.0  
        **Desarrollado por: layomx, epsilon, olvr, coke**
        """
    }
}

# Función para aplicar estilos visuales
def apply_custom_styles():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.8rem;
            font-weight: bold;
            color: #FF4B4B;
            text-align: center;
            margin-bottom: 0;
        }
        .sub-header {
            text-align: center;
            color: #666;
            font-size: 1.1rem;
            margin-top: 0;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-container {
            padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
