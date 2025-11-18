# Design Document: MCP Server for re:invent Planner API

## Overview

The MCP Server for re:invent Planner API is a Python-based Model Context Protocol server that exposes the existing API Gateway endpoints as MCP tools. This enables AI assistants and other MCP clients to interact with re:invent session data through standardized tool interfaces without requiring direct HTTP API knowledge.

The server acts as a bridge between MCP clients (like Claude Desktop, Kiro) and the deployed API Gateway endpoints, translating MCP tool calls into HTTP requests and returning structured responses.

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│   MCP Client    │
│ (Claude/Kiro)   │
└────────┬────────┘
         │ MCP Protocol (stdio)
         │
┌────────▼────────┐
│   server.py     │
│  (FastMCP)      │
│                 │
│  - Tool defs    │
│  - requests lib │
└────────┬────────┘
         │ HTTP/HTTPS
         │
┌────────▼────────┐
│  API Gateway    │
│                 │
│  /get-all-sessions
│  /sync-sessions
│  /get-sessions-by-venue
│  /get-sessions-by-day
│  /get-sessions-by-level
│  /get-sessions-by-short-id
└─────────────────┘
```

### Component Structure

```
src/mcp/
├── server.py              # Single file with all MCP server code
└── __init__.py
```

### Data Flow

**Tool Invocation Flow:**
```
1. MCP Client sends tool call request via stdin
2. FastMCP framework deserializes request
3. Tool function is invoked with parameters
4. requests.get/post makes HTTP call to API Gateway
5. Response JSON is returned directly
6. Structured response returned to MCP client via stdout
```

**Error Flow:**
```
1. API Gateway returns error response
2. requests raises HTTPError
3. Tool function catches exception
4. Error dict is returned with status code
5. Error returned to client
```

## Components and Interfaces

### Single File Implementation (`src/mcp/server.py`)

Complete MCP server in a single file using FastMCP and requests.

```python
import os
import requests
from typing import Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("reinvent-planner-api")

# Configuration from environment
API_BASE_URL = os.getenv(
    "API_GATEWAY_BASE_URL",
    "http://localhost:3000/mss-template"
)
TIMEOUT = 30

@mcp.tool()
def get_all_sessions() -> Dict[str, Any]:
    """
    Retrieve all re:invent sessions from the database.
    
    Returns a list of all sessions with their complete details including
    title, venue, speakers, schedule, topics, and difficulty level.
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-all-sessions",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

@mcp.tool()
def sync_sessions() -> Dict[str, Any]:
    """
    Sync sessions from the external re:invent catalog API.
    
    Triggers a data refresh operation that fetches the latest session
    data and updates the local database.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/sync-sessions",
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

@mcp.tool()
def get_sessions_by_venue(venue: str) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by venue location.
    
    Args:
        venue: Venue name (e.g., "Mandalay Bay", "Venetian")
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-sessions-by-venue",
            params={"venue": venue},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

@mcp.tool()
def get_sessions_by_day(day: str) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by conference day.
    
    Args:
        day: Day of the week (e.g., "Monday", "Tuesday", "Wednesday")
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-sessions-by-day",
            params={"day": day},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

@mcp.tool()
def get_sessions_by_level(level: int) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by difficulty level.
    
    Args:
        level: Difficulty level (100=Foundational, 200=Intermediate, 300=Advanced, 400=Expert)
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-sessions-by-level",
            params={"level": level},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

