import React, { useState } from 'react';
import { PdfAnalysisResponse } from '../../types/api';
import PDFUploader from './PDFUploader';
import AnalysisResults from './AnalysisResults';

interface PDFAnalysisContainerProps {
  projectId: number;
}

const PDFAnalysisContainer: React.FC<PDFAnalysisContainerProps> = ({ projectId }) => {
  const [analysisResult, setAnalysisResult] = useState<PdfAnalysisResponse | null>(null);

  const handleAnalysisComplete = (result: PdfAnalysisResponse) => {
    setAnalysisResult(result);
  };

  return (
    <div className="space-y-6">
      <PDFUploader projectId={projectId} onAnalysisComplete={handleAnalysisComplete} />
      
      {analysisResult && (
        <AnalysisResults
          tasks={analysisResult.tasks}
          totalEstimatedHours={analysisResult.total_estimated_hours}
          riskFactors={analysisResult.risk_factors}
          documentAnalysis={{
            type: analysisResult.document_analysis.type,
            context: analysisResult.document_analysis.context,
            client_type: analysisResult.document_analysis.client_type,
            complexity_level: analysisResult.document_analysis.complexity_level,
            clarity_score: analysisResult.document_analysis.clarity_score
          }}
          confidenceAnalysis={{
            overall_confidence: analysisResult.confidence_analysis.overall_confidence,
            rationale: analysisResult.confidence_analysis.rationale,
            improvement_suggestions: analysisResult.confidence_analysis.improvement_suggestions,
            accuracy_factors: analysisResult.confidence_analysis.accuracy_factors
          }}
        />
      )}
    </div>
  );
};

export default PDFAnalysisContainer;
