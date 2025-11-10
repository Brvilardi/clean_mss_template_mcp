# Feature Implementation Guide

## Overview

This guide provides a step-by-step approach to implementing new features in the Clean MSS Template project following Clean Architecture principles. Use this document as a reference when adding new functionality to ensure consistency and maintainability.

---

## Clean Architecture Layers

Before implementing a feature, understand the four layers and their dependencies:

```
┌─────────────────────────────────────────────────┐
│  4. Frameworks & Drivers (Infrastructure)       │
│     - Database implementations                  │
│     - External services                         │
└─────────────────┬───────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────┐
│  3. Interface Adapters                          │
│     - Controllers, Presenters, ViewModels       │
└─────────────────┬───────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────┐
│  2. Use Cases (Application Business Rules)      │
│     - Feature-specific business logic           │
└─────────────────┬───────────────────────────────┘
                  │ depends on
┌─────────────────▼───────────────────────────────┐
│  1. Domain (Enterprise Business Rules)          │
│     - Entities, Enums, Repository Interfaces    │
└─────────────────────────────────────────────────┘
```

**Key Principle**: Dependencies always point inward. Outer layers depend on inner layers, never the reverse.

---

## Implementation Order

Follow this sequence when implementing a new feature:


### Step 1: Domain Layer (Innermost)
1. Define Entities
2. Define Enums (if needed)
3. Define Repository Interface

### Step 2: Infrastructure Layer
4. Create DTOs (Data Transfer Objects)
5. Implement Repository (DynamoDB)
6. Implement Mock Repository (for testing)

### Step 3: Use Case Layer
7. Create Use Case

### Step 4: Interface Adapters Layer
8. Create ViewModel
9. Create Controller
10. Create Presenter (Lambda Handler)

### Step 5: Infrastructure as Code
11. Add Lambda Function to CDK Stack
12. Configure API Gateway Integration

### Step 6: Testing
13. Write Tests for Each Component

---

## Detailed Implementation Steps


## Step 1: Define Domain Entity

**Location**: `src/shared/domain/entities/`

**Purpose**: Entities represent core business objects with identity and business rules. They are framework-agnostic and contain validation logic.

**Importance**: 
- Encapsulates business rules at the entity level
- Ensures data integrity through validation
- Independent of external frameworks and databases
- Highly testable

**Example**: Creating a `Product` entity

```python
# src/shared/domain/entities/product.py
import abc
from src.shared.helpers.errors.domain_errors import EntityError

class Product(abc.ABC):
    name: str
    price: float
    category: str
    product_id: int
    MIN_NAME_LENGTH = 3
    MIN_PRICE = 0.01

    def __init__(self, name: str, price: float, category: str, product_id: int = None):
        # Validate name
        if not Product.validate_name(name):
            raise EntityError("name")
        self.name = name

        # Validate price
        if not Product.validate_price(price):
            raise EntityError("price")
        self.price = price

        # Validate category
        if not Product.validate_category(category):
            raise EntityError("category")
        self.category = category

        # Validate product_id
        if type(product_id) == int:
            if product_id < 0:
                raise EntityError("product_id")
        if type(product_id) != int and product_id is not None:
            raise EntityError("product_id")
        self.product_id = product_id

    @staticmethod
    def validate_name(name: str) -> bool:
        if name is None:
            return False
        elif type(name) != str:
            return False
        elif len(name) < Product.MIN_NAME_LENGTH:
            return False
        return True

    @staticmethod
    def validate_price(price: float) -> bool:
        if price is None:
            return False
        elif type(price) not in [int, float]:
            return False
        elif price < Product.MIN_PRICE:
            return False
        return True

    @staticmethod
    def validate_category(category: str) -> bool:
        if category is None:
            return False
        elif type(category) != str:
            return False
        elif len(category) < 2:
            return False
        return True

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price}, category={self.category}, product_id={self.product_id})"
```

**Key Points**:
- Use `abc.ABC` for abstract base class
- Include validation methods as static methods
- Raise `EntityError` for invalid data
- Keep business rules within the entity
- No dependencies on external frameworks


---

## Step 2: Define Enums (If Needed)

**Location**: `src/shared/domain/enums/`

**Purpose**: Enums define fixed sets of values that represent domain concepts.

**Importance**:
- Type safety for domain values
- Clear documentation of valid states
- Prevents invalid values

**Example**: Creating a `PRODUCT_STATUS` enum

```python
# src/shared/domain/enums/product_status_enum.py
from enum import Enum

class PRODUCT_STATUS(Enum):
    AVAILABLE = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    DISCONTINUED = "DISCONTINUED"
```

**Naming Convention**: 
- File name: `{name}_enum.py` (e.g., `product_status_enum.py`)
- Class name: SNAKE_CASE (e.g., `PRODUCT_STATUS`)
- Values: SNAKE_CASE

---

## Step 3: Define Repository Interface

**Location**: `src/shared/domain/repositories/`

**Purpose**: Repository interfaces define contracts for data access without specifying implementation details.

**Importance**:
- Dependency inversion: domain doesn't depend on infrastructure
- Allows multiple implementations (DynamoDB, Mock, etc.)
- Makes testing easier with mock implementations
- Clear contract for data operations

**Example**: Creating a `IProductRepository` interface

