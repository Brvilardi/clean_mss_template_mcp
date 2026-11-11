# re:Invent Planner Agent

A Strands-based AI agent that helps users organize their AWS re:Invent conference agenda.

## Overview

This agent leverages the existing MCP server to access session data and provides intelligent recommendations based on re:Invent best practices, venue logistics, and session characteristics.

The agent is deployed as an AWS Lambda function using AWS Lambda Web Adapter, providing a cost-effective serverless architecture with automatic scaling.

## Features

- **Session Discovery**: Natural language queries for finding sessions by topic, venue, day, or difficulty level
- **Venue Logistics**: Built-in knowledge of venue distances and travel times
- **Recording Awareness**: Prioritizes non-recorded sessions when scheduling conflicts occur
- **Schedule Building**: Helps create personalized schedules with conflict detection
- **Best Practices**: Provides guidance on optimal session spacing and conference planning

## Project Structure

```
src/strands-agent/
├── agent.py           # Agent factory and system prompt
├── config.py          # Environment configuration
├── entrypoint.py      # FastAPI application
├── run.sh             # Lambda handler script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Dependencies

- **strands-agents**: Core agent framework
- **fastapi**: Web framework for HTTP endpoints
- **uvicorn**: ASGI server
- **boto3**: AWS SDK for Python
- **httpx**: HTTP client for MCP communication
- **aws-opentelemetry-distro**: Observability and tracing

## Configuration

The agent is configured via environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `MCP_ENDPOINT` | MCP server endpoint URL | Yes (set by CDK) |
| `AWS_REGION` | AWS region for Bedrock | Yes (default: `us-east-1`) |
| `MODEL_NAME` | Bedrock model ID | Yes (default: `anthropic.claude-3-5-sonnet-20241022-v2:0`) |
| `MODEL_TEMPERATURE` | Model temperature | `0.7` |
| `ENVIRONMENT` | Deployment environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `AWS_LAMBDA_EXEC_WRAPPER` | Lambda Web Adapter wrapper | `/opt/bootstrap` |
| `AWS_LWA_PORT` | Lambda Web Adapter port | `8000` |
| `AWS_LWA_REMOVE_BASE_PATH` | API Gateway base path to remove | `/mss-template` |

## Local Development

### Prerequisites

- Python 3.14+
- AWS credentials configured
- MCP server endpoint accessible

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (MCP_ENDPOINT is set automatically by CDK deployment)
export AWS_REGION="us-east-1"
export MODEL_NAME="anthropic.claude-3-5-sonnet-20241022-v2:0"
```

### Testing Locally

```bash
# Start the FastAPI application
python -m uvicorn entrypoint:app --host 0.0.0.0 --port 8000

# In another terminal, test health check
curl http://localhost:8000/ping

# Test agent invocation
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Show me advanced sessions about serverless computing"
    }
  }'
```

## Lambda Deployment

The agent is deployed as an AWS Lambda function using AWS Lambda Web Adapter. This provides:

- **Cost Optimization**: Pay only for actual invocations (ARM64 architecture for 20% savings)
- **Automatic Scaling**: Lambda handles scaling automatically
- **Simplified Infrastructure**: No container registry or Docker builds needed
- **Fast Deployments**: Direct code deployment without container builds

### Architecture

```
API Gateway → Lambda (with Lambda Web Adapter) → FastAPI → Strands Agent → MCP Server
```

The Lambda Web Adapter converts Lambda events to HTTP requests, allowing the FastAPI application to run unchanged.

### Deploy with CDK

```bash
cd iac
cdk deploy LambdaStack
```

This deploys:
- Lambda function with Python 3.14 runtime (ARM64)
- Lambda Web Adapter layer
- Dependencies layer
- API Gateway integration at `/mss-template/agent`
- IAM permissions for Bedrock model invocation

### Invoke Deployed Agent

```bash
# Via API Gateway (replace with your actual API Gateway URL from CDK outputs)
curl -X POST https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/mss-template/agent/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Help me find sessions about machine learning"
    }
  }'

# Health check
curl https://{api-id}.execute-api.{region}.amazonaws.com/{stage}/mss-template/agent/ping
```

## Agent Capabilities

### MCP Tools Available

The agent has access to the following MCP tools:

- `get_all_sessions_paginated`: Retrieve all sessions with pagination
- `get_session_by_short_id`: Get detailed session information by short ID
- `get_sessions_by_venue`: Find sessions at a specific venue
- `get_sessions_by_day`: Find sessions on a specific day
- `get_sessions_by_level`: Find sessions by difficulty level

### Venue Knowledge

The agent has built-in knowledge of:

- Venue locations (Mandalay Bay, Venetian, MGM Grand, Caesars Forum)
- Travel times between venues
- Venue-specific considerations

### Best Practices

The agent provides guidance on:

- Optimal session spacing (30-minute breaks recommended)
- Maximum sessions per day (4-5 recommended)
- Session level balance
- Recording status prioritization
- Venue logistics

## Observability

The agent includes OpenTelemetry auto-instrumentation for observability:

- Distributed tracing with AWS X-Ray
- Metrics in CloudWatch
- Structured logging

To view metrics:

1. Enable CloudWatch Transaction Search in the AWS Console
2. Navigate to CloudWatch > GenAI Observability
3. Find your agent service and view traces/metrics

## Architecture

```
User → API Gateway → Lambda (Lambda Web Adapter) → FastAPI → Strands Agent → MCP Client → API Gateway → MCP Server Lambda → re:Invent Planner API → DynamoDB
```

### Key Components

1. **Lambda Function**: Runs the FastAPI application with Python 3.14 (ARM64)
2. **Lambda Web Adapter**: Converts Lambda events to HTTP requests
3. **FastAPI Application**: Provides `/invocations` and `/ping` endpoints
4. **Strands Agent**: Processes queries using Bedrock models
5. **MCP Client**: Communicates with MCP server via HTTPS
6. **API Gateway**: Provides HTTP endpoints for both agent and MCP server

## Lambda Configuration

- **Runtime**: Python 3.14
- **Architecture**: ARM64 (20% cost savings)
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Handler**: `run.sh` (shell script that starts uvicorn)
- **Layers**: Dependencies layer + Lambda Web Adapter layer

## References

- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [AWS Lambda Web Adapter](https://github.com/awslabs/aws-lambda-web-adapter)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Lambda Deployment Spec](.kiro/specs/lambda-strands-agent-deployment/requirements.md)
- [Lambda Deployment Design](.kiro/specs/lambda-strands-agent-deployment/design.md)

## License

See main project LICENSE file.
