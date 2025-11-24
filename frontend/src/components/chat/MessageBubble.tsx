import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";

interface MessageBubbleProps {
  content: string;
  isUser: boolean;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

export function MessageBubble({ content, isUser, timestamp, status }: MessageBubbleProps) {
  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    }).format(date);
  };

  return (
    <div className={cn(
      "flex gap-3 mb-4",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback className={cn(
          isUser ? "bg-blue-500 text-white" : "bg-orange-500 text-white"
        )}>
          {isUser ? "U" : "AI"}
        </AvatarFallback>
      </Avatar>
      
      <div className={cn(
        "flex flex-col gap-1 max-w-[70%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "rounded-lg px-4 py-2 break-words",
          isUser 
            ? "bg-blue-500 text-white" 
            : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
        )}>
          <p className="text-sm whitespace-pre-wrap">{content}</p>
        </div>
        
        <div className="flex items-center gap-2 px-1">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {formatTime(timestamp)}
          </span>
          
          {status && isUser && (
            <Badge 
              variant={status === 'error' ? 'destructive' : 'secondary'}
              className="text-xs h-5"
            >
              {status === 'sending' && 'Sending...'}
              {status === 'sent' && 'Sent'}
              {status === 'error' && 'Failed'}
            </Badge>
          )}
        </div>
      </div>
    </div>
  );
}
