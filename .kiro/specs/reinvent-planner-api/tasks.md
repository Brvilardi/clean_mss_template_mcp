# Implementation Plan: re:invent Planner API

## Overview
This implementation plan follows Clean Architecture principles to build a feature that fetches AWS re:invent session data from an external API, stores it in SQLite, and provides query endpoints. The plan is organized to build incrementally from domain layer outward.

---

## Domain Layer Implementation

- [x] 1. Create Session entity and validation
  - Create `src/shared/domain/entities/session.py` with Session class
  - Implement attributes: session_id, short_id, title, abstract, session_type, venue_name, venue_room, start_datetime, end_datetime, day, speakers, topics, areas_of_interest, level, level_value, features, seat_capacity
  - Implement static validation methods: validate_session_id, validate_title, validate_datetime, validate_session_type, validate_level_value
  - Add constructor with validation logic raising EntityError for invalid data
  - _Requirements: 1.3, 1.4, 5.4, 6.1_

- [x] 1.1 Write Session entity tests
  - Create `tests/shared/domain/entities/test_session.py`
  - Test Session validation methods with valid and invalid inputs
  - Test constructor with various data combinations
  - Test edge cases (empty strings, None values, invalid datetime formats)
  - _Requirements: 1.3, 5.4_

- [x] 2. Create Session repository interface
  - Create `src/shared/domain/repositories/session_repository_interface.py` with ISessionRepository
  - Define abstract methods: get_all_sessions(), sync_sessions_from_api(), get_session_by_id(session_id)
  - Add docstrings specifying return types and exceptions (NoItemsFound)
  - _Requirements: 2.1, 3.2, 4.2, 6.2_

---

## Infrastructure Layer Implementation

- [x] 3. Create external API client for re:invent catalog
  - Create `src/shared/infra/external/reinvent/` directory
  - Create `src/shared/infra/external/reinvent/__init__.py`
  - Create `src/shared/infra/external/reinvent/reinvent_catalog_client.py` with ReinventCatalogClient class
  - Implement fetch_sessions() method calling https://reinvent-planner.cloud/api/catalog
  - Handle connection errors and return list of session dictionaries
  - Add proper error logging for API failures
  - _Requirements: 1.1, 1.2, 4.2, 4.3, 5.1_

- [x] 4. Create Session SQLite DTO
  - Create `src/shared/infra/dto/session_sqlite_dto.py` with SessionSQLiteDTO class
  - Implement attributes matching database schema with JSON fields for lists
  - Implement from_entity(session) static method to convert Session to DTO
  - Implement to_entity() method to convert DTO to Session
  - Implement to_sqlite() method returning dict for database insertion
  - Implement from_sqlite(data) static method to create DTO from database row
  - Handle JSON serialization/deserialization for speakers, topics, areas_of_interest, features
  - _Requirements: 2.2, 2.3, 6.3_

- [x] 4.1 Write Session DTO tests
  - Create `tests/shared/infra/dto/test_session_sqlite_dto.py`
  - Test from_entity() conversion
  - Test to_entity() conversion
  - Test to_sqlite() serialization
  - Test from_sqlite() deserialization
  - Test JSON list handling for speakers, topics, areas_of_interest, features
  - _Requirements: 2.2, 2.3_

- [x] 5. Create SQLite database infrastructure
  - Create `src/shared/infra/external/sqlite/` directory
  - Create `src/shared/infra/external/sqlite/__init__.py`
  - Create database schema creation logic in repository (sessions table with all columns)
  - Add created_at and updated_at timestamp columns with triggers
  - _Requirements: 2.1, 2.2, 6.3_

- [x] 6. Implement Session Repository SQLite
  - Create `src/shared/infra/repositories/session_repository_sqlite.py` with SessionRepositorySQLite class
  - Implement __init__() to create database file at `src/shared/infra/external/sqlite/reinvent_sessions.db`
  - Implement _initialize_database() to create schema if not exists
  - Implement _fetch_from_external_api() using ReinventCatalogClient
  - Implement auto-population logic in __init__() when database is empty
  - Implement get_all_sessions() with SELECT query and DTO conversion
  - Implement get_session_by_id(session_id) with error handling
  - Implement sync_sessions_from_api() with fetch, parse, and upsert logic
  - Implement _upsert_session(session) with INSERT OR REPLACE
  - Use transactions for bulk operations
  - Add comprehensive error handling and logging
  - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.3, 2.4, 2.5, 3.2, 4.2, 4.4, 5.1, 5.3, 6.3_

