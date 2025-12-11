"""
Servicio de análisis de CSV
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import io
from app.utils import (
    detect_column_type,
    get_sample_values,
    calculate_basic_stats,
    prepare_data_for_visualization,
    clean_currency_value,
    clean_percentage_value,
    safe_get_value
)
from app.models import ColumnInfo, CSVMetadata


class CSVAnalyzer:
    """Clase para analizar archivos CSV"""
    
    def __init__(self):
        self.df = None
        self.metadata = None
        self.column_info = []
    
    def load_csv(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Carga un archivo CSV desde bytes
        """
        try:
            # Intentar con diferentes encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    self.df = pd.read_csv(
                        io.BytesIO(file_content),
                        encoding=encoding,
                        low_memory=False
                    )
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise ValueError("No se pudo decodificar el archivo CSV")
            
            # Crear metadata
            self.metadata = CSVMetadata(
                filename=filename,
                size=len(file_content),
                rows=len(self.df),
                columns=len(self.df.columns),
                column_names=self.df.columns.tolist()
            )
            
            return self.df
            
        except Exception as e:
            raise ValueError(f"Error al cargar CSV: {str(e)}")
    
    def analyze_columns(self) -> List[ColumnInfo]:
        """
        Analiza cada columna del DataFrame
        """
        if self.df is None:
            raise ValueError("No hay DataFrame cargado")
        
        self.column_info = []
        
        for col in self.df.columns:
            series = self.df[col]
            
            col_info = ColumnInfo(
                name=col,
                dtype=str(series.dtype),
                sample_values=get_sample_values(series, n=5),
                null_count=int(series.isna().sum()),
                unique_count=int(series.nunique()),
                detected_type=detect_column_type(series)
            )
            
            self.column_info.append(col_info)
        
        return self.column_info
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas resumidas del CSV
        """
        if self.df is None:
            raise ValueError("No hay DataFrame cargado")
        
        stats = calculate_basic_stats(self.df)
        
        # Agregar estadísticas descriptivas para columnas numéricas
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            desc_stats = self.df[numeric_cols].describe()
            stats["numeric_statistics"] = {
                col: {
                    "mean": safe_get_value(desc_stats[col]["mean"]),
                    "median": safe_get_value(self.df[col].median()),
                    "std": safe_get_value(desc_stats[col]["std"]),
                    "min": safe_get_value(desc_stats[col]["min"]),
                    "max": safe_get_value(desc_stats[col]["max"]),
                }
                for col in numeric_cols
            }
        
        return stats
    
    def generate_visualizations(self) -> List[Dict[str, Any]]:
        """
        Genera configuraciones de visualización basadas en los datos
        """
        if self.df is None:
            raise ValueError("No hay DataFrame cargado")
        
        visualizations = []
        
        # Encontrar columnas categóricas para gráficos de barras
        categorical_cols = [
            col_info.name for col_info in self.column_info
            if col_info.detected_type in ["categorical", "categorical_numeric"]
            and col_info.unique_count < 20
        ]
        
        for col in categorical_cols[:3]:  # Limitar a 3 gráficos
            viz = prepare_data_for_visualization(self.df, col, "bar")
            viz["title"] = f"Distribución de {col}"
            visualizations.append(viz)
        
        # Encontrar columnas numéricas para histogramas o líneas
        numeric_cols = [
            col_info.name for col_info in self.column_info
            if col_info.detected_type in ["integer", "float", "currency"]
        ]
        
        for col in numeric_cols[:2]:  # Limitar a 2 gráficos
            # Crear histograma de frecuencias
            series = self.df[col].dropna()
            if len(series) > 0:
                hist, bins = np.histogram(series, bins=10)
                viz = {
                    "column": col,
                    "type": "bar",
                    "title": f"Distribución de {col}",
                    "data": {
                        "labels": [f"{safe_get_value(bins[i]):.2f}-{safe_get_value(bins[i+1]):.2f}" 
                                 for i in range(len(bins)-1)],
                        "values": [int(x) for x in hist.tolist()]
                    }
                }
                visualizations.append(viz)
        
        return visualizations
    
    def get_data_preview(self, n_rows: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene una vista previa de los datos
        """
        if self.df is None:
            raise ValueError("No hay DataFrame cargado")
        
        preview = self.df.head(n_rows).to_dict(orient='records')
        
        # Convertir valores para serialización JSON
        cleaned_preview = []
        for row in preview:
            cleaned_row = {k: safe_get_value(v) for k, v in row.items()}
            cleaned_preview.append(cleaned_row)
        
        return cleaned_preview
    
    def prepare_for_ai_analysis(self) -> str:
        """
        Prepara un resumen del CSV para análisis con IA
        """
        if self.df is None:
            raise ValueError("No hay DataFrame cargado")
        
        summary = f"""
        Archivo CSV: {self.metadata.filename}
        Total de filas: {self.metadata.rows}
        Total de columnas: {self.metadata.columns}
        
        Columnas y sus características:
        """
        
        for col_info in self.column_info:
            summary += f"""
        - {col_info.name}:
          * Tipo: {col_info.dtype}
          * Tipo detectado: {col_info.detected_type}
          * Valores únicos: {col_info.unique_count}
          * Valores nulos: {col_info.null_count}
          * Ejemplos: {col_info.sample_values[:3]}
            """
        
        # Agregar vista previa de datos
        summary += "\n\nVista previa de los primeros 5 registros:\n"
        preview = self.get_data_preview(n_rows=5)
        for i, row in enumerate(preview, 1):
            summary += f"\nRegistro {i}: {row}"
        
        return summary
