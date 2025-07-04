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

### Features Added
- Setup script (`setup.sh`) for automated installation and configuration
- Python version validation and virtual environment setup


### Bug Fixes
- Fixed httpx proxy parameter for v0.28+ compatibility (proxies -> proxy)
- Added httpx[socks] dependency for proper SOCKS5 support
- Fixed MCP server initialization with correct ServerCapabilities
- Updated Claude Desktop configuration with absolute paths

### Testing
- Verified connection to Kodi at 192.168.1.71 (2083 movies found)
- MCP server starts without errors
- Virtual environment recreated with Python 3.11


## [1.1.0] - 2025-06-30

### Added
- `scan_tv_show` tool - Scan specific TV show directories instead of entire library
- `get_episode_details` tool - Get detailed episode information including file paths
- Enhanced episode playback debugging with file paths and episode IDs
- Improved error handling with troubleshooting suggestions

### Enhanced
- `play_episode` tool now provides detailed error information and file paths
- Better directory scanning that finds show folders automatically
- Targeted scanning reduces scan time from hours to minutes

### Bug Fixes
- Fixed issue where library scanning would scan entire collection
- Improved episode playback error reporting for troubleshooting


## [1.2.0] - 2025-06-30

### Added
- `play_next_unwatched` tool - Automatically finds and plays the next unwatched episode
- Watch status tracking via Kodi's playcount and lastplayed data
- `get_episodes_with_watch_status` API method for episode watch data
- Comprehensive test suite for all new functionality

### Enhanced
- Server version bumped to 1.2.0
- Complete workflow: scan specific show directory + play next unwatched episode
- Detailed previous watch status reporting

### Fixed
- Syntax errors in tool definitions
- Proper function placement to ensure all tools load correctly

### Development
- Organized test files into `tests/` directory
- Added test documentation and usage instructions
- Direct MCP server testing capabilities for development
