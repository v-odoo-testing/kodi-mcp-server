#!/usr/bin/env python3
"""
Kodi MCP Server

A Model Context Protocol server for interacting with Kodi media center.
Provides tools for querying media libraries, checking existing content,
and managing Kodi remotely.
"""

import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
    ServerCapabilities,
    ToolsCapability
)
from pydantic import BaseModel, Field


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kodi-mcp-server")

# Configuration from environment variables
KODI_HOST = os.getenv("KODI_HOST", "192.168.1.71")
KODI_PORT = int(os.getenv("KODI_PORT", "8080"))
KODI_USERNAME = os.getenv("KODI_USERNAME", "kodi")
KODI_PASSWORD = os.getenv("KODI_PASSWORD", "kodi")
KODI_TIMEOUT = int(os.getenv("KODI_TIMEOUT", "30"))
USE_HTTPS = os.getenv("USE_HTTPS", "false").lower() == "true"

# SOCKS5 proxy configuration
SOCKS5_HOST = os.getenv("SOCKS5_HOST")
SOCKS5_PORT = int(os.getenv("SOCKS5_PORT", "1080"))
SOCKS5_USERNAME = os.getenv("SOCKS5_USERNAME")
SOCKS5_PASSWORD = os.getenv("SOCKS5_PASSWORD")


class KodiMovie(BaseModel):
    """Model for Kodi movie data."""
    movieid: int
    title: str
    year: int = 0
    file: str = ""
    genre: List[str] = Field(default_factory=list)
    rating: float = 0.0
    runtime: int = 0
    plot: str = ""
    director: List[str] = Field(default_factory=list)


class KodiTVShow(BaseModel):
    """Model for Kodi TV show data."""
    tvshowid: int
    title: str
    year: int = 0
    genre: List[str] = Field(default_factory=list)
    rating: float = 0.0
    plot: str = ""
    episode: int = 0
    season: int = 0


class KodiEpisode(BaseModel):
    """Model for Kodi episode data."""
    episodeid: int
    title: str
    season: int
    episode: int
    file: str = ""
    tvshowid: int = 0
    showtitle: str = ""
    plot: str = ""
    rating: float = 0.0


