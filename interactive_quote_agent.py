#!/usr/bin/env python3
"""
Interactive SmolAgents quote bot that responds to user requests in Matrix.

This advanced example demonstrates:
1. Interactive messaging with wait_for_response via MCP stdio protocol
2. Different types of quotes based on user mood/request
3. Room management and user interaction

SETUP REQUIREMENTS:
1. Install this package to get the matrix-mcp-server console script:
   uv tool install . 
   (or: uv pip install -e . in your environment)

2. Set environment variables for the MCP server:
   export MATRIX_USERNAME="your-bot@matrix.org"
   export MATRIX_PASSWORD="your-password"
   export MATRIX_ROOMID="#test:matrix.org" 
   export MATRIX_HOMESERVER="https://matrix.org"  # optional
   export MATRIX_DEVICE_NAME="interactive-quote-bot"  # optional

HOW IT WORKS:
- ToolCollection.from_mcp("matrix-mcp-server") spawns the MCP server as subprocess
- SmolAgents communicates with matrix_mcp_server.py via stdin/stdout (stdio MCP)
- The MCP server handles Matrix authentication, room joining, and message handling
- wait_for_response tool sends a message then waits for human responses in Matrix
"""

import random
import argparse
from smolagents import CodeAgent, InferenceClientModel, ToolCollection
from mcp import StdioServerParameters

# Categorized quotes for different moods/requests
QUOTES_BY_CATEGORY = {
    "motivation": [
        "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
        "The way to get started is to quit talking and begin doing. - Walt Disney",
        "Don't be afraid to give up the good to go for the great. - John D. Rockefeller",
        "Innovation distinguishes between a leader and a follower. - Steve Jobs",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt"
    ],
    "wisdom": [
        "The only true wisdom is in knowing you know nothing. - Socrates",
        "Life is what happens to you while you're busy making other plans. - John Lennon",
        "In the middle of difficulty lies opportunity. - Albert Einstein",
        "It does not matter how slowly you go as long as you do not stop. - Confucius",
        "The journey of a thousand miles begins with one step. - Lao Tzu"
    ],
    "creativity": [
        "Creativity is intelligence having fun. - Albert Einstein",
        "The secret to creativity is knowing how to hide your sources. - Pablo Picasso",
        "You can't use up creativity. The more you use, the more you have. - Maya Angelou",
        "Creativity takes courage. - Henri Matisse",
        "Logic will get you from A to B. Imagination will take you everywhere. - Albert Einstein"
    ],
    "perseverance": [
        "It is during our darkest moments that we must focus to see the light. - Aristotle",
        "Fall seven times, stand up eight. - Japanese Proverb",
        "You learn more from failure than from success. Don't let it stop you. - Unknown",
        "Success is walking from failure to failure with no loss of enthusiasm. - Winston Churchill",
        "The only impossible journey is the one you never begin. - Tony Robbins"
    ]
}

def get_quote_by_category(category="random"):
    """Get a quote from a specific category or random."""
    if category == "random" or category not in QUOTES_BY_CATEGORY:
        # Pick a random category and quote
        category = random.choice(list(QUOTES_BY_CATEGORY.keys()))
        quote = random.choice(QUOTES_BY_CATEGORY[category])
        return quote, category
    else:
        quote = random.choice(QUOTES_BY_CATEGORY[category])
        return quote, category

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Interactive Matrix quote bot - provides inspirational quotes via Matrix chat"
    )
    parser.add_argument(
        "--oneshot", 
        action="store_true",
        help="Run in oneshot mode: ask for quote type, send one quote, then exit"
    )
    parser.add_argument(
        "--category",
        choices=["motivation", "wisdom", "creativity", "perseverance", "random"],
        help="In oneshot mode, specify quote category directly (skips user prompt)"
    )
    return parser.parse_args()


def main():
    """Main interactive quote bot function."""
    args = parse_arguments()
    
    if args.oneshot:
        print("🤖 Starting Quote Agent (Oneshot Mode)...")
        if args.category:
            print(f"Will send a {args.category} quote and exit.")
        else:
            print("Will ask for quote type, send one quote, then exit.")
    else:
        print("🤖 Starting Interactive Quote Agent...")
        print("This agent will interact with users in Matrix and provide quotes on demand.")
    
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
            print("   (matrix-mcp-server subprocess started for interactive session)")
            print(f"   Available tools: {[tool.name for tool in matrix_tools]}")
            
            # Create the agent
            agent = CodeAgent(
                tools=matrix_tools,
                model=model,
                stream_outputs=True
            )
            
            # Run the appropriate session mode within the context manager
            if args.oneshot:
                run_oneshot_session(agent, args.category)
            else:
                run_interactive_session(agent)
            
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


