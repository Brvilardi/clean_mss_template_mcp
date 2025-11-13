# Requirements Document

## Introduction

Este documento define os requisitos para migrar o armazenamento de sessões do re:Invent de SQLite para DynamoDB. A migração visa eliminar problemas de persistência em ambiente Lambda, melhorar performance e manter consistência arquitetural com o padrão já estabelecido para Users.

## Glossary

- **Session Repository**: Componente responsável por operações de persistência de sessões do re:Invent
- **DynamoDB**: Serviço de banco de dados NoSQL serverless da AWS
- **SQLite**: Banco de dados relacional baseado em arquivo atualmente em uso
- **Session Entity**: Entidade de domínio representando uma sessão do re:Invent
- **DTO (Data Transfer Object)**: Objeto responsável por conversão entre entidades e formato de armazenamento
- **Lambda Function**: Função serverless AWS que executa a lógica de negócio
- **API Sync**: Operação de sincronização de dados com a API externa do re:Invent
- **Clean Architecture**: Padrão arquitetural que separa domínio, casos de uso e infraestrutura

## Requirements

### Requirement 1: Implementar Repositório DynamoDB

**User Story:** Como desenvolvedor, quero um repositório DynamoDB para sessões, para que o sistema funcione corretamente em ambiente Lambda serverless

#### Acceptance Criteria

1. WHEN o sistema inicializa, THE Session Repository DynamoDB SHALL conectar-se à tabela DynamoDB configurada via variáveis de ambiente
2. THE Session Repository DynamoDB SHALL implementar todos os métodos da interface ISessionRepository
3. THE Session Repository DynamoDB SHALL utilizar apenas partition key "SESSION#{session_id}" sem sort key
4. THE Session Repository DynamoDB SHALL armazenar todos os 17 atributos da entidade Session
5. THE Session Repository DynamoDB SHALL serializar listas (speakers, topics, areas_of_interest, features) como atributos DynamoDB List
6. THE Session Repository DynamoDB SHALL implementar método get_sessions_by_venue que consulta via GSI
7. THE Session Repository DynamoDB SHALL implementar método get_sessions_by_day que consulta via GSI
8. THE Session Repository DynamoDB SHALL implementar método get_sessions_by_level que consulta via GSI

### Requirement 2: Criar DTO para DynamoDB

**User Story:** Como desenvolvedor, quero um DTO específico para DynamoDB, para que a conversão entre entidade e armazenamento seja consistente com o padrão do projeto

#### Acceptance Criteria

1. THE SessionDynamoDTO SHALL implementar método from_entity que converte Session para SessionDynamoDTO
2. THE SessionDynamoDTO SHALL implementar método to_dynamo que converte SessionDynamoDTO para dict compatível com DynamoDB
3. THE SessionDynamoDTO SHALL implementar método from_dynamo que converte dict do DynamoDB para SessionDynamoDTO
4. THE SessionDynamoDTO SHALL implementar método to_entity que converte SessionDynamoDTO para Session
5. THE SessionDynamoDTO SHALL incluir atributo "entity" com valor "session" para identificação de tipo no DynamoDB

### Requirement 3: Manter Compatibilidade com Interface Existente

**User Story:** Como desenvolvedor, quero que a migração não quebre código existente, para que os casos de uso continuem funcionando sem modificações

#### Acceptance Criteria

1. THE Session Repository DynamoDB SHALL implementar método get_all_sessions retornando List[Session]
2. THE Session Repository DynamoDB SHALL implementar método get_session_by_id retornando Session
3. THE Session Repository DynamoDB SHALL implementar método sync_sessions_from_api retornando Dict[str, int] com contadores
4. WHEN uma sessão não é encontrada, THE Session Repository DynamoDB SHALL lançar exceção NoItemsFound
5. WHEN ocorre erro de parsing de API, THE Session Repository DynamoDB SHALL lançar exceção EntityError

### Requirement 3.1: Estender Interface com Queries Otimizadas

**User Story:** Como desenvolvedor, quero métodos de busca otimizados por venue, dia e level, para que as consultas mais comuns sejam eficientes

#### Acceptance Criteria

1. THE ISessionRepository SHALL adicionar método get_sessions_by_venue que aceita venue_name como parâmetro
2. THE ISessionRepository SHALL adicionar método get_sessions_by_day que aceita day como parâmetro
3. THE ISessionRepository SHALL adicionar método get_sessions_by_level que aceita level_value como parâmetro
4. THE Session Repository DynamoDB SHALL implementar get_sessions_by_venue usando query no GSI-Venue
5. THE Session Repository DynamoDB SHALL implementar get_sessions_by_day usando query no GSI-Day
6. THE Session Repository DynamoDB SHALL implementar get_sessions_by_level usando query no GSI-Level
7. THE Session Repository Mock SHALL implementar os novos métodos filtrando a lista em memória

