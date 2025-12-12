from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import uvicorn

# Módulos Principales
# from extractor import extract_text_from_pdf
# MODELOS LOCALES REEMPLAZADOS POR GEMINI
from gemini_service import GeminiService
from embeddings import EmbeddingGenerator
from vector_store import VectorStore

app = FastAPI(title="Document AI API - Gemini Powered")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Servicios
print("Inicializando Servicios de IA...")
# 1. Gemini (Motor de Razonamiento)
gemini_service = GeminiService()

# 2. Embeddings (Motor de Búsqueda - Local es más rápido/barato para vectores)
embedder = EmbeddingGenerator()

# 3. Almacén Vectorial
vector_store = VectorStore()
print("Servicios de IA Inicializados (Gemini + Vectores Locales).")

# Asegurar directorios
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/analyze")
async def analyze_document(file: UploadFile = File(...)):
    try:
        # 0. Verificar Duplicados
        if vector_store.check_file_exists(file.filename):
             raise HTTPException(status_code=400, detail=f"El archivo '{file.filename}' ya existe en el sistema.")
             
        # 1. Guardar Archivo
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split(".")[-1]
        filename = f"{file_id}.{file_ext}"
        file_path = f"data/uploads/{filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1. PIPELINE DE ANÁLISIS (Gemini Multimodal: OCR + Clasificación + Resumen)
        
        # Detectar Tipo MIME
        mime_type = file.content_type
        if not mime_type or mime_type == "application/octet-stream":
             if file_ext in ["jpg", "jpeg"]: mime_type = "image/jpeg"
             elif file_ext == "png": mime_type = "image/png"
             elif file_ext == "webp": mime_type = "image/webp"
             else: mime_type = "application/pdf"
             
        print(f"Enviando {filename} ({mime_type}) a Gemini para Análisis Completo...")
        
        analysis_result = gemini_service.analyze_file(file_path, mime_type=mime_type)
        
        # Verificar si falló
        if "error" in analysis_result:
             # ¿Fallback? O solo retornar error
             pass 

        text = analysis_result.get("full_text_extracted", "")
        if not text:
             text = "Texto no encontrado por Gemini."
             
        classification = analysis_result.get("classification", {})
        category = classification.get("category", "Uncategorized")
        score = classification.get("confidence", 0.0)
        
        summary = analysis_result.get("summary", "Resumen no disponible.")
        
        # 2. Almacenar Resultado (Embeddings siguen siendo locales)
        print("Generando embeddings (Local)...")
        
        # GUARDAR TEXTO COMPLETO EN DISCO para Contexto de Búsqueda Semántica
        txt_path = f"data/uploads/{file_id}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
            
        # El generador de embeddings necesita texto. Gemini provee texto de alta calidad ahora.
        vector = embedder.generate(text)
        
        # 3. Almacenar en FAISS
        metadata = {
            "id": file_id,
            "filename": file.filename,
            "path": file_path,
            "category": category,
            "summary": summary,
            "deleted": False
        }
        vector_store.add_document(vector, metadata)
        
        return {
            "filename": file.filename,
            "category": category,
            "category_score": score,
            "summary": summary,
            "text_preview": text[:500] + "...",
            "full_text": text
        }

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

@app.get("/search")
async def search_documents(query: str):
    try:
        # La búsqueda es Híbrida + Rerank con Gemini:
        # 1. Embed query (Modelo Local)
        query_embedding = embedder.generate(query)
        
        # 2. Búsqueda en FAISS + Coincidencia de Palabras Clave
        # Obtener más candidatos (k=15) para dar a Gemini un buen grupo para filtrar
        raw_candidates = vector_store.search(query_embedding, query_text=query, k=15)
        
        # 3. Reranking Semántico con Gemini
        # Pedir a Gemini que filtre el ruido y encuentre las coincidencias verdaderas
        refined_results = gemini_service.semantic_search_rerank(query, raw_candidates)
        
        return refined_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def get_documents():
    try:
        return vector_store.list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    try:
        success = vector_store.delete_document(doc_id)
        if not success:
             raise HTTPException(status_code=404, detail="Archivo no encontrado")
        return {"status": "eliminado", "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents")
async def delete_all_documents():
    try:
        vector_store.clear_all()
        return {"status": "todos_eliminados"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
