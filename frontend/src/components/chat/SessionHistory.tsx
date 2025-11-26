import { useEffect, useState } from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ChatHistoryService, type SessionEvent, type ToolUseContent, type ToolResultContent } from "@/services/chatHistoryService";
import { MessageSquare, User, Bot, Wrench, CheckCircle, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";

interface SessionHistoryProps {
  sessionId: string;
  className?: string;
}

/**
 * SessionHistory component displays the conversation history for a specific session
 * from AgentCore Memory.
 * 
 * Features:
 * - Displays user and assistant messages
 * - Shows tool use and tool results
 * - Handles loading and error states
 * - Renders parsed events from backend
 */
export function SessionHistory({ sessionId, className }: SessionHistoryProps) {
  const [events, setEvents] = useState<SessionEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadHistory = async () => {
      if (!sessionId) {
        setEvents([]);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await ChatHistoryService.getSessionEvents(sessionId);
        setEvents(response.events);
      } catch (err: any) {
        console.error('Failed to load session history:', err);
        setError(err.message || 'Failed to load session history');
      } finally {
        setIsLoading(false);
      }
    };

    loadHistory();
  }, [sessionId]);

  // Loading state
  if (isLoading) {
    return (
      <div className={cn("space-y-4 p-4", className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-20 w-full" />
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className={cn("p-4", className)}>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  // Empty state
  if (events.length === 0) {
    return (
      <div 
        className={cn(
          "flex flex-col items-center justify-center p-6 text-center h-full",
          className
        )}
      >
        <MessageSquare className="h-12 w-12 text-muted-foreground mb-3 opacity-50" />
        <p className="text-sm text-muted-foreground">
          No messages in this session yet
        </p>
      </div>
    );
  }

  // Messages list
  return (
    <ScrollArea className={cn("h-full", className)}>
      <div className="space-y-4 p-4">
        {events.map((event) => (
          <EventMessage key={event.event_id} event={event} />
        ))}
      </div>
    </ScrollArea>
  );
}

/**
 * Render a single event message
 */
function EventMessage({ event }: { event: SessionEvent }) {
  const isUser = event.role === 'user';

  return (
    <div
      className={cn(
        "flex gap-3",
        isUser && "flex-row-reverse"
      )}
    >
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
      )}>
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Message content */}
      <Card className={cn(
        "flex-1 p-3 max-w-[80%]",
        isUser && "bg-primary/5"
      )}>
        <EventContent event={event} />
        
        {/* Timestamp */}
        <p className="text-xs text-muted-foreground mt-2">
          {formatTimestamp(event.timestamp)}
        </p>
      </Card>
    </div>
  );
}

/**
 * Render event content based on type
 */
function EventContent({ event }: { event: SessionEvent }) {
  switch (event.type) {
    case 'text':
      return <p className="text-sm whitespace-pre-wrap">{event.content as string}</p>;
    
    case 'tool_use':
      const toolUse = event.content as ToolUseContent;
      return (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium">
            <Wrench className="h-4 w-4" />
            <span>Using tool: {toolUse.tool_name}</span>
          </div>
          <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
            {JSON.stringify(toolUse.tool_input, null, 2)}
          </pre>
        </div>
      );
    
    case 'tool_result':
      const toolResult = event.content as ToolResultContent;
      return (
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm font-medium">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span>Tool result</span>
            <Badge variant={toolResult.status === 'success' ? 'default' : 'destructive'}>
              {toolResult.status}
            </Badge>
          </div>
          {toolResult.result && (
            <pre className="text-xs bg-muted p-2 rounded overflow-x-auto max-h-40">
              {toolResult.result}
            </pre>
          )}
        </div>
      );
    
    case 'error':
      return (
        <div className="flex items-center gap-2 text-sm text-destructive">
          <AlertCircle className="h-4 w-4" />
          <span>Error parsing event</span>
        </div>
      );
    
    default:
      return (
        <pre className="text-xs bg-muted p-2 rounded overflow-x-auto">
          {JSON.stringify(event.content, null, 2)}
        </pre>
      );
  }
}

/**
 * Format timestamp for display
 */
function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
