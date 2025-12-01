# Design Document: Agent Streaming Support

## Overview

This design implements streaming response support for the Strands re:Invent agent Lambda function using AWS Lambda response streaming, Lambda Web Adapter, and Strands' `stream_async()` method. The solution enables real-time progressive delivery of agent responses to improve user experience while maintaining the existing FastAPI architecture and authentication mechanisms.

The implementation adds a new `/invocations/stream` endpoint that returns Server-Sent Events (SSE) formatted responses, allowing the frontend to display agent output as it's generated rather than waiting for complete responses.

## Architecture

### High-Level Architecture

```
┌─────────────┐
│   Frontend  │
│   (React)   │
└──────┬──────┘
       │ POST /agent/invocations/stream
       │ (with Cognito JWT)
       ▼
┌─────────────────────────────────────┐
│   API Gateway (with Cognito Auth)  │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Lambda Function URL (Streaming)  │
│   + Lambda Web Adapter              │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   FastAPI Application               │
│   - /invocations (existing)         │
│   - /invocations/stream (new)       │
└──────┬──────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Strands Agent                     │
│   - stream_async() method           │
│   - Event filtering                 │
└──────┬──────────────────────────────┘
       │
       ├──────────────┬─────────────────┐
       ▼              ▼                 ▼
┌──────────┐  ┌──────────────┐  ┌──────────────┐
│ Bedrock  │  │ MCP Server   │  │ AgentCore    │
│ (Claude) │  │ (Sessions)   │  │ Memory       │
└──────────┘  └──────────────┘  └──────────────┘
```

### Component Interactions

1. **Frontend** sends POST request to `/agent/invocations/stream` with Cognito JWT
2. **API Gateway** validates JWT and forwards to Lambda Function URL
3. **Lambda Web Adapter** converts Lambda streaming response to HTTP streaming
4. **FastAPI** handles the request and calls Strands agent's `stream_async()`
5. **Strands Agent** processes the prompt, emitting events as it generates responses
6. **Event Filter** transforms agent events into SSE-formatted messages
7. **Frontend** receives and displays events in real-time

## Components and Interfaces

### 1. Streaming Endpoint (`entrypoint.py`)

**New Endpoint:**
```python
@app.post("/invocations/stream")
async def invoke_agent_stream(
    request: InvocationRequest,
    http_request: Request
) -> StreamingResponse
```

**Responsibilities:**
- Validate authentication (same as non-streaming endpoint)
- Extract actor_id from Cognito JWT
- Create agent instance with session context
- Call `stream_async()` and filter events
- Format events as SSE messages
- Handle errors gracefully

**Event Generator:**
```python
async def generate_stream_events(
    agent: Agent,
    user_message: str,
    session_id: Optional[str],
    actor_id: str
) -> AsyncGenerator[str, None]:
    """
    Generate SSE-formatted events from agent stream.
    
    Yields:
        SSE-formatted strings: "data: {json}\n\n"
    """
```

### 2. Event Filtering and Formatting

**Event Types to Emit:**

