import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { ChatMessage } from "./ChatMessage";
import type { Message } from "./ChatMessage";

interface ChatHistoryProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatHistory({ messages, isLoading }: ChatHistoryProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <ScrollArea 
      className="h-full px-2 sm:px-4 py-4 sm:py-6" 
      ref={scrollAreaRef}
      role="log"
      aria-label="Chat conversation history"
      aria-live="polite"
      aria-atomic="false"
    >
      {messages.length === 0 && !isLoading ? (
        <div 
          className="flex flex-col items-center justify-center h-full text-center px-4"
          role="region"
          aria-label="Welcome message and suggestions"
        >
          <div className="max-w-md space-y-4">
            <div className="mb-4">
              <img 
                src="/dati-logo.png" 
                alt="Dati company logo" 
                className="h-16 w-16 sm:h-20 sm:w-20 mx-auto object-contain bg-white p-2 rounded-lg"
              />
            </div>
            <h2 className="text-xl sm:text-2xl font-semibold text-foreground">
              Welcome to re:Invent Planner
            </h2>
            <p className="text-sm sm:text-base text-muted-foreground">
              Ask me anything about AWS re:Invent sessions, speakers, or help building your personalized schedule.
            </p>
            <div className="space-y-2 text-left">
              <p className="text-xs sm:text-sm font-medium text-foreground">
                Try asking:
              </p>
              <ul className="text-xs sm:text-sm space-y-1 text-muted-foreground" role="list">
                <li><span aria-hidden="true">• </span>"What sessions are available on December 5th?"</li>
                <li><span aria-hidden="true">• </span>"Show me all AI/ML sessions"</li>
                <li><span aria-hidden="true">• </span>"Find sessions by Werner Vogels"</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-2 sm:space-y-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              isUser={message.role === 'user'}
            />
          ))}
          
          {isLoading && (
            <div 
              className="flex gap-2 sm:gap-3 mb-3 sm:mb-4 px-2 sm:px-0"
              role="status"
              aria-label="Assistant is typing"
            >
              <Skeleton className="h-7 w-7 sm:h-8 sm:w-8 rounded-full flex-shrink-0" />
              <div className="flex flex-col gap-2 max-w-[85%] sm:max-w-[70%]">
                <Skeleton className="h-12 sm:h-16 w-full rounded-lg" />
                <Skeleton className="h-3 sm:h-4 w-16 sm:w-20" />
              </div>
              <span className="sr-only">Assistant is typing a response</span>
            </div>
          )}
          
          <div ref={bottomRef} aria-hidden="true" />
        </div>
      )}
    </ScrollArea>
  );
}
