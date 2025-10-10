import requests
import json
import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime


class ClimaManager:
    """Clase para manejar todas las funciones relacionadas con el clima"""
    
    def __init__(self, api_key=None, ubicacion_actual='Panama City', barra_estado=None):
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY', '')
        self.ubicacion_actual = ubicacion_actual
        self.barra_estado = barra_estado
        
        # Configuración de la API
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        
        # Elementos de interfaz para clima
        self.label_ubicacion = None
        self.label_temperatura = None
        self.label_humedad = None
        self.label_clima_desc = None
    
    def configurar_elementos_interfaz(self, label_ubicacion, label_temperatura, label_humedad, label_clima_desc):
        """Configura los elementos de la interfaz para mostrar información del clima"""
        self.label_ubicacion = label_ubicacion
        self.label_temperatura = label_temperatura  
        self.label_humedad = label_humedad
        self.label_clima_desc = label_clima_desc
    
    def configurar_api(self, root):
        """Permite configurar la API key de OpenWeatherMap"""
        ventana_config = tk.Toplevel(root)
        ventana_config.title("Configurar API del Clima")
        ventana_config.geometry("400x200")
        ventana_config.grab_set()
        
        tk.Label(ventana_config, text="API Key de OpenWeatherMap:", font=("Arial", 12)).pack(pady=10)
        
        entrada_api = tk.Entry(ventana_config, width=50, show="*")
        entrada_api.pack(pady=5)
        entrada_api.insert(0, self.api_key)
        
        def guardar_api():
            nueva_api = entrada_api.get().strip()
            if nueva_api:
                self.api_key = nueva_api
                try:
                    with open('.env', 'w') as f:
                        f.write(f'OPENWEATHER_API_KEY={nueva_api}\n')
                        f.write(f'DEFAULT_LOCATION={self.ubicacion_actual}\n')
                    messagebox.showinfo("Éxito", "API Key configurada correctamente")
                    ventana_config.destroy()
                    if self.barra_estado:
                        self.barra_estado.config(text="API del clima configurada")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")
            else:
                messagebox.showwarning("Advertencia", "Ingrese una API Key válida")
        
        tk.Button(ventana_config, text="Guardar", command=guardar_api, 
                 bg="green", fg="white", font=("Arial", 12)).pack(pady=10)
        
        tk.Label(ventana_config, text="Obtenga su API key gratuita en:\nopenweathermap.org", 
                font=("Arial", 10), fg="blue").pack(pady=5)
    
    def cambiar_ubicacion(self, root):
        """Permite cambiar la ubicación para consultas del clima"""
        ventana_ubicacion = tk.Toplevel(root)
        ventana_ubicacion.title("Cambiar Ubicación")
        ventana_ubicacion.geometry("300x150")
        ventana_ubicacion.grab_set()
        
        tk.Label(ventana_ubicacion, text="Nueva ubicación:", font=("Arial", 12)).pack(pady=10)
        
        entrada_ubicacion = tk.Entry(ventana_ubicacion, width=30)
        entrada_ubicacion.pack(pady=5)
        entrada_ubicacion.insert(0, self.ubicacion_actual)
        
        def guardar_ubicacion():
            nueva_ubicacion = entrada_ubicacion.get().strip()
            if nueva_ubicacion:
                self.ubicacion_actual = nueva_ubicacion
                if self.label_ubicacion:
                    self.label_ubicacion.config(text=f"Ubicación: {nueva_ubicacion}")
                messagebox.showinfo("Éxito", f"Ubicación cambiada a: {nueva_ubicacion}")
                ventana_ubicacion.destroy()
                if self.barra_estado:
                    self.barra_estado.config(text=f"Ubicación cambiada a: {nueva_ubicacion}")
            else:
                messagebox.showwarning("Advertencia", "Ingrese una ubicación válida")
        
        tk.Button(ventana_ubicacion, text="Cambiar", command=guardar_ubicacion,
                 bg="blue", fg="white", font=("Arial", 12)).pack(pady=10)
    
    def obtener_clima_actual(self):
        """Obtiene información del clima actual desde la API"""
        if not self.api_key:
            if self.barra_estado:
                self.barra_estado.config(text="Configure la API key primero")
            return None
        
        try:
            # Parámetros para la API
            params = {
                'q': self.ubicacion_actual,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'es'
            }
            
            # Realizar solicitud
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                clima_info = {
                    'temperatura': data['main']['temp'],
                    'humedad': data['main']['humidity'],
                    'descripcion': data['weather'][0]['description'],
                    'sensacion': data['main']['feels_like'],
                    'presion': data['main']['pressure'],
                    'viento': data['wind']['speed'] if 'wind' in data else 0,
                    'ubicacion': data['name'],
                    'pais': data['sys']['country']
                }
                
                return clima_info
                
            else:
                print(f"Error en API: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return None
        except Exception as e:
            print(f"Error procesando clima: {e}")
            return None
    
    def actualizar_interfaz_clima(self):
        """Actualiza la interfaz con información del clima actual"""
        try:
            clima = self.obtener_clima_actual()
            
            if clima and all([self.label_ubicacion, self.label_temperatura, 
                            self.label_humedad, self.label_clima_desc]):
                
                self.label_ubicacion.config(text=f"{clima['ubicacion']}, {clima['pais']}")
                self.label_temperatura.config(text=f"{clima['temperatura']:.1f}°C (Sensación: {clima['sensacion']:.1f}°C)")
                self.label_humedad.config(text=f"Humedad: {clima['humedad']}%")
                self.label_clima_desc.config(text=f"{clima['descripcion'].title()}")
                
                if self.barra_estado:
                    self.barra_estado.config(text=f"Clima actualizado: {clima['ubicacion']}")
                
                return clima
            
            else:
                if self.label_ubicacion:
                    self.label_ubicacion.config(text="Sin conexión")
                if self.label_temperatura:
                    self.label_temperatura.config(text="Temperatura: No disponible")
                if self.label_humedad:
                    self.label_humedad.config(text="Humedad: No disponible")
                if self.label_clima_desc:
                    self.label_clima_desc.config(text="Condiciones: Sin conexión")
                
                if self.barra_estado:
                    self.barra_estado.config(text="Error al obtener clima")
                
                return None
                
        except Exception as e:
            print(f"Error actualizando interfaz clima: {e}")
            if self.barra_estado:
                self.barra_estado.config(text=f"Error de clima: {str(e)}")
            return None
    
    def verificar_clima_cultivo(self, cultivo_actual, root):
        """Verifica si el clima actual es adecuado para el cultivo seleccionado"""
        if cultivo_actual is None or not self.api_key:
            messagebox.showwarning("Advertencia", "Seleccione un cultivo y configure la API")
            return
        
        ventana_clima = tk.Toplevel(root)
        ventana_clima.title(f"Análisis Climático - {cultivo_actual['cultivo']}")
        ventana_clima.geometry("600x500")
        
        texto_clima = scrolledtext.ScrolledText(ventana_clima, font=("Arial", 10))
        texto_clima.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Obtener clima actual
        clima = self.obtener_clima_actual()
        
        if clima:
            analisis = self._analizar_compatibilidad_clima(cultivo_actual, clima)
            texto_clima.insert(tk.END, analisis)
        else:
            texto_clima.insert(tk.END, "No se pudo obtener información del clima actual.\nVerifique su conexión a internet y la configuración de la API.")
    
    def _analizar_compatibilidad_clima(self, cultivo, clima):
        """Analiza la compatibilidad entre el clima actual y las necesidades del cultivo"""
        try:
            # Extraer temperatura ideal del cultivo
            temp_cultivo = cultivo['temperatura_ideal']
            lluvia_cultivo = cultivo['lluvia']
            
            analisis = f"""
ANÁLISIS CLIMÁTICO PARA {cultivo['cultivo'].upper()}
{'='*50}

CONDICIONES ACTUALES:
Ubicación: {clima['ubicacion']}, {clima['pais']}
Temperatura: {clima['temperatura']:.1f}°C
Humedad: {clima['humedad']}%
Condiciones: {clima['descripcion'].title()}
Viento: {clima.get('viento', 0):.1f} m/s
Presión: {clima.get('presion', 0)} hPa

REQUERIMIENTOS DEL CULTIVO:
Temperatura ideal: {temp_cultivo}
Nivel de lluvia: {lluvia_cultivo}
Tiempo de cosecha: {cultivo['tiempo_cosecha']}
Temporada óptima: {cultivo['temporada_siembra']}

ANÁLISIS DE COMPATIBILIDAD:
{'='*30}
            """
            
            # Análisis de temperatura
            temp_actual = clima['temperatura']
            
            # Evaluar temperatura (simplificado)
            if "25-30" in temp_cultivo or "cálido" in temp_cultivo.lower():
                if 25 <= temp_actual <= 35:
                    analisis += "TEMPERATURA: ÓPTIMA para el cultivo\n"
                elif 20 <= temp_actual <= 40:
                    analisis += "TEMPERATURA: ACEPTABLE para el cultivo\n"
                else:
                    analisis += "TEMPERATURA: NO IDEAL para el cultivo\n"
            elif "20-25" in temp_cultivo or "templado" in temp_cultivo.lower():
                if 18 <= temp_actual <= 28:
                    analisis += "TEMPERATURA: ÓPTIMA para el cultivo\n"
                else:
                    analisis += "TEMPERATURA: Podría no ser ideal\n"
            else:
                analisis += "TEMPERATURA: Requiere evaluación específica\n"
            
            # Análisis de humedad
            humedad_actual = clima['humedad']
            if lluvia_cultivo.lower() == "alta":
                if humedad_actual >= 70:
                    analisis += "HUMEDAD: ALTA - Favorable para cultivos que requieren mucha agua\n"
                else:
                    analisis += "HUMEDAD: MEDIA-BAJA - Considere riego adicional\n"
            elif lluvia_cultivo.lower() == "media":
                if 50 <= humedad_actual <= 80:
                    analisis += "HUMEDAD: MEDIA - Adecuada para el cultivo\n"
                else:
                    analisis += "HUMEDAD: Monitorear necesidades de riego\n"
            else:  # lluvia baja
                if humedad_actual <= 60:
                    analisis += "HUMEDAD: BAJA - Favorable para cultivos resistentes\n"
                else:
                    analisis += "HUMEDAD: ALTA - Podría favorecer enfermedades\n"
            
            # Recomendaciones
            analisis += f"""
RECOMENDACIONES ESPECÍFICAS:
{'='*35}
{cultivo['recomendaciones']}

FECHA DE ANÁLISIS: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

NOTA: Este análisis es orientativo. Consulte con expertos agrónomos
para decisiones de cultivo importantes.
            """
            
            return analisis
            
        except Exception as e:
            return f"Error al generar análisis climático: {str(e)}"
    
    def consultar_clima_ciudad(self, root):
        """Permite consultar el clima de una ciudad específica"""
        ventana_consulta = tk.Toplevel(root)
        ventana_consulta.title("Consultar Clima por Ciudad")
        ventana_consulta.geometry("400x300")
        
        tk.Label(ventana_consulta, text="Ingrese el nombre de la ciudad:", 
                font=("Arial", 12)).pack(pady=10)
        
        entrada_ciudad = tk.Entry(ventana_consulta, width=30)
        entrada_ciudad.pack(pady=5)
        
        resultado_texto = tk.Text(ventana_consulta, height=12, width=50)
        resultado_texto.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        def consultar():
            ciudad = entrada_ciudad.get().strip()
            if not ciudad:
                messagebox.showwarning("Advertencia", "Ingrese el nombre de una ciudad")
                return
            
            # Temporalmente cambiar ubicación
            ubicacion_original = self.ubicacion_actual
            self.ubicacion_actual = ciudad
            
            clima = self.obtener_clima_actual()
            
            # Restaurar ubicación original
            self.ubicacion_actual = ubicacion_original
            
            resultado_texto.delete(1.0, tk.END)
            
            if clima:
                info_clima = f"""
INFORMACIÓN CLIMÁTICA DE {ciudad.upper()}
{'='*40}

Ubicación: {clima['ubicacion']}, {clima['pais']}
Temperatura: {clima['temperatura']:.1f}°C
Sensación térmica: {clima['sensacion']:.1f}°C
Humedad: {clima['humedad']}%
Condiciones: {clima['descripcion'].title()}
Velocidad del viento: {clima.get('viento', 0):.1f} m/s
Presión atmosférica: {clima.get('presion', 0)} hPa

Consulta realizada: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
                """
                resultado_texto.insert(tk.END, info_clima)
                
                if self.barra_estado:
                    self.barra_estado.config(text=f"Clima consultado: {clima['ubicacion']}")
            else:
                resultado_texto.insert(tk.END, f"No se pudo obtener información del clima para: {ciudad}\n\nVerifique:\n- Conexión a internet\n- Nombre correcto de la ciudad\n- Configuración de la API key")
        
        tk.Button(ventana_consulta, text="Consultar", command=consultar,
                 bg="blue", fg="white", font=("Arial", 11)).pack(pady=5)