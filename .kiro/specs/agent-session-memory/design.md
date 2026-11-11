# Design Document

## Overview

This design implements persistent session storage with short-term memory (STM) and long-term memory (LTM) capabilities for the re:Invent Planner Agent using Amazon Bedrock AgentCore Memory and the Strands framework's session management system.

### Key Design Decisions

1. **AgentCore Memory for LTM**: Use Amazon Bedrock AgentCore Memory for intelligent long-term memory with three strategies: preferences, facts, and summaries
2. **DynamoDB for Metadata**: Store session metadata in DynamoDB for efficient querying and management
3. **Strands Session Manager**: Leverage Strands' built-in AgentCoreMemorySessionManager for seamless integration
4. **Environment-Based Configuration**: Support both local development (FileSessionManager) and production (AgentCoreMemorySessionManager) through environment variables
5. **CDK-First Approach**: Define all infrastructure as code with sensible defaults and minimal configuration
6. **Graceful Degradation**: Fall back to basic session persistence if AgentCore Memory is unavailable

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (Frontend Chat Application)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway / Lambda                        │
│                   (Agent Entrypoint Handler)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Strands Agent Core                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            AgentCoreMemorySessionManager                  │  │
│  │  - Session lifecycle management                           │  │
│  │  - Message persistence                                    │  │
│  │  - Memory retrieval coordination                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
    ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐
    │   DynamoDB   │  │ AgentCore Memory │  │  CloudWatch  │
    │   (Metadata) │  │  (STM + LTM)     │  │   (Logs)     │
    └──────────────┘  └──────────────────┘  └──────────────┘
         │                     │                     │
         │                     │                     │
         ▼                     ▼                     ▼
    Session Info      Conversation History    Structured Logs
    Actor Mapping     Preferences Storage     Error Tracking
    Timestamps        Facts Storage           Performance Metrics
                      Session Summaries
```

### Component Interaction Flow

1. **Session Initialization**:
   - Lambda receives request with session_id and actor_id
   - AgentCoreMemorySessionManager checks DynamoDB for session metadata
   - If session exists, restores conversation history from AgentCore Memory
   - If new session, creates session record in DynamoDB

2. **Message Processing**:
   - User message arrives via API Gateway
   - Agent processes message with full context (STM + LTM)
   - AgentCore Memory retrieves relevant preferences, facts, and summaries
   - Agent generates response using retrieved context
   - Both user message and agent response are persisted immediately

3. **Memory Strategy Execution**:
   - **Preferences**: Extracted and stored in `/preferences/{actorId}` namespace
   - **Facts**: Extracted and stored in `/facts/{actorId}` namespace
   - **Summaries**: Generated and stored in `/summaries/{actorId}/{sessionId}` namespace

## Components and Interfaces

### 1. Session Configuration Module

**Purpose**: Centralize session manager configuration and initialization

**Location**: `src/strands-agent/session_config.py`

**Key Classes**:

```python
@dataclass
class MemoryConfig:
    """Configuration for AgentCore Memory"""
    memory_id: str
    session_id: str
    actor_id: str
    region_name: str = "us-east-1"
    
    # Retrieval configurations for each namespace
    preferences_top_k: int = 5
    preferences_relevance_score: float = 0.7
    
    facts_top_k: int = 10
    facts_relevance_score: float = 0.3
    
    summaries_top_k: int = 5
    summaries_relevance_score: float = 0.5

class SessionManagerFactory:
    """Factory for creating appropriate session managers"""
    
    @staticmethod
    def create_session_manager(
        session_id: str,
        actor_id: str,
        environment: str = "production"
    ) -> SessionManager:
        """
        Create session manager based on environment.
        
        Args:
            session_id: Unique session identifier
            actor_id: Unique user identifier
            environment: "local" or "production"
            
        Returns:
            Configured session manager instance
        """
        pass