class KodiAPI:
    """Kodi JSON-RPC API client."""
    
    def __init__(self):
        self.protocol = "https" if USE_HTTPS else "http"
        self.base_url = f"{self.protocol}://{KODI_HOST}:{KODI_PORT}/jsonrpc"
        self.timeout = KODI_TIMEOUT
        
        # Create auth tuple if credentials provided
        self.auth = None
        if KODI_USERNAME and KODI_PASSWORD:
            self.auth = (KODI_USERNAME, KODI_PASSWORD)
        
        # SOCKS5 proxy configuration
        self.proxy_url = None
        if SOCKS5_HOST:
            if SOCKS5_USERNAME and SOCKS5_PASSWORD:
                self.proxy_url = f"socks5://{SOCKS5_USERNAME}:{SOCKS5_PASSWORD}@{SOCKS5_HOST}:{SOCKS5_PORT}"
            else:
                self.proxy_url = f"socks5://{SOCKS5_HOST}:{SOCKS5_PORT}"
    
    async def _make_request(self, method: str, params: Optional[Dict] = None, use_socks5: bool = False) -> Dict[str, Any]:
        """Make a JSON-RPC request to Kodi."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": 1
        }
        
        if params:
            payload["params"] = params
        
        try:
            # Determine proxy settings for httpx 0.28+
            proxy = None
            if use_socks5 and self.proxy_url:
                proxy = self.proxy_url
            
            async with httpx.AsyncClient(timeout=self.timeout, proxy=proxy) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    auth=self.auth
                )
                response.raise_for_status()
                
                data = response.json()
                
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown error")
                    raise Exception(f"Kodi API error: {error_msg}")
                
                return data.get("result", {})
                
        except httpx.TimeoutException:
            proxy_info = " via SOCKS5 proxy" if use_socks5 and self.proxy_url else ""
            raise Exception(f"Timeout connecting to Kodi at {self.base_url}{proxy_info}")
        except httpx.ConnectError:
            proxy_info = " via SOCKS5 proxy" if use_socks5 and self.proxy_url else ""
            raise Exception(f"Cannot connect to Kodi at {self.base_url}{proxy_info}")
        except Exception as e:
            if "Kodi API error" in str(e):
                raise
            proxy_info = " via SOCKS5 proxy" if use_socks5 and self.proxy_url else ""
            raise Exception(f"Error communicating with Kodi{proxy_info}: {str(e)}")
    
    async def get_movies(self, properties: Optional[List[str]] = None, use_socks5: bool = False) -> List[KodiMovie]:
        """Get all movies from Kodi library."""
        if properties is None:
            properties = ["title", "year", "file", "genre", "rating", "runtime", "plot", "director"]
        
        params = {
            "properties": properties,
            "sort": {"order": "ascending", "method": "title"}
        }
        
        result = await self._make_request("VideoLibrary.GetMovies", params, use_socks5)
        movies = result.get("movies", [])
        
        return [KodiMovie(**movie) for movie in movies]
    
    async def get_tv_shows(self, properties: Optional[List[str]] = None, use_socks5: bool = False) -> List[KodiTVShow]:
        """Get all TV shows from Kodi library."""
        if properties is None:
            properties = ["title", "year", "genre", "rating", "plot", "episode", "season"]
        
        params = {
            "properties": properties,
            "sort": {"order": "ascending", "method": "title"}
        }
        
        result = await self._make_request("VideoLibrary.GetTVShows", params, use_socks5)
        tvshows = result.get("tvshows", [])
        
        return [KodiTVShow(**show) for show in tvshows]
    
    async def get_episodes(self, tvshow_id: int, season: Optional[int] = None, use_socks5: bool = False) -> List[KodiEpisode]:
        """Get episodes for a TV show."""
        properties = ["title", "season", "episode", "file", "tvshowid", "showtitle", "plot", "rating"]
        
        params = {
            "tvshowid": tvshow_id,
            "properties": properties,
            "sort": {"order": "ascending", "method": "episode"}
        }
        
        if season is not None:
            params["season"] = season
        
        result = await self._make_request("VideoLibrary.GetEpisodes", params, use_socks5)
        episodes = result.get("episodes", [])
        
        return [KodiEpisode(**episode) for episode in episodes]
    
    async def play_movie(self, movie_id: int, use_socks5: bool = False) -> bool:
        """Play a movie by ID."""
        params = {
            "item": {"movieid": movie_id}
        }
        
        await self._make_request("Player.Open", params, use_socks5)
        return True
    
    async def play_episode(self, episode_id: int, use_socks5: bool = False) -> bool:
        """Play an episode by ID."""
        params = {
            "item": {"episodeid": episode_id}
        }
        
        await self._make_request("Player.Open", params, use_socks5)
        return True
    
    async def get_active_players(self, use_socks5: bool = False) -> List[Dict[str, Any]]:
        """Get currently active players."""
        result = await self._make_request("Player.GetActivePlayers", use_socks5=use_socks5)
        return result if isinstance(result, list) else []
    
    async def pause_playback(self, player_id: int = 1, use_socks5: bool = False) -> bool:
        """Pause/unpause playback."""
        params = {"playerid": player_id}
        await self._make_request("Player.PlayPause", params, use_socks5)
        return True
    
    async def stop_playback(self, player_id: int = 1, use_socks5: bool = False) -> bool:
        """Stop playback."""
        params = {"playerid": player_id}
        await self._make_request("Player.Stop", params, use_socks5)
        return True
    
    async def scan_library(self, directory: Optional[str] = None, use_socks5: bool = False) -> bool:
        """Trigger a library scan."""
        params = {}
        if directory:
            params["directory"] = directory
        
        await self._make_request("VideoLibrary.Scan", params, use_socks5)
        return True
    
    async def clean_library(self, use_socks5: bool = False) -> bool:
        """Clean the library (remove orphaned entries)."""
        await self._make_request("VideoLibrary.Clean", use_socks5=use_socks5)
        return True


# Initialize Kodi API client
kodi = KodiAPI()

# Create MCP server instance
server = Server("kodi-mcp-server")


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_movies",
            description="Search for movies in Kodi library by title, year, or genre",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Movie title to search for"},
                    "year": {"type": "integer", "description": "Release year"},
                    "genre": {"type": "string", "description": "Genre to filter by"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": []
            }
        ),
        Tool(
            name="search_tv_shows", 
            description="Search for TV shows in Kodi library by title or genre",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "TV show title to search for"},
                    "genre": {"type": "string", "description": "Genre to filter by"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": []
            }
        ),
        Tool(
            name="check_movie_exists",
            description="Check if a specific movie exists in Kodi library",
            inputSchema={
                "type": "object", 
                "properties": {
                    "title": {"type": "string", "description": "Movie title"},
                    "year": {"type": "integer", "description": "Release year (optional)"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="check_tv_show_exists",
            description="Check if a TV show, season, or episode exists in Kodi library",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "TV show title"},
                    "season": {"type": "integer", "description": "Season number (optional)"},
                    "episode": {"type": "integer", "description": "Episode number (optional)"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="play_movie",
            description="Play a movie in Kodi by title and optional year",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Movie title"},
                    "year": {"type": "integer", "description": "Release year (optional for disambiguation)"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="play_episode",
            description="Play a TV episode in Kodi",
            inputSchema={
                "type": "object",
                "properties": {
                    "show_title": {"type": "string", "description": "TV show title"},
                    "season": {"type": "integer", "description": "Season number"},
                    "episode": {"type": "integer", "description": "Episode number"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": ["show_title", "season", "episode"]
            }
        ),
        Tool(
            name="control_playback",
            description="Control Kodi playback (pause, stop, or get status)",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["pause", "stop", "status"],
                        "description": "Playback action to perform"
                    },
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="get_library_stats",
            description="Get overview statistics of Kodi media library",
            inputSchema={
                "type": "object",
                "properties": {
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": []
            }
        ),
        Tool(
            name="get_recently_added",
            description="Get recently added movies and TV episodes",
            inputSchema={
                "type": "object",
                "properties": {
                    "media_type": {
                        "type": "string",
                        "enum": ["movies", "episodes", "both"],
                        "description": "Type of media to retrieve",
                        "default": "both"
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of items to return",
                        "default": 20
                    },
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": []
            }
        ),
        Tool(
            name="update_library",
            description="Trigger Kodi library scan for new content",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Specific directory to scan (optional)"},
                    "use_socks5": {"type": "boolean", "description": "Use SOCKS5 proxy for this request (default: false)", "default": False}
                },
                "required": []
            }
        )
    ]


def fuzzy_match(search_term: str, target: str, threshold: float = 0.6) -> bool:
    """Simple fuzzy string matching."""
    search_lower = search_term.lower()
    target_lower = target.lower()
    
    # Exact match
    if search_lower == target_lower:
        return True
    
    # Contains match
    if search_lower in target_lower:
        return True
    
    # Simple similarity check
    words_search = set(search_lower.split())
    words_target = set(target_lower.split())
    
    if words_search and words_target:
        intersection = len(words_search.intersection(words_target))
        union = len(words_search.union(words_target))
        similarity = intersection / union
        return similarity >= threshold
    
    return False


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_movies":
            return await search_movies_tool(arguments)
        elif name == "search_tv_shows":
            return await search_tv_shows_tool(arguments)
        elif name == "check_movie_exists":
            return await check_movie_exists_tool(arguments)
        elif name == "check_tv_show_exists":
            return await check_tv_show_exists_tool(arguments)
        elif name == "play_movie":
            return await play_movie_tool(arguments)
        elif name == "play_episode":
            return await play_episode_tool(arguments)
        elif name == "control_playback":
            return await control_playback_tool(arguments)
        elif name == "get_library_stats":
            return await get_library_stats_tool(arguments)
        elif name == "get_recently_added":
            return await get_recently_added_tool(arguments)
        elif name == "update_library":
            return await update_library_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def search_movies_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for movies in Kodi library."""
    title_search = arguments.get("title", "").strip()
    year_search = arguments.get("year")
    genre_search = arguments.get("genre", "").strip().lower()
    use_socks5 = arguments.get("use_socks5", False)
    
    movies = await kodi.get_movies(use_socks5=use_socks5)
    
    if not movies:
        return [TextContent(type="text", text="No movies found in Kodi library.")]
    
    # Filter movies based on search criteria
    filtered_movies = []
    
    for movie in movies:
        # Title matching
        title_match = True
        if title_search:
            title_match = fuzzy_match(title_search, movie.title)
        
        # Year matching
        year_match = True
        if year_search:
            year_match = movie.year == year_search
        
        # Genre matching
        genre_match = True
        if genre_search:
            genre_match = any(genre_search in genre.lower() for genre in movie.genre)
        
        if title_match and year_match and genre_match:
            filtered_movies.append(movie)
    
    if not filtered_movies:
        search_terms = []
        if title_search:
            search_terms.append(f"title: '{title_search}'")
        if year_search:
            search_terms.append(f"year: {year_search}")
        if genre_search:
            search_terms.append(f"genre: '{genre_search}'")
        
        return [TextContent(
            type="text", 
            text=f"No movies found matching {', '.join(search_terms)}."
        )]
    
    # Format results
    result_text = f"Found {len(filtered_movies)} movie(s):\n\n"
    
    for movie in filtered_movies:
        genres = ", ".join(movie.genre) if movie.genre else "Unknown"
        directors = ", ".join(movie.director) if movie.director else "Unknown"
        
        result_text += f"**{movie.title}** ({movie.year})\n"
        result_text += f"  • Genres: {genres}\n"
        result_text += f"  • Director(s): {directors}\n"
        result_text += f"  • Rating: {movie.rating}/10\n"
        result_text += f"  • Runtime: {movie.runtime} minutes\n"
        if movie.file:
            result_text += f"  • File: {movie.file}\n"
        result_text += "\n"
    
    return [TextContent(type="text", text=result_text)]


