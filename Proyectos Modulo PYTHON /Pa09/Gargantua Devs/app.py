import warnings
import logging
import sys

warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*WebSocket.*')

logging.getLogger('tornado.application').setLevel(logging.ERROR)
logging.getLogger('tornado.general').setLevel(logging.ERROR)
logging.getLogger('tornado.websocket').setLevel(logging.ERROR)

class SuppressWebSocketErrors:
    def __init__(self, stream):
        self.stream = stream
        
    def write(self, message):
        # Filtrar mensajes de WebSocket
        if 'WebSocketClosedError' not in message and 'websocket.py' not in message:
            self.stream.write(message)
    
    def flush(self):
        self.stream.flush()

sys.stderr = SuppressWebSocketErrors(sys.stderr)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from src.web_config import PAGE_CONFIG, apply_custom_styles
import src.data_loader as dl
import src.visualizations as vz
import src.utils as ut

# ========== CONFIGURACIÓN DE LA PÁGINA ==========
st.set_page_config(**PAGE_CONFIG)

apply_custom_styles()

# Titulo de la aplicacion / pagina web
st.title("Panama Safe - Análisis Geográfico de Delitos")
st.markdown("Panel interactivo sobre homicidios y feminicidios en Panamá")
st.markdown("---")

# ========== CARGA DE DATOS ==========
df = dl.load_data()

# Cargar GeoJSON
@st.cache_resource
def load_geojson():
    with open('data/geojson/pa.geojson', 'r', encoding='utf-8') as f:
        return json.load(f)
geojson_panama = load_geojson()
#debugin solamente para el geojson
print(geojson_panama["features"][0]["properties"])

# ========== BARRA LATERAL CON FILTROS ==========
st.sidebar.header("Filtros de Análisis")
st.sidebar.markdown("Selecciona los criterios para filtrar los datos:")

# Filtro de Año con Slider
anios_disponibles = sorted(df['año'].dropna().unique())
if len(anios_disponibles) > 1:
    rango_anios = st.sidebar.slider(
        "Rango de Años",
        min_value=int(min(anios_disponibles)),
        max_value=int(max(anios_disponibles)),
        value=(int(min(anios_disponibles)), int(max(anios_disponibles)))
    )
else:
    rango_anios = (int(anios_disponibles[0]), int(anios_disponibles[0]))

# Filtro de Provincia
provincias_disponibles = sorted(df['provincia'].astype(str).unique())
provincias_seleccionadas = st.sidebar.multiselect(
    "Provincia(s)",
    options=provincias_disponibles,
    default=provincias_disponibles
)

# Filtro de Tipo de Crimen
crimen_disponibles = sorted(df['tipo_crimen'].unique())
crimen_seleccionados = st.sidebar.multiselect(
    "Tipo(s) de Crimen",
    options=crimen_disponibles,
    default=crimen_disponibles
)

# Filtro de Rango de Edad
edades_disponibles = sorted(df['rango_de_edad'].unique())
edades_seleccionadas = st.sidebar.multiselect(
    "Rango(s) de Edad",
    options=edades_disponibles,
    default=edades_disponibles
)

# Filtro de Tipo de Arma
armas_disponibles = sorted(df['tipo_de_arma_utilizada'].unique())
armas_seleccionadas = st.sidebar.multiselect(
    "🔫 Tipo(s) de Arma",
    options=armas_disponibles,
    default=armas_disponibles
)

# Filtro de Sexo
sexo_disponibles = sorted(df['sexo'].unique())
sexo_seleccionados = st.sidebar.multiselect(
    "Sexo",
    options=sexo_disponibles,
    default=sexo_disponibles
)

st.sidebar.markdown("---")

# Botón para resetear filtros
if st.sidebar.button("Resetear Filtros"):
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("**Tip**: Los gráficos se actualizan automáticamente al cambiar los filtros.")

# ========== APLICAR FILTROS ==========
df_filtrado = df.copy()

# Aplicar filtros
df_filtrado = df_filtrado[
    (df_filtrado['año'] >= rango_anios[0]) & 
    (df_filtrado['año'] <= rango_anios[1])
]

if provincias_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['provincia'].astype(str).isin(provincias_seleccionadas)]

if crimen_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['tipo_crimen'].isin(crimen_seleccionados)]

if edades_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['rango_de_edad'].isin(edades_seleccionadas)]

