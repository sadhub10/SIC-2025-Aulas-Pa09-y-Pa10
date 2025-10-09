# app_analisis_financiero.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- RUTAS DE ARCHIVOS ---
FINANCIAL_FILE_PATH = "Financial Statements.csv"
ABOUT_IMAGE_PATH = "spaghetti_coders.png"  

# ==============================================================================
# LÓGICA DE PROCESAMIENTO Y FORMATO (Funciones Auxiliares)
# ==============================================================================

@st.cache_data
def load_and_clean_data(file_path):
    """Carga y limpia el DataFrame completo una sola vez."""
    if not os.path.exists(file_path):
        return None
    try:
        df = pd.read_csv(file_path)

        # Limpiar y estandarizar nombres de columna
        df.columns = df.columns.str.strip()

        # Columnas numéricas esperadas (si no existen, se ignoran)
        numeric_cols = [
            'Year', 'Revenue', 'Net Income', 'Gross Profit', 'ROE', 'ROA',
            'Net Profit Margin', 'Current Ratio', 'Debt/Equity Ratio',
            'Market Cap(in B USD)'
        ]
        for c in numeric_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')

        # Company a mayúsculas y sin espacios
        if 'Company' in df.columns:
            df['Company'] = df['Company'].astype(str).str.strip().str.upper()

        # Asegurar Year entero (cuando sea posible)
        if 'Year' in df.columns:
            df['Year'] = pd.to_numeric(df['Year'], errors='coerce', downcast='integer')

        # Calcular Ratios Clave en la carga (con control de división por cero)
        if {'Gross Profit', 'Revenue'}.issubset(df.columns):
            df['Gross Margin'] = np.where(
                (df['Revenue'] > 0) & (~df['Revenue'].isna()),
                (df['Gross Profit'] / df['Revenue']) * 100,
                np.nan
            )

        # P/E Ratio estándar: no aplica si Net Income <= 0 o NaN
        if {'Net Income', 'Market Cap(in B USD)'}.issubset(df.columns):
            ni = pd.to_numeric(df['Net Income'], errors='coerce')
            mc_bil = pd.to_numeric(df['Market Cap(in B USD)'], errors='coerce')  # en miles de millones
            pe = np.where((ni > 0) & (~ni.isna()) & (~mc_bil.isna()), (mc_bil * 1000) / ni, np.nan)
            df['PE Ratio'] = pe

        # Sanea infinitos
        df.replace([np.inf, -np.inf], np.nan, inplace=True)

        return df
    except Exception as e:
        st.error(f"Error al cargar o limpiar los datos: {e}")
        return None


def format_currency(value, decimals=2):
    """Formatea un número grande como moneda (ej: $12.34M)."""
    if pd.isna(value):
        return "-"
    try:
        value = float(value)
    except Exception:
        return "-"
    if abs(value) >= 1e9:
        return f"${value/1e9:,.{decimals}f}B"
    elif abs(value) >= 1e6:
        return f"${value/1e6:,.{decimals}f}M"
    else:
        return f"${value:,.{decimals}f}"


def format_percentage(value):
    """Formatea un valor como porcentaje."""
    if pd.isna(value):
        return "-"
    try:
        return f"{float(value):.2f}%"
    except Exception:
        return "-"


def procesar_datos_financieros(df_base, empresa_simbolos):
    """Procesa los datos para las empresas seleccionadas."""
    if df_base is None or not empresa_simbolos:
        return {}

    data_dict = {}
    df_filtered = df_base[df_base['Company'].isin(empresa_simbolos)].copy()

    for empresa in empresa_simbolos:
        df_empresa_hist = df_filtered[df_filtered['Company'] == empresa].sort_values(by='Year').copy()
        if df_empresa_hist.empty:
            continue

        latest_year = df_empresa_hist['Year'].max()
        data_point = df_empresa_hist[df_empresa_hist['Year'] == latest_year].iloc[0].copy()

        data_dict[empresa] = {
            'historial_df': df_empresa_hist,
            'empresa': data_point.get('Company', empresa),
            'año': latest_year,
            'Revenue': data_point.get('Revenue', np.nan),
            'Net Income': data_point.get('Net Income', np.nan),
            'Gross Margin': data_point.get('Gross Margin', np.nan),
            'Net Margin': data_point.get('Net Profit Margin', np.nan),
            'ROE': data_point.get('ROE', np.nan),
            'ROA': data_point.get('ROA', np.nan),
            'PE Ratio': data_point.get('PE Ratio', np.nan),
        }

    return data_dict