- [x] 6.1 Write Session Repository SQLite tests
  - Create `tests/shared/infra/repositories/test_session_repository_sqlite.py`
  - Test database creation and schema initialization
  - Test get_all_sessions() with empty and populated database
  - Test sync_sessions_from_api() with mock API client
  - Test get_session_by_id() with valid and invalid IDs
  - Test transaction rollback on errors
  - _Requirements: 2.1, 2.4, 2.5, 3.2, 4.2, 4.4_

- [x] 7. Implement Session Repository Mock
  - Create `src/shared/infra/repositories/session_repository_mock.py` with SessionRepositoryMock class
  - Pre-populate with 3-5 sample re:invent sessions covering different types
  - Implement all interface methods (get_all_sessions, sync_sessions_from_api, get_session_by_id)
  - Mock sync operation to simulate API fetch
  - _Requirements: 6.3_

- [x] 8. Update Environments configuration
  - Add get_session_repo() static method to `src/shared/environments.py`
  - Return SessionRepositoryMock for TEST stage
  - Return SessionRepositorySQLite for DEV, HOMOLOG, PROD stages
  - _Requirements: 6.3_

---

## Application Layer - Get All Sessions Feature

- [x] 9. Implement Get All Sessions use case
  - Create `src/modules/get_all_sessions/` directory structure
  - Create `src/modules/get_all_sessions/__init__.py`
  - Create `src/modules/get_all_sessions/app/` directory
  - Create `src/modules/get_all_sessions/app/__init__.py`
  - Create `src/modules/get_all_sessions/app/get_all_sessions_usecase.py` with GetAllSessionsUsecase class
  - Implement __call__() method calling repo.get_all_sessions()
  - Return list of Session entities
  - _Requirements: 3.1, 3.2, 6.4_

- [x] 9.1 Write Get All Sessions use case tests
  - Create `tests/modules/get_all_sessions/app/test_get_all_sessions_usecase.py`
  - Test with mock repository returning sessions
  - Test with empty repository
  - _Requirements: 3.1_

- [x] 10. Implement Get All Sessions view model
  - Create `src/modules/get_all_sessions/app/get_all_sessions_viewmodel.py`
  - Create SessionViewmodel class for individual session serialization
  - Create GetAllSessionsViewmodel class with sessions list
  - Implement to_dict() returning JSON-serializable dict with sessions array and count
  - Include all session attributes in output
  - _Requirements: 3.3, 6.5_

- [x] 10.1 Write Get All Sessions view model tests
  - Create `tests/modules/get_all_sessions/app/test_get_all_sessions_viewmodel.py`
  - Test to_dict() output format
  - Test with empty sessions list
  - Test data transformation accuracy
  - _Requirements: 3.3_

- [x] 11. Implement Get All Sessions controller
  - Create `src/modules/get_all_sessions/app/get_all_sessions_controller.py` with GetAllSessionsController class
  - Implement __call__(request) method
  - Call use case and create view model
  - Handle exceptions: NoItemsFound (404), EntityError (400), Exception (500)
  - Return OK (200) with view model data or empty array
  - _Requirements: 3.3, 3.4, 3.5, 5.2, 6.5_

- [x] 11.1 Write Get All Sessions controller tests
  - Create `tests/modules/get_all_sessions/app/test_get_all_sessions_controller.py`
  - Test successful request handling
  - Test error response mapping
  - Test HTTP status codes
  - _Requirements: 3.3, 3.5, 5.2_

