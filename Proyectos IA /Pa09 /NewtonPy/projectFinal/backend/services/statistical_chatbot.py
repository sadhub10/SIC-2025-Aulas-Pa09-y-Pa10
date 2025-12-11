import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re
from datetime import datetime

class StatisticalChatbot:
    """
    Chatbot basado en análisis estadístico
    NO usa APIs externas - solo análisis de datos con Python
    """
    
    def __init__(self):
        self.question_patterns = {
            'total': ['total', 'suma', 'sum', 'cuánto', 'cuanto'],
            'average': ['promedio', 'media', 'average', 'mean'],
            'max': ['máximo', 'maximo', 'mayor', 'highest', 'max'],
            'min': ['mínimo', 'minimo', 'menor', 'lowest', 'min'],
            'count': ['cuántos', 'cuantos', 'cantidad', 'count', 'how many'],
            'trend': ['tendencia', 'trend', 'evolución', 'evolution', 'cambio'],
            'comparison': ['comparar', 'compare', 'diferencia', 'difference', 'versus', 'vs'],
            'distribution': ['distribución', 'distribution', 'rango', 'range'],
            'correlation': ['relación', 'relation', 'correlación', 'correlation', 'afecta'],
            'top': ['mejor', 'top', 'primero', 'first', 'mejores'],
            'bottom': ['peor', 'worst', 'último', 'ultimo', 'last', 'peores']
        }
    
    def ask(self, question: str, context_files: List[Dict]) -> str:
        """
        Responde preguntas analizando los datos estadísticamente
        """
        try:
            question_lower = question.lower()
            
            # Identificar tipo de pregunta
            question_type = self._identify_question_type(question_lower)
            
            # Extraer datos del contexto
            all_dataframes = []
            all_analysis = []
            
            for file_data in context_files:
                # Cargar DataFrame
                try:
                    df = pd.read_csv(file_data['filepath'])
                    all_dataframes.append({
                        'df': df,
                        'filename': file_data['filename'],
                        'category': file_data['detection']['category']
                    })
                    all_analysis.append(file_data['analysis'])
                except:
                    continue
            
            if not all_dataframes:
                return "No pude acceder a los datos de los archivos."
            
            # Responder según el tipo de pregunta
            if question_type == 'total':
                return self._answer_total(question_lower, all_dataframes)
            
            elif question_type == 'average':
                return self._answer_average(question_lower, all_dataframes)
            
            elif question_type == 'max':
                return self._answer_max(question_lower, all_dataframes)
            
            elif question_type == 'min':
                return self._answer_min(question_lower, all_dataframes)
            
            elif question_type == 'count':
                return self._answer_count(question_lower, all_dataframes)
            
            elif question_type == 'top':
                return self._answer_top(question_lower, all_dataframes)
            
            elif question_type == 'bottom':
                return self._answer_bottom(question_lower, all_dataframes)
            
            elif question_type == 'comparison':
                return self._answer_comparison(question_lower, all_dataframes, all_analysis)
            
            elif question_type == 'distribution':
                return self._answer_distribution(question_lower, all_dataframes)
            
            elif question_type == 'correlation':
                return self._answer_correlation(question_lower, all_dataframes)
            
            else:
                # Respuesta general
                return self._generate_general_summary(all_dataframes, all_analysis)
        
        except Exception as e:
            return f"Hubo un error al analizar tu pregunta: {str(e)}"
    
    def _identify_question_type(self, question: str) -> str:
        """Identifica el tipo de pregunta"""
        for q_type, keywords in self.question_patterns.items():
            if any(keyword in question for keyword in keywords):
                return q_type
        return 'general'
    
    def _find_relevant_column(self, question: str, df: pd.DataFrame) -> str:
        """Encuentra la columna más relevante para la pregunta"""
        question_words = set(question.lower().split())
        
        best_match = None
        best_score = 0
        
        for col in df.columns:
            col_words = set(col.lower().replace('_', ' ').split())
            score = len(question_words.intersection(col_words))
            
            if score > best_score:
                best_score = score
                best_match = col
        
        # Si no hay match, usar la primera columna numérica
        if best_match is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                best_match = numeric_cols[0]
        
        return best_match
    
    def _answer_total(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre totales"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            # Encontrar columna relevante
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                total = df[col].sum()
                responses.append(f"**{filename}**: El total de {col} es **{total:,.2f}**")
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para calcular totales."
    
    def _answer_average(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre promedios"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                avg = df[col].mean()
                responses.append(f"**{filename}**: El promedio de {col} es **{avg:,.2f}**")
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para calcular promedios."
    
    def _answer_max(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre valores máximos"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                max_val = df[col].max()
                max_idx = df[col].idxmax()
                
                # Intentar encontrar una columna de nombre/identificador
                name_col = None
                for c in df.columns:
                    if any(word in c.lower() for word in ['name', 'nombre', 'vendedor', 'empleado', 'producto']):
                        name_col = c
                        break
                
                if name_col:
                    name = df.loc[max_idx, name_col]
                    responses.append(f"**{filename}**: El valor máximo de {col} es **{max_val:,.2f}** ({name})")
                else:
                    responses.append(f"**{filename}**: El valor máximo de {col} es **{max_val:,.2f}**")
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para encontrar el máximo."
    
    def _answer_min(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre valores mínimos"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                min_val = df[col].min()
                min_idx = df[col].idxmin()
                
                name_col = None
                for c in df.columns:
                    if any(word in c.lower() for word in ['name', 'nombre', 'vendedor', 'empleado', 'producto']):
                        name_col = c
                        break
                
                if name_col:
                    name = df.loc[min_idx, name_col]
                    responses.append(f"**{filename}**: El valor mínimo de {col} es **{min_val:,.2f}** ({name})")
                else:
                    responses.append(f"**{filename}**: El valor mínimo de {col} es **{min_val:,.2f}**")
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para encontrar el mínimo."
    
    def _answer_count(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre conteos"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            responses.append(f"**{filename}**: Hay **{len(df)}** registros en total")
            
            # Si pregunta por algo específico
            col = self._find_relevant_column(question, df)
            if col:
                unique_count = df[col].nunique()
                responses.append(f"  - {unique_count} valores únicos en {col}")
        
        return "\n".join(responses)
    
    def _answer_top(self, question: str, dataframes: List[Dict], n: int = 5) -> str:
        """Responde preguntas sobre los mejores/top"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                top_n = df.nlargest(n, col)
                
                name_col = None
                for c in df.columns:
                    if any(word in c.lower() for word in ['name', 'nombre', 'vendedor', 'empleado', 'producto']):
                        name_col = c
                        break
                
                response = f"**{filename}** - Top {n} en {col}:\n"
                for i, (idx, row) in enumerate(top_n.iterrows(), 1):
                    val = row[col]
                    if name_col:
                        name = row[name_col]
                        response += f"  {i}. {name}: {val:,.2f}\n"
                    else:
                        response += f"  {i}. {val:,.2f}\n"
                
                responses.append(response)
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para generar el ranking."
    
    def _answer_bottom(self, question: str, dataframes: List[Dict], n: int = 5) -> str:
        """Responde preguntas sobre los peores/bottom"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                bottom_n = df.nsmallest(n, col)
                
                name_col = None
                for c in df.columns:
                    if any(word in c.lower() for word in ['name', 'nombre', 'vendedor', 'empleado', 'producto']):
                        name_col = c
                        break
                
                response = f"**{filename}** - Bottom {n} en {col}:\n"
                for i, (idx, row) in enumerate(bottom_n.iterrows(), 1):
                    val = row[col]
                    if name_col:
                        name = row[name_col]
                        response += f"  {i}. {name}: {val:,.2f}\n"
                    else:
                        response += f"  {i}. {val:,.2f}\n"
                
                responses.append(response)
        
        if responses:
            return "\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para generar el ranking."
    
    def _answer_comparison(self, question: str, dataframes: List[Dict], all_analysis: List[Dict]) -> str:
        """Responde preguntas de comparación"""
        if len(dataframes) < 2:
            return "Necesito al menos 2 archivos para hacer comparaciones."
        
        responses = []
        
        # Comparar totales
        col = self._find_relevant_column(question, dataframes[0]['df'])
        
        if col:
            for data in dataframes:
                df = data['df']
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    total = df[col].sum()
                    avg = df[col].mean()
                    responses.append(f"**{data['filename']}**:\n  - Total: {total:,.2f}\n  - Promedio: {avg:,.2f}")
        
        if responses:
            return "\n\n".join(responses)
        else:
            return "No pude encontrar datos comparables entre los archivos."
    
    def _answer_distribution(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre distribución"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            col = self._find_relevant_column(question, df)
            
            if col and pd.api.types.is_numeric_dtype(df[col]):
                stats = df[col].describe()
                response = f"**{filename}** - Distribución de {col}:\n"
                response += f"  - Mínimo: {stats['min']:,.2f}\n"
                response += f"  - Q1 (25%): {stats['25%']:,.2f}\n"
                response += f"  - Mediana: {stats['50%']:,.2f}\n"
                response += f"  - Q3 (75%): {stats['75%']:,.2f}\n"
                response += f"  - Máximo: {stats['max']:,.2f}\n"
                response += f"  - Media: {stats['mean']:,.2f}\n"
                response += f"  - Desv. Est.: {stats['std']:,.2f}"
                
                responses.append(response)
        
        if responses:
            return "\n\n".join(responses)
        else:
            return "No encontré columnas numéricas relevantes para analizar la distribución."
    
    def _answer_correlation(self, question: str, dataframes: List[Dict]) -> str:
        """Responde preguntas sobre correlaciones"""
        responses = []
        
        for data in dataframes:
            df = data['df']
            filename = data['filename']
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                
                # Encontrar las correlaciones más fuertes
                strong_corr = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if abs(corr_val) > 0.5:  # Correlación significativa
                            strong_corr.append({
                                'col1': corr_matrix.columns[i],
                                'col2': corr_matrix.columns[j],
                                'corr': corr_val
                            })
                
                if strong_corr:
                    response = f"**{filename}** - Correlaciones significativas:\n"
                    for sc in sorted(strong_corr, key=lambda x: abs(x['corr']), reverse=True)[:5]:
                        response += f"  - {sc['col1']} ↔ {sc['col2']}: {sc['corr']:.2f}\n"
                    responses.append(response)
        
        if responses:
            return "\n\n".join(responses)
        else:
            return "No encontré correlaciones significativas entre las variables numéricas."
    
    def _generate_general_summary(self, dataframes: List[Dict], all_analysis: List[Dict]) -> str:
        """Genera un resumen general de los datos"""
        responses = []
        
        for data, analysis in zip(dataframes, all_analysis):
            df = data['df']
            filename = data['filename']
            category = data['category']
            
            response = f"**{filename}** ({category}):\n"
            response += f"  - {len(df)} registros, {len(df.columns)} columnas\n"
            
            # Columnas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                response += f"  - {len(numeric_cols)} columnas numéricas\n"
                
                for col in numeric_cols[:3]:  # Primeras 3
                    total = df[col].sum()
                    avg = df[col].mean()
                    response += f"    • {col}: Total={total:,.2f}, Promedio={avg:,.2f}\n"
            
            # Insights del análisis
            insights = analysis.get('insights', [])
            if insights:
                response += "  - Insights:\n"
                for insight in insights[:3]:  # Primeros 3
                    response += f"    • {insight}\n"
            
            responses.append(response)
        
        return "\n".join(responses)
    
    def get_suggested_questions(self, category: str) -> List[str]:
        """
        Genera preguntas sugeridas según el tipo de datos
        """
        suggestions = {
            'financial': [
                "¿Cuál es el gasto total?",
                "¿Qué categoría tiene los mayores gastos?",
                "¿Hay algún gasto inusual o atípico?",
                "¿Cuál es el gasto promedio por transacción?",
                "¿Cómo se distribuyen los gastos?"
            ],
            'sales': [
                "¿Quién es el mejor vendedor?",
                "¿Cuáles son las ventas totales?",
                "¿Cuál es el promedio de ventas?",
                "¿Quiénes son los top 5 vendedores?",
                "¿Cuál es la distribución de las ventas?"
            ],
            'hr': [
                "¿Cuál es el salario promedio?",
                "¿Cuántos empleados hay?",
                "¿Qué departamento tiene los salarios más altos?",
                "¿Cuál es la distribución de edades?",
                "¿Quiénes son los empleados mejor pagados?"
            ]
        }
        
        return suggestions.get(category, [
            "¿Cuál es el total?",
            "¿Cuál es el promedio?",
            "¿Cuáles son los valores máximos y mínimos?",
            "¿Cómo se distribuyen los datos?",
            "¿Hay valores inusuales?"
        ])
