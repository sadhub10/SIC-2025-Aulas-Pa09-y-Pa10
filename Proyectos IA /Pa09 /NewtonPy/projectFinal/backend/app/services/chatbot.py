"""
Servicio de chatbot básico SIN IA de Anthropic
"""
from typing import List, Dict, Any


class DataChatbot:
    """Chatbot básico que responde sobre los datos del CSV"""
    
    def __init__(self):
        pass
    
    def answer_question(
        self,
        question: str,
        csv_summary: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Responde preguntas de forma básica"""
        
        question_lower = question.lower()
        
        # Respuestas predefinidas según palabras clave
        if any(word in question_lower for word in ['promedio', 'average', 'media']):
            response = "Para calcular el promedio, revisa las estadísticas numéricas en la sección de resultados. Allí encontrarás el promedio de cada columna numérica."
        elif any(word in question_lower for word in ['total', 'suma', 'sum']):
            response = "Puedes ver los totales en las estadísticas resumidas de cada columna numérica en la sección de análisis."
        elif any(word in question_lower for word in ['mayor', 'máximo', 'max', 'highest']):
            response = "Los valores máximos de cada columna están disponibles en las estadísticas descriptivas del análisis."
        elif any(word in question_lower for word in ['menor', 'mínimo', 'min', 'lowest']):
            response = "Los valores mínimos se muestran en las estadísticas de cada columna numérica."
        elif any(word in question_lower for word in ['tendencia', 'trend', 'patrón', 'pattern']):
            response = "Para identificar tendencias, revisa las visualizaciones generadas. Los gráficos muestran patrones en los datos."
        elif any(word in question_lower for word in ['comparar', 'compare', 'diferencia']):
            response = "Si has subido múltiples archivos, puedes alternar entre ellos usando los botones superiores para compararlos."
        else:
            response = f"He recibido tu pregunta sobre: '{question}'. Revisa las estadísticas, visualizaciones e insights generados automáticamente para encontrar información relevante sobre tus datos."
        
        return {
            "response": response,
            "suggested_questions": [
                "¿Cuál es el promedio de los valores?",
                "¿Cuál es el valor máximo?",
                "¿Hay alguna tendencia visible?",
                "¿Cómo puedo comparar múltiples archivos?"
            ],
            "sources": ["Análisis automático del sistema"]
        }
