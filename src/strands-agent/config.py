"""
Configuration module for the re:Invent Planner Agent.

This module provides environment-based configuration for the Strands agent,
including MCP server endpoints, model settings, and deployment configuration.
"""

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
    MODEL_NAME: str = os.getenv("MODEL_NAME", "us.anthropic.claude-3-5-sonnet-20241022-v2:0")
    
    # Deployment Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def is_production(cls) -> bool:
        """
        Check if running in production environment.
        
        Returns:
            True if ENVIRONMENT is 'production', False otherwise
        """
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def get_model_config(cls) -> dict:
        """
        Get model configuration for Strands agent.
        
        Returns:
            Dictionary containing model provider, model name, and region
        """
        return {
            "provider": cls.MODEL_PROVIDER,
            "model": cls.MODEL_NAME,
            "region": cls.AWS_REGION
        }
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Check required fields
        if not cls.MCP_ENDPOINT:
            return False
        
        if not cls.AWS_REGION:
            return False
        
        if not cls.MODEL_NAME:
            return False
        
        # Validate MCP endpoint format
        if not cls.MCP_ENDPOINT.startswith(("http://", "https://")):
            return False
        
        return True