async def search_tv_shows_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Search for TV shows in Kodi library."""
    title_search = arguments.get("title", "").strip()
    genre_search = arguments.get("genre", "").strip().lower()
    use_socks5 = arguments.get("use_socks5", False)
    
    tv_shows = await kodi.get_tv_shows(use_socks5=use_socks5)
    
    if not tv_shows:
        return [TextContent(type="text", text="No TV shows found in Kodi library.")]
    
    # Filter TV shows based on search criteria
    filtered_shows = []
    
    for show in tv_shows:
        # Title matching
        title_match = True
        if title_search:
            title_match = fuzzy_match(title_search, show.title)
        
        # Genre matching
        genre_match = True
        if genre_search:
            genre_match = any(genre_search in genre.lower() for genre in show.genre)
        
        if title_match and genre_match:
            filtered_shows.append(show)
    
    if not filtered_shows:
        search_terms = []
        if title_search:
            search_terms.append(f"title: '{title_search}'")
        if genre_search:
            search_terms.append(f"genre: '{genre_search}'")
        
        return [TextContent(
            type="text",
            text=f"No TV shows found matching {', '.join(search_terms)}."
        )]
    
    # Format results
    result_text = f"Found {len(filtered_shows)} TV show(s):\n\n"
    
    for show in filtered_shows:
        genres = ", ".join(show.genre) if show.genre else "Unknown"
        
        result_text += f"**{show.title}** ({show.year})\n"
        result_text += f"  • Genres: {genres}\n"
        result_text += f"  • Rating: {show.rating}/10\n"
        result_text += f"  • Episodes: {show.episode}\n"
        result_text += f"  • Seasons: {show.season}\n"
        result_text += "\n"
    
    return [TextContent(type="text", text=result_text)]


async def check_movie_exists_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Check if a specific movie exists in Kodi library."""
    title = arguments.get("title", "").strip()
    year = arguments.get("year")
    use_socks5 = arguments.get("use_socks5", False)
    
    if not title:
        return [TextContent(type="text", text="Error: Movie title is required.")]
    
    movies = await kodi.get_movies(use_socks5=use_socks5)
    
    # Find matching movies
    matching_movies = []
    
    for movie in movies:
        title_match = fuzzy_match(title, movie.title)
        year_match = year is None or movie.year == year
        
        if title_match and year_match:
            matching_movies.append(movie)
    
    if not matching_movies:
        search_text = f"'{title}'"
        if year:
            search_text += f" ({year})"
        return [TextContent(type="text", text=f"Movie {search_text} not found in Kodi library.")]
    
    if len(matching_movies) == 1:
        movie = matching_movies[0]
        result_text = f"✅ **{movie.title}** ({movie.year}) found in library!\n\n"
        result_text += f"  • File: {movie.file}\n"
        if movie.genre:
            result_text += f"  • Genres: {', '.join(movie.genre)}\n"
        result_text += f"  • Rating: {movie.rating}/10\n"
        result_text += f"  • Runtime: {movie.runtime} minutes\n"
    else:
        result_text = f"Found {len(matching_movies)} movies matching '{title}':\n\n"
        for movie in matching_movies:
            result_text += f"  • **{movie.title}** ({movie.year}) - {movie.file}\n"
    
    return [TextContent(type="text", text=result_text)]


