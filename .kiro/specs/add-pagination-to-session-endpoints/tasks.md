# Implementation Plan: Pagination for Session Endpoints

## Overview
This implementation plan adds new paginated endpoints for session retrieval while keeping all existing endpoints unchanged. Each feature is implemented completely (repository → use case → view model → controller → presenter) before moving to the next.

---

## Shared Infrastructure - Pagination Helper

- [x] 1. Create pagination helper utility with TTL support
- [x] 1.1 Implement PaginationHelper class
  - Create `src/shared/helpers/pagination/` directory
  - Create `src/shared/helpers/pagination/__init__.py`
  - Create `src/shared/helpers/pagination/pagination_helper.py`
  - Implement `PaginationHelper` class with `DEFAULT_TOKEN_TTL_SECONDS = 300`
  - Implement `encode_pagination_token(last_evaluated_key, ttl_seconds)` with timestamp embedding
  - Implement `decode_pagination_token(token, max_age_seconds)` with TTL validation
  - Implement `validate_page_size(page_size)` with range checking (1-100)
  - _Requirements: 1.1, 1.4, 1.5, 2.1, 2.5, 6.1, 6.2, 6.3, 6.4_

- [x] 1.2 Write pagination helper tests
  - Create `tests/shared/helpers/pagination/` directory
  - Create `tests/shared/helpers/pagination/__init__.py`
  - Create `tests/shared/helpers/pagination/test_pagination_helper.py`
  - Test `encode_pagination_token` with various DynamoDB keys
  - Test `decode_pagination_token` with valid tokens
  - Test `decode_pagination_token` with expired tokens (should raise ValueError)
  - Test `decode_pagination_token` with invalid base64
  - Test `validate_page_size` with valid values (1, 50, 100)
  - Test `validate_page_size` with invalid values (0, 101, -1, "abc")
  - Test round-trip encoding/decoding
  - _Requirements: 1.5, 2.5, 6.1, 6.2, 6.3, 6.4_

---

## Feature 1: Get All Sessions Paginated

- [x] 2. Implement Get All Sessions Paginated
- [x] 2.1 Add repository interface method
  - Update `src/shared/domain/repositories/session_repository_interface.py`
  - Add `get_all_sessions_paginated(page_size, last_evaluated_key)` abstract method
  - Method returns `Tuple[List[Session], Optional[str]]`
  - Add comprehensive docstring with parameter descriptions
  - _Requirements: 3.1, 3.2, 5.1, 5.2, 8.1_

- [x] 2.2 Implement Mock repository method
  - Update `src/shared/infra/repositories/session_repository_mock.py`
  - Import PaginationHelper
  - Implement `get_all_sessions_paginated(page_size, last_evaluated_key)`
  - Use list slicing to simulate pagination
  - Encode/decode pagination token with `{'index': position}` format
  - Return appropriate next_token when more results exist
  - _Requirements: 3.1, 3.2, 5.1, 5.2, 8.2_

- [x] 2.3 Write Mock repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_mock.py`
  - Test `get_all_sessions_paginated` returns correct page size
  - Test `get_all_sessions_paginated` with multiple pages
  - Test pagination token works across requests
  - Test last page returns None next_token
  - Test expired token raises ValueError
  - Test invalid page_size raises ValueError
  - _Requirements: 3.1, 3.2, 5.2_

- [x] 2.4 Implement DynamoDB repository method
  - Update `src/shared/infra/repositories/session_repository_dynamo.py`
  - Import PaginationHelper
  - Implement `get_all_sessions_paginated(page_size, last_evaluated_key)`
  - Use `PaginationHelper.validate_page_size()` for validation
  - Use `PaginationHelper.decode_pagination_token()` for token decoding
  - Use `PaginationHelper.encode_pagination_token()` for response token
  - Add `Limit` parameter to DynamoDB query
  - Add `ExclusiveStartKey` parameter when token provided
  - Handle `LastEvaluatedKey` in response
  - Maintain consistent ordering with `ScanIndexForward: True`
  - _Requirements: 3.1, 3.2, 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 8.2_

- [x] 2.5 Write DynamoDB repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_dynamo.py`
  - Mark tests with `@pytest.mark.skip(reason="Needs dynamoDB")`
  - Test `get_all_sessions_paginated` with page_size only
  - Test `get_all_sessions_paginated` with page_size and last_evaluated_key
  - Test pagination returns correct next_token when more results exist
  - Test pagination returns None next_token on last page
  - Test expired token raises ValueError
  - Test invalid page_size raises ValueError
  - _Requirements: 3.1, 3.2, 5.2, 5.3, 7.1_

