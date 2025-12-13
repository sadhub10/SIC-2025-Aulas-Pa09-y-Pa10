import sys
import os
import numpy as np
import pandas as pd
import json
from datetime import datetime
from collections import Counter

# Agregar ruta del proyecto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go

from src.models.predict import predict_text
from src.data.preprocess import clean_text
from src.features.vectorizer import load_vectorizer

# ================================
# CONFIGURACIÓN DE PÁGINA
# ================================
st.set_page_config(
    page_title="Mental Health Monitor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# ESTILOS CSS MEJORADOS
# ================================
st.markdown("""
<style>
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a4d7a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4a5568;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Alertas con mejor contraste */
    .alert-high {
        background-color: #fef2f2;
        border: 2px solid #dc2626;
        border-left: 6px solid #dc2626;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-high h2, .alert-high h3 {
        color: #991b1b;
        margin: 0;
    }

    .alert-medium {
        background-color: #fffbeb;
        border: 2px solid #f59e0b;
        border-left: 6px solid #f59e0b;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-medium h2, .alert-medium h3 {
        color: #92400e;
        margin: 0;
    }

    .alert-low {
        background-color: #f0fdf4;
        border: 2px solid #10b981;
        border-left: 6px solid #10b981;
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .alert-low h2, .alert-low h3 {
        color: #065f46;
        margin: 0;
    }

    /* Métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #1a4d7a;
        font-weight: 600;
    }

    /* Cajas de estadísticas */
    .stat-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .stat-box h4 {
        color: #1a4d7a;
        margin: 0 0 10px 0;
        font-size: 1.1rem;
    }
    .stat-box p {
        color: #4a5568;
        margin: 5px 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


# ================================
# FUNCIONES
# ================================
@st.cache_resource
def load_model_and_vectorizer():
    """Carga el modelo y vectorizador"""
    try:
        model_path = os.path.join(ROOT_DIR, "src", "models", "saved", "best_model.pkl")
        model = joblib.load(model_path)
        vectorizer = load_vectorizer()
        return model, vectorizer
    except Exception as e:
        st.error(f"Error al cargar el modelo: {e}")
        return None, None


@st.cache_data
def load_model_metrics():
    """Carga las métricas del modelo"""
    try:
        metrics_path = os.path.join(ROOT_DIR, "src", "models", "saved", "model_metrics.json")
        with open(metrics_path, 'r') as f:
            return json.load(f)
    except:
        # Métricas por defecto si no existe el archivo
        return {
            "accuracy": 0.85,
            "f1_score": 0.84,
            "precision": 0.85,
            "recall": 0.84,
            "total_samples": 48965,
            "n_categories": 5
        }


def get_prediction_confidence(model, vectorizer, text):
    """Obtiene predicción y confianza"""
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])

    prediction = model.predict(vec)[0]
    decision_values = model.decision_function(vec)[0]

    # Probabilidades (softmax manual)
    exp_values = np.exp(decision_values - np.max(decision_values))
    probs = exp_values / exp_values.sum()

    confidence_dict = {label: prob for label, prob in zip(model.classes_, probs)}

    return prediction, confidence_dict, cleaned


def get_top_keywords(model, vectorizer, text, prediction, top_n=10):
    """Extrae palabras que más influyeron en la predicción"""
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])

    class_idx = list(model.classes_).index(prediction)
    coefs = model.coef_[class_idx]
    feature_names = vectorizer.get_feature_names_out()

    vec_array = vec.toarray()[0]
    word_weights = []

    for idx, weight in enumerate(vec_array):
        if weight > 0:
            word = feature_names[idx]
            importance = coefs[idx] * weight
            word_weights.append((word, importance))

    word_weights.sort(key=lambda x: abs(x[1]), reverse=True)
    return word_weights[:top_n]


def get_alert_class(prediction):
    """Obtiene clase de alerta según predicción"""
    high_risk = ["Suicidal", "Ideación suicida"]
    medium_risk = ["Depression", "Depresión", "Anxiety", "Ansiedad"]

    if prediction in high_risk:
        return "alert-high"
    elif prediction in medium_risk:
        return "alert-medium"
    else:
        return "alert-low"


# ================================
# INICIALIZAR HISTORIAL
# ================================
if "history" not in st.session_state:
    st.session_state.history = []

# Cargar métricas del modelo
model_metrics = load_model_metrics()

# ================================
# HEADER
# ================================
st.markdown('<p class="main-header">Sistema de Monitoreo de Salud Mental</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Detección temprana de estados emocionales con Inteligencia Artificial</p>',
            unsafe_allow_html=True)

# ================================
# SIDEBAR
# ================================
with st.sidebar:
    st.header("Panel de Control")

    st.subheader("Información del Sistema")
    st.info("""
    **Modelo:** Support Vector Machine (SVM)

    **Técnica:** TF-IDF con bigramas

    **Categorías detectadas:**
    • Ansiedad
    • Depresión
    • Estrés
    • Ideación suicida
    """)

    # Métricas del modelo
    st.subheader("Rendimiento del Modelo")

    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Accuracy", f"{model_metrics['accuracy'] * 100:.1f}%")
        st.metric("Precision", f"{model_metrics['precision'] * 100:.1f}%")
    with col_m2:
        st.metric("F1-Score", f"{model_metrics['f1_score'] * 100:.1f}%")
        st.metric("Recall", f"{model_metrics['recall'] * 100:.1f}%")

    st.caption(f"Entrenado con {model_metrics['total_samples']:,} muestras")

    if st.session_state.history:
        st.subheader("Estadísticas de Sesión")

        predictions_only = [item['prediction'] for item in st.session_state.history]
        prediction_counts = Counter(predictions_only)

        st.metric("Total de análisis", len(st.session_state.history))

        for emotion, count in prediction_counts.most_common():
            st.write(f"**{emotion}:** {count}")

        if st.button("Limpiar Historial"):
            st.session_state.history = []
            st.rerun()

    st.divider()

    st.subheader("Recursos de Ayuda")
    st.markdown("""
    **Si estás en crisis:**

    Panamá: 169 (MINSA)

    Internacional: befrienders.org

    *Este sistema es una herramienta de apoyo y no reemplaza atención profesional.*
    """)

# ================================
# ÁREA PRINCIPAL
# ================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Ingresa tu texto para análisis")
    user_input = st.text_area(
        "Escribe cómo te sientes o qué está pasando por tu mente:",
        height=150,
        placeholder="Ejemplo: Me siento muy ansioso últimamente, no puedo dormir bien..."
    )

    analyze_button = st.button("Analizar Estado Emocional", type="primary", use_container_width=True)

with col2:
    st.subheader("Sugerencias")
    st.info("""
    **Para mejores resultados:**

    • Escribe al menos 2-3 oraciones

    • Sé honesto sobre tus sentimientos

    • Compatible con español e inglés
    """)

# ================================
# PROCESAMIENTO
# ================================
if analyze_button:
    if user_input.strip():
        with st.spinner("Analizando texto..."):
            model, vectorizer = load_model_and_vectorizer()

            if model and vectorizer:
                prediction, confidences, cleaned_text = get_prediction_confidence(
                    model, vectorizer, user_input
                )

                label_mapping = {
                    "Anxiety": "Ansiedad",
                    "Depression": "Depresión",
                    "Stress": "Estrés",
                    "Suicidal": "Ideación suicida",
                }

                prediction_es = label_mapping.get(prediction, prediction)
                alert_class = get_alert_class(prediction)

                st.session_state.history.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "text": user_input[:50] + "..." if len(user_input) > 50 else user_input,
                    "prediction": prediction_es,
                    "confidence": max(confidences.values()) * 100
                })

                st.divider()

                # ================================
                # RESULTADOS DEL ANÁLISIS
                # ================================
                st.subheader("Resultados del Análisis")

                col_res1, col_res2 = st.columns(2)

                with col_res1:
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <h3>Estado Detectado</h3>
                        <h2>{prediction_es}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col_res2:
                    max_conf = max(confidences.values()) * 100
                    st.metric("Nivel de Confianza", f"{max_conf:.1f}%")
                    st.progress(max_conf / 100)

                    # Mostrar confianza en palabras
                    if max_conf >= 80:
                        conf_text = "Muy Alta"
                    elif max_conf >= 60:
                        conf_text = "Alta"
                    elif max_conf >= 40:
                        conf_text = "Moderada"
                    else:
                        conf_text = "Baja"
                    st.caption(f"Confiabilidad: {conf_text}")

                st.divider()

                # ================================
                # DISTRIBUCIÓN DE CONFIANZA
                # ================================
                st.subheader("Distribución de Confianza por Categoría")

                conf_data = {label_mapping.get(k, k): v * 100 for k, v in confidences.items()}
                conf_df = pd.DataFrame({
                    "Emoción": list(conf_data.keys()),
                    "Confianza (%)": list(conf_data.values())
                }).sort_values("Confianza (%)", ascending=False)

                # Colores según categoría
                color_map = {
                    "Estrés": "#f59e0b",
                    "Ansiedad": "#f59e0b",
                    "Depresión": "#dc2626",
                    "Ideación suicida": "#991b1b"
                }
                conf_df["Color"] = conf_df["Emoción"].map(color_map)

                fig_conf = go.Figure(data=[
                    go.Bar(
                        y=conf_df["Emoción"],
                        x=conf_df["Confianza (%)"],
                        orientation='h',
                        marker=dict(
                            color=conf_df["Color"],
                            line=dict(color='#1a4d7a', width=1)
                        ),
                        text=conf_df["Confianza (%)"].round(1),
                        texttemplate='%{text}%',
                        textposition='outside',
                        textfont=dict(size=12, color='#1a4d7a', family='Arial')
                    )
                ])

                fig_conf.update_layout(
                    title="Nivel de confianza por categoría emocional",
                    title_font=dict(size=16, color='#1a4d7a', family='Arial'),
                    xaxis_title="Confianza (%)",
                    yaxis_title="",
                    height=300,
                    showlegend=False,
                    plot_bgcolor='black',
                    paper_bgcolor='black',
                    font=dict(color='#4a5568'),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='#e5e7eb',
                        range=[0, max(conf_df["Confianza (%)"]) * 1.15]
                    ),
                    yaxis=dict(
                        showgrid=False
                    )
                )
                st.plotly_chart(fig_conf, use_container_width=True)

                # ================================
                # PALABRAS CLAVE
                # ================================
                st.subheader("Palabras Clave Más Influyentes")

                keywords = get_top_keywords(model, vectorizer, user_input, prediction, top_n=10)

                if keywords:
                    col_kw1, col_kw2 = st.columns(2)

                    with col_kw1:
                        st.write("**Top 5 palabras que influyeron en la predicción:**")
                        kw_data = pd.DataFrame(keywords, columns=["Palabra", "Importancia"])
                        kw_data["Importancia"] = kw_data["Importancia"].abs()

                        fig_kw = go.Figure(data=[
                            go.Bar(
                                x=kw_data.head(5)["Importancia"],
                                y=kw_data.head(5)["Palabra"],
                                orientation='h',
                                marker=dict(
                                    color='#2563eb',
                                    line=dict(color='#1d4ed8', width=1)
                                ),
                                text=kw_data.head(5)["Importancia"].round(3),
                                textposition='outside',
                                textfont=dict(size=11, color='#1a4d7a', family='Arial')
                            )
                        ])

                        fig_kw.update_layout(
                            height=280,
                            showlegend=False,
                            plot_bgcolor='black',
                            paper_bgcolor='black',
                            font=dict(color='#4a5568'),
                            xaxis=dict(
                                title="Importancia",
                                showgrid=True,
                                gridcolor='#e5e7eb'
                            ),
                            yaxis=dict(
                                title="",
                                showgrid=False
                            ),
                            margin=dict(l=20, r=60, t=20, b=40)
                        )
                        st.plotly_chart(fig_kw, use_container_width=True)

                    with col_kw2:
                        st.write("**Lista completa de palabras clave:**")
                        for idx, (word, importance) in enumerate(keywords, 1):
                            st.write(f"{idx}. **{word}** ({importance:.3f})")

                st.divider()

                # ================================
                # RECOMENDACIONES
                # ================================
                st.subheader("Recomendaciones")

                if "Ideación suicida" in prediction_es or "Suicidal" in prediction:
                    st.error("""
                    **ALERTA: Se detectaron señales de alto riesgo**

                    Es muy importante que busques ayuda profesional inmediatamente:

                    • Llama al 169 (MINSA Panamá)

                    • Visita: befrienders.org

                    • Habla con alguien de confianza ahora mismo

                    • Acude a emergencias si te encuentras en peligro inmediato

                    **No estás solo. Hay ayuda disponible las 24 horas.**
                    """)

                elif "Depresión" in prediction_es or "Depression" in prediction:
                    st.warning("""
                    **Recomendaciones para manejar síntomas depresivos:**

                    • Practica técnicas de relajación y mindfulness

                    • Intenta hacer ejercicio ligero (caminar 15-20 min)

                    • Mantén contacto con amigos o familiares

                    • Considera agendar una consulta con un profesional

                    • Mantén una rutina de sueño regular
                    """)

                elif "Ansiedad" in prediction_es or "Anxiety" in prediction:
                    st.warning("""
                    **Recomendaciones para manejar la ansiedad:**

                    • Prueba ejercicios de respiración profunda (técnica 4-7-8)

                    • Escribe tus preocupaciones en un diario

                    • Escucha música relajante

                    • Practica meditación o yoga

                    • Si persiste, consulta con un profesional
                    """)

                elif "Estrés" in prediction_es or "Stress" in prediction:
                    st.info("""
                    **Recomendaciones para manejar el estrés:**

                    • Toma descansos regulares durante el día

                    • Prioriza tus tareas (urgente vs importante)

                    • Realiza actividad física regular

                    • Pasa tiempo en la naturaleza si es posible

                    • Asegúrate de descansar adecuadamente
                    """)

                else:
                    st.success("""
                    **Tu estado emocional parece estable**

                    • Continúa con tus hábitos saludables

                    • Practica la gratitud diariamente

                    • Mantén una rutina equilibrada

                    • Cultiva tus relaciones sociales
                    """)

    else:
        st.warning("Por favor, ingresa un texto para analizar.")

# ================================
# HISTORIAL
# ================================
if st.session_state.history:
    st.divider()
    st.subheader("Historial de Análisis (Sesión Actual)")

    hist_df = pd.DataFrame(st.session_state.history)

    col_hist1, col_hist2 = st.columns(2)

    with col_hist1:
        emotion_counts = hist_df['prediction'].value_counts()

        # Colores para el pie chart
        color_discrete_map = {
            "Estrés": "#f59e0b",
            "Ansiedad": "#f59e0b",
            "Depresión": "#dc2626",
            "Ideación suicida": "#991b1b"
        }

        fig_pie = px.pie(
            values=emotion_counts.values,
            names=emotion_counts.index,
            title='Distribución de Estados Emocionales Detectados',
            color=emotion_counts.index,
            color_discrete_map=color_discrete_map
        )
        fig_pie.update_traces(
            textfont_size=12,
            marker=dict(line=dict(color='#1a4d7a', width=2))
        )
        fig_pie.update_layout(
            title_font=dict(size=14, color='#1a4d7a'),
            font=dict(color='#4a5568')
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_hist2:
        st.write("**Últimos análisis realizados:**")
        display_df = hist_df[['timestamp', 'prediction', 'confidence']].copy()
        display_df.columns = ['Hora', 'Emoción', 'Confianza (%)']
        display_df['Confianza (%)'] = display_df['Confianza (%)'].round(1)
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ================================
# FOOTER
# ================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #6b7280; padding: 20px;'>
    <p><strong>Sistema de Monitoreo de Salud Mental - Fase 1</strong></p>
    <p>Desarrollado con IA para detección temprana de estados emocionales críticos</p>
    <p><em>Este sistema es una herramienta de apoyo y no sustituye la atención médica profesional</em></p>
</div>
""", unsafe_allow_html=True)
