import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
import os

class EDAFrame(ctk.CTkFrame):
    def __init__(self, master, df_cuant=None, df_desc=None):
        super().__init__(master)
        self.master = master
        self.df_cuant = df_cuant.copy() if df_cuant is not None else None
        self.df_desc = df_desc.copy() if df_desc is not None else None
        self.canvas_actual = None
        self.fig_actual = None
        
        # Variables para clustering
        self.k_optimo = None
        self.clusters = None
        
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
            
            # Limpiar frame_grafico
            if hasattr(self, 'frame_grafico'):
                for widget in self.frame_grafico.winfo_children():
                    try:
                        widget.destroy()
                    except:
                        pass
            
            plt.close('all')
        except:
            pass

    def setup_ui(self):
        """Configura la interfaz principal con scroll"""
        # Header compacto
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 5))

        title = ctk.CTkLabel(
            header,
            text="📊 Análisis Exploratorio de Datos (EDA)",
            font=("Segoe UI", 20, "bold"),
            text_color="#00BFFF"
        )
        title.pack(side="left")

        # Frame de botones más compacto
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.btn_correlacion = ctk.CTkButton(
            btn_frame,
            text="📈 Correlación",
            command=self.mostrar_correlacion,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_correlacion.pack(side="left", padx=5)

        self.btn_clustering = ctk.CTkButton(
            btn_frame,
            text="🎯 Segmentación",
            command=self.mostrar_clustering,
            width=150,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#9333EA",
            hover_color="#7C3AED"
        )
        self.btn_clustering.pack(side="left", padx=5)

        self.btn_exportar = ctk.CTkButton(
            btn_frame,
            text="💾 Exportar",
            command=self.exportar_resultados,
            width=130,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#00AA00",
            hover_color="#008800"
        )
        self.btn_exportar.pack(side="left", padx=5)

        # Frame principal con dos columnas
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Columna izquierda: Log CON SCROLL
        left_frame = ctk.CTkFrame(content_frame, width=450)
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)

        log_label = ctk.CTkLabel(
            left_frame,
            text="📝 Resultados del Análisis",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        )
        log_label.pack(pady=5)

        # ScrollableFrame para el log
        self.log_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="#2b2b2b")
        self.log_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Text widget dentro del scrollable frame
        self.text_info = tk.Text(
            self.log_scroll,
            bg="#2b2b2b",
            fg="white",
            font=("Courier", 9),
            wrap="word",
            borderwidth=0,
            highlightthickness=0
        )
        self.text_info.pack(fill="both", expand=True)

        # Columna derecha: Gráficos CON SCROLL
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        graph_label = ctk.CTkLabel(
            right_frame,
            text="📊 Visualizaciones",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        )
        graph_label.pack(pady=5)

        # ScrollableFrame para gráficos
        self.frame_grafico = ctk.CTkScrollableFrame(right_frame, fg_color="#2b2b2b")
        self.frame_grafico.pack(fill="both", expand=True, padx=5, pady=(0, 5))

        # Mensaje inicial
        self.log("=" * 60)
        self.log("MÓDULO DE ANÁLISIS EXPLORATORIO DE DATOS")
        self.log("=" * 60)
        self.log("\n✅ Datos cargados correctamente")
        self.log(f"📊 Dataset: {self.df_cuant.shape[0]} filas × {self.df_cuant.shape[1]} cols")
        self.log("\n💡 Selecciona un tipo de análisis")

    def log(self, mensaje):
        """Añade mensaje al log"""
        try:
            self.text_info.insert(tk.END, mensaje + "\n")
            self.text_info.see(tk.END)
        except:
            pass

    def limpiar_log(self):
        """Limpia el área de log"""
        try:
            self.text_info.delete("1.0", tk.END)
        except:
            pass

    def limpiar_graficos(self):
        """Limpia el área de gráficos de forma segura"""
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
            
            for widget in self.frame_grafico.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
        except:
            pass

    def verificar_archivos_csv(self):
        """Verifica que existan los archivos CSV necesarios"""
        cuant_exists = os.path.exists('dataset_cuantitativo.csv')
        desc_exists = os.path.exists('dataset_descriptivo.csv')
        
        if not cuant_exists or not desc_exists:
            archivos_faltantes = []
            if not cuant_exists:
                archivos_faltantes.append("dataset_cuantitativo.csv")
            if not desc_exists:
                archivos_faltantes.append("dataset_descriptivo.csv")
            
            mensaje_error = "❌ Error: No se encontraron los archivos necesarios:\n\n"
            mensaje_error += "\n".join([f"• {archivo}" for archivo in archivos_faltantes])
            mensaje_error += "\n\n⚠️ Por favor, ejecuta el preprocesamiento y guarda los CSVs primero."
            
            messagebox.showerror("Archivos no encontrados", mensaje_error)
            self.log("\n" + "=" * 60)
            self.log("❌ ERROR: ARCHIVOS CSV NO ENCONTRADOS")
            self.log("=" * 60)
            self.log("\nArchivos faltantes:")
            for archivo in archivos_faltantes:
                self.log(f"  ✗ {archivo}")
            self.log("\n⚠️ Solución:")
            self.log("  1. Ve a la sección 'Preprocesar'")
            self.log("  2. Ejecuta el preprocesamiento")
            self.log("  3. Haz clic en 'Guardar CSVs'")
            self.log("  4. Regresa aquí para continuar")
            
            return False
        
        return True

    def mostrar_correlacion(self):
        """Análisis de correlación con la variable objetivo"""
        self.limpiar_log()
        self.limpiar_graficos()
        
        # Verificar archivos antes de continuar
        if not self.verificar_archivos_csv():
            return

        self.log("=" * 60)
        self.log("ANÁLISIS DE CORRELACIÓN")
        self.log("=" * 60)
        
        try:
            # Cargar desde CSV
            self.log("\n📂 Cargando dataset_cuantitativo.csv...")
            df_cuant = pd.read_csv('dataset_cuantitativo.csv')
            self.log(f"✓ Cargado: {df_cuant.shape[0]} filas × {df_cuant.shape[1]} columnas")
            
            # Calcular matriz de correlación
            correlation_matrix = df_cuant.corr()
            
            # Verificar si existe la columna objetivo
            if 'Enfermedad_Cardiaca' not in df_cuant.columns:
                self.log("\n⚠️ No se encontró la columna 'Enfermedad_Cardiaca'")
                messagebox.showwarning("Advertencia", "No se encontró la variable objetivo")
                return
            
            # Correlaciones con variable objetivo
            correlaciones_target = correlation_matrix['Enfermedad_Cardiaca'].sort_values(ascending=False)
            
            self.log("\n📊 Correlaciones con Enfermedad_Cardiaca:")
            self.log("-" * 60)
            
            for var, corr in correlaciones_target.items():
                if var != 'Enfermedad_Cardiaca':
                    self.log(f"{var:45s}: {corr:+.4f}")
            
            # Identificar correlaciones más fuertes
            self.log("\n🔝 TOP 10 Correlaciones Positivas:")
            correlaciones_positivas = correlaciones_target[correlaciones_target > 0].drop('Enfermedad_Cardiaca')
            for i, (var, corr) in enumerate(correlaciones_positivas.head(10).items(), 1):
                self.log(f"  {i:2d}. {var:40s}: +{corr:.4f}")
            
            self.log("\n🔻 TOP 10 Correlaciones Negativas:")
            correlaciones_negativas = correlaciones_target[correlaciones_target < 0]
            for i, (var, corr) in enumerate(correlaciones_negativas.head(10).items(), 1):
                self.log(f"  {i:2d}. {var:40s}: {corr:.4f}")
            
            # Crear visualización
            self.fig_actual = Figure(figsize=(9, 7), facecolor='#2b2b2b', dpi=100)
            ax = self.fig_actual.add_subplot(111)
            
            # Tomar solo las correlaciones más fuertes
            correlaciones_sorted = correlaciones_target.drop('Enfermedad_Cardiaca').sort_values()
            top_correlaciones = pd.concat([
                correlaciones_sorted.head(8),
                correlaciones_sorted.tail(8)
            ]).sort_values()
            
            colors = ['#FF4444' if x < 0 else '#00AA00' for x in top_correlaciones]
            
            y_pos = np.arange(len(top_correlaciones))
            bars = ax.barh(y_pos, top_correlaciones.values, color=colors, alpha=0.85, 
                          edgecolor='white', linewidth=1.5)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(top_correlaciones.index, fontsize=9)
            ax.set_xlabel('Coeficiente de Correlación', fontsize=11, fontweight='bold', color='white')
            ax.set_title('Correlaciones con Enfermedad Cardíaca\n(Top 16 Variables)', 
                        fontsize=13, fontweight='bold', color='#00BFFF', pad=15)
            ax.axvline(x=0, color='white', linestyle='-', linewidth=2)
            ax.grid(axis='x', alpha=0.3, color='white', linestyle='--')
            
            # Añadir valores en las barras
            for bar, val in zip(bars, top_correlaciones.values):
                width = bar.get_width()
                label_x_pos = width + 0.01 if width > 0 else width - 0.01
                alignment = 'left' if width > 0 else 'right'
                ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, 
                       f'{val:.3f}', ha=alignment, va='center', 
                       color='white', fontsize=8, fontweight='bold')
            
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white', labelsize=9)
            for spine in ax.spines.values():
                spine.set_color('white')
                spine.set_linewidth(1.5)
            
            self.fig_actual.tight_layout(pad=1.5)
            
            # Mostrar en canvas
            self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=self.frame_grafico)
            self.canvas_actual.draw()
            self.canvas_actual.get_tk_widget().pack(fill="both", expand=False, pady=10)
            
            self.log("\n✅ Análisis de correlación completado")
            
        except Exception as e:
            self.log(f"\n❌ Error en análisis de correlación: {str(e)}")
            messagebox.showerror("Error", f"Error en el análisis:\n{str(e)}")

    def mostrar_clustering(self):
        """Análisis de clustering/segmentación"""
        self.limpiar_log()
        self.limpiar_graficos()
        
        # Verificar archivos antes de continuar
        if not self.verificar_archivos_csv():
            return

        self.log("=" * 60)
        self.log("ANÁLISIS DE CLUSTERING (K-MEANS)")
        self.log("=" * 60)
        
        try:
            # Cargar desde CSV
            self.log("\n📂 Cargando dataset_cuantitativo.csv...")
            df_cuant = pd.read_csv('dataset_cuantitativo.csv')
            self.log(f"✓ Cargado: {df_cuant.shape[0]} filas × {df_cuant.shape[1]} columnas")
            
            # Preparar datos
            X = df_cuant.drop('Enfermedad_Cardiaca', axis=1)
            
            self.log(f"\n📊 Variables utilizadas: {X.shape[1]}")
            self.log(f"📊 Observaciones: {X.shape[0]}")
            
            # Normalizar datos
            self.log("\n🔧 Normalizando datos...")
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Determinar K óptimo
            self.log("\n🎯 Evaluando número óptimo de clusters...")
            self.log("-" * 60)
            
            inertias = []
            silhouette_scores = []
            K_range = range(2, 11)
            
            for k in K_range:
                kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
                kmeans.fit(X_scaled)
                inertias.append(kmeans.inertia_)
                sil_score = silhouette_score(X_scaled, kmeans.labels_)
                silhouette_scores.append(sil_score)
                self.log(f"K={k}: Inercia={kmeans.inertia_:.2f}, Silueta={sil_score:.3f}")
            
            # K óptimo
            self.k_optimo = K_range[np.argmax(silhouette_scores)]
            self.log(f"\n⭐ K óptimo sugerido: {self.k_optimo}")
            self.log(f"   Mejor índice de Silueta: {max(silhouette_scores):.3f}")
            
            # Aplicar K-Means final
            self.log(f"\n🔄 Aplicando K-Means con K={self.k_optimo}...")
            kmeans_final = KMeans(n_clusters=self.k_optimo, random_state=42, n_init=10)
            self.clusters = kmeans_final.fit_predict(X_scaled)
            
            # Añadir clusters al dataframe
            df_temp = df_cuant.copy()
            df_temp['Cluster'] = self.clusters
            
            # PCA para visualización
            self.log("\n📉 Reducción dimensional con PCA...")
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            var_exp1 = pca.explained_variance_ratio_[0] * 100
            var_exp2 = pca.explained_variance_ratio_[1] * 100
            
            self.log(f"   PC1 explica: {var_exp1:.2f}%")
            self.log(f"   PC2 explica: {var_exp2:.2f}%")
            self.log(f"   Total explicado: {var_exp1 + var_exp2:.2f}%")
            
            # Caracterización de clusters
            self.log("\n" + "=" * 60)
            self.log("PERFIL DE CADA CLUSTER")
            self.log("=" * 60)
            
            vars_importantes = [
                'Edad', 'Presion_Arterial_Reposo', 'Colesterol',
                'Frecuencia_Cardiaca_Maxima', 'DepresionST_Ejercicio'
            ]
            
            for cluster_id in range(self.k_optimo):
                self.log(f"\n{'='*60}")
                self.log(f"CLUSTER {cluster_id}")
                self.log(f"{'='*60}")
                
                cluster_data = df_temp[df_temp['Cluster'] == cluster_id]
                n_pacientes = len(cluster_data)
                pct_enfermedad = cluster_data['Enfermedad_Cardiaca'].mean() * 100
                
                self.log(f"Número de pacientes: {n_pacientes} ({n_pacientes/len(df_temp)*100:.1f}% del total)")
                self.log(f"Prevalencia de enfermedad: {pct_enfermedad:.1f}%")
                self.log("\nCaracterísticas promedio:")
                self.log("-" * 60)
                
                for var in vars_importantes:
                    if var in cluster_data.columns:
                        self.log(f"{var:35s}: {cluster_data[var].mean():7.2f}")
                
                if 'Dolor_Inducido_Ejercicio' in cluster_data.columns:
                    pct = cluster_data['Dolor_Inducido_Ejercicio'].mean() * 100
                    self.log(f"\n{'Dolor_Inducido_Ejercicio (% Sí)':35s}: {pct:6.1f}%")
                
                if 'Glucemia_Ayunas_Mayor_120' in cluster_data.columns:
                    pct = cluster_data['Glucemia_Ayunas_Mayor_120'].mean() * 100
                    self.log(f"{'Glucemia_Ayunas_Mayor_120 (% Sí)':35s}: {pct:6.1f}%")
            
            # Crear visualización
            self.crear_grafico_clustering(df_temp)
            
            self.log("\n✅ Análisis de clustering completado")
            
        except Exception as e:
            self.log(f"\n❌ Error en clustering: {str(e)}")
            messagebox.showerror("Error", f"Error en el análisis:\n{str(e)}")

    def crear_grafico_clustering(self, df_temp):
        """Crea gráfica de distribución de enfermedad por cluster"""
        
        # Crear figura
        self.fig_actual = Figure(figsize=(9, 6), facecolor='#2b2b2b', dpi=100)
        ax = self.fig_actual.add_subplot(111)
        
        # Calcular distribución de enfermedad por cluster
        cluster_enfermedad = pd.crosstab(
            df_temp['Cluster'], 
            df_temp['Enfermedad_Cardiaca'], 
            normalize='index'
        ) * 100
        
        # Preparar datos para el gráfico de barras
        x = np.arange(self.k_optimo)
        width = 0.35
        
        # Barras para Sin Enfermedad y Con Enfermedad
        bars1 = ax.bar(x - width/2, cluster_enfermedad[0], width, 
                      label='Sin Enfermedad', color='#87CEEB', alpha=0.9, 
                      edgecolor='white', linewidth=2)
        bars2 = ax.bar(x + width/2, cluster_enfermedad[1], width, 
                      label='Con Enfermedad', color='#FA8072', alpha=0.9, 
                      edgecolor='white', linewidth=2)
        
        # Configurar ejes y título
        ax.set_xlabel('Cluster', fontsize=11, color='white', fontweight='bold')
        ax.set_ylabel('Porcentaje (%)', fontsize=11, color='white', fontweight='bold')
        ax.set_title('Distribución de Enfermedad Cardíaca por Cluster', 
                    fontsize=13, fontweight='bold', color='#00BFFF', pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels([f'Cluster {i}' for i in range(self.k_optimo)], fontsize=10)
        ax.set_ylim(0, 110)
        ax.legend(title='Estado', fontsize=10, title_fontsize=10, loc='upper right')
        ax.grid(axis='y', alpha=0.3, color='white', linestyle='--')
        
        # Añadir valores encima de las barras
        def add_values(bars):
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                       f'{height:.1f}%',
                       ha='center', va='bottom', color='white', 
                       fontsize=9, fontweight='bold')
        
        add_values(bars1)
        add_values(bars2)
        
        # Estilo del gráfico
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white', labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('white')
            spine.set_linewidth(1.5)
        
        self.fig_actual.tight_layout(pad=1.5)
        
        # Mostrar en canvas
        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=self.frame_grafico)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=False, pady=10)

    def exportar_resultados(self):
        """Exporta los resultados del análisis"""
        try:
            # Verificar que existan los archivos base
            if not self.verificar_archivos_csv():
                return
            
            archivos_exportados = []
            
            # Cargar datos desde CSV
            df_cuant = pd.read_csv('dataset_cuantitativo.csv')
            
            # Exportar correlaciones
            if 'Enfermedad_Cardiaca' in df_cuant.columns:
                correlation_matrix = df_cuant.corr()
                correlaciones_target = correlation_matrix['Enfermedad_Cardiaca'].sort_values(ascending=False)
                correlaciones_target.to_csv('analisis_correlaciones.csv', header=['Correlacion'])
                archivos_exportados.append('analisis_correlaciones.csv')
                self.log("\n💾 Correlaciones exportadas: analisis_correlaciones.csv")
            
            # Exportar clusters
            if self.clusters is not None:
                df_con_clusters = df_cuant.copy()
                df_con_clusters['Cluster'] = self.clusters
                df_con_clusters.to_csv('dataset_con_clusters.csv', index=False)
                archivos_exportados.append('dataset_con_clusters.csv')
                self.log("💾 Dataset con clusters: dataset_con_clusters.csv")
            
            if archivos_exportados:
                mensaje = "✅ Resultados exportados correctamente:\n\n" + "\n".join([f"• {archivo}" for archivo in archivos_exportados])
                messagebox.showinfo("Éxito", mensaje)
            else:
                messagebox.showwarning("Advertencia", "No hay resultados para exportar. Ejecuta un análisis primero.")
            
        except Exception as e:
            self.log(f"\n❌ Error al exportar: {str(e)}")
            messagebox.showerror("Error", f"No se pudieron exportar los resultados:\n{str(e)}")