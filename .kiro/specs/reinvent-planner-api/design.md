# Design Document: re:invent Planner API

## Overview

The re:invent Planner API is a feature that fetches AWS re:invent session data from an external catalog API, stores it in a local SQLite database, and provides endpoints to query and refresh this data. The implementation follows Clean Architecture principles, maintaining separation of concerns across domain, infrastructure, and application layers.

The system consists of two main operations:
1. **Get All Sessions**: Retrieve all sessions from the local SQLite database
2. **Sync Sessions**: Fetch latest data from the external API and update the local database

## Architecture

### Layer Structure

Following the existing Clean Architecture pattern in the codebase:

```
Domain Layer (Innermost)
├── Session Entity
├── Session Repository Interface
└── Session Validation Logic

Infrastructure Layer
├── Session SQLite DTO
├── Session Repository SQLite Implementation
├── Session Repository Mock Implementation
└── External API Client

Application Layer
├── Get All Sessions Use Case
├── Sync Sessions Use Case
├── Controllers (Get All Sessions, Sync Sessions)
├── View Models
└── Presenters (Lambda Handlers)

External Layer
└── AWS Lambda + API Gateway Integration
```

### Data Flow

**Get All Sessions Flow:**
```
API Gateway → Lambda → Presenter → Controller → Use Case → Repository → SQLite → Response
```

**Sync Sessions Flow:**
```
API Gateway → Lambda → Presenter → Controller → Use Case → External API Client
                                                          ↓
                                                    Repository → SQLite
```

**Repository Initialization Flow:**
```
Repository.__init__() → Check if DB exists → If empty, fetch from API → Populate DB
```

## Components and Interfaces

### 1. Domain Layer Components

#### Session Entity (`src/shared/domain/entities/session.py`)

Represents a re:invent session with the following attributes:

```python
class Session:
    session_id: str          # Unique identifier (id field from API)
    short_id: str           # Short session code (e.g., "TNC301")
    title: str              # Session title
    abstract: str           # Session description/abstract
    session_type: str       # Type display name (e.g., "Bootcamp", "Breakout Session")
    venue_name: str         # Venue display name (e.g., "Mandalay Bay")
    venue_room: str         # Room location (e.g., "Level 2 South | Breakers K")
    start_datetime: str     # ISO 8601 datetime string
    end_datetime: str       # ISO 8601 datetime string
    day: str               # Day of week (e.g., "Monday")
    speakers: List[dict]    # List of speaker objects with name, company
    topics: List[str]       # List of topic display names
    areas_of_interest: List[str]  # List of area display names
    level: str              # Difficulty level (e.g., "200 – Intermediate")
    level_value: int        # Numeric level (100, 200, 300, etc.)
    features: List[str]     # Session features (e.g., "Hands-on", "Interactive")
    seat_capacity: int      # Room capacity
```

**Validation Methods:**
- `validate_session_id(session_id: str) -> bool`: Ensures non-empty string
- `validate_title(title: str) -> bool`: Ensures non-empty string with min 3 characters
- `validate_datetime(datetime_str: str) -> bool`: Validates ISO 8601 format
- `validate_session_type(session_type: str) -> bool`: Ensures non-empty string
- `validate_level_value(level_value: int) -> bool`: Validates numeric level (100-400)

#### Session Repository Interface (`src/shared/domain/repositories/session_repository_interface.py`)

```python
class ISessionRepository(ABC):
    @abstractmethod
    def get_all_sessions(self) -> List[Session]:
        """Returns all sessions from storage"""
        pass
    
    @abstractmethod
    def sync_sessions_from_api(self) -> dict:
        """Fetches data from external API and updates storage
        Returns: {"inserted": int, "updated": int}
        """
        pass
    
    @abstractmethod
    def get_session_by_id(self, session_id: str) -> Session:
        """Returns a specific session by ID
        Raises: NoItemsFound if not found
        """
        pass
```

### 2. Infrastructure Layer Components

#### Session SQLite DTO (`src/shared/infra/dto/session_sqlite_dto.py`)

