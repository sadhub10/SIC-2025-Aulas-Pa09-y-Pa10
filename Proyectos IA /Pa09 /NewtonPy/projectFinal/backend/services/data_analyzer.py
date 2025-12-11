import pandas as pd
import numpy as np
from typing import Dict, List, Any
import json

class DataAnalyzer:
    """
    Analiza datos del CSV y genera insights automáticos
    """
    
    def analyze(self, filepath: str, detection_result: Dict) -> Dict[str, Any]:
        """
        Realiza análisis completo del CSV basado en su tipo detectado
        """
        try:
            df = self._read_csv_safely(filepath)
            category = detection_result.get('category', 'unknown')
            
            # Análisis estadístico básico
            stats = self._basic_statistics(df)
            
            # Análisis específico por categoría
            if category == 'financial':
                specific_analysis = self._analyze_financial(df)
            elif category == 'sales':
                specific_analysis = self._analyze_sales(df)
            elif category == 'hr':
                specific_analysis = self._analyze_hr(df)
            elif category == 'performance':
                specific_analysis = self._analyze_performance(df)
            else:
                specific_analysis = self._analyze_generic(df)
            
            # Detectar outliers
            outliers = self._detect_outliers(df)
            
            # Análisis de correlaciones
            correlations = self._analyze_correlations(df)
            
            # Generar insights textuales
            insights = self._generate_insights(df, category, specific_analysis)
            
            # Preparar datos para visualización
            viz_data = self._prepare_visualization_data(df, category)
            
            return {
                'statistics': stats,
                'specific_analysis': specific_analysis,
                'outliers': outliers,
                'correlations': correlations,
                'insights': insights,
                'visualization_data': viz_data
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'statistics': {},
                'insights': []
            }
    
    def _read_csv_safely(self, filepath: str) -> pd.DataFrame:
        """Lee CSV con diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except:
                continue
        
        return pd.read_csv(filepath)
    
    def _basic_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calcula estadísticas básicas"""
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': [],
            'text_columns': [],
            'missing_data': {}
        }
        
        # Analizar cada columna
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                stats['missing_data'][col] = {
                    'count': int(missing_count),
                    'percentage': float(missing_count / len(df) * 100)
                }
            
            if pd.api.types.is_numeric_dtype(df[col]):
                stats['numeric_columns'].append({
                    'name': col,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None,
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                    'median': float(df[col].median()) if not df[col].isna().all() else None,
                    'std': float(df[col].std()) if not df[col].isna().all() else None
                })
            else:
                stats['text_columns'].append({
                    'name': col,
                    'unique_values': int(df[col].nunique()),
                    'most_common': df[col].mode()[0] if len(df[col].mode()) > 0 else None
                })
        
        return stats
    
    def _analyze_financial(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico para datos financieros"""
        analysis = {}
        
        # Buscar columna de montos
        amount_col = None
        for col in df.columns:
            if any(keyword in col.lower() for keyword in ['amount', 'monto', 'total', 'price', 'cost', 'gasto']):
                if pd.api.types.is_numeric_dtype(df[col]):
                    amount_col = col
                    break
        
        if amount_col:
            analysis['total_amount'] = float(df[amount_col].sum())
            analysis['average_amount'] = float(df[amount_col].mean())
            analysis['max_transaction'] = float(df[amount_col].max())
            analysis['min_transaction'] = float(df[amount_col].min())
        
        # Analizar por categorías si existe
        category_cols = [col for col in df.columns if any(kw in col.lower() 
                         for kw in ['category', 'type', 'department', 'categoria', 'tipo', 'departamento'])]
        
        if category_cols and amount_col:
            cat_col = category_cols[0]
            analysis['by_category'] = df.groupby(cat_col)[amount_col].agg(['sum', 'mean', 'count']).to_dict('index')
        
        # Detectar fechas
        date_cols = [col for col in df.columns if any(kw in col.lower() 
                     for kw in ['date', 'fecha', 'time', 'timestamp'])]
        
        if date_cols and amount_col:
            date_col = date_cols[0]
            try:
                df['parsed_date'] = pd.to_datetime(df[date_col], errors='coerce')
                df['month'] = df['parsed_date'].dt.to_period('M')
                monthly = df.groupby('month')[amount_col].sum()
                analysis['monthly_trend'] = {str(k): float(v) for k, v in monthly.items()}
            except:
                pass
        
        return analysis
    
    def _analyze_sales(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico para datos de ventas"""
        analysis = {}
        
        # Buscar columnas relevantes
        sales_col = None
        seller_col = None
        
        for col in df.columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['venta', 'sales', 'sold', 'revenue']):
                sales_col = col
            if any(kw in col_lower for kw in ['vendedor', 'seller', 'nombre', 'name', 'empleado']):
                seller_col = col
        
        if sales_col:
            # Limpiar valores de ventas (remover $, comas, etc.)
            sales_clean = df[sales_col].astype(str).str.replace('$', '').str.replace(',', '')
            try:
                sales_numeric = pd.to_numeric(sales_clean, errors='coerce')
                analysis['total_sales'] = float(sales_numeric.sum())
                analysis['average_sales'] = float(sales_numeric.mean())
            except:
                pass
        
        if seller_col and sales_col:
            try:
                sales_clean = df[sales_col].astype(str).str.replace('$', '').str.replace(',', '')
                sales_numeric = pd.to_numeric(sales_clean, errors='coerce')
                df['sales_numeric'] = sales_numeric
                
                # Top vendedores
                top_sellers = df.groupby(seller_col)['sales_numeric'].sum().sort_values(ascending=False).head(10)
                analysis['top_sellers'] = {str(k): float(v) for k, v in top_sellers.items()}
                
                # Vendedores con bajo rendimiento
                bottom_sellers = df.groupby(seller_col)['sales_numeric'].sum().sort_values().head(5)
                analysis['bottom_sellers'] = {str(k): float(v) for k, v in bottom_sellers.items()}
            except:
                pass
        
        # Analizar efectividad si existe
        effectiveness_col = [col for col in df.columns if 'efectividad' in col.lower() or 'efficiency' in col.lower()]
        if effectiveness_col:
            eff_col = effectiveness_col[0]
            try:
                eff_clean = df[eff_col].astype(str).str.replace('%', '')
                eff_numeric = pd.to_numeric(eff_clean, errors='coerce')
                analysis['average_effectiveness'] = float(eff_numeric.mean())
            except:
                pass
        
        return analysis
    
    def _analyze_hr(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico para datos de RR.HH."""
        analysis = {}
        
        # Analizar salarios
        salary_col = [col for col in df.columns if any(kw in col.lower() 
                      for kw in ['salary', 'salario', 'sueldo', 'wage'])]
        
        if salary_col:
            sal_col = salary_col[0]
            analysis['average_salary'] = float(df[sal_col].mean())
            analysis['salary_range'] = {
                'min': float(df[sal_col].min()),
                'max': float(df[sal_col].max())
            }
            
            # Por departamento si existe
            dept_cols = [col for col in df.columns if 'departamento' in col.lower() or 'department' in col.lower()]
            if dept_cols:
                dept_col = dept_cols[0]
                analysis['salary_by_department'] = df.groupby(dept_col)[sal_col].mean().to_dict()
        
        # Analizar distribución de edades
        age_col = [col for col in df.columns if 'edad' in col.lower() or 'age' in col.lower()]
        if age_col:
            age_c = age_col[0]
            analysis['average_age'] = float(df[age_c].mean())
            analysis['age_distribution'] = {
                '<25': int((df[age_c] < 25).sum()),
                '25-35': int(((df[age_c] >= 25) & (df[age_c] < 35)).sum()),
                '35-45': int(((df[age_c] >= 35) & (df[age_c] < 45)).sum()),
                '45+': int((df[age_c] >= 45).sum())
            }
        
        return analysis
    
    def _analyze_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis específico para datos de rendimiento"""
        analysis = {}
        
        # Buscar columnas de métricas
        performance_cols = [col for col in df.columns if any(kw in col.lower() 
                           for kw in ['efectividad', 'efficiency', 'performance', 'calidad', 'quality'])]
        
        for col in performance_cols:
            try:
                # Limpiar valores (remover %, etc.)
                clean_vals = df[col].astype(str).str.replace('%', '').str.replace(',', '.')
                numeric_vals = pd.to_numeric(clean_vals, errors='coerce')
                
                analysis[f'{col}_average'] = float(numeric_vals.mean())
                analysis[f'{col}_top'] = float(numeric_vals.max())
                analysis[f'{col}_bottom'] = float(numeric_vals.min())
            except:
                continue
        
        return analysis
    
    def _analyze_generic(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis genérico para cualquier tipo de datos"""
        analysis = {}
        
        # Contar registros por columnas categóricas
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:3]:  # Solo primeras 3
            value_counts = df[col].value_counts().head(10)
            analysis[f'{col}_distribution'] = value_counts.to_dict()
        
        return analysis
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict[str, List]:
        """Detecta valores atípicos en columnas numéricas"""
        outliers = {}
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_indices = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
            
            if len(outlier_indices) > 0:
                outliers[col] = {
                    'count': len(outlier_indices),
                    'percentage': float(len(outlier_indices) / len(df) * 100),
                    'values': df.loc[outlier_indices, col].tolist()[:10]  # Solo primeros 10
                }
        
        return outliers
    
    def _analyze_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analiza correlaciones entre variables numéricas"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {'correlations': []}
        
        corr_matrix = numeric_df.corr()
        
        # Encontrar correlaciones fuertes (> 0.7 o < -0.7)
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append({
                        'var1': corr_matrix.columns[i],
                        'var2': corr_matrix.columns[j],
                        'correlation': float(corr_val)
                    })
        
        return {
            'strong_correlations': strong_corr,
            'correlation_matrix': corr_matrix.to_dict()
        }
    
    def _generate_insights(self, df: pd.DataFrame, category: str, specific: Dict) -> List[str]:
        """Genera insights textuales automáticos"""
        insights = []
        
        insights.append(f"El dataset contiene {len(df)} registros y {len(df.columns)} columnas.")
        
        if category == 'financial' and 'total_amount' in specific:
            insights.append(f"Total de gastos: ${specific['total_amount']:,.2f}")
            insights.append(f"Gasto promedio: ${specific['average_amount']:,.2f}")
            
            if 'by_category' in specific:
                top_cat = max(specific['by_category'].items(), key=lambda x: x[1]['sum'])
                insights.append(f"La categoría con mayor gasto es '{top_cat[0]}' con ${top_cat[1]['sum']:,.2f}")
        
        elif category == 'sales' and 'total_sales' in specific:
            insights.append(f"Ventas totales: ${specific['total_sales']:,.2f}")
            
            if 'top_sellers' in specific and specific['top_sellers']:
                top_seller = max(specific['top_sellers'].items(), key=lambda x: x[1])
                insights.append(f"El mejor vendedor es '{top_seller[0]}' con ventas de ${top_seller[1]:,.2f}")
        
        elif category == 'hr':
            if 'average_salary' in specific:
                insights.append(f"Salario promedio: ${specific['average_salary']:,.2f}")
            if 'average_age' in specific:
                insights.append(f"Edad promedio de empleados: {specific['average_age']:.1f} años")
        
        # Agregar insights sobre datos faltantes
        missing = df.isnull().sum()
        if missing.sum() > 0:
            cols_with_missing = missing[missing > 0]
            insights.append(f"Hay {len(cols_with_missing)} columnas con datos faltantes.")
        
        return insights
    
    def _prepare_visualization_data(self, df: pd.DataFrame, category: str) -> Dict[str, Any]:
        """Prepara datos para visualización en el frontend"""
        viz = {}
        
        # Gráfica de distribución para columnas numéricas principales
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            main_col = numeric_cols[0]
            viz['histogram'] = {
                'column': main_col,
                'data': df[main_col].dropna().tolist()[:1000]  # Limitar a 1000 puntos
            }
        
        # Gráfica de barras para categorías
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = df[cat_col].value_counts().head(10)
            viz['bar_chart'] = {
                'column': cat_col,
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist()
            }
        
        return viz
