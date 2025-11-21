from src.modules.get_all_sessions_paginated.app.get_all_sessions_paginated_usecase import GetAllSessionsPaginatedUsecase
from src.shared.infra.repositories.session_repository_mock import SessionRepositoryMock


class Test_GetAllSessionsPaginatedUsecase:
    def test_get_all_sessions_paginated_with_mock_repository(self):
        """Test use case with mock repository"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo)
        
        sessions, next_token = usecase(page_size=2)
        
        assert len(sessions) == 2
        assert next_token is not None
    
    def test_get_all_sessions_paginated_returns_tuple(self):
        """Test use case returns tuple (sessions, next_token)"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo)
        
        result = usecase(page_size=3)
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        sessions, next_token = result
        assert isinstance(sessions, list)
        assert isinstance(next_token, str) or next_token is None
    
    def test_get_all_sessions_paginated_with_page_size_only(self):
        """Test use case with page_size only"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo)
        
        sessions, next_token = usecase(page_size=3)
        
        assert len(sessions) == 3
        assert next_token is not None
    
    def test_get_all_sessions_paginated_with_page_size_and_token(self):
        """Test use case with page_size and last_evaluated_key"""
        repo = SessionRepositoryMock()
        usecase = GetAllSessionsPaginatedUsecase(repo)
        
        # Get first page
        page1, token1 = usecase(page_size=2)
        
        # Get second page using token
        page2, token2 = usecase(page_size=2, last_evaluated_key=token1)
        
        assert len(page1) == 2
        assert len(page2) == 2
        
        # Verify no overlap
        page1_ids = [s.session_id for s in page1]
        page2_ids = [s.session_id for s in page2]
        assert len(set(page1_ids) & set(page2_ids)) == 0
