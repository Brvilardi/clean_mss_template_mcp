# Design Document: Pagination for Session Endpoints

## Overview

This design adds pagination support to all existing session retrieval endpoints in the re:invent Planner API. The implementation leverages DynamoDB's native pagination capabilities and follows Clean Architecture principles by updating each layer systematically from domain to presentation.

The pagination design uses a cursor-based approach with base64-encoded tokens, providing efficient database queries and a simple API interface for consumers. All existing endpoints will support optional pagination parameters while maintaining backward compatibility.

## Architecture

### Pagination Flow

```
Client Request (page_size, last_evaluated_key)
    ↓
Controller (extract & validate pagination params)
    ↓
Use Case (pass pagination params)
    ↓
Repository (DynamoDB query with Limit & ExclusiveStartKey)
    ↓
Response (sessions + pagination metadata)
```

### Key Design Decisions

1. **Cursor-Based Pagination**: Using DynamoDB's LastEvaluatedKey for efficient queries
2. **Base64 Encoding**: Encoding pagination tokens for clean URL parameters
3. **Optional Parameters**: Backward compatible - pagination is opt-in
4. **Consistent Page Size**: Default 50, maximum 100 items per page
5. **Metadata in Response**: Include count, page_size, has_more, and last_evaluated_key
6. **Token TTL**: 5-minute expiration on pagination tokens to prevent stale pagination and sync issues

## Components and Interfaces

### 1. Domain Layer Updates

#### Updated Repository Interface

Add new paginated methods alongside existing methods:

```python
from typing import List, Dict, Optional, Tuple

class ISessionRepository(ABC):
    
    # Existing methods remain unchanged
    @abstractmethod
    def get_all_sessions(self) -> List[Session]:
        """Returns all sessions from storage."""
        pass
    
    @abstractmethod
    def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
        """Returns sessions filtered by venue name."""
        pass
    
    @abstractmethod
    def get_sessions_by_day(self, day: str) -> List[Session]:
        """Returns sessions filtered by day."""
        pass
    
    @abstractmethod
    def get_sessions_by_level(self, level_value: int) -> List[Session]:
        """Returns sessions filtered by level value."""
        pass
    
    @abstractmethod
    def get_sessions_by_short_id(self, short_id: str) -> List[Session]:
        """Returns sessions filtered by short_id."""
        pass
    
    # New paginated methods
    @abstractmethod
    def get_all_sessions_paginated(
        self, 
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns sessions from storage with pagination.
        
        Args:
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token
            
        Returns:
            Tuple of (sessions list, next_page_token)
            next_page_token is None if no more results
        """
        pass
    
    @abstractmethod
    def get_sessions_by_venue_paginated(
        self, 
        venue_name: str,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns sessions filtered by venue with pagination.
        
        Args:
            venue_name: The venue name to filter by
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token
            
        Returns:
            Tuple of (sessions list, next_page_token)
        """
        pass
    
    @abstractmethod
    def get_sessions_by_day_paginated(
        self, 
        day: str,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns sessions filtered by day with pagination.
        
        Args:
            day: The day to filter by
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token
            
        Returns:
            Tuple of (sessions list, next_page_token)
        """
        pass
    
    @abstractmethod
    def get_sessions_by_level_paginated(
        self, 
        level_value: int,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Returns sessions filtered by level with pagination.
        
        Args:
            level_value: The level value to filter by
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token
            
        Returns:
            Tuple of (sessions list, next_page_token)
        """
        pass
```

### 2. Infrastructure Layer Updates

#### Pagination Helper Utility

Create a new utility module for pagination token handling with TTL support:

**File**: `src/shared/helpers/pagination/pagination_helper.py`

