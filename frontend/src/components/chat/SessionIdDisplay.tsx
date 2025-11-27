import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@/components/ui/button";
import { Copy, Check } from "lucide-react";
import { cn } from "@/lib/utils";

interface SessionIdDisplayProps {
  sessionId: string | null;
  className?: string;
}

/**
 * SessionIdDisplay component shows the current session ID with copy functionality.
 * 
 * Features:
 * - Displays truncated session hash (first 12 characters)
 * - Copy-to-clipboard functionality using navigator.clipboard API
 * - Visual feedback (checkmark icon) after successful copy
 * - Tooltip with full hash on hover
 * - Accessible with proper ARIA labels
 * 
 * Requirements: 2.1, 2.2, 2.3, 2.4
 */
export function SessionIdDisplay({ sessionId, className }: SessionIdDisplayProps) {
  const { t } = useTranslation();
  const [copied, setCopied] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  // If no session ID, don't render anything
  if (!sessionId) {
    return null;
  }

  // Truncate session ID to first 12 characters
  const truncatedId = sessionId.substring(0, 12);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sessionId);
      setCopied(true);
      
      // Reset copied state after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to copy session ID:', error);
    }
  };

  return (
    <div 
      className={cn(
        "flex items-center gap-2 px-3 py-2 rounded-lg bg-muted/50 border border-border",
        className
      )}
      role="region"
      aria-label={t('chat.sessionId')}
    >
      {/* Session ID label */}
      <span className="text-xs text-muted-foreground font-medium">
        {t('chat.sessionId')}:
      </span>

      {/* Truncated session ID with tooltip */}
      <div className="relative">
        <button
          className={cn(
            "text-sm font-mono text-foreground hover:text-primary transition-colors",
            "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded px-1",
            "cursor-default"
          )}
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          aria-label={`Session ID: ${sessionId}`}
          title={sessionId}
          type="button"
        >
          {truncatedId}...
        </button>

        {/* Custom tooltip */}
        {showTooltip && (
          <div
            className={cn(
              "absolute z-50 top-full left-0 mt-2 px-3 py-2 rounded-md",
              "bg-popover text-popover-foreground border border-border shadow-lg",
              "text-xs font-mono break-all max-w-xs",
              "animate-in fade-in-0 zoom-in-95"
            )}
            role="tooltip"
          >
            {sessionId}
            <div className="absolute -top-1 left-4 w-2 h-2 bg-popover border-l border-t border-border rotate-45" />
          </div>
        )}
      </div>

      {/* Copy button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={handleCopy}
        disabled={copied}
        aria-label={copied ? t('chat.sessionId') + ' copied' : 'Copy ' + t('chat.sessionId')}
        className="h-7 w-7 p-0 hover:bg-accent"
      >
        {copied ? (
          <Check className="h-3.5 w-3.5 text-green-600" aria-hidden="true" />
        ) : (
          <Copy className="h-3.5 w-3.5" aria-hidden="true" />
        )}
      </Button>

      {/* Screen reader feedback */}
      {copied && (
        <span className="sr-only" role="status" aria-live="polite">
          {t('chat.sessionId')} copied to clipboard
        </span>
      )}
    </div>
  );
}
