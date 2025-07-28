#!/usr/bin/env python3

import asyncio
import logging
import os
from typing import Any, Dict, Optional
from dataclasses import dataclass

from mautrix.types import RoomID, UserID
from mcp.server.fastmcp import FastMCP

from chatcli import SimpleChatClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("matrix_mcp_server")


@dataclass
class PendingResponse:
    """Tracks a pending response for wait_for_response tool"""
    room_id: RoomID
    response_from: Optional[str]
    future: asyncio.Future
    timeout_task: Optional[asyncio.Task] = None


# Global state for Matrix client and pending responses
matrix_client: Optional[SimpleChatClient] = None
pending_responses: Dict[str, PendingResponse] = {}

# Create FastMCP server
app = FastMCP("matrix-mcp-server")


async def initialize_client():
    """Initialize Matrix client from environment variables"""
    global matrix_client
    
    if matrix_client:
        return matrix_client
        
    username = os.getenv("MATRIX_USERNAME")
    password = os.getenv("MATRIX_PASSWORD") 
    homeserver = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
    device_name = os.getenv("MATRIX_DEVICE_NAME", "mcp-server")
    
    if not username or not password:
        raise ValueError("MATRIX_USERNAME and MATRIX_PASSWORD environment variables required")
        
    matrix_client = SimpleChatClient(
        homeserver=homeserver,
        user_id=UserID(username),
        username=username,
        password=password,
        device_name=device_name
    )
    
    # Enhance message handler to handle pending responses
    original_handler = matrix_client._handle_message
    
    async def enhanced_message_handler(evt):
        await original_handler(evt)
        await check_pending_responses(evt)
        
    matrix_client._handle_message = enhanced_message_handler
    
    await matrix_client.authenticate()
    await matrix_client.start()
    
    # Give client time to sync
    await asyncio.sleep(2.0)
    matrix_client.initial_sync_complete = True
    
    logger.info(f"Matrix client initialized for {username}")
    return matrix_client


async def check_pending_responses(evt):
    """Check if message matches any pending response requests"""
    global pending_responses
    
    if evt.sender == matrix_client.user_id:
        return  # Ignore our own messages
        
    # Check each pending response
    for response_id, pending in list(pending_responses.items()):
        if evt.room_id != pending.room_id:
            continue
            
        # Check if response is from specific user (if specified)
        if pending.response_from and str(evt.sender) != pending.response_from:
            continue
            
        # We have a match - resolve the future
        if not pending.future.done():
            response_data = {
                "message": evt.content.body,
                "sender": str(evt.sender),
                "room_id": str(evt.room_id),
                "timestamp": evt.timestamp
            }
            pending.future.set_result(response_data)
            
        # Cancel timeout task
        if pending.timeout_task and not pending.timeout_task.done():
            pending.timeout_task.cancel()
            
        # Remove from pending
        del pending_responses[response_id]
        break


@app.tool()
async def send_message(
    room_id: str,
    message: str,
    join_if_needed: bool = True
) -> str:
    """Send a message to a Matrix room.
    
    Args:
        room_id: Room ID or alias (e.g., #room:server.com)
        message: Message text to send
        join_if_needed: Auto-join room if not already joined
    """
    try:
        client = await initialize_client()
        
        # Convert to RoomID if needed
        if room_id.startswith('#'):
            from mautrix.types import RoomAlias
            alias = RoomAlias(room_id)
            resolve_result = await client.client.resolve_room_alias(alias)
            actual_room_id = resolve_result.room_id
        else:
            actual_room_id = RoomID(room_id)
        
        # Join room if needed
        if join_if_needed:
            joined_rooms = await client.client.get_joined_rooms()
            if actual_room_id not in joined_rooms:
                await client.join_room(room_id)
        
        # Send message
        await client.send_message(message, actual_room_id)
        
        return f"Message sent to {room_id}: {message}"
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return f"Error sending message: {str(e)}"


