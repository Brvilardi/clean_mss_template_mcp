# API Reference

## Base URL

```
https://{api-gateway-id}.execute-api.{region}.amazonaws.com/{stage}/mss-template
```

Example:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/mss-template
```

---

## Authentication

Currently, this template does not implement authentication. For production use, consider adding:
- AWS IAM authentication
- Amazon Cognito user pools
- API keys
- Custom authorizers

---

## Common Headers

### Request Headers
```
Content-Type: application/json
```

### Response Headers
```
Content-Type: application/json
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

---

## Endpoints

### 1. Create User

Create a new user in the system.

**Endpoint**: `POST /mss-template/create-user`

**Request Body**:
```json
{
  "name": "string",
  "email": "string"
}
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | User's full name (minimum 2 characters) |
| email | string | Yes | Valid email address |

**Success Response** (201 Created):
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "PENDING",
  "message": "the user was created successfully"
}
```

**Error Responses**:

400 Bad Request - Missing name parameter:
```json
{
  "message": "Field name is missing"
}
```

400 Bad Request - Missing email parameter:
```json
{
  "message": "Field email is missing"
}
```

400 Bad Request - Invalid name:
```json
{
  "message": "Field name is not valid"
}
```

400 Bad Request - Invalid email format:
```json
{
  "message": "Field email is not valid"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/mss-template/create-user \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john.doe@example.com"
  }'
```

**Example Response**:
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "PENDING",
  "message": "the user was created successfully"
}
```

---

### 2. Get User

Retrieve a specific user by ID.

**Endpoint**: `GET /mss-template/get-user`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique user identifier |

**Success Response** (200 OK):
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was retrieved successfully"
}
```

**Error Responses**:

400 Bad Request - Missing user_id:
```json
{
  "message": "Field user_id is missing"
}
```

400 Bad Request - Invalid user_id type:
```json
{
  "message": "Field user_id is not valid"
}
```

404 Not Found - User doesn't exist:
```json
{
  "message": "No items found for user_id"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Request**:
```bash
curl -X GET "https://api.example.com/mss-template/get-user?user_id=1" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was retrieved successfully"
}
```

---

### 3. Get All Users

Retrieve all users in the system.

**Endpoint**: `GET /mss-template/get-all-users`

**Query Parameters**: None

**Success Response** (200 OK):
```json
{
  "users": [
    {
      "user_id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com",
      "state": "APPROVED"
    },
    {
      "user_id": 2,
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "state": "PENDING"
    }
  ],
  "message": "all users were retrieved successfully"
}
```

**Error Responses**:

404 Not Found - No users exist:
```json
{
  "message": "No items found"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Request**:
```bash
curl -X GET https://api.example.com/mss-template/get-all-users \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "users": [
    {
      "user_id": 1,
      "name": "John Doe",
      "email": "john.doe@example.com",
      "state": "APPROVED"
    },
    {
      "user_id": 2,
      "name": "Jane Smith",
      "email": "jane.smith@example.com",
      "state": "PENDING"
    }
  ],
  "message": "all users were retrieved successfully"
}
```

---

### 4. Update User

Update an existing user's information.

**Endpoint**: `POST /mss-template/update-user`

**Request Body**:
```json
{
  "user_id": 1,
  "new_name": "string"
}
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique user identifier |
| new_name | string | Yes | New name for the user (minimum 2 characters) |

**Success Response** (200 OK):
```json
{
  "user_id": 1,
  "name": "John Updated Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was updated successfully"
}
```

**Error Responses**:

400 Bad Request - Missing user_id:
```json
{
  "message": "Field user_id is missing"
}
```

400 Bad Request - Missing new_name:
```json
{
  "message": "Field new_name is missing"
}
```

400 Bad Request - Invalid new_name:
```json
{
  "message": "Field name is not valid"
}
```

404 Not Found - User doesn't exist:
```json
{
  "message": "No items found for user_id"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/mss-template/update-user \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "new_name": "John Updated Doe"
  }'
```

**Example Response**:
```json
{
  "user_id": 1,
  "name": "John Updated Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was updated successfully"
}
```

---

### 5. Delete User

Delete a user from the system.

**Endpoint**: `POST /mss-template/delete-user`

**Request Body**:
```json
{
  "user_id": 1
}
```

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | Unique user identifier |

**Success Response** (200 OK):
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was deleted successfully"
}
```

**Error Responses**:

400 Bad Request - Missing user_id:
```json
{
  "message": "Field user_id is missing"
}
```

400 Bad Request - Invalid user_id type:
```json
{
  "message": "Field user_id is not valid"
}
```

404 Not Found - User doesn't exist:
```json
{
  "message": "No items found for user_id"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Request**:
```bash
curl -X POST https://api.example.com/mss-template/delete-user \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1
  }'
