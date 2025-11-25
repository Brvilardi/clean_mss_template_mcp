# Implementation Plan: Session Type Filter

- [x] 1. Update repository interface with session_type parameter
  - Add `session_type: Optional[str] = None` parameter to `search_sessions` method in `ISessionRepository`
  - Update method docstring to document session_type parameter
  - _Requirements: 2.1_

- [x] 2. Implement session_type filtering in SessionRepositoryMock
  - Add session_type parameter to `search_sessions` method
  - Implement case-insensitive partial matching for session_type field
  - Combine session_type filter with existing filters (day, venue, level, keywords, speaker)
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [x] 2.1 Write property test for session type exact matching
  - **Property 1: Session type exact matching**
  - **Validates: Requirements 1.1, 1.2**

- [x] 2.2 Write property test for session type partial matching
  - **Property 2: Session type partial matching**
  - **Validates: Requirements 1.3**

- [x] 2.3 Write property test for session type combined with other filters
  - **Property 3: Session type combined with other filters**
  - **Validates: Requirements 1.4**

- [x] 2.4 Write property test for session type case-insensitive matching
  - **Property 5: Session type case-insensitive matching**
  - **Validates: Requirements 1.2**

- [x] 2.5 Write unit tests for SessionRepositoryMock session_type filtering
  - Test session_type filtering returns only matching sessions
  - Test case-insensitive matching
  - Test partial string matching
  - Test session_type combined with other filters
  - Test empty session_type query returns all sessions
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.3_

- [x] 3. Implement session_type filtering in SessionRepositoryDynamo
  - Add session_type parameter to `search_sessions` method
  - Create `_build_session_type_filter_expression` helper method
  - Use DynamoDB FilterExpression with `Attr('session_type').contains()`
  - Implement case-insensitive matching with multiple filter conditions (Original, UPPER, lower, Title Case)
  - Combine session_type FilterExpression with existing query/scan operations
  - Apply session_type filter to GSI queries when combined with indexed filters
  - Apply session_type filter to scans when used alone or with keywords
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2_

- [x] 3.1 Write integration test for session_type filtering with DynamoDB
  - Mark with `@pytest.mark.skip(reason="Needs dynamoDB")`
  - Test session_type filter returns only matching sessions
  - Test session_type filter with GSI queries
  - Test case-insensitive matching
  - _Requirements: 1.1, 1.2, 4.4_

- [x] 4. Update SearchSessionsUsecase with session_type parameter
  - Add `session_type: Optional[str] = None` parameter to `__call__` method
  - Add validation for session_type parameter (non-empty string if provided)
  - Raise EntityError if session_type is empty string or whitespace-only
  - Pass session_type parameter to repository search_sessions call
  - _Requirements: 2.2, 2.4, 2.5_

- [x] 4.1 Write property test for invalid session_type parameter rejection
  - **Property 4: Invalid session_type parameter rejection**
  - **Validates: Requirements 2.4, 2.5**

- [x] 4.2 Write unit tests for SearchSessionsUsecase session_type validation
  - Test invalid session_type (empty string) raises EntityError
  - Test invalid session_type (whitespace-only) raises EntityError
  - Test valid session_type parameter
  - Test session_type combined with other filters
  - _Requirements: 2.4, 2.5, 4.1, 4.2_

- [x] 5. Update SearchSessionsController with session_type parameter
  - Extract `session_type` query parameter from request
  - Pass session_type parameter to use case
  - Handle EntityError for invalid session_type (return 400 Bad Request)
  - _Requirements: 2.3, 2.5, 5.1, 5.2, 5.4_

- [x] 5.1 Write unit tests for SearchSessionsController session_type handling
  - Test controller with valid session_type parameter returns 200
  - Test controller with invalid session_type (empty) returns 400
  - Test controller with session_type combined with other filters
  - Test response includes sessions with matching session_type
  - _Requirements: 2.5, 5.1, 5.2, 5.5_

- [x] 6. Update API documentation
  - Document session_type query parameter in API endpoint specification
  - Add example requests with session_type filter
  - Document case-insensitive partial matching behavior
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Update MCP server tool and Strands agent prompt
  - Update `search_sessions` tool in `src/mcp/mcp_server.py` to include session_type parameter
  - Add session_type parameter to tool schema with description
  - Update tool description to mention session_type search capability
  - Update Strands agent prompt in `src/strands-agent/agent.py` to inform about session_type search
  - Document case-insensitive partial matching behavior
  - _Requirements: 1.1, 1.2, 1.3, 5.1, 5.2_

- [ ] 8. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.