@mcp.tool()
def get_session_by_short_id(short_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific session by its short ID code.
    
    Args:
        short_id: Session short ID (e.g., "TNC301", "COM305")
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/get-sessions-by-short-id",
            params={"short_id": short_id},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Key Features:**
- Single file implementation (~100 lines)
- Direct use of `requests` library
- Environment variable configuration
- Simple error handling
- All 6 session tools defined inline

## Data Models

### Tool Response Format

All tools return dictionaries with consistent structure:

**Success Response:**
```python
{
    "sessions": [
        {
            "session_id": str,
            "short_id": str,
            "title": str,
            "abstract": str,
            "session_type": str,
            "venue_name": str,
            "venue_room": str,
            "start_datetime": str,  # ISO 8601
            "end_datetime": str,    # ISO 8601
            "day": str,
            "speakers": [
                {
                    "displayName": str,
                    "company": str
                }
            ],
            "topics": List[str],
            "areas_of_interest": List[str],
            "level": str,
            "level_value": int,
            "features": List[str],
            "seat_capacity": int
        }
    ],
    "count": int
}
```

**Error Response:**
```python
{
    "error": str,           # Error message
    "status_code": int      # HTTP status code
}
```

**Sync Response:**
```python
{
    "message": str,
    "inserted": int,
    "updated": int,
    "total": int
}
```

### MCP Tool Schema

FastMCP automatically generates JSON Schema from Python type hints:

```python
# Example: get_sessions_by_venue tool schema
{
    "name": "get_sessions_by_venue",
    "description": "Retrieve sessions filtered by venue location...",
    "inputSchema": {
        "type": "object",
        "properties": {
            "venue": {
                "type": "string",
                "description": "Venue name to filter by..."
            }
        },
        "required": ["venue"]
    }
}
```

## Error Handling

### Error Categories

| Error Type | Status Code | Handling Strategy |
|------------|-------------|-------------------|
| Connection Error | 503 | Return error with retry suggestion |
| Timeout | 504 | Return error with timeout duration |
| Client Error (4xx) | 400-499 | Return API error message |
| Server Error (5xx) | 500-599 | Return generic error message |
| Validation Error | 400 | Return parameter validation message |

### Error Response Format

All errors returned to MCP clients follow this structure:

```python
{
    "error": "Human-readable error message",
    "status_code": 503,
    "details": "Optional additional context"
}
```

### Logging Strategy

- Log all tool invocations with parameters (excluding sensitive data)
- Log all HTTP requests and responses
- Log errors with full stack traces
- Use structured logging for easy parsing
- Write logs to stderr (stdout reserved for MCP protocol)

```python
import logging
import sys

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger("mcp.server")
```

## Testing Strategy

### Unit Tests

**Server Tests (`tests/mcp/test_server.py`):**
- Mock HTTP responses using `responses` library
- Test each tool with valid parameters
- Test successful GET and POST requests
- Test error handling (timeout, connection errors, HTTP errors)
- Test environment variable configuration
- Verify correct endpoints and parameters

### Integration Tests

**End-to-End Tests (`tests/mcp/test_integration.py`):**
- Start MCP server in test mode
- Send MCP protocol messages via stdin
- Verify responses on stdout
- Test with mock API Gateway server
- Test tool discovery
- Test tool invocation flow

### Manual Testing

**Testing with MCP Inspector:**
```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Run MCP server with inspector
npx @modelcontextprotocol/inspector python -m src.mcp.server
```

**Testing with Claude Desktop:**
Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "reinvent-planner": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "API_GATEWAY_BASE_URL": "https://your-api-gateway-url.com/mss-template"
      }
    }
  }
}
```

## Dependencies

### Required Python Packages

Add to `requirements.txt`:
```
fastmcp>=0.2.0
requests>=2.31.0
pydantic>=2.0.0
```

### Development Dependencies

Add to `requirements-dev.txt`:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
responses>=0.23.0
pytest-cov>=4.1.0
```

## Deployment and Configuration

### Local Development

```bash
# Set environment variables
export API_GATEWAY_BASE_URL="http://localhost:3000/mss-template"
export LOG_LEVEL="DEBUG"

# Run MCP server
python -m src.mcp.server
```

### Production Configuration

```bash
# Set production API Gateway URL
export API_GATEWAY_BASE_URL="https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/mss-template"
export API_TIMEOUT_SECONDS="30"
export LOG_LEVEL="INFO"

# Run MCP server
python -m src.mcp.server
```

