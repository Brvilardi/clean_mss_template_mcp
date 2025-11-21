# re:Invent Planner Agent

A Strands-based AI agent that helps users organize their AWS re:Invent conference agenda.

## Overview

This agent leverages the existing MCP server to access session data and provides intelligent recommendations based on re:Invent best practices, venue logistics, and session characteristics.

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
├── entrypoint.py      # FastAPI application for Agent Core
├── Dockerfile         # ARM64 container configuration
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Dependencies

- **strands-agents**: Core agent framework
- **fastapi**: Web framework for Agent Core endpoints
- **uvicorn**: ASGI server
- **boto3**: AWS SDK for Python
- **httpx**: HTTP client for MCP communication
- **aws-opentelemetry-distro**: Observability and tracing

## Configuration

The agent is configured via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_ENDPOINT` | MCP server endpoint URL | `https://3yf7o1q3s2.execute-api.us-east-1.amazonaws.com/prod/mss-template/mcp` |
| `AWS_REGION` | AWS region for Bedrock | `us-east-1` |
| `MODEL_NAME` | Bedrock model ID | `anthropic.claude-3-5-sonnet-20241022-v2:0` |
| `MODEL_TEMPERATURE` | Model temperature | `0.7` |
| `ENVIRONMENT` | Deployment environment | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Local Development

### Prerequisites

- Python 3.11+
- Docker (for containerized testing)
- AWS credentials configured

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally (once implemented)
python entrypoint.py
```

### Testing Locally

```bash
# Test health check
curl http://localhost:8080/ping

# Test agent invocation
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "prompt": "Show me advanced sessions about serverless computing"
    }
  }'
```

## Docker Deployment

### Build Image

```bash
# Build for ARM64 (required by Agent Core)
docker buildx build --platform linux/arm64 -t reinvent-planner-agent:latest .

# Test locally
docker run --platform linux/arm64 -p 8080:8080 \
  -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  -e AWS_SESSION_TOKEN="$AWS_SESSION_TOKEN" \
  -e AWS_REGION="$AWS_REGION" \
  reinvent-planner-agent:latest
```

### Push to ECR

```bash
# Authenticate with ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag reinvent-planner-agent:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/reinvent-planner-agent:latest

docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/reinvent-planner-agent:latest
```

## Deployment to AWS Bedrock Agent Core

The agent is deployed using AWS CDK. See the infrastructure code in `iac/iac/strands_agent_stack.py`.

### Deploy with CDK

```bash
cd iac
cdk deploy StrandsAgentStack
```

### Invoke Deployed Agent

```python
import boto3
import json

client = boto3.client('bedrock-agentcore', region_name='us-east-1')

payload = json.dumps({
    "input": {
        "prompt": "Help me find sessions about machine learning"
    }
})

response = client.invoke_agent_runtime(
    agentRuntimeArn='arn:aws:bedrock-agentcore:us-east-1:<account-id>:runtime/<runtime-id>',
    runtimeSessionId='unique-session-id-at-least-33-chars-long',
    payload=payload
)

response_body = response['response'].read()
print(json.loads(response_body))
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
User → Agent Core → FastAPI App → Strands Agent → MCP Client → MCP Server → Lambda Functions → DynamoDB
```

## Implementation Status

- [x] Task 1: Project structure and dependencies
- [ ] Task 2: Agent core module
- [ ] Task 3: FastAPI entrypoint
- [ ] Task 4: Docker configuration
- [ ] Task 5: Session discovery features
- [ ] Task 6: CDK infrastructure
- [ ] Task 7: Documentation
- [ ] Task 8: Unit tests
- [ ] Task 9: Integration tests
- [ ] Task 10: Deployment

## References

- [Strands Agents Documentation](https://strandsagents.com/latest/)
- [AWS Bedrock Agent Core Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Project Requirements](.kiro/specs/strands-reinvent-agent/requirements.md)
- [Project Design](.kiro/specs/strands-reinvent-agent/design.md)

## License

See main project LICENSE file.
