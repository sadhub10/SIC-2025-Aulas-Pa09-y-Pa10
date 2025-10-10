import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


# ==========================================================
# 🧩 MODELO PREDICTIVO
# ==========================================================
class ModeloPredictivoHeadway: # Modelo predictivo basado en estadísticas históricas. Predice el tiempo de espera (headway) entre buses.      
    def __init__(self, ruta_eventos: str):
        ruta_eventos = Path(ruta_eventos).resolve()
        if not ruta_eventos.exists():
            raise FileNotFoundError(
                f"⚠️ No se encontró el archivo {ruta_eventos}\n"
                f"   → Ejecuta primero 'generate_events.py' para generarlo."
            )
        
        print("\n🔄 Cargando datos para entrenamiento...")
        self.df_eventos = pd.read_csv(ruta_eventos, parse_dates=['marca_tiempo'])
        if self.df_eventos.empty:
            raise ValueError("⚠️ El archivo de eventos está vacío. No se puede entrenar el modelo.")
        
        self.modelo_entrenado = None
        self.metricas = {}
        
    def entrenar_modelo(self) -> Dict: #Entrena el modelo usando estadísticas agrupadas. Calcula promedios por ruta, hora, tipo de día y tipo de ruta.
        print("\n🎯 Entrenando modelo predictivo...")
        print("   Método: Promedios estadísticos por contexto")
        
        # Verificar si tipo_ruta existe
        columnas_agrupacion = ['id_ruta', 'hora', 'es_fin_semana', 'es_hora_pico']
        if 'tipo_ruta' in self.df_eventos.columns:
            columnas_agrupacion.append('tipo_ruta')
            print("   • Usando tipo_ruta en el modelo")
        else:
            print("   ⚠️ tipo_ruta no disponible, usando solo ruta/hora/día")
        
        # Agrupar por características clave
        self.modelo_entrenado = self.df_eventos.groupby(
            columnas_agrupacion
        )['intervalo_min'].agg(['mean', 'std', 'count']).reset_index()
        
        # Renombrar columnas dinámicamente
        nuevas_columnas = columnas_agrupacion + ['intervalo_predicho', 'desviacion', 'num_observaciones']
        self.modelo_entrenado.columns = nuevas_columnas
        self.usa_tipo_ruta = 'tipo_ruta' in columnas_agrupacion
        
        # Filtrar grupos con pocas observaciones
        self.modelo_entrenado = self.modelo_entrenado[
            self.modelo_entrenado['num_observaciones'] >= 2
        ]
        
        # Calcular fallback (promedio general)
        self.fallback_ruta = self.df_eventos.groupby('id_ruta')['intervalo_min'].mean().to_dict()
        self.fallback_global = self.df_eventos['intervalo_min'].mean()
        
        # Calcular métricas
        total_combinaciones = len(self.modelo_entrenado)
        cobertura = (total_combinaciones / len(self.df_eventos)) * 100
        
        self.metricas = {
            'total_eventos_entrenamiento': len(self.df_eventos),
            'total_patrones': total_combinaciones,
            'cobertura': cobertura,
            'rutas_unicas': self.df_eventos['id_ruta'].nunique(),
            'intervalo_promedio': self.df_eventos['intervalo_min'].mean(),
            'desviacion_promedio': self.df_eventos['intervalo_min'].std()
        }
        
        print(f"\n✅ Modelo entrenado exitosamente")
        print(f"   • Eventos de entrenamiento: {self.metricas['total_eventos_entrenamiento']:,}")
        print(f"   • Patrones identificados: {self.metricas['total_patrones']:,}")
        print(f"   • Rutas cubiertas: {self.metricas['rutas_unicas']}")
        print(f"   • Intervalo promedio: {self.metricas['intervalo_promedio']:.2f} min")
        
        return self.metricas
    
    def predecir(self, id_ruta: str, hora: int, es_fin_semana: bool, #predice el intervalo de espera para una ruta, hora y tipo de día específicos.
                 tipo_ruta: str = 'urbana') -> Dict:

        if self.modelo_entrenado is None:
            raise ValueError("Modelo no entrenado. Ejecuta entrenar_modelo() primero.")
        
        # Determinar si es hora pico
        es_hora_pico = (6 <= hora <= 9) or (17 <= hora <= 20)
        
        # Construir condiciones de búsqueda
        condiciones_exactas = (
            (self.modelo_entrenado['id_ruta'] == id_ruta) &
            (self.modelo_entrenado['hora'] == hora) &
            (self.modelo_entrenado['es_fin_semana'] == es_fin_semana) &
            (self.modelo_entrenado['es_hora_pico'] == es_hora_pico)
        )
        
        # Agregar tipo_ruta si está disponible
        if self.usa_tipo_ruta and tipo_ruta:
            condiciones_exactas = condiciones_exactas & (self.modelo_entrenado['tipo_ruta'] == tipo_ruta)
        
        # Buscar predicción exacta
        prediccion = self.modelo_entrenado[condiciones_exactas]
        
        if len(prediccion) > 0:
            pred = prediccion.iloc[0]
            num_obs = int(pred['num_observaciones'])
            
            if num_obs >= 10:
                confianza = 'Muy Alta'
            elif num_obs >= 5:
                confianza = 'Alta'
            else:
                confianza = 'Media-Alta'
            
            return {
                'intervalo_predicho': round(pred['intervalo_predicho'], 2),
                'desviacion': round(pred['desviacion'], 2),
                'confianza': confianza,
                'num_observaciones': num_obs,
                'metodo': 'Patrón específico'
            }
        
        # Fallbacks (predicciones aproximadas)
        prediccion_ruta_hora = self.modelo_entrenado[
            (self.modelo_entrenado['id_ruta'] == id_ruta) &
            (self.modelo_entrenado['hora'] == hora)
        ]
        if len(prediccion_ruta_hora) > 0:
            pred = prediccion_ruta_hora.iloc[0]
            num_obs = int(pred['num_observaciones'])
            confianza = 'Alta' if num_obs >= 8 else 'Media-Alta' if num_obs >= 5 else 'Media'
            return {
                'intervalo_predicho': round(pred['intervalo_predicho'], 2),
                'desviacion': round(pred['desviacion'], 2),
                'confianza': confianza,
                'num_observaciones': num_obs,
                'metodo': 'Promedio ruta-hora'
            }
        
        horas_cercanas = [hora - 1, hora + 1]
        prediccion_cercana = self.modelo_entrenado[
            (self.modelo_entrenado['id_ruta'] == id_ruta) &
            (self.modelo_entrenado['hora'].isin(horas_cercanas))
        ]
        if len(prediccion_cercana) > 0:
            pred = prediccion_cercana.iloc[0]
            num_obs = int(pred['num_observaciones'])
            return {
                'intervalo_predicho': round(pred['intervalo_predicho'], 2),
                'desviacion': round(pred['desviacion'], 2),
                'confianza': 'Media',
                'num_observaciones': num_obs,
                'metodo': 'Hora cercana'
            }
        
        if id_ruta in self.fallback_ruta:
            return {
                'intervalo_predicho': round(self.fallback_ruta[id_ruta], 2),
                'desviacion': None,
                'confianza': 'Media-Baja',
                'num_observaciones': None,
                'metodo': 'Promedio ruta'
            }
        
        return {
            'intervalo_predicho': round(self.fallback_global, 2),
            'desviacion': None,
            'confianza': 'Baja',
            'num_observaciones': None,
            'metodo': 'Promedio global'
        }

    def predecir_multiple(self, id_ruta: str, fecha: str, tipo_ruta: str = 'urbana') -> pd.DataFrame: #Predice intervalos para todas las horas de un día específico.
        try:
            fecha_dt = pd.to_datetime(fecha)
            es_fin_semana = fecha_dt.weekday() >= 5
        except:
            es_fin_semana = fecha.lower() in ['sabado', 'sábado', 'domingo']
        
        predicciones = []
        for hora in range(24):
            pred = self.predecir(id_ruta, hora, es_fin_semana, tipo_ruta)
            predicciones.append({
                'hora': hora,
                'intervalo_predicho': pred['intervalo_predicho'],
                'desviacion': pred['desviacion'],
                'confianza': pred['confianza']
            })
        return pd.DataFrame(predicciones)


