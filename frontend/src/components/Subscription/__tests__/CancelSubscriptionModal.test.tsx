import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import CancelSubscriptionModal from '../CancelSubscriptionModal';

describe('CancelSubscriptionModal', () => {
  const mockOnCancel = jest.fn();
  const mockOnClose = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders modal with correct content', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    expect(screen.getByText('Abonnement kündigen')).toBeInTheDocument();
    expect(screen.getByText('Kündigungsgrund (optional)')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Warum möchten Sie kündigen?')).toBeInTheDocument();
    expect(screen.getByText('Kündigen')).toBeInTheDocument();
    expect(screen.getByText('Abbrechen')).toBeInTheDocument();
  });

  it('handles cancellation with reason', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    const reasonInput = screen.getByPlaceholderText('Warum möchten Sie kündigen?');
    fireEvent.change(reasonInput, { target: { value: 'Test cancellation reason' } });
    
    const submitButton = screen.getByText('Kündigen');
    fireEvent.click(submitButton);

    expect(mockOnCancel).toHaveBeenCalledWith('Test cancellation reason');
  });

  it('handles cancellation without reason', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    const submitButton = screen.getByText('Kündigen');
    fireEvent.click(submitButton);

    expect(mockOnCancel).toHaveBeenCalledWith('');
  });

  it('handles close button click', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    const closeButton = screen.getByRole('button', { name: 'Schließen' });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('handles cancel button click', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    const cancelButton = screen.getByText('Abbrechen');
    fireEvent.click(cancelButton);

    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('prevents form submission default behavior', () => {
    render(
      <CancelSubscriptionModal
        onCancel={mockOnCancel}
        onClose={mockOnClose}
      />
    );

    const form = screen.getByRole('form');
    const mockPreventDefault = jest.fn();
    
    fireEvent.submit(form, { preventDefault: mockPreventDefault });
    
    expect(mockPreventDefault).toHaveBeenCalledTimes(1);
  });
});
