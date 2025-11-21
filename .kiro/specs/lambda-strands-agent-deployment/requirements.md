# Requirements Document

## Introduction

This document specifies the requirements for redeploying the Strands-based re:Invent planner agent using AWS Lambda with AWS Lambda Web Adapter, replacing the current Bedrock Agent Core deployment. This approach aligns with the existing MCP server deployment pattern, providing a simpler, more cost-effective serverless architecture while maintaining all agent functionality.

## Glossary

- **Strands Agent**: An AI agent built using the Strands framework that provides conversational assistance for re:Invent planning
- **AWS Lambda Web Adapter**: A tool that enables running web applications (FastAPI, Flask, etc.) on AWS Lambda
- **MCP Server**: Model Context Protocol server that exposes re:Invent session data through standardized tool interfaces
- **FastAPI**: Python web framework used for the agent's HTTP interface
- **API Gateway**: AWS service that provides HTTP endpoints for Lambda functions
- **Lambda Layer**: Reusable code package that can be attached to Lambda functions
- **ARM64**: CPU architecture used for Lambda functions (more cost-effective than x86)

## Requirements

### Requirement 1: Lambda Function Configuration

**User Story:** As a developer, I want to deploy the Strands agent as a Lambda function with AWS Lambda Web Adapter, so that I can leverage serverless benefits without the complexity of Bedrock Agent Core.

#### Acceptance Criteria

1. THE Strands Agent SHALL be deployed as an AWS Lambda function using Python 3.14 runtime
2. THE Strands Agent SHALL use ARM64 architecture for cost optimization
3. THE Strands Agent SHALL include the AWS Lambda Web Adapter layer
4. THE Strands Agent SHALL use the existing FastAPI entrypoint at `src/strands-agent/entrypoint.py`
5. THE Strands Agent SHALL configure the Lambda Web Adapter to route requests to port 8000

### Requirement 2: Handler Script Configuration

**User Story:** As a developer, I want a simple handler script that starts the FastAPI application, so that the Lambda Web Adapter can properly route requests.

#### Acceptance Criteria

1. THE Strands Agent SHALL include a `run.sh` handler script in `src/strands-agent/`
2. THE handler script SHALL start the FastAPI application using uvicorn
3. THE handler script SHALL bind to host 0.0.0.0 and port 8000
4. THE handler script SHALL be executable
5. THE handler script SHALL follow the same pattern as the MCP server's `run.sh`

### Requirement 3: Environment Variable Configuration

**User Story:** As a developer, I want proper environment variables configured for the Lambda Web Adapter, so that HTTP requests are correctly routed to the FastAPI application.

#### Acceptance Criteria

1. THE Lambda function SHALL set `AWS_LAMBDA_EXEC_WRAPPER` to "/opt/bootstrap"
2. THE Lambda function SHALL set `AWS_LWA_PORT` to "8000"
3. THE Lambda function SHALL set `AWS_LWA_REMOVE_BASE_PATH` to the API Gateway base path
4. THE Lambda function SHALL include the `MCP_ENDPOINT` environment variable
5. THE Lambda function SHALL include standard environment variables (STAGE, AWS_REGION, LOG_LEVEL)

### Requirement 4: API Gateway Integration

**User Story:** As a user, I want to access the Strands agent through an HTTP endpoint, so that I can interact with the agent via standard HTTP requests.

#### Acceptance Criteria

1. THE Strands Agent SHALL be accessible through API Gateway
2. THE API Gateway SHALL create a resource path for the agent (e.g., `/agent`)
3. THE API Gateway SHALL support the ANY method to handle all HTTP verbs
4. THE API Gateway SHALL integrate with the Lambda function using LambdaIntegration
5. THE API Gateway SHALL use the same API Gateway instance as other services

### Requirement 5: Lambda Layer Dependencies

**User Story:** As a developer, I want the agent's Python dependencies packaged as Lambda layers, so that deployment is efficient and follows AWS best practices.

#### Acceptance Criteria

1. THE Strands Agent SHALL use the shared dependencies layer from the existing infrastructure
2. THE Strands Agent SHALL use the AWS Lambda Web Adapter layer (ARM64 version)
3. THE Lambda function SHALL attach both layers in the correct order
4. THE dependencies layer SHALL include all packages from `src/strands-agent/requirements.txt`
5. THE Lambda Web Adapter layer SHALL use the official AWS-provided layer ARN

### Requirement 6: CDK Stack Implementation

**User Story:** As a developer, I want a CDK stack that deploys the Lambda-based agent, so that infrastructure is managed as code and deployments are repeatable.

#### Acceptance Criteria

1. THE CDK stack SHALL be named `StrandsAgentStack` and located in `iac/iac/strands_agent_stack.py`
2. THE CDK stack SHALL follow the same pattern as `MCPStack`
3. THE CDK stack SHALL create a Lambda function with the agent code
4. THE CDK stack SHALL configure API Gateway integration
5. THE CDK stack SHALL set appropriate memory size (512 MB minimum) and timeout (30 seconds minimum)

