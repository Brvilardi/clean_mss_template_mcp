# Design Document: Enhanced Session Search

## Overview

This design enhances the existing intelligent session search feature with two key improvements:

1. **Comprehensive DynamoDB Integration Tests**: Validates that GSI-based filtering (venue, day, level) works correctly against actual DynamoDB, ensuring the repository implementation properly leverages indexes and returns correctly filtered results.

2. **Speaker Filtering**: Adds the ability to search sessions by speaker name or company, enabling users to discover all sessions presented by specific individuals or organizations.

The design maintains consistency with existing search patterns, follows Clean Architecture principles, and ensures optimal performance by applying speaker filtering after GSI queries when combined with indexed filters.

## Architecture

### Component Updates

The enhancement touches these existing components:

1. **Repository Interface** (`ISessionRepository`): Add speaker parameter to `search_sessions` method
2. **Repository Implementations**: 
   - `SessionRepositoryDynamo`: Add speaker filtering logic
   - `SessionRepositoryMock`: Add speaker filtering logic
3. **Use Case** (`SearchSessionsUsecase`): Add speaker parameter validation
4. **Controller** (`SearchSessionsController`): Extract and validate speaker query parameter
5. **View Model** (`SearchSessionsViewmodel`): No changes needed (already handles session data)
6. **Presenter** (`SearchSessionsPresenter`): No changes needed (already extracts query params)

### Integration Test Strategy

New integration tests will be added to `tests/shared/infra/repositories/test_session_repository_dynamo.py` to validate:

- Venue filtering returns only matching sessions
- Day filtering returns only matching sessions
- Level filtering returns only matching sessions
- Combined filters work correctly
- GSI queries return results ordered by start_datetime
- Non-existent filter values return empty results

