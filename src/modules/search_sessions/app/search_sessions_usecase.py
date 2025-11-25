from typing import List, Optional, Tuple
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.helpers.errors.domain_errors import EntityError


class SearchSessionsUsecase:
    
    def __init__(self, repo: ISessionRepository):
        self.repo = repo
    
    def __call__(
        self,
        day: Optional[str] = None,
        venue: Optional[str] = None,
        level: Optional[int] = None,
        keywords: Optional[str] = None,
        speaker: Optional[str] = None,
        session_type: Optional[str] = None,
        page_size: int = 50,
        last_evaluated_key: Optional[str] = None
    ) -> Tuple[List[Session], Optional[str]]:
        """
        Search sessions with multiple filter criteria and pagination.
        
        Args:
            day: Filter by day (e.g., "Monday", "Tuesday")
            venue: Filter by venue name
            level: Filter by level value (100, 200, 300, 400)
            keywords: Space-separated keywords to search in title, abstract, topics, areas
            speaker: Filter by speaker name or company (case-insensitive, partial match)
            session_type: Filter by session type (case-insensitive, partial match)
            page_size: Maximum results per page (1-100, default 50)
            last_evaluated_key: Pagination token from previous request
            
        Returns:
            Tuple of (sessions list, next_page_token)
            
        Raises:
            EntityError: If parameters are invalid
        """
        # Validate day values (valid day names)
        if day is not None:
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day not in valid_days:
                raise EntityError("day")
        
        # Validate venue values (non-empty strings)
        if venue is not None:
            if not isinstance(venue, str) or len(venue.strip()) == 0:
                raise EntityError("venue")
        
        # Validate level values (100, 200, 300, 400)
        if level is not None:
            valid_levels = [100, 200, 300, 400]
            if level not in valid_levels:
                raise EntityError("level")
        
        # Validate speaker values (non-empty strings)
        if speaker is not None:
            if not isinstance(speaker, str) or len(speaker.strip()) == 0:
                raise EntityError("speaker")
        
        # Validate session_type values (non-empty strings)
        if session_type is not None:
            if not isinstance(session_type, str) or len(session_type.strip()) == 0:
                raise EntityError("session_type")
        
        # Validate page_size (1-100, default 50)
        if not isinstance(page_size, int):
            raise EntityError("page_size")
        if page_size < 1 or page_size > 100:
            raise EntityError("page_size")
        
        # Call repository search method
        return self.repo.search_sessions(
            day=day,
            venue=venue,
            level=level,
            keywords=keywords,
            speaker=speaker,
            session_type=session_type,
            page_size=page_size,
            last_evaluated_key=last_evaluated_key
        )
