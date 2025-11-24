import { create } from 'zustand';
import type { Message } from '../types/chat';
import { AgentService } from '../services/agentService';

interface ChatState {
  // State
  messages: Message[];
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  startNewSession: () => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  // Initial state
  messages: [],
  currentSessionId: null,
  isLoading: false,
  error: null,

  // Send message action with optimistic updates
  sendMessage: async (content: string) => {
    const state = get();
    
    // Create optimistic user message
    const optimisticMessage: Message = {
      id: crypto.randomUUID(),
      content: content,
      role: 'user',
      timestamp: new Date(),
      status: 'sending',
      sessionId: state.currentSessionId || undefined
    };

    // Add optimistic message to UI immediately
    set(state => ({
      messages: [...state.messages, optimisticMessage],
      isLoading: true,
      error: null
    }));

    try {
      // Send to API
      const response = await AgentService.sendMessage(
        content,
        state.currentSessionId || undefined
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
        sessionId: response.output.session_id
      };

      set(state => ({
        messages: [...state.messages, assistantMessage],
        currentSessionId: response.output.session_id || state.currentSessionId,
        isLoading: false
      }));

    } catch (error) {
      // Update optimistic message to 'error' status
      set(state => ({
        messages: state.messages.map(msg =>
          msg.id === optimisticMessage.id
            ? { ...msg, status: 'error' as const }
            : msg
        ),
        isLoading: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred'
      }));
    }
  },

  // Clear all messages
  clearMessages: () => {
    // Clear localStorage when clearing messages
    try {
      localStorage.removeItem('reinvent-chat-history');
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
    
    set({ 
      messages: [], 
      currentSessionId: null,
      error: null 
    });
  },

  // Start a new session
  startNewSession: () => {
    // Clear localStorage when starting new session
    try {
      localStorage.removeItem('reinvent-chat-history');
    } catch (error) {
      console.error('Failed to clear localStorage:', error);
    }
    
    set({
      messages: [],
      currentSessionId: crypto.randomUUID(),
      error: null,
      isLoading: false
    });
  },

  // Set error message
  setError: (error: string | null) => set({ error })
}));
