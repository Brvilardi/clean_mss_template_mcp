from typing import List, Optional

from src.shared.domain.entities.session import Session


class GetAllSessionsPaginatedViewmodel:
    """
    View model for paginated sessions response.
    """
    
    def __init__(
        self,
        sessions: List[Session],
        page_size: int,
        next_token: Optional[str]
    ):
        self.sessions = sessions
        self.page_size = page_size
        self.next_token = next_token
    
    def to_dict(self) -> dict:
        """
        Converts view model to dictionary with pagination metadata.
        
        Returns:
            Dictionary with sessions array and pagination metadata
        """
        response = {
            "sessions": [
                {
                    "session_id": s.session_id,
                    "short_id": s.short_id,
                    "title": s.title,
                    "abstract": s.abstract,
                    "session_type": s.session_type,
                    "venue_name": s.venue_name,
                    "venue_room": s.venue_room,
                    "start_datetime": s.start_datetime,
                    "end_datetime": s.end_datetime,
                    "day": s.day,
                    "speakers": s.speakers,
                    "topics": s.topics,
                    "areas_of_interest": s.areas_of_interest,
                    "level": s.level,
                    "level_value": s.level_value,
                    "features": s.features,
                    "seat_capacity": s.seat_capacity
                }
                for s in self.sessions
            ],
            "count": len(self.sessions),
            "page_size": self.page_size,
            "has_more": self.next_token is not None
        }
        
        # Only include last_evaluated_key if there are more results
        if self.next_token:
            response["last_evaluated_key"] = self.next_token
        
        return response
