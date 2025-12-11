import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import { TrendingUp, FileText, BarChart3, AlertCircle } from 'lucide-react';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const AnalysisResults = ({ analysis }) => {
  if (!analysis) return null;

  const { metadata, classification, insights, visualizations, summary_statistics } = analysis;
  console.log(analysis)
  // Generar colores para los gráficos
  const generateColors = (count) => {
    const colors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(251, 146, 60, 0.8)',
      'rgba(168, 85, 247, 0.8)',
      'rgba(236, 72, 153, 0.8)',
      'rgba(14, 165, 233, 0.8)',
      'rgba(132, 204, 22, 0.8)',
      'rgba(249, 115, 22, 0.8)',
    ];
    return colors.slice(0, count);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Clasificación */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 dark:from-blue-600 dark:to-blue-700 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold mb-2">
              {metadata.filename}
            </h2>
            <div className="flex items-center space-x-2">
              <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                {classification.category}
              </span>
              {classification.subcategory && (
                <span className="px-3 py-1 bg-white/10 rounded-full text-sm">
                  {classification.subcategory}
                </span>
              )}
              <span className="px-3 py-1 bg-white/10 rounded-full text-sm">
                Confianza: {(classification.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </div>
          <BarChart3 className="h-16 w-16 opacity-50" />
        </div>
        <p className="mt-4 text-blue-100">
          {classification.reasoning}
        </p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Filas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metadata.rows.toLocaleString()}
              </p>
            </div>
            <FileText className="h-8 w-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Columnas</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {metadata.columns}
              </p>
            </div>
            <BarChart3 className="h-8 w-8 text-green-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Tamaño</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {(metadata.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <AlertCircle className="h-8 w-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">Valores Faltantes</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {summary_statistics.missing_values}
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-purple-500" />
          </div>
        </div>
      </div>

      {/* Insights */}
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          💡 Insights Clave
        </h3>
        <ul className="space-y-3">
          {insights.map((insight, index) => (
            <li key={index} className="flex items-start space-x-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 flex items-center justify-center text-sm font-medium">
                {index + 1}
              </span>
              <span className="text-gray-700 dark:text-gray-300">{insight}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Visualizaciones */}
      {visualizations && visualizations.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {visualizations.map((viz, index) => (
            <div key={index} className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
              <h4 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                {viz.title}
              </h4>
              <div className="h-64">
                {viz.type === 'bar' && (
                  <Bar
                    data={{
                      labels: viz.data.labels,
                      datasets: [{
                        label: viz.column,
                        data: viz.data.values,
                        backgroundColor: generateColors(viz.data.values.length),
                      }],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                    }}
                  />
                )}
                {viz.type === 'pie' && (
                  <Pie
                    data={{
                      labels: viz.data.labels,
                      datasets: [{
                        data: viz.data.values,
                        backgroundColor: generateColors(viz.data.values.length),
                      }],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                    }}
                  />
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Análisis sugeridos */}
      {classification.suggested_analyses && classification.suggested_analyses.length > 0 && (
        <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-amber-900 dark:text-amber-100 mb-3">
            📊 Análisis Sugeridos
          </h3>
          <ul className="space-y-2">
            {classification.suggested_analyses.map((analysis, index) => (
              <li key={index} className="flex items-center space-x-2 text-amber-800 dark:text-amber-200">
                <span className="text-amber-500 dark:text-amber-400">•</span>
                <span>{analysis}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
