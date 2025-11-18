#!/usr/bin/env python3
"""
Simple test script to verify MCP server can list tools
"""
import subprocess
import json
import sys

def test_mcp_server():
    """Test that the MCP server can respond to a tools/list request"""
    
    # Start the MCP server
    process = subprocess.Popen(
        [sys.executable, "src/mcp/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Step 1: Initialize the connection
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize request...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Read initialize response
        init_response_line = process.stdout.readline()
        if init_response_line:
            init_response = json.loads(init_response_line)
            print("Initialize response:")
            print(json.dumps(init_response, indent=2))
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print("\nSending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Step 3: Request tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nSending tools/list request...")
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Read tools response
        tools_response_line = process.stdout.readline()
        
        if tools_response_line:
            tools_response = json.loads(tools_response_line)
            print("\nTools response:")
            print(json.dumps(tools_response, indent=2))
            
            if "result" in tools_response:
                tools = tools_response["result"].get("tools", [])
                print(f"\n✓ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"  - {tool.get('name')}: {tool.get('description', '')[:60]}...")
            elif "error" in tools_response:
                print(f"\n✗ Error: {tools_response['error']}")
        else:
            print("No response received")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        process.terminate()
        stderr = process.stderr.read()
        if stderr:
            print("\n--- Server stderr output ---")
            print(stderr)

if __name__ == "__main__":
    test_mcp_server()
