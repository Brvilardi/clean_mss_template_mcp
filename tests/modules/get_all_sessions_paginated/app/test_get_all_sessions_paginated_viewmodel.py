from src.modules.get_all_sessions_paginated.app.get_all_sessions_paginated_viewmodel import GetAllSessionsPaginatedViewmodel
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetAllSessionsPaginatedViewmodel:
    def test_to_dict_output_format(self):
        """Test to_dict() output format"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=2,
            next_token="test_token"
        )
        
        result = viewmodel.to_dict()
        
        assert "sessions" in result
        assert "count" in result
        assert "page_size" in result
        assert "has_more" in result
        assert isinstance(result["sessions"], list)
        assert isinstance(result["count"], int)
        assert isinstance(result["page_size"], int)
        assert isinstance(result["has_more"], bool)
    
    def test_has_more_is_true_when_next_token_exists(self):
        """Test has_more is true when next_token exists"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=2,
            next_token="test_token"
        )
        
        result = viewmodel.to_dict()
        
        assert result["has_more"] is True
    
    def test_has_more_is_false_when_next_token_is_none(self):
        """Test has_more is false when next_token is None"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=2,
            next_token=None
        )
        
        result = viewmodel.to_dict()
        
        assert result["has_more"] is False
    
    def test_last_evaluated_key_only_included_when_has_more_is_true(self):
        """Test last_evaluated_key only included when has_more is true"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        # With next_token
        viewmodel_with_token = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=2,
            next_token="test_token"
        )
        result_with_token = viewmodel_with_token.to_dict()
        assert "last_evaluated_key" in result_with_token
        assert result_with_token["last_evaluated_key"] == "test_token"
        
        # Without next_token
        viewmodel_without_token = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=2,
            next_token=None
        )
        result_without_token = viewmodel_without_token.to_dict()
        assert "last_evaluated_key" not in result_without_token
    
    def test_count_matches_number_of_sessions(self):
        """Test count matches number of sessions"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:3]
        
        viewmodel = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=5,
            next_token=None
        )
        
        result = viewmodel.to_dict()
        
        assert result["count"] == 3
        assert result["count"] == len(sessions)
    
    def test_page_size_is_included_in_response(self):
        """Test page_size is included in response"""
        repo = SessionRepositoryMock()
        sessions = repo.sessions[:2]
        
        viewmodel = GetAllSessionsPaginatedViewmodel(
            sessions=sessions,
            page_size=10,
            next_token=None
        )
        
        result = viewmodel.to_dict()
        
        assert result["page_size"] == 10
