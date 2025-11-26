"""
FastAPI entrypoint for the re:Invent Planner Agent.

This module provides the FastAPI application for Lambda deployment with Lambda Web Adapter,
including request/response handling, error management, and health checks.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import os
import time
from contextlib import asynccontextmanager

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

from agent import create_agent
from config import Config

# Initialize Powertools Logger, Metrics, and Tracer
logger = Logger(service="reinvent-agent", level=Config.LOG_LEVEL)
metrics = Metrics(namespace="ReinventAgent", service="agent-invocations")
tracer = Tracer(service="reinvent-agent")

# Configuration validation error (if any)
agent_initialization_error = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Validates configuration on startup.
    """
    global agent_initialization_error
    
    # Startup: Validate configuration
    logger.info("Starting re:Invent Planner Agent",
        mcp_endpoint=Config.MCP_ENDPOINT,
        model=Config.MODEL_NAME,
        environment=Config.ENVIRONMENT
    )
    
    try:
        # Validate configuration
        if not Config.validate():
            raise ValueError("Invalid configuration. Check MCP_ENDPOINT, AWS_REGION, and MODEL_NAME.")
        
        logger.info("Configuration validated successfully")
        
    except Exception as e:
        agent_initialization_error = str(e)
        logger.error("Configuration validation failed",
            error=str(e),
            error_type=type(e).__name__
        )
        # Don't raise - allow app to start but return errors on requests
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down re:Invent Planner Agent")


# Create FastAPI app with lifespan
app = FastAPI(
    title=Config.AGENT_NAME,
    version=Config.AGENT_VERSION,
    description="AI assistant for AWS re:Invent conference planning",
    lifespan=lifespan
)

# Configure CORS middleware
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000"
]

