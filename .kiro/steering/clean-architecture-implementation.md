---
inclusion: always
---

# Clean Architecture Implementation Rules for Kiro Agent

This steering file provides mandatory rules for implementing features in the Clean MSS Template project. Always follow these guidelines when creating or modifying code.

## Core Principles

1. **Dependencies point inward**: Outer layers depend on inner layers, never the reverse
2. **Domain independence**: Domain layer has no external dependencies
3. **Interface-based design**: Use interfaces for all cross-layer dependencies
4. **Single responsibility**: Each class has one reason to change

## Mandatory Implementation Order

When implementing a new feature, ALWAYS follow this exact sequence:

### 1. Domain Layer (Start Here)
- Create entity in `src/shared/domain/entities/{entity_name}.py`
- Add validation methods as static methods
- Create enums in `src/shared/domain/enums/` if needed
- Create repository interface in `src/shared/domain/repositories/{entity_name}_repository_interface.py`

### 2. Infrastructure Layer
- Create DTO in `src/shared/infra/dto/{entity_name}_dynamo_dto.py`
- Implement DynamoDB repository in `src/shared/infra/repositories/{entity_name}_repository_dynamo.py`
- Implement mock repository in `src/shared/infra/repositories/{entity_name}_repository_mock.py`

### 3. Use Case Layer
- Create use case in `src/modules/{feature_name}/app/{feature_name}_usecase.py`

### 4. Interface Adapters Layer
- Create view model in `src/modules/{feature_name}/app/{feature_name}_viewmodel.py`
- Create controller in `src/modules/{feature_name}/app/{feature_name}_controller.py`
- Create presenter in `src/modules/{feature_name}/app/{feature_name}_presenter.py`

### 5. Infrastructure as Code
- Add Lambda function to `iac/iac/lambda_stack.py`
- Add to `functions_that_need_dynamo_permissions` list


## Naming Conventions (MANDATORY)

### Files and Directories
- **snake_case** for all files: `create_product_controller.py`
- Module directory: `src/modules/{feature_name}/app/`

### Classes
- **Entity**: CamelCase, no prefix (e.g., `Product`, `User`)
- **Enum**: SNAKE_CASE (e.g., `PRODUCT_STATUS`, `STATE`)
- **Repository Interface**: Start with "I" (e.g., `IProductRepository`)
- **Repository Implementation**: 
  - DynamoDB: `{Entity}RepositoryDynamo` (e.g., `ProductRepositoryDynamo`)
  - Mock: `{Entity}RepositoryMock` (e.g., `ProductRepositoryMock`)
- **DTO**: `{Entity}DynamoDTO` (e.g., `ProductDynamoDTO`)
- **Use Case**: `{Action}{Entity}Usecase` (e.g., `CreateProductUsecase`)
- **Controller**: `{Action}{Entity}Controller` (e.g., `CreateProductController`)
- **View Model**: `{Action}{Entity}Viewmodel` (e.g., `CreateProductViewmodel`)

### Methods and Variables
- **snake_case** for all methods and variables
- Methods use verbs: `create_product`, `validate_name`
- Variables avoid verbs: `product_id`, `user_name`

## Code Templates

### Entity Template
```python
import abc
from src.shared.helpers.errors.domain_errors import EntityError

class {Entity}(abc.ABC):
    # Define attributes
    name: str
    {entity}_id: int
    
    def __init__(self, name: str, {entity}_id: int = None):
        if not {Entity}.validate_name(name):
            raise EntityError("name")
        self.name = name
        
        if type({entity}_id) == int:
            if {entity}_id < 0:
                raise EntityError("{entity}_id")
        if type({entity}_id) != int and {entity}_id is not None:
            raise EntityError("{entity}_id")
        self.{entity}_id = {entity}_id
    
    @staticmethod
    def validate_name(name: str) -> bool:
        if name is None:
            return False
        elif type(name) != str:
            return False
        elif len(name) < 2:
            return False
        return True
    
    def __repr__(self):
        return f"{Entity}(name={self.name}, {entity}_id={self.{entity}_id})"
```

