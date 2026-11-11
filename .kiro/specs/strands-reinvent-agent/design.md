# Design Document

## Overview

This document describes the design for a Strands-based AI agent that helps users organize their AWS re:Invent conference agenda. The agent will be deployed to AWS Bedrock Agent Core and will leverage the existing MCP server to access session data. The agent will provide intelligent recommendations based on re:Invent best practices, venue logistics, and session characteristics.

### Key Design Goals

1. **Conversational Interface**: Natural language interaction for session discovery and schedule building
2. **Intelligent Recommendations**: Context-aware suggestions based on venue distances, recording status, and user preferences
3. **Scalable Deployment**: Serverless deployment using AWS Bedrock Agent Core
4. **MCP Integration**: Seamless connection to the existing re:Invent MCP server
5. **Best Practices Knowledge**: Built-in understanding of re:Invent conference logistics

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│                 │
│  User/Client    │
│                 │
└────────┬────────┘
         │
         │ HTTP/API Gateway
         │
         ▼
┌─────────────────────────────────────┐
│                                     │
│  AWS Bedrock Agent Core Runtime     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │                               │ │
│  │  Strands re:Invent Agent      │ │
│  │                               │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │  Agent Core             │ │ │
│  │  │  - Conversation State   │ │ │
│  │  │  - Session Management   │ │ │
│  │  │  - System Prompt with   │ │ │
│  │  │    Venue Knowledge      │ │ │
│  │  └─────────────────────────┘ │ │
│  │                               │ │
│  │  ┌─────────────────────────┐ │ │
│  │  │  MCP Client             │ │ │
│  │  │  - Tool Discovery       │ │ │
│  │  │  - Tool Invocation      │ │ │
│  │  └─────────────────────────┘ │ │
│  │                               │ │
│  └───────────────────────────────┘ │
│                                     │
└──────────────┬──────────────────────┘
               │
               │ HTTP (Streamable-HTTP)
               │
               ▼
┌─────────────────────────────────────┐
│                                     │
│  API Gateway                        │
│                                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│                                     │
│  Lambda: MCP Server                 │
│  (FastMCP)                          │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  MCP Tools                    │ │
│  │  - get_all_sessions_paginated │ │
│  │  - get_session_by_short_id    │ │
│  │  - get_sessions_by_venue      │ │
│  │  - get_sessions_by_day        │ │
│  │  - get_sessions_by_level      │ │
│  └───────────────────────────────┘ │
│                                     │
└──────────────┬──────────────────────┘
               │
               │ Calls other Lambda functions
               │
               ▼
┌─────────────────────────────────────┐
│                                     │
│  Lambda: re:Invent Planner API      │
│  (Session Query Functions)          │
│                                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│                                     │
│  DynamoDB                           │
│  (Session Data)                     │
│                                     │
└─────────────────────────────────────┘
```

### Component Responsibilities

#### Strands Agent
- Processes user queries in natural language
- Maintains conversation context and state
- Invokes MCP tools to retrieve session data
- Applies re:Invent best practices to recommendations
- Formats responses in a conversational manner

#### MCP Client
- Establishes connection to the MCP server
- Discovers available tools
- Handles tool invocation and response parsing
- Manages connection lifecycle

#### Knowledge Base
- Stores venue distance information
- Contains re:Invent best practices
- Provides context for intelligent recommendations

## Components and Interfaces

### 1. Agent Module (`src/strands-agent/agent.py`)

The main agent implementation using Strands framework.

```python
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
import os

