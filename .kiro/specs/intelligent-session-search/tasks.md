# Implementation Plan: Intelligent Session Search

- [x] 1. Extend repository interface and implement search method
  - Add `search_sessions` method to `ISessionRepository` interface
  - Define method signature with all filter parameters and pagination support
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.1, 6.1_

- [x] 1.1 Implement search in SessionRepositoryMock
  - Create in-memory filtering logic for all filter types (day, venue, level, keywords)
  - Implement keyword search across title, abstract, topics, areas_of_interest
  - Implement relevance scoring for keyword matches
  - Implement pagination with token encoding/decoding
  - Implement result ordering (by relevance for keywords, by datetime otherwise)
  - _Requirements: 1.1, 1.2, 2.1, 2.6, 2.7, 3.2, 3.3, 3.4, 3.5, 5.1, 5.2, 5.3, 6.2_

- [x] 1.2 Write property test for combined filter matching
  - **Property 1: Combined filter matching**
  - **Validates: Requirements 1.1**

- [x] 1.3 Write property test for partial filter matching
  - **Property 2: Partial filter matching**
  - **Validates: Requirements 1.2**

- [x] 1.4 Write property test for keyword field coverage
  - **Property 4: Keyword field coverage**
  - **Validates: Requirements 2.1**

- [x] 1.5 Write property test for case-insensitive keyword matching
  - **Property 5: Case-insensitive keyword matching**
  - **Validates: Requirements 2.6**

- [x] 1.6 Write property test for multiple keyword OR logic
  - **Property 6: Multiple keyword OR logic**
  - **Validates: Requirements 2.7**

- [x] 1.7 Write unit tests for SessionRepositoryMock search
  - Test empty filters returns all sessions
  - Test single filter searches (day only, venue only, level only, keywords only)
  - Test combined filters
  - Test empty result sets
  - Test pagination with various page sizes
  - Test relevance ordering
  - Test datetime ordering
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 3.2, 5.1, 5.2_

- [x] 2. Implement search in SessionRepositoryDynamo
  - Implement index selection logic (Level > Venue > Day priority)
  - Implement GSI queries for indexed filters
  - Implement scan with entity filter for keyword-only searches
  - Implement application-level keyword filtering after DynamoDB query
  - Implement relevance scoring for keyword matches
  - Implement pagination using DynamoDB's LastEvaluatedKey
  - Implement result ordering
  - Handle edge cases (no filters, invalid tokens, etc.)
  - _Requirements: 1.1, 1.2, 2.1, 2.6, 2.7, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 6.2_

- [x] 2.1 Write property test for page size limit
  - **Property 7: Page size limit**
  - **Validates: Requirements 3.2**

- [x] 2.2 Write property test for next page token presence
  - **Property 8: Next page token presence**
  - **Validates: Requirements 3.3**

- [x] 2.3 Write property test for pagination continuation
  - **Property 9: Pagination continuation**
  - **Validates: Requirements 3.4**

- [x] 2.4 Write property test for final page token absence
  - **Property 10: Final page token absence**
  - **Validates: Requirements 3.5**

- [x] 2.5 Write property test for keyword relevance ordering
  - **Property 11: Keyword relevance ordering**
  - **Validates: Requirements 5.1**

- [x] 2.6 Write property test for default datetime ordering
  - **Property 12: Default datetime ordering**
  - **Validates: Requirements 5.2**

- [x] 2.7 Write property test for relevance tie-breaking
  - **Property 13: Relevance tie-breaking**
  - **Validates: Requirements 5.3**

- [x] 2.8 Write integration tests for SessionRepositoryDynamo search
  - Mark with `@pytest.mark.skip(reason="Needs dynamoDB")`
  - Test GSI query execution
  - Test keyword filtering performance
  - Test pagination with large datasets
  - _Requirements: 2.1, 3.2, 4.1_

