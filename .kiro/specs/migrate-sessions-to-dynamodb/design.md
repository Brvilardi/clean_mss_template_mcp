# Design Document: Migração de Sessions para DynamoDB

## Overview

Este documento descreve o design técnico para migrar o armazenamento de sessões do re:Invent de SQLite para DynamoDB. A migração elimina problemas de persistência em ambiente Lambda, melhora performance e mantém consistência com o padrão arquitetural já estabelecido para Users.

### Objetivos

1. Substituir SessionRepositorySQLite por SessionRepositoryDynamo
2. Criar modelo de dados DynamoDB otimizado para queries comuns
3. Implementar GSIs para buscas por venue, dia e level
4. Manter compatibilidade com interface existente
5. Provisionar infraestrutura via CDK
6. Migrar dados existentes sem perda

### Não-Objetivos

- Modificar a entidade Session do domínio
- Alterar casos de uso existentes
- Mudar contratos de API

## Architecture

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     Lambda Functions                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ GetAllSessions│  │ SyncSessions │  │GetSessionById│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Use Cases      │
                    │  (Unchanged)    │
                    └────────┬────────┘
                             │
              ┌──────────────▼──────────────┐
              │  ISessionRepository         │
              │  (Interface - Extended)     │
              └──────────────┬──────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│ SessionRepo    │  │ SessionRepo     │  │ SessionRepo    │
│ Mock           │  │ SQLite (Remove) │  │ Dynamo (NEW)   │
└────────────────┘  └─────────────────┘  └───────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │ SessionDynamoDTO│
                                         │     (NEW)       │
                                         └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  DynamoDB Table │
                                         │  + 3 GSIs       │
                                         └─────────────────┘
```

### Fluxo de Dados

1. **Query por ID**: Lambda → UseCase → Repository → GetItem(PK) → DynamoDB
2. **Query por Venue**: Lambda → UseCase → Repository → Query(GSI-Venue) → DynamoDB
3. **Query por Day**: Lambda → UseCase → Repository → Query(GSI-Day) → DynamoDB
4. **Query por Level**: Lambda → UseCase → Repository → Query(GSI-Level) → DynamoDB
5. **Sync API**: Lambda → UseCase → Repository → BatchWriteItem → DynamoDB

## Components and Interfaces

### 1. SessionDynamoDTO

**Responsabilidade**: Converter entre Session entity e formato DynamoDB

**Localização**: `src/shared/infra/dto/session_dynamo_dto.py`

**Estrutura**:

```python
class SessionDynamoDTO:
    session_id: str
    short_id: str
    title: str
    abstract: str
    session_type: str
    venue_name: str
    venue_room: str
    start_datetime: str
    end_datetime: str
    day: str
    speakers: List[Dict[str, str]]
    topics: List[str]
    areas_of_interest: List[str]
    level: str
    level_value: int
    features: List[str]
    seat_capacity: int
    
    @staticmethod
    def from_entity(session: Session) -> "SessionDynamoDTO"
    
    def to_dynamo(self) -> dict
    
    @staticmethod
    def from_dynamo(data: dict) -> "SessionDynamoDTO"
    
    def to_entity(self) -> Session