# System prompt with embedded venue knowledge and best practices
SYSTEM_PROMPT = """You are a helpful AI assistant for AWS re:Invent conference planning.

Your role is to help attendees:
- Discover sessions based on their interests
- Build personalized schedules
- Avoid scheduling conflicts
- Consider venue logistics and travel times
- Prioritize non-recorded sessions when conflicts occur

## Venue Knowledge

### Venue Locations and Characteristics
- **Mandalay Bay**: South Strip, large venue. Far from other venues - plan extra travel time.
- **Venetian**: North Strip, large venue with many session rooms.
- **MGM Grand**: Mid Strip, large venue, central location.
- **Caesars Forum**: Mid Strip, medium venue, connected to other venues.

### Travel Times Between Venues (walking/shuttle)
- Mandalay Bay ↔ Venetian: 25 minutes
- Mandalay Bay ↔ MGM Grand: 15 minutes
- Mandalay Bay ↔ Caesars Forum: 20 minutes
- Venetian ↔ MGM Grand: 15 minutes
- Venetian ↔ Caesars Forum: 10 minutes
- MGM Grand ↔ Caesars Forum: 10 minutes

## Best Practices

### Session Planning
- Maximum 4-5 sessions per day (avoid burnout)
- Allow 30-minute breaks between sessions
- Arrive 15 minutes early for popular sessions
- Add 20-minute buffer when traveling between venues

### Session Levels
- **100 (Foundational)**: Introductory content for beginners
- **200 (Intermediate)**: Some prior knowledge expected
- **300 (Advanced)**: Deep technical content
- **400 (Expert)**: Specialized, advanced topics

### Scheduling Guidelines
1. **Venue Distance**: Warn users if consecutive sessions are at venues >15 minutes apart
2. **Recording Priority**: Recommend attending non-recorded sessions in person (recorded sessions can be watched later)
3. **Level Balance**: Suggest a mix of session levels appropriate to user expertise
4. **Conflict Resolution**: When sessions overlap, prioritize non-recorded sessions or sessions at closer venues

Use the available MCP tools to query session data and provide helpful, context-aware recommendations."""

def create_agent(mcp_endpoint: str) -> Agent:
    """
    Create and configure the re:Invent planning agent.
    
    Args:
        mcp_endpoint: URL of the MCP server endpoint
        
    Returns:
        Configured Strands Agent instance
    """
    # Create MCP client with streamable HTTP transport
    mcp_client = MCPClient(
        lambda: streamablehttp_client(mcp_endpoint),
        prefix="reinvent"
    )
    
    # Create Bedrock model (uses Claude 4 Sonnet by default)
    model = BedrockModel(
        model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
        temperature=0.7,
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )
    
    # Create agent with MCP tools and system prompt
    # Using experimental managed MCP integration - agent handles lifecycle
    agent = Agent(
        model=model,
        tools=[mcp_client],
        system_prompt=SYSTEM_PROMPT
    )
    
    return agent
```

### 2. Agent Core Entrypoint (`src/strands-agent/entrypoint.py`)

FastAPI application for Agent Core deployment.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
import os
from agent import create_agent

app = FastAPI(title="re:Invent Planner Agent", version="1.0.0")

# Initialize agent
MCP_ENDPOINT = os.getenv(
    "MCP_ENDPOINT",
    "https://3yf7o1q3s2.execute-api.us-east-1.amazonaws.com/prod/mss-template/mcp"
)
agent = create_agent(mcp_endpoint=MCP_ENDPOINT)

class InvocationRequest(BaseModel):
    input: Dict[str, Any]

class InvocationResponse(BaseModel):
    output: Dict[str, Any]

@app.post("/invocations", response_model=InvocationResponse)
async def invoke_agent(request: InvocationRequest):
    """
    Agent Core invocation endpoint.
    
    Processes user queries and returns agent responses.
    """
    try:
        user_message = request.input.get("prompt", "")
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key."
            )
        
        # Process query through agent
        # Agent handles MCP lifecycle automatically with experimental managed integration
        result = agent(user_message)
        
        # Extract response text from agent result
        response_text = result.message['content'][0]['text']
        
        response = {
            "message": response_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": "reinvent-planner-agent"
        }
        
        return InvocationResponse(output=response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent processing failed: {str(e)}"
        )

@app.get("/ping")
async def ping():
    """Health check endpoint required by Agent Core."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### 3. Configuration Module (`src/strands-agent/config.py`)

Environment-based configuration (simplified without separate knowledge base module).



```python
import os
from typing import Optional

class Config:
    """Configuration for the re:Invent agent."""
    
    # MCP Server Configuration
    MCP_ENDPOINT: str = os.getenv(
        "MCP_ENDPOINT",
        "https://3yf7o1q3s2.execute-api.us-east-1.amazonaws.com/prod/mss-template/mcp"
    )
    
    # Agent Configuration
    AGENT_NAME: str = os.getenv("AGENT_NAME", "re:Invent Planner Agent")
    AGENT_VERSION: str = os.getenv("AGENT_VERSION", "1.0.0")
    
    # Model Configuration
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "bedrock")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    
    # Deployment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def get_model_config(cls) -> dict:
        """Get model configuration for Strands agent."""
        return {
            "provider": cls.MODEL_PROVIDER,
            "model": cls.MODEL_NAME,
            "region": cls.AWS_REGION
        }