```python
import base64
import json
import time
from typing import Optional, Dict

class PaginationHelper:
    
    # Default TTL for pagination tokens (5 minutes)
    DEFAULT_TOKEN_TTL_SECONDS = 300
    
    @staticmethod
    def encode_pagination_token(last_evaluated_key: Dict, ttl_seconds: int = DEFAULT_TOKEN_TTL_SECONDS) -> str:
        """
        Encodes DynamoDB LastEvaluatedKey to base64 string with TTL.
        
        Args:
            last_evaluated_key: DynamoDB LastEvaluatedKey dict
            ttl_seconds: Time-to-live in seconds (default 300 = 5 minutes)
            
        Returns:
            Base64-encoded string with embedded timestamp
        """
        # Add timestamp and TTL to token
        token_data = {
            **last_evaluated_key,
            'issued_at': int(time.time()),
            'ttl': ttl_seconds
        }
        
        json_str = json.dumps(token_data)
        encoded = base64.b64encode(json_str.encode('utf-8'))
        return encoded.decode('utf-8')
    
    @staticmethod
    def decode_pagination_token(token: str, max_age_seconds: int = DEFAULT_TOKEN_TTL_SECONDS) -> Optional[Dict]:
        """
        Decodes and validates base64 pagination token with TTL check.
        
        Args:
            token: Base64-encoded pagination token
            max_age_seconds: Maximum age in seconds (default 300 = 5 minutes)
            
        Returns:
            DynamoDB ExclusiveStartKey dict (without TTL metadata)
            
        Raises:
            ValueError: If token is expired, invalid base64, or invalid JSON
        """
        try:
            decoded = base64.b64decode(token.encode('utf-8'))
            token_data = json.loads(decoded.decode('utf-8'))
            
            # Check if token has TTL info and validate expiration
            if 'issued_at' in token_data:
                issued_at = token_data['issued_at']
                current_time = int(time.time())
                age = current_time - issued_at
                
                if age > max_age_seconds:
                    raise ValueError(
                        f"Pagination token expired. Tokens are valid for {max_age_seconds} seconds. "
                        f"Please restart pagination from the first page."
                    )
            
            # Remove TTL metadata and return only DynamoDB key parts
            db_key = {k: v for k, v in token_data.items() if k not in ['issued_at', 'ttl']}
            return db_key
            
        except (ValueError, json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid pagination token: {str(e)}")
    
    @staticmethod
    def validate_page_size(page_size: Optional[int]) -> int:
        """
        Validates and returns page size with default.
        
        Args:
            page_size: Requested page size
            
        Returns:
            Validated page size (default 50 if None)
            
        Raises:
            ValueError: If page_size is invalid
        """
        if page_size is None:
            return 50  # Default page size
        
        if not isinstance(page_size, int):
            raise ValueError("page_size must be an integer")
        
        if page_size < 1:
            raise ValueError("page_size must be at least 1")
        
        if page_size > 100:
            raise ValueError("page_size cannot exceed 100")
        
        return page_size
```

#### Updated DynamoDB Repository

Update `SessionRepositoryDynamo` to support pagination:

**Key Changes**:

1. **Query with Limit**: Use DynamoDB's `Limit` parameter
2. **ExclusiveStartKey**: Use decoded pagination token as starting point
3. **Return LastEvaluatedKey**: Encode and return for next page
4. **Maintain Ordering**: Ensure consistent sort order with ScanIndexForward

**Example Implementation Pattern**:

```python
def get_all_sessions_paginated(
    self, 
    page_size: int,
    last_evaluated_key: Optional[str] = None
) -> Tuple[List[Session], Optional[str]]:
    """
    Returns all sessions with pagination.
    """
    # Validate page size
    page_size = PaginationHelper.validate_page_size(page_size)
    
    # Decode pagination token
    exclusive_start_key = None
    if last_evaluated_key:
        exclusive_start_key = PaginationHelper.decode_pagination_token(last_evaluated_key)
    
    # Build query parameters
    query_params = {
        'TableName': self.table_name,
        'IndexName': 'GSI1',  # Global Secondary Index for all sessions
        'KeyConditionExpression': 'entity_type = :entity_type',
        'ExpressionAttributeValues': {
            ':entity_type': 'SESSION'
        },
        'ScanIndexForward': True,  # Sort by start_datetime ascending
        'Limit': page_size
    }
    
    if exclusive_start_key:
        query_params['ExclusiveStartKey'] = exclusive_start_key
    
    # Execute query
    response = self.dynamodb_client.query(**query_params)
    
    # Convert to entities
    sessions = [
        SessionDynamoDTO.from_dynamo(item).to_entity()
        for item in response.get('Items', [])
    ]
    
    # Encode next page token if more results exist
    next_token = None
    if 'LastEvaluatedKey' in response:
        next_token = PaginationHelper.encode_pagination_token(
            response['LastEvaluatedKey']
        )
    
    return sessions, next_token
```

**Similar Implementation for Other Paginated Methods**:
- `get_sessions_by_venue_paginated`: Query GSI with venue filter + pagination
- `get_sessions_by_day_paginated`: Query GSI with day filter + pagination
- `get_sessions_by_level_paginated`: Query GSI with level filter + pagination

**Note**: Existing non-paginated methods remain unchanged and continue to return all results.