@st.cache_data
def obtener_datos_para_global(df_base):
    """Calcula métricas medianas de la industria y devuelve el DF con ratios."""
    if df_base is None:
        return None

    required_cols = ['Revenue', 'Net Income', 'Net Profit Margin', 'Gross Margin', 'ROE', 'ROA']
    present = [c for c in required_cols if c in df_base.columns]
    if not present:
        return {'Total_Companies': 0, 'Net_Margin_Median': 0, 'df_full': pd.DataFrame()}

    df = df_base.dropna(subset=present).copy()
    if df.empty:
        return {'Total_Companies': 0, 'Net_Margin_Median': 0, 'df_full': pd.DataFrame()}

    global_metrics = {
        'Revenue_Median': df['Revenue'].median() if 'Revenue' in df else np.nan,
        'Net_Income_Median': df['Net Income'].median() if 'Net Income' in df else np.nan,
        'Gross_Margin_Median': df['Gross Margin'].median() if 'Gross Margin' in df else np.nan,
        'Net_Margin_Median': df['Net Profit Margin'].median() if 'Net Profit Margin' in df else np.nan,
        'ROE_Median': df['ROE'].median() if 'ROE' in df else np.nan,
        'ROA_Median': df['ROA'].median() if 'ROA' in df else np.nan,
        'Total_Companies': df['Company'].nunique() if 'Company' in df else 0,
        'df_full': df
    }
    return global_metrics


# ==============================================================================
# INTERFAZ STREAMLIT
# ==============================================================================

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Análisis Financiero",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TÍTULO PRINCIPAL ---
st.title("💰 Dashboard de Exploración Financiera")
st.markdown("Análisis y visualización de estados financieros de diversas compañías.")

# --- CARGA INICIAL Y PRE-PROCESAMIENTO ---
df_base = load_and_clean_data(FINANCIAL_FILE_PATH)

if df_base is None:
    st.error(f"⚠️ Error: No se pudo cargar el archivo de datos **`{FINANCIAL_FILE_PATH}`**.")
    st.stop()

company_list = sorted(df_base['Company'].dropna().unique().tolist())

# --- SIDEBAR: SELECTOR DE EMPRESAS ---
st.sidebar.title("⚙️ Configuración de Análisis")
empresas_seleccionadas = st.sidebar.multiselect(
    "Selecciona hasta 2 Compañías:",
    options=company_list,
    default=company_list[:1] if company_list else [],
    max_selections=2
)

st.sidebar.write("---")

# --- SIDEBAR: SOBRE NOSOTROS ---
with st.sidebar.expander("👥 Sobre nosotros", expanded=True):
    try:
        st.image(ABOUT_IMAGE_PATH, use_container_width=True)
    except Exception:
        st.info("Coloca la imagen 'spaghetti_coders.png' en la carpeta del proyecto para mostrarla aquí.")
    st.markdown(
        """
**Spaghetti Coders**  
Somos un grupo de estudiantes panameños apasionados por la informática y la creación de software.  
Este proyecto es la culminación del **módulo de Python** del **Samsung Innovation Campus 2025**.
        """
    )

# --- PROCESAMIENTO DE DATOS ---
datos_empresas = procesar_datos_financieros(df_base, empresas_seleccionadas)
datos_globales = obtener_datos_para_global(df_base)

# --- ESTRUCTURA PRINCIPAL DE PESTAÑAS ---
tab_stats, tab_analisis, tab_comparacion, tab_global, tab_info = st.tabs([
    "📈 Estadísticas y Distribución",
    "📊 Análisis Individual",
    "⚖️ Comparación Histórica",
    "🌎 Resumen Global",
    "📘 Explicación de Métricas Financieras"
])

