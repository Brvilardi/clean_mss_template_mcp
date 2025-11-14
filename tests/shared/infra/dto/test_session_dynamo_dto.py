from src.shared.domain.entities.session import Session
from src.shared.infra.dto.session_dynamo_dto import SessionDynamoDTO
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SessionDynamoDTO:
    def test_from_entity(self):
        repo = SessionRepositoryMock()
        
        session_dto = SessionDynamoDTO.from_entity(session=repo.sessions[0])
        
        expected_session_dto = SessionDynamoDTO(
            session_id=repo.sessions[0].session_id,
            short_id=repo.sessions[0].short_id,
            title=repo.sessions[0].title,
            abstract=repo.sessions[0].abstract,
            session_type=repo.sessions[0].session_type,
            venue_name=repo.sessions[0].venue_name,
            venue_room=repo.sessions[0].venue_room,
            start_datetime=repo.sessions[0].start_datetime,
            end_datetime=repo.sessions[0].end_datetime,
            day=repo.sessions[0].day,
            speakers=repo.sessions[0].speakers,
            topics=repo.sessions[0].topics,
            areas_of_interest=repo.sessions[0].areas_of_interest,
            level=repo.sessions[0].level,
            level_value=repo.sessions[0].level_value,
            features=repo.sessions[0].features,
            seat_capacity=repo.sessions[0].seat_capacity
        )
        
        assert session_dto == expected_session_dto

    def test_to_dynamo(self):
        repo = SessionRepositoryMock()
        
        session_dto = SessionDynamoDTO.from_entity(session=repo.sessions[0])
        
        session_dynamo = session_dto.to_dynamo()
        
        expected_dict = {
            "entity": "session",
            "session_id": repo.sessions[0].session_id,
            "short_id": repo.sessions[0].short_id,
            "title": repo.sessions[0].title,
            "abstract": repo.sessions[0].abstract,
            "session_type": repo.sessions[0].session_type,
            "venue_name": repo.sessions[0].venue_name,
            "venue_room": repo.sessions[0].venue_room,
            "start_datetime": repo.sessions[0].start_datetime,
            "end_datetime": repo.sessions[0].end_datetime,
            "day": repo.sessions[0].day,
            "speakers": repo.sessions[0].speakers,
            "topics": repo.sessions[0].topics,
            "areas_of_interest": repo.sessions[0].areas_of_interest,
            "level": repo.sessions[0].level,
            "level_value": repo.sessions[0].level_value,
            "features": repo.sessions[0].features,
            "seat_capacity": repo.sessions[0].seat_capacity
        }
        
        assert session_dynamo == expected_dict
        assert session_dynamo["entity"] == "session"

    def test_from_dynamo(self):
        dynamo_dict = {
            "entity": "session",
            "session_id": "1753651605588001kjXl",
            "short_id": "TNC301",
            "title": "Accelerate VMware Migration with AWS Transform",
            "abstract": "This bootcamp is for AWS Partners only.",
            "session_type": "Bootcamp",
            "venue_name": "Mandalay Bay",
            "venue_room": "Level 2 South | Breakers K",
            "start_datetime": "2025-12-04T21:00:00.000Z",
            "end_datetime": "2025-12-05T01:00:00.000Z",
            "day": "Thursday",
            "speakers": [{"displayName": "Parvesh Chopra", "company": "AWS"}],
            "topics": ["Artificial Intelligence", "Migration"],
            "areas_of_interest": ["Training & Certification"],
            "level": "300 – Advanced",
            "level_value": 300,
            "features": ["Hands-on"],
            "seat_capacity": 126
        }
        
        session_dto = SessionDynamoDTO.from_dynamo(session_data=dynamo_dict)
        
        expected_session_dto = SessionDynamoDTO(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only.",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Parvesh Chopra", "company": "AWS"}],
            topics=["Artificial Intelligence", "Migration"],
            areas_of_interest=["Training & Certification"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=126
        )
        
        assert session_dto == expected_session_dto

    def test_to_entity(self):
        repo = SessionRepositoryMock()
        
        session_dto = SessionDynamoDTO.from_entity(session=repo.sessions[0])
        
        session = session_dto.to_entity()
        
        assert session.session_id == repo.sessions[0].session_id
        assert session.short_id == repo.sessions[0].short_id
        assert session.title == repo.sessions[0].title
        assert session.abstract == repo.sessions[0].abstract
        assert session.session_type == repo.sessions[0].session_type
        assert session.venue_name == repo.sessions[0].venue_name
        assert session.venue_room == repo.sessions[0].venue_room
        assert session.start_datetime == repo.sessions[0].start_datetime
        assert session.end_datetime == repo.sessions[0].end_datetime
        assert session.day == repo.sessions[0].day
        assert session.speakers == repo.sessions[0].speakers
        assert session.topics == repo.sessions[0].topics
        assert session.areas_of_interest == repo.sessions[0].areas_of_interest
        assert session.level == repo.sessions[0].level
        assert session.level_value == repo.sessions[0].level_value
        assert session.features == repo.sessions[0].features
        assert session.seat_capacity == repo.sessions[0].seat_capacity

    def test_from_dynamo_to_entity(self):
        dynamo_dict = {
            "entity": "session",
            "session_id": "1753651605588002abCD",
            "short_id": "SVS201",
            "title": "Building Serverless Applications with AWS Lambda",
            "abstract": "Learn the fundamentals of building serverless applications.",
            "session_type": "Breakout Session",
            "venue_name": "Venetian",
            "venue_room": "Level 3 | Marcello 4405",
            "start_datetime": "2025-12-05T14:00:00.000Z",
            "end_datetime": "2025-12-05T15:00:00.000Z",
            "day": "Friday",
            "speakers": [
                {"displayName": "Jane Smith", "company": "AWS"},
                {"displayName": "John Doe", "company": "AWS"}
            ],
            "topics": ["Serverless", "Compute"],
            "areas_of_interest": ["Application Development"],
            "level": "200 – Intermediate",
            "level_value": 200,
            "features": ["Interactive"],
            "seat_capacity": 250
        }
        
        session_dto = SessionDynamoDTO.from_dynamo(session_data=dynamo_dict)
        session = session_dto.to_entity()
        
        expected_session = Session(
            session_id="1753651605588002abCD",
            short_id="SVS201",
            title="Building Serverless Applications with AWS Lambda",
            abstract="Learn the fundamentals of building serverless applications.",
            session_type="Breakout Session",
            venue_name="Venetian",
            venue_room="Level 3 | Marcello 4405",
            start_datetime="2025-12-05T14:00:00.000Z",
            end_datetime="2025-12-05T15:00:00.000Z",
            day="Friday",
            speakers=[
                {"displayName": "Jane Smith", "company": "AWS"},
                {"displayName": "John Doe", "company": "AWS"}
            ],
            topics=["Serverless", "Compute"],
            areas_of_interest=["Application Development"],
            level="200 – Intermediate",
            level_value=200,
            features=["Interactive"],
            seat_capacity=250
        )
        
        assert session.session_id == expected_session.session_id
        assert session.short_id == expected_session.short_id
        assert session.title == expected_session.title
        assert session.level_value == expected_session.level_value

    def test_from_entity_to_dynamo(self):
        repo = SessionRepositoryMock()
        
        session_dto = SessionDynamoDTO.from_entity(session=repo.sessions[1])
        session_dynamo = session_dto.to_dynamo()
        
        expected_dict = {
            "entity": "session",
            "session_id": repo.sessions[1].session_id,
            "short_id": repo.sessions[1].short_id,
            "title": repo.sessions[1].title,
            "abstract": repo.sessions[1].abstract,
            "session_type": repo.sessions[1].session_type,
            "venue_name": repo.sessions[1].venue_name,
            "venue_room": repo.sessions[1].venue_room,
            "start_datetime": repo.sessions[1].start_datetime,
            "end_datetime": repo.sessions[1].end_datetime,
            "day": repo.sessions[1].day,
            "speakers": repo.sessions[1].speakers,
            "topics": repo.sessions[1].topics,
            "areas_of_interest": repo.sessions[1].areas_of_interest,
            "level": repo.sessions[1].level,
            "level_value": repo.sessions[1].level_value,
            "features": repo.sessions[1].features,
            "seat_capacity": repo.sessions[1].seat_capacity
        }
        
        assert session_dynamo == expected_dict
        assert session_dynamo["entity"] == "session"

    def test_entity_attribute_always_session(self):
        """Test that entity attribute is always 'session' in DynamoDB format"""
        repo = SessionRepositoryMock()
        
        for session in repo.sessions:
            session_dto = SessionDynamoDTO.from_entity(session=session)
            session_dynamo = session_dto.to_dynamo()
            
            assert session_dynamo["entity"] == "session"