#### Updated Mock Repository

Add new paginated methods to `SessionRepositoryMock`:

```python
# Existing methods remain unchanged
def get_all_sessions(self) -> List[Session]:
    """Returns all sessions."""
    return self.sessions

# New paginated method
def get_all_sessions_paginated(
    self, 
    page_size: int,
    last_evaluated_key: Optional[str] = None
) -> Tuple[List[Session], Optional[str]]:
    """
    Returns all sessions with simulated pagination.
    """
    # Validate page size
    page_size = PaginationHelper.validate_page_size(page_size)
    
    # Decode start index from token
    start_index = 0
    if last_evaluated_key:
        try:
            decoded = PaginationHelper.decode_pagination_token(last_evaluated_key)
            start_index = decoded.get('index', 0)
        except ValueError:
            start_index = 0
    
    # Slice results
    end_index = start_index + page_size
    page_sessions = self.sessions[start_index:end_index]
    
    # Generate next token if more results exist
    next_token = None
    if end_index < len(self.sessions):
        next_key = {'index': end_index}
        next_token = PaginationHelper.encode_pagination_token(next_key)
    
    return page_sessions, next_token
```

**Similar Implementation for Other Paginated Methods**:
- `get_sessions_by_venue_paginated`
- `get_sessions_by_day_paginated`
- `get_sessions_by_level_paginated`

### 3. Application Layer Updates

#### New Paginated Use Cases

Create new use cases for paginated endpoints:

**Example: GetAllSessionsPaginatedUsecase**

```python
from typing import Optional, Tuple, List

class GetAllSessionsPaginatedUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(
        self,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Retrieves all sessions with pagination.
        
        Args:
            page_size: Maximum number of sessions to return
            last_evaluated_key: Pagination token for next page
            
        Returns:
            Tuple of (sessions list, next_page_token)
        """
        return self.repo.get_all_sessions_paginated(page_size, last_evaluated_key)
```

**Similar New Use Cases**:
- `GetSessionsByVenuePaginatedUsecase`
- `GetSessionsByDayPaginatedUsecase`
- `GetSessionsByLevelPaginatedUsecase`

**Note**: Existing use cases remain unchanged.

#### New Paginated Controllers

Create new controllers for paginated endpoints:

**Example: GetAllSessionsPaginatedController**

```python
from src.shared.helpers.errors.controller_errors import WrongTypeParameter, MissingParameters

class GetAllSessionsPaginatedController:
    
    def __init__(self, usecase: GetAllSessionsPaginatedUsecase):
        self.usecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract pagination parameters from query string
            page_size = request.data.get('page_size')
            last_evaluated_key = request.data.get('last_evaluated_key')
            
            # page_size is required for paginated endpoints
            if page_size is None:
                raise MissingParameters('page_size')
            
            # Convert page_size to int
            try:
                page_size = int(page_size)
            except (ValueError, TypeError):
                raise WrongTypeParameter(
                    'page_size',
                    'int',
                    type(page_size).__name__
                )
            
            # Call use case with pagination
            sessions, next_token = self.usecase(
                page_size=page_size,
                last_evaluated_key=last_evaluated_key
            )
            
            # Create view model with pagination metadata
            viewmodel = GetAllSessionsPaginatedViewmodel(
                sessions=sessions,
                page_size=page_size,
                next_token=next_token
            )
            
            return OK(viewmodel.to_dict())
        
        except ValueError as err:
            # Pagination validation errors (including token expiration)
            return BadRequest(body=str(err))
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except WrongTypeParameter as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=str(err))
```

**Similar New Controllers**:
- `GetSessionsByVenuePaginatedController`
- `GetSessionsByDayPaginatedController`
- `GetSessionsByLevelPaginatedController`

**Note**: Existing controllers remain unchanged.

#### New Paginated View Models

Create new view models for paginated responses:

**Example: GetAllSessionsPaginatedViewmodel**

```python
from typing import List, Optional

class GetAllSessionsPaginatedViewmodel:
    
    def __init__(
        self,
        sessions: List[Session],
        page_size: int,
        next_token: Optional[str]
    ):
        self.sessions = sessions
        self.page_size = page_size
        self.next_token = next_token
    
    def to_dict(self) -> dict:
        """
        Converts view model to dictionary with pagination metadata.
        """
        response = {
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
            "count": len(self.sessions),
            "page_size": self.page_size,
            "has_more": self.next_token is not None
        }
        
        # Only include last_evaluated_key if there are more results
        if self.next_token:
            response["last_evaluated_key"] = self.next_token
        
        return response
```

