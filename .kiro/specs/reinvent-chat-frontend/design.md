# Design Document

## Overview

The re:Invent Chat Frontend is a React-based single-page application that provides a clean, minimal chat interface for interacting with the AWS re:Invent Planner Agent. The application leverages the AWS Amplify frontend starter template with React 19, Tailwind CSS, React Router v7, shadcn UI components, and Zustand for state management. Users authenticate via AWS Cognito with custom corporate attributes, then interact with the Strands Agent through a conversational interface.

### Key Design Principles

1. **Simplicity First**: Minimal UI with focus on the chat experience
2. **Leverage Existing Patterns**: Use the starter template's authentication and layout structure
3. **State Management**: Zustand for centralized state, avoiding prop drilling
4. **Component Reusability**: Use shadcn UI components wherever possible
5. **Responsive Design**: Mobile-first approach with desktop optimization
6. **Performance**: Code splitting, lazy loading, and optimized bundle size

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend (SPA)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Authentication Layer                       │ │
│  │         (AWS Amplify + Cognito)                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Application Layer                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │   Chat Page  │  │  Dashboard   │  │  Settings   │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              State Management (Zustand)                 │ │
│  │  - Chat Messages  - User Session  - UI State          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AWS API Gateway                           │
│              /mss-template/agent/invocations                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              Lambda Function (Strands Agent)                 │
│                   FastAPI + Bedrock                          │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **React 19**: Latest React with concurrent features
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **React Router v7**: Client-side routing
- **Tailwind CSS**: Utility-first styling
- **shadcn/ui**: Pre-built accessible components
- **Zustand**: Lightweight state management
- **AWS Amplify**: Authentication and API integration
- **Lucide React**: Icon library

### Folder Structure

```
frontend/
├── public/
│   ├── favicon.png          # App icon (320x320)
│   └── splash.png           # Splash screen (1024x1024)
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── chat/            # Chat-specific components
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatHistory.tsx
│   │   │   └── MessageBubble.tsx
│   │   ├── auth/            # Auth components (from template)
│   │   │   ├── SignInForm.tsx
│   │   │   └── SignUpForm.tsx
│   │   └── layout/          # Layout components
│   │       ├── AppSidebar.tsx
│   │       └── PrivateLayout.tsx
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── SignIn.tsx
│   │   │   └── SignUp.tsx
│   │   ├── Dashboard.tsx    # Landing page after login
│   │   ├── Chat.tsx         # Main chat interface
│   │   └── Settings.tsx     # User settings
│   ├── store/
│   │   ├── chatStore.ts     # Chat state management
│   │   ├── authStore.ts     # Auth state (from template)
│   │   └── uiStore.ts       # UI state (loading, errors)
│   ├── services/
│   │   ├── agentService.ts  # API calls to Strands Agent
│   │   └── authService.ts   # Cognito integration
│   ├── types/
│   │   ├── chat.ts          # Chat-related types
│   │   └── api.ts           # API request/response types
│   ├── utils/
│   │   ├── formatters.ts    # Date, text formatting
│   │   └── validators.ts    # Form validation
│   ├── App.tsx
│   ├── main.tsx
│   └── routes.tsx
├── amplify_outputs.json     # AWS configuration
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── vite.config.ts
```

## Components and Interfaces

### Core Components

#### 1. Authentication Components (Reuse from Template)

**SignUpForm.tsx** - Extended with custom fields
```typescript
interface SignUpFormProps {
  onSuccess: () => void;
  onError: (error: string) => void;
}

interface SignUpFormData {
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  companyWebsite: string;
}
```

**SignInForm.tsx** - Standard Cognito sign-in
```typescript
interface SignInFormProps {
  onSuccess: () => void;
  onError: (error: string) => void;
}

interface SignInFormData {
  email: string;
  password: string;
}
```

#### 2. Chat Components

**ChatMessage.tsx** - Individual message display
```typescript
interface ChatMessageProps {
  message: Message;
  isUser: boolean;
}

interface Message {
  id: string;
  content: string;
  timestamp: Date;
  role: 'user' | 'assistant';
  status?: 'sending' | 'sent' | 'error';
}
```

**ChatInput.tsx** - Message input with send button
```typescript
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled: boolean;
  placeholder?: string;
}
```

**ChatHistory.tsx** - Scrollable message list
```typescript
interface ChatHistoryProps {
  messages: Message[];
  isLoading: boolean;
}
```

