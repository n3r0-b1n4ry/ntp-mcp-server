# NTP MCP Server 🕒

A Model Context Protocol (MCP) server that provides accurate time information from Network Time Protocol (NTP) servers with timezone support and structured output formatting.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com/r/n3r0b1n4ry/ntp-mcp-server)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green?logo=anthropic)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org/)
#### Add NTP MCP Server to LM Studio
[![Add NTP MCP Server to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-dark.svg)](https://lmstudio.ai/install-mcp?name=ntp-server&config=eyJjb21tYW5kIjoicHl0aG9uIiwiYXJncyI6WyJhcHAucHkiXSwiY3dkIjoiLiIsImVudiI6eyJOVFBfU0VSVkVSIjoicG9vbC5udHAub3JnIiwiVFoiOiJVVEMifX0=)
#### Add NTP MCP Server Docker to LM Studio
[![Add NTP MCP Server Docker to LM Studio](https://files.lmstudio.ai/deeplink/mcp-install-dark.svg)](https://lmstudio.ai/install-mcp?name=ntp-server-docker&config=eyJjb21tYW5kIjoiZG9ja2VyIiwiYXJncyI6WyJydW4iLCItLXJtIiwiLWkiLCItZSIsIk5UUF9TRVJWRVIiLCItZSIsIlRaIiwibnRwLW1jcC1zZXJ2ZXIiXSwiZW52Ijp7Ik5UUF9TRVJWRVIiOiJwb29sLm50cC5vcmciLCJUWiI6IlVUQyJ9fQ==)

## ✨ Features

- 🌍 **Multiple NTP Server Support**: Connect to any NTP server worldwide
- 🕰️ **Timezone Conversion**: Automatic timezone conversion with pytz
- 📋 **Structured Output Format**: Clean, parseable time format with separate date, time, and timezone components
- 🔄 **Fallback Mechanism**: Falls back to local time if NTP is unavailable
- 🐳 **Docker Ready**: Fully containerized for easy deployment
- ⚡ **Retry Logic**: Automatic retry with exponential backoff
- 🔧 **Configurable**: Environment variable configuration
- 📋 **MCP Compatible**: Works with Claude Desktop and other MCP clients
- 🧪 **Comprehensive Testing**: Full test suite with format validation

## 🕐 Time Output Format

The NTP server now outputs time in a **structured, easy-to-parse format**:

```
Date:YYYY-MM-DD
Time:HH:mm:ss
Timezone:timezone_name
```

### Example Outputs

**Successful NTP Response:**
```
Date:2025-07-25
Time:14:30:25
Timezone:UTC
```

**Fallback Response (when NTP unavailable):**
```
Date:2025-07-25
Time:14:30:25
Timezone:UTC (local fallback)
```

### Benefits of the New Format

- ✅ **More structured and easier to parse**
- ✅ **Separate date and time components**
- ✅ **Clear timezone information**
- ✅ **Consistent formatting across all responses**
- ✅ **Machine-readable and human-friendly**

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Build the Docker image
docker build -t ntp-mcp-server .

# Run with default settings
docker run --rm -i ntp-mcp-server

# Run with custom NTP server and timezone
docker run --rm -i \
  -e NTP_SERVER=time.google.com \
  -e TZ=America/New_York \
  ntp-mcp-server
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Direct Python Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

## 📦 Installation

### Prerequisites

- **Docker** (recommended) or **Python 3.11+**
- **MCP Client** (Claude Desktop, etc.)

### Method 1: Docker Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd ntp-mcp-server
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t ntp-mcp-server .
   ```

3. **Configure your MCP client** using `mcp-docker.json`

### Method 2: Python Installation

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd ntp-mcp-server
   pip install -r requirements.txt
   ```

2. **Configure your MCP client** using `mcp.json`

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NTP_SERVER` | `pool.ntp.org` | NTP server hostname |
| `TZ` | System local | Target timezone (e.g., `UTC`, `America/New_York`) |

### Supported NTP Servers

- `pool.ntp.org` (default)
- `time.google.com`
- `time.cloudflare.com`
- `time.apple.com`
- `time.nist.gov`
- Any RFC 5905 compliant NTP server

### Supported Timezones

Any timezone supported by the `pytz` library:
- `UTC`
- `America/New_York`
- `Europe/London`
- `Asia/Tokyo`
- `Australia/Sydney`
- And many more...

## 🔧 MCP Client Configuration

### For Claude Desktop

Add to your Claude Desktop configuration:

#### Docker Version (Recommended)
```json
{
  "mcpServers": {
    "ntp-server-docker": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-e", "NTP_SERVER", "-e", "TZ", "ntp-mcp-server"],
      "env": {
        "NTP_SERVER": "pool.ntp.org",
        "TZ": "UTC"
      }
    }
  }
}
```

#### Python Version
```json
{
  "mcpServers": {
    "ntp-server": {
      "command": "python",
      "args": ["app.py"],
      "cwd": "/path/to/your/ntp/project",
      "env": {
        "NTP_SERVER": "pool.ntp.org",
        "TZ": "UTC"
      }
    }
  }
}
```

## 🛠️ Available Tools

### `get_current_time`

Retrieves the current time from the configured NTP server in structured format.

**Parameters**: None

**Returns**: Current time in structured format with separate date, time, and timezone components

**Example Response**:
```
Date:2025-07-25
Time:14:30:25
Timezone:UTC
```

**Fallback Behavior**:
- If NTP server is unreachable, falls back to local system time
- Fallback responses include "(local fallback)" indicator
- Returns error message if all time sources fail

## 🧪 Testing

The project includes a comprehensive test suite with format validation:

### Available Test Scripts

1. **`test/simple_test.py`** - Windows-compatible direct testing
2. **`test/test_mcp.py`** - Basic MCP protocol testing with format validation
3. **`test/test_mcp_proper.py`** - Advanced MCP protocol testing
4. **`test/test_mcp_docker.py`** - Comprehensive Docker testing
5. **`test/test_direct_docker.py`** - Direct Docker container testing
6. **`test/run_all_tests.py`** - Comprehensive test runner

### Run All Tests

```bash
# Run comprehensive test suite
python test/run_all_tests.py

# Run individual tests
python test/simple_test.py           # Simple direct testing
python test/test_mcp_docker.py       # Docker functionality
python test/test_mcp_proper.py       # MCP protocol testing
python test/test_mcp.py              # Basic functionality
```

### Test Coverage

The test suite validates:
- ✅ **Time format structure** (Date:YYYY-MM-DD, Time:HH:mm:ss, Timezone:name)
- ✅ **Multiple NTP servers** (pool.ntp.org, time.google.com, time.cloudflare.com)
- ✅ **Different timezones** (UTC, America/New_York, Europe/London, Asia/Tokyo)
- ✅ **Docker containerization** with full MCP protocol
- ✅ **Environment variable configuration**
- ✅ **Fallback behavior** when NTP is unavailable
- ✅ **MCP protocol compliance** (initialization, tools list, tool calls)

### Manual Testing

```bash
# Test direct function call
python -c "import app, asyncio; result = asyncio.run(app.handle_call_tool('get_current_time', {})); print(result[0].text)"

# Start a container for testing
docker run --rm -i -e NTP_SERVER=time.google.com -e TZ=America/New_York ntp-mcp-server

# Send MCP requests (in another terminal)
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | docker exec -i <container-id> cat
```

## 🐳 Docker Details

### Image Information
- **Base Image**: `python:3.11-slim`
- **Size**: ~151MB
- **Architecture**: Multi-platform support

### Build Arguments
```bash
# Build with custom tag
docker build -t my-ntp-server .

# Build for specific platform
docker build --platform linux/amd64 -t ntp-mcp-server .
```

### Volume Mounts
No persistent volumes required - this is a stateless service.

## 📊 Project Structure

```
ntp-mcp-server/
├── app.py                      # Main MCP server implementation
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker build configuration
├── docker-compose.yml          # Docker Compose setup
├── .dockerignore               # Docker build optimization
├── .gitignore                  # Git ignore configuration
├── LICENSE                     # License information
├── config/
│   ├── mcp.json                # MCP client config (Python)
│   └── mcp-docker.json         # MCP client config (Docker)
├── test/
│   ├── simple_test.py          # Windows-compatible direct testing
│   ├── test_mcp.py             # Basic functionality tests with format validation
│   ├── test_mcp_proper.py      # Advanced MCP protocol tests
│   ├── test_mcp_docker.py      # Comprehensive Docker tests
│   ├── test_direct_docker.py   # Direct container tests
│   └── run_all_tests.py        # Comprehensive test runner
└── README.md                   # This file
```

## 🔍 Troubleshooting

### Common Issues

#### "Processing request of type ListToolsRequest" Error

**This is NOT an error!** This is normal debug logging. The message:
```
[ERROR] [Plugin(mcp/ntp-server-docker)] stderr: INFO:mcp.server.lowlevel.server:Processing request of type ListToolsRequest
```

Means your server is **working correctly**. The `INFO:` indicates it's just debug information.

#### Container Exits Immediately

MCP servers are designed to run as stdio servers. They exit when stdin is closed, which is normal behavior.

#### NTP Server Unreachable

The server will automatically fall back to local time if the NTP server is unreachable. Check your network connectivity and firewall settings.

#### Timezone Not Found

Ensure you're using a valid timezone identifier from the [pytz documentation](https://pythonhosted.org/pytz/).

#### Time Format Issues

The new structured format should always return:
```
Date:YYYY-MM-DD
Time:HH:mm:ss
Timezone:timezone_name
```

If you see different formatting, run the test suite to validate:
```bash
python test/simple_test.py
```

### Debug Commands

```bash
# Check if container is running
docker ps --filter ancestor=ntp-mcp-server

# View container logs
docker logs <container-id>

# Test container responsiveness with new format
python test/test_direct_docker.py

# Run comprehensive test suite
python test/run_all_tests.py

# Check NTP connectivity
docker run --rm ntp-mcp-server python -c "import ntplib; print(ntplib.NTPClient().request('pool.ntp.org'))"

# Validate time format directly
python -c "import app, asyncio; result = asyncio.run(app.handle_call_tool('get_current_time', {})); print('Format:', repr(result[0].text))"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `python test/run_all_tests.py`
6. Validate time format: `python test/simple_test.py`
7. Commit your changes: `git commit -m "Add feature"`
8. Push to the branch: `git push origin feature-name`
9. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Links

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [NTP Protocol (RFC 5905)](https://tools.ietf.org/html/rfc5905)
- [Docker Documentation](https://docs.docker.com/)
- [Python pytz Documentation](https://pythonhosted.org/pytz/)

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Run the test suite to verify functionality: `python test/run_all_tests.py`
3. Validate time format: `python test/simple_test.py`
4. Check that your MCP client configuration is correct
5. Ensure Docker is running (for Docker deployment)

## 🏷️ Version History

- **v2.0.0** - **NEW STRUCTURED TIME FORMAT**
  - ✨ **New structured output format**: `Date:YYYY-MM-DD\nTime:HH:mm:ss\nTimezone:timezone`
  - 🧪 **Enhanced test suite** with comprehensive format validation
  - 🔧 **Improved Windows compatibility** with dedicated test scripts
  - 📊 **Better error handling** and fallback behavior
  - 🐳 **Updated Docker tests** with full MCP protocol validation
  
- **v1.0.0** - Initial release with NTP support and Docker containerization
  - Full timezone support with pytz
  - Comprehensive test suite
  - Docker and Python deployment options
  - MCP protocol compliance

---

**Made with ❤️ for the MCP community** 