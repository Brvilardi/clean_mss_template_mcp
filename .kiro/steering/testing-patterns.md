# Testing Patterns and Standards for Kiro Agent

This steering file provides mandatory rules for writing tests in the Clean MSS Template project. Always follow these guidelines when creating or modifying tests.

## Core Testing Principles

1. **Test each layer independently**: Entity, Repository, Use Case, Controller, View Model, Presenter
2. **Use mock repositories for unit tests**: Only use DynamoDB repositories for integration tests
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Test happy path first**: Then test error cases
5. **Descriptive test names**: Use clear, descriptive method names that explain what is being tested

## Test Structure and Organization

### Directory Structure (Mirror Source Code)
```
tests/
├── modules/
│   └── {feature_name}/
│       └── app/
│           ├── test_{feature_name}_controller.py
│           ├── test_{feature_name}_usecase.py
│           ├── test_{feature_name}_viewmodel.py
│           └── test_{feature_name}_presenter.py
└── shared/
    ├── domain/
    │   └── entities/
    │       └── test_{entity}.py
    └── infra/
        ├── dto/
        │   └── test_{entity}_dynamo_dto.py
        └── repositories/
            ├── test_{entity}_repository_dynamo.py
            └── test_{entity}_repository_mock.py
```

### Test File Naming
- **Pattern**: `test_{module_name}.py`
- **Examples**: `test_user.py`, `test_create_user_controller.py`, `test_user_dynamo_dto.py`

### Test Class Naming
- **Pattern**: `Test_{ClassName}` (with underscore)
- **Examples**: `Test_User`, `Test_CreateUserController`, `Test_UserDynamoDTO`

### Test Method Naming
- **Pattern**: `test_{what_is_being_tested}_{scenario}`
- **Examples**: 
  - `test_create_user` (happy path)
  - `test_create_user_invalid_name` (error case)
  - `test_create_user_controller_missing_email` (specific error)

## Layer-Specific Testing Patterns

### 1. Entity Tests (`tests/shared/domain/entities/`)

**Purpose**: Test entity validation logic and business rules

**Pattern**:
```python
from src.shared.domain.entities.{entity} import {Entity}
from src.shared.helpers.errors.domain_errors import EntityError
import pytest


class Test_{Entity}:
    def test_{entity}(self):
        """Test creating a valid entity"""
        entity = {Entity}(
            name="Valid Name",
            {entity}_id=1
        )
        assert entity.name == "Valid Name"
        assert entity.{entity}_id == 1
    
    def test_{entity}_name_is_none(self):
        """Test entity constructor with None name"""
        with pytest.raises(EntityError):
            {Entity}(name=None, {entity}_id=1)
    
    def test_{entity}_name_is_not_str(self):
        """Test entity constructor with non-string name"""
        with pytest.raises(EntityError):
            {Entity}(name=123, {entity}_id=1)
    
    def test_{entity}_name_is_shorter_than_min_length(self):
        """Test entity constructor with name shorter than minimum"""
        with pytest.raises(EntityError):
            {Entity}(name="A", {entity}_id=1)
    
    def test_validate_name_valid(self):
        """Test validate_name with valid input"""
        assert {Entity}.validate_name("Valid Name") is True
    
    def test_validate_name_none(self):
        """Test validate_name with None"""
        assert {Entity}.validate_name(None) is False
```

**Requirements**:
- Test happy path first
- Test each validation method separately
- Test each field validation in constructor
- Use `pytest.raises(EntityError)` for validation failures
- Include docstrings for complex tests
- Test static validation methods directly
- Test edge cases (empty strings, zero values, boundary conditions)

### 2. Repository Mock Tests (`tests/shared/infra/repositories/`)

**Purpose**: Test mock repository CRUD operations