```python
# src/shared/domain/repositories/product_repository_interface.py
from abc import ABC, abstractmethod
from typing import List
from src.shared.domain.entities.product import Product

class IProductRepository(ABC):

    @abstractmethod
    def get_product(self, product_id: int) -> Product:
        """
        Retrieve a product by ID.
        If product not found, raise NoItemsFound.
        """
        pass

    @abstractmethod
    def get_all_products(self) -> List[Product]:
        """
        Retrieve all products.
        """
        pass

    @abstractmethod
    def create_product(self, new_product: Product) -> Product:
        """
        Create a new product.
        Returns the created product with assigned product_id.
        """
        pass

    @abstractmethod
    def update_product(self, product_id: int, name: str = None, price: float = None, category: str = None) -> Product:
        """
        Update product information.
        If product not found, raise NoItemsFound.
        """
        pass

    @abstractmethod
    def delete_product(self, product_id: int) -> Product:
        """
        Delete a product by ID.
        If product not found, raise NoItemsFound.
        Returns the deleted product.
        """
        pass

    @abstractmethod
    def get_product_counter(self) -> int:
        """
        Returns the total number of products ever created.
        Used for generating new product IDs.
        """
        pass
```

**Key Points**:
- Interface name starts with "I" (e.g., `IProductRepository`)
- All methods are abstract
- Include docstrings explaining behavior
- Specify exceptions to raise
- No implementation details


---

## Step 4: Create DTO (Data Transfer Object)

**Location**: `src/shared/infra/dto/`

**Purpose**: DTOs transform domain entities to/from database format. They handle the mapping between your clean domain model and the database schema.

**Importance**:
- Separates domain model from database schema
- Handles data format conversion
- Encapsulates database-specific logic
- Makes it easy to change database structure without affecting domain

**Example**: Creating a `ProductDynamoDTO`

```python
# src/shared/infra/dto/product_dynamo_dto.py
from src.shared.domain.entities.product import Product

class ProductDynamoDTO:
    pk: str  # Partition key
    sk: str  # Sort key
    name: str
    price: float
    category: str
    product_id: int

    def __init__(self, pk: str, sk: str, name: str, price: float, category: str, product_id: int):
        self.pk = pk
        self.sk = sk
        self.name = name
        self.price = price
        self.category = category
        self.product_id = product_id

    @staticmethod
    def from_entity(product: Product) -> "ProductDynamoDTO":
        """
        Convert domain entity to DTO.
        """
        return ProductDynamoDTO(
            pk=f"PRODUCT#{product.product_id}",
            sk=f"PRODUCT#{product.product_id}",
            name=product.name,
            price=product.price,
            category=product.category,
            product_id=product.product_id
        )

    def to_entity(self) -> Product:
        """
        Convert DTO to domain entity.
        """
        return Product(
            name=self.name,
            price=self.price,
            category=self.category,
            product_id=self.product_id
        )

    def to_dynamo(self) -> dict:
        """
        Convert to DynamoDB item format.
        """
        return {
            "PK": self.pk,
            "SK": self.sk,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "product_id": self.product_id
        }

    @staticmethod
    def from_dynamo(data: dict) -> "ProductDynamoDTO":
        """
        Create DTO from DynamoDB item.
        """
        return ProductDynamoDTO(
            pk=data["PK"],
            sk=data["SK"],
            name=data["name"],
            price=float(data["price"]),
            category=data["category"],
            product_id=int(data["product_id"])
        )
```

**Key Points**:
- DTO name: `{Entity}DynamoDTO` (e.g., `ProductDynamoDTO`)
- Include partition key (PK) and sort key (SK) for DynamoDB
- Provide conversion methods: `from_entity()`, `to_entity()`, `to_dynamo()`, `from_dynamo()`
- Handle type conversions (e.g., float, int)


---

## Step 5: Implement Repository (DynamoDB)

**Location**: `src/shared/infra/repositories/`

**Purpose**: Concrete implementation of the repository interface for DynamoDB. Handles all database operations.

**Importance**:
- Implements the repository contract
- Encapsulates database-specific logic
- Uses DTOs for data conversion
- Handles errors and edge cases

**Example**: Creating a `ProductRepositoryDynamo`

