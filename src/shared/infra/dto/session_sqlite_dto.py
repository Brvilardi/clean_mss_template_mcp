import json
from typing import List, Dict

from src.shared.domain.entities.session import Session


class SessionSQLiteDTO:
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
    speakers_json: str
    topics_json: str
    areas_of_interest_json: str
    level: str
    level_value: int
    features_json: str
    seat_capacity: int

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
        speakers_json: str,
        topics_json: str,
        areas_of_interest_json: str,
        level: str,
        level_value: int,
        features_json: str,
        seat_capacity: int
    ):
        self.session_id = session_id
        self.short_id = short_id
        self.title = title
        self.abstract = abstract
        self.session_type = session_type
        self.venue_name = venue_name
        self.venue_room = venue_room
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.day = day
        self.speakers_json = speakers_json
        self.topics_json = topics_json
        self.areas_of_interest_json = areas_of_interest_json
        self.level = level
        self.level_value = level_value
        self.features_json = features_json
        self.seat_capacity = seat_capacity

    @staticmethod
    def from_entity(session: Session) -> "SessionSQLiteDTO":
        """
        Parse data from Session entity to SessionSQLiteDTO.
        
        Args:
            session: Session entity to convert
            
        Returns:
            SessionSQLiteDTO instance
        """
        return SessionSQLiteDTO(
            session_id=session.session_id,
            short_id=session.short_id,
            title=session.title,
            abstract=session.abstract,
            session_type=session.session_type,
            venue_name=session.venue_name,
            venue_room=session.venue_room,
            start_datetime=session.start_datetime,
            end_datetime=session.end_datetime,
            day=session.day,
            speakers_json=json.dumps(session.speakers),
            topics_json=json.dumps(session.topics),
            areas_of_interest_json=json.dumps(session.areas_of_interest),
            level=session.level,
            level_value=session.level_value,
            features_json=json.dumps(session.features),
            seat_capacity=session.seat_capacity
        )

    def to_entity(self) -> Session:
        """
        Parse data from SessionSQLiteDTO to Session entity.
        
        Returns:
            Session entity instance
        """
        return Session(
            session_id=self.session_id,
            short_id=self.short_id,
            title=self.title,
            abstract=self.abstract,
            session_type=self.session_type,
            venue_name=self.venue_name,
            venue_room=self.venue_room,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            day=self.day,
            speakers=json.loads(self.speakers_json),
            topics=json.loads(self.topics_json),
            areas_of_interest=json.loads(self.areas_of_interest_json),
            level=self.level,
            level_value=self.level_value,
            features=json.loads(self.features_json),
            seat_capacity=self.seat_capacity
        )

    def to_sqlite(self) -> dict:
        """
        Parse data from SessionSQLiteDTO to dict for SQLite insertion.
        
        Returns:
            Dictionary with column names as keys
        """
        return {
            "session_id": self.session_id,
            "short_id": self.short_id,
            "title": self.title,
            "abstract": self.abstract,
            "session_type": self.session_type,
            "venue_name": self.venue_name,
            "venue_room": self.venue_room,
            "start_datetime": self.start_datetime,
            "end_datetime": self.end_datetime,
            "day": self.day,
            "speakers_json": self.speakers_json,
            "topics_json": self.topics_json,
            "areas_of_interest_json": self.areas_of_interest_json,
            "level": self.level,
            "level_value": self.level_value,
            "features_json": self.features_json,
            "seat_capacity": self.seat_capacity
        }

    @staticmethod
    def from_sqlite(data: dict) -> "SessionSQLiteDTO":
        """
        Parse data from SQLite row to SessionSQLiteDTO.
        
        Args:
            data: Dictionary from SQLite row
            
        Returns:
            SessionSQLiteDTO instance
        """
        return SessionSQLiteDTO(
            session_id=data["session_id"],
            short_id=data["short_id"],
            title=data["title"],
            abstract=data["abstract"],
            session_type=data["session_type"],
            venue_name=data["venue_name"],
            venue_room=data["venue_room"],
            start_datetime=data["start_datetime"],
            end_datetime=data["end_datetime"],
            day=data["day"],
            speakers_json=data["speakers_json"],
            topics_json=data["topics_json"],
            areas_of_interest_json=data["areas_of_interest_json"],
            level=data["level"],
            level_value=data["level_value"],
            features_json=data["features_json"],
            seat_capacity=data["seat_capacity"]
        )

    def __repr__(self):
        return (
            f"SessionSQLiteDTO(session_id={self.session_id}, short_id={self.short_id}, "
            f"title={self.title}, session_type={self.session_type})"
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