**Similar New View Models**:
- `GetSessionsByVenuePaginatedViewmodel`
- `GetSessionsByDayPaginatedViewmodel`
- `GetSessionsByLevelPaginatedViewmodel`

**Note**: Existing view models remain unchanged.

## Data Models

### Request Format

**New Paginated Endpoints**:
- `GET /sessions/paginated` - Get all sessions with pagination
- `GET /sessions/by-venue/paginated` - Get sessions by venue with pagination
- `GET /sessions/by-day/paginated` - Get sessions by day with pagination
- `GET /sessions/by-level/paginated` - Get sessions by level with pagination

**Query Parameters**:
- `page_size` (required): Integer between 1-100
- `last_evaluated_key` (optional): Base64-encoded pagination token
- Additional filter parameters (venue_name, day, level_value) as needed

**Example Requests**:
```
GET /sessions/paginated?page_size=20
GET /sessions/paginated?page_size=20&last_evaluated_key=eyJQSyI6IlNFU1NJT04jMTIzIiwiU0siOiIyMDI1LTEyLTA0VDIxOjAwOjAwLjAwMFoifQ==
GET /sessions/by-venue/paginated?venue_name=Mandalay%20Bay&page_size=50
GET /sessions/by-day/paginated?day=Monday&page_size=30&last_evaluated_key=...
GET /sessions/by-level/paginated?level_value=300&page_size=25
```

**Note**: Existing endpoints (`/sessions`, `/sessions/by-venue`, etc.) remain unchanged and continue to return all results.

### Response Format

**With More Results**:
```json
{
  "sessions": [
    {
      "session_id": "1753651605588001kjXl",
      "short_id": "TNC301",
      "title": "Accelerate VMware Migration",
      "abstract": "This bootcamp...",
      "session_type": "Bootcamp",
      "venue_name": "Mandalay Bay",
      "venue_room": "Level 2 South | Breakers K",
      "start_datetime": "2025-12-04T21:00:00.000Z",
      "end_datetime": "2025-12-05T01:00:00.000Z",
      "day": "Thursday",
      "speakers": [{"displayName": "John Doe", "company": "AWS"}],
      "topics": ["AI", "ML"],
      "areas_of_interest": ["Training"],
      "level": "300 – Advanced",
      "level_value": 300,
      "features": ["Hands-on"],
      "seat_capacity": 126
    }
  ],
  "count": 20,
  "page_size": 20,
  "has_more": true,
  "last_evaluated_key": "eyJQSyI6IlNFU1NJT04jNDU2IiwiU0siOiIyMDI1LTEyLTA1VDA5OjAwOjAwLjAwMFoifQ=="
}
```

**Last Page (No More Results)**:
```json
{
  "sessions": [...],
  "count": 15,
  "page_size": 20,
  "has_more": false
}
```

### Pagination Token Format

**Internal Structure** (before base64 encoding):
```json
{
  "PK": "SESSION#123",
  "SK": "2025-12-04T21:00:00.000Z",
  "issued_at": 1737374400,
  "ttl": 300
}
```

**Fields**:
- `PK`: DynamoDB partition key
- `SK`: DynamoDB sort key
- `issued_at`: Unix timestamp when token was created
- `ttl`: Time-to-live in seconds (300 = 5 minutes)

**Encoded Token**:
```
eyJQSyI6IlNFU1NJT04jMTIzIiwiU0siOiIyMDI1LTEyLTA0VDIxOjAwOjAwLjAwMFoiLCJpc3N1ZWRfYXQiOjE3MzczNzQ0MDAsInR0bCI6MzAwfQ==
```

**Token Expiration**:
- Tokens expire after 5 minutes (configurable)
- Expired tokens return 400 error with clear message
- Client must restart pagination from first page if token expires

## Error Handling

### Pagination-Specific Errors

| Error Scenario | HTTP Status | Error Message |
|----------------|-------------|---------------|
| page_size < 1 | 400 | "page_size must be at least 1" |
| page_size > 100 | 400 | "page_size cannot exceed 100" |
| page_size not integer | 400 | "page_size must be an integer" |
| Invalid pagination token | 400 | "Invalid pagination token: [details]" |
| Malformed base64 | 400 | "Invalid pagination token format" |
| Expired pagination token | 400 | "Pagination token expired. Tokens are valid for 300 seconds. Please restart pagination from the first page." |

### Error Handling Strategy

