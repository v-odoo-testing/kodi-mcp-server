# Kodi MCP Server

A Model Context Protocol (MCP) server for interacting with Kodi media center. This server provides tools for querying media libraries, checking existing content, playing media, and managing Kodi remotely.

## Features

- **Library Search**: Search movies and TV shows by title, year, or genre
- **Content Verification**: Check if movies/episodes exist before downloading
- **Smart Playback Control**: Play movies/episodes and control playback
- **Watch Status Tracking**: **NEW v1.2.0** - Automatically track what you've watched and play next unwatched episodes
- **Targeted Library Scanning**: **NEW v1.2.0** - Scan specific TV show directories instead of entire library (fast!)
- **Library Management**: Get statistics, recent additions, and trigger scans
- **SOCKS5 Proxy Support**: Connect to remote Kodi instances through SSH tunnels
- **Fuzzy Matching**: Intelligent title matching for better search results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/v-odoo-testing/kodi-mcp-server.git
cd kodi-mcp-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Test the connection:
```bash
python test_connection.py --host 192.168.1.71 --username kodi --password kodi
```

## Configuration

Configure the server using environment variables:

### Basic Configuration
```bash
export KODI_HOST="192.168.1.71"
export KODI_PORT="8080"
export KODI_USERNAME="kodi"
export KODI_PASSWORD="kodi"
export KODI_TIMEOUT="30"
export USE_HTTPS="false"
```

### SOCKS5 Proxy (for remote access)
```bash
export SOCKS5_HOST="localhost"
export SOCKS5_PORT="1080"
export SOCKS5_USERNAME=""  # Optional
export SOCKS5_PASSWORD=""  # Optional
```

## Claude Desktop Integration

