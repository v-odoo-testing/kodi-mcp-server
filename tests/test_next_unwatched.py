#!/usr/bin/env python3
"""
Test play_next_unwatched function
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path

async def test_next_unwatched():
    """Test the play_next_unwatched function."""
    
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
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        process.stdin.write((json.dumps(init_request) + "\n").encode())
        await process.stdin.drain()
        
        init_response = await process.stdout.readline()
        print(f"Init: {init_response.decode().strip()}")
        
        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write((json.dumps(initialized_notif) + "\n").encode())
        await process.stdin.drain()
        
        # Test play_next_unwatched
        play_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "play_next_unwatched",
                "arguments": {
                    "show_title": "Murderbot"
                }
            }
        }
        
        print("Finding and playing next unwatched Murderbot episode...")
        process.stdin.write((json.dumps(play_request) + "\n").encode())
        await process.stdin.drain()
        
        play_response = await process.stdout.readline()
        result = json.loads(play_response.decode().strip())
        
        if result.get("result", {}).get("content"):
            content = result["result"]["content"][0]["text"]
            print(f"Result: {content}")
        
        process.stdin.close()
        await process.wait()
        
    except Exception as e:
        print(f"Error: {e}")
        process.terminate()

if __name__ == "__main__":
    asyncio.run(test_next_unwatched())
