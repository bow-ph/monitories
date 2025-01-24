import axios from 'axios';
import { QueryClient } from '@tanstack/react-query';

// Create axios instance with default config
const getBaseUrl = () => {
  try {
    return import.meta.env.VITE_API_URL;
  } catch {
    // For test environment
    return 'http://localhost:8000';
  }
};

export const apiClient = axios.create({
  baseURL: getBaseUrl() || 'https://pmadmin.bow-agentur.de',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBwbXRvb2wudGVzdCIsImV4cCI6MTczODMxMjMwNX0.c_9LN8Z2xU9IVa9Ee2-bXxY-vjD8PkKQxCmu--346uY'
  },
});

// Create react-query client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// API endpoints
export const endpoints = {
  analyzePdf: (projectId: number) => `/projects/${projectId}/analyze-pdf`,
  getProactiveHints: (projectId: number) => `/projects/${projectId}/proactive-hints`,
};
