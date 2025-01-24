import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import SubscriptionManager from '../SubscriptionManager';
import { apiClient } from '../../../api/client';

// Mock dependencies
jest.mock('../../../api/client');
jest.mock('react-hot-toast');

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

describe('SubscriptionManager', () => {
  const mockSubscription = {
    id: 1,
    userId: 1,
    mollieId: 'sub_test',
    customerId: 'cust_test',
    packageType: 'team',
    projectLimit: 10,
    status: 'active',
    amount: 119.0,
    interval: '3 months',
    startDate: '2024-01-01T00:00:00Z',
    endDate: '2024-04-01T00:00:00Z',
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (apiClient.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('/subscriptions/me')) {
        return Promise.resolve({ data: mockSubscription });
      }
      if (url.includes('/project-limit')) {
        return Promise.resolve({
          data: {
            can_create: true,
            current_count: 5,
            limit: 10,
          },
        });
      }
      return Promise.reject(new Error('Not found'));
    });
  });

  it('renders loading state initially', () => {
    render(<SubscriptionManager />, { wrapper });
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('displays subscription details when loaded', async () => {
    render(<SubscriptionManager />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText('Team Paket')).toBeInTheDocument();
      expect(screen.getByText('3 Monate')).toBeInTheDocument();
      expect(screen.getByText('Aktiv')).toBeInTheDocument();
    });
  });

  it('handles subscription cancellation', async () => {
    (apiClient.post as jest.Mock).mockResolvedValueOnce({
      data: {
        status: 'success',
        message: 'Subscription cancelled successfully',
        end_date: '2024-04-01T00:00:00Z',
      },
    });

    render(<SubscriptionManager />, { wrapper });

    // Wait for subscription to load
    await waitFor(() => {
      expect(screen.getByText('Team Paket')).toBeInTheDocument();
    });

    // Click cancel button
    fireEvent.click(screen.getByText('Abonnement kündigen'));

    // Fill in cancellation reason
    const reasonInput = screen.getByPlaceholderText('Warum möchten Sie kündigen?');
    fireEvent.change(reasonInput, { target: { value: 'Test cancellation reason' } });

    // Submit cancellation
    fireEvent.click(screen.getByText('Kündigen'));

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledWith(
        expect.stringContaining('/cancel'),
        expect.objectContaining({
          subscriptionId: mockSubscription.id,
          reason: 'Test cancellation reason',
        })
      );
      expect(toast.success).toHaveBeenCalledWith('Abonnement erfolgreich gekündigt');
    });
  });

  it('displays error message when subscription load fails', async () => {
    (apiClient.get as jest.Mock).mockRejectedValueOnce(new Error('Failed to load'));
    
    render(<SubscriptionManager />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText('Kein aktives Abonnement gefunden')).toBeInTheDocument();
    });
  });

  it('displays project limit information', async () => {
    render(<SubscriptionManager />, { wrapper });
    
    await waitFor(() => {
      expect(screen.getByText('5 / 10')).toBeInTheDocument();
    });
  });
});
