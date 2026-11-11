# Implementation Plan

- [x] 1. Install Strands session management dependencies
  - Add `strands` to `src/strands-agent/requirements.txt` (if not already present)
  - Install locally for development: `pip install strands`
  - _Requirements: 7.1, 10.1_

- [x] 2. Update agent to use FileSessionManager for local development
  - Modify `src/strands-agent/agent.py` create_agent() to accept optional session_id and actor_id parameters
  - Import FileSessionManager from strands.session.file_session_manager
  - Create FileSessionManager with session_id when provided
  - Pass session_manager to Agent constructor
  - _Requirements: 7.1, 7.2, 7.3, 10.1, 10.2, 10.3_

- [x] 2.1 Write unit tests for agent with FileSessionManager
  - Test agent creation with FileSessionManager
  - Test agent creation without session manager (default behavior)
  - _Requirements: 7.1, 10.1, 10.2_

- [x] 3. Update entrypoint to extract session_id and actor_id
  - Modify `src/strands-agent/entrypoint.py` to extract session_id and actor_id from request body
  - Pass session_id and actor_id to create_agent()
  - Add error handling for missing session_id or actor_id (use defaults if not provided)
  - Add structured logging for session operations
  - _Requirements: 7.4, 7.5, 8.1, 8.5, 11.8_

- [ ]* 3.1 Write unit tests for entrypoint session handling
  - Test session_id and actor_id extraction from request
  - Test default values when not provided
  - Test error handling
  - _Requirements: 7.4, 7.5_

- [x] 4. Test local development with FileSessionManager
  - Run agent locally with session_id and actor_id
  - Verify conversation persistence to local filesystem
  - Test session restoration by restarting agent with same session_id
  - Verify messages are preserved in chronological order
  - _Requirements: 10.1, 10.2, 10.4, 10.5, 1.1, 1.2, 1.3, 1.4_

- [ ]* 4.1 Write property test for session restoration preserves message history
  - **Property 1: Session Restoration Preserves Message History**
  - **Validates: Requirements 1.1, 1.4**

- [ ]* 4.2 Write property test for message persistence is immediate
  - **Property 2: Message Persistence is Immediate**
  - **Validates: Requirements 1.2, 1.3**

- [x] 5. Install AgentCore Memory SDK
  - Add `bedrock-agentcore[strands-agents]` to `src/strands-agent/requirements.txt`
  - Add `bedrock-agentcore[strands-agents]` to `iac/lambda_agent_dependencies/requirements.txt`
  - _Requirements: 7.1, 10.1_

- [ ] 6. Update agent to support AgentCore Memory
  - Import AgentCoreMemoryConfig and AgentCoreMemorySessionManager
  - Check for AGENTCORE_MEMORY_ID environment variable
  - If set, create AgentCoreMemoryConfig with memory_id, session_id, actor_id
  - Configure retrieval_config for three namespaces with appropriate top_k and relevance_score
  - Create AgentCoreMemorySessionManager with config
  - If not set, use FileSessionManager (local development)
  - _Requirements: 7.1, 7.2, 7.3, 10.1, 10.2, 10.3, 2.3, 2.4, 3.3, 3.4, 4.3, 4.4, 6.1, 6.2_

- [ ]* 6.1 Write unit tests for agent with AgentCore Memory
  - Test agent creation with AgentCoreMemorySessionManager
  - Test fallback to FileSessionManager when AGENTCORE_MEMORY_ID not set
  - Test configuration validation
  - _Requirements: 7.1, 10.1, 10.2_

- [ ] 7. Create AgentCore Memory resource via CDK
  - Create CDK construct in `iac/iac/agent_memory_stack.py` to provision AgentCore Memory
  - Configure three memory strategies: summaryMemoryStrategy, userPreferenceMemoryStrategy, semanticMemoryStrategy
  - Set namespaces: `/summaries/{actorId}/{sessionId}`, `/preferences/{actorId}`, `/facts/{actorId}`
  - Add IAM permissions for AgentCore Memory operations to Lambda execution role
  - Export memory ID as environment variable `AGENTCORE_MEMORY_ID`
  - _Requirements: 9.1, 9.2, 11.1, 11.2, 11.3, 11.6_

- [ ] 8. Integrate AgentMemoryStack into main CDK stack
  - Update `iac/app.py` to instantiate AgentMemoryStack
  - Pass memory ID to StrandsAgentStack as environment variable
  - Update Strands agent Lambda with AgentCore Memory IAM permissions
  - _Requirements: 11.1, 11.2, 11.3, 11.7_

- [ ] 9. Deploy and test with AgentCore Memory
  - Deploy CDK stack to create AgentCore Memory resource
  - Test agent with session_id and actor_id in production
  - Verify conversation persistence across invocations
  - Verify long-term memory strategies (preferences, facts, summaries)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 3.1, 3.2, 4.1, 4.2_

- [ ]* 9.1 Write property test for preference storage persists across sessions
  - **Property 4: Preference Storage Persists Across Sessions**
  - **Validates: Requirements 2.1, 2.2**

- [ ]* 9.2 Write property test for fact extraction and storage
  - **Property 7: Fact Extraction and Storage**
  - **Validates: Requirements 3.1, 3.5**

- [ ]* 9.3 Write property test for session summary generation
  - **Property 9: Session Summary Generation**
  - **Validates: Requirements 4.1, 4.5**

- [ ] 10. Add error handling and monitoring
  - Add try-catch for AgentCore Memory initialization with fallback to FileSessionManager
  - Add structured error logging with context
  - Add CloudWatch metrics for session operations
  - _Requirements: 8.1, 8.2, 8.5, 11.8_

- [ ]* 10.1 Write unit tests for error handling
  - Test fallback to FileSessionManager when AgentCore Memory unavailable
  - Test error logging
  - _Requirements: 8.2, 8.5_

- [ ] 11. Final checkpoint - Verify all requirements
  - Test end-to-end session persistence
  - Test session restoration across multiple invocations
  - Test long-term memory retrieval
  - Verify all acceptance criteria are met
  - Ask the user if questions arise
