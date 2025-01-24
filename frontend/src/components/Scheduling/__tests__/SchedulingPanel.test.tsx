import React from 'react';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SchedulingPanel from '../SchedulingPanel';

// Mock the API client
jest.mock('../../../api/client');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('SchedulingPanel', () => {
  it('renders loading state initially', () => {
    render(<SchedulingPanel projectId={1} />, { wrapper });
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
});
