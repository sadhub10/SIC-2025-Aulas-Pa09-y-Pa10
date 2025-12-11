"""
Modelos de datos para la API
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class CSVMetadata(BaseModel):
    """Metadatos del archivo CSV"""
    filename: str
    size: int
    rows: int
    columns: int
    column_names: List[str]
    upload_date: datetime = Field(default_factory=datetime.now)


class ColumnInfo(BaseModel):
    """Información de una columna"""
    name: str
    dtype: str
    sample_values: List[Any]
    null_count: int
    unique_count: int
    detected_type: str  # numeric, categorical, date, text, currency, etc.


class CSVClassification(BaseModel):
    """Clasificación del CSV"""
    category: str  # finanzas, ventas, gastos, rrhh, inventario, etc.
    confidence: float  # 0-1
    subcategory: Optional[str] = None
    reasoning: str
    suggested_analyses: List[str]


class AnalysisResult(BaseModel):
    """Resultado del análisis de CSV"""
    file_id: str
    metadata: CSVMetadata
    classification: CSVClassification
    column_info: List[ColumnInfo]
    summary_statistics: Dict[str, Any]
    insights: List[str]
    visualizations: List[Dict[str, Any]]
    raw_data_preview: List[Dict[str, Any]]


class ComparisonRequest(BaseModel):
    """Request para comparar múltiples CSVs"""
    file_ids: List[str]


class ComparisonResult(BaseModel):
    """Resultado de comparación entre CSVs"""
    files: List[str]
    comparison_type: str
    insights: List[str]
    metrics: Dict[str, Any]
    visualizations: List[Dict[str, Any]]


class ChatMessage(BaseModel):
    """Mensaje del chat"""
    file_id: str
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = []


class ChatResponse(BaseModel):
    """Respuesta del chatbot"""
    response: str
    sources: Optional[List[str]] = []
    suggested_questions: Optional[List[str]] = []