Handles conversion between Session entities and SQLite records:

```python
class SessionSQLiteDTO:
    session_id: str
    short_id: str
    title: str
    abstract: str
    session_type: str
    venue_name: str
    venue_room: str
    start_datetime: str
    end_datetime: str
    day: str
    speakers_json: str           # JSON serialized list of speaker dicts
    topics_json: str             # JSON serialized list
    areas_of_interest_json: str  # JSON serialized list
    level: str
    level_value: int
    features_json: str           # JSON serialized list
    seat_capacity: int
    
    @staticmethod
    def from_entity(session: Session) -> SessionSQLiteDTO:
        """Converts Session entity to DTO"""
        pass
    
    def to_entity(self) -> Session:
        """Converts DTO to Session entity"""
        pass
    
    def to_sqlite(self) -> dict:
        """Converts DTO to SQLite row dict"""
        pass
    
    @staticmethod
    def from_sqlite(data: dict) -> SessionSQLiteDTO:
        """Creates DTO from SQLite row"""
        pass
```

#### Session Repository SQLite (`src/shared/infra/repositories/session_repository_sqlite.py`)

Implements the repository interface using SQLite:

**Database Schema:**
```sql
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    short_id TEXT,
    title TEXT NOT NULL,
    abstract TEXT,
    session_type TEXT,
    venue_name TEXT,
    venue_room TEXT,
    start_datetime TEXT,
    end_datetime TEXT,
    day TEXT,
    speakers_json TEXT,
    topics_json TEXT,
    areas_of_interest_json TEXT,
    level TEXT,
    level_value INTEGER,
    features_json TEXT,
    seat_capacity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Key Methods:**
- `__init__()`: Creates database file if not exists, initializes schema, auto-populates if empty
- `_fetch_from_external_api() -> List[dict]`: Calls https://reinvent-planner.cloud/api/catalog
- `_initialize_database()`: Creates tables and triggers auto-sync if empty
- `get_all_sessions()`: SELECT * FROM sessions
- `sync_sessions_from_api()`: Fetches, parses, and upserts sessions
- `_upsert_session(session: Session)`: INSERT OR REPLACE logic

#### External API Client (`src/shared/infra/external/reinvent_catalog_client.py`)

Handles HTTP communication with the catalog API:

```python
class ReinventCatalogClient:
    BASE_URL = "https://reinvent-planner.cloud/api/catalog"
    
    def fetch_sessions(self) -> List[dict]:
        """Fetches all sessions from the catalog API
        Returns: List of session dictionaries
        Raises: ConnectionError if API is unreachable
        """
        pass
```

#### Session Repository Mock (`src/shared/infra/repositories/session_repository_mock.py`)

In-memory implementation for testing:

```python
class SessionRepositoryMock(ISessionRepository):
    def __init__(self):
        self.sessions: List[Session] = []
        # Pre-populate with sample data
```

### 3. Application Layer Components

#### Get All Sessions Use Case (`src/modules/get_all_sessions/app/get_all_sessions_usecase.py`)

```python
class GetAllSessionsUsecase:
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self) -> List[Session]:
        """Retrieves all sessions from repository"""
        return self.repo.get_all_sessions()
```

#### Sync Sessions Use Case (`src/modules/sync_sessions/app/sync_sessions_usecase.py`)

```python
class SyncSessionsUsecase:
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self) -> dict:
        """Triggers sync from external API
        Returns: {"inserted": int, "updated": int, "total": int}
        """
        result = self.repo.sync_sessions_from_api()
        result["total"] = result["inserted"] + result["updated"]
        return result
