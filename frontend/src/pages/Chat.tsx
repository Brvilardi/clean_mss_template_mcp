import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useChatStore } from "../store/chatStore";
import { ErrorAlert } from "../components/ErrorAlert";
import { Button } from "@/components/ui/button";
import { useNetworkStatus } from "../hooks/useNetworkStatus";
import { WifiOff } from "lucide-react";
import { ChatAvatar } from "../components/chat/ChatAvatar";
import { 
  MainContainer, 
  ChatContainer, 
  MessageList, 
  Message, 
  MessageInput,
  TypingIndicator,
  Avatar,
  ConversationHeader
} from "@chatscope/chat-ui-kit-react";
import "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import "../styles/chat-theme.css";

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
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <header 
        className="p-3 sm:p-4 border-b border-border bg-card shadow-sm flex items-center justify-between gap-2 sm:gap-4"
        role="banner"
      >
        <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
          <img 
            src="/dati-logo.png" 
            alt="Dati company logo" 
            className="h-6 w-6 sm:h-8 sm:w-8 object-contain flex-shrink-0 bg-white p-1 rounded"
          />
          <h1 className="text-lg sm:text-xl font-bold truncate text-aws-orange">
            re:Invent Planner
          </h1>
          {!isOnline && (
            <div 
              className="flex items-center gap-1 text-xs text-destructive flex-shrink-0"
              role="status"
              aria-live="polite"
            >
              <WifiOff className="h-3 w-3" aria-hidden="true" />
              <span className="sr-only">You are currently offline</span>
            </div>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={startNewSession}
          disabled={isLoading || !isOnline}
          className="flex-shrink-0 border-aws-orange text-aws-orange hover:bg-aws-orange hover:text-white"
          aria-label="Start a new chat conversation"
        >
          <span className="hidden sm:inline">New Chat</span>
          <span className="sm:hidden">New</span>
        </Button>
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

      {/* Modern Chat Container */}
      <div className="flex-1 overflow-hidden">
        <MainContainer>
          <ChatContainer>
            <ConversationHeader>
              <div style={{ marginRight: '0.75rem' }}>
                <ChatAvatar isUser={false} size={40} />
              </div>
              <ConversationHeader.Content 
                userName="AI Assistant" 
                info={messages.length === 0 ? "Ask me about re:Invent sessions" : `${messages.length} messages`}
              />
            </ConversationHeader>
            
            <MessageList
              typingIndicator={isLoading ? <TypingIndicator content="AI is thinking..." /> : null}
            >
              {messages.length === 0 && !isLoading ? (
                <MessageList.Content
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    height: '100%',
                    textAlign: 'center',
                    padding: '2rem'
                  }}
                >
                  <div style={{ maxWidth: '500px', margin: '0 auto' }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'center',
                      marginBottom: '1rem'
                    }}>
                      <ChatAvatar isUser={false} size={80} />
                    </div>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                      Welcome to re:Invent Planner
                    </h2>
                    <p style={{ color: 'var(--muted-foreground)', marginBottom: '1rem' }}>
                      Ask me anything about AWS re:Invent sessions, speakers, or help building your personalized schedule.
                    </p>
                    <div style={{ textAlign: 'left', marginTop: '1.5rem' }}>
                      <p style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Try asking:</p>
                      <ul style={{ listStyle: 'none', padding: 0 }}>
                        <li style={{ marginBottom: '0.25rem' }}>• "What sessions are available on December 5th?"</li>
                        <li style={{ marginBottom: '0.25rem' }}>• "Show me all AI/ML sessions"</li>
                        <li style={{ marginBottom: '0.25rem' }}>• "Find sessions by Werner Vogels"</li>
                      </ul>
                    </div>
                  </div>
                </MessageList.Content>
              ) : (
                messages.map((msg) => (
                  <Message
                    key={msg.id}
                    model={{
                      message: msg.content,
                      sentTime: msg.timestamp.toISOString(),
                      sender: msg.role === 'user' ? 'You' : 'AI Assistant',
                      direction: msg.role === 'user' ? 'outgoing' : 'incoming',
                      position: 'single'
                    }}
                  >
                    <Avatar>
                      <ChatAvatar isUser={msg.role === 'user'} size={32} />
                    </Avatar>
                  </Message>
                ))
              )}
            </MessageList>
            
            <MessageInput
              placeholder="Ask about re:Invent sessions..."
              onSend={handleSendMessage}
              disabled={isLoading || !isOnline}
              attachButton={false}
              sendButton={true}
            />
          </ChatContainer>
        </MainContainer>
      </div>
    </div>
  );
}