1. **Text Events** - Agent-generated text chunks
```json
{
  "type": "text",
  "data": "Here are the sessions about serverless...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

2. **Tool Call Events** - When agent invokes tools
```json
{
  "type": "tool_call",
  "tool_name": "reinvent__search_sessions",
  "tool_id": "toolu_123",
  "status": "started",
  "timestamp": "2024-01-15T10:30:01Z"
}
```

3. **Tool Result Events** - When tool execution completes
```json
{
  "type": "tool_result",
  "tool_id": "toolu_123",
  "status": "completed",
  "timestamp": "2024-01-15T10:30:02Z"
}
```

4. **Done Event** - Stream completion with metadata
```json
{
  "type": "done",
  "session_id": "sess_123",
  "usage": {
    "input_tokens": 150,
    "output_tokens": 300,
    "total_tokens": 450
  },
  "metadata": {
    "duration_seconds": 3.5,
    "tool_calls_count": 2
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

5. **Error Event** - When errors occur
```json
{
  "type": "error",
  "error": {
    "type": "MCPConnectionError",
    "message": "Unable to connect to session data service",
    "suggestions": ["Try again in a few moments"]
  },
  "timestamp": "2024-01-15T10:30:03Z"
}
```

**Event Filtering Logic:**
```python
def should_emit_event(event: Dict[str, Any]) -> bool:
    """
    Determine if an agent event should be emitted to the client.
    
    Emit:
    - Text data events
    - Tool use events
    - Tool result events
    - Completion events
    
    Filter out:
    - Internal lifecycle events (init_event_loop, start_event_loop)
    - Message creation events
    - Force stop events (unless error)
    """
```

### 3. Lambda Configuration (CDK)

**Function URL with Streaming:**
```python
# Enable response streaming
self.agent_function_url = self.agent_function.add_function_url(
    auth_type=lambda_.FunctionUrlAuthType.AWS_IAM,
    invoke_mode=lambda_.InvokeMode.RESPONSE_STREAM  # Enable streaming
)
```

**API Gateway Integration:**
- Keep existing API Gateway for authentication
- API Gateway forwards to Function URL
- Lambda Web Adapter handles streaming conversion

**Environment Variables:**
```python
envs['AWS_LWA_INVOKE_MODE'] = 'RESPONSE_STREAM'  # Enable streaming mode
```

### 4. Frontend Integration

**Streaming Client (TypeScript):**
```typescript
async function* streamAgentResponse(
  prompt: string,
  sessionId?: string,
  language: string = 'pt'
): AsyncGenerator<AgentEvent, void, unknown> {
  const response = await fetch('/api/agent/invocations/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`
    },
    body: JSON.stringify({
      input: { prompt, language },
      session_id: sessionId
    })
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader!.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') return;
        
        try {
          const event = JSON.parse(data);
          yield event;
        } catch (e) {
          console.error('Failed to parse event:', data);
        }
      }
    }
  }
}
```

**React Component Usage:**
```typescript
const handleStreamingQuery = async (prompt: string) => {
  setIsStreaming(true);
  setResponse('');

  try {
    for await (const event of streamAgentResponse(prompt, sessionId)) {
      switch (event.type) {
        case 'text':
          setResponse(prev => prev + event.data);
          break;
        case 'tool_call':
          setToolStatus(`Using ${event.tool_name}...`);
          break;
        case 'done':
          setUsageStats(event.usage);
          break;
        case 'error':
          setError(event.error.message);
          break;
      }
    }
  } catch (error) {
    setError('Connection lost. Please try again.');
  } finally {
    setIsStreaming(false);
  }
};
```

## Data Models

### Request Models

```python
class InvocationRequest(BaseModel):
    """Request model for both streaming and non-streaming invocations."""
    input: Dict[str, Any] = Field(
        ...,
        description="Input data containing prompt and optional language"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation continuity"
    )
```

### Response Models

```python
class StreamEvent(BaseModel):
    """Base model for stream events."""
    type: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="ISO 8601 timestamp")

class TextEvent(StreamEvent):
    """Text generation event."""
    type: Literal["text"] = "text"
    data: str = Field(..., description="Generated text chunk")

class ToolCallEvent(StreamEvent):
    """Tool invocation event."""
    type: Literal["tool_call"] = "tool_call"
    tool_name: str = Field(..., description="Name of the tool")
    tool_id: str = Field(..., description="Unique tool invocation ID")
    status: Literal["started"] = "started"

class ToolResultEvent(StreamEvent):
    """Tool result event."""
    type: Literal["tool_result"] = "tool_result"
    tool_id: str = Field(..., description="Tool invocation ID")
    status: Literal["completed", "error"] = "completed"

