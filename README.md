 kodi:search_movies with use_socks5=true
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
- `control_playback` - Pause, stop, or get playback status

### Library Tools
- `get_library_stats` - Get library overview and statistics
- `get_recently_added` - List recently added content
- `update_library` - Trigger library scan

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

#### control_playback
```json
{
  "action": "pause|stop|status",
  "use_socks5": false
}
```

## Integration Examples

### With Transmission MCP Server

Perfect companion for media management:

```
User: "Check if I have The Batman (2022), download if missing"

Workflow:
1. kodi:check_movie_exists("The Batman", 2022)
2. If not found:
   - transmission:add_torrent(magnet_link, "/media/Movies/")
   - kodi:update_library()
3. If found: "Movie already exists in library"
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
