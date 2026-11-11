# Design Document

## Overview

This feature implements persistent chat session management for the re:Invent Planner frontend application. The system will automatically create and save chat sessions identified by unique hashes (UUIDs), display session IDs in the UI, and retrieve conversation history from AWS Bedrock AgentCore Memory through a Backend-for-Frontend (BFF) Lambda function.

The design follows Clean Architecture principles and integrates with the existing Strands Agent infrastructure, leveraging AWS Bedrock's AgentCore Memory service for message persistence and retrieval.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Session List │  │ Chat Window  │  │ Session ID Display   │  │
│  │  Component   │  │  Component   │  │    Component         │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────────┘  │
│         │                  │                                     │
│         └──────────────────┴─────────────────────────────────┐  │
│                                                               │  │
│                        ┌──────────────────────────────────┐  │  │
│                        │   Session Service (TypeScript)   │  │  │
│                        │  - List sessions                 │  │  │
│                        │  - Get session messages          │  │  │
│                        │  - Switch sessions               │  │  │
│                        └──────────────┬───────────────────┘  │  │
└───────────────────────────────────────┼──────────────────────┘  │
                                        │                          │
                                        │ HTTPS/API Gateway        │
                                        │                          │
┌───────────────────────────────────────┼──────────────────────────┐
│                         AWS Backend   │                          │
│                                       ▼                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │         BFF Lambda Function (Python)                       │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  List Sessions & Messages Endpoint                   │ │ │
│  │  │  - List sessions from AgentCore Memory               │ │ │
│  │  │  - Fetch messages for each session                   │ │ │
│  │  │  - Aggregate and return combined data                │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────┬───────────────────────────────┘ │
│                                │                                 │
│                                ▼                                 │
│                   ┌──────────────────────────────┐              │
│                   │  Bedrock AgentCore Memory    │              │
│                   │  - Session metadata          │              │
│                   │  - Conversation events       │              │
│                   │  - Message payloads          │              │
│                   │  - Timestamps                │              │
│                   │  (Single Source of Truth)    │              │
│                   └──────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Session Creation Flow**:
   - User sends first message → Frontend generates UUID session hash
   - Frontend sends message with session_id and actor_id to Strands Agent
   - Agent stores conversation in AgentCore Memory (automatic via session manager)
   - No additional storage needed - AgentCore Memory is the source of truth

2. **Session Retrieval Flow**:
   - Frontend requests session list from BFF Lambda
   - BFF calls AgentCore Memory API to list sessions for actor_id
   - BFF calls AgentCore Memory API for each session's messages
   - BFF aggregates and returns combined data to frontend

3. **Session Display Flow**:
   - Frontend displays session list with session hashes
   - User clicks session → Frontend loads messages from BFF
   - Chat window displays conversation history

## Components and Interfaces

### 1. Frontend Components

#### SessionService (TypeScript)
```typescript
interface SessionMetadata {
  session_id: string;
  actor_id: string;
  created_at: string;
  last_activity: string;
}

interface SessionMessage {
  event_id: string;
  timestamp: string;
  role: 'user' | 'assistant';
  content: string;
}

interface SessionWithMessages {
  metadata: SessionMetadata;
  messages: SessionMessage[];
}

class SessionService {
  // Create new session metadata
  async createSession(sessionId: string, actorId: string): Promise<SessionMetadata>
  
  // List all sessions for current user
  async listSessions(): Promise<SessionMetadata[]>
  
  // Get session with all messages
  async getSessionWithMessages(sessionId: string): Promise<SessionWithMessages>
}
```

#### Session List Component
- Displays all user sessions
- Shows truncated session hash (first 8 characters)
- Highlights active session
- Allows session switching

#### Session ID Display Component
- Shows current session hash
- Provides copy-to-clipboard functionality
- Displays full hash on hover/click

### 2. Backend Components

#### BFF Lambda Function

**Module**: `src/modules/list_session_messages/`