- [x] 2.6 Implement use case
  - Create `src/modules/get_all_sessions_paginated/` directory structure
  - Create `src/modules/get_all_sessions_paginated/__init__.py`
  - Create `src/modules/get_all_sessions_paginated/app/` directory
  - Create `src/modules/get_all_sessions_paginated/app/__init__.py`
  - Create `src/modules/get_all_sessions_paginated/app/get_all_sessions_paginated_usecase.py`
  - Implement `GetAllSessionsPaginatedUsecase` class
  - Implement `__call__(page_size, last_evaluated_key)` method
  - Call `repo.get_all_sessions_paginated(page_size, last_evaluated_key)`
  - Return tuple of (sessions, next_token)
  - _Requirements: 3.1, 3.2, 8.3_

- [x] 2.7 Write use case tests
  - Create `tests/modules/get_all_sessions_paginated/` directory structure
  - Create `tests/modules/get_all_sessions_paginated/app/test_get_all_sessions_paginated_usecase.py`
  - Test use case with mock repository
  - Test use case returns tuple (sessions, next_token)
  - Test use case with page_size only
  - Test use case with page_size and last_evaluated_key
  - _Requirements: 3.1, 3.2_

- [x] 2.8 Implement view model
  - Create `src/modules/get_all_sessions_paginated/app/get_all_sessions_paginated_viewmodel.py`
  - Implement `GetAllSessionsPaginatedViewmodel` class
  - Accept sessions list, page_size, and next_token in constructor
  - Implement `to_dict()` method
  - Include sessions array with all session attributes
  - Include count, page_size, has_more fields
  - Include last_evaluated_key only when has_more is true
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.5_

- [x] 2.9 Write view model tests
  - Create `tests/modules/get_all_sessions_paginated/app/test_get_all_sessions_paginated_viewmodel.py`
  - Test `to_dict()` output format
  - Test has_more is true when next_token exists
  - Test has_more is false when next_token is None
  - Test last_evaluated_key only included when has_more is true
  - Test count matches number of sessions
  - Test page_size is included in response
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2.10 Implement controller
  - Create `src/modules/get_all_sessions_paginated/app/get_all_sessions_paginated_controller.py`
  - Implement `GetAllSessionsPaginatedController` class
  - Implement `__call__(request)` method
  - Extract page_size from query parameters (required)
  - Extract last_evaluated_key from query parameters (optional)
  - Validate page_size is provided (raise MissingParameters if not)
  - Convert page_size to int (raise WrongTypeParameter if invalid)
  - Call use case with pagination parameters
  - Create view model with results
  - Return OK (200) with view model data
  - Handle ValueError for pagination errors (400)
  - Handle MissingParameters (400)
  - Handle WrongTypeParameter (400)
  - Handle Exception (500)
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 4.1, 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [x] 2.11 Write controller tests
  - Create `tests/modules/get_all_sessions_paginated/app/test_get_all_sessions_paginated_controller.py`
  - Test successful request with page_size only
  - Test successful request with page_size and last_evaluated_key
  - Test missing page_size returns 400
  - Test invalid page_size type returns 400
  - Test page_size < 1 returns 400
  - Test page_size > 100 returns 400
  - Test expired token returns 400
  - Test invalid token format returns 400
  - Test response includes pagination metadata
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 2.12 Implement presenter
  - Create `src/modules/get_all_sessions_paginated/app/get_all_sessions_paginated_presenter.py`
  - Initialize repository using `Environments.get_session_repo()`
  - Create use case instance
  - Create controller instance
  - Implement `lambda_handler(event, context)` function
  - Convert Lambda event to LambdaHttpRequest
  - Call controller with request
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 8.5_

- [x] 2.13 Write presenter tests
  - Create `tests/modules/get_all_sessions_paginated/app/test_get_all_sessions_paginated_presenter.py`
  - Test lambda_handler with valid event
  - Test response status code is 200
  - Test response body includes pagination metadata
  - _Requirements: 8.5_

- [x] 2.14 Add Lambda function to CDK stack
  - Update `iac/iac/lambda_stack.py`
  - Add `get_all_sessions_paginated_function` as GET method on `/sessions/paginated`
  - Set memory to 512 MB and timeout to 30 seconds
  - Add function to `functions_that_need_dynamo_permissions` list
  - _Requirements: 8.5_

---

## Feature 2: Get Sessions By Venue Paginated

- [ ] 3. Implement Get Sessions By Venue Paginated
- [ ] 3.1 Add repository interface method
  - Update `src/shared/domain/repositories/session_repository_interface.py`
  - Add `get_sessions_by_venue_paginated(venue_name, page_size, last_evaluated_key)` abstract method
  - Method returns `Tuple[List[Session], Optional[str]]`
  - Add comprehensive docstring
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.1_

- [ ] 3.2 Implement Mock repository method
  - Update `src/shared/infra/repositories/session_repository_mock.py`
  - Implement `get_sessions_by_venue_paginated(venue_name, page_size, last_evaluated_key)`
  - Filter by venue_name and apply pagination
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.2_

- [ ] 3.3 Write Mock repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_mock.py`
  - Test `get_sessions_by_venue_paginated` filters correctly
  - Test pagination with venue filter
  - _Requirements: 3.2, 3.3, 5.2_

- [ ] 3.4 Implement DynamoDB repository method
  - Update `src/shared/infra/repositories/session_repository_dynamo.py`
  - Implement `get_sessions_by_venue_paginated(venue_name, page_size, last_evaluated_key)`
  - Use PaginationHelper for validation and token handling
  - Query with venue filter and pagination parameters
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 8.2_

- [ ] 3.5 Write DynamoDB repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_dynamo.py`
  - Test `get_sessions_by_venue_paginated` with venue filter
  - Test pagination with venue filter
  - _Requirements: 3.2, 3.3, 5.2, 5.3, 7.1_

- [ ] 3.6 Implement use case
  - Create `src/modules/get_sessions_by_venue_paginated/` directory structure
  - Create `src/modules/get_sessions_by_venue_paginated/app/get_sessions_by_venue_paginated_usecase.py`
  - Implement `GetSessionsByVenuePaginatedUsecase` class
  - Implement `__call__(venue_name, page_size, last_evaluated_key)` method
  - _Requirements: 3.2, 3.3, 8.3_

- [ ] 3.7 Write use case tests
  - Create `tests/modules/get_sessions_by_venue_paginated/app/test_get_sessions_by_venue_paginated_usecase.py`
  - Test use case with venue filter and pagination
  - _Requirements: 3.2, 3.3_

- [ ] 3.8 Implement view model
  - Create `src/modules/get_sessions_by_venue_paginated/app/get_sessions_by_venue_paginated_viewmodel.py`
  - Implement `GetSessionsByVenuePaginatedViewmodel` class
  - Include venue_name in response along with pagination metadata
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.5_

- [ ] 3.9 Write view model tests
  - Create `tests/modules/get_sessions_by_venue_paginated/app/test_get_sessions_by_venue_paginated_viewmodel.py`
  - Test view model includes venue_name and pagination metadata
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 3.10 Implement controller
  - Create `src/modules/get_sessions_by_venue_paginated/app/get_sessions_by_venue_paginated_controller.py`
  - Implement `GetSessionsByVenuePaginatedController` class
  - Extract venue_name, page_size, and last_evaluated_key from query parameters
  - Validate venue_name is provided (raise MissingParameters)
  - Validate page_size is provided (raise MissingParameters)
  - Handle all pagination validation errors
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [ ] 3.11 Write controller tests
  - Create `tests/modules/get_sessions_by_venue_paginated/app/test_get_sessions_by_venue_paginated_controller.py`
  - Test missing venue_name returns 400
  - Test missing page_size returns 400
  - Test pagination validation errors
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 3.12 Implement presenter
  - Create `src/modules/get_sessions_by_venue_paginated/app/get_sessions_by_venue_paginated_presenter.py`
  - Initialize repository, use case, and controller
  - Implement lambda_handler function
  - _Requirements: 8.5_

