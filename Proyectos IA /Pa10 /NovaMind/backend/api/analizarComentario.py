# api/analizarComentario.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.config.database import get_db
from backend.ia.iaCore import NLPAnalyzer
from backend.core.coreServices import guardarAnalisis

router = APIRouter(tags=["Analisis"])

analyzer = NLPAnalyzer()

class AnalizarPayload(BaseModel):
    comentario: str
    meta: dict | None = None
@router.post("/analizar-comentario/")
def analizarComentario(payload: AnalizarPayload, db: Session = Depends(get_db)):

    try:
        result = analyzer.analyze_comment(payload.comentario, meta=payload.meta or {})

        print("🔥🔥🔥 ESTOY EJECUTANDO EL ENDPOINT CORRECTO 🔥🔥🔥")
        print(result)

        emotion_label = result["emotion"]["label"]
        emotion_score = float(result["emotion"]["score"])
        result["emotion"]["score"] = emotion_score

        row = guardarAnalisis(db, result)
        return {"status": "ok", "id": row.id, "resultado": result}

    except Exception as e:
        print("❌ ERROR EN ENDPOINT /analizar-comentario/")
        print(str(e))
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

