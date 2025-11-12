import json

from src.shared.domain.entities.session import Session
from src.shared.infra.dto.session_sqlite_dto import SessionSQLiteDTO


class Test_SessionSQLiteDTO:
    def test_from_entity(self):
        # Create a sample session entity
        session = Session(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Parvesh Chopra", "company": "AWS"}],
            topics=["Artificial Intelligence", "Machine Learning"],
            areas_of_interest=["Training & Certification"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=126
        )

        # Convert to DTO
        dto = SessionSQLiteDTO.from_entity(session)

        # Verify all fields are correctly converted
        assert dto.session_id == "1753651605588001kjXl"
        assert dto.short_id == "TNC301"
        assert dto.title == "Accelerate VMware Migration with AWS Transform"
        assert dto.abstract == "This bootcamp is for AWS Partners only"
        assert dto.session_type == "Bootcamp"
        assert dto.venue_name == "Mandalay Bay"
        assert dto.venue_room == "Level 2 South | Breakers K"
        assert dto.start_datetime == "2025-12-04T21:00:00.000Z"
        assert dto.end_datetime == "2025-12-05T01:00:00.000Z"
        assert dto.day == "Thursday"
        assert dto.level == "300 – Advanced"
        assert dto.level_value == 300
        assert dto.seat_capacity == 126

        # Verify JSON fields
        assert dto.speakers_json == json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}])
        assert dto.topics_json == json.dumps(["Artificial Intelligence", "Machine Learning"])
        assert dto.areas_of_interest_json == json.dumps(["Training & Certification"])
        assert dto.features_json == json.dumps(["Hands-on"])

    def test_to_entity(self):
        # Create a DTO
        dto = SessionSQLiteDTO(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers_json=json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}]),
            topics_json=json.dumps(["Artificial Intelligence", "Machine Learning"]),
            areas_of_interest_json=json.dumps(["Training & Certification"]),
            level="300 – Advanced",
            level_value=300,
            features_json=json.dumps(["Hands-on"]),
            seat_capacity=126
        )

        # Convert to entity
        session = dto.to_entity()

        # Verify all fields
        assert session.session_id == "1753651605588001kjXl"
        assert session.short_id == "TNC301"
        assert session.title == "Accelerate VMware Migration with AWS Transform"
        assert session.abstract == "This bootcamp is for AWS Partners only"
        assert session.session_type == "Bootcamp"
        assert session.venue_name == "Mandalay Bay"
        assert session.venue_room == "Level 2 South | Breakers K"
        assert session.start_datetime == "2025-12-04T21:00:00.000Z"
        assert session.end_datetime == "2025-12-05T01:00:00.000Z"
        assert session.day == "Thursday"
        assert session.level == "300 – Advanced"
        assert session.level_value == 300
        assert session.seat_capacity == 126

        # Verify deserialized lists
        assert session.speakers == [{"displayName": "Parvesh Chopra", "company": "AWS"}]
        assert session.topics == ["Artificial Intelligence", "Machine Learning"]
        assert session.areas_of_interest == ["Training & Certification"]
        assert session.features == ["Hands-on"]

    def test_to_sqlite(self):
        # Create a DTO
        dto = SessionSQLiteDTO(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers_json=json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}]),
            topics_json=json.dumps(["Artificial Intelligence"]),
            areas_of_interest_json=json.dumps(["Training & Certification"]),
            level="300 – Advanced",
            level_value=300,
            features_json=json.dumps(["Hands-on"]),
            seat_capacity=126
        )

        # Convert to SQLite dict
        sqlite_dict = dto.to_sqlite()

        # Verify the dict structure
        expected_dict = {
            "session_id": "1753651605588001kjXl",
            "short_id": "TNC301",
            "title": "Accelerate VMware Migration with AWS Transform",
            "abstract": "This bootcamp is for AWS Partners only",
            "session_type": "Bootcamp",
            "venue_name": "Mandalay Bay",
            "venue_room": "Level 2 South | Breakers K",
            "start_datetime": "2025-12-04T21:00:00.000Z",
            "end_datetime": "2025-12-05T01:00:00.000Z",
            "day": "Thursday",
            "speakers_json": json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}]),
            "topics_json": json.dumps(["Artificial Intelligence"]),
            "areas_of_interest_json": json.dumps(["Training & Certification"]),
            "level": "300 – Advanced",
            "level_value": 300,
            "features_json": json.dumps(["Hands-on"]),
            "seat_capacity": 126
        }

        assert sqlite_dict == expected_dict

    def test_from_sqlite(self):
        # Create a SQLite row dict
        sqlite_row = {
            "session_id": "1753651605588001kjXl",
            "short_id": "TNC301",
            "title": "Accelerate VMware Migration with AWS Transform",
            "abstract": "This bootcamp is for AWS Partners only",
            "session_type": "Bootcamp",
            "venue_name": "Mandalay Bay",
            "venue_room": "Level 2 South | Breakers K",
            "start_datetime": "2025-12-04T21:00:00.000Z",
            "end_datetime": "2025-12-05T01:00:00.000Z",
            "day": "Thursday",
            "speakers_json": json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}]),
            "topics_json": json.dumps(["Artificial Intelligence"]),
            "areas_of_interest_json": json.dumps(["Training & Certification"]),
            "level": "300 – Advanced",
            "level_value": 300,
            "features_json": json.dumps(["Hands-on"]),
            "seat_capacity": 126
        }

        # Convert from SQLite
        dto = SessionSQLiteDTO.from_sqlite(sqlite_row)

        # Verify all fields
        assert dto.session_id == "1753651605588001kjXl"
        assert dto.short_id == "TNC301"
        assert dto.title == "Accelerate VMware Migration with AWS Transform"
        assert dto.abstract == "This bootcamp is for AWS Partners only"
        assert dto.session_type == "Bootcamp"
        assert dto.venue_name == "Mandalay Bay"
        assert dto.venue_room == "Level 2 South | Breakers K"
        assert dto.start_datetime == "2025-12-04T21:00:00.000Z"
        assert dto.end_datetime == "2025-12-05T01:00:00.000Z"
        assert dto.day == "Thursday"
        assert dto.speakers_json == json.dumps([{"displayName": "Parvesh Chopra", "company": "AWS"}])
        assert dto.topics_json == json.dumps(["Artificial Intelligence"])
        assert dto.areas_of_interest_json == json.dumps(["Training & Certification"])
        assert dto.level == "300 – Advanced"
        assert dto.level_value == 300
        assert dto.features_json == json.dumps(["Hands-on"])
        assert dto.seat_capacity == 126

    def test_json_list_handling_speakers(self):
        # Test with multiple speakers
        speakers = [
            {"displayName": "John Doe", "company": "AWS"},
            {"displayName": "Jane Smith", "company": "Amazon"}
        ]
        
        session = Session(
            session_id="test123",
            short_id="TST101",
            title="Test Session",
            abstract="Test abstract",
            session_type="Workshop",
            venue_name="Test Venue",
            venue_room="Room A",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Monday",
            speakers=speakers,
            topics=["Topic1"],
            areas_of_interest=["Area1"],
            level="200 – Intermediate",
            level_value=200,
            features=["Feature1"],
            seat_capacity=50
        )

        dto = SessionSQLiteDTO.from_entity(session)
        reconstructed_session = dto.to_entity()

        assert reconstructed_session.speakers == speakers

    def test_json_list_handling_topics(self):
        # Test with multiple topics
        topics = ["AI", "ML", "Deep Learning", "Computer Vision"]
        
        session = Session(
            session_id="test123",
            short_id="TST101",
            title="Test Session",
            abstract="Test abstract",
            session_type="Workshop",
            venue_name="Test Venue",
            venue_room="Room A",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Monday",
            speakers=[{"displayName": "Test", "company": "AWS"}],
            topics=topics,
            areas_of_interest=["Area1"],
            level="200 – Intermediate",
            level_value=200,
            features=["Feature1"],
            seat_capacity=50
        )

        dto = SessionSQLiteDTO.from_entity(session)
        reconstructed_session = dto.to_entity()

        assert reconstructed_session.topics == topics

    def test_json_list_handling_areas_of_interest(self):
        # Test with multiple areas of interest
        areas = ["Security", "Compliance", "Governance", "Best Practices"]
        
        session = Session(
            session_id="test123",
            short_id="TST101",
            title="Test Session",
            abstract="Test abstract",
            session_type="Workshop",
            venue_name="Test Venue",
            venue_room="Room A",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Monday",
            speakers=[{"displayName": "Test", "company": "AWS"}],
            topics=["Topic1"],
            areas_of_interest=areas,
            level="200 – Intermediate",
            level_value=200,
            features=["Feature1"],
            seat_capacity=50
        )

        dto = SessionSQLiteDTO.from_entity(session)
        reconstructed_session = dto.to_entity()

        assert reconstructed_session.areas_of_interest == areas

    def test_json_list_handling_features(self):
        # Test with multiple features
        features = ["Hands-on", "Interactive", "Demo", "Q&A"]
        
        session = Session(
            session_id="test123",
            short_id="TST101",
            title="Test Session",
            abstract="Test abstract",
            session_type="Workshop",
            venue_name="Test Venue",
            venue_room="Room A",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Monday",
            speakers=[{"displayName": "Test", "company": "AWS"}],
            topics=["Topic1"],
            areas_of_interest=["Area1"],
            level="200 – Intermediate",
            level_value=200,
            features=features,
            seat_capacity=50
        )

        dto = SessionSQLiteDTO.from_entity(session)
        reconstructed_session = dto.to_entity()

        assert reconstructed_session.features == features

    def test_from_entity_to_sqlite_roundtrip(self):
        # Test complete roundtrip: Entity -> DTO -> SQLite dict -> DTO -> Entity
        original_session = Session(
            session_id="1753651605588001kjXl",
            short_id="TNC301",
            title="Accelerate VMware Migration with AWS Transform",
            abstract="This bootcamp is for AWS Partners only",
            session_type="Bootcamp",
            venue_name="Mandalay Bay",
            venue_room="Level 2 South | Breakers K",
            start_datetime="2025-12-04T21:00:00.000Z",
            end_datetime="2025-12-05T01:00:00.000Z",
            day="Thursday",
            speakers=[{"displayName": "Parvesh Chopra", "company": "AWS"}],
            topics=["Artificial Intelligence", "Machine Learning"],
            areas_of_interest=["Training & Certification"],
            level="300 – Advanced",
            level_value=300,
            features=["Hands-on"],
            seat_capacity=126
        )

        # Entity -> DTO -> SQLite dict
        dto1 = SessionSQLiteDTO.from_entity(original_session)
        sqlite_dict = dto1.to_sqlite()

        # SQLite dict -> DTO -> Entity
        dto2 = SessionSQLiteDTO.from_sqlite(sqlite_dict)
        reconstructed_session = dto2.to_entity()

        # Verify all fields match
        assert reconstructed_session.session_id == original_session.session_id
        assert reconstructed_session.short_id == original_session.short_id
        assert reconstructed_session.title == original_session.title
        assert reconstructed_session.abstract == original_session.abstract
        assert reconstructed_session.session_type == original_session.session_type
        assert reconstructed_session.venue_name == original_session.venue_name
        assert reconstructed_session.venue_room == original_session.venue_room
        assert reconstructed_session.start_datetime == original_session.start_datetime
        assert reconstructed_session.end_datetime == original_session.end_datetime
        assert reconstructed_session.day == original_session.day
        assert reconstructed_session.speakers == original_session.speakers
        assert reconstructed_session.topics == original_session.topics
        assert reconstructed_session.areas_of_interest == original_session.areas_of_interest
        assert reconstructed_session.level == original_session.level
        assert reconstructed_session.level_value == original_session.level_value
        assert reconstructed_session.features == original_session.features
        assert reconstructed_session.seat_capacity == original_session.seat_capacity
