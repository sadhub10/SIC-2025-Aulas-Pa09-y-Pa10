# dashboard.py

import streamlit as st
import altair as alt

import pandas as pd
import os
import glob
from datetime import datetime

# Importar las funciones de los módulos .py creados
from scanner import escanear_web
from csv_generador import generar_csv_reporte
from diccionario import get_detalles_vulnerabilidad

# funcion para generar un único dataframe que contenga todos los demas dataframe
def cargar_historial_reportes(directorio="reportes"):
    search_path = os.path.join(directorio, "reporte_seguridad_*.csv")
    archivos = glob.glob(search_path)
    
    if not archivos:
        return pd.DataFrame()
    
    dfs = []    # lista de dataframes
    for archivo in archivos:
        try:
            df = pd.read_csv(archivo)
            
            # Extraer fecha del nombre del archivo dividiendo el nombre en pedazos dentro de una lista
            timestamp = os.path.basename(archivo).split("reporte_seguridad_")[-1].split(".")[0]
            fecha = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")   # combierte la fecha en un tipo datetime
            
            df["FECHA_REPORTE"] = fecha
            dfs.append(df)
        except Exception as e:
            print(f"[AVISO] No se pudo cargar {archivo}: {e}")
    
    # unir los dataframes en uno solo
    if dfs:
        return pd.concat(dfs, ignore_index=True).sort_values(by="FECHA_REPORTE")
    else:
        return pd.DataFrame()
    
# =============================================
# Configuración de la Aplicación Streamlit 
# =============================================

