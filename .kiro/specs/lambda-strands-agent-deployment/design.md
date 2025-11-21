# Design Document

## Overview

This document describes the design for redeploying the Strands-based re:Invent planner agent using AWS Lambda with AWS Lambda Web Adapter. This migration replaces the Bedrock Agent Core deployment with a simpler, more cost-effective serverless architecture that aligns with the existing MCP server deployment pattern.

### Key Design Goals

1. **Simplified Deployment**: Use Lambda instead of Agent Core for easier management
2. **Cost Optimization**: Leverage Lambda's pay-per-use pricing and ARM64 architecture
3. **Pattern Consistency**: Follow the same deployment pattern as the MCP server
4. **Zero Code Changes**: Reuse existing FastAPI application without modifications
5. **Seamless Migration**: Maintain all agent functionality during the transition

### Benefits of Lambda Deployment

- **Lower Cost**: Pay only for actual invocations, no runtime costs when idle
- **Simpler Infrastructure**: No ECR, Docker builds, or custom resources needed
- **Faster Deployments**: Direct code deployment without container builds
- **Better Integration**: Native API Gateway integration
- **Proven Pattern**: Reuses the successful MCP server deployment approach

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│                 │
│  User/Client    │
│                 │
└────────┬────────┘
         │
         │ HTTPS
         │
         ▼
┌─────────────────────────────────────┐
│                                     │
│  API Gateway                        │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  /mss-template/agent        │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │  /mss-template/mcp          │   │
│  └─────────────────────────────┘   │
│                                     │
└──────┬──────────────────────┬───────┘
       │                      │
       │ Lambda Integration   │ Lambda Integration
       │                      │
       ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│                  │   │                  │
│  Lambda Function │   │  Lambda Function │
│  (Strands Agent) │   │  (MCP Server)    │
│                  │   │                  │
│  ┌────────────┐ │   │  ┌────────────┐ │
│  │ Lambda Web │ │   │  │ Lambda Web │ │
│  │ Adapter    │ │   │  │ Adapter    │ │
│  └────────────┘ │   │  └────────────┘ │
│                  │   │                  │
│  ┌────────────┐ │   │  ┌────────────┐ │
│  │  FastAPI   │ │   │  │  FastMCP   │ │
│  │  /invoke   │ │   │  │  Tools     │ │
│  │  /ping     │ │   │  │            │ │
│  └────────────┘ │   │  └────────────┘ │
│                  │   │                  │
│  ┌────────────┐ │   └──────────────────┘
│  │  Strands   │ │            │
│  │  Agent     │ │            │
│  │  ─────     │ │            │
│  │  Bedrock   │ │            │
│  │  MCP Client├─┼────────────┘
│  └────────────┘ │   HTTPS to API Gateway
│                  │   /mss-template/mcp
└──────────────────┘
         │
         │ Calls other Lambda functions
         │ via API Gateway
         ▼
┌─────────────────────────────────────┐
│                                     │
│  re:Invent Planner API (Lambda)     │
│  + DynamoDB                         │
│                                     │
└─────────────────────────────────────┘
```

### Request Flow

1. **Client Request**: User sends POST request to `/mss-template/agent/invocations`
2. **API Gateway**: Routes request to Strands Agent Lambda function
3. **Lambda Web Adapter**: Intercepts Lambda event, converts to HTTP request
4. **FastAPI**: Receives HTTP request on port 8000, routes to `/invocations` endpoint
5. **Agent Processing**: Strands agent processes query, determines it needs session data
6. **MCP Tool Invocation**: Agent's MCP client makes HTTPS request to API Gateway at `/mss-template/mcp`
7. **API Gateway → MCP Lambda**: API Gateway routes MCP request to MCP Server Lambda
8. **MCP Server Processing**: MCP server invokes appropriate tool, calls re:Invent Planner API Lambda
9. **Session Data Retrieval**: Planner API Lambda queries DynamoDB, returns session data
10. **MCP Response**: MCP server returns tool result through API Gateway to Strands Agent
11. **Agent Response**: Agent formats response with session data, returns through FastAPI → Lambda Web Adapter → API Gateway → Client

### Component Comparison: Agent Core vs Lambda

| Aspect | Agent Core (Old) | Lambda (New) |
|--------|------------------|--------------|
| Deployment | Docker container in ECR | Direct code deployment |
| Infrastructure | Custom Resource + ECR + Agent Core | Lambda + API Gateway |
| Cold Start | ~5-10 seconds | ~2-3 seconds |
| Cost Model | Runtime-based | Invocation-based |
| Scaling | Agent Core managed | Lambda auto-scaling |
| Complexity | High (Docker, ECR, Custom Resource) | Low (standard Lambda) |
| Maintenance | Container updates required | Code updates only |

## Components and Interfaces

### 1. Handler Script (`src/strands-agent/run.sh`)

Simple shell script that starts the FastAPI application for Lambda Web Adapter.

```bash
#!/bin/bash