### MCP Client Configuration

**For Kiro (`.kiro/settings/mcp.json`):**
```json
{
  "mcpServers": {
    "reinvent-planner": {
      "command": "python",
      "args": ["-m", "src.mcp.server"],
      "env": {
        "API_GATEWAY_BASE_URL": "https://your-api-gateway-url.com/mss-template",
        "PYTHONPATH": "/path/to/project"
      },
      "disabled": false,
      "autoApprove": ["get_all_sessions", "get_sessions_by_venue"]
    }
  }
}
```

**For uvx deployment:**
```json
{
  "mcpServers": {
    "reinvent-planner": {
      "command": "uvx",
      "args": ["--from", ".", "python", "-m", "src.mcp.server"],
      "env": {
        "API_GATEWAY_BASE_URL": "https://your-api-gateway-url.com/mss-template"
      }
    }
  }
}
```

## Security Considerations

### API Gateway Authentication

Currently, the API Gateway does not require authentication. For production:
- Consider adding API key authentication
- Implement IAM authentication for AWS-based clients
- Add rate limiting to prevent abuse

### Environment Variables

- Never commit API Gateway URLs to version control
- Use `.env` files for local development (add to `.gitignore`)
- Use secure secret management for production credentials

### Input Validation

- Validate all tool parameters before making API requests
- Sanitize user input to prevent injection attacks
- Limit parameter lengths to prevent DoS

### Error Messages

- Don't expose internal implementation details in errors
- Sanitize error messages before returning to clients
- Log full errors internally for debugging

## Performance Considerations

### HTTP Connection Pooling

- Use `requests.Session()` for connection reuse
- Configure connection pool size based on expected load
- Set appropriate timeout values

### Caching Strategy

For future enhancement:
- Cache GET responses with TTL
- Invalidate cache on sync operations
- Use in-memory cache (e.g., `cachetools`)

### Concurrent Requests

- FastMCP handles concurrent tool calls
- API Gateway client is thread-safe via `requests.Session()`
- Consider async/await for high-concurrency scenarios

## Monitoring and Observability

### Metrics to Track

- Tool invocation count by tool name
- API request latency
- Error rate by error type
- Cache hit/miss ratio (if caching implemented)

### Logging Best Practices

```python
# Log tool invocations
logger.info(f"Tool invoked: {tool_name}", extra={
    "tool": tool_name,
    "parameters": parameters
})

# Log API requests
logger.debug(f"API request: {method} {url}", extra={
    "method": method,
    "url": url,
    "params": params
})

# Log errors
logger.error(f"Tool error: {error}", extra={
    "tool": tool_name,
    "error": str(error),
    "status_code": status_code
}, exc_info=True)
```

## Future Enhancements

### Phase 2 Features (Out of Scope)

1. **Response Caching**: Cache GET responses to reduce API calls
2. **Batch Operations**: Support querying multiple sessions at once
3. **Streaming Responses**: Stream large result sets
4. **Advanced Filtering**: Combine multiple filters (venue + day + level)
5. **Session Resources**: Expose session details as MCP resources
6. **Webhooks**: Subscribe to session updates
7. **Authentication**: Support API key or OAuth authentication
8. **Rate Limiting**: Implement client-side rate limiting

### Potential Tool Additions

- `search_sessions(query: str)`: Full-text search across sessions
- `get_sessions_by_topic(topic: str)`: Filter by topic
- `get_sessions_by_speaker(speaker: str)`: Filter by speaker name
- `get_my_schedule()`: Retrieve user's saved sessions (requires auth)

## Summary

This design implements a clean, maintainable MCP server that bridges MCP clients with the re:invent Planner API Gateway. The FastMCP framework provides robust protocol handling, while the modular architecture ensures testability and extensibility. The server follows Python best practices and integrates seamlessly with existing MCP clients like Claude Desktop and Kiro.
