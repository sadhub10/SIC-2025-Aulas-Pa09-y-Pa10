# ia/configIA.py
from dataclasses import dataclass, field
from typing import List, Dict

CATEGORIAS_BASE = [
    "sobrecarga laboral", "liderazgo", "comunicación", "reconocimiento",
    "remuneración", "equilibrio vida-trabajo", "ambiente laboral",
    "procesos", "tecnología/herramientas", "conflictos internos",
    "recursos insuficientes", "formación/capacitación", "satisfacción general", "motivación"
]

STRESS_FROM_SENTIMENT = {"negative": "alto", "neutral": "medio", "positive": "bajo"}
STRESS_KEYWORDS = {
    "alto": {"agotado","estresado","quemado","burnout","ansioso","ansiedad","colapsado"},
    "medio": {"preocupado","tenso","presión","apuro"}
}

@dataclass(frozen=True)
class IAConfig:
    # Modelos en ESPAÑOL para mejor análisis de comentarios
    sentiment_model: str = "pysentimiento/robertuito-sentiment-analysis"
    emotion_model:   str = "finiteautomata/beto-emotion-analysis"
    # Modelo más ligero para clasificación de categorías
    zeroshot_model:  str = "Recognai/bert-base-spanish-wwm-cased-xnli"
    summarizer_model:str = "mrm8488/bert2bert_shared-spanish-finetuned-summarization"

    categorias: List[str] = field(default_factory=lambda: CATEGORIAS_BASE)
    min_score_categoria: float = 0.35
    stress_map: Dict[str,str] = field(default_factory=lambda: STRESS_FROM_SENTIMENT)
    stress_keywords: Dict[str,set] = field(default_factory=lambda: STRESS_KEYWORDS)
    max_len_summary: int = 800
    max_len_models: int = 1000
