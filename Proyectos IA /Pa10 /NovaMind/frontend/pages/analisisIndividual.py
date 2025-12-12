import streamlit as st
import pandas as pd
import sys
from pathlib import Path

frontend_path = Path(__file__).parent.parent
if str(frontend_path) not in sys.path:
    sys.path.insert(0, str(frontend_path))

from utils.callBackend import (
    obtenerHistoricos, obtenerEstadisticas, obtenerEstadisticasDepartamentos,
    obtenerTendencias, obtenerTextoComentarios, obtenerDepartamentos
)
from utils.formatHelper import (
    crearGraficoBarras, crearGraficoPie, crearGraficoLinea,
    mostrarTablaComentarios, crearGraficoMultilinea
)
from utils.worldCloudUtils import mostrarWordCloud

def mostrarDashboard():
    st.title("Dashboard - Anilisis de Bienestar Laboral")

    try:
        stats = obtenerEstadisticas()
    except Exception as e:
        st.error(f"Error obteniendo estadisticas: {str(e)}")
        return

    total = stats.get("total", 0)

    if total == 0:
        st.warning("No hay datos disponibles. Ingresa comentarios para comenzar el analisis.")
        return

    st.subheader("KPIs Generales")
    col1, col2, col3, col4 = st.columns(4)

    stress = stats.get("stress", {})
    stress_alto = stress.get("alto", 0)
    stress_alto_pct = (stress_alto / total * 100) if total > 0 else 0

    with col1:
        st.metric("Total Comentarios", total)

    with col2:
        st.metric("Estres Alto", f"{stress_alto_pct:.1f}%", delta=f"{stress_alto} comentarios")

    with col3:
        sent = stats.get("sentimiento_promedio", {})
        positivo_pct = sent.get("positivo", 0) * 100
        st.metric("Sentiment Positivo", f"{positivo_pct:.1f}%")

    with col4:
        categorias = stats.get("categorias_principales", [])
        top_cat = categorias[0]["categoria"] if categorias else "N/A"
        st.metric("Categoría Principal", top_cat[:20])

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Distribucion de Estres")
        stress_labels = ["Alto", "Medio", "Bajo"]
        stress_values = [
            stress.get("alto", 0),
            stress.get("medio", 0),
            stress.get("bajo", 0)
        ]

        if sum(stress_values) > 0:
            fig = crearGraficoPie("Niveles de Estres", stress_labels, stress_values)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de estres")

    with col_right:
        st.subheader("Emociones Detectadas")
        emociones = stats.get("emociones", {})

        if emociones:
            emo_labels = list(emociones.keys())
            emo_values = list(emociones.values())

            fig = crearGraficoBarras("Distribucion de Emociones", emo_labels, emo_values, color="lightblue")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de emociones")

    st.markdown("---")

    st.subheader("Top Categorias")
    if categorias:
        cat_labels = [c["categoria"] for c in categorias]
        cat_values = [c["count"] for c in categorias]

        fig = crearGraficoBarras("Categorias Mas Frecuentes", cat_labels, cat_values, color="steelblue")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de categorias")

    st.markdown("---")

    st.subheader("Analisis por Departamentos")

    try:
        dept_stats = obtenerEstadisticasDepartamentos()

        if dept_stats:
            dept_names = list(dept_stats.keys())
            dept_totals = [dept_stats[d]["total"] for d in dept_names]
            dept_stress_alto = [dept_stats[d]["stress_alto"] for d in dept_names]

            col_dept1, col_dept2 = st.columns(2)

            with col_dept1:
                fig = crearGraficoBarras("Comentarios por Departamento", dept_names, dept_totals, color="teal")
                st.plotly_chart(fig, use_container_width=True)

            with col_dept2:
                fig = crearGraficoBarras("Estres Alto por Departamento", dept_names, dept_stress_alto, color="crimson")
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("Ver comparacion detallada"):
                df_dept = pd.DataFrame({
                    "Departamento": dept_names,
                    "Total": dept_totals,
                    "Estres Alto": dept_stress_alto,
                    "Estres Medio": [dept_stats[d]["stress_medio"] for d in dept_names],
                    "Estres Bajo": [dept_stats[d]["stress_bajo"] for d in dept_names]
                })
                st.dataframe(df_dept, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos de departamentos")

    except Exception as e:
        st.error(f"Error obteniendo datos de departamentos: {str(e)}")

    st.markdown("---")

    st.subheader("Tendencias Temporales")

    try:
        tendencias = obtenerTendencias(dias=30)

        if tendencias:
            fechas = sorted(tendencias.keys())
            total_por_fecha = [tendencias[f]["total"] for f in fechas]
            stress_alto_por_fecha = [tendencias[f]["stress_alto"] for f in fechas]

            datos_multilinea = {
                "Total Comentarios": {"x": fechas, "y": total_por_fecha},
                "Estres Alto": {"x": fechas, "y": stress_alto_por_fecha}
            }

            fig = crearGraficoMultilinea("Tendencias en el Tiempo", datos_multilinea)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de tendencias")

    except Exception as e:
        st.error(f"Error obteniendo tendencias: {str(e)}")

    st.markdown("---")

    st.subheader("WordCloud de Comentarios")

    try:
        textos = obtenerTextoComentarios(limit=500)

        if textos:
            mostrarWordCloud(textos, titulo="Palabras Mas Frecuentes en Comentarios")
        else:
            st.info("No hay comentarios para generar WordCloud")

    except Exception as e:
        st.error(f"Error generando WordCloud: {str(e)}")

    st.markdown("---")

    st.subheader("Comentarios Recientes")

    try:
        comentarios = obtenerHistoricos(limit=20)

        if comentarios:
            mostrarTablaComentarios(comentarios, limite=20)
        else:
            st.info("No hay comentarios recientes")

    except Exception as e:
        st.error(f"Error obteniendo comentarios: {str(e)}")

def mostrarPaginaIndividual():
    st.title("Analisis Individual")
    st.markdown("Explora comentarios individuales con filtros avanzados")

    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        try:
            departamentos = obtenerDepartamentos()
            departamentos.insert(0, "Todos")
            dept_seleccionado = st.selectbox("Departamento", departamentos)
        except:
            dept_seleccionado = "Todos"

    with col_filter2:
        stress_seleccionado = st.selectbox("Nivel de Estres", ["Todos", "alto", "medio", "bajo"])

    with col_filter3:
        limite = st.number_input("Limite de resultados", min_value=10, max_value=500, value=50, step=10)

    if st.button("Aplicar Filtros"):
        try:
            filtros = {}
            if dept_seleccionado != "Todos":
                filtros["departamento"] = dept_seleccionado
            if stress_seleccionado != "Todos":
                filtros["stress_level"] = stress_seleccionado

            filtros["limit"] = limite

            comentarios = obtenerHistoricos(**filtros)

            if comentarios:
                st.success(f"Se encontraron {len(comentarios)} comentarios")
                mostrarTablaComentarios(comentarios, limite=limite)

                with st.expander("Ver detalles completos"):
                    for c in comentarios[:10]:
                        st.markdown(f"**ID {c['id']}** - {c['departamento']} - {c['fecha']}")
                        st.write(f"Comentario: {c['comentario']}")
                        st.write(f"Estres: {c['stress_level']} | Emocion: {c['emotion_label']}")
                        st.write(f"Resumen: {c['summary']}")
                        st.write(f"Sugerencia: {c['suggestion']}")
                        st.markdown("---")
            else:
                st.warning("No se encontraron comentarios con esos filtros")

        except Exception as e:
            st.error(f"Error aplicando filtros: {str(e)}")