- [x] 12. Implement Get All Sessions presenter
  - Create `src/modules/get_all_sessions/app/get_all_sessions_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Application Layer - Sync Sessions Feature

- [x] 13. Implement Sync Sessions use case
  - Create `src/modules/sync_sessions/` directory structure
  - Create `src/modules/sync_sessions/__init__.py`
  - Create `src/modules/sync_sessions/app/` directory
  - Create `src/modules/sync_sessions/app/__init__.py`
  - Create `src/modules/sync_sessions/app/sync_sessions_usecase.py` with SyncSessionsUsecase class
  - Implement __call__() method calling repo.sync_sessions_from_api()
  - Calculate and return dict with inserted, updated, and total counts
  - _Requirements: 4.1, 4.2, 4.4, 6.4_

- [x] 13.1 Write Sync Sessions use case tests
  - Create `tests/modules/sync_sessions/app/test_sync_sessions_usecase.py`
  - Test sync operation with mock repository
  - Test return value structure
  - _Requirements: 4.1_

- [x] 14. Implement Sync Sessions view model
  - Create `src/modules/sync_sessions/app/sync_sessions_viewmodel.py`
  - Create SyncSessionsViewmodel class
  - Implement to_dict() returning success message with inserted, updated, and total counts
  - _Requirements: 4.5, 6.5_

- [x] 14.1 Write Sync Sessions view model tests
  - Create `tests/modules/sync_sessions/app/test_sync_sessions_viewmodel.py`
  - Test to_dict() with various sync results
  - _Requirements: 4.5_

- [x] 15. Implement Sync Sessions controller
  - Create `src/modules/sync_sessions/app/sync_sessions_controller.py` with SyncSessionsController class
  - Implement __call__(request) method
  - Call use case and create view model
  - Handle exceptions: ConnectionError (503), EntityError (400), Exception (500)
  - Return OK (200) with sync statistics on success
  - _Requirements: 4.3, 4.5, 5.2, 6.5_

- [x] 15.1 Write Sync Sessions controller tests
  - Create `tests/modules/sync_sessions/app/test_sync_sessions_controller.py`
  - Test successful sync
  - Test connection error handling (503)
  - _Requirements: 4.3, 4.5, 5.2_

- [x] 16. Implement Sync Sessions presenter
  - Create `src/modules/sync_sessions/app/sync_sessions_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Infrastructure as Code

- [x] 17. Add Lambda functions to CDK stack
  - Update `iac/iac/lambda_stack.py` to add get_all_sessions_function
  - Configure as GET method on appropriate API Gateway resource
  - Update `iac/iac/lambda_stack.py` to add sync_sessions_function
  - Configure as POST method on appropriate API Gateway resource
  - Set memory to 512 MB and timeout to 30 seconds for both functions
  - Add environment variables if needed
  - Note: SQLite functions do NOT need DynamoDB permissions
  - _Requirements: 6.5_

---

## Application Layer - Get Sessions by Venue Feature

- [ ] 18. Implement Get Sessions by Venue feature
- [ ] 18.1 Implement Get Sessions by Venue use case
  - Create `src/modules/get_sessions_by_venue/` directory structure
  - Create `src/modules/get_sessions_by_venue/__init__.py`
  - Create `src/modules/get_sessions_by_venue/app/` directory
  - Create `src/modules/get_sessions_by_venue/app/__init__.py`
  - Create `src/modules/get_sessions_by_venue/app/get_sessions_by_venue_usecase.py` with GetSessionsByVenueUsecase class
  - Implement __call__(venue_name: str) method that filters sessions by venue_name
  - Return list of Session entities matching the venue
  - Create `tests/modules/get_sessions_by_venue/app/test_get_sessions_by_venue_usecase.py`
  - Test with mock repository returning filtered sessions
  - Test with venue that has no sessions
  - Test case-insensitive matching
  - _Requirements: 3.1, 3.2, 6.4_

- [ ] 18.2 Implement Get Sessions by Venue view model
  - Create `src/modules/get_sessions_by_venue/app/get_sessions_by_venue_viewmodel.py`
  - Create GetSessionsByVenueViewmodel class with sessions list
  - Implement to_dict() returning JSON-serializable dict with sessions array, count, and venue_name
  - Include all session attributes in output
  - Create `tests/modules/get_sessions_by_venue/app/test_get_sessions_by_venue_viewmodel.py`
  - Test to_dict() output format
  - Test with empty sessions list
  - _Requirements: 3.3, 6.5_

- [ ] 18.3 Implement Get Sessions by Venue controller
  - Create `src/modules/get_sessions_by_venue/app/get_sessions_by_venue_controller.py` with GetSessionsByVenueController class
  - Implement __call__(request) method
  - Extract venue_name from query parameters
  - Handle missing venue_name parameter (400)
  - Call use case and create view model
  - Handle exceptions: MissingParameters (400), EntityError (400), Exception (500)
  - Return OK (200) with view model data or empty array
  - Create `tests/modules/get_sessions_by_venue/app/test_get_sessions_by_venue_controller.py`
  - Test successful request handling
  - Test missing venue_name parameter
  - Test error response mapping
  - _Requirements: 3.3, 3.4, 3.5, 5.2, 6.5_

