import streamlit as st
import sys
from pathlib import Path

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import (
    obtenerPatrones, obtenerAlertas, obtenerDepartamentos,
    obtenerAlertasDepartamento
)
from utils.formatHelper import mostrarAlerta, mostrarTablaComentarios

def mostrarPaginaAlertas():
    st.title("Sistema de Alertas Automaticas")
    st.markdown("Deteccion de patrones criticos y tendencias en comentarios")

    st.subheader("Deteccion de Patrones")

    try:
        patrones = obtenerPatrones()

        total = patrones.get("total_comentarios", 0)
        stress_pct = patrones.get("stress_alto_porcentaje", 0)

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total de Comentarios Analizados", total)

        with col2:
            st.metric("Porcentaje de Estres Alto", f"{stress_pct:.1f}%")

        st.markdown("---")

        patrones_detectados = patrones.get("patrones_detectados", [])

        if patrones_detectados:
            st.subheader(f"Patrones Detectados ({len(patrones_detectados)})")

            for patron in patrones_detectados:
                tipo = patron.get("tipo", "")
                severidad = patron.get("severidad", "baja")
                mensaje = patron.get("mensaje", "")
                accion = patron.get("accion", "")

                with st.container():
                    mostrarAlerta(tipo, mensaje, severidad)
                    st.markdown(f"**Accion recomendada:** {accion}")
                    st.markdown("---")
        else:
            st.info("No se detectaron patrones creticos")

    except Exception as e:
        st.error(f"Error obteniendo patrones: {str(e)}")

    st.markdown("---")

    st.subheader("Alertas por Nivel de Estres")

    col_alert1, col_alert2 = st.columns([1, 3])

    with col_alert1:
        nivel_stress = st.selectbox("Nivel", ["alto", "medio", "bajo"])
        limite_alertas = st.number_input("Limite", min_value=5, max_value=100, value=20, step=5)

    if st.button("Buscar Alertas"):
        try:
            alertas = obtenerAlertas(nivel=nivel_stress, limite=limite_alertas)

            if alertas:
                st.success(f"Se encontraron {len(alertas)} comentarios con estres {nivel_stress}")
                mostrarTablaComentarios(alertas, limite=limite_alertas)

                with st.expander("Ver detalles completos"):
                    for alerta in alertas[:10]:
                        st.markdown(f"**ID {alerta['id']}** - {alerta['departamento']} - {alerta['fecha']}")
                        st.write(f"Comentario: {alerta['comentario']}")
                        st.write(f"Resumen: {alerta['summary']}")
                        st.write(f"Sugerencia: {alerta['suggestion']}")
                        st.markdown("---")
            else:
                st.warning(f"No hay comentarios con estres {nivel_stress}")

        except Exception as e:
            st.error(f"Error obteniendo alertas: {str(e)}")

    st.markdown("---")

    st.subheader("Analisis por Departamento")

    try:
        departamentos = obtenerDepartamentos()

        if departamentos:
            dept_seleccionado = st.selectbox("Selecciona un departamento", departamentos)

            if st.button("Analizar Departamento"):
                try:
                    dept_data = obtenerAlertasDepartamento(dept_seleccionado)

                    if "mensaje" in dept_data:
                        st.warning(dept_data["mensaje"])
                    else:
                        st.subheader(f"Analisis de {dept_seleccionado}")

                        col_dept1, col_dept2, col_dept3, col_dept4 = st.columns(4)

                        with col_dept1:
                            st.metric("Total", dept_data.get("total", 0))

                        stress_info = dept_data.get("stress", {})

                        with col_dept2:
                            st.metric("Estres Alto", stress_info.get("alto", 0))

                        with col_dept3:
                            st.metric("Estres Medio", stress_info.get("medio", 0))

                        with col_dept4:
                            st.metric("Estres Bajo", stress_info.get("bajo", 0))

                        st.markdown("---")

                        st.subheader("Top Categorias")
                        top_cats = dept_data.get("top_categorias", [])
                        if top_cats:
                            for cat in top_cats:
                                st.write(f"- **{cat['categoria']}**: {cat['count']} comentarios")
                        else:
                            st.info("No hay categorias disponibles")

                        st.markdown("---")

                        st.subheader("Alertas de Estres Alto")
                        alertas_dept = dept_data.get("alertas", [])
                        if alertas_dept:
                            mostrarTablaComentarios(alertas_dept, limite=10)
                        else:
                            st.success("No hay alertas de estres alto en este departamento")

                except Exception as e:
                    st.error(f"Error analizando departamento: {str(e)}")
        else:
            st.info("No hay departamentos disponibles")

    except Exception as e:
        st.error(f"Error obteniendo departamentos: {str(e)}")

def mostrarPaginaConfiguracion():
    st.title("Configuracion del Sistema")
    st.markdown("Ajustes y parametros del sistema NovaMind")

    st.subheader("Configuracion de Backend")

    backend_url = st.text_input("URL del Backend", value="http://127.0.0.1:8000")

    if st.button("Verificar Conexion"):
        import requests
        try:
            response = requests.get(backend_url, timeout=5)
            if response.status_code == 200:
                st.success("Conexion exitosa con el backend")
                st.json(response.json())
            else:
                st.error(f"Error de conexion: {response.status_code}")
        except Exception as e:
            st.error(f"No se pudo conectar: {str(e)}")

    st.markdown("---")

    st.subheader("Parametros de Analisis")

    st.info("Los parametros de los modelos de IA se configuran en el backend.")

    with st.expander("Modelos de IA Utilizados"):
        st.markdown("""
        **Modelos Transformer:**
        - Sentiment: cardiffnlp/twitter-roberta-base-sentiment-latest
        - Emotion: j-hartmann/emotion-english-distilroberta-base
        - Zero-shot: facebook/bart-large-mnli
        - Summarizer: sshleifer/distilbart-cnn-12-6
        """)

    st.markdown("---")

    st.subheader("Categorias de Analisis")

    categorias = [
        "sobrecarga laboral", "liderazgo", "comunicacion", "reconocimiento",
        "remuneracion", "equilibrio vida-trabajo", "ambiente laboral",
        "procesos", "tecnologia/herramientas", "conflictos internos",
        "recursos insuficientes", "formacion/capacitacion", "satisfaccion general", "motivacion"
    ]

    st.write("Categorias disponibles:")
    for i, cat in enumerate(categorias, 1):
        st.write(f"{i}. {cat}")

    st.markdown("---")

    st.subheader("Informacion del Sistema")

    st.info("NovaMind v1.0 - Sistema de Analisis de Bienestar Laboral con IA")

    with st.expander("Acerca de"):
        st.markdown("""
        NovaMind es un sistema completo para analizar comentarios de empleados utilizando
        Inteligencia Artificial y Procesamiento de Lenguaje Natural.

        **Caracteristicas:**
        - Analisis de emocion y estres
        - Categorizacion automatica
        - Generacion de resumenes
        - Sugerencias para RRHH
        - Dashboard con KPIs
        - Sistema de alertas automaticas
        """)
