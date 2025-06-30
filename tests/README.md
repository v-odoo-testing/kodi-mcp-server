# Kodi MCP Server Tests

This directory contains test scripts for direct MCP server testing.

## Test Scripts

- **`test_mcp.py`** - Basic episode playback test
- **`test_scan.py`** - TV show directory scanning test
- **`test_next_unwatched.py`** - Watch status and next unwatched episode test
- **`test_workflow.py`** - Complete scan + play workflow test

## Usage

All tests require the virtual environment to be activated:

```bash
cd ~/git/kodi-mcp-server
source venv/bin/activate
python tests/test_workflow.py
```

## Main Connection Test

For basic connection testing, use the main utility in the project root:

```bash
python test_connection.py
```

These tests bypass Claude Desktop and call the MCP server directly, which is useful for:
- Development and debugging
- Verifying server functionality
- Testing new features before Claude Desktop integration
