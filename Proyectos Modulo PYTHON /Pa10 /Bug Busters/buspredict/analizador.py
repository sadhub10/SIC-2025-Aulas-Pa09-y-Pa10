import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict
import numpy as np


class AnalizadorDescriptivo: #Realiza análisis descriptivo y genera gráficos a partir de datos de eventos de buses.
    
    def __init__(self, ruta_eventos: str, ruta_resumen: str): #Inicializa el analizador con rutas a archivos de eventos y resumen.
        ruta_eventos = Path(ruta_eventos)
        ruta_resumen = Path(ruta_resumen)

        if not ruta_eventos.exists():
            raise FileNotFoundError(f"❌ No se encontró el archivo de eventos: {ruta_eventos}")
        if not ruta_resumen.exists():
            raise FileNotFoundError(f"❌ No se encontró el archivo de resumen: {ruta_resumen}")
        
        self.df_eventos = pd.read_csv(ruta_eventos, parse_dates=['marca_tiempo'])
        self.df_resumen = pd.read_csv(ruta_resumen)

        # Verificar columnas mínimas necesarias
        columnas_requeridas = ['hora', 'intervalo_min', 'pasajeros', 'es_fin_semana']
        for col in columnas_requeridas:
            if col not in self.df_eventos.columns:
                self.df_eventos[col] = np.nan
        
        # Directorio para guardar gráficos
        self.ruta_graficos = Path("results/graficos")
        self.ruta_graficos.mkdir(parents=True, exist_ok=True)
        
        # Estilo visual
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
    
    # --------------------------------------------------------------
    def distribucion_por_hora(self, guardar: bool = True) -> Dict:
        print("\n📊 Analizando distribución por hora...")

        if 'hora' not in self.df_eventos.columns:
            print("⚠️ No hay columna 'hora' en los datos.")
            return {}
        
        eventos_por_hora = self.df_eventos.groupby('hora').size()
        if eventos_por_hora.empty:
            print("⚠️ No hay datos para generar la distribución por hora.")
            return {}

        umbral_pico = eventos_por_hora.quantile(0.75)
        horas_pico = eventos_por_hora[eventos_por_hora >= umbral_pico].index.tolist()
        promedio = eventos_por_hora.mean()

        fig, ax = plt.subplots(figsize=(14, 6))
        colores = ['#e74c3c' if hora in horas_pico else '#3498db' for hora in eventos_por_hora.index]
        ax.bar(eventos_por_hora.index, eventos_por_hora.values, color=colores)
        ax.axhline(y=promedio, color='green', linestyle='--', label=f'Promedio: {promedio:.0f}')
        ax.set_title('Distribución de Eventos por Hora (rojo = hora pico)', fontsize=14, fontweight='bold')
        ax.set_xlabel('Hora del día')
        ax.set_ylabel('Cantidad de eventos')
        ax.legend()
        plt.tight_layout()

        if guardar:
            ruta = self.ruta_graficos / "distribucion_por_hora.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            print(f"   ✓ Gráfico guardado: {ruta}")
        plt.close(fig)

        return {
            'eventos_por_hora': eventos_por_hora.to_dict(),
            'horas_pico': horas_pico,
            'hora_mas_activa': int(eventos_por_hora.idxmax()),
            'hora_menos_activa': int(eventos_por_hora.idxmin()),
            'promedio_eventos': float(promedio)
        }

    # --------------------------------------------------------------
    def comparativa_dias(self, guardar: bool = True) -> Dict: #Compara la operación entre días laborales y fines de semana.
        print("\n📅 Comparando días laborales vs fin de semana...")
        if 'es_fin_semana' not in self.df_eventos.columns:
            print("⚠️ No hay columna 'es_fin_semana' en los datos.")
            return {}

        datos = self.df_eventos.groupby('es_fin_semana')
        if datos.size().empty:
            print("⚠️ No hay datos suficientes para comparar días.")
            return {}

        stats = datos.agg({'intervalo_min': ['mean', 'median', 'std'],
                           'pasajeros': ['mean', 'sum'],
                           'marca_tiempo': 'count'}).round(2)

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        etiquetas = ['Días Laborales', 'Fin de Semana']
        colores_bar = ['#3498db', '#e74c3c']
        
        datos_intervalo = self.df_eventos.groupby('es_fin_semana')['intervalo_min'].mean()
        datos_eventos = self.df_eventos.groupby('es_fin_semana').size()

        axes[0].bar(etiquetas, datos_intervalo.values, color=colores_bar)
        axes[0].set_title('Intervalo promedio')
        axes[1].bar(etiquetas, datos_eventos.values, color=colores_bar)
        axes[1].set_title('Cantidad de eventos')
        plt.tight_layout()

        if guardar:
            ruta = self.ruta_graficos / "comparativa_dias.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            print(f"   ✓ Gráfico guardado: {ruta}")
        plt.close(fig)

        return {
            'intervalo_laboral': float(datos_intervalo.iloc[0]),
            'intervalo_fin_semana': float(datos_intervalo.iloc[1]),
            'eventos_laboral': int(datos_eventos.iloc[0]),
            'eventos_fin_semana': int(datos_eventos.iloc[1])
        }

    # --------------------------------------------------------------
    def rutas_mas_transitadas(self, top_n: int = 10, guardar: bool = True) -> pd.DataFrame: #Identifica las rutas con mayor demanda.
        print(f"\n🚏 Analizando top {top_n} rutas más transitadas...")
        if 'pasajeros_totales' not in self.df_resumen.columns:
            print("⚠️ El archivo resumen no contiene la columna 'pasajeros_totales'.")
            return pd.DataFrame()

        top_rutas = self.df_resumen.nlargest(top_n, 'pasajeros_totales')[
            ['id_ruta', 'nombre_ruta', 'pasajeros_totales', 'num_eventos', 'pasajeros_promedio']
        ]

        fig, ax = plt.subplots(figsize=(12, 8))
        nombres = [n[:50] + '...' if len(n) > 50 else n for n in top_rutas['nombre_ruta']]
        y = np.arange(len(nombres))
        colores = plt.cm.YlOrRd(np.linspace(0.9, 0.3, len(y)))
        ax.barh(y, top_rutas['pasajeros_totales'], color=colores)
        ax.set_yticks(y)
        ax.set_yticklabels(nombres)
        ax.invert_yaxis()
        ax.set_xlabel('Total de pasajeros')
        ax.set_title('Top Rutas Más Transitadas')
        plt.tight_layout()

        if guardar:
            ruta = self.ruta_graficos / "top_rutas_transitadas.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            print(f"   ✓ Gráfico guardado: {ruta}")
        plt.close(fig)

        return top_rutas

    # --------------------------------------------------------------
    def intervalos_por_ruta(self, top_n: int = 15, guardar: bool = True) -> pd.DataFrame: #Analiza las rutas con menor intervalo promedio.
        print(f"\n🕒 Analizando top {top_n} rutas más rápidas...")
        if 'intervalo_promedio' not in self.df_resumen.columns:
            print("⚠️ El archivo resumen no contiene la columna 'intervalo_promedio'.")
            return pd.DataFrame()

        rutas = self.df_resumen[self.df_resumen['num_eventos'] >= 500]
        top = rutas.nsmallest(top_n, 'intervalo_promedio')[
            ['id_ruta', 'nombre_ruta', 'intervalo_promedio', 'intervalo_desviacion', 'num_eventos']
        ]

        fig, ax = plt.subplots(figsize=(14, 9))
        nombres = [n[:45] + '...' if len(n) > 45 else n for n in top['nombre_ruta']]
        y = np.arange(len(nombres))
        intervalos = top['intervalo_promedio']
        colores = plt.cm.RdYlGn_r(np.linspace(0, 1, len(y)))
        ax.barh(y, intervalos, color=colores)
        ax.set_yticks(y)
        ax.set_yticklabels(nombres)
        ax.invert_yaxis()
        ax.set_xlabel('Intervalo promedio (minutos)')
        ax.set_title('Rutas con menor tiempo de espera')
        plt.tight_layout()

        if guardar:
            ruta = self.ruta_graficos / "intervalos_por_ruta.png"
            plt.savefig(ruta, dpi=300, bbox_inches='tight')
            print(f"   ✓ Gráfico guardado: {ruta}")
        plt.close(fig)

        return top

    # --------------------------------------------------------------
    def generar_reporte_completo(self) -> Dict: #Ejecuta todos los análisis y genera gráficos.
        print("\n" + "="*60)
        print("📊 GENERANDO ANÁLISIS DESCRIPTIVO COMPLETO")
        print("="*60)

        resultados = {
            'distribucion_hora': self.distribucion_por_hora(),
            'comparativa_dias': self.comparativa_dias(),
            'top_rutas': self.rutas_mas_transitadas(),
            'intervalos': self.intervalos_por_ruta()
        }

        print("\n✅ ANÁLISIS COMPLETADO")
        print(f"📁 Gráficos guardados en: {self.ruta_graficos.resolve()}")
        return resultados
