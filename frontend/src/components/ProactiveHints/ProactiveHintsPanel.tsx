import React from 'react';
import { ProactiveHintsResponse } from '../../types/api';

interface ProactiveHintsPanelProps {
  data: ProactiveHintsResponse;
}

const ProactiveHintsPanel: React.FC<ProactiveHintsPanelProps> = ({ data }) => {
  const getRiskLevelColor = (level: 'low' | 'medium' | 'high') => {
    switch (level) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Financial Impact */}
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Finanzielle Auswirkungen</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Risiko Level</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(data.financial_impact.risk_level)}`}>
                {data.financial_impact.risk_level.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Potenzielle Kostenüberschreitung</span>
              <span className="text-sm font-medium">{data.financial_impact.potential_cost_overrun}€</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Konfidenz</span>
              <span className="text-sm font-medium">{Math.round(data.financial_impact.confidence * 100)}%</span>
            </div>
          </div>
        </div>

        {/* Time Impact */}
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Zeitliche Auswirkungen</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Risiko Level</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getRiskLevelColor(data.time_impact.risk_level)}`}>
                {data.time_impact.risk_level.toUpperCase()}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Potenzielle Verzögerung</span>
              <span className="text-sm font-medium">{data.time_impact.potential_delay_hours} Stunden</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-500">Konfidenz</span>
              <span className="text-sm font-medium">{Math.round(data.time_impact.confidence * 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white shadow rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Empfehlungen</h3>
        <div className="space-y-3">
          {data.recommendations.map((rec, index) => (
            <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-md">
              <div className={`flex-shrink-0 w-2 h-2 mt-2 rounded-full ${
                rec.priority === 'high' ? 'bg-red-500' :
                rec.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
              }`} />
              <div>
                <p className="text-sm text-gray-900">{rec.description}</p>
                <p className="text-xs text-gray-500 mt-1">
                  Typ: {rec.type.charAt(0).toUpperCase() + rec.type.slice(1)}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Time Validation */}
      {data.time_validation && (
        <div className="bg-white shadow rounded-lg p-4">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Zeitvalidierung</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Qualität der Schätzung:</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                data.time_validation.overall_assessment.estimation_quality === 'good' ? 'bg-green-100 text-green-800' :
                data.time_validation.overall_assessment.estimation_quality === 'needs_review' ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800'
              }`}>
                {data.time_validation.overall_assessment.estimation_quality.toUpperCase()}
              </span>
            </div>
            
            <div className="space-y-2">
              {data.time_validation.overall_assessment.suggestions.map((suggestion, index) => (
                <p key={index} className="text-sm text-gray-600">• {suggestion}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProactiveHintsPanel;