```

### 2. DynamoDB Session Repository

**Purpose**: Store and retrieve session metadata

**Location**: `src/shared/infra/repositories/agent_session_repository_dynamo.py`

**Schema**:
```python
{
    "PK": "SESSION#{session_id}",
    "SK": "METADATA",
    "session_id": str,
    "actor_id": str,
    "created_at": str,  # ISO 8601
    "updated_at": str,  # ISO 8601
    "last_accessed_at": str,  # ISO 8601
    "message_count": int,
    "status": str  # "active", "completed", "archived"
}
```

**GSI for Actor Queries**:
```python
{
    "GSI1PK": "ACTOR#{actor_id}",
    "GSI1SK": "SESSION#{created_at}",
    # ... other attributes
}
```

### 3. Agent Entrypoint Integration

**Purpose**: Initialize agent with session management

**Location**: `src/strands-agent/entrypoint.py`

**Key Functions**:

```python
def lambda_handler(event: dict, context: Any) -> dict:
    """
    Lambda handler with session management.
    
    Expected event structure:
    {
        "body": {
            "message": str,
            "session_id": str,
            "actor_id": str
        }
    }
    """
    pass

def initialize_agent_with_session(
    session_id: str,
    actor_id: str,
    mcp_endpoint: str
) -> Agent:
    """Initialize agent with appropriate session manager"""
    pass
```

### 4. CDK Infrastructure Stack

**Purpose**: Provision all required AWS resources

**Location**: `iac/iac/agent_memory_stack.py`

**Resources**:
- AgentCore Memory resource with three strategies
- DynamoDB table for session metadata
- IAM roles and policies
- Lambda environment variables
- CloudWatch log groups

## Data Models

### Session Metadata Model

```python
@dataclass
class SessionMetadata:
    """Session metadata stored in DynamoDB"""
    session_id: str
    actor_id: str
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    message_count: int
    status: str  # "active", "completed", "archived"
    
    def to_dynamo(self) -> dict:
        """Convert to DynamoDB item format"""
        pass
    
    @staticmethod
    def from_dynamo(item: dict) -> 'SessionMetadata':
        """Create from DynamoDB item"""
        pass
```

### Memory Configuration Model

```python
@dataclass
class RetrievalConfig:
    """Configuration for memory retrieval"""
    top_k: int
    relevance_score: float
    
    def validate(self) -> bool:
        """Validate configuration values"""
        return 1 <= self.top_k <= 1000 and 0.0 <= self.relevance_score <= 1.0
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. 
Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Session Restoration Preserves Message History

*For any* session with existing messages, when a new agent instance is created with the same session ID, all previous messages should be restored in chronological order.

**Validates: Requirements 1.1, 1.4**

### Property 2: Message Persistence is Immediate

*For any* message sent to or from the agent, the message should appear in session storage immediately after the interaction completes.

**Validates: Requirements 1.2, 1.3**

### Property 3: Session Restoration Failure Degrades Gracefully

*For any* session restoration failure, the agent should start a new session and log the error without blocking user interaction.

**Validates: Requirements 1.5**

### Property 4: Preference Storage Persists Across Sessions

*For any* user preference expressed in any session, the preference should be retrievable in subsequent sessions for the same actor.

**Validates: Requirements 2.1, 2.2**

### Property 5: Preference Retrieval Applies Relevance Threshold

*For any* preference retrieval operation, only preferences with relevance scores >= 0.7 should be returned, limited to the top 5 results.

**Validates: Requirements 2.3, 2.4**

### Property 6: Preference Updates Modify Long-Term Memory

*For any* change in user preferences, the long-term memory should reflect the updated preference information.

**Validates: Requirements 2.5**

### Property 7: Fact Extraction and Storage

*For any* factual information shared by a user, the fact should be extracted and stored in long-term memory organized by actor ID.

**Validates: Requirements 3.1, 3.5**

### Property 8: Fact Retrieval with Relevance Filtering

*For any* fact retrieval operation, only facts with relevance scores >= 0.3 should be returned, limited to the top 10 results.

**Validates: Requirements 3.2, 3.3, 3.4**

### Property 9: Session Summary Generation

*For any* completed session, a summary should be generated and stored with both actor ID and session ID for scoped retrieval.

**Validates: Requirements 4.1, 4.5**

### Property 10: Summary Retrieval with Relevance Filtering

*For any* new session, summaries from previous sessions should be retrieved with relevance scores >= 0.5, limited to the top 5 results.

**Validates: Requirements 4.2, 4.3, 4.4**

### Property 11: Session Metadata Persistence

*For any* new session, metadata including session ID, actor ID, creation timestamp, and last updated timestamp should be stored in DynamoDB.

