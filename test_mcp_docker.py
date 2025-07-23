#!/usr/bin/env python3
"""
Docker-specific test script for the NTP MCP server.
Tests the Docker container with proper MCP protocol handling.
"""

import json
import subprocess
import sys
import asyncio
import time
import os

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
        """Parse and display MCP responses."""
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
                        print(f"✅ Tool result: {content[0]['text']}")
                else:
                    print(f"✅ Response: {json.dumps(result, indent=2)}")
            else:
                print(f"ℹ️  Notification or other: {json.dumps(response, indent=2)}")
        
        return success
    
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
    print("\n🌍 Testing Different Configurations...")
    
    configs = [
        ("pool.ntp.org", "UTC"),
        ("time.google.com", "America/New_York"),
        ("time.cloudflare.com", "Europe/London"),
        ("time.apple.com", "Asia/Tokyo")
    ]
    
    for ntp_server, timezone in configs:
        print(f"\n🔧 Testing NTP: {ntp_server}, TZ: {timezone}")
        
        tester = DockerMCPTester()
        if not tester.start_container(ntp_server, timezone):
            continue
        
        try:
            stdout, stderr = await tester.test_full_mcp_flow()
            if stdout:
                success = tester.parse_responses(stdout)
                if success:
                    print(f"✅ Configuration {ntp_server}/{timezone} works!")
                else:
                    print(f"❌ Configuration {ntp_server}/{timezone} failed!")
            else:
                print(f"❌ No response from {ntp_server}/{timezone}")
                
        finally:
            tester.stop_container()
        
        await asyncio.sleep(1)  # Brief pause between tests

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

async def main():
    """Main test function."""
    print("🧪 NTP MCP Server Docker Test Suite")
    print("=" * 50)
    
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
    
    try:
        stdout, stderr = await tester.test_full_mcp_flow()
        
        if stdout:
            success = tester.parse_responses(stdout)
            tester.show_debug_info(stderr)
            
            if success:
                print("\n🎉 Basic test PASSED!")
            else:
                print("\n❌ Basic test FAILED!")
        else:
            print("\n❌ No response from server")
            
    finally:
        tester.stop_container()
    
    # Test 3: Different configurations
    await test_different_configurations()
    
    # Test 4: Docker management
    test_docker_management()
    
    print("\n🏁 Test Suite Complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1) 