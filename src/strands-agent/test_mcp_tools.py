"""
Test script to verify MCP tools are accessible through the Strands agent.

This script tests the integration between the Strands agent and the MCP server
by invoking each tool and verifying the responses.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import create_agent
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_mcp_tools")


class MCPToolTester:
    """Test harness for verifying MCP tool accessibility."""
    
    def __init__(self):
        """Initialize the tester with an agent instance."""
        logger.info("Initializing MCP Tool Tester")
        logger.info(f"MCP Endpoint: {Config.MCP_ENDPOINT}")
        logger.info(f"Model: {Config.MODEL_NAME}")
        
        try:
            self.agent = create_agent(mcp_endpoint=Config.MCP_ENDPOINT)
            logger.info("Agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise
    
    def test_tool(self, tool_name: str, query: str) -> Dict[str, Any]:
        """
        Test a specific MCP tool by sending a query to the agent.
        
        Args:
            tool_name: Name of the tool being tested
            query: Natural language query that should trigger the tool
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {tool_name}")
        logger.info(f"Query: {query}")
        logger.info(f"{'='*60}")
        
        try:
            # Send query to agent
            result = self.agent(query)
            
            # Extract response
            response_text = result.message['content'][0]['text']
            
            # Check if tool was used (look for tool use in the result)
            tool_used = False
            if hasattr(result, 'tool_calls') and result.tool_calls:
                tool_used = True
            
            logger.info(f"✓ Tool invoked successfully")
            logger.info(f"Response length: {len(response_text)} characters")
            logger.info(f"Response preview: {response_text[:200]}...")
            
            return {
                "success": True,
                "tool_name": tool_name,
                "response": response_text,
                "tool_used": tool_used
            }
            
        except Exception as e:
            logger.error(f"✗ Tool invocation failed: {e}")
            return {
                "success": False,
                "tool_name": tool_name,
                "error": str(e)
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """
        Run tests for all MCP tools.
        
        Returns:
            Dictionary with overall test results
        """
        logger.info("\n" + "="*60)
        logger.info("Starting MCP Tool Accessibility Tests")
        logger.info("="*60 + "\n")
        
        tests = [
            {
                "tool": "get_all_sessions_paginated",
                "query": "Show me the first 5 sessions available at re:Invent"
            },
            {
                "tool": "get_session_by_short_id",
                "query": "Tell me about session TNC301"
            },
            {
                "tool": "get_sessions_by_venue",
                "query": "What sessions are at Mandalay Bay?"
            },
            {
                "tool": "get_sessions_by_day",
                "query": "What sessions are on Monday?"
            },
            {
                "tool": "get_sessions_by_level",
                "query": "Show me all 300-level sessions"
            }
        ]
        
        results = []
        for test in tests:
            result = self.test_tool(test["tool"], test["query"])
            results.append(result)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("Test Summary")
        logger.info("="*60)
        
        passed = sum(1 for r in results if r["success"])
        failed = len(results) - passed
        
        logger.info(f"Total tests: {len(results)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        
        for result in results:
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            logger.info(f"{status}: {result['tool_name']}")
            if not result["success"]:
                logger.info(f"  Error: {result.get('error', 'Unknown error')}")
        
        logger.info("="*60 + "\n")
        
        return {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "results": results
        }


def main():
    """Main entry point for the test script."""
    try:
        # Validate configuration
        if not Config.validate():
            logger.error("Invalid configuration. Check environment variables.")
            logger.error(f"MCP_ENDPOINT: {Config.MCP_ENDPOINT}")
            logger.error(f"AWS_REGION: {Config.AWS_REGION}")
            logger.error(f"MODEL_NAME: {Config.MODEL_NAME}")
            sys.exit(1)
        
        # Create tester and run tests
        tester = MCPToolTester()
        results = tester.run_all_tests()
        
        # Exit with appropriate code
        if results["failed"] > 0:
            logger.error(f"\n{results['failed']} test(s) failed")
            sys.exit(1)
        else:
            logger.info(f"\nAll {results['passed']} tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\nTest execution failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
