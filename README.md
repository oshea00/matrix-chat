# Matrix Chat CLI

Simple command-line Matrix chat client with token authentication utility.

## Files

- `chatcli.py` - Main chat client for unencrypted Matrix messaging
- `get_token.py` - Utility to obtain Matrix access tokens
- `pyproject.toml` - Project configuration and dependencies

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and packaging.

### Setup Development Environment

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync

# Install in editable mode for development
uv pip install -e .
```

### Running Tools

You can run the tools directly with uv:

```bash
# Get access token
uv run matrix-token <homeserver> <username> [device_name]
# Example: uv run matrix-token https://matrix.org @user:matrix.org myclient

# Run chat client
uv run matrix-chat <homeserver> <user_id> <access_token> <device_id>
# Example: uv run matrix-chat https://matrix.org @user:matrix.org token123 DEVICE456
```

Or activate the virtual environment and use the installed console scripts:

```bash
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

matrix-token <homeserver> <username> [device_name]
matrix-chat <homeserver> <user_id> <access_token> <device_id>
```

### Adding Dependencies

```bash
# Add runtime dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>
```

### Testing

This project currently relies on manual testing. To test the functionality:

1. **Get a token:**
   ```bash
   uv run matrix-token https://matrix.org your_username
   ```

2. **Test the chat client:**
   ```bash
   uv run matrix-chat https://matrix.org @your_user:matrix.org your_token your_device_id
   ```

3. **Test basic functionality:**
   - Join a room: `/join #test:matrix.org`
   - Send messages
   - Switch rooms: `/switch #another:matrix.org`
   - List rooms: `/rooms`

### Building and Packaging

```bash
# Build the package
uv build

# Install from built package
uv pip install dist/matrix_chat-1.0.0-py3-none-any.whl
```

## Installation and Usage

### Global Installation (Recommended)

Install the tools globally using uv:
```bash
uv tool install .
```

Then use the commands directly:
```bash
# Get access token
matrix-token <homeserver> <username> [device_name]
# Example: matrix-token https://matrix.org @user:matrix.org myclient

# Run chat client  
matrix-chat <homeserver> <user_id> <access_token> <device_id>
# Example: matrix-chat https://matrix.org @user:matrix.org token123 DEVICE456
```

### Local Development Usage

For development or one-time usage:
```bash
# Get access token
uv run matrix-token <homeserver> <username> [device_name]
# Example: uv run matrix-token https://matrix.org @user:matrix.org myclient

# Run chat client
uv run matrix-chat <homeserver> <user_id> <access_token> <device_id>
# Example: uv run matrix-chat https://matrix.org @user:matrix.org token123 DEVICE456
```

## Commands

- `/help` - Show available commands
- `/join <room>` - Join a room
- `/switch <room>` - Switch to different room
- `/rooms` - List joined rooms
- `/quit` - Exit client

## Features

- Unencrypted messaging only (simple and reliable)
- Room joining and switching
- Real-time message display
- Automatic room name resolution