from src.shared.domain.entities.session import Session
from src.shared.helpers.errors.domain_errors import EntityError
import pytest


class Test_Session:
    # Valid test data
    valid_session_data = {
        "session_id": "1753651605588001kjXl",
        "short_id": "TNC301",
        "title": "Accelerate VMware Migration with AWS Transform",
        "abstract": "This bootcamp is for AWS Partners only...",
        "session_type": "Bootcamp",
        "venue_name": "Mandalay Bay",
        "venue_room": "Level 2 South | Breakers K",
        "start_datetime": "2025-12-04T21:00:00.000Z",
        "end_datetime": "2025-12-05T01:00:00.000Z",
        "day": "Thursday",
        "speakers": [{"displayName": "Parvesh Chopra", "company": "AWS"}],
        "topics": ["Artificial Intelligence"],
        "areas_of_interest": ["Training & Certification"],
        "level": "300 – Advanced",
        "level_value": 300,
        "features": ["Hands-on"],
        "seat_capacity": 126
    }

    def test_session_valid(self):
        """Test creating a valid Session entity"""
        session = Session(**self.valid_session_data)
        assert session.session_id == "1753651605588001kjXl"
        assert session.title == "Accelerate VMware Migration with AWS Transform"
        assert session.level_value == 300

    # session_id validation tests
    def test_validate_session_id_valid(self):
        """Test validate_session_id with valid input"""
        assert Session.validate_session_id("1753651605588001kjXl") is True

    def test_validate_session_id_none(self):
        """Test validate_session_id with None"""
        assert Session.validate_session_id(None) is False

    def test_validate_session_id_not_string(self):
        """Test validate_session_id with non-string type"""
        assert Session.validate_session_id(123) is False

    def test_validate_session_id_empty_string(self):
        """Test validate_session_id with empty string"""
        assert Session.validate_session_id("") is False

    def test_session_id_none(self):
        """Test Session constructor with None session_id"""
        data = self.valid_session_data.copy()
        data["session_id"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_session_id_not_string(self):
        """Test Session constructor with non-string session_id"""
        data = self.valid_session_data.copy()
        data["session_id"] = 123
        with pytest.raises(EntityError):
            Session(**data)

    def test_session_id_empty_string(self):
        """Test Session constructor with empty session_id"""
        data = self.valid_session_data.copy()
        data["session_id"] = ""
        with pytest.raises(EntityError):
            Session(**data)

    # short_id validation tests
    def test_short_id_none(self):
        """Test Session constructor with None short_id"""
        data = self.valid_session_data.copy()
        data["short_id"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_short_id_not_string(self):
        """Test Session constructor with non-string short_id"""
        data = self.valid_session_data.copy()
        data["short_id"] = 123
        with pytest.raises(EntityError):
            Session(**data)

    def test_short_id_empty_string(self):
        """Test Session constructor with empty short_id"""
        data = self.valid_session_data.copy()
        data["short_id"] = ""
        with pytest.raises(EntityError):
            Session(**data)

    # title validation tests
    def test_validate_title_valid(self):
        """Test validate_title with valid input"""
        assert Session.validate_title("Valid Title") is True

    def test_validate_title_none(self):
        """Test validate_title with None"""
        assert Session.validate_title(None) is False

    def test_validate_title_not_string(self):
        """Test validate_title with non-string type"""
        assert Session.validate_title(123) is False

    def test_validate_title_too_short(self):
        """Test validate_title with string shorter than minimum length"""
        assert Session.validate_title("AB") is False

    def test_validate_title_minimum_length(self):
        """Test validate_title with exactly minimum length"""
        assert Session.validate_title("ABC") is True

    def test_title_none(self):
        """Test Session constructor with None title"""
        data = self.valid_session_data.copy()
        data["title"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_title_not_string(self):
        """Test Session constructor with non-string title"""
        data = self.valid_session_data.copy()
        data["title"] = 123
        with pytest.raises(EntityError):
            Session(**data)

    def test_title_too_short(self):
        """Test Session constructor with title shorter than minimum"""
        data = self.valid_session_data.copy()
        data["title"] = "AB"
        with pytest.raises(EntityError):
            Session(**data)

    # datetime validation tests
    def test_validate_datetime_valid_iso8601(self):
        """Test validate_datetime with valid ISO 8601 format"""
        assert Session.validate_datetime("2025-12-04T21:00:00.000Z") is True

    def test_validate_datetime_valid_without_z(self):
        """Test validate_datetime with ISO format without Z"""
        assert Session.validate_datetime("2025-12-04T21:00:00") is True

    def test_validate_datetime_none(self):
        """Test validate_datetime with None"""
        assert Session.validate_datetime(None) is False

    def test_validate_datetime_not_string(self):
        """Test validate_datetime with non-string type"""
        assert Session.validate_datetime(123) is False

    def test_validate_datetime_invalid_format(self):
        """Test validate_datetime with invalid format"""
        assert Session.validate_datetime("12/04/2025") is False

    def test_validate_datetime_empty_string(self):
        """Test validate_datetime with empty string"""
        assert Session.validate_datetime("") is False

    def test_start_datetime_none(self):
        """Test Session constructor with None start_datetime"""
        data = self.valid_session_data.copy()
        data["start_datetime"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_start_datetime_invalid_format(self):
        """Test Session constructor with invalid start_datetime format"""
        data = self.valid_session_data.copy()
        data["start_datetime"] = "12/04/2025"
        with pytest.raises(EntityError):
            Session(**data)

    def test_end_datetime_none(self):
        """Test Session constructor with None end_datetime"""
        data = self.valid_session_data.copy()
        data["end_datetime"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_end_datetime_invalid_format(self):
        """Test Session constructor with invalid end_datetime format"""
        data = self.valid_session_data.copy()
        data["end_datetime"] = "invalid-date"
        with pytest.raises(EntityError):
            Session(**data)

    # session_type validation tests
    def test_validate_session_type_valid(self):
        """Test validate_session_type with valid input"""
        assert Session.validate_session_type("Bootcamp") is True

    def test_validate_session_type_none(self):
        """Test validate_session_type with None"""
        assert Session.validate_session_type(None) is False

    def test_validate_session_type_not_string(self):
        """Test validate_session_type with non-string type"""
        assert Session.validate_session_type(123) is False

    def test_validate_session_type_empty_string(self):
        """Test validate_session_type with empty string"""
        assert Session.validate_session_type("") is False

    def test_session_type_none(self):
        """Test Session constructor with None session_type"""
        data = self.valid_session_data.copy()
        data["session_type"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_session_type_not_string(self):
        """Test Session constructor with non-string session_type"""
        data = self.valid_session_data.copy()
        data["session_type"] = 123
        with pytest.raises(EntityError):
            Session(**data)

    def test_session_type_empty_string(self):
        """Test Session constructor with empty session_type"""
        data = self.valid_session_data.copy()
        data["session_type"] = ""
        with pytest.raises(EntityError):
            Session(**data)

    # level_value validation tests
    def test_validate_level_value_100(self):
        """Test validate_level_value with 100"""
        assert Session.validate_level_value(100) is True

    def test_validate_level_value_200(self):
        """Test validate_level_value with 200"""
        assert Session.validate_level_value(200) is True

    def test_validate_level_value_300(self):
        """Test validate_level_value with 300"""
        assert Session.validate_level_value(300) is True

    def test_validate_level_value_400(self):
        """Test validate_level_value with 400"""
        assert Session.validate_level_value(400) is True

    def test_validate_level_value_invalid(self):
        """Test validate_level_value with invalid value"""
        assert Session.validate_level_value(500) is False

    def test_validate_level_value_not_int(self):
        """Test validate_level_value with non-integer type"""
        assert Session.validate_level_value("300") is False

    def test_level_value_invalid(self):
        """Test Session constructor with invalid level_value"""
        data = self.valid_session_data.copy()
        data["level_value"] = 500
        with pytest.raises(EntityError):
            Session(**data)

    def test_level_value_not_int(self):
        """Test Session constructor with non-integer level_value"""
        data = self.valid_session_data.copy()
        data["level_value"] = "300"
        with pytest.raises(EntityError):
            Session(**data)

    # Other field validation tests
    def test_abstract_none(self):
        """Test Session constructor with None abstract"""
        data = self.valid_session_data.copy()
        data["abstract"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_abstract_not_string(self):
        """Test Session constructor with non-string abstract"""
        data = self.valid_session_data.copy()
        data["abstract"] = 123
        with pytest.raises(EntityError):
            Session(**data)

    def test_venue_name_none(self):
        """Test Session constructor with None venue_name"""
        data = self.valid_session_data.copy()
        data["venue_name"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_venue_room_none(self):
        """Test Session constructor with None venue_room"""
        data = self.valid_session_data.copy()
        data["venue_room"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_day_none(self):
        """Test Session constructor with None day"""
        data = self.valid_session_data.copy()
        data["day"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_level_none(self):
        """Test Session constructor with None level"""
        data = self.valid_session_data.copy()
        data["level"] = None
        with pytest.raises(EntityError):
            Session(**data)

    # List field validation tests
    def test_speakers_none(self):
        """Test Session constructor with None speakers"""
        data = self.valid_session_data.copy()
        data["speakers"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_speakers_not_list(self):
        """Test Session constructor with non-list speakers"""
        data = self.valid_session_data.copy()
        data["speakers"] = "not a list"
        with pytest.raises(EntityError):
            Session(**data)

    def test_topics_none(self):
        """Test Session constructor with None topics"""
        data = self.valid_session_data.copy()
        data["topics"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_topics_not_list(self):
        """Test Session constructor with non-list topics"""
        data = self.valid_session_data.copy()
        data["topics"] = "not a list"
        with pytest.raises(EntityError):
            Session(**data)

    def test_areas_of_interest_none(self):
        """Test Session constructor with None areas_of_interest"""
        data = self.valid_session_data.copy()
        data["areas_of_interest"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_areas_of_interest_not_list(self):
        """Test Session constructor with non-list areas_of_interest"""
        data = self.valid_session_data.copy()
        data["areas_of_interest"] = "not a list"
        with pytest.raises(EntityError):
            Session(**data)

    def test_features_none(self):
        """Test Session constructor with None features"""
        data = self.valid_session_data.copy()
        data["features"] = None
        with pytest.raises(EntityError):
            Session(**data)

    def test_features_not_list(self):
        """Test Session constructor with non-list features"""
        data = self.valid_session_data.copy()
        data["features"] = "not a list"
        with pytest.raises(EntityError):
            Session(**data)

    # seat_capacity validation tests
    def test_seat_capacity_not_int(self):
        """Test Session constructor with non-integer seat_capacity"""
        data = self.valid_session_data.copy()
        data["seat_capacity"] = "126"
        with pytest.raises(EntityError):
            Session(**data)

    def test_seat_capacity_negative(self):
        """Test Session constructor with negative seat_capacity"""
        data = self.valid_session_data.copy()
        data["seat_capacity"] = -1
        with pytest.raises(EntityError):
            Session(**data)

    def test_seat_capacity_zero(self):
        """Test Session constructor with zero seat_capacity"""
        data = self.valid_session_data.copy()
        data["seat_capacity"] = 0
        session = Session(**data)
        assert session.seat_capacity == 0

    # Edge cases
    def test_session_with_empty_lists(self):
        """Test Session constructor with empty lists"""
        data = self.valid_session_data.copy()
        data["speakers"] = []
        data["topics"] = []
        data["areas_of_interest"] = []
        data["features"] = []
        session = Session(**data)
        assert session.speakers == []
        assert session.topics == []

    def test_session_with_empty_abstract(self):
        """Test Session constructor with empty abstract string"""
        data = self.valid_session_data.copy()
        data["abstract"] = ""
        session = Session(**data)
        assert session.abstract == ""
