from src.modules.get_sessions_by_venue.app.get_sessions_by_venue_controller import GetSessionsByVenueController
from src.modules.get_sessions_by_venue.app.get_sessions_by_venue_usecase import GetSessionsByVenueUsecase
from src.shared.helpers.external_interfaces.http_models import HttpRequest
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByVenueController:
    def test_get_sessions_by_venue_controller(self):
        """Test successful request with venue_name"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo=repo)
        controller = GetSessionsByVenueController(usecase=usecase)
        
        request = HttpRequest(query_params={'venue_name': 'Mandalay Bay'})
        

        response = controller(request=request)
        
        assert response.status_code == 200
        assert "sessions" in response.body
        assert "count" in response.body
        assert "venue_name" in response.body
        assert response.body["venue_name"] == "Mandalay Bay"
    
    def test_get_sessions_by_venue_controller_missing_venue_name(self):
        """Test request with missing venue_name returns 400"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo=repo)
        controller = GetSessionsByVenueController(usecase=usecase)
        
        request = HttpRequest(query_params={})
        
        response = controller(request=request)
        
        assert response.status_code == 400
        assert response.body == "Field venue_name is missing"
    
    def test_get_sessions_by_venue_controller_no_matches(self):
        """Test request with venue that has no sessions returns empty array"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo=repo)
        controller = GetSessionsByVenueController(usecase=usecase)
        
        request = HttpRequest(query_params={'venue_name': 'Nonexistent Venue'})
        
        response = controller(request=request)
        
        assert response.status_code == 200
        assert response.body["count"] == 0
        assert response.body["sessions"] == []
        assert response.body["venue_name"] == "Nonexistent Venue"
