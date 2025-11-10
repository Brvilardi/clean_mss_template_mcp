# Architecture Documentation

## Clean Architecture Overview

This project implements Clean Architecture principles, creating a maintainable, testable, and scalable microservice architecture for AWS Lambda.

![Architecture Diagram](architecture_diagram.png)

---

## Architectural Layers

### 1. Domain Layer (Innermost)

**Location**: `src/shared/domain/`

The core business logic layer, independent of frameworks and external systems.

#### Components

**Entities** (`entities/`)
```python
# src/shared/domain/entities/user.py
class User:
    - name: str
    - email: str
    - state: STATE
    - user_id: int
    
    # Business rules and validation
    - validate_name()
    - validate_email()
```

**Enums** (`enums/`)
```python
# src/shared/domain/enums/state_enum.py
class STATE(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    # ... other states
```

**Repository Interfaces** (`repositories/`)
```python
# src/shared/domain/repositories/user_repository_interface.py
class IUserRepository(ABC):
    @abstractmethod
    def get_user(user_id: int) -> User
    
    @abstractmethod
    def create_user(new_user: User) -> User
    
    @abstractmethod
    def update_user(user_id: int, new_name: str) -> User
    
    @abstractmethod
    def delete_user(user_id: int) -> User
    
    @abstractmethod
    def get_all_user() -> List[User]
```

**Key Principles**:
- No dependencies on outer layers
- Pure business logic
- Framework-agnostic
- Highly testable

---

### 2. Use Case Layer (Application Business Rules)

**Location**: `src/modules/*/app/*_usecase.py`

Orchestrates the flow of data to and from entities, implementing application-specific business rules.

#### Example: Create User Use Case

```python
# src/modules/create_user/app/create_user_usecase.py
class CreateUserUsecase:
    def __init__(self, repo: IUserRepository):
        self.repo = repo
    
    def __call__(self, name: str, email: str) -> User:
        # Validate inputs
        if not User.validate_name(name):
            raise EntityError("name")
        
        if not User.validate_email(email):
            raise EntityError("email")
        
        # Create entity
        user = User(
            name=name,
            email=email,
            state=STATE.PENDING
        )
        
        # Persist through repository
        return self.repo.create_user(user)
```

**Responsibilities**:
- Input validation
- Business logic orchestration
- Entity creation and manipulation
- Repository interaction
- Error handling

**Dependencies**:
- Domain entities
- Repository interfaces
- Domain errors

---

### 3. Interface Adapters Layer

**Location**: `src/modules/*/app/`

Converts data between the format most convenient for use cases and entities, and the format most convenient for external agencies.

#### Controllers

```python
# src/modules/create_user/app/create_user_controller.py
class CreateUserController:
    def __init__(self, usecase: CreateUserUsecase):
        self.CreateUserUsecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Extract parameters
            name = request.data.get('name')
            email = request.data.get('email')
            
            # Validate presence
            if name is None:
                raise MissingParameters('name')
            if email is None:
                raise MissingParameters('email')
            
            # Call use case
            user = self.CreateUserUsecase(name=name, email=email)
            
            # Format response
            viewmodel = CreateUserViewmodel(user)
            return Created(viewmodel.to_dict())
            
        except NoItemsFound as err:
            return NotFound(body=err.message)
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
```

**Responsibilities**:
- Parse HTTP requests
- Parameter validation
- Use case invocation
- Error handling and mapping
- HTTP response creation

#### ViewModels

```python
# src/modules/create_user/app/create_user_viewmodel.py
class CreateUserViewmodel:
    def __init__(self, user: User):
        self.user_id = user.user_id
        self.name = user.name
        self.email = user.email
        self.state = user.state
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'state': self.state.value,
            'message': "the user was created successfully"
        }
```

**Responsibilities**:
- Transform domain entities to API responses
- Add presentation-specific fields
- Format data for external consumption

#### Presenters (Lambda Handlers)

```python
# src/modules/create_user/app/create_user_presenter.py
repo = Environments.get_user_repo()()
usecase = CreateUserUsecase(repo)
controller = CreateUserController(usecase)

def lambda_handler(event, context):
    # Convert Lambda event to HTTP request
    httpRequest = LambdaHttpRequest(data=event)
    
    # Process request
    response = controller(httpRequest)
    
    # Convert to Lambda response
    httpResponse = LambdaHttpResponse(
        status_code=response.status_code,
        body=response.body,
        headers=response.headers
    )
    
    return httpResponse.toDict()
```

**Responsibilities**:
- Lambda entry point
- Dependency injection
- Event conversion
- Response formatting

---

### 4. Frameworks & Drivers Layer (Outermost)

**Location**: `src/shared/infra/`

Contains all the details: database implementations, web frameworks, external services.

#### Repository Implementations

