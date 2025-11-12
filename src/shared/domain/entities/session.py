import abc
from datetime import datetime
from typing import List, Dict

from src.shared.helpers.errors.domain_errors import EntityError


class Session(abc.ABC):
    session_id: str
    short_id: str
    title: str
    abstract: str
    session_type: str
    venue_name: str
    venue_room: str
    start_datetime: str
    end_datetime: str
    day: str
    speakers: List[Dict[str, str]]
    topics: List[str]
    areas_of_interest: List[str]
    level: str
    level_value: int
    features: List[str]
    seat_capacity: int
    
    MIN_TITLE_LENGTH = 3

    def __init__(
        self,
        session_id: str,
        short_id: str,
        title: str,
        abstract: str,
        session_type: str,
        venue_name: str,
        venue_room: str,
        start_datetime: str,
        end_datetime: str,
        day: str,
        speakers: List[Dict[str, str]],
        topics: List[str],
        areas_of_interest: List[str],
        level: str,
        level_value: int,
        features: List[str],
        seat_capacity: int
    ):
        if not Session.validate_session_id(session_id):
            raise EntityError("session_id")
        self.session_id = session_id

        if not Session.validate_session_id(short_id):
            raise EntityError("short_id")
        self.short_id = short_id

        if not Session.validate_title(title):
            raise EntityError("title")
        self.title = title

        if abstract is None or type(abstract) != str:
            raise EntityError("abstract")
        self.abstract = abstract

        if not Session.validate_session_type(session_type):
            raise EntityError("session_type")
        self.session_type = session_type

        if venue_name is None or type(venue_name) != str:
            raise EntityError("venue_name")
        self.venue_name = venue_name

        if venue_room is None or type(venue_room) != str:
            raise EntityError("venue_room")
        self.venue_room = venue_room

        if not Session.validate_datetime(start_datetime):
            raise EntityError("start_datetime")
        self.start_datetime = start_datetime

        if not Session.validate_datetime(end_datetime):
            raise EntityError("end_datetime")
        self.end_datetime = end_datetime

        if day is None or type(day) != str:
            raise EntityError("day")
        self.day = day

        if speakers is None or type(speakers) != list:
            raise EntityError("speakers")
        self.speakers = speakers

        if topics is None or type(topics) != list:
            raise EntityError("topics")
        self.topics = topics

        if areas_of_interest is None or type(areas_of_interest) != list:
            raise EntityError("areas_of_interest")
        self.areas_of_interest = areas_of_interest

        if level is None or type(level) != str:
            raise EntityError("level")
        self.level = level

        if not Session.validate_level_value(level_value):
            raise EntityError("level_value")
        self.level_value = level_value

        if features is None or type(features) != list:
            raise EntityError("features")
        self.features = features

        if type(seat_capacity) != int or seat_capacity < 0:
            raise EntityError("seat_capacity")
        self.seat_capacity = seat_capacity

    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validates session_id is a non-empty string.
        
        Args:
            session_id: The session identifier to validate
            
        Returns:
            True if valid, False otherwise
        """
        if session_id is None:
            return False
        if type(session_id) != str:
            return False
        if len(session_id) == 0:
            return False
        return True

    @staticmethod
    def validate_title(title: str) -> bool:
        """
        Validates title is a non-empty string with minimum length.
        
        Args:
            title: The session title to validate
            
        Returns:
            True if valid, False otherwise
        """
        if title is None:
            return False
        if type(title) != str:
            return False
        if len(title) < Session.MIN_TITLE_LENGTH:
            return False
        return True

    @staticmethod
    def validate_datetime(datetime_str: str) -> bool:
        """
        Validates datetime string is in ISO 8601 format.
        
        Args:
            datetime_str: The datetime string to validate
            
        Returns:
            True if valid ISO 8601 format, False otherwise
        """
        if datetime_str is None:
            return False
        if type(datetime_str) != str:
            return False
        
        try:
            # Try parsing as ISO 8601 format
            datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            return False

    @staticmethod
    def validate_session_type(session_type: str) -> bool:
        """
        Validates session_type is a non-empty string.
        
        Args:
            session_type: The session type to validate
            
        Returns:
            True if valid, False otherwise
        """
        if session_type is None:
            return False
        if type(session_type) != str:
            return False
        if len(session_type) == 0:
            return False
        return True

    @staticmethod
    def validate_level_value(level_value: int) -> bool:
        """
        Validates level_value is a valid numeric level (100-400).
        
        Args:
            level_value: The numeric level to validate
            
        Returns:
            True if valid (100, 200, 300, or 400), False otherwise
        """
        if type(level_value) != int:
            return False
        if level_value not in [100, 200, 300, 400]:
            return False
        return True

    def __repr__(self):
        return (
            f"Session(session_id={self.session_id}, short_id={self.short_id}, "
            f"title={self.title}, session_type={self.session_type}, "
            f"start_datetime={self.start_datetime}, level_value={self.level_value})"
        )