def run_oneshot_session(agent, category=None):
    """Run a single quote interaction and exit."""
    bot_name = "QuoteBot"
    
    print("🚀 Starting oneshot session in configured Matrix room")
    
    if category:
        # Direct category specified - send quote immediately
        quote, actual_category = get_quote_by_category(category)
        print(f"📝 Selected {actual_category} quote: {quote}")
        
        oneshot_task = f"""
        Send this {actual_category} quote to the Matrix room with nice formatting and an emoji:
        
        "{quote}"
        
        Introduce yourself briefly as {bot_name} and mention this is a {actual_category} quote.
        
        IMPORTANT: Use only keyword arguments:
        - Use: send_message(message="your formatted quote message")
        """
        
        try:
            print("📤 Sending quote...")
            result = agent.run(oneshot_task)
            print("✅ Quote sent successfully!")
            print("👋 Oneshot session complete.")
        except Exception as e:
            print(f"❌ Failed to send quote: {e}")
    
    else:
        # Ask user for category preference
        request_task = f"""
        Send a brief greeting as {bot_name} asking what type of quote they'd like:
        
        "Hi! I'm {bot_name}. What type of quote would you like?
        - motivation
        - wisdom  
        - creativity
        - perseverance
        - random"
        
        Then wait for their response for up to 60 seconds.
        
        IMPORTANT: Use only keyword arguments:
        - Use: send_message(message="your greeting")
        - Use: wait_for_response(message="What type of quote?", timeout_seconds=60)
        """
        
        try:
            print("📢 Asking for quote preference...")
            result = agent.run(request_task)
            print(f"Response received: {result}")
            
            # Parse the response to determine category 
            # The response format is: "Received response from @user:server.com: actual_message"
            response_lower = result.lower()
            
            # Extract the actual message part (after the last ": ")
            if ": " in result:
                actual_message = result.split(": ", 1)[1].lower()
            else:
                actual_message = response_lower
            
            print(f"🔍 Parsing user response: '{actual_message}'")
            
            # Determine category from the actual message
            if "motivat" in actual_message:
                chosen_category = "motivation"
            elif "wisdom" in actual_message or "wise" in actual_message:
                chosen_category = "wisdom"
            elif "creativ" in actual_message:
                chosen_category = "creativity"
            elif "persever" in actual_message:
                chosen_category = "perseverance"
            else:
                chosen_category = "random"
            
            print(f"📋 Determined category: {chosen_category}")
            
            # Send the appropriate quote
            quote, actual_category = get_quote_by_category(chosen_category)
            print(f"📝 Selected {actual_category} quote: {quote}")
            
            quote_task = f"""
            Send this {actual_category} quote with nice formatting and an emoji:
            
            "{quote}"
            
            IMPORTANT: Use only keyword arguments:
            - Use: send_message(message="your formatted quote message")
            """
            
            result = agent.run(quote_task)
            print("✅ Quote sent successfully!")
            print("👋 Oneshot session complete.")
            
        except Exception as e:
            print(f"❌ Oneshot session failed: {e}")


def run_interactive_session(agent):
    """Run the interactive quote session with the given agent."""
    # Configuration
    bot_name = "QuoteBot"
    
    print("🚀 Starting interactive session in configured Matrix room")
    
    # Send initial greeting and wait for user interaction
    greeting_task = f"""
    Send a friendly greeting message introducing yourself as {bot_name}.
    
    Tell users they can ask for quotes by category:
    - "motivation" for motivational quotes
    - "wisdom" for wisdom quotes  
    - "creativity" for creativity quotes
    - "perseverance" for perseverance quotes
    - "random" for any random quote
    
    IMPORTANT: Use only keyword arguments with the tools:
    - Use: send_message(message="your greeting text")
    - Use: wait_for_response(message="Ready for requests!", timeout_seconds=300)
    
    Then wait for a user response for up to 300 seconds (5 minutes).
    """
    
    try:
        print("📢 Sending greeting and waiting for user interaction...")
        result = agent.run(greeting_task)
        print(f"Bot interaction result: {result}")
        
        # Continue the conversation loop
        conversation_active = True
        while conversation_active:
            print("\n🔄 Waiting for next user request...")
            
            # Wait for user request
            wait_task = f"""
            Wait for a user message for up to 180 seconds (3 minutes).
            When you receive a message, analyze what type of quote they want:
            - If they mention motivation, motivational, inspire, etc. → category: "motivation"
            - If they mention wisdom, wise, philosophy, etc. → category: "wisdom"  
            - If they mention creativity, creative, art, etc. → category: "creativity"
            - If they mention perseverance, persistence, overcome, etc. → category: "perseverance"
            - Otherwise → category: "random"
            
            Then respond with an appropriate quote from that category with a nice emoji and formatting.
            
            IMPORTANT: Use only keyword arguments:
            - Use: wait_for_response(message="Waiting for your request...", timeout_seconds=180)
            - Use: send_message(message="your quote response")
            """
            
            try:
                result = agent.run(wait_task)
                print(f"✅ Handled user request: {result}")
                
                # Ask if we should continue (simple demonstration)
                print("\n🤔 Continue waiting for more requests? (Enter 'q' to quit, any other key to continue)")
                user_input = input().strip().lower()
                if user_input == 'q':
                    conversation_active = False
                    
            except Exception as e:
                print(f"⏰ No user interaction or error: {e}")
                print("🔄 Continuing to wait for requests...")
                continue
        
        # Send goodbye message
        goodbye_task = f"""
        Send a friendly goodbye message as {bot_name}.
        Thank users for the interaction and let them know they can call you again anytime.
        """
        
        agent.run(goodbye_task)
        print("👋 Sent goodbye message. Session ended.")
        
    except Exception as e:
        print(f"❌ Session error: {e}")

if __name__ == "__main__":
    main()