# Start FastAPI application with uvicorn
# Lambda Web Adapter will route requests to this server
exec python -m uvicorn entrypoint:app --host 0.0.0.0 --port 8000
```

**Key Points:**
- Must be executable (`chmod +x run.sh`)
- Uses `exec` to replace shell process with uvicorn
- Binds to 0.0.0.0:8000 (Lambda Web Adapter expects port 8000)
- Follows same pattern as MCP server's `run.sh`

### 2. FastAPI Application (`src/strands-agent/entrypoint.py`)

**No changes required** - the existing FastAPI application works as-is with Lambda Web Adapter.

The application includes:
- `/invocations` POST endpoint for agent queries
- `/ping` GET endpoint for health checks
- Agent initialization on startup
- Error handling and logging

**Lambda Web Adapter Integration:**
- Lambda Web Adapter converts Lambda events to HTTP requests
- FastAPI receives standard HTTP requests (no Lambda-specific code needed)
- Responses are automatically converted back to Lambda format

### 3. Agent Module (`src/strands-agent/agent.py`)

**No changes required** - the existing agent implementation works as-is.

The module includes:
- `create_agent()` factory function
- BedrockModel configuration
- MCP client setup with streamable HTTP transport
- System prompt with venue knowledge and best practices

### 4. Configuration Module (`src/strands-agent/config.py`)

**No changes required** - the existing configuration works as-is.

Environment variables are passed through Lambda configuration:
- `MCP_ENDPOINT`: URL of the MCP server
- `AWS_REGION`: AWS region for Bedrock
- `MODEL_NAME`: Bedrock model identifier
- `LOG_LEVEL`: Logging level
- `STAGE`: Deployment stage

### 5. CDK Stack (`iac/iac/strands_agent_stack.py`)

New implementation following the `MCPStack` pattern.

```python
import os
from aws_cdk import (
    aws_lambda as lambda_,
    Duration
)
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from constructs import Construct
from aws_cdk.aws_apigateway import Resource, LambdaIntegration


