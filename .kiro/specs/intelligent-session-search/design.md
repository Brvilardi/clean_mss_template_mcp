# Design Document: Intelligent Session Search

## Overview

The intelligent session search feature provides a high-performance, flexible search capability for re:Invent sessions. It combines multiple filter criteria (day, venue, level, keywords) with pagination support, enabling efficient discovery of relevant sessions through a single API endpoint.

The design prioritizes performance by leveraging DynamoDB Global Secondary Indexes (GSIs) for indexed filters and implementing smart query strategies that minimize data transfer and processing time.

## Architecture

### High-Level Flow

```
Client Request → API Gateway → Lambda (Presenter)
                                    ↓
                              Controller (validates input)
                                    ↓
                              Use Case (business logic)
                                    ↓
                              Repository (DynamoDB queries)
                                    ↓
                              View Model (format response)
                                    ↓
                              HTTP Response
```

### Component Responsibilities

1. **Repository Layer**: Executes optimized DynamoDB queries using GSIs when possible
2. **Use Case Layer**: Validates search criteria and orchestrates repository calls
3. **Controller Layer**: Handles HTTP request/response and error mapping
4. **View Model Layer**: Formats search results with pagination metadata
5. **Presenter Layer**: Lambda handler integration

## Components and Interfaces

### Repository Interface Extension

Add to `ISessionRepository`:

```python
def search_sessions(
    self,
    day: Optional[str] = None,
    venue: Optional[str] = None,
    level: Optional[int] = None,
    keywords: Optional[str] = None,
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
        page_size: Maximum results per page (1-100, default 50)
        last_evaluated_key: Pagination token from previous request
        
    Returns:
        Tuple of (sessions list, next_page_token)
        
    Raises:
        ValueError: If parameters are invalid
    """
    pass
```

### Use Case

```python
class SearchSessionsUsecase:
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(
        self,
        day: Optional[str] = None,
        venue: Optional[str] = None,
        level: Optional[int] = None,
        keywords: Optional[str] = None,
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        # Validate inputs
        # Call repository
        # Return results
        pass
```

### Controller

```python
class SearchSessionsController:
    def __init__(self, usecase: SearchSessionsUsecase):
        self.usecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        # Extract query parameters
        # Validate required parameters
        # Call use case
        # Return formatted response
        pass
```

### View Model

```python
class SearchSessionsViewmodel:
    def __init__(
        self,
        sessions: List[Session],
        next_page_token: Optional[str],
        total_results: int
    ):
        self.sessions = sessions
        self.next_page_token = next_page_token
        self.total_results = total_results
    
    def to_dict(self) -> dict:
        return {
            'sessions': [self._session_to_dict(s) for s in self.sessions],
            'pagination': {
                'page_size': len(self.sessions),
                'next_page_token': self.next_page_token
            },
            'message': 'search completed successfully'
        }
```

## Data Models

### Search Request Model

```python
{
    "day": Optional[str],           # "Monday", "Tuesday", etc.
    "venue": Optional[str],         # "Venetian", "Mandalay Bay", etc.
    "level": Optional[int],         # 100, 200, 300, 400
    "keywords": Optional[str],      # "security machine learning"
    "page_size": int,               # 1-100, default 50
    "next_page_token": Optional[str] # Base64-encoded pagination token
}
```

### Search Response Model

```python
{
    "sessions": [
        {
            "session_id": str,
            "short_id": str,
            "title": str,
            "abstract": str,
            "session_type": str,
            "venue_name": str,
            "venue_room": str,
            "start_datetime": str,
            "end_datetime": str,
            "day": str,
            "speakers": List[Dict],
            "topics": List[str],
            "areas_of_interest": List[str],
            "level": str,
            "level_value": int,
            "features": List[str],
            "seat_capacity": int
        }
    ],
    "pagination": {
        "page_size": int,
        "next_page_token": Optional[str]
    },
    "message": str
}
```

## Query Strategy and Performance Optimization

### Filter Priority and Index Selection

The repository implementation uses this decision tree for optimal performance:

1. **Single Indexed Filter**: Use corresponding GSI
   - Day only → GSI-Day
   - Venue only → GSI-Venue  
   - Level only → GSI-Level

2. **Multiple Indexed Filters**: Select most selective index
   - Priority: Level > Venue > Day (based on typical cardinality)
   - Query selected index, filter remaining criteria in application

3. **Keywords Only**: Scan with entity filter, apply keyword matching

