import React from 'react';
import { Task } from '../../types/api';

interface AnalysisResultsProps {
  tasks: Task[];
  totalEstimatedHours: number;
  riskFactors: string[];
  documentAnalysis: {
    type: string;
    context: string;
    client_type: string;
    complexity_level: string;
    clarity_score: number;
  };
  confidenceAnalysis: {
    overall_confidence: number;
    rationale: string;
    improvement_suggestions: string[];
    accuracy_factors: {
      document_clarity: number;
      technical_complexity: number;
      dependency_risk: number;
      client_input_risk: number;
    };
  };
}

const AnalysisResults: React.FC<AnalysisResultsProps> = ({
  tasks,
  totalEstimatedHours,
  riskFactors,
  confidenceAnalysis,
}) => {
  return (
    <div className="space-y-6">
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Dokumentanalyse</h3>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-sm font-medium text-gray-500">Dokumenttyp</p>
            <p className="mt-1 text-sm text-gray-900 capitalize">{documentAnalysis.type}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Kundentyp</p>
            <p className="mt-1 text-sm text-gray-900 capitalize">{documentAnalysis.client_type}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Komplexität</p>
            <p className="mt-1 text-sm text-gray-900 capitalize">{documentAnalysis.complexity_level}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Dokumentklarheit</p>
            <div className="mt-1 flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    documentAnalysis.clarity_score >= 0.8
                      ? 'bg-green-500'
                      : documentAnalysis.clarity_score >= 0.6
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.round(documentAnalysis.clarity_score * 100)}%` }}
                />
              </div>
              <span className="ml-2 text-sm text-gray-600">
                {Math.round(documentAnalysis.clarity_score * 100)}%
              </span>
            </div>
          </div>
        </div>
        <p className="text-sm text-gray-600">{documentAnalysis.context}</p>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Analyseergebnisse</h3>
          <p className="text-sm text-gray-500">
            Geschätzte Gesamtzeit: <span className="font-medium">{totalEstimatedHours} Stunden</span>
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div>
            <p className="text-sm font-medium text-gray-500">Gesamtvertrauen</p>
            <div className="mt-1 flex items-center">
              <div className="w-24 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    confidenceAnalysis.overall_confidence >= 0.8
                      ? 'bg-green-500'
                      : confidenceAnalysis.overall_confidence >= 0.6
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.round(confidenceAnalysis.overall_confidence * 100)}%` }}
                />
              </div>
              <span className="ml-2 text-sm text-gray-600">
                {Math.round(confidenceAnalysis.overall_confidence * 100)}%
              </span>
            </div>
          </div>
          {Object.entries(confidenceAnalysis.accuracy_factors).map(([key, value]) => (
            <div key={key}>
              <p className="text-sm font-medium text-gray-500 capitalize">
                {key.replace(/_/g, ' ')}
              </p>
              <div className="mt-1 flex items-center">
                <div className="w-24 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      value >= 0.8
                        ? 'bg-green-500'
                        : value >= 0.6
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.round(value * 100)}%` }}
                  />
                </div>
                <span className="ml-2 text-sm text-gray-600">
                  {Math.round(value * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-4">
          <h4 className="text-md font-medium text-gray-900">Aufgaben</h4>
          {tasks.map((task, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-lg p-4 border border-gray-200"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center">
                    <p className="text-sm font-medium text-gray-900">
                      {task.description}
                    </p>
                    {task.requires_client_input && (
                      <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
                        Kundeninput erforderlich
                      </span>
                    )}
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <p className="text-sm text-gray-500">
                      Geschätzte Zeit: {task.estimated_hours} Stunden
                    </p>
                    <p className="text-sm text-gray-500">
                      Komplexität: <span className="capitalize">{task.complexity || 'medium'}</span>
                    </p>
                  </div>
                  {task.technical_requirements && task.technical_requirements.length > 0 && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">Technische Anforderungen:</p>
                      <ul className="mt-1 list-disc list-inside text-sm text-gray-600">
                        {task.technical_requirements.map((req, i) => (
                          <li key={i}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {task.confidence_rationale && (
                    <p className="text-sm text-gray-600 mt-2 italic">
                      {task.confidence_rationale}
                    </p>
                  )}
                </div>
                <div className="ml-4">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                      ${
                        task.confidence_score >= 0.8
                          ? 'bg-green-100 text-green-800'
                          : task.confidence_score >= 0.6
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                  >
                    {Math.round(task.confidence_score * 100)}% Konfidenz
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {riskFactors.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Risikofaktoren</h4>
          <ul className="space-y-2">
            {riskFactors.map((risk, index) => (
              <li key={index} className="flex items-start">
                <span className="flex-shrink-0 h-5 w-5 text-yellow-500">
                  ⚠️
                </span>
                <span className="ml-2 text-sm text-gray-600">{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {confidenceAnalysis.improvement_suggestions.length > 0 && (
        <div className="bg-white shadow rounded-lg p-6">
          <h4 className="text-md font-medium text-gray-900 mb-4">Verbesserungsvorschläge</h4>
          <div className="space-y-3">
            {confidenceAnalysis.improvement_suggestions.map((suggestion, index) => (
              <div key={index} className="flex items-start">
                <span className="flex-shrink-0 h-5 w-5 text-blue-500">
                  💡
                </span>
                <p className="ml-2 text-sm text-gray-600">{suggestion}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;