```python
# src/shared/infra/repositories/product_repository_dynamo.py
from typing import List
from src.shared.domain.entities.product import Product
from src.shared.domain.repositories.product_repository_interface import IProductRepository
from src.shared.infra.dto.product_dynamo_dto import ProductDynamoDTO
from src.shared.infra.external.dynamo.dynamo_table import DynamoTable
from src.shared.helpers.errors.usecase_errors import NoItemsFound

class ProductRepositoryDynamo(IProductRepository):
    
    def __init__(self):
        self.dynamo = DynamoTable()

    def get_product(self, product_id: int) -> Product:
        """
        Retrieve a product by ID from DynamoDB.
        """
        pk = f"PRODUCT#{product_id}"
        sk = f"PRODUCT#{product_id}"
        
        response = self.dynamo.get_item(partition_key=pk, sort_key=sk)
        
        if response is None:
            raise NoItemsFound("product_id")
        
        product_dto = ProductDynamoDTO.from_dynamo(response)
        return product_dto.to_entity()

    def get_all_products(self) -> List[Product]:
        """
        Retrieve all products from DynamoDB.
        """
        # Query all items with PK starting with "PRODUCT#"
        response = self.dynamo.get_all_items()
        
        products = []
        for item in response:
            if item.get("PK", "").startswith("PRODUCT#") and item.get("SK", "").startswith("PRODUCT#"):
                product_dto = ProductDynamoDTO.from_dynamo(item)
                products.append(product_dto.to_entity())
        
        if len(products) == 0:
            raise NoItemsFound("products")
        
        return products

    def create_product(self, new_product: Product) -> Product:
        """
        Create a new product in DynamoDB.
        """
        # Get next product ID
        product_id = self.get_product_counter() + 1
        new_product.product_id = product_id
        
        # Convert to DTO
        product_dto = ProductDynamoDTO.from_entity(new_product)
        
        # Save to DynamoDB
        self.dynamo.put_item(
            partition_key=product_dto.pk,
            sort_key=product_dto.sk,
            item=product_dto.to_dynamo()
        )
        
        # Update counter
        self._update_product_counter(product_id)
        
        return new_product

    def update_product(self, product_id: int, name: str = None, price: float = None, category: str = None) -> Product:
        """
        Update product information in DynamoDB.
        """
        # Get existing product
        product = self.get_product(product_id)
        
        # Update fields if provided
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if category is not None:
            product.category = category
        
        # Convert to DTO and save
        product_dto = ProductDynamoDTO.from_entity(product)
        self.dynamo.put_item(
            partition_key=product_dto.pk,
            sort_key=product_dto.sk,
            item=product_dto.to_dynamo()
        )
        
        return product

    def delete_product(self, product_id: int) -> Product:
        """
        Delete a product from DynamoDB.
        """
        # Get product before deleting (to return it)
        product = self.get_product(product_id)
        
        pk = f"PRODUCT#{product_id}"
        sk = f"PRODUCT#{product_id}"
        
        self.dynamo.delete_item(partition_key=pk, sort_key=sk)
        
        return product

    def get_product_counter(self) -> int:
        """
        Get the current product counter from DynamoDB.
        """
        pk = "PRODUCT_COUNTER"
        sk = "PRODUCT_COUNTER"
        
        response = self.dynamo.get_item(partition_key=pk, sort_key=sk)
        
        if response is None:
            return 0
        
        return int(response.get("counter", 0))

    def _update_product_counter(self, new_count: int):
        """
        Update the product counter in DynamoDB.
        """
        pk = "PRODUCT_COUNTER"
        sk = "PRODUCT_COUNTER"
        
        self.dynamo.put_item(
            partition_key=pk,
            sort_key=sk,
            item={"PK": pk, "SK": sk, "counter": new_count}
        )
```

**Key Points**:
- Class name: `{Entity}RepositoryDynamo` (e.g., `ProductRepositoryDynamo`)
- Implements the repository interface
- Uses `DynamoTable` for database operations
- Uses DTOs for data conversion
- Raises `NoItemsFound` when items don't exist
- Manages ID generation with counter pattern


---

## Step 6: Implement Mock Repository

**Location**: `src/shared/infra/repositories/`

**Purpose**: In-memory implementation of the repository interface for testing. No external dependencies.

**Importance**:
- Enables fast unit testing without database
- No setup required for tests
- Predictable test data
- Easy to debug

**Example**: Creating a `ProductRepositoryMock`

```python
# src/shared/infra/repositories/product_repository_mock.py
from typing import List
from src.shared.domain.entities.product import Product
from src.shared.domain.repositories.product_repository_interface import IProductRepository
from src.shared.helpers.errors.usecase_errors import NoItemsFound

class ProductRepositoryMock(IProductRepository):
    
    def __init__(self):
        # Initialize with sample data
        self.products = [
            Product(name="Laptop", price=999.99, category="Electronics", product_id=1),
            Product(name="Mouse", price=29.99, category="Electronics", product_id=2),
            Product(name="Desk", price=299.99, category="Furniture", product_id=3),
        ]

    def get_product(self, product_id: int) -> Product:
        """
        Retrieve a product by ID from in-memory list.
        """
        for product in self.products:
            if product.product_id == product_id:
                return product
        
        raise NoItemsFound("product_id")

    def get_all_products(self) -> List[Product]:
        """
        Retrieve all products from in-memory list.
        """
        if len(self.products) == 0:
            raise NoItemsFound("products")
        
        return self.products

    def create_product(self, new_product: Product) -> Product:
        """
        Add a new product to in-memory list.
        """
        # Assign new ID
        new_product.product_id = self.get_product_counter() + 1
        
        # Add to list
        self.products.append(new_product)
        
        return new_product

    def update_product(self, product_id: int, name: str = None, price: float = None, category: str = None) -> Product:
        """
        Update product in in-memory list.
        """
        product = self.get_product(product_id)
        
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if category is not None:
            product.category = category
        
        return product

    def delete_product(self, product_id: int) -> Product:
        """
        Remove product from in-memory list.
        """
        product = self.get_product(product_id)
        self.products.remove(product)
        return product

    def get_product_counter(self) -> int:
        """
        Return the highest product ID.
        """
        if len(self.products) == 0:
            return 0
        
        return max([p.product_id for p in self.products])
```

