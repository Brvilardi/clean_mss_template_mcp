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

## Data Models

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