# ==============================================================================
# PESTAÑA 1: ESTADÍSTICAS Y DISTRIBUCIÓN
# ==============================================================================
with tab_stats:
    st.header("📈 Estadística Descriptiva y Distribución de Variables")

    df_global = datos_globales['df_full'].copy()

    # 1. ESTADÍSTICA DESCRIPTIVA
    st.markdown("### 📊 Estadística Descriptiva de Variables Numéricas")

    if not df_global.empty:
        # Seleccionar columnas numéricas relevantes para estadística
        numerical_cols_stats = df_global.select_dtypes(include=np.number).columns.tolist()
        cols_to_describe = [col for col in numerical_cols_stats if col not in ['Year']]

        if cols_to_describe:
            desc = df_global[cols_to_describe].describe().T

            # Arreglo defensivo por si alguna versión/locale trae 'min,' en lugar de 'min'
            if 'min,' in desc.columns:
                desc = desc.rename(columns={'min,': 'min'})

            # Selección segura de columnas estándar
            wanted = ['count', 'mean', 'std', 'min', 'max']
            available = [c for c in wanted if c in desc.columns]

            stats_df = desc[available].reset_index().rename(columns={'index': 'Variable'})

            # Renombrado amigable en español solo para columnas presentes
            rename_map = {
                'count': 'Conteo',
                'mean': 'Media',
                'std': 'Desviación Estándar',
                'min': 'Mínimo',
                'max': 'Máximo'
            }
            stats_df = stats_df.rename(columns={k: v for k, v in rename_map.items() if k in stats_df.columns})

            # Formateador dinámico solo para columnas que existan
            fmt_cols = {}
            if 'Conteo' in stats_df.columns:
                fmt_cols['Conteo'] = "{:,.0f}"

            def format_stat(val):
                if isinstance(val, (int, float, np.floating)):
                    return f"{val:,.0f}" if abs(val) > 1000 else f"{val:.2f}"
                return val

            for c in ['Media', 'Desviación Estándar', 'Mínimo', 'Máximo']:
                if c in stats_df.columns:
                    fmt_cols[c] = format_stat

            st.dataframe(stats_df.style.format(fmt_cols), use_container_width=True, hide_index=True)
        else:
            st.info("No hay columnas numéricas adecuadas para describir.")
    else:
        st.info("No hay datos suficientes para mostrar estadísticas descriptivas.")

    st.write("---")

    # 2. GRÁFICOS DE DISTRIBUCIÓN (HISTOGRAMAS)
    st.markdown("### 📉 Distribución de Variables Clave")

    available_for_chart = [
        c for c in ['Revenue', 'Net Income', 'Gross Profit', 'Net Profit Margin', 'ROE', 'ROA', 'PE Ratio']
        if c in df_global.columns
    ]
    if len(available_for_chart) >= 1:
        df_chart = df_global[available_for_chart].copy()

        # Limpieza de valores extremos para visualización (clip por percentiles por columna)
        lower_q = df_chart.quantile(0.01)
        upper_q = df_chart.quantile(0.99)
        df_chart = df_chart.clip(lower=lower_q, upper=upper_q, axis=1)

        col_hist1, col_hist2 = st.columns(2)

        with col_hist1:
            var_dist1 = st.selectbox("Histograma 1:", available_for_chart, index=0)
            fig_hist1, ax_hist1 = plt.subplots(figsize=(8, 4))
            sns.histplot(df_chart[var_dist1].dropna(), bins=30, kde=True, color='skyblue', ax=ax_hist1)
            ax_hist1.set_title(f'Distribución de {var_dist1}', fontsize=12)
            st.pyplot(fig_hist1)

        with col_hist2:
            idx2 = 1 if len(available_for_chart) > 1 else 0
            var_dist2 = st.selectbox("Histograma 2:", available_for_chart, index=idx2)
            fig_hist2, ax_hist2 = plt.subplots(figsize=(8, 4))
            sns.histplot(df_chart[var_dist2].dropna(), bins=30, kde=True, color='lightcoral', ax=ax_hist2)
            ax_hist2.set_title(f'Distribución de {var_dist2}', fontsize=12)
            st.pyplot(fig_hist2)
    else:
        st.info("No hay variables numéricas disponibles para los histogramas.")

