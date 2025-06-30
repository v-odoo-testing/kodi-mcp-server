#!/usr/bin/env python3
"""
Test script to call Kodi MCP server directly
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path

async def test_kodi_mcp():
    """Test the Kodi MCP server directly."""
    
    # Path to the server
    server_path = Path(__file__).parent / "src" / "server.py"
    venv_python = Path(__file__).parent / "venv" / "bin" / "python"
    
    # Start the server process
    process = await asyncio.create_subprocess_exec(
        str(venv_python), str(server_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={
            "KODI_HOST": "192.168.1.71",
            "KODI_PORT": "8080", 
            "KODI_USERNAME": "kodi",
            "KODI_PASSWORD": "kodi"
        }
    )
    
    try:
        # Initialize the server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialization...")
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read initialization response
        init_response = await process.stdout.readline()
        print(f"Init response: {init_response.decode().strip()}")
        
        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write((json.dumps(initialized_notif) + "\n").encode())
        await process.stdin.drain()
        
        # Now test the play_episode tool
        play_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "play_episode",
                "arguments": {
                    "show_title": "Murderbot",
                    "season": 1,
                    "episode": 4
                }
            }
        }
        
        print("Sending play episode request...")
        process.stdin.write((json.dumps(play_request) + "\n").encode())
        await process.stdin.drain()
        
        # Read response
        play_response = await process.stdout.readline()
        print(f"Play response: {play_response.decode().strip()}")
        
        # Close stdin to signal end
        process.stdin.close()
        
        # Wait for process to complete
        await process.wait()
        
    except Exception as e:
        print(f"Error: {e}")
        process.terminate()
        await process.wait()

if __name__ == "__main__":
    asyncio.run(test_kodi_mcp())
