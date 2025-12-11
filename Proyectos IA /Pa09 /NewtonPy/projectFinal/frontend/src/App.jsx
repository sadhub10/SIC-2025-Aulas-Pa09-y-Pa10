import React, { useState } from 'react';
import { Upload, FileText, BarChart3, MessageSquare, Loader, CheckCircle, XCircle } from 'lucide-react';
import FileUpload from './components/FileUpload';
import AnalysisResults from './components/AnalysisResults';
import Chatbot from './components/Chatbot';
import apiService from './services/api';
import './index.css';

function App() {
  const [currentStep, setCurrentStep] = useState('upload');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadedFileIds, setUploadedFileIds] = useState([]);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState([]);
  const [activeTab, setActiveTab] = useState('results');
  const [error, setError] = useState(null);

  const handleFilesSelected = (files) => {
    setSelectedFiles(files);
    setError(null);
  };

  const handleUploadAndAnalyze = async () => {
    if (selectedFiles.length === 0) {
      setError('Por favor, selecciona al menos un archivo');
      return;
    }

    setIsUploading(true);
    setCurrentStep('analyzing');
    setUploadStatus([]);
    setError(null);
    const fileIds = [];

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        
        setUploadStatus(prev => [...prev, {
          name: file.name,
          status: 'uploading',
          message: 'Subiendo...'
        }]);

        try {
          // Subir archivo
          console.log('Subiendo archivo:', file.name);
          const uploadResult = await apiService.uploadCSV(file);
          console.log('Archivo subido:', uploadResult);
          
          const fileId = uploadResult.file_id;
          fileIds.push(fileId);

          setUploadStatus(prev => prev.map(item => 
            item.name === file.name 
              ? { ...item, status: 'analyzing', message: 'Analizando con IA...' }
              : item
          ));

          // Analizar el archivo
          console.log('Analizando archivo:', fileId);
          const analysisResult = await apiService.analyzeCSV(fileId);
          console.log('Análisis completado:', analysisResult);

          setUploadStatus(prev => prev.map(item => 
            item.name === file.name 
              ? { ...item, status: 'complete', message: 'Completado', data: analysisResult }
              : item
          ));

          // Si es el primer archivo, mostrarlo
          if (i === 0) {
            setCurrentAnalysis(analysisResult);
          }
        } catch (error) {
          console.error('Error procesando archivo:', error);
          setUploadStatus(prev => prev.map(item => 
            item.name === file.name 
              ? { ...item, status: 'error', message: error.response?.data?.detail || error.message }
              : item
          ));
        }
      }

      setUploadedFileIds(fileIds);
      
      // Solo cambiar a results si hay al menos un análisis exitoso
      const hasSuccess = uploadStatus.some(s => s.status === 'complete');
      if (hasSuccess || currentAnalysis) {
        setCurrentStep('results');
      } else {
        setError('No se pudo analizar ningún archivo');
        setCurrentStep('upload');
      }
    } catch (error) {
      console.error('Error general:', error);
      setError(`Error: ${error.message}`);
      setCurrentStep('upload');
    } finally {
      setIsUploading(false);
    }
  };

  const handleSelectAnalysis = (analysisData) => {
    setCurrentAnalysis(analysisData);
    setActiveTab('results');
  };

  const handleReset = () => {
    setCurrentStep('upload');
    setSelectedFiles([]);
    setUploadedFileIds([]);
    setCurrentAnalysis(null);
    setUploadStatus([]);
    setActiveTab('results');
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">CSV AI Analyzer</h1>
                <p className="text-sm text-blue-200">Análisis Inteligente con IA</p>
              </div>
            </div>
            
            {currentStep === 'results' && (
              <button
                onClick={handleReset}
                className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                Nuevo Análisis
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="max-w-2xl mx-auto mb-4 p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {currentStep === 'upload' && (
          <div className="max-w-2xl mx-auto animate-fade-in">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">Sube tus archivos CSV</h2>
              <p className="text-blue-200">
                La IA detectará automáticamente el tipo de datos y realizará un análisis completo
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
              <FileUpload onFilesSelected={handleFilesSelected} maxFiles={5} />

              {selectedFiles.length > 0 && (
                <button
                  onClick={handleUploadAndAnalyze}
                  disabled={isUploading}
                  className="w-full mt-6 px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  <Upload className="h-5 w-5" />
                  <span>Subir y Analizar</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <FileText className="h-8 w-8 text-blue-400 mb-2" />
                <h3 className="text-white font-semibold mb-1">Detección Automática</h3>
                <p className="text-blue-200 text-sm">Identifica el tipo de datos automáticamente</p>
              </div>
              
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <BarChart3 className="h-8 w-8 text-green-400 mb-2" />
                <h3 className="text-white font-semibold mb-1">Análisis Profundo</h3>
                <p className="text-blue-200 text-sm">Insights y visualizaciones generadas con IA</p>
              </div>
              
              <div className="bg-white/5 backdrop-blur-sm rounded-lg p-4 border border-white/10">
                <MessageSquare className="h-8 w-8 text-purple-400 mb-2" />
                <h3 className="text-white font-semibold mb-1">Chat Inteligente</h3>
                <p className="text-blue-200 text-sm">Pregunta sobre tus datos en lenguaje natural</p>
              </div>
            </div>
          </div>
        )}

        {currentStep === 'analyzing' && (
          <div className="max-w-2xl mx-auto animate-fade-in">
            <div className="text-center mb-8">
              <Loader className="h-16 w-16 text-blue-400 mx-auto mb-4 animate-spin" />
              <h2 className="text-2xl font-bold text-white mb-2">Analizando archivos...</h2>
              <p className="text-blue-200">La IA está procesando tus datos</p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20 space-y-4">
              {uploadStatus.map((status, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {status.status === 'complete' && <CheckCircle className="h-5 w-5 text-green-400" />}
                    {status.status === 'error' && <XCircle className="h-5 w-5 text-red-400" />}
                    {(status.status === 'uploading' || status.status === 'analyzing') && (
                      <Loader className="h-5 w-5 text-blue-400 animate-spin" />
                    )}
                    
                    <div>
                      <p className="text-white font-medium">{status.name}</p>
                      <p className="text-sm text-blue-200">{status.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentStep === 'results' && currentAnalysis && (
          <div className="animate-fade-in">
            {uploadStatus.length > 1 && (
              <div className="mb-6 bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
                <p className="text-white font-medium mb-3">Archivos analizados:</p>
                <div className="flex flex-wrap gap-2">
                  {uploadStatus.filter(s => s.status === 'complete').map((status, index) => (
                    <button
                      key={index}
                      onClick={() => handleSelectAnalysis(status.data)}
                      className={`px-4 py-2 rounded-lg transition-colors ${
                        currentAnalysis.file_id === status.data.file_id
                          ? 'bg-blue-500 text-white'
                          : 'bg-white/10 text-blue-200 hover:bg-white/20'
                      }`}
                    >
                      {status.name}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div className="mb-6 bg-white/10 backdrop-blur-sm rounded-lg p-2 border border-white/20 inline-flex">
              <button
                onClick={() => setActiveTab('results')}
                className={`px-6 py-2 rounded-lg transition-colors ${
                  activeTab === 'results'
                    ? 'bg-white text-blue-900 font-semibold'
                    : 'text-blue-200 hover:text-white'
                }`}
              >
                <BarChart3 className="inline h-5 w-5 mr-2" />
                Resultados
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`px-6 py-2 rounded-lg transition-colors ${
                  activeTab === 'chat'
                    ? 'bg-white text-blue-900 font-semibold'
                    : 'text-blue-200 hover:text-white'
                }`}
              >
                <MessageSquare className="inline h-5 w-5 mr-2" />
                Chat
              </button>
            </div>

            {activeTab === 'results' && <AnalysisResults analysis={currentAnalysis} />}
            {activeTab === 'chat' && (
              <Chatbot 
                fileId={currentAnalysis.file_id} 
                fileName={currentAnalysis.metadata.filename}
              />
            )}
          </div>
        )}
      </main>

      <footer className="mt-16 py-6 border-t border-white/10">
        <div className="container mx-auto px-4 text-center text-blue-200 text-sm">
          <p>CSV AI Analyzer - Powered by Newton.py</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
