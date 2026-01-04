'use client';

import { useEffect } from 'react';
import { useUIStore } from '@/store';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const { theme, setTheme } = useUIStore();

  useEffect(() => {
    // Only run on client
    if (typeof window === 'undefined') return;

    // Get saved theme from localStorage or use system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    const initialTheme = savedTheme || (prefersDark ? 'dark' : 'light');
    setTheme(initialTheme);

    // Apply class to html element
    const root = document.documentElement;
    if (initialTheme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [setTheme]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    // Update HTML class and localStorage when theme changes
    const root = document.documentElement;
    if (!root) return;

    if (theme === 'dark') {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [theme]);

  return <>{children}</>;
}
