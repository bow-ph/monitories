import React, { useState, useEffect } from 'react';
import { format, startOfWeek, addDays, startOfMonth, endOfMonth, eachDayOfInterval, isWithinInterval, parseISO } from 'date-fns';
import { de } from 'date-fns/locale';
import { useQuery } from '@tanstack/react-query';
import { CalDAVTask } from '../../types/api';
import { apiClient } from '../../api/client';

interface CalendarEvent {
  id: string;
  title: string;
  start_date: Date;
  end_date: Date;
  type: 'task' | 'meeting' | 'deadline';
  estimated_hours?: number;
  status?: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
}

interface CalendarViewProps {
  events: CalendarEvent[];
  onEventUpdate?: (eventId: string, updates: Partial<CalendarEvent>) => void;
}

const CalendarView: React.FC<CalendarViewProps> = ({ events, onEventUpdate }) => {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const monthStart = startOfMonth(selectedDate);
  const monthEnd = endOfMonth(selectedDate);
  const startDate = startOfWeek(monthStart, { locale: de });

  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const weekDays = Array.from(Array(7)).map((_, index) => {
    const day = addDays(startDate, index);
    return format(day, 'EEE', { locale: de });
  });

  // Fetch calendar data from CalDAV
  const { data: calendarData } = useQuery({
    queryKey: ['calendar', format(monthStart, 'yyyy-MM'), format(monthEnd, 'yyyy-MM')],
    queryFn: async () => {
      const response = await apiClient.get('/tasks/1/PM%20Tool', {
        params: {
          start_date: monthStart.toISOString(),
          end_date: monthEnd.toISOString(),
        },
      });
      return response.data;
    },
  });

  // State for merged events and sync status
  const [mergedEvents, setMergedEvents] = useState<CalendarEvent[]>(events);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'error'>('idle');

  useEffect(() => {
    if (calendarData?.tasks) {
      setSyncStatus('syncing');
      try {
        const externalEvents: CalendarEvent[] = calendarData.tasks.map((task: CalDAVTask) => ({
          id: task.uid,
          title: task.description,
          start_date: parseISO(task.start_date),
          end_date: parseISO(task.end_date),
          type: 'task' as const,
          estimated_hours: task.estimated_hours,
          status: task.status as 'pending' | 'in_progress' | 'completed',
          priority: task.priority as 'high' | 'medium' | 'low' | undefined,
        }));

        // Merge external events with local events
        const merged = [...events];
        externalEvents.forEach((extEvent: CalendarEvent) => {
          const existingIndex = merged.findIndex(e => e.id === extEvent.id);
          if (existingIndex >= 0) {
            // Update existing event
            merged[existingIndex] = { ...merged[existingIndex], ...extEvent };
          } else {
            // Check for conflicts
            const hasConflict = merged.some(existingEvent =>
              isWithinInterval(extEvent.start_date, { start: existingEvent.start_date, end: existingEvent.end_date }) ||
              isWithinInterval(extEvent.end_date, { start: existingEvent.start_date, end: existingEvent.end_date })
            );
            
            if (hasConflict) {
              console.warn(`Conflict detected for task: ${extEvent.title}`);
            }
            merged.push(extEvent);
          }
        });
        
        setMergedEvents(merged);
        setSyncStatus('idle');
      } catch (error) {
        console.error('Error syncing calendar:', error);
        setSyncStatus('error');
      }
    }
  }, [calendarData, events]);

  const getEventsForDay = (date: Date) => {
    return mergedEvents.filter(event => 
      isWithinInterval(date, { start: event.start_date, end: event.end_date })
    );
  };

  const checkForOverlap = (event: CalendarEvent) => {
    return mergedEvents.some(existingEvent => 
      event.id !== existingEvent.id &&
      (isWithinInterval(event.start_date, { start: existingEvent.start_date, end: existingEvent.end_date }) ||
       isWithinInterval(event.end_date, { start: existingEvent.start_date, end: existingEvent.end_date }))
    );
  };

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <h2 className="text-lg font-semibold text-gray-900">
              {format(selectedDate, 'MMMM yyyy', { locale: de })}
            </h2>
            {syncStatus === 'syncing' && (
              <div className="flex items-center text-blue-600">
                <div className="animate-spin h-4 w-4 mr-2 border-2 border-blue-600 rounded-full border-t-transparent" />
                <span className="text-sm">Synchronisiere...</span>
              </div>
            )}
            {syncStatus === 'error' && (
              <div className="text-sm text-red-600">
                Fehler bei der Synchronisation
              </div>
            )}
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setSelectedDate(addDays(selectedDate, -30))}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
            >
              Vorheriger Monat
            </button>
            <button
              onClick={() => setSelectedDate(addDays(selectedDate, 30))}
              className="px-3 py-1 text-sm border rounded hover:bg-gray-50"
            >
              Nächster Monat
            </button>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-px bg-gray-200">
        {weekDays.map((day) => (
          <div key={day} className="bg-gray-50 p-2 text-center text-sm font-medium text-gray-500">
            {day}
          </div>
        ))}
        {days.map((day) => {
          const dayEvents = getEventsForDay(day);
          const hasOverlap = dayEvents.some(checkForOverlap);
          
          return (
            <div
              key={day.toString()}
              className={`bg-white p-2 h-32 overflow-y-auto ${
                format(day, 'yyyy-MM-dd') === format(new Date(), 'yyyy-MM-dd')
                  ? 'bg-blue-50'
                  : ''
              } ${hasOverlap ? 'border-l-4 border-yellow-400' : ''}`}
            >
              <div className="font-medium text-sm text-gray-900">
                {format(day, 'd')}
              </div>
              {dayEvents.map((event) => (
                <div
                  key={event.id}
                  className={`mt-1 px-2 py-1 text-xs rounded-md cursor-pointer transition-colors ${
                    event.type === 'task'
                      ? `${
                          event.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : event.status === 'in_progress'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-blue-100 text-blue-800'
                        }`
                      : event.type === 'meeting'
                      ? 'bg-purple-100 text-purple-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                  onClick={() => {
                    if (onEventUpdate && event.type === 'task') {
                      const newStatus = 
                        event.status === 'pending' ? 'in_progress' :
                        event.status === 'in_progress' ? 'completed' :
                        'pending';
                      onEventUpdate(event.id, { status: newStatus });
                    }
                  }}
                >
                  <div className="flex justify-between items-center">
                    <span>{event.title}</span>
                    {event.estimated_hours && (
                      <span className="text-xs opacity-75">
                        {event.estimated_hours}h
                      </span>
                    )}
                  </div>
                  {event.priority && (
                    <div className={`mt-1 h-1 rounded-full ${
                      event.priority === 'high' ? 'bg-red-400' :
                      event.priority === 'medium' ? 'bg-yellow-400' :
                      'bg-green-400'
                    }`} />
                  )}
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default CalendarView;