```

**Example Response**:
```json
{
  "user_id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com",
  "state": "APPROVED",
  "message": "the user was deleted successfully"
}
```

---

### 6. Search Sessions

Search for re:Invent sessions with multiple filter criteria including speaker name/company.

**Endpoint**: `GET /mss-template/search-sessions`

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| day | string | No | - | Filter by day (e.g., "Monday", "Tuesday") |
| venue | string | No | - | Filter by venue name (e.g., "Venetian", "Mandalay Bay") |
| level | integer | No | - | Filter by level (100, 200, 300, 400) |
| keywords | string | No | - | Space-separated keywords to search in title, abstract, topics, areas |
| speaker | string | No | - | Filter by speaker name or company (case-insensitive, partial match) |
| session_type | string | No | - | Filter by session type (case-insensitive, partial match) |
| page_size | integer | No | 50 | Results per page (1-100) |
| next_page_token | string | No | - | Pagination token from previous response |

**Speaker Parameter Behavior**:
- **Case-insensitive**: Searches for "Werner", "WERNER", or "werner" return the same results
- **Partial matching**: Searching for "John" matches "John Doe", "Johnny Smith", etc.
- **Searches both fields**: Searches both speaker displayName and company fields
- **Checks all speakers**: If a session has multiple speakers, matches any of them
- **Combines with other filters**: Can be used with day, venue, level, keywords, and session_type filters

**Session Type Parameter Behavior**:
- **Case-insensitive**: Searches for "Workshop", "WORKSHOP", or "workshop" return the same results
- **Partial matching**: Searching for "Break" matches "Breakout Session", "Breakfast Session", etc.
- **Searches session_type field**: Matches against the session's session_type attribute
- **Combines with other filters**: Can be used with day, venue, level, keywords, and speaker filters

**Success Response** (200 OK):
```json
{
  "sessions": [
    {
      "session_id": "ABC123",
      "short_id": "ABC123",
      "title": "Building Serverless Applications",
      "abstract": "Learn how to build serverless applications...",
      "session_type": "Breakout Session",
      "day": "Monday",
      "venue_name": "Venetian",
      "level_value": 300,
      "start_datetime": "2025-12-02T09:00:00.000Z",
      "end_datetime": "2025-12-02T10:00:00.000Z",
      "speakers": [
        {
          "displayName": "Werner Vogels",
          "company": "AWS"
        }
      ],
      "topics": ["Serverless", "Lambda"],
      "areas": ["Compute"],
      "features": ["Demo"]
    }
  ],
  "next_page_token": "eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0=",
  "total_results": 1,
  "message": "sessions retrieved successfully"
}
```

**Error Responses**:

400 Bad Request - Invalid speaker parameter (empty or whitespace-only):
```json
{
  "message": "Field speaker is not valid"
}
```

400 Bad Request - Invalid session_type parameter (empty or whitespace-only):
```json
{
  "message": "Field session_type is not valid"
}
```

400 Bad Request - Invalid page_size:
```json
{
  "message": "Field page_size is not valid"
}
```

400 Bad Request - Invalid level:
```json
{
  "message": "Field level is not valid"
}
```

500 Internal Server Error:
```json
{
  "message": "Internal server error message"
}
```

**Example Requests**:

Search by speaker name:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=Werner%20Vogels" \
  -H "Content-Type: application/json"
```

Search by company:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=AWS" \
  -H "Content-Type: application/json"
```

Search by partial speaker name:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=John" \
  -H "Content-Type: application/json"
```

Combine speaker with other filters:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=Werner&day=Monday&level=400" \
  -H "Content-Type: application/json"
```

Combine speaker with keywords:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=AWS&keywords=serverless%20lambda" \
  -H "Content-Type: application/json"
```

Search by session type:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?session_type=Workshop" \
  -H "Content-Type: application/json"
