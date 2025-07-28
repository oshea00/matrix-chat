# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a simple Python-based Matrix chat client with two main components:
- **chatcli.py**: Main chat client for unencrypted Matrix messaging
- **get_token.py**: Utility to obtain Matrix access tokens via login

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
```bash
# Get access token
uv run matrix-token <homeserver> <username> [device_name]
# or: python get_token.py <homeserver> <username> [device_name]

# Run chat client
uv run matrix-chat <homeserver> <user_id> <access_token> <device_id>
# or: python chatcli.py <homeserver> <user_id> <access_token> <device_id>
```

### Console Scripts (via pyproject.toml)
After running `uv sync`, you can use:
```bash
uv run matrix-token   # equivalent to python get_token.py
uv run matrix-chat    # equivalent to python chatcli.py
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
1. Running `uv run matrix-token` to authenticate
2. Running `uv run matrix-chat` with obtained credentials  
3. Testing room join/switch/messaging functionality

No linting or type checking commands are defined in the current setup.