# ==============================================================================
# PESTAÑA 2: ANÁLISIS INDIVIDUAL
# ==============================================================================
with tab_analisis:
    st.header("📊 Análisis Detallado y Evolución Histórica")

    if not empresas_seleccionadas:
        st.info("Por favor, selecciona al menos una compañía en la barra lateral.")
    elif datos_empresas:
        empresa_actual = empresas_seleccionadas[0]
        data = datos_empresas.get(empresa_actual)

        if data:
            st.subheader(f"Reporte Clave: {data['empresa']} - Año {data['año']}")

            # --- KPI Cards ---
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ingresos (Revenue)", format_currency(data['Revenue'], 0))
            with col2:
                st.metric("Ganancia Neta", format_currency(data['Net Income'], 0))
            with col3:
                st.metric("Margen Neto", format_percentage(data['Net Margin']))
            with col4:
                st.metric("ROE (Rentabilidad)", format_percentage(data['ROE']))

            st.write("---")

            # --- GRÁFICO DE EVOLUCIÓN: Ingresos vs Ganancias ---
            st.markdown(" #### Evolución de Ingresos y Ganancias (Histórico)")

            df_hist = data['historial_df'].copy()
            if not df_hist.empty:
                fig, ax = plt.subplots(figsize=(10, 5))

                # Gráfico de Revenue
                ax.plot(df_hist['Year'], df_hist['Revenue'], marker='o', label='Revenue', color='#1f77b4')
                ax.set_ylabel('Revenue (M/B USD)', color='#1f77b4')
                ax.tick_params(axis='y', labelcolor='#1f77b4')

                # Eje Y secundario para Net Income
                ax2 = ax.twinx()
                ax2.plot(df_hist['Year'], df_hist['Net Income'], marker='s', label='Net Income', color='#ff7f0e')
                ax2.set_ylabel('Net Income (M/B USD)', color='#ff7f0e')
                ax2.tick_params(axis='y', labelcolor='#ff7f0e')

                ax.set_title(f"Tendencia Financiera de {data['empresa']}")
                ax.set_xlabel('Año')
                ax.grid(True, linestyle='--', alpha=0.6)

                lines, labels = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines + lines2, labels + labels2, loc='upper left')

                st.pyplot(fig)
            else:
                st.info("No hay historial suficiente para graficar.")

