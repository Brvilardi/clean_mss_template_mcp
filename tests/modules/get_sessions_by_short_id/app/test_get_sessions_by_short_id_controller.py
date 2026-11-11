from src.modules.get_sessions_by_short_id.app.get_sessions_by_short_id_controller import GetSessionsByShortIdController
from src.modules.get_sessions_by_short_id.app.get_sessions_by_short_id_usecase import GetSessionsByShortIdUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByShortIdController:
    def test_get_sessions_by_short_id_controller(self):
        """Test successful request with valid short_id"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo=repo)
        controller = GetSessionsByShortIdController(usecase=usecase)
        
        request = HttpRequest(query_params={'short_id': 'TNC301'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body['count'] == 1
        assert response.body['short_id'] == 'TNC301'
        assert len(response.body['sessions']) == 1
        assert response.body['sessions'][0]['short_id'] == 'TNC301'
    
    def test_get_sessions_by_short_id_controller_missing_short_id(self):
        """Test request with missing short_id parameter"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo=repo)
        controller = GetSessionsByShortIdController(usecase=usecase)
        
        request = HttpRequest(query_params={})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field short_id is missing"
    
    def test_get_sessions_by_short_id_controller_not_found(self):
        """Test request with non-existent short_id returns empty array"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByShortIdUsecase(repo=repo)
        controller = GetSessionsByShortIdController(usecase=usecase)
        
        request = HttpRequest(query_params={'short_id': 'NONEXISTENT'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body['count'] == 0
        assert response.body['short_id'] == 'NONEXISTENT'
        assert response.body['sessions'] == []
