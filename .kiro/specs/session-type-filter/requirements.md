# Requirements Document

## Introduction

This document specifies requirements for adding session type filtering capability to the existing session search feature. The enhancement will enable users to filter sessions by their type (e.g., "Breakout Session", "Workshop", "Chalk Talk") using a simple string-based filter on the session_type field in DynamoDB.

## Glossary

- **Session**: A re:Invent conference session entity with attributes including session_type, title, venue, day, level, etc.
- **Session Type**: A string field indicating the format/type of the session (e.g., "Breakout Session", "Workshop", "Chalk Talk", "Lightning Talk")
- **Search System**: The complete search implementation including repository methods, use case, controller, and API endpoint
- **DynamoDB Repository**: The SessionRepositoryDynamo implementation that queries DynamoDB with GSI optimization
- **GSI (Global Secondary Index)**: DynamoDB index structure used for efficient querying on non-primary-key attributes
- **Filter Criteria**: Parameters used to narrow search results (day, venue, level, keywords, speaker, session_type)

## Requirements

### Requirement 1

**User Story:** As an API consumer, I want to filter sessions by session type, so that I can find sessions in specific formats that match my learning preferences.

#### Acceptance Criteria

1. WHEN a user provides a session_type parameter THEN the System SHALL return only sessions where session_type equals that value
2. WHEN a user provides a session_type parameter THEN the System SHALL use case-insensitive matching
3. WHEN a user provides a partial session_type THEN the System SHALL return sessions where session_type contains that partial string
4. WHEN a user combines session_type filter with other filters THEN the System SHALL return sessions matching all provided criteria
5. WHEN a user searches for a non-existent session_type THEN the System SHALL return an empty result set with 200 OK status

### Requirement 2

**User Story:** As a developer, I want the session_type filter to follow the same patterns as existing filters, so that the implementation is consistent and maintainable.

#### Acceptance Criteria

1. WHEN implementing session_type search THEN the System SHALL add session_type parameter to the search_sessions repository method
2. WHEN implementing session_type search THEN the System SHALL add session_type parameter to the SearchSessionsUsecase
3. WHEN implementing session_type search THEN the System SHALL add session_type parameter to the SearchSessionsController
4. WHEN implementing session_type search THEN the System SHALL validate session_type parameter is a non-empty string if provided
5. WHEN session_type filter is invalid THEN the System SHALL return 400 Bad Request with descriptive error message

### Requirement 3

**User Story:** As a system maintainer, I want session_type filtering to work efficiently with DynamoDB, so that search performance remains acceptable.

#### Acceptance Criteria

1. WHEN only session_type filter is provided THEN the System SHALL perform a scan with FilterExpression
2. WHEN session_type filter is combined with indexed filters THEN the System SHALL query the GSI first then filter by session_type using FilterExpression
3. WHEN session_type filter is combined with keyword search THEN the System SHALL apply both filters appropriately
4. WHEN filtering by session_type THEN the System SHALL use case-insensitive matching
5. WHEN filtering by session_type THEN the System SHALL support partial string matching

### Requirement 4

**User Story:** As a developer, I want comprehensive tests for session_type filtering, so that I can verify the feature works correctly across all scenarios.

#### Acceptance Criteria

1. WHEN testing session_type search THEN the System SHALL include unit tests for use case validation
2. WHEN testing session_type search THEN the System SHALL include unit tests for controller parameter handling
3. WHEN testing session_type search THEN the System SHALL include unit tests for repository filtering logic
4. WHEN testing session_type search THEN the System SHALL include integration tests with DynamoDB
5. WHEN testing session_type search THEN the System SHALL verify case-insensitive matching
6. WHEN testing session_type search THEN the System SHALL verify partial string matching

### Requirement 5

**User Story:** As an API consumer, I want clear documentation for the session_type filter parameter, so that I can use it correctly in my applications.

#### Acceptance Criteria

1. WHEN the session_type filter is implemented THEN the System SHALL accept a session_type query parameter
2. WHEN the session_type parameter is provided THEN the System SHALL accept any non-empty string value
3. WHEN the session_type parameter is empty or whitespace-only THEN the System SHALL return 400 Bad Request
4. WHEN the session_type parameter is omitted THEN the System SHALL perform search without session_type filtering
5. WHEN search includes session_type filter THEN the System SHALL return 200 OK with matching sessions
