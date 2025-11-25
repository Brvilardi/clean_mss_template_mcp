# Design Document: Session Type Filter

## Overview

This design adds session type filtering capability to the existing intelligent session search feature. Unlike the speaker filter which requires searching nested list structures, the session_type filter is simpler since it operates on a top-level string field in DynamoDB.

The implementation follows the same patterns established by the enhanced-session-search feature, maintaining consistency across the codebase while leveraging DynamoDB's FilterExpression for efficient server-side filtering.

## Architecture

### Component Updates

The enhancement touches these existing components:

1. **Repository Interface** (`ISessionRepository`): Add session_type parameter to `search_sessions` method
2. **Repository Implementations**: 
   - `SessionRepositoryDynamo`: Add session_type filtering logic using FilterExpression
   - `SessionRepositoryMock`: Add session_type filtering logic
3. **Use Case** (`SearchSessionsUsecase`): Add session_type parameter validation
4. **Controller** (`SearchSessionsController`): Extract and validate session_type query parameter
5. **View Model** (`SearchSessionsViewmodel`): No changes needed (already handles session data)
6. **Presenter** (`SearchSessionsPresenter`): No changes needed (already extracts query params)

## Components and Interfaces

### Updated Repository Interface

```python
# In src/shared/domain/repositories/session_repository_interface.py

def search_sessions(
    self,
    day: Optional[str] = None,
    venue: Optional[str] = None,
    level: Optional[int] = None,
    keywords: Optional[str] = None,
    speaker: Optional[str] = None,
    session_type: Optional[str] = None,  # NEW PARAMETER
    page_size: int = 50,
    last_evaluated_key: Optional[str] = None
) -> Tuple[List[Session], Optional[str]]:
    """
    Search sessions with multiple filter criteria and pagination.
    
    Args:
        day: Filter by day (e.g., "Monday", "Tuesday")
        venue: Filter by venue name
        level: Filter by level value (100, 200, 300, 400)
        keywords: Space-separated keywords to search in title, abstract, topics, areas
        speaker: Filter by speaker name or company (case-insensitive, partial match)
        session_type: Filter by session type (case-insensitive, partial match)
        page_size: Maximum results per page (1-100, default 50)
        last_evaluated_key: Pagination token from previous request
        
    Returns:
        Tuple of (sessions list, next_page_token)
        
    Raises:
        ValueError: If parameters are invalid
    """
    pass
```

### Updated Use Case

```python
# In src/modules/search_sessions/app/search_sessions_usecase.py

class SearchSessionsUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(
        self,
        day: Optional[str] = None,
        venue: Optional[str] = None,
        level: Optional[int] = None,
        keywords: Optional[str] = None,
        speaker: Optional[str] = None,
        session_type: Optional[str] = None,  # NEW PARAMETER
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Search sessions with multiple filter criteria and pagination.
        
        Validates all inputs and delegates to repository.
        """
        # Existing validations for day, venue, level, speaker, page_size...
        
        # NEW: Validate session_type parameter
        if session_type is not None:
            if not isinstance(session_type, str) or len(session_type.strip()) == 0:
                raise EntityError("session_type")
        
        # Call repository with all parameters
        return self.repo.search_sessions(
            day=day,
            venue=venue,
            level=level,
            keywords=keywords,
            speaker=speaker,
            session_type=session_type,
            page_size=page_size,
            last_evaluated_key=last_evaluated_key
        )
```

### Updated Controller

