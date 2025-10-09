import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Configuración de rutas
INTERIM_CSV = Path("data") / "interim" / "dataset_clean.csv"
FIG_DIR = Path("docs") / "figures"

# Cargar los datos
df = pd.read_csv(INTERIM_CSV)

# Diccionario de mapeo entre las categorías del selectbox y las columnas del DataFrame
categoria_mapping = {
    "Alimentación": "Gasto_Alimentacion",
    "Transporte": "Gasto_Transporte",
    "Vivienda": "Gasto_Vivienda",
    "Ocio": "Gasto_Ocio",
    "Material Escolar": "Gasto_Material_Escolar",
    "Cuidado Personal": "Gasto_Cuidado_Personal",
    "Salud": "Gasto_Salud",
    "Tecnología": "Gasto_Tecnologia",
    "Miscelánea": "Gasto_Miscelanea"
}

# 1. Landing Page (Descripción del Proyecto)
def show_landing_page():
    st.title("Análisis Financiero de Estudiantes")
    st.subheader("Bienvenido al análisis interactivo de los datos financieros de los estudiantes")
    st.write("""
    Este proyecto tiene como objetivo analizar los ingresos, gastos y ahorros de los estudiantes, 
    proporcionando información útil para optimizar sus finanzas. Se ofrece una visión general de 
    las tendencias de los ingresos y gastos, distribuciones de categorías de gasto, y cómo los estudiantes 
    gestionan su ahorro.
    
    **Características principales:**
    - Análisis de tendencias entre ingresos y gastos.
    - Comparación entre la meta de ahorro y el balance real de los estudiantes.
    - Distribución de los gastos de los estudiantes por categorías (alimentación, vivienda, etc.).
    - Exploración de las fuentes de ingreso.
    - Visualización interactiva para un análisis más detallado.
    
    **Filtra los datos por:**
    - Rango de ingresos.
    - Categorías de gasto.
    - Meses y periodos específicos.
    """)

# 2. Dashboard Interactivo
def show_dashboard():
    st.sidebar.title("Filtros de Datos")

    # Filtros
    ingreso_min = st.sidebar.slider("Rango de Ingresos Mínimo", min_value=0, max_value=int(df['Total_Ingresos'].max()), value=0)
    ingreso_max = st.sidebar.slider("Rango de Ingresos Máximo", min_value=0, max_value=int(df['Total_Ingresos'].max()), value=int(df['Total_Ingresos'].max()))
    
    # Seleccionar la categoría de gasto
    categoria = st.sidebar.selectbox("Selecciona la categoría de gasto", list(categoria_mapping.keys()))

    # Filtrar los datos
    df_filtered = df[(df['Total_Ingresos'] >= ingreso_min) & (df['Total_Ingresos'] <= ingreso_max)]
    
    # Asegurarse de que la columna seleccionada en el selectbox coincida con el nombre de la columna en el DataFrame
    selected_column = categoria_mapping[categoria]
    df_filtered = df_filtered[df_filtered[selected_column] > 0]

    st.write(f"Mostrando datos filtrados: Ingresos entre {ingreso_min} y {ingreso_max}, categoría de gasto: {categoria}")

    # Mostrar Resúmenes
    st.subheader("Resumen de los Datos")
    st.write(f"Total de estudiantes: {len(df_filtered)}")
    st.write(f"Ingreso promedio: {df_filtered['Total_Ingresos'].mean():.2f}")
    st.write(f"Gasto promedio: {df_filtered['Total_Gastos'].mean():.2f}")

    # Visualizaciones Interactivas
    plot_income_vs_expenses(df_filtered)
    plot_expenses_distribution(df_filtered)
    plot_savings_vs_income(df_filtered)
    plot_income_sources(df_filtered)

# Función para mostrar el gráfico de ingresos vs gastos
def plot_income_vs_expenses(df):
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.scatter(df['Total_Ingresos'], df['Total_Gastos'], color='blue', alpha=0.5)
    ax1.set_title('Ingresos vs Gastos Totales por Estudiante')
    ax1.set_xlabel('Ingresos Totales')
    ax1.set_ylabel('Gastos Totales')
    ax1.grid(True)
    st.pyplot(fig1)

# 4. Distribución de Gastos (Pie Chart)
def plot_expenses_distribution(df):
    # Categorías de gastos
    categories = ['Gasto_Alimentacion', 'Gasto_Transporte', 'Gasto_Vivienda', 'Gasto_Matricula', 
                  'Gasto_Material_Escolar', 'Gasto_Ocio', 'Gasto_Cuidado_Personal', 'Gasto_Salud', 
                  'Gasto_Tecnologia', 'Gasto_Miscelanea']
    
    # Sumar los gastos por categoría
    total_gastos_por_categoria = df[categories].sum()

    # Crear gráfico de pastel
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    total_gastos_por_categoria.plot(kind='pie', ax=ax2, autopct='%1.1f%%', startangle=90, colormap='tab10')
    ax2.set_title('Distribución Porcentual de Gastos por Categoría')
    ax2.set_ylabel('')  # Eliminar la etiqueta del eje y (por defecto)
    ax2.legend(title="Categorías de Gasto", bbox_to_anchor=(1.05, 1), loc='upper left')  # Leyenda a la derecha
    st.pyplot(fig2)

# 5. Ahorro vs Ingresos
def plot_savings_vs_income(df):
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    ax3.bar(df['Nombre'], df['Monto_Meta_Ahorro'], label='Meta de Ahorro', alpha=0.7)  # Cambié 'Meta_Ahorro' por 'Monto_Meta_Ahorro'
    ax3.bar(df['Nombre'], df['Diferencia_Ingresos_Gastos'], label='Balance', alpha=0.7)  # Cambié 'Balance' por 'Diferencia_Ingresos_Gastos'
    ax3.set_xticklabels(df['Nombre'], rotation=90)
    ax3.set_title('Comparación entre Meta de Ahorro y Balance de Estudiantes')
    ax3.set_xlabel('Estudiantes')
    ax3.set_ylabel('Monto (en unidades monetarias)')
    ax3.legend()
    st.pyplot(fig3)

# 6. Fuentes de Ingreso
def plot_income_sources(df):
    fig4, ax4 = plt.subplots(figsize=(8, 8))
    income_sources = ['Ingreso_Beca', 'Ingreso_Trabajo', 'Ingreso_Apoyo_Familiar']
    df[income_sources].sum().plot(kind='pie', ax=ax4, autopct='%1.1f%%', startangle=90)
    ax4.set_title('Distribución de Fuentes de Ingreso por Estudiante')
    ax4.set_ylabel('')
    st.pyplot(fig4)

# 7. Mostrar Landing Page y Dashboard
if __name__ == "__main__":
    show_landing_page()
    if st.button("Ver Dashboard"):
        show_dashboard()
