#!/usr/bin/env python3
"""
Proper MCP test that handles the initialization sequence.
"""

import json
import subprocess
import sys
import asyncio
import time

async def test_mcp_server_properly():
    """Test the MCP server with proper initialization sequence."""
    
    print("=== Proper MCP Server Test ===")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            ["python", "app.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        # Step 1: Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": False
                    }
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print(f"Sending initialization: {json.dumps(init_request, indent=2)}")
        
        # Send initialization
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # Wait a bit for initialization
        await asyncio.sleep(1)
        
        # Step 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        print(f"Sending initialized notification: {json.dumps(initialized_notification, indent=2)}")
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        
        # Wait a bit
        await asyncio.sleep(1)
        
        # Step 3: Now send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print(f"Sending tools/list: {json.dumps(tools_request, indent=2)}")
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        
        # Wait for response
        await asyncio.sleep(2)
        
        # Step 4: Send a tool call
        tool_call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_current_time",
                "arguments": {}
            }
        }
        
        print(f"Sending tool call: {json.dumps(tool_call_request, indent=2)}")
        
        process.stdin.write(json.dumps(tool_call_request) + "\n")
        process.stdin.flush()
        
        # Wait for final response
        await asyncio.sleep(2)
        
        # Close stdin and get output
        process.stdin.close()
        
        # Wait for process to finish or timeout
        try:
            stdout, stderr = process.communicate(timeout=5)
            print(f"\n=== Server Output ===")
            print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            print(f"Process killed due to timeout")
            print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
                
    except Exception as e:
        print(f"Test failed: {e}")
        if 'process' in locals():
            process.kill()

def test_simple_tool_call():
    """Simple test to call the tool directly (bypassing MCP protocol)."""
    print("\n=== Simple Tool Test ===")
    
    try:
        # Import and test the function directly
        import app
        import asyncio
        
        async def run_test():
            tools = await app.handle_list_tools()
            print(f"Available tools: {[tool.name for tool in tools]}")
            
            result = await app.handle_call_tool("get_current_time", {})
            print(f"Tool result: {result[0].text}")
        
        asyncio.run(run_test())
        
    except Exception as e:
        print(f"Simple test failed: {e}")

if __name__ == "__main__":
    # Test the tool functions directly first
    test_simple_tool_call()
    
    # Then test the full MCP protocol
    asyncio.run(test_mcp_server_properly()) 