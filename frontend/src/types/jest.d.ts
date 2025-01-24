import { Mock } from 'jest';

declare global {
  interface MediaQueryList {
    readonly matches: boolean;
    readonly media: string;
    onchange: ((this: MediaQueryList, ev: MediaQueryListEvent) => any) | null;
    addListener(callback: ((this: MediaQueryList, ev: MediaQueryListEvent) => any) | null): void;
    removeListener(callback: ((this: MediaQueryList, ev: MediaQueryListEvent) => any) | null): void;
  }

  interface Window {
    matchMedia: Mock<MediaQueryList>;
  }
}
