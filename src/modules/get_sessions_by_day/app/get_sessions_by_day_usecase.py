from typing import List
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class GetSessionsByDayUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self, day: str) -> List[Session]:
        """
        Retrieves all sessions for a specific day.
        
        Args:
            day: Day of the week to filter by (case-insensitive)
            
        Returns:
            List of Session entities matching the day
        """
        all_sessions = self.repo.get_all_sessions()
        
        # Filter sessions by day (case-insensitive)
        filtered_sessions = [
            session for session in all_sessions
            if session.day and session.day.lower() == day.lower()
        ]
        
        return filtered_sessions
