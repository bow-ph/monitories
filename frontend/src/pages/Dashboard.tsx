import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import CalendarView from '../components/Calendar/CalendarView';
import TodoList from '../components/TodoList/TodoList';
import { Task } from '../types/api';

const Dashboard = () => {
  const { data: tasks } = useQuery<Task[]>({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await apiClient.get('/tasks');
      return response.data;
    },
  });

  // Mock calendar events based on tasks
  const calendarEvents = tasks?.map(task => ({
    id: task.id?.toString() || '',
    title: task.description,
    date: new Date(), // TODO: Add actual dates to tasks
    type: 'task' as const,
  })) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900">Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <CalendarView events={calendarEvents} />
        </div>
        <div>
          <TodoList tasks={tasks || []} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