```

#### Controllers

**GetAllSessionsController:**
- Handles GET requests
- No input validation needed
- Returns 200 with session list or 500 on error

**SyncSessionsController:**
- Handles POST requests
- No input parameters required
- Returns 200 with sync statistics or 503 if API unreachable

#### View Models

**GetAllSessionsViewmodel:**
```python
def to_dict(self) -> dict:
    return {
        "sessions": [
            {
                "session_id": s.session_id,
                "short_id": s.short_id,
                "title": s.title,
                "abstract": s.abstract,
                "session_type": s.session_type,
                "venue_name": s.venue_name,
                "venue_room": s.venue_room,
                "start_datetime": s.start_datetime,
                "end_datetime": s.end_datetime,
                "day": s.day,
                "speakers": s.speakers,
                "topics": s.topics,
                "areas_of_interest": s.areas_of_interest,
                "level": s.level,
                "level_value": s.level_value,
                "features": s.features,
                "seat_capacity": s.seat_capacity
            }
            for s in self.sessions
        ],
        "count": len(self.sessions)
    }
```

**SyncSessionsViewmodel:**
```python
def to_dict(self) -> dict:
    return {
        "message": "Sessions synced successfully",
        "inserted": self.result["inserted"],
        "updated": self.result["updated"],
        "total": self.result["total"]
    }
```

## Data Models

### External API Response Format

Expected JSON structure from https://reinvent-planner.cloud/api/catalog:

```json
{
  "sessions": [
    {
      "id": "1753651605588001kjXl",
      "shortId": "TNC301",
      "title": "Accelerate VMware Migration with AWS Transform",
      "abstract": "This bootcamp is for AWS Partners only...",
      "startDateTime": "2025-12-04T21:00:00.000Z",
      "endDateTime": "2025-12-05T01:00:00.000Z",
      "day": "Thursday",
      "speakers": [
        {
          "displayName": "Parvesh Chopra",
          "company": "AWS"
        }
      ],
      "venueRoomName": "Level 2 South | Breakers K",
      "venue": {
        "displayName": "Mandalay Bay"
      },
      "type": {
        "displayName": "Bootcamp"
      },
      "level": {
        "displayName": "300 – Advanced",
        "value": 300
      },
      "topics": [
        {
          "displayName": "Artificial Intelligence"
        }
      ],
      "areaOfInterest": [
        {
          "displayName": "Training & Certification"
        }
      ],
      "features": [
        {
          "displayName": "Hands-on"
        }
      ],
      "seatCapacity": 126
    }
  ]
}
```

**Key Mapping:**
- `id` → `session_id`
- `shortId` → `short_id`
- `abstract` → `abstract`
- `startDateTime` → `start_datetime`
- `endDateTime` → `end_datetime`
- `venue.displayName` → `venue_name`
- `venueRoomName` → `venue_room`
- `type.displayName` → `session_type`
- `level.displayName` → `level`
- `level.value` → `level_value`
- `speakers` → `speakers` (array of objects)
- `topics[].displayName` → `topics` (array of strings)
- `areaOfInterest[].displayName` → `areas_of_interest` (array of strings)
- `features[].displayName` → `features` (array of strings)

### SQLite Storage Format

- Lists (speakers, topics, areas_of_interest, features) stored as JSON strings
- Speaker objects stored as JSON array of dicts with displayName and company
- Timestamps stored as ISO 8601 strings
- All text fields use TEXT type
- Numeric fields (level_value, seat_capacity) use INTEGER type
- session_id as PRIMARY KEY

### Internal Entity Format

Python dataclass with typed attributes, validated on construction.

## Error Handling

### Error Types and HTTP Responses

| Error Type | HTTP Status | Scenario |
|------------|-------------|----------|
| NoItemsFound | 404 | Session ID not found (future feature) |
| ConnectionError | 503 | External API unreachable |
| DatabaseError | 500 | SQLite operation failed |
| ValidationError | 400 | Invalid data format from API |
| Exception | 500 | Unexpected errors |

### Error Handling Strategy

1. **Repository Initialization**: Log warning if API fails, continue with empty DB
2. **Get All Sessions**: Return empty array if no sessions, never fail
3. **Sync Sessions**: Return 503 if API unreachable, rollback DB changes on error
4. **Database Errors**: Log full stack trace, return generic error message to client

### Logging

Use existing observability infrastructure:
- Log all API calls to external service
- Log database operations (create, sync)
- Log errors with full context
- Log sync statistics (inserted/updated counts)

## Testing Strategy

### Unit Tests

**Entity Tests:**
- Validation methods for all fields
- Constructor with valid/invalid data
- Edge cases (empty strings, None values, invalid formats)

**DTO Tests:**
- Conversion from entity to DTO
- Conversion from DTO to entity
- SQLite serialization/deserialization
- JSON list handling for speakers/topics

**Use Case Tests:**
- GetAllSessionsUsecase with mock repository
- SyncSessionsUsecase with mock repository
- Error handling scenarios

**Controller Tests:**
- Request handling with valid data
- Error response mapping
- HTTP status codes

**View Model Tests:**
- to_dict() output format
- Empty list handling
- Data transformation accuracy

### Integration Tests

**Repository Tests:**
- SQLite database creation
- CRUD operations
- Auto-initialization on first run
- Sync from mock API client
- Transaction rollback on error

**External API Client Tests:**
- Mock HTTP responses
- Connection error handling
- Response parsing

### Test Data

Create fixture with sample re:invent sessions covering:
- Different session types
- Various venues and times
- Multiple speakers and topics
- Different difficulty levels

## Implementation Notes

### SQLite Database Location

Store database file at: `src/shared/infra/external/sqlite/reinvent_sessions.db`

Create directory structure if it doesn't exist.

### Environment Configuration

Add to `src/shared/environments.py`:

```python
@staticmethod
def get_session_repo():
    if Environments.get_envs().STAGE == "TEST":
        return SessionRepositoryMock
    else:
        return SessionRepositorySQLite
