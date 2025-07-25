#!/usr/bin/env python3
"""
Docker-specific test script for the NTP MCP server.
Tests the Docker container with proper MCP protocol handling.
Updated to validate new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone
"""

import json
import subprocess
import sys
import asyncio
import time
import os
import re

class DockerMCPTester:
    def __init__(self, image_name="ntp-mcp-server"):
        self.image_name = image_name
        self.container_name = None
        self.process = None
    
    def build_image(self):
        """Build the Docker image."""
        print("🔨 Building Docker image...")
        try:
            result = subprocess.run([
                "docker", "build", "-t", self.image_name, "."
            ], capture_output=True, text=True, check=True)
            print(f"✅ Docker image '{self.image_name}' built successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to build Docker image: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False
    
    def start_container(self, ntp_server="pool.ntp.org", timezone="UTC"):
        """Start the Docker container for testing."""
        print(f"🚀 Starting Docker container with NTP_SERVER={ntp_server}, TZ={timezone}")
        
        try:
            self.process = subprocess.Popen([
                "docker", "run", "--rm", "-i",
                "-e", f"NTP_SERVER={ntp_server}",
                "-e", f"TZ={timezone}",
                self.image_name
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print("✅ Docker container started successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to start Docker container: {e}")
            return False
    
    def stop_container(self):
        """Stop the Docker container."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
                print("✅ Docker container stopped")
            except:
                self.process.kill()
                print("🔪 Docker container killed")
    
    async def send_mcp_message(self, message):
        """Send an MCP message to the container."""
        if not self.process:
            raise RuntimeError("Container not started")
        
        json_message = json.dumps(message) + "\n"
        self.process.stdin.write(json_message)
        self.process.stdin.flush()
        await asyncio.sleep(0.5)  # Give time for processing
    
    async def test_full_mcp_flow(self):
        """Test the complete MCP flow with the Docker container."""
        print("\n🧪 Testing Full MCP Protocol Flow...")
        
        try:
            # Step 1: Initialize
            print("📤 Sending initialization request...")
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"roots": {"listChanged": False}},
                    "clientInfo": {"name": "docker-test-client", "version": "1.0.0"}
                }
            }
            await self.send_mcp_message(init_request)
            
            # Step 2: Send initialized notification
            print("📤 Sending initialized notification...")
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            await self.send_mcp_message(initialized_notification)
            
            # Step 3: List tools
            print("📤 Requesting tools list...")
            tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            await self.send_mcp_message(tools_request)
            
            # Step 4: Call the NTP tool
            print("📤 Calling get_current_time tool...")
            tool_call = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "get_current_time",
                    "arguments": {}
                }
            }
            await self.send_mcp_message(tool_call)
            
            # Step 5: Give time for all responses
            await asyncio.sleep(2)
            
            # Close stdin and get results
            self.process.stdin.close()
            stdout, stderr = self.process.communicate(timeout=10)
            
            return stdout, stderr
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return None, str(e)
    
    def parse_responses(self, stdout):
        """Parse and display MCP responses, validating the new time format."""
        print("\n📥 Server Responses:")
        print("=" * 50)
        
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
        
        success = True
        time_format_validated = False
        
        for i, response in enumerate(responses, 1):
            print(f"\n📋 Response {i}:")
            
            if "error" in response:
                print(f"❌ Error: {response['error']}")
                success = False
            elif "result" in response:
                result = response["result"]
                
                if "serverInfo" in result:
                    print(f"✅ Server initialized: {result['serverInfo']['name']} v{result['serverInfo']['version']}")
                elif "tools" in result:
                    tools = result["tools"]
                    print(f"✅ Tools available: {[tool['name'] for tool in tools]}")
                elif "content" in result:
                    content = result["content"]
                    if content and content[0].get("type") == "text":
                        time_text = content[0]['text']
                        print(f"✅ Tool result received:")
                        print(f"   {time_text}")
                        
                        # Validate the new time format
                        if self.validate_new_time_format(time_text):
                            time_format_validated = True
                        else:
                            success = False
                else:
                    print(f"✅ Response: {json.dumps(result, indent=2)}")
            else:
                print(f"ℹ️  Notification or other: {json.dumps(response, indent=2)}")
        
        if not time_format_validated:
            print("❌ Time format validation failed or no time response found")
            success = False
        
        return success
    
    def validate_new_time_format(self, time_text):
        """Validate the new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone"""
        print(f"\n🔍 Validating time format...")
        
        # Split the text into lines
        lines = time_text.split('\n')
        
        if len(lines) < 3:
            print(f"❌ Expected at least 3 lines, got {len(lines)}")
            return False
        
        # Validate Date line
        date_pattern = r'^Date:\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, lines[0]):
            print(f"❌ Date format invalid: '{lines[0]}'")
            print(f"   Expected: Date:YYYY-MM-DD")
            return False
        
        # Validate Time line
        time_pattern = r'^Time:\d{2}:\d{2}:\d{2}$'
        if not re.match(time_pattern, lines[1]):
            print(f"❌ Time format invalid: '{lines[1]}'")
            print(f"   Expected: Time:HH:mm:ss")
            return False
        
        # Validate Timezone line (may include fallback text)
        timezone_pattern = r'^Timezone:.+$'
        if not re.match(timezone_pattern, lines[2]):
            print(f"❌ Timezone format invalid: '{lines[2]}'")
            print(f"   Expected: Timezone:timezone_name")
            return False
        
        print("✅ New time format validation PASSED!")
        print(f"   📅 Date: {lines[0]}")
        print(f"   🕐 Time: {lines[1]}")
        print(f"   🌍 Timezone: {lines[2]}")
        return True
    
    def show_debug_info(self, stderr):
        """Show debug information from stderr."""
        if stderr:
            print(f"\n🐛 Debug Information:")
            print("=" * 50)
            for line in stderr.strip().split('\n'):
                if line.strip():
                    if "ERROR" in line:
                        print(f"❌ {line}")
                    elif "WARNING" in line:
                        print(f"⚠️  {line}")
                    elif "INFO" in line:
                        print(f"ℹ️  {line}")
                    else:
                        print(f"📝 {line}")

async def test_different_configurations():
    """Test different NTP server and timezone configurations."""
    print("\n🌍 Testing Different Configurations with New Time Format...")
    
    configs = [
        ("pool.ntp.org", "UTC"),
        ("time.google.com", "America/New_York"),
        ("time.cloudflare.com", "Europe/London"),
        ("time.apple.com", "Asia/Tokyo")
    ]
    
    results = []
    
    for ntp_server, timezone in configs:
        print(f"\n🔧 Testing NTP: {ntp_server}, TZ: {timezone}")
        
        tester = DockerMCPTester()
        if not tester.start_container(ntp_server, timezone):
            results.append((ntp_server, timezone, False))
            continue
        
        try:
            stdout, stderr = await tester.test_full_mcp_flow()
            if stdout:
                success = tester.parse_responses(stdout)
                results.append((ntp_server, timezone, success))
                if success:
                    print(f"✅ Configuration {ntp_server}/{timezone} works with new format!")
                else:
                    print(f"❌ Configuration {ntp_server}/{timezone} failed!")
            else:
                print(f"❌ No response from {ntp_server}/{timezone}")
                results.append((ntp_server, timezone, False))
                
        finally:
            tester.stop_container()
        
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Summary
    print(f"\n📊 Configuration Test Results:")
    print("=" * 50)
    for ntp_server, timezone, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {ntp_server} / {timezone}: {status}")
    
    return all(result[2] for result in results)

def test_docker_management():
    """Test Docker image management commands."""
    print("\n🐳 Testing Docker Management...")
    
    # List Docker images
    try:
        result = subprocess.run([
            "docker", "images", "ntp-mcp-server"
        ], capture_output=True, text=True, check=True)
        print("✅ Docker image exists:")
        print(result.stdout)
    except subprocess.CalledProcessError:
        print("❌ Docker image not found")
    
    # Test container cleanup
    try:
        subprocess.run([
            "docker", "ps", "-a", "--filter", "ancestor=ntp-mcp-server", "--format", "table {{.ID}}\t{{.Status}}"
        ], check=True)
        print("✅ Container status checked")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Container status check failed: {e}")

def show_new_format_info():
    """Show information about the new time format."""
    print("🕐 New Time Format Information")
    print("=" * 50)
    print("The NTP server now outputs time in this structured format:")
    print("  Date:YYYY-MM-DD")
    print("  Time:HH:mm:ss")
    print("  Timezone:timezone_name")
    print()
    print("Benefits of the new format:")
    print("  ✅ More structured and easier to parse")
    print("  ✅ Separate date and time components")
    print("  ✅ Clear timezone information")
    print("  ✅ Consistent formatting across all responses")
    print()

async def main():
    """Main test function."""
    print("🧪 NTP MCP Server Docker Test Suite - New Time Format")
    print("=" * 60)
    
    # Show format information
    show_new_format_info()
    
    # Test 1: Build the image
    tester = DockerMCPTester()
    if not tester.build_image():
        print("❌ Cannot proceed without Docker image")
        return
    
    # Test 2: Basic functionality test
    print("\n🔍 Basic Functionality Test")
    if not tester.start_container():
        print("❌ Cannot start container")
        return
    
    basic_success = False
    try:
        stdout, stderr = await tester.test_full_mcp_flow()
        
        if stdout:
            basic_success = tester.parse_responses(stdout)
            tester.show_debug_info(stderr)
            
            if basic_success:
                print("\n🎉 Basic test PASSED with new time format!")
            else:
                print("\n❌ Basic test FAILED!")
        else:
            print("\n❌ No response from server")
            
    finally:
        tester.stop_container()
    
    # Test 3: Different configurations
    config_success = await test_different_configurations()
    
    # Test 4: Docker management
    test_docker_management()
    
    # Final summary
    print("\n🏁 Test Suite Complete!")
    print("=" * 60)
    print("📊 Final Results:")
    print(f"   Basic functionality: {'✅ PASSED' if basic_success else '❌ FAILED'}")
    print(f"   Configuration tests: {'✅ PASSED' if config_success else '❌ FAILED'}")
    
    if basic_success and config_success:
        print("\n🎉 ALL TESTS PASSED! New time format works perfectly!")
    else:
        print("\n❌ Some tests failed - check the output above for details")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 