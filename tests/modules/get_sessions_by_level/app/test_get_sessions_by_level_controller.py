from src.modules.get_sessions_by_level.app.get_sessions_by_level_controller import GetSessionsByLevelController
from src.modules.get_sessions_by_level.app.get_sessions_by_level_usecase import GetSessionsByLevelUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByLevelController:
    def test_get_sessions_by_level_controller_single(self):
        """Test successful request handling with single level"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': '300'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "count" in response.body
        assert "level_values" in response.body
        assert response.body["level_values"] == [300]
    
    def test_get_sessions_by_level_controller_multiple(self):
        """Test successful request handling with multiple levels"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': '100, 200'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "count" in response.body
        assert "level_values" in response.body
        assert response.body["level_values"] == [100, 200]
    
    def test_get_sessions_by_level_controller_all_levels(self):
        """Test successful request handling with all levels"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': '100, 200, 300, 400'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body["level_values"] == [100, 200, 300, 400]
    
    def test_get_sessions_by_level_controller_missing_level_values(self):
        """Test request with missing level_values parameter"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field level_values is missing"
    
    def test_get_sessions_by_level_controller_invalid_type(self):
        """Test request with invalid level_values type"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': 'invalid, text'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert "level_values" in response.body
    
    def test_get_sessions_by_level_controller_invalid_level_value(self):
        """Test request with invalid level_value (not 100/200/300/400)"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': '250'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field level_values is not valid"
    
    def test_get_sessions_by_level_controller_empty_results(self):
        """Test request with level that has no sessions"""
        repo = SessionRepositoryMock()
        # Clear all sessions to test empty results
        repo.sessions = []
        usecase = GetSessionsByLevelUsecase(repo=repo)
        controller = GetSessionsByLevelController(usecase=usecase)
        
        request = HttpRequest(query_params={'level_values': '100'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body["sessions"] == []
        assert response.body["count"] == 0
        assert response.body["level_values"] == [100]
