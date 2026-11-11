import { create } from 'zustand';

interface UIState {
  // State
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  globalError: string | null;
  errorSuggestions: string[];

  // Actions
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setGlobalError: (error: string | null, suggestions?: string[]) => void;
  clearGlobalError: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  // Initial state
  sidebarOpen: true,
  theme: 'light',
  globalError: null,
  errorSuggestions: [],

  // Toggle sidebar
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  // Set sidebar open state
  setSidebarOpen: (open: boolean) => set({ sidebarOpen: open }),

  // Set theme
  setTheme: (theme: 'light' | 'dark') => {
    set({ theme });
    // Persist theme preference
    try {
      localStorage.setItem('reinvent-theme', theme);
    } catch (error) {
      console.error('Failed to save theme preference:', error);
    }
  },

  // Set global error with optional suggestions
  setGlobalError: (error: string | null, suggestions: string[] = []) => {
    set({ globalError: error, errorSuggestions: suggestions });
  },

  // Clear global error
  clearGlobalError: () => {
    set({ globalError: null, errorSuggestions: [] });
  }
}));
