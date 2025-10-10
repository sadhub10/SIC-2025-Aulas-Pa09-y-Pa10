# Archivo especifico para las visualizaciones del proyecto
import pandas as pd 
import plotly.express as px

# Agregare algunas de prueba (Elvis Adames)
def grafico_tendencia_temporal(df):
    """Genera un gráfico de tendencia temporal de los delitos."""
    
    # columna periodo (año-mes)
    df['periodo'] = df['año'].astype(str) + '-' + df['mes'].astype(str).str.zfill(2)
    
    # Agrupacion por periodo y sexo
    df_temp = df.groupby(['periodo', 'sexo', 'año', 'mes']).size().reset_index(name='cantidad')
    
    # Ordenamiento por año y mes
    df_temp = df_temp.sort_values(['año', 'mes'])
    
    # Mapeo de colores
    color_discrete_map = {
        'Masculino': 'blue',
        'Femenino': 'red',
        'No disponible': 'green'
    }
    
    fig = px.line(
        df_temp,
        x='periodo',
        y='cantidad',
        color='sexo',
        title='Tendencia Temporal de Delitos por Sexo',
        labels= {'periodo': 'Periodo (Año-Mes)', 'cantidad': 'Número de Delitos', 'sexo': 'Sexo'},
        color_discrete_map= color_discrete_map
    )
    
    fig.update_layout(
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return fig

def grafico_proporcion_sexo(df):
    """Crea gráfico de proporción por sexo"""
    df_sexo = df['sexo'].value_counts().reset_index()
    df_sexo.columns = ['sexo', 'cantidad']
    
    fig = px.pie(
        df_sexo,
        values='cantidad',
        names='sexo',
        title='⚖️ Proporción de Víctimas por Sexo',
        color='sexo',
        color_discrete_map={'Masculino': '#1f77b4', 'Femenino': '#e377c2'},
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

def grafico_arma_barras(df):
    """Crea gráfico de barras alternativo para armas"""
    df_arma = df['tipo_de_arma_utilizada'].value_counts().head(10).reset_index()
    df_arma.columns = ['arma', 'cantidad']
    df_arma = df_arma.sort_values('cantidad', ascending=True)
    
    fig = px.bar(
        df_arma,
        x='cantidad',
        y='arma',
        orientation='h',
        title='Tipos de Armas Utilizadas',
        labels={'cantidad': 'Número de Casos', 'arma': 'Tipo de Arma'},
        color='cantidad',
        color_continuous_scale='Oranges'
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig
