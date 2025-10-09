import matplotlib.pyplot as plt
import pandas as pd
from config import FIG_DIR
from pathlib import Path

# Cargar los datos limpios
df_cleaned = pd.read_csv(Path("data") / "interim" / "dataset_clean.csv")

# 1. Tendencias de Ingresos vs Gastos
def plot_income_vs_expenses(df):
    plt.figure(figsize=(10, 6))
    plt.scatter(df['Total_Ingresos'], df['Total_Gastos'], color='blue', alpha=0.5)
    plt.title('Ingresos vs Gastos Totales por Estudiante')
    plt.xlabel('Ingresos Totales')
    plt.ylabel('Gastos Totales')
    plt.grid(True)
    plt.savefig(FIG_DIR / 'ingresos_vs_gastos.png')
    plt.close()

# 2. Distribución de Gastos (Gráfico de barras apiladas y pie chart)
def plot_expenses_distribution(df):
    # Gastos por categorías
    categories = ['Gasto_Alimentacion', 'Gasto_Transporte', 'Gasto_Vivienda', 'Gasto_Matricula', 
                  'Gasto_Material_Escolar', 'Gasto_Ocio', 'Gasto_Cuidado_Personal', 'Gasto_Salud', 
                  'Gasto_Tecnologia', 'Gasto_Miscelanea']
    
    # Gráfico de barras apiladas
    df[categories].plot(kind='bar', stacked=True, figsize=(12, 8), colormap='tab10')
    plt.title('Distribución de Gastos por Categoría')
    plt.xlabel('Estudiantes')
    plt.ylabel('Monto en Gastos')
    plt.legend(title="Categorías de Gasto", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'distribucion_gastos_barras_apiladas.png')
    plt.close()

    # Gráfico de pie chart de los gastos totales por categoría
    total_gastos_por_categoria = df[categories].sum()
    total_gastos_por_categoria.plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%', startangle=90)
    plt.title('Distribución Porcentual de Gastos Totales')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'distribucion_gastos_pie_chart.png')
    plt.close()

# 3. Ahorro vs Ingresos (Comparación entre la Meta de Ahorro y el Balance)
def plot_savings_vs_income(df):
    plt.figure(figsize=(10, 6))
    plt.bar(df['Nombre'], df['Meta_Ahorro'], label='Meta de Ahorro', alpha=0.7)
    plt.bar(df['Nombre'], df['Balance'], label='Balance', alpha=0.7)
    plt.xticks(rotation=90)
    plt.title('Comparación entre Meta de Ahorro y Balance de Estudiantes')
    plt.xlabel('Estudiantes')
    plt.ylabel('Monto (en unidades monetarias)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'ahorro_vs_balance.png')
    plt.close()

# 4. Análisis de Categorías de Ingreso (Pie chart de fuentes de ingresos)
def plot_income_sources(df):
    income_sources = ['Ingreso_Beca', 'Ingreso_Trabajo', 'Ingreso_Apoyo_Familiar']
    df[income_sources].sum().plot(kind='pie', figsize=(8, 8), autopct='%1.1f%%', startangle=90)
    plt.title('Distribución de Fuentes de Ingreso por Estudiante')
    plt.ylabel('')
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'distribucion_fuentes_ingreso.png')
    plt.close()

# Función para generar todas las gráficas
def generate_plots(df):
    plot_income_vs_expenses(df)
    plot_expenses_distribution(df)
    plot_savings_vs_income(df)
    plot_income_sources(df)

# Ejecutar todas las funciones
generate_plots(df_cleaned)

# Mensaje de éxito
"Gráficos generados correctamente en la carpeta 'docs/figures/'"
