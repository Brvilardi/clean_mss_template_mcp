from typing import List
from src.shared.domain.entities.session import Session


class GetSessionsByLevelViewmodel:
    
    def __init__(self, sessions: List[Session], level_values: List[int]):
        self.sessions = sessions
        self.level_values = level_values
    
    def to_dict(self) -> dict:
        """
        Converts the view model to a JSON-serializable dictionary.
        
        Returns:
            Dictionary with sessions array, count, and level_values
        """
        return {
            "sessions": [
                {
                    "session_id": session.session_id,
                    "short_id": session.short_id,
                    "title": session.title,
                    "abstract": session.abstract,
                    "session_type": session.session_type,
                    "venue_name": session.venue_name,
                    "venue_room": session.venue_room,
                    "start_datetime": session.start_datetime,
                    "end_datetime": session.end_datetime,
                    "day": session.day,
                    "speakers": session.speakers,
                    "topics": session.topics,
                    "areas_of_interest": session.areas_of_interest,
                    "level": session.level,
                    "level_value": session.level_value,
                    "features": session.features,
                    "seat_capacity": session.seat_capacity
                }
                for session in self.sessions
            ],
            "count": len(self.sessions),
            "level_values": self.level_values
        }