```

### API Gateway Integration

Two endpoints:
1. `GET /sessions` → get_all_sessions_presenter
2. `POST /sessions/sync` → sync_sessions_presenter

### Performance Considerations

- SQLite is sufficient for read-heavy workload
- Index on session_id (PRIMARY KEY provides this)
- Consider adding index on start_time for future date filtering
- Sync operation should be async-friendly (no long blocking)

### Future Enhancements (Out of Scope)

- Filtering by date range, topic, or venue
- Pagination for large result sets
- Incremental sync (only fetch changed sessions)
- Caching layer for frequently accessed data
- WebSocket for real-time updates

## Dependencies

### New Python Packages

- `sqlite3` (built-in, no installation needed)
- `requests` (for HTTP calls to external API)

Add to `requirements.txt`:
```
requests>=2.31.0
```

### Existing Dependencies

- boto3 (for Lambda/DynamoDB if needed)
- pytest (for testing)
- Existing error handling and HTTP utilities

## Deployment Considerations

### Lambda Configuration

- Memory: 512 MB (sufficient for SQLite operations)
- Timeout: 30 seconds (allow time for API fetch)
- Environment Variables: None required (API URL is hardcoded)

### SQLite in Lambda

- Database file stored in `/tmp` directory (ephemeral)
- Auto-recreates and syncs on cold start
- Consider using EFS for persistent storage (future enhancement)

### CDK Changes

Add two Lambda functions to `iac/iac/lambda_stack.py`:
1. `get_all_sessions_function` (GET)
2. `sync_sessions_function` (POST)

No DynamoDB permissions needed for this feature.

## Security Considerations

- External API calls over HTTPS
- No authentication required for public catalog API
- Input validation on all data from external API
- SQL injection prevention (use parameterized queries)
- No sensitive data stored in database

## Monitoring and Observability

### Metrics to Track

- Number of sessions in database
- Sync operation duration
- External API response time
- Error rates by type
- Lambda cold start frequency

### CloudWatch Logs

- Log sync operations with timestamps
- Log API call success/failure
- Log database initialization events
- Log error details for troubleshooting

## Summary

This design implements a clean, maintainable solution for managing re:invent session data following the existing Clean Architecture patterns in the codebase. The SQLite-based approach provides simplicity and adequate performance for the use case, while the layered architecture ensures testability and future extensibility.