class StrandsAgentStack(Construct):
    """CDK stack for Strands re:Invent agent deployed as Lambda function."""
    
    # AWS Lambda Web Adapter Layer ARN (ARM64)
    LAMBDA_WEB_ADAPTER_LAYER_ARN = lambda region: (
        f"arn:aws:lambda:{region}:753240598075:layer:LambdaAdapterLayerArm64:25"
    )
    
    def create_lambda_api_gateway_integration(
        self,
        method: str,
        api_gateway_resource: Resource,
        environment_variables: dict,
        memory_size: int = 512,
        timeout_seconds: int = 30,
        layers: list = None
    ):
        """
        Create Lambda function with API Gateway integration.
        
        Args:
            method: HTTP method (e.g., "ANY")
            api_gateway_resource: API Gateway resource to attach to
            environment_variables: Environment variables for Lambda
            memory_size: Lambda memory in MB
            timeout_seconds: Lambda timeout in seconds
            layers: Lambda layers to attach
            
        Returns:
            Lambda function
        """
        function = lambda_.Function(
            self, "StrandsAgentFunction",
            code=lambda_.Code.from_asset("../src/strands-agent"),
            handler="run.sh",
            runtime=lambda_.Runtime.PYTHON_3_14,
            architecture=lambda_.Architecture.ARM_64,
            layers=layers,
            environment=environment_variables,
            memory_size=memory_size,
            timeout=Duration.seconds(timeout_seconds)
        )
        
        # Create API Gateway resource and method
        api_gateway_resource.add_resource("agent").add_method(
            method,
            integration=LambdaIntegration(function)
        )
        
        return function
    
    def __init__(
        self,
        scope: Construct,
        api_gateway_resource: Resource,
        environment_variables: dict,
        dependencies_layer,
        region: str
    ) -> None:
        super().__init__(scope, "StrandsAgent")
        
        # Get Lambda Web Adapter layer
        self.lambda_web_adapter_layer = PythonLayerVersion.from_layer_version_arn(
            self, "LambdaWebAdapterLayer",
            StrandsAgentStack.LAMBDA_WEB_ADAPTER_LAYER_ARN(region)
        )
        
        # Combine layers
        self.layers = [dependencies_layer, self.lambda_web_adapter_layer]
        
        # Configure environment variables for Lambda Web Adapter
        envs = environment_variables.copy()
        envs['AWS_LAMBDA_EXEC_WRAPPER'] = "/opt/bootstrap"  # Lambda Web Adapter bootstrap
        envs['AWS_LWA_PORT'] = "8000"  # Port for FastAPI
        envs['AWS_LWA_REMOVE_BASE_PATH'] = "/mss-template"  # Remove API Gateway base path
        
        # Add MCP endpoint (API Gateway URL, not direct Lambda)
        # The agent calls the MCP server through API Gateway
        envs['MCP_ENDPOINT'] = (
            "https://3yf7o1q3s2.execute-api.us-east-1.amazonaws.com"
            "/prod/mss-template/mcp"
        )
        
        # Create Lambda function with API Gateway integration
        self.agent_function = self.create_lambda_api_gateway_integration(
            method="ANY",
            api_gateway_resource=api_gateway_resource,
            environment_variables=envs,
            memory_size=512,
            timeout_seconds=30,
            layers=self.layers
        )
        
        # Grant Bedrock permissions
        from aws_cdk import aws_iam as iam
        self.agent_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                resources=["*"]
            )
        )
```

**Key Design Decisions:**

1. **Layer Order**: Dependencies layer first, then Lambda Web Adapter layer
2. **Handler**: Uses `run.sh` script (not a Python function)
3. **Runtime**: Python 3.14 for latest features and performance
4. **Architecture**: ARM64 for 20% cost savings
5. **Memory**: 512 MB (sufficient for agent + model invocations)
6. **Timeout**: 30 seconds (allows for MCP calls and model invocations)

### 6. Main CDK App Integration (`iac/app.py`)

Update to instantiate the new StrandsAgentStack:

```python
from iac.strands_agent_stack import StrandsAgentStack

# ... existing code ...

# Create Strands Agent stack
strands_agent_stack = StrandsAgentStack(
    self,
    api_gateway_resource=api_gateway_resource,
    environment_variables=environment_variables,
    dependencies_layer=dependencies_layer,
    region=region
)
```

## Data Models

### Lambda Event Format

Lambda Web Adapter automatically converts Lambda events to HTTP requests, so the FastAPI application receives standard HTTP requests:

```python
# FastAPI receives standard HTTP request
POST /invocations
Content-Type: application/json

{
    "input": {
        "prompt": "Find sessions about serverless"
    }
}
```

### Response Format

FastAPI returns standard HTTP response, Lambda Web Adapter converts to Lambda format:

```python
# FastAPI returns standard HTTP response
HTTP/1.1 200 OK
Content-Type: application/json

{
    "output": {
        "message": "Here are some serverless sessions...",
        "timestamp": "2024-11-21T10:00:00Z",
        "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
    }
}
```

## Error Handling

### Error Flow

1. **FastAPI Error Handling**: Existing error handling in `entrypoint.py` catches exceptions
2. **HTTP Status Codes**: FastAPI returns appropriate status codes (400, 500, 503)
3. **Lambda Web Adapter**: Converts HTTP responses to Lambda format
4. **API Gateway**: Returns HTTP response to client

### Error Response Format

```python
{
    "error": {
        "type": "ServiceUnavailable",
        "message": "Agent is not available. Please try again later.",
        "details": "MCP server connection failed",
        "suggestions": [
            "Check that the MCP server is accessible",
            "Verify AWS credentials are configured"
        ]
    }
}
```

## Testing Strategy

### Unit Tests

**No new tests required** - existing tests for agent logic remain valid.

### Integration Tests

1. **Lambda Invocation Test**
   - Invoke Lambda function directly
   - Verify FastAPI application starts correctly
   - Verify endpoints are accessible

2. **API Gateway Test**
   - Send HTTP request through API Gateway
   - Verify request routing
   - Verify response format

3. **MCP Integration Test**
   - Verify agent can connect to MCP server
   - Verify tool invocations work
   - Verify session data retrieval

### Local Testing

```bash
# Test FastAPI application locally
cd src/strands-agent
python -m uvicorn entrypoint:app --host 0.0.0.0 --port 8000