These tests will use `@pytest.mark.skip(reason="Needs dynamoDB")` decorator and require local DynamoDB or AWS connection.

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
    speaker: Optional[str] = None,  # NEW PARAMETER
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
        speaker: Optional[str] = None,  # NEW PARAMETER
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Search sessions with multiple filter criteria and pagination.
        
        Validates all inputs and delegates to repository.
        """
        # Existing validations for day, venue, level, page_size...
        
        # NEW: Validate speaker parameter
        if speaker is not None:
            if not isinstance(speaker, str) or len(speaker.strip()) == 0:
                raise EntityError("speaker")
        
        # Call repository with all parameters
        return self.repo.search_sessions(
            day=day,
            venue=venue,
            level=level,
            keywords=keywords,
            speaker=speaker,
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
            page_size = request.data.get('page_size', 50)
            last_evaluated_key = request.data.get('next_page_token')
            
            # NEW: Extract speaker parameter
            speaker = request.data.get('speaker')
            
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
    "speaker": Optional[str],       # NEW: "John Doe" or "AWS" (searches name and company)
    "page_size": int,               # 1-100, default 50
    "next_page_token": Optional[str] # Base64-encoded pagination token
}
```

## Speaker Filtering Implementation

### Algorithm

The speaker filter uses DynamoDB's `FilterExpression` with the `contains()` function to search within the nested speakers list structure. This is more efficient than fetching all data and filtering in Python.

```python
def _build_speaker_filter_expression(speaker_query: str):
    """
    Build DynamoDB filter expression for speaker search.
    
    Args:
        speaker_query: Search term (case-insensitive requires lowercase storage or scan)
        
    Returns:
        FilterExpression for DynamoDB query/scan
    """
    from boto3.dynamodb.conditions import Attr
    
    # Note: DynamoDB doesn't support case-insensitive contains natively
    # We'll need to store lowercase versions or use multiple conditions
    # For now, we'll use case-sensitive contains and document the limitation
    
    # Search in speakers list for displayName or company containing the query
    # This uses DynamoDB's ability to search within list items
    filter_expr = Attr('speakers').contains({'displayName': speaker_query})
    filter_expr = filter_expr | Attr('speakers').contains({'company': speaker_query})
    
    return filter_expr
```

**Note on Case Sensitivity**: DynamoDB's `contains()` function is case-sensitive. To achieve case-insensitive matching, we have two options:

1. **Store lowercase versions** (recommended): Add `speakers_lowercase` field during sync with lowercase displayName and company values
2. **Multiple filter conditions**: Generate filter expressions for common case variations (Original, UPPER, lower, Title Case)

For this implementation, we'll use approach #2 initially (multiple conditions) and can optimize to approach #1 in a future enhancement.

### Integration with Existing Search

Speaker filtering is applied using DynamoDB FilterExpression:

1. **Speaker only**: Scan with FilterExpression for speaker matching
2. **Speaker + indexed filter**: Query GSI with FilterExpression for speaker
3. **Speaker + keywords**: Query/Scan with speaker FilterExpression, then apply keyword filtering in application (keywords still need application-level filtering for relevance scoring)
4. **Speaker + indexed + keywords**: Query GSI with speaker FilterExpression, apply keyword filtering in application

This approach leverages DynamoDB's native filtering capabilities, reducing data transfer and improving performance compared to application-level filtering.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

Reviewing the prework analysis for redundancy:
- Properties 5.5, 5.6, 5.7 are redundant with 2.2, 2.3, 2.4 (testing requirements)
- Property 1.4 and 1.5 can be combined into a single "combined filters" property
- Properties 1.7 and 1.8 are edge cases that will be handled by generators

After reflection, we have 12 unique testable properties.

### Property 1: Venue filtering correctness
*For any* venue name and set of sessions, filtering by that venue should return only sessions where venue_name equals that venue.
**Validates: Requirements 1.1**

### Property 2: Day filtering correctness
*For any* day name and set of sessions, filtering by that day should return only sessions where day equals that day.
**Validates: Requirements 1.2**

### Property 3: Level filtering correctness
*For any* level value and set of sessions, filtering by that level should return only sessions where level_value equals that level.
**Validates: Requirements 1.3**

### Property 4: Combined filter correctness
*For any* combination of venue, day, and level filters, all returned sessions should match all provided filter criteria.
**Validates: Requirements 1.4, 1.5**

### Property 5: GSI ordering preservation
*For any* GSI query (venue, day, or level), the returned sessions should be ordered by start_datetime in ascending order.
**Validates: Requirements 1.6**

### Property 6: Speaker displayName matching
*For any* speaker name query and set of sessions, all returned sessions should have at least one speaker whose displayName contains that query string.
**Validates: Requirements 2.1**

### Property 7: Speaker case-insensitive matching
*For any* speaker name with different casings (e.g., "John Doe", "JOHN DOE", "john doe"), the search should return the same sessions.
**Validates: Requirements 2.2**

### Property 8: Speaker partial name matching
*For any* speaker's full name and any substring of that name, searching for the substring should return sessions containing that speaker.
**Validates: Requirements 2.3**

### Property 9: Speaker company matching
*For any* company name query and set of sessions, all returned sessions should have at least one speaker whose company contains that query string.
**Validates: Requirements 2.4**

### Property 10: Speaker combined with other filters
*For any* speaker query combined with other filters (day, venue, level, keywords), all returned sessions should match all provided criteria.
**Validates: Requirements 2.5**

### Property 11: Speaker searches both fields
*For any* search term that appears in either displayName or company of any speaker, that session should be included in results.
**Validates: Requirements 4.4**

### Property 12: Speaker checks all speakers
*For any* session with multiple speakers, if the search term matches any speaker (not just the first), that session should be included in results.
**Validates: Requirements 4.5**

### Property 13: Invalid speaker parameter rejection
*For any* invalid speaker parameter (empty string, whitespace-only), the search should raise EntityError.
**Validates: Requirements 3.4, 6.3**

## Error Handling

### New Validation Errors (400 Bad Request)

- Invalid speaker value (empty string or whitespace-only)

### Existing Error Handling

All existing error handling remains unchanged:
- Invalid day, venue, level, page_size → 400 Bad Request
- No results → 200 OK with empty array
- DynamoDB errors → 500 Internal Server Error

## Testing Strategy

### Integration Tests for DynamoDB (New)

Add to `tests/shared/infra/repositories/test_session_repository_dynamo.py`:

```python
@pytest.mark.skip(reason="Needs dynamoDB")
def test_get_sessions_by_venue_filters_correctly(self):
    """Test venue filtering returns only matching sessions"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Get sessions for a known venue
    sessions = repo.get_sessions_by_venue("Venetian")
    
    # Verify all sessions have the correct venue
    for session in sessions:
        assert session.venue_name == "Venetian"

@pytest.mark.skip(reason="Needs dynamoDB")
def test_get_sessions_by_day_filters_correctly(self):
    """Test day filtering returns only matching sessions"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Get sessions for a known day
    sessions = repo.get_sessions_by_day("Monday")
    
    # Verify all sessions have the correct day
    for session in sessions:
        assert session.day == "Monday"

@pytest.mark.skip(reason="Needs dynamoDB")
def test_get_sessions_by_level_filters_correctly(self):
    """Test level filtering returns only matching sessions"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Get sessions for a known level
    sessions = repo.get_sessions_by_level(300)
    
    # Verify all sessions have the correct level
    for session in sessions:
        assert session.level_value == 300

