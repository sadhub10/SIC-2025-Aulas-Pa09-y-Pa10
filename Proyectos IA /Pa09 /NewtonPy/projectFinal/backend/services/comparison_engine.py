import pandas as pd
import numpy as np
from typing import Dict, List, Any

class ComparisonEngine:
    """
    Compara múltiples archivos CSV del mismo tipo y genera análisis comparativos
    """
    
    def compare(self, files: List[Dict]) -> Dict[str, Any]:
        """
        Compara múltiples archivos y genera insights comparativos
        """
        try:
            if len(files) < 2:
                return {'error': 'Need at least 2 files to compare'}
            
            # Verificar que sean del mismo tipo
            categories = [f['detection']['category'] for f in files]
            main_category = max(set(categories), key=categories.count)
            
            # Leer todos los DataFrames
            dfs = []
            for f in files:
                df = self._read_csv_safely(f['filepath'])
                df['_source_file'] = f['filename']
                dfs.append(df)
            
            # Comparación específica según categoría
            if main_category == 'financial':
                comparison = self._compare_financial(dfs, files)
            elif main_category == 'sales':
                comparison = self._compare_sales(dfs, files)
            elif main_category == 'hr':
                comparison = self._compare_hr(dfs, files)
            else:
                comparison = self._compare_generic(dfs, files)
            
            # Agregar información general
            comparison['files_compared'] = [f['filename'] for f in files]
            comparison['category'] = main_category
            comparison['total_records'] = sum(len(df) for df in dfs)
            
            return comparison
            
        except Exception as e:
            return {'error': str(e)}
    
    def _read_csv_safely(self, filepath: str) -> pd.DataFrame:
        """Lee CSV con diferentes encodings"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return pd.read_csv(filepath, encoding=encoding)
            except:
                continue
        
        return pd.read_csv(filepath)
    
    def _compare_financial(self, dfs: List[pd.DataFrame], files: List[Dict]) -> Dict[str, Any]:
        """Compara datos financieros"""
        comparison = {}
        
        # Buscar columna de montos
        amount_col = None
        for col in dfs[0].columns:
            if any(kw in col.lower() for kw in ['amount', 'monto', 'total', 'gasto', 'cost']):
                if pd.api.types.is_numeric_dtype(dfs[0][col]):
                    amount_col = col
                    break
        
        if amount_col:
            totals = []
            for i, df in enumerate(dfs):
                if amount_col in df.columns:
                    total = df[amount_col].sum()
                    totals.append({
                        'file': files[i]['filename'],
                        'total': float(total),
                        'average': float(df[amount_col].mean()),
                        'count': len(df)
                    })
            
            comparison['totals_by_file'] = totals
            
            # Calcular diferencias
            if len(totals) >= 2:
                diff = totals[1]['total'] - totals[0]['total']
                pct_change = (diff / totals[0]['total'] * 100) if totals[0]['total'] != 0 else 0
                
                comparison['change_analysis'] = {
                    'absolute_change': float(diff),
                    'percentage_change': float(pct_change),
                    'trend': 'increase' if diff > 0 else 'decrease' if diff < 0 else 'stable'
                }
        
        # Comparar por categorías
        category_col = None
        for col in dfs[0].columns:
            if any(kw in col.lower() for kw in ['category', 'type', 'categoria', 'tipo', 'department', 'departamento']):
                category_col = col
                break
        
        if category_col and amount_col:
            category_comparison = {}
            
            # Obtener todas las categorías únicas
            all_categories = set()
            for df in dfs:
                if category_col in df.columns:
                    all_categories.update(df[category_col].unique())
            
            for category in all_categories:
                category_data = []
                for i, df in enumerate(dfs):
                    if category_col in df.columns and amount_col in df.columns:
                        cat_total = df[df[category_col] == category][amount_col].sum()
                        category_data.append({
                            'file': files[i]['filename'],
                            'total': float(cat_total)
                        })
                
                category_comparison[str(category)] = category_data
            
            comparison['by_category'] = category_comparison
        
        return comparison
    
    def _compare_sales(self, dfs: List[pd.DataFrame], files: List[Dict]) -> Dict[str, Any]:
        """Compara datos de ventas"""
        comparison = {}
        
        # Buscar columnas de ventas
        sales_col = None
        seller_col = None
        
        for col in dfs[0].columns:
            col_lower = col.lower()
            if any(kw in col_lower for kw in ['venta', 'sales', 'sold']):
                sales_col = col
            if any(kw in col_lower for kw in ['vendedor', 'seller', 'nombre', 'name']):
                seller_col = col
        
        if sales_col:
            # Comparar totales de ventas
            sales_totals = []
            for i, df in enumerate(dfs):
                if sales_col in df.columns:
                    # Limpiar valores
                    sales_clean = df[sales_col].astype(str).str.replace('$', '').str.replace(',', '')
                    sales_numeric = pd.to_numeric(sales_clean, errors='coerce')
                    
                    sales_totals.append({
                        'file': files[i]['filename'],
                        'total_sales': float(sales_numeric.sum()),
                        'average_sales': float(sales_numeric.mean()),
                        'num_transactions': len(df)
                    })
            
            comparison['sales_by_file'] = sales_totals
            
            # Calcular crecimiento
            if len(sales_totals) >= 2:
                growth = sales_totals[1]['total_sales'] - sales_totals[0]['total_sales']
                growth_pct = (growth / sales_totals[0]['total_sales'] * 100) if sales_totals[0]['total_sales'] != 0 else 0
                
                comparison['growth_analysis'] = {
                    'absolute_growth': float(growth),
                    'percentage_growth': float(growth_pct),
                    'trend': 'positive' if growth > 0 else 'negative' if growth < 0 else 'stable'
                }
        
        if seller_col and sales_col:
            # Comparar vendedores entre períodos
            seller_comparison = {}
            
            # Obtener todos los vendedores
            all_sellers = set()
            for df in dfs:
                if seller_col in df.columns:
                    all_sellers.update(df[seller_col].unique())
            
            for seller in all_sellers:
                seller_data = []
                for i, df in enumerate(dfs):
                    if seller_col in df.columns and sales_col in df.columns:
                        seller_rows = df[df[seller_col] == seller]
                        if len(seller_rows) > 0:
                            sales_clean = seller_rows[sales_col].astype(str).str.replace('$', '').str.replace(',', '')
                            sales_numeric = pd.to_numeric(sales_clean, errors='coerce')
                            
                            seller_data.append({
                                'file': files[i]['filename'],
                                'total_sales': float(sales_numeric.sum()),
                                'num_sales': len(seller_rows)
                            })
                        else:
                            seller_data.append({
                                'file': files[i]['filename'],
                                'total_sales': 0,
                                'num_sales': 0
                            })
                
                # Calcular cambio para este vendedor
                if len(seller_data) >= 2:
                    change = seller_data[1]['total_sales'] - seller_data[0]['total_sales']
                    seller_comparison[str(seller)] = {
                        'data': seller_data,
                        'change': float(change),
                        'trend': 'improving' if change > 0 else 'declining' if change < 0 else 'stable'
                    }
            
            comparison['seller_performance'] = seller_comparison
            
            # Identificar top performers y underperformers
            if len(seller_comparison) > 0:
                changes = [(seller, data['change']) for seller, data in seller_comparison.items()]
                changes.sort(key=lambda x: x[1], reverse=True)
                
                comparison['top_improvers'] = [{'seller': s, 'improvement': float(c)} for s, c in changes[:5] if c > 0]
                comparison['top_decliners'] = [{'seller': s, 'decline': float(c)} for s, c in changes[-5:] if c < 0]
        
        return comparison
    
    def _compare_hr(self, dfs: List[pd.DataFrame], files: List[Dict]) -> Dict[str, Any]:
        """Compara datos de RR.HH."""
        comparison = {}
        
        # Comparar número de empleados
        employee_counts = []
        for i, df in enumerate(dfs):
            employee_counts.append({
                'file': files[i]['filename'],
                'count': len(df)
            })
        
        comparison['employee_count'] = employee_counts
        
        # Comparar salarios si existe la columna
        salary_col = None
        for col in dfs[0].columns:
            if any(kw in col.lower() for kw in ['salary', 'salario', 'sueldo']):
                salary_col = col
                break
        
        if salary_col:
            salary_comparison = []
            for i, df in enumerate(dfs):
                if salary_col in df.columns:
                    salary_comparison.append({
                        'file': files[i]['filename'],
                        'average_salary': float(df[salary_col].mean()),
                        'min_salary': float(df[salary_col].min()),
                        'max_salary': float(df[salary_col].max())
                    })
            
            comparison['salary_comparison'] = salary_comparison
        
        return comparison
    
    def _compare_generic(self, dfs: List[pd.DataFrame], files: List[Dict]) -> Dict[str, Any]:
        """Comparación genérica"""
        comparison = {}
        
        # Comparar tamaños
        sizes = []
        for i, df in enumerate(dfs):
            sizes.append({
                'file': files[i]['filename'],
                'rows': len(df),
                'columns': len(df.columns)
            })
        
        comparison['size_comparison'] = sizes
        
        # Comparar columnas comunes
        common_cols = set(dfs[0].columns)
        for df in dfs[1:]:
            common_cols = common_cols.intersection(set(df.columns))
        
        comparison['common_columns'] = list(common_cols)
        comparison['num_common_columns'] = len(common_cols)
        
        return comparison
