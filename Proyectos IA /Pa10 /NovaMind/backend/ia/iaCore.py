# ia/iaCore.py
from __future__ import annotations
from typing import Dict, Any, List, Iterable, Optional, Tuple
import logging

from transformers import pipeline, Pipeline
from backend.ia.configIA import IAConfig
from backend.ia.preProcesamiento import limpiarTextoBasico

logger = logging.getLogger("NLPAnalyzer")
if not logger.handlers:
    import sys
    h = logging.StreamHandler(sys.stdout)
    logger.addHandler(h)
logger.setLevel(logging.INFO)

# ============================================================
# 🔵 MAPEOS A ESPAÑOL
# ============================================================

EMO_MAP = {
    "joy": "alegría",
    "happy": "alegría",
    "happiness": "alegría",
    "sadness": "tristeza",
    "anger": "enojo",
    "fear": "miedo",
    "disgust": "asco",
    "surprise": "sorpresa",
    "others": "otro",
    "other": "otro"
}

def _map_emotion_es(label: str) -> str:
    label = (label or "").lower().strip()
    return EMO_MAP.get(label, "indefinido")


def _trim(text: str, n: int) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0]


def _meaningful(text: str) -> bool:
    return isinstance(text, str) and len(text.strip()) >= 3


# ============================================================
# 🔵 REGISTRO DE MODELOS
# ============================================================

class ModelRegistry:
    def __init__(self, cfg: IAConfig):
        self.cfg = cfg
        self._sentiment_pipe: Optional[Pipeline] = None
        self._emotion_pipe: Optional[Pipeline] = None
        self._zeroshot_pipe: Optional[Pipeline] = None
        self._summarizer_pipe: Optional[Pipeline] = None

    def sentiment(self) -> Pipeline:
        if self._sentiment_pipe is None:
            logger.info("Cargando modelo de Sentiment...")
            self._sentiment_pipe = pipeline(
                "sentiment-analysis",
                model=self.cfg.sentiment_model,
                device=-1,
                truncation=True
            )
        return self._sentiment_pipe

    def emotion(self) -> Pipeline:
        if self._emotion_pipe is None:
            logger.info("Cargando modelo de Emotion...")
            self._emotion_pipe = pipeline(
                "text-classification",
                model=self.cfg.emotion_model,
                device=-1,
                truncation=True
            )
        return self._emotion_pipe

    def zeroshot(self) -> Pipeline:
        if self._zeroshot_pipe is None:
            logger.info("Cargando modelo Zero-shot...")
            self._zeroshot_pipe = pipeline(
                "zero-shot-classification",
                model=self.cfg.zeroshot_model,
                device=-1,
                truncation=True
            )
        return self._zeroshot_pipe

    def summarizer(self) -> Pipeline:
        if self._summarizer_pipe is None:
            logger.info("Cargando modelo Summarization...")
            self._summarizer_pipe = pipeline(
                "summarization",
                model=self.cfg.summarizer_model,
                device=-1,
                truncation=True
            )
        return self._summarizer_pipe


# ============================================================
# 🔵 ANALIZADOR PRINCIPAL
# ============================================================