@pytest.mark.skip(reason="Needs dynamoDB")
def test_search_sessions_combined_filters(self):
    """Test combined venue and day filters"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Search with combined filters
    sessions, _ = repo.search_sessions(venue="Venetian", day="Monday")
    
    # Verify all sessions match both criteria
    for session in sessions:
        assert session.venue_name == "Venetian"
        assert session.day == "Monday"

@pytest.mark.skip(reason="Needs dynamoDB")
def test_gsi_query_ordering(self):
    """Test GSI queries return results ordered by start_datetime"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Query a GSI
    sessions = repo.get_sessions_by_venue("Venetian")
    
    # Verify ordering
    for i in range(len(sessions) - 1):
        assert sessions[i].start_datetime <= sessions[i + 1].start_datetime

@pytest.mark.skip(reason="Needs dynamoDB")
def test_search_sessions_with_speaker_filter(self):
    """Test speaker filtering in DynamoDB repository"""
    os.environ["STAGE"] = "TEST"
    repo = SessionRepositoryDynamo()
    
    # Search with speaker filter
    sessions, _ = repo.search_sessions(speaker="Werner")
    
    # Verify all sessions have a matching speaker
    for session in sessions:
        found_match = False
        for speaker in session.speakers:
            if "werner" in speaker.get('displayName', '').lower():
                found_match = True
                break
            if "werner" in speaker.get('company', '').lower():
                found_match = True
                break
        assert found_match
```

### Unit Tests for Speaker Filtering (New)

Add to `tests/modules/search_sessions/app/test_search_sessions_usecase.py`:

```python
def test_search_sessions_invalid_speaker_empty_string(self):
    """Test invalid speaker (empty string) raises EntityError"""
    repo = SessionRepositoryMock()
    usecase = SearchSessionsUsecase(repo)
    
    with pytest.raises(EntityError):
        usecase(speaker="")
    
    with pytest.raises(EntityError):
        usecase(speaker="   ")

def test_search_sessions_valid_speaker(self):
    """Test valid speaker parameter"""
    repo = SessionRepositoryMock()
    usecase = SearchSessionsUsecase(repo)
    
    sessions, next_token = usecase(speaker="John Doe")
    assert isinstance(sessions, list)

def test_search_sessions_speaker_with_other_filters(self):
    """Test speaker combined with other filters"""
    repo = SessionRepositoryMock()
    usecase = SearchSessionsUsecase(repo)
    
    sessions, next_token = usecase(
        speaker="John",
        day="Monday",
        venue="Venetian",
        level=300
    )
    assert isinstance(sessions, list)
```

Add to `tests/modules/search_sessions/app/test_search_sessions_controller.py`:

```python
def test_search_sessions_controller_with_speaker(self):
    """Test controller with speaker parameter"""
    repo = SessionRepositoryMock()
    usecase = SearchSessionsUsecase(repo)
    controller = SearchSessionsController(usecase)
    
    request = HttpRequest(body={
        'speaker': 'John Doe'
    })
    
    response = controller(request=request)
    
    assert response.status_code == 200
    assert 'sessions' in response.body

def test_search_sessions_controller_invalid_speaker(self):
    """Test controller with invalid speaker returns 400"""
    repo = SessionRepositoryMock()
    usecase = SearchSessionsUsecase(repo)
    controller = SearchSessionsController(usecase)
    
    request = HttpRequest(body={
        'speaker': ''
    })
    
    response = controller(request=request)
    
    assert response.status_code == 400
```

Add to `tests/shared/infra/repositories/test_session_repository_mock.py`:

```python
def test_search_sessions_by_speaker_displayname(self):
    """Test speaker filtering by displayName"""
    repo = SessionRepositoryMock()
    
    # Search for a speaker by name
    sessions, _ = repo.search_sessions(speaker="John")
    
    # Verify all sessions have a matching speaker
    for session in sessions:
        found_match = False
        for speaker in session.speakers:
            if "john" in speaker.get('displayName', '').lower():
                found_match = True
                break
        assert found_match

def test_search_sessions_by_speaker_company(self):
    """Test speaker filtering by company"""
    repo = SessionRepositoryMock()
    
    # Search for a speaker by company
    sessions, _ = repo.search_sessions(speaker="AWS")
    
    # Verify all sessions have a matching speaker
    for session in sessions:
        found_match = False
        for speaker in session.speakers:
            if "aws" in speaker.get('company', '').lower():
                found_match = True
                break
        assert found_match

