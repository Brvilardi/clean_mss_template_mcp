/**
 * SessionIdDisplay Component Usage Examples
 * 
 * This file demonstrates how to use the SessionIdDisplay component
 * in different contexts within the application.
 */

import { SessionIdDisplay } from './SessionIdDisplay';
import { useChatStore } from '@/store/chatStore';

/**
 * Example 1: Basic usage in a chat header
 * 
 * This is the most common use case - displaying the current session ID
 * in the chat interface header.
 */
export function ChatHeaderExample() {
  const { currentSessionId } = useChatStore();

  return (
    <header className="p-4 border-b flex items-center justify-between">
      <h1 className="text-xl font-bold">Chat</h1>
      
      {/* Display session ID in header */}
      <SessionIdDisplay sessionId={currentSessionId} />
    </header>
  );
}

/**
 * Example 2: Usage with custom styling
 * 
 * You can apply custom classes to match your design system.
 */
export function StyledSessionIdExample() {
  const { currentSessionId } = useChatStore();

  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-muted-foreground">Current Session:</span>
      <SessionIdDisplay 
        sessionId={currentSessionId}
        className="bg-accent/50 border-accent"
      />
    </div>
  );
}

/**
 * Example 3: Conditional rendering
 * 
 * The component automatically handles null session IDs by not rendering,
 * but you can also add your own conditional logic.
 */
export function ConditionalSessionIdExample() {
  const { currentSessionId, messages } = useChatStore();

  // Only show session ID if there are messages
  if (messages.length === 0) {
    return null;
  }

  return (
    <div className="p-2">
      <SessionIdDisplay sessionId={currentSessionId} />
    </div>
  );
}

/**
 * Example 4: Integration in Chat.tsx
 * 
 * Here's how to integrate the SessionIdDisplay into the main Chat page.
 * Add this to the header section of Chat.tsx:
 */
export function ChatPageIntegrationExample() {
  const { currentSessionId } = useChatStore();

  return (
    <header className="p-4 border-b bg-card shadow-sm flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        <img src="/dati-logo.png" alt="Logo" className="h-8 w-8" />
        <h1 className="text-xl font-bold">re:Invent Planner</h1>
      </div>

      {/* Add SessionIdDisplay here */}
      <div className="flex items-center gap-3">
        <SessionIdDisplay sessionId={currentSessionId} />
        <button className="btn-primary">New Chat</button>
      </div>
    </header>
  );
}

/**
 * Features of SessionIdDisplay:
 * 
 * 1. Truncated Display: Shows first 12 characters of session ID by default
 * 2. Copy to Clipboard: Click the copy button to copy full session ID
 * 3. Visual Feedback: Shows checkmark icon for 2 seconds after copying
 * 4. Tooltip: Hover over the session ID to see the full value
 * 5. Accessibility: Proper ARIA labels and screen reader support
 * 6. Responsive: Works well on mobile and desktop
 * 
 * Requirements Satisfied:
 * - 2.1: Displays session ID in the UI
 * - 2.2: Shows truncated hash (first 12 characters)
 * - 2.3: Copy-to-clipboard functionality
 * - 2.4: Tooltip with full hash on hover
 */
