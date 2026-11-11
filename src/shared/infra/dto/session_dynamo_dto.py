from typing import List, Dict

from src.shared.domain.entities.session import Session


class SessionDynamoDTO:
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
        self.speakers = speakers
        self.topics = topics
        self.areas_of_interest = areas_of_interest
        self.level = level
        self.level_value = level_value
        self.features = features
        self.seat_capacity = seat_capacity

    @staticmethod
    def from_entity(session: Session) -> "SessionDynamoDTO":
        """
        Parse data from Session to SessionDynamoDTO
        """
        return SessionDynamoDTO(
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
            speakers=session.speakers,
            topics=session.topics,
            areas_of_interest=session.areas_of_interest,
            level=session.level,
            level_value=session.level_value,
            features=session.features,
            seat_capacity=session.seat_capacity
        )

    def to_dynamo(self) -> dict:
        """
        Parse data from SessionDynamoDTO to dict compatible with DynamoDB
        """
        return {
            "entity": "session",
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
            "speakers": self.speakers,
            "topics": self.topics,
            "areas_of_interest": self.areas_of_interest,
            "level": self.level,
            "level_value": self.level_value,
            "features": self.features,
            "seat_capacity": self.seat_capacity
        }

    @staticmethod
    def from_dynamo(session_data: dict) -> "SessionDynamoDTO":
        """
        Parse data from DynamoDB to SessionDynamoDTO
        @param session_data: dict from DynamoDB
        """
        return SessionDynamoDTO(
            session_id=session_data["session_id"],
            short_id=session_data["short_id"],
            title=session_data["title"],
            abstract=session_data["abstract"],
            session_type=session_data["session_type"],
            venue_name=session_data["venue_name"],
            venue_room=session_data["venue_room"],
            start_datetime=session_data["start_datetime"],
            end_datetime=session_data["end_datetime"],
            day=session_data["day"],
            speakers=session_data["speakers"],
            topics=session_data["topics"],
            areas_of_interest=session_data["areas_of_interest"],
            level=session_data["level"],
            level_value=int(session_data["level_value"]),
            features=session_data["features"],
            seat_capacity=int(session_data["seat_capacity"])
        )

    def to_entity(self) -> Session:
        """
        Parse data from SessionDynamoDTO to Session
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
            speakers=self.speakers,
            topics=self.topics,
            areas_of_interest=self.areas_of_interest,
            level=self.level,
            level_value=self.level_value,
            features=self.features,
            seat_capacity=self.seat_capacity
        )

    def __repr__(self):
        return (
            f"SessionDynamoDTO(session_id={self.session_id}, short_id={self.short_id}, "
            f"title={self.title}, session_type={self.session_type}, "
            f"start_datetime={self.start_datetime}, level_value={self.level_value})"
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