class DoneEvent(StreamEvent):
    """Stream completion event."""
    type: Literal["done"] = "done"
    session_id: Optional[str] = Field(None, description="Session ID")
    usage: Dict[str, int] = Field(..., description="Token usage statistics")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class ErrorEvent(StreamEvent):
    """Error event."""
    type: Literal["error"] = "error"
    error: Dict[str, Any] = Field(..., description="Error details")
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Authentication Consistency
*For any* streaming request, the authentication and authorization logic should produce the same result as the non-streaming endpoint
**Validates: Requirements 5.1, 5.2, 5.3, 5.4**

### Property 2: Event Ordering
*For any* agent invocation, text events should be emitted in the order they are generated by the agent
**Validates: Requirements 1.2, 3.2**

### Property 3: Stream Completion
*For any* successful agent invocation, the stream should always emit a "done" event as the final event before closing
**Validates: Requirements 1.3, 3.4**

### Property 4: Error Propagation
*For any* error during streaming, an "error" event should be emitted and the stream should close gracefully without hanging
**Validates: Requirements 1.4, 7.2**

### Property 5: Session Context Preservation
*For any* streaming request with a session_id, the agent should maintain the same conversation context as non-streaming requests
**Validates: Requirements 1.5, 5.4**

### Property 6: Event Format Consistency
*For any* emitted event, the event structure should conform to the defined schema with required fields present
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

### Property 7: No Data Loss
*For any* text generated by the agent, all text chunks should be emitted in the stream without loss or duplication
**Validates: Requirements 1.2, 8.1**

### Property 8: Observability Completeness
*For any* streaming invocation, metrics and logs should be emitted for start, events, completion, and errors
**Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

## Error Handling

### Error Scenarios and Responses

1. **Authentication Failure**
   - Return 401 before establishing stream
   - Log authentication attempt with details
   - Emit metric for unauthorized access

2. **MCP Server Unavailable**
   - Emit error event with user-friendly message
   - Close stream gracefully
   - Log error with MCP endpoint details
   - Emit metric for MCP connection failure

3. **Agent Processing Error**
   - Emit error event with sanitized error message
   - Include suggestions for user action
   - Log full error details for debugging
   - Close stream gracefully

4. **Client Disconnection**
   - Detect disconnection via broken pipe or connection reset
   - Stop agent processing immediately
   - Log disconnection event
   - Clean up resources

5. **Timeout**
   - Emit error event before Lambda timeout
   - Provide partial response if available
   - Log timeout with context
   - Suggest retry or query simplification

### Error Event Format

```python
def create_error_event(
    error: Exception,
    error_type: str,
    user_message: str,
    suggestions: List[str]
) -> Dict[str, Any]:
    """
    Create standardized error event.
    
    Args:
        error: Original exception
        error_type: Classification of error
        user_message: User-friendly error message
        suggestions: List of suggested actions
        
    Returns:
        Error event dictionary
    """
    return {
        "type": "error",
        "error": {
            "type": error_type,
            "message": user_message,
            "suggestions": suggestions
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
```

## Testing Strategy

### Unit Tests

1. **Event Filtering Tests**
   - Test `should_emit_event()` with various event types
   - Verify internal events are filtered out
   - Verify user-facing events are emitted

2. **Event Formatting Tests**
   - Test SSE format generation
   - Verify JSON serialization
   - Test timestamp generation

3. **Error Event Creation Tests**
   - Test error event formatting
   - Verify sanitization of error details
   - Test suggestion generation

### Integration Tests

1. **Streaming Endpoint Tests**
   - Test successful streaming invocation
   - Test authentication validation
   - Test error handling
   - Test session context preservation

2. **Event Stream Tests**
   - Test complete event sequence
   - Test event ordering
   - Test stream completion
   - Test error propagation

### Property-Based Tests

1. **Authentication Consistency Property**
   - Generate random valid/invalid tokens
   - Verify streaming and non-streaming endpoints produce same auth results