if armas_seleccionadas:
    df_filtrado = df_filtrado[df_filtrado['tipo_de_arma_utilizada'].isin(armas_seleccionadas)]

if sexo_seleccionados:
    df_filtrado = df_filtrado[df_filtrado['sexo'].isin(sexo_seleccionados)]

# Verificación de datos
if df_filtrado.empty:
    st.error("No hay datos disponibles para los filtros seleccionados. Por favor, ajusta los filtros.")
    st.stop()

# ========== MÉTRICAS PRINCIPALES ==========
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: #1E1E2F;
        padding: 15px 10px;
        border-radius: 15px;
        border: 1px solid #2E2E3F;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetricValue"] {
        color: ##FFFFFF !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #CCCCCC !important;
        font-weight: bold;
    }
    div[data-testid="stMetricDelta"] {
        color: #77FF77 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_casos = len(df_filtrado)
    delta_casos = len(df_filtrado) - len(df)
    st.metric(
        label="Total de Casos",
        value=f"{total_casos:,}",
        delta=f"{delta_casos:,}" if delta_casos != 0 else "Todos los datos"
    )

with col2:
    if not df_filtrado.empty:
        provincia_mayor = df_filtrado['provincia'].value_counts().index[0]
        casos_mayor = df_filtrado['provincia'].value_counts().values[0]
        st.metric(
            label="Provincia Crítica",
            value=provincia_mayor,
            delta=f"{casos_mayor} casos"
        )

with col3:
    if not df_filtrado.empty:
        arma_comun = df_filtrado['tipo_de_arma_utilizada'].value_counts().index[0]
        pct_arma = (df_filtrado['tipo_de_arma_utilizada'].value_counts().values[0] / len(df_filtrado) * 100)
        st.metric(
            label="Arma más Usada",
            value=arma_comun,
            delta=f"{pct_arma:.1f}%"
        )

with col4:
    if not df_filtrado.empty:
        edad_comun = df_filtrado['rango_de_edad'].value_counts().index[0]
        casos_edad = df_filtrado['rango_de_edad'].value_counts().values[0]
        st.metric(
            label="Edad más Afectada",
            value=edad_comun,
            delta=f"{casos_edad} casos"
        )

st.markdown("---")

# ========== BOTÓN DE DESCARGA ==========
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')
#utfo8 pa que no queden caracteres raros en el .csv

csv = convert_df_to_csv(df_filtrado)
st.sidebar.download_button(
    label="Descargar datos filtrados",
    data=csv,
    file_name=f'panama_safe_datos_{pd.Timestamp.now().strftime("%Y%m%d")}.csv',
    mime='text/csv',
    help="Descarga los datos actuales con los filtros aplicados"
)

#habria que mejorar un poco esta parte ya sea incorporando nuevas graficas.
# ========== TABS PRINCIPALES ==========
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Mapa Interactivo", 
    "Tendencias Temporales", 
    "Análisis Comparativo",
    "Distribuciones",
    "Datos Crudos"
])

# ========== TAB 1: MAPA INTERACTIVO ==========
with tab1:
    st.markdown("Mapa de calor interactivo")
    
    # Preparar datos para el mapa
    df_mapa = df.groupby(['provincia', 'año']).size().reset_index(name='casos')
    #necsito ordenarlo pa evitar probelmas de años no consecutivos en el slider
    df_mapa = df_mapa.sort_values('año') 
    
    # Crear el mapa coroplético animado
    fig_mapa = px.choropleth(
        df_mapa,
        geojson=geojson_panama,
        locations='provincia',
        featureidkey="properties.name",
        color='casos',
        animation_frame='año',
        color_continuous_scale='Reds',
        range_color=[0, df_mapa['casos'].max()],
        labels={'casos': 'Número de Casos'},
        title='Evolución de Casos por Provincia'
    )
    
    fig_mapa.update_geos(
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=True,
        coastlinecolor="RebeccaPurple"
    )
    
    fig_mapa.update_layout(
        height=600,
        margin={"r":0,"t":40,"l":0,"b":0}
    )
    
    st.plotly_chart(fig_mapa, use_container_width=True)
    
    # Mapa de calor estático
    st.markdown("Intensidad de Casos por Provincia")
    df_mapa_estatico = df.groupby('provincia').size().reset_index(name='casos')
    
    fig_mapa_estatico = px.choropleth(
        df_mapa_estatico,
        geojson=geojson_panama,
        locations='provincia',
        featureidkey="properties.name",
        color='casos',
        color_continuous_scale='YlOrRd',
        labels={'casos': 'Total de Casos'},
        title='Concentración Total de Casos'
    )
    
    fig_mapa_estatico.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    fig_mapa_estatico.update_layout(height=500)
    st.plotly_chart(fig_mapa_estatico, use_container_width=True)

