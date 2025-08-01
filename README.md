# Matrix Chat CLI & MCP Server

Simple command-line Matrix chat client with integrated authentication, plus an MCP server for AI agent integration.

## Matrix Chat Client Features

- **Integrated authentication**: No separate token generation step required
- **Secure password handling**: Password prompted securely by default
- **Automatic token refresh**: Handles expired tokens transparently
- **Unencrypted messaging**: Simple and reliable (by design)
- **Room management**: Join, switch, and list rooms with alias support
- **Real-time messaging**: Live message display with room context
- **Command-line friendly**: Clear argument structure with help system## Components

### Matrix Chat Client
- `chatcli.py` - Interactive chat client for unencrypted Matrix messaging
- Console command: `matrix-chat`

### MCP Server for AI Agents  
- `matrix_mcp_server.py` - MCP server exposing Matrix messaging tools for AI agents
- Console command: `matrix-mcp-server`
- Design document: `MCPDESIGN.md`

### Configuration
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

## MCP Server for AI Agents

The MCP server (`matrix-mcp-server`) exposes Matrix messaging capabilities as tools for AI agents like HuggingFace SmolAgents.

### MCP Tools Available

- **`send_message`** - Send messages to Matrix rooms
- **`wait_for_response`** - Send message and wait for human response (with timeout)
- **`list_rooms`** - List joined Matrix rooms with names and aliases

### Running the MCP Server

#### Environment Setup
```bash
# Required environment variables
export MATRIX_USERNAME="your-bot@matrix.org"
export MATRIX_PASSWORD="your-password"
export MATRIX_ROOMID="#room:matrix.org"

# Optional environment variables
export MATRIX_HOMESERVER="https://matrix.org"  # default
export MATRIX_DEVICE_NAME="mcp-server"        # default
```

#### Starting the Server
```bash
# Global installation
uv tool install .
matrix-mcp-server

# Local development
uv run matrix-mcp-server
```

### SmolAgents Integration

```python
from smolagents import CodeAgent, InferenceClientModel, ToolCollection

# Load Matrix MCP tools
model = InferenceClientModel()
matrix_tools = ToolCollection.from_mcp("matrix-mcp-server")

agent = CodeAgent(tools=matrix_tools, model=model)

# Agent can now send Matrix messages
result = agent.run("Send a status update to #ops room when analysis is complete")
```

### MCP Usage Examples

#### Agent Notifications
```python
# Agent sends completion notification
send_message(
    room_id="#ops:company.com", 
    message="🤖 Data analysis completed successfully!"
)
```

#### Interactive Approval Workflows  
```python
# Agent requests approval and waits for response
response = wait_for_response(
    room_id="#approvals:company.com",
    message="🤖 Ready to deploy to production. Reply 'approve' to proceed.",
    timeout_seconds=600,
    response_from="@admin:company.com"
)
```

## Testing the MCP Server

### MCP Inspector - Interactive Testing

The MCP Inspector provides a web-based interface to test your Matrix messaging tools interactively.

#### Starting the MCP Development Environment

1. **Set your environment variables:**
   ```bash
   export MATRIX_USERNAME="your-bot@matrix.org"
   export MATRIX_PASSWORD="your-password"
   export MATRIX_ROOMID="#test:matrix.org"
   ```

2. **Start the MCP development server:**
   ```bash
   mcp dev matrix_mcp_server.py
   ```

   You'll see output like this:

   ![Starting MCP Dev Server](images/startmcpdev.png)

   The server will:
   - Start the MCP Inspector on localhost:6274
   - Provide a session token for authentication
   - Automatically open your browser to the inspector

#### Using the MCP Inspector

The web interface shows all available tools and lets you test them interactively:

![MCP Inspector Interface](images/mcpinspector.png)

**Available tools:**
- **send_message** - Send messages to Matrix rooms
- **wait_for_response** - Send message and wait for human response  
- **list_rooms** - List joined Matrix rooms

**Testing send_message:**
1. Select the `send_message` tool
2. Fill in the room ID (e.g., `#clearchat:matrix.org`) 
3. Enter your message text
4. Click "Run Tool"

#### Real-time Matrix Integration

Messages sent via the MCP tools appear instantly in Matrix clients:

![Matrix Mobile Response](images/mcpscreenchat.png)

The screenshots show:
- MCP server sending "Hello from MCP" to the #clearchat room
- Message appearing immediately in Element mobile app
- Two-way communication working (human reply: "Hi back")

![Matrix Chat List](images/mcpresponse.png)

The message appears in the Matrix chat list showing successful integration.

#### Interactive Response Testing

Test the `wait_for_response` tool:
1. Send a message that asks for input
2. The tool waits for a human response in Matrix
3. Returns the response content to your agent

This enables approval workflows and human-in-the-loop AI systems.

## SmolAgents Examples

The project includes two example SmolAgents scripts that demonstrate Matrix messaging integration:

### Setup Requirements

1. **Install the package:**
   ```bash
   uv tool install .
   ```

2. **Install SmolAgents:**
   ```bash
   pip install smolagents
   ```

3. **Set environment variables:**
   ```bash
   export MATRIX_USERNAME="your-bot@matrix.org"
   export MATRIX_PASSWORD="your-password"
   export MATRIX_ROOMID="#test:matrix.org"
   ```

4. **Verify setup:**
   ```bash
   python setup_verification.py
   ```

### Example Scripts

#### Simple Quote Agent (`quote_agent_example.py`)

Sends a single random inspirational quote to Matrix and exits:

```bash
python quote_agent_example.py
```

**Features:**
- Selects a random inspirational quote
- Sends it to the configured Matrix room
- Formats with emojis for engagement
- Exits gracefully after sending

#### Interactive Quote Bot (`interactive_quote_agent.py`)

A more advanced bot that can run in different modes:

**1. Interactive Mode (default):**
```bash
python interactive_quote_agent.py
```
- Runs continuously, waiting for user requests
- Responds to different quote categories (motivation, wisdom, creativity, etc.)
- Loops indefinitely until manually stopped

**2. Oneshot Mode - Ask for Category:**
```bash
python interactive_quote_agent.py --oneshot
```
- Asks user what type of quote they want
- Sends one quote based on their response
- Exits gracefully

**3. Oneshot Mode - Direct Category:**
```bash
python interactive_quote_agent.py --oneshot --category motivation
python interactive_quote_agent.py --oneshot --category wisdom
python interactive_quote_agent.py --oneshot --category creativity
python interactive_quote_agent.py --oneshot --category perseverance
python interactive_quote_agent.py --oneshot --category random
```
- Sends a quote from the specified category immediately
- No user interaction required
- Perfect for automation and scheduled tasks

### Real-world Usage

The interactive quote bot works seamlessly across Matrix clients:

![Interactive Quote Bot on Mobile](images/interactivequote.png)

The screenshot shows:
- Bot greeting and category options
- User requesting a "random" quote
- Bot responding with a relevant, nicely formatted quote
- Natural conversation flow in Matrix mobile client

### Integration with Automation

The oneshot modes are perfect for:
- **Scheduled delivery**: Use cron jobs to send daily motivational quotes
- **Webhook integration**: Trigger quotes from other systems
- **CI/CD notifications**: Send team morale boosts after successful deployments
- **Slack replacement**: Automated team engagement via Matrix

**Example cron job for daily motivation:**
```bash
# Send a daily motivational quote at 9 AM
0 9 * * * /usr/bin/python3 /path/to/interactive_quote_agent.py --oneshot --category motivation
```

