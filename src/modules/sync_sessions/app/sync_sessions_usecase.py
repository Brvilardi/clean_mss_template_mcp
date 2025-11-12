from typing import Dict

from src.shared.domain.repositories.session_repository_interface import ISessionRepository


class SyncSessionsUsecase:
    """
    Use case for syncing session data from external API.
    
    This use case triggers the repository to fetch the latest session data
    from the external re:invent catalog API and update the local storage.
    """

    def __init__(self, repo: ISessionRepository):
        """
        Initialize the use case with a session repository.
        
        Args:
            repo: Session repository implementation
        """
        self.repo = repo

    def __call__(self) -> Dict[str, int]:
        """
        Execute the sync operation.
        
        Calls the repository's sync_sessions_from_api method to fetch
        and update session data, then calculates the total count.
        
        Returns:
            Dictionary with keys:
                - 'inserted': Number of new sessions added
                - 'updated': Number of existing sessions updated
                - 'total': Total number of sessions affected (inserted + updated)
                
        Raises:
            ConnectionError: If external API is unreachable
        """
        result = self.repo.sync_sessions_from_api()
        result["total"] = result["inserted"] + result["updated"]
        return result