**DynamoDB Repository**
```python
# src/shared/infra/repositories/user_repository_dynamo.py
class UserRepositoryDynamo(IUserRepository):
    def __init__(self):
        self.dynamo = DynamoTable()
    
    def create_user(self, new_user: User) -> User:
        # Get next user ID
        user_id = self.get_user_counter() + 1
        new_user.user_id = user_id
        
        # Convert to DTO
        user_dto = UserDynamoDTO.from_entity(new_user)
        
        # Save to DynamoDB
        self.dynamo.put_item(
            partition_key=user_dto.pk,
            sort_key=user_dto.sk,
            item=user_dto.to_dynamo()
        )
        
        return new_user
```

**Mock Repository**
```python
# src/shared/infra/repositories/user_repository_mock.py
class UserRepositoryMock(IUserRepository):
    def __init__(self):
        self.users = [
            User(name="John Doe", email="john@example.com", 
                 state=STATE.APPROVED, user_id=1),
            # ... more mock users
        ]
    
    def create_user(self, new_user: User) -> User:
        new_user.user_id = len(self.users) + 1
        self.users.append(new_user)
        return new_user
```

#### Data Transfer Objects (DTOs)

```python
# src/shared/infra/dto/user_dynamo_dto.py
class UserDynamoDTO:
    pk: str  # Partition key: "USER#{user_id}"
    sk: str  # Sort key: "USER#{user_id}"
    name: str
    email: str
    state: str
    
    @staticmethod
    def from_entity(user: User) -> UserDynamoDTO:
        # Convert domain entity to DynamoDB format
        
    def to_entity(self) -> User:
        # Convert DynamoDB format to domain entity
    
    def to_dynamo(self) -> dict:
        # Convert to DynamoDB item format
```

#### External Services

**DynamoDB Client**
```python
# src/shared/infra/external/dynamo/dynamo_table.py
class DynamoTable:
    def __init__(self):
        self.dynamo = boto3.resource('dynamodb', 
                                     endpoint_url=Environments.get_envs().endpoint_url)
        self.table = self.dynamo.Table(Environments.get_envs().dynamo_table_name)
    
    def get_item(self, partition_key: str, sort_key: str) -> dict
    def put_item(self, partition_key: str, sort_key: str, item: dict)
    def delete_item(self, partition_key: str, sort_key: str)
    def query(self, key_condition_expression: str) -> List[dict]
```

**Observability**
```python
# src/shared/infra/external/observability/observability_aws.py
class ObservabilityAWS(IObservability):
    # AWS X-Ray integration
    # Lambda Powertools metrics
    # Structured logging
```

---

## Data Flow

### Request Flow (Create User Example)

```
1. API Gateway receives HTTP POST request
   ↓
2. Lambda invokes create_user_presenter.lambda_handler()
   ↓
3. Presenter converts Lambda event to LambdaHttpRequest
   ↓
4. Controller (CreateUserController) receives request
   ↓
5. Controller validates parameters
   ↓
6. Controller calls CreateUserUsecase
   ↓
7. Usecase validates business rules
   ↓
8. Usecase creates User entity
   ↓
9. Usecase calls repository.create_user()
   ↓
10. Repository (UserRepositoryDynamo) converts to DTO
   ↓
11. Repository saves to DynamoDB
   ↓
12. Repository returns User entity
   ↓
13. Usecase returns User to Controller
   ↓
14. Controller creates CreateUserViewmodel
   ↓
15. Controller returns HTTP 201 Created response
   ↓
16. Presenter converts to Lambda response format
   ↓
17. API Gateway returns HTTP response to client
```

### Dependency Flow

```
Presenter → Controller → Usecase → Repository Interface
                                          ↑
                                          |
                                    Repository Implementation
                                          ↑
                                          |
                                      DynamoDB
```

**Key Principle**: Dependencies point inward. Outer layers depend on inner layers, never the reverse.

---

## Infrastructure Architecture

### AWS Components

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│                    (REST API Endpoint)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─── POST /mss-template/create-user
                         ├─── GET  /mss-template/get-user
                         ├─── GET  /mss-template/get-all-users
                         ├─── POST /mss-template/update-user
                         └─── POST /mss-template/delete-user
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌──────────────┐                  ┌──────────────┐
│   Lambda     │                  │   Lambda     │
│  Functions   │                  │    Layer     │
│              │                  │  (shared/)   │
│ - create_user│◄─────────────────┤              │
│ - get_user   │                  │ - domain     │
│ - update_user│                  │ - helpers    │
│ - delete_user│                  │ - infra      │
│ - get_all    │                  └──────────────┘
└──────┬───────┘
       │
       │ Read/Write
       │
       ▼
┌──────────────┐
│   DynamoDB   │
│    Table     │
│              │
│ PK: USER#id  │
│ SK: USER#id  │
└──────────────┘
```

### CDK Stack Structure

```
TemplateStack (Main)
├── RestApi (API Gateway)
│   └── Resource: /mss-template
│       ├── POST /create-user
│       ├── GET  /get-user
│       ├── GET  /get-all-users
│       ├── POST /update-user
│       └── POST /delete-user
│
├── LambdaStack
│   ├── Lambda Layer (shared code)
│   ├── Lambda Powertools Layer
│   └── Lambda Functions (5)
│       ├── create_user_function
│       ├── get_user_function
│       ├── get_all_users_function
│       ├── update_user_function
│       └── delete_user_function
│
└── TemplateDynamoTable
    └── DynamoDB Table
        ├── Partition Key: PK
        ├── Sort Key: SK
        └── Permissions granted to Lambda functions
