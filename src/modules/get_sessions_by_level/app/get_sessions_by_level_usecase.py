from typing import List
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.helpers.errors.domain_errors import EntityError


class GetSessionsByLevelUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(self, level_values: List[int]) -> List[Session]:
        """
        Retrieves sessions filtered by level_values.
        
        Args:
            level_values: List of difficulty levels (100, 200, 300, or 400)
            
        Returns:
            List of Session entities matching any of the level_values
            
        Raises:
            EntityError: If any level_value is not one of 100, 200, 300, 400
        """
        # Validate level_values
        valid_levels = [100, 200, 300, 400]
        for level_value in level_values:
            if level_value not in valid_levels:
                raise EntityError("level_values")
        
        # Get sessions for each level and combine
        all_sessions = []
        for level_value in level_values:
            sessions = self.repo.get_sessions_by_level(level_value)
            all_sessions.extend(sessions)
        
        # Remove duplicates and sort by start_datetime
        unique_sessions = list({session.session_id: session for session in all_sessions}.values())
        unique_sessions.sort(key=lambda s: s.start_datetime)
        
        return unique_sessions
