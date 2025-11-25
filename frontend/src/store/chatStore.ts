import { create } from 'zustand';
import type { Message } from '../types/chat';
import { AgentService, type AgentError } from '../services/agentService';
import { useAuthStore } from './authStore';

// Cache configuration
const STORAGE_KEY = 'reinvent-chat-history';
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

interface CachedData {
  messages: Message[];
  currentSessionId: string | null;
  timestamp: number;
}

interface ChatState {
  // State
  messages: Message[];
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
  errorSuggestions: string[];
  isRetryable: boolean;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  retryLastMessage: () => Promise<void>;
  clearMessages: () => void;
  startNewSession: () => void;
  setError: (error: string | null, suggestions?: string[], isRetryable?: boolean) => void;
  clearError: () => void;
  loadFromCache: () => void;
  saveToCache: () => void;
  clearCache: () => void;
}

// Cache utility functions
const loadFromLocalStorage = (): CachedData | null => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;

    const data: CachedData = JSON.parse(stored);
    
    // Check if cache is expired
    const now = Date.now();
    if (now - data.timestamp > CACHE_TTL_MS) {
      localStorage.removeItem(STORAGE_KEY);
      return null;
    }

    // Validate data structure
    if (!data.messages || !Array.isArray(data.messages)) {
      return null;
    }

    // Convert timestamp strings back to Date objects
    data.messages = data.messages.map(msg => ({
      ...msg,
      timestamp: new Date(msg.timestamp)
    }));

    return data;
  } catch (error) {
    console.error('Failed to load from localStorage:', error);
    localStorage.removeItem(STORAGE_KEY);
    return null;
  }
};

const saveToLocalStorage = (messages: Message[], sessionId: string | null): void => {
  try {
    const data: CachedData = {
      messages,
      currentSessionId: sessionId,
      timestamp: Date.now()
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Failed to save to localStorage:', error);
  }
};

const clearLocalStorage = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear localStorage:', error);
  }
};

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  currentSessionId: null,
  isLoading: false,
  error: null,
  errorSuggestions: [],
  isRetryable: false,

  // Send message action with optimistic updates
  sendMessage: async (content: string) => {
    const state = get();
    
    // Check network connectivity first
    if (!AgentService.isOnline()) {
      set({
        error: 'No internet connection. Please check your network.',
        errorSuggestions: [
          'Check your WiFi or mobile data connection',
          'Try refreshing the page once connected'
        ],
        isRetryable: true
      });
      return;
    }
    
    // Get current user's Cognito sub ID for actor_id
    const authState = useAuthStore.getState();
    const actorId = authState.user?.id;
    
    // Generate session_id if not exists
    const sessionId = state.currentSessionId || crypto.randomUUID();
    
    // Create optimistic user message
    const optimisticMessage: Message = {
      id: crypto.randomUUID(),
      content: content,
      role: 'user',
      timestamp: new Date(),
      status: 'sending',
      sessionId: sessionId
    };

    // Add optimistic message to UI immediately
    set(state => ({
      messages: [...state.messages, optimisticMessage],
      currentSessionId: sessionId,
      isLoading: true,
      error: null,
      errorSuggestions: [],
      isRetryable: false
    }));

    try {
      // Send to API with session_id and actor_id
      const response = await AgentService.sendMessage(
        content,
        sessionId,
        actorId
      );

      // Update optimistic message to 'sent' status
      set(state => ({
        messages: state.messages.map(msg =>
          msg.id === optimisticMessage.id
            ? { ...msg, status: 'sent' as const }
            : msg
        )
      }));

      // Add assistant response
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: response.output.message,
        role: 'assistant',
        timestamp: new Date(response.output.timestamp),
        status: 'sent',
        sessionId: response.output.session_id || sessionId
      };

      set(state => ({
        messages: [...state.messages, assistantMessage],
        currentSessionId: response.output.session_id || sessionId,
        isLoading: false
      }));

    } catch (error) {
      const agentError = error as AgentError;
      
      // Update optimistic message to 'error' status
      set(state => ({
        messages: state.messages.map(msg =>
          msg.id === optimisticMessage.id
            ? { ...msg, status: 'error' as const }
            : msg
        ),
        isLoading: false,
        error: agentError.message || 'An unexpected error occurred',
        errorSuggestions: agentError.suggestions || [],
        isRetryable: agentError.isRetryable ?? true
      }));
    }
  },

  // Retry the last failed message
  retryLastMessage: async () => {
    const state = get();
    
    // Find the last user message with error status
    const lastErrorMessage = [...state.messages]
      .reverse()
      .find(msg => msg.role === 'user' && msg.status === 'error');
    
    if (!lastErrorMessage) {
      return;
    }

    // Remove the failed message and retry
    set(state => ({
      messages: state.messages.filter(msg => msg.id !== lastErrorMessage.id),
      error: null,
      errorSuggestions: [],
      isRetryable: false
    }));

    // Retry sending the message
    await get().sendMessage(lastErrorMessage.content);
  },

  // Clear all messages
  clearMessages: () => {
    clearLocalStorage();
    
    set({ 
      messages: [], 
      currentSessionId: null,
      error: null,
      errorSuggestions: [],
      isRetryable: false
    });
  },

  // Start a new session
  startNewSession: () => {
    clearLocalStorage();
    
    set({
      messages: [],
      currentSessionId: crypto.randomUUID(),
      error: null,
      errorSuggestions: [],
      isRetryable: false,
      isLoading: false
    });
  },

  // Set error message with suggestions
  setError: (error: string | null, suggestions: string[] = [], isRetryable: boolean = false) => {
    set({ 
      error, 
      errorSuggestions: suggestions,
      isRetryable 
    });
  },

  // Clear error
  clearError: () => {
    set({ 
      error: null, 
      errorSuggestions: [],
      isRetryable: false 
    });
  },

  // Load conversation from cache
  loadFromCache: () => {
    const cached = loadFromLocalStorage();
    if (cached) {
      set({
        messages: cached.messages,
        currentSessionId: cached.currentSessionId
      });
    }
  },

  // Save conversation to cache
  saveToCache: () => {
    const state = get();
    if (state.messages.length > 0) {
      saveToLocalStorage(state.messages, state.currentSessionId);
    }
  },

  // Clear cache
  clearCache: () => {
    clearLocalStorage();
  }
}));
