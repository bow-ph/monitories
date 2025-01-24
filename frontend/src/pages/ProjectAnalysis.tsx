import { useState } from 'react';
import PDFUploader from '../components/PDFAnalysis/PDFUploader';
import AnalysisResults from '../components/PDFAnalysis/AnalysisResults';
import ProactiveHintsPanel from '../components/ProactiveHints/ProactiveHintsPanel';
import { PdfAnalysisResponse, ProactiveHintsResponse } from '../types/api';
import { useQuery } from '@tanstack/react-query';
import { apiClient, endpoints } from '../api/client';

const ProjectAnalysis = () => {
  const [analysisResults, setAnalysisResults] = useState<PdfAnalysisResponse | null>(null);
  const projectId = 1; // TODO: Get from route params

  const { data: proactiveHints } = useQuery<ProactiveHintsResponse>({
    queryKey: ['proactiveHints', projectId],
    queryFn: async () => {
      const response = await apiClient.get(endpoints.getProactiveHints(projectId));
      return response.data;
    },
    enabled: !!projectId,
  });

  const handleAnalysisComplete = (results: PdfAnalysisResponse) => {
    setAnalysisResults(results);
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">KI-Planung</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">PDF Analyse</h2>
          <PDFUploader projectId={projectId} onAnalysisComplete={handleAnalysisComplete} />
          
          {analysisResults && (
            <div className="mt-8">
              <AnalysisResults
                tasks={analysisResults.tasks}
                totalEstimatedHours={analysisResults.total_estimated_hours}
                riskFactors={analysisResults.risk_factors}
              />
            </div>
          )}
        </div>

        {proactiveHints && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Proaktive Hinweise</h2>
            <ProactiveHintsPanel data={proactiveHints} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectAnalysis;
