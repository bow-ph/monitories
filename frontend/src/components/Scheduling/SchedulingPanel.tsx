import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import { Schedule, ScheduleValidation } from '../../types/scheduling';

interface SchedulingPanelProps {
  projectId: number;
}

const SchedulingPanel: React.FC<SchedulingPanelProps> = ({ projectId }) => {
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [validation, setValidation] = useState<ScheduleValidation | null>(null);

  const { data: scheduleData, isLoading, error } = useQuery({
    queryKey: ['schedule', projectId],
    queryFn: async () => {
      const response = await apiClient.post(`/v1/scheduling/projects/${projectId}/schedule`);
      return response.data;
    },
    enabled: !!projectId
  });

  useEffect(() => {
    if (scheduleData) {
      setSchedule(scheduleData);
      validateSchedule(scheduleData.schedule);
    }
  }, [scheduleData]);

  const validateSchedule = async (scheduleData: Schedule['schedule']) => {
    try {
      const response = await apiClient.post(
        `/v1/scheduling/projects/${projectId}/validate-schedule`,
        { schedule: scheduleData }
      );
      setValidation(response.data);
    } catch (error) {
      console.error('Error validating schedule:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div 
          role="status"
          className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"
          aria-label="Loading"
        >
          <span className="sr-only">Loading...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <p className="text-red-600">Error loading schedule</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Projektplan</h3>
        {validation && !validation.is_valid && (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            Konflikte gefunden
          </span>
        )}
      </div>

      {schedule && (
        <div className="space-y-4">
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Projektstart</dt>
                  <dd className="mt-1 text-sm text-gray-900">{schedule.earliest_start}</dd>
                </div>
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Projektende</dt>
                  <dd className="mt-1 text-sm text-gray-900">{schedule.latest_end}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Gesamtdauer</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {schedule.total_duration_days} Tage
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h4 className="text-base font-medium text-gray-900 mb-4">Zeitplan</h4>
              <div className="space-y-4">
                {schedule.schedule.map((slot, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {slot.description}
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          {slot.date} • {slot.start_time} - {slot.end_time}
                        </p>
                      </div>
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {slot.hours} Stunden
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {validation && (validation.conflicts.length > 0 || validation.warnings.length > 0) && (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h4 className="text-base font-medium text-gray-900 mb-4">
                  Validierungsergebnisse
                </h4>
                
                {validation.conflicts.length > 0 && (
                  <div className="mb-4">
                    <h5 className="text-sm font-medium text-red-800 mb-2">Konflikte</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {validation.conflicts.map((conflict, index) => (
                        <li key={index} className="text-sm text-red-600">
                          {conflict}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {validation.warnings.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-yellow-800 mb-2">Warnungen</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {validation.warnings.map((warning, index) => (
                        <li key={index} className="text-sm text-yellow-600">
                          {warning}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SchedulingPanel;