# ==========================================================
# 📊 EVALUADOR DEL MODELO
# ==========================================================
class EvaluadorModelo: #Evalúa el rendimiento del modelo predictivo.
    
    def __init__(self, modelo: ModeloPredictivoHeadway):
        self.modelo = modelo
        self.resultados_evaluacion = None

    def evaluar(self, muestra_size: int = 1000) -> Dict: #Evalúa el modelo usando una muestra de datos.
        if self.modelo.df_eventos.empty:
            print("⚠️ No hay datos disponibles para evaluar el modelo.")
            return {'mae': None, 'rmse': None, 'mape': None, 'mensaje': 'Sin datos'}
        
        print(f"\n📊 Evaluando modelo con {muestra_size} muestras...")
        df_muestra = self.modelo.df_eventos.sample(
            n=min(muestra_size, len(self.modelo.df_eventos)),
            random_state=42
        )
        
        predicciones, valores_reales, confianzas = [], [], []
        for _, row in df_muestra.iterrows():
            pred = self.modelo.predecir(row['id_ruta'], row['hora'], row['es_fin_semana'], row.get('tipo_ruta', 'urbana'))
            predicciones.append(pred['intervalo_predicho'])
            valores_reales.append(row['intervalo_min'])
            confianzas.append(pred['confianza'])
        
        predicciones = np.array(predicciones)
        valores_reales = np.array(valores_reales)
        
        mae = np.mean(np.abs(predicciones - valores_reales))
        rmse = np.sqrt(np.mean((predicciones - valores_reales) ** 2))
        mape = np.mean(np.abs((valores_reales - predicciones) / valores_reales)) * 100
        
        confianza_counts = pd.Series(confianzas).value_counts().to_dict()
        
        self.resultados_evaluacion = {
            'mae': mae,
            'rmse': rmse,
            'mape': mape,
            'total_predicciones': len(predicciones),
            'distribucion_confianza': confianza_counts
        }
        
        print(f"\n✅ Evaluación completada")
        print(f"   • MAE: {mae:.2f} min")
        print(f"   • RMSE: {rmse:.2f} min")
        print(f"   • MAPE: {mape:.2f}%")
        print("\n   • Distribución de confianza:")
        for nivel, count in confianza_counts.items():
            print(f"     - {nivel}: {count} ({count/len(predicciones)*100:.1f}%)")
        
        return self.resultados_evaluacion