1. **Validation in Helper**: PaginationHelper validates and raises ValueError
2. **Controller Catches**: Controller catches ValueError and returns 400
3. **Descriptive Messages**: Include specific reason for validation failure
4. **Backward Compatibility**: Missing pagination params = return all results

## Testing Strategy

### Unit Tests

**PaginationHelper Tests**:
- Test encode_pagination_token with various DynamoDB keys
- Test decode_pagination_token with valid and invalid tokens
- Test validate_page_size with valid, invalid, and edge cases
- Test error handling for malformed tokens

**Repository Tests**:
- Test pagination with page_size only
- Test pagination with both page_size and last_evaluated_key
- Test pagination returns correct next_token
- Test pagination with no more results (next_token is None)
- Test backward compatibility (no pagination params)

**Use Case Tests**:
- Test use cases pass pagination params correctly
- Test use cases return tuple (sessions, next_token)

**Controller Tests**:
- Test extraction of pagination query parameters
- Test validation of page_size (valid, invalid, missing)
- Test validation of last_evaluated_key (valid, invalid, missing)
- Test error responses for invalid pagination params

**View Model Tests**:
- Test to_dict() includes pagination metadata
- Test has_more is true when next_token exists
- Test has_more is false when next_token is None
- Test last_evaluated_key only included when has_more is true

### Integration Tests

**End-to-End Pagination**:
- Test retrieving multiple pages of results
- Test pagination maintains consistent ordering
- Test pagination with filters (venue, day, level)
- Test pagination token works across requests
- Test last page has no next_token

### Test Data

Create fixtures with:
- 150+ sessions for multi-page testing
- Sessions across different venues, days, levels
- Consistent timestamps for ordering verification

## Implementation Notes

### DynamoDB Considerations

1. **Global Secondary Index**: Ensure GSI exists for efficient queries
2. **Sort Key**: Use start_datetime as sort key for consistent ordering
3. **Limit Parameter**: DynamoDB Limit is approximate, may return fewer items
4. **LastEvaluatedKey**: Contains all key attributes (PK, SK, GSI keys)

### Performance Considerations

1. **Default Page Size**: 50 items balances performance and usability
2. **Maximum Page Size**: 100 items prevents excessive data transfer
3. **Token Encoding**: Base64 is lightweight and URL-safe
4. **Query Efficiency**: Pagination reduces DynamoDB read capacity usage

### Token TTL and Data Consistency

1. **TTL Duration**: 5 minutes (300 seconds) is the default
2. **Prevents Stale Pagination**: Expired tokens force clients to restart with fresh data
3. **Sync-Sessions Interaction**: If sync-sessions runs during pagination, tokens expire after 5 minutes, ensuring clients eventually get fresh data
4. **Configurable**: TTL can be adjusted via `DEFAULT_TOKEN_TTL_SECONDS` constant
5. **Stateless Design**: TTL is embedded in token, no server-side session storage needed

### Backward Compatibility

1. **New Endpoints**: Pagination is implemented as separate endpoints (e.g., `/sessions/paginated`)
2. **Existing Endpoints Unchanged**: All current endpoints (`/sessions`, `/sessions/by-venue`, etc.) remain unchanged
3. **No Breaking Changes**: Existing clients continue to work exactly as before
4. **Opt-In Pagination**: Clients choose to use paginated endpoints when needed
5. **Separate Code Paths**: New use cases, controllers, and view models keep code clean and maintainable

### Security Considerations

1. **Token Validation**: Validate base64 format before decoding
2. **Token Content**: Tokens contain only DynamoDB keys and timestamps, no sensitive data
3. **Input Validation**: Strict validation of page_size to prevent abuse
4. **Rate Limiting**: Consider API Gateway throttling for pagination endpoints
5. **TTL Protection**: Token expiration prevents long-lived pagination sessions



## Monitoring and Observability

### Metrics to Track

- Average page size requested
- Pagination token usage rate
- Error rate for invalid pagination params
- Query performance with pagination
- Number of pages per session

### CloudWatch Logs

- Log pagination parameters in requests
- Log pagination token generation
- Log validation errors with details
- Log performance metrics for paginated queries

## Summary

This design adds comprehensive pagination support to all session retrieval endpoints while maintaining backward compatibility and following Clean Architecture principles. The cursor-based approach using DynamoDB's native pagination provides efficient queries, and the base64-encoded tokens offer a clean API interface. All layers are updated systematically to support pagination, with proper validation, error handling, and testing strategies in place.
