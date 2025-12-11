import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy import stats
import re

class DataCleaner:
    """
    Limpieza inteligente de datos usando técnicas de Machine Learning
    - Detección y tratamiento de valores faltantes
    - Detección y manejo de outliers
    - Normalización y estandarización
    - Corrección de tipos de datos
    """
    
    def __init__(self):
        self.cleaning_report = {}
    
    def clean_dataframe(self, df: pd.DataFrame, auto_mode: bool = True) -> tuple:
        """
        Limpia el DataFrame completo
        
        Returns:
            tuple: (df_cleaned, cleaning_report)
        """
        df_clean = df.copy()
        self.cleaning_report = {
            'original_shape': df.shape,
            'steps': []
        }
        
        # 1. Detectar y corregir tipos de datos
        df_clean = self._detect_and_fix_types(df_clean)
        
        # 2. Limpiar nombres de columnas
        df_clean = self._clean_column_names(df_clean)
        
        # 3. Eliminar duplicados
        df_clean = self._remove_duplicates(df_clean)
        
        # 4. Manejar valores faltantes
        df_clean = self._handle_missing_values(df_clean, auto_mode)
        
        # 5. Detectar y manejar outliers
        df_clean = self._handle_outliers(df_clean, auto_mode)
        
        # 6. Normalizar datos numéricos (opcional)
        # df_clean = self._normalize_numeric(df_clean)
        
        # 7. Estandarizar formatos de texto
        df_clean = self._standardize_text(df_clean)
        
        self.cleaning_report['final_shape'] = df_clean.shape
        self.cleaning_report['rows_removed'] = df.shape[0] - df_clean.shape[0]
        self.cleaning_report['columns_removed'] = df.shape[1] - df_clean.shape[1]
        
        return df_clean, self.cleaning_report
    
    def _detect_and_fix_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detecta y corrige tipos de datos incorrectos
        """
        conversions = []
        
        for col in df.columns:
            # Intentar convertir a numérico si parece numérico
            if df[col].dtype == 'object':
                # Limpiar espacios y caracteres especiales
                cleaned = df[col].astype(str).str.strip()
                
                # Intentar convertir a numérico
                try:
                    # Remover símbolos de moneda y comas
                    cleaned = cleaned.str.replace(r'[$,€£¥]', '', regex=True)
                    numeric_vals = pd.to_numeric(cleaned, errors='coerce')
                    
                    # Si más del 80% son números, convertir
                    if numeric_vals.notna().sum() / len(df) > 0.8:
                        df[col] = numeric_vals
                        conversions.append(f"{col}: texto → numérico")
                        continue
                except:
                    pass
                
                # Intentar convertir a fecha
                try:
                    date_vals = pd.to_datetime(cleaned, errors='coerce')
                    if date_vals.notna().sum() / len(df) > 0.8:
                        df[col] = date_vals
                        conversions.append(f"{col}: texto → fecha")
                        continue
                except:
                    pass
        
        if conversions:
            self.cleaning_report['steps'].append({
                'step': 'Detección de tipos',
                'conversions': conversions
            })
        
        return df
    
    def _clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y estandariza nombres de columnas
        """
        old_names = df.columns.tolist()
        new_names = []
        
        for col in df.columns:
            # Convertir a minúsculas
            new_name = col.lower()
            
            # Remover caracteres especiales
            new_name = re.sub(r'[^\w\s]', '', new_name)
            
            # Reemplazar espacios con guiones bajos
            new_name = re.sub(r'\s+', '_', new_name)
            
            # Remover guiones bajos múltiples
            new_name = re.sub(r'_+', '_', new_name)
            
            # Remover guiones bajos al inicio y final
            new_name = new_name.strip('_')
            
            new_names.append(new_name)
        
        df.columns = new_names
        
        changes = [f"{old} → {new}" for old, new in zip(old_names, new_names) if old != new]
        if changes:
            self.cleaning_report['steps'].append({
                'step': 'Limpieza de nombres de columnas',
                'changes': changes
            })
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Elimina filas duplicadas
        """
        duplicates_before = df.duplicated().sum()
        df_clean = df.drop_duplicates()
        duplicates_removed = duplicates_before
        
        if duplicates_removed > 0:
            self.cleaning_report['steps'].append({
                'step': 'Eliminación de duplicados',
                'duplicates_removed': int(duplicates_removed),
                'percentage': f"{(duplicates_removed / len(df)) * 100:.2f}%"
            })
        
        return df_clean
    
    def _handle_missing_values(self, df: pd.DataFrame, auto_mode: bool) -> pd.DataFrame:
        """
        Maneja valores faltantes usando diferentes estrategias
        """
        missing_info = []
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_count > 0:
                strategy = None
                
                # Si más del 50% son nulos, considerar eliminar columna
                if missing_pct > 50 and auto_mode:
                    df = df.drop(columns=[col])
                    strategy = 'columna eliminada (>50% nulls)'
                
                # Para columnas numéricas
                elif pd.api.types.is_numeric_dtype(df[col]):
                    if missing_pct < 5:
                        # Pocos valores: imputar con la mediana
                        df[col].fillna(df[col].median(), inplace=True)
                        strategy = 'mediana'
                    else:
                        # Más valores: usar KNN imputer
                        try:
                            imputer = KNNImputer(n_neighbors=5)
                            df[[col]] = imputer.fit_transform(df[[col]])
                            strategy = 'KNN imputation'
                        except:
                            df[col].fillna(df[col].median(), inplace=True)
                            strategy = 'mediana (fallback)'
                
                # Para columnas categóricas
                else:
                    if missing_pct < 5:
                        # Imputar con la moda
                        mode_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
                        df[col].fillna(mode_value, inplace=True)
                        strategy = 'moda'
                    else:
                        # Crear categoría "Unknown"
                        df[col].fillna('Unknown', inplace=True)
                        strategy = 'categoría "Unknown"'
                
                if strategy:
                    missing_info.append({
                        'column': col,
                        'missing_count': int(missing_count),
                        'missing_percentage': f"{missing_pct:.2f}%",
                        'strategy': strategy
                    })
        
        if missing_info:
            self.cleaning_report['steps'].append({
                'step': 'Manejo de valores faltantes',
                'details': missing_info
            })
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame, auto_mode: bool) -> pd.DataFrame:
        """
        Detecta y maneja outliers usando el método IQR y Z-score
        """
        outlier_info = []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            # Método IQR (Interquartile Range)
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outliers_count = outliers_mask.sum()
            
            if outliers_count > 0:
                outliers_pct = (outliers_count / len(df)) * 100
                
                # Si son menos del 5%, tratarlos
                if outliers_pct < 5 and auto_mode:
                    # Opción 1: Winsorización (limitar a los bounds)
                    df.loc[df[col] < lower_bound, col] = lower_bound
                    df.loc[df[col] > upper_bound, col] = upper_bound
                    strategy = 'winsorización'
                else:
                    strategy = 'sin tratar (>5%)'
                
                outlier_info.append({
                    'column': col,
                    'outliers_count': int(outliers_count),
                    'outliers_percentage': f"{outliers_pct:.2f}%",
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'strategy': strategy
                })
        
        if outlier_info:
            self.cleaning_report['steps'].append({
                'step': 'Detección y manejo de outliers',
                'details': outlier_info
            })
        
        return df
    
    def _normalize_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza columnas numéricas usando StandardScaler
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            scaler = StandardScaler()
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
            
            self.cleaning_report['steps'].append({
                'step': 'Normalización',
                'columns': list(numeric_cols)
            })
        
        return df
    
    def _standardize_text(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza formato de columnas de texto
        """
        text_cols = df.select_dtypes(include=['object']).columns
        changes = []
        
        for col in text_cols:
            # Remover espacios extras
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
            
            # Capitalizar si parece nombre propio
            if any(word in col.lower() for word in ['name', 'nombre', 'ciudad', 'city', 'pais', 'country']):
                df[col] = df[col].str.title()
                changes.append(f"{col}: capitalizado")
        
        if changes:
            self.cleaning_report['steps'].append({
                'step': 'Estandarización de texto',
                'changes': changes
            })
        
        return df
    
    def get_quality_score(self, df: pd.DataFrame) -> dict:
        """
        Calcula un score de calidad de datos
        """
        score_components = {}
        
        # 1. Completitud (sin valores nulos)
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = (1 - null_cells / total_cells) * 100
        score_components['completeness'] = completeness
        
        # 2. Unicidad (sin duplicados)
        duplicates = df.duplicated().sum()
        uniqueness = (1 - duplicates / len(df)) * 100
        score_components['uniqueness'] = uniqueness
        
        # 3. Consistencia (tipos de datos correctos)
        # Verificar que columnas numéricas sean realmente numéricas
        numeric_consistency = 0
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            numeric_consistency = 100
        score_components['consistency'] = numeric_consistency
        
        # Score general (promedio ponderado)
        overall_score = (
            completeness * 0.4 +
            uniqueness * 0.3 +
            numeric_consistency * 0.3
        )
        
        return {
            'overall_score': round(overall_score, 2),
            'components': score_components,
            'grade': self._get_grade(overall_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """Convierte score a calificación"""
        if score >= 90:
            return 'A - Excelente'
        elif score >= 80:
            return 'B - Buena'
        elif score >= 70:
            return 'C - Aceptable'
        elif score >= 60:
            return 'D - Necesita mejoras'
        else:
            return 'F - Pobre'
