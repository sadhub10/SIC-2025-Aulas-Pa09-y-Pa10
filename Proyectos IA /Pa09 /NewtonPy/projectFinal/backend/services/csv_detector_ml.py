import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
from .neural_classifier import CSVNeuralClassifier
from .data_cleaner import DataCleaner

class CSVDetectorML:
    """
    Detector de tipo de CSV usando Red Neuronal propia
    NO usa Anthropic - solo librerías Python estándar
    """
    
    def __init__(self):
        # Inicializar red neuronal
        self.neural_classifier = CSVNeuralClassifier()
        
        # Inicializar limpiador de datos
        self.data_cleaner = DataCleaner()
        
        # Si no hay modelo entrenado, entrenar uno
        if not self.neural_classifier.is_trained:
            print("No se encontró modelo pre-entrenado. Entrenando nuevo modelo...")
            self.neural_classifier.train_with_synthetic_data(n_samples=1000)
        
        # Palabras clave por categoría (backup si la red falla)
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
        Detecta el tipo de CSV usando la red neuronal y limpia los datos
        """
        try:
            # 1. Leer CSV
            df = self._read_csv_safely(filepath)
            
            # 2. Información básica ANTES de limpiar
            basic_info_raw = self._extract_basic_info(df)
            
            # 3. Calcular score de calidad ANTES de limpiar
            quality_before = self.data_cleaner.get_quality_score(df)
            
            # 4. LIMPIAR DATOS con ML
            df_clean, cleaning_report = self.data_cleaner.clean_dataframe(df, auto_mode=True)
            
            # 5. Calcular score de calidad DESPUÉS de limpiar
            quality_after = self.data_cleaner.get_quality_score(df_clean)
            
            # 6. Información básica DESPUÉS de limpiar
            basic_info_clean = self._extract_basic_info(df_clean)
            
            # 7. Usar RED NEURONAL para clasificar
            nn_prediction = self.neural_classifier.predict(df_clean)
            
            # 8. Backup: método tradicional por si la red falla
            fallback_scores = self._score_categories(df_clean)
            
            # 9. Decidir categoría final
            if nn_prediction['confidence'] > 0.5:
                main_category = nn_prediction['category']
                confidence = nn_prediction['confidence']
                method = 'neural_network'
            else:
                main_category = max(fallback_scores, key=fallback_scores.get)
                confidence = fallback_scores[main_category]
                method = 'keyword_based'
            
            # 10. Detectar columnas importantes
            key_columns = self._identify_key_columns(df_clean, main_category)
            
            # 11. Analizar tipos de datos
            data_types = self._analyze_data_types(df_clean)
            
            # 12. Detectar patrones temporales
            temporal_info = self._detect_temporal_patterns(df_clean)
            
            result = {
                'category': main_category,
                'confidence': confidence,
                'method': method,
                'all_scores': nn_prediction.get('all_probabilities', fallback_scores),
                'basic_info': {
                    'raw': basic_info_raw,
                    'clean': basic_info_clean
                },
                'data_quality': {
                    'before_cleaning': quality_before,
                    'after_cleaning': quality_after,
                    'improvement': round(quality_after['overall_score'] - quality_before['overall_score'], 2)
                },
                'cleaning_report': cleaning_report,
                'key_columns': key_columns,
                'data_types': data_types,
                'temporal_info': temporal_info,
                'suggestions': self._generate_suggestions(main_category, df_clean),
                'cleaned_data_preview': df_clean.head(10).to_dict('records')
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'category': 'unknown',
                'confidence': 0,
                'method': 'error'
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
            'memory_usage': int(df.memory_usage(deep=True).sum()),
            'has_nulls': bool(df.isnull().any().any()),
            'null_percentage': round((df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2)
        }
    
    def _score_categories(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Método tradicional basado en palabras clave (backup)
        """
        scores = {category: 0.0 for category in self.keywords.keys()}
        
        columns_lower = [col.lower() for col in df.columns]
        columns_text = ' '.join(columns_lower)
        
        for category, keywords in self.keywords.items():
            score = 0
            
            for keyword in keywords['columns']:
                for col in columns_lower:
                    if keyword in col:
                        score += 2
            
            for pattern in keywords['patterns']:
                if pattern in columns_text:
                    score += 1
            
            sample_text = ' '.join(df.head(10).astype(str).values.flatten()).lower()
            for keyword in keywords['columns']:
                if keyword in sample_text:
                    score += 0.5
            
            scores[category] = score
        
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
        
        return scores
    
    def _identify_key_columns(self, df: pd.DataFrame, category: str) -> List[str]:
        """Identifica las columnas más importantes según la categoría"""
        key_cols = []
        columns_lower = {col: col.lower() for col in df.columns}
        
        relevant_keywords = self.keywords.get(category, {}).get('columns', [])
        
        for col, col_lower in columns_lower.items():
            for keyword in relevant_keywords:
                if keyword in col_lower:
                    key_cols.append(col)
                    break
        
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
        
        date_keywords = ['date', 'time', 'timestamp', 'fecha', 'hora', 'dia', 'mes', 'año', 'year', 'month', 'day']
        
        for col in df.columns:
            col_lower = col.lower()
            
            if any(keyword in col_lower for keyword in date_keywords):
                try:
                    dates = pd.to_datetime(df[col], errors='coerce')
                    if dates.notna().sum() > len(df) * 0.5:
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
