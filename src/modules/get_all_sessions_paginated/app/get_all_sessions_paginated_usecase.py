from typing import Optional, Tuple, List

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class GetAllSessionsPaginatedUsecase:
    """
    Use case for retrieving all sessions with pagination.
    """
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(
        self,
        page_size: int,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Retrieves all sessions with pagination.
        
        Args:
            page_size: Maximum number of sessions to return (1-100)
            last_evaluated_key: Base64-encoded pagination token from previous request
            
        Returns:
            Tuple of (sessions list, next_page_token)
            - sessions list: List of Session entities for the current page
            - next_page_token: Base64-encoded token for next page, None if no more results
            
        Raises:
            ValueError: If page_size is invalid or pagination token is expired/malformed
        """
        return self.repo.get_all_sessions_paginated(page_size, last_evaluated_key)
