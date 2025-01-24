export interface ScheduleSlot {
  date: string;
  task_id: number;
  description: string;
  hours: number;
  start_time: string;
  end_time: string;
}

export interface Schedule {
  status: string;
  project_id: number;
  schedule: ScheduleSlot[];
  total_duration_days: number;
  earliest_start: string | null;
  latest_end: string | null;
}

export interface AvailableSlot {
  date: string;
  available_hours: number;
  start_time: string;
  end_time: string;
}

export interface ScheduleValidation {
  is_valid: boolean;
  conflicts: string[];
  warnings: string[];
}

export interface SchedulingError {
  status: string;
  message: string;
}
