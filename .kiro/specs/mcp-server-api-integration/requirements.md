# Requirements Document

## Introduction

This document specifies the requirements for an MCP (Model Context Protocol) Server that exposes the re:invent Planner API Gateway endpoints as MCP tools. The MCP server will enable AI assistants and other MCP clients to interact with the re:invent session data through standardized tool interfaces, making the API accessible to LLM-based applications.

## Glossary

- **MCP Server**: A Model Context Protocol server that exposes tools and resources to MCP clients
- **MCP Client**: An application (like Claude Desktop, Kiro, or other AI assistants) that connects to MCP servers
- **MCP Tool**: A callable function exposed by an MCP server that performs a specific action
- **API Gateway Endpoint**: The HTTP REST API endpoints deployed via AWS API Gateway
- **Session**: A re:invent conference session entity with details like title, venue, speakers, and schedule
- **FastMCP**: A Python framework for building MCP servers quickly
- **Tool Schema**: JSON Schema definition that describes a tool's parameters and return type

## Requirements

### Requirement 1

**User Story:** As an MCP client developer, I want to discover all available session query tools, so that I can understand what operations are supported

#### Acceptance Criteria

1. THE MCP Server SHALL expose a list of available tools through the MCP protocol
2. WHEN an MCP client connects, THE MCP Server SHALL provide tool schemas for all session endpoints
3. THE MCP Server SHALL include descriptive names for each tool following the pattern `{action}_{resource}`
4. THE MCP Server SHALL provide detailed descriptions for each tool explaining its purpose and usage
5. THE MCP Server SHALL define input parameters with appropriate types and descriptions for each tool

### Requirement 2

**User Story:** As an MCP client, I want to retrieve all re:invent sessions through an MCP tool, so that I can access session data without making direct HTTP requests

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `get_all_sessions` that retrieves all sessions
2. WHEN the `get_all_sessions` tool is invoked, THE MCP Server SHALL make an HTTP GET request to the API Gateway endpoint
3. THE MCP Server SHALL parse the JSON response from the API Gateway
4. THE MCP Server SHALL return session data in a structured format to the MCP client
5. IF the API Gateway returns an error, THEN THE MCP Server SHALL return an error response with the HTTP status code and message

### Requirement 3

**User Story:** As an MCP client, I want to sync sessions from the external catalog API through an MCP tool, so that I can trigger data refresh operations

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `sync_sessions` that triggers a data sync
2. WHEN the `sync_sessions` tool is invoked, THE MCP Server SHALL make an HTTP POST request to the sync endpoint
3. THE MCP Server SHALL return sync statistics including inserted, updated, and total counts
4. IF the external catalog API is unreachable, THEN THE MCP Server SHALL return an error with status code 503
5. THE MCP Server SHALL include the sync operation duration in the response

### Requirement 4

**User Story:** As an MCP client, I want to query sessions by venue through an MCP tool, so that I can filter sessions by location

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `get_sessions_by_venue` that accepts a venue parameter
2. WHEN the tool is invoked with a venue name, THE MCP Server SHALL make an HTTP GET request with the venue as a query parameter
3. THE MCP Server SHALL validate that the venue parameter is provided and is a non-empty string
4. THE MCP Server SHALL return filtered session data matching the specified venue
5. IF no sessions match the venue, THE MCP Server SHALL return an empty sessions array with count 0

### Requirement 5

**User Story:** As an MCP client, I want to query sessions by day through an MCP tool, so that I can filter sessions by conference day

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `get_sessions_by_day` that accepts a day parameter
2. WHEN the tool is invoked with a day name, THE MCP Server SHALL make an HTTP GET request with the day as a query parameter
3. THE MCP Server SHALL validate that the day parameter is provided and is a non-empty string
4. THE MCP Server SHALL return filtered session data for the specified day
5. THE MCP Server SHALL support day values like "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"

### Requirement 6

