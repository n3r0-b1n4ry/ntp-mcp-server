#!/usr/bin/env python3
"""
Simple test script for the NTP server that works on Windows.
Tests the new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone
"""

import sys
import os
import re
import asyncio

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import app
except ImportError as e:
    print(f"❌ Failed to import app: {e}")
    sys.exit(1)

def validate_time_format(time_text):
    """Validate the new time format: Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone"""
    print(f"🔍 Validating time format...")
    print(f"📅 Received: {repr(time_text)}")
    
    # Split the text into lines
    lines = time_text.split('\n')
    
    if len(lines) < 3:
        print(f"❌ Expected at least 3 lines, got {len(lines)}")
        print(f"   Lines: {lines}")
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
    
    # Validate Timezone line
    timezone_pattern = r'^Timezone:.+$'
    if not re.match(timezone_pattern, lines[2]):
        print(f"❌ Timezone format invalid: '{lines[2]}'")
        print(f"   Expected: Timezone:timezone_name")
        return False
    
    print("✅ Time format validation PASSED!")
    print(f"   📅 Date: {lines[0]}")
    print(f"   🕐 Time: {lines[1]}")
    print(f"   🌍 Timezone: {lines[2]}")
    return True

async def test_tool_directly():
    """Test the get_current_time tool directly."""
    print("🧪 Testing get_current_time tool directly...")
    
    try:
        # List available tools
        tools = await app.handle_list_tools()
        print(f"📋 Available tools: {[tool.name for tool in tools]}")
        
        # Call the tool
        result = await app.handle_call_tool("get_current_time", {})
        time_text = result[0].text
        
        print(f"📤 Tool result:")
        print(f"   {time_text}")
        
        # Validate the format
        if validate_time_format(time_text):
            print("✅ Direct tool test PASSED!")
            return True
        else:
            print("❌ Direct tool test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Tool test failed: {e}")
        return False

def test_with_environment_variables():
    """Test with different environment variables."""
    print("\n🌍 Testing with different environment variables...")
    
    test_configs = [
        ("pool.ntp.org", "UTC"),
        ("time.google.com", "America/New_York"),
        ("time.cloudflare.com", "Europe/London"),
    ]
    
    results = []
    
    for ntp_server, timezone in test_configs:
        print(f"\n🔧 Testing NTP_SERVER={ntp_server}, TZ={timezone}")
        
        # Set environment variables
        os.environ['NTP_SERVER'] = ntp_server
        os.environ['TZ'] = timezone
        
        try:
            # Call the tool with new environment
            result = asyncio.run(app.handle_call_tool("get_current_time", {}))
            time_text = result[0].text
            
            print(f"📤 Result: {time_text}")
            
            if validate_time_format(time_text):
                print(f"✅ Configuration {ntp_server}/{timezone} PASSED!")
                results.append(True)
            else:
                print(f"❌ Configuration {ntp_server}/{timezone} FAILED!")
                results.append(False)
                
        except Exception as e:
            print(f"❌ Configuration {ntp_server}/{timezone} failed: {e}")
            results.append(False)
    
    # Clean up environment
    if 'NTP_SERVER' in os.environ:
        del os.environ['NTP_SERVER']
    if 'TZ' in os.environ:
        del os.environ['TZ']
    
    return all(results)

def main():
    """Main test function."""
    print("🕐 Simple NTP Server Test - New Time Format")
    print("=" * 60)
    print("Expected format: Date:YYYY-MM-DD\\nTime:HH:mm:ss\\nTimezone:timezone")
    print("=" * 60)
    
    # Test 1: Direct tool call
    print("\n📋 Test 1: Direct Tool Call")
    direct_success = asyncio.run(test_tool_directly())
    
    # Test 2: Environment variable configurations
    print("\n📋 Test 2: Environment Variable Configurations")
    env_success = test_with_environment_variables()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    print(f"   Direct tool call: {'✅ PASSED' if direct_success else '❌ FAILED'}")
    print(f"   Environment tests: {'✅ PASSED' if env_success else '❌ FAILED'}")
    
    if direct_success and env_success:
        print("\n🎉 ALL TESTS PASSED! New time format works perfectly!")
        return True
    else:
        print("\n❌ Some tests failed - check the output above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 