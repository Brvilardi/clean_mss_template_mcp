import requests
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class ReinventCatalogClient:
    """Client for fetching AWS re:invent session data from the catalog API."""
    
    BASE_URL = "https://reinvent-planner.cloud/api/catalog"
    
    def fetch_sessions(self) -> List[Dict]:
        """
        Fetches all sessions from the re:invent catalog API.
        
        Returns:
            List[Dict]: List of session dictionaries from the API
            
        Raises:
            ConnectionError: If the API is unreachable or returns an error
        """
        try:
            logger.info(f"Fetching sessions from {self.BASE_URL}")
            response = requests.get(self.BASE_URL, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            sessions = data.get('catalog', [])
            
            logger.info(f"Successfully fetched {len(sessions)} sessions from catalog API")
            return sessions
            
        except requests.exceptions.Timeout as e:
            error_msg = f"Timeout while connecting to re:invent catalog API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to re:invent catalog API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error from re:invent catalog API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching sessions from re:invent catalog API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
            
        except (ValueError, KeyError) as e:
            error_msg = f"Invalid JSON response from re:invent catalog API: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
