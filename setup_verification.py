#!/usr/bin/env python3
"""
Setup verification script for Matrix MCP SmolAgents integration.

This script helps verify that your environment is properly configured
to run the SmolAgents examples with matrix-mcp-server.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_environment_variables():
    """Check if required environment variables are set."""
    print("🔍 Checking environment variables...")
    
    required_vars = ["MATRIX_USERNAME", "MATRIX_PASSWORD", "MATRIX_ROOMID"]
    optional_vars = ["MATRIX_HOMESERVER", "MATRIX_DEVICE_NAME"]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print passwords
            display_value = "***" if "PASSWORD" in var else value
            print(f"  ✅ {var}={display_value}")
        else:
            print(f"  ❌ {var} not set")
            missing_vars.append(var)
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}={value}")
        else:
            default = "https://matrix.org" if var == "MATRIX_HOMESERVER" else "mcp-server"
            print(f"  ⚠️  {var} not set (will use default: {default})")
    
    return missing_vars

def check_command_availability():
    """Check if matrix-mcp-server command is available."""
    print("\n🔍 Checking command availability...")
    
    try:
        result = subprocess.run(
            ["which", "matrix-mcp-server"], 
            capture_output=True, 
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"  ✅ matrix-mcp-server found at: {result.stdout.strip()}")
            return True
        else:
            print("  ❌ matrix-mcp-server command not found")
            return False
    except subprocess.TimeoutExpired:
        print("  ❌ Command check timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error checking command: {e}")
        return False

def check_mcp_server_startup():
    """Test if matrix-mcp-server can start successfully."""
    print("\n🔍 Testing MCP server startup...")
    
    try:
        # Start the server process
        process = subprocess.Popen(
            ["matrix-mcp-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        import time
        time.sleep(2)
        
        # Check if it's still running
        if process.poll() is None:
            print("  ✅ matrix-mcp-server started successfully")
            # Terminate the test server
            process.terminate()
            process.wait(timeout=5)
            return True
        else:
            stdout, stderr = process.communicate()
            print("  ❌ matrix-mcp-server failed to start")
            if stderr:
                print(f"     Error: {stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ MCP server startup timed out")
        process.kill()
        return False
    except FileNotFoundError:
        print("  ❌ matrix-mcp-server command not found")
        return False
    except Exception as e:
        print(f"  ❌ Error testing server startup: {e}")
        return False

def check_smolagents_installation():
    """Check if smolagents is installed."""
    print("\n🔍 Checking SmolAgents installation...")
    
    try:
        import smolagents
        print(f"  ✅ smolagents installed (version: {smolagents.__version__})")
        return True
    except ImportError:
        print("  ❌ smolagents not installed")
        print("     Install with: pip install smolagents")
        return False
    except Exception as e:
        print(f"  ❌ Error checking smolagents: {e}")
        return False

def print_setup_instructions():
    """Print setup instructions."""
    print("\n📋 Setup Instructions:")
    print("1. Install this package:")
    print("   uv tool install .")
    print("   # or: uv pip install -e . (in your environment)")
    print()
    print("2. Install SmolAgents:")
    print("   pip install smolagents")
    print()
    print("3. Set environment variables:")
    print("   export MATRIX_USERNAME=\"your-bot@matrix.org\"")
    print("   export MATRIX_PASSWORD=\"your-password\"")
    print("   export MATRIX_ROOMID=\"#test:matrix.org\"")
    print("   export MATRIX_HOMESERVER=\"https://matrix.org\"  # optional")
    print("   export MATRIX_DEVICE_NAME=\"quote-bot\"          # optional")
    print()
    print("4. Test the MCP server:")
    print("   matrix-mcp-server")
    print("   (Ctrl+C to exit)")
    print()
    print("5. Run the SmolAgents examples:")
    print("   python quote_agent_example.py")
    print("   python interactive_quote_agent.py")

def main():
    """Main verification function."""
    print("🤖 Matrix MCP SmolAgents Setup Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check environment variables
    missing_vars = check_environment_variables()
    if missing_vars:
        all_good = False
    
    # Check SmolAgents
    if not check_smolagents_installation():
        all_good = False
    
    # Check command availability
    if not check_command_availability():
        all_good = False
    
    # Test server startup (only if command exists and env vars are set)
    if not missing_vars and check_command_availability():
        if not check_mcp_server_startup():
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 Setup verification complete! Everything looks good.")
        print("You can now run the SmolAgents examples:")
        print("  python quote_agent_example.py")
        print("  python interactive_quote_agent.py")
    else:
        print("❌ Setup verification found issues.")
        print_setup_instructions()
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())