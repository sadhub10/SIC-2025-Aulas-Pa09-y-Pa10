import streamlit as st
from typing import Dict, Any, List

def formatearResultadoAnalisis(resultado: Dict[str, Any]) -> None:
    if "resultado" in resultado:
        data = resultado["resultado"]
    else:
        data = resultado

    emocion = data.get("emotion", {})
    estres = data.get("stress", {})
    categorias = data.get("categories", [])
    resumen = data.get("summary", "")
    sugerencia = data.get("suggestion", "")

    emo_label = emocion.get("label", "desconocida")
    emo_score = emocion.get("score", 0.0)
    stress_level = estres.get("level", "desconocido")
    sent_dist = estres.get("sentiment_dist", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Emoción", emo_label.capitalize(), f"{emo_score:.2%}")

    with col2:
        color = obtenerColorStress(stress_level)
        st.markdown(f"**Nivel de Estrés:** :{color}[{stress_level.upper()}]")

    with col3:
        pos = sent_dist.get("positive", 0.0)
        neu = sent_dist.get("neutral", 0.0)
        neg = sent_dist.get("negative", 0.0)
        st.write(f"Sentiment: Pos:{pos:.2f} Neu:{neu:.2f} Neg:{neg:.2f}")

    if categorias:
        st.subheader("Categorías Detectadas")
        for cat in categorias[:3]:
            label = cat.get("label", "")
            score = cat.get("score", 0.0)
            st.write(f"- **{label}**: {score:.2%}")

    if resumen:
        st.subheader("Resumen")
        st.info(resumen)

    if sugerencia:
        st.subheader("Sugerencia para RRHH")
        st.success(sugerencia)


def obtenerColorStress(nivel: str) -> str:
    mapping = {
        "alto": "red",
        "medio": "orange",
        "bajo": "green"
    }
    return mapping.get(nivel.lower(), "gray")


def obtenerColorEmocion(emocion: str) -> str:
    mapping = {
        "joy": "green",
        "happiness": "green",
        "neutral": "gray",
        "sadness": "blue",
        "anger": "red",
        "fear": "orange",
        "surprise": "violet"
    }
    return mapping.get(emocion.lower(), "gray")


def formatearKPI(titulo: str, valor: Any, delta: Any = None, icono: str = "") -> None:
    if icono:
        st.metric(f"{icono} {titulo}", valor, delta)
    else:
        st.metric(titulo, valor, delta)


def mostrarTablaComentarios(comentarios: List[Dict[str, Any]], limite: int = 10) -> None:
    import pandas as pd

    if not comentarios:
        st.warning("No hay comentarios disponibles")
        return

    datos = []
    for c in comentarios[:limite]:
        datos.append({
            "ID": c.get("id", ""),
            "Comentario": c.get("comentario", ""),  # 👈 SIN CORTAR
            "Estrés": c.get("stress_level", ""),
            "Emoción": c.get("emotion_label", ""),
            "Departamento": c.get("departamento", ""),
            "Fecha": c.get("fecha", "")
        })

    df = pd.DataFrame(datos)
    st.dataframe(df, use_container_width=True, hide_index=True)



def crearGraficoBarras(titulo: str, etiquetas: List[str], valores: List[float], color: str = None):
    import plotly.graph_objects as go

    fig = go.Figure(data=[
        go.Bar(x=etiquetas, y=valores, marker_color=color or "steelblue")
    ])

    fig.update_layout(
        title=titulo,
        xaxis_title="",
        yaxis_title="Cantidad",
        height=400,
        template="plotly_white"
    )

    return fig


def crearGraficoPie(titulo: str, etiquetas: List[str], valores: List[float]):
    import plotly.graph_objects as go

    fig = go.Figure(data=[
        go.Pie(labels=etiquetas, values=valores, hole=0.3)
    ])

    fig.update_layout(
        title=titulo,
        height=400,
        template="plotly_white"
    )

    return fig


def crearGraficoLinea(titulo: str, x: List[str], y: List[float], nombre: str = ""):
    import plotly.graph_objects as go

    fig = go.Figure(data=[
        go.Scatter(x=x, y=y, mode='lines+markers', name=nombre)
    ])

    fig.update_layout(
        title=titulo,
        xaxis_title="Fecha",
        yaxis_title="Cantidad",
        height=400,
        template="plotly_white"
    )

    return fig


def crearGraficoMultilinea(titulo: str, datos: Dict[str, Dict[str, List]]):
    import plotly.graph_objects as go

    fig = go.Figure()

    for nombre, values in datos.items():
        fig.add_trace(go.Scatter(
            x=values["x"],
            y=values["y"],
            mode='lines+markers',
            name=nombre
        ))

    fig.update_layout(
        title=titulo,
        xaxis_title="Fecha",
        yaxis_title="Cantidad",
        height=400,
        template="plotly_white"
    )

    return fig


def mostrarAlerta(tipo: str, mensaje: str, severidad: str = "info") -> None:
    if severidad == "alta":
        st.error(mensaje)
    elif severidad == "media":
        st.warning(mensaje)
    else:
        st.info(mensaje)
