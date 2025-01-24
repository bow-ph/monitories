import { AxiosInstance } from 'axios';
import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

export const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: 0,
    },
  },
});

export const endpoints = {
  analyzePdf: (projectId: number) => `/v1/pdf-analysis/projects/${projectId}/analyze`,
  schedule: (projectId: number) => `/v1/scheduling/projects/${projectId}/schedule`,
  validateSchedule: (projectId: number) => `/v1/scheduling/projects/${projectId}/validate-schedule`,
  availableSlots: (projectId: number) => `/v1/scheduling/projects/${projectId}/available-slots`,
};
