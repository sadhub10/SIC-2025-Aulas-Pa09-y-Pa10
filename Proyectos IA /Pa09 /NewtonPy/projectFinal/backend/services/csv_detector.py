import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re

class CSVDetector:
    """
    Detecta automáticamente el tipo de CSV analizando:
    - Nombres de columnas
    - Tipos de datos
    - Patrones en los valores
    - Estructura del contenido
    """
    
    def __init__(self):
        # Palabras clave por categoría
        self.keywords = {
            'financial': {
                'columns': ['amount', 'price', 'cost', 'expense', 'revenue', 'income', 'payment', 
                           'invoice', 'transaction', 'balance', 'profit', 'loss', 'budget',
                           'gasto', 'ingreso', 'factura', 'pago', 'precio', 'costo', 'monto'],
                'patterns': ['currency', 'account', 'financial']
            },
            'sales': {
                'columns': ['sales', 'sold', 'customer', 'order', 'product', 'quantity', 'units',
                           'ventas', 'vendido', 'cliente', 'pedido', 'producto', 'cantidad'],
                'patterns': ['sale', 'purchase', 'buyer']
            },
            'hr': {
                'columns': ['employee', 'salary', 'department', 'position', 'hire', 'attendance',
                           'empleado', 'salario', 'departamento', 'puesto', 'asistencia', 'nombre',
                           'apellido', 'edad', 'contrato', 'antiguedad'],
                'patterns': ['staff', 'personnel', 'workforce']
            },
            'inventory': {
                'columns': ['stock', 'inventory', 'warehouse', 'supplier', 'quantity', 'sku',
                           'inventario', 'almacen', 'proveedor', 'existencia'],
                'patterns': ['storage', 'items', 'products']
            },
            'operations': {
                'columns': ['operation', 'process', 'maintenance', 'logistics', 'project',
                           'operacion', 'proceso', 'mantenimiento', 'logistica', 'proyecto'],
                'patterns': ['workflow', 'procedure']
            },
            'performance': {
                'columns': ['performance', 'metrics', 'kpi', 'efficiency', 'productivity',
                           'efectividad', 'rendimiento', 'desempeño', 'calidad'],
                'patterns': ['rating', 'score', 'evaluation']
            }
        }
    
    def detect_csv_type(self, filepath: str) -> Dict[str, Any]:
        """
        Detecta el tipo de CSV y extrae información relevante
        """
        try:
            # Leer CSV con diferentes encodings
            df = self._read_csv_safely(filepath)
            
            # Información básica
            basic_info = self._extract_basic_info(df)
            
            # Detectar categoría
            category_scores = self._score_categories(df)
            main_category = max(category_scores, key=category_scores.get)
            
            # Detectar columnas importantes
            key_columns = self._identify_key_columns(df, main_category)
            
            # Analizar tipos de datos
            data_types = self._analyze_data_types(df)
            
            # Detectar patrones temporales
            temporal_info = self._detect_temporal_patterns(df)
            
            result = {
                'category': main_category,
                'confidence': category_scores[main_category],
                'all_scores': category_scores,
                'basic_info': basic_info,
                'key_columns': key_columns,
                'data_types': data_types,
                'temporal_info': temporal_info,
                'suggestions': self._generate_suggestions(main_category, df)
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'category': 'unknown',
                'confidence': 0
            }
    
    def _read_csv_safely(self, filepath: str) -> pd.DataFrame:
        """Lee CSV probando diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                return df
            except:
                continue
        
        # Si ninguno funciona, intenta sin especificar encoding
        return pd.read_csv(filepath)
    
    def _extract_basic_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extrae información básica del DataFrame"""
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': df.columns.tolist(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'has_nulls': df.isnull().any().any(),
            'null_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
    
    def _score_categories(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula scores para cada categoría basado en palabras clave"""
        scores = {category: 0.0 for category in self.keywords.keys()}
        
        # Normalizar nombres de columnas
        columns_lower = [col.lower() for col in df.columns]
        columns_text = ' '.join(columns_lower)
        
        for category, keywords in self.keywords.items():
            score = 0
            
            # Buscar palabras clave en nombres de columnas
            for keyword in keywords['columns']:
                for col in columns_lower:
                    if keyword in col:
                        score += 2
            
            # Buscar patrones
            for pattern in keywords['patterns']:
                if pattern in columns_text:
                    score += 1
            
            # Analizar contenido de primeras filas
            sample_text = ' '.join(df.head(10).astype(str).values.flatten()).lower()
            for keyword in keywords['columns']:
                if keyword in sample_text:
                    score += 0.5
            
            scores[category] = score
        
        # Normalizar scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    def _identify_key_columns(self, df: pd.DataFrame, category: str) -> List[str]:
        """Identifica las columnas más importantes según la categoría"""
        key_cols = []
        columns_lower = {col: col.lower() for col in df.columns}
        
        # Palabras clave relevantes según categoría
        relevant_keywords = self.keywords.get(category, {}).get('columns', [])
        
        for col, col_lower in columns_lower.items():
            for keyword in relevant_keywords:
                if keyword in col_lower:
                    key_cols.append(col)
                    break
        
        # Si no encontramos columnas clave, usar las primeras columnas numéricas
        if not key_cols:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            key_cols = numeric_cols[:5]
        
        return key_cols
    
    def _analyze_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza los tipos de datos en el DataFrame"""
        type_info = {
            'numeric': [],
            'text': [],
            'date': [],
            'categorical': [],
            'boolean': []
        }
        
        for col in df.columns:
            dtype = df[col].dtype
            unique_ratio = df[col].nunique() / len(df) if len(df) > 0 else 0
            
            if pd.api.types.is_numeric_dtype(dtype):
                type_info['numeric'].append({
                    'name': col,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None
                })
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                type_info['date'].append(col)
            elif unique_ratio < 0.05 and df[col].nunique() < 50:
                type_info['categorical'].append({
                    'name': col,
                    'categories': df[col].unique().tolist()[:10]
                })
            elif df[col].nunique() == 2:
                type_info['boolean'].append(col)
            else:
                type_info['text'].append(col)
        
        return type_info
    
    def _detect_temporal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detecta patrones temporales en los datos"""
        temporal = {
            'has_dates': False,
            'date_columns': [],
            'date_range': None,
            'frequency': None
        }
        
        # Buscar columnas de fecha
        date_keywords = ['date', 'time', 'timestamp', 'fecha', 'hora', 'dia', 'mes', 'año', 'year', 'month', 'day']
        
        for col in df.columns:
            col_lower = col.lower()
            
            # Verificar si el nombre sugiere una fecha
            if any(keyword in col_lower for keyword in date_keywords):
                try:
                    # Intentar convertir a fecha
                    dates = pd.to_datetime(df[col], errors='coerce')
                    if dates.notna().sum() > len(df) * 0.5:  # Al menos 50% son fechas válidas
                        temporal['has_dates'] = True
                        temporal['date_columns'].append(col)
                        
                        if temporal['date_range'] is None:
                            temporal['date_range'] = {
                                'start': dates.min().strftime('%Y-%m-%d') if pd.notna(dates.min()) else None,
                                'end': dates.max().strftime('%Y-%m-%d') if pd.notna(dates.max()) else None
                            }
                except:
                    continue
        
        return temporal
    
    def _generate_suggestions(self, category: str, df: pd.DataFrame) -> List[str]:
        """Genera sugerencias de análisis según la categoría"""
        suggestions = []
        
        if category == 'financial':
            suggestions = [
                'Analizar tendencias de gastos por categoría',
                'Identificar gastos atípicos o anomalías',
                'Calcular totales por departamento o proyecto',
                'Comparar gastos entre períodos'
            ]
        elif category == 'sales':
            suggestions = [
                'Analizar ventas por vendedor o producto',
                'Identificar tendencias de ventas',
                'Calcular métricas de rendimiento',
                'Comparar períodos de ventas'
            ]
        elif category == 'hr':
            suggestions = [
                'Analizar distribución de salarios',
                'Evaluar asistencia y productividad',
                'Comparar rendimiento entre empleados',
                'Identificar empleados de alto/bajo rendimiento'
            ]
        elif category == 'performance':
            suggestions = [
                'Calcular métricas de efectividad',
                'Identificar patrones de rendimiento',
                'Comparar resultados entre períodos',
                'Analizar factores que afectan el rendimiento'
            ]
        else:
            suggestions = [
                'Explorar distribuciones de datos',
                'Identificar correlaciones entre variables',
                'Detectar valores atípicos',
                'Analizar tendencias temporales'
            ]
        
        return suggestions
