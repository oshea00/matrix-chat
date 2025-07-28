# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple Python-based Matrix chat client:
- **chatcli.py**: Main chat client for unencrypted Matrix messaging with integrated authentication

The project uses the `mautrix` library for Matrix protocol communication and focuses on unencrypted messaging for simplicity and reliability.

## Core Architecture

### SimpleChatClient Class (chatcli.py:32-327)
- Main client class that manages Matrix communication
- Uses memory-based stores (`MemoryStateStore`, `MemorySyncStore`) for session data
- Handles room joining, switching, and message sending/receiving
- Manages async event handlers for messages and member events

### Key Components
- **HTTPAPI**: Matrix API client from mautrix library
- **Client**: mautrix client with state and sync stores
- **Event Handlers**: Message and member event processing
- **Room Management**: Join, switch, list rooms with alias resolution

## Development Commands

### Installation
```bash
uv sync
```

### Running the Applications

#### Global Installation (Recommended)
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

#### Local Development
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

### Console Scripts (via pyproject.toml)
The project defines a console script that can be used via:
- `uv tool install .` for global installation - provides `matrix-chat` command
- `uv run matrix-chat` for local development
- Direct Python execution: `python chatcli.py` (with same argument structure)

### Command-Line Arguments
- `username`: Required. Matrix username (e.g., poolagent or @poolagent:matrix.org)
- `homeserver`: Optional. Matrix homeserver URL (default: https://matrix.org)
- `--password` / `-p`: Optional. Matrix password (if not provided, prompted securely)
- `--device-name` / `-d`: Optional. Device name for session (default: "chatcli")

### Practical Examples
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

## Python Requirements
- Python 3.10+
- Dependencies: mautrix>=0.20.0, aiohttp>=3,<4, attrs>=18.1.0, yarl>=1.5,<2

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

## Testing and Development

This project uses `uv` for dependency management and doesn't include formal test scripts. Manual testing involves:
1. Running `uv run matrix-chat <username>` (password prompted) or `uv run matrix-chat <username> --password <password>`
2. Testing room join/switch/messaging functionality

No linting or type checking commands are defined in the current setup.