**Pattern**:
```python
from src.shared.domain.entities.{entity} import {Entity}
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.infra.repositories.{entity}_repository_mock import {Entity}RepositoryMock
import pytest


class Test_{Entity}RepositoryMock:
    def test_get_{entity}(self):
        """Test retrieving an entity by ID"""
        repo = {Entity}RepositoryMock()
        entity = repo.get_{entity}(1)
        
        assert entity.name == "Expected Name"
        assert entity.{entity}_id == 1
    
    def test_get_{entity}_not_found(self):
        """Test retrieving non-existent entity raises NoItemsFound"""
        repo = {Entity}RepositoryMock()
        with pytest.raises(NoItemsFound):
            entity = repo.get_{entity}(999)
    
    def test_get_all_{entity}(self):
        """Test retrieving all entities"""
        repo = {Entity}RepositoryMock()
        entities = repo.get_all_{entity}()
        assert len(entities) == 3
    
    def test_create_{entity}(self):
        """Test creating a new entity"""
        repo = {Entity}RepositoryMock()
        entity = {Entity}(name="New Entity", {entity}_id=4)
        
        created = repo.create_{entity}(entity)
        
        assert repo.{entity}s[-1].name == "New Entity"
        assert repo.{entity}s[-1].{entity}_id == 4
        assert repo.{entity}_counter == 4
    
    def test_delete_{entity}(self):
        """Test deleting an entity"""
        repo = {Entity}RepositoryMock()
        deleted = repo.delete_{entity}(1)
        
        assert deleted.name == "Expected Name"
        assert deleted.{entity}_id == 1
    
    def test_delete_{entity}_not_found(self):
        """Test deleting non-existent entity raises NoItemsFound"""
        repo = {Entity}RepositoryMock()
        with pytest.raises(NoItemsFound):
            repo.delete_{entity}(999)
    
    def test_update_{entity}(self):
        """Test updating an entity"""
        repo = {Entity}RepositoryMock()
        updated = repo.update_{entity}(1, "Updated Name")
        
        assert updated.name == "Updated Name"
        assert repo.{entity}s[0].name == "Updated Name"
    
    def test_update_{entity}_not_found(self):
        """Test updating non-existent entity raises NoItemsFound"""
        repo = {Entity}RepositoryMock()
        with pytest.raises(NoItemsFound):
            repo.update_{entity}(999, "Updated Name")
    
    def test_get_{entity}_counter(self):
        """Test retrieving entity counter"""
        repo = {Entity}RepositoryMock()
        assert repo.get_{entity}_counter() == 3
```

**Requirements**:
- Test all CRUD operations
- Test both success and failure cases
- Always test `NoItemsFound` exceptions
- Verify counter increments on create
- Verify data persistence in mock storage
- Include docstrings for clarity

### 3. Repository DynamoDB Tests (`tests/shared/infra/repositories/`)

**Purpose**: Test DynamoDB repository integration (requires DynamoDB)

**Pattern**:
```python
import os
import pytest
from src.shared.infra.repositories.{entity}_repository_dynamo import {Entity}RepositoryDynamo
from src.shared.infra.repositories.{entity}_repository_mock import {Entity}RepositoryMock


class Test_{Entity}RepositoryDynamo:
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_create_{entity}(self):
        os.environ["STAGE"] = "TEST"
        
        repo = {Entity}RepositoryDynamo()
        repo_mock = {Entity}RepositoryMock()
        result = repo.create_{entity}(repo_mock.{entity}s[0])
        
        assert repo_mock.{entity}s[0].name == result.name
    
    @pytest.mark.skip(reason="Needs dynamoDB")
    def test_get_{entity}(self):
        os.environ["STAGE"] = "TEST"
        
        repo = {Entity}RepositoryDynamo()
        repo_mock = {Entity}RepositoryMock()
        result = repo.get_{entity}(1)
        
        assert repo_mock.{entity}s[0].name == result.name
```

**Requirements**:
- **ALWAYS** use `@pytest.mark.skip(reason="Needs dynamoDB")` decorator
- Set `os.environ["STAGE"] = "TEST"` at the start of each test
- Use mock repository for expected data comparison
- Test all CRUD operations
- These tests are for integration testing only

### 4. DTO Tests (`tests/shared/infra/dto/`)

**Purpose**: Test data transformation between entities and DynamoDB format

