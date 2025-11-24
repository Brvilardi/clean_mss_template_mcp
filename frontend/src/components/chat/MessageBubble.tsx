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

  const getStatusLabel = () => {
    if (!status || !isUser) return '';
    switch (status) {
      case 'sending': return 'Message is being sent';
      case 'sent': return 'Message sent successfully';
      case 'error': return 'Message failed to send';
      default: return '';
    }
  };

  return (
    <article 
      className={cn(
        "flex gap-2 sm:gap-3 mb-3 sm:mb-4 px-2 sm:px-0",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
      role="article"
      aria-label={`${isUser ? 'Your' : 'Assistant'} message at ${formatTime(timestamp)}`}
    >
      <Avatar className="h-7 w-7 sm:h-8 sm:w-8 flex-shrink-0" aria-hidden="true">
        <AvatarFallback className={cn(
          isUser ? "bg-dati-accent-1 text-white" : "bg-dati-primary text-white"
        )}>
          {isUser ? "U" : "AI"}
        </AvatarFallback>
      </Avatar>
      
      <div className={cn(
        "flex flex-col gap-1 max-w-[85%] sm:max-w-[75%] md:max-w-[70%]",
        isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "rounded-lg px-3 py-2 sm:px-4 sm:py-2.5 break-words shadow-sm",
          isUser 
            ? "bg-dati-accent-1 text-white" 
            : "bg-gray-100 text-gray-900 dark:bg-gray-800 dark:text-gray-100"
        )}>
          <p className="text-xs sm:text-sm whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
        
        <div className="flex items-center gap-2 px-1">
          <time 
            className="text-[10px] sm:text-xs text-gray-500 dark:text-gray-400"
            dateTime={timestamp.toISOString()}
          >
            {formatTime(timestamp)}
          </time>
          
          {status && isUser && status !== 'sent' && (
            <Badge 
              variant={status === 'error' ? 'destructive' : 'secondary'}
              className="text-[10px] sm:text-xs h-4 sm:h-5"
              role="status"
              aria-label={getStatusLabel()}
            >
              {status === 'sending' && 'Sending...'}
              {status === 'error' && 'Failed'}
            </Badge>
          )}
        </div>
      </div>
    </article>
  );
}
