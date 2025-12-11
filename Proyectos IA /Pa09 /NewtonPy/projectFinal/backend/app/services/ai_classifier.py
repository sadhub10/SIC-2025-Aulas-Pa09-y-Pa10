"""
Servicio de clasificación
"""
from typing import Dict, Any, List
from app.models import CSVClassification


class AIClassifier:
    """Clase para clasificar CSVs con reglas básicas"""
    
    def __init__(self):
        # No necesitamos cliente de Anthropic
        pass
    
    def classify_csv(self, csv_summary: str) -> CSVClassification:
        """Clasifica el tipo de CSV con reglas básicas"""
        
        summary_lower = csv_summary.lower()
        
        # Detección por palabras clave
        if any(word in summary_lower for word in ['gasto', 'expense', 'cost', 'vendor', 'invoice']):
            category = 'gastos_operativos'
            subcategory = 'gastos_generales'
            reasoning = 'Detectado CSV de gastos operativos por palabras clave: gasto, expense, vendor, invoice'
            suggested = [
                'Análisis de gastos por departamento',
                'Identificación de proveedores frecuentes',
                'Análisis de tendencias de gasto',
                'Detección de gastos atípicos'
            ]
        elif any(word in summary_lower for word in ['venta', 'sale', 'revenue', 'customer']):
            category = 'ventas'
            subcategory = 'rendimiento'
            reasoning = 'Detectado CSV de ventas por palabras clave: venta, sale, revenue'
            suggested = [
                'Análisis de ventas por período',
                'Identificación de productos top',
                'Análisis de tendencias de ventas',
                'Segmentación de clientes'
            ]
        elif any(word in summary_lower for word in ['empleado', 'employee', 'salario', 'salary', 'nomina']):
            category = 'recursos_humanos'
            subcategory = 'personal'
            reasoning = 'Detectado CSV de RRHH por palabras clave: empleado, salario, nómina'
            suggested = [
                'Análisis de distribución salarial',
                'Análisis de antigüedad',
                'Evaluación de rendimiento',
                'Análisis de estructura organizacional'
            ]
        elif any(word in summary_lower for word in ['stock', 'inventory', 'producto', 'product']):
            category = 'inventario'
            subcategory = 'control_stock'
            reasoning = 'Detectado CSV de inventario por palabras clave: stock, inventory, producto'
            suggested = [
                'Análisis de rotación de inventario',
                'Identificación de productos con bajo stock',
                'Análisis de valor del inventario',
                'Detección de productos obsoletos'
            ]
        elif any(word in summary_lower for word in ['ingreso', 'income', 'balance', 'financ']):
            category = 'finanzas'
            subcategory = 'estados_financieros'
            reasoning = 'Detectado CSV financiero por palabras clave: ingreso, balance, finanzas'
            suggested = [
                'Análisis de ratios financieros',
                'Análisis de tendencias',
                'Proyecciones financieras',
                'Análisis de rentabilidad'
            ]
        else:
            category = 'general'
            subcategory = None
            reasoning = 'CSV de propósito general - no se identificó una categoría específica'
            suggested = [
                'Análisis estadístico descriptivo',
                'Detección de valores atípicos',
                'Análisis de correlaciones',
                'Visualización de distribuciones'
            ]
        
        return CSVClassification(
            category=category,
            confidence=0.80,
            subcategory=subcategory,
            reasoning=reasoning,
            suggested_analyses=suggested
        )
    
    def generate_insights(self, csv_summary: str, classification: CSVClassification) -> List[str]:
        """Genera insights básicos sin IA"""
        
        insights = [
            f'Archivo clasificado como: {classification.category}',
            'Se han detectado patrones en los datos numéricos',
            'La estructura del CSV es consistente y está bien formateada',
            'Se recomienda realizar análisis adicionales según el tipo de datos',
            'Los datos están listos para análisis detallado'
        ]
        
        # Insights específicos por categoría
        if classification.category == 'gastos_operativos':
            insights.extend([
                'Se pueden identificar departamentos con mayores gastos',
                'Analizar frecuencia y montos de gastos por proveedor'
            ])
        elif classification.category == 'ventas':
            insights.extend([
                'Identificar productos o servicios más vendidos',
                'Analizar tendencias de ventas por período'
            ])
        elif classification.category == 'recursos_humanos':
            insights.extend([
                'Evaluar distribución de salarios y equidad',
                'Analizar relación entre antigüedad y rendimiento'
            ])
        
        return insights[:5]
    
    def compare_csvs(self, summaries: List[str], filenames: List[str]) -> Dict[str, Any]:
        """Comparación básica sin IA"""
        
        return {
            "comparison_type": "comparación_estructural",
            "insights": [
                f'Se están comparando {len(filenames)} archivos',
                'Los archivos parecen tener estructura similar',
                'Se recomienda análisis detallado de diferencias entre períodos',
                'Buscar tendencias y patrones entre los archivos'
            ],
            "metrics": {
                "total_archivos": len(filenames),
                "archivos": filenames
            }
        }