- [ ] 18.4 Implement Get Sessions by Venue presenter
  - Create `src/modules/get_sessions_by_venue/app/get_sessions_by_venue_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Application Layer - Get Sessions by Day Feature

- [ ] 19. Implement Get Sessions by Day feature
- [ ] 19.1 Implement Get Sessions by Day use case
  - Create `src/modules/get_sessions_by_day/` directory structure
  - Create `src/modules/get_sessions_by_day/__init__.py`
  - Create `src/modules/get_sessions_by_day/app/` directory
  - Create `src/modules/get_sessions_by_day/app/__init__.py`
  - Create `src/modules/get_sessions_by_day/app/get_sessions_by_day_usecase.py` with GetSessionsByDayUsecase class
  - Implement __call__(day: str) method that filters sessions by day
  - Return list of Session entities matching the day
  - Create `tests/modules/get_sessions_by_day/app/test_get_sessions_by_day_usecase.py`
  - Test with mock repository returning filtered sessions
  - Test with day that has no sessions
  - Test case-insensitive matching
  - _Requirements: 3.1, 3.2, 6.4_

- [ ] 19.2 Implement Get Sessions by Day view model
  - Create `src/modules/get_sessions_by_day/app/get_sessions_by_day_viewmodel.py`
  - Create GetSessionsByDayViewmodel class with sessions list
  - Implement to_dict() returning JSON-serializable dict with sessions array, count, and day
  - Include all session attributes in output
  - Create `tests/modules/get_sessions_by_day/app/test_get_sessions_by_day_viewmodel.py`
  - Test to_dict() output format
  - Test with empty sessions list
  - _Requirements: 3.3, 6.5_

- [ ] 19.3 Implement Get Sessions by Day controller
  - Create `src/modules/get_sessions_by_day/app/get_sessions_by_day_controller.py` with GetSessionsByDayController class
  - Implement __call__(request) method
  - Extract day from query parameters
  - Handle missing day parameter (400)
  - Call use case and create view model
  - Handle exceptions: MissingParameters (400), EntityError (400), Exception (500)
  - Return OK (200) with view model data or empty array
  - Create `tests/modules/get_sessions_by_day/app/test_get_sessions_by_day_controller.py`
  - Test successful request handling
  - Test missing day parameter
  - Test error response mapping
  - _Requirements: 3.3, 3.4, 3.5, 5.2, 6.5_

- [ ] 19.4 Implement Get Sessions by Day presenter
  - Create `src/modules/get_sessions_by_day/app/get_sessions_by_day_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Application Layer - Get Sessions by Level Feature

- [ ] 20. Implement Get Sessions by Level feature
- [ ] 20.1 Implement Get Sessions by Level use case
  - Create `src/modules/get_sessions_by_level/` directory structure
  - Create `src/modules/get_sessions_by_level/__init__.py`
  - Create `src/modules/get_sessions_by_level/app/` directory
  - Create `src/modules/get_sessions_by_level/app/__init__.py`
  - Create `src/modules/get_sessions_by_level/app/get_sessions_by_level_usecase.py` with GetSessionsByLevelUsecase class
  - Implement __call__(level_value: int) method that filters sessions by level_value
  - Validate level_value is one of: 100, 200, 300, 400
  - Return list of Session entities matching the level
  - Create `tests/modules/get_sessions_by_level/app/test_get_sessions_by_level_usecase.py`
  - Test with mock repository returning filtered sessions
  - Test with level that has no sessions
  - Test invalid level_value raises EntityError
  - _Requirements: 3.1, 3.2, 6.4_

- [ ] 20.2 Implement Get Sessions by Level view model
  - Create `src/modules/get_sessions_by_level/app/get_sessions_by_level_viewmodel.py`
  - Create GetSessionsByLevelViewmodel class with sessions list
  - Implement to_dict() returning JSON-serializable dict with sessions array, count, and level_value
  - Include all session attributes in output
  - Create `tests/modules/get_sessions_by_level/app/test_get_sessions_by_level_viewmodel.py`
  - Test to_dict() output format
  - Test with empty sessions list
  - _Requirements: 3.3, 6.5_

- [ ] 20.3 Implement Get Sessions by Level controller
  - Create `src/modules/get_sessions_by_level/app/get_sessions_by_level_controller.py` with GetSessionsByLevelController class
  - Implement __call__(request) method
  - Extract level_value from query parameters
  - Handle missing level_value parameter (400)
  - Convert level_value to integer
  - Handle invalid type conversion (400)
  - Call use case and create view model
  - Handle exceptions: MissingParameters (400), WrongTypeParameter (400), EntityError (400), Exception (500)
  - Return OK (200) with view model data or empty array
  - Create `tests/modules/get_sessions_by_level/app/test_get_sessions_by_level_controller.py`
  - Test successful request handling
  - Test missing level_value parameter
  - Test invalid level_value type
  - Test invalid level_value (not 100/200/300/400)
  - Test error response mapping
  - _Requirements: 3.3, 3.4, 3.5, 5.2, 6.5_

