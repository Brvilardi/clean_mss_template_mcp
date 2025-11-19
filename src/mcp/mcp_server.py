"""
MCP Server for re:invent Planner API

This module implements a Model Context Protocol server that exposes the
re:invent Planner API Gateway endpoints as MCP tools. It enables AI assistants
and other MCP clients to interact with re:invent session data through
standardized tool interfaces.
"""

import os
import logging
import sys
from typing import Dict, Any
from fastmcp import FastMCP
import requests
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Configure logging to stderr (stdout reserved for MCP protocol)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger("mcp.server")

# Initialize FastMCP server
mcp = FastMCP("reinvent-planner-api", stateless_http=True)

# Configuration from environment variables
API_BASE_URL = os.getenv(
    "API_GATEWAY_BASE_URL",
    "https://3yf7o1q3s2.execute-api.us-east-1.amazonaws.com/prod/mss-template"
)
TIMEOUT = 30

# Log configuration on startup
logger.info(f"MCP Server initialized with API_BASE_URL: {API_BASE_URL}")
logger.info(f"Request timeout set to: {TIMEOUT} seconds")


@mcp.tool()
def get_all_sessions() -> Dict[str, Any]:
    """
    Retrieve all re:invent sessions from the database.
    
    Returns a list of all sessions with their complete details including
    title, venue, speakers, schedule, topics, and difficulty level.
    
    Returns:
        Dictionary containing:
        - sessions: List of session objects with full details
        - count: Total number of sessions
        
        On error, returns:
        - error: Error message string
        - status_code: HTTP status code
    
    Example response:
        {
            "sessions": [
                {
                    "session_id": "abc123",
                    "short_id": "TNC301",
                    "title": "Advanced Networking",
                    "venue_name": "Mandalay Bay",
                    "day": "Monday",
                    "level": "Advanced",
                    ...
                }
            ],
            "count": 150
        }
    """
    try:
        logger.info("Tool invoked: get_all_sessions")
        
        url = f"{API_BASE_URL}/get-all-sessions"
        logger.debug(f"Making GET request to: {url}")
        
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved {result.get('count', 0)} sessions")
        logger.info("Sessions: ", result)
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
        logger.error(
            f"Error in get_all_sessions: {error_msg}",
            extra={"status_code": status_code},
            exc_info=True
        )
        
        return {
            "error": error_msg,
            "status_code": status_code
        }


