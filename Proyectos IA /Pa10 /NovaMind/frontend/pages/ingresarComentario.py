import streamlit as st
from datetime import date
import sys
from pathlib import Path

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import analizarComentarioIndividual, obtenerDepartamentos, obtenerEquipos
from utils.formatHelper import formatearResultadoAnalisis

def mostrarPaginaIngreso():
    st.title("Ingresar Comentario Individual")
    st.markdown("Analiza un comentario en tiempo real con IA")

    with st.form("form_comentario"):
        comentario = st.text_area(
            "Comentario del empleado",
            height=150,
            placeholder="Escribe aqui el comentario del empleado...",
            max_chars=2000
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            try:
                departamentos = obtenerDepartamentos()
                departamentos.insert(0, "")
            except:
                departamentos = [""]

            departamento = st.selectbox("Departamento", departamentos)

        with col2:
            try:
                if departamento:
                    equipos = obtenerEquipos(departamento)
                    equipos.insert(0, "")
                else:
                    equipos = [""]
            except:
                equipos = [""]

            equipo = st.selectbox("Equipo", equipos)

        with col3:
            fecha = st.date_input("Fecha", value=date.today())

        submitted = st.form_submit_button("Analizar Comentario", use_container_width=True)

    if submitted:
        if not comentario.strip():
            st.error("El comentario no puede estar vacio")
            return

        with st.spinner("Analizando comentario con IA..."):
            try:
                meta = {
                    "departamento": departamento,
                    "equipo": equipo,
                    "fecha": str(fecha)
                }

                resultado = analizarComentarioIndividual(comentario, meta)

                st.success("Analisis completado")
                st.markdown("---")

                formatearResultadoAnalisis(resultado)

                with st.expander("Ver respuesta completa del backend"):
                    st.json(resultado)

            except Exception as e:
                st.error(f"Error al analizar: {str(e)}")