- [ ] 20.4 Implement Get Sessions by Level presenter
  - Create `src/modules/get_sessions_by_level/app/get_sessions_by_level_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Application Layer - Get Sessions by Short ID Feature

- [ ] 21. Implement Get Sessions by Short ID feature
- [ ] 21.1 Implement Get Sessions by Short ID use case
  - Create `src/modules/get_sessions_by_short_id/` directory structure
  - Create `src/modules/get_sessions_by_short_id/__init__.py`
  - Create `src/modules/get_sessions_by_short_id/app/` directory
  - Create `src/modules/get_sessions_by_short_id/app/__init__.py`
  - Create `src/modules/get_sessions_by_short_id/app/get_sessions_by_short_id_usecase.py` with GetSessionsByShortIdUsecase class
  - Implement __call__(short_id: str) method that filters sessions by short_id
  - Return list of Session entities matching the short_id (should be 0 or 1 result)
  - Create `tests/modules/get_sessions_by_short_id/app/test_get_sessions_by_short_id_usecase.py`
  - Test with mock repository returning matching session
  - Test with short_id that doesn't exist
  - Test case-insensitive matching
  - _Requirements: 3.1, 3.2, 6.4_

- [ ] 21.2 Implement Get Sessions by Short ID view model
  - Create `src/modules/get_sessions_by_short_id/app/get_sessions_by_short_id_viewmodel.py`
  - Create GetSessionsByShortIdViewmodel class with sessions list
  - Implement to_dict() returning JSON-serializable dict with sessions array, count, and short_id
  - Include all session attributes in output
  - Create `tests/modules/get_sessions_by_short_id/app/test_get_sessions_by_short_id_viewmodel.py`
  - Test to_dict() output format
  - Test with empty sessions list
  - _Requirements: 3.3, 6.5_

- [ ] 21.3 Implement Get Sessions by Short ID controller
  - Create `src/modules/get_sessions_by_short_id/app/get_sessions_by_short_id_controller.py` with GetSessionsByShortIdController class
  - Implement __call__(request) method
  - Extract short_id from query parameters
  - Handle missing short_id parameter (400)
  - Call use case and create view model
  - Handle exceptions: MissingParameters (400), EntityError (400), Exception (500)
  - Return OK (200) with view model data or empty array
  - Create `tests/modules/get_sessions_by_short_id/app/test_get_sessions_by_short_id_controller.py`
  - Test successful request handling
  - Test missing short_id parameter
  - Test error response mapping
  - _Requirements: 3.3, 3.4, 3.5, 5.2, 6.5_

- [ ] 21.4 Implement Get Sessions by Short ID presenter
  - Create `src/modules/get_sessions_by_short_id/app/get_sessions_by_short_id_presenter.py`
  - Initialize repository using Environments.get_session_repo()
  - Create use case and controller instances
  - Implement lambda_handler(event, context) function
  - Convert Lambda event to LambdaHttpRequest
  - Return LambdaHttpResponse with proper status codes
  - _Requirements: 6.5_

---

## Infrastructure as Code - New Query Endpoints

- [ ] 22. Add new Lambda functions to CDK stack
  - Update `iac/iac/lambda_stack.py` to add get_sessions_by_venue_function
  - Configure as GET method with query parameter venue_name
  - Update `iac/iac/lambda_stack.py` to add get_sessions_by_day_function
  - Configure as GET method with query parameter day
  - Update `iac/iac/lambda_stack.py` to add get_sessions_by_level_function
  - Configure as GET method with query parameter level_value
  - Update `iac/iac/lambda_stack.py` to add get_sessions_by_short_id_function
  - Configure as GET method with query parameter short_id
  - Set memory to 512 MB and timeout to 30 seconds for all functions
  - Note: SQLite functions do NOT need DynamoDB permissions
  - _Requirements: 6.5_

---

## Notes

- Tasks marked with * are optional and focus on testing
- Each task builds incrementally on previous tasks
- Follow Clean Architecture dependency rules strictly
- SQLite database will be ephemeral in Lambda (stored in /tmp)
- Auto-initialization ensures database is populated on cold starts
- All validation happens in domain layer
- Error handling follows existing patterns in the codebase
- New query endpoints filter sessions from the existing get_all_sessions repository method
- All filtering logic is implemented in use cases, not in repository layer