async def check_tv_show_exists_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Check if a TV show, season, or episode exists in Kodi library."""
    title = arguments.get("title", "").strip()
    season_num = arguments.get("season")
    episode_num = arguments.get("episode")
    use_socks5 = arguments.get("use_socks5", False)
    
    if not title:
        return [TextContent(type="text", text="Error: TV show title is required.")]
    
    tv_shows = await kodi.get_tv_shows(use_socks5=use_socks5)
    
    # Find matching TV show
    matching_show = None
    for show in tv_shows:
        if fuzzy_match(title, show.title):
            matching_show = show
            break
    
    if not matching_show:
        return [TextContent(type="text", text=f"TV show '{title}' not found in Kodi library.")]
    
    # If only checking for show existence
    if season_num is None and episode_num is None:
        result_text = f"✅ **{matching_show.title}** ({matching_show.year}) found in library!\n\n"
        result_text += f"  • Total episodes: {matching_show.episode}\n"
        result_text += f"  • Total seasons: {matching_show.season}\n"
        if matching_show.genre:
            result_text += f"  • Genres: {', '.join(matching_show.genre)}\n"
        result_text += f"  • Rating: {matching_show.rating}/10\n"
        
        return [TextContent(type="text", text=result_text)]
    
    # Get episodes for detailed checking
    episodes = await kodi.get_episodes(matching_show.tvshowid, use_socks5=use_socks5)
    
    if season_num is not None:
        season_episodes = [ep for ep in episodes if ep.season == season_num]
        
        if not season_episodes:
            return [TextContent(
                type="text",
                text=f"Season {season_num} of '{matching_show.title}' not found in library."
            )]
        
        if episode_num is not None:
            # Check specific episode
            episode = next((ep for ep in season_episodes if ep.episode == episode_num), None)
            
            if episode:
                result_text = f"✅ **{matching_show.title}** S{season_num:02d}E{episode_num:02d} found!\n\n"
                result_text += f"  • Episode: {episode.title}\n"
                result_text += f"  • File: {episode.file}\n"
                result_text += f"  • Rating: {episode.rating}/10\n"
            else:
                result_text = f"Episode {episode_num} of season {season_num} of '{matching_show.title}' not found."
        else:
            # Check entire season
            result_text = f"✅ Season {season_num} of **{matching_show.title}** found!\n\n"
            result_text += f"  • Episodes in season: {len(season_episodes)}\n"
            result_text += f"  • Episode range: {min(ep.episode for ep in season_episodes)}-{max(ep.episode for ep in season_episodes)}\n"
    
    return [TextContent(type="text", text=result_text)]


async def get_library_stats_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get overview statistics of Kodi media library."""
    use_socks5 = arguments.get("use_socks5", False)
    
    try:
        movies = await kodi.get_movies(use_socks5=use_socks5)
        tv_shows = await kodi.get_tv_shows(use_socks5=use_socks5)
        
        # Calculate total episodes
        total_episodes = 0
        for show in tv_shows:
            total_episodes += show.episode
        
        # Calculate genres distribution for movies
        movie_genres = {}
        for movie in movies:
            for genre in movie.genre:
                movie_genres[genre] = movie_genres.get(genre, 0) + 1
        
        # Calculate genres distribution for TV shows
        tv_genres = {}
        for show in tv_shows:
            for genre in show.genre:
                tv_genres[genre] = tv_genres.get(genre, 0) + 1
        
        result_text = "📊 **Kodi Library Statistics**\n\n"
        result_text += f"**Movies:** {len(movies)}\n"
        result_text += f"**TV Shows:** {len(tv_shows)}\n"
        result_text += f"**Total Episodes:** {total_episodes}\n\n"
        
        if movie_genres:
            result_text += "**Top Movie Genres:**\n"
            sorted_movie_genres = sorted(movie_genres.items(), key=lambda x: x[1], reverse=True)
            for genre, count in sorted_movie_genres[:5]:
                result_text += f"  • {genre}: {count}\n"
            result_text += "\n"
        
        if tv_genres:
            result_text += "**Top TV Show Genres:**\n"
            sorted_tv_genres = sorted(tv_genres.items(), key=lambda x: x[1], reverse=True)
            for genre, count in sorted_tv_genres[:5]:
                result_text += f"  • {genre}: {count}\n"
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting library statistics: {str(e)}")]


