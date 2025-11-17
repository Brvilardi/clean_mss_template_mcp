from src.modules.get_sessions_by_level.app.get_sessions_by_level_viewmodel import GetSessionsByLevelViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByLevelViewmodel:
    def test_get_sessions_by_level_viewmodel_single(self):
        """Test view model transformation with single level"""
        repo = SessionRepositoryMock()
        sessions = [s for s in repo.sessions if s.level_value == 300]
        
        viewmodel = GetSessionsByLevelViewmodel(sessions=sessions, level_values=[300])
        result = viewmodel.to_dict()
        
        assert "sessions" in result
        assert "count" in result
        assert "level_values" in result
        assert result["count"] == len(sessions)
        assert result["level_values"] == [300]
        assert isinstance(result["sessions"], list)
        
        if len(sessions) > 0:
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
    
    def test_get_sessions_by_level_viewmodel_multiple(self):
        """Test view model transformation with multiple levels"""
        repo = SessionRepositoryMock()
        sessions = [s for s in repo.sessions if s.level_value in [200, 300]]
        
        viewmodel = GetSessionsByLevelViewmodel(sessions=sessions, level_values=[200, 300])
        result = viewmodel.to_dict()
        
        assert result["count"] == len(sessions)
        assert result["level_values"] == [200, 300]
    
    def test_get_sessions_by_level_viewmodel_empty(self):
        """Test view model with empty sessions list"""
        viewmodel = GetSessionsByLevelViewmodel(sessions=[], level_values=[100])
        result = viewmodel.to_dict()
        
        assert result["sessions"] == []
        assert result["count"] == 0
        assert result["level_values"] == [100]
