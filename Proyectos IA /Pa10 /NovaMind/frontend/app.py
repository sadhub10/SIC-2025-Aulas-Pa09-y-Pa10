import streamlit as st
import sys
from pathlib import Path

frontend_path = Path(__file__).parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import verificarConexion

st.set_page_config(
    page_title="NovaMind - Analisis de Bienestar Laboral",
    page_icon=">",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.sidebar.title("> NovaMind")
    st.sidebar.markdown("---")

    if not verificarConexion():
        st.sidebar.error("Backend no disponible")
        st.error("No se puede conectar con el backend. Verifica que esta ejecutandose en http://127.0.0.1:8000")
        st.info("Ejecuta: `uvicorn backend.main:app --reload --port 8000`")
        return

    st.sidebar.success("Backend conectado")

    paginas = {
        "Dashboard": "dashboard",
        "Ingresar Comentario": "ingreso",
        "Analisis CSV": "csv",
        "Analisis Individual": "individual",
        "Alertas": "alertas",
        "Configuracion": "config"
    }

    seleccion = st.sidebar.radio("Navegacion", list(paginas.keys()), index=0)

    st.sidebar.markdown("---")
    st.sidebar.caption("NovaMind v1.0")

    if seleccion == "Dashboard":
        import pages.analisisIndividual as dashboard
        dashboard.mostrarDashboard()
    elif seleccion == "Ingresar Comentario":
        import pages.ingresarComentario as ingreso
        ingreso.mostrarPaginaIngreso()
    elif seleccion == "Analisis CSV":
        import pages.analisisCSV as csv_page
        csv_page.mostrarPaginaCSV()
    elif seleccion == "Analisis Individual":
        import pages.analisisIndividual as individual
        individual.mostrarPaginaIndividual()
    elif seleccion == "Alertas":
        import pages.configuracion as alertas
        alertas.mostrarPaginaAlertas()
    elif seleccion == "Configuracion":
        import pages.configuracion as config
        config.mostrarPaginaConfiguracion()

if __name__ == "__main__":
    main()
