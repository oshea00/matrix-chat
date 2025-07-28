# Matrix Chat CLI

Simple command-line Matrix chat client with integrated authentication.

## Files

- `chatcli.py` - Main chat client for unencrypted Matrix messaging with integrated authentication
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

### Running the Application

You can run the chat client directly with uv:

```bash
# Basic usage - password will be prompted securely (uses matrix.org by default)
uv run matrix-chat <username>
# Example: uv run matrix-chat poolagent

# With password on command line
uv run matrix-chat <username> --password <password>
# Example: uv run matrix-chat poolagent --password mypass

# With custom device name
uv run matrix-chat <username> --device-name <device_name>
# Example: uv run matrix-chat poolagent --device-name "laptop-client"

# All options combined
uv run matrix-chat <username> -p <password> -d <device_name>
# Example: uv run matrix-chat poolagent -p mypass -d "laptop-client"

# Custom homeserver
uv run matrix-chat <username> <homeserver>
# Example: uv run matrix-chat poolagent https://custom.matrix.server
```

Or activate the virtual environment and use the installed console script:

```bash
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows

matrix-chat <username>
matrix-chat <username> --password <password>
matrix-chat <username> --device-name <device_name>
matrix-chat <username> <homeserver>  # for custom homeserver
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

1. **Run the chat client:**
   ```bash
   uv run matrix-chat your_username
   # Password will be prompted securely (uses matrix.org by default)
   ```

2. **Test basic functionality:**
   - Join a room: `/join #test:matrix.org`
   - Send messages
   - Switch rooms: `/switch #another:matrix.org`
   - List rooms: `/rooms`
   - Get help: `/help`

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

Then use the command directly:
```bash
# Basic usage - password prompted securely (uses matrix.org by default)
matrix-chat <username>
# Example: matrix-chat poolagent

# With password on command line
matrix-chat <username> --password <password>
# Example: matrix-chat poolagent --password mypass

# With custom device name
matrix-chat <username> --device-name <device_name>
# Example: matrix-chat poolagent --device-name "laptop-client"

# Custom homeserver
matrix-chat <username> <homeserver>
# Example: matrix-chat poolagent https://custom.matrix.server
```

### Local Development Usage

For development or one-time usage:
```bash
# Basic usage - password prompted securely (uses matrix.org by default)
uv run matrix-chat <username>
# Example: uv run matrix-chat poolagent

# With options
uv run matrix-chat <username> --password <password> --device-name <device_name>
# Example: uv run matrix-chat poolagent --password mypass --device-name "dev-client"

# Custom homeserver
uv run matrix-chat <username> <homeserver>
# Example: uv run matrix-chat poolagent https://custom.matrix.server
```

## Command-Line Arguments

- `username`: Required. Matrix username (e.g., poolagent or @poolagent:matrix.org)
- `homeserver`: Optional. Matrix homeserver URL (default: https://matrix.org)
- `--password` / `-p`: Optional. Matrix password (if not provided, prompted securely)
- `--device-name` / `-d`: Optional. Device name for session (default: "chatcli")

Use `matrix-chat --help` to see all available options.

## Chat Commands

Once connected, use these commands in the chat interface:

- `/help` - Show available commands
- `/join <room>` - Join a room
- `/switch <room>` - Switch to different room
- `/rooms` - List joined rooms
- `/quit` - Exit client

## Features

- **Integrated authentication**: No separate token generation step required
- **Secure password handling**: Password prompted securely by default
- **Automatic token refresh**: Handles expired tokens transparently
- **Unencrypted messaging**: Simple and reliable (by design)
- **Room management**: Join, switch, and list rooms with alias support
- **Real-time messaging**: Live message display with room context
- **Command-line friendly**: Clear argument structure with help system