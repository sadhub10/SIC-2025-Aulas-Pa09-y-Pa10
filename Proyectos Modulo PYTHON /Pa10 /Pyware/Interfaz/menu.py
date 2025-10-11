
import tkinter as tk
from .tab_registro import mostrar_registro_diario
from .tabs_visualizaciones import mostrar_visualizaciones
from .tabs_analisis import mostrar_analisis_estadistico
from .tabs_simulacion import mostrar_simulacion_dataset
from .tab_perfil import mostrar_perfil  
from .tabs_reportes import mostrar_reportes


def construir_menu(panel_derecho: tk.Frame, menu_lateral: tk.Frame):
    opciones = [
        ("Registro Diario", mostrar_registro_diario),
        ("Análisis Estadístico", mostrar_analisis_estadistico),
        ("Simulación Dataset", mostrar_simulacion_dataset),
        (" Reporte Visual", mostrar_reportes),
        ("Mi Perfil", mostrar_perfil), 
    ]

    def resaltar(e): e.widget.config(bg="#E0E0E0")
    def restaurar(e): e.widget.config(bg="white")

    for texto, fn in opciones:
        btn = tk.Label(menu_lateral, text=texto, bg="white", fg="black",
                       font=("Arial", 10), anchor="w", padx=10, cursor="hand2")
        btn.pack(fill="x", pady=2)
        btn.bind("<Enter>", resaltar)
        btn.bind("<Leave>", restaurar)
        btn.bind("<Button-1>", lambda e, f=fn: f(panel_derecho))