# ==========================================================
# 🔮 INTERFAZ PRINCIPAL
# ==========================================================
class PredictorHeadway:
    """Interfaz principal para usar el sistema de predicción."""
    
    def __init__(self, ruta_eventos: str, ruta_resumen: str):
        self.ruta_eventos = Path(ruta_eventos).resolve()
        self.ruta_resumen = Path(ruta_resumen).resolve()

        if not self.ruta_eventos.exists():
            raise FileNotFoundError(f"⚠️ No se encontró {self.ruta_eventos}")
        if not self.ruta_resumen.exists():
            raise FileNotFoundError(f"⚠️ No se encontró {self.ruta_resumen}")
        
        self.df_resumen = pd.read_csv(self.ruta_resumen)
        self.modelo = None
        self.evaluador = None
    
    def preparar_modelo(self) -> Dict: #Prepara y entrena el modelo predictivo.
        print("\n" + "="*60)
        print("PREPARACIÓN DEL MODELO PREDICTIVO")
        print("="*60)
        
        self.modelo = ModeloPredictivoHeadway(self.ruta_eventos)
        metricas_entrenamiento = self.modelo.entrenar_modelo()
        
        self.evaluador = EvaluadorModelo(self.modelo)
        metricas_evaluacion = self.evaluador.evaluar(muestra_size=1000)
        
        print("\n" + "="*60)
        print("MODELO LISTO PARA USAR")
        print("="*60)
        
        return {'entrenamiento': metricas_entrenamiento, 'evaluacion': metricas_evaluacion}
    
    def obtener_rutas_disponibles(self, limite: int = 20) -> pd.DataFrame: #Obtiene las rutas con más eventos registrados.
        return self.df_resumen.nlargest(limite, 'num_eventos')[
            ['id_ruta', 'nombre_ruta', 'tipo_ruta', 'num_eventos', 'intervalo_promedio']
        ]
    
    def predecir_intervalo(self, id_ruta: str, hora: int, es_fin_semana: bool) -> Dict: 
        if self.modelo is None:
            raise ValueError("Modelo no preparado. Ejecuta preparar_modelo() primero.")
        
        ruta_info = self.df_resumen[self.df_resumen['id_ruta'] == id_ruta]
        tipo_ruta = ruta_info.iloc[0].get('tipo_ruta', 'urbana') if len(ruta_info) > 0 else 'urbana'
        prediccion = self.modelo.predecir(id_ruta, hora, es_fin_semana, tipo_ruta)
        
        if len(ruta_info) > 0:
            prediccion['nombre_ruta'] = ruta_info.iloc[0]['nombre_ruta']
            prediccion['tipo_ruta'] = tipo_ruta
        return prediccion
    
    def predecir_dia_completo(self, id_ruta: str, tipo_dia: str = 'laboral') -> pd.DataFrame: #Predice intervalos para todas las horas de un día específico.
        if self.modelo is None:
            raise ValueError("Modelo no preparado. Ejecuta preparar_modelo() primero.")
        
        es_fin_semana = tipo_dia.lower() in ['sabado', 'sábado', 'domingo']
        ruta_info = self.df_resumen[self.df_resumen['id_ruta'] == id_ruta]
        tipo_ruta = ruta_info.iloc[0].get('tipo_ruta', 'urbana') if len(ruta_info) > 0 else 'urbana'
        predicciones = self.modelo.predecir_multiple(id_ruta, tipo_dia, tipo_ruta)
        return predicciones, (ruta_info.iloc[0]['nombre_ruta'] if len(ruta_info) > 0 else 'Desconocida')

