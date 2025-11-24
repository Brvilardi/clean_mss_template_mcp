import { MessageBubble } from "./MessageBubble";

export interface Message {
  id: string;
  content: string;
  timestamp: Date;
  role: 'user' | 'assistant';
  status?: 'sending' | 'sent' | 'error';
}

interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

export function ChatMessage({ message, isUser }: ChatMessageProps) {
  return (
    <MessageBubble
      content={message.content}
      isUser={isUser}
      timestamp={message.timestamp}
      status={message.status}
    />
  );
}