# ==============================================================================
# PESTAÑA 3: COMPARACIÓN DUAL (HISTÓRICA)
# ==============================================================================
with tab_comparacion:
    st.header("⚖️ Comparación de Métricas y Tendencias Históricas")

    if len(empresas_seleccionadas) < 2:
        st.info("💡 Por favor, selecciona **dos** compañías en la barra lateral para ver la comparación histórica.")
    elif len(empresas_seleccionadas) == 2 and datos_empresas:
        comp1 = empresas_seleccionadas[0]
        comp2 = empresas_seleccionadas[1]
        data1 = datos_empresas.get(comp1)
        data2 = datos_empresas.get(comp2)

        if data1 and data2:
            st.subheader(f"Comparativa: {comp1} vs. {comp2}")

            # --- TABLA DE COMPARACIÓN (Último Año) ---
            st.markdown("##### 1. Métricas del Último Año Reportado")
            comparison_metrics = {
                'Métrica': ['Ingresos', 'Ganancia Neta', 'Margen Neto (%)', 'ROE (%)', 'ROA (%)', 'P/E Ratio'],
                comp1: [data1['Revenue'], data1['Net Income'], data1['Net Margin'], data1['ROE'], data1['ROA'], data1['PE Ratio']],
                comp2: [data2['Revenue'], data2['Net Income'], data2['Net Margin'], data2['ROE'], data2['ROA'], data2['PE Ratio']]
            }

            df_comp = pd.DataFrame(comparison_metrics)

            def format_metric_comp(row, col_name):
                value = row[col_name]
                label = str(row['Métrica'])
                # Porcentajes
                if ('(%' in label) or ('Porcentaje' in label) or ('%' in label):
                    return "-" if pd.isna(value) else f"{float(value):.2f}%"
                # P/E
                if 'P/E' in label:
                    return "-" if (pd.isna(value) or (not np.isfinite(value)) or (value <= 0)) else f"{float(value):.1f}x"
                # Moneda
                return "-" if pd.isna(value) else format_currency(value, 1)

            df_comp[comp1] = df_comp.apply(lambda row: format_metric_comp(row, comp1), axis=1)
            df_comp[comp2] = df_comp.apply(lambda row: format_metric_comp(row, comp2), axis=1)

            st.dataframe(df_comp.set_index('Métrica'), use_container_width=True)

            st.write("---")

            # --- GRÁFICO DE EVOLUCIÓN: Comparación Histórica de Revenue ---
            st.markdown("##### 2. Evolución del Revenue (Ingresos)")

            df_combined_hist = pd.concat([
                data1['historial_df'][['Year', 'Revenue', 'Company']],
                data2['historial_df'][['Year', 'Revenue', 'Company']]
            ], ignore_index=True)

            if not df_combined_hist.empty:
                fig_rev, ax_rev = plt.subplots(figsize=(10, 5))
                sns.lineplot(data=df_combined_hist, x='Year', y='Revenue', hue='Company', marker='o', ax=ax_rev)
                ax_rev.set_title("Evolución de Ingresos (Revenue)")
                ax_rev.set_ylabel("Revenue (M/B USD)")
                ax_rev.set_xlabel("Año")
                ax_rev.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig_rev)
            else:
                st.info("No hay datos suficientes para comparar Revenue.")

            st.write("---")

            # --- GRÁFICO DE COMPARACIÓN: Ratios (último año) ---
            st.markdown("##### 3. Comparación de Rentabilidad (Último Año)")

            df_chart = pd.DataFrame({
                'Empresa': [comp1, comp1, comp2, comp2],
                'Ratio': ['ROE', 'ROA', 'ROE', 'ROA'],
                'Valor': [data1['ROE'], data1['ROA'], data2['ROE'], data2['ROA']]
            })

            fig_ratios, ax_ratios = plt.subplots(figsize=(10, 5))
            sns.barplot(x='Empresa', y='Valor', hue='Ratio', data=df_chart, palette='viridis', ax=ax_ratios)
            ax_ratios.set_title("Rentabilidad (ROE y ROA)")
            ax_ratios.set_ylabel("Porcentaje (%)")
            st.pyplot(fig_ratios)

