from typing import List
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class GetSessionsByShortIdUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self, short_id: str) -> List[Session]:
        """
        Retrieves sessions matching the given short_id.
        
        Args:
            short_id: The short ID to filter sessions by (case-insensitive)
            
        Returns:
            List of Session entities matching the short_id (0 or 1 result expected)
        """
        return self.repo.get_sessions_by_short_id(short_id)
