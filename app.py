#!/usr/bin/env python3
import asyncio
import ntplib
from datetime import datetime, timezone
import pytz
import os
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging with less verbose output
logging.basicConfig(level=logging.WARNING)  # Only show warnings and errors
logger = logging.getLogger("ntp-server")

# Create server instance
server = Server("ntp-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="get_current_time",
            description="Get the current time from an NTP server specified by NTP_SERVER env var (default 'pool.ntp.org'), in time zone specified by TZ env var (default system local)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    """Handle tool calls."""
    if name != "get_current_time":
        raise ValueError(f"Unknown tool: {name}")
    
    # Get NTP server from environment variable, default to 'pool.ntp.org'
    ntp_server = os.getenv('NTP_SERVER', 'pool.ntp.org')
    
    # Get time zone from environment variable
    tz_name = os.getenv('TZ')
    if tz_name:
        try:
            tz = pytz.timezone(tz_name)
        except pytz.UnknownTimeZoneError:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Unknown time zone: {tz_name}"
                )
            ]
    else:
        tz = None  # Use system's local time zone if TZ is not set

    try:
        # Attempt to get time from NTP server
        c = ntplib.NTPClient()
        response = await asyncio.get_event_loop().run_in_executor(
            None, c.request, ntp_server
        )
        utc_dt = datetime.fromtimestamp(response.tx_time, timezone.utc)
        
        # Convert to desired time zone or system's local time zone
        if tz:
            local_dt = utc_dt.astimezone(tz)
        else:
            local_dt = utc_dt.astimezone()  # System's local time zone
        
        result = f"Current time: {local_dt.isoformat()}"
        logger.info(f"NTP time retrieved: {result}")
        
    except Exception as e:
        # If NTP fails, fall back to local time
        logger.warning(f"NTP failed ({str(e)}), falling back to local time")
        try:
            if tz:
                # If TZ is set, get local time in that time zone
                local_dt = datetime.now(tz)
            else:
                # Otherwise, get system's local time with its time zone
                utc_now = datetime.now(timezone.utc)
                local_dt = utc_now.astimezone()
            
            result = f"Current time (local fallback): {local_dt.isoformat()}"
            
        except Exception as e2:
            # If all else fails, return an error
            result = f"Error: Failed to get time - {str(e2)}"
            logger.error(f"Failed to get time: {str(e2)}")
    
    return [
        types.TextContent(
            type="text",
            text=result
        )
    ]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def get_ntp_time(ntp_server):
    """Helper function to get NTP time with retry logic"""
    c = ntplib.NTPClient()
    return c.request(ntp_server)

async def main():
    # Run the server using stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="ntp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())