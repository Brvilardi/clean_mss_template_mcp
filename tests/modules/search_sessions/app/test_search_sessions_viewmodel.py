from src.modules.search_sessions.app.search_sessions_viewmodel import SearchSessionsViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_SearchSessionsViewmodel:
    def test_to_dict_includes_all_session_fields(self):
        """Test to_dict() includes all session fields"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:1]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token=None,
            total_results=1
        )
        
        result = viewmodel.to_dict()
        
        # Verify sessions array exists
        assert "sessions" in result
        assert len(result["sessions"]) == 1
        
        # Verify all session fields are present
        session_dict = result["sessions"][0]
        assert "session_id" in session_dict
        assert "short_id" in session_dict
        assert "title" in session_dict
        assert "abstract" in session_dict
        assert "session_type" in session_dict
        assert "venue_name" in session_dict
        assert "venue_room" in session_dict
        assert "start_datetime" in session_dict
        assert "end_datetime" in session_dict
        assert "day" in session_dict
        assert "speakers" in session_dict
        assert "topics" in session_dict
        assert "areas_of_interest" in session_dict
        assert "level" in session_dict
        assert "level_value" in session_dict
        assert "features" in session_dict
        assert "seat_capacity" in session_dict
    
    def test_pagination_metadata_is_present(self):
        """Test pagination metadata is present"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token="test_token",
            total_results=2
        )
        
        result = viewmodel.to_dict()
        
        # Verify pagination metadata exists
        assert "pagination" in result
        assert isinstance(result["pagination"], dict)
        assert "page_size" in result["pagination"]
        assert "next_page_token" in result["pagination"]
    
    def test_next_page_token_included_when_present(self):
        """Test next_page_token is included when present"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token="test_token_123",
            total_results=2
        )
        
        result = viewmodel.to_dict()
        
        assert result["pagination"]["next_page_token"] == "test_token_123"
    
    def test_next_page_token_is_null_when_absent(self):
        """Test next_page_token is null when absent"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token=None,
            total_results=2
        )
        
        result = viewmodel.to_dict()
        
        assert result["pagination"]["next_page_token"] is None
    
    def test_message_field_is_present(self):
        """Test message field is present"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:1]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token=None,
            total_results=1
        )
        
        result = viewmodel.to_dict()
        
        assert "message" in result
        assert result["message"] == "search completed successfully"
    
    def test_page_size_matches_number_of_sessions(self):
        """Test page_size matches number of sessions returned"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:3]
        
        viewmodel = SearchSessionsViewmodel(
            sessions=sessions,
            next_page_token=None,
            total_results=3
        )
        
        result = viewmodel.to_dict()
        
        assert result["pagination"]["page_size"] == 3
        assert result["pagination"]["page_size"] == len(sessions)
    
    def test_empty_sessions_list(self):
        """Test with empty sessions list"""
        viewmodel = SearchSessionsViewmodel(
            sessions=[],
            next_page_token=None,
            total_results=0
        )
        
        result = viewmodel.to_dict()
        
        assert "sessions" in result
        assert len(result["sessions"]) == 0
        assert result["pagination"]["page_size"] == 0
        assert result["pagination"]["next_page_token"] is None
        assert result["message"] == "search completed successfully"
