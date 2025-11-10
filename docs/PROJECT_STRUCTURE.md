# Project Structure Documentation

## Overview

This document provides a comprehensive overview of the **clean_mss_template** project structure, a microservice template built with Clean Architecture principles for AWS Lambda.

## Project Type

**AWS Lambda Microservice with Clean Architecture**

A serverless microservice template designed for building scalable, maintainable applications using AWS Lambda, API Gateway, and DynamoDB, following Clean Architecture patterns.

---

## Technology Stack

### Backend
- **Runtime**: Python 3.9
- **Framework**: AWS Lambda
- **API Gateway**: AWS API Gateway (REST API)
- **Database**: Amazon DynamoDB
- **Infrastructure as Code**: AWS CDK (Cloud Development Kit) 2.25.0
- **Observability**: AWS X-Ray + AWS Lambda Powertools 2.9.0

### Development & Testing
- **Testing Framework**: pytest 6.2.5
- **Code Coverage**: pytest-cov 4.0.0
- **Local Development**: Docker Compose (DynamoDB Local)
- **Environment Management**: python-dotenv 0.21.0

### AWS SDK & Tools
- **boto3**: 1.24.88 (AWS SDK for Python)
- **aws-xray-sdk**: 2.11.0 (Distributed tracing)

---

## Architecture Patterns

The project implements several key design patterns:

1. **Clean Architecture**: Separation of concerns with distinct layers (Domain, Use Cases, Interface Adapters, Frameworks)
2. **Repository Pattern**: Abstract data access through interfaces
3. **Use Case Pattern**: Business logic encapsulated in use cases
4. **Controller-Presenter Pattern**: Request handling and response formatting
5. **Dependency Injection**: Loose coupling through interface-based dependencies

---

## Directory Structure

```
.
├── .github/                    # GitHub Actions CI/CD workflows
│   └── workflows/
│       ├── CI.yml             # Continuous Integration
│       ├── CD.yml             # Continuous Deployment
│       └── CREATE_PR.yml      # Pull Request automation
│
├── docs/                       # Project documentation
│   ├── architecture_diagram.drawio
│   └── architecture_diagram.png
│
├── iac/                        # Infrastructure as Code (AWS CDK)
│   ├── iac/                   # CDK stack definitions
│   │   ├── lambda_stack.py    # Lambda functions and API Gateway
│   │   ├── template_stack.py  # Main stack orchestration
│   │   └── template_dynamo_table.py  # DynamoDB table definition
│   ├── local/                 # Local development setup
│   │   ├── docker-compose.yml # DynamoDB Local container
│   │   └── configure_dynamodb.md
│   ├── app.py                 # CDK app entry point
│   ├── cdk.json              # CDK configuration
│   ├── adjust_layer_directory.py  # Lambda layer preparation
│   └── requirements.txt       # CDK dependencies
│
├── src/                        # Application source code
│   ├── modules/               # Feature modules (Lambda handlers)
│   │   ├── create_user/
│   │   │   └── app/
│   │   │       ├── create_user_controller.py
│   │   │       ├── create_user_usecase.py
│   │   │       ├── create_user_presenter.py  # Lambda handler
│   │   │       └── create_user_viewmodel.py
│   │   ├── get_user/
│   │   ├── get_all_users/
│   │   ├── update_user/
│   │   └── delete_user/
│   │
│   └── shared/                # Shared code across modules
│       ├── domain/            # Business entities and rules
│       │   ├── entities/      # Domain entities (User)
│       │   ├── enums/         # Domain enumerations (STATE)
│       │   ├── repositories/  # Repository interfaces
│       │   └── observability/ # Observability interfaces
│       │
│       ├── helpers/           # Utility functions and classes
│       │   ├── enum/          # HTTP status codes
│       │   ├── errors/        # Custom error classes
│       │   └── external_interfaces/  # HTTP request/response models
│       │
│       ├── infra/             # Infrastructure implementations
│       │   ├── dto/           # Data Transfer Objects
│       │   ├── repositories/  # Repository implementations
│       │   │   ├── user_repository_dynamo.py
│       │   │   └── user_repository_mock.py
│       │   └── external/      # External service integrations
│       │       ├── dynamo/    # DynamoDB client
│       │       └── observability/  # X-Ray implementation
│       │
│       └── environments.py    # Environment configuration
│
└── tests/                      # Test suite
    ├── modules/               # Module-specific tests
    │   ├── create_user/
    │   ├── get_user/
    │   ├── get_all_users/
    │   ├── update_user/
    │   └── delete_user/
    └── shared/                # Shared code tests
        ├── domain/
        └── infra/
```

---

## Core Components

### 1. Domain Layer (`src/shared/domain/`)

The innermost layer containing business logic and rules.

**Entities** (`entities/`)
- `user.py`: User entity with validation logic
  - Properties: name, email, state, user_id
  - Validation: email format, name length

**Enums** (`enums/`)
- `state_enum.py`: User state enumeration (PENDING, APPROVED, etc.)

**Repository Interfaces** (`repositories/`)
- `user_repository_interface.py`: Abstract repository contract
  - Methods: get_user, get_all_user, create_user, update_user, delete_user

**Observability Interfaces** (`observability/`)
- `observability_interface.py`: Tracing and monitoring contract

### 2. Use Case Layer (`src/modules/*/app/*_usecase.py`)

Business logic orchestration for each feature.

**Example: CreateUserUsecase**
- Validates input data
- Creates User entity
- Calls repository to persist
- Returns created user

### 3. Interface Adapters Layer

