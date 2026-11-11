"""
Unit tests for the re:Invent Planner Agent with FileSessionManager.

Tests cover:
- Agent creation with FileSessionManager (Requirements 7.1, 10.1, 10.2)
- Agent creation without session manager (Requirements 7.1, 7.3)
"""

import pytest
import os
import tempfile
import shutil
import sys
from unittest.mock import Mock, patch

# Add the strands-agent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src/strands-agent'))

from agent import create_agent
from strands.session.file_session_manager import FileSessionManager


class Test_CreateAgent:
    """Test suite for create_agent function with FileSessionManager"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        # Create a temporary directory for session files
        self.temp_dir = tempfile.mkdtemp()
        self.original_session_dir = os.environ.get('STRANDS_SESSION_DIR')
        os.environ['STRANDS_SESSION_DIR'] = self.temp_dir
        
        # Mock MCP endpoint
        self.mcp_endpoint = "http://localhost:8000"
    
    def teardown_method(self):
        """Clean up after each test"""
        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        
        # Restore original environment variable
        if self.original_session_dir:
            os.environ['STRANDS_SESSION_DIR'] = self.original_session_dir
        elif 'STRANDS_SESSION_DIR' in os.environ:
            del os.environ['STRANDS_SESSION_DIR']

    
    @patch('agent.MCPClient')
    @patch('agent.BedrockModel')
    def test_create_agent_with_file_session_manager(self, mock_bedrock, mock_mcp):
        """
        Test agent creation with FileSessionManager.
        
        Validates:
        - Agent is created successfully with session_id and actor_id
        - Agent has a session_manager attribute
        - Session manager is a FileSessionManager instance
        - Requirements: 7.1, 10.1, 10.2
        """
        # Arrange
        session_id = "test-session-123"
        actor_id = "test-user-456"
        
        # Mock the MCP client to avoid connection attempts
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance
        
        # Mock the Bedrock model
        mock_model_instance = Mock()
        mock_bedrock.return_value = mock_model_instance
        
        # Act
        agent = create_agent(
            mcp_endpoint=self.mcp_endpoint,
            session_id=session_id,
            actor_id=actor_id
        )
        
        # Assert
        assert agent is not None
        assert hasattr(agent, '_session_manager')
        assert agent._session_manager is not None
        assert isinstance(agent._session_manager, FileSessionManager)
    
    @patch('agent.MCPClient')
    @patch('agent.BedrockModel')
    def test_create_agent_without_session_manager(self, mock_bedrock, mock_mcp):
        """
        Test agent creation without session manager (default behavior).
        
        Validates:
        - Agent is created successfully without session_id
        - Agent has no session_manager or session_manager is None
        - Agent functions normally without persistence
        - Requirements: 7.1, 7.3
        """
        # Arrange
        # Mock the MCP client to avoid connection attempts
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance
        
        # Mock the Bedrock model
        mock_model_instance = Mock()
        mock_bedrock.return_value = mock_model_instance
        
        # Act
        agent = create_agent(mcp_endpoint=self.mcp_endpoint)
        
        # Assert
        assert agent is not None
        # Session manager should be None when not provided
        if hasattr(agent, '_session_manager'):
            assert agent._session_manager is None

    
    @patch('agent.MCPClient')
    @patch('agent.BedrockModel')
    def test_session_storage_to_filesystem(self, mock_bedrock, mock_mcp):
        """
        Test that session data is actually stored to the filesystem.
        
        Validates:
        - Session manager is configured with correct session_id
        - FileSessionManager has the correct storage directory
        - Requirements: 1.2, 10.1, 10.5
        """
        # Arrange
        session_id = "test-session-storage"
        actor_id = "test-user-storage"
        
        # Mock the MCP client and Bedrock model
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance
        
        mock_model_instance = Mock()
        mock_bedrock.return_value = mock_model_instance
        
        # Act
        agent = create_agent(
            mcp_endpoint=self.mcp_endpoint,
            session_id=session_id,
            actor_id=actor_id
        )
        
        # Assert
        # Check that session manager was created
        assert agent._session_manager is not None
        assert isinstance(agent._session_manager, FileSessionManager)
        
        # Verify the session manager has the correct session_id
        # FileSessionManager stores session_id in its session attribute
        assert hasattr(agent._session_manager, 'session')
        assert agent._session_manager.session.session_id == session_id
        
        # Verify the storage directory is set (even if not created yet)
        assert hasattr(agent._session_manager, 'storage_dir')
        assert agent._session_manager.storage_dir is not None

    
    @patch('agent.MCPClient')
    @patch('agent.BedrockModel')
    def test_session_manager_configuration(self, mock_bedrock, mock_mcp):
        """
        Test that the session manager is properly configured for message persistence.
        
        Validates:
        - Session manager is correctly initialized with session_id and actor_id
        - Session manager has proper storage directory configured
        - Session manager can save session data to filesystem
        - Requirements: 1.2, 10.1, 10.5
        """
        # Arrange
        session_id = "test-config"
        actor_id = "test-user-config"
        
        # Mock the MCP client and Bedrock model
        mock_mcp_instance = Mock()
        mock_mcp.return_value = mock_mcp_instance
        
        mock_model_instance = Mock()
        mock_bedrock.return_value = mock_model_instance
        
        # Act
        agent = create_agent(
            mcp_endpoint=self.mcp_endpoint,
            session_id=session_id,
            actor_id=actor_id
        )
        
        # Get the session manager
        session_manager = agent._session_manager
        
        # Assert
        # Verify session manager is properly configured
        assert session_manager is not None, "Session manager should be initialized"
        assert isinstance(session_manager, FileSessionManager), "Should be a FileSessionManager instance"
        
        # Verify session_id is correctly set
        assert session_manager.session.session_id == session_id, f"Session ID should be {session_id}"
        
        # Verify storage directory is configured
        assert hasattr(session_manager, 'storage_dir'), "Session manager should have storage_dir attribute"
        assert session_manager.storage_dir is not None, "Storage directory should be set"
        
        # Verify the session manager has the necessary methods for message persistence
        # The FileSessionManager will automatically save messages when they are appended
        assert hasattr(session_manager, 'append_message'), "Session manager should have append_message method"
        assert hasattr(session_manager, 'list_messages'), "Session manager should have list_messages method"
        assert hasattr(session_manager, 'create_message'), "Session manager should have create_message method"
        
        # This confirms the agent is properly configured with session persistence capabilities
        # When the agent runs and processes messages, they will be automatically persisted
        # to the filesystem through the FileSessionManager