```

## Data Models

### Session Data Model

The agent works with session data retrieved from the MCP server. The session structure is:

```python
{
    "session_id": str,           # Unique identifier
    "short_id": str,             # Human-readable ID (e.g., "TNC301")
    "title": str,                # Session title
    "venue_name": str,           # Venue location
    "day": str,                  # Day of week
    "start_time": str,           # ISO 8601 timestamp
    "end_time": str,             # ISO 8601 timestamp
    "level": str,                # "Foundational", "Intermediate", "Advanced", "Expert"
    "level_value": int,          # 100, 200, 300, or 400
    "speakers": List[str],       # Speaker names
    "topics": List[str],         # Session topics
    "description": str,          # Session description
    "is_recorded": bool,         # Recording status
    "features": List[str]        # Additional features
}
```

### Agent Request/Response Models

```python
# Request to Agent Core
{
    "input": {
        "prompt": str,           # User's natural language query
        "session_id": str        # Optional: conversation session ID
    }
}

# Response from Agent Core
{
    "output": {
        "message": str,          # Agent's response
        "timestamp": str,        # ISO 8601 timestamp
        "model": str            # Model identifier
    }
}
```

## Error Handling

### Error Categories

1. **MCP Connection Errors**
   - Retry up to 2 times with exponential backoff
   - Fall back to cached data if available
   - Return user-friendly error message

2. **Tool Invocation Errors**
   - Log error details for debugging
   - Suggest alternative search methods to user
   - Gracefully degrade functionality

3. **Validation Errors**
   - Validate user input before processing
   - Return clear error messages
   - Suggest corrections

4. **Agent Core Errors**
   - Return appropriate HTTP status codes
   - Include error details in response
   - Log for monitoring

### Error Response Format

```python
{
    "error": {
        "type": str,             # Error category
        "message": str,          # User-friendly message
        "details": str,          # Technical details (optional)
        "suggestions": List[str] # Suggested actions
    }
}
```

## Testing Strategy

### Unit Tests

1. **Agent Logic Tests**
   - Test query processing
   - Test system prompt generation
   - Test MCP client initialization

2. **Configuration Tests**
   - Test environment variable loading
   - Test configuration validation

### Integration Tests

1. **MCP Integration Tests**
   - Test MCP client connection
   - Test tool discovery
   - Test tool invocation
   - Test response parsing

2. **End-to-End Tests**
   - Test complete user workflows
   - Test multi-turn conversations
   - Test error scenarios

### Testing Approach

```python
# tests/test_agent.py
import pytest
from src.strands_agent.agent import create_agent, SYSTEM_PROMPT
from src.strands_agent.config import Config

def test_agent_creation():
    """Test agent creation with MCP client."""
    agent = create_agent(mcp_endpoint="http://localhost:8000/mcp")
    assert agent is not None
    assert agent.model is not None
    assert len(agent.tools) > 0

def test_system_prompt_content():
    """Test system prompt contains venue knowledge."""
    assert "Mandalay Bay" in SYSTEM_PROMPT
    assert "Venetian" in SYSTEM_PROMPT
    assert "25 minutes" in SYSTEM_PROMPT
    assert "Best Practices" in SYSTEM_PROMPT

@pytest.mark.integration
def test_mcp_connection():
    """Test MCP server connection and tool discovery."""
    agent = create_agent(mcp_endpoint="http://localhost:8000/mcp")
    # Agent uses experimental managed MCP integration
    # Tools are automatically discovered and available
    assert len(agent.tools) > 0
```

## Deployment Architecture

### Infrastructure Components

1. **Agent Core Runtime**
   - Serverless compute for agent execution
   - Automatic scaling
   - Session isolation
   - Built-in monitoring

2. **ECR Repository**
   - Stores agent container image
   - ARM64 architecture
   - Version tagging

3. **IAM Roles**
   - Agent execution role
   - Bedrock model access
   - CloudWatch logging

4. **CloudWatch**
   - Application logs
   - Metrics and traces
   - Alarms for errors

### CDK Stack Structure

```python
# iac/iac/strands_agent_stack.py

from aws_cdk import (
    Stack,
    RemovalPolicy,
    CustomResource,
    Duration,
    aws_iam as iam,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_ecr_assets as ecr_assets,
    custom_resources as cr,
)
from constructs import Construct
import os