**Controllers** (`*_controller.py`)
- Parse HTTP requests
- Call use cases
- Handle errors
- Return HTTP responses

**Presenters** (`*_presenter.py`)
- Lambda handler entry point
- Initialize dependencies
- Convert Lambda events to HTTP requests
- Format responses for API Gateway

**ViewModels** (`*_viewmodel.py`)
- Transform domain entities to API responses
- Add presentation-specific fields

### 4. Infrastructure Layer (`src/shared/infra/`)

**Repositories** (`repositories/`)
- `user_repository_dynamo.py`: DynamoDB implementation
- `user_repository_mock.py`: In-memory implementation for testing

**DTOs** (`dto/`)
- `user_dynamo_dto.py`: DynamoDB data mapping

**External Services** (`external/`)
- `dynamo/dynamo_table.py`: DynamoDB client wrapper
- `observability/observability_aws.py`: AWS X-Ray integration

### 5. Infrastructure as Code (`iac/`)

**CDK Stacks**
- `template_stack.py`: Main stack with API Gateway
- `lambda_stack.py`: Lambda functions and integrations
- `template_dynamo_table.py`: DynamoDB table definition

**Configuration**
- Environment-based deployment (DEV, HOMOLOG, PROD)
- Automatic tagging and resource naming
- Lambda layer management

---

## API Modules

Each module follows the same structure:

### Create User
- **Endpoint**: POST /mss-template/create-user
- **Purpose**: Create a new user with name and email
- **Parameters**: name (string), email (string)

### Get User
- **Endpoint**: GET /mss-template/get-user
- **Purpose**: Retrieve a user by ID
- **Parameters**: user_id (integer)

### Get All Users
- **Endpoint**: GET /mss-template/get-all-users
- **Purpose**: Retrieve all users
- **Parameters**: None

### Update User
- **Endpoint**: POST /mss-template/update-user
- **Purpose**: Update user information
- **Parameters**: user_id (integer), new_name (string)

### Delete User
- **Endpoint**: POST /mss-template/delete-user
- **Purpose**: Delete a user by ID
- **Parameters**: user_id (integer)

---

## Key Features

1. **Clean Architecture Implementation**
   - Clear separation of concerns
   - Dependency inversion principle
   - Testable business logic

2. **AWS Lambda Functions**
   - Serverless compute
   - API Gateway integration
   - Lambda Powertools for observability

3. **DynamoDB Integration**
   - NoSQL data persistence
   - Single-table design
   - Local development support

4. **Mock Repositories**
   - In-memory testing
   - No external dependencies for tests
   - Fast test execution

5. **Infrastructure as Code**
   - AWS CDK for deployment
   - Version-controlled infrastructure
   - Multi-environment support

6. **Local Development**
   - Docker Compose for DynamoDB Local
   - Environment-based configuration
   - Easy setup and testing

7. **Observability**
   - AWS X-Ray distributed tracing
   - Lambda Powertools metrics
   - Structured logging

8. **Comprehensive Testing**
   - pytest framework
   - Unit tests for all layers
   - Code coverage reporting

---

## Dependencies

### Production Dependencies
```
aws-lambda-powertools==2.9.0
aws-xray-sdk==2.11.0
boto3==1.24.88
```

### Development Dependencies
```
pytest==6.2.5
pytest-cov==4.0.0
python-dotenv==0.21.0
```

### Infrastructure Dependencies
```
aws-cdk-lib==2.25.0
constructs>=10.0.0,<11.0.0
```

---

## Environment Configuration

The project supports multiple stages:

- **TEST**: Local development with mocks
- **DEV**: Development environment
- **HOMOLOG**: Staging/homologation environment
- **PROD**: Production environment

Configuration is managed through:
- Environment variables
- `.env` file for local development
- CDK context for infrastructure

---

## Naming Conventions

### Files and Directories
- snake_case (e.g., `create_user_controller.py`)
- Files named after classes they contain

### Classes
- CamelCase (e.g., `CreateUserController`)
- Interfaces start with "I" (e.g., `IUserRepository`)
- Repositories end with type (e.g., `UserRepositoryMock`, `UserRepositoryDynamo`)
- Controllers end with "Controller"
- Use cases end with "Usecase"
- ViewModels end with "Viewmodel"
- Presenters end with "Presenter"

### Methods and Variables
- snake_case
- Methods use verbs (e.g., `create_user`, `get_user`)
- Variables avoid verbs

### Enums
- SNAKE_CASE (e.g., `STATE_ENUM`)

### Tests
- snake_case
- Prefix with "test_" (e.g., `test_create_user_valid`)

---

## CI/CD Pipeline

### Continuous Integration (CI.yml)
- Run tests on pull requests
- Code coverage reporting
- Linting and formatting checks

### Continuous Deployment (CD.yml)
- Automated deployment to AWS
- Environment-specific deployments
- Infrastructure updates via CDK

### Pull Request Automation (CREATE_PR.yml)
- Automated PR creation
- Branch management

---

## Contributors

This template was created by the Dev. Community Mauá team:
- Bruno Vilardi
- Hector Guerrini
- João Branco
- Vitor Soller
- Lucas Duez
- Rodrigo Morales
- Lucas Milani
- Rafael Rubio

---

## References

- [Clean Architecture by Robert C. Martin](https://www.amazon.com.br/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164)
- [Clean Architecture Figma Diagram](https://www.figma.com/file/CmfQcH2xbZyIszPX0iOxPp/Clean-Arch---HackaBeckas)
- [Dev. Community Mauá](https://www.instagram.com/devcommunitymaua/)
- [Institute Mauá of Technology](https://www.maua.br/)