async def get_recently_added_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Get recently added movies and TV episodes."""
    media_type = arguments.get("media_type", "both")
    limit = arguments.get("limit", 20)
    use_socks5 = arguments.get("use_socks5", False)
    
    result_text = "📅 **Recently Added Content**\n\n"
    
    try:
        if media_type in ["movies", "both"]:
            # Get recently added movies
            params = {
                "properties": ["title", "year", "file", "genre", "dateadded"],
                "sort": {"order": "descending", "method": "dateadded"},
                "limits": {"end": limit if media_type == "movies" else limit // 2}
            }
            
            result = await kodi._make_request("VideoLibrary.GetRecentlyAddedMovies", params, use_socks5)
            recent_movies = result.get("movies", [])
            
            if recent_movies:
                result_text += f"**Movies ({len(recent_movies)}):**\n"
                for movie in recent_movies:
                    title = movie.get("title", "Unknown")
                    year = movie.get("year", 0)
                    dateadded = movie.get("dateadded", "Unknown date")
                    genres = ", ".join(movie.get("genre", []))
                    
                    result_text += f"  • **{title}** ({year}) - {dateadded}\n"
                    if genres:
                        result_text += f"    Genres: {genres}\n"
                result_text += "\n"
        
        if media_type in ["episodes", "both"]:
            # Get recently added episodes
            params = {
                "properties": ["title", "season", "episode", "showtitle", "file", "dateadded"],
                "sort": {"order": "descending", "method": "dateadded"},
                "limits": {"end": limit if media_type == "episodes" else limit // 2}
            }
            
            result = await kodi._make_request("VideoLibrary.GetRecentlyAddedEpisodes", params, use_socks5)
            recent_episodes = result.get("episodes", [])
            
            if recent_episodes:
                result_text += f"**Episodes ({len(recent_episodes)}):**\n"
                for episode in recent_episodes:
                    title = episode.get("title", "Unknown")
                    showtitle = episode.get("showtitle", "Unknown Show")
                    season = episode.get("season", 0)
                    episode_num = episode.get("episode", 0)
                    dateadded = episode.get("dateadded", "Unknown date")
                    
                    result_text += f"  • **{showtitle}** S{season:02d}E{episode_num:02d}: {title} - {dateadded}\n"
        
        if "Movies" not in result_text and "Episodes" not in result_text:
            result_text += "No recently added content found."
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error getting recently added content: {str(e)}")]


async def update_library_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Trigger Kodi library scan for new content."""
    directory = arguments.get("directory")
    use_socks5 = arguments.get("use_socks5", False)
    
    try:
        await kodi.scan_library(directory, use_socks5=use_socks5)
        
        if directory:
            result_text = f"✅ Library scan started for directory: {directory}"
        else:
            result_text = "✅ Full library scan started. This may take a few minutes."
        
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Error starting library scan: {str(e)}")]