# Test with curl
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Find sessions about serverless"}}'

# Test health check
curl http://localhost:8000/ping
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Lambda Web Adapter Configuration Completeness
*For any* Lambda function deployment, all three required Lambda Web Adapter environment variables (`AWS_LAMBDA_EXEC_WRAPPER`, `AWS_LWA_PORT`, `AWS_LWA_REMOVE_BASE_PATH`) must be set with correct values.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 2: Handler Script Executability
*For any* deployment, the `run.sh` handler script must be executable and successfully start the FastAPI application on port 8000.
**Validates: Requirements 2.2, 2.3, 2.4**

### Property 3: API Gateway Integration Consistency
*For any* API Gateway resource, the Lambda integration must support the ANY method and correctly route requests to the Lambda function.
**Validates: Requirements 4.2, 4.3, 4.4**

### Property 4: Layer Attachment Order
*For any* Lambda function configuration, the dependencies layer must be attached before the Lambda Web Adapter layer.
**Validates: Requirements 5.2, 5.3**

### Property 5: IAM Permission Sufficiency
*For any* agent invocation requiring Bedrock model access, the Lambda function's IAM role must include permissions for `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream`.
**Validates: Requirements 7.1, 7.2**

### Property 6: Endpoint Preservation
*For any* HTTP request to `/invocations` or `/ping`, the Lambda-based deployment must return responses with the same structure as the Agent Core deployment.
**Validates: Requirements 10.4, 10.5**

### Property 7: MCP Connectivity via API Gateway
*For any* agent invocation requiring session data, the agent must successfully connect to the MCP server through API Gateway using the endpoint specified in the `MCP_ENDPOINT` environment variable.
**Validates: Requirements 3.4, 12.3, 12.4**

### Property 8: Resource Allocation Adequacy
*For any* agent invocation, the Lambda function must have sufficient memory (≥512 MB) and timeout (≥30 seconds) to complete processing without resource exhaustion.
**Validates: Requirements 8.1, 8.2**

### Property 9: Architecture Consistency
*For any* Lambda function deployment, the architecture must be ARM64 and match the architecture of all attached layers.
**Validates: Requirements 1.2, 5.5, 8.5**

### Property 10: Environment Variable Propagation
*For any* configuration value (MCP_ENDPOINT, AWS_REGION, LOG_LEVEL, STAGE), the value set in CDK must be accessible to the FastAPI application at runtime.
**Validates: Requirements 3.4, 3.5**

## Deployment Architecture

### Infrastructure Components

1. **Lambda Function**
   - Runtime: Python 3.14
   - Architecture: ARM64
   - Memory: 512 MB
   - Timeout: 30 seconds
   - Handler: `run.sh`

2. **Lambda Layers**
   - Dependencies layer (shared with other functions)
   - AWS Lambda Web Adapter layer (official AWS layer)

3. **API Gateway**
   - Resource: `/agent`
   - Method: ANY
   - Integration: Lambda proxy integration

4. **IAM Role**
   - Bedrock model invocation permissions
   - CloudWatch Logs permissions
   - Basic Lambda execution permissions

### Deployment Process

1. **CDK Synthesis**: `cdk synth` generates CloudFormation template
2. **Asset Packaging**: CDK packages `src/strands-agent/` directory
3. **Stack Deployment**: `cdk deploy` creates/updates resources
4. **Lambda Update**: Code is deployed to Lambda function
5. **API Gateway Update**: Routes are configured