**Use Case**: `ListSessionMessagesUsecase`
```python
class ListSessionMessagesUsecase:
    def __init__(
        self,
        agentcore_client: AgentCoreMemoryClient
    ):
        self.agentcore_client = agentcore_client
    
    def __call__(self, actor_id: str, memory_id: str) -> List[SessionWithMessages]:
        # List all sessions for user from AgentCore Memory
        sessions = self.agentcore_client.list_sessions(
            memory_id=memory_id,
            actor_id=actor_id
        )
        
        # For each session, fetch messages from AgentCore Memory
        result = []
        for session in sessions:
            messages = self.agentcore_client.list_events(
                memory_id=memory_id,
                actor_id=actor_id,
                session_id=session['session_id'],
                include_payloads=True
            )
            result.append({
                'session_id': session['session_id'],
                'created_at': session.get('created_at'),
                'last_activity': session.get('last_activity'),
                'messages': messages
            })
        
        return result
```

**Controller**: `ListSessionMessagesController`
- Validates actor_id from JWT token
- Calls use case with memory_id from config
- Returns formatted response

**Presenter**: `list_session_messages_presenter.py`
- Lambda handler
- Integrates with API Gateway
- Returns JSON response

#### AgentCore Memory Client

**Module**: `src/shared/infra/external/bedrock/agentcore_memory_client.py`

```python
class AgentCoreMemoryClient:
    def __init__(self, region_name: str = "us-east-1"):
        self.client = boto3.client("bedrock-agent-runtime", region_name=region_name)
    
    def list_sessions(
        self,
        memory_id: str,
        actor_id: str,
        max_results: int = 100
    ) -> List[Dict]:
        """
        List all sessions for an actor from AgentCore Memory.
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        next_token = None
        
        while True:
            params = {
                'memoryId': memory_id,
                'actorId': actor_id,
                'maxResults': max_results
            }
            if next_token:
                params['nextToken'] = next_token
            
            response = self.client.list_sessions(**params)
            sessions.extend(response.get('sessions', []))
            
            next_token = response.get('nextToken')
            if not next_token:
                break
        
        return sessions
    
    def list_events(
        self,
        memory_id: str,
        actor_id: str,
        session_id: str,
        include_payloads: bool = True,
        max_results: int = 100
    ) -> List[Dict]:
        """
        List all events (messages) for a session from AgentCore Memory.
        
        Returns:
            List of event dictionaries with message content
        """
        events = []
        next_token = None
        
        while True:
            params = {
                'memoryId': memory_id,
                'actorId': actor_id,
                'sessionId': session_id,
                'includePayloads': include_payloads,
                'maxResults': max_results
            }
            if next_token:
                params['nextToken'] = next_token
            
            response = self.client.list_events(**params)
            events.extend(response.get('events', []))
            
            next_token = response.get('nextToken')
            if not next_token:
                break
        
        return self._parse_events(events)
    
    def _parse_events(self, events: List[Dict]) -> List[Dict]:
        """Parse and format events from AgentCore Memory response"""
        parsed = []
        for event in events:
            parsed.append({
                'event_id': event['eventId'],
                'timestamp': event['timestamp'],
                'role': self._extract_role(event),
                'content': self._extract_content(event)
            })
        return parsed
    
    def _extract_role(self, event: Dict) -> str:
        """Extract role from event payload"""
        # Implementation depends on AgentCore Memory event structure
        return event.get('payload', {}).get('role', 'unknown')
    
    def _extract_content(self, event: Dict) -> str:
        """Extract message content from event payload"""
        # Implementation depends on AgentCore Memory event structure
        return event.get('payload', {}).get('content', '')
```

### 3. Data Storage

#### AgentCore Memory as Single Source of Truth

All session and message data is stored in AWS Bedrock AgentCore Memory:

**Session Storage**:
- Automatically created when first message is sent with session_id
- Indexed by memory_id, actor_id, and session_id
- Metadata includes creation time and last activity

**Message Storage**:
- Each message stored as an event in AgentCore Memory
- Events include timestamp, role (user/assistant), and content
- Payloads contain full message data

