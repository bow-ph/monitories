import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../ThemeContext';
import { act } from 'react-dom/test-utils';
import '@testing-library/jest-dom';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
  })),
});

// Test component that uses the theme context
const TestComponent = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span data-testid="theme-value">{theme}</span>
      <button onClick={toggleTheme} data-testid="theme-toggle">
        Toggle Theme
      </button>
    </div>
  );
};

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.documentElement.classList.remove('dark');
  });

  it('provides light theme by default when no preference is set', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
  });

  it('uses dark theme when system preference is dark', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    window.matchMedia.mockImplementationOnce((query: string) => ({
      matches: query === '(prefers-color-scheme: dark)',
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
    }));
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('uses theme from localStorage if available', () => {
    mockLocalStorage.getItem.mockReturnValue('dark');
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('toggles theme when button is clicked', () => {
    mockLocalStorage.getItem.mockReturnValue('light');
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    const toggleButton = screen.getByTestId('theme-toggle');
    
    // Initial state
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    
    // Toggle to dark
    act(() => {
      fireEvent.click(toggleButton);
    });
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
    
    // Toggle back to light
    act(() => {
      fireEvent.click(toggleButton);
    });
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  it('persists theme preference in localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue('light');
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    act(() => {
      fireEvent.click(screen.getByTestId('theme-toggle'));
    });
    
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });
});
