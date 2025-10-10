import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class PreprocessingFrame(ctk.CTkFrame):
    def __init__(self, master, df=None):
        super().__init__(master)
        self.master = master
        self.df = df.copy() if df is not None else None
        self.df_cuantitativo = None
        self.df_descriptivo = None
        self.procesado = False
        self.canvas_actual = None
        self.fig_actual = None

        # Container principal
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
            text="⚙️ Preprocesamiento de Datos",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        )
        title.pack(side="left")

        # Frame de botones
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.btn_boxplot = ctk.CTkButton(
            btn_frame,
            text="📊 Ver Boxplots Originales",
            command=self.mostrar_boxplots_originales,
            width=200,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_boxplot.pack(side="left", padx=5)

        self.btn_preprocesar = ctk.CTkButton(
            btn_frame,
            text="🔧 Preprocesar Dataset",
            command=self.preprocesar,
            width=200,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#00AA00",
            hover_color="#008800"
        )
        self.btn_preprocesar.pack(side="left", padx=5)

        self.btn_boxplot_proc = ctk.CTkButton(
            btn_frame,
            text="📈 Ver Boxplots Procesados",
            command=self.mostrar_boxplots_procesados,
            width=200,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E",
            state="disabled"
        )
        self.btn_boxplot_proc.pack(side="left", padx=5)

        self.btn_guardar = ctk.CTkButton(
            btn_frame,
            text="💾 Guardar CSVs",
            command=self.guardar_csvs,
            width=180,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#666",
            hover_color="#888",
            state="disabled"
        )
        self.btn_guardar.pack(side="left", padx=5)

        self.btn_ver_tabla = ctk.CTkButton(
            btn_frame,
            text="📋 Ver Tablas Completas",
            command=self.mostrar_tabla_procesada,
            width=200,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E",
            state="disabled"
        )
        self.btn_ver_tabla.pack(side="left", padx=5)

        # Frame principal con dos columnas
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Columna izquierda: Log de información
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        log_label = ctk.CTkLabel(
            left_frame,
            text="📝 Registro de Procesamiento",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        log_label.pack(pady=10)

        self.text_info = tk.Text(
            left_frame,
            height=25,
            width=60,
            bg="#2b2b2b",
            fg="white",
            font=("Courier", 10),
            wrap="word"
        )
        self.text_info.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        scrollbar = tk.Scrollbar(self.text_info, command=self.text_info.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_info.config(yscrollcommand=scrollbar.set)

        # Columna derecha: Gráficos
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        graph_label = ctk.CTkLabel(
            right_frame,
            text="📊 Visualizaciones",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        )
        graph_label.pack(pady=10)

        self.frame_grafico = ctk.CTkFrame(right_frame)
        self.frame_grafico.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Mostrar info inicial
        if self.df is not None:
            self.mostrar_info_inicial()

    def limpiar_grafico(self):
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

    def log(self, mensaje):
        """Añade un mensaje al log"""
        try:
            self.text_info.insert(tk.END, mensaje + "\n")
            self.text_info.see(tk.END)
        except:
            pass

    def mostrar_info_inicial(self):
        """Muestra información básica del dataset"""
        self.log("=" * 50)
        self.log("INFORMACIÓN DEL DATASET")
        self.log("=" * 50)
        self.log(f"Dimensiones: {self.df.shape[0]} filas × {self.df.shape[1]} columnas")
        self.log(f"\nColumnas: {', '.join(self.df.columns.tolist())}")
        self.log(f"\nValores nulos por columna:")
        nulls_found = False
        for col in self.df.columns:
            nulls = self.df[col].isnull().sum()
            if nulls > 0:
                self.log(f"  {col}: {nulls}")
                nulls_found = True
        if not nulls_found:
            self.log("  No hay valores nulos")
        self.log("\n✅ Dataset cargado y listo para procesar")

    def mostrar_boxplots_originales(self):
        """Muestra boxplots de las variables originales"""
        if self.df is None:
            return
        
        self.limpiar_grafico()

        cols = ['chol', 'trestbps', 'oldpeak']
        cols_disponibles = [c for c in cols if c in self.df.columns]
        
        if not cols_disponibles:
            self.log("⚠️ No se encontraron las columnas esperadas")
            return

        self.fig_actual = Figure(figsize=(12, 4), facecolor='#2b2b2b')
        axs = self.fig_actual.subplots(1, len(cols_disponibles))
        
        if len(cols_disponibles) == 1:
            axs = [axs]
        
        for i, col in enumerate(cols_disponibles):
            sns.boxplot(x=self.df[col], ax=axs[i], color='#0078D7')
            axs[i].set_title(col, color='white', fontsize=12, fontweight='bold')
            axs[i].set_facecolor('#1e1e1e')
            axs[i].tick_params(colors='white')
            axs[i].spines['bottom'].set_color('white')
            axs[i].spines['left'].set_color('white')
            axs[i].spines['top'].set_visible(False)
            axs[i].spines['right'].set_visible(False)
        
        self.fig_actual.tight_layout()
        
        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=self.frame_grafico)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)
        
        self.log("\n📊 Mostrando boxplots de datos originales")

    def mostrar_boxplots_procesados(self):
        """Muestra boxplots de las variables procesadas"""
        if self.df_cuantitativo is None:
            return
        
        self.limpiar_grafico()

        cols = ['Colesterol', 'Presion_Arterial_Reposo', 'DepresionST_Ejercicio']
        cols_disponibles = [c for c in cols if c in self.df_cuantitativo.columns]
        
        if not cols_disponibles:
            self.log("⚠️ No se encontraron las columnas en datos procesados")
            return

        self.fig_actual = Figure(figsize=(12, 4), facecolor='#2b2b2b')
        axs = self.fig_actual.subplots(1, len(cols_disponibles))
        
        if len(cols_disponibles) == 1:
            axs = [axs]
        
        for i, col in enumerate(cols_disponibles):
            sns.boxplot(x=self.df_cuantitativo[col], ax=axs[i], color='#00AA00')
            axs[i].set_title(f"{col} (procesado)", color='white', fontsize=12, fontweight='bold')
            axs[i].set_facecolor('#1e1e1e')
            axs[i].tick_params(colors='white')
            axs[i].spines['bottom'].set_color('white')
            axs[i].spines['left'].set_color('white')
            axs[i].spines['top'].set_visible(False)
            axs[i].spines['right'].set_visible(False)
        
        self.fig_actual.tight_layout()
        
        self.canvas_actual = FigureCanvasTkAgg(self.fig_actual, master=self.frame_grafico)
        self.canvas_actual.draw()
        self.canvas_actual.get_tk_widget().pack(fill="both", expand=True)
        
        self.log("\n📈 Mostrando boxplots de datos procesados")

    def preprocesar(self):
        """Realiza el preprocesamiento completo del dataset"""
        if self.df is None:
            return
        
        self.log("\n" + "=" * 50)
        self.log("INICIANDO PREPROCESAMIENTO")
        self.log("=" * 50)
        
        try:
            # 1. Renombrar columnas al español
            self.log("\n1️⃣ Renombrando columnas al español...")
            nuevo_nombres = {
                'age': 'Edad',
                'sex': 'Sexo',
                'cp': 'Tipo_Dolor_Pecho',
                'trestbps': 'Presion_Arterial_Reposo',
                'chol': 'Colesterol',
                'fbs': 'Glucemia_Ayunas_Mayor_120',
                'restecg': 'Electrocardiograma_Reposo',
                'thalach': 'Frecuencia_Cardiaca_Maxima',
                'exang': 'Dolor_Inducido_Ejercicio',
                'oldpeak': 'DepresionST_Ejercicio',
                'slope': 'PendienteST_Ejercicio',
                'ca': 'Vasos_Principales_Color_Fluor',
                'thal': 'Talasemia',
                'target': 'Enfermedad_Cardiaca'
            }
            df = self.df.rename(columns=nuevo_nombres)
            self.log(f"   ✓ {len(nuevo_nombres)} columnas renombradas")
            
            # 2. Winsorización con método IQR
            self.log("\n2️⃣ Aplicando winsorización (método IQR) a outliers...")
            cols_outliers = ['Colesterol', 'Presion_Arterial_Reposo', 'DepresionST_Ejercicio']
            
            def winsorizar_iqr(df_temp, columna, factor=1.5):
                Q1 = df_temp[columna].quantile(0.25)
                Q3 = df_temp[columna].quantile(0.75)
                IQR = Q3 - Q1
                limite_inferior = Q1 - (factor * IQR)
                limite_superior = Q3 + (factor * IQR)
                valores_antes = df_temp[columna].copy()
                df_temp[columna] = np.where(df_temp[columna] < limite_inferior, limite_inferior, df_temp[columna])
                df_temp[columna] = np.where(df_temp[columna] > limite_superior, limite_superior, df_temp[columna])
                outliers_modificados = (valores_antes != df_temp[columna]).sum()
                return df_temp, outliers_modificados
            
            df_winsorized = df.copy()
            for col in cols_outliers:
                if col in df_winsorized.columns:
                    media_antes = df_winsorized[col].mean()
                    df_winsorized, n_outliers = winsorizar_iqr(df_winsorized, col)
                    media_despues = df_winsorized[col].mean()
                    self.log(f"   ✓ {col}:")
                    self.log(f"     - Media antes: {media_antes:.2f} → después: {media_despues:.2f}")
                    self.log(f"     - Outliers winzorizados: {n_outliers}")
            
            df = df_winsorized
            
            # 3. DATASET CUANTITATIVO (para modelos ML)
            self.log("\n3️⃣ Creando Dataset Cuantitativo (numérico)...")
            
            # Convertir columnas categóricas a tipo category
            cols_nominal = [
                'Tipo_Dolor_Pecho', 
                'Electrocardiograma_Reposo', 
                'PendienteST_Ejercicio', 
                'Talasemia'
            ]
            
            df_cuant = df.copy()
            for col in cols_nominal:
                if col in df_cuant.columns:
                    df_cuant[col] = df_cuant[col].astype('category')
            
            # Crear variables dummy
            self.df_cuantitativo = pd.get_dummies(df_cuant, columns=cols_nominal, drop_first=True)
            self.log(f"   ✓ Variables dummy creadas para {len(cols_nominal)} columnas")
            self.log(f"   ✓ Dataset cuantitativo: {self.df_cuantitativo.shape[0]} filas × {self.df_cuantitativo.shape[1]} columnas")
            
            # Mostrar columnas generadas
            nuevas_cols = set(self.df_cuantitativo.columns) - set(df.columns)
            self.log(f"   ✓ Nuevas columnas dummy: {len(nuevas_cols)}")
            
            # 4. DATASET DESCRIPTIVO (texto legible)
            self.log("\n4️⃣ Creando Dataset Descriptivo (cualitativo)...")
            
            # Mapeos para convertir a texto descriptivo
            mapa_dolor = {
                0: 'Asintomático', 
                1: 'Angina Típica', 
                2: 'Angina Atípica', 
                3: 'Dolor No Anginal'
            }
            
            mapa_ecg = {
                0: 'Normal', 
                1: 'Anormalidad Onda ST-T', 
                2: 'Hipertrofia Ventricular'
            }
            
            mapa_pendiente = {
                0: 'Ascendente', 
                1: 'Plana', 
                2: 'Descendente'
            }
            
            mapa_talasemia = {
                1: 'Normal', 
                2: 'Defecto Fijo', 
                3: 'Defecto Reversible'
            }
            
            df_descriptivo = df.copy()
            
            # Aplicar mapeos
            if 'Tipo_Dolor_Pecho' in df_descriptivo.columns:
                df_descriptivo['Tipo_Dolor_Pecho'] = df_descriptivo['Tipo_Dolor_Pecho'].map(mapa_dolor)
                self.log("   ✓ Tipo_Dolor_Pecho convertido a texto")
            
            if 'Electrocardiograma_Reposo' in df_descriptivo.columns:
                df_descriptivo['Electrocardiograma_Reposo'] = df_descriptivo['Electrocardiograma_Reposo'].map(mapa_ecg)
                self.log("   ✓ Electrocardiograma_Reposo convertido a texto")
            
            if 'PendienteST_Ejercicio' in df_descriptivo.columns:
                df_descriptivo['PendienteST_Ejercicio'] = df_descriptivo['PendienteST_Ejercicio'].map(mapa_pendiente)
                self.log("   ✓ PendienteST_Ejercicio convertido a texto")
            
            if 'Talasemia' in df_descriptivo.columns:
                df_descriptivo['Talasemia'] = df_descriptivo['Talasemia'].map(mapa_talasemia)
                self.log("   ✓ Talasemia convertido a texto")
            
            if 'Sexo' in df_descriptivo.columns:
                df_descriptivo['Sexo'] = df_descriptivo['Sexo'].map({0: 'M', 1: 'H'})
                self.log("   ✓ Sexo convertido a M/H")
            
            if 'Dolor_Inducido_Ejercicio' in df_descriptivo.columns:
                df_descriptivo['Dolor_Inducido_Ejercicio'] = df_descriptivo['Dolor_Inducido_Ejercicio'].map({0: 'No', 1: 'Sí'})
                self.log("   ✓ Dolor_Inducido_Ejercicio convertido a No/Sí")
            
            if 'Enfermedad_Cardiaca' in df_descriptivo.columns:
                df_descriptivo['Enfermedad_Cardiaca'] = df_descriptivo['Enfermedad_Cardiaca'].map({0: 'No', 1: 'Sí'})
                self.log("   ✓ Enfermedad_Cardiaca convertido a No/Sí")
            
            if 'Glucemia_Ayunas_Mayor_120' in df_descriptivo.columns:
                df_descriptivo['Glucemia_Ayunas_Mayor_120'] = df_descriptivo['Glucemia_Ayunas_Mayor_120'].map({0: 'No', 1: 'Sí'})
                self.log("   ✓ Glucemia_Ayunas_Mayor_120 convertido a No/Sí")
            
            self.df_descriptivo = df_descriptivo
            self.log(f"   ✓ Dataset descriptivo: {self.df_descriptivo.shape[0]} filas × {self.df_descriptivo.shape[1]} columnas")
            
            # Activar botones
            self.btn_boxplot_proc.configure(state="normal", fg_color="#0078D7")
            self.btn_guardar.configure(state="normal", fg_color="#00AA00")
            self.btn_ver_tabla.configure(state="normal", fg_color="#0078D7")
            self.procesado = True
            
            self.log("\n" + "=" * 50)
            self.log("✅ PREPROCESAMIENTO COMPLETADO EXITOSAMENTE")
            self.log("=" * 50)
            self.log("\n📋 Resumen:")
            self.log(f"   • Dataset Original: {self.df.shape[1]} columnas")
            self.log(f"   • Dataset Cuantitativo: {self.df_cuantitativo.shape[1]} columnas (con dummies)")
            self.log(f"   • Dataset Descriptivo: {self.df_descriptivo.shape[1]} columnas (texto legible)")
            
            # Notificar al parent
            if hasattr(self.master, 'datos_procesados'):
                self.master.datos_procesados(self.df_cuantitativo, self.df_descriptivo)
            
            messagebox.showinfo("Éxito", "✅ Preprocesamiento completado\n\n" +
                              f"• Cuantitativo: {self.df_cuantitativo.shape[1]} columnas\n" +
                              f"• Descriptivo: {self.df_descriptivo.shape[1]} columnas")
            
        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            messagebox.showerror("Error", f"Error en el preprocesamiento:\n{str(e)}")

    def guardar_csvs(self):
        """Guarda los datasets procesados en archivos CSV"""
        if self.df_cuantitativo is None or self.df_descriptivo is None:
            messagebox.showwarning("Advertencia", "Primero debes preprocesar los datos")
            return
        
        try:
            self.df_cuantitativo.to_csv('dataset_cuantitativo.csv', index=False, encoding='utf-8')
            self.df_descriptivo.to_csv('dataset_descriptivo.csv', index=False, encoding='utf-8')
            
            self.log("\n💾 Archivos guardados:")
            self.log("   ✓ dataset_cuantitativo.csv")
            self.log("   ✓ dataset_descriptivo.csv")
            
            messagebox.showinfo("Éxito", "📁 Archivos CSV guardados correctamente:\n\n" +
                              "✓ dataset_cuantitativo.csv\n" +
                              "✓ dataset_descriptivo.csv")
            
        except Exception as e:
            self.log(f"\n❌ Error al guardar: {str(e)}")
            messagebox.showerror("Error", f"No se pudieron guardar los archivos:\n{str(e)}")

    def mostrar_tabla_procesada(self):
        """Muestra las 3 tablas completas en una ventana nueva"""
        if self.df_cuantitativo is None:
            messagebox.showwarning("Advertencia", "Primero debes preprocesar los datos")
            return

        # Crear ventana emergente
        ventana_tabla = ctk.CTkToplevel(self)
        ventana_tabla.title("📊 Tablas Completas - Heart Risk System")
        ventana_tabla.geometry("1600x900")
        
        # Protocolo de cierre seguro
        def cerrar_ventana():
            try:
                ventana_tabla.destroy()
            except:
                pass
        
        ventana_tabla.protocol("WM_DELETE_WINDOW", cerrar_ventana)
        
        # Frame principal
        main_frame = ctk.CTkFrame(ventana_tabla)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#1e1e1e")
        header_frame.pack(fill="x", pady=(0, 10))

        title_label = ctk.CTkLabel(
            header_frame,
            text="📋 Visualización Completa de las 3 Tablas",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        )
        title_label.pack(pady=15)

        # Info
        info_text = f"Dataset Original: {self.df.shape[0]}×{self.df.shape[1]}  |  Cuantitativo: {self.df_cuantitativo.shape[0]}×{self.df_cuantitativo.shape[1]}  |  Descriptivo: {self.df_descriptivo.shape[0]}×{self.df_descriptivo.shape[1]}"
        
        info_label = ctk.CTkLabel(
            header_frame,
            text=info_text,
            font=("Segoe UI", 12),
            text_color="#AAAAAA"
        )
        info_label.pack(pady=(0, 10))

        # Pestañas
        tabview = ctk.CTkTabview(main_frame, height=700)
        tabview.pack(fill="both", expand=True)

        # Tab 1: Original
        tab1 = tabview.add("📄 Tabla 1: Original (Inglés)")
        self._crear_tabla_completa(tab1, self.df, "Original", "#0078D7")

        # Tab 2: Cuantitativo
        tab2 = tabview.add("📊 Tabla 2: Cuantitativo (Numérico)")
        self._crear_tabla_completa(tab2, self.df_cuantitativo, "Cuantitativo", "#00AA00")

        # Tab 3: Descriptivo
        tab3 = tabview.add("📋 Tabla 3: Descriptivo (Cualitativo)")
        self._crear_tabla_completa(tab3, self.df_descriptivo, "Descriptivo", "#FF8C00")

        # Botones
        bottom_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_frame.pack(pady=10)

        btn_exportar = ctk.CTkButton(
            bottom_frame,
            text="💾 Exportar Datasets",
            command=self.guardar_csvs,
            width=250,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color="#00AA00",
            hover_color="#008800"
        )
        btn_exportar.pack(side="left", padx=10)

        btn_cerrar = ctk.CTkButton(
            bottom_frame,
            text="✖ Cerrar",
            command=cerrar_ventana,
            width=180,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#666",
            hover_color="#888"
        )
        btn_cerrar.pack(side="left", padx=10)

    def _crear_tabla_completa(self, parent, dataframe, tipo, color):
        """Crea una tabla completa con todas las filas"""
        container = ctk.CTkFrame(parent)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header = ctk.CTkFrame(container, fg_color="#1e1e1e", corner_radius=10)
        header.pack(fill="x", pady=(0, 10))

        titulo = ctk.CTkLabel(
            header,
            text=f"Tabla {tipo} Completa",
            font=("Segoe UI", 20, "bold"),
            text_color=color
        )
        titulo.pack(pady=(10, 5))

        info_text = f"📊 {dataframe.shape[0]} filas × {dataframe.shape[1]} columnas  |  💾 Mostrando TODAS las filas"
        ctk.CTkLabel(
            header,
            text=info_text,
            font=("Segoe UI", 12),
            text_color="#CCCCCC"
        ).pack(pady=(0, 10))

        # Frame para tabla
        tabla_frame = ctk.CTkFrame(container, fg_color="#1e1e1e", corner_radius=10)
        tabla_frame.pack(fill="both", expand=True)

        # Estilo
        style = ttk.Style()
        style_name = f"Tabla{tipo}"
        
        style.configure(f"{style_name}.Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b",
                       font=("Segoe UI", 9),
                       rowheight=28)
        
        style.map(f'{style_name}.Treeview', 
                 background=[('selected', color)])
        
        style.configure(f"{style_name}.Treeview.Heading",
                       background="#1e1e1e",
                       foreground=color,
                       font=("Segoe UI", 11, "bold"),
                       relief="flat")

        # Treeview
        tree_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(
            tree_frame,
            columns=list(dataframe.columns),
            show='headings',
            style=f"{style_name}.Treeview",
            height=25
        )

        # Configurar columnas
        for col in dataframe.columns:
            tree.heading(col, text=col)
            max_width = max(len(str(col)) * 10, 120)
            tree.column(col, anchor="center", width=max_width, minwidth=80)

        # Insertar datos
        for idx, row in dataframe.iterrows():
            values = []
            for val in row:
                if pd.isna(val):
                    values.append("—")
                elif isinstance(val, float):
                    values.append(f"{val:.4f}")
                elif isinstance(val, (int, np.integer)):
                    values.append(str(int(val)))
                else:
                    values.append(str(val))
            
            tags = ('evenrow',) if idx % 2 == 0 else ('oddrow',)
            tree.insert("", "end", values=values, tags=tags)

        tree.tag_configure('evenrow', background='#2b2b2b')
        tree.tag_configure('oddrow', background='#333333')

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        # Footer con lista de columnas
        footer = ctk.CTkFrame(container, fg_color="#1e1e1e", corner_radius=10)
        footer.pack(fill="x", pady=(10, 0))

        columnas_text = f"📋 Columnas ({len(dataframe.columns)}): " + ", ".join(dataframe.columns.tolist())
        
        ctk.CTkLabel(
            footer,
            text=columnas_text,
            font=("Courier", 9),
            text_color="#888888",
            wraplength=1400,
            justify="left"
        ).pack(pady=10, padx=15, anchor="w")