**Benefits**:
- No data synchronization needed
- Single API for all session operations
- Built-in conversation history management
- Automatic timestamp tracking

## Data Models

### Frontend Models

```typescript
// Session metadata stored in DynamoDB
interface SessionMetadata {
  session_id: string;        // UUID
  actor_id: string;          // Cognito user sub
  created_at: string;        // ISO 8601 timestamp
  last_activity: string;     // ISO 8601 timestamp
}

// Message from AgentCore Memory
interface SessionMessage {
  event_id: string;
  timestamp: string;
  role: 'user' | 'assistant';
  content: string;
}

// Combined session data
interface SessionWithMessages {
  metadata: SessionMetadata;
  messages: SessionMessage[];
}
```

### Backend Models

```python
# Session metadata from AgentCore Memory
@dataclass
class SessionMetadata:
    session_id: str
    actor_id: str
    created_at: datetime
    last_activity: datetime

# AgentCore Memory Event
@dataclass
class SessionEvent:
    event_id: str
    timestamp: datetime
    role: str  # 'user' or 'assistant'
    content: str

# Combined session with messages
@dataclass
class SessionWithMessages:
    session_id: str
    created_at: datetime
    last_activity: datetime
    messages: List[SessionEvent]
```



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Unique session hash generation
*For any* new conversation, the generated session hash should be a valid UUID and unique across all sessions
**Validates: Requirements 1.1, 1.2**

### Property 2: Session persistence
*For any* created session, querying AgentCore Memory with the session_id should return the session metadata
**Validates: Requirements 1.3**

### Property 3: Session list completeness
*For any* actor_id with multiple sessions, listing sessions should return all sessions associated with that actor
**Validates: Requirements 1.4**

### Property 4: Session ID display presence
*For any* active session, the session ID should be present in the UI DOM
**Validates: Requirements 2.1**

### Property 5: Clipboard copy functionality
*For any* displayed session ID, the copy function should successfully copy the full session ID to clipboard
**Validates: Requirements 2.3**

### Property 6: Message retrieval completeness
*For any* session with messages, retrieving messages from AgentCore Memory should return all messages for that session
**Validates: Requirements 3.1**

### Property 7: API parameter correctness
*For any* message retrieval request, the AgentCore Memory client should be called with the correct memory_id, actor_id, and session_id
**Validates: Requirements 3.2**

### Property 8: Message payload completeness
*For any* retrieved message, the message object should contain event_id, timestamp, role, and content fields
**Validates: Requirements 3.3**

### Property 9: Chronological message ordering
*For any* list of messages, they should be ordered by timestamp in ascending order
**Validates: Requirements 3.4**

### Property 10: BFF session listing
*For any* authenticated user request to the BFF, all sessions for that actor_id should be returned
**Validates: Requirements 4.1**

### Property 11: Session metadata completeness
*For any* session in the BFF response, it should include session_id, created_at, and last_activity fields
**Validates: Requirements 4.2**

### Property 12: AgentCore Memory integration
*For any* session details request, the BFF should call AgentCore Memory list_events for each session
**Validates: Requirements 4.3**

### Property 13: Payload inclusion
*For any* AgentCore Memory list_events call, includePayloads should be set to True
**Validates: Requirements 4.4**

### Property 14: Response structure
*For any* BFF response, it should contain an array of objects with session_id, created_at, last_activity, and messages fields
**Validates: Requirements 4.5**

### Property 15: Session switching loads messages
*For any* session click event, the system should trigger loading of that session's messages
**Validates: Requirements 5.1**

### Property 16: State preservation during switch
*For any* session switch, the current session's messages should remain in memory before loading the new session
**Validates: Requirements 5.2**

### Property 17: Message display completeness
*For any* loaded session, all messages should be rendered in the chat interface
**Validates: Requirements 5.3**

### Property 18: Active session indication
*For any* active session, the UI should visually distinguish it from inactive sessions
**Validates: Requirements 5.4**

