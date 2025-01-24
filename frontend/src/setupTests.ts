import '@testing-library/jest-dom';
import { expect, jest } from '@jest/globals';

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};

// Mock import.meta
(global as any).import = {
  meta: {
    env: {
      VITE_API_URL: 'http://localhost:8000',
      MODE: 'test'
    }
  }
};
