"""
Utilidades compartidas
"""
import pandas as pd
import numpy as np
from typing import Any, List, Dict
import re


def detect_column_type(series: pd.Series) -> str:
    """
    Detecta el tipo de dato de una columna
    """
    # Eliminar valores nulos para el análisis
    series_clean = series.dropna()
    
    if len(series_clean) == 0:
        return "empty"
    
    # Convertir a string para análisis
    series_str = series_clean.astype(str)
    
    # Detectar moneda (ej: $1,000.00)
    currency_pattern = r'^\$?[\d,]+\.?\d*$|^\$[\d,]+$'
    if series_str.str.match(currency_pattern).sum() / len(series_str) > 0.7:
        return "currency"
    
    # Detectar porcentaje
    percentage_pattern = r'^\d+\.?\d*%$'
    if series_str.str.match(percentage_pattern).sum() / len(series_str) > 0.7:
        return "percentage"
    
    # Detectar fecha
    try:
        pd.to_datetime(series_clean)
        return "date"
    except:
        pass
    
    # Detectar numérico
    if pd.api.types.is_numeric_dtype(series):
        # Verificar si son enteros o flotantes
        if pd.api.types.is_integer_dtype(series):
            # Si hay pocos valores únicos, podría ser categórico
            if series.nunique() < 20:
                return "categorical_numeric"
            return "integer"
        return "float"
    
    # Detectar email
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if series_str.str.match(email_pattern).sum() / len(series_str) > 0.7:
        return "email"
    
    # Detectar teléfono
    phone_pattern = r'^\+?[\d\s\-()]+$'
    if series_str.str.match(phone_pattern).sum() / len(series_str) > 0.7:
        return "phone"
    
    # Detectar ID (patrones como INV-2025-001, PROJ-123, etc)
    id_pattern = r'^[A-Z]+-[\d-]+$'
    if series_str.str.match(id_pattern).sum() / len(series_str) > 0.7:
        return "id"
    
    # Si tiene pocos valores únicos, es categórico
    unique_ratio = series.nunique() / len(series)
    if unique_ratio < 0.3:
        return "categorical"
    
    # Por defecto, es texto
    return "text"


def clean_currency_value(value: str) -> float:
    """Limpia valores de moneda y los convierte a float"""
    if pd.isna(value):
        return np.nan
    
    value_str = str(value)
    # Remover símbolos de moneda y comas
    cleaned = re.sub(r'[^\d.-]', '', value_str)
    try:
        return float(cleaned)
    except:
        return np.nan


def clean_percentage_value(value: str) -> float:
    """Limpia valores de porcentaje y los convierte a float"""
    if pd.isna(value):
        return np.nan
    
    value_str = str(value)
    # Remover el símbolo de porcentaje
    cleaned = value_str.replace('%', '').strip()
    try:
        return float(cleaned)
    except:
        return np.nan


def safe_get_value(value: Any) -> Any:
    """Convierte valores de pandas/numpy a tipos serializables en JSON"""
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, (np.bool_)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def get_sample_values(series: pd.Series, n: int = 5) -> List[Any]:
    """Obtiene valores de muestra de una serie"""
    series_clean = series.dropna()
    if len(series_clean) == 0:
        return []
    
    # Obtener valores únicos si hay pocos
    if series_clean.nunique() <= n:
        samples = series_clean.unique().tolist()
    else:
        samples = series_clean.sample(min(n, len(series_clean))).tolist()
    
    return [safe_get_value(v) for v in samples]


def calculate_basic_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Calcula estadísticas básicas del dataframe"""
    stats = {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "missing_values": int(df.isna().sum().sum()),
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / 1024 / 1024),
        "numeric_columns": int(df.select_dtypes(include=[np.number]).shape[1]),
        "text_columns": int(df.select_dtypes(include=['object']).shape[1]),
    }
    
    return stats


def prepare_data_for_visualization(df: pd.DataFrame, column: str, 
                                   chart_type: str = "bar") -> Dict[str, Any]:
    """
    Prepara datos para visualización
    """
    result = {
        "column": column,
        "type": chart_type,
        "data": {}
    }
    
    if column not in df.columns:
        return result
    
    series = df[column].dropna()
    
    if chart_type == "bar":
        # Para gráficos de barras, agrupar y contar
        value_counts = series.value_counts().head(10)
        result["data"] = {
            "labels": [str(x) for x in value_counts.index.tolist()],
            "values": [safe_get_value(x) for x in value_counts.values.tolist()]
        }
    
    elif chart_type == "line":
        # Para líneas de tiempo
        result["data"] = {
            "labels": [str(i) for i in range(len(series))],
            "values": [safe_get_value(x) for x in series.tolist()]
        }
    
    elif chart_type == "pie":
        # Para gráficos de pastel
        value_counts = series.value_counts().head(5)
        result["data"] = {
            "labels": [str(x) for x in value_counts.index.tolist()],
            "values": [safe_get_value(x) for x in value_counts.values.tolist()]
        }
    
    return result
