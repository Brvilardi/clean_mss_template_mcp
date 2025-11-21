import pytest
from src.modules.get_all_sessions_paginated.app.get_all_sessions_paginated_controller import GetAllSessionsPaginatedController
from src.modules.get_all_sessions_paginated.app.get_all_sessions_paginated_usecase import GetAllSessionsPaginatedUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetAllSessionsPaginatedController:
    def test_successful_request_with_page_size_only(self):
        """Test successful request with page_size only"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '2'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert 'sessions' in response.body
        assert 'count' in response.body
        assert 'page_size' in response.body
        assert 'has_more' in response.body
        assert response.body['page_size'] == 2
    
    def test_successful_request_with_page_size_and_last_evaluated_key(self):
        """Test successful request with page_size and last_evaluated_key"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        # Get first page to get a token
        request1 = HttpRequest(query_params={'page_size': '2'})
        response1 = controller(request=request1)
        token = response1.body.get('last_evaluated_key')
        
        # Get second page using token
        request2 = HttpRequest(query_params={'page_size': '2', 'last_evaluated_key': token})
        response2 = controller(request=request2)
        
        assert response2.status_code == 200
        assert 'sessions' in response2.body
        assert len(response2.body['sessions']) <= 2
    
    def test_missing_page_size_returns_400(self):
        """Test missing page_size returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert 'page_size' in response.body
    
    def test_invalid_page_size_type_returns_400(self):
        """Test invalid page_size type returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': 'invalid'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
    
    def test_page_size_less_than_1_returns_400(self):
        """Test page_size < 1 returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '0'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert 'at least 1' in response.body
    
    def test_page_size_greater_than_100_returns_400(self):
        """Test page_size > 100 returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '101'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert 'cannot exceed 100' in response.body
    
    def test_expired_token_returns_400(self):
        """Test expired token returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        # Create an expired token
        import time
        import base64
        import json
        
        expired_token_data = {
            'index': 2,
            'issued_at': int(time.time()) - 400,  # 400 seconds ago (expired)
            'ttl': 300
        }
        
        expired_token = base64.b64encode(json.dumps(expired_token_data).encode('utf-8')).decode('utf-8')
        
        request = HttpRequest(query_params={'page_size': '2', 'last_evaluated_key': expired_token})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert 'expired' in response.body.lower()
    
    def test_invalid_token_format_returns_400(self):
        """Test invalid token format returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '2', 'last_evaluated_key': 'invalid_token'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
    
    def test_response_includes_pagination_metadata(self):
        """Test response includes pagination metadata"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo=repo)
        controller = GetAllSessionsPaginatedController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '2'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert 'sessions' in response.body
        assert 'count' in response.body
        assert 'page_size' in response.body
        assert 'has_more' in response.body
        assert response.body['count'] == len(response.body['sessions'])