**Validates: Requirements 5.1, 5.2**

### Property 12: Session Access Updates Timestamp

*For any* session access, the last accessed timestamp in DynamoDB should be updated to reflect the current time.

**Validates: Requirements 5.3**

### Property 13: Session Query by ID and Actor

*For any* session ID or actor ID, the system should support querying sessions by either identifier.

**Validates: Requirements 5.4, 5.5**

### Property 14: Configuration Validation

*For any* memory configuration, top_k values should be between 1 and 1000, and relevance_score values should be between 0.0 and 1.0.

**Validates: Requirements 6.1, 6.2**

### Property 15: Strategy Configuration Flexibility

*For any* memory strategy, the system should support enabling or disabling it independently through configuration.

**Validates: Requirements 6.3**

### Property 16: Environment Variable Configuration

*For any* provided environment variables, the system should use them to configure memory settings appropriately.

**Validates: Requirements 6.4**

### Property 17: Session Manager Enables Automatic Persistence

*For any* agent created with a session manager, conversations should be automatically persisted without explicit save calls.

**Validates: Requirements 7.2**

### Property 18: Lambda Initialization Failure Handling

*For any* session manager initialization failure in Lambda, the system should handle it gracefully and provide clear error messages.

**Validates: Requirements 7.5**

### Property 19: Memory Operation Error Logging

*For any* failed memory operation, the system should log the error with sufficient context information for debugging.

**Validates: Requirements 8.1**

### Property 20: AgentCore Memory Fallback

*For any* situation where AgentCore Memory is unavailable, the system should fall back to basic session persistence.

**Validates: Requirements 8.2**

### Property 21: DynamoDB Failure Resilience

*For any* DynamoDB operation failure, the system should log the error and continue with in-memory state.

**Validates: Requirements 8.3**

### Property 22: S3 Retry with Exponential Backoff

*For any* S3 operation failure, the system should log the error and attempt retry with exponential backoff.

**Validates: Requirements 8.4**

### Property 23: Clear Initialization Error Messages

*For any* initialization failure, the system should provide clear error messages indicating the root cause.

**Validates: Requirements 8.5**

### Property 24: File Session Restoration

*For any* local session files that exist, the system should be able to restore sessions from the filesystem.

**Validates: Requirements 10.5**

### Property 25: Structured CloudWatch Logging

*For any* operation, the system should provide clear CloudWatch logs with structured logging format.

**Validates: Requirements 11.8**

## Error Handling

### Error Categories and Responses

1. **AgentCore Memory Errors**:
   - **Unavailable**: Fall back to FileSessionManager or S3SessionManager
   - **Throttling**: Implement exponential backoff with jitter
   - **Invalid Configuration**: Log error and use defaults
   - **Permission Denied**: Log error with IAM guidance

2. **DynamoDB Errors**:
   - **Table Not Found**: Log error and continue with in-memory state
   - **Throttling**: Implement exponential backoff
   - **Item Not Found**: Treat as new session
   - **Conditional Check Failed**: Retry with updated data

3. **Session Restoration Errors**:
   - **Corrupted Data**: Log error and start new session
   - **Missing Session**: Create new session
   - **Timeout**: Retry once, then start new session

4. **Configuration Errors**:
   - **Invalid Values**: Use defaults and log warning
   - **Missing Required Config**: Fail fast with clear message
   - **Environment Mismatch**: Log warning and use detected environment

### Error Logging Format

