import { useTranslation } from "react-i18next";
import { useLanguage } from "../../hooks/useLanguage";
import { formatTime } from "../../utils/dateFormatter";
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
  const { t } = useTranslation();
  const { currentLanguage } = useLanguage();

  const getStatusLabel = () => {
    if (!status || !isUser) return '';
    switch (status) {
      case 'sending': return t('common.loading');
      case 'sent': return 'Sent';
      case 'error': return t('common.error');
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
      aria-label={`${isUser ? t('chat.you') : t('chat.aiAssistant')} message at ${formatTime(timestamp, currentLanguage)}`}
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
            : "bg-muted text-foreground"
        )}>
          <p className="text-xs sm:text-sm whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
        
        <div className="flex items-center gap-2 px-1">
          <time 
            className="text-[10px] sm:text-xs text-muted-foreground"
            dateTime={timestamp.toISOString()}
          >
            {formatTime(timestamp, currentLanguage)}
          </time>
          
          {status && isUser && status !== 'sent' && (
            <Badge 
              variant={status === 'error' ? 'destructive' : 'secondary'}
              className="text-[10px] sm:text-xs h-4 sm:h-5"
              role="status"
              aria-label={getStatusLabel()}
            >
              {status === 'sending' && t('common.loading')}
              {status === 'error' && t('common.error')}
            </Badge>
          )}
        </div>
      </div>
    </article>
  );
}