**MessageBubble.tsx** - Styled message container
```typescript
interface MessageBubbleProps {
  content: string;
  isUser: boolean;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}
```

#### 3. Layout Components (Reuse from Template)

**AppSidebar.tsx** - Navigation sidebar
- Dashboard link
- Chat link
- New Chat button
- Settings link
- Sign Out button

**PrivateLayout.tsx** - Authenticated page wrapper
- Sidebar on left
- Main content area on right
- Responsive mobile layout

#### 4. Page Components

**Dashboard.tsx** - Landing page
```typescript
interface DashboardProps {}

// Features:
// - Welcome message with user's company name
// - Quick start guide
// - Recent conversations (if any)
// - Sample queries to get started
```

**Chat.tsx** - Main chat interface
```typescript
interface ChatPageProps {}

// Features:
// - Full-height chat history
// - Fixed input at bottom
// - Loading states
// - Error handling
// - Auto-scroll to latest message
```

**Settings.tsx** - User preferences
```typescript
interface SettingsProps {}

// Features:
// - Display user info (email, company)
// - Theme preferences (if applicable)
// - Clear conversation history
// - Account management
```

### shadcn Components to Use

1. **Button** - Send button, action buttons
2. **Input** - Text input for messages, form fields
3. **Card** - Message bubbles, dashboard cards
4. **ScrollArea** - Chat history scrolling
5. **Avatar** - User and assistant avatars
6. **Badge** - Status indicators
7. **Separator** - Visual dividers
8. **Form** - Sign-up and settings forms
9. **Label** - Form labels
10. **Alert** - Error messages
11. **Skeleton** - Loading states
12. **Textarea** - Multi-line message input

## Data Models

### Message Model

```typescript
interface Message {
  id: string;                    // Unique message ID (UUID)
  content: string;               // Message text
  role: 'user' | 'assistant';   // Who sent the message
  timestamp: Date;               // When message was sent
  status?: MessageStatus;        // Message delivery status
  sessionId?: string;            // Conversation session ID
}

type MessageStatus = 'sending' | 'sent' | 'error';
```

### Conversation Model

```typescript
interface Conversation {
  id: string;                    // Unique conversation ID
  title: string;                 // Auto-generated or user-defined
  messages: Message[];           // Array of messages
  createdAt: Date;              // Conversation start time
  updatedAt: Date;              // Last message time
}
```

### User Model (Extended Cognito)

```typescript
interface User {
  id: string;                    // Cognito user ID
  email: string;                 // User email
  companyName: string;           // Custom attribute
  companyWebsite: string;        // Custom attribute
  createdAt: Date;              // Account creation date
}
```

### API Request/Response Models

```typescript
// Request to Strands Agent
interface AgentInvocationRequest {
  input: {
    prompt: string;              // User message
  };
  session_id?: string;           // Optional session ID
}

// Response from Strands Agent
interface AgentInvocationResponse {
  output: {
    message: string;             // Agent response
    timestamp: string;           // ISO 8601 timestamp
    model: string;               // Model used
    session_id?: string;         // Session ID
  };
}

// Error response
interface AgentErrorResponse {
  error: {
    type: string;                // Error type
    message: string;             // User-friendly message
    details?: string;            // Technical details (dev only)
    suggestions?: string[];      // Actionable suggestions
  };
}
```

## State Management (Zustand)

### Chat Store

```typescript
interface ChatState {
  // State
  messages: Message[];
  currentSessionId: string | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  sendMessage: (content: string) => Promise<void>;
  clearMessages: () => void;
  startNewSession: () => void;
  setError: (error: string | null) => void;
}

const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  currentSessionId: null,
  isLoading: false,
  error: null,
  
  sendMessage: async (content: string) => {
    // Implementation in services section
  },
  
  clearMessages: () => set({ messages: [], currentSessionId: null }),
  
  startNewSession: () => {
    set({ 
      messages: [], 
      currentSessionId: crypto.randomUUID(),
      error: null 
    });
  },
  
  setError: (error: string | null) => set({ error }),
}));
```

### Auth Store (From Template)

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (data: SignUpFormData) => Promise<void>;
  signOut: () => Promise<void>;
  checkAuth: () => Promise<void>;
}
```

### UI Store

```typescript
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}
```

## API Integration

### Agent Service

```typescript
// services/agentService.ts