**Key Points**:
- Class name: `{Entity}RepositoryMock` (e.g., `ProductRepositoryMock`)
- Implements the same interface as DynamoDB repository
- Uses in-memory list for storage
- Include sample data for testing
- Same behavior as real repository (raises same exceptions)


---

## Step 7: Create Use Case

**Location**: `src/modules/{feature_name}/app/`

**Purpose**: Use cases orchestrate business logic for specific features. They coordinate between entities and repositories.

**Importance**:
- Contains application-specific business rules
- Orchestrates the flow of data
- Independent of delivery mechanism (HTTP, CLI, etc.)
- Highly testable with mock repositories

**Example**: Creating a `CreateProductUsecase`

```python
# src/modules/create_product/app/create_product_usecase.py
from src.shared.domain.entities.product import Product
from src.shared.domain.repositories.product_repository_interface import IProductRepository
from src.shared.helpers.errors.domain_errors import EntityError

class CreateProductUsecase:
    
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    def __call__(self, name: str, price: float, category: str) -> Product:
        """
        Create a new product.
        
        Args:
            name: Product name
            price: Product price
            category: Product category
            
        Returns:
            Created Product entity
            
        Raises:
            EntityError: If validation fails
        """
        # Validate inputs using entity validation
        if not Product.validate_name(name):
            raise EntityError("name")
        
        if not Product.validate_price(price):
            raise EntityError("price")
        
        if not Product.validate_category(category):
            raise EntityError("category")
        
        # Create entity
        product = Product(
            name=name,
            price=price,
            category=category
        )
        
        # Persist through repository
        return self.repo.create_product(product)
```

**Additional Use Case Examples**:

```python
# src/modules/get_product/app/get_product_usecase.py
from src.shared.domain.entities.product import Product
from src.shared.domain.repositories.product_repository_interface import IProductRepository

class GetProductUsecase:
    
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    def __call__(self, product_id: int) -> Product:
        """
        Retrieve a product by ID.
        """
        if type(product_id) != int:
            raise EntityError("product_id")
        
        if product_id < 0:
            raise EntityError("product_id")
        
        return self.repo.get_product(product_id)
```

```python
# src/modules/update_product/app/update_product_usecase.py
from src.shared.domain.entities.product import Product
from src.shared.domain.repositories.product_repository_interface import IProductRepository
from src.shared.helpers.errors.domain_errors import EntityError

class UpdateProductUsecase:
    
    def __init__(self, repo: IProductRepository):
        self.repo = repo

    def __call__(self, product_id: int, name: str = None, price: float = None, category: str = None) -> Product:
        """
        Update product information.
        """
        # Validate product_id
        if type(product_id) != int or product_id < 0:
            raise EntityError("product_id")
        
        # Validate optional fields if provided
        if name is not None and not Product.validate_name(name):
            raise EntityError("name")
        
        if price is not None and not Product.validate_price(price):
            raise EntityError("price")
        
        if category is not None and not Product.validate_category(category):
            raise EntityError("category")
        
        return self.repo.update_product(product_id, name, price, category)
```

**Key Points**:
- Class name: `{Action}{Entity}Usecase` (e.g., `CreateProductUsecase`)
- Inject repository through constructor
- Implement `__call__` method for execution
- Validate inputs before creating entities
- Use entity validation methods
- Raise appropriate errors
- Return domain entities, not DTOs


---

## Step 8: Create ViewModel

**Location**: `src/modules/{feature_name}/app/`

**Purpose**: ViewModels transform domain entities into API response format. They add presentation-specific fields and format data for external consumption.

**Importance**:
- Separates domain model from API response format
- Adds presentation-specific fields (messages, metadata)
- Formats data appropriately for clients
- Allows different views of the same entity

**Example**: Creating a `CreateProductViewmodel`

```python
# src/modules/create_product/app/create_product_viewmodel.py
from src.shared.domain.entities.product import Product

class CreateProductViewmodel:
    product_id: int
    name: str
    price: float
    category: str

    def __init__(self, product: Product):
        self.product_id = product.product_id
        self.name = product.name
        self.price = product.price
        self.category = product.category

    def to_dict(self):
        """
        Convert to dictionary for JSON response.
        """
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'message': "the product was created successfully"
        }
```

**Additional ViewModel Examples**:

```python
# src/modules/get_product/app/get_product_viewmodel.py
from src.shared.domain.entities.product import Product

class GetProductViewmodel:
    product_id: int
    name: str
    price: float
    category: str

    def __init__(self, product: Product):
        self.product_id = product.product_id
        self.name = product.name
        self.price = product.price
        self.category = product.category

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'message': "the product was retrieved successfully"
        }
```

```python
# src/modules/get_all_products/app/get_all_products_viewmodel.py
from typing import List
from src.shared.domain.entities.product import Product

class GetAllProductsViewmodel:
    products: List[dict]

    def __init__(self, products: List[Product]):
        self.products = [
            {
                'product_id': p.product_id,
                'name': p.name,
                'price': p.price,
                'category': p.category
            }
            for p in products
        ]

    def to_dict(self):
        return {
            'products': self.products,
            'count': len(self.products),
            'message': "all products were retrieved successfully"
        }
```

