from src.modules.get_sessions_by_day.app.get_sessions_by_day_controller import GetSessionsByDayController
from src.modules.get_sessions_by_day.app.get_sessions_by_day_usecase import GetSessionsByDayUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByDayController:
    def test_get_sessions_by_day_controller(self):
        """Test successful request with valid day"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo=repo)
        controller = GetSessionsByDayController(usecase=usecase)
        
        request = HttpRequest(body={'day': 'Thursday'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert 'sessions' in response.body
        assert 'count' in response.body
        assert 'day' in response.body
        assert response.body['day'] == 'Thursday'
    
    def test_get_sessions_by_day_controller_missing_day(self):
        """Test request with missing day parameter returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo=repo)
        controller = GetSessionsByDayController(usecase=usecase)
        
        request = HttpRequest(body={})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field day is missing"
    
    def test_get_sessions_by_day_controller_no_matches(self):
        """Test request with day that has no sessions"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByDayUsecase(repo=repo)
        controller = GetSessionsByDayController(usecase=usecase)
        
        request = HttpRequest(body={'day': 'NonExistentDay'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body['sessions'] == []
        assert response.body['count'] == 0
        assert response.body['day'] == 'NonExistentDay'
