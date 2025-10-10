import customtkinter as ctk
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class VisualizationFrame(ctk.CTkFrame):
    def __init__(self, master, df_cuant=None, df_desc=None, df_original=None):
        super().__init__(master)
        self.master = master
        self.df_cuantitativo = df_cuant
        self.df_descriptivo = df_desc
        self.df_original = df_original
        self.canvas_actual = None
        self.fig_actual = None
        
        self.setup_ui()

    def __del__(self):
        """Destructor para limpiar recursos"""
        self.cleanup()

    def cleanup(self):
        """Limpia recursos antes de destruir"""
        try:
            if self.canvas_actual is not None:
                try:
                    self.canvas_actual.get_tk_widget().destroy()
                except:
                    pass
                self.canvas_actual = None
            
            if self.fig_actual is not None:
                try:
                    plt.close(self.fig_actual)
                except:
                    pass
                self.fig_actual = None
            
            plt.close('all')
        except:
            pass

    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))

        title = ctk.CTkLabel(
            header,
            text="📊 Visualización de Datos",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        )
        title.pack(side="left")

        # Frame de botones de navegación
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=20, pady=10)

        # Botones de diferentes visualizaciones
        self.btn_distribucion = ctk.CTkButton(
            nav_frame,
            text="📈 Distribuciones",
            command=self.mostrar_distribuciones,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_distribucion.pack(side="left", padx=5)

        self.btn_correlacion = ctk.CTkButton(
            nav_frame,
            text="🔗 Correlaciones",
            command=self.mostrar_correlaciones,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_correlacion.pack(side="left", padx=5)

        self.btn_comparacion = ctk.CTkButton(
            nav_frame,
            text="⚖️ Comparaciones",
            command=self.mostrar_comparaciones,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_comparacion.pack(side="left", padx=5)

        self.btn_target = ctk.CTkButton(
            nav_frame,
            text="🎯 Análisis Target",
            command=self.mostrar_analisis_target,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_target.pack(side="left", padx=5)

        self.btn_estadisticas = ctk.CTkButton(
            nav_frame,
            text="📊 Estadísticas",
            command=self.mostrar_estadisticas,
            width=160,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_estadisticas.pack(side="left", padx=5)

        # Frame principal para contenido
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Mostrar vista inicial
        self.mostrar_distribuciones()

    def limpiar_contenido(self):
        """Limpia el frame de contenido"""
        try:
            # Limpiar canvas y figuras
            if self.canvas_actual is not None:
                try:
                    self.canvas_actual.get_tk_widget().destroy()
                except:
                    pass
                self.canvas_actual = None
            
            if self.fig_actual is not None:
                try:
                    plt.close(self.fig_actual)
                except:
                    pass
                self.fig_actual = None
            
            # Limpiar widgets del content_frame
            for widget in self.content_frame.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
        except:
            pass

    def mostrar_distribuciones(self):
        """Muestra histogramas de las variables principales"""
        self.limpiar_contenido()

        # Título
        label = ctk.CTkLabel(
            self.content_frame,
            text="Distribución de Variables Principales",
            font=("Segoe UI", 18, "bold"),
            text_color="#00BFFF"
        )
        label.pack(pady=10)

        # Frame para el gráfico
        graph_frame = ctk.CTkFrame(self.content_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Crear figura
        self.fig_actual = Figure(figsize=(12, 8), facecolor='#2b2b2b')
        
        # Variables numéricas principales del dataset original
        numeric_cols = ['age', 'trestbps', 'chol', 'thalach', 'oldpeak']
        available_cols = [col for col in numeric_cols if col in self.df_original.columns]
        
        if not available_cols:
            available_cols = self.df_original.select_dtypes(include=[np.number]).columns[:6]
        
        n_cols = min(3, len(available_cols))
        n_rows = (len(available_cols) + n_cols - 1) // n_cols
        
        for i, col in enumerate(available_cols[:6], 1):
            ax = self.fig_actual.add_subplot(n_rows, n_cols, i)
            ax.hist(self.df_original[col].dropna(), bins=30, color='#0078D7', edgecolor='white', alpha=0.7)
            ax.set_title(col, color='white', fontsize=12, fontweight='bold')
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.set_xlabel('Valor', color='white')
            ax.set_ylabel('Frecuencia', color='white')
        
        self.fig_actual.tight_layout()

        # Mostrar en canvas
        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=graph_frame)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_correlaciones(self):
        """Muestra matriz de correlación"""
        self.limpiar_contenido()

        label = ctk.CTkLabel(
            self.content_frame,
            text="Matriz de Correlación",
            font=("Segoe UI", 18, "bold"),
            text_color="#00BFFF"
        )
        label.pack(pady=10)

        graph_frame = ctk.CTkFrame(self.content_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig_actual = Figure(figsize=(12, 10), facecolor='#2b2b2b')
        ax = self.fig_actual.add_subplot(111)

        # Seleccionar solo columnas numéricas
        numeric_df = self.df_cuantitativo.select_dtypes(include=[np.number])
        
        # Limitar a las primeras 15 columnas si hay muchas
        if len(numeric_df.columns) > 15:
            numeric_df = numeric_df.iloc[:, :15]

        corr = numeric_df.corr()

        # Crear heatmap
        sns.heatmap(
            corr,
            annot=True,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax,
            annot_kws={'size': 8}
        )
        
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.set_title('Correlación entre Variables', color='white', fontsize=14, fontweight='bold', pad=20)
        
        # Rotar etiquetas
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

        self.fig_actual.tight_layout()

        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=graph_frame)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_comparaciones(self):
        """Muestra comparaciones entre variables"""
        self.limpiar_contenido()

        label = ctk.CTkLabel(
            self.content_frame,
            text="Comparación de Variables Clave",
            font=("Segoe UI", 18, "bold"),
            text_color="#00BFFF"
        )
        label.pack(pady=10)

        graph_frame = ctk.CTkFrame(self.content_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig_actual = Figure(figsize=(12, 8), facecolor='#2b2b2b')

        # Boxplots comparativos
        variables = ['age', 'chol', 'trestbps', 'thalach']
        available_vars = [v for v in variables if v in self.df_original.columns]

        for i, var in enumerate(available_vars[:4], 1):
            ax = self.fig_actual.add_subplot(2, 2, i)
            
            if 'target' in self.df_original.columns or 'num' in self.df_original.columns:
                target_col = 'target' if 'target' in self.df_original.columns else 'num'
                
                data_to_plot = [
                    self.df_original[self.df_original[target_col] == 0][var].dropna(),
                    self.df_original[self.df_original[target_col] == 1][var].dropna()
                ]
                
                bp = ax.boxplot(data_to_plot, labels=['Sin riesgo', 'Con riesgo'],
                              patch_artist=True)
                
                for patch, color in zip(bp['boxes'], ['#00AA00', '#FF4444']):
                    patch.set_facecolor(color)
                    patch.set_alpha(0.7)
            else:
                ax.boxplot([self.df_original[var].dropna()])
            
            ax.set_title(var, color='white', fontsize=12, fontweight='bold')
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.2)

        self.fig_actual.tight_layout()

        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=graph_frame)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_analisis_target(self):
        """Muestra análisis específico de la variable objetivo"""
        self.limpiar_contenido()

        label = ctk.CTkLabel(
            self.content_frame,
            text="Análisis de Variable Objetivo (Target)",
            font=("Segoe UI", 18, "bold"),
            text_color="#00BFFF"
        )
        label.pack(pady=10)

        # Detectar columna target
        target_col = None
        for col in ['target', 'num', 'disease']:
            if col in self.df_original.columns:
                target_col = col
                break

        if target_col is None:
            msg_label = ctk.CTkLabel(
                self.content_frame,
                text="⚠️ No se encontró columna de target en el dataset",
                font=("Segoe UI", 14),
                text_color="#FFAA00"
            )
            msg_label.pack(pady=50)
            return

        graph_frame = ctk.CTkFrame(self.content_frame)
        graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.fig_actual = Figure(figsize=(12, 6), facecolor='#2b2b2b')

        # Gráfico 1: Distribución del target
        ax1 = self.fig_actual.add_subplot(1, 2, 1)
        counts = self.df_original[target_col].value_counts()
        colors = ['#00AA00', '#FF4444']
        ax1.bar(counts.index, counts.values, color=colors[:len(counts)], alpha=0.7, edgecolor='white')
        ax1.set_title('Distribución de Casos', color='white', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Categoría', color='white')
        ax1.set_ylabel('Frecuencia', color='white')
        ax1.set_facecolor('#1e1e1e')
        ax1.tick_params(colors='white')
        ax1.spines['bottom'].set_color('white')
        ax1.spines['left'].set_color('white')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Añadir porcentajes
        total = counts.sum()
        for i, v in enumerate(counts.values):
            ax1.text(i, v + 5, f'{v}\n({v/total*100:.1f}%)', 
                    ha='center', va='bottom', color='white', fontweight='bold')

        # Gráfico 2: Pie chart
        ax2 = self.fig_actual.add_subplot(1, 2, 2)
        ax2.pie(counts.values, labels=counts.index, autopct='%1.1f%%',
               colors=colors[:len(counts)], startangle=90,
               textprops={'color': 'white', 'fontsize': 12})
        ax2.set_title('Proporción de Casos', color='white', fontsize=14, fontweight='bold')

        self.fig_actual.tight_layout()

        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=graph_frame)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)

    def mostrar_estadisticas(self):
        """Muestra estadísticas descriptivas completas"""
        self.limpiar_contenido()

        label = ctk.CTkLabel(
            self.content_frame,
            text="Estadísticas Descriptivas Detalladas",
            font=("Segoe UI", 18, "bold"),
            text_color="#00BFFF"
        )
        label.pack(pady=10)

        # Frame scrollable
        scrollable = ctk.CTkScrollableFrame(self.content_frame)
        scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Estadísticas del dataset cuantitativo
        stats_cuant = self.df_cuantitativo.describe()
        
        # Título sección cuantitativa
        label_cuant = ctk.CTkLabel(
            scrollable,
            text="📊 Dataset Cuantitativo (Procesado)",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        label_cuant.pack(pady=(10, 5), anchor="w")

        # Mostrar en formato de texto
        stats_text = ctk.CTkTextbox(scrollable, height=250, font=("Courier", 10))
        stats_text.pack(fill="x", pady=5)
        stats_text.insert("1.0", stats_cuant.to_string())
        stats_text.configure(state="disabled")

        # Estadísticas del dataset descriptivo
        label_desc = ctk.CTkLabel(
            scrollable,
            text="📋 Dataset Descriptivo (Original)",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        label_desc.pack(pady=(20, 5), anchor="w")

        stats_desc = self.df_descriptivo.describe()
        stats_text2 = ctk.CTkTextbox(scrollable, height=250, font=("Courier", 10))
        stats_text2.pack(fill="x", pady=5)
        stats_text2.insert("1.0", stats_desc.to_string())
        stats_text2.configure(state="disabled")

        # Información adicional
        label_info = ctk.CTkLabel(
            scrollable,
            text="ℹ️ Información General",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        label_info.pack(pady=(20, 5), anchor="w")

        info_text = f"""
        Dataset Cuantitativo:
        - Dimensiones: {self.df_cuantitativo.shape[0]} filas × {self.df_cuantitativo.shape[1]} columnas
        - Valores nulos: {self.df_cuantitativo.isnull().sum().sum()}
        - Memoria: {self.df_cuantitativo.memory_usage(deep=True).sum() / 1024:.2f} KB

        Dataset Descriptivo:
        - Dimensiones: {self.df_descriptivo.shape[0]} filas × {self.df_descriptivo.shape[1]} columnas
        - Valores nulos: {self.df_descriptivo.isnull().sum().sum()}
        - Memoria: {self.df_descriptivo.memory_usage(deep=True).sum() / 1024:.2f} KB
        """

        info_label = ctk.CTkLabel(
            scrollable,
            text=info_text,
            font=("Courier", 11),
            justify="left",
            text_color="#CCCCCC"
        )
        info_label.pack(pady=10, anchor="w")