import { Bot, User } from "lucide-react";

interface ChatAvatarProps {
  isUser: boolean;
  size?: number;
}

export function ChatAvatar({ isUser, size = 32 }: ChatAvatarProps) {
  return (
    <div
      className={`flex items-center justify-center rounded-full ${
        isUser 
          ? 'bg-primary text-primary-foreground' 
          : 'bg-muted text-foreground'
      }`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        minWidth: `${size}px`,
        minHeight: `${size}px`
      }}
    >
      {isUser ? (
        <User size={size * 0.6} strokeWidth={2} />
      ) : (
        <Bot size={size * 0.6} strokeWidth={2} />
      )}
    </div>
  );
}