@mcp.tool()
def get_session_by_short_id(short_id: str) -> Dict[str, Any]:
    """
    Retrieve a specific re:invent session by its short ID code.
    
    Each session has a unique short ID (e.g., "TNC301", "COM305") that
    serves as a human-readable identifier. This tool retrieves the complete
    details for a single session.
    
    Args:
        short_id: Session short ID code (e.g., "TNC301", "COM305", "SVS201")
    
    Returns:
        Dictionary containing:
        - session: Session object with full details
        
        On error, returns:
        - error: Error message string
        - status_code: HTTP status code (404 if session not found)
    
    Example response:
        {
            "session": {
                "session_id": "abc123",
                "short_id": "TNC301",
                "title": "Advanced Networking",
                "venue_name": "Mandalay Bay",
                "day": "Monday",
                "level": "Advanced",
                ...
            }
        }
    """
    try:
        logger.info(f"Tool invoked: get_session_by_short_id with short_id={short_id}")
        
        if not short_id or not short_id.strip():
            logger.warning("Empty or invalid short_id provided")
            return {
                "error": "No valid session ID provided",
                "status_code": 400
            }
        
        url = f"{API_BASE_URL}/get-sessions-by-short-id"
        logger.debug(f"Making GET request to: {url} with params: short_id={short_id}")
        
        response = requests.get(
            url,
            params={"short_id": short_id.strip()},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved session with short_id: {short_id}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
        # Check if it's a 404 (session not found)
        if status_code == 404:
            logger.warning(f"Session not found: {short_id}")
        else:
            logger.error(
                f"Error in get_session_by_short_id: {error_msg}",
                extra={"status_code": status_code, "short_id": short_id},
                exc_info=True
            )
        
        return {
            "error": error_msg,
            "status_code": status_code
        }


# @mcp.tool()
# def sync_sessions() -> Dict[str, Any]:
#     """
#     Sync sessions from the external re:invent catalog API.
    
#     Triggers a data refresh operation that fetches the latest session
#     data from the AWS re:invent catalog API and updates the local database.
#     This operation may take several seconds to complete.
    
#     Returns:
#         Dictionary containing:
#         - message: Success message
#         - sessions_synced: Number of sessions updated
#         - timestamp: When the sync occurred
        
#         On error, returns:
#         - error: Error message string
#         - status_code: HTTP status code (503 if external API unavailable)
    
#     Example response:
#         {
#             "message": "Sessions synced successfully",
#             "sessions_synced": 150,
#             "timestamp": "2024-11-18T17:00:00Z"
#         }
#     """
#     try:
#         logger.info("Tool invoked: sync_sessions")
        
#         url = f"{API_BASE_URL}/sync-sessions"
#         logger.debug(f"Making POST request to: {url}")
        
#         response = requests.post(url, timeout=TIMEOUT)
#         response.raise_for_status()
        
#         result = response.json()
#         logger.info(f"Successfully synced {result.get('sessions_synced', 0)} sessions")
        
#         return result
        
#     except requests.exceptions.RequestException as e:
#         error_msg = str(e)
#         status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
#         # Check if it's a 503 (external service unavailable)
#         if status_code == 503:
#             logger.warning("External re:invent catalog API unavailable")
#         else:
#             logger.error(
#                 f"Error in sync_sessions: {error_msg}",
#                 extra={"status_code": status_code},
#                 exc_info=True
#             )
        
#         return {
#             "error": error_msg,
#             "status_code": status_code
#         }


@mcp.tool()
def get_sessions_by_venue(venue: str) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by venue location.
    
    Filters sessions to only those taking place at a specific venue.
    Venue names are case-sensitive and should match exactly.
    
    Args:
        venue: Venue name (e.g., "Mandalay Bay", "Venetian", "MGM Grand")
    
    Returns:
        Dictionary containing:
        - sessions: List of session objects at the specified venue
        - count: Number of sessions found
        - venue: The venue name that was searched
        
        On error, returns:
        - error: Error message string
        - status_code: HTTP status code
    
    Example response:
        {
            "sessions": [
                {
                    "session_id": "abc123",
                    "short_id": "TNC301",
                    "title": "Advanced Networking",
                    "venue_name": "Mandalay Bay",
                    ...
                }
            ],
            "count": 25,
            "venue": "Mandalay Bay"
        }
    """
    try:
        logger.info(f"Tool invoked: get_sessions_by_venue with venue={venue}")
        
        url = f"{API_BASE_URL}/get-sessions-by-venue"
        logger.debug(f"Making GET request to: {url} with params: venue={venue}")
        
        response = requests.get(
            url,
            params={"venue": venue},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved {result.get('count', 0)} sessions for venue: {venue}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
        logger.error(
            f"Error in get_sessions_by_venue: {error_msg}",
            extra={"status_code": status_code, "venue": venue},
            exc_info=True
        )
        
        return {
            "error": error_msg,
            "status_code": status_code
        }


@mcp.tool()
def get_sessions_by_day(day: str) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by conference day.
    
    Filters sessions to only those scheduled for a specific day of the week.
    Day names should be capitalized (e.g., "Monday", not "monday").
    
    Args:
        day: Day of the week (e.g., "Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
    
    Returns:
        Dictionary containing:
        - sessions: List of session objects on the specified day
        - count: Number of sessions found
        - day: The day that was searched
        
        On error, returns:
        - error: Error message string
        - status_code: HTTP status code
    
    Example response:
        {
            "sessions": [
                {
                    "session_id": "abc123",
                    "short_id": "TNC301",
                    "title": "Advanced Networking",
                    "day": "Monday",
                    ...
                }
            ],
            "count": 30,
            "day": "Monday"
        }
    """
    try:
        logger.info(f"Tool invoked: get_sessions_by_day with day={day}")
        
        url = f"{API_BASE_URL}/get-sessions-by-day"
        logger.debug(f"Making GET request to: {url} with params: day={day}")
        
        response = requests.get(
            url,
            params={"day": day},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved {result.get('count', 0)} sessions for day: {day}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
        logger.error(
            f"Error in get_sessions_by_day: {error_msg}",
            extra={"status_code": status_code, "day": day},
            exc_info=True
        )
        
        return {
            "error": error_msg,
            "status_code": status_code
        }


@mcp.tool()
def get_sessions_by_level(level: int) -> Dict[str, Any]:
    """
    Retrieve sessions filtered by difficulty level.
    
    Filters sessions to only those at a specific difficulty level.
    Levels follow AWS re:invent convention:
    - 100: Foundational (introductory content)
    - 200: Intermediate (some prior knowledge expected)
    - 300: Advanced (deep technical content)
    - 400: Expert (specialized, advanced topics)
    
    Args:
        level: Difficulty level (100, 200, 300, or 400)
    
    Returns:
        Dictionary containing:
        - sessions: List of session objects at the specified level
        - count: Number of sessions found
        - level: The level that was searched
        
        On error, returns:
        - error: Error message string
        - status_code: HTTP status code
    
    Example response:
        {
            "sessions": [
                {
                    "session_id": "abc123",
                    "short_id": "TNC301",
                    "title": "Advanced Networking",
                    "level": "Advanced",
                    "level_value": 300,
                    ...
                }
            ],
            "count": 40,
            "level": 300
        }
    """
    try:
        logger.info(f"Tool invoked: get_sessions_by_level with level={level}")
        
        url = f"{API_BASE_URL}/get-sessions-by-level"
        logger.debug(f"Making GET request to: {url} with params: level={level}")
        
        response = requests.get(
            url,
            params={"level": level},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        result = response.json()
        logger.info(f"Successfully retrieved {result.get('count', 0)} sessions for level: {level}")
        
        return result
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        status_code = getattr(e.response, 'status_code', 500) if hasattr(e, 'response') else 500
        
        logger.error(
            f"Error in get_sessions_by_level: {error_msg}",
            extra={"status_code": status_code, "level": level},
            exc_info=True
        )
        
        return {
            "error": error_msg,
            "status_code": status_code
        }


# Define CORS middleware
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],          # 🔓 debug; later swap to ["http://localhost:6274"]
        allow_methods=["*"],          # GET, POST, OPTIONS, etc.
        allow_headers=["*"],          # accept all request headers
        expose_headers=["mcp-session-id"],
    )
]


app = mcp.http_app(middleware=middleware, path="/mcp")

# if __name__ == "__main__":
#     logger.info(f"Starting MCP server with HTTP")
#     mcp.run(transport="http", app=app)
