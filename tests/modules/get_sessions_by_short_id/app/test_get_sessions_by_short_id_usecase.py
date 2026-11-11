from src.modules.get_sessions_by_short_id.app.get_sessions_by_short_id_usecase import GetSessionsByShortIdUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByShortIdUsecase:
    def test_get_sessions_by_short_id(self):
        """Test retrieving sessions by short_id"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo)
        
        # Use a short_id from the mock data
        sessions = usecase(short_id="TNC301")
        
        assert len(sessions) == 1
        assert sessions[0].short_id == "TNC301"
        assert sessions[0].title == "Accelerate VMware Migration with AWS Transform"
    
    def test_get_sessions_by_short_id_not_found(self):
        """Test retrieving sessions with non-existent short_id"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo)
        
        sessions = usecase(short_id="NONEXISTENT")
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_get_sessions_by_short_id_case_insensitive(self):
        """Test case-insensitive matching for short_id"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo)
        
        # Test with lowercase
        sessions_lower = usecase(short_id="tnc301")
        assert len(sessions_lower) == 1
        assert sessions_lower[0].short_id == "TNC301"
        
        # Test with uppercase
        sessions_upper = usecase(short_id="TNC301")
        assert len(sessions_upper) == 1
        assert sessions_upper[0].short_id == "TNC301"
        
        # Test with mixed case
        sessions_mixed = usecase(short_id="TnC301")
        assert len(sessions_mixed) == 1
        assert sessions_mixed[0].short_id == "TNC301"
