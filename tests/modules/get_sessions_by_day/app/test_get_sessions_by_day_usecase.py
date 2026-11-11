from src.modules.get_sessions_by_day.app.get_sessions_by_day_usecase import GetSessionsByDayUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByDayUsecase:
    def test_get_sessions_by_day(self):
        """Test retrieving sessions for a specific day"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo)
        
        sessions = usecase(day="Thursday")
        
        assert len(sessions) > 0
        for session in sessions:
            assert session.day.lower() == "thursday"
    
    def test_get_sessions_by_day_case_insensitive(self):
        """Test case-insensitive day matching"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo)
        
        sessions_lower = usecase(day="thursday")
        sessions_upper = usecase(day="THURSDAY")
        sessions_mixed = usecase(day="Thursday")
        
        assert len(sessions_lower) == len(sessions_upper)
        assert len(sessions_lower) == len(sessions_mixed)
    
    def test_get_sessions_by_day_no_matches(self):
        """Test retrieving sessions for a day with no sessions"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo)
        
        sessions = usecase(day="NonExistentDay")
        
        assert len(sessions) == 0
        assert sessions == []
