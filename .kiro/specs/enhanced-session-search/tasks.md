# Implementation Plan: Enhanced Session Search

- [x] 1. Add comprehensive DynamoDB integration tests
  - Add integration tests to `tests/shared/infra/repositories/test_session_repository_dynamo.py`
  - Test venue, day, and level filtering correctness
  - Test combined filters
  - Test GSI ordering by start_datetime

  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8_

- [x] 1.1 Write property test for venue filtering correctness
  - **Property 1: Venue filtering correctness**
  - **Validates: Requirements 1.1**

- [x] 1.2 Write property test for day filtering correctness
  - **Property 2: Day filtering correctness**
  - **Validates: Requirements 1.2**

- [x] 1.3 Write property test for level filtering correctness
  - **Property 3: Level filtering correctness**
  - **Validates: Requirements 1.3**

- [x] 1.4 Write property test for combined filter correctness
  - **Property 4: Combined filter correctness**
  - **Validates: Requirements 1.4, 1.5**

- [x] 1.5 Write property test for GSI ordering preservation
  - **Property 5: GSI ordering preservation**
  - **Validates: Requirements 1.6**

- [x] 2. Update repository interface with speaker parameter
  - Add `speaker: Optional[str] = None` parameter to `search_sessions` method in `ISessionRepository`
  - Update method docstring to document speaker parameter
  - _Requirements: 3.1_

- [x] 3. Implement speaker filtering in SessionRepositoryMock
  - Add speaker parameter to `search_sessions` method
  - Implement case-insensitive partial matching in displayName
  - Implement case-insensitive partial matching in company
  - Check all speakers in the speakers list
  - Combine speaker filter with existing filters (day, venue, level, keywords)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.4, 4.5_

- [x] 3.1 Write property test for speaker displayName matching
  - **Property 6: Speaker displayName matching**
  - **Validates: Requirements 2.1**

- [x] 3.2 Write property test for speaker case-insensitive matching
  - **Property 7: Speaker case-insensitive matching**
  - **Validates: Requirements 2.2**

- [x] 3.3 Write property test for speaker partial name matching
  - **Property 8: Speaker partial name matching**
  - **Validates: Requirements 2.3**

- [x] 3.4 Write property test for speaker company matching
  - **Property 9: Speaker company matching**
  - **Validates: Requirements 2.4**

- [x] 3.5 Write property test for speaker combined with other filters
  - **Property 10: Speaker combined with other filters**
  - **Validates: Requirements 2.5**

- [x] 3.6 Write property test for speaker searches both fields
  - **Property 11: Speaker searches both fields**
  - **Validates: Requirements 4.4**

- [x] 3.7 Write property test for speaker checks all speakers
  - **Property 12: Speaker checks all speakers**
  - **Validates: Requirements 4.5**

- [x] 3.8 Write unit tests for SessionRepositoryMock speaker filtering
  - Test speaker filtering by displayName
  - Test speaker filtering by company
  - Test case-insensitive matching
  - Test partial name matching
  - Test speaker combined with other filters
  - Test empty speaker query returns all sessions
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement speaker filtering in SessionRepositoryDynamo
  - Add speaker parameter to `search_sessions` method
  - Create `_build_speaker_filter_expression` helper method
  - Use DynamoDB FilterExpression with `Attr('speakers').contains()`
  - Implement case-insensitive matching with multiple filter conditions (Original, UPPER, lower, Title Case)
  - Combine speaker FilterExpression with existing query/scan operations
  - Apply speaker filter to GSI queries when combined with indexed filters
  - Apply speaker filter to scans when used alone or with keywords
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4.1 Write integration test for speaker filtering with DynamoDB
  - Mark with `@pytest.mark.skip(reason="Needs dynamoDB")`
  - Test speaker filter returns only matching sessions
  - Test speaker filter with GSI queries
  - Test case-insensitive matching
  - _Requirements: 2.1, 2.2, 5.4_

- [x] 5. Update SearchSessionsUsecase with speaker parameter
  - Add `speaker: Optional[str] = None` parameter to `__call__` method
  - Add validation for speaker parameter (non-empty string if provided)
  - Raise EntityError if speaker is empty string or whitespace-only
  - Pass speaker parameter to repository search_sessions call
  - _Requirements: 3.2, 3.4, 3.5_

- [x] 5.1 Write property test for invalid speaker parameter rejection
  - **Property 13: Invalid speaker parameter rejection**
  - **Validates: Requirements 3.4, 6.3**

- [x] 5.2 Write unit tests for SearchSessionsUsecase speaker validation
  - Test invalid speaker (empty string) raises EntityError
  - Test invalid speaker (whitespace-only) raises EntityError
  - Test valid speaker parameter
  - Test speaker combined with other filters
  - _Requirements: 3.4, 3.5, 5.1, 5.2_

- [x] 6. Update SearchSessionsController with speaker parameter
  - Extract `speaker` query parameter from request
  - Pass speaker parameter to use case
  - Handle EntityError for invalid speaker (return 400 Bad Request)
  - _Requirements: 3.3, 3.5, 6.1, 6.2, 6.4_

- [x] 6.1 Write unit tests for SearchSessionsController speaker handling
  - Test controller with valid speaker parameter returns 200
  - Test controller with invalid speaker (empty) returns 400
  - Test controller with speaker combined with other filters
  - Test response includes sessions with matching speakers
  - _Requirements: 3.5, 6.1, 6.2, 6.5_

- [x] 7. Update API documentation
  - Document speaker query parameter in API endpoint specification
  - Add example requests with speaker filter
  - Document case-insensitive partial matching behavior
  - Document that speaker searches both displayName and company fields
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 8. Update MCP server tool and Strands agent prompt
  - Update `search_sessions` tool in `src/mcp/mcp_server.py` to include speaker parameter
  - Add speaker parameter to tool schema with description
  - Update tool description to mention speaker search capability
  - Update Strands agent prompt in `src/strands-agent/agent.py` to inform about speaker search
  - Document that speaker searches both displayName and company fields
  - Document case-insensitive partial matching behavior
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 6.1, 6.2_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

