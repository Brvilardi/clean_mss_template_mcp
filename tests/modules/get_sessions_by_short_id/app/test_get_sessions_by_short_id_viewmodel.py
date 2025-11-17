from src.modules.get_sessions_by_short_id.app.get_sessions_by_short_id_viewmodel import GetSessionsByShortIdViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByShortIdViewmodel:
    def test_get_sessions_by_short_id_viewmodel(self):
        """Test view model transformation with sessions"""
        repo = SessionRepositoryMock()
        sessions = [repo.sessions[0]]  # Get first session
        
        viewmodel = GetSessionsByShortIdViewmodel(sessions=sessions, short_id="TNC301")
        result = viewmodel.to_dict()
        
        assert result["count"] == 1
        assert result["short_id"] == "TNC301"
        assert len(result["sessions"]) == 1
        assert result["sessions"][0]["session_id"] == sessions[0].session_id
        assert result["sessions"][0]["short_id"] == sessions[0].short_id
        assert result["sessions"][0]["title"] == sessions[0].title
        assert result["sessions"][0]["abstract"] == sessions[0].abstract
        assert result["sessions"][0]["session_type"] == sessions[0].session_type
        assert result["sessions"][0]["venue_name"] == sessions[0].venue_name
        assert result["sessions"][0]["venue_room"] == sessions[0].venue_room
        assert result["sessions"][0]["start_datetime"] == sessions[0].start_datetime
        assert result["sessions"][0]["end_datetime"] == sessions[0].end_datetime
        assert result["sessions"][0]["day"] == sessions[0].day
        assert result["sessions"][0]["speakers"] == sessions[0].speakers
        assert result["sessions"][0]["topics"] == sessions[0].topics
        assert result["sessions"][0]["areas_of_interest"] == sessions[0].areas_of_interest
        assert result["sessions"][0]["level"] == sessions[0].level
        assert result["sessions"][0]["level_value"] == sessions[0].level_value
        assert result["sessions"][0]["features"] == sessions[0].features
        assert result["sessions"][0]["seat_capacity"] == sessions[0].seat_capacity
    
    def test_get_sessions_by_short_id_viewmodel_empty(self):
        """Test view model transformation with empty sessions list"""
        viewmodel = GetSessionsByShortIdViewmodel(sessions=[], short_id="NONEXISTENT")
        result = viewmodel.to_dict()
        
        assert result["count"] == 0
        assert result["short_id"] == "NONEXISTENT"
        assert result["sessions"] == []
