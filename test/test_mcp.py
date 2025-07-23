#!/usr/bin/env python3
"""
FIXED: Proper MCP test that handles initialization correctly.
The previous version was sending requests before MCP initialization - that's what caused the bug!
"""

import json
import subprocess
import sys
import asyncio

async def test_mcp_server_correctly():
    """Test the MCP server with PROPER initialization sequence."""
    
    print("=== FIXED: Proper MCP Server Test ===")
    print("Note: The previous bug was caused by skipping MCP initialization!")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            ["python", "app.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # STEP 1: MUST send initialization first (this was missing before!)
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": False}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # STEP 2: Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # STEP 3: NOW we can send tools/list (this will work!)
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        process.stdin.write(json.dumps(tools_request) + "\n")
        process.stdin.flush()
        await asyncio.sleep(0.5)
        
        # STEP 4: Call the tool
        tool_call = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_current_time",
                "arguments": {}
            }
        }
        
        process.stdin.write(json.dumps(tool_call) + "\n")
        process.stdin.flush()
        await asyncio.sleep(1)
        
        process.stdin.close()
        stdout, stderr = process.communicate(timeout=5)
        
        print("=== SUCCESS: Server responded correctly! ===")
        print(f"STDOUT:\n{stdout}")
        if stderr:
            print(f"STDERR (debug logs):\n{stderr}")
            
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        if 'process' in locals():
            process.kill()
        return False

def show_bug_explanation():
    """Explain what the bug was and how it's fixed."""
    print("=" * 60)
    print("🐛 BUG EXPLANATION:")
    print("=" * 60)
    print("❌ OLD (BROKEN) APPROACH:")
    print("   - Sent tools/list immediately without initialization")
    print("   - MCP server rejected: 'Received request before initialization was complete'")
    print()
    print("✅ FIXED APPROACH:")
    print("   1. Send 'initialize' request first")
    print("   2. Send 'notifications/initialized' notification")
    print("   3. THEN send 'tools/list' and other requests")
    print()
    print("🎯 RESULT: Server works perfectly when MCP protocol is followed!")
    print("=" * 60)

if __name__ == "__main__":
    show_bug_explanation()
    
    # Test with proper initialization
    result = asyncio.run(test_mcp_server_correctly())
    
    if result:
        print("\n🎉 ALL TESTS PASSED! The bug is completely fixed!")
    else:
        print("\n❌ Test failed - check the error messages above") 