```

Search by partial session type:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?session_type=Break" \
  -H "Content-Type: application/json"
```

Combine session_type with other filters:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?session_type=Workshop&day=Monday&level=300" \
  -H "Content-Type: application/json"
```

Combine session_type with speaker and keywords:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?session_type=Breakout&speaker=AWS&keywords=serverless" \
  -H "Content-Type: application/json"
```

Search with pagination:
```bash
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=AWS&page_size=20&next_page_token=eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0=" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "sessions": [
    {
      "session_id": "ABC123",
      "short_id": "ABC123",
      "title": "Building Serverless Applications at Scale",
      "abstract": "Learn how to build and scale serverless applications using AWS Lambda, API Gateway, and DynamoDB...",
      "session_type": "Breakout Session",
      "day": "Monday",
      "venue_name": "Venetian",
      "level_value": 300,
      "start_datetime": "2025-12-02T09:00:00.000Z",
      "end_datetime": "2025-12-02T10:00:00.000Z",
      "speakers": [
        {
          "displayName": "Werner Vogels",
          "company": "AWS"
        },
        {
          "displayName": "Jane Smith",
          "company": "AWS"
        }
      ],
      "topics": ["Serverless", "Lambda", "API Gateway"],
      "areas": ["Compute", "Application Integration"],
      "features": ["Demo", "Hands-on"]
    },
    {
      "session_id": "DEF456",
      "short_id": "DEF456",
      "title": "Advanced Serverless Patterns",
      "abstract": "Deep dive into advanced serverless patterns...",
      "session_type": "Workshop",
      "day": "Tuesday",
      "venue_name": "Mandalay Bay",
      "level_value": 400,
      "start_datetime": "2025-12-03T14:00:00.000Z",
      "end_datetime": "2025-12-03T15:00:00.000Z",
      "speakers": [
        {
          "displayName": "John Doe",
          "company": "AWS"
        }
      ],
      "topics": ["Serverless", "Architecture"],
      "areas": ["Architecture"],
      "features": ["Workshop"]
    }
  ],
  "next_page_token": "eyJzZXNzaW9uX2lkIjoiREVGNDU2In0=",
  "total_results": 2,
  "message": "sessions retrieved successfully"
}
```

**Notes**:
- When no filters are provided, returns all sessions (paginated)
- Empty results return 200 OK with empty sessions array
- Speaker search is case-insensitive and matches partial names
- Speaker search checks both displayName and company fields
- Speaker search checks all speakers in a session's speakers list
- Session type search is case-insensitive and matches partial strings
- Session type search checks the session_type field
- Filters can be combined for more specific searches
- Results are ordered by start_datetime when using indexed filters (day, venue, level)

---

## Data Models

### Session Object

```json
{
  "session_id": "string",
  "short_id": "string",
  "title": "string",
  "abstract": "string",
  "session_type": "string",
  "day": "string",
  "venue_name": "string",
  "level_value": "integer",
  "start_datetime": "string (ISO 8601)",
  "end_datetime": "string (ISO 8601)",
  "speakers": [
    {
      "displayName": "string",
      "company": "string"
    }
  ],
  "topics": ["string"],
  "areas": ["string"],
  "features": ["string"]
}
```

**Fields**:
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| session_id | string | Unique session identifier | Required |
| short_id | string | Short session code | Required |
| title | string | Session title | Required, non-empty |
| abstract | string | Session description | Required |
| session_type | string | Session format/type | e.g., "Breakout Session", "Workshop", "Chalk Talk" |
| day | string | Day of the week | Monday-Friday |
| venue_name | string | Venue location | Required |
| level_value | integer | Session difficulty level | 100, 200, 300, or 400 |
| start_datetime | string | Session start time | ISO 8601 format |
| end_datetime | string | Session end time | ISO 8601 format |
| speakers | array | List of speakers | Can be empty |
| topics | array | Session topics | Can be empty |
| areas | array | AWS service areas | Can be empty |
| features | array | Session features | Can be empty |

### Speaker Object

```json
{
  "displayName": "string",
  "company": "string"
}
```

**Fields**:
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| displayName | string | Speaker's full name | Required |
| company | string | Speaker's company/organization | Optional |

### User Object

```json
{
  "user_id": "integer",
  "name": "string",
  "email": "string",
  "state": "string"
}
```

