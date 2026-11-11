from src.modules.get_sessions_by_venue.app.get_sessions_by_venue_viewmodel import GetSessionsByVenueViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByVenueViewmodel:
    def test_get_sessions_by_venue_viewmodel(self):
        """Test view model transformation with sessions"""
        repo = SessionRepositoryMock()
        sessions = repo.get_all_sessions()[:2]  # Get first 2 sessions
        
        viewmodel = GetSessionsByVenueViewmodel(sessions=sessions, venue_name="Mandalay Bay")
        result = viewmodel.to_dict()
        
        assert result["count"] == 2
        assert result["venue_name"] == "Mandalay Bay"
        assert len(result["sessions"]) == 2
        
        # Verify session structure
        first_session = result["sessions"][0]
        assert "session_id" in first_session
        assert "short_id" in first_session
        assert "title" in first_session
        assert "abstract" in first_session
        assert "session_type" in first_session
        assert "venue_name" in first_session
        assert "venue_room" in first_session
        assert "start_datetime" in first_session
        assert "end_datetime" in first_session
        assert "day" in first_session
        assert "speakers" in first_session
        assert "topics" in first_session
        assert "areas_of_interest" in first_session
        assert "level" in first_session
        assert "level_value" in first_session
        assert "features" in first_session
        assert "seat_capacity" in first_session
    
    def test_get_sessions_by_venue_viewmodel_empty(self):
        """Test view model with empty sessions list"""
        viewmodel = GetSessionsByVenueViewmodel(sessions=[], venue_name="Nonexistent Venue")
        result = viewmodel.to_dict()
        
        assert result["count"] == 0
        assert result["venue_name"] == "Nonexistent Venue"
        assert result["sessions"] == []