**Pattern**:
```python
from decimal import Decimal
from src.shared.domain.entities.{entity} import {Entity}
from src.shared.infra.dto.{entity}_dynamo_dto import {Entity}DynamoDTO
from src.shared.infra.repositories.{entity}_repository_mock import {Entity}RepositoryMock


class Test_{Entity}DynamoDTO:
    def test_from_entity(self):
        """Test converting entity to DTO"""
        repo = {Entity}RepositoryMock()
        
        dto = {Entity}DynamoDTO.from_entity({entity}=repo.{entity}s[0])
        
        expected_dto = {Entity}DynamoDTO(
            name=repo.{entity}s[0].name,
            {entity}_id=repo.{entity}s[0].{entity}_id
        )
        
        assert dto == expected_dto
    
    def test_to_dynamo(self):
        """Test converting DTO to DynamoDB format"""
        repo = {Entity}RepositoryMock()
        
        dto = {Entity}DynamoDTO.from_entity({entity}=repo.{entity}s[0])
        dynamo_dict = dto.to_dynamo()
        
        expected_dict = {
            "entity": "{entity}",
            "name": repo.{entity}s[0].name,
            "{entity}_id": repo.{entity}s[0].{entity}_id
        }
        
        assert dynamo_dict == expected_dict
        assert dynamo_dict["entity"] == "{entity}"
    
    def test_from_dynamo(self):
        """Test converting DynamoDB format to DTO"""
        dynamo_dict = {
            "entity": "{entity}",
            "{entity}_id": Decimal('1'),
            "name": "Test Name",
            "PK": "{entity}#1",
            "SK": "#1"
        }
        
        dto = {Entity}DynamoDTO.from_dynamo({entity}_data=dynamo_dict)
        
        expected_dto = {Entity}DynamoDTO(
            name="Test Name",
            {entity}_id=1
        )
        
        assert dto == expected_dto
    
    def test_to_entity(self):
        """Test converting DTO to entity"""
        repo = {Entity}RepositoryMock()
        
        dto = {Entity}DynamoDTO.from_entity({entity}=repo.{entity}s[0])
        entity = dto.to_entity()
        
        assert entity.name == repo.{entity}s[0].name
        assert entity.{entity}_id == repo.{entity}s[0].{entity}_id
    
    def test_from_dynamo_to_entity(self):
        """Test full conversion from DynamoDB to entity"""
        dynamo_dict = {
            "entity": "{entity}",
            "{entity}_id": Decimal('1'),
            "name": "Test Name"
        }
        
        dto = {Entity}DynamoDTO.from_dynamo({entity}_data=dynamo_dict)
        entity = dto.to_entity()
        
        expected_entity = {Entity}(name="Test Name", {entity}_id=1)
        
        assert entity.name == expected_entity.name
        assert entity.{entity}_id == expected_entity.{entity}_id
    
    def test_from_entity_to_dynamo(self):
        """Test full conversion from entity to DynamoDB"""
        repo = {Entity}RepositoryMock()
        
        dto = {Entity}DynamoDTO.from_entity({entity}=repo.{entity}s[0])
        dynamo_dict = dto.to_dynamo()
        
        expected_dict = {
            "entity": "{entity}",
            "name": repo.{entity}s[0].name,
            "{entity}_id": repo.{entity}s[0].{entity}_id
        }
        
        assert dynamo_dict == expected_dict
    
    def test_entity_attribute_always_{entity}(self):
        """Test that entity attribute is always '{entity}' in DynamoDB format"""
        repo = {Entity}RepositoryMock()
        
        for entity in repo.{entity}s:
            dto = {Entity}DynamoDTO.from_entity({entity}=entity)
            dynamo_dict = dto.to_dynamo()
            
            assert dynamo_dict["entity"] == "{entity}"
```

**Requirements**:
- Test all four conversion methods: `from_entity`, `to_dynamo`, `from_dynamo`, `to_entity`
- Test round-trip conversions: entity → DTO → DynamoDB and DynamoDB → DTO → entity
- Always verify the "entity" field in DynamoDB format
- Use `Decimal` type for numeric fields from DynamoDB (DynamoDB returns Decimals)
- Use mock repository for test data
- Include docstrings for each test

### 5. Use Case Tests (`tests/modules/{feature_name}/app/`)

**Purpose**: Test business logic and validation

**Pattern**:
```python
import pytest
from src.modules.{action}_{entity}.app.{action}_{entity}_usecase import {Action}{Entity}Usecase
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.repositories.{entity}_repository_mock import {Entity}RepositoryMock


class Test_{Action}{Entity}Usecase:
    def test_{action}_{entity}(self):
        """Test successful {action} operation"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo)
        
        entity = usecase(name="Valid Name")
        
        assert repo.{entity}s[-1] == entity
    
    def test_{action}_{entity}_invalid_name(self):
        """Test {action} with invalid name raises EntityError"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo)
        
        with pytest.raises(EntityError):
            usecase(name="A")
    
    def test_{action}_{entity}_invalid_email(self):
        """Test {action} with invalid email raises EntityError"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo)
        
        with pytest.raises(EntityError):
            usecase(name="Valid Name", email="invalid-email")
```

**Requirements**:
- Test happy path first
- Test all validation scenarios
- Use `pytest.raises(EntityError)` for validation failures
- Verify repository state changes
- Use mock repository only
- Include docstrings

### 6. Controller Tests (`tests/modules/{feature_name}/app/`)

**Purpose**: Test HTTP request/response handling and error mapping