**Fields**:
| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| user_id | integer | Unique identifier | Auto-generated, positive integer |
| name | string | User's full name | Minimum 2 characters |
| email | string | User's email address | Valid email format (RFC 5322) |
| state | string | User's current state | Enum: PENDING, APPROVED, etc. |

### State Enum

Possible values for the `state` field:
- `PENDING`: User created but not yet approved
- `APPROVED`: User has been approved
- (Additional states can be defined in `src/shared/domain/enums/state_enum.py`)

---

## Error Codes

### HTTP Status Codes

| Status Code | Meaning | When Used |
|-------------|---------|-----------|
| 200 | OK | Successful GET, UPDATE, DELETE operations |
| 201 | Created | Successful CREATE operation |
| 400 | Bad Request | Invalid input, missing parameters, validation errors |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Unexpected server error |

### Error Response Format

All error responses follow this format:
```json
{
  "message": "Error description"
}
```

### Common Error Messages

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "Field {field} is missing" | Required parameter not provided | Include the required field in request |
| "Field {field} is not valid" | Invalid data format or value | Check data type and format constraints |
| "No items found for user_id" | User with given ID doesn't exist | Verify user_id exists before operation |
| "No items found" | No users in system | Create users first |

---

## Validation Rules

### Name Validation
- **Type**: String
- **Minimum Length**: 2 characters
- **Required**: Yes
- **Example Valid**: "John Doe", "Jane"
- **Example Invalid**: "J", "", null

### Email Validation
- **Type**: String
- **Format**: Valid email address (RFC 5322)
- **Required**: Yes
- **Pattern**: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`
- **Example Valid**: "user@example.com", "john.doe+tag@company.co.uk"
- **Example Invalid**: "invalid", "user@", "@example.com", "user @example.com"

### User ID Validation
- **Type**: Integer
- **Minimum Value**: 0
- **Required**: Yes (for get, update, delete operations)
- **Example Valid**: 1, 42, 1000
- **Example Invalid**: -1, "abc", null, 3.14

### Speaker Parameter Validation
- **Type**: String
- **Required**: No
- **Case Sensitivity**: Case-insensitive matching
- **Matching**: Partial string matching
- **Search Fields**: Both displayName and company
- **Example Valid**: "Werner", "AWS", "John Doe", "amazon"
- **Example Invalid**: "" (empty string), "   " (whitespace-only)
- **Behavior**: 
  - Searches both speaker displayName and company fields
  - Matches any speaker in a session's speakers list
  - Case-insensitive: "Werner" matches "werner", "WERNER", "Werner"
  - Partial match: "John" matches "John Doe", "Johnny Smith"

### Session Type Parameter Validation
- **Type**: String
- **Required**: No
- **Case Sensitivity**: Case-insensitive matching
- **Matching**: Partial string matching
- **Search Fields**: session_type field
- **Example Valid**: "Workshop", "Breakout Session", "Chalk Talk", "Break"
- **Example Invalid**: "" (empty string), "   " (whitespace-only)
- **Behavior**: 
  - Searches the session_type field
  - Case-insensitive: "Workshop" matches "workshop", "WORKSHOP", "Workshop"
  - Partial match: "Break" matches "Breakout Session", "Breakfast Session"

### Day Parameter Validation
- **Type**: String
- **Required**: No
- **Valid Values**: "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
- **Example Valid**: "Monday", "Tuesday"
- **Example Invalid**: "Saturday", "monday" (case-sensitive)

### Venue Parameter Validation
- **Type**: String
- **Required**: No
- **Example Valid**: "Venetian", "Mandalay Bay", "MGM Grand"
- **Note**: Must match exact venue name (case-sensitive)

### Level Parameter Validation
- **Type**: Integer
- **Required**: No
- **Valid Values**: 100, 200, 300, 400
- **Example Valid**: 100, 200, 300, 400
- **Example Invalid**: 150, 500, "300" (must be integer)

### Keywords Parameter Validation
- **Type**: String
- **Required**: No
- **Format**: Space-separated keywords
- **Search Fields**: title, abstract, topics, areas
- **Example Valid**: "serverless lambda", "security machine learning"
- **Behavior**: Searches across multiple fields for relevance

### Page Size Validation
- **Type**: Integer
- **Required**: No
- **Default**: 50
- **Range**: 1-100
- **Example Valid**: 10, 50, 100
- **Example Invalid**: 0, 101, -5, "50" (must be integer)

---

## Rate Limiting

Currently, this template does not implement rate limiting. For production use, consider:
- AWS API Gateway usage plans
- Lambda concurrency limits
- DynamoDB capacity management

---

## CORS Configuration

The API is configured to allow cross-origin requests:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: *
```