**User Story:** As an MCP client, I want to query sessions by difficulty level through an MCP tool, so that I can find sessions appropriate for my skill level

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `get_sessions_by_level` that accepts a level parameter
2. WHEN the tool is invoked with a level value, THE MCP Server SHALL make an HTTP GET request with the level as a query parameter
3. THE MCP Server SHALL validate that the level parameter is a valid integer (100, 200, 300, or 400)
4. THE MCP Server SHALL return filtered session data matching the specified difficulty level
5. THE MCP Server SHALL include level descriptions in the tool schema (100=Foundational, 200=Intermediate, 300=Advanced, 400=Expert)

### Requirement 7

**User Story:** As an MCP client, I want to query a specific session by its short ID through an MCP tool, so that I can retrieve detailed information about a particular session

#### Acceptance Criteria

1. THE MCP Server SHALL expose a tool named `get_session_by_short_id` that accepts a short_id parameter
2. WHEN the tool is invoked with a short ID, THE MCP Server SHALL make an HTTP GET request with the short_id as a query parameter
3. THE MCP Server SHALL validate that the short_id parameter is provided and is a non-empty string
4. THE MCP Server SHALL return the matching session data if found
5. IF no session matches the short ID, THE MCP Server SHALL return a 404 error response

### Requirement 8

**User Story:** As a developer, I want the MCP server to handle API Gateway errors gracefully, so that clients receive meaningful error messages

#### Acceptance Criteria

1. WHEN an API Gateway endpoint returns a 4xx error, THE MCP Server SHALL return the error message to the client
2. WHEN an API Gateway endpoint returns a 5xx error, THE MCP Server SHALL return an internal server error message
3. IF the API Gateway is unreachable, THEN THE MCP Server SHALL return a connection error with details
4. THE MCP Server SHALL log all API requests and responses for debugging purposes
5. THE MCP Server SHALL include the HTTP status code in error responses

### Requirement 9

**User Story:** As a developer, I want the MCP server to read the API Gateway base URL from environment variables, so that it can work across different deployment stages

#### Acceptance Criteria

1. THE MCP Server SHALL read the API Gateway base URL from an environment variable named `API_GATEWAY_BASE_URL`
2. IF the environment variable is not set, THE MCP Server SHALL use a default URL for local development
3. THE MCP Server SHALL construct full endpoint URLs by appending resource paths to the base URL
4. THE MCP Server SHALL validate that the base URL is a valid HTTP/HTTPS URL
5. THE MCP Server SHALL log the configured base URL on startup

### Requirement 10

**User Story:** As a developer, I want the MCP server to follow Python best practices and use FastMCP framework, so that it is maintainable and follows MCP standards

#### Acceptance Criteria

1. THE MCP Server SHALL be implemented using the FastMCP Python framework
2. THE MCP Server SHALL use type hints for all function parameters and return values
3. THE MCP Server SHALL include docstrings for all tool functions explaining their purpose
4. THE MCP Server SHALL use the `@mcp.tool()` decorator to register tools
5. THE MCP Server SHALL handle exceptions and return structured error responses

### Requirement 11

**User Story:** As a developer, I want the MCP server to be runnable via stdio transport, so that it can be integrated with MCP clients like Claude Desktop and Kiro

#### Acceptance Criteria

1. THE MCP Server SHALL support stdio transport for communication with MCP clients
2. WHEN the server is started, THE MCP Server SHALL listen for MCP protocol messages on stdin
3. THE MCP Server SHALL write MCP protocol responses to stdout
4. THE MCP Server SHALL use stderr for logging and debugging output
5. THE MCP Server SHALL be executable via `python -m src.mcp.server` or `uvx` command

### Requirement 12

**User Story:** As a developer, I want comprehensive tool schemas with examples, so that MCP clients can understand how to use each tool

#### Acceptance Criteria

1. THE MCP Server SHALL define JSON Schema for all tool parameters
2. THE MCP Server SHALL include parameter descriptions explaining expected values
3. THE MCP Server SHALL specify required vs optional parameters
4. THE MCP Server SHALL include example values in parameter descriptions where helpful
5. THE MCP Server SHALL document the expected response format for each tool
