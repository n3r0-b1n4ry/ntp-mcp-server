#!/usr/bin/env python3
"""
Proper MCP test that handles the initialization sequence.
"""

import json
import subprocess
import sys
import asyncio
import time
import re

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
            
            # Parse and validate responses
            return parse_and_validate_responses(stdout)
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            print(f"Process killed due to timeout")
            print(f"STDOUT:\n{stdout}")
            if stderr:
                print(f"STDERR:\n{stderr}")
            return False
                
    except Exception as e:
        print(f"Test failed: {e}")
        if 'process' in locals():
            process.kill()
        return False

def parse_and_validate_responses(stdout):
    """Parse MCP responses and validate the time format."""
    if not stdout:
        print("❌ No responses received")
        return False
    
    responses = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            try:
                response = json.loads(line)
                responses.append(response)
            except json.JSONDecodeError:
                print(f"⚠️  Invalid JSON: {line}")
    
    print(f"\n📋 Parsed {len(responses)} responses")
    
    # Look for tool call response
    tool_response = None
    for response in responses:
        if response.get('id') == 3 and 'result' in response:  # Tool call response
            tool_response = response
            break
    
    if not tool_response:
        print("❌ No tool call response found")
        return False
    
    # Extract the time text from the response
    try:
        content = tool_response['result']['content']
        if content and content[0].get('type') == 'text':
            time_text = content[0]['text']
            print(f"📅 Received time text: {time_text}")
            return validate_new_time_format(time_text)
        else:
            print("❌ No text content in tool response")
            return False
    except (KeyError, IndexError) as e:
        print(f"❌ Error parsing tool response: {e}")
        return False

def validate_new_time_format(time_text):
    """Validate the new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone"""
    
    # Split the text into lines
    lines = time_text.split('\n')
    
    if len(lines) < 3:
        print(f"❌ Expected 3 lines, got {len(lines)}")
        return False
    
    # Validate Date line
    date_pattern = r'^Date:\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, lines[0]):
        print(f"❌ Date format invalid: {lines[0]}")
        print(f"   Expected: Date:YYYY-MM-DD")
        return False
    
    # Validate Time line
    time_pattern = r'^Time:\d{2}:\d{2}:\d{2}$'
    if not re.match(time_pattern, lines[1]):
        print(f"❌ Time format invalid: {lines[1]}")
        print(f"   Expected: Time:HH:mm:ss")
        return False
    
    # Validate Timezone line
    timezone_pattern = r'^Timezone:.+$'
    if not re.match(timezone_pattern, lines[2]):
        print(f"❌ Timezone format invalid: {lines[2]}")
        print(f"   Expected: Timezone:timezone_name")
        return False
    
    print("✅ New time format validation PASSED!")
    print(f"   Date: {lines[0]}")
    print(f"   Time: {lines[1]}")
    print(f"   Timezone: {lines[2]}")
    return True

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
            time_text = result[0].text
            print(f"Tool result: {time_text}")
            
            # Validate the format
            if validate_new_time_format(time_text):
                print("✅ Direct tool call format validation PASSED!")
                return True
            else:
                print("❌ Direct tool call format validation FAILED!")
                return False
        
        return asyncio.run(run_test())
        
    except Exception as e:
        print(f"Simple test failed: {e}")
        return False

if __name__ == "__main__":
    print("🕐 Testing NTP Server with New Time Format")
    print("Expected format: Date:YYYY-MM-DD\\nTime:HH:mm:ss\\nTimezone:timezone")
    print("=" * 60)
    
    # Test the tool functions directly first
    direct_success = test_simple_tool_call()
    
    # Then test the full MCP protocol
    mcp_success = asyncio.run(test_mcp_server_properly())
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Direct tool call: {'✅ PASSED' if direct_success else '❌ FAILED'}")
    print(f"   MCP protocol test: {'✅ PASSED' if mcp_success else '❌ FAILED'}")
    
    if direct_success and mcp_success:
        print("\n🎉 ALL TESTS PASSED! New time format works correctly!")
    else:
        print("\n❌ Some tests failed - check the output above") 