# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project provides two main components:

### Matrix Chat Client
- **chatcli.py**: Interactive chat client for unencrypted Matrix messaging with integrated authentication
- Console command: `matrix-chat`

### MCP Server for AI Agents
- **matrix_mcp_server.py**: MCP server exposing Matrix messaging tools for AI agent integration
- Console command: `matrix-mcp-server` 
- Design document: **MCPDESIGN.md**

The project uses the `mautrix` library for Matrix protocol communication and focuses on unencrypted messaging for simplicity and reliability.

## Core Architecture

### SimpleChatClient Class (chatcli.py:68-395)
- Main client class that manages Matrix communication
- Uses memory-based stores (`MemoryStateStore`, `MemorySyncStore`) for session data
- Handles room joining, switching, and message sending/receiving
- Manages async event handlers for messages and member events

### MatrixMCPServer Class (matrix_mcp_server.py:30-290)
- MCP server wrapper around SimpleChatClient
- Exposes Matrix messaging as MCP tools for AI agents
- Handles pending response tracking for interactive workflows
- Manages environment-based authentication

### Key Components
- **HTTPAPI**: Matrix API client from mautrix library
- **Client**: mautrix client with state and sync stores
- **Event Handlers**: Message and member event processing
- **Room Management**: Join, switch, list rooms with alias resolution
- **MCP Tools**: send_message, wait_for_response, list_rooms
- **Response Tracking**: Future-based async response waiting with timeouts

## Development Commands

### Installation
```bash
uv sync
```

### Running the Applications

#### Matrix Chat Client

##### Global Installation (Recommended)
```bash
# Install globally with uv
uv tool install .

# Then use the command directly
matrix-chat <username>
matrix-chat <username> --password <password>
matrix-chat <username> --device-name <device_name>
matrix-chat <username> -p <password> -d <device_name>
matrix-chat <username> <homeserver>  # for custom homeserver
```

##### Local Development
```bash
# Run chat client (password will be prompted securely)
uv run matrix-chat <username>

# With password on command line
uv run matrix-chat <username> --password <password>

# With custom device name
uv run matrix-chat <username> --device-name <device_name>

# All options
uv run matrix-chat <username> -p <password> -d <device_name>

# Custom homeserver
uv run matrix-chat <username> <homeserver>

# or direct Python execution:
python chatcli.py <username>
python chatcli.py <username> --password <password>
python chatcli.py <username> --device-name <device_name>
```

#### MCP Server for AI Agents

##### Environment Setup
```bash
# Required environment variables
export MATRIX_USERNAME="your-bot@matrix.org"
export MATRIX_PASSWORD="your-password"
export MATRIX_ROOMID="#room:matrix.org"

# Optional environment variables
export MATRIX_HOMESERVER="https://matrix.org"  # default
export MATRIX_DEVICE_NAME="mcp-server"        # default
```

##### Running the Server
```bash
# Global installation
uv tool install .
matrix-mcp-server

# Local development
uv run matrix-mcp-server

# Direct Python execution
python matrix_mcp_server.py
```

### Console Scripts (via pyproject.toml)
The project defines console scripts that can be used via:
- `uv tool install .` for global installation - provides `matrix-chat` and `matrix-mcp-server` commands
- `uv run matrix-chat` and `uv run matrix-mcp-server` for local development
- Direct Python execution: `python chatcli.py` and `python matrix_mcp_server.py`

### Command-Line Arguments

#### Matrix Chat Client (`matrix-chat`)
- `username`: Required. Matrix username (e.g., poolagent or @poolagent:matrix.org)
- `homeserver`: Optional. Matrix homeserver URL (default: https://matrix.org)
- `--password` / `-p`: Optional. Matrix password (if not provided, prompted securely)
- `--device-name` / `-d`: Optional. Device name for session (default: "chatcli")

#### MCP Server (`matrix-mcp-server`)
- No command-line arguments - uses environment variables for configuration

### Practical Examples

#### Matrix Chat Client
```bash
# Basic usage - password prompted securely (uses matrix.org by default)
matrix-chat poolagent

# With password on command line (less secure, but useful for scripts)
matrix-chat poolagent --password mypassword

# With custom device name (useful for identifying multiple clients)
matrix-chat poolagent --device-name "laptop-client"

# All options combined
matrix-chat poolagent -p mypassword -d "laptop-client"

# Custom homeserver
matrix-chat poolagent https://custom.matrix.server

# Full Matrix ID format also supported
matrix-chat @poolagent:matrix.org --password mypassword
```

#### MCP Server
```bash
# Set environment variables
export MATRIX_USERNAME="bot@matrix.org"
export MATRIX_PASSWORD="bot-password"
export MATRIX_ROOMID="#ops:matrix.org"
export MATRIX_DEVICE_NAME="ai-agent-bot"

# Run MCP server
matrix-mcp-server
```

## Python Requirements
- Python 3.10+
- Dependencies: mautrix>=0.20.0, aiohttp>=3,<4, attrs>=18.1.0, yarl>=1.5,<2, mcp>=1.0.0

## Key Implementation Details

### Async Architecture
- Uses asyncio throughout for Matrix API communication
- Background sync task runs continuously (`client.start()`)
- CLI input handled with `asyncio.to_thread()` for non-blocking operation

### Room Handling
- Supports both room IDs (`!roomid:server.com`) and aliases (`#room:server.com`)
- Automatic alias resolution to room IDs
- Room state cached in memory stores
- Membership verification before message sending

### Message Flow
- Initial sync delay prevents message spam during startup
- Real-time message display with room context
- Support for text messages and emotes
- Unencrypted messaging only (by design)

### State Management
- Uses `MemoryStateStore` and `MemorySyncStore` for session persistence
- Room membership tracked manually due to sync timing issues
- Graceful cleanup of HTTP sessions and tasks on shutdown

### MCP Server Architecture
- **MatrixMCPServer**: Wraps SimpleChatClient with MCP protocol
- **Environment Configuration**: Uses env vars for authentication
- **Response Tracking**: Future-based async response waiting system
- **Tool Registration**: Exposes send_message, wait_for_response, list_rooms tools
- **Message Handling**: Enhanced message handler for pending response matching

## Testing and Development

This project uses `uv` for dependency management and doesn't include formal test scripts. Manual testing involves:

### Matrix Chat Client Testing:
1. Running `uv run matrix-chat <username>` (password prompted) or `uv run matrix-chat <username> --password <password>`
2. Testing room join/switch/messaging functionality

### MCP Server Testing:
1. Set environment variables: `MATRIX_USERNAME`, `MATRIX_PASSWORD`
2. Run `uv run matrix-mcp-server`
3. Test with SmolAgents or other MCP clients

No linting or type checking commands are defined in the current setup.