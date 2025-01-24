import React from 'react';
import { Task } from '../../types/api';

interface TodoListProps {
  tasks: Task[];
  onStatusChange?: (taskId: number, status: 'pending' | 'in_progress' | 'completed') => void;
}

const TodoList: React.FC<TodoListProps> = ({ tasks, onStatusChange }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Aufgaben</h2>
      </div>
      <div className="divide-y divide-gray-200">
        {tasks.map((task) => (
          <div key={task.id} className="p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{task.description}</p>
                <div className="mt-1 flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    {task.estimated_hours} Stunden geschätzt
                  </span>
                  {task.actual_hours && (
                    <span className="text-sm text-gray-500">
                      • {task.actual_hours} Stunden tatsächlich
                    </span>
                  )}
                </div>
              </div>
              {onStatusChange && task.id && (
                <select
                  value={task.status}
                  onChange={(e) => onStatusChange(task.id!, e.target.value as any)}
                  className={`ml-4 text-sm rounded-full px-2.5 py-0.5 ${getStatusColor(
                    task.status
                  )}`}
                >
                  <option value="pending">Ausstehend</option>
                  <option value="in_progress">In Bearbeitung</option>
                  <option value="completed">Abgeschlossen</option>
                </select>
              )}
            </div>
            <div className="mt-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
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
        ))}
      </div>
    </div>
  );
};

export default TodoList;
