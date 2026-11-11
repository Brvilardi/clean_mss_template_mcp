from typing import List

from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class GetAllSessionsUsecase:
    """
    Use case for retrieving all sessions from the repository.
    """

    def __init__(self, repo: ISessionRepository):
        self.repo = repo

    def __call__(self) -> List[Session]:
        """
        Retrieves all sessions from the repository.
        
        Returns:
            List of Session entities
        """
        return self.repo.get_all_sessions()
