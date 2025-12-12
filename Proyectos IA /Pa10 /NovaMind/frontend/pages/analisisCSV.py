import streamlit as st
import pandas as pd
import sys
from pathlib import Path

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import analizarLoteCSV

def mostrarPaginaCSV():
    st.title("Anilisis Masivo desde CSV")
    st.markdown("Carga y analiza multiples comentarios desde un archivo CSV")

    st.info("El CSV debe contener las columnas: `comentario`, `departamento`, `equipo`, `fecha`")

    uploaded_file = st.file_uploader("Selecciona un archivo CSV", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            st.subheader("Vista previa del CSV")
            st.dataframe(df.head(10), use_container_width=True)

            st.write(f"Total de filas: {len(df)}")

            columnas_requeridas = ["comentario"]
            columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]

            if columnas_faltantes:
                st.error(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
                return

            if st.button("Procesar CSV completo", use_container_width=True):
                try:
                    datos = df.to_dict('records')

                    with st.spinner(f"Analizando {len(datos)} comentarios..."):
                        resultado = analizarLoteCSV(datos)

                    st.success(f"Procesamiento completado")
                    st.metric("Comentarios procesados", resultado.get("procesados", 0))
                    st.metric("Comentarios guardados", resultado.get("guardados", 0))

                    st.info("Los resultados han sido guardados en la base de datos. Consulta el Dashboard para visualizarlos.")

                except Exception as e:
                    st.error(f"Error procesando CSV: {str(e)}")
                    st.info("Asegúrate de que el backend está ejecutándose.")

        except Exception as e:
            st.error(f"Error leyendo CSV: {str(e)}")

    st.markdown("---")

    with st.expander("Formato de ejemplo del CSV"):
        ejemplo = pd.DataFrame({
            "comentario": [
                "Me siento muy agotado con la carga de trabajo actual",
                "El ambiente en el equipo es muy positivo",
                "Necesitamos mejores herramientas de comunicacion"
            ],
            "departamento": ["Operaciones", "Ventas", "IT"],
            "equipo": ["Turno A", "Equipo Norte", "Backend"],
            "fecha": ["2025-01-15", "2025-01-16", "2025-01-17"]
        })

        st.dataframe(ejemplo, use_container_width=True)
        st.download_button(
            "Descargar CSV de ejemplo",
            ejemplo.to_csv(index=False),
            "ejemplo_comentarios.csv",
            "text/csv"
        )