For production, consider restricting origins to specific domains.

---

## Testing the API

### Using cURL

```bash
# Create a user
curl -X POST https://api.example.com/mss-template/create-user \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'

# Get a user
curl -X GET "https://api.example.com/mss-template/get-user?user_id=1"

# Get all users
curl -X GET https://api.example.com/mss-template/get-all-users

# Update a user
curl -X POST https://api.example.com/mss-template/update-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "new_name": "Updated Name"}'

# Delete a user
curl -X POST https://api.example.com/mss-template/delete-user \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Search sessions by speaker
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=Werner%20Vogels"

# Search sessions by company
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=AWS"

# Search sessions with multiple filters including session_type
curl -X GET "https://api.example.com/mss-template/search-sessions?session_type=Workshop&speaker=Werner&day=Monday&level=300&keywords=serverless%20lambda"

# Search sessions with pagination
curl -X GET "https://api.example.com/mss-template/search-sessions?speaker=AWS&page_size=20&next_page_token=eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0="
```

### Using Python

```python
import requests
import json

base_url = "https://api.example.com/mss-template"

# Create user
response = requests.post(
    f"{base_url}/create-user",
    json={"name": "Test User", "email": "test@example.com"}
)
print(response.json())

# Get user
response = requests.get(
    f"{base_url}/get-user",
    params={"user_id": 1}
)
print(response.json())

# Get all users
response = requests.get(f"{base_url}/get-all-users")
print(response.json())

# Update user
response = requests.post(
    f"{base_url}/update-user",
    json={"user_id": 1, "new_name": "Updated Name"}
)
print(response.json())

# Delete user
response = requests.post(
    f"{base_url}/delete-user",
    json={"user_id": 1}
)
print(response.json())

# Search sessions by speaker
response = requests.get(
    f"{base_url}/search-sessions",
    params={"speaker": "Werner Vogels"}
)
print(response.json())

# Search sessions by company
response = requests.get(
    f"{base_url}/search-sessions",
    params={"speaker": "AWS"}
)
print(response.json())

# Search sessions by session type
response = requests.get(
    f"{base_url}/search-sessions",
    params={"session_type": "Workshop"}
)
print(response.json())

# Search sessions by partial session type
response = requests.get(
    f"{base_url}/search-sessions",
    params={"session_type": "Break"}
)
print(response.json())

# Search sessions with multiple filters including session_type
response = requests.get(
    f"{base_url}/search-sessions",
    params={
        "session_type": "Workshop",
        "speaker": "Werner",
        "day": "Monday",
        "level": 300,
        "keywords": "serverless lambda"
    }
)
print(response.json())

# Search sessions with pagination
response = requests.get(
    f"{base_url}/search-sessions",
    params={
        "speaker": "AWS",
        "page_size": 20,
        "next_page_token": "eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0="
    }
)
print(response.json())
```

### Using JavaScript (fetch)

```javascript
const baseUrl = 'https://api.example.com/mss-template';

// Create user
fetch(`${baseUrl}/create-user`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Test User',
    email: 'test@example.com'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Get user
fetch(`${baseUrl}/get-user?user_id=1`)
  .then(response => response.json())
  .then(data => console.log(data));

// Get all users
fetch(`${baseUrl}/get-all-users`)
  .then(response => response.json())
  .then(data => console.log(data));

// Update user
fetch(`${baseUrl}/update-user`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    user_id: 1,
    new_name: 'Updated Name'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Delete user
fetch(`${baseUrl}/delete-user`, {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({user_id: 1})
})
.then(response => response.json())
.then(data => console.log(data));

// Search sessions by speaker
fetch(`${baseUrl}/search-sessions?speaker=Werner%20Vogels`)
  .then(response => response.json())
  .then(data => console.log(data));

// Search sessions by company
fetch(`${baseUrl}/search-sessions?speaker=AWS`)
  .then(response => response.json())
  .then(data => console.log(data));

// Search sessions by session type
fetch(`${baseUrl}/search-sessions?session_type=Workshop`)
  .then(response => response.json())
  .then(data => console.log(data));

// Search sessions by partial session type
fetch(`${baseUrl}/search-sessions?session_type=Break`)
  .then(response => response.json())
  .then(data => console.log(data));

// Search sessions with multiple filters including session_type
const params = new URLSearchParams({
  session_type: 'Workshop',
  speaker: 'Werner',
  day: 'Monday',
  level: '300',
  keywords: 'serverless lambda'
});
fetch(`${baseUrl}/search-sessions?${params}`)
  .then(response => response.json())
  .then(data => console.log(data));

// Search sessions with pagination
const paginationParams = new URLSearchParams({
  speaker: 'AWS',
  page_size: '20',
  next_page_token: 'eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0='
});
fetch(`${baseUrl}/search-sessions?${paginationParams}`)
  .then(response => response.json())
  .then(data => console.log(data));
```

