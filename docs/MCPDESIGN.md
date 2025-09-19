# MCP Server Design for Matrix Messaging

This document outlines the design for a stdio MCP server that exposes Matrix messaging tools using the existing Matrix chat client infrastructure.

## Architecture Overview

Create a stdio MCP server (`matrix_mcp_server.py`) that wraps the existing `SimpleChatClient` to expose Matrix messaging capabilities via MCP tools.

## Core MCP Tools

### 1. `send_message` Tool

```json
{
  "name": "send_message",
  "description": "Send a message to a Matrix room",
  "inputSchema": {
    "type": "object",
    "properties": {
      "room_id": {"type": "string", "description": "Room ID or alias (e.g., #room:server.com)"},
      "message": {"type": "string", "description": "Message text to send"},
      "join_if_needed": {"type": "boolean", "default": true, "description": "Auto-join room if not already joined"}
    },
    "required": ["room_id", "message"]
  }
}
```

### 2. `wait_for_response` Tool

```json
{
  "name": "wait_for_response", 
  "description": "Send message and wait for human response in specified room",
  "inputSchema": {
    "type": "object",
    "properties": {
      "room_id": {"type": "string", "description": "Room ID or alias"},
      "message": {"type": "string", "description": "Message to send before waiting"},
      "timeout_seconds": {"type": "number", "default": 300, "description": "Max wait time (default: 5 min)"},
      "response_from": {"type": "string", "description": "Optional: specific user ID to wait for"}
    },
    "required": ["room_id", "message"]
  }
}
```

### 3. `list_rooms` Tool

```json
{
  "name": "list_rooms",
  "description": "List joined Matrix rooms with names and aliases",
  "inputSchema": {"type": "object", "properties": {}}
}
```

## Key Implementation Details

### Matrix Client Integration

- **Reuse `SimpleChatClient` class** from `chatcli.py:68-395`
- **Leverage existing authentication** (`authenticate()` at `chatcli.py:120`)
- **Use existing message sending** (`send_message()` at `chatcli.py:282`)
- **Extend message handling** (`_handle_message()` at `chatcli.py:206`)

### Response Waiting Mechanism

- Add message queue/event system to capture incoming messages
- Implement timeout handling with `asyncio.wait_for()`
- Filter responses by room and optionally by sender
- Return structured response with message content and metadata

### Configuration

Environment variables for Matrix credentials:
- `MATRIX_USERNAME`
- `MATRIX_PASSWORD` 
- `MATRIX_HOMESERVER` (default: https://matrix.org)
- `MATRIX_DEVICE_NAME` (default: "mcp-server")

### Error Handling

- **Authentication failures** → clear error messages
- **Room join failures** → attempt join with fallback
- **Network timeouts** → graceful retry logic
- **Token expiration** → automatic re-authentication (using `reauthenticate()` at `chatcli.py:153`)

## Usage Scenarios

### Agent Notification

```python
# Agent sends status update
send_message(room_id="#ops:company.com", message="🤖 Deployment completed successfully")
```

### Admin Approval

```python  
# Agent requests approval and waits
response = wait_for_response(
    room_id="#approvals:company.com",
    message="🤖 Request approval for database migration. Reply 'approve' or 'deny'",
    timeout_seconds=600,
    response_from="@admin:company.com"
)
```

## Implementation Files

- `matrix_mcp_server.py` - Main MCP server implementation
- `chatcli.py` - Existing Matrix client (reused)
- `pyproject.toml` - Add MCP server dependencies

## Dependencies

Additional dependencies needed:
- `mcp` - MCP server framework
- Existing dependencies from `pyproject.toml` (mautrix, aiohttp, etc.)

## SmolAgents Integration Example

Here's how a HuggingFace SmolAgents agent would use our Matrix MCP server:

```python
from smolagents import CodeAgent, InferenceClientModel, ToolCollection

# Initialize the agent with Matrix MCP tools
model = InferenceClientModel()
matrix_tools = ToolCollection.from_mcp("matrix_mcp_server.py")

agent = CodeAgent(
    tools=matrix_tools,
    model=model,
    stream_outputs=True
)

# Example: Agent processes a complex analysis and reports completion
result = agent.run("""
Analyze the quarterly sales data and provide insights on regional performance trends.
When you're done with your analysis, send a summary message to the #analytics room 
on Matrix to notify the team.
""")
```

The agent would generate code like:

```python
# Agent's generated code after completing analysis
sales_analysis = analyze_quarterly_data()
insights = generate_regional_insights(sales_analysis)

# Notify team via Matrix
send_message(
    room_id="#analytics:company.com",
    message=f"🤖 Quarterly analysis complete! Key insight: {insights['top_finding']}. Full report available in dashboard."
)
```

### Interactive Approval Workflow

```python
# Agent requests human approval before taking action
result = agent.run("""
Prepare a database migration script for the user table schema changes.
Before executing, send the migration plan to #database-ops room and wait for 
approval from the DBA team.
""")
```

Agent's generated code:
```python
migration_plan = prepare_migration_script("user_table_changes.sql")

# Request approval and wait for response
response = wait_for_response(
    room_id="#database-ops:company.com", 
    message=f"🤖 Ready to execute migration:\n```sql\n{migration_plan}\n```\nReply 'approve' to proceed or 'deny' to cancel.",
    timeout_seconds=1800,  # 30 minutes
    response_from="@dba-team:company.com"
)

if "approve" in response.lower():
    execute_migration(migration_plan)
    send_message(room_id="#database-ops:company.com", message="✅ Migration completed successfully!")
else:
    send_message(room_id="#database-ops:company.com", message="❌ Migration cancelled per team decision.")
```

## Benefits

- **Leverages existing code** - Reuses proven Matrix client implementation
- **Clean MCP interface** - Standard tool definitions for agent integration
- **Flexible messaging** - Supports both fire-and-forget and interactive scenarios
- **Robust error handling** - Built on existing authentication and retry logic
- **Easy deployment** - Single stdio server for agent integration
- **SmolAgents compatible** - Works seamlessly with HuggingFace SmolAgents framework