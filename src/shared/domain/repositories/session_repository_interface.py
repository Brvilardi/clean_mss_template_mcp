from abc import ABC, abstractmethod
from typing import List, Dict

from src.shared.domain.entities.session import Session


class ISessionRepository(ABC):

    @abstractmethod
    def get_all_sessions(self) -> List[Session]:
        """
        Returns all sessions from storage.
        
        Returns:
            List of Session entities
        """
        pass

    @abstractmethod
    def sync_sessions_from_api(self) -> Dict[str, int]:
        """
        Fetches data from external API and updates storage.
        
        Returns:
            Dictionary with keys 'inserted' and 'updated' containing counts
            
        Raises:
            ConnectionError: If external API is unreachable
        """
        pass

    @abstractmethod
    def get_session_by_id(self, session_id: str) -> Session:
        """
        Returns a specific session by ID.
        
        Args:
            session_id: The unique session identifier
            
        Returns:
            Session entity
            
        Raises:
            NoItemsFound: If session with given ID is not found
        """
        pass

    @abstractmethod
    def get_sessions_by_venue(self, venue_name: str) -> List[Session]:
        """
        Returns sessions filtered by venue name, ordered by start_datetime.
        
        Args:
            venue_name: The venue name to filter by
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        pass

    @abstractmethod
    def get_sessions_by_day(self, day: str) -> List[Session]:
        """
        Returns sessions filtered by day, ordered by start_datetime.
        
        Args:
            day: The day to filter by (e.g., "Monday", "Tuesday")
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        pass

    @abstractmethod
    def get_sessions_by_level(self, level_value: int) -> List[Session]:
        """
        Returns sessions filtered by level value, ordered by start_datetime.
        
        Args:
            level_value: The level value to filter by (100, 200, 300, 400)
            
        Returns:
            List of Session entities ordered by start_datetime
        """
        pass

    @abstractmethod
    def get_sessions_by_short_id(self, short_id: str) -> List[Session]:
        """
        Returns sessions filtered by short_id (case-insensitive).
        
        Args:
            short_id: The short ID to filter by (e.g., "TNC301")
            
        Returns:
            List of Session entities (typically 0 or 1 result)
        """
        pass