**Key Points**:
- Class name: `{Action}{Entity}Viewmodel` (e.g., `CreateProductViewmodel`)
- Takes domain entity in constructor
- Extracts relevant fields
- Implements `to_dict()` method for JSON serialization
- Add presentation-specific fields (messages, metadata)
- Can format data differently than entity (e.g., date formatting)


---

## Step 9: Create Controller

**Location**: `src/modules/{feature_name}/app/`

**Purpose**: Controllers handle HTTP requests, validate parameters, call use cases, and format HTTP responses. They are the entry point for request processing.

**Importance**:
- Handles HTTP-specific concerns
- Validates request parameters
- Maps HTTP errors to appropriate status codes
- Orchestrates use case execution
- Returns properly formatted HTTP responses

**Example**: Creating a `CreateProductController`

```python
# src/modules/create_product/app/create_product_controller.py
from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .create_product_usecase import CreateProductUsecase
from .create_product_viewmodel import CreateProductViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.external_interfaces.http_codes import Created, NotFound, BadRequest, InternalServerError

class CreateProductController:

    def __init__(self, usecase: CreateProductUsecase):
        self.CreateProductUsecase = usecase

    def __call__(self, request: IRequest) -> IResponse:
        """
        Handle create product request.
        
        Args:
            request: HTTP request with product data
            
        Returns:
            HTTP response with created product or error
        """
        try:
            # Validate required parameters
            if request.data.get('name') is None:
                raise MissingParameters('name')
            
            if request.data.get('price') is None:
                raise MissingParameters('price')
            
            if request.data.get('category') is None:
                raise MissingParameters('category')
            
            # Validate parameter types
            if type(request.data.get('price')) not in [int, float]:
                raise WrongTypeParameter('price', 'float', type(request.data.get('price')))

            # Call use case
            product = self.CreateProductUsecase(
                name=request.data.get('name'),
                price=float(request.data.get('price')),
                category=request.data.get('category')
            )

            # Create view model and return success response
            viewmodel = CreateProductViewmodel(product)
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

**Additional Controller Examples**:

```python
# src/modules/get_product/app/get_product_controller.py
from src.shared.helpers.external_interfaces.external_interface import IResponse, IRequest
from .get_product_usecase import GetProductUsecase
from .get_product_viewmodel import GetProductViewmodel
from src.shared.helpers.errors.controller_errors import MissingParameters, WrongTypeParameter
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.helpers.errors.usecase_errors import NoItemsFound
from src.shared.helpers.external_interfaces.http_codes import OK, NotFound, BadRequest, InternalServerError

class GetProductController:

    def __init__(self, usecase: GetProductUsecase):
        self.GetProductUsecase = usecase

    def __call__(self, request: IRequest) -> IResponse:
        try:
            # Validate required parameters
            if request.data.get('product_id') is None:
                raise MissingParameters('product_id')
            
            # Validate parameter type
            if type(request.data.get('product_id')) != int:
                raise WrongTypeParameter('product_id', 'int', type(request.data.get('product_id')))

            # Call use case
            product = self.GetProductUsecase(
                product_id=request.data.get('product_id')
            )

            # Create view model and return success response
            viewmodel = GetProductViewmodel(product)
            return OK(viewmodel.to_dict())

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

**Key Points**:
- Class name: `{Action}{Entity}Controller` (e.g., `CreateProductController`)
- Inject use case through constructor
- Implement `__call__` method
- Validate all required parameters first
- Validate parameter types
- Call use case with validated data
- Create view model from result
- Return appropriate HTTP status codes:
  - 200 OK: Successful GET, UPDATE, DELETE
  - 201 Created: Successful CREATE
  - 400 Bad Request: Validation errors
  - 404 Not Found: Resource not found
  - 500 Internal Server Error: Unexpected errors
- Handle all possible exceptions


---

## Step 10: Create Presenter (Lambda Handler)

**Location**: `src/modules/{feature_name}/app/`

**Purpose**: Presenters are the Lambda function entry points. They initialize dependencies, convert Lambda events to HTTP requests, and format responses for API Gateway.

**Importance**:
- Lambda function entry point
- Dependency injection setup
- Event format conversion
- Response format conversion
- Environment-based repository selection

**Example**: Creating a `create_product_presenter.py`

```python
# src/modules/create_product/app/create_product_presenter.py
from .create_product_controller import CreateProductController
from .create_product_usecase import CreateProductUsecase
from src.shared.environments import Environments
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest, LambdaHttpResponse

# Initialize dependencies
repo = Environments.get_user_repo()()  # Gets appropriate repository based on STAGE
usecase = CreateProductUsecase(repo)
controller = CreateProductController(usecase)

def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event from API Gateway
        context: Lambda context object
        
    Returns:
        Dictionary formatted for API Gateway response
    """
    # Optional: Print event for debugging
    from pprint import pprint
    pprint(event)

    # Convert Lambda event to HTTP request
    httpRequest = LambdaHttpRequest(data=event)
    
    # Process request through controller
    response = controller(httpRequest)
    
    # Convert to Lambda response format
    httpResponse = LambdaHttpResponse(
        status_code=response.status_code,
        body=response.body,
        headers=response.headers
    )

    return httpResponse.toDict()
```

