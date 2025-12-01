from typing import List, Optional, Tuple
from src.shared.domain.entities.session import Session
from src.shared.domain.repositories.session_repository_interface import ISessionRepository
from src.shared.helpers.errors.domain_errors import EntityError
from aws_lambda_powertools import Logger

logger = Logger(service="search-sessions", child=True)


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
        # Log search criteria
        logger.info(
            "Use case executing search",
            extra={
                "search_criteria": {
                    "day": day,
                    "venue": venue,
                    "level": level,
                    "keywords": keywords,
                    "speaker": speaker,
                    "session_type": session_type,
                    "page_size": page_size,
                    "has_pagination_token": last_evaluated_key is not None
                }
            }
        )
        
        # Validate day values (valid day names)
        if day is not None:
            valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if day not in valid_days:
                logger.warning("Invalid day value", extra={"day": day, "valid_days": valid_days})
                raise EntityError("day")
        
        # Validate venue values (non-empty strings)
        if venue is not None:
            if not isinstance(venue, str) or len(venue.strip()) == 0:
                logger.warning("Invalid venue value", extra={"venue": venue})
                raise EntityError("venue")
        
        # Validate level values (100, 200, 300, 400)
        if level is not None:
            valid_levels = [100, 200, 300, 400]
            if level not in valid_levels:
                logger.warning("Invalid level value", extra={"level": level, "valid_levels": valid_levels})
                raise EntityError("level")
        
        # Validate speaker values (non-empty strings)
        if speaker is not None:
            if not isinstance(speaker, str) or len(speaker.strip()) == 0:
                logger.warning("Invalid speaker value", extra={"speaker": speaker})
                raise EntityError("speaker")
        
        # Validate session_type values (non-empty strings)
        if session_type is not None:
            if not isinstance(session_type, str) or len(session_type.strip()) == 0:
                logger.warning("Invalid session_type value", extra={"session_type": session_type})
                raise EntityError("session_type")
        
        # Validate page_size (1-100, default 50)
        if not isinstance(page_size, int):
            logger.warning("Invalid page_size type", extra={"page_size": page_size, "type": type(page_size)})
            raise EntityError("page_size")
        if page_size < 1 or page_size > 100:
            logger.warning("Invalid page_size range", extra={"page_size": page_size, "valid_range": "1-100"})
            raise EntityError("page_size")
        
        # Call repository search method
        sessions, next_token = self.repo.search_sessions(
            day=day,
            venue=venue,
            level=level,
            keywords=keywords,
            speaker=speaker,
            session_type=session_type,
            page_size=page_size,
            last_evaluated_key=last_evaluated_key
        )
        
        # Log results summary
        logger.info(
            "Repository search completed",
            extra={
                "sessions_found": len(sessions),
                "has_next_page": next_token is not None,
                "session_ids": [s.short_id for s in sessions] if sessions else []
            }
        )
        
        return sessions, next_token