```

**Formato DynamoDB**:

```python
{
    "PK": "SESSION#abc123",
    "entity": "session",
    "session_id": "abc123",
    "short_id": "ABC301",
    "title": "Building Serverless Applications",
    "abstract": "Learn how to...",
    "session_type": "Breakout Session",
    "venue_name": "Venetian",
    "venue_room": "Level 2, Marcello 4405",
    "start_datetime": "2024-12-03T10:00:00Z",
    "end_datetime": "2024-12-03T11:00:00Z",
    "day": "Tuesday",
    "speakers": [
        {"displayName": "John Doe", "company": "AWS"}
    ],
    "topics": ["Serverless", "Lambda"],
    "areas_of_interest": ["Architecture"],
    "level": "300 - Advanced",
    "level_value": 300,
    "features": ["Live Demo"],
    "seat_capacity": 500
}
```

### 2. SessionRepositoryDynamo

**Responsabilidade**: Implementar operações de persistência no DynamoDB

**Localização**: `src/shared/infra/repositories/session_repository_dynamo.py`

**Métodos**:

```python
class SessionRepositoryDynamo(ISessionRepository):
    
    @staticmethod
    def partition_key_format(session_id: str) -> str:
        """Retorna 'SESSION#{session_id}'"""
    
    def __init__(self):
        """Inicializa conexão com DynamoDB via DynamoDatasource"""
    
    def get_session_by_id(self, session_id: str) -> Session:
        """
        Query: GetItem com PK = SESSION#{session_id}
        Raises: NoItemsFound se não encontrar
        """
    
    def get_all_sessions(self) -> List[Session]:
        """
        Query: Scan com FilterExpression entity = 'session'
        Nota: Para produção com muitos dados, considerar paginação
        """
    
    def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
        """
        Query: GSI-Venue com PK = venue_name
        Ordenado por start_datetime (SK do GSI)
        """
    
    def get_sessions_by_day(self, day: str) -> List[Session]:
        """
        Query: GSI-Day com PK = day
        Ordenado por start_datetime (SK do GSI)
        """
    
    def get_sessions_by_level(self, level_value: int) -> List[Session]:
        """
        Query: GSI-Level com PK = level_value
        Ordenado por start_datetime (SK do GSI)
        """
    
    def sync_sessions_from_api(self) -> Dict[str, int]:
        """
        1. Fetch da API externa via ReinventCatalogClient
        2. Parse para Session entities
        3. Batch write para DynamoDB (25 items por batch)
        4. Retorna contadores de inserted/updated
        """
```

### 3. ISessionRepository (Atualizada)

**Responsabilidade**: Definir contrato para repositórios de Session

**Localização**: `src/shared/domain/repositories/session_repository_interface.py`

**Novos Métodos**:

```python
@abstractmethod
def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
    """Retorna sessões filtradas por venue"""
    pass

@abstractmethod
def get_sessions_by_day(self, day: str) -> List[Session]:
    """Retorna sessões filtradas por dia"""
    pass

@abstractmethod
def get_sessions_by_level(self, level_value: int) -> List[Session]:
    """Retorna sessões filtradas por level"""
    pass
```

### 4. Environments (Atualizado)

**Responsabilidade**: Configurar qual repositório usar baseado em STAGE

**Localização**: `src/shared/environments.py`

**Novo Método**:

```python
@staticmethod
def get_session_repo():
    """
    Retorna classe de repositório baseada em STAGE:
    - TEST: SessionRepositoryMock
    - DEV/PROD: SessionRepositoryDynamo
    """
    if Environments.get_envs().stage == "TEST":
        from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock
        return SessionRepositoryMock
    else:
        from src.shared.infra.repositories.session_repository_dynamo import SessionRepositoryDynamo
        return SessionRepositoryDynamo
```

## Data Models

### Tabela Principal: SessionsTable (Exclusiva)

**Nota**: Tabela separada exclusiva para Sessions, sem sort key.

| Atributo | Tipo | Descrição | Indexado |
|----------|------|-----------|----------|
| PK | String | `SESSION#{session_id}` | Partition Key |
| entity | String | `"session"` | - |
| session_id | String | ID único da sessão | - |
| short_id | String | ID curto (ex: ABC301) | - |
| title | String | Título da sessão | - |
| abstract | String | Descrição completa | - |
| session_type | String | Tipo (Breakout, Workshop, etc) | - |
| venue_name | String | Nome do local | GSI-Venue PK |
| venue_room | String | Sala específica | - |
| start_datetime | String | ISO 8601 timestamp | GSI SK (todos) |
| end_datetime | String | ISO 8601 timestamp | - |
| day | String | Dia da semana | GSI-Day PK |
| speakers | List | Lista de objetos speaker | - |
| topics | List | Lista de strings | - |
| areas_of_interest | List | Lista de strings | - |
| level | String | Nível descritivo | - |
| level_value | Number | 100, 200, 300, 400 | GSI-Level PK |
| features | List | Lista de strings | - |
| seat_capacity | Number | Capacidade da sala | - |

### Global Secondary Indexes (GSIs)

#### GSI-Venue
- **Partition Key**: `venue_name` (String) - Valor direto: "Venetian", "Caesars Forum"
- **Sort Key**: `start_datetime` (String) - ISO 8601: "2024-12-03T10:00:00Z"
- **Projection**: ALL
- **Use Case**: Listar todas as sessões de um venue ordenadas por horário
- **Exemplo Query**: `venue_name = "Venetian"` retorna todas as sessões do Venetian ordenadas por horário

