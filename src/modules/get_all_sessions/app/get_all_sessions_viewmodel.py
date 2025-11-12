from typing import List

from src.shared.domain.entities.session import Session


class SessionViewmodel:
    def __init__(self, session: Session):
        self.session_id = session.session_id
        self.short_id = session.short_id
        self.title = session.title
        self.abstract = session.abstract
        self.session_type = session.session_type
        self.venue_name = session.venue_name
        self.venue_room = session.venue_room
        self.start_datetime = session.start_datetime
        self.end_datetime = session.end_datetime
        self.day = session.day
        self.speakers = session.speakers
        self.topics = session.topics
        self.areas_of_interest = session.areas_of_interest
        self.level = session.level
        self.level_value = session.level_value
        self.features = session.features
        self.seat_capacity = session.seat_capacity

    def to_dict(self):
        return {
            'session_id': self.session_id,
            'short_id': self.short_id,
            'title': self.title,
            'abstract': self.abstract,
            'session_type': self.session_type,
            'venue_name': self.venue_name,
            'venue_room': self.venue_room,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'day': self.day,
            'speakers': self.speakers,
            'topics': self.topics,
            'areas_of_interest': self.areas_of_interest,
            'level': self.level,
            'level_value': self.level_value,
            'features': self.features,
            'seat_capacity': self.seat_capacity
        }


class GetAllSessionsViewmodel:
    def __init__(self, sessions_list: List[Session]):
        self.sessions_viewmodel_list = [SessionViewmodel(session) for session in sessions_list]

    def to_dict(self):
        return {
            "sessions": [viewmodel.to_dict() for viewmodel in self.sessions_viewmodel_list],
            "count": len(self.sessions_viewmodel_list)
        }
