import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useChatStore } from "../store/chatStore";
import { ChatHistory } from "../components/chat/ChatHistory";
import { ChatInput } from "../components/chat/ChatInput";
import { ErrorAlert } from "../components/ErrorAlert";
import { Button } from "@/components/ui/button";
import { useNetworkStatus } from "../hooks/useNetworkStatus";
import { WifiOff } from "lucide-react";

export function Chat() {
  const location = useLocation();
  const isOnline = useNetworkStatus();
  const { 
    messages, 
    isLoading, 
    error, 
    errorSuggestions,
    isRetryable,
    sendMessage, 
    retryLastMessage,
    clearError,
    startNewSession, 
    currentSessionId,
    loadFromCache,
    saveToCache
  } = useChatStore();
  const initialQuerySent = useRef(false);
  const previousSessionId = useRef<string | null>(null);

  // Load conversation history from cache on mount
  useEffect(() => {
    loadFromCache();
  }, [loadFromCache]);

  // Handle initial query from navigation state (e.g., from Dashboard)
  useEffect(() => {
    const state = location.state as { initialQuery?: string } | null;
    if (state?.initialQuery && !initialQuerySent.current && !isLoading) {
      initialQuerySent.current = true;
      sendMessage(state.initialQuery);
      // Clear the state to prevent re-sending on navigation
      window.history.replaceState({}, document.title);
    }
  }, [location.state, sendMessage, isLoading]);

  // Save conversation history to cache whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      saveToCache();
    }
  }, [messages, saveToCache]);

  // Track session changes to determine if we should auto-focus
  useEffect(() => {
    previousSessionId.current = currentSessionId;
  }, [currentSessionId]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleRetry = async () => {
    await retryLastMessage();
  };

  const handleClearError = () => {
    clearError();
  };

  return (
    <div className="h-full flex flex-col" style={{ background: '#1a1a1a' }}>
      {/* Header */}
      <header 
        className="p-3 sm:p-4 md:p-6 border-b shadow-sm"
        style={{ backgroundColor: '#1a1a1a', borderColor: '#333' }}
        role="banner"
      >
        <div className="flex items-center justify-between gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
            <img 
              src="/dati-logo.png" 
              alt="Dati company logo" 
              className="h-6 w-6 sm:h-8 sm:w-8 object-contain flex-shrink-0 bg-white p-1 rounded"
            />
            <h1 
              className="text-lg sm:text-2xl md:text-3xl font-bold truncate"
              style={{ color: '#CC7A00' }}
            >
              re:Invent Planner
            </h1>
            {!isOnline && (
              <div 
                className="flex items-center gap-1 text-xs sm:text-sm text-red-600 dark:text-red-400 flex-shrink-0"
                role="status"
                aria-live="polite"
              >
                <WifiOff className="h-3 w-3 sm:h-4 sm:w-4" aria-hidden="true" />
                <span className="hidden sm:inline">Offline</span>
                <span className="sr-only">You are currently offline</span>
              </div>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={startNewSession}
            disabled={isLoading || !isOnline}
            className="flex-shrink-0 hover:text-white focus:ring-2 focus:ring-offset-2 transition-colors"
            style={{ 
              borderColor: '#CC7A00',
              color: '#CC7A00'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#CC7A00';
              e.currentTarget.style.color = 'white';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#CC7A00';
            }}
            aria-label="Start a new chat conversation"
          >
            <span className="hidden sm:inline">New Chat</span>
            <span className="sm:hidden">New</span>
          </Button>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="px-3 sm:px-4 pt-3 sm:pt-4" role="region" aria-label="Error notification">
          <ErrorAlert
            error={error}
            suggestions={errorSuggestions}
            onRetry={isRetryable ? handleRetry : undefined}
            onDismiss={handleClearError}
          />
        </div>
      )}

      {/* Chat History - Takes remaining space */}
      <div className="flex-1 overflow-hidden">
        <ChatHistory messages={messages} isLoading={isLoading} />
      </div>

      {/* Chat Input - Fixed at bottom */}
      <div className="border-t shadow-lg" style={{ backgroundColor: '#1a1a1a', borderColor: '#333' }}>
        <div className="max-w-4xl mx-auto">
          <ChatInput
            onSend={handleSendMessage}
            disabled={isLoading || !isOnline}
            placeholder="Ask about re:Invent sessions..."
            autoFocus={messages.length === 0}
          />
        </div>
      </div>
    </div>
  );
}