class StrandsAgentStack(Stack):
    """CDK stack for Strands re:Invent agent deployment to Agent Core."""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # ECR Repository for agent image
        self.agent_repository = ecr.Repository(
            self, "ReInventAgentRepository",
            repository_name="reinvent-planner-agent",
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Build and push Docker image using CDK Docker Asset
        agent_image = ecr_assets.DockerImageAsset(
            self, "ReInventAgentImage",
            directory=os.path.join(os.path.dirname(__file__), "../../src/strands-agent"),
            platform=ecr_assets.Platform.LINUX_ARM64,
        )
        
        # IAM Role for Agent Core
        self.agent_role = iam.Role(
            self, "AgentCoreRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            description="Execution role for re:Invent planner agent"
        )
        
        # Grant Bedrock model access
        self.agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )
        
        # Grant CloudWatch logging
        self.agent_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                resources=["*"]
            )
        )
        
        # CloudWatch Log Group
        self.log_group = logs.LogGroup(
            self, "AgentLogGroup",
            log_group_name="/aws/bedrock-agentcore/reinvent-planner",
            retention=logs.RetentionDays.ONE_WEEK
        )
        
        # Lambda function for Agent Core custom resource
        agent_core_handler = self._create_agent_core_handler()
        
        # Custom Resource Provider
        provider = cr.Provider(
            self, "AgentCoreProvider",
            on_event_handler=agent_core_handler,
            log_retention=logs.RetentionDays.ONE_DAY
        )
        
        # Custom Resource to create Agent Core runtime
        self.agent_runtime = CustomResource(
            self, "AgentCoreRuntime",
            service_token=provider.service_token,
            properties={
                "AgentRuntimeName": "reinvent-planner-agent",
                "ContainerUri": agent_image.image_uri,
                "RoleArn": self.agent_role.role_arn,
                "NetworkMode": "PUBLIC"
            }
        )
        
        # Ensure agent runtime is created after image is pushed
        self.agent_runtime.node.add_dependency(agent_image)
    
    def _create_agent_core_handler(self):
        """Create Lambda function to handle Agent Core runtime creation."""
        from aws_cdk import aws_lambda as lambda_
        
        # IAM role for the Lambda function
        handler_role = iam.Role(
            self, "AgentCoreHandlerRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ]
        )
        
        # Grant permissions to manage Agent Core
        handler_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock-agentcore-control:CreateAgentRuntime",
                    "bedrock-agentcore-control:DeleteAgentRuntime",
                    "bedrock-agentcore-control:UpdateAgentRuntime",
                    "bedrock-agentcore-control:GetAgentRuntime"
                ],
                resources=["*"]
            )
        )
        
        # Grant permission to pass the agent role
        handler_role.add_to_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[self.agent_role.role_arn]
            )
        )
        
        # Lambda function
        handler = lambda_.Function(
            self, "AgentCoreHandler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.handler",
            code=lambda_.Code.from_inline("""
import boto3
import json

client = boto3.client('bedrock-agentcore-control')

def handler(event, context):
    request_type = event['RequestType']
    props = event['ResourceProperties']
    
    if request_type == 'Create':
        response = client.create_agent_runtime(
            agentRuntimeName=props['AgentRuntimeName'],
            agentRuntimeArtifact={
                'containerConfiguration': {
                    'containerUri': props['ContainerUri']
                }
            },
            networkConfiguration={'networkMode': props['NetworkMode']},
            roleArn=props['RoleArn']
        )
        return {
            'PhysicalResourceId': response['agentRuntimeArn'],
            'Data': {
                'AgentRuntimeArn': response['agentRuntimeArn'],
                'Status': response['status']
            }
        }
    
    elif request_type == 'Update':
        # Agent Core doesn't support updates, so we delete and recreate
        agent_arn = event['PhysicalResourceId']
        try:
            client.delete_agent_runtime(agentRuntimeArn=agent_arn)
        except:
            pass
        
        response = client.create_agent_runtime(
            agentRuntimeName=props['AgentRuntimeName'],
            agentRuntimeArtifact={
                'containerConfiguration': {
                    'containerUri': props['ContainerUri']
                }
            },
            networkConfiguration={'networkMode': props['NetworkMode']},
            roleArn=props['RoleArn']
        )
        return {
            'PhysicalResourceId': response['agentRuntimeArn'],
            'Data': {
                'AgentRuntimeArn': response['agentRuntimeArn'],
                'Status': response['status']
            }
        }
    
    elif request_type == 'Delete':
        agent_arn = event['PhysicalResourceId']
        try:
            client.delete_agent_runtime(agentRuntimeArn=agent_arn)
        except Exception as e:
            print(f"Error deleting agent runtime: {e}")
        return {'PhysicalResourceId': agent_arn}
"""),
            role=handler_role,
            timeout=Duration.minutes(5)
        )
        
        return handler