def test_search_sessions_speaker_case_insensitive(self):
    """Test speaker search is case-insensitive"""
    repo = SessionRepositoryMock()
    
    # Search with different casings
    sessions1, _ = repo.search_sessions(speaker="john")
    sessions2, _ = repo.search_sessions(speaker="JOHN")
    sessions3, _ = repo.search_sessions(speaker="John")
    
    # Should return same results
    assert len(sessions1) == len(sessions2) == len(sessions3)

def test_search_sessions_speaker_partial_match(self):
    """Test speaker search with partial name"""
    repo = SessionRepositoryMock()
    
    # Search with partial name
    sessions, _ = repo.search_sessions(speaker="Doe")
    
    # Verify results contain speakers with "Doe" in name
    for session in sessions:
        found_match = False
        for speaker in session.speakers:
            if "doe" in speaker.get('displayName', '').lower():
                found_match = True
                break
        assert found_match
```

### Property-Based Tests (New)

Add property-based tests for the new correctness properties using Hypothesis:

```python
# Feature: enhanced-session-search, Property 6: Speaker displayName matching
# Feature: enhanced-session-search, Property 7: Speaker case-insensitive matching
# Feature: enhanced-session-search, Property 8: Speaker partial name matching
# Feature: enhanced-session-search, Property 9: Speaker company matching
# Feature: enhanced-session-search, Property 10: Speaker combined with other filters
# Feature: enhanced-session-search, Property 11: Speaker searches both fields
# Feature: enhanced-session-search, Property 12: Speaker checks all speakers
# Feature: enhanced-session-search, Property 13: Invalid speaker parameter rejection
```

## API Endpoint Updates

### Updated Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| day | string | No | - | Filter by day (e.g., "Monday") |
| venue | string | No | - | Filter by venue name |
| level | integer | No | - | Filter by level (100, 200, 300, 400) |
| keywords | string | No | - | Space-separated keywords |
| **speaker** | **string** | **No** | **-** | **Filter by speaker name or company (NEW)** |
| page_size | integer | No | 50 | Results per page (1-100) |
| next_page_token | string | No | - | Pagination token |

### Example Requests with Speaker Filter

```bash
# Search by speaker name
GET /sessions/search?speaker=Werner%20Vogels

# Search by company
GET /sessions/search?speaker=AWS

# Search by partial name
GET /sessions/search?speaker=John

# Combine speaker with other filters
GET /sessions/search?speaker=Werner&day=Monday&level=400

# Combine speaker with keywords
GET /sessions/search?speaker=AWS&keywords=serverless
```

## Performance Considerations

### Speaker Filter Performance

- **Speaker only**: Scan with FilterExpression (DynamoDB filters server-side, reducing data transfer)
- **Speaker + indexed filter**: GSI query with FilterExpression (optimal - indexed query + server-side filtering)
- **Optimization**: FilterExpression evaluated by DynamoDB before returning results, reducing network overhead
- **Trade-off**: No GSI for speakers avoids index maintenance cost and nested structure complexity
- **Case-insensitive cost**: Multiple filter conditions increase expression complexity but still more efficient than client-side filtering

### Expected Performance

- Speaker-only search: 150-400ms for ~5,000 sessions (FilterExpression reduces data transfer)
- Speaker + indexed filter: 80-250ms (GSI + FilterExpression is optimal)
- Speaker + keywords: 250-500ms (speaker filtered by DynamoDB, keywords in application)

## Implementation Notes

### Repository Implementation Pattern

- **SessionRepositoryDynamo**: Uses DynamoDB FilterExpression with `contains()` for speaker matching
- **SessionRepositoryMock**: Uses Python filtering logic to simulate DynamoDB behavior for testing

Both implementations ensure case-insensitive matching, but the approach differs:
- DynamoDB: Multiple filter conditions for case variations
- Mock: Python `.lower()` comparison

### Backward Compatibility

The speaker parameter is optional, so existing API consumers will continue to work without changes. The default value of `None` means "no speaker filter applied".

## Future Enhancements

1. **Speaker GSI**: If speaker searches become frequent, consider adding a GSI with speaker names (requires denormalization)
2. **Speaker Autocomplete**: Add endpoint to suggest speaker names as user types
3. **Speaker Profiles**: Link to speaker profile pages with all their sessions
4. **Advanced Speaker Search**: Support "AND" logic for multiple speakers, exact name matching
