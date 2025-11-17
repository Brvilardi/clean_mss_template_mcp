from typing import List
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class GetSessionsByVenueUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self, venue_name: str) -> List[Session]:
        """
        Retrieves all sessions matching the specified venue name.
        
        Args:
            venue_name: The venue name to filter by
            
        Returns:
            List of Session entities matching the venue, ordered by start_datetime
        """
        return self.repo.get_sessions_by_venue(venue_name=venue_name)
