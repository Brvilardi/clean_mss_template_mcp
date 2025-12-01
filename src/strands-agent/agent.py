"""
re:Invent Planner Agent

This module provides the main agent implementation for helping users organize
their AWS re:Invent conference agenda using the Strands framework.
"""
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.memory.integrations.strands.config import AgentCoreMemoryConfig
from bedrock_agentcore.memory.integrations.strands.session_manager import AgentCoreMemorySessionManager
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands.session.file_session_manager import FileSessionManager
from mcp.client.streamable_http import streamablehttp_client
import os
from typing import Optional
from aws_lambda_powertools import Logger, Tracer
from pathlib import Path

# Initialize Powertools
logger = Logger(service="reinvent-agent", child=True)
tracer = Tracer(service="reinvent-agent")

# Load system prompt from external file
def load_system_prompt() -> str:
    """Load the system prompt from the prompts directory."""
    prompt_path = Path(__file__).parent / "prompts" / "system_prompt.md"
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"System prompt file not found at {prompt_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        raise

SYSTEM_PROMPT = load_system_prompt()


@tracer.capture_method
def create_agent(
    mcp_endpoint: str,
    memory_id: str,
    session_id: Optional[str] = None,
    actor_id: Optional[str] = None,
    aws_region: str = None
) -> Agent:
    """
    Create and configure the re:Invent planning agent.
    
    Args:
        mcp_endpoint: URL of the MCP server endpoint
        session_id: Optional session identifier for conversation persistence
        actor_id: Optional user identifier for cross-session memory
        
    Returns:
        Configured Strands Agent instance
    """
    logger.info("Creating agent", 
        mcp_endpoint=mcp_endpoint,
        has_session_id=session_id is not None,
        has_actor_id=actor_id is not None
    )
    
    # Create MCP client with streamable HTTP transport
    with tracer.provider.in_subsegment("create_mcp_client") as subsegment:
        subsegment.put_annotation("mcp_endpoint", mcp_endpoint)
        subsegment.put_metadata("endpoint_url", mcp_endpoint)
        
        mcp_client = MCPClient(
            lambda: streamablehttp_client(mcp_endpoint),
            prefix="reinvent"
        )
        logger.debug("MCP client created", mcp_endpoint=mcp_endpoint)
    
    # Create Bedrock model - use Haiku for faster responses
    # For production, consider using cross-region inference profile for better availability
    with tracer.provider.in_subsegment("create_bedrock_model") as subsegment:
        model_id = os.getenv("MODEL_NAME", "anthropic.claude-3-haiku-20240307-v1:0")
        region = os.getenv("AWS_REGION", "us-east-1")
        
        subsegment.put_annotation("model_id", model_id)
        subsegment.put_annotation("region", region)
        subsegment.put_metadata("temperature", 0.0)
        
        model = BedrockModel(
            model_id=model_id,
            temperature=0.0,  # Zero temperature to prevent hallucinations
            region_name=region
        )
        logger.debug("Bedrock model created", model_id=model_id, region=region)

    session_manager = None
    logger.info("Session context", session_id=session_id, actor_id=actor_id)
    
    if session_id or actor_id:
        with tracer.provider.in_subsegment("create_session_manager") as subsegment:
            subsegment.put_annotation("has_session_id", session_id is not None)
            subsegment.put_annotation("has_actor_id", actor_id is not None)
            subsegment.put_metadata("memory_id", memory_id)
            
            agentcore_memory_config = AgentCoreMemoryConfig(
                memory_id=memory_id,
                session_id=session_id,
                actor_id=actor_id or "default"
            )

            # Create session manager
            session_manager = AgentCoreMemorySessionManager(
                agentcore_memory_config=agentcore_memory_config,
                region_name=os.getenv("REGION")
            )
            logger.debug("Session manager created", 
                memory_id=memory_id,
                session_id=session_id,
                actor_id=actor_id
            )
    
    # Create agent with MCP tools and system prompt
    # Using experimental managed MCP integration - agent handles lifecycle
    with tracer.provider.in_subsegment("initialize_agent") as subsegment:
        subsegment.put_annotation("has_session_manager", session_manager is not None)
        subsegment.put_metadata("system_prompt_length", len(SYSTEM_PROMPT))
        
        agent = Agent(
            model=model,
            tools=[mcp_client],
            system_prompt=SYSTEM_PROMPT,
            session_manager=session_manager
        )
        logger.info("Agent initialized successfully")
    
    return agent