2. **Event Ordering Property**
   - Generate random prompts
   - Verify text events maintain generation order

3. **Stream Completion Property**
   - Generate random successful invocations
   - Verify all streams end with "done" event

4. **No Data Loss Property**
   - Generate random prompts
   - Verify all generated text appears in stream events

### Manual Testing

1. **Frontend Integration**
   - Test real-time display of streaming responses
   - Test tool call indicators
   - Test error handling and retry
   - Test session continuity

2. **Performance Testing**
   - Measure time-to-first-byte
   - Measure event latency
   - Test under concurrent load
   - Verify Lambda timeout handling

## Deployment Considerations

### CDK Changes

1. **Enable Lambda Response Streaming**
   ```python
   invoke_mode=lambda_.InvokeMode.RESPONSE_STREAM
   ```

2. **Update Lambda Web Adapter Configuration**
   ```python
   envs['AWS_LWA_INVOKE_MODE'] = 'RESPONSE_STREAM'
   ```

3. **Maintain Backward Compatibility**
   - Keep existing `/invocations` endpoint
   - Add new `/invocations/stream` endpoint
   - Both endpoints share authentication logic

### Monitoring and Alerts

1. **CloudWatch Metrics**
   - `StreamingInvocationCount` - Number of streaming invocations
   - `StreamingDuration` - Duration of streaming invocations
   - `StreamingErrors` - Number of streaming errors
   - `EventsEmitted` - Number of events emitted per invocation
   - `ClientDisconnections` - Number of client disconnections

2. **CloudWatch Alarms**
   - High error rate (> 5% of invocations)
   - High disconnection rate (> 10% of invocations)
   - High latency (> 5s time-to-first-byte)
   - Lambda timeout approaching

3. **X-Ray Tracing**
   - Trace streaming invocations end-to-end
   - Track event emission timing
   - Identify bottlenecks in event processing

### Rollout Strategy

1. **Phase 1: Deploy Streaming Endpoint**
   - Deploy new endpoint alongside existing
   - Enable for internal testing only
   - Monitor metrics and logs

2. **Phase 2: Frontend Integration**
   - Update frontend to use streaming endpoint
   - Add feature flag for gradual rollout
   - Monitor user experience metrics

3. **Phase 3: Full Rollout**
   - Enable streaming for all users
   - Monitor performance and errors
   - Keep non-streaming endpoint as fallback

4. **Phase 4: Optimization**
   - Tune event filtering based on usage
   - Optimize event formatting
   - Reduce latency where possible

## Security Considerations

1. **Authentication**
   - Reuse existing Cognito JWT validation
   - Extract actor_id using same logic as non-streaming
   - Validate token before establishing stream

2. **Authorization**
   - Enforce same authorization rules as non-streaming
   - Validate session_id ownership
   - Prevent cross-user session access

3. **Rate Limiting**
   - Apply same rate limits as non-streaming
   - Consider streaming-specific limits
   - Return 429 with retry-after header

4. **Data Sanitization**
   - Sanitize error messages in production
   - Avoid exposing internal implementation details
   - Filter sensitive information from logs

5. **Connection Security**
   - Enforce HTTPS for all streaming connections
   - Validate CORS origins
   - Implement connection timeout limits

## Performance Optimization

1. **Event Buffering**
   - Emit events immediately without buffering
   - Use async generators for efficient streaming
   - Minimize memory usage

2. **JSON Serialization**
   - Use efficient JSON encoder
   - Pre-serialize common event structures
   - Avoid unnecessary serialization

3. **Connection Management**
   - Detect client disconnections early
   - Stop processing on disconnection
   - Clean up resources promptly

4. **Lambda Configuration**
   - Use appropriate memory allocation (3008 MB)
   - Enable SnapStart for faster cold starts
   - Use ARM64 architecture for better performance

5. **Event Filtering**
   - Filter events early in the pipeline
   - Minimize event processing overhead
   - Cache event formatting logic