### Property 19: No data loss on switch
*For any* session switch operation, no messages should be lost from either the current or target session
**Validates: Requirements 5.5**

### Property 20: Automatic session save
*For any* new message sent, if the session is new, it should be automatically persisted to AgentCore Memory
**Validates: Requirements 6.1**

### Property 21: Session metadata persistence
*For any* saved session, AgentCore Memory should contain the session_id and timestamp metadata
**Validates: Requirements 6.2**

### Property 22: Session persistence across refresh
*For any* saved session, refreshing the browser should not lose the session from the session list
**Validates: Requirements 6.3**

### Property 23: AgentCore Memory storage
*For any* created session, it should be stored in AgentCore Memory (not local storage only)
**Validates: Requirements 6.4**

### Property 24: Recent activity ordering
*For any* list of sessions, they should be ordered by last_activity timestamp in descending order
**Validates: Requirements 6.5**

### Property 25: BFF API integration
*For any* session data request, the frontend should call the BFF Lambda via API Gateway
**Validates: Requirements 7.1**

### Property 26: Authentication token inclusion
*For any* API request to the BFF, the request should include valid authentication tokens
**Validates: Requirements 7.2**

### Property 27: Response parsing correctness
*For any* BFF response, the frontend should correctly parse and display the session and message data
**Validates: Requirements 7.3**

### Property 28: Retry with exponential backoff
*For any* failed API call, the system should retry with exponentially increasing delays
**Validates: Requirements 7.4**

## Error Handling

### Frontend Error Handling

1. **Network Errors**:
   - Display user-friendly error messages
   - Implement retry logic with exponential backoff
   - Show offline indicator when network is unavailable

2. **API Errors**:
   - 401 Unauthorized: Redirect to login
   - 403 Forbidden: Show permission error
   - 404 Not Found: Show "session not found" message
   - 500 Server Error: Show generic error with retry option

3. **AgentCore Memory Errors**:
   - Session not found: Remove from local session list
   - Rate limiting: Implement backoff and queue requests
   - Timeout: Show timeout message with retry option

### Backend Error Handling

1. **AgentCore Memory API Errors**:
   - Handle pagination errors gracefully
   - Log errors for debugging
   - Return appropriate HTTP status codes

2. **Authentication Errors**:
   - Validate JWT tokens
   - Return 401 for invalid/expired tokens
   - Return 403 for insufficient permissions

3. **Validation Errors**:
   - Validate actor_id format
   - Validate session_id UUID format
   - Return 400 for invalid parameters

## Testing Strategy

### Unit Testing

**Frontend Components**:
- SessionService: Test API calls, error handling, data transformation
- Session List Component: Test rendering, click handlers, active state
- Session ID Display: Test formatting, copy functionality, hover behavior

**Backend Components**:
- AgentCoreMemoryClient: Test list_sessions, list_events, pagination
- ListSessionMessagesUsecase: Test session aggregation logic
- ListSessionMessagesController: Test validation, error handling

**Test Coverage Goals**:
- AgentCoreMemoryClient: 100% coverage of API methods
- Use Case: 100% coverage of business logic
- Controller: 100% coverage of HTTP handling
- Frontend Services: 100% coverage of API integration

### Property-Based Testing

**Property Testing Library**: Use `hypothesis` for Python backend, `fast-check` for TypeScript frontend

**Backend Properties**:
- Property 6: Message retrieval completeness
- Property 9: Chronological message ordering
- Property 10: BFF session listing
- Property 24: Recent activity ordering

**Frontend Properties**:
- Property 1: Unique session hash generation
- Property 19: No data loss on switch
- Property 28: Retry with exponential backoff

**Configuration**:
- Minimum 100 iterations per property test
- Each property test tagged with: `**Feature: chat-session-management, Property {number}: {property_text}**`

### Integration Testing

1. **AgentCore Memory Integration**:
   - Test actual API calls to AgentCore Memory (mocked in CI)
   - Verify pagination handling
   - Test error scenarios

