export interface TodoItem {
  id: number;
  description: string;
  estimated_hours: number;
  actual_hours?: number;
  status: 'pending' | 'in_progress' | 'completed';
  confidence_score: number;
  confidence_rationale?: string;
  due_date?: string;
  priority: 'high' | 'medium' | 'low';
  caldav_event_uid?: string;
  project_id: number;
  created_at: string;
  updated_at?: string;
}

export interface TodoList {
  items: TodoItem[];
  total_items: number;
  pending_items: number;
  in_progress_items: number;
  completed_items: number;
}

export interface TodoFilter {
  status?: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
  project_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface TodoSyncStatus {
  status: 'synced' | 'pending' | 'failed';
  last_sync?: string;
  error_message?: string;
}

export interface TodoUpdateRequest {
  status?: 'pending' | 'in_progress' | 'completed';
  priority?: 'high' | 'medium' | 'low';
  actual_hours?: number;
  due_date?: string;
}
