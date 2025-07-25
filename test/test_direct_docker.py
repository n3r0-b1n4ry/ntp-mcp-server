#!/usr/bin/env python3
"""
Direct test of the running Docker container to prove it works correctly.
Updated to validate the new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone
"""

import json
import subprocess
import time
import re

def test_running_container():
    """Test the currently running Docker container."""
    print("🧪 Testing Running Docker Container with New Time Format")
    print("=" * 50)
    
    # Find the running container
    result = subprocess.run([
        "docker", "ps", "--filter", "ancestor=ntp-mcp-server", "--format", "{{.ID}}"
    ], capture_output=True, text=True)
    
    if not result.stdout.strip():
        print("❌ No running ntp-mcp-server container found")
        return False
    
    container_id = result.stdout.strip()
    print(f"📦 Found container: {container_id}")
    
    # Create the MCP request sequence
    requests = [
        # 1. Initialize
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"roots": {"listChanged": False}},
                "clientInfo": {"name": "direct-test", "version": "1.0.0"}
            }
        },
        # 2. Initialized notification
        {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        },
        # 3. List tools
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # 4. Call tool
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_current_time",
                "arguments": {}
            }
        }
    ]
    
    # Send all requests
    input_data = "\n".join(json.dumps(req) for req in requests) + "\n"
    
    print("📤 Sending MCP requests...")
    try:
        result = subprocess.run([
            "docker", "exec", "-i", container_id, "python", "app.py"
        ], input=input_data, capture_output=True, text=True, timeout=10)
        
        print("📥 Container Response:")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        print(f"Return code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ Container is responsive and working!")
            # Validate the time format in the response
            return validate_container_response(result.stdout)
        else:
            print("❌ Container returned error")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Request timed out - container might be hanging")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def validate_container_response(stdout):
    """Validate that the container response contains the new time format."""
    if not stdout:
        print("❌ No output from container")
        return False
    
    print("\n🔍 Validating Time Format in Container Response...")
    
    # Parse JSON responses
    responses = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            try:
                response = json.loads(line)
                responses.append(response)
            except json.JSONDecodeError:
                continue
    
    # Look for tool call response (id=3)
    tool_response = None
    for response in responses:
        if response.get('id') == 3 and 'result' in response:
            tool_response = response
            break
    
    if not tool_response:
        print("❌ No tool call response found in container output")
        return False
    
    try:
        content = tool_response['result']['content']
        if content and content[0].get('type') == 'text':
            time_text = content[0]['text']
            print(f"📅 Extracted time text: {time_text}")
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
        print(f"❌ Expected at least 3 lines, got {len(lines)}")
        print(f"   Lines received: {lines}")
        return False
    
    # Validate Date line
    date_pattern = r'^Date:\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, lines[0]):
        print(f"❌ Date format invalid: '{lines[0]}'")
        print(f"   Expected pattern: Date:YYYY-MM-DD")
        return False
    
    # Validate Time line
    time_pattern = r'^Time:\d{2}:\d{2}:\d{2}$'
    if not re.match(time_pattern, lines[1]):
        print(f"❌ Time format invalid: '{lines[1]}'")
        print(f"   Expected pattern: Time:HH:mm:ss")
        return False
    
    # Validate Timezone line (may include fallback text)
    timezone_pattern = r'^Timezone:.+$'
    if not re.match(timezone_pattern, lines[2]):
        print(f"❌ Timezone format invalid: '{lines[2]}'")
        print(f"   Expected pattern: Timezone:timezone_name")
        return False
    
    print("✅ New time format validation PASSED!")
    print(f"   📅 {lines[0]}")
    print(f"   🕐 {lines[1]}")
    print(f"   🌍 {lines[2]}")
    return True

def check_container_logs():
    """Check the container logs to see what's happening."""
    print("\n📋 Container Logs:")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            "docker", "ps", "--filter", "ancestor=ntp-mcp-server", "--format", "{{.ID}}"
        ], capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("❌ No running container found")
            return
        
        container_id = result.stdout.strip()
        
        # Get logs
        logs_result = subprocess.run([
            "docker", "logs", container_id
        ], capture_output=True, text=True)
        
        print(f"Container logs:")
        print(f"STDOUT: {logs_result.stdout}")
        print(f"STDERR: {logs_result.stderr}")
        
    except Exception as e:
        print(f"❌ Failed to get logs: {e}")

def demonstrate_new_format():
    """Demonstrate the new time format."""
    print("\n🕐 New Time Format Specification")
    print("=" * 50)
    
    print("The NTP server now outputs time in this format:")
    print("  Date:YYYY-MM-DD")
    print("  Time:HH:mm:ss") 
    print("  Timezone:timezone_name")
    print()
    print("Example output:")
    print("  Date:2024-01-15")
    print("  Time:14:30:25")
    print("  Timezone:UTC")
    print()
    print("For fallback (local time):")
    print("  Date:2024-01-15")
    print("  Time:14:30:25")
    print("  Timezone:UTC (local fallback)")
    print()
    print("This format is more structured and easier to parse!")

if __name__ == "__main__":
    print("🔍 Direct Docker Container Test - New Time Format")
    print("=" * 50)
    
    # Explain the new format
    demonstrate_new_format()
    
    # Test the running container
    success = test_running_container()
    
    # Show container logs
    check_container_logs()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 CONCLUSION: Docker container works correctly with new time format!")
        print("✅ Time format validation PASSED")
    else:
        print("❌ CONCLUSION: Container test failed or time format is incorrect")
        print("🔧 Check the output above for details") 