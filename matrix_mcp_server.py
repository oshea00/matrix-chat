#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from mautrix.types import RoomID, UserID
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

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


class MatrixMCPServer:
    """MCP Server that exposes Matrix messaging tools"""
    
    def __init__(self):
        self.server = Server("matrix-mcp-server")
        self.client: Optional[SimpleChatClient] = None
        self.pending_responses: Dict[str, PendingResponse] = {}
        self._setup_tools()
        
    def _setup_tools(self):
        """Register MCP tools"""
        
        @self.server.list_tools()
        async def list_tools() -> List[types.Tool]:
            return [
                types.Tool(
                    name="send_message",
                    description="Send a message to a Matrix room",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "room_id": {
                                "type": "string",
                                "description": "Room ID or alias (e.g., #room:server.com)"
                            },
                            "message": {
                                "type": "string", 
                                "description": "Message text to send"
                            },
                            "join_if_needed": {
                                "type": "boolean",
                                "default": True,
                                "description": "Auto-join room if not already joined"
                            }
                        },
                        "required": ["room_id", "message"]
                    }
                ),
                types.Tool(
                    name="wait_for_response",
                    description="Send message and wait for human response in specified room",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "room_id": {
                                "type": "string",
                                "description": "Room ID or alias"
                            },
                            "message": {
                                "type": "string",
                                "description": "Message to send before waiting"
                            },
                            "timeout_seconds": {
                                "type": "number",
                                "default": 300,
                                "description": "Max wait time (default: 5 min)"
                            },
                            "response_from": {
                                "type": "string",
                                "description": "Optional: specific user ID to wait for"
                            }
                        },
                        "required": ["room_id", "message"]
                    }
                ),
                types.Tool(
                    name="list_rooms",
                    description="List joined Matrix rooms with names and aliases",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            try:
                if not self.client:
                    await self._initialize_client()
                    
                if name == "send_message":
                    return await self._send_message(arguments)
                elif name == "wait_for_response":
                    return await self._wait_for_response(arguments)
                elif name == "list_rooms":
                    return await self._list_rooms(arguments)
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Tool call error: {e}", exc_info=True)
                return [types.TextContent(
                    type="text", 
                    text=f"Error: {str(e)}"
                )]

    async def _initialize_client(self):
        """Initialize Matrix client from environment variables"""
        username = os.getenv("MATRIX_USERNAME")
        password = os.getenv("MATRIX_PASSWORD") 
        homeserver = os.getenv("MATRIX_HOMESERVER", "https://matrix.org")
        device_name = os.getenv("MATRIX_DEVICE_NAME", "mcp-server")
        
        if not username or not password:
            raise ValueError("MATRIX_USERNAME and MATRIX_PASSWORD environment variables required")
            
        self.client = SimpleChatClient(
            homeserver=homeserver,
            user_id=UserID(username),
            username=username,
            password=password,
            device_name=device_name
        )
        
        # Enhance message handler to handle pending responses
        original_handler = self.client._handle_message
        
        async def enhanced_message_handler(evt):
            await original_handler(evt)
            await self._check_pending_responses(evt)
            
        self.client._handle_message = enhanced_message_handler
        
        await self.client.authenticate()
        await self.client.start()
        
        # Give client time to sync
        await asyncio.sleep(2.0)
        self.client.initial_sync_complete = True
        
        logger.info(f"Matrix client initialized for {username}")

    async def _check_pending_responses(self, evt):
        """Check if message matches any pending response requests"""
        if evt.sender == self.client.user_id:
            return  # Ignore our own messages
            
        # Check each pending response
        for response_id, pending in list(self.pending_responses.items()):
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
            del self.pending_responses[response_id]
            break

    async def _send_message(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle send_message tool call"""
        room_id = args["room_id"]
        message = args["message"]
        join_if_needed = args.get("join_if_needed", True)
        
        try:
            # Convert to RoomID if needed
            if room_id.startswith('#'):
                from mautrix.types import RoomAlias
                alias = RoomAlias(room_id)
                resolve_result = await self.client.client.resolve_room_alias(alias)
                actual_room_id = resolve_result.room_id
            else:
                actual_room_id = RoomID(room_id)
            
            # Join room if needed
            if join_if_needed:
                joined_rooms = await self.client.client.get_joined_rooms()
                if actual_room_id not in joined_rooms:
                    await self.client.join_room(room_id)
            
            # Send message
            await self.client.send_message(message, actual_room_id)
            
            return [types.TextContent(
                type="text",
                text=f"Message sent to {room_id}: {message}"
            )]
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    async def _wait_for_response(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle wait_for_response tool call"""
        room_id = args["room_id"]
        message = args["message"]
        timeout_seconds = args.get("timeout_seconds", 300)
        response_from = args.get("response_from")
        
        try:
            # First send the message
            await self._send_message({
                "room_id": room_id,
                "message": message,
                "join_if_needed": True
            })
            
            # Convert to RoomID if needed
            if room_id.startswith('#'):
                from mautrix.types import RoomAlias
                alias = RoomAlias(room_id)
                resolve_result = await self.client.client.resolve_room_alias(alias)
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
            
            self.pending_responses[response_id] = pending
            
            try:
                # Wait for response
                response_data = await future
                
                return [types.TextContent(
                    type="text",
                    text=f"Received response from {response_data['sender']}: {response_data['message']}"
                )]
                
            except asyncio.TimeoutError as e:
                return [types.TextContent(
                    type="text",
                    text=f"Timeout: {str(e)}"
                )]
            finally:
                # Cleanup
                if response_id in self.pending_responses:
                    del self.pending_responses[response_id]
                if not timeout_task.done():
                    timeout_task.cancel()
                    
        except Exception as e:
            logger.error(f"Failed to wait for response: {e}")
            raise

    async def _list_rooms(self, args: Dict[str, Any]) -> List[types.TextContent]:
        """Handle list_rooms tool call"""
        try:
            rooms = await self.client.client.get_joined_rooms()
            room_list = []
            
            for room_id in rooms:
                try:
                    # Get room name
                    room_name = None
                    try:
                        from mautrix.types import EventType
                        room_state = await self.client.client.get_state(room_id, EventType.ROOM_NAME)
                        if room_state and hasattr(room_state, 'name'):
                            room_name = room_state.name
                    except Exception:
                        pass
                    
                    # Get canonical alias
                    room_alias = await self.client.get_room_canonical_alias(room_id)
                    
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
            
            return [types.TextContent(
                type="text",
                text=f"Joined rooms ({len(room_list)}):\n" + "\n".join(room_list)
            )]
            
        except Exception as e:
            logger.error(f"Failed to list rooms: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        if self.client:
            await self.client.stop()
        
        # Cancel any pending responses
        for pending in self.pending_responses.values():
            if not pending.future.done():
                pending.future.cancel()
            if pending.timeout_task and not pending.timeout_task.done():
                pending.timeout_task.cancel()
        
        self.pending_responses.clear()


async def main():
    """Main MCP server entry point"""
    mcp_server = MatrixMCPServer()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await mcp_server.server.run(
                read_stream,
                write_stream,
                mcp_server.server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    finally:
        await mcp_server.cleanup()


if __name__ == "__main__":
    asyncio.run(main())