Add this configuration to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "kodi": {
      "command": "/path/to/kodi-mcp-server/venv/bin/python",
      "args": ["/path/to/kodi-mcp-server/src/server.py"],
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

## Available Tools

### Search Tools
- `search_movies` - Search movies by title, year, or genre
- `search_tv_shows` - Search TV shows by title or genre
- `check_movie_exists` - Quick check if a movie exists
- `check_tv_show_exists` - Check TV show/season/episode availability

### Playback Tools
- `play_movie` - Play a movie by title
- `play_episode` - Play a specific TV episode
- `play_next_unwatched` - **NEW v1.2.0** - Find and play the next unwatched episode automatically
- `control_playback` - Pause, stop, or get playback status

### Library Tools
- `get_library_stats` - Get library overview and statistics
- `get_recently_added` - List recently added content
- `update_library` - Trigger library scan (full library)
- `scan_tv_show` - **NEW v1.2.0** - Scan specific TV show directory only (fast, targeted)
- `get_episode_details` - **NEW v1.2.0** - Get detailed episode information with file paths

All tools support the `use_socks5` parameter for remote access.

## SOCKS5 Proxy Setup

For remote Kodi access through SSH:

1. **Create SSH tunnel:**
```bash
ssh -D 1080 -N user@remote-server
```

2. **Set environment variables:**
```bash
export SOCKS5_HOST="localhost"
export SOCKS5_PORT="1080"
```

3. **Use proxy in tool calls:**
```
User: "Search my remote Kodi for movies, use SOCKS5"
Assistant: Uses search_movies with use_socks5=true
```

## API Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KODI_HOST` | `192.168.1.71` | Kodi server IP address |
| `KODI_PORT` | `8080` | Kodi web interface port |
| `KODI_USERNAME` | `kodi` | Authentication username |
| `KODI_PASSWORD` | `kodi` | Authentication password |
| `KODI_TIMEOUT` | `30` | Request timeout in seconds |
| `USE_HTTPS` | `false` | Use HTTPS connection |
| `SOCKS5_HOST` | - | SOCKS5 proxy host |
| `SOCKS5_PORT` | `1080` | SOCKS5 proxy port |
| `SOCKS5_USERNAME` | - | SOCKS5 proxy username (optional) |
| `SOCKS5_PASSWORD` | - | SOCKS5 proxy password (optional) |

### Tool Parameters

#### search_movies
```json
{
  "title": "Movie title to search for",
  "year": 2023,
  "genre": "Action",
  "use_socks5": false
}
```

#### play_movie
```json
{
  "title": "The Matrix",
  "year": 1999,
  "use_socks5": false
}
```

#### play_episode
```json
{
  "show_title": "Breaking Bad",
  "season": 1,
  "episode": 1,
  "use_socks5": false
}
```

#### play_next_unwatched
```json
{
  "show_title": "Murderbot",
  "use_socks5": false
}
```

#### scan_tv_show
```json
{
  "show_title": "Breaking Bad", 
  "use_socks5": false
}
```

#### get_episode_details
```json
{
  "show_title": "Breaking Bad",
  "season": 1,
  "episode": 1,
  "use_socks5": false
}
```

#### control_playback
```json
{
  "action": "pause|stop|status",
  "use_socks5": false
}
```

## Usage Examples

### Smart Episode Management (NEW v1.2.0)

**Scan specific show for new episodes and play next unwatched:**
```
User: "Scan the Murderbot TV show directory for new episodes and play the last one that I have not watched"

Workflow:
1. Uses kodi:scan_tv_show("Murderbot") → Scans only Murderbot directory (fast)
2. Uses kodi:play_next_unwatched("Murderbot") → Finds S01E03 was last watched, plays S01E04
```

**Get detailed episode information:**
```
User: "Get details for Murderbot S1E4"
Assistant: Uses kodi:get_episode_details → Shows file path, rating, plot, episode ID
```

### Basic Library Queries

**Check if content exists:**
```
User: "Do I have Inception (2010) in my Kodi library?"
Assistant: Uses kodi:check_movie_exists → "✅ Inception (2010) found in library!"
```

**Search for content:**
```
User: "Show me all action movies from 2022"
Assistant: Uses kodi:search_movies → Lists matching movies with details
```

### Playback Control

**Play specific content:**
```
User: "Play The Matrix"
Assistant: Uses kodi:play_movie → "🎬 Started playing The Matrix (1999)"

User: "Play Breaking Bad S1E1" 
Assistant: Uses kodi:play_episode → "📺 Started playing Breaking Bad S01E01: Pilot"
```

**Smart unwatched playback:**
```
User: "Play the next episode of Murderbot I haven't seen"
Assistant: Uses kodi:play_next_unwatched → Detects watch status, plays next episode
```

### Library Management

**Targeted scanning (no more full library scans!):**
```
User: "Scan just the Murderbot folder for new episodes"
Assistant: Uses kodi:scan_tv_show → Scans only that show's directory
```

**Get library information:**
```
User: "How many movies do I have?"
Assistant: Uses kodi:get_library_stats → Shows totals and top genres

User: "What did I add recently?"
Assistant: Uses kodi:get_recently_added → Lists recent additions with dates
```

## Integration Examples

### With Transmission MCP Server

Perfect companion for automated media management:

```
User: "Download Dune (2021) if I don't have it"

Workflow:
1. kodi:check_movie_exists("Dune", 2021)
2. If not found:
   - transmission:add_torrent(magnet_link, "/media/Movies/")
   - kodi:update_library()
3. If found: "Movie already exists in library"
```

### Smart TV Show Management (NEW v1.2.0)

```
User: "Check for new Murderbot episodes and play where I left off"

Workflow:
1. kodi:scan_tv_show("Murderbot") → Fast targeted scan
2. kodi:play_next_unwatched("Murderbot") → Plays next unwatched episode
```

### Automated Download Workflow

```python
# Pseudo-code workflow
async def smart_download(title, year, magnet_link):
    # Check if movie exists
    exists = await kodi.check_movie_exists(title, year)
    
    if not exists:
        # Download via transmission
        await transmission.add_torrent(magnet_link)
        
        # Wait for download completion
        await wait_for_download()
        
        # Scan library for new content
        await kodi.update_library()
        
        return f"Downloaded and added {title} to library"
    else:
        return f"{title} already exists in library"
```

## Troubleshooting

### Connection Issues

1. **Verify Kodi is running and accessible:**
```bash
python test_connection.py
```

2. **Check network connectivity:**
```bash
curl http://192.168.1.71:8080/jsonrpc -d '{"jsonrpc":"2.0","method":"JSONRPC.Ping","id":1}'
```

3. **Test SOCKS5 proxy:**
```bash
python test_connection.py --socks5 socks5://localhost:1080
```

### Common Errors

**"Cannot connect to Kodi"**
- Verify KODI_HOST and KODI_PORT
- Check if Kodi web interface is enabled
- Ensure firewall allows connections

**"Authentication failed"**
- Verify KODI_USERNAME and KODI_PASSWORD
- Check Kodi web interface authentication settings

**"SOCKS5 proxy connection failed"**
- Verify SSH tunnel is active
- Check SOCKS5_HOST and SOCKS5_PORT
- Test proxy with curl: `curl --socks5 localhost:1080 http://example.com`

### Kodi Configuration

Ensure Kodi has the following enabled:

1. **Web Interface:**
   - Settings → Services → Control → Allow remote control via HTTP
   - Username: `kodi`
   - Password: `kodi`

2. **Network Access:**
   - Allow connections from other systems
   - Port: `8080`

## Development

### Project Structure
```
kodi-mcp-server/
├── src/
│   └── server.py              # Main MCP server
├── requirements.txt           # Dependencies
├── test_connection.py         # Connection testing
├── claude-desktop-config.json # Claude integration
├── README.md                  # This file
├── CHANGELOG.md              # Development log
└── .gitignore                # Git ignore rules
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper commit messages
4. Update CHANGELOG.md (append only)
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Related Projects

- [Transmission MCP Server](https://github.com/v-odoo-testing/transmission-mcp-server) - BitTorrent client integration
- [Claude Desktop](https://claude.ai) - AI assistant with MCP support

## Support

For issues and questions:
- Create an issue on GitHub
- Check troubleshooting section
- Test connection with `test_connection.py`
