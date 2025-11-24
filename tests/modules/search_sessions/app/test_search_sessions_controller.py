from src.modules.search_sessions.app.search_sessions_controller import SearchSessionsController
from src.modules.search_sessions.app.search_sessions_usecase import SearchSessionsUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SearchSessionsController:
    def test_search_sessions_controller_successful(self):
        """Test successful search returns 200 OK"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'keywords': 'security'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
        assert "message" in response.body
    
    def test_search_sessions_controller_all_filters(self):
        """Test search with all filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={
            'day': 'Monday',
            'venue': 'Venetian',
            'level': '300',
            'keywords': 'security',
            'page_size': '20'
        })
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
        assert response.body["pagination"]["page_size"] <= 20
    
    def test_search_sessions_controller_partial_filters(self):
        """Test search with partial filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={
            'day': 'Tuesday',
            'level': '200'
        })
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
    
    def test_search_sessions_controller_no_filters(self):
        """Test search with no filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
    
    def test_search_sessions_controller_invalid_day(self):
        """Test invalid day returns 400"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'day': 'InvalidDay'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert "day" in response.body
    
    def test_search_sessions_controller_invalid_level(self):
        """Test invalid level returns 400"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'level': '500'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert "level" in response.body
    
    def test_search_sessions_controller_invalid_page_size(self):
        """Test invalid page_size returns 400"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '150'})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert "page_size" in response.body
    
    def test_search_sessions_controller_empty_results(self):
        """Test empty results returns 200 with empty array"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'keywords': 'nonexistentkeywordxyz123'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body["sessions"] == []
        assert "pagination" in response.body
    
    def test_search_sessions_controller_pagination_metadata(self):
        """Test response includes pagination metadata"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'page_size': '10'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "pagination" in response.body
        assert "page_size" in response.body["pagination"]
        assert "next_page_token" in response.body["pagination"]
    
    def test_search_sessions_controller_with_speaker(self):
        """Test controller with valid speaker parameter returns 200"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'speaker': 'Werner'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
    
    def test_search_sessions_controller_invalid_speaker_empty(self):
        """Test controller with invalid speaker (empty) returns 400"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'speaker': ''})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert "speaker" in response.body
    
    def test_search_sessions_controller_speaker_with_other_filters(self):
        """Test controller with speaker combined with other filters"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={
            'speaker': 'Werner',
            'day': 'Monday',
            'venue': 'Venetian',
            'level': '300',
            'keywords': 'serverless'
        })
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "pagination" in response.body
    
    def test_search_sessions_controller_speaker_matching_sessions(self):
        """Test response includes sessions with matching speakers"""
        repo = SessionRepositoryMock()
        usecase = SearchSessionsUsecase(repo=repo)
        controller = SearchSessionsController(usecase=usecase)
        
        request = HttpRequest(query_params={'speaker': 'AWS'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        
        # Verify all returned sessions have a matching speaker
        for session in response.body["sessions"]:
            found_match = False
            for speaker in session.get("speakers", []):
                if "aws" in speaker.get("displayName", "").lower() or "aws" in speaker.get("company", "").lower():
                    found_match = True
                    break
            assert found_match, f"Session {session.get('session_id')} does not have a matching speaker"
