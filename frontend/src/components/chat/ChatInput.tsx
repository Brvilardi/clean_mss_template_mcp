import { useState, useRef, useEffect } from "react";
import type { KeyboardEvent } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
  autoFocus?: boolean;
}

export function ChatInput({ 
  onSend, 
  disabled, 
  placeholder = "Ask about re:Invent sessions...",
  autoFocus = false
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus input field when autoFocus prop is true
  useEffect(() => {
    if (autoFocus && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [autoFocus]);

  const handleSend = () => {
    // Validate: prevent sending empty messages (whitespace only)
    const trimmedMessage = message.trim();
    if (!trimmedMessage || disabled) {
      return;
    }

    onSend(trimmedMessage);
    setMessage("");
    
    // Return focus to textarea after sending
    setTimeout(() => {
      textareaRef.current?.focus();
    }, 0);
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Send on Enter, but allow Shift+Enter for new lines
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-3 sm:p-4 md:p-6" role="region" aria-label="Message input">
      <div className="flex gap-2 sm:gap-3">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          aria-label="Type your message"
          aria-describedby="chat-input-help"
          className="min-h-[50px] sm:min-h-[60px] max-h-[150px] sm:max-h-[200px] resize-none text-sm sm:text-base focus:ring-2 focus:ring-dati-primary focus:ring-offset-2"
          style={{ 
            backgroundColor: '#2a2a2a',
            borderColor: '#444',
            color: '#9ca3af',
          }}
          rows={2}
        />
        <Button
          onClick={handleSend}
          disabled={disabled || !message.trim()}
          size="icon"
          aria-label="Send message"
          className="h-[50px] w-[50px] sm:h-[60px] sm:w-[60px] flex-shrink-0 bg-dati-primary hover:bg-dati-accent-4 focus:ring-2 focus:ring-dati-primary focus:ring-offset-2 transition-colors"
        >
          <Send className="h-4 w-4 sm:h-5 sm:w-5" aria-hidden="true" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
      <p 
        id="chat-input-help" 
        className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 text-center mt-2"
        role="status"
        aria-live="polite"
      >
        Press Enter to send, Shift+Enter for new line
      </p>
    </div>
  );
}