```

---

## Environment Management

### Configuration Strategy

```python
# src/shared/environments.py
class Environments:
    stage: STAGE  # TEST, DEV, HOMOLOG, PROD
    
    # DynamoDB configuration
    dynamo_table_name: str
    dynamo_partition_key: str
    dynamo_sort_key: str
    endpoint_url: str  # For local development
    
    # AWS configuration
    region: str
    s3_bucket_name: str
    
    @staticmethod
    def get_user_repo() -> IUserRepository:
        if stage == STAGE.TEST:
            return UserRepositoryMock
        else:
            return UserRepositoryDynamo
    
    @staticmethod
    def get_observability() -> IObservability:
        if stage == STAGE.TEST:
            return ObservabilityMock
        else:
            return ObservabilityAWS
```

### Stage-Specific Behavior

| Stage | Repository | Observability | Database |
|-------|-----------|---------------|----------|
| TEST | Mock | Mock | In-memory |
| DEV | DynamoDB | AWS X-Ray | DynamoDB (dev) |
| HOMOLOG | DynamoDB | AWS X-Ray | DynamoDB (staging) |
| PROD | DynamoDB | AWS X-Ray | DynamoDB (prod) |

---

## Error Handling Strategy

### Error Hierarchy

```
BaseError (base class)
├── DomainErrors
│   └── EntityError (invalid entity data)
│
├── UsecaseErrors
│   └── NoItemsFound (resource not found)
│
└── ControllerErrors
    ├── MissingParameters (required param missing)
    └── WrongTypeParameter (invalid param type)
```

### HTTP Status Code Mapping

| Error Type | HTTP Status | Example |
|-----------|-------------|---------|
| EntityError | 400 Bad Request | Invalid email format |
| MissingParameters | 400 Bad Request | Missing 'name' parameter |
| WrongTypeParameter | 400 Bad Request | 'user_id' must be integer |
| NoItemsFound | 404 Not Found | User not found |
| Exception | 500 Internal Server Error | Unexpected error |

---

## Testing Strategy

### Test Structure

```
tests/
├── modules/              # Integration tests
│   ├── create_user/
│   │   └── app/
│   │       ├── test_create_user_controller.py
│   │       ├── test_create_user_usecase.py
│   │       ├── test_create_user_viewmodel.py
│   │       └── test_create_user_presenter.py
│   └── ...
│
└── shared/              # Unit tests
    ├── domain/
    │   └── entities/
    │       └── test_user.py
    └── infra/
        └── repositories/
            ├── test_user_repository_mock.py
            └── test_user_repository_dynamo.py
```

### Testing Layers

1. **Domain Tests**: Pure unit tests, no dependencies
2. **Use Case Tests**: Use mock repositories
3. **Controller Tests**: Test request/response handling
4. **Repository Tests**: Test data access logic
5. **Integration Tests**: End-to-end module tests

---

## Observability

### AWS X-Ray Integration

- Distributed tracing across Lambda functions
- Performance monitoring
- Error tracking
- Service map visualization

### Lambda Powertools

- Structured logging
- Custom metrics
- Correlation IDs
- Request/response logging

### Monitoring Points

1. **API Gateway**: Request count, latency, errors
2. **Lambda Functions**: Invocations, duration, errors, cold starts
3. **DynamoDB**: Read/write capacity, throttling, latency
4. **Custom Metrics**: Business-specific metrics

---

## Security Considerations

### IAM Permissions

- Lambda execution role with minimal permissions
- DynamoDB read/write access only for required functions
- CloudWatch Logs write access
- X-Ray write access

### API Security

- CORS configuration for cross-origin requests
- Input validation at multiple layers
- Error messages don't expose sensitive information

### Data Security

- DynamoDB encryption at rest
- Secure environment variable handling
- No hardcoded credentials

---

## Scalability

### Horizontal Scaling

- Lambda auto-scales based on request volume
- DynamoDB on-demand capacity mode
- API Gateway handles high request rates

### Performance Optimization

- Lambda layer for shared code (reduces deployment size)
- Connection pooling for DynamoDB
- Efficient DynamoDB key design
- Cold start optimization

---

## Design Principles Applied

1. **Dependency Inversion**: High-level modules don't depend on low-level modules
2. **Single Responsibility**: Each class has one reason to change
3. **Open/Closed**: Open for extension, closed for modification
4. **Interface Segregation**: Clients don't depend on unused methods
5. **Liskov Substitution**: Subtypes are substitutable for their base types

---

## Benefits of This Architecture

1. **Testability**: Each layer can be tested independently
2. **Maintainability**: Clear separation of concerns
3. **Flexibility**: Easy to swap implementations (e.g., database)
4. **Scalability**: Serverless architecture scales automatically
5. **Reusability**: Shared code in Lambda layer
6. **Independence**: Business logic independent of frameworks
7. **Observability**: Built-in monitoring and tracing