```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "ERROR",
    "component": "SessionManager",
    "operation": "restore_session",
    "session_id": "sess_123",
    "actor_id": "user_456",
    "error_type": "AgentCoreMemoryUnavailable",
    "error_message": "Failed to connect to AgentCore Memory",
    "fallback_action": "Using FileSessionManager",
    "trace_id": "abc-def-ghi"
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify individual components in isolation:

1. **SessionManagerFactory Tests**:
   - Test creation of different session manager types
   - Test environment-based selection
   - Test configuration validation

2. **SessionMetadata Tests**:
   - Test DynamoDB conversion methods
   - Test timestamp handling
   - Test validation logic

3. **Configuration Tests**:
   - Test default value application
   - Test environment variable parsing
   - Test validation rules

### Property-Based Testing

Property-based tests will verify universal properties using the Hypothesis library for Python:

1. **Session Persistence Properties**:
   - Generate random sessions with messages
   - Verify restoration preserves all messages
   - Verify chronological ordering

2. **Memory Retrieval Properties**:
   - Generate random preferences, facts, and summaries
   - Verify relevance score filtering
   - Verify top_k limiting

3. **Configuration Validation Properties**:
   - Generate random configuration values
   - Verify boundary conditions (1-1000 for top_k, 0.0-1.0 for relevance)
   - Verify invalid values are rejected

4. **Error Handling Properties**:
   - Simulate various failure scenarios
   - Verify graceful degradation
   - Verify error logging

### Integration Testing

Integration tests will verify end-to-end functionality:

1. **Local Development Tests**:
   - Test FileSessionManager with filesystem
   - Test session restoration from files
   - Test multi-session scenarios

2. **AWS Integration Tests** (marked with `@pytest.mark.skip`):
   - Test AgentCore Memory integration
   - Test DynamoDB operations
   - Test IAM permissions
   - Test Lambda deployment

### Testing Configuration

```python
# pytest.ini
[pytest]
markers =
    unit: Unit tests (fast, no external dependencies)
    property: Property-based tests (medium speed)
    integration: Integration tests (slow, requires AWS)
    local: Local development tests (filesystem only)
```

### Property-Based Testing Requirements

- Use Hypothesis library for Python
- Configure minimum 100 iterations per property test
- Tag each property test with the design document property number
- Format: `# Feature: agent-session-memory, Property X: [property text]`
- Each correctness property must be implemented by a single property-based test

## Deployment Considerations

### Environment Variables

```bash
# Required for production
AGENTCORE_MEMORY_ID=mem_xxxxx
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=agent-sessions
ENVIRONMENT=production

# Optional configuration
PREFERENCES_TOP_K=5
PREFERENCES_RELEVANCE_SCORE=0.7
FACTS_TOP_K=10
FACTS_RELEVANCE_SCORE=0.3
SUMMARIES_TOP_K=5
SUMMARIES_RELEVANCE_SCORE=0.5

# Local development
ENVIRONMENT=local
SESSION_STORAGE_DIR=/tmp/agent-sessions
```

### CDK Stack Configuration

```python
# Minimal configuration required
agent_memory_stack = AgentMemoryStack(
    app,
    "AgentMemoryStack",
    # All other configuration uses sensible defaults
)
```

### Resource Naming Conventions

- DynamoDB Table: `{stack_name}-agent-sessions`
- AgentCore Memory: `{stack_name}-agent-memory`
- IAM Role: `{stack_name}-agent-execution-role`
- CloudWatch Log Group: `/aws/lambda/{stack_name}-agent`

### Monitoring and Observability

1. **CloudWatch Metrics**:
   - Session creation rate
   - Message persistence latency
   - Memory retrieval latency
   - Error rates by type

2. **CloudWatch Logs**:
   - Structured JSON logging
   - Request/response tracing
   - Error details with context

3. **X-Ray Tracing**:
   - End-to-end request tracing
   - Service map visualization
   - Performance bottleneck identification

## Security Considerations

### IAM Permissions

Minimum required permissions for Lambda execution role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*:*:foundation-model/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "bedrock-agentcore:CreateSession",
        "bedrock-agentcore:GetSession",
        "bedrock-agentcore:UpdateSession",
        "bedrock-agentcore:DeleteSession",
        "bedrock-agentcore:PutMemory",
        "bedrock-agentcore:GetMemory",
        "bedrock-agentcore:QueryMemory"
      ],
      "Resource": "arn:aws:bedrock-agentcore:*:*:memory/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/agent-sessions",
        "arn:aws:dynamodb:*:*:table/agent-sessions/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/*"
    }
  ]
}
```

### Data Privacy

1. **PII Handling**: Implement message redaction for sensitive information
2. **Encryption**: Use encryption at rest for DynamoDB and AgentCore Memory
3. **Access Control**: Implement actor-based access control for sessions
4. **Data Retention**: Implement TTL for old sessions (configurable)

### Best Practices

1. Use least privilege IAM policies
2. Enable CloudTrail for audit logging
3. Implement request validation
4. Use VPC endpoints for AWS service access
5. Enable encryption for data in transit and at rest