- [x] 3. Create SearchSessionsUsecase
  - Implement input validation for all parameters
  - Validate day values (valid day names)
  - Validate venue values (non-empty strings)
  - Validate level values (100, 200, 300, 400) 
  - Validate page_size (1-100, default 50)
  - Call repository search method
  - Handle repository exceptions
  - _Requirements: 1.1, 1.2, 1.4, 3.6, 3.7, 6.3_

- [x] 3.1 Write property test for invalid filter rejection
  - **Property 3: Invalid filter rejection**
  - **Validates: Requirements 1.4**

- [x] 3.2 Write unit tests for SearchSessionsUsecase
  - Test valid filter combinations
  - Test invalid day values raise EntityError
  - Test invalid level values raise EntityError
  - Test invalid page_size values raise EntityError
  - Test default page_size (50)
  - Test maximum page_size enforcement (100)
  - Test empty filters
  - _Requirements: 1.1, 1.2, 1.4, 3.6, 3.7_

- [x] 4. Create SearchSessionsController
  - Extract query parameters from request (day, venue, level, keywords, page_size, next_page_token)
  - Handle missing optional parameters
  - Call use case with extracted parameters
  - Map exceptions to HTTP status codes (EntityError → 400, ValueError → 400, Exception → 500)
  - Return 200 OK for successful searches (even with empty results)
  - _Requirements: 1.4, 6.4, 7.3, 7.4, 7.5_

- [x] 4.1 Write unit tests for SearchSessionsController
  - Test successful search returns 200 OK
  - Test search with all filters
  - Test search with partial filters
  - Test search with no filters
  - Test invalid day returns 400
  - Test invalid level returns 400
  - Test invalid page_size returns 400
  - Test empty results returns 200 with empty array
  - Test response includes pagination metadata
  - _Requirements: 1.4, 7.3, 7.4, 7.5_

- [x] 5. Create SearchSessionsViewmodel
  - Accept sessions list, next_page_token, and calculate total_results
  - Implement `to_dict()` method
  - Format sessions as list of dictionaries with all fields
  - Include pagination metadata (page_size, next_page_token)
  - Include success message
  - _Requirements: 6.4, 7.3_

- [x] 5.1 Write unit tests for SearchSessionsViewmodel
  - Test `to_dict()` includes all session fields
  - Test pagination metadata is present
  - Test next_page_token is included when present
  - Test next_page_token is null when absent
  - Test message field is present
  - _Requirements: 7.3_

- [x] 6. Create SearchSessionsPresenter
  - Import controller, use case, and repository from environments
  - Implement `lambda_handler` function
  - Parse Lambda event to extract query parameters
  - Convert request to HttpRequest format
  - Call controller
  - Convert response to Lambda response format
  - _Requirements: 6.4, 7.1, 7.2_

- [x] 6.1 Write unit tests for SearchSessionsPresenter
  - Test lambda_handler accepts GET request event
  - Test query parameters are extracted correctly
  - Test successful response format
  - Test endpoint path is /sessions/search
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 7. Add Lambda function to CDK stack
  - Add `search_sessions_function` to `lambda_stack.py`
  - Configure as GET endpoint at `/sessions/search`
  - Add to `functions_that_need_dynamo_permissions` list
  - Set appropriate timeout (10 seconds for search operations)
  - Set appropriate memory (512 MB for search operations)
  - _Requirements: 6.4_

- [x] 8. Update Environments configuration
  - Ensure `get_session_repo()` method is available
  - Verify environment variables for DynamoDB table access
  - _Requirements: 6.4_

- [ ] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. Manual testing and validation
  - Test search endpoint with various filter combinations
  - Verify pagination works correctly
  - Verify keyword search returns relevant results
  - Verify relevance ordering is correct
  - Verify performance meets < 500ms target for typical queries
  - Test with empty filters
  - Test with invalid parameters
  - _Requirements: 1.1, 1.2, 2.1, 3.2, 4.5, 5.1, 5.2_