### Requirement 4: Provisionar Infraestrutura DynamoDB

**User Story:** Como DevOps, quero infraestrutura DynamoDB provisionada via CDK, para que o deployment seja automatizado e reproduzível

#### Acceptance Criteria

1. THE CDK Stack SHALL criar tabela DynamoDB separada exclusiva para Sessions
2. THE Sessions DynamoDB Table SHALL utilizar billing mode PAY_PER_REQUEST para escalabilidade automática
3. THE Sessions DynamoDB Table SHALL ter apenas partition key "PK" do tipo String sem sort key
4. THE Sessions DynamoDB Table SHALL criar GSI "GSI-Venue" com partition key "venue_name" e sort key "start_datetime"
6. THE DynamoDB Table SHALL criar GSI "GSI-Day" com partition key "day" e sort key "start_datetime"
7. THE DynamoDB Table SHALL criar GSI "GSI-Level" com partition key "level_value" e sort key "start_datetime"
8. THE CDK Stack SHALL conceder permissões de leitura e escrita às Lambda functions de sessões
9. THE CDK Stack SHALL conceder permissões de query nos GSIs às Lambda functions de sessões

### Requirement 5: Atualizar Configuração de Ambiente

**User Story:** Como desenvolvedor, quero configuração centralizada de repositório, para que seja fácil alternar entre implementações

#### Acceptance Criteria

1. THE Environments Class SHALL implementar método get_session_repo que retorna classe de repositório baseada em variável STAGE
2. WHEN STAGE é "TEST", THE get_session_repo SHALL retornar SessionRepositoryMock
3. WHEN STAGE é "DEV" ou "PROD", THE get_session_repo SHALL retornar SessionRepositoryDynamo
4. THE Environments Class SHALL expor variáveis de configuração DynamoDB (table_name, region, endpoint_url)
5. THE .env file SHALL conter todas as variáveis necessárias para configuração DynamoDB

### Requirement 6: Migrar Dados Existentes

**User Story:** Como administrador, quero migrar dados existentes do SQLite para DynamoDB, para que não haja perda de informação

#### Acceptance Criteria

1. THE Migration Script SHALL ler todas as sessões do banco SQLite existente
2. THE Migration Script SHALL converter cada sessão SQLite para formato DynamoDB
3. THE Migration Script SHALL inserir sessões no DynamoDB usando batch_write_item para eficiência
4. THE Migration Script SHALL reportar quantidade de sessões migradas com sucesso
5. IF ocorrer erro em uma sessão, THE Migration Script SHALL registrar erro e continuar com as demais

### Requirement 7: Remover Dependências SQLite

**User Story:** Como desenvolvedor, quero remover código SQLite obsoleto, para que o projeto fique mais limpo e manutenível

#### Acceptance Criteria

1. THE Project SHALL remover arquivo session_repository_sqlite.py
2. THE Project SHALL remover arquivo session_sqlite_dto.py
3. THE Project SHALL remover diretório src/shared/infra/external/sqlite
4. THE Project SHALL remover arquivo de banco de dados reinvent_sessions.db
5. THE Project SHALL remover dependências SQLite do requirements.txt se não forem usadas em outros lugares

### Requirement 8: Atualizar Lambda Functions

**User Story:** Como desenvolvedor, quero que as Lambda functions usem o novo repositório, para que o sistema funcione em produção

#### Acceptance Criteria

1. THE get_all_sessions Lambda SHALL adicionar funções à lista functions_that_need_dynamo_permissions no CDK
2. THE sync_sessions Lambda SHALL adicionar funções à lista functions_that_need_dynamo_permissions no CDK
3. THE Lambda Functions SHALL receber variáveis de ambiente necessárias para conexão DynamoDB
4. THE Lambda Functions SHALL manter timeout de 30 segundos para operações de sync
5. THE Lambda Functions SHALL manter memory_size de 512MB para processamento de listas grandes

### Requirement 9: Validar Funcionalidade

**User Story:** Como QA, quero validar que todas as operações funcionam corretamente, para garantir que a migração foi bem-sucedida

#### Acceptance Criteria

1. WHEN get_all_sessions é chamado, THE System SHALL retornar todas as sessões do DynamoDB
2. WHEN get_session_by_id é chamado com ID válido, THE System SHALL retornar a sessão correspondente
3. WHEN get_session_by_id é chamado com ID inválido, THE System SHALL lançar NoItemsFound
4. WHEN sync_sessions_from_api é chamado, THE System SHALL atualizar DynamoDB com dados da API
5. THE System SHALL manter performance de resposta abaixo de 500ms para get_session_by_id
