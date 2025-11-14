# Implementation Plan

- [x] 1. Provisionar infraestrutura DynamoDB via CDK
- [x] 1.1 Criar SessionsDynamoTable (tabela exclusiva para Sessions)
  - Criar arquivo iac/iac/sessions_dynamo_table.py seguindo padrão de template_dynamo_table.py
  - Criar classe SessionsDynamoTable que herda de Construct
  - Criar tabela com apenas partition_key "PK" (String) sem sort_key
  - Configurar billing_mode como PAY_PER_REQUEST
  - Configurar removal_policy como RETAIN para proteção de dados
  - _Requirements: 4.1, 4.2, 4.3_

- [x] 1.2 Adicionar Global Secondary Indexes na SessionsDynamoTable
  - Adicionar GSI-Venue usando table.add_global_secondary_index (PK: venue_name, SK: start_datetime)
  - Adicionar GSI-Day usando table.add_global_secondary_index (PK: day, SK: start_datetime)
  - Adicionar GSI-Level usando table.add_global_secondary_index (PK: level_value Number, SK: start_datetime)
  - Configurar projection_type como dynamodb.ProjectionType.ALL para todos os GSIs
  - _Requirements: 4.5, 4.6, 4.7_

- [x] 1.3 Integrar SessionsDynamoTable no TemplateStack
  - Importar SessionsDynamoTable em template_stack.py
  - Instanciar SessionsDynamoTable no __init__ do TemplateStack
  - Adicionar variável de ambiente SESSIONS_DYNAMO_TABLE_NAME com table_name da SessionsDynamoTable
  - Adicionar variável de ambiente SESSIONS_DYNAMO_PARTITION_KEY com valor "PK"
  - _Requirements: 4.1, 5.4_

- [x] 1.4 Configurar permissões IAM no Lambda Stack
  - Criar lista functions_that_need_sessions_dynamo_permissions no lambda_stack.py
  - Adicionar get_all_sessions_function à lista functions_that_need_sessions_dynamo_permissions
  - Adicionar sync_sessions_function à lista functions_that_need_sessions_dynamo_permissions
  - No template_stack.py, conceder grant_read_write_data da SessionsDynamoTable para funções da lista
  - Garantir que permissões incluem dynamodb:Query para os GSIs
  - _Requirements: 4.8, 4.9, 8.1, 8.2_

- [x] 1.5 Criar script de setup e load para DynamoDB Local
  - Criar script load_session_mock_to_dynamo.py em src/shared/infra/repositories/
  - Implementar função setup_dynamo_table que cria tabela com apenas PK (sem SK)
  - Implementar criação do GSI-Venue (PK: venue_name, SK: start_datetime) na função setup
  - Implementar criação do GSI-Day (PK: day, SK: start_datetime) na função setup
  - Implementar criação do GSI-Level (PK: level_value Number, SK: start_datetime) na função setup
  - Implementar função load_mock_to_local_dynamo que carrega dados do SessionRepositoryMock
  - Atualizar iac/local/README.md com comando para rodar o script de sessions
  - Atualizar iac/local/configure_dynamodb.md com seção sobre load_session_mock_to_dynamo
  - _Requirements: 5.4_

- [x] 2. Criar SessionDynamoDTO
  - Implementar classe SessionDynamoDTO com todos os 17 atributos da entidade Session
  - Implementar método from_entity para converter Session para SessionDynamoDTO
  - Implementar método to_dynamo para converter SessionDynamoDTO para dict DynamoDB
  - Implementar método from_dynamo para converter dict DynamoDB para SessionDynamoDTO
  - Implementar método to_entity para converter SessionDynamoDTO para Session
  - Garantir que atributo "entity" seja sempre "session" no formato DynamoDB
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Estender ISessionRepository com novos métodos
  - Adicionar método abstrato get_sessions_by_venue na interface ISessionRepository
  - Adicionar método abstrato get_sessions_by_day na interface ISessionRepository
  - Adicionar método abstrato get_sessions_by_level na interface ISessionRepository
  - _Requirements: 3.1.1, 3.1.2, 3.1.3_

- [x] 4. Atualizar SessionRepositoryMock com novos métodos
  - Implementar get_sessions_by_venue filtrando lista em memória
  - Implementar get_sessions_by_day filtrando lista em memória
  - Implementar get_sessions_by_level filtrando lista em memória
  - Garantir que resultados sejam ordenados por start_datetime
  - _Requirements: 3.1.7_

