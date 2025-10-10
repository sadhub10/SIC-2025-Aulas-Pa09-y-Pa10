import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from datetime import datetime
import os


class DatosManager:
    """Clase para manejar todas las operaciones de datos"""
    
    def __init__(self, archivo_csv="dataset_cultivos_panama.csv", barra_estado=None):
        self.archivo_csv = archivo_csv
        self.barra_estado = barra_estado
        self.df = self.cargar_dataset()
    
    def cargar_dataset(self):
        """Carga el dataset de cultivos desde el CSV"""
        try:
            df = pd.read_csv(self.archivo_csv)
            print(f"Dataset cargado: {len(df)} cultivos disponibles")
            if self.barra_estado:
                self.barra_estado.config(text=f"Dataset cargado: {len(df)} cultivos")
            return df
        except Exception as e:
            print(f"Error cargando dataset: {e}")
            if self.barra_estado:
                self.barra_estado.config(text="Error cargando dataset")
            return pd.DataFrame()
    
    def recargar_dataset(self):
        """Recarga el dataset desde el archivo"""
        self.df = self.cargar_dataset()
        return self.df
    
    def buscar_cultivo(self, nombre_cultivo):
        """Busca un cultivo específico en el dataset"""
        if not nombre_cultivo:
            return None
        
        # Buscar en el dataframe (case insensitive)
        resultado = self.df[self.df['cultivo'].str.lower() == nombre_cultivo.lower()]
        
        if not resultado.empty:
            return resultado.iloc[0]
        else:
            return None
    
    def obtener_lista_cultivos(self):
        """Obtiene la lista completa de cultivos disponibles"""
        if not self.df.empty:
            return sorted(self.df['cultivo'].tolist())
        return []
    
    def filtrar_por_temporada(self, temporada):
        """Filtra cultivos por temporada de siembra"""
        if not temporada:
            return self.df
        
        return self.df[self.df['temporada_siembra'].str.lower() == temporada.lower()]
    
    def filtrar_por_lluvia(self, nivel_lluvia):
        """Filtra cultivos por nivel de lluvia requerido"""
        if not nivel_lluvia:
            return self.df
        
        return self.df[self.df['lluvia'].str.lower() == nivel_lluvia.lower()]
    
    def filtrar_por_rendimiento(self, min_rendimiento=None, max_rendimiento=None):
        """Filtra cultivos por rango de rendimiento"""
        df_filtrado = self.df.copy()
        
        # Agregar columna numérica de rendimiento si no existe
        if 'rendimiento_numerico' not in df_filtrado.columns:
            df_filtrado['rendimiento_numerico'] = df_filtrado['rendimiento_promedio'].apply(
                lambda x: self._extraer_valor_numerico(x)
            )
        
        if min_rendimiento is not None:
            df_filtrado = df_filtrado[df_filtrado['rendimiento_numerico'] >= min_rendimiento]
        
        if max_rendimiento is not None:
            df_filtrado = df_filtrado[df_filtrado['rendimiento_numerico'] <= max_rendimiento]
        
        return df_filtrado
    
    def _extraer_valor_numerico(self, texto):
        """Extrae el valor numérico de un texto (ej: '25.0 t/ha' -> 25.0)"""
        try:
            return float(str(texto).split()[0])
        except:
            return 0.0
    
    def obtener_estadisticas_generales(self):
        """Calcula estadísticas generales del dataset"""
        try:
            # Preparar datos numéricos
            rendimientos = []
            tiempos = []
            
            for _, fila in self.df.iterrows():
                try:
                    rend = self._extraer_valor_numerico(fila['rendimiento_promedio'])
                    tiempo = int(fila['tiempo_cosecha'].split('-')[0])
                    rendimientos.append(rend)
                    tiempos.append(tiempo)
                except:
                    continue
            
            stats = {
                'total_cultivos': len(self.df),
                'rendimiento_promedio': np.mean(rendimientos) if rendimientos else 0,
                'rendimiento_max': np.max(rendimientos) if rendimientos else 0,
                'rendimiento_min': np.min(rendimientos) if rendimientos else 0,
                'tiempo_promedio': np.mean(tiempos) if tiempos else 0,
                'tiempo_max': np.max(tiempos) if tiempos else 0,
                'tiempo_min': np.min(tiempos) if tiempos else 0,
            }
            
            # Estadísticas por categorías
            stats['por_temporada'] = self.df['temporada_siembra'].value_counts().to_dict()
            stats['por_lluvia'] = self.df['lluvia'].value_counts().to_dict()
            
            return stats
            
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
            return {}
    
    def mostrar_dataset(self, root):
        """Muestra el dataset completo en una ventana"""
        ventana_datos = tk.Toplevel(root)
        ventana_datos.title("Dataset de Cultivos - Panamá")
        ventana_datos.geometry("1200x600")
        
        # Frame principal
        frame_principal = tk.Frame(ventana_datos)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Controles de filtro
        frame_filtros = tk.LabelFrame(frame_principal, text="Filtros", font=("Arial", 12, "bold"))
        frame_filtros.pack(fill=tk.X, pady=(0, 10))
        
        # Filtro por temporada
        tk.Label(frame_filtros, text="Temporada:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        combo_temporada = ttk.Combobox(frame_filtros, values=["Todas"] + list(self.df['temporada_siembra'].unique()))
        combo_temporada.set("Todas")
        combo_temporada.grid(row=0, column=1, padx=5, pady=5)
        
        # Filtro por lluvia
        tk.Label(frame_filtros, text="Lluvia:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        combo_lluvia = ttk.Combobox(frame_filtros, values=["Todas"] + list(self.df['lluvia'].unique()))
        combo_lluvia.set("Todas")
        combo_lluvia.grid(row=0, column=3, padx=5, pady=5)
        
        # Crear Treeview para mostrar datos
        columnas = list(self.df.columns)
        tree = ttk.Treeview(frame_principal, columns=columnas, show="headings", height=20)
        
        # Configurar columnas
        for col in columnas:
            tree.heading(col, text=col.replace('_', ' ').title())
            tree.column(col, width=120)
        
        # Scrollbars
        scroll_y = ttk.Scrollbar(frame_principal, orient="vertical", command=tree.yview)
        scroll_x = ttk.Scrollbar(frame_principal, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        # Empaquetar
        tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        
        def actualizar_vista():
            # Limpiar vista actual
            for item in tree.get_children():
                tree.delete(item)
            
            # Aplicar filtros
            df_filtrado = self.df.copy()
            
            temporada_sel = combo_temporada.get()
            if temporada_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado['temporada_siembra'] == temporada_sel]
            
            lluvia_sel = combo_lluvia.get()
            if lluvia_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado['lluvia'] == lluvia_sel]
            
            # Agregar datos filtrados
            for _, fila in df_filtrado.iterrows():
                tree.insert("", "end", values=list(fila))
            
            # Actualizar contador
            label_contador.config(text=f"Mostrando: {len(df_filtrado)} de {len(self.df)} cultivos")
        
        # Botones y contador
        frame_botones = tk.Frame(frame_principal)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(frame_botones, text="Aplicar Filtros", command=actualizar_vista,
                 bg="blue", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(frame_botones, text="Limpiar Filtros", 
                 command=lambda: [combo_temporada.set("Todas"), combo_lluvia.set("Todas"), actualizar_vista()],
                 bg="orange", fg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        label_contador = tk.Label(frame_botones, text="", font=("Arial", 10))
        label_contador.pack(side=tk.RIGHT)
        
        # Cargar datos iniciales
        actualizar_vista()
    
    def mostrar_estadisticas(self, root):
        """Muestra estadísticas detalladas del dataset con presentación mejorada"""
        stats = self.obtener_estadisticas_generales()
        
        ventana_stats = tk.Toplevel(root)
        ventana_stats.title("Estadísticas Completas - Dataset Cultivos Panamá")
        ventana_stats.geometry("900x700")
        ventana_stats.grab_set()
        
        # Crear notebook para pestañas
        notebook = ttk.Notebook(ventana_stats)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Resumen General
        frame_resumen = ttk.Frame(notebook)
        notebook.add(frame_resumen, text="Resumen General")
        
        # Frame principal con scroll
        canvas_resumen = tk.Canvas(frame_resumen)
        scrollbar_resumen = ttk.Scrollbar(frame_resumen, orient="vertical", command=canvas_resumen.yview)
        scrollable_frame_resumen = ttk.Frame(canvas_resumen)
        
        scrollable_frame_resumen.bind(
            "<Configure>",
            lambda e: canvas_resumen.configure(scrollregion=canvas_resumen.bbox("all"))
        )
        
        canvas_resumen.create_window((0, 0), window=scrollable_frame_resumen, anchor="nw")
        canvas_resumen.configure(yscrollcommand=scrollbar_resumen.set)
        
        canvas_resumen.pack(side="left", fill="both", expand=True)
        scrollbar_resumen.pack(side="right", fill="y")
        
        # Título principal
        tk.Label(scrollable_frame_resumen, text="ESTADÍSTICAS GENERALES", 
                font=("Arial", 16, "bold"), fg="darkgreen").pack(pady=10)
        
        # Frame para métricas principales
        frame_metricas = tk.LabelFrame(scrollable_frame_resumen, text="Métricas Principales", 
                                      font=("Arial", 12, "bold"))
        frame_metricas.pack(fill=tk.X, padx=10, pady=5)
        
        metricas_text = f"""
TOTAL DE CULTIVOS: {stats.get('total_cultivos', 0)}

RENDIMIENTOS:
   • Promedio: {stats.get('rendimiento_promedio', 0):.2f} t/ha
   • Máximo: {stats.get('rendimiento_max', 0):.2f} t/ha  
   • Mínimo: {stats.get('rendimiento_min', 0):.2f} t/ha

TIEMPOS DE COSECHA:
   • Promedio: {stats.get('tiempo_promedio', 0):.1f} meses
   • Máximo: {stats.get('tiempo_max', 0)} meses
   • Mínimo: {stats.get('tiempo_min', 0)} meses
        """
        
        tk.Label(frame_metricas, text=metricas_text, font=("Arial", 11), 
                justify=tk.LEFT, anchor="w").pack(padx=10, pady=5)
        
        # Frame para distribuciones
        frame_distrib = tk.LabelFrame(scrollable_frame_resumen, text="Distribuciones", 
                                     font=("Arial", 12, "bold"))
        frame_distrib.pack(fill=tk.X, padx=10, pady=5)
        
        # Distribución por temporadas
        temporadas_frame = tk.Frame(frame_distrib)
        temporadas_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(temporadas_frame, text="POR TEMPORADAS:", 
                font=("Arial", 11, "bold")).pack(anchor="w")
        
        for temporada, cantidad in stats.get('por_temporada', {}).items():
            porcentaje = (cantidad / stats.get('total_cultivos', 1)) * 100
            tk.Label(temporadas_frame, 
                    text=f"   • {temporada}: {cantidad} cultivos ({porcentaje:.1f}%)",
                    font=("Arial", 10)).pack(anchor="w")
        
        # Distribución por lluvia
        lluvia_frame = tk.Frame(frame_distrib)
        lluvia_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(lluvia_frame, text="POR NIVEL DE LLUVIA:", 
                font=("Arial", 11, "bold")).pack(anchor="w")
        
        for lluvia, cantidad in stats.get('por_lluvia', {}).items():
            porcentaje = (cantidad / stats.get('total_cultivos', 1)) * 100
            tk.Label(lluvia_frame, 
                    text=f"   • {lluvia}: {cantidad} cultivos ({porcentaje:.1f}%)",
                    font=("Arial", 10)).pack(anchor="w")
        
        # Pestaña 2: Análisis Detallado
        frame_analisis = ttk.Frame(notebook)
        notebook.add(frame_analisis, text="Análisis Detallado")
        
        texto_analisis = scrolledtext.ScrolledText(frame_analisis, font=("Courier", 10))
        texto_analisis.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generar análisis detallado por nivel de lluvia
        df = self.df.copy()
        df['rendimiento_numerico'] = df['rendimiento_promedio'].apply(self._extraer_valor_numerico)
        df['tiempo_numerico'] = df['tiempo_cosecha'].apply(lambda x: int(x.split('-')[0]) if '-' in str(x) else 0)
        
        analisis_detallado = f"""
ANÁLISIS DETALLADO POR NIVEL DE LLUVIA
{'='*50}

        """
        
        for nivel in ['Baja', 'Media', 'Alta']:
            if nivel in df['lluvia'].unique():
                datos = df[df['lluvia'] == nivel]
                if not datos.empty:
                    mejor_idx = datos['rendimiento_numerico'].idxmax()
                    mejor_cultivo = datos.loc[mejor_idx, 'cultivo']
                    
                    analisis_detallado += f"""
{nivel.upper()} LLUVIA:
{'-'*20}
• Cantidad: {len(datos)} cultivos
• Rendimiento promedio: {datos['rendimiento_numerico'].mean():.2f} t/ha
• Rendimiento máximo: {datos['rendimiento_numerico'].max():.2f} t/ha
• Mejor cultivo: {mejor_cultivo}
• Tiempo promedio cosecha: {datos['tiempo_numerico'].mean():.1f} meses
• Cultivos incluidos: {', '.join(datos['cultivo'].head(10).tolist())}
{' '*4}{'...' if len(datos) > 10 else ''}

                    """
        
        # Agregar top cultivos
        top_rendimientos = df.nlargest(10, 'rendimiento_numerico')
        analisis_detallado += f"""
TOP 10 CULTIVOS POR RENDIMIENTO:
{'='*35}
        """
        
        for i, (_, cultivo) in enumerate(top_rendimientos.iterrows(), 1):
            analisis_detallado += f"{i:2d}. {cultivo['cultivo']:<20} {cultivo['rendimiento_numerico']:>6.1f} t/ha\n"
        
        analisis_detallado += f"""

CULTIVOS DE COSECHA RÁPIDA (≤ 4 meses):
{'='*40}
        """
        
        rapidos = df[df['tiempo_numerico'] <= 4].sort_values('rendimiento_numerico', ascending=False)
        for _, cultivo in rapidos.head(10).iterrows():
            analisis_detallado += f"• {cultivo['cultivo']:<20} {cultivo['tiempo_numerico']} meses - {cultivo['rendimiento_numerico']:.1f} t/ha\n"
        
        analisis_detallado += f"\n\nReporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        
        texto_analisis.insert(tk.END, analisis_detallado)
        
        # Pestaña 3: Comparaciones
        frame_comparaciones = ttk.Frame(notebook)
        notebook.add(frame_comparaciones, text="Comparaciones")
        
        # Frame para controles de comparación
        frame_controles = tk.LabelFrame(frame_comparaciones, text="Configurar Comparación")
        frame_controles.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_controles, text="Comparar por:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        var_comparacion = tk.StringVar(value="rendimiento")
        tk.Radiobutton(frame_controles, text="Rendimiento", variable=var_comparacion, value="rendimiento").grid(row=0, column=1, padx=5)
        tk.Radiobutton(frame_controles, text="Tiempo de cosecha", variable=var_comparacion, value="tiempo").grid(row=0, column=2, padx=5)
        tk.Radiobutton(frame_controles, text="Temporada", variable=var_comparacion, value="temporada").grid(row=0, column=3, padx=5)
        
        # Área de resultados de comparación
        texto_comparacion = scrolledtext.ScrolledText(frame_comparaciones, height=20)
        texto_comparacion.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        def generar_comparacion():
            criterio = var_comparacion.get()
            comparacion = f"\nCOMPARACIÓN POR {criterio.upper()}\n{'='*50}\n"
            
            if criterio == "rendimiento":
                # Top y bottom rendimientos
                top_5 = df.nlargest(5, 'rendimiento_numerico')
                bottom_5 = df.nsmallest(5, 'rendimiento_numerico')
                
                comparacion += "\nTOP 5 RENDIMIENTOS:\n" + "-"*25 + "\n"
                for i, (_, c) in enumerate(top_5.iterrows(), 1):
                    comparacion += f"{i}. {c['cultivo']:<20} {c['rendimiento_numerico']:>6.1f} t/ha\n"
                
                comparacion += "\nBOTTOM 5 RENDIMIENTOS:\n" + "-"*25 + "\n"
                for i, (_, c) in enumerate(bottom_5.iterrows(), 1):
                    comparacion += f"{i}. {c['cultivo']:<20} {c['rendimiento_numerico']:>6.1f} t/ha\n"
                    
            elif criterio == "tiempo":
                # Cultivos más rápidos y más lentos
                rapidos = df.nsmallest(5, 'tiempo_numerico')
                lentos = df.nlargest(5, 'tiempo_numerico')
                
                comparacion += "\nCULTIVOS MÁS RÁPIDOS:\n" + "-"*25 + "\n"
                for i, (_, c) in enumerate(rapidos.iterrows(), 1):
                    comparacion += f"{i}. {c['cultivo']:<20} {c['tiempo_numerico']:>3} meses\n"
                
                comparacion += "\nCULTIVOS MÁS LENTOS:\n" + "-"*25 + "\n"
                for i, (_, c) in enumerate(lentos.iterrows(), 1):
                    comparacion += f"{i}. {c['cultivo']:<20} {c['tiempo_numerico']:>3} meses\n"
                    
            elif criterio == "temporada":
                # Análisis por temporada
                for temp in df['temporada_siembra'].unique():
                    temp_data = df[df['temporada_siembra'] == temp]
                    comparacion += f"\n{temp.upper()}:\n" + "-"*20 + "\n"
                    comparacion += f"Cultivos: {len(temp_data)}\n"
                    comparacion += f"Rendimiento promedio: {temp_data['rendimiento_numerico'].mean():.2f} t/ha\n"
                    comparacion += f"Mejor: {temp_data.loc[temp_data['rendimiento_numerico'].idxmax(), 'cultivo']}\n"
                    comparacion += f"Tiempo promedio: {temp_data['tiempo_numerico'].mean():.1f} meses\n"
            
            texto_comparacion.delete('1.0', tk.END)
            texto_comparacion.insert(tk.END, comparacion)
        
        tk.Button(frame_controles, text="Generar Comparación", 
                 command=generar_comparacion,
                 bg="blue", fg="white", font=("Arial", 10)).grid(row=1, column=1, columnspan=2, pady=10)
        
        # Botones inferiores
        frame_botones = tk.Frame(ventana_stats)
        frame_botones.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botones, text="Exportar Estadísticas", 
                 command=self.exportar_datos_completos,
                 bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="Cerrar", 
                 command=ventana_stats.destroy,
                 bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
        
        # Generar comparación inicial
        generar_comparacion()
    
    def exportar_datos_completos(self):
        """Exporta todos los datos del dataset con análisis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reporte_completo_{timestamp}.txt"
            
            stats = self.obtener_estadisticas_generales()
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("REPORTE COMPLETO - ASISTENTE AGRÍCOLA PANAMÁ\n")
                f.write("="*60 + "\n")
                f.write(f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
                
                # Estadísticas generales
                f.write("ESTADÍSTICAS GENERALES\n")
                f.write("-"*30 + "\n")
                f.write(f"Total de cultivos en base de datos: {stats.get('total_cultivos', 0)}\n")
                f.write(f"Rendimiento promedio general: {stats.get('rendimiento_promedio', 0):.2f} t/ha\n")
                f.write(f"Rendimiento máximo: {stats.get('rendimiento_max', 0):.2f} t/ha\n")
                f.write(f"Rendimiento mínimo: {stats.get('rendimiento_min', 0):.2f} t/ha\n\n")
                
                # Distribución por temporadas
                f.write("DISTRIBUCIÓN POR TEMPORADAS\n")
                f.write("-"*35 + "\n")
                for temporada, cantidad in stats.get('por_temporada', {}).items():
                    f.write(f"{temporada}: {cantidad} cultivos\n")
                f.write("\n")
                
                # Distribución por nivel de lluvia
                f.write("DISTRIBUCIÓN POR NIVEL DE LLUVIA\n")
                f.write("-"*40 + "\n")
                for lluvia, cantidad in stats.get('por_lluvia', {}).items():
                    f.write(f"{lluvia}: {cantidad} cultivos\n")
                f.write("\n")
                
                # Detalle de cada cultivo
                f.write("DETALLE DE TODOS LOS CULTIVOS\n")
                f.write("="*40 + "\n\n")
                
                for _, fila in self.df.iterrows():
                    f.write(f"CULTIVO: {fila['cultivo']}\n")
                    f.write("-"*len(f"CULTIVO: {fila['cultivo']}") + "\n")
                    f.write(f"Temporada: {fila['temporada_siembra']}\n")
                    f.write(f"Tiempo de cosecha: {fila['tiempo_cosecha']}\n")
                    f.write(f"Temperatura ideal: {fila['temperatura_ideal']}\n")
                    f.write(f"Lluvia: {fila['lluvia']}\n")
                    f.write(f"Rendimiento: {fila['rendimiento_promedio']}\n")
                    f.write(f"Recomendaciones: {fila['recomendaciones']}\n")
                    f.write("\n" + "="*60 + "\n\n")
            
            messagebox.showinfo("Éxito", f"Reporte completo exportado: {filename}")
            if self.barra_estado:
                self.barra_estado.config(text=f"Reporte exportado: {filename}")
            
            return filename
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar datos: {str(e)}")
            return None
    
    def buscar_cultivos_similares(self, cultivo_referencia):
        """Busca cultivos con características similares"""
        if not cultivo_referencia:
            return []
        
        similares = []
        ref_fila = None
        
        # Encontrar el cultivo de referencia
        for _, fila in self.df.iterrows():
            if fila['cultivo'] == cultivo_referencia:
                ref_fila = fila
                break
        
        if ref_fila is None:
            return []
        
        # Buscar similares
        for _, fila in self.df.iterrows():
            if fila['cultivo'] == cultivo_referencia:
                continue
            
            puntuacion = 0
            
            # Misma temporada de siembra
            if fila['temporada_siembra'] == ref_fila['temporada_siembra']:
                puntuacion += 3
            
            # Mismo nivel de lluvia
            if fila['lluvia'] == ref_fila['lluvia']:
                puntuacion += 2
            
            # Temperatura similar
            if fila['temperatura_ideal'] == ref_fila['temperatura_ideal']:
                puntuacion += 2
            
            # Rendimiento similar (±20%)
            try:
                rend_ref = self._extraer_valor_numerico(ref_fila['rendimiento_promedio'])
                rend_actual = self._extraer_valor_numerico(fila['rendimiento_promedio'])
                
                if abs(rend_ref - rend_actual) / rend_ref <= 0.2:
                    puntuacion += 1
            except:
                pass
            
            if puntuacion >= 3:  # Al menos 3 puntos de similitud
                similares.append((fila['cultivo'], puntuacion))
        
        # Ordenar por puntuación
        similares.sort(key=lambda x: x[1], reverse=True)
        return [cultivo for cultivo, _ in similares[:5]]  # Top 5