st.set_page_config(
    page_title="Dashboard de Seguridad Web",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================
#           Funciones de Utilidad 
# =============================================

def obtener_ultimo_reporte(directorio="reportes"):
    # buscar el archivo csv mas reciente en la carpeta reportes
    search_path = os.path.join(directorio, "reporte_seguridad_*.csv")
    archivos = glob.glob(search_path)
    
    if not archivos:
        return None
        
    archivos.sort(key=os.path.getmtime, reverse=True)
    return archivos[0]

def cargar_datos(ruta_csv):
    # Cargar los datos del csv en un DataFrame
    try:
        df = pd.read_csv(ruta_csv)
        # Asegura el orden correcto de las severidades
        severidad_orden = ["Alta", "Media", "Baja", "Informativa"]
        df['SEVERIDAD'] = pd.Categorical(df['SEVERIDAD'], categories=severidad_orden, ordered=True)
        return df
    except Exception as e:
        st.error(f"Error al cargar el CSV: {e}")
        return pd.DataFrame() 

def extraer_fecha_reporte(ruta_csv):
    # extae la fecha del nombre del archivo csv y la formatea

    nombre_archivo = os.path.basename(ruta_csv)
    
    try:
        # Extraer la parte de la fecha y hora: YYYYmmdd_HHMMSS
        timestamp_completo = nombre_archivo.split('reporte_seguridad_')[-1].split('.')[0]
        
        formato_lectura = "%Y%m%d_%H%M%S" 
        fecha_formateada = datetime.strptime(timestamp_completo, formato_lectura).strftime("%d/%m/%Y a las %H:%M:%S")
        return fecha_formateada
    except (ValueError, IndexError):
        return "Fecha Desconocida (Error de Formato)"


# =============================================
# --- Interfaz de Usuario y Lógica Principal ---
# =============================================

st.title("Escaner de Seguridad Web")
st.caption("Herramienta para evaluar fallos comunes de configuración y cabeceras de seguridad.")

# =========================================================================
# 1. SIDEBAR: CONTROL DE ESCANEO
# =========================================================================

with st.sidebar:
    st.header("Iniciar Nuevo Escaneo")
    
    target_url = st.text_input(
        "Ingresa la URL objetivo",
        placeholder="https://tudominio.com"
    )
    
    if st.button("Iniciar Escaneo", type="primary"):
        if target_url:
            with st.spinner(f"Escaneando: {target_url}..."):
                resultados_escaneo = escanear_web(target_url)
                
                if resultados_escaneo and resultados_escaneo[0]['ID_VULN'] == 'CONEXION_FALLIDA':
                    st.error(f"¡Fallo de Conexión! No se pudo acceder a {target_url}. Verifica la URL o la conexión.")
                    st.stop()
                
                if resultados_escaneo:
                    ruta_csv = generar_csv_reporte(resultados_escaneo)
                    if ruta_csv:
                        st.success("¡Escaneo completado y reporte generado! Recargando dashboard...")
                        st.rerun() 
                    else:
                        st.info("Escaneo completado, no se encontraron vulnerabilidades que reportar.")
                else:
                    st.info("Escaneo completado, no se encontraron vulnerabilidades.")
        else:
            st.warning("Por favor, ingrese una URL válida para iniciar el escaneo.")

# =========================================================================
# 2. CUERPO PRINCIPAL: VISUALIZACIÓN DE DATOS Y DESCARGA
# =========================================================================

ruta_ultimo_csv = obtener_ultimo_reporte()

if ruta_ultimo_csv:
    df_reporte = cargar_datos(ruta_ultimo_csv)
    nombre_archivo_base = os.path.basename(ruta_ultimo_csv)
    
    fecha_reporte = extraer_fecha_reporte(ruta_ultimo_csv)
    
    col_header, col_download = st.columns([0.7, 0.3])
    
    with col_header:
        st.subheader(f"Análisis del Último Reporte: {fecha_reporte}")
    
    if not df_reporte.empty:
        
        # --- BOTÓN DE DESCARGA ---
        with col_download:
            try:
                # Leer el archivo como bytes para el botón de descarga
                with open(ruta_ultimo_csv, "rb") as file:
                    st.download_button(
                        label="Descargar Reporte CSV",
                        data=file,
                        file_name=nombre_archivo_base,
                        mime='text/csv',
                        type="secondary"
                    )
            except Exception as e:
                st.warning("No se pudo preparar el archivo para la descarga.")
        # -------------------------

        # --- FILAS DE MÉTRICAS
        col1, col2, col3= st.columns(3)
        
        col1.metric(label="Total de Hallazgos", value=len(df_reporte))
        
        alta_count = df_reporte[df_reporte['SEVERIDAD'] == 'Alta'].shape[0]
        media_count = df_reporte[df_reporte['SEVERIDAD'] == 'Media'].shape[0]

        
        # Inyección CSS
        st.markdown("""
        <style>
        div[data-testid="stMetricDelta"] {
            color: #f5f5f5;
            font-size: 16px;
            background-color: #E60000;
        }
        div[data-testid="stMetricDelta"] svg {
            fill: #f5f5f5;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col2.metric(label="🚨 Severidad ALTA", value=alta_count, delta=f"Riesgo Crítico")
        col3.metric(label="⚠️ Severidad MEDIA", value=media_count, delta=f"Riesgo Moderado")
        
        try:
            url_escaneada = df_reporte['URL_AFECTADA'].iloc[0].split('/')[2]
        except IndexError:
            url_escaneada = "N/A"
            
        st.metric(label="Dominio Escaneado", value=url_escaneada)

        st.markdown("---")

        # --- GRÁFICO DE SEVERIDAD ---
        st.subheader("Distribución de Vulnerabilidades Detectadas")
        
        conteo_df = (
            df_reporte["SEVERIDAD"]
            .value_counts()
            .reset_index()
            .rename(columns={"SEVERIDAD": "Severidad", "count": "Cantidad"})
        )
        severidad_orden = ["Alta", "Media", "Baja", "Informativa"]

        chart = (
            alt.Chart(conteo_df)
            .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
            .encode(
                x=alt.X(
                    "Severidad",
                    sort=severidad_orden,
                    title=None
                ),
                y=alt.Y("Cantidad", title=None),
                color=alt.Color(
                    "Severidad",
                    scale=alt.Scale(
                        domain=severidad_orden,
                        range=["#E60000", "#FFA500", "#FFCC00", "#3399FF"]
                    ),
                ),
                tooltip=["Severidad", "Cantidad"]
            )
            .properties(height=400)
        )

        st.altair_chart(chart, use_container_width=True)

        st.markdown("---")
        
        # --- TABLA DE HALLAZGOS ---
        st.subheader("Lista Detallada de Hallazgos")
        
        df_display = df_reporte.rename(columns={
            'ID_VULN': 'ID',
            'URL_AFECTADA': 'URL/Endpoint',
            'SEVERIDAD': 'Riesgo',
            'TIPO_FALLO': 'Descripción Breve'
        })
        
        # 1. Definimos el st.dataframe con una clave (key) para almacenar el resultado.
        st.dataframe(
            df_display,
            use_container_width=True,
            height=300,
            column_order=('Riesgo', 'ID', 'Descripción Breve', 'URL/Endpoint'),
            hide_index=True,
            selection_mode='single-row',
            key='selection_data' # <-- Clave de estado de sesión
        )

        # 2. Accedemos a la selección a través de st.session_state, donde es un diccionario.
        selection_dict = st.session_state.get('selection_data', {})
        
        # Lógica de selección para mostrar detalles
        # Verificamos que el diccionario de selección exista y contenga la lista de filas
        if selection_dict and 'selection' in selection_dict and 'rows' in selection_dict['selection']:
            selected_index_list = selection_dict['selection']['rows']
            
            if selected_index_list:
                selected_index = selected_index_list[0]
                selected_vuln_id = df_reporte.iloc[selected_index]['ID_VULN']
                
                detalles_completos = get_detalles_vulnerabilidad(selected_vuln_id)
                
                if detalles_completos:
                    st.markdown("---")
                    st.subheader(f"Detalles y Solución para: **{detalles_completos['nombre']}**")
                    
                    st.markdown(f"**Riesgo Detectado:** `{selected_vuln_id}` en `{df_reporte.iloc[selected_index]['URL_AFECTADA']}`")
                    
                    st.info(f"**Descripción:** {detalles_completos['descripcion']}")
                    
                    st.success(f"**Solución Recomendada:** {detalles_completos['solucion']}")
                else:
                    st.warning("Detalles no encontrados en el diccionario para este ID.")

    else:
        st.warning(f"El reporte de {fecha_reporte} se cargó correctamente, pero no contiene datos de vulnerabilidades.")

else:
    st.info("No se han encontrado reportes de escaneo. Inicie un nuevo escaneo en la barra lateral para generar el primer reporte.")


# ================================
# Sección: Historial General
# ================================

st.markdown("## Historial de Escaneos")

df_historial = cargar_historial_reportes()

if not df_historial.empty:

    st.subheader("Distribución de Vulnerabilidades")

    conteo_df = (
        df_historial["SEVERIDAD"]
        .value_counts()
        .reset_index()
        .rename(columns={"SEVERIDAD": "Severidad", "count": "Cantidad"})
    )
    
    severidad_orden = ["Alta", "Media", "Baja", "Informativa"]
    
    chart = (
        alt.Chart(conteo_df)
        .mark_bar(cornerRadiusTopLeft=10, cornerRadiusTopRight=10)
        .encode(
            x=alt.X(
                "Severidad",
                sort=severidad_orden,
                title=None
            ),
            y=alt.Y("Cantidad", title=None),
            color=alt.Color(
                "Severidad",
                scale=alt.Scale(
                    domain=severidad_orden,
                    range=["#E60000", "#FFA500", "#FFCC00", "#3399FF"]
                ),
            ),
            tooltip=["Severidad", "Cantidad"]
        )
        .properties(height=400)
    )

    st.altair_chart(chart, use_container_width=True)

    # Botón para exportar todo el dataset
    csv_export = df_historial.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar historial (CSV)",
        data=csv_export,
        file_name="historial_vulnerabilidades.csv",
        mime="text/csv"
    )
else:
    st.info("No se han encontrado múltiples reportes para construir un historial.")
