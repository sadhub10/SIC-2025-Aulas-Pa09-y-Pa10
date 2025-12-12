# core/coreServices.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.core.coreModels import AnalisisComentario  # ✔ IMPORT CORRECTO
import logging

logger = logging.getLogger(__name__)

def guardarAnalisis(db: Session, payload: Dict[str, Any]) -> AnalisisComentario:
    stress = payload.get("stress", {})
    sent = stress.get("sentiment_dist", {})
    cats = payload.get("categories", [])

    row = AnalisisComentario(
        comentario     = payload.get("meta", {}).get("comentario_original", "") or payload.get("meta", {}).get("comentario", ""),
        emotion_label  = payload.get("emotion", {}).get("label", ""),
        emotion_score  = payload.get("emotion", {}).get("score", 0.0),
        stress_level   = stress.get("level", "desconocido"),
        sent_pos       = float(sent.get("positive", 0.0) or 0.0),
        sent_neu       = float(sent.get("neutral", 0.0) or 0.0),
        sent_neg       = float(sent.get("negative", 0.0) or 0.0),
        categories     = cats,
        summary        = payload.get("summary", ""),
        suggestion     = payload.get("suggestion", ""),
        departamento   = payload.get("meta", {}).get("departamento", ""),
        equipo         = payload.get("meta", {}).get("equipo", ""),
        fecha          = payload.get("meta", {}).get("fecha", "")
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def guardarAnalisisLote(db: Session, resultados: List[Dict[str, Any]]) -> int:
    count = 0
    for i, r in enumerate(resultados):
        try:
            guardarAnalisis(db, r)
            count += 1
            logger.info(f"Registro {i+1} guardado exitosamente")
        except Exception as e:
            logger.error(f"Error guardando registro {i+1}: {e}")
            logger.error(f"Datos del registro: {r}")
            db.rollback()
    return count

def obtenerHistoricos(db: Session, limit: int = 200) -> List[AnalisisComentario]:
    return db.query(AnalisisComentario).order_by(AnalisisComentario.id.desc()).limit(limit).all()

def obtenerAlertas(db: Session, nivel: str = "alto", limite: int = 50) -> List[AnalisisComentario]:
    return (
        db.query(AnalisisComentario)
        .filter(AnalisisComentario.stress_level == nivel)
        .order_by(AnalisisComentario.id.desc())
        .limit(limite)
        .all()
    )