---

## Postman Collection

You can import this API into Postman using the following collection structure:

```json
{
  "info": {
    "name": "Clean MSS Template API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create User",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"name\": \"John Doe\", \"email\": \"john@example.com\"}"
        },
        "url": "{{base_url}}/create-user"
      }
    },
    {
      "name": "Get User",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/get-user?user_id=1",
          "query": [{"key": "user_id", "value": "1"}]
        }
      }
    },
    {
      "name": "Get All Users",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/get-all-users"
      }
    },
    {
      "name": "Update User",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"user_id\": 1, \"new_name\": \"Updated Name\"}"
        },
        "url": "{{base_url}}/update-user"
      }
    },
    {
      "name": "Delete User",
      "request": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {
          "mode": "raw",
          "raw": "{\"user_id\": 1}"
        },
        "url": "{{base_url}}/delete-user"
      }
    },
    {
      "name": "Search Sessions - By Speaker",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?speaker=Werner%20Vogels",
          "query": [{"key": "speaker", "value": "Werner Vogels"}]
        }
      }
    },
    {
      "name": "Search Sessions - By Company",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?speaker=AWS",
          "query": [{"key": "speaker", "value": "AWS"}]
        }
      }
    },
    {
      "name": "Search Sessions - By Session Type",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?session_type=Workshop",
          "query": [{"key": "session_type", "value": "Workshop"}]
        }
      }
    },
    {
      "name": "Search Sessions - By Partial Session Type",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?session_type=Break",
          "query": [{"key": "session_type", "value": "Break"}]
        }
      }
    },
    {
      "name": "Search Sessions - Multiple Filters",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?session_type=Workshop&speaker=Werner&day=Monday&level=300&keywords=serverless%20lambda",
          "query": [
            {"key": "session_type", "value": "Workshop"},
            {"key": "speaker", "value": "Werner"},
            {"key": "day", "value": "Monday"},
            {"key": "level", "value": "300"},
            {"key": "keywords", "value": "serverless lambda"}
          ]
        }
      }
    },
    {
      "name": "Search Sessions - With Pagination",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/search-sessions?speaker=AWS&page_size=20&next_page_token=eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0=",
          "query": [
            {"key": "speaker", "value": "AWS"},
            {"key": "page_size", "value": "20"},
            {"key": "next_page_token", "value": "eyJzZXNzaW9uX2lkIjoiQUJDMTIzIn0="}
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "https://api.example.com/mss-template"
    }
  ]
}
```

---

## Best Practices

1. **Always validate input** on the client side before sending requests
2. **Handle errors gracefully** and provide user-friendly messages
3. **Use appropriate HTTP methods** (GET for retrieval, POST for modifications)
4. **Include proper headers** (Content-Type: application/json)
5. **Check response status codes** before processing response body
6. **Implement retry logic** for transient failures (500 errors)
7. **Log API interactions** for debugging and monitoring
8. **Don't expose sensitive information** in error messages

---

## Future Enhancements

Consider implementing these features for production:

1. **Pagination** for get-all-users endpoint
2. **Filtering and sorting** capabilities
3. **Partial updates** (PATCH method)
4. **Bulk operations** (create/update/delete multiple users)
5. **API versioning** (v1, v2, etc.)
6. **Request/response compression**
7. **API documentation** (OpenAPI/Swagger)
8. **Webhooks** for event notifications
9. **GraphQL** alternative endpoint
10. **Rate limiting** and throttling
