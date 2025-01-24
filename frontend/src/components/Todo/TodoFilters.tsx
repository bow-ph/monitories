import React from 'react';
import { TodoFilter } from '../../types/todo';

interface TodoFiltersProps {
  filters: TodoFilter;
  onChange: (filters: TodoFilter) => void;
}

const TodoFilters: React.FC<TodoFiltersProps> = ({ filters, onChange }) => {
  const handleFilterChange = (key: keyof TodoFilter, value: string | undefined) => {
    onChange({
      ...filters,
      [key]: value === 'all' ? undefined : value,
    });
  };

  return (
    <div className="flex space-x-4 bg-gray-50 p-4 rounded-lg">
      <select
        value={filters.status || 'all'}
        onChange={(e) => handleFilterChange('status', e.target.value)}
        className="text-sm border-gray-300 rounded-md"
      >
        <option value="all">Alle Status</option>
        <option value="pending">Ausstehend</option>
        <option value="in_progress">In Bearbeitung</option>
        <option value="completed">Abgeschlossen</option>
      </select>

      <select
        value={filters.priority || 'all'}
        onChange={(e) => handleFilterChange('priority', e.target.value)}
        className="text-sm border-gray-300 rounded-md"
      >
        <option value="all">Alle Prioritäten</option>
        <option value="high">Hoch</option>
        <option value="medium">Mittel</option>
        <option value="low">Niedrig</option>
      </select>

      <input
        type="date"
        value={filters.start_date || ''}
        onChange={(e) => handleFilterChange('start_date', e.target.value)}
        className="text-sm border-gray-300 rounded-md"
        placeholder="Von"
      />

      <input
        type="date"
        value={filters.end_date || ''}
        onChange={(e) => handleFilterChange('end_date', e.target.value)}
        className="text-sm border-gray-300 rounded-md"
        placeholder="Bis"
      />
    </div>
  );
};

export default TodoFilters;