- [ ] 3.13 Write presenter tests
  - Create `tests/modules/get_sessions_by_venue_paginated/app/test_get_sessions_by_venue_paginated_presenter.py`
  - Test lambda_handler with valid event
  - _Requirements: 8.5_

- [ ] 3.14 Add Lambda function to CDK stack
  - Update `iac/iac/lambda_stack.py`
  - Add `get_sessions_by_venue_paginated_function` as GET method on `/sessions/by-venue/paginated`
  - Set memory to 512 MB and timeout to 30 seconds
  - Add function to `functions_that_need_dynamo_permissions` list
  - _Requirements: 8.5_

---

## Feature 3: Get Sessions By Day Paginated

- [ ] 4. Implement Get Sessions By Day Paginated
- [ ] 4.1 Add repository interface method
  - Update `src/shared/domain/repositories/session_repository_interface.py`
  - Add `get_sessions_by_day_paginated(day, page_size, last_evaluated_key)` abstract method
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.1_

- [ ] 4.2 Implement Mock repository method
  - Update `src/shared/infra/repositories/session_repository_mock.py`
  - Implement `get_sessions_by_day_paginated(day, page_size, last_evaluated_key)`
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.2_

- [ ] 4.3 Write Mock repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_mock.py`
  - Test `get_sessions_by_day_paginated` filters correctly
  - _Requirements: 3.2, 3.3, 5.2_

- [ ] 4.4 Implement DynamoDB repository method
  - Update `src/shared/infra/repositories/session_repository_dynamo.py`
  - Implement `get_sessions_by_day_paginated(day, page_size, last_evaluated_key)`
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 8.2_

- [ ] 4.5 Write DynamoDB repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_dynamo.py`
  - Test `get_sessions_by_day_paginated` with day filter
  - _Requirements: 3.2, 3.3, 5.2, 5.3, 7.1_

- [ ] 4.6 Implement use case
  - Create `src/modules/get_sessions_by_day_paginated/` directory structure
  - Create `src/modules/get_sessions_by_day_paginated/app/get_sessions_by_day_paginated_usecase.py`
  - Implement `GetSessionsByDayPaginatedUsecase` class
  - _Requirements: 3.2, 3.3, 8.3_

- [ ] 4.7 Write use case tests
  - Create `tests/modules/get_sessions_by_day_paginated/app/test_get_sessions_by_day_paginated_usecase.py`
  - Test use case with day filter and pagination
  - _Requirements: 3.2, 3.3_

- [ ] 4.8 Implement view model
  - Create `src/modules/get_sessions_by_day_paginated/app/get_sessions_by_day_paginated_viewmodel.py`
  - Implement `GetSessionsByDayPaginatedViewmodel` class
  - Include day in response
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.5_

- [ ] 4.9 Write view model tests
  - Create `tests/modules/get_sessions_by_day_paginated/app/test_get_sessions_by_day_paginated_viewmodel.py`
  - Test view model includes day and pagination metadata
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4.10 Implement controller
  - Create `src/modules/get_sessions_by_day_paginated/app/get_sessions_by_day_paginated_controller.py`
  - Implement `GetSessionsByDayPaginatedController` class
  - Extract day, page_size, and last_evaluated_key
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [ ] 4.11 Write controller tests
  - Create `tests/modules/get_sessions_by_day_paginated/app/test_get_sessions_by_day_paginated_controller.py`
  - Test missing day returns 400
  - Test missing page_size returns 400
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 4.12 Implement presenter
  - Create `src/modules/get_sessions_by_day_paginated/app/get_sessions_by_day_paginated_presenter.py`
  - Implement lambda_handler function
  - _Requirements: 8.5_

- [ ] 4.13 Write presenter tests
  - Create `tests/modules/get_sessions_by_day_paginated/app/test_get_sessions_by_day_paginated_presenter.py`
  - Test lambda_handler with valid event
  - _Requirements: 8.5_

- [ ] 4.14 Add Lambda function to CDK stack
  - Update `iac/iac/lambda_stack.py`
  - Add `get_sessions_by_day_paginated_function` as GET method on `/sessions/by-day/paginated`
  - _Requirements: 8.5_

---

## Feature 4: Get Sessions By Level Paginated

