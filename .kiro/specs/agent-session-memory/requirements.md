# Requirements Document

## Introduction

This feature implements persistent session storage with short-term memory (STM) and long-term memory (LTM) capabilities for the re:Invent Planner Agent using Amazon Bedrock AgentCore Memory. The system will enable the agent to maintain conversation context across sessions, learn user preferences, extract facts, and provide personalized recommendations based on historical interactions.

## Glossary

- **Agent**: The re:Invent Planner AI assistant built with Strands framework
- **Session**: A single conversation instance between a user and the agent
- **Actor**: A unique user identifier across multiple sessions
- **STM (Short-Term Memory)**: Conversation persistence within a single session
- **LTM (Long-Term Memory)**: Cross-session memory with intelligent retrieval strategies
- **AgentCore Memory**: Amazon Bedrock service providing advanced memory capabilities
- **Memory Strategy**: A configured approach for storing and retrieving specific types of information
- **Namespace**: A scoped storage location for memory data (e.g., preferences, facts, summaries)
- **Session Manager**: Component responsible for persisting and retrieving agent state
- **DynamoDB**: AWS NoSQL database service used for session metadata storage
- **S3**: AWS object storage service used as fallback for session persistence

## Requirements

### Requirement 1

**User Story:** As a conference attendee, I want the agent to remember my previous conversations, so that I don't have to repeat my preferences and context in every new chat session.

#### Acceptance Criteria

1. WHEN a user starts a new conversation with an existing session ID THEN the Agent SHALL restore the previous conversation history
2. WHEN a user sends a message THEN the Agent SHALL persist the message to the session storage immediately
3. WHEN the agent responds to a message THEN the Agent SHALL persist the response to the session storage immediately
4. WHEN a session is restored THEN the Agent SHALL load all previous messages in chronological order
5. WHEN session restoration fails THEN the Agent SHALL start a new session and log the error without blocking the user

### Requirement 2

**User Story:** As a conference attendee, I want the agent to learn my preferences over time, so that it can provide increasingly personalized session recommendations.

#### Acceptance Criteria

1. WHEN a user expresses preferences across multiple sessions THEN the Agent SHALL store these preferences in long-term memory
2. WHEN a user asks for recommendations THEN the Agent SHALL retrieve relevant preferences from long-term memory
3. WHEN preferences are retrieved THEN the Agent SHALL apply a relevance score threshold of 0.7 or higher
4. WHEN preferences are retrieved THEN the Agent SHALL return the top 5 most relevant preference records
5. WHEN a user's preferences change THEN the Agent SHALL update the long-term memory with new preference information

### Requirement 3

**User Story:** As a conference attendee, I want the agent to remember facts about me and my interests, so that conversations feel more natural and contextual.

#### Acceptance Criteria

1. WHEN a user shares factual information about themselves THEN the Agent SHALL extract and store these facts in long-term memory
2. WHEN a user asks questions related to previously shared facts THEN the Agent SHALL retrieve relevant facts from long-term memory
3. WHEN facts are retrieved THEN the Agent SHALL apply a relevance score threshold of 0.3 or higher
4. WHEN facts are retrieved THEN the Agent SHALL return the top 10 most relevant fact records
5. WHEN factual information is stored THEN the Agent SHALL organize facts by actor ID for cross-session retrieval

### Requirement 4

**User Story:** As a conference attendee, I want the agent to summarize my previous sessions, so that I can quickly recall what we discussed without reading through entire conversation histories.

#### Acceptance Criteria

1. WHEN a session completes THEN the Agent SHALL generate a summary of the conversation
2. WHEN a user starts a new session THEN the Agent SHALL retrieve summaries from previous sessions
3. WHEN summaries are retrieved THEN the Agent SHALL apply a relevance score threshold of 0.5 or higher
4. WHEN summaries are retrieved THEN the Agent SHALL return the top 5 most relevant session summaries
5. WHEN a summary is generated THEN the Agent SHALL store it with both actor ID and session ID for scoped retrieval

### Requirement 5

**User Story:** As a system administrator, I want session metadata stored in DynamoDB, so that I can query, analyze, and manage user sessions efficiently.

#### Acceptance Criteria

