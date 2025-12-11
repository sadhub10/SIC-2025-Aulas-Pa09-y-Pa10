"""
API principal de CSV AI Analyzer
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uuid
from datetime import datetime

from app.models import (
    AnalysisResult,
    ComparisonRequest,
    ComparisonResult,
    ChatMessage,
    ChatResponse
)
from app.services.csv_analyzer import CSVAnalyzer
from app.services.ai_classifier import AIClassifier
from app.services.chatbot import DataChatbot


# Crear instancia de FastAPI
app = FastAPI(
    title="CSV AI Analyzer API",
    description="API para análisis inteligente de archivos CSV con IA",
    version="1.0.0"
)

# Configurar CORS. para ek fronted 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Almacenamiento en memoria (en producción, usar base de datos)
uploaded_files: Dict[str, Dict[str, Any]] = {}
analysis_results: Dict[str, AnalysisResult] = {}


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "CSV AI Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "upload": "/upload",
            "analyze": "/analyze/{file_id}",
            "compare": "/compare",
            "chat": "/chat"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """
    Sube un archivo CSV y retorna un ID único
    """
    try:
        # Validar que sea un archivo CSV
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Solo se permiten archivos CSV"
            )
        
        # Leer el contenido del archivo
        content = await file.read()
        
        # Generar ID único
        file_id = str(uuid.uuid4())
        
        # Guardar información del archivo
        uploaded_files[file_id] = {
            "filename": file.filename,
            "content": content,
            "upload_date": datetime.now(),
            "size": len(content)
        }
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "size": len(content),
            "message": "Archivo subido exitosamente"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al subir archivo: {str(e)}"
        )


@app.get("/analyze/{file_id}")
async def analyze_csv(file_id: str):
    """
    Analiza un archivo CSV previamente subido
    """
    try:
        # Verificar que el archivo existe
        if file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        file_info = uploaded_files[file_id]
        
        # Inicializar analizador
        analyzer = CSVAnalyzer()
        
        # Cargar y analizar CSV
        df = analyzer.load_csv(file_info["content"], file_info["filename"])
        column_info = analyzer.analyze_columns()
        summary_stats = analyzer.get_summary_statistics()
        visualizations = analyzer.generate_visualizations()
        data_preview = analyzer.get_data_preview(n_rows=10)
        
        # Preparar resumen para IA
        csv_summary = analyzer.prepare_for_ai_analysis()
        
        # Clasificar con IA
        classifier = AIClassifier()
        classification = classifier.classify_csv(csv_summary)
        
        # Generar insights con IA
        insights = classifier.generate_insights(csv_summary, classification)
        
        # Crear resultado del análisis
        result = AnalysisResult(
            file_id=file_id,
            metadata=analyzer.metadata,
            classification=classification,
            column_info=column_info,
            summary_statistics=summary_stats,
            insights=insights,
            visualizations=visualizations,
            raw_data_preview=data_preview
        )
        
        # Guardar resultado
        analysis_results[file_id] = result
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al analizar archivo: {str(e)}"
        )


@app.post("/compare")
async def compare_csvs(request: ComparisonRequest):
    """
    Compara múltiples archivos CSV
    """
    try:
        # Verificar que todos los archivos existen
        for file_id in request.file_ids:
            if file_id not in uploaded_files:
                raise HTTPException(
                    status_code=404,
                    detail=f"Archivo {file_id} no encontrado"
                )
        
        # Obtener resúmenes de todos los archivos
        summaries = []
        filenames = []
        
        for file_id in request.file_ids:
            file_info = uploaded_files[file_id]
            
            # Analizar si no está ya analizado
            if file_id not in analysis_results:
                analyzer = CSVAnalyzer()
                analyzer.load_csv(file_info["content"], file_info["filename"])
                summary = analyzer.prepare_for_ai_analysis()
            else:
                # Usar el análisis existente
                result = analysis_results[file_id]
                summary = f"""
                Archivo: {result.metadata.filename}
                Categoría: {result.classification.category}
                Filas: {result.metadata.rows}
                Columnas: {result.metadata.columns}
                """
            
            summaries.append(summary)
            filenames.append(file_info["filename"])
        
        # Comparar con IA
        classifier = AIClassifier()
        comparison_data = classifier.compare_csvs(summaries, filenames)
        
        # Crear resultado de comparación
        result = ComparisonResult(
            files=filenames,
            comparison_type=comparison_data.get("comparison_type", "general"),
            insights=comparison_data.get("insights", []),
            metrics=comparison_data.get("metrics", {}),
            visualizations=[]  # Podrías agregar visualizaciones comparativas
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comparar archivos: {str(e)}"
        )


@app.post("/chat")
async def chat_with_data(message: ChatMessage):
    """
    Chat inteligente sobre los datos del CSV
    """
    try:
        # Verificar que el archivo existe
        if message.file_id not in uploaded_files:
            raise HTTPException(
                status_code=404,
                detail="Archivo no encontrado"
            )
        
        # Obtener el resumen del CSV
        if message.file_id in analysis_results:
            result = analysis_results[message.file_id]
            csv_summary = f"""
            Archivo: {result.metadata.filename}
            Categoría: {result.classification.category}
            Filas: {result.metadata.rows}
            Columnas: {result.metadata.columns}
            
            Columnas: {', '.join(result.metadata.column_names)}
            
            Insights generados:
            {chr(10).join([f'- {insight}' for insight in result.insights])}
            
            Vista previa de datos:
            {result.raw_data_preview[:3]}
            """
        else:
            # Si no está analizado, analizar primero
            file_info = uploaded_files[message.file_id]
            analyzer = CSVAnalyzer()
            analyzer.load_csv(file_info["content"], file_info["filename"])
            csv_summary = analyzer.prepare_for_ai_analysis()
        
        # Inicializar chatbot
        chatbot = DataChatbot()
        
        # Obtener respuesta
        response_data = chatbot.answer_question(
            message.message,
            csv_summary,
            message.conversation_history or []
        )
        
        # Crear respuesta
        response = ChatResponse(
            response=response_data["response"],
            sources=response_data.get("sources", []),
            suggested_questions=response_data.get("suggested_questions", [])
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en chat: {str(e)}"
        )


@app.get("/files")
async def list_files():
    """
    Lista todos los archivos subidos
    """
    files_list = [
        {
            "file_id": file_id,
            "filename": info["filename"],
            "size": info["size"],
            "upload_date": info["upload_date"].isoformat(),
            "analyzed": file_id in analysis_results
        }
        for file_id, info in uploaded_files.items()
    ]
    
    return {"files": files_list, "total": len(files_list)}


@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Elimina un archivo subido
    """
    if file_id not in uploaded_files:
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )
    
    # Eliminar archivo y su análisis
    del uploaded_files[file_id]
    if file_id in analysis_results:
        del analysis_results[file_id]
    
    return {"message": "Archivo eliminado exitosamente"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