# ========== TAB 2: TENDENCIAS TEMPORALES ==========
with tab2:
    st.markdown("Análisis temporal de delitos")
    
    # Gráfico de tendencia original
    st.plotly_chart(vz.grafico_tendencia_temporal(df_filtrado), use_container_width=True)
    
# ========== TAB 3: ANÁLISIS COMPARATIVO ==========
with tab3:
    st.markdown("Comparador de provincias")
    
    provincias_comparar = st.multiselect(
        "Selecciona provincias para comparar (máximo 5):",
        options=provincias_disponibles,
        default=provincias_disponibles[:min(3, len(provincias_disponibles))],
        max_selections=5
    )
    
    if provincias_comparar:
        df_comp = df_filtrado[df_filtrado['provincia'].isin(provincias_comparar)]
        df_comp_grouped = df_comp.groupby(['año', 'provincia']).size().reset_index(name='casos')
        
        fig_comp = px.line(
            df_comp_grouped,
            x='año',
            y='casos',
            color='provincia',
            markers=True,
            title='Comparación Temporal entre Provincias Seleccionadas',
            labels={'casos': 'Número de Casos', 'año': 'Año'}
        )
        fig_comp.update_layout(height=500, hovermode='x unified')
        st.plotly_chart(fig_comp, use_container_width=True)
        
# ========== TAB 4: DISTRIBUCIONES ==========
with tab4:
    st.markdown("Análisis de distribuciones")
    
    # Distribución por edad y sexo
    st.markdown("Distribución por Rango de Edad y Sexo")
    df_edad_sexo = df_filtrado.groupby(['rango_de_edad', 'sexo']).size().reset_index(name='casos')
    
    if not df_edad_sexo.empty:
        fig_edad = px.bar(
            df_edad_sexo,
            x='rango_de_edad',
            y='casos',
            color='sexo',
            barmode='group',
            title='Casos por Rango de Edad y Sexo',
            labels={'casos': 'Número de Casos', 'rango_de_edad': 'Rango de Edad'}
        )
        fig_edad.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig_edad, use_container_width=True)
        
    st.markdown("---")
    
    if not df_filtrado.empty and 'tipo_de_arma_utilizada' in df_filtrado.columns:
        fig_sexo = vz.grafico_arma_barras(df_filtrado)
        st.plotly_chart(fig_sexo, use_container_width=True)
    
# ========== TAB 5: DATOS CRUDOS ==========
with tab5:
    st.markdown(" Vista de Datos Filtrados")
    st.markdown(f"**Total de registros:** {len(df_filtrado):,}")
    
    # Opciones de visualización
    col1, col2 = st.columns([3, 1])
    with col1:
        num_filas = st.slider("Número de filas a mostrar:", 10, 500, 100)
    with col2:
        mostrar_todo = st.checkbox("Mostrar todo")
    
    if mostrar_todo:
        st.dataframe(df_filtrado, use_container_width=True, height=600)
    else:
        st.dataframe(df_filtrado.head(num_filas), use_container_width=True, height=600)
    
    # Estadísticas descriptivas
    st.markdown("Estadísticas Descriptivas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("Por Provincia")
        st.dataframe(
            df_filtrado['provincia'].value_counts().reset_index(),
            column_config={
                "provincia": "Provincia",
                "count": "Casos"
            },
            hide_index=True
        )
    
    with col2:
        st.markdown("Por Tipo de Crimen")
        st.dataframe(
            df_filtrado['tipo_crimen'].value_counts().reset_index(),
            column_config={
                "tipo_crimen": "Tipo de Crimen",
                "count": "Casos"
            },
            hide_index=True
        )
    
    with col3:
        st.markdown("Por Año")
        st.dataframe(
            df_filtrado['año'].value_counts().sort_index().reset_index(),
            column_config={
                "año": "Año",
                "count": "Casos"
            },
            hide_index=True
        )