4. **Indexed + Keywords**: Query index first, then filter by keywords

### Keyword Search Implementation

Keywords are searched across multiple fields with relevance scoring:

```python
def calculate_relevance_score(session: Session, keywords: List[str]) -> int:
    """
    Calculate relevance score for ranking.
    Higher score = more relevant.
    """
    score = 0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Title matches (highest priority)
        if keyword_lower in session.title.lower():
            score += 10
        
        # Abstract matches
        if keyword_lower in session.abstract.lower():
            score += 5
        
        # Topic matches
        for topic in session.topics:
            if keyword_lower in topic.lower():
                score += 3
                break
        
        # Area of interest matches
        for area in session.areas_of_interest:
            if keyword_lower in area.lower():
                score += 2
                break
    
    return score
```

### Pagination Strategy

- Use DynamoDB's native pagination (LastEvaluatedKey)
- Encode/decode pagination tokens using base64
- Apply keyword filtering after pagination to maintain consistent page sizes
- For keyword searches, may need to fetch multiple pages from DynamoDB to fill requested page_size

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

Before defining properties, let's identify and eliminate redundancy:

- Properties 2.2-2.5 are redundant with 2.1 (all test keyword search in different fields)
- Property 5.4 is redundant with 5.2 (both test ascending date order)
- Property 7.5 is redundant with 1.4 (both test invalid input handling)

After reflection, we have 13 unique testable properties.

### Property 1: Combined filter matching
*For any* combination of day, venue, level, and keywords filters, all returned sessions should match all provided filter criteria.
**Validates: Requirements 1.1**

### Property 2: Partial filter matching
*For any* subset of available filters (day, venue, level, keywords), all returned sessions should match only the provided filters and ignore unprovided filters.
**Validates: Requirements 1.2**

### Property 3: Invalid filter rejection
*For any* invalid filter value (invalid day name, non-existent venue, invalid level value), the search should return a 400 error with descriptive message.
**Validates: Requirements 1.4**

### Property 4: Keyword field coverage
*For any* keyword, if it appears in a session's title, abstract, topics, or areas_of_interest, that session should be included in search results.
**Validates: Requirements 2.1**

### Property 5: Case-insensitive keyword matching
*For any* keyword with different casing (e.g., "Security", "SECURITY", "security"), the search should return the same results.
**Validates: Requirements 2.6**

### Property 6: Multiple keyword OR logic
*For any* multi-word keyword string, sessions matching any of the individual keywords should be included in results (OR logic, not AND).
**Validates: Requirements 2.7**

### Property 7: Page size limit
*For any* valid page_size value, the number of returned sessions should not exceed that value.
**Validates: Requirements 3.2**

### Property 8: Next page token presence
*For any* search where total results exceed page_size, the response should include a non-null next_page_token.
**Validates: Requirements 3.3**

### Property 9: Pagination continuation
*For any* valid next_page_token, using it should return the next set of results without duplicates from the previous page.
**Validates: Requirements 3.4**

### Property 10: Final page token absence
*For any* search where the current page contains the last results, the next_page_token should be null.
**Validates: Requirements 3.5**

### Property 11: Keyword relevance ordering
*For any* keyword search, sessions with keyword matches in title should appear before sessions with matches only in abstract, which should appear before sessions with matches only in topics/areas.
**Validates: Requirements 5.1**

### Property 12: Default datetime ordering
*For any* search without keywords, results should be ordered by start_datetime in ascending order (earlier sessions first).
**Validates: Requirements 5.2**

### Property 13: Relevance tie-breaking
*For any* two sessions with equal relevance scores in a keyword search, the session with earlier start_datetime should appear first.
**Validates: Requirements 5.3**

## Error Handling

### Validation Errors (400 Bad Request)

- Invalid day value (not a valid day name)
- Invalid venue value (empty string)
- Invalid level value (not in [100, 200, 300, 400])
- Invalid page_size (< 1 or > 100)
- Invalid pagination token (malformed or expired)

### Not Found (200 OK with empty results)

- No sessions match the provided criteria
- Return empty array with appropriate message

### Internal Errors (500 Internal Server Error)

- DynamoDB connection failures
- Unexpected exceptions during query execution

## Testing Strategy

### Unit Testing

Unit tests will cover specific examples and edge cases:

- Empty filter search returns all sessions
- Single filter searches (day only, venue only, level only, keywords only)
- Invalid parameter handling
- Empty result sets
- Default page_size behavior (50)
- Maximum page_size enforcement (100)
- Endpoint accepts GET requests
- Response structure validation

### Property-Based Testing

Property-based tests will verify universal properties across many inputs:

- Use **Hypothesis** library for Python property-based testing
- Configure each property test to run minimum 100 iterations
- Each property test must be tagged with format: `# Feature: intelligent-session-search, Property {number}: {property_text}`
- Generate random combinations of filters and verify matching logic
- Generate random keywords and verify field coverage
- Generate random page sizes and verify limits
- Test pagination token continuity across multiple pages
- Verify relevance scoring and ordering logic

### Integration Testing

- Test with real DynamoDB Local instance
- Verify GSI query performance
- Test pagination with large datasets
- Measure query execution time (< 500ms target)

## API Endpoint Specification

### Endpoint

```
GET /sessions/search
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| day | string | No | - | Filter by day (e.g., "Monday") |
| venue | string | No | - | Filter by venue name |
| level | integer | No | - | Filter by level (100, 200, 300, 400) |
| keywords | string | No | - | Space-separated keywords |
| page_size | integer | No | 50 | Results per page (1-100) |
| next_page_token | string | No | - | Pagination token |

### Response Codes

- **200 OK**: Search completed successfully (even if no results)
- **400 Bad Request**: Invalid parameters
- **500 Internal Server Error**: Server error

### Example Requests

```bash
# Search by keyword
GET /sessions/search?keywords=security

# Search by day and venue
GET /sessions/search?day=Monday&venue=Venetian

# Search with pagination
GET /sessions/search?keywords=machine%20learning&page_size=20

# Next page
GET /sessions/search?keywords=security&next_page_token=eyJQSyI6...
```

### Example Response

```json
{
  "sessions": [
    {
      "session_id": "abc123",
      "short_id": "SEC301",
      "title": "Advanced Security Practices",
      "abstract": "Learn about security...",
      "session_type": "Breakout Session",
      "venue_name": "Venetian",
      "venue_room": "Level 2, Marcello 4405",
      "start_datetime": "2025-12-02T14:00:00.000Z",
      "end_datetime": "2025-12-02T15:00:00.000Z",
      "day": "Monday",
      "speakers": [
        {
          "displayName": "John Doe",
          "company": "AWS"
        }
      ],
      "topics": ["Security", "Best Practices"],
      "areas_of_interest": ["Security, Identity, & Compliance"],
      "level": "Advanced",
      "level_value": 300,
      "features": ["Live Q&A"],
      "seat_capacity": 500
    }
  ],
  "pagination": {
    "page_size": 1,
    "next_page_token": "eyJQSyI6IlNFU1NJT04jYWJjMTIzIn0="
  },
  "message": "search completed successfully"
}
```

## Implementation Notes

### DynamoDB Query Optimization

1. **Index Selection Logic**:
   ```python
   if level:
       use GSI-Level  # Most selective (4-5 distinct values)
   elif venue:
       use GSI-Venue  # Medium selectivity (~10-15 venues)
   elif day:
       use GSI-Day    # Least selective (5-7 days)
   else:
       use Scan with entity filter
   ```

2. **Keyword Filtering**:
   - Apply after DynamoDB query to minimize data transfer
   - Use Python's `in` operator for substring matching (case-insensitive)
   - Calculate relevance scores for ranking

3. **Pagination Handling**:
   - For indexed queries: use DynamoDB's native pagination
   - For keyword searches: may need to fetch multiple DynamoDB pages to fill requested page_size
   - Cache relevance scores in pagination token if needed

### Performance Considerations

- **Target**: < 500ms for typical queries (< 1000 matching sessions)
- **Optimization**: Use GSIs to reduce scanned items
- **Trade-off**: Keyword search requires application-level filtering (unavoidable with DynamoDB)
- **Future Enhancement**: Consider ElasticSearch/OpenSearch for full-text search if keyword performance becomes critical

## Future Enhancements

1. **Advanced Keyword Search**:
   - Phrase matching with quotes
   - Boolean operators (AND, OR, NOT)
   - Fuzzy matching for typos

2. **Additional Filters**:
   - Session type filter
   - Speaker name filter
   - Time range filter

3. **Search Analytics**:
   - Track popular search terms
   - Optimize indexes based on usage patterns

4. **Caching**:
   - Cache popular search queries
   - Use CloudFront for API response caching