# ==============================================================================
# PESTAÑA 4: RESUMEN GLOBAL
# ==============================================================================
with tab_global:
    st.header("🌎 Resumen Global y Distribución de la Industria")

    if datos_globales is None or datos_globales.get('Total_Companies', 0) == 0:
        st.warning("No se pudieron procesar los datos globales.")
    else:
        st.info(f"Análisis basado en **{datos_globales['Total_Companies']}** compañías únicas en el archivo.")

        # --- KPI Global Cards ---
        st.markdown("##### Medianas de la Industria (Benchmark)")
        col_g1, col_g2, col_g3 = st.columns(3)

        with col_g1:
            st.metric("Mediana de Ingresos", format_currency(datos_globales['Revenue_Median'], 0))
            st.metric("Mediana de Ganancia Neta", format_currency(datos_globales['Net_Income_Median'], 0))

        with col_g2:
            st.metric("Mediana de Margen Bruto", format_percentage(datos_globales['Gross_Margin_Median']))
            st.metric("Mediana de Margen Neto", format_percentage(datos_globales['Net_Margin_Median']))

        with col_g3:
            st.metric("Mediana de ROE", format_percentage(datos_globales['ROE_Median']))
            st.metric("Mediana de ROA", format_percentage(datos_globales['ROA_Median']))

        st.write("---")

        # --- GRÁFICO DE CORRELACIÓN GLOBAL (HEATMAP) ---
        st.markdown("##### Matriz de Correlación de Variables Clave")

        df_corr = datos_globales['df_full'].copy()
        numerical_cols_corr = [
            'Revenue', 'Net Income', 'Gross Profit', 'Net Profit Margin',
            'ROE', 'ROA', 'Current Ratio', 'Debt/Equity Ratio', 'PE Ratio'
        ]
        # Solo columnas presentes
        cols_to_use = [col for col in numerical_cols_corr if col in df_corr.columns]

        if cols_to_use:
            corr_matrix = df_corr[cols_to_use].corr()
            fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
            sns.heatmap(
                corr_matrix,
                annot=True,
                cmap='coolwarm',
                fmt=".2f",
                linewidths=.5,
                cbar_kws={'label': 'Coeficiente de Correlación'},
                ax=ax_corr
            )
            ax_corr.set_title('Matriz de Correlación de Variables Financieras', fontsize=14)
            st.pyplot(fig_corr)
        else:
            st.info("No hay suficientes columnas numéricas para calcular correlaciones.")

# ==============================================================================
# PESTAÑA 5: EXPLICACIÓN DE MÉTRICAS FINANCIERAS
# ==============================================================================
with tab_info:
    st.header("📘 Explicación de Métricas Financieras")
    st.markdown("""
    A continuación se describen las principales métricas utilizadas en este panel:

    ### 💵 **Revenue (Ingresos Totales)**
    Representa el total de dinero generado por la empresa a través de sus ventas o servicios antes de restar los costos.  
    *Sirve para medir el tamaño de la empresa y su capacidad de generar ventas.*

    ### 💰 **Net Income (Utilidad Neta)**
    Es la ganancia final después de restar todos los costos, gastos e impuestos.  
    *Indica si la empresa es rentable o está generando pérdidas.*

    ### 📊 **Gross Margin (Margen Bruto)**
    Porcentaje de ingresos que queda tras cubrir los costos directos de producción.  
    *Refleja la eficiencia operativa y el control de costos.*

    ### 📈 **Net Profit Margin (Margen Neto)**
    Porcentaje de ingresos que se convierte en utilidad neta.  
    *Permite evaluar la rentabilidad general de la empresa.*

    ### 🧮 **ROE (Return on Equity / Rentabilidad sobre el Patrimonio)**
    Rentabilidad que obtienen los accionistas sobre su inversión.  
    *Mide qué tan bien la empresa utiliza el capital de los accionistas.*  
    **Fórmula:** ROE = Net Income / Equity × 100

    ### 💼 **ROA (Return on Assets / Rentabilidad sobre Activos)**
    Eficiencia para usar los activos y generar beneficios.  
    *Útil para comparar empresas de distinto tamaño.*  
    **Fórmula:** ROA = Net Income / Total Assets × 100

    ### ⚖️ **P/E Ratio (Price-to-Earnings)**
    Relación entre el valor de mercado y las ganancias netas.  
    *Aproxima cuántos años de utilidades recuperarían el precio pagado.*  
    **Nota:** no se muestra si la utilidad neta es ≤ 0.

    ### 🧾 **Debt/Equity Ratio (Relación Deuda/Capital)**
    Compara la deuda total con el patrimonio neto de los accionistas.  
    *Evalúa apalancamiento financiero y riesgo de endeudamiento.*  
    **Fórmula:** D/E = Total Debt / Total Equity

    ### 💧 **Current Ratio (Razón Corriente)**
    Compara los activos circulantes con los pasivos a corto plazo.  
    *Mide la capacidad para cubrir obligaciones inmediatas.*  
    **Fórmula:** Current Ratio = Current Assets / Current Liabilities
    """)

    st.success("✅ Estas métricas permiten interpretar la rentabilidad, eficiencia y estabilidad financiera de las compañías analizadas.")