**Key Points**:
- File name: `{feature_name}_presenter.py` (e.g., `create_product_presenter.py`)
- Initialize dependencies at module level (outside lambda_handler)
- Use `Environments.get_user_repo()` for environment-based repository selection
- Function name must be `lambda_handler`
- Convert Lambda event to `LambdaHttpRequest`
- Convert controller response to `LambdaHttpResponse`
- Return dictionary with `toDict()`

**Dependency Injection Flow**:
```
Environments.get_user_repo() 
    → Returns Mock or DynamoDB repository based on STAGE
    → Repository injected into Usecase
    → Usecase injected into Controller
```


---

## Step 11: Add Lambda Function to CDK Stack

**Location**: `iac/iac/lambda_stack.py`

**Purpose**: Define the Lambda function and API Gateway integration in the CDK infrastructure code.

**Importance**:
- Deploys Lambda function to AWS
- Configures API Gateway endpoint
- Sets environment variables
- Manages permissions

**Example**: Adding a product endpoint to `lambda_stack.py`

```python
# iac/iac/lambda_stack.py
# Add to the __init__ method of LambdaStack class

self.create_product_function = self.create_lambda_api_gateway_integration(
    module_name="create_product",
    method="POST",
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

self.get_product_function = self.create_lambda_api_gateway_integration(
    module_name="get_product",
    method="GET",
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

self.get_all_products_function = self.create_lambda_api_gateway_integration(
    module_name="get_all_products",
    method="GET",
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

self.update_product_function = self.create_lambda_api_gateway_integration(
    module_name="update_product",
    method="POST",
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

self.delete_product_function = self.create_lambda_api_gateway_integration(
    module_name="delete_product",
    method="POST",
    mss_student_api_resource=api_gateway_resource,
    environment_variables=environment_variables
)

# Add to functions_that_need_dynamo_permissions list
self.functions_that_need_dynamo_permissions = [
    self.get_user_function, 
    self.create_user_function,
    self.delete_user_function, 
    self.update_user_function,
    self.create_product_function,  # Add new functions
    self.get_product_function,
    self.get_all_products_function,
    self.update_product_function,
    self.delete_product_function
]
```

**Key Points**:
- Use `create_lambda_api_gateway_integration()` helper method
- `module_name` must match the directory name in `src/modules/`
- `method` is the HTTP method (GET, POST, PUT, DELETE)
- Add function to `functions_that_need_dynamo_permissions` list
- This automatically:
  - Creates Lambda function
  - Creates API Gateway resource
  - Integrates Lambda with API Gateway
  - Grants DynamoDB permissions

**Resulting API Endpoints**:
```
POST   /mss-template/create-product
GET    /mss-template/get-product
GET    /mss-template/get-all-products
POST   /mss-template/update-product
POST   /mss-template/delete-product
```


---

## Step 12: Update Environment Configuration

**Location**: `src/shared/environments.py`

**Purpose**: Add repository factory method for the new entity if needed.

**Example**: Adding product repository to environments

```python
# src/shared/environments.py
# Add to Environments class

@staticmethod
def get_product_repo() -> IProductRepository:
    if Environments.get_envs().stage == STAGE.TEST:
        from src.shared.infra.repositories.product_repository_mock import ProductRepositoryMock
        return ProductRepositoryMock
    elif Environments.get_envs().stage in [STAGE.DEV, STAGE.HOMOLOG, STAGE.PROD]:
        from src.shared.infra.repositories.product_repository_dynamo import ProductRepositoryDynamo
        return ProductRepositoryDynamo
    else:
        raise Exception("No repository found for this stage")
```

**Note**: If you're adding operations to an existing entity (like User), you don't need to modify `environments.py`. Only add new methods when introducing new entities.

---

## Step 13: Write Tests

**Location**: `tests/`

**Purpose**: Ensure code quality and correctness through comprehensive testing.

**Test Structure**:
```
tests/
├── shared/
│   ├── domain/
│   │   └── entities/
│   │       └── test_product.py
│   └── infra/
│       └── repositories/
│           ├── test_product_repository_mock.py
│           └── test_product_repository_dynamo.py
└── modules/
    └── create_product/
        └── app/
            ├── test_create_product_usecase.py
            ├── test_create_product_controller.py
            ├── test_create_product_viewmodel.py
            └── test_create_product_presenter.py
```

**Example: Entity Test**

```python
# tests/shared/domain/entities/test_product.py
import pytest
from src.shared.domain.entities.product import Product
from src.shared.helpers.errors.domain_errors import EntityError

class TestProduct:
    
    def test_product_valid(self):
        product = Product(name="Laptop", price=999.99, category="Electronics", product_id=1)
        assert product.name == "Laptop"
        assert product.price == 999.99
        assert product.category == "Electronics"
        assert product.product_id == 1
    
    def test_product_invalid_name_too_short(self):
        with pytest.raises(EntityError):
            Product(name="AB", price=999.99, category="Electronics")
    
    def test_product_invalid_price_negative(self):
        with pytest.raises(EntityError):
            Product(name="Laptop", price=-10.0, category="Electronics")
    
    def test_product_invalid_category_empty(self):
        with pytest.raises(EntityError):
            Product(name="Laptop", price=999.99, category="")
```