import { post } from 'aws-amplify/api';

export class AgentService {
  private static readonly ENDPOINT_NAME = 'StrandsAgentAPI';
  private static readonly INVOCATION_PATH = '/invocations';
  
  /**
   * Send a message to the Strands Agent
   */
  static async sendMessage(
    prompt: string, 
    sessionId?: string
  ): Promise<AgentInvocationResponse> {
    try {
      const request: AgentInvocationRequest = {
        input: { prompt },
        ...(sessionId && { session_id: sessionId })
      };
      
      const response = await post({
        apiName: this.ENDPOINT_NAME,
        path: this.INVOCATION_PATH,
        options: {
          body: request,
          headers: {
            'Content-Type': 'application/json'
          }
        }
      }).response;
      
      const data = await response.body.json();
      return data as AgentInvocationResponse;
      
    } catch (error) {
      // Transform error to user-friendly format
      throw this.handleError(error);
    }
  }
  
  /**
   * Transform API errors to user-friendly messages
   */
  private static handleError(error: any): Error {
    if (error.response?.status === 503) {
      return new Error('The agent service is temporarily unavailable. Please try again in a moment.');
    }
    
    if (error.response?.status === 400) {
      return new Error('Invalid request. Please check your message and try again.');
    }
    
    if (error.message?.includes('Network')) {
      return new Error('Network error. Please check your connection and try again.');
    }
    
    return new Error('An unexpected error occurred. Please try again.');
  }
}
```

### Auth Service (Cognito Integration)

```typescript
// services/authService.ts

import { signUp, signIn, signOut, getCurrentUser } from 'aws-amplify/auth';

export class AuthService {
  /**
   * Sign up with custom Cognito attributes
   */
  static async signUp(data: SignUpFormData): Promise<void> {
    await signUp({
      username: data.email,
      password: data.password,
      options: {
        userAttributes: {
          email: data.email,
          'custom:company_name': data.companyName,
          'custom:company_website': data.companyWebsite
        }
      }
    });
  }
  
  /**
   * Sign in user
   */
  static async signIn(email: string, password: string): Promise<void> {
    await signIn({
      username: email,
      password: password
    });
  }
  
  /**
   * Sign out user
   */
  static async signOut(): Promise<void> {
    await signOut();
  }
  
  /**
   * Get current authenticated user
   */
  static async getCurrentUser(): Promise<User | null> {
    try {
      const { username, userId, signInDetails } = await getCurrentUser();
      const attributes = await fetchUserAttributes();
      
      return {
        id: userId,
        email: attributes.email || '',
        companyName: attributes['custom:company_name'] || '',
        companyWebsite: attributes['custom:company_website'] || '',
        createdAt: new Date()
      };
    } catch {
      return null;
    }
  }
}
```

## Routing Structure

```typescript
// routes.tsx

import { createBrowserRouter } from 'react-router-dom';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      {
        path: 'signin',
        element: <SignIn />
      },
      {
        path: 'signup',
        element: <SignUp />
      }
    ]
  },
  {
    path: '/app',
    element: <PrivateLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/app/dashboard" replace />
      },
      {
        path: 'dashboard',
        element: <Dashboard />
      },
      {
        path: 'chat',
        element: <Chat />
      },
      {
        path: 'settings',
        element: <Settings />
      }
    ]
  },
  {
    path: '*',
    element: <Navigate to="/signin" replace />
  }
]);
```

## Error Handling

### Error Types and User Messages

1. **Network Errors**
   - Message: "Unable to connect. Please check your internet connection."
   - Action: Retry button

2. **Service Unavailable (503)**
   - Message: "The agent is temporarily unavailable. Please try again in a moment."
   - Action: Retry button

3. **Authentication Errors**
   - Message: "Invalid email or password. Please try again."
   - Action: Clear form, allow retry

4. **Validation Errors**
   - Message: Specific field errors (e.g., "Please enter a valid email address")
   - Action: Highlight invalid fields

5. **Unexpected Errors**
   - Message: "Something went wrong. Please try again."
   - Action: Retry button, contact support link

### Error Display Component

```typescript
interface ErrorAlertProps {
  error: string;
  onRetry?: () => void;
  onDismiss?: () => void;
}

// Use shadcn Alert component with custom styling
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy load pages
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Chat = lazy(() => import('./pages/Chat'));
const Settings = lazy(() => import('./pages/Settings'));