2. **End-to-End Flow**:
   - Create session → Send message → Retrieve session list → Load messages
   - Test session switching
   - Test error recovery

### Manual Testing Scenarios

1. **Session Management**:
   - Create multiple sessions
   - Switch between sessions
   - Verify session list updates
   - Test session ID display and copy

2. **Error Scenarios**:
   - Network disconnection during session load
   - Invalid session ID
   - Expired authentication token

3. **Performance**:
   - Load time with many sessions (50+)
   - Message retrieval time for long conversations (100+ messages)
   - UI responsiveness during session switching

## Performance Considerations

### Frontend Optimization

1. **Lazy Loading**:
   - Load session list on demand
   - Load messages only when session is selected
   - Implement virtual scrolling for long message lists

2. **Caching**:
   - Cache session list in memory
   - Cache loaded messages per session
   - Invalidate cache on new messages

3. **Debouncing**:
   - Debounce session list refresh
   - Throttle scroll events in message list

### Backend Optimization

1. **Pagination**:
   - Limit sessions per request (default: 100)
   - Limit messages per session (default: 100)
   - Implement cursor-based pagination

2. **Parallel Processing**:
   - Fetch messages for multiple sessions in parallel
   - Use asyncio for concurrent AgentCore Memory calls

3. **Response Size**:
   - Limit message content length in list view
   - Provide separate endpoint for full message content

### AgentCore Memory Optimization

1. **Batch Requests**:
   - Minimize number of API calls
   - Use pagination efficiently
   - Cache responses when appropriate

2. **Rate Limiting**:
   - Implement exponential backoff
   - Queue requests during high load
   - Monitor API quotas

## Security Considerations

### Authentication & Authorization

1. **JWT Token Validation**:
   - Validate token signature
   - Check token expiration
   - Verify actor_id matches token claims

2. **Session Access Control**:
   - Users can only access their own sessions (actor_id validation)
   - Validate session_id belongs to actor_id
   - Prevent session enumeration attacks

### Data Privacy

1. **Message Content**:
   - Messages stored in AgentCore Memory (AWS managed)
   - No sensitive data in logs
   - Comply with data retention policies

2. **Session IDs**:
   - Use cryptographically secure UUIDs
   - Don't expose internal identifiers
   - Validate UUID format on backend

### API Security

1. **Rate Limiting**:
   - Implement per-user rate limits
   - Prevent abuse of session listing
   - Monitor for suspicious patterns

2. **Input Validation**:
   - Sanitize all user inputs
   - Validate UUID formats
   - Prevent injection attacks

## Deployment Considerations

### Infrastructure

1. **Lambda Configuration**:
   - Memory: 512 MB (adjust based on load)
   - Timeout: 30 seconds
   - Concurrency: Auto-scaling
   - Environment variables: MEMORY_ID, AWS_REGION

2. **API Gateway**:
   - CORS configuration for frontend domain
   - Request/response validation
   - API key or Cognito authorizer

3. **IAM Permissions**:
   - Lambda execution role needs:
     - `bedrock-agent-runtime:ListSessions`
     - `bedrock-agent-runtime:ListEvents`
     - CloudWatch Logs permissions

### Monitoring

1. **CloudWatch Metrics**:
   - Lambda invocation count
   - Error rate
   - Duration
   - AgentCore Memory API call count

2. **CloudWatch Logs**:
   - Log all API errors
   - Log session access patterns
   - Monitor for anomalies

3. **Alarms**:
   - High error rate (>5%)
   - High latency (>3 seconds)
   - AgentCore Memory API throttling

### Configuration Management

1. **Environment Variables**:
   - `MEMORY_ID`: AgentCore Memory identifier
   - `AWS_REGION`: AWS region for AgentCore Memory
   - `MAX_SESSIONS`: Maximum sessions to return
   - `MAX_MESSAGES_PER_SESSION`: Maximum messages per session

2. **Feature Flags**:
   - Enable/disable session management
   - Enable/disable message caching
   - Enable/disable parallel processing
