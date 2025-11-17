import pytest
from src.modules.get_sessions_by_level.app.get_sessions_by_level_usecase import GetSessionsByLevelUsecase
from src.shared.helpers.errors.domain_errors import EntityError
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByLevelUsecase:
    def test_get_sessions_by_level_single(self):
        """Test retrieving sessions by single level_value"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        sessions = usecase(level_values=[300])
        
        assert len(sessions) > 0
        for session in sessions:
            assert session.level_value == 300
    
    def test_get_sessions_by_level_multiple(self):
        """Test retrieving sessions by multiple level_values"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        sessions = usecase(level_values=[200, 300])
        
        assert len(sessions) > 0
        for session in sessions:
            assert session.level_value in [200, 300]
    
    def test_get_sessions_by_level_all(self):
        """Test retrieving sessions by all level_values"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        sessions = usecase(level_values=[100, 200, 300, 400])
        
        assert len(sessions) > 0
    
    def test_get_sessions_by_level_no_results(self):
        """Test retrieving sessions with level that has no sessions"""
        repo = SessionRepositoryMock()
        # Clear all sessions to test empty results
        repo.sessions = []
        usecase = GetSessionsByLevelUsecase(repo)
        
        sessions = usecase(level_values=[100])
        
        assert isinstance(sessions, list)
        assert len(sessions) == 0
    
    def test_get_sessions_by_level_invalid_level_value(self):
        """Test that invalid level_value raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level_values=[250])
    
    def test_get_sessions_by_level_invalid_level_value_in_list(self):
        """Test that invalid level_value in list raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level_values=[100, 250, 300])
    
    def test_get_sessions_by_level_invalid_level_value_zero(self):
        """Test that level_value 0 raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level_values=[0])
    
    def test_get_sessions_by_level_invalid_level_value_negative(self):
        """Test that negative level_value raises EntityError"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo)
        
        with pytest.raises(EntityError):
            usecase(level_values=[-100])