// Wrap in Suspense with loading fallback
<Suspense fallback={<LoadingSpinner />}>
  <Outlet />
</Suspense>
```

### Message Virtualization

For long conversation histories, implement virtual scrolling:
- Use `react-window` or `react-virtual` for efficient rendering
- Only render visible messages
- Maintain scroll position on new messages

### Optimistic Updates

```typescript
// Add message to UI immediately
const optimisticMessage: Message = {
  id: crypto.randomUUID(),
  content: userInput,
  role: 'user',
  timestamp: new Date(),
  status: 'sending'
};

set(state => ({
  messages: [...state.messages, optimisticMessage]
}));

// Send to API
try {
  const response = await AgentService.sendMessage(userInput);
  // Update message status to 'sent'
} catch (error) {
  // Update message status to 'error'
}
```

### Caching Strategy

- Cache conversation history in localStorage
- Restore on page refresh
- Clear on sign out
- Implement TTL for cache expiration

## Testing Strategy

### Unit Tests

1. **Component Tests**
   - ChatMessage rendering
   - ChatInput validation
   - Form validation
   - Error display

2. **Service Tests**
   - AgentService API calls
   - AuthService Cognito integration
   - Error handling

3. **Store Tests**
   - State updates
   - Action execution
   - Side effects

### Integration Tests

1. **User Flows**
   - Sign up with custom attributes
   - Sign in and navigate to chat
   - Send message and receive response
   - Start new conversation
   - Sign out

2. **Error Scenarios**
   - Network failure handling
   - Service unavailable handling
   - Invalid input handling

### E2E Tests (Optional)

- Full user journey from sign-up to chat interaction
- Use Playwright or Cypress

## Deployment Configuration

### amplify_outputs.json Structure

```json
{
  "auth": {
    "user_pool_id": "us-east-1_XXXXXXXXX",
    "user_pool_client_id": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
    "identity_pool_id": "us-east-1:XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "region": "us-east-1",
    "oauth": {
      "domain": "your-domain.auth.us-east-1.amazoncognito.com",
      "scope": ["email", "openid", "profile"],
      "redirect_sign_in": "http://localhost:5173/",
      "redirect_sign_out": "http://localhost:5173/",
      "response_type": "code"
    }
  },
  "api": {
    "StrandsAgentAPI": {
      "endpoint": "https://XXXXXXXXXX.execute-api.us-east-1.amazonaws.com/prod/mss-template/agent",
      "region": "us-east-1"
    }
  }
}
```

### Environment Variables

```bash
# .env.local
VITE_APP_NAME="re:Invent Planner"
VITE_APP_DESCRIPTION="AI-powered conference planning assistant"
VITE_PRIMARY_COLOR="#FF9900"  # AWS Orange
```

### Build Configuration

```typescript
// vite.config.ts
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'aws-vendor': ['aws-amplify'],
          'ui-vendor': ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu']
        }
      }
    }
  }
});
```

## Security Considerations

1. **Authentication**
   - All API calls include Cognito JWT tokens
   - Tokens automatically refreshed by Amplify
   - Secure token storage in memory

2. **Input Validation**
   - Client-side validation for all forms
   - Sanitize user input before display
   - Prevent XSS attacks

3. **HTTPS Only**
   - All API calls over HTTPS
   - Secure cookie flags

4. **CORS Configuration**
   - API Gateway configured with appropriate CORS headers
   - Restrict origins in production

## Accessibility

1. **Keyboard Navigation**
   - All interactive elements keyboard accessible
   - Proper tab order
   - Focus indicators

2. **Screen Reader Support**
   - Semantic HTML
   - ARIA labels where needed
   - Alt text for images

3. **Color Contrast**
   - WCAG AA compliance
   - High contrast mode support

4. **Responsive Text**
   - Scalable font sizes
   - Readable line lengths

## Future Enhancements

1. **Conversation Management**
   - Save multiple conversations
   - Search conversation history
   - Export conversations

2. **Rich Message Formatting**
   - Markdown support in messages
   - Code syntax highlighting
   - Link previews

3. **Real-time Updates**
   - WebSocket connection for streaming responses
   - Typing indicators
   - Read receipts

4. **Personalization**
   - User preferences
   - Favorite queries
   - Custom themes

5. **Analytics**
   - Usage tracking
   - Error monitoring
   - Performance metrics
