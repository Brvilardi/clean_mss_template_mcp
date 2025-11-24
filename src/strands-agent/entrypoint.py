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
import logging
import sys
import os
import time
from contextlib import asynccontextmanager

from agent import create_agent
from config import Config

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("reinvent-agent")

# Global agent instance
agent = None
agent_initialization_error = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles agent initialization on startup and cleanup on shutdown.
    """
    global agent, agent_initialization_error
    
    # Startup: Initialize agent
    logger.info("Initializing re:Invent Planner Agent", extra={
        "mcp_endpoint": Config.MCP_ENDPOINT,
        "model": Config.MODEL_NAME,
        "environment": Config.ENVIRONMENT
    })
    
    try:
        # Validate configuration
        if not Config.validate():
            raise ValueError("Invalid configuration. Check MCP_ENDPOINT, AWS_REGION, and MODEL_NAME.")
        
        # Create agent with retry logic
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                agent = create_agent(mcp_endpoint=Config.MCP_ENDPOINT)
                logger.info("Agent initialized successfully", extra={
                    "attempt": attempt + 1,
                    "max_retries": max_retries
                })
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Agent initialization attempt {attempt + 1} failed, retrying...", extra={
                        "error": str(e),
                        "retry_delay": retry_delay
                    })
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise
        
        if agent is None:
            raise RuntimeError("Failed to initialize agent after all retry attempts")
        
    except Exception as e:
        agent_initialization_error = str(e)
        logger.error("Failed to initialize agent", extra={
            "error": str(e),
            "error_type": type(e).__name__
        })
        # Don't raise - allow app to start but return errors on requests
    
    yield
    
    # Shutdown: Cleanup
    logger.info("Shutting down re:Invent Planner Agent")
    agent = None


# Create FastAPI app with lifespan
app = FastAPI(
    title=Config.AGENT_NAME,
    version=Config.AGENT_VERSION,
    description="AI assistant for AWS re:Invent conference planning",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
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


@app.post("/invocations", response_model=InvocationResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
    503: {"model": ErrorResponse, "description": "Service Unavailable"}
})
async def invoke_agent(request: InvocationRequest):
    """
    Agent invocation endpoint.
    
    Processes user queries and returns agent responses with error handling
    and retry logic for tool invocations.
    
    Args:
        request: InvocationRequest containing user prompt
        
    Returns:
        InvocationResponse with agent's response
        
    Raises:
        HTTPException: For various error conditions
    """
    request_start_time = time.time()
    
    # Check if agent is initialized
    if agent is None:
        logger.error("Agent invocation attempted but agent not initialized", extra={
            "initialization_error": agent_initialization_error
        })
        raise HTTPException(
            status_code=503,
            detail={
                "error": {
                    "type": "ServiceUnavailable",
                    "message": "Agent is not available. Please try again later.",
                    "details": agent_initialization_error,
                    "suggestions": [
                        "Check that the MCP server is accessible",
                        "Verify AWS credentials are configured",
                        "Check CloudWatch logs for detailed error information"
                    ]
                }
            }
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
        
        logger.info("Processing agent invocation", extra={
            "prompt_length": len(user_message),
            "session_id": request.session_id
        })
        
        # Process query through agent with retry logic for tool invocations
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Agent handles MCP lifecycle automatically with experimental managed integration
                result = agent(user_message)
                
                # Extract response text from agent result
                response_text = result.message['content'][0]['text']
                
                logger.info("Agent invocation successful", extra={
                    "response_length": len(response_text),
                    "attempt": attempt + 1,
                    "duration_seconds": time.time() - request_start_time
                })
                
                response = {
                    "message": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": Config.MODEL_NAME,
                    "session_id": request.session_id
                }
                
                return InvocationResponse(output=response)
                
            except Exception as tool_error:
                last_error = tool_error
                error_type = type(tool_error).__name__
                
                # Check if it's a retryable error (connection, timeout, etc.)
                retryable_errors = ["ConnectionError", "TimeoutError", "HTTPError"]
                is_retryable = any(err in error_type for err in retryable_errors)
                
                if is_retryable and attempt < max_retries:
                    logger.warning(f"Tool invocation failed (attempt {attempt + 1}), retrying...", extra={
                        "error": str(tool_error),
                        "error_type": error_type,
                        "attempt": attempt + 1,
                        "max_retries": max_retries
                    })
                    time.sleep(1 * (attempt + 1))  # Progressive delay
                    continue
                else:
                    # Non-retryable error or max retries reached
                    break
        
        # If we get here, all retries failed
        logger.error("Agent invocation failed after retries", extra={
            "error": str(last_error),
            "error_type": type(last_error).__name__,
            "attempts": max_retries + 1,
            "duration_seconds": time.time() - request_start_time
        })
        
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
        logger.error("Unexpected error during agent invocation", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_seconds": time.time() - request_start_time
        })
        
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
    
    Returns agent status and basic health information.
    
    Returns:
        Dictionary with status and health information
    """
    health_status = {
        "status": "healthy" if agent is not None else "unhealthy",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": Config.AGENT_VERSION,
        "environment": Config.ENVIRONMENT
    }
    
    if agent is None and agent_initialization_error:
        health_status["error"] = agent_initialization_error
        logger.warning("Health check: Agent not initialized", extra={
            "error": agent_initialization_error
        })
    
    return health_status


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Logs the error and returns a user-friendly error response.
    """
    logger.error("Unhandled exception", extra={
        "error": str(exc),
        "error_type": type(exc).__name__,
        "path": request.url.path,
        "method": request.method
    })
    
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
    
    logger.info("Starting re:Invent Planner Agent server", extra={
        "host": "0.0.0.0",
        "port": 8080,
        "environment": Config.ENVIRONMENT
    })
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level=Config.LOG_LEVEL.lower()
    )
