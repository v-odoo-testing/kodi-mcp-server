# Example Claude Desktop Configuration

To add the Kodi MCP Server to Claude Desktop, add this configuration to your Claude Desktop settings:

**Location of config file:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/claude/claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "kodi": {
      "command": "/FULL/PATH/TO/kodi-mcp-server/venv/bin/python",
      "args": ["/FULL/PATH/TO/kodi-mcp-server/src/server.py"],
      "env": {
        "KODI_HOST": "192.168.1.71",
        "KODI_PORT": "8080",
        "KODI_USERNAME": "kodi",
        "KODI_PASSWORD": "kodi",
        "KODI_TIMEOUT": "30",
        "USE_HTTPS": "false",
        "SOCKS5_HOST": "",
        "SOCKS5_PORT": "1080",
        "SOCKS5_USERNAME": "",
        "SOCKS5_PASSWORD": ""
      }
    }
  }
}
```

**Important Notes:**
1. Replace `/FULL/PATH/TO/` with the actual absolute path to your installation
2. For example: `/Users/yourname/git/kodi-mcp-server/venv/bin/python`
3. Update the Kodi connection details as needed
4. For SOCKS5 proxy access, set SOCKS5_HOST (e.g., "localhost" for SSH tunnel)
5. Restart Claude Desktop after adding the configuration

**Quick Path Setup:**
```bash
cd /path/to/kodi-mcp-server
echo "Full path: $(pwd)/venv/bin/python"
echo "Args path: $(pwd)/src/server.py"
```
