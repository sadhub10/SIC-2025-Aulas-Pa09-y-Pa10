import pandas as pd
from typing import List, Dict
import re
from difflib import get_close_matches
from pathlib import Path


class BuscadorRutas: #Busca rutas por origen y destino usando búsqueda inteligente.
    
    def __init__(self, ruta_resumen: str):
        ruta_resumen = Path(ruta_resumen).resolve()
        if not ruta_resumen.exists():
            raise FileNotFoundError(
                f"⚠️ No se encontró el archivo {ruta_resumen}\n"
                f"   → Ejecuta primero 'analyze_dataset.py' para generarlo."
            )
        
        self.df_rutas = pd.read_csv(ruta_resumen)
        
        # Verificar columnas mínimas
        columnas_requeridas = ['id_ruta', 'nombre_ruta', 'intervalo_promedio']
        for col in columnas_requeridas:
            if col not in self.df_rutas.columns:
                self.df_rutas[col] = None
        
        self.ubicaciones = self._extraer_ubicaciones()
    
    # ---------------------------------------------------------------
    # 📍 Extracción y búsqueda de ubicaciones
    # ---------------------------------------------------------------
    def _extraer_ubicaciones(self) -> List[str]: #Extrae ubicaciones únicas de los nombres de rutas.
        ubicaciones = set()
        for nombre in self.df_rutas['nombre_ruta'].dropna():
            partes = nombre.split('-')
            for parte in partes:
                parte_limpia = re.sub(r'^(Vía |Estación |Terminal )', '', parte.strip())
                if parte_limpia and len(parte_limpia) > 2:
                    ubicaciones.add(parte_limpia)
        return sorted(ubicaciones)
    
    def obtener_ubicaciones_populares(self, top_n: int = 20) -> List[str]: #Obtiene las ubicaciones más comunes en los nombres de rutas.
        contador = {}
        for nombre in self.df_rutas['nombre_ruta'].dropna():
            for ubicacion in self.ubicaciones:
                if ubicacion in nombre:
                    contador[ubicacion] = contador.get(ubicacion, 0) + 1
        ubicaciones_ordenadas = sorted(contador.items(), key=lambda x: x[1], reverse=True)
        return [ub for ub, _ in ubicaciones_ordenadas[:top_n]]
    
    def buscar_ubicacion(self, texto: str, max_sugerencias: int = 5) -> List[str]: #Busca ubicaciones similares al texto dado.
        texto_lower = texto.lower().strip()
        coincidencias_exactas = [ub for ub in self.ubicaciones if texto_lower in ub.lower()]
        if coincidencias_exactas:
            return coincidencias_exactas[:max_sugerencias]
        return get_close_matches(texto, self.ubicaciones, n=max_sugerencias, cutoff=0.6)
    
    # ---------------------------------------------------------------
    # 🚌 Búsqueda de rutas
    # ---------------------------------------------------------------
    def buscar_rutas(self, origen: str, destino: str) -> pd.DataFrame: #Busca rutas que conecten origen con destino.
        origen_norm, destino_norm = origen.strip(), destino.strip()
        rutas_encontradas = self.df_rutas[
            self.df_rutas['nombre_ruta'].str.contains(origen_norm, case=False, na=False, regex=False) &
            self.df_rutas['nombre_ruta'].str.contains(destino_norm, case=False, na=False, regex=False)
        ].copy()
        
        if rutas_encontradas.empty:
            return pd.DataFrame()
        
        rutas_encontradas['direccion_correcta'] = rutas_encontradas['nombre_ruta'].apply(
            lambda x: self._verificar_direccion(x, origen_norm, destino_norm)
        )
        rutas_encontradas['via'] = rutas_encontradas['nombre_ruta'].apply(self._extraer_via)
        return rutas_encontradas.sort_values('intervalo_promedio')
    
    def buscar_por_id(self, id_ruta: str) -> pd.Series: #Busca una ruta específica por su ID.
        ruta = self.df_rutas[self.df_rutas['id_ruta'] == id_ruta]
        return ruta.iloc[0] if len(ruta) else None
    
    def buscar_por_nombre(self, texto: str, max_resultados: int = 10) -> pd.DataFrame: #Busca rutas que contengan el texto dado en su nombre.
        texto_lower = texto.lower().strip()
        rutas = self.df_rutas[
            self.df_rutas['nombre_ruta'].str.contains(texto_lower, case=False, na=False, regex=False)
        ].copy()
        return rutas.sort_values('intervalo_promedio').head(max_resultados)
    
    # ---------------------------------------------------------------
    # 🔍 Utilidades internas
    # ---------------------------------------------------------------
    def _verificar_direccion(self, nombre_ruta: str, origen: str, destino: str) -> bool: #Verifica si la ruta va de origen → destino.
        idx_origen = nombre_ruta.lower().find(origen.lower())
        idx_destino = nombre_ruta.lower().find(destino.lower())
        return idx_origen < idx_destino

    def _extraer_via(self, nombre_ruta: str) -> str: #Identifica la vía o ruta intermedia.
        if 'Directo' in nombre_ruta:
            return 'Directo'
        elif 'Vía España' in nombre_ruta or 'VE' in nombre_ruta:
            return 'Vía España'
        elif 'Transístmica' in nombre_ruta:
            return 'Transístmica'
        elif 'Tumba Muerto' in nombre_ruta:
            return 'Tumba Muerto'
        elif 'Corredor' in nombre_ruta:
            return 'Corredor'
        return 'Ruta regular'

    def formatear_resultado(self, ruta: pd.Series, numero: int, tiempo_actual: int = None) -> str: #Formatea una ruta para mostrar al usuario.
        nombre = ruta['nombre_ruta']
        via = ruta.get('via', 'Ruta regular')
        intervalo = ruta['intervalo_promedio']
        
        resultado = f"[{numero}] {nombre}\n"
        resultado += f"    Via: {via}\n"
        resultado += f"    Intervalo promedio: {intervalo:.1f} minutos\n"
        if tiempo_actual is not None:
            resultado += f"    Próximo bus: ~{intervalo:.0f} minutos\n"
        if not ruta.get('direccion_correcta', True):
            resultado += "    ⚠️  NOTA: Esta ruta va en dirección opuesta\n"
        return resultado