- [ ] 5. Implement Get Sessions By Level Paginated
- [ ] 5.1 Add repository interface method
  - Update `src/shared/domain/repositories/session_repository_interface.py`
  - Add `get_sessions_by_level_paginated(level_value, page_size, last_evaluated_key)` abstract method
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.1_

- [ ] 5.2 Implement Mock repository method
  - Update `src/shared/infra/repositories/session_repository_mock.py`
  - Implement `get_sessions_by_level_paginated(level_value, page_size, last_evaluated_key)`
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 8.2_

- [ ] 5.3 Write Mock repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_mock.py`
  - Test `get_sessions_by_level_paginated` filters correctly
  - _Requirements: 3.2, 3.3, 5.2_

- [ ] 5.4 Implement DynamoDB repository method
  - Update `src/shared/infra/repositories/session_repository_dynamo.py`
  - Implement `get_sessions_by_level_paginated(level_value, page_size, last_evaluated_key)`
  - _Requirements: 3.2, 3.3, 5.1, 5.2, 5.3, 7.1, 7.2, 7.3, 8.2_

- [ ] 5.5 Write DynamoDB repository method tests
  - Update `tests/shared/infra/repositories/test_session_repository_dynamo.py`
  - Test `get_sessions_by_level_paginated` with level filter
  - _Requirements: 3.2, 3.3, 5.2, 5.3, 7.1_

- [ ] 5.6 Implement use case
  - Create `src/modules/get_sessions_by_level_paginated/` directory structure
  - Create `src/modules/get_sessions_by_level_paginated/app/get_sessions_by_level_paginated_usecase.py`
  - Implement `GetSessionsByLevelPaginatedUsecase` class
  - _Requirements: 3.2, 3.3, 8.3_

- [ ] 5.7 Write use case tests
  - Create `tests/modules/get_sessions_by_level_paginated/app/test_get_sessions_by_level_paginated_usecase.py`
  - Test use case with level filter and pagination
  - _Requirements: 3.2, 3.3_

- [ ] 5.8 Implement view model
  - Create `src/modules/get_sessions_by_level_paginated/app/get_sessions_by_level_paginated_viewmodel.py`
  - Implement `GetSessionsByLevelPaginatedViewmodel` class
  - Include level_value in response
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.5_

- [ ] 5.9 Write view model tests
  - Create `tests/modules/get_sessions_by_level_paginated/app/test_get_sessions_by_level_paginated_viewmodel.py`
  - Test view model includes level_value and pagination metadata
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 5.10 Implement controller
  - Create `src/modules/get_sessions_by_level_paginated/app/get_sessions_by_level_paginated_controller.py`
  - Implement `GetSessionsByLevelPaginatedController` class
  - Extract level_value, page_size, and last_evaluated_key
  - Convert level_value to int
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 3.3, 6.1, 6.2, 6.3, 6.4, 6.5, 8.4_

- [ ] 5.11 Write controller tests
  - Create `tests/modules/get_sessions_by_level_paginated/app/test_get_sessions_by_level_paginated_controller.py`
  - Test missing level_value returns 400
  - Test missing page_size returns 400
  - Test invalid level_value type returns 400
  - _Requirements: 1.1, 1.5, 2.1, 2.5, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 5.12 Implement presenter
  - Create `src/modules/get_sessions_by_level_paginated/app/get_sessions_by_level_paginated_presenter.py`
  - Implement lambda_handler function
  - _Requirements: 8.5_

- [ ] 5.13 Write presenter tests
  - Create `tests/modules/get_sessions_by_level_paginated/app/test_get_sessions_by_level_paginated_presenter.py`
  - Test lambda_handler with valid event
  - _Requirements: 8.5_

- [ ] 5.14 Add Lambda function to CDK stack
  - Update `iac/iac/lambda_stack.py`
  - Add `get_sessions_by_level_paginated_function` as GET method on `/sessions/by-level/paginated`
  - _Requirements: 8.5_

---

## Notes

- Each feature is implemented completely before moving to the next
- Follow Clean Architecture dependency rules strictly
- All new features are separate from existing endpoints
- Existing endpoints remain completely unchanged
- Token TTL is set to 5 minutes (300 seconds) by default
- page_size is required for all paginated endpoints
- page_size must be between 1 and 100
- Pagination tokens expire after 5 minutes
- All new Lambda functions require DynamoDB permissions
