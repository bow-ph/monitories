import React from 'react';
import { useParams } from 'react-router-dom';
import PDFAnalysisContainer from '../components/PDFAnalysis/PDFAnalysisContainer';
import ProjectScheduling from '../components/Project/ProjectScheduling';

const ProjectView: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const numericProjectId = parseInt(projectId || '0', 10);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="space-y-8">
        <PDFAnalysisContainer projectId={numericProjectId} />
        <ProjectScheduling projectId={numericProjectId} />
      </div>
    </div>
  );
};

export default ProjectView;
