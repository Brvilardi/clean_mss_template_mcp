from src.modules.get_sessions_by_day.app.get_sessions_by_day_viewmodel import GetSessionsByDayViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByDayViewmodel:
    def test_get_sessions_by_day_viewmodel(self):
        """Test view model transformation with sessions"""
        repo = SessionRepositoryMock()
        sessions = [s for s in repo.sessions if s.day and s.day.lower() == "thursday"]
        
        viewmodel = GetSessionsByDayViewmodel(sessions=sessions, day="Thursday").to_dict()
        
        assert "sessions" in viewmodel
        assert "count" in viewmodel
        assert "day" in viewmodel
        assert viewmodel["count"] == len(sessions)
        assert viewmodel["day"] == "Thursday"
        assert len(viewmodel["sessions"]) == len(sessions)
        
        # Verify session structure
        if len(sessions) > 0:
            first_session = viewmodel["sessions"][0]
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
    
    def test_get_sessions_by_day_viewmodel_empty(self):
        """Test view model with empty sessions list"""
        viewmodel = GetSessionsByDayViewmodel(sessions=[], day="NonExistentDay").to_dict()
        
        assert viewmodel["sessions"] == []
        assert viewmodel["count"] == 0
        assert viewmodel["day"] == "NonExistentDay"
