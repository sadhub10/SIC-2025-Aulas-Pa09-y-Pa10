import streamlit as st
import pandas as pd
import numpy as np
import catboost as cb
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from difflib import SequenceMatcher


# Configuración de la página
st.set_page_config(
    page_title="Predicción de Deserción Escolar",
    page_icon="🎓",
    layout="wide"
)

# Título principal
st.title("🎓 Sistema de Predicción de Deserción Escolar")
st.markdown("---")

# Definir las columnas esperadas y sus valores posibles
COLUMNAS_ESPERADAS = {
    'edad': {'tipo': 'int64', 'rango': (5, 18), 'descripcion': 'Edad del estudiante', 'aliases': ['age', 'años']},
    'genero': {'tipo': 'object', 'valores': ['M', 'F'], 'descripcion': 'Género del estudiante', 'aliases': ['gender', 'sexo', 'sex']},
    'zona_residencia': {'tipo': 'object', 'valores': ['Urbana', 'Rural'], 'descripcion': 'Zona de residencia', 'aliases': ['zona', 'residencia', 'area']},
    'nivel': {'tipo': 'object', 'valores': ['Primaria', 'Premedia', 'Media'], 'descripcion': 'Nivel educativo', 'aliases': ['nivel_educativo', 'level']},
    'grado': {'tipo': 'int64', 'rango': (1, 12), 'descripcion': 'Grado escolar', 'aliases': ['grade', 'curso', 'año']},
    'tipo_escuela': {'tipo': 'object', 'valores': ['Oficial', 'Particular'], 'descripcion': 'Tipo de escuela', 'aliases': ['tipo', 'escuela', 'school_type']},
    'veces_repitio_grado': {'tipo': 'int64', 'rango': (0, 5), 'descripcion': 'Veces que repitió grado', 'aliases': ['repitio', 'repeticiones', 'veces_repitio']},
    'sobre_edad': {'tipo': 'int64', 'rango': (0, 5), 'descripcion': 'Años de sobre edad', 'aliases': ['sobreedad', 'edad_extra']},
    'promedio_actual': {'tipo': 'float64', 'rango': (1.0, 5.0), 'descripcion': 'Promedio académico actual', 'aliases': ['promedio', 'gpa', 'nota_actual']},
    'promedio_anterior': {'tipo': 'float64', 'rango': (1.0, 5.0), 'descripcion': 'Promedio académico anterior', 'aliases': ['promedio_previo', 'gpa_anterior']},
    'materias_reprobadas': {'tipo': 'int64', 'rango': (0, 10), 'descripcion': 'Número de materias reprobadas', 'aliases': ['reprobadas', 'materias_perdidas', 'failed_subjects']},
    'porcentaje_asistencia': {'tipo': 'float64', 'rango': (0, 100), 'descripcion': 'Porcentaje de asistencia', 'aliases': ['asistencia', 'attendance', 'pct_asistencia']},
    'tercil_socioeconomico': {'tipo': 'int64', 'valores': [1, 2, 3], 'descripcion': 'Tercil socioeconómico', 'aliases': ['tercil', 'nivel_socioeconomico', 'ses']},
    'nivel_educacion_padres': {'tipo': 'object', 'valores': ['Secundaria_Completa', 'Secundaria_Incompleta', 
                                                               'Primaria_Incompleta', 'Universidad', 'Primaria_Completa'], 
                                'descripcion': 'Nivel educativo de los padres', 'aliases': ['educacion_padres', 'parent_education']},
    'trabaja_estudiante': {'tipo': 'int64', 'valores': [0, 1], 'descripcion': 'Si el estudiante trabaja', 'aliases': ['trabaja', 'working', 'trabajo']}
}