# Add production frontend URL if configured
if Config.FRONTEND_URL:
    allowed_origins.append(Config.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InvocationRequest(BaseModel):
    """Request model for agent invocations."""
    input: Dict[str, Any] = Field(
        ...,
        description="Input data containing the user prompt"
    )
    session_id: Optional[str] = Field(
        None,
        description="Optional session ID for conversation continuity"
    )


class InvocationResponse(BaseModel):
    """Response model for agent invocations."""
    output: Dict[str, Any] = Field(
        ...,
        description="Output data containing the agent response"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: Dict[str, Any] = Field(
        ...,
        description="Error details"
    )


@tracer.capture_method
def process_agent_invocation(user_message: str, session_id: Optional[str], actor_id: str) -> Dict[str, Any]:
    """
    Process agent invocation with tracing.
    
    Args:
        user_message: User's prompt
        session_id: Optional session ID
        actor_id: User identifier
        
    Returns:
        Response dictionary with agent output
    """
    tracer.put_annotation("prompt_length", len(user_message))
    tracer.put_annotation("session_id", session_id or "none")
    tracer.put_annotation("actor_id", actor_id)
    
    # Create agent
    agent = create_agent(
        mcp_endpoint=Config.MCP_ENDPOINT,
        memory_id=Config.MEMORY_ID,
        session_id=session_id,
        actor_id=actor_id
    )
    
    # Invoke agent
    result = agent(user_message)
    
    # Extract response
    response_text = result.message['content'][0]['text']
    usage = result.message.get('usage', {})
    input_tokens = usage.get('input_tokens', 0)
    output_tokens = usage.get('output_tokens', 0)
    total_tokens = input_tokens + output_tokens
    
    # Add token annotations
    tracer.put_annotation("input_tokens", input_tokens)
    tracer.put_annotation("output_tokens", output_tokens)
    tracer.put_annotation("total_tokens", total_tokens)
    tracer.put_annotation("response_length", len(response_text))
    
    # Process tool history
    tool_calls, tool_results = process_tool_history(result)
    
    # Add tool metrics
    tracer.put_annotation("tool_calls_count", len(tool_calls))
    tracer.put_metadata("tools_used", [t['tool'] for t in tool_calls])
    
    # Log success
    logger.info("Agent invocation successful",
        response_length=len(response_text),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        tool_calls_count=len(tool_calls),
        tools_used=[t['tool'] for t in tool_calls]
    )
    
    # Add metrics
    metrics.add_metric(name="InvocationSuccess", unit=MetricUnit.Count, value=1)
    metrics.add_metric(name="InputTokens", unit=MetricUnit.Count, value=input_tokens)
    metrics.add_metric(name="OutputTokens", unit=MetricUnit.Count, value=output_tokens)
    metrics.add_metric(name="TotalTokens", unit=MetricUnit.Count, value=total_tokens)
    metrics.add_metric(name="ToolCallsCount", unit=MetricUnit.Count, value=len(tool_calls))
    
    return {
        "message": response_text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": Config.MODEL_NAME,
        "session_id": session_id,
        "actor_id": actor_id,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens
        },
        "metadata": {
            "tool_calls_count": len(tool_calls),
            "tools_used": [t['tool'] for t in tool_calls]
        }
    }


@tracer.capture_method
def process_tool_history(result) -> tuple:
    """
    Process tool calls and results from agent history with tracing.
    
    Args:
        result: Agent result with history
        
    Returns:
        Tuple of (tool_calls, tool_results)
    """
    tool_calls = []
    tool_results = []
    
    if not hasattr(result, 'history') or not result.history:
        return tool_calls, tool_results
    
    for turn in result.history:
        # Capture tool calls (from assistant)
        if turn.get('role') == 'assistant':
            content = turn.get('content', [])
            for item in content:
                if item.get('type') == 'tool_use':
                    tool_call = {
                        'id': item.get('id'),
                        'tool': item.get('name'),
                        'input': item.get('input', {})
                    }
                    tool_calls.append(tool_call)
                    
                    # Log and trace individual tool call
                    log_mcp_tool_call(item)
        
        # Capture tool results (from user role with tool_result)
        elif turn.get('role') == 'user':
            content = turn.get('content', [])
            for item in content:
                if item.get('type') == 'tool_result':
                    tool_result = {
                        'tool_use_id': item.get('tool_use_id'),
                        'content': item.get('content', [])
                    }
                    tool_results.append(tool_result)
                    
                    # Log and trace tool result
                    log_mcp_tool_result(item)
    
    return tool_calls, tool_results


@tracer.capture_method
def log_mcp_tool_call(item: Dict[str, Any]):
    """
    Log and trace MCP tool call.
    
    Args:
        item: Tool use item from agent history
    """
    tool_name = item.get('name', 'unknown')
    tool_id = item.get('id', 'unknown')
    tool_input = item.get('input', {})
    
    tracer.put_annotation("tool_name", tool_name)
    tracer.put_annotation("tool_id", tool_id)
    tracer.put_metadata("tool_input", tool_input)
    
    logger.info(f"MCP tool called: {tool_name}",
        tool_name=tool_name,
        tool_id=tool_id,
        parameters=tool_input
    )
    
    metrics.add_metric(name="ToolCalled", unit=MetricUnit.Count, value=1)
    metrics.add_dimension(name="ToolName", value=tool_name)


@tracer.capture_method
def log_mcp_tool_result(item: Dict[str, Any]):
    """
    Log and trace MCP tool result.
    
    Args:
        item: Tool result item from agent history
    """
    tool_use_id = item.get('tool_use_id', 'unknown')
    is_error = item.get('is_error', False)
    
    # Extract result summary
    result_text = ""
    if isinstance(item.get('content'), list):
        for content_item in item.get('content', []):
            if content_item.get('type') == 'text':
                result_text = content_item.get('text', '')[:500]
    
    tracer.put_annotation("tool_use_id", tool_use_id)
    tracer.put_annotation("is_error", is_error)
    tracer.put_metadata("result_preview", result_text[:200])
    
    logger.info("MCP tool result received",
        tool_use_id=tool_use_id,
        result_preview=result_text[:100] + "..." if len(result_text) > 100 else result_text,
        is_error=is_error
    )
    
    if is_error:
        metrics.add_metric(name="ToolError", unit=MetricUnit.Count, value=1)


@app.post("/invocations", response_model=InvocationResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
    503: {"model": ErrorResponse, "description": "Service Unavailable"}
})
@tracer.capture_method
async def invoke_agent(request: InvocationRequest, http_request: Request):
    """
    Agent invocation endpoint with Cognito authentication.
    
    Processes user queries and returns agent responses with error handling
    and retry logic for tool invocations.
    
    The actor_id is extracted from the Cognito JWT token via API Gateway authorizer.
    This ensures consistency with the BFF list_sessions endpoint.
    
    Args:
        request: InvocationRequest containing user prompt and session_id
        http_request: FastAPI Request object containing headers with API Gateway context
        
    Returns:
        InvocationResponse with agent's response
        
    Raises:
        HTTPException: For various error conditions
    """
    request_start_time = time.time()
    
    # Check if configuration is valid
    if agent_initialization_error:
        logger.error("Agent invocation attempted but configuration is invalid",
            initialization_error=agent_initialization_error
        )
        metrics.add_metric(name="ConfigurationInvalid", unit=MetricUnit.Count, value=1)
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "type": "ServiceUnavailable",
                    "message": "Agent configuration is invalid. Please check configuration.",
                    "details": agent_initialization_error,
                    "suggestions": [
                        "Check that the MCP server is accessible",
                        "Verify AWS credentials are configured",
                        "Check CloudWatch logs for detailed error information"
                    ]
                }
            }
        )
    
    # Extract actor_id from API Gateway authorizer context (Cognito JWT)
    # Lambda Web Adapter passes API Gateway request context via x-amzn-request-context header
    actor_id = None
    
    # Extract from x-amzn-request-context header (Lambda Web Adapter)
    request_context_header = http_request.headers.get("x-amzn-request-context")
    if request_context_header:
        try:
            import json
            request_context = json.loads(request_context_header)
            authorizer = request_context.get("authorizer", {})
            claims = authorizer.get("claims", {})
            
            # Use cognito:username for consistency with list_sessions endpoint
            actor_id = claims.get("cognito:username") or claims.get("sub")
            
            logger.info("Extracted actor_id from Cognito JWT",
                actor_id=actor_id,
                has_username=bool(claims.get("cognito:username")),
                has_sub=bool(claims.get("sub")),
                email=claims.get("email")
            )
        except Exception as e:
            logger.warning("Failed to parse request context from header",
                error=str(e),
                header_present=bool(request_context_header)
            )
    
    # If still no actor_id, return 401 Unauthorized
    if not actor_id:
        logger.error("Unable to extract actor_id from request",
            headers=dict(http_request.headers)
        )
        metrics.add_metric(name="UnauthorizedRequest", unit=MetricUnit.Count, value=1)
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "type": "Unauthorized",
                    "message": "Unable to identify user from authentication token",
                    "suggestions": [
                        "Ensure you are authenticated with a valid Cognito token",
                        "Check that the Authorization header is present",
                        "Try signing in again"
                    ]
                }
            }
        )
    
    # Extract session_id from request
    session_id = request.session_id
    
    # Log session information
    logger.info("Processing request with session context",
        session_id=session_id,
        actor_id=actor_id,
        has_session_id=request.session_id is not None
    )
    
    try:
        # Extract user message from request
        user_message = request.input.get("prompt")
        if not user_message:
            logger.warning("Invocation request missing prompt field")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "type": "MissingParameters",
                        "message": "No prompt found in input. Please provide a 'prompt' key.",
                        "suggestions": [
                            "Include a 'prompt' field in the input object",
                            "Example: {\"input\": {\"prompt\": \"Find sessions about serverless\"}}"
                        ]
                    }
                }
            )
        
        logger.info("Processing agent invocation",
            prompt_length=len(user_message),
            session_id=session_id,
            actor_id=actor_id,
            user_message_preview=user_message[:100] + "..." if len(user_message) > 100 else user_message
        )
        
        # Add metric for invocation
        metrics.add_metric(name="InvocationStarted", unit=MetricUnit.Count, value=1)
        
        # Process query through agent with retry logic
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                tracer.put_annotation("attempt", attempt + 1)
                
                # Process agent invocation (traced via decorator)
                response = process_agent_invocation(user_message, session_id, actor_id)
                
                # Add duration metric
                duration = round(time.time() - request_start_time, 2)
                metrics.add_metric(name="ResponseTime", unit=MetricUnit.Milliseconds, value=duration * 1000)
                tracer.put_annotation("duration_seconds", duration)
                
                response["metadata"]["duration_seconds"] = duration
                
                return InvocationResponse(output=response)
                
            except Exception as tool_error:
                last_error = tool_error
                error_type = type(tool_error).__name__
                
                # Check if it's a retryable error (connection, timeout, etc.)
                retryable_errors = ["ConnectionError", "TimeoutError", "HTTPError"]
                is_retryable = any(err in error_type for err in retryable_errors)
                
                if is_retryable and attempt < max_retries:
                    logger.warning(f"Tool invocation failed (attempt {attempt + 1}), retrying...",
                        error=str(tool_error),
                        error_type=error_type,
                        attempt=attempt + 1,
                        max_retries=max_retries
                    )
                    metrics.add_metric(name="InvocationRetry", unit=MetricUnit.Count, value=1)
                    time.sleep(1 * (attempt + 1))  # Progressive delay
                    continue
                else:
                    # Non-retryable error or max retries reached
                    break
        
        # If we get here, all retries failed
        logger.error("Agent invocation failed after retries",
            error=str(last_error),
            error_type=type(last_error).__name__,
            attempts=max_retries + 1,
            duration_seconds=time.time() - request_start_time,
            session_id=session_id,
            actor_id=actor_id
        )
        
        # Add failure metrics
        metrics.add_metric(name="InvocationFailure", unit=MetricUnit.Count, value=1)
        metrics.add_dimension(name="ErrorType", value=type(last_error).__name__)
        
        # Provide user-friendly error message based on error type
        error_type = type(last_error).__name__
        if "Connection" in error_type or "Timeout" in error_type:
            error_message = "Unable to connect to the session data service. Please try again."
            suggestions = [
                "Check your network connection",
                "Try again in a few moments",
                "Contact support if the issue persists"
            ]
        elif "MCP" in str(last_error):
            error_message = "Error communicating with the session data service."
            suggestions = [
                "The MCP server may be temporarily unavailable",
                "Try rephrasing your query",
                "Contact support if the issue persists"
            ]
        else:
            error_message = "An error occurred while processing your request."
            suggestions = [
                "Try rephrasing your query",
                "Simplify your request",
                "Contact support if the issue persists"
            ]
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "type": error_type,
                    "message": error_message,
                    "details": str(last_error) if not Config.is_production() else None,
                    "suggestions": suggestions
                }
            }
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error("Unexpected error during agent invocation",
            error=str(e),
            error_type=type(e).__name__,
            duration_seconds=time.time() - request_start_time,
            session_id=session_id if 'session_id' in locals() else None,
            actor_id=actor_id if 'actor_id' in locals() else None
        )
        
        metrics.add_metric(name="UnexpectedError", unit=MetricUnit.Count, value=1)
        metrics.add_dimension(name="ErrorType", value=type(e).__name__)
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred. Please try again.",
                    "details": str(e) if not Config.is_production() else None,
                    "suggestions": [
                        "Try again in a few moments",
                        "Contact support if the issue persists"
                    ]
                }
            }
        )


@app.get("/ping")
async def ping():
    """
    Health check endpoint for Lambda.
    
    Returns configuration status and basic health information.
    
    Returns:
        Dictionary with status and health information
    """
    health_status = {
        "status": "healthy" if not agent_initialization_error else "unhealthy",
        "configuration_valid": agent_initialization_error is None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": Config.AGENT_VERSION,
        "environment": Config.ENVIRONMENT
    }
    
    if agent_initialization_error:
        health_status["error"] = agent_initialization_error
        logger.warning("Health check: Configuration invalid",
            error=agent_initialization_error
        )
    
    return health_status


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Logs the error and returns a user-friendly error response.
    """
    logger.error("Unhandled exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method
    )
    
    metrics.add_metric(name="UnhandledException", unit=MetricUnit.Count, value=1)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": "InternalServerError",
                "message": "An unexpected error occurred. Please try again.",
                "details": str(exc) if not Config.is_production() else None
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting re:Invent Planner Agent server",
        host="0.0.0.0",
        port=8080,
        environment=Config.ENVIRONMENT
    )
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level=Config.LOG_LEVEL.lower()
    )