async def main():
    """Main entry point for the server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="kodi-mcp-server",
                server_version="1.0.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(listChanged=True)
                )
            ),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

async def play_movie_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Play a movie in Kodi."""
    title = arguments.get("title", "").strip()
    year = arguments.get("year")
    use_socks5 = arguments.get("use_socks5", False)
    
    if not title:
        return [TextContent(type="text", text="Error: Movie title is required.")]
    
    movies = await kodi.get_movies(use_socks5=use_socks5)
    
    # Find matching movie
    matching_movies = []
    for movie in movies:
        title_match = fuzzy_match(title, movie.title)
        year_match = year is None or movie.year == year
        
        if title_match and year_match:
            matching_movies.append(movie)
    
    if not matching_movies:
        search_text = f"'{title}'"
        if year:
            search_text += f" ({year})"
        return [TextContent(type="text", text=f"Movie {search_text} not found in Kodi library.")]
    
    if len(matching_movies) > 1:
        result_text = f"Multiple movies found matching '{title}':\n\n"
        for i, movie in enumerate(matching_movies, 1):
            result_text += f"{i}. **{movie.title}** ({movie.year})\n"
        result_text += "\nPlease be more specific with year or exact title."
        return [TextContent(type="text", text=result_text)]
    
    # Play the movie
    movie = matching_movies[0]
    try:
        await kodi.play_movie(movie.movieid, use_socks5=use_socks5)
        result_text = f"🎬 Started playing **{movie.title}** ({movie.year})"
        return [TextContent(type="text", text=result_text)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error starting playback: {str(e)}")]


async def play_episode_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Play a TV episode in Kodi."""
    show_title = arguments.get("show_title", "").strip()
    season = arguments.get("season")
    episode = arguments.get("episode")
    use_socks5 = arguments.get("use_socks5", False)
    
    if not show_title or season is None or episode is None:
        return [TextContent(type="text", text="Error: Show title, season, and episode are required.")]
    
    tv_shows = await kodi.get_tv_shows(use_socks5=use_socks5)
    
    # Find matching TV show
    matching_show = None
    for show in tv_shows:
        if fuzzy_match(show_title, show.title):
            matching_show = show
            break
    
    if not matching_show:
        return [TextContent(type="text", text=f"TV show '{show_title}' not found in Kodi library.")]
    
    # Get episodes and find the specific one
    episodes = await kodi.get_episodes(matching_show.tvshowid, use_socks5=use_socks5)
    target_episode = None
    
    for ep in episodes:
        if ep.season == season and ep.episode == episode:
            target_episode = ep
            break
    
    if not target_episode:
        return [TextContent(
            type="text",
            text=f"Episode S{season:02d}E{episode:02d} of '{matching_show.title}' not found in library."
        )]
    
    # Play the episode
    try:
        await kodi.play_episode(target_episode.episodeid, use_socks5=use_socks5)
        result_text = f"📺 Started playing **{matching_show.title}** S{season:02d}E{episode:02d}: {target_episode.title}"
        return [TextContent(type="text", text=result_text)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error starting playback: {str(e)}")]


async def control_playback_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    """Control Kodi playback."""
    action = arguments.get("action")
    use_socks5 = arguments.get("use_socks5", False)
    
    if not action:
        return [TextContent(type="text", text="Error: Action is required.")]
    
    try:
        if action == "status":
            players = await kodi.get_active_players(use_socks5=use_socks5)
            if not players:
                return [TextContent(type="text", text="No active playback sessions.")]
            
            result_text = f"🎮 Active players: {len(players)}\n"
            for player in players:
                player_type = player.get("type", "unknown")
                player_id = player.get("playerid", "unknown")
                result_text += f"  • Player {player_id}: {player_type}\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif action == "pause":
            await kodi.pause_playback(use_socks5=use_socks5)
            return [TextContent(type="text", text="⏸️ Playback paused/resumed")]
        
        elif action == "stop":
            await kodi.stop_playback(use_socks5=use_socks5)
            return [TextContent(type="text", text="⏹️ Playback stopped")]
        
        else:
            return [TextContent(type="text", text=f"Unknown action: {action}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error controlling playback: {str(e)}")]

