#!/usr/bin/env python3
"""
Test complete workflow: scan Murderbot directory + play next unwatched
"""

import asyncio
import json
import sys
import subprocess
from pathlib import Path

async def test_complete_workflow():
    """Test scan + play next unwatched workflow."""
    
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
        print(f"🚀 Server v{json.loads(init_response.decode())['result']['serverInfo']['version']} initialized")
        
        # Send initialized notification
        initialized_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        process.stdin.write((json.dumps(initialized_notif) + "\n").encode())
        await process.stdin.drain()
        
        # Step 1: Scan Murderbot directory for new episodes
        scan_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "scan_tv_show",
                "arguments": {
                    "show_title": "Murderbot"
                }
            }
        }
        
        print("\n📁 Step 1: Scanning Murderbot directory for new episodes...")
        process.stdin.write((json.dumps(scan_request) + "\n").encode())
        await process.stdin.drain()
        
        scan_response = await process.stdout.readline()
        scan_result = json.loads(scan_response.decode().strip())
        
        if scan_result.get("result", {}).get("content"):
            content = scan_result["result"]["content"][0]["text"]
            print(f"📊 Scan result: {content}")
        
        # Wait a moment for scan to process
        await asyncio.sleep(2)
        
        # Step 2: Play next unwatched episode
        play_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "play_next_unwatched",
                "arguments": {
                    "show_title": "Murderbot"
                }
            }
        }
        
        print("\n🎬 Step 2: Finding and playing next unwatched episode...")
        process.stdin.write((json.dumps(play_request) + "\n").encode())
        await process.stdin.drain()
        
        play_response = await process.stdout.readline()
        play_result = json.loads(play_response.decode().strip())
        
        if play_result.get("result", {}).get("content"):
            content = play_result["result"]["content"][0]["text"]
            print(f"🎯 Play result: {content}")
        
        print("\n✅ Complete workflow successful!")
        
        process.stdin.close()
        await process.wait()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        process.terminate()

if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
