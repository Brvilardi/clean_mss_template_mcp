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

## Notes

- Tasks marked with * are optional and focus on testing
- Each task builds incrementally on previous tasks
- Follow Clean Architecture dependency rules strictly
- SQLite database will be ephemeral in Lambda (stored in /tmp)
- Auto-initialization ensures database is populated on cold starts
- All validation happens in domain layer
- Error handling follows existing patterns in the codebase
