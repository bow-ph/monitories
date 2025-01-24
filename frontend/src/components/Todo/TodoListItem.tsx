import React, { useState } from 'react';
import { TodoItem } from '../../types/todo';

interface TodoListItemProps {
  item: TodoItem;
  onUpdate: (updates: Partial<TodoItem>) => void;
}

const TodoListItem: React.FC<TodoListItemProps> = ({ item, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [actualHours, setActualHours] = useState(item.actual_hours?.toString() || '');

  const handleStatusChange = (status: TodoItem['status']) => {
    onUpdate({ status });
  };

  const handleActualHoursSubmit = () => {
    const hours = parseFloat(actualHours);
    if (!isNaN(hours) && hours >= 0) {
      onUpdate({ actual_hours: hours });
    }
    setIsEditing(false);
  };

  return (
    <div className="bg-white shadow rounded-lg p-4 border border-gray-200">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <select
              value={item.status}
              onChange={(e) => handleStatusChange(e.target.value as TodoItem['status'])}
              className="text-sm border-gray-300 rounded-md"
            >
              <option value="pending">Ausstehend</option>
              <option value="in_progress">In Bearbeitung</option>
              <option value="completed">Abgeschlossen</option>
            </select>
            <span className={`px-2 py-1 text-xs rounded-full ${
              item.priority === 'high' ? 'bg-red-100 text-red-800' :
              item.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {item.priority === 'high' ? 'Hoch' :
               item.priority === 'medium' ? 'Mittel' : 'Niedrig'}
            </span>
          </div>
          <p className="mt-2 text-sm text-gray-900">{item.description}</p>
          <div className="mt-1 text-sm text-gray-500">
            <span>Geschätzt: {item.estimated_hours}h</span>
            {item.actual_hours !== undefined && (
              <span className="ml-2">Tatsächlich: {item.actual_hours}h</span>
            )}
          </div>
        </div>
        <div className="ml-4 flex items-center space-x-2">
          {isEditing ? (
            <div className="flex items-center space-x-2">
              <input
                type="number"
                value={actualHours}
                onChange={(e) => setActualHours(e.target.value)}
                className="w-20 text-sm border-gray-300 rounded-md"
                min="0"
                step="0.5"
              />
              <button
                onClick={handleActualHoursSubmit}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Speichern
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsEditing(true)}
              className="text-sm text-gray-600 hover:text-gray-800"
            >
              Zeit erfassen
            </button>
          )}
        </div>
      </div>
      {item.confidence_rationale && (
        <div className="mt-2 text-sm text-gray-500">
          <span className="font-medium">Konfidenz: </span>
          {item.confidence_rationale}
        </div>
      )}
    </div>
  );
};

export default TodoListItem;
