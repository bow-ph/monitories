import React from 'react';
import SchedulingPanel from '../Scheduling/SchedulingPanel';

interface ProjectSchedulingProps {
  projectId: number;
}

const ProjectScheduling: React.FC<ProjectSchedulingProps> = ({ projectId }) => {
  return (
    <div className="bg-white shadow sm:rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Projektplanung</h2>
        <SchedulingPanel projectId={projectId} />
      </div>
    </div>
  );
};

export default ProjectScheduling;
