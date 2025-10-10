"""
ASISTENTE PARA AGRICULTORES - PANAMÁ
===================================

Sistema modular de asistencia agrícola para agricultores panameños.
Proporciona información sobre cultivos, análisis climático, visualizaciones
y recomendaciones basadas en datos.

Autores: Pandas con flow
Fecha: 2025
"""

import tkinter as tk
from tkinter import messagebox
import os
import sys
from dotenv import load_dotenv

# Configurar matplotlib antes de importar los módulos
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
plt.style.use('default')

# Cargar variables de entorno
load_dotenv()

# Importar módulos del sistema
try:
    from modulos.datos import DatosManager
    from modulos.graficos import GraficosManager
    from modulos.clima import ClimaManager
    from modulos.interfaz import InterfazManager
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrese de que la carpeta 'modulos' existe y contiene todos los archivos necesarios")
    sys.exit(1)


class AsistenteAgricola:
    """Clase principal del Sistema de Asistencia Agrícola"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Asistente para Agricultores - Panamá")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        
        # Configuración inicial
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.ubicacion_actual = os.getenv('DEFAULT_LOCATION', 'Panama City')
        
        # Inicializar managers
        self._inicializar_managers()
        
        # Configurar menú
        self._configurar_menu()
        
        # Configurar interfaz
        self.interfaz_manager.configurar_interfaz()
        
        # Mensaje de bienvenida
        print(f"Sistema Agrícola iniciado correctamente")
        print(f"{len(self.datos_manager.df)} cultivos disponibles")
        
        # Actualizar clima inicial
        self.root.after(1000, self.clima_manager.actualizar_interfaz_clima)
    
    def _inicializar_managers(self):
        """Inicializa todos los managers del sistema"""
        # Manager de datos - debe ser el primero
        self.datos_manager = DatosManager()
        
        # Manager de gráficos  
        self.graficos_manager = GraficosManager(self.datos_manager.df)
        
        # Manager de clima
        self.clima_manager = ClimaManager(
            api_key=self.api_key,
            ubicacion_actual=self.ubicacion_actual
        )
        
        # Manager de interfaz - debe ser el último
        self.interfaz_manager = InterfazManager(
            root=self.root,
            datos_manager=self.datos_manager,
            graficos_manager=self.graficos_manager,
            clima_manager=self.clima_manager
        )
    
    def _configurar_menu(self):
        """Configura la barra de menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        menu_archivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=menu_archivo)
        menu_archivo.add_command(label="Recargar Dataset", command=self._recargar_dataset)
        menu_archivo.add_command(label="Exportar Datos Completos", command=self._exportar_datos)
        menu_archivo.add_separator()
        menu_archivo.add_command(label="Salir", command=self.root.quit)
        
        # Menú Cultivos
        menu_cultivos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Cultivos", menu=menu_cultivos)
        menu_cultivos.add_command(label="Ver Dataset Completo", 
                                 command=lambda: self.datos_manager.mostrar_dataset(self.root))
        menu_cultivos.add_command(label="Estadísticas Generales", 
                                 command=lambda: self.datos_manager.mostrar_estadisticas(self.root))
        menu_cultivos.add_separator()
        menu_cultivos.add_command(label="Buscar Cultivo", command=self._enfocar_busqueda)
        
        # Menú Gráficos
        menu_graficos = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Gráficos", menu=menu_graficos)
        menu_graficos.add_command(label="Gráfico del Cultivo Actual", 
                                 command=self.interfaz_manager.generar_grafico_cultivo)
        menu_graficos.add_command(label="Test de Gráficos", 
                                 command=lambda: self.graficos_manager.test_graficos_simple(self.root))
        
        # Menú Clima
        menu_clima = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Clima", menu=menu_clima)
        menu_clima.add_command(label="Configurar API", 
                              command=lambda: self.clima_manager.configurar_api(self.root))
        menu_clima.add_command(label="Cambiar Ubicación", 
                              command=lambda: self.clima_manager.cambiar_ubicacion(self.root))
        menu_clima.add_command(label="Consultar Ciudad", 
                              command=lambda: self.clima_manager.consultar_clima_ciudad(self.root))
        menu_clima.add_separator()
        menu_clima.add_command(label="Actualizar Clima", 
                              command=self.clima_manager.actualizar_interfaz_clima)
        menu_clima.add_command(label="Verificar Clima del Cultivo", 
                              command=self.interfaz_manager.verificar_clima)
        
        # Menú Herramientas
        menu_herramientas = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=menu_herramientas)
        menu_herramientas.add_command(label="Calculadora de Rendimiento", command=self._abrir_calculadora)
        menu_herramientas.add_separator()
        menu_herramientas.add_command(label="Información del Sistema", command=self._mostrar_info_sistema)
        
        # Menú Ayuda
        menu_ayuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=menu_ayuda)
        menu_ayuda.add_command(label="Guía de Uso", command=self._mostrar_guia_uso)
        menu_ayuda.add_command(label="Cultivos Disponibles", command=self._mostrar_cultivos_disponibles)
        menu_ayuda.add_separator()
        menu_ayuda.add_command(label="Acerca de", command=self._mostrar_acerca_de)
    
    def _recargar_dataset(self):
        """Recarga el dataset de cultivos"""
        try:
            self.datos_manager.recargar_dataset()
            # Actualizar el dataframe en el graficos_manager
            self.graficos_manager.df = self.datos_manager.df
            messagebox.showinfo("Éxito", f"Dataset recargado: {len(self.datos_manager.df)} cultivos")
            
            if hasattr(self.interfaz_manager, 'barra_estado') and self.interfaz_manager.barra_estado:
                self.interfaz_manager.barra_estado.config(text="Dataset recargado exitosamente")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al recargar dataset: {str(e)}")
    
    def _exportar_datos(self):
        """Exporta los datos completos"""
        try:
            filename = self.datos_manager.exportar_datos_completos()
            if filename:
                messagebox.showinfo("Éxito", f"Datos exportados en: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")
    
    def _enfocar_busqueda(self):
        """Enfoca el campo de búsqueda"""
        if hasattr(self.interfaz_manager, 'entrada_cultivo') and self.interfaz_manager.entrada_cultivo:
            self.interfaz_manager.entrada_cultivo.focus()
    
    def _abrir_calculadora(self):
        """Abre calculadora de rendimiento"""
        ventana_calc = tk.Toplevel(self.root)
        ventana_calc.title("Calculadora de Rendimiento")
        ventana_calc.geometry("400x300")
        
        tk.Label(ventana_calc, text="CALCULADORA DE RENDIMIENTO", 
                font=("Arial", 14, "bold")).pack(pady=10)
        
        # Campos de entrada
        frame_campos = tk.Frame(ventana_calc)
        frame_campos.pack(pady=10)
        
        tk.Label(frame_campos, text="Área cultivada (hectáreas):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entrada_area = tk.Entry(frame_campos)
        entrada_area.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_campos, text="Rendimiento esperado (t/ha):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entrada_rendimiento = tk.Entry(frame_campos)
        entrada_rendimiento.grid(row=1, column=1, padx=5, pady=5)
        
        # Resultado
        resultado_label = tk.Label(ventana_calc, text="", font=("Arial", 12, "bold"), fg="green")
        resultado_label.pack(pady=10)
        
        def calcular():
            try:
                area = float(entrada_area.get())
                rendimiento = float(entrada_rendimiento.get())
                total = area * rendimiento
                resultado_label.config(text=f"Producción Total: {total:.2f} toneladas")
            except ValueError:
                messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        
        tk.Button(ventana_calc, text="Calcular", command=calcular, 
                 bg="green", fg="white", font=("Arial", 12)).pack(pady=10)
    
    def _mostrar_info_sistema(self):
        """Muestra información del sistema"""
        ventana_info = tk.Toplevel(self.root)
        ventana_info.title("Información del Sistema")
        ventana_info.geometry("500x400")
        
        from tkinter import scrolledtext
        texto_info = scrolledtext.ScrolledText(ventana_info, font=("Arial", 10))
        texto_info.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        info_sistema = f"""
SISTEMA AGRÍCOLA PARA PANAMÁ - INFORMACIÓN
{'='*45}

ESTADÍSTICAS DEL SISTEMA:
• Total de cultivos: {len(self.datos_manager.df)}
• Base de datos: dataset_cultivos_panama.csv

MÓDULOS ACTIVOS:
• Gestión de Datos: Activo
• Visualizaciones: Activo  
• Clima API: {'Configurado' if self.api_key else 'No configurado'}
• Interfaz de Usuario: Activo

CONFIGURACIÓN CLIMÁTICA:
• API Key: {'Configurada' if self.api_key else 'No configurada'}
• Ubicación actual: {self.ubicacion_actual}

ARCHIVOS DEL SISTEMA:
• asistente_agricola_modular.py (Principal)
• modulos/datos.py (Gestión de datos)
• modulos/graficos.py (Visualizaciones)
• modulos/clima.py (API del clima)
• modulos/interfaz.py (Interfaz de usuario)
• dataset_cultivos_panama.csv (Base de datos)

CARACTERÍSTICAS:
• Búsqueda inteligente de cultivos
• Análisis comparativos automáticos
• Gráficos personalizados por cultivo
• Integración con datos climáticos en tiempo real
• Exportación de reportes detallados
• Interfaz intuitiva y profesional

OBJETIVO:
Proporcionar a los agricultores panameños información 
precisa y actualizada para la toma de decisiones 
agrícolas basadas en datos científicos.

Desarrollado con Python, Tkinter, Pandas y Matplotlib.
        """
        
        texto_info.insert(tk.END, info_sistema)
    
    def _mostrar_guia_uso(self):
        """Muestra la guía de uso del sistema"""
        ventana_guia = tk.Toplevel(self.root)
        ventana_guia.title("Guía de Uso")
        ventana_guia.geometry("700x500")
        
        from tkinter import scrolledtext
        texto_guia = scrolledtext.ScrolledText(ventana_guia, font=("Arial", 10))
        texto_guia.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        guia_texto = """
GUÍA DE USO - ASISTENTE AGRÍCOLA PANAMÁ
======================================

INICIO RÁPIDO:

1. BUSCAR CULTIVO:
   • Escriba el nombre en el campo de búsqueda
   • Use las sugerencias de cultivos comunes
   • Presione Enter o haga clic en "Buscar"

2. ANÁLISIS DEL CULTIVO:
   • "Análisis Detallado": Información completa y comparaciones
   • "Generar Gráfico": Visualizaciones personalizadas
   • "Verificar Clima": Compatibilidad con clima actual

3. EXPLORAR DATOS:
   • "Ver Dataset Completo": Todos los cultivos con filtros
   • "Estadísticas": Análisis general del sistema
   • "Gráfico de Rendimientos": Comparaciones visuales

FUNCIONES AVANZADAS:

MENÚ CULTIVOS:
• Dataset completo con filtros por temporada y lluvia
• Estadísticas generales del sistema
• Búsqueda rápida de cultivos

MENÚ GRÁFICOS:
• Gráficos personalizados por cultivo seleccionado
• Test de funcionamiento del sistema
• Exportación de imágenes en alta calidad

MENÚ CLIMA:
• Configuración de API de OpenWeatherMap
• Consulta de clima por ciudad
• Análisis de compatibilidad climática
• Cambio de ubicación base

MENÚ HERRAMIENTAS:
• Calculadora de rendimiento por área
• Información técnica del sistema

CONSEJOS DE USO:

Para mejores resultados:
1. Configure la API del clima para datos actualizados
2. Use nombres exactos de cultivos (ej: "Arroz", no "arroz")
3. Explore las comparaciones en "Análisis Detallado"
4. Guarde los gráficos importantes usando los botones

CULTIVOS PRINCIPALES:
Arroz, Maíz, Frijol, Plátano, Yuca, Ñame, Café, Cacao,
Frutas: Naranja, Limón, Mango, Papaya, Piña, Aguacate
Hortalizas: Tomate, Cebolla, Pimiento, Lechuga

SOLUCIÓN DE PROBLEMAS:
• Si no aparecen gráficos: Use "Test de Gráficos"
• Si no hay datos de clima: Configure API en Menú > Clima
• Para reportar errores: Verifique "Información del Sistema"

¡Explore todas las funciones para aprovechar al máximo el sistema!
        """
        
        texto_guia.insert(tk.END, guia_texto)
    
    def _mostrar_cultivos_disponibles(self):
        """Muestra lista de cultivos disponibles"""
        ventana_cultivos = tk.Toplevel(self.root)
        ventana_cultivos.title("Cultivos Disponibles")
        ventana_cultivos.geometry("600x400")
        
        from tkinter import scrolledtext
        texto_cultivos = scrolledtext.ScrolledText(ventana_cultivos, font=("Arial", 11))
        texto_cultivos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        lista_cultivos = "CULTIVOS DISPONIBLES EN EL SISTEMA\n"
        lista_cultivos += "="*40 + "\n\n"
        
        for i, cultivo in enumerate(self.datos_manager.obtener_lista_cultivos(), 1):
            lista_cultivos += f"{i:2d}. {cultivo}\n"
        
        lista_cultivos += f"\nTotal: {len(self.datos_manager.df)} cultivos disponibles"
        lista_cultivos += f"\n\nPuede buscar cualquier cultivo de esta lista usando el campo de búsqueda principal."
        
        texto_cultivos.insert(tk.END, lista_cultivos)
    
    def _mostrar_acerca_de(self):
        """Muestra información sobre el sistema"""
        mensaje = """
ASISTENTE PARA AGRICULTORES - PANAMÁ

Sistema de asistencia técnica para agricultores
basado en datos científicos y análisis estadístico.

Características:
• 25 cultivos de Panamá
• Análisis climático en tiempo real
• Visualizaciones personalizadas
• Comparaciones inteligentes
• Exportación de reportes

Tecnología:
• Python 3.11+
• Tkinter (Interfaz)  
• Pandas (Datos)
• Matplotlib (Gráficos)
• OpenWeatherMap API (Clima)

Desarrollado para apoyar la agricultura panameña
con herramientas modernas y accesibles.

© 2025 - Sistema Agrícola AI
        """
        messagebox.showinfo("Acerca de", mensaje)


def main():
    """Función principal del sistema"""
    try:
        # Verificar que existe el dataset
        if not os.path.exists("dataset_cultivos_panama.csv"):
            print("Error: No se encontró el archivo 'dataset_cultivos_panama.csv'")
            print("   Asegúrese de que el archivo está en la misma carpeta que el programa")
            return
        
        root = tk.Tk()
        
        try:
            root.iconbitmap("icono.ico")
        except:
            pass 
        
        # Inicializar sistema
        app = AsistenteAgricola(root)
        
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        pos_x = (root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error crítico al inicializar el sistema: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()