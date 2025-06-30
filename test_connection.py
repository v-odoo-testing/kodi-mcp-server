#!/usr/bin/env python3
"""
Kodi Connection Test Utility

Test connection to Kodi server before running the MCP server.
"""

import asyncio
import json
import sys
from typing import Dict, Any

import httpx


async def test_kodi_connection(
    host: str = "192.168.1.71",
    port: int = 8080,
    username: str = "kodi", 
    password: str = "kodi",
    use_https: bool = False,
    timeout: int = 10,
    socks5_proxy: str = None
) -> bool:
    """Test connection to Kodi server."""
    protocol = "https" if use_https else "http"
    base_url = f"{protocol}://{host}:{port}/jsonrpc"
    
    # Create auth tuple if credentials provided
    auth = None
    if username and password:
        auth = (username, password)
    
    # Test payload
    payload = {
        "jsonrpc": "2.0",
        "method": "JSONRPC.Ping",
        "id": 1
    }
    
    try:
        proxies = None
        if socks5_proxy:
            proxies = {"all://": socks5_proxy}
        
        print(f"Testing connection to Kodi at {base_url}")
        if proxies:
            print(f"Using SOCKS5 proxy: {socks5_proxy}")
        
        async with httpx.AsyncClient(timeout=timeout, proxies=proxies) as client:
            response = await client.post(
                base_url,
                json=payload,
                auth=auth
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "result" in data and data["result"] == "pong":
                print("✅ Connection successful!")
                
                # Test getting library stats
                stats_payload = {
                    "jsonrpc": "2.0",
                    "method": "VideoLibrary.GetMovies",
                    "params": {"limits": {"end": 1}},
                    "id": 2
                }
                
                stats_response = await client.post(
                    base_url,
                    json=stats_payload,
                    auth=auth
                )
                stats_data = stats_response.json()
                
                if "result" in stats_data:
                    limits = stats_data["result"].get("limits", {})
                    total_movies = limits.get("total", 0)
                    print(f"📊 Found {total_movies} movies in library")
                
                return True
            else:
                print("❌ Unexpected response from Kodi")
                return False
                
    except httpx.TimeoutException:
        print("❌ Connection timeout")
        return False
    except httpx.ConnectError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Main entry point."""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Test Kodi connection")
    parser.add_argument("--host", default=os.getenv("KODI_HOST", "192.168.1.71"))
    parser.add_argument("--port", type=int, default=int(os.getenv("KODI_PORT", "8080")))
    parser.add_argument("--username", default=os.getenv("KODI_USERNAME", "kodi"))
    parser.add_argument("--password", default=os.getenv("KODI_PASSWORD", "kodi"))
    parser.add_argument("--https", action="store_true", help="Use HTTPS")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--socks5", help="SOCKS5 proxy URL (e.g., socks5://localhost:1080)")
    
    args = parser.parse_args()
    
    # Check for SOCKS5 proxy from environment
    socks5_proxy = args.socks5
    if not socks5_proxy:
        socks5_host = os.getenv("SOCKS5_HOST")
        if socks5_host:
            socks5_port = os.getenv("SOCKS5_PORT", "1080")
            socks5_username = os.getenv("SOCKS5_USERNAME")
            socks5_password = os.getenv("SOCKS5_PASSWORD")
            
            if socks5_username and socks5_password:
                socks5_proxy = f"socks5://{socks5_username}:{socks5_password}@{socks5_host}:{socks5_port}"
            else:
                socks5_proxy = f"socks5://{socks5_host}:{socks5_port}"
    
    success = await test_kodi_connection(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        use_https=args.https,
        timeout=args.timeout,
        socks5_proxy=socks5_proxy
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
