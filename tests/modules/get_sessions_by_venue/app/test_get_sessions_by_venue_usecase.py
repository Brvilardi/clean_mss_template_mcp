from src.modules.get_sessions_by_venue.app.get_sessions_by_venue_usecase import GetSessionsByVenueUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetSessionsByVenueUsecase:
    def test_get_sessions_by_venue(self):
        """Test retrieving sessions by venue name"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo)
        
        # Get sessions for a venue that exists in mock data
        sessions = usecase(venue_name="Mandalay Bay")
        
        assert len(sessions) > 0
        for session in sessions:
            assert session.venue_name.lower() == "mandalay bay"
    
    def test_get_sessions_by_venue_no_matches(self):
        """Test retrieving sessions for venue with no sessions"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo)
        
        sessions = usecase(venue_name="Nonexistent Venue")
        
        assert len(sessions) == 0
        assert sessions == []
    
    def test_get_sessions_by_venue_exact_match(self):
        """Test exact venue name matching"""
        repo = SessionRepositoryMock()
        usecase = GetSessionsByVenueUsecase(repo)
        
        # Test with exact match
        sessions = usecase(venue_name="Mandalay Bay")
        assert len(sessions) > 0
        
        # Test that case-sensitive matching is used
        sessions_wrong_case = usecase(venue_name="mandalay bay")
        assert len(sessions_wrong_case) == 0
