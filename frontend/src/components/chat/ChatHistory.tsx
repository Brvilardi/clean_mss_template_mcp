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
    <ScrollArea className="flex-1 px-4 py-6" ref={scrollAreaRef}>
      {messages.length === 0 && !isLoading ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="max-w-md space-y-4">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">
              Welcome to re:Invent Planner
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Ask me anything about AWS re:Invent sessions, speakers, or help building your personalized schedule.
            </p>
            <div className="space-y-2 text-left">
              <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Try asking:
              </p>
              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <li>• "What sessions are available on December 3rd?"</li>
                <li>• "Show me all AI/ML sessions"</li>
                <li>• "Find sessions by Werner Vogels"</li>
              </ul>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              isUser={message.role === 'user'}
            />
          ))}
          
          {isLoading && (
            <div className="flex gap-3 mb-4">
              <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
              <div className="flex flex-col gap-2 max-w-[70%]">
                <Skeleton className="h-16 w-full rounded-lg" />
                <Skeleton className="h-4 w-20" />
              </div>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>
      )}
    </ScrollArea>
  );
}