### Requirement 7: IAM Permissions

**User Story:** As a developer, I want the Lambda function to have appropriate IAM permissions, so that the agent can invoke Bedrock models and write logs.

#### Acceptance Criteria

1. THE Lambda function SHALL have permissions to invoke Bedrock models
2. THE Lambda function SHALL have permissions to write to CloudWatch Logs
3. THE Lambda function SHALL use the principle of least privilege
4. THE Lambda function SHALL have permissions to invoke the MCP server endpoint
5. THE Lambda function SHALL NOT have unnecessary permissions

### Requirement 8: Resource Sizing

**User Story:** As a developer, I want appropriate resource allocation for the Lambda function, so that the agent performs well without excessive costs.

#### Acceptance Criteria

1. THE Lambda function SHALL have a minimum memory size of 512 MB
2. THE Lambda function SHALL have a timeout of at least 30 seconds
3. THE Lambda function SHALL support timeout configuration via CDK parameters
4. THE Lambda function SHALL support memory configuration via CDK parameters
5. THE Lambda function SHALL use ARM64 architecture for cost optimization

### Requirement 9: Deployment Integration

**User Story:** As a developer, I want the agent stack integrated into the main CDK application, so that it deploys alongside other infrastructure components.

#### Acceptance Criteria

1. THE StrandsAgentStack SHALL be imported in `iac/app.py`
2. THE StrandsAgentStack SHALL be instantiated with the main CDK app
3. THE StrandsAgentStack SHALL receive the API Gateway resource as a parameter
4. THE StrandsAgentStack SHALL receive environment variables as a parameter
5. THE StrandsAgentStack SHALL receive the dependencies layer as a parameter

### Requirement 10: Backward Compatibility

**User Story:** As a developer, I want the agent's application code to remain unchanged, so that the migration from Agent Core to Lambda is transparent to the agent logic.

#### Acceptance Criteria

1. THE existing `src/strands-agent/entrypoint.py` SHALL work without modifications
2. THE existing `src/strands-agent/agent.py` SHALL work without modifications
3. THE existing `src/strands-agent/config.py` SHALL work without modifications
4. THE agent's FastAPI endpoints SHALL remain the same (`/invocations`, `/ping`)
5. THE agent's request/response format SHALL remain unchanged

### Requirement 11: Removal of Agent Core Infrastructure

**User Story:** As a developer, I want to remove the Agent Core deployment infrastructure, so that the codebase only contains the Lambda-based deployment.

#### Acceptance Criteria

1. THE Dockerfile in `src/strands-agent/` SHALL be removed or archived
2. THE Agent Core-specific CDK code SHALL be removed from `iac/iac/strands_agent_stack.py`
3. THE ECR repository creation SHALL be removed
4. THE Agent Core custom resource SHALL be removed
5. THE documentation SHALL be updated to reflect Lambda deployment

### Requirement 12: Testing and Verification

**User Story:** As a developer, I want to verify that the Lambda-based agent works correctly, so that I can ensure feature parity with the Agent Core deployment.

#### Acceptance Criteria

1. THE Lambda function SHALL respond to health check requests at `/ping`
2. THE Lambda function SHALL process agent invocations at `/invocations`
3. THE agent SHALL successfully connect to the MCP server
4. THE agent SHALL successfully invoke MCP tools
5. THE agent SHALL return properly formatted responses

### Requirement 13: Cost Optimization

**User Story:** As a developer, I want the Lambda deployment to be cost-effective, so that running costs are minimized compared to Agent Core.

#### Acceptance Criteria

1. THE Lambda function SHALL use ARM64 architecture (20% cost savings)
2. THE Lambda function SHALL use appropriate memory allocation (not over-provisioned)
3. THE Lambda function SHALL have a reasonable timeout (not excessive)
4. THE Lambda function SHALL leverage Lambda's pay-per-use pricing model
5. THE deployment SHALL eliminate Agent Core runtime costs

### Requirement 14: Monitoring and Logging

**User Story:** As a developer, I want proper logging and monitoring for the Lambda function, so that I can troubleshoot issues and monitor performance.

#### Acceptance Criteria

1. THE Lambda function SHALL write logs to CloudWatch Logs
2. THE Lambda function SHALL include structured logging with relevant context
3. THE Lambda function SHALL log agent initialization events
4. THE Lambda function SHALL log MCP tool invocations
5. THE Lambda function SHALL log errors with appropriate detail

### Requirement 15: Documentation Updates

**User Story:** As a developer, I want updated documentation that reflects the Lambda deployment, so that future developers understand the architecture.

#### Acceptance Criteria

1. THE `src/strands-agent/README.md` SHALL be updated with Lambda deployment information
2. THE README SHALL include instructions for local testing
3. THE README SHALL document environment variables
4. THE README SHALL explain the Lambda Web Adapter configuration
5. THE README SHALL include deployment commands
