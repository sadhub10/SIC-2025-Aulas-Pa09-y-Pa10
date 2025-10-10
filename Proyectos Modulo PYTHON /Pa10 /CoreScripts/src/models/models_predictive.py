import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib
import os
from datetime import datetime

# Intentar importar reportlab para PDF
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_DISPONIBLE = True
except ImportError:
    REPORTLAB_DISPONIBLE = False
    print("⚠️ Advertencia: reportlab no disponible. Los PDFs no estarán disponibles.")

class ModelosFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        # Variables del modelo
        self.modelo = None
        self.scaler = None
        self.feature_cols = None
        self.modelo_entrenado = False
        
        # Inicializar historial
        self.historial_file = 'historial_pacientes.csv'
        self.inicializar_historial()
        
        self.setup_ui()
    
    def inicializar_historial(self):
        """Crea el archivo de historial si no existe"""
        if not os.path.exists(self.historial_file):
            columnas = [
                'Fecha_Registro', 'Hora_Registro', 'Nombre', 'Cedula', 'Edad', 'Sexo',
                'Presion_Arterial', 'Colesterol', 'Glucemia_Mayor_120', 
                'FC_Maxima', 'Dolor_Ejercicio', 'Depresion_ST', 'Vasos_Estenosis',
                'Probabilidad_Enfermedad_%', 'Nivel_Riesgo', 'Riesgo_Framingham_%',
                'Puntos_Factores_Riesgo'
            ]
            df_vacio = pd.DataFrame(columns=columnas)
            df_vacio.to_csv(self.historial_file, index=False, encoding='utf-8')
            print(f"✅ Archivo de historial creado: {self.historial_file}")
    
    def guardar_en_historial(self, datos, factores):
        """Guarda los datos del paciente en el historial CSV"""
        try:
            # Preparar datos para el historial
            prob = datos['prob_enfermedad']
            if prob < 30:
                nivel_riesgo = "BAJO"
            elif prob < 60:
                nivel_riesgo = "MODERADO"
            else:
                nivel_riesgo = "ALTO"
            
            nueva_fila = {
                'Fecha_Registro': datetime.now().strftime('%d/%m/%Y'),
                'Hora_Registro': datetime.now().strftime('%H:%M:%S'),
                'Nombre': datos['nombre'],
                'Cedula': datos['cedula'],
                'Edad': datos['edad'],
                'Sexo': 'Masculino' if datos['sexo'] == 'H' else 'Femenino',
                'Presion_Arterial': datos['presion'],
                'Colesterol': datos['colesterol'],
                'Glucemia_Mayor_120': 'Sí' if datos['glucemia_num'] == 1 else 'No',
                'FC_Maxima': datos['fc_maxima'],
                'Dolor_Ejercicio': 'Sí' if datos['dolor_ejercicio_num'] == 1 else 'No',
                'Depresion_ST': datos['depresion_st'],
                'Vasos_Estenosis': datos['vasos'],
                'Probabilidad_Enfermedad_%': round(prob, 2),
                'Nivel_Riesgo': nivel_riesgo,
                'Riesgo_Framingham_%': datos['riesgo_fram'],
                'Puntos_Factores_Riesgo': factores['puntos']
            }
            
            # Leer historial existente
            if os.path.exists(self.historial_file):
                df_historial = pd.read_csv(self.historial_file, encoding='utf-8')
            else:
                df_historial = pd.DataFrame()
            
            # Agregar nueva fila
            df_historial = pd.concat([df_historial, pd.DataFrame([nueva_fila])], ignore_index=True)
            
            # Guardar
            df_historial.to_csv(self.historial_file, index=False, encoding='utf-8')
            print(f"✅ Paciente guardado en historial: {datos['nombre']}")
            
        except Exception as e:
            print(f"⚠️ Error al guardar en historial: {str(e)}")
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(10, 5))

        title = ctk.CTkLabel(
            header,
            text="🤖 Modelos Predictivos - Random Forest",
            font=("Segoe UI", 20, "bold"),
            text_color="#00BFFF"
        )
        title.pack(side="left")

        # Botones de navegación
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=5)

        self.btn_entrenar = ctk.CTkButton(
            btn_frame,
            text="🎓 Entrenar Modelo",
            command=self.entrenar_modelo,
            width=180,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#00AA00",
            hover_color="#008800"
        )
        self.btn_entrenar.pack(side="left", padx=5)

        self.btn_predecir = ctk.CTkButton(
            btn_frame,
            text="🩺 Predecir Paciente Nuevo",
            command=self.mostrar_formulario_paciente,
            width=200,
            height=35,
            font=("Segoe UI", 12, "bold"),
            fg_color="#0078D7",
            hover_color="#005A9E",
            state="disabled"
        )
        self.btn_predecir.pack(side="left", padx=5)

        self.btn_historial = ctk.CTkButton(
            btn_frame,
            text="📊 Ver Historial",
            command=self.mostrar_historial,
            width=150,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#FF6B35",
            hover_color="#E85A2F"
        )
        self.btn_historial.pack(side="left", padx=5)

        self.btn_cargar = ctk.CTkButton(
            btn_frame,
            text="📂 Cargar Modelo",
            command=self.cargar_modelo_guardado,
            width=150,
            height=35,
            font=("Segoe UI", 12),
            fg_color="#9333EA",
            hover_color="#7C3AED"
        )
        self.btn_cargar.pack(side="left", padx=5)

        # Frame principal scrollable
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Mensaje inicial
        self.mostrar_pantalla_inicial()
    
    def mostrar_pantalla_inicial(self):
        """Muestra la pantalla de bienvenida"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame de bienvenida
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=15)
        welcome_frame.pack(fill="both", expand=True, pady=50, padx=50)

        ctk.CTkLabel(
            welcome_frame,
            text="🤖 Sistema de Predicción de Riesgo Cardiovascular",
            font=("Segoe UI", 24, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(30, 10))

        info_text = """
        Este módulo utiliza Random Forest para predecir el riesgo 
        de enfermedad cardiovascular en pacientes.
        
        📋 Pasos para usar el sistema:
        
        1️⃣ Entrena el modelo con el dataset descriptivo
        2️⃣ Revisa las métricas y gráficas de rendimiento
        3️⃣ Ingresa datos de pacientes nuevos para predicción
        4️⃣ Consulta el historial de pacientes evaluados
        
        💡 El modelo y los datos se guardan automáticamente
        """
        
        ctk.CTkLabel(
            welcome_frame,
            text=info_text,
            font=("Segoe UI", 13),
            text_color="#CCCCCC",
            justify="left"
        ).pack(pady=20, padx=40)

        ctk.CTkLabel(
            welcome_frame,
            text="👆 Comienza haciendo clic en 'Entrenar Modelo'",
            font=("Segoe UI", 14, "bold"),
            text_color="#00AA00"
        ).pack(pady=(10, 30))
    
    def mostrar_historial(self):
        """Muestra el historial de pacientes evaluados"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Frame del historial
        hist_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=15)
        hist_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Título
        header = ctk.CTkFrame(hist_frame, fg_color="#2b2b2b", corner_radius=10)
        header.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="📊 HISTORIAL DE PACIENTES EVALUADOS",
            font=("Segoe UI", 20, "bold"),
            text_color="#00BFFF"
        ).pack(pady=15)

        # Verificar si existe el archivo
        if not os.path.exists(self.historial_file):
            ctk.CTkLabel(
                hist_frame,
                text="📭 No hay pacientes registrados aún",
                font=("Segoe UI", 16),
                text_color="#AAAAAA"
            ).pack(pady=50)
            return
        
        # Leer historial
        try:
            df_historial = pd.read_csv(self.historial_file, encoding='utf-8')
            
            if df_historial.empty:
                ctk.CTkLabel(
                    hist_frame,
                    text="📭 No hay pacientes registrados aún",
                    font=("Segoe UI", 16),
                    text_color="#AAAAAA"
                ).pack(pady=50)
                return
            
            # Información general
            info_frame = ctk.CTkFrame(hist_frame, fg_color="#2b2b2b", corner_radius=10)
            info_frame.pack(fill="x", padx=15, pady=10)

            info_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
            info_grid.pack(pady=15, padx=20)

            stats = [
                ("Total Pacientes", str(len(df_historial)), "#00BFFF"),
                ("Riesgo Alto", str(len(df_historial[df_historial['Nivel_Riesgo'] == 'ALTO'])), "#FF4444"),
                ("Riesgo Moderado", str(len(df_historial[df_historial['Nivel_Riesgo'] == 'MODERADO'])), "#FFAA00"),
                ("Riesgo Bajo", str(len(df_historial[df_historial['Nivel_Riesgo'] == 'BAJO'])), "#00AA00")
            ]

            for i, (label, value, color) in enumerate(stats):
                stat_box = ctk.CTkFrame(info_grid, fg_color="#1e1e1e", corner_radius=8)
                stat_box.grid(row=0, column=i, padx=10, pady=5, sticky="ew")
                
                ctk.CTkLabel(
                    stat_box,
                    text=label,
                    font=("Segoe UI", 11),
                    text_color="#CCCCCC"
                ).pack(pady=(10, 2))
                
                ctk.CTkLabel(
                    stat_box,
                    text=value,
                    font=("Segoe UI", 24, "bold"),
                    text_color=color
                ).pack(pady=(2, 10))

            # Botones de acción
            btn_frame = ctk.CTkFrame(hist_frame, fg_color="transparent")
            btn_frame.pack(fill="x", padx=15, pady=10)

            ctk.CTkButton(
                btn_frame,
                text="💾 Exportar Historial",
                command=self.exportar_historial,
                width=180,
                height=35,
                font=("Segoe UI", 12, "bold"),
                fg_color="#00AA00",
                hover_color="#008800"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="🔄 Actualizar Vista",
                command=self.mostrar_historial,
                width=160,
                height=35,
                font=("Segoe UI", 12),
                fg_color="#0078D7",
                hover_color="#005A9E"
            ).pack(side="left", padx=5)

            ctk.CTkButton(
                btn_frame,
                text="🗑️ Limpiar Historial",
                command=self.limpiar_historial,
                width=160,
                height=35,
                font=("Segoe UI", 12),
                fg_color="#FF4444",
                hover_color="#CC0000"
            ).pack(side="left", padx=5)

            # Tabla de datos
            table_frame = ctk.CTkFrame(hist_frame, fg_color="#2b2b2b", corner_radius=10)
            table_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))

            ctk.CTkLabel(
                table_frame,
                text="📋 Registros de Pacientes",
                font=("Segoe UI", 14, "bold"),
                text_color="#00BFFF"
            ).pack(pady=10)

            # Crear Treeview con scroll
            tree_scroll_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
            tree_scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            # Configurar estilo
            style = ttk.Style()
            style.theme_use("default")
            style.configure("Treeview",
                          background="#2b2b2b",
                          foreground="white",
                          fieldbackground="#2b2b2b",
                          borderwidth=0,
                          font=("Segoe UI", 9))
            style.configure("Treeview.Heading",
                          background="#1e1e1e",
                          foreground="white",
                          borderwidth=1,
                          font=("Segoe UI", 10, "bold"))
            style.map("Treeview",
                     background=[("selected", "#0078D7")])

            # Scrollbars
            scroll_y = ttk.Scrollbar(tree_scroll_frame, orient="vertical")
            scroll_y.pack(side="right", fill="y")

            scroll_x = ttk.Scrollbar(tree_scroll_frame, orient="horizontal")
            scroll_x.pack(side="bottom", fill="x")

            # Treeview
            columns = list(df_historial.columns)
            tree = ttk.Treeview(tree_scroll_frame,
                               columns=columns,
                               show="headings",
                               yscrollcommand=scroll_y.set,
                               xscrollcommand=scroll_x.set,
                               height=15)

            scroll_y.config(command=tree.yview)
            scroll_x.config(command=tree.xview)

            # Configurar columnas
            for col in columns:
                tree.heading(col, text=col)
                if col in ['Nombre', 'Cedula']:
                    tree.column(col, width=150, anchor="w")
                elif col in ['Fecha_Registro', 'Hora_Registro']:
                    tree.column(col, width=100, anchor="center")
                elif col in ['Probabilidad_Enfermedad_%', 'Riesgo_Framingham_%']:
                    tree.column(col, width=140, anchor="center")
                elif col == 'Nivel_Riesgo':
                    tree.column(col, width=120, anchor="center")
                else:
                    tree.column(col, width=100, anchor="center")

            # Insertar datos (más recientes primero)
            for idx in reversed(df_historial.index):
                row = df_historial.iloc[idx]
                values = [row[col] for col in columns]
                
                # Color según nivel de riesgo
                nivel_riesgo = row['Nivel_Riesgo']
                if nivel_riesgo == 'ALTO':
                    tags = ('alto',)
                elif nivel_riesgo == 'MODERADO':
                    tags = ('moderado',)
                else:
                    tags = ('bajo',)
                
                tree.insert("", "end", values=values, tags=tags)

            # Configurar colores de tags
            tree.tag_configure('alto', background="#4D1F1F")
            tree.tag_configure('moderado', background="#4D3D1F")
            tree.tag_configure('bajo', background="#1F4D1F")

            tree.pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar historial:\n{str(e)}")
    
    def exportar_historial(self):
        """Exporta el historial a un archivo CSV en la ubicación que elija el usuario"""
        try:
            if not os.path.exists(self.historial_file):
                messagebox.showwarning("Sin datos", "No hay historial para exportar")
                return
            
            df_historial = pd.read_csv(self.historial_file, encoding='utf-8')
            
            if df_historial.empty:
                messagebox.showwarning("Sin datos", "El historial está vacío")
                return
            
            # Diálogo para guardar
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archivo_guardar = filedialog.asksaveasfilename(
                title="Exportar Historial",
                defaultextension=".csv",
                initialfile=f"historial_pacientes_{timestamp}.csv",
                filetypes=[
                    ("Archivos CSV", "*.csv"),
                    ("Archivos Excel", "*.xlsx"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if not archivo_guardar:
                return
            
            # Guardar según extensión
            extension = os.path.splitext(archivo_guardar)[1].lower()
            
            if extension == '.xlsx':
                df_historial.to_excel(archivo_guardar, index=False, engine='openpyxl')
            else:
                df_historial.to_csv(archivo_guardar, index=False, encoding='utf-8')
            
            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Historial exportado correctamente:\n\n{archivo_guardar}\n\n" +
                f"Total de registros: {len(df_historial)}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar historial:\n{str(e)}")
    
    def limpiar_historial(self):
        """Limpia el historial de pacientes"""
        respuesta = messagebox.askyesno(
            "Confirmar limpieza",
            "⚠️ ¿Estás seguro de que deseas limpiar todo el historial?\n\n" +
            "Esta acción NO se puede deshacer.\n\n" +
            "Se recomienda exportar el historial antes de limpiarlo."
        )
        
        if respuesta:
            try:
                self.inicializar_historial()
                messagebox.showinfo("Historial limpiado", "✅ El historial ha sido limpiado exitosamente")
                self.mostrar_historial()
            except Exception as e:
                messagebox.showerror("Error", f"Error al limpiar historial:\n{str(e)}")
    
    def entrenar_modelo(self):
        """Entrena el modelo Random Forest"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Verificar archivo
        if not os.path.exists('dataset_descriptivo.csv'):
            messagebox.showerror(
                "Error",
                "No se encontró 'dataset_descriptivo.csv'\n\n" +
                "Por favor, ejecuta el preprocesamiento primero."
            )
            self.mostrar_pantalla_inicial()
            return
        
        # Frame de progreso
        progress_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e")
        progress_frame.pack(fill="x", pady=10, padx=10)

        progress_label = ctk.CTkLabel(
            progress_frame,
            text="⏳ Entrenando modelo... Por favor espera",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        )
        progress_label.pack(pady=20)

        self.update_idletasks()

        try:
            # Cargar datos
            df = self.cargar_datos('dataset_descriptivo.csv')
            
            # Entrenar
            resultados = self.crear_modelo_predictivo(df)
            
            if resultados:
                self.modelo = resultados['modelo']
                self.scaler = resultados['scaler']
                self.feature_cols = resultados['feature_cols']
                self.modelo_entrenado = True
                
                # Habilitar predicción
                self.btn_predecir.configure(state="normal", fg_color="#0078D7")
                
                # Mostrar resultados
                self.mostrar_resultados_entrenamiento(resultados)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al entrenar modelo:\n{str(e)}")
            self.mostrar_pantalla_inicial()
    
    def cargar_datos(self, archivo):
        """Carga y prepara datos"""
        try:
            df = pd.read_csv(archivo)
        except:
            try:
                df = pd.read_csv(archivo, sep=',')
            except:
                df = pd.read_csv(archivo, sep='\t')

        df.columns = df.columns.str.strip().str.replace(' ', '_')

        # Mapeos
        map_sino = {'Sí': 1, 'Si': 1, 'YES': 1, 'Yes': 1, True: 1,
                    'No': 0, 'NO': 0, False: 0, 1: 1, 0: 0}

        if 'Sexo' in df.columns:
            df['Sexo_Num'] = df['Sexo'].map({'H': 1, 'M': 0, 'Male': 1, 'Female': 0})
        if 'Enfermedad_Cardiaca' in df.columns:
            df['Enfermedad_Num'] = df['Enfermedad_Cardiaca'].map(map_sino)
        if 'Dolor_Inducido_Ejercicio' in df.columns:
            df['Dolor_Ejercicio_Num'] = df['Dolor_Inducido_Ejercicio'].map(map_sino)

        for col in df.columns:
            if df[col].dtype == object and df[col].isin(map_sino.keys()).any():
                df[col] = df[col].map(map_sino)

        return df
    
    def crear_modelo_predictivo(self, df):
        """Entrena Random Forest"""
        feature_cols = [
            'Edad', 'Sexo_Num', 'Presion_Arterial_Reposo', 'Colesterol',
            'Glucemia_Ayunas_Mayor_120', 'Frecuencia_Cardiaca_Maxima',
            'Dolor_Ejercicio_Num', 'DepresionST_Ejercicio',
            'Vasos_Principales_Color_Fluor'
        ]

        feature_cols = [col for col in feature_cols if col in df.columns]

        X = df[feature_cols].apply(pd.to_numeric, errors='coerce').fillna(df[feature_cols].median())
        y = df['Enfermedad_Num']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        modelo = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
        modelo.fit(X_train_scaled, y_train)

        y_pred = modelo.predict(X_test_scaled)
        y_pred_proba = modelo.predict_proba(X_test_scaled)[:, 1]

        # Métricas
        report = classification_report(y_test, y_pred, target_names=['Sin Enfermedad', 'Con Enfermedad'], output_dict=True)
        auc = roc_auc_score(y_test, y_pred_proba)
        cm = confusion_matrix(y_test, y_pred)
        
        # Importancias
        importancias = pd.DataFrame({
            'Factor': feature_cols,
            'Importancia': modelo.feature_importances_
        }).sort_values('Importancia', ascending=False)

        # Guardar modelo
        os.makedirs('modelos', exist_ok=True)
        joblib.dump(modelo, 'modelos/modelo_rf.joblib')
        joblib.dump(scaler, 'modelos/scaler.joblib')
        joblib.dump(feature_cols, 'modelos/feature_cols.joblib')

        return {
            'modelo': modelo,
            'scaler': scaler,
            'feature_cols': feature_cols,
            'report': report,
            'auc': auc,
            'cm': cm,
            'importancias': importancias,
            'y_test': y_test,
            'y_pred_proba': y_pred_proba
        }
    
    def mostrar_resultados_entrenamiento(self, resultados):
        """Muestra resultados del entrenamiento"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Título
        title_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=10)
        title_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(
            title_frame,
            text="✅ Modelo Entrenado Exitosamente",
            font=("Segoe UI", 18, "bold"),
            text_color="#00AA00"
        ).pack(pady=15)

        # Métricas principales
        metrics_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=10)
        metrics_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(
            metrics_frame,
            text="📊 Métricas de Rendimiento",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(10, 5))

        # Grid de métricas
        metrics_grid = ctk.CTkFrame(metrics_frame, fg_color="transparent")
        metrics_grid.pack(pady=10, padx=20)

        report = resultados['report']
        
        metrics = [
            ("Precisión Global", f"{report['accuracy']:.3f}", "#00AA00"),
            ("AUC-ROC", f"{resultados['auc']:.3f}", "#0078D7"),
            ("Precisión (Sin Enf.)", f"{report['Sin Enfermedad']['precision']:.3f}", "#FFAA00"),
            ("Recall (Con Enf.)", f"{report['Con Enfermedad']['recall']:.3f}", "#FF6B6B")
        ]

        for i, (label, value, color) in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            metric_box = ctk.CTkFrame(metrics_grid, fg_color="#2b2b2b", corner_radius=8)
            metric_box.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            ctk.CTkLabel(
                metric_box,
                text=label,
                font=("Segoe UI", 11),
                text_color="#CCCCCC"
            ).pack(pady=(10, 2))
            
            ctk.CTkLabel(
                metric_box,
                text=value,
                font=("Segoe UI", 20, "bold"),
                text_color=color
            ).pack(pady=(2, 10))

        # Gráficas
        graphs_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=10)
        graphs_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(
            graphs_frame,
            text="📈 Visualizaciones del Modelo",
            font=("Segoe UI", 16, "bold"),
            text_color="#00BFFF"
        ).pack(pady=10)

        # Frame scrollable para las gráficas
        scroll_graphs = ctk.CTkScrollableFrame(graphs_frame, height=600)
        scroll_graphs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 1. Matriz de Confusión
        fig1 = Figure(figsize=(10, 6), facecolor='#2b2b2b', dpi=100)
        ax1 = fig1.add_subplot(1, 1, 1)
        sns.heatmap(resultados['cm'], annot=True, fmt='d', cmap='RdYlGn_r',
                   xticklabels=['Sin Enf.', 'Con Enf.'],
                   yticklabels=['Sin Enf.', 'Con Enf.'],
                   ax=ax1, cbar_kws={'label': 'Cantidad'})
        ax1.set_title('Matriz de Confusión', color='white', fontsize=14, fontweight='bold', pad=15)
        ax1.set_ylabel('Valor Real', color='white', fontsize=12)
        ax1.set_xlabel('Predicción', color='white', fontsize=12)
        ax1.set_facecolor('#1e1e1e')
        ax1.tick_params(colors='white')
        fig1.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=scroll_graphs)
        canvas1.draw()
        canvas1.get_tk_widget().pack(pady=10)

        # 2. Importancia de Features
        fig2 = Figure(figsize=(10, 6), facecolor='#2b2b2b', dpi=100)
        ax2 = fig2.add_subplot(1, 1, 1)
        imp_df = resultados['importancias'].head(8)
        colors_imp = plt.cm.viridis(np.linspace(0, 1, len(imp_df)))
        ax2.barh(imp_df['Factor'], imp_df['Importancia'], color=colors_imp, edgecolor='white', linewidth=1.5)
        ax2.set_xlabel('Importancia', color='white', fontsize=12, fontweight='bold')
        ax2.set_title('Top 8 Factores Más Importantes', color='white', fontsize=14, fontweight='bold', pad=15)
        ax2.set_facecolor('#1e1e1e')
        ax2.tick_params(colors='white', labelsize=10)
        ax2.grid(axis='x', alpha=0.3, color='white')
        for spine in ax2.spines.values():
            spine.set_color('white')
        fig2.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=scroll_graphs)
        canvas2.draw()
        canvas2.get_tk_widget().pack(pady=10)

        # 3. Curva ROC
        fig3 = Figure(figsize=(10, 6), facecolor='#2b2b2b', dpi=100)
        ax3 = fig3.add_subplot(1, 1, 1)
        fpr, tpr, _ = roc_curve(resultados['y_test'], resultados['y_pred_proba'])
        ax3.plot(fpr, tpr, color='#00AA00', linewidth=3, label=f'AUC = {resultados["auc"]:.3f}')
        ax3.plot([0, 1], [0, 1], 'r--', linewidth=2, label='Azar')
        ax3.set_xlabel('Tasa Falsos Positivos', color='white', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Tasa Verdaderos Positivos', color='white', fontsize=12, fontweight='bold')
        ax3.set_title('Curva ROC', color='white', fontsize=14, fontweight='bold', pad=15)
        ax3.legend(loc='lower right', fontsize=11)
        ax3.set_facecolor('#1e1e1e')
        ax3.tick_params(colors='white')
        ax3.grid(True, alpha=0.3, color='white')
        for spine in ax3.spines.values():
            spine.set_color('white')
        fig3.tight_layout()

        canvas3 = FigureCanvasTkAgg(fig3, master=scroll_graphs)
        canvas3.draw()
        canvas3.get_tk_widget().pack(pady=10)

        # Información adicional
        info_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=10)
        info_frame.pack(fill="x", pady=10, padx=10)

        info_text = f"""
        ✅ Modelo guardado en: modelos/modelo_rf.joblib
        📊 Características utilizadas: {len(resultados['feature_cols'])}
        🎯 Precisión en prueba: {report['accuracy']*100:.1f}%
        💾 Listo para predicciones de pacientes nuevos
        """

        ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Courier", 11),
            text_color="#CCCCCC",
            justify="left"
        ).pack(pady=15, padx=20)
    
    def cargar_modelo_guardado(self):
        """Carga modelo previamente guardado"""
        if not os.path.exists('modelos/modelo_rf.joblib'):
            messagebox.showwarning(
                "Modelo no encontrado",
                "No se encontró un modelo entrenado.\n\n" +
                "Por favor, entrena el modelo primero."
            )
            return
        
        try:
            self.modelo = joblib.load('modelos/modelo_rf.joblib')
            self.scaler = joblib.load('modelos/scaler.joblib')
            self.feature_cols = joblib.load('modelos/feature_cols.joblib')
            self.modelo_entrenado = True
            
            self.btn_predecir.configure(state="normal", fg_color="#0078D7")
            
            messagebox.showinfo(
                "Éxito",
                "✅ Modelo cargado correctamente\n\n" +
                "Ahora puedes predecir pacientes nuevos"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar modelo:\n{str(e)}")
    
    def mostrar_formulario_paciente(self):
        """Muestra formulario para ingresar datos del paciente"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Frame del formulario
        form_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=15)
        form_frame.pack(fill="both", expand=True, pady=10, padx=10)

        ctk.CTkLabel(
            form_frame,
            text="🩺 Ingreso de Datos del Paciente",
            font=("Segoe UI", 20, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(20, 10))

        # Crear campos
        self.campos = {}
        
        secciones = [
            ("📋 DATOS DEMOGRÁFICOS", [
                ("nombre", "Nombre completo del paciente", "text"),
                ("cedula", "Cédula (Ej: 10-444-2345)", "text"),
                ("edad", "Edad (años)", "number"),
                ("sexo", "Sexo (H/M)", "text")
            ]),
            ("💉 SIGNOS VITALES", [
                ("presion", "Presión Arterial en Reposo (mmHg)", "number"),
                ("colesterol", "Colesterol Total (mg/dl)", "number")
            ]),
            ("🔬 EXÁMENES DE LABORATORIO", [
                ("glucemia", "Glucemia en ayunas > 120 mg/dl? (S/N)", "text")
            ]),
            ("🏃 PRUEBAS DE ESFUERZO", [
                ("fc_maxima", "Frecuencia Cardíaca Máxima (lpm)", "number"),
                ("dolor_ejercicio", "Dolor/Angina durante ejercicio? (S/N)", "text"),
                ("depresion_st", "Depresión del segmento ST (mm, ej: 1.5)", "decimal")
            ]),
            ("🔍 ESTUDIOS COMPLEMENTARIOS", [
                ("vasos", "Número de vasos con estenosis (0-3)", "number")
            ])
        ]

        scroll_form = ctk.CTkScrollableFrame(form_frame, height=400)
        scroll_form.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        for seccion_nombre, campos in secciones:
            # Título de sección
            seccion_frame = ctk.CTkFrame(scroll_form, fg_color="#2b2b2b", corner_radius=10)
            seccion_frame.pack(fill="x", pady=10, padx=5)

            ctk.CTkLabel(
                seccion_frame,
                text=seccion_nombre,
                font=("Segoe UI", 14, "bold"),
                text_color="#00BFFF"
            ).pack(pady=10, anchor="w", padx=15)

            # Campos de la sección
            for campo_id, label_text, tipo in campos:
                campo_frame = ctk.CTkFrame(seccion_frame, fg_color="transparent")
                campo_frame.pack(fill="x", padx=15, pady=5)

                ctk.CTkLabel(
                    campo_frame,
                    text=label_text,
                    font=("Segoe UI", 12),
                    text_color="#CCCCCC",
                    anchor="w"
                ).pack(side="left", padx=(0, 10))

                entry = ctk.CTkEntry(
                    campo_frame,
                    width=200,
                    height=35,
                    font=("Segoe UI", 12)
                )
                entry.pack(side="right", padx=5)
                
                self.campos[campo_id] = entry

        # Botones
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(
            btn_frame,
            text="🔍 Generar Diagnóstico",
            command=self.predecir_paciente,
            width=200,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color="#00AA00",
            hover_color="#008800"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Limpiar Formulario",
            command=self.mostrar_formulario_paciente,
            width=180,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#666",
            hover_color="#888"
        ).pack(side="left", padx=10)
    
    def predecir_paciente(self):
        """Realiza predicción para el paciente ingresado"""
        try:
            # Validar y obtener datos del paciente
            nombre = self.campos['nombre'].get().strip()
            if not nombre:
                raise ValueError("El nombre del paciente es obligatorio")
            
            cedula = self.campos['cedula'].get().strip()
            if not cedula:
                raise ValueError("La cédula del paciente es obligatoria")
            
            edad = int(self.campos['edad'].get())
            sexo = self.campos['sexo'].get().strip().upper()
            if sexo not in ['H', 'M']:
                raise ValueError("Sexo debe ser H o M")
            sexo_num = 1 if sexo == 'H' else 0

            presion = int(self.campos['presion'].get())
            colesterol = int(self.campos['colesterol'].get())
            
            glucemia = self.campos['glucemia'].get().strip().upper()
            if glucemia not in ['S', 'N']:
                raise ValueError("Glucemia debe ser S o N")
            glucemia_num = 1 if glucemia == 'S' else 0

            fc_maxima = int(self.campos['fc_maxima'].get())
            
            dolor_ejercicio = self.campos['dolor_ejercicio'].get().strip().upper()
            if dolor_ejercicio not in ['S', 'N']:
                raise ValueError("Dolor ejercicio debe ser S o N")
            dolor_ejercicio_num = 1 if dolor_ejercicio == 'S' else 0

            depresion_st = float(self.campos['depresion_st'].get())
            
            vasos = int(self.campos['vasos'].get())
            if vasos not in [0, 1, 2, 3]:
                raise ValueError("Vasos debe estar entre 0 y 3")

            # Crear vector
            X_paciente = [[edad, sexo_num, presion, colesterol, glucemia_num,
                          fc_maxima, dolor_ejercicio_num, depresion_st, vasos]]

            # Normalizar y predecir
            X_scaled = self.scaler.transform(X_paciente)
            prediccion = self.modelo.predict(X_scaled)[0]
            prob_enfermedad = self.modelo.predict_proba(X_scaled)[0][1] * 100

            # Calcular riesgo Framingham
            riesgo_fram = self.calcular_riesgo_framingham(
                edad, sexo, colesterol, 40, presion, False, glucemia_num==1)

            # Preparar datos
            datos_paciente = {
                'nombre': nombre,
                'cedula': cedula,
                'edad': edad,
                'sexo': sexo,
                'presion': presion,
                'colesterol': colesterol,
                'glucemia_num': glucemia_num,
                'fc_maxima': fc_maxima,
                'dolor_ejercicio_num': dolor_ejercicio_num,
                'depresion_st': depresion_st,
                'vasos': vasos,
                'prob_enfermedad': prob_enfermedad,
                'riesgo_fram': riesgo_fram
            }

            # Identificar factores de riesgo
            factores = self.identificar_factores_riesgo(datos_paciente)

            # Guardar en historial
            self.guardar_en_historial(datos_paciente, factores)

            # Mostrar reporte
            self.mostrar_reporte_diagnostico(datos_paciente)

        except ValueError as e:
            messagebox.showerror("Error de validación", f"Por favor verifica los datos:\n{str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la predicción:\n{str(e)}")
    
    def calcular_riesgo_framingham(self, edad, sexo, colesterol, hdl, presion, fumador, diabetes):
        """Calcula riesgo Framingham"""
        puntos = 0

        if sexo == 'H':
            if edad < 35: puntos += -1
            elif edad < 45: puntos += 2
            elif edad < 55: puntos += 5
            elif edad < 65: puntos += 6
            else: puntos += 7
        else:
            if edad < 35: puntos += -9
            elif edad < 45: puntos += -4
            elif edad < 55: puntos += 0
            elif edad < 65: puntos += 3
            else: puntos += 5

        if colesterol < 160: puntos += 0
        elif colesterol < 200: puntos += 1
        elif colesterol < 240: puntos += 2
        elif colesterol < 280: puntos += 3
        else: puntos += 4

        if presion < 120: puntos += 0
        elif presion < 140: puntos += 1
        elif presion < 160: puntos += 2
        else: puntos += 3

        if diabetes: puntos += 3

        if puntos < 0: riesgo = 1
        elif puntos < 5: riesgo = 5
        elif puntos < 10: riesgo = 10
        elif puntos < 15: riesgo = 20
        else: riesgo = 30

        return riesgo
    
    def mostrar_reporte_diagnostico(self, datos):
        """Muestra el reporte completo del diagnóstico"""
        # Limpiar contenido
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Frame del reporte
        report_frame = ctk.CTkFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=15)
        report_frame.pack(fill="both", expand=True, pady=10, padx=10)

        # Título
        header = ctk.CTkFrame(report_frame, fg_color="#2b2b2b", corner_radius=10)
        header.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(
            header,
            text="📋 REPORTE DE DIAGNÓSTICO MÉDICO",
            font=("Segoe UI", 22, "bold"),
            text_color="#00BFFF"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            header,
            text=f"Paciente: {datos['nombre']}  |  Cédula: {datos['cedula']}",
            font=("Segoe UI", 13, "bold"),
            text_color="#00AA00"
        ).pack(pady=5)

        ctk.CTkLabel(
            header,
            text=f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            font=("Segoe UI", 11),
            text_color="#AAAAAA"
        ).pack(pady=(0, 10))

        # Scrollable para el reporte
        scroll_report = ctk.CTkScrollableFrame(report_frame, height=500)
        scroll_report.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Resumen de datos
        datos_frame = ctk.CTkFrame(scroll_report, fg_color="#2b2b2b", corner_radius=10)
        datos_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            datos_frame,
            text="👤 RESUMEN DE DATOS DEL PACIENTE",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        ).pack(pady=10, anchor="w", padx=15)

        resumen_text = f"""
Nombre: {datos['nombre']}
Cédula: {datos['cedula']}
Edad: {datos['edad']} años  |  Sexo: {'Masculino' if datos['sexo']=='H' else 'Femenino'}
Presión Arterial: {datos['presion']} mmHg  |  Colesterol: {datos['colesterol']} mg/dl
Glucemia >120: {'Sí' if datos['glucemia_num']==1 else 'No'}  |  FC Máxima: {datos['fc_maxima']} lpm
Angina por ejercicio: {'Sí' if datos['dolor_ejercicio_num']==1 else 'No'}  |  Depresión ST: {datos['depresion_st']} mm
Vasos con estenosis: {datos['vasos']}
        """
        
        ctk.CTkLabel(
            datos_frame,
            text=resumen_text,
            font=("Courier", 10),
            text_color="#CCCCCC",
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")

        # Evaluación de riesgo con colores
        prob = datos['prob_enfermedad']
        if prob < 30:
            nivel_riesgo = "BAJO"
            color_riesgo = "#00AA00"
            urgencia = "Seguimiento rutinario"
        elif prob < 60:
            nivel_riesgo = "MODERADO"
            color_riesgo = "#FFAA00"
            urgencia = "Evaluación cardiológica recomendada"
        else:
            nivel_riesgo = "ALTO"
            color_riesgo = "#FF4444"
            urgencia = "EVALUACIÓN CARDIOLÓGICA URGENTE"

        riesgo_frame = ctk.CTkFrame(scroll_report, fg_color=color_riesgo, corner_radius=10)
        riesgo_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            riesgo_frame,
            text="⚠️ EVALUACIÓN DE RIESGO",
            font=("Segoe UI", 14, "bold"),
            text_color="white"
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            riesgo_frame,
            text=f"{prob:.1f}%",
            font=("Segoe UI", 36, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            riesgo_frame,
            text=f"Probabilidad de Enfermedad Cardíaca",
            font=("Segoe UI", 12),
            text_color="white"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            riesgo_frame,
            text=f"Nivel de Riesgo: {nivel_riesgo}",
            font=("Segoe UI", 16, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(
            riesgo_frame,
            text=f"Recomendación: {urgencia}",
            font=("Segoe UI", 12),
            text_color="white"
        ).pack(pady=(0, 15))

        # Riesgo Framingham
        fram_frame = ctk.CTkFrame(scroll_report, fg_color="#2b2b2b", corner_radius=10)
        fram_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            fram_frame,
            text=f"📊 Riesgo Cardiovascular a 10 años (Framingham): {datos['riesgo_fram']}%",
            font=("Segoe UI", 12, "bold"),
            text_color="#0078D7"
        ).pack(pady=15)

        # Factores de riesgo
        factores_frame = ctk.CTkFrame(scroll_report, fg_color="#2b2b2b", corner_radius=10)
        factores_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            factores_frame,
            text="🔍 FACTORES DE RIESGO IDENTIFICADOS",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        ).pack(pady=10, anchor="w", padx=15)

        factores = self.identificar_factores_riesgo(datos)
        
        factores_text = "\n".join(factores['lista']) if factores['lista'] else "✅ No se identifican factores de riesgo mayores"
        factores_text += f"\n\n⚠️ Puntuación total de riesgo: {factores['puntos']} puntos"

        ctk.CTkLabel(
            factores_frame,
            text=factores_text,
            font=("Segoe UI", 11),
            text_color="#CCCCCC",
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")

        # Recomendaciones
        recom_frame = ctk.CTkFrame(scroll_report, fg_color="#2b2b2b", corner_radius=10)
        recom_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            recom_frame,
            text="💊 RECOMENDACIONES MÉDICAS",
            font=("Segoe UI", 14, "bold"),
            text_color="#00BFFF"
        ).pack(pady=10, anchor="w", padx=15)

        recomendaciones = self.generar_recomendaciones(datos, prob)

        ctk.CTkLabel(
            recom_frame,
            text=recomendaciones,
            font=("Segoe UI", 11),
            text_color="#CCCCCC",
            justify="left"
        ).pack(pady=(0, 10), padx=15, anchor="w")

        # Botones de acción
        btn_frame = ctk.CTkFrame(report_frame, fg_color="transparent")
        btn_frame.pack(pady=15)

        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar Reporte",
            command=lambda: self.guardar_reporte(datos, factores, recomendaciones),
            width=180,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color="#00AA00",
            hover_color="#008800"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="👤 Nuevo Paciente",
            command=self.mostrar_formulario_paciente,
            width=180,
            height=40,
            font=("Segoe UI", 13),
            fg_color="#0078D7",
            hover_color="#005A9E"
        ).pack(side="left", padx=10)

    def identificar_factores_riesgo(self, datos):
        """Identifica factores de riesgo del paciente"""
        factores = []
        puntos = 0

        if datos['edad'] > 55:
            factores.append(f"• Edad avanzada ({datos['edad']} años)")
            puntos += 2

        if datos['presion'] > 140:
            factores.append(f"• Hipertensión arterial ({datos['presion']} mmHg)")
            puntos += 2
        elif datos['presion'] > 130:
            factores.append(f"• Presión arterial elevada ({datos['presion']} mmHg)")
            puntos += 1

        if datos['colesterol'] > 240:
            factores.append(f"• Hipercolesterolemia ({datos['colesterol']} mg/dl)")
            puntos += 2
        elif datos['colesterol'] > 200:
            factores.append(f"• Colesterol límite alto ({datos['colesterol']} mg/dl)")
            puntos += 1

        if datos['glucemia_num'] == 1:
            factores.append("• Hiperglucemia en ayunas (diabetes/prediabetes)")
            puntos += 2

        if datos['fc_maxima'] < 120:
            factores.append(f"• Capacidad funcional severamente reducida (FC: {datos['fc_maxima']} lpm)")
            puntos += 3
        elif datos['fc_maxima'] < 140:
            factores.append(f"• Capacidad funcional reducida (FC: {datos['fc_maxima']} lpm)")
            puntos += 2

        if datos['dolor_ejercicio_num'] == 1:
            factores.append("• Angina inducida por ejercicio (altamente significativo)")
            puntos += 3

        if datos['depresion_st'] > 2:
            factores.append(f"• Depresión ST significativa ({datos['depresion_st']} mm)")
            puntos += 3
        elif datos['depresion_st'] > 1:
            factores.append(f"• Depresión ST moderada ({datos['depresion_st']} mm)")
            puntos += 2

        if datos['vasos'] >= 2:
            factores.append(f"• Enfermedad coronaria multivaso ({datos['vasos']} vasos)")
            puntos += 4
        elif datos['vasos'] == 1:
            factores.append("• Enfermedad coronaria de un vaso")
            puntos += 2

        return {'lista': factores, 'puntos': puntos}

    def generar_recomendaciones(self, datos, prob):
        """Genera recomendaciones médicas personalizadas"""
        recom = []

        if prob > 60:
            recom.append("🚨 MEDIDAS URGENTES:")
            recom.append("   - Evaluación cardiológica inmediata")
            recom.append("   - Considerar hospitalización")

        recom.append("\n💊 Farmacoterapia sugerida:")
        if prob > 30 or datos['vasos'] >= 1:
            recom.append("   - Antiagregante plaquetario (Aspirina 100mg/día)")
            recom.append("   - Betabloqueador")

        if datos['presion'] > 130:
            recom.append("   - IECA o ARA-II para control de presión")

        if datos['colesterol'] > 190:
            recom.append("   - Estatina de alta intensidad")

        recom.append("\n🏃 Modificaciones del estilo de vida:")
        recom.append("   - Dieta cardioprotectora (tipo mediterránea)")
        recom.append("   - Ejercicio aeróbico 150 min/semana")
        recom.append("   - Cesación completa de tabaquismo")
        recom.append("   - Control de peso (IMC 18.5-24.9)")

        recom.append("\n📅 Plan de seguimiento:")
        if prob > 60:
            recom.append("   - Evaluación inmediata con cardiólogo")
        elif prob > 40:
            recom.append("   - Control en 1-2 semanas")
        else:
            recom.append("   - Control en 1-3 meses")

        return "\n".join(recom)

    def guardar_reporte(self, datos, factores, recomendaciones):
        """Guarda el reporte en archivo TXT y PDF con selector de ubicación"""
        try:
            # Crear nombre base para el archivo usando nombre y cédula del paciente
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Limpiar el nombre para usarlo en el archivo (sin espacios ni caracteres especiales)
            nombre_limpio = datos['nombre'].replace(' ', '_').replace('.', '')
            cedula_limpia = datos['cedula'].replace('-', '')
            nombre_base = f"reporte_{nombre_limpio}_{cedula_limpia}_{timestamp}"
            
            # Mostrar diálogo para seleccionar ubicación
            archivo_guardar = filedialog.asksaveasfilename(
                title="Guardar Reporte",
                defaultextension=".txt",
                initialfile=nombre_base,
                filetypes=[
                    ("Archivos de texto", "*.txt"),
                    ("Documentos PDF", "*.pdf"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            # Si el usuario cancela, salir
            if not archivo_guardar:
                return
            
            # Determinar el formato según la extensión
            extension = os.path.splitext(archivo_guardar)[1].lower()
            
            # Contenido del reporte
            contenido = self.generar_contenido_reporte(datos, factores, recomendaciones)
            
            # Guardar según formato
            if extension == '.pdf':
                if REPORTLAB_DISPONIBLE:
                    self.guardar_como_pdf(archivo_guardar, datos, factores, recomendaciones, contenido)
                else:
                    messagebox.showwarning(
                        "Librería no disponible",
                        "No se puede generar PDF porque la librería 'reportlab' no está instalada.\n\n" +
                        "Se guardará como archivo de texto (.txt) en su lugar.\n\n" +
                        "Para habilitar PDF, instala: pip install reportlab"
                    )
                    archivo_guardar = archivo_guardar.replace('.pdf', '.txt')
                    with open(archivo_guardar, 'w', encoding='utf-8') as f:
                        f.write(contenido)
            else:
                # Guardar como TXT
                with open(archivo_guardar, 'w', encoding='utf-8') as f:
                    f.write(contenido)
            
            # También guardar copia en carpeta local
            os.makedirs('reportes', exist_ok=True)
            ruta_local = f"reportes/{nombre_base}.txt"
            with open(ruta_local, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            messagebox.showinfo(
                "Reporte Guardado",
                f"✅ Reporte guardado exitosamente:\n\n" +
                f"📄 Ubicación seleccionada:\n{archivo_guardar}\n\n" +
                f"📁 Copia local:\n{ruta_local}\n\n" +
                f"💾 Registro en historial: {self.historial_file}"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar reporte:\n{str(e)}")
    
    def generar_contenido_reporte(self, datos, factores, recomendaciones):
        """Genera el contenido del reporte en formato texto"""
        contenido = "=" * 70 + "\n"
        contenido += "REPORTE MÉDICO CARDIOVASCULAR\n"
        contenido += "=" * 70 + "\n\n"
        contenido += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        contenido += f"Paciente: {datos['nombre']}\n"
        contenido += f"Cédula: {datos['cedula']}\n\n"
        
        contenido += "DATOS DEL PACIENTE:\n"
        contenido += "-" * 70 + "\n"
        contenido += f"Edad: {datos['edad']} años | Sexo: {'Masculino' if datos['sexo']=='H' else 'Femenino'}\n"
        contenido += f"Presión Arterial: {datos['presion']} mmHg\n"
        contenido += f"Colesterol: {datos['colesterol']} mg/dl\n"
        contenido += f"Glucemia >120: {'Sí' if datos['glucemia_num']==1 else 'No'}\n"
        contenido += f"FC Máxima: {datos['fc_maxima']} lpm\n"
        contenido += f"Angina por ejercicio: {'Sí' if datos['dolor_ejercicio_num']==1 else 'No'}\n"
        contenido += f"Depresión ST: {datos['depresion_st']} mm\n"
        contenido += f"Vasos con estenosis: {datos['vasos']}\n\n"
        
        contenido += "EVALUACIÓN DE RIESGO:\n"
        contenido += "-" * 70 + "\n"
        prob = datos['prob_enfermedad']
        if prob < 30:
            nivel_riesgo = "BAJO"
        elif prob < 60:
            nivel_riesgo = "MODERADO"
        else:
            nivel_riesgo = "ALTO"
        contenido += f"Probabilidad de Enfermedad: {prob:.1f}%\n"
        contenido += f"Nivel de Riesgo: {nivel_riesgo}\n"
        contenido += f"Riesgo Framingham (10 años): {datos['riesgo_fram']}%\n\n"
        
        contenido += "FACTORES DE RIESGO:\n"
        contenido += "-" * 70 + "\n"
        if factores['lista']:
            for factor in factores['lista']:
                contenido += factor + "\n"
        else:
            contenido += "✅ No se identifican factores de riesgo mayores\n"
        contenido += f"\nPuntuación total: {factores['puntos']} puntos\n\n"
        
        contenido += "RECOMENDACIONES:\n"
        contenido += "-" * 70 + "\n"
        contenido += recomendaciones + "\n\n"
        
        contenido += "=" * 70 + "\n"
        contenido += "NOTA: Este reporte es una herramienta de apoyo diagnóstico.\n"
        contenido += "NO reemplaza el juicio clínico del médico tratante.\n"
        contenido += "=" * 70 + "\n"
        
        return contenido
    
    def guardar_como_pdf(self, archivo, datos, factores, recomendaciones, contenido_txt):
        """Guarda el reporte como PDF"""
        try:
            # Crear PDF
            doc = SimpleDocTemplate(archivo, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            titulo_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#0078D7'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            subtitulo_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#00BFFF'),
                spaceAfter=12,
                fontName='Helvetica-Bold'
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            # Título
            story.append(Paragraph("REPORTE MÉDICO CARDIOVASCULAR", titulo_style))
            story.append(Paragraph(f"Paciente: {datos['nombre']}", normal_style))
            story.append(Paragraph(f"Cédula: {datos['cedula']}", normal_style))
            story.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Datos del paciente
            story.append(Paragraph("DATOS DEL PACIENTE", subtitulo_style))
            datos_tabla = [
                ['Edad:', f"{datos['edad']} años", 'Sexo:', 'Masculino' if datos['sexo']=='H' else 'Femenino'],
                ['Presión Arterial:', f"{datos['presion']} mmHg", 'Colesterol:', f"{datos['colesterol']} mg/dl"],
                ['Glucemia >120:', 'Sí' if datos['glucemia_num']==1 else 'No', 'FC Máxima:', f"{datos['fc_maxima']} lpm"],
                ['Angina ejercicio:', 'Sí' if datos['dolor_ejercicio_num']==1 else 'No', 'Depresión ST:', f"{datos['depresion_st']} mm"],
                ['Vasos estenosis:', str(datos['vasos']), '', '']
            ]
            
            tabla = Table(datos_tabla, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
                ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#E8F4F8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(tabla)
            story.append(Spacer(1, 0.3*inch))
            
            # Evaluación de riesgo
            story.append(Paragraph("EVALUACIÓN DE RIESGO", subtitulo_style))
            prob = datos['prob_enfermedad']
            if prob < 30:
                nivel_riesgo = "BAJO"
                color_riesgo = colors.green
            elif prob < 60:
                nivel_riesgo = "MODERADO"
                color_riesgo = colors.orange
            else:
                nivel_riesgo = "ALTO"
                color_riesgo = colors.red
            
            riesgo_style = ParagraphStyle(
                'RiesgoStyle',
                parent=normal_style,
                fontSize=12,
                textColor=color_riesgo,
                fontName='Helvetica-Bold'
            )
            
            story.append(Paragraph(f"Probabilidad de Enfermedad Cardíaca: {prob:.1f}%", riesgo_style))
            story.append(Paragraph(f"Nivel de Riesgo: {nivel_riesgo}", riesgo_style))
            story.append(Paragraph(f"Riesgo Cardiovascular a 10 años (Framingham): {datos['riesgo_fram']}%", normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Factores de riesgo
            story.append(Paragraph("FACTORES DE RIESGO IDENTIFICADOS", subtitulo_style))
            if factores['lista']:
                for factor in factores['lista']:
                    story.append(Paragraph(factor, normal_style))
            else:
                story.append(Paragraph("✅ No se identifican factores de riesgo mayores", normal_style))
            story.append(Paragraph(f"<b>Puntuación total de riesgo: {factores['puntos']} puntos</b>", normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Recomendaciones
            story.append(Paragraph("RECOMENDACIONES MÉDICAS", subtitulo_style))
            recom_lineas = recomendaciones.split('\n')
            for linea in recom_lineas:
                if linea.strip():
                    story.append(Paragraph(linea, normal_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Nota final
            nota_style = ParagraphStyle(
                'NotaStyle',
                parent=normal_style,
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("=" * 80, nota_style))
            story.append(Paragraph("NOTA: Este reporte es una herramienta de apoyo diagnóstico.", nota_style))
            story.append(Paragraph("NO reemplaza el juicio clínico del médico tratante.", nota_style))
            story.append(Paragraph("=" * 80, nota_style))
            
            # Generar PDF
            doc.build(story)
            
        except Exception as e:
            messagebox.showerror("Error PDF", f"Error al generar PDF:\n{str(e)}\n\nSe guardará como TXT")
            archivo_txt = archivo.replace('.pdf', '.txt')
            with open(archivo_txt, 'w', encoding='utf-8') as f:
                f.write(contenido_txt)