**Pattern**:
```python
from src.modules.{action}_{entity}.app.{action}_{entity}_controller import {Action}{Entity}Controller
from src.modules.{action}_{entity}.app.{action}_{entity}_usecase import {Action}{Entity}Usecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.{entity}_repository_mock import {Entity}RepositoryMock


class Test_{Action}{Entity}Controller:
    def test_{action}_{entity}_controller(self):
        """Test successful {action} request"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo=repo)
        controller = {Action}{Entity}Controller(usecase=usecase)
        
        request = HttpRequest(body={
            'name': 'Valid Name',
            'email': 'valid@email.com'
        })
        
        response = controller(request=request)
        
        assert response.status_code == 201
        assert response.body['name'] == repo.{entity}s[-1].name
        assert response.body['message'] == "the {entity} was created successfully"
    
    def test_{action}_{entity}_controller_missing_name(self):
        """Test request with missing name returns 400"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo=repo)
        controller = {Action}{Entity}Controller(usecase=usecase)
        
        request = HttpRequest(body={'email': 'valid@email.com'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field name is missing"
    
    def test_{action}_{entity}_controller_invalid_name(self):
        """Test request with invalid name returns 400"""
        repo = {Entity}RepositoryMock()
        usecase = {Action}{Entity}Usecase(repo=repo)
        controller = {Action}{Entity}Controller(usecase=usecase)
        
        request = HttpRequest(body={
            'name': 'A',
            'email': 'valid@email.com'
        })
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field name is not valid"
```

**Requirements**:
- Test happy path with 200/201 status code
- Test all missing parameter scenarios (400)
- Test all invalid parameter scenarios (400)
- Test not found scenarios (404) for GET/UPDATE/DELETE
- Verify response body structure
- Verify response status codes
- Use HttpRequest for request construction
- Include docstrings

**HTTP Status Code Mapping**:
- `201 Created`: Successful CREATE
- `200 OK`: Successful GET, UPDATE, DELETE
- `400 Bad Request`: Missing parameters, invalid parameters, validation errors
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Unexpected errors

### 7. View Model Tests (`tests/modules/{feature_name}/app/`)

**Purpose**: Test data transformation for API responses

**Pattern**:
```python
from src.modules.{action}_{entity}.app.{action}_{entity}_viewmodel import {Action}{Entity}Viewmodel
from src.shared.domain.entities.{entity} import {Entity}


class Test_{Action}{Entity}Viewmodel:
    def test_{action}_{entity}_viewmodel(self):
        """Test view model transformation"""
        entity = {Entity}(
            {entity}_id=1,
            name="Test Name",
            email="test@email.com"
        )
        
        viewmodel = {Action}{Entity}Viewmodel({entity}=entity).to_dict()
        
        expected = {
            '{entity}_id': 1,
            'name': 'Test Name',
            'email': 'test@email.com',
            'message': 'the {entity} was created successfully'
        }
        
        assert viewmodel == expected
```

**Requirements**:
- Test `to_dict()` method
- Verify all fields are present in output
- Verify message field is correct
- Test with different entity states if applicable
- Include docstrings

### 8. Presenter Tests (`tests/modules/{feature_name}/app/`)

**Purpose**: Test Lambda handler integration

**Pattern**:
```python
import json
from src.modules.{action}_{entity}.app.{action}_{entity}_presenter import lambda_handler


class Test_{Action}{Entity}Presenter:
    def test_{action}_{entity}(self):
        """Test Lambda handler with valid event"""
        event = {
            "version": "2.0",
            "routeKey": "$default",
            "rawPath": "/my/path",
            "headers": {
                "header1": "value1"
            },
            "requestContext": {
                "accountId": "123456789012",
                "apiId": "<urlid>",
                "domainName": "<url-id>.lambda-url.us-west-2.on.aws",
                "http": {
                    "method": "POST",
                    "path": "/my/path",
                    "protocol": "HTTP/1.1",
                    "sourceIp": "123.123.123.123",
                    "userAgent": "agent"
                },
                "requestId": "id",
                "routeKey": "$default",
                "stage": "$default",
                "time": "12/Mar/2020:19:03:58 +0000",
                "timeEpoch": 1583348638390
            },
            "body": '{"name":"Test Name", "email":"test@email.com"}',
            "isBase64Encoded": False
        }
        
        response = lambda_handler(event, None)
        
        assert response["statusCode"] == 201
        assert json.loads(response["body"])["message"] == "the {entity} was created successfully"
```

**Requirements**:
- Test with realistic Lambda event structure
- Use `json.loads()` to parse response body
- Verify status code
- Verify response message
- Include docstrings
- Test only happy path (error cases covered in controller tests)

## Special Testing Scenarios