**Example: Use Case Test**

```python
# tests/modules/create_product/app/test_create_product_usecase.py
import pytest
from src.modules.create_product.app.create_product_usecase import CreateProductUsecase
from src.shared.infra.repositories.product_repository_mock import ProductRepositoryMock
from src.shared.helpers.errors.domain_errors import EntityError

class TestCreateProductUsecase:
    
    def test_create_product_valid(self):
        repo = ProductRepositoryMock()
        usecase = CreateProductUsecase(repo)
        
        product = usecase(name="Keyboard", price=79.99, category="Electronics")
        
        assert product.name == "Keyboard"
        assert product.price == 79.99
        assert product.category == "Electronics"
        assert product.product_id is not None
    
    def test_create_product_invalid_name(self):
        repo = ProductRepositoryMock()
        usecase = CreateProductUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(name="AB", price=79.99, category="Electronics")
    
    def test_create_product_invalid_price(self):
        repo = ProductRepositoryMock()
        usecase = CreateProductUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(name="Keyboard", price=-10.0, category="Electronics")
```

**Example: Controller Test**

```python
# tests/modules/create_product/app/test_create_product_controller.py
from src.modules.create_product.app.create_product_controller import CreateProductController
from src.modules.create_product.app.create_product_usecase import CreateProductUsecase
from src.shared.infra.repositories.product_repository_mock import ProductRepositoryMock
from src.shared.helpers.external_interfaces.http_lambda_requests import LambdaHttpRequest

class TestCreateProductController:
    
    def test_create_product_valid(self):
        repo = ProductRepositoryMock()
        usecase = CreateProductUsecase(repo)
        controller = CreateProductController(usecase)
        
        request = LambdaHttpRequest(data={
            'name': 'Monitor',
            'price': 299.99,
            'category': 'Electronics'
        })
        
        response = controller(request)
        
        assert response.status_code == 201
        assert response.body['name'] == 'Monitor'
        assert response.body['price'] == 299.99
        assert 'product_id' in response.body
    
    def test_create_product_missing_name(self):
        repo = ProductRepositoryMock()
        usecase = CreateProductUsecase(repo)
        controller = CreateProductController(usecase)
        
        request = LambdaHttpRequest(data={
            'price': 299.99,
            'category': 'Electronics'
        })
        
        response = controller(request)
        
        assert response.status_code == 400
        assert 'name' in response.body
```

**Key Testing Points**:
- Test valid cases
- Test all validation rules
- Test error cases
- Use mock repository for unit tests
- Test each layer independently
- Aim for high code coverage


---

## Complete Feature Checklist

Use this checklist when implementing a new feature:

### Domain Layer
- [ ] Create entity in `src/shared/domain/entities/`
- [ ] Add validation methods to entity
- [ ] Create enums in `src/shared/domain/enums/` (if needed)
- [ ] Create repository interface in `src/shared/domain/repositories/`
- [ ] Document all methods with docstrings

### Infrastructure Layer
- [ ] Create DTO in `src/shared/infra/dto/`
- [ ] Implement conversion methods (from_entity, to_entity, to_dynamo, from_dynamo)
- [ ] Create DynamoDB repository in `src/shared/infra/repositories/`
- [ ] Create mock repository in `src/shared/infra/repositories/`
- [ ] Add repository factory to `src/shared/environments.py` (for new entities)

### Module Creation
- [ ] Create module directory in `src/modules/{feature_name}/app/`
- [ ] Create use case file
- [ ] Create view model file
- [ ] Create controller file
- [ ] Create presenter file (Lambda handler)

### Infrastructure as Code
- [ ] Add Lambda function to `iac/iac/lambda_stack.py`
- [ ] Add function to DynamoDB permissions list
- [ ] Verify API Gateway endpoint configuration

### Testing
- [ ] Write entity tests in `tests/shared/domain/entities/`
- [ ] Write repository tests in `tests/shared/infra/repositories/`
- [ ] Write use case tests in `tests/modules/{feature_name}/app/`
- [ ] Write controller tests in `tests/modules/{feature_name}/app/`
- [ ] Write view model tests in `tests/modules/{feature_name}/app/`
- [ ] Write presenter tests in `tests/modules/{feature_name}/app/`
- [ ] Run all tests: `pytest`
- [ ] Check coverage: `pytest --cov=src`

### Deployment
- [ ] Run tests locally
- [ ] Deploy to dev environment: `cd iac && cdk deploy`
- [ ] Test API endpoints with curl or Postman
- [ ] Verify CloudWatch logs
- [ ] Check X-Ray traces
- [ ] Deploy to staging/production

---

## Common Patterns and Best Practices

### Naming Conventions

**Files and Directories**:
- snake_case: `create_product_controller.py`
- Module directory: `src/modules/{feature_name}/app/`

**Classes**:
- Entity: `Product`
- Enum: `PRODUCT_STATUS`
- Repository Interface: `IProductRepository`
- Repository Implementation: `ProductRepositoryDynamo`, `ProductRepositoryMock`
- DTO: `ProductDynamoDTO`
- Use Case: `CreateProductUsecase`
- Controller: `CreateProductController`
- View Model: `CreateProductViewmodel`
- Presenter: `create_product_presenter.py` (file name)