1. WHEN a new session is created THEN the System SHALL store session metadata in DynamoDB
2. WHEN session metadata is stored THEN the System SHALL include session ID, actor ID, creation timestamp, and last updated timestamp
3. WHEN a session is accessed THEN the System SHALL update the last accessed timestamp in DynamoDB
4. WHEN querying sessions THEN the System SHALL support retrieval by session ID
5. WHEN querying sessions THEN the System SHALL support retrieval by actor ID to find all sessions for a user

### Requirement 6

**User Story:** As a system administrator, I want the memory system to be configurable, so that I can adjust retrieval parameters and storage strategies based on usage patterns.

#### Acceptance Criteria

1. WHEN configuring memory retrieval THEN the System SHALL support setting top_k values between 1 and 1000
2. WHEN configuring memory retrieval THEN the System SHALL support setting relevance_score thresholds between 0.0 and 1.0
3. WHEN configuring memory strategies THEN the System SHALL support enabling or disabling individual strategies
4. WHEN environment variables are provided THEN the System SHALL use them to configure memory settings
5. WHEN no configuration is provided THEN the System SHALL use sensible default values

### Requirement 7

**User Story:** As a developer, I want the memory system to integrate seamlessly with the existing agent architecture, so that I can enable memory features without major code refactoring.

#### Acceptance Criteria

1. WHEN creating an agent THEN the System SHALL accept an optional session_manager parameter
2. WHEN a session manager is provided THEN the Agent SHALL automatically persist conversations
3. WHEN no session manager is provided THEN the Agent SHALL function normally without persistence
4. WHEN the agent is deployed to Lambda THEN the System SHALL initialize the session manager from environment variables
5. WHEN the agent is deployed to Lambda THEN the System SHALL handle session manager initialization failures gracefully

### Requirement 8

**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can troubleshoot memory-related issues quickly.

#### Acceptance Criteria

1. WHEN a memory operation fails THEN the System SHALL log the error with context information
2. WHEN AgentCore Memory is unavailable THEN the System SHALL fall back to basic session persistence
3. WHEN DynamoDB operations fail THEN the System SHALL log the error and continue with in-memory state
4. WHEN S3 operations fail THEN the System SHALL log the error and attempt retry with exponential backoff
5. WHEN initialization fails THEN the System SHALL provide clear error messages indicating the root cause

### Requirement 9

**User Story:** As a security-conscious administrator, I want proper IAM permissions configured, so that the agent can access memory services securely without over-privileged access.

#### Acceptance Criteria

1. WHEN the Lambda function is deployed THEN the System SHALL have IAM permissions for AgentCore Memory operations
2. WHEN the Lambda function is deployed THEN the System SHALL have IAM permissions for DynamoDB read and write operations
3. WHEN the Lambda function is deployed THEN the System SHALL have IAM permissions for S3 read and write operations
4. WHEN IAM policies are created THEN the System SHALL follow the principle of least privilege
5. WHEN IAM policies are created THEN the System SHALL scope permissions to specific resources using ARNs

### Requirement 10

**User Story:** As a developer, I want the memory system to support both local development and production deployment, so that I can test memory features locally before deploying.

#### Acceptance Criteria

1. WHEN running locally THEN the System SHALL support FileSessionManager for development
2. WHEN running in production THEN the System SHALL use AgentCoreMemorySessionManager
3. WHEN environment variables indicate local mode THEN the System SHALL skip AgentCore Memory initialization
4. WHEN switching between environments THEN the System SHALL not require code changes
5. WHEN local session files exist THEN the System SHALL be able to restore sessions from the filesystem

### Requirement 11

**User Story:** As a developer, I want the system to be as simple as possible with minimal configuration, so that I can easily manage, deploy, and maintain it using AWS CDK.

#### Acceptance Criteria

1. WHEN deploying via CDK THEN the System SHALL automatically provision all required AWS resources
2. WHEN deploying via CDK THEN the System SHALL configure IAM permissions automatically
3. WHEN deploying via CDK THEN the System SHALL set environment variables for the Lambda function automatically
4. WHEN the CDK stack is defined THEN the System SHALL use sensible defaults that work out of the box
5. WHEN the CDK stack is defined THEN the System SHALL minimize the number of configuration parameters required
6. WHEN AgentCore Memory resources are created THEN the System SHALL use CDK constructs to define memory strategies declaratively
7. WHEN updating the deployment THEN the System SHALL support incremental updates without manual intervention
8. WHEN troubleshooting THEN the System SHALL provide clear CloudWatch logs with structured logging
