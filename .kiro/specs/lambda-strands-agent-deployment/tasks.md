# Implementation Plan

## Overview
This plan migrates the Strands-based re:Invent planner agent from Bedrock Agent Core to AWS Lambda with Lambda Web Adapter, following the proven MCP server deployment pattern.

## Tasks

- [x] 1. Create Lambda handler script and refactor StrandsAgentStack
  - Create `src/strands-agent/run.sh` following MCP server pattern (executable, PYTHONPATH setup, uvicorn on port 8000)
  - Completely rewrite `iac/iac/strands_agent_stack.py` following MCPStack pattern
  - Remove all Agent Core infrastructure (CfnRuntime, ECR, Docker image asset)
  - Implement Lambda function with Python 3.14, ARM64, 512MB memory, 30s timeout, handler=`run.sh`
  - Configure Lambda Web Adapter environment variables (AWS_LAMBDA_EXEC_WRAPPER, AWS_LWA_PORT, AWS_LWA_REMOVE_BASE_PATH)
  - Attach layers in correct order: dependencies layer, then Lambda Web Adapter layer (ARM64)
  - Add Bedrock IAM permissions (InvokeModel, InvokeModelWithResponseStream)
  - Create API Gateway `/agent` resource with ANY method and LambdaIntegration
  - _Requirements: 1.1-1.5, 2.1-2.5, 3.1-3.5, 4.1-4.5, 5.1-5.5, 6.1-6.5, 7.1-7.5, 8.1-8.5_

- [x] 2. Update TemplateStack integration
  - Modify `iac/iac/template_stack.py` to pass correct parameters to StrandsAgentStack
  - Pass api_gateway_resource, environment_variables, dependencies_layer, and region
  - Remove account parameter (not needed for Lambda deployment)
  - Verify application code (entrypoint.py, agent.py, config.py) works without modifications
  - _Requirements: 9.1-9.5, 10.1-10.5_

- [x] 3. Clean up Agent Core artifacts
  - Remove or archive `src/strands-agent/Dockerfile`
  - Remove Agent Core-specific IAM policies from old code
  - Verify all ECR, Docker, and CfnRuntime resources are removed
  - _Requirements: 11.1-11.5_

- [x] 4. Deploy, test, and document
  - Deploy stack with `cdk deploy`
  - Test /ping and /invocations endpoints via API Gateway
  - Verify MCP connectivity and tool invocations
  - Verify CloudWatch Logs are working
  - Update `src/strands-agent/README.md` with Lambda deployment info, environment variables, local testing, and deployment commands
  - _Requirements: 12.1-12.5, 14.1-14.5, 15.1-15.5_

- [ ] 5. Final verification
  - Confirm cost optimization (ARM64, appropriate sizing)
  - Verify all Agent Core resources are removed from AWS
  - Test end-to-end agent functionality
  - Update any CI/CD pipelines or deployment scripts
  - _Requirements: 13.1-13.5_

## Notes

- The FastAPI application code (entrypoint.py, agent.py, config.py) requires NO changes
- Follow the exact pattern used by MCPStack for consistency
- Lambda Web Adapter automatically converts Lambda events to HTTP requests
- The agent will be accessible at: `https://{api-gateway-url}/mss-template/agent`
- Port 8000 is used internally by Lambda Web Adapter (not exposed externally)
- The handler is `run.sh` (shell script), not a Python function
- Layer order matters: dependencies layer must come before Lambda Web Adapter layer

## Testing Strategy

### Local Testing
```bash
cd src/strands-agent
python -m uvicorn entrypoint:app --host 0.0.0.0 --port 8000

# Test invocation
curl -X POST http://localhost:8000/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Find sessions about serverless"}}'

# Test health check
curl http://localhost:8000/ping
```

### Lambda Testing
```bash
# Deploy stack
cd iac
cdk deploy LambdaStack

# Test via API Gateway
curl -X POST https://{api-gateway-url}/mss-template/agent/invocations \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "Find sessions about serverless"}}'

# Test health check
curl https://{api-gateway-url}/mss-template/agent/ping
```

## Success Criteria

- [ ] Lambda function deploys successfully
- [ ] Health check endpoint returns 200 OK
- [ ] Agent invocation endpoint processes queries correctly
- [ ] MCP tools are invoked successfully
- [ ] Response format matches Agent Core deployment
- [ ] CloudWatch logs show agent activity
- [ ] No Agent Core resources remain in the stack
- [ ] Cost is reduced compared to Agent Core deployment
- [ ] Documentation is updated and accurate
