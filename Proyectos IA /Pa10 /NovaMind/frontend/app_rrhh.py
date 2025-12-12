import streamlit as st
import sys
from pathlib import Path

frontend_path = Path(__file__).parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import verificarConexion, login

st.set_page_config(
    page_title="NovaMind - Panel RRHH",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

def mostrarLogin():
    st.title("NovaMind - Panel de Recursos Humanos")

    if not verificarConexion():
        st.error("No se puede conectar con el backend. Verifica que esté ejecutándose en http://127.0.0.1:8000")
        st.info("Ejecuta: `uvicorn backend.main:app --reload --port 8000`")
        return

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("### Iniciar Sesión")

        with st.form("form_login"):
            usuario = st.text_input("Usuario", placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingresa tu contraseña")
            submitted = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

        if submitted:
            if not usuario or not password:
                st.error("Por favor completa todos los campos")
                return

            try:
                resultado = login(usuario, password)

                if resultado.get("success"):
                    st.session_state.authenticated = True
                    st.session_state.usuario = resultado.get("usuario")
                    st.session_state.nombre_completo = resultado.get("nombre_completo")
                    st.success(f"Bienvenido, {resultado.get('nombre_completo')}")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

            except Exception as e:
                st.error("Error al iniciar sesión")
                st.write(f"Detalle: {str(e)}")

        st.markdown("---")
        st.caption("Credenciales por defecto:")
        st.code("Usuario: admin\nContraseña: admin123")

def mostrarPanelRRHH():
    st.sidebar.title(f" NovaMind")
    st.sidebar.markdown(f"**Usuario:** {st.session_state.get('nombre_completo', 'RRHH')}")
    st.sidebar.markdown("---")

    paginas = {
        "Dashboard": "dashboard",
        "Análisis Individual": "individual",
        "Análisis CSV": "csv",
        "Alertas": "alertas",
        "Configuración": "config"
    }

    seleccion = st.sidebar.radio("Navegación", list(paginas.keys()), index=0)

    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.usuario = None
        st.session_state.nombre_completo = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.caption("NovaMind v1.0")

    if seleccion == "Dashboard":
        import pages.analisisIndividual as dashboard
        dashboard.mostrarDashboard()
    elif seleccion == "Análisis Individual":
        import pages.analisisIndividual as individual
        individual.mostrarPaginaIndividual()
    elif seleccion == "Análisis CSV":
        import pages.analisisCSV as csv_page
        csv_page.mostrarPaginaCSV()
    elif seleccion == "Alertas":
        import pages.configuracion as alertas
        alertas.mostrarPaginaAlertas()
    elif seleccion == "Configuración":
        import pages.configuracion as config
        config.mostrarPaginaConfiguracion()

def main():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        mostrarPanelRRHH()
    else:
        mostrarLogin()

if __name__ == "__main__":
    main()