#### GSI-Day
- **Partition Key**: `day` (String) - Valor direto: "Monday", "Tuesday", "Wednesday"
- **Sort Key**: `start_datetime` (String) - ISO 8601: "2024-12-03T10:00:00Z"
- **Projection**: ALL
- **Use Case**: Listar todas as sessões de um dia ordenadas por horário
- **Exemplo Query**: `day = "Tuesday"` retorna todas as sessões de terça ordenadas por horário

#### GSI-Level
- **Partition Key**: `level_value` (Number) - Valor direto: 100, 200, 300, 400
- **Sort Key**: `start_datetime` (String) - ISO 8601: "2024-12-03T10:00:00Z"
- **Projection**: ALL
- **Use Case**: Listar todas as sessões de um nível ordenadas por horário
- **Exemplo Query**: `level_value = 300` retorna todas as sessões nível 300 ordenadas por horário

### Padrões de Acesso

| Query | Método | Índice | Complexidade |
|-------|--------|--------|--------------|
| Buscar por ID | GetItem | Table PK | O(1) |
| Listar todas | Scan | Table | O(n) |
| Buscar por venue | Query | GSI-Venue | O(log n) |
| Buscar por dia | Query | GSI-Day | O(log n) |
| Buscar por level | Query | GSI-Level | O(log n) |

## Infrastructure as Code

### CDK Stack Updates

**Arquivo**: `iac/iac/lambda_stack.py`

**Mudanças**:

1. Adicionar funções à lista de permissões DynamoDB:

```python
self.functions_that_need_dynamo_permissions = [
    self.get_user_function,
    self.create_user_function,
    self.delete_user_function,
    self.update_user_function,
    self.get_all_sessions_function,  # NOVO
    self.sync_sessions_function       # NOVO
]
```

### DynamoDB Table Definition

**Arquivo**: `iac/iac/sessions_dynamo_table.py` (novo arquivo)

```python
from aws_cdk import (
    aws_dynamodb as dynamodb,
    RemovalPolicy
)
from constructs import Construct

class SessionsDynamoTable(Construct):
    table: dynamodb.Table

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Tabela exclusiva para Sessions sem sort key
        self.table = dynamodb.Table(
            self, "SessionsDynamoTable",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # GSI-Venue
        self.table.add_global_secondary_index(
            index_name="GSI-Venue",
            partition_key=dynamodb.Attribute(
                name="venue_name",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI-Day
        self.table.add_global_secondary_index(
            index_name="GSI-Day",
            partition_key=dynamodb.Attribute(
                name="day",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )

        # GSI-Level
        self.table.add_global_secondary_index(
            index_name="GSI-Level",
            partition_key=dynamodb.Attribute(
                name="level_value",
                type=dynamodb.AttributeType.NUMBER
            ),
            sort_key=dynamodb.Attribute(
                name="start_datetime",
                type=dynamodb.AttributeType.STRING
            ),
            projection_type=dynamodb.ProjectionType.ALL
        )
```

## Error Handling

### Exceções Mapeadas

| Erro DynamoDB | Exceção Domain | HTTP Status | Cenário |
|---------------|----------------|-------------|---------|
| Item não encontrado | NoItemsFound | 404 | get_session_by_id com ID inválido |
| ValidationException | EntityError | 400 | Dados inválidos no put_item |
| ProvisionedThroughputExceededException | InternalServerError | 500 | Throttling (raro com PAY_PER_REQUEST) |
| ResourceNotFoundException | InternalServerError | 500 | Tabela não existe |

### Retry Strategy

- **Operações de leitura**: 3 tentativas com backoff exponencial
- **Operações de escrita**: 3 tentativas com backoff exponencial
- **Batch operations**: Processar UnprocessedItems automaticamente

## Testing Strategy

### Unit Tests

**Arquivo**: `tests/shared/infra/repositories/test_session_repository_dynamo.py`

**Casos de Teste**:

1. `test_get_session_by_id_success`: Verifica retorno correto
2. `test_get_session_by_id_not_found`: Verifica exceção NoItemsFound
3. `test_get_all_sessions`: Verifica listagem completa
4. `test_get_sessions_by_venue`: Verifica query no GSI-Venue
5. `test_get_sessions_by_day`: Verifica query no GSI-Day
6. `test_get_sessions_by_level`: Verifica query no GSI-Level
7. `test_sync_sessions_from_api`: Verifica sync e contadores

