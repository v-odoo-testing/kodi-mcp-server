# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-30

### Added
- Initial implementation of Kodi MCP Server
- Basic connection to Kodi JSON-RPC API with authentication
- SOCKS5 proxy support for remote access through SSH tunnels
- Core library search tools:
  - `search_movies` - Search movies by title, year, or genre
  - `search_tv_shows` - Search TV shows by title or genre  
  - `check_movie_exists` - Quick movie existence check
  - `check_tv_show_exists` - TV show/season/episode availability check
- Playback control tools:
  - `play_movie` - Play movies by title
  - `play_episode` - Play specific TV episodes
  - `control_playback` - Pause, stop, and get playback status
- Library management tools:
  - `get_library_stats` - Library overview and statistics
  - `get_recently_added` - List recently added content
  - `update_library` - Trigger library scans
- Fuzzy string matching for improved search results
- Comprehensive error handling and connection management
- Environment variable configuration for all settings
- Connection testing utility (`test_connection.py`)
- Claude Desktop integration configuration
- Complete documentation with usage examples
- All tools support optional `use_socks5` parameter for proxy usage

### Development Milestones
- Project setup and repository created at https://github.com/v-odoo-testing/kodi-mcp-server
- Initial commit with complete feature set and documentation