- [x] 5. Implementar SessionRepositoryDynamo
- [x] 5.1 Criar estrutura básica do repositório
  - Criar classe SessionRepositoryDynamo que implementa ISessionRepository
  - Implementar __init__ para inicializar DynamoDatasource com configurações do Environments (usar variáveis SESSIONS_DYNAMO_*)
  - Implementar método estático partition_key_format que retorna "SESSION#{session_id}"
  - Nota: Não precisa de sort_key_format pois tabela não tem SK
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 5.2 Implementar operações básicas de CRUD
  - Implementar get_session_by_id usando GetItem com apenas PK (sem SK)
  - Implementar get_all_sessions usando Scan com filter entity='session'
  - Implementar sync_sessions_from_api com fetch da API e batch write
  - Garantir que NoItemsFound seja lançado quando sessão não for encontrada
  - Garantir que EntityError seja lançado quando dados da API forem inválidos
  - _Requirements: 1.2, 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 5.3 Implementar queries otimizadas com GSIs
  - Implementar get_sessions_by_venue usando Query no GSI-Venue
  - Implementar get_sessions_by_day usando Query no GSI-Day
  - Implementar get_sessions_by_level usando Query no GSI-Level
  - Garantir que resultados sejam ordenados por start_datetime
  - _Requirements: 1.6, 1.7, 1.8, 3.1.4, 3.1.5, 3.1.6_

- [x] 6. Atualizar configuração de ambiente
  - Implementar método get_session_repo no Environments
  - Configurar retorno de SessionRepositoryMock quando STAGE é "TEST"
  - Configurar retorno de SessionRepositoryDynamo quando STAGE é "DEV" ou "PROD"
  - Adicionar variáveis de ambiente no .env (SESSIONS_DYNAMO_TABLE_NAME, SESSIONS_DYNAMO_PARTITION_KEY)
  - Atualizar presenters de get_all_sessions e sync_sessions para usar Environments.get_session_repo()
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.3_

- [x] 7. Testar localmente com DynamoDB Local
  - Iniciar DynamoDB Local via docker: `docker run -p 8000:8000 amazon/dynamodb-local -sharedDB -inMemory`
  - Executar script load_session_mock_to_dynamo.py para criar tabela e carregar dados
  - Testar get_session_by_id com DynamoDB Local retorna sessão correta
  - Testar get_sessions_by_venue com DynamoDB Local retorna sessões filtradas
  - Testar get_sessions_by_day com DynamoDB Local retorna sessões filtradas
  - Testar get_sessions_by_level com DynamoDB Local retorna sessões filtradas
  - Validar que GSIs estão funcionando e ordenando por start_datetime
  - _Requirements: 9.1, 9.2, 9.5_

<!-- - [ ] 8. Criar script de migração de dados
  - Criar script migrate_sqlite_to_dynamodb.py
  - Implementar leitura de todas as sessões do SQLite
  - Implementar conversão de SessionSQLiteDTO para SessionDynamoDTO
  - Implementar batch write para DynamoDB (25 items por batch)
  - Implementar validação de contagem de registros migrados
  - Implementar geração de relatório de migração (sucesso, erros, total)
  - Adicionar tratamento de erros para continuar migração mesmo com falhas individuais
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_ -->

- [x] 9. Validar funcionalidade end-to-end em DEV
  - Testar get_all_sessions retorna todas as sessões
  - Testar get_session_by_id com ID válido retorna sessão correta
  - Testar get_session_by_id com ID inválido lança NoItemsFound
  - Testar get_sessions_by_venue retorna sessões filtradas e ordenadas
  - Testar get_sessions_by_day retorna sessões filtradas e ordenadas
  - Testar get_sessions_by_level retorna sessões filtradas e ordenadas
  - Testar sync_sessions_from_api atualiza DynamoDB corretamente
  - Validar performance de get_session_by_id < 500ms
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 10. Remover código SQLite obsoleto
  - Remover arquivo session_repository_sqlite.py
  - Remover arquivo session_sqlite_dto.py
  - Remover diretório src/shared/infra/external/sqlite
  - Remover arquivo de banco de dados reinvent_sessions.db se existir
  - Verificar e remover dependências SQLite do requirements.txt se não usadas
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
