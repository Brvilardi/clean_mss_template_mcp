import { useNavigate } from "react-router-dom";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { useChatStore, type SessionMetadata } from "@/store/chatStore";
import { MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatHistoryListProps {
  className?: string;
}

/**
 * ChatHistoryList component displays all available chat sessions
 * with metadata like session hash, message count, and last message preview.
 * 
 * Features:
 * - Displays truncated session hash (first 8 characters)
 * - Highlights active session
 * - Shows loading state while fetching
 * - Shows empty state when no sessions
 * - Handles session switching on click
 */
export function ChatHistoryList({ className }: ChatHistoryListProps) {
  const navigate = useNavigate();
  const { 
    chatHistory, 
    isLoadingHistory, 
    currentSessionId,
    switchSession 
  } = useChatStore();

  const handleSessionClick = (sessionId: string) => {
    switchSession(sessionId);
    // Navigate to chat page if not already there
    navigate('/app/chat');
  };

  const truncateSessionId = (sessionId: string): string => {
    return sessionId.substring(0, 8) + "...";
  };

  // Loading state
  if (isLoadingHistory) {
    return (
      <div className={cn("space-y-2 p-2", className)}>
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-2 p-3 rounded-lg border">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-16" />
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (chatHistory.length === 0) {
    return (
      <div 
        className={cn(
          "flex flex-col items-center justify-center p-6 text-center",
          className
        )}
        role="region"
        aria-label="No chat history"
      >
        <MessageSquare className="h-12 w-12 text-muted-foreground mb-3 opacity-50" />
        <p className="text-sm text-muted-foreground">
          No chat history yet
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          Start a conversation to see it here
        </p>
      </div>
    );
  }

  // Session list
  return (
    <ScrollArea className={cn("h-full", className)}>
      <div className="space-y-2 p-2">
        {chatHistory.map((session: SessionMetadata) => {
          const isActive = session.session_id === currentSessionId;
          
          return (
            <button
              key={session.session_id}
              onClick={() => handleSessionClick(session.session_id)}
              className={cn(
                "w-full text-left p-3 rounded-lg border transition-all",
                "hover:bg-accent hover:border-accent-foreground/20",
                "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
                isActive && "bg-accent border-accent-foreground/30 shadow-sm"
              )}
              aria-label={`Switch to session ${truncateSessionId(session.session_id)}`}
              aria-current={isActive ? "true" : undefined}
            >
              <div className="space-y-2">
                {/* Session ID */}
                <div className="flex items-center justify-between gap-2">
                  <span 
                    className={cn(
                      "text-sm font-mono font-medium truncate",
                      isActive ? "text-foreground" : "text-muted-foreground"
                    )}
                    title={session.session_id}
                  >
                    {truncateSessionId(session.session_id)}
                  </span>
                  {isActive && (
                    <Badge variant="secondary" className="text-xs px-2 py-0">
                      Active
                    </Badge>
                  )}
                </div>

                {/* Last message preview */}
                {session.last_message_preview && (
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {session.last_message_preview}
                  </p>
                )}

                {/* Metadata footer */}
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  {session.message_count !== undefined && (
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3 w-3" />
                      {session.message_count} {session.message_count === 1 ? 'message' : 'messages'}
                    </span>
                  )}
                  {session.last_activity && (
                    <span>
                      {formatRelativeTime(session.last_activity)}
                    </span>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </ScrollArea>
  );
}

/**
 * Format a timestamp as relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(timestamp: string): string {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) {
    return 'Just now';
  } else if (diffMins < 60) {
    return `${diffMins}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return date.toLocaleDateString();
  }
}