@app.tool()
async def wait_for_response(
    room_id: str,
    message: str,
    timeout_seconds: int = 300,
    response_from: Optional[str] = None
) -> str:
    """Send message and wait for human response in specified room.
    
    Args:
        room_id: Room ID or alias
        message: Message to send before waiting
        timeout_seconds: Max wait time (default: 5 min)
        response_from: Optional specific user ID to wait for
    """
    global pending_responses
    
    try:
        client = await initialize_client()
        
        # First send the message
        send_result = await send_message(room_id, message, join_if_needed=True)
        if send_result.startswith("Error"):
            return send_result
        
        # Convert to RoomID if needed
        if room_id.startswith('#'):
            from mautrix.types import RoomAlias
            alias = RoomAlias(room_id)
            resolve_result = await client.client.resolve_room_alias(alias)
            actual_room_id = resolve_result.room_id
        else:
            actual_room_id = RoomID(room_id)
        
        # Create pending response tracker
        response_id = f"{actual_room_id}:{asyncio.get_event_loop().time()}"
        future = asyncio.Future()
        
        # Create timeout task
        async def timeout_handler():
            await asyncio.sleep(timeout_seconds)
            if not future.done():
                future.set_exception(asyncio.TimeoutError(f"No response received within {timeout_seconds} seconds"))
        
        timeout_task = asyncio.create_task(timeout_handler())
        
        pending = PendingResponse(
            room_id=actual_room_id,
            response_from=response_from,
            future=future,
            timeout_task=timeout_task
        )
        
        pending_responses[response_id] = pending
        
        try:
            # Wait for response
            response_data = await future
            
            return f"Received response from {response_data['sender']}: {response_data['message']}"
            
        except asyncio.TimeoutError as e:
            return f"Timeout: {str(e)}"
        finally:
            # Cleanup
            if response_id in pending_responses:
                del pending_responses[response_id]
            if not timeout_task.done():
                timeout_task.cancel()
                
    except Exception as e:
        logger.error(f"Failed to wait for response: {e}")
        return f"Error waiting for response: {str(e)}"


@app.tool()
async def list_rooms() -> str:
    """List joined Matrix rooms with names and aliases."""
    try:
        client = await initialize_client()
        rooms = await client.client.get_joined_rooms()
        room_list = []
        
        for room_id in rooms:
            try:
                # Get room name
                room_name = None
                try:
                    from mautrix.types import EventType
                    room_state = await client.client.get_state(room_id, EventType.ROOM_NAME)
                    if room_state and hasattr(room_state, 'name'):
                        room_name = room_state.name
                except Exception:
                    pass
                
                # Get canonical alias
                room_alias = await client.get_room_canonical_alias(room_id)
                
                # Build display string
                display_parts = []
                if room_name:
                    display_parts.append(room_name)
                if room_alias:
                    display_parts.append(room_alias)
                
                if display_parts:
                    display_info = " | ".join(display_parts)
                    room_list.append(f"{room_id} ({display_info})")
                else:
                    room_list.append(str(room_id))
                    
            except Exception as e:
                logger.warning(f"Error processing room {room_id}: {e}")
                room_list.append(str(room_id))
        
        return f"Joined rooms ({len(room_list)}):\n" + "\n".join(room_list)
        
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}")
        return f"Error listing rooms: {str(e)}"


async def cleanup():
    """Cleanup resources"""
    global matrix_client, pending_responses
    
    if matrix_client:
        await matrix_client.stop()
    
    # Cancel any pending responses
    for pending in pending_responses.values():
        if not pending.future.done():
            pending.future.cancel()
        if pending.timeout_task and not pending.timeout_task.done():
            pending.timeout_task.cancel()
    
    pending_responses.clear()


# For MCP CLI compatibility
server = app
mcp = app


async def main():
    """Main MCP server entry point"""
    try:
        await app.run("stdio")
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    finally:
        await cleanup()


if __name__ == "__main__":
    asyncio.run(main())