**Single Command Deployment:**
```bash
cd iac
cdk deploy LambdaStack  # Deploys all Lambda functions including agent
```

### Migration Steps

1. **Deploy New Lambda Stack**: Deploy Lambda-based agent alongside Agent Core
2. **Test Lambda Deployment**: Verify functionality through API Gateway
3. **Update Client Endpoints**: Switch clients to new Lambda endpoint
4. **Remove Agent Core**: Delete Agent Core stack after verification
5. **Clean Up**: Remove Docker files and ECR repository

## Security Considerations

### IAM Permissions

```python
# Lambda execution role permissions
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

### Network Security

- **HTTPS Only**: All communications use HTTPS
- **API Gateway**: Provides DDoS protection and throttling
- **Lambda Isolation**: Each invocation runs in isolated environment
- **No VPC Required**: Public endpoints with IAM authentication

### Secrets Management

- **Environment Variables**: Non-sensitive configuration
- **IAM Roles**: No hardcoded credentials
- **Bedrock Access**: IAM role-based authentication

## Monitoring and Observability

### CloudWatch Logs

Lambda automatically creates log groups:
- Log Group: `/aws/lambda/StrandsAgentFunction`
- Retention: Configurable (default: never expire)
- Structure: Includes Lambda request ID, duration, memory usage

### Metrics

Lambda provides built-in metrics:
- **Invocations**: Number of function invocations
- **Duration**: Execution time per invocation
- **Errors**: Number of failed invocations
- **Throttles**: Number of throttled requests
- **ConcurrentExecutions**: Number of concurrent invocations

### Custom Metrics

Agent logs include:
- Agent initialization events
- MCP tool invocations
- Model invocation latency
- Error details with context

### Alarms

Recommended CloudWatch alarms:
- Error rate > 5%
- Duration > 25 seconds (approaching timeout)
- Throttles > 0
- Concurrent executions > 80% of limit

## Performance Optimization

### Cold Start Optimization

1. **ARM64 Architecture**: Faster cold starts than x86
2. **Minimal Dependencies**: Only essential packages in layer
3. **Code Size**: Keep function code small
4. **Provisioned Concurrency**: Optional for consistent performance

### Memory Optimization

- **512 MB**: Sufficient for agent + model invocations
- **Monitor**: Use CloudWatch metrics to adjust if needed
- **Cost vs Performance**: Higher memory = faster CPU = potentially lower cost

### Timeout Configuration

- **30 seconds**: Allows for MCP calls + model invocations
- **Retry Logic**: Agent retries failed MCP calls
- **Graceful Degradation**: Returns partial results if timeout approaches

## Cost Analysis

### Lambda Costs (ARM64)

- **Compute**: $0.0000133334 per GB-second
- **Requests**: $0.20 per 1M requests
- **Example**: 10,000 invocations/month at 512 MB, 5 seconds average
  - Compute: 10,000 × 0.5 GB × 5 sec × $0.0000133334 = $0.33
  - Requests: 10,000 × $0.20 / 1M = $0.002
  - **Total**: ~$0.33/month

### Agent Core Costs (Comparison)

- **Runtime**: ~$0.10/hour when active
- **Example**: 10 hours/month active = $1.00/month
- **Savings**: ~70% cost reduction with Lambda

### Additional Costs

- **API Gateway**: $3.50 per million requests
- **CloudWatch Logs**: $0.50 per GB ingested
- **Bedrock**: Pay per model invocation (same for both deployments)

## Future Enhancements

1. **Provisioned Concurrency**: For consistent low-latency responses
2. **Lambda SnapStart**: Faster cold starts (when available for Python)
3. **Multi-Region Deployment**: Deploy to multiple regions for lower latency
4. **Caching Layer**: Cache frequent queries to reduce Bedrock costs
5. **Async Processing**: Use SQS for long-running queries

## Migration Checklist

- [ ] Create `run.sh` handler script
- [ ] Update CDK stack to use Lambda pattern
- [ ] Deploy Lambda-based agent
- [ ] Test all endpoints
- [ ] Verify MCP integration
- [ ] Update documentation
- [ ] Remove Agent Core infrastructure
- [ ] Delete Docker files
- [ ] Update deployment scripts
- [ ] Monitor costs and performance