**Mock Strategy**: Usar `moto` para mockar DynamoDB

### Integration Tests

**Arquivo**: `tests/integration/test_session_repository_integration.py`

**Casos de Teste**:

1. Criar sessão real no DynamoDB local
2. Buscar por ID
3. Buscar por venue
4. Verificar ordenação por start_datetime nos GSIs

### Performance Tests

**Métricas Alvo**:

- `get_session_by_id`: < 10ms (p99)
- `get_sessions_by_venue`: < 50ms (p99)
- `get_all_sessions`: < 200ms para 1000 sessões (p99)
- `sync_sessions_from_api`: < 5s para 500 sessões (p99)

## Migration Strategy

### Script de Migração

**Arquivo**: `scripts/migrate_sqlite_to_dynamodb.py`

**Fluxo**:

1. Conectar ao SQLite existente
2. Ler todas as sessões
3. Converter para formato DynamoDB via SessionDynamoDTO
4. Batch write para DynamoDB (25 items por batch)
5. Validar contagem de registros
6. Gerar relatório de migração

**Execução**:

```bash
python scripts/migrate_sqlite_to_dynamodb.py \
  --sqlite-path src/shared/infra/external/sqlite/reinvent_sessions.db \
  --dynamodb-table reinvent-sessions-dev \
  --region us-east-1
```

### Rollback Plan

1. Manter SQLite repository como backup temporário
2. Adicionar feature flag para alternar entre repositórios
3. Após 1 semana de validação, remover código SQLite

## Performance Considerations

### Otimizações

1. **Batch Operations**: Usar batch_write_item para sync (25 items/batch)
2. **Projection**: GSIs com ALL projection para evitar queries adicionais
3. **Caching**: Considerar DAX se latência for crítica (não necessário inicialmente)
4. **Pagination**: Implementar para get_all_sessions se volume crescer

### Custos Estimados

**Assumindo**:
- 1000 sessões (~1MB total)
- 10.000 reads/mês
- 100 writes/mês (syncs ocasionais)

**Cálculo**:
- Storage: 1GB × $0.25 = $0.25/mês
- Reads: 10.000 × $0.25/1M = $0.0025/mês
- Writes: 100 × $1.25/1M = $0.000125/mês
- **Total: ~$0.25/mês**

## Security

### IAM Permissions

Lambda functions precisam:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:BatchWriteItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/reinvent-sessions-*",
        "arn:aws:dynamodb:*:*:table/reinvent-sessions-*/index/*"
      ]
    }
  ]
}
```

### Encryption

- **At Rest**: Encryption habilitada por padrão (AWS managed keys)
- **In Transit**: TLS 1.2+ para todas as conexões

## Monitoring and Observability

### CloudWatch Metrics

Monitorar:

- `ConsumedReadCapacityUnits`
- `ConsumedWriteCapacityUnits`
- `UserErrors` (4xx)
- `SystemErrors` (5xx)
- `SuccessfulRequestLatency`

### Logs

Adicionar logs estruturados:

```python
logger.info("Fetching session", extra={
    "session_id": session_id,
    "operation": "get_session_by_id"
})
```

### Alarms

Criar alarmes para:

- Latência > 100ms (p99)
- Error rate > 1%
- Throttling events

## Deployment Plan

### Fase 1: Preparação (Dia 1)
1. Criar tabela DynamoDB via CDK
2. Implementar SessionDynamoDTO
3. Implementar SessionRepositoryDynamo
4. Escrever testes unitários

### Fase 2: Migração (Dia 2)
1. Executar script de migração
2. Validar dados no DynamoDB
3. Atualizar Environments.get_session_repo()
4. Deploy em DEV

### Fase 3: Validação (Dia 3-7)
1. Testes de integração em DEV
2. Validação de performance
3. Monitoramento de erros

### Fase 4: Produção (Dia 8)
1. Deploy em PROD
2. Monitoramento intensivo por 24h
3. Remover código SQLite após 1 semana

## Open Questions

1. ~~Precisamos de sort key na tabela principal?~~ **Resolvido: Não, apenas PK**
2. Devemos implementar TTL para sessões antigas? **Decisão: Não inicialmente**
3. Precisamos de backup automático? **Decisão: Usar PITR (Point-in-time Recovery)**
4. Devemos criar novos endpoints para queries otimizadas? **Decisão: Sim, na próxima iteração**