### Testing with Empty Repositories
```python
def test_get_all_{entity}_empty_repository(self):
    """Test retrieving entities from empty repository"""
    repo = {Entity}RepositoryMock()
    repo.{entity}s = []  # Clear pre-populated data
    usecase = GetAll{Entity}Usecase(repo)
    
    entities = usecase()
    
    assert len(entities) == 0
    assert entities == []
```

### Testing with Complex Data Structures
```python
def test_{entity}_with_empty_lists(self):
    """Test entity with empty list fields"""
    entity = {Entity}(
        name="Test",
        speakers=[],
        topics=[],
        features=[]
    )
    
    assert entity.speakers == []
    assert entity.topics == []
```

### Testing Validation Methods Directly
```python
def test_validate_datetime_valid_iso8601(self):
    """Test validate_datetime with valid ISO 8601 format"""
    assert Session.validate_datetime("2025-12-04T21:00:00.000Z") is True

def test_validate_datetime_invalid_format(self):
    """Test validate_datetime with invalid format"""
    assert Session.validate_datetime("12/04/2025") is False
```

## Common Testing Patterns

### Setup Pattern (Arrange-Act-Assert)
```python
def test_create_user(self):
    # Arrange
    repo = UserRepositoryMock()
    usecase = CreateUserUsecase(repo)
    
    # Act
    user = usecase(name="Test User", email="test@test.com")
    
    # Assert
    assert repo.users[-1] == user
```

### Error Testing Pattern
```python
def test_create_user_invalid_email(self):
    repo = UserRepositoryMock()
    usecase = CreateUserUsecase(repo)
    
    with pytest.raises(EntityError):
        usecase(name="Test User", email="invalid-email")
```

### Multiple Assertions Pattern
```python
def test_create_user_controller(self):
    # ... setup ...
    response = controller(request=request)
    
    assert response.status_code == 201
    assert response.body['user_id'] == repo.users[-1].user_id
    assert response.body['name'] == repo.users[-1].name
    assert response.body['message'] == "the user was created successfully"
```

## Testing Checklist

Before committing tests, verify:

- [ ] All test files follow naming convention: `test_{module_name}.py`
- [ ] All test classes follow naming convention: `Test_{ClassName}`
- [ ] All test methods follow naming convention: `test_{what}_{scenario}`
- [ ] Entity tests cover all validation methods
- [ ] Entity tests cover all field validations
- [ ] Repository tests cover all CRUD operations
- [ ] Repository tests test both success and failure cases
- [ ] DTO tests cover all four conversion methods
- [ ] DTO tests verify "entity" field in DynamoDB format
- [ ] Use case tests cover happy path and validation errors
- [ ] Controller tests cover all HTTP status codes
- [ ] Controller tests verify response body structure
- [ ] View model tests verify `to_dict()` output
- [ ] Presenter tests use realistic Lambda event structure
- [ ] DynamoDB tests use `@pytest.mark.skip` decorator
- [ ] All tests use mock repositories (except DynamoDB integration tests)
- [ ] All tests include docstrings for complex scenarios
- [ ] All tests pass: `pytest`

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/modules/create_user/app/test_create_user_controller.py
```

### Run Specific Test Class
```bash
pytest tests/modules/create_user/app/test_create_user_controller.py::Test_CreateUserController
```

### Run Specific Test Method
```bash
pytest tests/modules/create_user/app/test_create_user_controller.py::Test_CreateUserController::test_create_user_controller
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Skip DynamoDB Tests
```bash
pytest -m "not skip"
```

## Common Mistakes to Avoid

1. ❌ **Don't** use DynamoDB repository in unit tests (use mock only)
2. ❌ **Don't** forget to test error cases
3. ❌ **Don't** skip testing validation methods
4. ❌ **Don't** forget docstrings for complex tests
5. ❌ **Don't** test multiple concerns in one test
6. ❌ **Don't** forget to verify response status codes
7. ❌ **Don't** forget to test empty/edge cases
8. ❌ **Don't** forget `@pytest.mark.skip` for DynamoDB tests
9. ❌ **Don't** use real AWS resources in tests
10. ❌ **Don't** forget to test the "entity" field in DTO tests

## Test Coverage Goals

- **Entity**: 100% coverage of validation logic
- **Repository Mock**: 100% coverage of CRUD operations
- **DTO**: 100% coverage of conversion methods
- **Use Case**: 100% coverage of business logic
- **Controller**: 100% coverage of HTTP handling
- **View Model**: 100% coverage of transformation logic
- **Presenter**: Basic integration test (happy path)

---

**Remember**: Good tests are the foundation of maintainable code. Write tests that are clear, focused, and comprehensive.
