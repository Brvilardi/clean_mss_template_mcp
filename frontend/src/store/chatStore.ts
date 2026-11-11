import { create } from 'zustand';
import type { Message } from '../types/chat';
import { AgentService, type AgentError } from '../services/agentService';
import { ChatHistoryService, type SessionEvent } from '../services/chatHistoryService';
import i18n from '../i18n/config';

// Cache configuration
const STORAGE_KEY = 'reinvent-chat-history';
const CACHE_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours

interface CachedData {
  messages: Message[];
  currentSessionId: string | null;
  timestamp: number;
}

/**
 * Session metadata from chat history
 */
export interface SessionMetadata {
  session_id: string;
  actor_id: string;
  created_at?: string;
  last_activity: string;
  message_count?: number;
  last_message_preview?: string;
}

interface ChatState {
  // State
  messages: Message[];
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
  errorSuggestions: string[];
  isRetryable: boolean;
  
  // Chat history state
  chatHistory: SessionMetadata[];
  isLoadingHistory: boolean;
  historyError: string | null;

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
  
  // Chat history actions
  loadChatHistory: () => Promise<void>;
  loadSessionMessages: (sessionId: string) => Promise<void>;
  switchSession: (sessionId: string) => Promise<void>;
  updateSessionHistory: (sessionId: string, lastMessage: string) => void;
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
  
  // Chat history state
  chatHistory: [],
  isLoadingHistory: false,
  historyError: null,

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
    
    // Generate session_id if not exists
    // Note: actor_id is no longer needed - it's extracted from Cognito JWT automatically
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
      // Get current language code (ISO 639-1: pt, en)
      const languageCode = i18n.language.split('-')[0];
      
      // Send to API with session_id and language
      // actor_id is automatically extracted from Cognito JWT by API Gateway
      const response = await AgentService.sendMessage(
        content,
        sessionId,
        languageCode
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

      // Update session history in localStorage
      get().updateSessionHistory(sessionId, content);

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
  },

  // Load chat history - fetch all available sessions for the user
  loadChatHistory: async () => {
    set({ isLoadingHistory: true, historyError: null });

    try {
      // NOTE: AWS Bedrock AgentCore Memory does not support listing all sessions for a user.
      // As a workaround, we track session IDs in localStorage when they are created.
      // This means chat history is local to the browser and won't sync across devices.
      
      // Load session IDs from localStorage
      const sessionHistoryKey = 'reinvent-session-history';
      const storedHistory = localStorage.getItem(sessionHistoryKey);
      
      let sessions: SessionMetadata[] = [];
      
      if (storedHistory) {
        try {
          const parsed = JSON.parse(storedHistory);
          if (Array.isArray(parsed)) {
            sessions = parsed;
          }
        } catch (e) {
          console.error('Failed to parse session history from localStorage:', e);
          localStorage.removeItem(sessionHistoryKey);
        }
      }
      
      // Sort by last_activity (most recent first)
      const sortedSessions = sessions.sort((a, b) => {
        const dateA = new Date(a.last_activity).getTime();
        const dateB = new Date(b.last_activity).getTime();
        return dateB - dateA;
      });

      set({ 
        chatHistory: sortedSessions,
        isLoadingHistory: false 
      });

      // Auto-load most recent session if no messages are currently loaded
      const state = get();
      if (sortedSessions.length > 0 && state.messages.length === 0 && !state.currentSessionId) {
        const mostRecentSession = sortedSessions[0];
        await get().loadSessionMessages(mostRecentSession.session_id);
      }

    } catch (error: any) {
      console.error('Failed to load chat history:', error);
      set({ 
        historyError: error.message || 'Failed to load chat history',
        isLoadingHistory: false 
      });
    }
  },

  // Load messages for a specific session
  loadSessionMessages: async (sessionId: string) => {
    set({ isLoading: true, error: null });

    try {
      // Fetch session events from AgentCore Memory
      const response = await ChatHistoryService.getSessionEvents(sessionId);
      
      // Convert events to messages - only include text messages from user/assistant
      const messages: Message[] = response.events
        .filter((event: SessionEvent) => {
          // Only include text events with user or assistant role
          return event.type === 'text' && (event.role === 'user' || event.role === 'assistant');
        })
        .map((event: SessionEvent): Message => {
          return {
            id: event.event_id,
            content: event.content as string,
            role: event.role as 'user' | 'assistant',
            timestamp: new Date(event.timestamp),
            status: 'sent',
            sessionId: sessionId
          };
        })
        .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

      set({ 
        messages,
        currentSessionId: sessionId,
        isLoading: false 
      });

      // Save to cache (current session only)
      saveToLocalStorage(messages, sessionId);

    } catch (error: any) {
      console.error('Failed to load session messages:', error);
      set({ 
        error: error.message || 'Failed to load session messages',
        errorSuggestions: error.suggestions || ['Try refreshing the page', 'Check your internet connection'],
        isRetryable: error.isRetryable ?? true,
        isLoading: false 
      });
    }
  },

  // Switch to a different session
  switchSession: async (sessionId: string) => {
    const state = get();
    
    // If switching to the same session, do nothing
    if (state.currentSessionId === sessionId) {
      return;
    }

    // Save current session to cache before switching
    if (state.currentSessionId && state.messages.length > 0) {
      saveToLocalStorage(state.messages, state.currentSessionId);
    }

    // Clear current messages and load new session
    set({ 
      messages: [],
      currentSessionId: sessionId,
      error: null,
      errorSuggestions: [],
      isRetryable: false
    });

    // Load messages for the new session
    await get().loadSessionMessages(sessionId);
  },

  // Update session history in localStorage (helper function)
  updateSessionHistory: (sessionId: string, lastMessage: string) => {
    const sessionHistoryKey = 'reinvent-session-history';
    const storedHistory = localStorage.getItem(sessionHistoryKey);
    
    let sessions: SessionMetadata[] = [];
    
    if (storedHistory) {
      try {
        const parsed = JSON.parse(storedHistory);
        if (Array.isArray(parsed)) {
          sessions = parsed;
        }
      } catch (e) {
        console.error('Failed to parse session history:', e);
      }
    }
    
    // Find existing session or create new one
    const existingIndex = sessions.findIndex(s => s.session_id === sessionId);
    const now = new Date().toISOString();
    
    if (existingIndex >= 0) {
      // Update existing session
      sessions[existingIndex] = {
        ...sessions[existingIndex],
        last_activity: now,
        last_message_preview: lastMessage.substring(0, 100),
        message_count: (sessions[existingIndex].message_count || 0) + 1
      };
    } else {
      // Create new session entry
      sessions.push({
        session_id: sessionId,
        actor_id: 'current-user', // Will be replaced with actual actor_id when available
        created_at: now,
        last_activity: now,
        last_message_preview: lastMessage.substring(0, 100),
        message_count: 1
      });
    }
    
    // Save back to localStorage
    try {
      localStorage.setItem(sessionHistoryKey, JSON.stringify(sessions));
      
      // Update the chatHistory state
      const sortedSessions = sessions.sort((a, b) => {
        const dateA = new Date(a.last_activity).getTime();
        const dateB = new Date(b.last_activity).getTime();
        return dateB - dateA;
      });
      
      set({ chatHistory: sortedSessions });
    } catch (e) {
      console.error('Failed to save session history:', e);
    }
  }
}));