def calcular_similitud(str1, str2):
    """Calcula la similitud entre dos strings"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def auto_mapear_columnas(columnas_archivo):
    """Intenta mapear automáticamente las columnas basándose en similitud de nombres"""
    mapeo_automatico = {}
    umbral_similitud = 0.6
    
    for col_esperada, info in COLUMNAS_ESPERADAS.items():
        mejor_match = None
        mejor_similitud = 0
        
        # Buscar coincidencia exacta primero
        if col_esperada in columnas_archivo:
            mapeo_automatico[col_esperada] = col_esperada
            continue
        
        # Buscar en aliases
        for alias in info.get('aliases', []):
            if alias in columnas_archivo:
                mapeo_automatico[col_esperada] = alias
                break
        
        # Si no hay match exacto, buscar por similitud
        if col_esperada not in mapeo_automatico:
            for col_archivo in columnas_archivo:
                # Calcular similitud con el nombre esperado
                sim = calcular_similitud(col_esperada, col_archivo)
                
                # Calcular similitud con aliases
                for alias in info.get('aliases', []):
                    sim_alias = calcular_similitud(alias, col_archivo)
                    sim = max(sim, sim_alias)
                
                if sim > mejor_similitud and sim >= umbral_similitud:
                    mejor_similitud = sim
                    mejor_match = col_archivo
            
            if mejor_match:
                mapeo_automatico[col_esperada] = mejor_match
    
    return mapeo_automatico

def crear_features_avanzados(df):
    """Crea features sintéticos basados en los pesos reales del generador de datos"""
    
    df_enhanced = df.copy()
    
    # Normalizar variables a [0, 1]
    promedio_norm = (5.0 - df['promedio_actual']) / 4.0
    materias_norm = df['materias_reprobadas'] / 3.0
    repitio_norm = df['veces_repitio_grado'] / 3.0
    sobre_edad_norm = df['sobre_edad'] / 3.0
    asistencia_norm = (100 - df['porcentaje_asistencia']) / 60.0
    tercil_norm = (3 - df['tercil_socioeconomico']) / 2.0
    trabaja_norm = df['trabaja_estudiante']
    
    educacion_bajo = (df['nivel_educacion_padres'].isin(['Primaria_Incompleta', 'Primaria_Completa'])).astype(int)
    
    # ÍNDICE DE RIESGO con pesos reales del generador
    df_enhanced['indice_riesgo_sintetico'] = (
        promedio_norm * 0.16 +
        materias_norm * 0.10 +
        repitio_norm * 0.18 +
        sobre_edad_norm * 0.22 +
        asistencia_norm * 0.12 +
        tercil_norm * 0.14 +
        trabaja_norm * 0.08 +
        educacion_bajo * 0.45
    )
    
    # Interacciones críticas
    df_enhanced['interaccion_tercil_repitio'] = (
        (df['tercil_socioeconomico'] == 1).astype(int) *
        (df['veces_repitio_grado'] >= 2).astype(int) * 2.5
    )
    
    df_enhanced['interaccion_trabajo_promedio'] = (
        df['trabaja_estudiante'] *
        (df['promedio_actual'] < 2.5).astype(int) * 3.2
    )
    
    df_enhanced['riesgo_academico_asistencia'] = (
        (df['porcentaje_asistencia'] < 75).astype(int) *
        (df['promedio_actual'] < 2.5).astype(int) * 2.0
    )
    
    # Features derivados
    df_enhanced['deterioro_academico'] = np.maximum(0, df['promedio_anterior'] - df['promedio_actual'])
    
    df_enhanced['riesgo_academico_total'] = (promedio_norm + materias_norm + repitio_norm + sobre_edad_norm) / 4.0
    df_enhanced['riesgo_socioeconomico_total'] = (tercil_norm + trabaja_norm + educacion_bajo) / 3.0
    df_enhanced['riesgo_acumulado'] = (df_enhanced['riesgo_academico_total'] * 
                                        df_enhanced['riesgo_socioeconomico_total'] * 
                                        asistencia_norm) ** (1/3)
    
    # One-hot encoding
    df_enhanced = pd.get_dummies(df_enhanced, columns=['nivel', 'nivel_educacion_padres'], drop_first=False)
    
    # Convertir categóricos a binario
    df_enhanced['genero'] = (df_enhanced['genero'] == 'M').astype(int)
    df_enhanced['zona_residencia'] = (df_enhanced['zona_residencia'] == 'Rural').astype(int)
    df_enhanced['tipo_escuela'] = (df_enhanced['tipo_escuela'] == 'Oficial').astype(int)
    
    return df_enhanced

def crear_visualizaciones(df_original, probabilidades, predicciones):
    """Crea visualizaciones de los resultados"""
    
    df_viz = df_original.copy()
    df_viz['probabilidad_desercion'] = probabilidades
    df_viz['prediccion'] = predicciones
    df_viz['categoria_riesgo'] = pd.cut(probabilidades, 
                                         bins=[0, 0.3, 0.6, 1.0], 
                                         labels=['Bajo', 'Medio', 'Alto'])
    
    # Crear subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distribución de Riesgo de Deserción', 
                       'Estudiantes por Categoría de Riesgo',
                       'Riesgo por Nivel Educativo',
                       'Top 10 Estudiantes en Mayor Riesgo'),
        specs=[[{'type': 'histogram'}, {'type': 'bar'}],
               [{'type': 'box'}, {'type': 'bar'}]]
    )
    
    # 1. Histograma de probabilidades
    fig.add_trace(
        go.Histogram(x=probabilidades, nbinsx=30, name='Probabilidad',
                    marker_color='rgb(55, 83, 109)'),
        row=1, col=1
    )
    
    # 2. Conteo por categoría
    categoria_counts = df_viz['categoria_riesgo'].value_counts()
    fig.add_trace(
        go.Bar(x=categoria_counts.index, y=categoria_counts.values,
              marker_color=['green', 'orange', 'red'], name='Estudiantes'),
        row=1, col=2
    )
    
    # 3. Box plot por nivel
    for nivel in df_viz['nivel'].unique():
        datos_nivel = df_viz[df_viz['nivel'] == nivel]['probabilidad_desercion']
        fig.add_trace(
            go.Box(y=datos_nivel, name=nivel),
            row=2, col=1
        )
    
    # 4. Top 10 en riesgo
    top_10 = df_viz.nlargest(10, 'probabilidad_desercion').reset_index()
    fig.add_trace(
        go.Bar(x=top_10.index, y=top_10['probabilidad_desercion'],
              marker_color='red', name='Probabilidad',
              text=top_10['probabilidad_desercion'].round(3),
              textposition='outside'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="Resumen de Predicciones de Deserción")
    fig.update_xaxes(title_text="Probabilidad", row=1, col=1)
    fig.update_xaxes(title_text="Categoría", row=1, col=2)
    fig.update_xaxes(title_text="Nivel Educativo", row=2, col=1)
    fig.update_xaxes(title_text="Estudiante", row=2, col=2)
    fig.update_yaxes(title_text="Frecuencia", row=1, col=1)
    fig.update_yaxes(title_text="Cantidad", row=1, col=2)
    fig.update_yaxes(title_text="Probabilidad", row=2, col=1)
    fig.update_yaxes(title_text="Probabilidad", row=2, col=2)
    
    return fig, df_viz

# Inicializar session state
if 'df_cargado' not in st.session_state:
    st.session_state.df_cargado = None
if 'mapeo_columnas' not in st.session_state:
    st.session_state.mapeo_columnas = {}
if 'predicciones_realizadas' not in st.session_state:
    st.session_state.predicciones_realizadas = False
if 'mapeo_automatico_realizado' not in st.session_state:
    st.session_state.mapeo_automatico_realizado = False

# Paso 1: Cargar archivo CSV
st.header("📁 Paso 1: Cargar Archivo CSV")
uploaded_file = st.file_uploader("Selecciona tu archivo CSV", type=['csv'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state.df_cargado = df
        
        # Auto-mapeo automático solo la primera vez
        if not st.session_state.mapeo_automatico_realizado:
            mapeo_auto = auto_mapear_columnas(df.columns.tolist())
            st.session_state.mapeo_columnas = mapeo_auto
            st.session_state.mapeo_automatico_realizado = True
            
            if mapeo_auto:
                st.success(f"✅ Archivo cargado: {len(df)} registros | 🎯 {len(mapeo_auto)} columnas mapeadas automáticamente")
            else:
                st.success(f"✅ Archivo cargado exitosamente: {len(df)} registros encontrados")
        
        with st.expander("👀 Vista previa de los datos"):
            st.dataframe(df.head(10))
            st.write(f"**Dimensiones:** {df.shape[0]} filas × {df.shape[1]} columnas")
            st.write(f"**Columnas encontradas:** {', '.join(df.columns.tolist())}")
    
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {str(e)}")

# Paso 2: Mapear columnas
if st.session_state.df_cargado is not None:
    st.header("🔄 Paso 2: Mapear Columnas")
    
    # Mostrar estadísticas de mapeo
    columnas_mapeadas = len(st.session_state.mapeo_columnas)
    columnas_totales = len(COLUMNAS_ESPERADAS)
    columnas_faltantes = columnas_totales - columnas_mapeadas
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Columnas Mapeadas", f"{columnas_mapeadas}/{columnas_totales}")
    with col_stat2:
        st.metric("Faltantes", columnas_faltantes)
    with col_stat3:
        progreso = (columnas_mapeadas / columnas_totales) * 100
        st.metric("Progreso", f"{progreso:.0f}%")
    
    # Mostrar barra de progreso
    st.progress(progreso / 100)
    
    if columnas_mapeadas > 0:
        with st.expander("✅ Ver columnas ya mapeadas"):
            for col_dest, col_orig in st.session_state.mapeo_columnas.items():
                st.write(f"• **{col_dest}** ← `{col_orig}`")
    
    st.write("Asigna cada columna de tu archivo a la columna correspondiente del modelo:")
    
    # Botón para resetear mapeo
    if st.button("🔄 Resetear Mapeo", help="Elimina todos los mapeos y empieza de nuevo"):
        st.session_state.mapeo_columnas = {}
        st.session_state.mapeo_automatico_realizado = False
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    mapeo = st.session_state.mapeo_columnas.copy()
    
    # Obtener columnas ya seleccionadas
    columnas_seleccionadas = set(mapeo.values())
    
    # Crear lista de columnas disponibles (excluyendo las ya seleccionadas)
    def get_opciones_disponibles(columna_actual=None):
        columnas_disponibles = ['-- Seleccionar --']
        for col in st.session_state.df_cargado.columns:
            # Incluir si no está seleccionada O si es la columna actual
            if col not in columnas_seleccionadas or col == columna_actual:
                columnas_disponibles.append(col)
        return columnas_disponibles
    
    with col1:
        st.subheader("Información del Estudiante")
        for col in ['edad', 'genero', 'zona_residencia', 'nivel', 'grado', 'tipo_escuela']:
            valor_actual = mapeo.get(col, '-- Seleccionar --')
            opciones = get_opciones_disponibles(valor_actual if valor_actual != '-- Seleccionar --' else None)
            
            # Determinar el índice inicial
            if valor_actual in opciones:
                index_inicial = opciones.index(valor_actual)
            else:
                index_inicial = 0
            
            # Mostrar indicador de mapeo
            if valor_actual != '-- Seleccionar --':
                emoji = "✅"
            else:
                emoji = "⚠️"
            
            nueva_seleccion = st.selectbox(
                f"{emoji} {col} - {COLUMNAS_ESPERADAS[col]['descripcion']}",
                opciones,
                index=index_inicial,
                key=f"map_{col}"
            )
            
            if nueva_seleccion != '-- Seleccionar --':
                mapeo[col] = nueva_seleccion
            elif col in mapeo:
                del mapeo[col]
    
    with col2:
        st.subheader("Información Académica y Socioeconómica")
        for col in ['veces_repitio_grado', 'sobre_edad', 'promedio_actual', 'promedio_anterior', 
                    'materias_reprobadas', 'porcentaje_asistencia', 'tercil_socioeconomico', 
                    'nivel_educacion_padres', 'trabaja_estudiante']:
            valor_actual = mapeo.get(col, '-- Seleccionar --')
            opciones = get_opciones_disponibles(valor_actual if valor_actual != '-- Seleccionar --' else None)
            
            # Determinar el índice inicial
            if valor_actual in opciones:
                index_inicial = opciones.index(valor_actual)
            else:
                index_inicial = 0
            
            # Mostrar indicador de mapeo
            if valor_actual != '-- Seleccionar --':
                emoji = "✅"
            else:
                emoji = "⚠️"
            
            nueva_seleccion = st.selectbox(
                f"{emoji} {col} - {COLUMNAS_ESPERADAS[col]['descripcion']}",
                opciones,
                index=index_inicial,
                key=f"map_{col}"
            )
            
            if nueva_seleccion != '-- Seleccionar --':
                mapeo[col] = nueva_seleccion
            elif col in mapeo:
                del mapeo[col]
    
    # Actualizar session state
    st.session_state.mapeo_columnas = mapeo
    
    # Validar mapeo
    if len(st.session_state.mapeo_columnas) == len(COLUMNAS_ESPERADAS):
        st.success("✅ ¡Perfecto! Todas las columnas han sido mapeadas correctamente")
    else:
        faltantes = set(COLUMNAS_ESPERADAS.keys()) - set(st.session_state.mapeo_columnas.keys())
        st.warning(f"⚠️ Faltan mapear {len(faltantes)} columnas: **{', '.join(faltantes)}**")

# Paso 3: Realizar predicción
if st.session_state.df_cargado is not None and len(st.session_state.mapeo_columnas) == len(COLUMNAS_ESPERADAS):
    st.header("🎯 Paso 3: Realizar Predicción")
    
    if st.button("🚀 Ejecutar Predicción", type="primary"):
        try:
            with st.spinner("Procesando datos y generando predicciones..."):
                # Crear DataFrame mapeado
                df_mapeado = pd.DataFrame()
                for col_destino, col_origen in st.session_state.mapeo_columnas.items():
                    df_mapeado[col_destino] = st.session_state.df_cargado[col_origen]
                
                # Crear features
                df_enhanced = crear_features_avanzados(df_mapeado)
                
                # Escalar datos
                scaler = StandardScaler()
                data_to_predict = scaler.fit_transform(df_enhanced)
                
                # NOTA: Aquí deberías cargar tu modelo real
                # Por ahora, generamos predicciones simuladas
                #st.warning("⚠️ Usando predicciones simuladas. Carga tu modelo 'mi_modelo_final.cbm' para predicciones reales.")
                
                # Simulación de predicciones (reemplazar con modelo real)
                model = cb.CatBoostClassifier()
                model.load_model("catboost_best_model.cbm")
                probabilidades = model.predict_proba(data_to_predict)[:, 1]
                predicciones = np.where(probabilidades >= 0.5014, 1, 0)
                
                # Crear visualizaciones
                fig, df_resultados = crear_visualizaciones(df_mapeado, probabilidades, predicciones)
                
                st.session_state.predicciones_realizadas = True
                st.session_state.df_resultados = df_resultados
                st.session_state.fig = fig
                
        except Exception as e:
            st.error(f"❌ Error durante la predicción: {str(e)}")

# Mostrar resultados
if st.session_state.get('predicciones_realizadas', False):
    st.header("📊 Resultados de la Predicción")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    df_res = st.session_state.df_resultados
    
    with col1:
        st.metric("Total Estudiantes", len(df_res))
    with col2:
        en_riesgo = (df_res['prediccion'] == 1).sum()
        st.metric("En Riesgo de Deserción", en_riesgo, 
                 delta=f"{(en_riesgo/len(df_res)*100):.1f}%")
    with col3:
        prob_promedio = df_res['probabilidad_desercion'].mean()
        st.metric("Probabilidad Promedio", f"{prob_promedio:.2%}")
    with col4:
        alto_riesgo = (df_res['categoria_riesgo'] == 'Alto').sum()
        st.metric("Riesgo Alto", alto_riesgo)
    
    st.plotly_chart(st.session_state.fig, use_container_width=True)
    
    # Tabla de resultados
    st.subheader("📋 Detalle de Estudiantes")
    
    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        filtro_riesgo = st.multiselect("Filtrar por categoría de riesgo:",
                                       ['Bajo', 'Medio', 'Alto'],
                                       default=['Alto'])
    with col2:
        filtro_nivel = st.multiselect("Filtrar por nivel educativo:",
                                      df_res['nivel'].unique(),
                                      default=df_res['nivel'].unique())
    
    df_filtrado = df_res[
        (df_res['categoria_riesgo'].isin(filtro_riesgo)) &
        (df_res['nivel'].isin(filtro_nivel))
    ].sort_values('probabilidad_desercion', ascending=False)
    
    st.dataframe(
        df_filtrado[['edad', 'genero', 'nivel', 'grado', 'promedio_actual', 
                     'porcentaje_asistencia', 'probabilidad_desercion', 
                     'categoria_riesgo']].head(50),
        use_container_width=True
    )
    
    # Descargar resultados
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Resultados Completos (CSV)",
        data=csv,
        file_name="predicciones_desercion.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("💡 **Nota:** Este sistema utiliza un modelo de Machine Learning para predecir el riesgo de deserción escolar basado en múltiples factores académicos y socioeconómicos.")