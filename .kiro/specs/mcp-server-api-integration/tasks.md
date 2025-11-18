# Implementation Plan

- [x] 1. Set up MCP server dependencies and structure
  - Add `fastmcp` and `requests` to requirements.txt
  - Create `src/mcp/__init__.py` file
  - _Requirements: 10.1, 10.2_

- [x] 2. Implement core MCP server with configuration
  - Create `src/mcp/server.py` with FastMCP initialization
  - Add environment variable configuration for API_GATEWAY_BASE_URL
  - Add TIMEOUT constant
  - Implement main entry point with stdio transport
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 3. Implement get_all_sessions tool
  - Define `@mcp.tool()` decorated function
  - Add comprehensive docstring with description and return format
  - Implement HTTP GET request to `/get-all-sessions` endpoint
  - Add error handling with try/except for RequestException
  - Return JSON response or error dict
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 12.1, 12.2, 12.5_

- [x] 4. Implement sync_sessions tool
  - Define `@mcp.tool()` decorated function
  - Add comprehensive docstring explaining sync operation
  - Implement HTTP POST request to `/sync-sessions` endpoint
  - Add error handling for connection failures (503)
  - Return sync statistics or error dict
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 12.1, 12.2, 12.5_

- [x] 5. Implement get_sessions_by_venue tool
  - Define `@mcp.tool()` decorated function with venue parameter
  - Add docstring with parameter description and examples
  - Implement HTTP GET request with venue query parameter
  - Add error handling
  - Return filtered sessions or error dict
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 12.1, 12.2, 12.3, 12.4_

- [x] 6. Implement get_sessions_by_day tool
  - Define `@mcp.tool()` decorated function with day parameter
  - Add docstring with day examples (Monday, Tuesday, etc.)
  - Implement HTTP GET request with day query parameter
  - Add error handling
  - Return filtered sessions or error dict
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 12.1, 12.2, 12.3, 12.4_

- [x] 7. Implement get_sessions_by_level tool
  - Define `@mcp.tool()` decorated function with level parameter (int)
  - Add docstring with level descriptions (100-400)
  - Implement HTTP GET request with level query parameter
  - Add error handling
  - Return filtered sessions or error dict
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 12.1, 12.2, 12.3, 12.4_

- [x] 8. Implement get_session_by_short_id tool
  - Define `@mcp.tool()` decorated function with short_id parameter
  - Add docstring with short_id examples (TNC301, COM305)
  - Implement HTTP GET request with short_id query parameter
  - Add error handling for 404 not found
  - Return session details or error dict
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 12.1, 12.2, 12.3, 12.4_

- [x] 9. Add comprehensive error handling
  - Ensure all tools catch RequestException
  - Return error dicts with error message and status_code
  - Handle timeout, connection errors, and HTTP errors consistently
  - Use getattr to safely extract status_code from response
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 10. Create unit tests for MCP server
  - Create `tests/mcp/__init__.py`
  - Create `tests/mcp/test_server.py`
  - Mock HTTP responses using `responses` library
  - Test each tool with successful responses
  - Test error handling (timeout, connection errors, HTTP errors)
  - Test environment variable configuration
  - Verify correct endpoints and query parameters
  - _Requirements: All requirements_

- [ ] 11. Create MCP client configuration documentation
  - Create `docs/MCP_SERVER_SETUP.md` with setup instructions
  - Document environment variables (API_GATEWAY_BASE_URL)
  - Add Kiro configuration example (.kiro/settings/mcp.json)
  - Add Claude Desktop configuration example
  - Add uvx deployment example
  - Include testing instructions with MCP Inspector
  - _Requirements: 9.1, 9.2, 11.5_

- [ ] 12. Update project documentation
  - Update main README.md with MCP server section
  - Add link to MCP_SERVER_SETUP.md
  - Document available MCP tools
  - Add example usage with MCP clients
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
