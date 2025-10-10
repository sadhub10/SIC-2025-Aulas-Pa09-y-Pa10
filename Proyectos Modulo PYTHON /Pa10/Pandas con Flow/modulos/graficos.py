import tkinter as tk
from tkinter import messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvasTk, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
from datetime import datetime


class GraficosManager:
    """Clase para manejar todos los gráficos del sistema"""
    
    def __init__(self, df, barra_estado=None):
        self.df = df
        self.barra_estado = barra_estado
    
    def mostrar_grafico_cultivo(self, cultivo_actual, root):
        """Muestra selector de gráficos específicos del cultivo seleccionado"""
        if cultivo_actual is None:
            messagebox.showwarning("Advertencia", "Seleccione un cultivo primero")
            return
        
        try:
            ventana_selector = tk.Toplevel(root)
            ventana_selector.title(f"Gráficos - {cultivo_actual['cultivo']}")
            ventana_selector.geometry("700x600")
            ventana_selector.grab_set()
            
            # Frame para título
            frame_titulo = tk.Frame(ventana_selector)
            frame_titulo.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Label(frame_titulo, text=f"ANÁLISIS GRÁFICO", 
                    font=("Arial", 18, "bold"), fg="darkgreen").pack()
            
            tk.Label(frame_titulo, text=f"Cultivo: {cultivo_actual['cultivo']}", 
                    font=("Arial", 14, "bold"), fg="darkblue").pack(pady=5)
            
            tk.Label(frame_titulo, text="Seleccione el tipo de análisis que desea visualizar", 
                    font=("Arial", 11)).pack()
            
            # Frame para botones de selección
            frame_selector_cult = tk.LabelFrame(ventana_selector, text="Análisis Disponibles",
                                               font=("Arial", 12, "bold"))
            frame_selector_cult.pack(fill=tk.X, padx=10, pady=10)
            
            # Botones de análisis individual
            botones_cultivo = [
                ("Comparación de Rendimiento", "Posición vs otros cultivos", "rendimiento_comparativo", "purple"),
                ("Información del Cultivo", "Características y recomendaciones", "info_cultivo", "blue"),
                ("Tiempo de Cosecha", "Comparación de tiempos", "tiempo_cosecha", "darkgreen"),
                ("Cultivos Similares", "Recomendaciones relacionadas", "cultivos_similares", "orange")
            ]
            
            for i, (texto, descripcion, tipo, color) in enumerate(botones_cultivo):
                # Frame para cada botón
                frame_boton = tk.Frame(frame_selector_cult)
                frame_boton.pack(fill=tk.X, padx=10, pady=5)
                
                # Botón principal
                btn = tk.Button(frame_boton, text=texto, 
                               command=lambda t=tipo: self.mostrar_grafico_cultivo_individual(t, cultivo_actual, ventana_selector),
                               bg=color, fg="white", font=("Arial", 11, "bold"),
                               width=30, height=2)
                btn.pack(pady=2)
                
                # Descripción
                tk.Label(frame_boton, text=descripcion, font=("Arial", 9),
                        justify=tk.CENTER).pack()
            
            # Botones de acción
            frame_botones = tk.Frame(ventana_selector)
            frame_botones.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Button(frame_botones, text="Ver Todos los Análisis", 
                     command=lambda: self.mostrar_todos_graficos_cultivo(cultivo_actual, ventana_selector),
                     bg="darkgreen", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_selector.destroy,
                     bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
            
            if self.barra_estado:
                self.barra_estado.config(text=f"Selector de gráficos abierto para {cultivo_actual['cultivo']}")
            
        except Exception as e:
            print(f"Error en mostrar_grafico_cultivo: {e}")
            messagebox.showerror("Error", f"Error al abrir selector: {str(e)}")
            if self.barra_estado:
                self.barra_estado.config(text="Error al abrir selector")
    
    def mostrar_grafico_cultivo_individual(self, tipo_grafico, cultivo_actual, ventana_padre):
        """Muestra un gráfico individual del cultivo según el tipo seleccionado"""
        try:
            ventana_grafico = tk.Toplevel(ventana_padre)
            ventana_grafico.grab_set()
            
            # Crear figura
            fig = Figure(figsize=(10, 8), dpi=100)
            ax = fig.add_subplot(111)
            
            # Generar gráfico según tipo
            if tipo_grafico == "rendimiento_comparativo":
                ventana_grafico.title(f"Comparación de Rendimiento - {cultivo_actual['cultivo']}")
                ventana_grafico.geometry("900x700")
                self.crear_grafico_rendimiento_comparativo(ax, cultivo_actual)
                
            elif tipo_grafico == "info_cultivo":
                ventana_grafico.title(f"Información - {cultivo_actual['cultivo']}")
                ventana_grafico.geometry("800x600")
                self.crear_grafico_info_cultivo(ax, cultivo_actual)
                
            elif tipo_grafico == "tiempo_cosecha":
                ventana_grafico.title(f"Tiempo de Cosecha - {cultivo_actual['cultivo']}")
                ventana_grafico.geometry("800x600")
                self.crear_grafico_tiempo_cosecha(ax, cultivo_actual)
                
            elif tipo_grafico == "cultivos_similares":
                ventana_grafico.title(f"Cultivos Similares - {cultivo_actual['cultivo']}")
                ventana_grafico.geometry("800x600")
                self.crear_grafico_cultivos_similares(ax, cultivo_actual)
            
            fig.tight_layout(pad=2.0)
            
            # Mostrar canvas
            canvas = FigureCanvasTk(fig, ventana_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Toolbar
            try:
                toolbar = NavigationToolbar2Tk(canvas, ventana_grafico)
                toolbar.update()
            except:
                pass
            
            # Botones
            frame_botones = tk.Frame(ventana_grafico)
            frame_botones.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(frame_botones, text="Guardar Gráfico", 
                     command=lambda: self.guardar_graficos(fig, cultivo_actual),
                     bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_grafico.destroy,
                     bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
            
            if self.barra_estado:
                self.barra_estado.config(text=f"Gráfico {tipo_grafico} generado para {cultivo_actual['cultivo']}")
                
        except Exception as e:
            print(f"Error en mostrar_grafico_cultivo_individual: {e}")
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")
    
    def mostrar_todos_graficos_cultivo(self, cultivo_actual, ventana_padre):
        """Muestra todos los gráficos del cultivo en una ventana (versión original)"""
        try:
            ventana_todos = tk.Toplevel(ventana_padre)
            ventana_todos.title(f"Análisis Completo - {cultivo_actual['cultivo']}")
            ventana_todos.geometry("1200x900")
            ventana_todos.grab_set()
            
            # Frame para controles
            frame_controles = tk.Frame(ventana_todos)
            frame_controles.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame_controles, text=f"Análisis Completo: {cultivo_actual['cultivo']}", 
                    font=("Arial", 16, "bold")).pack()
            
            # Crear figura con subplots
            fig = Figure(figsize=(14, 10), dpi=100)
            
            try:
                # Subplot 1: Comparacion de rendimiento
                ax1 = fig.add_subplot(221)
                self.crear_grafico_rendimiento_comparativo(ax1, cultivo_actual)
                
                # Subplot 2: Información del cultivo
                ax2 = fig.add_subplot(222)
                self.crear_grafico_info_cultivo(ax2, cultivo_actual)
                
                # Subplot 3: Tiempo de cosecha vs otros cultivos
                ax3 = fig.add_subplot(223)
                self.crear_grafico_tiempo_cosecha(ax3, cultivo_actual)
                
                # Subplot 4: Cultivos similares
                ax4 = fig.add_subplot(224)
                self.crear_grafico_cultivos_similares(ax4, cultivo_actual)
                
                fig.suptitle(f'Análisis Completo - {cultivo_actual["cultivo"]}', 
                            fontsize=16, fontweight='bold')
                # Ajustar espaciado para evitar superposición
                fig.tight_layout(rect=[0, 0.03, 1, 0.95], pad=4.0, h_pad=5.0, w_pad=4.0)
                fig.subplots_adjust(hspace=0.6, wspace=0.4, 
                                  top=0.90, bottom=0.12, left=0.08, right=0.96)
                
            except Exception as subplot_error:
                print(f"Error en subplots: {subplot_error}")
                ax = fig.add_subplot(111)
                ax.text(0.5, 0.5, f'Error al generar análisis\nCultivo: {cultivo_actual["cultivo"]}', 
                       ha='center', va='center', fontsize=14, transform=ax.transAxes)
                ax.set_title('Error en Análisis', fontweight='bold')
                fig.tight_layout(pad=2.0)
            
            # Crear canvas y mostrar
            canvas = FigureCanvasTk(fig, ventana_todos)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Toolbar
            try:
                toolbar = NavigationToolbar2Tk(canvas, ventana_todos)
                toolbar.update()
            except:
                pass
            
            # Botones de control
            frame_botones = tk.Frame(ventana_todos)
            frame_botones.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(frame_botones, text="Guardar Análisis Completo", 
                     command=lambda: self.guardar_graficos(fig, cultivo_actual),
                     bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_todos.destroy,
                     bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
            
            if self.barra_estado:
                self.barra_estado.config(text=f"Análisis completo generado para {cultivo_actual['cultivo']}")
            
        except Exception as e:
            print(f"Error en mostrar_todos_graficos_cultivo: {e}")
            messagebox.showerror("Error", f"Error al generar análisis completo: {str(e)}")
            if self.barra_estado:
                self.barra_estado.config(text="Error al generar análisis completo")
    
    def crear_grafico_rendimiento_comparativo(self, ax, cultivo_actual):
        """Crea grafico comparativo de rendimientos centrado en el cultivo seleccionado"""
        try:
            # Obtener rendimiento del cultivo actual
            cultivo_actual_rend = float(cultivo_actual['rendimiento_promedio'].split()[0])
            
            # Preparar datos de todos los cultivos
            rendimientos = []
            nombres = []
            
            for _, fila in self.df.iterrows():
                try:
                    valor = float(fila['rendimiento_promedio'].split()[0])
                    rendimientos.append(valor)
                    nombres.append(fila['cultivo'])
                except:
                    continue
            
            if not rendimientos:
                ax.text(0.5, 0.5, 'No hay datos de rendimiento disponibles', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Crear DataFrame y obtener Top 10 + cultivo actual
            df_rend = pd.DataFrame({'cultivo': nombres, 'rendimiento': rendimientos})
            top_10 = df_rend.nlargest(10, 'rendimiento')
            
            # Asegurar que el cultivo actual esté incluido
            if cultivo_actual['cultivo'] not in top_10['cultivo'].values:
                cultivo_actual_row = df_rend[df_rend['cultivo'] == cultivo_actual['cultivo']]
                if not cultivo_actual_row.empty:
                    top_10 = pd.concat([top_10.head(9), cultivo_actual_row]).sort_values('rendimiento', ascending=False)
            
            # Colorear: rojo para cultivo actual, azul para otros
            colors = []
            for cultivo in top_10['cultivo'].values:
                if cultivo == cultivo_actual['cultivo']:
                    colors.append('red')
                else:
                    colors.append('lightblue')
            
            bars = ax.bar(range(len(top_10)), top_10['rendimiento'], color=colors)
            
            # Título más específico
            posicion = list(top_10['cultivo']).index(cultivo_actual['cultivo']) + 1 if cultivo_actual['cultivo'] in top_10['cultivo'].values else "N/A"
            ax.set_title(f'Rendimientos - {cultivo_actual["cultivo"]} (Posición #{posicion})', fontweight='bold')
            
            ax.set_xticks(range(len(top_10)))
            ax.set_xticklabels(top_10['cultivo'], rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('Toneladas por hectárea', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Ajustar márgenes para las etiquetas rotadas
            ax.margins(x=0.02, y=0.1)
            
            # Destacar el rendimiento del cultivo actual
            for i, (bar, cultivo, rend) in enumerate(zip(bars, top_10['cultivo'], top_10['rendimiento'])):
                height = bar.get_height()
                if cultivo == cultivo_actual['cultivo']:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{height:.1f} ★', ha='center', va='bottom', fontweight='bold', color='red')
                else:
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                           f'{height:.1f}', ha='center', va='bottom')
        
        except Exception as e:
            print(f"Error en crear_grafico_rendimiento_comparativo: {e}")
            ax.text(0.5, 0.5, f'Error al crear gráfico de rendimientos:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def crear_grafico_info_cultivo(self, ax, cultivo_actual):
        """Crea panel informativo del cultivo actual"""
        try:
            # Limpiar el eje
            ax.clear()
            ax.axis('off')
            
            # Título principal
            ax.text(0.5, 0.95, f'CARACTERÍSTICAS DE {cultivo_actual["cultivo"].upper()}', 
                   ha='center', va='top', fontsize=14, fontweight='bold',
                   transform=ax.transAxes)
            
            # Información básica compacta
            info_text = f"""TEMPORADA: {cultivo_actual['temporada_siembra']}
COSECHA: {cultivo_actual['tiempo_cosecha']}
TEMP: {cultivo_actual['temperatura_ideal']}
LLUVIA: {cultivo_actual['lluvia']}
REND: {cultivo_actual['rendimiento_promedio']}"""
            
            ax.text(0.05, 0.85, info_text, ha='left', va='top', fontsize=8,
                   transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.2", facecolor="lightcyan", alpha=0.8))
            
            # Calcular estadísticas comparativas
            try:
                rend_actual = float(cultivo_actual['rendimiento_promedio'].split()[0])
                tiempo_actual = int(cultivo_actual['tiempo_cosecha'].split('-')[0])
                
                # Estadísticas comparativas
                all_rend = []
                all_tiempo = []
                for _, fila in self.df.iterrows():
                    try:
                        r = float(fila['rendimiento_promedio'].split()[0])
                        t = int(fila['tiempo_cosecha'].split('-')[0])
                        all_rend.append(r)
                        all_tiempo.append(t)
                    except:
                        continue
                
                if all_rend:
                    percentil_rend = (sum(1 for r in all_rend if r < rend_actual) / len(all_rend)) * 100
                    percentil_tiempo = (sum(1 for t in all_tiempo if t > tiempo_actual) / len(all_tiempo)) * 100
                    
                    stats_text = f"""COMPARATIVO:
Superior al {percentil_rend:.0f}%
Rápido que {percentil_tiempo:.0f}%
Promedio: {np.mean(all_rend):.1f} t/ha
Actual: {rend_actual:.1f} t/ha"""
                    
                    ax.text(0.05, 0.50, stats_text, ha='left', va='top', fontsize=7,
                           transform=ax.transAxes,
                           bbox=dict(boxstyle="round,pad=0.15", facecolor="lightyellow", alpha=0.8))
            except:
                pass
            
            # Agregar recomendación más compacta
            recom = cultivo_actual['recomendaciones'][:60] + "..." if len(cultivo_actual['recomendaciones']) > 60 else cultivo_actual['recomendaciones']
            ax.text(0.05, 0.20, f"RECOM:\n{recom}", ha='left', va='top', fontsize=6,
                   transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.1", facecolor="lightgreen", alpha=0.7))
            
        except Exception as e:
            print(f"Error en crear_grafico_info_cultivo: {e}")
            ax.text(0.5, 0.5, f'Error al crear información del cultivo:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def crear_grafico_tiempo_cosecha(self, ax, cultivo_actual):
        """Crea grafico de comparación de tiempos de cosecha"""
        try:
            # Obtener tiempo del cultivo actual
            tiempo_actual = int(cultivo_actual['tiempo_cosecha'].split('-')[0])
            
            # Categorizar cultivos por velocidad
            rapidos = []  # <= 4 meses
            medios = []   # 5-8 meses
            lentos = []   # >= 9 meses
            
            for _, fila in self.df.iterrows():
                try:
                    tiempo = int(fila['tiempo_cosecha'].split('-')[0])
                    if tiempo <= 4:
                        rapidos.append(fila['cultivo'])
                    elif tiempo <= 8:
                        medios.append(fila['cultivo'])
                    else:
                        lentos.append(fila['cultivo'])
                except:
                    continue
            
            # Determinar categoría del cultivo actual
            categoria_actual = "Rápidos" if tiempo_actual <= 4 else ("Medios" if tiempo_actual <= 8 else "Lentos")
            
            # Datos para el gráfico
            categorias = ['Rápidos\n(≤4 meses)', 'Medios\n(5-8 meses)', 'Lentos\n(≥9 meses)']
            cantidades = [len(rapidos), len(medios), len(lentos)]
            
            # Colorear según la categoría del cultivo actual
            colors = []
            for i, cat in enumerate(['Rápidos', 'Medios', 'Lentos']):
                if cat == categoria_actual:
                    colors.append('red')
                else:
                    colors.append('lightblue')
            
            bars = ax.bar(categorias, cantidades, color=colors, alpha=0.8, edgecolor='black')
            
            ax.set_title(f'Velocidad de Cosecha\n{cultivo_actual["cultivo"]}: {tiempo_actual} meses ({categoria_actual})', 
                        fontweight='bold', fontsize=9)
            ax.set_ylabel('Número de cultivos', fontsize=9)
            ax.grid(True, alpha=0.3, axis='y')
            
            # Ajustar tamaño de etiquetas del eje X
            ax.tick_params(axis='x', labelsize=8)
            ax.tick_params(axis='y', labelsize=8)
            
            # Agregar valores en las barras
            for bar, cantidad in zip(bars, cantidades):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{cantidad}', ha='center', va='bottom', fontweight='bold')
            
        except Exception as e:
            print(f"Error en crear_grafico_tiempo_cosecha: {e}")
            ax.text(0.5, 0.5, f'Error al crear gráfico de tiempo:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def crear_grafico_cultivos_similares(self, ax, cultivo_actual):
        """Crea grafico de cultivos alternativos"""
        try:
            # Encontrar cultivos similares
            similares_score = []
            
            for _, fila in self.df.iterrows():
                if fila['cultivo'] == cultivo_actual['cultivo']:
                    continue
                
                score = 0
                nombre = fila['cultivo']
                
                # Puntuación por temporada (3 puntos)
                if fila['temporada_siembra'] == cultivo_actual['temporada_siembra']:
                    score += 3
                
                # Puntuación por lluvia (2 puntos)
                if fila['lluvia'] == cultivo_actual['lluvia']:
                    score += 2
                
                # Puntuación por temperatura (2 puntos)
                if fila['temperatura_ideal'] == cultivo_actual['temperatura_ideal']:
                    score += 2
                
                # Puntuación por rendimiento similar (1 punto)
                try:
                    rend_actual = float(cultivo_actual['rendimiento_promedio'].split()[0])
                    rend_comp = float(fila['rendimiento_promedio'].split()[0])
                    if abs(rend_actual - rend_comp) / rend_actual <= 0.3:  # ±30%
                        score += 1
                except:
                    pass
                
                if score >= 2:  # Al menos 2 puntos de similitud
                    try:
                        rend = float(fila['rendimiento_promedio'].split()[0])
                        similares_score.append((nombre, score, rend))
                    except:
                        pass
            
            if not similares_score:
                ax.text(0.5, 0.5, f'No se encontraron cultivos similares\na {cultivo_actual["cultivo"]}', 
                       ha='center', va='center', transform=ax.transAxes)
                return
            
            # Ordenar y tomar los mejores 6
            similares_score.sort(key=lambda x: (x[1], x[2]), reverse=True)
            top_similares = similares_score[:6]
            
            nombres = [s[0] for s in top_similares]
            scores = [s[1] for s in top_similares]
            rendimientos = [s[2] for s in top_similares]
            
            # Colores según puntuación
            colors = []
            for score in scores:
                if score >= 6:
                    colors.append('darkgreen')
                elif score >= 4:
                    colors.append('green')
                else:
                    colors.append('orange')
            
            bars = ax.barh(nombres, rendimientos, color=colors)
            
            ax.set_title(f'Cultivos Alternativos a {cultivo_actual["cultivo"]}\n(Ordenados por similitud)', 
                        fontweight='bold', fontsize=9)
            ax.set_xlabel('Rendimiento (t/ha)', fontsize=9)
            ax.grid(True, alpha=0.3)
            
            # Ajustar etiquetas del eje Y para evitar recorte
            ax.tick_params(axis='y', labelsize=8)
            
            # Agregar valores
            for i, (bar, rend, score) in enumerate(zip(bars, rendimientos, scores)):
                ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                       f'{rend:.1f}', ha='left', va='center', fontsize=9)
                
                ax.text(0.02, bar.get_y() + bar.get_height()/2,
                       f'★{score}', ha='left', va='center', fontsize=8, 
                       color='white', fontweight='bold')
            
        except Exception as e:
            print(f"Error en crear_grafico_cultivos_similares: {e}")
            ax.text(0.5, 0.5, f'Error al crear gráfico de alternativas:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes)
    
    def guardar_graficos(self, fig, cultivo_actual):
        """Guarda los gráficos en archivo PNG"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"grafico_{cultivo_actual['cultivo']}_{timestamp}.png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Éxito", f"Gráficos guardados como: {filename}")
            if self.barra_estado:
                self.barra_estado.config(text=f"Gráficos guardados: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def test_graficos_simple(self, root):
        """Test simple para verificar que matplotlib funcione"""
        try:
            ventana_test = tk.Toplevel(root)
            ventana_test.title("Test de Gráficos")
            ventana_test.geometry("600x400")
            
            fig = Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            x = np.linspace(0, 10, 100)
            y = np.sin(x)
            
            ax.plot(x, y, 'b-', linewidth=2, label='sin(x)')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Test de Matplotlib - Funcionando OK')
            ax.grid(True)
            ax.legend()
            
            canvas = FigureCanvasTk(fig, ventana_test)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            if self.barra_estado:
                self.barra_estado.config(text="Test de gráficos ejecutado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error en Test", f"Error en test de gráficos: {str(e)}")
            if self.barra_estado:
                self.barra_estado.config(text="Error en test de gráficos")
    
    def mostrar_grafico_rendimientos_general(self, root):
        """Muestra ventana con selector de gráficos de rendimientos"""
        try:
            ventana_rendimientos = tk.Toplevel(root)
            ventana_rendimientos.title("Selector de Gráficos de Rendimientos")
            ventana_rendimientos.geometry("800x600")
            ventana_rendimientos.grab_set()
            
            # Frame para título
            frame_titulo = tk.Frame(ventana_rendimientos)
            frame_titulo.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Label(frame_titulo, text="ANÁLISIS DE RENDIMIENTOS", 
                    font=("Arial", 18, "bold"), fg="darkgreen").pack()
            
            tk.Label(frame_titulo, text="Seleccione el tipo de análisis que desea visualizar", 
                    font=("Arial", 12)).pack(pady=5)
            
            # Frame para botones de selección
            frame_selector = tk.LabelFrame(ventana_rendimientos, text="Tipos de Gráficos Disponibles",
                                         font=("Arial", 12, "bold"))
            frame_selector.pack(fill=tk.X, padx=10, pady=10)
            
            # Organizar botones en grid
            botones_info = [
                ("Top Rendimientos", "Gráfico de barras con los 15 mejores cultivos", "top_rendimientos", "purple"),
                ("Por Temporadas", "Distribución circular del rendimiento por temporada", "por_temporadas", "blue"),
                ("Rendimiento vs Lluvia", "Correlación entre nivel de lluvia y rendimiento", "lluvia_scatter", "darkblue"),
                ("Distribución General", "Histograma de distribución de todos los rendimientos", "histograma", "green"),
                ("Comparación por Lluvia", "Box plot comparando niveles de lluvia", "box_plot", "orange"),
                ("Estadísticas Completas", "Panel con todas las estadísticas numéricas", "estadisticas", "darkred")
            ]
            
            for i, (texto, descripcion, tipo, color) in enumerate(botones_info):
                row = i // 2
                col = i % 2
                
                # Frame para cada botón
                frame_boton = tk.Frame(frame_selector)
                frame_boton.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
                
                # Botón principal
                btn = tk.Button(frame_boton, text=texto, 
                               command=lambda t=tipo: self.mostrar_grafico_individual(t, ventana_rendimientos),
                               bg=color, fg="white", font=("Arial", 11, "bold"),
                               width=20, height=2)
                btn.pack(pady=2)
                
                # Descripción
                tk.Label(frame_boton, text=descripcion, font=("Arial", 9),
                        wraplength=200, justify=tk.CENTER).pack()
            
            # Configurar grid columns para que se expandan
            frame_selector.grid_columnconfigure(0, weight=1)
            frame_selector.grid_columnconfigure(1, weight=1)
            
            # Botones de acción
            frame_botones = tk.Frame(ventana_rendimientos)
            frame_botones.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Button(frame_botones, text="Ver Todos los Gráficos", 
                     command=lambda: self.mostrar_todos_graficos_rendimientos(ventana_rendimientos),
                     bg="darkgreen", fg="white", font=("Arial", 12, "bold")).pack(pady=10)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_rendimientos.destroy,
                     bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
            
            if self.barra_estado:
                self.barra_estado.config(text="Selector de gráficos abierto")
            
        except Exception as e:
            print(f"Error en mostrar_grafico_rendimientos_general: {e}")
            messagebox.showerror("Error", f"Error al abrir selector: {str(e)}")
            if self.barra_estado:
                self.barra_estado.config(text="Error al abrir selector de gráficos")
    
    def mostrar_grafico_individual(self, tipo_grafico, ventana_padre):
        """Muestra un gráfico individual según el tipo seleccionado"""
        try:
            ventana_grafico = tk.Toplevel(ventana_padre)
            ventana_grafico.grab_set()
            
            # Preparar datos comunes
            rendimientos = []
            nombres = []
            temporadas = []
            lluvias = []
            
            for _, fila in self.df.iterrows():
                try:
                    valor = float(fila['rendimiento_promedio'].split()[0])
                    rendimientos.append(valor)
                    nombres.append(fila['cultivo'])
                    temporadas.append(fila['temporada_siembra'])
                    lluvias.append(fila['lluvia'])
                except:
                    continue
            
            if not rendimientos:
                messagebox.showwarning("Sin datos", "No hay datos de rendimiento disponibles")
                ventana_grafico.destroy()
                return
            
            df_rend = pd.DataFrame({
                'cultivo': nombres, 
                'rendimiento': rendimientos,
                'temporada': temporadas,
                'lluvia': lluvias
            })
            
            # Configurar ventana según tipo de gráfico
            if tipo_grafico == "top_rendimientos":
                ventana_grafico.title("Top 15 Cultivos por Rendimiento")
                ventana_grafico.geometry("900x600")
                self._crear_grafico_top_rendimientos(ventana_grafico, df_rend)
                
            elif tipo_grafico == "por_temporadas":
                ventana_grafico.title("Rendimiento Promedio por Temporada")
                ventana_grafico.geometry("700x600")
                self._crear_grafico_por_temporadas(ventana_grafico, df_rend)
                
            elif tipo_grafico == "lluvia_scatter":
                ventana_grafico.title("Rendimiento vs Nivel de Lluvia")
                ventana_grafico.geometry("800x600")
                self._crear_grafico_lluvia_scatter(ventana_grafico, df_rend)
                
            elif tipo_grafico == "histograma":
                ventana_grafico.title("Distribución de Rendimientos")
                ventana_grafico.geometry("700x600")
                self._crear_grafico_histograma(ventana_grafico, df_rend)
                
            elif tipo_grafico == "box_plot":
                ventana_grafico.title("Comparación por Nivel de Lluvia")
                ventana_grafico.geometry("700x600")
                self._crear_grafico_box_plot(ventana_grafico, df_rend)
                
            elif tipo_grafico == "estadisticas":
                ventana_grafico.title("Estadísticas Completas")
                ventana_grafico.geometry("600x700")
                self._crear_panel_estadisticas(ventana_grafico, df_rend)
            
            if self.barra_estado:
                self.barra_estado.config(text=f"Gráfico generado: {tipo_grafico}")
                
        except Exception as e:
            print(f"Error en mostrar_grafico_individual: {e}")
            messagebox.showerror("Error", f"Error al generar gráfico: {str(e)}")
    
    def _crear_grafico_top_rendimientos(self, ventana, df_rend):
        """Crea gráfico de top rendimientos"""
        fig = Figure(figsize=(12, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        top_15 = df_rend.nlargest(15, 'rendimiento')
        colors = plt.cm.viridis(np.linspace(0, 1, len(top_15)))
        
        bars = ax.bar(range(len(top_15)), top_15['rendimiento'], color=colors)
        ax.set_title('Top 15 Cultivos por Rendimiento', fontweight='bold', fontsize=16)
        ax.set_xlabel('Cultivos', fontsize=12)
        ax.set_ylabel('Rendimiento (t/ha)', fontsize=12)
        ax.set_xticks(range(len(top_15)))
        ax.set_xticklabels(top_15['cultivo'], rotation=45, ha='right', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Agregar valores en las barras
        for bar, valor in zip(bars, top_15['rendimiento']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        fig.tight_layout()
        self._mostrar_canvas(fig, ventana, "Top_Rendimientos")
    
    def _crear_grafico_por_temporadas(self, ventana, df_rend):
        """Crea gráfico circular por temporadas"""
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        temp_counts = df_rend.groupby('temporada')['rendimiento'].mean()
        colors = plt.cm.Set3(np.linspace(0, 1, len(temp_counts)))
        
        wedges, texts, autotexts = ax.pie(temp_counts.values, labels=temp_counts.index, 
                                         autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Rendimiento Promedio por Temporada', fontweight='bold', fontsize=16)
        
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        # Agregar leyenda con valores
        leyenda = [f'{temp}: {valor:.1f} t/ha' for temp, valor in temp_counts.items()]
        ax.legend(leyenda, loc='center left', bbox_to_anchor=(1, 0.5))
        
        fig.tight_layout()
        self._mostrar_canvas(fig, ventana, "Por_Temporadas")
    
    def _crear_grafico_lluvia_scatter(self, ventana, df_rend):
        """Crea scatter plot lluvia vs rendimiento"""
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        lluvia_map = {'Baja': 1, 'Media': 2, 'Alta': 3}
        lluvia_numerica = [lluvia_map.get(l, 0) for l in df_rend['lluvia']]
        
        scatter = ax.scatter(lluvia_numerica, df_rend['rendimiento'], 
                           c=df_rend['rendimiento'], cmap='coolwarm', 
                           alpha=0.7, s=80)
        ax.set_xlabel('Nivel de Lluvia', fontsize=12)
        ax.set_ylabel('Rendimiento (t/ha)', fontsize=12)
        ax.set_title('Correlación: Rendimiento vs Nivel de Lluvia', fontweight='bold', fontsize=16)
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(['Baja', 'Media', 'Alta'])
        ax.grid(True, alpha=0.3)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Rendimiento (t/ha)', fontsize=12)
        
        # Agregar línea de tendencia
        z = np.polyfit(lluvia_numerica, df_rend['rendimiento'], 1)
        p = np.poly1d(z)
        ax.plot([1, 2, 3], p([1, 2, 3]), "r--", alpha=0.8, linewidth=2, label='Tendencia')
        ax.legend()
        
        fig.tight_layout()
        self._mostrar_canvas(fig, ventana, "Lluvia_Scatter")
    
    def _crear_grafico_histograma(self, ventana, df_rend):
        """Crea histograma de distribución"""
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        n, bins, patches = ax.hist(df_rend['rendimiento'], bins=12, color='skyblue', 
                                  alpha=0.7, edgecolor='black', linewidth=1)
        
        # Colorear barras según valor
        for i, p in enumerate(patches):
            p.set_facecolor(plt.cm.viridis(i / len(patches)))
        
        ax.axvline(np.mean(df_rend['rendimiento']), color='red', linestyle='--', linewidth=2,
                  label=f'Promedio: {np.mean(df_rend["rendimiento"]):.1f} t/ha')
        ax.axvline(np.median(df_rend['rendimiento']), color='orange', linestyle='--', linewidth=2,
                  label=f'Mediana: {np.median(df_rend["rendimiento"]):.1f} t/ha')
        
        ax.set_xlabel('Rendimiento (t/ha)', fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.set_title('Distribución de Rendimientos de Cultivos', fontweight='bold', fontsize=16)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Agregar estadísticas
        stats_text = f'Total: {len(df_rend)} cultivos\nDesv. Std: {np.std(df_rend["rendimiento"]):.1f} t/ha'
        ax.text(0.7, 0.8, stats_text, transform=ax.transAxes, fontsize=11,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
        
        fig.tight_layout()
        self._mostrar_canvas(fig, ventana, "Histograma")
    
    def _crear_grafico_box_plot(self, ventana, df_rend):
        """Crea box plot por nivel de lluvia"""
        fig = Figure(figsize=(10, 8), dpi=100)
        ax = fig.add_subplot(111)
        
        lluvia_data = [df_rend[df_rend['lluvia']==nivel]['rendimiento'].tolist() 
                      for nivel in ['Baja', 'Media', 'Alta']]
        
        box_plot = ax.boxplot(lluvia_data, labels=['Baja', 'Media', 'Alta'], 
                             patch_artist=True, notch=True)
        
        colors = ['lightcoral', 'lightblue', 'lightgreen']
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax.set_xlabel('Nivel de Lluvia', fontsize=12)
        ax.set_ylabel('Rendimiento (t/ha)', fontsize=12)
        ax.set_title('Distribución de Rendimientos por Nivel de Lluvia', fontweight='bold', fontsize=16)
        ax.grid(True, alpha=0.3)
        
        # Agregar estadísticas por nivel
        for i, nivel in enumerate(['Baja', 'Media', 'Alta']):
            data = df_rend[df_rend['lluvia']==nivel]['rendimiento']
            promedio = data.mean()
            ax.text(i+1, promedio, f'μ={promedio:.1f}', ha='center', va='bottom',
                   fontweight='bold', color='red', fontsize=10)
        
        fig.tight_layout()
        self._mostrar_canvas(fig, ventana, "Box_Plot")
    
    def _crear_panel_estadisticas(self, ventana, df_rend):
        """Crea panel con estadísticas completas"""
        # Crear scrolled text
        texto_stats = scrolledtext.ScrolledText(ventana, font=("Courier", 11))
        texto_stats.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generar estadísticas completas
        stats = f"""
╔══════════════════════════════════════════════════════════════╗
║                    ESTADÍSTICAS COMPLETAS                    ║
║                   Rendimientos de Cultivos                   ║
╚══════════════════════════════════════════════════════════════╝

RESUMEN GENERAL:
    Total de cultivos: {len(df_rend)}
    Rendimiento promedio: {df_rend['rendimiento'].mean():.2f} t/ha
    Rendimiento máximo: {df_rend['rendimiento'].max():.2f} t/ha
    Rendimiento mínimo: {df_rend['rendimiento'].min():.2f} t/ha
    Desviación estándar: {df_rend['rendimiento'].std():.2f} t/ha
    Coeficiente de variación: {(df_rend['rendimiento'].std()/df_rend['rendimiento'].mean()*100):.1f}%

TOP 10 CULTIVOS:
"""
        
        top_10 = df_rend.nlargest(10, 'rendimiento')
        for i, (_, cultivo) in enumerate(top_10.iterrows(), 1):
            stats += f"    {i:2d}. {cultivo['cultivo']:<20} {cultivo['rendimiento']:>6.1f} t/ha\n"
        
        stats += f"""
ANÁLISIS POR TEMPORADA:
"""
        
        for temporada in df_rend['temporada'].unique():
            temp_data = df_rend[df_rend['temporada'] == temporada]
            stats += f"""    {temporada}:
        Cultivos: {len(temp_data)}
        Promedio: {temp_data['rendimiento'].mean():.1f} t/ha
        Mejor: {temp_data.loc[temp_data['rendimiento'].idxmax(), 'cultivo']}
        
"""
        
        stats += f"""ANÁLISIS POR NIVEL DE LLUVIA:
"""
        
        for nivel in ['Baja', 'Media', 'Alta']:
            if nivel in df_rend['lluvia'].unique():
                lluvia_data = df_rend[df_rend['lluvia'] == nivel]
                stats += f"""    {nivel} lluvia:
        Cultivos: {len(lluvia_data)}
        Promedio: {lluvia_data['rendimiento'].mean():.1f} t/ha
        Máximo: {lluvia_data['rendimiento'].max():.1f} t/ha
        Mejor: {lluvia_data.loc[lluvia_data['rendimiento'].idxmax(), 'cultivo']}
        
"""
        
        stats += f"""CULTIVOS DESTACADOS:
    Mejor rendimiento: {df_rend.loc[df_rend['rendimiento'].idxmax(), 'cultivo']} ({df_rend['rendimiento'].max():.1f} t/ha)
    Más consistentes: {', '.join(df_rend.nlargest(3, 'rendimiento')['cultivo'].tolist())}
    
Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        texto_stats.insert(tk.END, stats)
        
        # Botón para guardar estadísticas
        frame_botones = tk.Frame(ventana)
        frame_botones.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botones, text="Exportar Estadísticas", 
                 command=lambda: self._exportar_estadisticas(stats),
                 bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    def _mostrar_canvas(self, fig, ventana, nombre_grafico):
        """Función helper para mostrar canvas con toolbar"""
        canvas = FigureCanvasTk(fig, ventana)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Toolbar
        try:
            toolbar = NavigationToolbar2Tk(canvas, ventana)
            toolbar.update()
        except:
            pass
        
        # Botones
        frame_botones = tk.Frame(ventana)
        frame_botones.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(frame_botones, text="Guardar Gráfico", 
                 command=lambda: self.guardar_graficos(fig, {'cultivo': nombre_grafico}),
                 bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame_botones, text="Cerrar", 
                 command=ventana.destroy,
                 bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
    
    def _exportar_estadisticas(self, stats):
        """Exporta estadísticas a archivo de texto"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"estadisticas_rendimientos_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(stats)
            
            messagebox.showinfo("Exportado", f"Estadísticas guardadas en: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def mostrar_todos_graficos_rendimientos(self, ventana_padre):
        """Muestra todos los gráficos en una ventana (función original mejorada)"""
        try:
            ventana_todos = tk.Toplevel(ventana_padre)
            ventana_todos.title("Todos los Análisis de Rendimientos")
            ventana_todos.geometry("1400x900")
            ventana_todos.grab_set()
            
            # Frame para controles
            frame_controles = tk.Frame(ventana_todos)
            frame_controles.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Label(frame_controles, text="Análisis Completo de Rendimientos - Todos los Gráficos", 
                    font=("Arial", 16, "bold")).pack()
            
            # Crear figura con múltiples subplots
            fig = Figure(figsize=(16, 11), dpi=100)
            
            # Preparar datos
            rendimientos = []
            nombres = []
            temporadas = []
            lluvias = []
            
            for _, fila in self.df.iterrows():
                try:
                    valor = float(fila['rendimiento_promedio'].split()[0])
                    rendimientos.append(valor)
                    nombres.append(fila['cultivo'])
                    temporadas.append(fila['temporada_siembra'])
                    lluvias.append(fila['lluvia'])
                except:
                    continue
            
            if not rendimientos:
                fig.text(0.5, 0.5, 'No hay datos de rendimiento disponibles', 
                        ha='center', va='center', fontsize=14)
            else:
                # Subplot 1: Top 15 rendimientos (gráfico de barras)
                ax1 = fig.add_subplot(2, 3, 1)
                df_rend = pd.DataFrame({
                    'cultivo': nombres, 
                    'rendimiento': rendimientos,
                    'temporada': temporadas,
                    'lluvia': lluvias
                })
                
                top_15 = df_rend.nlargest(15, 'rendimiento')
                colors = plt.cm.viridis(np.linspace(0, 1, len(top_15)))
                
                bars = ax1.bar(range(len(top_15)), top_15['rendimiento'], color=colors)
                ax1.set_title('Top 15 Cultivos por Rendimiento', fontweight='bold', fontsize=12)
                ax1.set_xlabel('Cultivos')
                ax1.set_ylabel('Rendimiento (t/ha)')
                ax1.set_xticks(range(len(top_15)))
                ax1.set_xticklabels(top_15['cultivo'], rotation=45, ha='right', fontsize=9)
                
                # Agregar valores en las barras
                for bar, valor in zip(bars, top_15['rendimiento']):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=8)
                
                # Subplot 2: Distribución por temporadas (gráfico circular)
                ax2 = fig.add_subplot(2, 3, 2)
                temp_counts = df_rend.groupby('temporada')['rendimiento'].mean()
                colors_pie = plt.cm.Set3(np.linspace(0, 1, len(temp_counts)))
                
                wedges, texts, autotexts = ax2.pie(temp_counts.values, labels=temp_counts.index, 
                                                  autopct='%1.1f%%', colors=colors_pie, startangle=90)
                ax2.set_title('Rendimiento Promedio por Temporada', fontweight='bold', fontsize=12)
                
                for autotext in autotexts:
                    autotext.set_fontsize(9)
                    autotext.set_color('white')
                    autotext.set_weight('bold')
                
                # Subplot 3: Rendimiento vs lluvia (scatter plot)
                ax3 = fig.add_subplot(2, 3, 3)
                lluvia_map = {'Baja': 1, 'Media': 2, 'Alta': 3}
                lluvia_numerica = [lluvia_map.get(l, 0) for l in df_rend['lluvia']]
                
                scatter = ax3.scatter(lluvia_numerica, df_rend['rendimiento'], 
                                    c=df_rend['rendimiento'], cmap='coolwarm', 
                                    alpha=0.7, s=60)
                ax3.set_xlabel('Nivel de Lluvia')
                ax3.set_ylabel('Rendimiento (t/ha)')
                ax3.set_title('Rendimiento vs Nivel de Lluvia', fontweight='bold', fontsize=12)
                ax3.set_xticks([1, 2, 3])
                ax3.set_xticklabels(['Baja', 'Media', 'Alta'])
                ax3.grid(True, alpha=0.3)
                
                # Colorbar para scatter plot
                plt.colorbar(scatter, ax=ax3, label='Rendimiento (t/ha)')
                
                # Subplot 4: Histograma de distribución de rendimientos
                ax4 = fig.add_subplot(2, 3, 4)
                ax4.hist(rendimientos, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
                ax4.axvline(np.mean(rendimientos), color='red', linestyle='--', 
                           label=f'Promedio: {np.mean(rendimientos):.1f} t/ha')
                ax4.set_xlabel('Rendimiento (t/ha)')
                ax4.set_ylabel('Frecuencia')
                ax4.set_title('Distribución de Rendimientos', fontweight='bold', fontsize=12)
                ax4.legend()
                ax4.grid(True, alpha=0.3)
                
                # Subplot 5: Box plot por nivel de lluvia
                ax5 = fig.add_subplot(2, 3, 5)
                lluvia_data = [df_rend[df_rend['lluvia']==nivel]['rendimiento'].tolist() 
                              for nivel in ['Baja', 'Media', 'Alta']]
                box_plot = ax5.boxplot(lluvia_data, labels=['Baja', 'Media', 'Alta'], patch_artist=True)
                
                colors_box = ['lightcoral', 'lightblue', 'lightgreen']
                for patch, color in zip(box_plot['boxes'], colors_box):
                    patch.set_facecolor(color)
                
                ax5.set_xlabel('Nivel de Lluvia')
                ax5.set_ylabel('Rendimiento (t/ha)')
                ax5.set_title('Distribución por Nivel de Lluvia', fontweight='bold', fontsize=12)
                ax5.grid(True, alpha=0.3)
                
                # Subplot 6: Estadísticas resumidas (texto)
                ax6 = fig.add_subplot(2, 3, 6)
                ax6.axis('off')
                
                stats_text = f"""ESTADÍSTICAS GENERALES

Total de cultivos: {len(rendimientos)}
Rendimiento promedio: {np.mean(rendimientos):.2f} t/ha
Rendimiento máximo: {np.max(rendimientos):.2f} t/ha
Rendimiento mínimo: {np.min(rendimientos):.2f} t/ha
Desviación estándar: {np.std(rendimientos):.2f} t/ha

CULTIVOS DESTACADOS:
Mejor: {top_15.iloc[0]['cultivo']} ({top_15.iloc[0]['rendimiento']:.1f} t/ha)
Top 3: {', '.join(top_15.head(3)['cultivo'].tolist())}

POR TEMPORADA:
{chr(10).join([f'{temp}: {count:.1f} t/ha promedio' for temp, count in temp_counts.items()])}
"""
                
                ax6.text(0.05, 0.95, stats_text, transform=ax6.transAxes, fontsize=10,
                        verticalalignment='top', fontfamily='monospace',
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
            
            # Ajustar layout
            fig.suptitle('Análisis Completo de Rendimientos - Cultivos de Panamá', 
                        fontsize=18, fontweight='bold')
            fig.tight_layout(rect=[0, 0.03, 1, 0.96], pad=3.0)
            
            # Crear canvas y mostrar
            canvas = FigureCanvasTk(fig, ventana_todos)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            # Toolbar para navegación
            try:
                toolbar = NavigationToolbar2Tk(canvas, ventana_todos)
                toolbar.update()
            except:
                pass
            
            # Botones de control
            frame_botones = tk.Frame(ventana_todos)
            frame_botones.pack(fill=tk.X, padx=10, pady=5)
            
            tk.Button(frame_botones, text="Guardar Análisis Completo", 
                     command=lambda: self.guardar_graficos(fig, {'cultivo': 'Análisis_Completo_Rendimientos'}),
                     bg="green", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(frame_botones, text="Cerrar", 
                     command=ventana_todos.destroy,
                     bg="red", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, padx=5)
            
            if self.barra_estado:
                self.barra_estado.config(text="Análisis completo de rendimientos generado")
            
        except Exception as e:
            print(f"Error en mostrar_todos_graficos_rendimientos: {e}")
            messagebox.showerror("Error", f"Error al generar análisis completo: {str(e)}")
            if self.barra_estado:
                self.barra_estado.config(text="Error al generar análisis completo")