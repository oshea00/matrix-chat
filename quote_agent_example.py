#!/usr/bin/env python3
"""
SmolAgents example script that generates random inspirational quotes
and sends them to Matrix rooms using the matrix-mcp-server.

This script demonstrates how to:
1. Use SmolAgents with Matrix MCP tools via stdio subprocess communication
2. Generate random quotes with an AI agent  
3. Send messages to Matrix rooms via MCP tools

SETUP REQUIREMENTS:
1. Install this package to get the matrix-mcp-server console script:
   uv tool install . 
   (or: uv pip install -e . in your environment)

2. Set environment variables for the MCP server:
   export MATRIX_USERNAME="your-bot@matrix.org"
   export MATRIX_PASSWORD="your-password"  
   export MATRIX_ROOMID="#test:matrix.org"
   export MATRIX_HOMESERVER="https://matrix.org"  # optional
   export MATRIX_DEVICE_NAME="quote-bot"          # optional

3. ToolCollection.from_mcp("matrix-mcp-server") will:
   - Spawn the "matrix-mcp-server" command as a subprocess
   - Communicate with it via stdin/stdout (stdio MCP protocol)
   - Load the available tools: send_message, wait_for_response, list_rooms
"""

import random
from smolagents import CodeAgent, InferenceClientModel, ToolCollection
from mcp import StdioServerParameters

# Collection of inspirational quotes for random selection
QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs", 
    "Life is what happens to you while you're busy making other plans. - John Lennon",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "The way to get started is to quit talking and begin doing. - Walt Disney",
    "Don't let yesterday take up too much of today. - Will Rogers",
    "You learn more from failure than from success. Don't let it stop you. Failure builds character. - Unknown",
    "If you are working on something that you really care about, you don't have to be pushed. The vision pulls you. - Steve Jobs",
    "People who are crazy enough to think they can change the world, are the ones who do. - Rob Siltanen"
]

def get_random_quote():
    """Select a random quote from the collection."""
    return random.choice(QUOTES)

def main():
    """Main function to run the quote-sending agent."""
    
    print("🤖 Starting Quote Agent...")
    print("This agent will generate a random inspirational quote and send it to Matrix.")
    
    # Initialize the language model
    model = InferenceClientModel()
    
    # Load Matrix MCP tools - this spawns matrix-mcp-server as subprocess
    # ToolCollection.from_mcp() returns a context manager
    try:
        import os
        server_params = StdioServerParameters(
            command="matrix-mcp-server",
            env=os.environ.copy()  # Pass environment variables to subprocess
        )
        with ToolCollection.from_mcp(server_params, trust_remote_code=True) as matrix_tool_collection:
            matrix_tools = matrix_tool_collection.tools
            print("✅ Successfully loaded Matrix MCP tools")
            print("   (matrix-mcp-server subprocess started and connected)")
            print(f"   Available tools: {[tool.name for tool in matrix_tools]}")
            
            # Create the agent with Matrix messaging capabilities
            agent = CodeAgent(
                tools=matrix_tools,
                model=model,
                stream_outputs=True
            )
            
            # Get a random quote
            quote = get_random_quote()
            print(f"📝 Selected quote: {quote}")
            
            # Have the agent send the quote to the configured Matrix room
            # The room is determined by the MATRIX_ROOMID environment variable
            
            task_prompt = f"""
            Send this inspirational quote to the Matrix room:
            
            "{quote}"
            
            Format it nicely with an emoji and make it look engaging for the chat room.
            Use the send_message tool without specifying room_id since it will use the default room.
            """
            
            print("🚀 Sending quote to configured Matrix room...")
            
            try:
                result = agent.run(task_prompt)
                print("✅ Quote sent successfully!")
                print(f"Agent result: {result}")
            except Exception as e:
                print(f"❌ Failed to send quote: {e}")
                
    except Exception as e:
        print(f"❌ Failed to load Matrix MCP tools: {e}")
        print("\nTroubleshooting:")
        print("1. Install the package: uv tool install . (or uv pip install -e .)")
        print("2. Verify matrix-mcp-server command exists: which matrix-mcp-server")
        print("3. Set environment variables:")
        print("   export MATRIX_USERNAME=\"your-bot@matrix.org\"")
        print("   export MATRIX_PASSWORD=\"your-password\"")
        print("   export MATRIX_ROOMID=\"#test:matrix.org\"")
        print("4. Test MCP server directly: matrix-mcp-server")
        return

if __name__ == "__main__":
    main()