```

### Deployment Process

The deployment is fully automated using AWS CDK with Python. The CDK stack handles:
1. Building and pushing the Docker image to ECR
2. Creating the Agent Core runtime
3. Configuring IAM roles and permissions

**Single Command Deployment:**
```bash
cd iac
cdk deploy StrandsAgentStack
```

**CDK Stack Implementation:**

The CDK stack includes:
- ECR repository creation
- Docker image build and push (using CDK Docker assets)
- IAM role for Agent Core
- Agent Core runtime creation using Custom Resource
- CloudWatch log group configuration

**Build and Deploy Script (`iac/deploy_agent.py`):**

```python
import boto3
import subprocess
import os

def build_and_push_image(account_id: str, region: str, repository_name: str) -> str:
    """Build and push Docker image to ECR."""
    # Build image
    subprocess.run([
        "docker", "buildx", "build",
        "--platform", "linux/arm64",
        "-t", f"{repository_name}:latest",
        "../src/strands-agent"
    ], check=True)
    
    # Login to ECR
    subprocess.run([
        "aws", "ecr", "get-login-password",
        "--region", region
    ], check=True, stdout=subprocess.PIPE)
    
    # Tag and push
    image_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/{repository_name}:latest"
    subprocess.run(["docker", "tag", f"{repository_name}:latest", image_uri], check=True)
    subprocess.run(["docker", "push", image_uri], check=True)
    
    return image_uri

def create_agent_runtime(image_uri: str, role_arn: str, region: str) -> dict:
    """Create Agent Core runtime."""
    client = boto3.client('bedrock-agentcore-control', region_name=region)
    
    response = client.create_agent_runtime(
        agentRuntimeName='reinvent-planner-agent',
        agentRuntimeArtifact={
            'containerConfiguration': {
                'containerUri': image_uri
            }
        },
        networkConfiguration={'networkMode': 'PUBLIC'},
        roleArn=role_arn
    )
    
    return response
```

This script is invoked by the CDK stack during deployment.

## Security Considerations

1. **Authentication**
   - Use IAM roles for AWS service access
   - No hardcoded credentials
   - Principle of least privilege

2. **Network Security**
   - HTTPS for all communications
   - VPC endpoints for private connectivity (optional)
   - Security groups for access control

3. **Data Privacy**
   - Session isolation in Agent Core
   - No persistent storage of user data
   - Encrypted communications

4. **Secrets Management**
   - Use AWS Secrets Manager for sensitive configuration
   - Environment variables for non-sensitive config
   - Rotate credentials regularly

## Monitoring and Observability

### Metrics to Track

1. **Performance Metrics**
   - Response latency
   - Tool invocation time
   - MCP connection time

2. **Usage Metrics**
   - Number of queries
   - Tool usage frequency
   - Session duration

3. **Error Metrics**
   - Error rate by type
   - Failed tool invocations
   - MCP connection failures

### Logging Strategy

```python
import logging
import sys

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger("reinvent-agent")

# Log important events
logger.info("Agent initialized", extra={
    "mcp_endpoint": mcp_endpoint,
    "model": model_name
})

logger.error("Tool invocation failed", extra={
    "tool": tool_name,
    "error": str(error)
})
```

### CloudWatch Integration

- Enable ADOT (AWS Distro for OpenTelemetry)
- Automatic trace collection
- Metrics dashboard
- Alarm configuration

## Performance Optimization

1. **Caching Strategy**
   - Cache frequently accessed session data
   - Cache venue distance calculations
   - TTL-based cache invalidation

2. **Pagination Handling**
   - Limit automatic pagination to 5 pages
   - Stream results for large datasets
   - Inform users of truncation

3. **Connection Pooling**
   - Reuse MCP connections
   - Connection timeout configuration
   - Graceful connection recovery

## Future Enhancements

1. **Multi-Agent Architecture**
   - Specialized agents for different tasks
   - Agent-to-agent communication via A2A protocol
   - Orchestrator agent for coordination

2. **Personalization**
   - User preference storage
   - Learning from past interactions
   - Customized recommendations

3. **Advanced Features**
   - Calendar integration
   - Conflict resolution algorithms
   - Social features (group scheduling)

4. **Enhanced Knowledge**
   - Real-time venue capacity data
   - Session popularity metrics
   - Speaker ratings and reviews