### Repository Interface Template
```python
from abc import ABC, abstractmethod
from typing import List
from src.shared.domain.entities.{entity} import {Entity}

class I{Entity}Repository(ABC):
    
    @abstractmethod
    def get_{entity}(self, {entity}_id: int) -> {Entity}:
        """If not found raise NoItemsFound"""
        pass
    
    @abstractmethod
    def get_all_{entity}(self) -> List[{Entity}]:
        pass
    
    @abstractmethod
    def create_{entity}(self, new_{entity}: {Entity}) -> {Entity}:
        pass
    
    @abstractmethod
    def update_{entity}(self, {entity}_id: int, new_name: str) -> {Entity}:
        """If not found raise NoItemsFound"""
        pass
    
    @abstractmethod
    def delete_{entity}(self, {entity}_id: int) -> {Entity}:
        """If not found raise NoItemsFound"""
        pass
    
    @abstractmethod
    def get_{entity}_counter(self) -> int:
        """Returns the number of all {entity}s ever created"""
        pass
```

### Use Case Template
```python
from src.shared.domain.entities.{entity} import {Entity}
from src.shared.domain.repositories.{entity}_repository_interface import I{Entity}Repository
from src.shared.helpers.errors.domain_errors import EntityError

class {Action}{Entity}Usecase:
    
    def __init__(self, repo: I{Entity}Repository):
        self.repo = repo
    
    def __call__(self, name: str) -> {Entity}:
        # Validate inputs
        if not {Entity}.validate_name(name):
            raise EntityError("name")
        
        # Create entity
        {entity} = {Entity}(name=name)
        
        # Persist through repository
        return self.repo.create_{entity}({entity})
```

### Controller Template
```python
from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .{action}_{entity}_usecase import {Action}{Entity}Usecase
from .{action}_{entity}_viewmodel import {Action}{Entity}Viewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.external_interfaces.http_codes import Created, NotFound, BadRequest, InternalServerError

class {Action}{Entity}Controller:
    
    def __init__(self, usecase: {Action}{Entity}Usecase):
        self.{Action}{Entity}Usecase = usecase
    
    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Validate required parameters
            if request.data.get('name') is None:
                raise MissingParameters('name')
            
            # Call use case
            {entity} = self.{Action}{Entity}Usecase(
                name=request.data.get('name')
            )
            
            # Create view model and return
            viewmodel = {Action}{Entity}Viewmodel({entity})
            return Created(viewmodel.to_dict())
        
        except NoItemsFound as err:
            return NotFound(body=err.message)
        except MissingParameters as err:
            return BadRequest(body=err.message)
        except WrongTypeParameter as err:
            return BadRequest(body=err.message)
        except EntityError as err:
            return BadRequest(body=err.message)
        except Exception as err:
            return InternalServerError(body=err.args[0])
```

### Presenter Template
```python
from .{action}_{entity}_controller import {Action}{Entity}Controller
from .{action}_{entity}_usecase import {Action}{Entity}Usecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

repo = Environments.get_{entity}_repo()()
usecase = {Action}{Entity}Usecase(repo)
controller = {Action}{Entity}Controller(usecase)

def lambda_handler(event, context):
    from pprint import pprint
    pprint(event)
    
    httpRequest = LambdaHttpRequest(data=event)
    response = controller(httpRequest)
    httpResponse = LambdaHttpResponse(
        status_code=response.status_code,
        body=response.body,
        headers=response.headers
    )
    
    return httpResponse.toDict()
```

## Error Handling Rules

### Always Handle These Exceptions in Controllers
1. `NoItemsFound` → 404 Not Found
2. `MissingParameters` → 400 Bad Request
3. `WrongTypeParameter` → 400 Bad Request
4. `EntityError` → 400 Bad Request
5. `Exception` → 500 Internal Server Error

### HTTP Status Codes
- **200 OK**: Successful GET, UPDATE, DELETE
- **201 Created**: Successful CREATE
- **400 Bad Request**: Validation errors
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Unexpected errors

## Validation Rules

