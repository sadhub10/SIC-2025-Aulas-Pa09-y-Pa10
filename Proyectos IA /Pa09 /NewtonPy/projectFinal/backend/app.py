from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import json

# Importar servicios PROPIOS (sin Anthropic)
from services.csv_detector_ml import CSVDetectorML
from services.data_analyzer import DataAnalyzer
from services.statistical_chatbot import StatisticalChatbot
from services.comparison_engine import ComparisonEngine

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Instancias de servicios (SIN ANTHROPIC)
print("Inicializando servicios de IA propios...")
csv_detector = CSVDetectorML()  # Usa red neuronal propia
data_analyzer = DataAnalyzer()
ai_chatbot = StatisticalChatbot()  # Usa análisis estadístico
comparison_engine = ComparisonEngine()
print("✓ Servicios inicializados correctamente")

# Almacenamiento temporal de archivos analizados
analyzed_files = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'message': 'CSV AI Analyzer API is running',
        'ai_engine': 'Neural Network + Statistical Analysis (No external APIs)',
        'neural_network_trained': csv_detector.neural_classifier.is_trained
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Subir y analizar archivo CSV con IA propia"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only CSV, XLSX, XLS allowed'}), 400
        
        # Guardar archivo
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        print(f"\nAnalizando archivo: {filename}")
        
        # Detectar tipo de CSV con RED NEURONAL + LIMPIAR DATOS
        print("  → Clasificando con red neuronal...")
        detection_result = csv_detector.detect_csv_type(filepath)
        print(f"  → Categoría detectada: {detection_result['category']} (confianza: {detection_result['confidence']:.2%})")
        print(f"  → Método: {detection_result.get('method', 'unknown')}")
        
        # Analizar datos
        print("  → Analizando estadísticas...")
        analysis_result = data_analyzer.analyze(filepath, detection_result)
        print("  ✓ Análisis completado")
        
        # Guardar en memoria para futuras consultas
        file_id = filename.replace('.', '_')
        analyzed_files[file_id] = {
            'filename': filename,
            'filepath': filepath,
            'detection': detection_result,
            'analysis': analysis_result
        }
        
        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': filename,
            'detection': detection_result,
            'analysis': analysis_result,
            'ai_info': {
                'classification_method': detection_result.get('method', 'unknown'),
                'data_cleaned': True,
                'neural_network_used': detection_result.get('method') == 'neural_network'
            }
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Obtener lista de archivos analizados"""
    files_list = []
    for file_id, data in analyzed_files.items():
        files_list.append({
            'file_id': file_id,
            'filename': data['filename'],
            'type': data['detection']['category'],
            'confidence': data['detection']['confidence'],
            'data_quality': data['detection'].get('data_quality', {}).get('after_cleaning', {}).get('overall_score', 'N/A')
        })
    return jsonify({'files': files_list})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chatbot estadístico para consultar sobre los datos (SIN APIs EXTERNAS)"""
    try:
        data = request.json
        file_ids = data.get('file_ids', [])
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Preparar contexto de archivos
        context_files = []
        for file_id in file_ids:
            if file_id in analyzed_files:
                context_files.append(analyzed_files[file_id])
        
        if not context_files:
            return jsonify({'error': 'No valid files provided'}), 400
        
        print(f"\n Pregunta: {question}")
        print(f"   Archivos: {len(context_files)}")
        
        # Obtener respuesta del chatbot ESTADÍSTICO (sin APIs)
        response = ai_chatbot.ask(question, context_files)
        print(f"   Respuesta generada")
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': response,
            'ai_info': {
                'engine': 'Statistical Analysis',
                'uses_external_api': False
            }
        })
    
    except Exception as e:
        print(f"Error en chat: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare', methods=['POST'])
def compare_files():
    """Comparar múltiples archivos del mismo tipo"""
    try:
        data = request.json
        file_ids = data.get('file_ids', [])
        
        if len(file_ids) < 2:
            return jsonify({'error': 'Need at least 2 files to compare'}), 400
        
        # Obtener archivos
        files_to_compare = []
        for file_id in file_ids:
            if file_id in analyzed_files:
                files_to_compare.append(analyzed_files[file_id])
        
        if len(files_to_compare) < 2:
            return jsonify({'error': 'Invalid file IDs provided'}), 400
        
        print(f"\nComparando {len(files_to_compare)} archivos...")
        
        # Realizar comparación
        comparison = comparison_engine.compare(files_to_compare)
        print("   ✓ Comparación completada")
        
        return jsonify({
            'success': True,
            'comparison': comparison
        })
    
    except Exception as e:
        print(f"Error en comparación: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/file/<file_id>', methods=['GET'])
def get_file_details(file_id):
    """Obtener detalles de un archivo específico"""
    if file_id not in analyzed_files:
        return jsonify({'error': 'File not found'}), 404
    
    return jsonify({
        'success': True,
        'data': analyzed_files[file_id]
    })

@app.route('/api/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Eliminar archivo"""
    if file_id not in analyzed_files:
        return jsonify({'error': 'File not found'}), 404
    
    try:
        filepath = analyzed_files[file_id]['filepath']
        if os.path.exists(filepath):
            os.remove(filepath)
        del analyzed_files[file_id]
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train-neural-network', methods=['POST'])
def train_neural_network():
    """
    Endpoint para re-entrenar la red neuronal con más datos
    """
    try:
        data = request.json
        n_samples = data.get('n_samples', 1000)
        
        print(f"\nRe-entrenando red neuronal con {n_samples} muestras...")
        history = csv_detector.neural_classifier.train_with_synthetic_data(n_samples)
        
        return jsonify({
            'success': True,
            'message': 'Neural network retrained successfully',
            'final_accuracy': float(history.history['accuracy'][-1]),
            'val_accuracy': float(history.history['val_accuracy'][-1])
        })
    
    except Exception as e:
        print(f"Error entrenando red: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':

    print("CSV AI ANALYZER - Servidor iniciado")

    print("Motor de IA: Red Neuronal Propia + Análisis Estadístico")
    print("Sin dependencias de APIs externas (Anthropic eliminado)")
    print("Limpieza automática de datos con ML")
  
    app.run(debug=True, port=5000, host='0.0.0.0')