```python
# In src/modules/search_sessions/app/search_sessions_controller.py

class SearchSessionsController:
    
    def __init__(self, usecase: SearchSessionsUsecase):
        self.usecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract existing parameters...
            day = request.data.get('day')
            venue = request.data.get('venue')
            level = request.data.get('level')
            keywords = request.data.get('keywords')
            speaker = request.data.get('speaker')
            page_size = request.data.get('page_size', 50)
            last_evaluated_key = request.data.get('next_page_token')
            
            # NEW: Extract session_type parameter
            session_type = request.data.get('session_type')
            
            # Convert level to int if provided
            if level is not None:
                level = int(level)
            
            # Convert page_size to int
            page_size = int(page_size)
            
            # Call use case
            sessions, next_token = self.usecase(
                day=day,
                venue=venue,
                level=level,
                keywords=keywords,
                speaker=speaker,
                session_type=session_type,
                page_size=page_size,
                last_evaluated_key=last_evaluated_key
            )
            
            # Create view model and return
            viewmodel = SearchSessionsViewmodel(
                sessions=sessions,
                next_page_token=next_token,
                total_results=len(sessions)
            )
            return OK(viewmodel.to_dict())
        
        except EntityError as err:
            return BadRequest(body=err.message)
        except ValueError as err:
            return BadRequest(body=str(err))
        except Exception as err:
            return InternalServerError(body=str(err))
```

## Data Models

### Updated Search Request Model

```python
{
    "day": Optional[str],           # "Monday", "Tuesday", etc.
    "venue": Optional[str],         # "Venetian", "Mandalay Bay", etc.
    "level": Optional[int],         # 100, 200, 300, 400
    "keywords": Optional[str],      # "security machine learning"
    "speaker": Optional[str],       # "John Doe" or "AWS"
    "session_type": Optional[str],  # NEW: "Breakout Session", "Workshop", etc.
    "page_size": int,               # 1-100, default 50
    "next_page_token": Optional[str] # Base64-encoded pagination token
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

Reviewing the prework analysis for redundancy:
- Properties from 3.3, 3.4, 3.5, 5.2, 5.3, 5.5 are redundant with properties 1.1-1.4 and 2.4-2.5
- Edge cases 1.5 and 5.4 will be handled by property test generators

After reflection, we have 5 unique testable properties.

### Property 1: Session type exact matching
*For any* session_type value and set of sessions, filtering by that session_type should return only sessions where session_type equals that value (case-insensitive).
**Validates: Requirements 1.1, 1.2**

### Property 2: Session type partial matching
*For any* session's session_type and any substring of that session_type, searching for the substring should return sessions with that type.
**Validates: Requirements 1.3**

### Property 3: Session type combined with other filters
*For any* session_type query combined with other filters (day, venue, level, keywords, speaker), all returned sessions should match all provided criteria.
**Validates: Requirements 1.4**

### Property 4: Invalid session_type parameter rejection
*For any* invalid session_type parameter (empty string, whitespace-only), the search should raise EntityError.
**Validates: Requirements 2.4, 2.5**

### Property 5: Session type case-insensitive matching
*For any* session_type with different casings (e.g., "Workshop", "WORKSHOP", "workshop"), the search should return the same sessions.
**Validates: Requirements 1.2**

## Session Type Filtering Implementation

### Algorithm

The session_type filter uses DynamoDB's `FilterExpression` with the `contains()` function for case-insensitive partial matching. Since session_type is a simple string field (not nested), this is more straightforward than the speaker filter.

```python
def _build_session_type_filter_expression(session_type_query: str):
    """
    Build DynamoDB filter expression for session_type search.
    
    Args:
        session_type_query: Search term (case-insensitive)
        
    Returns:
        FilterExpression for DynamoDB query/scan
    """
    from boto3.dynamodb.conditions import Attr
    
    # DynamoDB contains() is case-sensitive, so we need multiple conditions
    # for case-insensitive matching
    query_lower = session_type_query.lower()
    query_upper = session_type_query.upper()
    query_title = session_type_query.title()
    
    # Create filter expression with multiple case variations
    filter_expr = Attr('session_type').contains(session_type_query)
    
    if query_lower != session_type_query:
        filter_expr = filter_expr | Attr('session_type').contains(query_lower)
    
    if query_upper != session_type_query:
        filter_expr = filter_expr | Attr('session_type').contains(query_upper)
    
    if query_title != session_type_query:
        filter_expr = filter_expr | Attr('session_type').contains(query_title)
    
    return filter_expr
