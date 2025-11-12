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
