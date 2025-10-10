# Archivo de ejecución principal de la aplicación Heart Risk System
import customtkinter as ctk
from tkinter import messagebox
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
from config import FileSelector
from analysis.preprocesing import PreprocessingFrame
from models.eda import EDAFrame
from analysis.visualization import VisualizationFrame
import sys
import gc
from PIL import Image

# Importar el módulo de modelos de forma segura
try:
    from models.models_predictive import ModelosFrame
    MODELOS_DISPONIBLE = True
except ImportError:
    MODELOS_DISPONIBLE = False
    print("⚠️ Advertencia: Módulo de modelos predictivos no disponible")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Heart Risk System")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variable para controlar el cierre
        self._closing = False
        self._switching = False
        
        # Protocolo para cerrar la ventana correctamente
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # === Menú lateral ===
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)

        # Logo/Título del sidebar
        try:
            # Intentar cargar el logo desde archivo
            logo_image = Image.open("assets/image.png")  # Cambia la ruta a tu logo
            
            # Mantener aspecto original y ajustar a ancho máximo de 180px
            width, height = logo_image.size
            max_width = 180
            max_height = 100
            
            # Calcular nuevo tamaño manteniendo proporción
            ratio = min(max_width/width, max_height/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            
            logo_image = logo_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_photo = ctk.CTkImage(
                light_image=logo_image, 
                dark_image=logo_image, 
                size=(new_width, new_height)
            )
            
            # Frame contenedor para centrar el logo
            logo_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
            logo_container.pack(pady=(30, 40), fill="x")
            
            self.sidebar_logo = ctk.CTkLabel(
                logo_container,
                image=self.logo_photo,
                text=""
            )
            self.sidebar_logo.pack(anchor="center")
            
        except Exception as e:
            # Fallback: usar texto si no se encuentra la imagen
            print(f"⚠️ No se pudo cargar el logo: {e}")
            self.sidebar_title = ctk.CTkLabel(
                self.sidebar,
                text="Heart Risk\nSystem",
                font=("Segoe UI", 20, "bold"),
                text_color="#00BFFF"
            )
            self.sidebar_title.pack(pady=(30, 40))

        # Botones del menú
        self.btn_carga = ctk.CTkButton(
            self.sidebar,
            text="📂 Cargar Datos",
            command=self.mostrar_carga,
            width=180,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#0078D7",
            hover_color="#005A9E"
        )
        self.btn_carga.pack(pady=10, padx=20)

        self.btn_procesar = ctk.CTkButton(
            self.sidebar,
            text="⚙️ Preprocesar",
            command=self.mostrar_procesamiento,
            width=180,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666",
            state="disabled"
        )
        self.btn_procesar.pack(pady=10, padx=20)

        self.btn_eda = ctk.CTkButton(
            self.sidebar,
            text="📊 Análisis EDA",
            command=self.mostrar_eda,
            width=180,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666",
            state="disabled"
        )
        self.btn_eda.pack(pady=10, padx=20)

        self.btn_modelos = ctk.CTkButton(
            self.sidebar,
            text="🤖 Modelos ML",
            command=self.mostrar_modelos,
            width=180,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666",
            state="disabled"
        )
        self.btn_modelos.pack(pady=10, padx=20)

        self.btn_visualizar = ctk.CTkButton(
            self.sidebar,
            text="📈 Visualizar",
            command=self.mostrar_visualizacion,
            width=180,
            height=50,
            font=("Segoe UI", 14),
            fg_color="#444",
            hover_color="#666",
            state="disabled"
        )
        self.btn_visualizar.pack(pady=10, padx=20)

        # Separador
        separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="#444")
        separator.pack(pady=20, padx=20, fill="x")

        # Info del estado
        self.label_estado = ctk.CTkLabel(
            self.sidebar,
            text="Estado: Inicio",
            font=("Segoe UI", 11),
            text_color="#AAAAAA",
            wraplength=180
        )
        self.label_estado.pack(pady=(10, 10), padx=10)

        # Indicador de progreso
        self.progress_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.progress_frame.pack(pady=(10, 20), padx=20)

        progress_text = """
🔄 Pipeline:
  1️⃣ Cargar datos
  2️⃣ Preprocesar
  3️⃣ Análisis EDA
  4️⃣ Modelos ML
  5️⃣ Visualización
        """
        self.label_progress = ctk.CTkLabel(
            self.progress_frame,
            text=progress_text,
            font=("Courier", 9),
            text_color="#666",
            justify="left"
        )
        self.label_progress.pack()

        # Container para el frame principal
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        # Variables de estado
        self.main_frame = None
        self.df_actual = None
        self.df_cuantitativo = None
        self.df_descriptivo = None

        # Mostrar vista inicial
        self.after(100, self.mostrar_carga)
        self.actualizar_progreso()

    def limpiar_matplotlib(self):
        """Limpia todas las figuras de matplotlib"""
        try:
            plt.close('all')
            gc.collect()
        except:
            pass

    def limpiar_frame_principal(self):
        """Limpia el frame principal de forma segura"""
        if self._closing or self._switching:
            return
            
        self._switching = True
        
        try:
            if self.main_frame is not None:
                # Limpiar matplotlib
                self.limpiar_matplotlib()
                
                # Detener todos los after pendientes
                try:
                    for after_id in self.tk.call('after', 'info'):
                        self.after_cancel(after_id)
                except:
                    pass
                
                # Destruir todos los widgets hijos
                try:
                    for widget in self.main_frame.winfo_children():
                        try:
                            widget.destroy()
                        except:
                            pass
                except:
                    pass
                
                # Desempaquetar
                try:
                    self.main_frame.pack_forget()
                except:
                    pass
                
                # Forzar actualización
                self.update_idletasks()
                
                # Destruir el frame
                try:
                    self.main_frame.destroy()
                except:
                    pass
                
                self.main_frame = None
                
                # Forzar recolección de basura
                gc.collect()
                
                # Esperar un poco más
                self.update()
                
        except Exception as e:
            print(f"⚠️ Error al limpiar frame: {e}")
        finally:
            self._switching = False

    def actualizar_progreso(self):
        """Actualiza el indicador de progreso"""
        if self._closing:
            return
            
        try:
            progress_text = "🔄 Pipeline:\n"
            
            if self.df_actual is not None:
                progress_text += "  ✅ Cargar datos\n"
            else:
                progress_text += "  1️⃣ Cargar datos\n"
            
            if self.df_cuantitativo is not None and self.df_descriptivo is not None:
                progress_text += "  ✅ Preprocesar\n"
            else:
                progress_text += "  2️⃣ Preprocesar\n"
            
            if self.df_cuantitativo is not None:
                progress_text += "  ✅ Análisis EDA\n"
            else:
                progress_text += "  3️⃣ Análisis EDA\n"
            
            if self.df_descriptivo is not None:
                progress_text += "  ✅ Modelos ML\n"
            else:
                progress_text += "  4️⃣ Modelos ML\n"
            
            if self.df_cuantitativo is not None and self.df_descriptivo is not None:
                progress_text += "  ✅ Visualización"
            else:
                progress_text += "  5️⃣ Visualización"
            
            if self.winfo_exists():
                self.label_progress.configure(text=progress_text)
        except:
            pass

    def actualizar_estado(self, mensaje):
        """Actualiza el label de estado en el sidebar"""
        if self._closing:
            return
        try:
            if self.winfo_exists():
                self.label_estado.configure(text=f"Estado: {mensaje}")
                self.actualizar_progreso()
        except:
            pass

    def habilitar_navegacion(self):
        """Habilita los botones según el estado de los datos"""
        if self._closing:
            return
            
        try:
            if self.winfo_exists():
                if self.df_actual is not None:
                    self.btn_procesar.configure(state="normal", fg_color="#0078D7")
                
                if self.df_cuantitativo is not None and self.df_descriptivo is not None:
                    self.btn_eda.configure(state="normal", fg_color="#0078D7")
                    self.btn_modelos.configure(state="normal", fg_color="#0078D7")
                    self.btn_visualizar.configure(state="normal", fg_color="#0078D7")
        except:
            pass

    def cambiar_vista(self, callback):
        """Cambia de vista de forma segura"""
        if self._closing or self._switching:
            return
        
        # Limpiar frame actual
        self.limpiar_frame_principal()
        
        # Esperar un poco antes de crear el nuevo frame
        self.after(50, callback)

    def mostrar_carga(self):
        """Muestra la vista de carga de archivos"""
        if self._closing:
            return
        
        def _mostrar():
            try:
                self.main_frame = FileSelector(self)
                self.main_frame.pack(in_=self.content_container, fill="both", expand=True)
                
                if self.winfo_exists():
                    self.btn_carga.configure(fg_color="#0078D7")
                    self.btn_procesar.configure(fg_color="#444" if self.df_actual is None else "#0078D7")
                    self.btn_eda.configure(fg_color="#444")
                    self.btn_modelos.configure(fg_color="#444")
                    self.btn_visualizar.configure(fg_color="#444")
            except Exception as e:
                print(f"❌ Error al mostrar carga: {e}")
        
        if self.main_frame is not None:
            self.cambiar_vista(_mostrar)
        else:
            _mostrar()

    def cargar_datos(self, df):
        """Callback cuando se carga un archivo exitosamente"""
        self.df_actual = df
        self.actualizar_estado(f"✅ Datos cargados")
        self.habilitar_navegacion()

    def mostrar_procesamiento(self):
        """Muestra la vista de preprocesamiento"""
        if self._closing:
            return
            
        if self.df_actual is None:
            self.actualizar_estado("⚠️ Carga datos primero")
            self.mostrar_carga()
            return
        
        def _mostrar():
            try:
                self.main_frame = PreprocessingFrame(self, df=self.df_actual)
                self.main_frame.pack(in_=self.content_container, fill="both", expand=True)
                
                if self.winfo_exists():
                    self.btn_carga.configure(fg_color="#0078D7")
                    self.btn_procesar.configure(fg_color="#00AA00")
                    self.btn_eda.configure(fg_color="#444" if self.df_cuantitativo is None else "#0078D7")
                    self.btn_modelos.configure(fg_color="#444" if self.df_descriptivo is None else "#0078D7")
                    self.btn_visualizar.configure(fg_color="#444" if self.df_cuantitativo is None else "#0078D7")
            except Exception as e:
                print(f"❌ Error al mostrar preprocesamiento: {e}")
        
        self.cambiar_vista(_mostrar)

    def datos_procesados(self, df_cuant, df_desc):
        """Callback cuando se procesan los datos"""
        self.df_cuantitativo = df_cuant
        self.df_descriptivo = df_desc
        self.actualizar_estado("✅ Datos procesados")
        self.habilitar_navegacion()

    def mostrar_eda(self):
        """Muestra la vista de análisis EDA"""
        if self._closing:
            return
            
        if self.df_cuantitativo is None or self.df_descriptivo is None:
            self.actualizar_estado("⚠️ Procesa datos primero")
            self.mostrar_procesamiento()
            return
        
        def _mostrar():
            try:
                self.main_frame = EDAFrame(
                    self,
                    df_cuant=self.df_cuantitativo,
                    df_desc=self.df_descriptivo
                )
                self.main_frame.pack(in_=self.content_container, fill="both", expand=True)
                self.actualizar_estado("📊 Análisis EDA")
                
                if self.winfo_exists():
                    self.btn_carga.configure(fg_color="#0078D7")
                    self.btn_procesar.configure(fg_color="#0078D7")
                    self.btn_eda.configure(fg_color="#9333EA")
                    self.btn_modelos.configure(fg_color="#0078D7")
                    self.btn_visualizar.configure(fg_color="#0078D7")
            except Exception as e:
                print(f"❌ Error al mostrar EDA: {e}")
        
        self.cambiar_vista(_mostrar)

    def mostrar_modelos(self):
        """Muestra la vista de modelos predictivos"""
        if self._closing:
            return
            
        if not MODELOS_DISPONIBLE:
            messagebox.showerror(
                "Módulo no disponible",
                "El módulo de modelos predictivos no está disponible."
            )
            return
        
        if self.df_descriptivo is None:
            self.actualizar_estado("⚠️ Procesa datos primero")
            self.mostrar_procesamiento()
            return
        
        def _mostrar():
            try:
                self.main_frame = ModelosFrame(self)
                self.main_frame.pack(in_=self.content_container, fill="both", expand=True)
                self.actualizar_estado("🤖 Modelos ML")
                
                if self.winfo_exists():
                    self.btn_carga.configure(fg_color="#0078D7")
                    self.btn_procesar.configure(fg_color="#0078D7")
                    self.btn_eda.configure(fg_color="#0078D7")
                    self.btn_modelos.configure(fg_color="#00AA00")
                    self.btn_visualizar.configure(fg_color="#0078D7")
            except Exception as e:
                print(f"❌ Error al mostrar modelos: {e}")
        
        self.cambiar_vista(_mostrar)

    def mostrar_visualizacion(self):
        """Muestra la vista de visualización"""
        if self._closing:
            return
            
        if self.df_cuantitativo is None or self.df_descriptivo is None:
            self.actualizar_estado("⚠️ Procesa datos primero")
            self.mostrar_procesamiento()
            return
        
        def _mostrar():
            try:
                self.main_frame = VisualizationFrame(
                    self,
                    df_cuant=self.df_cuantitativo,
                    df_desc=self.df_descriptivo,
                    df_original=self.df_actual
                )
                self.main_frame.pack(in_=self.content_container, fill="both", expand=True)
                self.actualizar_estado("📈 Visualización")
                
                if self.winfo_exists():
                    self.btn_carga.configure(fg_color="#0078D7")
                    self.btn_procesar.configure(fg_color="#0078D7")
                    self.btn_eda.configure(fg_color="#0078D7")
                    self.btn_modelos.configure(fg_color="#0078D7")
                    self.btn_visualizar.configure(fg_color="#00AA00")
            except Exception as e:
                print(f"❌ Error al mostrar visualización: {e}")
        
        self.cambiar_vista(_mostrar)

    def on_closing(self):
        """Maneja el cierre de la aplicación de forma segura"""
        if self._closing:
            return
        
        print("🔄 Cerrando aplicación...")
        self._closing = True
        
        try:
            # Detener todos los after pendientes
            try:
                for after_id in self.tk.call('after', 'info'):
                    try:
                        self.after_cancel(after_id)
                    except:
                        pass
            except:
                pass
            
            # Limpiar matplotlib
            self.limpiar_matplotlib()
            
            # Limpiar el frame principal
            if self.main_frame is not None:
                try:
                    self.main_frame.destroy()
                except:
                    pass
                self.main_frame = None
            
            # Limpiar datos
            self.df_actual = None
            self.df_cuantitativo = None
            self.df_descriptivo = None
            
            # Forzar actualización y recolección de basura
            self.update_idletasks()
            gc.collect()
            
            # Destruir la ventana
            self.quit()
            self.destroy()
            
            print("✅ Aplicación cerrada correctamente")
        except Exception as e:
            print(f"⚠️ Error al cerrar: {e}")
            # Forzar salida
            sys.exit(0)

def main():
    app = None
    try:
        # Configurar matplotlib antes de iniciar
        plt.ioff()  # Modo no interactivo
        
        app = MainApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n✅ Aplicación cerrada por el usuario")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpieza final
        try:
            plt.close('all')
        except:
            pass
        
        if app is not None:
            try:
                app.quit()
                app.destroy()
            except:
                pass
        
        # Forzar limpieza
        gc.collect()
        print("🏁 Programa terminado")

if __name__ == "__main__":
    main()