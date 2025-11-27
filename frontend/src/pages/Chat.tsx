import { useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useChatStore } from "../store/chatStore";
import { ErrorAlert } from "../components/ErrorAlert";
import { Button } from "@/components/ui/button";
import { useNetworkStatus } from "../hooks/useNetworkStatus";
import { useLanguage } from "../hooks/useLanguage";
import { formatRelativeDate, formatTime } from "../utils/dateFormatter";
import { WifiOff } from "lucide-react";
import { ChatAvatar } from "../components/chat/ChatAvatar";
import { SessionIdDisplay } from "../components/chat/SessionIdDisplay";
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
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();
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
    saveToCache,
    loadChatHistory,
    loadSessionMessages
  } = useChatStore();
  const initialQuerySent = useRef(false);
  const previousSessionId = useRef<string | null>(null);
  const isLoadingSessionRef = useRef(false);

  // Load conversation history from cache on mount
  useEffect(() => {
    loadFromCache();
  }, [loadFromCache]);

  // Load chat history (list of all sessions) on mount and auto-load most recent session
  useEffect(() => {
    const loadHistory = async () => {
      await loadChatHistory();
    };
    loadHistory();
  }, [loadChatHistory]);

  // Load session messages when currentSessionId changes (from sidebar or URL)
  useEffect(() => {
    if (currentSessionId && currentSessionId !== previousSessionId.current) {
      // Only load if we don't already have messages for this session
      if (messages.length === 0 || messages[0]?.sessionId !== currentSessionId) {
        isLoadingSessionRef.current = true;
        loadSessionMessages(currentSessionId).finally(() => {
          isLoadingSessionRef.current = false;
        });
      }
      previousSessionId.current = currentSessionId;
    }
  }, [currentSessionId, loadSessionMessages, messages]);

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
        className="p-3 sm:p-4 border-b border-border bg-card shadow-sm flex flex-col gap-2 sm:gap-3"
        role="banner"
      >
        <div className="flex items-center justify-between gap-2 sm:gap-4">
          <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
            <img 
              src="/dati-logo.png" 
              alt="Dati company logo" 
              className="h-6 w-6 sm:h-8 sm:w-8 object-contain flex-shrink-0 bg-white p-1 rounded"
            />
            <h1 className="text-lg sm:text-xl font-bold truncate text-aws-orange">
              {t('chat.title')}
            </h1>
            {!isOnline && (
              <div 
                className="flex items-center gap-1 text-xs text-destructive flex-shrink-0"
                role="status"
                aria-live="polite"
              >
                <WifiOff className="h-3 w-3" aria-hidden="true" />
                <span className="sr-only">{t('chat.aria.youAreOffline')}</span>
              </div>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={startNewSession}
            disabled={isLoading || !isOnline}
            className="flex-shrink-0 border-aws-orange text-aws-orange hover:bg-aws-orange hover:text-white"
            aria-label={t('chat.aria.startNewChat')}
          >
            <span className="hidden sm:inline">{t('chat.newChat')}</span>
            <span className="sm:hidden">{t('common.new')}</span>
          </Button>
        </div>
        
        {/* Session ID Display */}
        {currentSessionId && (
          <SessionIdDisplay sessionId={currentSessionId} />
        )}
      </header>

      {/* Error Alert */}
      {error && (
        <div className="px-3 sm:px-4 pt-3 sm:pt-4" role="region" aria-label={t('chat.aria.errorNotification')}>
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
                userName={t('chat.aiAssistant')} 
                info={
                  isLoading && messages.length === 0 
                    ? t('chat.loadingSessionHistory') 
                    : isLoading
                      ? t('chat.thinking')
                      : messages.length === 0 
                        ? t('chat.askAboutSessions') 
                        : t('chat.messagesCount', { count: messages.length })
                }
              />
            </ConversationHeader>
            
            <MessageList
              typingIndicator={isLoading && messages.length > 0 ? <TypingIndicator content={t('chat.aiIsThinking')} /> : null}
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
                      {t('chat.welcome')}
                    </h2>
                    <p style={{ color: 'var(--muted-foreground)', marginBottom: '1rem' }}>
                      {t('chat.welcomeMessage')}
                    </p>
                    <div style={{ textAlign: 'left', marginTop: '1.5rem' }}>
                      <p style={{ fontWeight: '500', marginBottom: '0.5rem' }}>{t('chat.tryAsking')}</p>
                      <ul style={{ listStyle: 'none', padding: 0 }}>
                        <li style={{ marginBottom: '0.25rem' }}>• "{t('chat.exampleQuestions.question1')}"</li>
                        <li style={{ marginBottom: '0.25rem' }}>• "{t('chat.exampleQuestions.question2')}"</li>
                        <li style={{ marginBottom: '0.25rem' }}>• "{t('chat.exampleQuestions.question3')}"</li>
                      </ul>
                    </div>
                  </div>
                </MessageList.Content>
              ) : messages.length === 0 && isLoading ? (
                <MessageList.Content
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100%',
                    textAlign: 'center',
                    padding: '2rem'
                  }}
                >
                  <div style={{ maxWidth: '400px' }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'center',
                      marginBottom: '1.5rem'
                    }}>
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-aws-orange"></div>
                    </div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem' }}>
                      {t('chat.loadingSessionHistory')}
                    </h3>
                    <p style={{ color: 'var(--muted-foreground)' }}>
                      {t('common.loading')}
                    </p>
                  </div>
                </MessageList.Content>
              ) : (
                messages.map((msg) => {
                  const messageDate = new Date(msg.timestamp);
                  
                  // Format date using locale-aware formatter
                  const dateStr = formatRelativeDate(messageDate, currentLanguage, t);
                  
                  // Format time using locale-aware formatter
                  const timeStr = formatTime(messageDate, currentLanguage);
                  
                  return (
                    <Message
                      key={msg.id}
                      model={{
                        message: msg.content,
                        sentTime: msg.timestamp.toISOString(),
                        sender: msg.role === 'user' ? t('chat.you') : t('chat.aiAssistant'),
                        direction: msg.role === 'user' ? 'outgoing' : 'incoming',
                        position: 'single'
                      }}
                    >
                      <Avatar>
                        <ChatAvatar isUser={msg.role === 'user'} size={32} />
                      </Avatar>
                      <Message.Footer 
                        sentTime={`${dateStr} at ${timeStr}`}
                        style={{ 
                          fontSize: '0.75rem',
                          opacity: 0.7,
                          marginTop: '0.25rem'
                        }}
                      />
                    </Message>
                  );
                })
              )}
            </MessageList>
            
            <MessageInput
              placeholder={
                isLoading && messages.length === 0 
                  ? t('chat.placeholderLoading')
                  : !isOnline 
                    ? t('chat.placeholderOffline')
                    : isLoading 
                      ? t('chat.placeholderThinking')
                      : t('chat.placeholder')
              }
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
