import { useEffect } from "react";
import { useChatStore } from "../store/chatStore";
import { ChatHistory } from "../components/chat/ChatHistory";
import { ChatInput } from "../components/chat/ChatInput";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";

const STORAGE_KEY = "reinvent-chat-history";

export function Chat() {
  const { messages, isLoading, error, sendMessage, setError, startNewSession } = useChatStore();

  // Load conversation history from localStorage on mount
  useEffect(() => {
    const loadConversationHistory = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const data = JSON.parse(stored);
          
          // Validate stored data structure
          if (data.messages && Array.isArray(data.messages)) {
            // Restore messages to store
            useChatStore.setState({
              messages: data.messages.map((msg: any) => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
              })),
              currentSessionId: data.currentSessionId || null
            });
          }
        }
      } catch (error) {
        console.error("Failed to load conversation history:", error);
        // Clear corrupted data
        localStorage.removeItem(STORAGE_KEY);
      }
    };

    loadConversationHistory();
  }, []);

  // Save conversation history to localStorage whenever messages change
  useEffect(() => {
    if (messages.length > 0) {
      try {
        const data = {
          messages: messages,
          currentSessionId: useChatStore.getState().currentSessionId,
          lastUpdated: new Date().toISOString()
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } catch (error) {
        console.error("Failed to save conversation history:", error);
      }
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  const handleRetry = () => {
    setError(null);
  };

  const handleClearError = () => {
    setError(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 sm:p-6 border-b border-gray-200 bg-white dark:bg-gray-950">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-gray-100">
            re:Invent Planner
          </h1>
          <Button
            variant="outline"
            size="sm"
            onClick={startNewSession}
            disabled={isLoading}
          >
            New Chat
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="px-4 pt-4">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <div className="flex gap-2 ml-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRetry}
                  className="h-8"
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Retry
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleClearError}
                  className="h-8"
                >
                  Dismiss
                </Button>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      )}

      {/* Chat History - Takes remaining space */}
      <div className="flex-1 overflow-hidden">
        <ChatHistory messages={messages} isLoading={isLoading} />
      </div>

      {/* Chat Input - Fixed at bottom */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder="Ask about re:Invent sessions..."
      />
    </div>
  );
}