### Entity Validation
- All validation in entity as static methods
- Raise `EntityError` for invalid data
- Validate in both entity constructor and use case

### Controller Validation
- Check for missing required parameters first
- Check parameter types second
- Let use case handle business validation

## DynamoDB Patterns

### Key Structure
- **Partition Key (PK)**: `{ENTITY}#{id}` (e.g., `PRODUCT#123`)
- **Sort Key (SK)**: `{ENTITY}#{id}` (e.g., `PRODUCT#123`)
- **Counter Key**: `{ENTITY}_COUNTER` for both PK and SK

### DTO Conversion Methods (Required)
- `from_entity(entity)` → DTO
- `to_entity()` → Entity
- `to_dynamo()` → dict
- `from_dynamo(data)` → DTO

## Testing Requirements

### Test Each Layer
1. **Entity Tests**: Validation rules, edge cases
2. **Repository Tests**: CRUD operations, error cases
3. **Use Case Tests**: Business logic, validation
4. **Controller Tests**: HTTP handling, error mapping
5. **View Model Tests**: Data transformation

### Use Mock Repository
- Always use mock repository for unit tests
- Only use DynamoDB repository for integration tests

## CDK Integration

### Adding Lambda Function
```python
# In iac/iac/lambda_stack.py __init__ method

self.{action}_{entity}_function = self.create_lambda_api_gateway_integration(
    module_name="{action}_{entity}",
    method="POST",  # or "GET"
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

# Add to permissions list
self.functions_that_need_dynamo_permissions.append(
    self.{action}_{entity}_function
)
```

## Documentation Requirements

### Docstrings Required For
- All repository interface methods
- All use case `__call__` methods
- All public methods in entities

### Docstring Format
```python
def method_name(self, param: type) -> return_type:
    """
    Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
        
    Raises:
        ExceptionType: When this exception is raised
    """
```

## Reference Documentation

For detailed implementation examples and explanations, refer to:
- `docs/FEATURE_IMPLEMENTATION_GUIDE.md` - Complete step-by-step guide
- `docs/ARCHITECTURE.md` - Architecture details
- `docs/PROJECT_STRUCTURE.md` - Project organization

## Quick Reference: File Locations

```
src/
├── shared/
│   ├── domain/
│   │   ├── entities/{entity}.py
│   │   ├── enums/{enum}_enum.py
│   │   └── repositories/{entity}_repository_interface.py
│   └── infra/
│       ├── dto/{entity}_dynamo_dto.py
│       └── repositories/
│           ├── {entity}_repository_dynamo.py
│           └── {entity}_repository_mock.py
└── modules/
    └── {feature_name}/
        └── app/
            ├── {feature_name}_usecase.py
            ├── {feature_name}_controller.py
            ├── {feature_name}_viewmodel.py
            └── {feature_name}_presenter.py
```

## Common Mistakes to Avoid

1. ❌ **Don't** import infrastructure in domain layer
2. ❌ **Don't** put business logic in controllers
3. ❌ **Don't** return DTOs from use cases (return entities)
4. ❌ **Don't** skip validation in use cases
5. ❌ **Don't** forget to add functions to DynamoDB permissions list
6. ❌ **Don't** use different naming conventions
7. ❌ **Don't** skip writing tests
8. ❌ **Don't** forget to handle all exception types in controllers

## Checklist Before Committing

- [ ] All files follow naming conventions
- [ ] Entity has validation methods
- [ ] Repository interface defined
- [ ] Both DynamoDB and Mock repositories implemented
- [ ] Use case validates inputs
- [ ] Controller handles all exceptions
- [ ] View model has `to_dict()` method
- [ ] Presenter uses `Environments.get_{entity}_repo()`
- [ ] Lambda function added to CDK stack
- [ ] Function added to DynamoDB permissions
- [ ] Tests written for all components
- [ ] All tests pass: `pytest`
- [ ] Docstrings added to public methods

---

**Remember**: Clean Architecture is about separation of concerns and dependency management. When in doubt, ask: "Does this dependency point inward?" If not, refactor.