```

### Integration with Existing Search

Session type filtering is applied using DynamoDB FilterExpression:

1. **Session type only**: Scan with FilterExpression for session_type matching
2. **Session type + indexed filter**: Query GSI with FilterExpression for session_type
3. **Session type + keywords**: Query/Scan with session_type FilterExpression, then apply keyword filtering in application
4. **Session type + indexed + keywords**: Query GSI with session_type FilterExpression, apply keyword filtering in application

This approach leverages DynamoDB's native filtering capabilities, reducing data transfer and improving performance.

## Error Handling

### New Validation Errors (400 Bad Request)

- Invalid session_type value (empty string or whitespace-only)

### Existing Error Handling

All existing error handling remains unchanged:
- Invalid day, venue, level, speaker, page_size → 400 Bad Request
- No results → 200 OK with empty array
- DynamoDB errors → 500 Internal Server Error

## Testing Strategy

### Unit Tests for Session Type Filtering

The testing strategy follows the established patterns from enhanced-session-search:

1. **Repository Mock Tests**: Test session_type filtering logic in SessionRepositoryMock
2. **Repository DynamoDB Tests**: Integration tests with actual DynamoDB (marked with `@pytest.mark.skip`)
3. **Use Case Tests**: Test session_type parameter validation
4. **Controller Tests**: Test session_type parameter extraction and error handling
5. **Property-Based Tests**: Test correctness properties using Hypothesis

### Property-Based Tests

Property-based tests will be written using Hypothesis to validate the correctness properties:

- Property 1: Session type exact matching
- Property 2: Session type partial matching
- Property 3: Session type combined with other filters
- Property 4: Invalid session_type parameter rejection
- Property 5: Session type case-insensitive matching

Each property test will run a minimum of 100 iterations to ensure comprehensive coverage.

### Test Organization

Tests will be added to existing test files:
- `tests/shared/infra/repositories/test_session_repository_mock.py`
- `tests/shared/infra/repositories/test_session_repository_dynamo.py`
- `tests/modules/search_sessions/app/test_search_sessions_usecase.py`
- `tests/modules/search_sessions/app/test_search_sessions_controller.py`

## API Endpoint Updates

### Updated Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| day | string | No | - | Filter by day (e.g., "Monday") |
| venue | string | No | - | Filter by venue name |
| level | integer | No | - | Filter by level (100, 200, 300, 400) |
| keywords | string | No | - | Space-separated keywords |
| speaker | string | No | - | Filter by speaker name or company |
| **session_type** | **string** | **No** | **-** | **Filter by session type (NEW)** |
| page_size | integer | No | 50 | Results per page (1-100) |
| next_page_token | string | No | - | Pagination token |

### Example Requests with Session Type Filter

```bash
# Search by session type
GET /sessions/search?session_type=Workshop

# Search by partial session type
GET /sessions/search?session_type=Break

# Combine session_type with other filters
GET /sessions/search?session_type=Workshop&day=Monday&level=300

# Combine session_type with keywords
GET /sessions/search?session_type=Breakout&keywords=serverless
```

## Performance Considerations

### Session Type Filter Performance

- **Session type only**: Scan with FilterExpression (DynamoDB filters server-side)
- **Session type + indexed filter**: GSI query with FilterExpression (optimal)
- **Optimization**: FilterExpression evaluated by DynamoDB before returning results
- **Advantage over speaker filter**: Simpler since session_type is a top-level string field, not nested

### Expected Performance

- Session type-only search: 100-300ms for ~5,000 sessions
- Session type + indexed filter: 50-200ms (GSI + FilterExpression is optimal)
- Session type + keywords: 200-400ms (session_type filtered by DynamoDB, keywords in application)

## Implementation Notes

### Repository Implementation Pattern

- **SessionRepositoryDynamo**: Uses DynamoDB FilterExpression with `contains()` for session_type matching
- **SessionRepositoryMock**: Uses Python filtering logic to simulate DynamoDB behavior

Both implementations ensure case-insensitive partial matching.

### Backward Compatibility

The session_type parameter is optional, so existing API consumers will continue to work without changes. The default value of `None` means "no session_type filter applied".

## Future Enhancements

1. **Session Type GSI**: If session_type searches become frequent, consider adding a GSI (requires evaluation of query patterns)
2. **Session Type Enumeration**: Add endpoint to list all available session types
3. **Session Type Statistics**: Show session count by type in search results