class NLPAnalyzer:
    def __init__(self, cfg: Optional[IAConfig] = None):
        self.cfg = cfg or IAConfig()
        self.m = ModelRegistry(self.cfg)

    # ---------------------------
    # 🔶 EMOCIÓN
    # ---------------------------
    def _emotion(self, text: str) -> Tuple[str, float]:
        if not _meaningful(text):
            return ("indefinido", 0.0)

        try:
            out = self.m.emotion()(_trim(text, self.cfg.max_len_models))

            if isinstance(out, list) and len(out):
                pred = out[0]
                raw = str(pred.get("label", "")).lower().strip()
                score = float(pred.get("score", 0.0))
                mapped = _map_emotion_es(raw)
                return mapped, score

            return ("indefinido", 0.0)

        except Exception:
            return ("indefinido", 0.0)

    # ---------------------------
    # 🔶 ESTRÉS
    # ---------------------------
    def _stress(self, text: str) -> Tuple[str, Dict[str,float]]:
        if not _meaningful(text):
            return ("bajo", {"positive":0.0, "neutral":1.0, "negative":0.0})

        try:
            out = self.m.sentiment()(_trim(text, self.cfg.max_len_models))

            if not out:
                return ("medio", {"positive":0.0, "neutral":1.0, "negative":0.0})

            label = out[0]["label"].upper()
            score = float(out[0]["score"])

            if "NEG" in label:
                sent = "negative"
            elif "POS" in label:
                sent = "positive"
            else:
                sent = "neutral"

            dist = {"positive":0.0, "neutral":0.0, "negative":0.0}
            dist[sent] = score

            level = self.cfg.stress_map.get(sent, "medio")
            return level, dist

        except Exception:
            return ("medio", {"positive":0.0, "neutral":1.0, "negative":0.0})

    # ---------------------------
    # 🔶 CATEGORÍAS
    # ---------------------------
    def _categories(self, text: str, top_k: int = 3):
        if not _meaningful(text):
            return []

        try:
            out = self.m.zeroshot()(
                _trim(text, self.cfg.max_len_models),
                self.cfg.categorias,
                multi_label=True
            )

            pairs = [(lab, float(scr)) for lab, scr in zip(out["labels"], out["scores"])
                     if scr >= self.cfg.min_score_categoria]

            pairs.sort(key=lambda x: x[1], reverse=True)

            return pairs[:top_k]

        except Exception:
            return []

    # ---------------------------
    # 🔶 RESUMEN
    # ---------------------------
    def _summary(self, text: str) -> str:
        if not _meaningful(text):
            return ""
        if len(text) <= 140:
            return text

        try:
            out = self.m.summarizer()(
                _trim(text, self.cfg.max_len_summary),
                max_length=80,
                min_length=25,
                do_sample=False
            )
            return out[0]["summary_text"].strip()

        except Exception:
            return text[:160]

    # ============================================================
    # 🔷 API PRINCIPAL
    # ============================================================
    def analyze_comment(self, text: str, meta: dict | None = None) -> Dict[str, Any]:
        meta = meta or {}
        txt = limpiarTextoBasico(text)

        if not _meaningful(txt):
            return {
                "emotion": {"label": "indefinido", "score": 0.0},
                "stress": {"level": "bajo", "sentiment_dist": {"positive": 0, "neutral": 1, "negative": 0}},
                "categories": [],
                "summary": "",
                "suggestion": "Comentario no informativo.",
                "meta": meta
            }

        emo_label, emo_score = self._emotion(txt)
        stress_level, dist = self._stress(txt)
        cats = self._categories(txt)
        summary = self._summary(txt)

        return {
            "emotion": {"label": emo_label, "score": float(emo_score)},
            "stress": {"level": stress_level, "sentiment_dist": dist},
            "categories": [{"label": c, "score": s} for c, s in cats],
            "summary": summary,
            "suggestion": self._generate_suggestion(stress_level, emo_label, [c for c, _ in cats], txt),
            "meta": meta
        }

    # ============================================================
    # 🔷 GENERADOR DE SUGERENCIAS
    # ============================================================
    def _generate_suggestion(self, stress_level: str, emotion: str, categories: List[str], text: str) -> str:
        text = text.lower()

        # Keywords
        carga = any(w in text for w in ["carga", "presión", "estresado", "mucho trabajo", "agotado", "plazos"])
        recursos = any(w in text for w in ["recursos", "herramientas", "sistema", "equipo", "materiales"])
        jefe = any(w in text for w in ["jefe", "supervisor", "líder", "manager", "gerente"])
        comunicacion = "comunicación" in text
        conflicto = any(w in text for w in ["conflicto", "pelea", "problema", "discusión"])
        tiempo = any(w in text for w in ["tiempo", "horas", "horario"])
        
        # --- ALTO ESTRÉS ---
        if stress_level == "alto":
            if carga or "sobrecarga laboral" in categories:
                return "Se recomienda una reunión inmediata para revisar la carga laboral, redistribuir tareas y ajustar plazos."
            if recursos or "recursos insuficientes" in categories:
                return "Revisar disponibilidad de herramientas o personal. Evaluar apoyo temporal o reasignación de recursos."
            if jefe:
                return "Sugerencia: reunión con el supervisor para revisar expectativas y mejorar comunicación."
            if conflicto:
                return "Se recomienda una intervención de RRHH para resolver conflictos internos."
            if emotion in ["miedo", "tristeza"]:
                return "Se sugiere acompañamiento emocional y seguimiento cercano del caso."
            return "Plan de acción urgente: reunión 1:1, revisión de causas de estrés y seguimiento semanal."

        # --- ESTRÉS MEDIO ---
        if stress_level == "medio":
            if comunicacion:
                return "Mejorar canales de comunicación. Establecer reuniones periódicas para evitar malentendidos."
            if tiempo:
                return "Revisar distribución del tiempo y prioridades. Posible capacitación en gestión del tiempo."
            if recursos:
                return "Analizar si existen recursos suficientes para realizar el trabajo adecuadamente."
            return "Monitoreo recomendado para evitar escalamiento a alto estrés."

        # --- ESTRÉS BAJO ---
        if stress_level == "bajo":
            if emotion in ["alegría", "sorpresa"]:
                return "El empleado muestra señales positivas. Reforzar prácticas actuales."
            if "motivación" in categories:
                return "El empleado está motivado. Considerar nuevos retos o proyectos de crecimiento."
            return "Situación estable. Mantener comunicación abierta."

        return "Se recomienda un seguimiento continuo para promover bienestar y comunicación abierta."