**Methods**:
- snake_case: `create_product`, `get_product`, `validate_name`
- Use verbs for actions

**Variables**:
- snake_case: `product_id`, `user_name`
- Avoid verbs

### Error Handling

**Domain Errors** (`EntityError`):
- Invalid entity data
- Validation failures
- Business rule violations

**Use Case Errors** (`NoItemsFound`):
- Resource not found
- Empty result sets

**Controller Errors**:
- `MissingParameters`: Required parameter not provided
- `WrongTypeParameter`: Parameter has wrong type

**HTTP Status Codes**:
- 200 OK: Successful GET, UPDATE, DELETE
- 201 Created: Successful CREATE
- 400 Bad Request: Validation errors, missing parameters
- 404 Not Found: Resource not found
- 500 Internal Server Error: Unexpected errors

### Dependency Flow

```
Presenter (Lambda Handler)
    ↓ creates
Controller
    ↓ uses
Use Case
    ↓ uses
Repository Interface
    ↑ implemented by
Repository Implementation (DynamoDB or Mock)
    ↓ uses
DTO
    ↓ converts to/from
Entity
```

### Testing Strategy

1. **Unit Tests**: Test each component in isolation
   - Use mock repositories
   - Test all validation rules
   - Test error cases

2. **Integration Tests**: Test components together
   - Test full request flow
   - Use mock repository for speed

3. **End-to-End Tests**: Test deployed API
   - Test actual API endpoints
   - Verify database operations
   - Check CloudWatch logs

### Code Organization

**Keep layers separate**:
- Domain layer has no dependencies on outer layers
- Use cases depend only on domain
- Controllers depend on use cases and domain
- Infrastructure implements domain interfaces

**Single Responsibility**:
- Each class has one reason to change
- Entities: business rules
- Use cases: application logic
- Controllers: HTTP handling
- Repositories: data access

**Dependency Inversion**:
- Depend on abstractions (interfaces), not implementations
- Use dependency injection
- Repository interfaces in domain, implementations in infrastructure

---

## Example: Complete Feature Implementation

Here's a complete example showing all files for a "Create Product" feature:

### File Structure
```
src/
├── shared/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── product.py
│   │   └── repositories/
│   │       └── product_repository_interface.py
│   └── infra/
│       ├── dto/
│       │   └── product_dynamo_dto.py
│       └── repositories/
│           ├── product_repository_dynamo.py
│           └── product_repository_mock.py
└── modules/
    └── create_product/
        └── app/
            ├── create_product_usecase.py
            ├── create_product_controller.py
            ├── create_product_viewmodel.py
            └── create_product_presenter.py
```

### Implementation Order Summary

1. **Start with Domain** (innermost layer)
   - Define what a Product IS
   - Define how to access Products (interface)

2. **Implement Infrastructure** (outermost layer)
   - Define how to store Products (DTO)
   - Implement storage (repositories)

3. **Create Use Case** (application logic)
   - Define what the feature DOES

4. **Create Interface Adapters** (presentation)
   - Define how to present data (view model)
   - Define how to handle requests (controller)
   - Define Lambda entry point (presenter)

5. **Deploy Infrastructure**
   - Add to CDK stack
   - Deploy to AWS

6. **Test Everything**
   - Unit tests for each component
   - Integration tests for full flow

---

## Troubleshooting

### Common Issues

**Import Errors**:
- Ensure all `__init__.py` files exist
- Check import paths are correct
- Verify module structure matches imports

**Repository Not Found**:
- Check `environments.py` has factory method
- Verify STAGE environment variable is set
- Ensure repository class names match

**Lambda Function Not Found**:
- Verify module directory name matches `module_name` in CDK
- Check presenter file name: `{module_name}_presenter.py`
- Ensure `lambda_handler` function exists

**DynamoDB Errors**:
- Check table name in environment variables
- Verify partition key and sort key names
- Ensure Lambda has DynamoDB permissions

**API Gateway 502 Errors**:
- Check CloudWatch logs for Lambda errors
- Verify presenter returns correct format
- Check for Python exceptions in code

---

## Additional Resources

- **Clean Architecture Book**: https://www.amazon.com/Clean-Architecture-Craftsmans-Software-Structure/dp/0134494164
- **Clean Architecture Diagram**: https://www.figma.com/file/CmfQcH2xbZyIszPX0iOxPp/Clean-Arch---HackaBeckas
- **AWS Lambda Documentation**: https://docs.aws.amazon.com/lambda/
- **AWS CDK Documentation**: https://docs.aws.amazon.com/cdk/
- **DynamoDB Best Practices**: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html

---

## Summary

Implementing a new feature in this Clean Architecture template follows a consistent pattern:

1. **Domain First**: Define entities and interfaces
2. **Infrastructure**: Implement data access
3. **Use Cases**: Implement business logic
4. **Interface Adapters**: Handle presentation
5. **Deploy**: Add to CDK and deploy
6. **Test**: Verify everything works

This approach ensures:
- **Maintainability**: Clear separation of concerns
- **Testability**: Each layer can be tested independently
- **Flexibility**: Easy to change implementations
- **Scalability**: Serverless architecture scales automatically

Follow this guide for consistent, high-quality feature implementations that align with Clean Architecture principles.
